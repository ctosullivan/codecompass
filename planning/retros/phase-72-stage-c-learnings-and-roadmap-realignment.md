# Phase 72 retro — Ledgerkit Stage C learnings capture + post-v1 roadmap realignment

- **Date:** 2026-09-27.
- **Commit(s):** `933579c` (plan + ROADMAP row), `b014068` (the four
  new/changed planning documents), `c0c0d15` (fork-review fix, Phase 20
  design-doc citation), `336b4cd` (domain-corpus freshness
  reconciliation — incomplete, see "What didn't work"), `0cbad62`
  (retro + `knowledge-curator` triage), `2066a49` (closeout), `f2f7cbf`
  (persists the drift audit's own report, redone from scratch — finds
  `336b4cd` incomplete), `5d6a37d` (fixes the 3 sibling instances +
  1 stale citation the redone audit found), `71f5949` (CONTEXT/
  CHANGELOG updated for the follow-on fix).
- **Agents used:** `context-health-planner` (stage-boundary adequacy
  assessment), a fork (independent citation/consistency review),
  `docs-reconstructor` (per-phase drift audit, **dispatched twice** —
  see below), `domain-skeptic` (freshness reconciliation, **dispatched
  twice**), `context-researcher` (Claim revision), `knowledge-curator`
  (learning triage), `release-phase-auditor` (DoD audit, **dispatched
  twice** — first pass FAIL, second pass PASS WITH NON-BLOCKING
  OBSERVATIONS).

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

Two real misfires, both eventually caught by the next independent check
in the sequence rather than by the acting agent itself:

- **The drift audit's own standalone report was never written to disk
  the first time.** `docs-reconstructor`'s per-phase drift audit ran
  during the phase and its finding (a "Stage E" citation-staleness
  cluster) was correctly routed to `domain-skeptic` and fixed — but the
  audit's own `planning/retros/_drift-audit-phase-NN.md` file, required
  by every phase from 45 through 71, was never actually written. This
  was caught only by `release-phase-auditor`'s own independent DoD
  audit (first pass: **FAIL**, the only blocking finding), not by any
  step in the phase's own execution.
- **The first domain-corpus remediation (`336b4cd`) was itself
  incomplete.** Fixing the drift audit's own missing-report gap required
  redoing the audit from scratch, which then found the original fix had
  missed three sibling instances of the identical retired-terminology
  pattern (`decision.md` x2, `observation.md`) plus a stale Claim
  citation (`evidence.md`) — all in files the first fix commit was
  already editing for the same underlying issue, or files sharing the
  same collision material. A second `domain-skeptic` dispatch confirmed
  and named the fixes; a second `release-phase-auditor` pass (PASS WITH
  NON-BLOCKING OBSERVATIONS) is what actually caught that this retro
  itself needed updating to reflect the rework, rather than the lead
  noticing unprompted.

Both misfires were real process gaps, not merely findings the process
was designed to catch — the independent-audit discipline this project
already runs (`CLAUDE.md` §5, `release-phase-auditor` never trusting a
report) is exactly what caught both, working as intended even though
the individual steps it caught did not.

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
own independent assessment of whether this is worth a filed learning
(landed as `L-051`, though scoped narrower — citation-form fragility,
not the Claim-supersession mechanism itself).

**A fix commit closing a drift-audit finding needs its own completeness
check against every sibling instance of the identical pattern, not just
the specific locations first named.** `336b4cd` fixed exactly the four
locations `domain-skeptic`'s first report named, but neither
`domain-skeptic` nor the lead grepped the wider corpus for other
occurrences of the same retired term before considering the finding
closed — `docs-reconstructor`'s redone audit found three more in files
`336b4cd` was already touching. This is a narrower instance of the same
shape `L-051` already generalises (a retired label is fragile wherever
it appears, not only where it was first noticed) — no separate learning
filed for it here, cross-referenced instead.

**A `docs-reconstructor` (or any milestone/per-phase report-writing
role) dispatch prompt should say explicitly "write your report to
`planning/retros/_drift-audit-phase-N.md`," not assume the role's own
definition alone guarantees the file gets written.** This phase's first
dispatch produced a real, substantive verbal finding but no persisted
file — the role's own agent definition states the output path, but
nothing in the dispatch prompt or this project's own workflow step
explicitly re-states that requirement at dispatch time. Left for
`knowledge-curator`'s own independent assessment.

## Process-improvement feedback

None beyond the lesson above.

## Candidate learnings filed

None directly by the lead at first-draft time — the Claim-supersession
lesson (landed as `L-051`) was described but deliberately left for
`knowledge-curator`'s own independent triage. The two "What didn't
work" misfires above (the unpersisted drift-audit report; a fix commit
needing a completeness check against sibling instances) surfaced only
after `knowledge-curator`'s own triage pass had already run — a
second, follow-on triage decision is `knowledge-curator`'s own call,
not pre-decided here.

## Where we're going

No phase is yet planned for any of Priority A-F. Priority A (task-context
completeness) is the recommended first pick — `context-health-planner`'s
own stage-boundary assessment independently confirms `CG-001` as its
founding, still-uncorroborated evidence — but needs its own fresh
`planning/phase-N-*.md` scoping pass (`CLAUDE.md` §1) when picked up,
not a resumption of old Phase 48's scope unchanged.

## Time / cost note

Nine agent dispatches total: `context-health-planner`, a fork review,
`docs-reconstructor` (drift audit, twice — the first produced no
persisted file), `domain-skeptic` (freshness check, twice),
`context-researcher` (Claim revision), `knowledge-curator` (learning
triage), `release-phase-auditor` (DoD audit, twice — first pass FAIL).
No `src/codecompass/` change; planning-documents-only phase throughout.
The rework roughly doubled this phase's own agent-dispatch cost relative
to Phase 71's comparable five — a real cost of the two misfires above,
not free.
