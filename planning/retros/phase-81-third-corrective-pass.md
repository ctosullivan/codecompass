# Phase 81 third corrective-pass retro

- **Date:** 2026-10-08
- **Commit(s):** (this pass's own implementation + validation commit(s),
  recorded at closeout)
- **Agents used:** `docs-reconstructor` (drift audit, if warranted),
  `knowledge-curator` (learning/context-gap triage, if warranted),
  `release-phase-auditor` (fresh completion audit)

## Where we are

This is the third same-effort reopening of Phase 81 (persistent
bidirectional intermediate knowledge layer). The original implementation
and two prior corrective passes (`decisions/0073`, nine defects;
`decisions/0074`, fourteen defects) were each closed `done` with a
passing independent completion audit. This pass reviews the second
corrective pass's own work one level deeper and fixes two further real
defects it left behind — both narrow applications of principles
`decisions/0074` itself had already established elsewhere in the same
codebase, not new architecture.

## Goal

Correct two real defects found reviewing the second corrective pass: (1)
a valid `Type: Requirement` candidate could still be created from a
stale manifest because its own live-text presence check never ran before
its type-specific apply path; (2) grounded-region concurrency identity
omitted the cited-id set itself, so adding/removing a grounding citation
was silently invisible to both detection and apply.

## Scope delivered vs planned

Both items delivered exactly as scoped, plus their required regression
tests and dogfood exercises — no scope added or dropped. The governing
request's own explicit "do not duplicate this logic independently across
multiple branches" instruction for item 1 was followed literally: a new
`_CandidateIdentity` value and `_derive_candidate_identity` helper are
the single source of truth for a candidate's own kind/statement/decision,
used by both the presence check and the real apply path.

## What was achieved

**Item 1 — candidate-presence validation before all candidate-type
branches.** `_requirement_proposal_validity` factored out of
`_apply_requirement_proposal` as a pure, side-effect-free check. A new
`_CandidateIdentity` dataclass (`kind`, `statement`, `decision`) and
`_derive_candidate_identity` function compute a candidate's own intended
canonical identity exactly once, before `_apply_candidate_addition`'s
live-text presence check runs — previously, a `Type: Requirement`
candidate branched into `_apply_requirement_proposal` *before* that
check, so a stale manifest could still create a Requirement whose live
candidate text had already been deleted or materially changed. The
presence check (and its own type-aware "search for an already-applied
equivalent, else fail closed" fallback) now runs first, for every
candidate shape, using that one derived identity.

**Item 2 — grounded-region concurrency identity includes cited-id
membership.** `detect_grounded_region_changes` now computes
`membership_changed = sorted(current cited ids) != sorted(baseline cited
ids)` — explicitly order-insensitive (`CL-A, CL-B` reordered to `CL-B,
CL-A` is not a change) but add/remove-sensitive — and folds it into the
existing `structural_changed` signal alongside `region_changed`, so a
membership-only edit produces `case = "doc_candidate"`, never a silent
`"noop"`, and flows through the exact same review/apply path a prose
edit already uses. Per-id content-drift detection is now restricted to
ids cited in *both* the baseline and the live marker, so an added/removed
id is never double-counted as "its own content changed." `_apply_doc_region_edit`
gained a matching apply-time check — `sorted(live cited_ids) ==
sorted(manifest cited_ids)` — immediately after the region-text check and
before the per-id content-hash check, failing closed (no record created,
no baseline advanced) on any mismatch.

8 new tests added to `tests/test_knowledge_intermediate.py` (73 total):
a deleted valid Requirement candidate with no match fails closed, zero
records created; a deleted valid Requirement candidate with a genuine
already-applied equivalent is a safe no-op, no duplicate; the existing
ordinary-Claim candidate-disappearance behaviour is unaffected
(regression guard); removing a cited id is not `noop` and stays pending
across repeated detection; adding a cited id is not `noop`; reordering
cited ids only is `noop` (documented order-insensitive policy); a
membership change between detection and apply fails the apply closed
with zero stray records; a mere reorder between detection and apply does
not block the apply. Full project suite: 853 passed, 2 skipped. Lint and
strict knowledge-base/user-docs validation both clean.

Append-only ADR `decisions/0075` records both corrections, explicit that
this is an implementation correction already implied by `decisions/0074`'s
own principles, not a new architectural decision.
`docs/codecompass-knowledge-workflow.md` and `docs/cli-reference.md` both
updated to describe the corrected membership-change/apply-time behaviour.

## Real dogfood validation

Against a scratch copy of the real, live `codecompass-domain` corpus and
its real grounded README region (`region:intermediate-knowledge-layer`,
citing `CL-KNOW-001`):

1. Confirmed the real baseline re-detects clean (`noop`) with no drift.
2. Added a second, already-existing, real citation (`CL-ADPT-001`) to
   the live marker, with the region's own prose left byte-identical —
   confirmed `doc-select-candidates` surfaced this as a real candidate
   (`doc_candidate`), never a silent `noop`, exactly as `decisions/0075`
   requires. No synthetic fact was invented for this step — reusing an
   already-real citation kept the scratch corpus's own content honest.
3. Mutated the marker's own membership a second time (removing
   `CL-ADPT-001` again) between detection/manifest-write and apply —
   confirmed `apply` refused with an explicit "cited-record membership
   changed since detection" message, and confirmed directly (file count
   before/after, 31 `CL-*.yaml` files in both the scratch copy and the
   real repository) that zero stray records were created.

Against a dedicated, disposable throwaway slug
(`planning/knowledge/dogfood-requirement-scratch/`, never merged into any
real project knowledge, confined entirely to the scratch copy) with its
own synthetic, clearly-labelled-as-throwaway `DEC-SCRATCH-001` Decision:
created a valid, structurally-complete `Type: Requirement` candidate,
detected it, accepted it in the manifest, then deleted the candidate text
from the live file before running `apply` — confirmed `apply` refused
with an explicit apply-time-race message, and confirmed directly that
the slug still contains only its own original `DEC-SCRATCH-001.yaml`,
zero Requirement or Claim records created. This exercises exactly the
scenario `decisions/0073`'s "the current ordinary candidate path
correctly fails closed" standard already set for a plain Claim, now
genuinely also true for an explicit Requirement.

## What worked

- Factoring `_requirement_proposal_validity` out of
  `_apply_requirement_proposal` made the bug's own fix mechanical once
  identified: the validity check already existed in exactly the right
  shape, it just needed to run earlier and be shared rather than
  recomputed.
- Reusing an already-real citation (`CL-ADPT-001`) for the membership-
  addition dogfood step, rather than inventing a new fact, kept the
  scratch corpus honest while still exercising the real code path — the
  membership mechanism doesn't care whether a cited id's own content is
  "interesting," only that the set changed.

## What didn't work

- No misfires this pass — both defects were narrow, well-specified by
  the governing request's own required flow diagram, and each had a
  single, localized fix point once the relevant function was read in
  full.

## Lessons learnt

- A concurrency/identity model that was deliberately extended once
  (`decisions/0074`'s dual-hash model, extended to cover cited-record
  *content*) can still omit a further dimension (cited-record *set
  membership*) that feels, in hindsight, like an obvious sibling of what
  was already covered — worth explicitly enumerating "what are all the
  independent things that could change here" as its own design-review
  step for any concurrency-identity mechanism, not just trusting that
  extending coverage once means coverage is now complete.
- A "derive once, reuse everywhere" helper (`_CandidateIdentity`) is both
  the fix and a structural guard against the same bug recurring in a
  fourth candidate shape later — worth preferring this shape over
  per-branch duplication whenever a governing instruction doesn't
  explicitly require otherwise.

## Process-improvement feedback

- None beyond what `L-086`/`L-087`/`L-088` (second corrective pass)
  already captured — this pass's own two defects are each a concrete
  instance of the general principles those three learnings already
  generalised (detection/presence consistency across branches;
  concurrency identity completeness), rather than a new process gap.

## Candidate learnings filed

To be determined by this pass's own `knowledge-curator` triage step —
recorded here once that step runs.

## Where we're going

Closes out Phase 81 as a whole (original implementation + three
corrective passes) once this pass's own fresh completion audit passes.
No change to Priority D's own broader trajectory in `planning/ROADMAP.md`
and no stage-gate impact.

## Time / cost note

One session, two narrowly-scoped defects with explicit required-flow
specifications supplied by the governing request itself — meaningfully
shorter than either prior corrective pass, consistent with a
well-specified, narrow patch rather than an open-ended review.
