# Phase 45 retro — Register Ledgerkit + baseline evaluation

- **Date:** 2026-09-13
- **Commit(s):** `b0717ee` (`feat(phase-45)`)
- **Agents used:** `context-evaluator` (baseline report),
  `context-health-planner` (first genuine solo run), `docs-maintainer`
  (reconcile), `docs-reconstructor` (drift audit), `knowledge-curator`
  (triage), `release-phase-auditor` (final pass)

## Where we are

Stage B's first real reference-project phase (Phase 44 built the
templates; this phase is their first genuine use). This is
**CodeCompass's first-ever external reference-project datapoint** — every
prior phase evaluated CodeCompass against itself. Everything from here on
in Stage B is measured against real evidence, not the desk assessment
`ledgerkit-plan.md` was written from.

## Goal

Clone Ledgerkit at a pinned commit into a scratch location, run
CodeCompass against it as-is, record exactly what it discovers,
`context-evaluator` baseline report for 2–3 representative questions,
`context-health-planner`'s first genuine solo run, register the result,
write Phase 46's plan.

## Scope delivered vs planned

Delivered as planned, with one significant correction the plan itself
anticipated: `ledgerkit-plan.md` and this phase's own plan file assumed
Ledgerkit's "Milestone 5 — CLI Filter Flags" was the live next task. On
cloning the pinned commit, Ledgerkit had undergone its own **"Core
redefinition" the same day** (2026-09-12) — Milestone 5 is now
`[SUPERSEDED]`, folded into a new Stage C; Ledgerkit's own roadmap moved
to a Stage A–I model, with Stage A (agent roster + CodeCompass
integration + compatibility harness) just closed. This is exactly the
kind of live-repo movement Phase 45's own "Design decisions" section
predicted ("the registration record's inspection findings supersede the
desk assessment wherever the live clone disagrees") — the plan worked as
designed, not despite itself.

A second, unplanned discovery: Ledgerkit has already independently
adopted CodeCompass's own Phase 43e adoption blueprint — a live
`.claude/agents/context-curator.md` role and `validation/codecompass/`
findings-intake mechanism exist, structurally matching
`codecompass-feedback-ingestion.md` almost exactly, with zero findings
filed yet. This is real, positive validation of the blueprint's
usability by an actual adopting project, discovered as a side effect of
registration rather than sought out.

## What was achieved

- `planning/reference-projects/ledgerkit.md` — full registration record
  with corrected live inspection findings.
- `planning/reference-projects/ledgerkit/00-baseline.md` — three baseline
  questions evaluated. **Q2 is the redefined-v1 effort's first FAIL
  verdict**: CodeCompass returned a confident "not found" for
  `dev-docs/hledger-compatibility.md` — a real, current, 238-line file
  that is precisely Ledgerkit's own designated hledger-1.52-compatibility
  governance document — rather than an honest empty result. Q1
  (dependencies) and Q3 (roadmap state) both PASS WITH GAPS / LOW
  advantage, both honest expected-thin results.
- Root cause confirmed and filed as **CG-002**: `spec_docs.py::_DEFAULT_GLOBS`
  has no `dev-docs/**/*.md` entry — the identical category of fix as
  Phase 37's `ai-docs/` glob addition, this time surfaced by an *external*
  reference project.
- Two further, distinct product-quality findings filed as candidate
  learnings: **L-015** (no CLI-level signal that optional-dependencies
  exist but are unscanned) and **L-016** (`query relations`'s "not found"
  error is indistinguishable from a genuine typo, giving no signal to
  suspect a coverage gap — a symptom-layer issue distinct from CG-002's
  root cause, and one that will recur for the *next* unanticipated
  doc-directory convention even after CG-002 itself is fixed).
- `context-health-planner`'s first genuine solo run (`planning/context-health.md`):
  predicted LOW context-advantage for Phase 46, since Stage B's actual
  task material lives in `dev-docs/` — CG-002's territory exactly.
- `planning/phase-46-ledgerkit-tasks.md` written, explicitly hedged since
  Ledgerkit's own Stage B isn't yet scoped/approved — names a concrete,
  already-genuine candidate (the compat-register migration follow-up)
  but requires live reconfirmation at Phase 46's own start.

## What worked

- **Treating the pinned-commit reconfirmation as load-bearing, not
  ceremonial** — actually re-reading `ROADMAP.md`/`CONTEXT.md` at clone
  time (rather than trusting `ledgerkit-plan.md`'s desk assessment) is
  what caught the Milestone-5-superseded change before it silently
  invalidated Phase 46's plan.
- **Distinguishing "not found" from "no relations" as materially
  different failure modes** — the `context-evaluator`'s rigor here (per
  its brief's rule 3, "incorrect/misleading outranks incomplete")
  produced the phase's most important finding. A looser evaluation might
  have logged Q2 as just another "thin result."
- **Running `context-health-planner` before the genuine task, not
  after** — its prediction (LOW advantage, CG-002 load-bearing) gives
  Phase 46 an explicit, falsifiable expectation to test against, rather
  than discovering the same thing mid-task with no baseline to compare.

## What didn't work

- No misfires this phase. The one friction point (Ledgerkit's Stage B not
  yet being scoped, so Phase 46 can't name a single fixed task) isn't a
  process failure — it's an accurate reflection of the actual live state
  of a project under active, independent development.

## Lessons learnt

1. **A reference project's "current state" can move between planning and
   execution even within the same day** — the desk assessment and the
   live clone were both dated 2026-09-12, and they still disagreed. The
   protocol's "reconfirm live" instruction is not boilerplate caution; it
   caught a real, material change this phase.
2. **"Not found" and "no relations" must stay distinguishable failure
   modes in both the tool's own behaviour and in how an evaluator reports
   on it** — collapsing them (as CodeCompass's CLI currently does, L-016)
   makes a real coverage gap indistinguishable from a typo, at exactly
   the moment an agent most needs the distinction.
3. **A blueprint's real-world adoption is best discovered, not sought** —
   Ledgerkit's independent adoption of `adoption-blueprint.md` surfaced
   naturally while reading its repo for an unrelated reason (its Stage A
   closeout note); this is stronger validation than the adopting project
   announcing it to CodeCompass directly would have been.

## Process-improvement feedback

None this phase — the amended step 10/14 split (L-013, Phase 44) worked
exactly as intended: `CONTEXT.md`/`CHANGELOG.md` stayed unreconciled
through this retro, triage, and audit, with the final `roadmap-context-curator`
dispatch coming only after all three complete.

## Candidate learnings filed

- **CG-002** — `dev-docs/**/*.md` invisible to spec-doc detection
  (`planning/context-gaps/inbox.md`).
- **L-015** — no CLI signal for unscanned optional-dependencies.
- **L-016** — "not found" conflates coverage gap with typo.

## Where we're going

- **Next: Phase 46** — the genuine-task procedure, with the task
  reconfirmed live at that phase's own start (Milestone-5 lesson applied
  forward). No gate blocks it, but Ledgerkit's own Stage B scoping status
  should be re-checked before committing to a specific task.
- **Trajectory: confirmed, with real evidence now attached.** Stage B's
  premise — that Ledgerkit's real technical dependencies are almost
  entirely non-package — is no longer a hypothesis from a desk
  assessment; it's demonstrated by a genuine FAIL verdict. This directly
  feeds GATE DB (Phase 47) with its first real datapoint.

## Time / cost note

Single session, continuing directly from Phase 44 (same day). No AI
enrichment spend against the Ledgerkit clone (mechanical-only `codecompass
--budget 0`, matching the honest near-zero-cost expectation for a
0-dependency project). No `src/codecompass/` change, no test change (full
suite re-verified: 554 passed / 2 skipped, `ruff` clean).
