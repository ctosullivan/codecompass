# Phase 82 drift audit

**Auditor:** docs-reconstructor (independent, MODE 1 per-phase drift
audit, dispatched before implementation's own fix commit).
**Scope:** `git diff d945864..ebca4bf -- src/ scripts/ planning/knowledge/
balance-from-spec/ planning/contracts/` plus `git show ebca4bf --stat`,
cross-referenced against `README.md`, `ai-docs/README.md`, every file
under `docs/`, and the real code in `src/codecompass/oracle.py` and
`knowledge_intermediate.py::derive_epistemic_profile` directly (not from
the implementer's own summary).

Backfilled by the lead, from the dispatched agent's own full report
(delivered as this session's agent-hand-back message, 2026-10-21), per
`release-phase-auditor`'s own non-blocking observation that no standalone
written record of this pass existed yet — the pass itself already ran
and its findings were already fixed in commit `a450bfe` before this
backfill; this file records that pass's own verdict and findings for the
historical record future sessions can point to without re-deriving it.

**Verdict at time of the original pass: DRIFT — 3 findings, all
non-blocking** (omissions in developer/process docs, no user-facing
false statement). **All three fixed in `a450bfe`, independently
re-verified by `release-phase-auditor` against that same commit.**

## Method

Checked every file Phase 82 added/changed under `src/`, `scripts/`,
`planning/knowledge/balance-from-spec/`, `planning/contracts/`, plus the
two docs files the phase itself had already touched
(`docs/architecture/components.md`, `docs/concepts/knowledge-model.md`),
plus a targeted grep sweep of `README.md`/`ai-docs/README.md`/`docs/**`
for `oracle`/`contract`/`verified`/`evidence`/`knowledge` terms. No
top-level `architecture/` directory exists in this repo (only
`docs/architecture/`), and `docs/domain/` does not exist yet, so the
domain-claim-staleness step was skipped per the role's own standing
instructions for a repo in this state.

## Findings (all fixed in `a450bfe`)

1. **`docs/development/contributing.md`, "Maintainer-only tooling"
   section** — omitted the two new Phase 82 scripts entirely
   (`scripts/check_contracts.py`, `scripts/run_balance_from_spec_oracle.py`),
   and the existing `scripts/check_knowledge_base.py` bullet's inline
   check list omitted the new `check_verified_status_cites_passing_
   oracle_result` check (confirmed present in that script's `CHECKS`
   list — a genuinely new check category, not already covered by any
   item listed). **Fixed**: both new scripts added as their own bullets;
   the existing bullet's check list extended.
2. **`docs/development/testing.md`** — the parenthetical list of test
   modules for maintainer-only `scripts/` tooling omitted the new
   `tests/test_check_contracts.py`. **Fixed**: added, plus
   `tests/test_oracle.py` to the general `src/codecompass/` module-test
   list for completeness.
3. **`docs/decisions.md`** (the mechanically-derived ADR title+status
   index) — stopped at `0075`; Phase 82 added `decisions/0080`/`0081`,
   neither indexed. Noted as a **pre-existing gap this phase extended,
   not one it created** — the index was already missing `0076`-`0079`
   before Phase 82 touched anything (last regenerated at Phase 81B).
   **Fixed**: extended through `0081`, including the two genuinely
   missing prior entries (`0076`/`0077`) found in the same pass.

## Checked and found accurate (no action needed)

- `docs/architecture/components.md` (new `oracle.py` row, amended
  `knowledge_intermediate.py` row) and `docs/concepts/knowledge-model.md`
  (new INTENDED/OBSERVED/VERIFIED/CONTESTED section) — independently
  verified against the real code: `GAP` is genuinely computed by
  `aggregate_contract`/`evaluate_result_precedence`, never a persisted
  `OracleResult.outcome` value (`_OUTCOME_VALUES = {"PASS", "FAIL",
  "INVALID"}`); the four predicates match the doc's description exactly,
  including "never a persisted field" and "library-only as of Phase 82"
  (grepped `src/codecompass/*.py` for `derive_epistemic_profile` outside
  `knowledge_intermediate.py` itself — no CLI wiring found).
- `ai-docs/README.md` — no update needed; the oracle/contract mechanism
  governs CodeCompass's own planning artifacts, is explicitly not a
  `codecompass` CLI subcommand, matching this file's existing exclusion
  of `check_knowledge_base.py` on the same basis.
- `docs/limitations.md` ("Knowledge layer" section) — still accurate,
  untouched and not contradicted by this phase.
- `docs/workflows/knowledge-reconciliation-loop.md` — unaffected: the
  new validator check lives only in the offline maintainer script, not
  in `codecompass knowledge apply`'s own write path.
- `README.md` — no false or stale claims relevant to this phase.

## Non-docs note (out of this audit's own scope, resolved separately)

`scripts/run_balance_from_spec_oracle.py`'s own module docstring
referenced a `scripts/accept_balance_from_spec_baseline.py` that does
not exist — an internal code comment, not a README/docs/architecture/
ai-docs claim, so outside this audit's own scope; flagged for the lead
to confirm was an intentional deferral. Fixed in `a450bfe` (points to
the real `oracle.accept_baseline` function instead).
