"""Idempotent routing-table injection into the project root CLAUDE.md.

Deliberately reads already-synced per-vendor `CLAUDE.md` files rather than
re-running `sync` — `index` must stay cheap and side-effect-free even
after Phase 5 adds an AI-gated gap-analysis step to `sync`; if `index`
triggered `sync` internally, running it would start silently paying that
cost too. See architecture/overview.md's "Two consumption modes" section
and planning/phase-4-sync-index-init.md's Design decisions (this exact
detail was left open there for implementation time to settle).
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from codecompass.claude_md import read_installed_version
from codecompass.core import VendorConfig
from codecompass.graph import has_enrichment

_START_MARKER = "<!-- codecompass:start -->"
_END_MARKER = "<!-- codecompass:end -->"
_MARKER_BLOCK_RE = re.compile(
    re.escape(_START_MARKER) + r".*?" + re.escape(_END_MARKER), re.DOTALL
)

_GRAPH_DB_FILENAME = "context-graph.db"

_CONSULT_WHEN_BY_ENRICHED = {
    True: "API questions and known gotchas",
    False: "general usage questions",
}

_ROUTING_INSTRUCTION = (
    "The table below lists dependencies with a generated reference digest "
    "under `vendor/<name>/`. Consult the linked digest before relying on "
    "training knowledge for these libraries."
)


def _open_graph_readonly(project_root: Path) -> sqlite3.Connection | None:
    """`None` if `context-graph.db` doesn't exist yet — a project that's
    only run `init`/one `sync <vendor>`, never a whole-project sync. A
    genuine read-only connection (SQLite URI `mode=ro`), not
    `graph.open_graph` — `index` must stay cheap and side-effect-free
    (this module's own docstring), and `open_graph` both creates the file
    if absent and issues `CREATE TABLE IF NOT EXISTS` on every call, which
    is not appropriate for what should be a pure read.
    """
    db_path = project_root / _GRAPH_DB_FILENAME
    if not db_path.exists():
        return None
    return sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)


@dataclass
class RoutingRow:
    """One vendor's routing-table row. `version` is `None` if the vendor
    hasn't been synced yet — `index` reads persisted state, it never
    triggers a sync itself. `enriched` is graph-derived (`has_enrichment`)
    rather than `config.depth`-derived — `False` (not just for an unsynced
    vendor but for any project without a `context-graph.db` yet) rather
    than erroring.
    """

    config: VendorConfig
    version: str | None
    enriched: bool


def load_routing_rows(configs: list[VendorConfig], project_root: Path) -> list[RoutingRow]:
    conn = _open_graph_readonly(project_root)
    try:
        rows = []
        for config in configs:
            claude_md_path = project_root / "vendor" / config.name / "CLAUDE.md"
            enriched = conn is not None and has_enrichment(conn, config.name)
            rows.append(
                RoutingRow(
                    config=config,
                    version=read_installed_version(claude_md_path),
                    enriched=enriched,
                )
            )
        return rows
    finally:
        if conn is not None:
            conn.close()


def render_routing_table(rows: list[RoutingRow]) -> str:
    lines = [
        _ROUTING_INSTRUCTION,
        "",
        "| Vendor | Path | Version | Enriched | Deps | Consult when |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        config = row.config
        version = row.version if row.version is not None else "_not synced_"
        deps = f"[DEPTREE.md](./vendor/{config.name}/DEPTREE.md)"
        enriched_label = "yes" if row.enriched else "no"
        consult_when = _CONSULT_WHEN_BY_ENRICHED[row.enriched]
        lines.append(
            f"| {config.name} | `vendor/{config.name}/` | {version} | "
            f"{enriched_label} | {deps} | {consult_when} |"
        )
    return "\n".join(lines)


def update_root_claude_md(project_root: Path, table_md: str) -> None:
    """Append the marker block on first run; `re.sub` (DOTALL) replaces
    just the marked block on regeneration, leaving hand-written content
    around it untouched.
    """
    claude_md_path = project_root / "CLAUDE.md"
    existing = claude_md_path.read_text(encoding="utf-8") if claude_md_path.exists() else ""
    block = f"{_START_MARKER}\n{table_md}\n{_END_MARKER}"

    if _MARKER_BLOCK_RE.search(existing):
        updated = _MARKER_BLOCK_RE.sub(block, existing)
    else:
        separator = "\n\n" if existing and not existing.endswith("\n\n") else ""
        updated = f"{existing}{separator}{block}\n"

    claude_md_path.write_text(updated, encoding="utf-8")
