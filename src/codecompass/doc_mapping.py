"""Doc-artifact and dependency-edge mapping: pure transformations over
already-generated per-vendor artifacts (`vendor/<name>/CLAUDE.md`,
`vendor/<name>/OVERVIEW.md`, `vendor/<name>/deptree.json`) and the doc
artifacts `skill_scan.py` collects — no new AI call, no new symbol
extraction. See planning/phase-12-doc-and-wide-skill-mapping.md.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from codecompass.core import VendorConfig
from codecompass.graph import (
    DependsOnEdgeRow,
    DocArtifactRow,
    DocRelationEdgeRow,
    DocumentsEdgeRow,
    RoutesViaEdgeRow,
    SymbolRow,
)

_DEPTREE_FILENAME = "deptree.json"

# Root-level-only, fixed filename set (Phase 27, decisions/0041) — not a
# recursive **/*.md glob, which would sweep up a vendor's own
# node_modules/build output/nested-package docs inside a monorepo-shaped
# clone, and not every language's `docs/`-folder convention either (a
# larger dependency's own `docs/` can hold hundreds of arbitrarily nested,
# uncurated files). `README*.md` matches every root-level README variant a
# clone actually has (`README.md`, `README.cn.md`, etc.) rather than just
# the bare `README.md` — simplest pattern that still satisfies the plan's
# examples, at the cost of also picking up a vendor's own translated
# READMEs when it has them at the root (see decisions/0041's Alternatives
# considered).
_VENDOR_UPSTREAM_DOC_GLOB_PATTERNS = (
    "README*.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "MIGRATION.md",
)


def collect_vendor_doc_artifacts(
    configs: list[VendorConfig], project_root: Path
) -> list[DocArtifactRow]:
    """One `kind='claude_md'` row per tracked vendor's `vendor/<name>/
    CLAUDE.md` and one `kind='overview'` row for `vendor/<name>/
    OVERVIEW.md` if it exists (only currently-`promote`d, `depth=full`
    vendors have one) — both `origin='codecompass_vendor'`. A vendor
    that hasn't been synced yet (no `CLAUDE.md` on disk) is skipped
    rather than pointing a doc-artifact row at a nonexistent file.
    """
    rows: list[DocArtifactRow] = []
    for config in configs:
        vendor_dir = project_root / "vendor" / config.name

        claude_md = vendor_dir / "CLAUDE.md"
        if claude_md.exists():
            rows.append(
                DocArtifactRow(
                    path=claude_md.relative_to(project_root).as_posix(),
                    kind="claude_md",
                    origin="codecompass_vendor",
                    vendor_name=config.name,
                    name=f"{config.name} CLAUDE.md",
                )
            )

        overview = vendor_dir / "OVERVIEW.md"
        if overview.exists():
            rows.append(
                DocArtifactRow(
                    path=overview.relative_to(project_root).as_posix(),
                    kind="overview",
                    origin="codecompass_vendor",
                    vendor_name=config.name,
                    name=f"{config.name} OVERVIEW.md",
                )
            )
    return rows


def collect_vendor_upstream_doc_artifacts(
    configs: list[VendorConfig], project_root: Path
) -> list[DocArtifactRow]:
    """One `kind='vendor_doc'` row per matched top-level doc file found
    directly under each tracked vendor's *cloned source* root
    (`vendor/<name>/src/` — the clone root `sync.sync_vendor`/
    `source_resolution.resolve_and_clone` actually write to, not
    `vendor/<name>/` itself, which only ever holds codecompass's own
    generated `CLAUDE.md`/`OVERVIEW.md`/`FILETREE.md`/`DEPTREE.md`). All
    rows are `origin='vendor_upstream'` — deliberately distinct from
    `collect_vendor_doc_artifacts`'s `origin='codecompass_vendor'` above:
    this is upstream-*authored* content codecompass merely indexes, not
    content it generated itself (see decisions/0041).

    Matched against `_VENDOR_UPSTREAM_DOC_GLOB_PATTERNS`, root-level only —
    no recursion into subdirectories (so a vendor's own nested `docs/`
    folder, `node_modules`, or monorepo sub-packages are never swept up). A
    vendor with no clone on disk yet (unresolved source, or not yet synced)
    is skipped entirely, the same tolerant posture `collect_vendor_doc_
    artifacts` already takes toward a not-yet-synced vendor's missing
    `CLAUDE.md`.
    """
    rows: list[DocArtifactRow] = []
    for config in configs:
        clone_root = project_root / "vendor" / config.name / "src"
        if not clone_root.is_dir():
            continue

        matched: set[Path] = set()
        for pattern in _VENDOR_UPSTREAM_DOC_GLOB_PATTERNS:
            matched.update(p for p in clone_root.glob(pattern) if p.is_file())

        for doc_path in sorted(matched):
            rows.append(
                DocArtifactRow(
                    path=doc_path.relative_to(project_root).as_posix(),
                    kind="vendor_doc",
                    origin="vendor_upstream",
                    vendor_name=config.name,
                    name=f"{config.name} {doc_path.name}",
                )
            )
    return rows


def build_documents_edges(
    doc_artifact_rows: list[DocArtifactRow],
    symbol_rows: list[SymbolRow],
    project_root: Path,
) -> list[DocumentsEdgeRow]:
    """For each `claude_md`/`overview`/`vendor_doc` doc artifact, read its
    file text off disk and word-boundary-match it against *that same
    vendor's* known symbol names — one edge per match. A coverage
    heuristic ("this symbol's name appears in the vendor's own digest
    text"), not a quality judgment. `vendor_doc` (Phase 27) was added to
    this filter in Phase 29 — a vendor's own upstream README is at least
    as authoritative a source of "this doc documents this symbol" as
    codecompass's own generated `CLAUDE.md`/`OVERVIEW.md`, and it already
    carries `vendor_name` (Phase 27), so no other change was needed here.
    """
    symbols_by_vendor: dict[str, list[str]] = defaultdict(list)
    for symbol in symbol_rows:
        symbols_by_vendor[symbol.vendor_name].append(symbol.name)

    edges: list[DocumentsEdgeRow] = []
    for row in doc_artifact_rows:
        if row.kind not in ("claude_md", "overview", "vendor_doc") or row.vendor_name is None:
            continue
        vendor_symbols = symbols_by_vendor.get(row.vendor_name)
        if not vendor_symbols:
            continue
        text = (project_root / row.path).read_text(encoding="utf-8")
        for symbol_name in vendor_symbols:
            if re.search(rf"\b{re.escape(symbol_name)}\b", text):
                edges.append(
                    DocumentsEdgeRow(
                        doc_artifact_path=row.path,
                        vendor_name=row.vendor_name,
                        symbol_name=symbol_name,
                    )
                )
    return edges


def build_routes_via_edges(
    configs: list[VendorConfig], doc_artifact_rows: list[DocArtifactRow]
) -> list[RoutesViaEdgeRow]:
    """Route each vendor to its own per-vendor Skill doc artifact
    (`kind='skill'`, `origin='codecompass_vendor'`) if one exists;
    otherwise to the shared tool-level Skill (`kind='skill'`,
    `origin='codecompass_tool'`) if *that* is present in
    `doc_artifact_rows`. Operationalizes `decisions/0013` point 6 as real
    queryable data.
    """
    per_vendor_skill: dict[str, str] = {}
    tool_skill_path: str | None = None
    for row in doc_artifact_rows:
        if row.kind != "skill":
            continue
        if row.origin == "codecompass_vendor" and row.vendor_name is not None:
            per_vendor_skill.setdefault(row.vendor_name, row.path)
        elif row.origin == "codecompass_tool" and tool_skill_path is None:
            tool_skill_path = row.path

    edges: list[RoutesViaEdgeRow] = []
    for config in configs:
        target = per_vendor_skill.get(config.name, tool_skill_path)
        if target is not None:
            edges.append(RoutesViaEdgeRow(vendor_name=config.name, doc_artifact_path=target))
    return edges


# Closed allow-set of scannable relationship-source kinds (Phase 29,
# decisions/0043) — deliberately not "any kind not otherwise excluded".
# A codecompass-*generated* artifact (`claude_md`, `overview`, `skill`,
# `cursor_mdc`, `slash_command`) mentioning a vendor by name is structural,
# not signal, so it stays out of this set; adding a new source kind later
# is a deliberate one-line change here, not an accidental side effect of
# some other doc kind's origin changing.
_DOC_RELATION_SOURCE_KINDS = frozenset({"spec_doc", "vendor_doc"})


def build_doc_relations_edges(
    source_doc_rows: list[DocArtifactRow],
    configs: list[VendorConfig],
    other_doc_artifact_rows: list[DocArtifactRow],
    project_root: Path,
) -> list[DocRelationEdgeRow]:
    """For each scannable source doc — `kind` in `_DOC_RELATION_SOURCE_KINDS`
    (`spec_doc`, `vendor_doc`; a closed allow-set, see decisions/0043),
    non-matching rows in `source_doc_rows` are skipped — read its file text
    off disk once and word-boundary-match it
    (`re.search(rf"\\b{re.escape(name)}\\b", text)`, same helper pattern as
    `build_documents_edges`/`skill_scan.build_skill_mentions_edges`)
    against: (a) every tracked vendor's name
    (`relation_kind='mentions_dependency'`), and (b) every *other* doc
    artifact's `name` field — a Skill's frontmatter `name`, a dependency
    doc's `f"{vendor} CLAUDE.md"`-style name
    (`relation_kind='mentions_artifact'`). A doc artifact with no `name`
    set is never a match target — nothing to word-boundary-search for.

    Self-mention exclusion (Phase 29): a `vendor_doc` source row's own
    vendor (its `vendor_name`) never produces a `mentions_dependency` edge
    targeting that same vendor — a package's own README mentioning its own
    name is guaranteed, universal noise, unlike a spec doc mentioning a
    vendor, or a vendor doc mentioning a *different* tracked vendor, both
    of which are real evidence of a relationship. No equivalent exclusion
    applies to `mentions_artifact` edges, and none applies to `spec_doc`
    sources at all (a spec doc has no `vendor_name` of its own to compare
    against) — see decisions/0043.

    Source-doc-outward scanning only (Phase 21's Explicitly deferred
    section, widened to vendor docs by Phase 29): a Skill's or dependency
    doc's own body mentioning a spec/vendor doc by name is not scanned for
    here, and never will be from this function — that's a distinct,
    deliberately deferred direction.
    """
    vendor_names = [config.name for config in configs]
    named_artifacts = [row for row in other_doc_artifact_rows if row.name]

    edges: list[DocRelationEdgeRow] = []
    for row in source_doc_rows:
        if row.kind not in _DOC_RELATION_SOURCE_KINDS:
            continue
        text = (project_root / row.path).read_text(encoding="utf-8")

        for vendor_name in vendor_names:
            if row.kind == "vendor_doc" and row.vendor_name == vendor_name:
                continue
            if re.search(rf"\b{re.escape(vendor_name)}\b", text):
                edges.append(
                    DocRelationEdgeRow(
                        source_doc_artifact_path=row.path,
                        relation_kind="mentions_dependency",
                        target_vendor_name=vendor_name,
                    )
                )

        for artifact in named_artifacts:
            if re.search(rf"\b{re.escape(artifact.name)}\b", text):
                edges.append(
                    DocRelationEdgeRow(
                        source_doc_artifact_path=row.path,
                        relation_kind="mentions_artifact",
                        target_doc_artifact_path=artifact.path,
                    )
                )

    return edges


def _flatten_deptree(node: dict, out: dict[str, set[str]] | None = None) -> dict[str, set[str]]:
    """Walks a `deptree.render_deptree_json`-shaped tree into a flat
    `name -> {versions}` map, resolving `{"ref": "name@version"}` back-
    references via `rpartition("@")` (not `split`) so scoped npm names
    like `@babel/core` — which themselves contain `@` — parse correctly.
    Mirrors `staleness._flatten`'s approach; duplicated locally rather
    than imported, consistent with this project's existing style of
    small, module-local private helpers.
    """
    if out is None:
        out = {}
    if "ref" in node:
        name, sep, version = node["ref"].rpartition("@")
        if sep:
            out.setdefault(name, set()).add(version)
        return out
    name = node.get("name")
    version = node.get("version")
    if name is not None and version is not None:
        out.setdefault(name, set()).add(version)
    for child in node.get("children", []):
        _flatten_deptree(child, out)
    return out


def build_depends_on_edges(
    configs: list[VendorConfig], project_root: Path
) -> list[DependsOnEdgeRow]:
    """For each tracked vendor, read its persisted `vendor/<name>/
    deptree.json` and flatten it — emitting a `Vendor → Vendor` edge
    wherever a flattened name matches another *tracked* vendor's name
    (checked against `configs`, not the flattened dependency's own
    version). An untracked transitive dependency isn't a graph node, so
    no edge for it. A missing or corrupt `deptree.json` (vendor not yet
    synced) is skipped, best-effort — same tolerant posture
    `staleness._detect_transitive_drift` already takes toward this exact
    file.
    """
    tracked_names = {config.name for config in configs}
    edges: list[DependsOnEdgeRow] = []
    for config in configs:
        deptree_path = project_root / "vendor" / config.name / _DEPTREE_FILENAME
        if not deptree_path.exists():
            continue
        try:
            tree = json.loads(deptree_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        flattened = _flatten_deptree(tree)
        for name in sorted(flattened):
            if name != config.name and name in tracked_names:
                edges.append(
                    DependsOnEdgeRow(vendor_name=config.name, depends_on_vendor_name=name)
                )
    return edges
