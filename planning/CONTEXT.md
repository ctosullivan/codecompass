# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**MVP phases 0-6 are all complete (unchanged this session).** The
`CLAUDE.md` §6 release-promotion step (a dated `[Unreleased]` →
version-tagged `CHANGELOG.md` section, tagging the MVP milestone) still
has **not** been done — still a separate, explicit action.

**Phase 7: Zero-question bootstrap & promote — planned, not yet
implemented.** A separate planning session proposed redefining the
post-MVP direction: a zero-question deterministic bootstrap on bare
`depcompass`, a single reactive `promote <vendor>` command as the only
cost/confirmation point, and replacing `depth = FULL` generation's
mechanism. This session reconciled that proposal against actual repo
state (see below) and produced `planning/phase-7-bootstrap-and-
promote.md` plus five new ADRs. No code was changed.

## What was just completed

Reconciled an external design doc against the real repo state before
writing anything, per `CLAUDE.md` §1 and the doc's own instructions.
Reconciliation found the doc's central premise for reversing `depth =
FULL` generation was wrong: it assumed gap analysis (`decisions/0003`,
Phase 5) compares a dependency's source against the model's own
training-knowledge self-assessment. No such mechanism exists in this
repo — the real mechanism compares the vendor's API surface against the
consuming project's `context_path` (its README/spec), gated on
`context_path` being set. This was surfaced and resolved with the user
before drafting: the replacement (grounded description, sourced from
material retrieved at `promote` time) proceeds, but the new ADR's
rationale is the real one — `context_path` gating is an adoption
blocker and produces project-specific rather than vendor-general output
— not the mistaken training-knowledge framing.

Also found: the proposal's asks substantially overlap two already-
planned, not-started roadmap rows — former Phase 9 (Agent Skills +
Cursor `.mdc` export) and Phase 10 (`init` bulk-discovery refinement).
Both are folded into the new Phase 7 rather than left as separate rows;
`planning/ROADMAP.md` was renumbered accordingly (former Phase 7/8 →
8/9, former 11/12 → 10/11 — all were `not started`, so this was a clean
renumber).

Five new ADRs written: `decisions/0017` (zero-question bootstrap — bare
`depcompass` auto-discovers manifests, idempotent refresh on re-run),
`decisions/0018` (`promote <vendor>` as the sole cost-disclosure/
confirmation point, bundling source resolution + generation + Skill +
`.mdc` export + `index` refresh), `decisions/0019` (grounded description
replaces `context_path`-gated gap analysis for `FULL`-depth generation —
model tier, `decisions/0003`, unaffected), `decisions/0020` (a
templated, unconditionally-generated tool-level Skill distinct from
per-vendor Skills), `decisions/0021` (PyPI source resolution fails loud
rather than falling back to a tarball when no repository URL resolves).

`planning/phase-7-bootstrap-and-promote.md` written, covering source
resolution, retrieval scope (a proposed default flagged as needing
confirmation before implementation, per `CLAUDE.md` §1), CLI changes,
the `promote` command, the tool-level Skill, and a test plan. Notes one
open architectural question for the implementer: whether the existing
`vendor/<name>/src/` local-install snapshot (`decisions/0004`) and the
new upstream-repository retrieval for grounded description
(`decisions/0021`) should share a location on disk or stay separate.

## Decisions made this session not already captured in an ADR

- None beyond the five ADRs above — the retrieval-scope default and the
  `vendor/<name>/src/`-vs-new-retrieval-location question are recorded
  as open implementation questions in `planning/phase-7-bootstrap-and-
  promote.md`'s Design decisions section, not settled here.

## Next concrete step

**Two things remain undecided, same as before this session** (this
session added a plan for one path forward, it didn't choose between
them):
1. The `CLAUDE.md` §6 release-promotion step for the MVP 0-6 milestone.
2. Implementing `planning/phase-7-bootstrap-and-promote.md` — per
   `CLAUDE.md` §1, do not begin without an explicit new implementation
   request; the plan file's retrieval-scope default needs explicit
   confirmation first (flagged in the plan itself).

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
