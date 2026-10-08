"""Tests for scripts/check_knowledge_base.py — a maintainer-only tool,
not part of the codecompass package. Imported directly from its file
path since scripts/ is deliberately not a package (see
tests/test_check_user_docs.py's own identical precedent).

Phase 79 additions covered here: the two new Claim-schema checks
(check_optional_enum_fields, check_list_fields_are_inline — including
the fail-closed bypasses a narrower block-list detector missed: an
intervening comment, a blank line, and an indentless list) and the two
new snapshot-integrity checks (check_snapshot_historical_integrity,
check_snapshot_current_divergence), exercised against a real, disposable
git fixture repository — not mocked — per the user's own explicit
instruction to add meaningful verification that a normal supersession
preserves historical integrity, historical-content tampering is
detected, and a current change triggers reassessment.
"""

from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

_SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "check_knowledge_base.py"
)
_spec = importlib.util.spec_from_file_location("check_knowledge_base", _SCRIPT_PATH)
check_knowledge_base = importlib.util.module_from_spec(_spec)
sys.modules["check_knowledge_base"] = check_knowledge_base
_spec.loader.exec_module(check_knowledge_base)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_no_false_positives_against_real_repo():
    """Blocking findings only — an informational one (e.g. a snapshot
    current-divergence report) is expected and fine; it never fails
    `--strict` either (Finding.strict=False)."""
    findings = check_knowledge_base.run_all(REPO_ROOT)
    assert [f for f in findings if f.strict] == []


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


_CLAIM_HEADER = """\
id: CL-TEST-001
kind: claim
statement: test statement
derivation: DE-TEST-001
supporting_evidence: [EV-TEST-001]
contradicting_evidence: []
derived_by: test
repository_revision: "working tree"
timestamp: "2026-10-01T00:00:00Z"
status: supported
supersedes: null
"""


class TestOptionalEnumFields:
    def test_valid_value_no_finding(self, tmp_path):
        _write(
            tmp_path / "CL-TEST-001.yaml",
            _CLAIM_HEADER + "assertion_kind: definition\nbasis: directly_stated\n",
        )
        findings = check_knowledge_base.check_optional_enum_fields(tmp_path, root=tmp_path)
        assert findings == []

    def test_invalid_value_flagged(self, tmp_path):
        _write(
            tmp_path / "CL-TEST-001.yaml",
            _CLAIM_HEADER + "assertion_kind: not_a_real_kind\n",
        )
        findings = check_knowledge_base.check_optional_enum_fields(tmp_path, root=tmp_path)
        assert len(findings) == 1
        assert "assertion_kind" in findings[0].message
        assert findings[0].strict

    def test_absent_field_is_fine(self, tmp_path):
        _write(tmp_path / "CL-TEST-001.yaml", _CLAIM_HEADER)
        findings = check_knowledge_base.check_optional_enum_fields(tmp_path, root=tmp_path)
        assert findings == []


class TestListFieldsAreInline:
    def test_inline_form_no_finding(self, tmp_path):
        _write(
            tmp_path / "CL-TEST-001.yaml",
            _CLAIM_HEADER + "depends_on: [CL-TEST-002, CL-TEST-003]\n",
        )
        findings = check_knowledge_base.check_list_fields_are_inline(tmp_path, root=tmp_path)
        assert findings == []

    def test_empty_inline_list_no_finding(self, tmp_path):
        _write(tmp_path / "CL-TEST-001.yaml", _CLAIM_HEADER + "depends_on: []\n")
        findings = check_knowledge_base.check_list_fields_are_inline(tmp_path, root=tmp_path)
        assert findings == []

    def test_block_list_flagged(self, tmp_path):
        """The exact real-world shape found in this project's own
        pre-existing knowledge base (15 real records, fixed the same day
        this check was added) — a bare `key:` followed by indented
        `- item` lines."""
        _write(
            tmp_path / "CL-TEST-001.yaml",
            _CLAIM_HEADER + "depends_on:\n  - CL-TEST-002\n  - CL-TEST-003\n",
        )
        findings = check_knowledge_base.check_list_fields_are_inline(tmp_path, root=tmp_path)
        assert len(findings) == 1
        assert "depends_on" in findings[0].message
        assert findings[0].strict

    def test_block_list_with_comment_before_first_item_flagged(self, tmp_path):
        """Bypass #1 the second revision's own narrower detector missed:
        an intervening comment line between the bare key and its first
        list item — the fail-closed, parsed-value check catches it
        anyway, since the comment never survives into the parsed value
        either way."""
        _write(
            tmp_path / "CL-TEST-001.yaml",
            _CLAIM_HEADER
            + "depends_on:\n  # a comment explaining this\n  - CL-TEST-002\n",
        )
        findings = check_knowledge_base.check_list_fields_are_inline(tmp_path, root=tmp_path)
        assert len(findings) == 1
        assert "depends_on" in findings[0].message

    def test_indentless_block_list_flagged(self, tmp_path):
        """Bypass #2 the second revision's own narrower detector missed:
        an indentless block list (no leading whitespace on the `- item`
        lines) — a real regex requiring `^\\s+-\\s` never matches this,
        but the fail-closed parsed-value check does not care about
        indentation at all."""
        _write(
            tmp_path / "CL-TEST-001.yaml",
            _CLAIM_HEADER + "depends_on:\n- CL-TEST-002\n- CL-TEST-003\n",
        )
        findings = check_knowledge_base.check_list_fields_are_inline(tmp_path, root=tmp_path)
        assert len(findings) == 1
        assert "depends_on" in findings[0].message

    def test_malformed_non_bracket_value_flagged(self, tmp_path):
        _write(
            tmp_path / "CL-TEST-001.yaml",
            _CLAIM_HEADER + "depends_on: CL-TEST-002, CL-TEST-003\n",
        )
        findings = check_knowledge_base.check_list_fields_are_inline(tmp_path, root=tmp_path)
        assert len(findings) == 1

    def test_non_claim_kind_not_checked(self, tmp_path):
        """This field set is Claim-specific; a Derivation record (which
        has no `kind: claim`) is never checked against it, even if it
        happened to have a same-named field."""
        _write(
            tmp_path / "DE-TEST-001.yaml",
            "id: DE-TEST-001\nkind: derivation\nclaim: CL-TEST-001\n"
            "method: test\ninputs: []\nperformed_by: test\n"
            'timestamp: "2026-10-01T00:00:00Z"\ndepends_on:\n  - X\n',
        )
        findings = check_knowledge_base.check_list_fields_are_inline(tmp_path, root=tmp_path)
        assert findings == []


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)


def _commit_all(root: Path, message: str) -> str:
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=root, check=True)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
    ).stdout.strip()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


class TestSnapshotIntegrity:
    """Exercised against a real, disposable git repository — not mocked
    — per the user's own explicit instruction. Three scenarios: a normal
    supersession must preserve historical integrity; direct tampering
    with a snapshot's own recorded hash must be detected; and a current
    change must trigger a reassessment-worthy divergence report, without
    ever failing --strict on its own."""

    def _build_base_repo(self, tmp_path: Path) -> tuple[Path, str, str]:
        feature_dir = tmp_path / "planning" / "knowledge" / "test-topic"
        claim_path = feature_dir / "CL-TEST-001.yaml"
        _write(claim_path, _CLAIM_HEADER)
        ev_path = feature_dir / "EV-TEST-001.yaml"
        _write(
            ev_path,
            "id: EV-TEST-001\nkind: evidence\nevidence_kind: source\n"
            "what_it_shows: test\nrepository_revision: \"working tree\"\n"
            "status: current\n",
        )
        de_path = feature_dir / "DE-TEST-001.yaml"
        _write(
            de_path,
            "id: DE-TEST-001\nkind: derivation\nclaim: CL-TEST-001\n"
            "method: test\ninputs: []\nperformed_by: test\n"
            'timestamp: "2026-10-01T00:00:00Z"\n',
        )
        _init_git_repo(tmp_path)
        rev = _commit_all(tmp_path, "add CL-TEST-001 + its cited evidence/derivation")
        content_hash = _sha256_file(claim_path)

        snapshots_dir = feature_dir / "snapshots"
        snapshots_dir.mkdir(parents=True)
        rel_path = "planning/knowledge/test-topic/CL-TEST-001.yaml"
        snapshot_toml = f"""\
snapshot_id = "test-topic@v1"
created = "2026-10-01T00:00:00Z"
repository_revision_at_freeze = "{rev}"
excluded_assertions = []

[assertions."CL-TEST-001"]
path = "{rel_path}"
repository_revision = "{rev}"
content_hash = "{content_hash}"

[assertions."CL-TEST-001".supporting_evidence."EV-TEST-001"]
path = "planning/knowledge/test-topic/EV-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{_sha256_file(ev_path)}"

[assertions."CL-TEST-001".derivation."DE-TEST-001"]
path = "planning/knowledge/test-topic/DE-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{_sha256_file(de_path)}"
"""
        snapshot_path = snapshots_dir / "snapshot-v1.toml"
        _write(snapshot_path, snapshot_toml)
        _commit_all(tmp_path, "freeze snapshot-v1")
        return feature_dir, rev, content_hash

    def test_normal_supersession_preserves_historical_integrity(self, tmp_path):
        """A legitimate lifecycle transition (superseding the same
        assertion, editing its own `status` field in place) must never
        be reported as tampering — the whole point of hashing the
        historical git blob instead of the live file."""
        feature_dir, rev, content_hash = self._build_base_repo(tmp_path)
        claim_path = feature_dir / "CL-TEST-001.yaml"

        # Legitimate supersession: status moves to superseded, a new
        # successor record is created — exactly per the versioning
        # discipline.
        claim_path.write_text(
            claim_path.read_text().replace("status: supported", "status: superseded"),
            encoding="utf-8",
        )
        _write(
            feature_dir / "CL-TEST-002.yaml",
            _CLAIM_HEADER.replace("CL-TEST-001", "CL-TEST-002")
            + "\n",
        )
        (feature_dir / "CL-TEST-002.yaml").write_text(
            (feature_dir / "CL-TEST-002.yaml")
            .read_text()
            .replace("supersedes: null", "supersedes: CL-TEST-001"),
            encoding="utf-8",
        )
        _commit_all(tmp_path, "supersede CL-TEST-001 with CL-TEST-002")

        integrity_findings = check_knowledge_base.check_snapshot_historical_integrity(
            feature_dir, root=tmp_path
        )
        assert integrity_findings == [], (
            "a legitimate supersession must never be reported as "
            f"historical tampering, got: {integrity_findings}"
        )

    def test_historical_tampering_is_detected(self, tmp_path):
        """Directly corrupting a snapshot's own recorded hash (simulating
        either a hand-edited sidecar or rewritten git history) must be
        caught."""
        feature_dir, rev, content_hash = self._build_base_repo(tmp_path)
        snapshot_path = feature_dir / "snapshots" / "snapshot-v1.toml"
        tampered = snapshot_path.read_text().replace(
            content_hash, "0" * 64  # a deliberately wrong hash
        )
        snapshot_path.write_text(tampered, encoding="utf-8")

        findings = check_knowledge_base.check_snapshot_historical_integrity(
            feature_dir, root=tmp_path
        )
        assert len(findings) == 1
        assert findings[0].rule == "knowledge-base-snapshot-tampering"
        assert findings[0].strict

    def test_current_change_triggers_reassessment_divergence(self, tmp_path):
        """A change to the *current* file (not a formal supersession —
        just a direct edit) must be surfaced as a current-divergence
        finding, informationally, never failing --strict on its own."""
        feature_dir, rev, content_hash = self._build_base_repo(tmp_path)
        claim_path = feature_dir / "CL-TEST-001.yaml"
        claim_path.write_text(
            claim_path.read_text().replace(
                "statement: test statement", "statement: a changed statement"
            ),
            encoding="utf-8",
        )
        _commit_all(tmp_path, "edit CL-TEST-001's statement directly")

        integrity_findings = check_knowledge_base.check_snapshot_historical_integrity(
            feature_dir, root=tmp_path
        )
        assert integrity_findings == [], (
            "the historical blob at the frozen revision is untouched -- "
            "only the current file changed"
        )

        divergence_findings = check_knowledge_base.check_snapshot_current_divergence(
            feature_dir, root=tmp_path
        )
        assert len(divergence_findings) == 1
        assert divergence_findings[0].rule == "knowledge-base-snapshot-current-divergence"
        assert not divergence_findings[0].strict, (
            "a current-record divergence must never fail --strict on its own"
        )

    def test_legitimate_supersession_is_also_completeness_clean(self, tmp_path):
        """The same legitimate-supersession scenario above must also
        produce zero completeness findings -- a lifecycle transition is
        not truncation."""
        feature_dir, rev, content_hash = self._build_base_repo(tmp_path)
        claim_path = feature_dir / "CL-TEST-001.yaml"
        claim_path.write_text(
            claim_path.read_text().replace("status: supported", "status: superseded"),
            encoding="utf-8",
        )
        _commit_all(tmp_path, "supersede CL-TEST-001 in place")

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        assert findings == [], f"a legitimate lifecycle change must not be flagged: {findings}"


_CLAIM_WITH_EVIDENCE_HEADER = """\
id: CL-TEST-001
kind: claim
statement: test statement
derivation: DE-TEST-001
supporting_evidence: [EV-TEST-001, EV-TEST-002]
contradicting_evidence: []
derived_by: test
repository_revision: "working tree"
timestamp: "2026-10-01T00:00:00Z"
status: supported
supersedes: null
"""


class TestSnapshotCompleteness:
    """`check_snapshot_completeness` — fail-closed structural/completeness
    validation, distinct from `check_snapshot_historical_integrity`'s own
    hash-tampering check (which only validates entries already present,
    and so accepts a sidecar truncated down to nothing). Exercised
    against real, disposable git fixtures per the user's own explicit
    instruction covering: incomplete snapshots, omitted closure entries,
    malformed structures, tampering (already covered above, unaffected by
    this check), and legitimate lifecycle changes (immediately above)."""

    def _build_repo_with_evidence(self, tmp_path: Path) -> tuple[Path, str]:
        """A base repo with one Claim citing two Evidence records plus a
        Derivation, and a complete snapshot capturing all of it —
        returned alongside the freeze revision so each test can mutate
        the snapshot (not the records) into a specific broken shape."""
        feature_dir = tmp_path / "planning" / "knowledge" / "test-topic"
        _write(feature_dir / "CL-TEST-001.yaml", _CLAIM_WITH_EVIDENCE_HEADER)
        _write(
            feature_dir / "EV-TEST-001.yaml",
            "id: EV-TEST-001\nkind: evidence\nevidence_kind: source\n"
            "what_it_shows: test\nrepository_revision: \"working tree\"\n"
            "status: current\n",
        )
        _write(
            feature_dir / "EV-TEST-002.yaml",
            "id: EV-TEST-002\nkind: evidence\nevidence_kind: source\n"
            "what_it_shows: test\nrepository_revision: \"working tree\"\n"
            "status: current\n",
        )
        _write(
            feature_dir / "DE-TEST-001.yaml",
            "id: DE-TEST-001\nkind: derivation\nclaim: CL-TEST-001\n"
            "method: test\ninputs: []\nperformed_by: test\n"
            'timestamp: "2026-10-01T00:00:00Z"\n',
        )
        _init_git_repo(tmp_path)
        rev = _commit_all(tmp_path, "add CL-TEST-001 + evidence + derivation")

        def _hash(name: str) -> str:
            return _sha256_file(feature_dir / name)

        snapshots_dir = feature_dir / "snapshots"
        snapshots_dir.mkdir(parents=True)
        prefix = "planning/knowledge/test-topic"
        snapshot_toml = f"""\
snapshot_id = "test-topic@v1"
created = "2026-10-01T00:00:00Z"
repository_revision_at_freeze = "{rev}"
excluded_assertions = []

[assertions."CL-TEST-001"]
path = "{prefix}/CL-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{_hash("CL-TEST-001.yaml")}"

[assertions."CL-TEST-001".supporting_evidence."EV-TEST-001"]
path = "{prefix}/EV-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{_hash("EV-TEST-001.yaml")}"

[assertions."CL-TEST-001".supporting_evidence."EV-TEST-002"]
path = "{prefix}/EV-TEST-002.yaml"
repository_revision = "{rev}"
content_hash = "{_hash("EV-TEST-002.yaml")}"

[assertions."CL-TEST-001".derivation."DE-TEST-001"]
path = "{prefix}/DE-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{_hash("DE-TEST-001.yaml")}"
"""
        snapshot_path = snapshots_dir / "snapshot-v1.toml"
        _write(snapshot_path, snapshot_toml)
        _commit_all(tmp_path, "freeze complete snapshot-v1")
        return feature_dir, rev

    def test_complete_snapshot_has_no_findings(self, tmp_path):
        feature_dir, rev = self._build_repo_with_evidence(tmp_path)
        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        assert findings == []

    def test_gutted_snapshot_reduced_to_only_snapshot_id(self, tmp_path):
        """The exact scenario named explicitly: a sidecar reduced to only
        `snapshot_id` must not silently validate clean just because it
        has no entries left to hash."""
        feature_dir, rev = self._build_repo_with_evidence(tmp_path)
        snapshot_path = feature_dir / "snapshots" / "snapshot-v1.toml"
        snapshot_path.write_text('snapshot_id = "test-topic@v1"\n', encoding="utf-8")

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        rules = {f.rule for f in findings}
        assert "knowledge-base-snapshot-missing-metadata" in rules
        assert all(f.strict for f in findings), "a gutted snapshot must fail --strict"
        # historical-integrity must not crash on this either, even though
        # it has nothing left to hash:
        integrity_findings = check_knowledge_base.check_snapshot_historical_integrity(
            feature_dir, root=tmp_path
        )
        assert integrity_findings == []

    def _write_cl_test_001_and_closure(self, feature_dir: Path) -> None:
        """`CL-TEST-001` plus the real `EV-TEST-001`/`DE-TEST-001` records
        it cites (`_CLAIM_HEADER`'s own `supporting_evidence`/
        `derivation` fields) — shared setup for tests whose own subject
        is the assertion-inventory logic, not closure, so a captured
        `CL-TEST-001` entry should itself be closure-complete and produce
        no incidental closure findings."""
        _write(feature_dir / "CL-TEST-001.yaml", _CLAIM_HEADER)
        _write(
            feature_dir / "EV-TEST-001.yaml",
            "id: EV-TEST-001\nkind: evidence\nevidence_kind: source\n"
            "what_it_shows: test\nrepository_revision: \"working tree\"\n"
            "status: current\n",
        )
        _write(
            feature_dir / "DE-TEST-001.yaml",
            "id: DE-TEST-001\nkind: derivation\nclaim: CL-TEST-001\n"
            "method: test\ninputs: []\nperformed_by: test\n"
            'timestamp: "2026-10-01T00:00:00Z"\n',
        )

    def test_missing_assertion_entirely_omitted(self, tmp_path):
        """An entire real Claim silently dropped from the snapshot's own
        assertions table (not excluded) must be flagged — the case a
        naive per-entry-only hash check cannot see at all."""
        feature_dir = tmp_path / "planning" / "knowledge" / "test-topic"
        self._write_cl_test_001_and_closure(feature_dir)
        _write(
            feature_dir / "CL-TEST-002.yaml",
            _CLAIM_HEADER.replace("CL-TEST-001", "CL-TEST-002"),
        )
        _init_git_repo(tmp_path)
        rev = _commit_all(tmp_path, "add two claims + CL-TEST-001's closure")
        snapshots_dir = feature_dir / "snapshots"
        snapshots_dir.mkdir(parents=True)
        prefix = "planning/knowledge/test-topic"
        cl_hash = _sha256_file(feature_dir / "CL-TEST-001.yaml")
        ev_hash = _sha256_file(feature_dir / "EV-TEST-001.yaml")
        de_hash = _sha256_file(feature_dir / "DE-TEST-001.yaml")
        # Snapshot captures CL-TEST-001 completely (including its own
        # closure), but silently omits CL-TEST-002 entirely -- never
        # excluded, just dropped.
        snapshot_toml = f"""\
snapshot_id = "test-topic@v1"
created = "2026-10-01T00:00:00Z"
repository_revision_at_freeze = "{rev}"
excluded_assertions = []

[assertions."CL-TEST-001"]
path = "{prefix}/CL-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{cl_hash}"

[assertions."CL-TEST-001".supporting_evidence."EV-TEST-001"]
path = "{prefix}/EV-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{ev_hash}"

[assertions."CL-TEST-001".derivation."DE-TEST-001"]
path = "{prefix}/DE-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{de_hash}"
"""
        _write(snapshots_dir / "snapshot-v1.toml", snapshot_toml)
        _commit_all(tmp_path, "freeze incomplete snapshot")

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        assert len(findings) == 1
        assert findings[0].rule == "knowledge-base-snapshot-missing-assertion"
        assert "CL-TEST-002" in findings[0].message
        assert findings[0].strict

    def test_excluded_assertion_is_not_flagged_missing(self, tmp_path):
        """A real Claim explicitly named in `excluded_assertions` (e.g.
        still `proposed`, deliberately left out of the frozen set) must
        never be flagged as missing — this is the documented, legitimate
        exclusion mechanism, not truncation."""
        feature_dir = tmp_path / "planning" / "knowledge" / "test-topic"
        self._write_cl_test_001_and_closure(feature_dir)
        _write(
            feature_dir / "CL-TEST-002.yaml",
            _CLAIM_HEADER.replace("CL-TEST-001", "CL-TEST-002"),
        )
        _init_git_repo(tmp_path)
        rev = _commit_all(tmp_path, "add two claims + CL-TEST-001's closure")
        snapshots_dir = feature_dir / "snapshots"
        snapshots_dir.mkdir(parents=True)
        prefix = "planning/knowledge/test-topic"
        cl_hash = _sha256_file(feature_dir / "CL-TEST-001.yaml")
        ev_hash = _sha256_file(feature_dir / "EV-TEST-001.yaml")
        de_hash = _sha256_file(feature_dir / "DE-TEST-001.yaml")
        snapshot_toml = f"""\
snapshot_id = "test-topic@v1"
created = "2026-10-01T00:00:00Z"
repository_revision_at_freeze = "{rev}"
excluded_assertions = ["CL-TEST-002"]

[assertions."CL-TEST-001"]
path = "{prefix}/CL-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{cl_hash}"

[assertions."CL-TEST-001".supporting_evidence."EV-TEST-001"]
path = "{prefix}/EV-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{ev_hash}"

[assertions."CL-TEST-001".derivation."DE-TEST-001"]
path = "{prefix}/DE-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{de_hash}"
"""
        _write(snapshots_dir / "snapshot-v1.toml", snapshot_toml)
        _commit_all(tmp_path, "freeze snapshot excluding CL-TEST-002")

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        assert findings == []

    def test_a_claim_created_after_freeze_is_not_flagged_missing(self, tmp_path):
        """A Claim created *after* a snapshot's own freeze revision must
        never be flagged as missing from it — ordinary history, exactly
        the scenario that motivated checking the historical directory
        listing at `repository_revision_at_freeze`, never the live
        filesystem."""
        feature_dir, rev = self._build_repo_with_evidence(tmp_path)
        # A later Claim, added after the snapshot above was already frozen.
        _write(
            feature_dir / "CL-TEST-999.yaml",
            _CLAIM_HEADER.replace("CL-TEST-001", "CL-TEST-999"),
        )
        _commit_all(tmp_path, "add a later claim, after the snapshot was frozen")

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        assert findings == [], (
            f"a Claim created after freeze time must not be flagged: {findings}"
        )

    def test_omitted_evidence_closure_entry_flagged(self, tmp_path):
        """A captured assertion that silently drops one of its own real,
        cited Evidence records — the exact "missing Evidence/Derivation
        tables are not checked against historical Claims" gap named
        explicitly."""
        feature_dir, rev = self._build_repo_with_evidence(tmp_path)
        snapshot_path = feature_dir / "snapshots" / "snapshot-v1.toml"
        text = snapshot_path.read_text()
        # Remove the EV-TEST-002 sub-table entirely, leaving EV-TEST-001
        # and the derivation intact -- the claim itself still "validates"
        # by its own top-level hash.
        import re as _re

        text = _re.sub(
            r'\[assertions\."CL-TEST-001"\.supporting_evidence\."EV-TEST-002"\]\n'
            r"(?:.+\n)*?(?=\n|\Z)",
            "",
            text,
        )
        snapshot_path.write_text(text, encoding="utf-8")

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        closure_findings = [
            f for f in findings if f.rule == "knowledge-base-snapshot-incomplete-closure"
        ]
        assert len(closure_findings) == 1
        assert "EV-TEST-002" in closure_findings[0].message
        assert closure_findings[0].strict

    def test_omitted_derivation_closure_entry_flagged(self, tmp_path):
        feature_dir, rev = self._build_repo_with_evidence(tmp_path)
        snapshot_path = feature_dir / "snapshots" / "snapshot-v1.toml"
        text = snapshot_path.read_text()
        import re as _re

        text = _re.sub(
            r'\[assertions\."CL-TEST-001"\.derivation\."DE-TEST-001"\]\n'
            r"(?:.+\n)*?(?=\n|\Z)",
            "",
            text,
        )
        snapshot_path.write_text(text, encoding="utf-8")

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        closure_findings = [
            f for f in findings if f.rule == "knowledge-base-snapshot-incomplete-closure"
        ]
        assert len(closure_findings) == 1
        assert "DE-TEST-001" in closure_findings[0].message

    def test_malformed_assertions_table_is_a_finding_not_a_crash(self, tmp_path):
        """`assertions` present but the wrong TOML type (a string instead
        of a table) must produce an actionable finding, never an uncaught
        exception."""
        feature_dir, rev = self._build_repo_with_evidence(tmp_path)
        snapshot_path = feature_dir / "snapshots" / "snapshot-v1.toml"
        snapshot_path.write_text(
            'snapshot_id = "test-topic@v1"\n'
            'created = "2026-10-01T00:00:00Z"\n'
            f'repository_revision_at_freeze = "{rev}"\n'
            "excluded_assertions = []\n"
            'assertions = "not a table"\n',
            encoding="utf-8",
        )

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        assert any(f.rule == "knowledge-base-snapshot-malformed-structure" for f in findings)
        # must not have crashed the other snapshot checks either:
        check_knowledge_base.check_snapshot_historical_integrity(feature_dir, root=tmp_path)
        check_knowledge_base.check_snapshot_current_divergence(feature_dir, root=tmp_path)

    def test_malformed_excluded_assertions_is_a_finding_not_a_crash(self, tmp_path):
        feature_dir, rev = self._build_repo_with_evidence(tmp_path)
        snapshot_path = feature_dir / "snapshots" / "snapshot-v1.toml"
        text = snapshot_path.read_text().replace(
            "excluded_assertions = []", 'excluded_assertions = "CL-TEST-001"'
        )
        snapshot_path.write_text(text, encoding="utf-8")

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        assert any(f.rule == "knowledge-base-snapshot-malformed-structure" for f in findings)

    def test_identity_mismatch_flagged(self, tmp_path):
        """An assertion's own `path` resolves to a real record whose `id:`
        field doesn't match the key it was filed under in the snapshot —
        a copy-paste/key-typo defect, not tampering (the hash itself may
        still be internally consistent)."""
        feature_dir = tmp_path / "planning" / "knowledge" / "test-topic"
        _write(feature_dir / "CL-TEST-001.yaml", _CLAIM_HEADER)
        _init_git_repo(tmp_path)
        rev = _commit_all(tmp_path, "add CL-TEST-001")
        content_hash = _sha256_file(feature_dir / "CL-TEST-001.yaml")
        snapshots_dir = feature_dir / "snapshots"
        snapshots_dir.mkdir(parents=True)
        prefix = "planning/knowledge/test-topic"
        # Filed under the wrong key, "CL-TEST-999", even though the real
        # record's own id: field says CL-TEST-001.
        snapshot_toml = f"""\
snapshot_id = "test-topic@v1"
created = "2026-10-01T00:00:00Z"
repository_revision_at_freeze = "{rev}"
excluded_assertions = ["CL-TEST-001"]

[assertions."CL-TEST-999"]
path = "{prefix}/CL-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{content_hash}"
"""
        _write(snapshots_dir / "snapshot-v1.toml", snapshot_toml)
        _commit_all(tmp_path, "freeze snapshot with a key/id mismatch")

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        identity_findings = [
            f for f in findings if f.rule == "knowledge-base-snapshot-identity-mismatch"
        ]
        assert len(identity_findings) == 1
        assert "CL-TEST-999" in identity_findings[0].message
        assert "CL-TEST-001" in identity_findings[0].message


class TestNestedEntryValidation:
    """Closes a real gap the sixth amendment found: a nested
    `supporting_evidence`/`contradicting_evidence`/`derivation` entry's
    own *key* being present was previously enough to count as "captured,"
    regardless of whether the entry's own *value* was a well-formed table
    or whether it actually identified the record its key claims to.
    Exercises three real attack shapes against a real, disposable git
    fixture: a nested table replaced by a scalar, a key kept but its
    entry re-pointed at a *different* real record (an identity swap, not
    a hash mismatch -- the swapped-in record's own hash is genuinely
    correct for what it actually is), and the equivalent for Derivations.
    """

    def _build_repo_with_two_evidence_and_two_derivations(
        self, tmp_path: Path
    ) -> tuple[Path, str, dict[str, str]]:
        feature_dir = tmp_path / "planning" / "knowledge" / "test-topic"
        # Deliberately cites only ONE of each (EV-TEST-001, DE-TEST-001) --
        # EV-TEST-002/DE-TEST-002 exist as real records this fixture can
        # swap an entry's identity to point at, but are not themselves
        # cited by CL-TEST-001, so a valid baseline snapshot need not
        # capture them.
        _write(
            feature_dir / "CL-TEST-001.yaml",
            "id: CL-TEST-001\nkind: claim\nstatement: test statement\n"
            "derivation: DE-TEST-001\nsupporting_evidence: [EV-TEST-001]\n"
            "contradicting_evidence: []\nderived_by: test\n"
            'repository_revision: "working tree"\ntimestamp: "2026-10-01T00:00:00Z"\n'
            "status: supported\nsupersedes: null\n",
        )
        _write(
            feature_dir / "EV-TEST-001.yaml",
            "id: EV-TEST-001\nkind: evidence\nevidence_kind: source\n"
            "what_it_shows: the real EV-TEST-001\n"
            'repository_revision: "working tree"\nstatus: current\n',
        )
        _write(
            feature_dir / "EV-TEST-002.yaml",
            "id: EV-TEST-002\nkind: evidence\nevidence_kind: source\n"
            "what_it_shows: a completely different real record, EV-TEST-002\n"
            'repository_revision: "working tree"\nstatus: current\n',
        )
        _write(
            feature_dir / "DE-TEST-001.yaml",
            "id: DE-TEST-001\nkind: derivation\nclaim: CL-TEST-001\n"
            "method: the real DE-TEST-001\ninputs: []\nperformed_by: test\n"
            'timestamp: "2026-10-01T00:00:00Z"\n',
        )
        _write(
            feature_dir / "DE-TEST-002.yaml",
            "id: DE-TEST-002\nkind: derivation\nclaim: CL-TEST-001\n"
            "method: a completely different real record, DE-TEST-002\n"
            'inputs: []\nperformed_by: test\ntimestamp: "2026-10-01T00:00:00Z"\n',
        )
        _init_git_repo(tmp_path)
        rev = _commit_all(tmp_path, "add CL-TEST-001 + two evidence + two derivations")

        hashes = {
            name: _sha256_file(feature_dir / f"{name}.yaml")
            for name in ("CL-TEST-001", "EV-TEST-001", "EV-TEST-002", "DE-TEST-001", "DE-TEST-002")
        }

        snapshots_dir = feature_dir / "snapshots"
        snapshots_dir.mkdir(parents=True)
        prefix = "planning/knowledge/test-topic"
        snapshot_toml = f"""\
snapshot_id = "test-topic@v1"
created = "2026-10-01T00:00:00Z"
repository_revision_at_freeze = "{rev}"
excluded_assertions = []

[assertions."CL-TEST-001"]
path = "{prefix}/CL-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["CL-TEST-001"]}"

[assertions."CL-TEST-001".supporting_evidence."EV-TEST-001"]
path = "{prefix}/EV-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["EV-TEST-001"]}"

[assertions."CL-TEST-001".derivation."DE-TEST-001"]
path = "{prefix}/DE-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["DE-TEST-001"]}"
"""
        snapshot_path = snapshots_dir / "snapshot-v1.toml"
        _write(snapshot_path, snapshot_toml)
        _commit_all(tmp_path, "freeze complete, valid snapshot-v1")
        return feature_dir, rev, hashes

    def test_baseline_complete_snapshot_passes(self, tmp_path):
        feature_dir, rev, hashes = self._build_repo_with_two_evidence_and_two_derivations(
            tmp_path
        )
        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        assert findings == []
        integrity_findings = check_knowledge_base.check_snapshot_historical_integrity(
            feature_dir, root=tmp_path
        )
        assert integrity_findings == []

    def test_scalar_in_place_of_evidence_table_is_blocking_finding(self, tmp_path):
        """Attack 1: a required nested Evidence table is replaced by a
        scalar string. The key `EV-TEST-001` is still present, but a
        checker that only inspects dict *keys* would wrongly treat this
        as captured."""
        feature_dir, rev, hashes = self._build_repo_with_two_evidence_and_two_derivations(
            tmp_path
        )
        snapshot_path = feature_dir / "snapshots" / "snapshot-v1.toml"
        text = f"""\
snapshot_id = "test-topic@v1"
created = "2026-10-01T00:00:00Z"
repository_revision_at_freeze = "{rev}"
excluded_assertions = []

[assertions."CL-TEST-001"]
path = "planning/knowledge/test-topic/CL-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["CL-TEST-001"]}"
supporting_evidence = {{"EV-TEST-001" = "not a table at all"}}

[assertions."CL-TEST-001".derivation."DE-TEST-001"]
path = "planning/knowledge/test-topic/DE-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["DE-TEST-001"]}"
"""
        snapshot_path.write_text(text, encoding="utf-8")

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        malformed = [f for f in findings if f.rule == "knowledge-base-snapshot-malformed-structure"]
        closure = [f for f in findings if f.rule == "knowledge-base-snapshot-incomplete-closure"]
        assert len(malformed) == 1, findings
        assert "EV-TEST-001" in malformed[0].message
        assert malformed[0].strict
        assert len(closure) == 1, (
            "a malformed nested entry must not count as satisfying closure"
        )
        assert "EV-TEST-001" in closure[0].message
        assert closure[0].strict

        # Must not crash the hash-integrity pass either (it independently
        # iterates well-formed dict entries only, via _iter_snapshot_entries).
        check_knowledge_base.check_snapshot_historical_integrity(feature_dir, root=tmp_path)

    def test_evidence_identity_swap_is_blocking_finding(self, tmp_path):
        """Attack 2: the key `EV-TEST-001` is kept, but its entry's own
        `path`/`content_hash` are re-pointed at the real `EV-TEST-002`
        record, with `EV-TEST-002`'s own genuinely correct hash. The hash
        itself is not tampered -- it is exactly right for what it points
        to -- so a pure hash-integrity check would not catch this; only
        checking the pointed-to record's own `id` against the key it was
        filed under does."""
        feature_dir, rev, hashes = self._build_repo_with_two_evidence_and_two_derivations(
            tmp_path
        )
        snapshot_path = feature_dir / "snapshots" / "snapshot-v1.toml"
        text = f"""\
snapshot_id = "test-topic@v1"
created = "2026-10-01T00:00:00Z"
repository_revision_at_freeze = "{rev}"
excluded_assertions = []

[assertions."CL-TEST-001"]
path = "planning/knowledge/test-topic/CL-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["CL-TEST-001"]}"

[assertions."CL-TEST-001".supporting_evidence."EV-TEST-001"]
path = "planning/knowledge/test-topic/EV-TEST-002.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["EV-TEST-002"]}"

[assertions."CL-TEST-001".derivation."DE-TEST-001"]
path = "planning/knowledge/test-topic/DE-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["DE-TEST-001"]}"
"""
        snapshot_path.write_text(text, encoding="utf-8")

        # The swapped-in hash is genuinely correct for EV-TEST-002's own
        # content, so the pure tampering check must NOT flag this as a
        # hash mismatch -- confirming the identity swap is invisible to
        # hash-integrity alone, and only the identity check catches it.
        integrity_findings = check_knowledge_base.check_snapshot_historical_integrity(
            feature_dir, root=tmp_path
        )
        assert integrity_findings == [], (
            "a correctly-hashed identity swap must not be reported as "
            f"tampering (that would be the wrong diagnosis): {integrity_findings}"
        )

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        identity = [f for f in findings if f.rule == "knowledge-base-snapshot-identity-mismatch"]
        closure = [f for f in findings if f.rule == "knowledge-base-snapshot-incomplete-closure"]
        assert len(identity) == 1, findings
        assert "EV-TEST-001" in identity[0].message and "EV-TEST-002" in identity[0].message
        assert identity[0].strict
        assert len(closure) == 1, (
            "an identity-swapped nested entry must not count as satisfying "
            "closure for the id it claims to be"
        )
        assert closure[0].strict

    def test_derivation_scalar_in_place_of_table_is_blocking_finding(self, tmp_path):
        """Attack 3 (Derivation equivalent of attack 1)."""
        feature_dir, rev, hashes = self._build_repo_with_two_evidence_and_two_derivations(
            tmp_path
        )
        snapshot_path = feature_dir / "snapshots" / "snapshot-v1.toml"
        text = f"""\
snapshot_id = "test-topic@v1"
created = "2026-10-01T00:00:00Z"
repository_revision_at_freeze = "{rev}"
excluded_assertions = []

[assertions."CL-TEST-001"]
path = "planning/knowledge/test-topic/CL-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["CL-TEST-001"]}"
derivation = {{"DE-TEST-001" = "not a table at all"}}

[assertions."CL-TEST-001".supporting_evidence."EV-TEST-001"]
path = "planning/knowledge/test-topic/EV-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["EV-TEST-001"]}"
"""
        snapshot_path.write_text(text, encoding="utf-8")

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        malformed = [f for f in findings if f.rule == "knowledge-base-snapshot-malformed-structure"]
        closure = [f for f in findings if f.rule == "knowledge-base-snapshot-incomplete-closure"]
        assert len(malformed) == 1, findings
        assert "DE-TEST-001" in malformed[0].message
        assert len(closure) == 1
        assert "DE-TEST-001" in closure[0].message

    def test_derivation_identity_swap_is_blocking_finding(self, tmp_path):
        """Attack 4 (Derivation equivalent of attack 2): key `DE-TEST-001`
        kept, entry re-pointed at the real `DE-TEST-002` record with its
        own genuinely correct hash."""
        feature_dir, rev, hashes = self._build_repo_with_two_evidence_and_two_derivations(
            tmp_path
        )
        snapshot_path = feature_dir / "snapshots" / "snapshot-v1.toml"
        text = f"""\
snapshot_id = "test-topic@v1"
created = "2026-10-01T00:00:00Z"
repository_revision_at_freeze = "{rev}"
excluded_assertions = []

[assertions."CL-TEST-001"]
path = "planning/knowledge/test-topic/CL-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["CL-TEST-001"]}"

[assertions."CL-TEST-001".supporting_evidence."EV-TEST-001"]
path = "planning/knowledge/test-topic/EV-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["EV-TEST-001"]}"

[assertions."CL-TEST-001".derivation."DE-TEST-001"]
path = "planning/knowledge/test-topic/DE-TEST-002.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["DE-TEST-002"]}"
"""
        snapshot_path.write_text(text, encoding="utf-8")

        integrity_findings = check_knowledge_base.check_snapshot_historical_integrity(
            feature_dir, root=tmp_path
        )
        assert integrity_findings == []

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        identity = [f for f in findings if f.rule == "knowledge-base-snapshot-identity-mismatch"]
        closure = [f for f in findings if f.rule == "knowledge-base-snapshot-incomplete-closure"]
        assert len(identity) == 1, findings
        assert "DE-TEST-001" in identity[0].message and "DE-TEST-002" in identity[0].message
        assert len(closure) == 1

    def test_kind_mismatch_is_blocking_finding(self, tmp_path):
        """A nested `supporting_evidence` key whose own entry points at a
        real record of the *wrong kind* (a Claim, not an Evidence record)
        must be flagged, even if the id happened to match and the hash is
        genuinely correct for that (wrong-kind) file."""
        feature_dir, rev, hashes = self._build_repo_with_two_evidence_and_two_derivations(
            tmp_path
        )
        # Make a second claim whose id we can (ab)use as if it were an
        # evidence id, to exercise the kind check independent of identity.
        feature_dir2 = feature_dir
        _write(
            feature_dir2 / "CL-FAKE-EV.yaml",
            "id: CL-FAKE-EV\nkind: claim\nstatement: wrong kind entirely\n"
            "derivation: DE-TEST-001\nsupporting_evidence: []\n"
            "contradicting_evidence: []\nderived_by: test\n"
            'repository_revision: "working tree"\ntimestamp: "2026-10-01T00:00:00Z"\n'
            "status: supported\nsupersedes: null\n",
        )
        _commit_all(tmp_path, "add a wrong-kind record for the kind-mismatch test")
        rev2 = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=tmp_path, capture_output=True, text=True, check=True
        ).stdout.strip()
        fake_hash = _sha256_file(feature_dir2 / "CL-FAKE-EV.yaml")

        snapshot_path = feature_dir / "snapshots" / "snapshot-v1.toml"
        text = f"""\
snapshot_id = "test-topic@v1"
created = "2026-10-01T00:00:00Z"
repository_revision_at_freeze = "{rev2}"
excluded_assertions = []

[assertions."CL-TEST-001"]
path = "planning/knowledge/test-topic/CL-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["CL-TEST-001"]}"

[assertions."CL-TEST-001".supporting_evidence."EV-TEST-001"]
path = "planning/knowledge/test-topic/CL-FAKE-EV.yaml"
repository_revision = "{rev2}"
content_hash = "{fake_hash}"

[assertions."CL-TEST-001".derivation."DE-TEST-001"]
path = "planning/knowledge/test-topic/DE-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{hashes["DE-TEST-001"]}"
"""
        snapshot_path.write_text(text, encoding="utf-8")
        _commit_all(tmp_path, "freeze snapshot citing a wrong-kind record (via a fake matching id)")

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        kind_mismatch = [f for f in findings if f.rule == "knowledge-base-snapshot-kind-mismatch"]
        identity_mismatch = [
            f for f in findings if f.rule == "knowledge-base-snapshot-identity-mismatch"
        ]
        # The fake record's own id (CL-FAKE-EV) differs from the key
        # (EV-TEST-001) too, so this also trips identity-mismatch --
        # both are real, correct findings for this constructed case.
        assert len(identity_mismatch) == 1
        assert len(kind_mismatch) == 1, findings
        assert "evidence" in kind_mismatch[0].message


class TestAbsentIdentityFields:
    """A real gap found by direct review: `if real_id and real_id !=
    expected_id` (and the equivalent for `kind`) is a truthy guard --
    it silently skips validation when the historical content has no
    `id:`/`kind:` field at all, rather than flagging "this isn't
    identifiable as anything," which is strictly worse than a mismatch
    (a mismatch at least proves the pointed-to content IS some other
    real record). Exercises both the top-level assertion slot and a
    nested Evidence slot pointed at a committed, genuinely plain file
    (no `id:`, no `kind:` at all) with its own correct historical hash
    -- a real hash match, not tampering, which is exactly why the old
    truthy-guard code let it through."""

    def _commit_plain_file(self, tmp_path: Path, feature_dir: Path) -> tuple[str, str]:
        _write(
            feature_dir / "plain-file.yaml",
            "this is just some unrelated text content\n"
            "with no id field and no kind field at all\n",
        )
        rev = _commit_all(tmp_path, "add a plain, identity-less file")
        return rev, _sha256_file(feature_dir / "plain-file.yaml")

    def test_assertion_slot_pointed_at_identity_less_file(self, tmp_path):
        feature_dir = tmp_path / "planning" / "knowledge" / "test-topic"
        feature_dir.mkdir(parents=True)
        _init_git_repo(tmp_path)
        rev, plain_hash = self._commit_plain_file(tmp_path, feature_dir)

        snapshots_dir = feature_dir / "snapshots"
        snapshots_dir.mkdir()
        prefix = "planning/knowledge/test-topic"
        _write(
            snapshots_dir / "snapshot-v1.toml",
            f"""\
snapshot_id = "test-topic@v1"
created = "2026-10-01T00:00:00Z"
repository_revision_at_freeze = "{rev}"
excluded_assertions = []

[assertions."CL-TEST-001"]
path = "{prefix}/plain-file.yaml"
repository_revision = "{rev}"
content_hash = "{plain_hash}"
""",
        )
        _commit_all(tmp_path, "freeze assertion slot pointed at the plain file")

        # The hash is genuinely correct for the plain file's own content --
        # this must never be reported as tampering.
        integrity_findings = check_knowledge_base.check_snapshot_historical_integrity(
            feature_dir, root=tmp_path
        )
        assert integrity_findings == []

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        identity_missing = [
            f for f in findings if f.rule == "knowledge-base-snapshot-identity-missing"
        ]
        kind_missing = [f for f in findings if f.rule == "knowledge-base-snapshot-kind-missing"]
        assert len(identity_missing) == 1, findings
        assert identity_missing[0].strict
        assert len(kind_missing) == 1, findings
        assert kind_missing[0].strict

    def test_evidence_slot_pointed_at_identity_less_file(self, tmp_path):
        feature_dir = tmp_path / "planning" / "knowledge" / "test-topic"
        feature_dir.mkdir(parents=True)
        _write(feature_dir / "CL-TEST-001.yaml", _CLAIM_HEADER)
        _init_git_repo(tmp_path)
        rev, plain_hash = self._commit_plain_file(tmp_path, feature_dir)
        cl_hash = _sha256_file(feature_dir / "CL-TEST-001.yaml")

        snapshots_dir = feature_dir / "snapshots"
        snapshots_dir.mkdir()
        prefix = "planning/knowledge/test-topic"
        _write(
            snapshots_dir / "snapshot-v1.toml",
            f"""\
snapshot_id = "test-topic@v1"
created = "2026-10-01T00:00:00Z"
repository_revision_at_freeze = "{rev}"
excluded_assertions = []

[assertions."CL-TEST-001"]
path = "{prefix}/CL-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{cl_hash}"

[assertions."CL-TEST-001".supporting_evidence."EV-TEST-001"]
path = "{prefix}/plain-file.yaml"
repository_revision = "{rev}"
content_hash = "{plain_hash}"
""",
        )
        _commit_all(tmp_path, "freeze evidence slot pointed at the plain file")

        integrity_findings = check_knowledge_base.check_snapshot_historical_integrity(
            feature_dir, root=tmp_path
        )
        assert integrity_findings == []

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        identity_missing = [
            f for f in findings if f.rule == "knowledge-base-snapshot-identity-missing"
        ]
        kind_missing = [f for f in findings if f.rule == "knowledge-base-snapshot-kind-missing"]
        assert len(identity_missing) == 1, findings
        assert "EV-TEST-001" in identity_missing[0].message
        assert len(kind_missing) == 1, findings
        assert "EV-TEST-001" in kind_missing[0].message

    def test_legitimate_well_formed_entries_still_pass(self, tmp_path):
        """Regression guard: the new identity-missing/kind-missing checks
        must not fire against genuinely well-formed records that do have
        real id/kind fields."""
        feature_dir = tmp_path / "planning" / "knowledge" / "test-topic"
        _write(feature_dir / "CL-TEST-001.yaml", _CLAIM_HEADER)
        _init_git_repo(tmp_path)
        rev = _commit_all(tmp_path, "add a well-formed claim")
        cl_hash = _sha256_file(feature_dir / "CL-TEST-001.yaml")

        snapshots_dir = feature_dir / "snapshots"
        snapshots_dir.mkdir()
        prefix = "planning/knowledge/test-topic"
        _write(
            snapshots_dir / "snapshot-v1.toml",
            f"""\
snapshot_id = "test-topic@v1"
created = "2026-10-01T00:00:00Z"
repository_revision_at_freeze = "{rev}"
excluded_assertions = []

[assertions."CL-TEST-001"]
path = "{prefix}/CL-TEST-001.yaml"
repository_revision = "{rev}"
content_hash = "{cl_hash}"
""",
        )
        _commit_all(tmp_path, "freeze a well-formed snapshot")

        findings = check_knowledge_base.check_snapshot_completeness(feature_dir, root=tmp_path)
        identity_or_kind = [
            f
            for f in findings
            if f.rule
            in (
                "knowledge-base-snapshot-identity-missing",
                "knowledge-base-snapshot-kind-missing",
            )
        ]
        assert identity_or_kind == []


_DECISION_HEADER = """\
id: DEC-TEST-001
kind: decision
decides: a test decision
rationale: because this is a test
supersedes: null
decided_by: test
timestamp: "2026-10-01T00:00:00Z"
status: {status}
"""

_REQUIREMENT_HEADER = """\
id: REQ-TEST-001
kind: requirement
statement: a test requirement
example: |
  Given a test
  When it runs
  Then it passes
decision: DEC-TEST-001
status: proposed
"""


class TestRequirementCitesApprovedDecision:
    """Phase 81 (planning/phase-81-intermediate-knowledge-layer.md
    §11/§14.3): the real gap this check closes — before it existed, a
    Requirement's `decision:` field was only checked for *resolving* to
    some real record (`check_cross_references_resolve`), never for that
    record actually being an `approved` Decision. Reproduced here before
    confirming the fix, per this project's own established discipline."""

    def test_approved_decision_no_finding(self, tmp_path):
        _write(tmp_path / "DEC-TEST-001.yaml", _DECISION_HEADER.format(status="approved"))
        _write(tmp_path / "REQ-TEST-001.yaml", _REQUIREMENT_HEADER)
        findings = check_knowledge_base.check_requirement_cites_approved_decision(
            tmp_path, root=tmp_path
        )
        assert findings == []

    def test_proposed_decision_flagged(self, tmp_path):
        """The real gap: a Requirement citing a merely-`proposed` (not yet
        human-approved) Decision must be rejected — a Requirement is never
        free-floating, unauthorised implementation guidance
        (docs/domain/concepts/requirement.md's own invariant)."""
        _write(tmp_path / "DEC-TEST-001.yaml", _DECISION_HEADER.format(status="proposed"))
        _write(tmp_path / "REQ-TEST-001.yaml", _REQUIREMENT_HEADER)
        findings = check_knowledge_base.check_requirement_cites_approved_decision(
            tmp_path, root=tmp_path
        )
        assert len(findings) == 1
        assert findings[0].rule == "knowledge-base-requirement-cites-unapproved-decision"
        assert findings[0].strict

    def test_rejected_decision_flagged(self, tmp_path):
        _write(tmp_path / "DEC-TEST-001.yaml", _DECISION_HEADER.format(status="rejected"))
        _write(tmp_path / "REQ-TEST-001.yaml", _REQUIREMENT_HEADER)
        findings = check_knowledge_base.check_requirement_cites_approved_decision(
            tmp_path, root=tmp_path
        )
        assert len(findings) == 1
        assert findings[0].rule == "knowledge-base-requirement-cites-unapproved-decision"

    def test_superseded_decision_flagged(self, tmp_path):
        _write(tmp_path / "DEC-TEST-001.yaml", _DECISION_HEADER.format(status="superseded"))
        _write(tmp_path / "REQ-TEST-001.yaml", _REQUIREMENT_HEADER)
        findings = check_knowledge_base.check_requirement_cites_approved_decision(
            tmp_path, root=tmp_path
        )
        assert len(findings) == 1

    def test_cross_directory_approved_decision_via_fallback_map(self, tmp_path):
        """A Requirement may legitimately cite a Decision recorded in a
        different feature directory, exactly as check_cross_references_resolve
        already allows — resolved here via the all_decision_status fallback
        map, the same two-tier (local-then-global) resolution order."""
        req_dir = tmp_path / "req-feature"
        req_dir.mkdir()
        _write(req_dir / "REQ-TEST-001.yaml", _REQUIREMENT_HEADER)
        findings = check_knowledge_base.check_requirement_cites_approved_decision(
            req_dir, all_decision_status={"DEC-TEST-001": "approved"}
        )
        assert findings == []

    def test_dangling_decision_not_double_reported(self, tmp_path):
        """A decision id that resolves nowhere at all is
        check_cross_references_resolve's own concern, not this check's --
        this check must stay silent rather than crash or double-report."""
        _write(tmp_path / "REQ-TEST-001.yaml", _REQUIREMENT_HEADER)
        findings = check_knowledge_base.check_requirement_cites_approved_decision(
            tmp_path, root=tmp_path
        )
        assert findings == []

    def test_missing_decision_field_not_double_reported(self, tmp_path):
        """A Requirement missing `decision:` entirely is
        check_required_fields's own concern."""
        no_decision = _REQUIREMENT_HEADER.replace("decision: DEC-TEST-001\n", "")
        _write(tmp_path / "REQ-TEST-001.yaml", no_decision)
        findings = check_knowledge_base.check_requirement_cites_approved_decision(
            tmp_path, root=tmp_path
        )
        assert findings == []

    def test_real_repository_satisfies_this_check(self):
        """Confirmed by direct inspection before adding this check: all
        nine pre-existing Requirement records already cite an approved
        Decision, so adding this fail-closed check breaks nothing real."""
        all_decision_status: dict[str, str] = {}
        knowledge_dir = REPO_ROOT / "planning" / "knowledge"
        for feature_dir in sorted(p for p in knowledge_dir.iterdir() if p.is_dir()):
            for yaml_path in feature_dir.glob("*.yaml"):
                fields = check_knowledge_base.parse_record(yaml_path)
                if fields.get("kind") == "decision" and fields.get("id"):
                    all_decision_status[fields["id"]] = fields.get("status", "")
        findings: list[check_knowledge_base.Finding] = []
        for feature_dir in sorted(p for p in knowledge_dir.iterdir() if p.is_dir()):
            findings.extend(
                check_knowledge_base.check_requirement_cites_approved_decision(
                    feature_dir, all_decision_status
                )
            )
        assert findings == []


class TestAnchorIntegrity:
    """Phase 81 (§4.3/§11): a stable knowledge anchor in an
    `intermediate/*.md` projection must resolve to a real record of the
    matching kind — identity, not merely presence."""

    def test_no_intermediate_dir_no_finding(self, tmp_path):
        findings = check_knowledge_base.check_anchor_integrity(tmp_path, root=tmp_path)
        assert findings == []

    def test_valid_anchor_no_finding(self, tmp_path):
        _write(tmp_path / "CL-TEST-001.yaml", _CLAIM_HEADER)
        _write(
            tmp_path / "intermediate" / "overview.md",
            "<!-- codecompass-knowledge: CL-TEST-001 "
            "semantic-sha256:abc projection-sha256:def -->\n"
            "### A test claim\n\ntest statement\n"
            "<!-- /codecompass-knowledge -->\n",
        )
        findings = check_knowledge_base.check_anchor_integrity(tmp_path, root=tmp_path)
        assert findings == []

    def test_dangling_anchor_flagged(self, tmp_path):
        """The real failure mode: an anchor citing an id with no matching
        record at all — e.g. the record was deleted but the projection was
        never re-rendered."""
        _write(
            tmp_path / "intermediate" / "overview.md",
            "<!-- codecompass-knowledge: CL-GHOST-001 "
            "semantic-sha256:abc projection-sha256:def -->\n"
            "### A ghost claim\n\nno such record exists\n"
            "<!-- /codecompass-knowledge -->\n",
        )
        findings = check_knowledge_base.check_anchor_integrity(tmp_path, root=tmp_path)
        assert len(findings) == 1
        assert findings[0].rule == "knowledge-base-dangling-anchor"
        assert findings[0].strict

    def test_real_kind_mismatch_flagged(self, tmp_path):
        _write(tmp_path / "CL-TEST-001.yaml", _CLAIM_HEADER)
        _write(
            tmp_path / "intermediate" / "overview.md",
            # Deliberately contrived: rename the claim's own id so its
            # prefix (DEC-) disagrees with its real kind (claim) -- this can
            # only happen if a record's id and kind fields disagree with
            # each other, which check_required_fields's own id-prefix check
            # already guards against for the record itself; this test
            # exercises the anchor-side half of that same discipline.
            "<!-- codecompass-knowledge: DEC-MISLABEL-001 "
            "semantic-sha256:abc projection-sha256:def -->\n"
            "### Mislabelled anchor\n\ntext\n"
            "<!-- /codecompass-knowledge -->\n",
        )
        # Inject a record whose id disagrees with its own kind, to exercise
        # the anchor-side mismatch path directly.
        _write(
            tmp_path / "DEC-MISLABEL-001.yaml",
            _CLAIM_HEADER.replace("id: CL-TEST-001", "id: DEC-MISLABEL-001"),
        )
        findings = check_knowledge_base.check_anchor_integrity(tmp_path, root=tmp_path)
        assert len(findings) == 1
        assert findings[0].rule == "knowledge-base-anchor-kind-mismatch"
        assert findings[0].strict

    def test_real_repository_has_no_dangling_anchors(self):
        """Every slug's own real, rendered intermediate/*.md anchors
        resolve to a real, correctly-kinded record — confirmed directly
        against the live repository, not merely against a disposable
        fixture."""
        knowledge_dir = REPO_ROOT / "planning" / "knowledge"
        findings: list[check_knowledge_base.Finding] = []
        for feature_dir in sorted(p for p in knowledge_dir.iterdir() if p.is_dir()):
            findings.extend(
                check_knowledge_base.check_anchor_integrity(feature_dir, root=REPO_ROOT)
            )
        assert findings == []


class TestNoPendingReconciliation:
    """Phase 81B (§10): a committed `intermediate/*.md` projection must
    not be stale relative to its own canonical records. Reuses Phase 81's
    own `detect_anchor_changes` rather than re-deriving the dual-hash
    comparison a second time."""

    def _make_slug(self, tmp_path: Path, slug: str = "demo-slug") -> Path:
        sdir = tmp_path / "planning" / "knowledge" / slug
        sdir.mkdir(parents=True)
        _write(
            sdir / "CL-DEMO-001.yaml",
            "id: CL-DEMO-001\nkind: claim\nstatement: A test statement.\n"
            "derivation: null\nsupporting_evidence: []\ncontradicting_evidence: []\n"
            'derived_by: t\nrepository_revision: "working tree"\n'
            'timestamp: "2026-10-08T00:00:00Z"\nstatus: supported\n',
        )
        return sdir

    def test_no_intermediate_dir_no_finding(self, tmp_path):
        sdir = tmp_path / "planning" / "knowledge" / "empty-slug"
        sdir.mkdir(parents=True)
        findings = check_knowledge_base.check_no_pending_reconciliation(sdir, root=tmp_path)
        assert findings == []

    def test_freshly_rendered_slug_has_no_finding(self, tmp_path):
        from codecompass import knowledge_intermediate as ki

        self._make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        findings = check_knowledge_base.check_no_pending_reconciliation(
            tmp_path / "planning" / "knowledge" / "demo-slug", root=tmp_path
        )
        assert findings == []

    def test_stale_projection_after_canonical_change_is_flagged(self, tmp_path):
        """The real failure mode this check exists to catch: a canonical
        record changes, the committed projection is never re-rendered to
        catch up, and nothing else in this project's own checkers notices
        — check_anchor_integrity explicitly disclaims this in its own
        docstring ('the anchor's own semantic/projection hashes are
        reconciliation's own concern, not this structural check's')."""
        from codecompass import knowledge_intermediate as ki

        sdir = self._make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        # The canonical record changes; the committed projection is never
        # re-rendered -- exactly the gap check_anchor_integrity's own
        # docstring names as out of its own scope.
        (sdir / "CL-DEMO-001.yaml").write_text(
            (sdir / "CL-DEMO-001.yaml").read_text().replace(
                "status: supported", "status: verified"
            ),
            encoding="utf-8",
        )
        findings = check_knowledge_base.check_no_pending_reconciliation(sdir, root=tmp_path)
        assert len(findings) == 1
        assert findings[0].rule == "knowledge-base-stale-projection"
        assert findings[0].strict

    def test_live_candidate_region_addition_is_not_flagged(self, tmp_path):
        """A not-yet-reviewed addition sitting in a live `## Candidate
        additions` region is an open contribution, not drift — this check
        has no opinion on whether it should be accepted."""
        from codecompass import knowledge_intermediate as ki

        sdir = self._make_slug(tmp_path)
        ki.render_slug(tmp_path, "demo-slug")
        overview = sdir / "intermediate" / "overview.md"
        text = overview.read_text(encoding="utf-8").replace(
            ki.CANDIDATE_START + ki.CANDIDATE_END,
            ki.CANDIDATE_START + "\nA genuinely new, not-yet-reviewed fact.\n" + ki.CANDIDATE_END,
        )
        overview.write_text(text, encoding="utf-8")
        findings = check_knowledge_base.check_no_pending_reconciliation(sdir, root=tmp_path)
        assert findings == []

    def test_real_repository_has_no_pending_reconciliation(self):
        """The real repository's own committed projections, as they stand
        right now, are not stale relative to their own canonical
        records."""
        knowledge_dir = REPO_ROOT / "planning" / "knowledge"
        findings: list[check_knowledge_base.Finding] = []
        for feature_dir in sorted(p for p in knowledge_dir.iterdir() if p.is_dir()):
            findings.extend(
                check_knowledge_base.check_no_pending_reconciliation(feature_dir, root=REPO_ROOT)
            )
        assert findings == []
