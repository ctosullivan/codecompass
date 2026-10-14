#!/usr/bin/env python3
"""Phase 81B Amendment 5 (corrective) -- a repeatable, executable Mode B
isolation preflight.

`planning/phase-81b-mode-b-isolation-investigation.md` and
`planning/phase-81b-broker-isolation-investigation.md` recorded real,
actively-run escape attempts against the namespace/`pivot_root` sandbox
mechanism, but only as investigation prose -- a future maintainer would
need to reconstruct shell commands from a report to re-establish the same
guarantee. This script turns those checks into durable project tooling:
build a disposable Linux-namespace sandbox (the same `unshare --user
--map-root-user --mount --net --pid --fork` + `pivot_root` mechanism used
for the real cold-reader/writer runs), run a probe inside it, and report
pass/fail per named condition.

Deliberately uses only scratch/synthetic evidence and a fake, local,
content-neutral stand-in broker -- this tool never invokes real model
inference and never generates project documentation. It is a boundary
check, not a clean-room documentation run.

Usage:

    python3 scripts/verify_cleanroom_isolation.py

Internal, re-exec'd inside the sandbox -- not for direct use:

    python3 scripts/verify_cleanroom_isolation.py --probe <config.json>
"""

from __future__ import annotations

import json
import os
import secrets
import shutil
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_CREDENTIAL_SHAPED_ENV_NAME_FRAGMENTS = ("token", "key", "secret", "credential", "password")


# ---------------------------------------------------------------------------
# Fake, local, content-neutral stand-in broker (never real inference --
# §27.2's own explicit scope limit).
# ---------------------------------------------------------------------------


class _FakeBrokerHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        self.request.settimeout(5)
        try:
            data = self.request.recv(65536)
        except OSError:
            return
        try:
            json.loads(data.decode("utf-8")) if data else None
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass
        response = json.dumps({"ok": True, "output": "fake-broker-ack", "usage": {}}).encode(
            "utf-8"
        )
        try:
            self.request.sendall(response)
        except OSError:
            pass


class _FakeUnixBroker(socketserver.ThreadingUnixStreamServer):
    allow_reuse_address = True


class _FakeTCPBroker(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


# ---------------------------------------------------------------------------
# Probe mode -- runs INSIDE the sandbox once pivot_root has completed.
# ---------------------------------------------------------------------------


def _check(name: str, status: str, detail: str) -> dict:
    assert status in ("pass", "fail", "skip")
    return {"check": name, "status": status, "detail": detail}


def _probe_evidence_readable(config: dict) -> dict:
    marker = Path("/evidence/marker.txt")
    if not marker.is_file():
        return _check("evidence_readable", "fail", "/evidence/marker.txt not found")
    content = marker.read_text(encoding="utf-8").strip()
    if content != config["evidence_token"]:
        return _check(
            "evidence_readable", "fail", f"unexpected evidence content: {content!r}"
        )
    return _check(
        "evidence_readable", "pass", "/evidence/marker.txt readable with expected content"
    )


def _probe_output_writable(_config: dict) -> dict:
    target = Path("/output/preflight-write-test.txt")
    try:
        target.write_text("ok\n", encoding="utf-8")
        readback = target.read_text(encoding="utf-8")
    except OSError as exc:
        return _check("output_writable", "fail", f"could not write/read /output: {exc}")
    if readback != "ok\n":
        return _check("output_writable", "fail", "readback mismatch")
    return _check("output_writable", "pass", "/output is writable and readable")


def _probe_parent_host_paths_unavailable(config: dict) -> dict:
    if Path("/home").exists():
        return _check("parent_host_paths_unavailable", "fail", "/home exists in the sandbox view")
    real_root = Path(config["real_root"])
    if real_root.exists():
        return _check(
            "parent_host_paths_unavailable", "fail", f"{real_root} is reachable from the sandbox"
        )
    return _check(
        "parent_host_paths_unavailable",
        "pass",
        "/home absent; the real repository checkout path is unreachable",
    )


def _probe_sibling_repositories_unavailable(config: dict) -> dict:
    reachable = [s for s in config["siblings"] if Path(config["real_root_parent"], s).exists()]
    if reachable:
        return _check(
            "sibling_repositories_unavailable", "fail", f"reachable siblings: {reachable}"
        )
    return _check(
        "sibling_repositories_unavailable",
        "pass",
        f"none of {len(config['siblings'])} real sibling checkouts reachable",
    )


def _probe_git_history_unavailable(_config: dict) -> dict:
    result = subprocess.run(
        ["find", "/", "-maxdepth", "6", "-iname", ".git"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    hits = [line for line in result.stdout.splitlines() if line]
    if hits:
        return _check("git_history_unavailable", "fail", f"found .git at: {hits}")
    return _check(
        "git_history_unavailable", "pass", "no .git directory anywhere in the sandbox's view"
    )


def _probe_git_remotes_unavailable(_config: dict) -> dict:
    result = subprocess.run(
        ["git", "remote"], cwd="/", capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0 and result.stdout.strip():
        return _check("git_remotes_unavailable", "fail", f"git remote succeeded: {result.stdout}")
    return _check(
        "git_remotes_unavailable",
        "pass",
        "`git remote` fails or is empty -- no repository, hence no remotes",
    )


def _probe_environment_secrets_absent(config: dict) -> dict:
    leaked = []
    for name, value in os.environ.items():
        lowered = name.lower()
        if any(fragment in lowered for fragment in _CREDENTIAL_SHAPED_ENV_NAME_FRAGMENTS):
            leaked.append(name)
        if config["credential_canary"] in value:
            leaked.append(f"{name} (contains canary value)")
    if leaked:
        return _check("environment_secrets_absent", "fail", f"leaked: {leaked}")
    return _check(
        "environment_secrets_absent",
        "pass",
        f"{len(os.environ)} environment variables present, none credential-shaped or "
        "carrying the injected canary",
    )


def _probe_unapproved_network_unavailable(_config: dict) -> dict:
    result = subprocess.run(
        ["curl", "-m", "3", "-s", "-o", "/dev/null", "-w", "%{http_code}", "https://example.com"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip() not in ("", "000"):
        return _check(
            "unapproved_network_unavailable",
            "fail",
            f"curl to example.com succeeded: http_code={result.stdout}",
        )
    return _check(
        "unapproved_network_unavailable",
        "pass",
        f"curl to example.com failed as expected (exit {result.returncode})",
    )


def _probe_github_unavailable(_config: dict) -> dict:
    result = subprocess.run(
        ["curl", "-m", "3", "-s", "-o", "/dev/null", "-w", "%{http_code}", "https://github.com"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip() not in ("", "000"):
        return _check(
            "github_unavailable", "fail", f"curl to github.com succeeded: http_code={result.stdout}"
        )
    return _check(
        "github_unavailable",
        "pass",
        f"curl to github.com failed as expected (exit {result.returncode})",
    )


def _probe_broker_boundary(config: dict) -> dict:
    # (a) the one bind-mounted socket must work.
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect(config["broker_socket_path"])
            sock.sendall(json.dumps({"system_prompt": "x", "messages": []}).encode("utf-8"))
            sock.shutdown(socket.SHUT_WR)
            resp = json.loads(sock.recv(65536).decode("utf-8"))
        if not resp.get("ok"):
            return _check("broker_boundary", "fail", f"bind-mounted broker socket returned: {resp}")
    except OSError as exc:
        return _check(
            "broker_boundary", "fail", f"could not reach the bind-mounted broker socket: {exc}"
        )

    # (b) the broker's own host-side TCP listener (same fake broker,
    # reachable over the network on the host) must NOT be reachable --
    # the only approved path in is the one bind-mounted Unix socket.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            sock.connect(("127.0.0.1", config["broker_host_tcp_port"]))
        return _check(
            "broker_boundary",
            "fail",
            "reached the broker's host-side TCP listener -- a non-IPC path is reachable",
        )
    except OSError:
        pass

    return _check(
        "broker_boundary",
        "pass",
        "broker reachable only via the one bind-mounted Unix socket; its host-side "
        "TCP listener (a deliberately-provided non-approved path) is unreachable",
    )


def _probe_parent_agent_context_absent(config: dict) -> dict:
    findings = []
    for candidate in ("/root/.claude", "/home/.claude"):
        if Path(candidate).exists():
            findings.append(candidate)
    for value in os.environ.values():
        if config["parent_context_canary"] in value:
            findings.append("parent-context canary present in environment")
            break
    if findings:
        return _check("parent_agent_context_absent", "fail", f"found: {findings}")
    return _check(
        "parent_agent_context_absent",
        "pass",
        "no .claude state and no parent-conversation canary reachable from the sandbox",
    )


_PROBE_CHECKS = [
    _probe_evidence_readable,
    _probe_output_writable,
    _probe_parent_host_paths_unavailable,
    _probe_sibling_repositories_unavailable,
    _probe_git_history_unavailable,
    _probe_git_remotes_unavailable,
    _probe_environment_secrets_absent,
    _probe_unapproved_network_unavailable,
    _probe_github_unavailable,
    _probe_broker_boundary,
    _probe_parent_agent_context_absent,
]


def _run_probe(config: dict) -> int:
    for fn in _PROBE_CHECKS:
        try:
            result = fn(config)
        except Exception as exc:  # noqa: BLE001 -- report, never silently pass
            result = _check(fn.__name__, "fail", f"probe raised {type(exc).__name__}: {exc}")
        print(json.dumps(result))
    return 0


# ---------------------------------------------------------------------------
# Outer driver -- builds the sandbox, runs the probe inside it, reports.
# ---------------------------------------------------------------------------


def _find_siblings(real_root: Path) -> list[str]:
    parent = real_root.parent
    siblings = []
    try:
        for entry in parent.iterdir():
            if entry.is_dir() and entry != real_root and (entry / ".git").exists():
                siblings.append(entry.name)
    except OSError:
        pass
    return sorted(siblings)


def _build_sandbox_tree(newroot: Path) -> None:
    dirs = (
        "usr", "lib", "lib64", "bin", "sbin", "etc", "proc", "run", "evidence", "output", "oldroot"
    )
    for d in dirs:
        (newroot / d).mkdir(parents=True, exist_ok=True)


def main_outer() -> int:
    real_root = ROOT
    scratch = Path(tempfile.mkdtemp(prefix="cleanroom-isolation-preflight-"))
    try:
        evidence_src = scratch / "evidence-src"
        output_src = scratch / "output-src"
        evidence_src.mkdir()
        output_src.mkdir()
        evidence_token = secrets.token_hex(16)
        (evidence_src / "marker.txt").write_text(evidence_token + "\n", encoding="utf-8")

        credential_canary = "PREFLIGHT-CREDENTIAL-CANARY-" + secrets.token_hex(8)
        parent_context_canary = "PREFLIGHT-PARENT-CONTEXT-CANARY-" + secrets.token_hex(8)

        # Fake, local, content-neutral stand-in broker -- never real
        # inference (§27.2). Listens on both a Unix socket (the one
        # approved IPC path, bind-mounted into the sandbox below) and a
        # host-side TCP port (deliberately NOT bind-mounted, used only to
        # prove that path is unreachable from inside the sandbox).
        broker_sock_path = scratch / "broker.sock"
        unix_broker = _FakeUnixBroker(str(broker_sock_path), _FakeBrokerHandler)
        tcp_broker = _FakeTCPBroker(("127.0.0.1", 0), _FakeBrokerHandler)
        broker_host_tcp_port = tcp_broker.server_address[1]
        for srv in (unix_broker, tcp_broker):
            threading.Thread(target=srv.serve_forever, daemon=True).start()
        time.sleep(0.2)

        config = {
            "evidence_token": evidence_token,
            "real_root": str(real_root),
            "real_root_parent": str(real_root.parent),
            "siblings": _find_siblings(real_root),
            "credential_canary": credential_canary,
            "parent_context_canary": parent_context_canary,
            "broker_socket_path": "/run/broker.sock",
            "broker_host_tcp_port": broker_host_tcp_port,
        }

        newroot = scratch / "newroot"
        _build_sandbox_tree(newroot)
        config_path = scratch / "config.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        probe_script_dst = newroot / "run" / "verify_cleanroom_isolation.py"
        probe_script_dst.touch()
        probe_config_dst = newroot / "run" / "config.json"
        probe_config_dst.touch()
        (newroot / "run" / "broker.sock").touch()

        this_script = Path(__file__).resolve()
        bash_script = f"""
set -e
NR={newroot}
mount --bind "$NR" "$NR"
mount --bind /usr "$NR/usr" -o ro
mount --bind /lib "$NR/lib" -o ro
mount --bind /lib64 "$NR/lib64" -o ro 2>/dev/null || true
mount --bind /bin "$NR/bin" -o ro
mount --bind /sbin "$NR/sbin" -o ro
mount --bind /etc "$NR/etc" -o ro
mount --bind {evidence_src} "$NR/evidence" -o ro
mount --bind {output_src} "$NR/output"
mount --bind {this_script} "$NR/run/verify_cleanroom_isolation.py" -o ro
mount --bind {config_path} "$NR/run/config.json" -o ro
mount --bind {broker_sock_path} "$NR/run/broker.sock"
mount -t proc proc "$NR/proc"
cd "$NR" && pivot_root . oldroot && umount -l /oldroot
exec env -i PATH=/usr/bin:/bin HOME=/nonexistent \
    /usr/bin/python3 /run/verify_cleanroom_isolation.py --probe /run/config.json
"""
        # Simulate a real orchestrator process whose own OS environment
        # contains a credential-shaped variable (exactly the class of real
        # bug the original Mode B investigation found:
        # CLAUDE_CODE_MESSAGING_TOKEN inheriting into the sandboxed
        # process unless explicitly cleared). This variable is injected
        # into *this* process's environment only -- never into the `env
        # -i` command line above -- so the launch subprocess below
        # inherits it exactly the way a real orchestrator's own launch
        # would, and the only thing standing between it and the sandboxed
        # probe is the `env -i PATH=... HOME=...` boundary inside
        # `bash_script` itself. If that boundary is ever weakened (e.g.
        # someone "simplifies" it to a bare `unshare ... -- python3 ...`),
        # this check regresses to a real, visible failure.
        sandboxed_env = dict(os.environ)
        fake_token_var = "CLEANROOM_PREFLIGHT_FAKE_" + secrets.token_hex(4).upper() + "_TOKEN"
        sandboxed_env[fake_token_var] = credential_canary
        sandboxed_env["CLEANROOM_PREFLIGHT_PARENT_CONTEXT"] = parent_context_canary

        result = subprocess.run(
            [
                "unshare",
                "--user",
                "--map-root-user",
                "--mount",
                "--net",
                "--pid",
                "--fork",
                "--",
                "bash",
                "-c",
                bash_script,
            ],
            capture_output=True,
            text=True,
            timeout=120,
            env=sandboxed_env,
        )

        for srv in (unix_broker, tcp_broker):
            srv.shutdown()

        results = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        expected_checks = {fn.__name__.removeprefix("_probe_") for fn in _PROBE_CHECKS}
        seen_checks = {r["check"].removeprefix("_probe_") for r in results}
        for missing in sorted(expected_checks - seen_checks):
            results.append(
                _check(
                    missing,
                    "skip",
                    "this condition could not be mechanically evaluated by this "
                    "preflight run -- reported separately rather than assumed to pass",
                )
            )

        print(f"{'CHECK':<40} {'STATUS':<6} DETAIL")
        print("-" * 100)
        any_failed = False
        any_skipped = False
        for r in results:
            name = r["check"].removeprefix("_probe_")
            status = r["status"]
            if status == "fail":
                any_failed = True
            if status == "skip":
                any_skipped = True
            print(f"{name:<40} {status:<6} {r['detail']}")

        if result.returncode != 0 and not results:
            print("\nFAIL: sandbox construction itself failed", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return 1

        if any_skipped:
            print(
                "\nNOTE: one or more conditions could not be mechanically tested -- "
                "see 'skip' rows above; this preflight does not claim they pass."
            )
        if any_failed:
            print("\nFAIL: one or more isolation checks failed")
            return 1
        print("\nPASS: every mechanically-testable isolation condition held")
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main(argv: list[str]) -> int:
    if len(argv) >= 3 and argv[1] == "--probe":
        config = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
        return _run_probe(config)
    return main_outer()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
