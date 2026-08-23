from pathlib import Path

from codecompass.spec_docs import scan_spec_docs


def _write(project_root: Path, rel_path: str, text: str = "content\n") -> Path:
    path = project_root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_scan_spec_docs_finds_root_level_named_files(tmp_path: Path) -> None:
    _write(tmp_path, "README.md")
    _write(tmp_path, "ARCHITECTURE.md")
    _write(tmp_path, "REQUIREMENTS.md")
    _write(tmp_path, "PRD.md")

    rows = scan_spec_docs(tmp_path)

    paths = {row.path for row in rows}
    assert paths == {"README.md", "ARCHITECTURE.md", "REQUIREMENTS.md", "PRD.md"}
    for row in rows:
        assert row.kind == "spec_doc"
        assert row.origin == "project"
        assert row.vendor_name is None


def test_scan_spec_docs_finds_nested_glob_directories(tmp_path: Path) -> None:
    _write(tmp_path, "docs/usage.md")
    _write(tmp_path, "docs/nested/guide.md")
    _write(tmp_path, "architecture/overview.md")
    _write(tmp_path, "decisions/0001-example.md")
    _write(tmp_path, "spec/thing.md")
    _write(tmp_path, "specs/other.md")
    _write(tmp_path, "rfcs/0001.md")

    rows = scan_spec_docs(tmp_path)

    paths = {row.path for row in rows}
    assert paths == {
        "docs/usage.md",
        "docs/nested/guide.md",
        "architecture/overview.md",
        "decisions/0001-example.md",
        "spec/thing.md",
        "specs/other.md",
        "rfcs/0001.md",
    }


def test_scan_spec_docs_finds_dot_spec_dot_md_suffix(tmp_path: Path) -> None:
    _write(tmp_path, "checkout.spec.md")

    rows = scan_spec_docs(tmp_path)

    assert [row.path for row in rows] == ["checkout.spec.md"]


def test_scan_spec_docs_excludes_changelog_contributing_license_and_root_claude_md(
    tmp_path: Path,
) -> None:
    _write(tmp_path, "CHANGELOG.md")
    _write(tmp_path, "CONTRIBUTING.md")
    _write(tmp_path, "CLAUDE.md")
    _write(tmp_path, "LICENSE")
    _write(tmp_path, "LICENSE.md")
    _write(tmp_path, "README.md")  # the one real spec doc among these

    rows = scan_spec_docs(tmp_path)

    assert [row.path for row in rows] == ["README.md"]


def test_scan_spec_docs_prunes_nested_build_or_dependency_noise_dirs(tmp_path: Path) -> None:
    """None of the default glob roots (`docs/`, `architecture/`, etc.) sit
    *inside* `vendor/`/`node_modules/`/`.git/` — they're anchored at the
    project root — so the prune-dir check only actually bites for the
    (unusual, but not impossible) case of one of *those* names nested
    underneath an already-matched spec-doc directory, e.g. a `docs/`
    subtree that itself vendors a copy of some other project's docs.
    """
    _write(tmp_path, "docs/vendor/README.md")
    _write(tmp_path, "architecture/node_modules/x.md")
    _write(tmp_path, "decisions/.git/x.md")
    _write(tmp_path, "docs/normal/README.md")  # the one real spec doc among these

    rows = scan_spec_docs(tmp_path)

    assert [row.path for row in rows] == ["docs/normal/README.md"]


def test_scan_spec_docs_never_reaches_into_pruned_top_level_dirs_by_construction(
    tmp_path: Path,
) -> None:
    """Even without the prune-dir check at all, none of the default glob
    patterns can reach into `vendor/`/`.claude/`/`.cursor/`/
    `node_modules/`/`.git/` — each pattern's first path segment is a fixed
    literal (`docs`, `architecture`, `decisions`, `spec`, `specs`, `rfcs`)
    that never matches any of those directory names, so a markdown file
    living inside one of them is excluded by construction, not just by the
    prune-dir check.
    """
    _write(tmp_path, "vendor/some-lib/docs/README.md")
    _write(tmp_path, ".claude/skills/codecompass/docs/README.md")
    _write(tmp_path, ".cursor/rules/docs/README.md")
    _write(tmp_path, "node_modules/pkg/docs/README.md")
    _write(tmp_path, ".git/docs/README.md")
    _write(tmp_path, "docs/README.md")  # the one real spec doc among these

    rows = scan_spec_docs(tmp_path)

    assert [row.path for row in rows] == ["docs/README.md"]


def test_scan_spec_docs_returns_empty_for_project_with_no_spec_docs(tmp_path: Path) -> None:
    assert scan_spec_docs(tmp_path) == []


def test_scan_spec_docs_deduplicates_a_path_matched_by_more_than_one_glob(
    tmp_path: Path,
) -> None:
    # docs/**/*.md and *.spec.md never overlap in practice, but a file
    # nested under a glob-matched directory tree still shows up only once
    # even walking multiple `**` segments.
    _write(tmp_path, "docs/a/b/c/deep.md")

    rows = scan_spec_docs(tmp_path)

    assert [row.path for row in rows] == ["docs/a/b/c/deep.md"]


def test_scan_spec_docs_ignores_unrelated_root_markdown_files(tmp_path: Path) -> None:
    _write(tmp_path, "NOTES.md")

    rows = scan_spec_docs(tmp_path)

    assert rows == []


def test_scan_spec_docs_finds_ai_docs_directory(tmp_path: Path) -> None:
    _write(tmp_path, "ai-docs/README.md")
    _write(tmp_path, "ai-docs/CLAUDE.md")

    rows = scan_spec_docs(tmp_path)

    paths = {row.path for row in rows}
    assert paths == {"ai-docs/README.md", "ai-docs/CLAUDE.md"}
    # ai-docs/CLAUDE.md is not root-level, so the root-only CLAUDE.md
    # exclusion correctly does not apply to it.
