# Roadmap

Tracks every roadmap phase and its completion status. This file is kept
up to date **with every change that affects phase scope or status** — see
`CLAUDE.md` §2. Unlike `planning/CONTEXT.md` (which reflects only the
*current* phase in detail for session-resumption), this file is the
full-roadmap, at-a-glance view: what's done, what's next, what's still
just planned.

Status values: `not started` / `planned` (a `planning/phase-N-*.md` file
exists) / `in progress` / `done`.

## MVP (v0.1) — phases 0-8

One milestone (see `CLAUDE.md` §6): tagged/released only once phase 8 is
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
| 7 | Zero-question bootstrap (bare `depcompass` auto-discovery, decisions/0017) & `promote` (reactive depth escalation, decisions/0018) — grounded-description FULL-depth generation (decisions/0019), tool-level Skill (decisions/0020), PyPI source-resolution fail-loud (decisions/0021); absorbs the former Phase 9 (Skills + Cursor export) and Phase 10 (`init` bulk-discovery refinement) rows | done | [`phase-7-bootstrap-and-promote.md`](phase-7-bootstrap-and-promote.md) |
| 8 | Single-vendor chat REPL (explicit `chat <vendor>` only; project-root routing is Phase 9) — grounds on persisted `CLAUDE.md`/`OVERVIEW.md` text, no digest regeneration (decisions/0023) | done | [`phase-8-chat-repl.md`](phase-8-chat-repl.md) |

**MVP done when:** a real project can run `init`, `sync`, `promote`, and
`check` against real npm/Python/Cargo dependencies, and query them via
`depcompass chat`, and get correct, useful output. **All eight MVP phases
(0-8) are now done.** The `CLAUDE.md` §6 release-promotion step (a dated
`[Unreleased]` → version-tagged `CHANGELOG.md` section) is now applicable
(`decisions/0022`) but cutting the `v0.1` tag is a separate, not-yet-made
decision — it is not implied by phase completion alone.

## Post-MVP

| Phase | Name | Status | Plan file |
|---|---|---|---|
| 9a | Context graph — vendor presence detection: `SourceFile`/`Vendor` nodes, vendor-level `uses` edges, dead-dependency detection surfaced via `check` (decisions/0024, decisions/0025) | planned | [`phase-9a-vendor-presence-graph.md`](phase-9a-vendor-presence-graph.md) |
| 9b | Context graph — symbol-level usage: upgrades `uses` to `SourceFile → Symbol`, reusing existing per-ecosystem symbol extraction | planned | [`phase-9b-symbol-usage-graph.md`](phase-9b-symbol-usage-graph.md) |
| 9c | Context graph — doc & Skill mapping: `DocArtifact` nodes, `documents`/`routes_via`/`depends_on` edges, coverage-gap reporting via `check` (decisions/0013 point 6 made concrete as real data) | planned | [`phase-9c-doc-skill-mapping.md`](phase-9c-doc-skill-mapping.md) |
| 9d | Context graph — optional LLM enrichment: usage-purpose labels, clustering, `DOCUMENTS` quality delta, file-role summaries, `EXPLAINS` chunk retrieval, trigger-accuracy proxy; off by default, separately cost-disclosed (decisions/0026, decisions/0027) | planned | [`phase-9d-llm-enrichment.md`](phase-9d-llm-enrichment.md) |
| 9e | Usage-cluster classification + draft (never auto-written) project-level Skill suggestion — deliberately deferred until 9d ships real field data (decisions/0028) | not started | — |
| 10 | *(was 9)* Project-root-aware REPL routing (Tier 1 sourced from Phase 7's Skill descriptions, decisions/0013) + whole-project context + unconditional dependency rollup at session start (decisions/0012) + digest-exceeded escalation to the generated Skill folder (decisions/0013) — now consumes 9a-9d's context graph instead of inventing ad hoc heuristics | not started | — |
| 11 | *(was 10)* Polish: PyPI publish, examples, docs site evaluation | not started | — |
| 12 | *(was 11)* MCP server (`query_vendor`) | not started | — |

**Renumbering note (this table, dated to Phase 7's planning):** the
former Phase 9 ("Agent Skills export + Cursor `.mdc` export") and
Phase 10 (`init` bulk-discovery refinement) rows were removed — both are
fully absorbed into the new Phase 7 above, per `decisions/0017` and
`decisions/0018`. The former Phase 7 (REPL) and Phase 8 (REPL routing)
shifted to 8 and 9; former Phase 11/12 (polish, MCP) shifted to 10/11.
All shifted phases were `not started`, so this is a clean renumber, not
a rewrite of in-flight work.

**Renumbering note (this table, dated to the Phase 9 context-graph
planning session):** the context graph (9a-9e) is inserted as the new
Phase 9, ahead of the routing/rollup work — it supplies that work with
real usage/doc-mapping data instead of the routing phase inventing ad
hoc heuristics inline. The former Phase 9 (routing/rollup) shifts to
**10**; former 10/11 (polish, MCP) shift to **11/12**. All shifted
phases were `not started`, so this is again a clean renumber, not a
rewrite of in-flight work — same precedent condition as the note above.

**MVP-boundary note (dated to this change):** Phase 7 and Phase 8 moved
from this table into the MVP table above — per `decisions/0022`, the MVP
milestone now spans phases 0-8, not 0-6, since Phase 8 (the REPL,
`decisions/0012`'s "actual product") structurally depends on Phase 7's
outputs. No phase was renumbered by this move, only its table
membership.

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
