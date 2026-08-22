"""Core, ecosystem-agnostic data models for codecompass.

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


@dataclass(frozen=True)
class VendorConfig:
    """One `[[vendor]]` entry from vendor.toml.

    Narrowed to `(name, ecosystem)` in Phase 16 (`decisions/0031`,
    `decisions/0035`) — the per-vendor `depth` toggle (SURFACE/FULL) that
    used to gate a pinned source snapshot and AI-generated description is
    retired: cloning is unconditional (Phase 13) and AI enrichment is
    usage-driven, read from the context graph, not a `vendor.toml` field.
    """

    name: str
    ecosystem: Ecosystem


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
    `action_pointer_note` by `sync_vendor`'s read-only lookup of this
    vendor's current `vendor_enrichment` record in the context graph
    (Phase 16, `decisions/0035` — usage-driven AI enrichment, written by
    `codecompass.enrichment`, is the only source of these fields now).
    `description_error` is set instead only on a source-clone failure
    (`codecompass.source_resolution`), not a description failure — there's
    no description "attempt" inside `sync_vendor` to fail anymore.

    Does not carry staleness information — `codecompass.staleness` (Phase
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
