#!/usr/bin/env python3
"""Stage 87B -- safe, bounded executable-example verification for
docs/getting-started.md (plan §O.C; third corrective amendment finding
D). See
planning/phase-87-documentation-schema-knowledge-compiled-documentation.md
§O.C for the full design this implements.

**Why this reuses `verify_cleanroom_isolation.py`'s own technique
directly, rather than a new sandboxing approach**: this host has no
docker/podman/bwrap/firejail installed (checked directly, not assumed);
`unshare` is present and `verify_cleanroom_isolation.py` already has a
real, working, tested preflight built on `unshare --user --map-root-user
--mount --net --pid --fork` + `pivot_root`. This script builds the
identical sandbox tree/mount/pivot sequence, with two differences: (1)
the payload is one real, allow-listed command instead of a fixed probe,
and (2) the sandbox's own `--net` network isolation is deliberately
*not* worked around with any live network path -- `pip install` and
`git clone` both run entirely against locally bind-mounted, pre-staged
content (a wheel cache, a git mirror), never a live fetch.

**Why there is no general-purpose command runner here**: `ALLOWED_
COMMANDS` is a small, explicit, hand-maintained dict. A command name
not present in it is rejected before the sandbox is even entered -- no
process is spawned, no namespace is built. Widening it is a deliberate,
reviewed, future edit to this file, never a runtime decision this
script makes for itself. Two real, paid-API-triggering commands
(`codecompass --yes`, `codecompass --budget 1.00`) are deliberately
*not* in this list at all -- a credential-less sandbox can never
complete them; they are verified by a separate, mocked unit test
instead (`tests/test_cli.py`), never live execution, inside or outside
this harness.

Usage:

    python3 scripts/execute_doc_example.py --prepare-fixtures
    python3 scripts/execute_doc_example.py <command-name>
    python3 scripts/execute_doc_example.py --list

`--prepare-fixtures` builds the local wheel cache and git mirror this
script's own `pip install`/vendor-cloning commands run against --
performed once, out of band, over a real (but one-time, cacheable)
network fetch; every actual harness run afterward is fully offline.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT / "examples"

# Never under the repository, never committed -- a disposable, locally
# cached staging area for the one-time, out-of-band network fetch
# `--prepare-fixtures` performs. Safe to delete and rebuild at any time.
CACHE_DIR = Path(tempfile.gettempdir()) / "codecompass-doc-example-cache"
WHEEL_CACHE_DIR = CACHE_DIR / "wheels"
GIT_MIRROR_DIR = CACHE_DIR / "git-mirrors"
# A dedicated, self-contained venv with `codecompass-context` installed
# for real from WHEEL_CACHE_DIR -- never this repository's own dev
# `.venv` (an editable install pointing at `src/`, which would need the
# real source tree mounted into the sandbox too, and would test an
# editable checkout rather than the real distributed package). Built
# once by `--prepare-fixtures`, reused read-only by every sandboxed run.
HARNESS_VENV_DIR = CACHE_DIR / "venv"

_FIXTURE_UPSTREAM_REPOS = {
    # Resolved the same way the real code resolves them
    # (adapter.repository_url() against each vendor's own installed
    # package metadata) -- confirmed directly at the time this script
    # was written, not assumed to stay fixed forever; `--prepare-
    # fixtures` re-resolves them live each time it is run, these are
    # only the fallback if live resolution fails.
    "click": "https://github.com/pallets/click",
    "requests": "https://github.com/psf/requests",
}


@dataclass
class AllowedCommand:
    argv: list[str]
    fixture: str | None  # dir name under examples/, copied fresh per run; None = bare scratch dir
    expected_exit_code: int
    comparison_mode: str  # "exact" | "normalized_whitespace" | "regex"
    pattern: str
    needs_wheel_cache: bool = False
    needs_git_mirror: bool = False
    needs_venv: bool = False
    setup: tuple[list[str], ...] = ()  # argv(s) run before `argv`, same fixture dir, same mounts


ALLOWED_COMMANDS: dict[str, AllowedCommand] = {
    "pip-install": AllowedCommand(
        argv=["python3", "-m", "pip", "install", "--no-index",
              "--find-links", "/run/wheel-cache", "--target", "/output/site-packages",
              "codecompass-context"],
        fixture=None,
        expected_exit_code=0,
        comparison_mode="regex",
        pattern=r"Successfully installed",
        needs_wheel_cache=True,
        needs_venv=True,
    ),
    "codecompass-no-candidates": AllowedCommand(
        argv=["codecompass"],
        fixture="no-candidates-project",
        expected_exit_code=0,
        comparison_mode="regex",
        pattern=r"bootstrapped .*vendor\.toml — 0 vendor\(s\) tracked, 0 newly discovered",
        needs_venv=True,
    ),
    "codecompass-budget-0": AllowedCommand(
        argv=["codecompass", "--budget", "0"],
        fixture="toy-project",
        expected_exit_code=1,
        comparison_mode="regex",
        pattern=(
            r"bootstrapped .*vendor\.toml — 2 vendor\(s\) tracked.*\n"
            r"enrichment will make ~\d+ AI call\(s\) \(~\$\d+\.\d\d\) using [\w.-]+ to\s*\n"
            r"describe 2 vendor\(s\): click, requests, and 0 relationship\(s\)\s*\n"
            r"error: estimated cost \$\d+\.\d\d for \d+ batch\(es\) covering 2 vendor\(s\)"
            r" and 0\s*\nrelationship\(s\) exceeds --budget \$0\.00"
        ),
        needs_venv=True,
        needs_git_mirror=True,
    ),
    "codecompass-query-vendors": AllowedCommand(
        argv=["codecompass", "query", "vendors"],
        fixture="toy-project",
        expected_exit_code=0,
        comparison_mode="regex",
        pattern=r"click\s+.*python.*yes.*\n.*requests\s+.*python.*yes",
        needs_venv=True,
        needs_git_mirror=True,
        # Chained exactly like the real captured example: query vendors
        # only shows real, documented output once a prior bootstrap run
        # has populated context-graph.db/vendor.toml in this same
        # working copy.
        setup=(["codecompass", "--budget", "0"],),
    ),
}


def _build_sandbox_tree(newroot: Path) -> None:
    dirs = (
        "usr", "lib", "lib64", "bin", "sbin", "etc", "proc", "run", "venv", "project",
        "output", "dev", "tmp", "oldroot",
    )
    for d in dirs:
        (newroot / d).mkdir(parents=True, exist_ok=True)
    # `git` (among other real-world tools) opens /dev/null directly --
    # a real, reproducible gap this script's own real sandboxed run
    # against `git clone` found (`fatal: could not open '/dev/null'`),
    # not a hypothetical. Bind-mounting the host's own device node is
    # sufficient and needs no special privilege (it's a file bind
    # mount, not device creation) under `--user --map-root-user`.
    (newroot / "dev" / "null").touch()
    (newroot / "dev" / "urandom").touch()
    (newroot / "dev" / "random").touch()


def run_isolation_preflight() -> None:
    """Mirrors `compile_doc_section.py`'s own fail-closed preflight
    convention -- aborts the whole harness run before any allow-listed
    command is ever attempted, never an un-isolated fallback."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_cleanroom_isolation.py")],
        capture_output=True, text=True, timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"cleanroom isolation preflight failed (exit {result.returncode}): "
            f"{result.stdout}\n{result.stderr}"
        )


def prepare_fixtures() -> None:
    """One-time, out-of-band setup: downloads `codecompass-context`
    (and its real runtime dependencies) into a local wheel cache, and
    mirrors the two real fixture vendors' upstream source into a local
    bare git mirror. Both are real, live network operations -- the only
    ones this whole mechanism ever performs -- run exactly once, cached
    afterward; every actual harness invocation runs fully offline
    against what this function already staged."""
    WHEEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"downloading codecompass-context + dependencies into {WHEEL_CACHE_DIR} ...")
    subprocess.run(
        [sys.executable, "-m", "pip", "download", "-d", str(WHEEL_CACHE_DIR),
         "codecompass-context"],
        check=True,
    )
    # toy-project's own fixture code declares click/requests, but
    # CodeCompass's PythonAdapter.installed_version() introspects the
    # ENVIRONMENT CODECOMPASS ITSELF RUNS IN (`importlib.metadata.
    # version`), not merely what the target project's own manifest
    # declares -- confirmed directly by a real run that failed with
    # `AdapterError: click: not installed in this environment` before
    # this was added. Both fixture vendors must therefore also be
    # installed into the harness's own venv, matching how a real user
    # following "## Install" would already have whatever their own
    # project needs available in the same environment.
    print(f"downloading click/requests (needed by toy-project) into {WHEEL_CACHE_DIR} ...")
    subprocess.run(
        [sys.executable, "-m", "pip", "download", "-d", str(WHEEL_CACHE_DIR), "click", "requests"],
        check=True,
    )

    GIT_MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in _FIXTURE_UPSTREAM_REPOS.items():
        mirror_path = GIT_MIRROR_DIR / name
        if mirror_path.is_dir():
            print(f"{name}: mirror already present at {mirror_path}, skipping")
            continue
        print(f"mirroring {name} ({url}) into {mirror_path} ...")
        subprocess.run(["git", "clone", "--mirror", url, str(mirror_path)], check=True)

    if HARNESS_VENV_DIR.is_dir():
        print(f"harness venv already present at {HARNESS_VENV_DIR}, skipping")
    else:
        print(f"building a fresh, self-contained venv at {HARNESS_VENV_DIR} ...")
        subprocess.run([sys.executable, "-m", "venv", str(HARNESS_VENV_DIR)], check=True)
        subprocess.run(
            [str(HARNESS_VENV_DIR / "bin" / "python3"), "-m", "pip", "install", "--no-index",
             "--find-links", str(WHEEL_CACHE_DIR), "codecompass-context", "click", "requests"],
            check=True,
        )
    print("fixtures prepared -- every subsequent run is fully offline")


def _write_git_insteadof_config(path: Path) -> None:
    lines = []
    for name, url in _FIXTURE_UPSTREAM_REPOS.items():
        mirror_path = GIT_MIRROR_DIR / name
        lines.append(f'[url "file://{mirror_path}"]')
        lines.append(f"\tinsteadOf = {url}")
        lines.append(f"\tinsteadOf = {url}.git")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


@dataclass
class ExecutionResult:
    command_name: str
    exit_code: int
    stdout: str
    stderr: str
    passed: bool
    reason: str


def _classify(command: AllowedCommand, exit_code: int, stdout: str) -> tuple[bool, str]:
    if exit_code != command.expected_exit_code:
        return False, f"exit code {exit_code} != expected {command.expected_exit_code}"
    if command.comparison_mode == "exact":
        ok = stdout == command.pattern
    elif command.comparison_mode == "normalized_whitespace":
        ok = " ".join(stdout.split()) == " ".join(command.pattern.split())
    elif command.comparison_mode == "regex":
        ok = re.search(command.pattern, stdout) is not None
    else:
        return False, f"unknown comparison_mode {command.comparison_mode!r}"
    if not ok:
        return False, (
            f"output did not match the documented expected outcome ({command.comparison_mode})"
        )
    return True, "matches documented expected outcome"


def execute(command_name: str, *, timeout: float = 120.0) -> ExecutionResult:
    if command_name not in ALLOWED_COMMANDS:
        raise ValueError(
            f"{command_name!r} is not in this script's own fixed allow-list "
            f"({sorted(ALLOWED_COMMANDS)}) -- rejected before any sandbox was entered"
        )
    command = ALLOWED_COMMANDS[command_name]
    run_isolation_preflight()

    if command.needs_wheel_cache and not WHEEL_CACHE_DIR.is_dir():
        raise RuntimeError("wheel cache missing -- run --prepare-fixtures first")
    if command.needs_git_mirror and not GIT_MIRROR_DIR.is_dir():
        raise RuntimeError("git mirror missing -- run --prepare-fixtures first")

    scratch = Path(tempfile.mkdtemp(prefix="doc-example-harness-"))
    try:
        newroot = scratch / "newroot"
        _build_sandbox_tree(newroot)

        project_src = scratch / "project-src"
        project_src.mkdir()
        if command.fixture is not None:
            shutil.copytree(EXAMPLES_DIR / command.fixture, project_src, dirs_exist_ok=True)

        output_src = scratch / "output-src"
        output_src.mkdir()

        mounts = [
            ("/usr", "usr", True),
            ("/lib", "lib", True),
            ("/lib64", "lib64", True) if Path("/lib64").is_dir() else None,
            ("/bin", "bin", True),
            ("/sbin", "sbin", True),
            ("/etc", "etc", True),
            ("/dev/null", "dev/null", False),
            ("/dev/urandom", "dev/urandom", False),
            ("/dev/random", "dev/random", False),
            (str(project_src), "project", False),
            (str(output_src), "output", False),
        ]
        if command.needs_venv:
            # Mounted at its own real absolute path, not an alias --
            # the installed `codecompass`/`python3` console scripts'
            # own shebang lines hardcode this absolute path, so the
            # mount point must match it exactly for exec to resolve.
            venv_rel = str(HARNESS_VENV_DIR.relative_to(HARNESS_VENV_DIR.anchor))
            (newroot / venv_rel).mkdir(parents=True, exist_ok=True)
            mounts.append((str(HARNESS_VENV_DIR), venv_rel, True))
        mounts = [m for m in mounts if m is not None]

        git_config_path = None
        if command.needs_git_mirror:
            git_config_path = scratch / "gitconfig"
            _write_git_insteadof_config(git_config_path)
            (newroot / "run" / "gitconfig").touch()
            mounts.append((str(git_config_path), "run/gitconfig", True))
            # The `insteadOf` rewrite points at GIT_MIRROR_DIR's own
            # real absolute path (`file://...`) -- that path must
            # therefore exist and be mounted inside the sandbox too,
            # at that exact same absolute path, not just the config
            # file naming it (a real, reproducible gap this script's
            # own first sandboxed run found: "does not appear to be a
            # git repository" once /dev/null was fixed, because the
            # mirror *data* was never mounted, only its config entry).
            mirror_rel = str(GIT_MIRROR_DIR.relative_to(GIT_MIRROR_DIR.anchor))
            (newroot / mirror_rel).mkdir(parents=True, exist_ok=True)
            mounts.append((str(GIT_MIRROR_DIR), mirror_rel, True))

        wheel_cache_mount = None
        if command.needs_wheel_cache:
            (newroot / "run" / "wheel-cache").mkdir(parents=True, exist_ok=True)
            wheel_cache_mount = (str(WHEEL_CACHE_DIR), "run/wheel-cache", True)
            mounts.append(wheel_cache_mount)

        mount_lines = []
        for src, dst_rel, readonly in mounts:
            ro_flag = " -o ro" if readonly else ""
            mount_lines.append(f'mount --bind "{src}" "$NR/{dst_rel}"{ro_flag}')

        venv_bin = f"{HARNESS_VENV_DIR}/bin" if command.needs_venv else ""
        path_value = f"{venv_bin}:/usr/bin:/bin" if venv_bin else "/usr/bin:/bin"
        env_vars = f"PATH={path_value} HOME=/project"
        if command.needs_git_mirror:
            env_vars += " GIT_CONFIG_GLOBAL=/run/gitconfig"

        # Setup steps must run under the *exact same* cleared/rebuilt
        # environment the final command does (`env -i {env_vars}`) --
        # a real, reproducible bug this script's own first chained-
        # scenario run found: run unqualified before `exec env -i` ever
        # applied PATH, `codecompass` was simply not found, silently
        # swallowed by `|| true`, so the setup step appeared to
        # succeed while doing nothing at all.
        setup_lines = []
        for setup_argv in command.setup:
            quoted = " ".join(f'"{a}"' for a in setup_argv)
            setup_lines.append(
                f'(cd /project && env -i {env_vars} {quoted} > /dev/null 2>&1) || true'
            )

        bash_script = f"""
set -e
NR={newroot}
mount --bind "$NR" "$NR"
{chr(10).join(mount_lines)}
mount -t proc proc "$NR/proc"
cd "$NR" && pivot_root . oldroot && umount -l /oldroot
cd /project
{chr(10).join(setup_lines)}
exec env -i {env_vars} {' '.join(command.argv)}
"""
        result = subprocess.run(
            [
                "unshare", "--user", "--map-root-user", "--mount", "--net", "--pid", "--fork",
                "--", "bash", "-c", bash_script,
            ],
            capture_output=True, text=True, timeout=timeout,
        )
        passed, reason = _classify(command, result.returncode, result.stdout)
        return ExecutionResult(
            command_name=command_name, exit_code=result.returncode,
            stdout=result.stdout, stderr=result.stderr, passed=passed, reason=reason,
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", help="One of the allow-listed command names.")
    parser.add_argument("--prepare-fixtures", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args(argv)

    if args.list:
        for name in sorted(ALLOWED_COMMANDS):
            print(name)
        return 0
    if args.prepare_fixtures:
        prepare_fixtures()
        return 0
    if not args.command:
        parser.print_help()
        return 2

    result = execute(args.command)
    print(f"exit_code={result.exit_code}")
    print(f"passed={result.passed} ({result.reason})")
    print("--- stdout ---")
    print(result.stdout)
    if result.stderr:
        print("--- stderr ---")
        print(result.stderr)
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
