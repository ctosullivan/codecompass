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
`codecompass.skill_scan`), which rebuilds `context-graph.db` from every
tracked vendor's current state plus a fresh project-source usage scan —
decoupled from `sync_all`'s per-vendor loop on purpose (see
planning/phase-11-project-source-usage-detection.md's Design decisions)
and called only from the two whole-project call sites in `cli.py`. See
planning/phase-4-sync-index-init.md, planning/phase-5-gap-analysis.md,
planning/phase-7-bootstrap-and-promote.md,
planning/phase-11-project-source-usage-detection.md,
planning/phase-12-doc-and-wide-skill-mapping.md, and
planning/phase-16-retire-depth.md.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

from codecompass import skill_scan, usage
from codecompass.adapters import EcosystemAdapter, get_adapter
from codecompass.claude_md import render_vendor_claude_md
from codecompass.core import VendorConfig, VendorDigest
from codecompass.deptree import render_deptree_json, render_deptree_markdown
from codecompass.doc_mapping import (
    build_depends_on_edges,
    build_documents_edges,
    build_routes_via_edges,
    collect_vendor_doc_artifacts,
)
from codecompass.filetree import (
    build_symbol_index,
    iter_source_files,
    render_filetree_json,
    render_filetree_markdown,
)
from codecompass.graph import (
    SourceFileRow,
    SymbolRow,
    UsesEdgeRow,
    VendorRow,
    open_graph,
    rebuild_deterministic,
)
from codecompass.source_resolution import SourceResolutionError, resolve_and_clone
from codecompass.symbols import Symbol, extract_symbols_for_file

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
    vendor's own symbol list via the same walk+extract pairing
    `build_symbol_index` already does internally, just captured as
    structured `Symbol` objects instead of a rendered string. Then
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
        symbols = _collect_vendor_symbols(adapter, config)
        vendor_symbol_names[config.name] = {s.name for s in symbols}
        for symbol in symbols:
            symbol_rows.append(
                SymbolRow(vendor_name=config.name, name=symbol.name, purpose=symbol.purpose)
            )

    source_file_paths: set[str] = set()
    uses_edge_rows: list[UsesEdgeRow] = []
    for rel_path, detected in usage.resolve_project_usage(project_root, configs):
        source_file_paths.add(rel_path)
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
    source_file_rows = [SourceFileRow(path=p) for p in sorted(source_file_paths)]

    vendor_doc_rows = collect_vendor_doc_artifacts(configs, project_root)
    skill_doc_rows = skill_scan.scan_skills(project_root, configs)
    doc_artifact_rows = vendor_doc_rows + skill_doc_rows

    documents_edge_rows = build_documents_edges(doc_artifact_rows, symbol_rows, project_root)
    skill_mentions_edge_rows = skill_scan.build_skill_mentions_edges(
        skill_doc_rows, configs, source_file_rows, project_root
    )
    routes_via_edge_rows = build_routes_via_edges(configs, doc_artifact_rows)
    depends_on_edge_rows = build_depends_on_edges(configs, project_root)

    conn = open_graph(project_root)
    try:
        rebuild_deterministic(
            conn,
            vendors=vendor_rows,
            source_files=source_file_rows,
            symbols=symbol_rows,
            uses_edges=uses_edge_rows,
            doc_artifacts=doc_artifact_rows,
            documents_edges=documents_edge_rows,
            skill_mentions_edges=skill_mentions_edge_rows,
            routes_via_edges=routes_via_edge_rows,
            depends_on_edges=depends_on_edge_rows,
        )
    finally:
        conn.close()


def _collect_vendor_symbols(adapter: EcosystemAdapter, config: VendorConfig) -> list[Symbol]:
    """Same walk+extract pairing `build_symbol_index` uses internally,
    reused rather than duplicated — captured as structured `Symbol`
    objects instead of a rendered string.
    """
    symbols: list[Symbol] = []
    for path in iter_source_files(adapter.source_location()):
        symbols.extend(extract_symbols_for_file(path, config.ecosystem))
    return symbols


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
