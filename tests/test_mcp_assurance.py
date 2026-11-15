"""Tests for the Stage 88B MCP assurance tools (`impact_classify_change`,
`oracle_list_checks`, `oracle_execute_check`). See `planning/
phase-88-agent-integration-mcp.md` §6/§11.2 for the full spec and this
stage's own acceptance criteria -- this file implements the named
adversarial categories: a changed-path-confinement test (absolute,
traversal, symlink-escape, all rejected before any delegation; a
legitimate path unaffected); a permission-bypass test (execution
disabled); an unauthorised-execution test (a check/contract id not
present in the real contract file); a repo-root-key-injection test; a
modified/untrusted-code test (confirms real execution with real
effects, not a cached/stale result); and real-corpus parity against
the real `~/projects/ledgerkit` checkout for the two already-passing
`balance-from-spec` checks.

Synthetic fixtures mirror `tests/test_assess_change_impact.py`'s own
`tmp_path`-as-fake-repo convention -- two separate roots, never
conflated: `project_root` (this server's own `planning/knowledge/`/
`planning/contracts/`) and `target_root` (the pinned repository under
assessment/execution).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from mcp.server.mcpserver.exceptions import ToolError

from codecompass import graph, oracle
from codecompass.mcp import security as sec
from codecompass.mcp import tools as mcp_tools

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGERKIT_ROOT = Path.home() / "projects" / "ledgerkit"
requires_ledgerkit = pytest.mark.skipif(
    not (LEDGERKIT_ROOT.is_dir() and (LEDGERKIT_ROOT / "context-graph.db").is_file()),
    reason="~/projects/ledgerkit (with its own context-graph.db) is not present here",
)


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _write_flat(path: Path, fields: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}: {value}" for key, value in fields.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_target_repo(
    tmp_path: Path, *, test_body: str, impl_body: str = "def widget():\n    return 1\n"
) -> Path:
    target = tmp_path / "target-repo"
    (target / "tests").mkdir(parents=True)
    (target / "impl.py").write_text(impl_body, encoding="utf-8")
    (target / "tests" / "test_impl.py").write_text(test_body, encoding="utf-8")
    return target


def _sync_graph(
    target_root: Path, *, rel_path: str = "impl.py", name: str = "widget", line: int = 1
) -> None:
    conn = graph.open_graph(target_root)
    try:
        content_hash = oracle.sha256_file(target_root / rel_path)
        conn.execute(
            "INSERT INTO source_files (path, language, content_hash, symbol_index_status) "
            "VALUES (?, 'python', ?, 'indexed')",
            (rel_path, content_hash),
        )
        file_id = conn.execute(
            "SELECT id FROM source_files WHERE path = ?", (rel_path,)
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO source_symbols (source_file_id, name, kind, line, purpose, exposure) "
            "VALUES (?, ?, 'function', ?, 'does a thing', 'public')",
            (file_id, name, line),
        )
        conn.commit()
    finally:
        conn.close()


def _build_knowledge_and_contract(
    project_root: Path, slug: str, *, check_id: str = "chk-a", required: bool = True
) -> None:
    slug_dir = project_root / "planning" / "knowledge" / slug
    _write_flat(
        slug_dir / "REQ-X-001.yaml",
        {"id": "REQ-X-001", "kind": "requirement", "statement": "req"},
    )
    _write_flat(
        slug_dir / "EV-X-001.yaml",
        {
            "id": "EV-X-001", "kind": "evidence", "evidence_kind": "source",
            "source_ref": "impl.py:1 def widget", "what_it_shows": "x",
        },
    )
    _write_flat(
        slug_dir / "CL-X-001.yaml",
        {"id": "CL-X-001", "kind": "claim", "supporting_evidence": "[EV-X-001]", "statement": "x"},
    )
    contract_path = project_root / "planning" / "contracts" / slug / "oracle-contract.yaml"
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "contract_id": "REQ-X-001",
                "tested_paths": ["impl.py"],
                "checks": [
                    {
                        "check_id": check_id,
                        "scope": "scope A",
                        "execution_provider": "pytest",
                        "check_reference": "tests/test_impl.py::test_ok",
                        "test_input_paths": ["tests/test_impl.py"],
                        "required": required,
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _config(project_root: Path, repo_roots: dict | None = None, *, execution_enabled: bool = False):
    return sec.ServerConfig.build(
        project_root, repo_roots or {}, execution_enabled=execution_enabled
    )


# ---------------------------------------------------------------------------
# impact_classify_change
# ---------------------------------------------------------------------------


class TestImpactClassifyChange:
    def test_valid_change_reports_behavioural_risk(self, tmp_path: Path) -> None:
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        _sync_graph(target)
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")

        config = _config(project_root, {"target": target})
        resp = mcp_tools.impact_classify_change(
            config, "target", "demo", [{"path": "impl.py", "start": 1, "end": 1}]
        )
        finding = resp["findings"][0]
        assert finding["status"] == "resolved"
        # This fixture's only citing Evidence is `source`-kind, with no
        # `test`-kind Evidence bridging to a passing oracle result --
        # correctly `relevant_no_coverage_link`, not `behavioural_risk`
        # (the latter requires a real bridging check, exercised against
        # the real Ledgerkit corpus in TestRealLedgerkitCorpus below).
        assert finding["symbol_classifications"][0]["classification"] == "relevant_no_coverage_link"
        assert "target_revision" in resp
        assert "target_repo_root" not in resp
        assert "target_graph_db" not in resp
        assert "knowledge_root" not in resp

    def test_unknown_repo_root_key_rejected(self, tmp_path: Path) -> None:
        config = _config(tmp_path)
        with pytest.raises(ToolError):
            mcp_tools.impact_classify_change(
                config, "not-configured", "demo", [{"path": "impl.py", "start": 1, "end": 1}]
            )

    def test_unknown_slug_rejected(self, tmp_path: Path) -> None:
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        config = _config(tmp_path, {"target": target})
        with pytest.raises(ToolError):
            mcp_tools.impact_classify_change(
                config, "target", "no-such-slug", [{"path": "impl.py", "start": 1, "end": 1}]
            )

    def test_empty_changed_list_rejected(self, tmp_path: Path) -> None:
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, {"target": target})
        with pytest.raises(ToolError):
            mcp_tools.impact_classify_change(config, "target", "demo", [])

    def test_changed_entry_missing_path_key_is_a_tool_error_not_a_bare_keyerror(
        self, tmp_path: Path
    ) -> None:
        """Independent audit finding (Stage 88B): a malformed changed[]
        entry missing its own 'path' key must never surface as an
        uncaught KeyError -- always a structured ToolError, matching
        every other malformed-input case this tool rejects."""
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, {"target": target})
        with pytest.raises(ToolError, match="malformed changed"):
            mcp_tools.impact_classify_change(config, "target", "demo", [{"start": 1, "end": 1}])

    def test_changed_entry_not_a_mapping_is_a_tool_error(self, tmp_path: Path) -> None:
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, {"target": target})
        with pytest.raises(ToolError, match="malformed changed"):
            mcp_tools.impact_classify_change(config, "target", "demo", ["impl.py:1-1"])

    def test_absolute_path_rejected_before_delegation(self, tmp_path: Path) -> None:
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, {"target": target})
        with pytest.raises(ToolError, match="absolute"):
            mcp_tools.impact_classify_change(
                config, "target", "demo", [{"path": "/etc/passwd", "start": 1, "end": 1}]
            )

    def test_traversal_path_rejected_before_delegation(self, tmp_path: Path) -> None:
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, {"target": target})
        with pytest.raises(ToolError, match="traversal"):
            mcp_tools.impact_classify_change(
                config, "target", "demo", [{"path": "../../../etc/passwd", "start": 1, "end": 1}]
            )

    def test_symlink_escape_rejected_before_delegation(self, tmp_path: Path) -> None:
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        outside = tmp_path / "outside.py"
        outside.write_text("SECRET = 1\n", encoding="utf-8")
        (target / "evil.py").symlink_to(outside)
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, {"target": target})
        with pytest.raises(ToolError, match="symlink"):
            mcp_tools.impact_classify_change(
                config, "target", "demo", [{"path": "evil.py", "start": 1, "end": 1}]
            )

    def test_legitimate_path_unaffected_by_confinement_check(self, tmp_path: Path) -> None:
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        _sync_graph(target)
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, {"target": target})
        resp = mcp_tools.impact_classify_change(
            config, "target", "demo", [{"path": "impl.py", "start": 1, "end": 1}]
        )
        assert resp["findings"][0]["status"] == "resolved"


# ---------------------------------------------------------------------------
# oracle_list_checks
# ---------------------------------------------------------------------------


class TestOracleListChecks:
    def test_lists_real_checks_with_aggregate_status(self, tmp_path: Path) -> None:
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo", check_id="chk-a")
        config = _config(project_root)
        resp = mcp_tools.oracle_list_checks(config, "demo")
        assert len(resp["checks"]) == 1
        check = resp["checks"][0]
        assert check["check_id"] == "chk-a"
        assert check["contract_id"] == "REQ-X-001"
        assert check["required"] is True
        assert check["latest_result_status"] == "GAP"  # required, no results yet

    def test_unknown_slug_rejected(self, tmp_path: Path) -> None:
        config = _config(tmp_path)
        with pytest.raises(ToolError):
            mcp_tools.oracle_list_checks(config, "no-such-slug")

    def test_missing_contract_returns_empty_checks(self, tmp_path: Path) -> None:
        project_root = tmp_path / "project-root"
        (project_root / "planning" / "knowledge" / "demo").mkdir(parents=True)
        config = _config(project_root)
        resp = mcp_tools.oracle_list_checks(config, "demo")
        assert resp["checks"] == []


# ---------------------------------------------------------------------------
# oracle_execute_check
# ---------------------------------------------------------------------------


class TestOracleExecuteCheck:
    def test_disabled_server_rejects_before_any_subprocess(self, tmp_path: Path) -> None:
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, {"target": target}, execution_enabled=False)
        sentinel = tmp_path / "ran.marker"
        target_test = target / "tests" / "test_impl.py"
        target_test.write_text(
            f"def test_ok():\n    open({str(sentinel)!r}, 'w').close()\n    assert True\n",
            encoding="utf-8",
        )
        with pytest.raises(ToolError, match="disabled"):
            mcp_tools.oracle_execute_check(config, "demo", "REQ-X-001", "chk-a", "target")
        assert not sentinel.exists(), "no subprocess should ever have been launched"

    def test_unknown_check_id_rejected(self, tmp_path: Path) -> None:
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, {"target": target}, execution_enabled=True)
        with pytest.raises(ToolError, match="unknown check_id"):
            mcp_tools.oracle_execute_check(
                config, "demo", "REQ-X-001", "not-a-real-check", "target"
            )

    def test_wrong_contract_id_rejected(self, tmp_path: Path) -> None:
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, {"target": target}, execution_enabled=True)
        with pytest.raises(ToolError, match="does not match"):
            mcp_tools.oracle_execute_check(config, "demo", "WRONG-ID", "chk-a", "target")

    def test_unknown_slug_rejected(self, tmp_path: Path) -> None:
        config = _config(tmp_path, execution_enabled=True)
        with pytest.raises(ToolError):
            mcp_tools.oracle_execute_check(config, "no-such-slug", "REQ-X-001", "chk-a", "target")

    def test_unconfigured_repo_root_key_rejected(self, tmp_path: Path) -> None:
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, execution_enabled=True)
        with pytest.raises(ToolError):
            mcp_tools.oracle_execute_check(config, "demo", "REQ-X-001", "chk-a", "not-configured")

    def test_path_shaped_repo_root_key_rejected_exactly_like_any_other_unknown_key(
        self, tmp_path: Path
    ) -> None:
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, execution_enabled=True)
        with pytest.raises(ToolError):
            mcp_tools.oracle_execute_check(config, "demo", "REQ-X-001", "chk-a", "/etc/passwd")

    def test_real_execution_writes_append_only_result(self, tmp_path: Path) -> None:
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, {"target": target}, execution_enabled=True)

        results_dir = project_root / "planning" / "contracts" / "demo" / "results"
        assert not results_dir.exists()

        resp1 = mcp_tools.oracle_execute_check(config, "demo", "REQ-X-001", "chk-a", "target")
        assert resp1["outcome"] == "PASS"
        assert resp1["aggregate_state"] == "PASS"
        first_run_files = sorted(results_dir.glob("*.yaml"))
        assert len(first_run_files) == 1

        # raw_output_ref must be relative (portability convention,
        # preserved via the scoped chdir) -- never an absolute,
        # machine-specific path baked into a committed result file.
        raw_ref = Path(resp1["raw_output_ref"])
        assert not raw_ref.is_absolute()
        assert (project_root / raw_ref).is_file()

        resp2 = mcp_tools.oracle_execute_check(config, "demo", "REQ-X-001", "chk-a", "target")
        assert resp2["run_id"] != resp1["run_id"]
        second_run_files = sorted(results_dir.glob("*.yaml"))
        assert len(second_run_files) == 2
        # The first run's own result file is never overwritten or
        # deleted by the second -- append-only, by construction.
        assert first_run_files[0].exists()

    def test_real_execution_matches_direct_oracle_evaluate_check(self, tmp_path: Path) -> None:
        """Behavioural parity (§11.2's own acceptance criterion): the
        MCP tool's fresh outcome must match what calling `oracle.
        evaluate_check` directly would produce for the identical
        inputs -- confirming the thin wrapper adds confinement/
        envelope only, never a divergent execution path."""
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert False\n")
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, {"target": target}, execution_enabled=True)

        resp = mcp_tools.oracle_execute_check(config, "demo", "REQ-X-001", "chk-a", "target")
        assert resp["outcome"] == "FAIL"

        contract_path = project_root / "planning" / "contracts" / "demo" / "oracle-contract.yaml"
        contract = oracle.parse_oracle_contract(contract_path)
        check = contract.check_by_id("chk-a")
        direct_outcome, _invalid_reason, _raw = oracle.run_pytest_check(
            target, check.check_reference
        )
        assert direct_outcome == resp["outcome"] == "FAIL"

    def test_modified_target_code_produces_a_real_observable_side_effect(
        self, tmp_path: Path
    ) -> None:
        """The §5.8/§11.2-named "modified/untrusted-code" test: confirms
        this tool genuinely executes the *current* content of the
        target's own test file under the server's own privileges, with
        real effects -- not a cached, stale, or simulated result."""
        target = _build_target_repo(tmp_path, test_body="def test_ok():\n    assert True\n")
        project_root = tmp_path / "project-root"
        _build_knowledge_and_contract(project_root, "demo")
        config = _config(project_root, {"target": target}, execution_enabled=True)

        sentinel = tmp_path / "side_effect.marker"
        assert not sentinel.exists()
        (target / "tests" / "test_impl.py").write_text(
            f"def test_ok():\n    open({str(sentinel)!r}, 'w').write('ran')\n    assert True\n",
            encoding="utf-8",
        )
        resp = mcp_tools.oracle_execute_check(config, "demo", "REQ-X-001", "chk-a", "target")
        assert resp["outcome"] == "PASS"
        assert sentinel.is_file()
        assert sentinel.read_text(encoding="utf-8") == "ran"


# ---------------------------------------------------------------------------
# Real-corpus parity against the real ~/projects/ledgerkit checkout.
# ---------------------------------------------------------------------------


@requires_ledgerkit
class TestRealLedgerkitCorpus:
    def test_impact_classify_change_against_real_balance_from_spec(self) -> None:
        config = _config(REPO_ROOT, {"ledgerkit": LEDGERKIT_ROOT})
        resp = mcp_tools.impact_classify_change(
            config, "ledgerkit", "balance-from-spec",
            [{"path": "ledgerkit/reports.py", "start": 600, "end": 668}],
        )
        finding = resp["findings"][0]
        assert finding["status"] in ("resolved", "partially_resolved")
        assert any(
            sc["classification"] == "behavioural_risk" for sc in finding["symbol_classifications"]
        )

    def test_oracle_list_checks_against_real_balance_from_spec(self) -> None:
        config = _config(REPO_ROOT)
        resp = mcp_tools.oracle_list_checks(config, "balance-from-spec")
        by_id = {c["check_id"]: c for c in resp["checks"]}
        assert by_id["single-section-expense-subtotal"]["latest_result_status"] == "PASS"
        assert by_id["multi-section-income-expense-subtotal"]["latest_result_status"] == "PASS"
        gap_check = by_id["overlapping-account-patterns-no-double-count"]
        assert gap_check["latest_result_status"] == "GAP"

    # Deliberately no automated `oracle_execute_check` test against the
    # real ~/projects/ledgerkit checkout here: unlike the two read-only
    # tests above, executing a real check permanently appends a new
    # result file to this repository's own committed `planning/
    # contracts/balance-from-spec/results/` directory (the established
    # append-only convention -- never deleted). Doing that on every
    # automated test run would accumulate test-generated result files
    # on every invocation, which is test pollution, not verification.
    # This exact call (`oracle_execute_check` against `single-section-
    # expense-subtotal`) was instead run once, deliberately, as this
    # stage's own manual verification step -- its real, permanent
    # result file is committed alongside this stage's code, confirming
    # `outcome: PASS`/`aggregate_state: PASS` and a portable, relative
    # `raw_output_ref`, matching `scripts/run_balance_from_spec_
    # oracle.py`'s own established behaviour exactly.
