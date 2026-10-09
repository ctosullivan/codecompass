# Data and control flow

## End-to-end: bare `codecompass`

```
discover_manifest_paths(root) -> discover_all(...) -> write/append vendor.toml
        |
        v
sync_all(new_configs, root)         # per-vendor digests, every new vendor
        |
        v
rebuild_project_graph(all_configs, root)   # context-graph.db, pre-enrichment
        |
        v
_maybe_run_enrichment(...)          # Phase B: cost-disclosed AI enrichment, gated
        |
        v
_refresh_generated_artifacts(...)   # second graph rebuild + routing table + Skills + /discovery
```

The second graph rebuild after enrichment is deliberate, not an oversight: `rebuild_deterministic` is a wipe-and-rewrite transaction with no partial-update mode, and this redundant second pass is itself free (no AI call) — it exists so the routing table and tool Skill reflect *this run's* enrichment, not the state from before it.

## The context graph schema (`context-graph.db`)

A single SQLite file at the project root. Tables, as of the current schema version (`"11"` in `graph.py`):

| Table | Survives a whole-project rebuild? |
|---|---|
| `meta` | key/value bookkeeping (schema version, last rebuild timestamp, `git_topology_status`, `source_index_version`) |
| `vendors` | **upserted by natural key** (`name`) — same row id across reruns for an unchanged vendor |
| `source_files` | **upserted by natural key** (`path`) |
| `source_symbols` | **upserted by natural key** (`source_file_id, name, kind, line` — occurrence-based identity, not name alone, specifically because real function overloading produces several distinct declarations sharing one name) |
| `symbols` | **upserted by natural key** (`vendor_id, name`) |
| `uses_edges`, `doc_chunks`, `doc_artifacts`, `documents_edges`, `skill_mentions_edges`, `routes_via_edges`, `depends_on_edges`, `doc_relations_edges`, `git_repositories`, `git_worktrees`, `git_submodules` | **fully cleared and reinserted** on every rebuild — no cross-rebuild identity to preserve |
| `vendor_enrichment`, `symbol_enrichment`, `doc_relation_enrichment` | **never touched** by `rebuild_deterministic` at all — the mechanical reason AI-enrichment spend survives a later whole-project refresh |

Six edge tables, precisely: `uses_edges`, `documents_edges`, `skill_mentions_edges`, `routes_via_edges`, `depends_on_edges`, `doc_relations_edges`. Each represents a real, typed, mechanically-detected relationship — a genuinely different, structurally separate thing from Git topology rows (`git_worktrees`/`git_submodules`, added later), which connect only to a self-contained `git_repositories` entity that no content table ever references.

A `doc_artifacts.origin` value is one of: `codecompass_tool`, `codecompass_vendor`, `third_party`, `project`, `vendor_upstream`, `pinned_reference`. `pinned_reference` (the newest addition) classifies externally-sourced, revision-pinned reference material a tool materialized into the project tree — detected by `spec_docs.py` reading a YAML frontmatter block carrying both a `resolved_commit` and a `source_url` key.

A `doc_relation_enrichment.relation_label` value is one of: `documents_configuration_of`, `explains_usage_of`, `contrasts_with`, `supersedes`, `other` (the required fallback for anything a model returns outside this closed set).

## Reading the graph without writing SQL

`codecompass query ...` covers the common cases (see `docs/reference/cli.md`). For anything else, `context-graph.db` is a plain SQLite file — `sqlite3 context-graph.db "SELECT ..."` works directly.

## Where AI enrichment writes

Exactly three tables: `vendor_enrichment`, `symbol_enrichment`, `doc_relation_enrichment`. Each carries a `model` column recording the producer — either a real Anthropic model id (`claude-haiku-4-5-20251001`, the one model used throughout) or, for the agent-driven producer (`codecompass enrich apply --agent <name>`), a literal string `agent:<name>`. These are two distinct, independently-identifiable producers writing into the same tables, never confusable from the `model` column alone.
