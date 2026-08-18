from pathlib import Path

import pytest

import codecompass.source_resolution as source_resolution_module
from codecompass.core import Depth, Ecosystem, RepositoryLocation, VendorConfig
from codecompass.source_resolution import SourceResolutionError, resolve_and_clone


class _FakeAdapter:
    def __init__(self, config: VendorConfig, location: RepositoryLocation | None) -> None:
        self.config = config
        self._location = location

    def repository_url(self) -> RepositoryLocation | None:
        return self._location


def _config(name: str = "turndown") -> VendorConfig:
    return VendorConfig(name=name, ecosystem=Ecosystem.NPM, depth=Depth.FULL)


def _fake_clone_writes_marker(marker_name: str = "cloned.txt"):
    def _git_clone(url: str, dest: Path) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / marker_name).write_text(url, encoding="utf-8")

    return _git_clone


def test_resolve_and_clone_returns_dest_when_no_subdirectory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(source_resolution_module, "_git_clone", _fake_clone_writes_marker())
    adapter = _FakeAdapter(_config(), RepositoryLocation(url="https://example.com/repo.git"))
    dest = tmp_path / "src"

    result = resolve_and_clone(adapter, dest)

    assert result == dest
    assert (dest / "cloned.txt").read_text(encoding="utf-8") == "https://example.com/repo.git"


def test_resolve_and_clone_scopes_to_subdirectory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def _git_clone(url: str, dest: Path) -> None:
        (dest / "packages" / "foo").mkdir(parents=True)

    monkeypatch.setattr(source_resolution_module, "_git_clone", _git_clone)
    adapter = _FakeAdapter(
        _config(),
        RepositoryLocation(url="https://example.com/repo.git", subdirectory="packages/foo"),
    )
    dest = tmp_path / "src"

    result = resolve_and_clone(adapter, dest)

    assert result == dest / "packages" / "foo"


def test_resolve_and_clone_missing_subdirectory_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(source_resolution_module, "_git_clone", _fake_clone_writes_marker())
    adapter = _FakeAdapter(
        _config(),
        RepositoryLocation(url="https://example.com/repo.git", subdirectory="does/not/exist"),
    )

    with pytest.raises(SourceResolutionError, match="does/not/exist"):
        resolve_and_clone(adapter, tmp_path / "src")


def test_resolve_and_clone_no_repository_raises(tmp_path: Path) -> None:
    adapter = _FakeAdapter(_config(), None)

    with pytest.raises(SourceResolutionError, match="no repository URL found"):
        resolve_and_clone(adapter, tmp_path / "src")


def test_git_clone_missing_git_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(source_resolution_module.shutil, "which", lambda tool: None)

    with pytest.raises(SourceResolutionError, match="required tool not found: 'git'"):
        source_resolution_module._git_clone("https://example.com/repo.git", tmp_path / "src")


def test_git_clone_nonzero_exit_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class _FakeResult:
        returncode = 1
        stderr = "fatal: repository not found"

    monkeypatch.setattr(source_resolution_module.shutil, "which", lambda tool: "/usr/bin/git")
    monkeypatch.setattr(
        source_resolution_module.subprocess, "run", lambda *a, **k: _FakeResult()
    )

    with pytest.raises(SourceResolutionError, match="repository not found"):
        source_resolution_module._git_clone("https://example.com/repo.git", tmp_path / "src")


def test_git_clone_removes_existing_dest_first(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    dest = tmp_path / "src"
    dest.mkdir()
    (dest / "stale.txt").write_text("old", encoding="utf-8")

    class _FakeResult:
        returncode = 0
        stderr = ""

    def _fake_run(cmd, **kwargs):  # noqa: ANN001
        Path(cmd[-1]).mkdir(parents=True, exist_ok=True)
        return _FakeResult()

    monkeypatch.setattr(source_resolution_module.shutil, "which", lambda tool: "/usr/bin/git")
    monkeypatch.setattr(source_resolution_module.subprocess, "run", _fake_run)

    source_resolution_module._git_clone("https://example.com/repo.git", dest)

    assert not (dest / "stale.txt").exists()
