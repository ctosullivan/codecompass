# 0088. `check_contracts.py`'s result-integrity check no longer blocks on a historical result superseded by a current, fresh PASS for the same check

## Status

Accepted (2026-10-28, found during Phase 83 implementation — "CodeCompass
Orchestrator — Amend and Implement Phase 83," direct user request).
Corrects a real, independently demonstrated defect in `scripts/
check_contracts.py::check_result_integrity` — not a defect in
`src/codecompass/oracle.py`, which is unmodified. Does not reopen
`decisions/0080`-`0083`'s own design.

## Context

Implementing Phase 83's extension to `planning/contracts/balance-from-
spec/oracle-contract.yaml` (`decisions/0086`/`0087`, one new check
appended) is the **first time since Phase 82 shipped** that this
contract's own content has changed. Per `decisions/0086` §4 (itself
derived from `decisions/0081` §4's own pre-existing digest-drift design),
this was expected to invalidate the six existing `PASS` results'
recorded `oracle_contract_content_hash`, resolved by re-running the two
pre-existing checks once to produce two fresh, current `PASS` results.

Doing this for real (not merely reasoned about) found that `check_
contracts.py::check_result_integrity` reports **every** result whose
effective outcome recomputes to `INVALID` as a *blocking*
`contract-result-integrity-mismatch` finding, unconditionally — with no
exemption for a result that is superseded by a different, current `PASS`
for the exact same `check_id`. Re-running the two pre-existing checks did
not clear `--strict`: all six original results remained blocking forever,
with no available remedy short of deleting or editing historical
evidence — which `decisions/0081`/`0082` both explicitly forbid
("historical results are a true historical fact — never deleted, never
corrected"). This is a real, demonstrated gap: `decisions/0081` §4
already named exactly this situation ("historically valid... excluded
from the current aggregate... not deleted, not corrected") as an
expected and acceptable state for `aggregate_contract`'s own aggregation,
but `check_result_integrity` — a separate consumer of `evaluate_result_
precedence` — had no corresponding exemption, because no real contract
had ever been extended before this phase to expose it. No existing test
in `tests/test_check_contracts.py` exercised "two results for the same
`check_id`, one stale, one current" at all.

## Decision

`check_result_integrity` now computes, once per contract, the set of
`check_id`s with at least one result that currently evaluates `PASS`
(via the same `evaluate_result_precedence` already used throughout). A
result whose own effective outcome recomputes to `INVALID` is downgraded
from blocking to **informational** specifically when a *different*
result for the same `check_id` is in that current-`PASS` set — the
finding itself is still reported (visibility is preserved; the message
names the superseding state explicitly) but no longer fails `--strict`.
A mismatching result with no current `PASS` anywhere for its own
`check_id` remains exactly as blocking as before — this is the real
problem case the check exists to catch, unchanged.

Two new tests in `tests/test_check_contracts.py::TestResultIntegrity`
lock in both directions: `test_mismatch_with_no_superseding_pass_stays_
blocking` (the pre-existing guarantee, unweakened) and `test_mismatch_
superseded_by_fresh_pass_is_informational` (the new behaviour, modelled
directly on the real scenario that exposed the gap: extend a contract,
re-run the affected check, confirm the old result's own mismatch no
longer blocks).

## Alternatives considered

- **Archive/move superseded result files out of `results/`.** Rejected:
  contradicts `decisions/0081`/`0082`'s own explicit "never deleted,
  never corrected" discipline for historical evidence, and would require
  a new archival convention for no real benefit over simply recognising
  the state that already exists on disk.
- **String-match `evaluate_result_precedence`'s own `reason` text** to
  distinguish "digest/hash drift" from "tampering" and treat only the
  former as supersedable. Rejected: fragile (couples this check to the
  exact wording of another function's free-text diagnostic string); the
  chosen "does a current PASS exist for this check_id" test is simpler,
  already uses existing machinery, and correctly treats tampering as
  non-blocking too *when* a fresh PASS already supersedes it — which is
  the right outcome (the fresh evidence is what matters going forward),
  while still catching tampering as blocking in the normal case where no
  fresh PASS exists yet.

## Consequences

- `scripts/check_contracts.py::check_result_integrity` is corrected;
  `src/codecompass/oracle.py` is unmodified.
- `tests/test_check_contracts.py` gains two new tests (above).
- `decisions/0078`-`0087` are not edited.
