# Phase 67 retro — Final validation: self-dogfood + Ledgerkit + Stage F smoke test

- **Date:** 2026-09-24
- **Commit(s):** `27fa8bf` (plan + ROADMAP row split), `5669439`
  (sub-task 1 assessment), `4bfb14d` (sub-task 1 fix), `abc1186`
  (sub-tasks 2/3), `bf5850c` (sub-task 4), `3962043` (drift audit).
- **Agents used:** `context-health-planner` (sub-task 1), a
  `general-purpose` agent (sub-task 4, the fresh-agent test),
  `docs-reconstructor` (per-phase drift audit).

## Where we are

Stage G's fourth phase, `EXPERIMENTAL (gates v1)` — the last phase
before Phase 68's independent release audit. Unlike Phases 64–66
(reconstruction/reconciliation), this phase is a validation gate: its
own verdict determines whether CodeCompass can be described as a
validated reference/model project, not whether the software itself may
ship (that's already gated by GATE DF/DD/G9, satisfied).

## Goal

A lightweight confirmation pass (not a full re-run): re-verify
CodeCompass's own dogfooding signal is current; re-confirm Ledgerkit's
and Phase 63's smoke-test numbers still hold against the code as
shipped; state plainly how many real times the development methodology
was exercised pre-v1; run a fresh-agent acceptance test once.

## Scope delivered vs planned

All four sub-tasks delivered exactly as planned, with one real,
unplanned finding acted on:

- **Sub-task 1**: found genuinely stale (`context-health.md`/
  `context-use-log.md` untouched across 21 phases, Phases 46–66). A
  fresh assessment found this checkout's own `context-graph.db` had
  regressed to the point of `ai-docs/README.md`'s own published worked
  example erroring — fixed with a full deterministic sync (no cost, no
  `src/` change), live-reverified.
- **Sub-task 2**: Ledgerkit re-confirmed live against a pin newer
  (`c6168b2`) than the original GATE DC evaluation (`05218e3`); Phase
  63's own smoke-test basis (no adapter code change, regression suite
  green) independently re-checked, not assumed. An explicit written
  justification recorded for shipping at LOW advantage (below the
  roadmap's own MODERATE+ target) — a structural ceiling (`CG-003`,
  gated by GATE DD), not a defect.
- **Sub-task 3**: the methodology exercise count reported honestly as
  one (Phase 63D), not inflated by counting Phase 60's own
  component-level reuse as a second exercise.
- **Sub-task 4**: the fresh-agent acceptance test scored 4/4 PASS, with
  one criterion carrying an honestly-disclosed platform caveat (see
  "What didn't work").

## What was achieved

A real self-dogfooding credibility gap (this repo's own stale context
graph) was found and closed before it could surface during Phase 68's
own independent audit. Ledgerkit's fix was re-verified on a genuinely
newer pin, not just re-asserted from an old report. The methodology's
own validation claim now has an honest, disclosed exercise count
instead of an implicit, untested "repeated use" assumption. The
fresh-agent test produced a real, usable design artifact
(`planning/symbol-enrichment-provenance-proposal.md`) for whoever
eventually implements `L-031`, alongside a genuine PASS/FAIL evaluation
of the reconstructed documentation's own discoverability — the first
real test of Phases 63D–66's own combined output from a truly
fresh-agent perspective.

## What worked

- **Checking "is this file actually current" before trusting it as a
  re-confirmation input**, rather than assuming `context-health.md`
  was fine because nothing had flagged it, surfaced a real, 21-phase-old
  gap immediately. The plan's own §1 named this risk explicitly in
  advance ("a real gap this phase must address, not assume away") — and
  it was real.
- **Doing the Ledgerkit re-confirmation live, on a newer pin, rather
  than re-stating the old report's numbers.** A live clone happened to
  be available in this environment; using it rather than treating the
  Phase 51 report as sufficient found genuine fresh evidence (a
  different pin, the exact same disambiguation behaviour) rather than
  circular confirmation of the same old test run.
- **Assessing the fresh-agent test's own report directly, not the
  agent's self-summary**, caught something worth naming even in a
  4/4-PASS result: the agent's own summary implied clean, unqualified
  success, but reading the actual report surfaced the CLAUDE.md
  auto-load caveat on criterion 1 — a nuance the self-summary would
  have hidden.

## What didn't work

**`context-health.md`/`context-use-log.md` had no standing trigger
keeping them current, and went 21 phases (46–66) without an update** —
found only because Phase 67's own plan happened to name them
explicitly as a re-verification input. Unlike `ROADMAP.md`/`CONTEXT.md`,
which get touched every phase by convention (and, since Phase 66,
`CONTEXT.md` is explicitly compact and current-only), nothing in
`planning/agent-led-workflow.md`'s 14 steps schedules a periodic
re-check of these two files. This let a real staleness accumulate
silently for a long stretch before anything happened to need them.

## Lessons learnt

- **A file that only gets updated "when something happens to need it"
  will drift silently for as long as nothing needs it** — the same
  underlying shape as `CONTEXT.md`'s own pre-Phase-66 append-only
  drift, but here manifesting as staleness-by-neglect rather than
  bloat-by-accretion. Worth `knowledge-curator`'s own independent
  triage on whether this needs a standing trigger (e.g. a periodic
  `context-health-planner` dispatch at a fixed phase cadence, not only
  ad hoc) rather than the lead's own unilateral judgment that "it'll
  probably come up when needed."
- **A fresh-agent acceptance test run inside Claude Code itself cannot
  cleanly isolate "did the agent discover `CLAUDE.md`" from "did the
  platform hand it `CLAUDE.md` automatically."** This is a structural
  property of testing this specific criterion on this specific
  platform, not a finding about CodeCompass's own documentation. Worth
  recording for whoever designs a repeat of this test (Phase 67 is
  meant to validate the methodology once, but `decisions/0060`'s own
  text doesn't rule out repeating it) — the other three criteria
  (locating `docs/domain/`, recognising uncertainty, producing a
  grounded design) remain clean, unconfounded signal.

## Process-improvement feedback

Consider whether `context-health-planner` should get a standing
periodic-dispatch trigger in `agent-led-workflow.md` (e.g. every N
phases, or at every stage boundary) rather than only being dispatched
when a specific later phase happens to need its own output — the same
kind of fix `L-034`/`L-038` already applied to other files that drift
silently between the moments something forces a look.

## Candidate learnings filed

None filed directly by the lead — both "What didn't work" and the
platform-caveat lesson are described above but deliberately left for
`knowledge-curator`'s own independent triage, per this project's now-
established precedent (Phase 63/64/65/66) of not trusting the retro's
own "candidate-worthy or not" judgment unchecked.

## Where we're going

Phase 68 (independent release audit) is next. No gate blocks it — Phase
67 confirmed the planned trajectory without changing it; its own verdict
(4/4 PASS on the fresh-agent test, LOW-advantage-with-justification on
Ledgerkit, an honest one-exercise methodology count) is the record
Phase 68's own audit and any future "is this a validated reference
project" claim should point to. Its own plan does not yet exist and
must be written per `CLAUDE.md` §1 before implementation begins.

## Time / cost note

Two agent dispatches (`context-health-planner`, one `general-purpose`
fresh-agent test), one live deterministic `codecompass sync` (no AI
cost — Phase B declined), one live Ledgerkit re-run, two full `pytest`
runs. No `src/codecompass/` change.
