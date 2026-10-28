# 0090: Phase 83 final corrective amendment — `oracle_contract_id` validation

**Status:** accepted (2026-10-29). Governing prompt: "CodeCompass
Orchestrator — Close Phase 83 and Implement Phase 84" (2026-10-29).
`decisions/0089` fixed three defects in `scripts/assess_change_impact.py`
and was independently audited PASS (`planning/retros/_audit-phase-83.md`,
against commit `057e59d`). This ADR documents one further, narrowly
scoped defect found by direct inspection after that audit, closing out
the Phase 83 corrective line of work.

## Context

`OracleResult` (`src/codecompass/oracle.py`) carries two independent
contract-identity fields, both required by its schema
(`_RESULT_REQUIRED`): `contract_id` and `oracle_contract_id`.
`evaluate_result_precedence` already treats a mismatch on *either* field
as grounds for `INVALID` (`oracle.py:733-737`:
`result.contract_id != contract.contract_id or result.oracle_contract_id
!= contract.contract_id`) — the schema deliberately carries both because
they originate from different points in a result's own provenance (one
is the contract the check was declared against; the other is the
contract identity the run itself recorded at execution time), and a
genuinely valid result must agree with the live contract on both.

`classify_symbol()`'s own historical-evidence validation
(`decisions/0089` §C), as corrected, checks `result.contract_id ==
contract.contract_id`, `contract.check_by_id(result.check_id)`, and
`result.scope == check.scope` — but never checks
`result.oracle_contract_id`. A historical `OracleResult` whose
`contract_id` happens to match the live contract by coincidence (or by a
copy/paste error when the record was authored) while its
`oracle_contract_id` names a different contract entirely would still be
accepted here as establishing `behavioural_risk` coverage — exactly the
"malformed/mismatched... test Evidence... establish[ing] verified
coverage" failure mode `decisions/0089` §C was written to close, left
open for this one specific field.

Confirmed by direct reading of `scripts/assess_change_impact.py` as
corrected by `decisions/0089` (commit `365dec1`): the `test_evidence_
check_id` loop in `classify_symbol()` has no `oracle_contract_id`
comparison anywhere.

## Decision

Add one more comparison to the same loop, immediately alongside the
existing `contract_id` check:

```python
if result.contract_id != contract.contract_id:
    continue
if result.oracle_contract_id != contract.contract_id:
    continue
```

Both fields must independently identify the live contract. No new
parsing, no new validation infrastructure — this reuses the exact
`OracleResult` fields `parse_oracle_result` already exposes, following
the same "validate what the schema already carries, do not duplicate
it" discipline `decisions/0089` §C established.

As with §C's own design, this is deliberately **not** achieved by
routing through `evaluate_result_precedence` — that function also
recomputes the live `oracle-contract.yaml` file's own content hash
against the historical result's `oracle_contract_content_hash`, which
(per `decisions/0089`'s own "Alternatives considered") would retroactively
invalidate any historical result predating a later, unrelated contract
extension. The narrower two-field structural identity check keeps the
historical-relationship question (did this result ever validly cite this
contract) separate from the current-execution-outcome question
(`run_check_assurance`'s own job, entirely unchanged by this fix).

## Consequences

- One citing `test`-kind Evidence record whose referenced `OracleResult`
  has a correct `contract_id` but an incorrect `oracle_contract_id` no
  longer contributes a `check_id` to `test_evidence_check_id` — the
  citing symbol's classification falls back to whatever its `source`-kind
  Evidence alone would establish (`relevant_no_coverage_link` if no other
  valid test Evidence exists for it, `no_recorded_relationship` if no
  Evidence cites it at all).
- No change to `RangeResolution`/`RangeReport`/`AssuranceFinding` shapes —
  this fix changes only which historical results are accepted as valid
  Evidence, not the report's own structure.
- No change to `oracle.py`, `graph.py`, `knowledge_intermediate.py` —
  `evaluate_result_precedence`'s own existing two-field check is read as
  precedent, not modified or called.
- No change to real or scratch Ledgerkit checkouts, no change to the real
  canonical `planning/knowledge/`/`planning/contracts/` corpus.
- The one still-outstanding, separately-gated item named at Phase 83's
  original closeout (the real Ledgerkit overlapping-pattern test landing
  in `~/projects/ledgerkit`) is unaffected and remains exactly as
  outstanding as before.

## Alternatives considered

- **Route through `evaluate_result_precedence` with `repo_root=None`.**
  Rejected for the same reason `decisions/0089` §C already rejected it:
  it recomputes a live content-hash comparison that is a current-outcome
  question, not a historical-relationship one, and would retroactively
  flip historical validity whenever the contract is later extended for
  unrelated reasons.
- **Treat `oracle_contract_id` as redundant with `contract_id` and skip
  it.** Rejected — the schema requires both as independently meaningful
  fields (confirmed via `_RESULT_REQUIRED` and `evaluate_result_
  precedence`'s own treatment of them as two separate comparisons); a
  validator that only checks one is a narrower check than the schema
  itself warrants, exactly the gap this ADR closes.
