from pathlib import Path

from codecompass.core import Ecosystem, VendorConfig
from codecompass.graph import DocArtifactRow, SourceFileRow
from codecompass.skill_scan import build_skill_mentions_edges, scan_skills


def _config(name: str) -> VendorConfig:
    return VendorConfig(name=name, ecosystem=Ecosystem.PYTHON)


def _write_skill(project_root: Path, dir_name: str, text: str) -> Path:
    skill_dir = project_root / ".claude" / "skills" / dir_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    path = skill_dir / "SKILL.md"
    path.write_text(text, encoding="utf-8")
    return path


def _write_mdc(project_root: Path, filename: str, text: str) -> Path:
    rules_dir = project_root / ".cursor" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    path = rules_dir / filename
    path.write_text(text, encoding="utf-8")
    return path


_SINGLE_LINE_SKILL = """---
name: codecompass
description: a short single-line description
---

# codecompass

Body text mentioning demo and app.py here.
"""

_FOLDED_SKILL = """---
name: codecompass-demo
description: >-
  A longer description that wraps
  across two lines.
---

# demo

Body text.
"""


# --- scan_skills --------------------------------------------------------------


def test_scan_skills_classifies_tool_skill(tmp_path: Path) -> None:
    _write_skill(tmp_path, "codecompass", _SINGLE_LINE_SKILL)
    configs = [_config("demo")]

    rows = scan_skills(tmp_path, configs)

    assert len(rows) == 1
    row = rows[0]
    assert row.path == ".claude/skills/codecompass/SKILL.md"
    assert row.kind == "skill"
    assert row.origin == "codecompass_tool"
    assert row.vendor_name is None
    assert row.name == "codecompass"
    assert row.description == "a short single-line description"


def test_scan_skills_classifies_per_vendor_skill_with_folded_description(tmp_path: Path) -> None:
    _write_skill(tmp_path, "codecompass-demo", _FOLDED_SKILL)
    configs = [_config("demo")]

    rows = scan_skills(tmp_path, configs)

    assert len(rows) == 1
    row = rows[0]
    assert row.origin == "codecompass_vendor"
    assert row.vendor_name == "demo"
    assert row.name == "codecompass-demo"
    assert row.description == "A longer description that wraps across two lines."


def test_scan_skills_classifies_third_party_skill(tmp_path: Path) -> None:
    _write_skill(tmp_path, "some-other-skill", _SINGLE_LINE_SKILL.replace("codecompass", "other"))
    configs = [_config("demo")]

    rows = scan_skills(tmp_path, configs)

    assert len(rows) == 1
    assert rows[0].origin == "third_party"
    assert rows[0].vendor_name is None


def test_scan_skills_codecompass_dash_vendor_dir_for_untracked_vendor_is_third_party(
    tmp_path: Path,
) -> None:
    _write_skill(tmp_path, "codecompass-untracked", _SINGLE_LINE_SKILL)
    configs = [_config("demo")]  # "untracked" isn't in configs

    rows = scan_skills(tmp_path, configs)

    assert rows[0].origin == "third_party"


def test_scan_skills_includes_cursor_mdc_files(tmp_path: Path) -> None:
    _write_mdc(
        tmp_path,
        "codecompass-demo.mdc",
        "---\ndescription: cursor rule for demo\nalwaysApply: false\n---\n\nBody.\n",
    )
    configs = [_config("demo")]

    rows = scan_skills(tmp_path, configs)

    assert len(rows) == 1
    row = rows[0]
    assert row.path == ".cursor/rules/codecompass-demo.mdc"
    assert row.kind == "cursor_mdc"
    assert row.origin == "codecompass_vendor"
    assert row.vendor_name == "demo"
    assert row.description == "cursor rule for demo"


def test_scan_skills_returns_empty_when_no_skills_or_rules_present(tmp_path: Path) -> None:
    assert scan_skills(tmp_path, [_config("demo")]) == []


def test_scan_skills_tolerates_file_without_frontmatter(tmp_path: Path) -> None:
    _write_skill(tmp_path, "codecompass", "# codecompass\n\nNo frontmatter here.\n")
    configs = [_config("demo")]

    rows = scan_skills(tmp_path, configs)

    assert len(rows) == 1
    assert rows[0].name is None
    assert rows[0].description is None


# --- discovery.md indexing (Phase 17) ------------------------------------


def _write_discovery_command(project_root: Path, text: str) -> Path:
    commands_dir = project_root / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    path = commands_dir / "discovery.md"
    path.write_text(text, encoding="utf-8")
    return path


_DISCOVERY_COMMAND_TEXT = """---
description: Explore this project's dependency context graph read-only.
---

# /discovery

Body text.
"""


def test_scan_skills_indexes_discovery_command_when_present(tmp_path: Path) -> None:
    _write_discovery_command(tmp_path, _DISCOVERY_COMMAND_TEXT)
    configs = [_config("demo")]

    rows = scan_skills(tmp_path, configs)

    assert len(rows) == 1
    row = rows[0]
    assert row.path == ".claude/commands/discovery.md"
    assert row.kind == "slash_command"
    assert row.origin == "codecompass_tool"
    assert row.vendor_name is None
    assert row.description == "Explore this project's dependency context graph read-only."


def test_scan_skills_omits_discovery_command_when_absent(tmp_path: Path) -> None:
    configs = [_config("demo")]

    rows = scan_skills(tmp_path, configs)

    assert rows == []


def test_scan_skills_indexes_discovery_command_alongside_other_artifacts(
    tmp_path: Path,
) -> None:
    _write_skill(tmp_path, "codecompass", _SINGLE_LINE_SKILL)
    _write_discovery_command(tmp_path, _DISCOVERY_COMMAND_TEXT)
    configs = [_config("demo")]

    rows = scan_skills(tmp_path, configs)

    kinds = {row.kind for row in rows}
    assert kinds == {"skill", "slash_command"}


# --- build_skill_mentions_edges -----------------------------------------------


def test_build_skill_mentions_edges_matches_vendor_and_source_file(tmp_path: Path) -> None:
    skill_path = _write_skill(tmp_path, "codecompass", _SINGLE_LINE_SKILL)
    doc_row = DocArtifactRow(
        path=skill_path.relative_to(tmp_path).as_posix(), kind="skill", origin="codecompass_tool",
    )
    configs = [_config("demo")]
    source_file_rows = [SourceFileRow(path="src/app.py")]

    edges = build_skill_mentions_edges([doc_row], configs, source_file_rows, tmp_path)

    vendor_edges = [e for e in edges if e.vendor_name is not None]
    file_edges = [e for e in edges if e.source_file_path is not None]
    assert len(vendor_edges) == 1
    assert vendor_edges[0].vendor_name == "demo"
    assert len(file_edges) == 1
    assert file_edges[0].source_file_path == "src/app.py"


def test_build_skill_mentions_edges_word_boundary_avoids_substring_false_positive(
    tmp_path: Path,
) -> None:
    """Regression case from the phase plan: a vendor named "six" must not
    false-positive-match "sixty-four" in a skill's body text.
    """
    text = "---\nname: codecompass\ndescription: test\n---\n\nShips sixty-four bit values.\n"
    skill_path = _write_skill(tmp_path, "codecompass", text)
    doc_row = DocArtifactRow(
        path=skill_path.relative_to(tmp_path).as_posix(), kind="skill", origin="codecompass_tool",
    )
    configs = [_config("six")]

    edges = build_skill_mentions_edges([doc_row], configs, [], tmp_path)

    assert edges == []


def test_build_skill_mentions_edges_no_mention_produces_no_edge(tmp_path: Path) -> None:
    text = "---\nname: codecompass\ndescription: test\n---\n\nNothing relevant here.\n"
    skill_path = _write_skill(tmp_path, "codecompass", text)
    doc_row = DocArtifactRow(
        path=skill_path.relative_to(tmp_path).as_posix(), kind="skill", origin="codecompass_tool",
    )
    configs = [_config("demo")]
    source_file_rows = [SourceFileRow(path="src/app.py")]

    edges = build_skill_mentions_edges([doc_row], configs, source_file_rows, tmp_path)

    assert edges == []


def test_build_skill_mentions_edges_multiple_source_files_sharing_a_basename(
    tmp_path: Path,
) -> None:
    text = "---\nname: codecompass\ndescription: test\n---\n\nSee __init__.py for details.\n"
    skill_path = _write_skill(tmp_path, "codecompass", text)
    doc_row = DocArtifactRow(
        path=skill_path.relative_to(tmp_path).as_posix(), kind="skill", origin="codecompass_tool",
    )
    source_file_rows = [
        SourceFileRow(path="pkg_a/__init__.py"),
        SourceFileRow(path="pkg_b/__init__.py"),
    ]

    edges = build_skill_mentions_edges([doc_row], [], source_file_rows, tmp_path)

    mentioned_paths = {e.source_file_path for e in edges}
    assert mentioned_paths == {"pkg_a/__init__.py", "pkg_b/__init__.py"}
