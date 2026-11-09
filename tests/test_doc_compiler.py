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


# ---------------------------------------------------------------------------
# compile_document -- orchestration (gap/citation blocking, pending review)
# ---------------------------------------------------------------------------


def _schema(**overrides) -> dict:
    base = {
        "schema_version": 1,
        "document": "docs/demo.md",
        "sections": [{
            "id": "s1",
            "audience": "a new developer",
            "tone": "instructional",
            "depth": "brief",
            "required_knowledge": ["CL-DOCDEMO-001"],
            "max_evidence_chars": 100_000,
            "min_claim_status": "supported",
            "allow_unconfirmed_scopes": False,
        }],
    }
    base.update(overrides)
    return base


def test_compile_document_blocks_section_on_gap_without_calling_composer(tmp_path):
    _make_fixture_repo(tmp_path, min_record_status="candidate")
    schema = _schema()
    schema["sections"][0]["min_claim_status"] = "verified"
    called = {"composer": False}

    def _composer(section, packet):
        called["composer"] = True
        return "never reached", []

    results = dc.compile_document(
        tmp_path, schema, repo_root=tmp_path, compose_and_validate=_composer,
    )
    assert results[0].status == "gap_blocked"
    assert called["composer"] is False


def test_compile_document_blocks_on_unsupported_citation(tmp_path):
    _make_fixture_repo(tmp_path)
    schema = _schema()

    def _composer(section, packet):
        text = "A fact {{cite:CL-DOCDEMO-002}}."
        return dc.strip_citation_tags(text).strip(), dc.validate_section_citations(text, packet)

    results = dc.compile_document(
        tmp_path, schema, repo_root=tmp_path, compose_and_validate=_composer,
    )
    assert results[0].status == "citation_blocked"


def test_compile_document_reaches_pending_review_when_all_citations_supported(tmp_path):
    _make_fixture_repo(tmp_path)
    schema = _schema()

    def _composer(section, packet):
        text = "A fact {{cite:CL-DOCDEMO-001}}."
        return dc.strip_citation_tags(text).strip(), dc.validate_section_citations(text, packet)

    results = dc.compile_document(
        tmp_path, schema, repo_root=tmp_path, compose_and_validate=_composer,
    )
    assert results[0].status == "pending_review"
    assert results[0].draft_body == "A fact."


# ---------------------------------------------------------------------------
# decide_publish_safety -- publication-time concurrency guard (Stage 87B
# §O.D point 3, third corrective amendment finding C)
# ---------------------------------------------------------------------------


def _finding(case: str, *, region_hash: str = "irrelevant", region_id: str = "demo-s1"):
    from codecompass import knowledge_intermediate as ki

    return ki.GroundedRegionFinding(
        doc_name="docs/demo.md", index=0, region_id=region_id,
        cited_ids=["CL-DEMO-001"], region_text="\nSome text\n",
        region_hash=region_hash, case=case,
    )


def test_decide_publish_safety_allows_when_no_finding_exists():
    assert dc.decide_publish_safety(None, "A fresh body.") is None


def test_decide_publish_safety_allows_noop():
    assert dc.decide_publish_safety(_finding("noop"), "A fresh body.") is None


def test_decide_publish_safety_allows_claims_changed():
    assert dc.decide_publish_safety(_finding("claims_changed"), "A fresh body.") is None


def test_decide_publish_safety_refuses_doc_candidate():
    reason = dc.decide_publish_safety(_finding("doc_candidate"), "A fresh body.")
    assert reason is not None
    assert "doc_candidate" in reason


def test_decide_publish_safety_refuses_concurrent_conflict():
    reason = dc.decide_publish_safety(_finding("concurrent_conflict"), "A fresh body.")
    assert reason is not None
    assert "concurrent_conflict" in reason


def test_decide_publish_safety_allows_new_when_live_content_matches_the_new_body():
    # The exact gap the third corrective amendment fixed: an unbaselined
    # ("new") region whose live content already IS the body about to be
    # published is a legitimate idempotent re-publish/baseline-catch-up.
    body = "A fresh body."
    matching_hash = oracle.sha256_text(f"\n{body}\n")
    finding = _finding("new", region_hash=matching_hash)
    assert dc.decide_publish_safety(finding, body) is None


def test_decide_publish_safety_refuses_new_when_live_content_does_not_match():
    # The exact gap the third corrective amendment fixed: an unbaselined
    # region whose live content is something ELSE entirely (e.g.
    # genuinely human-authored, never baselined) must never be assumed
    # safe to overwrite just because no baseline happens to exist yet.
    finding = _finding("new", region_hash=oracle.sha256_text("\nSome human-written text\n"))
    reason = dc.decide_publish_safety(finding, "A completely different fresh body.")
    assert reason is not None
    assert "does not match" in reason


# ---------------------------------------------------------------------------
# publish_section -- grounded-marker publication (amendment finding A/C --
# hyphenated region ids, always-on machine-readable grounding)
# ---------------------------------------------------------------------------


def test_publish_section_writes_grounded_marker_into_new_document(tmp_path):
    doc_path = tmp_path / "docs" / "demo.md"
    dc.publish_section(
        doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="A fact.",
    )
    text = doc_path.read_text(encoding="utf-8")
    assert "codecompass-grounded-by: CL-DOCDEMO-001 region:demo-s1" in text
    assert "A fact." in text


def test_publish_section_replaces_existing_region_in_place(tmp_path):
    doc_path = tmp_path / "docs" / "demo.md"
    dc.publish_section(
        doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="Old text.",
    )
    dc.publish_section(
        doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="New text.",
    )
    text = doc_path.read_text(encoding="utf-8")
    assert "New text." in text
    assert "Old text." not in text
    assert text.count("codecompass-grounded-by") == 2  # one open + one close comment, one region


def test_publish_section_rejects_region_id_outside_pattern(tmp_path):
    doc_path = tmp_path / "docs" / "demo.md"
    with pytest.raises(dc.DocCompilerError):
        dc.publish_section(
            doc_path, region_id="demo.s1", record_ids=["CL-DOCDEMO-001"], body="A fact.",
        )


def test_publish_section_marker_round_trips_through_parse_grounding_markers(tmp_path):
    from codecompass import knowledge_intermediate as ki

    doc_path = tmp_path / "docs" / "demo.md"
    dc.publish_section(doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="A fact.")
    parsed = ki.parse_grounding_markers(doc_path.read_text(encoding="utf-8"))
    assert len(parsed) == 1
    ids, body, region_id = parsed[0]
    assert ids == ["CL-DOCDEMO-001"]
    assert region_id == "demo-s1"
    assert "A fact." in body


# ---------------------------------------------------------------------------
# maintain_document -- five-state reconciliation (amendment finding E,
# restructuring-pass §A.3)
# ---------------------------------------------------------------------------


def test_maintain_document_new_region_establishes_baseline_without_regenerating_others(tmp_path):
    _make_fixture_repo(tmp_path)
    doc_path = tmp_path / "docs" / "demo.md"
    dc.publish_section(doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="A fact.")
    report = dc.maintain_document(tmp_path, ("docs/demo.md",))
    assert report.established_new == ["id:demo-s1"]


def test_maintain_document_detects_doc_candidate_for_human_edit_with_no_knowledge_change(tmp_path):
    _make_fixture_repo(tmp_path)
    doc_path = tmp_path / "docs" / "demo.md"
    dc.publish_section(doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="A fact.")
    dc.maintain_document(tmp_path, ("docs/demo.md",))  # establish baseline

    # Human hand-edits the section's own wording; no knowledge changed.
    dc.publish_section(
        doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="A hand-edited fact.",
    )
    report = dc.maintain_document(tmp_path, ("docs/demo.md",))
    assert report.doc_candidates == ["id:demo-s1"]
    # The hand-edit is preserved byte-for-byte -- maintain never
    # regenerates a doc_candidate section.
    assert "A hand-edited fact." in doc_path.read_text(encoding="utf-8")


def test_maintain_document_unrelated_sections_are_never_visited(tmp_path):
    _make_fixture_repo(tmp_path)
    doc_path = tmp_path / "docs" / "demo.md"
    dc.publish_section(doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="A fact.")
    dc.maintain_document(tmp_path, ("docs/demo.md",))
    before = doc_path.read_text(encoding="utf-8")

    report = dc.maintain_document(tmp_path, ("docs/demo.md",))
    assert report.noop == ["id:demo-s1"]
    assert doc_path.read_text(encoding="utf-8") == before


# ---------------------------------------------------------------------------
# strip_citation_tags -- no stray whitespace artifacts left behind (real
# defect found during Stage 87A's own live demonstration run)
# ---------------------------------------------------------------------------


def test_strip_citation_tags_leaves_no_space_before_following_punctuation():
    text = "A fact {{cite:CL-X}}. Another clause {{cite:CL-Y}}, continues here."
    stripped = dc.strip_citation_tags(text)
    assert stripped == "A fact. Another clause, continues here."


def test_strip_citation_tags_collapses_double_space_between_adjacent_tags():
    text = "First point {{cite:CL-X}} Second point {{cite:CL-Y}} here."
    stripped = dc.strip_citation_tags(text)
    assert "  " not in stripped
    assert stripped == "First point Second point here."


def test_strip_citation_tags_is_deterministic_across_repeated_calls():
    # Stage 87B post-closeout hardening, Finding A requirement 5: the
    # publishable body is derived from tagged_draft via this function
    # at publish time, not merely at compile time -- it must produce
    # byte-identical output every time it is run against the same input.
    text = "First {{cite:CL-X}}. Second {{cite:CL-Y}}, continues {{cite:CL-Z}}."
    results = {dc.strip_citation_tags(text) for _ in range(5)}
    assert len(results) == 1


# ---------------------------------------------------------------------------
# document_identity / publish_section's expected_document_identity --
# Stage 87B post-closeout hardening, Finding C: a compare-and-swap
# snapshot of the document's own exact content, checked immediately
# before the write.
# ---------------------------------------------------------------------------


def test_document_identity_is_absent_for_a_missing_file(tmp_path):
    assert dc.document_identity(tmp_path / "docs" / "nope.md") == "absent"


def test_document_identity_matches_a_fresh_hash_of_the_same_content(tmp_path):
    doc_path = tmp_path / "docs" / "demo.md"
    doc_path.parent.mkdir(parents=True)
    doc_path.write_text("hello\n", encoding="utf-8")
    assert dc.document_identity(doc_path) == oracle.sha256_text("hello\n")


def test_document_identity_changes_when_the_file_content_changes(tmp_path):
    doc_path = tmp_path / "docs" / "demo.md"
    doc_path.parent.mkdir(parents=True)
    doc_path.write_text("hello\n", encoding="utf-8")
    before = dc.document_identity(doc_path)
    doc_path.write_text("goodbye\n", encoding="utf-8")
    after = dc.document_identity(doc_path)
    assert before != after


def test_publish_section_accepts_a_matching_expected_document_identity(tmp_path):
    doc_path = tmp_path / "docs" / "demo.md"
    dc.publish_section(doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="Old.")
    identity = dc.document_identity(doc_path)
    dc.publish_section(
        doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="New.",
        expected_document_identity=identity,
    )
    assert "New." in doc_path.read_text(encoding="utf-8")


def test_publish_section_refuses_a_stale_expected_document_identity(tmp_path):
    # A snapshot taken before an intervening write must be refused --
    # the document's live identity no longer matches it.
    doc_path = tmp_path / "docs" / "demo.md"
    dc.publish_section(doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="Old.")
    stale_identity = dc.document_identity(doc_path)
    doc_path.write_text(doc_path.read_text(encoding="utf-8") + "\nan intervening edit\n")

    with pytest.raises(dc.DocPublishConflictError):
        dc.publish_section(
            doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="New.",
            expected_document_identity=stale_identity,
        )
    assert "an intervening edit" in doc_path.read_text(encoding="utf-8")
    assert "New." not in doc_path.read_text(encoding="utf-8")


def test_publish_section_accepts_expected_absent_for_a_genuinely_new_document(tmp_path):
    doc_path = tmp_path / "docs" / "demo.md"
    dc.publish_section(
        doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="New.",
        expected_document_identity="absent",
    )
    assert "New." in doc_path.read_text(encoding="utf-8")


def test_publish_section_refuses_expected_absent_when_the_file_now_exists(tmp_path):
    # The "new document" path has its own identity ("absent") -- a file
    # created in the gap between the caller's snapshot (taken when the
    # file genuinely did not exist) and the write must be refused the
    # same way a changed existing file is.
    doc_path = tmp_path / "docs" / "demo.md"
    doc_path.parent.mkdir(parents=True)
    doc_path.write_text("a file that appeared concurrently\n", encoding="utf-8")
    with pytest.raises(dc.DocPublishConflictError):
        dc.publish_section(
            doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="New.",
            expected_document_identity="absent",
        )
    assert doc_path.read_text(encoding="utf-8") == "a file that appeared concurrently\n"


def test_publish_section_atomic_write_leaves_the_original_intact_on_mid_write_failure(
    tmp_path, monkeypatch
):
    # Partial-write safety: a failure during the write must never leave
    # the target file truncated or corrupted, and must never leave a
    # stray temp file behind.
    doc_path = tmp_path / "docs" / "demo.md"
    dc.publish_section(doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="Old.")
    original = doc_path.read_text(encoding="utf-8")

    def _boom(*args, **kwargs):
        raise OSError("simulated crash during rename")

    monkeypatch.setattr(dc.os, "replace", _boom)
    with pytest.raises(OSError):
        dc.publish_section(
            doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="New.",
        )

    assert doc_path.read_text(encoding="utf-8") == original
    leftover_tmp_files = list(doc_path.parent.glob(f".{doc_path.name}.*.tmp"))
    assert leftover_tmp_files == []


def test_publish_section_preserves_unrelated_regions_through_an_atomic_rewrite(tmp_path):
    doc_path = tmp_path / "docs" / "demo.md"
    dc.publish_section(doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="First.")
    dc.publish_section(doc_path, region_id="demo-s2", record_ids=["CL-DOCDEMO-002"], body="Second.")
    before_s2 = doc_path.read_text(encoding="utf-8")
    assert "region:demo-s2" in before_s2

    identity = dc.document_identity(doc_path)
    dc.publish_section(
        doc_path, region_id="demo-s1", record_ids=["CL-DOCDEMO-001"], body="First, revised.",
        expected_document_identity=identity,
    )
    after = doc_path.read_text(encoding="utf-8")
    assert "First, revised." in after
    assert "Second." in after
    assert "region:demo-s2" in after


# ---------------------------------------------------------------------------
# Grounded-region identity: reordering and duplicate-id rejection
# (amendment finding A, governing task §7's "incorrect grounding ids")
# ---------------------------------------------------------------------------


def test_region_identity_survives_reordering_within_a_document(tmp_path):
    from codecompass import knowledge_intermediate as ki

    doc_path = tmp_path / "docs" / "demo.md"
    dc.publish_section(doc_path, region_id="demo-a", record_ids=["CL-DOCDEMO-001"], body="First.")
    dc.publish_section(doc_path, region_id="demo-b", record_ids=["CL-DOCDEMO-001"], body="Second.")

    # Physically reorder the two regions in the document.
    text = doc_path.read_text(encoding="utf-8")
    parts = text.strip().split("\n\n")
    assert len(parts) == 2
    doc_path.write_text("\n\n".join(reversed(parts)) + "\n", encoding="utf-8")

    parsed = ki.parse_grounding_markers(doc_path.read_text(encoding="utf-8"))
    region_ids = {region_id for _ids, _body, region_id in parsed}
    assert region_ids == {"demo-a", "demo-b"}
    # Each region's own body is still correctly associated with its own id,
    # not swapped by the reorder.
    by_id = {region_id: body for _ids, body, region_id in parsed}
    assert "Second." in by_id["demo-b"]
    assert "First." in by_id["demo-a"]


def test_duplicate_region_id_across_two_documents_is_rejected(tmp_path):
    from codecompass import knowledge_intermediate as ki

    doc_a = tmp_path / "docs" / "a.md"
    doc_b = tmp_path / "docs" / "b.md"
    dc.publish_section(doc_a, region_id="shared-id", record_ids=["CL-DOCDEMO-001"], body="A.")
    dc.publish_section(doc_b, region_id="shared-id", record_ids=["CL-DOCDEMO-001"], body="B.")

    with pytest.raises(ki.DuplicateGroundingRegionIdError):
        dc.maintain_document(tmp_path, ("docs/a.md", "docs/b.md"))
