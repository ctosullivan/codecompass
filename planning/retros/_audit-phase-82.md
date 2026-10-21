# Phase 82 — Contract and Evidence Foundation — independent completion audit

**Auditor:** `release-phase-auditor` (independent pass, read-only)
**Audited commit:** `a450bfe` (HEAD at audit time)
**Commit range covered:** `d945864` (plan correction) → `ebca4bf`
(implementation) → `62b2f39` (retro/learning) → `63f4d84`
(knowledge-curator triage) → `a450bfe` (docs-drift fix)
**Plan file:** `planning/phase-82-contract-and-evidence-foundation.md`
(§10 Verification, §11 Exit gate)
**Governing ADRs:** `decisions/0078`, `0079`, `0080`, `0081`

## Verdict

**PASS WITH NON-BLOCKING OBSERVATIONS**

The real, end-to-end Ledgerkit vertical slice this phase set out to
build genuinely exists and genuinely works: a real `PASS` against the
live, unmodified `~/projects/ledgerkit` checkout, a real `FAIL` against
a deliberately mutated scratch copy, a vacuous-verification guard that
was confirmed — by actually breaking it, not merely reading its name —
to fail closed, and a full regression suite (980 passed / 2 pre-existing,
unrelated skips) plus `ruff`, `check_knowledge_base.py --strict`,
`check_contracts.py --strict`, and `check_user_docs.py --strict` all
clean. One process gap (below) is real but does not undermine the
substance of what was verified; it is reported as a non-blocking
observation per the instructions on honest-but-incomplete reporting,
not papered over.

## 1. Plan's own §10/§11 verification — re-run myself

- `python scripts/run_balance_from_spec_oracle.py` (using this repo's
  own `.venv/bin/python`, against the real `~/projects/ledgerkit`
  checkout) re-run live: produced **PASS** for both
  `single-section-expense-subtotal` and
  `multi-section-income-expense-subtotal`. Diffed the result against the
  committed files afterward: only `run_id`/`executed_at` changed —
  every digest field (`tested_subject_digest`,
  `oracle_contract_content_hash`, `test_input_digest`,
  `raw_output_sha256`) was byte-identical to the committed value. This
  is strong, direct evidence the committed results are real,
  reproducible oracle output, not hand-fabricated YAML. Working tree
  restored to the committed state (`git checkout --`) after recording
  this.
- `.venv/bin/python -m pytest tests/test_oracle.py
  tests/test_knowledge_intermediate.py tests/test_check_knowledge_base.py
  tests/test_check_contracts.py -q` → **178 passed**, 0 failed.
- Specifically re-ran the negative-control tests
  (`test_deliberately_broken_implementation_produces_fail`,
  `test_passing_result_cannot_verify_subsequently_modified_candidate`,
  and two more `-k "negative or fail or mutat"` matches) in isolation:
  **4 passed**. Read the test bodies directly (not just names): the
  first genuinely builds a disposable scratch copy, mutates
  `reports.py`'s `if section.invert:` to `if not section.invert:`,
  re-runs the real pytest check against the mutated scratch tree, and
  asserts `result.outcome == "FAIL"` with `"FAILED"` in the captured raw
  output — a real, demonstrated negative control, not an assertion of
  possibility.

## 2. No vacuous verification — tried to break it directly

Moved the committed
`planning/contracts/balance-from-spec/results/single-section-expense-subtotal.yaml`
out of the tree (not a dry read — an actual, temporary removal,
restored immediately after) and re-ran
`scripts/check_knowledge_base.py --strict` against the real repository
state:

- **Before removal:** exit `0`, only pre-existing `(info)`-level
  snapshot-divergence findings (24 of them, none new to this phase, none
  blocking).
- **After removal:** exit `1`, with a new, blocking finding:
  `[knowledge-base-verified-status-without-passing-oracle-result]
  planning/knowledge/balance-from-spec/CL-BFS-003.yaml: status=verified
  but required scope(s) ['single-section expense aggregation'] have no
  current, matching PASS`.

This is a genuine, demonstrated fail-closed result, not an inference
from reading `check_verified_status_cites_passing_oracle_result`'s
source. File restored; `git status --porcelain` confirmed clean
afterward. Also read the function's own logic
(`scripts/check_knowledge_base.py:606-690`): it correctly treats both
"empty required-check set" and "any required scope with no surviving
PASS" as disqualifying — matching `decisions/0081` §3 exactly, and the
compatibility exemption (slug has no `planning/contracts/<slug>/`
directory at all) is checked first and applies to none of this phase's
own records.

## 3. The twelve pre-existing `status: verified` records — unaffected

Ran `check_knowledge_base.py --strict` against the clean, current tree:
exit `0`. The only new finding class introduced by this phase
(`knowledge-base-verified-status-without-passing-oracle-result`) does
not fire against any of the twelve named exempted records
(`REQ-DOCORIGIN-001/002/003`, `REQ-HSAPI-001`–`006`, `CL-DEPTH-001`,
`CL-FPSS-006/007`) — confirmed by inspecting
`check_verified_status_cites_passing_oracle_result`'s own early-return
(`if not contract_path.is_file(): return findings`), which is exactly
the compatibility gate `decisions/0081` §3 specifies, and by the clean
exit code itself (no blocking finding against any of them appeared in
either the baseline or the broken-tree run above).

## 4. Full regression — exact pass/fail counts

- `.venv/bin/python -m pytest -q` → **980 passed, 2 skipped** (0 failed).
  The 2 skips are pre-existing and unrelated to Phase 82
  (`tests/test_adapter_cargo.py`/`test_adapter_npm.py`-style
  `skipif(shutil.which(...) is None)` guards for toolchains not
  installed on this machine — confirmed by grep across `tests/*.py`;
  nothing oracle/contract/knowledge-intermediate-related is skipped).
- `.venv/bin/python -m ruff check src/ scripts/ tests/` → **All checks
  passed!**
- `.venv/bin/python scripts/check_knowledge_base.py --strict` → exit
  `0`, only pre-existing `(info)` findings (not new to this phase).
- `.venv/bin/python scripts/check_contracts.py --strict` → **no
  findings**, exit `0`.
- `.venv/bin/python scripts/check_user_docs.py --strict` → **no
  findings**, exit `0`.

## 5. Doc-sync — checked the claimed `a450bfe` fixes directly, not the commit message

- `docs/development/contributing.md`: confirmed it now lists
  `scripts/check_contracts.py` and `scripts/run_balance_from_spec_oracle.py`,
  and the `check_knowledge_base.py` bullet now mentions the Phase 82
  `status: verified`-citing-oracle check. Both named scripts
  (`check_contracts.py::run_all`, `run_balance_from_spec_oracle.py`)
  exist in `scripts/` with exactly the described shape.
- `docs/development/testing.md`: confirmed `tests/test_oracle.py` and
  `tests/test_check_contracts.py` are now both named in the test-module
  list.
- `docs/decisions.md`: confirmed the ADR index table now includes
  `0076`–`0081` (previously missing `0076`–`0079` as well — the fix
  commit correctly extended the backfill rather than only covering what
  this phase itself added), and the "confirmed numbering gap" sentence's
  range was updated from `0001`–`0075` to `0001`–`0081`.
- `scripts/run_balance_from_spec_oracle.py`'s own docstring: confirmed
  it no longer references a nonexistent
  `scripts/accept_balance_from_spec_baseline.py` and instead correctly
  names the real `codecompass.oracle.accept_baseline` function (which
  exists at `src/codecompass/oracle.py:453`).
- No further current-truth-doc drift found in a targeted re-check of
  these three files plus `docs/architecture/components.md` and
  `docs/concepts/knowledge-model.md` (both updated in the same
  `ebca4bf` implementation commit, per `CLAUDE.md` §2's same-commit
  rule).

**Observation (non-blocking):** No persisted
`planning/retros/_drift-audit-phase-82.md` artifact exists for this
phase's `docs-reconstructor` pass — unlike most phases from 64 through
81, which each left a `_drift-audit-phase-N.md` file as a durable record
of that independent pass's own findings/verdict (though not
universally for every sub-pass, e.g. several Phase 81 sub-passes also
have none). The only trace of the docs-reconstructor pass having run at
all is the retro's own reference ("`docs-reconstructor` ... dispatched
for independent closeout checks — see those reports") and the `a450bfe`
fix commit's message. I independently re-verified the fixes directly
against the current file contents (above) and found them correct and
complete, with no further drift in a hands-on re-check — this
substantively closes the DoD's "finding fixed, doc no longer
misdescribes the system" requirement — but there is no standalone,
independently-written docs-reconstructor verdict file for a future
session to point to without re-deriving it. Recommend the lead have
`docs-reconstructor` write (or backfill) that report before/alongside
the terminal reconciliation commit, matching established project
practice. This does not block the phase: the substance was checked and
holds; only the durable-artifact form is missing.

## 6. Changelog, retro, learning-triage

- `CHANGELOG.md` `[Unreleased]` has a single, substantive Phase 82 entry
  ("Phase 82 — Contract and Evidence Foundation, implemented") plus
  three earlier, clearly-separate planning-only amendment entries for
  the same phase's own ADRs (`0079`/`0080` amendments) — these are
  amendment history of the one phase, not separate phases batched
  together, consistent with §12-14 of the plan file itself.
- `planning/retros/phase-82-contract-and-evidence-foundation.md` exists
  and is fully populated against `TEMPLATE.md`'s shape: Where we are,
  Goal, Scope delivered vs planned (including one explicitly-justified
  deviation — two checks instead of one), What was achieved, What
  worked, What didn't work, Lessons learnt, Process-improvement
  feedback, Candidate learnings filed, Where we're going, Time/cost
  note. Not a stub.
- `planning/learnings/inbox.md` L-101 entry: `status: promoted`, with a
  real, specific observation (editable-install `sys.path` shadowing a
  scratch mutation), evidence section, and classification. Matching
  `planning/learnings/promoted.md` line:
  `L-101 | 2026-10-21 | invariant | src/codecompass/oracle.py
  (run_pytest_check's PYTHONPATH pin + _interpreter_for) +
  tests/test_oracle.py (test_deliberately_broken_implementation_produces_fail,
  test_passing_result_cannot_verify_subsequently_modified_candidate) @
  ebca4bf`. Independently confirmed real, not just asserted: grepped
  `src/codecompass/oracle.py` and found `_interpreter_for` (line 306)
  and an explicit `env["PYTHONPATH"] = str(repo_root)...` assignment
  inside `run_pytest_check` (lines 333-336); read both named tests in
  `tests/test_oracle.py` directly and confirmed each genuinely exercises
  the scenario the learning describes (a real scratch-copy mutation, a
  real pytest re-run, a real outcome assertion) — the promotion's cited
  evidence is accurate, not a status flip with an unverified citation.
- `planning/CONTEXT.md` correctly still describes "No roadmap phase is
  `in progress`" / "Planning only — no Phase 82-88 implementation" —
  **this is expected** per the task's own note and `CLAUDE.md` §5's
  terminal-reconciliation exemption; not flagged as a gap.

## 7. Protected-file drift

- `git diff bb10927 HEAD -- CLAUDE.md` → **empty**. `CLAUDE.md` was not
  touched anywhere across this phase's entire commit range (confirmed
  against the commit immediately before this phase's planning work
  began, not just the implementation commit).
- `decisions/0078.md`, `0079.md`, `0080.md`, `0081.md`: each has exactly
  one commit in `git log --oneline --follow`, its own original creation
  commit (`bb10927`, `47ab61c`, `2750752`, `d945864` respectively) — no
  ADR was edited in place after its own creation. Append-only confirmed.

## Changed-file list vs plan scope

`git show --stat` on `ebca4bf` (implementation), `62b2f39` (retro),
`63f4d84` (triage), and `a450bfe` (docs-drift fix) were all read in
full. Every changed file is one of: the plan's own named new modules
(`src/codecompass/oracle.py`,
`knowledge_intermediate.py::derive_epistemic_profile`,
`scripts/check_contracts.py`,
`scripts/run_balance_from_spec_oracle.py`,
`check_knowledge_base.py`'s one new check), the plan's own named new
knowledge/contract artifacts (`planning/knowledge/balance-from-spec/*`,
`planning/contracts/balance-from-spec/*`), their test files, the
same-commit `docs/`/`architecture/` updates §2 requires, `CHANGELOG.md`,
the plan file itself, `planning/ROADMAP.md`, `planning/v2-roadmap.md`,
the new ADR files, `planning/learnings/{inbox,promoted}.md`, and the
retro. No scope creep into any file the plan didn't name or imply.

## Other DoD items checked, not applicable

- Item 8 (context-evaluator report for a reference-project phase): not
  applicable — Phase 82 reuses the already-established Ledgerkit
  reference project (Phases 45-78); it does not introduce a new one.
- Item 9 (domain-staleness term check): not applicable —
  `docs/domain/` does not exist in this repository.
- Item 10 (corrective-pass scrutiny): not applicable — Phase 82's
  implementation (`ebca4bf`) is a first implementation, not a
  corrective pass of an earlier, already-shipped version of this same
  phase. The three ADR amendments (`0079`/`0080`/`0081`) were all
  planning-only corrections made *before* any code was written.

## Summary for the lead

Everything the plan's own exit gate (§11) requires is real and was
independently re-demonstrated, not merely trusted from a report:
Requirement → Claims → Evidence citing a real source location → oracle
contract → a real `PASS` re-run against the live checkout → a real
`FAIL` against a deliberately introduced defect, with vacuous
verification shown to fail closed by actually breaking it. Full
regression is clean (980 passed / 2 unrelated pre-existing skips, ruff
clean, three `--strict` checks clean). Doc-sync fixes in `a450bfe` were
checked against the files directly and are accurate. Protected-file
and ADR append-only rules hold. The one gap — no persisted
`_drift-audit-phase-82.md` artifact — is a durable-record-keeping gap,
not a substantive-correctness gap (I independently re-verified the
substance it would have recorded), so it does not block marking Phase
82 `done`, but should be closed by having `docs-reconstructor` write
that report for the historical record before the terminal
reconciliation commit, consistent with Phases 64-80's practice.
