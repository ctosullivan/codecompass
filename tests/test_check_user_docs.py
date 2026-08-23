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


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
