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
    """Blocking findings only — an informational one (e.g. the
    generated_artifacts_match_source SKILL.md comparison skipping itself
    on a checkout with no context-graph.db, L-011) is expected and fine;
    it never fails `--strict` either (see Finding.strict)."""
    findings = check_user_docs.run_all(REPO_ROOT)
    assert [f for f in findings if f.strict] == []


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
        _write(tmp_path / "docs" / "reference" / "cli.md", "# CLI reference\n\nnothing here\n")

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
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass frobnicate`\n\n```\ncodecompass frobnicate\n```\n",
        )

        findings = check_user_docs.check_cli_commands_documented(tmp_path)

        assert findings == []

    def test_flags_removed_command_still_documented(self, tmp_path):
        """A command removed from cli.py but still documented -- the
        other direction of the presence check."""
        _write(
            tmp_path / "src" / "codecompass" / "cli.py",
            "import typer\napp = typer.Typer()\n\n\n"
            "@app.command()\ndef frobnicate():\n    pass\n",
        )
        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass frobnicate|retired`\n\n"
            "```\ncodecompass frobnicate\ncodecompass retired\n```\n",
        )

        findings = check_user_docs.check_cli_commands_documented(tmp_path)

        assert len(findings) == 1
        assert "retired" in findings[0].message
        assert "no longer a real command" in findings[0].message

    def test_covers_every_sub_app_not_only_app_and_query_app(self, tmp_path):
        """The real, pre-existing gap this amendment fixes: knowledge_app/
        docs_app/enrich_app were never walked at all (only `app`/
        `query_app` were)."""
        _write(
            tmp_path / "src" / "codecompass" / "cli.py",
            "import typer\n"
            "app = typer.Typer()\n"
            "knowledge_app = typer.Typer()\n"
            "docs_app = typer.Typer()\n"
            "enrich_app = typer.Typer()\n"
            "app.add_typer(knowledge_app, name='knowledge')\n"
            "app.add_typer(docs_app, name='docs')\n"
            "app.add_typer(enrich_app, name='enrich')\n\n\n"
            "@knowledge_app.command('trace')\ndef knowledge_trace():\n    pass\n\n\n"
            "@docs_app.command('maintain')\ndef docs_maintain():\n    pass\n\n\n"
            "@enrich_app.command('apply')\ndef enrich_apply():\n    pass\n",
        )
        _write(tmp_path / "docs" / "reference" / "cli.md", "# CLI reference\n\nnothing here\n")

        findings = check_user_docs.check_cli_commands_documented(tmp_path)

        messages = {f.message for f in findings}
        assert any("knowledge trace" in m for m in messages)
        assert any("docs maintain" in m for m in messages)
        assert any("enrich apply" in m for m in messages)
        assert len(findings) == 3


def _knowledge_cli_py(trace_relation_default: str = "supporting_evidence") -> str:
    """One `knowledge_app` command, `trace`, with a required argument, an
    optional string flag with a concrete default, a boolean flag, and a
    repeatable-list flag -- enough surface to exercise every branch of the
    four-point default policy in one real-shaped command."""
    return (
        "import typer\n"
        "app = typer.Typer()\n"
        "knowledge_app = typer.Typer()\n"
        "app.add_typer(knowledge_app, name='knowledge')\n\n\n"
        "@knowledge_app.command('trace')\n"
        "def knowledge_trace(\n"
        "    record_id: str = typer.Argument(...),\n"
        f"    relation: str = typer.Option({trace_relation_default!r}, '--relation'),\n"
        "    verbose: bool = typer.Option(False, '--verbose'),\n"
        "    kind: list[str] = typer.Option([], '--kind'),\n"
        "):\n"
        "    pass\n"
    )


class TestCliParameterDefaultsDocumented:
    def test_flags_omitted_default(self, tmp_path):
        """A non-exempt optional parameter's default disclosed nowhere at
        all -- the real failure mode all five known gaps are."""
        _write(tmp_path / "src" / "codecompass" / "cli.py", _knowledge_cli_py())
        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass knowledge trace`\n\n"
            "```\ncodecompass knowledge trace RECORD_ID [--relation RELATION] "
            "[--verbose] [--kind KIND ...]\n```\n",
        )

        findings = check_user_docs.check_cli_parameter_defaults_documented(tmp_path)

        assert len(findings) == 1
        assert "--relation" in findings[0].message
        assert "supporting_evidence" in findings[0].message

    def test_flags_wrong_documented_default(self, tmp_path):
        """A documented default that disagrees with the live value."""
        _write(tmp_path / "src" / "codecompass" / "cli.py", _knowledge_cli_py())
        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass knowledge trace`\n\n"
            "```\ncodecompass knowledge trace RECORD_ID [--relation RELATION] "
            "[--verbose] [--kind KIND ...]\n```\n\n"
            "- **`trace RECORD_ID`** — `--relation`, default `wrong_value`.\n",
        )

        findings = check_user_docs.check_cli_parameter_defaults_documented(tmp_path)

        assert len(findings) == 1
        assert "--relation" in findings[0].message

    def test_passes_synopsis_embedded_literal(self, tmp_path):
        """The real `init --output vendor.toml` convention: the default
        embedded directly in the synopsis line's own bracket."""
        _write(tmp_path / "src" / "codecompass" / "cli.py", _knowledge_cli_py())
        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass knowledge trace`\n\n"
            "```\ncodecompass knowledge trace RECORD_ID "
            "[--relation supporting_evidence] [--verbose] [--kind KIND ...]\n```\n",
        )

        findings = check_user_docs.check_cli_parameter_defaults_documented(tmp_path)

        assert findings == []

    def test_passes_prose_default_statement(self, tmp_path):
        """The real `schema-init --section-id` convention: "default
        `value`" in prose."""
        _write(tmp_path / "src" / "codecompass" / "cli.py", _knowledge_cli_py())
        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass knowledge trace`\n\n"
            "```\ncodecompass knowledge trace RECORD_ID [--relation RELATION] "
            "[--verbose] [--kind KIND ...]\n```\n\n"
            "- **`trace RECORD_ID`** — `--relation`, default `supporting_evidence`.\n",
        )

        findings = check_user_docs.check_cli_parameter_defaults_documented(tmp_path)

        assert findings == []

    def test_substring_collision_is_not_mistaken_for_disclosure(self, tmp_path):
        """Real false negatives this amendment fixed: a default value that
        is a substring of unrelated text (an enum-choices list naming the
        same string as one of several *choices*; the synopsis line's own
        leading `codecompass <path>` tokens) must not be read as
        disclosure."""
        _write(tmp_path / "src" / "codecompass" / "cli.py", _knowledge_cli_py())
        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass knowledge trace`\n\n"
            "```\ncodecompass knowledge trace RECORD_ID [--relation RELATION] "
            "[--verbose] [--kind KIND ...]\n```\n\n"
            "- **`trace RECORD_ID`** — `--relation` is one of `depends_on`/"
            "`supporting_evidence`/`contradicting_evidence` (not a default statement).\n",
        )

        findings = check_user_docs.check_cli_parameter_defaults_documented(tmp_path)

        assert len(findings) == 1
        assert "--relation" in findings[0].message

    def test_bool_and_list_params_never_require_disclosure(self, tmp_path):
        _write(tmp_path / "src" / "codecompass" / "cli.py", _knowledge_cli_py())
        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass knowledge trace`\n\n"
            "```\ncodecompass knowledge trace RECORD_ID [--relation supporting_evidence] "
            "[--verbose] [--kind KIND ...]\n```\n",
        )

        findings = check_user_docs.check_cli_parameter_defaults_documented(tmp_path)

        assert findings == []  # --verbose/--kind flagged nowhere despite no stated default

    def test_minimal_content_cannot_pass_by_heading_and_fence_alone(self, tmp_path):
        """A command with a real heading and a real fenced synopsis, but
        no prose and no stated default anywhere -- must still fail; the
        checker cannot be satisfied merely because the command's own
        heading/fence exists."""
        cli_py = (
            "import typer\n"
            "app = typer.Typer()\n"
            "docs_app = typer.Typer()\n"
            "app.add_typer(docs_app, name='docs')\n\n\n"
            "@docs_app.command('schema-init')\n"
            "def docs_schema_init(\n"
            "    document: str = typer.Argument(...),\n"
            "    section_id: str = typer.Option('section-one', '--section-id'),\n"
            "):\n"
            "    pass\n"
        )
        _write(tmp_path / "src" / "codecompass" / "cli.py", cli_py)
        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass docs schema-init`\n\n"
            "```\ncodecompass docs schema-init DOCUMENT [--section-id ID]\n```\n",
        )

        findings = check_user_docs.check_cli_parameter_defaults_documented(tmp_path)
        assert len(findings) == 1
        assert "--section-id" in findings[0].message

        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass docs schema-init`\n\n"
            "```\ncodecompass docs schema-init DOCUMENT [--section-id ID]\n```\n\n"
            "- **`schema-init DOCUMENT`** — `--section-id`, default `section-one`.\n",
        )
        findings = check_user_docs.check_cli_parameter_defaults_documented(tmp_path)
        assert findings == []  # isolates exactly what changed


def _shared_block_cli_py() -> str:
    """Two commands sharing one heading/fenced block, mirroring the real
    `knowledge`/`docs` convention -- `first` has a real default; `second`
    has a backslash-continued, multi-line synopsis matching `docs
    record-review`'s own real shape."""
    return (
        "import typer\n"
        "app = typer.Typer()\n"
        "grp_app = typer.Typer()\n"
        "app.add_typer(grp_app, name='grp')\n\n\n"
        "@grp_app.command('first')\n"
        "def grp_first(\n"
        "    value: str = typer.Option('alpha', '--value'),\n"
        "):\n"
        "    pass\n\n\n"
        "@grp_app.command('second')\n"
        "def grp_second(\n"
        "    record_id: str = typer.Argument(...),\n"
        "    kind: str = typer.Option(..., '--kind'),\n"
        "    other: str = typer.Option('beta', '--other'),\n"
        "):\n"
        "    pass\n"
    )


class TestCommandIsolation:
    """Where multiple commands share one heading/fenced block, a default
    documented for one command must not satisfy a different, neighbouring
    command's own disclosure requirement -- the specific attribution bug
    this amendment's own test design targets, in both the synopsis-line
    and the prose form."""

    def test_correct_attribution_passes(self, tmp_path):
        _write(tmp_path / "src" / "codecompass" / "cli.py", _shared_block_cli_py())
        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass grp first|second`\n\n"
            "```\ncodecompass grp first [--value alpha]\n"
            "codecompass grp second RECORD_ID --kind KIND \\\n"
            "    [--other beta]\n```\n",
        )
        findings = check_user_docs.check_cli_parameter_defaults_documented(tmp_path)
        assert findings == []

    def test_omitted_default_on_one_command_fails(self, tmp_path):
        _write(tmp_path / "src" / "codecompass" / "cli.py", _shared_block_cli_py())
        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass grp first|second`\n\n"
            "```\ncodecompass grp first [--value VALUE]\n"
            "codecompass grp second RECORD_ID --kind KIND \\\n"
            "    [--other beta]\n```\n",
        )
        findings = check_user_docs.check_cli_parameter_defaults_documented(tmp_path)
        assert len(findings) == 1
        assert "--value" in findings[0].message

    def test_wrong_default_on_one_command_fails(self, tmp_path):
        _write(tmp_path / "src" / "codecompass" / "cli.py", _shared_block_cli_py())
        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass grp first|second`\n\n"
            "```\ncodecompass grp first [--value wrong]\n"
            "codecompass grp second RECORD_ID --kind KIND \\\n"
            "    [--other beta]\n```\n",
        )
        findings = check_user_docs.check_cli_parameter_defaults_documented(tmp_path)
        assert len(findings) == 1
        assert "--value" in findings[0].message

    def test_correct_value_under_neighbouring_synopsis_line_fails(self, tmp_path):
        """The core attribution bug: `first`'s own correct default
        ("alpha") sits only in `second`'s own synopsis line, not its
        own."""
        _write(tmp_path / "src" / "codecompass" / "cli.py", _shared_block_cli_py())
        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass grp first|second`\n\n"
            "```\ncodecompass grp first [--value VALUE]\n"
            "codecompass grp second RECORD_ID --kind KIND \\\n"
            "    [--other beta] alpha\n```\n",
        )
        findings = check_user_docs.check_cli_parameter_defaults_documented(tmp_path)
        assert len(findings) == 1
        assert "--value" in findings[0].message

    def test_correct_value_under_neighbouring_prose_bullet_fails(self, tmp_path):
        """The same attribution bug in the *prose* disclosure form: a
        naive 'is this value anywhere in the heading's own prose'
        implementation would wrongly pass this."""
        _write(tmp_path / "src" / "codecompass" / "cli.py", _shared_block_cli_py())
        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass grp first|second`\n\n"
            "```\ncodecompass grp first [--value VALUE]\n"
            "codecompass grp second RECORD_ID --kind KIND \\\n"
            "    [--other beta]\n```\n\n"
            "- **`first`** — an ordinary command.\n"
            "- **`second RECORD_ID`** — `--value`, default `alpha` "
            "(this belongs to `first`, not `second` — misplaced on purpose).\n",
        )
        findings = check_user_docs.check_cli_parameter_defaults_documented(tmp_path)
        assert len(findings) == 1
        assert "--value" in findings[0].message

    def test_shared_block_and_continuation_parse_correctly_when_fully_correct(self, tmp_path):
        _write(tmp_path / "src" / "codecompass" / "cli.py", _shared_block_cli_py())
        _write(
            tmp_path / "docs" / "reference" / "cli.md",
            "## `codecompass grp first|second`\n\n"
            "```\ncodecompass grp first [--value alpha]\n"
            "codecompass grp second RECORD_ID --kind KIND \\\n"
            "    [--other beta]\n```\n\n"
            "- **`first`** — `--value`, default `alpha`.\n"
            "- **`second RECORD_ID`** — `--other`, default `beta`.\n",
        )
        findings = check_user_docs.check_cli_parameter_defaults_documented(tmp_path)
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
        _write(tmp_path / "docs" / "reference" / "configuration.md", "Fields: `name`\n")

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
        _write(
            tmp_path / "docs" / "reference" / "configuration.md", "Fields: `name`, `ecosystem`\n"
        )

        findings = check_user_docs.check_vendor_config_fields_documented(tmp_path)

        assert findings == []

    def test_flags_undocumented_ecosystem_member(self, tmp_path):
        _write(
            tmp_path / "src" / "codecompass" / "core.py",
            "from enum import StrEnum\n\n\n"
            "class Ecosystem(StrEnum):\n"
            "    NPM = 'npm'\n    PYTHON = 'python'\n",
        )
        _write(tmp_path / "docs" / "reference" / "configuration.md", "One of `npm`.\n")

        findings = check_user_docs.check_vendor_config_fields_documented(tmp_path)

        assert len(findings) == 1
        assert "python" in findings[0].message

    def test_no_finding_when_every_ecosystem_member_documented(self, tmp_path):
        _write(
            tmp_path / "src" / "codecompass" / "core.py",
            "from enum import StrEnum\n\n\n"
            "class Ecosystem(StrEnum):\n"
            "    NPM = 'npm'\n    PYTHON = 'python'\n",
        )
        _write(
            tmp_path / "docs" / "reference" / "configuration.md", "One of `npm`, `python`.\n"
        )

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

_GOOD_OBSERVATION = (
    "### OBS-042 — an edge was retrieved and it went fine\n\n"
    "- **origin:** Phase 99\n"
    "- **date:** 2026-09-10\n"
    "- **codecompass_revision:** abc1234\n"
    "- **project:** codecompass (own dev)\n"
    "- **edge identity:** `foo.py -- uses --> bar`\n"
    "- **observation type:** EDGE_USEFUL\n"
    "- **edge correctness:** correct\n"
    "- **task usefulness:** useful\n"
    "- **status:** recorded\n"
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


class TestLearningsStatusMatchesRetainOutcome:
    def test_flags_retain_outcome_with_stale_candidate_status(self, tmp_path):
        _write(
            tmp_path / "planning" / "learnings" / "inbox.md",
            _GOOD_CANDIDATE
            + "- **curation:** provenance accepted. **Outcome: retain**, not "
            "promote.\n",
        )
        findings = check_user_docs.check_learnings_status_matches_retain_outcome(
            tmp_path
        )
        assert len(findings) == 1 and "L-042" in findings[0].message

    def test_no_finding_when_status_already_retained(self, tmp_path):
        _write(
            tmp_path / "planning" / "learnings" / "inbox.md",
            _GOOD_CANDIDATE.replace("**status:** candidate", "**status:** retained")
            + "- **curation:** provenance accepted. **Outcome: retain**, not "
            "promote.\n",
        )
        assert (
            check_user_docs.check_learnings_status_matches_retain_outcome(tmp_path)
            == []
        )


class TestContextObservationFields:
    def test_flags_missing_fields(self, tmp_path):
        _write(
            tmp_path / "planning" / "context-observations" / "inbox.md",
            "### OBS-001 — incomplete\n\n- **origin:** Phase 1\n",
        )
        findings = check_user_docs.check_context_observation_fields(tmp_path)
        assert len(findings) == 1
        assert "OBS-001" in findings[0].message
        assert "edge correctness" in findings[0].message

    def test_no_finding_when_complete(self, tmp_path):
        _write(
            tmp_path / "planning" / "context-observations" / "inbox.md",
            _GOOD_OBSERVATION,
        )
        assert check_user_docs.check_context_observation_fields(tmp_path) == []

    def test_no_finding_when_file_absent(self, tmp_path):
        assert check_user_docs.check_context_observation_fields(tmp_path) == []

    def test_flags_correctness_usefulness_split_specifically(self, tmp_path):
        # The whole point of Phase 52's format: collapsing "was it true"
        # and "did it help" into one field must still be caught.
        missing_split = _GOOD_OBSERVATION.replace(
            "- **edge correctness:** correct\n- **task usefulness:** useful\n",
            "",
        )
        _write(
            tmp_path / "planning" / "context-observations" / "inbox.md",
            missing_split,
        )
        findings = check_user_docs.check_context_observation_fields(tmp_path)
        assert len(findings) == 1
        assert "edge correctness" in findings[0].message
        assert "task usefulness" in findings[0].message


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


class TestDonePhasesHaveAuditReport:
    def _roadmap(self, rows: str) -> str:
        return "| Phase | Name | Status |\n|---|---|---|\n" + rows

    def test_flags_done_phase_without_audit_report_or_trivial_marker(self, tmp_path):
        _write(
            tmp_path / "planning" / "ROADMAP.md",
            self._roadmap("| 76 | x | done |\n"),
        )
        _write(tmp_path / "planning" / "retros" / "phase-76-x.md", "# retro\nshipped\n")
        findings = check_user_docs.check_done_phases_have_audit_report(tmp_path)
        assert len(findings) == 1 and "phase 76" in findings[0].message

    def test_no_finding_when_audit_report_present(self, tmp_path):
        _write(
            tmp_path / "planning" / "ROADMAP.md",
            self._roadmap("| 76 | x | done |\n"),
        )
        _write(tmp_path / "planning" / "retros" / "_audit-phase-76.md", "verdict: PASS\n")
        assert check_user_docs.check_done_phases_have_audit_report(tmp_path) == []

    def test_no_finding_when_retro_documents_trivial_carve_out(self, tmp_path):
        _write(
            tmp_path / "planning" / "ROADMAP.md",
            self._roadmap("| 76 | x | done |\n"),
        )
        _write(
            tmp_path / "planning" / "retros" / "phase-76-x.md",
            "# retro\nTrivial phase -- lead confirmation stands in.\n",
        )
        assert check_user_docs.check_done_phases_have_audit_report(tmp_path) == []

    def test_ignores_phases_before_41(self, tmp_path):
        _write(
            tmp_path / "planning" / "ROADMAP.md",
            self._roadmap("| 39 | x | done |\n"),
        )
        assert check_user_docs.check_done_phases_have_audit_report(tmp_path) == []

    def test_ignores_non_done_phases(self, tmp_path):
        _write(
            tmp_path / "planning" / "ROADMAP.md",
            self._roadmap("| 76 | x | in progress |\n"),
        )
        assert check_user_docs.check_done_phases_have_audit_report(tmp_path) == []


class TestContextNotStaleAboutPendingAudit:
    def test_flags_pending_release_phase_auditor_language(self, tmp_path):
        _write(
            tmp_path / "planning" / "CONTEXT.md",
            "Pending: Phase 76's release-phase-auditor DoD pass, then push.\n",
        )
        findings = check_user_docs.check_context_not_stale_about_pending_audit(tmp_path)
        assert len(findings) == 1

    def test_no_finding_when_context_is_clean(self, tmp_path):
        _write(
            tmp_path / "planning" / "CONTEXT.md",
            "Phase 76 is closed. No phase is currently planned.\n",
        )
        assert check_user_docs.check_context_not_stale_about_pending_audit(tmp_path) == []


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

    def test_accepts_bracketed_usage_synopsis(self, tmp_path):
        """Regression test for a real finding from Phase 81B Amendment 4's
        documentation disposition: a usage-synopsis line like
        `codecompass [--yes] [--budget USD]` (square-bracket-optional-arg
        convention) was wrongly flagged as an attempt to invoke a
        subcommand literally named '[--yes]', since that token doesn't
        start with '-' the way a bare flag would."""
        root = self._root(tmp_path, "```\ncodecompass [--yes] [--budget USD]\n```\n")
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
        """Blocking findings only — see test_no_false_positives_against_real_repo."""
        findings = check_user_docs.check_generated_artifacts_match_source(REPO_ROOT)
        assert [f for f in findings if f.strict] == []

    def test_missing_artifacts_produce_no_finding(self, tmp_path):
        # Neither generated artifact exists in this fixture — nothing to compare.
        assert check_user_docs.check_generated_artifacts_match_source(tmp_path) == []

    def test_skill_comparison_skipped_without_graph_db(self, tmp_path):
        """A SKILL.md committed from a machine that had already run
        `codecompass sync` says e.g. "3 enriched"; a fresh checkout with no
        context-graph.db can only render "0 enriched" and would otherwise
        false-positive as drift (candidate learning L-011). No live sync
        happened here — the comparison should be skipped, not fail."""
        import shutil

        shutil.copytree(REPO_ROOT / ".claude", tmp_path / ".claude")
        shutil.copy(REPO_ROOT / "vendor.toml", tmp_path / "vendor.toml")
        assert not (tmp_path / "context-graph.db").exists()

        findings = check_user_docs.check_generated_artifacts_match_source(tmp_path)

        assert not any(f.strict for f in findings)
        assert any("context-graph.db" in f.message for f in findings)
        assert not any("does not match" in f.message for f in findings)


class TestMainStrictExitCode:
    def _broken_root(self, tmp_path):
        """A minimal fixture repo where every rule passes except the
        ANTHROPIC_API_KEY mention — isolates --strict's exit-code behavior
        from the other four rules, which need their own real source files."""
        _write(tmp_path / "README.md", "Status: phases 0-0 all `done`. No env vars here.\n")
        _write(
            tmp_path / "planning" / "ROADMAP.md",
            "In brief: the foundation (phases 0-0) is the tool.\n",
        )
        _write(tmp_path / "src" / "codecompass" / "cli.py", "import typer\napp = typer.Typer()\n")
        _write(tmp_path / "docs" / "reference" / "cli.md", "# CLI reference\n")
        _write(
            tmp_path / "src" / "codecompass" / "core.py",
            "from dataclasses import dataclass\n\n\n"
            "@dataclass(frozen=True)\nclass VendorConfig:\n    pass\n",
        )
        _write(tmp_path / "docs" / "reference" / "configuration.md", "# config schema\n")
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
