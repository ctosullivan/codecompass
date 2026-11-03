"""Tests for scripts/check_knowledge_placement.py — a maintainer-only
tool, not part of the codecompass package. Imported directly from its
file path, mirroring tests/test_check_self_knowledge_quality.py's own
identical precedent (scripts/ is deliberately not a package).

Phase 86 (planning/phase-86-knowledge-placement-code-quality-review.md
§6.A/§11). Covers: ast/tokenize-scoped citation extraction (never an
ordinary string literal); `decision-citation-exists`; the real-corpus,
four-section (title/Status/Decision/Consequences) `decision-citation-
superseded` detection, including every negative control this plan's
own amendment rounds found and disclosed; parse-failure handling; line
provenance for multiline docstrings; and determinism.

**Deliberately does not assert zero findings against the real
repository** for `decision-citation-superseded` — the real `decisions/
0019` citation in `source_resolution.py` is this phase's own dogfood
candidate (§9), a genuine, independently-confirmed, pre-existing
placement defect this test suite pins by name rather than suppresses.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "check_knowledge_placement.py"
)
_spec = importlib.util.spec_from_file_location("check_knowledge_placement", _SCRIPT_PATH)
check_knowledge_placement = importlib.util.module_from_spec(_spec)
sys.modules["check_knowledge_placement"] = check_knowledge_placement
_spec.loader.exec_module(check_knowledge_placement)

REPO_ROOT = Path(__file__).resolve().parent.parent


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run(tmp_path: Path, decisions: dict[str, str], sources: dict[str, str]):
    """Writes `decisions/<name>.md` and `src/codecompass/<name>.py`
    fixtures under `tmp_path`, then runs the real check against them."""
    for name, text in decisions.items():
        _write(tmp_path / "decisions" / name, text)
    for name, text in sources.items():
        _write(tmp_path / "src" / "codecompass" / name, text)
    return check_knowledge_placement.run_all(project_root=tmp_path)


class TestExtractionBoundary:
    def test_ordinary_string_literal_is_never_a_citation(self, tmp_path):
        findings = _run(
            tmp_path,
            decisions={},
            sources={
                "mod.py": (
                    'FIXTURE_TEXT = "see decisions/0019 for context"\n'
                    "\n"
                    "def f():\n"
                    "    pass\n"
                ),
            },
        )
        assert findings == []

    def test_docstring_citation_is_detected(self, tmp_path):
        findings = _run(
            tmp_path,
            decisions={"0019-x.md": "# 0019. Something\n\n## Status\n\nAccepted\n"},
            sources={"mod.py": '"""See decisions/0019 for context."""\n'},
        )
        assert findings == []  # cites a real, non-superseded ADR -- no finding at all

    def test_comment_citation_is_detected(self, tmp_path):
        findings = _run(
            tmp_path,
            decisions={},
            sources={"mod.py": "x = 1  # see decisions/0999\n"},
        )
        assert len(findings) == 1
        assert findings[0].rule == "decision-citation-exists"
        assert "decisions/0999" in findings[0].message

    def test_multiline_docstring_citation_line_is_exact_not_the_docstring_start(self, tmp_path):
        """The fixture includes a blank line right after the opening
        `\"\"\"` (this project's own common style) specifically because a
        fixture with no leading blank line cannot distinguish a correct
        raw (`clean=False`) implementation from a buggy cleaned
        (`clean=True`, the `ast.get_docstring` default) one — the two
        give the same newline count when there is nothing to strip."""
        source = (
            "def f():\n"
            '    """\n'
            "\n"
            "    Line with decisions/0999 citation here.\n"
            '    """\n'
            "    pass\n"
        )
        findings = _run(tmp_path, decisions={}, sources={"mod.py": source})
        assert len(findings) == 1
        assert findings[0].file == "src/codecompass/mod.py"
        assert findings[0].line == 4  # the citation's own real line, not line 2 (docstring start)


class TestDecisionCitationExists:
    def test_citing_real_adr_is_unflagged(self, tmp_path):
        findings = _run(
            tmp_path,
            decisions={"0005-x.md": "# 0005. Something\n\n## Status\n\nAccepted\n"},
            sources={"mod.py": "# decisions/0005\n"},
        )
        assert findings == []

    def test_citing_nonexistent_adr_is_blocking(self, tmp_path):
        findings = _run(
            tmp_path,
            decisions={"0005-x.md": "# 0005. Something\n\n## Status\n\nAccepted\n"},
            sources={"mod.py": "# decisions/0006\n"},
        )
        assert len(findings) == 1
        assert findings[0].rule == "decision-citation-exists"
        assert findings[0].strict is True

    def test_bare_decisions_substring_with_no_digits_is_never_a_match(self, tmp_path):
        """Fail-closed minimal-content edge case (CLAUDE.md §1, L-070/
        L-075): confirms *scope* (something ran) and *depth* (a
        well-formed-looking but non-existent number is still caught,
        covered separately below) are both exercised."""
        findings = _run(
            tmp_path,
            decisions={},
            sources={"mod.py": "# see decisions/ for background, no number here\n"},
        )
        assert findings == []

    def test_wellformed_but_nonexistent_number_is_caught(self, tmp_path):
        """L-075's depth-vs-scope distinction: decisions/0000 looks
        exactly like a real citation syntactically but resolves to no
        real file."""
        findings = _run(tmp_path, decisions={}, sources={"mod.py": "# decisions/0000\n"})
        assert len(findings) == 1
        assert findings[0].rule == "decision-citation-exists"
        assert "0000" in findings[0].message


class TestEmptyAndMinimalInputs:
    def test_empty_src_tree_is_no_findings_no_crash(self, tmp_path):
        (tmp_path / "src" / "codecompass").mkdir(parents=True)
        (tmp_path / "decisions").mkdir(parents=True)
        findings = check_knowledge_placement.run_all(project_root=tmp_path)
        assert findings == []

    def test_missing_src_and_decisions_dirs_do_not_crash(self, tmp_path):
        findings = check_knowledge_placement.run_all(project_root=tmp_path)
        assert findings == []


class TestParseFailureHandling:
    def test_syntax_error_produces_blocking_diagnostic_and_does_not_crash(self, tmp_path):
        findings = _run(
            tmp_path,
            decisions={},
            sources={"broken.py": "def f(:\n    pass\n"},
        )
        assert len(findings) == 1
        assert findings[0].rule == "knowledge-placement-unparseable-source-file"
        assert findings[0].strict is True
        assert findings[0].line == 1

    def test_one_broken_file_does_not_prevent_other_files_from_being_checked(self, tmp_path):
        findings = _run(
            tmp_path,
            decisions={},
            sources={
                "broken.py": "def f(:\n    pass\n",
                "fine.py": "# decisions/0999\n",
            },
        )
        rules = sorted(f.rule for f in findings)
        assert rules == ["decision-citation-exists", "knowledge-placement-unparseable-source-file"]

    def test_unreadable_file_produces_blocking_diagnostic_not_a_crash(self, tmp_path, monkeypatch):
        _write(tmp_path / "src" / "codecompass" / "mod.py", "# decisions/0005\n")
        (tmp_path / "decisions").mkdir(parents=True)
        real_read_text = Path.read_text

        def _boom(self, *args, **kwargs):
            if self.name == "mod.py":
                raise PermissionError("denied")
            return real_read_text(self, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", _boom)
        findings = check_knowledge_placement.run_all(project_root=tmp_path)
        assert len(findings) == 1
        assert findings[0].rule == "knowledge-placement-unparseable-source-file"
        assert findings[0].strict is True


class TestRealCorpusSupersessionDetection:
    """Real-corpus fixtures, not constructed ones, per the governing
    review's explicit instruction to use actual repository examples.
    Each test reads the real decisions/*.md file directly from the
    live repository (REPO_ROOT), not a copy, confirming the design
    against the files it was actually written against."""

    def test_0061_title_attributes_0019_as_superseded(self):
        findings = check_knowledge_placement.run_all(
            project_root=REPO_ROOT,
            decisions_root=REPO_ROOT / "decisions",
            files=[REPO_ROOT / "src" / "codecompass" / "source_resolution.py"],
        )
        superseded = [f for f in findings if f.rule == "decision-citation-superseded"]
        assert any("decisions/0019" in f.message and "0061" in f.message for f in superseded)
        assert all(not f.strict for f in superseded)

    def test_0064_point_level_claim_is_not_attributed(self, tmp_path):
        """decisions/0064's real title, '`decisions/0063` point 8 is
        superseded: ...' -- 'point 8' breaks immediate adjacency, a
        narrower, point-level claim this check correctly does not
        parse as whole-ADR supersession."""
        real_0064 = (REPO_ROOT / "decisions").glob("0064-*.md")
        text = next(iter(real_0064)).read_text(encoding="utf-8")
        findings = _run(
            tmp_path,
            decisions={
                "0063-x.md": "# 0063. Something\n\n## Status\n\nAccepted\n",
                "0064-y.md": text,
            },
            sources={"mod.py": "# decisions/0063\n"},
        )
        assert findings == []

    def test_0031_consequences_self_reference_is_attributed(self, tmp_path):
        real_0031 = next(iter((REPO_ROOT / "decisions").glob("0031-*.md")))
        text = real_0031.read_text(encoding="utf-8")
        findings = _run(
            tmp_path,
            decisions={
                "0001-x.md": "# 0001. Something\n\n## Status\n\nAccepted\n",
                "0031-y.md": text,
            },
            sources={"mod.py": "# decisions/0001\n"},
        )
        superseded = [f for f in findings if f.rule == "decision-citation-superseded"]
        assert len(superseded) == 1
        assert not superseded[0].strict

    def test_0033_fully_superseded_matched_partially_superseded_not_matched(self, tmp_path):
        """decisions/0033's real Consequences text: '`decisions/0018`
        is **fully** superseded' (matched) alongside '`decisions/0017`
        is **partially** superseded' (deliberately **not** matched —
        a scoped, partial claim is not an unambiguous whole-citation
        signal) — both in the same real file, both asserted here."""
        real_0033 = next(iter((REPO_ROOT / "decisions").glob("0033-*.md")))
        text = real_0033.read_text(encoding="utf-8")
        findings = _run(
            tmp_path,
            decisions={
                "0017-x.md": "# 0017. Something\n\n## Status\n\nAccepted\n",
                "0018-x.md": "# 0018. Something\n\n## Status\n\nAccepted\n",
                "0033-y.md": text,
            },
            sources={"mod.py": "# decisions/0017 and decisions/0018\n"},
        )
        superseded_numbers = {
            f.message.split("decisions/")[1][:4]
            for f in findings
            if f.rule == "decision-citation-superseded"
        }
        assert superseded_numbers == {"0018"}

    def test_0027_negation_is_a_critical_negative_control(self, tmp_path):
        """decisions/0027's real Consequences text: '`decisions/0023`
        is **not** superseded by this ADR — both remain in force.'
        Must never be flagged: 'is... not... superseded' never
        satisfies the literal 'is [fully] superseded' pattern."""
        real_0027 = next(iter((REPO_ROOT / "decisions").glob("0027-*.md")))
        text = real_0027.read_text(encoding="utf-8")
        findings = _run(
            tmp_path,
            decisions={
                "0023-x.md": "# 0023. Something\n\n## Status\n\nAccepted\n",
                "0027-y.md": text,
            },
            sources={"mod.py": "# decisions/0023\n"},
        )
        assert findings == []

    def test_0058_context_section_mention_is_never_scanned(self, tmp_path):
        """decisions/0058's real `## Context` text contains the literal
        substring 'is superseded by direct instruction' -- discussing a
        past deferral, not declaring this ADR's own supersession of
        another. `## Context` is never scanned regardless of content."""
        real_0058 = next(iter((REPO_ROOT / "decisions").glob("0058-*.md")))
        text = real_0058.read_text(encoding="utf-8")
        findings = _run(
            tmp_path,
            decisions={"0058-y.md": text},
            sources={},
        )
        assert findings == []

    def test_0070_active_status_and_passive_decision_both_fire(self, tmp_path):
        """decisions/0070's real text: active 'Supersedes `decisions/
        0069`' in `## Status`, and passive '`decisions/0069` is
        superseded.' in `## Decision` -- both independently attribute
        0069 as superseded, confirming both patterns and both of the
        two newly-widened sections, including case-insensitivity on
        the capitalised 'Supersedes'."""
        real_0070 = next(iter((REPO_ROOT / "decisions").glob("0070-*.md")))
        text = real_0070.read_text(encoding="utf-8")
        findings = _run(
            tmp_path,
            decisions={
                "0069-x.md": "# 0069. Something\n\n## Status\n\nAccepted\n",
                "0070-y.md": text,
            },
            sources={"mod.py": "# decisions/0069\n"},
        )
        superseded = [f for f in findings if f.rule == "decision-citation-superseded"]
        assert len(superseded) == 1
        assert not superseded[0].strict

    def test_0043_and_0078_active_voice_capture_the_cited_number(self, tmp_path):
        real_0043 = next(iter((REPO_ROOT / "decisions").glob("0043-*.md")))
        real_0078 = next(iter((REPO_ROOT / "decisions").glob("0078-*.md")))
        findings = _run(
            tmp_path,
            decisions={
                "0041-x.md": "# 0041. Something\n\n## Status\n\nAccepted\n",
                "0043-y.md": real_0043.read_text(encoding="utf-8"),
                "0062-x.md": "# 0062. Something\n\n## Status\n\nAccepted\n",
                "0078-y.md": real_0078.read_text(encoding="utf-8"),
            },
            sources={"mod.py": "# decisions/0041 and decisions/0062\n"},
        )
        superseded_numbers = {
            f.message.split("decisions/")[1][:4]
            for f in findings
            if f.rule == "decision-citation-superseded"
        }
        assert superseded_numbers == {"0041", "0062"}

    def test_0032_conjunction_gap_is_disclosed_not_silent(self, tmp_path):
        """decisions/0032's real Consequences text: '`decisions/0024`
        and `decisions/0025` are superseded by this ADR' -- only
        `0025` (immediately adjacent to the verb) is captured; `0024`
        is honestly **not** captured. This test asserts the documented
        gap exists exactly as disclosed (§6.A), not papered over."""
        real_0032 = next(iter((REPO_ROOT / "decisions").glob("0032-*.md")))
        text = real_0032.read_text(encoding="utf-8")
        findings = _run(
            tmp_path,
            decisions={
                "0024-x.md": "# 0024. Something\n\n## Status\n\nAccepted\n",
                "0025-x.md": "# 0025. Something\n\n## Status\n\nAccepted\n",
                "0032-y.md": text,
            },
            sources={"mod.py": "# decisions/0024 and decisions/0025\n"},
        )
        superseded_numbers = {
            f.message.split("decisions/")[1][:4]
            for f in findings
            if f.rule == "decision-citation-superseded"
        }
        assert superseded_numbers == {"0025"}  # 0024 disclosed-gap, not captured

    def test_nonstandard_section_name_is_never_scanned(self, tmp_path):
        findings = _run(
            tmp_path,
            decisions={
                "0001-x.md": "# 0001. Something\n\n## Status\n\nAccepted\n",
                "0002-y.md": (
                    "# 0002. Something else\n\n## Status\n\nAccepted\n\n"
                    "## Restated\n\n`decisions/0001` is superseded by `decisions/0002`.\n"
                ),
            },
            sources={"mod.py": "# decisions/0001\n"},
        )
        assert findings == []


class TestDecisionCitationStatusMismatchIsDeferred:
    """decision-citation-status-mismatch is deferred, not shipped
    (§6.A/§7/§12/§13) -- nothing to test until it ships. This test
    exists only to assert the rule name never appears in any real
    output, guarding against an accidental future reintroduction
    without the independently testable annotation convention §13
    item 2 requires."""

    def test_rule_name_never_appears_in_real_corpus_run(self):
        findings = check_knowledge_placement.run_all(project_root=REPO_ROOT)
        assert not any(f.rule == "decision-citation-status-mismatch" for f in findings)


class TestDeterminism:
    def test_repeated_runs_are_byte_identical(self):
        first = check_knowledge_placement.run_all(project_root=REPO_ROOT)
        second = check_knowledge_placement.run_all(project_root=REPO_ROOT)
        assert [(f.file, f.line, f.rule, f.message, f.strict) for f in first] == [
            (f.file, f.line, f.rule, f.message, f.strict) for f in second
        ]

    def test_output_is_sorted_by_file_then_line_then_rule(self):
        findings = check_knowledge_placement.run_all(project_root=REPO_ROOT)
        keys = [(f.file, f.line, f.rule) for f in findings]
        assert keys == sorted(keys)


class TestRealCorpusBaseline:
    def test_source_resolution_dogfood_finding_is_present(self):
        """Pins the specific, independently-confirmed real finding
        this phase's own dogfood (§9) is grounded in -- never
        suppressed to make this test pass."""
        findings = check_knowledge_placement.run_all(project_root=REPO_ROOT)
        assert any(
            f.rule == "decision-citation-superseded"
            and "source_resolution.py" in f.file
            and "decisions/0019" in f.message
            for f in findings
        )

    def test_no_decision_citation_exists_false_positives_on_real_corpus(self):
        findings = check_knowledge_placement.run_all(project_root=REPO_ROOT)
        exists_findings = [f for f in findings if f.rule == "decision-citation-exists"]
        assert exists_findings == []

    def test_no_unparseable_source_file_findings_on_real_corpus(self):
        findings = check_knowledge_placement.run_all(project_root=REPO_ROOT)
        assert not any(f.rule == "knowledge-placement-unparseable-source-file" for f in findings)

    def test_does_not_duplicate_check_self_knowledge_quality_rule_names(self):
        self_knowledge_rules = {
            "self-knowledge-quality-missing-contract",
            "self-knowledge-quality-needs-review",
            "self-knowledge-quality-concurrent-conflict",
            "self-knowledge-quality-missing-evidence",
            "self-knowledge-quality-missing-test-ref-file",
            "self-knowledge-quality-malformed-test-ref-file",
            "self-knowledge-quality-unreadable-test-ref-file",
            "self-knowledge-quality-duplicate-statement",
            "self-knowledge-quality-possible-evidence-overlap",
            "self-knowledge-quality-contradiction",
            "self-knowledge-quality-unverified-required-scope",
            "self-knowledge-quality-stale-test-citation",
        }
        placement_rules = {
            f.rule for f in check_knowledge_placement.run_all(project_root=REPO_ROOT)
        }
        assert placement_rules.isdisjoint(self_knowledge_rules)


class TestCliStrictExitCode:
    def test_strict_exits_zero_when_only_informational_findings(self, monkeypatch, capsys):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "check_knowledge_placement.py",
                "--strict",
                "--files",
                "src/codecompass/source_resolution.py",
            ],
        )
        monkeypatch.chdir(REPO_ROOT)
        exit_code = check_knowledge_placement.main()
        assert exit_code == 0

    def test_strict_exits_one_when_a_blocking_finding_exists(self, tmp_path, monkeypatch, capsys):
        broken = tmp_path / "broken.py"
        broken.write_text("def f(:\n    pass\n", encoding="utf-8")
        monkeypatch.setattr(
            sys, "argv", ["check_knowledge_placement.py", "--strict", "--files", str(broken)]
        )
        exit_code = check_knowledge_placement.main()
        assert exit_code == 1
