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

## MVP (v0.2) — phases 9-19

A second milestone group (`decisions/0030`), grouped for the same reason
`decisions/0022` grouped 0-8: no phase in this range is a coherent,
shippable state on its own — the rework's payoff (SQLite graph +
generated Skills + `/discovery` as the primary interface, `promote`/
`Depth` fully retired) only exists once Phase 19 lands. **All eleven
phases (9-19) are now `done`.** Tagged/released only once phase 19 is
`done`, not after each individual phase — cutting the actual `v0.2` tag
remains a separate, not-yet-made decision (same posture `decisions/0022`
established for `v0.1`, which also remains untagged).

| Phase | Name | Status | Plan file |
|---|---|---|---|
| 9 | Rename to codecompass — mechanical only, zero behavior change (decisions/0029) | done | [`phase-9-rename-to-codecompass.md`](phase-9-rename-to-codecompass.md) |
| 10 | SQLite graph foundation — new `graph.py`: schema, `init_schema`, `rebuild_deterministic`, queries (library only, not CLI-wired yet) (decisions/0032) | done | [`phase-10-sqlite-graph-foundation.md`](phase-10-sqlite-graph-foundation.md) |
| 11 | Project-source usage detection — new `usage.py` (Python/npm/Rust import + symbol-level detection), wired into `sync.py`'s whole-project path | done | [`phase-11-project-source-usage-detection.md`](phase-11-project-source-usage-detection.md) |
| 12 | Doc & wide skill mapping — new `doc_mapping.py` (ports former 9c) + new `skill_scan.py` (project-wide `.claude/skills/**` indexing, not just codecompass-generated skills) | done | [`phase-12-doc-and-wide-skill-mapping.md`](phase-12-doc-and-wide-skill-mapping.md) |
| 13 | Universal source cloning — remove the `depth is FULL` gate in `sync.py`/`source_resolution.py`; clone every vendor by default (decisions/0033) | done | [`phase-13-universal-source-cloning.md`](phase-13-universal-source-cloning.md) |
| 14 | Batched enrichment (Phase B) — new `enrichment.py` replacing `grounded_description.py`; usage-scoped candidate selection, batched calls, CLAUDE.md-hash-line caching, reworked cost estimate | done | [`phase-14-batched-enrichment.md`](phase-14-batched-enrichment.md) |
| 15 | CLI rewire — `cli.py`: Phase A+B wiring, `promote` deleted, `query` command added, `check`/`index`/`skill.py` migrated to graph-backed data (decisions/0033) | done | [`phase-15-cli-rewire.md`](phase-15-cli-rewire.md) |
| 16 | Retire `Depth` — `core.py`/`config.py`/`discovery.py` shrink; legacy `depth=` tolerated on read (decisions/0031); `sync_vendor` reads enrichment from the graph and `grounded_description.py` is retired (decisions/0035) | done | [`phase-16-retire-depth.md`](phase-16-retire-depth.md) |
| 17 | `/discovery` slash command — new generated `.claude/commands/discovery.md`, read-only guided-exploration entry point, wired into the same generation points as the tool Skill | done | [`phase-17-discovery-slash-command.md`](phase-17-discovery-slash-command.md) |
| 18 | `undo` command — new `undo [--yes] [--dry-run]`, driven by the graph's origin-tagged artifacts + known fixed paths; root CLAUDE.md removal goes through the diff-approval flow (CLAUDE.md §0) | done | [`phase-18-undo-command.md`](phase-18-undo-command.md) |
| 19 | Chat demotion + governance docs — README/architecture rewritten around the graph+Skills+`/discovery` as primary; tool Skill stops featuring chat first (decisions/0034) | done | [`phase-19-chat-demotion-and-governance-docs.md`](phase-19-chat-demotion-and-governance-docs.md) |

**Renumbering note (dated to Phase 10's planning):** the original Phase
9-planning-session order placed "Retire `Depth`" second (as Phase 10),
ahead of everything that would replace its role. That's a dependency-order
bug caught before any Phase 10 code was written: `Depth` is read by eight
call sites (`sync.py`'s clone gate, `grounded_description.py`'s cost
estimate, `cli.py`'s `promote`, `index.py`/`skill.py`/`claude_md.py`'s
display columns, `chat.py`'s banner, `discovery.py`'s default) and none of
their replacements exist yet at that point in the sequence. Corrected:
"Retire `Depth`" moves to **Phase 16**, after phases 13-15 have replaced
every one of those call sites; the graph/usage-detection/cloning/
enrichment/CLI phases (formerly 11-16) shift down to **10-15**. Phases
17-19 (`/discovery`, `undo`, chat demotion) are unaffected. All shifted
phases were `not started`, so this is a clean renumber, not a rewrite of
in-flight work — same precedent condition as every renumbering note above.
**`decisions/0031`-`0034` (already written) contain a handful of internal
"Phase N" citations keyed to the pre-reorder numbering** (e.g. `0031`
says "Phase 12" for usage detection, now Phase 11; `0032` says "Phase 11"
for `graph.py`, now Phase 10, and "Phase 15" for the enrichment cache-key
mechanism, now Phase 14; `0033` says "Phase 16" for `promote`'s removal,
now Phase 15; `0034` says "Phase 16/19" for the tool Skill rewrite, now
"Phase 15/19") — not editable (append-only), so use this note to
translate old→new when cross-referencing them.

**MVP (v0.2) done when:** a real project can run bare `codecompass`
against real npm/Python/Cargo dependencies, get every vendor cloned and
deterministically documented for free, see usage-proven vendors
automatically enriched (with disclosed, confirmable cost), query the
resulting relationship graph via `codecompass query` or `/discovery`, and
cleanly `undo` everything if desired — all under the `codecompass` name,
with `promote`/`Depth` fully retired and chat re-framed as secondary.

## Post-MVP

| Phase | Name | Status | Plan file |
|---|---|---|---|
| 20 | Refresh generated artifacts after enrichment — fixes the graph/enrichment ordering gap found during this project's first live enrichment run: the routing table, tool Skill, and `undo`/`query skills`'s view of the graph lag one sync cycle behind a vendor's first enrichment | planned | [`phase-20-refresh-generated-artifacts-after-enrichment.md`](phase-20-refresh-generated-artifacts-after-enrichment.md) |
| 21 | Spec-doc detection & relationship graph — new `spec_docs.py` classifies a project's own README/`docs/`/`architecture/`/`decisions/` etc. as graph nodes; new `doc_relations_edges` mechanically links them to dependency docs and skills (mention heuristic, no AI call) | planned | [`phase-21-spec-doc-detection-and-relationship-graph.md`](phase-21-spec-doc-detection-and-relationship-graph.md) |
| 22 | AI-enriched cross-artifact relationships — batched AI summary of *how* each Phase 21 edge relates, gated on Phase 21's mechanically-proven candidates only, folded into the existing Phase B cost/consent flow; never writes to a spec doc's own file | planned | [`phase-22-ai-enriched-cross-artifact-relationships.md`](phase-22-ai-enriched-cross-artifact-relationships.md) |
| 23 | *(was 22, was 21, was 11, formerly 10)* Polish: PyPI publish as `codecompass`, examples, docs site evaluation — the v1.0 release itself | not started | — |
| 24 | *(was 21, was 20, was 10, formerly 9)* Project-root-aware REPL routing (Tier 1 sourced from generated Skill descriptions, decisions/0013) + whole-project context + unconditional dependency rollup at session start (decisions/0012, now demoted per decisions/0034) + digest-exceeded escalation to the generated Skill folder — now consumes the SQLite graph (decisions/0032) instead of inventing ad hoc heuristics — deferred past v1.0, see renumbering note below | not started | — |
| 25 | *(was 23, was 22, was 12, formerly 11)* MCP server (`query_vendor`) — deferred past v1.0, see renumbering note below | not started | — |

**Renumbering note (dated to `planning/v1.0-initial-release-roadmap.md`'s
planning session):** two new phases (21, "Spec-doc detection &
relationship graph" and 22, "AI-enriched cross-artifact relationships")
are inserted, requested alongside a path-to-v1.0 roadmap pass. Former
Phase 21 (routing/rollup) and Phase 22 (polish/PyPI publish) both shift —
but not by a uniform +2: Polish (formerly 22) moves to **23**, directly
after the two new phases, since it *is* the release itself and Phases
20-22 are all release blockers; routing/rollup (formerly 21) moves to
**24**, past the release line, on the reasoning that it enhances the
already-demoted `chat` REPL (decisions/0034) rather than the primary
`/discovery`/Skills interface, so it doesn't need to block v1.0 — see
`planning/v1.0-initial-release-roadmap.md`'s "Why this order" section for
the full reasoning (flagged there as a proposal, not a locked decision).
Former Phase 23 (MCP) shifts to **25**, unaffected in relative order but
renumbered by the two insertions ahead of it. All three shifted phases
were `not started`, so this is a clean renumber, not a rewrite of
in-flight work — same precedent condition as every renumbering note
below.

**Renumbering note (dated to this project's first live enrichment run):**
a new Phase 20 ("Refresh generated artifacts after enrichment") is
inserted ahead of the former Phase 20 (project-root routing/rollup),
which shifts to **21**; former 21/22 (polish, MCP) shift to **22/23**.
The new phase fixes a real, reproduced gap (see its plan file and
`planning/CONTEXT.md`'s account of the validation session that found it)
rather than being purely a planning reorganization like the earlier
renumbering notes below, but the mechanical effect on this table is the
same: all three shifted phases were `not started`, so this is a clean
renumber, not a rewrite of in-flight work.

**Superseded planning (dated to this rework's planning session):** the
former Post-MVP context-graph phases 9a-9e (`planning/
phase-9a-vendor-presence-graph.md` through `phase-9d-llm-enrichment.md`,
plus the never-planned 9e) are **superseded and their plan files
deleted** from the working tree (still recoverable from git history at
or before commit `a9969e4` if needed as a reference) — their design is
the closest existing source for Phase 11's SQLite schema and Phase
12/13's usage/doc-mapping modules, which port its content directly
rather than redesigning from scratch, but the files themselves no longer
need to stay on disk once that porting happens phase-by-phase. Their five
ADRs (`decisions/0024`-`0028`) are **not deleted** — append-only per
`CLAUDE.md` §2, unlike plan files. Their JSON-file storage model
(`decisions/0024`) is superseded by `decisions/0032`; their
optional/manually-promoted enrichment posture (`decisions/0026`) is
superseded by `decisions/0031`/`0033`'s usage-driven,
automatically-triggered model. Phase 9e's deferral condition
(`decisions/0028` — needs real field data from a 9d that will now never
ship in its originally planned form) is moot; usage-cluster
classification remains unplanned, now with no specific future phase
slot, revisit only if real need resurfaces.

**Renumbering note (this table, dated to this rework's planning
session):** the former Post-MVP table's Phase 9/10/11/12 renumbered to
**20/21/22** (routing/rollup, polish, MCP), making room for the new MVP
(v0.2) group (phases 9-19) above. All three were `not started`, so this
is a clean renumber, not a rewrite of in-flight work — same precedent
condition as the two renumbering notes below.

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
(This context-graph insertion is itself now superseded — see the
"Superseded planning" note above.)

**MVP-boundary note (dated to Phase 7-8's completion):** Phase 7 and
Phase 8 moved from this table into the MVP (v0.1) table above — per
`decisions/0022`, the MVP milestone now spans phases 0-8, not 0-6, since
Phase 8 (the REPL, `decisions/0012`'s "actual product") structurally
depends on Phase 7's outputs. No phase was renumbered by this move, only
its table membership.

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
