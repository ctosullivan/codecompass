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

    def _fake_sync_all(configs, project_root, *, budget=None):  # noqa: ANN001
        synced_names.extend(c.name for c in configs)
        return [VendorDigest(config=c, installed_version="1.0.0") for c in configs]

    monkeypatch.setattr(cli_module, "sync_all", _fake_sync_all)

    result = runner.invoke(app, ["sync", "a"])

    assert result.exit_code == 0, result.output
    assert synced_names == ["a"]


def test_sync_budget_too_low_aborts_before_any_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "turndown"\necosystem = "npm"\ndepth = "full"\n'
        'context_path = "README.md"\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["sync", "--budget", "0"])

    assert result.exit_code == 1
    assert "exceeds --budget" in result.output
    assert not (tmp_path / "vendor").exists()


def test_sync_reports_gap_analysis_failure_and_exits_nonzero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "turndown"\necosystem = "npm"\ndepth = "surface"\n',
        encoding="utf-8",
    )

    def _fake_sync_all(configs, project_root, *, budget=None):  # noqa: ANN001
        return [
            VendorDigest(
                config=c,
                installed_version="1.0.0",
                gap_analysis_error="Anthropic API call failed: timeout",
            )
            for c in configs
        ]

    monkeypatch.setattr(cli_module, "sync_all", _fake_sync_all)

    result = runner.invoke(app, ["sync"])

    assert result.exit_code == 1
    assert "gap analysis failed" in result.output
    assert "timeout" in result.output


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


def _write_vendor_toml_and_synced_claude_md(
    tmp_path: Path, *, name: str = "demo", ecosystem: str = "python", recorded: str = "1.0.0"
) -> None:
    (tmp_path / "vendor.toml").write_text(
        f'[[vendor]]\nname = "{name}"\necosystem = "{ecosystem}"\ndepth = "surface"\n',
        encoding="utf-8",
    )
    vendor_dir = tmp_path / "vendor" / name
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "CLAUDE.md").write_text(
        f"# {name}\n\n## Metadata\n\n- **Installed version:** {recorded}\n", encoding="utf-8"
    )


def test_check_bare_always_exits_0_even_with_major_delta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_vendor_toml_and_synced_claude_md(tmp_path, recorded="1.0.0")
    monkeypatch.setattr(
        "depcompass.staleness.get_adapter",
        lambda config, project_root: _FakeStalenessAdapter(version="2.0.0"),
    )

    result = runner.invoke(app, ["check"])

    assert result.exit_code == 0, result.output
    assert "major" in result.output


def test_check_strict_exits_1_on_major_delta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_vendor_toml_and_synced_claude_md(tmp_path, recorded="1.0.0")
    monkeypatch.setattr(
        "depcompass.staleness.get_adapter",
        lambda config, project_root: _FakeStalenessAdapter(version="2.0.0"),
    )

    result = runner.invoke(app, ["check", "--strict"])

    assert result.exit_code == 1


def test_check_strict_exits_0_on_minor_or_patch_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_vendor_toml_and_synced_claude_md(tmp_path, recorded="1.0.0")
    monkeypatch.setattr(
        "depcompass.staleness.get_adapter",
        lambda config, project_root: _FakeStalenessAdapter(version="1.1.0"),
    )

    result = runner.invoke(app, ["check", "--strict"])

    assert result.exit_code == 0, result.output


def test_check_strict_and_fix_together_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_vendor_toml_and_synced_claude_md(tmp_path)

    result = runner.invoke(app, ["check", "--strict", "--fix"])

    assert result.exit_code == 1
    assert "mutually exclusive" in result.output


def test_check_fix_regenerates_stale_vendor_and_exits_0(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_vendor_toml_and_synced_claude_md(tmp_path, recorded="1.0.0")
    monkeypatch.setattr(
        "depcompass.staleness.get_adapter",
        lambda config, project_root: _FakeStalenessAdapter(version="2.0.0"),
    )
    monkeypatch.setattr(
        cli_module,
        "sync_vendor",
        lambda config, project_root: VendorDigest(config=config, installed_version="2.0.0"),
    )

    result = runner.invoke(app, ["check", "--fix"])

    assert result.exit_code == 0, result.output
    assert "fixed" in result.output


def test_check_fix_isolates_one_vendor_adapter_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "a"\necosystem = "python"\ndepth = "surface"\n\n'
        '[[vendor]]\nname = "b"\necosystem = "python"\ndepth = "surface"\n',
        encoding="utf-8",
    )
    for name in ("a", "b"):
        vendor_dir = tmp_path / "vendor" / name
        vendor_dir.mkdir(parents=True)
        (vendor_dir / "CLAUDE.md").write_text(
            f"# {name}\n\n## Metadata\n\n- **Installed version:** 1.0.0\n", encoding="utf-8"
        )

    monkeypatch.setattr(
        "depcompass.staleness.get_adapter",
        lambda config, project_root: _FakeStalenessAdapter(version="2.0.0"),
    )
    fixed: list[str] = []

    def _fake_sync_vendor(config, project_root):  # noqa: ANN001
        if config.name == "a":
            raise cli_module.AdapterError("a is broken")
        fixed.append(config.name)
        return VendorDigest(config=config, installed_version="2.0.0")

    monkeypatch.setattr(cli_module, "sync_vendor", _fake_sync_vendor)

    result = runner.invoke(app, ["check", "--fix"])

    assert result.exit_code == 1
    assert fixed == ["b"]
    assert "fix failed" in result.output


class _FakeStalenessAdapter:
    def __init__(self, *, version: str, error: Exception | None = None) -> None:
        self._version = version
        self._error = error

    def installed_version(self) -> str:
        if self._error is not None:
            raise self._error
        return self._version

    def dependency_tree(self):  # noqa: ANN201
        from depcompass.core import DepNode

        return DepNode(name="demo", version=self._version)


def test_chat_command_is_still_a_stub() -> None:
    result = runner.invoke(app, ["chat"])
    assert result.exit_code == 1
    assert "not yet implemented" in result.output
