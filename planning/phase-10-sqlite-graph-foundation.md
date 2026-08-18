# Phase 10: SQLite graph foundation

## Scope

**Covered:**
- `src/codecompass/graph.py` (new) — the SQLite persistence layer every
  later phase in this arc (11-16) builds on. Pure library in this phase:
  a schema, a set of typed row dataclasses as the insertion contract, a
  full-rebuild orchestrator, and read-only query functions. **Not called
  from `sync.py` or `cli.py` yet** — that wiring starts in Phase 11
  (usage detection) and continues through Phase 15 (CLI rewire).
- Schema (see Design decisions below), created via `init_schema(conn)` —
  idempotent `CREATE TABLE IF NOT EXISTS` for every table plus a `meta`
  table (`schema_version`, `last_deterministic_rebuild_at`).
- `open_graph(project_root: Path) -> sqlite3.Connection` — resolves
  `context-graph.db` at the project root, connects (creating the file if
  absent), calls `init_schema`, returns the connection. The one function
  later phases actually call to get a working handle.
- Row dataclasses as `rebuild_deterministic`'s input contract —
  `VendorRow`, `SourceFileRow`, `SymbolRow`, `UsesEdgeRow`,
  `DocArtifactRow`, `DocumentsEdgeRow`, `SkillMentionEdgeRow`,
  `RoutesViaEdgeRow`, `DependsOnEdgeRow` — defined in `graph.py` itself
  (not `core.py`; these are graph-persistence-specific, not shared
  domain types, matching how `deptree.py`/`filetree.py` already keep
  their own local types rather than growing `core.py` unboundedly).
  Phases 11-13 (usage detection, doc/skill mapping) will construct these
  from their own detection logic; `graph.py` has no import dependency on
  those not-yet-existing modules, avoiding any circular-import risk.
- `rebuild_deterministic(conn, *, vendors, source_files, symbols,
  uses_edges, doc_artifacts, documents_edges, skill_mentions_edges,
  routes_via_edges, depends_on_edges) -> None` — wipes and rewrites every
  deterministic table inside one transaction, updates
  `meta.last_deterministic_rebuild_at`, and **never touches
  `vendor_enrichment`/`symbol_enrichment`** — this is the mechanical
  reason Phase 14's enrichment output survives a later Phase A refresh
  (`decisions/0025`'s rebuild-trigger posture, carried forward by
  `decisions/0032`).
- Query functions, each a plain read against already-populated tables:
  - `unused_vendors(conn) -> list[str]`
  - `documented_but_unused(conn) -> list[tuple[str, str]]` (vendor,
    symbol pairs)
  - `used_but_undocumented(conn) -> list[tuple[str, str]]`
  - `vendor_profile(conn, name) -> dict | None` — vendor row + its
    symbols + usage count + documenting artifacts + routed Skill +
    `depends_on` list
  - `symbol_profile(conn, name) -> list[dict]` — every match across
    vendors (symbol names aren't globally unique)
  - `skills_index(conn) -> list[dict]` — every `doc_artifacts` row with
    `kind='skill'`, its `origin`, and what it mechanically mentions
  - `enrichment_candidates(conn) -> list[dict]` — every vendor with ≥1
    `uses_edges` row, its currently-used symbol names, and its existing
    `vendor_enrichment.symbol_set_hash` if any (Phase 14's `enrichment.py`
    diffs this itself; `graph.py` doesn't decide staleness)
- `record_enrichment(conn, vendor_id, **fields)` /
  `record_symbol_enrichment(conn, symbol_id, purpose, generated_at)` —
  the only writers to the two enrichment tables, kept separate from
  `rebuild_deterministic` on purpose.
- `.gitignore`: add `context-graph.db` (extends the existing `vendor/`
  entry's precedent — a deterministic, cheaply-regeneratable artifact).
- Tests: `tests/test_graph.py` (new) — schema creation, insertion via
  `rebuild_deterministic` with synthetic fixture rows (no real
  usage-detection data exists yet — Phase 11 supplies that), every query
  function against known fixture state, and a rebuild-doesn't-touch-
  enrichment regression test (insert enrichment rows, call
  `rebuild_deterministic`, assert they're unchanged).
- Same-commit docs: `architecture/overview.md` gains a new "Context
  graph" section describing `graph.py`'s schema and API as it exists
  after this phase (library only — later phases extend this section in
  place rather than rewriting it), `planning/ROADMAP.md`,
  `planning/CONTEXT.md`, `CHANGELOG.md`.

**Explicitly deferred / out of scope:**
- Any actual population from real project data — `usage.py` (Phase 11),
  `doc_mapping.py`/`skill_scan.py` (Phase 12) don't exist yet. This
  phase's tests exercise `graph.py` entirely through synthetic fixture
  rows.
- Wiring into `sync.py`'s whole-project path — Phase 11.
- Any CLI command (`codecompass query`, `check`'s new coverage-gap
  sections) — Phase 15.
- The enrichment cache-key mechanism's *producer* side (computing a
  symbol-set hash from real usage data, writing it into `CLAUDE.md`) —
  Phase 14. This phase only provides the table column
  (`vendor_enrichment.symbol_set_hash`) and the writer function.
- `DocChunk`/`EXPLAINS` tables — explicitly deferred per `decisions/0032`
  and the former phase-9d design; not part of this schema at all, not
  even as unused tables.

## Design decisions

See `decisions/0032` for full reasoning (SQLite over the original
`decisions/0024` JSON-file choice) and `decisions/0025` (rebuild-trigger
posture, carried forward unchanged). Schema:

```sql
CREATE TABLE meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE vendors (
  id                      INTEGER PRIMARY KEY,
  name                    TEXT NOT NULL UNIQUE,
  ecosystem               TEXT NOT NULL CHECK (ecosystem IN ('npm','python','cargo')),
  installed_version       TEXT,
  repository_url          TEXT,
  repository_subdirectory TEXT,
  source_resolved         INTEGER NOT NULL DEFAULT 0,
  source_resolution_error TEXT,
  last_synced_at          TEXT
);

CREATE TABLE source_files (
  id   INTEGER PRIMARY KEY,
  path TEXT NOT NULL UNIQUE
);

CREATE TABLE symbols (
  id        INTEGER PRIMARY KEY,
  vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  name      TEXT NOT NULL,
  purpose   TEXT,
  UNIQUE (vendor_id, name)
);
CREATE INDEX idx_symbols_vendor ON symbols(vendor_id);

CREATE TABLE uses_edges (
  id             INTEGER PRIMARY KEY,
  source_file_id INTEGER NOT NULL REFERENCES source_files(id) ON DELETE CASCADE,
  vendor_id      INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  symbol_id      INTEGER REFERENCES symbols(id) ON DELETE CASCADE,
  line           INTEGER
);
CREATE INDEX idx_uses_vendor ON uses_edges(vendor_id);
CREATE INDEX idx_uses_symbol ON uses_edges(symbol_id);
CREATE INDEX idx_uses_source_file ON uses_edges(source_file_id);

CREATE TABLE doc_artifacts (
  id          INTEGER PRIMARY KEY,
  vendor_id   INTEGER REFERENCES vendors(id) ON DELETE CASCADE,
  kind        TEXT NOT NULL CHECK (kind IN ('claude_md','overview','skill','cursor_mdc')),
  origin      TEXT CHECK (origin IN ('codecompass_tool','codecompass_vendor','third_party')),
  path        TEXT NOT NULL UNIQUE,
  name        TEXT,
  description TEXT
);

CREATE TABLE documents_edges (
  id              INTEGER PRIMARY KEY,
  doc_artifact_id INTEGER NOT NULL REFERENCES doc_artifacts(id) ON DELETE CASCADE,
  symbol_id       INTEGER NOT NULL REFERENCES symbols(id) ON DELETE CASCADE
);

CREATE TABLE skill_mentions_edges (
  id              INTEGER PRIMARY KEY,
  doc_artifact_id INTEGER NOT NULL REFERENCES doc_artifacts(id) ON DELETE CASCADE,
  vendor_id       INTEGER REFERENCES vendors(id) ON DELETE CASCADE,
  source_file_id  INTEGER REFERENCES source_files(id) ON DELETE CASCADE
);

CREATE TABLE routes_via_edges (
  id              INTEGER PRIMARY KEY,
  vendor_id       INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  doc_artifact_id INTEGER NOT NULL REFERENCES doc_artifacts(id) ON DELETE CASCADE,
  UNIQUE (vendor_id, doc_artifact_id)
);

CREATE TABLE depends_on_edges (
  id                   INTEGER PRIMARY KEY,
  vendor_id            INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  depends_on_vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  UNIQUE (vendor_id, depends_on_vendor_id)
);

-- Survive every rebuild_deterministic call:
CREATE TABLE vendor_enrichment (
  id                      INTEGER PRIMARY KEY,
  vendor_id               INTEGER NOT NULL UNIQUE REFERENCES vendors(id) ON DELETE CASCADE,
  technical_description   TEXT,
  conversational_overview TEXT,
  action_pointer_file     TEXT,
  action_pointer_note     TEXT,
  symbol_set_hash         TEXT NOT NULL,
  model                   TEXT NOT NULL,
  generated_at            TEXT NOT NULL
);

CREATE TABLE symbol_enrichment (
  id           INTEGER PRIMARY KEY,
  symbol_id    INTEGER NOT NULL UNIQUE REFERENCES symbols(id) ON DELETE CASCADE,
  purpose      TEXT NOT NULL,
  generated_at TEXT NOT NULL
);
```

`ON DELETE CASCADE` matters specifically because `rebuild_deterministic`
deletes and reinserts `vendors`/`source_files` rows wholesale each run —
cascading avoids needing to manually clear every dependent table in a
specific order. Foreign keys must be enabled per-connection
(`PRAGMA foreign_keys = ON`, SQLite's default is off) — `open_graph` sets
this immediately after connecting.

## Files

- `src/codecompass/graph.py` (new) — see Scope above.
- `tests/test_graph.py` (new).
- `.gitignore` — add `context-graph.db`.
- `architecture/overview.md` — new "Context graph" section (library-only
  state after this phase).
- `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md` — updated
  in place, same commit (`CLAUDE.md` §2).

## Verification

- `pytest` — full suite passes, including `tests/test_graph.py`; no live
  API call anywhere (none are made in this phase's code at all).
- `ruff check .` — clean.
- Manual: in a scratch SQLite session, run `open_graph` against a temp
  directory, call `rebuild_deterministic` with a small synthetic fixture
  (2 vendors, one used, one not; one symbol each; one doc artifact
  documenting the used vendor's symbol), then confirm each query function
  returns the expected result — `unused_vendors` lists exactly the
  unused one, `used_but_undocumented`/`documented_but_unused` are both
  empty for the fully-covered vendor, `vendor_profile` returns a
  populated dict for the used vendor and `None` for a nonexistent name.
- Regression check: insert a `vendor_enrichment` row via
  `record_enrichment`, call `rebuild_deterministic` again with the same
  fixture, confirm the enrichment row is still present and unchanged
  afterward — the concrete proof that deterministic rebuilds don't
  clobber paid enrichment output.
