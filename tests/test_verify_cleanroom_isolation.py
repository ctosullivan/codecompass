"""Tests for scripts/verify_cleanroom_isolation.py -- a maintainer-only
tool, not part of the codecompass package.

Phase 81B §27 "Amendment 5" (corrective): the Mode B isolation preflight
existed only as investigation prose before this amendment. These tests
confirm the executable preflight itself is real: its pure-logic pieces
are unit tested directly, and a real, adversarially-meaningful end-to-end
run (building and tearing down an actual Linux-namespace sandbox) proves
every one of the eleven named conditions is genuinely, mechanically
checked -- not merely asserted in a report. Skipped automatically where
`unshare`/`pivot_root` aren't available (e.g. a non-Linux CI runner),
per this module's own `_sandbox_tools_available()` check, matching this
project's existing `smoke`-marker precedent for environment-dependent
tests.
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import re
import shutil
import socket
import sys
import threading
import time
from pathlib import Path

import pytest

_SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "verify_cleanroom_isolation.py"
)
_spec = importlib.util.spec_from_file_location("verify_cleanroom_isolation", _SCRIPT_PATH)
verify_cleanroom_isolation = importlib.util.module_from_spec(_spec)
sys.modules["verify_cleanroom_isolation"] = verify_cleanroom_isolation
_spec.loader.exec_module(verify_cleanroom_isolation)


def _sandbox_tools_available() -> bool:
    return all(shutil.which(tool) for tool in ("unshare", "pivot_root", "curl", "bash"))


requires_sandbox_tools = pytest.mark.skipif(
    not _sandbox_tools_available(),
    reason="unshare/pivot_root/curl not available in this environment",
)


# ---------------------------------------------------------------------------
# Pure-logic unit tests (no real sandbox construction).
# ---------------------------------------------------------------------------


def test_check_rejects_an_invalid_status():
    with pytest.raises(AssertionError):
        verify_cleanroom_isolation._check("x", "maybe", "detail")


def test_find_siblings_lists_only_real_git_checkouts(tmp_path):
    root = tmp_path / "codecompass"
    root.mkdir()
    (root / ".git").mkdir()
    sibling_a = tmp_path / "sibling-a"
    (sibling_a / ".git").mkdir(parents=True)
    sibling_b = tmp_path / "sibling-b-not-a-repo"
    sibling_b.mkdir()
    (tmp_path / "a-plain-file.txt").write_text("x\n", encoding="utf-8")

    siblings = verify_cleanroom_isolation._find_siblings(root)
    assert siblings == ["sibling-a"]


def test_fake_broker_unix_protocol_round_trip(tmp_path):
    """The fake stand-in broker's own protocol, exercised directly over a
    real Unix socket -- never real model inference (§27.2's own scope
    limit)."""
    sock_path = tmp_path / "broker.sock"
    srv = verify_cleanroom_isolation._FakeUnixBroker(
        str(sock_path), verify_cleanroom_isolation._FakeBrokerHandler
    )
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        time.sleep(0.1)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(3)
            client.connect(str(sock_path))
            client.sendall(json.dumps({"system_prompt": "x", "messages": []}).encode("utf-8"))
            client.shutdown(socket.SHUT_WR)
            resp = json.loads(client.recv(65536).decode("utf-8"))
        assert resp == {"ok": True, "output": "fake-broker-ack", "usage": {}}
    finally:
        srv.shutdown()


def test_fake_broker_tolerates_malformed_input_without_crashing(tmp_path):
    sock_path = tmp_path / "broker.sock"
    srv = verify_cleanroom_isolation._FakeUnixBroker(
        str(sock_path), verify_cleanroom_isolation._FakeBrokerHandler
    )
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        time.sleep(0.1)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(3)
            client.connect(str(sock_path))
            client.sendall(b"not json at all \xff\xfe")
            client.shutdown(socket.SHUT_WR)
            resp = json.loads(client.recv(65536).decode("utf-8"))
        assert resp["ok"] is True
    finally:
        srv.shutdown()


def test_main_dispatches_to_probe_mode(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "evidence_token": "x",
                "real_root": "/nonexistent",
                "real_root_parent": "/nonexistent",
                "siblings": [],
                "credential_canary": "canary",
                "parent_context_canary": "canary2",
                "broker_socket_path": "/nonexistent.sock",
                "broker_host_tcp_port": 1,
            }
        ),
        encoding="utf-8",
    )
    called = {}

    def _fake_run_probe(config):
        called["config"] = config
        return 0

    monkeypatch.setattr(verify_cleanroom_isolation, "_run_probe", _fake_run_probe)
    rc = verify_cleanroom_isolation.main(["prog", "--probe", str(config_path)])
    assert rc == 0
    assert called["config"]["evidence_token"] == "x"


def test_probe_mode_reports_every_check_even_if_one_raises(monkeypatch, capsys):
    """A probe function raising an exception must be reported as a failed
    check, not crash the whole probe run and silently report nothing
    (would otherwise look identical to a hang/timeout from the outer
    driver's perspective)."""

    def _boom(_config):
        raise RuntimeError("synthetic failure")

    monkeypatch.setattr(verify_cleanroom_isolation, "_PROBE_CHECKS", [_boom])
    rc = verify_cleanroom_isolation._run_probe({})
    assert rc == 0  # the probe process itself always exits 0; failures are in the JSON lines
    out = capsys.readouterr().out.strip()
    result = json.loads(out)
    assert result["status"] == "fail"
    assert "synthetic failure" in result["detail"]


def test_sandbox_launch_uses_a_strict_minimal_environment_allowlist():
    """Guards against silently widening the sandbox launch's own `env -i`
    allowlist -- exactly the real regression class the original
    investigation found (a credential-shaped variable, e.g.
    CLAUDE_CODE_MESSAGING_TOKEN, inheriting into the sandboxed process
    because the launch didn't rebuild its environment from empty).
    Inspects the real source of `main_outer`, not a copy, so it can't go
    stale relative to what's actually run."""
    source = inspect.getsource(verify_cleanroom_isolation.main_outer)
    match = re.search(r"exec env -i ([A-Za-z0-9_=:/.\s\\]+?)\\\n\s*/usr/bin/python3", source)
    assert match, "expected an `exec env -i ... /usr/bin/python3` launch line in main_outer"
    assigned_vars = re.findall(r"([A-Z_]+)=", match.group(1))
    assert assigned_vars == ["PATH", "HOME"], (
        f"sandbox launch environment allowlist changed unexpectedly: {assigned_vars} "
        "-- if this is a deliberate, reviewed change, update this guard test too"
    )


def test_expected_checks_cover_every_governing_prompt_condition():
    """§27.5's own table names eleven conditions. Confirms the actual
    _PROBE_CHECKS list has exactly this many entries, not fewer (a
    silently dropped check) or a divergent count (a typo'd duplicate)."""
    assert len(verify_cleanroom_isolation._PROBE_CHECKS) == 11


# ---------------------------------------------------------------------------
# Real, end-to-end sandbox integration test.
# ---------------------------------------------------------------------------


@requires_sandbox_tools
def test_real_sandbox_preflight_passes_every_check():
    """The actual, real thing: build a real Linux-namespace sandbox,
    bind-mount scratch evidence/output/broker-socket into it, pivot_root,
    run the real probe inside it, and confirm every one of the eleven
    named conditions genuinely, mechanically passes. No real model
    inference occurs (the stand-in broker is fake and content-neutral)
    and no project documentation is read or generated."""
    rc = verify_cleanroom_isolation.main_outer()
    assert rc == 0
