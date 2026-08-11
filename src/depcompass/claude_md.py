"""Per-vendor CLAUDE.md template rendering.

See architecture/overview.md's "Per-vendor CLAUDE.md structure" section.
Description (section 4 in that spec) is populated by Phase 7's AI-gated
grounded-description step for every `depth = full` vendor (replaced
Phase 5's `context_path`-gated gap analysis — decisions/0019); omitted
entirely (not a placeholder) for every other vendor. `read_installed_version`
reads the Metadata section's load-bearing line back — this module owns
the file format it targets, so `index.py` (Phase 4) and `staleness.py`
(Phase 6) both call it rather than keeping their own copies of the regex.
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
    description_section = _render_description_section(digest)
    if description_section is not None:
        parts += ["", "## Description", "", description_section]
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


def _render_description_section(digest: VendorDigest) -> str | None:
    """`None` means "omit the section entirely" (`depth = surface` —
    grounded description never runs for it). A failed call still renders
    an explicit "unavailable" note rather than being indistinguishable
    from "never ran" — consistent with this project's never-silent-
    failure convention (explicit collapse/cap notices elsewhere).
    """
    if digest.description_error:
        return f"_Description unavailable: `{digest.description_error}`_"
    if not digest.technical_description:
        return None
    lines = [digest.technical_description]
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
