# The context graph (`context-graph.db`)

Part of the `architecture/` reference set. See [`overview.md`](overview.md)
for the system-at-a-glance entry point; the rest of this set:
[`module-map.md`](module-map.md), [`core-data-model.md`](core-data-model.md),
[`adapter-interface.md`](adapter-interface.md),
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md).

Full schema as of `src/codecompass/graph.py`'s `_SCHEMA_SQL`, schema
version `"11"`. One SQLite file at the project root, opened via
`open_graph(project_root)`, which runs foreign-key-enabling PRAGMA, six
in-place migrations (for an on-disk database whose `doc_artifacts`/
`symbols`/`vendors`/`doc_relation_enrichment`/`symbol_enrichment`/
`source_files` shape predates the current one), then `init_schema`'s
idempotent `CREATE TABLE IF NOT EXISTS`. See
[`docs/domain/concepts/context.md`](../docs/domain/concepts/context.md)
sense 1 and
[`relationship-edge.md`](../docs/domain/concepts/relationship-edge.md)
for what this graph means conceptually; this page is the literal schema.

## Node tables

| Table | Key columns | Notes |
|---|---|---|
| `meta` | `key` (PK), `value` | `schema_version` (informational bookkeeping since Phase 76 — no migration's own trigger condition reads it any more), `last_deterministic_rebuild_at`, `git_topology_status`/`git_topology_reason` (Phase 76 — see "Git topology tables" below; absent entirely, as opposed to any of the four real status values, means "never indexed under Phase-76-aware code"), `source_index_version` (Phase 77 — see "First-party source tables" below; absent means "first-party source has never been indexed under Phase-77-aware code"). |
| `vendors` | `name` UNIQUE, `ecosystem` CHECK'd to the 4-member set, `installed_version`, `repository_url`, `repository_subdirectory`, `source_resolved`, `source_resolution_error`, `last_synced_at` | **Upserted** by `name` on every rebuild — never deleted-and-reinserted while still present in the new fixture, so its integer `id` (and anything foreign-keying to it) is stable across syncs. |
| `source_files` | `path` UNIQUE, `language` (nullable — a *first-party* language, `('python'\|'rust'\|'javascript'\|'typescript'\|'haskell')` in practice, not `CHECK`-constrained; deliberately distinct from `vendors.ecosystem`, Phase 77), `content_hash` (nullable), `symbol_index_status` (nullable, CHECK'd to a 5-value set — see below), `symbol_index_diagnostic` (nullable) | **Every recognized first-party source file** (Phase 77 — broadened from "only a file with a detected vendor-import" to the full first-party file set, independent of `vendor.toml`). **Upserted** by `path`, same stability guarantee as `vendors`/`symbols`. All four non-`path` columns are nullable identically on a fresh or a migrated database (`decisions/0065`) — `NULL` means unresolved/legacy, never a database-history-dependent inconsistency. |
| `symbols` | `(vendor_id, name)` UNIQUE, `purpose`, `export_kind` CHECK'd `('export'\|'reexport'\|'undetermined')` default `'export'`, `note` | Also **upserted** by natural key, for the same enrichment-preservation reason as `vendors`. Vendor API-surface symbols only — see `source_symbols` below for a project's own first-party implementation symbols, a structurally separate table, never a nullable `vendor_id` here. |
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
  `purpose`, `model` (nullable — Phase 74; a pre-Phase-74 row honestly
  backfills `NULL`, never a fabricated value, unlike the two `NOT NULL`
  `model` columns above/below), `generated_at`. Written only by
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

## Git topology tables (Phase 76)

Three tables — `git_repositories`, `git_worktrees`, `git_submodules` —
plus two `meta` keys (`git_topology_status`, `git_topology_reason`), all
written by `rebuild_deterministic`, fully cleared and reinserted every
rebuild (no cross-rebuild identity to preserve, same category as
`doc_artifacts`). Detection lives in `git_topology.py`, entirely separate
from `graph.py` — `sync.py::rebuild_project_graph` is the only place that
converts `git_topology.detect_git_topology`'s own plain dataclasses into
these row types, the same "detection module stays graph-agnostic"
pattern `usage.DetectedImport → graph.UsesEdgeRow` already establishes.
See `planning/phase-76-git-repository-topology.md` and `decisions/0063`
for the full design rationale.

| Table | Key columns | Notes |
|---|---|---|
| `git_repositories` | `common_dir` UNIQUE, `origin_url` (sanitized — credentials never persisted) | Identified by the absolute path to the shared `.git` directory — identical across every worktree of one repository, deliberately never the invocation directory or any per-worktree path. |
| `git_worktrees` | `repository_id → git_repositories`, `worktree_path`, `is_current`, `branch`, `is_detached`, `head_commit`, `is_dirty` (nullable — **always `NULL` for a non-current/sibling worktree**, by design: probing a sibling's workspace state is never attempted), `is_bare`, `is_locked`, `is_prunable` | One row per worktree `git worktree list --porcelain` reports, not only the current one. `is_bare` can be `1` for a *sibling* row (a bare "hub" repository with linked, non-bare worktrees is representable); the *current* worktree can never carry `is_bare=1`, since a bare repository as the current checkout is out of scope entirely (`git_topology_status='unavailable'`, no `git_worktrees` row for "self" is ever built). |
| `git_submodules` | `parent_repository_id → git_repositories`, `path`, `is_path_safe`, `child_repository_url` (sanitized), `pinned_commit` (nullable), `is_initialized` (nullable), `checked_out_commit`, `revision_matches_pin`, `child_branch`, `child_is_dirty` | One row per path `.gitmodules` declares — always emitted once declared, regardless of how much else is resolvable (`pinned_commit=NULL` when `.gitmodules` names a path with no corresponding gitlink in `HEAD`'s tree yet; every child-state field `NULL` when not initialized). `is_path_safe=0` means the declared path, resolved against the repository's own worktree root, escaped it — every other field is left unset and **no `git`/filesystem command is ever run against that path**. |

`meta.git_topology_status` is one of `detected` / `not_git` / `unavailable`
/ `partial` (`git_topology.TopologyStatus`) — a **whole-pass** status
("could repository identity and the worktree/submodule lists be
enumerated at all"), entirely distinct from the per-row nullable columns
above, which represent per-fact uncertainty *within* a structure that
*was* successfully enumerated. `unavailable` covers both "`git` missing"
and "no working tree" (a bare repository as the current checkout — not
supported, detected honestly via the distinctive `git rev-parse
--show-toplevel` failure message, never conflated with `not_git`).
`partial` means repository identity was established but a subsequent
enumeration step (worktree list, `.gitmodules` read) failed unexpectedly
— the structure that *was* established is still persisted, not
discarded. The key's own **absence** (as opposed to any of these four
values) means "no sync has ever run under Phase-76-aware code" —
`cli.py::query_topology` checks for this before ever reading the value,
and never invokes `git` itself on any path, including this one.

Requires Git 2.7+ (`decisions/0064`) — `--git-common-dir` itself only
needs Git 2.5, but `git worktree list`/`git remote get-url`, both called
unconditionally on every detection pass, need 2.7; no feature newer than
2.7 is used anywhere in `git_topology.py`. A Git older than 2.7 is
detected via a single `git --version` check and surfaces as
`unavailable` with an explicit, version-naming `git_topology_reason`,
never a crash.

## First-party source tables (Phase 77)

`source_files` (extended, see above) plus a new `source_symbols` table,
plus one `meta` key (`source_index_version`). Closes `CG-009`: a
project's own first-party source files/top-level implementation symbols
are now durable, queryable objects, independent of `vendor.toml` — works
identically at 0 tracked vendors. Detection lives in
`source_symbols.py`, entirely separate from `graph.py` (the same
"detection module stays graph-agnostic" pattern `git_topology.py`/
`usage.py` already establish); `sync.py::rebuild_project_graph` is the
only place that converts its plain dataclasses into these row types. See
`planning/phase-77-first-party-source-and-template.md` and
`decisions/0065` for the full design rationale.

| Table | Key columns | Notes |
|---|---|---|
| `source_symbols` | `(source_file_id, name, kind, line)` UNIQUE, `line` **`NOT NULL`**, `purpose` (nullable), `exposure` CHECK'd to a 5-value set | **Occurrence-based identity, not name-only** — a top-level declaration's identity includes its own location, since a real language feature (function overloading) produces multiple genuinely distinct declarations sharing one name (live-verified on both Python `@typing.overload` and TypeScript). `line` is never `NULL`: an extractor unable to determine a location for a candidate does not emit a row for it at all. **Upserted** by this natural key, same stability guarantee as `vendors`/`symbols`/`source_files`. |

`source_files.symbol_index_status` closed set: `indexed` (a real
structural parser ran — Python's own `ast`, today), `indexed_partial` (a
coarse line-scan/regex technique ran — Rust and JS/TS, today; concrete
fidelity limits below), `unsupported` (no extractor exists for this
file's language — Haskell, today), `parse_error` (the language's own
parser rejected the file — Python-specific, since Rust/JS/TS's coarse
techniques have no real "parse" step to fail structurally), `unreadable`
(the file itself could not be read).
`symbol_index_diagnostic` carries the caught exception's own message for
`parse_error`/`unreadable`, `NULL` otherwise. Modeled directly on
`git_topology.RepositoryTopology`'s own status+reason+data shape — an
empty `symbols` list for `indexed`/`indexed_partial` is a real, valid,
distinct outcome ("genuinely no top-level symbols"), never conflated
with any failure state.

`source_symbols.exposure` closed set: `public`, `restricted`,
`internal`, `conventional_private`, `unknown` — a genuinely
cross-language classification, not a simplistic public/private binary.
Python's leading-underscore convention maps to `conventional_private`
(a naming *convention* with one real language-level consequence, `from
module import *`'s own exclusion — deliberately distinct from
`internal`, which means a language *itself* enforces non-visibility).
Rust's real three-tier visibility maps to `public` (bare `pub`),
`restricted` (`pub(crate)`/`pub(super)`/`pub(in ...)`), or `internal` (no
modifier) — live-verified against 8 representative declarations.
JS/TS maps `export` to `public`, its absence to `internal` (no
`restricted`-equivalent tier exists for these languages). `unknown` is
reserved for a future, less-certain extractor — not actually produced by
any extractor this phase ships. **Recorded as a separate property, never
used to filter a symbol out of the table** — first-party symbol
extraction answers "what does this project implement," not "what public
API does this dependency expose" (the question vendor `symbols.export_kind`
answers); a non-exported/private top-level declaration is still a real
row.

`meta.source_index_version` is a plain version marker (`"1"` today, not
a multi-state status enum — first-party discovery has no "could the
structure be enumerated at all" failure mode the way Git topology
detection does; it either ran, or it hasn't yet), written unconditionally
by `rebuild_deterministic` whenever a genuinely Phase-77-aware rebuild
runs, **regardless of whether any first-party source files were actually
found** (mirroring `git_topology_status`'s own "written even with zero
worktrees" precedent). The key's own **absence** means "first-party
source has never been indexed under Phase-77-aware code" —
`cli.py::query_source`/`query_source_symbol` check for this before ever
reading `source_files`/`source_symbols`, and remain read-only throughout
(never invoke a rebuild). Kept structurally separate from the per-file
`symbol_index_status` above — a whole-project "has indexing ever run"
fact and a per-file "what happened when it did" fact answer different
questions, the same two-level-uncertainty discipline `git_topology_status`
(whole-pass) vs. its own per-row nullable columns already established,
applied here as the same two-level shape at a different granularity
(whole-*project* vs. per-*file*, rather than whole-*pass* vs. per-*row*).

### Known fidelity limitations of `indexed_partial` and Python extraction

`decisions/0065` and the Phase 77 plan describe `indexed_partial`'s
coarse-technique risk only in general prose ("a multi-line signature, an
unusual formatting style, or a false match inside a string/comment can
defeat them"). Live probing against real Rust/JS/TS/Python source
narrows that down to specific, reproducible shapes, not a diffuse
"unusual formatting" risk:

- A parameter list spanning multiple physical lines does **not** defeat
  either regex-based extractor — both item regexes only need to match
  the keyword+name text on the line where a declaration's own name first
  appears.
- A single-line `//` comment or single-line string literal containing
  declaration-like text does **not** produce a false match — both regexes
  anchor against each line's own stripped leading content.
- A multi-line Rust raw-string literal whose interior line matches the
  anchored pattern **does** produce a genuine, silent false-positive
  `source_symbols` row — e.g. a raw string embedding `pub fn
  embedded_in_string() {}` on its own line.
- A plain `/* ... */` block comment in JS/TS — as opposed to a `/**`
  JSDoc comment, which is specially recognized — is not treated as a
  comment at all, so a commented-out declaration inside one **does**
  produce a genuine, silent false-positive row.

Both real false-positive shapes are silent: `symbol_index_status` stays
`indexed_partial`, `symbol_index_diagnostic` stays `NULL`, and nothing in
the returned extraction result distinguishes the false-positive row from
a genuine declaration.

Two further limitations affect extraction *scope* rather than
correctness of what's matched, independent of the false-positive
boundary above, and are structural properties of how the extractors are
built rather than untested edge cases:

- **Python extraction is top-level-only.** Only the module's own direct
  children are visited (`ast.iter_child_nodes` on the module node, not a
  recursive walk) — a method defined inside a class, or a function nested
  inside another function, is never visited and never emitted as its own
  `source_symbols` row.
- **A JS/TS `const` binding's `kind` is always recorded literally as
  `"const"`, never `"function"`**, regardless of what it's bound to — the
  extractor assigns `kind` directly from the matched keyword with no
  inspection of the right-hand side of an `=`. `export const useWidget =
  () => {}` is therefore schema-indistinguishable from `export const PI =
  3.14`.

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
5. Insert `git_repositories`, then `git_worktrees`/`git_submodules`
   (resolved against `git_repositories` by `common_dir`), then write
   `meta.git_topology_status`/`git_topology_reason` (Phase 76) — only
   when the caller actually supplies a status; an old caller/test that
   omits them leaves those two `meta` keys untouched, never fabricated.
6. Write `meta.last_deterministic_rebuild_at`.

Called from exactly one place: `sync.rebuild_project_graph` — see
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md) for
what assembles the row lists this function is handed.

## Migrations — why six separate functions, not one

`open_graph` runs six migration functions before `init_schema`, each
independently idempotent and **each checking its own precondition
directly** (`PRAGMA table_info`, or the stored `CREATE TABLE` SQL text)
— **none of them gates on `meta.schema_version`** (Phase 76:
`_migrate_doc_artifacts_constraints` was the last holdout still doing
this; `git log` confirms its old version-diff trigger had already fired
unnecessarily twice, for two unrelated schema bumps — Phase 60's
`vendors.ecosystem` widening and Phase 62's `symbols.export_kind`/`note`
addition, neither of which touched `doc_artifacts` at all — before being
brought into line with this file's own other four migrations'
introspection style):

- `_migrate_doc_artifacts_constraints` — the only one that actually drops
  and recreates tables (`doc_artifacts`, `documents_edges`,
  `doc_relations_edges`), because none of the three holds enrichment data
  that must survive. Triggers only when `_doc_artifacts_schema_is_current`
  (direct introspection of the stored CHECK-constraint text and column
  set) says the on-disk shape is genuinely stale — never merely because
  `meta.schema_version` differs from `_SCHEMA_VERSION`.
- `_migrate_doc_relation_enrichment_relation_label`,
  `_migrate_symbols_export_kind_note_columns`,
  `_migrate_symbol_enrichment_model_column`,
  `_migrate_vendors_ecosystem_constraint` — each uses `ALTER TABLE ADD
  COLUMN` or (for `vendors`, since SQLite has no `ALTER TABLE` form for
  changing a `CHECK` constraint) a create-copy-drop-rename dance that
  preserves every existing row's `id`, specifically because
  `vendor_enrichment`/`symbol_enrichment` cascade from these tables and
  must not be destroyed by a schema upgrade on an existing project's
  database.
- `_migrate_source_files_columns` (Phase 77) — adds `source_files`'s four
  new nullable columns (`language`, `content_hash`,
  `symbol_index_status`, `symbol_index_diagnostic`) via `ALTER TABLE ADD
  COLUMN`, for the identical reason: `source_files.id` is referenced by
  `uses_edges.source_file_id ON DELETE CASCADE`, so a drop-and-recreate
  here would destroy real usage-edge data on an existing project's
  database, exactly the class of risk `decisions/0064` fixed for
  `doc_artifacts`.

`meta.schema_version` itself is updated unconditionally, on every
`open_graph` call, regardless of what any migration above decided —
purely informational bookkeeping ("last schema-code vintage this
database was opened under"), read by no migration's own trigger
condition and by nothing else in `src/codecompass/`.

## Read/query functions

Not exhaustive, but every one of these is a real, currently-callable
function, not a design sketch: `unused_vendors`, `documented_but_unused`,
`used_but_undocumented`, `spec_docs_without_relations`,
`vendor_docs_without_relations`, `doc_relations`, `doc_code_trace`,
`vendor_profile`, `symbol_profile`, `skills_index`,
`enrichment_candidates`, `has_enrichment`,
`relation_enrichment_candidates`, `topology_profile` (Phase 76 — `None`
if `meta.git_topology_status` was never written, the "not yet indexed"
case `cli.py::query_topology` renders without ever invoking `git`).
Each is read-only except the three
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
