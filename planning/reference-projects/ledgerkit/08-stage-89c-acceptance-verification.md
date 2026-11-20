# Phase 89 Stage 89C — independent acceptance verification (both arms)

Performed per the plan's §6 "Creation sequence" against fresh verify
clones (`ledgerkit-verify-control`, `ledgerkit-verify-treatment`), each
a `cp -r` of the pinned, pristine seed clone (`a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`)
with exactly that arm's own real `git diff` applied, plus this plan's
own pinned `tests/test_combined_section_acceptance.py` added verbatim
and identically to both. Both arms touched exactly two files
(`ledgerkit/models.py`, `tests/test_reports.py`) — the task (§3) named
only the first; the second is each arm's own added unit tests, which
the dispatch prompt explicitly permitted ("you may add your own unit
tests if you wish"). Reported as a benign, permitted deviation, not a
scope violation.

## 11-test acceptance suite (`tests/test_combined_section_acceptance.py`)

Both arms: **11/11 PASSED**, identical outcome, no divergence.

| Test | Control | Treatment |
|---|---|---|
| test_overlapping_patterns_across_combined_sections_counted_once | PASS | PASS |
| test_non_overlapping_patterns_sum_correctly | PASS | PASS |
| test_three_or_more_sections_combine_correctly | PASS | PASS |
| test_zero_sections_raises | PASS | PASS |
| test_conflicting_invert_raises | PASS | PASS |
| test_does_not_mutate_input_sections | PASS | PASS |
| test_unrelated_existing_report_behaviour_unaffected | PASS | PASS |
| test_union_of_exclude_patterns | PASS | PASS |
| test_conflicting_depth_raises | PASS | PASS |
| test_label_override_used | PASS | PASS |
| test_default_label_omitted_matches_ordinary_section_convention | PASS | PASS |

**This is a tie on acceptance-test outcome** — success-criterion signal
(i) ("treatment's acceptance-test outcome is correct where control's is
not") is **not met**; both are correct.

## Primary-scope `OracleResult` (real Phase 82 API: `evaluate_check` →
`write_oracle_result` → `parse_oracle_result` →
`evaluate_result_precedence`)

Disposable contract `STAGE89C-TASKB-VERIFY`, one `required: true` check
`combined-section-no-double-count`, `tested_paths: [ledgerkit/models.py]`,
`test_input_paths: [tests/test_combined_section_acceptance.py,
tests/fixtures/filtered.journal]`.

| Field | Control | Treatment |
|---|---|---|
| `evaluate_check` outcome | PASS | PASS |
| `invalid_reason` | None | None |
| `run_id` | `20261120T160729910366Z-4e61a8f1` | `20261120T160730927778Z-6506946d` |
| `tested_subject_digest` | `cbc51899badb2ffc56b44098ae9dcf8c092304d1970e814de46149100ff7ae49` | `ef3c3e946aa0d94364268416a22f9c918e59f805612d57f64559ad89db3fc2dc` |
| `test_input_digest` | `01ca96bc92c8e21ba2e75f247d11da1055a16403e4670d2fa04ef3574fbef214` | `01ca96bc92c8e21ba2e75f247d11da1055a16403e4670d2fa04ef3574fbef214` |
| `oracle_contract_content_hash` | `6f5ce5cc369c5b7dca079e5dd38cd58597bd4f462e768a0fddae8a35c2933bd4` | (identical — same disposable contract file) |
| round-tripped (`write_oracle_result`→`parse_oracle_result`) outcome match | True | True |
| `evaluate_result_precedence` | `('PASS', None)` | `('PASS', None)` |

`tested_subject_digest` correctly differs between arms (each arm's own
`ledgerkit/models.py` content differs); `test_input_digest` correctly
matches (the acceptance test file is byte-identical for both, as
required). Both results are genuinely, independently re-validated PASS
— not merely a stored field trusted at face value.

Raw output and result JSON persisted under the session scratchpad
(`oracle-raw-{control,treatment}/`, `oracle-result-{control,treatment}.json`)
and summarized here; not committed to this repository (disposable,
scratch-only per plan §13).

## Full Ledgerkit regression suite (`pytest tests/ -q`)

| Clone | Result |
|---|---|
| `ledgerkit-seed` (pristine baseline) | 935 passed, 14 subtests passed |
| `ledgerkit-verify-control` | 957 passed, 14 subtests passed — **0 failed** |
| `ledgerkit-verify-treatment` | 958 passed, 14 subtests passed — **0 failed** |

No regression in either arm relative to the pristine baseline. The
raw pass counts differ slightly between arms because each arm wrote a
different number of its own additional unit tests (control added 10,
treatment added 11, to `tests/test_reports.py`) on top of the shared
11-test acceptance file — this is expected and benign, not a
discrepancy requiring explanation beyond each arm's own disclosed test
additions.

## Summary

Technically, both arms produced a complete, correct, non-regressing
implementation. The primary acceptance-test oracle result is PASS for
both, independently re-validated via the real Phase 82 API for both.
**Acceptance-test outcome does not distinguish the two arms** — this
experiment's positive-result signal, if any, must come from signal
(ii) or (iii) (the independent `context-evaluator`'s verdict/rating),
not from this signal (i).
