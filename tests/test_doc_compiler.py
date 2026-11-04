"""Tests for codecompass.doc_compiler (Phase 87 -- Documentation Schema
and Knowledge-Compiled Documentation). See
planning/phase-87-documentation-schema-knowledge-compiled-documentation.md
§A.5/§C for the design this implements -- this module reads
knowledge_api only, never planning/knowledge/ directly, and never
re-derives currency/epistemic logic knowledge_api already provides.

Mirrors tests/test_knowledge_api.py's own tmp_path-as-fake-repo fixture
convention.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from codecompass import doc_compiler as dc
from codecompass import oracle


def _write_flat(path: Path, fields: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for key, value in fields.items():
        if isinstance(value, list):
            lines.append(f"{key}: [{', '.join(value)}]")
        else:
            lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_contract(
    path: Path, *, contract_id="REQ-DOCDEMO-001", check_id="chk-a", scope="scope A"
) -> None:
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
                "test_input_paths": ["tests/test_impl.py"], "required": True,
            }],
        }, sort_keys=False),
        encoding="utf-8",
    )


def _write_result(
    path: Path, contract_path: Path, *, contract_id="REQ-DOCDEMO-001", check_id="chk-a",
    scope="scope A", outcome="PASS", run_id="r1",
    tested_subject_digest: str, test_input_digest: str,
) -> None:
    import yaml

    path.parent.mkdir(parents=True, exist_ok=True)
    raw_output_path = path.with_suffix(".raw.txt")
    raw_output_path.write_text("1 passed\n", encoding="utf-8")
    path.write_text(
        yaml.safe_dump({
            "schema_version": 1,
            "run_id": run_id,
            "contract_id": contract_id,
            "check_id": check_id,
            "scope": scope,
            "baseline_id": "b1",
            "tested_subject_digest": tested_subject_digest,
            "oracle_contract_id": contract_id,
            "oracle_contract_content_hash": oracle.sha256_file(contract_path),
            "test_input_digest": test_input_digest,
            "raw_output_ref": str(raw_output_path),
            "raw_output_sha256": oracle.sha256_file(raw_output_path),
            "outcome": outcome,
            "executed_at": "2026-11-04T00:00:00Z",
            "execution_provider": "pytest",
        }, sort_keys=False),
        encoding="utf-8",
    )


def _make_fixture_repo(project_root: Path, *, min_record_status: str = "verified") -> Path:
    slug = "docdemo"
    slug_dir = project_root / "planning" / "knowledge" / slug
    contract_path = project_root / "planning" / "contracts" / slug / "oracle-contract.yaml"
    _write_contract(contract_path)
    result_path = project_root / "planning" / "contracts" / slug / "results" / "chk-a--r1.yaml"

    (project_root / "impl.py").write_text("def target():\n    return 1\n", encoding="utf-8")
    (project_root / "tests").mkdir(exist_ok=True)
    (project_root / "tests" / "test_impl.py").write_text(
        "def test_ok():\n    assert True\n", encoding="utf-8"
    )
    real_tested = oracle.compute_tree_digest(project_root, ["impl.py"])
    real_input = oracle.compute_tree_digest(project_root, ["tests/test_impl.py"])
    _write_result(
        result_path, contract_path, tested_subject_digest=real_tested, test_input_digest=real_input,
    )

    long_statement = (
        "This claim's statement is deliberately longer than two hundred "
        "and eighty characters so that a test can distinguish full "
        "hydration via knowledge_api.get()'s own details.fields path from "
        "knowledge_api.search()/get_context_packet()'s own 280-character "
        "truncated summary field -- if resolve_section_packet ever silently "
        "used the truncated summary instead of the real full field content, "
        "this exact sentence would be cut off well before this final clause "
        "closes it out, and a test asserting the full text survives intact "
        "would fail immediately, which is exactly the regression this "
        "fixture exists to catch."
    )
    assert len(long_statement) > 280

    _write_flat(slug_dir / "EV-DOCDEMO-001.yaml", {
        "id": "EV-DOCDEMO-001", "kind": "evidence", "evidence_kind": "test",
        "what_it_shows": "demo", "test_ref": f'"{result_path.relative_to(project_root)}"',
        "status": "current",
    })
    _write_flat(slug_dir / "CL-DOCDEMO-001.yaml", {
        "id": "CL-DOCDEMO-001", "kind": "claim", "statement": long_statement,
        "supporting_evidence": ["EV-DOCDEMO-001"], "contradicting_evidence": [],
        "basis": "observed_behaviour", "status": min_record_status,
    })
    _write_flat(slug_dir / "CL-DOCDEMO-002.yaml", {
        "id": "CL-DOCDEMO-002", "kind": "claim", "statement": "a second, unrelated claim",
        "supporting_evidence": [], "contradicting_evidence": [], "basis": "observed_behaviour",
        "status": "contradicted",
    })
    return project_root


# ---------------------------------------------------------------------------
# resolve_section_ids
# ---------------------------------------------------------------------------


def test_resolve_section_ids_returns_concrete_ids_unchanged():
    section = {"id": "s1", "required_knowledge": ["CL-DOCDEMO-001", "EV-DOCDEMO-001"]}
    assert dc.resolve_section_ids(section) == ["CL-DOCDEMO-001", "EV-DOCDEMO-001"]


def test_resolve_section_ids_rejects_unresolved_discover_entry():
    section = {"id": "s1", "required_knowledge": ["discover:something not yet resolved"]}
    with pytest.raises(dc.DocCompilerError):
        dc.resolve_section_ids(section)


def test_resolve_section_ids_empty_required_knowledge_is_the_minimal_content_edge_case():
    # CLAUDE.md §1 L-070: a fail-closed mechanism's own minimal-content
    # edge case -- a section declaring NO required knowledge at all is
    # well-formed enough to reach this function, which must not raise;
    # the resulting empty packet is find_section_gaps's concern (below),
    # not this function's.
    assert dc.resolve_section_ids({"id": "s1", "required_knowledge": []}) == []


# ---------------------------------------------------------------------------
# check_record_currency
# ---------------------------------------------------------------------------


def test_check_record_currency_reuses_consistency_envelope_current(tmp_path):
    _make_fixture_repo(tmp_path)
    status, reasons = dc.check_record_currency(tmp_path, "EV-DOCDEMO-001", repo_root=tmp_path)
    # evidence-kind record; the claim is the one asserting "current" below
    assert status in ("current", "unconfirmed")
    assert isinstance(reasons, list)


def test_check_record_currency_current_for_a_live_reconfirmed_claim(tmp_path):
    _make_fixture_repo(tmp_path)
    status, _reasons = dc.check_record_currency(tmp_path, "CL-DOCDEMO-001", repo_root=tmp_path)
    assert status == "current"


def test_check_record_currency_absent_for_nonexistent_record(tmp_path):
    _make_fixture_repo(tmp_path)
    status, reasons = dc.check_record_currency(tmp_path, "CL-DOES-NOT-EXIST", repo_root=tmp_path)
    assert status == "absent"
    assert reasons


# ---------------------------------------------------------------------------
# find_section_gaps
# ---------------------------------------------------------------------------


def test_find_section_gaps_empty_when_all_requirements_met(tmp_path):
    _make_fixture_repo(tmp_path, min_record_status="verified")
    section = {
        "id": "s1",
        "required_knowledge": ["CL-DOCDEMO-001"],
        "min_claim_status": "supported",
        "allow_unconfirmed_scopes": False,
    }
    gaps = dc.find_section_gaps(tmp_path, section, repo_root=tmp_path)
    assert gaps == []


def test_find_section_gaps_flags_record_below_min_claim_status(tmp_path):
    _make_fixture_repo(tmp_path, min_record_status="candidate")
    section = {
        "id": "s1",
        "required_knowledge": ["CL-DOCDEMO-001"],
        "min_claim_status": "verified",
        "allow_unconfirmed_scopes": False,
    }
    gaps = dc.find_section_gaps(tmp_path, section, repo_root=tmp_path)
    assert any(g.kind == "below_min_claim_status" and g.record_id == "CL-DOCDEMO-001" for g in gaps)


def test_find_section_gaps_flags_missing_required_knowledge(tmp_path):
    # The near-empty-content fail-closed edge case (L-070): a section
    # whose only required record simply does not exist must be reported
    # as a gap, never silently generated around.
    _make_fixture_repo(tmp_path)
    section = {"id": "s1", "required_knowledge": ["CL-DOES-NOT-EXIST"]}
    gaps = dc.find_section_gaps(tmp_path, section, repo_root=tmp_path)
    assert any(
        g.kind == "unresolved_required_knowledge" and g.record_id == "CL-DOES-NOT-EXIST"
        for g in gaps
    )


def test_find_section_gaps_flags_contradiction(tmp_path):
    _make_fixture_repo(tmp_path)
    section = {"id": "s1", "required_knowledge": ["CL-DOCDEMO-002"]}
    gaps = dc.find_section_gaps(tmp_path, section, repo_root=tmp_path)
    assert any(g.kind == "contradiction" and g.record_id == "CL-DOCDEMO-002" for g in gaps)


# ---------------------------------------------------------------------------
# resolve_section_packet -- the depth test: full hydration, never summary
# ---------------------------------------------------------------------------


def test_resolve_section_packet_hydrates_full_fields_not_truncated_summary(tmp_path):
    _make_fixture_repo(tmp_path)
    section = {"id": "s1", "required_knowledge": ["CL-DOCDEMO-001"], "max_evidence_chars": 100_000}
    packet = dc.resolve_section_packet(tmp_path, section, repo_root=tmp_path)
    full_statement = packet.hydrated["CL-DOCDEMO-001"]["statement"]
    assert len(full_statement) > 280
    assert full_statement.strip().endswith("exists to catch.")


def test_resolve_section_packet_raises_when_required_evidence_exceeds_budget(tmp_path):
    _make_fixture_repo(tmp_path)
    section = {"id": "s1", "required_knowledge": ["CL-DOCDEMO-001"], "max_evidence_chars": 10}
    with pytest.raises(dc.DocCompilerError):
        dc.resolve_section_packet(tmp_path, section, repo_root=tmp_path)


def test_resolve_section_packet_deduplicates_by_id(tmp_path):
    _make_fixture_repo(tmp_path)
    section = {
        "id": "s1",
        "required_knowledge": ["CL-DOCDEMO-001", "CL-DOCDEMO-001"],
        "max_evidence_chars": 100_000,
    }
    packet = dc.resolve_section_packet(tmp_path, section, repo_root=tmp_path)
    assert packet.record_ids.count("CL-DOCDEMO-001") == 1


# ---------------------------------------------------------------------------
# Citation-tag parsing and scope verification (§C step 7, points 1-2)
# ---------------------------------------------------------------------------


def test_parse_citation_tags_extracts_cited_ids_in_order():
    text = "Installation requires Python {{cite:CL-DOCDEMO-001}}. See also {{cite:EV-DOCDEMO-001}}."
    tags = dc.parse_citation_tags(text)
    assert [t.record_id for t in tags] == ["CL-DOCDEMO-001", "EV-DOCDEMO-001"]


def test_validate_section_citations_passes_when_all_citations_in_packet(tmp_path):
    _make_fixture_repo(tmp_path)
    section = {"id": "s1", "required_knowledge": ["CL-DOCDEMO-001"], "max_evidence_chars": 100_000}
    packet = dc.resolve_section_packet(tmp_path, section, repo_root=tmp_path)
    text = "A fact {{cite:CL-DOCDEMO-001}}."
    findings = dc.validate_section_citations(text, packet)
    assert all(f.classification != "unsupported" for f in findings)


def test_validate_section_citations_flags_citation_outside_packet(tmp_path):
    # The depth-not-scope test (L-075): CL-DOCDEMO-002 is a real record
    # in the project, but it was never resolved into THIS section's own
    # packet -- citing it must be rejected precisely because it is
    # outside what this section was permitted to use, not because it
    # doesn't exist anywhere.
    _make_fixture_repo(tmp_path)
    section = {"id": "s1", "required_knowledge": ["CL-DOCDEMO-001"], "max_evidence_chars": 100_000}
    packet = dc.resolve_section_packet(tmp_path, section, repo_root=tmp_path)
    text = "A fact {{cite:CL-DOCDEMO-002}}."
    findings = dc.validate_section_citations(text, packet)
    assert any(
        f.classification == "unsupported" and f.record_id == "CL-DOCDEMO-002" for f in findings
    )


def test_validate_section_citations_flags_citation_to_nonexistent_record(tmp_path):
    _make_fixture_repo(tmp_path)
    section = {"id": "s1", "required_knowledge": ["CL-DOCDEMO-001"], "max_evidence_chars": 100_000}
    packet = dc.resolve_section_packet(tmp_path, section, repo_root=tmp_path)
    text = "A fact {{cite:CL-TOTALLY-MADE-UP}}."
    findings = dc.validate_section_citations(text, packet)
    assert any(
        f.classification == "unsupported" and f.record_id == "CL-TOTALLY-MADE-UP" for f in findings
    )
