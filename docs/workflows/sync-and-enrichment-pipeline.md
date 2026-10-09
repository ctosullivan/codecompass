# Workflow: the sync and enrichment pipeline

This page walks the real, current behaviour of `codecompass sync` and the bare-command bootstrap, end to end, grounded directly in `src/codecompass/cli.py`, `sync.py`, `enrichment.py`, and `relation_enrichment.py`.

## Phase A — deterministic, always free

Triggered by bare `codecompass` or `codecompass sync`:

1. **Discovery** (only on the bare-command path): scan for known manifest files, write/extend `vendor.toml`.
2. **Per-vendor sync** (`sync_vendor`, for each vendor needing it): resolve the matching adapter, read installed version / API surface / dependency tree, attempt to clone the vendor's own upstream source into `vendor/<name>/src/` (falling back to a local-install-sourced copy if cloning fails — `description_error` records why, but this is a *clone* failure, never a "description" failure, since nothing in this phase ever attempts to generate a description), render `DEPTREE.md`/`FILETREE.md`/their JSON mirrors, and render `CLAUDE.md` — reading back any *already-existing* enrichment from the graph (a from-scratch re-render must reproduce a vendor's already-enriched Description section, not silently drop it).
3. **Whole-project graph rebuild** (`rebuild_project_graph`, only on a whole-project sync — never on `sync <vendor>`): for every tracked vendor, record its installed version/repository URL/symbols; scan the consuming project's own source for both vendor usage (`usage.py`) and first-party symbols (`source_symbols.py`); scan the project's own spec docs, vendor's embedded upstream docs, and every Skill/`.mdc` rule in the project; detect Git repository topology; assemble every edge table; call `rebuild_deterministic`.

None of this phase ever makes a network call beyond cloning each vendor's own real, public upstream repository, and never makes an Anthropic API call.

## Phase B — usage-driven, cost-gated AI enrichment

Auto-triggered immediately after Phase A, on bare `codecompass` and on a whole-project `codecompass sync` — never on `sync <vendor>` (single-vendor sync has no enrichment trigger at all).

### Candidate selection

Two independent candidate sets are selected, from the **just-rebuilt** context graph:

- **Vendor/symbol candidates** (`enrichment.select_candidates`): every vendor with at least one real `uses_edges` row (i.e. your own project code genuinely imports it), whose current used-symbol set doesn't already match a cached hash — checked two ways: a database-level hash (`vendor_enrichment.symbol_set_hash`) *and* a file-level hash embedded in the committed `CLAUDE.md`'s own Metadata section (the second check is what still works correctly on a fresh clone with no `context-graph.db` at all, since that file is gitignored).
- **Relationship candidates** (`relation_enrichment.select_candidates`): every mechanically-detected `doc_relations_edges` row (a spec doc mentioning a tracked vendor, or mentioning another named doc artifact) whose freshly-computed content hash doesn't already match a cached `doc_relation_enrichment` row.

### Disclosure and consent

Both candidate sets' combined cost is disclosed in **one** printed line and gated by **one** confirmation prompt (or `--yes`/`--budget`) — never two separate prompts. Cost is estimated at a flat `$0.02` per API *batch* (not per vendor/relationship — several candidates share one call), using the model `claude-haiku-4-5-20251001` throughout. `--budget <USD>` aborts *before any API call* if the combined estimate exceeds it.

### The call itself

Each candidate set is batched (`plan_batches`, a greedy character-budget packer, default `150,000` characters per batch) and sent as one forced-tool-use Anthropic API call per batch, grounded entirely in real retrieved material (a vendor's own README/docs/entry-point file, or a spec doc's own excerpt — centered on the actual mechanical match, not just the file's first N characters, when the match's location is known).

### Writing results

- **Vendor enrichment** writes `vendor_enrichment` + per-symbol `symbol_enrichment` rows, rewrites just the Description section and the enrichment-hash line of the vendor's already-rendered `CLAUDE.md` (never a full re-render), writes `OVERVIEW.md` even on a vendor's very first enrichment (a real, fixed bug: without this, `OVERVIEW.md` would not have appeared until the *next* sync), and regenerates that vendor's per-vendor Skill/`.mdc` rule.
- **Relationship enrichment** writes only to `doc_relation_enrichment`. **This is a structural, non-negotiable boundary**: `relation_enrichment.apply_results` does not even accept a `project_root` parameter — it has no filesystem handle to a spec doc file at all, and cannot write into one even if it wanted to. The AI-generated relationship summary is visible via `codecompass query relations`, never injected into your own spec-doc file.

### A second, non-automated producer

`codecompass enrich apply <entries_file> --agent <name>` lets an AI coding agent (reasoning over the exact same `select_candidates` output, rather than calling the Anthropic API directly) submit relationship enrichment. This is mechanically gated, not merely instructed: an entry is only accepted if it matches a row `select_candidates` currently lists as genuinely pending (new or changed since last enrichment) — an edge that doesn't exist, or is already enriched and unchanged, is rejected outright. Writes go through the identical `apply_results` path, tagged `model = "agent:<name>"`, never confusable with the automated-API producer.

## Post-enrichment refresh

Regardless of whether Phase B ran, found nothing, or was declined/budget-capped, the invocation finishes with an unconditional second graph rebuild plus regeneration of the root `CLAUDE.md` routing table, the tool-level Skill, and `/discovery` — so these always reflect the current run's own outcome.
