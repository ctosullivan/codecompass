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
| 2 | Ecosystem adapters (npm, Python, Cargo) | planned | [`phase-2-ecosystem-adapters.md`](phase-2-ecosystem-adapters.md) |
| 3 | Deterministic tree generation (FILETREE/DEPTREE) | not started | — |
| 4 | `sync` and `index` commands (deterministic path) | not started | — |
| 5 | AI-gated gap analysis (`depth = full`), `--budget` | not started | — |
| 6 | Staleness checking (`check`, `--strict`/`--fix`) | not started | — |

**MVP done when:** a real project can run `init`, `sync`, and `check`
against real npm/Python/Cargo dependencies and get correct, useful
output.

## Post-MVP

| Phase | Name | Status | Plan file |
|---|---|---|---|
| 7 | Single-vendor chat REPL | not started | — |
| 8 | Project-root-aware REPL routing + whole-project context | not started | — |
| 9 | Cursor `.mdc` export | not started | — |
| 10 | `init` bulk-discovery refinement | not started | — |
| 11 | Polish: PyPI publish, examples, docs site evaluation | not started | — |
| 12 | MCP server (`query_vendor`) | not started | — |

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
