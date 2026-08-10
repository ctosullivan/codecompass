"""Per-vendor sync orchestration.

Wires together an ecosystem adapter (Phase 2), Phase 3's tree renderers,
Phase 5's AI-gated gap analysis (`depth = full` + `context_path` vendors
only), a pruned `vendor/<name>/src/` snapshot copy for `depth = full`
vendors, and per-vendor `CLAUDE.md` templating — writing everything under
`vendor/<name>/`. See planning/phase-4-sync-index-init.md and
planning/phase-5-gap-analysis.md.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from depcompass.adapters import get_adapter
from depcompass.claude_md import render_vendor_claude_md
from depcompass.core import Depth, VendorConfig, VendorDigest
from depcompass.deptree import render_deptree_json, render_deptree_markdown
from depcompass.filetree import build_symbol_index, render_filetree_json, render_filetree_markdown
from depcompass.gap_analysis import GapAnalysisError, check_budget, generate_gap_analysis

_SNAPSHOT_PRUNE_NAMES = ("node_modules", "dist", "build", ".git", "__pycache__", ".venv", "venv")


def sync_vendor(config: VendorConfig, project_root: Path) -> VendorDigest:
    """Orchestrate one vendor end to end. Deterministic and idempotent —
    every output file listed below is fully overwritten on each call, no
    diffing against previous output.

    A `depth = full` vendor's gap-analysis failure is caught locally: the
    vendor still gets its deterministic output (with an explicit
    "unavailable" note in `CLAUDE.md` instead of a silently missing
    section), it just doesn't propagate out of this function. Budget
    enforcement happens in `sync_all`, before any vendor's `sync_vendor`
    runs — this function never checks budget itself.
    """
    adapter = get_adapter(config, project_root)
    installed_version = adapter.installed_version()
    api_surface = adapter.readme_and_api_surface()

    gap_analysis = None
    gap_analysis_error = None
    if config.depth is Depth.FULL and config.context_path:
        try:
            gap_analysis = generate_gap_analysis(config, api_surface, project_root)
        except GapAnalysisError as exc:
            gap_analysis_error = str(exc)
    action_pointer = None
    if gap_analysis and gap_analysis.action_pointer_file:
        action_pointer = (gap_analysis.action_pointer_file, gap_analysis.action_pointer_note)

    dep_tree_root = adapter.dependency_tree()
    source_location = adapter.source_location()

    vendor_dir = project_root / "vendor" / config.name
    vendor_dir.mkdir(parents=True, exist_ok=True)

    dep_tree_markdown = render_deptree_markdown(dep_tree_root)
    (vendor_dir / "DEPTREE.md").write_text(dep_tree_markdown, encoding="utf-8")
    (vendor_dir / "deptree.json").write_text(
        json.dumps(render_deptree_json(dep_tree_root), indent=2), encoding="utf-8"
    )

    file_tree_markdown = _render_filetree_with_symbol_index(
        source_location, config, action_pointer
    )
    (vendor_dir / "FILETREE.md").write_text(file_tree_markdown, encoding="utf-8")
    (vendor_dir / "filetree.json").write_text(
        json.dumps(
            render_filetree_json(source_location, config.ecosystem, action_pointer=action_pointer),
            indent=2,
        ),
        encoding="utf-8",
    )

    if config.depth is Depth.FULL:
        _copy_source_snapshot(source_location, vendor_dir / "src")

    digest = VendorDigest(
        config=config,
        installed_version=installed_version,
        file_tree=file_tree_markdown,
        dep_tree=dep_tree_markdown,
        api_surface=api_surface,
        gap_analysis=gap_analysis.technical if gap_analysis else None,
        conversational_overview=gap_analysis.conversational_overview if gap_analysis else None,
        gap_analysis_error=gap_analysis_error,
        action_pointer_file=gap_analysis.action_pointer_file if gap_analysis else None,
        action_pointer_note=gap_analysis.action_pointer_note if gap_analysis else None,
        side_effects=list(dep_tree_root.side_effects),
    )
    if gap_analysis:
        (vendor_dir / "OVERVIEW.md").write_text(
            gap_analysis.conversational_overview, encoding="utf-8"
        )
    (vendor_dir / "CLAUDE.md").write_text(render_vendor_claude_md(digest), encoding="utf-8")
    return digest


def sync_all(
    configs: list[VendorConfig], project_root: Path, *, budget: float | None = None
) -> list[VendorDigest]:
    """`check_budget` runs first and raises `GapAnalysisError` — before
    any vendor's `sync_vendor` is called, and therefore before any output
    is written this invocation — if the projected gap-analysis cost for
    this batch exceeds `budget`.
    """
    check_budget(configs, budget)
    return [sync_vendor(config, project_root) for config in configs]


def _render_filetree_with_symbol_index(
    source_location: Path, config: VendorConfig, action_pointer: tuple[str, str] | None
) -> str:
    """The flat symbol index renders as a section within FILETREE.md
    ("alongside the nested tree", architecture/overview.md) rather than a
    separate sidecar file — sync produces five deterministic output files
    per vendor (six for a `depth = full` vendor whose gap analysis
    succeeds, which additionally gets `OVERVIEW.md`).
    """
    tree_markdown = render_filetree_markdown(
        source_location, config.ecosystem, action_pointer=action_pointer
    )
    symbol_index = build_symbol_index(source_location, config.ecosystem)
    if not symbol_index:
        return tree_markdown
    return f"{tree_markdown}\n\n## Symbol index\n\n{symbol_index}"


def _copy_source_snapshot(source: Path, dest: Path) -> None:
    """Copy `source` to `dest`, stripping node_modules/dist/build/.git-
    style noise only — looser than filetree.py's prune list, since a
    depth=full vendor's own test suite is often exactly what someone
    wants to reference in standalone mode (decisions/0004). Fully
    overwrites `dest` on each call.
    """
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest, ignore=shutil.ignore_patterns(*_SNAPSHOT_PRUNE_NAMES))
