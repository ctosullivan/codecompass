# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 2: Ecosystem adapters — planned (plan file written, implementation
not started).** Unchanged by this session — see below.

## What was just completed

Recorded a second design decision, independent of Phase 2: Agent Skills
become the primary multi-tool export target (Phase 9), motivated by a
reliability gap in the `CLAUDE.md` routing table (a soft "consult this
digest" instruction an agent can simply not follow, especially for
well-known libraries it feels confident about). New ADR
`decisions/0013-agent-skills-as-shared-context-selection-source.md`
covers: one Skill per `FULL`-depth vendor with `references/`-bundled
trees; Cursor `.mdc` export and the `CLAUDE.md` routing table retained as
fallbacks, not replaced; Phase 8's REPL Tier 1 routing consuming the same
generated Skill description text Phase 9 produces (one source of truth,
not independently-tuned duplicates); and an explicit REPL escalation path
to the generated Skill folder for questions exceeding digest-only scope.
`architecture/overview.md`'s Multi-tool export and Chat REPL sections,
`planning/ROADMAP.md`'s Phase 8/9 rows, and `CHANGELOG.md` were updated in
the same commit batch. No `CLAUDE.md` change and no code change (Phases
0-2 remain untouched).

Side effect, second time this has happened: taking ADR number `0013` for
this decision means Phase 2's plan file
(`planning/phase-2-ecosystem-adapters.md`), which had provisionally
re-referenced `decisions/0013` for its own fixture-mocking-testing ADR
(itself a renumbering from an earlier `0012` collision), was bumped again
to `decisions/0014`. Added a standing note directly in that plan file to
verify the true next-available number against `/decisions` at
implementation time rather than trust either provisional number — this
has now collided twice, so the plan file should not be trusted blindly
on this point.

## Decisions made this session not already captured in an ADR

- None — this session's only decision is the ADR itself
  (`decisions/0013`).

## Next concrete step

Two independent threads, in no particular order:

1. **Phase 2 implementation** (unchanged from before this session):
   implement per `planning/phase-2-ecosystem-adapters.md`, starting with
   `src/depcompass/adapters/base.py`, then each adapter + tests. Before
   creating its adapter-testing ADR, check `/decisions` for the actual
   next available number rather than trusting the plan file's `0014` —
   it has been wrong twice already.
2. **Whenever Phase 5, Phase 8, or Phase 9 begin**: their
   `planning/phase-N-*.md` plan files (not yet written) must incorporate
   the relevant ADR(s) from the start:
   - Phase 5: `decisions/0012`'s dual-audience gap-analysis output.
   - Phase 8: `decisions/0012`'s dependency-rollup synthesis, plus
     `decisions/0013`'s Tier-1-sources-from-Skill-descriptions dependency
     on Phase 9 and the digest-exceeded escalation path.
   - Phase 9: `decisions/0013`'s Skills-as-primary-export scope
     (broadened from Cursor-only), including the trigger-accuracy
     evaluation step.
   Whichever of Phase 8/Phase 9 is written first should note explicitly,
   in its own plan file, what data shape the other phase will need to
   consume — this is the detail most likely to get lost by the time both
   phases actually exist, so it's called out here rather than trusting
   the ADRs alone to be re-read at the right moment.
