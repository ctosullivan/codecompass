import json
from pathlib import Path

import pytest

import depcompass.staleness as staleness_module
from depcompass.adapters import AdapterError
from depcompass.core import DepNode, Depth, Ecosystem, VendorConfig
from depcompass.deptree import render_deptree_json
from depcompass.staleness import (
    Severity,
    VendorStaleness,
    check_all,
    check_vendor,
    classify,
)

# --- _parse_version / classify -------------------------------------------------


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        ("1.2.3", (1, 2, 3)),
        ("v1.2.3", (1, 2, 3)),
        ("1.2.3-beta.1", (1, 2, 3)),
        ("1.2.3+build.5", (1, 2, 3)),
        ("not-a-version", None),
        ("1.2", None),
    ],
)
def test_parse_version(version: str, expected: tuple[int, int, int] | None) -> None:
    assert staleness_module._parse_version(version) == expected


def test_classify_none_when_identical() -> None:
    assert classify("1.2.3", "1.2.3") == Severity.NONE


def test_classify_none_when_numeric_triple_matches_despite_string_diff() -> None:
    assert classify("1.2.3+build.1", "1.2.3+build.2") == Severity.NONE


def test_classify_patch() -> None:
    assert classify("1.2.3", "1.2.4") == Severity.PATCH


def test_classify_minor() -> None:
    assert classify("1.2.3", "1.3.0") == Severity.MINOR


def test_classify_major() -> None:
    assert classify("1.2.3", "2.0.0") == Severity.MAJOR


def test_classify_unknown_when_either_side_unparseable() -> None:
    assert classify("1.2.3", "not-a-version") == Severity.UNKNOWN
    assert classify("not-a-version", "1.2.3") == Severity.UNKNOWN


# --- check_vendor / check_all ---------------------------------------------------


class _FakeAdapter:
    def __init__(
        self,
        config: VendorConfig,
        project_root: Path,
        *,
        version: str = "1.0.0",
        tree: DepNode | None = None,
        error: AdapterError | None = None,
    ) -> None:
        self.config = config
        self.project_root = project_root
        self._version = version
        self._tree = tree or DepNode(name=config.name, version=version)
        self._error = error

    def installed_version(self) -> str:
        if self._error is not None:
            raise self._error
        return self._version

    def dependency_tree(self) -> DepNode:
        return self._tree


def _patch_adapter(monkeypatch: pytest.MonkeyPatch, **adapter_kwargs: object) -> None:
    monkeypatch.setattr(
        staleness_module,
        "get_adapter",
        lambda config, project_root: _FakeAdapter(config, project_root, **adapter_kwargs),
    )


def _write_synced_vendor(
    project_root: Path, name: str, recorded_version: str, tree: DepNode | None = None
) -> None:
    vendor_dir = project_root / "vendor" / name
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "CLAUDE.md").write_text(
        f"# {name}\n\n## Metadata\n\n- **Installed version:** {recorded_version}\n",
        encoding="utf-8",
    )
    root = tree or DepNode(name=name, version=recorded_version)
    (vendor_dir / "deptree.json").write_text(
        json.dumps(render_deptree_json(root)), encoding="utf-8"
    )


def _config(name: str = "demo") -> VendorConfig:
    return VendorConfig(name=name, ecosystem=Ecosystem.PYTHON, depth=Depth.SURFACE)


def test_check_vendor_never_synced(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_adapter(monkeypatch, version="1.0.0")
    config = _config()

    result = check_vendor(config, tmp_path)

    assert result == VendorStaleness(
        config=config,
        recorded_version=None,
        live_version="1.0.0",
        severity=Severity.NONE,
        transitive_drift=False,
        error=None,
    )


def test_check_vendor_patch_delta(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_synced_vendor(tmp_path, "demo", "1.0.0")
    _patch_adapter(monkeypatch, version="1.0.1")
    config = _config()

    result = check_vendor(config, tmp_path)

    assert result.severity == Severity.PATCH
    assert result.recorded_version == "1.0.0"
    assert result.live_version == "1.0.1"


def test_check_vendor_minor_delta(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_synced_vendor(tmp_path, "demo", "1.0.0")
    _patch_adapter(monkeypatch, version="1.1.0")
    config = _config()

    result = check_vendor(config, tmp_path)

    assert result.severity == Severity.MINOR


def test_check_vendor_major_delta(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_synced_vendor(tmp_path, "demo", "1.0.0")
    _patch_adapter(monkeypatch, version="2.0.0")
    config = _config()

    result = check_vendor(config, tmp_path)

    assert result.severity == Severity.MAJOR


def test_check_vendor_transitive_drift_when_root_unchanged(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    persisted_tree = DepNode(
        name="demo", version="1.0.0", children=[DepNode(name="child", version="1.0.0")]
    )
    _write_synced_vendor(tmp_path, "demo", "1.0.0", tree=persisted_tree)
    live_tree = DepNode(
        name="demo", version="1.0.0", children=[DepNode(name="child", version="2.0.0")]
    )
    _patch_adapter(monkeypatch, version="1.0.0", tree=live_tree)
    config = _config()

    result = check_vendor(config, tmp_path)

    assert result.severity == Severity.NONE
    assert result.transitive_drift is True


def test_check_vendor_no_transitive_drift_when_trees_match(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    tree = DepNode(
        name="demo", version="1.0.0", children=[DepNode(name="child", version="1.0.0")]
    )
    _write_synced_vendor(tmp_path, "demo", "1.0.0", tree=tree)
    _patch_adapter(monkeypatch, version="1.0.0", tree=tree)
    config = _config()

    result = check_vendor(config, tmp_path)

    assert result.transitive_drift is False


def test_check_vendor_no_transitive_drift_check_when_root_changed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    persisted_tree = DepNode(
        name="demo", version="1.0.0", children=[DepNode(name="child", version="1.0.0")]
    )
    _write_synced_vendor(tmp_path, "demo", "1.0.0", tree=persisted_tree)
    live_tree = DepNode(
        name="demo", version="2.0.0", children=[DepNode(name="child", version="2.0.0")]
    )
    _patch_adapter(monkeypatch, version="2.0.0", tree=live_tree)
    config = _config()

    result = check_vendor(config, tmp_path)

    assert result.severity == Severity.MAJOR
    assert result.transitive_drift is False


def test_check_vendor_adapter_error_is_isolated(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _write_synced_vendor(tmp_path, "demo", "1.0.0")
    _patch_adapter(monkeypatch, error=AdapterError("not installed"))
    config = _config()

    result = check_vendor(config, tmp_path)  # should not raise

    assert result.error == "not installed"
    assert result.live_version is None


def test_check_all_checks_every_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_adapter(monkeypatch, version="1.0.0")
    configs = [_config("a"), _config("b")]

    results = check_all(configs, tmp_path)

    assert [r.config.name for r in results] == ["a", "b"]
