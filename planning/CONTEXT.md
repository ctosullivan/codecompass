# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 7: Zero-question bootstrap & promote — done. MVP phases 0-7 are
complete** (MVP spans 0-8, `decisions/0022`). Phase 8 (single-vendor chat
REPL) is not started — it has no `planning/phase-8-*.md` yet; that plan
file needs writing, per `CLAUDE.md` §1, before its implementation can
start. The `CLAUDE.md` §6 release-promotion step (a dated `[Unreleased]`
→ version-tagged `CHANGELOG.md` section) still has **not** been done — it
waits on Phase 8, not Phase 7.

## What was just completed

Implemented `planning/phase-7-bootstrap-and-promote.md` in full. Bare
`depcompass` (no subcommand, Typer `invoke_without_command`) auto-
discovers manifests (`package.json`, `pyproject.toml`, `requirements.txt`
— new parser — `Cargo.toml`), writes/refreshes `vendor.toml` at `depth =
surface` with no prompts or AI calls, and regenerates trees + the root
routing table + a new unconditional tool-level Skill
(`depcompass.skill.write_tool_skill`, `decisions/0020`). Refreshing an
already-bootstrapped project only syncs newly-discovered vendors —
already-tracked ones, including any at `depth = full`, are left
untouched, so the command never pays AI cost.

New `depcompass promote <vendor> [--yes]`: the sole cost-disclosure/
confirmation point (`decisions/0018`). On confirmation it rewrites
`vendor.toml`'s depth to `full` (`discovery.rewrite_vendor_toml`, new),
runs `sync_vendor` (which now resolves and clones the vendor's real
upstream repository — `depcompass.source_resolution`, `decisions/0021`
— and generates a grounded description — `depcompass.
grounded_description`, replacing `gap_analysis.py`, `decisions/0019`),
writes that vendor's per-vendor Skill and Cursor `.mdc` export
(`depcompass.skill`, `decisions/0013`), and refreshes the routing table
and tool-level Skill. Idempotent on an already-`full` vendor.

`context_path` was removed from `VendorConfig`/`vendor.toml` entirely —
grounded-description generation is unconditional for every `depth =
full` vendor, no longer gated on a project-supplied field. `VendorDigest`
gained `technical_description`/`description_error` (renamed from
`gap_analysis`/`gap_analysis_error`); `conversational_overview` and
`action_pointer_file`/`action_pointer_note` are unchanged in shape.
`vendor/<name>/src/` is now cloned from the vendor's own upstream
repository for `depth = full` vendors (a refinement of `decisions/0004`'s
snapshot-not-reference concern, not a reversal), falling back to the old
local-install-sourced copy if source resolution fails; if cloning
succeeds but generation fails, the real clone is kept rather than
discarded for the fallback — a nested try/except in `sync_vendor`, not a
flat one.

Each adapter gained `repository_url()` (`decisions/0021`), resolved from
already-local package metadata, no registry network call: npm reads
`package.json`'s `repository` field (string, `git+`-prefixed, or
`github:`-shorthand, all normalized; an object form's `directory` key
respected for monorepo packages); Python reads installed `Project-URL`
metadata entries, checking key-variant labels in priority order; Cargo
reads `cargo metadata`'s package-level `repository` field (no
`directory` equivalent — a known, accepted limitation for workspace
crates). A PyPI vendor with no resolvable URL fails `promote` loudly
rather than falling back to a source tarball.

Same-commit docs updated: `docs/config-schema.md` and
`docs/cli-reference.md` (bare `depcompass`, `promote`, `context_path`
removal), `architecture/overview.md` (Core data model, Adapter interface,
Tree generation, the renamed Grounded description section, Per-vendor
CLAUDE.md structure, Two consumption modes, Multi-tool export,
Retrofitting to existing projects, Cost model, Known footguns —
extensively updated throughout), `README.md` (Status, Core idea, Quick
example, How it works), `planning/ROADMAP.md` (Phase 7 → done),
`CHANGELOG.md`.

**Verification**: `pytest` reports 207 passed, 1 skipped (Cargo live
smoke test, unchanged since Phase 2), up from 162 at the end of Phase 6;
`ruff check .` is clean. Bare bootstrap and its idempotent refresh were
manually verified end-to-end in a scratch directory. Source resolution
and cloning were manually verified against a real repository (`pytest`,
resolved via its real PyPI metadata, cloned with real `git`) — confirmed
working outside of fixtures. The AI call itself
(`generate_grounded_description`) was **not** exercised against the live
Anthropic API this session, matching `decisions/0016`'s existing posture
and this project's caution around agents autonomously incurring real
spend — see **Still outstanding** below.

## Decisions made this session not already captured in an ADR

- None — `decisions/0017`-`0021` (written in the prior planning session)
  already cover this implementation; the two open questions those ADRs'
  originating plan flagged (retrieval scope, `vendor/<name>/src/`
  location) were resolved via `AskUserQuestion` before implementation
  began and are recorded in `planning/phase-7-bootstrap-and-promote.md`'s
  Status section, not as new ADRs (neither reverses a prior decision).

## Next concrete step

**MVP phases 0-7 are complete.** The two things that could reasonably
come next, neither decided yet:
1. Planning Phase 8 (single-vendor chat REPL) — per `CLAUDE.md` §1,
   would need its own `planning/phase-8-*.md` written and approved
   before any implementation starts. Depends on Phase 7's Skill/
   grounded-description output, which now exists.
2. The `CLAUDE.md` §6 release-promotion step doesn't apply yet — it
   waits on Phase 8, per `decisions/0022`.

Neither has been started or requested yet — surface both as open options
next session rather than assuming which one the user wants first.

**Still outstanding, not a blocker but worth remembering**:
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter's fixture
  assumptions (including the new `repository_url()`) and regex-based
  `pub` extraction against real `cargo metadata` output and a real crate
  — currently entirely unverified, and `promote`'s end-to-end flow
  against a real Cargo vendor is likewise untested.
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `depcompass.grounded_description` (Phase 7) has never been run against
  the real Anthropic API in this environment — a human must do this
  manually at least once before trusting output quality
  (`decisions/0016`), the same gap Phase 5 accepted for `gap_analysis.py`.
- `staleness.py`'s custom version parser (Phase 6) has no real PEP 440 or
  full-semver correctness — flag if it misclassifies a real-world version
  string once used against real projects.
- A formal trigger-accuracy evaluation harness for per-vendor Skills
  (decisions/0013's Consequences) was not built in Phase 7 — Skill
  generation itself works and is tested, but nothing automatically
  verifies a generated trigger description actually fires on relevant
  questions.
- Cursor `.mdc` export has no `globs` field (description-based relevance
  only) — glob scoping to wherever a vendor is actually imported in the
  consuming codebase is a documented future refinement, not implemented.
