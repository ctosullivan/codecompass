import importlib.metadata
import json
from pathlib import Path

import pytest

import depcompass.adapters.python as python_module
from depcompass.adapters.base import AdapterError
from depcompass.adapters.python import PythonAdapter
from depcompass.core import Depth, Ecosystem, RepositoryLocation, VendorConfig

FIXTURES = Path(__file__).parent / "fixtures"


def _adapter(name: str, project_root: Path) -> PythonAdapter:
    config = VendorConfig(name=name, ecosystem=Ecosystem.PYTHON, depth=Depth.SURFACE)
    return PythonAdapter(config, project_root=project_root)


def test_installed_version_matches_importlib_metadata(tmp_path: Path) -> None:
    adapter = _adapter("pytest", tmp_path)
    assert adapter.installed_version() == importlib.metadata.version("pytest")


def test_source_location_resolves_to_real_directory(tmp_path: Path) -> None:
    adapter = _adapter("pytest", tmp_path)
    assert adapter.source_location().is_dir()


class _FakeMetadata:
    def __init__(self, project_urls: list[str]) -> None:
        self._project_urls = project_urls

    def get_all(self, key: str) -> list[str] | None:
        return self._project_urls if key == "Project-URL" else None


def test_repository_url_prefers_source_label(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = _FakeMetadata(
        ["Homepage, https://example.com", "Source, https://github.com/psf/requests"]
    )
    monkeypatch.setattr(python_module.importlib.metadata, "metadata", lambda name: fake)
    adapter = _adapter("requests", tmp_path)

    assert adapter.repository_url() == RepositoryLocation(
        url="https://github.com/psf/requests", subdirectory=None
    )


def test_repository_url_falls_back_to_homepage_when_no_better_label(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = _FakeMetadata(["Homepage, https://github.com/psf/requests"])
    monkeypatch.setattr(python_module.importlib.metadata, "metadata", lambda name: fake)
    adapter = _adapter("requests", tmp_path)

    assert adapter.repository_url() == RepositoryLocation(
        url="https://github.com/psf/requests", subdirectory=None
    )


def test_repository_url_none_when_no_project_urls(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        python_module.importlib.metadata, "metadata", lambda name: _FakeMetadata([])
    )
    adapter = _adapter("some-pkg", tmp_path)

    assert adapter.repository_url() is None


def test_repository_url_none_when_no_recognized_label(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = _FakeMetadata(["Funding, https://example.com/sponsor"])
    monkeypatch.setattr(python_module.importlib.metadata, "metadata", lambda name: fake)
    adapter = _adapter("some-pkg", tmp_path)

    assert adapter.repository_url() is None


def test_missing_package_raises_adapter_error(tmp_path: Path) -> None:
    adapter = _adapter("definitely-not-a-real-package-xyz", tmp_path)
    with pytest.raises(AdapterError, match="not installed"):
        adapter.installed_version()


def test_dependency_tree_fixture(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = json.loads((FIXTURES / "pipdeptree_json_tree.json").read_text(encoding="utf-8"))
    monkeypatch.setattr(python_module, "_run_json", lambda cmd, cwd: data)

    adapter = _adapter("pytest", tmp_path)
    tree = adapter.dependency_tree()

    assert tree.name == "pytest"
    assert tree.version == "8.0.0"
    assert {c.name for c in tree.children} == {"pluggy", "iniconfig"}


def test_dev_only_always_false(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = json.loads((FIXTURES / "pipdeptree_json_tree.json").read_text(encoding="utf-8"))
    monkeypatch.setattr(python_module, "_run_json", lambda cmd, cwd: data)

    adapter = _adapter("pytest", tmp_path)
    tree = adapter.dependency_tree()

    assert tree.dev_only is False
    assert all(child.dev_only is False for child in tree.children)


def test_pyi_preferred_over_ast(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "sample.pyi").write_text(
        (FIXTURES / "sample.pyi").read_text(encoding="utf-8"), encoding="utf-8"
    )
    adapter = _adapter("some-pkg", tmp_path)
    monkeypatch.setattr(adapter, "source_location", lambda: tmp_path)

    surface = adapter.readme_and_api_surface()
    assert "def greet(name: str) -> str: ..." in surface


def test_ast_fallback_when_no_pyi(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "__init__.py").write_text(
        (FIXTURES / "sample_module_with_all.py").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    adapter = _adapter("some-pkg", tmp_path)
    monkeypatch.setattr(adapter, "source_location", lambda: tmp_path)

    surface = adapter.readme_and_api_surface()
    assert "__all__ = greet, Greeter" in surface
    assert "greet: Return a friendly greeting." in surface
    assert "Greeter: Greets people repeatedly." in surface


def test_live_smoke_pytest_self(tmp_path: Path) -> None:
    """Always runnable — pytest is already an installed dependency, no
    skipif needed."""
    adapter = _adapter("pytest", Path.cwd())
    tree = adapter.dependency_tree()

    assert tree.name == "pytest"
    assert len(tree.children) > 0
