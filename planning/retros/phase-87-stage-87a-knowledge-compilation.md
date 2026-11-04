# Phase 87 Stage 87A retro — Prove knowledge compilation

- **Date:** 2026-11-04
- **Commit(s):** `b2fbc23`, `d237826`, `db4aa5b`, `a54be15`, `d2e51f6`,
  `e73a6c7`, `a9667b5`, `fe664b7`, `b81ace7`, plus this retro's own
  closeout commits.
- **Agents used:** `Plan` (three independent planning-review rounds —
  the original READY WITH NON-BLOCKING OBSERVATIONS, the amendment's
  NOT READY→READY round, this restructuring pass's NOT READY→READY
  round), `general-purpose` (×6 — three real semantic-support/
  completeness dispatches and three real editorial-quality dispatches
  against the live demonstration draft), `docs-reconstructor`
  (per-phase drift audit), `release-phase-auditor` (Stage 87A DoD
  audit, FAIL then fix-and-recheck), `knowledge-curator` (candidate
  learning triage, L-118/L-119).

## Where we are

Phase 86 closed with the Knowledge Placement Policy and its enforcement
surface fully done. Phase 87 was planned once (READY WITH NON-BLOCKING
OBSERVATIONS), then amended for six implementation-contract gaps (also
READY), then — this session — restructured into three stages after a
*second* independent review found the single-stage scope too large and
four further real implementation-contract defects. Stage 87A is the
first of those three stages: prove the smallest useful
knowledge-compilation workflow — one bounded section, real evidence,
real independent verification, real publication — before building the
complete documentation platform.

## Goal

Demonstrate that CodeCompass can generate one genuinely useful
documentation section from canonical knowledge, with traceable evidence
and independent verification, using the smallest implementation that
proves the complete vertical path: schema → accepted knowledge →
hydrated evidence → bounded packet → isolated section generation →
independent factual verification → editorial assessment → publishable
prose.

## Scope delivered vs planned

Delivered exactly the plan's own §D.1 list: the minimal schema format,
`doc_compiler.py`'s deterministic resolution/hydration/gap-detection/
citation-scope-checking, `check_doc_schema.py`, the corrected clean-room
adapter (`compile_doc_section.py`), the three-question claim-
verification workflow (scope mechanically, depth and completeness via
one independent dispatch), a separate editorial dispatch,
`publish_section`/`maintain_document` on the real five-state grounded-
region mechanism, and the `docs` CLI group. One deviation, caught by
the independent audit rather than planned for: the DoD's own paper
trail (`CONTEXT.md`, `ROADMAP.md`, `CHANGELOG.md`, this retro, a
persisted drift-audit report, learnings triage, `cli.md`, an
architecture doc) was not kept current *during* implementation — it was
caught, and is being closed, only at the end, in response to the first
`release-phase-auditor` pass's own FAIL verdict. Nothing from the
plan's own explicit Stage 87A exclusions (full-document generation,
the execution harness, full-suite schemas, deterministic CLI-reference
generation, the matched-baseline experiment, new standing agents) was
built — confirmed directly by the auditor via `find`, not assumed.

## What was achieved

A real, complete, end-to-end knowledge-compilation run against the live
repository, three times, with no mocking and no synthetic fixture:
round 1 and round 2 were both correctly rejected by independent review
(an invented elaboration not actually in the cited record; auditor-
facing phrasing and a self-referential terminology tangent, recurring
in different wording after a first, too-generic prompt revision); round
3 passed both independent dispatches and was published —
`README.md` now has a real "Understanding Digests" section, grounded in
`CL-CTXT-005`, wrapped in a real `codecompass-grounded-by` marker.
`codecompass docs maintain` was then run for real and correctly (a)
established a baseline for the new section and (b) detected and left
untouched a genuine, pre-existing `doc_candidate` region
(`intermediate-knowledge-layer`) that predates this phase entirely —
unplanned, real evidence that the "unrelated sections remain unchanged"
guarantee holds against actual content, not only a fixture.

## What worked

- **Test-first discipline caught every implementation bug before it
  reached the real demonstration run, and the real demonstration run
  caught two more that no unit test had anticipated.** The stray-space-
  after-citation-strip defect and the `schema_slug` dot-truncation
  defect were both found live, by the gates actually doing their job
  (an independent editorial dispatch; `publish_section`'s own fail-
  closed region-id validation) — not by inspection. Both got regression
  tests immediately.
- **Dispatching the same two independent reviews against three real,
  successive drafts, rather than trusting a single pass, is what
  actually demonstrated the architecture works.** A single successful
  round would have proven much less than two real, independently-
  confirmed failures followed by a real, independently-confirmed pass.
- **Correcting a wrong design assumption by re-deriving it from the
  real source, not by patching around the symptom** — finding that
  `prepare_cleanroom_branch.py` fundamentally cannot export uncommitted
  runtime data (§G.B) led to a cleaner, narrower, better-justified
  adapter design than the original plan's own allow-list-extension
  idea, confirmed independently twice.
- **A narrow, mechanically-verifiable re-check (not a full re-review)
  for a single, literal correction** (e.g. the `check_doc_schema.py`
  field-shape fix, the `detect_grounded_region_changes` five-state fix)
  kept the review cost proportional to the finding, without skipping
  independent verification entirely.

## What didn't work

- **The project's own DoD paper-trail requirements (`CLAUDE.md` §5)
  were not kept current during implementation**, despite being
  well-known and explicit. The pace of chasing the real demonstration
  (three real model-call rounds, each needing a fresh review dispatch)
  crowded out the bookkeeping until the first independent audit caught
  it — a FAIL that was entirely about missing paper trail, not about
  code correctness, confirmed by the auditor's own independent
  re-verification of everything else. This is the session's one real
  process failure.
- **A vague prompt revision ("avoid tangents") did not fix a specific,
  named content problem** — the model reintroduced the identical defect
  in different wording. Only a literal, specific instruction naming the
  exact recurring phrasing worked (filed as `L-119`).
- **A derived slug's own naive suffix-stripping was tested only against
  the common case** (a document name with no dot) and broke on the
  real first demonstrator's own filename. Caught live, not by the unit
  tests that existed at the time (filed as `L-118`).

## Lessons learnt

See `L-118`/`L-119` (filed to `planning/learnings/inbox.md`, triaged by
`knowledge-curator`) for the two generalizable technical takeaways.
The process takeaway, not filed as a separate learning since it is
already covered by `CLAUDE.md` §5's own letter rather than being a new
rule: **treat the DoD checklist as a running task list from the start
of implementation, not a single step performed at the end** — in a
multi-round, demonstration-heavy phase, the temptation to defer
"paperwork" until the code is proven is real and this phase gave in to
it once.

## Process-improvement feedback

The agent-led workflow itself worked as designed here: the independent
`release-phase-auditor` dispatch caught exactly the kind of omission a
self-review would plausibly have missed (an implementer is the worst-
positioned party to notice "the demonstrator's own bookkeeping wasn't
updated," having just spent the whole session on the demonstrator
itself). No tool or agent-boundary friction otherwise.

## Candidate learnings filed

`L-118`, `L-119` — both filed to `planning/learnings/inbox.md`, this
phase, 2026-11-04; triaged by `knowledge-curator` (see that file's own
curation notes for each).

## Where we're going

Stage 87B (schema-governed `README.md`/`docs/getting-started.md`, a
narrow execution harness reusing `verify_cleanroom_isolation.py`'s own
technique, real multi-section manual maintenance, a clean-environment
onboarding exercise) and Stage 87C (the complete minimum publication
suite, deterministic CLI-reference generation, the matched-baseline
quality comparison, final closeout) are both planned (plan's own §E/§F)
but require their own separate, explicit authorisation before any
further implementation — this session's own governing task authorised
Stage 87A only. Phase 87 overall remains `not done`.

## Time / cost note

One extended session, entirely within this same conversation. Three
real, billed clean-room model-inference calls (one per demonstration
round) plus six real `general-purpose` review dispatches. The real
demonstration's own iteration cost (three rounds before a passing
draft) is itself a data point worth carrying into Stage 87C's eventual
generation-cost comparison, though not a formal measurement under
matched conditions (that discipline is 87C's own, not retrofitted here).
