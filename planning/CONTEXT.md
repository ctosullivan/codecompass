# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and
`planning/retros/` for history; per `CLAUDE.md` §4, this file is for
session-resumption, not a project history.

## Current phase

**CodeCompass v1.0.0 is released.** The redefined-v1 milestone group
(`decisions/0048`, Phases 0–70) is complete and closed: published to
PyPI as the `codecompass-context` distribution (CLI command and Python
import package both stay `codecompass`), tagged `v1.0.0`. Current-state
description of what CodeCompass does: `README.md`,
`architecture/module-map.md`, `docs/quickstart.md` — not this file.
Full status: `planning/ROADMAP.md`. Closeout record:
`planning/v1-closeout.md`.

Deferred, post-v1, each with its own revisit trigger in
`planning/ROADMAP.md`: GATE DD/Stage E, Phases 24/25/48/50.

## What was just completed

**Phase 71 — post-v1 documentation refresh — in progress (2026-09-24).**
Direct user request: `README.md` rewritten (limitations, evidence/
provenance model, realistic v1 positioning); `planning/ROADMAP.md`
restructured (412→113 lines, historical phase table replaced with a
concise current-state summary — full history preserved in
`v1-closeout.md`, `v1-redefinition/roadmap.md`, and git history); this
file further reduced. One mechanical check adapted:
`check_readme_phase_count` now compares README's and ROADMAP's own
"phases 0-N" prose claims directly, since the per-phase row table it
used to scan no longer exists.

## Known standing gaps (current-state facts, not phase history)

- Cargo adapter (`decisions/0014`) never validated against real `cargo
  metadata` output or a real crate — no Rust toolchain available yet.
- `extract_npm_symbols` untested against real-world `.d.ts` authoring
  styles beyond hand-written fixtures.
- `chat.py` never run against the real Anthropic API in this
  environment.
- `staleness.py`'s version parser has no real PEP 440/semver
  correctness — string comparison only.
- No formal trigger-accuracy evaluation harness for per-vendor Skills.
- Cursor `.mdc` export has no `globs` field.
- `symbol_enrichment` has no producer/model attribution (`L-031`,
  tracked in `planning/ROADMAP.md`'s future-improvement backlog).
- External-adapter wire protocol's `ecosystem`/`capabilities` fields
  received but not validated (`L-032`, same backlog).
- `vendor/` and a local `.venv/` exist in this checkout (both
  gitignored, freely regeneratable) — live artifacts, not fixtures.

## Next concrete step

Finish Phase 71: independent consistency review of the rewritten
`README.md`/`ROADMAP.md` against `src/`/tests/`v1-closeout.md`; a
consistency sweep of other current-facing docs; standard closeout
(retro, drift audit, learning triage, DoD audit).
