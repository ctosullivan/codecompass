# 0030. MVP redefined: v0.2 spans phases 9-19

## Status

Accepted

## Context

`decisions/0022` established the precedent that the MVP milestone is a
roadmap phase *group*, expanded once (from phases 0-6 to 0-8) when a
later phase's framing (`decisions/0012`'s "the REPL is the actual
product") made an earlier milestone boundary stale relative to the
project's own stated design.

The user has now requested a second, larger redefinition: retract the
never-built post-MVP context-graph plan (former phases 9a-9e, ADRs
0024-0028) and replace it with a new scope — rename to `codecompass`,
retire `promote`/`Depth` in favor of usage-driven enrichment, a SQLite
relationship graph, a `/discovery` slash command, and an `undo` command —
explicitly framed as "a new definition of the MVP," not an incremental
post-MVP addition.

None of this new scope is a coherent, shippable state on its own until
its last phase lands: intermediate phases leave the tool inconsistent
(e.g., Phase 16 removes `promote` from the CLI but the docs/tool-Skill
text isn't re-framed around the graph/Skills/`/discovery` as primary until
Phase 19). Tagging or documenting a release at any earlier point would,
by the same reasoning `decisions/0022` already used, describe something
stale relative to the project's own stated design.

## Decision

The MVP milestone gains a second phase group: **v0.2 spans phases 9-19**
(rename through chat-demotion-and-governance-docs — see
`planning/ROADMAP.md`'s new MVP (v0.2) table). Phases 0-8 (v0.1) remain
done and unchanged. `v0.2` tags only once Phase 19 is `done`, mirroring
`decisions/0022`'s "tag on group completion, not per-phase" rule. Phases
20-22 (project-root routing/rollup, polish, MCP server — renumbered from
former 10/11/12) remain post-MVP, unaffected in content, only in numbering.

Whether/when to cut the (still-pending) `v0.1` tag remains a separate,
not-yet-made decision, unaffected by this change — same posture
`decisions/0022` already established.

`CLAUDE.md` §6's illustrative parenthetical ("the MVP (phases 0-8) is one
milestone") is now incomplete once a second milestone group exists. Per
`CLAUDE.md` §0, updating that file requires presenting the specific diff
to the user and receiving explicit approval before it's written — this
ADR records the intended change; the edit itself is a distinct, separately
approved step, not bundled into this commit.

## Alternatives considered

- **Treat phases 9-19 as ordinary post-MVP work, not a new MVP tier.**
  Rejected — the user explicitly requested a new MVP definition, and the
  same "REPL is the actual product" reasoning `decisions/0022` used to
  justify its own MVP expansion applies here just as directly: this
  rework's payoff (the graph + Skills + `/discovery` as primary interface)
  doesn't exist as a coherent product until its own group completes.
- **Ship v0.2 incrementally, milestone-tagging after each phase.**
  Rejected for the same reason `decisions/0022` rejected it: an
  intermediate state (e.g. `promote` already removed but docs still
  describing it) would tag/document a release stale relative to the
  project's own design before the group finishes.

## Consequences

- `planning/ROADMAP.md` gains a new "MVP (v0.2) — phases 9-19" table,
  alongside the unchanged "MVP (v0.1) — phases 0-8" table, and a
  renumbered "Post-MVP" table for 20-22.
- The former post-MVP rows 9a-9e are marked superseded (not deleted) in
  the same commit, per `planning/ROADMAP.md`'s own established
  renumbering-note convention.
- `CLAUDE.md` §6's phase-count parenthetical needs updating as a distinct,
  explicitly approved follow-up (see Decision above) — not forced into
  this commit.
- `CONTRIBUTING.md`'s mirrored MVP-boundary text (per `decisions/0022`'s
  precedent of keeping the two in sync) should be updated alongside
  whatever `CLAUDE.md` diff is eventually approved.
