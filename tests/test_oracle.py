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
