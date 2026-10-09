"""Deterministic heading-based markdown chunking (Phase 32) — splits a
doc artifact's text into heading-scoped slices, additively sharpening
Phase 30's `doc_code_trace` (an optional `heading` field) and Phase 31's
enrichment excerpts (the matched chunk's own text in place of Phase 28's
needle-re-derivation) once a mechanical mention can be attributed to
exactly one chunk. No NLP, no embeddings, no model call — the same
mechanical, structure-based posture as every other detection mechanism in
this project. See planning/phase-32-doc-chunking.md.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

# Any markdown heading level (`#` through `######`) is a chunk boundary —
# "headings are the unit" (the phase plan's Explicitly does not cover
# section names *sub-heading* chunking as the thing excluded, not deeper
# heading levels), so `heading_path` reflects the full nesting chain
# (e.g. "Scope > Covers"), not just top-level sections.
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


@dataclass(frozen=True)
class DocChunk:
    """One heading-scoped slice of a markdown doc's text. `start_line`/
    `end_line` are 1-indexed and inclusive, matching this project's
    existing `uses_edges.line` convention. `heading_path` is the
    " > "-joined chain of enclosing heading titles, root-first
    (`"Scope > Covers"`, not `"Covers > Scope"`) — empty string only for
    a leading chunk of content that precedes a doc's first heading.
    """

    heading_path: str
    start_line: int
    end_line: int
    content_hash: str


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def chunk_markdown(text: str) -> list[DocChunk]:
    """Splits `text` into heading-scoped chunks. Returns `[]` for a doc
    with no headings at all — deliberately not one chunk covering the
    whole file, so a headerless doc naturally produces zero `doc_chunks`
    rows and every mention-detection match against it stays
    `chunk_id = NULL`, exactly the "doc has no headings at all" case the
    phase plan names as one of the two reasons a match can't be
    attributed to a chunk (the other being a match spanning multiple
    chunks — handled by the caller, not here: this function only
    produces the chunk boundaries, `doc_mapping.py` decides attribution).
    """
    lines = text.splitlines()
    headings: list[tuple[int, int, str]] = []
    in_fence = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Phase 34: a fenced code block (```/~~~) can contain a `#`-prefixed
        # comment (shell/Python example code) that would otherwise match
        # the heading regex — track fence state so lines inside one are
        # never treated as headings, matching real markdown semantics.
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = _HEADING_RE.match(line)
        if m:
            headings.append((i, len(m.group(1)), m.group(2)))
    if not headings:
        return []

    chunks: list[DocChunk] = []

    first_heading_line = headings[0][0]
    if first_heading_line > 0:
        leading_text = "\n".join(lines[0:first_heading_line])
        chunks.append(
            DocChunk(
                heading_path="",
                start_line=1,
                end_line=first_heading_line,
                content_hash=_hash(leading_text),
            )
        )

    stack: list[tuple[int, str]] = []
    for index, (line_index, level, title) in enumerate(headings):
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        heading_path = " > ".join(t for _, t in stack)

        start_line = line_index + 1
        end_line = headings[index + 1][0] if index + 1 < len(headings) else len(lines)
        chunk_text = "\n".join(lines[line_index:end_line])
        chunks.append(
            DocChunk(
                heading_path=heading_path,
                start_line=start_line,
                end_line=end_line,
                content_hash=_hash(chunk_text),
            )
        )

    return chunks
