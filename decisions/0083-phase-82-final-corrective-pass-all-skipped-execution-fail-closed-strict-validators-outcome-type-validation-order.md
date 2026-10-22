# 0083: Phase 82 final corrective pass — all-skipped execution is INVALID, strict validators fail closed on missing verification machinery, outcome type validated before enum membership

**Status:** Accepted (extends `decisions/0080`/`0081`/`0082`; does not reverse any of them)

## Context

The Phase 82 corrective pass (`decisions/0082`) fixed four assurance
defects and received an independent PASS. A further, separate
independent post-completion review of that same shipped code — again a
direct corrective-pass governing prompt, not this session's own
initiative — found three additional, narrower assurance weaknesses.
Each was reproduced directly against the real code (not assumed from the
review's own description) before any fix was written.

**A. All-skipped pytest execution incorrectly establishes PASS.**
`_classify_pytest_junit` (`oracle.py`, as corrected by `decisions/0082`
§B) rejects a junit-xml report with `tests="0"`, but a run where every
collected test is individually skipped (`@pytest.mark.skip`) still
reports `tests > 0` — every skipped testcase counts toward the
`<testsuite tests="...">` total. Confirmed directly this session against
real pytest 9.1.1: a two-test file where both tests are skipped exits 0
and produces `tests="2" skipped="2" errors="0" failures="0"`, which
`_classify_pytest_junit`'s prior logic (`tests != 0`, `errors == 0`,
`failures == 0` ⇒ `PASS`) reports as `PASS` — a check reference that
asserted nothing whatsoever about the tested subject's actual behaviour.

**B. Strict validators fail open when required verification modules
cannot be imported.** Both `scripts/check_contracts.py::run_all` and
`scripts/check_knowledge_base.py::check_verified_status_cites_passing_oracle_result`
use the project's established "import-or-None" pattern
(`_load_oracle_module`/`_load_knowledge_intermediate`) for a bare
checkout where `src/` isn't importable. In both locations, a failed
import previously produced a `strict=False` (informational-only)
finding — meaning `--strict` reports success (exit 0) even though every
oracle-contract/oracle-result check (`check_contracts.py`) or the entire
`status: verified` oracle-citation check (`check_knowledge_base.py`) was
silently skipped in its entirety. This is a materially different failure
mode from the pattern's other, genuinely-optional uses (e.g.
`check_no_pending_reconciliation`'s own `ki is None` branch, which skips
only the projection-staleness check, a narrower and non-assurance-
critical concern, left unchanged by this ADR) — a validator cannot
report "no blocking findings" while the specific machinery responsible
for finding them never ran.

**C. Malformed result fields can escape controlled schema validation.**
`parse_oracle_result` (`oracle.py`, prior to this ADR) checked
`outcome not in _OUTCOME_VALUES` (a `set`) before confirming `outcome`
was even a string. `in`/`not in` against a `set` computes `hash(value)`
first; an unhashable YAML value (a list or mapping, e.g. malformed input
`outcome: [FAIL, PASS]`) raises an uncaught `TypeError`, not the
controlled `OracleSchemaError` every other malformed field in this
module already produces — confirmed directly this session
(`hash(['x'])` raises `TypeError: unhashable type: 'list'`). Separately,
the optional fields `baseline_id`, `environment_descriptor`, and
`invalid_reason` were read via `raw.get(...)` with no type validation at
all — a YAML mapping or list in any of these three fields would silently
populate a dataclass field downstream code assumes is `str | None`.
Finally, `run_pytest_check`'s `subprocess.run` call had no handling for
a launch failure (`OSError`, e.g. a broken/unexecutable interpreter
path): such a failure would propagate as an uncaught exception out of
`run_pytest_check` and `evaluate_check`, rather than being classified as
the execution-environment failure it actually is.

## Decision

**A. `_classify_pytest_junit` requires at least one genuinely executed
test before recording `PASS`.**

A new check, placed after the existing `tests == 0` check and before the
`errors`/`failures` checks (an all-skipped run can never also report
`errors`/`failures`, since neither is possible without a test actually
being attempted): if `tests - skipped <= 0`, the result is `INVALID`,
with an `invalid_reason` explicitly naming that all collected tests were
skipped rather than executed. A partially-skipped run (at least one
executed test) is unaffected — confirmed by direct experimentation this
session: a one-skip-one-pass file still classifies `PASS`, and a
one-skip-one-fail file still classifies `FAIL`, exactly as before this
change. No new dependency: `skipped` is already a `<testsuite>` XML
attribute pytest's own `--junit-xml` always emits.

**B. Both named validators fail closed when their own required
verification machinery is unavailable.**

- `check_contracts.py::run_all`'s `oracle is None` branch now returns a
  finding with `strict=True` (the dataclass default — no longer
  explicitly overridden to `False`). The message is unchanged in
  substance (names the import failure and that every oracle check was
  skipped) but now blocks `--strict`.
- `check_knowledge_base.py::check_verified_status_cites_passing_oracle_result`'s
  `oracle is None or ki is None` branch is changed the same way: `strict=True`.
  This function only runs at all for a slug that already has a real
  `oracle-contract.yaml` (the pre-existing compatibility-exemption gate,
  `decisions/0081` §3, checked first and unchanged) — a slug reaching
  this branch has already committed to making an oracle-backed
  verification claim, so failing to confirm it must never read as "no
  problem found."
- No other `strict=False` informational finding in either validator is
  touched — `contract-ledgerkit-checkout-unavailable` (missing external
  checkout, not missing verification *code*), `contract-check-gap`
  (an expected, non-error state), and `check_no_pending_reconciliation`'s
  own `ki is None` branch (projection staleness, not oracle verification)
  all remain exactly as informational as before. The distinction drawn
  here is specifically "the verification machinery itself could not run
  at all," not "an external, optional resource was unavailable."

**C. `parse_oracle_result` validates every field's type before using it,
in an order that cannot itself raise.**

- `outcome`'s type (`isinstance(outcome, str)`) is checked and rejected
  with a named `OracleSchemaError` *before* the `not in _OUTCOME_VALUES`
  membership check, closing the unhashable-value `TypeError` path
  entirely — confirmed this session with both a list and a mapping value.
- `invalid_reason`, when present, must be a string (checked before the
  existing `INVALID` ⇒ non-empty rule, which now operates on an
  already-type-checked value).
- `baseline_id` and `environment_descriptor`, when present, must each be
  a string — both previously unvalidated, read straight from `raw.get(...)`.
- `run_pytest_check` now wraps its `subprocess.run` call in `try`/`except
  OSError`: a launch failure (interpreter cannot be executed at all) is
  classified `INVALID`, with the `OSError`'s own text preserved in both
  the `invalid_reason` and the raw diagnostic output, rather than
  propagating as an uncaught exception.

No new schema framework is introduced; `_SUPPORTED_EXECUTION_PROVIDERS`
remains `{"pytest"}`, unchanged.

## Consequences

- An oracle contract check whose `check_reference` resolves only to
  skipped tests (e.g. all marked `@pytest.mark.skip`, or gated behind an
  unmet `skipif` condition in the target environment) now reports
  `INVALID`, not `PASS` — any existing contract relying on a reference
  that happens to currently skip everything would surface this as a new
  `GAP`/`unconfirmed` state at aggregation, which is the intended,
  corrected behaviour, not a regression. A repository-wide check
  confirms the real `balance-from-spec` contract's two checks both
  resolve to genuinely executed, non-skipped tests — unaffected.
- `check_contracts.py --strict` and `check_knowledge_base.py --strict`
  now exit nonzero in an environment where `codecompass` (or a required
  dependency such as `pyyaml`) cannot be imported at all — previously
  such an environment could report a false "no findings" / exit 0. A
  correctly configured development or CI environment (where `src/` is
  always importable) sees no behavioural change; this only changes
  outcome in the specific broken-environment case the governing prompt's
  own negative control exercises.
- `parse_oracle_result` rejects strictly more malformed input than
  before (unhashable `outcome`, wrongly-typed optional fields) — no
  previously-valid, well-formed result file is affected; both real
  committed result files and this session's two freshly-generated real
  `PASS` results continue to parse without any finding.
- None of `decisions/0080`/`0081`/`0082`'s design — the derived
  epistemic view, oracle-check collection versioning, PASS/FAIL/GAP/
  INVALID precedence/aggregation, immutable per-run evidence naming, or
  the four defects `decisions/0082` already corrected — is reopened or
  reversed by this ADR. Every change above is a further correction to
  how faithfully that existing design is enforced in code.
