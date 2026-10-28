# 0087. Phase 83 second corrective planning amendment: INVALID is checked before the aggregate-GAP fallback; classification is determined solely by the fresh result; a scratch-only test file keeps the original-suite baseline run clean

## Status

Accepted (2026-10-28, direct user request — "CodeCompass Orchestrator —
Amend and Implement Phase 83"). Amends `planning/phase-83-semantic-
change-assurance.md` §4 in place. Does not reverse `decisions/0078`-
`0086`; corrects one real defect in `decisions/0086`'s own §2 precedence
design (found before any code was written against it) and clarifies two
sequencing details (`decisions/0086` §4's ordering; the Ledgerkit
scratch-copy demonstration's own test-file handling) that the first
corrective pass left implicit. This ADR also records the explicit
authorisation to proceed directly with Phase 83 implementation —
superseding the prior "planning only" gate on this plan file.

## Context

Ledgerkit's HEAD is still `7224bb5c113cd3aad7e86e994365703cd0070154`,
re-confirmed this session, unchanged since both prior planning passes.

**The defect**: `decisions/0086` §2 specified this precedence over an
applicable check's fresh execution:

1. Any observed outcome is `FAIL` → CONFIRMED_REGRESSION.
2. Else aggregate `state` is `PASS` → VERIFIED_SCOPE.
3. Else aggregate `state` is `GAP` → VERIFICATION_GAP.
4. Else any observed outcome is `INVALID` → INVALID_ASSESSMENT.

`aggregate_contract` (`oracle.py` line 786-826, unchanged, re-confirmed
by direct reading) returns `GAP` for a required check whenever no result
satisfies precedence rule 3 with `outcome: PASS` — this includes a check
whose *only* result is `INVALID` (an invalid result is not a passing
one, so `passing` stays `None`). Rule 3 above therefore always fires
before rule 4 can be reached whenever the fresh result is `INVALID`
(since an `INVALID` result can never make the aggregate `PASS`, and
always leaves it `GAP`) — rule 4, `INVALID_ASSESSMENT`, was dead code in
the amended plan's own design, not merely an edge case. A corrupted raw
output, a digest mismatch, a tampered result, or a scope mismatch on the
one fresh execution would all have been reported as `VERIFICATION_GAP`
("no usable evidence") rather than `INVALID_ASSESSMENT` ("evidence
exists but cannot be trusted") — exactly the distinction `0086` itself
was written to preserve, broken by its own rule ordering.

## Decision

### 1. Classification is determined solely by the one fresh result's own effective outcome — never by the separately-computed aggregate `state`

`--run-checks` produces **exactly one** fresh `OracleResult` per
applicable check (`oracle.evaluate_check`, called once). Its *effective*
outcome — via `oracle.evaluate_result_precedence`, never its own raw
`outcome` field — is always exactly one of `PASS`/`FAIL`/`INVALID` (never
`GAP`, which `evaluate_result_precedence` never returns for a single
result). The classification precedence is revised to test this fresh
effective outcome directly, with no step that can be pre-empted by an
aggregate computed over a *different* question (whether any result,
historical or fresh, happens to be an accepted `PASS`):

1. Fresh effective outcome is `FAIL` → **CONFIRMED_REGRESSION**.
2. Else fresh effective outcome is `INVALID` → **INVALID_ASSESSMENT** —
   reachable now, unconditionally, whenever the fresh execution itself
   could not be trusted or validated.
3. Else fresh effective outcome is `PASS` → **VERIFIED_SCOPE**.
4. Else — no fresh result exists for this check at all (`--run-checks`
   was not passed, or §3's relevance/coverage model found no applicable
   check in the first place) → **VERIFICATION_GAP**. This is reserved
   for *no verification was attempted*, never reused for an attempt that
   produced a real, if untrustworthy, `INVALID` outcome.

The separately-computed aggregate `state` (`PASS`/`GAP`/`NOT_REQUIRED`,
over every `OracleResult` on file for the check — historical and fresh
together) is **always shown alongside** the classification above, for
context, never substituted as a determining step. This is how a
`CONFIRMED_REGRESSION`'s own near-always-`GAP` aggregate stays visible
(unchanged from `decisions/0086`), and, new here, how an `INVALID_
ASSESSMENT`'s own near-always-`GAP` aggregate (an invalid result is
never a passing one either) is shown without being mistaken for the
determining signal that produced `INVALID_ASSESSMENT` in the first
place. A historical `PASS` on file for the same check can never promote
a fresh `FAIL`/`INVALID` past rule 1/2 above — classification reads only
the fresh result, per the governing prompt's own "do not allow
historical results to mask a fresh failure."

### 2. Negative tests, naming every effective-outcome path explicitly

`tests/test_assess_change_impact.py` must exercise, each as its own
fixture-driven case (never inferred from the positive-path tests alone):
a fresh genuine `FAIL` (CONFIRMED_REGRESSION); a fresh digest mismatch
(tested-subject or test-input — `INVALID_ASSESSMENT`); a fresh corrupted/
tampered raw output (`raw_output_sha256` mismatch — `INVALID_
ASSESSMENT`); a fresh all-skipped execution (pytest's own existing
`decisions/0083` all-skipped-is-`INVALID` behaviour, surfaced here as
`INVALID_ASSESSMENT`, not silently passed through); and no fresh result
at all / no applicable check found (`VERIFICATION_GAP`). Each test
asserts the specific classification produced, not merely that it differs
from the others.

### 3. The Ledgerkit scratch-copy demonstration keeps the new test out of the original-suite run by construction, not by filtering

To satisfy "the new test must not already be included in the suite used
to establish the original coverage gap," the demonstration's own ordering
is fixed, not left to be inferred from running `pytest tests/` twice and
hoping the new file is excluded some other way:

1. A pristine scratch copy is made from Ledgerkit's pinned HEAD
   (`7224bb5c113cd3aad7e86e994365703cd0070154`) — no new test file
   anywhere in its tree yet.
2. The mutation patch is applied to `ledgerkit/reports.py` only.
3. `pytest tests/` is run in **this exact tree** — the new check's own
   test file does not exist in it at all, so "the suite used to establish
   the original coverage gap" cannot include it by construction, not by
   a path filter that could silently drift. This run's full output is
   captured verbatim (not paraphrased) as the frozen original-baseline
   comparison.
4. Only **after** step 3's output is captured, the new check's own test
   function is added to this scratch tree, as a new file
   (`tests/test_phase83_overlap_regression.py` — never merged into
   `tests/test_reports.py` in the scratch copy, and never committed to
   the real `~/projects/ledgerkit` checkout as part of this phase). The
   new check's own `check_reference` (in `oracle-contract.yaml`) names
   this test by its eventual real intended location
   (`tests/test_reports.py::TestBalanceFromSpec::test_section_accounts_
   overlapping_patterns_no_double_count`) — the scratch copy's own
   temporary file is placed at a path/name convenient for this
   demonstration only, not required to match the contract's own
   `check_reference` string, since the demonstration runs the check
   directly against the scratch file (by its own real pytest node id) to
   confirm real PASS/FAIL behaviour, independent of whether it has yet
   landed at its eventual permanent location.
5. A second, separately pinned scratch copy (clean HEAD, same new test
   file added, no mutation) confirms the new check `PASS`es on correct
   code — both directions demonstrated, not only the failing one.
6. `scripts/assess_change_impact.py --run-checks` is run against the
   mutated scratch copy from step 4, producing the real
   `CONFIRMED_REGRESSION` report.

**Contract-vs-demonstration consequence, named explicitly**: the real
`planning/contracts/balance-from-spec/oracle-contract.yaml`'s own new
check has a `check_reference` pointing at a test that does **not yet
exist** in the real, live `~/projects/ledgerkit` checkout (landing it
there is the separately authorised action, §13/§10 of the plan,
unchanged). Running the new check for real against the live checkout
today will correctly, honestly classify `INVALID_ASSESSMENT` ("zero
collected tests" — `oracle.py`'s own existing, unmodified `_classify_
pytest_junit`, confirmed by direct reading to already produce exactly
this outcome for an unresolvable pytest node id) until that separate
authorisation lands the test for real — this is not executed or recorded
as a real `OracleResult` in this phase (it would be a trivially
uninformative `INVALID`, known in advance, not a finding), and is instead
named as this phase's one explicit, outstanding, unresolved gate (plan
§7.4/§13, unchanged) — never silently treated as satisfied.

### 4. Explicit authorisation to implement

This governing prompt authorises proceeding directly with Phase 83
implementation after the correction above, without a further planning
review round, unless a genuinely material architectural blocker is
found during implementation.

## Consequences

- `planning/phase-83-semantic-change-assurance.md` §4 (precedence),
  §10 (tests), and §11 (demonstration ordering) are revised in place to
  carry this design.
- No change to `src/codecompass/oracle.py`, `graph.py`, or `knowledge_
  intermediate.py` — the defect was in the plan's own precedence
  specification, not in any shipped code; `aggregate_contract`'s
  behaviour is exactly as `decisions/0081` already specifies and remains
  unmodified.
- `decisions/0078`-`0086` are not edited.
