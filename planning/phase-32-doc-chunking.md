# Phase 32: Heading-based doc chunking (additive precision upgrade)

## Status

`done` — depended on Phase 30 and Phase 31, both `done` first.

## Context

Every `doc_artifacts` row today is whole-file: a mention edge
(`documents_edges`, `doc_relations_edges`) says a doc relates to a
vendor/symbol/artifact somewhere in the file, with no location finer than
"this 91,000-character document." Phase 28 already worked around the
sharpest edge of this — re-deriving the mechanical match's character
offset at enrichment time and centering a window on it, rather than
always slicing the first 4,000 characters — but that's a runtime patch
over an imprecise unit, not a fix to the unit itself.

This phase makes the unit itself finer: split each markdown
`doc_artifacts` row into heading-scoped chunks (deterministic, on `#`/`##`
boundaries — no NLP, no embeddings, same mechanical posture as every
other detection phase in this project) and let mention-detection and
enrichment operate at chunk granularity where it's populated, falling
back to whole-doc behavior everywhere it isn't.

This is the same additive-upgrade shape as two direct precedents:
Phase 26 added symbol-level usage detection on top of Phase 11's
vendor-level detection without rewriting it; Phase 28 added
needle-centered excerpts on top of Phase 22's enrichment without
rewriting its selection logic. This phase does the analogous thing to
both Phase 30 and Phase 31 at once.

## Scope

**Covers:**
- `doc_chunking.py` (new): deterministic heading-based split of a
  markdown doc's text into `(heading_path, start_line, end_line,
  content_hash)` chunks. No AI, no semantic boundary detection.
- `doc_chunks` table (new): `id`, `doc_artifact_id` (FK), `heading_path`,
  `start_line`, `end_line`, `content_hash`.
- `documents_edges` and `doc_relations_edges` each gain a **nullable**
  `chunk_id` column. Existing rows keep `chunk_id = NULL` and continue to
  resolve at whole-doc granularity exactly as before — this is additive,
  not a migration.
- `doc_mapping.py`'s mention-detection (`build_documents_edges`,
  `build_doc_relations_edges`) gains an additional per-chunk pass: the
  same existing word-boundary regex (`re.search(rf"\b{re.escape(name)}\b",
  text)`), run against each chunk's own text slice instead of the whole
  file, populating `chunk_id` on the resulting edge when a single chunk
  contains the match. If a match can't be attributed to one chunk (e.g. it
  spans a boundary, or the doc has no headings at all), `chunk_id` stays
  `NULL` and the edge behaves exactly as it does today — no regression,
  no forced choice.
- `relation_enrichment.py`: when `chunk_id` is populated, use that
  chunk's own text as the excerpt directly, in place of Phase 28's
  needle-re-derivation. Phase 28's logic remains as the fallback for any
  edge without a `chunk_id` — not deleted, not made unreachable.
- Phase 30's `doc_code_trace` output gains an optional `heading` field
  when the underlying edge has a `chunk_id`.
- `query relations` output shows the heading alongside the existing path,
  when available.

**Explicitly does not cover:**
- Sub-heading (paragraph-level) chunking — headings are the unit; a
  future phase could go finer if a real case shows heading-level isn't
  enough, but that's not assumed here.
- Any change to the detection boundary — chunking makes existing
  mechanical matches more precisely located, it does not let AI propose
  new relations. Same explicit non-goal as Phases 30 and 31.
- Chunking of non-markdown doc artifacts (none currently exist in this
  project's `doc_artifacts` kinds, all are `.md`).
- Retroactive backfill of `chunk_id` on rows written before this phase —
  see Design decisions.

## Design decisions

- **Heading boundaries only, not semantic boundaries.** Consistent with
  every other detection mechanism in this codebase — deterministic,
  regex/structure-based, no model call in the loop for detection itself.
  Clarified during implementation: "on `#`/`##` boundaries" means any
  heading level (`#` through `######`) is a chunk boundary, with
  `heading_path` reflecting the full root-first nesting chain — the
  phase's own Explicitly-does-not-cover section names *sub-heading*
  (paragraph-level) chunking as the thing excluded, not deeper heading
  levels, and the plan's own "nested heading levels" test scenario
  confirms this reading.
- **`chunk_id` is nullable and additive everywhere it's added**, not a
  required field — mirrors the two-nullable-target shape already used by
  `SkillMentionEdgeRow`/`DocRelationEdgeRow` for a different reason, same
  underlying principle: don't force a value where none cleanly applies.
- **No backfill.** Existing edges get `chunk_id` the next time mention-
  detection naturally reruns (a graph rebuild via `sync`), same "let the
  natural refresh cycle handle it" posture Phase 31 already takes for its
  own rollout — no separate migration script.
- **`content_hash` per chunk**, not just per doc-artifact, so a change
  confined to one section of a long doc doesn't invalidate enrichment
  cached against unrelated chunks — a real precision win over the current
  whole-file staleness granularity, worth calling out explicitly since it
  touches the two-axis staleness model (`decisions/0005`-adjacent):
  DOCUMENTS/EXPLAINS-edge invalidation can now happen at chunk grain
  instead of whole-doc grain. If this interacts with the staleness model
  in a way that isn't obvious during implementation, write the ADR before
  proceeding rather than assuming.
- **A headerless doc produces zero chunks, not one whole-file chunk.**
  Found during implementation to be the cleanest way to satisfy "the doc
  has no headings at all" as a `chunk_id = NULL` case: `chunk_markdown`
  simply returns `[]`, so no downstream code needs to special-case "is
  this the fallback whole-doc chunk" before deciding attribution.
- **`documents_edges`/`doc_relations_edges` migrate via the same
  drop-and-recreate approach `doc_artifacts` already uses**, not
  `ALTER TABLE ADD COLUMN` — both tables are fully cleared and reinserted
  by `rebuild_deterministic` on every whole-project sync regardless, so
  there's no data-loss risk, unlike `doc_relation_enrichment` (Phase 31),
  which holds paid AI spend and genuinely needs the additive migration.
  See `decisions/0046`.

## Files

- `src/codecompass/doc_chunking.py` (new) — heading-based splitter,
  per-chunk content hash.
- `src/codecompass/graph.py` (changed) — `doc_chunks` table;
  `chunk_id` on `documents_edges`/`doc_relations_edges`; schema version
  bump.
- `src/codecompass/doc_mapping.py` (changed) — additive per-chunk mention
  pass alongside the existing whole-file pass.
- `src/codecompass/relation_enrichment.py` (changed) — prefer chunk text
  as excerpt when `chunk_id` is set; Phase 28's needle-centering remains
  as fallback.
- `src/codecompass/cli.py` (changed) — `query relations` and Phase 30's
  trace output show `heading` when available.
- `decisions/0046-doc-chunking-heading-based-additive.md` (new) —
  records the heading-only choice, the nullable/additive `chunk_id`
  design, and explicitly reaffirms the no-new-detection boundary.
- `tests/test_doc_chunking.py` (new) — splitter correctness against
  hand-written fixture markdown, including edge cases (no headings, a
  match spanning a boundary, nested heading levels).
- `tests/test_doc_mapping.py` (changed) — `chunk_id` populated on the
  single-chunk-match case, left `NULL` on the boundary-spanning case.
- `tests/test_relation_enrichment.py` (changed) — chunk-text excerpt path
  and the fallback-to-Phase-28 path, both exercised.
- `docs/cli-reference.md` / `architecture/overview.md` — document the new
  field and the fallback behavior.
- `CHANGELOG.md` — `[Unreleased]` entry, `Added` category.

## Verification

- `pytest` passes, new tests included.
- `ruff check .` clean.
- Live dogfood against this repo's own real docs: run chunking against
  `architecture/overview.md`'s actual headings, confirm the split matches
  the file's real structure by eye.
- Pick a real, already-enriched relation in this repo (e.g. one from
  Phase 22/28's own validation) and confirm its excerpt now comes from
  the matched chunk's exact text, and that the chunk's content genuinely
  is the passage that triggered the match — same standard Phase 28 used,
  read the real surrounding text directly, not just green tests.
- Confirm a pre-existing (pre-Phase-32) `doc_relations_edges` row with
  `chunk_id = NULL` still enriches correctly via the Phase 28 fallback —
  explicit regression check, not assumed from the code reading correct.
- Confirm Phase 29's self-mention exclusion (`vendor_doc` source row
  mentioning its own vendor name) still holds under the new per-chunk
  pass — that exclusion is enforced at match time inside
  `build_doc_relations_edges`, not inherited automatically, so this needs
  an explicit test against a real vendor doc that mentions its own name
  multiple times. Confirmed with both a new unit test
  (`test_build_doc_relations_edges_self_mention_exclusion_holds_under_
  per_chunk_pass`) and live against this repo's real data — not
  `vendor/anthropic/src/README.md` as originally named here (that file
  turned out, on inspection, to mention no *other* tracked vendor at all,
  so it produces zero outgoing edges regardless and isn't a meaningful
  live check), but `vendor/anthropic/src/CHANGELOG.md`, the real fixture
  that actually sources vendor-mention edges: it says "anthropic" 1,161
  times (word-boundary matches) yet produces exactly one outgoing edge,
  targeting `rich`, zero self-referencing.
- Core-logic diff read directly against this plan before marking `done`.
  Live-verified beyond the above: chunking `architecture/overview.md`'s
  real ~1,600 lines produced a correctly-nested heading structure by eye;
  a real already-enriched relation
  (`decisions/0016-gap-analysis-tests-never-call-the-live-anthropic-
  api.md` → `anthropic`) now has its AI-enrichment excerpt sliced exactly
  from its matched chunk's real text (`_select_source_excerpt_from_chunk`
  called directly against the real file, output inspected byte-for-byte);
  a pre-existing relation with `chunk_id = NULL`
  (`architecture/overview.md` → `anthropic`, ambiguous — the name appears
  across many sections) still carries a valid, grounded `ai_summary` via
  the unchanged Phase 28 fallback path.
