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
