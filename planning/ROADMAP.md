# Roadmap

Tracks every roadmap phase and its completion status. This file is kept
up to date **with every change that affects phase scope or status** — see
`CLAUDE.md` §2. Unlike `planning/CONTEXT.md` (which reflects only the
*current* phase in detail for session-resumption), this file is the
full-roadmap, at-a-glance view: what's done, what's next, what's still
just planned.

Status values: `not started` / `planned` (a `planning/phase-N-*.md` file
exists) / `in progress` / `done` / `deferred` (on the roadmap, not
scheduled — revisit trigger named in the row) / `superseded` (replaced by
a later decision — ADR named in the row).

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
| 20 | Refresh generated artifacts after enrichment — fixes the graph/enrichment ordering gap found during this project's first live enrichment run: the routing table, tool Skill, and `undo`/`query skills`'s view of the graph lag one sync cycle behind a vendor's first enrichment | done | [`phase-20-refresh-generated-artifacts-after-enrichment.md`](phase-20-refresh-generated-artifacts-after-enrichment.md) |
| 21 | Spec-doc detection & relationship graph — new `spec_docs.py` classifies a project's own README/`docs/`/`architecture/`/`decisions/` etc. as graph nodes; new `doc_relations_edges` mechanically links them to dependency docs and skills (mention heuristic, no AI call) (decisions/0037) | done | [`phase-21-spec-doc-detection-and-relationship-graph.md`](phase-21-spec-doc-detection-and-relationship-graph.md) |
| 22 | AI-enriched cross-artifact relationships — batched AI summary of *how* each Phase 21 edge relates, gated on Phase 21's mechanically-proven candidates only, folded into the existing Phase B cost/consent flow; never writes to a spec doc's own file (decisions/0038) | done | [`phase-22-ai-enriched-cross-artifact-relationships.md`](phase-22-ai-enriched-cross-artifact-relationships.md) |
| 23 | *(was 22, was 21, was 11, formerly 10)* Polish: examples, docs-site evaluation, packaging readiness (decisions/0039). **Part A done.** Part B (the PyPI publish) is **superseded** by the v1 redefinition (`decisions/0048`) — CodeCompass publishes nothing until the redefined v1 (Phase 67, gate G2-b). | Part A done; Part B superseded | [`phase-23-polish-and-pypi-publish.md`](phase-23-polish-and-pypi-publish.md) |
| 24 | *(was 21, was 20, was 10, formerly 9)* Project-root-aware REPL routing + whole-project context + dependency rollup at session start (decisions/0012, demoted per decisions/0034) — **deferred** (`decisions/0048`); revisit as a redefined-v1 Stage C candidate only if reference-project evidence shows project-root context routing is a recurring need. **Not renumbered.** | deferred | — |
| 25 | *(was 23, was 22, was 12, formerly 11)* MCP server (`query_vendor`) — **deferred** (`decisions/0048`); revisit post-redefined-v1, informed by real CLI/Skill usage. **Not renumbered.** | deferred | — |
| 26 | Symbol-level resolution for `module.attr` usage — `usage.detect_python_imports` currently only resolves `from X import Y`-style usage to a symbol; a plain `import X` followed by `X.Attr(...)` (this project's own dominant style for `anthropic`) stays vendor-level-only, causing real used symbols to show as "documented but unused" in `check` | done | [`phase-26-symbol-level-resolution-for-attribute-usage.md`](phase-26-symbol-level-resolution-for-attribute-usage.md) |
| 27 | Register embedded vendor docs — a cloned vendor's own upstream README/CHANGELOG/CONTRIBUTING etc. (confirmed real content under `vendor/*/src/` in this repo) currently has no `doc_artifacts` row at all, so none of Phase 21/22's relationship detection/enrichment ever applies to them (decisions/0041) | done | [`phase-27-register-embedded-vendor-docs.md`](phase-27-register-embedded-vendor-docs.md) |
| 28 | Center relationship excerpts on the actual match — `relation_enrichment.select_candidates` always sends the spec doc's first 4,000 characters, regardless of where the mechanical match actually is; confirmed with real data from this repo that both currently-enriched vendor-doc relationships got ungrounded AI summaries because the real match sits far past that window (decisions/0042) | done | [`phase-28-center-relationship-excerpts-on-the-actual-match.md`](phase-28-center-relationship-excerpts-on-the-actual-match.md) |
| 29 | Vendor docs as relationship sources — `build_documents_edges` currently excludes `vendor_doc` rows entirely (a vendor's own README never documents its own symbols), and `build_doc_relations_edges` only ever scans spec docs outward, never a vendor doc's own content, found via direct user observation during a `/discovery` session (decisions/0043, supersedes decisions/0041's "never a relation source" claim) | done | [`phase-29-vendor-docs-as-relationship-sources.md`](phase-29-vendor-docs-as-relationship-sources.md) |
| 30 | Expose vendor/doc → package-code traversal in the query layer — `vendor_profile`/`symbol_profile` currently collapse `uses_edges`' existing file/line data to a bare `usage_count`; this phase surfaces it as a `used_at` list and adds a new `graph.doc_code_trace` two-hop query (`documents_edges`/`doc_relations_edges` → `uses_edges`) — query-time join only, no new tables, no AI. Confirmed live: `query symbol Console`'s `used_at` matches real import-line locations in this repo; `query relations architecture/overview.md`'s new "Package code" section lists real `typer` call sites | done | [`phase-30-bidirectional-code-traversal.md`](phase-30-bidirectional-code-traversal.md) |
| 31 | Typed relation kinds for AI-enriched doc relations — a closed `relation_label` enum (`documents_configuration_of`/`explains_usage_of`/`contrasts_with`/`supersedes`/`other`) added alongside Phase 22's existing free-text `ai_summary`, strictly gated on Phase 21/29's already-mechanically-proven candidates — no new candidate discovery, `decisions/0031`'s boundary held (decisions/0045). Confirmed live: a real re-enrichment run against this repo's 39 real relationships populated a valid label on every row (0 NULL/invalid), 2 spot-checked labels confirmed grounded against the real decision text | done | [`phase-31-typed-relation-enrichment.md`](phase-31-typed-relation-enrichment.md) |
| 32 | Heading-based doc chunking — deterministic heading-boundary split of markdown doc artifacts into a new `doc_chunks` table; nullable, additive `chunk_id` on `documents_edges`/`doc_relations_edges` sharpens Phase 30's trace output and Phase 31/28's enrichment excerpt precision without changing existing whole-doc fallback behavior (decisions/0046). Confirmed live: chunked `architecture/overview.md`'s real ~1,600 lines correctly; a real enrichment excerpt now slices exactly from its matched chunk; the Phase 28 fallback and Phase 29 self-mention exclusion both confirmed still correct under the new per-chunk pass | done | [`phase-32-doc-chunking.md`](phase-32-doc-chunking.md) |
| 33 | Fix invalid JSON from `query --json`'s Rich line-wrapping — every `--json` call site printed pre-serialized JSON through the shared Rich `Console`, which word-wraps long text by inserting real line breaks; a value long enough to cross the wrap width got a literal newline inserted into it, corrupting the JSON. Confirmed live against this repo's own `query vendor anthropic --json`. Found via the same `/discovery` session that surfaced Phases 30-32; the session's other flagged item (a version-drift reading that looked backwards) was investigated and confirmed **not** a bug — `check`'s "live" column reads the currently-installed version in this environment, not a PyPI-latest lookup, and this repo's `.venv` genuinely has an older `anthropic` installed than what was last recorded | done | [`phase-33-fix-query-json-line-wrapping.md`](phase-33-fix-query-json-line-wrapping.md) |
| 34 | Fix `doc_chunking`'s heading detection inside fenced code blocks — a `#`-prefixed comment inside a ` ``` `/`~~~` fence (e.g. example shell/Python code) was misdetected as a real markdown heading, corrupting `heading_path`. Found via a `/discovery` session testing Phase 30-33's real output; scanning all 84 chunkable doc artifacts found 37 false-positive lines, 12 of which had already produced bogus headings on `vendor/anthropic/src/MIGRATION.md`'s real `documents_edges` rows. Fixed by tracking fence state; no backfill, the next `sync` recomputes `doc_chunks` from scratch | done | [`phase-34-fix-chunking-fenced-code-blocks.md`](phase-34-fix-chunking-fenced-code-blocks.md) |
| 35 | User-facing docs rewrite + `ai-docs/` folder — `README.md` gains a real Setup section (Python version, `git`, `ANTHROPIC_API_KEY`) and a standalone "AI enrichment vs. no-AI usage" explainer reusing `examples/README.md`'s real transcript; new `ai-docs/README.md` (capability/boundary overview with example prompts, each "does NOT do" claim traced to a real ADR) and `ai-docs/CLAUDE.md` (agent entrypoint, distinct from root `CLAUDE.md`); `CONTRIBUTING.md`'s stale closing line removed. Requested directly by the user, not found via `/discovery` | done | [`phase-35-user-facing-docs-and-ai-docs.md`](phase-35-user-facing-docs-and-ai-docs.md) |
| 36 | Maintainer-only docs-sync script + skill — new `scripts/check_user_docs.py` (outside `src/codecompass/`, not a shipped feature, per explicit user decision) mechanically flags drift between this repo's own hand-authored docs and its own code (CLI command coverage in `docs/cli-reference.md`, README phase-count consistency with ROADMAP, `ANTHROPIC_API_KEY` mention, `VendorConfig` field coverage in `docs/config-schema.md`, `ai-docs/` file presence); new `.claude/skills/docs-sync/SKILL.md` instructs an agent to run it and fix findings by judgment, never mechanically. Confirmed live: running it against this repo today reports zero findings. Depends on Phase 35 (checks what it creates) | done | [`phase-36-docs-sync-tooling.md`](phase-36-docs-sync-tooling.md) |
| 37 | Register `ai-docs/` in spec-doc detection — `spec_docs._DEFAULT_GLOBS` had no entry for `ai-docs/`, found live via this repo's own dogfooding sync right after Phase 35 created `ai-docs/README.md`/`ai-docs/CLAUDE.md`: `query relations ai-docs/README.md` errored "not found in context-graph.db". Added `"ai-docs/**/*.md"` to the fixed glob set — the module's own comment says it stays fixed "until a real project shows it's wrong for it," and this repo just did. Confirmed live: both files now resolve in `query relations` | done | [`phase-37-ai-docs-spec-doc-detection.md`](phase-37-ai-docs-spec-doc-detection.md) |
| 38 | Final polish: redundancy cleanup — a 5-category redundancy/dead-code audit (dead references to retired `Depth`/`promote`/`grounded_description`, duplicate logic, unused/unpinned deps, doc staleness, test overlap) found `cli.py` had two verbatim-duplicate error blocks and a 6-times-repeated graph-connection open/close scaffold (both extracted into `_not_found_error`/`_graph_session`); `vendor.toml` had 4 dead leftover `depth = "surface"` lines from the retired `Depth` field (stripped); `pyproject.toml`'s 4 runtime deps had zero version pins (given lower bounds, `decisions/0047`, verified safe against `anthropic`'s real 1.0.0 breaking release). The word-boundary mention-regex duplication across `doc_mapping.py`/`skill_scan.py`/`relation_enrichment.py` was investigated and deliberately left as-is per `decisions/0038`'s existing small-module precedent. Requested directly by the user | done | [`phase-38-final-polish-redundancy-cleanup.md`](phase-38-final-polish-redundancy-cleanup.md) |

**Renumbering note:** none — 30/31/32 are appended after 29, keeping the
numbering already assigned in `planning/doc-graph-precision-roadmap.md`
(the umbrella doc for this group). Order is fixed 30 → 31 → 32 by
dependency: 31 doesn't hard-depend on 30 but is written to ship after it;
32 hard-depends on both being `done`, since it modifies files both touch
— see the umbrella doc's "Why this order" section for the full reasoning.

> **"v1.0" in every scope note below now means the *foundation release*,
> superseded by the v1 redefinition (Phase 39, `decisions/0048`).** The
> notes are accurate dated records of what was decided at the time and
> are **not edited** (same treatment superseded ADRs get). What they call
> "Phase 23 Part B (the actual PyPI publish, paused)" is now superseded:
> per gate G2-b, CodeCompass publishes nothing until the redefined v1
> (Phase 67). Phases 24/25's "deferred past v1.0" still holds — see the
> "Redefined CodeCompass v1" section below and
> [`v1-redefinition/roadmap.md`](v1-redefinition/roadmap.md).

**v1.0 scope note (dated to this planning session):** at explicit user
request, Phases 30-32 (doc-graph precision: bidirectional traversal,
typed relation labels, heading-based chunking) were added to v1.0's
blocking scope, alongside Phase 23. **All three (plus Phase 33, a bug fix
found along the way) are now `done`** — Phase 23 Part B (the actual PyPI
publish, already paused pending explicit user confirmation per
`planning/CONTEXT.md`) no longer waits on anything from this group; the
"don't re-release almost immediately after" reasoning
`planning/v1.0-initial-release-roadmap.md` used to order Phases 20-22
ahead of 23 originally is satisfied. Phases 24/25 (routing/rollup, MCP)
remain deferred past v1.0, unaffected by this — that document's own open
reordering question (whether they should block v1.0 instead) is still
unresolved and orthogonal to this group.

**v1.0 scope note (dated to Phase 35/36's planning session):** at explicit
user request, Phases 35-36 (user-facing docs rewrite + `ai-docs/` folder;
maintainer-only docs-sync tooling) were added to v1.0's blocking scope,
alongside Phase 23 and the now-`done` 30-33 group above. **Both are now
`done`** — Phase 23 Part B (the actual PyPI publish, already paused pending
explicit user confirmation) no longer waits on anything from this pair.
Unlike 30-33, this pair wasn't found via `/discovery` dogfooding — requested
directly by the user, motivated by `README.md` lacking a real setup/AI-usage
explainer and no agent-facing project overview existing anywhere. Phases
24/25 remain deferred past v1.0, unaffected.

**v1.0 scope note (dated to Phase 38's planning session):** at explicit user
request, Phase 38 (final polish: redundancy cleanup) was added to v1.0's
blocking scope, alongside Phase 23 and the now-`done` 30-37 group above.
**Phase 38 is now `done`** — Phase 23 Part B (the actual PyPI publish,
already paused pending explicit user confirmation) no longer waits on
anything from it. Requested directly by the user as a pre-release polish
pass, not found via `/discovery` dogfooding. Phases 24/25 remain deferred
past v1.0, unaffected.

**Renumbering note:** none — 26/27 are appended after the existing 24/25
(routing/rollup, MCP) rather than inserted ahead of them. Both were found
via a `/discovery` dogfooding session *after* v1.0's own phases (20-23)
were already planned/underway, are independent, non-blocking improvements
to already-shipped Phase 12/21/22 mechanisms, and don't affect the
reasoning behind 24/25's deferral-past-v1.0 placement — no reason to
reorder phases that were already `not started`.

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

## Redefined CodeCompass v1 — Stages A–G (phases 39–70)

**Planning package:** [`v1-redefinition/`](v1-redefinition/) (umbrella,
same role `v1.0-initial-release-roadmap.md` played for 20–23, larger
scope). This milestone group **redefines what "CodeCompass v1" means** —
from a packaging milestone (publish the npm/PyPI/Cargo package-source
tool) to a *product-validation* milestone: CodeCompass developed
agent-led, validated against real external reference-project work
(**Ledgerkit, then Technical Clipper** — reordered 2026-09-12, see
below), improved from that evidence, generalised only as far as evidence
justifies, released after a blank-slate documentation reconstruction and
an independent audit. Full rationale:
[`v1-redefinition/README.md`](v1-redefinition/README.md);
`decisions/0048`, `0049`.

**Ratified by Phase 39 (2026-09-09).** Gates G1 (`pyproject.toml` →
`1.0.0.dev0`), G2 (→ G2-b: **hold all publishing until the redefined v1**
— CodeCompass has never been published; the first-ever PyPI release is
the redefined v1 as `1.0.0` at Phase 70), G3 (this restructuring), and G5
(ADRs 0048/0049) are decided. Phases 0–38 and 24/25 are **not**
renumbered. Historical tables and "v1.0 scope notes" above are unchanged
(dated records); the note before them reframes "v1.0" → "foundation
release".

**Realigned by the 2026-09-12 reassessment**
([`v1-redefinition/realignment-2026-09.md`](v1-redefinition/realignment-2026-09.md)) —
**gates G11, G12, G13 all approved** ("Proceed as recommended",
2026-09-12): Ledgerkit becomes Stage B/D (was Stage D only, second);
Technical Clipper becomes a new Stage F, later. Phases 39–43c are
unchanged/`done`/not renumbered; phases 45–67 (none started) are
renumbered 45–70 to make room for the new Stage F. Two new Stage-A
bridge phases, both **done**: **43d** (GPL-3.0-or-later relicensing —
`decisions/0053`) and **43e** (reusable agent-led adoption blueprint).
`decisions/0052` (the reorder) is also `Accepted`.

Gate **G4** (`CLAUDE.md` §8/§5/§1/§6 changes for the agent-led model) was
approved and applied in **Phase 40** (2026-09-09), mirrored into
`CONTRIBUTING.md` — see
[`v1-redefinition/proposed-governance-changes.md`](v1-redefinition/proposed-governance-changes.md).
A follow-on `CLAUDE.md` §5 amendment (two more DoD conditions — a
lead-authored phase retro in `planning/retros/`, and a per-phase
independent `docs-reconstructor` drift audit) was approved 2026-09-10 and
applied in **Phase 41**, mirrored into `CONTRIBUTING.md`; `decisions/0050`
records both mechanisms.

Milestone-grouping convention (`CLAUDE.md` §6, `decisions/0022`/`0030`):
Stages A–G are **one milestone group**; the `v1.0.0` tag/release is cut
only on group completion (Phase 70), not per phase.

Stage labels: **COMMITTED** (will happen; only a §7 gate stops it) /
**EXPERIMENTAL** (activity committed, findings not) / **CONDITIONAL** (on
a named gate; may be dropped) / **DEFERRED** (revisit trigger named).

| Phase | Name | Label | Status | Plan file |
|---|---|---|---|---|
| 39 | Reconcile repo state + versioning realignment | COMMITTED | done | [`phase-39-reconcile-v1-redefinition.md`](phase-39-reconcile-v1-redefinition.md) |
| 40 | Specialist agent roster + lead workflow | COMMITTED | done | [`phase-40-specialist-agents.md`](phase-40-specialist-agents.md) |
| 41 | Project-learning lifecycle + phase retros + per-phase docs-drift gate | COMMITTED | done | [`phase-41-learning-lifecycle.md`](phase-41-learning-lifecycle.md) |
| 42 | Documentation lifecycle (incremental + closeout gate) | COMMITTED | done | [`phase-42-documentation-lifecycle.md`](phase-42-documentation-lifecycle.md) |
| 43 | Dogfood the agent-led loop on a real change (`query skills` widen — [`43a`](phase-43a-query-skills-widen-kinds.md)) — **GATE DA passed** (roster stays at 7, no pruning, 4 amendments + `43b`) | COMMITTED | done | [`phase-43-dogfood-agent-led-workflow.md`](phase-43-dogfood-agent-led-workflow.md) |
| 43b | Two `check_user_docs.py` rules from GATE DA (deleted-names-as-live; generated-artifacts-match-source) — runs before Phase 44 | COMMITTED | done | [`phase-43b-standing-doc-drift-checks.md`](phase-43b-standing-doc-drift-checks.md) |
| 43c | Stage A→B bridge: agent context-suggestion capture pathway (`planning/context-gaps/`), context-vs-default-pathway eval per use (`context-use-log.md`), context-health planning (`context-health.md` + `context-health-planner`, the roster's 8th agent — user-approved Option A; GATE DA's "roster stays at 7" was about pruning, not a cap on adding). Capture + evidence only — **no `src/` change** (that's Stage C/E, gated). `decisions/0051`. | COMMITTED | done | [`phase-43c-agent-context-pathways.md`](phase-43c-agent-context-pathways.md) |
| 43d | GPL-3.0-or-later relicensing (aligns with `hledger`'s own confirmed licence) — **gate G12 approved**, `LICENSE`/`pyproject.toml`/`README.md`/`CONTRIBUTING.md` updated, `decisions/0053` Accepted | COMMITTED | done | [`phase-43d-gpl-relicensing-plan.md`](phase-43d-gpl-relicensing-plan.md) |
| 43e | Reusable agent-led adoption blueprint (`adoption-blueprint.md`) — **gate G13 approved** | COMMITTED | done | [`phase-43e-agent-led-adoption-blueprint.md`](phase-43e-agent-led-adoption-blueprint.md) |
| 44 | Reference-project protocol + context-quality eval spec (project-agnostic; retargeted to write Phase 45's Ledgerkit plan) | COMMITTED | done | [`phase-44-reference-project-protocol.md`](phase-44-reference-project-protocol.md) |
| 45 | Register **Ledgerkit** + baseline evaluation *(was Technical Clipper — reordered 2026-09-12, gate G11)* — first external reference-project datapoint; first-ever **FAIL** verdict (`CG-002`, dev-docs/ glob-coverage gap) | EXPERIMENTAL | done | [`phase-45-ledgerkit-baseline.md`](phase-45-ledgerkit-baseline.md) |
| 46 | CodeCompass during a genuine Ledgerkit task + independent evals *(task reconfirmed live at phase start — Ledgerkit's own Stage B closed and Stage C opened mid-Phase-45/46, so the actual task run was hledger 1.52 query-term semantics, not the plan's named candidate)* — second-ever **FAIL** verdict, LOW (negative) advantage; `CG-002` re-confirmed (`recurred`), `CG-003` filed (external hledger.org manual, zero representation) | EXPERIMENTAL | done | [`phase-46-ledgerkit-tasks.md`](phase-46-ledgerkit-tasks.md) |
| 47 | Consolidate recurring friction into confirmed findings — **GATE DB** | EXPERIMENTAL | not started | [`phase-47-consolidate-findings.md`](phase-47-consolidate-findings.md) |
| 48–51 | Stage C — improve the existing product (task-oriented retrieval, graph quality, shared-agent context/entry points, re-evaluate against Ledgerkit) | CONDITIONAL (GATE DB) | not started | — |
| 52–55 | Stage D — deeper Ledgerkit dogfooding: continued Core development, heterogeneous docs / executable / behavioural context, refine the blueprint — **GATE DD** | EXPERIMENTAL | not started | — |
| 56–59 | Stage E — minimum justified generalisation (technical-dependency + provenance abstractions, migrate package/source, re-validate against Ledgerkit) | CONDITIONAL (GATE DD) | not started | — |
| 60–63 | Stage F — cross-ecosystem regression: register + evaluate **Technical Clipper** *(new stage, was Stage B — moved 2026-09-12, gate G11)*; does CodeCompass generalise or overfit? — **GATE DF** | EXPERIMENTAL | not started | — |
| 64–70 | Stage G — blank-slate doc reconstruction, architecture/ADR/roadmap reconciliation, final self-dogfood + Ledgerkit + Technical Clipper confirmation, independent release audit, milestone closeout, release *(was Stage F, phases 60–67 — renumbered +4)* | COMMITTED (once F completes) | not started | — |

Detail for every stage: [`v1-redefinition/roadmap.md`](v1-redefinition/roadmap.md).
Phases 45+ get their own plan files as their preceding gate resolves —
later stages are deliberately revisable based on earlier findings, so
they are not written speculatively now.

**Existing Post-MVP Phases 24 (chat routing/rollup) and 25 (MCP)** are
marked **deferred** in the Post-MVP table above (`decisions/0048`) — 24 a
redefined-v1 Stage C candidate (only if reference-project evidence
supports project-root context routing), 25 post-redefined-v1. **Not
renumbered.**

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
