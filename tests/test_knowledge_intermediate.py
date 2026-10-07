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


class TestRequirementInvariant:
    def test_unapproved_decision_falls_back_to_claim(self, tmp_path):
        sdir = _make_slug(tmp_path, decision=_DECISION_PROPOSED)
        ki.render_slug(tmp_path, "demo-slug")
        overview_path = sdir / "intermediate" / "overview.md"
        text = overview_path.read_text(encoding="utf-8")
        text = text.replace(
            ki.CANDIDATE_START + ki.CANDIDATE_END,
            ki.CANDIDATE_START + "\nPer DEC-DEMO-001, add a feature.\n" + ki.CANDIDATE_END,
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

    def test_approved_decision_may_create_requirement(self, tmp_path):
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
        assert candidates[0].cited_decision == "DEC-DEMO-001"
        manifest_path = ki.write_manifest(tmp_path, "demo-slug", [], candidates)
        _accept_all(manifest_path)
        result = ki.apply_manifest(tmp_path, manifest_path)

        new_id = result.applied[0].new_record_id
        assert new_id.startswith("REQ-")
        records = ki.load_slug_records(sdir)
        assert records[new_id].kind == "requirement"
        assert records[new_id].fields["decision"] == "DEC-DEMO-001"


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
