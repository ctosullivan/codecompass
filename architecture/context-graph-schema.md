# The context graph (`context-graph.db`)

Part of the `architecture/` reference set. See [`overview.md`](overview.md)
for the system-at-a-glance entry point; the rest of this set:
[`module-map.md`](module-map.md), [`core-data-model.md`](core-data-model.md),
[`adapter-interface.md`](adapter-interface.md),
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md).

Full schema as of `src/codecompass/graph.py`'s `_SCHEMA_SQL`, schema
version `"9"`. One SQLite file at the project root, opened via
`open_graph(project_root)`, which runs foreign-key-enabling PRAGMA, four
in-place migrations (for an on-disk database created under an older
schema version), then `init_schema`'s idempotent `CREATE TABLE IF NOT
EXISTS`. See
[`docs/domain/concepts/context.md`](../docs/domain/concepts/context.md)
sense 1 and
[`relationship-edge.md`](../docs/domain/concepts/relationship-edge.md)
for what this graph means conceptually; this page is the literal schema.

## Node tables

| Table | Key columns | Notes |
|---|---|---|
| `meta` | `key` (PK), `value` | `schema_version`, `last_deterministic_rebuild_at`. |
| `vendors` | `name` UNIQUE, `ecosystem` CHECK'd to the 4-member set, `installed_version`, `repository_url`, `repository_subdirectory`, `source_resolved`, `source_resolution_error`, `last_synced_at` | **Upserted** by `name` on every rebuild — never deleted-and-reinserted while still present in the new fixture, so its integer `id` (and anything foreign-keying to it) is stable across syncs. |
| `source_files` | `path` UNIQUE | Every project source file with at least one detected `uses_edges` row. |
| `symbols` | `(vendor_id, name)` UNIQUE, `purpose`, `export_kind` CHECK'd `('export'\|'reexport'\|'undetermined')` default `'export'`, `note` | Also **upserted** by natural key, for the same enrichment-preservation reason as `vendors`. |
| `doc_artifacts` | `path` UNIQUE, `kind` CHECK'd to a 7-value set, `origin` CHECK'd to a 6-value set, `vendor_id` (nullable), `name`, `description` | **Fully deleted and reinserted** every rebuild (not upserted) — this is why `doc_relation_enrichment` below is keyed by plain text, not a foreign key to this table. |
| `doc_chunks` | `(doc_artifact_id, start_line)` unique in practice via natural key, `heading_path`, `end_line`, `content_hash` | Heading-scoped slices of a doc's text (`doc_chunking.chunk_markdown`). **Not** the `DocChunk`/`EXPLAINS` tables from a former, earlier design that `decisions/0032` explicitly excluded from this schema — same name, unrelated design (no embeddings, no semantic chunking; heading-boundary-only, additive to the mechanical mention-detection pipeline below). See `decisions/0032`/`decisions/0046`. |

`doc_artifacts.kind` closed set: `claude_md`, `overview`, `skill`,
`cursor_mdc`, `slash_command`, `spec_doc`, `vendor_doc`. `doc_artifacts.origin`
closed set: `codecompass_tool`, `codecompass_vendor`, `third_party`,
`project`, `vendor_upstream`, `pinned_reference` — `project` and
`vendor_upstream`/`vendor_doc` distinguish this project's own
hand-authored docs from a vendor's own upstream-authored files
CodeCompass merely indexes (never generates); `pinned_reference` is for a
`spec_doc` row whose leading content is a YAML frontmatter block carrying
both a `resolved_commit` and a `source_url` key — externally-sourced,
revision-pinned reference material a tool materialized into the project
tree, distinct from `project` and never reusing `vendor_upstream` (which
requires a tracked `vendors` row this material deliberately has none of).
`vendor_id` is nullable for tool-level artifacts like the unconditional
tool Skill (`decisions/0020`).

## Edge tables

All six, per
[`relationship-edge.md`](../docs/domain/concepts/relationship-edge.md)'s
own table (reproduced here against the literal schema, not re-derived):

| Table | Connects | Nullable target(s) | `UNIQUE` |
|---|---|---|---|
| `uses_edges` | `source_file_id → vendor_id`/`symbol_id` | `symbol_id` (vendor-level usage with no resolved symbol) | none |
| `documents_edges` | `doc_artifact_id → symbol_id` | `chunk_id` | none |
| `skill_mentions_edges` | `doc_artifact_id → vendor_id`/`source_file_id` | both, independently | none |
| `routes_via_edges` | `vendor_id → doc_artifact_id` | — | `(vendor_id, doc_artifact_id)` |
| `depends_on_edges` | `vendor_id → depends_on_vendor_id` | — | `(vendor_id, depends_on_vendor_id)` |
| `doc_relations_edges` | `source_doc_artifact_id → target_vendor_id`/`target_doc_artifact_id` | both target columns, `chunk_id` | `(source_doc_artifact_id, target_vendor_id, target_doc_artifact_id)` |

`doc_relations_edges.relation_kind` is CHECK'd to exactly
`'mentions_dependency'` or `'mentions_artifact'` — exactly one of
`target_vendor_id`/`target_doc_artifact_id` is set per row, mirroring
`skill_mentions_edges`'s own two-nullable-target shape. A source row's
`kind` is restricted to a closed allow-set (`spec_doc`, `vendor_doc`) —
either a project's own spec doc or a vendor's own embedded upstream doc
can be a relation *source*; every other `doc_artifacts` kind can only
ever be a relation *target*. Two self-mention exclusions prevent
guaranteed-noise edges: a `vendor_doc` row belonging to vendor `V` never
produces a `mentions_dependency` edge targeting `V` itself (a package's
own README mentioning its own name is universal and adds no signal), and
a source row is never matched against its own `path` as a
`mentions_artifact` target (a doc's own first-heading title, once used as
its `name`, is trivially present in that same doc's own text). See
`decisions/0043` for the vendor-name exclusion's full reasoning.

Every edge table foreign-keys with `ON DELETE CASCADE` to its
`vendors`/`symbols`/`doc_artifacts`/`source_files` parent — `graph.py`'s
`open_graph` sets `PRAGMA foreign_keys = ON` per connection (SQLite
defaults this off), so a parent delete during `rebuild_deterministic`
cascades automatically without manual multi-table ordering.

## Enrichment tables — the ones a rebuild never touches

Three tables hold paid AI output and are **never** written by
`rebuild_deterministic` — a comment directly above their `CREATE TABLE`
statements says so explicitly:

- **`vendor_enrichment`** — one row per vendor (`vendor_id` UNIQUE),
  `technical_description`, `conversational_overview`,
  `action_pointer_file`, `action_pointer_note`, `symbol_set_hash`,
  `model`, `generated_at`. Written only by `graph.record_enrichment`
  (`enrichment.py`'s writer).
- **`symbol_enrichment`** — one row per symbol (`symbol_id` UNIQUE),
  `purpose`, `generated_at`. Written only by
  `graph.record_symbol_enrichment`.
- **`doc_relation_enrichment`** — keyed by plain **text** columns
  (`source_doc_path`, `target_vendor_name`, `target_doc_path`), *not* a
  foreign key to `doc_artifacts.id` (`decisions/0038`) — because
  `doc_artifacts` is fully deleted and reinserted every rebuild, a
  foreign key here would cascade this table's whole content away on
  every whole-project sync. Also carries `ai_summary`, `relation_label`
  (CHECK'd to a closed 5-value taxonomy, see below), `content_hash`,
  `model`, `generated_at`. Written only by
  `graph.record_relation_enrichment`. Not upserted via `INSERT ...
  ON CONFLICT DO UPDATE` the way `record_enrichment` is — SQL's `UNIQUE`
  treats every `NULL` as distinct from every other `NULL`, and exactly
  one of `target_vendor_name`/`target_doc_path` is `NULL` per row, so an
  `ON CONFLICT` target naming both would never detect a conflict against
  an existing row whose non-matching column is `NULL`; instead it deletes
  any existing row for the exact triple (NULL-safe `IS` match) and
  inserts fresh, in one transaction.

`vendors`/`symbols` being **upserted** rather than deleted-and-reinserted
is the entire mechanism that lets `vendor_enrichment`/`symbol_enrichment`
survive a rebuild via their own `ON DELETE CASCADE` foreign key without
special-casing: as long as a vendor/symbol's natural key still appears in
the new fixture, its integer id (and anything cascading from it) is
untouched. Only a vendor or symbol that no longer appears in the new
fixture at all is deleted (correctly cascading away its enrichment too,
since the thing it enriched no longer exists).

## `RELATION_LABELS` — the closed taxonomy

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
(the same posture `export_kind`'s own default embodies). The label
describes an already-mechanically-proven relationship; it cannot create,
widen, or narrow *which* relationships get enriched (`decisions/0045`).

## Row dataclasses and natural keys

Every row dataclass `rebuild_deterministic` accepts (`VendorRow` keyed by
`name`, `SourceFileRow` by `path`, `SymbolRow` by `(vendor_name, name)`,
`DocArtifactRow` by `path`, every edge row by the natural keys of what it
connects) references its targets by **natural key, not by pre-assigned
integer id**. This is deliberate, not incidental: the detection logic
that constructs these rows (an AST/regex walk over project source,
doc/Skill mapping) naturally produces vendor names, file paths, and
symbol names — not database-assigned ids — and keeping the row
dataclasses natural-key-shaped means `graph.py` has no import dependency
on any of the modules that build them, avoiding a circular-import risk.
`rebuild_deterministic` resolves natural keys to integer primary keys
internally, building the mapping as it inserts each table in order.

## `rebuild_deterministic` — the one write path for everything except enrichment

One transaction (`with conn:`), in this fixed order:

1. Delete every edge/leaf table unconditionally (`doc_relations_edges`
   through `source_files` — `doc_chunks`, `doc_artifacts` included).
2. Upsert `vendors`, then `symbols` (by natural key), deleting only rows
   whose natural key no longer appears in the new fixture.
3. Insert `source_files`, `doc_artifacts`, `doc_chunks` fresh, building
   natural-key → integer-id maps as it goes.
4. Insert every edge table, resolving each row's natural-key references
   (vendor name, symbol name, doc path, chunk `(path, start_line)`) via
   those maps.
5. Write `meta.last_deterministic_rebuild_at`.

Called from exactly one place: `sync.rebuild_project_graph` — see
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md) for
what assembles the row lists this function is handed.

## Migrations — why four separate functions, not one

`open_graph` runs four migration functions before `init_schema`, each
independently idempotent and each checking its own precondition directly
(`PRAGMA table_info`, or the stored `CREATE TABLE` SQL text) rather than
uniformly gating on `meta.schema_version`:

- `_migrate_doc_artifacts_constraints` — the only one that actually drops
  and recreates tables (`doc_artifacts`, `documents_edges`,
  `doc_relations_edges`), because none of the three holds enrichment data
  that must survive.
- `_migrate_doc_relation_enrichment_relation_label`,
  `_migrate_symbols_export_kind_note_columns`,
  `_migrate_vendors_ecosystem_constraint` — each uses `ALTER TABLE ADD
  COLUMN` or (for `vendors`, since SQLite has no `ALTER TABLE` form for
  changing a `CHECK` constraint) a create-copy-drop-rename dance that
  preserves every existing row's `id`, specifically because
  `vendor_enrichment`/`symbol_enrichment` cascade from these tables and
  must not be destroyed by a schema upgrade on an existing project's
  database.

## Read/query functions

Not exhaustive, but every one of these is a real, currently-callable
function, not a design sketch: `unused_vendors`, `documented_but_unused`,
`used_but_undocumented`, `spec_docs_without_relations`,
`vendor_docs_without_relations`, `doc_relations`, `doc_code_trace`,
`vendor_profile`, `symbol_profile`, `skills_index`,
`enrichment_candidates`, `has_enrichment`,
`relation_enrichment_candidates`. Each is read-only except the three
enrichment writers (`record_enrichment`, `record_symbol_enrichment`,
`record_relation_enrichment`) and `rebuild_deterministic` itself —
`graph.py` has no other write path. `graph.py` deliberately never decides
staleness itself: `enrichment_candidates`/`relation_enrichment_candidates`
return whatever hash is currently cached, and it is `enrichment.py`/
`relation_enrichment.py`'s own job to diff that against a freshly-computed
one.

`vendor_profile`/`symbol_profile` surface real `(file, line)` usage
locations (`used_at`) alongside usage counts. `doc_code_trace` is a
query-time composition of edges already in the graph (no new table):
given a doc artifact path, it unions what that doc documents (via
`documents_edges → symbols → uses_edges`) with what it mentions (via its
own outgoing `mentions_dependency` `doc_relations_edges → vendors →
uses_edges`); given a vendor name instead, it returns that vendor's own
`uses_edges` directly. `'documents'`/`'mentions_dependency'` rows also
carry `heading` — the doc-side heading enclosing the edge, when it has a
`chunk_id`.
