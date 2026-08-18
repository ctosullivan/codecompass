"""Grounded-description generation — the only step in codecompass that
calls the Anthropic API. Runs for every `depth = full` vendor. Replaces
Phase 5's `context_path`-gated gap analysis (decisions/0019): instead of
comparing a vendor's API surface against a project-supplied README/spec,
this describes the vendor entirely from material retrieved from its own
upstream repository (decisions/0021's `source_resolution`), unconditionally.
See architecture/overview.md's "Grounded description" section and
decisions/0003 (model tier, unaffected by this replacement) and
decisions/0016 (test strategy, unaffected).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import anthropic

from codecompass.core import Depth, Ecosystem, VendorConfig

_MODEL = "claude-haiku-4-5-20251001"
_MAX_TOKENS = 1024
_ESTIMATED_COST_PER_CALL_USD = 0.01

# Retrieval scope (decisions/0019, confirmed at Phase 7 implementation
# time): README + a docs/doc folder if present + one ecosystem-typical
# entry-point file, capped well under Haiku's context window — so a
# single call suffices, no multi-call chunking loop is needed.
_RAW_TEXT_CHAR_CAP = 50_000
_DOCS_FILE_CAP = 5

_TOOL_NAME = "submit_grounded_description"
_TOOL_SCHEMA = {
    "name": _TOOL_NAME,
    "description": (
        "Submit the grounded description for this dependency: a technical "
        "summary for an AI coding agent, a short conversational overview "
        "for a human, and an optional pointer to the single most useful "
        "file in the retrieved material for understanding this dependency "
        "further."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "technical_analysis": {
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
            "action_pointer_file": {
                "type": ["string", "null"],
                "description": (
                    "Relative path, within the retrieved material, to the "
                    "single file most worth reading next to understand this "
                    "dependency further — or null if none stands out."
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
        "required": ["technical_analysis", "conversational_overview"],
    },
}

_SYSTEM_PROMPT = (
    "You are describing a single software dependency for a coding project, "
    "grounded entirely in material retrieved from its actual upstream "
    "repository — its README, documentation, and a representative source "
    "file. Describe what this dependency does, its core concepts and data "
    "model, and reference specific files, functions, or classes from the "
    "retrieved material. Do not describe anything not grounded in the "
    "provided material — your own prior knowledge of this dependency may "
    "be outdated or wrong; the retrieved material is authoritative."
)


class GroundedDescriptionError(Exception):
    """Raised when grounded-description generation can't produce a result
    — no retrievable material in the cloned repository, an Anthropic API
    failure, or an unparseable tool-use response.
    """


@dataclass
class GroundedDescription:
    technical: str
    conversational_overview: str
    action_pointer_file: str | None = None
    action_pointer_note: str | None = None


def generate_grounded_description(config: VendorConfig, repo_root: Path) -> GroundedDescription:
    """Gather retrieval material from `repo_root` (an already-cloned
    upstream repository — see `codecompass.source_resolution`), call the
    model once via `_call_anthropic` (forced tool-use, so both audiences
    come back in one structured response — decisions/0012), and map the
    result into `GroundedDescription`. Raises `GroundedDescriptionError`
    on any failure; callers decide how to handle it, this function never
    swallows an error itself.
    """
    material = _gather_material(repo_root, config)
    if not material.strip():
        raise GroundedDescriptionError(
            f"{config.name}: no README, docs, or entry-point file found "
            f"in the cloned repository at {repo_root}"
        )

    user_prompt = _build_user_prompt(config, material)
    result = _call_anthropic(_SYSTEM_PROMPT, user_prompt)

    try:
        technical = result["technical_analysis"]
        conversational_overview = result["conversational_overview"]
    except KeyError as exc:
        raise GroundedDescriptionError(
            f"{config.name}: Anthropic response missing required field {exc}"
        ) from exc

    return GroundedDescription(
        technical=technical,
        conversational_overview=conversational_overview,
        action_pointer_file=result.get("action_pointer_file"),
        action_pointer_note=result.get("action_pointer_note"),
    )


def _gather_material(repo_root: Path, config: VendorConfig) -> str:
    """README (repo root) + a docs/doc folder if present + one
    ecosystem-typical entry-point file, each section tagged with its
    source path so the model can (and is instructed to) cite it. Total
    capped at `_RAW_TEXT_CHAR_CAP` raw characters — later sections are
    truncated or dropped once the cap is reached, earlier ones (README
    first) are never truncated to make room for later ones.
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


def _build_user_prompt(config: VendorConfig, material: str) -> str:
    return (
        f"Dependency: {config.name} ({config.ecosystem.value})\n\n"
        f"## Retrieved material\n\n{material}"
    )


def _call_anthropic(system_prompt: str, user_prompt: str) -> dict:
    """Run one forced-tool-use call against `_MODEL`. Tests monkeypatch
    this per-module (`codecompass.grounded_description._call_anthropic`)
    to inject a fixed response — no test makes a real API call, ever
    (decisions/0016).
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
        raise GroundedDescriptionError(f"Anthropic API call failed: {exc}") from exc

    for block in response.content:
        if block.type == "tool_use":
            return block.input
    raise GroundedDescriptionError("Anthropic response did not include the expected tool call")


def estimate_cost(vendor_count: int) -> float:
    """Rough, fixed placeholder estimate — not live-queried pricing, not
    a guarantee of actual billed cost. See planning/phase-5-gap-analysis.md's
    Design decisions (carried forward unchanged into Phase 7).
    """
    return vendor_count * _ESTIMATED_COST_PER_CALL_USD


def check_budget(configs: list[VendorConfig], budget: float | None) -> None:
    """No-op if `budget` is `None`. Otherwise, raises
    `GroundedDescriptionError` *before any API call is made* if this
    run's projected cost exceeds `budget` — the whole run aborts,
    nothing is written, rather than partially processing vendors up to
    the budget. Every `depth = full` vendor counts now — unlike Phase
    5's gap analysis, generation is unconditional, no longer gated on a
    `context_path` field (removed — decisions/0019).
    """
    if budget is None:
        return
    pending = sum(1 for c in configs if c.depth is Depth.FULL)
    estimated = estimate_cost(pending)
    if estimated > budget:
        raise GroundedDescriptionError(
            f"estimated cost ${estimated:.2f} for {pending} vendor(s) "
            f"exceeds --budget ${budget:.2f} — raise --budget or reduce the "
            "number of depth=full vendors"
        )
