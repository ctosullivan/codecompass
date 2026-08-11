# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**The MVP milestone now spans phases 0-8, not 0-6 (`decisions/0022`,
this session).** Phases 0-6 remain done, unchanged. Phase 7 is planned,
not implemented. Phase 8 (single-vendor chat REPL) is not started — it
has no `planning/phase-8-*.md` yet; that plan file still needs to be
written, per `CLAUDE.md` §1, before its implementation can start
(realistically once Phase 7 lands, since Phase 8 depends on Phase 7's
outputs — see `decisions/0022`). The `CLAUDE.md` §6 release-promotion
step (a dated `[Unreleased]` → version-tagged `CHANGELOG.md` section,
tagging the MVP milestone) now waits on Phase 8, not Phase 6.

Phase 7 covers a zero-question deterministic bootstrap on bare
`depcompass`, a single reactive `promote <vendor>` command as the only
cost/confirmation point, and replacing `depth = FULL` generation's
mechanism — see `decisions/0017`-`0021` and
`planning/phase-7-bootstrap-and-promote.md` for detail.

## What was just completed

Expanded the MVP milestone from phases 0-6 to phases 0-8
(`decisions/0022`) — bookkeeping only, no code. Prompted by a request to
promote Phase 8 (single-vendor chat REPL) into the MVP; surfaced first
that Phase 8 isn't standalone — it depends on Phase 7's outputs (Skill
files, dual-audience content shape) — so both moved together, in order,
rather than Phase 8 alone. Rationale also ties back to `decisions/0012`:
the REPL is "the actual product," so an MVP milestone stopping at Phase
6 would ship none of it, alongside a `FULL`-depth mechanism (Phase 5's
`gap_analysis`) already scheduled for replacement by Phase 7.

Updated: `planning/ROADMAP.md` (Phase 7/8 rows moved from Post-MVP into
the MVP table; "MVP done when" criteria now include `promote`/`chat`),
`CLAUDE.md` §6 and `CONTRIBUTING.md` ("phases 0-6" → "phases 0-8", the
`CLAUDE.md` edit shown separately and explicitly approved per §0),
`docs/cli-reference.md` and `architecture/overview.md` (stale "MVP
complete at Phase 6" language corrected), `README.md`'s Status section
(also corrected an unrelated pre-existing staleness — it still claimed
"currently at Phase 0"). No phase was renumbered; only table membership
and milestone-boundary text changed.

Prior session's work (Phase 7 planning — reconciling an external
bootstrap/`promote` design doc against real repo state, producing
`decisions/0017`-`0021` and `planning/phase-7-bootstrap-and-promote.md`)
is unchanged by this session; see git history / `CHANGELOG.md` for that
session's detail rather than repeating it here.

## Decisions made this session not already captured in an ADR

- None — `decisions/0022` records this session's only decision.

## Next concrete step

**Two things remain undecided:**
1. `planning/phase-8-*.md` doesn't exist yet — needs writing per
   `CLAUDE.md` §1 before Phase 8 implementation can start. Realistically
   comes after Phase 7 is implemented, given the dependency
   `decisions/0022` documents.
2. Implementing `planning/phase-7-bootstrap-and-promote.md` — per
   `CLAUDE.md` §1, do not begin without an explicit new implementation
   request; the plan file's retrieval-scope default needs explicit
   confirmation first (flagged in the plan itself).

The `CLAUDE.md` §6 release-promotion step now waits on Phase 8, not
Phase 6 — not actionable until both phases above are done.

Also still outstanding from before, unchanged by this session: Cargo
adapter validation blocked on no Rust toolchain (`decisions/0014`),
`extract_npm_symbols` untested against real-world `.d.ts` styles, and
`staleness.py`'s version parser has no real PEP 440/full-semver
correctness.

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
