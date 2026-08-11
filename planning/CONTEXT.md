# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 6: Staleness checking — planned, not yet implemented.** MVP
phases 0-5 are done; `planning/phase-6-staleness-checking.md` exists and
is committed, but no `check`/`staleness.py` code has been written yet.
Phase 6 is the last phase before MVP phases 0-6 can be promoted from
`[Unreleased]` to a dated release (`CLAUDE.md` §6).

## What was just completed

Wrote and saved `planning/phase-6-staleness-checking.md` (plan-only, per
`CLAUDE.md` §1 — no implementation code this session). Four design
questions were resolved with the user via `AskUserQuestion` before
finalizing: (1) version parsing — a small custom `major.minor.patch`
regex parser, no new dependency, consistent with `decisions/0009`/`0011`'s
established dependency-avoidance; (2) bare `check` (no flags) is
report-only and always exits 0 — only `check --strict` turns
MAJOR/`UNKNOWN`/adapter-error into a non-zero exit; (3) transitive-drift
detection is a full diff (persisted `deptree.json` vs. a fresh live tree,
flattened to `name -> set[version]` maps), not just a root-version
comparison; (4) `check --fix` reuses `sync_vendor` as-is, unmodified,
isolating `AdapterError` per vendor in `cli.py`'s own `--fix` loop rather
than inside `sync_vendor`.

A fifth decision came up during design (not a separate question, resolved
by extending an already-approved precedent): `check` must stay cheap and
side-effect-free the same way `index.py` (Phase 4) already is, which means
it never builds a full `VendorDigest`. That leaves the Phase-1
`VendorDigest.is_stale` stub with no code path that could ever populate
it, so the plan removes `is_stale`/`_stale` from `VendorDigest` entirely
and gives `check` its own `VendorStaleness` dataclass (mirroring
`index.py`'s `RoutingRow`). Flagged explicitly in the plan as a removal,
not silently dropped.

Also decided: `read_installed_version` (the `**Installed version:**` regex
+ file read) moves from a private copy in `index.py` into a new shared
`claude_md.read_installed_version`, since `claude_md.py` already owns that
file format — `index.py`'s behavior is unchanged, just de-duplicated.

`planning/ROADMAP.md`'s Phase 6 row is now `planned` with a link to the
plan file; `CHANGELOG.md` has a `[Unreleased]` → `Added` entry describing
the plan (not the implementation, which doesn't exist yet).

## Decisions made this session not already captured in an ADR

- None of Phase 6's five design decisions (see above) were judged
  ADR-worthy — none reverses a previously-recorded decision; all are
  captured in `planning/phase-6-staleness-checking.md`'s Design decisions
  section. Re-evaluate this at implementation time if something in Design
  turns out to be more load-bearing than it looks from the plan alone
  (per `CLAUDE.md` §2's standing instruction).

## Next concrete step

Implement `planning/phase-6-staleness-checking.md`: `claude_md.py`'s
`read_installed_version` + `index.py`'s refactor + their tests first, then
`staleness.py` + tests, then `core.py`'s `is_stale` removal + test
cleanup, then `cli.py`'s `check --strict`/`--fix` + tests, then the
same-commit doc/changelog/context closeout described in the plan's Scope
section. This has not been started — do not begin without an explicit new
implementation request, per this project's plan-before-implementing
process (`CLAUDE.md` §1) having already been satisfied by the plan file
alone, not yet by any code.

**Still outstanding, not a Phase 6 blocker but worth remembering**:
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter's fixture
  assumptions and regex-based `pub` extraction against real `cargo
  metadata` output and a real crate — currently entirely unverified.
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `gap_analysis.py` (Phase 5) has never been run against the real
  Anthropic API in this environment — a human must do this manually at
  least once before trusting output quality (`decisions/0016`).
- Once Phase 6 actually lands, the `CLAUDE.md` §6 release-promotion step
  (dated `CHANGELOG.md` section + version tag for the MVP milestone,
  phases 0-6) is a separate, explicit action — not something to bundle
  silently into Phase 6's own closeout commit.
