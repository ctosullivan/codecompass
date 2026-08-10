"""Per-vendor sync orchestration.

Wires together an ecosystem adapter (Phase 2), Phase 3's tree renderers,
a pruned `vendor/<name>/src/` snapshot copy for `depth = full` vendors,
and per-vendor `CLAUDE.md` templating — writing everything under
`vendor/<name>/`. No AI calls; gap analysis is Phase 5. See
planning/phase-4-sync-index-init.md.
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

_SNAPSHOT_PRUNE_NAMES = ("node_modules", "dist", "build", ".git", "__pycache__", ".venv", "venv")


def sync_vendor(config: VendorConfig, project_root: Path) -> VendorDigest:
    """Orchestrate one vendor end to end. Deterministic and idempotent —
    every output file listed below is fully overwritten on each call, no
    diffing against previous output.
    """
    adapter = get_adapter(config, project_root)
    installed_version = adapter.installed_version()
    api_surface = adapter.readme_and_api_surface()
    dep_tree_root = adapter.dependency_tree()
    source_location = adapter.source_location()

    vendor_dir = project_root / "vendor" / config.name
    vendor_dir.mkdir(parents=True, exist_ok=True)

    dep_tree_markdown = render_deptree_markdown(dep_tree_root)
    (vendor_dir / "DEPTREE.md").write_text(dep_tree_markdown, encoding="utf-8")
    (vendor_dir / "deptree.json").write_text(
        json.dumps(render_deptree_json(dep_tree_root), indent=2), encoding="utf-8"
    )

    file_tree_markdown = _render_filetree_with_symbol_index(source_location, config)
    (vendor_dir / "FILETREE.md").write_text(file_tree_markdown, encoding="utf-8")
    (vendor_dir / "filetree.json").write_text(
        json.dumps(render_filetree_json(source_location, config.ecosystem), indent=2),
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
        side_effects=list(dep_tree_root.side_effects),
    )
    (vendor_dir / "CLAUDE.md").write_text(render_vendor_claude_md(digest), encoding="utf-8")
    return digest


def sync_all(configs: list[VendorConfig], project_root: Path) -> list[VendorDigest]:
    return [sync_vendor(config, project_root) for config in configs]


def _render_filetree_with_symbol_index(source_location: Path, config: VendorConfig) -> str:
    """The flat symbol index renders as a section within FILETREE.md
    ("alongside the nested tree", architecture/overview.md) rather than a
    separate sidecar file — sync produces five output files per vendor,
    not six.
    """
    tree_markdown = render_filetree_markdown(source_location, config.ecosystem)
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
