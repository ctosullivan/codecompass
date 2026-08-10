from pathlib import Path

from depcompass.core import Depth, Ecosystem, VendorConfig
from depcompass.index import (
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
    configs = [VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)]

    rows = load_routing_rows(configs, tmp_path)

    assert rows == [RoutingRow(config=configs[0], version="7.1.2")]


def test_load_routing_rows_none_when_not_yet_synced(tmp_path: Path) -> None:
    configs = [VendorConfig(name="unsynced", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)]

    rows = load_routing_rows(configs, tmp_path)

    assert rows[0].version is None


def test_render_routing_table_includes_expected_columns() -> None:
    row = RoutingRow(
        config=VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE),
        version="7.1.2",
    )
    table = render_routing_table([row])

    assert "| turndown | `vendor/turndown/` | 7.1.2 | surface |" in table
    assert "[DEPTREE.md](./vendor/turndown/DEPTREE.md)" in table


def test_render_routing_table_shows_not_synced_placeholder() -> None:
    row = RoutingRow(
        config=VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE),
        version=None,
    )
    table = render_routing_table([row])

    assert "_not synced_" in table


def test_update_root_claude_md_first_run_appends_marker_block(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# My Project\n\nSome hand-written notes.\n", encoding="utf-8")

    update_root_claude_md(tmp_path, "| table |")

    content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Some hand-written notes." in content
    assert "<!-- depcompass:start -->" in content
    assert "<!-- depcompass:end -->" in content
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
        "<!-- depcompass:start -->\nold table\n<!-- depcompass:end -->\n\n"
        "After.\n",
        encoding="utf-8",
    )

    update_root_claude_md(tmp_path, "new table")

    content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert content.count("<!-- depcompass:start -->") == 1
    assert content.count("<!-- depcompass:end -->") == 1
    assert "old table" not in content
    assert "new table" in content
    assert "Before." in content
    assert "After." in content
