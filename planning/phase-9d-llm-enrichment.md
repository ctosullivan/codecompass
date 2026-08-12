# Phase 9d: Context graph — optional LLM enrichment

## Scope

**Covered:**
- New `src/depcompass/enrichment.py` — every 9d LLM-calling function
  lives here, each following `grounded_description`'s exact
  forced-tool-use pattern (`_TOOL_SCHEMA` + `tool_choice` forced to that
  tool + dict read-back from the `tool_use` content block) — never
  `chat.py`'s freeform multi-turn loop, per `decisions/0026`:
  - `DocChunkNode(id, doc_artifact, heading, text)` in
    `context_graph.py` — deterministic, heading-level split of each
    `DocArtifact`'s body. Non-AI, a 9d prerequisite built first.
  - `generate_explains_edges(doc_artifact, chunks, symbols) ->
    list[ExplainsEdge]` — one forced-tool-use call **per doc artifact**
    (not per chunk), mapping its chunks to the symbols they actually
    explain and carrying the real excerpt (`decisions/0027` — this data
    is for a future Phase 10 consumer; `chat.py` is untouched).
  - `generate_usage_purpose_labels(symbol, files) -> str` — batched
    per symbol-per-file, not per call site (cost scales with graph
    nodes, not project size, per `decisions/0026`).
  - `generate_concept_clusters(vendor, symbols) -> list[Cluster]` — one
    call per vendor.
  - `generate_documentation_quality_delta(doc_artifact, symbols) -> ...`
    — reuses the same forced-tool-use shape as `grounded_description`,
    per `decisions/0026`.
  - `generate_file_role_summary(source_file, uses_edges) -> str`.
  - `generate_trigger_accuracy_proxy(symbol, skill_description) ->
    ProxyResult` — a battery of generated questions per heavily-used
    symbol, self-judged for plausible routing. **Explicit interim
    stopgap for `decisions/0013`'s Consequences item, not a resolution
    of it** — stated in the module docstring, not just this plan file.
  - `_call_anthropic(...)` — the single seam every function above
    routes through, matching `grounded_description._call_anthropic`'s
    shape.
  - All of the above gated by a threshold (e.g. `depth = full` vendors
    only, or a usage-count floor) — nothing enriched unconditionally.
- `src/depcompass/context_graph.py` — `enrichment` key populated with
  the above outputs; `null`/absent when 9d hasn't run.
- `src/depcompass/cli.py` — new `depcompass graph --enrich [--budget X]`
  command/flag: cost-disclosed, confirms unless `--yes` (mirrors
  `promote`'s pattern per `decisions/0026` — enrichment is the action
  being confirmed, not a side effect of another one). Bare
  `depcompass graph` (no `--enrich`) runs 9a–9c's deterministic build
  and writes `context-graph.json` with no API key required.
- Tests: `tests/test_enrichment.py` (new) — the two-tier monkeypatch
  pattern `decisions/0016` establishes and `tests/test_chat.py`/
  `tests/test_grounded_description.py` already use: per-function
  `_call_anthropic` monkeypatch for logic tests, plus a fake
  `anthropic.Anthropic` client for the seam's own SDK-interaction tests.
  No test makes a live API call.

**Explicitly deferred:**
- Usage-cluster classification + draft Skill suggestion — Phase 9e,
  `decisions/0028`. Not part of this pass, on purpose (see that ADR's
  Context section for the risk-asymmetry reasoning).
- Any retrofit of `chat <vendor>`'s grounding mechanism —
  `decisions/0027`; `chat.py` is not touched by this phase.
- A real trigger-accuracy eval harness (actual Claude-Code-session
  triggering behavior) — remains outstanding after this phase,
  `decisions/0026`.

## Design decisions

See `decisions/0026` (9d's optional/deterministic-gated posture,
including why the trigger-accuracy proxy doesn't close
`decisions/0013`'s item) and `decisions/0027` (`EXPLAINS` coexists with,
doesn't replace, `decisions/0023`'s whole-file chat grounding — this
phase's plan states explicitly, per that ADR's requirement, that
`EXPLAINS` data is for a future Phase 10 consumer only; no current
consumer reads it yet). Testing follows `decisions/0016` directly, not
9a–9c's simpler "zero LLM calls in construction" posture, since this
phase's construction *does* call the API when `--enrich` is passed.

## Files

- `src/depcompass/enrichment.py` (new) — see Scope above.
- `src/depcompass/context_graph.py` — extended (`enrichment` key,
  `DocChunkNode`, `ExplainsEdge`).
- `src/depcompass/cli.py` — `graph --enrich` command.
- `tests/test_enrichment.py` (new).
- Same-commit docs: `architecture/overview.md`'s "Context graph" section
  (extended) and its Cost model section (a second, opt-in cost center
  distinct from `promote`'s), `docs/cli-reference.md` (`graph --enrich`),
  `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md`.

## Verification

- `pytest` — full suite passes, including the new test file; no live
  API call anywhere in the suite (`decisions/0016`).
- `ruff check .` — clean.
- Manual, with a real `ANTHROPIC_API_KEY`, against this repository's own
  `rich` vendor (`depth = full`):
  - `depcompass graph --enrich` — cost disclosure shown, confirm
    prompt honored; on confirmation, `context-graph.json`'s
    `enrichment` block populates with real content (usage-purpose
    labels, at least one cluster, `explains` edges referencing real
    excerpts from `vendor/rich/CLAUDE.md`/`OVERVIEW.md`).
  - Run `depcompass sync` (bare, whole-project) afterward — confirm the
    `enrichment` block is **not** cleared or silently invalidated by
    9a–9c's rebuild (their trigger, `decisions/0025`, is independent of
    9d's, `decisions/0026`) — verified experimentally by inspecting the
    file before and after, not just by code inspection.
  - `depcompass graph` (no `--enrich`) with `ANTHROPIC_API_KEY` unset —
    confirm it still succeeds fully, producing 9a–9c's deterministic
    output with `enrichment: null`.
