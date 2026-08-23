"""Batched, usage-driven AI enrichment over spec-doc relationships (Phase
22) — a sibling module to `codecompass.enrichment`, not folded into it (see
planning/phase-22-ai-enriched-cross-artifact-relationships.md's Design
decisions / decisions/0038): a relationship candidate's shape (a doc pair
plus two text excerpts) is different enough from a vendor enrichment
candidate's shape (a vendor plus its used symbols) that sharing one
module's functions would mean threading a type-discriminated candidate
through every function.

Selects candidates from `graph.relation_enrichment_candidates` — every
`doc_relations_edges` row (Phase 21's mechanical spec-doc <-> dependency/
Skill detection) not already cached at its current content hash — and
describes several relationships per Anthropic call, reusing the same
batched forced-tool-use call shape `codecompass.enrichment` established
(client setup, retry-via-`AnthropicError`, per-module monkeypatch test
seam — decisions/0016) rather than reinventing it.

**Non-negotiable boundary** (see the phase plan and decisions/0038): the
AI-generated summary is written only to `doc_relation_enrichment` (the
gitignored graph), never into a spec doc's own file. codecompass reads a
spec doc's text (the same way it already reads a consuming project's own
source for usage detection) but has no write path to one at all —
`apply_results` below never opens a spec-doc path in write mode, and
structurally can't: it doesn't even accept a `project_root`.

Wired into `cli.py`'s `_maybe_run_enrichment`, alongside (not instead of)
the existing vendor/symbol enrichment call, folded into the same disclosed
cost/consent prompt (`enrichment.estimate_cost`/`check_budget`, extended
to fold in this module's candidate/batch counts).
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import anthropic

from codecompass import graph
from codecompass.graph import RELATION_LABELS

_MODEL = "claude-haiku-4-5-20251001"
_MAX_TOKENS = 4096
_DEFAULT_BATCH_CHAR_BUDGET = 150_000

# A few thousand characters of the spec doc's own text — a fixed constant
# to start, tuned from real output quality later, same "start simple"
# posture Phase 14 took for `enrichment._RAW_TEXT_CHAR_CAP`/`_DEFAULT_
# BATCH_CHAR_BUDGET` (the phase plan's Explicitly deferred section: no
# `vendor.toml` configurability yet).
_SPEC_DOC_EXCERPT_CHAR_CAP = 4_000

# Phase 28: when the mechanical mention that produced this candidate
# (`doc_mapping.build_doc_relations_edges`'s word-boundary match) can be
# re-found in the source text, the excerpt centers on it instead of always
# starting at character 0 — otherwise a mention past the first
# `_SPEC_DOC_EXCERPT_CHAR_CAP` characters never actually reaches the model,
# producing a plausible-sounding but ungrounded summary (confirmed against
# this repo's own two `"anthropic README.md"` relationships — see the
# phase plan). Asymmetric before/after split, not a symmetric 2,000/2,000:
# a mention is more often followed by explanatory text (what it does, why
# it's used) than preceded by it, so more of the fixed budget goes after
# the match. Both constants sum to `_SPEC_DOC_EXCERPT_CHAR_CAP` — this
# relocates the window, it doesn't enlarge it. A starting point to retune
# from real output quality later, same posture as `_SPEC_DOC_EXCERPT_CHAR_
# CAP` itself.
_EXCERPT_CHARS_BEFORE_MATCH = 1_000
_EXCERPT_CHARS_AFTER_MATCH = _SPEC_DOC_EXCERPT_CHAR_CAP - _EXCERPT_CHARS_BEFORE_MATCH

_TOOL_NAME = "submit_batched_relation_enrichment"
_TOOL_SCHEMA = {
    "name": _TOOL_NAME,
    "description": (
        "Submit a one-to-two sentence explanation, plus a closed-taxonomy "
        "label, of how each spec-doc excerpt in this batch relates to "
        "what it mentions — a tracked dependency, or another generated "
        "doc artifact."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "description": (
                    "One result per relationship supplied in this batch — "
                    "every relationship given must appear exactly once."
                ),
                "items": {
                    "type": "object",
                    "properties": {
                        "relationship_id": {
                            "type": "string",
                            "description": (
                                "The relationship's id, exactly as given in "
                                "the material — echo it back unchanged."
                            ),
                        },
                        "ai_summary": {
                            "type": "string",
                            "description": (
                                "One or two sentences explaining how the "
                                "spec doc's excerpt relates to what it "
                                "mentions, grounded entirely in the "
                                "material given for that relationship."
                            ),
                        },
                        "relation_label": {
                            "type": "string",
                            "enum": list(RELATION_LABELS),
                            "description": (
                                "The single label from this closed set that "
                                "best characterizes the relationship. Use "
                                "'other' if none of the specific labels fit "
                                "— never invent a label outside this list."
                            ),
                        },
                    },
                    "required": ["relationship_id", "ai_summary", "relation_label"],
                },
            },
        },
        "required": ["results"],
    },
}

_SYSTEM_PROMPT = (
    "You are explaining, in one or two sentences each, how a software "
    "project's own spec documentation relates to something it mechanically "
    "mentions — a tracked dependency or another generated doc artifact — "
    "for several relationships in one batch. Ground each explanation "
    "entirely in the material given for that relationship: the spec doc's "
    "own excerpt and the target's existing description. Do not describe "
    "anything not grounded in the material given — your own prior "
    "knowledge may not match what this specific spec doc actually says. "
    "For each relationship, also pick exactly one relation_label from this "
    "closed set: 'documents_configuration_of' (the excerpt explains how to "
    "configure or set up the target), 'explains_usage_of' (the excerpt "
    "explains how or why the target is used), 'contrasts_with' (the "
    "excerpt compares or distinguishes itself from the target), "
    "'supersedes' (the excerpt states it replaces or deprecates the "
    "target), or 'other' (none of the above cleanly fits — never invent a "
    "new label). Submit exactly one result per relationship given."
)


class RelationEnrichmentError(Exception):
    """Raised when batched relationship enrichment can't produce a usable
    result for a batch — an Anthropic API failure or an unparseable/
    incomplete tool-use response. Mirrors `enrichment.EnrichmentError`'s
    role for that sibling module.
    """


@dataclass(frozen=True)
class RelationEnrichmentCandidate:
    """One spec-doc relationship eligible for (re-)enrichment this run — a
    `doc_relations_edges` row (`graph.relation_enrichment_candidates`)
    whose freshly-computed content hash doesn't match what's already
    cached in `doc_relation_enrichment`. Exactly one of `target_vendor_
    name`/`target_doc_path` is set, mirroring `DocRelationEdgeRow` itself.
    `target_label` is a human-readable name for the target (the vendor
    name, or the doc artifact's path) used to build the prompt.
    """

    source_doc_path: str
    relation_kind: str
    target_vendor_name: str | None
    target_doc_path: str | None
    target_label: str
    target_text: str
    source_excerpt: str
    content_hash: str


@dataclass(frozen=True)
class RelationEnrichmentResult:
    source_doc_path: str
    target_vendor_name: str | None
    target_doc_path: str | None
    ai_summary: str
    content_hash: str
    relation_label: str


def _compute_content_hash(source_text: str, target_text: str) -> str:
    """sha256 over the source spec doc's full text + the target's existing
    digest/description text, joined with a separator byte that can't
    appear in either — the cache key `graph.relation_enrichment_
    candidates`'s returned `content_hash` is diffed against (same shape as
    `enrichment._compute_symbol_set_hash`, different inputs). Hashes the
    *full* source text, not the capped excerpt actually sent to the model,
    so a change outside the excerpt window still invalidates the cache
    even though it wouldn't have changed this run's actual API output.
    """
    payload = "\x1f".join([source_text, target_text])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _lookup_vendor_technical_description(
    conn: sqlite3.Connection, vendor_name: str
) -> str | None:
    """This vendor's `vendor_enrichment.technical_description`, if any.
    `graph.py` has no existing read function returning just this column
    (`vendor_profile` never joins `vendor_enrichment` at all), so this
    queries the table directly — the same precedent `sync._lookup_
    enrichment` already set, rather than stretching an existing function's
    contract to cover a shape it wasn't built for.
    """
    row = conn.execute(
        """
        SELECT ve.technical_description
        FROM vendor_enrichment ve
        JOIN vendors v ON ve.vendor_id = v.id
        WHERE v.name = ?
        """,
        (vendor_name,),
    ).fetchone()
    return row[0] if row is not None else None


def _lookup_doc_artifact_description(conn: sqlite3.Connection, path: str) -> str | None:
    """This doc artifact's own `description` column (a Skill's frontmatter
    description, populated by `skill_scan.scan_skills`) — direct query for
    the same reason `_lookup_vendor_technical_description` above is.
    """
    row = conn.execute(
        "SELECT description FROM doc_artifacts WHERE path = ?", (path,)
    ).fetchone()
    return row[0] if row is not None else None


def _relation_needle(
    relation_kind: str,
    target_vendor_name: str | None,
    target_doc_artifact_name: str | None,
) -> str | None:
    """The exact literal `doc_mapping.build_doc_relations_edges` word-
    boundary-matched to detect this relationship in the first place: the
    target vendor's name for `'mentions_dependency'`, the target doc
    artifact's own `name` field (not its path) for `'mentions_artifact'`.
    Re-deriving it here — rather than persisting the match position from
    Phase 21's detection — is this phase's design decision (see the new
    ADR): `doc_relations_edges` stays a purely mechanical table with no
    concept of "where an as-yet-unenriched candidate's excerpt should
    center."
    """
    if relation_kind == "mentions_dependency":
        return target_vendor_name
    if relation_kind == "mentions_artifact":
        return target_doc_artifact_name
    return None


def _select_source_excerpt(source_text: str, needle: str | None) -> str:
    """The excerpt sent to the model for a relationship's spec-doc side —
    centered on `needle`'s first word-boundary match (`re.search(rf"\\b
    {re.escape(needle)}\\b", source_text)`, the exact same regex shape
    `doc_mapping.build_doc_relations_edges` used to detect this
    relationship), so the model actually sees the sentence/paragraph that
    triggered the match rather than whatever happens to sit in the file's
    opening `_SPEC_DOC_EXCERPT_CHAR_CAP` characters (Phase 28).

    Falls back to the original first-N-characters slice when `needle` is
    `None` or can't be re-found — the file changed between the graph
    rebuild that detected the mention and this call. Expected to be rare
    (the mention was proven to exist as of the last rebuild) but must
    degrade gracefully, not raise.

    Only the *first* match is used, same as `build_doc_relations_edges`
    itself already implicitly does via `re.search` (not `re.finditer`) —
    a relationship with multiple mechanical matches in the same doc isn't
    handled specially here.
    """
    if needle:
        match = re.search(rf"\b{re.escape(needle)}\b", source_text)
        if match is not None:
            start = max(0, match.start() - _EXCERPT_CHARS_BEFORE_MATCH)
            end = match.end() + _EXCERPT_CHARS_AFTER_MATCH
            return source_text[start:end]
    return source_text[:_SPEC_DOC_EXCERPT_CHAR_CAP]


def _select_source_excerpt_from_chunk(source_text: str, start_line: int, end_line: int) -> str:
    """The excerpt sent to the model when the mechanical match has been
    attributed to exactly one heading-scoped chunk (Phase 32,
    `doc_mapping.build_doc_relations_edges`'s per-chunk pass) — that
    chunk's own text directly, in place of Phase 28's needle-re-
    derivation-plus-fixed-window guess. `start_line`/`end_line` are
    1-indexed and inclusive, matching `doc_chunking.DocChunk`'s
    convention. No character cap here: a heading-scoped section is
    already a much tighter unit than `_SPEC_DOC_EXCERPT_CHAR_CAP`'s
    4,000-character window in the common case, and truncating a real
    section arbitrarily would reintroduce the exact "the model doesn't
    see the whole grounding" failure mode Phase 28 fixed.
    """
    lines = source_text.splitlines()
    return "\n".join(lines[start_line - 1 : end_line])


def select_candidates(
    conn: sqlite3.Connection, project_root: Path
) -> list[RelationEnrichmentCandidate]:
    """Every `doc_relations_edges` row (`graph.relation_enrichment_
    candidates`) whose freshly-computed content hash doesn't match what's
    already cached. No file-level fallback cache the way vendor enrichment
    has (the phase plan's Explicitly deferred section): spec docs are
    never written to (see the non-negotiable boundary in this module's
    docstring), so there's no codecompass-owned file to embed a
    cache-hash line into — a fresh clone re-pays for relationship
    enrichment once, accepted for v1.

    A spec doc that's vanished from disk since the last graph rebuild (a
    rename/delete mid-session) is skipped outright, non-fatal — the same
    tolerant posture `enrichment.select_candidates` takes toward a vendor
    with no retrievable material.

    Phase 32: when the candidate's edge has a `chunk_id` (`graph.
    relation_enrichment_candidates`'s `chunk_start_line`/`chunk_end_line`
    both set), the excerpt is that chunk's own text directly (`_select_
    source_excerpt_from_chunk`) — Phase 28's needle-re-derivation-plus-
    fixed-window approach (`_select_source_excerpt`) remains exactly as
    it was, used only as the fallback when there's no chunk to prefer.
    """
    candidates: list[RelationEnrichmentCandidate] = []

    for row in graph.relation_enrichment_candidates(conn):
        source_doc_path = row["source_doc_path"]
        target_vendor_name = row["target_vendor_name"]
        target_doc_path = row["target_doc_path"]
        target_doc_artifact_name = row["target_doc_artifact_name"]

        try:
            source_text = (project_root / source_doc_path).read_text(encoding="utf-8")
        except OSError:
            continue  # spec doc vanished from disk since the graph rebuild

        if target_vendor_name is not None:
            target_label = target_vendor_name
            target_text = _lookup_vendor_technical_description(conn, target_vendor_name) or ""
        else:
            target_label = target_doc_path or ""
            target_text = _lookup_doc_artifact_description(conn, target_doc_path or "") or ""

        content_hash = _compute_content_hash(source_text, target_text)
        if row["content_hash"] == content_hash:
            continue  # cache hit — neither side's grounding text has changed

        relation_kind = row["relation_kind"]
        chunk_start_line = row.get("chunk_start_line")
        chunk_end_line = row.get("chunk_end_line")
        if chunk_start_line is not None and chunk_end_line is not None:
            source_excerpt = _select_source_excerpt_from_chunk(
                source_text, chunk_start_line, chunk_end_line
            )
        else:
            needle = _relation_needle(relation_kind, target_vendor_name, target_doc_artifact_name)
            source_excerpt = _select_source_excerpt(source_text, needle)

        candidates.append(
            RelationEnrichmentCandidate(
                source_doc_path=source_doc_path,
                relation_kind=relation_kind,
                target_vendor_name=target_vendor_name,
                target_doc_path=target_doc_path,
                target_label=target_label,
                target_text=target_text,
                source_excerpt=source_excerpt,
                content_hash=content_hash,
            )
        )

    return candidates


def plan_batches(
    candidates: list[RelationEnrichmentCandidate],
    *,
    batch_char_budget: int = _DEFAULT_BATCH_CHAR_BUDGET,
) -> list[list[RelationEnrichmentCandidate]]:
    """Greedily groups `candidates` into as few batches as fit under
    `batch_char_budget` total (excerpt + target text) characters per
    batch, preserving input order. A single candidate whose own material
    already exceeds the budget still gets its own one-candidate batch
    rather than being split or dropped — identical shape to `enrichment.
    plan_batches`, ported rather than shared since the two operate on
    different candidate types (see this module's docstring).
    """
    batches: list[list[RelationEnrichmentCandidate]] = []
    current: list[RelationEnrichmentCandidate] = []
    current_chars = 0

    for candidate in candidates:
        material_chars = len(candidate.source_excerpt) + len(candidate.target_text)
        if current and current_chars + material_chars > batch_char_budget:
            batches.append(current)
            current = []
            current_chars = 0
        current.append(candidate)
        current_chars += material_chars

    if current:
        batches.append(current)

    return batches


def run_enrichment_batches(
    candidates: list[RelationEnrichmentCandidate],
) -> list[RelationEnrichmentResult]:
    """Call `_call_anthropic` once per batch from `plan_batches(candidates)`
    (default budget), mapping each batch's response back to its
    relationships via the synthetic per-batch `relationship_id` index
    `_build_batch_user_prompt` assigns — safer than matching on an echoed
    doc path/vendor name the way `enrichment.py` does for vendors, since a
    spec-doc path can be long/nested and a small transcription slip would
    silently drop a result rather than just fail to match.
    """
    results: list[RelationEnrichmentResult] = []
    for batch in plan_batches(candidates):
        response = _call_anthropic(_SYSTEM_PROMPT, _build_batch_user_prompt(batch))
        results.extend(_map_batch_response(batch, response))
    return results


def _build_batch_user_prompt(batch: list[RelationEnrichmentCandidate]) -> str:
    sections = []
    for index, candidate in enumerate(batch):
        sections.append(
            f"# Relationship {index}\n\n"
            f"Relationship id: {index}\n\n"
            f"Relation kind: {candidate.relation_kind}\n\n"
            f"Spec doc: {candidate.source_doc_path}\n\n"
            f"## Spec doc excerpt\n\n{candidate.source_excerpt}\n\n"
            f"Target: {candidate.target_label}\n\n"
            f"## Target's existing description\n\n"
            f"{candidate.target_text or '(no existing description)'}"
        )
    return "\n\n---\n\n".join(sections)


def _normalize_relation_label(raw_label: object) -> str:
    """Coerces whatever the model returned for `relation_label` to a value
    in `RELATION_LABELS`, falling back to `'other'` for anything outside
    the closed set (missing, wrong type, or a string the model invented
    despite the schema's `enum` constraint — a forced-tool-use call still
    can't be trusted to always honor an `enum` field). Never raises,
    matching this project's established "never raises, degrades to a
    safe default" posture (`staleness._parse_version`, `skill_scan.
    _extract_scalar`) — an enrichment run over dozens of relationships
    shouldn't fail because one label came back malformed.
    """
    if raw_label in RELATION_LABELS:
        return raw_label  # type: ignore[return-value]
    return "other"


def _map_batch_response(
    batch: list[RelationEnrichmentCandidate], response: dict
) -> list[RelationEnrichmentResult]:
    try:
        raw_results = response["results"]
    except KeyError as exc:
        raise RelationEnrichmentError(
            f"Anthropic response missing required field {exc}"
        ) from exc

    mapped: list[RelationEnrichmentResult] = []
    for raw in raw_results:
        try:
            relationship_id = raw["relationship_id"]
            ai_summary = raw["ai_summary"]
        except KeyError as exc:
            raise RelationEnrichmentError(
                f"Anthropic response missing required field {exc}"
            ) from exc
        relation_label = _normalize_relation_label(raw.get("relation_label"))

        try:
            index = int(relationship_id)
        except (TypeError, ValueError):
            # The model echoed back something that isn't one of the ids it
            # was given — ignore rather than fail the whole batch.
            continue
        if not 0 <= index < len(batch):
            continue

        candidate = batch[index]
        mapped.append(
            RelationEnrichmentResult(
                source_doc_path=candidate.source_doc_path,
                target_vendor_name=candidate.target_vendor_name,
                target_doc_path=candidate.target_doc_path,
                ai_summary=ai_summary,
                content_hash=candidate.content_hash,
                relation_label=relation_label,
            )
        )

    return mapped


def apply_results(conn: sqlite3.Connection, results: list[RelationEnrichmentResult]) -> None:
    """Persist each result via `graph.record_relation_enrichment` — the
    **only** thing this function does. Deliberately takes no `project_
    root` parameter at all: unlike `enrichment.apply_results` (which
    rewrites a vendor's `CLAUDE.md`/Skill/`.mdc` files on disk), there is
    no file-write step here, structurally, not just by convention — this
    function has no filesystem handle to a spec doc to even attempt
    writing to one. This is the concrete mechanism behind this phase's
    non-negotiable boundary: the AI-generated summary is written only to
    `doc_relation_enrichment` (the gitignored graph), never into a spec
    doc's own file (see this module's docstring and decisions/0038).
    """
    generated_at = datetime.now(UTC).isoformat()
    for result in results:
        graph.record_relation_enrichment(
            conn,
            result.source_doc_path,
            result.target_vendor_name,
            result.target_doc_path,
            result.ai_summary,
            result.content_hash,
            _MODEL,
            generated_at,
            relation_label=result.relation_label,
        )


def _call_anthropic(system_prompt: str, user_prompt: str) -> dict:
    """Run one forced-tool-use call against `_MODEL`, requesting the
    batched `_TOOL_SCHEMA`. Ported near-verbatim from `enrichment._call_
    anthropic` — same client setup, same forced-tool-use params, same
    `AnthropicError`-wrapping shape — with its own module-scoped
    `RelationEnrichmentError` in place of `EnrichmentError`. Tests
    monkeypatch this per-module (`codecompass.relation_enrichment._call_
    anthropic`) to inject a fixed response — no test makes a real API
    call, ever (decisions/0016).
    """
    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=_MODEL,
            max_tokens=_MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            tools=[_TOOL_SCHEMA],
            tool_choice={"type": "tool", "name": _TOOL_NAME},
        )
    except anthropic.AnthropicError as exc:
        raise RelationEnrichmentError(f"Anthropic API call failed: {exc}") from exc

    for block in response.content:
        if block.type == "tool_use":
            return block.input
    raise RelationEnrichmentError("Anthropic response did not include the expected tool call")
