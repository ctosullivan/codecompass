# Phase 89 Stage 89C — Task B controlled comparison

Executed under governing dispatch "CodeCompass Orchestrator — Final
Stage 89C Corrections, Verification and Implementation," against the
plan at `planning/phase-89-stage-89c-task-b-controlled-comparison.md`
(commit `b0b2ef8`, independently reviewed **READY WITH NON-BLOCKING
OBSERVATIONS** across three amendment rounds — full history in
`planning/retros/_review-phase89-stage89c-plan.md`). This report is the
plan's own §9 schema, filled in with the real trial's actual results —
not a projection or a dry run.

## Setup

- **Ledgerkit pinned commit**: `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`
  — confirmed, by three independent checks (the mechanical-setup fork,
  the independent `context-evaluator`, and the `release-phase-auditor`),
  to be the SHA every clone in this trial actually used; the real
  `~/projects/ledgerkit` checkout's own current `HEAD` was separately
  confirmed to equal this same SHA throughout, with no drift and no
  silent substitution.
- **CodeCompass commit**: `b0b2ef8` (HEAD at the time this trial ran).
- **Control/treatment clone paths** (scratch, disposable, deleted after
  this report and its sibling artifacts were persisted):
  `<scratch>/stage89c-exec/ledgerkit-control`,
  `<scratch>/stage89c-exec/ledgerkit-treatment`. Pre-dispatch equivalence
  confirmed (`diff -rq`, excluding `.git`, empty; both `HEAD` match the
  pin; no CodeCompass-generated artifact in either).
- **Packet-equivalence check result**:
  [`08-stage-89c-fixture-equivalence.md`](08-stage-89c-fixture-equivalence.md)
  — the mechanical `diff <(jq -S .) <(jq -S .)` between
  `control-packet.json`/`treatment-packet.json` showed **exactly** the
  three allowed differences the plan's §5.4 names (the one new
  `EV-BALANCEFROMS-004` Evidence item; `CL-BFS-004`'s own
  `knowledge_revision` hash; `CL-BFS-004`'s own `reasons` text changing
  "3 required scope(s)…" → "2 required scope(s)…") and nothing else —
  independently re-derived three times (by the setup fork, the
  evaluator, and the auditor), all three agreeing.

## Three separate outcomes (never conflated, per plan §2 invariant 5)

### Outcome 1 — Technical implementation completed

**Yes, for both arms.** Both arms produced a buildable, runnable
`ReportSpec.with_combined_section` implementation in
`ledgerkit/models.py`, each confirmed by direct, independent
re-inspection (the verification fork and the auditor both read each
arm's actual code). Full regression-suite results (seed baseline **935
passed**; control **957 passed**; treatment **958 passed**; zero
failures in either) — no regression introduced by either arm. Real
Ledgerkit checkout and real CodeCompass canonical knowledge confirmed
untouched throughout (`git status --short` clean on both, before and
after).

### Outcome 2 — Controlled evaluation validly executed

**PASS WITH NON-BLOCKING OBSERVATIONS** (`release-phase-auditor`
verdict, [`08-stage-89c-procedural-audit.md`](08-stage-89c-procedural-audit.md)).
The auditor independently re-derived nearly every mechanical claim in
this report from raw artifacts rather than trusting prior self-reports,
and found one genuine, honestly-reported procedural-fidelity finding:

- **A real allocation-blinding leak occurred and is reported here, not
  excused**: the blinded-materials preparation step's own redaction
  sweep (plan §8 item 2) correctly redacted the literal strings
  `ledgerkit-control`/`ledgerkit-treatment` wherever they appeared in
  structured files, but missed the related, longer strings
  `ledgerkit-verify-control`/`ledgerkit-verify-treatment` inside raw,
  unstructured oracle-subprocess `.txt` transcripts specifically. This
  is a stage-one-caliber hit under plan §8 item 6's own check (a known,
  literal allocation-bearing clone name, not a contextual judgment
  call) — independently confirmed real by direct grep, first by the
  context-evaluator (who disclosed it unprompted) and again,
  independently, by the auditor. **Materiality**: this did not taint
  this run's own Outcome 3, because the actual result is a tie on every
  single signal (acceptance test, evaluator verdict, evaluator rating —
  see Outcome 3 below), so there was no asymmetric result for a leak to
  have produced, and the evaluator's own full reasoning chain was
  independently confirmed (by the auditor, reading the evaluator's
  reasoning end to end) to be traceable entirely to genuine, verifiable
  content differences, never to allocation knowledge. Filed as
  candidate learning `L-139` (triage pending/complete — see
  `planning/learnings/inbox.md`) so a future trial's own redaction
  sweep checks every file type/location a sensitive string could
  appear in, not only the ones a prior sweep happened to check.
- Every other procedural-fidelity check the auditor ran — exact dispatch
  prompt equivalence (byte-diffed, differing only in clone path and
  packet content); the pinned SHA never substituted anywhere; the
  packet diff matching the allowlist exactly; `EV-BALANCEFROMS-004`'s
  own `OracleResult` genuinely PASS, not fabricated; both clones
  starting equivalent; no other cross-arm leakage; no real-repository
  writes; no "GATE MET" claim anywhere — **confirmed sound**.

### Outcome 3 — Positive comparative advantage demonstrated or not

Applying plan §2 invariant 5 / the pre-registration's own success
criterion mechanically:

- **(i) acceptance-test divergence?** **No.** Both arms: 11/11 PASS on
  the pinned acceptance suite; primary-scope `OracleResult` genuinely
  `PASS` for both (control run `20261120T160729910366Z-4e61a8f1`,
  treatment run `20261120T160730927778Z-6506946d`; `test_input_digest`
  identical between the two, confirming both were graded against the
  identical acceptance file; `tested_subject_digest` correctly differs,
  confirming each result is genuinely tied to that arm's own code).
- **(ii) context-evaluator verdict strictly better for treatment?**
  **No.** Both drafts: **PASS WITH GAPS**
  ([`08-stage-89c-evaluation.md`](08-stage-89c-evaluation.md)).
- **(iii) context-advantage rating strictly higher for treatment?**
  **No.** Both drafts: **LOW**.

**→ GATE NOT MET.** Per the plan's own explicit tie-handling rule
(§10), this is reported plainly as a tie, not massaged toward a
positive reading, and no tie-breaking metric was sought among the
exploratory numbers below to manufacture a different conclusion.

## Acceptance-test results

| Test | Control | Treatment |
|---|---|---|
| All 11 methods of `TestCombinedSectionAcceptance` | 11/11 PASS | 11/11 PASS |
| Primary scope `OracleResult` (`combined-section-no-double-count`) | `PASS`, run `20261120T160729910366Z-4e61a8f1` | `PASS`, run `20261120T160730927778Z-6506946d` |
| Full Ledgerkit regression suite | 957 passed, 0 failed | 958 passed, 0 failed |

Full per-test detail: [`08-stage-89c-acceptance-verification.md`](08-stage-89c-acceptance-verification.md).

## Context-evaluator verdicts

Both drafts: **PASS WITH GAPS** / context-advantage **LOW** / "would
this have misled the implementing engineer? **No**" for both. Full
reasoning, including the evaluator's own independent re-derivation of
the packet diff and its application of the `L-027` equal-raw-access
check, is in
[`08-stage-89c-evaluation.md`](08-stage-89c-evaluation.md). Key
finding, reproduced here because it is the central explanation for why
Outcome 3 came out tied: **both engineers' own task framing already
contained the correct design answer** (§3's own final sentence,
deliberately included in both dispatch prompts identically), and both
engineers independently verified the no-double-count property by
reading `balance_from_spec` directly themselves rather than relying on
either packet as an authority — so, per `L-027`, almost none of either
arm's correct conclusion can be credited to its own context packet
specifically.

Two shared, packet-quality defects were found by the evaluator,
independently re-confirmed by the auditor's own reading of the real
source, and apply equally to both drafts (not differentiators between
them, and not part of Outcome 3's own gate): (1) every item's `summary`
field is silently hard-truncated at exactly 280 characters, while the
packet's own `bounds.truncated` flag falsely reports `false` — filed as
candidate learning `L-140`; (2) `CL-BFS-004`/`EV-BFS-001`'s own
`source_revision` cites an older Ledgerkit commit than the actual pinned
one — confirmed harmless here (the cited file is byte-identical between
the two revisions) but noted as a metadata clarity gap.

## Evidence of knowledge reuse or redundant investigation

The **treatment** arm's own report explicitly names the packet's cited
Claim/Evidence (`CL-BFS-004`/`EV-BALANCEFROMS-004`) in its reasoning,
treating it as "to verify, not to trust blindly" rather than as settled
fact — it then independently re-confirmed the same conclusion via direct
source reading and its own fresh executable test. The **control** arm
(whose own pre-reconciliation packet carries no equivalent Evidence
item at all) reached the **identical** correct conclusion through
direct source reading and its own fresh executable test, with no
packet-level prompt toward it. Both arms therefore had, and used, equal
raw access to the decisive fact (`L-027`) — the treatment arm's packet
was not redundant with its own independent investigation, but neither
was it decisive: the control arm's investigation, run without that
Evidence item at all, reached the same correct place by the same route.

## Independent procedural audit verdict

**PASS WITH NON-BLOCKING OBSERVATIONS** —
[`08-stage-89c-procedural-audit.md`](08-stage-89c-procedural-audit.md),
summarised in Outcome 2 above.

## Exploratory cost/usefulness metrics

(Clearly separated per plan §9/dispatch §10 — never used to adjust
Outcome 3 above.)

| Dispatch | Model tokens | Tool calls | Wall-clock |
|---|---|---|---|
| Control development arm | 88,370 | 27 | ~4.1 min |
| Treatment development arm | 85,424 | 32 | ~4.8 min |
| Mechanical setup (clones, reconciliation, packets) | 197,389 | 22 | ~3.3 min |
| Independent verification (both arms) | 224,824 | 19 | ~3.0 min |
| Blinded-materials preparation | 247,035 | 10 | ~1.7 min |
| Context-evaluator | 131,295 | 36 | ~7.5 min |
| Release-phase-auditor | 167,870 | 47 | ~8.0 min |
| Focused plan re-review (pre-execution) | 114,751 | 13 | ~2.0 min |

- Development/test attempts: both arms ran their own tests before
  finishing (control: full suite + its own 10 new tests; treatment:
  full suite + its own 11 new tests) and reported no need for a second
  implementation attempt — both state their first implementation
  passed everything they ran.
- Human/lead review effort: **not separately instrumented**, disclosed
  as unavailable, not zero (orchestration/dispatch-composition time
  across ~8 agent dispatches and the plan amendment itself).
- Context-generation/reconciliation overhead: contained within the
  "mechanical setup" row above (one combined dispatch covering seed
  clone, equivalence check, Task A reconciliation, both packet
  generations, and the contamination check).
- Whether the treatment arm reused the packet's cited Evidence rather
  than re-deriving the same fact from scratch: **partially** — see
  "Evidence of knowledge reuse" above; it named the Evidence explicitly
  but still independently re-verified rather than trusting it outright
  (itself a reasonable, non-credulous use of supplied context, not a
  failure to use it).

## Explicit scope statement

This trial tests the benefit of STRONGER VERIFICATION of an existing,
already-asserted behavioural fact (CL-BFS-004), not the discovery of a
previously unknown one. **This run's own result is a credible negative
finding**: on this one bounded task, reconciled Evidence did not
measurably improve the development decision, because the task's own
framing and the code's own directly-readable structure already made the
correct answer equally reachable without it. This does not establish
that reconciliation is valueless in general, and does not establish
that a differently-scoped task — e.g. one where the decisive fact is
*not* independently re-derivable from a two-minute read of the source,
or where `L-027`'s equal-access condition does not hold as cleanly —
would behave the same way. Per `L-133`, it also does not mean the real
Ledgerkit repository has gained a combined-section constructor, and does
not mean the real `balance-from-spec` canonical knowledge's own
production state has changed (it has not — confirmed clean throughout).
