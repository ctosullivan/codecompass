# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 1: Core data models & config parsing — done.**

## What was just completed

Phase 1 (core data models, `vendor.toml` parsing, CLI skeleton) is done —
see the prior entry in git history / `CHANGELOG.md` for detail. Since
then: added `planning/ROADMAP.md`, a full-roadmap phase-status table
(all 13 phases, MVP-milestone vs post-MVP, distinct from this file's
current-phase-only view). Updated `CLAUDE.md` (§0, §1, §2, §5 — approved
by the user before commit, per its own rule) and `CONTRIBUTING.md` to
require keeping `planning/ROADMAP.md` in sync: added to it when a phase's
plan file is created, marked `done` when a phase finishes.

## Decisions made this session not already captured in an ADR

- `VendorDigest.is_stale` is implemented as a property/setter pair backed
  by a private `_stale` field (`init=False`) rather than a constructor
  argument — keeps `VendorDigest(config=..., installed_version=...)`
  construction clean while still letting Phase 6's `staleness.check()`
  populate it later via plain assignment (`digest.is_stale = True`).
  Implementation detail, not an architectural tradeoff worth its own ADR.
- CLI stub commands (`init`/`sync`/`index`/`check`/`chat`) were kept
  argument-free for Phase 1 rather than wiring up the flags documented in
  `docs/cli-reference.md` (e.g. `--scan`, `--budget`, `--strict`) — those
  flags get added when each command's real logic lands in its own phase,
  to avoid writing parsing code now that would need revisiting anyway.
  `docs/cli-reference.md`'s intro note flags this explicitly.
- `Depth` and `Ecosystem` use `enum.StrEnum` (stdlib since 3.11) rather
  than `class X(str, Enum)` — a small direct benefit of the Phase 0
  min-Python-3.11 decision (`decisions/0009`).
- `planning/ROADMAP.md`'s addition was treated as a process/tooling
  change, not an architectural decision — no new ADR was written for it
  (comparable to how Phase 0's git-commit-granularity choice lived here
  rather than as an ADR).

## Next concrete step

Write `planning/phase-2-ecosystem-adapters.md` before any Phase 2 code,
per `CLAUDE.md` §1. Phase 2 scope (per the original roadmap): the
`EcosystemAdapter` ABC (`installed_version`, `source_location`,
`readme_and_api_surface`, `dependency_tree`) plus npm, Python, and Cargo
adapter implementations. Note before starting: the Cargo toolchain
(`cargo`/`rustc`) is not installed in the primary dev environment as of
this session — confirm availability (or an alternative testing strategy)
before committing to the Cargo adapter's verification plan.
