# 0034. Chat demoted; the graph, generated Skills, and `/discovery` are the primary interface

## Status

Accepted

## Context

`decisions/0012` framed the REPL as "the actual product," a decision
significant enough to later justify expanding the MVP milestone itself
(`decisions/0022`) around Phase 8's dependency on it. The user has asked,
as part of this rework, to demote chat to a secondary, dev/debug-oriented
tool — no longer the product's primary framing — with the new SQLite
graph (`decisions/0032`), generated Skills (`decisions/0013`,
`decisions/0020`), and a new `/discovery` slash command (Phase 17) taking
over as the primary way both humans and agents interact with
`codecompass`'s output.

## Decision

`chat <vendor>` remains a fully functional subcommand with **zero code
changes** (`chat.py`'s logic, its digest-only grounding, and
`decisions/0023`'s "never regenerates" rule are all unaffected). What
changes is framing, not behavior: `README.md`, `architecture/overview.md`,
and the tool-level Skill's instruction text are rewritten (Phase 19) to
present the graph + generated Skills + `/discovery` as the primary
consumption surface, with `chat` mentioned as an available but secondary,
narrower option — no longer described as "the actual product."

## Alternatives considered

- **Remove `chat` entirely.** Rejected — it remains genuinely useful for
  quick, digest-only Q&A in a plain terminal, and removing working,
  tested code purely for a framing change is unwarranted churn this
  project's own conventions (don't refactor beyond what a task requires)
  argue against.
- **Gate `chat` behind an explicit dev signal** (an env var, a `--dev`
  flag, or a debug namespace). Explicitly considered and rejected during
  this rework's planning interview in favor of the lighter option above —
  re-framing documentation was judged sufficient; adding friction to a
  still-useful command was not.

## Consequences

- `decisions/0012` is superseded by this ADR; it is not edited
  (append-only) — its historical framing remains accurate for the period
  before this decision.
- `decisions/0023` (chat grounds on persisted files, never regenerates)
  is unaffected in substance — it continues to describe the now-secondary
  feature's actual behavior.
- The tool-level Skill's rewritten instruction list (Phase 16/19) no
  longer features `chat` as a first workflow step; `/discovery` (Phase 17)
  is positioned as the richer, graph-grounded alternative for guided
  exploration inside a real Claude Code session.
