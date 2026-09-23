# Module map

Part of the `architecture/` reference set. See [`overview.md`](overview.md)
for the system-at-a-glance entry point; the rest of this set:
[`core-data-model.md`](core-data-model.md),
[`adapter-interface.md`](adapter-interface.md),
[`context-graph-schema.md`](context-graph-schema.md),
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md).

`src/codecompass/` is 23 top-level modules plus a 6-module `adapters/`
package (8,623 lines total). No package splits below
`codecompass`/`codecompass.adapters` exist.

## Layering, by dependency direction

Reading `import` statements module-by-module (not asserted from memory)
shows four rough layers, thinnest/most-depended-upon first. A module in a
later layer may import from any earlier layer; the reverse never happens
in the current codebase.

### Layer 1 — core data model, no I/O

- **`core.py`** — `Ecosystem` (4-member `StrEnum`), `VendorConfig`,
  `RepositoryLocation`, `DepNode`, `VendorDigest`. See
  [`core-data-model.md`](core-data-model.md).
- **`symbols.py`** — `Symbol` dataclass plus the no-AI, per-ecosystem
  symbol/purpose extractors (`extract_python_symbols`,
  `extract_rust_symbols`, `extract_npm_symbols`,
  `extract_symbols_for_file`, `purpose_for_file`).

### Layer 2 — mechanical detection/generation (file I/O, subprocess, no AI, no shared state)

- **`config.py`** — `vendor.toml` parsing → `list[VendorConfig]`
  (`load_vendor_config`).
- **`discovery.py`** — manifest-based dependency discovery
  (`package.json`/`pyproject.toml`/`requirements.txt`/`Cargo.toml`/
  `package.yaml`) and `vendor.toml` bootstrap/append.
- **`adapters/`** — the `EcosystemAdapter` contract and four concrete
  adapters (`npm.py`, `python.py`, `cargo.py`, `haskell.py`) plus the
  generic external-process client (`external_process.py`). See
  [`adapter-interface.md`](adapter-interface.md).
- **`filetree.py`** / **`deptree.py`** — deterministic `FILETREE.md`/
  `filetree.json` and `DEPTREE.md`/`deptree.json` rendering from a source
  tree / a `DepNode` tree. No AI, unconditional on every `sync`.
- **`usage.py`** — project-source-side import detection
  (`detect_python_imports`/`detect_npm_imports`/`detect_rust_imports`,
  `resolve_project_usage`) — the mirror image of `symbols.py`: pulls
  usage sites *out of* the consuming project rather than symbols *out of*
  a vendor.
- **`source_resolution.py`** — resolves a vendor's upstream repository
  from locally-available adapter metadata only (never a network registry
  lookup, `decisions/0021`) and shallow-clones it (`resolve_and_clone`).
- **`doc_mapping.py`** — pure transformations over already-generated
  per-vendor artifacts (`CLAUDE.md`/`OVERVIEW.md`/`deptree.json`) into
  `context-graph.db` edge rows (`documents_edges`, `routes_via_edges`,
  `depends_on_edges`, `doc_relations_edges`) plus `doc_chunks`.
- **`doc_chunking.py`** — deterministic heading-based markdown chunking
  (`chunk_markdown`) — no NLP, no embeddings, no model call.
- **`skill_scan.py`** — indexes every Skill under `.claude/skills/` and
  every Cursor `.mdc` rule under `.cursor/rules/`, project-wide (not just
  CodeCompass's own generated ones).
- **`spec_docs.py`** — detects a project's own human-authored spec docs
  (README, `ARCHITECTURE.md`, `docs/**/*.md`, `decisions/**/*.md`, a
  fixed default glob set) as `doc_artifacts` rows (`kind='spec_doc'`,
  `origin='project'`), including `origin='pinned_reference'` detection
  for revision-pinned reference material.
- **`staleness.py`** — compares a persisted `CLAUDE.md`'s recorded
  installed version against a live adapter read; severity per
  `decisions/0005` (patch=silent, minor=warn, major=hard-fail).

### Layer 3 — persistence, orchestration, and generated-artifact rendering

- **`graph.py`** — `context-graph.db`'s schema, `rebuild_deterministic`
  (the whole-project rebuild transaction), and every read/write query
  function. See [`context-graph-schema.md`](context-graph-schema.md). The
  single largest module (1,696 lines).
- **`claude_md.py`** — per-vendor `CLAUDE.md` template rendering
  (`render_vendor_claude_md`) plus the narrower in-place Description-only
  edit path (`update_description_section`) enrichment uses.
- **`skill.py`** — the unconditional tool-level Skill
  (`render_tool_skill`/`write_tool_skill`) and the per-vendor Skill +
  Cursor `.mdc` export, generated once a vendor has an enrichment record.
- **`commands.py`** — the `/discovery` custom slash command
  (`.claude/commands/discovery.md`), a distinct artifact type from a
  Skill (different frontmatter shape, different trigger mechanism).
- **`index.py`** — idempotent routing-table injection into the project
  root `CLAUDE.md` (`update_root_claude_md`) — deliberately reads
  already-synced per-vendor `CLAUDE.md` files rather than re-running
  `sync`, so it stays cheap even after enrichment exists.
- **`sync.py`** — `sync_vendor` (one vendor end to end),
  `rebuild_project_graph` (the whole-project graph rebuild, decoupled
  from the per-vendor loop). See
  [`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md).
- **`enrichment.py`** / **`relation_enrichment.py`** — batched,
  usage-driven AI enrichment: vendor/symbol descriptions and spec-doc
  relationship summaries respectively. Sibling modules, not merged — a
  relationship candidate's shape differs enough from a vendor candidate's
  shape that a shared module would need a type-discriminated candidate
  threaded through every function.
- **`chat.py`** — the single-vendor chat REPL (`run_chat`), grounded
  only on already-persisted digest files, never re-running `sync_vendor`.

### Layer 4 — CLI

- **`cli.py`** — the Typer app: `init`, `sync`, `index`, `check`,
  `query` (a sub-app: `vendors`, `vendor`, `symbol`, `skills`,
  `relations`), `chat`, `undo`, plus bare `codecompass`'s own
  bootstrap/enrichment orchestration (`_bootstrap`,
  `_maybe_run_enrichment`, `_refresh_generated_artifacts`). 1,219
  lines — the second-largest module, and the only one every other layer
  is invisible to (nothing in layers 1-3 imports `cli.py`).

## Two informal senses of "adapter" in this codebase

[`docs/domain/concepts/adapter.md`](../docs/domain/concepts/adapter.md)
documents this directly and it matters for reading this module map
correctly: `skill.py`, `commands.py`, and `index.py` are sometimes
informally grouped as "host-output adapters" in this project's own prose
(renderers that turn already-computed content into a tool-specific
format — see `overview.md`'s "Module tiers" section), but **this
grouping has no corresponding class, ABC, or shared interface anywhere
in `src/`** — a direct grep for the word "adapter" in those three files
returns zero hits. The only real, code-level `adapter` concept is
`EcosystemAdapter` ([`adapter-interface.md`](adapter-interface.md)). Do
not conflate the two senses.

## What actually calls what, at the top

`cli.py`'s bare-command path (`main` → `_bootstrap`) and its `sync`
command are the only two callers of `sync.rebuild_project_graph`
(confirmed by grep: `rebuild_project_graph(` appears only in
`cli.py:136,234,300` and `sync.py`'s own definition). Every other module
that touches `context-graph.db` (`enrichment.py`, `relation_enrichment.py`,
`index.py`, `skill.py`) opens a read-only or narrowly-scoped connection
and never rebuilds the deterministic tables itself.
