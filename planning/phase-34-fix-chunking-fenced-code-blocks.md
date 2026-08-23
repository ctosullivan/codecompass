# Phase 34: Fix `doc_chunking`'s heading detection inside fenced code blocks

## Status

`done`

## Context

Found during the `/discovery` session testing Phase 30-33's real output
quality: `doc_chunking.chunk_markdown`'s heading regex
(`^(#{1,6})\s+(.*\S)\s*$`) matches any line starting with `#` and a space,
with no awareness of markdown fenced code blocks (` ``` `). A `#`-prefixed
comment *inside* a code fence — e.g. a shell/Python comment in an example
— gets misdetected as a real markdown heading, both creating a bogus
chunk boundary and corrupting the `heading_path` of whatever real heading
follows it.

Confirmed live and reproducible, not hypothetical:
- `docs/cli-reference.md` has a fenced example block containing `#  Not a
  shell command — typed inside a Claude Code session:` (a comment, not a
  heading). This produced a bogus chunk, and the *real* next heading
  (`## codecompass undo [--yes] [--dry-run]`) got nested under it,
  reporting `heading: "Not a shell command — typed inside a Claude Code
  session: > `codecompass undo [--yes] [--dry-run]`"` for the `typer`
  relation sourced from that doc — not a real section title.
- Scanning all 84 currently-chunkable doc artifacts
  (`claude_md`/`overview`/`vendor_doc`/`spec_doc`) found **37** such
  false-positive `#`-inside-fence lines, concentrated in
  `vendor/anthropic/src/MIGRATION.md` (`# Before`/`# After` code
  comments — a common style in migration guides) and `CONTRIBUTING.md`.
  This already has real, materialized impact: 12 real `documents_edges`
  rows on `MIGRATION.md` alone currently carry bogus headings, e.g.
  `"After > Bedrock: a region is now required"` (a fake "After" parent
  prepended to a real heading) or entirely-fabricated chains like `"the
  very first lines of your entry point > Response and error objects"`.

## Scope

**Covers:**
- `doc_chunking.chunk_markdown` tracks fenced-code-block state (a line
  whose stripped content starts with ` ``` ` or `~~~` toggles it) and
  never treats a line matched by the heading regex as a real heading
  while inside a fence.
- Regression tests: a `#`-prefixed comment inside a fenced block must not
  produce a chunk boundary or appear in any `heading_path`; a real
  heading immediately after a closed fence must still be detected
  correctly (the fence-tracking must turn back off).

**Explicitly does not cover:**
- Indented (4-space) code blocks — a heading regex already requires the
  `#` at column 0, so an indented `#`-line inside an indented code block
  can never match `_HEADING_RE` in the first place; nothing to fix there.
- Any change to what counts as a heading level, or to `heading_path`'s
  nesting/join logic — untouched, still correct once fenced lines are
  correctly excluded from the heading candidate list.
- Retroactive correction of currently-stored bogus `heading_path` values
  in `doc_chunks` — the next whole-project `sync` naturally rebuilds
  `doc_chunks` from scratch (same "let the natural refresh cycle handle
  it" posture this project has used for every additive/corrective schema
  change so far), no backfill script needed.

## Design decisions

- **Track fence state with a simple toggle, not a full markdown
  parser.** Consistent with this project's established "deterministic,
  regex/structure-based, no over-engineering" posture for every other
  mechanical detection pass. A fence line is any stripped line starting
  with three-or-more backticks or tildes; this project's real fixtures
  only use backtick fences, but tilde fences cost nothing extra to
  handle correctly.
- **No backfill for already-stored bogus headings.** Same posture Phase
  31/32 already established for their own migrations — a whole-project
  `sync` naturally recomputes `doc_chunks` (and everything derived from
  it) from scratch every time, so there's no persisted state that needs
  a special correction path.

## Files

- `src/codecompass/doc_chunking.py` — fence-aware heading detection in
  `chunk_markdown`.
- `tests/test_doc_chunking.py` — new regression tests for the fenced-
  code-block case (a `#`-comment inside a fence, and a real heading
  correctly detected right after the fence closes).
- `CHANGELOG.md` — `[Unreleased]` entry, `Fixed` category.

## Verification

- `pytest` passes, including the new regression tests (confirmed to fail
  against the pre-fix code, matching this project's standing pattern for
  bug-fix phases).
- `ruff check .` clean.
- Live dogfood: re-run chunking against `docs/cli-reference.md` and
  `vendor/anthropic/src/MIGRATION.md` and confirm none of the 37
  previously-found false-positive lines still produce a heading/chunk
  boundary; re-sync this repo and confirm `query relations
  docs/cli-reference.md`'s `typer` entry now reports the real heading
  (`codecompass undo [--yes] [--dry-run]`), not the bogus one.
- Core-logic diff read directly against this plan before marking `done`.

**Confirmed live** (this phase's actual implementation): re-synced this
repo after the fix. `docs/cli-reference.md`'s `typer` relation now
reports `"CLI reference > `codecompass undo [--yes] [--dry-run]`"` — the
real heading, not the previous `"Not a shell command..."` fabrication.
`vendor/anthropic/src/MIGRATION.md`'s `documents_edges` rows that
previously carried bogus headings now correctly report real chains, e.g.
`"Migrating to v1 > Bedrock: a region is now required"` (the fake
`"After"` prefix is gone, replaced by the real parent heading) and
`"Migrating to v1 > The SDK is built on \`httpx2\` > Response and error
objects"` (previously an entirely fabricated chain).
