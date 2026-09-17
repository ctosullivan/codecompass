# Phase 54b retro — LedgerKit behavioural-understanding experiment

- **Date:** 2026-09-18
- **Commit(s):** (this phase's own closeout commit, see `planning/CONTEXT.md`)
- **Agents used:** two independent `general-purpose` dispatches (baseline,
  treatment — deliberately not `context-evaluator`/`reference-project-tester`
  roles, since these needed to be genuinely fresh agents under test, not
  evaluators), `context-evaluator` (independent ground-truth verification
  and rating of both runs), `reference-project-tester` (friction filing),
  `knowledge-curator` (triage).

## Where we are

Phase 54b existed as a claimed-but-undetailed bridge phase (`decisions/0056`,
2026-09-17). This phase expanded it into a concrete, run experiment,
prompted by Ledgerkit's own real Stage C Phase 5 (`c6168b2`) landing a
materially richer evidence case than the placeholder assumed.

## Goal

Test whether CodeCompass's document/reference layer helps an agent
reconstruct execution-path-complete behavioural understanding of a real,
multi-entry-point hledger behaviour (`depth:`/`--depth` across five
commands), and specifically whether it helps avoid a real, dated
premature-conclusion mistake Ledgerkit's own Stage C Phase 1 made
(classifying `depth:` from one function's signature without tracing any
command's actual consumption of it).

## Scope delivered vs planned

Delivered exactly as scoped in
`planning/phase-54b-ledgerkit-behavioural-understanding-experiment.md`:
extended Phase 54's ingestion pipeline with 11 new selections (manual
sections, the `matchesAccount` predicate, all six real command-consumer
files); a scratch Ledgerkit copy pinned at its real current `HEAD`
(`c6168b2`); two fresh-dispatched agent runs (baseline, treatment) on
the identical real task; independent `context-evaluator` rating using
the standard instrument plus the plan's own new execution-path-
completeness criterion; every real friction point filed via the
existing context-gap/context-observation queues. No new ontology, claim
system, or execution graph — confirmed, not just asserted (`CG-007` was
filed as a candidate for GATE DD, not built).

One real deviation from the plan's own draft process, caught and fixed
before it could matter (see "What didn't work" below), not disclosed
after the fact as a limitation discovered too late.

## What was achieved

1. **A real, extended ingestion set** (11 new selections in
   `references.toml`, all line ranges independently reconfirmed live
   against the pinned hledger source before use, not copied from a
   citation) — 13 passing pipeline tests, updated for the new count.
2. **A genuine, non-contaminated two-run comparison**: both baseline and
   treatment were fresh `general-purpose` dispatches with zero memory of
   this phase's own planning conversation (the lead, having read
   Ledgerkit's Stage C Phase 5 material to write the plan, could not
   have been the agent under test without invalidating the result).
   Both independently reached the fully correct, complete answer (three
   distinct behaviours: clip/aggregate for `balance`/`register`/
   `accounts`; genuine partial exclusion for `stats`; total inertness
   for `print`).
3. **Independent, ground-truth-verified evaluation**
   (`planning/reference-projects/ledgerkit/02-depth-behavioural-reconstruction-evaluation.md`):
   baseline PASS, treatment PASS WITH GAPS, context advantage **LOW** —
   the curated `dev-docs/hledger-reference/` set omitted `Stats.hs`
   entirely, forcing a disclosed fallback exactly where the task's one
   genuine exception lived; the baseline never hit this gap, since it
   worked from the full raw source with no curation step in between.
   Mechanical `query relations` returned **zero** edges for all 19
   indexed files — independently reconfirmed via direct graph
   inspection, a second data point for the same structural ceiling
   `CG-006`/`OBS-008` already recorded, now with `CG-004`'s fix already
   live (populated names still didn't produce relations, since nothing
   else mentions these newly-minted labels by name).
4. **Both runs rated `complete`** on the new execution-path-completeness
   criterion — neither reproduced Stage C Phase 1's real historical
   mistake. A genuinely negative result for the specific failure mode
   this phase was designed to catch, reported honestly rather than
   reframed.
5. **Three new findings filed**: `CG-007` (symbol-level cross-references
   between pinned reference-doc excerpts have no representable relation
   kind), `OBS-013` (confirms the empty `query relations` result is
   mechanically correct, not a bug), `OBS-014` (confirms the `Stats.hs`
   gap is a curation-completeness problem, not a detection defect).

## What worked

- **Deliberately not using the lead as the agent under test.** The lead
  had unavoidably absorbed the correct answer while reading Ledgerkit's
  own Stage C Phase 5 material to write this phase's plan; running
  either the baseline or treatment condition personally would have made
  the result meaningless. Two genuinely fresh dispatches, with no shared
  context, kept the comparison real.
- **Reusing an already-answered, independently-verified question as a
  controlled re-creation** (the plan's own disclosed methodological
  choice, §3): letting `context-evaluator` grade both runs against
  actual, checkable fact, rather than the lead's own judgement of what
  "good" context would have looked like — a stronger evaluation bar than
  Phase 54's own `tag:` task had.
- **Giving the treatment condition an honest, disclosed fallback path**
  (raw clone + manual, if the indexed material proved insufficient)
  rather than an artificial hard restriction — this is exactly what
  surfaced the `Stats.hs` gap as a real, reportable finding instead of
  either papering over it or producing an artificially failed run.

## What didn't work

The plan's own draft extraction step, before either agent was
dispatched, put analytical conclusions directly into the fields
`reference_pipeline.py`'s `render_extracted_markdown` renders into the
agent-visible output — a label reading `"depth-trap-matchesaccount"` and
a `note` beginning `"THE TRAP: ... is the exact evidence Ledgerkit's own
Stage C Phase 1 read before wrongly classifying depth: ..."`, and
similarly for a `"THE EXCEPTION"` label/note. Had this shipped to the
treatment agent, the entire comparison would have been silently
worthless: the treatment condition would have been handed the
conclusion outright, indistinguishable in the resulting report from a
genuinely-reasoned finding, since the report's own prose would have read
identically either way. Caught by rereading `render_extracted_markdown`/
`write_extracted_markdown` to check exactly which fields get rendered
into the extracted file's visible body versus which stay in
`references.toml`'s own (never-rendered) comments — before dispatching
either agent, not after. Every label/note was rewritten to strictly
neutral file/function identification before either run started.

## Lessons learnt

When building any evaluation material a to-be-tested agent will read,
verifying "what will the agent actually see" means reading the real
rendering/output code path directly — not just the authoring interface
(`references.toml`'s own comments, which are never rendered, felt safe
to write analytically in) and not just trusting that a field named
`note` is "just a note." The two are easy to conflate when the same
tool has both an author-facing surface (TOML comments) and a
reader-facing surface (rendered Markdown) built from adjacent-looking
fields. This generalises beyond this one pipeline: any tool that
renders structured input into content a test subject will read has
exactly this risk, and the check is cheap (reread the render function
once) relative to the cost of a silently-invalidated result.

## Process-improvement feedback

The independence discipline this project already applies to *evaluation*
roles (`context-evaluator` never trusts the implementing session's own
report) needed, this phase, to be applied one level earlier — to
*who runs the task being evaluated at all*, not just who grades it. That
principle isn't new (Phase 54 already used fresh baseline/treatment
framing), but this phase is the first time the lead's own prior-session
knowledge of the correct answer was concrete and specific enough that
running either condition personally would have been a real, not
theoretical, contamination risk — worth naming explicitly for any future
phase that reuses an already-answered question as its test case (per
this phase's own disclosed §3 methodology): if the lead had to research
the answer to write the plan, the lead cannot also be an arm of the
experiment.

## Candidate learnings filed

- `planning/context-gaps/inbox.md` — `CG-007`.
- `planning/context-observations/inbox.md` — `OBS-013`, `OBS-014`.
- `planning/learnings/` — see `knowledge-curator`'s own triage for
  whether the "What didn't work" rendering-path lesson above meets the
  bar for a filed `L-NNN` candidate (my own judgement, subject to that
  triage: it likely does, since it is a concrete, generalisable process
  risk, not a one-off implementation slip specific to this pipeline).

## Where we're going

GATE DD (Phase 55's own gate) remains open, now with one more evidence
point: the document/reference layer's real failure mode here was
curation-completeness, not detection or relation — which sharpens,
without yet satisfying, the ≥2-occurrence promotion bar for `CG-007`.
Phase 60 (minimal Haskell adapter) carries forward a named, open design
question (does mechanical call-site/usage detection catch what
hand-curation missed here); Phase 61 (hledger cross-language experiment)
now has this phase's own LOW-advantage, gap-disclosed result as its
baseline for "how much better does real structural information do."

## Time / cost note

Six dispatches across this phase: two independent baseline/treatment
runs (~294s/~336s wall time, 35/39 tool uses respectively — a modest,
not dramatic, efficiency difference, consistent with the LOW-advantage
verdict), one `context-evaluator` pass (~433s, 41 tool uses, re-deriving
ground truth from scratch rather than trusting either report),
one `reference-project-tester` pass (~446s, 36 tool uses, including
direct sqlite3 verification of the empty-relations claim), one
`knowledge-curator` triage. The rendering-path check that caught the
label/note leak (a single reread of two functions) took under a minute
and prevented the entire experiment from producing a worthless result —
by a wide margin the highest-value few minutes of the phase.
