"""Generic JSON-Lines subprocess client for external CodeCompass adapters.

Speaks the protocol defined by `codecompass-adaptor-protocol`
(checked out locally at `protocol/codecompass-adaptor-protocol/`,
`decisions/0058`) and `decisions/0057`. **Zero ecosystem-specific
knowledge** — this module never mentions Haskell, `stack`, or
`package.yaml` anywhere in its own source, and has no import dependency
on either submodule's own content. It spawns whatever executable it is
configured to invoke, purely as an opaque subprocess, and is reusable by
any future external-process adapter (a COBOL one, or a second Haskell
variant) without modification.

See architecture/overview.md's "External adapters" section.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from codecompass.adapters.base import AdapterError

_DEFAULT_TIMEOUT_SECONDS = 120.0
_SHUTDOWN_TIMEOUT_SECONDS = 5.0

# Closed capability set — mirrors codecompass-adaptor-protocol's own
# SCHEMA.md. Kept here, not imported from the submodule (which ships no
# code), so this module has zero file-system dependency on the
# submodule being checked out to be importable.
CAPABILITIES = ("dependencies", "symbols", "observations", "diagnostics")

PROTOCOL_VERSION = 1


class ExternalAdapterProcess:
    """One external adapter subprocess, from `initialize` through
    `shutdown`. Not reused across projects — construct one per
    `analyze_project` call site, matching every in-process adapter's own
    per-`EcosystemAdapter`-instance lifetime.
    """

    def __init__(self, command: list[str]) -> None:
        self._command = command
        self._process: subprocess.Popen[str] | None = None
        self._next_id = 1
        self.capabilities: tuple[str, ...] = ()
        self.adapter_name: str | None = None
        self.adapter_version: str | None = None
        self.ecosystem: str | None = None

    def initialize(self) -> None:
        """Spawn the adapter process and perform the handshake. Raises
        `AdapterError` on a version mismatch, a malformed response, or a
        protocol-level `error` response — never leaves the caller with a
        half-initialized process silently.
        """
        try:
            self._process = subprocess.Popen(
                self._command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        except OSError as exc:
            raise AdapterError(
                f"could not start external adapter process {self._command!r}: {exc}"
            ) from exc
        response = self._request(
            "initialize", {"protocol_version": PROTOCOL_VERSION}
        )
        if response.get("protocol_version") != PROTOCOL_VERSION:
            raise AdapterError(
                "external adapter protocol_version mismatch: "
                f"CodeCompass speaks {PROTOCOL_VERSION}, adapter responded "
                f"with {response.get('protocol_version')!r}"
            )
        self.adapter_name = response.get("adapter_name")
        self.adapter_version = response.get("adapter_version")
        self.ecosystem = response.get("ecosystem")
        self.capabilities = tuple(response.get("capabilities", []))

    def analyze_project(self, project_root: Path, package_name: str) -> dict[str, Any]:
        """Request analysis of an already-resolved package directory.
        Returns the raw, neutral `result` object exactly as the adapter
        sent it — translation into CodeCompass's own graph/evidence
        model happens in the caller (`HaskellAdapter`), not here.
        """
        return self._request(
            "analyze_project",
            {"project_root": str(project_root), "package_name": package_name},
        )

    def shutdown(self) -> None:
        """Request a clean shutdown, then close stdin and wait for exit
        (with a timeout, then a hard kill). Safe to call even if
        `initialize` was never called or already failed.
        """
        if self._process is None:
            return
        try:
            self._request("shutdown", None)
        except AdapterError:
            pass  # best-effort — still proceed to close/kill below
        assert self._process.stdin is not None
        self._process.stdin.close()
        try:
            self._process.wait(timeout=_SHUTDOWN_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()

    def _request(self, method: str, params: dict[str, Any] | None) -> dict[str, Any]:
        if self._process is None:
            raise AdapterError("external adapter process not started")
        assert self._process.stdin is not None
        assert self._process.stdout is not None
        request_id = self._next_id
        self._next_id += 1
        message: dict[str, Any] = {"id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        try:
            self._process.stdin.write(json.dumps(message) + "\n")
            self._process.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise AdapterError(
                f"external adapter process exited before request {method!r} "
                f"could be sent: {self._stderr_tail()}"
            ) from exc
        line = self._process.stdout.readline()
        if not line:
            raise AdapterError(
                f"external adapter process produced no response to {method!r} "
                f"(closed stdout): {self._stderr_tail()}"
            )
        try:
            response = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AdapterError(
                f"external adapter produced invalid JSON in response to {method!r}: {exc}"
            ) from exc
        if response.get("id") != request_id:
            raise AdapterError(
                f"external adapter response id {response.get('id')!r} does not "
                f"match request id {request_id!r} for method {method!r}"
            )
        if "error" in response:
            error = response["error"]
            raise AdapterError(
                f"external adapter error ({error.get('code')}) on {method!r}: "
                f"{error.get('message')}"
            )
        if "result" not in response:
            raise AdapterError(
                f"external adapter response to {method!r} has neither "
                "'result' nor 'error'"
            )
        return response["result"]

    def _stderr_tail(self) -> str:
        if self._process is None or self._process.stderr is None:
            return ""
        try:
            return self._process.stderr.read(4096).strip()
        except (OSError, ValueError):
            return ""
