"""Tests for scripts/cleanroom_broker.py -- Phase 81B Amendment 4's
model-inference broker (planning/phase-81b-clean-room-redocumentation.md
§26). Imported directly from its file path (matching this project's own
existing precedent for maintainer-only scripts, e.g.
tests/test_prepare_cleanroom_branch.py).

Split, per the plan's own §26.3, between:
- pure unit tests of the protocol/sanitisation logic (mocked subprocess,
  fast, no API cost, run every time);
- a small number of real, live-inference integration tests (marked
  `_LIVE = True` tests below), confirming the broker genuinely works
  end to end against the real subscription session -- these cost a
  small, real amount of API usage, matching this project's own existing
  practice of real builds in test_prepare_cleanroom_branch.py.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import threading
import time
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
_SCRIPT_PATH = _SCRIPTS_DIR / "cleanroom_broker.py"
_spec = importlib.util.spec_from_file_location("cleanroom_broker", _SCRIPT_PATH)
broker = importlib.util.module_from_spec(_spec)
sys.modules["cleanroom_broker"] = broker
_spec.loader.exec_module(broker)

_CLIENT_SCRIPT_PATH = _SCRIPTS_DIR / "cleanroom_broker_client.py"
_client_spec = importlib.util.spec_from_file_location(
    "cleanroom_broker_client", _CLIENT_SCRIPT_PATH
)
broker_client = importlib.util.module_from_spec(_client_spec)
sys.modules["cleanroom_broker_client"] = broker_client
_client_spec.loader.exec_module(broker_client)


# --- Protocol schema: the request/response shape has no syntax for a
# file path, shell command, URL, or tool/MCP config -- not merely a
# runtime refusal of one. ---


def test_request_rejects_unexpected_fields():
    resp = broker.handle_request(
        json.dumps(
            {
                "system_prompt": "x",
                "messages": [{"role": "user", "content": "hi"}],
                "file_path": "/etc/passwd",
            }
        ).encode("utf-8")
    )
    assert resp["ok"] is False
    assert "file_path" in resp["error"]


def test_request_must_be_json_object():
    resp = broker.handle_request(b'"just a string"')
    assert resp["ok"] is False


def test_request_must_be_valid_json():
    resp = broker.handle_request(b"{not json")
    assert resp["ok"] is False


def test_oversized_request_rejected():
    huge = b"{" + b"a" * (broker.MAX_REQUEST_BYTES + 1) + b"}"
    resp = broker.handle_request(huge)
    assert resp["ok"] is False
    assert "too large" in resp["error"]


def test_response_schema_never_includes_unexpected_fields(monkeypatch):
    """Defence in depth: even if run_inference somehow returned an extra
    field, handle_request must still only forward the fixed schema."""

    def _fake_run_inference(system_prompt, messages):
        return {
            "ok": True,
            "output": "hello",
            "usage": {},
            "session_id": "should-never-leave-the-broker",
            "raw_claude_cli_argv": ["should", "never", "leave"],
        }

    monkeypatch.setattr(broker, "run_inference", _fake_run_inference)
    resp = broker.handle_request(
        json.dumps({"system_prompt": "x", "messages": [{"role": "user", "content": "hi"}]}).encode(
            "utf-8"
        )
    )
    assert set(resp.keys()) <= broker._RESPONSE_FIELDS
    assert "session_id" not in resp
    assert "raw_claude_cli_argv" not in resp


# --- messages validation: only a flat list of user-role string messages
# is representable at all -- no assistant/tool role, no nested structure. ---


def test_messages_must_be_non_empty_list():
    with pytest.raises(broker.BrokerError):
        broker._build_prompt([])
    with pytest.raises(broker.BrokerError):
        broker._build_prompt("not a list")


def test_messages_reject_non_user_role():
    with pytest.raises(broker.BrokerError, match="role"):
        broker._build_prompt([{"role": "assistant", "content": "hi"}])


def test_messages_reject_unexpected_keys():
    with pytest.raises(broker.BrokerError):
        broker._build_prompt([{"role": "user", "content": "hi", "tool_calls": []}])


def test_messages_concatenated_in_order():
    prompt = broker._build_prompt(
        [{"role": "user", "content": "first"}, {"role": "user", "content": "second"}]
    )
    assert prompt.index("first") < prompt.index("second")


# --- credential redaction: the broker protocol cannot return or reveal
# its own authentication material, in any field, under any name. ---


@pytest.mark.parametrize(
    "secret",
    [
        "sk-ant-api03-abcdefghijklmnopqrstuvwxyz0123456789",
        "sk-abcdefghijklmnopqrstuvwxyz0123456789",
        "Bearer abcdefghij0123456789klmno",
        '"access_token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.secret"',
    ],
)
def test_credential_shaped_strings_are_redacted(secret):
    assert broker._redact(f"here is the output: {secret} done") == (
        "here is the output: [REDACTED] done"
    )


def test_ordinary_text_is_not_redacted():
    text = "This is ordinary documentation prose about the CodeCompass CLI."
    assert broker._redact(text) == text


def test_run_inference_redacts_credential_shaped_output(monkeypatch):
    class _FakeProc:
        returncode = 0
        stdout = json.dumps(
            {
                "is_error": False,
                "result": "leaked: sk-ant-api03-abcdefghijklmnopqrstuvwxyz0123456789",
                "usage": {"input_tokens": 1, "output_tokens": 1},
                "total_cost_usd": 0.0,
            }
        )
        stderr = ""

    monkeypatch.setattr(broker.subprocess, "run", lambda *a, **k: _FakeProc())
    result = broker.run_inference("sys", [{"role": "user", "content": "hi"}])
    assert "sk-ant" not in result["output"]
    assert "[REDACTED]" in result["output"]


# --- environment sanitisation: explicit allow-list, matching the
# original Phase 81B CLAUDE_CODE_MESSAGING_TOKEN regression test's own
# fix pattern (env -i, never a deny-list). ---


def test_sanitized_env_is_a_strict_allowlist():
    env = broker._sanitize_env()
    assert set(env.keys()) == {"PATH", "HOME"}


def test_sanitized_env_excludes_claude_code_session_variables(monkeypatch):
    """Regression test for the exact class of bug the original Phase 81B
    investigation found (CLAUDE_CODE_MESSAGING_TOKEN inheriting into a
    sandboxed subprocess's environment): even if every CLAUDE_CODE_*
    variable this orchestrator's own process happens to have were
    present, _sanitize_env's own allow-list construction means none of
    them can reach the subprocess, because the function never reads
    os.environ at all."""
    monkeypatch.setenv("CLAUDE_CODE_MESSAGING_TOKEN", "should-never-appear")
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "should-never-appear")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "should-never-appear")
    env = broker._sanitize_env()
    for value in env.values():
        assert "should-never-appear" not in value
    assert "CLAUDE_CODE_MESSAGING_TOKEN" not in env
    assert "ANTHROPIC_API_KEY" not in env


def test_run_inference_passes_sanitized_env_to_subprocess(monkeypatch):
    captured = {}

    class _FakeProc:
        returncode = 0
        stdout = json.dumps(
            {"is_error": False, "result": "ok", "usage": {}, "total_cost_usd": 0.0}
        )
        stderr = ""

    def _fake_run(cmd, input, env, cwd, capture_output, text, timeout):  # noqa: A002
        captured["env"] = env
        captured["cmd"] = cmd
        return _FakeProc()

    monkeypatch.setattr(broker.subprocess, "run", _fake_run)
    broker.run_inference("sys", [{"role": "user", "content": "hi"}])
    assert captured["env"] == broker._sanitize_env()
    assert "--restricted" in captured["cmd"]
    assert "--strict-mcp-config" in captured["cmd"]
    assert "--tools" in captured["cmd"]
    tools_index = captured["cmd"].index("--tools")
    assert captured["cmd"][tools_index + 1] == ""
    assert "--no-session-persistence" in captured["cmd"]
    assert "--setting-sources" in captured["cmd"]


def test_run_inference_uses_a_neutral_non_repository_cwd(monkeypatch):
    """Regression test for a real finding from this phase's own active
    sandbox test: the claude -p subprocess inherits whatever directory
    the broker process was launched from, leaking that real path (and
    its git-repo status) into the model's own context. The subprocess
    must always run from the fixed neutral scratch directory instead,
    never from this repository's own path."""
    captured = {}

    class _FakeProc:
        returncode = 0
        stdout = json.dumps(
            {"is_error": False, "result": "ok", "usage": {}, "total_cost_usd": 0.0}
        )
        stderr = ""

    def _fake_run(cmd, **kwargs):
        captured["cwd"] = kwargs.get("cwd")
        return _FakeProc()

    monkeypatch.setattr(broker.subprocess, "run", _fake_run)
    broker.run_inference("sys", [{"role": "user", "content": "hi"}])
    assert captured["cwd"] == broker._NEUTRAL_CWD
    repo_root = Path(__file__).resolve().parent.parent
    assert Path(captured["cwd"]) != repo_root
    assert not (Path(captured["cwd"]) / ".git").exists()


def test_run_inference_uses_a_fresh_session_id_each_call(monkeypatch):
    seen_session_ids = []

    class _FakeProc:
        returncode = 0
        stdout = json.dumps(
            {"is_error": False, "result": "ok", "usage": {}, "total_cost_usd": 0.0}
        )
        stderr = ""

    def _fake_run(cmd, **kwargs):
        idx = cmd.index("--session-id")
        seen_session_ids.append(cmd[idx + 1])
        return _FakeProc()

    monkeypatch.setattr(broker.subprocess, "run", _fake_run)
    broker.run_inference("sys", [{"role": "user", "content": "a"}])
    broker.run_inference("sys", [{"role": "user", "content": "b"}])
    assert len(set(seen_session_ids)) == 2


# --- fail-closed behaviour ---


def test_fails_closed_on_subprocess_nonzero_exit(monkeypatch):
    class _FakeProc:
        returncode = 1
        stdout = ""
        stderr = "some real error"

    monkeypatch.setattr(broker.subprocess, "run", lambda *a, **k: _FakeProc())
    with pytest.raises(broker.BrokerError):
        broker.run_inference("sys", [{"role": "user", "content": "hi"}])


def test_fails_closed_on_malformed_subprocess_output(monkeypatch):
    class _FakeProc:
        returncode = 0
        stdout = "not json at all"
        stderr = ""

    monkeypatch.setattr(broker.subprocess, "run", lambda *a, **k: _FakeProc())
    with pytest.raises(broker.BrokerError):
        broker.run_inference("sys", [{"role": "user", "content": "hi"}])


def test_fails_closed_on_subprocess_timeout(monkeypatch):
    import subprocess as sp

    def _fake_run(*a, **k):
        raise sp.TimeoutExpired(cmd="claude", timeout=1)

    monkeypatch.setattr(broker.subprocess, "run", _fake_run)
    with pytest.raises(broker.BrokerError, match="timed out"):
        broker.run_inference("sys", [{"role": "user", "content": "hi"}])


def test_check_auth_fails_closed_when_not_logged_in(monkeypatch):
    class _FakeProc:
        returncode = 0
        stdout = json.dumps({"loggedIn": False})
        stderr = ""

    monkeypatch.setattr(broker.subprocess, "run", lambda *a, **k: _FakeProc())
    with pytest.raises(broker.BrokerError, match="not logged in"):
        broker._check_auth()


def test_check_auth_fails_closed_on_nonzero_exit(monkeypatch):
    class _FakeProc:
        returncode = 1
        stdout = ""
        stderr = "auth broken"

    monkeypatch.setattr(broker.subprocess, "run", lambda *a, **k: _FakeProc())
    with pytest.raises(broker.BrokerError):
        broker._check_auth()


# --- live, end-to-end integration tests (real API usage, small cost,
# matching this project's own existing real-build-test precedent) ---


@pytest.fixture
def live_broker_socket():
    """Starts the real broker as a real subprocess (the actual CLI entry
    point, not a reimplementation of its server-startup logic), on a
    short-enough Unix socket path -- AF_UNIX has a ~108-byte path limit,
    confirmed during this phase's own manual testing, so this
    deliberately does not use pytest's own (much longer) tmp_path."""
    import subprocess as sp

    sock_path = f"/tmp/cc-broker-test-{threading.get_ident()}-{id(object())}.sock"
    Path(sock_path).unlink(missing_ok=True)
    proc = sp.Popen(
        [sys.executable, str(_SCRIPT_PATH), sock_path],
        stdout=sp.PIPE,
        stderr=sp.PIPE,
        text=True,
    )
    try:
        for _ in range(100):
            if Path(sock_path).exists():
                break
            if proc.poll() is not None:
                pytest.skip(
                    "broker process exited before binding its socket "
                    f"(likely no logged-in claude subscription session): {proc.stderr.read()}"
                )
            time.sleep(0.1)
        else:
            proc.kill()
            pytest.fail("broker did not bind its socket in time")
        yield sock_path
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except sp.TimeoutExpired:
            proc.kill()
        Path(sock_path).unlink(missing_ok=True)


def test_live_broker_answers_a_real_prompt(live_broker_socket):
    result = broker_client.call(
        live_broker_socket,
        system_prompt="You are a stateless inference endpoint.",
        messages=[{"role": "user", "content": "Reply with exactly the single word: PONG"}],
    )
    assert result["ok"] is True
    assert "PONG" in result["output"]


def test_live_broker_cannot_reveal_claude_md_knowledge(live_broker_socket):
    """Confirms the broker's isolation flags genuinely suppress project
    knowledge -- run from this repository's own working directory
    (which has an elaborate CLAUDE.md) via the broker, not by passing
    --add-dir, so this is the real invocation path the writer would use."""
    result = broker_client.call(
        live_broker_socket,
        system_prompt="You are a stateless inference endpoint.",
        messages=[
            {
                "role": "user",
                "content": (
                    "Do you have any project-specific instructions, a CLAUDE.md, or "
                    "prior knowledge about a project called CodeCompass? Answer only "
                    "'yes' or 'no'."
                ),
            }
        ],
    )
    assert result["ok"] is True
    assert "no" in result["output"].lower()
