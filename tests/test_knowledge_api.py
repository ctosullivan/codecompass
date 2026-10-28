"""Tests for codecompass.knowledge_api (Phase 84 -- Consolidated Knowledge
API and Query CLI). See planning/phase-84-consolidated-knowledge-api.md
and decisions/0084/0085 for the full design.

Three groups: (1) synthetic `tmp_path` fixtures for negative controls and
mechanism-level guarantees (no-mutation-path, identity stability across a
rebuild, consistency-envelope current/stale/incompatible), mirroring
tests/test_assess_change_impact.py's own tmp_path-as-fake-repo
convention; (2) tests against this project's own real corpus
(`planning/knowledge/balance-from-spec/`, `planning/contracts/
balance-from-spec/`) -- required by the plan's own "real corpus, not
synthetic fixture only" instruction; (3) the real-corpus dogfood,
additionally resolving a real source symbol against the real
`~/projects/ledgerkit` checkout's own `context-graph.db` (skipped when
that checkout isn't present).
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import pytest

from codecompass import graph
from codecompass import knowledge_api as ka
from codecompass import knowledge_intermediate as ki
from codecompass import oracle

REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_API_SRC = REPO_ROOT / "src" / "codecompass" / "knowledge_api.py"

LEDGERKIT_ROOT = Path.home() / "projects" / "ledgerkit"
requires_ledgerkit = pytest.mark.skipif(
    not (LEDGERKIT_ROOT.is_dir() and (LEDGERKIT_ROOT / "context-graph.db").is_file()),
    reason="~/projects/ledgerkit (with its own context-graph.db) is not present in this environment",
)


# ---------------------------------------------------------------------------
# Fixture helpers
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


def _write_contract(path: Path, *, contract_id="REQ-DEMO-001", check_id="chk-a", scope="scope A", required=True) -> None:
    import yaml

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump({
            "schema_version": 1,
            "contract_id": contract_id,
            "tested_paths": ["impl.py"],
            "checks": [{
                "check_id": check_id, "scope": scope, "execution_provider": "pytest",
                "check_reference": "tests/test_impl.py::test_ok",
                "test_input_paths": ["tests/test_impl.py"], "required": required,
            }],
        }, sort_keys=False),
        encoding="utf-8",
    )


def _write_result(path: Path, contract_path: Path, *, contract_id="REQ-DEMO-001", check_id="chk-a",
                   scope="scope A", outcome="PASS", run_id="r1",
                   tested_subject_digest: str | None = None, test_input_digest: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw_path = path.parent / f"{check_id}-{run_id}-raw.txt"
    raw_path.write_text("ok", encoding="utf-8")
    result = oracle.OracleResult(
        schema_version=1, run_id=run_id, contract_id=contract_id, check_id=check_id,
        scope=scope, baseline_id=None, tested_subject_digest=tested_subject_digest or "d" * 64,
        oracle_contract_id=contract_id, oracle_contract_content_hash=oracle.sha256_file(contract_path),
        test_input_digest=test_input_digest or "i" * 64, raw_output_ref=str(raw_path),
        raw_output_sha256=oracle.sha256_file(raw_path), outcome=outcome,
        executed_at="2026-10-29T00:00:00Z", execution_provider="pytest",
        environment_descriptor=None, invalid_reason=None,
    )
    oracle.write_oracle_result(path, result)


def _write_minimal_slug(project_root: Path, slug: str) -> Path:
    """A Decision -> Requirement -> Claim -> Evidence(source) chain, plus
    a matching oracle contract/result, under one slug -- the smallest
    fixture exercising every relation this module supports."""
    slug_dir = project_root / "planning" / "knowledge" / slug
    contract_path = project_root / "planning" / "contracts" / slug / "oracle-contract.yaml"
    _write_contract(contract_path, contract_id="REQ-DEMO-001")
    result_path = project_root / "planning" / "contracts" / slug / "results" / "chk-a--r1.yaml"

    (project_root / "impl.py").write_text("def target_function():\n    return 1\n", encoding="utf-8")
    (project_root / "tests").mkdir(exist_ok=True)
    (project_root / "tests" / "test_impl.py").write_text(
        "def test_ok():\n    assert True\n", encoding="utf-8"
    )
    # Real, correctly recomputable digests -- so a `repo_root`-reachable
    # call genuinely resolves this result to a live, current PASS (§3.B's
    # own "current" case), not merely a structurally-valid-but-digest-
    # mismatched historical one.
    real_tested_digest = oracle.compute_tree_digest(project_root, ["impl.py"])
    real_input_digest = oracle.compute_tree_digest(project_root, ["tests/test_impl.py"])
    _write_result(
        result_path, contract_path,
        tested_subject_digest=real_tested_digest, test_input_digest=real_input_digest,
    )

    _write_flat(slug_dir / "DEC-DEMO-001.yaml", {
        "id": "DEC-DEMO-001", "kind": "decision", "decides": "demo decision", "status": "approved",
    })
    _write_flat(slug_dir / "REQ-DEMO-001.yaml", {
        "id": "REQ-DEMO-001", "kind": "requirement", "statement": "demo requirement",
        "decision": "DEC-DEMO-001", "status": "implemented", "depends_on": ["CL-DEMO-001"],
    })
    _write_flat(slug_dir / "OBS-DEMO-001.yaml", {
        "id": "OBS-DEMO-001", "kind": "observation", "method": "source_read",
        "what_was_done": "read impl.py", "status": "recorded",
    })
    _write_flat(slug_dir / "EV-DEMO-001.yaml", {
        "id": "EV-DEMO-001", "kind": "evidence", "evidence_kind": "source",
        "what_it_shows": "demo", "observations": ["OBS-DEMO-001"],
        "source_ref": '"impl.py:1 def target_function"', "status": "current",
    })
    _write_flat(slug_dir / "EV-DEMO-002.yaml", {
        "id": "EV-DEMO-002", "kind": "evidence", "evidence_kind": "test",
        "what_it_shows": "demo", "test_ref": f'"{result_path.relative_to(project_root)}"',
        "status": "current",
    })
    _write_flat(slug_dir / "CL-DEMO-001.yaml", {
        "id": "CL-DEMO-001", "kind": "claim", "statement": "demo claim",
        "supporting_evidence": ["EV-DEMO-001", "EV-DEMO-002"], "contradicting_evidence": [],
        "basis": "observed_behaviour", "status": "supported",
    })
    return slug_dir


# ---------------------------------------------------------------------------
# No-mutation-path (plan §6's own explicit test)
# ---------------------------------------------------------------------------


class TestNoMutationPath:
    _FORBIDDEN_REFERENCES = [
        "write_oracle_result", "accept_baseline", "run_pytest_check", "evaluate_check",
        "write_presentation_cache", "render_block(", "render_slug(", "render_phase_brief(",
        "_replace_anchor_blocks", "refresh_safe_anchors", "apply_automatic_refreshes",
        "write_manifest(", "_write_record(", "apply_manifest(", "_apply_doc_region_edit",
        "_write_region_baseline", "establish_new_region_baselines",
        "acknowledge_stale_grounded_region", "write_doc_candidates_to_manifests",
        "_add_cited_id_to_grounding_marker", "advance_doc_chunk_baseline",
        "open_graph(", "rebuild_deterministic(", "record_enrichment(",
        "record_symbol_enrichment", "record_relation_enrichment",
    ]

    def test_module_source_references_no_writer_function(self):
        src = KNOWLEDGE_API_SRC.read_text(encoding="utf-8")
        for name in self._FORBIDDEN_REFERENCES:
            assert name not in src, f"knowledge_api.py references forbidden writer {name!r}"

    def test_every_sqlite_connect_call_is_read_only(self):
        src = KNOWLEDGE_API_SRC.read_text(encoding="utf-8")
        calls = re.findall(r"sqlite3\.connect\(([^)]*)\)", src)
        assert calls, "expected at least one sqlite3.connect call in knowledge_api.py"
        for call in calls:
            assert "mode=ro" in call, f"non-read-only sqlite3.connect call: {call!r}"

    def test_get_does_not_create_a_missing_context_graph_db(self, tmp_path):
        assert not (tmp_path / "context-graph.db").exists()
        response = ka.get(tmp_path, "REQ-DOES-NOT-EXIST-001")
        assert response.status == "empty"
        assert not (tmp_path / "context-graph.db").exists()

    def test_export_snapshot_refuses_to_write_inside_knowledge_tree(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        target = tmp_path / "planning" / "knowledge" / "demo" / "sneaky.json"
        with pytest.raises(ValueError):
            ka.export_snapshot(tmp_path, "demo", target)
        assert not target.exists()

    def test_export_snapshot_refuses_to_write_inside_contracts_tree(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        target = tmp_path / "planning" / "contracts" / "demo" / "sneaky.json"
        with pytest.raises(ValueError):
            ka.export_snapshot(tmp_path, "demo", target)
        assert not target.exists()

    def test_export_snapshot_does_not_modify_canonical_records(self, tmp_path):
        slug_dir = _write_minimal_slug(tmp_path, "demo")
        before = {p.name: p.read_text() for p in slug_dir.glob("*.yaml")}
        ka.export_snapshot(tmp_path, "demo", tmp_path / "out.json")
        after = {p.name: p.read_text() for p in slug_dir.glob("*.yaml")}
        assert before == after


# ---------------------------------------------------------------------------
# §3.A -- stable identities across a deterministic rebuild
# ---------------------------------------------------------------------------


class TestStableIdentityAcrossRebuild:
    def _rebuild(self, conn):
        graph.rebuild_deterministic(
            conn,
            vendors=[graph.VendorRow(name="demo-vendor", ecosystem="npm", installed_version="1.0.0")],
            source_files=[graph.SourceFileRow(path="src/app.ts", language="typescript", content_hash="h1")],
            symbols=[graph.SymbolRow(vendor_name="demo-vendor", name="doThing")],
            uses_edges=[graph.UsesEdgeRow(source_file_path="src/app.ts", vendor_name="demo-vendor",
                                           symbol_name="doThing", line=3)],
            doc_artifacts=[graph.DocArtifactRow(path="README.md", kind="spec_doc", origin="project")],
            documents_edges=[], skill_mentions_edges=[], routes_via_edges=[], depends_on_edges=[],
            doc_relations_edges=[graph.DocRelationEdgeRow(
                source_doc_artifact_path="README.md", relation_kind="mentions_dependency",
                target_vendor_name="demo-vendor",
            )],
            source_symbols=[graph.SourceSymbolRow(
                source_file_path="src/app.ts", name="main", kind="function", line=10,
            )],
        )

    def test_natural_key_table_identity_survives_rebuild(self, tmp_path):
        """`source_symbols` is upserted by natural key (Phase 77) -- its
        raw `id` *may* differ across a rebuild (never guaranteed stable by
        this module), while `knowledge_api.symbol_identity`'s own computed
        identity is byte-identical, because it is a pure function of
        columns the rebuild deliberately preserves (path/name/kind/line),
        never of the row's own `INTEGER PRIMARY KEY`."""
        conn = graph.open_graph(tmp_path)
        self._rebuild(conn)
        row_before = conn.execute(
            "SELECT id FROM source_symbols WHERE name = 'main'"
        ).fetchone()
        identity_before = ka.symbol_identity("src/app.ts", "main", "function", 10)

        self._rebuild(conn)  # same unchanged source -- a second full rebuild
        row_after = conn.execute(
            "SELECT id FROM source_symbols WHERE name = 'main'"
        ).fetchone()
        identity_after = ka.symbol_identity("src/app.ts", "main", "function", 10)
        conn.close()

        assert identity_before == identity_after
        # Phase 77 upserts by natural key -- raw id is in fact stable here
        # too, confirming the *computed* identity is never merely an
        # accident of a stable raw id either.
        assert row_before == row_after

    def test_wholesale_rebuilt_edge_table_raw_id_is_not_guaranteed_stable(self, tmp_path):
        """`doc_relations_edges` is fully cleared and reinserted every
        rebuild (confirmed directly in `graph.py`, not inferred) -- its
        raw `id` is not preserved across a rebuild even when the fixture
        is byte-for-byte unchanged, demonstrating the real risk `symbol_
        identity`/`doc_identity`-style natural keys exist to avoid. This
        module never exposes that raw id as an identity at all."""
        conn = graph.open_graph(tmp_path)
        self._rebuild(conn)
        # A second, deliberately different doc_relations_edges row, added
        # BEFORE the tracked one on the second rebuild only -- demonstrates
        # the raw id is a function of clear+reinsert order, not of the
        # relation's own content, which `doc_identity`'s own natural key
        # (never used for this edge kind -- `docrel:`'s own id below is
        # itself index-based within one response, not a persisted row id)
        # must never depend on.
        id_before = conn.execute(
            "SELECT id FROM doc_relations_edges WHERE relation_kind = 'mentions_dependency'"
        ).fetchone()[0]
        conn2 = graph.open_graph(tmp_path)
        graph.rebuild_deterministic(
            conn2,
            vendors=[graph.VendorRow(name="demo-vendor", ecosystem="npm", installed_version="1.0.0"),
                     graph.VendorRow(name="other-vendor", ecosystem="npm", installed_version="1.0.0")],
            source_files=[graph.SourceFileRow(path="src/app.ts", language="typescript", content_hash="h1")],
            symbols=[graph.SymbolRow(vendor_name="demo-vendor", name="doThing")],
            uses_edges=[graph.UsesEdgeRow(source_file_path="src/app.ts", vendor_name="demo-vendor",
                                           symbol_name="doThing", line=3)],
            doc_artifacts=[graph.DocArtifactRow(path="README.md", kind="spec_doc", origin="project")],
            documents_edges=[], skill_mentions_edges=[], routes_via_edges=[], depends_on_edges=[],
            doc_relations_edges=[
                # A new, unrelated relation inserted FIRST this time --
                # same unchanged tracked relation now lands at a different
                # row id purely because of insertion order.
                graph.DocRelationEdgeRow(
                    source_doc_artifact_path="README.md", relation_kind="mentions_dependency",
                    target_vendor_name="other-vendor",
                ),
                graph.DocRelationEdgeRow(
                    source_doc_artifact_path="README.md", relation_kind="mentions_dependency",
                    target_vendor_name="demo-vendor",
                ),
            ],
            source_symbols=[graph.SourceSymbolRow(
                source_file_path="src/app.ts", name="main", kind="function", line=10,
            )],
        )
        id_after = conn2.execute(
            "SELECT id FROM doc_relations_edges WHERE target_vendor_id = "
            "(SELECT id FROM vendors WHERE name = 'demo-vendor')"
        ).fetchone()[0]
        conn.close()
        conn2.close()
        # The same logical relation (README.md mentions demo-vendor) now
        # has a different raw row id purely because of insertion order --
        # the documented, confirmed-real risk, not a flaky assertion:
        assert id_after != id_before
        # ...and knowledge_api never surfaces that volatile id as identity:
        response = ka.get(tmp_path, "README.md")
        assert response.status == "empty"  # not a knowledge_api identity shape at all
        response = ka.traverse(tmp_path, "README.md", "doc_mentions")
        assert response.status == "result"
        # The `docrel:` id's own trailing integer is a response-local
        # position (`enumerate`), never the row's own volatile
        # `doc_relations_edges.id` -- confirmed directly: that raw id
        # column name never appears in any returned detail dict at all.
        assert all("id" not in r.details for r in response.results)


# ---------------------------------------------------------------------------
# §3.B -- snapshot consistency (current / stale / incompatible)
# ---------------------------------------------------------------------------


class TestConsistencyEnvelope:
    def test_current_when_live_source_and_contract_both_reachable_and_matching(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        response = ka.get(tmp_path, "EV-DEMO-001", repo_root=tmp_path)
        assert response.status == "result"
        # EV-DEMO-001 cites EV-DEMO-002's own check via CL-DEMO-001 -- the
        # claim itself is what carries verified/gap scopes; checked below.
        # repo_root=tmp_path makes the tested_subject_digest live-
        # reconfirmable -- without it, §3.B's own rule is "unconfirmed",
        # exercised separately below.
        claim = ka.get(tmp_path, "CL-DEMO-001", repo_root=tmp_path).results[0]
        assert claim.consistency.evidence_currency == "current"
        assert claim.consistency.status == "current"

    def test_stale_reported_when_indexed_source_hash_disagrees_with_live_file(self, tmp_path):
        conn = graph.open_graph(tmp_path)
        graph.rebuild_deterministic(
            conn, vendors=[], source_files=[graph.SourceFileRow(path="impl.py", content_hash="h-original")],
            symbols=[], uses_edges=[], doc_artifacts=[],
            documents_edges=[], skill_mentions_edges=[], routes_via_edges=[], depends_on_edges=[],
            doc_relations_edges=[],
            source_symbols=[graph.SourceSymbolRow(
                source_file_path="impl.py", name="target_function", kind="function", line=1,
            )],
        )
        conn.close()
        (tmp_path / "impl.py").write_text("def target_function():\n    return 2\n", encoding="utf-8")

        response = ka.get(tmp_path, ka.symbol_identity("impl.py", "target_function", "function", 1))
        assert response.status == "result"
        assert response.results[0].consistency.status == "stale"
        assert response.results[0].consistency.reasons

    def test_unconfirmed_when_no_repo_root_reachable_to_reconfirm_a_historical_pass(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        # Mutate the contract so the recorded result's own
        # oracle_contract_content_hash no longer matches the live file --
        # the same real-world scenario (a later-extended contract) this
        # project's own balance-from-spec corpus actually exhibits.
        contract_path = tmp_path / "planning" / "contracts" / "demo" / "oracle-contract.yaml"
        _write_contract(contract_path, contract_id="REQ-DEMO-001", check_id="chk-a", scope="scope A, extended")
        response = ka.get(tmp_path, "CL-DEMO-001")
        claim = response.results[0]
        assert claim.consistency.evidence_currency in ("absent", "unconfirmed")
        assert claim.consistency.status != "current"

    def test_incompatible_revision_surfaced_via_evaluate_result_precedence(self, tmp_path):
        slug_dir = _write_minimal_slug(tmp_path, "demo")
        contract_path = tmp_path / "planning" / "contracts" / "demo" / "oracle-contract.yaml"
        bad_result_path = tmp_path / "planning" / "contracts" / "demo" / "results" / "chk-a--bad.yaml"
        _write_result(bad_result_path, contract_path, run_id="bad")
        # Tamper the recorded tested_subject_digest so it can never match a
        # live recomputation -- evaluate_result_precedence's own INVALID
        # path, reused unchanged by this module.
        bad = oracle.parse_oracle_result(bad_result_path)
        bad.tested_subject_digest = "f" * 64
        oracle.write_oracle_result(bad_result_path, bad)

        response = ka.get(tmp_path, ka.result_identity("REQ-DEMO-001", "chk-a", "bad"))
        assert response.status == "result"
        details = response.results[0].details
        outcome, reason = oracle.evaluate_result_precedence(
            oracle.parse_oracle_result(bad_result_path),
            oracle.parse_oracle_contract(contract_path),
            oracle.parse_oracle_contract(contract_path).check_by_id("chk-a"),
            contract_path=contract_path, repo_root=tmp_path,
        )
        assert outcome == "INVALID"


# ---------------------------------------------------------------------------
# Corrective pass defect A -- verification currency must be accurate
# across get()/traverse(), never implied "current" by an optimistic
# default, and only ever positively earned by a live repo_root
# reconfirmation (decisions/0092).
# ---------------------------------------------------------------------------


class TestResultVerificationCurrency:
    def test_recorded_pass_current_against_unchanged_target(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        response = ka.get(tmp_path, ka.result_identity("REQ-DEMO-001", "chk-a", "r1"), repo_root=tmp_path)
        assert response.status == "result"
        result = response.results[0]
        assert result.details["outcome"] == "PASS"
        assert result.details["effective_outcome"] == "PASS"
        assert result.consistency.status == "current"
        assert result.consistency.evidence_currency == "current"

    def test_recorded_pass_invalidated_by_changed_implementation(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        # The real target has since changed -- the recorded
        # tested_subject_digest can no longer match a live recomputation.
        (tmp_path / "impl.py").write_text("def target_function():\n    return 999\n", encoding="utf-8")
        response = ka.get(tmp_path, ka.result_identity("REQ-DEMO-001", "chk-a", "r1"), repo_root=tmp_path)
        result = response.results[0]
        assert result.details["outcome"] == "PASS"  # recorded outcome never rewritten
        assert result.details["effective_outcome"] == "INVALID"
        assert result.consistency.status == "stale"
        assert result.consistency.reasons

    def test_recorded_pass_unconfirmed_without_a_reachable_checkout(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        # No repo_root at all -- the digest can neither be confirmed nor
        # actively refuted; a historical PASS must never be reported as
        # currently verified on that basis alone.
        response = ka.get(tmp_path, ka.result_identity("REQ-DEMO-001", "chk-a", "r1"))
        result = response.results[0]
        assert result.details["outcome"] == "PASS"
        assert result.details["effective_outcome"] == "PASS"
        assert result.consistency.status == "unconfirmed"
        assert result.consistency.status != "current"
        assert result.consistency.reasons

    def test_outdated_contract_reported_stale_regardless_of_repo_root(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        contract_path = tmp_path / "planning" / "contracts" / "demo" / "oracle-contract.yaml"
        _write_contract(contract_path, contract_id="REQ-DEMO-001", check_id="chk-a", scope="scope A, extended")
        response = ka.get(tmp_path, ka.result_identity("REQ-DEMO-001", "chk-a", "r1"), repo_root=tmp_path)
        result = response.results[0]
        assert result.details["effective_outcome"] == "INVALID"
        assert result.consistency.status == "stale"

    def test_missing_raw_output_artifact_reported_stale(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        raw_path = tmp_path / "planning" / "contracts" / "demo" / "results" / "chk-a-r1-raw.txt"
        raw_path.unlink()
        response = ka.get(tmp_path, ka.result_identity("REQ-DEMO-001", "chk-a", "r1"), repo_root=tmp_path)
        result = response.results[0]
        assert result.details["effective_outcome"] == "INVALID"
        assert result.consistency.status == "stale"
        assert "raw_output_ref" in result.consistency.reasons[0]

    def test_get_and_traverse_results_agree_on_effective_outcome_and_status(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        (tmp_path / "impl.py").write_text("def target_function():\n    return 999\n", encoding="utf-8")
        get_response = ka.get(tmp_path, ka.result_identity("REQ-DEMO-001", "chk-a", "r1"), repo_root=tmp_path)
        traverse_response = ka.traverse(
            tmp_path, ka.check_identity("REQ-DEMO-001", "chk-a"), "results", repo_root=tmp_path
        )
        get_result = get_response.results[0]
        traverse_result = next(r for r in traverse_response.results if r.id == get_result.id)
        assert get_result.details["effective_outcome"] == traverse_result.details["effective_outcome"] == "INVALID"
        assert get_result.consistency.status == traverse_result.consistency.status == "stale"

    def test_traverse_results_without_repo_root_reports_unconfirmed_not_current(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        response = ka.traverse(tmp_path, ka.check_identity("REQ-DEMO-001", "chk-a"), "results")
        passing = [r for r in response.results if r.details["effective_outcome"] == "PASS"]
        assert passing
        assert all(r.consistency.status == "unconfirmed" for r in passing)

    def test_check_aggregate_current_only_with_reachable_repo_root(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        without = ka.get(tmp_path, ka.check_identity("REQ-DEMO-001", "chk-a"))
        with_repo = ka.get(tmp_path, ka.check_identity("REQ-DEMO-001", "chk-a"), repo_root=tmp_path)
        assert without.results[0].details["aggregate_state"] == "PASS"
        assert without.results[0].consistency.status == "unconfirmed"
        assert with_repo.results[0].details["aggregate_state"] == "PASS"
        assert with_repo.results[0].consistency.status == "current"

    def test_search_results_do_not_default_to_current(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        response = ka.search(tmp_path, "demo claim")
        assert response.status == "result"
        assert all(r.consistency.status != "current" for r in response.results)

    def test_context_packet_items_reflect_real_currency_not_an_optimistic_default(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        response = ka.get_context_packet(tmp_path, "CL-DEMO-001", repo_root=tmp_path)
        items = response.results[0].details["items"]
        claim_item = next(i for i in items if i["id"] == "CL-DEMO-001")
        assert claim_item["consistency"]["status"] == "current"
        without_repo = ka.get_context_packet(tmp_path, "CL-DEMO-001")
        claim_item_unconfirmed = next(
            i for i in without_repo.results[0].details["items"] if i["id"] == "CL-DEMO-001"
        )
        assert claim_item_unconfirmed["consistency"]["status"] != "current"


# ---------------------------------------------------------------------------
# §3.C -- authority tagging
# ---------------------------------------------------------------------------


class TestAuthorityTagging:
    def test_unverified_symbol_tagged_derived_index_never_scoped_verification(self, tmp_path):
        conn = graph.open_graph(tmp_path)
        graph.rebuild_deterministic(
            conn, vendors=[], source_files=[graph.SourceFileRow(path="impl.py")],
            symbols=[], uses_edges=[], doc_artifacts=[],
            documents_edges=[], skill_mentions_edges=[], routes_via_edges=[], depends_on_edges=[],
            doc_relations_edges=[],
            source_symbols=[graph.SourceSymbolRow(
                source_file_path="impl.py", name="lonely_function", kind="function", line=5,
            )],
        )
        conn.close()
        (tmp_path / "impl.py").write_text("def lonely_function():\n    pass\n", encoding="utf-8")
        response = ka.get(tmp_path, ka.symbol_identity("impl.py", "lonely_function", "function", 5))
        assert response.results[0].authority == ka.AUTHORITY_DERIVED_INDEX
        assert response.results[0].authority != ka.AUTHORITY_SCOPED_VERIFICATION

    def test_decision_and_oracle_result_are_visibly_separate_authority_layers(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        decision = ka.get(tmp_path, "DEC-DEMO-001").results[0]
        result = ka.get(tmp_path, ka.result_identity("REQ-DEMO-001", "chk-a", "r1")).results[0]
        assert decision.authority == ka.AUTHORITY_STATED_INTENT
        assert result.authority == ka.AUTHORITY_SCOPED_VERIFICATION
        assert decision.authority != result.authority

    @requires_ledgerkit
    def test_real_balance_from_spec_shows_stated_intent_and_scoped_verification_separately(self):
        decision = ka.get(REPO_ROOT, "DEC-BFS-001")
        assert decision.status == "result"
        assert decision.results[0].authority == ka.AUTHORITY_STATED_INTENT

        check_response = ka.traverse(REPO_ROOT, "contract:REQ-BFS-001", "checks")
        assert check_response.status == "result"
        results_response = ka.traverse(
            REPO_ROOT, "check:REQ-BFS-001:single-section-expense-subtotal", "results"
        )
        assert results_response.status == "result"
        assert all(r.authority == ka.AUTHORITY_SCOPED_VERIFICATION for r in results_response.results)
        assert any(r.details["outcome"] == "PASS" for r in results_response.results)


# ---------------------------------------------------------------------------
# get() / search() / traverse() -- negative paths, result/empty/gap shape
# ---------------------------------------------------------------------------


class TestGetNegativePaths:
    def test_unknown_id_shape_is_empty(self, tmp_path):
        response = ka.get(tmp_path, "not-an-id-at-all")
        assert response.status == "empty"

    def test_well_formed_but_absent_knowledge_id_is_empty(self, tmp_path):
        response = ka.get(tmp_path, "REQ-NOPE-999")
        assert response.status == "empty"

    def test_absent_symbol_identity_is_empty_not_an_exception(self, tmp_path):
        graph.open_graph(tmp_path).close()
        response = ka.get(tmp_path, ka.symbol_identity("nope.py", "nope", "function", 1))
        assert response.status == "empty"

    def test_malformed_check_identity_is_empty(self, tmp_path):
        response = ka.get(tmp_path, "check:not-enough-parts")
        assert response.status == "empty"


class TestSearchNegativePaths:
    def test_empty_query_text_is_empty(self, tmp_path):
        assert ka.search(tmp_path, "   ").status == "empty"

    def test_no_match_is_empty(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        assert ka.search(tmp_path, "zzz-nothing-matches-zzz").status == "empty"

    def test_kinds_filter_restricts_matches(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        response = ka.search(tmp_path, "demo", kinds=["decision"])
        assert response.status == "result"
        assert all(r.kind == "decision" for r in response.results)


class TestTraverseNegativePaths:
    def test_unknown_starting_identity_is_empty(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        response = ka.traverse(tmp_path, "REQ-NOPE-999", "depends_on")
        assert response.status == "empty"

    def test_known_identity_with_zero_edges_is_result_not_empty(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        response = ka.traverse(tmp_path, "CL-DEMO-001", "contradicting_evidence")
        assert response.status == "result"
        assert response.results == []

    def test_unknown_relation_name_is_empty(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        response = ka.traverse(tmp_path, "CL-DEMO-001", "not-a-real-relation")
        assert response.status == "empty"

    def test_doc_mentions_unknown_name_is_empty(self, tmp_path):
        graph.open_graph(tmp_path).close()
        response = ka.traverse(tmp_path, "does-not-exist-at-all", "doc_mentions")
        assert response.status == "empty"


# ---------------------------------------------------------------------------
# trace_evidence() / epistemic_status() / find_gaps() -- result/empty/gap
# ---------------------------------------------------------------------------


class TestTraceEvidence:
    def test_claim_with_no_supporting_evidence_is_a_gap(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        _write_flat(slug_dir / "CL-BARE-001.yaml", {
            "id": "CL-BARE-001", "kind": "claim", "statement": "unsupported", "status": "proposed",
        })
        response = ka.trace_evidence(tmp_path, "CL-BARE-001")
        assert response.status == "gap"
        assert response.gaps[0].kind == "missing_evidence"

    def test_claim_with_evidence_is_a_result_not_a_gap(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        response = ka.trace_evidence(tmp_path, "CL-DEMO-001")
        assert response.status == "result"
        assert {r.id for r in response.results} == {"EV-DEMO-001", "EV-DEMO-002"}

    def test_absent_record_is_empty_not_a_gap(self, tmp_path):
        response = ka.trace_evidence(tmp_path, "CL-NOPE-001")
        assert response.status == "empty"

    # -- Corrective pass defect B: a declared Evidence citation that does
    # not resolve to a real record must never be silently treated as
    # successful coverage (decisions/0092).

    def test_exclusively_dangling_supporting_evidence_is_a_gap(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        _write_flat(slug_dir / "CL-DANGLE-001.yaml", {
            "id": "CL-DANGLE-001", "kind": "claim", "statement": "dangling only",
            "supporting_evidence": ["EV-MISSING-001"], "status": "supported",
        })
        response = ka.trace_evidence(tmp_path, "CL-DANGLE-001")
        assert response.status == "gap"
        assert response.results == []
        dangling = [g for g in response.gaps if g.kind == "dangling_evidence_reference"]
        assert len(dangling) == 1
        assert dangling[0].subject_id == "CL-DANGLE-001"
        assert dangling[0].scope == "supporting"
        assert "EV-MISSING-001" in dangling[0].reason

    def test_mixed_valid_and_dangling_supporting_evidence_reports_both(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        _write_flat(slug_dir / "CL-MIXED-001.yaml", {
            "id": "CL-MIXED-001", "kind": "claim", "statement": "mixed",
            "supporting_evidence": ["EV-DEMO-001", "EV-MISSING-002"], "status": "supported",
        })
        response = ka.trace_evidence(tmp_path, "CL-MIXED-001")
        assert response.status == "gap"
        # The valid citation is never discarded because a sibling citation
        # is broken.
        assert {r.id for r in response.results} == {"EV-DEMO-001"}
        dangling = [g for g in response.gaps if g.kind == "dangling_evidence_reference"]
        assert {g.subject_id for g in dangling} == {"CL-MIXED-001"}
        assert any("EV-MISSING-002" in g.reason for g in dangling)

    def test_dangling_contradicting_evidence_is_a_gap(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        _write_flat(slug_dir / "CL-CONTRA-001.yaml", {
            "id": "CL-CONTRA-001", "kind": "claim", "statement": "has real support",
            "supporting_evidence": [], "contradicting_evidence": ["EV-MISSING-003"], "status": "supported",
        })
        response = ka.trace_evidence(tmp_path, "CL-CONTRA-001")
        assert response.status == "gap"
        kinds = {g.kind for g in response.gaps}
        assert "dangling_evidence_reference" in kinds
        dangling = [g for g in response.gaps if g.kind == "dangling_evidence_reference"]
        assert dangling[0].scope == "contradicting"
        assert "EV-MISSING-003" in dangling[0].reason


class TestEpistemicStatus:
    def test_requirement_aggregates_over_its_dependent_claims(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        response = ka.epistemic_status(tmp_path, "REQ-DEMO-001", repo_root=tmp_path)
        details = response.results[0].details
        assert details["intended"] is True
        assert "scope A" in details["verified_scopes"]

    def test_absent_record_is_empty(self, tmp_path):
        assert ka.epistemic_status(tmp_path, "REQ-NOPE-001").status == "empty"


class TestFindGaps:
    def test_missing_contract_detected(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "no-contract"
        _write_flat(slug_dir / "CL-NC-001.yaml", {
            "id": "CL-NC-001", "kind": "claim", "statement": "x", "status": "proposed",
        })
        response = ka.find_gaps(tmp_path, "no-contract")
        assert response.status == "gap"
        assert any(g.kind == "missing_contract" for g in response.gaps)

    def test_contradiction_detected(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        _write_flat(slug_dir / "CL-BAD-001.yaml", {
            "id": "CL-BAD-001", "kind": "claim", "statement": "x", "status": "contradicted",
        })
        response = ka.find_gaps(tmp_path, "demo")
        assert any(g.kind == "contradiction" and g.subject_id == "CL-BAD-001" for g in response.gaps)

    def test_no_gaps_when_fully_covered_and_no_contradictions(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "clean"
        contract_path = tmp_path / "planning" / "contracts" / "clean" / "oracle-contract.yaml"
        _write_contract(contract_path, contract_id="REQ-CLEAN-001")
        result_path = tmp_path / "planning" / "contracts" / "clean" / "results" / "chk-a--r1.yaml"
        _write_result(result_path, contract_path, contract_id="REQ-CLEAN-001")
        _write_flat(slug_dir / "EV-CLEAN-001.yaml", {
            "id": "EV-CLEAN-001", "kind": "evidence", "evidence_kind": "test",
            "test_ref": f'"{result_path.relative_to(tmp_path)}"', "status": "current",
        })
        _write_flat(slug_dir / "CL-CLEAN-001.yaml", {
            "id": "CL-CLEAN-001", "kind": "claim", "statement": "x",
            "supporting_evidence": ["EV-CLEAN-001"], "contradicting_evidence": [], "status": "supported",
        })
        response = ka.find_gaps(tmp_path, "clean")
        assert response.status == "empty"
        assert response.gaps == []

    def test_dangling_evidence_reference_detected_corpus_wide(self, tmp_path):
        """find_gaps and trace_evidence use consistent semantics
        (corrective pass, decisions/0092) -- a dangling citation is
        detected scanning the whole corpus, not only when the citing
        record is itself the subject of a direct trace_evidence call."""
        slug_dir = tmp_path / "planning" / "knowledge" / "dangling-demo"
        _write_flat(slug_dir / "CL-DANGLE-002.yaml", {
            "id": "CL-DANGLE-002", "kind": "claim", "statement": "x",
            "supporting_evidence": ["EV-GHOST-001"], "status": "supported",
        })
        response = ka.find_gaps(tmp_path, "dangling-demo")
        assert response.status == "gap"
        dangling = [g for g in response.gaps if g.kind == "dangling_evidence_reference"]
        assert any(g.subject_id == "CL-DANGLE-002" and "EV-GHOST-001" in g.reason for g in dangling)

    def test_no_obligations_no_contract_is_not_a_gap(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "obs-only"
        _write_flat(slug_dir / "OBS-ONLY-001.yaml", {
            "id": "OBS-ONLY-001", "kind": "observation", "method": "source_read",
            "what_was_done": "x", "status": "recorded",
        })
        response = ka.find_gaps(tmp_path, "obs-only")
        assert response.status == "empty"

    @requires_ledgerkit
    def test_real_corpus_surfaces_the_known_stale_test_citation(self):
        """A genuine, pre-existing finding in this project's own real
        corpus (not staged for this test): `EV-BFS-002`/`EV-BFS-003` each
        cite a historical result file whose `oracle_contract_content_hash`
        no longer matches the live, three-check `oracle-contract.yaml`
        (extended by Phase 83) -- while a different, later, currently-
        passing result for the very same check_id exists, uncited, in the
        same `results/` directory. Confirms `find_gaps` genuinely detects
        this real condition, not only a constructed one."""
        response = ka.find_gaps(REPO_ROOT, "balance-from-spec")
        assert response.status == "gap"
        stale = [g for g in response.gaps if g.kind == "stale_test_citation"]
        assert {g.subject_id for g in stale} >= {"EV-BFS-002", "EV-BFS-003"}


# ---------------------------------------------------------------------------
# get_context_packet()
# ---------------------------------------------------------------------------


class TestContextPacket:
    def test_bounded_and_deterministic(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        first = ka.get_context_packet(tmp_path, "REQ-DEMO-001")
        second = ka.get_context_packet(tmp_path, "REQ-DEMO-001")
        assert first.results[0].details["items"] == second.results[0].details["items"]

    def test_max_items_enforced_and_reported(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        response = ka.get_context_packet(tmp_path, "REQ-DEMO-001", max_items=1)
        packet = response.results[0].details
        assert len(packet["items"]) <= 1
        assert packet["bounds"]["truncated"] is True

    def test_unknown_topic_is_empty(self, tmp_path):
        assert ka.get_context_packet(tmp_path, "nothing-matches-this-zzz").status == "empty"

    def test_gaps_included_for_subject(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        _write_flat(slug_dir / "CL-BARE-001.yaml", {
            "id": "CL-BARE-001", "kind": "claim", "statement": "unsupported claim text", "status": "proposed",
        })
        response = ka.get_context_packet(tmp_path, "CL-BARE-001")
        packet = response.results[0].details
        assert packet["gaps"]
        assert packet["gaps"][0]["kind"] == "missing_evidence"

    # -- Corrective pass defect C: bounds must apply to every retrieval
    # path, including a free-text topic resolving to a non-knowledge-record
    # item (decisions/0092).

    def _write_lone_contract(self, tmp_path):
        """A slug with an oracle contract and no knowledge records at all,
        whose check_id/scope text appears nowhere else in the corpus --
        guarantees search()'s first hit for that text is the oracle check
        itself, not a knowledge record."""
        contract_path = tmp_path / "planning" / "contracts" / "ctxtest" / "oracle-contract.yaml"
        _write_contract(
            contract_path, contract_id="REQ-CTXTEST-001",
            check_id="unique-check-xyz", scope="unique scope xyz for context bounds",
        )

    def test_non_knowledge_record_topic_is_bounded_by_max_chars(self, tmp_path):
        self._write_lone_contract(tmp_path)
        response = ka.get_context_packet(tmp_path, "unique-check-xyz", max_chars=1)
        packet = response.results[0].details
        assert packet["items"] == []
        assert packet["bounds"]["truncated"] is True

    def test_non_knowledge_record_topic_is_bounded_by_max_items(self, tmp_path):
        self._write_lone_contract(tmp_path)
        response = ka.get_context_packet(tmp_path, "unique-check-xyz", max_items=1)
        packet = response.results[0].details
        assert len(packet["items"]) == 1
        assert packet["bounds"]["truncated"] is False

    def test_non_knowledge_record_topic_fits_within_generous_bounds(self, tmp_path):
        self._write_lone_contract(tmp_path)
        response = ka.get_context_packet(tmp_path, "unique-check-xyz")
        packet = response.results[0].details
        assert len(packet["items"]) == 1
        assert packet["items"][0]["kind"] == "oracle_check"
        assert packet["bounds"]["truncated"] is False

    def test_repeated_identical_requests_are_deterministic_for_non_knowledge_record_topic(self, tmp_path):
        self._write_lone_contract(tmp_path)
        first = ka.get_context_packet(tmp_path, "unique-check-xyz")
        second = ka.get_context_packet(tmp_path, "unique-check-xyz")
        assert first.results[0].details["items"] == second.results[0].details["items"]


# ---------------------------------------------------------------------------
# export_snapshot()
# ---------------------------------------------------------------------------


class TestExportSnapshot:
    def test_writes_portable_envelope_with_identity_and_revision(self, tmp_path):
        _write_minimal_slug(tmp_path, "demo")
        out_path = tmp_path / "exports" / "demo.json"
        response = ka.export_snapshot(tmp_path, "demo", out_path, project_id="demo-project")
        assert response.status == "result"
        payload = json.loads(out_path.read_text())
        assert payload["project_id"] == "demo-project"
        assert payload["knowledge_schema_version"] == 1
        assert "exported_at" in payload
        assert payload["revision"]["scheme"] in ("git-commit", "unknown")
        assert "REQ-DEMO-001" in payload["records"]
        assert payload["contract"]["contract_id"] == "REQ-DEMO-001"
        assert len(payload["results"]) == 1

    def test_empty_slug_reports_empty(self, tmp_path):
        response = ka.export_snapshot(tmp_path, "no-such-slug", tmp_path / "out.json")
        assert response.status == "empty"
        assert not (tmp_path / "out.json").exists()


# ---------------------------------------------------------------------------
# Real-corpus dogfood demonstration (plan §8/§6's "required dogfood")
# ---------------------------------------------------------------------------


@requires_ledgerkit
class TestRealCorpusDogfoodDemonstration:
    """A fresh consumer, using only knowledge_api.py, retrieves and
    connects DEC-BFS-001 -> REQ-BFS-001 -> balance_from_spec's real
    implementation evidence -> the Phase 82 behavioural contract -> real
    oracle results -> provenance -> the still-outstanding overlapping-
    pattern limitation -- verifying each hop's own epistemic
    classification against the underlying canonical evidence directly,
    never merely asserting the API "works" or displaying records in
    isolation."""

    def test_architectural_intent_to_obligation(self):
        decision = ka.get(REPO_ROOT, "DEC-BFS-001")
        assert decision.status == "result"
        assert decision.results[0].authority == ka.AUTHORITY_STATED_INTENT

        requirement_response = ka.traverse(REPO_ROOT, "DEC-BFS-001", "decision_reverse")
        assert requirement_response.status == "result"
        assert [r.id for r in requirement_response.results] == ["REQ-BFS-001"]
        assert requirement_response.results[0].authority == ka.AUTHORITY_ACCEPTED_OBLIGATION

        # Independently verify against the real record, not the API's own
        # claim about itself.
        real_requirement = ki.load_slug_records(
            ki.slug_dir(REPO_ROOT, "balance-from-spec")
        )["REQ-BFS-001"]
        assert real_requirement.fields.get("decision") == "DEC-BFS-001"

    def test_obligation_to_implementation_evidence_and_real_source(self):
        claims_response = ka.traverse(REPO_ROOT, "REQ-BFS-001", "depends_on")
        claim_ids = {r.id for r in claims_response.results}
        assert claim_ids == {"CL-BFS-001", "CL-BFS-002", "CL-BFS-003"}

        evidence_response = ka.trace_evidence(REPO_ROOT, "CL-BFS-001")
        assert evidence_response.status == "result"
        evidence_ids = {r.id for r in evidence_response.results}
        assert "EV-BFS-001" in evidence_ids

        cites_response = ka.traverse(REPO_ROOT, "EV-BFS-001", "cites")
        source_refs = [r for r in cites_response.results if r.kind == "source_ref"]
        assert source_refs
        assert "ledgerkit/reports.py:600" in source_refs[0].details["raw"]

        # Resolve the real symbol this Evidence cites, against Ledgerkit's
        # own real, unmodified context-graph.db -- a second, independent
        # project_root, read-only.
        symbol_response = ka.get(
            LEDGERKIT_ROOT, ka.symbol_identity("ledgerkit/reports.py", "balance_from_spec", "function", 600)
        )
        assert symbol_response.status == "result"
        assert symbol_response.results[0].authority == ka.AUTHORITY_DERIVED_INDEX

    def test_contract_and_real_passing_oracle_results(self):
        contract_response = ka.get(REPO_ROOT, "contract:REQ-BFS-001")
        assert contract_response.status == "result"
        contract_details = contract_response.results[0].details
        assert set(contract_details["checks"]) == {
            "single-section-expense-subtotal",
            "multi-section-income-expense-subtotal",
            "overlapping-account-patterns-no-double-count",
        }

        results_response = ka.traverse(
            REPO_ROOT, "check:REQ-BFS-001:single-section-expense-subtotal", "results"
        )
        assert results_response.status == "result"
        current_passes = [
            r for r in results_response.results
            if r.details["effective_outcome"] == "PASS"
        ]
        assert current_passes, "expected at least one currently-effective PASS result"
        for r in current_passes:
            assert r.authority == ka.AUTHORITY_SCOPED_VERIFICATION

        # Independently verify against a direct, non-API recomputation.
        contract_path = REPO_ROOT / "planning" / "contracts" / "balance-from-spec" / "oracle-contract.yaml"
        contract = oracle.parse_oracle_contract(contract_path)
        check = contract.check_by_id("single-section-expense-subtotal")
        independently_confirmed_pass = False
        for result_path in sorted(
            (REPO_ROOT / "planning" / "contracts" / "balance-from-spec" / "results").glob(
                "single-section-expense-subtotal--*.yaml"
            )
        ):
            result = oracle.parse_oracle_result(result_path)
            outcome, _ = oracle.evaluate_result_precedence(result, contract, check, contract_path=contract_path)
            if outcome == "PASS":
                independently_confirmed_pass = True
        assert independently_confirmed_pass

    def test_known_verification_limitation_overlapping_pattern_check(self):
        gaps_response = ka.find_gaps(REPO_ROOT, "balance-from-spec")
        gap_scopes = {g.scope for g in gaps_response.gaps if g.kind == "unverified_required_scope"}
        assert any("OR-combined" in (scope or "") for scope in gap_scopes)

        # Independently verify: the overlapping-pattern check really has
        # zero results of any kind on disk.
        results_dir = REPO_ROOT / "planning" / "contracts" / "balance-from-spec" / "results"
        overlapping_results = [
            p for p in results_dir.glob("*.yaml")
            if oracle.parse_oracle_result(p).check_id == "overlapping-account-patterns-no-double-count"
        ]
        assert overlapping_results == []

    def test_intent_observation_and_verification_remain_visibly_distinct(self):
        """The governing principle, directly: for REQ-BFS-001, `stated_
        intent` (the Decision), `accepted_obligation` (the Requirement),
        and `scoped_verification` (a real oracle PASS) are three separate,
        independently retrievable items -- never collapsed into one
        "verified" answer, and a historical PASS never silently implies
        current verification without passing through `evaluate_result_
        precedence` first."""
        decision = ka.get(REPO_ROOT, "DEC-BFS-001").results[0]
        requirement = ka.get(REPO_ROOT, "REQ-BFS-001").results[0]
        results_response = ka.traverse(
            REPO_ROOT, "check:REQ-BFS-001:single-section-expense-subtotal", "results"
        )
        authorities = {decision.authority, requirement.authority, *(r.authority for r in results_response.results)}
        assert authorities == {
            ka.AUTHORITY_STATED_INTENT, ka.AUTHORITY_ACCEPTED_OBLIGATION, ka.AUTHORITY_SCOPED_VERIFICATION,
        }
        # At least one real historical result is recorded PASS but
        # currently INVALID (hash drift after the contract's own later
        # extension) -- confirming the module never treats "recorded
        # outcome" and "effective outcome" as interchangeable.
        assert any(
            r.details["outcome"] == "PASS" and r.details["effective_outcome"] == "INVALID"
            for r in results_response.results
        )
