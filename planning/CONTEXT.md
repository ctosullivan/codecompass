# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 5: AI-gated gap analysis — planned (plan file written, not yet
implemented).** MVP phases 0-4 are done; Phase 5 is the next
implementation target, followed by Phase 6 (staleness checking) to close
out the MVP milestone.

## What was just completed

Wrote and reviewed `planning/phase-5-gap-analysis.md` (plan-only session,
per `CLAUDE.md` §1 — mirrors the Phase 2-4 plan-writing sessions'
precedent). Scope: a new `gap_analysis.py` module making the one AI call
in depcompass (`depth = full` + `context_path` vendors only), using
forced tool-use for structured dual-audience output (technical block for
`CLAUDE.md`, conversational overview for a new `vendor/<name>/OVERVIEW.md`
that Phase 8's REPL rollup will later consume, per `decisions/0012`).
`VendorDigest` gains `conversational_overview`/`gap_analysis_error`
fields. `sync.py`/`claude_md.py` are updated to wire it in, with per-
vendor failures caught locally (deterministic output still written,
`sync` exits non-zero overall) and a `--budget` pre-flight check that
aborts the whole run before any API call if projected cost is too high.
Phase 5 also closes Phase 3's deferred FILETREE-cross-linking loop via a
new optional `action_pointer` parameter on `filetree.py`'s renderers.

Four design questions were resolved via user interview before finalizing
the plan, all matching the recommended option: pin the model to a dated
Haiku 4.5 snapshot rather than `decisions/0003`'s rolling alias; `--budget`
overruns abort the whole run rather than partially processing; a single
vendor's AI failure doesn't abort the batch; and Phase 5 (not some later,
unowned phase) implements FILETREE cross-linking. `planning/ROADMAP.md`
and `CHANGELOG.md` updated in the same commit as the plan file, per
`CLAUDE.md` §1/§2/§3. **No gap-analysis code has been implemented yet** —
that's a separate, later session.

**Real cost implication flagged for implementation time**: gap analysis
is fully regenerated on every `sync` run for a `depth = full` +
`context_path` vendor, not cached — consistent with Phase 4's "always
fully overwritten" design applied to the one step that now costs real
money each time. Must be disclosed in docs, not silently inherited.

## Decisions made this session not already captured in an ADR

- None yet — all of this session's design decisions (model pinning,
  `--budget` behavior, per-vendor failure handling, FILETREE
  cross-linking scope, structured-output mechanism, `OVERVIEW.md`
  persistence, `context_path` truncation, cost-estimate approach) are
  recorded in `planning/phase-5-gap-analysis.md`'s Design decisions
  section. One of them — the no-live-API-call testing strategy — is
  slated to become a new ADR (number confirmed against actual repo state)
  once implementation actually happens, per the plan file's Same-commit
  doc updates list.

## Next concrete step

Implement `planning/phase-5-gap-analysis.md`: `gap_analysis.py` + tests
first (the seam and budget/cost logic everything else depends on), then
the `core.py`/`filetree.py` additions + their tests, then `sync.py`
wiring + tests (including the new `OVERVIEW.md` output), then
`claude_md.py`'s Gap analysis section + tests, then `cli.py`'s
`--budget` + tests, then the new ADR, then the doc/changelog/context
closeout — same commit-per-logical-change pattern as Phases 0-4.

**Still outstanding, not a Phase 5 blocker but worth remembering**: once
a Rust toolchain is available anywhere in the pipeline, `decisions/0014`
requires validating the Cargo adapter's fixture assumptions and regex-
based `pub` extraction against real `cargo metadata` output and a real
crate — currently entirely unverified. `extract_npm_symbols` (Phase 3) is
also still untested against real-world `.d.ts` authoring styles beyond
hand-written fixtures.
