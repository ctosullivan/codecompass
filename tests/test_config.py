from pathlib import Path

import pytest

from codecompass.config import ConfigError, load_vendor_config
from codecompass.core import Depth, Ecosystem

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_valid_vendor_config() -> None:
    vendors = load_vendor_config(FIXTURES / "vendor.toml")
    assert [v.name for v in vendors] == ["turndown", "lodash", "requests", "serde"]

    turndown = vendors[0]
    assert turndown.ecosystem is Ecosystem.NPM
    assert turndown.depth is Depth.FULL

    lodash = vendors[1]
    assert lodash.depth is Depth.SURFACE

    assert vendors[2].ecosystem is Ecosystem.PYTHON
    assert vendors[3].ecosystem is Ecosystem.CARGO


def test_missing_file_raises_config_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="could not read"):
        load_vendor_config(tmp_path / "does-not-exist.toml")


def test_malformed_toml_raises_config_error(tmp_path: Path) -> None:
    path = tmp_path / "vendor.toml"
    path.write_text("this is not [ valid toml", encoding="utf-8")
    with pytest.raises(ConfigError, match="not valid TOML"):
        load_vendor_config(path)


def test_missing_required_field_raises_config_error(tmp_path: Path) -> None:
    path = tmp_path / "vendor.toml"
    path.write_text(
        '[[vendor]]\necosystem = "npm"\ndepth = "surface"\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="missing required field 'name'"):
        load_vendor_config(path)


def test_invalid_ecosystem_raises_config_error(tmp_path: Path) -> None:
    path = tmp_path / "vendor.toml"
    path.write_text(
        '[[vendor]]\nname = "bad"\necosystem = "deno"\ndepth = "surface"\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="invalid ecosystem 'deno'"):
        load_vendor_config(path)


def test_invalid_depth_raises_config_error(tmp_path: Path) -> None:
    path = tmp_path / "vendor.toml"
    path.write_text(
        '[[vendor]]\nname = "bad"\necosystem = "npm"\ndepth = "deep"\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="invalid depth 'deep'"):
        load_vendor_config(path)


def test_full_depth_without_context_path_no_longer_errors(tmp_path: Path) -> None:
    """`context_path` was removed in Phase 7 (decisions/0019) — `depth =
    full` no longer requires any companion field.
    """
    path = tmp_path / "vendor.toml"
    path.write_text(
        '[[vendor]]\nname = "ok"\necosystem = "npm"\ndepth = "full"\n',
        encoding="utf-8",
    )
    vendors = load_vendor_config(path)
    assert vendors[0].depth is Depth.FULL


def test_fails_fast_on_first_invalid_entry(tmp_path: Path) -> None:
    """Two invalid vendors: only the first one's problem should be reported."""
    path = tmp_path / "vendor.toml"
    path.write_text(
        '[[vendor]]\necosystem = "npm"\ndepth = "surface"\n'
        '\n'
        '[[vendor]]\nname = "second"\necosystem = "bogus"\ndepth = "surface"\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="missing required field 'name'"):
        load_vendor_config(path)
