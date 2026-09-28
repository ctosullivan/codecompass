"""Git repository topology detection — worktrees and submodules.

Phase 76. A pure, graph-agnostic detection module: mirrors `discovery.py`/
`usage.py`/`spec_docs.py`'s own shape — `sync.py` is the only place that
converts this module's own plain dataclasses into `graph.py` row types.

Establishes and keeps distinct three separate paths a naive implementation
could otherwise conflate: the *invocation root* (`project_root`, wherever
CodeCompass was actually run from — may be a subdirectory of a Git
worktree), the *Git worktree root* (`git rev-parse --show-toplevel`), and
the *Git common directory* (`git rev-parse --git-common-dir` — identical
across every worktree of one repository, the canonical identity this
module uses). See planning/phase-76-git-repository-topology.md §5-§8 for
the full design rationale, including why no Git feature newer than
`git worktree`/`--git-common-dir` themselves (Git 2.5, July 2015) is ever
required.

`detect_git_topology` never returns `None` and never raises — its own
`status` field tells the caller how much of the rest to trust (§6):
`detected` (repository/worktree-list/submodule-list enumeration all
succeeded structurally), `not_git` (confidently not a Git repository),
`unavailable` (git missing, no working tree/bare repository, or any other
detection failure), `partial` (repository identity established but a
subsequent enumeration step failed unexpectedly). This is a *whole-pass*
status, distinct from the per-row nullable fields below, which represent
per-fact uncertainty within a structure that *was* successfully
enumerated (e.g. a declared submodule whose pinned commit can't currently
be resolved) — neither ever stands in for the other.

A fifth, "not yet indexed" state (an existing database that has never
been synced under Phase-76-aware code) is deliberately *not* a value
`TopologyStatus` takes — it is a query-layer concept (`cli.py`), keyed on
the absence of a persisted `meta.git_topology_status` row. This module's
own output is only ever consulted while a sync is actually running, so it
never needs to represent "I have not run yet."
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

_GIT_TIMEOUT_SECONDS = 10


class TopologyStatus(StrEnum):
    DETECTED = "detected"
    NOT_GIT = "not_git"
    UNAVAILABLE = "unavailable"
    PARTIAL = "partial"


@dataclass(frozen=True)
class WorktreeInfo:
    """One worktree of a repository — `is_current=True` for the one
    `detect_git_topology` was actually invoked against, `False` for a
    sibling observed via `git worktree list`. `is_dirty` is only ever
    populated for the current worktree: probing a sibling's workspace
    state would need an extra subprocess call per sibling against a path
    that may be stale, unmounted, or removed, and would imply a kind of
    live authority over another checkout's mutable state this module
    never claims — a stated, permanent limitation of the data contract,
    not a transient gap.
    """

    path: str
    is_current: bool
    branch: str | None
    is_detached: bool
    head_commit: str | None
    is_dirty: bool | None
    is_bare: bool
    is_locked: bool
    is_prunable: bool


@dataclass(frozen=True)
class SubmoduleInfo:
    """One submodule `.gitmodules` declares. Always emitted once declared,
    regardless of how much else is resolvable — `path` and `is_path_safe`
    are the only fields guaranteed meaningful; every other field is
    allowed to be honestly unset rather than forcing the row out of
    existence entirely (a materially different posture from silently
    dropping a submodule the moment one fact about it can't be
    determined).
    """

    path: str
    is_path_safe: bool
    child_repository_url: str | None
    pinned_commit: str | None
    is_initialized: bool | None
    checked_out_commit: str | None
    revision_matches_pin: bool | None
    child_branch: str | None
    child_is_dirty: bool | None


@dataclass(frozen=True)
class RepositoryTopology:
    status: TopologyStatus
    reason: str | None
    invocation_root: str
    worktree_root: str | None
    common_dir: str | None
    origin_url: str | None
    worktrees: tuple[WorktreeInfo, ...]
    submodules: tuple[SubmoduleInfo, ...]


def _run_git(
    args: list[str], cwd: Path
) -> subprocess.CompletedProcess[str]:
    """`git <args>` with `cwd` as the working directory (used instead of
    `-C` so callers can pass a `Path` uniformly); never raises on a
    non-zero exit — every caller inspects `.returncode`/`.stderr` itself,
    since a git failure here is ordinary, expected control flow (a
    missing gitlink, a non-repository, ...), not an exceptional one.
    """
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=_GIT_TIMEOUT_SECONDS,
    )


def sanitize_git_url(url: str) -> str:
    """Strips any password/token component from a parseable, URI-form Git
    remote URL before it is ever placed in a dataclass, persisted to
    `context-graph.db`, or shown in any CLI/JSON/Skill output.

    Scheme-aware, not scheme-blind: for `http`/`https`, the *entire*
    userinfo component is stripped, including a bare username with no
    password — a bare token used as a username is a common, real
    credential-leak pattern for these schemes (GitHub PATs, GitLab CI job
    tokens). For any other recognized URI scheme (`ssh`, `git`, ...), only
    an actual password component is stripped; a bare username is ordinary,
    non-secret connection identity (almost always the public `git`
    convention, e.g. `ssh://git@host/...`) and is preserved. SCP-like
    syntax (`git@host:org/repo.git`, no `scheme://`) has no parseable
    userinfo at all under `urllib.parse.urlsplit` — confirmed live during
    planning — and is therefore left completely untouched, not because it
    is assumed safe, but because there is nothing here to identify as a
    username/password pair to strip.

    The invariant this function exists to guarantee: CodeCompass never
    persists or prints a password/token component of a parseable Git
    remote URL. It does not claim to detect every conceivable
    credential-bearing string shape (planning/phase-76-git-repository-topology.md
    §16's own explicit non-goal).
    """
    parsed = urlsplit(url)
    if not parsed.scheme or not parsed.hostname:
        return url
    if not parsed.username and not parsed.password:
        return url
    if parsed.scheme in ("http", "https"):
        netloc = parsed.hostname
    else:
        netloc = f"{parsed.username}@{parsed.hostname}" if parsed.username else parsed.hostname
    if parsed.port:
        netloc += f":{parsed.port}"
    return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))


def _strip_branch_ref_prefix(ref: str) -> str:
    """`git worktree list --porcelain`'s own `branch` line always gives a
    full ref (`refs/heads/main`) — CodeCompass stores the short name
    (`main`), stripping the well-known `refs/heads/` prefix. A branch ref
    that doesn't use that prefix (real but exceedingly uncommon) is
    returned unstripped rather than mis-parsed.
    """
    prefix = "refs/heads/"
    return ref[len(prefix):] if ref.startswith(prefix) else ref


_NULL_SHA = "0" * 40


def _normalize_head_commit(head: str | None) -> str | None:
    """`git worktree list --porcelain`'s own `HEAD` line reports the
    all-zero SHA for a truly unborn branch (no commits yet) — confirmed
    live — rather than omitting the line; CodeCompass normalizes this to
    `None`, matching every other "no commits yet" representation in this
    module (e.g. a submodule's own `checked_out_commit`).
    """
    if head is None or head == _NULL_SHA:
        return None
    return head


def _empty_topology(
    project_root: Path, status: TopologyStatus, reason: str | None
) -> RepositoryTopology:
    return RepositoryTopology(
        status=status,
        reason=reason,
        invocation_root=str(project_root),
        worktree_root=None,
        common_dir=None,
        origin_url=None,
        worktrees=(),
        submodules=(),
    )


def detect_git_topology(project_root: Path) -> RepositoryTopology:
    """Detects the Git repository/worktree/submodule topology visible from
    `project_root`. Always returns a `RepositoryTopology` — never `None`,
    never raises. See this module's own docstring for the status model.
    """
    project_root = project_root.resolve()
    if shutil.which("git") is None:
        return _empty_topology(
            project_root, TopologyStatus.UNAVAILABLE, "git executable not found on PATH"
        )

    try:
        result = _run_git(["rev-parse", "--show-toplevel", "--git-common-dir"], project_root)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return _empty_topology(project_root, TopologyStatus.UNAVAILABLE, str(exc))

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "not a git repository" in stderr:
            return _empty_topology(project_root, TopologyStatus.NOT_GIT, None)
        if "must be run in a work tree" in stderr:
            return _empty_topology(
                project_root,
                TopologyStatus.UNAVAILABLE,
                "no working tree (bare repository) — Git topology requires a checkout",
            )
        return _empty_topology(
            project_root, TopologyStatus.UNAVAILABLE, stderr or "git rev-parse failed"
        )

    lines = result.stdout.splitlines()
    if len(lines) < 2:
        return _empty_topology(
            project_root, TopologyStatus.UNAVAILABLE, "unexpected rev-parse output"
        )
    worktree_root = Path(lines[0]).resolve()
    raw_common_dir = lines[1]
    common_dir = (
        Path(raw_common_dir)
        if Path(raw_common_dir).is_absolute()
        else (project_root / raw_common_dir)
    ).resolve()

    origin_url = _detect_origin_url(worktree_root)

    status = TopologyStatus.DETECTED
    reason: str | None = None

    worktrees, worktree_reason = _detect_worktrees(worktree_root)
    if worktree_reason is not None:
        status = TopologyStatus.PARTIAL
        reason = worktree_reason

    submodules, submodule_reason = _detect_submodules(worktree_root)
    if submodule_reason is not None and reason is None:
        status = TopologyStatus.PARTIAL
        reason = submodule_reason

    return RepositoryTopology(
        status=status,
        reason=reason,
        invocation_root=str(project_root),
        worktree_root=str(worktree_root),
        common_dir=str(common_dir),
        origin_url=origin_url,
        worktrees=tuple(worktrees),
        submodules=tuple(submodules),
    )


def _detect_origin_url(worktree_root: Path) -> str | None:
    try:
        result = _run_git(["remote", "get-url", "origin"], worktree_root)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    return sanitize_git_url(url) if url else None


def _detect_worktrees(worktree_root: Path) -> tuple[list[WorktreeInfo], str | None]:
    try:
        result = _run_git(["worktree", "list", "--porcelain"], worktree_root)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [], f"could not enumerate worktrees: {exc}"
    if result.returncode != 0:
        return [], f"could not enumerate worktrees: {result.stderr.strip()}"

    worktrees: list[WorktreeInfo] = []
    resolved_root = worktree_root.resolve()
    found_current = False
    for block in result.stdout.strip("\n").split("\n\n"):
        if not block.strip():
            continue
        fields = {}
        flags: set[str] = set()
        path: Path | None = None
        for line in block.splitlines():
            if line.startswith("worktree "):
                path = Path(line[len("worktree "):]).resolve()
            elif line.startswith("HEAD "):
                fields["head"] = line[len("HEAD "):]
            elif line.startswith("branch "):
                fields["branch"] = _strip_branch_ref_prefix(line[len("branch "):])
            elif line == "detached":
                flags.add("detached")
            elif line == "bare":
                flags.add("bare")
            elif line.startswith("locked"):
                flags.add("locked")
            elif line.startswith("prunable"):
                flags.add("prunable")
        if path is None:
            continue
        is_current = path == resolved_root
        if is_current:
            found_current = True
        is_dirty = _detect_dirty(path) if is_current else None
        worktrees.append(
            WorktreeInfo(
                path=str(path),
                is_current=is_current,
                branch=fields.get("branch"),
                is_detached="detached" in flags,
                head_commit=_normalize_head_commit(fields.get("head")),
                is_dirty=is_dirty,
                is_bare="bare" in flags,
                is_locked="locked" in flags,
                is_prunable="prunable" in flags,
            )
        )

    if not found_current:
        return worktrees, "current worktree not found in its own worktree list"
    return worktrees, None


def _detect_dirty(path: Path) -> bool | None:
    try:
        result = _run_git(["status", "--porcelain"], path)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return bool(result.stdout.strip())


def _detect_submodules(worktree_root: Path) -> tuple[list[SubmoduleInfo], str | None]:
    gitmodules_path = worktree_root / ".gitmodules"
    if not gitmodules_path.is_file():
        return [], None

    try:
        result = _run_git(["config", "-f", ".gitmodules", "--list", "-z"], worktree_root)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [], f"could not read .gitmodules: {exc}"
    if result.returncode != 0:
        return [], f"could not read .gitmodules: {result.stderr.strip()}"

    entries: dict[str, dict[str, str]] = {}
    tokens = result.stdout.split("\x00")
    for token in tokens:
        if not token or "\n" not in token:
            continue
        key, _, value = token.partition("\n")
        if not key.startswith("submodule."):
            continue
        rest = key[len("submodule."):]
        name, _, field = rest.rpartition(".")
        if field not in ("path", "url"):
            continue
        entries.setdefault(name, {})[field] = value

    submodules: list[SubmoduleInfo] = []
    for entry in entries.values():
        declared_path = entry.get("path")
        if not declared_path:
            continue
        submodules.append(_build_submodule_info(worktree_root, declared_path, entry.get("url")))
    return submodules, None


def _build_submodule_info(
    worktree_root: Path, declared_path: str, url: str | None
) -> SubmoduleInfo:
    resolved = (worktree_root / declared_path).resolve()
    is_path_safe = resolved.is_relative_to(worktree_root.resolve())

    sanitized_url = sanitize_git_url(url) if url else None

    if not is_path_safe:
        return SubmoduleInfo(
            path=declared_path,
            is_path_safe=False,
            child_repository_url=sanitized_url,
            pinned_commit=None,
            is_initialized=None,
            checked_out_commit=None,
            revision_matches_pin=None,
            child_branch=None,
            child_is_dirty=None,
        )

    pinned_commit = _detect_pinned_commit(worktree_root, declared_path)
    is_initialized = (resolved / ".git").exists()

    checked_out_commit: str | None = None
    child_branch: str | None = None
    child_is_dirty: bool | None = None
    if is_initialized:
        checked_out_commit = _rev_parse_head(resolved)
        child_branch = _detect_child_branch(resolved)
        child_is_dirty = _detect_dirty(resolved)

    revision_matches_pin = (
        checked_out_commit == pinned_commit
        if pinned_commit is not None and checked_out_commit is not None
        else None
    )

    return SubmoduleInfo(
        path=declared_path,
        is_path_safe=True,
        child_repository_url=sanitized_url,
        pinned_commit=pinned_commit,
        is_initialized=is_initialized,
        checked_out_commit=checked_out_commit,
        revision_matches_pin=revision_matches_pin,
        child_branch=child_branch,
        child_is_dirty=child_is_dirty,
    )


def _detect_pinned_commit(worktree_root: Path, declared_path: str) -> str | None:
    try:
        result = _run_git(["ls-tree", "HEAD", "--", declared_path], worktree_root)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    # `<mode> commit <sha>\t<path>` -- a gitlink entry.
    fields = result.stdout.strip().split("\t", 1)[0].split()
    if len(fields) != 3 or fields[1] != "commit":
        return None
    return fields[2]


def _rev_parse_head(path: Path) -> str | None:
    try:
        result = _run_git(["rev-parse", "HEAD"], path)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _detect_child_branch(path: Path) -> str | None:
    try:
        result = _run_git(["symbolic-ref", "--short", "HEAD"], path)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None
