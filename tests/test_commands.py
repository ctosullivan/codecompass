from pathlib import Path

from codecompass.commands import render_discovery_command, write_discovery_command


def test_render_discovery_command_has_frontmatter_with_description() -> None:
    content = render_discovery_command()
    lines = content.splitlines()
    assert lines[0] == "---"
    assert "description: >-" in content
    assert lines.index("---", 1) > 0  # a closing frontmatter delimiter exists


def test_render_discovery_command_allowed_tools_excludes_write_and_edit() -> None:
    content = render_discovery_command()
    assert "allowed-tools:" in content
    # The allowed-tools value never grants Write/Edit — mechanical, not
    # just instructional, enforcement of the read-only constraint.
    assert "Write" not in content.split("---")[1]  # frontmatter block only
    assert "Edit" not in content.split("---")[1]
    assert "Read" in content
    assert "Grep" in content
    assert "Glob" in content


def test_render_discovery_command_mentions_canned_queries_and_sqlite_escape_hatch() -> None:
    content = render_discovery_command()
    assert "codecompass query vendors" in content
    assert "codecompass query vendor <name>" in content
    assert "codecompass query symbol <name>" in content
    assert "codecompass query skills" in content
    assert "codecompass query relations <name>" in content
    assert "codecompass check" in content
    assert "sqlite3 context-graph.db" in content


def test_render_discovery_command_mentions_persisted_digest_files() -> None:
    content = render_discovery_command()
    assert "CLAUDE.md" in content
    assert "OVERVIEW.md" in content
    assert "FILETREE.md" in content
    assert "DEPTREE.md" in content
    assert "SKILL.md" in content


def test_render_discovery_command_states_no_write_edit_plan_or_code_change_constraint() -> None:
    content = render_discovery_command()
    assert "No `Write`" in content
    assert "No `Edit`" in content
    assert "no plan file" in content
    assert "say so explicitly and stop" in content


def test_render_discovery_command_repeats_the_constraint_at_least_twice() -> None:
    """The plan calls for the no-Write/no-Edit/no-plan/no-code-change
    constraint to be stated explicitly and repeatedly, not just once —
    a single-tool-restriction-line isn't a substitute for the model
    actually internalizing it as a repeated instruction.
    """
    content = render_discovery_command()
    assert content.count("No `Write`") >= 1
    assert content.count("Write") >= 2  # once in allowed-tools' absence framing, once+ in body
    assert content.lower().count("stop") >= 2


def test_write_discovery_command_writes_expected_path(tmp_path: Path) -> None:
    write_discovery_command(tmp_path)
    command_md = tmp_path / ".claude" / "commands" / "discovery.md"
    assert command_md.exists()
    content = command_md.read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert "description:" in content


def test_write_discovery_command_is_idempotent_and_overwrites(tmp_path: Path) -> None:
    write_discovery_command(tmp_path)
    command_md = tmp_path / ".claude" / "commands" / "discovery.md"
    first_content = command_md.read_text(encoding="utf-8")

    write_discovery_command(tmp_path)
    second_content = command_md.read_text(encoding="utf-8")

    assert first_content == second_content
