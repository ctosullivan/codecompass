"""Batched, usage-driven AI enrichment (Phase B) — `codecompass.enrichment`.

Selects vendors for AI enrichment from the SQLite context graph's actual
usage evidence (`graph.enrichment_candidates`), not a per-vendor `Depth`
toggle (`decisions/0031`), and describes several vendors per Anthropic
call instead of one call per vendor. Conceptually replaces
`codecompass.grounded_description`, but that module stays in place and
unmodified through this phase — `sync_vendor` still calls it for
`depth = full` vendors, since `Depth`/`promote` aren't retired until
Phase 15/16 (`decisions/0033`). `_gather_material`/`_find_entry_point`/
`_read_text`/`_first_existing` and the `_call_anthropic` forced-tool-use
pattern below are ported near-verbatim from that module.

**Library only, like Phase 10's `graph.py`** — nothing here is called
from `cli.py`/`sync.py` yet; that wiring is Phase 15. See
architecture/overview.md's "Batched enrichment" section and
planning/phase-14-batched-enrichment.md.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import anthropic

from codecompass import graph
from codecompass.claude_md import read_enrichment_hash, update_description_section
from codecompass.core import Depth, Ecosystem, VendorConfig, VendorDigest
from codecompass.skill import write_cursor_mdc, write_vendor_skill

_MODEL = "claude-haiku-4-5-20251001"
_MAX_TOKENS = 4096
_ESTIMATED_COST_PER_BATCH_USD = 0.02

# Retrieval scope per vendor — same caps `grounded_description.py` uses,
# ported unchanged (Phase 7's Design decisions cover why these numbers).
_RAW_TEXT_CHAR_CAP = 50_000
_DOCS_FILE_CAP = 5

_DEFAULT_BATCH_CHAR_BUDGET = 150_000

_TOOL_NAME = "submit_batched_enrichment"
_TOOL_SCHEMA = {
    "name": _TOOL_NAME,
    "description": (
        "Submit grounded descriptions for every dependency in this batch: "
        "for each vendor, a technical summary for an AI coding agent, a "
        "short conversational overview for a human, a one-line purpose "
        "for each of its used symbols, and an optional pointer to the "
        "single most useful file in that vendor's retrieved material."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "description": (
                    "One result per vendor supplied in this batch — every "
                    "vendor given must appear exactly once."
                ),
                "items": {
                    "type": "object",
                    "properties": {
                        "vendor": {
                            "type": "string",
                            "description": "The vendor name, exactly as given in the material.",
                        },
                        "technical_description": {
                            "type": "string",
                            "description": (
                                "Agent-facing technical description: what this "
                                "dependency does, its core concepts and data model, "
                                "grounded entirely in the retrieved material — cite "
                                "specific files, functions, or classes from what was "
                                "provided, not general knowledge about this dependency."
                            ),
                        },
                        "conversational_overview": {
                            "type": "string",
                            "description": (
                                "A short, casual explanation of what this dependency "
                                "does and why a project might use it — written the way "
                                "you'd explain it to a colleague, not the way you'd "
                                "document it."
                            ),
                        },
                        "symbol_purposes": {
                            "type": "array",
                            "description": (
                                "One entry per symbol listed in this vendor's used "
                                "symbols, describing what that specific symbol is for."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "symbol": {"type": "string"},
                                    "purpose": {"type": "string"},
                                },
                                "required": ["symbol", "purpose"],
                            },
                        },
                        "action_pointer_file": {
                            "type": ["string", "null"],
                            "description": (
                                "Relative path, within this vendor's retrieved "
                                "material, to the single file most worth reading "
                                "next — or null if none stands out."
                            ),
                        },
                        "action_pointer_note": {
                            "type": ["string", "null"],
                            "description": (
                                "A short note on why action_pointer_file is worth "
                                "reading, if action_pointer_file is set."
                            ),
                        },
                    },
                    "required": [
                        "vendor",
                        "technical_description",
                        "conversational_overview",
                        "symbol_purposes",
                    ],
                },
            },
        },
        "required": ["results"],
    },
}

_SYSTEM_PROMPT = (
    "You are describing several software dependencies for a coding project in "
    "one batch, each grounded entirely in material retrieved from its own "
    "actual upstream repository — its README, documentation, and a "
    "representative source file. For each vendor, describe what it does, its "
    "core concepts and data model, and the purpose of each symbol the project "
    "actually uses from it — referencing specific files, functions, or "
    "classes from the retrieved material. Do not describe anything not "
    "grounded in the provided material for that vendor — your own prior "
    "knowledge of these dependencies may be outdated or wrong; the retrieved "
    "material is authoritative. Submit exactly one result per vendor given."
)


class EnrichmentError(Exception):
    """Raised when batched enrichment can't produce a usable result for a
    batch — an Anthropic API failure or an unparseable/incomplete tool-use
    response. Mirrors `GroundedDescriptionError`'s role for the single-call
    module this one replaces.
    """


@dataclass(frozen=True)
class EnrichmentCandidate:
    """One vendor eligible for (re-)enrichment this run — usage-proven
    (`graph.enrichment_candidates`) and not already cached at its current
    symbol set (`select_candidates`'s two-tier hash check).

    `installed_version` isn't in planning/phase-14-batched-enrichment.md's
    field sketch but is carried here anyway: `run_enrichment_batches` needs
    it to compute each `EnrichmentResult.symbol_set_hash` with the *exact*
    same `_compute_symbol_set_hash(vendor_name, sorted(used_symbol_names),
    installed_version)` inputs `select_candidates` used to decide this
    candidate was stale — otherwise the hash written back by `apply_results`
    would never match what a later `select_candidates` call recomputes,
    silently breaking the cache and re-purchasing enrichment every run.
    """

    vendor: VendorConfig
    used_symbol_names: list[str]
    material: str
    installed_version: str


@dataclass(frozen=True)
class EnrichmentResult:
    vendor: str
    technical_description: str
    conversational_overview: str
    symbol_purposes: dict[str, str] = field(default_factory=dict)
    action_pointer_file: str | None = None
    action_pointer_note: str | None = None
    symbol_set_hash: str = ""


def _compute_symbol_set_hash(
    vendor_name: str, sorted_symbol_names: list[str], installed_version: str
) -> str:
    """sha256 over vendor name + installed version + sorted used-symbol
    names — the cache key `decisions/0032` describes: unchanged inputs
    hash the same, so an already-enriched, still-current vendor is skipped
    rather than re-purchased. Uses a separator byte that can't appear in
    any of the inputs (symbol/vendor names, version strings) to avoid two
    different input tuples concatenating to the same string.
    """
    payload = "\x1f".join([vendor_name, installed_version, *sorted_symbol_names])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def select_candidates(
    conn: sqlite3.Connection, configs: list[VendorConfig], project_root: Path
) -> list[EnrichmentCandidate]:
    """Every usage-proven vendor (`graph.enrichment_candidates`) whose
    current used-symbol set hasn't already been enriched — checked two
    ways, per planning/phase-14-batched-enrichment.md's belt-and-suspenders
    design (`decisions/0032`):

    1. DB-level: the freshly-computed hash against
       `vendor_enrichment.symbol_set_hash` (via `graph.enrichment_candidates`).
    2. File-level: the same freshly-computed hash against the committed
       `vendor/<name>/CLAUDE.md`'s `**Enrichment symbol-set hash:**` line
       (`claude_md.read_enrichment_hash`) — the check that still works on a
       fresh clone with no `context-graph.db` at all (gitignored).

    A candidate is skipped if *either* check already matches. `configs`
    supplies each candidate's `Ecosystem`/`Depth` (not derivable from the
    graph, which has no `depth` column — `decisions/0031` hasn't removed
    the field yet) and `project_root` locates both `vendor/<name>/src/`
    (material) and `vendor/<name>/CLAUDE.md` (file-level hash check,
    unconditionally cloned since Phase 13). A vendor with no retrievable
    material (no README/docs/entry-point in its clone) is skipped outright
    — same "nothing to ground the call in" posture
    `generate_grounded_description` enforces by raising, just non-fatal
    here since one ungroundable vendor shouldn't abort an entire batch run.
    """
    configs_by_name = {config.name: config for config in configs}
    candidates: list[EnrichmentCandidate] = []

    for row in graph.enrichment_candidates(conn):
        vendor_name = row["vendor"]
        config = configs_by_name.get(vendor_name)
        if config is None:
            continue  # tracked in the graph but no longer in vendor.toml

        profile = graph.vendor_profile(conn, vendor_name)
        installed_version = (profile["vendor"]["installed_version"] if profile else None) or ""
        used_symbol_names = sorted(row["used_symbols"])
        current_hash = _compute_symbol_set_hash(vendor_name, used_symbol_names, installed_version)

        if row["symbol_set_hash"] == current_hash:
            continue  # DB-level cache hit

        claude_md_path = project_root / "vendor" / vendor_name / "CLAUDE.md"
        if read_enrichment_hash(claude_md_path) == current_hash:
            continue  # file-level cache hit — survives a fresh clone

        repo_root = project_root / "vendor" / vendor_name / "src"
        material = _gather_material(repo_root, config)
        if not material.strip():
            continue  # nothing to ground a description in

        candidates.append(
            EnrichmentCandidate(
                vendor=config,
                used_symbol_names=used_symbol_names,
                material=material,
                installed_version=installed_version,
            )
        )

    return candidates


def plan_batches(
    candidates: list[EnrichmentCandidate], *, batch_char_budget: int = _DEFAULT_BATCH_CHAR_BUDGET
) -> list[list[EnrichmentCandidate]]:
    """Greedily group `candidates` into as few batches as fit under
    `batch_char_budget` total material characters per batch, preserving
    input order. A single candidate whose own material already exceeds the
    budget still gets its own one-candidate batch rather than being split
    or dropped. `batch_char_budget` defaults to a conservative starting
    point — planning/phase-14-batched-enrichment.md flags this as a value
    to tune empirically once Phase 15 makes a real multi-vendor batched
    call reachable to test manually, not a settled constant.
    """
    batches: list[list[EnrichmentCandidate]] = []
    current: list[EnrichmentCandidate] = []
    current_chars = 0

    for candidate in candidates:
        material_chars = len(candidate.material)
        if current and current_chars + material_chars > batch_char_budget:
            batches.append(current)
            current = []
            current_chars = 0
        current.append(candidate)
        current_chars += material_chars

    if current:
        batches.append(current)

    return batches


def run_enrichment_batches(candidates: list[EnrichmentCandidate]) -> list[EnrichmentResult]:
    """Call `_call_anthropic` once per batch from `plan_batches(candidates)`
    (default budget), mapping each batch's response back to its vendors.
    Same forced-tool-use call pattern and per-module monkeypatch test seam
    as `grounded_description._call_anthropic` (decisions/0016) — ported,
    not reinvented.
    """
    results: list[EnrichmentResult] = []
    for batch in plan_batches(candidates):
        response = _call_anthropic(_SYSTEM_PROMPT, _build_batch_user_prompt(batch))
        results.extend(_map_batch_response(batch, response))
    return results


def _build_batch_user_prompt(batch: list[EnrichmentCandidate]) -> str:
    sections = []
    for candidate in batch:
        used_symbols = ", ".join(candidate.used_symbol_names) or (
            "(none proven — vendor-level use only)"
        )
        sections.append(
            f"# Vendor: {candidate.vendor.name} ({candidate.vendor.ecosystem.value})\n\n"
            f"Used symbols: {used_symbols}\n\n"
            f"## Retrieved material\n\n{candidate.material}"
        )
    return "\n\n---\n\n".join(sections)


def _map_batch_response(
    batch: list[EnrichmentCandidate], response: dict
) -> list[EnrichmentResult]:
    try:
        raw_results = response["results"]
    except KeyError as exc:
        raise EnrichmentError(f"Anthropic response missing required field {exc}") from exc

    candidates_by_name = {candidate.vendor.name: candidate for candidate in batch}
    mapped: list[EnrichmentResult] = []

    for raw in raw_results:
        try:
            vendor_name = raw["vendor"]
            technical_description = raw["technical_description"]
            conversational_overview = raw["conversational_overview"]
        except KeyError as exc:
            raise EnrichmentError(f"Anthropic response missing required field {exc}") from exc

        candidate = candidates_by_name.get(vendor_name)
        if candidate is None:
            # The model named a vendor outside this batch — ignore rather
            # than fail the whole batch over one hallucinated/misspelled entry.
            continue

        symbol_purposes = {
            entry["symbol"]: entry["purpose"]
            for entry in raw.get("symbol_purposes") or []
            if "symbol" in entry and "purpose" in entry
        }
        symbol_set_hash = _compute_symbol_set_hash(
            candidate.vendor.name, candidate.used_symbol_names, candidate.installed_version
        )
        mapped.append(
            EnrichmentResult(
                vendor=vendor_name,
                technical_description=technical_description,
                conversational_overview=conversational_overview,
                symbol_purposes=symbol_purposes,
                action_pointer_file=raw.get("action_pointer_file"),
                action_pointer_note=raw.get("action_pointer_note"),
                symbol_set_hash=symbol_set_hash,
            )
        )

    return mapped


def apply_results(
    conn: sqlite3.Connection, project_root: Path, results: list[EnrichmentResult]
) -> None:
    """Persist each result: `graph.record_enrichment` + one
    `graph.record_symbol_enrichment` per resolvable symbol (Phase 10's
    writers, unchanged); `claude_md.update_description_section` to rewrite
    just that vendor's `CLAUDE.md` Description section and enrichment-hash
    line in place, without re-running `sync_vendor`'s full pipeline; then
    `skill.write_vendor_skill`/`write_cursor_mdc` against a **minimal
    `VendorDigest`** populated only with the fields those two render
    functions actually read (`config`, `installed_version`,
    `conversational_overview`, `technical_description`,
    `action_pointer_file`, `action_pointer_note`) — confirmed by reading
    both functions' bodies that neither touches
    `api_surface`/`file_tree`/`dep_tree`/`side_effects`, so leaving those
    at their dataclass defaults is safe. `VendorConfig.depth` has no
    real meaning for this path (`decisions/0031` — enrichment eligibility
    is usage-driven, not depth-driven) and isn't available here (a result
    only carries the vendor's name); it's set to `Depth.FULL` as the
    closest existing label for "this vendor now has a grounded AI
    description," a value `skill.py` never actually reads.
    """
    generated_at = datetime.now(UTC).isoformat()

    for result in results:
        profile = graph.vendor_profile(conn, result.vendor)
        if profile is None:
            continue  # vendor vanished from the graph mid-run; nothing to attach this to

        vendor_row = profile["vendor"]
        graph.record_enrichment(
            conn,
            vendor_row["id"],
            technical_description=result.technical_description,
            conversational_overview=result.conversational_overview,
            action_pointer_file=result.action_pointer_file,
            action_pointer_note=result.action_pointer_note,
            symbol_set_hash=result.symbol_set_hash,
            model=_MODEL,
            generated_at=generated_at,
        )

        symbol_ids_by_name = {symbol["name"]: symbol["id"] for symbol in profile["symbols"]}
        for symbol_name, purpose in result.symbol_purposes.items():
            symbol_id = symbol_ids_by_name.get(symbol_name)
            if symbol_id is None:
                continue  # model described a symbol not actually recorded for this vendor
            graph.record_symbol_enrichment(conn, symbol_id, purpose, generated_at)

        claude_md_path = project_root / "vendor" / result.vendor / "CLAUDE.md"
        update_description_section(
            claude_md_path,
            technical_description=result.technical_description,
            action_pointer_file=result.action_pointer_file,
            action_pointer_note=result.action_pointer_note,
            symbol_set_hash=result.symbol_set_hash,
        )

        minimal_digest = VendorDigest(
            config=VendorConfig(
                name=result.vendor,
                ecosystem=Ecosystem(vendor_row["ecosystem"]),
                depth=Depth.FULL,
            ),
            installed_version=vendor_row["installed_version"] or "",
            conversational_overview=result.conversational_overview,
            technical_description=result.technical_description,
            action_pointer_file=result.action_pointer_file,
            action_pointer_note=result.action_pointer_note,
        )
        write_vendor_skill(project_root, minimal_digest)
        write_cursor_mdc(project_root, minimal_digest)


def _gather_material(repo_root: Path, config: VendorConfig) -> str:
    """README (repo root) + a docs/doc folder if present + one
    ecosystem-typical entry-point file, each section tagged with its
    source path so the model can (and is instructed to) cite it. Total
    capped at `_RAW_TEXT_CHAR_CAP` raw characters — later sections are
    truncated or dropped once the cap is reached, earlier ones (README
    first) are never truncated to make room for later ones. Ported
    near-verbatim from `grounded_description._gather_material`; `repo_root`
    is now always `vendor/<name>/src/` (Phase 13 made that exist for every
    vendor, not just formerly-`depth = full` ones), not a special
    grounded-description-only clone.
    """
    candidates: list[tuple[str, str]] = []

    for readme in sorted(repo_root.glob("README*"))[:1]:
        candidates.append((readme.name, _read_text(readme)))

    for docs_name in ("docs", "doc"):
        docs_dir = repo_root / docs_name
        if docs_dir.is_dir():
            for doc_file in sorted(docs_dir.rglob("*.md"))[:_DOCS_FILE_CAP]:
                rel = doc_file.relative_to(repo_root)
                candidates.append((str(rel), _read_text(doc_file)))
            break

    entry_point = _find_entry_point(repo_root, config)
    if entry_point is not None:
        rel = entry_point.relative_to(repo_root)
        candidates.append((str(rel), _read_text(entry_point)))

    sections = []
    remaining = _RAW_TEXT_CHAR_CAP
    for name, text in candidates:
        if remaining <= 0:
            break
        chunk = text[:remaining]
        sections.append(f"# {name}\n\n{chunk}")
        remaining -= len(chunk)
    return "\n\n".join(sections)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


_NPM_ENTRY_CANDIDATES = ("index.js", "index.ts", "src/index.js", "src/index.ts")
_CARGO_ENTRY_CANDIDATES = ("src/lib.rs", "src/main.rs")


def _find_entry_point(repo_root: Path, config: VendorConfig) -> Path | None:
    """One ecosystem-typical "main module" file, if findable — best
    effort, not exhaustive. Returns `None` rather than guessing when
    nothing matches; the README/docs material still grounds the call.
    Ported unchanged from `grounded_description._find_entry_point`.
    """
    if config.ecosystem is Ecosystem.NPM:
        package_json = repo_root / "package.json"
        if package_json.is_file():
            try:
                data = json.loads(package_json.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                data = {}
            for key in ("main", "module"):
                candidate = data.get(key)
                if candidate and (repo_root / candidate).is_file():
                    return repo_root / candidate
        return _first_existing(repo_root, _NPM_ENTRY_CANDIDATES)
    if config.ecosystem is Ecosystem.PYTHON:
        return _first_existing(
            repo_root, (f"{config.name}/__init__.py", f"src/{config.name}/__init__.py")
        )
    if config.ecosystem is Ecosystem.CARGO:
        return _first_existing(repo_root, _CARGO_ENTRY_CANDIDATES)
    return None


def _first_existing(root: Path, relative_candidates: tuple[str, ...]) -> Path | None:
    for candidate in relative_candidates:
        path = root / candidate
        if path.is_file():
            return path
    return None


def _call_anthropic(system_prompt: str, user_prompt: str) -> dict:
    """Run one forced-tool-use call against `_MODEL`, requesting the
    batched `_TOOL_SCHEMA`. Tests monkeypatch this per-module
    (`codecompass.enrichment._call_anthropic`) to inject a fixed response —
    no test makes a real API call, ever (decisions/0016). Ported unchanged
    in shape from `grounded_description._call_anthropic`, raising
    `EnrichmentError` instead.
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
        raise EnrichmentError(f"Anthropic API call failed: {exc}") from exc

    for block in response.content:
        if block.type == "tool_use":
            return block.input
    raise EnrichmentError("Anthropic response did not include the expected tool call")


def estimate_cost(batch_count: int) -> float:
    """Rough, fixed placeholder estimate — not live-queried pricing, not a
    guarantee of actual billed cost. Reworked from
    `grounded_description.estimate_cost`: cost now scales with the number
    of *batches* (`len(plan_batches(...))`), not 1:1 with vendor count,
    reflecting the real batched call shape — several vendors' material and
    output share one call.
    """
    return batch_count * _ESTIMATED_COST_PER_BATCH_USD


def check_budget(candidates: list[EnrichmentCandidate], budget: float | None) -> None:
    """No-op if `budget` is `None`. Otherwise raises `EnrichmentError`
    *before any API call is made* if this run's projected cost (based on
    how many batches `plan_batches(candidates)` would need) exceeds
    `budget` — the whole run aborts, nothing is written, matching
    `grounded_description.check_budget`'s abort-before-any-spend contract.
    """
    if budget is None:
        return
    batch_count = len(plan_batches(candidates))
    estimated = estimate_cost(batch_count)
    if estimated > budget:
        raise EnrichmentError(
            f"estimated cost ${estimated:.2f} for {batch_count} batch(es) covering "
            f"{len(candidates)} vendor(s) exceeds --budget ${budget:.2f} — raise "
            "--budget or wait for fewer vendors to need enrichment"
        )
