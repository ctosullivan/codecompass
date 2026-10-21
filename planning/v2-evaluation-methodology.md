# CodeCompass v2 — evaluation strategy and baseline methodology (Phase 86)

Direct user request, 2026-10-21, part of the v2 strategic realignment
(`decisions/0078`, `planning/v2-roadmap.md`). Defines Phase 86's
comparative-trial measurement method **before** any benchmark runs, per
the governing prompt's own explicit instruction to avoid speculative
numerical targets without baseline evidence. This document is
methodology only — Phase 86 itself is not yet phase-planned, and no
trial has run under this methodology.

## Why this exists as its own document

`context-quality-evaluation.md` already established this project's core
evaluation discipline — "advantage over the default pathway," not graph
size or edge count — and it remains primary. Phase 86 is a materially
larger exercise than any prior reference-project evaluation (three arms,
not one treatment-vs-baseline pair; the central test of this ADR's own
governing hypothesis), so its own pre-registration deserves a dedicated
record rather than a subsection of the roadmap file, mirroring how
Phase 78's own trial design got a dedicated amendment log before it ran.

## The three arms

| Arm | Description |
|---|---|
| **A — Conventional** | Existing repository access, standard development tools and tests. No CodeCompass involvement at all. |
| **B — Knowledge-assisted** | Same model, plus reconciled project knowledge, MCP, and task context packets (Phases 82, 84, 85) — no independent oracle/assurance layer. |
| **C — Assurance-assisted** | Same model, plus B's knowledge/MCP, plus semantic impact analysis and independently enforced verification (Phase 83's oracle). |

Arm B isolates the *context* contribution; Arm C isolates the additional
*assurance* contribution on top of B. This decomposition is deliberate:
a result showing B ≈ A but C > A would mean the value is in
verification, not context — a materially different, equally honest
finding from B > A, C ≈ B (value is in context, assurance adds little
further). Both outcomes, and every outcome in between, are reported.

## Held comparable across arms (the dominant named risk)

Per the governing prompt's own explicit warning, the following are held
fixed or matched as closely as practically possible, and any unavoidable
difference is disclosed in the trial report rather than silently
absorbed into the result:

- **Model**: identical model/version across all three arms.
- **Task**: the same real Ledgerkit task definition, not three
  differently-scoped tasks.
- **Baseline**: Arm A's own unaided result is the reference baseline
  every other arm is measured against, not an external industry figure.
- **Oracle**: Arm B does not get informal access to Phase 83's oracle;
  only Arm C does — the oracle is the one deliberate, named difference
  between B and C.
- **Tooling permissions**: identical file/shell/network permissions
  across arms, varying only in which CodeCompass surfaces are reachable.
- **Resource ceilings**: identical token/time/attempt budgets.

## Metrics

Per the governing prompt's own list, recorded for every arm on every
task:

1. Independently verified completion (per Phase 82/83's own oracle
   definitions of PASS, not the arm's own self-report).
2. Regressions and escaped defects (found by a check the arm itself did
   not run or control).
3. Verification gaps and false assurance (a PASS claim later shown
   incomplete).
4. First-pass success (no retry needed).
5. Attempts and escalation (how many retries, and whether a human had
   to intervene).
6. Context consumption (tokens, for the arms that use CodeCompass
   context).
7. Model and execution costs.
8. Human preparation and review time.
9. Knowledge maintenance overhead (time spent keeping reconciled
   knowledge current, charged against Arms B/C, never against Arm A).
10. Integration effort (one-time setup cost, amortised honestly across
    however many tasks the trial actually runs, not charged entirely to
    the first task).
11. Subsequent knowledge reuse (Phase 85's own "second task benefits
    from the first" evidence, measured here at trial scale).

Failures, timeouts, and incomplete work are recorded as data points, not
excluded from the result set — a trial that only reports completed runs
systematically overstates advantage.

## Independent verification of the comparison itself

Mirroring `context-evaluator`'s existing independence rule (it inspects
the target repository directly rather than trusting CodeCompass's own
self-report), whoever determines each arm's "independently verified
completion" and "regressions/escaped defects" does so by direct
inspection of the real Ledgerkit change and real test results — never by
accepting the arm's own agent's closing summary.

## Pre-registration discipline

Before any arm runs: the task is fixed, the oracle's accepted checks are
fixed and pinned (Phase 82's own tamper-detection mechanism applies
here directly), and the metrics above are the complete metric set — no
metric is added after seeing results in a direction that favours one
arm, and no metric already listed here is quietly dropped if its result
is unfavourable. Any genuinely necessary mid-trial methodology
correction is logged as a dated amendment to this file (the same
amendment-log convention `planning/phase-N-*.md` files already use),
never a silent edit.

## Optional source-blind research arm

A fourth, explicitly optional, bounded arm — the model develops against
Ledgerkit with contracts/evidence/context available but the underlying
source withheld, testing whether CodeCompass's evidence layer alone can
substitute for source access on a narrow task. This arm:

- Is never a v2 release dependency (governing prompt §4's own explicit
  instruction).
- Reuses Phase 81B's clean-room isolation mechanism to enforce the
  source-withholding boundary mechanically, not by instruction alone —
  the same "verify by active attempt, not by design intent" discipline
  Phase 81B already proved out.
- Is reported with the same honesty standard as the three primary arms:
  a negative or inconclusive result here does not reflect on Arms A/B/C.

## Reporting standard

Phase 86's exit gate requires a reproducible report establishing whether
CodeCompass improves verified development outcomes **after accounting
for total overhead** (metrics 6-10 above are not footnotes — they are
netted against metrics 1-5's apparent gains before any conclusion is
drawn). A neutral or negative result is reported in the same report
structure as a positive one, with the same prominence, per the governing
prompt's explicit instruction that such results "must be reported, not
concealed."

## What this document does not do

It does not fix which Ledgerkit task(s) Phase 86 will use — that is
Phase 86's own planning-time decision, made against Ledgerkit's then-
current state (mirroring every prior reference-project trial's own
practice of re-verifying task availability live rather than reusing a
stale task description). It does not set a numeric target for any
metric above. It does not commit to a specific sample size (number of
tasks/runs) — Phase 86's own plan fixes that, informed by how much
genuine Ledgerkit task variety exists at the time.
