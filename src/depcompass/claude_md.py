"""Per-vendor CLAUDE.md template rendering.

See architecture/overview.md's "Per-vendor CLAUDE.md structure" section.
Gap analysis (section 4 in that spec) is populated by Phase 5's AI-gated
step for `depth = full` + `context_path` vendors; omitted entirely (not a
placeholder) for every other vendor. `read_installed_version` reads the
Metadata section's load-bearing line back — this module owns the file
format it targets, so `index.py` (Phase 4) and `staleness.py` (Phase 6)
both call it rather than keeping their own copies of the regex.
"""

from __future__ import annotations

import re
from pathlib import Path

from depcompass.core import VendorDigest

_INSTALLED_VERSION_RE = re.compile(r"\*\*Installed version:\*\*\s*(\S+)")

_GROUNDING_PREAMBLE = (
    "> **Grounding note:** This file describes the version of `{name}` "
    "actually installed in this project — not what you may already know "
    "about this library from training data. Prefer the information here "
    "over prior knowledge; if something here conflicts with what you'd "
    "otherwise assume, this file is authoritative."
)

_NO_SIDE_EFFECTS_LINE = "No known side effects detected."


def render_vendor_claude_md(digest: VendorDigest) -> str:
    """Sections, in order: Metadata, Grounding preamble, Public API
    surface, Gap analysis (conditional), Known gotchas, Quick links. The
    Metadata section's `**Installed version:**` line is load-bearing —
    `staleness.py` (Phase 6) regexes against this exact format.
    """
    config = digest.config
    parts = [
        f"# {config.name}",
        "",
        "## Metadata",
        "",
        f"- **Ecosystem:** {config.ecosystem.value}",
        f"- **Depth:** {config.depth.value}",
        f"- **Installed version:** {digest.installed_version}",
        "",
        "## Grounding",
        "",
        _GROUNDING_PREAMBLE.format(name=config.name),
        "",
        "## Public API surface",
        "",
        digest.api_surface or "_No API surface extracted._",
    ]
    gap_analysis_section = _render_gap_analysis_section(digest)
    if gap_analysis_section is not None:
        parts += ["", "## Gap analysis", "", gap_analysis_section]
    parts += [
        "",
        "## Known gotchas",
        "",
        _render_known_gotchas(digest),
        "",
        "## Quick links",
        "",
        "- [FILETREE.md](./FILETREE.md)",
        "- [DEPTREE.md](./DEPTREE.md)",
        "- [Project root CLAUDE.md](../../CLAUDE.md)",
    ]
    return "\n".join(parts)


def _render_gap_analysis_section(digest: VendorDigest) -> str | None:
    """`None` means "omit the section entirely" (`depth = surface`, or
    `full` without `context_path` — gap analysis never ran). A failed
    call still renders an explicit "unavailable" note rather than being
    indistinguishable from "never ran" — consistent with this project's
    never-silent-failure convention (explicit collapse/cap notices
    elsewhere).
    """
    if digest.gap_analysis_error:
        return f"_Gap analysis unavailable: `{digest.gap_analysis_error}`_"
    if not digest.gap_analysis:
        return None
    lines = [digest.gap_analysis]
    if digest.action_pointer_file:
        lines.append(
            f"\n**Action pointer:** `{digest.action_pointer_file}` — "
            f"{digest.action_pointer_note}"
        )
    return "\n".join(lines)


def _render_known_gotchas(digest: VendorDigest) -> str:
    if not digest.side_effects:
        return _NO_SIDE_EFFECTS_LINE
    return "\n".join(f"- {effect}" for effect in digest.side_effects)


def read_installed_version(claude_md_path: Path) -> str | None:
    """Read back the Metadata section's `**Installed version:**` line from
    an already-synced per-vendor `CLAUDE.md` — the format this module
    itself renders in `render_vendor_claude_md`. Returns `None` if the
    file doesn't exist or the line isn't found (never synced, or a
    hand-edited file missing the line). Shared by `index.py` (routing
    table) and `staleness.py` (Phase 6) rather than each keeping its own
    copy of this regex.
    """
    if not claude_md_path.exists():
        return None
    match = _INSTALLED_VERSION_RE.search(claude_md_path.read_text(encoding="utf-8"))
    return match.group(1) if match else None
