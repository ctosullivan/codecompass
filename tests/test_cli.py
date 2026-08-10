import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

import depcompass.cli as cli_module
from depcompass.cli import app
from depcompass.config import load_vendor_config
from depcompass.core import VendorDigest

runner = CliRunner()


def test_init_creates_parseable_vendor_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"lodash": "^4.0.0"}}), encoding="utf-8"
    )

    result = runner.invoke(app, ["init", "--scan", "package.json"])

    assert result.exit_code == 0, result.output
    vendors = load_vendor_config(tmp_path / "vendor.toml")
    assert [v.name for v in vendors] == ["lodash"]


def test_init_errors_when_vendor_toml_already_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"lodash": "^4.0.0"}}), encoding="utf-8"
    )
    (tmp_path / "vendor.toml").write_text("# hand-edited\n", encoding="utf-8")

    result = runner.invoke(app, ["init", "--scan", "package.json"])

    assert result.exit_code == 1
    assert "already exists" in result.output
    assert (tmp_path / "vendor.toml").read_text(encoding="utf-8") == "# hand-edited\n"


def test_sync_all_vendors_end_to_end_real_python_adapter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Real end-to-end run against an already-installed package (pytest),
    same live-package pattern as Phase 2's adapter smoke tests — no
    mocking of sync/adapters here.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "pytest"\necosystem = "python"\ndepth = "surface"\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["sync"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "vendor" / "pytest" / "CLAUDE.md").exists()
    assert (tmp_path / "vendor" / "pytest" / "FILETREE.md").exists()


def test_sync_unknown_vendor_name_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "pytest"\necosystem = "python"\ndepth = "surface"\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["sync", "not-a-real-vendor"])

    assert result.exit_code == 1
    assert "not found in vendor.toml" in result.output


def test_sync_single_vendor_filters_by_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "a"\necosystem = "python"\ndepth = "surface"\n\n'
        '[[vendor]]\nname = "b"\necosystem = "python"\ndepth = "surface"\n',
        encoding="utf-8",
    )
    synced_names: list[str] = []

    def _fake_sync_all(configs, project_root):  # noqa: ANN001
        synced_names.extend(c.name for c in configs)
        return [VendorDigest(config=c, installed_version="1.0.0") for c in configs]

    monkeypatch.setattr(cli_module, "sync_all", _fake_sync_all)

    result = runner.invoke(app, ["sync", "a"])

    assert result.exit_code == 0, result.output
    assert synced_names == ["a"]


def test_index_injects_routing_table_into_root_claude_md(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "turndown"\necosystem = "npm"\ndepth = "surface"\n',
        encoding="utf-8",
    )
    vendor_dir = tmp_path / "vendor" / "turndown"
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "CLAUDE.md").write_text(
        "# turndown\n\n## Metadata\n\n- **Installed version:** 7.1.2\n", encoding="utf-8"
    )
    (tmp_path / "CLAUDE.md").write_text("# My Project\n", encoding="utf-8")

    result = runner.invoke(app, ["index"])

    assert result.exit_code == 0, result.output
    root_claude_md = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "turndown" in root_claude_md
    assert "7.1.2" in root_claude_md
    assert "<!-- depcompass:start -->" in root_claude_md


def test_check_command_is_still_a_stub() -> None:
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "not yet implemented" in result.output


def test_chat_command_is_still_a_stub() -> None:
    result = runner.invoke(app, ["chat"])
    assert result.exit_code == 1
    assert "not yet implemented" in result.output
