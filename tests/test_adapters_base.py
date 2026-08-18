import shutil
import subprocess
from pathlib import Path

import pytest

from codecompass.adapters.base import AdapterError, EcosystemAdapter, _run_json
from codecompass.core import Depth, Ecosystem, VendorConfig


class _FakeCompletedProcess:
    def __init__(self, returncode: int, stdout: str, stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _pretend_tool_is_on_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """_run_json resolves cmd[0] via shutil.which before invoking it —
    tests that fake subprocess.run must also fake a successful resolve,
    or _run_json short-circuits to the "not found" branch first."""
    monkeypatch.setattr(shutil, "which", lambda name: f"/fake/path/to/{name}")


def test_run_json_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _pretend_tool_is_on_path(monkeypatch)

    def fake_run(cmd, **kwargs):
        return _FakeCompletedProcess(0, '{"ok": true}')

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert _run_json(["some-tool"], cwd=tmp_path) == {"ok": True}


def test_run_json_missing_tool_raises_adapter_error(tmp_path: Path) -> None:
    with pytest.raises(AdapterError, match="not found"):
        _run_json(["definitely-not-a-real-command-xyz"], cwd=tmp_path)


def test_run_json_non_zero_exit_raises_adapter_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _pretend_tool_is_on_path(monkeypatch)

    def fake_run(cmd, **kwargs):
        return _FakeCompletedProcess(1, "", "something went wrong")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(AdapterError, match="something went wrong"):
        _run_json(["some-tool"], cwd=tmp_path)


def test_run_json_invalid_json_raises_adapter_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _pretend_tool_is_on_path(monkeypatch)

    def fake_run(cmd, **kwargs):
        return _FakeCompletedProcess(0, "not json")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(AdapterError, match="invalid JSON"):
        _run_json(["some-tool"], cwd=tmp_path)


def test_ecosystem_adapter_rejects_incomplete_subclass() -> None:
    class Incomplete(EcosystemAdapter):
        def installed_version(self) -> str:
            return "1.0.0"

    config = VendorConfig(name="x", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    with pytest.raises(TypeError):
        Incomplete(config, Path("."))  # type: ignore[abstract]
