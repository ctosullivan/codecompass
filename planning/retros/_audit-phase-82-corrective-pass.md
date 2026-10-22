# Independent completion audit — Phase 82 corrective pass

**Auditor:** release-phase-auditor (independent pass, read-only).
**Audited against:** `HEAD` = `5aebe10` (confirmed via `git log --oneline
-1` at the start of this audit; `git status` clean on entry). The five
corrective-pass commits audited: `078196c` (ADR + plan §15), `098b312`
(implementation), `8fc066e` (retro + L-102), `ae3731d` (L-102 regression
tests), `5aebe10` (promoted.md hash fill).

**Verdict: FAIL**

One concrete, narrow, fully-actionable gap blocks this pass — see §7.
Every code-correctness claim made by the corrective pass was
independently re-derived and holds. This is not a verdict on whether the
four defects are genuinely fixed (they are, robustly, confirmed below) —
it is a verdict on whether every Definition-of-Done condition for this
corrective-pass closeout currently holds, and one does not yet.

---

## 1. Defect A — current vs. historical verification

Read `src/codecompass/knowledge_intermediate.py::derive_epistemic_profile`
and `EpistemicProfile` directly (not the ADR's description). Confirmed:

- `live_repo_root = repo_root if (repo_root is not None and
  repo_root.is_dir()) else None` — gates live confirmation on the path
  actually existing on disk, not merely being passed.
- A required check lands in `verified_scopes` only when `matched_pass and
  live_repo_root is not None`; `elif matched_pass` (live_repo_root is
  None) lands in the new `unconfirmed_scopes`; otherwise (no PASS at all)
  `known_gap_scopes` as before.
- `scripts/check_knowledge_base.py::check_verified_status_cites_passing_oracle_result`
  (line 612) now takes `ledgerkit_root: Path = DEFAULT_LEDGERKIT_ROOT`
  and threads it through to `derive_epistemic_profile` (line 694) instead
  of a hardcoded `None`; fails closed (blocking `Finding`, not
  `strict=False`) whenever `profile.unconfirmed_scopes` is non-empty for
  a `status: verified` record, with a distinct message naming
  "historically recorded PASS that could not be reconfirmed."
- `scripts/check_contracts.py::check_result_integrity` (line 212) adds
  `contract-current-verification-unconfirmable` (blocking,
  `strict=True`), firing only inside the `repo_root is None` branch, and
  only when a `required: true` check has a recorded `PASS`. A checkout
  that's merely unavailable with nothing relying on it yet still gets
  only the pre-existing informational `contract-ledgerkit-checkout-
  unavailable` finding (`strict=False`). Confirmed by reading the actual
  conditional, not assuming from the diff summary.

**Independent adversarial testing (not just re-running the shipped
tests):**

- Called `derive_epistemic_profile` directly against the real
  `CL-BFS-003` (`status: verified`) record with four `repo_root` values:
  `None` → `unconfirmed_scopes` (both scopes); a path that does not
  exist → `unconfirmed_scopes` (both scopes); **an existing-but-wrong
  decoy directory** (an empty scratch dir — the adversarial case not
  explicitly in the shipped test suite) → `known_gap_scopes` (both
  scopes), because `compute_tree_digest` against the decoy raises
  `OracleDigestError`, caught, and returns `INVALID` — `matched_pass`
  stays `False`. **Finding:** this is a real, if minor, labelling
  imprecision — a decoy-but-real directory is reported via the
  `known_gap_scopes` message ("have no current, matching PASS") rather
  than the `unconfirmed_scopes` message ("could not be reconfirmed"),
  even though the operator's intent was closer to the latter. **This
  does not weaken the fail-closed guarantee**: both branches in
  `check_verified_status_cites_passing_oracle_result` trigger the same
  blocking finding (`if ... profile.known_gap_scopes or
  profile.unconfirmed_scopes`), so the record is correctly rejected
  either way. Non-blocking observation, not a defect — recorded for
  completeness since the audit brief explicitly asked for an adversarial
  case beyond the shipped tests.
  - The real `~/projects/ledgerkit` checkout (`repo_root` = the genuine
    sibling project) correctly produced `verified_scopes` for both
    scopes — confirmed no over-correction (a real, currently-matching
    PASS still counts as verified).
- End-to-end: `scripts/check_knowledge_base.py --strict --ledgerkit-root
  /nonexistent/path/xyz` → exit code **1**, with exactly the
  `knowledge-base-verified-status-without-passing-oracle-result` finding
  naming `CL-BFS-003` and the unconfirmed-PASS reason. This is the
  literal fail-closed behaviour the ADR claims, reproduced end-to-end,
  not merely at the unit level.
- `scripts/check_contracts.py --strict` and `scripts/check_knowledge_base.py
  --strict` both run clean (exit 0) against the real, unmodified
  `~/projects/ledgerkit` (confirmed present at commit `7224bb5`, matching
  `EV-BFS-002`/`003`'s own `repository_revision`). `check_knowledge_base.py
  --strict`'s 24 findings are all `knowledge-base-snapshot-current-
  divergence` (informational, `strict=False`, pre-existing and unrelated
  to this phase).

## 2. Defect B — execution-failure classification

Read `_classify_pytest_junit`/`run_pytest_check` in `src/codecompass/oracle.py`
directly. Independently reproduced, not trusted from the ADR:

- Confirmed `.venv/bin/python -c "import pytest"` → `9.1.1`, matching the
  ADR's claimed version exactly.
- Built five real scratch pytest scenarios (good pass, good fail,
  nonexistent node id, broken-import collection error, zero-match file)
  plus a nonexistent file path, and ran real `pytest -q --junit-xml=...`
  against each with this exact interpreter. **Measured exit codes: 0
  (pass), 1 (fail), 4 (invalid node id / nonexistent file), 2
  (collection error), 5 (zero tests)** — exactly matching the ADR's and
  retro's claimed values.
- Fed the five real junit-xml files produced directly into
  `_classify_pytest_junit` (imported the real module, not a re-
  implementation): PASS, FAIL, INVALID×3 (zero-collected-tests reason
  for node-id/zero-tests/nonexistent-file; collection-error reason for
  the broken import) — matches exactly.
- Ran the full `run_pytest_check(repo_root, check_reference)` end-to-end
  against the scratch fixtures (falls back to this environment's own
  interpreter since the scratch dir has no `.venv`, which itself
  confirmed `_interpreter_for`'s fallback branch): same five outcomes.
- Also tested a **fifth real pytest exit code not named by the ADR's own
  four conditions**: a test file whose only test is unconditionally
  `@pytest.mark.skip`-marked. Real pytest: exit 0, junit-xml shows
  `tests="1" errors="0" failures="0"` (pytest counts a skip in `tests`).
  `_classify_pytest_junit` therefore returns **PASS** for a check
  reference that never actually executed any assertion. **This is a
  real, non-blocking residual gap** — outside the four named defects
  this corrective pass was commissioned to fix, and not a regression
  introduced by it (the pre-existing bare-exit-code logic would also
  have called exit-0 "PASS"). Recorded as a candidate finding for a
  future phase, not a blocker for this one, since defect B's own named
  scope (ADR text, decisions/0082 §B) is exactly the four conditions it
  addresses and all four are genuinely, verifiably fixed.
- `bare /usr/bin/python3` lacking `pytest` at all reproduced the "missing
  dependency" branch for free (`ModuleNotFoundError`, exit 1, no
  junit-xml written) — `_classify_pytest_junit` on a missing file
  correctly returns `INVALID` with the "execution environment itself
  failed" reason.

## 3. Defect C — immutable oracle-result evidence

- `oracle.py::evaluate_check` and `run_balance_from_spec_oracle.py` both
  construct `f"{check_id}--{run_id}.yaml"` / `.txt` — read directly,
  confirmed.
- `git log --follow` on both renamed result files resolves back through
  `078196c` to the original Phase 82 implementation commit `ebca4bf`,
  confirming real rename history, not fresh files. Diffed the exact
  committed blobs at `ebca4bf` vs. `078196c`: **byte-identical
  (`sha256sum` match)** — a pure `git mv`, no content rewrite, exactly as
  claimed. The one-line `raw_output_ref` content update inside the YAML
  happens in the next commit (`098b312`), consistent with the two-step
  rename-then-update-pointer sequence and not a contradiction of the ADR's
  "pure rename" claim about `078196c` specifically.
- `EV-BFS-002.yaml`/`EV-BFS-003.yaml`'s `test_ref` fields updated to the
  new filenames in `098b312`, same commit as the implementation.
- **Independently re-ran `scripts/run_balance_from_spec_oracle.py`
  myself** against the real `~/projects/ledgerkit`: produced two new,
  genuinely fresh `PASS` results with new `run_id`s; confirmed via `git
  status` that all four previously-committed result/raw files (two from
  `2026-10-21`, two from `2026-10-22` in `098b312`) were untouched —
  only new untracked files appeared. Deleted my own scratch artifacts
  afterward; `git status` clean.
- **Authenticity check on the two new result files already committed in
  `098b312`** (not just my own re-run): independently recomputed
  `tested_subject_digest`/`test_input_digest` via
  `oracle.compute_tree_digest` against the real `~/projects/ledgerkit`
  checkout and got **exact matches** to the committed
  `single-section-expense-subtotal--20261022T093853996670Z-95d133e1.yaml`
  values; independently `sha256sum`'d the committed raw-output file and
  it matches the recorded `raw_output_sha256` exactly. These are real,
  reproducible results, not fabricated.

## 4. Defect D — strict schema type/value enforcement

Read `parse_oracle_contract`/`parse_oracle_result` and the new
`_require_bool`/`_require_int`/`_require_schema_version`/
`_require_execution_provider`/`_require_non_empty_str`/`_require_str_list`
helpers directly in `src/codecompass/oracle.py`. Confirmed: `required`
now requires `isinstance(value, bool)` (closing `bool("false") is
True`); `schema_version` requires a real `int` (excluding `bool`, a
`int` subclass) in `_SUPPORTED_SCHEMA_VERSIONS = {1}`;
`execution_provider` checked against `_SUPPORTED_EXECUTION_PROVIDERS =
{"pytest"}` at parse time in both contract and result parsing (not only
at `evaluate_check` time); every string identifier field requires
non-empty-after-strip; `tested_paths`/`test_input_paths`/
`test_input_paths` require non-empty lists of non-empty strings;
`yaml.safe_load` wrapped, `yaml.YAMLError` → `OracleSchemaError`. All of
this read directly from the current file, not assumed from the ADR.

## 5. Full regression suite and ruff

- `.venv/bin/python -m pytest -q`: **994 passed, 2 skipped** (0:04:17).
  Matches the commit message's "991 passed, 2 skipped" plus the 3 new
  regression tests landed in `ae3731d` for L-102 (994 = 991 + 3).
- `.venv/bin/python -m ruff check .`: **All checks passed.**
- Ran the new/changed test modules in isolation too:
  `tests/test_check_knowledge_base.py tests/test_check_contracts.py
  tests/test_knowledge_intermediate.py tests/test_oracle.py` → 192
  passed.
- **Falsification check on the new L-102 regression tests** (requested
  explicitly by the governing brief): wrote a throwaway test file
  (outside the repo, in scratch) that monkeypatches
  `oracle._classify_pytest_junit` back to the pre-fix bare-exit-code
  logic (`"FAIL" if returncode else "PASS"`) and called the real
  `run_pytest_check` against an invalid node id. **It genuinely fails**
  (`AssertionError: assert 'FAIL' == 'INVALID'`) — confirming
  `test_run_pytest_check_invalid_node_id_is_invalid_not_fail` (and its
  siblings) are not vacuous; they would catch a real regression of
  defect B. Deleted the scratch file afterward.
- New negative-control tests for defect A
  (`test_valid_result_no_mismatch_finding_but_current_verification_unconfirmable`,
  `test_no_recorded_pass_yet_stays_informational_only`,
  `test_historical_pass_without_live_checkout_fails_closed`) and the two
  expanded `derive_epistemic_profile` scenario tests (scenario 2 and
  scenario 4, now exercising a real, live-computed digest via a scratch
  "repo" fixture plus the explicit `None`/nonexistent-path negative
  control) were read directly — real digest computation against
  fabricated-but-real fixture files, not placeholder hex strings
  pretending to be digests. High-quality, depth-checking tests (matching
  the project's own `L-075` standard), not merely scope-checking ones.

## 6. Git history, protected files, scope

- `git diff c2902ec..HEAD -- CLAUDE.md`: empty. Untouched.
- `git log --oneline c2902ec..HEAD -- decisions/0078* decisions/0079*
  decisions/0080* decisions/0081*`: empty. All four prior ADRs
  untouched; `decisions/0082` is new (`078196c`), not an edit to an
  existing file.
- `git diff --name-status c2902ec..HEAD`: 25 files touched, all of them
  directly explained by the four named defects (`src/codecompass/
  knowledge_intermediate.py`, `src/codecompass/oracle.py`,
  `scripts/check_contracts.py`, `scripts/check_knowledge_base.py`,
  `scripts/run_balance_from_spec_oracle.py`), their required test files,
  the new ADR, the plan's own §15, `CHANGELOG.md`, the four `docs/`
  files actually describing the affected behaviour
  (`architecture/components.md`, `concepts/knowledge-model.md`,
  `decisions.md`, `development/contributing.md`), the renamed/new
  result/raw evidence files, the two `EV-BFS-00{2,3}` `test_ref` updates,
  the retro, and the learnings inbox/promoted files. Two result-file
  pairs show as git-detected renames (`R091`/`R100`), confirming history
  preservation, not delete+recreate. **No scope creep** — nothing touches
  a file the ADR/plan §15 doesn't account for.
- `planning/phase-82-contract-and-evidence-foundation.md`'s Status line
  correctly reads "done ... A corrective pass (2026-10-22, decisions/0082,
  §15 below) subsequently fixed four assurance defects ... Phase 82
  remains done throughout; the corrective pass is its own closeout, not a
  reopening." Not corrupted. §15's own closing paragraph explicitly
  states the plan's status line will not be touched again until after
  this audit — consistent with what I found (no premature "Independently
  audited" sentence yet referencing this report).
- `planning/CONTEXT.md` and `planning/ROADMAP.md` are **not yet** updated
  to reflect the corrective pass (confirmed via `git log --oneline
  c2902ec..HEAD -- planning/CONTEXT.md` / `-- planning/ROADMAP.md`, both
  empty). **This is expected, not a defect**: `CLAUDE.md` §5's own named
  exemption reserves exactly this update for the terminal
  `roadmap-context-curator` reconciliation commit that follows a PASS
  verdict from this audit (matching the original Phase 82 precedent:
  audit commit `a3d4045` preceded the terminal reconciliation commit
  `c2902ec`, in that order). Noted here as the correctly-sequenced next
  step once §7's gap is closed and a fresh audit passes — not listed as
  a numbered defect.

## 7. Blocking finding — the corrective-pass retro is not fully populated against `TEMPLATE.md`

`planning/retros/phase-82-corrective-pass.md` has: a Date/Trigger intro
line (not the template's own `- **Date:**`/`- **Commit(s):**`/`- **Agents
used:**` bullet block), `## Goal`, `## Delivered vs. planned`, `##
Lessons learnt`, `## Process-improvement feedback`, and a closing
pointer to the learnings inbox. It is **missing**, entirely: `## Where we
are` (arc/stage context — which milestone group, what the prior phase(s)
established, the project state after this pass), an explicit `## What
worked` / `## What didn't work` split (the current retro folds
everything into "Delivered vs. planned" + "Lessons learnt" — real
content, but not in the structure the template requires, and no
dedicated "what cost more than it returned" accounting), `## Where we're
going` (next phase(s), the Phase 83 gate ahead, whether this pass
confirmed or changed the trajectory), and `## Time / cost note`.

This is not a stylistic nitpick:

- This corrective pass is **not trivial** — four real assurance defects,
  a new ADR, a 792-line implementation diff across 22 files, 12+ new test
  functions — so the "a few lines suffice for a trivial phase" carve-out
  in `CLAUDE.md` §5 / my own operating brief does not apply.
- Direct project precedent contradicts treating this as acceptable:
  `planning/retros/phase-81-second-corrective-pass.md`,
  `-third-corrective-pass.md`, and `-corrective-pass.md` (all prior
  corrective passes in this same project) are each fully populated
  against every `TEMPLATE.md` section, including `Where we are` and
  `Where we're going`.
- The *original* Phase 82 audit (`planning/retros/_audit-phase-82.md`
  §6) explicitly checked this exact property for the original phase's
  own retro and named it as a condition for that PASS ("fully populated
  against `TEMPLATE.md`'s shape: Where we are, Goal, ... Where we're
  going, Time/cost note. Not a stub.") — the same standard this audit is
  required to apply here, and the corrective-pass retro does not meet
  it.

**What must be fixed before re-audit:**

1. Expand `planning/retros/phase-82-corrective-pass.md` to cover every
   `TEMPLATE.md` section substantively: add the `- **Date:**` / `-
   **Commit(s):**` / `- **Agents used:**` header bullets; add `## Where
   we are` (this pass's place in the v2/Stage arc, what Phase 82's
   original implementation established that this pass is correcting, the
   project state now); split the existing narrative explicitly into `##
   What worked` and `## What didn't work` (the current content has real
   material for both — e.g. "direct experimentation over trusting
   pytest's own docs" worked; nothing substantial seems to have failed
   this session, which is itself a valid, honest "what didn't work: no
   misfires" answer per the template's own guidance); add `## Where we're
   going` (Phase 83 "Semantic Change Assurance" is next and not yet
   phase-planned; note whether this corrective pass changes that
   trajectory — it does not, per `decisions/0082`'s own Consequences
   section, but the retro should say so in its own voice); add `## Time /
   cost note`.
2. Re-run this audit against the fixed retro commit before treating the
   corrective pass as closed.

No other defect was found. Everything in §§1-6 above independently
confirms the four defects are genuinely, robustly fixed — re-derived by
direct code reading, live reproduction against real pytest and the real
`~/projects/ledgerkit` checkout, adversarial testing beyond the shipped
test suite, and a falsification check on the new regression tests
themselves. Once the retro gap in §7 is closed, I would expect a
re-audit of this same scope to return PASS (or PASS WITH NON-BLOCKING
OBSERVATIONS for the two already-noted non-blocking residuals: the
decoy-directory `known_gap_scopes`-vs-`unconfirmed_scopes` labelling
imprecision in §1, and the all-tests-skipped-still-PASS residual gap in
defect B's own classification in §2 — neither undermines the four named
defects' own fixes, both are out of this corrective pass's named scope).
