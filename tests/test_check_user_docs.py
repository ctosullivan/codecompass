"""Tests for scripts/check_user_docs.py — a maintainer-only tool, not part
of the codecompass package. Imported directly from its file path since
scripts/ is deliberately not a package (see planning/phase-36-docs-sync-
tooling.md)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "check_user_docs.py"
_spec = importlib.util.spec_from_file_location("check_user_docs", _SCRIPT_PATH)
check_user_docs = importlib.util.module_from_spec(_spec)
sys.modules["check_user_docs"] = check_user_docs
_spec.loader.exec_module(check_user_docs)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_no_false_positives_against_real_repo():
    findings = check_user_docs.run_all(REPO_ROOT)
    assert findings == []


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class TestCliCommandsDocumented:
    def test_flags_undocumented_command(self, tmp_path):
        _write(
            tmp_path / "src" / "codecompass" / "cli.py",
            "import typer\napp = typer.Typer()\n\n\n"
            "@app.command()\ndef frobnicate():\n    pass\n",
        )
        _write(tmp_path / "docs" / "cli-reference.md", "# CLI reference\n\nnothing here\n")

        findings = check_user_docs.check_cli_commands_documented(tmp_path)

        assert len(findings) == 1
        assert "frobnicate" in findings[0].message

    def test_no_finding_when_documented(self, tmp_path):
        _write(
            tmp_path / "src" / "codecompass" / "cli.py",
            "import typer\napp = typer.Typer()\n\n\n"
            "@app.command()\ndef frobnicate():\n    pass\n",
        )
        _write(
            tmp_path / "docs" / "cli-reference.md",
            "# CLI reference\n\n`codecompass frobnicate`\n",
        )

        findings = check_user_docs.check_cli_commands_documented(tmp_path)

        assert findings == []


class TestReadmePhaseCount:
    def test_flags_mismatch(self, tmp_path):
        _write(tmp_path / "README.md", "Status: phases 0-5 all `done`.\n")
        _write(
            tmp_path / "planning" / "ROADMAP.md",
            "| Phase | Name | Status |\n"
            "|---|---|---|\n"
            "| 0 | a | done |\n"
            "| 1 | b | done |\n"
            "| 2 | c | not started |\n",
        )

        findings = check_user_docs.check_readme_phase_count(tmp_path)

        assert len(findings) == 1
        assert "0-5" in findings[0].message
        assert " 1" in findings[0].message or "is 1" in findings[0].message

    def test_no_finding_when_consistent(self, tmp_path):
        _write(tmp_path / "README.md", "Status: phases 0-1 all `done`.\n")
        _write(
            tmp_path / "planning" / "ROADMAP.md",
            "| Phase | Name | Status |\n"
            "|---|---|---|\n"
            "| 0 | a | done |\n"
            "| 1 | b | done |\n",
        )

        findings = check_user_docs.check_readme_phase_count(tmp_path)

        assert findings == []

    def test_ignores_done_phases_in_redefined_v1_section(self, tmp_path):
        # `done` phases under the "Redefined CodeCompass v1" heading are a
        # separate milestone group (decisions/0048) and must not force the
        # README's foundation "phases 0-N" claim upward.
        _write(tmp_path / "README.md", "Status: phases 0-1 all `done`.\n")
        _write(
            tmp_path / "planning" / "ROADMAP.md",
            "| Phase | Name | Status |\n"
            "|---|---|---|\n"
            "| 0 | a | done |\n"
            "| 1 | b | done |\n"
            "\n## Redefined CodeCompass v1 — Stages A–F (phases 39–67)\n\n"
            "| Phase | Name | Status |\n"
            "|---|---|---|\n"
            "| 39 | ratify | done |\n"
            "| 40 | agents | done |\n",
        )

        findings = check_user_docs.check_readme_phase_count(tmp_path)

        assert findings == []


class TestApiKeyDocumented:
    def test_flags_missing_mention(self, tmp_path):
        _write(tmp_path / "README.md", "# codecompass\n\nno env vars mentioned here.\n")

        findings = check_user_docs.check_api_key_documented(tmp_path)

        assert len(findings) == 1

    def test_no_finding_when_mentioned(self, tmp_path):
        _write(tmp_path / "README.md", "Set `ANTHROPIC_API_KEY` to enable enrichment.\n")

        findings = check_user_docs.check_api_key_documented(tmp_path)

        assert findings == []


class TestVendorConfigFieldsDocumented:
    def test_flags_undocumented_field(self, tmp_path):
        _write(
            tmp_path / "src" / "codecompass" / "core.py",
            "from dataclasses import dataclass\n\n\n"
            "@dataclass(frozen=True)\nclass VendorConfig:\n"
            "    name: str\n    ecosystem: str\n",
        )
        _write(tmp_path / "docs" / "config-schema.md", "Fields: `name`\n")

        findings = check_user_docs.check_vendor_config_fields_documented(tmp_path)

        assert len(findings) == 1
        assert "ecosystem" in findings[0].message

    def test_no_finding_when_all_documented(self, tmp_path):
        _write(
            tmp_path / "src" / "codecompass" / "core.py",
            "from dataclasses import dataclass\n\n\n"
            "@dataclass(frozen=True)\nclass VendorConfig:\n"
            "    name: str\n    ecosystem: str\n",
        )
        _write(tmp_path / "docs" / "config-schema.md", "Fields: `name`, `ecosystem`\n")

        findings = check_user_docs.check_vendor_config_fields_documented(tmp_path)

        assert findings == []


class TestAiDocsPresent:
    def test_flags_missing_directory(self, tmp_path):
        findings = check_user_docs.check_ai_docs_present(tmp_path)

        assert len(findings) == 1

    def test_flags_empty_file(self, tmp_path):
        _write(tmp_path / "ai-docs" / "README.md", "content\n")
        (tmp_path / "ai-docs" / "CLAUDE.md").touch()

        findings = check_user_docs.check_ai_docs_present(tmp_path)

        assert len(findings) == 1
        assert "CLAUDE.md" in findings[0].message

    def test_no_finding_when_all_present_and_nonempty(self, tmp_path):
        _write(tmp_path / "ai-docs" / "README.md", "content\n")
        _write(tmp_path / "ai-docs" / "CLAUDE.md", "content\n")

        findings = check_user_docs.check_ai_docs_present(tmp_path)

        assert findings == []


_GOOD_CANDIDATE = (
    "### L-042 — a thing was noticed\n\n"
    "- **origin:** Phase 99\n"
    "- **date:** 2026-09-10\n"
    "- **project_revision:** abc1234\n"
    "- **observation:** X happened\n"
    "- **evidence:** foo.py:1\n"
    "- **classification:** uncertain\n"
    "- **status:** candidate\n"
)


class TestLearningsCandidateFields:
    def test_flags_missing_fields(self, tmp_path):
        _write(
            tmp_path / "planning" / "learnings" / "inbox.md",
            "### L-001 — incomplete\n\n- **observation:** something\n",
        )
        findings = check_user_docs.check_learnings_candidate_fields(tmp_path)
        assert len(findings) == 1
        assert "L-001" in findings[0].message
        assert "origin" in findings[0].message

    def test_no_finding_when_complete(self, tmp_path):
        _write(tmp_path / "planning" / "learnings" / "inbox.md", _GOOD_CANDIDATE)
        assert check_user_docs.check_learnings_candidate_fields(tmp_path) == []

    def test_reads_candidates_subdir(self, tmp_path):
        _write(tmp_path / "planning" / "learnings" / "inbox.md", "# inbox\n")
        _write(
            tmp_path / "planning" / "learnings" / "candidates" / "L-007.md",
            "### L-007 — bad\n\n- **status:** candidate\n",
        )
        findings = check_user_docs.check_learnings_candidate_fields(tmp_path)
        assert len(findings) == 1 and "L-007" in findings[0].message


class TestPromotedLearningsLogged:
    def test_flags_promoted_without_pointer(self, tmp_path):
        _write(
            tmp_path / "planning" / "learnings" / "inbox.md",
            _GOOD_CANDIDATE.replace("**status:** candidate", "**status:** promoted"),
        )
        _write(tmp_path / "planning" / "learnings" / "promoted.md", "# log\n")
        findings = check_user_docs.check_promoted_learnings_logged(tmp_path)
        assert len(findings) == 1 and "L-042" in findings[0].message

    def test_no_finding_when_logged(self, tmp_path):
        _write(
            tmp_path / "planning" / "learnings" / "inbox.md",
            _GOOD_CANDIDATE.replace("**status:** candidate", "**status:** promoted"),
        )
        _write(
            tmp_path / "planning" / "learnings" / "promoted.md",
            "# log\n\nL-042 | 2026-09-10 | uncertain | foo.py @ abc1234\n",
        )
        assert check_user_docs.check_promoted_learnings_logged(tmp_path) == []

    def test_candidate_status_not_flagged(self, tmp_path):
        _write(tmp_path / "planning" / "learnings" / "inbox.md", _GOOD_CANDIDATE)
        assert check_user_docs.check_promoted_learnings_logged(tmp_path) == []


class TestStaleEvidenceGathering:
    def test_informational_only(self, tmp_path):
        _write(
            tmp_path / "planning" / "learnings" / "inbox.md",
            _GOOD_CANDIDATE.replace(
                "**status:** candidate", "**status:** evidence-gathering"
            ),
        )
        findings = check_user_docs.check_stale_evidence_gathering(tmp_path)
        assert len(findings) == 1
        assert findings[0].strict is False


class TestPhaseRetrosPresent:
    def _roadmap(self, rows: str) -> str:
        return "| Phase | Name | Status |\n|---|---|---|\n" + rows

    def test_flags_done_phase_without_retro(self, tmp_path):
        _write(
            tmp_path / "planning" / "ROADMAP.md",
            self._roadmap("| 41 | x | done |\n| 42 | y | in progress |\n"),
        )
        findings = check_user_docs.check_phase_retros_present(tmp_path)
        assert len(findings) == 1 and "phase 41" in findings[0].message

    def test_no_finding_when_retro_present(self, tmp_path):
        _write(
            tmp_path / "planning" / "ROADMAP.md",
            self._roadmap("| 41 | x | done |\n"),
        )
        _write(tmp_path / "planning" / "retros" / "phase-41-x.md", "# retro\n")
        assert check_user_docs.check_phase_retros_present(tmp_path) == []

    def test_ignores_phases_before_41(self, tmp_path):
        _write(
            tmp_path / "planning" / "ROADMAP.md",
            self._roadmap("| 39 | x | done |\n| 40 | y | done |\n"),
        )
        assert check_user_docs.check_phase_retros_present(tmp_path) == []


_CLI_PY = (
    "import typer\n"
    "app = typer.Typer()\n"
    "query_app = typer.Typer()\n"
    'app.add_typer(query_app, name="query")\n'
    "@app.command()\n"
    "def sync():\n    pass\n"
    '@query_app.command("vendor")\n'
    "def query_vendor():\n    pass\n"
)


class TestInternalLinksResolve:
    def test_flags_missing_file(self, tmp_path):
        _write(tmp_path / "README.md", "See [x](./docs/gone.md).\n")
        findings = check_user_docs.check_internal_links_resolve(tmp_path)
        assert len(findings) == 1
        assert "gone.md" in findings[0].message and findings[0].strict

    def test_resolves_existing_and_skips_http(self, tmp_path):
        _write(tmp_path / "docs" / "a.md", "# A\n")
        _write(
            tmp_path / "README.md",
            "[a](docs/a.md) and [ext](https://example.com) and [self](#heading)\n\n# Heading\n",
        )
        assert check_user_docs.check_internal_links_resolve(tmp_path) == []

    def test_bad_anchor_is_informational(self, tmp_path):
        _write(tmp_path / "README.md", "[x](#no-such-heading)\n\n# Real Heading\n")
        findings = check_user_docs.check_internal_links_resolve(tmp_path)
        assert len(findings) == 1 and findings[0].strict is False

    def test_ignores_links_in_code_fences(self, tmp_path):
        _write(tmp_path / "README.md", "```\n[x](./nope.md)\n```\n")
        assert check_user_docs.check_internal_links_resolve(tmp_path) == []


class TestFencedCodecompassExamples:
    def _root(self, tmp_path, doc_body: str):
        _write(tmp_path / "src" / "codecompass" / "cli.py", _CLI_PY)
        _write(tmp_path / "README.md", doc_body)
        return tmp_path

    def test_flags_bad_subcommand(self, tmp_path):
        root = self._root(tmp_path, "```bash\ncodecompass frobnicate\n```\n")
        findings = check_user_docs.check_fenced_codecompass_examples(root)
        assert len(findings) == 1 and "frobnicate" in findings[0].message

    def test_flags_bad_query_subcommand(self, tmp_path):
        root = self._root(tmp_path, "```\ncodecompass query bogus\n```\n")
        findings = check_user_docs.check_fenced_codecompass_examples(root)
        assert len(findings) == 1 and "bogus" in findings[0].message

    def test_accepts_real_commands_flags_and_prompts(self, tmp_path):
        root = self._root(
            tmp_path,
            "```bash\n"
            "$ codecompass sync turndown\n"
            "codecompass --budget 0\n"
            "codecompass query vendor turndown  # a comment\n"
            "codecompass\n"
            "```\n",
        )
        assert check_user_docs.check_fenced_codecompass_examples(root) == []

    def test_ignores_prose_mentions(self, tmp_path):
        root = self._root(tmp_path, "Run `codecompass wibble` — not in a fence.\n")
        assert check_user_docs.check_fenced_codecompass_examples(root) == []


class TestAdrStatusAndSupersedes:
    def test_flags_missing_status(self, tmp_path):
        _write(tmp_path / "decisions" / "0001-x.md", "# 0001. X\n\nsome text\n")
        findings = check_user_docs.check_adr_status_and_supersedes(tmp_path)
        assert len(findings) == 1 and "Status" in findings[0].message

    def test_flags_dangling_reference(self, tmp_path):
        _write(
            tmp_path / "decisions" / "0002-y.md",
            "# 0002. Y\n\n## Status\n\nAccepted\n\nSupersedes decisions/0099.\n",
        )
        findings = check_user_docs.check_adr_status_and_supersedes(tmp_path)
        assert any("0099" in f.message for f in findings)

    def test_clean_adr_pair(self, tmp_path):
        _write(
            tmp_path / "decisions" / "0001-x.md",
            "# 0001. X\n\n## Status\n\nSuperseded by `0002`\n",
        )
        _write(
            tmp_path / "decisions" / "0002-y.md",
            "# 0002. Y\n\n## Status\n\nAccepted — supersedes decisions/0001\n",
        )
        assert check_user_docs.check_adr_status_and_supersedes(tmp_path) == []


class TestNoDeletedNamesAsLive:
    def test_flags_live_sounding_claim(self, tmp_path):
        _write(
            tmp_path / "docs" / "x.md",
            "The tool sets depth = full for every vendor by default.\n",
        )
        findings = check_user_docs.check_no_deleted_names_as_live(tmp_path)
        assert len(findings) == 1
        assert "depth = full" in findings[0].message

    def test_does_not_flag_historically_framed_mention(self, tmp_path):
        _write(
            tmp_path / "architecture" / "overview.md",
            "- **`grounded_description.py`'s cache** — this module was "
            "retired and deleted in Phase 16; `depth = full` no longer "
            "exists as a config value.\n",
        )
        assert check_user_docs.check_no_deleted_names_as_live(tmp_path) == []

    def test_marker_must_be_in_the_same_unit_not_just_the_file(self, tmp_path):
        _write(
            tmp_path / "docs" / "x.md",
            "`promote` was retired in Phase 15.\n"
            "\n"
            "Unrelated paragraph: run `codecompass promote` to regenerate "
            "a vendor's Skill.\n",
        )
        findings = check_user_docs.check_no_deleted_names_as_live(tmp_path)
        assert len(findings) == 1
        assert "codecompass promote" in findings[0].message

    def test_ignores_fenced_code_examples(self, tmp_path):
        _write(
            tmp_path / "docs" / "x.md",
            "```\ncodecompass promote anthropic\n```\n",
        )
        assert check_user_docs.check_no_deleted_names_as_live(tmp_path) == []

    def test_clean_against_real_repo(self):
        assert check_user_docs.check_no_deleted_names_as_live(REPO_ROOT) == []


class TestGeneratedArtifactsMatchSource:
    def test_flags_hand_edited_tool_skill(self, tmp_path, monkeypatch):
        import shutil

        shutil.copytree(REPO_ROOT / ".claude", tmp_path / ".claude")
        shutil.copy(REPO_ROOT / "vendor.toml", tmp_path / "vendor.toml")
        skill_path = tmp_path / ".claude" / "skills" / "codecompass" / "SKILL.md"
        skill_path.write_text(
            skill_path.read_text(encoding="utf-8") + "\nHAND EDITED\n", encoding="utf-8"
        )

        findings = check_user_docs.check_generated_artifacts_match_source(tmp_path)

        assert any("SKILL.md" in f.message for f in findings)

    def test_flags_hand_edited_discovery_command(self, tmp_path):
        import shutil

        shutil.copytree(REPO_ROOT / ".claude", tmp_path / ".claude")
        shutil.copy(REPO_ROOT / "vendor.toml", tmp_path / "vendor.toml")
        discovery_path = tmp_path / ".claude" / "commands" / "discovery.md"
        discovery_path.write_text(
            discovery_path.read_text(encoding="utf-8") + "\nHAND EDITED\n", encoding="utf-8"
        )

        findings = check_user_docs.check_generated_artifacts_match_source(tmp_path)

        assert any("discovery.md" in f.message for f in findings)

    def test_clean_against_real_repo(self):
        assert check_user_docs.check_generated_artifacts_match_source(REPO_ROOT) == []

    def test_missing_artifacts_produce_no_finding(self, tmp_path):
        # Neither generated artifact exists in this fixture — nothing to compare.
        assert check_user_docs.check_generated_artifacts_match_source(tmp_path) == []


class TestMainStrictExitCode:
    def _broken_root(self, tmp_path):
        """A minimal fixture repo where every rule passes except the
        ANTHROPIC_API_KEY mention — isolates --strict's exit-code behavior
        from the other four rules, which need their own real source files."""
        _write(tmp_path / "README.md", "Status: phases 0-0 all `done`. No env vars here.\n")
        _write(
            tmp_path / "planning" / "ROADMAP.md",
            "| Phase | Name | Status |\n|---|---|---|\n| 0 | a | done |\n",
        )
        _write(tmp_path / "src" / "codecompass" / "cli.py", "import typer\napp = typer.Typer()\n")
        _write(tmp_path / "docs" / "cli-reference.md", "# CLI reference\n")
        _write(
            tmp_path / "src" / "codecompass" / "core.py",
            "from dataclasses import dataclass\n\n\n"
            "@dataclass(frozen=True)\nclass VendorConfig:\n    pass\n",
        )
        _write(tmp_path / "docs" / "config-schema.md", "# config schema\n")
        _write(tmp_path / "ai-docs" / "README.md", "content\n")
        return tmp_path

    def test_strict_exits_nonzero_on_findings(self, tmp_path, monkeypatch):
        monkeypatch.setattr(check_user_docs, "ROOT", self._broken_root(tmp_path))
        monkeypatch.setattr(sys, "argv", ["check_user_docs.py", "--strict"])

        assert check_user_docs.main() == 1

    def test_bare_exits_zero_even_with_findings(self, tmp_path, monkeypatch):
        monkeypatch.setattr(check_user_docs, "ROOT", self._broken_root(tmp_path))
        monkeypatch.setattr(sys, "argv", ["check_user_docs.py"])

        assert check_user_docs.main() == 0

    def test_info_finding_does_not_fail_strict(self, tmp_path, monkeypatch):
        root = self._broken_root(tmp_path)
        _write(root / "README.md", "Status: phases 0-0 all `done`. ANTHROPIC_API_KEY.\n")
        _write(
            root / "planning" / "learnings" / "inbox.md",
            _GOOD_CANDIDATE.replace(
                "**status:** candidate", "**status:** evidence-gathering"
            ),
        )
        monkeypatch.setattr(check_user_docs, "ROOT", root)
        monkeypatch.setattr(sys, "argv", ["check_user_docs.py", "--strict"])

        # the only finding is the informational stale-evidence one
        assert check_user_docs.main() == 0


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
