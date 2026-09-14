# 0054. Agent-driven enrichment is a second, non-authoritative producer feeding the existing enrichment tables

## Status

Accepted (Phase 52, user request 2026-09-14, during the context-edge-
lifecycle implementation — `planning/context-edge-lifecycle-plan.md`,
`planning/phase-52-context-edge-lifecycle.md`).

## Context

Every enrichment table (`vendor_enrichment`, `symbol_enrichment`,
`doc_relation_enrichment`) has, since Phase 14/22, exactly one producer:
`enrichment.py`/`relation_enrichment.py` calling `_call_anthropic`
directly — a disclosed, budget-gated, batched HTTP call to the Anthropic
API, triggered only for usage-proven candidates
(`decisions/0033`/`0035`/`0038`). This requires a live
`ANTHROPIC_API_KEY` in the calling environment. No other write path into
these tables exists or has ever existed.

Testing the context-edge-lifecycle work (Phase 52) against Ledgerkit
surfaced a real, non-hypothetical case where that requirement can't be
met: this development environment has no `ANTHROPIC_API_KEY` configured.
The user's direction: rather than skip the enrichment scenario, **have a
Claude Code agent produce the enrichment content instead** — a Claude
Code subagent is itself already an LLM invocation via the harness, with
no separate API key or network call required, and the user explicitly
asked that this respect "appropriate separation of concerns" rather than
folding it into an existing agent's remit for convenience.

This is a genuine, if narrow, architectural question: enrichment has
always been *content an AI produces*, never *a fact CodeCompass
proves* (`decisions/0031`/`0037`/`0045`'s boundary is about graph facts,
not about which specific AI call produces the interpretive text sitting
beside a fact). Whether that content comes from a direct API call inside
`codecompass`'s own process, or from a Claude Code agent reasoning over
the same underlying evidence and having its output written through the
same validated path, is a question of *mechanism*, not of *authority* —
provided the output lands through the exact same non-authoritative
tables, the exact same content-hash caching, and the exact same
provenance discipline the automated path already has.

## Decision

**Agent-driven enrichment is accepted as a second producer for the
existing enrichment tables, writing through the existing `apply_results`
validation path, never through raw SQL, never touching a graph-fact
table, and always distinguishable from automated enrichment by its
`model` column value.**

1. **No schema change.** `vendor_enrichment.model` / `symbol_enrichment`
   (via its shared write path) / `doc_relation_enrichment.model` are
   already `TEXT NOT NULL` columns recording provenance. Agent-driven
   enrichment writes a value of the form `agent:<agent-name>` (e.g.
   `agent:context-enrichment-agent`) into this column — never a string
   that could be confused with a real Anthropic model identifier — so
   every downstream reader (`query vendor`, `query relations`, `check`)
   can already distinguish the two producers with zero code change,
   using a column that has existed since Phase 14.
2. **Same write function, same validation, same caching.** Agent-driven
   results are constructed as ordinary `RelationEnrichmentResult` /
   equivalent objects and passed to the existing `apply_results()` —
   `select_candidates()`'s content-hash cache-hit logic, the
   `UNIQUE(source_doc_path, target_vendor_name, target_doc_path)`
   constraint, and every other invariant `decisions/0038` established are
   unchanged and apply identically regardless of producer.
3. **A new, narrow agent role — not an extension of `knowledge-curator`.**
   `knowledge-curator`'s job is triage and investigation of *observations
   about* edges (`planning/learnings/`, `planning/context-gaps/`,
   `planning/context-observations/`); it has no Bash, writes only
   `planning/**`, and is explicitly forbidden from touching graph state
   of any kind. Enrichment-writing is a different concern — grounded
   interpretation of an already-proven fact, produced by reading real
   source text, not judging an observation. Mixing the two would blur
   "investigates problems with context" with "produces context," and the
   user's own instruction named this distinction explicitly. A new,
   minimal agent (`.claude/agents/context-enrichment-agent.md`) owns this
   one job and nothing else.
4. **Hard boundary, restated for the new role specifically:** the
   agent may only enrich a `doc_relations_edges` (or `uses_edges`,
   symbol-level) row that **already exists** — it is never given, and
   must never accept, an instruction to enrich a relationship that isn't
   already mechanically proven. It has no tool capable of writing a
   graph-fact table. It grounds every claim in the real excerpted source
   text `select_candidates` already selects (the same excerpt the
   automated path would use) — it does not invent content beyond what
   that text supports, mirroring the batched-API prompt's own existing
   grounding instruction.
5. **A minimal CLI surface is justified here, unlike the read-only
   planning-file operations `context-edge-lifecycle-plan.md` §6.1
   already declined to add surface for.** This is a genuine new write
   capability, not a convenience wrapper around files an agent could
   already `Read`/`Edit` directly — `context-graph.db` has no `Edit`-safe
   text representation. `codecompass enrich apply` (exact surface: see
   `planning/phase-52-context-edge-lifecycle.md`) accepts agent-authored
   candidate/result pairs and calls the existing `apply_results`,
   nothing more.

## Alternatives considered

- **Skip the enrichment scenario in this environment, note it as an
  untested gap.** Rejected by the user directly — an agent-driven path is
  both a legitimate test workaround *and*, independently, a real
  capability worth having (an environment without API credentials
  configured is not a hypothetical edge case for a self-hosted tool).
- **Extend `knowledge-curator` to also write enrichment.** Rejected —
  the user's own instruction asked for separation of concerns to be
  considered explicitly; folding "produce interpretive content grounded
  in source text" into an agent whose brief is entirely
  triage-and-investigation-with-no-graph-access would require relaxing
  its most load-bearing prohibition ("never touches graph state") for
  one narrow case, weakening a boundary that currently has zero
  exceptions.
- **Have the agent write raw SQL / edit `context-graph.db` directly.**
  Rejected — bypasses `apply_results`'s existing validation
  (`UNIQUE` constraint handling, content-hash computation, the
  `_RELATION_LABEL_CHECK_SQL` enum guard) and reintroduces exactly the
  "one well-meaning feature away from unproven content look like fact"
  risk `decisions/0051` already rejected for a different data path. Reuse
  the existing function; don't hand-roll a second writer.
- **A generalised `source` column (`model` renamed, `'automated'` vs.
  `'agent'` plus a sub-field) across all three enrichment tables.**
  Rejected as unnecessary schema churn — the existing `model` `TEXT`
  column already accepts any string, and a namespaced convention
  (`agent:<name>`) is sufficient to distinguish producers without a
  migration. Revisit only if a third producer kind ever appears.

## Consequences

- New `.claude/agents/context-enrichment-agent.md` — narrow role, no
  Bash beyond what's needed to invoke `codecompass enrich apply`,
  explicit hard rules mirroring this ADR's §4.
- `src/codecompass/cli.py` gains `enrich apply` (or the exact name
  settled in the phase plan) — the first CLI surface addition this
  milestone's own planning package otherwise avoided, justified
  specifically because it's a write capability with no `Edit`-safe
  alternative.
- `relation_enrichment.py`/`enrichment.py`: no change to `select_candidates`,
  `apply_results`, or any hashing logic — the new CLI path is a thin
  caller of what already exists.
- Every existing reader of `model`/enrichment content is unaffected;
  `agent:*`-provenanced rows behave identically to API-provenanced rows
  everywhere except that one column's value.
- This ADR does not reopen `decisions/0031`/`0037`/`0045` (graph-fact
  authority) or `decisions/0038` (relation-enrichment's natural-key,
  never-writes-spec-docs posture) — both are reaffirmed, not amended.
