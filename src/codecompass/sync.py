"""Per-vendor sync orchestration.

Wires together an ecosystem adapter (Phase 2), Phase 3's tree renderers, a
`vendor/<name>/src/` snapshot sourced from the vendor's own upstream
repository via `codecompass.source_resolution` (decisions/0021) — since
Phase 13, cloned unconditionally for every vendor (decisions/0033) — a
read-only lookup of this vendor's current AI enrichment from the context
graph (Phase 16, decisions/0035 — `codecompass.enrichment` is the only
writer of that data; `sync_vendor` never generates it), and per-vendor
`CLAUDE.md` templating — writing everything under `vendor/<name>/`. Also
`rebuild_project_graph` (Phase 11, extended in
Phase 12 with doc/skill-mapping data via `codecompass.doc_mapping`/
`codecompass.skill_scan`, and in Phase 27 with a scan of each vendor's own
embedded upstream doc files), which rebuilds `context-graph.db` from every
tracked vendor's current state plus a fresh project-source usage scan —
decoupled from `sync_all`'s per-vendor loop on purpose (see
planning/phase-11-project-source-usage-detection.md's Design decisions)
and called only from the two whole-project call sites in `cli.py`. See
planning/phase-4-sync-index-init.md, planning/phase-5-gap-analysis.md,
planning/phase-7-bootstrap-and-promote.md,
planning/phase-11-project-source-usage-detection.md,
planning/phase-12-doc-and-wide-skill-mapping.md,
planning/phase-16-retire-depth.md, and
planning/phase-27-register-embedded-vendor-docs.md.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
from pathlib import Path

from codecompass import git_topology, skill_scan, source_symbols, spec_docs, usage
from codecompass.adapters import get_adapter
from codecompass.claude_md import render_vendor_claude_md
from codecompass.core import VendorConfig, VendorDigest
from codecompass.deptree import render_deptree_json, render_deptree_markdown
from codecompass.doc_mapping import (
    build_depends_on_edges,
    build_doc_chunks,
    build_doc_relations_edges,
    build_documents_edges,
    build_routes_via_edges,
    collect_vendor_doc_artifacts,
    collect_vendor_upstream_doc_artifacts,
)
from codecompass.filetree import (
    build_symbol_index,
    render_filetree_json,
    render_filetree_markdown,
)
from codecompass.graph import (
    GitRepositoryRow,
    GitSubmoduleRow,
    GitWorktreeRow,
    SourceFileRow,
    SourceSymbolRow,
    SymbolRow,
    UsesEdgeRow,
    VendorRow,
    open_graph,
    rebuild_deterministic,
)
from codecompass.source_resolution import SourceResolutionError, resolve_and_clone

_SNAPSHOT_PRUNE_NAMES = ("node_modules", "dist", "build", ".git", "__pycache__", ".venv", "venv")
_GRAPH_DB_FILENAME = "context-graph.db"


def _open_graph_readonly(project_root: Path) -> sqlite3.Connection | None:
    """`None` if `context-graph.db` doesn't exist yet — a project that's
    never run a whole-project sync. Mirrors `index.py`'s
    `_open_graph_readonly` exactly: a genuine read-only connection (SQLite
    URI `mode=ro`), not `graph.open_graph` — this lookup runs on every
    `sync_vendor` call and must stay a pure read, never creating the file
    or issuing schema DDL as a side effect.
    """
    db_path = project_root / _GRAPH_DB_FILENAME
    if not db_path.exists():
        return None
    return sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)


def _lookup_enrichment(conn: sqlite3.Connection, vendor_name: str) -> tuple | None:
    """This vendor's `vendor_enrichment` row, if any — the four fields
    `sync_vendor` needs to populate its `VendorDigest`. `graph.py` has no
    existing read function returning these columns (`vendor_profile`
    joins `vendors`/`symbols`/`doc_artifacts`/etc., never
    `vendor_enrichment`), so this queries the table directly rather than
    stretching `vendor_profile`'s contract to cover a shape it wasn't
    built for.
    """
    return conn.execute(
        """
        SELECT ve.technical_description, ve.conversational_overview,
               ve.action_pointer_file, ve.action_pointer_note
        FROM vendor_enrichment ve
        JOIN vendors v ON ve.vendor_id = v.id
        WHERE v.name = ?
        """,
        (vendor_name,),
    ).fetchone()


def sync_vendor(config: VendorConfig, project_root: Path) -> VendorDigest:
    """Orchestrate one vendor end to end. Deterministic and idempotent —
    every output file listed below is fully overwritten on each call, no
    diffing against previous output, and no AI call is ever made from this
    function.

    Cloning (`resolve_and_clone`, falling back to `_copy_source_snapshot`
    on failure) runs unconditionally for every vendor (decisions/0033) —
    it costs nothing (no AI call). Separately, this vendor's current AI
    enrichment (if any) is read from the context graph
    (`_lookup_enrichment`, read-only, skipped gracefully if no
    `context-graph.db` exists yet) and used to populate
    `technical_description`/`conversational_overview`/
    `action_pointer_file`/`action_pointer_note` — the fix for the bug
    `decisions/0035` describes: a from-scratch re-render must reproduce a
    vendor's already-enriched Description section, not silently drop it
    for lack of a value nothing in this deterministic path ever computes
    itself. `codecompass.enrichment` is the only writer of that data
    (Phase B, usage-driven, batched, triggered from `cli.py`) — this
    function only ever reads it.

    If source resolution/cloning fails, `description_error` is set (a
    clone failure, not a description failure — there's no description
    "attempt" here to fail) and `vendor/<name>/src/` falls back to the old
    local-install-sourced snapshot (decisions/0004) so standalone browsing
    still has *something*; `FILETREE.md`/`filetree.json`/the symbol index
    fall back to rendering from `source_location()` too.
    """
    adapter = get_adapter(config, project_root)
    installed_version = adapter.installed_version()
    api_surface = adapter.readme_and_api_surface()
    dep_tree_root = adapter.dependency_tree()
    source_location = adapter.source_location()

    vendor_dir = project_root / "vendor" / config.name
    vendor_dir.mkdir(parents=True, exist_ok=True)

    src_dest = vendor_dir / "src"
    description_error = None
    try:
        repo_root: Path | None = resolve_and_clone(adapter, src_dest)
    except SourceResolutionError as exc:
        description_error = str(exc)
        _copy_source_snapshot(source_location, src_dest)
        repo_root = None

    tree_root = repo_root if repo_root is not None else source_location

    technical_description = conversational_overview = None
    action_pointer_file = action_pointer_note = None
    graph_conn = _open_graph_readonly(project_root)
    if graph_conn is not None:
        try:
            enrichment_row = _lookup_enrichment(graph_conn, config.name)
        finally:
            graph_conn.close()
        if enrichment_row is not None:
            (
                technical_description,
                conversational_overview,
                action_pointer_file,
                action_pointer_note,
            ) = enrichment_row

    action_pointer = None
    if action_pointer_file:
        action_pointer = (action_pointer_file, action_pointer_note)

    dep_tree_markdown = render_deptree_markdown(dep_tree_root)
    (vendor_dir / "DEPTREE.md").write_text(dep_tree_markdown, encoding="utf-8")
    (vendor_dir / "deptree.json").write_text(
        json.dumps(render_deptree_json(dep_tree_root), indent=2), encoding="utf-8"
    )

    file_tree_markdown = _render_filetree_with_symbol_index(tree_root, config, action_pointer)
    (vendor_dir / "FILETREE.md").write_text(file_tree_markdown, encoding="utf-8")
    (vendor_dir / "filetree.json").write_text(
        json.dumps(
            render_filetree_json(tree_root, config.ecosystem, action_pointer=action_pointer),
            indent=2,
        ),
        encoding="utf-8",
    )

    digest = VendorDigest(
        config=config,
        installed_version=installed_version,
        file_tree=file_tree_markdown,
        dep_tree=dep_tree_markdown,
        api_surface=api_surface,
        technical_description=technical_description,
        conversational_overview=conversational_overview,
        description_error=description_error,
        action_pointer_file=action_pointer_file,
        action_pointer_note=action_pointer_note,
        side_effects=list(dep_tree_root.side_effects),
    )
    if conversational_overview:
        (vendor_dir / "OVERVIEW.md").write_text(conversational_overview, encoding="utf-8")
    (vendor_dir / "CLAUDE.md").write_text(render_vendor_claude_md(digest), encoding="utf-8")
    return digest


def sync_all(configs: list[VendorConfig], project_root: Path) -> list[VendorDigest]:
    """Sync every config in order. No budget/cost gate here — `sync_vendor`
    never makes an AI call; the one AI-call budget gate left in this
    codebase (Phase B enrichment) lives in `cli.py`'s
    `_maybe_run_enrichment`, gating `codecompass.enrichment` directly.
    """
    return [sync_vendor(config, project_root) for config in configs]


def _render_filetree_with_symbol_index(
    tree_root: Path, config: VendorConfig, action_pointer: tuple[str, str] | None
) -> str:
    """The flat symbol index renders as a section within FILETREE.md
    ("alongside the nested tree", architecture/overview.md) rather than a
    separate sidecar file — sync produces five deterministic output files
    per vendor (six for a vendor with an existing enrichment record, which
    additionally gets `OVERVIEW.md`). `tree_root` is the clone root when
    this vendor's clone succeeded this run, else the local-install
    `source_location()` fallback (Phase 13).
    """
    tree_markdown = render_filetree_markdown(
        tree_root, config.ecosystem, action_pointer=action_pointer
    )
    symbol_index = build_symbol_index(tree_root, config.ecosystem)
    if not symbol_index:
        return tree_markdown
    return f"{tree_markdown}\n\n## Symbol index\n\n{symbol_index}"


def rebuild_project_graph(configs: list[VendorConfig], project_root: Path) -> None:
    """Rebuild `context-graph.db` from **every** tracked vendor's current
    state (not just ones `sync_vendor` touched this run — the graph must
    reflect the full current state regardless of which vendors were just
    resynced) plus a fresh scan of the project's own source for vendor
    usage.

    For each config: read `installed_version()`/`repository_url()` (both
    already-existing, no-network-call adapter methods) and collect that
    vendor's own symbol list via `adapter.symbols()` (Phase 62) — the
    generic adapter capability every ecosystem now implements (in-process
    ecosystems inherit `EcosystemAdapter.symbols()`'s own walk+extract
    default; `HaskellAdapter` overrides it with real data from its
    already-computed external-process result, closing `CG-008`). Then
    `usage.resolve_project_usage` detects the project's imports, and each
    `DetectedImport.symbol_name` is resolved against the matching vendor's
    collected symbol list by name — unresolved or no match stays a
    vendor-level fallback edge (`symbol_name=None`), matching
    `uses_edges.symbol_id`'s nullability (`decisions/0031`).

    Phase 12 adds the doc/skill-mapping tables: `doc_mapping.py` collects
    each vendor's `CLAUDE.md`/`OVERVIEW.md` as doc artifacts and derives
    `documents_edges`/`routes_via_edges`/`depends_on_edges` from them plus
    the persisted per-vendor `deptree.json` files; `skill_scan.py` indexes
    every Skill/`.mdc` under the project (not just codecompass's own) and
    derives `skill_mentions_edges`. Both modules are pure transformations
    over already-generated artifacts — no new AI call, no new extraction.

    Phase 21 adds the project's own spec docs: `spec_docs.scan_spec_docs`
    globs the fixed default spec-doc pattern set (`kind='spec_doc'`,
    `origin='project'`), and `doc_mapping.build_doc_relations_edges`
    word-boundary-scans each one's text for mentions of a tracked vendor
    or another doc artifact's name, producing `doc_relations_edges` —
    mechanical only, same posture as every other edge table here.

    Phase 29 widens `build_doc_relations_edges`'s scannable-source set from
    spec docs alone to `spec_doc_rows + vendor_upstream_doc_rows` — a
    vendor's own upstream doc (`kind='vendor_doc'`) can now mechanically
    mention another tracked vendor, a Skill, or another doc artifact too,
    not just be mentioned by this project's own docs (see
    `decisions/0043`).

    Phase 55b widens the *target* set the same way: `spec_doc_rows` is
    now also included in the third argument (previously `vendor_doc_rows
    + vendor_upstream_doc_rows + skill_doc_rows` only), so one project
    spec doc can mechanically mention another — reachable at all only
    once `spec_docs.scan_spec_docs` started populating `name`
    (`_extract_title`), which is what actually makes a `spec_doc` row an
    eligible `mentions_artifact` target (closes `CG-004`).

    Phase 77 replaces the old vendor-usage-gated `source_files`
    population (only a file with a detected tracked-vendor import ever
    became a row) with `source_symbols.discover_source_files` — every
    recognized first-party source file, independent of `vendor.toml`,
    closing `CG-009`. Each recognized file's own top-level implementation
    symbols are extracted via `source_symbols.extract_source_symbols_for_file`
    and persisted to the new `source_symbols` table; `meta.source_index_version`
    is written unconditionally (`"1"`), regardless of whether any
    first-party files were found, so `cli.py::query_source`/
    `query_source_symbol` can distinguish "genuinely indexed, zero
    results" from "first-party source has never been indexed" (mirroring
    `git_topology_status`'s own absence-means-never-synced precedent).
    `source_file_rows`' own set is now a strict superset of the file set
    `usage.resolve_project_usage` can ever detect a vendor import in
    (every suffix that module recognizes maps to a `Language` here too),
    so `uses_edge_rows` always resolves against a path this pass also
    produces. A known, accepted minor inefficiency: this pass and
    `usage.resolve_project_usage` each walk the project tree once,
    independently — deferred, since correctness does not depend on
    merging the two walks and doing so would touch `usage.py`'s own
    well-tested, unrelated walk logic for a performance-only gain no
    evidence yet calls for.
    """
    vendor_rows: list[VendorRow] = []
    symbol_rows: list[SymbolRow] = []
    vendor_symbol_names: dict[str, set[str]] = {}

    for config in configs:
        adapter = get_adapter(config, project_root)
        repository = adapter.repository_url()
        vendor_rows.append(
            VendorRow(
                name=config.name,
                ecosystem=config.ecosystem.value,
                installed_version=adapter.installed_version(),
                repository_url=repository.url if repository else None,
                repository_subdirectory=repository.subdirectory if repository else None,
            )
        )
        symbols = adapter.symbols()
        vendor_symbol_names[config.name] = {s.name for s in symbols}
        for symbol in symbols:
            symbol_rows.append(
                SymbolRow(
                    vendor_name=config.name,
                    name=symbol.name,
                    purpose=symbol.purpose,
                    export_kind=symbol.export_kind,
                    note=symbol.note,
                )
            )

    uses_edge_rows: list[UsesEdgeRow] = []
    for rel_path, detected in usage.resolve_project_usage(project_root, configs):
        known_names = vendor_symbol_names.get(detected.vendor, set())
        symbol_name = detected.symbol_name if detected.symbol_name in known_names else None
        uses_edge_rows.append(
            UsesEdgeRow(
                source_file_path=rel_path,
                vendor_name=detected.vendor,
                symbol_name=symbol_name,
                line=detected.line,
            )
        )

    # Phase 77: first-party source discovery — every recognized source
    # file, independent of vendor.toml (works identically at 0 tracked
    # vendors, since language classification is suffix-based). A strict
    # superset of `usage.resolve_project_usage`'s own vendor-import-
    # matched file set (every suffix that module's own detectors
    # recognize is also a `source_symbols.Language`), so `uses_edge_rows`
    # above always resolves against a path this pass also produces.
    source_file_rows: list[SourceFileRow] = []
    source_symbol_rows: list[SourceSymbolRow] = []
    for rel_path, language in source_symbols.discover_source_files(project_root):
        absolute_path = project_root / rel_path
        try:
            content_hash = hashlib.sha256(absolute_path.read_bytes()).hexdigest()
        except OSError:
            content_hash = None
        extraction = source_symbols.extract_source_symbols_for_file(absolute_path, language)
        source_file_rows.append(
            SourceFileRow(
                path=rel_path,
                language=language.value,
                content_hash=content_hash,
                symbol_index_status=extraction.status.value,
                symbol_index_diagnostic=extraction.diagnostic,
            )
        )
        for symbol in extraction.symbols:
            source_symbol_rows.append(
                SourceSymbolRow(
                    source_file_path=rel_path,
                    name=symbol.name,
                    kind=symbol.kind,
                    line=symbol.line,
                    purpose=symbol.purpose,
                    exposure=symbol.exposure,
                )
            )

    vendor_doc_rows = collect_vendor_doc_artifacts(configs, project_root)
    vendor_upstream_doc_rows = collect_vendor_upstream_doc_artifacts(configs, project_root)
    skill_doc_rows = skill_scan.scan_skills(project_root, configs)
    spec_doc_rows = spec_docs.scan_spec_docs(project_root)
    doc_artifact_rows = (
        vendor_doc_rows + vendor_upstream_doc_rows + skill_doc_rows + spec_doc_rows
    )

    doc_chunk_rows = build_doc_chunks(doc_artifact_rows, project_root)
    documents_edge_rows = build_documents_edges(doc_artifact_rows, symbol_rows, project_root)
    skill_mentions_edge_rows = skill_scan.build_skill_mentions_edges(
        skill_doc_rows, configs, source_file_rows, project_root
    )
    routes_via_edge_rows = build_routes_via_edges(configs, doc_artifact_rows)
    depends_on_edge_rows = build_depends_on_edges(configs, project_root)
    doc_relations_edge_rows = build_doc_relations_edges(
        spec_doc_rows + vendor_upstream_doc_rows,
        configs,
        vendor_doc_rows + vendor_upstream_doc_rows + skill_doc_rows + spec_doc_rows,
        project_root,
    )

    topology = git_topology.detect_git_topology(project_root)
    git_repository_rows, git_worktree_rows, git_submodule_rows = _build_git_topology_rows(topology)

    conn = open_graph(project_root)
    try:
        rebuild_deterministic(
            conn,
            vendors=vendor_rows,
            source_files=source_file_rows,
            symbols=symbol_rows,
            uses_edges=uses_edge_rows,
            doc_artifacts=doc_artifact_rows,
            doc_chunks=doc_chunk_rows,
            documents_edges=documents_edge_rows,
            skill_mentions_edges=skill_mentions_edge_rows,
            routes_via_edges=routes_via_edge_rows,
            depends_on_edges=depends_on_edge_rows,
            doc_relations_edges=doc_relations_edge_rows,
            git_repositories=git_repository_rows,
            git_worktrees=git_worktree_rows,
            git_submodules=git_submodule_rows,
            git_topology_status=topology.status.value,
            git_topology_reason=topology.reason,
            source_symbols=source_symbol_rows,
            source_index_version="1",
        )
    finally:
        conn.close()


def _build_git_topology_rows(
    topology: git_topology.RepositoryTopology,
) -> tuple[list[GitRepositoryRow], list[GitWorktreeRow], list[GitSubmoduleRow]]:
    """Converts `git_topology.detect_git_topology`'s own plain dataclasses
    into `graph.py` row types — the same "detection module stays
    graph-agnostic, `sync.py` is the only place that converts" pattern
    `usage.DetectedImport` -> `graph.UsesEdgeRow` already establishes.
    Empty for `not_git`/`unavailable` (`topology.common_dir` is `None`
    for both — confirmed by `detect_git_topology`'s own contract), not a
    special case here.
    """
    if topology.common_dir is None:
        return [], [], []

    repository_rows = [
        GitRepositoryRow(common_dir=topology.common_dir, origin_url=topology.origin_url)
    ]
    worktree_rows = [
        GitWorktreeRow(
            repository_common_dir=topology.common_dir,
            worktree_path=w.path,
            is_current=w.is_current,
            branch=w.branch,
            is_detached=w.is_detached,
            head_commit=w.head_commit,
            is_dirty=w.is_dirty,
            is_bare=w.is_bare,
            is_locked=w.is_locked,
            is_prunable=w.is_prunable,
        )
        for w in topology.worktrees
    ]
    submodule_rows = [
        GitSubmoduleRow(
            parent_repository_common_dir=topology.common_dir,
            path=s.path,
            is_path_safe=s.is_path_safe,
            child_repository_url=s.child_repository_url,
            pinned_commit=s.pinned_commit,
            is_initialized=s.is_initialized,
            checked_out_commit=s.checked_out_commit,
            revision_matches_pin=s.revision_matches_pin,
            child_branch=s.child_branch,
            child_is_dirty=s.child_is_dirty,
        )
        for s in topology.submodules
    ]
    return repository_rows, worktree_rows, submodule_rows


def _copy_source_snapshot(source: Path, dest: Path) -> None:
    """Copy `source` to `dest`, stripping node_modules/dist/build/.git-
    style noise only — looser than filetree.py's prune list, since an
    enriched vendor's own test suite is often exactly what someone wants
    to reference in standalone mode (decisions/0004). Fully overwrites
    `dest` on each call.
    """
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest, ignore=shutil.ignore_patterns(*_SNAPSHOT_PRUNE_NAMES))
