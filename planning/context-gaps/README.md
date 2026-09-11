# Context gaps

A log of **relationships an agent (or the lead) believes CodeCompass's
context should represent, but that mechanical detection does not — or
cannot — produce.**

Introduced by Phase 43c. Governed by `decisions/0051`.

## What belongs here

- A dependency ↔ dependency link CodeCompass has no concept for
  (e.g. "package X is only ever used together with package Y").
- A dependency ↔ local-code link the import / usage-edge scan misses
  (dynamic import, a CLI shelling out to an executable, a re-export).
- A local-code ↔ local-code link that is one *feature* spread across
  files, which the graph (imports + usage edges + doc mentions) does not
  join — e.g. `skill.py` ↔ `graph.skills_index` ↔ `cli.py::query_skills`
  (`CG-001`).
- A doc ↔ code or behaviour ↔ test link a human sees immediately and the
  word-boundary mention pass cannot (a doc that discusses a dependency
  *conceptually* without naming it — the gap `decisions/0045` explicitly
  left open).
- Context that was **present but wrong or misleading** because the graph
  lacked the relationship needed to correct it.

## What does NOT belong here

- "How we should work" observations — those are **candidate learnings**
  (`planning/learnings/inbox.md`). A context-gap is specifically "what the
  graph cannot represent".
- Bugs in existing detection (a mention the pass *should* have caught and
  didn't) — that is a normal defect / candidate learning, not a gap in
  the model.
- Feature requests for `query` output formatting, Skills, etc.
- Anything that would be fixed by a re-`sync` (that is a freshness
  problem — see `planning/context-health.md`).

## The hard rule (`decisions/0051`)

**A context-gap entry is an observation with provenance. It never enters
`context-graph.db`.** It becomes authoritative only by promotion through
the learning lifecycle into either:

- a **mechanical-detection improvement** — a new *deterministic*
  heuristic — a **Stage C** decision, gated on **GATE DB** (Phase 47),
  with its own ADR (`decisions/0045`'s standing requirement); or
- a **new graph capability** — a provenance-carrying edge kind — a
  **Stage E** decision, gated on **GATE DD** (Phase 55), with its own ADR
  (`conditional-generalisation.md` §3).

Until then it is prose in this folder and nothing more.

## How it feeds the gates

`conditional-generalisation.md` §1.2 lists the hypotheses GATE DB/DD will
rule on. Several are confirmed by *recurring* context-gaps:

| Hypothesis (`conditional-generalisation.md`) | Context-gap signal that would support it |
|---|---|
| v1 needs a generalised `technical_dependency` concept (§2.1) | ≥2 entries "CodeCompass cannot represent dependency kind X" across ≥1 project |
| v1 needs first-class provenance (§2.4) | recurring "context was misleading because an inferred/doc claim was shown like a source fact" |
| task-oriented retrieval needs new edges, not just joins (§2.6) | recurring "the "one feature, N modules" map can't be built from existing graph data" (`CG-001` is the first) |

The `knowledge-curator` reviews this folder alongside `planning/learnings/`
at every phase's triage step, and in bulk at Phases 47 and 55. A gap that
**recurs**, or is **filed independently by two agents**, is promoted from
`candidate` to `recurred` and named in the GATE DB/DD input.

## Files

- `TEMPLATE.md` — the per-gap record format.
- `inbox.md` — the live queue. New entries at the top.

There is deliberately **no** long-lived "all context gaps ever" document
and no promoted-pointer log of its own — a promoted gap is logged in
`planning/learnings/promoted.md` like any other promotion, pointing at the
ADR / heuristic that resolved it.

## Statuses

`candidate` → `recurred` → `promoted-to-roadmap` (a Stage C/E phase now
owns it) / `discarded` (one-line reason).
