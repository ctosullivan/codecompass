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
    assert value == "1"


def test_init_schema_is_idempotent(tmp_path) -> None:
    conn = sqlite3.connect(tmp_path / "context-graph.db")
    init_schema(conn)
    init_schema(conn)  # must not raise
    (value,) = conn.execute(
        "SELECT value FROM meta WHERE key = 'schema_version'"
    ).fetchone()
    assert value == "1"


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
