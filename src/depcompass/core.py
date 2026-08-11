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
    `gap_analysis`/`conversational_overview`/`action_pointer_file`/
    `action_pointer_note` by the AI-gated step (Phase 5, only for `depth =
    full` vendors with `context_path` set) — a failure there sets
    `gap_analysis_error` instead, rather than leaving everything silently
    `None` with no way to tell "not applicable" from "failed".

    Does not carry staleness information — `depcompass.staleness` (Phase
    6) reads persisted per-vendor `CLAUDE.md` files directly rather than
    building a `VendorDigest`, the same cheap-and-side-effect-free pattern
    `index.py` (Phase 4) already established, and returns its own
    `VendorStaleness` type. An earlier `is_stale` stub on this class was
    removed in Phase 6 once that pattern made it clear no code path would
    ever populate it.
    """

    config: VendorConfig
    installed_version: str
    file_tree: str | None = None
    dep_tree: str | None = None
    api_surface: str | None = None
    gap_analysis: str | None = None
    conversational_overview: str | None = None
    gap_analysis_error: str | None = None
    action_pointer_file: str | None = None
    action_pointer_note: str | None = None
    side_effects: list[str] = field(default_factory=list)
