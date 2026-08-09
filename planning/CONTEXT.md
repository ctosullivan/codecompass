# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 0: Repository scaffolding — done.**

## What was just completed

Initialized the empty repository with full Phase 0 scaffolding:
licensing/packaging metadata (`LICENSE`, `pyproject.toml`, `.gitignore`,
empty `src/depcompass/` placeholder), the process-rules `CLAUDE.md`
(explicitly approved by the user before commit, per its own §0 rule), a
living `architecture/overview.md`, nine foundational ADRs
(`decisions/0001`-`0009`), forward-looking `docs/cli-reference.md` and
`docs/config-schema.md` stubs, and an empty `tests/` skeleton. No
implementation code exists yet — `src/depcompass/__init__.py` is empty and
the `depcompass.cli:app` entry point it references doesn't exist yet.

## Decisions made this session not already captured in an ADR

- **Git commit granularity for Phase 0**: scaffolding landed as 8 separate
  commits (metadata/licensing, README+CONTRIBUTING, CLAUDE.md alone,
  architecture, ADRs as one batch, docs stubs, tests skeleton, plan+
  context+changelog) rather than one big commit, so each piece is
  independently reviewable — especially isolating the CLAUDE.md commit
  since it required its own approval step. This is a process choice, not
  an architectural one, so it lives here rather than as its own ADR.
- **CI workflow deferred entirely to Phase 6** (not even a placeholder in
  Phase 0) — rationale is in `planning/phase-0-repo-scaffolding.md`'s
  Scope section: a placeholder now would either run against zero tests
  (misleading) or need rework once real tests land.
- **Build backend: setuptools. Package layout: `src/depcompass/`. Lint
  tooling: ruff, added now as a `dev` extra.** These were open ambiguities
  the Phase 0 Plan agent flagged; resolved with the user before
  implementation (all "recommended" options chosen).
- **Commit message prefixes are type-appropriate** (`chore(phase-0):`,
  `docs(phase-0):`) rather than a blanket `feat(phase-0):`, since nothing
  in Phase 0 is a behavioral feature.
- `tests/__init__.py` was omitted — modern pytest doesn't require it;
  revisit only if Phase 1's actual package layout needs mirrored
  `__init__.py` files for import resolution.

## Next concrete step

Write `planning/phase-1-core-data-models.md` (scope: `VendorConfig`,
`Depth`, `DepNode`, `VendorDigest` in `src/depcompass/core.py`, plus
`vendor.toml` parsing via stdlib `tomllib`) before writing any Phase 1
code, per `CLAUDE.md` §1. That plan file must also resolve the still-open
question from the original spec (§6): whether `vendor/<name>/src/` source
snapshots for `FULL`-depth vendors are committed to git or gitignored and
regenerated on `sync` — noted as unresolved in
`architecture/overview.md`'s Known footguns section and in
`decisions/0004`.
