# 0097. Phase 89 Stage 89A corrective pass: apply-time re-validation,
shared-test-input attribution, and idempotent-retry recovery

## Status

Accepted (2026-11-18, direct user request — "CodeCompass Orchestrator —
Phase 89A Corrective Implementation and Re-Audit"). Corrective, not a
reopening of `decisions/0096`'s own four tradeoffs, which stand
unchanged. This ADR documents three further implementation-contract
resolutions a source-level review found Stage 89A's original
implementation had left unsound, plus two bounded integrity fixes.
Governed by `decisions/0085` §3 (Phase 89's own split-and-scope
decision) and `decisions/0096`, neither of which this ADR reopens.

## Context

Stage 89A was implemented and independently audited (PASS WITH
NON-BLOCKING OBSERVATIONS, `planning/retros/_audit-phase-89-stage-89a.md`)
against a real Ledgerkit demonstration. A subsequent source-level review
found three material defects the original audit's own ten-point
checklist did not probe for, plus two further bounded integrity gaps.

### 1. Shared-test-input attribution and baseline eligibility

`source_reconciliation._tracked_test_input_paths` built `{test_input_
path: check_id}` — a single-valued mapping. The real Ledgerkit
`balance-from-spec` contract has two already-covered checks
(`single-section-expense-subtotal`, `multi-section-income-expense-
subtotal`) sharing both `tests/test_reports.py` and `tests/fixtures/
filtered.journal` as `test_input_paths` — a shared-file change silently
collapsed to whichever check `contract.checks` iterated to last,
permanently hiding the other's own drift from `detect_source_changes`.

**Decided**: `_tracked_test_input_paths` now returns `{test_input_path:
[check_id, ...]}` (one-to-many). `detect_source_changes` emits one
`SourceChangeFinding` per `(path, check_id)` pair sharing a path — the
dataclass itself is unchanged; this is a multiplicity fix at emission
time, not a schema change. `propose_reconciliation` deduplicates
*execution* only (a `check_id` triggered by two shared paths in one call
is evaluated once, its result reused for every finding naming it),
never check identity or per-path attribution.

A related correctness gap this exposes: once a single shared file can
produce more than one, independently-reviewable manifest item (one per
Claim), accepting one sibling must never let its own apply advance the
shared file's baseline while another sibling citing the same file is
still rejected or pending — that would silently waive the unresolved
check's own drift. `propose_reconciliation` now also returns
`baseline_eligible_test_input_paths`: a path is eligible only once
**every** check sharing it (`required_by_path`, from every
`test_input_change` finding) was successfully, validly re-verified this
run (`accounted_by_path` — a no-op re-confirmation against an
already-`supported` Claim still counts, since the check genuinely was
re-run; an `INVALID` result or an unresolvable `check_id` does not).
`write_source_reconciliation_manifest` excludes an ineligible shared
path from every item's own `contributing_source_paths` this round.
`advance_baselines_for_applied_item` additionally gates *per path* at
apply time: given `manifest_items` (now a required keyword argument,
not optional, so this guard can never be silently skipped), a path only
advances once every item in the same manifest citing it has reached
`state == "applied"` — a still-pending or rejected sibling blocks it
indefinitely, exactly like this project's own existing
`concurrent_conflict` philosophy ("never auto-resolved … keeps being
reported until the underlying facts actually change again").

### 2. Apply-time re-validation must not trust a stale or tampered result

`_apply_source_reconciliation` checked only `(contract_id, check_id,
run_id)` identity against the manifest's own cached tuple and that the
cited result file re-parsed — it never re-ran Phase 82's own
precedence/validity check at the canonical write boundary, and it
trusted the manifest's cached `contributing_target_fields` verbatim
rather than independently deriving which Claim field a fresh outcome
belongs in.

**Decided**: reuse the *existing* `oracle.evaluate_result_precedence`
(Phase 82, unmodified) rather than build a second verification engine.
For every cited result, `_apply_source_reconciliation` now: resolves the
live check from the live contract (refusing if either no longer
exists); requires the manifest item's own recorded `repo_root` to be a
real, existing directory, **fail-closed** otherwise (apply-time
re-validation is only ever meaningful against a live checkout — an
unavailable one is refused, never silently skipped); calls
`evaluate_result_precedence(result, contract, check, contract_path=...,
repo_root=...)`, which re-checks `oracle_contract_content_hash` against
the live contract, `contract_id`/`oracle_contract_id`, `tested_subject_
digest`/`test_input_digest` against the live checkout, `raw_output_ref`
existence and its `raw_output_sha256`, and `scope` — refusing the whole
item on `INVALID`; and independently derives `target_field` from the
*effective* outcome (`FAIL` → `contradicting_evidence`, else
`supporting_evidence`), refusing if that disagrees with the manifest's
own cached value rather than ever trusting the cached value alone. No
Evidence or Claim mutation happens unless every cited finding in the
item passes this re-validation.

### 3. Idempotent-retry recovery after a Claim write has already succeeded

`_apply_source_reconciliation` is the one `apply_manifest` item kind
that mutates the exact record (`base_claim_hash`) its own race check
guards. A crash after the Claim write succeeds but before the caller
durably records `state="applied"` left a retry unable to distinguish
its own prior successful write from a genuine concurrent human edit —
the stale-looking hash made every retry fail as a false conflict.

**Decided**: a narrow, read-only pre-check — never a general
transaction manager — runs before the existing `base_claim_hash`
comparison. It resolves each finding's own Evidence identity (`_find_
existing_evidence_for_run`, unchanged) and asks whether every one is
*already* cited, in the independently-derived correct field, in the
*live* Claim, and whether recomputing `evidence_support_state` from the
live Claim's own full accumulated fields agrees with what is already
recorded there. Only when every one of those holds does this return a
successful, idempotent no-op recovery outcome without writing anything
— any disagreement (including the ordinary case where nothing has been
written yet, or only some findings have Evidence so far) falls through
unchanged to the pre-existing hash check and per-finding apply loop,
so a genuine concurrent edit (a human changing the Claim's `statement`,
for instance) is still refused exactly as before.

A sibling gap in the same failure class: `cli.py::knowledge_apply_
manifest` only ever ran baseline advancement for items this *one* call
to `apply_manifest` returned in `result.applied` — an item already
`state == "applied"` from an earlier, interrupted run is reported via
`result.skipped`, so a crash between `apply_manifest` returning and
baseline advancement completing left that advancement un-retriable on a
simple re-run. **Decided**: the CLI now re-reads the manifest fresh
after `apply_manifest` returns and re-attempts baseline advancement for
**every** `source_reconciliation` item already `state == "applied"`,
not only the ones this call newly applied — safe because `establish_
source_baseline`/`advance_source_baseline_after_apply` unconditionally
overwrite with the same value, making the whole operation naturally
idempotent on retry. This is the resolution to `decisions/0096`'s own
disclosed "known limitation" bullet (baseline advancement not wired
into `apply_manifest`'s own generic dispatch) — the orchestration still
lives in the CLI layer exactly as 0096 chose, now simply re-run in full
on every invocation rather than once per freshly-applied item.

### 4. Two bounded integrity fixes

**Non-Python oracle inputs.** `tests/fixtures/filtered.journal` is a
real, contract-declared `test_input_path` with no `source_files` row in
the target's own symbol graph (it is never Python-indexed) — the
original code treated "not indexed" identically for every tracked path,
permanently diverting it to `stale_graph_index` and never comparing it
against its own baseline at all. **Decided**: for a `test_input_change`
path specifically (never `symbol_change`, which still genuinely needs
the graph for `classify_symbol`), a missing graph row falls back to a
direct `sha256_file` of the live file for baseline comparison — in
`detect_source_changes`'s own main loop, in `establish_baselines_for_
new_files`, and in `write_source_reconciliation_manifest`'s own
`contributing_source_hashes` computation (all three needed the same
fallback to keep a non-Python fixture's baseline lifecycle complete end
to end).

**Working-tree provenance.** `_repo_revision` returned bare `git
rev-parse HEAD` output regardless of working-tree state, silently
implying a clean commit was verified even when local modifications were
present — the common case for reconciling a change that has not yet
been committed. **Decided**: `_repo_revision` additionally checks `git
status --porcelain`; a dirty tree is marked `+dirty` and, when the real
`OracleResult` being recorded is available, its own `tested_subject_
digest`/`test_input_digest` (genuine content-digest provenance, never
derived from git) are embedded directly in the returned string. A clean
tree's return value is unchanged. `OracleResult`'s own schema is
untouched — this is purely about the string written into the pre-
existing Evidence `repository_revision` field.

## Consequences

- `propose_reconciliation` now returns a `ReconciliationProposal`
  dataclass (`findings` + `baseline_eligible_test_input_paths`) instead
  of a bare list — its one production call site (`cli.py::knowledge_
  verify_changes`) and all test call sites were updated accordingly.
- `write_source_reconciliation_manifest` gains one new optional
  parameter (`baseline_eligible_test_input_paths`); omitting it treats
  every shared test-input path as ineligible, a deliberately
  conservative default for any caller that does not thread it through.
- `advance_baselines_for_applied_item` gains one new **required**
  keyword argument (`manifest_items`) — a breaking signature change for
  its one caller (`cli.py`), chosen deliberately so the cross-item
  guard can never be silently omitted by a caller that forgets to pass
  it.
- `_apply_source_reconciliation` now requires every `source_
  reconciliation` manifest item to carry a resolvable `repo_root` to
  apply at all — an item written before this corrective pass (with no
  `repo_root`, or one pointing at a checkout that no longer exists) is
  refused, fail-closed, rather than applied against unverifiable
  provenance.
- No change to `OracleResult`'s schema, `oracle.py`'s existing
  precedence logic, or any of `decisions/0096`'s four original
  tradeoffs.
