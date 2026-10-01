# Architecture: the persistence layer (`context-graph.db`)

**Provenance tier: CONFIRMED-LIVE.** Source:
`phase80-implementation-reconstruction.md` §3. `graph.py` (2428 lines) is
the single largest, most load-bearing module in the Stage 2 evidence
base, and its real test file (`test_graph.py`, 75 tests) actually ran in
the sandbox with 100% passing. This is a "building block" / static view:
what exists and what its lifecycle guarantees are. For what actually
calls into this layer at runtime, see `05-runtime-pipelines.md` (a
materially lower confidence tier — read-only, not run).

The file is a SQLite database, `context-graph.db`, with an informational
schema version string (currently `"11"`; see "Migrations" below for why
this version string is no longer load-bearing for migration logic).

## Tables

Schema creation is idempotent (`CREATE TABLE IF NOT EXISTS`).

- **`meta`** — key/value store.
- **`vendors`** — `name` UNIQUE; `ecosystem` constrained to
  `npm`/`python`/`cargo`/`haskell`; installed version; repository
  URL/subdirectory; source-resolution status and error; last-synced
  timestamp.
- **`source_files`** — `path` UNIQUE; language, content hash, and
  symbol-index status/diagnostic, all nullable; status constrained to
  `indexed`/`indexed_partial`/`unsupported`/`parse_error`/`unreadable`.
- **`source_symbols`** — occurrence-keyed (`UNIQUE(source_file_id, name,
  kind, line)`, `line NOT NULL`); exposure constrained to
  `public`/`restricted`/`internal`/`conventional_private`/`unknown`.
- **`symbols`** — `UNIQUE(vendor_id, name)`; `export_kind` defaults to
  `'export'`; free-text `note`. **Symbol names are not globally unique
  across vendors** — a fact the CLI's `query symbol` command depends on
  directly (see `02-cli-reference.md`).
- **`uses_edges`** — `source_file_id`, `vendor_id`, nullable `symbol_id`,
  nullable `line`.
- **`doc_chunks`**, **`doc_artifacts`** — `doc_artifacts.path` UNIQUE;
  `kind` constrained to `claude_md`/`overview`/`skill`/`cursor_mdc`/
  `slash_command`/`spec_doc`/`vendor_doc`; `origin` constrained to
  `codecompass_tool`/`codecompass_vendor`/`third_party`/`project`/
  `vendor_upstream`/`pinned_reference`.
- **`documents_edges`**, **`skill_mentions_edges`**, **`routes_via_edges`**
  (unique per vendor+doc), **`depends_on_edges`** (unique vendor pair).
- **`doc_relations_edges`** — `relation_kind` constrained to
  `mentions_dependency`/`mentions_artifact`; unique on
  source+target_vendor+target_doc.
- **`vendor_enrichment`**, **`symbol_enrichment`**,
  **`doc_relation_enrichment`** — the three AI-enrichment tables; see
  "Enrichment survives rebuilds" below. `relation_label` is constrained
  to a closed set: `documents_configuration_of`/`explains_usage_of`/
  `contrasts_with`/`supersedes`/`other`.
- **`git_repositories`**, **`git_worktrees`**, **`git_submodules`** —
  git-topology tables, fully cleared and reinserted every rebuild, with
  no cross-rebuild row identity. Architecturally distinct from the six
  content-edge tables above even though they share the same
  wipe/reinsert lifecycle: every one of the six content-edge tables has
  at least one endpoint among vendors/symbols/source-files/doc-artifacts,
  while the git-topology tables connect only to each other
  (`codecompass-overview@v1#CL-CTXT-006`).

The six content-edge tables above (`uses_edges`, `documents_edges`,
`skill_mentions_edges`, `routes_via_edges`, `depends_on_edges`,
`doc_relations_edges`) are exactly the set that "relationship" and
"edge" refer to precisely elsewhere in this draft — see
`01-concepts.md`.

## The core rebuild function: `rebuild_deterministic`

`rebuild_deterministic(conn, **row_sequences)` is the one function that
rewrites the graph's content on every whole-project sync. Its behavior,
confirmed directly by running `test_graph.py`:

- **Wipes and reinserts unconditionally**, inside one transaction: every
  edge/leaf table (`doc_relations_edges`, `depends_on_edges`,
  `routes_via_edges`, `skill_mentions_edges`, `documents_edges`,
  `uses_edges`, `doc_chunks`, `doc_artifacts`), plus all three git-topology
  tables.
- **Upserts by natural key**: `vendors` (by name), `symbols` (by
  vendor+name), `source_files` (by path), `source_symbols` (by
  file+name+kind+line). A dedicated passing test confirms row ids remain
  stable across repeated rebuilds for unchanged rows
  (`test_rebuild_deterministic_preserves_vendor_id_across_rebuilds`,
  and the equivalent for `source_files`). Rows present before a rebuild
  but absent from the new input are explicitly deleted (also
  test-confirmed).
- **Is genuinely idempotent**: running the function twice with identical
  input produces identical row counts, not duplicates
  (`test_rebuild_deterministic_is_repeatable_without_duplicating_rows`).
- **Never touches the three enrichment tables** —
  `vendor_enrichment`/`symbol_enrichment`/`doc_relation_enrichment`.
  Dedicated tests write an enrichment row, rebuild the graph again, and
  assert the row is byte-identical before and after. This is the actual
  mechanism by which paid AI-enrichment output survives a plain
  mechanical `sync` — not a convention or a comment, a tested guarantee.
- Writes `meta.last_deterministic_rebuild_at` on every call, and
  conditionally writes `meta.git_topology_status`/`git_topology_reason`
  and `meta.source_index_version` only when the caller actually supplies
  them — confirmed by a test proving "indexed, zero results" is
  distinguishable from "never indexed."

## Migrations: introspection, not a version counter

Six in-place migration functions run unconditionally at every
`open_graph()` call. Each is self-gated by **directly inspecting the
real schema** (`PRAGMA table_info`, or reading `sqlite_master.sql` text
for a specific constraint), **not** by comparing `meta.schema_version`.
The code's own comments state this was a deliberate choice, after
`meta.schema_version` was found (via project history, not independently
re-verified in this evidence base) to have been bumped twice for
unrelated schema changes — which would have falsely triggered migrations
if the version number had been trusted. All six migrations are exercised
directly against hand-built pre-migration schema fixtures and all of
them pass, including, for instance, a migration that widens the
`vendors.ecosystem` constraint for a newly-added ecosystem value.

Two migration strategies are used depending on data-loss risk:

- `ALTER TABLE ... ADD COLUMN` for anything that would otherwise
  cascade-delete enrichment data through a foreign key.
- Drop-and-recreate, used only for tables that are fully rewritten on
  every sync anyway (`doc_artifacts`, `documents_edges`,
  `doc_relations_edges`), where there is nothing to lose.
- A `vendors` CHECK-constraint widening (adding a new ecosystem value)
  uses a copy-into-new-table-and-rename approach, since SQLite cannot
  `ALTER` a CHECK constraint in place.

This is a genuinely high-value, currently undocumented-elsewhere piece of
maintainer knowledge: if you add a new table or constraint to this
schema, follow the introspection-gated pattern above, not a version-bump
pattern — see `06-extension-points.md`.
