from pathlib import Path

import pytest

import depcompass.sync as sync_module
from depcompass.core import DepNode, Depth, Ecosystem, VendorConfig
from depcompass.sync import sync_all, sync_vendor


class _FakeAdapter:
    def __init__(
        self,
        config: VendorConfig,
        project_root: Path,
        *,
        version: str = "1.0.0",
        api_surface: str = "some_fn: does a thing.",
        tree: DepNode | None = None,
        source_dir: Path | None = None,
    ) -> None:
        self.config = config
        self.project_root = project_root
        self._version = version
        self._api_surface = api_surface
        self._tree = tree or DepNode(name=config.name, version=version)
        self._source_dir = source_dir or project_root

    def installed_version(self) -> str:
        return self._version

    def source_location(self) -> Path:
        return self._source_dir

    def readme_and_api_surface(self) -> str:
        return self._api_surface

    def dependency_tree(self) -> DepNode:
        return self._tree


def _build_source_tree(root: Path) -> Path:
    src = root / "pkgsrc"
    (src).mkdir()
    (src / "__init__.py").write_text(
        '"""Entry point for the demo package."""\n\ndef main() -> None:\n    pass\n',
        encoding="utf-8",
    )
    (src / "tests").mkdir()
    (src / "tests" / "test_thing.py").write_text("def test_thing(): ...\n", encoding="utf-8")
    (src / "dist").mkdir()
    (src / "dist" / "bundle.js").write_text("built\n", encoding="utf-8")
    return src


def _patch_adapter(monkeypatch: pytest.MonkeyPatch, **adapter_kwargs: object) -> None:
    monkeypatch.setattr(
        sync_module,
        "get_adapter",
        lambda config, project_root: _FakeAdapter(config, project_root, **adapter_kwargs),
    )


def test_sync_vendor_writes_all_five_output_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, version="2.0.0", source_dir=src)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON, depth=Depth.SURFACE)

    digest = sync_vendor(config, tmp_path)

    vendor_dir = tmp_path / "vendor" / "demo"
    for filename in ("FILETREE.md", "DEPTREE.md", "filetree.json", "deptree.json", "CLAUDE.md"):
        assert (vendor_dir / filename).exists(), filename

    assert digest.installed_version == "2.0.0"
    claude_md = (vendor_dir / "CLAUDE.md").read_text(encoding="utf-8")
    assert "- **Installed version:** 2.0.0" in claude_md.splitlines()


def test_sync_vendor_omits_test_dirs_from_filetree(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON, depth=Depth.SURFACE)

    sync_vendor(config, tmp_path)

    filetree_md = (tmp_path / "vendor" / "demo" / "FILETREE.md").read_text(encoding="utf-8")
    assert "test_thing.py" not in filetree_md
    assert "bundle.js" not in filetree_md
    assert "__init__.py" in filetree_md


def test_sync_vendor_depth_full_copies_looser_pruned_snapshot(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    config = VendorConfig(
        name="demo", ecosystem=Ecosystem.PYTHON, depth=Depth.FULL, context_path="README.md"
    )

    sync_vendor(config, tmp_path)

    snapshot = tmp_path / "vendor" / "demo" / "src"
    assert (snapshot / "tests" / "test_thing.py").exists()  # kept, unlike FILETREE.md
    assert not (snapshot / "dist").exists()  # stripped, same as FILETREE.md
    assert (snapshot / "__init__.py").exists()


def test_sync_vendor_depth_surface_does_not_copy_snapshot(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON, depth=Depth.SURFACE)

    sync_vendor(config, tmp_path)

    assert not (tmp_path / "vendor" / "demo" / "src").exists()


def test_sync_vendor_is_idempotent_on_repeat_runs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    config = VendorConfig(
        name="demo", ecosystem=Ecosystem.PYTHON, depth=Depth.FULL, context_path="README.md"
    )

    sync_vendor(config, tmp_path)
    sync_vendor(config, tmp_path)  # should not raise

    assert (tmp_path / "vendor" / "demo" / "src" / "__init__.py").exists()


def test_sync_vendor_known_gotchas_from_dependency_tree_side_effects(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    tree = DepNode(name="demo", version="1.0.0", side_effects=["postinstall: node build.js"])
    _patch_adapter(monkeypatch, source_dir=src, tree=tree)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON, depth=Depth.SURFACE)

    digest = sync_vendor(config, tmp_path)

    assert digest.side_effects == ["postinstall: node build.js"]
    claude_md = (tmp_path / "vendor" / "demo" / "CLAUDE.md").read_text(encoding="utf-8")
    assert "- postinstall: node build.js" in claude_md.splitlines()


def test_sync_all_syncs_every_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    configs = [
        VendorConfig(name="a", ecosystem=Ecosystem.PYTHON, depth=Depth.SURFACE),
        VendorConfig(name="b", ecosystem=Ecosystem.PYTHON, depth=Depth.SURFACE),
    ]

    digests = sync_all(configs, tmp_path)

    assert [d.config.name for d in digests] == ["a", "b"]
    assert (tmp_path / "vendor" / "a" / "CLAUDE.md").exists()
    assert (tmp_path / "vendor" / "b" / "CLAUDE.md").exists()
