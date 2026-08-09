# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 2: Ecosystem adapters — planned (plan file written, implementation
not started).**

## What was just completed

Wrote and committed `planning/phase-2-ecosystem-adapters.md`, resolving
the Cargo-toolchain-unavailable blocker flagged at the end of Phase 1:
adapters will call subprocesses through a shared `_run_json` seam that
tests monkeypatch with hand-written fixture JSON, so all three adapters
(npm, Python, Cargo) get tested core parsing logic without needing a real
toolchain locally — to be recorded as `decisions/0012` during
implementation. Also decided: `pipdeptree` will be added as a real
dependency (not an external prerequisite like npm/cargo), Python API
surface extraction will use static `ast` parsing rather than importing
installed code, and confirmed live (in this dev environment) that `npm ls
--json` needs `--all` to avoid truncating, and `pipdeptree --json` (flat)
is the wrong shape — `--output json-tree --packages <name>` is required.
No adapter code has been written yet — this session was scoped to the
plan only, per explicit instruction.

## Decisions made this session not already captured in an ADR

- None beyond what's captured in `planning/phase-2-ecosystem-adapters.md`
  itself (its "Design decisions" section covers everything decided this
  session). `decisions/0012` will be written during implementation, not
  this planning session, since ADRs record decisions as they're acted on.

## Next concrete step

Implement Phase 2 per `planning/phase-2-ecosystem-adapters.md`: start
with `src/depcompass/adapters/base.py` (the ABC, `AdapterError`, and the
`_run_json` seam), then each adapter + its tests (npm, then Python, then
Cargo), then `decisions/0012`, then the same-commit doc updates
(`architecture/overview.md`, `planning/ROADMAP.md`, `CHANGELOG.md`), then
this file. Mirror the Phase 1 commit-per-logical-change pattern.
