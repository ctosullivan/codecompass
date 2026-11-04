"""Tests for scripts/check_doc_schema.py (Phase 87 documentation-schema
validator). Mirrors scripts/check_contracts.py's own Finding/--strict
convention. See
planning/phase-87-documentation-schema-knowledge-compiled-documentation.md
§B for the schema format this validates.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT / "scripts" / "check_doc_schema.py"

_spec = importlib.util.spec_from_file_location("check_doc_schema", SCRIPT_PATH)
check_doc_schema = importlib.util.module_from_spec(_spec)
sys.modules["check_doc_schema"] = check_doc_schema
_spec.loader.exec_module(check_doc_schema)


def _write_flat_record(
    path: Path, record_id: str, kind: str = "claim", status: str = "supported"
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"id: {record_id}\nkind: {kind}\nstatement: demo statement for {record_id}\n"
        f"supporting_evidence: []\ncontradicting_evidence: []\nstatus: {status}\n",
        encoding="utf-8",
    )


def _write_schema(path: Path, **overrides) -> dict:
    # Stage 87A's own minimal schema shape (plan §B, restructuring-pass
    # correction) -- flat per-section fields, no `evidence_requirements`
    # nesting, `citation_display` not `provenance`, no 87B/87C-only
    # fields (`verification_method`, `requires_tested_example`) required.
    base = {
        "schema_version": 1,
        "document": "docs/demo.md",
        "audience": "a developer new to the project",
        "sections": [{
            "id": "s1",
            "required_knowledge": ["CL-SCHEMADEMO-001"],
            "max_evidence_chars": 4000,
            "depth": "brief",
            "tone": "instructional",
            "min_claim_status": "supported",
            "allow_unconfirmed_scopes": False,
            "citation_display": "none",
        }],
        "acceptance_criteria": ["An unfamiliar developer understands the purpose."],
        "owner": "lead",
    }
    base.update(overrides)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
    return base


@pytest.fixture
def project(tmp_path):
    _write_flat_record(
        tmp_path / "planning" / "knowledge" / "schemademo" / "CL-SCHEMADEMO-001.yaml",
        "CL-SCHEMADEMO-001",
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_well_formed_schema_produces_no_blocking_findings(project):
    schema_path = project / "docs" / "demo.schema.yaml"
    _write_schema(schema_path)
    findings = check_doc_schema.run_all(project, [schema_path])
    assert not [f for f in findings if f.strict]


# ---------------------------------------------------------------------------
# Document-path confinement (hardening pass §N.B): schema-validation-time
# half of `doc_compiler.resolve_publication_target` -- the publish-time
# half is already covered directly in tests/test_cli.py.
# ---------------------------------------------------------------------------


def test_traversal_document_path_is_blocking(project):
    schema_path = project / "docs" / "demo.schema.yaml"
    _write_schema(schema_path, document="../outside.md")
    findings = check_doc_schema.run_all(project, [schema_path])
    assert any(f.strict and f.rule == "doc-schema-unsafe-document-path" for f in findings)


def test_absolute_document_path_is_blocking(project):
    schema_path = project / "docs" / "demo.schema.yaml"
    _write_schema(schema_path, document="/etc/evil.md")
    findings = check_doc_schema.run_all(project, [schema_path])
    assert any(f.strict and f.rule == "doc-schema-unsafe-document-path" for f in findings)


def test_document_path_outside_approved_targets_is_blocking(project):
    schema_path = project / "docs" / "demo.schema.yaml"
    _write_schema(schema_path, document="CONTRIBUTING.md")
    findings = check_doc_schema.run_all(project, [schema_path])
    assert any(f.strict and f.rule == "doc-schema-unsafe-document-path" for f in findings)


def test_legitimate_readme_document_path_produces_no_path_finding(project):
    schema_path = project / "README.md.schema.yaml"
    _write_schema(schema_path, document="README.md")
    findings = check_doc_schema.run_all(project, [schema_path])
    assert not any(f.rule == "doc-schema-unsafe-document-path" for f in findings)


# ---------------------------------------------------------------------------
# Required fields / enum validation
# ---------------------------------------------------------------------------


def test_missing_required_top_level_field_is_blocking(project):
    schema_path = project / "docs" / "demo.schema.yaml"
    data = _write_schema(schema_path)
    del data["acceptance_criteria"]
    schema_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    findings = check_doc_schema.run_all(project, [schema_path])
    assert any(f.strict and f.rule == "doc-schema-missing-field" for f in findings)


def test_unknown_schema_version_is_blocking_fail_closed(project):
    schema_path = project / "docs" / "demo.schema.yaml"
    _write_schema(schema_path, schema_version=999)
    findings = check_doc_schema.run_all(project, [schema_path])
    assert any(f.strict and f.rule == "doc-schema-unknown-version" for f in findings)


def test_invalid_min_claim_status_is_blocking(project):
    schema_path = project / "docs" / "demo.schema.yaml"
    data = _write_schema(schema_path)
    data["sections"][0]["min_claim_status"] = "extremely-sure"
    schema_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    findings = check_doc_schema.run_all(project, [schema_path])
    assert any(f.strict and f.rule == "doc-schema-invalid-min-claim-status" for f in findings)


def test_requires_tested_example_without_comparison_mode_is_blocking(project):
    schema_path = project / "docs" / "demo.schema.yaml"
    data = _write_schema(schema_path)
    data["sections"][0]["requires_tested_example"] = True
    schema_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    findings = check_doc_schema.run_all(project, [schema_path])
    assert any(f.strict and f.rule == "doc-schema-missing-comparison-mode" for f in findings)


# ---------------------------------------------------------------------------
# required_knowledge resolution (amendment finding A)
# ---------------------------------------------------------------------------


def test_concrete_id_that_does_not_resolve_is_blocking(project):
    schema_path = project / "docs" / "demo.schema.yaml"
    data = _write_schema(schema_path)
    data["sections"][0]["required_knowledge"] = ["CL-DOES-NOT-EXIST"]
    schema_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    findings = check_doc_schema.run_all(project, [schema_path])
    assert any(f.strict and f.rule == "doc-schema-unresolved-record-id" for f in findings)


def test_discover_query_resolving_to_exactly_one_record_is_rewritten_in_place(project):
    schema_path = project / "docs" / "demo.schema.yaml"
    data = _write_schema(schema_path)
    data["sections"][0]["required_knowledge"] = ["discover:demo statement"]
    schema_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    findings = check_doc_schema.run_all(project, [schema_path])
    assert not [f for f in findings if f.strict]

    rewritten = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    assert rewritten["sections"][0]["required_knowledge"] == ["CL-SCHEMADEMO-001"]


def test_discover_query_resolving_to_zero_records_is_blocking(project):
    schema_path = project / "docs" / "demo.schema.yaml"
    data = _write_schema(schema_path)
    data["sections"][0]["required_knowledge"] = ["discover:nothing matches this at all"]
    schema_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    findings = check_doc_schema.run_all(project, [schema_path])
    assert any(f.strict and f.rule == "doc-schema-ambiguous-discover-query" for f in findings)


def test_discover_query_resolving_to_multiple_records_is_blocking_never_guesses(project):
    _write_flat_record(
        project / "planning" / "knowledge" / "schemademo" / "CL-SCHEMADEMO-002.yaml",
        "CL-SCHEMADEMO-002",
    )
    schema_path = project / "docs" / "demo.schema.yaml"
    data = _write_schema(schema_path)
    data["sections"][0]["required_knowledge"] = ["discover:demo statement"]
    schema_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    findings = check_doc_schema.run_all(project, [schema_path])
    assert any(f.strict and f.rule == "doc-schema-ambiguous-discover-query" for f in findings)
    # Never silently guesses via the first match -- the file is untouched.
    unchanged = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    assert unchanged["sections"][0]["required_knowledge"] == ["discover:demo statement"]


# ---------------------------------------------------------------------------
# document path uniqueness across schema files
# ---------------------------------------------------------------------------


def test_duplicate_document_path_across_schemas_is_blocking(project):
    schema_a = project / "docs" / "a.schema.yaml"
    schema_b = project / "docs" / "b.schema.yaml"
    _write_schema(schema_a, document="docs/same.md")
    _write_schema(schema_b, document="docs/same.md")
    findings = check_doc_schema.run_all(project, [schema_a, schema_b])
    assert any(f.strict and f.rule == "doc-schema-duplicate-document-path" for f in findings)


# ---------------------------------------------------------------------------
# CLI --files (mirrors the Phase 86 nargs="+" precedent -- L-... finding B)
# ---------------------------------------------------------------------------


def test_cli_rejects_explicit_empty_files_selection():
    with pytest.raises(SystemExit) as exc_info:
        check_doc_schema.main(["--files"])
    assert exc_info.value.code == 2


def test_dotted_section_id_is_blocking_amendment_finding_a(project):
    # Amendment finding A (restructuring pass, §G.A): a dotted id would
    # silently truncate at the real region-id parser -- confirmed by
    # direct execution against knowledge_intermediate._REGION_ID_RE.
    schema_path = project / "docs" / "demo.schema.yaml"
    data = _write_schema(schema_path)
    data["sections"][0]["id"] = "readme.install"
    schema_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    findings = check_doc_schema.run_all(project, [schema_path])
    assert any(f.strict and f.rule == "doc-schema-invalid-section-id" for f in findings)


def test_invalid_citation_display_is_blocking(project):
    schema_path = project / "docs" / "demo.schema.yaml"
    data = _write_schema(schema_path)
    data["sections"][0]["citation_display"] = "on_demand"  # dropped value, §G.C
    schema_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    findings = check_doc_schema.run_all(project, [schema_path])
    assert any(f.strict and f.rule == "doc-schema-invalid-citation-display" for f in findings)


def test_minimal_87a_schema_without_87b_87c_only_fields_is_not_blocking(project):
    # The exact regression the restructuring-pass review caught: §B's
    # own minimal schema example must actually pass this validator.
    schema_path = project / "docs" / "demo.schema.yaml"
    _write_schema(schema_path)  # no verification_method, no requires_tested_example
    findings = check_doc_schema.run_all(project, [schema_path])
    assert not [f for f in findings if f.strict]
