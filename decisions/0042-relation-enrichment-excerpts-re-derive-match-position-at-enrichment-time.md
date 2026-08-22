# 0042. Relationship-enrichment excerpts re-derive the match position at enrichment time, don't persist it from Phase 21

## Status

Accepted

## Context

Phase 28 (`planning/phase-28-center-relationship-excerpts-on-the-actual-match.md`)
was found via a live `/discovery` session testing Phase 26/27's real output
quality, not guessed at. `relation_enrichment.select_candidates` sent the
model `source_text[:_SPEC_DOC_EXCERPT_CHAR_CAP]` — the spec doc's first
4,000 characters — as the grounding excerpt for every relationship,
regardless of where in the file the mechanical mention that produced the
candidate (`doc_mapping.build_doc_relations_edges`'s word-boundary match)
actually sits.

Confirmed with real data from this repo's own two currently-enriched
vendor-doc relationships (`architecture/overview.md`/`docs/
cli-reference.md` → `vendor/anthropic/src/README.md`, both mechanically
matched via the literal phrase `"anthropic README.md"`): the match sits at
character 7,870 in `docs/cli-reference.md` (18,912 chars total) and
character 91,374 in `architecture/overview.md` (108,307 chars total) —
both well past the 4,000-character excerpt actually sent to the model.
Reading both resulting `ai_summary` values confirmed the consequence
directly: both are plausible-sounding but describe the *wrong part* of
each document (one talks about `init --scan`, the other about "Core data
model") — the model filled in a reasonable story from whatever *was* in
its window, not from the sentence that actually triggered the match. This
isn't a one-off hallucination; it's structural: any spec doc where the
real mention falls past the fixed prefix window gets an ungrounded
summary, and this repo's own two current examples both did.

Fixing this requires knowing, at enrichment time, roughly where in
`source_text` the mention is. One design question needed settling: does
that position get computed once, during Phase 21's mechanical detection,
and persisted for enrichment to read later — or does enrichment
independently re-derive it?

## Decision

**Re-derive the match position at enrichment time, in
`relation_enrichment.select_candidates`, via the exact same regex shape
`doc_mapping.build_doc_relations_edges` used to detect the relationship in
the first place** (`re.search(rf"\b{re.escape(needle)}\b", source_text)`)
— rather than having `build_doc_relations_edges` record the match's
character offset directly on the `doc_relations_edges` row and having
enrichment simply read it back.

`doc_relations_edges` is a purely mechanical, fully-rebuilt-every-sync
table (Phase 21, `decisions/0037`): "this spec doc mechanically mentions
this vendor/doc artifact" is all it means, with no concept of "this
candidate hasn't been enriched yet, so remember exactly where its excerpt
should center." That's an enrichment-time concern — it only matters to
`relation_enrichment.select_candidates`, and only for a candidate that
isn't already cache-hit by content hash. Threading a match-offset column
back through the mechanical table would blur what that table means (a real
relationship exists, full stop) with a detail nothing except enrichment
cares about, and would leave a column that's stale the moment the source
file changes between a graph rebuild and the next enrichment run anyway —
`doc_relations_edges` doesn't re-run on every enrichment call, only on a
whole-project sync (`decisions/0025`), so a persisted offset could easily
point at the wrong place in a file that's been edited since.

Re-running the same `re.search` at enrichment time is cheap: one regex
search over a source doc that's already being read into memory in full for
`_compute_content_hash` and the excerpt slice itself, no extra I/O. The
needle to search for comes from `graph.relation_enrichment_candidates`'s
new `target_doc_artifact_name` column (this phase's other change) —
`target_vendor_name` for `relation_kind='mentions_dependency'`, `target_
doc_artifact_name` for `'mentions_artifact'` — mirroring exactly what
`build_doc_relations_edges` itself matched against.

**Excerpt window: 1,000 characters before the match, 3,000 after, same
total `_SPEC_DOC_EXCERPT_CHAR_CAP` (4,000) budget as before.** The
asymmetric split is a deliberate starting guess, not measured: a mention
is more often followed by explanatory text (what it does, why it's used)
than preceded by it, so more of the fixed budget goes after the match.
Implemented as two named constants (`_EXCERPT_CHARS_BEFORE_MATCH`,
`_EXCERPT_CHARS_AFTER_MATCH`) specifically so the split is easy to retune
once real output quality from a second live validation run is in hand —
the same "start simple, tune from real usage" posture this project already
took for `enrichment.py`'s batch-size constants and for `_SPEC_DOC_
EXCERPT_CHAR_CAP` itself. This phase relocates the window; it does not
resize it — `_SPEC_DOC_EXCERPT_CHAR_CAP`'s value and `plan_batches`'
budget accounting are both unchanged.

**A needle that can't be re-found falls back to the original
first-N-characters slice, non-fatal.** Expected to be rare — Phase 21's
last rebuild already proved the mention exists in the file at that point —
but the file can still change between that rebuild and this call (an edit
mid-session), and degrading gracefully to the old behavior is strictly
better than raising and dropping the whole candidate.

## Alternatives considered

- **Persist the match offset on `doc_relations_edges` at detection time.**
  Rejected for the reasons above: it's an enrichment-only concern that
  doesn't belong on a purely mechanical, fully-rebuilt table, and a
  persisted offset would go stale between a graph rebuild and a later
  enrichment call in exactly the case this phase cares about (a file
  edited in between) — re-deriving is not just cleaner, it's also more
  correct in that window.
- **A symmetric before/after split** (2,000/2,000). Considered simplest,
  but rejected in favor of the asymmetric 1,000/3,000 split — a mention is
  typically the *subject* introduced followed by explanation, not the
  conclusion of a preceding block, so weighting the budget toward what
  comes after seemed like the better first guess. Neither split has real
  evidence behind it yet; this is a named-constant starting point, not a
  locked-in conclusion (see Decision above).
- **Handle multiple mechanical matches specially** (e.g. picking the "best"
  one, or unioning several windows). Rejected/deferred: `build_doc_
  relations_edges` itself already implicitly takes only the first match
  via `re.search` (not `re.finditer`) when *detecting* the relationship —
  `select_candidates` matching that same first-match behavior when
  *re-finding* it keeps the two functions consistent. A relationship
  genuinely discussed in multiple, disconnected parts of one spec doc is a
  real but separate problem, out of scope here.

## Consequences

- `select_candidates` now depends on `graph.relation_enrichment_
  candidates` returning `target_doc_artifact_name`, a new column this
  phase adds — any future caller of that function must account for the
  extra dict key.
- A future change to `doc_mapping.build_doc_relations_edges`'s matching
  logic (e.g. a different needle, a different regex shape) must be mirrored
  in `relation_enrichment._relation_needle`/`_select_source_excerpt` or the
  two will silently drift apart — re-derivation trades a small amount of
  duplicated logic for not coupling the two tables' schemas together.
- The 1,000/3,000 split is a guess pending a second live validation run
  (the phase plan's own verification step); revisiting it does not require
  another ADR, only tuning the two named constants.
