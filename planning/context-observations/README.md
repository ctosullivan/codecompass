# Context observations

A log of **how real context experience went** — did a piece of
mechanically-detected, possibly AI-enriched context help an agent, and
if not, why. Introduced by Phase 52, generalising the free-text
`planning/context-use-log.md` (Phase 43c) into the same structural rigor
`planning/context-gaps/` already has.

## What belongs here

- **`EDGE_USEFUL`** — a real (existing) edge helped a real task.
- **`EDGE_UNHELPFUL`** — a real edge was surfaced but didn't help *this*
  task. Not the same as "wrong" — a mechanically correct edge can still
  be irrelevant to the task at hand (see "edge correctness vs. task
  usefulness" below).
- **`EDGE_MISLEADING`** — an edge, or its enrichment, actively led an
  agent astray.
- **`EDGE_STALE`** — an edge's enrichment no longer matches current
  reality (the underlying content changed and the cache hasn't caught
  up, or a real behavioural change wasn't reflected).
- **`EDGE_REDUNDANT`** — context that duplicated something already
  known/shown, adding noise without adding information.

## What does NOT belong here

- **A relationship CodeCompass doesn't have at all** (a missing/requested
  edge) — that's `planning/context-gaps/`, a sibling queue with a
  different destination (a Stage C detection heuristic or Stage E graph
  capability, `decisions/0051`). This file is about *experience with
  edges that exist*, not about edges that should exist but don't.
- **A "how we should work" observation** — that's
  `planning/learnings/inbox.md`.
- **A forward-looking "is the graph adequate for what's coming" call** —
  that's `context-health-planner`'s `planning/context-health.md`.

## Edge correctness vs. task usefulness — always record both, separately

A correct edge can be useless for a given task (`README.md MENTIONS
click`, true, irrelevant to a transaction-validation change). Never
collapse "was this true" and "did this help" into one rating. Recording
`edge correctness: correct` + `task usefulness:
irrelevant-to-this-task` is not the same finding as `edge correctness:
incorrect` — the second is a graph/enrichment defect worth investigating
immediately (`EDGE_MISLEADING`); the first is expected, ordinary noise
that doesn't need action unless it recurs for the *same* edge/detector
across multiple unrelated tasks.

**Never delete or invalidate an authoritative relationship merely
because it was unhelpful for one task.** Recording the observation is
the correct response; touching the graph is not — the graph stays
exactly what mechanical detection produced regardless of what this file
says about it.

## How an entry gets triaged

`knowledge-curator` reviews this inbox at every phase's triage step and
in bulk at milestone consolidations, exactly as it already does for
`planning/learnings/` and `planning/context-gaps/`. The investigate-vs-
record rule it applies (`.claude/agents/knowledge-curator.md`):

| Observation | Default action |
|---|---|
| `EDGE_USEFUL` | record only |
| `EDGE_UNHELPFUL`, first occurrence for this edge/detector | record only |
| `EDGE_UNHELPFUL`, recurring (≥2 instances, same edge or same detector) | investigate — file/link a `CG-NNN` or `L-NNN` |
| `EDGE_MISLEADING` | investigate immediately |
| `EDGE_STALE` | investigate immediately |
| `EDGE_REDUNDANT` | record only, unless recurring |

An investigation's outcome (§ below) either resolves with "no action —
recorded as evidence," or produces/links a `planning/context-gaps/`
entry (if the fix would be a detector/graph change) or a
`planning/learnings/` entry (if it's a process/retrieval/ranking
question) — this file is never itself the destination of a fix, only
the record of what prompted looking for one.

## Statuses

`recorded` → `investigating` → `resolved`. Most entries stay `recorded`
forever — that's expected, not a backlog.

## Files

- `TEMPLATE.md` — the per-observation record format.
- `inbox.md` — the live queue. New entries at the top.

`planning/context-use-log.md` (Phase 43c) is superseded by this
directory as of Phase 52 — its historical entries were migrated in
verbatim (reshaped into this format, no content lost), and it now
carries a pointer here rather than accepting new entries.
