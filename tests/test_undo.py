from pathlib import Path

import pytest
from typer.testing import CliRunner

from codecompass import graph
from codecompass.cli import app

runner = CliRunner()


def _write(path: Path, text: str = "content\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _skill_frontmatter(name: str) -> str:
    return f"---\nname: {name}\ndescription: test\n---\n\nBody.\n"


def _build_full_project(tmp_path: Path) -> None:
    """A project with generated codecompass output for one vendor plus a
    hand-written CLAUDE.md and a genuine third-party Skill — the fixture
    every graph-backed test starts from.
    """
    _write(tmp_path / "vendor.toml", '[[vendor]]\nname = "demo"\necosystem = "python"\n')
    _write(tmp_path / "vendor" / "demo" / "CLAUDE.md", "# demo\n")
    _write(tmp_path / "vendor" / "demo" / "OVERVIEW.md", "demo overview\n")

    _write(
        tmp_path / ".claude" / "skills" / "codecompass" / "SKILL.md",
        _skill_frontmatter("codecompass"),
    )
    _write(
        tmp_path / ".claude" / "skills" / "codecompass-demo" / "SKILL.md",
        _skill_frontmatter("codecompass-demo"),
    )
    _write(
        tmp_path / ".claude" / "skills" / "codecompass-demo" / "references" / "FILETREE.md",
        "tree\n",
    )
    _write(
        tmp_path / ".cursor" / "rules" / "codecompass-demo.mdc",
        "---\ndescription: test\nalwaysApply: false\n---\n\nBody.\n",
    )
    _write(tmp_path / ".claude" / "commands" / "discovery.md", "discovery body\n")

    _write(
        tmp_path / ".claude" / "skills" / "third-party" / "SKILL.md",
        _skill_frontmatter("third-party"),
    )

    _write(
        tmp_path / "CLAUDE.md",
        "# My Project\n\nHand-written notes.\n\n"
        "<!-- codecompass:start -->\n| table |\n<!-- codecompass:end -->\n",
    )

    conn = graph.open_graph(tmp_path)
    graph.rebuild_deterministic(
        conn,
        vendors=[graph.VendorRow(name="demo", ecosystem="python", installed_version="1.0.0")],
        source_files=[],
        symbols=[],
        uses_edges=[],
        doc_artifacts=[
            graph.DocArtifactRow(
                path="vendor/demo/CLAUDE.md",
                kind="claude_md",
                origin="codecompass_vendor",
                vendor_name="demo",
            ),
            graph.DocArtifactRow(
                path="vendor/demo/OVERVIEW.md",
                kind="overview",
                origin="codecompass_vendor",
                vendor_name="demo",
            ),
            graph.DocArtifactRow(
                path=".claude/skills/codecompass/SKILL.md",
                kind="skill",
                origin="codecompass_tool",
                name="codecompass",
            ),
            graph.DocArtifactRow(
                path=".claude/skills/codecompass-demo/SKILL.md",
                kind="skill",
                origin="codecompass_vendor",
                vendor_name="demo",
                name="codecompass-demo",
            ),
            graph.DocArtifactRow(
                path=".cursor/rules/codecompass-demo.mdc",
                kind="cursor_mdc",
                origin="codecompass_vendor",
                vendor_name="demo",
                name="codecompass-demo",
            ),
            graph.DocArtifactRow(
                path=".claude/commands/discovery.md",
                kind="slash_command",
                origin="codecompass_tool",
                name="discovery",
            ),
            graph.DocArtifactRow(
                path=".claude/skills/third-party/SKILL.md",
                kind="skill",
                origin="third_party",
                name="third-party",
            ),
        ],
        documents_edges=[],
        skill_mentions_edges=[],
        routes_via_edges=[],
        depends_on_edges=[],
        doc_relations_edges=[],
    )
    conn.close()


# --- graph-backed enumeration --------------------------------------------


def test_undo_dry_run_graph_backed_lists_generated_paths_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _build_full_project(tmp_path)

    result = runner.invoke(app, ["undo", "--dry-run"])

    assert result.exit_code == 0, result.output
    assert "vendor/demo" in result.output
    assert "vendor.toml" in result.output
    assert "context-graph.db" in result.output
    assert ".claude/skills/codecompass" in result.output
    assert ".cursor/rules/codecompass-demo.mdc" in result.output
    assert ".claude/commands/discovery.md" in result.output
    assert "CLAUDE.md" in result.output
    # Never enumerates the third-party skill.
    assert "third-party" not in result.output


def test_undo_dry_run_performs_zero_filesystem_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _build_full_project(tmp_path)

    result = runner.invoke(app, ["undo", "--dry-run"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "vendor" / "demo" / "CLAUDE.md").exists()
    assert (tmp_path / "vendor.toml").exists()
    assert (tmp_path / "context-graph.db").exists()
    assert (tmp_path / ".claude" / "skills" / "codecompass" / "SKILL.md").exists()
    assert (tmp_path / ".claude" / "skills" / "codecompass-demo" / "SKILL.md").exists()
    assert (tmp_path / ".cursor" / "rules" / "codecompass-demo.mdc").exists()
    assert (tmp_path / ".claude" / "commands" / "discovery.md").exists()
    assert (tmp_path / ".claude" / "skills" / "third-party" / "SKILL.md").exists()
    root_claude_md = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "<!-- codecompass:start -->" in root_claude_md


def test_undo_yes_deletes_generated_paths_and_preserves_third_party(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _build_full_project(tmp_path)

    result = runner.invoke(app, ["undo", "--yes"])

    assert result.exit_code == 0, result.output
    assert not (tmp_path / "vendor" / "demo").exists()
    assert not (tmp_path / "vendor.toml").exists()
    assert not (tmp_path / "context-graph.db").exists()
    assert not (tmp_path / ".claude" / "skills" / "codecompass").exists()
    assert not (tmp_path / ".claude" / "skills" / "codecompass-demo").exists()
    assert not (tmp_path / ".cursor" / "rules" / "codecompass-demo.mdc").exists()
    assert not (tmp_path / ".claude" / "commands" / "discovery.md").exists()
    # Third-party Skill survives untouched.
    assert (tmp_path / ".claude" / "skills" / "third-party" / "SKILL.md").exists()


def test_undo_yes_strips_marker_block_but_keeps_hand_written_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _build_full_project(tmp_path)

    result = runner.invoke(app, ["undo", "--yes"])

    assert result.exit_code == 0, result.output
    root_claude_md = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "<!-- codecompass:start -->" not in root_claude_md
    assert "<!-- codecompass:end -->" not in root_claude_md
    assert "| table |" not in root_claude_md
    assert "Hand-written notes." in root_claude_md
    assert "# My Project" in root_claude_md


def test_undo_vendor_skill_references_subdir_removed_not_just_skill_md(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A per-vendor Skill's `doc_artifacts` row points at its `SKILL.md`
    file, but the whole Skill directory (including `references/`) must be
    removed, or the copied reference files would be orphaned.
    """
    monkeypatch.chdir(tmp_path)
    _build_full_project(tmp_path)

    result = runner.invoke(app, ["undo", "--yes"])

    assert result.exit_code == 0, result.output
    assert not (
        tmp_path / ".claude" / "skills" / "codecompass-demo" / "references" / "FILETREE.md"
    ).exists()


def test_undo_without_confirmation_prompts_and_declining_skips(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _build_full_project(tmp_path)

    result = runner.invoke(app, ["undo"], input="n\n")

    assert result.exit_code == 0, result.output
    assert "skipped" in result.output.lower()
    assert (tmp_path / "vendor.toml").exists()
    assert (tmp_path / "vendor" / "demo").exists()


def test_undo_confirmed_via_prompt_deletes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _build_full_project(tmp_path)

    result = runner.invoke(app, ["undo"], input="y\n")

    assert result.exit_code == 0, result.output
    assert not (tmp_path / "vendor.toml").exists()


# --- fallback (no-graph) enumeration --------------------------------------


def test_undo_fallback_lists_pattern_matched_paths_when_no_graph(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / "vendor.toml", '[[vendor]]\nname = "demo"\necosystem = "python"\n')
    _write(tmp_path / "vendor" / "demo" / "CLAUDE.md", "# demo\n")
    _write(
        tmp_path / ".claude" / "skills" / "codecompass" / "SKILL.md",
        _skill_frontmatter("codecompass"),
    )
    _write(
        tmp_path / ".claude" / "skills" / "codecompass-demo" / "SKILL.md",
        _skill_frontmatter("codecompass-demo"),
    )
    _write(
        tmp_path / ".cursor" / "rules" / "codecompass-demo.mdc",
        "---\ndescription: test\nalwaysApply: false\n---\n\nBody.\n",
    )
    _write(tmp_path / ".claude" / "commands" / "discovery.md", "discovery body\n")
    # A hand-renamed/unrelated third-party skill that must never be touched.
    _write(
        tmp_path / ".claude" / "skills" / "hand-written" / "SKILL.md",
        _skill_frontmatter("hand-written"),
    )
    assert not (tmp_path / "context-graph.db").exists()

    result = runner.invoke(app, ["undo", "--dry-run"])

    assert result.exit_code == 0, result.output
    assert "vendor/demo" in result.output
    assert "vendor.toml" in result.output
    assert ".claude/skills/codecompass" in result.output
    assert ".cursor/rules/codecompass-demo.mdc" in result.output
    assert ".claude/commands/discovery.md" in result.output
    assert "hand-written" not in result.output
    # No graph existed, so it's never enumerated for deletion either.
    assert "context-graph.db" not in result.output


def test_undo_fallback_yes_cleans_up_without_erroring_on_missing_graph(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mirrors the plan's `init --scan`-only scratch-project check: only
    `vendor.toml` (and whatever partial state) exists, no `sync` ever ran,
    so there is no `context-graph.db` at all.
    """
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / "vendor.toml", '[[vendor]]\nname = "demo"\necosystem = "python"\n')
    assert not (tmp_path / "context-graph.db").exists()

    result = runner.invoke(app, ["undo", "--yes"])

    assert result.exit_code == 0, result.output
    assert not (tmp_path / "vendor.toml").exists()


def test_undo_fallback_preserves_hand_written_skill(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / "vendor.toml", '[[vendor]]\nname = "demo"\necosystem = "python"\n')
    _write(
        tmp_path / ".claude" / "skills" / "hand-written" / "SKILL.md",
        _skill_frontmatter("hand-written"),
    )

    result = runner.invoke(app, ["undo", "--yes"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / ".claude" / "skills" / "hand-written" / "SKILL.md").exists()


# --- nothing to undo -------------------------------------------------------


def test_undo_nothing_to_remove_prints_note_and_exits_0(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["undo", "--dry-run"])

    assert result.exit_code == 0, result.output
    assert "nothing" in result.output.lower()
