# 0082: Phase 82 corrective pass — current vs. historical verification, execution-failure classification, immutable oracle-result evidence, strict schema type enforcement

**Status:** Accepted (extends `decisions/0080`/`0081`; does not reverse either)

## Context

Phase 82 ("Contract and Evidence Foundation") was implemented and marked
`done` (`decisions/0080`/`0081`, commit `c2902ec`). An independent review
after completion, dispatched as a direct corrective-pass governing
prompt, re-examined the actual shipped code — not only the plan — and
found four real assurance weaknesses that survive the original
implementation and its own independent audit. All four were confirmed by
direct inspection and reproduction (not assumed from the review's own
description) before any fix was written:

**A. Current verification without access to current source.**
`derive_epistemic_profile` (`knowledge_intermediate.py`) and
`check_verified_status_cites_passing_oracle_result`
(`check_knowledge_base.py:677`, hardcoded `repo_root=None`) can both
report a `status: verified` record as fully backed using only a
result's own *recorded* digests, never recomputing them against the
actual current implementation. `evaluate_result_precedence`'s own
documented behaviour (`oracle.py:506-507`) already named this exact gap:
"when omitted ... the tested-subject/test-input digests are trusted as
recorded." Separately, `scripts/check_contracts.py`'s own
`contract-ledgerkit-checkout-unavailable` finding
(`check_contracts.py:216-226`) is unconditionally `strict=False`,
meaning `check_contracts.py --strict` exits 0 even when a required
check's only on-record evidence cannot currently be confirmed at all —
an unavailable checkout should never be indistinguishable from a clean
pass.

**B. Execution failures misclassified as behavioural failures.**
`run_pytest_check` (`oracle.py:317-350`) converts any nonzero pytest
exit code into `outcome: FAIL`. Direct experimentation this session
(real `pytest` 9.1.1, both via Ledgerkit's own `.venv` and the bare
system interpreter) confirmed pytest reuses exit code 1 for both a
genuine assertion failure *and* nothing else bad enough to say more —
but separately returns 2 for a collection error (e.g. an `ImportError`
in the test module), 4 for an invalid/nonexistent node id or file path,
5 for a syntactically valid file with zero matching tests, and produces
no output at all (just a bare interpreter error on stderr, return code
1) when the target interpreter altogether lacks the `pytest` package.
None of these four infrastructure/configuration conditions is a
behavioural defect in the tested subject, yet all four currently land as
`FAIL` — a `FAIL` oracle-result is supposed to mean "a valid execution
demonstrates non-satisfaction," which is not what happened in any of
these cases.

**C. Oracle execution destructively overwrites historical evidence.**
`scripts/run_balance_from_spec_oracle.py` (and `oracle.py::evaluate_check`
itself, for its raw-output file) names both the result and raw-output
file for a run purely by `check_id` (`results/<check_id>.yaml`,
`results/raw/<check_id>.txt`) — every subsequent run of the same check
silently overwrites the prior file, including the prior run's own unique
`run_id`, even though `run_id` is already designed to make each
execution individually identifiable. A deliberately failing run,
recorded today, is gone the moment the check is re-run and passes (or
vice versa) — there is no way to inspect "what did the last five runs of
this check actually show," only "what is true right now," which is a
materially weaker evidentiary record than the schema's own `run_id`
field already implies exists.

**D. Insufficient oracle schema type/value validation.**
`parse_oracle_contract` (`oracle.py:185-235`, prior to this ADR)
converts `required` via Python's own `bool(...)` builtin
(`required=bool(entry["required"])`) — `bool("false")` is `True` in
Python, so a contract author writing `required: "false"` (a YAML string,
not a YAML boolean) silently becomes a *required*, not optional, check,
the exact opposite of the authored intent, with no error raised anywhere.
`schema_version` is cast with a bare `int(...)` and never checked against
a supported-version set. `execution_provider` is accepted as any string
at parse time; the one supported-value check lives only in
`evaluate_check`, at execution time, not at schema-validation time.
Malformed YAML (`yaml.safe_load` raising `yaml.YAMLError`) propagates as
an uncaught exception from both parse functions rather than becoming a
reportable `OracleSchemaError` — the same failure mode `check_contracts.py`
and `check_knowledge_base.py` already exist specifically to turn into
controlled findings instead of crashes.

## Decision

**A. Current vs. historical verification is now an explicit, separate
concept, never conflated.**

- `derive_epistemic_profile` gains a new output field,
  `unconfirmed_scopes: list[str]` — distinct from both `verified_scopes`
  (a `PASS` independently reconfirmed against a live, available
  `repo_root`) and `known_gap_scopes` (no citation resolves to any `PASS`
  at all, confirmed or not). A required check whose only citation is a
  *historically recorded* `PASS` — one that cannot currently be
  reconfirmed because no `repo_root` was supplied, or the supplied path
  does not exist on disk — now lands in `unconfirmed_scopes`, never in
  `verified_scopes`. The historical evidence itself is not discarded,
  downgraded, or hidden: it is reported under its own honest name.
- Live confirmation is gated on the checkout actually existing
  (`repo_root is not None and repo_root.is_dir()`), not merely on a
  `repo_root` argument being passed — a caller pointing at a path that
  happens not to exist gets the same honest "unconfirmed" treatment as a
  caller passing `None` outright, rather than a stale-looking `INVALID`
  that would wrongly imply the implementation was actually checked and
  found non-matching.
- `check_verified_status_cites_passing_oracle_result` now accepts and
  threads through a real `ledgerkit_root` (same default,
  `~/projects/ledgerkit`, as `check_contracts.py`'s own convention —
  `scripts/check_knowledge_base.py --ledgerkit-root PATH` is a new,
  optional CLI flag) instead of hardcoding `repo_root=None`. A
  `status: verified` record is now rejected — a blocking finding, not a
  silent pass — whenever any required scope is only `unconfirmed`, with
  a distinct message naming that this is unconfirmed-currentness, not
  simply "this record has never been run at all" (`known_gap_scopes`'s
  own, differently-worded finding). **This is the literal "fail closed
  when current verification is required but the tested implementation
  cannot be inspected" behaviour the corrective-pass prompt names.**
- `scripts/check_contracts.py --strict` gains one new, narrowly-scoped
  blocking finding, `contract-current-verification-unconfirmable`: when
  the Ledgerkit checkout is unavailable *and* at least one `required:
  true` check's only on-record evidence is a historically recorded
  `PASS`, `--strict` now fails rather than silently reporting "no
  findings." The pre-existing informational
  `contract-ledgerkit-checkout-unavailable` finding is unchanged and
  still fires on its own (non-blocking) whenever a checkout is missing,
  including when nothing currently depends on confirming it (e.g. a
  freshly authored contract with no results yet) — unavailability by
  itself is not an error; unavailability *while something is currently
  relying on it* is.
- This does **not** touch the twelve pre-existing `status: verified`
  records' own named compatibility exemption (`decisions/0081` §3) — the
  exemption gate (a slug with no `planning/contracts/<slug>/` directory
  at all) is checked before any oracle logic runs, untouched by this ADR.

**B. Pytest execution outcomes are classified from pytest's own
structured `--junit-xml` report, never from a bare exit code alone.**

`run_pytest_check` now always passes `--junit-xml=<tmp-file>` (a feature
already built into pytest — no new dependency) and classifies the run by
reading the resulting `<testsuite tests=".." errors=".." failures="..">`
element (parsed with the stdlib `xml.etree.ElementTree`, also no new
dependency), in this fixed order:

1. No junit-xml file was produced at all (the interpreter crashed before
   pytest could run — e.g. the target interpreter lacks the `pytest`
   package, confirmed this session via the bare `/usr/bin/python3 -m
   pytest`, exit 1, `No module named pytest`, no XML written) →
   `INVALID`, `invalid_reason` naming the execution could not start, with
   the raw stderr retained for inspection.
2. The junit-xml report parses but `tests="0"` (confirmed this session
   for three distinct causes: an invalid/nonexistent node id, a
   nonexistent file path, and a syntactically valid file with zero
   matching test functions — all three return different pytest exit
   codes, 4/4/5 respectively, but an identical `tests="0"` report) →
   `INVALID`, `invalid_reason` stating the check reference resolved to
   zero collected tests.
3. `errors > 0` (a collection failure — confirmed this session via a
   deliberately broken `import` in a test module, pytest exit code 2) →
   `INVALID`, `invalid_reason` naming the failing module(s) and their
   collection error message(s) from the report's own `<error>` elements.
4. `failures > 0` (confirmed this session via a genuine `assert`
   failure, pytest exit code 1) → `FAIL` — a real, demonstrated
   behavioural defect.
5. Otherwise (`errors == 0`, `failures == 0`, `tests > 0`) → `PASS`.

This is a reliable, already-built-in structured signal, not fragile text
matching against pytest's own human-readable console output, and it
cleanly separates "the tested subject does the wrong thing" (`FAIL`) from
"the check itself could not be meaningfully executed" (`INVALID`) —
exactly the distinction `evaluate_result_precedence`'s own PASS/FAIL/
INVALID precedence rule (`decisions/0081` §2) already assumes is
possible to draw correctly at the point a result is first recorded.
`run_pytest_check`'s return shape changes from `(passed: bool, raw_text:
str)` to `(outcome: str, invalid_reason: str | None, raw_text: str)`;
`evaluate_check` is updated to thread this through directly rather than
re-deriving `PASS`/`FAIL` from a boolean.

**C. Oracle-result evidence becomes immutable per execution; a flat
`check_id`-only filename is never reused across runs.**

- Both the committed `oracle-result.yaml` and its raw-output file are now
  named `<check_id>--<run_id>.yaml` / `<check_id>--<run_id>.txt`
  (`oracle.py::evaluate_check`'s own `raw_output_dir` naming, and
  `scripts/run_balance_from_spec_oracle.py`'s own `results_dir` naming) —
  `run_id` was already guaranteed unique
  (`YYYYmmddTHHMMSSffffffZ-<8 hex>`, a UTC timestamp plus a random
  suffix), so this never collides and sorts chronologically by
  construction. Every run a maintainer executes from this point on
  produces a new, permanent file; nothing already written is ever
  overwritten or deleted by a later run.
- **No new "current pointer" mechanism is introduced.** "Which evidence
  currently applies" is already fully determined by the existing
  mechanism this phase already has: an Evidence record's own `test_ref`
  field cites one specific, named result file, and
  `evaluate_result_precedence`'s own `tested_subject_digest`/
  `test_input_digest` check (§5a, `decisions/0081`) already independently
  confirms whether that cited file's content still matches the current
  implementation — a cited result going stale is detected the same way
  it always was, with or without this ADR. Deciding to cite a *different*
  (e.g. more recent) result remains an explicit editorial action on the
  citing Evidence record, consistent with this project's existing
  "baseline acceptance is explicit, never automatic" posture
  (`CLAUDE.md` §1 L-087) — `run_balance_from_spec_oracle.py` prints the
  new file's path and does not touch any Evidence record itself.
- **Migration of the two already-committed results** (both predate this
  ADR): `results/single-section-expense-subtotal.yaml` and
  `results/multi-section-income-expense-subtotal.yaml` are renamed to
  `results/single-section-expense-subtotal--20261021T085158258751Z-85ec4f35.yaml`
  and
  `results/multi-section-income-expense-subtotal--20261021T085159042773Z-584a42f5.yaml`
  respectively — using each file's own already-recorded `run_id`
  verbatim, a pure rename with no content change (confirmed: `git mv`,
  not a content rewrite). The two corresponding raw-output files move
  the same way. `EV-BFS-002`/`EV-BFS-003`'s own `test_ref` fields are
  updated to the new paths in the same commit as the rename — the one
  place this ADR's migration is visible outside `planning/contracts/`
  itself, named explicitly here rather than left to be discovered later.

**D. Oracle-contract/oracle-result parsing enforces real types and closed
value sets, at parse time, for every field this schema already claims to
constrain — malformed input never reaches an uncaught exception.**

- `yaml.safe_load` is now wrapped in both parse functions: a
  `yaml.YAMLError` becomes `OracleSchemaError("malformed YAML: ...")`,
  not an uncaught exception.
- `required` must be a genuine `bool` (`isinstance(value, bool)`); a
  string, int, or any other type is rejected with a message naming the
  received value and type, explicitly stating that a string is never
  interpreted as a boolean here — directly closing the `bool("false") is
  True` defect.
- `schema_version` must be a real `int` (not a `bool`, which is a Python
  subclass of `int`) and a member of a new, explicit
  `_SUPPORTED_SCHEMA_VERSIONS = {1}` set — an unsupported or malformed
  version is rejected by name.
- `execution_provider` is validated against
  `_SUPPORTED_EXECUTION_PROVIDERS = {"pytest"}` at **parse** time, not
  only inside `evaluate_check` at execution time — the existing
  execution-time check remains as defence in depth for a contract
  constructed directly in code (bypassing the parser, as some unit tests
  already do), but a contract file with an unsupported provider is now
  rejected the moment it is read, before anything tries to run it.
- `check_id`, `scope`, `check_reference`, `contract_id`, and every string
  identifier field must be a non-empty (post-strip) string — an empty or
  whitespace-only identifier is rejected by name, not silently accepted
  as a technically-present field.
- `tested_paths`/`test_input_paths` must each be a non-empty list whose
  every entry is itself a non-empty string — a non-list value, an empty
  list, or a list containing a non-string/empty entry is rejected,
  closing the "incorrect collection type" gap named by the corrective-pass
  prompt.
- Duplicate `check_id` rejection (already present) is unchanged.
- `parse_oracle_result` gains the equivalent non-empty-string
  enforcement for its own required string fields
  (`run_id`/`contract_id`/`check_id`/`scope`/`oracle_contract_id`/
  `oracle_contract_content_hash`/`tested_subject_digest`/
  `test_input_digest`/`raw_output_ref`/`raw_output_sha256`/`executed_at`/
  `execution_provider`), plus the same closed `execution_provider`
  check — `outcome`'s own closed-enum check and the existing
  `INVALID` ⇒ non-empty `invalid_reason` rule are unchanged.

No execution-provider-plugin system is introduced by any of the above —
`pytest` remains the one closed, named value (`decisions/0081` §1,
unchanged).

## Consequences

- `scripts/check_contracts.py --strict` and `scripts/check_knowledge_base.py
  --strict` now require a real, reachable Ledgerkit checkout to report a
  clean pass whenever the `balance-from-spec` contract (or any future
  contract reaching the same code paths) has at least one required
  check's only on-record evidence being a historically recorded `PASS` —
  this is a deliberate, intended tightening: an environment without the
  sibling checkout can no longer produce a false "all clear." Every
  existing ledgerkit-dependent test in this repository was already
  marked `skipif`-guarded for exactly this reason (`requires_ledgerkit`,
  `tests/test_oracle.py`); the one previously unguarded test asserting
  `check_contracts.py`'s real-repository findings
  (`tests/test_check_contracts.py::TestRealRepository`) gains the same
  guard as part of this ADR, since its own assumption now genuinely
  depends on the checkout being present.
- `run_pytest_check`'s new structured classification means an
  `INVALID` outcome is now reachable from four distinct real conditions
  (missing dependency, invalid node id, zero-match file, collection
  error) that previously all silently became `FAIL` — any existing
  external tooling or reader that assumed every nonzero pytest exit code
  means `FAIL` must update that assumption; nothing in this repository
  depended on the old, incorrect behaviour (confirmed by this session's
  own test-suite run before and after the change).
- `planning/contracts/balance-from-spec/results/`'s two existing files
  are renamed (git history preserves the rename, not a deletion); any
  external tooling or documentation that hardcoded the old bare
  `<check_id>.yaml` filename must be updated — a repository-wide grep
  confirmed the only two references were the two `EV-BFS-00{2,3}`
  `test_ref` fields themselves, both updated in the same commit.
- Future maintainer runs of `scripts/run_balance_from_spec_oracle.py`
  accumulate one new, permanent file pair per execution under
  `planning/contracts/balance-from-spec/results/` — an intended,
  accepted growth pattern (mirroring how `planning/knowledge/` itself
  already accumulates append-only records over a project's lifetime),
  not a defect to be pruned by a future phase without an explicit,
  separate retention-policy decision.
- None of Phase 82's exit gate, its one pinned Ledgerkit contract, its
  INTENDED/OBSERVED/VERIFIED/CONTESTED derived-view design, or its
  PASS/FAIL/GAP/INVALID precedence/aggregation rule (`decisions/0080`/
  `0081`) is reopened or reversed by this ADR — every change above is a
  correction to how faithfully the existing design is enforced in code,
  not a change to the design itself.
