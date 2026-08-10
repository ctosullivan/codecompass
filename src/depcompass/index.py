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
from dataclasses import dataclass
from pathlib import Path

from depcompass.core import Depth, VendorConfig

_START_MARKER = "<!-- depcompass:start -->"
_END_MARKER = "<!-- depcompass:end -->"
_MARKER_BLOCK_RE = re.compile(
    re.escape(_START_MARKER) + r".*?" + re.escape(_END_MARKER), re.DOTALL
)
_INSTALLED_VERSION_RE = re.compile(r"\*\*Installed version:\*\*\s*(\S+)")

_CONSULT_WHEN_BY_DEPTH = {
    Depth.SURFACE: "general usage questions",
    Depth.FULL: "API questions and known gotchas",
}

_ROUTING_INSTRUCTION = (
    "The table below lists dependencies with a generated reference digest "
    "under `vendor/<name>/`. Consult the linked digest before relying on "
    "training knowledge for these libraries."
)


@dataclass
class RoutingRow:
    """One vendor's routing-table row. `version` is `None` if the vendor
    hasn't been synced yet — `index` reads persisted state, it never
    triggers a sync itself.
    """

    config: VendorConfig
    version: str | None


def load_routing_rows(configs: list[VendorConfig], project_root: Path) -> list[RoutingRow]:
    rows = []
    for config in configs:
        claude_md_path = project_root / "vendor" / config.name / "CLAUDE.md"
        version = None
        if claude_md_path.exists():
            match = _INSTALLED_VERSION_RE.search(claude_md_path.read_text(encoding="utf-8"))
            version = match.group(1) if match else None
        rows.append(RoutingRow(config=config, version=version))
    return rows


def render_routing_table(rows: list[RoutingRow]) -> str:
    lines = [
        _ROUTING_INSTRUCTION,
        "",
        "| Vendor | Path | Version | Depth | Deps | Consult when |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        config = row.config
        version = row.version if row.version is not None else "_not synced_"
        deps = f"[DEPTREE.md](./vendor/{config.name}/DEPTREE.md)"
        consult_when = _CONSULT_WHEN_BY_DEPTH[config.depth]
        lines.append(
            f"| {config.name} | `vendor/{config.name}/` | {version} | "
            f"{config.depth.value} | {deps} | {consult_when} |"
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
