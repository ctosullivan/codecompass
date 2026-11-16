# Audit — Phase 89, Stage 89A ("Detection and Manifest Extension")

**Audited commit (HEAD at audit time):** `2040a8e`
**Stage commit range reviewed:** `a7d3db8..2040a8e` (`7365ee4`, `7dcae8f`,
`b7e9a10`, `52bc369`, `2040a8e`)
**Auditor:** `release-phase-auditor` (independent, read-only pass)
**Scope:** Stage 89A only, per the governing dispatch's explicit
ten-point checklist. Stages 89B/89C and Phase 89's own roadmap exit gate
are out of scope (and confirmed not started — see point 10 below).

## Verdict

**FAIL** — one real, independently-confirmed, narrow defect blocks
closeout: Stage 89A's own two new files introduce 64 new `ruff`
violations (all `E501`, line-length) that were never caught or fixed
before this audit. Every other examined dimension — the ten explicit
checklist points, the quantitative claims in the implementer's own
retro, and a live, independent end-to-end reproduction of detector (b)
against a disposable scratch copy — is sound. This is a narrow,
mechanical, trivially-fixable gap, not a defect in the stage's
substantive design or correctness; it does not require reopening any of
the ten points below, only a lint-cleanliness fix and a fresh, focused
re-audit of that fix per `CLAUDE.md` §5's "any commit after the
auditor's own pass that touches audited scope voids that pass" rule.

Precedent: this project's own Phase 87D terminal audit treated an
essentially identical situation (new code introducing 5 new `ruff`
findings, never caught before the terminal audit) as a real `FAIL`
requiring a fix-and-reaudit cycle (`598a245`), not softened to "PASS
WITH OBSERVATIONS" — this audit is consistent with that established
practice, at a larger scale (64 vs. 5 findings, same root cause: nobody
ran `ruff check .` against the new files before this audit).

## What must be fixed before re-audit

1. **Fix all 64 new `ruff` violations Stage 89A's own new files
   introduce** (confirmed via `git archive a7d3db8` baseline comparison
   — `pyproject.toml`'s `ruff` config is unchanged; these are 100%
   attributable to new code, not a pre-existing baseline or a
   config change):
   - `src/codecompass/source_reconciliation.py:640:101` — `E501` (101 >
     100).
   - `tests/test_source_reconciliation.py` — 63 `E501` findings (line
     lengths up to 117 chars), scattered through the file (e.g. lines
     907, 923, 928, and many others — run `ruff check
     tests/test_source_reconciliation.py` for the full list).
   - Every other file touched by this stage (`cli.py`, `change_impact.
     py`, `knowledge_intermediate.py`, `oracle.py`) introduces **zero**
     new violations — confirmed by diffing `ruff check .` run against
     the `a7d3db8` baseline (167 pre-existing errors, all in files
     Stage 89A does not touch or, for `cli.py`, the same 5 pre-existing
     errors before and after) vs. the current tree (231 errors; the
     +64 difference is entirely the two new files).
   - After fixing, re-run `ruff check .` and confirm it reports exactly
     167 errors (the unchanged, pre-existing baseline in
     `knowledge_api.py`/`test_knowledge_api.py`/
     `test_assess_change_impact.py`/`test_check_self_knowledge_quality.
     py`/`scripts/check_self_knowledge_quality.py`/`tests/test_cli.py`/
     `cli.py`'s 5 pre-existing ones) — not zero, since those are
     out-of-scope pre-existing findings this stage did not introduce
     and is not asked to fix, but confirmed *not increased* by this
     stage's own work.
2. **Name this as a process gap explicitly in the phase retro or a
   follow-up note**: nothing in Stage 89A's own implementation process
   (the implementing pass, the six planning-review rounds, the ADR)
   ever ran `ruff check .` against the new files before this terminal
   stage audit — this is the same gap `L-130` (Phase 87D) already named
   once; it recurred here at a larger scale. Worth a learning entry
   alongside `L-135`/`L-136` if not already covered by `L-130`'s own
   existing scope.

Two further items are **non-blocking observations**, not required
before re-audit, but should not be silently dropped — see "Non-blocking
observations" below.

## Evidence for the FAIL finding

```
$ git archive a7d3db8 | tar -x -C <scratch-baseline>
$ ruff check <scratch-baseline> --output-format=concise | ...
Found 167 errors.   (5 in cli.py, 68 in knowledge_api.py, 57 in
                      test_knowledge_api.py, 18 in
                      test_assess_change_impact.py, 14 in
                      test_check_self_knowledge_quality.py, 4 in
                      scripts/check_self_knowledge_quality.py, 1 in
                      test_cli.py — all pre-existing, none touched by
                      this stage's own diff)

$ ruff check .   (against 2040a8e, the real committed tree)
Found 231 errors.   (same 167 above, UNCHANGED, + 63 new in
                      tests/test_source_reconciliation.py + 1 new in
                      src/codecompass/source_reconciliation.py)
```

`pyproject.toml`'s `[tool.ruff]` config (`line-length = 100`) has zero
diff across this commit range — the +64 is attributable entirely to
newly written code, not a config change or a baseline re-measurement
artifact.

## The ten checklist points

### 1. Both Ledgerkit detector pathways execute successfully

**Confirmed, including a live, independent end-to-end reproduction of
detector (b)** (not merely re-traced — actually run), plus direct
source/test verification of detector (a)'s own claims.

- Direct source tracing: `detect_source_changes`,
  `detect_newly_coverable_checks`, `propose_reconciliation`, and
  `apply_manifest`'s new `"source_reconciliation"` branch
  (`knowledge_intermediate.py:_apply_source_reconciliation`) all match
  the plan/ADR's own description exactly — confirmed by reading every
  one of these functions directly against the real committed source
  (`src/codecompass/source_reconciliation.py`,
  `src/codecompass/knowledge_intermediate.py:2524-2662`).
- Detector (a)'s own retro-described mutation and test bodies were
  verified directly against the real `~/projects/ledgerkit` checkout
  (never modified — `git status`/`git log` confirmed clean throughout
  and unchanged, still at `a7740fd`): `reports.py:663`'s matching gate
  and `reports.py:685`'s `if section.invert:` guard are at exactly the
  line numbers the plan/ADR cite; `tests/test_reports.py`'s
  `test_single_section_rows_and_subtotal`/`test_multi_section_
  correct_values` assert the exact subtotal values (`1359.00`/
  `6000.00`) the plan's own §0.2.C analysis depends on, and
  `test_section_multiple_accounts_patterns_or_union` asserts only row
  membership, never subtotal arithmetic — confirming the plan's own
  reasoning for *why* the original OR-union mutation would not have
  failed any real test, and why the corrected sign-inversion mutation
  does. `test_section_accounts_overlapping_patterns_no_double_count`
  (detector (b)'s own target test) does **not** exist in the real
  checkout — confirmed absent, exactly as expected (added only to a
  disposable scratch copy per the plan's own non-goal).
- **Live reproduction of detector (b), run by this audit, end to end,
  against disposable scratch copies** (`cp -r ~/projects/ledgerkit` +
  a scratch copy of the real `planning/contracts/balance-from-spec`/
  `planning/knowledge/balance-from-spec` directories — never the real
  CodeCompass or Ledgerkit checkouts, both confirmed `git status`-clean
  before and after):
  1. Added the real `test_section_accounts_overlapping_patterns_no_
     double_count` test body (accounts=`("food", "groceries")` against
     the real £150.00 groceries posting) to the scratch Ledgerkit copy
     — confirmed it genuinely passes standalone (`pytest -q`: `1
     passed`).
  2. `codecompass sync --yes` against the scratch Ledgerkit copy —
     `context-graph.db` correctly populated (`reports.py`/`test_
     reports.py` content hashes present) despite a non-fatal `TypeError`
     from the Phase B (AI enrichment) step with no API key configured,
     exit code 0 — exactly matching `L-136`'s own account.
  3. `codecompass knowledge detect-changes balance-from-spec
     --repo-root <scratch-ledgerkit> --probe-coverage --json` —
     correctly reported `newly_coverable: [{check_id:
     "overlapping-account-patterns-no-double-count", claim_id:
     "CL-BFS-004"}]`, and correctly reported `tests/fixtures/
     filtered.journal` as `stale_graph_index` (not Python-indexed,
     exactly matching the retro's own named limitation).
  4. `codecompass knowledge verify-changes balance-from-spec
     --repo-root <scratch-ledgerkit> --json` — wrote a manifest with
     one `source_reconciliation` item, label `"newly_covered"`, target
     field `supporting_evidence`, citing a real, freshly-persisted
     `OracleResult` under `planning/contracts/balance-from-spec/
     results/` with a real `run_id`/`raw_output_ref`.
  5. Set `decision = "accept"`, ran `codecompass knowledge apply
     <manifest>` — applied successfully, minted a new Evidence record,
     and `CL-BFS-004.evidence_support_state` changed from
     `partially_supported` to `supported`, `supporting_evidence`
     correctly became `[EV-BFS-001, EV-<new>]` (old citation preserved,
     new one appended) — matching the plan's/retro's own claimed
     outcome exactly.
  - **One cosmetic, non-blocking discrepancy found during this
    reproduction**: the real, pre-existing, unmodified `_next_id`
    helper (`knowledge_intermediate.py:2070-2078`, not touched by this
    stage) mints the new Evidence record as `EV-BALANCEFROMS-004`, not
    `EV-BFS-004` as the plan's own §6.1 step 8 walkthrough names it —
    because `_next_id`'s slug token is mechanically derived from the
    slug directory name's own uppercase alphanumerics
    (`balance-from-spec` → `BALANCEFROMS`), while the existing,
    hand-authored `EV-BFS-00{1,2,3}` records use a human-chosen
    abbreviation `_next_id` was never previously exercised to produce
    (this is the *first* mechanized Evidence-creation path in this
    codebase, per the ADR, so this characteristic of an
    already-existing, unmodified helper was never previously visible).
    Purely cosmetic — does not affect uniqueness, correctness, or any
    invariant this mechanism depends on — but the plan's own
    illustrative walkthrough's literal ID is not what a real run
    against the real slug would actually produce. Worth a one-line
    correction to the plan/ADR's own prose if anyone revisits it, never
    a functional fix.
  - Both the real `~/projects/ledgerkit` and the real `codecompass`
    checkouts were confirmed `git status`-clean before this
    reproduction began and after it concluded (all work happened under
    a disposable `/tmp` scratch path); the scratch path was deleted
    afterward.

Detector (a) was not independently re-run live by this audit (time
budget favoured a full live reproduction of detector (b), the more
novel of the two, plus direct source/test verification of detector
(a)'s own specific claims) — this matches the dispatch's own "at
minimum... re-trace" bar, which detector (a) clears via direct,
line-number-verified source/test reading.

### 2. Test-only changes trigger appropriate verification

**Confirmed real, implemented, and tested.** `detect_source_changes`'s
`resolution="test_input_change"` branch
(`source_reconciliation.py:364-383`) is distinct from
`"symbol_change"`, tracks `oracle-contract.yaml`'s own
`test_input_paths` for checks with existing citing Evidence
(`_tracked_test_input_paths`), and resolves via
`_claims_bridged_by_check_id` (a direct check_id→Evidence→Claim lookup)
— never through `change_impact.classify_symbol`. Dedicated test:
`TestDetectSourceChanges::test_test_only_change_detected_via_test_
input_paths` (asserts the resolution, `check_id`, `claim_ids`, and
explicitly asserts it is **never** misreported as `symbol_change`) —
passes.

### 3. Historical Evidence remains distinguishable from newly covered checks

**Confirmed.** `detect_newly_coverable_checks`
(`source_reconciliation.py:411-479`) gates on "zero existing
`evidence_kind: "test"` Evidence record... for this `check_id`"
(`covered_check_ids`, built from `_test_evidence_check_id_map`) — never
on "zero currently-valid historical result." Dedicated regression test,
read directly: `TestDetectNewlyCoverableChecks::test_check_with_
existing_evidence_is_never_newly_coverable_even_if_stale` — constructs
exactly the "previously-covered-but-now-stale" scenario (an existing
citing Evidence record whose underlying test input has drifted) and
asserts `result.coverable == []` and `result.not_yet_coverable == []`
(never even scanned — confirmed detector (a)'s own exclusive scope) —
passes.

### 4. OracleResults retain durable, portable provenance

**Confirmed.** `_durable_raw_output_dir` (`source_reconciliation.py:
504-509`) returns `planning/contracts/<slug>/results/raw` —
project-relative, never `scratch-assessments`. `_persist_and_verify`
(`source_reconciliation.py:512-556`) writes under this convention and
round-trips (re-parse + raw-output hash re-check) before returning
`ok=True`. Dedicated tests, all read directly and confirmed passing in
the full suite run (see point 9): `test_persist_and_verify_writes_
results_dir_and_results_raw_dir`; `test_reloading_from_a_freshly_
copied_location_still_resolves` (a genuine fresh-filesystem-relocation
test — `shutil.copytree` to a new path, re-parses and re-evaluates
precedence from the moved location, asserts `PASS`);
`test_corrupted_raw_output_fails_closed` (a corrupted raw-output file
fails the hash check); `test_retry_never_rewrites_an_already_persisted_
result` (the crash-and-retry-without-duplication case — confirmed
`_persist_and_verify` detects the immutable per-run filename already
exists and skips re-writing it, returning `"already persisted"`).

### 5. Multiple-range callback results cannot be incorrectly paired

**Confirmed, by direct reading and the dedicated test.**
`run_check_assurance` (`change_impact.py`) takes `on_fresh_result:
Callable[[OracleResult], None] | None = None` (single-arg). `assess`
takes `on_fresh_result: Callable[[int, OracleResult], None] | None`
(the `int` being the zero-based range index), wrapping the single-arg
form per range before passing down
(`(lambda result, _i=range_index: on_fresh_result(_i, result))`).
`source_reconciliation.propose_reconciliation`'s own `_capture` closure
is a flat `dict[(range_index, check_id), OracleResult]`
(`source_reconciliation.py:602-605`), never a list. Dedicated test,
read directly: `TestOnFreshResultCallback::test_multi_range_capture_
is_keyed_by_range_index_and_check_id` — genuinely constructs two
different `ChangedRange`s in one `assess()` call contributing the same
`check_id`, asserts both `(0, "chk-a")` and `(1, "chk-a")` are present
with **different** `run_id`s (no cross-contamination) — passes.

### 6. Evidence and Claim updates are safe to retry

**Mostly confirmed, with one real, non-blocking test-coverage gap
found.** `_find_existing_evidence_for_run`
(`knowledge_intermediate.py:2148-2196`, near `_find_existing_promoted_
record`) and the Claim-side append idempotency check
(`_apply_source_reconciliation`'s own `if ev_id not in
supporting/contradicting` guards, same file ~line 2650) are two
genuinely **independent** checks in the real code — confirmed by direct
reading, not merely asserted. Dedicated tests exist and pass for:
Evidence-identity retry (`test_evidence_identity_retry_never_
duplicates`) and a conflicting-edit-between-detection-and-apply refusal
(`test_conflicting_edit_between_detection_and_apply_is_refused`).

**Gap found**: the plan's own §7 test list calls for *three* separate
tests here — "Evidence-identity-retry," "Claim-append-retry" (named
explicitly as independent of whether the Evidence record itself was
newly written or already existed), and "interrupted-apply" (crash
mid-batch across multiple items, re-run detection reports the same
findings). Only a **combined** full-item-retry test exists
(`test_evidence_identity_retry_never_duplicates` re-applies an
already-fully-applied item, which happens to exercise both the
Evidence-write skip and the Claim-append skip together, since both had
already fully completed on the first attempt). No test isolates the
genuinely asymmetric case the two-independent-checks design exists
for: an Evidence record already written to disk (e.g. from a prior
crashed attempt) but the Claim-side append **not yet** applied. No
dedicated "interrupted-apply" test (crash mid-*batch*, across separate
items) exists either, though this is largely guaranteed by detection's
own read-only-by-construction design.

This audit independently verified the production code *itself* handles
the untested asymmetric case correctly (a disposable scratch script,
not committed, constructed an Evidence record already on disk with the
Claim not yet citing it, and confirmed `_apply_source_reconciliation`
correctly skips re-writing the Evidence and correctly performs the
still-needed append, producing the right final state) — so this is a
**test-coverage gap, not a functional defect**. Listed as a
non-blocking observation below, not part of the required-fix list,
since the mechanism itself is correct.

### 7. Human approval and canonical mutation boundaries remain enforced

**Confirmed.** `apply_manifest`'s shared gate
(`knowledge_intermediate.py:2690-2697`) skips any item whose `decision
!= "accept"` **before** reaching any `_apply_*` dispatch branch,
including the new `"source_reconciliation"` one — structurally, this
new branch cannot be reached on `"undecided"`/`"reject"`. `detect-
changes` without `--probe-coverage`: confirmed zero subprocesses, zero
files via both the dedicated test
(`TestCliBoundaries::test_detect_changes_without_probe_spawns_no_
subprocess_and_writes_nothing`, which monkeypatches `subprocess.Popen`
to raise if called) **and** this audit's own live reproduction (ran
the real `detect-changes --json` command against a real scratch
Ledgerkit copy; no subprocess was spawned, confirmed by direct
observation of the invocation completing instantly with correct JSON
output). `--probe-coverage` spawns exactly one `pytest --collect-only`
subprocess per uncovered check (`test_detect_changes_with_probe_
spawns_exactly_one_collect_only_subprocess`, asserting both the call
count and `--collect-only` appearing in the captured command). `verify-
changes` is the only command that actually executes checks/persists
results (`test_verify_changes_executes_and_persists` — confirmed by
this audit's own live run too). `apply` is the only command that
mutates canonical knowledge, and only on `"accept"` — confirmed live.

### 8. CLI execution behaviour matches documentation

**Confirmed.** `docs/reference/cli.md`'s new section (diff reviewed
directly) accurately describes `detect-changes`'s default zero-
subprocess/zero-write behaviour, `--probe-coverage`'s exactly-one-
subprocess/zero-write behaviour, `--establish-baselines`'s one
explicit exception, and `verify-changes`'s real-execution/persistence/
manifest-writing behaviour — matching `cli.py`'s real implementation in
every particular checked. No mismatch found.

### 9. Phase 81-88 interfaces remain compatible

**Confirmed, including a full, fresh test-suite run.** `mcp/
tools.py:342` (`impact_classify_change`'s own call to `_ci.assess(...,
run_checks=False)`) was read directly — it passes neither
`on_fresh_result` nor `raw_output_dir`, and separately, since it passes
`run_checks=False`, never reaches the code path that would invoke the
callback even if it had — unaffected on two independent counts,
exactly as the ADR claims.

**Full suite run by this audit** (`.venv/bin/pytest -q` from the repo
root, 463.89s): **`1497 passed, 2 skipped`** — exactly matching the
figure claimed in `CHANGELOG.md`/`planning/CONTEXT.md`/`planning/
ROADMAP.md` ("full suite (1497 tests)... all pass"). No regression
observed anywhere outside the new test file.

### 10. No Stage 89B/89C functionality prematurely implemented

**Confirmed clean.**
- `grep -rn "claim_contradicted_by_fresh_check"` across `src/`,
  `tests/`, `decisions/`, `docs/` returns **zero** matches — only the
  plan file and the plan-review file reference it (as Stage 89B's own
  future deliverable).
- `git diff a7d3db8 2040a8e --stat -- src/codecompass/knowledge_api.py`
  is **empty** — `find_gaps` (home of the gap-kind taxonomy) was not
  touched at all.
- `planning/retros/phase-89-ledgerkit-two-task-demonstration.md`
  (Task B's pre-registration) was read in full: §9 "Execution" states
  explicitly "Task B itself is **not executed** under this dispatch's
  own authorisation (Stage 89A only)" — no controlled-comparison
  execution/results anywhere in the file, only the selection
  rule/rationale/design, exactly as a genuine pre-registration record
  should look.
- `planning/ROADMAP.md`'s Phase 89 row reads "in progress (Stage 89A
  done)" — **not** `done`. Confirmed directly, not merely trusted from
  the retro's own account.

## Quantitative claims independently verified

| Claim (retro/CHANGELOG/CONTEXT/ROADMAP) | Independently verified |
|---|---|
| 33 new tests in `tests/test_source_reconciliation.py` | Confirmed — `pytest --collect-only -q` reports exactly 33 |
| Full suite 1497 tests, all pass | Confirmed — `1497 passed, 2 skipped in 463.89s` |
| `scripts/check_knowledge_base.py` passes | Ran: 24 informational (`knowledge-base-snapshot-current-divergence`) findings, exit 0, all pre-existing lifecycle-status divergences unrelated to Stage 89A |
| `scripts/check_contracts.py` passes | Ran: 7 informational findings (6 `contract-result-integrity-mismatch` for pre-existing stale `balance-from-spec` results under the live contract hash, 1 `contract-check-gap` for the still-pending third check), exit 0 |
| Stage 89A did not touch `planning/contracts/` | Confirmed — `git diff a7d3db8 2040a8e --stat -- planning/contracts/` is empty; all 7 `check_contracts.py` findings are pre-existing, per `decisions/0081`/`0088`'s own named, expected state, not newly introduced by this stage |
| Files changed match the plan's own named deliverables | Confirmed — `git diff --stat` shows exactly: `CHANGELOG.md`, `decisions/0096-*.md` (new), `docs/architecture/components.md`, `docs/reference/cli.md`, `planning/CONTEXT.md`, `planning/ROADMAP.md`, `planning/knowledge/balance-from-spec/REQ-BFS-002.yaml`, `planning/learnings/inbox.md`, `planning/retros/phase-89-ledgerkit-two-task-demonstration.md` (new), `planning/retros/phase-89-stage-89a.md` (new), `src/codecompass/{change_impact,cli,knowledge_intermediate,oracle,source_reconciliation}.py`, `tests/test_source_reconciliation.py` (new) — no scope creep into `mcp/`, `doc_compiler.py`, `knowledge_api.py`, or any file the plan's explicit non-goals (§10) name as off-limits |
| No `CLAUDE.md` drift, no past-ADR edits | Confirmed — `git diff a7d3db8 2040a8e -- CLAUDE.md` empty; `decisions/` diff is exactly one new file (`0096-*.md`), zero modifications to any existing ADR |

## Non-blocking observations (not required before re-audit)

1. **Test-coverage gap for the asymmetric Evidence/Claim-append-retry
   case** (point 6 above) — recommend adding a dedicated test before
   Stage 89A is fully closed, though the mechanism itself was
   independently verified correct by this audit.
2. **No dedicated "interrupted-apply" (crash mid-batch, re-run
   detection) test** exists as its own named test, though this is
   largely guaranteed by detection's read-only design.
3. **No `docs-reconstructor`-style independent drift audit has yet run**
   for Stage 89A's own documentation changes (`docs/architecture/
   components.md`, `docs/reference/cli.md`). `CLAUDE.md` §5 names this
   as a general per-phase DoD condition, and its absence caused Phase
   88's own *first* terminal audit to `FAIL` (a precedent worth
   recalling). This audit's own explicit ten-point checklist did not
   name it, and the plan's own §7 Stage 89A deliverable list names only
   a stage-level `release-phase-auditor` pass (this one), deferring a
   full documentation-drift pass to Phase 89's own terminal closeout —
   consistent with that staged structure, but flagged here so it is not
   silently dropped before that closeout happens. This audit's own
   direct reading of both changed doc sections (point 8 above) found no
   mismatch, which is some evidence against drift, but is not a
   substitute for an independent `docs-reconstructor` pass.
4. **Cosmetic plan/ADR-vs-reality ID mismatch** — see point 1's
   `EV-BALANCEFROMS-004` vs. `EV-BFS-004` finding above. No functional
   impact; worth a one-line correction if the plan/ADR text is ever
   revisited.
5. **Candidate learnings `L-135`/`L-136` remain `status: candidate`,
   untriaged** — this is expected and correct per the plan's own §7
   staged structure (learnings triage is a named *terminal* Phase 89
   closeout activity, not a Stage 89A one) — not a gap at this stage.

## Process note

Per `CLAUDE.md` §5, any commit after this audit's own pass that touches
audited scope voids this pass. The required fix (item 1 above) touches
exactly two files already in audited scope
(`src/codecompass/source_reconciliation.py`,
`tests/test_source_reconciliation.py`) and, if it also updates the
phase retro with a process-gap note (item 2), that file too — a fresh,
focused re-audit of just that fix (confirming `ruff check .` now
reports the unchanged 167-error pre-existing baseline, the full test
suite still passes, and nothing else changed) is required before Stage
89A can be treated as closed. It should not require re-verifying the
ten checklist points above from scratch, since none of them touch the
lines being fixed.
