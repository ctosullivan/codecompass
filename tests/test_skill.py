from pathlib import Path

from codecompass.core import Depth, Ecosystem, VendorConfig, VendorDigest
from codecompass.skill import (
    render_cursor_mdc,
    render_tool_skill,
    render_vendor_skill,
    write_cursor_mdc,
    write_tool_skill,
    write_vendor_skill,
)


def _configs() -> list[VendorConfig]:
    return [
        VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.FULL),
        VendorConfig(name="lodash", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE),
    ]


def _digest(**overrides: object) -> VendorDigest:
    config = overrides.pop("config", None) or VendorConfig(
        name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.FULL
    )
    defaults: dict[str, object] = {"config": config, "installed_version": "7.1.2"}
    defaults.update(overrides)
    return VendorDigest(**defaults)  # type: ignore[arg-type]


def test_render_tool_skill_lists_commands_and_vendor_table() -> None:
    content = render_tool_skill(_configs())
    assert "name: codecompass" in content
    assert "codecompass promote <vendor>" in content
    assert "| turndown | npm | full |" in content
    assert "| lodash | npm | surface |" in content
    assert "2 tracked, 1 at `full` depth" in content


def test_write_tool_skill_writes_expected_path(tmp_path: Path) -> None:
    write_tool_skill(tmp_path, _configs())
    skill_md = tmp_path / ".claude" / "skills" / "codecompass" / "SKILL.md"
    assert skill_md.exists()
    assert "name: codecompass" in skill_md.read_text(encoding="utf-8")


def test_render_vendor_skill_name_cannot_collide_with_tool_skill() -> None:
    content = render_vendor_skill(_digest())
    assert "name: codecompass-turndown" in content


def test_render_vendor_skill_includes_technical_description_and_action_pointer() -> None:
    content = render_vendor_skill(
        _digest(
            technical_description="Converts HTML to Markdown via visitor rules.",
            action_pointer_file="src/commonmark-rules.js",
            action_pointer_note="override fencedCodeBlock here",
        )
    )
    assert "Converts HTML to Markdown via visitor rules." in content
    assert "src/commonmark-rules.js" in content
    assert "override fencedCodeBlock here" in content


def test_render_vendor_skill_description_capped_length() -> None:
    long_overview = "x" * 1000
    content = render_vendor_skill(_digest(conversational_overview=long_overview))
    description_line = next(line for line in content.splitlines() if line.startswith("  API"))
    assert len(description_line) < 600


def test_write_vendor_skill_bundles_filetree_and_deptree_as_references(tmp_path: Path) -> None:
    vendor_dir = tmp_path / "vendor" / "turndown"
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "FILETREE.md").write_text("# tree", encoding="utf-8")
    (vendor_dir / "DEPTREE.md").write_text("# deps", encoding="utf-8")

    write_vendor_skill(tmp_path, _digest())

    skill_dir = tmp_path / ".claude" / "skills" / "codecompass-turndown"
    assert (skill_dir / "SKILL.md").exists()
    assert (skill_dir / "references" / "FILETREE.md").read_text(encoding="utf-8") == "# tree"
    assert (skill_dir / "references" / "DEPTREE.md").read_text(encoding="utf-8") == "# deps"


def test_write_vendor_skill_tolerates_missing_tree_files(tmp_path: Path) -> None:
    write_vendor_skill(tmp_path, _digest())  # no vendor/turndown/ dir at all — should not raise
    skill_dir = tmp_path / ".claude" / "skills" / "codecompass-turndown"
    assert (skill_dir / "SKILL.md").exists()
    assert not (skill_dir / "references" / "FILETREE.md").exists()


def test_render_cursor_mdc_includes_technical_description() -> None:
    content = render_cursor_mdc(_digest(technical_description="Converts HTML to Markdown."))
    assert "alwaysApply: false" in content
    assert "Converts HTML to Markdown." in content


def test_write_cursor_mdc_writes_expected_path(tmp_path: Path) -> None:
    write_cursor_mdc(tmp_path, _digest())
    mdc_path = tmp_path / ".cursor" / "rules" / "codecompass-turndown.mdc"
    assert mdc_path.exists()
