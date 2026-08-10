"""Core, ecosystem-agnostic data models for depcompass.

See architecture/overview.md's "Core data model" section for the design
rationale behind these types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Ecosystem(StrEnum):
    """Package ecosystem a vendor belongs to."""

    NPM = "npm"
    PYTHON = "python"
    CARGO = "cargo"


class Depth(StrEnum):
    """How much detail depcompass generates for a vendor.

    Set per vendor (see decisions/0001), not globally: SURFACE is free
    metadata + API surface; FULL adds a pinned source snapshot and an
    AI-generated gap analysis.
    """

    SURFACE = "surface"
    FULL = "full"


@dataclass(frozen=True)
class VendorConfig:
    """One `[[vendor]]` entry from vendor.toml."""

    name: str
    ecosystem: Ecosystem
    depth: Depth
    context_path: str | None = None

    def __post_init__(self) -> None:
        if self.depth is Depth.FULL and not self.context_path:
            raise ValueError(
                f"vendor {self.name!r}: depth='full' requires context_path "
                "— without it, gap analysis has no basis to judge what "
                "counts as a gap (see architecture/overview.md)"
            )


@dataclass
class DepNode:
    """One node in a dependency tree, ecosystem-agnostic.

    Built incrementally by tree generation (Phase 3), so this type is
    intentionally mutable rather than frozen.
    """

    name: str
    version: str
    children: list[DepNode] = field(default_factory=list)
    dev_only: bool = False
    side_effects: list[str] = field(default_factory=list)


@dataclass
class VendorDigest:
    """Aggregate output of generating a single vendor's documentation.

    Populated incrementally across later phases: `file_tree`/`dep_tree` by
    tree generation (Phase 3), `api_surface` by adapters (Phase 2),
    `side_effects` by `sync_vendor` (Phase 4, copied from the dependency
    tree's root `DepNode.side_effects` — e.g. npm postinstall scripts —
    for the per-vendor `CLAUDE.md`'s Known Gotchas section),
    `gap_analysis` by the AI-gated step (Phase 5). `is_stale` stays a
    documented stub — it raises until `staleness.check()` (Phase 6) sets
    it; a missing implementation there is not a bug to "fix" with a
    default.
    """

    config: VendorConfig
    installed_version: str
    file_tree: str | None = None
    dep_tree: str | None = None
    api_surface: str | None = None
    gap_analysis: str | None = None
    side_effects: list[str] = field(default_factory=list)
    _stale: bool | None = field(default=None, repr=False, init=False)

    @property
    def is_stale(self) -> bool:
        if self._stale is None:
            raise NotImplementedError(
                "VendorDigest.is_stale is unpopulated until staleness.check() "
                "(Phase 6) runs — this is a documented stub, not a bug."
            )
        return self._stale

    @is_stale.setter
    def is_stale(self, value: bool) -> None:
        self._stale = value
