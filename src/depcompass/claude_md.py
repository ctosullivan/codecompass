"""Per-vendor CLAUDE.md template rendering.

See architecture/overview.md's "Per-vendor CLAUDE.md structure" section.
Gap analysis (section 4 in that spec) is omitted entirely until Phase 5
produces real output to render — not stubbed with placeholder text, per
planning/phase-4-sync-index-init.md's Design decisions.
"""

from __future__ import annotations

from depcompass.core import VendorDigest

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
    surface, Known gotchas, Quick links. The Metadata section's
    `**Installed version:**` line is load-bearing — `staleness.py`
    (Phase 6) regexes against this exact format.
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


def _render_known_gotchas(digest: VendorDigest) -> str:
    if not digest.side_effects:
        return _NO_SIDE_EFFECTS_LINE
    return "\n".join(f"- {effect}" for effect in digest.side_effects)
