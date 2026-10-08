"""Per-vendor CLAUDE.md template rendering.

See architecture/overview.md's "Per-vendor CLAUDE.md structure" section.
Description (section 4 in that spec) is populated whenever a vendor has an
enrichment record — usage-driven, batched AI enrichment
(`codecompass.enrichment`, decisions/0031), read from the context graph by
`sync_vendor` (Phase 16, decisions/0035) for a from-scratch re-render;
omitted entirely (not a placeholder) for every other vendor.
`read_installed_version` reads the Metadata section's load-bearing line
back — this module owns the file format it targets, so `index.py` (Phase
4) and `staleness.py` (Phase 6) both call it rather than keeping their own
copies of the regex.

Phase 14 adds a second, narrower in-place-editing path:
`update_description_section`/`read_enrichment_hash` rewrite just the
Description section and a metadata hash line of an already-rendered
`CLAUDE.md`, for `codecompass.enrichment`'s batched, usage-driven
enrichment — called right after `graph.record_enrichment` writes the same
data these two functions edit into the file, so the two paths
(`sync_vendor`'s from-scratch re-render and this in-place edit) never
disagree about what a vendor's current enrichment content is; both
ultimately read from or write the same `vendor_enrichment` table.
"""

from __future__ import annotations

import re
from pathlib import Path

from codecompass.core import VendorDigest

_INSTALLED_VERSION_RE = re.compile(r"\*\*Installed version:\*\*\s*(\S+)")
_INSTALLED_VERSION_LINE_RE = re.compile(r"^(- \*\*Installed version:\*\*.*)$", re.MULTILINE)
_ENRICHMENT_HASH_RE = re.compile(r"\*\*Enrichment symbol-set hash:\*\*\s*(\S+)")
_ENRICHMENT_HASH_LINE_RE = re.compile(
    r"^- \*\*Enrichment symbol-set hash:\*\*.*$", re.MULTILINE
)
_DESCRIPTION_HEADING = "## Description"
_KNOWN_GOTCHAS_HEADING = "## Known gotchas"
_EXISTING_DESCRIPTION_SECTION_RE = re.compile(
    rf"^{re.escape(_DESCRIPTION_HEADING)}\n\n.*?\n\n(?=^{re.escape(_KNOWN_GOTCHAS_HEADING)}\n)",
    re.MULTILINE | re.DOTALL,
)
_KNOWN_GOTCHAS_LINE_RE = re.compile(rf"^{re.escape(_KNOWN_GOTCHAS_HEADING)}\n", re.MULTILINE)

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
    """`None` means "omit the section entirely" — no enrichment content
    exists for this vendor yet. Phase 16 (decisions/0035) drops the old
    depth-gate ahead of this check: `technical_description`'s own
    truthiness already means exactly "is there enrichment content to
    show," the same test this function already used as its second check,
    so a redundant first flag would just be another way to say the same
    thing.

    `description_error` (Phase 13) is a source-clone failure, not a
    description failure — since Phase 16 there's no description
    "attempt" inside `sync_vendor` to fail — and is deliberately not
    consulted here: surfacing a clone error in this section would show a
    misleading "Description unavailable" note for a vendor that either
    was never enriched at all, or has a perfectly good enrichment record
    from a previous run that this run's clone failure has no bearing on.
    A clone failure still belongs in Known Gotchas / standalone-mode
    context, just not this section.
    """
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


def _render_description_body(
    technical_description: str | None,
    action_pointer_file: str | None,
    action_pointer_note: str | None,
) -> str:
    """Same body shape `_render_description_section` produces for a
    successful grounded description — `technical_description` plus an
    optional Action pointer line — kept as a separate helper since this
    path never has a `description_error` to fall back to (see module
    docstring: this function is only ever called for a vendor that was
    just successfully enriched).
    """
    lines = [technical_description or "_Description unavailable._"]
    if action_pointer_file:
        lines.append(f"\n**Action pointer:** `{action_pointer_file}` — {action_pointer_note}")
    return "\n".join(lines)


def update_description_section(
    claude_md_path: Path,
    *,
    technical_description: str | None,
    action_pointer_file: str | None,
    action_pointer_note: str | None,
    symbol_set_hash: str,
) -> None:
    """Rewrite just `claude_md_path`'s "## Description" section — bounded
    by the fixed "## Public API surface" / "## Known gotchas" headings
    `render_vendor_claude_md`'s docstring guarantees the order of — and
    the Metadata section's `**Enrichment symbol-set hash:**` line, leaving
    every other part of the file untouched. Reuses `index.py`'s "regenerate
    just the bounded part" idiom for a heading-delimited region instead of
    a literal comment-marker pair, since a per-vendor `CLAUDE.md` has no
    marker comments of its own.

    Inserts a new "## Description" section (right before "## Known
    gotchas") if the file doesn't already have one — the common case the
    first time a formerly-undocumented vendor gets enriched, since
    `_render_description_section` omits the section outright for a vendor
    with no enrichment record yet. Replaces it in place if one already
    exists. Does nothing else to the file: no eligibility check here (see
    module docstring) — the caller decides who gets enriched.
    """
    content = claude_md_path.read_text(encoding="utf-8")
    body = _render_description_body(technical_description, action_pointer_file, action_pointer_note)
    new_section = f"{_DESCRIPTION_HEADING}\n\n{body}\n\n"

    if _EXISTING_DESCRIPTION_SECTION_RE.search(content):
        content = _EXISTING_DESCRIPTION_SECTION_RE.sub(new_section, content, count=1)
    else:
        content = _KNOWN_GOTCHAS_LINE_RE.sub(
            new_section + _KNOWN_GOTCHAS_HEADING + "\n", content, count=1
        )

    content = _set_enrichment_hash_line(content, symbol_set_hash)
    claude_md_path.write_text(content, encoding="utf-8")


def _set_enrichment_hash_line(content: str, symbol_set_hash: str) -> str:
    new_line = f"- **Enrichment symbol-set hash:** {symbol_set_hash}"
    if _ENRICHMENT_HASH_LINE_RE.search(content):
        return _ENRICHMENT_HASH_LINE_RE.sub(new_line, content, count=1)
    # First enrichment for this vendor — insert right after the Metadata
    # section's `**Installed version:**` line, alongside it.
    return _INSTALLED_VERSION_LINE_RE.sub(
        lambda m: f"{m.group(1)}\n{new_line}", content, count=1
    )


def read_enrichment_hash(claude_md_path: Path) -> str | None:
    """Read back the Metadata section's `**Enrichment symbol-set hash:**`
    line, mirroring `read_installed_version`'s exact pattern — the
    file-level half of `codecompass.enrichment`'s two-tier cache-key check
    (decisions/0032): the one that still works against a fresh clone with
    no `context-graph.db` at all, since this line lives in the committed
    `CLAUDE.md`, not the gitignored database.
    """
    if not claude_md_path.exists():
        return None
    match = _ENRICHMENT_HASH_RE.search(claude_md_path.read_text(encoding="utf-8"))
    return match.group(1) if match else None
