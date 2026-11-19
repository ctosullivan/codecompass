# Phase 89 Stage 89A retro — Detection and Manifest Extension

## Where we are

Phase 89 (Incremental Knowledge and Documentation Reconciliation) is
the second of the two phases split out of the old merged Phase 88
(`decisions/0085` §3) — the other, Phase 88 (Agent Integration and
MCP), landed first and independently (`planning/retros/
_audit-phase-88.md`). Phase 89 itself is staged into three parts:
Stage 89A (this retro — detection, durable Evidence, human-approved
canonical reconciliation), Stage 89B (the new knowledge-gap
classification plus the documentation-invalidation cascade demonstration
— `planning/retros/phase-89-stage-89b.md`), and Stage 89C (Task B's
own pre-registered controlled comparison, not yet started). Stage 89A
itself builds directly on Phase 83 (`change_impact.py`'s existing
symbol-classification/assurance machinery, reused unmodified) and
Phase 87 (`docs maintain`/`compile`/`publish`'s own grounded-region
reconciliation, which Stage 89B later feeds into without modification).
After this stage (and its two corrective passes, both below), the
project state is: a source or test change to a real target checkout
can be detected, independently re-verified, and reconciled into
canonical knowledge through a human-approved, auditable manifest flow
— the prerequisite Stage 89B's own documentation cascade depends on.

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

## What worked

- **Running the real Ledgerkit demonstration, not only the synthetic
  unit suite, caught two genuine implementation bugs** (the missing
  `--establish-baselines` primitive; the re-confirmation skip-condition
  bug) that 32 passing unit tests built from the same fixtures by the
  same implementer did not — see "Lessons learnt" above for the full
  account. Keeping the real-demonstration step as a mandatory part of
  this stage's own closeout, not an optional nice-to-have, is exactly
  what caught these.
- **Resolving an implementation-contract ambiguity at build time**
  (the `on_fresh_result` capture-parameter design, "Process-improvement
  feedback" above) rather than treating the plan's own sketch as
  literal, produced a simpler, equally sound mechanism — the dispatch's
  own explicit authorisation to do this paid off directly.
- **The plan's own six-round independent review before implementation
  began** (`planning/retros/_review-phase89-plan.md`) meant this
  stage's own implementation had very few design-level surprises; the
  defects found afterward (both corrective passes, below) were all at
  the *implementation* level, never a planning-level gap the plan's own
  review should have caught but didn't.

## What didn't work

- **The original `release-phase-auditor` pass's own ten-point
  checklist, however thorough against what it was scoped to check, did
  not generalise to catch either corrective pass's own defects** — not
  because that audit was careless, but because a checklist built
  against one defect class says nothing about a structurally different
  one in the same code. See the "2026-11-18/19" addendum below, and the
  new candidate learning (`L-137`) filed specifically to name this
  pattern, for the full account — stated here too since it is, in
  hindsight, as much a "what didn't work" for *this* stage's own
  original closeout as it is a lesson for future ones.
- **The first attempt at this retro's own closeout treated the
  original audit's PASS as the stage's final word**, without
  anticipating that a later, independent, differently-scoped review
  could still find real defects in already-"PASSed" code — exactly the
  gap `L-137` now names explicitly, so a future stage's own closeout
  checklist can ask the question directly rather than relying on a
  single audit round's own silence as proof of nothing left to find.

## Candidate learnings filed

`L-135` and `L-136` (both filed during this stage's own original
Ledgerkit demonstration, 2026-11-17) — triage disposition and a third,
related learning (`L-137`, filed afterward naming the audit-checklist-
scoping pattern both corrective passes below demonstrated) are recorded
in `planning/learnings/inbox.md`/`promoted.md`, not repeated here (this
retro states facts about the stage's own work; the learning lifecycle's
own disposition record is the inbox's job, per this project's own
established separation).

## Where we're going

This stage's own two corrective passes (below) close out Stage 89A
itself. Stage 89B (the new `claim_contradicted_by_fresh_check` gap kind
plus the real documentation-cascade demonstration) depends directly on
this stage's own durable `OracleResult`/Evidence/manifest mechanism —
it reads the same manifests this stage's own `verify-changes`/`apply`
commands produce, adding no new detection or reconciliation mechanism
of its own. Stage 89C (Task B's own pre-registered controlled
comparison) remains the only piece of Phase 89's own roadmap exit gate
not yet started. This stage's own outcome did not change that
trajectory — the plan's own staged order (§7) is being followed as
written.

## Time / cost note

Original implementation: roughly one extended session (2026-11-16/17),
including the real two-detector Ledgerkit demonstration and the Task B
pre-registration. First corrective pass: a further session (2026-11-18).
Second corrective pass plus its own independent audit history (original
→ first corrective → second corrective → a third, process-completeness-
only audit → this retro's own completion): a fourth session (2026-11-18/
19). No AI-spend figures were separately instrumented for this stage by
the harness; the real cost driver across all rounds was independent
`release-phase-auditor`/`knowledge-curator` dispatch time, not
implementation time — each corrective pass's own fix was small once the
defect was correctly identified.

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

## 2026-11-18/19 — second corrective pass (`decisions/0098`) and its
own independent audits

That second audit returned **PASS WITH NON-BLOCKING OBSERVATIONS**
(`planning/retros/_audit-phase-89-stage-89a.md`), live-reproducing all
four mandated checks of the first corrective pass against fresh
Ledgerkit scratch copies and confirming the suite/validator/ruff
results unregressed.

A further, independent source-level review then found two more
material defects neither the original audit's checklist nor the first
corrective pass's own checklist had been scoped to probe for:
`_apply_source_reconciliation` could silently promote a whole-contract/
aggregate Claim (the real `CL-BFS-005`, whose own `depends_on` names
`CL-BFS-001`/`CL-BFS-002`) to a new support state on the strength of a
single re-verified check's result — contradicting this module's own
docstring-asserted but previously unenforced single-check-scope
invariant; and `write_source_reconciliation_manifest`'s one-second-
precision timestamp filename could let a second `verify-changes` run
within the same second silently overwrite an earlier, still-pending
manifest's own recorded review decision. Fixed via a new, reused-not-
invented `claim_scope_category` eligibility gate (superseded/aggregate/
ambiguous/eligible, applied both at proposal time and defensively at
apply time) and collision-resistant exclusive manifest creation
(atomic hardlink-from-temp-file, bounded retry with a disambiguating
suffix) — full detail in `decisions/0098` and `CHANGELOG.md`. Covered
by 18 new tests (75 total in `tests/test_source_reconciliation.py`) and
re-demonstrated live against fresh Ledgerkit scratch copies
(`planning/retros/phase-89-stage-89a-second-corrective-ledgerkit-
demonstration.md`), confirming `CL-BFS-003` stays untouched,
`CL-BFS-005` is reported affected but never mutated, `CL-BFS-001`/
`CL-BFS-002` reconcile correctly, the shared baseline still advances
once every sharing check is resolved, and detector (b)'s own
`CL-BFS-004` reconciliation remains fully functional. A second,
independent `release-phase-auditor` pass live-reproduced both defects
and their fixes against its own disposable scratch copy and returned
**PASS**. The implementation landed at commit `61591f4`.

**A third independent `release-phase-auditor` pass**, dispatched
specifically to re-verify this exact committed state before Stage 89B
began, confirmed every mechanism in its own five audited areas (Claim-
scope correctness; shared-test-input/baseline integrity; apply-time
Evidence integrity/recovery; manifest-collision safety; repository/
audit integrity) sound — but returned **FAIL on process-completeness
grounds, not a code defect**: this retro had not yet been updated for
the second corrective pass at all (fixed by this very addendum);
`L-135`/`L-136` sat untriaged in `planning/learnings/inbox.md` despite
being filed during the original Stage 89A implementation (triaged by
`knowledge-curator`, see that file's own history for the disposition,
plus a new candidate learning filed naming the recurring "an audit
checklist built for one defect class does not generalize to a
different one" pattern — the same shape Phase 88's own `L-132` already
named); and `CHANGELOG.md`/`planning/ROADMAP.md`/`planning/CONTEXT.md`
still described the implementation as staged-but-uncommitted after the
commit had already landed (fixed in all three). The auditor also
separately, correctly observed that Stage 89B implementation had begun
concurrently with its own audit of the live working tree, before this
third audit's own verdict was known — a genuine sequencing artifact of
the governing dispatch's own "proceed directly to Stage 89B" instruction
on a presumptively-sound Stage 89A, not a concealment; disclosed here
and in the Phase 89 completion report rather than smoothed over. None
of this required touching `source_reconciliation.py`, `knowledge_
intermediate.py`, or `tests/test_source_reconciliation.py` as committed
at `61591f4` — that code was independently reconfirmed sound a third
time. A fresh re-audit of this process-completeness fix is recorded in
`planning/retros/_audit-phase-89-stage-89a.md` once it runs.

**Lesson, stated plainly rather than repeated as a bare fact**: three
independent review rounds in a row (original audit → first corrective
pass → second corrective pass) each found real, material defects the
previous round's own checklist had not been scoped to catch — not
because any one review was careless, but because a checklist built
from one defect's own shape does not automatically generalize to a
structurally different defect in the same code. This is the same
pattern `L-132` already named for Phase 88; Stage 89A is now a second,
independently-arrived-at confirmation of it, not a coincidence specific
to this stage.
