# The context graph (`context-graph.db`)

Full schema as of `src/codecompass/graph.py`'s `_SCHEMA_SQL`
(`graph.py:49-203`), schema version `"9"` (`graph.py:32`). One SQLite file
at the project root, opened via `open_graph(project_root)`
(`graph.py:602-617`), which runs foreign-key-enabling PRAGMA, four
in-place migrations (for an on-disk database created under an older
schema version), then `init_schema`'s idempotent `CREATE TABLE IF NOT
EXISTS`. See `docs/domain/concepts/context.md` sense 1 and
`docs/domain/concepts/relationship-edge.md` for what this graph means
conceptually; this page is the literal schema.

## Node tables

| Table | Key columns | Notes |
|---|---|---|
| `meta` | `key` (PK), `value` | `schema_version`, `last_deterministic_rebuild_at`. |
| `vendors` | `name` UNIQUE, `ecosystem` CHECK'd to the 4-member set, `installed_version`, `repository_url`, `repository_subdirectory`, `source_resolved`, `source_resolution_error`, `last_synced_at` | **Upserted** by `name` on every rebuild — never deleted-and-reinserted while still present in the new fixture (`graph.py:701-735`), so its integer `id` (and anything foreign-keying to it) is stable across syncs. |
| `source_files` | `path` UNIQUE | Every project source file with at least one detected `uses_edges` row. |
| `symbols` | `(vendor_id, name)` UNIQUE, `purpose`, `export_kind` CHECK'd `('export'\|'reexport'\|'undetermined')` default `'export'`, `note` | Also **upserted** by natural key, for the same enrichment-preservation reason as `vendors`. |
| `doc_artifacts` | `path` UNIQUE, `kind` CHECK'd to a 7-value set, `origin` CHECK'd to a 6-value set, `vendor_id` (nullable), `name`, `description` | **Fully deleted and reinserted** every rebuild (not upserted) — this is why `doc_relation_enrichment` below is keyed by plain text, not a foreign key to this table. |
| `doc_chunks` | `(doc_artifact_id, start_line)` unique in practice via natural key, `heading_path`, `end_line`, `content_hash` | Heading-scoped slices of a doc's text (`doc_chunking.chunk_markdown`), added Phase 32. |

`doc_artifacts.kind` closed set: `claude_md`, `overview`, `skill`,
`cursor_mdc`, `slash_command`, `spec_doc`, `vendor_doc`
(`graph.py:107-112`). `doc_artifacts.origin` closed set:
`codecompass_tool`, `codecompass_vendor`, `third_party`, `project`,
`vendor_upstream`, `pinned_reference` (`graph.py:113-118`).

## Edge tables

All six, per `docs/domain/concepts/relationship-edge.md`'s own table
(reproduced here against the literal schema, not re-derived):

| Table | Connects | Nullable target(s) | `UNIQUE` |
|---|---|---|---|
| `uses_edges` | `source_file_id → vendor_id`/`symbol_id` | `symbol_id` (vendor-level usage with no resolved symbol) | none |
| `documents_edges` | `doc_artifact_id → symbol_id` | `chunk_id` | none |
| `skill_mentions_edges` | `doc_artifact_id → vendor_id`/`source_file_id` | both, independently | none |
| `routes_via_edges` | `vendor_id → doc_artifact_id` | — | `(vendor_id, doc_artifact_id)` |
| `depends_on_edges` | `vendor_id → depends_on_vendor_id` | — | `(vendor_id, depends_on_vendor_id)` |
| `doc_relations_edges` | `source_doc_artifact_id → target_vendor_id`/`target_doc_artifact_id` | both target columns, `chunk_id` | `(source_doc_artifact_id, target_vendor_id, target_doc_artifact_id)` |

`doc_relations_edges.relation_kind` is CHECK'd to exactly
`'mentions_dependency'` or `'mentions_artifact'`
(`graph.py:157-159`) — exactly one of `target_vendor_id`/
`target_doc_artifact_id` is set per row, mirroring
`skill_mentions_edges`'s own two-nullable-target shape.

Every edge table foreign-keys with `ON DELETE CASCADE` to its
`vendors`/`symbols`/`doc_artifacts`/`source_files` parent — `graph.py`'s
`open_graph` sets `PRAGMA foreign_keys = ON` per connection (SQLite
defaults this off), so a parent delete during `rebuild_deterministic`
cascades automatically without manual multi-table ordering.

## Enrichment tables — the ones a rebuild never touches

Three tables hold paid AI output and are **never** written by
`rebuild_deterministic` — a comment directly above their `CREATE TABLE`
statements says so explicitly (`graph.py:164, 184-190`):

- **`vendor_enrichment`** (`graph.py:165-175`) — one row per vendor
  (`vendor_id` UNIQUE), `technical_description`, `conversational_overview`,
  `action_pointer_file`, `action_pointer_note`, `symbol_set_hash`,
  `model`, `generated_at`. Written only by `graph.record_enrichment`
  (`enrichment.py`'s writer).
- **`symbol_enrichment`** (`graph.py:177-182`) — one row per symbol
  (`symbol_id` UNIQUE), `purpose`, `generated_at`. Written only by
  `graph.record_symbol_enrichment`.
- **`doc_relation_enrichment`** (`graph.py:191-202`) — keyed by plain
  **text** columns (`source_doc_path`, `target_vendor_name`,
  `target_doc_path`), *not* a foreign key to `doc_artifacts.id`
  (`decisions/0038`) — because `doc_artifacts` is fully deleted and
  reinserted every rebuild, a foreign key here would cascade this
  table's whole content away on every whole-project sync. Also carries
  `ai_summary`, `relation_label` (CHECK'd to a closed 5-value taxonomy,
  see below), `content_hash`, `model`, `generated_at`. Written only by
  `graph.record_relation_enrichment`.

`vendors`/`symbols` being **upserted** rather than deleted-and-reinserted
is the entire mechanism that lets `vendor_enrichment`/`symbol_enrichment`
survive a rebuild via their own `ON DELETE CASCADE` foreign key without
special-casing: as long as a vendor/symbol's natural key still appears in
the new fixture, its integer id (and anything cascading from it) is
untouched.

## `RELATION_LABELS` — the closed taxonomy (`graph.py:38-47`)

```python
RELATION_LABELS = (
    "documents_configuration_of",
    "explains_usage_of",
    "contrasts_with",
    "supersedes",
    "other",
)
```

`doc_relation_enrichment.relation_label`'s CHECK constraint
(`decisions/0045`). `"other"` is the required fallback for any label an
AI response returns that isn't in this set — callers are expected to
substitute it themselves before calling `record_relation_enrichment`
(`relation_enrichment._normalize_relation_label`), matching this
project's general "never raises, degrades to a safe default" posture
(the same posture `export_kind`'s own default embodies).

## `rebuild_deterministic` (`graph.py:623-698`) — the one write path for everything except enrichment

One transaction (`with conn:`), in this fixed order:

1. Delete every edge/leaf table unconditionally (`doc_relations_edges`
   through `source_files` — `doc_chunks`, `doc_artifacts` included).
2. Upsert `vendors`, then `symbols` (by natural key), deleting only
   rows whose natural key no longer appears in the new fixture.
3. Insert `source_files`, `doc_artifacts`, `doc_chunks` fresh, building
   natural-key → integer-id maps as it goes.
4. Insert every edge table, resolving each row's natural-key references
   (vendor name, symbol name, doc path, chunk `(path, start_line)`) via
   those maps.
5. Write `meta.last_deterministic_rebuild_at`.

Called from exactly one place: `sync.rebuild_project_graph`
(`sync.py:234-368`) — see `sync-and-enrichment-pipeline.md` for what
assembles the row lists this function is handed.

## Migrations — why four separate functions, not one

`open_graph` runs four migration functions before `init_schema`, each
independently idempotent and each checking its own precondition directly
(`PRAGMA table_info`, or the stored `CREATE TABLE` SQL text) rather than
uniformly gating on `meta.schema_version`:

- `_migrate_doc_artifacts_constraints` (`graph.py:374-430`) — the only
  one that actually drops and recreates tables (`doc_artifacts`,
  `documents_edges`, `doc_relations_edges`), because none of the three
  holds enrichment data that must survive.
- `_migrate_doc_relation_enrichment_relation_label`,
  `_migrate_symbols_export_kind_note_columns`,
  `_migrate_vendors_ecosystem_constraint` — each uses `ALTER TABLE ADD
  COLUMN` or (for `vendors`, since SQLite has no `ALTER TABLE` form for
  changing a `CHECK` constraint) a create-copy-drop-rename dance that
  preserves every existing row's `id`, specifically because
  `vendor_enrichment`/`symbol_enrichment` cascade from these tables and
  must not be destroyed by a schema upgrade on an existing project's
  database.

## Read/query functions (`graph.py:970` onward)

Not exhaustive, but every one of these is a real, currently-callable
function, not a design sketch: `unused_vendors`, `documented_but_unused`,
`used_but_undocumented`, `spec_docs_without_relations`,
`vendor_docs_without_relations`, `doc_relations`, `vendor_profile`,
`symbol_profile`, `doc_code_trace`, `skills_index`,
`enrichment_candidates`, `has_enrichment`,
`relation_enrichment_candidates`. Each is read-only except the four
enrichment writers (`record_enrichment`, `record_symbol_enrichment`,
`record_relation_enrichment`) and `rebuild_deterministic` itself —
`graph.py` has no other write path.
