"""Tests for `src/codecompass/source_reconciliation.py` (Phase 89 Stage
89A, `decisions/0096`) plus the new `change_impact.py`/`knowledge_
intermediate.py`/`cli.py` surface it depends on. Deliberately
independent of the real ~/projects/ledgerkit checkout -- each test
constructs its own minimal, disposable fake target repository + graph
database + knowledge-record/contract fixtures, mirroring `tests/
test_assess_change_impact.py`'s own established convention.
"""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from codecompass import change_impact as ci  # noqa: E402
from codecompass import cli, oracle  # noqa: E402
from codecompass import knowledge_intermediate as ki  # noqa: E402
from codecompass import source_reconciliation as sr  # noqa: E402

runner = CliRunner()


# ---------------------------------------------------------------------------
# Shared fixture builders
# ---------------------------------------------------------------------------


def _write_graph_db(
    db_path: Path, files: dict[str, str], symbols: dict[str, list[tuple[str, str, int]]]
) -> None:
    if db_path.is_file():
        db_path.unlink()  # re-sync: replace, never append to a stale graph
    con = sqlite3.connect(db_path)
    con.execute(
        "CREATE TABLE source_files (id INTEGER PRIMARY KEY, path TEXT UNIQUE, content_hash TEXT)"
    )
    con.execute(
        "CREATE TABLE source_symbols (id INTEGER PRIMARY KEY, source_file_id INTEGER, "
        "name TEXT, kind TEXT, line INTEGER)"
    )
    for path, content_hash in files.items():
        cur = con.execute(
            "INSERT INTO source_files (path, content_hash) VALUES (?, ?)", (path, content_hash)
        )
        file_id = cur.lastrowid
        for name, kind, line in symbols.get(path, []):
            con.execute(
                "INSERT INTO source_symbols (source_file_id, name, kind, line) VALUES (?, ?, ?, ?)",
                (file_id, name, kind, line),
            )
    con.commit()
    con.close()


_IMPL_TEXT = "def helper():\n    return 1\n\n\ndef target_function():\n    return 2\n"
_TEST_TEXT_PASS = "def test_ok():\n    assert True\n"
_TEST_TEXT_FAIL = "def test_ok():\n    assert False\n"
_TEST_TEXT_TWO = "def test_ok():\n    assert True\n\n\ndef test_ok_2():\n    assert True\n"


def _build_repo(tmp_path: Path, name: str = "target-repo", *, impl_text: str = _IMPL_TEXT,
                 test_text: str = _TEST_TEXT_PASS) -> Path:
    repo = tmp_path / name
    (repo / "tests").mkdir(parents=True)
    (repo / "impl.py").write_text(impl_text, encoding="utf-8")
    (repo / "tests" / "test_impl.py").write_text(test_text, encoding="utf-8")
    return repo


def _sync_graph(repo: Path, *, extra_files: dict[str, str] | None = None) -> Path:
    graph_db = repo / "context-graph.db"
    files = {"impl.py": oracle.sha256_file(repo / "impl.py")}
    if (repo / "tests" / "test_impl.py").is_file():
        files["tests/test_impl.py"] = oracle.sha256_file(repo / "tests" / "test_impl.py")
    if extra_files:
        for p in extra_files:
            files[p] = oracle.sha256_file(repo / p)
    _write_graph_db(
        graph_db, files,
        {"impl.py": [("helper", "function", 1), ("target_function", "function", 5)]},
    )
    return graph_db


def _write_flat(path: Path, fields: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for key, value in fields.items():
        if isinstance(value, list):
            lines.append(f"{key}: [{', '.join(value)}]")
        else:
            lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_contract(path: Path, *, checks: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1, "contract_id": "REQ-X-001",
                "tested_paths": ["impl.py"], "checks": checks,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _default_check(check_id="chk-a", scope="scope A", check_reference="tests/test_impl.py::test_ok",
                    test_input_paths=None, required=True):
    return {
        "check_id": check_id, "scope": scope, "execution_provider": "pytest",
        "check_reference": check_reference,
        "test_input_paths": test_input_paths or ["tests/test_impl.py"], "required": required,
    }


def _setup_slug(project_root: Path, slug: str, *, checks: list[dict]) -> tuple[Path, Path]:
    contract_path = project_root / "planning" / "contracts" / slug / "oracle-contract.yaml"
    _write_contract(contract_path, checks=checks)
    slug_dir = project_root / "planning" / "knowledge" / slug
    slug_dir.mkdir(parents=True, exist_ok=True)
    return contract_path, slug_dir


def _bridge_evidence(slug_dir: Path, contract_path: Path, *, check_id: str, result_path: Path,
                      ev_id="EV-X-002", outcome="PASS") -> None:
    _write_fake_result(result_path, contract_path, check_id=check_id, outcome=outcome)
    rel_result = result_path.relative_to(slug_dir.parents[2])
    _write_flat(slug_dir / f"{ev_id}.yaml", {
        "id": ev_id, "kind": "evidence", "evidence_kind": "test",
        "test_ref": f'"{rel_result}"',
    })


def _write_fake_result(path: Path, contract_path: Path, *, check_id: str, outcome: str = "PASS",
                        run_id: str = "r1", scope: str = "scope A",
                        repo_root: Path | None = None,
                        tested_paths: list[str] | None = None,
                        test_input_paths: list[str] | None = None) -> None:
    """When `repo_root` is given, `tested_subject_digest`/`test_input_digest`
    are REAL recomputed digests against that checkout (defaulting to
    `tested_paths=["impl.py"]`/`test_input_paths=["tests/test_impl.py"]`,
    matching `_build_repo`/`_write_contract`'s own defaults) -- required
    so `oracle.evaluate_result_precedence(..., repo_root=repo_root)`
    (the apply-time re-validation Phase 89A's corrective pass adds,
    defect B) genuinely resolves PASS/FAIL rather than always INVALID.
    Without `repo_root`, the digests stay fixed placeholder strings, for
    the many tests that never exercise that apply-time re-validation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    raw_path = path.parent / f"{check_id}-{run_id}-raw.txt"
    raw_path.write_text("ok", encoding="utf-8")
    if repo_root is not None:
        tested_subject_digest = oracle.compute_tree_digest(repo_root, tested_paths or ["impl.py"])
        test_input_digest = oracle.compute_tree_digest(
            repo_root, test_input_paths or ["tests/test_impl.py"]
        )
    else:
        tested_subject_digest = "d" * 64
        test_input_digest = "i" * 64
    result = oracle.OracleResult(
        schema_version=1, run_id=run_id, contract_id="REQ-X-001", check_id=check_id,
        scope=scope, baseline_id=None, tested_subject_digest=tested_subject_digest,
        oracle_contract_id="REQ-X-001",
        oracle_contract_content_hash=oracle.sha256_file(contract_path),
        test_input_digest=test_input_digest, raw_output_ref=str(raw_path),
        raw_output_sha256=oracle.sha256_file(raw_path), outcome=outcome,
        executed_at="2026-10-28T00:00:00Z", execution_provider="pytest",
        environment_descriptor=None, invalid_reason=None,
    )
    oracle.write_oracle_result(path, result)


# ---------------------------------------------------------------------------
# on_fresh_result / assess backward compatibility + multi-range capture
# (decisions/0096, dispatch §3.C)
# ---------------------------------------------------------------------------


class TestOnFreshResultCallback:
    def test_run_check_assurance_without_callback_is_unaffected(self, tmp_path):
        repo = _build_repo(tmp_path)
        contract_path, contract = contract_obj = _contract(tmp_path, repo)
        finding = ci.run_check_assurance(
            oracle, contract_path, contract_obj[1], "chk-a", repo, tmp_path / "raw",
            historical_results=[],
        )
        assert finding.classification == "VERIFIED_SCOPE"

    def test_run_check_assurance_invokes_callback_with_real_result(self, tmp_path):
        repo = _build_repo(tmp_path)
        contract_path, contract = _contract(tmp_path, repo)
        captured = []
        finding = ci.run_check_assurance(
            oracle, contract_path, contract, "chk-a", repo, tmp_path / "raw", historical_results=[],
            on_fresh_result=captured.append,
        )
        assert len(captured) == 1
        assert captured[0].check_id == "chk-a"
        assert captured[0].run_id  # a real, minted run_id
        assert finding.classification == "VERIFIED_SCOPE"

    def test_assess_mcp_style_call_without_callback_unaffected(self, tmp_path):
        """The one real existing caller (`mcp/tools.py:342`) passes
        neither parameter and also passes run_checks=False -- confirm
        this exact call shape still behaves identically."""
        project_root = tmp_path
        repo = _build_repo(tmp_path)
        graph_db = _sync_graph(repo)
        _setup_slug_for_assess(project_root, repo, graph_db)
        report = ci.assess(
            target_repo_root=repo, target_graph_db=graph_db, knowledge_root=project_root,
            slug="demo", changed=[ci.ChangedRange("impl.py", 5, 6)], run_checks=False,
        )
        assert report["ran_checks"] is False

    def test_multi_range_capture_is_keyed_by_range_index_and_check_id(self, tmp_path):
        """Two different ChangedRanges in one assess() call contributing
        the SAME check_id -- both captured results must be retained
        independently, never one overwriting the other."""
        project_root = tmp_path
        repo = _build_repo(tmp_path)
        graph_db = _sync_graph(repo, extra_files={})
        # Two first-party files, each with their own symbol, both bridged
        # to the SAME check_id via separate Claims.
        (repo / "impl2.py").write_text("def other_function():\n    return 3\n", encoding="utf-8")
        _write_graph_db(
            graph_db,
            {
                "impl.py": oracle.sha256_file(repo / "impl.py"),
                "impl2.py": oracle.sha256_file(repo / "impl2.py"),
                "tests/test_impl.py": oracle.sha256_file(repo / "tests" / "test_impl.py"),
            },
            {
                "impl.py": [("target_function", "function", 5)],
                "impl2.py": [("other_function", "function", 1)],
            },
        )
        contract_path, slug_dir = _setup_slug(project_root, "demo", checks=[_default_check()])
        result_path = (
            project_root / "planning" / "contracts" / "demo" / "results" / "chk-a--r1.yaml"
        )
        _write_fake_result(result_path, contract_path, check_id="chk-a")
        _write_flat(slug_dir / "EV-SRC-1.yaml", {
            "id": "EV-SRC-1", "kind": "evidence", "evidence_kind": "source",
            "source_ref": '"impl.py:5 def target_function"',
        })
        _write_flat(slug_dir / "EV-SRC-2.yaml", {
            "id": "EV-SRC-2", "kind": "evidence", "evidence_kind": "source",
            "source_ref": '"impl2.py:1 def other_function"',
        })
        _write_flat(slug_dir / "EV-TEST-1.yaml", {
            "id": "EV-TEST-1", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_path.relative_to(project_root)}"',
        })
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {
            "id": "CL-DEMO-001", "kind": "claim",
            "supporting_evidence": ["EV-SRC-1", "EV-TEST-1"], "contradicting_evidence": [],
        })
        _write_flat(slug_dir / "CL-DEMO-002.yaml", {
            "id": "CL-DEMO-002", "kind": "claim",
            "supporting_evidence": ["EV-SRC-2", "EV-TEST-1"], "contradicting_evidence": [],
        })

        captured = {}

        def _capture(range_index, result, _store=captured):
            _store[(range_index, result.check_id)] = result

        report = ci.assess(
            target_repo_root=repo, target_graph_db=graph_db, knowledge_root=project_root,
            slug="demo",
            changed=[ci.ChangedRange("impl.py", 1, 6), ci.ChangedRange("impl2.py", 1, 2)],
            run_checks=True, on_fresh_result=_capture, raw_output_dir=tmp_path / "raw",
        )
        assert len(captured) == 2
        assert (0, "chk-a") in captured
        assert (1, "chk-a") in captured
        # Two genuinely distinct runs -- never the same object reused.
        assert captured[(0, "chk-a")].run_id != captured[(1, "chk-a")].run_id
        assert report["findings"][0]["assurance"][0]["classification"] == "VERIFIED_SCOPE"
        assert report["findings"][1]["assurance"][0]["classification"] == "VERIFIED_SCOPE"


def _contract(tmp_path: Path, repo: Path):
    contract_path = repo / "oracle-contract.yaml"
    _write_contract(contract_path, checks=[_default_check()])
    contract = oracle.parse_oracle_contract(contract_path)
    return contract_path, contract


def _setup_slug_for_assess(project_root: Path, repo: Path, graph_db: Path) -> None:
    contract_path, slug_dir = _setup_slug(project_root, "demo", checks=[_default_check()])
    result_path = (
        project_root / "planning" / "contracts" / "demo" / "results" / "chk-a--r1.yaml"
    )
    _write_fake_result(result_path, contract_path, check_id="chk-a")
    _write_flat(slug_dir / "EV-SRC-1.yaml", {
        "id": "EV-SRC-1", "kind": "evidence", "evidence_kind": "source",
        "source_ref": '"impl.py:5 def target_function"',
    })
    _write_flat(slug_dir / "EV-TEST-1.yaml", {
        "id": "EV-TEST-1", "kind": "evidence", "evidence_kind": "test",
        "test_ref": f'"{result_path.relative_to(project_root)}"',
    })
    _write_flat(slug_dir / "CL-DEMO-001.yaml", {
        "id": "CL-DEMO-001", "kind": "claim",
        "supporting_evidence": ["EV-SRC-1", "EV-TEST-1"], "contradicting_evidence": [],
    })


# ---------------------------------------------------------------------------
# detect_source_changes -- graph freshness, baseline comparison,
# symbol_change vs test_input_change, negative controls
# ---------------------------------------------------------------------------


class TestDetectSourceChanges:
    def _setup(self, tmp_path):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        graph_db = _sync_graph(repo)
        contract_path, slug_dir = _setup_slug(project_root, "demo", checks=[_default_check()])
        result_path = (
            project_root / "planning" / "contracts" / "demo" / "results" / "chk-a--r1.yaml"
        )
        _write_fake_result(result_path, contract_path, check_id="chk-a")
        _write_flat(slug_dir / "EV-SRC-1.yaml", {
            "id": "EV-SRC-1", "kind": "evidence", "evidence_kind": "source",
            "source_ref": '"impl.py:5 def target_function"',
        })
        _write_flat(slug_dir / "EV-TEST-1.yaml", {
            "id": "EV-TEST-1", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_path.relative_to(project_root)}"',
        })
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {
            "id": "CL-DEMO-001", "kind": "claim",
            "supporting_evidence": ["EV-SRC-1", "EV-TEST-1"], "contradicting_evidence": [],
        })
        return project_root, repo, graph_db

    def test_new_file_reported_as_new_never_establishes_baseline(self, tmp_path):
        project_root, repo, graph_db = self._setup(tmp_path)
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert "impl.py" in result.new_files
        assert sr._read_baseline(project_root, "demo") == {}

    def test_establish_baselines_for_new_files_is_explicit_and_opt_in(self, tmp_path):
        project_root, repo, graph_db = self._setup(tmp_path)
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert sr._read_baseline(project_root, "demo") == {}  # detection alone never writes one
        established = sr.establish_baselines_for_new_files(
            project_root, "demo", repo_root=repo, result=result, target_graph_db=graph_db,
        )
        assert "impl.py" in established
        baseline = sr._read_baseline(project_root, "demo")
        assert baseline["impl.py"]["content_hash"] == oracle.sha256_file(repo / "impl.py")
        # A second call never advances an EXISTING baseline past what
        # detection alone found -- only ever re-establishes the same
        # already-recorded new-file set, never a changed file.
        (repo / "impl.py").write_text(_IMPL_TEXT + "\n# edited after baseline\n", encoding="utf-8")
        result2 = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert "impl.py" not in result2.new_files  # already baselined, reported stale/changed

    def test_stale_graph_index_excludes_file_from_comparison(self, tmp_path):
        project_root, repo, graph_db = self._setup(tmp_path)
        sr.establish_source_baseline(
            project_root, "demo", "impl.py", oracle.sha256_file(repo / "impl.py")
        )
        (repo / "impl.py").write_text(_IMPL_TEXT + "\n# unsynced edit\n", encoding="utf-8")
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert any(f.path == "impl.py" for f in result.stale_graph_index)
        assert result.changed == []

    def test_unchanged_file_reports_nothing(self, tmp_path):
        project_root, repo, graph_db = self._setup(tmp_path)
        sr.establish_source_baseline(
            project_root, "demo", "impl.py", oracle.sha256_file(repo / "impl.py")
        )
        sr.establish_source_baseline(
            project_root, "demo", "tests/test_impl.py",
            oracle.sha256_file(repo / "tests" / "test_impl.py"),
        )
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert result.changed == []
        assert result.stale_graph_index == []
        assert result.new_files == []

    def test_symbol_change_detected_after_baseline_and_fresh_sync(self, tmp_path):
        project_root, repo, graph_db = self._setup(tmp_path)
        sr.establish_source_baseline(
            project_root, "demo", "impl.py", oracle.sha256_file(repo / "impl.py")
        )
        (repo / "impl.py").write_text(_IMPL_TEXT + "\n# a real change\n", encoding="utf-8")
        graph_db = _sync_graph(repo)  # re-sync, matching the required order
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert len(result.changed) == 1
        assert result.changed[0].path == "impl.py"
        assert result.changed[0].resolution == "symbol_change"

    def test_test_only_change_detected_via_test_input_paths(self, tmp_path):
        """dispatch §3.A: a change to the test file alone (production
        source untouched) must still be discovered, through
        test_input_paths, resolved directly to the bridged Claim."""
        project_root, repo, graph_db = self._setup(tmp_path)
        sr.establish_source_baseline(
            project_root, "demo", "impl.py", oracle.sha256_file(repo / "impl.py")
        )
        sr.establish_source_baseline(
            project_root, "demo", "tests/test_impl.py",
            oracle.sha256_file(repo / "tests" / "test_impl.py"),
        )
        (repo / "tests" / "test_impl.py").write_text(
            "def test_ok():\n    assert True  # a real test-only edit\n", encoding="utf-8",
        )
        graph_db = _sync_graph(repo)
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        test_changes = [f for f in result.changed if f.resolution == "test_input_change"]
        assert len(test_changes) == 1
        assert test_changes[0].path == "tests/test_impl.py"
        assert test_changes[0].check_id == "chk-a"
        assert test_changes[0].claim_ids == ["CL-DEMO-001"]
        # And it must NEVER be misreported as a symbol_change.
        assert not any(
            f.path == "tests/test_impl.py" and f.resolution == "symbol_change"
            for f in result.changed
        )

    def test_test_only_change_on_stale_graph_is_excluded_like_source(self, tmp_path):
        project_root, repo, graph_db = self._setup(tmp_path)
        sr.establish_source_baseline(
            project_root, "demo", "tests/test_impl.py",
            oracle.sha256_file(repo / "tests" / "test_impl.py"),
        )
        (repo / "tests" / "test_impl.py").write_text(
            "def test_ok():\n    assert True  # edit\n", encoding="utf-8",
        )
        # Deliberately NOT re-synced -- graph_db still has the old hash.
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert any(f.path == "tests/test_impl.py" for f in result.stale_graph_index)
        assert not any(f.path == "tests/test_impl.py" for f in result.changed)

    def test_unrelated_file_change_is_a_false_positive_control(self, tmp_path):
        """A file that is neither a tracked source_ref nor any covered
        check's own test_input_paths is never tracked at all."""
        project_root, repo, graph_db = self._setup(tmp_path)
        (repo / "unrelated.py").write_text("x = 1\n", encoding="utf-8")
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert not any(f.path == "unrelated.py" for f in result.changed)
        assert not any(f.path == "unrelated.py" for f in result.stale_graph_index)
        assert "unrelated.py" not in result.new_files

    def test_deleted_file_reported_distinctly(self, tmp_path):
        project_root, repo, graph_db = self._setup(tmp_path)
        sr.establish_source_baseline(
            project_root, "demo", "impl.py", oracle.sha256_file(repo / "impl.py")
        )
        (repo / "impl.py").unlink()
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert "impl.py" in result.deleted_files
        assert "impl.py" not in result.new_files


# ---------------------------------------------------------------------------
# detect_newly_coverable_checks -- corrected gate, fail-closed guard
# ---------------------------------------------------------------------------


class TestDetectNewlyCoverableChecks:
    def test_check_with_no_citing_evidence_is_newly_coverable_once_it_collects(self, tmp_path):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        contract_path, slug_dir = _setup_slug(project_root, "demo", checks=[_default_check()])
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {
            "id": "CL-DEMO-001", "kind": "claim",
            "supporting_evidence": [], "contradicting_evidence": [],
        })
        _write_flat(slug_dir / "REQ-DEMO-001.yaml", {
            "id": "REQ-DEMO-001", "kind": "requirement",
            "depends_on": ["CL-DEMO-001"], "check_id": "chk-a",
        })
        result = sr.detect_newly_coverable_checks(project_root, "demo", repo_root=repo, probe=True)
        assert result.coverable == [
            sr.NewlyCoverableCheck(check_id="chk-a", claim_id="CL-DEMO-001")
        ]

    def test_check_does_not_yet_collect(self, tmp_path):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        _setup_slug(project_root, "demo", checks=[
            _default_check(check_reference="tests/test_impl.py::test_does_not_exist")
        ])
        slug_dir = project_root / "planning" / "knowledge" / "demo"
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {"id": "CL-DEMO-001", "kind": "claim"})
        _write_flat(slug_dir / "REQ-DEMO-001.yaml", {
            "id": "REQ-DEMO-001", "kind": "requirement",
            "depends_on": ["CL-DEMO-001"], "check_id": "chk-a",
        })
        result = sr.detect_newly_coverable_checks(project_root, "demo", repo_root=repo, probe=True)
        assert result.coverable == []
        assert "chk-a" in result.not_yet_coverable

    def test_check_with_existing_evidence_is_never_newly_coverable_even_if_stale(self, tmp_path):
        """§0.2.B: a previously-covered check whose historical result has
        gone stale must stay detector (a)'s own scope, never detector (b)'s,
        regardless of "no currently-valid result"."""
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        contract_path, slug_dir = _setup_slug(project_root, "demo", checks=[_default_check()])
        result_path = (
            project_root / "planning" / "contracts" / "demo" / "results" / "chk-a--r1.yaml"
        )
        _write_fake_result(result_path, contract_path, check_id="chk-a")
        _write_flat(slug_dir / "EV-TEST-1.yaml", {
            "id": "EV-TEST-1", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_path.relative_to(project_root)}"',
        })
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {"id": "CL-DEMO-001", "kind": "claim"})
        _write_flat(slug_dir / "REQ-DEMO-001.yaml", {
            "id": "REQ-DEMO-001", "kind": "requirement",
            "depends_on": ["CL-DEMO-001"], "check_id": "chk-a",
        })
        # Simulate real staleness (decisions/0088): the test's own input
        # file changes under the already-recorded result -- this affects
        # evaluate_result_precedence's own current-validity question, but
        # must NOT affect the Evidence-bridge IDENTITY check (contract_id/
        # oracle_contract_id/scope), which is a historical-relationship
        # question only (classify_symbol's own established distinction).
        (repo / "tests" / "test_impl.py").write_text(
            "def test_ok():\n    assert True  # drifted\n", encoding="utf-8",
        )
        result = sr.detect_newly_coverable_checks(project_root, "demo", repo_root=repo, probe=True)
        assert result.coverable == []
        assert result.not_yet_coverable == []  # never even scanned -- detector (a)'s scope

    def test_multi_check_requirement_guard_refuses_ambiguous_resolution(self, tmp_path):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        _setup_slug(project_root, "demo", checks=[_default_check()])
        slug_dir = project_root / "planning" / "knowledge" / "demo"
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {"id": "CL-DEMO-001", "kind": "claim"})
        _write_flat(slug_dir / "CL-DEMO-002.yaml", {"id": "CL-DEMO-002", "kind": "claim"})
        _write_flat(slug_dir / "REQ-DEMO-001.yaml", {
            "id": "REQ-DEMO-001", "kind": "requirement",
            "depends_on": ["CL-DEMO-001", "CL-DEMO-002"], "check_id": "chk-a",
        })
        result = sr.detect_newly_coverable_checks(project_root, "demo", repo_root=repo, probe=True)
        assert result.coverable == []
        assert len(result.config_errors) == 1
        assert result.config_errors[0].check_id == "chk-a"

    def test_no_requirement_names_check_id_is_indeterminate(self, tmp_path):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        _setup_slug(project_root, "demo", checks=[_default_check()])
        result = sr.detect_newly_coverable_checks(project_root, "demo", repo_root=repo, probe=True)
        assert result.coverable == []
        assert any(c == "chk-a" for c, _ in result.indeterminate)

    def test_probe_false_never_runs_a_subprocess(self, tmp_path, monkeypatch):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        _setup_slug(project_root, "demo", checks=[_default_check()])
        slug_dir = project_root / "planning" / "knowledge" / "demo"
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {"id": "CL-DEMO-001", "kind": "claim"})
        _write_flat(slug_dir / "REQ-DEMO-001.yaml", {
            "id": "REQ-DEMO-001", "kind": "requirement",
            "depends_on": ["CL-DEMO-001"], "check_id": "chk-a",
        })

        def _fail(*a, **k):
            raise AssertionError("subprocess.Popen must never be called with probe=False")

        monkeypatch.setattr(subprocess, "Popen", _fail)
        result = sr.detect_newly_coverable_checks(project_root, "demo", repo_root=repo, probe=False)
        assert result.coverable == []
        assert "chk-a" in result.not_yet_coverable  # unknown until probed -- reported honestly


# ---------------------------------------------------------------------------
# Durable OracleResult persistence + portability (dispatch §3.B)
# ---------------------------------------------------------------------------


class TestDurableResultPersistence:
    def test_persist_and_verify_writes_results_dir_and_results_raw_dir(self, tmp_path):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        contract_path, _ = _setup_slug(project_root, "demo", checks=[_default_check()])
        contract = oracle.parse_oracle_contract(contract_path)
        check = contract.check_by_id("chk-a")
        with sr._chdir(project_root):
            result = oracle.evaluate_check(
                contract, check, contract_path=contract_path, repo_root=repo,
                raw_output_dir=sr._durable_raw_output_dir("demo"),
            )
        out_path, ok, _reason = sr._persist_and_verify(project_root, "demo", result)
        assert ok
        assert out_path.is_file()
        assert (project_root / "planning" / "contracts" / "demo" / "results" / "raw").is_dir()
        assert "scratch-assessments" not in result.raw_output_ref

    def test_reloading_from_a_freshly_copied_location_still_resolves(self, tmp_path):
        """Portability: copy the whole knowledge_root elsewhere and
        confirm the persisted result + its raw output still resolve
        correctly (the relative-path convention is the whole point)."""
        import shutil

        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        contract_path, _ = _setup_slug(project_root, "demo", checks=[_default_check()])
        contract = oracle.parse_oracle_contract(contract_path)
        check = contract.check_by_id("chk-a")
        with sr._chdir(project_root):
            result = oracle.evaluate_check(
                contract, check, contract_path=contract_path, repo_root=repo,
                raw_output_dir=sr._durable_raw_output_dir("demo"),
            )
        out_path, ok, _ = sr._persist_and_verify(project_root, "demo", result)
        assert ok

        moved_root = tmp_path / "moved-knowledge-root"
        shutil.copytree(project_root, moved_root)
        moved_result_path = moved_root / out_path.relative_to(project_root)
        with sr._chdir(moved_root):
            reparsed = oracle.parse_oracle_result(moved_result_path)
            moved_contract_path = (
                moved_root / "planning" / "contracts" / "demo" / "oracle-contract.yaml"
            )
            outcome, _reason = oracle.evaluate_result_precedence(
                reparsed, contract, check,
                contract_path=moved_contract_path,
                repo_root=repo,
            )
        assert outcome == "PASS"

    def test_corrupted_raw_output_fails_closed(self, tmp_path):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        contract_path, _ = _setup_slug(project_root, "demo", checks=[_default_check()])
        contract = oracle.parse_oracle_contract(contract_path)
        check = contract.check_by_id("chk-a")
        with sr._chdir(project_root):
            result = oracle.evaluate_check(
                contract, check, contract_path=contract_path, repo_root=repo,
                raw_output_dir=sr._durable_raw_output_dir("demo"),
            )
        out_path, ok, _ = sr._persist_and_verify(project_root, "demo", result)
        assert ok
        raw_path = project_root / result.raw_output_ref
        raw_path.write_text("CORRUPTED", encoding="utf-8")
        # A fresh, independent re-check now fails closed.
        reparsed = oracle.parse_oracle_result(out_path)
        assert oracle.sha256_file(raw_path) != reparsed.raw_output_sha256

    def test_retry_never_rewrites_an_already_persisted_result(self, tmp_path):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        contract_path, _ = _setup_slug(project_root, "demo", checks=[_default_check()])
        contract = oracle.parse_oracle_contract(contract_path)
        check = contract.check_by_id("chk-a")
        with sr._chdir(project_root):
            result = oracle.evaluate_check(
                contract, check, contract_path=contract_path, repo_root=repo,
                raw_output_dir=sr._durable_raw_output_dir("demo"),
            )
        out_path1, ok1, reason1 = sr._persist_and_verify(project_root, "demo", result)
        assert ok1 and "persisted and verified" in reason1
        before = out_path1.read_text(encoding="utf-8")
        out_path2, ok2, reason2 = sr._persist_and_verify(project_root, "demo", result)
        assert ok2 and "already persisted" in reason2
        assert out_path1 == out_path2
        assert out_path2.read_text(encoding="utf-8") == before

    def test_modified_test_input_invalidates_the_persisted_result(self, tmp_path):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        contract_path, _ = _setup_slug(project_root, "demo", checks=[_default_check()])
        contract = oracle.parse_oracle_contract(contract_path)
        check = contract.check_by_id("chk-a")
        with sr._chdir(project_root):
            result = oracle.evaluate_check(
                contract, check, contract_path=contract_path, repo_root=repo,
                raw_output_dir=sr._durable_raw_output_dir("demo"),
            )
        sr._persist_and_verify(project_root, "demo", result)
        (repo / "tests" / "test_impl.py").write_text(
            "def test_ok():\n    assert True  # changed\n", encoding="utf-8",
        )
        outcome, reason = oracle.evaluate_result_precedence(
            result, contract, check, contract_path=contract_path, repo_root=repo,
        )
        assert outcome == "INVALID"
        assert "test_input_digest" in reason


# ---------------------------------------------------------------------------
# propose_reconciliation + write_source_reconciliation_manifest +
# apply_manifest's new "source_reconciliation" branch -- Evidence
# identity, cumulative evidence_support_state, same-Claim merge,
# conflicting-edit refusal
# ---------------------------------------------------------------------------


class TestReconfirmationAfterMutationReversal:
    def test_re_confirmed_pass_is_still_proposed_against_a_non_supported_claim(self, tmp_path):
        """A fresh VERIFIED_SCOPE re-confirming a Claim that is NOT yet
        `evidence_support_state: supported` (e.g. `conflicting`, from an
        earlier accepted regression) must still be proposed -- real-world
        scenario: a regression mutation is reversed and re-verified; the
        fix must not be silently dropped as a no-op just because a
        historical PASS also existed before the regression."""
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        graph_db = _sync_graph(repo)
        contract_path, slug_dir = _setup_slug(project_root, "demo", checks=[_default_check()])
        results_dir = project_root / "planning" / "contracts" / "demo" / "results"
        old_pass_path = results_dir / "chk-a--old.yaml"
        _write_fake_result(
            old_pass_path, contract_path, check_id="chk-a", run_id="old", outcome="PASS"
        )
        regression_path = results_dir / "chk-a--reg.yaml"
        _write_fake_result(
            regression_path, contract_path, check_id="chk-a", run_id="reg", outcome="FAIL"
        )
        _write_flat(slug_dir / "EV-SRC-1.yaml", {
            "id": "EV-SRC-1", "kind": "evidence", "evidence_kind": "source",
            "source_ref": '"impl.py:5 def target_function"',
        })
        _write_flat(slug_dir / "EV-TEST-1.yaml", {
            "id": "EV-TEST-1", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{old_pass_path.relative_to(project_root)}"',
        })
        _write_flat(slug_dir / "EV-TEST-2.yaml", {
            "id": "EV-TEST-2", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{regression_path.relative_to(project_root)}"',
        })
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {
            "id": "CL-DEMO-001", "kind": "claim",
            "supporting_evidence": ["EV-SRC-1", "EV-TEST-1"],
            "contradicting_evidence": ["EV-TEST-2"],
            "evidence_support_state": "conflicting",
        })
        sr.establish_source_baseline(
            project_root, "demo", "impl.py", oracle.sha256_file(repo / "impl.py")
        )
        # The test now genuinely passes again (mutation reversed) --
        # touch the file (so it's detected as "changed") without
        # altering behaviour, then re-sync.
        (repo / "impl.py").write_text(_IMPL_TEXT + "\n# reversed\n", encoding="utf-8")
        graph_db = _sync_graph(repo)
        source_result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert any(f.path == "impl.py" for f in source_result.changed)

        proposal = sr.propose_reconciliation(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db,
            source_changes=source_result,
        )
        findings = proposal.findings
        assert len(findings) == 1
        assert findings[0].label == "re_confirmed"
        assert findings[0].target_field == "supporting_evidence"
        assert findings[0].claim_id == "CL-DEMO-001"


class TestEndToEndReconciliation:
    def _setup_newly_coverable(self, tmp_path):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        contract_path, slug_dir = _setup_slug(project_root, "demo", checks=[_default_check()])
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {
            "id": "CL-DEMO-001", "kind": "claim",
            "supporting_evidence": ["EV-SRC-1"], "contradicting_evidence": [],
            "evidence_support_state": "partially_supported",
        })
        _write_flat(slug_dir / "EV-SRC-1.yaml", {
            "id": "EV-SRC-1", "kind": "evidence", "evidence_kind": "source",
            "source_ref": '"impl.py:5 def target_function"',
        })
        _write_flat(slug_dir / "REQ-DEMO-001.yaml", {
            "id": "REQ-DEMO-001", "kind": "requirement",
            "depends_on": ["CL-DEMO-001"], "check_id": "chk-a",
        })
        return project_root, repo

    def test_newly_coverable_check_pass_upgrades_claim_to_supported(self, tmp_path):
        project_root, repo = self._setup_newly_coverable(tmp_path)
        coverable = sr.detect_newly_coverable_checks(
            project_root, "demo", repo_root=repo, probe=True
        )
        assert coverable.coverable
        proposal = sr.propose_reconciliation(
            project_root, "demo", repo_root=repo, newly_coverable=coverable.coverable,
        )
        findings = proposal.findings
        assert len(findings) == 1
        assert findings[0].label == "newly_covered"
        assert findings[0].target_field == "supporting_evidence"
        manifest_path = sr.write_source_reconciliation_manifest(
            project_root, "demo", findings, repo_root=repo,
        )
        assert manifest_path is not None

        import tomllib
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        assert len(data["items"]) == 1
        item = data["items"][0]
        item["decision"] = "accept"
        manifest_path.write_text(ki._serialize_manifest(data), encoding="utf-8")

        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 1
        records = ki.load_slug_records(project_root / "planning" / "knowledge" / "demo")
        claim = records["CL-DEMO-001"]
        assert claim.fields["evidence_support_state"] == "supported"
        assert "EV-X-001" not in claim.fields["supporting_evidence"]
        new_evidence_ids = [
            rid for rid, rec in records.items()
            if rec.kind == "evidence" and rid.startswith("EV-") and rid != "EV-SRC-1"
        ]
        assert len(new_evidence_ids) == 1
        assert new_evidence_ids[0] in claim.fields["supporting_evidence"]

    def test_evidence_identity_retry_never_duplicates(self, tmp_path):
        project_root, repo = self._setup_newly_coverable(tmp_path)
        coverable = sr.detect_newly_coverable_checks(
            project_root, "demo", repo_root=repo, probe=True
        )
        proposal = sr.propose_reconciliation(
            project_root, "demo", repo_root=repo, newly_coverable=coverable.coverable,
        )
        findings = proposal.findings
        manifest_path = sr.write_source_reconciliation_manifest(
            project_root, "demo", findings, repo_root=repo,
        )
        import tomllib
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        data["items"][0]["decision"] = "accept"
        manifest_path.write_text(ki._serialize_manifest(data), encoding="utf-8")

        ki.apply_manifest(project_root, manifest_path)
        records_after_first = ki.load_slug_records(project_root / "planning" / "knowledge" / "demo")
        evidence_count_1 = sum(1 for r in records_after_first.values() if r.kind == "evidence")

        # Simulate a retry of the same already-applied item (e.g. a crash
        # before the manifest's own buffered state write landed).
        data2 = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        data2["items"][0]["state"] = "pending"  # force re-apply as if the flag never persisted
        manifest_path.write_text(ki._serialize_manifest(data2), encoding="utf-8")
        ki.apply_manifest(project_root, manifest_path)
        records_after_retry = ki.load_slug_records(project_root / "planning" / "knowledge" / "demo")
        evidence_count_2 = sum(1 for r in records_after_retry.values() if r.kind == "evidence")
        assert evidence_count_1 == evidence_count_2  # no duplicate Evidence written
        claim = records_after_retry["CL-DEMO-001"]
        supporting = ki._extract_id_strings(claim.fields["supporting_evidence"])
        assert len(supporting) == len(set(supporting))  # no duplicate citation either

    def test_conflicting_edit_between_detection_and_apply_is_refused(self, tmp_path):
        project_root, repo = self._setup_newly_coverable(tmp_path)
        coverable = sr.detect_newly_coverable_checks(
            project_root, "demo", repo_root=repo, probe=True
        )
        proposal = sr.propose_reconciliation(
            project_root, "demo", repo_root=repo, newly_coverable=coverable.coverable,
        )
        findings = proposal.findings
        manifest_path = sr.write_source_reconciliation_manifest(
            project_root, "demo", findings, repo_root=repo,
        )
        import tomllib
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        data["items"][0]["decision"] = "accept"
        manifest_path.write_text(ki._serialize_manifest(data), encoding="utf-8")

        # A human hand-edits the Claim between detection and apply.
        slug_dir = project_root / "planning" / "knowledge" / "demo"
        claim_path = slug_dir / "CL-DEMO-001.yaml"
        claim_path.write_text(
            claim_path.read_text(encoding="utf-8") + "\n# hand edit\n", encoding="utf-8"
        )

        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 0
        assert len(result.skipped) == 1
        assert "race" in result.skipped[0].reason

    def test_cumulative_state_preserves_historical_contradiction(self, tmp_path):
        """§4.4: a Claim already carrying a contradicting_evidence entry
        from an earlier batch must stay "conflicting" (never silently
        reset to "supported") when a later batch adds only supporting
        evidence."""
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        contract_path, slug_dir = _setup_slug(project_root, "demo", checks=[_default_check()])
        _write_flat(slug_dir / "EV-DEMO-099.yaml", {
            "id": "EV-DEMO-099", "kind": "evidence",
            "evidence_kind": "test", "test_ref": "null",
        })
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {
            "id": "CL-DEMO-001", "kind": "claim",
            "supporting_evidence": [], "contradicting_evidence": ["EV-DEMO-099"],
            "evidence_support_state": "unsupported",
        })
        result_path = (
            project_root / "planning" / "contracts" / "demo" / "results" / "chk-a--r2.yaml"
        )
        _write_fake_result(
            result_path, contract_path, check_id="chk-a", run_id="r2", outcome="PASS",
            repo_root=repo,
        )
        from codecompass.knowledge_intermediate import _apply_source_reconciliation

        item = {
            "kind": "source_reconciliation", "record_id": "CL-DEMO-001",
            "base_claim_hash": ki.sha256_text(
                (slug_dir / "CL-DEMO-001.yaml").read_text(encoding="utf-8")
            ),
            "repo_root": str(repo),
            "contributing_contract_ids": ["REQ-X-001"], "contributing_check_ids": ["chk-a"],
            "contributing_run_ids": ["r2"], "contributing_labels": ["re_confirmed"],
            "contributing_target_fields": ["supporting_evidence"],
            "contributing_what_it_shows": ["fresh PASS"],
            "contributing_repository_revisions": ["working tree"],
        }
        outcome = _apply_source_reconciliation(project_root, "demo", item)
        assert outcome.ok
        records = ki.load_slug_records(slug_dir)
        claim = records["CL-DEMO-001"]
        assert claim.fields["evidence_support_state"] == "conflicting"
        assert "EV-DEMO-099" in claim.fields["contradicting_evidence"]


# ---------------------------------------------------------------------------
# CLI boundary tests (dispatch §3.D / §6)
# ---------------------------------------------------------------------------


class TestCliBoundaries:
    def test_detect_changes_without_probe_spawns_no_subprocess_and_writes_nothing(
        self, tmp_path, monkeypatch
    ):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        _setup_slug(project_root, "demo", checks=[_default_check()])
        slug_dir = project_root / "planning" / "knowledge" / "demo"
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {"id": "CL-DEMO-001", "kind": "claim"})
        _write_flat(slug_dir / "REQ-DEMO-001.yaml", {
            "id": "REQ-DEMO-001", "kind": "requirement",
            "depends_on": ["CL-DEMO-001"], "check_id": "chk-a",
        })

        def _fail(*a, **k):
            raise AssertionError("no subprocess should be spawned without --probe-coverage")

        monkeypatch.setattr(subprocess, "Popen", _fail)
        monkeypatch.chdir(project_root)
        before = set((project_root / "planning").rglob("*"))
        res = runner.invoke(
            cli.app, ["knowledge", "detect-changes", "demo", "--repo-root", str(repo)]
        )
        assert res.exit_code == 0
        after = set((project_root / "planning").rglob("*"))
        assert before == after  # zero files written

    def test_detect_changes_with_probe_spawns_exactly_one_collect_only_subprocess(
        self, tmp_path, monkeypatch
    ):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        _setup_slug(project_root, "demo", checks=[_default_check()])
        slug_dir = project_root / "planning" / "knowledge" / "demo"
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {"id": "CL-DEMO-001", "kind": "claim"})
        _write_flat(slug_dir / "REQ-DEMO-001.yaml", {
            "id": "REQ-DEMO-001", "kind": "requirement",
            "depends_on": ["CL-DEMO-001"], "check_id": "chk-a",
        })
        calls = []
        real_popen = subprocess.Popen

        def _tracking_popen(cmd, *a, **k):
            calls.append(cmd)
            return real_popen(cmd, *a, **k)

        monkeypatch.setattr(subprocess, "Popen", _tracking_popen)
        monkeypatch.chdir(project_root)
        before = set((project_root / "planning").rglob("*"))
        res = runner.invoke(
            cli.app,
            ["knowledge", "detect-changes", "demo", "--repo-root", str(repo), "--probe-coverage"],
        )
        assert res.exit_code == 0
        assert len(calls) == 1
        assert "--collect-only" in calls[0]
        after = set((project_root / "planning").rglob("*"))
        assert before == after  # a probe still writes nothing

    def test_verify_changes_executes_and_persists(self, tmp_path, monkeypatch):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        contract_path, slug_dir = _setup_slug(project_root, "demo", checks=[_default_check()])
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {
            "id": "CL-DEMO-001", "kind": "claim",
            "supporting_evidence": [], "contradicting_evidence": [],
            "evidence_support_state": "unsupported",
        })
        _write_flat(slug_dir / "REQ-DEMO-001.yaml", {
            "id": "REQ-DEMO-001", "kind": "requirement",
            "depends_on": ["CL-DEMO-001"], "check_id": "chk-a",
        })
        monkeypatch.chdir(project_root)
        res = runner.invoke(
            cli.app, ["knowledge", "verify-changes", "demo", "--repo-root", str(repo), "--json"]
        )
        assert res.exit_code == 0
        results_dir = project_root / "planning" / "contracts" / "demo" / "results"
        assert any(results_dir.glob("chk-a--*.yaml"))
        reconciliation_dir = project_root / "planning" / "knowledge" / "demo" / "reconciliation"
        manifests = list(reconciliation_dir.glob("*-source.toml"))
        assert len(manifests) == 1

    def test_apply_cli_recognises_source_reconciliation_kind(self, tmp_path, monkeypatch):
        """CLAUDE.md L-021: apply_manifest's real production call site is
        cli.py::knowledge_apply_manifest -- exercised directly, not only
        apply_manifest() called in isolation."""
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        contract_path, slug_dir = _setup_slug(project_root, "demo", checks=[_default_check()])
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {
            "id": "CL-DEMO-001", "kind": "claim",
            "supporting_evidence": [], "contradicting_evidence": [],
            "evidence_support_state": "unsupported",
        })
        _write_flat(slug_dir / "REQ-DEMO-001.yaml", {
            "id": "REQ-DEMO-001", "kind": "requirement",
            "depends_on": ["CL-DEMO-001"], "check_id": "chk-a",
        })
        monkeypatch.chdir(project_root)
        runner.invoke(cli.app, ["knowledge", "verify-changes", "demo", "--repo-root", str(repo)])
        reconciliation_dir = project_root / "planning" / "knowledge" / "demo" / "reconciliation"
        manifest_path = next(reconciliation_dir.glob("*-source.toml"))
        import tomllib
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        data["items"][0]["decision"] = "accept"
        manifest_path.write_text(ki._serialize_manifest(data), encoding="utf-8")

        res = runner.invoke(cli.app, ["knowledge", "apply", str(manifest_path)])
        assert res.exit_code == 0
        assert "applied" in res.stdout
        records = ki.load_slug_records(project_root / "planning" / "knowledge" / "demo")
        assert records["CL-DEMO-001"].fields["evidence_support_state"] == "supported"


# ---------------------------------------------------------------------------
# Phase 89A corrective pass (decisions/0097) -- defect A: a shared
# test-input path must identify and independently attribute EVERY
# covered check sharing it, never silently drop all but one.
# ---------------------------------------------------------------------------


class TestSharedTestInputMultiCheck:
    def _setup(self, tmp_path):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path, test_text=_TEST_TEXT_TWO)
        checks = [
            _default_check(check_id="chk-a", scope="scope A",
                            check_reference="tests/test_impl.py::test_ok"),
            _default_check(check_id="chk-b", scope="scope B",
                            check_reference="tests/test_impl.py::test_ok_2"),
        ]
        contract_path, slug_dir = _setup_slug(project_root, "demo", checks=checks)
        results_dir = project_root / "planning" / "contracts" / "demo" / "results"
        result_a = results_dir / "chk-a--r1.yaml"
        result_b = results_dir / "chk-b--r1.yaml"
        _write_fake_result(
            result_a, contract_path, check_id="chk-a", scope="scope A", repo_root=repo
        )
        _write_fake_result(
            result_b, contract_path, check_id="chk-b", scope="scope B", repo_root=repo
        )
        _write_flat(slug_dir / "EV-TEST-001.yaml", {
            "id": "EV-TEST-001", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_a.relative_to(project_root)}"',
        })
        _write_flat(slug_dir / "EV-TEST-002.yaml", {
            "id": "EV-TEST-002", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_b.relative_to(project_root)}"',
        })
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {
            "id": "CL-DEMO-001", "kind": "claim",
            "supporting_evidence": ["EV-TEST-001"], "contradicting_evidence": [],
            "evidence_support_state": "partially_supported",
        })
        _write_flat(slug_dir / "CL-DEMO-002.yaml", {
            "id": "CL-DEMO-002", "kind": "claim",
            "supporting_evidence": ["EV-TEST-002"], "contradicting_evidence": [],
            "evidence_support_state": "partially_supported",
        })
        original_hash = oracle.sha256_file(repo / "tests" / "test_impl.py")
        sr.establish_source_baseline(project_root, "demo", "tests/test_impl.py", original_hash)
        graph_db = _sync_graph(repo)
        return project_root, repo, contract_path, slug_dir, graph_db, original_hash

    def test_shared_test_input_change_detected_for_every_covered_check(self, tmp_path):
        """Core defect-A regression: both checks sharing `tests/
        test_impl.py` must be reported as independent findings, each
        correctly attributed to its own bridged Claim -- the original
        bug silently dropped all but the last check iterated."""
        project_root, repo, _cp, _sd, graph_db, _oh = self._setup(tmp_path)
        (repo / "tests" / "test_impl.py").write_text(
            _TEST_TEXT_TWO + "\n# edit\n", encoding="utf-8"
        )
        graph_db = _sync_graph(repo)
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        changed = [f for f in result.changed if f.resolution == "test_input_change"]
        assert {f.check_id for f in changed} == {"chk-a", "chk-b"}
        assert all(f.path == "tests/test_impl.py" for f in changed)
        by_check = {f.check_id: f for f in changed}
        assert by_check["chk-a"].claim_ids == ["CL-DEMO-001"]
        assert by_check["chk-b"].claim_ids == ["CL-DEMO-002"]

    def test_repeated_detection_is_deterministic_and_non_duplicating(self, tmp_path):
        """Calling `detect_source_changes` twice in a row (no further
        change in between) is purely observational and reports exactly
        the same two findings both times -- no accumulation, no
        duplication, no side effect."""
        project_root, repo, _cp, _sd, graph_db, _oh = self._setup(tmp_path)
        (repo / "tests" / "test_impl.py").write_text(
            _TEST_TEXT_TWO + "\n# edit\n", encoding="utf-8"
        )
        graph_db = _sync_graph(repo)
        first = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        second = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        key = lambda f: (f.path, f.resolution, f.check_id, tuple(f.claim_ids))  # noqa: E731
        assert sorted(map(key, first.changed)) == sorted(map(key, second.changed))
        assert len(first.changed) == 2

    def test_unresolvable_sibling_check_blocks_shared_baseline_eligibility(self, tmp_path):
        """A path required by two checks is eligible for baseline
        advancement only once BOTH are successfully, validly accounted
        for -- a sibling check that cannot even be resolved against the
        live contract must never let the other's own success advance
        the shared baseline."""
        project_root, repo, _cp, _sd, graph_db, _oh = self._setup(tmp_path)
        source_result = sr.DetectSourceChangesResult(changed=[
            sr.SourceChangeFinding(
                path="tests/test_impl.py", resolution="test_input_change",
                check_id="chk-a", claim_ids=["CL-DEMO-001"],
            ),
            sr.SourceChangeFinding(
                path="tests/test_impl.py", resolution="test_input_change",
                check_id="chk-ghost", claim_ids=["CL-DEMO-002"],
            ),
        ])
        proposal = sr.propose_reconciliation(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db,
            source_changes=source_result,
        )
        assert any(f.check_id == "chk-a" for f in proposal.findings)
        assert not any(f.check_id == "chk-ghost" for f in proposal.findings)
        assert "tests/test_impl.py" not in proposal.baseline_eligible_test_input_paths

    def test_reject_one_accept_other_blocks_shared_baseline_advance(self, tmp_path):
        """Mandatory partially-resolved multi-check control: accepting
        chk-a's own item while rejecting chk-b's sibling item (both
        citing the same shared file) must apply chk-a's effect but
        never advance the shared file's baseline -- chk-b's own check
        remains genuinely unresolved, never silently waived."""
        project_root, repo, _cp, slug_dir, graph_db, original_hash = self._setup(tmp_path)
        (repo / "tests" / "test_impl.py").write_text(
            _TEST_TEXT_TWO + "\n# shared edit\n", encoding="utf-8"
        )
        graph_db = _sync_graph(repo)
        source_result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        proposal = sr.propose_reconciliation(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db,
            source_changes=source_result,
        )
        assert {f.check_id for f in proposal.findings} == {"chk-a", "chk-b"}
        assert "tests/test_impl.py" in proposal.baseline_eligible_test_input_paths
        manifest_path = sr.write_source_reconciliation_manifest(
            project_root, "demo", proposal.findings, repo_root=repo, target_graph_db=graph_db,
            baseline_eligible_test_input_paths=proposal.baseline_eligible_test_input_paths,
        )
        import tomllib
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        assert len(data["items"]) == 2
        for item in data["items"]:
            item["decision"] = "accept" if item["record_id"] == "CL-DEMO-001" else "reject"
        manifest_path.write_text(ki._serialize_manifest(data), encoding="utf-8")

        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 1
        assert len(result.skipped) == 1
        assert result.applied[0].new_record_id == "CL-DEMO-001"

        data_after = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        for item in data_after["items"]:
            if item.get("kind") == "source_reconciliation" and item.get("state") == "applied":
                sr.advance_baselines_for_applied_item(
                    project_root, "demo", item, manifest_items=data_after["items"],
                )
        baseline = sr._read_baseline(project_root, "demo")
        assert baseline["tests/test_impl.py"]["content_hash"] == original_hash  # unchanged

        records = ki.load_slug_records(slug_dir)
        assert records["CL-DEMO-001"].fields["evidence_support_state"] == "supported"
        assert records["CL-DEMO-002"].fields["evidence_support_state"] == "partially_supported"

        # Now resolve the sibling too, via a fresh verify-changes-style
        # proposal + accept + apply -- once every check sharing the
        # file is genuinely applied, the baseline is free to advance.
        source_result2 = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        proposal2 = sr.propose_reconciliation(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db,
            source_changes=source_result2,
        )
        assert {f.check_id for f in proposal2.findings} == {"chk-b"}
        manifest_path2 = sr.write_source_reconciliation_manifest(
            project_root, "demo", proposal2.findings, repo_root=repo, target_graph_db=graph_db,
            baseline_eligible_test_input_paths=proposal2.baseline_eligible_test_input_paths,
        )
        data2 = tomllib.loads(manifest_path2.read_text(encoding="utf-8"))
        data2["items"][0]["decision"] = "accept"
        manifest_path2.write_text(ki._serialize_manifest(data2), encoding="utf-8")
        ki.apply_manifest(project_root, manifest_path2)
        data2_after = tomllib.loads(manifest_path2.read_text(encoding="utf-8"))
        for item in data2_after["items"]:
            if item.get("kind") == "source_reconciliation" and item.get("state") == "applied":
                sr.advance_baselines_for_applied_item(
                    project_root, "demo", item, manifest_items=data2_after["items"],
                )
        baseline2 = sr._read_baseline(project_root, "demo")
        new_hash = oracle.sha256_file(repo / "tests" / "test_impl.py")
        assert baseline2["tests/test_impl.py"]["content_hash"] == new_hash


# ---------------------------------------------------------------------------
# Phase 89A corrective pass -- bounded check 1: a non-Python oracle
# input (never indexed by the target's own symbol graph) is still
# tracked, directly by content hash.
# ---------------------------------------------------------------------------


class TestNonPythonFixtureTracking:
    def _setup(self, tmp_path):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        (repo / "tests" / "fixtures").mkdir(parents=True)
        fixture_path = repo / "tests" / "fixtures" / "data.journal"
        fixture_path.write_text("2026-01-01 opening balance\n", encoding="utf-8")
        contract_path, slug_dir = _setup_slug(project_root, "demo", checks=[
            _default_check(test_input_paths=["tests/test_impl.py", "tests/fixtures/data.journal"])
        ])
        result_path = (
            project_root / "planning" / "contracts" / "demo" / "results" / "chk-a--r1.yaml"
        )
        _write_fake_result(result_path, contract_path, check_id="chk-a", repo_root=repo)
        _write_flat(slug_dir / "EV-TEST-1.yaml", {
            "id": "EV-TEST-1", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_path.relative_to(project_root)}"',
        })
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {
            "id": "CL-DEMO-001", "kind": "claim",
            "supporting_evidence": ["EV-TEST-1"], "contradicting_evidence": [],
            "evidence_support_state": "partially_supported",
        })
        # The graph is synced over impl.py/tests/test_impl.py only --
        # the fixture is deliberately never indexed, mirroring a real
        # non-Python oracle input (tests/fixtures/filtered.journal).
        graph_db = _sync_graph(repo)
        return project_root, repo, fixture_path, graph_db

    def test_new_fixture_can_still_have_a_baseline_established(self, tmp_path):
        project_root, repo, fixture_path, graph_db = self._setup(tmp_path)
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert "tests/fixtures/data.journal" in result.new_files
        established = sr.establish_baselines_for_new_files(
            project_root, "demo", repo_root=repo, result=result, target_graph_db=graph_db,
        )
        assert "tests/fixtures/data.journal" in established
        baseline = sr._read_baseline(project_root, "demo")
        assert (
            baseline["tests/fixtures/data.journal"]["content_hash"]
            == oracle.sha256_file(fixture_path)
        )

    def test_changed_fixture_is_detected_not_stale_graph_index(self, tmp_path):
        project_root, repo, fixture_path, graph_db = self._setup(tmp_path)
        sr.establish_source_baseline(
            project_root, "demo", "tests/fixtures/data.journal", oracle.sha256_file(fixture_path)
        )
        fixture_path.write_text(
            "2026-01-01 opening balance\n2026-01-02 groceries\n", encoding="utf-8",
        )
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert any(
            f.path == "tests/fixtures/data.journal" and f.resolution == "test_input_change"
            for f in result.changed
        )
        assert not any(f.path == "tests/fixtures/data.journal" for f in result.stale_graph_index)

    def test_unchanged_fixture_reports_nothing(self, tmp_path):
        project_root, repo, fixture_path, graph_db = self._setup(tmp_path)
        sr.establish_source_baseline(
            project_root, "demo", "tests/fixtures/data.journal", oracle.sha256_file(fixture_path)
        )
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert not any(f.path == "tests/fixtures/data.journal" for f in result.changed)
        assert not any(f.path == "tests/fixtures/data.journal" for f in result.stale_graph_index)

    def test_deleted_fixture_reported_distinctly(self, tmp_path):
        project_root, repo, fixture_path, graph_db = self._setup(tmp_path)
        sr.establish_source_baseline(
            project_root, "demo", "tests/fixtures/data.journal", oracle.sha256_file(fixture_path)
        )
        fixture_path.unlink()
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert "tests/fixtures/data.journal" in result.deleted_files

    def test_unrelated_fixture_never_tracked(self, tmp_path):
        project_root, repo, fixture_path, graph_db = self._setup(tmp_path)
        unrelated = repo / "tests" / "fixtures" / "unrelated.journal"
        unrelated.write_text("nothing to see\n", encoding="utf-8")
        result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        assert "tests/fixtures/unrelated.journal" not in result.new_files
        assert not any(f.path == "tests/fixtures/unrelated.journal" for f in result.changed)


# ---------------------------------------------------------------------------
# Phase 89A corrective pass -- bounded check 2: working-tree provenance
# must never silently imply a clean commit was verified when the tree
# is dirty.
# ---------------------------------------------------------------------------


class TestWorkingTreeProvenance:
    def test_clean_tree_returns_bare_commit_hash(self, tmp_path):
        repo = tmp_path / "git-repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
        (repo / "f.txt").write_text("x\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
        rev = sr._repo_revision(repo)
        assert "+dirty" not in rev
        assert len(rev) == 40  # a bare commit hash, nothing appended

    def test_dirty_tree_is_marked_and_carries_content_digests(self, tmp_path):
        repo = tmp_path / "git-repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
        (repo / "f.txt").write_text("x\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
        (repo / "f.txt").write_text("y uncommitted\n", encoding="utf-8")  # dirty now

        class _FakeResult:
            tested_subject_digest = "a" * 64
            test_input_digest = "b" * 64

        rev = sr._repo_revision(repo, fresh_result=_FakeResult())
        assert "+dirty" in rev
        assert "a" * 64 in rev
        assert "b" * 64 in rev

    def test_dirty_tree_without_fresh_result_still_marks_dirty(self, tmp_path):
        repo = tmp_path / "git-repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
        (repo / "f.txt").write_text("x\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
        (repo / "f.txt").write_text("y uncommitted\n", encoding="utf-8")
        rev = sr._repo_revision(repo)
        assert rev.endswith("+dirty")


# ---------------------------------------------------------------------------
# Phase 89A corrective pass -- defect B: apply-time re-validation must
# never trust a stale or tampered cited result.
# ---------------------------------------------------------------------------


def _setup_accepted_manifest(tmp_path):
    """A single-check, fully proposed-and-accepted (not yet applied)
    manifest, for the defect-B tamper tests below to mutate on-disk
    state against before calling `apply`."""
    project_root = tmp_path / "knowledge-root"
    repo = _build_repo(tmp_path)
    contract_path, slug_dir = _setup_slug(project_root, "demo", checks=[_default_check()])
    _write_flat(slug_dir / "CL-DEMO-001.yaml", {
        "id": "CL-DEMO-001", "kind": "claim",
        "supporting_evidence": [], "contradicting_evidence": [],
        "evidence_support_state": "unsupported",
    })
    _write_flat(slug_dir / "REQ-DEMO-001.yaml", {
        "id": "REQ-DEMO-001", "kind": "requirement",
        "depends_on": ["CL-DEMO-001"], "check_id": "chk-a",
    })
    coverable = sr.detect_newly_coverable_checks(project_root, "demo", repo_root=repo, probe=True)
    assert coverable.coverable
    proposal = sr.propose_reconciliation(
        project_root, "demo", repo_root=repo, newly_coverable=coverable.coverable,
    )
    manifest_path = sr.write_source_reconciliation_manifest(
        project_root, "demo", proposal.findings, repo_root=repo,
    )
    import tomllib
    data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    data["items"][0]["decision"] = "accept"
    manifest_path.write_text(ki._serialize_manifest(data), encoding="utf-8")
    result_path = next(
        (project_root / "planning" / "contracts" / "demo" / "results").glob("chk-a--*.yaml")
    )
    return project_root, repo, contract_path, slug_dir, manifest_path, result_path


class TestApplyTimeRevalidation:
    def test_legitimate_untampered_item_still_applies(self, tmp_path):
        project_root, repo, _cp, slug_dir, manifest_path, _rp = _setup_accepted_manifest(tmp_path)
        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 1
        records = ki.load_slug_records(slug_dir)
        assert records["CL-DEMO-001"].fields["evidence_support_state"] == "supported"

    def test_tampered_raw_output_is_refused(self, tmp_path):
        (
            project_root,
            repo,
            _cp,
            slug_dir,
            manifest_path,
            result_path,
        ) = _setup_accepted_manifest(tmp_path)
        reparsed = oracle.parse_oracle_result(result_path)
        raw_path = project_root / reparsed.raw_output_ref
        raw_path.write_text("TAMPERED", encoding="utf-8")
        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 0
        assert "failed re-validation" in result.skipped[0].reason
        records = ki.load_slug_records(slug_dir)
        assert records["CL-DEMO-001"].fields["evidence_support_state"] == "unsupported"
        assert not any(r.kind == "evidence" for r in records.values())

    def test_tampered_outcome_is_refused(self, tmp_path):
        (
            project_root,
            repo,
            _cp,
            slug_dir,
            manifest_path,
            result_path,
        ) = _setup_accepted_manifest(tmp_path)
        text = result_path.read_text(encoding="utf-8")
        tampered = text.replace("outcome: PASS", "outcome: FAIL")
        assert tampered != text
        result_path.write_text(tampered, encoding="utf-8")
        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 0
        assert "disagrees" in result.skipped[0].reason
        records = ki.load_slug_records(slug_dir)
        assert not any(r.kind == "evidence" for r in records.values())

    def test_tampered_contract_id_is_refused(self, tmp_path):
        (
            project_root,
            repo,
            _cp,
            slug_dir,
            manifest_path,
            result_path,
        ) = _setup_accepted_manifest(tmp_path)
        text = result_path.read_text(encoding="utf-8")
        tampered = text.replace("contract_id: REQ-X-001", "contract_id: REQ-GHOST-999")
        assert tampered != text
        result_path.write_text(tampered, encoding="utf-8")
        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 0
        records = ki.load_slug_records(slug_dir)
        assert not any(r.kind == "evidence" for r in records.values())

    def test_tampered_check_id_is_refused(self, tmp_path):
        (
            project_root,
            repo,
            _cp,
            slug_dir,
            manifest_path,
            result_path,
        ) = _setup_accepted_manifest(tmp_path)
        text = result_path.read_text(encoding="utf-8")
        tampered = text.replace("check_id: chk-a", "check_id: chk-ghost")
        assert tampered != text
        result_path.write_text(tampered, encoding="utf-8")
        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 0
        assert "no longer matches" in result.skipped[0].reason
        records = ki.load_slug_records(slug_dir)
        assert not any(r.kind == "evidence" for r in records.values())

    def test_tampered_scope_is_refused(self, tmp_path):
        (
            project_root,
            repo,
            _cp,
            slug_dir,
            manifest_path,
            result_path,
        ) = _setup_accepted_manifest(tmp_path)
        text = result_path.read_text(encoding="utf-8")
        tampered = text.replace("scope: scope A", "scope: scope GHOST")
        assert tampered != text
        result_path.write_text(tampered, encoding="utf-8")
        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 0
        records = ki.load_slug_records(slug_dir)
        assert not any(r.kind == "evidence" for r in records.values())

    def test_tampered_test_input_is_refused(self, tmp_path):
        """Editing the test input after persistence changes the live
        `test_input_digest` recomputation -- the cited result no longer
        matches the current fixture/test files, so apply must refuse."""
        project_root, repo, _cp, slug_dir, manifest_path, _rp = _setup_accepted_manifest(tmp_path)
        (repo / "tests" / "test_impl.py").write_text(
            "def test_ok():\n    assert True  # edited after persistence\n", encoding="utf-8",
        )
        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 0
        assert "failed re-validation" in result.skipped[0].reason
        records = ki.load_slug_records(slug_dir)
        assert not any(r.kind == "evidence" for r in records.values())

    def test_missing_repo_root_is_refused_fail_closed(self, tmp_path):
        project_root, repo, _cp, slug_dir, manifest_path, _rp = _setup_accepted_manifest(tmp_path)
        import tomllib
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        data["items"][0]["repo_root"] = str(tmp_path / "does-not-exist")
        manifest_path.write_text(ki._serialize_manifest(data), encoding="utf-8")
        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 0
        assert "fail-closed" in result.skipped[0].reason


# ---------------------------------------------------------------------------
# Phase 89A corrective pass -- defect C: idempotent retry recovery must
# never mistake its own completed write for a concurrent-edit conflict.
# ---------------------------------------------------------------------------


class TestIdempotentRetryRecovery:
    def test_recovers_after_claim_written_but_manifest_state_not_persisted(self, tmp_path):
        """The crash scenario this defect targets: the Claim write
        succeeded but the caller never got to mark the manifest item
        `state="applied"` -- a retry must recognise its own completed
        effect and succeed idempotently, not refuse as a false
        concurrent-edit conflict."""
        project_root, repo, _cp, slug_dir, manifest_path, _rp = _setup_accepted_manifest(tmp_path)
        first = ki.apply_manifest(project_root, manifest_path)
        assert len(first.applied) == 1
        claim_after_first = (slug_dir / "CL-DEMO-001.yaml").read_text(encoding="utf-8")

        import tomllib
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        data["items"][0]["state"] = "pending"  # as if the flag never persisted
        manifest_path.write_text(ki._serialize_manifest(data), encoding="utf-8")

        second = ki.apply_manifest(project_root, manifest_path)
        assert len(second.applied) == 1
        assert "recovered from an interrupted retry" in second.applied[0].reason
        assert (slug_dir / "CL-DEMO-001.yaml").read_text(encoding="utf-8") == claim_after_first

        records = ki.load_slug_records(slug_dir)
        evidence_ids = [r.record_id for r in records.values() if r.kind == "evidence"]
        assert len(evidence_ids) == 1  # no duplicate Evidence
        claim = records["CL-DEMO-001"]
        supporting = ki._extract_id_strings(claim.fields["supporting_evidence"])
        assert supporting == evidence_ids
        assert claim.fields["evidence_support_state"] == "supported"

    def test_evidence_written_claim_not_yet_updated_resumes_normally(self, tmp_path):
        """A crash between the Evidence write and the Claim write: the
        next attempt must reuse the already-written Evidence (never a
        duplicate) and still go on to update the Claim -- this is NOT
        the idempotent-recovery short-circuit (the Claim itself is
        still untouched, so base_claim_hash still matches)."""
        (
            project_root,
            repo,
            _cp,
            slug_dir,
            manifest_path,
            result_path,
        ) = _setup_accepted_manifest(tmp_path)
        reparsed = oracle.parse_oracle_result(result_path)

        # Simulate the exact on-disk state a crash right after the
        # Evidence write (but before the Claim write) would leave.
        pre_ev_id = "EV-X-900"
        _write_flat(slug_dir / f"{pre_ev_id}.yaml", {
            "id": pre_ev_id, "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_path.relative_to(project_root)}"',
        })
        assert ki._find_existing_evidence_for_run(
            project_root, ki.load_slug_records(slug_dir),
            reparsed.contract_id, reparsed.check_id, reparsed.run_id,
        ) == pre_ev_id

        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 1
        records = ki.load_slug_records(slug_dir)
        evidence_ids = [r.record_id for r in records.values() if r.kind == "evidence"]
        assert evidence_ids == [pre_ev_id]  # reused, never duplicated
        claim = records["CL-DEMO-001"]
        assert pre_ev_id in claim.fields["supporting_evidence"]
        assert claim.fields["evidence_support_state"] == "supported"

    def test_genuine_concurrent_claim_edit_is_still_refused_after_recovery_fix(self, tmp_path):
        """The idempotent-recovery pre-check must never be tricked by a
        real, unrelated human edit to the Claim's own statement field
        -- it is not "this item's own effect already present" just
        because the Claim happens to differ from base_claim_hash."""
        project_root, repo, _cp, slug_dir, manifest_path, _rp = _setup_accepted_manifest(tmp_path)
        claim_path = slug_dir / "CL-DEMO-001.yaml"
        claim_path.write_text(
            claim_path.read_text(encoding="utf-8") + "\nstatement: hand-edited\n", encoding="utf-8",
        )
        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 0
        assert "race" in result.skipped[0].reason
        records = ki.load_slug_records(slug_dir)
        assert not any(r.kind == "evidence" for r in records.values())

    def test_cli_apply_retry_is_idempotent_for_baseline_advancement(self, tmp_path, monkeypatch):
        """Defect C, scenario 4: re-running `knowledge apply` against an
        already-applied manifest must still (re-)advance the baseline
        for every file it touched -- recovering from a crash between
        `apply_manifest` returning and baseline advancement completing,
        without ever duplicating Evidence or re-mutating the Claim."""
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        contract_path, slug_dir = _setup_slug(project_root, "demo", checks=[_default_check()])
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {
            "id": "CL-DEMO-001", "kind": "claim",
            "supporting_evidence": ["EV-SRC-1", "EV-TEST-1"], "contradicting_evidence": [],
            "evidence_support_state": "partially_supported",
        })
        _write_flat(slug_dir / "EV-SRC-1.yaml", {
            "id": "EV-SRC-1", "kind": "evidence", "evidence_kind": "source",
            "source_ref": '"impl.py:5 def target_function"',
        })
        _write_flat(slug_dir / "REQ-DEMO-001.yaml", {
            "id": "REQ-DEMO-001", "kind": "requirement",
            "depends_on": ["CL-DEMO-001"], "check_id": "chk-a",
        })
        result_path = (
            project_root / "planning" / "contracts" / "demo" / "results" / "chk-a--r1.yaml"
        )
        _write_fake_result(result_path, contract_path, check_id="chk-a", repo_root=repo)
        _write_flat(slug_dir / "EV-TEST-1.yaml", {
            "id": "EV-TEST-1", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_path.relative_to(project_root)}"',
        })
        sr.establish_source_baseline(
            project_root, "demo", "tests/test_impl.py",
            oracle.sha256_file(repo / "tests" / "test_impl.py"),
        )
        (repo / "tests" / "test_impl.py").write_text(
            "def test_ok():\n    assert True  # changed\n", encoding="utf-8",
        )
        monkeypatch.chdir(project_root)
        res = runner.invoke(
            cli.app, ["knowledge", "verify-changes", "demo", "--repo-root", str(repo)]
        )
        assert res.exit_code == 0
        reconciliation_dir = project_root / "planning" / "knowledge" / "demo" / "reconciliation"
        manifest_path = next(reconciliation_dir.glob("*-source.toml"))
        import tomllib
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        data["items"][0]["decision"] = "accept"
        manifest_path.write_text(ki._serialize_manifest(data), encoding="utf-8")

        res1 = runner.invoke(cli.app, ["knowledge", "apply", str(manifest_path)])
        assert res1.exit_code == 0
        new_hash = oracle.sha256_file(repo / "tests" / "test_impl.py")
        baseline = sr._read_baseline(project_root, "demo")
        assert baseline["tests/test_impl.py"]["content_hash"] == new_hash

        # Retry the exact same command against the now-fully-applied
        # manifest -- must remain idempotent (no duplicate Evidence, no
        # error) and keep the baseline exactly where it correctly is.
        res2 = runner.invoke(cli.app, ["knowledge", "apply", str(manifest_path)])
        assert res2.exit_code == 0
        records = ki.load_slug_records(slug_dir)
        evidence_ids = [r.record_id for r in records.values() if r.kind == "evidence"]
        assert len(evidence_ids) == len(set(evidence_ids))
        baseline_after_retry = sr._read_baseline(project_root, "demo")
        assert baseline_after_retry["tests/test_impl.py"]["content_hash"] == new_hash


# ---------------------------------------------------------------------------
# Phase 89A corrective pass (second round) -- defect A: a whole-contract
# (aggregate/dependent) or ambiguously-scoped Claim must never be
# automatically mutated by the single-check Evidence-update/support-
# state-recomputation path, even though it is genuinely *affected* by
# the same check's drift that a sibling, genuinely single-check Claim
# is correctly reconciled against. Mirrors the real Ledgerkit shape
# (CL-BFS-001/002 single-check, CL-BFS-003 superseded,
# CL-BFS-005 aggregate via `depends_on`) with a synthetic, generic
# fixture that also exercises the "ambiguous mapping" case the real
# records never construct.
# ---------------------------------------------------------------------------


class TestWholeContractClaimScopeProtection:
    def _setup(self, tmp_path):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path, test_text=_TEST_TEXT_TWO)
        checks = [
            _default_check(check_id="chk-a", scope="scope A",
                            check_reference="tests/test_impl.py::test_ok"),
            _default_check(check_id="chk-b", scope="scope B",
                            check_reference="tests/test_impl.py::test_ok_2"),
        ]
        contract_path, slug_dir = _setup_slug(project_root, "demo", checks=checks)
        results_dir = project_root / "planning" / "contracts" / "demo" / "results"
        result_a = results_dir / "chk-a--r1.yaml"
        result_b = results_dir / "chk-b--r1.yaml"
        _write_fake_result(
            result_a, contract_path, check_id="chk-a", scope="scope A", repo_root=repo
        )
        _write_fake_result(
            result_b, contract_path, check_id="chk-b", scope="scope B", repo_root=repo
        )
        _write_flat(slug_dir / "EV-TEST-001.yaml", {
            "id": "EV-TEST-001", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_a.relative_to(project_root)}"',
        })
        _write_flat(slug_dir / "EV-TEST-002.yaml", {
            "id": "EV-TEST-002", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_b.relative_to(project_root)}"',
        })
        # Genuinely single-check Claims (CL-BFS-001/002's own real shape):
        # no depends_on, bridged from exactly one check each.
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {
            "id": "CL-DEMO-001", "kind": "claim",
            "supporting_evidence": ["EV-TEST-001"], "contradicting_evidence": [],
            "evidence_support_state": "partially_supported",
        })
        _write_flat(slug_dir / "CL-DEMO-002.yaml", {
            "id": "CL-DEMO-002", "kind": "claim",
            "supporting_evidence": ["EV-TEST-002"], "contradicting_evidence": [],
            "evidence_support_state": "partially_supported",
        })
        # Aggregate Claim (CL-BFS-005's own real shape): depends_on
        # names the two single-check Claims above, and also happens to
        # cite both checks' own bridging Evidence directly.
        _write_flat(slug_dir / "CL-DEMO-AGG.yaml", {
            "id": "CL-DEMO-AGG", "kind": "claim",
            "supporting_evidence": ["EV-TEST-001", "EV-TEST-002"], "contradicting_evidence": [],
            "evidence_support_state": "partially_supported",
            "depends_on": ["CL-DEMO-001", "CL-DEMO-002"],
        })
        # Superseded Claim (CL-BFS-003's own real shape): bridged from
        # chk-a's own Evidence, but historical -- never touched.
        _write_flat(slug_dir / "CL-DEMO-SUPERSEDED.yaml", {
            "id": "CL-DEMO-SUPERSEDED", "kind": "claim",
            "supporting_evidence": ["EV-TEST-001"], "contradicting_evidence": [],
            "evidence_support_state": "supported", "status": "superseded",
        })
        # Ambiguous Claim: no depends_on of its own, but cites BOTH
        # checks' own bridging Evidence directly -- nothing structural
        # says this Claim is scoped to one check in particular.
        _write_flat(slug_dir / "CL-DEMO-AMBIGUOUS.yaml", {
            "id": "CL-DEMO-AMBIGUOUS", "kind": "claim",
            "supporting_evidence": ["EV-TEST-001", "EV-TEST-002"], "contradicting_evidence": [],
            "evidence_support_state": "partially_supported",
        })
        original_hash = oracle.sha256_file(repo / "tests" / "test_impl.py")
        sr.establish_source_baseline(project_root, "demo", "tests/test_impl.py", original_hash)
        graph_db = _sync_graph(repo)
        (repo / "tests" / "test_impl.py").write_text(
            _TEST_TEXT_TWO + "\n# edit\n", encoding="utf-8"
        )
        graph_db = _sync_graph(repo)
        return project_root, repo, contract_path, slug_dir, graph_db, original_hash

    def _propose(self, project_root, repo, graph_db):
        source_result = sr.detect_source_changes(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db
        )
        return sr.propose_reconciliation(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db,
            source_changes=source_result,
        )

    def test_aggregate_claim_citing_two_checks_is_affected_not_mutated(self, tmp_path):
        project_root, repo, _cp, slug_dir, graph_db, _oh = self._setup(tmp_path)
        proposal = self._propose(project_root, repo, graph_db)
        assert {f.claim_id for f in proposal.findings} == {"CL-DEMO-001", "CL-DEMO-002"}
        agg_affected = [a for a in proposal.affected_claims if a.claim_id == "CL-DEMO-AGG"]
        assert {a.check_id for a in agg_affected} == {"chk-a", "chk-b"}
        assert all(a.category == "aggregate" for a in agg_affected)
        manifest_path = sr.write_source_reconciliation_manifest(
            project_root, "demo", proposal.findings, repo_root=repo, target_graph_db=graph_db,
            baseline_eligible_test_input_paths=proposal.baseline_eligible_test_input_paths,
            affected_claims=proposal.affected_claims,
        )
        import tomllib
        before_hash = ki.sha256_text(
            (slug_dir / "CL-DEMO-AGG.yaml").read_text(encoding="utf-8")
        )
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        assert {item["record_id"] for item in data["items"]} == {"CL-DEMO-001", "CL-DEMO-002"}
        for item in data["items"]:
            item["decision"] = "accept"
        manifest_path.write_text(ki._serialize_manifest(data), encoding="utf-8")
        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 2
        after_hash = ki.sha256_text(
            (slug_dir / "CL-DEMO-AGG.yaml").read_text(encoding="utf-8")
        )
        assert before_hash == after_hash  # never mutated, byte-identical

    def test_superseded_claim_is_never_touched_or_reported(self, tmp_path):
        project_root, repo, _cp, slug_dir, graph_db, _oh = self._setup(tmp_path)
        proposal = self._propose(project_root, repo, graph_db)
        assert not any(f.claim_id == "CL-DEMO-SUPERSEDED" for f in proposal.findings)
        assert not any(
            a.claim_id == "CL-DEMO-SUPERSEDED" for a in proposal.affected_claims
        )
        before_hash = ki.sha256_text(
            (slug_dir / "CL-DEMO-SUPERSEDED.yaml").read_text(encoding="utf-8")
        )
        manifest_path = sr.write_source_reconciliation_manifest(
            project_root, "demo", proposal.findings, repo_root=repo, target_graph_db=graph_db,
            baseline_eligible_test_input_paths=proposal.baseline_eligible_test_input_paths,
            affected_claims=proposal.affected_claims,
        )
        import tomllib
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        for item in data["items"]:
            item["decision"] = "accept"
        manifest_path.write_text(ki._serialize_manifest(data), encoding="utf-8")
        ki.apply_manifest(project_root, manifest_path)
        after_hash = ki.sha256_text(
            (slug_dir / "CL-DEMO-SUPERSEDED.yaml").read_text(encoding="utf-8")
        )
        assert before_hash == after_hash

    def test_ambiguous_claim_mapping_fails_closed(self, tmp_path):
        project_root, repo, _cp, _sd, graph_db, _oh = self._setup(tmp_path)
        proposal = self._propose(project_root, repo, graph_db)
        assert not any(f.claim_id == "CL-DEMO-AMBIGUOUS" for f in proposal.findings)
        ambiguous = [a for a in proposal.affected_claims if a.claim_id == "CL-DEMO-AMBIGUOUS"]
        assert {a.check_id for a in ambiguous} == {"chk-a", "chk-b"}
        assert all(a.category == "ambiguous" for a in ambiguous)

    def test_genuinely_single_check_claim_is_eligible_and_mutated(self, tmp_path):
        project_root, repo, _cp, slug_dir, graph_db, _oh = self._setup(tmp_path)
        proposal = self._propose(project_root, repo, graph_db)
        manifest_path = sr.write_source_reconciliation_manifest(
            project_root, "demo", proposal.findings, repo_root=repo, target_graph_db=graph_db,
            baseline_eligible_test_input_paths=proposal.baseline_eligible_test_input_paths,
            affected_claims=proposal.affected_claims,
        )
        import tomllib
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        for item in data["items"]:
            item["decision"] = "accept"
        manifest_path.write_text(ki._serialize_manifest(data), encoding="utf-8")
        ki.apply_manifest(project_root, manifest_path)
        records = ki.load_slug_records(slug_dir)
        assert records["CL-DEMO-001"].fields["evidence_support_state"] == "supported"
        assert records["CL-DEMO-002"].fields["evidence_support_state"] == "supported"

    def test_apply_refuses_hand_crafted_manifest_item_against_aggregate_claim(self, tmp_path):
        """Defensive fail-closed backstop: even a manifest item that
        never went through `propose_reconciliation`'s own gate (e.g.
        hand-edited, or produced by a future/third-party writer) is
        refused by `_apply_source_reconciliation` itself."""
        project_root, repo, _cp, slug_dir, graph_db, _oh = self._setup(tmp_path)
        before_hash = ki.sha256_text(
            (slug_dir / "CL-DEMO-AGG.yaml").read_text(encoding="utf-8")
        )
        claim_text = (slug_dir / "CL-DEMO-AGG.yaml").read_text(encoding="utf-8")
        data = {
            "manifest_id": "demo@hand-crafted", "created": "2026-11-18T00:00:00Z",
            "slug": "demo",
            "items": [{
                "kind": "source_reconciliation",
                "record_id": "CL-DEMO-AGG",
                "base_claim_hash": ki.sha256_text(claim_text),
                "repo_root": str(repo),
                "contributing_source_paths": [],
                "contributing_source_hashes": [],
                "contributing_contract_ids": ["REQ-X-001"],
                "contributing_check_ids": ["chk-a"],
                "contributing_run_ids": ["r1"],
                "contributing_raw_output_refs": [""],
                "contributing_labels": ["re_confirmed"],
                "contributing_target_fields": ["supporting_evidence"],
                "contributing_what_it_shows": ["hand-crafted"],
                "contributing_repository_revisions": ["unknown"],
                "state": "pending", "decision": "accept",
            }],
        }
        manifest_path = (
            project_root / "planning" / "knowledge" / "demo" / "reconciliation"
            / "hand-crafted.toml"
        )
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(ki._serialize_manifest(data), encoding="utf-8")
        result = ki.apply_manifest(project_root, manifest_path)
        assert len(result.applied) == 0
        assert len(result.skipped) == 1
        assert "never automatically mutated" in result.skipped[0].reason
        after_hash = ki.sha256_text(
            (slug_dir / "CL-DEMO-AGG.yaml").read_text(encoding="utf-8")
        )
        assert before_hash == after_hash

    def test_shared_baseline_advances_despite_excluded_aggregate_claim(self, tmp_path):
        """Baseline eligibility is decided per-CHECK (`required_by_path`/
        `accounted_by_path`), never per-Claim -- excluding the aggregate
        Claim from mutation must not block the shared file's baseline
        from advancing once both checks sharing it are genuinely,
        validly accounted for."""
        project_root, repo, _cp, _sd, graph_db, original_hash = self._setup(tmp_path)
        proposal = self._propose(project_root, repo, graph_db)
        assert "tests/test_impl.py" in proposal.baseline_eligible_test_input_paths
        manifest_path = sr.write_source_reconciliation_manifest(
            project_root, "demo", proposal.findings, repo_root=repo, target_graph_db=graph_db,
            baseline_eligible_test_input_paths=proposal.baseline_eligible_test_input_paths,
            affected_claims=proposal.affected_claims,
        )
        import tomllib
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        for item in data["items"]:
            item["decision"] = "accept"
        manifest_path.write_text(ki._serialize_manifest(data), encoding="utf-8")
        ki.apply_manifest(project_root, manifest_path)
        data_after = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        for item in data_after["items"]:
            if item.get("kind") == "source_reconciliation" and item.get("state") == "applied":
                sr.advance_baselines_for_applied_item(
                    project_root, "demo", item, manifest_items=data_after["items"],
                )
        baseline = sr._read_baseline(project_root, "demo")
        new_hash = oracle.sha256_file(repo / "tests" / "test_impl.py")
        assert new_hash != original_hash
        assert baseline["tests/test_impl.py"]["content_hash"] == new_hash

    def test_affected_claims_survive_apply_manifest_rewrite(self, tmp_path):
        project_root, repo, _cp, _sd, graph_db, _oh = self._setup(tmp_path)
        proposal = self._propose(project_root, repo, graph_db)
        manifest_path = sr.write_source_reconciliation_manifest(
            project_root, "demo", proposal.findings, repo_root=repo, target_graph_db=graph_db,
            baseline_eligible_test_input_paths=proposal.baseline_eligible_test_input_paths,
            affected_claims=proposal.affected_claims,
        )
        import tomllib
        before = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        assert len(before["affected_claims"]) == 4  # CL-DEMO-AGG x2 + CL-DEMO-AMBIGUOUS x2
        for item in before["items"]:
            item["decision"] = "accept"
        manifest_path.write_text(ki._serialize_manifest(before), encoding="utf-8")
        ki.apply_manifest(project_root, manifest_path)  # rewrites the manifest in place
        after = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        assert after["affected_claims"] == before["affected_claims"]


# ---------------------------------------------------------------------------
# Phase 89A corrective pass (second round) -- defect A unit coverage of
# `claim_scope_category` itself, independent of the full detection/
# proposal pipeline above.
# ---------------------------------------------------------------------------


class TestClaimScopeCategory:
    def _claim(self, tmp_path, fields):
        path = tmp_path / "CL-X-001.yaml"
        _write_flat(path, {"id": "CL-X-001", "kind": "claim", **fields})
        return ki.load_slug_records(tmp_path)["CL-X-001"]

    def test_superseded_takes_priority_over_everything_else(self, tmp_path):
        claim = self._claim(tmp_path, {
            "status": "superseded", "depends_on": ["CL-X-002", "CL-X-003"],
        })
        category, reason = ki.claim_scope_category(claim, bridging_check_ids={"a", "b"})
        assert category == "superseded"
        assert "CL-X-001" in reason

    def test_depends_on_naming_one_claim_is_aggregate(self, tmp_path):
        claim = self._claim(tmp_path, {"depends_on": ["CL-X-002"]})
        category, reason = ki.claim_scope_category(claim)
        assert category == "aggregate"
        assert "CL-X-002" in reason

    def test_depends_on_naming_two_claims_is_aggregate(self, tmp_path):
        claim = self._claim(tmp_path, {"depends_on": ["CL-X-002", "CL-X-003"]})
        category, _reason = ki.claim_scope_category(claim, bridging_check_ids={"a", "b"})
        assert category == "aggregate"  # depends_on checked before the ambiguous test

    def test_multi_check_bridging_with_no_depends_on_is_ambiguous(self, tmp_path):
        claim = self._claim(tmp_path, {})
        category, reason = ki.claim_scope_category(claim, bridging_check_ids={"chk-a", "chk-b"})
        assert category == "ambiguous"
        assert "chk-a" in reason and "chk-b" in reason

    def test_single_check_bridging_is_eligible(self, tmp_path):
        claim = self._claim(tmp_path, {})
        category, reason = ki.claim_scope_category(claim, bridging_check_ids={"chk-a"})
        assert category == "eligible"
        assert reason == ""

    def test_no_depends_on_and_bridging_not_evaluated_is_eligible(self, tmp_path):
        """Detector (b) never passes `bridging_check_ids` at all -- its
        own single-check-to-single-Claim resolution is already
        fail-closed via a different mechanism (the Requirement's own
        `depends_on`-length guard)."""
        claim = self._claim(tmp_path, {})
        category, reason = ki.claim_scope_category(claim)
        assert category == "eligible"
        assert reason == ""


# ---------------------------------------------------------------------------
# Phase 89A corrective pass (second round) -- defect B: manifest
# filename collision. `write_source_reconciliation_manifest`'s own
# one-second-precision timestamp filename must never let a second
# verification run overwrite an earlier, still-pending manifest.
# ---------------------------------------------------------------------------


def _frozen_datetime(moment):
    from datetime import datetime as _real_datetime

    class _Frozen(_real_datetime):
        @classmethod
        def now(cls, tz=None):
            return moment if tz is None else moment.astimezone(tz)

    return _Frozen


class TestManifestCollisionResistance:
    def _setup(self, tmp_path):
        project_root = tmp_path / "knowledge-root"
        repo = _build_repo(tmp_path)
        contract_path, slug_dir = _setup_slug(project_root, "demo", checks=[_default_check()])
        _write_flat(slug_dir / "CL-DEMO-001.yaml", {
            "id": "CL-DEMO-001", "kind": "claim",
            "supporting_evidence": [], "contradicting_evidence": [],
            "evidence_support_state": "unsupported",
        })
        _write_flat(slug_dir / "CL-DEMO-002.yaml", {
            "id": "CL-DEMO-002", "kind": "claim",
            "supporting_evidence": [], "contradicting_evidence": [],
            "evidence_support_state": "unsupported",
        })
        result_path = (
            project_root / "planning" / "contracts" / "demo" / "results" / "chk-a--r1.yaml"
        )
        _write_fake_result(result_path, contract_path, check_id="chk-a", repo_root=repo)
        rel = result_path.relative_to(project_root)
        finding1 = sr.ContributingFinding(
            claim_id="CL-DEMO-001", contract_id="REQ-X-001", check_id="chk-a", run_id="r1",
            raw_output_ref=f"{rel}", label="newly_covered", target_field="supporting_evidence",
            what_it_shows="first", repository_revision="unknown",
        )
        finding2 = sr.ContributingFinding(
            claim_id="CL-DEMO-002", contract_id="REQ-X-001", check_id="chk-a", run_id="r1",
            raw_output_ref=f"{rel}", label="newly_covered", target_field="supporting_evidence",
            what_it_shows="second", repository_revision="unknown",
        )
        return project_root, repo, slug_dir, finding1, finding2

    def test_two_manifests_in_the_same_frozen_second_do_not_collide(self, tmp_path, monkeypatch):
        from datetime import UTC, datetime
        project_root, repo, _sd, finding1, finding2 = self._setup(tmp_path)
        moment = datetime(2026, 11, 18, 12, 0, 0, tzinfo=UTC)
        monkeypatch.setattr(sr, "datetime", _frozen_datetime(moment))
        path1 = sr.write_source_reconciliation_manifest(
            project_root, "demo", [finding1], repo_root=repo,
        )
        path2 = sr.write_source_reconciliation_manifest(
            project_root, "demo", [finding2], repo_root=repo,
        )
        assert path1 != path2
        assert path1.is_file() and path2.is_file()
        import tomllib
        data1 = tomllib.loads(path1.read_text(encoding="utf-8"))
        data2 = tomllib.loads(path2.read_text(encoding="utf-8"))
        assert data1["manifest_id"] != data2["manifest_id"]
        assert data1["items"][0]["record_id"] == "CL-DEMO-001"
        assert data2["items"][0]["record_id"] == "CL-DEMO-002"

    def test_existing_review_decision_survives_a_colliding_second_write(
        self, tmp_path, monkeypatch,
    ):
        from datetime import UTC, datetime
        project_root, repo, _sd, finding1, finding2 = self._setup(tmp_path)
        moment = datetime(2026, 11, 18, 12, 0, 0, tzinfo=UTC)
        monkeypatch.setattr(sr, "datetime", _frozen_datetime(moment))
        path1 = sr.write_source_reconciliation_manifest(
            project_root, "demo", [finding1], repo_root=repo,
        )
        import tomllib
        data1 = tomllib.loads(path1.read_text(encoding="utf-8"))
        data1["items"][0]["decision"] = "accept"
        path1.write_text(ki._serialize_manifest(data1), encoding="utf-8")
        before_text = path1.read_text(encoding="utf-8")
        path2 = sr.write_source_reconciliation_manifest(
            project_root, "demo", [finding2], repo_root=repo,
        )
        assert path1.read_text(encoding="utf-8") == before_text  # never touched
        assert path2 != path1
        data1_after = tomllib.loads(path1.read_text(encoding="utf-8"))
        assert data1_after["items"][0]["decision"] == "accept"

    def test_both_colliding_manifests_apply_correctly_and_idempotently(
        self, tmp_path, monkeypatch,
    ):
        from datetime import UTC, datetime
        project_root, repo, slug_dir, finding1, finding2 = self._setup(tmp_path)
        moment = datetime(2026, 11, 18, 12, 0, 0, tzinfo=UTC)
        monkeypatch.setattr(sr, "datetime", _frozen_datetime(moment))
        path1 = sr.write_source_reconciliation_manifest(
            project_root, "demo", [finding1], repo_root=repo,
        )
        path2 = sr.write_source_reconciliation_manifest(
            project_root, "demo", [finding2], repo_root=repo,
        )
        import tomllib
        for path in (path1, path2):
            data = tomllib.loads(path.read_text(encoding="utf-8"))
            data["items"][0]["decision"] = "accept"
            path.write_text(ki._serialize_manifest(data), encoding="utf-8")
        result1 = ki.apply_manifest(project_root, path1)
        result2 = ki.apply_manifest(project_root, path2)
        assert len(result1.applied) == 1
        assert len(result2.applied) == 1
        records = ki.load_slug_records(slug_dir)
        # Both manifests cited the SAME real OracleResult identity
        # (contract_id, check_id, run_id) -- never duplicate Evidence
        # merely because two distinct manifests reference it.
        evidence_ids = [r.record_id for r in records.values() if r.kind == "evidence"]
        assert len(evidence_ids) == 1
        assert records["CL-DEMO-001"].fields["supporting_evidence"] == records[
            "CL-DEMO-002"
        ].fields["supporting_evidence"]
        # Retrying both is still idempotent -- no new Evidence, no error
        # (each manifest's own item is already `state == "applied"`, so
        # `apply_manifest`'s own generic loop short-circuits it as a
        # harmless skip, never re-dispatching to `_apply_source_
        # reconciliation` at all).
        result1_retry = ki.apply_manifest(project_root, path1)
        result2_retry = ki.apply_manifest(project_root, path2)
        assert len(result1_retry.applied) == 0
        assert len(result2_retry.applied) == 0
        assert result1_retry.skipped[0].reason == "already applied (state=applied)"
        assert result2_retry.skipped[0].reason == "already applied (state=applied)"
        records_after_retry = ki.load_slug_records(slug_dir)
        evidence_ids_after_retry = [
            r.record_id for r in records_after_retry.values() if r.kind == "evidence"
        ]
        assert len(evidence_ids_after_retry) == 1

    def test_interrupted_creation_never_leaves_a_valid_partial_manifest(
        self, tmp_path, monkeypatch,
    ):
        """A failure between the temp-file write and the atomic link
        (simulating an interruption) must never leave a readable,
        half-written file at a real manifest path."""
        dir_path = tmp_path / "reconciliation"
        real_link = os.link

        def _boom(src, dst):
            raise OSError("simulated interruption")

        monkeypatch.setattr(os, "link", _boom)
        with pytest.raises(OSError):
            ki._write_manifest_exclusive(dir_path, "20261118T120000Z-source", lambda stem: "x")
        monkeypatch.setattr(os, "link", real_link)
        assert not (dir_path / "20261118T120000Z-source.toml").exists()
        assert list(dir_path.glob("*.tmp-*")) == []  # cleaned up, nothing orphaned

    def test_collision_retry_regenerates_content_for_the_new_stem(self, tmp_path):
        """`render` is called fresh per attempt so a disambiguated
        filename's own embedded `manifest_id` always matches it --
        never a stale value computed for the first, collided stem."""
        dir_path = tmp_path / "reconciliation"
        dir_path.mkdir()
        (dir_path / "20261118T120000Z-source.toml").write_text("existing", encoding="utf-8")
        seen_stems = []

        def _render(stem):
            seen_stems.append(stem)
            return f"manifest_id = \"demo@{stem}\"\n"

        result_path = ki._write_manifest_exclusive(
            dir_path, "20261118T120000Z-source", _render,
        )
        assert result_path != dir_path / "20261118T120000Z-source.toml"
        expected_text = f'manifest_id = "demo@{result_path.stem}"\n'
        assert result_path.read_text(encoding="utf-8") == expected_text
        assert len(seen_stems) == 2  # one collided attempt, one that succeeded
        # The pre-existing file must be completely untouched.
        assert (dir_path / "20261118T120000Z-source.toml").read_text(encoding="utf-8") == "existing"
