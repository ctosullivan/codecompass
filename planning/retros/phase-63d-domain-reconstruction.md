# Phase 63D retro — Domain reconstruction

- **Date:** 2026-09-23
- **Commit(s):** `fef153b` (agent setup: `domain-skeptic` created,
  `context-researcher`/`docs-reconstructor` extended), `f39a986`
  (corpus drafted, researched, independently reviewed), `27bac36`
  (CONTEXT.md status update), this phase's own closeout commit for the
  post-approval corrections and audits.
- **Agents used:** three parallel `context-researcher` dispatches
  (evidentiary-model cluster, context/packaging cluster, adapter/
  protocol cluster), one `domain-skeptic` dispatch (independent review),
  `docs-reconstructor` (per-phase drift audit), `release-phase-auditor`
  (DoD audit).

## Where we are

Stage F is complete (Phases 60–63, GATE DF PASS). Phase 63D
(`decisions/0060`) is the new bridge phase sitting between Stage F and
Stage G — the first project-scoped application of the newly-formalized
Scope → Plan → Domain → Design → Implement methodology's own Domain
stage, and the first real use of the new `domain-skeptic` role.

## Goal

Dogfood CodeCompass against its own repository to build an
evidence-backed domain corpus (`docs/domain/`) for CodeCompass's own
core concepts — evidence, observation, claim, adapter, context, and
others found along the way — derived from source/tests/ADRs/behaviour,
never from treating existing documentation as authoritative by default.
Produce an approved domain baseline Phase 64 (blank-slate documentation
reconstruction) can consume rather than independently rediscover.

## Scope delivered vs planned

Delivered exactly as the thrice-amended plan scoped, plus the
post-approval correction cycle described below:

- 19 concept pages under `docs/domain/concepts/`: the 14 concepts named
  directly in the plan's own §1, plus `vendor`, `ecosystem`, `capability`,
  `digest`, and `requirement` — all justified by real disambiguation
  work the research found necessary, not scope creep.
- 6 integration files: `README.md`, `glossary.md`, `invariants.md`,
  `examples.md`, `open-questions.md`, `references.md`.
- 138 supporting Observation/Evidence/Claim/Derivation records under
  `planning/knowledge/codecompass-domain/` (id-prefixed `EVID`/`CTXT`/
  `ADPT` by cluster, `SKEP` for `domain-skeptic`'s own resolving
  evidence).
- One new agent role (`domain-skeptic`), created per the plan's own
  Files section; two existing agent files extended
  (`context-researcher`'s write boundary widened to `docs/domain/` for
  project-scoped work; `docs-reconstructor`'s per-phase drift audit
  gained the domain-claim staleness-candidate check).
- One real, evidence-based resolution of a disclosed contradiction
  (`decisions/0058`'s adapter/adaptor naming drift — `CL-ADPT-010`
  supersedes `CL-ADPT-008`, via real `git log`/`git ls-remote`
  investigation, not guessed at).
- One real tooling fix, found along the way:
  `scripts/check_knowledge_base.py`'s cross-reference check only looked
  within one feature directory, producing 11 false positives against
  this corpus's own legitimate cross-feature citations — fixed to
  resolve against the union of all `planning/knowledge/*/` directories,
  verified (0 findings after, full suite still 623 passed/2 skipped).
- Two real implementation gaps found incidentally, routed to
  `planning/learnings/inbox.md` as `L-031`/`L-032` (future-improvement
  candidates for `knowledge-curator`), not fixed inline — matching the
  plan's own explicit scope boundary (evidence and documentation only,
  no `src/codecompass/` change).

**Post-approval correction cycle**: the actual user/domain owner
approved the corpus subject to four corrections found during their own
review:
1. `provenance.md`'s Definition section asserted "the three enrichment
   tables each carry a single `model` column" in the same breath as
   correctly noting `symbol_enrichment` has none — an internal
   self-contradiction. Fixed to state plainly that two of the three
   carry it.
2. `evidence.md`'s own "Relationships" section made the identical
   over-generalisation in passing. Fixed to point at `provenance.md`'s
   own corrected account rather than restating it.
3. `requirement.md` cited `phase-54c-evidence-workflow.md` — missing
   "-knowledge-" from the real file's name
   (`phase-54c-evidence-knowledge-workflow.md`). Fixed; swept the whole
   corpus for the same typo elsewhere (none found).
4. Phase 63D's own status was inconsistent: `CONTEXT.md` correctly said
   "corpus complete, awaiting approval" while `ROADMAP.md` and the
   phase plan still said "not started"/"plan only" — a real closeout
   gap, not caught before presenting the corpus for review. Reconciled
   across `planning/phase-63d-domain-reconstruction.md`,
   `planning/ROADMAP.md` (both the Phase 63D row and the Stage G row),
   and `planning/v1-redefinition/roadmap.md` (the full Phase 63D
   section, including its own Exit criteria and a second,
   previously-missed traceability-spine ordering error found while
   fixing it).

All four applied and independently re-verified
(`check_user_docs.py --strict`, `check_knowledge_base.py`, a full
repository-wide grep for the stale filename and the wrong spine
ordering) before this retro was written.

## What was achieved

- `check_user_docs.py --strict`: clean, throughout.
- `check_knowledge_base.py`: clean (0 findings, down from 11
  false positives, after the checker fix).
- Full `pytest`: 623 passed, 2 skipped — unchanged from Phase 63's own
  baseline, confirming the `scripts/` fix introduced no regression.
- **Zero genuine domain/product escalations reached the actual user.**
  `domain-skeptic`'s own independent review resolved what could be
  resolved with evidence and correctly left the rest as disclosed,
  non-blocking open questions.
- The actual user's own review caught four real defects
  `domain-skeptic`'s own review had not — a genuine, useful check this
  project's own no-stand-in design intends the human review step to
  provide, not a rubber-stamp step.

## What worked

- Splitting the 19-concept investigation into three parallel,
  cleanly-bounded clusters (evidentiary model; context/packaging;
  adapter/protocol) let each `context-researcher` dispatch go deep
  without diluting focus across unrelated concepts, while still
  producing genuinely cross-referenced pages (each cluster explicitly
  disambiguated its own concepts from named neighbours in other
  clusters).
- Dispatching `domain-skeptic` against the *integrated* corpus (after
  all three clusters landed, not against each cluster in isolation)
  is what let it catch cross-cluster consistency issues a single
  cluster's own review never would have seen.
- `domain-skeptic` resolving the `decisions/0058` naming drift with
  real `git log`/`git ls-remote` evidence, rather than either guessing
  or reflexively escalating it, is exactly the "attempt resolution
  before treating anything as escalation-worthy" behaviour this role
  was designed for — and it worked on its first real use.

## What didn't work

- **The internal self-contradiction in `provenance.md`'s own Definition
  section (correction 1) should have been caught by `domain-skeptic`'s
  own review, and wasn't.** `domain-skeptic`'s own report explicitly
  re-verified the *Counterexample* section's claim about
  `symbol_enrichment` against the real schema and confirmed it
  accurate — but did not notice that the *Definition* section, two
  paragraphs earlier in the same file, asserted the opposite in
  passing. This is a real gap in this first review: checking a page's
  own central claim against source is necessary but not sufficient —
  checking a page's own sections against *each other* is a distinct
  pass `domain-skeptic`'s own charter names ("actively search for
  contradictions... between two concept pages") but doesn't explicitly
  name *within* one page, and this review didn't do it thoroughly
  enough for `provenance.md` specifically.
- **This phase's own closeout status update (marking `CONTEXT.md`
  correctly, but not `ROADMAP.md`/the phase plan) repeated a mistake
  already named as a lesson during Phase 62's own closeout** — the
  same "the plan file's own Status line and the roadmap tables need
  the exact same closeout discipline as CONTEXT.md, and are easy to
  forget because they're not the file actively being narrated" pattern.
  This is now a second occurrence.

## Lessons learnt

- **A within-page consistency check is a distinct pass from a
  claim-against-source check, and both are needed.** `domain-skeptic`'s
  own charter should be read (and, if the pattern recurs, amended) to
  make explicit that "search for contradictions" includes a page's own
  sections against each other, not only page-against-page or
  page-against-source. Filed as a candidate learning (see below).
- **The "did I update every planning-status file, not just the one I'm
  actively narrating" checklist needs to be more than tribal memory** —
  this is the second time in two consecutive phases (62, then 63D) that
  `CONTEXT.md` was updated correctly while `ROADMAP.md`/the plan file's
  own Status line were not. Filed as a candidate learning (see below).

## Process-improvement feedback

- Consider whether `roadmap-context-curator`'s own dispatch should
  become a mandatory step immediately before presenting any phase's
  work for user review (not only at phase start/end as currently
  practised) — it exists specifically to reconcile `ROADMAP.md`/
  `CONTEXT.md` against actual state, and would likely have caught this
  phase's own status inconsistency before the user had to.

## Candidate learnings filed

- Both "what didn't work" items above are real, second-occurrence-or-
  first-occurrence findings worth `knowledge-curator`'s own independent
  triage, not the lead's unilateral call that they're (or aren't)
  candidate-worthy — filed to `planning/learnings/inbox.md` as `L-033`
  (within-page consistency checks) and `L-034` (planning-status closeout
  discipline), for `knowledge-curator` to triage during this phase's own
  closeout, per the process `decisions/0060`'s own precedent (Phase 62)
  already established for exactly this situation.

## Where we're going

Phase 64 (blank-slate documentation reconstruction, Stage G) is next —
gated on nothing further; both Stage F and Phase 63D are complete. Its
own plan does not yet exist and must be written per `CLAUDE.md` §1
before implementation begins. It consumes this phase's own approved
`docs/domain/` corpus directly, per `documentation-lifecycle.md` §3's
own amended text, rather than independently rediscovering domain
terminology.

## Time / cost note

No AI-API spend beyond agent dispatch compute — this phase is pure
research/documentation/evidence work, no `src/codecompass/` change, one
small `scripts/` fix.
