# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 1: Core data models & config parsing — done.**

## What was just completed

Implemented `depcompass.core` (`VendorConfig`, `Ecosystem`, `Depth` as
`StrEnum`, `DepNode`, `VendorDigest`), `depcompass.config`
(`load_vendor_config()` — fail-fast `vendor.toml` parsing via stdlib
`tomllib`), and `depcompass.cli` (a Typer app with all 5 commands
registered as stubs, satisfying the `depcompass.cli:app` entry point).
Recorded two new ADRs: `decisions/0010` resolves the vendor-src
commit-vs-gitignore question left open from Phase 0 (decided: gitignored,
regenerated on `sync`), and `decisions/0011` records dataclasses over
pydantic for the core models. 16 tests pass, `ruff check .` is clean, and
`depcompass --help` / stub command invocations behave as designed (see
`planning/phase-1-core-data-models.md`'s Status for the full verification
record).

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

## Next concrete step

Write `planning/phase-2-ecosystem-adapters.md` before any Phase 2 code,
per `CLAUDE.md` §1. Phase 2 scope (per the original roadmap): the
`EcosystemAdapter` ABC (`installed_version`, `source_location`,
`readme_and_api_surface`, `dependency_tree`) plus npm, Python, and Cargo
adapter implementations. Note before starting: the Cargo toolchain
(`cargo`/`rustc`) is not installed in the primary dev environment as of
this session — confirm availability (or an alternative testing strategy)
before committing to the Cargo adapter's verification plan.
