from dataclasses import dataclass
from pathlib import Path

import pytest

import codecompass.relation_enrichment as relation_enrichment_module
from codecompass.graph import (
    DocArtifactRow,
    DocRelationEdgeRow,
    VendorRow,
    open_graph,
    rebuild_deterministic,
    record_enrichment,
    record_relation_enrichment,
)
from codecompass.relation_enrichment import (
    RelationEnrichmentCandidate,
    RelationEnrichmentError,
    RelationEnrichmentResult,
    apply_results,
    plan_batches,
    run_enrichment_batches,
    select_candidates,
)

_SPEC_DOC_PATH = "README.md"
_SKILL_PATH = ".claude/skills/codecompass-demo/SKILL.md"
_SPEC_DOC_TEXT = "This project uses demo for HTTP calls. See codecompass-demo."


def _seed_relation_graph(
    conn, tmp_path: Path, *, spec_doc_text: str = _SPEC_DOC_TEXT
) -> None:
    (tmp_path / _SPEC_DOC_PATH).write_text(spec_doc_text, encoding="utf-8")
    rebuild_deterministic(
        conn,
        vendors=[VendorRow(name="demo", ecosystem="npm", installed_version="1.0.0")],
        source_files=[],
        symbols=[],
        uses_edges=[],
        doc_artifacts=[
            DocArtifactRow(path=_SPEC_DOC_PATH, kind="spec_doc", origin="project"),
            DocArtifactRow(
                path=_SKILL_PATH,
                kind="skill",
                origin="codecompass_vendor",
                vendor_name="demo",
                name="codecompass-demo",
                description="Knows how to call demo's HTTP client.",
            ),
        ],
        documents_edges=[],
        skill_mentions_edges=[],
        routes_via_edges=[],
        depends_on_edges=[],
        doc_relations_edges=[
            DocRelationEdgeRow(
                source_doc_artifact_path=_SPEC_DOC_PATH,
                relation_kind="mentions_dependency",
                target_vendor_name="demo",
            ),
            DocRelationEdgeRow(
                source_doc_artifact_path=_SPEC_DOC_PATH,
                relation_kind="mentions_artifact",
                target_doc_artifact_path=_SKILL_PATH,
            ),
        ],
    )


# --- select_candidates -------------------------------------------------------


def test_select_candidates_returns_both_relation_kinds(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path)

    candidates = select_candidates(conn, tmp_path)

    assert len(candidates) == 2
    by_kind = {c.relation_kind: c for c in candidates}
    assert by_kind["mentions_dependency"].target_vendor_name == "demo"
    assert by_kind["mentions_dependency"].target_doc_path is None
    assert "demo for HTTP calls" in by_kind["mentions_dependency"].source_excerpt
    assert by_kind["mentions_artifact"].target_doc_path == _SKILL_PATH
    assert by_kind["mentions_artifact"].target_text == "Knows how to call demo's HTTP client."


def test_select_candidates_uses_vendor_technical_description_as_target_text(
    tmp_path: Path,
) -> None:
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path)
    (vendor_id,) = conn.execute("SELECT id FROM vendors WHERE name = 'demo'").fetchone()
    record_enrichment(
        conn,
        vendor_id,
        technical_description="demo is a minimal HTTP client.",
        symbol_set_hash="irrelevant-to-this-test",
        model="claude-haiku-4-5",
        generated_at="2026-01-01T00:00:00+00:00",
    )

    candidates = select_candidates(conn, tmp_path)

    dependency_candidate = next(c for c in candidates if c.relation_kind == "mentions_dependency")
    assert dependency_candidate.target_text == "demo is a minimal HTTP client."


def test_select_candidates_target_text_empty_when_nothing_enriched_yet(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path)

    candidates = select_candidates(conn, tmp_path)

    dependency_candidate = next(c for c in candidates if c.relation_kind == "mentions_dependency")
    assert dependency_candidate.target_text == ""


def test_select_candidates_skips_when_content_hash_matches(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path)
    candidates = select_candidates(conn, tmp_path)
    dependency_candidate = next(c for c in candidates if c.relation_kind == "mentions_dependency")

    record_relation_enrichment(
        conn,
        dependency_candidate.source_doc_path,
        dependency_candidate.target_vendor_name,
        dependency_candidate.target_doc_path,
        "already enriched",
        dependency_candidate.content_hash,
        "claude-haiku-4-5-20251001",
        "2026-01-01T00:00:00+00:00",
    )

    remaining = select_candidates(conn, tmp_path)
    assert {c.relation_kind for c in remaining} == {"mentions_artifact"}


def test_select_candidates_does_not_skip_when_content_hash_is_stale(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path)
    candidates = select_candidates(conn, tmp_path)
    dependency_candidate = next(c for c in candidates if c.relation_kind == "mentions_dependency")

    record_relation_enrichment(
        conn,
        dependency_candidate.source_doc_path,
        dependency_candidate.target_vendor_name,
        dependency_candidate.target_doc_path,
        "stale summary",
        "stale-hash-from-before-the-doc-changed",
        "claude-haiku-4-5-20251001",
        "2026-01-01T00:00:00+00:00",
    )

    remaining = select_candidates(conn, tmp_path)
    assert {c.relation_kind for c in remaining} == {"mentions_dependency", "mentions_artifact"}


def test_select_candidates_empty_after_apply_results(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path)
    candidates = select_candidates(conn, tmp_path)
    assert len(candidates) == 2

    results = [
        RelationEnrichmentResult(
            source_doc_path=c.source_doc_path,
            target_vendor_name=c.target_vendor_name,
            target_doc_path=c.target_doc_path,
            ai_summary="a generated summary",
            content_hash=c.content_hash,
            relation_label="explains_usage_of",
        )
        for c in candidates
    ]
    apply_results(conn, results)

    assert select_candidates(conn, tmp_path) == []


def test_select_candidates_skips_spec_doc_missing_from_disk(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path)
    (tmp_path / _SPEC_DOC_PATH).unlink()

    assert select_candidates(conn, tmp_path) == []


# --- select_candidates: excerpt centering (Phase 28) -------------------------

# Padding with no "demo"/"codecompass-demo" substring, well past
# `_SPEC_DOC_EXCERPT_CHAR_CAP` (4,000) — reproduces the exact scenario the
# phase plan found in this repo's own graph: a mechanical mention sitting
# well after the file's opening window.
_PADDING = "filler content far from the mention. " * 150
assert len(_PADDING) > relation_enrichment_module._SPEC_DOC_EXCERPT_CHAR_CAP


def test_select_candidates_excerpt_centers_on_dependency_match_past_the_cap(
    tmp_path: Path,
) -> None:
    spec_doc_text = (
        _PADDING + "The demo library powers HTTP calls in this project. " + "more " * 50
    )
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path, spec_doc_text=spec_doc_text)

    candidates = select_candidates(conn, tmp_path)

    dependency_candidate = next(c for c in candidates if c.relation_kind == "mentions_dependency")
    assert "demo library powers HTTP calls" in dependency_candidate.source_excerpt
    # Not just the file's opening window -- that window never mentions
    # "demo" at all, which is the whole bug this phase fixes.
    assert "demo" not in spec_doc_text[: relation_enrichment_module._SPEC_DOC_EXCERPT_CHAR_CAP]


def test_select_candidates_excerpt_centers_on_artifact_match_past_the_cap(
    tmp_path: Path,
) -> None:
    spec_doc_text = (
        _PADDING
        + "See codecompass-demo for details on the HTTP client wiring. "
        + "more " * 50
    )
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path, spec_doc_text=spec_doc_text)

    candidates = select_candidates(conn, tmp_path)

    artifact_candidate = next(c for c in candidates if c.relation_kind == "mentions_artifact")
    assert "codecompass-demo for details" in artifact_candidate.source_excerpt
    assert (
        "codecompass-demo"
        not in spec_doc_text[: relation_enrichment_module._SPEC_DOC_EXCERPT_CHAR_CAP]
    )


def test_select_candidates_excerpt_falls_back_when_needle_not_found(tmp_path: Path) -> None:
    """A relationship whose needle can't be re-found in the current source
    text (the file changed since the graph rebuild that detected it, an
    edge case the phase plan calls out explicitly) degrades gracefully to
    the original first-N-characters excerpt instead of raising.
    """
    spec_doc_text = "This document no longer mentions either target by name."
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path, spec_doc_text=spec_doc_text)

    candidates = select_candidates(conn, tmp_path)

    assert len(candidates) == 2
    for candidate in candidates:
        assert candidate.source_excerpt == (
            spec_doc_text[: relation_enrichment_module._SPEC_DOC_EXCERPT_CHAR_CAP]
        )


def test_select_candidates_excerpt_unchanged_when_match_already_near_the_start(
    tmp_path: Path,
) -> None:
    """Regression: a needle that already sits within the first
    `_SPEC_DOC_EXCERPT_CHAR_CAP` characters still produces an excerpt
    containing it -- centering must not break the already-working case.
    """
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path)  # default _SPEC_DOC_TEXT, mention near byte 0

    candidates = select_candidates(conn, tmp_path)

    by_kind = {c.relation_kind: c for c in candidates}
    assert "demo for HTTP calls" in by_kind["mentions_dependency"].source_excerpt
    assert "codecompass-demo" in by_kind["mentions_artifact"].source_excerpt


# --- plan_batches -------------------------------------------------------------


def _candidate(
    source_excerpt_len: int, target_text_len: int = 0, **overrides
) -> RelationEnrichmentCandidate:
    defaults = {
        "source_doc_path": "README.md",
        "relation_kind": "mentions_dependency",
        "target_vendor_name": "demo",
        "target_doc_path": None,
        "target_label": "demo",
        "target_text": "x" * target_text_len,
        "source_excerpt": "x" * source_excerpt_len,
        "content_hash": "hash",
    }
    defaults.update(overrides)
    return RelationEnrichmentCandidate(**defaults)


def test_plan_batches_groups_under_budget_into_one_batch() -> None:
    candidates = [_candidate(40), _candidate(40)]
    assert plan_batches(candidates, batch_char_budget=100) == [candidates]


def test_plan_batches_splits_once_the_budget_would_be_exceeded() -> None:
    candidates = [_candidate(60), _candidate(60)]
    assert plan_batches(candidates, batch_char_budget=100) == [
        [candidates[0]],
        [candidates[1]],
    ]


def test_plan_batches_exact_budget_boundary_stays_in_one_batch() -> None:
    candidates = [_candidate(50), _candidate(50)]
    assert plan_batches(candidates, batch_char_budget=100) == [candidates]


def test_plan_batches_oversized_single_candidate_gets_its_own_batch() -> None:
    candidates = [_candidate(200)]
    assert plan_batches(candidates, batch_char_budget=100) == [[candidates[0]]]


def test_plan_batches_empty_candidates_returns_no_batches() -> None:
    assert plan_batches([], batch_char_budget=100) == []


def test_plan_batches_accounts_for_target_text_too() -> None:
    # 60 excerpt chars + 60 target-text chars = 120, over a 100 budget —
    # material_chars must include target_text, not just source_excerpt.
    candidates = [_candidate(60, 60), _candidate(10, 10)]
    assert plan_batches(candidates, batch_char_budget=100) == [
        [candidates[0]],
        [candidates[1]],
    ]


# --- run_enrichment_batches / _call_anthropic ---------------------------------

_FIXED_BATCH_RESPONSE = {
    "results": [
        {
            "relationship_id": "0",
            "ai_summary": "This README explains why demo is used for HTTP calls.",
        }
    ]
}


def test_run_enrichment_batches_maps_response_to_result(monkeypatch: pytest.MonkeyPatch) -> None:
    candidate = _candidate(40)
    monkeypatch.setattr(
        relation_enrichment_module, "_call_anthropic", lambda *a, **k: dict(_FIXED_BATCH_RESPONSE)
    )

    results = run_enrichment_batches([candidate])

    assert len(results) == 1
    result = results[0]
    assert result.source_doc_path == candidate.source_doc_path
    assert result.target_vendor_name == candidate.target_vendor_name
    assert result.target_doc_path == candidate.target_doc_path
    assert result.ai_summary == "This README explains why demo is used for HTTP calls."
    assert result.content_hash == candidate.content_hash
    # No `relation_label` key in _FIXED_BATCH_RESPONSE — never raises,
    # falls back to "other" (Phase 31).
    assert result.relation_label == "other"


def test_run_enrichment_batches_maps_valid_relation_label(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _candidate(40)
    response = {
        "results": [
            {
                "relationship_id": "0",
                "ai_summary": "x",
                "relation_label": "explains_usage_of",
            }
        ]
    }
    monkeypatch.setattr(
        relation_enrichment_module, "_call_anthropic", lambda *a, **k: dict(response)
    )

    results = run_enrichment_batches([candidate])

    assert results[0].relation_label == "explains_usage_of"


def test_run_enrichment_batches_falls_back_to_other_for_adversarial_label(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Phase 31 verification: a label the model invents despite the tool
    # schema's `enum` constraint must never raise — forced tool use still
    # can't be fully trusted to honor `enum`.
    candidate = _candidate(40)
    response = {
        "results": [
            {
                "relationship_id": "0",
                "ai_summary": "x",
                "relation_label": "definitely_not_a_real_label",
            }
        ]
    }
    monkeypatch.setattr(
        relation_enrichment_module, "_call_anthropic", lambda *a, **k: dict(response)
    )

    results = run_enrichment_batches([candidate])

    assert results[0].relation_label == "other"


def test_run_enrichment_batches_missing_required_field_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _candidate(40)
    monkeypatch.setattr(
        relation_enrichment_module,
        "_call_anthropic",
        lambda *a, **k: {"results": [{"relationship_id": "0"}]},
    )
    with pytest.raises(RelationEnrichmentError, match="missing required field"):
        run_enrichment_batches([candidate])


def test_run_enrichment_batches_missing_results_key_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _candidate(40)
    monkeypatch.setattr(relation_enrichment_module, "_call_anthropic", lambda *a, **k: {})
    with pytest.raises(RelationEnrichmentError, match="missing required field"):
        run_enrichment_batches([candidate])


def test_run_enrichment_batches_ignores_id_outside_the_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _candidate(40)
    response = {"results": [{"relationship_id": "5", "ai_summary": "x"}]}
    monkeypatch.setattr(
        relation_enrichment_module, "_call_anthropic", lambda *a, **k: dict(response)
    )

    assert run_enrichment_batches([candidate]) == []


def test_run_enrichment_batches_ignores_non_integer_id(monkeypatch: pytest.MonkeyPatch) -> None:
    candidate = _candidate(40)
    response = {"results": [{"relationship_id": "not-a-number", "ai_summary": "x"}]}
    monkeypatch.setattr(
        relation_enrichment_module, "_call_anthropic", lambda *a, **k: dict(response)
    )

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
    monkeypatch.setattr(
        relation_enrichment_module.anthropic, "Anthropic", lambda: _FakeClient(response)
    )

    result = relation_enrichment_module._call_anthropic("system", "user")

    assert result == {"results": []}


def test_call_anthropic_raises_if_no_tool_use_block(monkeypatch: pytest.MonkeyPatch) -> None:
    response = _FakeResponse(content=[_FakeTextBlock(text="I refuse to use the tool")])
    monkeypatch.setattr(
        relation_enrichment_module.anthropic, "Anthropic", lambda: _FakeClient(response)
    )

    with pytest.raises(RelationEnrichmentError, match="did not include the expected tool call"):
        relation_enrichment_module._call_anthropic("system", "user")


def test_call_anthropic_wraps_sdk_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    import anthropic

    class _RaisingClient:
        @property
        def messages(self) -> object:
            raise anthropic.AnthropicError("boom")

    monkeypatch.setattr(
        relation_enrichment_module.anthropic, "Anthropic", lambda: _RaisingClient()
    )

    with pytest.raises(RelationEnrichmentError, match="Anthropic API call failed"):
        relation_enrichment_module._call_anthropic("system", "user")


# --- apply_results -------------------------------------------------------------


def test_apply_results_writes_doc_relation_enrichment_row(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path)

    result = RelationEnrichmentResult(
        source_doc_path=_SPEC_DOC_PATH,
        target_vendor_name="demo",
        target_doc_path=None,
        ai_summary="This README explains why demo is used.",
        content_hash="hash-1",
        relation_label="explains_usage_of",
    )

    apply_results(conn, [result])

    row = conn.execute(
        "SELECT ai_summary, content_hash, model, relation_label FROM doc_relation_enrichment "
        "WHERE source_doc_path = ? AND target_vendor_name = ?",
        (_SPEC_DOC_PATH, "demo"),
    ).fetchone()
    assert row == (
        "This README explains why demo is used.",
        "hash-1",
        relation_enrichment_module._MODEL,
        "explains_usage_of",
    )


def test_apply_results_never_writes_any_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Structural regression for this phase's non-negotiable boundary: the
    AI-generated summary is written only to `doc_relation_enrichment` (the
    gitignored graph), never into a spec doc's own file — codecompass has
    no write path to a spec doc at all. `apply_results` doesn't even
    accept a `project_root`, so it has no filesystem handle to write
    through in the first place; this test proves that structurally, not
    just by convention: `Path.write_text`/`Path.open` in a write mode both
    raise if called at all during `apply_results`.
    """
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path)

    def _raise_write_text(self: Path, *a: object, **k: object) -> None:
        raise AssertionError(f"apply_results must never write a file, tried: {self}")

    real_open = Path.open

    def _guarded_open(self: Path, mode: str = "r", *a: object, **k: object) -> object:
        if any(flag in mode for flag in ("w", "a", "x", "+")):
            raise AssertionError(f"apply_results must never open a file for writing: {self}")
        return real_open(self, mode, *a, **k)

    monkeypatch.setattr(Path, "write_text", _raise_write_text)
    monkeypatch.setattr(Path, "open", _guarded_open)

    result = RelationEnrichmentResult(
        source_doc_path=_SPEC_DOC_PATH,
        target_vendor_name="demo",
        target_doc_path=None,
        ai_summary="A generated summary.",
        content_hash="hash-1",
        relation_label="explains_usage_of",
    )

    apply_results(conn, [result])  # must not raise

    row = conn.execute(
        "SELECT ai_summary FROM doc_relation_enrichment WHERE source_doc_path = ?",
        (_SPEC_DOC_PATH,),
    ).fetchone()
    assert row == ("A generated summary.",)


def test_apply_results_leaves_spec_doc_file_byte_identical(tmp_path: Path) -> None:
    """The concrete, file-level proof of the same boundary: a spec doc's
    content and mtime are untouched after `apply_results` runs.
    """
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path)
    spec_doc_path = tmp_path / _SPEC_DOC_PATH
    original_content = spec_doc_path.read_text(encoding="utf-8")
    original_mtime_ns = spec_doc_path.stat().st_mtime_ns

    result = RelationEnrichmentResult(
        source_doc_path=_SPEC_DOC_PATH,
        target_vendor_name="demo",
        target_doc_path=None,
        ai_summary="A generated summary.",
        content_hash="hash-1",
        relation_label="explains_usage_of",
    )
    apply_results(conn, [result])

    assert spec_doc_path.read_text(encoding="utf-8") == original_content
    assert spec_doc_path.stat().st_mtime_ns == original_mtime_ns


def test_apply_results_updates_in_place_on_second_call(tmp_path: Path) -> None:
    conn = open_graph(tmp_path)
    _seed_relation_graph(conn, tmp_path)

    apply_results(
        conn,
        [
            RelationEnrichmentResult(
                source_doc_path=_SPEC_DOC_PATH,
                target_vendor_name="demo",
                target_doc_path=None,
                ai_summary="first summary",
                content_hash="hash-1",
                relation_label="explains_usage_of",
            )
        ],
    )
    apply_results(
        conn,
        [
            RelationEnrichmentResult(
                source_doc_path=_SPEC_DOC_PATH,
                target_vendor_name="demo",
                target_doc_path=None,
                ai_summary="second summary",
                content_hash="hash-2",
                relation_label="contrasts_with",
            )
        ],
    )

    rows = conn.execute(
        "SELECT ai_summary FROM doc_relation_enrichment "
        "WHERE source_doc_path = ? AND target_vendor_name = 'demo'",
        (_SPEC_DOC_PATH,),
    ).fetchall()
    assert rows == [("second summary",)]
