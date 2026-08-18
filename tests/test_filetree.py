from pathlib import Path

import codecompass.filetree as filetree_module
from codecompass.core import Ecosystem
from codecompass.filetree import (
    build_symbol_index,
    render_filetree_json,
    render_filetree_markdown,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _build_pruned_sample_tree(root: Path) -> None:
    (root / "index.py").write_text(
        '"""Entry point for the demo package."""\n\ndef main() -> None:\n    pass\n',
        encoding="utf-8",
    )
    (root / "node_modules").mkdir()
    (root / "node_modules" / "foo.js").write_text("module.exports = {};\n", encoding="utf-8")
    (root / "dist").mkdir()
    (root / "dist" / "bundle.js").write_text("/* built */\n", encoding="utf-8")
    (root / "lib.min.js").write_text("!function(){}();\n", encoding="utf-8")


def test_render_filetree_markdown_prunes_directories_and_files(tmp_path: Path) -> None:
    _build_pruned_sample_tree(tmp_path)

    markdown = render_filetree_markdown(tmp_path, Ecosystem.PYTHON)

    assert "index.py" in markdown
    assert "node_modules" not in markdown
    assert "dist" not in markdown
    assert "bundle.js" not in markdown
    assert "lib.min.js" not in markdown


def test_render_filetree_markdown_includes_purpose_annotation(tmp_path: Path) -> None:
    (tmp_path / "greeting.py").write_text(
        (FIXTURES / "sample_module_with_all.py").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    markdown = render_filetree_markdown(tmp_path, Ecosystem.PYTHON)

    assert "greeting.py  — Return a friendly greeting." in markdown


def test_render_filetree_markdown_omits_version_numbers(tmp_path: Path) -> None:
    (tmp_path / "plain.txt").write_text("just some text\n", encoding="utf-8")

    markdown = render_filetree_markdown(tmp_path, Ecosystem.NPM)

    assert "- plain.txt" in markdown  # no purpose line, no version suffix


def test_render_filetree_json_shape(tmp_path: Path) -> None:
    (tmp_path / "greeting.py").write_text(
        (FIXTURES / "sample_module_with_all.py").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    data = render_filetree_json(tmp_path, Ecosystem.PYTHON)

    assert data == {
        "entries": [{"path": "greeting.py", "purpose": "Return a friendly greeting."}]
    }


def test_build_symbol_index_lists_name_to_path(tmp_path: Path) -> None:
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "lib.rs").write_text(
        (FIXTURES / "sample_lib.rs").read_text(encoding="utf-8"), encoding="utf-8"
    )

    index = build_symbol_index(tmp_path, Ecosystem.CARGO)

    assert "add -> src/lib.rs" in index.splitlines()
    assert "Point -> src/lib.rs" in index.splitlines()


def test_build_symbol_index_excludes_pruned_files(tmp_path: Path) -> None:
    _build_pruned_sample_tree(tmp_path)

    index = build_symbol_index(tmp_path, Ecosystem.NPM)

    assert "node_modules" not in index
    assert "dist" not in index


def test_build_symbol_index_caps_with_explicit_notice(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(filetree_module, "_SYMBOL_INDEX_CAP", 2)
    (tmp_path / "many.py").write_text(
        "def a(): ...\n\ndef b(): ...\n\ndef c(): ...\n\ndef d(): ...\n",
        encoding="utf-8",
    )

    index = build_symbol_index(tmp_path, Ecosystem.PYTHON)
    lines = index.splitlines()

    assert len(lines) == 3  # 2 capped entries + the notice line
    assert lines[-1] == "... +2 more, not shown"


def test_build_symbol_index_no_notice_when_under_cap(tmp_path: Path) -> None:
    (tmp_path / "one.py").write_text("def solo(): ...\n", encoding="utf-8")

    index = build_symbol_index(tmp_path, Ecosystem.PYTHON)

    assert "not shown" not in index
    assert index.splitlines() == ["solo -> one.py"]


def test_render_filetree_markdown_marks_action_pointer_on_matching_file(tmp_path: Path) -> None:
    (tmp_path / "index.py").write_text("def main(): ...\n", encoding="utf-8")
    (tmp_path / "other.py").write_text("def helper(): ...\n", encoding="utf-8")

    markdown = render_filetree_markdown(
        tmp_path, Ecosystem.PYTHON, action_pointer=("index.py", "override main() here")
    )
    lines = markdown.splitlines()

    assert any(line.startswith("- index.py") and "← ACTION TARGET: override main() here" in line
               for line in lines)
    assert not any("ACTION TARGET" in line for line in lines if line.startswith("- other.py"))


def test_render_filetree_markdown_no_action_pointer_leaves_output_unchanged(
    tmp_path: Path,
) -> None:
    (tmp_path / "index.py").write_text("def main(): ...\n", encoding="utf-8")

    with_none = render_filetree_markdown(tmp_path, Ecosystem.PYTHON, action_pointer=None)
    without_arg = render_filetree_markdown(tmp_path, Ecosystem.PYTHON)

    assert with_none == without_arg
    assert "ACTION TARGET" not in with_none


def test_render_filetree_json_marks_action_pointer_on_matching_entry(tmp_path: Path) -> None:
    (tmp_path / "index.py").write_text("def main(): ...\n", encoding="utf-8")
    (tmp_path / "other.py").write_text("def helper(): ...\n", encoding="utf-8")

    data = render_filetree_json(
        tmp_path, Ecosystem.PYTHON, action_pointer=("index.py", "override main() here")
    )
    by_path = {entry["path"]: entry for entry in data["entries"]}

    assert by_path["index.py"]["action_pointer"] == "override main() here"
    assert "action_pointer" not in by_path["other.py"]
