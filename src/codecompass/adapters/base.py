"""EcosystemAdapter interface and the shared subprocess seam.

See architecture/overview.md's "Adapter interface" section.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

from codecompass.core import DepNode, RepositoryLocation, VendorConfig
from codecompass.filetree import iter_source_files
from codecompass.symbols import Symbol, extract_symbols_for_file


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
    def repository_url(self) -> RepositoryLocation | None:
        """The vendor's upstream source repository, resolved from
        locally-available package metadata only — never a network call
        (decisions/0021). Returns `None` if this ecosystem's local
        metadata carries no repository information for this package;
        callers (`codecompass.source_resolution`) treat that as a
        fail-loud condition, not a fallback trigger.
        """

    @abstractmethod
    def dependency_tree(self) -> DepNode:
        """The raw, fully-expanded dependency tree rooted at this vendor.

        NOT deduplicated — diamond dependencies appear in full, repeated,
        exactly as the underlying tool reports them. Deduplication into
        "see X above" back-references is Phase 3's tree-rendering
        concern, not this method's tree-construction concern.
        """

    def symbols(self) -> list[Symbol]:
        """Structured public-API-surface symbols for this vendor, for
        `context-graph.db`'s own `symbols` table (Phase 62). **Concrete,
        not abstract** — a future adapter that doesn't implement
        structured extraction isn't forced to (no `TypeError` at
        construction), matching this project's own "safe default over
        forced complexity" posture elsewhere (`RELATION_LABELS`' `'other'`
        fallback, `dev_only` defaulting `False` for pipdeptree, etc.).

        The default walks this vendor's own source tree and dispatches
        each file through `extract_symbols_for_file` by ecosystem — the
        exact walk+extract pairing `sync.py::rebuild_project_graph` used
        to perform itself (as `_collect_vendor_symbols`) for every
        in-process ecosystem (npm/Python/Cargo); relocated here so the
        caller no longer needs to know which ecosystems support
        structured extraction and which don't. `HaskellAdapter` (an
        **external-process** adapter — `extract_symbols_for_file` has no
        Haskell branch, and never will: real Haskell symbol extraction
        lives in `codecompass-adaptor-haskell`, not `src/codecompass/`)
        overrides this with its own conversion from the external
        adapter's already-computed `symbols` wire data.
        """
        result: list[Symbol] = []
        for path in iter_source_files(self.source_location()):
            result.extend(extract_symbols_for_file(path, self.config.ecosystem))
        return result


def _run_json(cmd: list[str], cwd: Path) -> dict | list:
    """Run cmd, parse stdout as JSON.

    This is the seam each adapter module imports and calls, and that
    tests monkeypatch per-module (e.g. codecompass.adapters.npm._run_json)
    to inject fixture JSON instead of invoking a real toolchain — see
    decisions/0014.

    Resolves ``cmd[0]`` via ``shutil.which`` before invoking it. This
    isn't just a nicer error message: several real-world tools this seam
    invokes (notably npm) are ``.cmd`` shims on Windows, which
    ``CreateProcess`` can't launch directly by bare name without a shell
    — a well-known Windows-specific `subprocess` gotcha. Resolving first
    gives the full, correctly-extensioned path, so plain ``shell=False``
    works cross-platform without needing a shell (and the injection
    surface that comes with one).
    """
    resolved = shutil.which(cmd[0])
    if resolved is None:
        raise AdapterError(
            f"required tool not found: {cmd[0]!r} — is it installed and on PATH?"
        )
    try:
        result = subprocess.run(
            [resolved, *cmd[1:]], cwd=cwd, capture_output=True, text=True, check=False
        )
    except OSError as exc:
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
