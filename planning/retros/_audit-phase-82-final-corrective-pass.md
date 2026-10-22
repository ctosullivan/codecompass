# Independent completion audit — Phase 82 final corrective pass

**Auditor:** release-phase-auditor (independent pass, read-only).
**Audited against:** `HEAD` = `4407b38` (confirmed via `git log -1` at
the start of this audit; `git status` clean on entry). The four
final-corrective-pass commits audited, all on top of `e3917ad` (the
first corrective pass's own terminal commit): `65840ca` (ADR `decisions/
0083` + plan §16), `04c0ed2` (implementation + tests + docs + fresh real
oracle evidence), `97ef607` (retro + candidate learning L-103), `4407b38`
(L-103 triage — retained, no code change).

**Verdict: PASS**

Every claim made by the implementing session about this pass was
independently re-derived against the real code and real tool behaviour —
not merely re-run from the shipped tests — and holds. One non-blocking
process observation is recorded (§6) but does not block completion.

---

## 1. Finding A — all-skipped pytest execution — independently falsified

Read `_classify_pytest_junit` (`src/codecompass/oracle.py:438-502`)
directly. Confirmed the new `tests - skipped <= 0` check sits after the
pre-existing `tests == 0` check and before `errors`/`failures`, with its
own distinct `invalid_reason` text.

Constructed and ran my **own** scenarios independently of the shipped
test suite, against real pytest 9.1.1 (`.venv/bin/python -m pytest`),
then fed the resulting real junit-xml into the real
`_classify_pytest_junit`:

- Two tests, both `@pytest.mark.skipif(True, ...)` (a variant the
  shipped tests don't use — they use `@pytest.mark.skip`): junit-xml
  `tests="2" skipped="2"` → **`INVALID`**, reason names "all 2 collected
  test(s) were skipped, not executed."
- Zero-test file (a module with no `test_*` function at all, pytest exit
  code 5, `tests="0"`): → **`INVALID`**, but with the **pre-existing,
  textually distinct** message ("check_reference resolved to zero
  collected tests...") — confirmed the all-skipped fix did not collapse
  into, or mask, the original zero-tests `INVALID` path.
- A single genuinely-executed trivial test (`def test_trivial():
  assert True`): → **`PASS`**, confirming the fix does not
  over-correct against a minimal-but-real execution.
- Mixed skip+pass (`@pytest.mark.skip` + a real passing test): →
  **`PASS`**, reason `None`.
- Mixed skip+fail (`@pytest.mark.skip` + a real failing test): →
  **`FAIL`**.

All five outcomes match the ADR's and plan's claims exactly, confirmed
independently (own test files, own junit-xml generation, own direct
call into `_classify_pytest_junit`, not copy-pasted from the shipped
`tests/test_oracle.py`).

## 2. Finding B — strict validators fail closed — independently falsified end-to-end

Read the exact code paths: `scripts/check_contracts.py::run_all`
(lines 372-392) and `scripts/check_knowledge_base.py::
check_verified_status_cites_passing_oracle_result` (lines 612-666).
Confirmed both `oracle is None` / `oracle is None or ki is None` branches
now construct a `Finding` with no explicit `strict=` override, and the
`Finding` dataclass's own default is `strict: bool = True` in both
scripts (`check_contracts.py:54`, `check_knowledge_base.py:235`) — the
fix is a real default-flip, not merely cosmetic.

Rather than trusting the shipped monkeypatch-based unit tests, I forced a
**genuinely broken import**, not a simulated one:

- `check_contracts.py`: copied only `scripts/check_contracts.py` into an
  empty scratch directory (no `src/` present) and ran it with plain
  system `python3` (confirmed `import codecompass` fails there). Result:
  `check_contracts: 1 finding(s) [contract-codecompass-unimportable]`,
  **exit code 1** under `--strict`.
- `check_knowledge_base.py`: copied the script into a scratch directory
  with `planning/` symlinked back to the real repo but no `src/`, called
  `check_verified_status_cites_passing_oracle_result` directly against
  the real `balance-from-spec` slug under plain `python3`. Result:
  `knowledge-base-oracle-unimportable`, `strict=True`.

Both are real, not monkeypatched, confirmations that `--strict` now
actually exits nonzero in a genuinely broken environment.

**Searched independently for any other call site of the same
import-or-None helpers** (`_load_oracle_module`/
`_load_knowledge_intermediate`) in both scripts via `grep`. Found exactly
three call sites total: the two now-fixed ones, plus
`check_no_pending_reconciliation`'s own `ki is None` branch (left
`strict=False`, explicit). Confirmed this one is justifiably left
informational — it only gates the projection-staleness check (`detect_
anchor_changes`), not any oracle-verification claim; this matches the
ADR's own stated distinction ("the verification machinery itself could
not run" vs. "an optional, non-assurance-critical convenience"). No
other oracle-import-gated check was found left informational anywhere
in either script. A third script, `scripts/check_user_docs.py`, has its
own unrelated `_load_codecompass_generators` import-or-None pattern for
doc-generation drift checks — confirmed out of scope (not an
oracle/knowledge_intermediate import, not named by `decisions/0083`).

## 3. Finding C — outcome-type-before-membership and subprocess OSError handling — independently falsified

Read `parse_oracle_result` (lines 317-394) directly: `isinstance(outcome,
str)` is checked and raises before the `outcome not in _OUTCOME_VALUES`
membership test; `invalid_reason`/`baseline_id`/`environment_descriptor`
are each type-checked via `isinstance(..., str)` when present, before
any use.

Constructed my own malformed-input matrix (not copied from the shipped
tests) and ran it directly against the real `parse_oracle_result`:

| Field / value | Result |
|---|---|
| `outcome=5` (int) | `OracleSchemaError` |
| `outcome=1.5` (float) | `OracleSchemaError` |
| `outcome=None` | `OracleSchemaError` |
| `outcome=['FAIL','PASS']` (list) | `OracleSchemaError` |
| `outcome={'a':1}` (dict) | `OracleSchemaError` |
| `outcome=True` (bool) | `OracleSchemaError` (bool is not `str`) |
| `invalid_reason=True` (bool, outcome=INVALID) | `OracleSchemaError` |
| `invalid_reason=['x']` (list, outcome=INVALID) | `OracleSchemaError` |
| `baseline_id=[]` (empty list) | `OracleSchemaError` |
| `baseline_id=['a','b']` (populated list) | `OracleSchemaError` |
| `baseline_id=''` (empty string) | accepted (valid, if unusual, string) |
| `baseline_id=None` | accepted (field is `str \| None`) |
| `environment_descriptor={'os':'linux'}` | `OracleSchemaError` |
| `environment_descriptor=42` | `OracleSchemaError` |

Every malformed case raised a controlled `OracleSchemaError` — never an
uncaught exception — and every well-typed case was accepted correctly.
Confirmed both the empty-list and populated-list variants of `baseline_id`
are rejected identically (both are lists, not strings), closing exactly
the depth gap the governing prompt's own L-075-style concern would raise.

For the subprocess-launch-failure path, rather than reusing the shipped
tests' "nonexistent cwd" approach, I built a **non-executable interpreter
file** (`chmod -x` on a real file at a fake `.venv/bin/python`) and called
`run_pytest_check` against it directly. Result: a real `OSError`
(`[Errno 13] Permission denied`), caught, classified **`INVALID`** with
the exact `OSError` text preserved in both `invalid_reason` and the raw
diagnostic text — no uncaught exception.

## 4. Regression check — no unintended behavioural change

- The real committed `balance-from-spec` contract's two check results
  dated `2026-10-22T12:4x` (this pass's own fresh evidence, confirmed via
  `git log -1` per file to land in `04c0ed2`) have raw output showing
  `1 passed` (a dot, not an `s`) for both
  `test_multi_section_correct_values` and
  `test_single_section_rows_and_subtotal` — genuinely executed,
  non-skipped tests, confirmed unaffected by finding A's new INVALID
  path.
- Full regression suite, re-run independently: **1006 passed, 2 skipped,
  0 failed** (282s) — exact match to the implementing session's claim.
- `ruff check .`: **All checks passed.**
- `scripts/check_contracts.py --strict` against the real repo: **no
  findings**, exit 0.
- `scripts/check_knowledge_base.py --strict` against the real repo: **24
  findings**, all `knowledge-base-snapshot-current-divergence`
  (informational), exit 0 — exact match to the claimed count and
  category.
- `scripts/check_user_docs.py --strict`: **no findings**, exit 0.
- None of `decisions/0080`/`0081`/`0082`'s design, or the first
  corrective pass's own four fixes, is touched by this pass's diff
  (`git diff e3917ad..4407b38` touches only `oracle.py`,
  `check_contracts.py`, `check_knowledge_base.py`'s named functions, new
  tests, docs, `CHANGELOG.md`, the new result/raw-output file pair,
  `planning/learnings/inbox.md`, the retro, and the plan/ADR files).

## 5. CLAUDE.md §5 DoD conditions

- **Plan's own §16 verification step passes**: confirmed directly above
  (regression suite, ruff, both strict validators, real
  Ledgerkit-backed fresh evidence).
- **`docs/`, `architecture/`, `decisions/` updated in the right commit**:
  `04c0ed2` updates `docs/architecture/components.md`, `docs/decisions.md`,
  `docs/development/contributing.md` — spot-checked each against the real
  code (the `oracle.py` row's new "all-skipped"/"subprocess-launch-failure"
  language, `check_contracts.py`'s new import-fail-closed sentence,
  `run_balance_from_spec_oracle.py`'s new INVALID-not-PASS sentence) —
  all accurate, no drift found. `decisions/0083` created in `65840ca`,
  never amended afterward (confirmed via `git log --follow`) — no past
  ADR content touched.
- **Changelog entry**: present in `04c0ed2` under `[Unreleased] →
  Fixed`, scoped to this pass only, accurately describing all three
  findings and the 12-test-function claim (independently recounted via
  diff: 9 in `tests/test_oracle.py` + 2 in `tests/test_check_contracts.py`
  + 1 in `tests/test_check_knowledge_base.py` = 12, exact match).
- **`planning/CONTEXT.md` / `planning/ROADMAP.md` / plan Status line**:
  **not yet updated** to reflect this pass — they still describe the
  state as of `e3917ad` (the first corrective pass's own terminal
  commit). This is **expected, not a defect**: per CLAUDE.md §5's named
  exemption, the terminal `roadmap-context-curator` reconciliation
  commit (which flips these three targets, and only these three) is
  explicitly deferred until *after* this independent audit authorizes
  it — exactly the same sequencing the first corrective pass followed
  (its own terminal reconciliation, `e3917ad`, landed only after its
  reaudit's PASS, `59942e6`). This audit's PASS is what authorizes that
  commit to happen next; it is not yet overdue.
- **Retro matches `TEMPLATE.md`'s full shape**: `planning/retros/
  phase-82-final-corrective-pass.md` has all ten sections (Where we are,
  Goal, Scope delivered vs planned, What was achieved, What worked, What
  didn't work, Lessons learnt, Process-improvement feedback, Candidate
  learnings filed, Where we're going, Time/cost note), each substantive
  — explicitly does not repeat the first corrective pass's own
  under-specified-retro mistake (`_audit-phase-82-corrective-pass.md`'s
  §7 FAIL).
- **Candidate learning triaged**: L-103's `inbox.md` entry
  (`planning/learnings/inbox.md:11`) has `status: retained`, a
  curation note with a concrete, checkable grep methodology and three
  named "safe shape" findings — spot-checked two of the three directly
  (`CAPABILITIES` is a tuple at `adapters/external_process.py:32`, not a
  set; `_require_schema_version`/`_require_execution_provider` in
  `oracle.py:235-250` already type-check before membership-check) — both
  hold. `scripts/check_user_docs.py --strict` (which includes
  `check_learnings_status_matches_retain_outcome`) passes clean against
  the current state.
- **No protected-file drift**: `git diff e3917ad..4407b38 -- CLAUDE.md
  decisions/` touches only the new `decisions/0083-*.md` file (156
  insertions, 0 deletions to any pre-existing file) — `CLAUDE.md`
  untouched, no past ADR's original content edited.
- **Changed-file list matches plan scope**: full `git diff e3917ad..
  4407b38 --stat` is `CHANGELOG.md`, the new ADR, three `docs/` files,
  four new result/raw-output files, `planning/learnings/inbox.md`, the
  plan file itself, the retro, `scripts/check_contracts.py`,
  `scripts/check_knowledge_base.py`, `src/codecompass/oracle.py`, three
  test files — exactly the scope `decisions/0083`/plan §16 name, no
  creep.
- **Commit authorship**: all four commits (`65840ca`, `04c0ed2`,
  `97ef607`, `4407b38`) authored by the lead (Cormac O'Sullivan) —
  consistent with CLAUDE.md §8 (agents never commit `src/`,
  `decisions/*`, or `CLAUDE.md`).
- **Reference-project / domain-staleness checks**: not applicable —
  this is not a reference-project or context-evaluation phase, and
  `docs/domain/` does not exist in this repository.

## 6. Non-blocking observation

No standalone, persisted `docs-reconstructor` per-phase drift-audit
report (e.g. a `_drift-audit-phase-82-final-corrective-pass.md`) exists
for this pass, unlike the precedent set at Phase 81's second corrective
pass (`planning/retros/_drift-audit-phase-81-second-corrective-pass.md`).
Neither of Phase 82's *two* corrective passes produced one — this
pattern was already present (and not flagged) at the first corrective
pass's own independently-PASSed audit
(`_audit-phase-82-corrective-pass.md`/`-reaudit.md`), and no mechanical
check (`scripts/check_user_docs.py`) requires this specific file the way
`check_done_phases_have_audit_report` requires a completion-audit report.
I independently re-derived the substance of what such an audit would
check — diffed every `docs/` file this pass touched against the real
code (§5 above) and grepped `docs/`/`architecture/`/`ai-docs/`/
`README.md` for stale references to the changed functions — and found no
actual drift: all three touched doc files describe the current, corrected
behaviour accurately, and `docs/concepts/knowledge-model.md`'s existing
`decisions/0082` discussion is unaffected by (not contradicted by)
`decisions/0083`'s narrower fixes. Recorded as a **process gap worth
closing** (the project's own established convention, demonstrated at
Phase 81, is to persist this report even for a corrective pass) but
**not blocking** this pass's completion, since the substantive DoD
condition (no current-truth doc misdescribes the system) is independently
confirmed to hold.

## 7. What this verdict authorizes

**PASS.** This authorizes the terminal `roadmap-context-curator`
reconciliation commit (CLAUDE.md §5's named exemption): flipping
`planning/ROADMAP.md`'s Phase 82 row text to record this final
corrective pass, overwriting `planning/CONTEXT.md`'s current-state
section to reference `decisions/0083`, and updating
`planning/phase-82-contract-and-evidence-foundation.md`'s own Status
line to point at this audit report — nothing else. Per CLAUDE.md §6,
pushing to `origin` once that commit lands is authorized by this PASS
without a separate per-push confirmation.

Suggested, non-blocking, for whoever next touches this area: consider
having a `docs-reconstructor` pass produce and persist a standalone
drift-audit report for corrective passes going forward, matching the
Phase 81 precedent, so a future audit doesn't have to re-derive that
scope from scratch each time.
