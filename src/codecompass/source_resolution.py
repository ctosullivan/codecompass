"""Upstream repository resolution and shallow clone, for grounded-
description generation. See decisions/0019 and decisions/0021.

Resolution itself reads only locally-available package metadata (each
adapter's `repository_url()`) — no registry network calls. Cloning does
need network access (`git`).
"""

from __future__ import annotations

import shutil
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


def _git_clone(url: str, dest: Path) -> None:
    """Shallow clone `url` into `dest`, replacing it if it already
    exists. Tests monkeypatch this per-module
    (`codecompass.source_resolution._git_clone`) to avoid a real network
    call, the same seam role `_run_json` plays for ecosystem adapters
    (decisions/0014).
    """
    if dest.exists():
        shutil.rmtree(dest)
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
