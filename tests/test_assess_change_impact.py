"""Tests for scripts/assess_change_impact.py (Phase 83 -- Semantic Change
Assurance). A maintainer-only tool, not part of the codecompass package --
imported directly from its file path, same convention as
tests/test_check_contracts.py. See planning/phase-83-semantic-change-
assurance.md and decisions/0086/0087 for the full design.

Deliberately independent of the real ~/projects/ledgerkit checkout for
every test below except the small group marked `requires_ledgerkit` --
each constructs its own minimal, disposable fake "target repository"
(a tiny implementation file + pytest test file + a real sqlite graph
database) and its own minimal knowledge-record/contract fixtures,
mirroring tests/test_oracle.py's own `tmp_path`-as-fake-repo convention.
"""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest
import yaml

_SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "assess_change_impact.py"
_spec = importlib.util.spec_from_file_location("assess_change_impact", _SCRIPT_PATH)
aci = importlib.util.module_from_spec(_spec)
sys.modules["assess_change_impact"] = aci
_spec.loader.exec_module(aci)

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
from codecompass import oracle  # noqa: E402

LEDGERKIT_ROOT = Path.home() / "projects" / "ledgerkit"
requires_ledgerkit = pytest.mark.skipif(
    not (LEDGERKIT_ROOT.is_dir() and (LEDGERKIT_ROOT / ".venv" / "bin" / "python").is_file()),
    reason="~/projects/ledgerkit (with its own .venv) is not present in this environment",
)


# ---------------------------------------------------------------------------
# parse_changed_arg
# ---------------------------------------------------------------------------


class TestParseChangedArg:
    def test_range_form(self):
        c = aci.parse_changed_arg("a/b.py:10-20")
        assert (c.path, c.start, c.end) == ("a/b.py", 10, 20)

    def test_single_line_form(self):
        c = aci.parse_changed_arg("a/b.py:10")
        assert (c.path, c.start, c.end) == ("a/b.py", 10, 10)

    def test_missing_colon_rejected(self):
        with pytest.raises(Exception):
            aci.parse_changed_arg("a/b.py")

    def test_non_integer_rejected(self):
        with pytest.raises(Exception):
            aci.parse_changed_arg("a/b.py:ten-twenty")

    def test_end_before_start_rejected(self):
        with pytest.raises(Exception):
            aci.parse_changed_arg("a/b.py:20-10")

    def test_zero_start_rejected(self):
        with pytest.raises(Exception):
            aci.parse_changed_arg("a/b.py:0-5")


# ---------------------------------------------------------------------------
# resolve_enclosing_symbol -- pure function, no DB
# ---------------------------------------------------------------------------


class TestResolveEnclosingSymbol:
    def test_resolves_to_preceding_symbol(self):
        symbols = [
            aci.SymbolRow("foo", "function", 1),
            aci.SymbolRow("bar", "function", 10),
            aci.SymbolRow("baz", "function", 20),
        ]
        assert aci.resolve_enclosing_symbol(symbols, 15).name == "bar"
        assert aci.resolve_enclosing_symbol(symbols, 10).name == "bar"
        assert aci.resolve_enclosing_symbol(symbols, 25).name == "baz"

    def test_line_before_first_symbol_is_unresolved(self):
        symbols = [aci.SymbolRow("foo", "function", 5)]
        assert aci.resolve_enclosing_symbol(symbols, 1) is None

    def test_empty_symbol_list_is_unresolved(self):
        assert aci.resolve_enclosing_symbol([], 1) is None


# ---------------------------------------------------------------------------
# Fake-repo + fake-graph builders, reused across resolve_changed_range and
# classify_symbol/assess tests
# ---------------------------------------------------------------------------


def _write_graph_db(db_path: Path, *, path: str, content_hash: str, symbols: list[tuple[str, str, int]]) -> None:
    con = sqlite3.connect(db_path)
    con.execute(
        "CREATE TABLE source_files (id INTEGER PRIMARY KEY, path TEXT UNIQUE, content_hash TEXT)"
    )
    con.execute(
        "CREATE TABLE source_symbols (id INTEGER PRIMARY KEY, source_file_id INTEGER, "
        "name TEXT, kind TEXT, line INTEGER)"
    )
    cur = con.execute("INSERT INTO source_files (path, content_hash) VALUES (?, ?)", (path, content_hash))
    file_id = cur.lastrowid
    for name, kind, line in symbols:
        con.execute(
            "INSERT INTO source_symbols (source_file_id, name, kind, line) VALUES (?, ?, ?, ?)",
            (file_id, name, kind, line),
        )
    con.commit()
    con.close()


_IMPL_TEXT = (
    "def helper():\n"
    "    return 1\n"
    "\n"
    "\n"
    "def target_function():\n"
    "    return 2\n"
)


def _build_fake_target_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "target-repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "impl.py").write_text(_IMPL_TEXT, encoding="utf-8")
    return repo


def _sync_graph_for(repo: Path) -> Path:
    graph_db = repo / "context-graph.db"
    content_hash = oracle.sha256_file(repo / "impl.py")
    _write_graph_db(
        graph_db, path="impl.py", content_hash=content_hash,
        symbols=[("helper", "function", 1), ("target_function", "function", 5)],
    )
    return graph_db


# ---------------------------------------------------------------------------
# resolve_changed_range -- §5 revision consistency
# ---------------------------------------------------------------------------


class TestResolveChangedRange:
    def test_resolved_when_hash_matches(self, tmp_path):
        repo = _build_fake_target_repo(tmp_path)
        graph_db = _sync_graph_for(repo)
        res = aci.resolve_changed_range(oracle, repo, graph_db, aci.ChangedRange("impl.py", 5, 6))
        assert res.status == "resolved"
        assert res.symbol.name == "target_function"

    def test_stale_index_on_hash_mismatch(self, tmp_path):
        repo = _build_fake_target_repo(tmp_path)
        graph_db = _sync_graph_for(repo)
        # Live file changes after the graph was synced -- hash now drifts.
        (repo / "impl.py").write_text(_IMPL_TEXT + "\n# a later, unsynced edit\n", encoding="utf-8")
        res = aci.resolve_changed_range(oracle, repo, graph_db, aci.ChangedRange("impl.py", 5, 6))
        assert res.status == "stale_index"
        assert "content_hash" in res.reason

    def test_cannot_map_missing_file_on_disk(self, tmp_path):
        repo = _build_fake_target_repo(tmp_path)
        graph_db = _sync_graph_for(repo)
        res = aci.resolve_changed_range(oracle, repo, graph_db, aci.ChangedRange("nope.py", 1, 2))
        assert res.status == "cannot_map"
        assert "does not exist" in res.reason

    def test_cannot_map_missing_graph_db(self, tmp_path):
        repo = _build_fake_target_repo(tmp_path)
        res = aci.resolve_changed_range(
            oracle, repo, repo / "no-such.db", aci.ChangedRange("impl.py", 1, 2)
        )
        assert res.status == "cannot_map"
        assert "does not exist or is unreadable" in res.reason

    def test_cannot_map_no_source_files_row(self, tmp_path):
        repo = _build_fake_target_repo(tmp_path)
        graph_db = repo / "context-graph.db"
        _write_graph_db(graph_db, path="other.py", content_hash="x", symbols=[])
        res = aci.resolve_changed_range(oracle, repo, graph_db, aci.ChangedRange("impl.py", 1, 2))
        assert res.status == "cannot_map"
        assert "not indexed" in res.reason

    def test_cannot_map_line_past_file_extent(self, tmp_path):
        repo = _build_fake_target_repo(tmp_path)
        graph_db = _sync_graph_for(repo)
        res = aci.resolve_changed_range(oracle, repo, graph_db, aci.ChangedRange("impl.py", 9999, 9999))
        assert res.status == "cannot_map"
        assert "own extent" in res.reason

    def test_cannot_map_line_before_any_symbol(self, tmp_path):
        repo = _build_fake_target_repo(tmp_path)
        graph_db = repo / "context-graph.db"
        content_hash = oracle.sha256_file(repo / "impl.py")
        # Only one symbol, recorded at a line AFTER the requested range.
        _write_graph_db(graph_db, path="impl.py", content_hash=content_hash, symbols=[("target_function", "function", 5)])
        res = aci.resolve_changed_range(oracle, repo, graph_db, aci.ChangedRange("impl.py", 1, 1))
        assert res.status == "cannot_map"
        assert "no indexed top-level symbol" in res.reason


# ---------------------------------------------------------------------------
# classify_symbol -- §3 three-tier relevance/coverage model
# ---------------------------------------------------------------------------


def _write_flat(path: Path, fields: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for key, value in fields.items():
        if isinstance(value, list):
            lines.append(f"{key}: [{', '.join(value)}]")
        else:
            lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_demo_contract(path: Path, *, check_id="chk-a", scope="scope A") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump({
            "schema_version": 1,
            "contract_id": "REQ-X-001",
            "tested_paths": ["impl.py"],
            "checks": [{
                "check_id": check_id, "scope": scope, "execution_provider": "pytest",
                "check_reference": "tests/test_impl.py::test_ok",
                "test_input_paths": ["tests/test_impl.py"], "required": True,
            }],
        }, sort_keys=False),
        encoding="utf-8",
    )


class TestClassifySymbol:
    def test_no_recorded_relationship_when_no_evidence_cites_symbol(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        _write_demo_contract(tmp_path / "planning" / "contracts" / "demo" / "oracle-contract.yaml")
        ki = _load_ki()
        records = ki.load_slug_records(slug_dir)  # empty -- no records at all
        contract = oracle.parse_oracle_contract(
            tmp_path / "planning" / "contracts" / "demo" / "oracle-contract.yaml"
        )
        classification, findings = aci.classify_symbol(records, contract, "target_function", tmp_path)
        assert classification == "no_recorded_relationship"
        assert findings == []

    def test_relevant_no_coverage_link_when_claim_lacks_test_evidence(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        _write_flat(slug_dir / "EV-X-001.yaml", {
            "id": "EV-X-001", "kind": "evidence", "evidence_kind": "source",
            "source_ref": '"impl.py:5 def target_function"',
        })
        _write_flat(slug_dir / "CL-X-001.yaml", {
            "id": "CL-X-001", "kind": "claim", "supporting_evidence": ["EV-X-001"],
        })
        _write_flat(slug_dir / "REQ-X-001.yaml", {
            "id": "REQ-X-001", "kind": "requirement", "depends_on": ["CL-X-001"],
        })
        contract_path = tmp_path / "planning" / "contracts" / "demo" / "oracle-contract.yaml"
        _write_demo_contract(contract_path)
        contract = oracle.parse_oracle_contract(contract_path)
        ki = _load_ki()
        records = ki.load_slug_records(slug_dir)

        classification, findings = aci.classify_symbol(records, contract, "target_function", tmp_path)
        assert classification == "relevant_no_coverage_link"
        assert len(findings) == 1
        assert findings[0].claim_id == "CL-X-001"
        assert findings[0].requirement_ids == ["REQ-X-001"]
        assert findings[0].tier == "relevant_no_coverage_link"
        assert findings[0].check_id is None

    def test_behavioural_risk_when_claim_bridges_to_a_real_check(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        contracts_dir = tmp_path / "planning" / "contracts" / "demo"
        contract_path = contracts_dir / "oracle-contract.yaml"
        _write_demo_contract(contract_path, check_id="chk-a", scope="scope A")

        _write_flat(slug_dir / "EV-X-001.yaml", {
            "id": "EV-X-001", "kind": "evidence", "evidence_kind": "source",
            "source_ref": '"impl.py:5 def target_function"',
        })
        result_path = contracts_dir / "results" / "chk-a--r1.yaml"
        _write_fake_result(result_path, contract_path, check_id="chk-a")
        _write_flat(slug_dir / "EV-X-002.yaml", {
            "id": "EV-X-002", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_path.relative_to(tmp_path)}"',
        })
        _write_flat(slug_dir / "CL-X-001.yaml", {
            "id": "CL-X-001", "kind": "claim", "supporting_evidence": ["EV-X-001", "EV-X-002"],
        })
        _write_flat(slug_dir / "REQ-X-001.yaml", {
            "id": "REQ-X-001", "kind": "requirement", "depends_on": ["CL-X-001"],
        })

        contract = oracle.parse_oracle_contract(contract_path)
        ki = _load_ki()
        records = ki.load_slug_records(slug_dir)
        classification, findings = aci.classify_symbol(records, contract, "target_function", tmp_path)
        assert classification == "behavioural_risk"
        assert len(findings) == 1
        assert findings[0].tier == "behavioural_risk"
        assert findings[0].check_id == "chk-a"


def _load_ki():
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from codecompass import knowledge_intermediate as ki

    return ki


def _write_fake_result(path: Path, contract_path: Path, *, check_id: str, outcome: str = "PASS") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw_path = path.parent / f"{check_id}-raw.txt"
    raw_path.write_text("ok", encoding="utf-8")
    result = oracle.OracleResult(
        schema_version=1, run_id="r1", contract_id="REQ-X-001", check_id=check_id,
        scope="scope A", baseline_id=None, tested_subject_digest="d" * 64,
        oracle_contract_id="REQ-X-001", oracle_contract_content_hash=oracle.sha256_file(contract_path),
        test_input_digest="i" * 64, raw_output_ref=str(raw_path),
        raw_output_sha256=oracle.sha256_file(raw_path), outcome=outcome,
        executed_at="2026-10-28T00:00:00Z", execution_provider="pytest",
        environment_descriptor=None, invalid_reason=None,
    )
    oracle.write_oracle_result(path, result)


# ---------------------------------------------------------------------------
# §4 -- independent assurance precedence (decisions/0087 §1):
# fresh FAIL > fresh INVALID > fresh PASS > no fresh result
# ---------------------------------------------------------------------------


def _build_assurance_repo(tmp_path: Path, *, test_body: str) -> Path:
    repo = tmp_path / "assurance-repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "impl.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    (repo / "tests" / "test_impl.py").write_text(test_body, encoding="utf-8")
    return repo


def _contract_and_check(repo: Path, *, check_reference: str, test_input_paths=None):
    contract_path = repo / "oracle-contract.yaml"
    contract_path.write_text(
        yaml.safe_dump({
            "schema_version": 1, "contract_id": "REQ-X-001", "tested_paths": ["impl.py"],
            "checks": [{
                "check_id": "chk-a", "scope": "scope A", "execution_provider": "pytest",
                "check_reference": check_reference,
                "test_input_paths": test_input_paths or ["tests/test_impl.py"], "required": True,
            }],
        }, sort_keys=False),
        encoding="utf-8",
    )
    contract = oracle.parse_oracle_contract(contract_path)
    return contract_path, contract


class TestRunCheckAssurance:
    def test_fresh_fail_is_confirmed_regression(self, tmp_path):
        repo = _build_assurance_repo(tmp_path, test_body="def test_ok():\n    assert False\n")
        contract_path, contract = _contract_and_check(repo, check_reference="tests/test_impl.py::test_ok")
        finding = aci.run_check_assurance(
            oracle, contract_path, contract, "chk-a", repo, tmp_path / "raw", historical_results=[]
        )
        assert finding.classification == "CONFIRMED_REGRESSION"
        assert finding.fresh_effective_outcome == "FAIL"
        # Both facts shown side by side, never collapsed (decisions/0086 §2/0087 §1).
        assert finding.aggregate_state == "GAP"

    def test_fresh_pass_is_verified_scope(self, tmp_path):
        repo = _build_assurance_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        contract_path, contract = _contract_and_check(repo, check_reference="tests/test_impl.py::test_ok")
        finding = aci.run_check_assurance(
            oracle, contract_path, contract, "chk-a", repo, tmp_path / "raw", historical_results=[]
        )
        assert finding.classification == "VERIFIED_SCOPE"
        assert finding.fresh_effective_outcome == "PASS"
        assert finding.aggregate_state == "PASS"

    def test_fresh_invalid_unresolvable_node_id_is_invalid_assessment(self, tmp_path):
        """decisions/0087 §1's own corrected-precedence reachability test:
        INVALID must never be routed through the aggregate-GAP fallback."""
        repo = _build_assurance_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        contract_path, contract = _contract_and_check(
            repo, check_reference="tests/test_impl.py::test_does_not_exist"
        )
        finding = aci.run_check_assurance(
            oracle, contract_path, contract, "chk-a", repo, tmp_path / "raw", historical_results=[]
        )
        assert finding.classification == "INVALID_ASSESSMENT"
        assert finding.fresh_effective_outcome == "INVALID"
        assert "zero collected tests" in (finding.fresh_invalid_reason or "")
        assert finding.aggregate_state == "GAP"

    def test_fresh_invalid_all_skipped_is_invalid_assessment(self, tmp_path):
        repo = _build_assurance_repo(
            tmp_path,
            test_body=(
                "import pytest\n\n"
                "@pytest.mark.skip(reason='demo')\n"
                "def test_ok():\n    assert True\n"
            ),
        )
        contract_path, contract = _contract_and_check(repo, check_reference="tests/test_impl.py::test_ok")
        finding = aci.run_check_assurance(
            oracle, contract_path, contract, "chk-a", repo, tmp_path / "raw", historical_results=[]
        )
        assert finding.classification == "INVALID_ASSESSMENT"
        assert finding.fresh_effective_outcome == "INVALID"
        assert "skipped" in (finding.fresh_invalid_reason or "")

    def test_fresh_tampered_raw_output_is_invalid_assessment(self, tmp_path):
        """decisions/0087 §2's own named, required case: a fresh
        corrupted/tampered raw output (raw_output_sha256 mismatch) must
        classify INVALID_ASSESSMENT -- exercised through run_check_
        assurance's own real call path (oracle.evaluate_check +
        evaluate_result_precedence), not merely re-testing oracle.py's
        pre-existing tamper detection in isolation (tests/test_oracle.py's
        own test_tampered_raw_output_produces_invalid already covers
        that). A thin wrapper around the real oracle module tampers the
        *fresh* result's own raw_output_ref immediately after execution,
        before run_check_assurance's own precedence recomputation runs."""

        class _TamperingOracle:
            """Delegates everything to the real `oracle` module except
            `evaluate_check`, whose own freshly-written raw output it
            corrupts before returning -- simulating a fresh execution
            whose evidence is tampered immediately after being produced."""

            def __getattr__(self, name):
                return getattr(oracle, name)

            def evaluate_check(self, *args, **kwargs):
                result = oracle.evaluate_check(*args, **kwargs)
                Path(result.raw_output_ref).write_text("TAMPERED", encoding="utf-8")
                return result

        repo = _build_assurance_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        contract_path, contract = _contract_and_check(repo, check_reference="tests/test_impl.py::test_ok")
        finding = aci.run_check_assurance(
            _TamperingOracle(), contract_path, contract, "chk-a", repo, tmp_path / "raw",
            historical_results=[],
        )
        assert finding.classification == "INVALID_ASSESSMENT"
        assert finding.fresh_effective_outcome == "INVALID"
        assert "raw_output_ref" in (finding.fresh_invalid_reason or "")
        assert "tampered or corrupted" in (finding.fresh_invalid_reason or "")
        assert finding.aggregate_state == "GAP"

    def test_fresh_invalid_test_input_digest_mismatch(self, tmp_path):
        """A named test_input_paths entry does not exist -- digest
        computation itself fails closed, INVALID, never silently PASS."""
        repo = _build_assurance_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        contract_path, contract = _contract_and_check(
            repo, check_reference="tests/test_impl.py::test_ok",
            test_input_paths=["tests/does_not_exist.py"],
        )
        finding = aci.run_check_assurance(
            oracle, contract_path, contract, "chk-a", repo, tmp_path / "raw", historical_results=[]
        )
        assert finding.classification == "INVALID_ASSESSMENT"
        assert finding.fresh_effective_outcome == "INVALID"

    def test_historical_pass_never_masks_a_fresh_fail(self, tmp_path):
        """decisions/0087's own explicit guarantee: a historical PASS on
        file for the same check must never promote a fresh FAIL/INVALID
        past CONFIRMED_REGRESSION/INVALID_ASSESSMENT."""
        repo = _build_assurance_repo(tmp_path, test_body="def test_ok():\n    assert False\n")
        contract_path, contract = _contract_and_check(repo, check_reference="tests/test_impl.py::test_ok")
        historical_pass = oracle.OracleResult(
            schema_version=1, run_id="old", contract_id="REQ-X-001", check_id="chk-a",
            scope="scope A", baseline_id=None, tested_subject_digest=oracle.compute_tree_digest(repo, ["impl.py"]),
            oracle_contract_id="REQ-X-001", oracle_contract_content_hash=oracle.sha256_file(contract_path),
            test_input_digest=oracle.compute_tree_digest(repo, ["tests/test_impl.py"]),
            raw_output_ref=str(tmp_path / "old-raw.txt"), raw_output_sha256=None,
            outcome="PASS", executed_at="2026-10-01T00:00:00Z", execution_provider="pytest",
            environment_descriptor=None, invalid_reason=None,
        )
        (tmp_path / "old-raw.txt").write_text("historically passing output", encoding="utf-8")
        historical_pass.raw_output_sha256 = oracle.sha256_file(tmp_path / "old-raw.txt")

        finding = aci.run_check_assurance(
            oracle, contract_path, contract, "chk-a", repo, tmp_path / "raw",
            historical_results=[historical_pass],
        )
        assert finding.classification == "CONFIRMED_REGRESSION"
        assert finding.fresh_effective_outcome == "FAIL"
        # The historical PASS is visible in the aggregate's observed
        # outcomes, but never changes the classification itself.
        assert "PASS" in finding.observed_outcomes
        assert "FAIL" in finding.observed_outcomes


# ---------------------------------------------------------------------------
# End-to-end assess() -- VERIFICATION_GAP when --run-checks is omitted
# ---------------------------------------------------------------------------


class TestAssessEndToEnd:
    def test_verification_gap_when_run_checks_omitted(self, tmp_path):
        repo = _build_fake_target_repo(tmp_path / "target")
        graph_db = _sync_graph_for(repo)

        slug_dir = tmp_path / "knowledge-root" / "planning" / "knowledge" / "demo"
        contracts_dir = tmp_path / "knowledge-root" / "planning" / "contracts" / "demo"
        contract_path = contracts_dir / "oracle-contract.yaml"
        _write_demo_contract(contract_path, check_id="chk-a")
        result_path = contracts_dir / "results" / "chk-a--r1.yaml"
        _write_fake_result(result_path, contract_path, check_id="chk-a")
        _write_flat(slug_dir / "EV-X-001.yaml", {
            "id": "EV-X-001", "kind": "evidence", "evidence_kind": "source",
            "source_ref": '"impl.py:5 def target_function"',
        })
        _write_flat(slug_dir / "EV-X-002.yaml", {
            "id": "EV-X-002", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_path.relative_to(tmp_path / "knowledge-root")}"',
        })
        _write_flat(slug_dir / "CL-X-001.yaml", {
            "id": "CL-X-001", "kind": "claim", "supporting_evidence": ["EV-X-001", "EV-X-002"],
        })

        report = aci.assess(
            target_repo_root=repo, target_graph_db=graph_db,
            knowledge_root=tmp_path / "knowledge-root", slug="demo",
            changed=[aci.ChangedRange("impl.py", 5, 6)], run_checks=False,
        )
        finding = report["findings"][0]
        assert finding["classification"] == "behavioural_risk"
        assert len(finding["assurance"]) == 1
        assert finding["assurance"][0]["classification"] == "VERIFICATION_GAP"
        assert finding["assurance"][0]["fresh_effective_outcome"] is None

    def test_cannot_map_reported_when_no_changed_given_is_a_cli_error(self):
        # main()'s own guard -- exercised at the CLI boundary, not here;
        # this test documents the contract assess() itself has no implicit
        # "assess everything" fallback (every finding is driven by an
        # explicit --changed entry, never inferred).
        report = aci.assess(
            target_repo_root=Path("/nonexistent"), target_graph_db=Path("/nonexistent/db"),
            knowledge_root=Path("/nonexistent"), slug="demo", changed=[], run_checks=False,
        )
        assert report["findings"] == []
