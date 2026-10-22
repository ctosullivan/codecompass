"""Tests for scripts/check_contracts.py -- a maintainer-only tool, not
part of the codecompass package. Imported directly from its file path,
same convention as tests/test_check_knowledge_base.py. See
planning/phase-82-contract-and-evidence-foundation.md §8 and
decisions/0080/0081.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

_SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "check_contracts.py"
_spec = importlib.util.spec_from_file_location("check_contracts", _SCRIPT_PATH)
check_contracts = importlib.util.module_from_spec(_spec)
sys.modules["check_contracts"] = check_contracts
_spec.loader.exec_module(check_contracts)

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
from codecompass import oracle  # noqa: E402

LEDGERKIT_ROOT = Path.home() / "projects" / "ledgerkit"
_HAS_LEDGERKIT = LEDGERKIT_ROOT.is_dir()
requires_ledgerkit = pytest.mark.skipif(
    not _HAS_LEDGERKIT, reason="~/projects/ledgerkit not present"
)

_TWO_CHECKS = [
    {
        "check_id": "check-a", "scope": "scope A", "execution_provider": "pytest",
        "check_reference": "t::a", "test_input_paths": ["f"], "required": True,
    },
    {
        "check_id": "check-b", "scope": "scope B", "execution_provider": "pytest",
        "check_reference": "t::b", "test_input_paths": ["f"], "required": True,
    },
]


def _write_contract(
    path: Path, *, contract_id="REQ-CC-001", checks=None, tested_paths=None
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "contract_id": contract_id,
                "tested_paths": tested_paths or ["impl.py"],
                "checks": checks if checks is not None else _TWO_CHECKS,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _write_requirement(root: Path, slug: str, req_id: str) -> None:
    sdir = root / "planning" / "knowledge" / slug
    sdir.mkdir(parents=True, exist_ok=True)
    (sdir / f"{req_id}.yaml").write_text(
        f"id: {req_id}\nkind: requirement\nstatement: s\nexample: e\n"
        "decision: DEC-X-001\nstatus: implemented\n",
        encoding="utf-8",
    )


def _write_result(
    path: Path,
    contract_path: Path,
    *,
    contract_id="REQ-CC-001",
    check_id="check-a",
    scope="scope A",
    outcome="PASS",
) -> oracle.OracleResult:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw_path = path.parent / f"{check_id}-raw.txt"
    raw_path.write_text("ok", encoding="utf-8")
    result = oracle.OracleResult(
        schema_version=1, run_id="r1", contract_id=contract_id, check_id=check_id,
        scope=scope, baseline_id=None, tested_subject_digest="d" * 64,
        oracle_contract_id=contract_id,
        oracle_contract_content_hash=oracle.sha256_file(contract_path),
        test_input_digest="i" * 64, raw_output_ref=str(raw_path),
        raw_output_sha256=oracle.sha256_file(raw_path), outcome=outcome,
        executed_at="2026-10-21T00:00:00Z", execution_provider="pytest",
        environment_descriptor=None, invalid_reason=None,
    )
    oracle.write_oracle_result(path, result)
    return result


class TestContractSchemaCheck:
    def test_valid_contract_no_finding(self, tmp_path):
        contract_path = tmp_path / "oracle-contract.yaml"
        _write_contract(contract_path)
        findings, contract = check_contracts.check_contract_schema(tmp_path, oracle, root=tmp_path)
        assert findings == []
        assert contract is not None

    def test_missing_contract_flagged(self, tmp_path):
        findings, contract = check_contracts.check_contract_schema(tmp_path, oracle, root=tmp_path)
        assert len(findings) == 1
        assert contract is None

    def test_empty_checks_flagged(self, tmp_path):
        contract_path = tmp_path / "oracle-contract.yaml"
        _write_contract(contract_path, checks=[])
        findings, contract = check_contracts.check_contract_schema(tmp_path, oracle, root=tmp_path)
        assert len(findings) == 1
        assert contract is None


class TestContractIdResolves:
    def test_resolves_to_real_requirement(self, tmp_path):
        _write_requirement(tmp_path, "demo-slug", "REQ-CC-001")
        contract_path = tmp_path / "planning" / "contracts" / "demo-slug" / "oracle-contract.yaml"
        _write_contract(contract_path)
        contract = oracle.parse_oracle_contract(contract_path)
        findings = check_contracts.check_contract_id_resolves("demo-slug", contract, root=tmp_path)
        assert findings == []

    def test_dangling_contract_id_flagged(self, tmp_path):
        contract_path = tmp_path / "planning" / "contracts" / "demo-slug" / "oracle-contract.yaml"
        _write_contract(contract_path)
        contract = oracle.parse_oracle_contract(contract_path)
        findings = check_contracts.check_contract_id_resolves("demo-slug", contract, root=tmp_path)
        assert len(findings) == 1
        assert "dangling" in findings[0].rule


class TestResultCrossReferences:
    def test_dangling_check_id_flagged(self, tmp_path):
        slug_dir = tmp_path / "planning" / "contracts" / "demo-slug"
        contract_path = slug_dir / "oracle-contract.yaml"
        _write_contract(contract_path)
        contract = oracle.parse_oracle_contract(contract_path)
        result_path = slug_dir / "results" / "check-x.yaml"
        result = _write_result(result_path, contract_path, check_id="check-x")
        findings = check_contracts.check_result_cross_references(
            slug_dir, contract, [(result_path, result)], root=tmp_path
        )
        assert any(f.rule == "contract-result-dangling-check-id" for f in findings)

    def test_valid_results_no_finding(self, tmp_path):
        slug_dir = tmp_path / "planning" / "contracts" / "demo-slug"
        contract_path = slug_dir / "oracle-contract.yaml"
        _write_contract(contract_path)
        contract = oracle.parse_oracle_contract(contract_path)
        result_path = slug_dir / "results" / "check-a.yaml"
        result = _write_result(result_path, contract_path)
        findings = check_contracts.check_result_cross_references(
            slug_dir, contract, [(result_path, result)], root=tmp_path
        )
        assert findings == []


class TestResultIntegrity:
    def test_tampered_raw_output_flagged(self, tmp_path):
        slug_dir = tmp_path / "planning" / "contracts" / "demo-slug"
        contract_path = slug_dir / "oracle-contract.yaml"
        _write_contract(contract_path)
        contract = oracle.parse_oracle_contract(contract_path)
        result_path = slug_dir / "results" / "check-a.yaml"
        result = _write_result(result_path, contract_path)
        Path(result.raw_output_ref).write_text("TAMPERED", encoding="utf-8")

        findings = check_contracts.check_result_integrity(
            slug_dir, contract, [(result_path, result)], oracle,
            ledgerkit_root=tmp_path / "no-such-dir", root=tmp_path,
        )
        assert any(f.rule == "contract-result-integrity-mismatch" for f in findings)

    def test_valid_result_no_mismatch_finding_but_current_verification_unconfirmable(
        self, tmp_path
    ):
        """decisions/0082 §A: a checkout-unavailable environment never
        reports integrity-mismatch (it cannot compare against anything),
        but a required check's only PASS being merely historical is now
        its own, separate blocking finding -- `--strict` must not report
        clean when it cannot confirm current state at all."""
        slug_dir = tmp_path / "planning" / "contracts" / "demo-slug"
        contract_path = slug_dir / "oracle-contract.yaml"
        _write_contract(contract_path)
        contract = oracle.parse_oracle_contract(contract_path)
        result_path = slug_dir / "results" / "check-a.yaml"
        result = _write_result(result_path, contract_path)

        findings = check_contracts.check_result_integrity(
            slug_dir, contract, [(result_path, result)], oracle,
            ledgerkit_root=tmp_path / "no-such-dir", root=tmp_path,
        )
        assert not any(f.rule == "contract-result-integrity-mismatch" for f in findings)
        # Informational note that the live checkout wasn't available.
        assert any(f.rule == "contract-ledgerkit-checkout-unavailable" for f in findings)
        # New blocking finding: required check-a's only PASS is unconfirmed.
        unconfirmable = [
            f for f in findings if f.rule == "contract-current-verification-unconfirmable"
        ]
        assert len(unconfirmable) == 1
        assert unconfirmable[0].strict is True

    def test_no_recorded_pass_yet_stays_informational_only(self, tmp_path):
        """A required check with no results at all has nothing current to
        misrepresent -- checkout-unavailable stays informational, no new
        blocking finding fires."""
        slug_dir = tmp_path / "planning" / "contracts" / "demo-slug"
        contract_path = slug_dir / "oracle-contract.yaml"
        _write_contract(contract_path)
        contract = oracle.parse_oracle_contract(contract_path)

        findings = check_contracts.check_result_integrity(
            slug_dir, contract, [], oracle,
            ledgerkit_root=tmp_path / "no-such-dir", root=tmp_path,
        )
        assert not any(
            f.rule == "contract-current-verification-unconfirmable" for f in findings
        )
        assert [f.strict for f in findings] == [False]


class TestGapAggregate:
    def test_required_check_with_no_result_is_gap_informational(self, tmp_path):
        slug_dir = tmp_path / "planning" / "contracts" / "demo-slug"
        contract_path = slug_dir / "oracle-contract.yaml"
        _write_contract(contract_path)
        contract = oracle.parse_oracle_contract(contract_path)

        findings = check_contracts.check_gap_aggregate(
            slug_dir, contract, [], oracle, ledgerkit_root=tmp_path / "no-such-dir", root=tmp_path
        )
        assert len(findings) == 2  # both checks are required and have no result
        assert all(not f.strict for f in findings)  # informational, never --strict-blocking

    def test_both_checks_passing_no_gap_finding(self, tmp_path):
        slug_dir = tmp_path / "planning" / "contracts" / "demo-slug"
        contract_path = slug_dir / "oracle-contract.yaml"
        _write_contract(contract_path)
        contract = oracle.parse_oracle_contract(contract_path)
        path_a = slug_dir / "results" / "check-a.yaml"
        r1 = _write_result(path_a, contract_path, check_id="check-a", scope="scope A")
        path_b = slug_dir / "results" / "check-b.yaml"
        r2 = _write_result(path_b, contract_path, check_id="check-b", scope="scope B")

        findings = check_contracts.check_gap_aggregate(
            slug_dir, contract, [(path_a, r1), (path_b, r2)], oracle,
            ledgerkit_root=tmp_path / "no-such-dir", root=tmp_path,
        )
        assert findings == []


class TestSourceRefSymbolDepth:
    def test_real_symbol_at_cited_location_no_finding(self, tmp_path):
        ledgerkit_root = tmp_path / "ledgerkit-fixture"
        (ledgerkit_root / "pkg").mkdir(parents=True)
        (ledgerkit_root / "pkg" / "mod.py").write_text(
            "x = 1\ndef real_function():\n    pass\n", encoding="utf-8"
        )
        feature_dir = tmp_path / "planning" / "knowledge" / "demo-slug"
        feature_dir.mkdir(parents=True)
        (feature_dir / "EV-X-001.yaml").write_text(
            "id: EV-X-001\nkind: evidence\nevidence_kind: source\n"
            "what_it_shows: x\nobservations: null\n"
            'source_ref: "pkg/mod.py:2 def real_function"\n'
            "doc_ref: null\ntest_ref: null\n"
            'repository_revision: "x"\nstatus: current\n',
            encoding="utf-8",
        )
        findings = check_contracts.check_source_ref_symbol_depth(
            feature_dir, ledgerkit_root, root=tmp_path
        )
        assert findings == []

    def test_wrong_symbol_at_cited_location_flagged(self, tmp_path):
        """CLAUDE.md §1 L-075 (depth, not just scope): a citation to a
        real file that doesn't actually contain the cited symbol must
        fail validation, not pass because the path merely resolves."""
        ledgerkit_root = tmp_path / "ledgerkit-fixture"
        (ledgerkit_root / "pkg").mkdir(parents=True)
        (ledgerkit_root / "pkg" / "mod.py").write_text(
            "x = 1\ndef a_totally_different_function():\n    pass\n", encoding="utf-8"
        )
        feature_dir = tmp_path / "planning" / "knowledge" / "demo-slug"
        feature_dir.mkdir(parents=True)
        (feature_dir / "EV-X-002.yaml").write_text(
            "id: EV-X-002\nkind: evidence\nevidence_kind: source\n"
            "what_it_shows: x\nobservations: null\n"
            'source_ref: "pkg/mod.py:2 def real_function"\n'
            "doc_ref: null\ntest_ref: null\n"
            'repository_revision: "x"\nstatus: current\n',
            encoding="utf-8",
        )
        findings = check_contracts.check_source_ref_symbol_depth(
            feature_dir, ledgerkit_root, root=tmp_path
        )
        assert len(findings) == 1
        assert findings[0].rule == "contract-source-ref-symbol-not-found"

    def test_missing_file_flagged(self, tmp_path):
        ledgerkit_root = tmp_path / "ledgerkit-fixture"
        ledgerkit_root.mkdir()
        feature_dir = tmp_path / "planning" / "knowledge" / "demo-slug"
        feature_dir.mkdir(parents=True)
        (feature_dir / "EV-X-003.yaml").write_text(
            "id: EV-X-003\nkind: evidence\nevidence_kind: source\n"
            "what_it_shows: x\nobservations: null\n"
            'source_ref: "pkg/does_not_exist.py:2 def f"\n'
            "doc_ref: null\ntest_ref: null\n"
            'repository_revision: "x"\nstatus: current\n',
            encoding="utf-8",
        )
        findings = check_contracts.check_source_ref_symbol_depth(
            feature_dir, ledgerkit_root, root=tmp_path
        )
        assert len(findings) == 1
        assert findings[0].rule == "contract-source-ref-missing-file"

    def test_real_balance_from_spec_evidence_is_clean(self):
        """The real, committed EV-BFS-001 source_ref citation resolves
        correctly against the real Ledgerkit checkout."""
        feature_dir = REPO_ROOT / "planning" / "knowledge" / "balance-from-spec"
        findings = check_contracts.check_source_ref_symbol_depth(
            feature_dir, LEDGERKIT_ROOT, root=REPO_ROOT
        )
        assert findings == []


class TestRealRepository:
    @requires_ledgerkit
    def test_real_repository_has_no_blocking_findings(self):
        """decisions/0082 §A: with the real checkout available, the real,
        committed balance-from-spec contract's two required checks are
        both live-confirmed PASS -- no blocking finding, including the
        new contract-current-verification-unconfirmable rule, which only
        fires when the checkout is unavailable."""
        findings = check_contracts.run_all(REPO_ROOT, check_contracts.DEFAULT_LEDGERKIT_ROOT)
        assert [f for f in findings if f.strict] == []
