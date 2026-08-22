from dataclasses import dataclass
from pathlib import Path

import pytest

import codecompass.enrichment as enrichment_module
from codecompass.claude_md import (
    read_enrichment_hash,
    read_installed_version,
    render_vendor_claude_md,
)
from codecompass.core import Ecosystem, VendorConfig, VendorDigest
from codecompass.enrichment import (
    EnrichmentCandidate,
    EnrichmentError,
    EnrichmentResult,
    apply_results,
    check_budget,
    estimate_cost,
    plan_batches,
    run_enrichment_batches,
    select_candidates,
)
from codecompass.graph import (
    SourceFileRow,
    SymbolRow,
    UsesEdgeRow,
    VendorRow,
    open_graph,
    rebuild_deterministic,
    record_enrichment,
)

_SOURCE_FILE = "src/app.ts"
_USED_SYMBOLS = ("convert", "parse")


def _vendor_config(name: str = "turndown", ecosystem: Ecosystem = Ecosystem.NPM) -> VendorConfig:
    return VendorConfig(name=name, ecosystem=ecosystem)


def _seed_graph(
    conn,
    *,
    vendor_name: str = "turndown",
    ecosystem: str = "npm",
    installed_version: str = "7.1.2",
    used_symbols: tuple[str, ...] = _USED_SYMBOLS,
) -> None:
    rebuild_deterministic(
        conn,
        vendors=[
            VendorRow(name=vendor_name, ecosystem=ecosystem, installed_version=installed_version)
        ],
        source_files=[SourceFileRow(path=_SOURCE_FILE)],
        symbols=[SymbolRow(vendor_name=vendor_name, name=s) for s in used_symbols],
        uses_edges=[
            UsesEdgeRow(source_file_path=_SOURCE_FILE, vendor_name=vendor_name, symbol_name=s)
            for s in used_symbols
        ],
        doc_artifacts=[],
        documents_edges=[],
        skill_mentions_edges=[],
        routes_via_edges=[],
        depends_on_edges=[],
    )


def _write_vendor_files(
    project_root: Path,
    config: VendorConfig,
    *,
    installed_version: str = "7.1.2",
    readme_text: str = "Converts HTML to Markdown.",
) -> Path:
    vendor_dir = project_root / "vendor" / config.name
    src_dir = vendor_dir / "src"
    src_dir.mkdir(parents=True)
    (src_dir / "README.md").write_text(readme_text, encoding="utf-8")
    digest = VendorDigest(
        config=config, installed_version=installed_version, api_surface="Some API surface."
    )
    (vendor_dir / "CLAUDE.md").write_text(render_vendor_claude_md(digest), encoding="utf-8")
    return vendor_dir


def _current_hash(
    vendor_name: str = "turndown",
    used_symbols: tuple[str, ...] = _USED_SYMBOLS,
    installed_version: str = "7.1.2",
) -> str:
    return enrichment_module._compute_symbol_set_hash(
        vendor_name, sorted(used_symbols), installed_version
    )


def _candidate(
    name: str,
    material_len: int,
    *,
    used: tuple[str, ...] = ("sym",),
    installed_version: str = "1.0.0",
) -> EnrichmentCandidate:
    return EnrichmentCandidate(
        vendor=_vendor_config(name),
        used_symbol_names=list(used),
        material="x" * material_len,
        installed_version=installed_version,
    )


# --- select_candidates -------------------------------------------------------


def test_select_candidates_returns_usage_proven_vendor(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_graph(conn)
    config = _vendor_config()
    _write_vendor_files(tmp_path, config)

    candidates = select_candidates(conn, [config], tmp_path)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.vendor.name == "turndown"
    assert candidate.used_symbol_names == ["convert", "parse"]
    assert candidate.installed_version == "7.1.2"
    assert "Converts HTML to Markdown." in candidate.material


def test_select_candidates_skips_vendor_not_in_configs(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_graph(conn)
    assert select_candidates(conn, [], tmp_path) == []


def test_select_candidates_skips_vendor_with_no_material(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_graph(conn)
    config = _vendor_config()
    vendor_dir = tmp_path / "vendor" / config.name
    (vendor_dir / "src").mkdir(parents=True)
    digest = VendorDigest(config=config, installed_version="7.1.2")
    (vendor_dir / "CLAUDE.md").write_text(render_vendor_claude_md(digest), encoding="utf-8")

    assert select_candidates(conn, [config], tmp_path) == []


def test_select_candidates_skips_when_db_level_hash_matches(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_graph(conn)
    config = _vendor_config()
    _write_vendor_files(tmp_path, config)

    (vendor_id,) = conn.execute("SELECT id FROM vendors WHERE name = 'turndown'").fetchone()
    record_enrichment(
        conn,
        vendor_id,
        symbol_set_hash=_current_hash(),
        model="claude-haiku-4-5",
        generated_at="2026-01-01T00:00:00+00:00",
    )

    assert select_candidates(conn, [config], tmp_path) == []


def test_select_candidates_skips_when_file_level_hash_matches(tmp_path: Path) -> None:
    """A fresh clone has no `context-graph.db` at all (gitignored,
    decisions/0032) — the file-level check on the committed `CLAUDE.md`
    must be sufficient on its own to skip re-enrichment.
    """
    conn = open_graph(tmp_path)
    _seed_graph(conn)
    config = _vendor_config()
    vendor_dir = _write_vendor_files(tmp_path, config)
    claude_md_path = vendor_dir / "CLAUDE.md"
    content = claude_md_path.read_text(encoding="utf-8")
    content += f"\n- **Enrichment symbol-set hash:** {_current_hash()}\n"
    claude_md_path.write_text(content, encoding="utf-8")

    # No record_enrichment call at all — DB-level hash is still None.
    assert select_candidates(conn, [config], tmp_path) == []


def test_select_candidates_does_not_skip_when_hash_is_stale(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_graph(conn)
    config = _vendor_config()
    _write_vendor_files(tmp_path, config)

    (vendor_id,) = conn.execute("SELECT id FROM vendors WHERE name = 'turndown'").fetchone()
    record_enrichment(
        conn,
        vendor_id,
        symbol_set_hash="stale-hash-from-before-a-new-symbol-was-used",
        model="claude-haiku-4-5",
        generated_at="2026-01-01T00:00:00+00:00",
    )

    assert len(select_candidates(conn, [config], tmp_path)) == 1


def test_select_candidates_empty_after_apply_results(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_graph(conn)
    config = _vendor_config()
    _write_vendor_files(tmp_path, config)

    candidates = select_candidates(conn, [config], tmp_path)
    assert len(candidates) == 1

    result = EnrichmentResult(
        vendor="turndown",
        technical_description="Converts HTML to Markdown.",
        conversational_overview="Handles HTML-to-Markdown conversion.",
        symbol_purposes={},
        symbol_set_hash=_current_hash(),
    )
    apply_results(conn, tmp_path, [result])

    assert select_candidates(conn, [config], tmp_path) == []


# --- plan_batches -------------------------------------------------------------


def test_plan_batches_groups_under_budget_into_one_batch() -> None:
    candidates = [_candidate("a", 40), _candidate("b", 40)]
    assert plan_batches(candidates, batch_char_budget=100) == [candidates]


def test_plan_batches_splits_once_the_budget_would_be_exceeded() -> None:
    candidates = [_candidate("a", 60), _candidate("b", 60)]
    assert plan_batches(candidates, batch_char_budget=100) == [
        [candidates[0]],
        [candidates[1]],
    ]


def test_plan_batches_exact_budget_boundary_stays_in_one_batch() -> None:
    candidates = [_candidate("a", 50), _candidate("b", 50)]
    assert plan_batches(candidates, batch_char_budget=100) == [candidates]


def test_plan_batches_oversized_single_candidate_gets_its_own_batch() -> None:
    candidates = [_candidate("a", 200)]
    assert plan_batches(candidates, batch_char_budget=100) == [[candidates[0]]]


def test_plan_batches_empty_candidates_returns_no_batches() -> None:
    assert plan_batches([], batch_char_budget=100) == []


# --- run_enrichment_batches / _call_anthropic ---------------------------------

_FIXED_BATCH_RESPONSE = {
    "results": [
        {
            "vendor": "turndown",
            "technical_description": "TurndownService converts HTML to Markdown via visitor rules.",
            "conversational_overview": "Handles HTML-to-Markdown conversion.",
            "symbol_purposes": [
                {"symbol": "convert", "purpose": "Runs the conversion."},
                {"symbol": "parse", "purpose": "Parses HTML into a DOM-like tree."},
            ],
            "action_pointer_file": "src/commonmark-rules.js",
            "action_pointer_note": "override fencedCodeBlock here",
        }
    ]
}


def test_run_enrichment_batches_maps_response_to_result(monkeypatch: pytest.MonkeyPatch) -> None:
    candidate = _candidate("turndown", 100, used=_USED_SYMBOLS, installed_version="7.1.2")
    monkeypatch.setattr(
        enrichment_module, "_call_anthropic", lambda *a, **k: dict(_FIXED_BATCH_RESPONSE)
    )

    results = run_enrichment_batches([candidate])

    assert len(results) == 1
    result = results[0]
    assert result.vendor == "turndown"
    assert result.technical_description == (
        "TurndownService converts HTML to Markdown via visitor rules."
    )
    assert result.symbol_purposes == {
        "convert": "Runs the conversion.",
        "parse": "Parses HTML into a DOM-like tree.",
    }
    assert result.action_pointer_file == "src/commonmark-rules.js"
    assert result.symbol_set_hash == _current_hash()


def test_run_enrichment_batches_missing_required_field_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _candidate("turndown", 100)
    monkeypatch.setattr(
        enrichment_module,
        "_call_anthropic",
        lambda *a, **k: {"results": [{"vendor": "turndown", "technical_description": "x"}]},
    )
    with pytest.raises(EnrichmentError, match="missing required field"):
        run_enrichment_batches([candidate])


def test_run_enrichment_batches_missing_results_key_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _candidate("turndown", 100)
    monkeypatch.setattr(enrichment_module, "_call_anthropic", lambda *a, **k: {})
    with pytest.raises(EnrichmentError, match="missing required field"):
        run_enrichment_batches([candidate])


def test_run_enrichment_batches_ignores_vendor_outside_the_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _candidate("turndown", 100)
    response = {
        "results": [
            {
                "vendor": "not-in-this-batch",
                "technical_description": "x",
                "conversational_overview": "y",
                "symbol_purposes": [],
            }
        ]
    }
    monkeypatch.setattr(enrichment_module, "_call_anthropic", lambda *a, **k: dict(response))

    assert run_enrichment_batches([candidate]) == []


@dataclass
class _FakeToolUseBlock:
    input: dict
    type: str = "tool_use"


@dataclass
class _FakeTextBlock:
    text: str
    type: str = "text"


@dataclass
class _FakeResponse:
    content: list


class _FakeMessages:
    def __init__(self, response: object) -> None:
        self._response = response

    def create(self, **kwargs: object) -> object:
        return self._response


class _FakeClient:
    def __init__(self, response: object) -> None:
        self.messages = _FakeMessages(response)


def test_call_anthropic_returns_tool_use_input(monkeypatch: pytest.MonkeyPatch) -> None:
    response = _FakeResponse(content=[_FakeToolUseBlock(input={"results": []})])
    monkeypatch.setattr(enrichment_module.anthropic, "Anthropic", lambda: _FakeClient(response))

    result = enrichment_module._call_anthropic("system", "user")

    assert result == {"results": []}


def test_call_anthropic_raises_if_no_tool_use_block(monkeypatch: pytest.MonkeyPatch) -> None:
    response = _FakeResponse(content=[_FakeTextBlock(text="I refuse to use the tool")])
    monkeypatch.setattr(enrichment_module.anthropic, "Anthropic", lambda: _FakeClient(response))

    with pytest.raises(EnrichmentError, match="did not include the expected tool call"):
        enrichment_module._call_anthropic("system", "user")


def test_call_anthropic_wraps_sdk_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    import anthropic

    class _RaisingClient:
        @property
        def messages(self) -> object:
            raise anthropic.AnthropicError("boom")

    monkeypatch.setattr(enrichment_module.anthropic, "Anthropic", lambda: _RaisingClient())

    with pytest.raises(EnrichmentError, match="Anthropic API call failed"):
        enrichment_module._call_anthropic("system", "user")


# --- _gather_material / _find_entry_point (ported from grounded_description) --


def test_gather_material_includes_readme_docs_and_entry_point(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("readme text", encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / "docs" / "guide.md").write_text("docs text", encoding="utf-8")
    (repo / "index.js").write_text("module.exports = {};", encoding="utf-8")

    material = enrichment_module._gather_material(repo, _vendor_config())

    assert "readme text" in material
    assert "docs text" in material
    assert "module.exports" in material


def test_gather_material_caps_total_raw_text(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(enrichment_module, "_RAW_TEXT_CHAR_CAP", 20)
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("x" * 1000, encoding="utf-8")

    material = enrichment_module._gather_material(repo, _vendor_config())

    assert material.count("x") == 20


def test_find_entry_point_python_prefers_package_init(tmp_path: Path) -> None:
    (tmp_path / "widget").mkdir()
    init_file = tmp_path / "widget" / "__init__.py"
    init_file.write_text("", encoding="utf-8")
    config = VendorConfig(name="widget", ecosystem=Ecosystem.PYTHON)

    assert enrichment_module._find_entry_point(tmp_path, config) == init_file


def test_find_entry_point_cargo_prefers_lib_rs(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    lib_rs = tmp_path / "src" / "lib.rs"
    lib_rs.write_text("", encoding="utf-8")
    config = VendorConfig(name="serde", ecosystem=Ecosystem.CARGO)

    assert enrichment_module._find_entry_point(tmp_path, config) == lib_rs


def test_find_entry_point_returns_none_when_nothing_matches(tmp_path: Path) -> None:
    config = VendorConfig(name="widget", ecosystem=Ecosystem.NPM)
    assert enrichment_module._find_entry_point(tmp_path, config) is None


# --- estimate_cost / check_budget ---------------------------------------------


def test_estimate_cost_scales_with_batch_count() -> None:
    assert estimate_cost(0) == 0
    assert estimate_cost(3) == pytest.approx(3 * enrichment_module._ESTIMATED_COST_PER_BATCH_USD)


def test_check_budget_none_is_noop() -> None:
    check_budget([_candidate("a", 10)], None)  # should not raise


def test_check_budget_scales_with_batch_count_not_candidate_count() -> None:
    # Both candidates fit comfortably in one default-budget batch, so this
    # is one batch's worth of cost, not two vendors' worth.
    candidates = [_candidate("a", 10), _candidate("b", 10)]
    check_budget(candidates, budget=enrichment_module._ESTIMATED_COST_PER_BATCH_USD)


def test_check_budget_over_budget_raises() -> None:
    # Each candidate alone exceeds the default 150_000-char batch budget, so
    # this is two separate batches.
    candidates = [_candidate("a", 200_000), _candidate("b", 200_000)]
    with pytest.raises(EnrichmentError, match="exceeds --budget"):
        check_budget(candidates, budget=0.0)


# --- apply_results -------------------------------------------------------------


def test_apply_results_writes_graph_claude_md_and_skills(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_graph(conn)
    config = _vendor_config()
    vendor_dir = _write_vendor_files(tmp_path, config)
    claude_md_path = vendor_dir / "CLAUDE.md"
    assert "## Description" not in claude_md_path.read_text(encoding="utf-8")

    result = EnrichmentResult(
        vendor="turndown",
        technical_description="TurndownService converts HTML via visitor rules.",
        conversational_overview="Handles HTML-to-Markdown conversion.",
        symbol_purposes={"convert": "Runs the conversion.", "parse": "Parses HTML."},
        action_pointer_file="src/commonmark-rules.js",
        action_pointer_note="override fencedCodeBlock here",
        symbol_set_hash=_current_hash(),
    )

    apply_results(conn, tmp_path, [result])

    (vendor_id,) = conn.execute("SELECT id FROM vendors WHERE name = 'turndown'").fetchone()
    row = conn.execute(
        "SELECT technical_description, symbol_set_hash FROM vendor_enrichment WHERE vendor_id = ?",
        (vendor_id,),
    ).fetchone()
    assert row == ("TurndownService converts HTML via visitor rules.", _current_hash())

    purposes = dict(
        conn.execute(
            """
            SELECT s.name, se.purpose FROM symbol_enrichment se
            JOIN symbols s ON se.symbol_id = s.id
            WHERE s.vendor_id = ?
            """,
            (vendor_id,),
        )
    )
    assert purposes == {"convert": "Runs the conversion.", "parse": "Parses HTML."}

    content = claude_md_path.read_text(encoding="utf-8")
    assert content.count("## Description") == 1
    assert "TurndownService converts HTML via visitor rules." in content
    assert (
        "**Action pointer:** `src/commonmark-rules.js` — override fencedCodeBlock here" in content
    )
    assert read_enrichment_hash(claude_md_path) == _current_hash()
    assert read_installed_version(claude_md_path) == "7.1.2"

    skill_path = tmp_path / ".claude" / "skills" / "codecompass-turndown" / "SKILL.md"
    mdc_path = tmp_path / ".cursor" / "rules" / "codecompass-turndown.mdc"
    assert skill_path.exists()
    assert "TurndownService converts HTML via visitor rules." in skill_path.read_text(
        encoding="utf-8"
    )
    assert mdc_path.exists()
    assert "TurndownService converts HTML via visitor rules." in mdc_path.read_text(
        encoding="utf-8"
    )


def test_apply_results_replaces_an_existing_description_section(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_graph(conn)
    config = _vendor_config()
    vendor_dir = tmp_path / "vendor" / config.name
    (vendor_dir / "src").mkdir(parents=True)
    (vendor_dir / "src" / "README.md").write_text("Converts HTML to Markdown.", encoding="utf-8")
    old_digest = VendorDigest(
        config=config,
        installed_version="7.1.2",
        api_surface="API.",
        technical_description="OLD description.",
    )
    claude_md_path = vendor_dir / "CLAUDE.md"
    claude_md_path.write_text(render_vendor_claude_md(old_digest), encoding="utf-8")

    result = EnrichmentResult(
        vendor="turndown",
        technical_description="NEW description.",
        conversational_overview="overview",
        symbol_purposes={},
        symbol_set_hash=_current_hash(),
    )

    apply_results(conn, tmp_path, [result])

    content = claude_md_path.read_text(encoding="utf-8")
    assert content.count("## Description") == 1
    assert "NEW description." in content
    assert "OLD description." not in content
