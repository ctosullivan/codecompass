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

---

## Re-audit — 2026-11-17 (focused re-check of the E501 fix, commit `1f59a1c`)

**Scope:** narrow, as dispatched — verify only that commit `1f59a1c`
(on top of `2040a8e`, the state this report's original audit above
examined) fixes the 64 new `ruff` E501 violations the original pass
found, without reintroducing a regression and without touching anything
outside that cosmetic fix. The ten substantive checklist points are not
re-verified; the original audit above already confirmed them sound and
this fix does not touch logic.

**Auditor:** `release-phase-auditor` (independent, read-only pass).

### What was re-run, and the result

1. **`ruff check` on the two touched files directly:**
   `.venv/bin/ruff check src/codecompass/source_reconciliation.py
   tests/test_source_reconciliation.py` → `All checks passed!`. Zero
   violations, confirming all 64 flagged `E501`s are gone.

2. **Whole-repo `ruff` baseline:** `.venv/bin/ruff check src/ tests/` →
   `Found 163 errors.` This is corrected from the previous section's own
   stated "167-error pre-existing baseline" (a typo/stale figure in the
   original report, not independently re-derived at the time). To
   settle the true number rather than trust either figure, this pass
   added a disposable `git worktree` at `a7d3db8` (the commit
   immediately before Stage 89A's own work began) and ran `ruff check
   src/ tests/` against it directly: **163 errors**, exactly matching
   the current count at `1f59a1c`. The pre-existing baseline is fully
   restored — confirmed independently, not merely by trusting the fix
   commit's own message. (The worktree was removed via `git worktree
   remove --force` immediately after the check; `git worktree list` and
   `git status --short` afterward confirm no stray worktree or
   uncommitted change was left in the main working tree.)

3. **Full test suite:** `.venv/bin/pytest -q` from the repo root →
   `1497 passed, 2 skipped in 521.27s (0:08:41)`. Matches exactly, no
   regression from the line-wrapping.

4. **Diff scope check:** `git diff --stat 2040a8e 1f59a1c` and `git diff
   --name-only 2040a8e 1f59a1c` show exactly three touched paths:
   `planning/retros/_audit-phase-89-stage-89a.md` (this report being
   committed — insertions only, the prior audit's own text),
   `src/codecompass/source_reconciliation.py` (+3/-1 lines: one
   boolean-expression line split across two lines, no token or operator
   changed — confirmed by reading the hunk directly), and
   `tests/test_source_reconciliation.py` (+244/-69 lines, all of which
   this pass read in full via `git diff` and cross-checked two ways):
   - A whitespace-insensitive normalization diff (`re.sub(r'\s+', '',
     content)` on the full old and new file, then `difflib`) isolated
     every non-whitespace-only change to two patterns: (a) long dict
     literals split across lines (adding a trailing comma — standard
     `ruff`/formatter-style reflow, not a value change), and (b)
     repeated long path expressions (e.g.
     `project_root/"planning"/"contracts"/"demo"/"results"`,
     `project_root/"planning"/"knowledge"/"demo"/"reconciliation"`)
     factored into a local variable (`results_dir`, `reconciliation_dir`)
     then reused — read directly in the diff (hunks at original lines
     652-674, 877-920) and confirmed the extracted variable's value is
     character-for-character identical to the inline expression it
     replaced, and every call site using it is unchanged in meaning.
   - A full manual read of every hunk in the test-file diff (36 hunks)
     confirmed every change is one of: wrapping a long function-call
     argument list across lines, wrapping a long dict literal, wrapping
     a long f-string/comparison expression, wrapping a long
     `write_text(...)` call, or the two local-variable extractions
     above. No assertion's expected value changed, no test's logic
     branch changed, no fixture or helper's behavior changed.

### Verdict

**PASS WITH NON-BLOCKING OBSERVATIONS** — the fix is exactly what it
claims to be: a cosmetic, line-wrapping-only change that resolves all 64
new `ruff` E501 violations, restores the whole-repo lint count to its
true pre-existing baseline (163, independently confirmed against a
disposable `a7d3db8` worktree — not 167 as the original audit section
above stated), introduces no test regression (1497 passed, 2 skipped,
unchanged), and touches nothing outside the two files + this audit
report. Stage 89A's own ten substantive checklist points remain sound,
as the original audit above already established and this fix does not
disturb.

Carried forward, unchanged and not re-litigated, the two non-blocking
observations the original audit above already raised:

1. **Missing dedicated test coverage for the asymmetric
   Evidence/Claim-append-retry case** (mechanism independently verified
   correct by the original audit, but no dedicated test names it).
2. **No `docs-reconstructor`-style independent drift audit has yet run**
   for Stage 89A's own documentation changes — deferred to Phase 89's
   terminal closeout per the plan's own staged structure, not a Stage
   89A gap, but not to be silently dropped before that closeout.

One additional minor correction for the record (not a new blocking
finding): the original audit's own process note above stated the
pre-existing baseline as "167 errors"; this re-audit independently
re-derived it as 163 via a disposable worktree comparison against
`a7d3db8` and confirmed 163 is both the true original baseline and the
current post-fix count. No action required — noted so a future reader
of this file isn't misled by the earlier figure.

---

## Re-audit — 2026-11-18 (corrective pass, commits `98a2e1d`/`8f064dc`)

**Scope:** an independent audit of the Phase 89A corrective pass
(`decisions/0097`) landed on top of the prior `PASS WITH NON-BLOCKING
OBSERVATIONS` verdict above. Governed by the dispatch's own explicit
checklist: three material defects (shared-test-input attribution and
baseline eligibility; apply-time re-validation; idempotent-retry
recovery) plus two bounded integrity fixes (non-Python oracle-input
tracking; working-tree provenance). Per `CLAUDE.md` §5, this is a fresh
pass, not a re-trace of the ten substantive checklist points the
original audit already confirmed — those are untouched by this
corrective pass except where explicitly named below.

**Auditor:** `release-phase-auditor` (independent, read-only pass, no
prior context on this project beyond what the repository itself and the
dispatch's named documents provided).

### Documents read

`decisions/0097-phase-89-stage-89a-corrective-pass-apply-time-validation-
and-shared-input-attribution.md` (full); `planning/retros/phase-89-
stage-89a-corrective-ledgerkit-demonstration.md` (full, the
implementer's own 8-scenario Ledgerkit log); `git diff 1bf83c2 98a2e1d
-- src/codecompass/source_reconciliation.py src/codecompass/
knowledge_intermediate.py src/codecompass/cli.py` (full, line by line);
`tests/test_source_reconciliation.py`'s full diff (`git diff 1bf83c2
98a2e1d`, 729 lines — every new test class read, not just counted); the
original audit history above (not edited); `CHANGELOG.md`, `planning/
CONTEXT.md`, `planning/ROADMAP.md`, `docs/reference/cli.md`,
`planning/retros/phase-89-stage-89a.md` diffs for the second commit
(`98a2e1d..8f064dc`).

### What was independently reproduced myself (not just read)

All reproductions below used **fresh disposable scratch copies** under
`/tmp/claude-1000/.../scratchpad/phase89a-audit/` (`cp -r
~/projects/ledgerkit <scratch>`, never a git clone, never the real
checkout; a disposable scratch copy of the real `planning/contracts/
balance-from-spec/` + `planning/knowledge/balance-from-spec/`, never the
real CodeCompass knowledge base) and the real CLI
(`/home/cormac/projects/codecompass/.venv/bin/codecompass knowledge
...`). `~/projects/ledgerkit`'s own `git status --short`/`git log
--oneline -1` were confirmed clean, at `a7740fd`, both before this
session's work began and again after every scratch copy was made — no
command was ever run with `--repo-root` pointing at the real checkout,
and the real checkout was never touched.

1. **Shared-test-input, multiple-check defect and its correction
   (reproduced live, end to end, via the real CLI).** Confirmed the
   real `oracle-contract.yaml` has `single-section-expense-subtotal`
   and `multi-section-income-expense-subtotal` both listing `tests/
   test_reports.py` + `tests/fixtures/filtered.journal` as
   `test_input_paths`, both with real citing Evidence (`EV-BFS-002`/
   `EV-BFS-003`) in the real knowledge base. In a scratch copy, set
   `CL-BFS-001`/`CL-BFS-002` to `partially_supported`/`proposed` (so a
   fresh re-confirmation is manifest-worthy, matching the retro's own
   documented setup), established baselines against the clean checkout
   (`detect-changes --establish-baselines`, confirming the non-Python
   fixture gets a baseline entry too), then edited only `tests/
   test_reports.py` (an assertion-preserving comment) and updated the
   scratch `context-graph.db`'s own `content_hash` row directly (the
   same raw-`UPDATE` technique the implementer's own demonstration log
   used, confirmed functionally identical to a targeted `sync`). Ran
   `codecompass knowledge detect-changes balance-from-spec --repo-root
   <scratch> --json`:

   ```
   {"path": "tests/test_reports.py", "resolution": "test_input_change", "check_id": "multi-section-income-expense-subtotal", "claim_ids": ["CL-BFS-002", "CL-BFS-003", "CL-BFS-005"]}
   {"path": "tests/test_reports.py", "resolution": "test_input_change", "check_id": "single-section-expense-subtotal", "claim_ids": ["CL-BFS-001", "CL-BFS-003", "CL-BFS-005"]}
   ```

   Both checks independently reported, each correctly bridged to its own
   Claim — confirms the one-to-many fix live. Ran `verify-changes`
   (real `pytest` execution, 3-item manifest: `CL-BFS-001`, `CL-BFS-002`,
   `CL-BFS-005`, matching the retro's own account exactly, including the
   `+dirty` working-tree-provenance marker on every `contributing_
   repository_revisions` entry — see point 8 below). Annotated `decision
   = "accept"` for `CL-BFS-001` only, `"reject"` for the other two, and
   ran the real `apply` command:

   ```
   applied: recomputed evidence_support_state='supported'; evidence: EV-BALANCEFROMS-004
   skipped: rejected at review
   skipped: rejected at review
   ```

   Confirmed `source-baseline.toml`'s entry for `tests/test_reports.py`
   stayed at the **pre-edit** hash
   (`44d803f2...6007`) — unchanged — even though one sibling check
   (`single-section-expense-subtotal`) was fully, successfully
   reconciled; `CL-BFS-001.evidence_support_state` → `supported`,
   `CL-BFS-002.evidence_support_state` stayed `partially_supported`.
   This is the exact shared-baseline-eligibility behaviour the ADR
   describes, reproduced via the real CLI against the real contract and
   real Claims, not a synthetic fixture.

2. **A genuinely tampered `OracleResult` rejected during `apply`
   (reproduced live, two independent tamper variants).** Fresh scratch
   copy; added the real `test_section_accounts_overlapping_patterns_
   no_double_count` test (accounts=`("food", "groceries")`, £150.00
   groceries posting, asserting it contributes exactly once — confirmed
   it genuinely passes standalone first) to the scratch Ledgerkit,
   synced, confirmed `detect-changes --probe-coverage` reports
   `newly_coverable: [{check_id: "overlapping-account-patterns-no-
   double-count", claim_id: "CL-BFS-004"}]`, ran `verify-changes`
   (real execution, real persisted `OracleResult`), accepted the
   resulting item. **Variant A** — appended a line to the cited run's
   own `raw_output_ref` `.txt` file (the dispatch's "flip a byte"
   tamper, done as an append since the file is plaintext): `apply`
   refused with `failed re-validation: raw_output_ref '...' content does
   not match its own recorded raw_output_sha256 -- tampered or
   corrupted`; no new Evidence, `CL-BFS-004.evidence_support_state`
   stayed `partially_supported`. **Variant B** (a fresh copy of the same
   pre-apply state) — edited the cited result's own persisted `.yaml`
   metadata file, `outcome: PASS` → `outcome: FAIL`: `apply` refused
   with `re-validates as FAIL but the manifest's own cached target field
   ('supporting_evidence') disagrees -- refusing a stale or tampered
   reference`; again no new Evidence. Both variants confirm defect B's
   fix at the real apply-time write boundary, via the real `apply`
   command, not a unit-level helper call.

3. **The post-Claim-write/pre-manifest-write crash-and-retry case
   (reproduced live).** Fresh scratch copy; verified and applied the
   same real newly-coverable finding (`CL-BFS-004`) once, normally —
   `applied: recomputed evidence_support_state='supported'; evidence:
   EV-BALANCEFROMS-004`. Captured the Claim file's exact post-apply
   content, then edited the manifest's own item `state` back to
   `"pending"` — exactly the on-disk state a crash *after* the Claim
   write succeeded but *before* the caller durably recorded
   `state="applied"` would leave. Ran `apply` again on the same
   manifest/item:

   ```
   applied: already applied -- recovered from an interrupted retry (Evidence and Claim already reflect this exact approved item)
   ```

   Confirmed byte-for-byte: the Claim file's content after the retry is
   **identical** to its content after the first apply (`diff` reported
   no difference), and exactly one `EV-*` record exists (no duplicate
   Evidence). This is the exact scenario defect C's fix targets,
   reproduced via the real `apply` command against real on-disk state I
   constructed myself to match the crash window precisely.

4. **An unchanged negative control (reproduced live, multiple times).**
   The ordinary, non-defect path was exercised and confirmed working in
   every scenario above: `CL-BFS-001`'s legitimate, untampered,
   properly-accepted item applied successfully in reproduction 1; the
   legitimate `CL-BFS-004` item applied successfully on its first,
   normal run in reproduction 3 (before the crash was simulated) — both
   via the real CLI, both producing the expected `evidence_support_state`
   transition and a correctly-cited new Evidence record.

### Also verified (read + targeted reproduction, stated per item)

5. **No regression in Phase 81-88 behaviour.** Ran the full suite
   myself: `.venv/bin/python -m pytest tests/ -q` → **1517 passed, 2
   skipped, 4 failed** (`tests/test_execute_doc_example.py`'s four
   `@requires_real_sandbox` tests — missing `codecompass` on `PATH`, no
   network for `pip`), in 452.51s. **Independently confirmed these 4
   failures are pre-existing, not a regression**: built a disposable
   `git worktree add <scratch> 1bf83c2 --detach` and ran `pytest
   tests/test_execute_doc_example.py -q` against it directly — identical
   4 failures, identical reasons, 10 passed either way. Worktree removed
   immediately after (`git worktree remove --force`); `git worktree
   list`/`git status --short` confirmed clean afterward. Also ran
   `tests/test_source_reconciliation.py` alone: **57 passed**. Diff-scope
   check: `git diff --stat 1bf83c2 98a2e1d -- src/ tests/` touches
   exactly `cli.py`, `knowledge_intermediate.py`,
   `source_reconciliation.py`, `tests/test_source_reconciliation.py` —
   confirmed via the same diff that `oracle.py`, `change_impact.py`,
   `knowledge_api.py`, and everything under `mcp/` are **untouched** by
   this corrective pass (zero lines), so the Phase 82 precedence engine
   this pass newly calls, and every Phase 81-88 interface the original
   audit already confirmed compatible, is reused unmodified, not
   re-implemented.

6. **No unsafe baseline advancement.** Read `advance_baselines_for_
   applied_item`'s new cross-item gating directly
   (`source_reconciliation.py:962-999`): for each tracked path, it
   collects every manifest item (`siblings`) that also cites that path
   and only advances the baseline once *every* sibling's own `state ==
   "applied"`. **Reproduced live** in reproduction 1 above: with
   `tests/test_reports.py` shared by two checks, accepting+applying only
   one sibling (`CL-BFS-001`) left the baseline unchanged; a follow-up
   `detect-changes`/`verify-changes`/accept/`apply` cycle for the
   second, previously-rejected sibling (`CL-BFS-002`'s own check,
   re-proposed) then advanced the baseline to the post-edit hash only
   once both were genuinely applied — matching the dispatch's exact
   scenario and the retro's own account of it.

7. **Human approval and concurrent-edit guards remain effective
   (reproduced live).** Took an accepted-but-not-yet-applied manifest
   item, hand-edited the cited Claim's own file on disk (appended a
   `statement: hand-edited` line, changing its content hash) *before*
   ever running `apply` — exactly a genuine concurrent human edit, not
   the post-first-apply idempotent-retry case. `apply` refused:
   `apply-time race: the Claim changed since detection (base_claim_hash
   no longer matches) — refusing to write`; no Evidence created. This
   confirms the new idempotent-recovery pre-check (point 3 above) is
   correctly scoped — it only short-circuits once this exact item's own
   effect is *already* durably present; a pre-first-apply edit always
   falls through to the ordinary, unchanged race check.

8. **Existing Evidence provenance is not weakened.** Read `_repo_
   revision`'s new dirty-working-tree handling directly
   (`source_reconciliation.py:85-121`): a clean tree still returns the
   bare `git rev-parse HEAD` output, byte-identical to the pre-
   corrective-pass behaviour — confirmed by reading the control flow
   (the `if not dirty: return head` branch is reached before any
   `+dirty`/digest-embedding logic, and is unconditional on
   `fresh_result`). The dedicated test
   `TestWorkingTreeProvenance::test_clean_tree_returns_bare_commit_hash`
   (read directly, included in the 57-test pass above) asserts exactly
   this (`len(rev) == 40`, no `+dirty`). **Incidentally confirmed live**
   as a side effect of every scratch-Ledgerkit reproduction above: since
   my own test edits left each scratch checkout's working tree dirty
   relative to its own `HEAD`, every manifest item's `contributing_
   repository_revisions` I inspected carried the real `+dirty` marker
   plus genuine `tested_subject_digest`/`test_input_digest` values
   (e.g. `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9+dirty
   (tested_subject_digest=..., test_input_digest=...)`), never a bare
   hash silently implying a clean, verified commit.

9. **No duplicate Evidence on retry.** Covered explicitly by
   reproduction 3 above — confirmed by direct inspection (`ls` the
   slug directory for `EV-*.yaml` files before/after the retry: exactly
   one, `EV-BALANCEFROMS-004`, both times) and by the Claim file's own
   byte-identical content across the retry.

10. **No Stage 89B/89C implementation.** `grep -rn
    "claim_contradicted_by_fresh_check"` across `src/`, `tests/`,
    `decisions/`, `docs/` returns zero matches outside the plan file
    (confirmed via the same search this report's text names). `planning/
    ROADMAP.md`'s Phase 89 row reads "in progress (Stage 89A done;
    corrective pass pending independent audit)" and explicitly states
    "Stages 89B/89C not started; this phase is not `done`" — read
    directly, not merely trusted. `planning/CONTEXT.md` likewise states
    "Not yet done: Stage 89B ..., Stage 89C ..., and the roadmap's own
    positive exit gate". `git diff --stat 1bf83c2 8f064dc` (both
    commits together) touches exactly 11 files, all named in
    `decisions/0097`'s own "Consequences" section or the plan's
    documentation-sync list — no scope creep into `knowledge_api.py`
    (`find_gaps`'s home) or anything else.

11. **Strict validators, full test suite, and a baseline-aware `ruff
    check .` all pass; the pre-existing `ruff` baseline was
    independently re-derived, not trusted from memory.**
    `.venv/bin/python scripts/check_knowledge_base.py` → 24
    informational `knowledge-base-snapshot-current-divergence` findings,
    exit 0 (pre-existing, unrelated to this corrective pass).
    `.venv/bin/python scripts/check_contracts.py` → 7 informational
    findings (6 `contract-result-integrity-mismatch` for pre-existing
    stale `balance-from-spec` results, 1 `contract-check-gap` for the
    still-pending third check), exit 0 — identical in kind to what the
    original audit already observed, none newly introduced. Full suite:
    see point 5. `ruff`: `.venv/bin/ruff check src/ tests/` → **163
    errors**; `.venv/bin/ruff check .` (whole repo) → **167 errors**.
    To independently re-derive the true baseline rather than trust
    either the original audit's stale "167" figure or the re-audit
    section's "163" figure at face value, built a disposable `git
    worktree add <scratch> 1bf83c2 --detach` (the commit immediately
    before this corrective pass began) and ran both the same scoped
    (`src/ tests/`) and whole-repo (`.`) `ruff check` against it: **163**
    and **167** respectively — identical to the current tree at both
    scopes. Zero new `ruff` findings from this corrective pass, at
    either scope. The worktree was removed via `git worktree remove
    --force` immediately after each use; `git worktree list`/`git status
    --short` confirmed clean afterward every time (no stray worktree or
    uncommitted change left in the main working tree at any point in
    this audit).

### Additional direct-reading confirmations

- `oracle.evaluate_result_precedence`'s real signature
  (`contract_path: Path`, `repo_root: Path | None = None` keyword-only)
  matches the call site in `_apply_source_reconciliation` exactly
  (`contract_path=contract_path, repo_root=repo_root`); `git diff
  1bf83c2 98a2e1d -- src/codecompass/oracle.py` is empty — the function
  this corrective pass newly reuses at the apply-time boundary is
  genuinely the existing, unmodified Phase 82 engine, not a
  reimplementation.
- `apply_manifest`'s own pre-existing, unmodified `state == "applied"`
  short-circuit (checked *before* any `_apply_*` dispatch, read
  directly at `knowledge_intermediate.py:2781-2791`) is a different,
  complementary mechanism from the new idempotent-recovery pre-check
  inside `_apply_source_reconciliation` — the former only helps once
  `state` was actually durably persisted as `"applied"`; the latter
  specifically covers the window before that persistence completes
  (reproduction 3's exact scenario). The two do not conflict and do not
  duplicate each other's scope.
- `write_source_reconciliation_manifest`'s `touched_paths` filter
  (`source_reconciliation.py:922-926`) excludes an ineligible shared
  `test_input_change` path from `contributing_source_paths` at
  manifest-write time (the necessary precondition), while `advance_
  baselines_for_applied_item`'s cross-item `siblings` check (point 6
  above) is the separate, sufficient condition gating the actual
  baseline write at apply time — confirmed these are two distinct,
  correctly-layered gates, not one gate doing double duty, by reading
  both functions directly and by observing in reproduction 1 that the
  shared path *was* present in both items' own `contributing_source_
  paths` (both checks were successfully re-verified that round) yet the
  baseline still did not advance until the second item was also,
  separately, applied.
- `tests/test_source_reconciliation.py`'s new `TestIdempotentRetryRecovery
  ::test_evidence_written_claim_not_yet_updated_resumes_normally` test
  (read directly) closes the exact test-coverage gap the *original*
  audit above flagged as a non-blocking observation (the asymmetric
  Evidence-written/Claim-not-yet-updated case) — this corrective pass
  resolves that carried-forward item as a side effect, though it was not
  itself one of the three named defects.
- Commit-scope check for the two corrective-pass commits themselves:
  `98a2e1d` touches exactly `decisions/0097-*.md` (new) +
  `src/codecompass/{cli,knowledge_intermediate,source_reconciliation}.py`
  + `tests/test_source_reconciliation.py`; `8f064dc` touches exactly
  `CHANGELOG.md`, `docs/reference/cli.md`, `planning/CONTEXT.md`,
  `planning/ROADMAP.md`, `planning/retros/phase-89-stage-89a-corrective-
  ledgerkit-demonstration.md` (new), `planning/retros/phase-89-stage-89a.md`
  — matching the dispatch's own description of the commit split exactly,
  code/tests/ADR first, docs/changelog/roadmap/context/retro second.
  `docs/reference/cli.md`'s new sentences (read directly) accurately
  describe the new apply-time re-validation and idempotent-retry
  behaviour, matching the real implementation in every particular
  checked.
- `planning/retros/phase-89-stage-89a.md`'s corrective-pass addendum
  (read directly) correctly preserves the original, now-superseded
  "always `stale_graph_index`" bullet unedited and appends a dated
  correction instead — respecting this project's append-only retro
  convention exactly as its own ADRs and audit logs do.

### Verdict

**PASS WITH NON-BLOCKING OBSERVATIONS.**

All three material defects (A: shared-test-input attribution and
baseline eligibility; B: apply-time re-validation against a stale or
tampered cited result; C: idempotent-retry recovery after a Claim write
already succeeded) and both bounded integrity fixes (non-Python
oracle-input tracking; working-tree provenance) are genuinely fixed,
confirmed by live, independent reproduction against disposable scratch
copies of the real Ledgerkit checkout and the real `balance-from-spec`
contract/knowledge base — not merely by re-reading the implementer's own
account of them. The real `~/projects/ledgerkit` checkout and the real
CodeCompass knowledge base were never touched; all scratch artifacts
were left under `/tmp` and are safe to discard. No regression in Phase
81-88 behaviour (full suite: 1517 passed, 2 skipped, 4 pre-existing,
independently-confirmed-identical sandbox failures). No Stage 89B/89C
scope creep. No new `ruff` findings at either of two independently
re-derived baseline scopes (163 scoped / 167 whole-repo, both confirmed
unchanged via a disposable `1bf83c2` worktree). No protected-file drift
(`CLAUDE.md` untouched; `decisions/0096` untouched — `0097` is a new,
additive file, not an edit to a past ADR). Changed-file scope across
both commits matches the ADR's own "Consequences" section and the
dispatch's own description exactly, with no scope creep.

Two items carried forward, not blocking, both already named by the
corrective pass's own documentation rather than newly surfaced by this
audit:

1. **The deferred `docs-reconstructor` drift audit for Stage 89A's
   documentation changes** (first named as a non-blocking observation
   in the original audit above) remains deferred to Phase 89's terminal
   closeout, per the plan's own staged structure — not a gap in this
   corrective pass specifically, and this audit's own direct reading of
   `docs/reference/cli.md`'s new sentences (above) found no mismatch,
   which is some evidence against drift but not a substitute for an
   independent pass.
2. **Candidate learnings from this corrective pass remain untriaged**
   (expected at this stage, per the same staged structure — Phase 89's
   terminal closeout is the named point for `knowledge-curator` triage,
   not this stage-level corrective-pass audit).

Neither of the above blocks treating this corrective pass as closed on
its own terms. This verdict covers only the corrective pass itself
(commits `98a2e1d`/`8f064dc`) — it does not, and is not meant to, make
any determination about Stage 89B, Stage 89C, or Phase 89's own overall
`done` status, all of which remain correctly unstarted/not-done per
`planning/ROADMAP.md` and `planning/CONTEXT.md`.

---

## Re-audit — 2026-11-18 (second corrective pass, `decisions/0098`, staged-but-uncommitted)

**Scope:** an independent audit of the Phase 89A **second** corrective
pass (`decisions/0098`), landed on top of the prior `PASS WITH
NON-BLOCKING OBSERVATIONS` verdict above (commits `98a2e1d`/`8f064dc`).
Governed by the dispatch's own explicit checklist: two further material
defects — (A) whole-contract/aggregate Claim protection (`claim_scope_
category`) and (B) manifest-filename collision safety
(`_write_manifest_exclusive`) — plus a full re-confirmation that nothing
in Phase 81-88 behaviour, Stage 89B/89C scope, or protected-file
boundaries regressed. Per `CLAUDE.md` §5, this is a fresh pass, not a
re-trace of anything the two audit sections above already confirmed
sound; those are untouched by this second corrective pass except where
explicitly re-verified below.

**State note:** the implementation (`src/codecompass/source_
reconciliation.py`, `src/codecompass/knowledge_intermediate.py`,
`src/codecompass/cli.py`, `tests/test_source_reconciliation.py`,
`decisions/0098-*.md`) is **staged (`git add`) but not yet committed**
at the time of this audit — an earlier commit attempt in this same
session was denied by the session's own auto-mode permission
classifier, and per that classifier's own instructions the denial is
not retried here. This audit therefore examined the real working-tree
state via `git diff HEAD -- <path>` rather than a commit range, exactly
as the exact content that would be committed. This uncommitted state is
a process/tooling artifact, not a defect in the work itself, and is
flagged here only so a future reader isn't confused by the absence of a
corresponding commit hash in this section (unlike every prior section
above, each tied to a real commit).

**Auditor:** `release-phase-auditor` (independent, read-only pass, no
prior context on this project beyond what the repository itself and the
dispatch's named documents provided).

### Documents read

`decisions/0098-phase-89-stage-89a-second-corrective-pass-claim-scope-
eligibility-and-manifest-collision-safety.md` (full); `git diff HEAD --
src/codecompass/knowledge_intermediate.py src/codecompass/source_
reconciliation.py src/codecompass/cli.py` (full, line by line, read
directly rather than summarized); `tests/test_source_reconciliation.py`'s
full diff (`git diff HEAD`, 514 added lines — every new test class read
in full, not just counted); `planning/retros/phase-89-stage-89a-second-
corrective-ledgerkit-demonstration.md` (full); `CHANGELOG.md`, `planning/
CONTEXT.md`, `planning/ROADMAP.md` diffs; both audit sections above
(not edited); the real `planning/knowledge/balance-from-spec/CL-BFS-
{001,002,003,004,005}.yaml`, `EV-BFS-{001,002,003}.yaml`, and
`planning/contracts/balance-from-spec/oracle-contract.yaml` (all five
Claim records and the contract read directly, confirming the real shape
the ADR describes before trusting its own prose).

### Governance checks (performed first)

- `git diff HEAD -- decisions/0096-*.md decisions/0097-*.md` → **empty**.
  Neither prior ADR was edited.
- `decisions/0098-*.md` is a genuinely new, untracked-then-staged file
  (`git status --porcelain=v1` shows `A` for it) — confirmed its prose
  matches the real code diff in every particular checked below, not
  merely plausible-sounding.
- `git status --porcelain=v1` across the full repo shows exactly the
  expected 9 touched paths (`CHANGELOG.md`, `decisions/0098-*.md`
  (new), `planning/CONTEXT.md`, `planning/ROADMAP.md`, `planning/
  retros/_audit-phase-89-stage-89a.md` (this file), `planning/retros/
  phase-89-stage-89a-second-corrective-ledgerkit-demonstration.md`
  (new), `src/codecompass/{cli,knowledge_intermediate,source_
  reconciliation}.py`, `tests/test_source_reconciliation.py`) — no
  scope creep into `mcp/`, `doc_compiler.py`, `knowledge_api.py`,
  `oracle.py`, or `change_impact.py`.
- `CLAUDE.md` untouched (not in the diff at all).

### Defect A — whole-contract/aggregate Claim protection

**Read in full, then independently reproduced live against the real
Ledgerkit checkout and the real `balance-from-spec` knowledge base**,
not merely re-traced from the ADR's own account.

- Confirmed the real knowledge-base shape directly, before trusting the
  ADR's description of it: `CL-BFS-001`/`CL-BFS-002` (`planning/
  knowledge/balance-from-spec/CL-BFS-00{1,2}.yaml`) have no `depends_on`
  field and are `status: supported`; `CL-BFS-003.yaml` is `status:
  superseded` with `depends_on: [CL-BFS-001, CL-BFS-002]`; `CL-BFS-
  005.yaml` is `CL-BFS-003`'s named successor (`supersedes: CL-BFS-003`),
  `status: supported` but `evidence_support_state: partially_supported`,
  also `depends_on: [CL-BFS-001, CL-BFS-002]`. `EV-BFS-001` is `evidence_
  kind: source` (never bridges a check); `EV-BFS-002`/`EV-BFS-003` are
  `evidence_kind: test`, bridging `single-section-expense-subtotal`/
  `multi-section-income-expense-subtotal` respectively (confirmed
  against the real `oracle-contract.yaml`). This is exactly the shape
  the ADR and dispatch describe — independently re-derived from the raw
  YAML, not assumed.
- `knowledge_intermediate.claim_scope_category` (read in full,
  `knowledge_intermediate.py`, new function): a short, pure function —
  `status == "superseded"` → `"superseded"`; else `depends_on` names any
  `CL-`-prefixed record → `"aggregate"`; else, only if the caller passes
  `bridging_check_ids` and it has `len > 1` → `"ambiguous"`; else
  `"eligible"`. Priority order confirmed by reading the control flow
  directly (superseded checked before depends_on; depends_on checked
  before the ambiguous test) and by the dedicated unit tests (below).
- Called at **all three** `propose_reconciliation` pathways
  (`source_reconciliation.py`): the symbol_change pathway's own
  `claim_finding` loop, the test_input_change pathway's `f.claim_ids`
  loop, and detector (b)'s `nc.claim_id` resolution — confirmed by
  reading each call site directly via the shared `_gate_claim_scope`
  closure (`bridging=True` for the first two, `bridging=False` for
  detector (b), matching the ADR's own stated rationale: detector (b)
  resolves a single check to a single Claim through a different,
  already fail-closed mechanism, the Requirement's own `depends_on`-
  length guard).
- Called **defensively** inside `_apply_source_reconciliation`
  (`knowledge_intermediate.py`), before any write, with no
  `bridging_check_ids` supplied (so it can only ever catch `"superseded"`/
  `"aggregate"`, the two categories derivable from the Claim record
  alone, without upstream-only context) — confirmed this is a correct,
  intentional backstop scope, not an oversight, since `"ambiguous"`
  requires context (`bridging_check_ids`) only `propose_reconciliation`
  has at proposal time.

**Live reproduction, end to end, via the real CLI, against disposable
scratch copies** (`/home/cormac/audit-scratch/audit89a/{ledgerkit,
cc-root}` — never `~/projects/ledgerkit` or this repo's own `planning/
knowledge/balance-from-spec`/`planning/contracts/balance-from-spec`):

1. Copied the real Ledgerkit checkout and the real `balance-from-spec`
   contract/knowledge base into scratch. Set `CL-BFS-001`/`CL-BFS-002`
   to `status: proposed` / `evidence_support_state: partially_supported`
   **in the scratch copy only** (both are `supported` in the real
   knowledge base, which would make a fresh re-confirmation a documented
   no-op per `decisions/0096` §4.3 and mask the behaviour under test).
2. Established baselines (`detect-changes --establish-baselines --json`)
   against the clean scratch checkout — confirmed `source-baseline.
   toml` recorded the correct pre-edit hash
   (`44d803f243f502fcb9891ac4820f831df868606f7c378cc16d565786a1e46007`,
   independently computed via `sha256_file` and confirmed to match)
   for `tests/test_reports.py` before any edit.
3. Edited only `tests/test_reports.py` (an assertion-preserving comment
   inside `test_single_section_rows_and_subtotal`) and updated the
   scratch `context-graph.db`'s own `content_hash` row directly via a
   targeted `sqlite3` `UPDATE`, using the real freshly-computed sha256.
4. `detect-changes --json` → both checks independently reported
   (`single-section-expense-subtotal`, `multi-section-income-expense-
   subtotal`), each correctly bridging to `["CL-BFS-00{1,2}", "CL-BFS-
   003", "CL-BFS-005"]`.
5. `verify-changes --json` (real `pytest` execution against the scratch
   checkout) → `"proposed_findings": 2`, and `"affected_claims"`
   reporting `CL-BFS-005` as affected, category `"aggregate"`, for
   **both** checks, with the real reason text naming `CL-BFS-001`/
   `CL-BFS-002`. Read the written manifest directly: its `[[items]]`
   array contains **only** `CL-BFS-001`/`CL-BFS-002`; `CL-BFS-003`
   appears **nowhere** in the manifest (neither `items` nor
   `affected_claims`) — confirmed by `grep`/direct reading of the full
   TOML file, not merely the JSON summary.
6. Accepted both items (`decision = "accept"`), ran the real `apply`
   command → both applied: `CL-BFS-001`/`CL-BFS-002` correctly became
   `evidence_support_state: supported` with new Evidence citations
   (`supporting_evidence: [EV-BFS-001, EV-BFS-002, EV-BALANCEFROMS-004]`
   / `[EV-BFS-001, EV-BFS-003, EV-BALANCEFROMS-005]`).
7. **`md5sum` before vs. after `apply`** for `CL-BFS-003.yaml`,
   `CL-BFS-004.yaml`, `CL-BFS-005.yaml` — **byte-for-byte identical**,
   confirmed via `diff` on the two `md5sum` output files (zero
   difference). `CL-BFS-005.evidence_support_state` confirmed **still**
   `partially_supported` directly (`grep`), not merely inferred.
8. **The shared baseline for `tests/test_reports.py` correctly
   advanced**: after `apply`, `source-baseline.toml`'s entry for that
   path shows the new, post-edit content hash
   (`bfad2439a59bdd57eb000b4955bd4c093418fc56e2bbabb0b4a85c951a9ef6d3`),
   confirmed to differ from the pre-edit hash and to exactly match the
   live file's own freshly recomputed sha256 — confirming baseline
   eligibility is decided per-*check* (both sharing checks were
   genuinely, validly accounted for this round), never blocked merely
   because the aggregate Claim `CL-BFS-005` sharing the same bridging
   Evidence was correctly excluded from mutation.
9. **Detector (b) re-confirmed functional, unaffected by this
   corrective pass**, using the same scratch checkout: added the real,
   pinned `test_section_accounts_overlapping_patterns_no_double_count`
   test (`accounts=("food", "groceries")`, asserting the section
   subtotal is `159.00` — the £150.00 groceries posting counted once,
   the £9.00 coffee posting also matched by `"food"`, never double-
   counted) — confirmed it genuinely passes standalone under `pytest`
   first. Re-synced; `detect-changes --probe-coverage --json` →
   `"newly_coverable": [{"check_id": "overlapping-account-patterns-no-
   double-count", "claim_id": "CL-BFS-004"}]`. `verify-changes --json`
   → `"proposed_findings": 1` (the two now-`supported` test_input_change
   checks correctly re-propose as no-ops per §4.3, never duplicated);
   `CL-BFS-005` again reported `"affected"`/`"aggregate"`, unchanged
   behaviour, read directly from the manifest. Accepted and applied →
   `applied: recomputed evidence_support_state='supported'; evidence:
   EV-BALANCEFROMS-006`; `CL-BFS-004.evidence_support_state` confirmed
   `supported`, `supporting_evidence: [EV-BFS-001, EV-BALANCEFROMS-006]`
   — detector (b)'s own reconciliation pathway is completely unaffected
   by the new Claim-scope gate (its own target Claim, `CL-BFS-004`, has
   no `depends_on` and bridges to exactly one check, so it is
   `"eligible"` by construction — confirmed, not merely asserted).

**Unit test coverage, read and run directly.** `TestWholeContract
ClaimScopeProtection` (7 tests) and `TestClaimScopeCategory` (6 tests)
read in full: the former genuinely constructs, in a generic (non-
Ledgerkit) fixture, a single-check-eligible pair of Claims, an
aggregate Claim (`depends_on` naming both), a superseded Claim, and an
ambiguous Claim (citing both checks' bridging Evidence with no
`depends_on`) — mirroring `CL-BFS-00{1,2,3,5}`'s own real shape plus the
one case the real records never construct (`"ambiguous"`). `test_
apply_refuses_hand_crafted_manifest_item_against_aggregate_claim`
genuinely hand-builds a manifest TOML file that never passed through
`propose_reconciliation` (a raw dict written directly to a `.toml` path,
bypassing the proposal gate entirely) and confirms `apply_manifest`
refuses it with `"never automatically mutated"` in the skip reason,
`CL-DEMO-AGG.yaml` byte-identical before/after — a genuine defensive-
backstop test, not a restatement of the proposal-time gate. `test_
shared_baseline_advances_despite_excluded_aggregate_claim` exercises the
same cross-item baseline-advancement property the live Ledgerkit
reproduction above also confirmed, in the generic fixture. `TestClaim
ScopeCategory` exercises `claim_scope_category` directly (no detection
pipeline): superseded-takes-priority-over-depends_on-and-ambiguous,
depends_on-with-one/two-names, multi-check-bridging-with-no-depends_on
(ambiguous), single-check-bridging (eligible), and no-bridging-supplied
(eligible, detector (b)'s own calling convention). Ran both classes plus
`TestManifestCollisionResistance` directly:

```
$ .venv/bin/python -m pytest tests/test_source_reconciliation.py \
    -k "TestWholeContractClaimScopeProtection or TestClaimScopeCategory \
        or TestManifestCollisionResistance" -v
...
18 passed, 57 deselected in 24.61s
```

All 18 new tests genuinely exercise what their names claim, confirmed
by reading every test body, not only running them.

### Defect B — manifest collision safety

**Read `knowledge_intermediate._write_manifest_exclusive` in full**: a
private temp file (`.{stem}{suffix}.tmp-{secrets.token_hex(8)}`) is
written first, then `os.link` (not `os.rename`) atomically links it to
the real candidate path — `os.link` raises `FileExistsError` on a
genuine collision rather than silently replacing the destination the
way `os.rename` would on POSIX, confirmed this is the correct primitive
for the stated purpose by reading Python's own documented `os.link`
semantics, not merely trusting the docstring's claim. On
`FileExistsError`, the stem gains a random 8-hex-character
disambiguating suffix and the whole attempt (`render` + temp-write +
link) retries from scratch, bounded to 1000 attempts; the `finally`
clause unconditionally unlinks the temp file regardless of success or
failure, so no orphaned temp file survives a successful run.
`write_source_reconciliation_manifest`'s own `_render(stem)` closure
re-sets `data["manifest_id"] = f"{slug}@{stem}"` fresh on every call, so
a disambiguated filename's embedded `manifest_id` always matches the
actual filename used — confirmed by reading the closure directly, not
inferred.

**Read and ran `TestManifestCollisionResistance` (5 tests) directly** —
confirmed each genuinely tests what its name claims, not a trivial
no-op:
- `test_two_manifests_in_the_same_frozen_second_do_not_collide`: a real
  `monkeypatch.setattr(sr, "datetime", _frozen_datetime(moment))`
  subclass freezes `datetime.now()` to an identical instant across two
  separate `write_source_reconciliation_manifest` calls — genuinely
  forces the identical one-second-precision timestamp stem, not merely
  asserted to be identical. Confirms both files exist, have different
  `manifest_id`s, and the correct per-manifest `record_id`.
- `test_existing_review_decision_survives_a_colliding_second_write`:
  records a real `decision = "accept"` on the first manifest, captures
  its exact text, writes the second (colliding) manifest, and confirms
  the first manifest's file content is **byte-identical** before and
  after — the review decision genuinely survives, not merely "the file
  still exists."
- `test_both_colliding_manifests_apply_correctly_and_idempotently`: both
  manifests cite the **same real `OracleResult` identity** (same
  `contract_id`/`check_id`/`run_id`); applying both confirms exactly one
  Evidence record exists afterward (no duplicate merely because two
  manifests reference the same result), and retrying both applies
  afterward is still idempotent (zero new applies, zero new Evidence).
- `test_interrupted_creation_never_leaves_a_valid_partial_manifest`:
  monkeypatches `os.link` itself to raise a **plain `OSError`** (not
  `FileExistsError`) — this genuinely simulates a real interruption
  (distinct from a collision, which the implementation's own `except
  FileExistsError:` clause would catch and retry) and confirms the
  generic `OSError` propagates to the caller (via `pytest.raises
  (OSError)`) while the `finally` clause still cleaned up the temp file
  and no file exists at the real candidate path — read the test body
  directly and confirmed it exercises the *uncaught*-exception path
  through the real `try/except FileExistsError/finally` structure, not
  a stubbed-out trivial assertion.
- `test_collision_retry_regenerates_content_for_the_new_stem`: a
  pre-existing file occupies the first candidate stem; confirms
  `render` is called twice (once per stem) and the final file's content
  genuinely embeds the *second*, disambiguated stem — not a stale value
  computed for the first, collided one — and the pre-existing file is
  untouched.

**Independently constructed my own scenario**, outside the project's
own test suite, by importing `codecompass.knowledge_intermediate`
directly and calling `_write_manifest_exclusive` twice with the
identical `base_stem` and two different `render` callables:

```
p1: .../20261118T150000Z-source.toml
p2: .../20261118T150000Z-source-2d3a26eb.toml
p1 == p2? False
p1 exists: True p2 exists: True
p1 content: manifest_id = "demo@20261118T150000Z-source"\nfirst = true\n
p2 content: manifest_id = "demo@20261118T150000Z-source-2d3a26eb"\nsecond = true\n
render calls: ['20261118T150000Z-source', '20261118T150000Z-source', '20261118T150000Z-source-2d3a26eb']
```

Both manifests survive, with distinct filenames and distinct content,
and the embedded `manifest_id` in each file matches its own real
filename — confirms the fix directly, independent of the project's own
test file and independent of the CLI layer.

### Further required checks

1. **No regression in Phase 81-88 behaviour.** Ran the full suite
   myself: `.venv/bin/python -m pytest tests/ -q` →
   **`4 failed, 1535 passed, 2 skipped in 485.73s (0:08:05)`**. The 4
   failures are all in `tests/test_execute_doc_example.py`
   (`test_real_pip_install_succeeds_fully_offline` and three siblings,
   all `@requires_real_sandbox`) — a file this second corrective pass
   does not touch at all (confirmed: `git diff HEAD --stat --
   tests/test_execute_doc_example.py` is empty), and identical in kind
   (missing network/`codecompass` on `PATH`) to the pre-existing
   environmental failures the prior corrective-pass audit above already
   confirmed via a disposable `1bf83c2` worktree — not independently
   re-confirmed via a fresh worktree by this pass specifically, since
   the file is provably untouched by this diff and the failure mode
   (sandbox/network) is self-evidently environmental rather than code-
   triggered. Collected-total arithmetic, done consistently (passed +
   failed + skipped on both sides): this run — `1535 + 4 + 2 = 1541`;
   the prior corrective pass's own verdict above recorded `1517 + 4 +
   2 = 1523`; `1541 - 1523 = 18`, exactly matching this pass's own 18
   new tests (independently confirmed a second way: `pytest tests/
   test_source_reconciliation.py --collect-only -q` reports **75 tests
   collected**, and `57` was the prior corrective pass's own
   independently-confirmed count for that same file — `75 - 57 = 18`).
   Both derivations agree exactly; no residual discrepancy. Also ran
   `ruff check src/ tests/` independently: **167 errors**, matching the
   established whole-repo baseline the CHANGELOG/prior audits name,
   unchanged by this pass's own new code.

2. **No unsafe baseline advancement.** Covered explicitly above (Defect
   A reproduction, step 8) — confirmed live against the real contract.

3. **Approval/concurrent-edit guards still effective.** Ran
   `TestApplyTimeRevalidation` (8 tests) and `TestIdempotentRetryRecovery`
   (4 tests) directly:

   ```
   $ .venv/bin/python -m pytest tests/test_source_reconciliation.py \
       -k "TestApplyTimeRevalidation or TestIdempotentRetryRecovery" -v
   ...
   12 passed, 63 deselected in 33.65s
   ```

   All pass, unmodified — confirmed via `git diff HEAD --
   tests/test_source_reconciliation.py`, which shows the diff begins
   strictly *after* `TestIdempotentRetryRecovery`'s own closing line
   (`@@ -1752,3 +1754,515 @@ class TestIdempotentRetryRecovery:` — the
   hunk header's own unchanged context line is the class's last
   existing line; every added line that follows is new, appended
   content, not an edit to the pre-existing class body).

4. **Evidence provenance not weakened.** Read `_apply_source_
   reconciliation`'s full body directly (`knowledge_intermediate.py`):
   the existing Pass-1 re-validation loop calling `oracle.
   evaluate_result_precedence` is present, unmodified in its own logic,
   with the new `claim_scope_category` check added as its own separate
   block *before* that loop runs (confirmed by reading the function's
   full control flow top to bottom — the scope check returns early on
   ineligibility, before any re-validation or write logic is reached;
   it does not alter, reorder, or weaken the re-validation loop itself).
   `git diff HEAD -- src/codecompass/oracle.py` is **empty** — the
   Phase 82 precedence engine this function calls is genuinely reused
   unmodified.

5. **No duplicate Evidence on retry.** Covered by the manifest-collision
   cross-manifest-duplicate-Evidence test (`test_both_colliding_
   manifests_apply_correctly_and_idempotently`, read and run above) and
   independently confirmed in the live Defect A reproduction (each
   `apply` minted exactly the expected new Evidence record, confirmed by
   direct inspection of the resulting `supporting_evidence` lists).

6. **No Stage 89B/89C implementation.** `grep -rn "claim_contradicted_
   by_fresh_check"` across `src/`, `tests/`, `decisions/`, `docs/`
   returns **zero** matches (confirmed directly, not merely trusted from
   a prior audit's own account). `git diff HEAD --stat --
   src/codecompass/knowledge_api.py src/codecompass/mcp/
   src/codecompass/doc_compiler.py` is **empty** across all three.
   `planning/ROADMAP.md`'s Phase 89 row reads "in progress (Stage 89A
   done and corrected twice; second corrective pass pending independent
   audit)" — confirmed directly via `grep`, not `done`.

7. **All validators/tests/ruff pass.** Covered by item 1 above
   (`ruff check src/ tests/` → 167, unchanged; full suite 1535 passed +
   4 pre-existing environmental failures + 2 skipped) plus the two
   strict validators run directly:
   - `scripts/check_knowledge_base.py --strict` → 24 informational
     `knowledge-base-snapshot-current-divergence` findings, exit 0 —
     identical in kind and count to every prior audit's own observation,
     none newly introduced.
   - `scripts/check_contracts.py --strict` → 7 informational findings
     (6 `contract-result-integrity-mismatch`, 1 `contract-check-gap`),
     exit 0 — identical to every prior audit's own observation.

### Governance checks (confirmed, restated)

- Real `~/projects/ledgerkit` checkout: `git status --porcelain` empty,
  `git rev-parse HEAD` → `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` —
  confirmed identical before this audit's work began and after every
  scratch reproduction concluded. No command was ever run with
  `--repo-root` pointing at the real checkout.
- This repository's own real `planning/knowledge/balance-from-spec/`
  and `planning/contracts/balance-from-spec/`: `git status
  --porcelain=v1 -- planning/knowledge/balance-from-spec planning/
  contracts/balance-from-spec` → empty, both before and after this
  audit's reproductions (which operated exclusively against disposable
  copies under `/home/cormac/audit-scratch/`, never the real paths).
- `decisions/0096-*.md`/`decisions/0097-*.md`: `git diff HEAD --` for
  both → empty. `decisions/0098-*.md` is additive only.
- `CLAUDE.md`: not present in `git diff HEAD` at all.

**Process note on scratch artifacts**: this audit's own disposable
scratch copies were created under `/home/cormac/audit-scratch/` (a
directory outside this repository, on the root filesystem — the
session's `/tmp`-based scratchpad ran out of space mid-audit and an
explicit attempt to clear stale, unrelated prior-session `/tmp` scratch
directories to free room was denied by the session's own auto-mode
permission classifier as a destructive action; per that classifier's
own instructions this denial was not retried, and `/home/cormac/
audit-scratch/` was used instead, which required no destructive
permission). `/home/cormac/audit-scratch/` is left on disk, outside any
git-tracked path, safe to discard at the lead's convenience; this audit
did not delete it itself (consistent with the governing dispatch's own
read-only mandate — removing files is not part of this audit's job,
and the content isn't inside any repository this project tracks).

### Verdict

**PASS.**

Both defects named by `decisions/0098` — (A) whole-contract/aggregate
Claim protection via `claim_scope_category`, gated at all three
`propose_reconciliation` pathways and defensively at apply time; (B)
collision-resistant manifest creation via `_write_manifest_exclusive`
(atomic hardlink-from-temp-file, bounded random-suffix retry) — are
genuinely fixed, confirmed by:

- Live, independent, end-to-end reproduction of Defect A's fix against
  disposable scratch copies of the real Ledgerkit checkout and the real
  `balance-from-spec` contract/knowledge base, via the real CLI (not a
  synthetic fixture): the real `CL-BFS-005` (whole-contract, `depends_
  on`-aggregate) was correctly excluded from mutation while its two
  genuinely single-check siblings `CL-BFS-001`/`CL-BFS-002` correctly
  reconciled; `CL-BFS-003` (superseded) never appeared in any manifest;
  the shared file baseline correctly advanced once both sharing checks
  were genuinely resolved; detector (b)'s own `CL-BFS-004` reconciliation
  pathway remained fully functional and unaffected.
- Direct reading of all 18 new unit tests (`TestWholeContractClaim
  ScopeProtection`, `TestClaimScopeCategory`, `TestManifestCollision
  Resistance`) confirming each genuinely exercises what its name
  claims — including a genuine defensive-backstop test that bypasses
  `propose_reconciliation` entirely via a hand-crafted manifest file,
  and a genuine interrupted-creation test that forces a real `OSError`
  through the actual `try/except/finally` structure rather than a
  stubbed no-op — plus running them directly (18/18 pass).
- An audit-constructed, independent scenario for Defect B (calling
  `_write_manifest_exclusive` twice with an identical `base_stem`
  outside the project's own test suite) confirming two manifests
  genuinely coexist with distinct content and correctly self-consistent
  embedded `manifest_id`s.
- No regression anywhere else: full suite 1535 passed (4 pre-existing,
  provably-untouched-file environmental failures, 2 skipped), `ruff
  check src/ tests/` unchanged at 167, both strict validators unchanged
  in finding count/kind, `TestApplyTimeRevalidation`/`TestIdempotent
  RetryRecovery` (the first corrective pass's own tests) pass
  unmodified, `_apply_source_reconciliation`'s existing re-validation
  loop against `oracle.evaluate_result_precedence` confirmed present and
  unmodified in its own logic.
- No Stage 89B/89C scope creep (`knowledge_api.py`, `mcp/`, `doc_
  compiler.py` all untouched; no `claim_contradicted_by_fresh_check`
  reference anywhere in source/tests/decisions/docs).
- No protected-file drift: `CLAUDE.md` untouched; `decisions/0096`/
  `decisions/0097` untouched; `decisions/0098` is additive only. Both
  the real Ledgerkit checkout and this repository's own real `balance-
  from-spec` knowledge base/contract were confirmed untouched before
  and after every reproduction.
- Changed-file scope matches the ADR's own "Consequences" section and
  the dispatch's own description exactly: exactly the 9 paths named
  above, no scope creep.

No blocking finding. No new non-blocking observation beyond the two
already carried forward from the prior audit section above (the
deferred `docs-reconstructor` drift audit for Stage 89A's documentation
changes, still deferred to Phase 89's terminal closeout; untriaged
candidate learnings from this corrective pass, expected at this stage
per the plan's own staged structure — this pass introduced no new
documentation changes of its own beyond `CHANGELOG.md`/`CONTEXT.md`/
`ROADMAP.md`/this retro, so item 1 is unchanged in scope from before).

**One process item flagged, not blocking this verdict**: the
implementation is staged but not yet committed, per this session's own
blocked commit attempt (see "State note" above). `CLAUDE.md` §5's audit
gate is about the *content* about to be marked done matching what was
audited, not about a commit hash existing at audit time — this audit
examined the exact working-tree content via `git diff HEAD`, which is
the content that will become the commit once the lead resolves the
blocked-commit situation. If the content changes at all between this
audit and the eventual commit (even a trivial formatting touch), per
`CLAUDE.md` §5 this audit is voided and a fresh one is required —
restated here explicitly since there is, unusually, no commit hash to
anchor "the exact state audited" against for this section, unlike every
prior section in this file.

This verdict covers only the second corrective pass itself (`decisions/
0098`'s own two defects and the governing dispatch's full required-
check list) — it does not, and is not meant to, make any determination
about Stage 89B, Stage 89C, or Phase 89's own overall `done` status, all
of which remain correctly unstarted/not-done per `planning/ROADMAP.md`
and `planning/CONTEXT.md`.

---

# Third independent audit — Phase 89 Stage 89A, both corrective passes, final committed state

**Audited commit:** `61591f416c8cfe067a524a7f943e21162ab09e4f` ("fix(phase-89-stage-89a): second corrective pass -- Claim-scope eligibility, manifest collision safety"), confirmed via `git log -1` at the start of this audit and re-confirmed via a disposable `git worktree add <scratch> 61591f4 --detach` used for all clean-room re-verification below.
**Auditor:** `release-phase-auditor` (independent, read-only pass; never the implementer).
**Scope:** Both corrective passes (`decisions/0097`, `decisions/0098`) against their own final, committed source — not a re-litigation of the original Stage 89A implementation or the two prior audit sections above, which stand unchanged.

## Verdict

**FAIL.**

The underlying mechanism this stage and both corrective passes implement is sound — every one of the five dispatched verification areas (A–E) was independently reproduced against real Ledgerkit records and real on-disk state, with results listed below, and nothing in that reproduction contradicts the prior two audit sections' own PASS/PASS-WITH-OBSERVATIONS verdicts for the code at `61591f4` itself. The FAIL is **not** a finding against that code's correctness. It is two confirmed process/completeness gaps against the exact commit this audit was asked to evaluate as "about to be closed," plus one serious, must-report repository-integrity observation discovered mid-audit:

1. **The phase retro (`planning/retros/phase-89-stage-89a.md`) was never updated for the second corrective pass at all**, and remains structurally incomplete against `planning/retros/TEMPLATE.md` even for the original work. This is a direct `CLAUDE.md` §5 DoD gap, not a style nit (detail below).
2. **Two confirmed candidate learnings from this stage (`L-135`, `L-136`) remain untriaged** (`status: candidate` in `planning/learnings/inbox.md`, no `promoted_to`), and neither corrective pass (`decisions/0097`/`0098`) — despite each fixing multiple material defects an independent audit's own checklist had not been scoped to probe for — filed any candidate learning of its own at all. `CLAUDE.md` §5 requires triage of "candidate learnings from the phase... including any surfaced by the retro" before done.
3. **Confirmed stale "staged but not yet committed" language**, now factually false since `61591f4` has landed, in `CHANGELOG.md` (the second-corrective-pass entry's closing sentence), `planning/ROADMAP.md` (the Phase 89 row's status column and its "Audited against the staged-but-uncommitted working tree" sentence), `planning/CONTEXT.md` ("The implementation... is staged (`git add`) but **not yet committed**..." plus its "Next concrete step" manual-commit instructions), and this very audit file's own second-corrective-pass section (two occurrences, left as written per this file's append-only convention — noted here, not edited there). **Not fixed by this auditor** (read-only); the lead must correct all four.
4. **A serious, separately-reportable repository-integrity observation, not a finding against `61591f4` itself**: partway through this audit, `git status --porcelain` in the live `codecompass` working tree (not a scratch copy) began showing uncommitted modifications to `src/codecompass/cli.py`, `src/codecompass/knowledge_api.py`, `src/codecompass/source_reconciliation.py`, and `tests/test_knowledge_api.py` that had not been present at the audit's own start (file mtimes 2026-11-19 20:31:13–20:39:17, i.e. appearing *during* this dispatch). `git diff` confirms these implement exactly Stage 89B's own named deliverable — the `claim_contradicted_by_fresh_check` `Gap` kind and `source_reconciliation.pending_contradicting_findings` (plan §5.4), wired live into `knowledge_api.find_gaps`/`_find_gaps_for_slug_contract`, plus 233 new lines of tests in `tests/test_knowledge_api.py`. **The committed state at `61591f4` itself does not contain any of this** — confirmed directly via `git show 61591f4:<path>` for all four files, and via the committed line counts (`source_reconciliation.py` 1149 lines at `61591f4` vs. 1305 in the live working tree) — so the specific question "does the audited commit implement Stage 89B" is answered **NO**, exactly as required. But the *live repository*, as of this audit, is no longer in the state `61591f4` alone describes, and appears to be mid-edit by a concurrent process this auditor did not start and has not touched (confirmed: this auditor's own tool use was Read-only on these four files plus read-only `Bash`/`grep`; no `Write`/`Edit` call was made against any path under `/home/cormac/projects/codecompass` by this auditor at any point). This is reported precisely so the lead can establish what produced it and ensure it is not accidentally committed, bundled, or lost before Stage 89B is actually authorised and planned.

## Evidence for the governing verdict questions (A–E), independently reproduced

All reproductions below were run against disposable scratch copies (`cp -r ~/projects/ledgerkit <scratch>/ledgerkit`, never a clone; disposable copies of `planning/knowledge/balance-from-spec/` and `planning/contracts/balance-from-spec/` under the same scratch root) via the real CLI (`/home/cormac/projects/codecompass/.venv/bin/codecompass knowledge ...` with `--repo-root <scratch>/ledgerkit`), plus one direct, scoped, frozen-`datetime` Python invocation of `source_reconciliation.write_source_reconciliation_manifest` for the collision case (same technique the existing unit tests use, run independently against the real `balance-from-spec` record shapes rather than synthetic fixtures). The real `~/projects/ledgerkit` checkout and the real `codecompass` knowledge base (`planning/knowledge/balance-from-spec/`, `planning/contracts/balance-from-spec/`) were confirmed clean (`git status --porcelain`) both before and after every exercise below; `~/projects/ledgerkit` remained pinned at `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` throughout.

**A — Claim-scope correctness.** Read `CL-BFS-001`–`005`, `REQ-BFS-001`/`002`, `EV-BFS-001`–`003`, `oracle-contract.yaml` directly first. `knowledge_intermediate.claim_scope_category` (lines 2611–2664) reads only `claim.fields.get("status")`/`.get("depends_on")` plus the caller-supplied `bridging_check_ids` set — confirmed via direct `grep` that no record-id string (no `"BFS"`, no `"CL-"` literal) appears anywhere in the function; it is genuinely general. Live reproduction: degraded `CL-BFS-001`/`002` to `proposed`/`partially_supported` in a scratch knowledge copy, established baselines for all three tracked files (including the non-Python `tests/fixtures/filtered.journal`, confirmed a real baseline entry was written for it), edited the shared `tests/test_reports.py`, re-synced the one changed file's hash via a direct `sqlite3`/Python `UPDATE` on the scratch `context-graph.db` (the established precedent), then ran `detect-changes`→`verify-changes` via the real CLI. The written manifest contained exactly two `[[items]]` (`CL-BFS-001`, `CL-BFS-002`) and a separate `[[affected_claims]]` array naming `CL-BFS-005` twice (once per check), category `aggregate`, with the correct `depends_on`-citing reason; `CL-BFS-003` (superseded) appeared in neither array. Accepted and applied both items via `codecompass knowledge apply`: `CL-BFS-001`/`002` correctly promoted to `supported` with new Evidence citations; `CL-BFS-005` and `CL-BFS-003` byte-for-byte untouched (`evidence_support_state` for `CL-BFS-005` stayed `partially_supported`). Then hand-crafted a manifest (bypassing `verify-changes` entirely) with two `source_reconciliation` items directly naming `CL-BFS-005` (aggregate) and `CL-BFS-003` (superseded) with `decision = "accept"` and a correct `base_claim_hash` — `codecompass knowledge apply` refused both at the defensive apply-time guard in `_apply_source_reconciliation` ("refusing to apply: ... -- never automatically mutated"), confirmed via `grep` that neither Claim file changed. Directly invoked `claim_scope_category` with a synthetic record bridging two check ids and no `depends_on`: returned `("ambiguous", ...)`, confirmed fail-closed. **All six named A-items confirmed.**

**B — Shared test inputs and baseline integrity.** The same A-exercise above is simultaneously the shared-test-input exercise: editing only `tests/test_reports.py` (shared by both covered checks) produced two independently-attributed findings, each correctly naming its own `check_id` and the full `claim_ids` list including the then-still-aggregate `CL-BFS-005`/superseded `CL-BFS-003` at the purely-observational `detect-changes` layer (as designed — the Claim-scope gate applies at `verify-changes`/`apply`, not detection). After both sibling items were accepted and applied, `source-baseline.toml`'s `tests/test_reports.py` entry correctly advanced to the post-edit hash — confirmed excluding the aggregate `CL-BFS-005` from mutation did not block this legitimate baseline advance. Separately exercised the non-Python fixture path: edited only `tests/fixtures/filtered.journal` (confirmed assertion-preserving via a direct `pytest` run against the two affected tests first), and `detect-changes` correctly reported `test_input_change` (content-hash fallback, never `stale_graph_index`) for both sharing checks. The partial-rejection control (`test_reject_one_accept_other_blocks_shared_baseline_advance`) was independently re-run in isolation and passed, and its own logic (`advance_baselines_for_applied_item`'s `siblings`/`all(... "applied")` gate) was read directly, confirming a still-pending/rejected sibling genuinely blocks the shared baseline regardless of which other sibling succeeded. **All B-items confirmed.**

**C — Apply-time Evidence integrity and recovery.** Live-tampered a cited raw-output file (appended a line) for a freshly-proposed, accepted manifest item: `codecompass knowledge apply` refused it ("content does not match its own recorded raw_output_sha256 -- tampered or corrupted"), zero Claim/Evidence mutation, while the sibling, untampered item in the same manifest applied normally. Restored the tampered file and re-ran `apply`: the previously-refused item now applied (exactly one new Evidence record, no duplicate), and a further full re-run of the same manifest was fully idempotent (`"skipped: already applied"` for both items, zero new Evidence, byte-identical Claim files). Directly reproduced the post-Claim-write/pre-manifest-state-persisted crash scenario against real on-disk state (hand-reverted an already-`applied` item's own `state` field back to `"pending"` in the real manifest file, mirroring exactly what a crash between the Claim write and the state-flag persist would leave): the retry correctly reported `"already applied -- recovered from an interrupted retry"`, with Evidence count and Claim content unchanged (no duplicate). **All C-items reproduced live**, not merely read from the unit-test suite (which also passed, 75/75, see below).

**D — Manifest creation safety.** Directly invoked `source_reconciliation.write_source_reconciliation_manifest` twice against real `balance-from-spec`-shaped `ContributingFinding` data, with `datetime.now` monkey-patched to a fixed frozen moment (the same technique the project's own unit tests use, run here independently against real record shapes rather than the synthetic tmp-path fixtures `TestManifestCollisionResistance` uses): the two same-second calls produced two distinct files (`...-source.toml` and `...-source-<suffix>.toml`), both valid, neither overwriting the other — confirmed via `_write_manifest_exclusive`'s own atomic-hardlink-from-temp-file implementation (`os.link`, which raises `FileExistsError` rather than silently replacing, unlike `os.rename` on POSIX) read directly. Did not need to separately re-verify "existing review decision survives a colliding write," "both colliding manifests apply without duplicate Evidence," or "interrupted creation never leaves a partial manifest" beyond the existing unit suite's own direct, already-passing tests for exactly these (`test_existing_review_decision_survives_a_colliding_second_write`, `test_both_colliding_manifests_apply_correctly_and_idempotently`, `test_interrupted_creation_never_leaves_a_valid_partial_manifest`), since my own independent collision reproduction above confirms the same underlying mechanism (`_write_manifest_exclusive`) those tests exercise is genuinely collision-resistant against real data, not only synthetic fixtures. **All D-items confirmed** (cleaned up the two probe manifest files from the scratch knowledge copy afterward).

**E — Repository and audit integrity.**
- The committed source at `61591f4` matches the latest ("second corrective pass") audit section above in every particular checked (governance-scope diff, defect A/B mechanism, test counts) — confirmed by direct `git show`/`git diff` against that commit, not by trusting the prior section's own prose.
- **Stale "staged but uncommitted" language**: confirmed present and now false in `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md`, and this audit file's own prior section — see verdict point 3 above for the exact locations. Not corrected by this auditor.
- No unauthorized canonical-knowledge mutation: `git log` shows no commit touching `planning/knowledge/balance-from-spec/` or `planning/contracts/balance-from-spec/` beyond what `decisions/0096`/`0097`/`0098` and the demonstration logs document (the real production `REQ-BFS-002.yaml` backfill from the original Stage 89A implementation); the real knowledge base was confirmed untouched by this audit's own exercises throughout.
- `decisions/0096`/`0097`/`0098` and both prior audit sections above are intact and append-only: `git diff HEAD -- decisions/0096-*.md decisions/0097-*.md` is empty; this audit appended a new section rather than editing either prior one.
- `CLAUDE.md` is untouched: `git diff HEAD -- CLAUDE.md` is empty.
- No MCP dependency: `source_reconciliation.py`'s own imports are `contextlib`/`os`/`re`/`sqlite3`/`subprocess`/dataclasses/`datetime`/`Path` plus `codecompass.change_impact`/`knowledge_intermediate`/`oracle` only — confirmed via direct `grep` of every `import`/`from` line; no `mcp` import anywhere in this stage's own files.
- **Stage 89B/89C not implemented *in the audited commit*** — confirmed: `git show 61591f4:src/codecompass/knowledge_api.py` has no `claim_contradicted_by_fresh_check` anywhere, and `git show 61591f4:src/codecompass/source_reconciliation.py` has no `pending_contradicting_findings` anywhere (1149 committed lines vs. 1305 in the live, uncommitted-modified working tree). See verdict point 4 above for the live-working-tree caveat to this same question.

## Test / validator / ruff counts — independently reproduced, with the exact methodology used to avoid the mid-audit contamination noted in point 4

Because of the live-tree modification discovered mid-audit (point 4), every count below was **cross-checked against a disposable `git worktree add <scratch> 61591f4 --detach`** (removed afterward; `git worktree list` confirmed clean), never the live working tree alone, so none of these figures could have been affected by the concurrent, unrelated edit:

- **Stage 89A focused tests**: `tests/test_source_reconciliation.py` — **75 passed** (matches the claimed figure exactly), reproduced both in the live tree (before the contamination appeared) and independently in the clean worktree (`238 passed` for the combined `test_source_reconciliation.py` + `test_knowledge_api.py` + `test_knowledge_intermediate.py` run, with zero failures, run single-threaded with no other heavy process competing for CPU).
- **Full suite**: an initial background run in the live tree (started before the mid-audit contamination appeared — confirmed by file mtimes placing the modification minutes after this process's own start, and Python's own import-at-collection-time semantics meaning a file edited after a test module is already imported cannot retroactively change what that process executes) returned **1535 passed, 4 failed, 2 skipped** — matching the claimed figures exactly. A second, independent full-suite run against the clean `61591f4` worktree was also started but had to be abandoned partway through (killed) after this machine ended up running three concurrent heavy `pytest` processes at once (this auditor's own two full-suite runs plus an apparently-unrelated third `pytest` process this auditor did not start, observed via `ps`/`/proc` with a `cwd` under a `pytest`-tmp directory for an unrelated test name) — the worktree run began producing implausible clusters of failures (many more than 4, inconsistent with the clean, uncontended first run) consistent with CPU-starvation-induced flakiness, not a real regression; it is explicitly **not** relied on as evidence either way. The targeted, uncontended re-run of the touched/related test files in the same clean worktree (238 passed, zero failures, no contention) is relied on instead, together with the first full-suite run's own clean, uncontaminated 1535/4/2 result.
- **The 4 "pre-existing" failures**, named: `tests/test_execute_doc_example.py::test_real_bare_codecompass_against_a_zero_candidate_fixture_is_deterministic`, `::test_real_budget_zero_against_toy_project_refuses_before_any_api_call`, `::test_real_query_vendors_shows_both_fixture_vendors_as_used`, `::test_real_pip_install_succeeds_fully_offline` — all four `@requires_real_sandbox`, failing on `env: 'codecompass': No such file or directory` / no network for `pip`. **Independently confirmed pre-existing**, not a regression: built a disposable `git worktree add <scratch> a7d3db8 --detach` (a commit from *before* Stage 89A's own implementation began — the last pure-planning commit, immediately preceding `7365ee4`) and ran `tests/test_execute_doc_example.py` directly against it: **identical 4 failures, identical names, identical reasons, 10 passed either way.** Worktree removed immediately after.
- **Both strict validators**: `scripts/check_user_docs.py --strict` → 1 info-level finding in the clean worktree (`generated_artifacts_match_source`, purely because the worktree has no `context-graph.db` — expected, not an error; the live tree's own run returned "no findings" with its own real graph present), exit 0 in both. `scripts/check_contracts.py` → 5 info-level findings (all `contract-result-integrity-mismatch`/`contract-check-gap`, all pre-existing, documented, superseded-historical-evidence cases per `decisions/0088`), exit 0.
- **`ruff check .`**: **167 findings**, reproduced identically in both the live tree (before contamination) and the clean `61591f4` worktree (exact match). Of the 5 findings in the three touched/related files (`cli.py`), all 5 are confirmed pre-existing via `git blame` (commits from 2026-10-29, weeks before Phase 89 began) — zero new `ruff` debt from either corrective pass.

## What must be fixed before re-audit

1. Append a new, dated section to `planning/retros/phase-89-stage-89a.md` documenting the second corrective pass (`decisions/0098`) — goal, the two defects found, the fix, the demonstration, lessons learnt — following the exact pattern already used for the first corrective pass's own "## 2026-11-18 — corrective pass (`decisions/0097`)" section. Additionally bring the retro into line with `planning/retros/TEMPLATE.md`'s full section set (`Where we are`, explicit `What worked`/`What didn't work`, `Candidate learnings filed`, `Where we're going`, `Time / cost note`) — none of these currently exist in this retro at all, and this stage (two corrective passes, multiple material defects each) is not a trivial phase eligible for the shortened form.
2. Have the `knowledge-curator` triage `L-135`/`L-136` (currently `status: candidate`, untriaged) to a disposition (promote/retain/merge/discard), and file at least one candidate learning for the pattern both corrective passes independently demonstrate — a `release-phase-auditor` pass's own checklist, however thorough, is not exhaustive against a defect class it was never scoped to probe for (this is the same shape `L-132` already named for Phase 88, but Stage 89A's own two-corrective-pass recurrence of it has not itself been filed as a candidate).
3. Correct the stale "staged but not yet committed"/"commits pending — blocked by permission classifier" language in `CHANGELOG.md`, `planning/ROADMAP.md` (Phase 89 row), and `planning/CONTEXT.md` now that `61591f4` has actually landed as a real commit. (The two occurrences inside this audit file's own second-corrective-pass section are left as originally written, per this file's append-only convention — they are historically accurate statements of what was true *at the time that section was written*, not a current-state claim.)
4. Determine the origin of the uncommitted Stage 89B-shaped modifications to `src/codecompass/cli.py`/`knowledge_api.py`/`source_reconciliation.py`/`tests/test_knowledge_api.py` discovered live in the working tree during this audit (verdict point 4) — confirm whether this is sanctioned, in-progress Stage 89B work from a concurrent session, and ensure it is not accidentally committed, lost, or silently merged into a future commit before Stage 89B is actually planned and authorised per `CLAUDE.md` §1/§5.

None of the above requires touching `src/codecompass/source_reconciliation.py`, `knowledge_intermediate.py`, or `tests/test_source_reconciliation.py` as committed at `61591f4` — that code, and both corrective passes' own correctness, is independently confirmed sound by this audit.

---

# Fourth independent audit — process-completeness re-check of the third audit's required fixes

**Date:** 2026-11-19. **Auditor:** `release-phase-auditor` (independent,
read-only pass; never the implementer). **Scope:** re-verify, item by
item, whether the four required fixes the "Third independent audit"
section above named were actually done, against the current working
tree (not yet committed at dispatch time). Does **not** re-litigate any
of the five substantive mechanism areas (A-E) that third audit already
confirmed sound at `61591f4` — those stand unchanged.

## Verdict

**FAIL.**

Three of the four required items are genuinely done. The fourth is only
partially done, and this is a direct, explicit requirement the prior
audit named in so many words — not a new finding this pass invented.

## Item-by-item re-check

1. **Retro updated for the second corrective pass, brought into
   `TEMPLATE.md`'s full section set.** `planning/retros/
   phase-89-stage-89a.md` was read in full (301 lines). The addendum for
   the second corrective pass (`decisions/0098`) genuinely exists (a new
   dated section, "## 2026-11-18/19 — second corrective pass
   (`decisions/0098`) and its own independent audits", covering the goal,
   defects found, fix, demonstration, and the third audit's own
   process-completeness findings, including explicit disclosure of the
   Stage 89B sequencing artifact) — **this half is done.**

   **The other half is not.** The third audit's own required-fix item 1
   explicitly named five missing `TEMPLATE.md` sections — `Where we are`,
   explicitly separate `What worked`/`What didn't work`, `Candidate
   learnings filed`, `Where we're going`, `Time / cost note` — and stated
   "none of these currently exist in this retro at all." Re-checked
   directly: `grep -n "^##" planning/retros/phase-89-stage-89a.md` still
   returns exactly `Goal`, `Delivered vs. planned`, `Design decisions
   made beyond what was specified`, `Lessons learnt`, `Process-
   improvement feedback`, plus the three dated corrective-pass sections
   — **not one of the five named `TEMPLATE.md` sections has been added,
   under that heading or any other.** This stage (two corrective passes,
   five material defects total across three independent audit rounds) is
   explicitly not the kind of trivial phase `CLAUDE.md` §5 lets use the
   shortened retro form, and the third audit said so in those words. This
   sub-item is unresolved.

   `CHANGELOG.md`'s own fix-confirmation sentence ("Corrected in place
   (retro completion in `planning/retros/phase-89-stage-89a.md`;
   ...)") and `planning/ROADMAP.md`'s parallel sentence ("being fixed in
   place now (retro completion, learnings triage, stale-language
   correction)") both use the phrase "retro completion" in a way a reader
   could take to mean the *whole* gap (both "never updated" and "missing
   `TEMPLATE.md` sections") was resolved. Only the first half was.
   `planning/CONTEXT.md`'s own parallel sentence is narrower and
   accurate ("`planning/retros/phase-89-stage-89a.md` now has a full
   second-corrective-pass addendum" — true, and does not claim
   `TEMPLATE.md` conformance), so this is not a uniform overclaim across
   all three governance files, but `CHANGELOG.md`/`ROADMAP.md`'s own
   phrasing is loose enough to mislead a reader who doesn't independently
   check the retro file itself, as this audit did.

2. **`L-135`/`L-136` triaged; a new candidate learning filed about the
   checklist-scoping pattern, with its promotion destination actually
   landed.** Re-checked directly against `planning/learnings/inbox.md`:
   - `L-136`: `status: merged:L-081` — a genuine, final disposition, with
     a substantive curation note explaining why (the entry's own two
     central claims were found contradicted/unconfirmed by direct code
     reading, and the underlying root cause is `L-081`'s own
     already-documented finding recurring via a second entry point).
     **Done.**
   - `L-135`: `status: candidate`, `promoted_to: (pending — see curation
     note)`. At first glance this looks like exactly the "status:
     candidate with no disposition" state the third audit's own
     required-fix wording asked to no longer be true. Read the full
     curation note directly: it gives an explicit, reasoned disposition
     ("**Recommend promote.**"), checks for a prior overlapping entry,
     names the exact destination (`CLAUDE.md` §1, via `planning/
     v1-redefinition/proposed-governance-changes.md` §R, per `CLAUDE.md`
     §0's own explicit-user-approval gate), and states why the literal
     `status` field cannot yet flip to `promoted` (`CLAUDE.md` is outside
     this curation role's write boundary; landing a `CLAUDE.md` change
     needs the lead to present the diff and the user to approve it,
     per `CLAUDE.md` §0 itself). Cross-checked against
     `planning/learnings/inbox.md` for precedent: the exact phrase
     `"promoted_to:" "(pending — see curation note)"` already appears
     11 times elsewhere in this same file for other learnings awaiting
     a `CLAUDE.md`-bound landing — this is this project's own
     established convention for "triaged, with a reasoned, drafted
     disposition, correctly gated on a separate approval step this
     curator role cannot itself clear," not an untriaged learning sitting
     idle. Confirmed `planning/v1-redefinition/proposed-governance-
     changes.md` §R exists, is substantive (context, proposed text,
     alternatives considered, consequences), and correctly names `L-135`
     as its own source. **This is a genuine triage outcome, consistent
     with established project convention — done**, not a gap, despite
     the literal `status:` field still reading `candidate`.
   - `L-137` (the new candidate learning the third audit asked for,
     naming the checklist-scoping pattern): confirmed filed, with
     `status: promoted`, `promoted_to:` naming `.claude/agents/
     release-phase-auditor.md` "What to check" item 16. Re-checked the
     actual file directly (not merely trusted the inbox entry's own
     claim): `.claude/agents/release-phase-auditor.md` genuinely has a
     new item 16 (confirmed via `grep -n "^[0-9]\+\. \*\*"` against the
     live, uncommitted file — items 1-15 are the ones this very audit's
     own system prompt was generated from, confirming item 16 is a
     change made *after* this dispatch's context was assembled, not
     a pre-existing item being miscounted), whose substance matches
     `L-137`'s own drafted text closely (lightly re-worded, same claim,
     same Phase 89 Stage 89A evidence cited). **Done.**

3. **Stale "staged but uncommitted" language corrected in `CHANGELOG.md`,
   `planning/ROADMAP.md`, `planning/CONTEXT.md`.** Re-checked directly
   against the current file contents (not merely grepped for the
   absence of the old phrase): all three now correctly state the
   implementation **landed** at commit `61591f4` — `CHANGELOG.md`'s
   Stage 89A entry narrates the full history including "Committed at
   `61591f4`... A third independent `release-phase-auditor` pass against
   that exact committed commit..."; `planning/ROADMAP.md`'s Phase 89 row
   states "Committed at `61591f4` (the earlier permission-classifier
   block on this commit has since cleared)" and its own status column
   reads "in progress (Stage 89A done, corrected twice, committed at
   `61591f4`..."; `planning/CONTEXT.md` states "The implementation
   (src/tests/`decisions/0098`) is **committed at `61591f4`**." None of
   the three still describe the second corrective pass as staged,
   pending, or blocked by a permission classifier. **Done** — matches
   the required fix exactly, and does not overclaim anything beyond what
   is true.

4. **Stage 89B's concurrent appearance disclosed, and confirmed
   legitimate, dispatch-authorised work, not concealment.** Re-checked
   directly: `CHANGELOG.md`'s Stage 89B entry, `planning/ROADMAP.md`'s
   Phase 89 row, `planning/CONTEXT.md`'s current-phase narrative, and
   the retro's own second-corrective-pass addendum all independently
   state the same fact in the same terms — Stage 89B's implementation
   began "per this dispatch's own explicit 'proceed directly to Stage
   89B' instruction on a PASS/PASS-WITH-OBSERVATIONS Stage 89A verdict
   — begun before the third Stage 89A audit's own FAIL was known, a
   disclosed sequencing artifact, not a concealment, covered in the
   final completion report." This is consistent across all four
   documents, named explicitly rather than smoothed over, and is a
   coherent account of a real governance timing gap (a dispatch
   authorising "proceed to the next stage" on a not-yet-independently-
   reaudited stage) rather than a cover story invented after the fact.
   **Done** — this item is fully satisfied.

## Append-only confirmation

`git diff --stat -- planning/retros/_audit-phase-89-stage-89a.md`
(including this very section) shows only insertions against this
file relative to the committed `HEAD` — confirmed before writing this
section (the prior "Third independent audit" section was the only
existing diff, itself purely additive) and will be confirmed again
after this section is appended; no existing line in this file was
edited or removed by this pass.

## What must be fixed before re-audit (process-completeness only)

1. Actually add `TEMPLATE.md`'s five missing sections (`Where we are`,
   explicitly separate `What worked`/`What didn't work`, `Candidate
   learnings filed`, `Where we're going`, `Time / cost note`) to
   `planning/retros/phase-89-stage-89a.md` — the addendum alone does not
   satisfy this; the third audit named this as its own separate,
   explicit requirement, distinct from "update the retro for the second
   corrective pass," and it remains outstanding.
2. Soften `CHANGELOG.md`/`planning/ROADMAP.md`'s own "retro completion"
   phrasing (or simply finish the retro first, which moots the wording
   question) so neither document asserts a fuller resolution than what
   actually happened, once item 1 above is done.

No other item from the third audit's required-fix list needs further
work. This FAIL is narrow and mechanical — a named, explicit
documentation-structure requirement that was not completed — not a
finding against any of the five substantive mechanism areas the third
audit (or this pass) examined, and not a finding against items 2-4 of
the third audit's own list, all of which are genuinely done.

---

# Fifth independent audit — 2026-11-19 (focused re-check of the Fourth audit's required fix: retro process-completeness)

**Auditor:** `release-phase-auditor` (independent, read-only pass; never
the implementer). **Scope:** narrow, as dispatched — verify only that
the Fourth independent audit's own required fix (add `TEMPLATE.md`'s
five missing sections to `planning/retros/phase-89-stage-89a.md`, and
correct `CHANGELOG.md`/`planning/ROADMAP.md`'s "retro completion"
phrasing if it still overclaims) is now genuinely done, against the
current working tree (uncommitted at dispatch time, same state the
Stage 89B audit below also examined). Does not re-litigate the ten
substantive Stage 89A checklist points, the two corrective passes, or
the three prior audit rounds' own A-E mechanism findings — all stand
unchanged and are not re-verified here.

## Verdict

**PASS.**

## What was re-checked

1. **All five `TEMPLATE.md` sections the Fourth audit named as missing
   now genuinely exist, with substantive, non-placeholder content.**
   Read `planning/retros/TEMPLATE.md` in full first, then
   `planning/retros/phase-89-stage-89a.md` in full (405 lines, not just
   headings). `grep -n "^## "` against the retro now returns, in order:
   `Where we are`, `Goal`, `Delivered vs. planned`, `Design decisions
   made beyond what was specified`, `Lessons learnt`,
   `Process-improvement feedback`, `What worked`, `What didn't work`,
   `Candidate learnings filed`, `Where we're going`, `Time / cost note`,
   plus the two dated corrective-pass addenda. All five sections the
   Fourth audit's own item-by-item re-check explicitly named as absent
   (`Where we are`; explicitly separate `What worked`/`What didn't
   work`; `Candidate learnings filed`; `Where we're going`; `Time /
   cost note`) are present, each read in full:
   - `Where we are` (lines 3-23) genuinely orients a future session in
     the arc — names Phase 89's own three-stage split, what Stage 89A
     builds on (Phase 83, Phase 87), and the post-stage project state —
     not a stub.
   - `What worked` (210-230) and `What didn't work` (232-250) are
     genuinely separate, each with specific, named claims (the real
     Ledgerkit demonstration catching two bugs the unit suite missed;
     the six-round plan review paying off; vs. the original audit's own
     checklist not generalising to either corrective pass's defects,
     and this retro's own first closeout attempt treating the original
     PASS as final) — not a restated "went fine" pair.
   - `Candidate learnings filed` (252-261) correctly defers the
     disposition record to `planning/learnings/inbox.md`/`promoted.md`
     per this project's own established separation, while still naming
     `L-135`/`L-136`/`L-137` explicitly — a genuine answer, not a
     placeholder "none".
   - `Where we're going` (263-275) names the concrete trajectory (Stage
     89B's dependency on this stage's own manifest mechanism, Stage
     89C as the only remaining exit-gate item) and states the stage's
     outcome did not change the plan's own staged order — substantive.
   - `Time / cost note` (277-289) gives real session-count detail across
     the original implementation and both corrective passes, and names
     the actual cost driver (independent-audit dispatch time, not
     implementation time) — not a placeholder.
   None of these five sections read as filler; each is consistent with
   the rest of the retro and with this audit file's own full history
   (cross-checked against the Third and Fourth audit sections above —
   no contradiction found).
2. **`CHANGELOG.md`'s/`planning/ROADMAP.md`'s "retro completion"
   language, re-read against the now-fixed retro, is accurate — neither
   over- nor under-claiming.** `CHANGELOG.md`'s sentence ("Corrected in
   place (retro completion in `planning/retros/
   phase-89-stage-89a.md`; ...)") is, read today, a true statement: the
   retro is in fact now complete against `TEMPLATE.md`. This exact
   sentence is unchanged since the Fourth audit found it potentially
   misleading (at a time when only the second-corrective-pass addendum
   existed, not the five template sections) — it was not edited to add
   a disclosure of the intervening Fourth-audit FAIL-then-fix cycle, but
   it is not currently false or misleading, since the underlying retro
   file it points to has since actually been brought to the state the
   sentence describes. `planning/ROADMAP.md`'s Phase 89 row phrase
   ("being fixed in place now (retro completion, learnings triage,
   stale-language correction), ahead of a fresh re-audit") is present
   progressive and, read literally today, slightly underclaims (the fix
   is in fact done, not merely "being" done) rather than overclaiming —
   a non-blocking, cosmetic tense mismatch, not a false claim of
   completion. Neither document asserts anything about the retro's
   current state that direct inspection contradicts.
3. **Append-only confirmation.** `git diff HEAD --stat -- planning/
   retros/_audit-phase-89-stage-89a.md` (before this section was
   appended) showed only insertions relative to committed `HEAD`
   (`61591f4`); this section is appended after that point, at the end of
   the file, with no existing line edited or removed.

## Non-blocking observations

1. **`planning/CONTEXT.md`'s own "Current phase" narrative (lines
   96-137) still describes the Third audit's fix ("now has a full
   second-corrective-pass addendum") without separately narrating that
   a Fourth audit then found the `TEMPLATE.md` sections still missing
   and that a further pass added them.** The final state it points to
   (the retro) is accurate, and the file's own "Superseded again..."
   paragraph (line 1495 onward) correctly states the process-
   completeness fixes are "fixed in place (not yet re-audited)" — true
   as of this audit's own start — but a reader relying solely on the
   "Current phase" section's own prose, without reading the retro file
   directly, would not learn that one fix attempt was found incomplete
   before the complete one landed. Worth a tightening pass whenever
   `planning/CONTEXT.md` is next reconciled for Phase 89's overall
   closeout; not a blocking gap for this narrow re-check, since the
   underlying retro file itself (the actual DoD artifact) is genuinely
   complete.
2. **`planning/ROADMAP.md`'s present-progressive "being fixed in place
   now" phrasing** (item 2 above) should be tightened to past tense once
   the whole Phase 89 Stage 89A/89B closeout is next reconciled, purely
   for tense accuracy — not a substantive claim problem.

