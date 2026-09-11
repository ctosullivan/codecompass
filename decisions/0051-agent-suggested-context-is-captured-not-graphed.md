# 0051. Agent-suggested context is captured as reviewable candidates, never written to the context graph

## Status

Accepted (Phase 43c, user request 2026-09-11).

## Context

`decisions/0031`, `0037`, and `0045` drew and re-drew one line: **AI may
describe a relationship a mechanical pass already proved real; AI may not
decide *whether* a relationship exists.** `0045` closed with an explicit
instruction that any future phase letting AI participate in *detection*
"needs its own ADR arguing the specific gap and the false-positive/cost
tradeoff — not a quiet extension" of an existing mechanism.

Phase 43c introduces a genuinely new input: **a development agent (or the
lead), mid-task, notices a relationship CodeCompass does not represent and
mechanical detection has no way to find.** The motivating case is real —
during Phase 43 the lead reasoned about
`src/codecompass/skill.py` ↔ `graph.skills_index` ↔ `cli.py::query_skills`
as one feature spread across three modules; nothing in the import graph,
the usage-edge scan, or doc-mention detection connects them, and that
observation evaporated when the phase closed.

The redefined-v1 roadmap already anticipates this question. Stage C
(mechanical-detection improvements, gated on GATE DB) and Stage E
(conditional graph abstractions, gated on GATE DD) are where
`conditional-generalisation.md` §2.1 / §2.4 / §2.6 (a generalised
`technical_dependency`, first-class provenance with an `agent_inference`
source kind, task-oriented retrieval edges) get *decided* — on evidence.
Phase 43c must not pre-empt those gated decisions; it must feed them.

The risk if this is done carelessly: an agent-suggested edge written into
`context-graph.db` is indistinguishable, three phases later, from a
mechanically-proven one — exactly the "a low-confidence claim shown like a
source-derived fact" failure mode `conditional-generalisation.md` §2.4
exists to prevent, and a back-door around the `0031`/`0045` boundary.

## Decision

**An agent's suggested relationship is an observation with provenance. It
is captured in `planning/context-gaps/` and nowhere else.**

1. **It never enters `context-graph.db`.** No `agent_suggested_edges`
   table, no `source='agent_inference'` column, no write path from a
   `context-gaps/` entry into any graph table. `context-graph.db` remains
   exactly what `decisions/0024`/`0025`/`0032` describe: a
   deterministically rebuilt store of mechanically-detected structure.
   This holds for Phase 43c unconditionally.

2. **It becomes authoritative only by promotion through the learning
   lifecycle** (`decisions/0050`, `planning/v1-redefinition/learning-lifecycle.md`),
   into one of two destinations, each with its own gate:
   - a **mechanical-detection improvement** (a new deterministic
     heuristic — e.g. "functions in module A that are only called by
     module B's public surface") — a Stage C decision, gated on GATE DB,
     with its own ADR per `0045`'s standing instruction; or
   - a **new graph capability** (a provenance-carrying edge kind) — a
     Stage E decision, gated on GATE DD, with its own ADR per
     `conditional-generalisation.md` §3.

3. **`planning/context-gaps/` is a sibling of `planning/learnings/`, not
   part of it.** A learning is "how we should work"; a context-gap is
   "what the graph cannot represent". Different destinations, so different
   queues — but the `knowledge-curator` reviews both at every triage step
   and in the Phase 47 / 55 consolidations, and a context-gap that
   recurs, or is raised independently by two agents, is the evidence GATE
   DB/DD weighs.

4. **The determinism-first boundary is reaffirmed, not reopened.** Phase
   43c adds a *capture pathway and an evidence trail*. It does not give
   any agent, or any AI call, influence over the contents of the graph.

## Alternatives considered

- **A staging table in `context-graph.db`** (`agent_suggested_edges`,
  never joined into `query` output until reviewed). Rejected: it puts
  unproven relationships one `JOIN` typo — or one future well-meaning
  feature — away from being shown as fact, and it makes a schema change
  and migration for something that is, today, a list of prose
  observations. A `planning/` file has none of that blast radius and is
  just as reviewable.
- **Fold context-gaps into `planning/learnings/inbox.md`.** Rejected:
  the learning lifecycle's classification→destination table
  (`learning-lifecycle.md` §4) routes to tests / ADRs / docs / rules /
  roadmap rows — none of which is "a detection heuristic" or "a graph
  edge kind". Mixing the two queues would blur which gate (DB/DD)
  a given item is evidence for. One curator, two queues.
- **Let the lead add well-supported edges directly to the graph builder
  now.** Rejected: that *is* AI participating in detection, exactly what
  `0045` said needs its own gated ADR. The motivating `skill.py` ↔
  `graph` ↔ `cli.py` case may well justify a real heuristic — but that
  decision belongs at GATE DB with the reference-project evidence beside
  it, not mid-Phase-43c on one example.
- **Do nothing — agents can already file candidate learnings.** Rejected:
  they can, but nothing prompts them to at the moment the observation
  occurs, and a candidate learning routes to the wrong lifecycle. The
  point of Phase 43c is to make the capture *systematic* and *pointed at
  the right gate*, so GATE DB isn't deciding from a blank page.

## Consequences

- New `planning/context-gaps/` (`README.md`, `TEMPLATE.md`, `inbox.md`),
  populated with at least one real entry (`CG-001`, the Phase 43
  `skill.py` ↔ `graph.skills_index` ↔ `cli.py::query_skills` relationship).
- `.claude/agents/knowledge-curator.md` and
  `.claude/agents/reference-project-tester.md` briefs updated to name
  `context-gaps/` as an input / output respectively.
- `planning/v1-redefinition/conditional-generalisation.md` §1.2 marked
  "agent-suggested-edge evidence collection started (Phase 43c)".
- No `src/codecompass/` change in Phase 43c. Any later change is a
  separate, gated, separately-ADR'd decision.
- This ADR does not supersede `0031`/`0037`/`0045` — it extends the same
  boundary to a new input source.
