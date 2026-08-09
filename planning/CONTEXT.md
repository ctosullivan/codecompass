# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 2: Ecosystem adapters — planned (plan file written, implementation
not started).** Unchanged by this session — see below.

## What was just completed

Recorded a design decision that doesn't touch Phase 2: the chat REPL
(Phases 7-8, not yet started) is now designed as a primary consumption
mode for vendor digests, not a convenience layer bolted onto the markdown
files. New ADR `decisions/0012-conversational-first-repl-design.md`
covers two consequences for not-yet-written phase plans: Phase 5's gap
analysis will produce dual-audience output (existing technical block +
a new conversational overview, same AI call/cost); Phase 8's REPL will
load a project-wide dependency rollup (synthesized from per-vendor
conversational overviews) unconditionally at session start, rather than
routing to it the way vendor-specific escalation does. `architecture
/overview.md`'s Gap analysis and Chat REPL sections, `planning/ROADMAP.md`
's Phase 5/8 rows, and `CHANGELOG.md` were updated in the same commit
batch. No `CLAUDE.md` change (no process rule affected) and no code
change (Phases 0-2 are untouched).

Side effect: taking ADR number `0012` for this decision means Phase 2's
plan file (`planning/phase-2-ecosystem-adapters.md`), which had
provisionally referenced `decisions/0012` for its own fixture-mocking-
testing ADR, was renumbered to `decisions/0013` — fixed in the same
commit as the new ADR.

## Decisions made this session not already captured in an ADR

- None — this session's only decision is the ADR itself
  (`decisions/0012`).

## Next concrete step

Two independent threads, in no particular order:

1. **Phase 2 implementation** (unchanged from before this session):
   implement per `planning/phase-2-ecosystem-adapters.md`, starting with
   `src/depcompass/adapters/base.py`, then each adapter + tests, then
   `decisions/0013` (not 0012 — see above), then doc/changelog/context
   closeout.
2. **Whenever Phase 5 or Phase 8 begin**: their `planning/phase-N-*.md`
   plan files (not yet written) must incorporate `decisions/0012` from
   the start — Phase 5's plan must scope the dual-audience gap-analysis
   output, Phase 8's plan must scope the dependency-rollup synthesis step
   — rather than being written to the old single-audience/fully-routed
   design and needing rework later. This is the detail most likely to get
   lost by the time those phases actually start, so it's called out here
   explicitly rather than trusting the ADR alone to be re-read.
