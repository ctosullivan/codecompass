"""Tests for `oracle.run_pytest_check`'s Phase 88 §5.3 hardening: a
subprocess timeout, bounded-while-running output capture, and
process-group-wide termination (not merely the direct pytest child).
See `planning/phase-88-agent-integration-mcp.md` §5.3 for the full
design -- this file implements the two adversarial tests it names
explicitly: a hanging-process test (confirming both the pytest parent
and a deliberately-spawned descendant are terminated) and a
large-output test (confirming early termination, never a silent
truncation presented as a complete result, and never unbounded memory
growth).
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from codecompass import oracle


def _process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


class TestTimeout:
    def test_hanging_check_is_invalid_with_timeout_reason(self, tmp_path: Path) -> None:
        (tmp_path / "test_hang.py").write_text(
            "import time\n\ndef test_hangs():\n    time.sleep(30)\n", encoding="utf-8"
        )
        start = time.monotonic()
        outcome, reason, raw = oracle.run_pytest_check(
            tmp_path, "test_hang.py", timeout_seconds=2.0
        )
        elapsed = time.monotonic() - start
        assert outcome == "INVALID"
        assert "timeout" in reason.lower()
        assert "2.0" in reason
        assert "TERMINATED" in raw
        # Confirms the call actually returned near the configured
        # timeout, not after the full 30s sleep -- the real behaviour
        # under test, not merely the reported outcome string.
        assert elapsed < 15.0

    def test_descendant_process_is_also_terminated_not_only_pytest_itself(
        self, tmp_path: Path
    ) -> None:
        """The second-round correction named explicitly (§5.3): a plain
        single-process kill reaches only the direct pytest child, never
        a descendant the tested code itself spawns. Writes the
        descendant's own real PID to a file so this test can verify,
        after `run_pytest_check` returns, that process is genuinely
        dead -- not merely that the parent pytest process exited."""
        pid_file = tmp_path / "child.pid"
        (tmp_path / "test_hang_with_child.py").write_text(
            f"""
import os
import subprocess
import time

def test_spawns_a_child_then_hangs():
    proc = subprocess.Popen(["sleep", "60"])
    with open({str(pid_file)!r}, "w") as f:
        f.write(str(proc.pid))
    time.sleep(60)
""",
            encoding="utf-8",
        )
        outcome, reason, _raw = oracle.run_pytest_check(
            tmp_path, "test_hang_with_child.py", timeout_seconds=2.0
        )
        assert outcome == "INVALID"
        assert "timeout" in reason.lower()

        # Give the kernel a brief moment to finish reaping; the kill
        # itself is synchronous (SIGKILL), but this avoids flakiness
        # from scheduling jitter in CI-like environments.
        deadline = time.monotonic() + 3.0
        child_pid = int(pid_file.read_text().strip())
        while _process_alive(child_pid) and time.monotonic() < deadline:
            time.sleep(0.1)
        assert not _process_alive(child_pid), (
            f"descendant process {child_pid} is still alive -- process-group "
            "kill did not reach it"
        )


class TestOutputCap:
    def test_large_output_check_is_invalid_with_cap_reason_and_bounded_capture(
        self, tmp_path: Path
    ) -> None:
        # Writes far more than the small cap below, in a tight loop with
        # no delay -- if capture were unbounded (the pre-existing
        # `capture_output=True` behaviour), this would accumulate the
        # entire flood in memory before any check could apply.
        #
        # Deliberately fails (`assert False`): pytest's own default
        # per-test output capture (`--capture=fd`) holds a passing
        # test's stdout entirely internally and never emits it to this
        # process's real stdout pipe at all -- confirmed empirically
        # this session (a passing 2000-line flood produced zero bytes
        # on the real pipe; the identical flood on a *failing* test
        # produced the full, real byte count, replayed as part of
        # pytest's own failure report). A failing test is therefore the
        # only way to genuinely exercise this cap against real bytes
        # arriving on the real subprocess pipe, not an artifact of this
        # test's own construction.
        (tmp_path / "test_flood.py").write_text(
            "def test_floods_stdout():\n"
            "    for _ in range(1_000_000):\n"
            "        print('x' * 200)\n"
            "    assert False\n",
            encoding="utf-8",
        )
        small_cap = 50_000  # bytes -- the flood above would produce ~200MB uncapped
        outcome, reason, raw = oracle.run_pytest_check(
            tmp_path, "test_flood.py", timeout_seconds=60.0, max_output_bytes=small_cap
        )
        assert outcome == "INVALID"
        assert "cap" in reason.lower()
        assert str(small_cap) in reason
        assert "TERMINATED" in raw
        # Bounded capture, not a post-hoc truncation of an already-huge
        # buffer -- the raw text actually returned should be in the same
        # order of magnitude as the cap, not anywhere near the flood's
        # full, uncapped size.
        assert len(raw) < small_cap * 3

    def test_small_output_well_under_cap_is_unaffected(self, tmp_path: Path) -> None:
        (tmp_path / "test_small.py").write_text(
            "def test_ok():\n    print('hello')\n    assert True\n", encoding="utf-8"
        )
        outcome, reason, raw = oracle.run_pytest_check(
            tmp_path, "test_small.py", max_output_bytes=10_000_000
        )
        assert outcome == "PASS"
        assert reason is None
        assert "1 passed" in raw


class TestNoRegressionForOrdinaryExecution:
    def test_default_timeout_and_cap_do_not_affect_a_normal_fast_passing_check(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / "test_ok.py").write_text(
            "def test_ok():\n    assert 1 + 1 == 2\n", encoding="utf-8"
        )
        outcome, reason, raw = oracle.run_pytest_check(tmp_path, "test_ok.py")
        assert outcome == "PASS"
        assert reason is None
        assert "returncode: 0" in raw
