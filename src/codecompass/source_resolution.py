"""Upstream repository resolution and shallow clone, for grounded-
description generation. See decisions/0019 and decisions/0021.

Resolution itself reads only locally-available package metadata (each
adapter's `repository_url()`) — no registry network calls. Cloning does
need network access (`git`).
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

from codecompass.adapters.base import EcosystemAdapter


class SourceResolutionError(Exception):
    """Raised when a vendor's upstream repository can't be resolved (no
    repository field in local package metadata — decisions/0021's
    fail-loud case) or can't be cloned (`git` missing, network failure,
    invalid URL, or a declared monorepo subdirectory that doesn't exist
    in the clone). Never falls back to a registry source tarball.
    """


def resolve_and_clone(adapter: EcosystemAdapter, dest: Path) -> Path:
    """Resolve `adapter`'s vendor's repository and shallow-clone it into
    `dest`, replacing whatever was there. Returns the resolved source
    root within the clone — `dest` itself, or `dest / subdirectory` for
    an npm monorepo package (decisions/0021).
    """
    location = adapter.repository_url()
    if location is None:
        raise SourceResolutionError(
            f"{adapter.config.name}: no repository URL found in local "
            f"{adapter.config.ecosystem.value} package metadata"
        )
    _git_clone(location.url, dest)
    source_root = dest / location.subdirectory if location.subdirectory else dest
    if not source_root.is_dir():
        raise SourceResolutionError(
            f"{adapter.config.name}: cloned {location.url}, but declared "
            f"subdirectory {location.subdirectory!r} does not exist in it"
        )
    return source_root


def rmtree_best_effort(path: Path) -> bool:
    """`shutil.rmtree`, but a file `PermissionError` (most commonly a git
    clone's own read-only `.git/objects/pack/*` files, especially on
    Windows — `git` marks packfiles read-only after writing them) clears
    the read-only bit and retries once before giving up on that one file,
    rather than raising outright or (with plain `ignore_errors=True`)
    silently leaving files behind while the caller believes removal
    succeeded. Returns whether `path` is fully gone afterward, so the
    caller can decide how to react to a partial failure instead of
    assuming success. Shared by `_git_clone` (re-cloning over a vendor's
    previous clone) and `cli.undo` (Phase 18, `decisions/0036`) — the
    same underlying problem in two different callers, not duplicated
    logic.
    """

    def _on_error(func, sub_path, exc_info):  # noqa: ANN001
        del exc_info
        try:
            os.chmod(sub_path, stat.S_IWRITE)
            func(sub_path)
        except OSError:
            pass

    shutil.rmtree(path, onerror=_on_error)
    return not path.exists()


def _git_clone(url: str, dest: Path) -> None:
    """Shallow clone `url` into `dest`, replacing it if it already
    exists. Tests monkeypatch this per-module
    (`codecompass.source_resolution._git_clone`) to avoid a real network
    call, the same seam role `_run_json` plays for ecosystem adapters
    (decisions/0014).
    """
    if dest.exists() and not rmtree_best_effort(dest):
        raise SourceResolutionError(
            f"could not fully remove the previous clone at {dest} before "
            "re-cloning — a file is likely locked or still read-only; "
            "remove it manually and retry"
        )
    resolved = shutil.which("git")
    if resolved is None:
        raise SourceResolutionError(
            "required tool not found: 'git' — is it installed and on PATH?"
        )
    result = subprocess.run(
        [resolved, "clone", "--depth", "1", "--quiet", url, str(dest)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SourceResolutionError(f"git clone {url} failed: {result.stderr.strip()}")
