"""Tests for scripts/check_self_knowledge_quality.py — a maintainer-only
tool, not part of the codecompass package. Imported directly from its
file path since scripts/ is deliberately not a package (mirrors
tests/test_check_knowledge_base.py's own identical precedent).

Phase 85 (planning/phase-85-self-curation-knowledge-quality-validation.md
§4.C/§8). Covers: `missing_contract` reachability and corrected severity
(always informational); the `test_ref`-file check and its discovered
contract-bearing-slug scoping fix; the corpus-wide `missing_evidence`
composition's decided-vs-proposed severity split; the refined duplicate/
overlap detection's five sub-rules; and determinism.

**Deliberately does not assert zero blocking findings against the real
repository**, unlike test_check_knowledge_base.py's/test_check_contracts.
py's own `test_no_false_positives_against_real_repo` — this script's
whole purpose is to surface genuine, pre-existing knowledge-quality
defects in the self-knowledge corpus (a real, independently-confirmed
contradiction on CL-ADPT-008; a real, independently-confirmed unverified
required scope and stale test citation on balance-from-spec, cross-
checked against check_contracts.py's own `contract-check-gap` finding
for the identical check_id). Suppressing those to make a test pass would
be exactly the "automatically suppress a genuine defect" this project's
own governing instructions rule out. Instead, the real-baseline test
below pins the specific, already-investigated findings by name.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "check_self_knowledge_quality.py"
)
_spec = importlib.util.spec_from_file_location("check_self_knowledge_quality", _SCRIPT_PATH)
check_self_knowledge_quality = importlib.util.module_from_spec(_spec)
sys.modules["check_self_knowledge_quality"] = check_self_knowledge_quality
_spec.loader.exec_module(check_self_knowledge_quality)

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGERKIT_ROOT = Path.home() / "projects" / "ledgerkit"
requires_ledgerkit = pytest.mark.skipif(
    not LEDGERKIT_ROOT.is_dir(), reason="~/projects/ledgerkit not present"
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


_CLAIM = """\
id: {id}
kind: claim
statement: {statement}
derivation: DE-TEST-001
supporting_evidence: {supporting_evidence}
contradicting_evidence: []
derived_by: test
repository_revision: "working tree"
timestamp: "2026-10-01T00:00:00Z"
status: {status}
supersedes: null
"""

_REQUIREMENT = """\
id: {id}
kind: requirement
statement: a requirement statement
example: |
  Given X
  When Y
  Then Z
decision: DEC-TEST-001
status: {status}
"""

_EVIDENCE_TEST = """\
id: {id}
kind: evidence
evidence_kind: test
what_it_shows: a test result
test_ref: "{test_ref}"
repository_revision: "working tree"
status: current
"""


@requires_ledgerkit
class TestRealBaseline:
    def test_runs_without_crashing_and_is_deterministic(self):
        first = check_self_knowledge_quality.run_all(REPO_ROOT, LEDGERKIT_ROOT)
        second = check_self_knowledge_quality.run_all(REPO_ROOT, LEDGERKIT_ROOT)
        assert [(f.rule, f.message, f.strict) for f in first] == [
            (f.rule, f.message, f.strict) for f in second
        ]
        assert first  # the real corpus has real, known findings -- never silently empty

    def test_missing_contract_is_always_informational_on_real_corpus(self):
        findings = check_self_knowledge_quality.run_all(REPO_ROOT, LEDGERKIT_ROOT)
        contract_findings = [f for f in findings if f.rule == "self-knowledge-quality-missing-contract"]
        # Five of the six real knowledge slugs have no oracle contract.
        assert len(contract_findings) == 5
        assert all(not f.strict for f in contract_findings)

    def test_missing_contract_not_reported_for_contract_bearing_slug(self):
        findings = check_self_knowledge_quality.run_all(REPO_ROOT, LEDGERKIT_ROOT)
        assert not any(
            f.rule == "self-knowledge-quality-missing-contract" and "balance-from-spec" in f.message
            for f in findings
        )

    def test_known_pre_existing_findings_are_present_and_classified(self):
        """Pins the specific, independently-investigated real findings this
        plan's own implementation discovered -- not a defect this phase
        introduces or is responsible for fixing (CL-ADPT-008's domain
        contradiction and balance-from-spec's own missing oracle coverage
        both predate Phase 85)."""
        findings = check_self_knowledge_quality.run_all(REPO_ROOT, LEDGERKIT_ROOT)
        by_rule = {f.rule for f in findings}
        assert "self-knowledge-quality-contradiction" in by_rule
        assert "self-knowledge-quality-unverified-required-scope" in by_rule
        assert "self-knowledge-quality-stale-test-citation" in by_rule
        # These four pre-Phase-82 Evidence records use the older plain
        # pytest-citation convention in a non-contract-bearing slug --
        # never flagged by the test_ref-file check (the contract-bearing
        # scoping fix).
        no_result_file_check = [
            f for f in findings if f.rule.startswith("self-knowledge-quality-missing-test-ref-file")
        ]
        assert no_result_file_check == []


class TestMissingContractSeverity:
    def test_fixture_slug_with_requirement_and_no_contract_is_informational(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        _write(
            slug_dir / "REQ-FIX-001.yaml",
            _REQUIREMENT.format(id="REQ-FIX-001", status="approved"),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        contract_findings = [
            f for f in findings if f.rule == "self-knowledge-quality-missing-contract"
        ]
        assert len(contract_findings) == 1
        assert contract_findings[0].strict is False

    def test_fixture_slug_with_only_observations_has_no_obligation_finding(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        _write(
            slug_dir / "OBS-FIX-001.yaml",
            "id: OBS-FIX-001\nkind: observation\nmethod: source_read\n"
            'what_was_done: "read a file"\nrepository_revision: "working tree"\n'
            'timestamp: "2026-10-01T00:00:00Z"\nperformed_by: test\nstatus: recorded\n',
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        assert findings == [] or not any(
            f.rule == "self-knowledge-quality-missing-contract" for f in findings
        )


class TestTestRefFileCheck:
    def _make_contract(self, tmp_path: Path, slug: str) -> None:
        contract_dir = tmp_path / "planning" / "contracts" / slug
        _write(
            contract_dir / "oracle-contract.yaml",
            f"""\
contract_id: REQ-{slug.upper()}-001
tested_paths: []
checks:
  - check_id: a-check
    scope: a scope
    execution_provider: pytest
    check_reference: tests/test_x.py::test_a
    test_input_paths: [tests/test_x.py]
    required: false
""",
        )

    def test_missing_result_file_is_blocking(self, tmp_path):
        slug = "fixture-slug"
        self._make_contract(tmp_path, slug)
        slug_dir = tmp_path / "planning" / "knowledge" / slug
        _write(
            slug_dir / "EV-FIX-001.yaml",
            _EVIDENCE_TEST.format(id="EV-FIX-001", test_ref=f"planning/contracts/{slug}/results/missing.yaml"),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [f for f in findings if f.rule == "self-knowledge-quality-missing-test-ref-file"]
        assert len(hits) == 1
        assert hits[0].strict is True

    def test_malformed_result_file_is_blocking(self, tmp_path):
        slug = "fixture-slug"
        self._make_contract(tmp_path, slug)
        slug_dir = tmp_path / "planning" / "knowledge" / slug
        ref = f"planning/contracts/{slug}/results/broken.yaml"
        _write(tmp_path / ref, "not: a valid oracle result\n")
        _write(
            slug_dir / "EV-FIX-001.yaml",
            _EVIDENCE_TEST.format(id="EV-FIX-001", test_ref=ref),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [f for f in findings if f.rule == "self-knowledge-quality-malformed-test-ref-file"]
        assert len(hits) == 1
        assert hits[0].strict is True

    def test_well_formed_result_file_is_not_flagged(self, tmp_path):
        slug = "fixture-slug"
        self._make_contract(tmp_path, slug)
        slug_dir = tmp_path / "planning" / "knowledge" / slug
        ref = f"planning/contracts/{slug}/results/good.yaml"
        _write(
            tmp_path / ref,
            """\
schema_version: 1
run_id: run-001
contract_id: REQ-FIXTURE-SLUG-001
check_id: a-check
scope: a scope
baseline_id: null
tested_subject_digest: deadbeef
oracle_contract_id: REQ-FIXTURE-SLUG-001
oracle_contract_content_hash: deadbeef
test_input_digest: deadbeef
environment_descriptor: null
raw_output_ref: planning/contracts/fixture-slug/results/raw/run-001.txt
raw_output_sha256: deadbeef
outcome: PASS
executed_at: "2026-10-01T00:00:00+00:00"
execution_provider: pytest
invalid_reason: null
""",
        )
        _write(
            slug_dir / "EV-FIX-001.yaml",
            _EVIDENCE_TEST.format(id="EV-FIX-001", test_ref=ref),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [
            f
            for f in findings
            if f.rule
            in ("self-knowledge-quality-missing-test-ref-file", "self-knowledge-quality-malformed-test-ref-file")
        ]
        assert hits == []

    def test_non_resolving_test_ref_in_slug_without_contract_is_not_flagged(self, tmp_path):
        """The discovered scoping fix: a plain pytest-file citation in a
        slug with no oracle contract is a legitimate, pre-Phase-82
        convention, never a defect."""
        slug = "fixture-slug-no-contract"
        slug_dir = tmp_path / "planning" / "knowledge" / slug
        _write(
            slug_dir / "EV-FIX-001.yaml",
            _EVIDENCE_TEST.format(id="EV-FIX-001", test_ref="tests/test_whatever.py:10-20"),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [
            f
            for f in findings
            if f.rule
            in ("self-knowledge-quality-missing-test-ref-file", "self-knowledge-quality-malformed-test-ref-file")
        ]
        assert hits == []

    def test_unreadable_result_file_is_blocking(self, tmp_path, monkeypatch):
        """Corrective pass: a filesystem failure (permission error or any
        other `OSError`) reading an otherwise-existing `test_ref` file must
        become a typed, blocking finding -- never an uncaught exception
        that terminates the whole validator. Reproduced deterministically
        via an injected `Path.read_text` failure rather than relying on a
        real `chmod`, which would behave differently as root."""
        slug = "fixture-slug"
        self._make_contract(tmp_path, slug)
        slug_dir = tmp_path / "planning" / "knowledge" / slug
        ref = f"planning/contracts/{slug}/results/unreadable.yaml"
        target = (tmp_path / ref).resolve()
        _write(tmp_path / ref, "schema_version: 1\n")
        _write(
            slug_dir / "EV-FIX-001.yaml",
            _EVIDENCE_TEST.format(id="EV-FIX-001", test_ref=ref),
        )

        real_read_text = Path.read_text

        def _fake_read_text(self, *args, **kwargs):
            if self.resolve() == target:
                raise PermissionError(13, "Permission denied", str(self))
            return real_read_text(self, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", _fake_read_text)

        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [f for f in findings if f.rule == "self-knowledge-quality-unreadable-test-ref-file"]
        assert len(hits) == 1
        assert hits[0].strict is True
        assert "EV-FIX-001" in hits[0].message
        assert "PermissionError" in hits[0].message

    def test_unreadable_result_file_does_not_crash_the_whole_run(self, tmp_path, monkeypatch):
        """Pre-fix behaviour: an uncaught `OSError` from `oracle.
        parse_oracle_result` propagated out of `check_test_ref_files` and
        crashed `run_all()` entirely, hiding every other real finding
        (the real corpus's genuine contradiction/scope findings among
        them). This must no longer happen."""
        slug = "fixture-slug"
        self._make_contract(tmp_path, slug)
        slug_dir = tmp_path / "planning" / "knowledge" / slug
        ref = f"planning/contracts/{slug}/results/unreadable.yaml"
        target = (tmp_path / ref).resolve()
        _write(tmp_path / ref, "schema_version: 1\n")
        _write(
            slug_dir / "EV-FIX-001.yaml",
            _EVIDENCE_TEST.format(id="EV-FIX-001", test_ref=ref),
        )
        _write(
            slug_dir / "CL-FIX-001.yaml",
            _CLAIM.format(id="CL-FIX-001", statement="a claim", supporting_evidence="[]", status="supported"),
        )

        real_read_text = Path.read_text

        def _fake_read_text(self, *args, **kwargs):
            if self.resolve() == target:
                raise PermissionError(13, "Permission denied", str(self))
            return real_read_text(self, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", _fake_read_text)

        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        assert any(f.rule == "self-knowledge-quality-missing-evidence" for f in findings)
        assert any(f.rule == "self-knowledge-quality-unreadable-test-ref-file" for f in findings)


class TestMissingEvidenceSeverity:
    def test_proposed_claim_with_no_evidence_is_informational(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        _write(
            slug_dir / "CL-FIX-001.yaml",
            _CLAIM.format(id="CL-FIX-001", statement="a claim", supporting_evidence="[]", status="proposed"),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [f for f in findings if f.rule == "self-knowledge-quality-missing-evidence"]
        assert len(hits) == 1
        assert hits[0].strict is False

    def test_supported_claim_with_no_evidence_is_blocking(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        _write(
            slug_dir / "CL-FIX-001.yaml",
            _CLAIM.format(id="CL-FIX-001", statement="a claim", supporting_evidence="[]", status="supported"),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [f for f in findings if f.rule == "self-knowledge-quality-missing-evidence"]
        assert len(hits) == 1
        assert hits[0].strict is True


class TestDuplicateOverlapDetection:
    def test_identical_statement_different_evidence_is_informational(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        _write(
            slug_dir / "CL-FIX-001.yaml",
            _CLAIM.format(
                id="CL-FIX-001", statement="the exact same statement text",
                supporting_evidence="[EV-FIX-001]", status="supported",
            ),
        )
        _write(
            slug_dir / "CL-FIX-002.yaml",
            _CLAIM.format(
                id="CL-FIX-002", statement="the   exact same   statement text",
                supporting_evidence="[EV-FIX-002]", status="supported",
            ),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [f for f in findings if f.rule == "self-knowledge-quality-duplicate-statement"]
        assert len(hits) == 1
        assert hits[0].strict is False

    def test_identical_nonempty_evidence_different_statement_is_possible_overlap(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        _write(
            slug_dir / "CL-FIX-001.yaml",
            _CLAIM.format(
                id="CL-FIX-001", statement="statement A",
                supporting_evidence="[EV-FIX-001, EV-FIX-002]", status="supported",
            ),
        )
        _write(
            slug_dir / "CL-FIX-002.yaml",
            _CLAIM.format(
                id="CL-FIX-002", statement="statement B, a genuinely different assertion",
                supporting_evidence="[EV-FIX-002, EV-FIX-001]", status="supported",
            ),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [f for f in findings if f.rule == "self-knowledge-quality-possible-evidence-overlap"]
        assert len(hits) == 1
        assert hits[0].strict is False
        # Not merged/auto-resolved -- both records remain, two separate
        # files, as this check never edits canonical knowledge.
        assert (slug_dir / "CL-FIX-001.yaml").is_file()
        assert (slug_dir / "CL-FIX-002.yaml").is_file()

    def test_both_empty_evidence_sets_never_trigger_overlap_on_their_own(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        _write(
            slug_dir / "CL-FIX-001.yaml",
            _CLAIM.format(id="CL-FIX-001", statement="statement A", supporting_evidence="[]", status="proposed"),
        )
        _write(
            slug_dir / "CL-FIX-002.yaml",
            _CLAIM.format(id="CL-FIX-002", statement="statement B", supporting_evidence="[]", status="proposed"),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        overlap_hits = [f for f in findings if "overlap" in f.rule or "duplicate" in f.rule]
        assert overlap_hits == []

    def test_same_evidence_genuinely_different_claims_remain_distinguishable(self, tmp_path):
        """Confirms the possible-overlap signal never causes these two
        distinct Claims to be treated as one -- advisory only."""
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        _write(
            slug_dir / "CL-FIX-001.yaml",
            _CLAIM.format(
                id="CL-FIX-001", statement="the probe shows a false positive on raw strings",
                supporting_evidence="[EV-FIX-001]", status="supported",
            ),
        )
        _write(
            slug_dir / "CL-FIX-002.yaml",
            _CLAIM.format(
                id="CL-FIX-002", statement="the probe's line-number attribution is off by one",
                supporting_evidence="[EV-FIX-001]", status="supported",
            ),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        overlap_hits = [f for f in findings if f.rule == "self-knowledge-quality-possible-evidence-overlap"]
        assert len(overlap_hits) == 1  # flagged for a human to look at...
        duplicate_hits = [f for f in findings if f.rule == "self-knowledge-quality-duplicate-statement"]
        assert duplicate_hits == []  # ...but never treated as a duplicate

    def test_true_semantic_overlap_with_disjoint_evidence_is_not_flagged(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        _write(
            slug_dir / "CL-FIX-001.yaml",
            _CLAIM.format(
                id="CL-FIX-001", statement="raw string literals can defeat the extractor",
                supporting_evidence="[EV-FIX-001]", status="supported",
            ),
        )
        _write(
            slug_dir / "CL-FIX-002.yaml",
            _CLAIM.format(
                id="CL-FIX-002", statement="multi-line string content is mistaken for code",
                supporting_evidence="[EV-FIX-002]", status="supported",
            ),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        overlap_hits = [f for f in findings if "overlap" in f.rule or "duplicate" in f.rule]
        assert overlap_hits == []


_MIN_EVIDENCE = """\
id: {id}
kind: evidence
evidence_kind: source
what_it_shows: a minimal evidence record
repository_revision: "working tree"
status: current
"""

_CLAIM_WITH_CONTRADICTION = """\
id: {id}
kind: claim
statement: {statement}
derivation: DE-TEST-001
supporting_evidence: [EV-FIX-001]
contradicting_evidence: [EV-FIX-002]
derived_by: test
repository_revision: "working tree"
timestamp: "2026-10-01T00:00:00Z"
status: {status}
supersedes: {supersedes}
"""


class TestContradictionSeverity:
    """Corrective pass: `find_gaps()`'s own `contradiction` Gap fires
    whenever a record has non-empty `contradicting_evidence`, regardless
    of whether the record's own `status` already resolved that
    contradiction historically (`status: superseded`). The real
    `CL-ADPT-008` is exactly this case -- `status: superseded`, retaining
    `contradicting_evidence: [EV-ADPT-008]` as provenance, genuinely
    resolved by `CL-ADPT-010` (`status: supported`, `supersedes:
    CL-ADPT-008`). `knowledge_intermediate.derive_provenance_label`
    already treats `status: superseded` as `HISTORICAL` elsewhere in this
    project -- this reclassifies severity using a distinction the project
    already treats as authoritative, without changing `find_gaps()`
    itself."""

    def _two_evidence(self, slug_dir):
        _write(slug_dir / "EV-FIX-001.yaml", _MIN_EVIDENCE.format(id="EV-FIX-001"))
        _write(slug_dir / "EV-FIX-002.yaml", _MIN_EVIDENCE.format(id="EV-FIX-002"))

    def test_active_contradicted_claim_remains_blocking(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        self._two_evidence(slug_dir)
        _write(
            slug_dir / "CL-FIX-001.yaml",
            _CLAIM_WITH_CONTRADICTION.format(
                id="CL-FIX-001", statement="an actively contradicted claim",
                status="contradicted", supersedes="null",
            ),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [
            f for f in findings
            if f.rule == "self-knowledge-quality-contradiction" and "CL-FIX-001" in f.message
        ]
        assert hits
        assert all(f.strict for f in hits)

    def test_superseded_claim_with_genuine_successor_is_informational(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        self._two_evidence(slug_dir)
        _write(
            slug_dir / "CL-FIX-001.yaml",
            _CLAIM_WITH_CONTRADICTION.format(
                id="CL-FIX-001", statement="a historically superseded claim",
                status="superseded", supersedes="null",
            ),
        )
        _write(
            slug_dir / "CL-FIX-002.yaml",
            _CLAIM.format(
                id="CL-FIX-002", statement="the resolving successor claim",
                supporting_evidence="[EV-FIX-001]", status="supported",
            ).replace("supersedes: null", "supersedes: CL-FIX-001"),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [
            f for f in findings
            if f.rule == "self-knowledge-quality-contradiction" and "CL-FIX-001" in f.message
        ]
        assert hits
        assert all(not f.strict for f in hits)

    def test_orphaned_superseded_status_remains_blocking(self, tmp_path):
        """A `status: superseded` Claim that nothing actually names in a
        `supersedes` field is not automatically trusted -- fail-closed,
        stays blocking."""
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        self._two_evidence(slug_dir)
        _write(
            slug_dir / "CL-FIX-001.yaml",
            _CLAIM_WITH_CONTRADICTION.format(
                id="CL-FIX-001", statement="a claim marked superseded but never actually replaced",
                status="superseded", supersedes="null",
            ),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [
            f for f in findings
            if f.rule == "self-knowledge-quality-contradiction" and "CL-FIX-001" in f.message
        ]
        assert hits
        assert all(f.strict for f in hits)

    def test_superseded_claim_with_unresolved_successor_remains_blocking(self, tmp_path):
        """The successor itself must be credible -- a `status:
        contradicted` claimed successor does not genuinely resolve
        anything, so severity is not downgraded."""
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        self._two_evidence(slug_dir)
        _write(
            slug_dir / "CL-FIX-001.yaml",
            _CLAIM_WITH_CONTRADICTION.format(
                id="CL-FIX-001", statement="a claim superseded by a broken successor",
                status="superseded", supersedes="null",
            ),
        )
        _write(
            slug_dir / "CL-FIX-002.yaml",
            _CLAIM.format(
                id="CL-FIX-002", statement="a successor that is itself contradicted",
                supporting_evidence="[EV-FIX-001]", status="contradicted",
            ).replace("supersedes: null", "supersedes: CL-FIX-001"),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [
            f for f in findings
            if f.rule == "self-knowledge-quality-contradiction" and "CL-FIX-001" in f.message
        ]
        assert hits
        assert all(f.strict for f in hits)

    def test_non_superseded_status_with_contradicting_evidence_remains_blocking(self, tmp_path):
        """An unresolved contradiction on a Claim that is not even marked
        `superseded` (e.g. still `supported`) must remain blocking --
        this is the ordinary, active case the check exists to catch."""
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        self._two_evidence(slug_dir)
        _write(
            slug_dir / "CL-FIX-001.yaml",
            _CLAIM_WITH_CONTRADICTION.format(
                id="CL-FIX-001", statement="a supported claim with unresolved contradicting evidence",
                status="supported", supersedes="null",
            ),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [
            f for f in findings
            if f.rule == "self-knowledge-quality-contradiction" and "CL-FIX-001" in f.message
        ]
        assert hits
        assert all(f.strict for f in hits)

    def test_real_cl_adpt_008_contradiction_is_now_informational(self):
        """Direct confirmation against the real corpus: `CL-ADPT-008`
        (`status: superseded`, genuinely resolved by `CL-ADPT-010`) no
        longer reports as a blocking contradiction."""
        if not REPO_ROOT.joinpath("planning/knowledge/codecompass-domain/CL-ADPT-008.yaml").is_file():
            pytest.skip("CL-ADPT-008 fixture record not present in this checkout")
        findings = check_self_knowledge_quality.run_all(REPO_ROOT, repo_root=None)
        hits = [
            f for f in findings
            if f.rule == "self-knowledge-quality-contradiction" and "CL-ADPT-008" in f.message
        ]
        assert hits
        assert all(not f.strict for f in hits)


class TestFindGapsComposition:
    def test_dangling_evidence_reference_remains_blocking(self, tmp_path):
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        _write(
            slug_dir / "CL-FIX-001.yaml",
            _CLAIM.format(
                id="CL-FIX-001", statement="a claim",
                supporting_evidence="[EV-MISSING-001]", status="supported",
            ),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        hits = [f for f in findings if f.rule == "self-knowledge-quality-dangling-evidence-reference"]
        assert len(hits) == 1
        assert hits[0].strict is True

    def test_no_slug_filter_means_missing_contract_is_reachable(self, tmp_path):
        """Reachability regression guard (this plan's own first material
        fix): confirms the script's own call to find_gaps() is not
        accidentally narrowed to only contract-bearing slugs."""
        slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
        _write(
            slug_dir / "REQ-FIX-001.yaml",
            _REQUIREMENT.format(id="REQ-FIX-001", status="approved"),
        )
        findings = check_self_knowledge_quality.run_all(tmp_path, repo_root=None)
        assert any(f.rule == "self-knowledge-quality-missing-contract" for f in findings)


def test_cli_strict_exit_code_reflects_blocking_findings(tmp_path, monkeypatch, capsys):
    slug_dir = tmp_path / "planning" / "knowledge" / "fixture-slug"
    _write(
        slug_dir / "CL-FIX-001.yaml",
        _CLAIM.format(
            id="CL-FIX-001", statement="a claim",
            supporting_evidence="[EV-MISSING-001]", status="supported",
        ),
    )
    monkeypatch.setattr(check_self_knowledge_quality, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["check_self_knowledge_quality.py", "--strict"])
    exit_code = check_self_knowledge_quality.main()
    assert exit_code == 1
    monkeypatch.setattr(sys, "argv", ["check_self_knowledge_quality.py"])
    exit_code = check_self_knowledge_quality.main()
    assert exit_code == 0
