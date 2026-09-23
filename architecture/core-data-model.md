# Core data model

Part of the `architecture/` reference set. See [`overview.md`](overview.md)
for the system-at-a-glance entry point; the rest of this set:
[`module-map.md`](module-map.md), [`adapter-interface.md`](adapter-interface.md),
[`context-graph-schema.md`](context-graph-schema.md),
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md).

Everything in `src/codecompass/core.py` (103 lines) is a plain dataclass —
no methods beyond dataclass defaults, no I/O. See
[`docs/domain/concepts/vendor.md`](../docs/domain/concepts/vendor.md),
[`ecosystem.md`](../docs/domain/concepts/ecosystem.md),
[`digest.md`](../docs/domain/concepts/digest.md) for what these mean; this
page is only about their shape and how later code populates them.

## `Ecosystem` (`core.py:13-19`)

```python
class Ecosystem(StrEnum):
    NPM = "npm"
    PYTHON = "python"
    CARGO = "cargo"
    HASKELL = "haskell"
```

A fixed, closed 4-member enum. `get_adapter`'s dispatch table
(`adapters/__init__.py:18-23`) is total over all four members — there is
no fifth ecosystem and no fallback case.

## `VendorConfig` (`core.py:22-34`)

```python
@dataclass(frozen=True)
class VendorConfig:
    name: str
    ecosystem: Ecosystem
```

Exactly two fields — narrowed from an earlier `(name, ecosystem, depth)`
shape (`decisions/0031`, `decisions/0035`): a per-vendor `depth`
(`SURFACE`/`FULL`) toggle used to gate cloning and AI description; cloning
is now unconditional and AI enrichment is usage-driven, read from the
context graph, never a `vendor.toml` field. A legacy `vendor.toml` entry
still carrying a `depth = "..."` line keeps parsing without error —
`config.load_vendor_config` simply never looks at that key. One instance
per `[[vendor]]` entry in `vendor.toml`, parsed by
`config.load_vendor_config`. See
[`../docs/config-schema.md`](../docs/config-schema.md) for the file
format.

## `RepositoryLocation` (`core.py:37-49`)

```python
@dataclass(frozen=True)
class RepositoryLocation:
    url: str
    subdirectory: str | None = None
```

Where a vendor's upstream repository actually lives, resolved from
locally-available package metadata only (`decisions/0021` — never a
network lookup). `subdirectory` is set for ecosystems that can express
"this package is a subdirectory of a larger repo" — the npm adapter's
`repository.directory` field, and the Haskell adapter's own monorepo
package-root resolution (`HaskellAdapter.repository_url`,
`adapters/haskell.py:67-97`).

## `DepNode` (`core.py:52-63`)

```python
@dataclass
class DepNode:
    name: str
    version: str
    children: list[DepNode] = field(default_factory=list)
    dev_only: bool = False
    side_effects: list[str] = field(default_factory=list)
```

One node in a dependency tree, ecosystem-agnostic, deliberately mutable
(built incrementally by each adapter's `dependency_tree()`). **Not
deduplicated at construction** — diamond dependencies appear repeated in
full exactly as the underlying tool reports them; deduplication into
"see X above" back-references happens only at render time
(`deptree.render_deptree_markdown`/`render_deptree_json`).

## `VendorDigest` (`core.py:66-103`)

```python
@dataclass
class VendorDigest:
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
```

The aggregate output of generating one vendor's documentation — see
[`docs/domain/concepts/digest.md`](../docs/domain/concepts/digest.md) for
the full digest-vs-context-packet distinction. `file_tree`/`dep_tree`/
`api_surface`/`side_effects` are populated deterministically, every
`sync`, for every vendor, at no AI cost. `technical_description`/
`conversational_overview`/`action_pointer_file`/`action_pointer_note` are
populated only by a **read-only lookup** of that vendor's existing
`vendor_enrichment` row (`sync.py`'s `_lookup_enrichment`) —
`sync_vendor` never generates these itself; `codecompass.enrichment` is
the only writer (`decisions/0035`). `description_error` is set only on a
source-clone failure, not a description failure — there is no
description "attempt" inside `sync_vendor` to fail. `VendorDigest`
carries **no staleness field** — `codecompass.staleness` reads persisted
`CLAUDE.md` files directly rather than building a `VendorDigest` for that
purpose (kept cheap and side-effect-free so `check` stays usable as a
fast CI gate).

## `Symbol` (`symbols.py:26-47`, not `core.py`)

```python
@dataclass
class Symbol:
    name: str
    purpose: str | None = None
    export_kind: str = "export"
    note: str | None = None
```

Lives in `symbols.py`, not `core.py`, because it is produced by
extraction logic that module also owns. `export_kind`/`note` generalize
the external wire protocol's own `kind`/`note` pair (`decisions/0059`)
into CodeCompass's internal model — deliberately narrow
**export/exposure-status** fields (`"export"` | `"reexport"` |
`"undetermined"`), explicitly *not* a symbol-type/kind field (function
vs. class vs. module). Every in-process extractor
(`extract_python_symbols`, `extract_rust_symbols`, `extract_npm_symbols`)
only ever sets the default (`"export"`, no note) — none of them has a
confidence-tiering concept of its own. `HaskellAdapter.symbols()` is the
one place that actually produces a non-default `export_kind`, converting
the external adapter's own wire `kind` field 1:1
(`adapters/haskell.py:124-150`). See
[`adapter-interface.md`](adapter-interface.md) for how each adapter
populates `Symbol` instances.

## What is deliberately absent from this layer

- No `id` fields anywhere in `core.py` — every cross-reference elsewhere
  in the codebase (including `context-graph.db`'s own row dataclasses in
  `graph.py`) resolves by natural key (name, path), never a pre-assigned
  integer, so this layer stays free of any database-shaped concept. See
  [`context-graph-schema.md`](context-graph-schema.md#row-dataclasses-and-natural-keys)
  for why the graph layer follows the same convention.
- No network-facing fields — `RepositoryLocation.url` is a string
  resolved from local metadata; nothing in `core.py` performs I/O to
  populate itself.
