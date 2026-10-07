# Phase 81 second corrective-pass retro

- **Date:** 2026-10-07
- **Commit(s):** `7a0e270` (main correction), `42f9486` (drift-audit
  follow-up fix), `2e1b5a7`/`939140e` (L-086 promotion),
  `1c3981b`/`a9bcd02` (L-087/L-088 user-approved `CLAUDE.md` amendment +
  promotion), plus the post-audit fix commit(s) closing the findings
  below
- **Agents used:** `docs-reconstructor` (drift audit), `knowledge-curator`
  (learning/context-gap triage), `release-phase-auditor` (completion
  audit, two passes)

## Where we are

This is the second of two same-day reopenings of Phase 81 (persistent
bidirectional intermediate knowledge layer), itself the current head of
Priority D's own trajectory (`planning/ROADMAP.md`'s Priority D row).
Phase 81 originally shipped, was dogfooded, and closed `done`. A first
corrective pass (`decisions/0073`) then fixed nine real defects a
post-completion review found. This second pass reviews that first
corrective pass's own newly-written code — mostly the grounded-document
reconciliation path it introduced — and fixes fourteen further defects
and gaps found there. After this phase, the knowledge-layer feature's
grounded-document half is exercised and corrected to the same depth its
intermediate-document half already received, and the project gained two
new standing plan-time requirements (`L-087`/`L-088`) aimed at catching
this exact shape of gap earlier next time.

## Goal

Correct fourteen real defects/gaps found reviewing the first corrective
pass's own code (nearly all in grounded-document reconciliation), then
run the phase's full closeout sequence to a genuine `done`.

## Scope delivered vs planned

All fourteen items from the governing request were delivered as scoped —
no scope was dropped or deferred. One item (6, the public template
update) required an additional, unplanned-for verification step
(confirming via `git fetch` that the push actually reached the real
remote, not just a local commit) which the first corrective pass had
already learned the hard way was necessary. The closeout sequence itself
ran longer than planned: a first independent completion audit returned
**FAIL** on verification/documentation-integrity grounds (see "What
didn't work" below), requiring an unplanned second round of fixes and a
second audit pass before the phase could close — this is itself now
part of what shipped, not a deviation hidden from this retro.

## What was achieved

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

`tests/test_knowledge_intermediate.py` now has 65 tests (up from 32
before this pass), covering every correction directly: stable-identity
insertion/reordering and duplicate-id rejection; detect-without-apply
non-acknowledgement for both the `doc_candidate` and `claims_changed`
cases, and the separate ungrounded-chunk advisory; apply-time concurrency
conflict on a cited grounding record (and the matching
success-when-nothing-changed case); presentation-vs-semantic branching
for a grounded-document edit; post-apply grounding discoverability from
the new Claim; `Type: Intent` header-stripping (asserting the resulting
Claim's own `statement` content, not only its `basis`); candidate-
disappearance fail-closed behaviour (both the genuine-race case and the
already-promoted-safe-no-op case); and cross-kind dedup independence in
both directions (a pre-existing Claim never blocking a new Requirement,
and vice versa). Full project suite: 841 passed, 2 skipped.

Two new project-wide plan-time requirements landed in `CLAUDE.md` §1
(user-approved per §0, `commit 1c3981b`): a plan introducing a persisted
"last-known-state" mechanism must state how detection differs from
acknowledgement (`L-087`); a plan introducing a new tracked, re-orderable
entity must check for an existing identity convention and test
insertion/reordering specifically (`L-088`). A third, scoped addition
landed in `.claude/agents/release-phase-auditor.md` (`L-086`): a
corrective pass's own newly-written code is full audited scope, never a
lighter-touch re-check.

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

## What worked

- Dogfooding against a scratch copy of the *live* corpus (not only
  disposable fixtures) continues to pay off, as it did in the first
  corrective pass: it's what let the apply-time concurrency conflict and
  the post-apply grounding update be exercised against a real, already-
  grounded region with real citation structure, not a synthetic
  approximation of one.
- Fixing the stable-identity mechanism (item 10) first, before the other
  thirteen items, was the right sequencing call — every baseline-keying
  change downstream depended on it, and building it last would have
  meant re-touching every other fix's own state-key logic afterward.
- The `release-phase-auditor`'s FAIL on this pass's own first completion
  audit is itself a case of the process working as designed: it caught a
  real gap (claimed test coverage that didn't exist) that every
  mechanical check (lint, strict validation, the full test suite itself)
  was structurally incapable of catching, because the gap was the
  *absence* of a test, not a failure of an existing one.

## What didn't work

- The implementing session's own retro and `decisions/0074` both
  overstated test coverage before the first completion audit ran —
  claiming `Type: Intent` header-stripping, candidate-disappearance
  fail-closed behaviour, and cross-kind dedup independence were covered
  by name, when in fact one assertion checked the wrong field and the
  other two had no test at all (only ad hoc, non-persisted manual
  verification during implementation). This is exactly the failure shape
  `CLAUDE.md` §1's own `L-021`/`L-070`/`L-075` sentences exist to prevent
  for a *plan's* verification section, but nothing analogous currently
  requires a *retro's* own coverage claims to be checked against the real
  diff before being written — a gap this retro's own process-improvement
  note below names explicitly.
- `planning/CONTEXT.md` was left stale after the drift audit and learning
  triage both landed — it still described them as future, pending work
  at the point the first completion audit ran. The update should have
  happened in the same sitting as each of those steps, not deferred to
  end-of-phase.
- No persisted drift-audit report file was produced for this pass (the
  project's own usual convention for most other phases), only a
  commit-message mention. The audit genuinely ran and found a genuine,
  real gap (`ai-docs/README.md`), but its own account was not durably
  recorded anywhere a future session could find without reading git log.

## Lessons learnt

- A corrective pass aimed at fixing real defects can itself introduce new
  ones in the same review cycle — most of this pass's fourteen findings
  were in code `decisions/0073` had just written (the grounded-document
  path), not in the original Phase 81 design. A pass that adds a new
  mechanism under time pressure is exactly the kind of change most worth
  a second, independent look before being trusted as closed. (`L-086`)
- "Detection must never itself count as acknowledgement" is a general
  principle this project had already half-learned for canonical Claim
  dedup and apply-time races, but had not yet applied consistently to
  *baseline* state for an advisory/grounding mechanism — the same
  discipline (observe vs. commit are different verbs) applies anywhere a
  mechanism persists "the last known state" rather than just comparing
  against the live state fresh each time. (`L-087`)
- Giving a tracked entity (here, a grounded document region) only a
  positional identity works until the first insertion/reorder — the same
  failure mode CodeCompass had already corrected once before for anchored
  knowledge blocks (`decisions/0073`'s own stable-anchor work) recurred
  independently in the newer grounded-document code, because the two
  mechanisms were implemented separately rather than sharing an identity
  convention from the start. (`L-088`)
- A closeout retro's own coverage claims ("N new tests covering X, Y, Z")
  are themselves an assertion that needs checking against the real diff,
  not merely against the implementer's own memory of intent — an
  independent audit is exactly what catches this, but it is cheaper to
  verify each named claim against a `grep`/direct test read before
  writing the retro in the first place than to rely on the audit catching
  it after the fact.

## Process-improvement feedback

- Consider requiring whoever writes a phase's own retro to verify each
  named test-coverage claim against the actual test file (one grep or
  read per claim) before the retro is written, not only before the audit
  runs — the audit is a backstop, not the first line of defense, and
  catching this kind of gap earlier would have saved an entire extra
  audit round-trip on this phase.
- `planning/CONTEXT.md` should probably be updated at the moment each
  closeout step (drift audit, learning triage) actually completes, not
  batched to end-of-phase — this phase's own staleness finding happened
  precisely because the update was deferred.

## Candidate learnings filed

`L-086`, `L-087`, `L-088` — all filed to `planning/learnings/inbox.md`
during this phase's own triage step, all promoted (see "What was
achieved" above for where each landed).

## Where we're going

This closes out Phase 81 as a whole (original implementation + both
corrective passes) once the fresh completion audit following these fixes
passes. Priority D's own broader trajectory
(`planning/ROADMAP.md`) is otherwise unchanged by this phase — the next
concrete deliverable in that row remains whatever is named there as not
yet started. No stage gate in `planning/v1-redefinition/README.md` §7 is
affected by this phase either way.

## Time / cost note

Three same-day sessions on one phase (original implementation, first
corrective pass, second corrective pass), the second corrective pass
itself running long enough to need a mid-pass context-window
continuation. The second corrective pass's own closeout required two
independent-audit round-trips (FAIL, then a fix cycle, then re-audit) —
worth noting as a real cost of the overstated-coverage gap above, not
just a process formality.
