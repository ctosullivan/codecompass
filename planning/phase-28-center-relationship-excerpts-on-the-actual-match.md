# Phase 28: Center relationship excerpts on the actual match

## Scope

Found via a live `/discovery` session testing Phase 26/27's real output
quality, not guessed at. `relation_enrichment.select_candidates` sends
the model `source_text[:_SPEC_DOC_EXCERPT_CHAR_CAP]` (the first 4,000
characters of the spec doc) as the grounding excerpt for every
relationship — regardless of *where in the file* the mechanical mention
that produced this candidate (`doc_mapping.build_doc_relations_edges`'s
word-boundary match) actually is.

Confirmed with real data from this repo's own two currently-enriched
vendor-doc relationships (`architecture/overview.md`/`docs/
cli-reference.md` → `vendor/anthropic/src/README.md`, both mechanically
matched via the literal phrase `"anthropic README.md"`): the match sits
at character 7,870 in `docs/cli-reference.md` (18,912 chars total) and
character 91,374 in `architecture/overview.md` (108,307 chars total) —
both **well past** the 4,000-character excerpt actually sent to the
model. Reading both resulting `ai_summary` values confirms the
consequence directly: both are plausible-sounding but describe the
*wrong part* of each document (one talks about `init --scan`, the other
about "Core data model") — the model filled in a reasonable story from
whatever *was* in its window, not from the sentence that actually
triggered the match. This isn't a one-off hallucination; it's
structural — any spec doc where the real mention falls past the fixed
prefix window will get an ungrounded summary, and this repo's own two
current examples both do.

**Covered:**
- `graph.relation_enrichment_candidates`: add `tda.name` to the
  `SELECT`/returned dict (`target_doc_artifact_name`) — currently only
  `tda.path` is returned, but `doc_mapping.build_doc_relations_edges`'s
  actual mechanical match for a `mentions_artifact` row was against the
  target's `name` field (e.g. `"anthropic README.md"`), not its path
  (`"vendor/anthropic/src/README.md"`) — `select_candidates` needs the
  same needle to re-find the same match.
- `relation_enrichment.select_candidates`: compute the "needle" exactly
  the way `build_doc_relations_edges` did — `target_vendor_name` for
  `relation_kind='mentions_dependency'`, the target's `name` field for
  `'mentions_artifact'` — `re.search(rf"\b{re.escape(needle)}\b",
  source_text)` to find its position, then extract a window *centered* on
  that match (some characters of context before, more after — the
  sentence/paragraph containing the mention plus its surrounding
  discussion) instead of always the file's opening. Total window size
  stays at the same `_SPEC_DOC_EXCERPT_CHAR_CAP` budget — this is a
  relocation of the window, not an increase in per-call cost.
- A needle that can't be re-found (the file changed between the graph
  rebuild that detected it and this call, or between the migration and
  now) falls back to the existing first-N-characters behavior — this
  should be rare (Phase 21 just proved the mention exists as of the last
  rebuild) but must degrade gracefully, not raise.
- Tests proving the fix against the *exact* scenario found: a source text
  where the needle sits past the current fixed cap, asserting the
  produced excerpt actually contains the needle's surrounding context
  (not just the file's first N characters).

**Explicitly deferred / out of scope:**
- Any change to `_SPEC_DOC_EXCERPT_CHAR_CAP`'s actual size, or to
  `plan_batches`' batch-budget accounting — this phase relocates the
  window, it doesn't resize it.
- Handling a relationship with *multiple* mechanical matches at different
  positions in the same source doc differently (e.g. picking the
  "best" one) — take the first match, same as `doc_mapping.
  build_doc_relations_edges` itself already implicitly does via
  `re.search` (not `re.finditer`).
- Any change to `doc_mapping.build_doc_relations_edges` itself, or to
  Phase 21's mechanical detection — this phase only affects what
  `relation_enrichment.py` sends to the model, not what counts as a
  detected relation in the first place.

## Design decisions

**Re-derive the match position at enrichment time, don't persist it from
Phase 21's detection.** Considered having `build_doc_relations_edges`
record the match's character offset directly on the `doc_relations_edges`
row, avoiding a second `re.search` later. Rejected: `doc_relations_edges`
is a purely mechanical, fully-rebuilt-every-sync table (Phase 21) with no
concept of "this candidate hasn't been enriched yet, so remember exactly
where its excerpt should center" — that's an enrichment-time concern, and
threading it back through the mechanical table would blur what that table
means (a real relationship exists) with a detail nothing except
enrichment cares about. Re-running the same `re.search` at enrichment
time is cheap (one regex search over a source doc that's already being
read into memory anyway) and keeps `doc_relations_edges` exactly what it
already is.

**Window size split (before/after the match), left as an implementation
detail to tune, not locked in this plan.** A reasonable starting point is
asymmetric — more context *after* the match than before, since a mention
is often followed by explanatory text — but the exact split (e.g.
1,000 before / 3,000 after vs. a symmetric 2,000/2,000) doesn't have
real evidence behind it yet. Implement with a named constant, easy to
retune once real output quality from a second live validation run is in
hand — same "start simple, tune from real usage" posture this project
already applied to `enrichment.py`'s batch-size constant.

## Files

- `src/codecompass/graph.py` — `relation_enrichment_candidates` gains the
  target-name column.
- `src/codecompass/relation_enrichment.py` — `select_candidates`'s excerpt
  selection.
- `tests/test_graph.py`, `tests/test_relation_enrichment.py` — new cases
  per Covered above.
- `architecture/overview.md` — the relationship-enrichment description
  updated to describe centered excerpts rather than "first N characters."
- `decisions/` — new ADR (the re-derive-vs-persist call above is a real,
  non-obvious tradeoff worth recording).

## Verification

- `pytest`/`ruff check .` — full suite passes, including the new
  reproduction case (a source text with the needle past the current
  fixed cap).
- Manual, against this repo itself: **note that a plain re-sync will not
  by itself re-trigger enrichment for the two already-enriched vendor-doc
  relationships** — `doc_relation_enrichment`'s cache key
  (`content_hash`) is a hash of the full source/target text, which this
  phase doesn't change, so the existing cached (ungrounded) summaries
  will still read as fresh. Verifying the fix requires either manually
  clearing those two `doc_relation_enrichment` rows before re-running
  Phase B, or another equally direct way of forcing re-enrichment — do
  this deliberately, not by accident, and confirm the *new* summaries for
  `architecture/overview.md`/`docs/cli-reference.md` →
  `vendor/anthropic/src/README.md` actually describe Phase 27's own
  feature (the real content surrounding the "anthropic README.md"
  mention), not `init --scan`/"Core data model" as today's ungrounded
  ones do.
