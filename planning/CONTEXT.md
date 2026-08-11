# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 6: Staleness checking — done. MVP phases 0-6 are all complete.**
The `CLAUDE.md` §6 release-promotion step (a dated `[Unreleased]` →
version-tagged `CHANGELOG.md` section, tagging the MVP milestone) has
**not** been done yet — it's a separate, explicit action, not something
Phase 6's own closeout performs automatically.

## What was just completed

Implemented `planning/phase-6-staleness-checking.md` in full. New
`depcompass.staleness` module: `Severity` enum
(`NONE`/`PATCH`/`MINOR`/`MAJOR`/`UNKNOWN`), a small custom
`major.minor.patch`-triple version parser (no new dependency, per
`decisions/0009`/`0011`'s established pattern), `classify` implementing
`decisions/0005`'s patch-silent/minor-warns/major-hard-fails policy,
`VendorStaleness` (a lightweight result type mirroring `index.py`'s
`RoutingRow`, not a `VendorDigest`), `check_vendor`/`check_all`. Detects
transitive-only (DEPTREE) drift by diffing a vendor's persisted
`deptree.json` against a freshly built live tree (via a shared `_flatten`
helper, `deptree.render_deptree_json`'s already-deduplicated shape reused
for both sides) whenever the vendor's own root version is unchanged —
informational only, never affects `--strict`'s exit code.

`cli.py`'s `check` command is real: bare `check` is report-only and always
exits 0; `--strict` is the CI gate (non-zero on `MAJOR`/`UNKNOWN`
severity or a failed live-version read); `--fix` regenerates every stale
vendor via the exact same `sync_vendor` `sync` itself uses (including a
fresh gap-analysis call for `depth = full` vendors), with `check`'s own
`--fix` loop — not `sync_vendor` — isolating one vendor's `AdapterError`
from the rest of the batch; `--strict` and `--fix` are mutually exclusive.
Output is a Rich `Table` (Vendor, Recorded, Live, Severity, Notes), rows
styled red/yellow by severity/error.

`claude_md.read_installed_version` is a new shared helper (moved out of a
private regex `index.py` used to keep to itself) — `index.py`'s
`load_routing_rows` now calls it too, behavior-preserving, de-duplication
only.

**`VendorDigest.is_stale`/`_stale` were removed from `core.py`**, along
with the two tests that exercised the old stub. This was flagged in the
plan before implementation, not a silent drive-by: `check` never builds a
`VendorDigest` (same reasoning `index.py` established in Phase 4 for
staying cheap and side-effect-free), so the Phase-1 `is_stale` stub had no
code path left that could ever populate it.

All same-commit docs updated: `architecture/overview.md` (Core data model,
Per-vendor CLAUDE.md structure, Two consumption modes, and a rewritten
Staleness checking section with real signatures; Known footguns gained the
version-parser's limitations, the bare-`check`-always-exits-0 behavior,
and the `is_stale` removal), `docs/cli-reference.md` (`check` section
rewritten from stub to real), `planning/ROADMAP.md` (Phase 6 → done, MVP
completion noted), `CHANGELOG.md` (`Added`/`Removed`/`Changed` entries),
`planning/phase-6-staleness-checking.md`'s own Status field.

**Verification**: `pytest` reports 162 passed, 1 skipped (the Cargo live
smoke test, unchanged since Phase 2) out of 163, up from 136 at the end of
Phase 5; `ruff check .` is clean. A manual end-to-end run against the
real, already-installed `pytest` package confirmed `sync` → `check` shows
`NONE` severity and exits 0, `check --strict` also exits 0 when nothing is
stale, `check --strict --fix` together errors immediately with no output,
and `check --fix` against an already-fresh vendor makes no changes. No new
ADR was written — neither the version-parser choice nor the `is_stale`
removal reverses a previously-recorded decision.

## Decisions made this session not already captured in an ADR

- None. All five of Phase 6's design decisions (version parsing, bare
  `check`'s always-exits-0 behavior, full transitive-drift diffing,
  `--fix` reusing `sync_vendor` unmodified, and the `is_stale` removal)
  are documented in `planning/phase-6-staleness-checking.md`'s Design
  decisions section and in `architecture/overview.md`'s Known footguns —
  none was judged to reverse a previously-recorded decision.

## Next concrete step

**MVP phases 0-6 are complete.** The two things that could reasonably
come next, neither decided yet:
1. The `CLAUDE.md` §6 release-promotion step itself: dated
   `[Unreleased]` → a versioned `CHANGELOG.md` section, and a version tag,
   for the phases 0-6 MVP milestone.
2. Planning Phase 7 (single-vendor chat REPL, per `planning/ROADMAP.md`'s
   Post-MVP table) — per `CLAUDE.md` §1, would need its own
   `planning/phase-7-*.md` written and approved before any implementation
   starts, same process as every phase so far.

Neither has been started or requested yet — surface both as open options
next session rather than assuming which one the user wants first.

**Still outstanding, not a blocker but worth remembering**:
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter's fixture
  assumptions and regex-based `pub` extraction against real `cargo
  metadata` output and a real crate — currently entirely unverified.
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `gap_analysis.py` (Phase 5) has never been run against the real
  Anthropic API in this environment — a human must do this manually at
  least once before trusting output quality (`decisions/0016`).
- `staleness.py`'s custom version parser (Phase 6) has no real PEP 440 or
  full-semver correctness — flag if it misclassifies a real-world version
  string once used against real projects.
