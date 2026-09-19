#!/usr/bin/env python3
"""A tiny, hand-written fake external adapter process, for
tests/test_adapters_external_process.py. Reads one JSON object per line
on stdin, writes one JSON object per line on stdout — a real, minimal
implementation of the codecompass-adaptor-protocol wire shape, not a
mock of `ExternalAdapterProcess` itself, so these tests exercise the
real framing/parsing code end to end without needing the real Haskell
adapter or a `stack` toolchain. Behaviour selected via the
`FAKE_ADAPTER_MODE` environment variable so one fixture script covers
every scenario these tests need.
"""

import json
import os
import sys


def main() -> None:
    mode = os.environ.get("FAKE_ADAPTER_MODE", "normal")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        request = json.loads(line)
        method = request.get("method")
        req_id = request.get("id")

        if mode == "bad_id":
            response = {"id": (req_id or 0) + 1000, "result": {}}
        elif mode == "no_result_no_error":
            response = {"id": req_id}
        elif method == "initialize":
            protocol_version = 999 if mode == "bad_version" else 1
            response = {
                "id": req_id,
                "result": {
                    "protocol_version": protocol_version,
                    "adapter_name": "fake-adapter",
                    "adapter_version": "0.1.0",
                    "ecosystem": "fake",
                    "capabilities": [
                        "dependencies",
                        "symbols",
                        "observations",
                        "diagnostics",
                    ],
                },
            }
        elif method == "analyze_project":
            params = request.get("params", {})
            if mode == "error" or params.get("package_name") == "trigger-error":
                response = {
                    "id": req_id,
                    "error": {"code": "not_found", "message": "package not found"},
                }
            else:
                response = {
                    "id": req_id,
                    "result": {
                        "dependencies": {
                            "name": params.get("package_name", "demo"),
                            "version": "1.0.0",
                            "dev_only": False,
                            "children": [
                                {
                                    "name": "child-dep",
                                    "version": "0.1.0",
                                    "dev_only": False,
                                    "children": [],
                                }
                            ],
                        },
                        "symbols": [
                            {"name": "doThing", "purpose": None, "module": "Demo.Core"}
                        ],
                        "observations": [
                            {
                                "method": "executable",
                                "what_was_done": "ran fake tool",
                                "location": None,
                                "raw_result": "ok",
                                "tool": "fake",
                                "tool_version": "1.0",
                            }
                        ],
                        "diagnostics": [],
                    },
                }
        elif method == "shutdown":
            response = {"id": req_id, "result": {}}
        else:
            response = {
                "id": req_id,
                "error": {"code": "unsupported_capability", "message": f"unknown method {method}"},
            }

        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
