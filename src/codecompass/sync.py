"""Per-vendor sync orchestration.

Wires together an ecosystem adapter (Phase 2), Phase 3's tree renderers,
Phase 7's AI-gated grounded-description generation (`depth = full`
vendors, unconditional — replaced Phase 5's `context_path`-gated gap
analysis, decisions/0019), a `vendor/<name>/src/` snapshot for `depth =
full` vendors (now sourced from the vendor's own upstream repository via
`codecompass.source_resolution`, not the local install — decisions/0021),
and per-vendor `CLAUDE.md` templating — writing everything under
`vendor/<name>/`. See planning/phase-4-sync-index-init.md,
planning/phase-5-gap-analysis.md, and
planning/phase-7-bootstrap-and-promote.md.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from codecompass.adapters import get_adapter
from codecompass.claude_md import render_vendor_claude_md
from codecompass.core import Depth, VendorConfig, VendorDigest
from codecompass.deptree import render_deptree_json, render_deptree_markdown
from codecompass.filetree import build_symbol_index, render_filetree_json, render_filetree_markdown
from codecompass.grounded_description import (
    GroundedDescriptionError,
    check_budget,
    generate_grounded_description,
)
from codecompass.source_resolution import SourceResolutionError, resolve_and_clone

_SNAPSHOT_PRUNE_NAMES = ("node_modules", "dist", "build", ".git", "__pycache__", ".venv", "venv")


def sync_vendor(config: VendorConfig, project_root: Path) -> VendorDigest:
    """Orchestrate one vendor end to end. Deterministic and idempotent —
    every output file listed below is fully overwritten on each call, no
    diffing against previous output.

    A `depth = full` vendor's description failure is caught locally: the
    vendor still gets its deterministic output (with an explicit
    "unavailable" note in `CLAUDE.md` instead of a silently missing
    section), it just doesn't propagate out of this function. Two
    distinct failure points are handled separately: if source resolution/
    cloning itself fails, `vendor/<name>/src/` falls back to the old
    local-install-sourced snapshot (decisions/0004) so standalone
    browsing still has *something*; if cloning succeeds but the AI call
    fails, the real clone is kept as-is (better than discarding it for a
    stale local-install copy). Budget enforcement happens in `sync_all`,
    before any vendor's `sync_vendor` runs — this function never checks
    budget itself.
    """
    adapter = get_adapter(config, project_root)
    installed_version = adapter.installed_version()
    api_surface = adapter.readme_and_api_surface()
    dep_tree_root = adapter.dependency_tree()
    source_location = adapter.source_location()

    vendor_dir = project_root / "vendor" / config.name
    vendor_dir.mkdir(parents=True, exist_ok=True)

    description = None
    description_error = None
    if config.depth is Depth.FULL:
        src_dest = vendor_dir / "src"
        try:
            repo_root = resolve_and_clone(adapter, src_dest)
        except SourceResolutionError as exc:
            description_error = str(exc)
            _copy_source_snapshot(source_location, src_dest)
        else:
            try:
                description = generate_grounded_description(config, repo_root)
            except GroundedDescriptionError as exc:
                description_error = str(exc)

    action_pointer = None
    if description and description.action_pointer_file:
        action_pointer = (description.action_pointer_file, description.action_pointer_note)

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

    digest = VendorDigest(
        config=config,
        installed_version=installed_version,
        file_tree=file_tree_markdown,
        dep_tree=dep_tree_markdown,
        api_surface=api_surface,
        technical_description=description.technical if description else None,
        conversational_overview=description.conversational_overview if description else None,
        description_error=description_error,
        action_pointer_file=description.action_pointer_file if description else None,
        action_pointer_note=description.action_pointer_note if description else None,
        side_effects=list(dep_tree_root.side_effects),
    )
    if description:
        (vendor_dir / "OVERVIEW.md").write_text(
            description.conversational_overview, encoding="utf-8"
        )
    (vendor_dir / "CLAUDE.md").write_text(render_vendor_claude_md(digest), encoding="utf-8")
    return digest


def sync_all(
    configs: list[VendorConfig], project_root: Path, *, budget: float | None = None
) -> list[VendorDigest]:
    """`check_budget` runs first and raises `GroundedDescriptionError` —
    before any vendor's `sync_vendor` is called, and therefore before any
    output is written this invocation — if the projected generation cost
    for this batch exceeds `budget`.
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
