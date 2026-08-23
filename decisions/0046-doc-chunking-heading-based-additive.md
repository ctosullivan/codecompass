# 0046: Heading-based doc chunking, additive and nullable throughout

## Status

Accepted.

## Context

Every `doc_artifacts` row is whole-file: `documents_edges` and
`doc_relations_edges` say a doc relates to a symbol/vendor/artifact
*somewhere* in the file, with no location finer than the whole document.
Phase 28 (`decisions/0042`) already worked around the sharpest edge of
this for AI enrichment specifically — re-deriving the mechanical match's
character offset at enrichment time and centering a window on it, rather
than always slicing the first 4,000 characters — but that's a runtime
patch over an imprecise unit, not a fix to the unit itself. Phase 30's
`doc_code_trace` has the same ceiling: it can say a doc mentions a vendor,
but not *where in the doc*.

## Decision

Split each chunkable doc artifact's markdown text into heading-scoped
chunks — deterministic, on any heading level (`#` through `######`), no
NLP, no embeddings, the same mechanical, structure-based posture as every
other detection mechanism in this project. "Headings are the unit" per
the phase plan; a doc's `heading_path` is the full root-first nesting
chain (`"Scope > Covers"`, not just the nearest heading), since a
sub-heading's context is part of what makes a location precise. A doc
with no headings at all produces **zero** chunks, not one chunk covering
the whole file — this is what makes `chunk_id` naturally stay `NULL` for
a headerless doc without any special-casing in the mention-detection code
that assigns it.

Only doc kinds that can ever be a `documents_edges`/`doc_relations_edges`
source or target (`claude_md`, `overview`, `vendor_doc`, `spec_doc`) are
chunked at all — chunking a Skill/`.mdc` rule/slash-command doc would
produce `doc_chunks` rows nothing could ever reference, since neither
builder function scans those kinds.

**`chunk_id` is nullable everywhere it's added, and additive, not a
migration.** A mechanical match is attributed to a chunk only when
exactly one chunk's own text contains a word-boundary match for the same
needle the whole-doc pass already used; zero or more than one chunk
matching leaves `chunk_id = NULL` and the edge behaves exactly as it did
before this phase. The whole-doc edge itself is always produced
identically regardless — chunking sharpens *location*, it never changes
*whether* a relationship exists.

**Two tables get genuinely new columns on an existing database, migrated
two different ways** — deliberately, not by oversight:
- `documents_edges`/`doc_relations_edges` gain `chunk_id` via the same
  drop-and-recreate approach `doc_artifacts`'s own migration already
  uses (`_migrate_doc_artifacts_constraints`, widened rather than
  duplicated) — both tables are fully cleared and reinserted by
  `rebuild_deterministic` on every whole-project sync regardless, so
  there's no data to lose.
- `doc_relation_enrichment` is untouched by this phase (it already has no
  `chunk_id` column and doesn't need one — the excerpt-selection code
  reads chunk boundaries from `doc_relations_edges`/`doc_chunks` at
  enrichment *time*, not from a column stored on the enrichment row
  itself). The general lesson this phase reinforces, set by Phase 31's
  `relation_label` migration: a table holding paid AI spend gets an
  `ALTER TABLE ADD COLUMN` migration if it ever needs one; a table fully
  rewritten every sync gets drop-and-recreate. The right migration
  strategy depends on what the table holds, not on applying one pattern
  uniformly everywhere.

**Enrichment excerpts prefer chunk text over Phase 28's fixed-window
guess, without removing it.** When an edge selected for enrichment has a
`chunk_id`, `relation_enrichment.select_candidates` uses that chunk's own
text as the excerpt directly — no character cap, since a heading-scoped
section is already a tighter unit than the 4,000-character window in the
common case. Phase 28's needle-re-derivation-plus-fixed-window logic
remains, verbatim, as the fallback for any edge without a `chunk_id`
(headerless doc, or an ambiguous multi-chunk match) — not deleted, not
made unreachable.

## Consequences

- New `doc_chunks` table (`id`, `doc_artifact_id`, `heading_path`,
  `start_line`, `end_line`, `content_hash`) — content hashed per chunk,
  not just per doc-artifact, so a change confined to one section of a
  long doc doesn't invalidate an unrelated section's cached chunk
  identity (not currently consumed for enrichment cache invalidation —
  `select_candidates` still hashes the source doc's *full* text against
  the target's text, unchanged from Phase 22 — but the per-chunk hash is
  there, computed correctly, for a future phase to use if chunk-grain
  cache invalidation is ever pursued).
- Phase 30's `doc_code_trace` and `query relations`/`query vendor`'s
  underlying `graph.doc_relations` gain an optional `heading` field,
  `None` unless the edge has a `chunk_id`.
- No retroactive backfill of `chunk_id` on rows written before this
  phase — the next whole-project `sync` naturally rebuilds
  `documents_edges`/`doc_relations_edges` (and, for the first time,
  `doc_chunks`) from scratch, the same "let the natural refresh cycle
  handle it" posture Phase 31 already took for `relation_label`.

## Alternatives considered

- **One chunk covering the whole file for a headerless doc**, instead of
  zero chunks. Rejected — would require every call site that decides
  chunk attribution to also check "is this the fallback whole-doc chunk"
  before treating a match as attributable, duplicating logic that "zero
  chunks" already gives for free by construction.
- **Paragraph-level (sub-heading) chunking.** Rejected for this phase,
  per the plan's Explicitly does not cover section — headings are a
  natural, already-authored structural unit; going finer is unproven
  value until a real case shows heading-level isn't enough.
- **Storing chunk text in the table**, rather than re-slicing the doc's
  own file by `(start_line, end_line)` at read time. Rejected — every
  other precedent in this project (excerpts, `used_at` locations) derives
  transient data from the source of truth (the file on disk / the graph)
  rather than duplicating it into a second stored copy that could drift.
