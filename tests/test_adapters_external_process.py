"""Fixture tests for the generic JSON-Lines external-adapter protocol
client (`decisions/0057`, `decisions/0058`) — run against a small,
hand-written fake adapter process (`tests/fixtures/fake_adapter.py`),
never a mock of this module's own internals, and never requiring the
real Haskell toolchain or the `adapters/haskell/` submodule to be
checked out. See planning/phase-60-minimal-haskell-adapter.md §7.
"""

import sys
from pathlib import Path

import pytest

from codecompass.adapters.base import AdapterError
from codecompass.adapters.external_process import ExternalAdapterProcess

FAKE_ADAPTER = Path(__file__).parent / "fixtures" / "fake_adapter.py"


def _process(mode: str, monkeypatch: pytest.MonkeyPatch) -> ExternalAdapterProcess:
    monkeypatch.setenv("FAKE_ADAPTER_MODE", mode)
    return ExternalAdapterProcess([sys.executable, str(FAKE_ADAPTER)])


def test_initialize_reads_capabilities_and_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    process = _process("normal", monkeypatch)
    process.initialize()
    try:
        assert process.adapter_name == "fake-adapter"
        assert process.adapter_version == "0.1.0"
        assert process.ecosystem == "fake"
        assert process.capabilities == (
            "dependencies",
            "symbols",
            "observations",
            "diagnostics",
        )
    finally:
        process.shutdown()


def test_protocol_version_mismatch_raises_adapter_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = _process("bad_version", monkeypatch)
    with pytest.raises(AdapterError, match="protocol_version mismatch"):
        process.initialize()


def test_analyze_project_returns_raw_neutral_result(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    process = _process("normal", monkeypatch)
    process.initialize()
    try:
        result = process.analyze_project(tmp_path, "demo-package")
        assert result["dependencies"]["name"] == "demo-package"
        assert result["dependencies"]["children"][0]["name"] == "child-dep"
        assert result["symbols"] == [
            {"name": "doThing", "purpose": None, "module": "Demo.Core"}
        ]
        assert result["diagnostics"] == []
    finally:
        process.shutdown()


def test_analyze_project_error_response_raises_adapter_error_with_code(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    process = _process("normal", monkeypatch)
    process.initialize()
    try:
        with pytest.raises(AdapterError, match="not_found"):
            process.analyze_project(tmp_path, "trigger-error")
    finally:
        process.shutdown()


def test_response_id_mismatch_raises_adapter_error(monkeypatch: pytest.MonkeyPatch) -> None:
    process = _process("bad_id", monkeypatch)
    with pytest.raises(AdapterError, match="does not match request id"):
        process.initialize()


def test_response_missing_result_and_error_raises_adapter_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = _process("no_result_no_error", monkeypatch)
    with pytest.raises(AdapterError, match="neither 'result' nor 'error'"):
        process.initialize()


def test_unknown_command_raises_adapter_error(monkeypatch: pytest.MonkeyPatch) -> None:
    process = ExternalAdapterProcess(["/no/such/executable-codecompass-test"])
    with pytest.raises(AdapterError, match="could not start"):
        process.initialize()


def test_shutdown_is_safe_before_initialize() -> None:
    process = ExternalAdapterProcess([sys.executable, str(FAKE_ADAPTER)])
    process.shutdown()  # must not raise
