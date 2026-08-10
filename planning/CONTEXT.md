# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 5: AI-gated gap analysis — done.** MVP phases 0-5 are complete;
Phase 6 (staleness checking) is the last phase before the MVP milestone
can be promoted from `[Unreleased]` to a dated release (`CLAUDE.md` §6).

## What was just completed

Implemented `planning/phase-5-gap-analysis.md` in full: `depcompass.gap_analysis`
(`generate_gap_analysis`, a single forced-tool-use Anthropic call per
qualifying vendor, pinned to the dated `claude-haiku-4-5-20251001`
snapshot rather than `decisions/0003`'s rolling alias; `estimate_cost`/
`check_budget` for `sync --budget`). `VendorDigest` gained
`conversational_overview`, `gap_analysis_error`, `action_pointer_file`,
`action_pointer_note`. `sync_vendor` now calls gap analysis for `depth =
full` + `context_path` vendors, catching failures locally so the rest of
`sync` isn't blocked by one bad call, and writes a new
`vendor/<name>/OVERVIEW.md` on success. `claude_md.py`'s Gap analysis
section is back (technical text + action pointer, or an explicit
"unavailable" note on failure — never a silent gap). `filetree.py`'s
renderers gained an optional `action_pointer` parameter, closing Phase
3's deferred FILETREE-cross-linking loop. New ADR `decisions/0016`
records that no test in this project ever makes a real Anthropic API
call — a cost-driven extension of `decisions/0014`'s fixture-mocking
precedent. `architecture/overview.md`, `docs/cli-reference.md`,
`docs/config-schema.md`, `planning/ROADMAP.md`, and `CHANGELOG.md`
updated to match — including two stale-doc fixes caught along the way
(the old `_write_claude_md` stub footgun entry, still present despite
Phase 4 having removed it; the Gap analysis section's strikethrough in
the Per-vendor CLAUDE.md structure list). All tests pass (136 total: 135
passed, 1 skipped — the Cargo live smoke test, unchanged since Phase 2 —
up from 108 at the end of Phase 4), `ruff check .` is clean.

**No test makes a real Anthropic API call** — every `generate_gap_analysis`
test monkeypatches `_call_anthropic`; a smaller set of tests exercises
`_call_anthropic` itself against a fake `anthropic.Anthropic` client
(constructed in-test) to verify tool-use parsing and SDK-error wrapping
without going over the network. This means **gap_analysis.py's prompt/
schema correctness against the real model is unverified** — a human must
manually run `depcompass sync` against a real `depth = full` +
`context_path` vendor with a real `ANTHROPIC_API_KEY` at least once
before trusting this phase's output quality. Flagged in
`decisions/0016`'s Consequences and `architecture/overview.md`'s Known
footguns, not just here.

## Decisions made this session not already captured in an ADR

- None beyond `decisions/0016` (already written this session) — the
  model-pinning, `--budget` abort-before-any-calls, per-vendor failure
  isolation, and FILETREE-cross-linking-in-Phase-5 decisions are all
  recorded in `planning/phase-5-gap-analysis.md`'s Design decisions
  section; none individually rise to a second new ADR.

## Next concrete step

Write `planning/phase-6-staleness-checking.md` before any Phase 6 code,
per `CLAUDE.md` §1. Phase 6 scope (per the roadmap): `depcompass check
[--strict] [--fix]` — comparing each vendor's `CLAUDE.md`
`**Installed version:**` line against the ecosystem adapter's live read,
severity-aware (patch silent, minor warns, major hard-fails per
`decisions/0005`), distinguishing vendor-version bumps from
transitive-only DEPTREE drift where practical. This is the last phase
before MVP phases 0-6 can be promoted from `[Unreleased]` to a dated
release per `CLAUDE.md` §6.

**Still outstanding, not a Phase 6 blocker but worth remembering**:
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter's fixture
  assumptions and regex-based `pub` extraction against real `cargo
  metadata` output and a real crate — currently entirely unverified.
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `gap_analysis.py` (Phase 5) has never been run against the real
  Anthropic API in this environment — see above.
