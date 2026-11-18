# Phase 89 Stage 89A retro — Detection and Manifest Extension

## Goal

Implement, test, and independently demonstrate Stage 89A of the
approved Phase 89 plan (`planning/phase-89-incremental-knowledge-
documentation-reconciliation.md`, READY WITH NON-BLOCKING OBSERVATIONS,
six independent review rounds) per the governing dispatch ("Implement
Phase 89A with Additional Acceptance Tests"): two sibling source/test
change detectors, durable `OracleResult` persistence, run-identity
Evidence deduplication, human-approved canonical mutation, a
pre-registered Task B record, and a real, two-detector Ledgerkit
demonstration — without implementing Stage 89B/89C or marking Phase 89
`done`.

## Delivered vs. planned

All 14 named Stage 89A deliverables (dispatch §2) were implemented:
`source_reconciliation.py`'s two detectors; baseline establishment/
comparison/controlled advancement; graph-index freshness validation;
the `check_id` Requirement field plus `REQ-BFS-002.yaml` backfill;
`on_fresh_result` capture; durable `OracleResult` persistence+
integrity verification; manifest generation; run-identity Evidence
dedup; human-approved Evidence/Claim creation; cumulative `evidence_
support_state`; `detect-changes`/`verify-changes`; the Stage 89A ADR
(`decisions/0096`); Task B pre-registration.

The four additional mandatory acceptance requirements (dispatch §3)
were also delivered: (A) test-only-change detection via a new, direct
`check_id`→Claim bridge over `oracle-contract.yaml`'s own
`test_input_paths`, bypassing `classify_symbol` entirely since no
symbol is involved — this gap was real; neither the plan nor
`classify_symbol` had a path for "a test file changed, production
source didn't." (B) the durable `results/`/`results/raw/` convention,
replacing Phase 83's own disposable `scratch-assessments/` for anything
Stage 89A persists — the gap this round found was concrete: `assess()`'s
own default raw-output directory was never meant to be durable, and
nothing stopped Phase 89 from accidentally relying on it. (C) a final,
resolved `on_fresh_result` signature — `run_check_assurance` takes a
plain `Callable[[OracleResult], None]` (no second argument needed,
since `OracleResult` already carries its own `check_id`); `assess`
takes `Callable[[int, OracleResult], None]`, the `int` being the
zero-based range index — simpler than the plan's own "list per
check_id, consumed in range order" design, since `assess()`'s own loop
structure guarantees at most one result per `(range, check_id)` pair,
making a flat dict sufficient. (D) CLI execution/filesystem boundaries
— `detect-changes` (observation only, zero subprocesses/writes),
`--probe-coverage` (exactly one collection-only subprocess per
uncovered check, still zero writes), `verify-changes` (the only command
that actually executes checks and persists results), `apply` (the only
canonical-mutation entry point) — each with a dedicated regression test
proving the claimed subprocess/file-write counts, not just exit codes.

**Real Ledgerkit demonstration (dispatch §4)**: both detectors were run
end to end against disposable `cp -r ~/projects/ledgerkit` scratch
copies (the real checkout was never modified — confirmed via `git
status`/`git diff --stat` on the real repo throughout). Detector (a):
unmodified code PASSes both required checks → the real sign-inversion
mutation (removing `reports.py`'s own `if section.invert:` guard) →
`codecompass sync` → `detect_source_changes` reports the changed range
→ the existing Evidence bridge (`EV-BFS-002`/`EV-BFS-003`) → fresh
execution → genuine FAIL → persisted, round-trip-verified `OracleResult`
→ reconciliation proposal correctly naming `CL-BFS-001`/`CL-BFS-002`
(label `"regression"`) → human-approved → applied
(`evidence_support_state: conflicting`, correctly reflecting both the
earlier real support and the new real contradiction) → mutation
reversed → re-synced → re-detected → re-verified → genuine PASS →
correctly re-proposed (label `"re_confirmed"`) → applied
(`evidence_support_state` stays `conflicting` — the historical
contradiction from the regression is never silently erased, exactly
the cumulative-state guarantee this stage exists to provide). Detector
(b): the real `overlapping-account-patterns-no-double-count` check,
previously uncovered → the real test (`rows["expenses:food:groceries"]
== Decimal("150.00")`, `subtotal == Decimal("159.00")`, matching Phase
88's own already-documented body) added to a scratch copy → genuinely
collects and genuinely passes → `check_id`→`REQ-BFS-002`→`CL-BFS-004`
resolution → durable `OracleResult` persisted → proposed Evidence →
human-approved → applied → `CL-BFS-004.evidence_support_state` upgraded
from `partially_supported` to `supported`. Both negative controls (an
unrelated file edit; a file with no `source_files` row at all, e.g.
`tests/fixtures/filtered.journal`, correctly reported `stale_graph_
index`, never silently ignored) confirmed nothing proposable.

**Not run as a real Ledgerkit scratch demonstration** (covered instead
by the unit suite, using the identical real code paths against
synthetic fixtures): the previously-covered-but-stale case and the
test-only-change scenario. Named explicitly as a scoping choice, not an
oversight — time budget favoured covering every acceptance criterion at
least once with full fidelity (real code, real assertions) over
re-running every scenario against a second real checkout when the unit
tests already exercise the exact same production code paths.

**Task B pre-registration** (`planning/retros/phase-89-ledgerkit-two-
task-demonstration.md`) was written and committed *before* either
Ledgerkit demonstration ran. The plan's own deterministic `find_gaps`-
based selection rule was actually executed against the real, current,
pre-Task-A `balance-from-spec` knowledge state (17 gaps, two kinds:
`stale_test_citation`, `unverified_required_scope`) — and found,
honestly, that every one of them is a knowledge-maintenance artifact of
the same pre-existing contract-hash drift, not an independently-
motivated development task. The plan's own pre-registered fallback (a
`ReportSpec` "combined section" constructor, with its own concrete
acceptance test and benefit rationale) was selected instead, named as a
fallback rather than disguised as the primary rule's own output.

## Design decisions made beyond what was specified

1. **`_persist_and_verify`'s own round-trip check** — re-parses the
   just-written YAML and re-checks its `raw_output_ref`'s own hash,
   under a scoped `chdir`, mirroring `mcp/tools.py::_chdir`'s own
   documented rationale exactly (duplicated locally rather than
   importing from `mcp/`, since this module has no other dependency on
   it).
2. **`run_pytest_collect_only`** duplicates `run_pytest_check`'s own
   bounded-subprocess pattern (timeout, output cap, process-group kill)
   in full rather than a shared-helper extraction — the two functions
   classify outcomes on genuinely different bases (junit-xml parsing
   vs. bare return code), and the extraction risk for a timeout/
   process-group-sensitive function was judged higher than the cost of
   controlled duplication.
3. **`--establish-baselines`**, found missing while running the real
   detector-A demonstration — dispatch item 2 names "source-baseline
   establishment" as its own required deliverable, but nothing
   previously exposed a way to bootstrap a first-ever baseline entry
   for a newly-observed file. Added as an explicit, opt-in
   `detect-changes` flag, never a side effect of plain detection.
4. **The re-confirmation skip condition**, found and fixed mid-
   demonstration — `propose_reconciliation` was unconditionally
   skipping every "re_confirmed" `VERIFIED_SCOPE` finding regardless of
   the target Claim's own current `evidence_support_state`, when the
   plan's own §4.3 rule only licenses skipping an ALREADY-`supported`
   Claim. A Claim left `conflicting` by an earlier accepted regression
   still needs a reversed mutation's own fresh PASS proposed. Fixed in
   both the symbol_change and test_input_change branches, with a
   dedicated regression test.
5. **Baseline advancement for a `source_reconciliation` item is a
   separate, explicit function** (`advance_baselines_for_applied_
   item`), called by the CLI only after a confirmed successful apply —
   not wired into the generic `apply_manifest` dispatch itself, which
   has no `repo_root` in its signature. Disclosed in `decisions/0096`
   as a known interim design, not hidden.

## Lessons learnt

- **Running the real demonstration surfaced two genuine implementation
  gaps the unit-test suite, built from the same fixtures I designed,
  did not catch**: the missing `--establish-baselines` primitive and
  the re-confirmation skip-condition bug. Both were caught only because
  the real Ledgerkit scratch-copy run exercised a *sequence* of
  detect→verify→apply→reverse→detect→verify→apply across real state
  transitions that a single, isolated unit test rarely constructs on
  its own. This confirms the project's own existing practice (a real
  reference-project demonstration as part of, not instead of, the unit
  suite) is pulling its weight — a plan this heavily reviewed on paper
  still had two live bugs no amount of further *planning* review would
  have caught.
- **`codecompass sync`'s own Phase B (AI enrichment) step fails without
  an API key configured** in this environment, with a non-fatal
  `TypeError` surfaced after the graph rebuild itself has already
  completed successfully — the exit code was still 0 and
  `context-graph.db` was already correctly populated by the time the
  error printed. Not a Phase 89 defect; noted here as a minor
  friction point for a future session running the same kind of
  real-repo demonstration (the graph is usable despite the trailing
  error; no `--budget 0`/`--skip-enrichment` flag currently exists to
  suppress the attempt cleanly).
- **`tests/fixtures/filtered.journal` (a non-Python data fixture named
  in `test_input_paths`) is never indexed by `codecompass sync`'s own
  symbol-scanner**, so it is correctly, but unavoidably, always reported
  `stale_graph_index` rather than ever being comparable against a
  baseline — a real, structural limitation of reusing `source_files`
  for non-Python test-input tracking, disclosed here rather than
  silently working around it.

## Process-improvement feedback

- The plan's own `on_fresh_result`/multi-range-capture design (a list
  per `check_id`, "consumed in range order") was more complex than
  necessary; the simpler, provably-correct flat-dict-keyed-by-`(range,
  check_id)` design adopted during implementation is a case where
  resolving an implementation-contract ambiguity at build time (as this
  dispatch explicitly authorised) produced a better design than the
  planning-time version — worth keeping in mind for future stages: a
  plan's own mechanism sketch is a starting point, not a contract to
  implement literally when direct source inspection reveals a simpler,
  equally sound alternative.

## 2026-11-18 — corrective pass (`decisions/0097`)

A source-level review, independent of this retro's own original
"delivered" assessment above, found three material defects the
original `release-phase-auditor` pass's own ten-point checklist had not
been scoped to probe for: (A) `_tracked_test_input_paths`'s
single-valued mapping silently dropping all but one check sharing a
test-input path (live against the real `balance-from-spec` contract,
which already has two such checks); (B) `_apply_source_reconciliation`
never re-validating a cited result against live oracle/checkout state
at the apply-time write boundary, trusting the manifest's own cached
`target_field` verbatim; (C) a crash-after-Claim-write-before-state-
persisted retry failing as a false concurrent-edit conflict. All three
were confirmed against real source/data before any fix was written,
fixed, covered by 24 new tests, and re-demonstrated live against fresh
Ledgerkit scratch copies (`planning/retros/phase-89-stage-89a-
corrective-ledgerkit-demonstration.md`) — see `CHANGELOG.md` and
`decisions/0097` for the full account.

**This retro's own §"Limitations and non-goals" above is corrected on
one point, not merely superseded**: the bullet stating `tests/fixtures/
filtered.journal` is "correctly, but unavoidably, always reported
`stale_graph_index`" was accurate when written but is **no longer
true** — the corrective pass's bounded check 1 resolves exactly this,
tracking a non-Python oracle input directly by content hash instead.
Left unedited above (this project's retros are append-only, like its
ADRs and audit logs) so a future reader sees the original, honest
assessment at the time it was written; this note is the correction.
The `codecompass sync` AI-enrichment friction-point bullet is
unaffected and still stands.

A second, fresh independent `release-phase-auditor` dispatch (never a
fork of the implementer) against this corrective pass is required
before it can be treated as closed, and had not yet run as of this
note — see `planning/retros/_audit-phase-89-stage-89a.md` for its
append-only verdict history once it does.
