# Roadmap

Tracks every roadmap phase and its completion status. This file is kept
up to date **with every change that affects phase scope or status** — see
`CLAUDE.md` §2. Unlike `planning/CONTEXT.md` (which reflects only the
*current* phase in detail for session-resumption), this file is the
full-roadmap, at-a-glance view: what's done, what's next, what's still
just planned.

Status values: `not started` / `planned` (a `planning/phase-N-*.md` file
exists) / `in progress` / `done` / `deferred` (on the roadmap, not
scheduled — revisit trigger named in the row) / `not funded` (a gate
explicitly declined to fund it, per evidence at the time — revisit
trigger named in the row) / `superseded` (replaced by a later decision
— ADR named in the row).

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
| 23 | *(was 22, was 21, was 11, formerly 10)* Polish: examples, docs-site evaluation, packaging readiness (decisions/0039). **Part A done.** Part B (the PyPI publish) is **superseded** by the v1 redefinition (`decisions/0048`) — CodeCompass publishes nothing until the redefined v1 (Phase 70, gate G2-b). | Part A done; Part B superseded | [`phase-23-polish-and-pypi-publish.md`](phase-23-polish-and-pypi-publish.md) |
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
> (Phase 70). Phases 24/25's "deferred past v1.0" still holds — see the
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
| 47 | Consolidate recurring friction into confirmed findings — **GATE DB ratified 2026-09-13**: fund one narrow Stage C phase (49); Phase 48 not funded (no corroborating evidence) | EXPERIMENTAL → decision | done | [`phase-47-consolidate-findings.md`](phase-47-consolidate-findings.md) |
| 48 | Task-oriented context retrieval | CONDITIONAL | **not funded** (GATE DB, Phase 47 — `CG-001` single-occurrence, own-dev only) | — |
| 49 | `dev-docs/**/*.md` spec-doc coverage (`CG-002`) + `query relations` "not found" disambiguation (`L-016`) — CodeCompass's first `src/codecompass/` change driven by external reference-project evidence, live-verified against the real Ledgerkit clone | CONDITIONAL (GATE DB — funded) | done | [`phase-49-spec-doc-coverage-and-error-disambiguation.md`](phase-49-spec-doc-coverage-and-error-disambiguation.md) |
| 50 | Shared-agent context / entry-point improvements | CONDITIONAL | **not funded** (GATE DB, Phase 47 — no supporting evidence) | — |
| 51 | Re-run Ledgerkit evaluation — **GATE DC confirmed 2026-09-14**: both original FAILs (Phase 45 baseline Q2, Phase 46 genuine task) moved to PASS WITH GAPS, generalisation confirmed against a brand-new file; advantage stayed LOW (structural ceiling — `query relations` name-mention-only, 0 tracked Ledgerkit vendors); Phase 49's fix judged a success on its own narrow terms. **Completes Stage C** (48/50 not funded, 49 done, 51 done). | EXPERIMENTAL | done | [`phase-51-rerun-ledgerkit-evaluation.md`](phase-51-rerun-ledgerkit-evaluation.md) |
| 52 | Context edge lifecycle — `context-observations/` queue + agent-driven enrichment (`decisions/0054`), demonstrated against a local Ledgerkit-mimicking fixture (two cycles) — new `context-enrichment-agent` (roster's 9th), new `codecompass enrich apply` CLI command; live two-cycle demonstration proved the enrichment trust boundary, the enrichment cache surviving a graph rebuild, and a genuine stale-resubmission rejection; one honest complication root-caused live and filed (`L-019`) | EXPERIMENTAL | done | [`phase-52-context-edge-lifecycle.md`](phase-52-context-edge-lifecycle.md) |
| 53 | Legacy feature rationalisation — full feature inventory (CORE/AGENT/HOST-OUTPUT ADAPTER classification), redundancy map, and per-feature KEEP/REMOVE/DEFER decisions across direct-API enrichment vs. Phase 52's agent-driven path, chat, Skills, and dead code (`rewrite_vendor_toml`) — **review gate passed** (user approved keeping direct-API enrichment and `chat.py` unchanged, deferring two doc-only findings); removed dead `rewrite_vendor_toml` + its test, added `architecture/overview.md`'s Module-tiers section *(retargets this slot from the original "Stage D" sketch, same findings-drive-scope precedent as Phases 49/52 — orthogonal to, does not resolve, the open Stage D-vs-F/G decision)* | EXPERIMENTAL | done | [`phase-53-legacy-feature-rationalisation-plan.md`](phase-53-legacy-feature-rationalisation-plan.md) |
| 54 | Heterogeneous reference-material experiment — real Git-backed resolve/lock/fetch/extract pipeline (outside `src/codecompass/`), tested against one genuine Ledgerkit Stage C task (`tag:` query semantics) with an independently-evaluated baseline-vs-treatment comparison — **treatment FAIL / baseline PASS WITH GAPS / advantage LOW** (a real, caught-and-fixed extraction-boundary defect, not a mechanism failure); detection generalises with zero code change, mechanical relation-detection structurally cannot link two `spec_doc` artifacts (`CG-004`), `origin` has no externally-pinned-reference value (`CG-005`), a working YAML-evidence-matching fallback was demonstrated real but unwired (`OBS-008`) *(retargets this slot from the original "Stage D" sketch, "External executable / behavioural context" — that sketch is not discarded, just left without a claimed number — see `phase-54-heterogeneous-reference-material-experiment.md` §0)* | EXPERIMENTAL | done | [`phase-54-heterogeneous-reference-material-experiment.md`](phase-54-heterogeneous-reference-material-experiment.md) |
| 54b | LedgerKit reference/behaviour validation — a behavioural-understanding experiment using Ledgerkit's real Stage C Phase 5 `depth:` investigation. **Done 2026-09-18**: two fresh, independent agents (baseline: no CodeCompass; treatment: CodeCompass-indexed reference material) both reached the fully correct, execution-path-complete answer across all five hledger commands — `context-evaluator` rated baseline PASS / treatment PASS WITH GAPS, context advantage **LOW** (the curated set omitted the one file covering the task's genuine exception, `Stats.hs`; mechanical `query relations` again found zero edges). Filed `CG-007`, `OBS-013`, `OBS-014`, promoted `L-022`. No `src/` change. Full plan: `planning/phase-54b-ledgerkit-behavioural-understanding-experiment.md`; results: `planning/reference-projects/ledgerkit/findings.md` | EXPERIMENTAL | done | [`v1-redefinition/roadmap.md`](v1-redefinition/roadmap.md) §Stage D |
| 54c | Evidence-backed, knowledge-based, documentation-first development workflow — a bounded, reversible experiment (file-based Observation/Evidence/Claim/Derivation/Decision/Requirement model under `planning/knowledge/`). **Done 2026-09-18**: both proving cases run for real — `CG-005` (full research→design→review→packet→implementation→revalidation loop; `doc_artifacts.origin` gains `pinned_reference`, real `codecompass sync` confirms all 19 real Phase 54b-ingested files now correctly classified; `CG-005` promoted) and a retroactive `hledger-depth` design doc that correctly matches Ledgerkit's real shipped Stage C Phase 5 outcome. A fresh-agent traceability test passed. Two real gaps found and promoted (`L-023`, `L-024`). Two of ten evaluation questions honestly left unanswered (contradicting-evidence retention, review-catches-a-misunderstanding) rather than claimed positive. Whether the workflow improves development quality generally remains undecided, deferred to Phase 60/61. No new ADR. Retro: `planning/retros/phase-54c-evidence-knowledge-workflow.md` | EXPERIMENTAL | done | [`v1-redefinition/roadmap.md`](v1-redefinition/roadmap.md) §Stage D |
| 55 | Stage D decision — GATE DD: is a generalised technical-dependency/provenance concept necessary for v1, informed by Phase 54's evidence and the Phase 55 evidence-reconciliation package? | EXPERIMENTAL → decision | not started | [`planning/phase-55-evidence-reconciliation.md`](phase-55-evidence-reconciliation.md) |
| — | External executable / behavioural context (displaced from its original Phase 54 slot; unclaimed, no phase number) | CONDITIONAL | not started | — |
| 55b | Populate `doc_artifacts.name` for `spec_doc` rows, closing `CG-004` — doubly-corroborated (Phase 54's own scratch-copy experiment + Ledgerkit's independent live-repo `CC-LK-001` finding) doc-to-doc relation gap. **Numbered as a bridge phase** (43d/43e precedent), not consuming Stage E's (56-59)/Stage F's (60-63) pre-written sketch numbers, none of which matched this phase's content. Real production-wiring gap caught by an independent `context-evaluator` round-1 FAIL (unit tests passed but `sync.py` never actually called the new code path); fixed, plus a genericity guard (`_is_specific_enough`) after round 1 quantified 50 hypothetical false-positive edges from a bare project-name README title. Round 2: **PASS WITH NON-BLOCKING OBSERVATIONS**, confirmed via a real before/after against the live Ledgerkit repository (3 genuine edges, zero reintroduced noise). Residual, honestly disclosed limitation filed as `CG-006` (matches by title text only, never filename — the original `CC-LK-001` three files still show no relation to each other). | EXPERIMENTAL | done | [`phase-55b-spec-doc-name-population.md`](phase-55b-spec-doc-name-population.md) |
| 56–59 | Stage E — minimum justified generalisation (technical-dependency + provenance abstractions, migrate package/source, re-validate against Ledgerkit) | CONDITIONAL (GATE DD) | not started | — |
| 60 | Minimal Haskell adapter, as the reference implementation of a genuinely **external** CodeCompass adapter, in two real separate public repositories. **Done 2026-09-19**: `codecompass-adaptor-protocol` (MIT, schemas/examples/conformance only) and `codecompass-adaptor-haskell` (GPL-3.0-or-later, real Stack project) both created, pushed, and checked out as git submodules (`protocol/codecompass-adaptor-protocol/`, `adapters/haskell/`); `decisions/0057`/`0058`/`0059` (the third — an additive `symbols.kind`/`note` wire extension for re-export/undetermined entries, caught by `knowledge-curator`'s own packet-sufficiency check before implementation). CodeCompass core gains `Ecosystem.HASKELL`, a non-destructive `vendors.ecosystem` CHECK-widening migration (`_SCHEMA_VERSION` 7→8 — table-rebuilt in place, never dropped, to protect FK'd `vendor_enrichment`/`symbol_enrichment`), `discovery.py`'s `package.yaml` discoverer (real `PyYAML`), `external_process.py` (generic protocol client), `haskell.py` (thin dispatcher). Phase 54c's evidence-backed workflow ran in full for Haskell API-surface extraction (`planning/knowledge/haskell-api-surface-extraction/`: 13 Observations, 11 Evidence, 6 Claims, 1 Decision, 6 Requirements, all `verified`) — a real `codecompass sync` against `hledger-lib` (the pinned reference corpus) independently confirmed correct: the 48-name `Hledger.Data.AccountName` export set matches live `stack ghci :browse` output exactly, `Hledger.hs`'s `module X` alias resolves to its 5 real covered modules, `Hledger/Data/Types.hs`'s CPP-gated `Year` entry is flagged undetermined rather than guessed. Real finding, disclosed and routed (not fixed here, per direct instruction): `_collect_vendor_symbols` doesn't ingest the adapter's own structured symbols into `context-graph.db`'s `symbols` table (`CG-008`, routed to Phase 62). `0.1.0` tagged in both new repositories after this phase's own DoD audit passed. Does **not** resolve GATE DD and does **not** complete or bypass Phases 55-59, which remain exactly as open as before. Retro: `planning/retros/phase-60-minimal-haskell-adapter.md`. Full plan: `planning/phase-60-minimal-haskell-adapter.md` | EXPERIMENTAL | done | [`planning/phase-60-minimal-haskell-adapter.md`](phase-60-minimal-haskell-adapter.md) |
| 61 | hledger cross-language experiment — tracked both `hledger-lib` and `hledger` as real Haskell vendors in a disposable Ledgerkit scratch copy. **Done 2026-09-19.** Fixed the required prerequisite: `HaskellAdapter.repository_url()` now sets `RepositoryLocation.subdirectory` for a monorepo member. Real, symmetric two-agent comparison (commit-pinned, byte-identical source, identical task/tools) scored two-part-plus-overall: **Part 1** (`depth:` reconstruction) — treatment PASS (vs. Phase 54b's own PASS WITH GAPS), context advantage **LOW** (the improvement traced to `hledger` now being tracked at all, not to anything the generated digest explained); **Part 2** (cross-language equivalence recognition) — context advantage **effectively NULL** (Ledgerkit isn't a tracked vendor; both agents read identical raw source). **Outcome shape (b)**: helped Part 1 navigation marginally, did not materially help Part 2. Rediscovery comparison: **no measurable reduction**. A real, previously-unrecorded Ledgerkit correctness gap was found and empirically confirmed (`stats()`'s commodity count isn't depth-excluded the way hledger's real one is) — Ledgerkit's own issue, not acted on here. `usage.py`'s Haskell import detection investigated and **not built** (no real consumer; the one relevant cross-vendor edge is already free via `depends_on_edges`). Three learnings filed and triaged (`L-026`/`L-027`/`L-028`); two context-observations filed (`OBS-015`/`OBS-016`). Does **not** resolve GATE DD or complete/bypass Phases 55-59. Retro: `planning/retros/phase-61-hledger-cross-language-experiment.md`. Evaluation: `planning/reference-projects/ledgerkit/03-hledger-cross-language-evaluation.md`. Full plan: `planning/phase-61-hledger-cross-language-experiment.md` | EXPERIMENTAL | done | [`planning/phase-61-hledger-cross-language-experiment.md`](phase-61-hledger-cross-language-experiment.md) |
| 62 | Adapter-interface consolidation — closes `CG-008` (the graph's `symbols` table stayed empty for Haskell vendors). **Done 2026-09-19.** Amended before coding (direct instruction): the new core field is named `export_kind`, not `kind` — the wire's three values (`decisions/0059`) describe export/exposure status, not a symbol's own intrinsic type, and a generic `kind` field would collide with a future adapter's own type concept (e.g. a hypothetical COBOL adapter's program/paragraph/section/copybook). `EcosystemAdapter` gains a new, concrete (not abstract) `symbols()` method, defaulting to the exact walk+extract pairing `sync.py`'s own private `_collect_vendor_symbols` (now removed) used to perform — npm/Python/Cargo inherit correct behaviour for free, no per-adapter changes needed (a refinement discovered during implementation: the plan's own literal "refactor each adapter's `readme_and_api_surface()`" text turned out unnecessary once the shared default existed, and inaccurate for npm specifically, which never had the described duplication). `HaskellAdapter.symbols()` overrides it, converting its own already-computed external-process result — the one place the wire's `kind` and the core's `export_kind` meet. `Symbol`/`SymbolRow` widen with `export_kind`/`note`; `symbols` table gains nullable columns via `ADD COLUMN` (`_SCHEMA_VERSION` 8→9, not a `vendors`-style rebuild — `symbol_enrichment`'s own cascade risk is avoidable without one). `HaskellAdapter` gains a per-instance `_analyze()` cache (real, confirmed redundant external-process spawns across `dependency_tree()`/`readme_and_api_surface()`/the new `symbols()`) — explicitly not cross-instance. `codecompass query vendor`'s CLI table and JSON both show `export_kind`/`note`. Real, live re-confirmation: a real `codecompass sync` against `hledger-lib` produced 1305 real `symbols` rows (1256 `export`, 48 `reexport`, 1 `undetermined`), checked directly via SQL and via `query vendor --json`. Explicitly, disclosed, **not fixed**: `build_symbol_index`/`purpose_for_file` (FILETREE.md's own flat symbol index) stay Haskell-blind — a real architectural mismatch (per-file, no-subprocess functions vs. a per-vendor, subprocess-backed adapter) judged materially bigger than this phase's own "smallest justified fix" mandate. Retro: `planning/retros/phase-62-adapter-interface-consolidation.md`. Full plan: `planning/phase-62-adapter-interface-consolidation.md` | EXPERIMENTAL | done | [`planning/phase-62-adapter-interface-consolidation.md`](phase-62-adapter-interface-consolidation.md) |
| 63 | Stage F, remainder — lightweight ordinary-project smoke test — **GATE DF** *(retargeted 2026-09-17, `decisions/0056`: Technical Clipper is no longer this stage's target — demoted to an optional Phase 63 smoke-test candidate, not roadmap-driving; Rust/npm adapter maturation similarly demoted to later ecosystem-expansion work; original Technical-Clipper content preserved in `v1-redefinition/roadmap.md`, not deleted)*. **Done 2026-09-22.** Amended before implementation: `which npm`/`which cargo` both confirmed absent from this sandbox, so the live Technical Clipper clone (which could only have exercised a fraction of `NpmAdapter`'s own methods, never `dependency_tree()`) was dropped rather than run partially — direct user instruction, matching the roadmap's own express "if convenient, not required" allowance. **GATE DF verdict: PASS** — full regression suite (623 passed, 2 skipped, identical to Phase 62's own baseline), `ruff`, `check_user_docs.py --strict` all clean; no regression found in npm/Python/Cargo adapter support from Phases 60–62. Stage G (and Phase 63D) unblocked. Retro: `planning/retros/phase-63-lightweight-smoke-test.md`. Full plan: `planning/phase-63-lightweight-smoke-test.md` | EXPERIMENTAL | done | [`planning/phase-63-lightweight-smoke-test.md`](phase-63-lightweight-smoke-test.md) |
| 63D | **Domain reconstruction** *(new bridge phase, `decisions/0060`, 2026-09-20 — non-disruptive letter-suffixed numbering, Stage G's 64–70 undisturbed)* — dogfoods CodeCompass against its own repository to build an evidence-backed domain corpus (`docs/domain/`) for core concepts (evidence, observation, claim, derivation, provenance, relationship/edge, context, context packet, adapter, connector, protocol, reference, decision, invariant, and others found along the way), reusing Phase 54c's own Observation/Evidence/Claim/Derivation/Decision record model project-wide rather than per-feature, plus a new independent adversarial reviewer (`domain-skeptic`) before any ambiguity reaches the user — no agent or lead may stand in for the user on a genuine escalation, amended 2026-09-20. First project-scoped application of the newly-formalized **Scope → Plan → Domain → Design → Implement** v1 development methodology (`v1-redefinition/development-methodology.md`). Sits immediately before Phase 64, whose own scope now consumes this phase's output rather than independently rediscovering terminology. Gated on Phase 63/GATE DF completing — **GATE DF passed 2026-09-22**, unblocked; **not** gated on GATE DD. **Done 2026-09-23**: three parallel `context-researcher` dispatches produced 19 concept pages + 135+ evidence records; `domain-skeptic`'s own first real review found zero genuine escalations (one naming drift resolved with new git-history evidence, six terminology-loosenesses correctly left open, two implementation gaps routed to `planning/learnings/inbox.md` as `L-031`/`L-032`); the actual user/domain owner approved the corpus subject to four corrections (two content over-generalisations, one stale file reference, this row's own then-stale status), all applied and verified same day. Retro: `planning/retros/phase-63d-domain-reconstruction.md`. Full plan: `planning/phase-63d-domain-reconstruction.md` | EXPERIMENTAL | done | [`planning/phase-63d-domain-reconstruction.md`](phase-63d-domain-reconstruction.md) |
| 64 | **Blank-slate documentation reconstruction** — Stage G's first phase. `docs-reconstructor` (MILESTONE mode) derives a fresh documentation proposal from authoritative project reality, **consuming Phase 63D's own approved `docs/domain/` corpus as an input rather than re-deriving domain terminology**, organized into the six documentation categories (`documentation-lifecycle.md` §1.4): domain, architecture, user, developer, protocol/adapter, development-process. Produces a shadow proposal under `planning/v1-docs-reconstruction/` — never overwrites `docs/`/`README.md`/`architecture/`/`ai-docs/`; comparing it against current active docs is Phase 65's job. No `src/codecompass/` change. Gated on Phase 63D completing — **done 2026-09-23**, unblocked. **Done 2026-09-23**: three parallel `docs-reconstructor` dispatches produced 28 files across all six categories; a lead cross-cluster consistency pass consolidated five retirement candidates (`concepts-to-retire.md`) and distinguished a genuine independent corroboration from a re-confirmation of the already-tracked `L-032`; `knowledge-curator` independently reviewed the retro's own learning-triage call and promoted two further process findings (`L-035`, `L-036`) into `planning/agent-led-workflow.md` step 5. Retro: `planning/retros/phase-64-blank-slate-documentation-reconstruction.md`. Full plan: `planning/phase-64-blank-slate-documentation-reconstruction.md` | COMMITTED | done | [`planning/phase-64-blank-slate-documentation-reconstruction.md`](phase-64-blank-slate-documentation-reconstruction.md) |
| 65 | **Architecture + ADR reconciliation** — Stage G's second phase. Compares Phase 64's shadow proposal (`planning/v1-docs-reconstruction/`) against current active documentation, document by document, recording retain/rewrite/consolidate/split/replace/remove decisions (`documentation-lifecycle.md` §4). Concrete inputs: `architecture-split-candidates.md`'s 32 remaining history-shaped passages in `architecture/overview.md`, `concepts-to-retire.md`'s 5 candidates. Also: ADR status review (mark superseded ADRs, don't rewrite them) across all 59 ADRs, and the domain-corpus freshness reconciliation (`domain-skeptic` re-checks staleness candidates accumulated since Phase 63D — none found by Phase 64's own drift audit so far). Gated on Phase 64 completing — **done 2026-09-23**, unblocked. **Done 2026-09-23**: `architecture/overview.md` reduced 2312→1037 lines (all 32 catalogued items + 3 new findings resolved); 5 files adopted from Phase 64's proposal (`module-map.md`, `core-data-model.md`, `adapter-interface.md`, `context-graph-schema.md`, `sync-and-enrichment-pipeline.md`) plus a new `historical-notes.md`; `docs/external-adapters.md` split into 4 audience-specific files; `docs/quickstart.md`/`docs/domain/quick-reference.md` adopted; one real ADR governance gap found and fixed (`decisions/0061`, `decisions/0019` superseded by `decisions/0035`); domain-corpus freshness confirmed clean. Retro: `planning/retros/phase-65-architecture-adr-reconciliation.md`. Full plan: `planning/phase-65-architecture-adr-reconciliation.md` | COMMITTED | done | [`planning/phase-65-architecture-adr-reconciliation.md`](phase-65-architecture-adr-reconciliation.md) |
| 66 | **Roadmap + context reconciliation** — Stage G's third phase. `roadmap-context-curator` audits `ROADMAP.md`'s full table against actual project state; every deferred/not-funded/conditional item confirmed clearly parked with a stated revisit trigger (GATE DD/Stage E recorded as intentionally, legitimately open, not an oversight). `planning/CONTEXT.md` rewritten in full to comply with `CLAUDE.md` §4 (current-only, not an ever-appended history) — flagged as a standing, multi-phase drift by Phase 65's own audit. Gated on Phase 65 completing — **done 2026-09-23**, unblocked. **Done 2026-09-24**: three real `ROADMAP.md` findings fixed (a status-legend omission, a stale `L-021` approval claim, a missing plan-file link); `CONTEXT.md` rewritten 2449→126 lines (a fork cross-check confirmed no information loss); the domain-corpus freshness reconciliation caught a real cross-file staleness case on its first non-trivial exercise (`connector.md`'s file-list claim, four off-by-one citations), both resolved. Retro: `planning/retros/phase-66-roadmap-context-reconciliation.md`. Full plan: `planning/phase-66-roadmap-context-reconciliation.md` | COMMITTED | done | [`planning/phase-66-roadmap-context-reconciliation.md`](phase-66-roadmap-context-reconciliation.md) |
| 67 | **Final validation: self-dogfood + Ledgerkit + Stage F smoke test** — Stage G's fourth phase, EXPERIMENTAL, gates v1 (a FAIL blocks describing CodeCompass as a validated reference project, not the software release itself). A lightweight confirmation pass: re-verify `context-health.md` currency; re-confirm Ledgerkit's current PASS WITH GAPS/LOW status and Phase 63's smoke-test basis still hold; state plainly how many real times the Scope→Plan→Domain→Design→Implement methodology was exercised pre-v1; a fresh-agent acceptance test (one real small task, `decisions/0060`). Gated on Phase 66 completing — **done 2026-09-24**, unblocked. **Done 2026-09-24**: `context-health.md` found genuinely stale (21 phases, this checkout's own graph regressed) and fixed with a deterministic sync; Ledgerkit re-confirmed live on a newer pin (`c6168b2`) than the original GATE DC evaluation; methodology exercise count reported honestly as one (Phase 63D); fresh-agent acceptance test scored **4/4 PASS**. Three learnings promoted (`L-040`/`L-041`/`L-042`). Retro: `planning/retros/phase-67-final-validation.md`. Full plan: `planning/phase-67-final-validation.md` | EXPERIMENTAL | done | [`planning/phase-67-final-validation.md`](phase-67-final-validation.md) |
| 68 | **Independent release audit** — Stage G's fifth phase, COMMITTED (FAIL blocks Phase 69/70). `release-phase-auditor`, read-only, a milestone-level Definition-of-Done audit across every Stage A–G phase since Phase 41 (retro requirement began there) plus `planning/milestone-closeout-checklist.md`'s own steps 1–7 (steps 8–11 are Phase 69/70's own job). Gated on Phase 67 completing — **done 2026-09-24**, unblocked. **Done 2026-09-24: verdict PASS**, first pass, no fix cycle needed — every phase since 41 has a real retro, every checklist step 1–7 independently re-verified against current state. Two learnings triaged: `L-043` (promoted — a new mechanical check, `check_learnings_status_matches_retain_outcome`, closes the gap that let `L-008`'s own status field drift inconsistent for ~57 phases) and `L-044` (retained — single-occurrence). Retro: `planning/retros/phase-68-independent-release-audit.md`. Full plan: `planning/phase-68-independent-release-audit.md` | COMMITTED | done | [`planning/phase-68-independent-release-audit.md`](phase-68-independent-release-audit.md) |
| 69–70 | Stage G, remainder — milestone closeout, release *(was Stage F, phases 65–67 — renumbered +4)* | COMMITTED — gated only on Phase 68 completing in turn | not started | — |

Detail for every stage: [`v1-redefinition/roadmap.md`](v1-redefinition/roadmap.md).
Phases 45+ get their own plan files as their preceding gate resolves —
later stages are deliberately revisable based on earlier findings, so
they are not written speculatively now.

**Existing Post-MVP Phases 24 (chat routing/rollup) and 25 (MCP)** are
marked **deferred** in the Post-MVP table above (`decisions/0048`) — 24 a
redefined-v1 Stage C candidate (only if reference-project evidence
supports project-root context routing), 25 post-redefined-v1. **Not
renumbered.**

## Future-improvement backlog (unscheduled)

Findings that the learning lifecycle
(`planning/v1-redefinition/learning-lifecycle.md` §4) classified
`future-improvement` land here once `knowledge-curator` recommends
promotion — this is that classification's roadmap destination, finalised
by `roadmap-context-curator` per that section. A row here has **no phase
number and is not scheduled**; it becomes a numbered phase only if/when
someone plans one, at which point its row is replaced by the phase's own
row elsewhere in this file (per the "How this file is kept in sync"
section below) rather than left duplicated here. Full evidence lives in
the originating `planning/learnings/inbox.md` entry (and, once the lead
records it, `planning/learnings/promoted.md`); this table only tracks
existence and status.

| ID | Finding | Classification | Status | Notes |
|---|---|---|---|---|
| L-031 | `symbol_enrichment` has no producer-attribution column, unlike `vendor_enrichment`/`doc_relation_enrichment` (both carry `model TEXT NOT NULL`) — `symbol_enrichment` rows currently cannot be attributed to a specific producer (agent or automated API call) at all. Add a `model` column via an additive migration (mirroring `_migrate_symbols_export_kind_note_columns`'s `ADD COLUMN` pattern, Phase 62), or explicitly document the asymmetry as an intentional simplification if a rationale is found. Origin: `L-031` (Phase 63D, `domain-skeptic`'s own review). | FUTURE-IMPROVEMENT | not started | — |
| L-032 | `ExternalAdapterProcess.initialize()` receives `ecosystem` and `capabilities` from an external adapter's wire response (`external_process.py:83-84`) but never validates either: `ecosystem` is never compared against the `core.Ecosystem` value CodeCompass configured the adapter under, and `capabilities` is never checked against the protocol's own closed 4-value set already defined in the same file (`CAPABILITIES`). An adapter reporting a mismatched `ecosystem` string or an unrecognized capability is currently accepted uncomplainingly. Add a membership/equality check in `initialize()`, raising `AdapterError` on mismatch (matching the existing `protocol_version` mismatch handling immediately above it in the same method). Origin: `L-032` (Phase 63D, `domain-skeptic`'s own review). | FUTURE-IMPROVEMENT | not started | — |

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
- A `future-improvement`-classified learning is added to the "Future
  improvement backlog" table above by `roadmap-context-curator`, once
  `knowledge-curator` recommends promotion (`learning-lifecycle.md` §4),
  in the same pass that updates `planning/learnings/inbox.md`'s status
  and `promoted.md`. When a backlog row is later turned into a real
  phase, remove the backlog row in the same commit that adds the phase's
  own row and plan file.
