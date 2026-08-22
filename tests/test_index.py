from pathlib import Path

from codecompass.core import Ecosystem, VendorConfig
from codecompass.graph import VendorRow, open_graph, rebuild_deterministic, record_enrichment
from codecompass.index import (
    RoutingRow,
    load_routing_rows,
    render_routing_table,
    update_root_claude_md,
)


def _write_vendor_claude_md(project_root: Path, name: str, version: str) -> None:
    vendor_dir = project_root / "vendor" / name
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "CLAUDE.md").write_text(
        f"# {name}\n\n## Metadata\n\n- **Installed version:** {version}\n",
        encoding="utf-8",
    )


def test_load_routing_rows_reads_version_from_synced_claude_md(tmp_path: Path) -> None:
    _write_vendor_claude_md(tmp_path, "turndown", "7.1.2")
    configs = [VendorConfig(name="turndown", ecosystem=Ecosystem.NPM)]

    rows = load_routing_rows(configs, tmp_path)

    assert rows == [RoutingRow(config=configs[0], version="7.1.2", enriched=False)]


def test_load_routing_rows_none_when_not_yet_synced(tmp_path: Path) -> None:
    configs = [VendorConfig(name="unsynced", ecosystem=Ecosystem.NPM)]

    rows = load_routing_rows(configs, tmp_path)

    assert rows[0].version is None


def test_load_routing_rows_enriched_false_when_no_graph_yet(tmp_path: Path) -> None:
    """A project that's only run `init`/one `sync <vendor>`, never a
    whole-project sync, has no context-graph.db yet — falls back to "not
    enriched" rather than erroring.
    """
    configs = [VendorConfig(name="turndown", ecosystem=Ecosystem.NPM)]

    rows = load_routing_rows(configs, tmp_path)

    assert rows[0].enriched is False


def test_load_routing_rows_enriched_true_when_graph_says_so(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(
        conn,
        vendors=[VendorRow(name="turndown", ecosystem="npm", installed_version="7.1.2")],
        source_files=[],
        symbols=[],
        uses_edges=[],
        doc_artifacts=[],
        documents_edges=[],
        skill_mentions_edges=[],
        routes_via_edges=[],
        depends_on_edges=[],
    )
    (vendor_id,) = conn.execute(
        "SELECT id FROM vendors WHERE name = 'turndown'"
    ).fetchone()
    record_enrichment(
        conn,
        vendor_id,
        symbol_set_hash="hash",
        model="claude-haiku-4-5",
        generated_at="2026-01-01T00:00:00+00:00",
    )
    conn.close()
    configs = [VendorConfig(name="turndown", ecosystem=Ecosystem.NPM)]

    rows = load_routing_rows(configs, tmp_path)

    assert rows[0].enriched is True


def test_render_routing_table_includes_expected_columns() -> None:
    row = RoutingRow(
        config=VendorConfig(name="turndown", ecosystem=Ecosystem.NPM),
        version="7.1.2",
        enriched=True,
    )
    table = render_routing_table([row])

    assert "| turndown | `vendor/turndown/` | 7.1.2 | yes |" in table
    assert "[DEPTREE.md](./vendor/turndown/DEPTREE.md)" in table
    assert "API questions and known gotchas" in table


def test_render_routing_table_not_enriched_shows_general_usage_consult_when() -> None:
    row = RoutingRow(
        config=VendorConfig(name="turndown", ecosystem=Ecosystem.NPM),
        version="7.1.2",
        enriched=False,
    )
    table = render_routing_table([row])

    assert "| turndown | `vendor/turndown/` | 7.1.2 | no |" in table
    assert "general usage questions" in table


def test_render_routing_table_shows_not_synced_placeholder() -> None:
    row = RoutingRow(
        config=VendorConfig(name="turndown", ecosystem=Ecosystem.NPM),
        version=None,
        enriched=False,
    )
    table = render_routing_table([row])

    assert "_not synced_" in table


def test_update_root_claude_md_first_run_appends_marker_block(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text(
        "# My Project\n\nSome hand-written notes.\n", encoding="utf-8"
    )

    update_root_claude_md(tmp_path, "| table |")

    content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Some hand-written notes." in content
    assert "<!-- codecompass:start -->" in content
    assert "<!-- codecompass:end -->" in content
    assert "| table |" in content


def test_update_root_claude_md_creates_file_when_missing(tmp_path: Path) -> None:
    update_root_claude_md(tmp_path, "| table |")

    content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "| table |" in content


def test_update_root_claude_md_is_idempotent_and_preserves_surrounding_content(
    tmp_path: Path,
) -> None:
    (tmp_path / "CLAUDE.md").write_text(
        "# My Project\n\nBefore.\n\n"
        "<!-- codecompass:start -->\nold table\n<!-- codecompass:end -->\n\n"
        "After.\n",
        encoding="utf-8",
    )

    update_root_claude_md(tmp_path, "new table")

    content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert content.count("<!-- codecompass:start -->") == 1
    assert content.count("<!-- codecompass:end -->") == 1
    assert "old table" not in content
    assert "new table" in content
    assert "Before." in content
    assert "After." in content
