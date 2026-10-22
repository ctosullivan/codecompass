"""Tests for src/codecompass/oracle.py (Phase 82 — oracle contract/result
schema, tested-subject digesting, PASS/FAIL/GAP/INVALID precedence and
aggregation). See planning/phase-82-contract-and-evidence-foundation.md
§10 and decisions/0080/0081 for the required scenario list this file
implements, including the governing prompt's own twelve required
verification items.

Several tests exercise the real `~/projects/ledgerkit` sibling checkout
(this project's own established reference project, Phases 45-78) --
skipped when that checkout is not present in this environment, since it
is a dev-environment fixture, not something this repository bundles or
CI is guaranteed to have.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from codecompass import oracle

LEDGERKIT_ROOT = Path.home() / "projects" / "ledgerkit"
_HAS_LEDGERKIT = LEDGERKIT_ROOT.is_dir() and (LEDGERKIT_ROOT / ".venv" / "bin" / "python").is_file()
requires_ledgerkit = pytest.mark.skipif(
    not _HAS_LEDGERKIT,
    reason="~/projects/ledgerkit (with its own .venv) is not present in this environment",
)

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_CONTRACT_PATH = (
    REPO_ROOT / "planning" / "contracts" / "balance-from-spec" / "oracle-contract.yaml"
)

_SYSTEM_PY3 = Path("/usr/bin/python3")


def _system_python_lacks_pytest() -> bool:
    if not _SYSTEM_PY3.is_file():
        return False
    import subprocess

    result = subprocess.run(
        [str(_SYSTEM_PY3), "-c", "import pytest"], capture_output=True, check=False
    )
    return result.returncode != 0


requires_system_python_without_pytest = pytest.mark.skipif(
    not _system_python_lacks_pytest(),
    reason="/usr/bin/python3 is absent or unexpectedly has pytest installed",
)

_TESTED_PATHS = [
    "ledgerkit/reports.py",
    "ledgerkit/models.py",
    "ledgerkit/parser.py",
    "ledgerkit/query/ast.py",
    "ledgerkit/query/depth.py",
    "ledgerkit/query/eval.py",
    "ledgerkit/query/regex.py",
    "ledgerkit/query/compat.py",
]
_SINGLE_SECTION_CHECK_REF = (
    "tests/test_reports.py::TestBalanceFromSpec::test_single_section_rows_and_subtotal"
)
_MULTI_SECTION_CHECK_REF = (
    "tests/test_reports.py::TestBalanceFromSpec::test_multi_section_correct_values"
)
_TEST_INPUT_PATHS = ["tests/test_reports.py", "tests/fixtures/filtered.journal"]


def _copy_ledgerkit_scratch(dest: Path) -> Path:
    """A disposable, fully runnable scratch copy of the whole Ledgerkit
    package and test tree -- mutated freely by tests, never the real
    checkout (plan §6: "never committed to the real
    ~/projects/ledgerkit repository"). Copies the *whole* `ledgerkit/`
    and `tests/` trees (not just `_TESTED_PATHS`/`_TEST_INPUT_PATHS`) so
    the scratch copy actually runs standalone -- `tested_subject_digest`/
    `test_input_digest` still only ever cover the named, reviewed lists
    (decisions/0081 §4); the extra files exist solely to make the
    environment executable, not to be tracked by either digest.
    `run_pytest_check`'s own `PYTHONPATH=repo_root` ensures the package
    actually imported is this scratch copy, not Ledgerkit's real
    `pip install -e .` registration elsewhere on `sys.path`."""
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(LEDGERKIT_ROOT / "ledgerkit", dest / "ledgerkit")
    shutil.copytree(LEDGERKIT_ROOT / "tests", dest / "tests")
    (dest / ".venv").symlink_to(LEDGERKIT_ROOT / ".venv", target_is_directory=True)
    return dest


def _write_contract(path: Path, *, checks=None) -> None:
    import yaml

    data = {
        "schema_version": 1,
        "contract_id": "REQ-BFS-001",
        "tested_paths": _TESTED_PATHS,
        "checks": checks
        if checks is not None
        else [
            {
                "check_id": "single-section-expense-subtotal",
                "scope": "single-section expense aggregation",
                "execution_provider": "pytest",
                "check_reference": _SINGLE_SECTION_CHECK_REF,
                "test_input_paths": _TEST_INPUT_PATHS,
                "required": True,
            },
            {
                "check_id": "multi-section-income-expense-subtotal",
                "scope": "multi-section income/expense aggregation with sign inversion",
                "execution_provider": "pytest",
                "check_reference": _MULTI_SECTION_CHECK_REF,
                "test_input_paths": _TEST_INPUT_PATHS,
                "required": True,
            },
        ],
    }
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Digests
# ---------------------------------------------------------------------------


def test_compute_tree_digest_deterministic(tmp_path: Path):
    (tmp_path / "a.py").write_text("one")
    (tmp_path / "b.py").write_text("two")
    d1 = oracle.compute_tree_digest(tmp_path, ["a.py", "b.py"])
    d2 = oracle.compute_tree_digest(tmp_path, ["b.py", "a.py"])  # order-insensitive
    assert d1 == d2


def test_compute_tree_digest_changes_with_content(tmp_path: Path):
    (tmp_path / "a.py").write_text("one")
    before = oracle.compute_tree_digest(tmp_path, ["a.py"])
    (tmp_path / "a.py").write_text("ONE MUTATED")
    after = oracle.compute_tree_digest(tmp_path, ["a.py"])
    assert before != after


def test_compute_tree_digest_missing_path_raises(tmp_path: Path):
    with pytest.raises(oracle.OracleDigestError, match="missing.yaml"):
        oracle.compute_tree_digest(tmp_path, ["missing.yaml"])


# ---------------------------------------------------------------------------
# Schema parsing
# ---------------------------------------------------------------------------


def test_parse_oracle_contract_valid(tmp_path: Path):
    contract_path = tmp_path / "oracle-contract.yaml"
    _write_contract(contract_path)
    contract = oracle.parse_oracle_contract(contract_path)
    assert contract.contract_id == "REQ-BFS-001"
    assert len(contract.checks) == 2
    assert contract.check_by_id("single-section-expense-subtotal") is not None
    assert contract.check_by_id("nonexistent") is None


def test_parse_oracle_contract_empty_checks_rejected(tmp_path: Path):
    """Governing prompt item 6 / decisions/0081 §3: an empty required-
    check set can never establish verification -- rejected at parse
    time, the earliest possible point."""
    contract_path = tmp_path / "oracle-contract.yaml"
    _write_contract(contract_path, checks=[])
    with pytest.raises(oracle.OracleSchemaError, match="non-empty"):
        oracle.parse_oracle_contract(contract_path)


def test_parse_oracle_contract_missing_field_rejected(tmp_path: Path):
    import yaml

    contract_path = tmp_path / "oracle-contract.yaml"
    contract_path.write_text(
        yaml.safe_dump({"schema_version": 1, "contract_id": "REQ-X-001"}), encoding="utf-8"
    )
    with pytest.raises(oracle.OracleSchemaError, match="missing required"):
        oracle.parse_oracle_contract(contract_path)


def test_parse_oracle_contract_duplicate_check_id_rejected(tmp_path: Path):
    contract_path = tmp_path / "oracle-contract.yaml"
    check = {
        "check_id": "dup",
        "scope": "s",
        "execution_provider": "pytest",
        "check_reference": "x::y",
        "test_input_paths": ["f"],
        "required": True,
    }
    _write_contract(contract_path, checks=[check, dict(check)])
    with pytest.raises(oracle.OracleSchemaError, match="duplicate check_id"):
        oracle.parse_oracle_contract(contract_path)


def _minimal_result_dict(**overrides) -> dict:
    base = {
        "schema_version": 1,
        "run_id": "r1",
        "contract_id": "REQ-BFS-001",
        "check_id": "single-section-expense-subtotal",
        "scope": "single-section expense aggregation",
        "baseline_id": None,
        "tested_subject_digest": "d" * 64,
        "oracle_contract_id": "REQ-BFS-001",
        "oracle_contract_content_hash": "c" * 64,
        "test_input_digest": "i" * 64,
        "raw_output_ref": "raw.txt",
        "raw_output_sha256": "r" * 64,
        "outcome": "INVALID",
        "executed_at": "2026-10-21T00:00:00Z",
        "execution_provider": "pytest",
        "invalid_reason": "minimal-content edge case",
    }
    base.update(overrides)
    return base


def test_parse_oracle_result_minimal_invalid_content_is_well_formed(tmp_path: Path):
    """CLAUDE.md §1 L-070 (minimal-content edge case): the bare-minimum
    well-formed INVALID result (no optional fields set) must still
    validate successfully."""
    import yaml

    result_path = tmp_path / "result.yaml"
    result_path.write_text(yaml.safe_dump(_minimal_result_dict()), encoding="utf-8")
    result = oracle.parse_oracle_result(result_path)
    assert result.outcome == "INVALID"
    assert result.invalid_reason


def test_parse_oracle_result_missing_required_field_fails_closed(tmp_path: Path):
    import yaml

    data = _minimal_result_dict()
    del data["tested_subject_digest"]
    result_path = tmp_path / "result.yaml"
    result_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(oracle.OracleSchemaError, match="missing required"):
        oracle.parse_oracle_result(result_path)


def test_parse_oracle_result_gap_outcome_rejected(tmp_path: Path):
    """decisions/0081 §2: GAP is never a per-result outcome."""
    import yaml

    result_path = tmp_path / "result.yaml"
    result_path.write_text(
        yaml.safe_dump(_minimal_result_dict(outcome="GAP")), encoding="utf-8"
    )
    with pytest.raises(oracle.OracleSchemaError, match="GAP"):
        oracle.parse_oracle_result(result_path)


def test_parse_oracle_result_invalid_without_reason_rejected(tmp_path: Path):
    import yaml

    data = _minimal_result_dict()
    data["invalid_reason"] = None
    result_path = tmp_path / "result.yaml"
    result_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(oracle.OracleSchemaError, match="invalid_reason"):
        oracle.parse_oracle_result(result_path)


def test_write_oracle_result_roundtrip(tmp_path: Path):
    result = oracle.OracleResult(**_minimal_result_dict(outcome="PASS", invalid_reason=None))
    out_path = tmp_path / "result.yaml"
    oracle.write_oracle_result(out_path, result)
    reparsed = oracle.parse_oracle_result(out_path)
    assert reparsed == result


# ---------------------------------------------------------------------------
# Real execution against the live Ledgerkit checkout (items 1, 3, 11, 12)
# ---------------------------------------------------------------------------


@requires_ledgerkit
def test_real_contract_passes_both_checks_against_unmodified_checkout(tmp_path: Path):
    """Item 1 (a genuine Ledgerkit contract passes its accepted oracle
    check) and item 3 (multiple required checks across different scopes
    evaluated correctly), against the real, currently-committed contract."""
    contract = oracle.parse_oracle_contract(REAL_CONTRACT_PATH)
    assert len(contract.checks) == 2
    assert len({c.scope for c in contract.checks}) == 2  # genuinely distinct scopes

    raw_dir = tmp_path / "raw"
    results = [
        oracle.evaluate_check(
            contract, check, contract_path=REAL_CONTRACT_PATH,
            repo_root=LEDGERKIT_ROOT, raw_output_dir=raw_dir,
        )
        for check in contract.checks
    ]
    assert all(r.outcome == "PASS" for r in results)

    aggregates = oracle.aggregate_contract(
        contract, results, contract_path=REAL_CONTRACT_PATH, repo_root=LEDGERKIT_ROOT
    )
    assert all(a.state == "PASS" for a in aggregates)


@requires_ledgerkit
def test_deliberately_broken_implementation_produces_fail(tmp_path: Path):
    """Item 2: a deliberately incorrect implementation produces FAIL --
    the exit gate's own named negative control, run for real against a
    disposable scratch copy, never the real checkout."""
    scratch = _copy_ledgerkit_scratch(tmp_path / "scratch")
    reports_path = scratch / "ledgerkit" / "reports.py"
    text = reports_path.read_text(encoding="utf-8")
    # Minimal, deliberate defect: invert the sign-inversion condition, so
    # Income (which sets invert=True) stops being inverted -- breaks only
    # the multi-section scope's own assertion, a real, targeted mutation.
    assert "if section.invert:" in text
    mutated = text.replace("if section.invert:", "if not section.invert:", 1)
    assert mutated != text
    reports_path.write_text(mutated, encoding="utf-8")

    contract_path = scratch / "oracle-contract.yaml"
    _write_contract(contract_path)
    contract = oracle.parse_oracle_contract(contract_path)
    multi_check = contract.check_by_id("multi-section-income-expense-subtotal")

    result = oracle.evaluate_check(
        contract, multi_check, contract_path=contract_path,
        repo_root=scratch, raw_output_dir=scratch / "raw",
    )
    assert result.outcome == "FAIL"
    assert "FAILED" in Path(result.raw_output_ref).read_text(encoding="utf-8")


@requires_ledgerkit
def test_passing_result_cannot_verify_subsequently_modified_candidate(tmp_path: Path):
    """Item 7: a passing result does not verify a candidate modified
    after the run."""
    scratch = _copy_ledgerkit_scratch(tmp_path / "scratch")
    contract_path = scratch / "oracle-contract.yaml"
    _write_contract(contract_path)
    contract = oracle.parse_oracle_contract(contract_path)
    check = contract.check_by_id("single-section-expense-subtotal")

    result = oracle.evaluate_check(
        contract, check, contract_path=contract_path,
        repo_root=scratch, raw_output_dir=scratch / "raw",
    )
    assert result.outcome == "PASS"

    # Mutate the scratch copy post-hoc -- any change, not necessarily one
    # that breaks behaviour (plan §6, negative control 1).
    models_path = scratch / "ledgerkit" / "models.py"
    models_path.write_text(models_path.read_text(encoding="utf-8") + "\n# unrelated change\n")

    outcome, reason = oracle.evaluate_result_precedence(
        result, contract, check, contract_path=contract_path, repo_root=scratch
    )
    assert outcome == "INVALID"
    assert "tested_subject_digest" in reason


@requires_ledgerkit
def test_changed_fixture_input_invalidates_prior_result(tmp_path: Path):
    """Item 8 / plan §6 negative control 3: altered fixture/input data
    invalidates a prior result."""
    scratch = _copy_ledgerkit_scratch(tmp_path / "scratch")
    contract_path = scratch / "oracle-contract.yaml"
    _write_contract(contract_path)
    contract = oracle.parse_oracle_contract(contract_path)
    check = contract.check_by_id("single-section-expense-subtotal")

    result = oracle.evaluate_check(
        contract, check, contract_path=contract_path,
        repo_root=scratch, raw_output_dir=scratch / "raw",
    )
    assert result.outcome == "PASS"

    fixture = scratch / "tests" / "fixtures" / "filtered.journal"
    fixture.write_text(fixture.read_text(encoding="utf-8") + "\n; unrelated comment\n")

    outcome, reason = oracle.evaluate_result_precedence(
        result, contract, check, contract_path=contract_path, repo_root=scratch
    )
    assert outcome == "INVALID"
    assert "test_input_digest" in reason


def test_changed_contract_check_reference_invalidates_prior_result(tmp_path: Path):
    """Item 8 (contract side) / plan §6 negative control 2: a result
    citing a prior oracle_contract_content_hash is not reused once the
    contract's own checks change."""
    contract_path = tmp_path / "oracle-contract.yaml"
    _write_contract(contract_path)
    contract = oracle.parse_oracle_contract(contract_path)
    check = contract.check_by_id("single-section-expense-subtotal")

    stale_hash = oracle.sha256_file(contract_path)
    result = oracle.OracleResult(
        **_minimal_result_dict(
            outcome="PASS",
            invalid_reason=None,
            oracle_contract_content_hash=stale_hash,
            scope=check.scope,
        )
    )
    raw_path = tmp_path / "raw.txt"
    raw_path.write_text("ok", encoding="utf-8")
    result.raw_output_ref = str(raw_path)
    result.raw_output_sha256 = oracle.sha256_file(raw_path)

    # Genuinely change the contract (a different check_reference, same
    # contract_id).
    mutated_check = {
        "check_id": "single-section-expense-subtotal",
        "scope": check.scope,
        "execution_provider": "pytest",
        "check_reference": "a::different::node",
        "test_input_paths": ["f"],
        "required": True,
    }
    other = contract.check_by_id("multi-section-income-expense-subtotal")
    _write_contract(
        contract_path,
        checks=[
            mutated_check,
            {
                "check_id": other.check_id,
                "scope": other.scope,
                "execution_provider": other.execution_provider,
                "check_reference": other.check_reference,
                "test_input_paths": other.test_input_paths,
                "required": other.required,
            },
        ],
    )
    new_contract = oracle.parse_oracle_contract(contract_path)
    new_check = new_contract.check_by_id("single-section-expense-subtotal")

    outcome, reason = oracle.evaluate_result_precedence(
        result, new_contract, new_check, contract_path=contract_path, repo_root=None
    )
    assert outcome == "INVALID"
    assert "oracle_contract_content_hash" in reason


def test_tampered_raw_output_produces_invalid(tmp_path: Path):
    """Item 5 / plan §6 negative control 4: tampered raw evidence fails
    closed."""
    contract_path = tmp_path / "oracle-contract.yaml"
    _write_contract(contract_path)
    contract = oracle.parse_oracle_contract(contract_path)
    check = contract.check_by_id("single-section-expense-subtotal")

    raw_path = tmp_path / "raw.txt"
    raw_path.write_text("original passing output", encoding="utf-8")
    result = oracle.OracleResult(
        **_minimal_result_dict(
            outcome="PASS",
            invalid_reason=None,
            oracle_contract_content_hash=oracle.sha256_file(contract_path),
            scope=check.scope,
            raw_output_ref=str(raw_path),
            raw_output_sha256=oracle.sha256_file(raw_path),
        )
    )
    # Tamper after the fact.
    raw_path.write_text("TAMPERED output claiming the same result", encoding="utf-8")

    outcome, reason = oracle.evaluate_result_precedence(
        result, contract, check, contract_path=contract_path, repo_root=None
    )
    assert outcome == "INVALID"
    assert "raw_output" in reason


def test_missing_raw_output_produces_invalid(tmp_path: Path):
    contract_path = tmp_path / "oracle-contract.yaml"
    _write_contract(contract_path)
    contract = oracle.parse_oracle_contract(contract_path)
    check = contract.check_by_id("single-section-expense-subtotal")

    result = oracle.OracleResult(
        **_minimal_result_dict(
            outcome="PASS",
            invalid_reason=None,
            oracle_contract_content_hash=oracle.sha256_file(contract_path),
            scope=check.scope,
            raw_output_ref=str(tmp_path / "does-not-exist.txt"),
            raw_output_sha256="x" * 64,
        )
    )
    outcome, reason = oracle.evaluate_result_precedence(
        result, contract, check, contract_path=contract_path, repo_root=None
    )
    assert outcome == "INVALID"
    assert "does not exist" in reason


def test_scope_mismatch_produces_invalid_not_silently_accepted(tmp_path: Path):
    """Item 9 (precedence rule 2): a result's scope must match the named
    check's own scope exactly."""
    contract_path = tmp_path / "oracle-contract.yaml"
    _write_contract(contract_path)
    contract = oracle.parse_oracle_contract(contract_path)
    check = contract.check_by_id("single-section-expense-subtotal")

    raw_path = tmp_path / "raw.txt"
    raw_path.write_text("ok", encoding="utf-8")
    result = oracle.OracleResult(
        **_minimal_result_dict(
            outcome="PASS",
            invalid_reason=None,
            oracle_contract_content_hash=oracle.sha256_file(contract_path),
            scope="a completely different, non-matching scope",
            raw_output_ref=str(raw_path),
            raw_output_sha256=oracle.sha256_file(raw_path),
        )
    )
    outcome, reason = oracle.evaluate_result_precedence(
        result, contract, check, contract_path=contract_path, repo_root=None
    )
    assert outcome == "INVALID"
    assert "scope" in reason


# ---------------------------------------------------------------------------
# GAP aggregation (item 4, item 9)
# ---------------------------------------------------------------------------


def test_missing_required_evidence_produces_gap_not_fail_or_pass(tmp_path: Path):
    """Item 4: missing required evidence produces GAP, not FAIL or PASS."""
    contract_path = tmp_path / "oracle-contract.yaml"
    _write_contract(contract_path)
    contract = oracle.parse_oracle_contract(contract_path)

    aggregates = oracle.aggregate_contract(
        contract, results=[], contract_path=contract_path, repo_root=None
    )
    assert len(aggregates) == 2
    assert all(a.state == "GAP" for a in aggregates)
    assert all(a.passing_result is None for a in aggregates)


def test_fail_result_does_not_get_reclassified_as_gap(tmp_path: Path):
    """decisions/0081 §2: a FAIL result is never silently reclassified
    as merely missing evidence."""
    contract_path = tmp_path / "oracle-contract.yaml"
    _write_contract(contract_path)
    contract = oracle.parse_oracle_contract(contract_path)
    check = contract.check_by_id("single-section-expense-subtotal")

    raw_path = tmp_path / "raw.txt"
    raw_path.write_text("a failing run", encoding="utf-8")
    fail_result = oracle.OracleResult(
        **_minimal_result_dict(
            outcome="FAIL",
            invalid_reason=None,
            oracle_contract_content_hash=oracle.sha256_file(contract_path),
            scope=check.scope,
            raw_output_ref=str(raw_path),
            raw_output_sha256=oracle.sha256_file(raw_path),
        )
    )
    aggregates = oracle.aggregate_contract(
        contract, [fail_result], contract_path=contract_path, repo_root=None
    )
    this_check = next(a for a in aggregates if a.check_id == check.check_id)
    assert this_check.state == "GAP"  # still no passing evidence
    assert this_check.observed_outcomes == ["FAIL"]  # but the FAIL fact is retained, not erased
    assert this_check.passing_result is None


def test_one_scope_passing_does_not_imply_other_scope_verified(tmp_path: Path):
    """Item 9: verification of one scope never implies verification of
    another."""
    contract_path = tmp_path / "oracle-contract.yaml"
    _write_contract(contract_path)
    contract = oracle.parse_oracle_contract(contract_path)
    single_check = contract.check_by_id("single-section-expense-subtotal")

    raw_path = tmp_path / "raw.txt"
    raw_path.write_text("ok", encoding="utf-8")
    passing = oracle.OracleResult(
        **_minimal_result_dict(
            outcome="PASS",
            invalid_reason=None,
            oracle_contract_content_hash=oracle.sha256_file(contract_path),
            scope=single_check.scope,
            check_id=single_check.check_id,
            raw_output_ref=str(raw_path),
            raw_output_sha256=oracle.sha256_file(raw_path),
        )
    )
    aggregates = oracle.aggregate_contract(
        contract, [passing], contract_path=contract_path, repo_root=None
    )
    by_id = {a.check_id: a for a in aggregates}
    assert by_id["single-section-expense-subtotal"].state == "PASS"
    assert by_id["multi-section-income-expense-subtotal"].state == "GAP"


# ---------------------------------------------------------------------------
# Baseline acceptance (item 11, CLAUDE.md §1 L-087)
# ---------------------------------------------------------------------------


@requires_ledgerkit
def test_evaluate_check_never_mints_a_baseline(tmp_path: Path):
    contract = oracle.parse_oracle_contract(REAL_CONTRACT_PATH)
    check = contract.checks[0]
    result1 = oracle.evaluate_check(
        contract, check, contract_path=REAL_CONTRACT_PATH,
        repo_root=LEDGERKIT_ROOT, raw_output_dir=tmp_path / "raw",
    )
    result2 = oracle.evaluate_check(
        contract, check, contract_path=REAL_CONTRACT_PATH,
        repo_root=LEDGERKIT_ROOT, raw_output_dir=tmp_path / "raw",
    )
    assert result1.baseline_id is None
    assert result2.baseline_id is None
    assert not list(tmp_path.glob("*baseline*"))


def test_accept_baseline_is_the_only_explicit_minting_path(tmp_path: Path):
    baseline_path = tmp_path / "baseline.yaml"
    acceptance = oracle.accept_baseline(
        baseline_path,
        tested_subject_revision="deadbeef",
        oracle_contract_content_hash="c" * 64,
        accepted_by="test",
    )
    assert baseline_path.is_file()
    assert acceptance.baseline_id == oracle.compute_baseline_id("deadbeef", "c" * 64)
    # Deterministic -- the same inputs always mint the same baseline_id.
    assert oracle.compute_baseline_id("deadbeef", "c" * 64) == acceptance.baseline_id


# ---------------------------------------------------------------------------
# decisions/0082 §C -- immutable oracle-result/raw-output evidence
# ---------------------------------------------------------------------------


@requires_ledgerkit
def test_repeated_runs_including_a_failure_preserve_all_historical_evidence(tmp_path: Path):
    """decisions/0082 §C negative control: running the same check
    multiple times, including a deliberately failing execution, must
    never overwrite a prior run's own result/raw-output file -- every
    execution remains independently inspectable and correctly associated
    with its own tested subject."""
    raw_dir = tmp_path / "raw"

    passing_contract = oracle.parse_oracle_contract(REAL_CONTRACT_PATH)
    passing_check = passing_contract.check_by_id("single-section-expense-subtotal")
    result1 = oracle.evaluate_check(
        passing_contract, passing_check, contract_path=REAL_CONTRACT_PATH,
        repo_root=LEDGERKIT_ROOT, raw_output_dir=raw_dir,
    )
    assert result1.outcome == "PASS"

    scratch = _copy_ledgerkit_scratch(tmp_path / "scratch")
    reports_path = scratch / "ledgerkit" / "reports.py"
    text = reports_path.read_text(encoding="utf-8")
    assert "if section.invert:" in text
    reports_path.write_text(text.replace("if section.invert:", "if not section.invert:", 1))
    failing_contract_path = scratch / "oracle-contract.yaml"
    _write_contract(failing_contract_path)
    failing_contract = oracle.parse_oracle_contract(failing_contract_path)
    failing_check = failing_contract.check_by_id("multi-section-income-expense-subtotal")
    result2 = oracle.evaluate_check(
        failing_contract, failing_check, contract_path=failing_contract_path,
        repo_root=scratch, raw_output_dir=raw_dir,
    )
    assert result2.outcome == "FAIL"

    result3 = oracle.evaluate_check(
        passing_contract, passing_check, contract_path=REAL_CONTRACT_PATH,
        repo_root=LEDGERKIT_ROOT, raw_output_dir=raw_dir,
    )
    assert result3.outcome == "PASS"

    # Three distinct runs, three distinct run_ids, three distinct files --
    # none overwritten by a later one, including the FAIL sandwiched
    # between two PASSes of a *different* check_id's own raw_output_dir.
    assert len({result1.run_id, result2.run_id, result3.run_id}) == 3
    assert len({result1.raw_output_ref, result2.raw_output_ref, result3.raw_output_ref}) == 3
    assert Path(result1.raw_output_ref).is_file()
    assert Path(result2.raw_output_ref).is_file()
    assert Path(result3.raw_output_ref).is_file()
    assert "FAILED" in Path(result2.raw_output_ref).read_text(encoding="utf-8")
    assert result1.tested_subject_digest == result3.tested_subject_digest
    assert result1.tested_subject_digest != result2.tested_subject_digest  # different subject


# ---------------------------------------------------------------------------
# decisions/0082 §B -- run_pytest_check's own INVALID-vs-FAIL classification
#
# Filed as candidate learning L-102 (planning/learnings/inbox.md):
# knowledge-curator triage correctly found that the real negative-control
# evidence for defect B was gathered via ad hoc interactive invocations
# during this corrective-pass session, not landed as actual regression
# tests calling run_pytest_check directly -- a revert to bare
# exit-code-only classification would have passed every other test in
# this file unchanged. These three close that gap.
# ---------------------------------------------------------------------------


def test_run_pytest_check_invalid_node_id_is_invalid_not_fail(tmp_path: Path):
    (tmp_path / "test_dummy.py").write_text(
        "def test_ok():\n    assert True\n", encoding="utf-8"
    )
    outcome, reason, raw = oracle.run_pytest_check(
        tmp_path, "test_dummy.py::test_does_not_exist_at_all"
    )
    assert outcome == "INVALID"
    assert "zero collected tests" in reason
    assert "returncode" in raw


def test_run_pytest_check_collection_error_is_invalid_not_fail(tmp_path: Path):
    (tmp_path / "test_broken.py").write_text(
        "import this_module_does_not_exist_at_all\n\n"
        "def test_never_reached():\n    assert True\n",
        encoding="utf-8",
    )
    outcome, reason, raw = oracle.run_pytest_check(tmp_path, "test_broken.py")
    assert outcome == "INVALID"
    assert "collection" in reason.lower()
    assert "ModuleNotFoundError" in raw


@requires_system_python_without_pytest
def test_run_pytest_check_missing_pytest_dependency_is_invalid_not_fail(tmp_path: Path):
    """_interpreter_for prefers `repo_root/.venv/bin/python` when present
    -- pointed here at the bare system interpreter, which this project's
    own established precedent (oracle.py's own module docstring, L-101)
    confirms lacks pytest, so no junit-xml report can ever be produced."""
    (tmp_path / "test_dummy.py").write_text(
        "def test_ok():\n    assert True\n", encoding="utf-8"
    )
    venv_bin = tmp_path / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    (venv_bin / "python").symlink_to(_SYSTEM_PY3)

    outcome, reason, raw = oracle.run_pytest_check(tmp_path, "test_dummy.py")
    assert outcome == "INVALID"
    assert "no junit-xml report" in reason
    assert "No module named pytest" in raw


# ---------------------------------------------------------------------------
# decisions/0082 §D -- strict schema type/value enforcement
# ---------------------------------------------------------------------------


def test_required_string_value_rejected_not_silently_truthy(tmp_path: Path):
    """The bool("false") is True defect: a YAML string must never be
    silently accepted where a real boolean is required."""
    contract_path = tmp_path / "oracle-contract.yaml"
    check = dict(
        check_id="c", scope="s", execution_provider="pytest",
        check_reference="t::a", test_input_paths=["f"], required="false",
    )
    _write_contract(contract_path, checks=[check])
    with pytest.raises(oracle.OracleSchemaError, match="real YAML boolean"):
        oracle.parse_oracle_contract(contract_path)


def test_unsupported_schema_version_rejected(tmp_path: Path):
    contract_path = tmp_path / "oracle-contract.yaml"
    import yaml

    contract_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 2,
                "contract_id": "REQ-X-001",
                "tested_paths": ["f"],
                "checks": [
                    {
                        "check_id": "c", "scope": "s", "execution_provider": "pytest",
                        "check_reference": "t::a", "test_input_paths": ["f"], "required": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(oracle.OracleSchemaError, match="schema_version"):
        oracle.parse_oracle_contract(contract_path)


def test_malformed_yaml_rejected_not_an_uncaught_exception(tmp_path: Path):
    contract_path = tmp_path / "oracle-contract.yaml"
    contract_path.write_text("checks: [this is not: valid: yaml: at all", encoding="utf-8")
    with pytest.raises(oracle.OracleSchemaError, match="malformed YAML"):
        oracle.parse_oracle_contract(contract_path)


def test_invalid_execution_provider_rejected_at_parse_time(tmp_path: Path):
    contract_path = tmp_path / "oracle-contract.yaml"
    check = dict(
        check_id="c", scope="s", execution_provider="bespoke-shell-script",
        check_reference="t::a", test_input_paths=["f"], required=True,
    )
    _write_contract(contract_path, checks=[check])
    with pytest.raises(oracle.OracleSchemaError, match="not supported"):
        oracle.parse_oracle_contract(contract_path)


def test_empty_identifier_rejected(tmp_path: Path):
    contract_path = tmp_path / "oracle-contract.yaml"
    check = dict(
        check_id="   ", scope="s", execution_provider="pytest",
        check_reference="t::a", test_input_paths=["f"], required=True,
    )
    _write_contract(contract_path, checks=[check])
    with pytest.raises(oracle.OracleSchemaError, match="non-empty string"):
        oracle.parse_oracle_contract(contract_path)


def test_incorrect_collection_type_rejected(tmp_path: Path):
    contract_path = tmp_path / "oracle-contract.yaml"
    check = dict(
        check_id="c", scope="s", execution_provider="pytest",
        check_reference="t::a", test_input_paths="not-a-list", required=True,
    )
    _write_contract(contract_path, checks=[check])
    with pytest.raises(oracle.OracleSchemaError, match="non-empty list"):
        oracle.parse_oracle_contract(contract_path)


def test_duplicate_check_id_still_rejected_with_new_validation(tmp_path: Path):
    """Confirms decisions/0082 §D's stricter validation did not regress
    decisions/0081's own pre-existing duplicate-check_id rejection."""
    contract_path = tmp_path / "oracle-contract.yaml"
    check = dict(
        check_id="dup", scope="s", execution_provider="pytest",
        check_reference="t::a", test_input_paths=["f"], required=True,
    )
    _write_contract(contract_path, checks=[check, dict(check)])
    with pytest.raises(oracle.OracleSchemaError, match="duplicate check_id"):
        oracle.parse_oracle_contract(contract_path)


def test_result_execution_provider_validated_at_parse_time(tmp_path: Path):
    import yaml

    result_path = tmp_path / "result.yaml"
    result_path.write_text(
        yaml.safe_dump(_minimal_result_dict(execution_provider="carrier-pigeon")),
        encoding="utf-8",
    )
    with pytest.raises(oracle.OracleSchemaError, match="not supported"):
        oracle.parse_oracle_result(result_path)


# ---------------------------------------------------------------------------
# decisions/0082 final corrective pass §A -- all-skipped execution must
# never establish PASS
# ---------------------------------------------------------------------------


def test_run_pytest_check_all_skipped_is_invalid_not_pass(tmp_path: Path):
    """Negative control named by the governing prompt: a valid pytest
    reference containing only skipped tests must never establish
    verification. Confirmed against real pytest 9.1.1 this session: an
    all-skipped run exits 0 and its junit-xml reports tests=2 (every
    skipped testcase counted), errors=0, failures=0 -- `tests > 0` alone
    is not evidence that anything actually ran."""
    (tmp_path / "test_allskip.py").write_text(
        "import pytest\n\n"
        "@pytest.mark.skip(reason='probe')\n"
        "def test_one():\n    assert False\n\n"
        "@pytest.mark.skip(reason='probe')\n"
        "def test_two():\n    assert False\n",
        encoding="utf-8",
    )
    outcome, reason, raw = oracle.run_pytest_check(tmp_path, "test_allskip.py")
    assert outcome == "INVALID"
    assert "skipped" in reason
    assert "skipped in" in raw.lower() or "skipped" in raw.lower()


def test_run_pytest_check_mixed_skip_and_pass_is_still_pass(tmp_path: Path):
    """A partially-skipped run with at least one genuinely executed,
    passing test is unaffected by the all-skipped fix -- only a run
    where *every* collected test was skipped is INVALID."""
    (tmp_path / "test_mixed.py").write_text(
        "import pytest\n\n"
        "@pytest.mark.skip(reason='probe')\n"
        "def test_skip():\n    assert False\n\n"
        "def test_pass():\n    assert True\n",
        encoding="utf-8",
    )
    outcome, reason, raw = oracle.run_pytest_check(tmp_path, "test_mixed.py")
    assert outcome == "PASS"
    assert reason is None


def test_run_pytest_check_mixed_skip_and_fail_is_fail(tmp_path: Path):
    """A partially-skipped run with a genuine behavioural failure is
    still correctly classified FAIL, not swallowed by the skip handling."""
    (tmp_path / "test_mixed2.py").write_text(
        "import pytest\n\n"
        "@pytest.mark.skip(reason='probe')\n"
        "def test_skip():\n    assert False\n\n"
        "def test_fail():\n    assert False\n",
        encoding="utf-8",
    )
    outcome, reason, raw = oracle.run_pytest_check(tmp_path, "test_mixed2.py")
    assert outcome == "FAIL"


# ---------------------------------------------------------------------------
# decisions/0082 final corrective pass §C -- type-before-membership
# validation, optional-field types, subprocess-launch failures
# ---------------------------------------------------------------------------


def test_unhashable_outcome_produces_schema_error_not_type_error(tmp_path: Path):
    """The exact bug named by the governing prompt: parse_oracle_result
    checked `outcome not in _OUTCOME_VALUES` (a set) before confirming
    `outcome` was even a string -- an unhashable YAML value (a list or
    mapping) raised an uncaught TypeError instead of the controlled
    OracleSchemaError every other malformed field produces."""
    import yaml

    result_path = tmp_path / "result.yaml"
    result_path.write_text(
        yaml.safe_dump(_minimal_result_dict(outcome=["not", "a", "string"])),
        encoding="utf-8",
    )
    with pytest.raises(oracle.OracleSchemaError, match="outcome must be a string"):
        oracle.parse_oracle_result(result_path)


def test_unhashable_outcome_is_mapping_also_rejected(tmp_path: Path):
    import yaml

    result_path = tmp_path / "result.yaml"
    result_path.write_text(
        yaml.safe_dump(_minimal_result_dict(outcome={"a": 1})),
        encoding="utf-8",
    )
    with pytest.raises(oracle.OracleSchemaError, match="outcome must be a string"):
        oracle.parse_oracle_result(result_path)


def test_wrongly_typed_invalid_reason_rejected(tmp_path: Path):
    import yaml

    result_path = tmp_path / "result.yaml"
    result_path.write_text(
        yaml.safe_dump(_minimal_result_dict(invalid_reason=["x", "y"])),
        encoding="utf-8",
    )
    with pytest.raises(oracle.OracleSchemaError, match="invalid_reason must be a string"):
        oracle.parse_oracle_result(result_path)


def test_wrongly_typed_baseline_id_rejected(tmp_path: Path):
    import yaml

    result_path = tmp_path / "result.yaml"
    result_path.write_text(
        yaml.safe_dump(_minimal_result_dict(outcome="PASS", baseline_id={"a": 1})),
        encoding="utf-8",
    )
    with pytest.raises(oracle.OracleSchemaError, match="baseline_id must be a string"):
        oracle.parse_oracle_result(result_path)


def test_wrongly_typed_environment_descriptor_rejected(tmp_path: Path):
    import yaml

    result_path = tmp_path / "result.yaml"
    result_path.write_text(
        yaml.safe_dump(_minimal_result_dict(outcome="PASS", environment_descriptor=42)),
        encoding="utf-8",
    )
    with pytest.raises(oracle.OracleSchemaError, match="environment_descriptor must be a string"):
        oracle.parse_oracle_result(result_path)


def test_run_pytest_check_launch_failure_is_invalid_not_uncaught(tmp_path: Path):
    """A subprocess-launch failure (here: cwd that does not exist, so the
    OS itself refuses to launch the interpreter) is an execution-
    environment failure, not a behavioural result -- it must be caught
    and classified INVALID with diagnostic evidence preserved, never
    propagate as an uncaught OSError out of run_pytest_check."""
    nonexistent_repo_root = tmp_path / "no-such-directory"
    outcome, reason, raw = oracle.run_pytest_check(nonexistent_repo_root, "whatever.py")
    assert outcome == "INVALID"
    assert "launch" in reason
    assert "no-such-directory" in raw or "No such file" in raw
