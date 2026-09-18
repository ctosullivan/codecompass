from pathlib import Path

from codecompass.spec_docs import (
    _extract_title,
    _has_pinned_reference_frontmatter,
    _is_specific_enough,
    scan_spec_docs,
)


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


def test_scan_spec_docs_finds_dev_docs_directory(tmp_path: Path) -> None:
    # Phase 49 (CG-002): a real project (Ledgerkit) names its
    # developer-facing spec/architecture docs `dev-docs/` rather than
    # `docs/`/`architecture/`, and the fixed glob list had no entry for
    # it — `query relations` returned an authoritative "not found" for a
    # real, current, load-bearing file. Nested paths must resolve too
    # (CG-002 was independently re-confirmed to extend past top-level
    # `dev-docs/` files).
    _write(tmp_path, "dev-docs/hledger-compatibility.md")
    _write(tmp_path, "dev-docs/planning/core-redefinition/07-query-regex.md")

    rows = scan_spec_docs(tmp_path)

    paths = {row.path for row in rows}
    assert paths == {
        "dev-docs/hledger-compatibility.md",
        "dev-docs/planning/core-redefinition/07-query-regex.md",
    }


# Phase 55b (closes CG-004): `spec_doc` rows previously always got
# `name=None`, which structurally excluded every one of them from
# `doc_mapping.build_doc_relations_edges`'s `mentions_artifact` matching
# — two independent real-task findings (CodeCompass's own Phase 54,
# Ledgerkit's `CC-LK-001`) confirmed this meant two obviously-related
# spec docs could never mechanically relate to each other, in any
# project.


def test_extract_title_reads_the_first_h1_heading(tmp_path: Path) -> None:
    path = _write(tmp_path, "docs/usage.md", "# Usage Guide\n\nSome body text.\n")

    assert _extract_title(path) == "Usage Guide"


def test_extract_title_ignores_headings_below_h1(tmp_path: Path) -> None:
    # Falls through to the stem ("usage"), which is then rejected by
    # _is_specific_enough (a single bare word, no digit/hyphen) — None,
    # not a false-positive-prone generic match target. See
    # test_extract_title_falls_back_to_a_specific_enough_stem_when_no_h1
    # for the case where the stem itself IS specific enough to keep.
    path = _write(tmp_path, "docs/usage.md", "## Not a title\n\nBody.\n")

    assert _extract_title(path) is None


def test_extract_title_uses_the_first_h1_when_multiple_exist(tmp_path: Path) -> None:
    path = _write(tmp_path, "docs/usage.md", "# First Title\n\nBody.\n\n# Second Title\n")

    assert _extract_title(path) == "First Title"


def test_extract_title_falls_back_to_a_specific_enough_stem_when_no_h1(tmp_path: Path) -> None:
    path = _write(tmp_path, "dev-docs/hledger-compatibility.md", "No heading at all.\n")

    assert _extract_title(path) == "hledger-compatibility"


def test_extract_title_returns_none_for_an_empty_file_with_a_generic_stem(tmp_path: Path) -> None:
    # "empty" is a single bare word with no digit/hyphen — the same
    # noise pattern a bare project-name README title has (see
    # _is_specific_enough's own docstring); correctly None, not a
    # false-positive-prone match target.
    path = _write(tmp_path, "docs/empty.md", "")

    assert _extract_title(path) is None


def test_extract_title_returns_none_for_an_unreadable_path_with_a_generic_stem(
    tmp_path: Path,
) -> None:
    # A path that doesn't exist on disk behaves the same as "unreadable" —
    # never raises, degrades to the stem, which here is also rejected as
    # not specific enough ("missing", a single bare word).
    missing = tmp_path / "docs" / "missing.md"

    assert _extract_title(missing) is None


def test_extract_title_keeps_an_unreadable_paths_stem_when_specific_enough(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "dev-docs" / "hledger-compatibility.md"

    assert _extract_title(missing) == "hledger-compatibility"


def test_is_specific_enough_rejects_a_bare_project_name_style_title() -> None:
    """The real noise case this guard exists for, found live against the
    real Ledgerkit repo: a root README's H1 is just the bare repo name
    (`# ledgerkit`), which would otherwise match nearly every doc in the
    project purely because they all mention the project's own name in
    ordinary prose.
    """
    assert _is_specific_enough("ledgerkit") is False
    assert _is_specific_enough("Architecture") is False
    assert _is_specific_enough("Usage Guide") is True
    assert _is_specific_enough("07-query-regex") is True
    assert _is_specific_enough("hledger-compatibility") is True


def test_scan_spec_docs_populates_name_from_the_h1_heading(tmp_path: Path) -> None:
    _write(tmp_path, "docs/usage.md", "# Usage Guide\n\nBody.\n")

    rows = scan_spec_docs(tmp_path)

    assert len(rows) == 1
    assert rows[0].name == "Usage Guide"


def test_scan_spec_docs_populates_name_from_the_stem_when_no_h1(tmp_path: Path) -> None:
    _write(tmp_path, "dev-docs/hledger-compatibility.md", "No heading here.\n")

    rows = scan_spec_docs(tmp_path)

    assert len(rows) == 1
    assert rows[0].name == "hledger-compatibility"


# --- Phase 54c: origin='pinned_reference' detection (CG-005, REQ-DOCORIGIN-002/003) ---

_PINNED_REFERENCE_FRONTMATTER = """---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Query.hs
lines: [868, 878]
content_hash: sha256:deadbeef
extracted_at: 2026-09-18T00:00:00+00:00
---

# some-excerpt

Excerpt body.
"""


def test_scan_spec_docs_pinned_reference_frontmatter(tmp_path: Path) -> None:
    """REQ-DOCORIGIN-002's own example: a file whose leading content is
    ingestion-pipeline frontmatter (both `resolved_commit`/`source_url`
    keys present) is classified `origin='pinned_reference'`, not
    `'project'`.
    """
    _write(tmp_path, "dev-docs/hledger-reference/some-excerpt.md", _PINNED_REFERENCE_FRONTMATTER)

    rows = scan_spec_docs(tmp_path)

    assert len(rows) == 1
    assert rows[0].origin == "pinned_reference"


def test_scan_spec_docs_frontmatter_missing_one_key_stays_project(tmp_path: Path) -> None:
    """REQ-DOCORIGIN-002: frontmatter missing either required key keeps
    the existing `origin='project'` behaviour unchanged — both keys are
    required, not either.
    """
    only_source_url = """---
reference: hledger
source_url: https://github.com/simonmichael/hledger
---

# partial
"""
    _write(tmp_path, "dev-docs/hledger-reference/partial.md", only_source_url)

    rows = scan_spec_docs(tmp_path)

    assert len(rows) == 1
    assert rows[0].origin == "project"


def test_scan_spec_docs_ordinary_file_without_frontmatter_stays_project(tmp_path: Path) -> None:
    """The pre-existing behaviour for ordinary hand-authored content —
    unaffected by Phase 54c's new detection branch.
    """
    _write(tmp_path, "dev-docs/hledger-compatibility.md", "# Compat notes\n\nOrdinary prose.\n")

    rows = scan_spec_docs(tmp_path)

    assert len(rows) == 1
    assert rows[0].origin == "project"


def test_has_pinned_reference_frontmatter_requires_both_keys() -> None:
    assert _has_pinned_reference_frontmatter(_PINNED_REFERENCE_FRONTMATTER) is True
    assert _has_pinned_reference_frontmatter("---\nsource_url: x\n---\nbody\n") is False
    assert _has_pinned_reference_frontmatter("---\nresolved_commit: x\n---\nbody\n") is False
    assert _has_pinned_reference_frontmatter("no frontmatter at all\n") is False
    assert _has_pinned_reference_frontmatter("---\nunterminated: true\n") is False
