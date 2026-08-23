"""SQLite persistence layer for the project-wide context graph.

Pure library in this phase: a schema, a set of typed row dataclasses that
form `rebuild_deterministic`'s insertion contract, a full-rebuild
orchestrator, and read-only query functions. **Not called from `sync.py`
or `cli.py` yet** — that wiring starts in Phase 11 (usage detection) and
continues through Phase 15 (CLI rewire). See architecture/overview.md's
"Context graph" section, planning/phase-10-sqlite-graph-foundation.md,
[`decisions/0032`](../../decisions/0032-context-graph-stored-in-sqlite.md)
(SQLite over the original `decisions/0024` JSON-file choice), and
[`decisions/0025`](../../decisions/0025-context-graph-rebuilds-only-on-whole-project-sync.md)
(rebuild-trigger posture, carried forward unchanged).

Row dataclasses reference each other by natural key (vendor name, source
file path, doc artifact path, symbol name scoped to its vendor) rather
than by pre-assigned integer id — the detection logic in later phases
(usage scanning, doc/skill mapping) naturally produces names and paths,
not opaque database ids, and this keeps `graph.py` free of any import
dependency on those not-yet-existing modules. `rebuild_deterministic`
resolves natural keys to integer primary keys internally.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

_DB_FILENAME = "context-graph.db"
_SCHEMA_VERSION = "6"

# Closed taxonomy for `doc_relation_enrichment.relation_label` (Phase 31,
# decisions/0045). `'other'` is the required fallback for any label an AI
# response returns that isn't in this set — never raises, matches this
# project's established "never raises, degrades to a safe default" posture.
RELATION_LABELS = (
    "documents_configuration_of",
    "explains_usage_of",
    "contrasts_with",
    "supersedes",
    "other",
)
_RELATION_LABEL_CHECK_SQL = "relation_label IN ({})".format(
    ", ".join(f"'{label}'" for label in RELATION_LABELS)
)

_SCHEMA_SQL = f"""
CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vendors (
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

CREATE TABLE IF NOT EXISTS source_files (
  id   INTEGER PRIMARY KEY,
  path TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS symbols (
  id        INTEGER PRIMARY KEY,
  vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  name      TEXT NOT NULL,
  purpose   TEXT,
  UNIQUE (vendor_id, name)
);
CREATE INDEX IF NOT EXISTS idx_symbols_vendor ON symbols(vendor_id);

CREATE TABLE IF NOT EXISTS uses_edges (
  id             INTEGER PRIMARY KEY,
  source_file_id INTEGER NOT NULL REFERENCES source_files(id) ON DELETE CASCADE,
  vendor_id      INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  symbol_id      INTEGER REFERENCES symbols(id) ON DELETE CASCADE,
  line           INTEGER
);
CREATE INDEX IF NOT EXISTS idx_uses_vendor ON uses_edges(vendor_id);
CREATE INDEX IF NOT EXISTS idx_uses_symbol ON uses_edges(symbol_id);
CREATE INDEX IF NOT EXISTS idx_uses_source_file ON uses_edges(source_file_id);

CREATE TABLE IF NOT EXISTS doc_chunks (
  id              INTEGER PRIMARY KEY,
  doc_artifact_id INTEGER NOT NULL REFERENCES doc_artifacts(id) ON DELETE CASCADE,
  heading_path    TEXT NOT NULL,
  start_line      INTEGER NOT NULL,
  end_line        INTEGER NOT NULL,
  content_hash    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_doc_chunks_doc_artifact ON doc_chunks(doc_artifact_id);

CREATE TABLE IF NOT EXISTS doc_artifacts (
  id          INTEGER PRIMARY KEY,
  vendor_id   INTEGER REFERENCES vendors(id) ON DELETE CASCADE,
  kind        TEXT NOT NULL CHECK (
                kind IN (
                  'claude_md','overview','skill','cursor_mdc','slash_command','spec_doc',
                  'vendor_doc'
                )
              ),
  origin      TEXT CHECK (
                origin IN (
                  'codecompass_tool','codecompass_vendor','third_party','project',
                  'vendor_upstream'
                )
              ),
  path        TEXT NOT NULL UNIQUE,
  name        TEXT,
  description TEXT
);

CREATE TABLE IF NOT EXISTS documents_edges (
  id              INTEGER PRIMARY KEY,
  doc_artifact_id INTEGER NOT NULL REFERENCES doc_artifacts(id) ON DELETE CASCADE,
  symbol_id       INTEGER NOT NULL REFERENCES symbols(id) ON DELETE CASCADE,
  chunk_id        INTEGER REFERENCES doc_chunks(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS skill_mentions_edges (
  id              INTEGER PRIMARY KEY,
  doc_artifact_id INTEGER NOT NULL REFERENCES doc_artifacts(id) ON DELETE CASCADE,
  vendor_id       INTEGER REFERENCES vendors(id) ON DELETE CASCADE,
  source_file_id  INTEGER REFERENCES source_files(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS routes_via_edges (
  id              INTEGER PRIMARY KEY,
  vendor_id       INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  doc_artifact_id INTEGER NOT NULL REFERENCES doc_artifacts(id) ON DELETE CASCADE,
  UNIQUE (vendor_id, doc_artifact_id)
);

CREATE TABLE IF NOT EXISTS depends_on_edges (
  id                   INTEGER PRIMARY KEY,
  vendor_id            INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  depends_on_vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  UNIQUE (vendor_id, depends_on_vendor_id)
);

CREATE TABLE IF NOT EXISTS doc_relations_edges (
  id                     INTEGER PRIMARY KEY,
  source_doc_artifact_id INTEGER NOT NULL REFERENCES doc_artifacts(id) ON DELETE CASCADE,
  target_vendor_id       INTEGER REFERENCES vendors(id) ON DELETE CASCADE,
  target_doc_artifact_id INTEGER REFERENCES doc_artifacts(id) ON DELETE CASCADE,
  relation_kind          TEXT NOT NULL CHECK (
                           relation_kind IN ('mentions_dependency','mentions_artifact')
                         ),
  chunk_id               INTEGER REFERENCES doc_chunks(id) ON DELETE SET NULL,
  UNIQUE (source_doc_artifact_id, target_vendor_id, target_doc_artifact_id)
);

-- Survive every rebuild_deterministic call:
CREATE TABLE IF NOT EXISTS vendor_enrichment (
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

CREATE TABLE IF NOT EXISTS symbol_enrichment (
  id           INTEGER PRIMARY KEY,
  symbol_id    INTEGER NOT NULL UNIQUE REFERENCES symbols(id) ON DELETE CASCADE,
  purpose      TEXT NOT NULL,
  generated_at TEXT NOT NULL
);

-- Survives every rebuild_deterministic call, same intent as
-- vendor_enrichment/symbol_enrichment above, but keyed by plain natural-key
-- TEXT columns rather than a foreign key to doc_artifacts.id: unlike
-- vendors/symbols (upserted by natural key, Phase 10), doc_artifacts is
-- fully deleted and reinserted on every rebuild_deterministic call, so a
-- foreign key here would cascade this table's whole content away on every
-- whole-project sync. See decisions/0038.
CREATE TABLE IF NOT EXISTS doc_relation_enrichment (
  id                 INTEGER PRIMARY KEY,
  source_doc_path    TEXT NOT NULL,
  target_vendor_name TEXT,
  target_doc_path    TEXT,
  ai_summary         TEXT NOT NULL,
  relation_label     TEXT CHECK ({_RELATION_LABEL_CHECK_SQL}),
  content_hash       TEXT NOT NULL,
  model              TEXT NOT NULL,
  generated_at       TEXT NOT NULL,
  UNIQUE (source_doc_path, target_vendor_name, target_doc_path)
);
"""


# --- Row dataclasses: rebuild_deterministic's insertion contract ---------


@dataclass(frozen=True)
class VendorRow:
    """One `vendors` row, keyed by `name` (unique)."""

    name: str
    ecosystem: str
    installed_version: str | None = None
    repository_url: str | None = None
    repository_subdirectory: str | None = None
    source_resolved: bool = False
    source_resolution_error: str | None = None
    last_synced_at: str | None = None


@dataclass(frozen=True)
class SourceFileRow:
    """One `source_files` row, keyed by `path` (unique)."""

    path: str


@dataclass(frozen=True)
class SymbolRow:
    """One `symbols` row, keyed by `(vendor_name, name)`."""

    vendor_name: str
    name: str
    purpose: str | None = None


@dataclass(frozen=True)
class UsesEdgeRow:
    """One `uses_edges` row. `symbol_name` is optional — a usage that
    resolves to a vendor but not a specific symbol still records the
    vendor-level edge, matching `uses_edges.symbol_id`'s nullability.
    """

    source_file_path: str
    vendor_name: str
    symbol_name: str | None = None
    line: int | None = None


@dataclass(frozen=True)
class DocChunkRow:
    """One `doc_chunks` row (Phase 32), keyed by `(doc_artifact_path,
    start_line)` — a chunk's start line can't repeat within one doc, so
    that pair is unambiguous without a pre-assigned integer id, the same
    natural-key posture every other row dataclass in this module takes.
    """

    doc_artifact_path: str
    heading_path: str
    start_line: int
    end_line: int
    content_hash: str


@dataclass(frozen=True)
class DocArtifactRow:
    """One `doc_artifacts` row, keyed by `path` (unique). `vendor_name` is
    optional — tool-level artifacts (e.g. the unconditional tool Skill,
    `decisions/0020`) aren't scoped to one vendor.
    """

    path: str
    kind: str
    origin: str | None = None
    vendor_name: str | None = None
    name: str | None = None
    description: str | None = None


@dataclass(frozen=True)
class DocumentsEdgeRow:
    """One `documents_edges` row: a doc artifact documenting one symbol.
    `chunk_start_line` (Phase 32) is the natural-key half of an optional
    reference to the one `doc_chunks` row (by `(doc_artifact_path,
    chunk_start_line)`) whose own text contains the match that produced
    this edge — `None` when the match can't be attributed to exactly one
    chunk (the doc has no headings, or the match appears in more than
    one chunk).
    """

    doc_artifact_path: str
    vendor_name: str
    symbol_name: str
    chunk_start_line: int | None = None


@dataclass(frozen=True)
class SkillMentionEdgeRow:
    """One `skill_mentions_edges` row: a Skill mechanically mentioning a
    vendor and/or a source file. Both are optional independently, matching
    `skill_mentions_edges`' nullable `vendor_id`/`source_file_id`.
    """

    doc_artifact_path: str
    vendor_name: str | None = None
    source_file_path: str | None = None


@dataclass(frozen=True)
class RoutesViaEdgeRow:
    """One `routes_via_edges` row: a vendor routed to a Skill."""

    vendor_name: str
    doc_artifact_path: str


@dataclass(frozen=True)
class DependsOnEdgeRow:
    """One `depends_on_edges` row: a vendor depending on another vendor."""

    vendor_name: str
    depends_on_vendor_name: str


@dataclass(frozen=True)
class DocRelationEdgeRow:
    """One `doc_relations_edges` row: a spec doc or vendor doc (Phase 29,
    decisions/0043) mechanically mentioning a tracked vendor or another doc
    artifact. `relation_kind` says which:
    `'mentions_dependency'` pairs with `target_vendor_name`,
    `'mentions_artifact'` with `target_doc_artifact_path` — exactly one of
    the two is set per row, mirroring `SkillMentionEdgeRow`'s existing
    two-nullable-target shape, not a new pattern. `chunk_start_line`
    (Phase 32) mirrors `DocumentsEdgeRow.chunk_start_line` — the natural-
    key half of an optional reference to the *source* doc's one
    `doc_chunks` row whose own text contains the match that produced this
    edge, `None` when the match can't be attributed to exactly one chunk.
    """

    source_doc_artifact_path: str
    relation_kind: str
    target_vendor_name: str | None = None
    target_doc_artifact_path: str | None = None
    chunk_start_line: int | None = None


# --- Schema / connection setup --------------------------------------------


def init_schema(conn: sqlite3.Connection) -> None:
    """Idempotent `CREATE TABLE IF NOT EXISTS` for every table, plus a
    `meta.schema_version` row seeded on first call. Safe to call on every
    `open_graph`, including against an already-initialized database.
    """
    conn.executescript(_SCHEMA_SQL)
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO meta (key, value) VALUES ('schema_version', ?)",
            (_SCHEMA_VERSION,),
        )


def _migrate_doc_artifacts_constraints(conn: sqlite3.Connection) -> None:
    """Migrates an on-disk schema older than `_SCHEMA_VERSION` by dropping
    and recreating `doc_artifacts` under the current (widened) CHECK
    constraints, plus `documents_edges`/`doc_relations_edges` under their
    current column set. Phase 17 widened `kind` (added `'slash_command'`,
    "1" -> "2"); Phase 21 widens both `kind` (added `'spec_doc'`) and
    `origin` (added `'project'`, "2" -> "3") for the same reason; Phase 27
    widens both again (`kind` gains `'vendor_doc'`, `origin` gains
    `'vendor_upstream'`, "3" -> "4") for a vendor's own embedded upstream
    doc files (`vendor/<name>/src/README.md` and siblings); Phase 32 adds
    a nullable `chunk_id` column to `documents_edges`/`doc_relations_edges`
    ("5" -> "6") — dropping `doc_artifacts` alone only cascades a DELETE of
    those two tables' *rows* (`ON DELETE CASCADE`), it doesn't touch their
    own column set, so they need their own explicit drop for `chunk_id` to
    actually appear on an existing database. One generic, version-agnostic
    function handles any prior version, not one function per phase — it
    only ever compares the stored version against current and, on
    mismatch, drops+recreates once; `init_schema`'s `CREATE TABLE IF NOT
    EXISTS` won't retrofit an already-existing table's columns/constraints
    on its own, which is why this is needed at all. Safe: all three tables
    (plus `skill_mentions_edges`/`routes_via_edges`, cascaded from
    `doc_artifacts`) are fully cleared and rewritten by `rebuild_
    deterministic` on every whole-project sync anyway, so there's no
    data-loss risk in recreating them here — and with `PRAGMA foreign_keys
    = ON` already set on this connection, SQLite itself cascades the
    `doc_artifacts` drop into `skill_mentions_edges`/`routes_via_edges`'s
    rows, so no dangling foreign keys are left behind even between this
    migration and
    the next sync. Never touches `vendor_enrichment`/`symbol_enrichment` —
    those tables have no foreign key to `doc_artifacts` at all, so a
    `doc_artifacts` drop can't reach them (same "never touch enrichment"
    invariant every other phase in this arc preserves).

    A brand-new database (no `meta` table yet — `init_schema` hasn't run
    at all) has nothing to migrate; `init_schema`, called right after this
    function returns, seeds `schema_version` at the current value fresh.
    """
    meta_table_exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'meta'"
    ).fetchone()
    if not meta_table_exists:
        return
    row = conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()
    if row is None or row[0] == _SCHEMA_VERSION:
        return
    with conn:
        conn.execute("DROP TABLE IF EXISTS documents_edges")
        conn.execute("DROP TABLE IF EXISTS doc_relations_edges")
        conn.execute("DROP TABLE IF EXISTS doc_artifacts")
        conn.execute("UPDATE meta SET value = ? WHERE key = 'schema_version'", (_SCHEMA_VERSION,))


def _migrate_doc_relation_enrichment_relation_label(conn: sqlite3.Connection) -> None:
    """Adds `doc_relation_enrichment.relation_label` (Phase 31) to a
    pre-Phase-31 on-disk database via `ALTER TABLE ... ADD COLUMN`, not
    `_migrate_doc_artifacts_constraints`'s drop-and-recreate approach:
    `doc_relation_enrichment` holds paid AI enrichment output that
    survives every `rebuild_deterministic` call (decisions/0038), so
    dropping it would destroy real spend, unlike `doc_artifacts`, which
    is fully rewritten every sync anyway and has no such cost to lose.
    SQLite has supported `ADD COLUMN ... CHECK (...)` since 3.25 (2018); a
    `CHECK` referencing only the new column is satisfied by every
    pre-existing row automatically, since a bare `ADD COLUMN` with no
    `DEFAULT` back-fills `NULL`, and `NULL IN (...)` evaluates to `NULL`
    (not `FALSE`), which SQLite's `CHECK` treats as passing — existing
    rows simply start with `relation_label = NULL`, exactly the "not
    migrated, filled on next natural re-enrichment cycle" design (see
    planning/phase-31-typed-relation-enrichment.md's Design decisions).

    Checked directly via `PRAGMA table_info`, not `meta.schema_version` —
    self-contained and idempotent regardless of whether some other
    migration already advanced the stored version this call, since this
    function's own precondition is "does the column exist," not "what
    version does `meta` say." A brand-new database has no `doc_relation_
    enrichment` table yet at all — `init_schema`'s `CREATE TABLE IF NOT
    EXISTS`, called right after this function returns, creates it with
    the column already present, so there's nothing to migrate.
    """
    table_exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'doc_relation_enrichment'"
    ).fetchone()
    if not table_exists:
        return
    columns = {row[1] for row in conn.execute("PRAGMA table_info(doc_relation_enrichment)")}
    if "relation_label" in columns:
        return
    with conn:
        conn.execute(
            f"ALTER TABLE doc_relation_enrichment ADD COLUMN relation_label TEXT "
            f"CHECK ({_RELATION_LABEL_CHECK_SQL})"
        )


def open_graph(project_root: Path) -> sqlite3.Connection:
    """Resolve `context-graph.db` at `project_root`, connect (creating the
    file if absent), enable foreign keys (SQLite defaults this off, so it
    must be set per-connection), migrate an older on-disk schema version if
    needed, initialize the schema, and return the connection. The one
    function later phases call to get a working handle.
    """
    db_path = project_root / _DB_FILENAME
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    _migrate_doc_artifacts_constraints(conn)
    _migrate_doc_relation_enrichment_relation_label(conn)
    init_schema(conn)
    return conn


# --- rebuild_deterministic -------------------------------------------------


def rebuild_deterministic(
    conn: sqlite3.Connection,
    *,
    vendors: Sequence[VendorRow],
    source_files: Sequence[SourceFileRow],
    symbols: Sequence[SymbolRow],
    uses_edges: Sequence[UsesEdgeRow],
    doc_artifacts: Sequence[DocArtifactRow],
    doc_chunks: Sequence[DocChunkRow] = (),
    documents_edges: Sequence[DocumentsEdgeRow],
    skill_mentions_edges: Sequence[SkillMentionEdgeRow],
    routes_via_edges: Sequence[RoutesViaEdgeRow],
    depends_on_edges: Sequence[DependsOnEdgeRow],
    doc_relations_edges: Sequence[DocRelationEdgeRow],
) -> None:
    """Wipe and rewrite every deterministic table inside one transaction,
    then update `meta.last_deterministic_rebuild_at`. Never touches
    `vendor_enrichment`/`symbol_enrichment` — the mechanical reason
    Phase 14's enrichment output survives a later whole-project refresh
    (`decisions/0025`'s rebuild-trigger posture, carried forward by
    `decisions/0032`).

    `vendor_enrichment`/`symbol_enrichment` cascade from `vendors`/
    `symbols` on delete, so surviving a rebuild requires never deleting a
    vendor/symbol that's still present in the new fixture: vendors and
    symbols are upserted by their natural key (name, and vendor+name
    respectively), which preserves their integer id and leaves any
    enrichment row referencing that id completely untouched. Only vendors
    / symbols that no longer appear in the new fixture at all are deleted
    (correctly cascading away enrichment for something that no longer
    exists). Every other table has no cross-rebuild identity to preserve
    and is fully cleared and reinserted, `doc_chunks` (Phase 32) included —
    `doc_chunks` defaults to `()` so pre-Phase-32 callers/tests that don't
    pass it keep working unchanged.
    """
    with conn:
        # Edge / leaf tables carry no cross-rebuild identity — clear and
        # reinsert unconditionally.
        conn.execute("DELETE FROM doc_relations_edges")
        conn.execute("DELETE FROM depends_on_edges")
        conn.execute("DELETE FROM routes_via_edges")
        conn.execute("DELETE FROM skill_mentions_edges")
        conn.execute("DELETE FROM documents_edges")
        conn.execute("DELETE FROM uses_edges")
        conn.execute("DELETE FROM doc_chunks")
        conn.execute("DELETE FROM doc_artifacts")
        conn.execute("DELETE FROM source_files")

        _sync_vendors(conn, vendors)
        vendor_ids = _fetch_name_to_id(conn, "vendors")

        _sync_symbols(conn, symbols, vendor_ids)
        symbol_ids = _fetch_symbol_ids(conn)

        source_file_ids = _insert_source_files(conn, source_files)
        doc_artifact_ids = _insert_doc_artifacts(conn, doc_artifacts, vendor_ids)
        doc_chunk_ids = _insert_doc_chunks(conn, doc_chunks, doc_artifact_ids)

        _insert_uses_edges(conn, uses_edges, vendor_ids, symbol_ids, source_file_ids)
        _insert_documents_edges(
            conn, documents_edges, symbol_ids, doc_artifact_ids, doc_chunk_ids
        )
        _insert_skill_mentions_edges(
            conn, skill_mentions_edges, vendor_ids, source_file_ids, doc_artifact_ids
        )
        _insert_routes_via_edges(conn, routes_via_edges, vendor_ids, doc_artifact_ids)
        _insert_depends_on_edges(conn, depends_on_edges, vendor_ids)
        _insert_doc_relations_edges(
            conn, doc_relations_edges, vendor_ids, doc_artifact_ids, doc_chunk_ids
        )

        conn.execute(
            "INSERT INTO meta (key, value) VALUES ('last_deterministic_rebuild_at', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (datetime.now(UTC).isoformat(),),
        )


def _sync_vendors(conn: sqlite3.Connection, vendors: Sequence[VendorRow]) -> None:
    existing = {name for (name,) in conn.execute("SELECT name FROM vendors")}
    incoming = {v.name for v in vendors}
    for stale_name in existing - incoming:
        conn.execute("DELETE FROM vendors WHERE name = ?", (stale_name,))

    for v in vendors:
        conn.execute(
            """
            INSERT INTO vendors (
                name, ecosystem, installed_version, repository_url,
                repository_subdirectory, source_resolved,
                source_resolution_error, last_synced_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                ecosystem = excluded.ecosystem,
                installed_version = excluded.installed_version,
                repository_url = excluded.repository_url,
                repository_subdirectory = excluded.repository_subdirectory,
                source_resolved = excluded.source_resolved,
                source_resolution_error = excluded.source_resolution_error,
                last_synced_at = excluded.last_synced_at
            """,
            (
                v.name,
                v.ecosystem,
                v.installed_version,
                v.repository_url,
                v.repository_subdirectory,
                int(v.source_resolved),
                v.source_resolution_error,
                v.last_synced_at,
            ),
        )


def _sync_symbols(
    conn: sqlite3.Connection, symbols: Sequence[SymbolRow], vendor_ids: dict[str, int]
) -> None:
    existing = {
        (vendor_name, symbol_name)
        for (vendor_name, symbol_name) in conn.execute(
            "SELECT vendors.name, symbols.name FROM symbols "
            "JOIN vendors ON symbols.vendor_id = vendors.id"
        )
    }
    incoming = {(s.vendor_name, s.name) for s in symbols}
    for vendor_name, symbol_name in existing - incoming:
        conn.execute(
            "DELETE FROM symbols WHERE vendor_id = ? AND name = ?",
            (vendor_ids[vendor_name], symbol_name),
        )

    for s in symbols:
        conn.execute(
            """
            INSERT INTO symbols (vendor_id, name, purpose)
            VALUES (?, ?, ?)
            ON CONFLICT(vendor_id, name) DO UPDATE SET purpose = excluded.purpose
            """,
            (vendor_ids[s.vendor_name], s.name, s.purpose),
        )


def _fetch_name_to_id(conn: sqlite3.Connection, table: str) -> dict[str, int]:
    # `table` is always one of this module's own fixed table-name literals
    # (never external input), so this isn't a SQL-injection surface.
    return dict(conn.execute(f"SELECT name, id FROM {table}"))


def _fetch_symbol_ids(conn: sqlite3.Connection) -> dict[tuple[str, str], int]:
    return {
        (vendor_name, symbol_name): symbol_id
        for symbol_id, vendor_name, symbol_name in conn.execute(
            "SELECT symbols.id, vendors.name, symbols.name FROM symbols "
            "JOIN vendors ON symbols.vendor_id = vendors.id"
        )
    }


def _insert_source_files(
    conn: sqlite3.Connection, source_files: Sequence[SourceFileRow]
) -> dict[str, int]:
    ids: dict[str, int] = {}
    for sf in source_files:
        cur = conn.execute("INSERT INTO source_files (path) VALUES (?)", (sf.path,))
        ids[sf.path] = cur.lastrowid
    return ids


def _insert_doc_artifacts(
    conn: sqlite3.Connection,
    doc_artifacts: Sequence[DocArtifactRow],
    vendor_ids: dict[str, int],
) -> dict[str, int]:
    ids: dict[str, int] = {}
    for d in doc_artifacts:
        vendor_id = vendor_ids[d.vendor_name] if d.vendor_name is not None else None
        cur = conn.execute(
            """
            INSERT INTO doc_artifacts (vendor_id, kind, origin, path, name, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (vendor_id, d.kind, d.origin, d.path, d.name, d.description),
        )
        ids[d.path] = cur.lastrowid
    return ids


def _insert_doc_chunks(
    conn: sqlite3.Connection,
    doc_chunks: Sequence[DocChunkRow],
    doc_artifact_ids: dict[str, int],
) -> dict[tuple[str, int], int]:
    """Inserts every `DocChunkRow`, keyed by `(doc_artifact_path,
    start_line)` for `_insert_documents_edges`/`_insert_doc_relations_
    edges` to resolve a `DocumentsEdgeRow`/`DocRelationEdgeRow`'s optional
    `chunk_start_line` back to an integer `chunk_id`.
    """
    ids: dict[tuple[str, int], int] = {}
    for c in doc_chunks:
        cur = conn.execute(
            """
            INSERT INTO doc_chunks
                (doc_artifact_id, heading_path, start_line, end_line, content_hash)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                doc_artifact_ids[c.doc_artifact_path],
                c.heading_path,
                c.start_line,
                c.end_line,
                c.content_hash,
            ),
        )
        ids[(c.doc_artifact_path, c.start_line)] = cur.lastrowid
    return ids


def _insert_uses_edges(
    conn: sqlite3.Connection,
    uses_edges: Sequence[UsesEdgeRow],
    vendor_ids: dict[str, int],
    symbol_ids: dict[tuple[str, str], int],
    source_file_ids: dict[str, int],
) -> None:
    for e in uses_edges:
        symbol_id = symbol_ids[(e.vendor_name, e.symbol_name)] if e.symbol_name else None
        conn.execute(
            """
            INSERT INTO uses_edges (source_file_id, vendor_id, symbol_id, line)
            VALUES (?, ?, ?, ?)
            """,
            (source_file_ids[e.source_file_path], vendor_ids[e.vendor_name], symbol_id, e.line),
        )


def _insert_documents_edges(
    conn: sqlite3.Connection,
    documents_edges: Sequence[DocumentsEdgeRow],
    symbol_ids: dict[tuple[str, str], int],
    doc_artifact_ids: dict[str, int],
    doc_chunk_ids: dict[tuple[str, int], int],
) -> None:
    for e in documents_edges:
        chunk_id = (
            doc_chunk_ids.get((e.doc_artifact_path, e.chunk_start_line))
            if e.chunk_start_line is not None
            else None
        )
        conn.execute(
            "INSERT INTO documents_edges (doc_artifact_id, symbol_id, chunk_id) VALUES (?, ?, ?)",
            (
                doc_artifact_ids[e.doc_artifact_path],
                symbol_ids[(e.vendor_name, e.symbol_name)],
                chunk_id,
            ),
        )


def _insert_skill_mentions_edges(
    conn: sqlite3.Connection,
    skill_mentions_edges: Sequence[SkillMentionEdgeRow],
    vendor_ids: dict[str, int],
    source_file_ids: dict[str, int],
    doc_artifact_ids: dict[str, int],
) -> None:
    for e in skill_mentions_edges:
        vendor_id = vendor_ids[e.vendor_name] if e.vendor_name is not None else None
        source_file_id = (
            source_file_ids[e.source_file_path] if e.source_file_path is not None else None
        )
        conn.execute(
            """
            INSERT INTO skill_mentions_edges (doc_artifact_id, vendor_id, source_file_id)
            VALUES (?, ?, ?)
            """,
            (doc_artifact_ids[e.doc_artifact_path], vendor_id, source_file_id),
        )


def _insert_routes_via_edges(
    conn: sqlite3.Connection,
    routes_via_edges: Sequence[RoutesViaEdgeRow],
    vendor_ids: dict[str, int],
    doc_artifact_ids: dict[str, int],
) -> None:
    for e in routes_via_edges:
        conn.execute(
            "INSERT INTO routes_via_edges (vendor_id, doc_artifact_id) VALUES (?, ?)",
            (vendor_ids[e.vendor_name], doc_artifact_ids[e.doc_artifact_path]),
        )


def _insert_depends_on_edges(
    conn: sqlite3.Connection,
    depends_on_edges: Sequence[DependsOnEdgeRow],
    vendor_ids: dict[str, int],
) -> None:
    for e in depends_on_edges:
        conn.execute(
            "INSERT INTO depends_on_edges (vendor_id, depends_on_vendor_id) VALUES (?, ?)",
            (vendor_ids[e.vendor_name], vendor_ids[e.depends_on_vendor_name]),
        )


def _insert_doc_relations_edges(
    conn: sqlite3.Connection,
    doc_relations_edges: Sequence[DocRelationEdgeRow],
    vendor_ids: dict[str, int],
    doc_artifact_ids: dict[str, int],
    doc_chunk_ids: dict[tuple[str, int], int],
) -> None:
    for e in doc_relations_edges:
        target_vendor_id = (
            vendor_ids[e.target_vendor_name] if e.target_vendor_name is not None else None
        )
        target_doc_artifact_id = (
            doc_artifact_ids[e.target_doc_artifact_path]
            if e.target_doc_artifact_path is not None
            else None
        )
        chunk_id = (
            doc_chunk_ids.get((e.source_doc_artifact_path, e.chunk_start_line))
            if e.chunk_start_line is not None
            else None
        )
        conn.execute(
            """
            INSERT INTO doc_relations_edges (
                source_doc_artifact_id, target_vendor_id, target_doc_artifact_id, relation_kind,
                chunk_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                doc_artifact_ids[e.source_doc_artifact_path],
                target_vendor_id,
                target_doc_artifact_id,
                e.relation_kind,
                chunk_id,
            ),
        )


# --- Query functions --------------------------------------------------------


def unused_vendors(conn: sqlite3.Connection) -> list[str]:
    """Vendor names with zero `uses_edges` rows anywhere in the project."""
    rows = conn.execute(
        """
        SELECT v.name FROM vendors v
        WHERE NOT EXISTS (SELECT 1 FROM uses_edges u WHERE u.vendor_id = v.id)
        ORDER BY v.name
        """
    ).fetchall()
    return [name for (name,) in rows]


def documented_but_unused(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    """`(vendor, symbol)` pairs that some doc artifact documents but that
    have no `uses_edges` row anywhere.
    """
    return conn.execute(
        """
        SELECT v.name, s.name
        FROM symbols s
        JOIN vendors v ON s.vendor_id = v.id
        WHERE EXISTS (SELECT 1 FROM documents_edges de WHERE de.symbol_id = s.id)
          AND NOT EXISTS (SELECT 1 FROM uses_edges ue WHERE ue.symbol_id = s.id)
        ORDER BY v.name, s.name
        """
    ).fetchall()


def used_but_undocumented(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    """`(vendor, symbol)` pairs with at least one `uses_edges` row but no
    documenting artifact.
    """
    return conn.execute(
        """
        SELECT v.name, s.name
        FROM symbols s
        JOIN vendors v ON s.vendor_id = v.id
        WHERE EXISTS (SELECT 1 FROM uses_edges ue WHERE ue.symbol_id = s.id)
          AND NOT EXISTS (SELECT 1 FROM documents_edges de WHERE de.symbol_id = s.id)
        ORDER BY v.name, s.name
        """
    ).fetchall()


def spec_docs_without_relations(conn: sqlite3.Connection) -> list[str]:
    """Spec-doc paths (`kind='spec_doc'`) with zero `doc_relations_edges`
    rows as their source — could mean genuinely unrelated content, could
    mean a naming mismatch worth a human look. `check`'s report-only
    coverage-gap section, never `--strict`-blocking, same posture as every
    other graph-derived coverage gap.
    """
    rows = conn.execute(
        """
        SELECT da.path FROM doc_artifacts da
        WHERE da.kind = 'spec_doc'
          AND NOT EXISTS (
              SELECT 1 FROM doc_relations_edges dre WHERE dre.source_doc_artifact_id = da.id
          )
        ORDER BY da.path
        """
    ).fetchall()
    return [path for (path,) in rows]


def vendor_docs_without_relations(conn: sqlite3.Connection) -> list[str]:
    """Vendor-doc paths (`kind='vendor_doc'`, Phase 27) with zero
    `doc_relations_edges` rows *targeting* them — the mirror image of
    `spec_docs_without_relations` above, not a parameterized copy of it:
    this checks `target_doc_artifact_id` specifically, deliberately
    ignoring whether the same vendor doc might independently appear as a
    `source_doc_artifact_id` too (Phase 29, decisions/0043, widened
    `build_doc_relations_edges` to also scan vendor docs outward). The two
    roles are orthogonal — "does anything mention this vendor doc" is a
    different, still-useful coverage question from "does this vendor doc
    itself mention anything," and this function only answers the former.
    `check`'s report-only coverage-gap section, never `--strict`-blocking,
    same posture as every other graph-derived coverage gap.
    """
    rows = conn.execute(
        """
        SELECT da.path FROM doc_artifacts da
        WHERE da.kind = 'vendor_doc'
          AND NOT EXISTS (
              SELECT 1 FROM doc_relations_edges dre WHERE dre.target_doc_artifact_id = da.id
          )
        ORDER BY da.path
        """
    ).fetchall()
    return [path for (path,) in rows]


def doc_relations(conn: sqlite3.Connection, doc_artifact_path: str) -> list[dict]:
    """Every `doc_relations_edges` row whose source is `doc_artifact_path`,
    resolved to the target's name/path. Empty for an unknown path or a
    spec doc with zero detected mentions — never an error, mirroring every
    other by-name query function's graceful-empty posture. `heading`
    (Phase 32) is the source doc's own heading enclosing the mechanical
    match, when the edge has a `chunk_id`; `None` otherwise (a headerless
    doc, or a match not attributable to exactly one chunk).
    """
    row = conn.execute(
        "SELECT id FROM doc_artifacts WHERE path = ?", (doc_artifact_path,)
    ).fetchone()
    if row is None:
        return []
    source_id = row[0]
    results = []
    for relation_kind, target_vendor, target_path, target_name, heading in conn.execute(
        """
        SELECT dre.relation_kind, v.name, da.path, da.name, dch.heading_path
        FROM doc_relations_edges dre
        LEFT JOIN vendors v ON dre.target_vendor_id = v.id
        LEFT JOIN doc_artifacts da ON dre.target_doc_artifact_id = da.id
        LEFT JOIN doc_chunks dch ON dre.chunk_id = dch.id
        WHERE dre.source_doc_artifact_id = ?
        ORDER BY v.name, da.path
        """,
        (source_id,),
    ):
        results.append(
            {
                "relation_kind": relation_kind,
                "target_vendor": target_vendor,
                "target_doc_artifact_path": target_path,
                "target_doc_artifact_name": target_name,
                "heading": heading,
            }
        )
    return results


def vendor_profile(conn: sqlite3.Connection, name: str) -> dict | None:
    """The vendor row plus its symbols, total usage count, documenting
    artifacts (directly linked or via one of its symbols), routed Skills,
    and its `depends_on` vendor names. `None` if `name` isn't a known
    vendor.
    """
    row = conn.execute(
        """
        SELECT id, name, ecosystem, installed_version, repository_url,
               repository_subdirectory, source_resolved,
               source_resolution_error, last_synced_at
        FROM vendors WHERE name = ?
        """,
        (name,),
    ).fetchone()
    if row is None:
        return None
    vendor_id = row[0]

    vendor = {
        "id": vendor_id,
        "name": row[1],
        "ecosystem": row[2],
        "installed_version": row[3],
        "repository_url": row[4],
        "repository_subdirectory": row[5],
        "source_resolved": bool(row[6]),
        "source_resolution_error": row[7],
        "last_synced_at": row[8],
    }

    symbols = [
        {"id": sid, "name": sname, "purpose": purpose}
        for sid, sname, purpose in conn.execute(
            "SELECT id, name, purpose FROM symbols WHERE vendor_id = ? ORDER BY name",
            (vendor_id,),
        )
    ]

    (usage_count,) = conn.execute(
        "SELECT COUNT(*) FROM uses_edges WHERE vendor_id = ?", (vendor_id,)
    ).fetchone()

    used_at = [
        {"source_file_path": path, "line": line}
        for path, line in conn.execute(
            """
            SELECT sf.path, ue.line
            FROM uses_edges ue
            JOIN source_files sf ON ue.source_file_id = sf.id
            WHERE ue.vendor_id = ?
            ORDER BY sf.path, ue.line
            """,
            (vendor_id,),
        )
    ]

    documenting_artifacts = [
        {"id": did, "path": path, "kind": kind, "name": dname, "description": description}
        for did, path, kind, dname, description in conn.execute(
            """
            SELECT DISTINCT da.id, da.path, da.kind, da.name, da.description
            FROM doc_artifacts da
            WHERE da.vendor_id = ?
               OR da.id IN (
                    SELECT de.doc_artifact_id FROM documents_edges de
                    JOIN symbols s ON de.symbol_id = s.id
                    WHERE s.vendor_id = ?
               )
            ORDER BY da.path
            """,
            (vendor_id, vendor_id),
        )
    ]

    routed_skills = [
        {"id": did, "path": path, "name": sname}
        for did, path, sname in conn.execute(
            """
            SELECT da.id, da.path, da.name
            FROM routes_via_edges rve
            JOIN doc_artifacts da ON rve.doc_artifact_id = da.id
            WHERE rve.vendor_id = ?
            ORDER BY da.path
            """,
            (vendor_id,),
        )
    ]

    depends_on = [
        depended_name
        for (depended_name,) in conn.execute(
            """
            SELECT v2.name
            FROM depends_on_edges doe
            JOIN vendors v2 ON doe.depends_on_vendor_id = v2.id
            WHERE doe.vendor_id = ?
            ORDER BY v2.name
            """,
            (vendor_id,),
        )
    ]

    return {
        "vendor": vendor,
        "symbols": symbols,
        "usage_count": usage_count,
        "used_at": used_at,
        "documenting_artifacts": documenting_artifacts,
        "routed_skills": routed_skills,
        "depends_on": depends_on,
    }


def symbol_profile(conn: sqlite3.Connection, name: str) -> list[dict]:
    """Every symbol row named `name`, across every vendor (symbol names
    aren't globally unique) — each with its vendor, usage count, and
    documenting artifacts.
    """
    profiles = []
    for symbol_id, vendor_name, purpose in conn.execute(
        """
        SELECT s.id, v.name, s.purpose
        FROM symbols s
        JOIN vendors v ON s.vendor_id = v.id
        WHERE s.name = ?
        ORDER BY v.name
        """,
        (name,),
    ):
        (usage_count,) = conn.execute(
            "SELECT COUNT(*) FROM uses_edges WHERE symbol_id = ?", (symbol_id,)
        ).fetchone()
        used_at = [
            {"source_file_path": path, "line": line}
            for path, line in conn.execute(
                """
                SELECT sf.path, ue.line
                FROM uses_edges ue
                JOIN source_files sf ON ue.source_file_id = sf.id
                WHERE ue.symbol_id = ?
                ORDER BY sf.path, ue.line
                """,
                (symbol_id,),
            )
        ]
        documenting_artifacts = [
            {"id": did, "path": path, "kind": kind}
            for did, path, kind in conn.execute(
                """
                SELECT da.id, da.path, da.kind
                FROM documents_edges de
                JOIN doc_artifacts da ON de.doc_artifact_id = da.id
                WHERE de.symbol_id = ?
                ORDER BY da.path
                """,
                (symbol_id,),
            )
        ]
        profiles.append(
            {
                "id": symbol_id,
                "vendor": vendor_name,
                "name": name,
                "purpose": purpose,
                "usage_count": usage_count,
                "used_at": used_at,
                "documenting_artifacts": documenting_artifacts,
            }
        )
    return profiles


def doc_code_trace(conn: sqlite3.Connection, doc_path_or_vendor_name: str) -> list[dict]:
    """Composes existing edges into a doc/vendor → package-code usage
    trace (Phase 30) — a query-time join over data already in the graph,
    no new table, same posture as `documented_but_unused`. Each returned
    dict has `vendor`, `symbol` (`None` for a vendor-level usage site),
    `source_file_path`, `line`, and `via` (which composition produced it):

    - A known `doc_artifacts.path` resolves two ways, unioned:
      - `'documents'`: `documents_edges` → `symbols` → `uses_edges` — every
        symbol this doc artifact documents, and where the project's own
        code actually calls it.
      - `'mentions_dependency'`: this doc artifact's own outgoing
        `doc_relations_edges` rows of kind `'mentions_dependency'` →
        `uses_edges` — every vendor this doc mechanically mentions
        (a spec doc or vendor doc, per `decisions/0043`), and every
        real usage site for that vendor anywhere in the project.
    - A known vendor `name` resolves directly: `'direct_usage'` — that
      vendor's own `uses_edges`, the same rows `vendor_profile`'s
      `used_at` already exposes, available here too so a caller that only
      has a name (not knowing whether it's a doc path or a vendor) can
      use one function for either.
    - A name matching neither is an empty list, not an error — mirrors
      `doc_relations`'s existing graceful-empty posture for an unknown
      path.

    Each `'documents'`/`'mentions_dependency'` dict also carries `heading`
    (Phase 32) — the heading in the *doc* (not the code file) enclosing
    the edge that produced this row, when that edge has a `chunk_id`;
    `None` otherwise. `'direct_usage'` rows have no doc side at all, so
    `heading` is always `None` there.
    """
    doc_row = conn.execute(
        "SELECT id FROM doc_artifacts WHERE path = ?", (doc_path_or_vendor_name,)
    ).fetchone()
    if doc_row is not None:
        doc_id = doc_row[0]
        results = [
            {
                "via": "documents",
                "vendor": vendor_name,
                "symbol": symbol_name,
                "source_file_path": path,
                "line": line,
                "heading": heading,
            }
            for vendor_name, symbol_name, path, line, heading in conn.execute(
                """
                SELECT v.name, s.name, sf.path, ue.line, dch.heading_path
                FROM documents_edges de
                JOIN symbols s ON de.symbol_id = s.id
                JOIN vendors v ON s.vendor_id = v.id
                JOIN uses_edges ue ON ue.symbol_id = s.id
                JOIN source_files sf ON ue.source_file_id = sf.id
                LEFT JOIN doc_chunks dch ON de.chunk_id = dch.id
                WHERE de.doc_artifact_id = ?
                ORDER BY v.name, s.name, sf.path, ue.line
                """,
                (doc_id,),
            )
        ]
        results.extend(
            {
                "via": "mentions_dependency",
                "vendor": vendor_name,
                "symbol": None,
                "source_file_path": path,
                "line": line,
                "heading": heading,
            }
            for vendor_name, path, line, heading in conn.execute(
                """
                SELECT v.name, sf.path, ue.line, dch.heading_path
                FROM doc_relations_edges dre
                JOIN vendors v ON dre.target_vendor_id = v.id
                JOIN uses_edges ue ON ue.vendor_id = v.id
                JOIN source_files sf ON ue.source_file_id = sf.id
                LEFT JOIN doc_chunks dch ON dre.chunk_id = dch.id
                WHERE dre.source_doc_artifact_id = ?
                  AND dre.relation_kind = 'mentions_dependency'
                ORDER BY v.name, sf.path, ue.line
                """,
                (doc_id,),
            )
        )
        return results

    vendor_row = conn.execute(
        "SELECT id, name FROM vendors WHERE name = ?", (doc_path_or_vendor_name,)
    ).fetchone()
    if vendor_row is not None:
        vendor_id, vendor_name = vendor_row
        return [
            {
                "via": "direct_usage",
                "vendor": vendor_name,
                "symbol": None,
                "source_file_path": path,
                "line": line,
                "heading": None,
            }
            for path, line in conn.execute(
                """
                SELECT sf.path, ue.line
                FROM uses_edges ue
                JOIN source_files sf ON ue.source_file_id = sf.id
                WHERE ue.vendor_id = ?
                ORDER BY sf.path, ue.line
                """,
                (vendor_id,),
            )
        ]

    return []


def skills_index(conn: sqlite3.Connection) -> list[dict]:
    """Every `doc_artifacts` row with `kind='skill'`, its `origin`, and
    what it mechanically mentions (`skill_mentions_edges`).
    """
    index = []
    for doc_artifact_id, path, dname, origin in conn.execute(
        "SELECT id, path, name, origin FROM doc_artifacts WHERE kind = 'skill' ORDER BY path"
    ):
        mentions_vendors = [
            vname
            for (vname,) in conn.execute(
                """
                SELECT v.name FROM skill_mentions_edges sme
                JOIN vendors v ON sme.vendor_id = v.id
                WHERE sme.doc_artifact_id = ?
                ORDER BY v.name
                """,
                (doc_artifact_id,),
            )
        ]
        mentions_source_files = [
            path_
            for (path_,) in conn.execute(
                """
                SELECT sf.path FROM skill_mentions_edges sme
                JOIN source_files sf ON sme.source_file_id = sf.id
                WHERE sme.doc_artifact_id = ?
                ORDER BY sf.path
                """,
                (doc_artifact_id,),
            )
        ]
        index.append(
            {
                "id": doc_artifact_id,
                "path": path,
                "name": dname,
                "origin": origin,
                "mentions_vendors": mentions_vendors,
                "mentions_source_files": mentions_source_files,
            }
        )
    return index


def enrichment_candidates(conn: sqlite3.Connection) -> list[dict]:
    """Every vendor with at least one `uses_edges` row, its currently-used
    symbol names, and its existing `vendor_enrichment.symbol_set_hash` if
    any. `graph.py` doesn't decide staleness — Phase 14's `enrichment.py`
    diffs the returned hash against a freshly-computed one itself.
    """
    candidates = []
    for vendor_id, name, symbol_set_hash in conn.execute(
        """
        SELECT v.id, v.name, ve.symbol_set_hash
        FROM vendors v
        LEFT JOIN vendor_enrichment ve ON ve.vendor_id = v.id
        WHERE EXISTS (SELECT 1 FROM uses_edges ue WHERE ue.vendor_id = v.id)
        ORDER BY v.name
        """
    ):
        used_symbols = [
            sname
            for (sname,) in conn.execute(
                """
                SELECT DISTINCT s.name
                FROM uses_edges ue
                JOIN symbols s ON ue.symbol_id = s.id
                WHERE ue.vendor_id = ?
                ORDER BY s.name
                """,
                (vendor_id,),
            )
        ]
        candidates.append(
            {
                "id": vendor_id,
                "vendor": name,
                "used_symbols": used_symbols,
                "symbol_set_hash": symbol_set_hash,
            }
        )
    return candidates


def has_enrichment(conn: sqlite3.Connection, vendor_name: str) -> bool:
    """Whether `vendor_name` has a `vendor_enrichment` row — i.e. has been
    AI-enriched at least once (Phase B, `decisions/0031`/`decisions/0033`).
    `False` for an unknown vendor name too, never an error — callers
    (`index.py`'s routing table, `skill.py`'s tool Skill) treat "not yet
    enriched" and "not a known vendor" the same way for display purposes.
    """
    row = conn.execute(
        """
        SELECT 1 FROM vendor_enrichment ve
        JOIN vendors v ON ve.vendor_id = v.id
        WHERE v.name = ?
        """,
        (vendor_name,),
    ).fetchone()
    return row is not None


# --- Enrichment writers ------------------------------------------------------


def record_enrichment(conn: sqlite3.Connection, vendor_id: int, **fields: object) -> None:
    """Insert or update the one `vendor_enrichment` row for `vendor_id`.
    The only writer to `vendor_enrichment`, kept separate from
    `rebuild_deterministic` on purpose so a deterministic rebuild never
    touches it. `fields` keys: `technical_description`,
    `conversational_overview`, `action_pointer_file`,
    `action_pointer_note`, `symbol_set_hash`, `model`, `generated_at`.
    """
    columns = (
        "technical_description",
        "conversational_overview",
        "action_pointer_file",
        "action_pointer_note",
        "symbol_set_hash",
        "model",
        "generated_at",
    )
    values = [fields.get(c) for c in columns]
    with conn:
        conn.execute(
            f"""
            INSERT INTO vendor_enrichment (vendor_id, {", ".join(columns)})
            VALUES (?, {", ".join("?" for _ in columns)})
            ON CONFLICT(vendor_id) DO UPDATE SET
                {", ".join(f"{c} = excluded.{c}" for c in columns)}
            """,
            (vendor_id, *values),
        )


def record_symbol_enrichment(
    conn: sqlite3.Connection, symbol_id: int, purpose: str, generated_at: str
) -> None:
    """Insert or update the one `symbol_enrichment` row for `symbol_id`.
    The only writer to `symbol_enrichment`, kept separate from
    `rebuild_deterministic` for the same reason as `record_enrichment`.
    """
    with conn:
        conn.execute(
            """
            INSERT INTO symbol_enrichment (symbol_id, purpose, generated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(symbol_id) DO UPDATE SET
                purpose = excluded.purpose,
                generated_at = excluded.generated_at
            """,
            (symbol_id, purpose, generated_at),
        )


def relation_enrichment_candidates(conn: sqlite3.Connection) -> list[dict]:
    """Every `doc_relations_edges` row (Phase 21), joined to its source/
    target *text* identity — `source_doc_path`, `target_vendor_name`,
    `target_doc_path` (exactly one of the latter two set per row, mirroring
    `doc_relations_edges` itself) — plus the `content_hash` already on file
    for that exact natural-key triple in `doc_relation_enrichment`, if any.
    `graph.py` doesn't decide staleness here, the same division of
    responsibility `enrichment_candidates` already has for vendors:
    `relation_enrichment.select_candidates` freshly computes each
    candidate's current content hash and diffs it against what this
    function returns.

    Also returns `target_doc_artifact_name` — the target doc artifact's own
    `name` field (e.g. `"anthropic README.md"`), NULL whenever `target_
    doc_path` is NULL. Phase 28: `doc_mapping.build_doc_relations_edges`'s
    mechanical `mentions_artifact` match was against this `name` field, not
    the target's `path` — `select_candidates` needs it back to re-run the
    exact same word-boundary search and center the excerpt on the actual
    mention instead of always the file's opening.

    The join matches with SQLite's NULL-safe `IS`, not `=` — `target_
    vendor_name`/`target_doc_path` are NULL for whichever `relation_kind`
    doesn't apply, and plain `=` never matches two NULLs, which would
    silently fail to find an already-cached row for any relationship whose
    natural key includes a NULL column (i.e. every one of them).

    Also returns `chunk_start_line`/`chunk_end_line` (Phase 32) — the
    source doc's own matched chunk's line range, from `doc_chunks` via
    `dre.chunk_id`, both `NULL` when the edge has no `chunk_id`.
    `select_candidates` uses these to slice the chunk's own text directly
    as the excerpt, in place of Phase 28's needle-re-derivation, when
    present.
    """
    rows = conn.execute(
        """
        SELECT sda.path, tv.name, tda.path, tda.name, dre.relation_kind, dre_enrich.content_hash,
               dch.start_line, dch.end_line
        FROM doc_relations_edges dre
        JOIN doc_artifacts sda ON dre.source_doc_artifact_id = sda.id
        LEFT JOIN vendors tv ON dre.target_vendor_id = tv.id
        LEFT JOIN doc_artifacts tda ON dre.target_doc_artifact_id = tda.id
        LEFT JOIN doc_relation_enrichment dre_enrich
            ON dre_enrich.source_doc_path = sda.path
           AND dre_enrich.target_vendor_name IS tv.name
           AND dre_enrich.target_doc_path IS tda.path
        LEFT JOIN doc_chunks dch ON dre.chunk_id = dch.id
        ORDER BY sda.path, tv.name, tda.path
        """
    ).fetchall()
    return [
        {
            "source_doc_path": row[0],
            "target_vendor_name": row[1],
            "target_doc_path": row[2],
            "target_doc_artifact_name": row[3],
            "relation_kind": row[4],
            "content_hash": row[5],
            "chunk_start_line": row[6],
            "chunk_end_line": row[7],
        }
        for row in rows
    ]


def record_relation_enrichment(
    conn: sqlite3.Connection,
    source_doc_path: str,
    target_vendor_name: str | None,
    target_doc_path: str | None,
    ai_summary: str,
    content_hash: str,
    model: str,
    generated_at: str,
    relation_label: str | None = None,
) -> None:
    """Insert or update the one `doc_relation_enrichment` row for this
    natural-key triple. The only writer, kept separate from `rebuild_
    deterministic` for the same reason `record_enrichment`/`record_symbol_
    enrichment` are (Phase 10): a deterministic rebuild and a paid
    enrichment write are different trigger points with different costs.

    `relation_label` (Phase 31) is one of `RELATION_LABELS`, enforced by
    the column's own `CHECK` constraint — callers are expected to have
    already substituted `'other'` for anything the model returned outside
    the closed set (`relation_enrichment._normalize_relation_label`), not
    to rely on this function to validate. Defaults to `None` so existing
    callers/tests that don't pass it keep working unchanged.

    Deletes any existing row for this exact triple, then inserts fresh,
    rather than `INSERT ... ON CONFLICT(...) DO UPDATE` the way `record_
    enrichment` upserts by `vendor_id`. SQL's `UNIQUE` constraint treats
    every `NULL` as distinct from every other `NULL` (including another
    `NULL` in the very same column) — since exactly one of `target_vendor_
    name`/`target_doc_path` is `NULL` per row here, an `ON CONFLICT` target
    naming both columns would never actually detect a conflict against an
    existing row whose non-matching column is `NULL`, silently inserting a
    duplicate row on every re-enrichment instead of updating the existing
    one in place. Deleting first with a NULL-safe `IS` comparison (matching
    `relation_enrichment_candidates`'s own join above), then inserting,
    sidesteps that gotcha entirely — wrapped in one transaction (`with
    conn:`) so a crash between the two statements can't leave this
    relationship with zero rows.
    """
    with conn:
        conn.execute(
            """
            DELETE FROM doc_relation_enrichment
            WHERE source_doc_path = ?
              AND target_vendor_name IS ?
              AND target_doc_path IS ?
            """,
            (source_doc_path, target_vendor_name, target_doc_path),
        )
        conn.execute(
            """
            INSERT INTO doc_relation_enrichment (
                source_doc_path, target_vendor_name, target_doc_path,
                ai_summary, relation_label, content_hash, model, generated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_doc_path,
                target_vendor_name,
                target_doc_path,
                ai_summary,
                relation_label,
                content_hash,
                model,
                generated_at,
            ),
        )
