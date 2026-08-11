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
    """One `[[vendor]]` entry from vendor.toml.

    `depth = FULL` no longer requires any companion field (`context_path`
    was removed in Phase 7 — decisions/0019 — since grounded-description
    generation is sourced from the vendor's own upstream repository, not
    from a project-supplied README/spec).
    """

    name: str
    ecosystem: Ecosystem
    depth: Depth


@dataclass(frozen=True)
class RepositoryLocation:
    """Where a vendor's upstream source repository actually lives —
    resolved from locally-available package metadata (decisions/0021),
    not a network lookup. `subdirectory` is set only for ecosystems that
    can express "this package is a subdirectory of a larger repo" (npm's
    `repository.directory`); `None` means the repository root itself is
    the package root.
    """

    url: str
    subdirectory: str | None = None


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
    `technical_description`/`conversational_overview`/`action_pointer_file`/
    `action_pointer_note` by the AI-gated step (Phase 7,
    `depcompass.grounded_description` — replaced Phase 5's `context_path`-
    gated gap analysis, decisions/0019 — runs for every `depth = full`
    vendor unconditionally) — a failure there sets `description_error`
    instead, rather than leaving everything silently `None` with no way
    to tell "not applicable" from "failed".

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
    technical_description: str | None = None
    conversational_overview: str | None = None
    description_error: str | None = None
    action_pointer_file: str | None = None
    action_pointer_note: str | None = None
    side_effects: list[str] = field(default_factory=list)
