import sqlite3

from codecompass.graph import (
    DependsOnEdgeRow,
    DocArtifactRow,
    DocChunkRow,
    DocRelationEdgeRow,
    DocumentsEdgeRow,
    RoutesViaEdgeRow,
    SkillMentionEdgeRow,
    SourceFileRow,
    SymbolRow,
    UsesEdgeRow,
    VendorRow,
    doc_code_trace,
    doc_relations,
    documented_but_unused,
    enrichment_candidates,
    has_enrichment,
    init_schema,
    open_graph,
    rebuild_deterministic,
    record_enrichment,
    record_relation_enrichment,
    record_symbol_enrichment,
    relation_enrichment_candidates,
    skills_index,
    spec_docs_without_relations,
    symbol_profile,
    unused_vendors,
    used_but_undocumented,
    vendor_docs_without_relations,
    vendor_profile,
)

_ALL_TABLES = {
    "meta",
    "vendors",
    "source_files",
    "symbols",
    "uses_edges",
    "doc_artifacts",
    "doc_chunks",
    "documents_edges",
    "skill_mentions_edges",
    "routes_via_edges",
    "depends_on_edges",
    "doc_relations_edges",
    "vendor_enrichment",
    "symbol_enrichment",
    "doc_relation_enrichment",
}

_SOURCE_FILE = "src/app.ts"
_CLAUDE_MD_PATH = "vendor/used-lib/CLAUDE.md"
_SKILL_PATH = ".claude/skills/used-lib/SKILL.md"
_SPEC_DOC_PATH = "README.md"
_UNRELATED_SPEC_DOC_PATH = "docs/unrelated.md"


def _fixture_kwargs() -> dict:
    """2 vendors (one used, one not); the used vendor has three symbols
    covering all three coverage states (fully covered, used-but-
    undocumented, documented-but-unused); one doc artifact documenting two
    of them; one skill routed to the used vendor and mentioning it plus the
    one source file; a depends_on edge from the used vendor to the unused
    one; two spec docs, one mentioning the used vendor and the skill (one
    `doc_relations_edges` row of each kind) and one with zero relations.
    """
    return {
        "vendors": [
            VendorRow(name="used-lib", ecosystem="npm", installed_version="1.2.3"),
            VendorRow(name="unused-lib", ecosystem="python", installed_version="0.1.0"),
        ],
        "source_files": [SourceFileRow(path=_SOURCE_FILE)],
        "symbols": [
            SymbolRow(vendor_name="used-lib", name="doStuff", purpose="does stuff"),
            SymbolRow(vendor_name="used-lib", name="otherStuff"),
            SymbolRow(vendor_name="used-lib", name="docOnly"),
            SymbolRow(vendor_name="unused-lib", name="neverUsed"),
        ],
        "uses_edges": [
            UsesEdgeRow(
                source_file_path=_SOURCE_FILE, vendor_name="used-lib", symbol_name="doStuff",
                line=10,
            ),
            UsesEdgeRow(
                source_file_path=_SOURCE_FILE, vendor_name="used-lib", symbol_name="otherStuff",
                line=20,
            ),
        ],
        "doc_artifacts": [
            DocArtifactRow(
                path=_CLAUDE_MD_PATH,
                kind="claude_md",
                origin="codecompass_vendor",
                vendor_name="used-lib",
                name="used-lib CLAUDE.md",
            ),
            DocArtifactRow(
                path=_SKILL_PATH,
                kind="skill",
                origin="codecompass_tool",
                name="used-lib skill",
            ),
            DocArtifactRow(path=_SPEC_DOC_PATH, kind="spec_doc", origin="project"),
            DocArtifactRow(path=_UNRELATED_SPEC_DOC_PATH, kind="spec_doc", origin="project"),
        ],
        "documents_edges": [
            DocumentsEdgeRow(
                doc_artifact_path=_CLAUDE_MD_PATH, vendor_name="used-lib", symbol_name="doStuff"
            ),
            DocumentsEdgeRow(
                doc_artifact_path=_CLAUDE_MD_PATH, vendor_name="used-lib", symbol_name="docOnly"
            ),
        ],
        "skill_mentions_edges": [
            SkillMentionEdgeRow(doc_artifact_path=_SKILL_PATH, vendor_name="used-lib"),
            SkillMentionEdgeRow(doc_artifact_path=_SKILL_PATH, source_file_path=_SOURCE_FILE),
        ],
        "routes_via_edges": [
            RoutesViaEdgeRow(vendor_name="used-lib", doc_artifact_path=_SKILL_PATH),
        ],
        "depends_on_edges": [
            DependsOnEdgeRow(vendor_name="used-lib", depends_on_vendor_name="unused-lib"),
        ],
        "doc_relations_edges": [
            DocRelationEdgeRow(
                source_doc_artifact_path=_SPEC_DOC_PATH,
                relation_kind="mentions_dependency",
                target_vendor_name="used-lib",
            ),
            DocRelationEdgeRow(
                source_doc_artifact_path=_SPEC_DOC_PATH,
                relation_kind="mentions_artifact",
                target_doc_artifact_path=_SKILL_PATH,
            ),
        ],
    }


# --- Schema / connection ----------------------------------------------------


def test_open_graph_creates_db_file_and_all_tables(tmp_path) -> None:
    conn = open_graph(tmp_path)
    assert (tmp_path / "context-graph.db").exists()

    table_names = {
        name
        for (name,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    assert _ALL_TABLES <= table_names


def test_open_graph_enables_foreign_keys(tmp_path) -> None:
    conn = open_graph(tmp_path)
    (enabled,) = conn.execute("PRAGMA foreign_keys").fetchone()
    assert enabled == 1


def test_init_schema_seeds_schema_version(tmp_path) -> None:
    conn = open_graph(tmp_path)
    (value,) = conn.execute(
        "SELECT value FROM meta WHERE key = 'schema_version'"
    ).fetchone()
    assert value == "6"


def test_init_schema_is_idempotent(tmp_path) -> None:
    conn = sqlite3.connect(tmp_path / "context-graph.db")
    init_schema(conn)
    init_schema(conn)  # must not raise
    (value,) = conn.execute(
        "SELECT value FROM meta WHERE key = 'schema_version'"
    ).fetchone()
    assert value == "6"


def test_doc_artifacts_accepts_slash_command_kind(tmp_path) -> None:
    """Phase 17: `doc_artifacts.kind`'s CHECK constraint was widened to
    include `'slash_command'` — a fresh database must accept it directly
    (the migration test below covers an already-existing pre-Phase-17 db).
    """
    conn = open_graph(tmp_path)
    conn.execute(
        "INSERT INTO doc_artifacts (kind, origin, path) VALUES "
        "('slash_command', 'codecompass_tool', '.claude/commands/discovery.md')"
    )  # must not raise


def test_doc_artifacts_accepts_spec_doc_kind_and_project_origin(tmp_path) -> None:
    """Phase 21: `doc_artifacts.kind`'s CHECK constraint gained `'spec_doc'`
    and `origin`'s gained `'project'` — a fresh database must accept both
    directly (a migration test below covers an already-existing
    pre-Phase-21 db).
    """
    conn = open_graph(tmp_path)
    conn.execute(
        "INSERT INTO doc_artifacts (kind, origin, path) VALUES ('spec_doc', 'project', 'README.md')"
    )  # must not raise


def test_doc_artifacts_accepts_vendor_doc_kind_and_vendor_upstream_origin(tmp_path) -> None:
    """Phase 27: `doc_artifacts.kind`'s CHECK constraint gained `'vendor_doc'`
    and `origin`'s gained `'vendor_upstream'` — a fresh database must accept
    both directly (a migration test below covers an already-existing
    pre-Phase-27 db).
    """
    conn = open_graph(tmp_path)
    conn.execute(
        "INSERT INTO doc_artifacts (kind, origin, path) VALUES "
        "('vendor_doc', 'vendor_upstream', 'vendor/demo/src/README.md')"
    )  # must not raise


def test_open_graph_migrates_pre_phase_17_schema(tmp_path) -> None:
    """Simulates a `context-graph.db` created before Phase 17
    (`schema_version` "1", `doc_artifacts.kind`'s CHECK constraint not yet
    widened) — `open_graph` must migrate it in place on next open: bump
    `schema_version`, drop+recreate `doc_artifacts` under the new
    constraint (cascading away any stale referencing rows in
    `documents_edges`), and leave `vendor_enrichment` completely untouched.
    """
    db_path = tmp_path / "context-graph.db"
    old_conn = sqlite3.connect(db_path)
    old_conn.execute("PRAGMA foreign_keys = ON")
    old_conn.executescript(
        """
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE vendors (
          id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE,
          ecosystem TEXT NOT NULL, installed_version TEXT
        );
        CREATE TABLE doc_artifacts (
          id INTEGER PRIMARY KEY,
          vendor_id INTEGER REFERENCES vendors(id) ON DELETE CASCADE,
          kind TEXT NOT NULL CHECK (kind IN ('claude_md','overview','skill','cursor_mdc')),
          origin TEXT, path TEXT NOT NULL UNIQUE, name TEXT, description TEXT
        );
        CREATE TABLE documents_edges (
          id INTEGER PRIMARY KEY,
          doc_artifact_id INTEGER NOT NULL REFERENCES doc_artifacts(id) ON DELETE CASCADE,
          symbol_id INTEGER NOT NULL
        );
        CREATE TABLE vendor_enrichment (
          id INTEGER PRIMARY KEY,
          vendor_id INTEGER NOT NULL UNIQUE REFERENCES vendors(id) ON DELETE CASCADE,
          technical_description TEXT, symbol_set_hash TEXT NOT NULL,
          model TEXT NOT NULL, generated_at TEXT NOT NULL
        );
        """
    )
    old_conn.execute("INSERT INTO meta (key, value) VALUES ('schema_version', '1')")
    old_conn.execute(
        "INSERT INTO vendors (id, name, ecosystem, installed_version) "
        "VALUES (1, 'demo', 'python', '1.0.0')"
    )
    old_conn.execute(
        "INSERT INTO doc_artifacts (id, kind, origin, path) VALUES "
        "(1, 'skill', 'codecompass_tool', '.claude/skills/codecompass/SKILL.md')"
    )
    old_conn.execute("INSERT INTO documents_edges (doc_artifact_id, symbol_id) VALUES (1, 1)")
    old_conn.execute(
        "INSERT INTO vendor_enrichment "
        "(vendor_id, technical_description, symbol_set_hash, model, generated_at) VALUES "
        "(1, 'A demo library.', 'hash-abc', 'claude-haiku-4-5', '2026-01-01T00:00:00+00:00')"
    )
    old_conn.commit()
    old_conn.close()

    conn = open_graph(tmp_path)

    (schema_version,) = conn.execute(
        "SELECT value FROM meta WHERE key = 'schema_version'"
    ).fetchone()
    assert schema_version == "6"

    # Would raise sqlite3.IntegrityError under the pre-migration constraint.
    conn.execute(
        "INSERT INTO doc_artifacts (kind, origin, path) VALUES "
        "('slash_command', 'codecompass_tool', '.claude/commands/discovery.md')"
    )
    # Same for Phase 21's and Phase 27's widened values, migrated to in the
    # same pass since this simulated db's stored version ("1") is older
    # than all three.
    conn.execute(
        "INSERT INTO doc_artifacts (kind, origin, path) VALUES ('spec_doc', 'project', 'README.md')"
    )
    conn.execute(
        "INSERT INTO doc_artifacts (kind, origin, path) VALUES "
        "('vendor_doc', 'vendor_upstream', 'vendor/demo/src/README.md')"
    )

    # The stale documents_edges row (referencing a doc_artifacts id wiped
    # out by the migration's drop+recreate) was cascade-cleared, not left
    # dangling.
    (edge_count,) = conn.execute("SELECT COUNT(*) FROM documents_edges").fetchone()
    assert edge_count == 0

    # vendor_enrichment has no foreign key to doc_artifacts at all — this
    # migration can't reach it, and doesn't.
    (technical_description, symbol_set_hash) = conn.execute(
        "SELECT technical_description, symbol_set_hash FROM vendor_enrichment WHERE vendor_id = 1"
    ).fetchone()
    assert technical_description == "A demo library."
    assert symbol_set_hash == "hash-abc"


def test_open_graph_migrates_pre_phase_21_schema(tmp_path) -> None:
    """Simulates a `context-graph.db` created at Phase 17-20's schema
    (`schema_version` "2", `doc_artifacts.kind`/`origin` CHECK constraints
    not yet widened for spec docs) — `open_graph` must migrate it in place:
    bump `schema_version` (now "6", since this simulated db's stored
    version is older than every widening since) and accept
    `kind='spec_doc'`, `origin='project'` afterward. `doc_relations_edges`
    itself needs no migration (a brand-new table `init_schema`'s `CREATE
    TABLE IF NOT EXISTS` creates directly), only `doc_artifacts`'s
    constraints do.
    """
    db_path = tmp_path / "context-graph.db"
    old_conn = sqlite3.connect(db_path)
    old_conn.execute("PRAGMA foreign_keys = ON")
    old_conn.executescript(
        """
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE vendors (
          id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE,
          ecosystem TEXT NOT NULL, installed_version TEXT
        );
        CREATE TABLE doc_artifacts (
          id INTEGER PRIMARY KEY,
          vendor_id INTEGER REFERENCES vendors(id) ON DELETE CASCADE,
          kind TEXT NOT NULL CHECK (
            kind IN ('claude_md','overview','skill','cursor_mdc','slash_command')
          ),
          origin TEXT CHECK (origin IN ('codecompass_tool','codecompass_vendor','third_party')),
          path TEXT NOT NULL UNIQUE, name TEXT, description TEXT
        );
        """
    )
    old_conn.execute("INSERT INTO meta (key, value) VALUES ('schema_version', '2')")
    old_conn.commit()
    old_conn.close()

    conn = open_graph(tmp_path)

    (schema_version,) = conn.execute(
        "SELECT value FROM meta WHERE key = 'schema_version'"
    ).fetchone()
    assert schema_version == "6"

    # Would raise sqlite3.IntegrityError under the pre-Phase-21 constraints.
    conn.execute(
        "INSERT INTO doc_artifacts (kind, origin, path) VALUES ('spec_doc', 'project', 'README.md')"
    )
    # Same for Phase 27's widened values.
    conn.execute(
        "INSERT INTO doc_artifacts (kind, origin, path) VALUES "
        "('vendor_doc', 'vendor_upstream', 'vendor/demo/src/README.md')"
    )

    table_names = {
        name for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    assert "doc_relations_edges" in table_names


def test_open_graph_migrates_pre_phase_27_schema(tmp_path) -> None:
    """Simulates a `context-graph.db` created at Phase 21-26's schema
    (`schema_version` "3", `doc_artifacts.kind`/`origin` CHECK constraints
    not yet widened for vendor-embedded upstream docs) — `open_graph` must
    migrate it in place: bump `schema_version` to "6" (current, since this
    simulated db's stored version is older than every widening since) and
    accept `kind='vendor_doc'`, `origin='vendor_upstream'` afterward.
    """
    db_path = tmp_path / "context-graph.db"
    old_conn = sqlite3.connect(db_path)
    old_conn.execute("PRAGMA foreign_keys = ON")
    old_conn.executescript(
        """
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE vendors (
          id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE,
          ecosystem TEXT NOT NULL, installed_version TEXT
        );
        CREATE TABLE doc_artifacts (
          id INTEGER PRIMARY KEY,
          vendor_id INTEGER REFERENCES vendors(id) ON DELETE CASCADE,
          kind TEXT NOT NULL CHECK (
            kind IN ('claude_md','overview','skill','cursor_mdc','slash_command','spec_doc')
          ),
          origin TEXT CHECK (
            origin IN ('codecompass_tool','codecompass_vendor','third_party','project')
          ),
          path TEXT NOT NULL UNIQUE, name TEXT, description TEXT
        );
        """
    )
    old_conn.execute("INSERT INTO meta (key, value) VALUES ('schema_version', '3')")
    old_conn.commit()
    old_conn.close()

    conn = open_graph(tmp_path)

    (schema_version,) = conn.execute(
        "SELECT value FROM meta WHERE key = 'schema_version'"
    ).fetchone()
    assert schema_version == "6"

    # Would raise sqlite3.IntegrityError under the pre-Phase-27 constraints.
    conn.execute(
        "INSERT INTO doc_artifacts (kind, origin, path) VALUES "
        "('vendor_doc', 'vendor_upstream', 'vendor/demo/src/README.md')"
    )


def test_open_graph_migration_is_noop_when_schema_version_already_current(tmp_path) -> None:
    """A second `open_graph` call against an already-current-version
    database must not drop/recreate `doc_artifacts` again (which would
    needlessly discard same-run data mid-session).
    """
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    conn.close()

    conn = open_graph(tmp_path)

    (doc_artifact_count,) = conn.execute("SELECT COUNT(*) FROM doc_artifacts").fetchone()
    assert doc_artifact_count == len(_fixture_kwargs()["doc_artifacts"])


def test_open_graph_migrates_pre_phase_31_schema_preserves_existing_rows(tmp_path) -> None:
    """Simulates a `context-graph.db` created before Phase 31
    (`schema_version` "4", `doc_relation_enrichment` with no
    `relation_label` column) with one real paid-enrichment row already on
    disk — `open_graph` must add the column via `ALTER TABLE ADD COLUMN`,
    not `_migrate_doc_artifacts_constraints`'s drop-and-recreate approach:
    this table holds paid AI spend that must survive the migration, unlike
    `doc_artifacts`, which is safe to drop because it's always fully
    rewritten by the next `rebuild_deterministic` anyway.
    """
    db_path = tmp_path / "context-graph.db"
    old_conn = sqlite3.connect(db_path)
    old_conn.executescript(
        """
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE doc_relation_enrichment (
          id INTEGER PRIMARY KEY,
          source_doc_path TEXT NOT NULL,
          target_vendor_name TEXT,
          target_doc_path TEXT,
          ai_summary TEXT NOT NULL,
          content_hash TEXT NOT NULL,
          model TEXT NOT NULL,
          generated_at TEXT NOT NULL,
          UNIQUE (source_doc_path, target_vendor_name, target_doc_path)
        );
        """
    )
    old_conn.execute("INSERT INTO meta (key, value) VALUES ('schema_version', '4')")
    old_conn.execute(
        "INSERT INTO doc_relation_enrichment "
        "(source_doc_path, target_vendor_name, target_doc_path, ai_summary, "
        "content_hash, model, generated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "README.md",
            "demo",
            None,
            "pre-existing summary",
            "hash-1",
            "claude-haiku-4-5-20251001",
            "2026-01-01T00:00:00+00:00",
        ),
    )
    old_conn.commit()
    old_conn.close()

    conn = open_graph(tmp_path)

    row = conn.execute(
        "SELECT ai_summary, relation_label FROM doc_relation_enrichment "
        "WHERE source_doc_path = 'README.md'"
    ).fetchone()
    assert row == ("pre-existing summary", None)

    # Would raise sqlite3.IntegrityError under a CHECK rejecting an unknown label.
    conn.execute(
        "UPDATE doc_relation_enrichment SET relation_label = 'explains_usage_of' "
        "WHERE source_doc_path = 'README.md'"
    )


def test_open_graph_relation_label_migration_is_idempotent(tmp_path) -> None:
    """A second `open_graph` call against an already-migrated database must
    not attempt `ALTER TABLE ADD COLUMN` again, which would raise
    `sqlite3.OperationalError: duplicate column name`.
    """
    conn = open_graph(tmp_path)
    conn.close()

    conn = open_graph(tmp_path)  # must not raise

    columns = {row[1] for row in conn.execute("PRAGMA table_info(doc_relation_enrichment)")}
    assert "relation_label" in columns


# --- rebuild_deterministic ---------------------------------------------------


def test_rebuild_deterministic_populates_tables(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    (vendor_count,) = conn.execute("SELECT COUNT(*) FROM vendors").fetchone()
    (symbol_count,) = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()
    (uses_count,) = conn.execute("SELECT COUNT(*) FROM uses_edges").fetchone()
    assert vendor_count == 2
    assert symbol_count == 4
    assert uses_count == 2


def test_rebuild_deterministic_sets_last_rebuild_timestamp(tmp_path) -> None:
    conn = open_graph(tmp_path)
    assert conn.execute(
        "SELECT value FROM meta WHERE key = 'last_deterministic_rebuild_at'"
    ).fetchone() is None

    rebuild_deterministic(conn, **_fixture_kwargs())

    (value,) = conn.execute(
        "SELECT value FROM meta WHERE key = 'last_deterministic_rebuild_at'"
    ).fetchone()
    assert value  # non-empty ISO timestamp string


def test_rebuild_deterministic_is_repeatable_without_duplicating_rows(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    rebuild_deterministic(conn, **_fixture_kwargs())

    (vendor_count,) = conn.execute("SELECT COUNT(*) FROM vendors").fetchone()
    (symbol_count,) = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()
    (uses_count,) = conn.execute("SELECT COUNT(*) FROM uses_edges").fetchone()
    assert vendor_count == 2
    assert symbol_count == 4
    assert uses_count == 2


def test_rebuild_deterministic_preserves_vendor_id_across_rebuilds(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    (id_before,) = conn.execute(
        "SELECT id FROM vendors WHERE name = 'used-lib'"
    ).fetchone()

    rebuild_deterministic(conn, **_fixture_kwargs())
    (id_after,) = conn.execute(
        "SELECT id FROM vendors WHERE name = 'used-lib'"
    ).fetchone()

    assert id_before == id_after


def test_rebuild_deterministic_removes_vendors_and_symbols_no_longer_present(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    # A fixture that drops the "unused-lib" vendor and the "docOnly" symbol.
    kwargs = _fixture_kwargs()
    kwargs["vendors"] = [v for v in kwargs["vendors"] if v.name != "unused-lib"]
    kwargs["symbols"] = [
        s for s in kwargs["symbols"] if s.vendor_name != "unused-lib" and s.name != "docOnly"
    ]
    kwargs["depends_on_edges"] = []
    kwargs["documents_edges"] = [
        e for e in kwargs["documents_edges"] if e.symbol_name != "docOnly"
    ]
    rebuild_deterministic(conn, **kwargs)

    remaining_vendors = {
        name for (name,) in conn.execute("SELECT name FROM vendors")
    }
    remaining_symbols = {
        name for (name,) in conn.execute("SELECT name FROM symbols")
    }
    assert remaining_vendors == {"used-lib"}
    assert "docOnly" not in remaining_symbols


def test_rebuild_deterministic_never_touches_vendor_enrichment(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    (vendor_id,) = conn.execute(
        "SELECT id FROM vendors WHERE name = 'used-lib'"
    ).fetchone()
    record_enrichment(
        conn,
        vendor_id,
        technical_description="A used library.",
        conversational_overview="Does stuff.",
        action_pointer_file="index.ts",
        action_pointer_note="Entry point.",
        symbol_set_hash="hash-abc123",
        model="claude-haiku-4-5",
        generated_at="2026-01-01T00:00:00+00:00",
    )
    before = conn.execute(
        "SELECT * FROM vendor_enrichment WHERE vendor_id = ?", (vendor_id,)
    ).fetchone()

    rebuild_deterministic(conn, **_fixture_kwargs())

    after = conn.execute(
        "SELECT * FROM vendor_enrichment WHERE vendor_id = ?", (vendor_id,)
    ).fetchone()
    assert before == after
    assert after is not None


def test_rebuild_deterministic_never_touches_symbol_enrichment(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    (symbol_id,) = conn.execute(
        "SELECT id FROM symbols WHERE name = 'doStuff'"
    ).fetchone()
    record_symbol_enrichment(
        conn, symbol_id, purpose="Does the stuff.", generated_at="2026-01-01T00:00:00+00:00"
    )
    before = conn.execute(
        "SELECT * FROM symbol_enrichment WHERE symbol_id = ?", (symbol_id,)
    ).fetchone()

    rebuild_deterministic(conn, **_fixture_kwargs())

    after = conn.execute(
        "SELECT * FROM symbol_enrichment WHERE symbol_id = ?", (symbol_id,)
    ).fetchone()
    assert before == after
    assert after is not None


def test_record_enrichment_upserts_on_second_call(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    (vendor_id,) = conn.execute(
        "SELECT id FROM vendors WHERE name = 'used-lib'"
    ).fetchone()

    record_enrichment(
        conn,
        vendor_id,
        symbol_set_hash="hash-v1",
        model="claude-haiku-4-5",
        generated_at="2026-01-01T00:00:00+00:00",
    )
    record_enrichment(
        conn,
        vendor_id,
        symbol_set_hash="hash-v2",
        model="claude-haiku-4-5",
        generated_at="2026-01-02T00:00:00+00:00",
    )

    (count,) = conn.execute(
        "SELECT COUNT(*) FROM vendor_enrichment WHERE vendor_id = ?", (vendor_id,)
    ).fetchone()
    (hash_,) = conn.execute(
        "SELECT symbol_set_hash FROM vendor_enrichment WHERE vendor_id = ?", (vendor_id,)
    ).fetchone()
    assert count == 1
    assert hash_ == "hash-v2"


# --- Query functions ---------------------------------------------------------


def test_unused_vendors_lists_exactly_the_unused_vendor(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    assert unused_vendors(conn) == ["unused-lib"]


def test_documented_but_unused_lists_the_undocumented_pair(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    assert documented_but_unused(conn) == [("used-lib", "docOnly")]


def test_used_but_undocumented_lists_the_uncovered_pair(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    assert used_but_undocumented(conn) == [("used-lib", "otherStuff")]


def test_fully_covered_symbol_appears_in_neither_gap_query(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    assert ("used-lib", "doStuff") not in documented_but_unused(conn)
    assert ("used-lib", "doStuff") not in used_but_undocumented(conn)


def test_vendor_profile_for_used_vendor(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    profile = vendor_profile(conn, "used-lib")

    assert profile is not None
    assert profile["vendor"]["name"] == "used-lib"
    assert profile["vendor"]["ecosystem"] == "npm"
    assert profile["vendor"]["installed_version"] == "1.2.3"
    # SQLite's default BINARY collation sorts uppercase before lowercase,
    # so "doStuff" (capital S) sorts before "docOnly" (lowercase c).
    assert [s["name"] for s in profile["symbols"]] == ["doStuff", "docOnly", "otherStuff"]
    assert profile["usage_count"] == 2
    assert [d["path"] for d in profile["documenting_artifacts"]] == [_CLAUDE_MD_PATH]
    assert [s["path"] for s in profile["routed_skills"]] == [_SKILL_PATH]
    assert profile["depends_on"] == ["unused-lib"]
    assert profile["used_at"] == [
        {"source_file_path": _SOURCE_FILE, "line": 10},
        {"source_file_path": _SOURCE_FILE, "line": 20},
    ]


def test_vendor_profile_for_nonexistent_vendor_is_none(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    assert vendor_profile(conn, "does-not-exist") is None


def test_symbol_profile_returns_every_match_across_vendors(tmp_path) -> None:
    conn = open_graph(tmp_path)
    kwargs = _fixture_kwargs()
    kwargs["symbols"].append(SymbolRow(vendor_name="unused-lib", name="doStuff"))
    rebuild_deterministic(conn, **kwargs)

    profiles = symbol_profile(conn, "doStuff")

    assert {p["vendor"] for p in profiles} == {"used-lib", "unused-lib"}
    used_lib_profile = next(p for p in profiles if p["vendor"] == "used-lib")
    assert used_lib_profile["usage_count"] == 1
    assert [d["path"] for d in used_lib_profile["documenting_artifacts"]] == [_CLAUDE_MD_PATH]
    assert used_lib_profile["used_at"] == [{"source_file_path": _SOURCE_FILE, "line": 10}]
    unused_lib_profile = next(p for p in profiles if p["vendor"] == "unused-lib")
    assert unused_lib_profile["usage_count"] == 0
    assert unused_lib_profile["documenting_artifacts"] == []
    assert unused_lib_profile["used_at"] == []


def test_symbol_profile_for_nonexistent_symbol_is_empty(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    assert symbol_profile(conn, "doesNotExist") == []


def test_doc_code_trace_via_documents_edges(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    trace = doc_code_trace(conn, _CLAUDE_MD_PATH)

    assert trace == [
        {
            "via": "documents",
            "vendor": "used-lib",
            "symbol": "doStuff",
            "source_file_path": _SOURCE_FILE,
            "line": 10,
            "heading": None,
        }
    ]


def test_doc_code_trace_via_mentions_dependency(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    trace = doc_code_trace(conn, _SPEC_DOC_PATH)

    assert [t["via"] for t in trace] == ["mentions_dependency", "mentions_dependency"]
    assert all(t["vendor"] == "used-lib" and t["symbol"] is None for t in trace)
    assert {t["line"] for t in trace} == {10, 20}


def test_doc_code_trace_via_vendor_name(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    trace = doc_code_trace(conn, "used-lib")

    assert [t["via"] for t in trace] == ["direct_usage", "direct_usage"]
    assert {t["line"] for t in trace} == {10, 20}


def test_doc_code_trace_for_unknown_name_is_empty(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    assert doc_code_trace(conn, "does-not-exist") == []


def test_rebuild_deterministic_populates_doc_chunks_and_resolves_chunk_id(tmp_path) -> None:
    """Phase 32 end-to-end: `doc_chunks` rows are inserted, and both
    `DocumentsEdgeRow.chunk_start_line`/`DocRelationEdgeRow.chunk_start_line`
    resolve to the right integer `chunk_id` — surfaced back out as
    `heading` by `doc_relations`/`doc_code_trace`.
    """
    kwargs = _fixture_kwargs()
    kwargs["doc_chunks"] = [
        DocChunkRow(
            doc_artifact_path=_CLAUDE_MD_PATH,
            heading_path="API",
            start_line=1,
            end_line=5,
            content_hash="hash-claude-md-chunk",
        ),
        DocChunkRow(
            doc_artifact_path=_SPEC_DOC_PATH,
            heading_path="Dependencies",
            start_line=1,
            end_line=3,
            content_hash="hash-readme-chunk",
        ),
    ]
    kwargs["documents_edges"] = [
        DocumentsEdgeRow(
            doc_artifact_path=_CLAUDE_MD_PATH,
            vendor_name="used-lib",
            symbol_name="doStuff",
            chunk_start_line=1,
        ),
        DocumentsEdgeRow(
            doc_artifact_path=_CLAUDE_MD_PATH, vendor_name="used-lib", symbol_name="docOnly"
        ),
    ]
    kwargs["doc_relations_edges"] = [
        DocRelationEdgeRow(
            source_doc_artifact_path=_SPEC_DOC_PATH,
            relation_kind="mentions_dependency",
            target_vendor_name="used-lib",
            chunk_start_line=1,
        ),
        DocRelationEdgeRow(
            source_doc_artifact_path=_SPEC_DOC_PATH,
            relation_kind="mentions_artifact",
            target_doc_artifact_path=_SKILL_PATH,
        ),
    ]

    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **kwargs)

    (chunk_count,) = conn.execute("SELECT COUNT(*) FROM doc_chunks").fetchone()
    assert chunk_count == 2

    relations = doc_relations(conn, _SPEC_DOC_PATH)
    dependency = next(r for r in relations if r["relation_kind"] == "mentions_dependency")
    assert dependency["heading"] == "Dependencies"
    artifact = next(r for r in relations if r["relation_kind"] == "mentions_artifact")
    assert artifact["heading"] is None  # no chunk_start_line given for this edge

    documents_trace = doc_code_trace(conn, _CLAUDE_MD_PATH)
    do_stuff_row = next(t for t in documents_trace if t["symbol"] == "doStuff")
    assert do_stuff_row["heading"] == "API"

    mentions_trace = doc_code_trace(conn, _SPEC_DOC_PATH)
    dependency_rows = [t for t in mentions_trace if t["via"] == "mentions_dependency"]
    assert dependency_rows and all(t["heading"] == "Dependencies" for t in dependency_rows)


def test_rebuild_deterministic_doc_chunks_default_is_empty_and_backward_compatible(
    tmp_path,
) -> None:
    """Pre-Phase-32 callers/tests that don't pass `doc_chunks` at all must
    keep working unchanged — `chunk_id` simply stays `NULL` everywhere.
    """
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())  # no doc_chunks key

    (chunk_count,) = conn.execute("SELECT COUNT(*) FROM doc_chunks").fetchone()
    assert chunk_count == 0

    relations = doc_relations(conn, _SPEC_DOC_PATH)
    assert all(r["heading"] is None for r in relations)


def test_open_graph_migrates_pre_phase_32_schema_adds_chunk_id_columns(tmp_path) -> None:
    """Simulates a `context-graph.db` created at Phase 30-31's schema
    (`schema_version` "5", `documents_edges`/`doc_relations_edges` with no
    `chunk_id` column and no `doc_chunks` table at all) — `open_graph`
    must migrate it in place: drop+recreate both edge tables under their
    current (widened) column set and create `doc_chunks` fresh. Safe the
    same way `doc_artifacts`'s own migration is — both edge tables are
    fully cleared and reinserted by `rebuild_deterministic` on every
    whole-project sync regardless.
    """
    db_path = tmp_path / "context-graph.db"
    old_conn = sqlite3.connect(db_path)
    old_conn.executescript(
        """
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE vendors (
          id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE,
          ecosystem TEXT NOT NULL, installed_version TEXT
        );
        CREATE TABLE doc_artifacts (
          id INTEGER PRIMARY KEY,
          vendor_id INTEGER REFERENCES vendors(id) ON DELETE CASCADE,
          kind TEXT NOT NULL, origin TEXT,
          path TEXT NOT NULL UNIQUE, name TEXT, description TEXT
        );
        CREATE TABLE symbols (
          id INTEGER PRIMARY KEY,
          vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
          name TEXT NOT NULL, purpose TEXT
        );
        CREATE TABLE documents_edges (
          id INTEGER PRIMARY KEY,
          doc_artifact_id INTEGER NOT NULL REFERENCES doc_artifacts(id) ON DELETE CASCADE,
          symbol_id INTEGER NOT NULL REFERENCES symbols(id) ON DELETE CASCADE
        );
        CREATE TABLE doc_relations_edges (
          id INTEGER PRIMARY KEY,
          source_doc_artifact_id INTEGER NOT NULL REFERENCES doc_artifacts(id) ON DELETE CASCADE,
          target_vendor_id INTEGER REFERENCES vendors(id) ON DELETE CASCADE,
          target_doc_artifact_id INTEGER REFERENCES doc_artifacts(id) ON DELETE CASCADE,
          relation_kind TEXT NOT NULL
        );
        """
    )
    old_conn.execute("INSERT INTO meta (key, value) VALUES ('schema_version', '5')")
    old_conn.commit()
    old_conn.close()

    conn = open_graph(tmp_path)

    (schema_version,) = conn.execute(
        "SELECT value FROM meta WHERE key = 'schema_version'"
    ).fetchone()
    assert schema_version == "6"

    documents_edges_columns = {row[1] for row in conn.execute("PRAGMA table_info(documents_edges)")}
    doc_relations_edges_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(doc_relations_edges)")
    }
    assert "chunk_id" in documents_edges_columns
    assert "chunk_id" in doc_relations_edges_columns

    table_names = {
        name for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    assert "doc_chunks" in table_names


def test_skills_index_lists_skill_artifacts_and_mentions(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    index = skills_index(conn)

    assert len(index) == 1
    entry = index[0]
    assert entry["path"] == _SKILL_PATH
    assert entry["origin"] == "codecompass_tool"
    assert entry["mentions_vendors"] == ["used-lib"]
    assert entry["mentions_source_files"] == [_SOURCE_FILE]


def test_enrichment_candidates_lists_only_vendors_with_usage(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    candidates = enrichment_candidates(conn)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate["vendor"] == "used-lib"
    assert candidate["used_symbols"] == ["doStuff", "otherStuff"]
    assert candidate["symbol_set_hash"] is None


def test_enrichment_candidates_surfaces_existing_symbol_set_hash(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    (vendor_id,) = conn.execute(
        "SELECT id FROM vendors WHERE name = 'used-lib'"
    ).fetchone()
    record_enrichment(
        conn,
        vendor_id,
        symbol_set_hash="hash-abc123",
        model="claude-haiku-4-5",
        generated_at="2026-01-01T00:00:00+00:00",
    )

    candidates = enrichment_candidates(conn)

    assert candidates[0]["symbol_set_hash"] == "hash-abc123"


# --- has_enrichment -----------------------------------------------------


def test_has_enrichment_false_before_any_enrichment(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    assert has_enrichment(conn, "used-lib") is False


def test_has_enrichment_true_after_record_enrichment(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    (vendor_id,) = conn.execute(
        "SELECT id FROM vendors WHERE name = 'used-lib'"
    ).fetchone()
    record_enrichment(
        conn,
        vendor_id,
        symbol_set_hash="hash-abc123",
        model="claude-haiku-4-5",
        generated_at="2026-01-01T00:00:00+00:00",
    )

    assert has_enrichment(conn, "used-lib") is True


def test_has_enrichment_false_for_unknown_vendor(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    assert has_enrichment(conn, "does-not-exist") is False


# --- doc_relations / spec_docs_without_relations -----------------------


def test_doc_relations_lists_both_relation_kinds_for_a_spec_doc(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    relations = doc_relations(conn, _SPEC_DOC_PATH)

    kinds = {r["relation_kind"] for r in relations}
    assert kinds == {"mentions_dependency", "mentions_artifact"}
    dependency_relation = next(r for r in relations if r["relation_kind"] == "mentions_dependency")
    assert dependency_relation["target_vendor"] == "used-lib"
    assert dependency_relation["target_doc_artifact_path"] is None
    artifact_relation = next(r for r in relations if r["relation_kind"] == "mentions_artifact")
    assert artifact_relation["target_doc_artifact_path"] == _SKILL_PATH
    assert artifact_relation["target_vendor"] is None


def test_doc_relations_empty_for_spec_doc_with_no_relations(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    assert doc_relations(conn, _UNRELATED_SPEC_DOC_PATH) == []


def test_doc_relations_empty_for_unknown_path(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    assert doc_relations(conn, "does/not/exist.md") == []


def test_spec_docs_without_relations_lists_only_the_unrelated_one(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    assert spec_docs_without_relations(conn) == [_UNRELATED_SPEC_DOC_PATH]


def test_vendor_docs_without_relations_lists_only_the_unmentioned_one(tmp_path) -> None:
    """A vendor doc (`kind='vendor_doc'`, Phase 27) is only ever a
    `doc_relations_edges` *target*, never a source — this checks the
    opposite column from `spec_docs_without_relations` above, not a
    parameterized copy of the same query (decisions/0041).
    """
    conn = open_graph(tmp_path)
    kwargs = _fixture_kwargs()
    mentioned_vendor_doc_path = "vendor/used-lib/src/README.md"
    unmentioned_vendor_doc_path = "vendor/unused-lib/src/README.md"
    kwargs["doc_artifacts"] = kwargs["doc_artifacts"] + [
        DocArtifactRow(
            path=mentioned_vendor_doc_path,
            kind="vendor_doc",
            origin="vendor_upstream",
            vendor_name="used-lib",
            name="used-lib README.md",
        ),
        DocArtifactRow(
            path=unmentioned_vendor_doc_path,
            kind="vendor_doc",
            origin="vendor_upstream",
            vendor_name="unused-lib",
            name="unused-lib README.md",
        ),
    ]
    kwargs["doc_relations_edges"] = kwargs["doc_relations_edges"] + [
        DocRelationEdgeRow(
            source_doc_artifact_path=_SPEC_DOC_PATH,
            relation_kind="mentions_artifact",
            target_doc_artifact_path=mentioned_vendor_doc_path,
        ),
    ]
    rebuild_deterministic(conn, **kwargs)

    assert vendor_docs_without_relations(conn) == [unmentioned_vendor_doc_path]


# --- doc_relation_enrichment (Phase 22) --------------------------------------


def test_doc_relation_enrichment_has_no_foreign_key(tmp_path) -> None:
    """The central design point of Phase 22 (decisions/0038): unlike
    `vendor_enrichment`/`symbol_enrichment` (FK to an upserted-by-natural-
    key row), `doc_relation_enrichment` must have *no* foreign key to
    `doc_artifacts` at all — that table is fully deleted and reinserted on
    every `rebuild_deterministic` call, so an FK here would cascade this
    table's whole content away on every whole-project sync.
    """
    conn = open_graph(tmp_path)
    fk_rows = conn.execute("PRAGMA foreign_key_list(doc_relation_enrichment)").fetchall()
    assert fk_rows == []


def test_record_relation_enrichment_survives_rebuild_deterministic(tmp_path) -> None:
    """The concrete regression test for the same design point: unlike
    `doc_relations_edges` (fully cleared on every rebuild), a `doc_
    relation_enrichment` row recorded via `record_relation_enrichment` must
    still be there — untouched — after a second `rebuild_deterministic`
    call, even though that call deletes and reinserts every `doc_
    artifacts` row (and everything that cascades from it).
    """
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    record_relation_enrichment(
        conn,
        _SPEC_DOC_PATH,
        "used-lib",
        None,
        "This README explains why used-lib is the tracked HTTP client.",
        "hash-1",
        "claude-haiku-4-5-20251001",
        "2026-01-01T00:00:00+00:00",
    )

    # A second whole-project rebuild — same fixture, deletes+reinserts
    # doc_artifacts and everything cascading from it.
    rebuild_deterministic(conn, **_fixture_kwargs())

    row = conn.execute(
        "SELECT ai_summary, content_hash FROM doc_relation_enrichment "
        "WHERE source_doc_path = ? AND target_vendor_name = ?",
        (_SPEC_DOC_PATH, "used-lib"),
    ).fetchone()
    assert row == (
        "This README explains why used-lib is the tracked HTTP client.",
        "hash-1",
    )


def test_record_relation_enrichment_updates_in_place_not_duplicated(tmp_path) -> None:
    """Regression for the NULL-uniqueness footgun `record_relation_
    enrichment`'s docstring explains: a naive `ON CONFLICT` on a UNIQUE
    index over nullable columns never detects a conflict when the
    non-matching column is NULL (SQL treats every NULL as distinct from
    every other NULL), so a second call for the same natural-key triple
    must still result in exactly one row, not two.
    """
    conn = open_graph(tmp_path)
    record_relation_enrichment(
        conn,
        "README.md",
        "demo",
        None,
        "first summary",
        "hash-a",
        "claude-haiku-4-5-20251001",
        "2026-01-01T00:00:00+00:00",
    )
    record_relation_enrichment(
        conn,
        "README.md",
        "demo",
        None,
        "second summary",
        "hash-b",
        "claude-haiku-4-5-20251001",
        "2026-01-02T00:00:00+00:00",
    )

    rows = conn.execute(
        "SELECT ai_summary, content_hash FROM doc_relation_enrichment "
        "WHERE source_doc_path = 'README.md' AND target_vendor_name = 'demo'"
    ).fetchall()
    assert rows == [("second summary", "hash-b")]


def test_relation_enrichment_candidates_lists_both_relation_kinds(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())

    candidates = relation_enrichment_candidates(conn)

    by_kind = {c["relation_kind"]: c for c in candidates}
    assert by_kind["mentions_dependency"]["source_doc_path"] == _SPEC_DOC_PATH
    assert by_kind["mentions_dependency"]["target_vendor_name"] == "used-lib"
    assert by_kind["mentions_dependency"]["target_doc_path"] is None
    assert by_kind["mentions_dependency"]["target_doc_artifact_name"] is None
    assert by_kind["mentions_dependency"]["content_hash"] is None
    assert by_kind["mentions_artifact"]["target_doc_path"] == _SKILL_PATH
    assert by_kind["mentions_artifact"]["target_vendor_name"] is None
    # Phase 28: the target doc artifact's own `name` field (the literal
    # `doc_mapping.build_doc_relations_edges` word-boundary-matched),
    # distinct from its `path` above — `select_candidates` needs this to
    # re-find the same mechanical match and center the excerpt on it.
    assert by_kind["mentions_artifact"]["target_doc_artifact_name"] == "used-lib skill"
    assert by_kind["mentions_artifact"]["content_hash"] is None


def test_relation_enrichment_candidates_surfaces_existing_content_hash(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    record_relation_enrichment(
        conn,
        _SPEC_DOC_PATH,
        "used-lib",
        None,
        "summary",
        "matching-hash",
        "claude-haiku-4-5-20251001",
        "2026-01-01T00:00:00+00:00",
    )

    candidates = relation_enrichment_candidates(conn)
    by_kind = {c["relation_kind"]: c for c in candidates}
    assert by_kind["mentions_dependency"]["content_hash"] == "matching-hash"
    # The other relationship (mentions_artifact) has no enrichment row yet.
    assert by_kind["mentions_artifact"]["content_hash"] is None
