# Phase 72 retro — Ledgerkit Stage C learnings capture + post-v1 roadmap realignment

- **Date:** 2026-09-27.
- **Commit(s):** `933579c` (plan + ROADMAP row), `b014068` (the four
  new/changed planning documents), `c0c0d15` (fork-review fix, Phase 20
  design-doc citation), `336b4cd` (domain-corpus freshness
  reconciliation).
- **Agents used:** `context-health-planner` (stage-boundary adequacy
  assessment), a fork (independent citation/consistency review),
  `docs-reconstructor` (per-phase drift audit), `domain-skeptic`
  (freshness reconciliation), `context-researcher` (Claim revision).

## Where we are

First substantial post-v1 direction-setting phase after Phase 71's
documentation refresh. Direct user request: record Ledgerkit Stage C's
real learnings as durable knowledge, then realign the post-v1 roadmap
around the highest-value capabilities they demonstrate.

## Goal

Distill 11 user-specified learnings into a durable, citation-grounded
record; use them to decide post-v1 priorities via this project's own
existing GATE DD decision procedure rather than inventing a new
prioritization mechanism; disposition every material pre-v1 roadmap
item so nothing is silently dropped; realign `planning/ROADMAP.md`
accordingly — without implementing any new roadmap capability.

## Scope delivered vs planned

Delivered exactly as planned, no scope amendments. The single largest
finding, confirmed independently at multiple points (the drafting
itself, the fork review, `context-health-planner`'s own assessment): most
of the mechanisms the 11 learnings call for **already exist, proven, as
CodeCompass's own internal development-process tooling**
(`planning/knowledge/`'s Observation/Evidence/Claim model, `context-gaps/`,
`context-evaluator`, the Scope→Plan→Domain→Design→Implement workflow)
and have simply never been offered to a downstream user of the shipped
tool. This reframed the roadmap work from "design six new capabilities"
to "productise five already-proven internal mechanisms plus one genuine
gap (execution-path modelling)" — a materially cheaper, better-evidenced
starting point than a blank-slate design exercise would have been.

## What was achieved

`planning/ledgerkit-stage-c-learnings.md` (new): 11 learnings, each
citation-grounded and classified validated-observation /
design-principle / existing-vs-proposed / open-hypothesis.
`decisions/0062` (new ADR): records the prioritisation pivot (task-
context completeness over graph completeness, Priority A-F) without
resolving GATE DD's own graph-schema questions — deliberately, since
most individual `context-gaps` candidates (`CG-001`, `CG-003`, `CG-006`,
`CG-007`) have not independently crossed this project's own recurrence
bar, and funding a schema generalisation on the qualitative narrative
alone would have repeated the premature-generalisation mistake
`conditional-generalisation.md` was written to prevent.
`planning/pre-v1-disposition.md` (new): every material pre-v1 item
(Phase 24/25/48/50, GATE DD/Stage E, retargeted phases, superseded ADRs,
open context-gaps, future-improvement backlog) given an explicit
disposition. `planning/ROADMAP.md`'s old "Deferred/not-funded" table
replaced by the Priority A-F structure with concrete success criteria
per priority.

## What worked

- **Reusing the project's own existing GATE DD decision procedure**
  (`conditional-generalisation.md` §3 — list every confirmed finding,
  name the smallest candidate, take the union) rather than inventing a
  new prioritisation framework kept this realignment grounded in
  established project discipline instead of a fresh, unvalidated
  methodology. It also produced an honest result: the union of
  *individually-evidenced* candidates is smaller than the union of
  *qualitatively-compelling* ones, and the ADR says so explicitly rather
  than smoothing over the gap.
- **The domain-corpus freshness-reconciliation mechanism caught a real,
  third independent instance** of the exact fragility `L-048` named at
  Phase 71 (a planning-document restructure elsewhere breaking a
  `docs/domain/` citation with zero domain-meaning change) — this time
  inside a *Claim record's own statement text*, not just a concept
  page's citation list, which required `context-researcher` (not
  `domain-skeptic`) to make the actual correction, exercising a
  write-boundary distinction (`domain-skeptic` finds and names; only the
  role that owns a record kind revises it) that had been designed but
  never actually tested end-to-end before this phase.
- **The independent fork review caught a real, concrete completeness
  gap** (a design document for Phase 24's own scope existed but wasn't
  cited in its disposition entry) that a second read-through by the
  lead alone had missed — the review step earned its cost again.

## What didn't work

None beyond the fork review's own single finding, already the review
step working as intended rather than a process failure.

## Lessons learnt

**A Claim/Evidence-model correction that only revises a *resolution-
mechanism reference* (not the underlying substantive claim) is still
correctly handled by the full Claim-supersedes-Claim mechanism, not a
lighter-weight edit** — confirmed real this phase (`CL-EVID-011`/
`CL-EVID-012` superseding `CL-EVID-009`/`CL-EVID-003`), the first time
this project's own contradiction/supersession machinery has been
exercised with real content at all (previously "structurally-checked
but experimentally unproven," per Phase 54c's own retro — now
partially exercised, though `context-researcher`'s own report is
careful to note this was a narrow, mechanical correction, not a genuine
substantive reversal, so the mechanism's behaviour under real
disagreement remains otherwise untested). Left for `knowledge-curator`'s
own independent assessment of whether this is worth a filed learning.

## Process-improvement feedback

None beyond the lesson above.

## Candidate learnings filed

None directly by the lead — the Claim-supersession lesson above is
described but deliberately left for `knowledge-curator`'s own
independent triage, per this project's established practice.

## Where we're going

No phase is yet planned for any of Priority A-F. Priority A (task-context
completeness) is the recommended first pick — `context-health-planner`'s
own stage-boundary assessment independently confirms `CG-001` as its
founding, still-uncorroborated evidence — but needs its own fresh
`planning/phase-N-*.md` scoping pass (`CLAUDE.md` §1) when picked up,
not a resumption of old Phase 48's scope unchanged.

## Time / cost note

Five agent dispatches: `context-health-planner`, a fork review, a
`docs-reconstructor` drift audit, `domain-skeptic` (freshness check),
`context-researcher` (Claim revision). No `src/codecompass/` change;
planning-documents-only phase throughout.
