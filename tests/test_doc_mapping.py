import json
from pathlib import Path

from codecompass.core import Ecosystem, VendorConfig
from codecompass.doc_mapping import (
    build_depends_on_edges,
    build_documents_edges,
    build_routes_via_edges,
    collect_vendor_doc_artifacts,
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
