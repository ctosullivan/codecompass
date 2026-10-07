# Phase 81 second corrective-pass retro

## Goal

Reopen the already-reopened Phase 81 a second time, same day, after
further review of the first corrective pass (`decisions/0073`) itself
found fourteen more real defects and gaps — nearly all in the grounded-
document reconciliation path that pass introduced — and run the phase's
full closeout sequence to a genuine `done`.

## Delivered

All fourteen corrections implemented, see `decisions/0074` for full
detail: baseline advancement now requires an actual `apply` or explicit
acknowledgement, never mere detection (two new commands,
`doc-acknowledge-stale`/`doc-acknowledge-chunks`); apply-time concurrency
checks for a grounded document's own cited records, not just its own
text; an explicit `semantic_change` field distinguishing a presentation-
only documentation edit (acknowledged, no Claim) from a factual one
(creates a candidate Claim); a semantic edit's new Claim added back to
the region's own grounding marker so it stays discoverable; corrected
inline candidate instructions matching the real `Type: Requirement`/
`Type: Intent` protocol; the public `codecompass-template` rewritten and
pushed; a `Type: Intent` block's own header no longer leaking into the
resulting Claim's `statement`; a disappeared candidate with no matching
record now failing closed instead of reporting false success; type-aware
(and decision-aware) deduplication so a Claim and a Requirement never
cross-dedup; and stable `region:<id>` grounded-region identity surviving
insertion/reordering, with duplicate explicit ids failing closed.

29 new tests added to `tests/test_knowledge_intermediate.py` (61 total),
covering every correction directly: stable-identity insertion/reordering
and duplicate-id rejection; detect-without-apply non-acknowledgement for
both the `doc_candidate` and `claims_changed` cases, and the separate
ungrounded-chunk advisory; apply-time concurrency conflict on a cited
grounding record (and the matching success-when-nothing-changed case);
presentation-vs-semantic branching for a grounded-document edit; post-
apply grounding discoverability from the new Claim; `Type: Intent`
header-stripping; candidate-disappearance fail-closed behaviour; and
cross-kind dedup independence in both directions. Full project suite:
830 passed, 2 skipped.

## Real dogfood validation

Against a scratch copy of the real, live `codecompass-domain` corpus and
its real grounded README region (citing `CL-KNOW-001`): exercised the
complete lifecycle end to end —

1. Confirmed the already-migrated real baseline re-detects clean
   (`noop`) with no drift from the `region:<id>` migration itself.
2. A presentation-only edit (capitalisation) detected, reviewed with
   `semantic_change = false`, applied — confirmed zero new Claims, the
   edit acknowledged, and a clean re-detection afterward.
3. A genuine factual edit detected, reviewed with `semantic_change =
   true`, applied — confirmed exactly one new Claim created
   (`CL-CODECOMPASSD-014`), the live README marker rewritten to cite both
   the original and new Claim, and `find_grounded_doc_regions` correctly
   discovering the region from the *new* Claim's id.
4. A further factual edit detected and its manifest written, then the
   cited `CL-KNOW-001` record mutated before apply — confirmed `apply`
   refused with an explicit apply-time concurrency message and created
   no stray record (verified directly: exactly one `CL-CODECOMPASSD-*`
   record exists in the scratch corpus afterward, not two).

The real README.md's own pre-existing grounding marker was migrated to
`region:intermediate-knowledge-layer` and `.grounding-state.toml` re-keyed
to match, confirmed via live `codecompass knowledge doc-select-candidates`/
`knowledge status` runs against the real repository to report clean with
no spurious drift.

The public `codecompass-template`'s `optional-intermediate-knowledge/`
README and worked example were rewritten for the corrected workflow,
committed, and pushed to the real public default branch
(`ctosullivan/codecompass-template`, commit `bd2420d`) — verified present
via a fresh `git fetch` against the actual remote, not just a local
commit.

## Lessons learnt

- A corrective pass aimed at fixing real defects can itself introduce new
  ones in the same review cycle — most of this pass's fourteen findings
  were in code `decisions/0073` had just written (the grounded-document
  path), not in the original Phase 81 design. A pass that adds a new
  mechanism under time pressure is exactly the kind of change most worth
  a second, independent look before being trusted as closed.
- "Detection must never itself count as acknowledgement" is a general
  principle this project had already half-learned for canonical Claim
  dedup and apply-time races, but had not yet applied consistently to
  *baseline* state for an advisory/grounding mechanism — the same
  discipline (observe vs. commit are different verbs) applies anywhere a
  mechanism persists "the last known state" rather than just comparing
  against the live state fresh each time.
- Giving a tracked entity (here, a grounded document region) only a
  positional identity works until the first insertion/reorder — the same
  failure mode CodeCompass had already corrected once before for anchored
  knowledge blocks (`decisions/0073`'s own stable-anchor work) recurred
  independently in the newer grounded-document code, because the two
  mechanisms were implemented separately rather than sharing an identity
  convention from the start.
