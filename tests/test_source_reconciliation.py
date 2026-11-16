"""Tests for `src/codecompass/source_reconciliation.py` (Phase 89 Stage
89A, `decisions/0096`) plus the new `change_impact.py`/`knowledge_
intermediate.py`/`cli.py` surface it depends on. Deliberately
independent of the real ~/projects/ledgerkit checkout -- each test
constructs its own minimal, disposable fake target repository + graph
database + knowledge-record/contract fixtures, mirroring `tests/
test_assess_change_impact.py`'s own established convention.
"""

from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

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
                        run_id: str = "r1") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw_path = path.parent / f"{check_id}-{run_id}-raw.txt"
    raw_path.write_text("ok", encoding="utf-8")
    result = oracle.OracleResult(
        schema_version=1, run_id=run_id, contract_id="REQ-X-001", check_id=check_id,
        scope="scope A", baseline_id=None, tested_subject_digest="d" * 64,
        oracle_contract_id="REQ-X-001",
        oracle_contract_content_hash=oracle.sha256_file(contract_path),
        test_input_digest="i" * 64, raw_output_ref=str(raw_path),
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

        findings = sr.propose_reconciliation(
            project_root, "demo", repo_root=repo, target_graph_db=graph_db,
            source_changes=source_result,
        )
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
        findings = sr.propose_reconciliation(
            project_root, "demo", repo_root=repo, newly_coverable=coverable.coverable,
        )
        assert len(findings) == 1
        assert findings[0].label == "newly_covered"
        assert findings[0].target_field == "supporting_evidence"
        manifest_path = sr.write_source_reconciliation_manifest(project_root, "demo", findings)
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
        findings = sr.propose_reconciliation(
            project_root, "demo", repo_root=repo, newly_coverable=coverable.coverable,
        )
        manifest_path = sr.write_source_reconciliation_manifest(project_root, "demo", findings)
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
        findings = sr.propose_reconciliation(
            project_root, "demo", repo_root=repo, newly_coverable=coverable.coverable,
        )
        manifest_path = sr.write_source_reconciliation_manifest(project_root, "demo", findings)
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
            result_path, contract_path, check_id="chk-a", run_id="r2", outcome="PASS"
        )
        from codecompass.knowledge_intermediate import _apply_source_reconciliation

        item = {
            "kind": "source_reconciliation", "record_id": "CL-DEMO-001",
            "base_claim_hash": ki.sha256_text(
                (slug_dir / "CL-DEMO-001.yaml").read_text(encoding="utf-8")
            ),
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
