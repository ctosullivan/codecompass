# Roadmap

Tracks every roadmap phase and its completion status. This file is kept
up to date **with every change that affects phase scope or status** — see
`CLAUDE.md` §2. Unlike `planning/CONTEXT.md` (which reflects only the
*current* phase in detail for session-resumption), this file is the
full-roadmap, at-a-glance view: what's done, what's next, what's still
just planned.

Status values: `not started` / `planned` (a `planning/phase-N-*.md` file
exists) / `in progress` / `done`.

## MVP (v0.1) — phases 0-6

One milestone (see `CLAUDE.md` §6): tagged/released only once phase 6 is
`done`, not after each individual phase.

| Phase | Name | Status | Plan file |
|---|---|---|---|
| 0 | Repository scaffolding | done | [`phase-0-repo-scaffolding.md`](phase-0-repo-scaffolding.md) |
| 1 | Core data models & config parsing | done | [`phase-1-core-data-models.md`](phase-1-core-data-models.md) |
| 2 | Ecosystem adapters (npm, Python, Cargo — Cargo unverified against real cargo output, decisions/0014) | done | [`phase-2-ecosystem-adapters.md`](phase-2-ecosystem-adapters.md) |
| 3 | Deterministic tree generation (FILETREE/DEPTREE) | done | [`phase-3-tree-generation.md`](phase-3-tree-generation.md) |
| 4 | `init`, `sync`, and `index` commands (deterministic path) | done | [`phase-4-sync-index-init.md`](phase-4-sync-index-init.md) |
| 5 | AI-gated gap analysis (`depth = full`), dual-audience output (technical + conversational overview, decisions/0012), `--budget`, FILETREE cross-linking | done | [`phase-5-gap-analysis.md`](phase-5-gap-analysis.md) |
| 6 | Staleness checking (`check`, `--strict`/`--fix`) | done | [`phase-6-staleness-checking.md`](phase-6-staleness-checking.md) |

**MVP done when:** a real project can run `init`, `sync`, and `check`
against real npm/Python/Cargo dependencies and get correct, useful
output. **All six MVP phases are now done** — the `CLAUDE.md` §6
release-promotion step (a dated `[Unreleased]` → version-tagged
`CHANGELOG.md` section) is a separate, explicit follow-up action, not
performed automatically as part of Phase 6's own closeout.

## Post-MVP

| Phase | Name | Status | Plan file |
|---|---|---|---|
| 7 | Zero-question bootstrap (bare `depcompass` auto-discovery, decisions/0017) & `promote` (reactive depth escalation, decisions/0018) — grounded-description FULL-depth generation (decisions/0019), tool-level Skill (decisions/0020), PyPI source-resolution fail-loud (decisions/0021); absorbs the former Phase 9 (Skills + Cursor export) and Phase 10 (`init` bulk-discovery refinement) rows below | planned | [`phase-7-bootstrap-and-promote.md`](phase-7-bootstrap-and-promote.md) |
| 8 | Single-vendor chat REPL | not started | — |
| 9 | Project-root-aware REPL routing (Tier 1 sourced from Phase 7's Skill descriptions, decisions/0013) + whole-project context + unconditional dependency rollup at session start (decisions/0012) + digest-exceeded escalation to the generated Skill folder (decisions/0013) | not started | — |
| 10 | Polish: PyPI publish, examples, docs site evaluation | not started | — |
| 11 | MCP server (`query_vendor`) | not started | — |

**Renumbering note (this table, dated to Phase 7's planning):** the
former Phase 9 ("Agent Skills export + Cursor `.mdc` export") and
Phase 10 (`init` bulk-discovery refinement) rows were removed — both are
fully absorbed into the new Phase 7 above, per `decisions/0017` and
`decisions/0018`. The former Phase 7 (REPL) and Phase 8 (REPL routing)
shifted to 8 and 9; former Phase 11/12 (polish, MCP) shifted to 10/11.
All shifted phases were `not started`, so this is a clean renumber, not
a rewrite of in-flight work.

## How this file is kept in sync

- Starting a phase: add its plan-file link here and flip status to
  `planned` or `in progress` in the same commit that adds
  `planning/phase-N-*.md` (per `CLAUDE.md` §1).
- Finishing a phase: flip status to `done` in the same commit that marks
  the phase's own plan file `done` (per `CLAUDE.md` §5's definition of
  done).
- Scope changes to any unstarted phase (a roadmap phase gets split,
  reordered, or redefined): update the relevant row(s) here in the same
  commit as whatever decision or ADR records the change.
- This table is the source of truth for "what phase are we on" — if it
  ever disagrees with `planning/CONTEXT.md`, treat that as a bug to fix
  immediately, not a discrepancy to reconcile later.
