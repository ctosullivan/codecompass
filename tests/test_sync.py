import shutil
from pathlib import Path

import pytest

import depcompass.sync as sync_module
from depcompass.core import DepNode, Depth, Ecosystem, VendorConfig
from depcompass.grounded_description import GroundedDescription, GroundedDescriptionError
from depcompass.source_resolution import SourceResolutionError
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


def _fake_clone(fake_repo: Path):
    def _resolve_and_clone(adapter, dest: Path) -> Path:
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(fake_repo, dest)
        return dest

    return _resolve_and_clone


def _build_fake_repo(root: Path) -> Path:
    fake_repo = root / "fake_repo"
    fake_repo.mkdir()
    (fake_repo / "README.md").write_text("This is the readme.", encoding="utf-8")
    return fake_repo


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


def test_sync_vendor_full_depth_clones_repo_into_src(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    fake_repo = _build_fake_repo(tmp_path)
    monkeypatch.setattr(sync_module, "resolve_and_clone", _fake_clone(fake_repo))
    monkeypatch.setattr(
        sync_module,
        "generate_grounded_description",
        lambda *a, **k: GroundedDescription(technical="desc", conversational_overview="friendly"),
    )
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON, depth=Depth.FULL)

    digest = sync_vendor(config, tmp_path)

    snapshot = tmp_path / "vendor" / "demo" / "src"
    assert (snapshot / "README.md").exists()
    assert digest.technical_description == "desc"
    assert digest.conversational_overview == "friendly"
    assert digest.description_error is None


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
    fake_repo = _build_fake_repo(tmp_path)
    monkeypatch.setattr(sync_module, "resolve_and_clone", _fake_clone(fake_repo))
    monkeypatch.setattr(
        sync_module,
        "generate_grounded_description",
        lambda *a, **k: GroundedDescription(technical="d", conversational_overview="o"),
    )
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON, depth=Depth.FULL)

    sync_vendor(config, tmp_path)
    sync_vendor(config, tmp_path)  # should not raise

    assert (tmp_path / "vendor" / "demo" / "src" / "README.md").exists()


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


def test_sync_vendor_full_depth_writes_overview(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    fake_repo = _build_fake_repo(tmp_path)
    monkeypatch.setattr(sync_module, "resolve_and_clone", _fake_clone(fake_repo))
    monkeypatch.setattr(
        sync_module,
        "generate_grounded_description",
        lambda *a, **k: GroundedDescription(
            technical="gap found in X",
            conversational_overview="This is a friendly overview.",
            action_pointer_file="__init__.py",
            action_pointer_note="fix here",
        ),
    )
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON, depth=Depth.FULL)

    digest = sync_vendor(config, tmp_path)

    assert digest.technical_description == "gap found in X"
    assert digest.conversational_overview == "This is a friendly overview."
    assert digest.description_error is None
    vendor_dir = tmp_path / "vendor" / "demo"
    assert (vendor_dir / "OVERVIEW.md").read_text(encoding="utf-8") == (
        "This is a friendly overview."
    )
    filetree_md = (vendor_dir / "FILETREE.md").read_text(encoding="utf-8")
    assert "← ACTION TARGET: fix here" in filetree_md


def test_sync_vendor_source_resolution_failure_falls_back_to_local_snapshot(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)

    def _raise(*args: object, **kwargs: object) -> None:
        raise SourceResolutionError("no repository found")

    monkeypatch.setattr(sync_module, "resolve_and_clone", _raise)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON, depth=Depth.FULL)

    digest = sync_vendor(config, tmp_path)  # should not raise

    snapshot = tmp_path / "vendor" / "demo" / "src"
    assert (snapshot / "tests" / "test_thing.py").exists()  # kept, unlike FILETREE.md
    assert not (snapshot / "dist").exists()  # stripped, same as FILETREE.md
    assert (snapshot / "__init__.py").exists()
    assert digest.description_error == "no repository found"
    assert digest.technical_description is None
    vendor_dir = tmp_path / "vendor" / "demo"
    for filename in ("FILETREE.md", "DEPTREE.md", "filetree.json", "deptree.json", "CLAUDE.md"):
        assert (vendor_dir / filename).exists(), filename
    assert not (vendor_dir / "OVERVIEW.md").exists()


def test_sync_vendor_description_generation_failure_keeps_cloned_snapshot(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Cloning succeeded — the AI call failing afterward shouldn't throw
    away real, already-retrieved source in favor of a stale local-install
    copy.
    """
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    fake_repo = _build_fake_repo(tmp_path)
    monkeypatch.setattr(sync_module, "resolve_and_clone", _fake_clone(fake_repo))

    def _raise(*args: object, **kwargs: object) -> None:
        raise GroundedDescriptionError("simulated failure")

    monkeypatch.setattr(sync_module, "generate_grounded_description", _raise)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON, depth=Depth.FULL)

    digest = sync_vendor(config, tmp_path)  # should not raise

    assert digest.description_error == "simulated failure"
    assert digest.technical_description is None
    snapshot = tmp_path / "vendor" / "demo" / "src"
    assert (snapshot / "README.md").exists()  # real clone kept, not discarded
    assert not (tmp_path / "vendor" / "demo" / "OVERVIEW.md").exists()


def test_sync_vendor_surface_depth_never_calls_source_resolution(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)

    def _fail_if_called(*args: object, **kwargs: object) -> None:
        raise AssertionError("should not be called for depth=surface")

    monkeypatch.setattr(sync_module, "resolve_and_clone", _fail_if_called)
    monkeypatch.setattr(sync_module, "generate_grounded_description", _fail_if_called)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON, depth=Depth.SURFACE)

    digest = sync_vendor(config, tmp_path)  # should not raise

    assert digest.technical_description is None


def test_sync_all_budget_too_low_raises_before_any_vendor_is_touched(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    configs = [VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON, depth=Depth.FULL)]

    with pytest.raises(GroundedDescriptionError, match="exceeds --budget"):
        sync_all(configs, tmp_path, budget=0.0)

    assert not (tmp_path / "vendor").exists()


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
