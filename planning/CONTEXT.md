# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 2: Ecosystem adapters — done.**

## What was just completed

Implemented `depcompass.adapters`: the `EcosystemAdapter` ABC, `AdapterError`,
and a shared `_run_json` subprocess seam (`base.py`); `NpmAdapter`,
`PythonAdapter`, and `CargoAdapter`, each implementing the four adapter
methods per `planning/phase-2-ecosystem-adapters.md`. `pipdeptree` added
as a real dependency. New ADR `decisions/0014` records the fixture-mocked
testing strategy (resolving the Cargo-toolchain-unavailable blocker).
`architecture/overview.md`, `planning/ROADMAP.md`, and `CHANGELOG.md`
updated to match. All tests pass (42 total: 41 passed, 1 skipped — the
Cargo live smoke test — up from 16 at the end of Phase 1), `ruff check .`
is clean, and the npm/Python live smoke tests
both ran successfully against real installed packages in this
environment; the Cargo live smoke test is written but skipped (no Rust
toolchain here).

**Two real cross-platform bugs were found and fixed during
implementation** (documented in `architecture/overview.md`'s Known
footguns and `decisions/0014`'s Consequences, not just here): (1) on
Windows, `npm` resolves to a `.cmd` shim that `subprocess.run` can't
launch by bare name without a shell — fixed by resolving via
`shutil.which` before invoking, in `_run_json`. (2) A bare `pipdeptree`
isn't reliably on `PATH` outside an activated venv — fixed by invoking it
as `sys.executable -m pipdeptree` in the Python adapter. Neither would
have been caught by fixture-only testing; both were caught by the live
smoke tests the Phase 2 plan called for.

## Decisions made this session not already captured in an ADR

- None beyond what's captured in `decisions/0014` and
  `planning/phase-2-ecosystem-adapters.md` — the two subprocess fixes
  above are implementation bugs/fixes, not architectural tradeoffs,
  recorded as footguns in `architecture/overview.md` rather than as
  ADRs.

## Next concrete step

Write `planning/phase-3-tree-generation.md` before any Phase 3 code, per
`CLAUDE.md` §1. Phase 3 scope (per the roadmap): deterministic
`FILETREE.md`/`DEPTREE.md` generation from the `DepNode` trees Phase 2's
adapters now produce — diamond-dependency deduplication (the "see X
above" back-references explicitly deferred from Phase 2), dev-only
collapsing to a count, depth-capping large trees with an explicit
collapse notice, purpose annotations, the flat greppable symbol index,
and the `filetree.json`/`deptree.json` sidecars. No AI calls in this
phase (see `architecture/overview.md`'s Tree generation section).

**Still outstanding, not a Phase 3 blocker but worth remembering**: once
a Rust toolchain is available anywhere in the pipeline, `decisions/0014`
requires validating the Cargo adapter's fixture assumptions and regex-
based `pub` extraction against real `cargo metadata` output and a real
crate — currently entirely unverified.
