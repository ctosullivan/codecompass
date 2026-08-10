"""AI-gated gap analysis — the only step in depcompass that calls the
Anthropic API. Runs only for `depth = full` vendors with `context_path`
set. See architecture/overview.md's "Gap analysis" section and
decisions/0003.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import anthropic

from depcompass.core import Depth, VendorConfig

_MODEL = "claude-haiku-4-5-20251001"
_MAX_TOKENS = 1024
_CONTEXT_PATH_CHAR_CAP = 8000
_ESTIMATED_COST_PER_CALL_USD = 0.01

_TOOL_NAME = "submit_gap_analysis"
_TOOL_SCHEMA = {
    "name": _TOOL_NAME,
    "description": (
        "Submit the gap analysis for this dependency: a technical summary "
        "for an AI coding agent, a short conversational overview for a "
        "human, and an optional pointer to where in the dependency's own "
        "source this gap is most relevant."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "technical_analysis": {
                "type": "string",
                "description": (
                    "Agent-facing technical analysis: how the project's "
                    "stated needs compare to this dependency's actual API "
                    "surface, and what gaps (if any) exist."
                ),
            },
            "conversational_overview": {
                "type": "string",
                "description": (
                    "A short, casual explanation of what this dependency "
                    "does, why the project uses it, and its risk posture "
                    "— written the way you'd explain it to a colleague, "
                    "not the way you'd document it."
                ),
            },
            "action_pointer_file": {
                "type": ["string", "null"],
                "description": (
                    "Relative path, within the dependency's own source "
                    "tree, to the single most relevant file for the gap "
                    "identified — or null if none stands out."
                ),
            },
            "action_pointer_note": {
                "type": ["string", "null"],
                "description": (
                    "A short note on what to do at action_pointer_file, "
                    "if action_pointer_file is set."
                ),
            },
        },
        "required": ["technical_analysis", "conversational_overview"],
    },
}

_SYSTEM_PROMPT = (
    "You are analyzing a single software dependency for a coding project. "
    "Compare the dependency's public API surface against how the "
    "consuming project describes its own needs, and identify concrete "
    "gaps: missing functionality, version-specific footguns, or API "
    "surface the project doesn't appear to be using correctly. Be concise "
    "and specific — cite actual function/class names from the API "
    "surface, not generic advice."
)


class GapAnalysisError(Exception):
    """Raised when gap-analysis generation can't produce a result —
    missing/unreadable `context_path`, an Anthropic API failure, or an
    unparseable tool-use response.
    """


@dataclass
class GapAnalysis:
    technical: str
    conversational_overview: str
    action_pointer_file: str | None = None
    action_pointer_note: str | None = None


def generate_gap_analysis(
    config: VendorConfig, api_surface: str, project_root: Path
) -> GapAnalysis:
    """Read `context_path`, call the model once via `_call_anthropic`
    (forced tool-use, so both audiences come back in one structured
    response — decisions/0012), and map the result into `GapAnalysis`.
    Raises `GapAnalysisError` on any failure; callers decide how to
    handle it, this function never swallows an error itself.
    """
    if not config.context_path:
        raise GapAnalysisError(
            f"{config.name}: gap analysis requires context_path to be set"
        )
    context_file = project_root / config.context_path
    try:
        context_text = context_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise GapAnalysisError(
            f"{config.name}: could not read context_path {context_file}: {exc}"
        ) from exc
    context_text = context_text[:_CONTEXT_PATH_CHAR_CAP]

    user_prompt = _build_user_prompt(config, api_surface, context_text)
    result = _call_anthropic(_SYSTEM_PROMPT, user_prompt)

    try:
        technical = result["technical_analysis"]
        conversational_overview = result["conversational_overview"]
    except KeyError as exc:
        raise GapAnalysisError(
            f"{config.name}: Anthropic response missing required field {exc}"
        ) from exc

    return GapAnalysis(
        technical=technical,
        conversational_overview=conversational_overview,
        action_pointer_file=result.get("action_pointer_file"),
        action_pointer_note=result.get("action_pointer_note"),
    )


def _build_user_prompt(config: VendorConfig, api_surface: str, context_text: str) -> str:
    return (
        f"Dependency: {config.name} ({config.ecosystem.value})\n\n"
        f"## Public API surface\n\n{api_surface}\n\n"
        f"## Consuming project's own description (from {config.context_path})\n\n"
        f"{context_text}"
    )


def _call_anthropic(system_prompt: str, user_prompt: str) -> dict:
    """Run one forced-tool-use call against `_MODEL`. Tests monkeypatch
    this per-module (`depcompass.gap_analysis._call_anthropic`) to inject
    a fixed response — no test makes a real API call, ever (see the new
    ADR recorded for this phase; unlike Phase 2's free npm/pytest live
    smoke tests, a real call here costs real money and needs a live key).
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
        raise GapAnalysisError(f"Anthropic API call failed: {exc}") from exc

    for block in response.content:
        if block.type == "tool_use":
            return block.input
    raise GapAnalysisError("Anthropic response did not include the expected tool call")


def estimate_cost(vendor_count: int) -> float:
    """Rough, fixed placeholder estimate — not live-queried pricing, not
    a guarantee of actual billed cost. See planning/phase-5-gap-analysis.md's
    Design decisions.
    """
    return vendor_count * _ESTIMATED_COST_PER_CALL_USD


def check_budget(configs: list[VendorConfig], budget: float | None) -> None:
    """No-op if `budget` is `None`. Otherwise, raises `GapAnalysisError`
    *before any API call is made* if this run's projected gap-analysis
    cost exceeds `budget` — the whole run aborts, nothing is written,
    rather than partially processing vendors up to the budget.
    """
    if budget is None:
        return
    pending = sum(1 for c in configs if c.depth is Depth.FULL and c.context_path)
    estimated = estimate_cost(pending)
    if estimated > budget:
        raise GapAnalysisError(
            f"estimated gap-analysis cost ${estimated:.2f} for {pending} vendor(s) "
            f"exceeds --budget ${budget:.2f} — raise --budget or reduce the number "
            "of depth=full vendors with context_path set"
        )
