"""Tests for scripts/assess_change_impact.py (Phase 83 -- Semantic Change
Assurance). A maintainer-only tool, not part of the codecompass package --
imported directly from its file path, same convention as
tests/test_check_contracts.py. See planning/phase-83-semantic-change-
assurance.md and decisions/0086/0087/0089 for the full design.

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
# resolve_intersecting_symbols / compute_symbol_spans -- pure functions, no DB
# (decisions/0089 §B: replaces the single-result resolve_enclosing_symbol)
# ---------------------------------------------------------------------------


class TestComputeSymbolSpans:
    def test_each_span_runs_to_one_less_than_the_next_symbols_line(self):
        symbols = [
            aci.SymbolRow("foo", "function", 1),
            aci.SymbolRow("bar", "function", 10),
            aci.SymbolRow("baz", "function", 20),
        ]
        spans = aci.compute_symbol_spans(symbols, line_count=25)
        assert [(s.symbol.name, s.span_start, s.span_end) for s in spans] == [
            ("foo", 1, 9), ("bar", 10, 19), ("baz", 20, 25),
        ]

    def test_empty_symbol_list(self):
        assert aci.compute_symbol_spans([], line_count=10) == []


class TestResolveIntersectingSymbols:
    def test_single_point_resolves_to_enclosing_symbol_only(self):
        symbols = [
            aci.SymbolRow("foo", "function", 1),
            aci.SymbolRow("bar", "function", 10),
            aci.SymbolRow("baz", "function", 20),
        ]
        matched = aci.resolve_intersecting_symbols(symbols, line_count=25, start=15, end=15)
        assert [s.symbol.name for s in matched] == ["bar"]

    def test_range_crossing_two_symbols_resolves_both(self):
        symbols = [
            aci.SymbolRow("foo", "function", 1),
            aci.SymbolRow("bar", "function", 10),
            aci.SymbolRow("baz", "function", 20),
        ]
        matched = aci.resolve_intersecting_symbols(symbols, line_count=25, start=8, end=12)
        assert [s.symbol.name for s in matched] == ["foo", "bar"]

    def test_range_before_first_symbol_resolves_to_nothing(self):
        symbols = [aci.SymbolRow("foo", "function", 5)]
        assert aci.resolve_intersecting_symbols(symbols, line_count=10, start=1, end=2) == []

    def test_empty_symbol_list_resolves_to_nothing(self):
        assert aci.resolve_intersecting_symbols([], line_count=10, start=1, end=1) == []


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

# A third fixture with a top-of-file region (an import) before any
# top-level symbol -- used to exercise `partially_resolved` (decisions/
# 0089 §B): a range starting in that region is not fully covered by any
# indexed symbol's own span.
_IMPL_WITH_PREAMBLE_TEXT = (
    "import os\n"           # 1
    "\n"                     # 2
    "\n"                     # 3
    "def helper():\n"        # 4
    "    return os\n"        # 5
    "\n"                     # 6
    "\n"                     # 7
    "def target_function():\n"  # 8
    "    return 2\n"         # 9
)


def _build_fake_target_repo(tmp_path: Path, *, text: str = _IMPL_TEXT) -> Path:
    repo = tmp_path / "target-repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "impl.py").write_text(text, encoding="utf-8")
    return repo


def _sync_graph_for(repo: Path, *, symbols: list[tuple[str, str, int]] | None = None) -> Path:
    graph_db = repo / "context-graph.db"
    content_hash = oracle.sha256_file(repo / "impl.py")
    _write_graph_db(
        graph_db, path="impl.py", content_hash=content_hash,
        symbols=symbols or [("helper", "function", 1), ("target_function", "function", 5)],
    )
    return graph_db


# ---------------------------------------------------------------------------
# resolve_changed_range -- §5 revision consistency + §B multi-symbol/EOF
# ---------------------------------------------------------------------------


class TestResolveChangedRange:
    def test_resolved_when_hash_matches(self, tmp_path):
        repo = _build_fake_target_repo(tmp_path)
        graph_db = _sync_graph_for(repo)
        res = aci.resolve_changed_range(oracle, repo, graph_db, aci.ChangedRange("impl.py", 5, 6))
        assert res.status == "resolved"
        assert [s.name for s in res.symbols] == ["target_function"]

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

    def test_cannot_map_start_past_file_extent(self, tmp_path):
        repo = _build_fake_target_repo(tmp_path)
        graph_db = _sync_graph_for(repo)
        res = aci.resolve_changed_range(oracle, repo, graph_db, aci.ChangedRange("impl.py", 9999, 9999))
        assert res.status == "cannot_map"
        assert "own extent" in res.reason

    def test_cannot_map_end_past_file_extent(self, tmp_path):
        """decisions/0089 §B: previously only `start` was validated against
        the file's own extent -- a `start` within range but an `end` far
        past it (6 lines total) must also be rejected, not silently
        resolved as if `end` had never been consulted."""
        repo = _build_fake_target_repo(tmp_path)
        graph_db = _sync_graph_for(repo)
        res = aci.resolve_changed_range(oracle, repo, graph_db, aci.ChangedRange("impl.py", 5, 99999))
        assert res.status == "cannot_map"
        assert "end=99999" in res.reason
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

    def test_range_crossing_multiple_functions_resolves_all(self, tmp_path):
        """decisions/0089 §B: a range spanning two top-level declarations
        must resolve BOTH, not only the one enclosing the range's start."""
        repo = _build_fake_target_repo(tmp_path)
        graph_db = _sync_graph_for(repo)
        res = aci.resolve_changed_range(oracle, repo, graph_db, aci.ChangedRange("impl.py", 1, 6))
        assert res.status == "resolved"
        assert sorted(s.name for s in res.symbols) == ["helper", "target_function"]

    def test_file_level_change_resolves_every_symbol(self, tmp_path):
        repo = _build_fake_target_repo(tmp_path)
        graph_db = _sync_graph_for(repo)
        line_count = len(_IMPL_TEXT.splitlines())
        res = aci.resolve_changed_range(oracle, repo, graph_db, aci.ChangedRange("impl.py", 1, line_count))
        assert res.status == "resolved"
        assert sorted(s.name for s in res.symbols) == ["helper", "target_function"]

    def test_partially_resolved_when_range_extends_before_first_symbol(self, tmp_path):
        """decisions/0089 §B: a range starting in a module's top-of-file
        region (before any indexed top-level symbol) but extending into a
        real symbol's span must still assess that symbol, while explicitly
        naming the unmapped lines rather than silently dropping them."""
        repo = _build_fake_target_repo(tmp_path, text=_IMPL_WITH_PREAMBLE_TEXT)
        graph_db = _sync_graph_for(
            repo, symbols=[("helper", "function", 4), ("target_function", "function", 8)]
        )
        res = aci.resolve_changed_range(oracle, repo, graph_db, aci.ChangedRange("impl.py", 1, 5))
        assert res.status == "partially_resolved"
        assert [s.name for s in res.symbols] == ["helper"]
        assert "1-3" in res.reason

    def test_duplicate_applicable_checks_deduplicated_with_provenance(self, tmp_path):
        """decisions/0089 §B: when two touched symbols both bridge to the
        SAME check, assess() must run that check exactly once, while still
        recording every symbol that made it applicable."""
        repo = _build_fake_target_repo(tmp_path)
        graph_db = _sync_graph_for(repo)

        slug_dir = tmp_path / "knowledge-root" / "planning" / "knowledge" / "demo"
        contracts_dir = tmp_path / "knowledge-root" / "planning" / "contracts" / "demo"
        contract_path = contracts_dir / "oracle-contract.yaml"
        _write_demo_contract(contract_path, check_id="chk-a")
        result_path = contracts_dir / "results" / "chk-a--r1.yaml"
        _write_fake_result(result_path, contract_path, check_id="chk-a")
        test_ref = f'"{result_path.relative_to(tmp_path / "knowledge-root")}"'

        for i, (sym_name, source_line) in enumerate((("helper", 1), ("target_function", 5)), start=1):
            ev_src, ev_test, cl = f"EV-SYM-{i}01", f"EV-SYM-{i}02", f"CL-SYM-{i}"
            _write_flat(slug_dir / f"{ev_src}.yaml", {
                "id": ev_src, "kind": "evidence", "evidence_kind": "source",
                "source_ref": f'"impl.py:{source_line} def {sym_name}"',
            })
            _write_flat(slug_dir / f"{ev_test}.yaml", {
                "id": ev_test, "kind": "evidence", "evidence_kind": "test",
                "test_ref": test_ref,
            })
            _write_flat(slug_dir / f"{cl}.yaml", {
                "id": cl, "kind": "claim",
                "supporting_evidence": [ev_src, ev_test],
            })

        report = aci.assess(
            target_repo_root=repo, target_graph_db=graph_db,
            knowledge_root=tmp_path / "knowledge-root", slug="demo",
            changed=[aci.ChangedRange("impl.py", 1, 6)], run_checks=False,
        )
        finding = report["findings"][0]
        assert finding["status"] == "resolved"
        assert len(finding["symbol_classifications"]) == 2
        assert all(sc["classification"] == "behavioural_risk" for sc in finding["symbol_classifications"])
        # Exactly one assurance entry for the shared check -- deduplicated.
        assert len(finding["assurance"]) == 1
        assert finding["assurance"][0]["check_id"] == "chk-a"
        assert sorted(finding["assurance"][0]["contributing_symbols"]) == ["helper", "target_function"]


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
        classification, findings = aci.classify_symbol(
            records, contract, oracle, "target_function", "impl.py", tmp_path
        )
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

        classification, findings = aci.classify_symbol(
            records, contract, oracle, "target_function", "impl.py", tmp_path
        )
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
        classification, findings = aci.classify_symbol(
            records, contract, oracle, "target_function", "impl.py", tmp_path
        )
        assert classification == "behavioural_risk"
        assert len(findings) == 1
        assert findings[0].tier == "behavioural_risk"
        assert findings[0].check_id == "chk-a"


# ---------------------------------------------------------------------------
# classify_symbol -- §A source-path identity (decisions/0089 §A): a citing
# Evidence must match on BOTH symbol name and source path, never name alone
# ---------------------------------------------------------------------------


class TestClassifySymbolSourceIdentity:
    def test_same_named_symbol_in_a_different_file_does_not_inherit_evidence(self, tmp_path):
        """The regression this corrective pass exists to fix: an Evidence
        citing `other.py`'s own `target_function` must never answer for
        `impl.py`'s own, identically-named `target_function`."""
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        contract_path = tmp_path / "planning" / "contracts" / "demo" / "oracle-contract.yaml"
        _write_demo_contract(contract_path)
        _write_flat(slug_dir / "EV-X-001.yaml", {
            "id": "EV-X-001", "kind": "evidence", "evidence_kind": "source",
            "source_ref": '"other.py:5 def target_function"',
        })
        _write_flat(slug_dir / "CL-X-001.yaml", {
            "id": "CL-X-001", "kind": "claim", "supporting_evidence": ["EV-X-001"],
        })
        contract = oracle.parse_oracle_contract(contract_path)
        ki = _load_ki()
        records = ki.load_slug_records(slug_dir)

        classification, findings = aci.classify_symbol(
            records, contract, oracle, "target_function", "impl.py", tmp_path
        )
        assert classification == "no_recorded_relationship"
        assert findings == []

    def test_matching_path_and_symbol_still_establishes_relevance(self, tmp_path):
        """Positive control, alongside a decoy same-named-but-different-file
        Evidence -- only the matching-path Evidence's Claim surfaces."""
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        contract_path = tmp_path / "planning" / "contracts" / "demo" / "oracle-contract.yaml"
        _write_demo_contract(contract_path)
        _write_flat(slug_dir / "EV-DECOY-001.yaml", {
            "id": "EV-DECOY-001", "kind": "evidence", "evidence_kind": "source",
            "source_ref": '"other.py:5 def target_function"',
        })
        _write_flat(slug_dir / "CL-DECOY-001.yaml", {
            "id": "CL-DECOY-001", "kind": "claim", "supporting_evidence": ["EV-DECOY-001"],
        })
        _write_flat(slug_dir / "EV-REAL-001.yaml", {
            "id": "EV-REAL-001", "kind": "evidence", "evidence_kind": "source",
            "source_ref": '"impl.py:5 def target_function"',
        })
        _write_flat(slug_dir / "CL-REAL-001.yaml", {
            "id": "CL-REAL-001", "kind": "claim", "supporting_evidence": ["EV-REAL-001"],
        })
        contract = oracle.parse_oracle_contract(contract_path)
        ki = _load_ki()
        records = ki.load_slug_records(slug_dir)

        classification, findings = aci.classify_symbol(
            records, contract, oracle, "target_function", "impl.py", tmp_path
        )
        assert classification == "relevant_no_coverage_link"
        assert [f.claim_id for f in findings] == ["CL-REAL-001"]

    def test_equivalent_path_spellings_still_match(self, tmp_path):
        """`./impl.py` and `impl.py` must normalise to the same identity
        (decisions/0089 §A: "normalising paths consistently")."""
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        contract_path = tmp_path / "planning" / "contracts" / "demo" / "oracle-contract.yaml"
        _write_demo_contract(contract_path)
        _write_flat(slug_dir / "EV-X-001.yaml", {
            "id": "EV-X-001", "kind": "evidence", "evidence_kind": "source",
            "source_ref": '"./impl.py:5 def target_function"',
        })
        _write_flat(slug_dir / "CL-X-001.yaml", {
            "id": "CL-X-001", "kind": "claim", "supporting_evidence": ["EV-X-001"],
        })
        contract = oracle.parse_oracle_contract(contract_path)
        ki = _load_ki()
        records = ki.load_slug_records(slug_dir)

        classification, _ = aci.classify_symbol(
            records, contract, oracle, "target_function", "impl.py", tmp_path
        )
        assert classification == "relevant_no_coverage_link"


# ---------------------------------------------------------------------------
# classify_symbol -- §C validated test-evidence (decisions/0089 §C): a
# referenced historical result must parse as a real OracleResult and
# genuinely belong to the live contract/check/scope, never a bare YAML
# key check
# ---------------------------------------------------------------------------


def _write_source_and_claim(slug_dir: Path, test_evidence_fields: dict) -> None:
    _write_flat(slug_dir / "EV-SRC-001.yaml", {
        "id": "EV-SRC-001", "kind": "evidence", "evidence_kind": "source",
        "source_ref": '"impl.py:5 def target_function"',
    })
    _write_flat(slug_dir / "EV-TEST-001.yaml", {**test_evidence_fields, "id": "EV-TEST-001"})
    _write_flat(slug_dir / "CL-X-001.yaml", {
        "id": "CL-X-001", "kind": "claim", "supporting_evidence": ["EV-SRC-001", "EV-TEST-001"],
    })


class TestClassifySymbolEvidenceValidation:
    def test_valid_historical_result_establishes_behavioural_risk(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        contracts_dir = tmp_path / "planning" / "contracts" / "demo"
        contract_path = contracts_dir / "oracle-contract.yaml"
        _write_demo_contract(contract_path, check_id="chk-a", scope="scope A")
        contract = oracle.parse_oracle_contract(contract_path)
        result_path = contracts_dir / "results" / "chk-a--r1.yaml"
        _write_fake_result(result_path, contract_path, check_id="chk-a")
        _write_source_and_claim(slug_dir, {
            "id": "EV-TEST", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_path.relative_to(tmp_path)}"',
        })
        ki = _load_ki()
        records = ki.load_slug_records(slug_dir)
        classification, findings = aci.classify_symbol(
            records, contract, oracle, "target_function", "impl.py", tmp_path
        )
        assert classification == "behavioural_risk"
        assert findings[0].check_id == "chk-a"

    def test_malformed_yaml_result_never_establishes_coverage(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        contracts_dir = tmp_path / "planning" / "contracts" / "demo"
        contract_path = contracts_dir / "oracle-contract.yaml"
        _write_demo_contract(contract_path, check_id="chk-a")
        contract = oracle.parse_oracle_contract(contract_path)
        bad_path = contracts_dir / "results" / "chk-a--malformed.yaml"
        bad_path.parent.mkdir(parents=True, exist_ok=True)
        bad_path.write_text("not: valid: yaml: at: all: [[[", encoding="utf-8")
        _write_source_and_claim(slug_dir, {
            "id": "EV-TEST", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{bad_path.relative_to(tmp_path)}"',
        })
        ki = _load_ki()
        records = ki.load_slug_records(slug_dir)
        classification, _ = aci.classify_symbol(
            records, contract, oracle, "target_function", "impl.py", tmp_path
        )
        assert classification == "relevant_no_coverage_link"

    def test_missing_required_fields_never_establishes_coverage(self, tmp_path):
        """The exact malformed shape the original defect accepted: a
        top-level mapping with a matching `check_id` key but almost none
        of OracleResult's own required fields."""
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        contracts_dir = tmp_path / "planning" / "contracts" / "demo"
        contract_path = contracts_dir / "oracle-contract.yaml"
        _write_demo_contract(contract_path, check_id="chk-a")
        contract = oracle.parse_oracle_contract(contract_path)
        bad_path = contracts_dir / "results" / "chk-a--incomplete.yaml"
        bad_path.parent.mkdir(parents=True, exist_ok=True)
        bad_path.write_text("check_id: chk-a\noutcome: PASS\n", encoding="utf-8")
        _write_source_and_claim(slug_dir, {
            "id": "EV-TEST", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{bad_path.relative_to(tmp_path)}"',
        })
        ki = _load_ki()
        records = ki.load_slug_records(slug_dir)
        classification, _ = aci.classify_symbol(
            records, contract, oracle, "target_function", "impl.py", tmp_path
        )
        assert classification == "relevant_no_coverage_link"

    def test_wrong_contract_identity_never_establishes_coverage(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        contracts_dir = tmp_path / "planning" / "contracts" / "demo"
        contract_path = contracts_dir / "oracle-contract.yaml"
        _write_demo_contract(contract_path, check_id="chk-a", scope="scope A")
        contract = oracle.parse_oracle_contract(contract_path)
        result_path = contracts_dir / "results" / "chk-a--wrong-contract.yaml"
        _write_fake_result(
            result_path, contract_path, check_id="chk-a",
            contract_id_override="REQ-UNRELATED-999",
        )
        _write_source_and_claim(slug_dir, {
            "id": "EV-TEST", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_path.relative_to(tmp_path)}"',
        })
        ki = _load_ki()
        records = ki.load_slug_records(slug_dir)
        classification, _ = aci.classify_symbol(
            records, contract, oracle, "target_function", "impl.py", tmp_path
        )
        assert classification == "relevant_no_coverage_link"

    def test_wrong_scope_never_establishes_coverage(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        contracts_dir = tmp_path / "planning" / "contracts" / "demo"
        contract_path = contracts_dir / "oracle-contract.yaml"
        _write_demo_contract(contract_path, check_id="chk-a", scope="scope A")
        contract = oracle.parse_oracle_contract(contract_path)
        result_path = contracts_dir / "results" / "chk-a--wrong-scope.yaml"
        _write_fake_result(
            result_path, contract_path, check_id="chk-a", scope_override="an entirely different scope",
        )
        _write_source_and_claim(slug_dir, {
            "id": "EV-TEST", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_path.relative_to(tmp_path)}"',
        })
        ki = _load_ki()
        records = ki.load_slug_records(slug_dir)
        classification, _ = aci.classify_symbol(
            records, contract, oracle, "target_function", "impl.py", tmp_path
        )
        assert classification == "relevant_no_coverage_link"

    def test_unknown_check_id_never_establishes_coverage(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        contracts_dir = tmp_path / "planning" / "contracts" / "demo"
        contract_path = contracts_dir / "oracle-contract.yaml"
        _write_demo_contract(contract_path, check_id="chk-a", scope="scope A")
        contract = oracle.parse_oracle_contract(contract_path)
        result_path = contracts_dir / "results" / "chk-unknown--r1.yaml"
        _write_fake_result(
            result_path, contract_path, check_id="chk-unknown", scope_override="scope A",
        )
        _write_source_and_claim(slug_dir, {
            "id": "EV-TEST", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_path.relative_to(tmp_path)}"',
        })
        ki = _load_ki()
        records = ki.load_slug_records(slug_dir)
        classification, _ = aci.classify_symbol(
            records, contract, oracle, "target_function", "impl.py", tmp_path
        )
        assert classification == "relevant_no_coverage_link"

    def test_missing_referenced_file_never_establishes_coverage(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        contract_path = tmp_path / "planning" / "contracts" / "demo" / "oracle-contract.yaml"
        _write_demo_contract(contract_path, check_id="chk-a")
        contract = oracle.parse_oracle_contract(contract_path)
        _write_source_and_claim(slug_dir, {
            "id": "EV-TEST", "kind": "evidence", "evidence_kind": "test",
            "test_ref": '"planning/contracts/demo/results/does-not-exist.yaml"',
        })
        ki = _load_ki()
        records = ki.load_slug_records(slug_dir)
        classification, _ = aci.classify_symbol(
            records, contract, oracle, "target_function", "impl.py", tmp_path
        )
        assert classification == "relevant_no_coverage_link"


def _load_ki():
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from codecompass import knowledge_intermediate as ki

    return ki


def _write_fake_result(
    path: Path, contract_path: Path, *, check_id: str, outcome: str = "PASS",
    contract_id_override: str | None = None, scope_override: str | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw_path = path.parent / f"{check_id}-raw.txt"
    raw_path.write_text("ok", encoding="utf-8")
    contract_id = contract_id_override or "REQ-X-001"
    scope = scope_override or "scope A"
    result = oracle.OracleResult(
        schema_version=1, run_id="r1", contract_id=contract_id, check_id=check_id,
        scope=scope, baseline_id=None, tested_subject_digest="d" * 64,
        oracle_contract_id=contract_id, oracle_contract_content_hash=oracle.sha256_file(contract_path),
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
        assert len(finding["symbol_classifications"]) == 1
        assert finding["symbol_classifications"][0]["classification"] == "behavioural_risk"
        assert len(finding["assurance"]) == 1
        assert finding["assurance"][0]["classification"] == "VERIFICATION_GAP"
        assert finding["assurance"][0]["fresh_effective_outcome"] is None
        assert finding["assurance"][0]["contributing_symbols"] == ["target_function"]

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
