"""Tests for src/codecompass/knowledge_intermediate.py (Phase 81 —
persistent bidirectional intermediate knowledge layer). See
planning/phase-81-intermediate-knowledge-layer.md §16.1 for the required
acceptance-case list this file implements.

Unlike tests/test_check_knowledge_base.py (which imports its target by
file path, since scripts/ is deliberately not part of the installed
package), this module is shipped as part of `codecompass`, so it is
imported normally.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from codecompass import knowledge_intermediate as ki
from codecompass.cli import app

runner = CliRunner()

_CLAIM = """\
id: CL-DEMO-001
kind: claim
statement: >
  The sync pipeline is idempotent.
derivation: DE-DEMO-001
supporting_evidence: []
contradicting_evidence: []
derived_by: test
repository_revision: "working tree"
timestamp: "2026-10-07T00:00:00Z"
status: supported
supersedes: null
basis: observed_behaviour
"""

_DECISION_APPROVED = """\
id: DEC-DEMO-001
kind: decision
decides: use a new flag
rationale: because this is a test
supersedes: null
decided_by: human
timestamp: "2026-10-07T00:00:00Z"
status: approved
"""

_DECISION_PROPOSED = _DECISION_APPROVED.replace("status: approved", "status: proposed")


def _make_slug(tmp_path: Path, slug: str = "demo-slug", decision: str | None = None) -> Path:
    sdir = tmp_path / "planning" / "knowledge" / slug
    sdir.mkdir(parents=True)
    (sdir / "CL-DEMO-001.yaml").write_text(_CLAIM, encoding="utf-8")
    if decision:
        (sdir / "DEC-DEMO-001.yaml").write_text(decision, encoding="utf-8")
    return sdir


def _accept_all(manifest_path: Path) -> None:
    text = manifest_path.read_text(encoding="utf-8")
    text = text.replace('decision = "undecided"', 'decision = "accept"')
    manifest_path.write_text(text, encoding="utf-8")


def _edit_body(sdir: Path, old: str, new: str, filename: str = "overview.md") -> Path:
    path = sdir / "intermediate" / filename
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
    return path


def _set_record_status(yaml_path: Path, old_status: str, new_status: str) -> None:
    text = yaml_path.read_text(encoding="utf-8")
    text = text.replace(f"status: {old_status}", f"status: {new_status}")
    yaml_path.write_text(text, encoding="utf-8")


class TestNoOpRoundTrip:
    def test_render_no_edit_select_candidates_empty_rerender_identical(self, tmp_path):
        _make_slug(tmp_path)
        written = ki.render_slug(tmp_path, "demo-slug")
        snapshot = {p.name: p.read_text(encoding="utf-8") for p in written}

        anchors = ki.detect_anchor_changes(tmp_path, "demo-slug")
        assert all(a.case == "noop" for a in anchors)
        candidates = ki.detect_candidate_additions(tmp_path, "demo-slug")
        assert candidates == []
        manifest = ki.write_manifest(tmp_path, "demo-slug", anchors, candidates)
        assert manifest is None

        written_again = ki.render_slug(tmp_path, "demo-slug")
        for path in written_again:
            assert path.read_text(encoding="utf-8") == snapshot[path.name]


class TestProjectionOnlyEdit:
    def test_wording_change_with_unchanged_canonical_yields_candidate(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        _edit_body(sdir, "idempotent.", "idempotent, by design.")

        anchors = ki.detect_anchor_changes(tmp_path, "demo-slug")
        assert len(anchors) == 1
        assert anchors[0].canonical_changed is False
        assert anchors[0].projection_edited is True
        assert anchors[0].case == "candidate"


class TestCanonicalOnlyChange:
    def test_canonical_change_with_untouched_projection_is_safely_refreshed(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        (sdir / "CL-DEMO-001.yaml").write_text(
            _CLAIM.replace("idempotent", "idempotent (re-verified)"), encoding="utf-8"
        )

        anchors = ki.detect_anchor_changes(tmp_path, "demo-slug")
        assert len(anchors) == 1
        assert anchors[0].canonical_changed is True
        assert anchors[0].projection_edited is False
        assert anchors[0].case == "refresh"

        # No manifest entry needed -- a refresh is handled directly.
        manifest = ki.write_manifest(tmp_path, "demo-slug", anchors, [])
        assert manifest is None

        refreshed = ki.apply_automatic_refreshes(tmp_path, "demo-slug")
        assert refreshed == ["CL-DEMO-001"]
        overview = (sdir / "intermediate" / "overview.md").read_text(encoding="utf-8")
        assert "re-verified" in overview


class TestConcurrentChange:
    def test_neither_side_overwritten_and_apply_refuses(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        yaml_path = sdir / "CL-DEMO-001.yaml"
        yaml_before = yaml_path.read_text(encoding="utf-8")
        _set_record_status(yaml_path, "supported", "verified")
        overview_path = _edit_body(sdir, "idempotent.", "idempotent (human edit).")
        overview_before = overview_path.read_text(encoding="utf-8")

        anchors = ki.detect_anchor_changes(tmp_path, "demo-slug")
        assert len(anchors) == 1
        assert anchors[0].case == "concurrent_conflict"

        manifest_path = ki.write_manifest(tmp_path, "demo-slug", anchors, [])
        assert manifest_path is not None
        _accept_all(manifest_path)
        result = ki.apply_manifest(tmp_path, manifest_path)

        assert result.applied == []
        assert len(result.skipped) == 1
        assert "concurrent" in result.skipped[0].reason

        # Neither side was touched by detection or by the refused apply.
        assert yaml_path.read_text(encoding="utf-8") == yaml_before.replace(
            "status: supported", "status: verified"
        )
        assert overview_path.read_text(encoding="utf-8") == overview_before


class TestApplyTimeRace:
    def test_apply_rechecks_base_semantic_hash_and_fails_closed(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        _edit_body(sdir, "idempotent.", "idempotent, always.")

        anchors = ki.detect_anchor_changes(tmp_path, "demo-slug")
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", anchors, [])
        _accept_all(manifest_path)

        # The canonical record changes AFTER detection, BEFORE apply.
        yaml_path = sdir / "CL-DEMO-001.yaml"
        _set_record_status(yaml_path, "supported", "verified")

        result = ki.apply_manifest(tmp_path, manifest_path)
        assert result.applied == []
        assert "race" in result.skipped[0].reason
        # The race-triggering change is the only change present.
        assert "status: verified" in yaml_path.read_text(encoding="utf-8")


class TestPresentationIndependence:
    def test_canonical_record_untouched_and_wording_preserved_across_rerender(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        _edit_body(
            sdir,
            "The sync pipeline is idempotent.",
            "The sync pipeline can be run any number of times safely.",
        )

        anchors = ki.detect_anchor_changes(tmp_path, "demo-slug")
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", anchors, [])
        _accept_all(manifest_path)
        result = ki.apply_manifest(tmp_path, manifest_path)

        assert len(result.applied) == 1
        assert "untouched" in result.applied[0].reason
        yaml_after = (sdir / "CL-DEMO-001.yaml").read_text(encoding="utf-8")
        assert yaml_after == _CLAIM  # byte-identical -- never touched

        ki.render_slug(tmp_path, "demo-slug")
        overview = (sdir / "intermediate" / "overview.md").read_text(encoding="utf-8")
        assert "any number of times safely" in overview

    def test_different_presentations_in_different_docs_both_survive(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        _edit_body(sdir, "The sync pipeline is idempotent.", "Running sync twice changes nothing.")
        anchors = ki.detect_anchor_changes(tmp_path, "demo-slug")
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", anchors, [])
        _accept_all(manifest_path)
        ki.apply_manifest(tmp_path, manifest_path)

        # A second, independently-worded presentation of the same fact
        # (a grounded README region) is untouched by the cache update above.
        readme = tmp_path / "README.md"
        readme.write_text(
            "<!-- codecompass-grounded-by: CL-DEMO-001 -->\n"
            "Sync is safe to re-run as often as you like.\n"
            "<!-- /codecompass-grounded-by -->\n",
            encoding="utf-8",
        )
        hits = ki.find_grounded_doc_regions(tmp_path, "CL-DEMO-001")
        assert len(hits) == 1
        assert "safe to re-run" in hits[0][1]
        ki.render_slug(tmp_path, "demo-slug")
        overview = (sdir / "intermediate" / "overview.md").read_text(encoding="utf-8")
        assert "Running sync twice changes nothing." in overview
        assert "safe to re-run" in readme.read_text(encoding="utf-8")


class TestUnsupportedExternalAssertion:
    def test_no_fabricated_observation_or_evidence(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        overview_path = sdir / "intermediate" / "overview.md"
        text = overview_path.read_text(encoding="utf-8")
        text = text.replace(
            ki.CANDIDATE_START + ki.CANDIDATE_END,
            ki.CANDIDATE_START + "\nThe parser handles UTF-8 BOM markers.\n" + ki.CANDIDATE_END,
        )
        overview_path.write_text(text, encoding="utf-8")

        candidates = ki.detect_candidate_additions(tmp_path, "demo-slug")
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", [], candidates)
        _accept_all(manifest_path)
        result = ki.apply_manifest(tmp_path, manifest_path)

        assert len(result.applied) == 1
        new_id = result.applied[0].new_record_id
        records = ki.load_slug_records(sdir)
        new_record = records[new_id]
        assert new_record.kind == "claim"
        assert new_record.fields["status"] == "proposed"
        assert "evidence_support_state" not in new_record.fields

        fabricated = [rid for rid in records if rid.startswith(("OBS-", "EV-"))]
        assert fabricated == []


_VALID_REQUIREMENT_BLOCK = (
    "Type: Requirement\n"
    "Decision: DEC-DEMO-001\n"
    "Statement: The CLI must expose a --json flag for status output.\n"
    "Example: Given the status command runs with --json, when output is "
    "captured, then it is valid JSON.\n"
)


class TestRequirementInvariant:
    def test_mere_mention_of_approved_decision_does_not_create_requirement(self, tmp_path):
        """decisions/0073, point 6: ordinary prose merely mentioning an
        approved Decision id is never enough -- only an explicit
        `Type: Requirement` proposal may create one."""
        sdir = _make_slug(tmp_path, decision=_DECISION_APPROVED)
        ki.render_slug(tmp_path, "demo-slug")
        overview_path = sdir / "intermediate" / "overview.md"
        text = overview_path.read_text(encoding="utf-8")
        text = text.replace(
            ki.CANDIDATE_START + ki.CANDIDATE_END,
            ki.CANDIDATE_START
            + "\nPer DEC-DEMO-001, the CLI should expose a --json flag.\n"
            + ki.CANDIDATE_END,
        )
        overview_path.write_text(text, encoding="utf-8")

        candidates = ki.detect_candidate_additions(tmp_path, "demo-slug")
        assert candidates[0].requirement_decision is None
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", [], candidates)
        _accept_all(manifest_path)
        result = ki.apply_manifest(tmp_path, manifest_path)

        new_id = result.applied[0].new_record_id
        assert new_id.startswith("CL-")
        records = ki.load_slug_records(sdir)
        assert records[new_id].kind == "claim"

    def test_unapproved_decision_falls_back_to_claim(self, tmp_path):
        sdir = _make_slug(tmp_path, decision=_DECISION_PROPOSED)
        ki.render_slug(tmp_path, "demo-slug")
        overview_path = sdir / "intermediate" / "overview.md"
        text = overview_path.read_text(encoding="utf-8")
        text = text.replace(
            ki.CANDIDATE_START + ki.CANDIDATE_END,
            ki.CANDIDATE_START + "\n" + _VALID_REQUIREMENT_BLOCK + ki.CANDIDATE_END,
        )
        overview_path.write_text(text, encoding="utf-8")

        candidates = ki.detect_candidate_additions(tmp_path, "demo-slug")
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", [], candidates)
        _accept_all(manifest_path)
        result = ki.apply_manifest(tmp_path, manifest_path)

        new_id = result.applied[0].new_record_id
        assert new_id.startswith("CL-")
        records = ki.load_slug_records(sdir)
        assert records[new_id].kind == "claim"

    def test_explicit_proposal_with_approved_decision_may_create_requirement(self, tmp_path):
        sdir = _make_slug(tmp_path, decision=_DECISION_APPROVED)
        ki.render_slug(tmp_path, "demo-slug")
        overview_path = sdir / "intermediate" / "overview.md"
        text = overview_path.read_text(encoding="utf-8")
        text = text.replace(
            ki.CANDIDATE_START + ki.CANDIDATE_END,
            ki.CANDIDATE_START + "\n" + _VALID_REQUIREMENT_BLOCK + ki.CANDIDATE_END,
        )
        overview_path.write_text(text, encoding="utf-8")

        candidates = ki.detect_candidate_additions(tmp_path, "demo-slug")
        assert candidates[0].requirement_decision == "DEC-DEMO-001"
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", [], candidates)
        _accept_all(manifest_path)
        result = ki.apply_manifest(tmp_path, manifest_path)

        new_id = result.applied[0].new_record_id
        assert new_id.startswith("REQ-")
        records = ki.load_slug_records(sdir)
        assert records[new_id].kind == "requirement"
        assert records[new_id].fields["decision"] == "DEC-DEMO-001"
        assert "to be refined" not in records[new_id].fields["example"]

    def test_explicit_proposal_missing_acceptance_example_fails_closed(self, tmp_path):
        sdir = _make_slug(tmp_path, decision=_DECISION_APPROVED)
        ki.render_slug(tmp_path, "demo-slug")
        overview_path = sdir / "intermediate" / "overview.md"
        text = overview_path.read_text(encoding="utf-8")
        block = "Type: Requirement\nDecision: DEC-DEMO-001\nStatement: Needs a flag.\n"
        new_region = ki.CANDIDATE_START + "\n" + block + ki.CANDIDATE_END
        text = text.replace(ki.CANDIDATE_START + ki.CANDIDATE_END, new_region)
        overview_path.write_text(text, encoding="utf-8")

        candidates = ki.detect_candidate_additions(tmp_path, "demo-slug")
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", [], candidates)
        _accept_all(manifest_path)
        result = ki.apply_manifest(tmp_path, manifest_path)

        new_id = result.applied[0].new_record_id
        records = ki.load_slug_records(sdir)
        assert records[new_id].kind == "claim"


class TestCandidateRegionBoundary:
    def test_prose_outside_markers_is_never_a_candidate(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        overview_path = sdir / "intermediate" / "overview.md"
        text = overview_path.read_text(encoding="utf-8")
        # Add commentary right before the candidate region, outside it.
        text = text.replace(
            "## Candidate additions",
            "Some maintainer commentary about this section.\n\n## Candidate additions",
        )
        overview_path.write_text(text, encoding="utf-8")
        candidates = ki.detect_candidate_additions(tmp_path, "demo-slug")
        assert candidates == []

    def test_content_inside_markers_is_exactly_the_candidate(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        overview_path = sdir / "intermediate" / "overview.md"
        text = overview_path.read_text(encoding="utf-8")
        text = text.replace(
            ki.CANDIDATE_START + ki.CANDIDATE_END,
            ki.CANDIDATE_START + "\nA genuinely new fact.\n" + ki.CANDIDATE_END,
        )
        overview_path.write_text(text, encoding="utf-8")
        candidates = ki.detect_candidate_additions(tmp_path, "demo-slug")
        assert len(candidates) == 1
        assert candidates[0].text == "A genuinely new fact."


class TestExplicitDocumentGrounding:
    def test_claim_change_identifies_affected_readme_region_deterministically(self, tmp_path):
        _make_slug(tmp_path)
        readme = tmp_path / "README.md"
        readme.write_text(
            "<!-- codecompass-grounded-by: CL-DEMO-001 -->\n"
            "Sync is idempotent.\n"
            "<!-- /codecompass-grounded-by -->\n",
            encoding="utf-8",
        )
        hits = ki.find_grounded_doc_regions(tmp_path, "CL-DEMO-001")
        assert len(hits) == 1
        assert hits[0][0] == readme

    def test_grounded_region_change_identifies_cited_claim_ids(self, tmp_path):
        text = (
            "<!-- codecompass-grounded-by: CL-DEMO-001, REQ-DEMO-002 -->\n"
            "Some factual prose that just changed.\n"
            "<!-- /codecompass-grounded-by -->\n"
        )
        marked = ki.parse_grounding_markers(text)
        assert len(marked) == 1
        ids, region = marked[0]
        assert ids == ["CL-DEMO-001", "REQ-DEMO-002"]
        assert "just changed" in region


class TestGroundingCoverageAdvisory:
    def test_contradicted_grounded_record_surfaced_with_no_mutation(self, tmp_path):
        sdir = _make_slug(tmp_path)
        contradicted = _CLAIM.replace("status: supported", "status: contradicted")
        (sdir / "CL-DEMO-001.yaml").write_text(contradicted, encoding="utf-8")
        readme = tmp_path / "README.md"
        readme.write_text(
            "<!-- codecompass-grounded-by: CL-DEMO-001 -->\n"
            "Sync is idempotent.\n"
            "<!-- /codecompass-grounded-by -->\n",
            encoding="utf-8",
        )
        readme_before = readme.read_text(encoding="utf-8")
        claim_before = (sdir / "CL-DEMO-001.yaml").read_text(encoding="utf-8")

        report = ki.knowledge_status(tmp_path)
        assert "CL-DEMO-001" in report.grounding["README.md"]["regions_needing_review"]

        # Purely advisory -- nothing was mutated by computing the report.
        assert readme.read_text(encoding="utf-8") == readme_before
        assert (sdir / "CL-DEMO-001.yaml").read_text(encoding="utf-8") == claim_before


class TestThreeStageApplicationSafety:
    def test_proposal_is_not_authoritative_until_apply_runs(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        _edit_body(sdir, "idempotent.", "idempotent (edited).")
        yaml_path = sdir / "CL-DEMO-001.yaml"
        before_detect = yaml_path.read_text(encoding="utf-8")

        # Stage 1: detect.
        anchors = ki.detect_anchor_changes(tmp_path, "demo-slug")
        assert yaml_path.read_text(encoding="utf-8") == before_detect

        # Stage 2: a manifest exists, annotated (simulated review) -- still
        # not authoritative.
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", anchors, [])
        assert yaml_path.read_text(encoding="utf-8") == before_detect
        _accept_all(manifest_path)
        assert yaml_path.read_text(encoding="utf-8") == before_detect

        # Stage 3: only apply may change canonical knowledge.
        ki.apply_manifest(tmp_path, manifest_path)
        # This edit was wording-only -> presentation cache, canonical
        # record genuinely never changes even after apply.
        assert yaml_path.read_text(encoding="utf-8") == before_detect


class TestStableIdentityUnderReorganisation:
    def test_anchor_resolves_after_record_file_renamed(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        old_path = sdir / "CL-DEMO-001.yaml"
        new_path = sdir / "renamed-but-same-id.yaml"
        new_path.write_text(old_path.read_text(encoding="utf-8"), encoding="utf-8")
        old_path.unlink()

        anchors = ki.detect_anchor_changes(tmp_path, "demo-slug")
        assert len(anchors) == 1
        assert anchors[0].case == "noop"
        assert anchors[0].record_id == "CL-DEMO-001"


class TestDeriveProvenanceLabel:
    def test_observed_behaviour(self, tmp_path):
        sdir = _make_slug(tmp_path)
        records = ki.load_slug_records(sdir)
        assert ki.derive_provenance_label(records["CL-DEMO-001"], records) == "OBSERVED"

    def test_declared_policy(self, tmp_path):
        sdir = _make_slug(tmp_path)
        declared = _CLAIM.replace("basis: observed_behaviour", "basis: proposed_policy")
        (sdir / "CL-DEMO-001.yaml").write_text(declared, encoding="utf-8")
        records = ki.load_slug_records(sdir)
        assert ki.derive_provenance_label(records["CL-DEMO-001"], records) == "DECLARED"

    def test_derived_inferred(self, tmp_path):
        sdir = _make_slug(tmp_path)
        derived = _CLAIM.replace("basis: observed_behaviour", "basis: inferred")
        (sdir / "CL-DEMO-001.yaml").write_text(derived, encoding="utf-8")
        records = ki.load_slug_records(sdir)
        assert ki.derive_provenance_label(records["CL-DEMO-001"], records) == "DERIVED"

    def test_historical_supersedes_basis(self, tmp_path):
        sdir = _make_slug(tmp_path)
        historical = _CLAIM.replace("status: supported", "status: superseded")
        (sdir / "CL-DEMO-001.yaml").write_text(historical, encoding="utf-8")
        records = ki.load_slug_records(sdir)
        assert ki.derive_provenance_label(records["CL-DEMO-001"], records) == "HISTORICAL"

    def test_decision_is_declared(self, tmp_path):
        sdir = _make_slug(tmp_path, decision=_DECISION_APPROVED)
        records = ki.load_slug_records(sdir)
        assert ki.derive_provenance_label(records["DEC-DEMO-001"], records) == "DECLARED"

    def test_requirement_authorised_by_approved_decision_is_decided(self, tmp_path):
        sdir = _make_slug(tmp_path, decision=_DECISION_APPROVED)
        (sdir / "REQ-DEMO-001.yaml").write_text(
            "id: REQ-DEMO-001\nkind: requirement\nstatement: a requirement\n"
            "example: Given/When/Then\ndecision: DEC-DEMO-001\nstatus: proposed\n",
            encoding="utf-8",
        )
        records = ki.load_slug_records(sdir)
        assert ki.derive_provenance_label(records["REQ-DEMO-001"], records) == "DECIDED"

    def test_ambiguous_directly_stated_resolves_to_cautious_label(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ambiguous = _CLAIM.replace("basis: observed_behaviour", "basis: directly_stated")
        (sdir / "CL-DEMO-001.yaml").write_text(ambiguous, encoding="utf-8")
        records = ki.load_slug_records(sdir)
        # No supporting_evidence cited at all -- the cautious default.
        assert ki.derive_provenance_label(records["CL-DEMO-001"], records) == "DECLARED"


class TestPhaseBrief:
    """§5.2's own single entry point into a phase knowledge package --
    a mechanically-compiled index, not a separate representation of the
    same knowledge. Found missing (planned, never implemented) by the
    independent per-phase docs-drift audit and added here."""

    def test_render_slug_produces_phase_brief(self, tmp_path):
        _make_slug(tmp_path)
        written = ki.render_slug(tmp_path, "demo-slug")
        assert any(p.name == "phase-brief.md" for p in written)
        brief = (
            (tmp_path / "planning" / "knowledge" / "demo-slug" / "intermediate" / "phase-brief.md")
            .read_text(encoding="utf-8")
        )
        assert "CL-DEMO-001" in brief
        assert "## Candidate additions" in brief

    def test_no_records_no_brief(self, tmp_path):
        sdir = tmp_path / "planning" / "knowledge" / "empty-slug"
        sdir.mkdir(parents=True)
        assert ki.render_phase_brief(tmp_path, "empty-slug") is None

    def test_requirement_gets_its_own_line(self, tmp_path):
        sdir = _make_slug(tmp_path, decision=_DECISION_APPROVED)
        (sdir / "REQ-DEMO-001.yaml").write_text(
            "id: REQ-DEMO-001\nkind: requirement\nstatement: a requirement\n"
            "example: Given/When/Then\ndecision: DEC-DEMO-001\nstatus: proposed\n",
            encoding="utf-8",
        )
        ki.render_slug(tmp_path, "demo-slug")
        brief = (sdir / "intermediate" / "phase-brief.md").read_text(encoding="utf-8")
        assert "REQ-DEMO-001" in brief
        assert "tests-and-acceptance.md" in brief

    def test_candidate_region_preserved_across_rerender(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        brief_path = sdir / "intermediate" / "phase-brief.md"
        text = brief_path.read_text(encoding="utf-8")
        text = text.replace(
            ki.CANDIDATE_START + ki.CANDIDATE_END,
            ki.CANDIDATE_START + "\nnot yet processed\n" + ki.CANDIDATE_END,
        )
        brief_path.write_text(text, encoding="utf-8")
        ki.render_slug(tmp_path, "demo-slug")
        assert "not yet processed" in brief_path.read_text(encoding="utf-8")


class TestCLI:
    def test_render_select_candidates_status_via_cli(self, tmp_path, monkeypatch):
        _make_slug(tmp_path)
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["knowledge", "render", "demo-slug"])
        assert result.exit_code == 0
        assert "rendered 5 file(s)" in result.output

        result = runner.invoke(app, ["knowledge", "select-candidates", "demo-slug"])
        assert result.exit_code == 0
        assert "nothing to review" in result.output

        result = runner.invoke(app, ["knowledge", "status"])
        assert result.exit_code == 0
        assert "nothing to report" in result.output

    def test_apply_missing_manifest_errors(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["knowledge", "apply", "no-such-manifest.toml"])
        assert result.exit_code == 1
        assert "no such manifest" in result.output


# ---------------------------------------------------------------------------
# Corrective pass (decisions/0073) -- regression coverage for the nine
# defects found by post-completion review, plus the combination cases the
# original suite missed.
# ---------------------------------------------------------------------------

_DECISION_APPROVED_2 = _DECISION_APPROVED


def _make_two_record_slug(tmp_path: Path, slug: str = "demo-slug") -> Path:
    """Two Claims with no `assertion_kind`, so both land in the SAME
    rendered file (`overview.md`) -- required for the same-file
    safe-refresh/concurrent-conflict combination tests."""
    sdir = tmp_path / "planning" / "knowledge" / slug
    sdir.mkdir(parents=True)
    (sdir / "CL-A-001.yaml").write_text(
        "id: CL-A-001\nkind: claim\nstatement: Fact A original.\nderivation: null\n"
        "supporting_evidence: []\ncontradicting_evidence: []\nderived_by: t\n"
        'repository_revision: "working tree"\ntimestamp: "2026-10-07T00:00:00Z"\n'
        "status: supported\n",
        encoding="utf-8",
    )
    (sdir / "CL-B-001.yaml").write_text(
        "id: CL-B-001\nkind: claim\nstatement: Fact B original.\nderivation: null\n"
        "supporting_evidence: []\ncontradicting_evidence: []\nderived_by: t\n"
        'repository_revision: "working tree"\ntimestamp: "2026-10-07T00:00:00Z"\n'
        "status: supported\n",
        encoding="utf-8",
    )
    return sdir


class TestUnsafeRefreshCorrected:
    """decisions/0073, point 1: `select-candidates` must classify every
    anchor before any mutation, then refresh ONLY safe-refresh blocks --
    never a whole-slug render that could erase an unrelated pending edit."""

    def test_safe_refresh_a_plus_edited_b_same_file(self, tmp_path):
        sdir = _make_two_record_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        overview = sdir / "intermediate" / "overview.md"
        assert overview.read_text(encoding="utf-8").count("codecompass-knowledge:") == 2

        (sdir / "CL-A-001.yaml").write_text(
            (sdir / "CL-A-001.yaml").read_text(encoding="utf-8").replace(
                "Fact A original.", "Fact A UPDATED."
            ),
            encoding="utf-8",
        )
        overview.write_text(
            overview.read_text(encoding="utf-8").replace(
                "Fact B original.", "Fact B HUMAN EDIT."
            ),
            encoding="utf-8",
        )

        anchors = ki.detect_anchor_changes(tmp_path, "demo-slug")
        cases = {a.record_id: a.case for a in anchors}
        assert cases == {"CL-A-001": "refresh", "CL-B-001": "candidate"}

        refreshed = ki.refresh_safe_anchors(tmp_path, "demo-slug", anchors)
        assert refreshed == ["CL-A-001"]

        final_text = overview.read_text(encoding="utf-8")
        assert "Fact A UPDATED." in final_text
        assert "Fact B HUMAN EDIT." in final_text, "B's edit must survive byte-for-byte"

        manifest_path = ki.write_manifest(tmp_path, "demo-slug", anchors, [])
        manifest_text = manifest_path.read_text(encoding="utf-8")
        assert "CL-B-001" in manifest_text
        assert "CL-A-001" not in manifest_text

    def test_safe_refresh_a_plus_edited_b_different_files(self, tmp_path):
        sdir = tmp_path / "planning" / "knowledge" / "demo-slug"
        sdir.mkdir(parents=True)
        (sdir / "CL-A-001.yaml").write_text(
            "id: CL-A-001\nkind: claim\nstatement: Fact A.\nderivation: null\n"
            "supporting_evidence: []\ncontradicting_evidence: []\nderived_by: t\n"
            'repository_revision: "working tree"\ntimestamp: "2026-10-07T00:00:00Z"\n'
            "status: supported\nassertion_kind: invariant\n",
            encoding="utf-8",
        )
        (sdir / "CL-B-001.yaml").write_text(
            "id: CL-B-001\nkind: claim\nstatement: Fact B.\nderivation: null\n"
            "supporting_evidence: []\ncontradicting_evidence: []\nderived_by: t\n"
            'repository_revision: "working tree"\ntimestamp: "2026-10-07T00:00:00Z"\n'
            "status: supported\nassertion_kind: relationship\n",
            encoding="utf-8",
        )
        ki.render_slug(tmp_path, "demo-slug")
        invariants = sdir / "intermediate" / "invariants-and-constraints.md"
        behaviours = sdir / "intermediate" / "interfaces-and-behaviours.md"
        assert "CL-A-001" in invariants.read_text(encoding="utf-8")
        assert "CL-B-001" in behaviours.read_text(encoding="utf-8")

        (sdir / "CL-A-001.yaml").write_text(
            (sdir / "CL-A-001.yaml").read_text(encoding="utf-8").replace("Fact A.", "Fact A!"),
            encoding="utf-8",
        )
        behaviours.write_text(
            behaviours.read_text(encoding="utf-8").replace("Fact B.", "Fact B edited."),
            encoding="utf-8",
        )

        anchors = ki.detect_anchor_changes(tmp_path, "demo-slug")
        cases = {a.record_id: a.case for a in anchors}
        assert cases == {"CL-A-001": "refresh", "CL-B-001": "candidate"}
        ki.refresh_safe_anchors(tmp_path, "demo-slug", anchors)
        assert "Fact A!" in invariants.read_text(encoding="utf-8")
        assert "Fact B edited." in behaviours.read_text(encoding="utf-8")

    def test_safe_refresh_a_plus_concurrent_conflict_b(self, tmp_path):
        sdir = _make_two_record_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        overview = sdir / "intermediate" / "overview.md"

        (sdir / "CL-A-001.yaml").write_text(
            (sdir / "CL-A-001.yaml").read_text(encoding="utf-8").replace(
                "Fact A original.", "Fact A UPDATED."
            ),
            encoding="utf-8",
        )
        (sdir / "CL-B-001.yaml").write_text(
            (sdir / "CL-B-001.yaml").read_text(encoding="utf-8").replace(
                "status: supported", "status: verified"
            ),
            encoding="utf-8",
        )
        overview.write_text(
            overview.read_text(encoding="utf-8").replace(
                "Fact B original.", "Fact B HUMAN EDIT."
            ),
            encoding="utf-8",
        )

        anchors = ki.detect_anchor_changes(tmp_path, "demo-slug")
        cases = {a.record_id: a.case for a in anchors}
        assert cases == {"CL-A-001": "refresh", "CL-B-001": "concurrent_conflict"}

        before_refresh = overview.read_text(encoding="utf-8")
        ki.refresh_safe_anchors(tmp_path, "demo-slug", anchors)
        after_refresh = overview.read_text(encoding="utf-8")
        assert "Fact A UPDATED." in after_refresh
        assert "Fact B HUMAN EDIT." in after_refresh, "conflict block must never be rewritten"
        # Only A's own block should have changed between the two reads.
        assert "Fact B HUMAN EDIT." in before_refresh


class TestIdempotencyCombinations:
    """decisions/0073, point 2 and point 11's own combination cases."""

    def test_candidate_apply_then_detect_again_not_rediscovered(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        overview = sdir / "intermediate" / "overview.md"
        text = overview.read_text(encoding="utf-8")
        text = text.replace(
            ki.CANDIDATE_START + ki.CANDIDATE_END,
            ki.CANDIDATE_START + "\nA genuinely new fact.\n" + ki.CANDIDATE_END,
        )
        overview.write_text(text, encoding="utf-8")

        candidates = ki.detect_candidate_additions(tmp_path, "demo-slug")
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", [], candidates)
        _accept_all(manifest_path)
        ki.apply_manifest(tmp_path, manifest_path)

        assert ki.detect_candidate_additions(tmp_path, "demo-slug") == []

    def test_apply_manifest_twice_exactly_one_record(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        overview = sdir / "intermediate" / "overview.md"
        text = overview.read_text(encoding="utf-8")
        text = text.replace(
            ki.CANDIDATE_START + ki.CANDIDATE_END,
            ki.CANDIDATE_START + "\nSome new candidate fact.\n" + ki.CANDIDATE_END,
        )
        overview.write_text(text, encoding="utf-8")

        candidates = ki.detect_candidate_additions(tmp_path, "demo-slug")
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", [], candidates)
        _accept_all(manifest_path)
        ki.apply_manifest(tmp_path, manifest_path)
        ki.apply_manifest(tmp_path, manifest_path)

        new_records = [r for r in ki.load_slug_records(sdir) if r != "CL-DEMO-001"]
        assert len(new_records) == 1

    def test_identical_prose_two_candidates_deterministic(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        overview = sdir / "intermediate" / "overview.md"
        text = overview.read_text(encoding="utf-8")
        text = text.replace(
            ki.CANDIDATE_START + ki.CANDIDATE_END,
            ki.CANDIDATE_START + "\nIdentical fact.\n\nIdentical fact.\n" + ki.CANDIDATE_END,
        )
        overview.write_text(text, encoding="utf-8")

        candidates = ki.detect_candidate_additions(tmp_path, "demo-slug")
        assert len(candidates) == 2
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", [], candidates)
        _accept_all(manifest_path)
        ki.apply_manifest(tmp_path, manifest_path)

        new_records = [r for r in ki.load_slug_records(sdir) if r != "CL-DEMO-001"]
        assert len(new_records) == 1, "identical text is one contribution by documented design"


class TestExplicitDocumentGroundingReconciliation:
    """decisions/0073, point 3: grounded regions now participate in real
    reconciliation, not just identification."""

    def _ground(self, tmp_path: Path, statement: str = "Sync is idempotent.") -> tuple[Path, Path]:
        sdir = tmp_path / "planning" / "knowledge" / "demo-slug"
        sdir.mkdir(parents=True)
        (sdir / "CL-X-001.yaml").write_text(
            f"id: CL-X-001\nkind: claim\nstatement: {statement}\nderivation: null\n"
            "supporting_evidence: []\ncontradicting_evidence: []\nderived_by: t\n"
            'repository_revision: "working tree"\ntimestamp: "2026-10-07T00:00:00Z"\n'
            "status: supported\n",
            encoding="utf-8",
        )
        readme = tmp_path / "README.md"
        readme.write_text(
            "<!-- codecompass-grounded-by: CL-X-001 -->\n"
            f"{statement}\n"
            "<!-- /codecompass-grounded-by -->\n",
            encoding="utf-8",
        )
        return sdir, readme

    def test_grounded_edit_becomes_reconciliation_candidate(self, tmp_path):
        sdir, readme = self._ground(tmp_path)
        findings = ki.detect_grounded_region_changes(tmp_path)
        ki.advance_grounding_baseline(tmp_path, findings)  # establish baseline

        readme.write_text(
            readme.read_text(encoding="utf-8").replace(
                "Sync is idempotent.", "Sync can run any number of times safely."
            ),
            encoding="utf-8",
        )
        findings2 = ki.detect_grounded_region_changes(tmp_path)
        assert findings2[0].case == "doc_candidate"

        written = ki.write_doc_candidates_to_manifests(tmp_path, findings2)
        assert "demo-slug" in written
        manifest_path = written["demo-slug"]
        _accept_all(manifest_path)
        result = ki.apply_manifest(tmp_path, manifest_path)

        assert len(result.applied) == 1
        new_records = [r for r in ki.load_slug_records(sdir) if r != "CL-X-001"]
        assert len(new_records) == 1

    def test_grounded_edit_plus_claim_change_is_conflict(self, tmp_path):
        sdir, readme = self._ground(tmp_path)
        findings = ki.detect_grounded_region_changes(tmp_path)
        ki.advance_grounding_baseline(tmp_path, findings)

        readme.write_text(
            readme.read_text(encoding="utf-8").replace(
                "Sync is idempotent.", "Sync can run as often as needed."
            ),
            encoding="utf-8",
        )
        (sdir / "CL-X-001.yaml").write_text(
            (sdir / "CL-X-001.yaml").read_text(encoding="utf-8").replace(
                "status: supported", "status: verified"
            ),
            encoding="utf-8",
        )
        findings2 = ki.detect_grounded_region_changes(tmp_path)
        assert findings2[0].case == "concurrent_conflict"

        readme_before = readme.read_text(encoding="utf-8")
        claim_before = (sdir / "CL-X-001.yaml").read_text(encoding="utf-8")
        written = ki.write_doc_candidates_to_manifests(tmp_path, findings2)
        assert written == {}, "a conflict must never be silently turned into a candidate"
        assert readme.read_text(encoding="utf-8") == readme_before
        assert (sdir / "CL-X-001.yaml").read_text(encoding="utf-8") == claim_before

    def test_canonical_change_surfaces_grounded_region_as_potentially_stale(self, tmp_path):
        sdir, readme = self._ground(tmp_path)
        findings = ki.detect_grounded_region_changes(tmp_path)
        ki.advance_grounding_baseline(tmp_path, findings)

        (sdir / "CL-X-001.yaml").write_text(
            (sdir / "CL-X-001.yaml").read_text(encoding="utf-8").replace(
                "status: supported", "status: verified"
            ),
            encoding="utf-8",
        )
        findings2 = ki.detect_grounded_region_changes(tmp_path)
        assert findings2[0].case == "claims_changed"
        readme_before = readme.read_text(encoding="utf-8")
        written = ki.write_doc_candidates_to_manifests(tmp_path, findings2)
        assert written == {}
        assert readme.read_text(encoding="utf-8") == readme_before


class TestAdvisoryGroundingCoverageHonest:
    """decisions/0073, point 4."""

    def test_ungrounded_readme_change_is_advisory_only(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text("# Demo\n\n## Section\n\nSome prose.\n", encoding="utf-8")
        ki.advance_doc_chunk_baseline(tmp_path)

        readme.write_text(
            readme.read_text(encoding="utf-8").replace("Some prose.", "Totally new prose."),
            encoding="utf-8",
        )
        report = ki.detect_doc_chunk_changes(tmp_path)
        assert report["README.md"]["changed_ungrounded_chunks"] != []
        assert report["README.md"]["changed_grounded_chunks"] == []

        kdir = tmp_path / "planning" / "knowledge"
        yaml_files = list(kdir.rglob("*.yaml")) if kdir.exists() else []
        assert yaml_files == [], "ungrounded prose must never become a canonical Claim"

    def test_grounded_readme_change_reported_as_grounded(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text(
            "# Demo\n\n## Section\n\n"
            "<!-- codecompass-grounded-by: CL-X-001 -->\n"
            "Grounded fact.\n"
            "<!-- /codecompass-grounded-by -->\n",
            encoding="utf-8",
        )
        ki.advance_doc_chunk_baseline(tmp_path)
        readme.write_text(
            readme.read_text(encoding="utf-8").replace("Grounded fact.", "Updated grounded fact."),
            encoding="utf-8",
        )
        report = ki.detect_doc_chunk_changes(tmp_path)
        assert report["README.md"]["changed_grounded_chunks"] != []
        assert report["README.md"]["changed_ungrounded_chunks"] == []


class TestPresentationOverrideRetainsCanonicalMeaning:
    """decisions/0073, point 5."""

    def test_canonical_statement_retrievable_despite_presentation_override(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        cache_path = ki.presentation_cache_path(tmp_path, "demo-slug")
        sem_hash = ki.sha256_text((sdir / "CL-DEMO-001.yaml").read_text(encoding="utf-8"))
        ki.write_presentation_cache(
            cache_path,
            {
                "CL-DEMO-001": ki.PresentationEntry(
                    accepted_for_semantic_hash=sem_hash,
                    wording="Materially different presentation wording.",
                )
            },
        )
        ki.render_slug(tmp_path, "demo-slug")
        overview = (sdir / "intermediate" / "overview.md").read_text(encoding="utf-8")
        assert "Materially different presentation wording." in overview
        canonical = ki.extract_canonical_statement(overview)
        assert canonical is not None
        assert "idempotent" in canonical, "canonical meaning must remain retrievable"


class TestFactualHypothesisVsDeclaredIntent:
    """decisions/0073, point 7."""

    def test_factual_hypothesis_is_not_misclassified_as_proposed_policy(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        overview = sdir / "intermediate" / "overview.md"
        text = overview.read_text(encoding="utf-8")
        text = text.replace(
            ki.CANDIDATE_START + ki.CANDIDATE_END,
            ki.CANDIDATE_START
            + "\nThe system currently does X, not yet verified.\n"
            + ki.CANDIDATE_END,
        )
        overview.write_text(text, encoding="utf-8")
        candidates = ki.detect_candidate_additions(tmp_path, "demo-slug")
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", [], candidates)
        _accept_all(manifest_path)
        result = ki.apply_manifest(tmp_path, manifest_path)
        new_id = result.applied[0].new_record_id
        records = ki.load_slug_records(sdir)
        assert "basis" not in records[new_id].fields

    def test_declared_intent_via_explicit_type_becomes_proposed_policy(self, tmp_path):
        sdir = _make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        overview = sdir / "intermediate" / "overview.md"
        text = overview.read_text(encoding="utf-8")
        text = text.replace(
            ki.CANDIDATE_START + ki.CANDIDATE_END,
            ki.CANDIDATE_START + "\nType: Intent\nThe system should do X.\n" + ki.CANDIDATE_END,
        )
        overview.write_text(text, encoding="utf-8")
        candidates = ki.detect_candidate_additions(tmp_path, "demo-slug")
        assert candidates[0].declared_intent is True
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", [], candidates)
        _accept_all(manifest_path)
        result = ki.apply_manifest(tmp_path, manifest_path)
        new_id = result.applied[0].new_record_id
        records = ki.load_slug_records(sdir)
        assert records[new_id].fields.get("basis") == "proposed_policy"


class TestProvenanceDerivationCorrected:
    """decisions/0073, point 8 -- real-shaped Evidence/Observation records."""

    def _slug_with_evidence(self, tmp_path: Path, slug: str = "demo-slug") -> Path:
        sdir = tmp_path / "planning" / "knowledge" / slug
        sdir.mkdir(parents=True)
        return sdir

    def test_directly_stated_with_real_observation_is_observed(self, tmp_path):
        sdir = self._slug_with_evidence(tmp_path)
        (sdir / "OBS-X-001.yaml").write_text(
            'id: OBS-X-001\nkind: observation\nmethod: m\nwhat_was_done: w\n'
            'repository_revision: "x"\ntimestamp: "2026-10-07T00:00:00Z"\n'
            "performed_by: p\nstatus: recorded\n",
            encoding="utf-8",
        )
        (sdir / "EV-X-001.yaml").write_text(
            "id: EV-X-001\nkind: evidence\nevidence_kind: source\nwhat_it_shows: w\n"
            'observations: [OBS-X-001]\nrepository_revision: "x"\nstatus: current\n',
            encoding="utf-8",
        )
        (sdir / "CL-X-002.yaml").write_text(
            "id: CL-X-002\nkind: claim\nstatement: observed fact\nderivation: null\n"
            "supporting_evidence: [EV-X-001]\ncontradicting_evidence: []\nderived_by: t\n"
            'repository_revision: "x"\ntimestamp: "2026-10-07T00:00:00Z"\n'
            "status: supported\nbasis: directly_stated\n",
            encoding="utf-8",
        )
        records = ki.load_slug_records(sdir)
        assert ki.derive_provenance_label(records["CL-X-002"], records) == "OBSERVED"

    def test_directly_stated_with_direct_source_no_observation_is_cautious(self, tmp_path):
        """The real schema (docs/domain/concepts/evidence.md): Evidence may
        cite source/doc/test directly with no Observation at all -- must
        never be mistaken for OBSERVED provenance."""
        sdir = self._slug_with_evidence(tmp_path)
        (sdir / "EV-X-002.yaml").write_text(
            "id: EV-X-002\nkind: evidence\nevidence_kind: source\nwhat_it_shows: w\n"
            'source_ref: "x:1"\nrepository_revision: "x"\nstatus: current\n',
            encoding="utf-8",
        )
        (sdir / "CL-X-003.yaml").write_text(
            "id: CL-X-003\nkind: claim\nstatement: direct source cite\nderivation: null\n"
            "supporting_evidence: [EV-X-002]\ncontradicting_evidence: []\nderived_by: t\n"
            'repository_revision: "x"\ntimestamp: "2026-10-07T00:00:00Z"\n'
            "status: supported\nbasis: directly_stated\n",
            encoding="utf-8",
        )
        records = ki.load_slug_records(sdir)
        assert ki.derive_provenance_label(records["CL-X-003"], records) != "OBSERVED"

    def test_mixed_evidence_chain_is_mixed(self, tmp_path):
        sdir = self._slug_with_evidence(tmp_path)
        (sdir / "OBS-X-001.yaml").write_text(
            'id: OBS-X-001\nkind: observation\nmethod: m\nwhat_was_done: w\n'
            'repository_revision: "x"\ntimestamp: "2026-10-07T00:00:00Z"\n'
            "performed_by: p\nstatus: recorded\n",
            encoding="utf-8",
        )
        (sdir / "EV-X-001.yaml").write_text(
            "id: EV-X-001\nkind: evidence\nevidence_kind: source\nwhat_it_shows: w\n"
            'observations: [OBS-X-001]\nrepository_revision: "x"\nstatus: current\n',
            encoding="utf-8",
        )
        (sdir / "EV-X-002.yaml").write_text(
            "id: EV-X-002\nkind: evidence\nevidence_kind: source\nwhat_it_shows: w\n"
            'source_ref: "x:1"\nrepository_revision: "x"\nstatus: current\n',
            encoding="utf-8",
        )
        (sdir / "CL-X-004.yaml").write_text(
            "id: CL-X-004\nkind: claim\nstatement: mixed\nderivation: null\n"
            "supporting_evidence: [EV-X-001, EV-X-002]\ncontradicting_evidence: []\n"
            'derived_by: t\nrepository_revision: "x"\ntimestamp: "2026-10-07T00:00:00Z"\n'
            "status: supported\nbasis: directly_stated\n",
            encoding="utf-8",
        )
        records = ki.load_slug_records(sdir)
        assert ki.derive_provenance_label(records["CL-X-004"], records) == "MIXED"
