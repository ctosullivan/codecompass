# CodeCompass v2 — evaluation strategy and baseline methodology (Phase 90)

Direct user request, 2026-10-21, part of the v2 strategic realignment
(`decisions/0078`, `planning/v2-roadmap.md`). Defines the comparative-
trial measurement method **before** any benchmark runs, per the
governing prompt's own explicit instruction to avoid speculative
numerical targets without baseline evidence. This document is
methodology only — the trial phase itself is not yet phase-planned, and
no trial has run under this methodology. **Renumbered twice, same day,
2026-10-23**: first from Phase 86 to Phase 89 by `decisions/0084` (four
new phases inserted ahead of it), then from Phase 89 to Phase 90 by
`decisions/0085` (the merged MCP/reconciliation phase split into two,
shifting every phase after it by one) — its own content, arms, and
metrics are otherwise unchanged except for the two dated amendments at
the end of this file.

## Why this exists as its own document

`context-quality-evaluation.md` already established this project's core
evaluation discipline — "advantage over the default pathway," not graph
size or edge count — and it remains primary. Phase 90 is a materially
larger exercise than any prior reference-project evaluation (three arms,
not one treatment-vs-baseline pair; the central test of this ADR's own
governing hypothesis), so its own pre-registration deserves a dedicated
record rather than a subsection of the roadmap file, mirroring how
Phase 78's own trial design got a dedicated amendment log before it ran.

## The three arms

| Arm | Description |
|---|---|
| **A — Conventional** | Existing repository access, standard development tools and tests. No CodeCompass involvement at all. |
| **B — Knowledge-assisted** | Same model, plus reconciled project knowledge, the consolidated knowledge API, generated documentation, MCP, and reconciled task context packets (Phases 82, 84, 87, 88, 89 — renumbered 2026-10-23 twice, first from 82/84/85 by `decisions/0084`, then 88 split into 88/89 by `decisions/0085`; content unchanged, "knowledge-assisted" still means no independent oracle/assurance layer) — no independent oracle/assurance layer. |
| **C — Assurance-assisted** | Same model, plus B's knowledge/MCP, plus semantic impact analysis and independently enforced verification (Phase 83's oracle — unchanged). |

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
11. Subsequent knowledge reuse across the full task sequence (Phase 89's
    own "a later task benefits from an earlier one" evidence — this
    reconciliation capability was the former Phase 85, merged into the
    old Phase 88 by `decisions/0084`, then split back out as its own
    independently-deliverable Phase 89 by `decisions/0085` §3 — measured
    here at trial scale, generalised from "a second task" to the
    complete successive-task sequence per the second amendment below).

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

Phase 90's exit gate requires a reproducible report establishing whether
CodeCompass improves verified development outcomes **after accounting
for total overhead** (metrics 6-10 above are not footnotes — they are
netted against metrics 1-5's apparent gains before any conclusion is
drawn). A neutral or negative result is reported in the same report
structure as a positive one, with the same prominence, per the governing
prompt's explicit instruction that such results "must be reported, not
concealed."

## Amendment (2026-10-23, `decisions/0084`): documentation quality and a concise-instructions baseline

Part of the v2 strategic realignment around Knowledge-Driven Software
Development. Two items the realignment's own governing prompt names
explicitly, not present in this document's original metric list, are
added here — the existing three-arm design, held-comparable conditions,
and pre-registration discipline above are otherwise unchanged.

**New metric — documentation quality and maintenance overhead.**
Distinct from the existing "knowledge maintenance overhead" metric
above (which already covers the time spent keeping reconciled knowledge
current): this metric covers the generated-documentation surface Phase
87 (Documentation Schema and Knowledge-Compiled Documentation) adds.
Reported for Arms B and C, which both have CodeCompass-generated
documentation to maintain. **Arm A's own treatment of this metric is
corrected by the second amendment below** — it is not excluded from
documentation-quality measurement. Measured the same way Phase 87's own
exit gate measures it — human correction required relative to a
baseline, factual-grounding/structural validation pass/fail, and
editorial-quality assessment — never a bare word count or page count.

**New comparison point — concise-repository-instructions baseline.**
Reported alongside, not folded into, the existing three arms: the same
task attempted using only a short, hand-written instructions file (no
CodeCompass knowledge, contracts, API, or MCP surface at all) —
isolating whether CodeCompass's structured machinery earns its overhead
over the cheapest plausible alternative, not only over nothing. This is
a comparison point with the same metric set as the primary arms, not a
fourth primary arm with independent release implications. **Its
"optional" framing is corrected by the second amendment below** — it
carries the same "never a v2 release dependency" framing already
established above for the optional source-blind research arm, but is no
longer optional for the principal net-efficiency conclusion itself. The
same honesty standard applies either way: a result favouring the
concise-instructions baseline is reported with the same prominence as
one favouring CodeCompass.

## Amendment 2 (2026-10-23, `decisions/0085`): Arm A included in documentation measurement, the concise-instructions baseline made mandatory, cumulative benefit measured across a task sequence

Part of the same-day corrective amendment to the v2 roadmap
("CodeCompass Orchestrator — Corrective Amendment to v2 Knowledge-Driven
Development Roadmap"). Three corrections to Amendment 1 above and to
this document's own original design — the existing three-arm design,
held-comparable conditions, and pre-registration discipline remain
otherwise unchanged.

**Correction — Arm A is included in documentation-quality measurement,
not excluded.** Amendment 1's own "not reported for Arm A, which has
none" is withdrawn: Arm A's *absence* of CodeCompass-generated
documentation is not a reason to exclude it from measurement. Arm A is
scored on the same documentation-quality/effort/maintenance-cost rubric
against whatever documentation outcome it actually produces, including a
scored "produced none" outcome where that is genuinely what happens —
every arm receives an equivalent documentation deliverable requirement
and acceptance criteria, not a different standard for one arm.

**Correction — the concise-repository-instructions comparator is
mandatory for the principal net-efficiency evaluation.** It is run under
the same task, resource, and evaluation conditions as the three primary
arms, and **the trial's overall net-efficiency conclusion is not valid
without it**. It remains, exactly as Amendment 1 established, never a
v2 release dependency on its own — a result favouring this baseline over
CodeCompass does not block v2.0, and is reported with equal prominence.

**Correction — cumulative benefit is measured across a genuine sequence
of successive tasks, not a single task.** The trial design includes a
sequence of related development tasks (not one task) so that whether
knowledge retained from an earlier task reduces later effort can
actually be observed. For each task in the sequence, record:
independently accepted changes; regressions and rework; token/execution
costs; elapsed time; human investigation/review time; knowledge
construction/reconciliation costs; documentation generation/maintenance
costs; initial setup/integration costs (amortised across the real number
of tasks run, unchanged from the existing Metric 10 discipline); reuse
of previously accepted knowledge; and correctness/maintainability
outcomes. Metric 11 above is generalised from "a second task" to "the
full task sequence" by this same correction, not replaced.

The principal criterion remains unchanged: improved verified,
maintainable software changes per unit of total effort, after netting
overhead against apparent gains — no numerical target is set in advance
of this phase's own baseline.

## What this document does not do

It does not fix which Ledgerkit task(s) Phase 90 will use — that is
Phase 90's own planning-time decision, made against Ledgerkit's then-
current state (mirroring every prior reference-project trial's own
practice of re-verifying task availability live rather than reusing a
stale task description). It does not set a numeric target for any
metric above. It does not commit to a specific sample size (number of
tasks/runs) — Phase 90's own plan fixes that, informed by how much
genuine Ledgerkit task variety exists at the time.
