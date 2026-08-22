import sqlite3

from codecompass.graph import (
    DependsOnEdgeRow,
    DocArtifactRow,
    DocumentsEdgeRow,
    RoutesViaEdgeRow,
    SkillMentionEdgeRow,
    SourceFileRow,
    SymbolRow,
    UsesEdgeRow,
    VendorRow,
    documented_but_unused,
    enrichment_candidates,
    has_enrichment,
    init_schema,
    open_graph,
    rebuild_deterministic,
    record_enrichment,
    record_symbol_enrichment,
    skills_index,
    symbol_profile,
    unused_vendors,
    used_but_undocumented,
    vendor_profile,
)

_ALL_TABLES = {
    "meta",
    "vendors",
    "source_files",
    "symbols",
    "uses_edges",
    "doc_artifacts",
    "documents_edges",
    "skill_mentions_edges",
    "routes_via_edges",
    "depends_on_edges",
    "vendor_enrichment",
    "symbol_enrichment",
}

_SOURCE_FILE = "src/app.ts"
_CLAUDE_MD_PATH = "vendor/used-lib/CLAUDE.md"
_SKILL_PATH = ".claude/skills/used-lib/SKILL.md"


def _fixture_kwargs() -> dict:
    """2 vendors (one used, one not); the used vendor has three symbols
    covering all three coverage states (fully covered, used-but-
    undocumented, documented-but-unused); one doc artifact documenting two
    of them; one skill routed to the used vendor and mentioning it plus the
    one source file; a depends_on edge from the used vendor to the unused
    one.
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
    assert value == "2"


def test_init_schema_is_idempotent(tmp_path) -> None:
    conn = sqlite3.connect(tmp_path / "context-graph.db")
    init_schema(conn)
    init_schema(conn)  # must not raise
    (value,) = conn.execute(
        "SELECT value FROM meta WHERE key = 'schema_version'"
    ).fetchone()
    assert value == "2"


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
    assert schema_version == "2"

    # Would raise sqlite3.IntegrityError under the pre-migration constraint.
    conn.execute(
        "INSERT INTO doc_artifacts (kind, origin, path) VALUES "
        "('slash_command', 'codecompass_tool', '.claude/commands/discovery.md')"
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
    unused_lib_profile = next(p for p in profiles if p["vendor"] == "unused-lib")
    assert unused_lib_profile["usage_count"] == 0
    assert unused_lib_profile["documenting_artifacts"] == []


def test_symbol_profile_for_nonexistent_symbol_is_empty(tmp_path) -> None:
    conn = open_graph(tmp_path)
    rebuild_deterministic(conn, **_fixture_kwargs())
    assert symbol_profile(conn, "doesNotExist") == []


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
