import json
from pathlib import Path

import pytest

from codecompass.config import load_vendor_config
from codecompass.core import Depth, Ecosystem, VendorConfig
from codecompass.discovery import (
    DiscoveryError,
    append_vendor_toml,
    discover_all,
    discover_cargo,
    discover_manifest_paths,
    discover_npm,
    discover_python,
    discover_requirements_txt,
    render_vendor_block,
    rewrite_vendor_toml,
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


def test_discover_requirements_txt_strips_specifiers_and_skips_comments_and_options(
    tmp_path: Path,
) -> None:
    manifest = tmp_path / "requirements.txt"
    manifest.write_text(
        "requests>=2.0\n"
        "# a comment\n"
        "\n"
        "click[extra]==8.0\n"
        "-r other-requirements.txt\n"
        "-e .\n"
        "rich\n",
        encoding="utf-8",
    )
    assert discover_requirements_txt(manifest) == ["click", "requests", "rich"]


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


def test_discover_all_merges_pyproject_and_requirements_into_one_ecosystem(
    tmp_path: Path,
) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\ndependencies = ["requests"]\n', encoding="utf-8"
    )
    (tmp_path / "requirements.txt").write_text("rich\n", encoding="utf-8")

    result = discover_all([tmp_path / "pyproject.toml", tmp_path / "requirements.txt"])

    assert result == {Ecosystem.PYTHON: ["requests", "rich"]}


def test_discover_all_rejects_unrecognized_manifest_filename(tmp_path: Path) -> None:
    manifest = tmp_path / "Gemfile"
    manifest.write_text("gem 'rails'\n", encoding="utf-8")
    with pytest.raises(DiscoveryError, match="unrecognized manifest filename"):
        discover_all([manifest])


def test_discover_manifest_paths_finds_known_filenames_at_root(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    (tmp_path / "Cargo.toml").write_text("", encoding="utf-8")
    (tmp_path / "unrelated.txt").write_text("", encoding="utf-8")

    found = discover_manifest_paths(tmp_path)

    assert sorted(p.name for p in found) == ["Cargo.toml", "package.json"]


def test_discover_manifest_paths_ignores_nested_manifests(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "package.json").write_text("{}", encoding="utf-8")

    assert discover_manifest_paths(tmp_path) == []


def test_write_vendor_toml_produces_parseable_config(tmp_path: Path) -> None:
    target = tmp_path / "vendor.toml"
    write_vendor_toml({Ecosystem.NPM: ["lodash"], Ecosystem.PYTHON: ["requests"]}, target)

    vendors = load_vendor_config(target)
    assert {v.name for v in vendors} == {"lodash", "requests"}
    assert all(v.depth.value == "surface" for v in vendors)


def test_write_vendor_toml_errors_if_target_already_exists(tmp_path: Path) -> None:
    target = tmp_path / "vendor.toml"
    target.write_text("# hand-edited\n", encoding="utf-8")

    with pytest.raises(DiscoveryError, match="already exists"):
        write_vendor_toml({Ecosystem.NPM: ["lodash"]}, target)

    assert target.read_text(encoding="utf-8") == "# hand-edited\n"


def test_render_vendor_block_produces_parseable_toml_block() -> None:
    config = VendorConfig(name="lodash", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    block = render_vendor_block(config)
    assert 'name = "lodash"' in block
    assert 'ecosystem = "npm"' in block
    assert 'depth = "surface"' in block


def test_append_vendor_toml_extends_existing_file(tmp_path: Path) -> None:
    target = tmp_path / "vendor.toml"
    write_vendor_toml({Ecosystem.NPM: ["lodash"]}, target)

    append_vendor_toml(
        [VendorConfig(name="requests", ecosystem=Ecosystem.PYTHON, depth=Depth.SURFACE)], target
    )

    vendors = load_vendor_config(target)
    assert {v.name for v in vendors} == {"lodash", "requests"}


def test_append_vendor_toml_empty_list_is_noop(tmp_path: Path) -> None:
    target = tmp_path / "vendor.toml"
    write_vendor_toml({Ecosystem.NPM: ["lodash"]}, target)
    original = target.read_text(encoding="utf-8")

    append_vendor_toml([], target)

    assert target.read_text(encoding="utf-8") == original


def test_rewrite_vendor_toml_persists_depth_change(tmp_path: Path) -> None:
    target = tmp_path / "vendor.toml"
    configs = [
        VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE),
        VendorConfig(name="lodash", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE),
    ]
    rewrite_vendor_toml(configs, target)

    promoted = [
        VendorConfig(name=c.name, ecosystem=c.ecosystem, depth=Depth.FULL)
        if c.name == "turndown"
        else c
        for c in configs
    ]
    rewrite_vendor_toml(promoted, target)

    vendors = {v.name: v for v in load_vendor_config(target)}
    assert vendors["turndown"].depth is Depth.FULL
    assert vendors["lodash"].depth is Depth.SURFACE
