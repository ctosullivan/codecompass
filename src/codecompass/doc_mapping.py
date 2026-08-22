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
    DocumentsEdgeRow,
    RoutesViaEdgeRow,
    SymbolRow,
)

_DEPTREE_FILENAME = "deptree.json"


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


def build_documents_edges(
    doc_artifact_rows: list[DocArtifactRow],
    symbol_rows: list[SymbolRow],
    project_root: Path,
) -> list[DocumentsEdgeRow]:
    """For each `claude_md`/`overview` doc artifact, read its file text off
    disk and word-boundary-match it against *that same vendor's* known
    symbol names — one edge per match. A coverage heuristic ("this
    symbol's name appears in the vendor's own digest text"), not a
    quality judgment.
    """
    symbols_by_vendor: dict[str, list[str]] = defaultdict(list)
    for symbol in symbol_rows:
        symbols_by_vendor[symbol.vendor_name].append(symbol.name)

    edges: list[DocumentsEdgeRow] = []
    for row in doc_artifact_rows:
        if row.kind not in ("claude_md", "overview") or row.vendor_name is None:
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
