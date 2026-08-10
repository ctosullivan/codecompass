"""EcosystemAdapter interface and the shared subprocess seam.

See architecture/overview.md's "Adapter interface" section.
"""

from __future__ import annotations

import json
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

from depcompass.core import DepNode, VendorConfig


class AdapterError(Exception):
    """Raised when an ecosystem adapter can't produce a result — missing
    tool, non-zero subprocess exit, or unparseable output.
    """


class EcosystemAdapter(ABC):
    """Common interface every ecosystem (npm/Python/Cargo) implements.

    Adding a new ecosystem means writing one adapter class against this
    interface, not touching core logic. See decisions/0002.
    """

    def __init__(self, config: VendorConfig, project_root: Path) -> None:
        self.config = config
        self.project_root = project_root

    @abstractmethod
    def installed_version(self) -> str:
        """The currently installed version string for this vendor."""

    @abstractmethod
    def source_location(self) -> Path:
        """Filesystem path to the installed package's source directory.

        Used by Phase 4's sync to build vendor/<name>/src/ snapshots for
        FULL vendors — a copy, never a live reference (decisions/0004).
        """

    @abstractmethod
    def readme_and_api_surface(self) -> str:
        """Rendered README + extracted public API surface, as one string."""

    @abstractmethod
    def dependency_tree(self) -> DepNode:
        """The raw, fully-expanded dependency tree rooted at this vendor.

        NOT deduplicated — diamond dependencies appear in full, repeated,
        exactly as the underlying tool reports them. Deduplication into
        "see X above" back-references is Phase 3's tree-rendering
        concern, not this method's tree-construction concern.
        """


def _run_json(cmd: list[str], cwd: Path) -> dict | list:
    """Run cmd, parse stdout as JSON.

    This is the seam each adapter module imports and calls, and that
    tests monkeypatch per-module (e.g. depcompass.adapters.npm._run_json)
    to inject fixture JSON instead of invoking a real toolchain — see
    decisions/0014.
    """
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, check=False
        )
    except FileNotFoundError as exc:
        raise AdapterError(
            f"required tool not found: {cmd[0]!r} — is it installed and on PATH?"
        ) from exc
    if result.returncode != 0:
        raise AdapterError(
            f"{' '.join(cmd)} failed (exit {result.returncode}): "
            f"{result.stderr.strip()}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AdapterError(f"{' '.join(cmd)} produced invalid JSON: {exc}") from exc
