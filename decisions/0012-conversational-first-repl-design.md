# 0012. Conversational-first REPL design

## Status

Accepted

## Context

Up to now, digest content and REPL routing were designed agent-first: the
per-vendor `CLAUDE.md` digests were the primary artifact, and the chat
REPL (`depcompass chat`, Phases 7-8) was treated as one access mode among
several — a convenience layer reading the same markdown an AI agent would
read directly. A design conversation clarified that this should flip: the
REPL is the actual product, and the markdown digests (`CLAUDE.md`,
`FILETREE.md`, `DEPTREE.md`) are backing store for **two** consumers — AI
agents reading them directly, and the REPL synthesizing them into
conversation. Both matter, but content generation should be written with
"does this read well spoken aloud in a casual chat" as a first-class
constraint from here forward, not an afterthought bolted on at query time.

This decision is recorded now, at the Phase 2 checkpoint, so Phase 5 (gap
analysis) and Phase 8 (REPL routing) aren't built against an incomplete
understanding of what they're for — recording it after those phases start
would mean rework instead of a one-time design correction.

## Decision

Two concrete changes fall out of this, both scoped into existing phases
rather than requiring new ones:

1. **Gap analysis becomes dual-audience** (Phase 5). The existing
   technical output (API surface gap vs. project needs, action pointer)
   is unchanged. A second, short conversational overview is added to the
   same AI call — what the dependency does, why the project uses it, its
   risk posture, written the way you'd explain it to a colleague, not the
   way you'd document it. Same call, same cost: this is a prompt/schema
   change, not a new cost center.
2. **A project-wide dependency rollup is loaded unconditionally at REPL
   session start** (Phase 8), not routed to. It's synthesized once — not
   per query — from the already-generated per-vendor conversational
   overviews: dependency count by depth, a staleness rollup by severity,
   notable side-effect flags, and a short narrative. No new
   per-dependency AI calls; one cheap summarization pass over data that's
   already paid for. The existing Tier 1/Tier 2 routing (vendor-name
   matching, then project-context signal matching, then model-judged
   fallback) still governs *vendor-specific* escalation on top of this
   baseline — it is not replaced, only no longer the sole gate on whether
   *any* project-level context loads at session start.

## Alternatives considered

- **Keep gap analysis single-audience and let the REPL reformat it
  conversationally at query time.** Rejected — this re-does synthesis
  work on every query instead of once at generation time, and produces a
  weaker result than a purpose-written conversational overview would
  (a reformatted technical block still reads like a reformatted technical
  block).
- **Keep the rollup signal-gated, routed the same way vendor-specific
  questions are.** Rejected — casual whole-project questions ("anything
  risky in my deps right now," "why do we even use X," "what changed
  recently") don't reliably signal either "vendor" or
  "architecture/decisions" the way Tier 1's keyword matching expects, and
  the rollup is cheap enough (one summarization pass, already-paid-for
  inputs) that always-loading it isn't a meaningful cost tradeoff worth
  gating.

## Consequences

- Phase 5's gap-analysis prompt/schema gains a second output section;
  its plan file (not yet written) must scope this in from the start.
- Phase 8's plan file (not yet written) gains a new synthesis step (the
  rollup) as an explicit deliverable, sourced from Phase 5's per-vendor
  conversational overviews — it depends on those existing, same
  dependency ordering as before, no new phase inserted.
- Phase 8's REPL startup banner announces the rollup once, at session
  start, rather than the context-indicator line re-announcing it on every
  turn — the indicator line's existing job (telling the user what
  *additional* context, beyond the baseline rollup, grounded a given
  answer) is unchanged.
- `architecture/overview.md`'s Gap analysis and Chat REPL sections are
  updated in the same commit as this ADR to describe the target design
  going forward.
- No change to `CLAUDE.md`, `core.py`, or any already-shipped Phase 0-2
  code — this is a design decision for not-yet-built phases, not a
  retroactive change to what's already implemented.
