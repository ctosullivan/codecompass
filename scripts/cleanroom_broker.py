#!/usr/bin/env python3
"""Phase 81B Amendment 4 -- narrowly-scoped model-inference broker.

Runs OUTSIDE the clean-room sandbox, on the trusted host. Holds the
existing Claude subscription session (~/.claude/.credentials.json,
never copied, never exposed) and exposes only a narrow inference
capability over a Unix domain socket: a clean-room writer or cold-reader
inside the sandbox sends {system_prompt, messages}, gets back
{ok, output, usage} -- never a credential, never a tool, never a file
path, never a shell command.

See planning/phase-81b-clean-room-redocumentation.md §26 for the full
design rationale and the investigation this implementation is grounded
in. Every isolation/fail-closed property named there is enforced here,
not only described.
"""

from __future__ import annotations

import json
import re
import socketserver
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

CLAUDE_BIN = "claude"
SUBPROCESS_TIMEOUT_S = 600
MAX_REQUEST_BYTES = 8 * 1024 * 1024

# A real, active sandbox test (Phase 81B Amendment 4) found that the
# claude -p subprocess inherits whatever directory the broker process
# itself happens to be launched from, and that directory's path (and
# git-repo status) leaks into the model's own "Environment" system-
# reminder block -- regardless of the sandbox's own isolation, since
# this leak happens entirely on the trusted-host side, inside the
# broker. A fresh, neutral, non-git scratch directory -- unrelated to
# any real project path, created once per broker process -- is used as
# every inference subprocess's cwd instead, so the real repository's
# path and git status never reach the model.
_NEUTRAL_CWD = tempfile.mkdtemp(prefix="cleanroom-broker-cwd-")
MAX_OUTPUT_BYTES = 8 * 1024 * 1024

# Only these top-level fields are ever accepted from a request, and only
# these are ever returned in a response. The protocol has no syntax to
# ask for a file path, a shell command, a URL, or a tool/MCP config --
# not merely a runtime refusal of one.
_REQUEST_FIELDS = {"system_prompt", "messages", "max_turns"}
_RESPONSE_FIELDS = {"ok", "output", "usage", "error"}

# Credential/secret-shaped content must never cross back out of the
# broker, in any field, under any name. Intentionally broad (errs
# toward over-redaction, never under).
_CREDENTIAL_PATTERN = re.compile(
    r"(sk-ant-[A-Za-z0-9_-]{10,})"
    r"|(sk-[A-Za-z0-9]{20,})"
    r"|([A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,})"  # JWT-shaped
    r"|(\bBearer\s+[A-Za-z0-9._-]{10,}\b)"
    r"|(\"access_token\"\s*:\s*\"[^\"]+\")"
    r"|(\"refresh_token\"\s*:\s*\"[^\"]+\")"
    r"|(\"apiKey\"\s*:\s*\"[^\"]+\")"
)


class BrokerError(Exception):
    pass


def _sanitize_env() -> dict[str, str]:
    """Explicit allow-list, never a deny-list. This is the same fix
    Phase 81B's original investigation required after finding
    CLAUDE_CODE_MESSAGING_TOKEN inherits into a subprocess's environment
    unless explicitly cleared -- building via env -i PATH=... HOME=...
    rather than os.environ.copy() + delete, so a newly-added
    CLAUDE_CODE_* variable in a future CLI version can never silently
    reappear here without this allow-list being edited to add it back
    on purpose."""
    return {"PATH": "/usr/bin:/bin:/home/cormac/.local/bin", "HOME": "/home/cormac"}


def _redact(text: str) -> str:
    return _CREDENTIAL_PATTERN.sub("[REDACTED]", text)


def _check_auth() -> None:
    """Fail closed at startup, not per-request: if the host session is
    not genuinely logged in to a usable subscription, refuse to serve
    any request at all rather than falling back to a weaker mechanism
    (an API key, a stale cached response) silently."""
    try:
        proc = subprocess.run(
            [CLAUDE_BIN, "auth", "status"],
            env=_sanitize_env(),
            cwd=_NEUTRAL_CWD,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BrokerError(f"could not run `claude auth status`: {exc}") from exc
    if proc.returncode != 0:
        raise BrokerError(f"`claude auth status` exited {proc.returncode}: {proc.stderr}")
    try:
        status = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise BrokerError(f"`claude auth status` produced non-JSON output: {exc}") from exc
    if not status.get("loggedIn"):
        raise BrokerError("`claude auth status` reports not logged in -- refusing to serve")


def _build_prompt(messages: list[dict]) -> str:
    """Only a flat sequence of user-role messages is supported -- there
    is no agentic tool-call loop here (--tools "" ensures none can
    exist), so there is no assistant/tool turn for this protocol to
    represent. Concatenated with a clear separator so a multi-part
    clean-room prompt (instructions + handoff content assembled by the
    caller) reads as one coherent stateless request."""
    if not isinstance(messages, list) or not messages:
        raise BrokerError("messages must be a non-empty list")
    parts = []
    for i, m in enumerate(messages):
        if not isinstance(m, dict) or set(m.keys()) - {"role", "content"}:
            raise BrokerError(f"messages[{i}] has an unexpected shape")
        if m.get("role") != "user":
            raise BrokerError(f"messages[{i}].role must be 'user' (got {m.get('role')!r})")
        content = m.get("content")
        if not isinstance(content, str) or not content:
            raise BrokerError(f"messages[{i}].content must be a non-empty string")
        parts.append(content)
    return "\n\n---\n\n".join(parts)


def run_inference(system_prompt: str, messages: list[dict]) -> dict:
    """The one real capability this broker exposes. Every subprocess is
    fresh: a brand-new --session-id, no --resume/--continue, so two
    calls (e.g. cold-reader then writer) never share hidden state."""
    if not isinstance(system_prompt, str) or not system_prompt:
        raise BrokerError("system_prompt must be a non-empty string")
    prompt = _build_prompt(messages)
    session_id = str(uuid.uuid4())
    cmd = [
        CLAUDE_BIN,
        "-p",
        "--restricted",
        "--strict-mcp-config",
        "--tools",
        "",
        "--no-session-persistence",
        "--output-format",
        "json",
        "--setting-sources",
        "",
        "--session-id",
        session_id,
        "--system-prompt",
        system_prompt,
    ]
    try:
        proc = subprocess.run(
            cmd,
            input=prompt,
            env=_sanitize_env(),
            cwd=_NEUTRAL_CWD,
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired as exc:
        raise BrokerError(f"inference subprocess timed out after {SUBPROCESS_TIMEOUT_S}s") from exc
    except OSError as exc:
        raise BrokerError(f"could not start inference subprocess: {exc}") from exc
    if proc.returncode != 0:
        detail = _redact(proc.stderr)[:2000]
        raise BrokerError(f"inference subprocess exited {proc.returncode}: {detail}")
    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise BrokerError(f"inference subprocess produced non-JSON output: {exc}") from exc
    if envelope.get("is_error"):
        detail = _redact(str(envelope.get("result")))[:2000]
        raise BrokerError(f"inference reported an error: {detail}")
    output = envelope.get("result")
    if not isinstance(output, str):
        raise BrokerError("inference subprocess produced no usable 'result' text")
    if len(output) > MAX_OUTPUT_BYTES:
        raise BrokerError("inference output exceeded the maximum allowed size")
    output = _redact(output)
    usage_raw = envelope.get("usage") or {}
    usage = {
        "input_tokens": usage_raw.get("input_tokens"),
        "output_tokens": usage_raw.get("output_tokens"),
        "total_cost_usd": envelope.get("total_cost_usd"),
    }
    return {"ok": True, "output": output, "usage": usage}


def handle_request(raw: bytes) -> dict:
    if len(raw) > MAX_REQUEST_BYTES:
        return {"ok": False, "error": "request too large"}
    try:
        req = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": f"request is not valid JSON: {exc}"}
    if not isinstance(req, dict):
        return {"ok": False, "error": "request must be a JSON object"}
    unexpected = set(req.keys()) - _REQUEST_FIELDS
    if unexpected:
        return {"ok": False, "error": f"unexpected request field(s): {sorted(unexpected)}"}
    try:
        result = run_inference(req.get("system_prompt"), req.get("messages"))
    except BrokerError as exc:
        return {"ok": False, "error": str(exc)}
    # Final defence-in-depth: strip anything outside the fixed response
    # schema, however it got there.
    return {k: v for k, v in result.items() if k in _RESPONSE_FIELDS}


class _Handler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        try:
            line = self.rfile.readline(MAX_REQUEST_BYTES + 1)
        except OSError:
            return
        if not line:
            return
        response = handle_request(line.rstrip(b"\n"))
        try:
            self.wfile.write(json.dumps(response).encode("utf-8") + b"\n")
        except OSError:
            pass


class _Server(socketserver.ThreadingUnixStreamServer):
    daemon_threads = True
    allow_reuse_address = True


def serve(socket_path: str) -> None:
    _check_auth()
    path = Path(socket_path)
    if path.exists():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    server = _Server(str(path), _Handler)
    path.chmod(0o600)
    print(f"cleanroom_broker: listening on {path}", file=sys.stderr, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        path.unlink(missing_ok=True)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <socket-path>", file=sys.stderr)
        return 2
    try:
        serve(argv[1])
    except BrokerError as exc:
        print(f"cleanroom_broker: FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
