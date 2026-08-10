import json
from pathlib import Path

import pytest

from depcompass.config import load_vendor_config
from depcompass.core import Ecosystem
from depcompass.discovery import (
    DiscoveryError,
    discover_all,
    discover_cargo,
    discover_npm,
    discover_python,
    write_vendor_toml,
)


def test_discover_npm_reads_dependencies_and_dev_dependencies(tmp_path: Path) -> None:
    manifest = tmp_path / "package.json"
    manifest.write_text(
        json.dumps({"dependencies": {"lodash": "^4.0.0"}, "devDependencies": {"jest": "^29.0.0"}}),
        encoding="utf-8",
    )
    assert discover_npm(manifest) == ["jest", "lodash"]


def test_discover_npm_malformed_json_raises_discovery_error(tmp_path: Path) -> None:
    manifest = tmp_path / "package.json"
    manifest.write_text("not json", encoding="utf-8")
    with pytest.raises(DiscoveryError, match="could not read as JSON"):
        discover_npm(manifest)


def test_discover_python_strips_version_specifiers_and_extras(tmp_path: Path) -> None:
    manifest = tmp_path / "pyproject.toml"
    manifest.write_text(
        '[project]\ndependencies = ["requests>=2.0", "click[extra]==8.0", "rich"]\n',
        encoding="utf-8",
    )
    assert discover_python(manifest) == ["click", "requests", "rich"]


def test_discover_python_no_dependencies_table_returns_empty(tmp_path: Path) -> None:
    manifest = tmp_path / "pyproject.toml"
    manifest.write_text('[project]\nname = "demo"\n', encoding="utf-8")
    assert discover_python(manifest) == []


def test_discover_cargo_reads_dependencies_and_dev_dependencies(tmp_path: Path) -> None:
    manifest = tmp_path / "Cargo.toml"
    manifest.write_text(
        '[dependencies]\nserde = "1.0"\n\n[dev-dependencies]\nserde_test = "1.0"\n',
        encoding="utf-8",
    )
    assert discover_cargo(manifest) == ["serde", "serde_test"]


def test_discover_all_dispatches_by_manifest_filename(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"lodash": "^4.0.0"}}), encoding="utf-8"
    )
    (tmp_path / "pyproject.toml").write_text(
        '[project]\ndependencies = ["requests"]\n', encoding="utf-8"
    )
    (tmp_path / "Cargo.toml").write_text('[dependencies]\nserde = "1.0"\n', encoding="utf-8")

    result = discover_all(
        [tmp_path / "package.json", tmp_path / "pyproject.toml", tmp_path / "Cargo.toml"]
    )

    assert result == {
        Ecosystem.NPM: ["lodash"],
        Ecosystem.PYTHON: ["requests"],
        Ecosystem.CARGO: ["serde"],
    }


def test_discover_all_rejects_unrecognized_manifest_filename(tmp_path: Path) -> None:
    manifest = tmp_path / "requirements.txt"
    manifest.write_text("requests\n", encoding="utf-8")
    with pytest.raises(DiscoveryError, match="unrecognized manifest filename"):
        discover_all([manifest])


def test_write_vendor_toml_produces_parseable_config(tmp_path: Path) -> None:
    target = tmp_path / "vendor.toml"
    write_vendor_toml({Ecosystem.NPM: ["lodash"], Ecosystem.PYTHON: ["requests"]}, target)

    vendors = load_vendor_config(target)
    assert {v.name for v in vendors} == {"lodash", "requests"}
    assert all(v.depth.value == "surface" for v in vendors)
    assert all(v.context_path is None for v in vendors)


def test_write_vendor_toml_errors_if_target_already_exists(tmp_path: Path) -> None:
    target = tmp_path / "vendor.toml"
    target.write_text("# hand-edited\n", encoding="utf-8")

    with pytest.raises(DiscoveryError, match="already exists"):
        write_vendor_toml({Ecosystem.NPM: ["lodash"]}, target)

    assert target.read_text(encoding="utf-8") == "# hand-edited\n"
