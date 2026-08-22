import json
from pathlib import Path

from codecompass.core import Ecosystem, VendorConfig
from codecompass.doc_mapping import (
    build_depends_on_edges,
    build_doc_relations_edges,
    build_documents_edges,
    build_routes_via_edges,
    collect_vendor_doc_artifacts,
    collect_vendor_upstream_doc_artifacts,
)
from codecompass.graph import DependsOnEdgeRow, DocArtifactRow, SymbolRow


def _config(name: str, ecosystem: Ecosystem = Ecosystem.PYTHON) -> VendorConfig:
    return VendorConfig(name=name, ecosystem=ecosystem)


def _write_vendor_claude_md(project_root: Path, name: str, text: str) -> None:
    vendor_dir = project_root / "vendor" / name
    vendor_dir.mkdir(parents=True, exist_ok=True)
    (vendor_dir / "CLAUDE.md").write_text(text, encoding="utf-8")


def _write_deptree(project_root: Path, name: str, tree: dict) -> None:
    vendor_dir = project_root / "vendor" / name
    vendor_dir.mkdir(parents=True, exist_ok=True)
    (vendor_dir / "deptree.json").write_text(json.dumps(tree), encoding="utf-8")


# --- collect_vendor_doc_artifacts -------------------------------------------


def test_collect_vendor_doc_artifacts_includes_claude_md(tmp_path: Path) -> None:
    _write_vendor_claude_md(tmp_path, "demo", "# demo\n")
    configs = [_config("demo")]

    rows = collect_vendor_doc_artifacts(configs, tmp_path)

    assert len(rows) == 1
    row = rows[0]
    assert row.path == "vendor/demo/CLAUDE.md"
    assert row.kind == "claude_md"
    assert row.origin == "codecompass_vendor"
    assert row.vendor_name == "demo"


def test_collect_vendor_doc_artifacts_skips_unsynced_vendor(tmp_path: Path) -> None:
    configs = [_config("demo")]

    rows = collect_vendor_doc_artifacts(configs, tmp_path)

    assert rows == []


def test_collect_vendor_doc_artifacts_includes_overview_only_if_present(tmp_path: Path) -> None:
    _write_vendor_claude_md(tmp_path, "demo", "# demo\n")
    overview_path = tmp_path / "vendor" / "demo" / "OVERVIEW.md"
    overview_path.write_text("Friendly overview.", encoding="utf-8")
    configs = [_config("demo")]

    rows = collect_vendor_doc_artifacts(configs, tmp_path)

    kinds = {row.kind for row in rows}
    assert kinds == {"claude_md", "overview"}
    overview_row = next(row for row in rows if row.kind == "overview")
    assert overview_row.path == "vendor/demo/OVERVIEW.md"
    assert overview_row.origin == "codecompass_vendor"
    assert overview_row.vendor_name == "demo"


# --- collect_vendor_upstream_doc_artifacts -----------------------------------


def _write_clone_file(project_root: Path, vendor_name: str, filename: str, text: str) -> Path:
    clone_root = project_root / "vendor" / vendor_name / "src"
    clone_root.mkdir(parents=True, exist_ok=True)
    path = clone_root / filename
    path.write_text(text, encoding="utf-8")
    return path


def test_collect_vendor_upstream_doc_artifacts_finds_readme(tmp_path: Path) -> None:
    _write_clone_file(tmp_path, "demo", "README.md", "# demo\n")
    configs = [_config("demo")]

    rows = collect_vendor_upstream_doc_artifacts(configs, tmp_path)

    assert len(rows) == 1
    row = rows[0]
    assert row.path == "vendor/demo/src/README.md"
    assert row.kind == "vendor_doc"
    assert row.origin == "vendor_upstream"
    assert row.vendor_name == "demo"
    assert row.name == "demo README.md"


def test_collect_vendor_upstream_doc_artifacts_matches_the_fixed_filename_set(
    tmp_path: Path,
) -> None:
    for filename in ("README.md", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md", "MIGRATION.md"):
        _write_clone_file(tmp_path, "demo", filename, f"# {filename}\n")
    _write_clone_file(tmp_path, "demo", "api.md", "# not in the fixed set\n")
    configs = [_config("demo")]

    rows = collect_vendor_upstream_doc_artifacts(configs, tmp_path)

    matched_names = {row.name for row in rows}
    assert matched_names == {
        "demo README.md",
        "demo CHANGELOG.md",
        "demo CONTRIBUTING.md",
        "demo SECURITY.md",
        "demo MIGRATION.md",
    }


def test_collect_vendor_upstream_doc_artifacts_matches_readme_variants(tmp_path: Path) -> None:
    _write_clone_file(tmp_path, "demo", "README.md", "# demo\n")
    _write_clone_file(tmp_path, "demo", "README.cn.md", "# demo (cn)\n")
    configs = [_config("demo")]

    rows = collect_vendor_upstream_doc_artifacts(configs, tmp_path)

    matched_names = {row.name for row in rows}
    assert matched_names == {"demo README.md", "demo README.cn.md"}


def test_collect_vendor_upstream_doc_artifacts_ignores_nested_files(tmp_path: Path) -> None:
    _write_clone_file(tmp_path, "demo", "README.md", "# demo\n")
    nested = tmp_path / "vendor" / "demo" / "src" / "docs"
    nested.mkdir(parents=True)
    (nested / "features.md").write_text("# nested, must be ignored\n", encoding="utf-8")
    configs = [_config("demo")]

    rows = collect_vendor_upstream_doc_artifacts(configs, tmp_path)

    assert [row.path for row in rows] == ["vendor/demo/src/README.md"]


def test_collect_vendor_upstream_doc_artifacts_skips_vendor_without_clone(tmp_path: Path) -> None:
    configs = [_config("demo")]

    rows = collect_vendor_upstream_doc_artifacts(configs, tmp_path)

    assert rows == []


def test_collect_vendor_upstream_doc_artifacts_ignores_files_outside_the_fixed_set(
    tmp_path: Path,
) -> None:
    _write_clone_file(tmp_path, "demo", "LICENSE", "MIT\n")
    _write_clone_file(tmp_path, "demo", "helpers.md", "# not in the fixed set\n")
    configs = [_config("demo")]

    rows = collect_vendor_upstream_doc_artifacts(configs, tmp_path)

    assert rows == []


# --- build_documents_edges ---------------------------------------------------


def test_build_documents_edges_matches_symbol_names_in_own_vendor_text(tmp_path: Path) -> None:
    _write_vendor_claude_md(tmp_path, "demo", "## API\n\ndoStuff: does the thing.\n")
    doc_rows = [
        DocArtifactRow(
            path="vendor/demo/CLAUDE.md", kind="claude_md", origin="codecompass_vendor",
            vendor_name="demo",
        )
    ]
    symbol_rows = [
        SymbolRow(vendor_name="demo", name="doStuff"),
        SymbolRow(vendor_name="demo", name="neverMentioned"),
    ]

    edges = build_documents_edges(doc_rows, symbol_rows, tmp_path)

    assert len(edges) == 1
    assert edges[0].doc_artifact_path == "vendor/demo/CLAUDE.md"
    assert edges[0].vendor_name == "demo"
    assert edges[0].symbol_name == "doStuff"


def test_build_documents_edges_does_not_cross_match_other_vendors_symbols(tmp_path: Path) -> None:
    _write_vendor_claude_md(tmp_path, "demo", "mentions otherVendorSymbol here\n")
    doc_rows = [
        DocArtifactRow(
            path="vendor/demo/CLAUDE.md", kind="claude_md", origin="codecompass_vendor",
            vendor_name="demo",
        )
    ]
    symbol_rows = [SymbolRow(vendor_name="other", name="otherVendorSymbol")]

    edges = build_documents_edges(doc_rows, symbol_rows, tmp_path)

    assert edges == []


def test_build_documents_edges_word_boundary_avoids_substring_false_positive(
    tmp_path: Path,
) -> None:
    _write_vendor_claude_md(tmp_path, "six", "This library ships sixty-four bit integers.\n")
    doc_rows = [
        DocArtifactRow(
            path="vendor/six/CLAUDE.md", kind="claude_md", origin="codecompass_vendor",
            vendor_name="six",
        )
    ]
    symbol_rows = [SymbolRow(vendor_name="six", name="six")]

    edges = build_documents_edges(doc_rows, symbol_rows, tmp_path)

    assert edges == []


def test_build_documents_edges_ignores_non_claude_or_overview_doc_artifacts(tmp_path: Path) -> None:
    skills_dir = tmp_path / ".claude" / "skills" / "codecompass"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text("doStuff appears here too\n", encoding="utf-8")
    doc_rows = [
        DocArtifactRow(
            path=".claude/skills/codecompass/SKILL.md", kind="skill", origin="codecompass_tool",
        )
    ]
    symbol_rows = [SymbolRow(vendor_name="demo", name="doStuff")]

    edges = build_documents_edges(doc_rows, symbol_rows, tmp_path)

    assert edges == []


# --- build_routes_via_edges --------------------------------------------------


def test_build_routes_via_edges_prefers_per_vendor_skill(tmp_path: Path) -> None:
    configs = [_config("demo")]
    doc_rows = [
        DocArtifactRow(
            path=".claude/skills/codecompass-demo/SKILL.md", kind="skill",
            origin="codecompass_vendor", vendor_name="demo",
        ),
        DocArtifactRow(
            path=".claude/skills/codecompass/SKILL.md", kind="skill", origin="codecompass_tool",
        ),
    ]

    edges = build_routes_via_edges(configs, doc_rows)

    assert len(edges) == 1
    assert edges[0].vendor_name == "demo"
    assert edges[0].doc_artifact_path == ".claude/skills/codecompass-demo/SKILL.md"


def test_build_routes_via_edges_falls_back_to_tool_skill(tmp_path: Path) -> None:
    configs = [_config("demo")]
    doc_rows = [
        DocArtifactRow(
            path=".claude/skills/codecompass/SKILL.md", kind="skill", origin="codecompass_tool",
        ),
    ]

    edges = build_routes_via_edges(configs, doc_rows)

    assert len(edges) == 1
    assert edges[0].vendor_name == "demo"
    assert edges[0].doc_artifact_path == ".claude/skills/codecompass/SKILL.md"


def test_build_routes_via_edges_no_edge_when_neither_skill_present() -> None:
    configs = [_config("demo")]

    edges = build_routes_via_edges(configs, [])

    assert edges == []


# --- build_depends_on_edges --------------------------------------------------


def test_build_depends_on_edges_emits_edge_for_tracked_transitive_dependency(
    tmp_path: Path,
) -> None:
    _write_deptree(
        tmp_path,
        "a",
        {
            "name": "a",
            "version": "1.0.0",
            "children": [{"name": "b", "version": "2.0.0", "children": []}],
        },
    )
    configs = [_config("a"), _config("b")]

    edges = build_depends_on_edges(configs, tmp_path)

    assert edges == [DependsOnEdgeRow(vendor_name="a", depends_on_vendor_name="b")]


def test_build_depends_on_edges_ignores_untracked_transitive_dependency(tmp_path: Path) -> None:
    _write_deptree(
        tmp_path,
        "a",
        {
            "name": "a",
            "version": "1.0.0",
            "children": [{"name": "untracked", "version": "2.0.0", "children": []}],
        },
    )
    configs = [_config("a")]

    edges = build_depends_on_edges(configs, tmp_path)

    assert edges == []


def test_build_depends_on_edges_resolves_ref_back_references(tmp_path: Path) -> None:
    _write_deptree(
        tmp_path,
        "a",
        {
            "name": "a",
            "version": "1.0.0",
            "children": [
                {
                    "name": "mid",
                    "version": "1.0.0",
                    "children": [{"ref": "b@2.0.0"}],
                },
                {"name": "b", "version": "2.0.0", "children": []},
            ],
        },
    )
    configs = [_config("a"), _config("b")]

    edges = build_depends_on_edges(configs, tmp_path)

    assert edges == [DependsOnEdgeRow(vendor_name="a", depends_on_vendor_name="b")]


def test_build_depends_on_edges_skips_vendor_without_deptree(tmp_path: Path) -> None:
    configs = [_config("a")]

    edges = build_depends_on_edges(configs, tmp_path)

    assert edges == []


def test_build_depends_on_edges_no_self_edge(tmp_path: Path) -> None:
    _write_deptree(tmp_path, "a", {"name": "a", "version": "1.0.0", "children": []})
    configs = [_config("a")]

    edges = build_depends_on_edges(configs, tmp_path)

    assert edges == []


# --- build_doc_relations_edges ------------------------------------------


def _write_spec_doc(project_root: Path, rel_path: str, text: str) -> None:
    path = project_root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_build_doc_relations_edges_matches_tracked_vendor_name(tmp_path: Path) -> None:
    _write_spec_doc(tmp_path, "README.md", "This project depends on demo for parsing.\n")
    spec_doc_rows = [DocArtifactRow(path="README.md", kind="spec_doc", origin="project")]
    configs = [_config("demo")]

    edges = build_doc_relations_edges(spec_doc_rows, configs, [], tmp_path)

    assert len(edges) == 1
    assert edges[0].source_doc_artifact_path == "README.md"
    assert edges[0].relation_kind == "mentions_dependency"
    assert edges[0].target_vendor_name == "demo"
    assert edges[0].target_doc_artifact_path is None


def test_build_doc_relations_edges_matches_other_doc_artifact_name(tmp_path: Path) -> None:
    _write_spec_doc(tmp_path, "README.md", "See the codecompass-demo skill for details.\n")
    spec_doc_rows = [DocArtifactRow(path="README.md", kind="spec_doc", origin="project")]
    other_rows = [
        DocArtifactRow(
            path=".claude/skills/codecompass-demo/SKILL.md",
            kind="skill",
            origin="codecompass_vendor",
            vendor_name="demo",
            name="codecompass-demo",
        )
    ]

    edges = build_doc_relations_edges(spec_doc_rows, [], other_rows, tmp_path)

    assert len(edges) == 1
    assert edges[0].source_doc_artifact_path == "README.md"
    assert edges[0].relation_kind == "mentions_artifact"
    assert edges[0].target_doc_artifact_path == ".claude/skills/codecompass-demo/SKILL.md"
    assert edges[0].target_vendor_name is None


def test_build_doc_relations_edges_word_boundary_avoids_substring_false_positive(
    tmp_path: Path,
) -> None:
    """Regression case, same posture as `build_documents_edges`'s /
    `build_skill_mentions_edges`'s own: a vendor named "six" must not
    false-positive-match "sixty-four" in a spec doc's body text.
    """
    _write_spec_doc(tmp_path, "README.md", "Ships sixty-four bit values.\n")
    spec_doc_rows = [DocArtifactRow(path="README.md", kind="spec_doc", origin="project")]
    configs = [_config("six")]

    edges = build_doc_relations_edges(spec_doc_rows, configs, [], tmp_path)

    assert edges == []


def test_build_doc_relations_edges_no_mention_produces_no_edge(tmp_path: Path) -> None:
    _write_spec_doc(tmp_path, "README.md", "Nothing relevant here.\n")
    spec_doc_rows = [DocArtifactRow(path="README.md", kind="spec_doc", origin="project")]
    configs = [_config("demo")]
    other_rows = [
        DocArtifactRow(
            path="vendor/demo/CLAUDE.md", kind="claude_md", origin="codecompass_vendor",
            vendor_name="demo", name="demo CLAUDE.md",
        )
    ]

    edges = build_doc_relations_edges(spec_doc_rows, configs, other_rows, tmp_path)

    assert edges == []


def test_build_doc_relations_edges_ignores_unnamed_doc_artifacts(tmp_path: Path) -> None:
    """A doc artifact with no `name` set (e.g. a Skill file whose
    frontmatter couldn't be parsed) is never a match target — nothing to
    word-boundary-search for.
    """
    _write_spec_doc(tmp_path, "README.md", "demo appears here, name=None below.\n")
    spec_doc_rows = [DocArtifactRow(path="README.md", kind="spec_doc", origin="project")]
    other_rows = [
        DocArtifactRow(
            path=".claude/skills/mystery/SKILL.md", kind="skill", origin="third_party", name=None,
        )
    ]

    edges = build_doc_relations_edges(spec_doc_rows, [], other_rows, tmp_path)

    assert edges == []


def test_build_doc_relations_edges_scans_every_spec_doc_independently(tmp_path: Path) -> None:
    _write_spec_doc(tmp_path, "README.md", "Uses demo.\n")
    _write_spec_doc(tmp_path, "docs/other.md", "No mentions here.\n")
    spec_doc_rows = [
        DocArtifactRow(path="README.md", kind="spec_doc", origin="project"),
        DocArtifactRow(path="docs/other.md", kind="spec_doc", origin="project"),
    ]
    configs = [_config("demo")]

    edges = build_doc_relations_edges(spec_doc_rows, configs, [], tmp_path)

    assert len(edges) == 1
    assert edges[0].source_doc_artifact_path == "README.md"
