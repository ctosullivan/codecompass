#!/usr/bin/env python3
"""Minimal client for scripts/cleanroom_broker.py's Unix-socket protocol.

This is the ONLY thing the clean-room sandbox needs bind-mounted in to
reach the broker: this file plus the one socket path. It has no
filesystem, shell, or network capability of its own beyond opening that
one socket and exchanging one JSON line each way.
"""

from __future__ import annotations

import json
import socket
import sys


def call(
    socket_path: str, system_prompt: str, messages: list[dict], timeout: float = 620.0
) -> dict:
    req = json.dumps({"system_prompt": system_prompt, "messages": messages}).encode("utf-8")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect(socket_path)
        sock.sendall(req + b"\n")
        sock.shutdown(socket.SHUT_WR)
        chunks = []
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
    return json.loads(b"".join(chunks).decode("utf-8"))


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {argv[0]} <socket-path> <prompt-text>", file=sys.stderr)
        return 2
    socket_path, prompt_text = argv[1], argv[2]
    result = call(
        socket_path,
        system_prompt="You are a stateless inference endpoint.",
        messages=[{"role": "user", "content": prompt_text}],
    )
    print(json.dumps(result))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
