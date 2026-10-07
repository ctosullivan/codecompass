# Phase 81 corrective-pass retro

## Goal

Reopen the already-`done` Phase 81 for a focused corrective pass after
post-completion review found nine real implementation defects outside
the original completion audit's own scope.

## Delivered

All nine corrections implemented, see `decisions/0073` for full detail:
targeted per-block refresh (never whole-slug) replacing the unsafe
automatic-refresh path; idempotent, consumable reconciliation (manifest
`state` lifecycle + content-addressed dedup + candidate-text
consumption); grounded README/CONTRIBUTING regions now participate in
real, bidirectional reconciliation via a new `doc-select-candidates`
command and `doc_region_edit` manifest item kind; honest advisory
grounding coverage reusing `doc_chunking.chunk_markdown`; canonical
meaning retrievable via an embedded machine-facing comment even under a
presentation-cache override; Requirement proposals now require an
explicit `Type: Requirement` structured block; external candidates
default to an honest `UNCLASSIFIED` basis rather than `proposed_policy`;
provenance derivation now walks the real `Evidence.observations:` field;
`codecompass-template`'s delivery was verified against the real public
repository and completed (pushed via SSH after HTTPS failed).

19 new/expanded tests added to `tests/test_knowledge_intermediate.py`
(49 total in that file), covering every corrected behaviour plus the
combination cases the original suite tested only in isolation (same-file
safe-refresh + pending edit, same-file safe-refresh + conflict,
apply-twice, apply-then-detect-again, grounded-edit-to-candidate,
grounded-edit-plus-claim-change-to-conflict, ungrounded-change-advisory,
presentation-override-plus-retrievable-canonical-meaning, mere-mention-
vs-explicit-Requirement, factual-hypothesis-vs-declared-intent,
directly_stated-with-and-without-real-Observation). Full project suite:
829 passed, 2 skipped.

## Real dogfood validation

Against a scratch copy of the real, 31-anchor `codecompass-domain`
corpus: confirmed a canonical-only change to one record and a pending
human edit to a *different* record in the *same* rendered file are both
handled correctly — the first refreshed, the second surviving
byte-for-byte and correctly entering the manifest alone.

Against the real `hledger-depth` slug: found and fixed a genuine,
live instance of the exact bug point 2 describes — a candidate's raw
text, applied under the pre-correction code in the original dogfood run,
was still sitting unconsumed in the live candidate region. Running the
corrected `select-candidates`/`apply` against this real, pre-existing
state confirmed the dedup check recognised the already-existing record
and refused to duplicate it, and the stale leftover text was correctly
consumed from the real file.

Against the real README.md's own grounded region: established the new
`.grounding-state.toml`/`.doc-chunk-state.toml` baselines for the first
time via `codecompass knowledge doc-select-candidates`.

## Not yet done at the point this retro was written

The usage-limit warning arrived mid-session after the implementation,
tests, and real dogfood validation were complete but before the standard
closeout sequence (fresh per-phase drift audit, learning/context-gap
triage, fresh independent completion audit) had run. Per `CLAUDE.md` §5,
Phase 81 must not be marked `done` again until that sequence completes
with a PASS. `planning/ROADMAP.md`'s own row reflects this honestly —
`reopened`, not `done` — until that happens.

## Lessons learnt

- A corrective pass surfaced by adversarial post-completion review can
  find real defects a first, good-faith independent audit genuinely
  missed — not because the audit was careless, but because some defects
  (concurrency races, idempotency, a second direction of a bidirectional
  flow) only show up under combination scenarios a single-pass audit
  scoped to "does this do what it claims" doesn't always construct.
- Dogfooding against a scratch copy of real, already-existing project
  data (not just disposable fixtures) found a real, live bug instance
  the fixture-based unit tests alone would not have — the stale
  candidate text in `hledger-depth` only existed because an earlier,
  real dogfood run had exercised the pre-correction code against real
  content. Worth preserving this practice: when fixing a bug in a
  mechanism already dogfooded once, re-run the dogfood against the
  *existing* real artefacts it already touched, not only fresh
  fixtures.
