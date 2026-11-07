"""Tests for scripts/execute_doc_example.py -- Stage 87B's own safe,
bounded executable-example verification harness for
docs/getting-started.md (plan §O.C, third corrective amendment finding
D).

Mirrors tests/test_verify_cleanroom_isolation.py's own convention: the
pure-logic pieces (the allow-list rejection, output classification) are
unit tested directly and always run; the real, adversarially-meaningful
end-to-end runs (building an actual Linux-namespace sandbox and
genuinely executing `codecompass`/`pip install`/`git clone` inside it)
are skipped automatically where `unshare`/`pivot_root` aren't available,
or where the one-time, out-of-band fixture cache (`--prepare-fixtures`)
hasn't been built yet -- never run with a live, un-cached network fetch
inside a test.
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_SCRIPT_PATH = ROOT / "scripts" / "execute_doc_example.py"

_spec = importlib.util.spec_from_file_location("execute_doc_example", _SCRIPT_PATH)
execute_doc_example = importlib.util.module_from_spec(_spec)
sys.modules["execute_doc_example"] = execute_doc_example
_spec.loader.exec_module(execute_doc_example)


def _sandbox_tools_available() -> bool:
    return all(shutil.which(tool) for tool in ("unshare", "pivot_root", "git", "bash"))


def _fixtures_prepared() -> bool:
    return (
        execute_doc_example.WHEEL_CACHE_DIR.is_dir()
        and execute_doc_example.GIT_MIRROR_DIR.is_dir()
        and execute_doc_example.HARNESS_VENV_DIR.is_dir()
    )


requires_real_sandbox = pytest.mark.skipif(
    not (_sandbox_tools_available() and _fixtures_prepared()),
    reason="unshare/pivot_root/git not available, or --prepare-fixtures has not been run",
)


# ---------------------------------------------------------------------------
# Pure-logic unit tests (no real sandbox construction) -- always run.
# ---------------------------------------------------------------------------


def test_unauthorised_command_is_rejected_before_the_sandbox_is_entered():
    with pytest.raises(ValueError, match="not in this script's own fixed allow-list"):
        execute_doc_example.execute("rm -rf /")


def test_every_allowed_command_is_a_real_allowed_command_instance():
    assert execute_doc_example.ALLOWED_COMMANDS  # non-empty
    for name, command in execute_doc_example.ALLOWED_COMMANDS.items():
        assert isinstance(command, execute_doc_example.AllowedCommand), name
        assert command.argv, name
        assert command.comparison_mode in ("exact", "normalized_whitespace", "regex"), name


def test_paid_api_triggering_commands_are_never_in_the_allow_list():
    # Third corrective amendment, finding D: a credential-less sandbox
    # can never complete `--yes`/`--budget 1.00` -- they must never be
    # reachable through this harness at all.
    for command in execute_doc_example.ALLOWED_COMMANDS.values():
        assert "--yes" not in command.argv
        assert "1.00" not in command.argv


def _make_command(**overrides):
    base = dict(
        argv=["x"], fixture=None, expected_exit_code=0,
        comparison_mode="exact", pattern="hello",
    )
    base.update(overrides)
    return execute_doc_example.AllowedCommand(**base)


def test_classify_fails_on_wrong_exit_code():
    command = _make_command(expected_exit_code=0)
    ok, reason = execute_doc_example._classify(command, 1, "hello")
    assert not ok
    assert "exit code" in reason


def test_classify_exact_match():
    command = _make_command(comparison_mode="exact", pattern="hello world")
    ok, _ = execute_doc_example._classify(command, 0, "hello world")
    assert ok


def test_classify_exact_rejects_a_near_miss():
    command = _make_command(comparison_mode="exact", pattern="hello world")
    ok, reason = execute_doc_example._classify(command, 0, "hello World")
    assert not ok
    assert "did not match" in reason


def test_classify_normalized_whitespace_ignores_spacing_differences():
    command = _make_command(comparison_mode="normalized_whitespace", pattern="hello   world")
    ok, _ = execute_doc_example._classify(command, 0, "hello\nworld")
    assert ok


def test_classify_regex_matches_a_narrow_numeric_shape_pattern():
    command = _make_command(comparison_mode="regex", pattern=r"cost \$\d+\.\d\d")
    ok, _ = execute_doc_example._classify(command, 0, "estimated cost $0.02 for this run")
    assert ok


def test_classify_regex_rejects_a_materially_wrong_output():
    command = _make_command(comparison_mode="regex", pattern=r"2 vendor\(s\) tracked")
    ok, reason = execute_doc_example._classify(command, 0, "0 vendor(s) tracked")
    assert not ok
    assert "did not match" in reason


# ---------------------------------------------------------------------------
# Real, end-to-end sandboxed execution -- genuinely builds the namespace
# sandbox and runs the real allow-listed command inside it.
# ---------------------------------------------------------------------------


@requires_real_sandbox
def test_real_bare_codecompass_against_a_zero_candidate_fixture_is_deterministic():
    result = execute_doc_example.execute("codecompass-no-candidates")
    assert result.passed, (result.stdout, result.stderr)
    assert result.exit_code == 0


@requires_real_sandbox
def test_real_budget_zero_against_toy_project_refuses_before_any_api_call():
    result = execute_doc_example.execute("codecompass-budget-0")
    assert result.passed, (result.stdout, result.stderr)
    assert result.exit_code == 1
    assert "exceeds --budget $0.00" in result.stdout


@requires_real_sandbox
def test_real_query_vendors_shows_both_fixture_vendors_as_used():
    result = execute_doc_example.execute("codecompass-query-vendors")
    assert result.passed, (result.stdout, result.stderr)
    assert "click" in result.stdout
    assert "requests" in result.stdout


@requires_real_sandbox
def test_real_pip_install_succeeds_fully_offline():
    result = execute_doc_example.execute("pip-install")
    assert result.passed, (result.stdout, result.stderr)
    assert result.exit_code == 0


@requires_real_sandbox
def test_real_isolation_preflight_failure_aborts_before_any_command_runs(monkeypatch):
    def _fail():
        raise RuntimeError("simulated preflight failure")

    monkeypatch.setattr(execute_doc_example, "run_isolation_preflight", _fail)
    with pytest.raises(RuntimeError, match="simulated preflight failure"):
        execute_doc_example.execute("codecompass-no-candidates")
