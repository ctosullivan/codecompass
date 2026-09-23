# Sync and enrichment pipeline

Part of the `architecture/` reference set. See [`overview.md`](overview.md)
for the system-at-a-glance entry point; the rest of this set:
[`module-map.md`](module-map.md), [`core-data-model.md`](core-data-model.md),
[`adapter-interface.md`](adapter-interface.md),
[`context-graph-schema.md`](context-graph-schema.md).

Traced from `cli.py`'s bare-command path (`main` → `_bootstrap`) and
`sync` command, the two whole-project entry points. `sync <vendor>`
(single-vendor) and `check --fix` are narrower — noted below.

## Phase A — free, deterministic, zero-question (`_bootstrap`)

1. **Discover** manifests (`discovery.discover_manifest_paths` +
   `discover_all`) and write/extend `vendor.toml`
   (`write_vendor_toml`/`append_vendor_toml`). An already-tracked
   vendor's existing entry is left untouched.
2. **Sync only the newly-discovered vendors** (`sync_all`) — an
   already-tracked vendor's generated output is not touched by a bare
   invocation unless it's new this run (`decisions/0017`'s zero-question
   guarantee: Phase A never pays AI cost, and doesn't even regenerate old
   vendors' files for free, to stay predictable).
3. **Rebuild the whole-project graph** (`rebuild_project_graph`) — must
   happen before Phase B, since `enrichment.select_candidates` reads
   usage-proven candidates *from* the graph.
4. **Phase B** (`_maybe_run_enrichment`, see below) — auto-triggered, but
   cost-disclosed and confirmable.
5. **Unconditionally refresh generated artifacts**
   (`_refresh_generated_artifacts`) — in a `finally` block, so it runs
   whether Phase B ran, was skipped, or was budget-aborted.

`codecompass init --scan <manifest file> [--scan <manifest file> ...]`
is the explicit, scripted/CI-friendly synonym for step 1 — useful for
naming specific manifests rather than relying on root-level
auto-discovery. Unlike bare `codecompass`, it keeps a stricter contract:
errors rather than overwriting if `vendor.toml` already exists. It is not
a Phase A/B trigger point itself — no cloning, no graph rebuild, no
Phase B.

## `sync_vendor` — one vendor end to end (`sync.py:102-202`)

Deterministic and idempotent: every output file is fully overwritten on
each call, no diffing against previous output, **no AI call ever made
from this function**.

1. `adapter = get_adapter(config, project_root)`; read
   `installed_version()`, `readme_and_api_surface()`,
   `dependency_tree()`, `source_location()` — all adapter methods, no
   network beyond whatever the adapter itself shells out to.
2. Clone the vendor's own upstream source unconditionally
   (`resolve_and_clone`, `decisions/0033`) into `vendor/<name>/src/`; on
   `SourceResolutionError`, fall back to copying the local-install
   snapshot (`_copy_source_snapshot`) and record `description_error` (a
   clone failure, not a description failure).
3. **Read-only** lookup of this vendor's current `vendor_enrichment` row
   from the graph, if `context-graph.db` exists yet (`_lookup_enrichment`)
   — populates `technical_description`/`conversational_overview`/
   `action_pointer_file`/`action_pointer_note` on the `VendorDigest`.
   This function never writes enrichment; it only reproduces
   already-paid-for content on a from-scratch re-render
   (`decisions/0035`).
4. Render `DEPTREE.md`/`deptree.json`, `FILETREE.md`/`filetree.json`
   (with an embedded Symbol index section — the symbol index renders
   *within* `FILETREE.md`, not a separate file), `OVERVIEW.md` (only if
   `conversational_overview` is set), and `CLAUDE.md`
   (`render_vendor_claude_md`). Five files per vendor normally, six for
   an already-enriched one.

## `rebuild_project_graph` — the whole-project graph rebuild (`sync.py:234-368`)

Rebuilds `context-graph.db` from **every** tracked vendor's current state
(not just vendors `sync_vendor` touched this run) plus a fresh
project-source usage scan. In order:

1. For each config: `adapter.repository_url()`,
   `adapter.installed_version()` → a `VendorRow`; `adapter.symbols()` →
   `SymbolRow`s (the generic adapter capability every adapter has, via
   `EcosystemAdapter.symbols()`'s own default walk-and-extract for
   in-process adapters, or `HaskellAdapter`'s own override reading
   already-computed external-process data).
2. `usage.resolve_project_usage(project_root, configs)` detects the
   project's own imports; each `DetectedImport.symbol_name` is resolved
   against the matching vendor's just-collected symbol names — no match
   falls back to a vendor-level edge (`symbol_name=None`). The project's
   own `tests`/`fixtures` importing a vendor counts as real usage signal
   — `usage.py`'s own prune set drops only build/dependency noise
   (`node_modules`, `dist`, `build`, `.git`, `__pycache__`, `.venv`,
   `venv`), never test directories, deliberately narrower than
   `filetree.py`'s own prune set.
3. `doc_mapping.collect_vendor_doc_artifacts` /
   `collect_vendor_upstream_doc_artifacts`, `skill_scan.scan_skills`,
   `spec_docs.scan_spec_docs` — collect every `doc_artifacts` row (four
   `origin` categories: codecompass-generated per-vendor docs, a
   vendor's own embedded upstream docs, project Skills/`.mdc` rules, the
   project's own spec docs). `spec_docs.scan_spec_docs` and `usage.py`
   both deliberately prune `vendor/` — a vendor's own cloned source
   never self-references its own package name as false "project uses
   this vendor" evidence.
4. `doc_mapping.build_doc_chunks`, `build_documents_edges`,
   `skill_scan.build_skill_mentions_edges`, `build_routes_via_edges`,
   `build_depends_on_edges`, `build_doc_relations_edges` — every edge
   table's row list, each a pure mechanical transformation over
   already-generated artifacts (no new AI call, no new extraction).
   Mention detection is **word-boundary** (`\b<name>\b`), not substring —
   a naive substring match risks false positives on a vendor/file name
   that collides with a common English word or is short enough to appear
   inside an unrelated word (a vendor named `six` must not match
   `sixty-four`).
5. `graph.rebuild_deterministic(conn, ...)` — the one write. See
   [`context-graph-schema.md`](context-graph-schema.md) for the schema
   this populates.

**No AI call anywhere in this function or in `sync_vendor`.** The only
AI-call budget gate in the codebase lives in `cli.py`'s
`_maybe_run_enrichment`, gating `enrichment`/`relation_enrichment`
directly.

## Phase B — usage-driven AI enrichment (`_maybe_run_enrichment`, `cli.py:153-216`)

A no-op if neither `enrichment.select_candidates` nor
`relation_enrichment.select_candidates` finds anything eligible.

1. **Select candidates** from the just-rebuilt graph:
   - `enrichment.select_candidates` — every vendor
     `graph.enrichment_candidates` reports as usage-proven, whose current
     used-symbol set doesn't already match a cached hash, checked **two
     ways** (belt-and-suspenders, `decisions/0032`): the DB-level
     `vendor_enrichment.symbol_set_hash`, and the file-level `**Enrichment
     symbol-set hash:**` line already committed in
     `vendor/<name>/CLAUDE.md` (the check that still works on a fresh
     clone with no gitignored `context-graph.db` at all). A vendor with
     no retrievable material (no README/entry-point in its clone) is
     skipped, not fatal.
   - `relation_enrichment.select_candidates` — every `doc_relations_edges`
     row not already cached at its current content hash. Each
     candidate's source excerpt is centered on the actual mechanical
     mention (re-deriving the same word-boundary match
     `doc_mapping.build_doc_relations_edges` found, then slicing 1,000
     characters before / 3,000 after it) rather than the file's opening —
     falling back to a first-N-characters slice only if the needle can no
     longer be found (the file changed since the last graph rebuild).
     When the matched edge has an attributed chunk, the chunk's own text
     is used directly instead, no character cap. See `decisions/0042`,
     `decisions/0046`, and `overview.md`'s "Known footguns"/historical
     note for how this excerpt selection evolved.
2. **Estimate cost** (`enrichment.estimate_cost`, folding in both
   candidate sets' batch counts) and print it — model named explicitly
   (`claude-haiku-4-5-20251001`).
3. **Budget check** (`enrichment.check_budget`) runs *before* the
   confirmation prompt — no point asking a human to confirm a run that's
   already refused on cost grounds.
4. **Confirm** (skipped by `--yes`).
5. **Run** both batch sets (`run_enrichment_batches` for each,
   `_call_anthropic`'s forced-tool-use pattern) and **apply** results
   (`enrichment.apply_results`, `relation_enrichment.apply_results`) —
   writes to `vendor_enrichment`/`symbol_enrichment`/
   `doc_relation_enrichment` plus an in-place `CLAUDE.md`
   Description-section rewrite (`claude_md.update_description_section`)
   and regenerated per-vendor Skill/`.mdc` files, all without re-running
   `sync_vendor`'s full pipeline. `relation_enrichment.apply_results`
   accepts no `project_root` parameter at all, structurally guaranteeing
   its AI-generated summary is written *only* to
   `doc_relation_enrichment`, never into a spec doc's own file.

A second, agent-driven producer writes through this same
`relation_enrichment.apply_results` path: `codecompass enrich apply`
(see [`docs/cli-reference.md`](../docs/cli-reference.md)) lets a Claude
Code agent supply `ai_summary`/`relation_label` for a pending candidate,
distinguished from the automated Anthropic-API producer only by its
`model` value (`f"agent:{agent}"`) — see
[`decisions/0054`](../decisions/0054-agent-driven-enrichment-is-a-second-non-authoritative-producer.md).

Relationship candidates are selected *before* this same invocation's own
vendor enrichment is applied — a vendor being enriched for the first time
in this run grounds any relationship mentioning it in whatever its digest
said *before* this run started; the next sync's candidates re-derive from
the newer content once it exists (an accepted, deliberate ordering, not
an oversight).

## `_refresh_generated_artifacts` — the unconditional closing step (`cli.py:219-238`)

A **second, full** `rebuild_project_graph` pass (not a lighter targeted
update — `rebuild_deterministic` is a deliberate wipe-and-rewrite
transaction with no partial-update mode, and the redundant pass is
deterministic and free), then `load_routing_rows` + `update_root_claude_md`
(the project-root `CLAUDE.md` vendor table), `write_tool_skill`,
`write_discovery_command`. Runs once, unconditionally, at the end of both
`_bootstrap` and `sync`'s whole-project branch, after
`_maybe_run_enrichment` returns — success or budget-abort — so the
routing table/tool Skill never reflect stale pre-enrichment state. See
`overview.md`'s historical note for the bug this design fixed.

## Narrower entry points

- **`sync <vendor>`** (single-vendor) — `sync_vendor` only. No graph
  rebuild, no enrichment trigger (`decisions/0025`).
- **`check --fix`** — re-syncs individual vendors found stale; does not
  touch the graph (`cli.py`'s `_run_fix`).
- **`index`** — deliberately does *not* call `sync` — reads
  already-persisted per-vendor `CLAUDE.md` files directly, so it stays
  cheap even after enrichment exists on `sync`.
- **`chat <vendor>`** — grounds only on already-persisted digest files
  (`CLAUDE.md`, `OVERVIEW.md` if enriched) — never calls `sync_vendor` or
  reconstructs a `VendorDigest`, so starting a chat session never
  re-incurs clone + AI-generation cost.
