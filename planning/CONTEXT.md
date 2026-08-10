# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 4: `init`/`sync`/`index` commands — done.** MVP phases 0-4 are
now complete; phases 5 (AI-gated gap analysis) and 6 (staleness checking)
remain before the MVP milestone is done.

## What was just completed

Implemented `planning/phase-4-sync-index-init.md` in full: `get_adapter`
dispatch (`adapters/__init__.py`); `depcompass.claude_md` (per-vendor
`CLAUDE.md` template — Metadata with the load-bearing `**Installed
version:**` line, Grounding preamble, API surface, Known gotchas from
`DepNode.side_effects`, Quick links; Gap analysis section omitted, not
stubbed, until Phase 5); `depcompass.sync` (`sync_vendor`/`sync_all` —
per-vendor orchestration writing all five output files under
`vendor/<name>/`, plus a `vendor/<name>/src/` snapshot copy for `depth =
full`, pruned more loosely than `FILETREE.md` so test directories
survive); `depcompass.index` (idempotent routing-table injection);
`depcompass.discovery` (manifest-based `vendor.toml` bootstrap for `init
--scan`). `cli.py`'s `init`/`sync`/`index` are wired to this real logic;
the `_write_claude_md` stub is gone. `VendorDigest` gained a
`side_effects` field. `architecture/overview.md`, `docs/cli-reference.md`,
`docs/config-schema.md`, `planning/ROADMAP.md`, and `CHANGELOG.md`
updated to match. All tests pass (109 total: 108 passed, 1 skipped — the
Cargo live smoke test, unchanged since Phase 2 — up from 68 at the end of
Phase 3), `ruff check .` is clean.

**Two deliberate, disclosed deviations from the plan's literal design**
(documented in `architecture/overview.md`'s Known footguns and
`CHANGELOG.md`, not just here):
1. `index` reads each vendor's already-synced `CLAUDE.md` from disk
   (`index.RoutingRow`/`load_routing_rows`) instead of accepting
   `list[VendorDigest]` and/or re-running `sync` — the plan had
   explicitly left this open. Re-running `sync` inside `index` would make
   `index` silently pay gap-analysis AI cost once Phase 5 lands, which
   would defeat the entire architectural reason `index` exists as a
   command separate from `sync`. Consequence: a never-synced vendor shows
   `_not synced_` rather than erroring, and the routing table's Deps
   column links to `DEPTREE.md` rather than showing a live count.
2. `init --scan`'s real CLI syntax is a repeated flag
   (`--scan a --scan b`), not one flag followed by space-separated files
   as the original `docs/cli-reference.md` draft showed — Click/Typer
   options don't support the latter for a named flag. The docs were
   corrected in this session's closeout commit, not left stale.

**One real end-to-end verification, not just fixture/mock-based**: `sync`
was run for real (via the CLI, `typer.testing.CliRunner`) against this
repo's own installed `pytest` dependency, producing a genuine
`vendor/pytest/` directory — not mocked, matching the plan's Verification
step 3.

## Decisions made this session not already captured in an ADR

- None — the two deviations above are implementation refinements of
  details the plan itself left open (see `planning/phase-4-sync-index-init.md`'s
  Design decisions and Status sections), not new architectural tradeoffs
  requiring a fresh ADR. No new ADR was written this session.

## Next concrete step

Write `planning/phase-5-gap-analysis.md` before any Phase 5 code, per
`CLAUDE.md` §1. Phase 5 scope (per the roadmap): AI-gated gap analysis at
`depth = full` using `claude-haiku-4-5`, dual-audience output (technical +
conversational overview, per `decisions/0012`), `--budget` cost control
for promoting several vendors to `full` at once, and slotting the Gap
analysis section back into `claude_md.render_vendor_claude_md` (after API
surface, per architecture/overview.md) — the first section that section
of the template has been missing since Phase 4 built it.

**Still outstanding, not a Phase 5 blocker but worth remembering**: once
a Rust toolchain is available anywhere in the pipeline, `decisions/0014`
requires validating the Cargo adapter's fixture assumptions and regex-
based `pub` extraction against real `cargo metadata` output and a real
crate — currently entirely unverified. `extract_npm_symbols` (Phase 3) is
also still untested against real-world `.d.ts` authoring styles beyond
hand-written fixtures.
