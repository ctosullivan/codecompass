# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Phase 32**: new `doc_chunking.py` deterministically splits a
  chunkable doc artifact's (`claude_md`/`overview`/`vendor_doc`/
  `spec_doc`) markdown text into heading-scoped chunks — any heading
  level, root-first nested `heading_path` (`"Scope > Covers"`), no NLP,
  no embeddings. New `doc_chunks` table; `documents_edges`/`doc_relations_
  edges` each gain a nullable `chunk_id`, populated when a mechanical
  mention-detection match is attributable to exactly one chunk (`doc_
  mapping.py`'s existing whole-doc word-boundary passes gain an additive
  per-chunk pass). A doc with no headings at all produces zero chunks, so
  its matches naturally stay unattributed — no special-casing needed.
  Phase 30's `doc_code_trace`/`graph.doc_relations` (and `query
  relations`'s output) gain an optional `heading` field when a match has
  a `chunk_id`. `relation_enrichment.select_candidates` now uses the
  matched chunk's own text directly as the AI-enrichment excerpt when one
  exists, in place of Phase 28's needle-re-derivation-plus-fixed-window
  guess — which remains, unchanged, as the fallback for any edge without
  a chunk. `documents_edges`/`doc_relations_edges` migrate on an existing
  database via the same drop-and-recreate approach `doc_artifacts`'s
  migration already uses (both are always fully rewritten every sync
  regardless); `doc_relation_enrichment` (paid AI spend) is untouched by
  this phase. See `decisions/0046`.

- **Phase 31**: `doc_relation_enrichment` (Phase 22) gains a closed-
  taxonomy `relation_label` alongside its existing free-text `ai_summary`
  — `documents_configuration_of`, `explains_usage_of`, `contrasts_with`,
  `supersedes`, or `other`. The batched enrichment tool schema now
  requires a `relation_label` per result; any value the model returns
  outside the enum (missing, malformed, or invented despite the schema's
  own `enum` constraint) is normalized to `'other'`, never raises.
  Strictly gated on Phase 21/29's already-mechanically-proven candidates —
  no new candidate discovery, same detection-vs-description boundary held
  since `decisions/0031`. `query relations` shows the label alongside the
  summary in both human and `--json` output. Schema migrates an existing
  database via `ALTER TABLE ... ADD COLUMN` (not the drop-and-recreate
  `doc_artifacts` uses) since this table holds paid AI spend that must
  survive; pre-existing rows get `relation_label = NULL` until their next
  natural re-enrichment, no backfill. See `decisions/0045`.

- **Phase 30**: `codecompass query vendor`/`query symbol` now show real
  `(file, line)` usage locations ("Used at" — `used_at` in JSON), no
  longer just a bare `usage_count`. New `graph.doc_code_trace(conn,
  doc_path_or_vendor_name)` composes existing edges into a two-hop
  package-code trace — `documents_edges` → `symbols` → `uses_edges` for
  what a doc documents, and a doc's own outgoing `mentions_dependency`
  `doc_relations_edges` → `vendors` → `uses_edges` for what it mentions —
  surfaced in `query relations` as a new "Package code" section. Pure
  query-time joins over data already in the graph; no new table, no new
  detection, no AI call, same posture as `documented_but_unused`.
  `query relations --json`'s payload changes from a bare list to
  `{"relations": [...], "package_code": [...]}` — a relation and a usage
  site are different shapes that don't merge into one row; `query
  vendor`/`query symbol --json` gain `used_at` as one more key, purely
  additive. Confirmed live against this repo's real graph: `query symbol
  Console`'s `used_at` matches the real import-line locations `grep`
  finds; `query relations architecture/overview.md`'s "Package code"
  section lists real `typer` call sites in `cli.py`. See `planning/
  phase-30-bidirectional-code-traversal.md`.

### Fixed

- **Phase 33**: `codecompass query vendors|vendor|symbol|skills|relations
  --json` no longer emits invalid JSON. Every `--json` call site printed
  through the shared Rich `Console`, which word-wraps long printed text by
  inserting real line breaks; a value long enough to cross the wrap width
  (e.g. `anthropic`'s longer symbol `purpose` strings, confirmed live
  against this repo's real graph) got a literal newline inserted into it,
  corrupting the JSON. Fixed by adding `soft_wrap=True` to all five call
  sites — the same flag Rich's own `Console.print_json` uses internally
  for exactly this case. New regression test confirmed to fail against the
  pre-fix code and pass against the fix. Found via the same `/discovery`
  session that surfaced Phases 30-32 below; that session's other flagged
  item (a `check` version-drift reading that looked backwards) was
  investigated and confirmed not a bug — see `planning/
  phase-33-fix-query-json-line-wrapping.md`'s Context section.

### Added

- Planning: `planning/doc-graph-precision-roadmap.md` — a new umbrella
  plan (same role `v1.0-initial-release-roadmap.md` played for 20-23),
  plus three new phase plans it introduces: `planning/
  phase-30-bidirectional-code-traversal.md` (surface `uses_edges`'
  existing file/line data via a new `used_at` list and a `doc_code_trace`
  two-hop query — no new tables, no AI), `planning/
  phase-31-typed-relation-enrichment.md` (a closed `relation_label` enum
  alongside Phase 22's existing free-text `ai_summary`, gated on Phase
  21/29's already-mechanically-proven candidates only), and `planning/
  phase-32-doc-chunking.md` (deterministic heading-based split of doc
  artifacts into a new `doc_chunks` table, with a nullable, additive
  `chunk_id` on `documents_edges`/`doc_relations_edges`). All three hold
  the same detection-vs-description AI boundary established by
  `decisions/0031`. `planning/ROADMAP.md`'s Post-MVP table updated: 30/31/32
  appended after 29, no renumbering. At explicit user request, these three
  phases also expand v1.0's blocking scope — Phase 23 Part B (the actual
  publish) now waits on 30-32 reaching `done` too, alongside its existing
  confirmation gates. Planning only, no code changed.

- **Phase 29**: a vendor's own embedded upstream doc (`kind='vendor_doc'`,
  Phase 27) is no longer passive, indexed-only content — it now
  participates in the graph as a relationship *source*, symmetric to how
  spec docs already did. `build_documents_edges` now scans `vendor_doc`
  rows for symbol mentions too (a vendor's own README documenting its own
  API is now a real `documents_edges` source, confirmed live:
  `vendor/anthropic/src/README.md` now documents the `Anthropic` symbol).
  `build_doc_relations_edges` now accepts vendor docs as sources alongside
  spec docs, via a deliberately closed allow-set
  (`{"spec_doc", "vendor_doc"}` — codecompass-generated artifacts are
  excluded on purpose, since they'd only ever produce structural
  self-mentions, not signal), with a self-mention exclusion so a vendor's
  own README mentioning its own name never produces a
  `mentions_dependency` edge to itself (confirmed live against real data:
  zero such edges despite `vendor/anthropic/src/README.md` containing
  "anthropic"/"Anthropic" seven times). Confirmed live: 3 new
  vendor-doc-sourced relationships appeared on the first re-sync. See
  `decisions/0043`, which supersedes `decisions/0041`'s "a vendor doc is
  never a relation source" claim specifically (its actual root-level
  detection-scope decision is unaffected).

### Fixed

- **Phase 28**: `relation_enrichment.select_candidates` no longer always
  sends the spec doc's first 4,000 characters as AI grounding — it now
  re-derives the mechanical match's position (the same needle and regex
  shape `doc_mapping.build_doc_relations_edges` used to detect the
  relationship) and centers a 4,000-character window on it, falling back
  to the old first-N-characters slice only if the needle can no longer be
  found. Fixes a real, reproduced bug: this repo's own two currently-
  enriched `"anthropic README.md"` relationships had their real
  mechanical match at character 7,870 and 91,374 of their respective
  files, both past the old fixed window, producing plausible-sounding but
  ungrounded AI summaries. `graph.relation_enrichment_candidates` gained
  a `target_doc_artifact_name` column to support this. See `decisions/0042`.

- Planning: `planning/phase-28-center-relationship-excerpts-on-the-
  actual-match.md` — a future plan found via a live `/discovery` session
  testing Phase 26/27's real output quality. `relation_enrichment.
  select_candidates` always sends a spec doc's first 4,000 characters as
  grounding, regardless of where the mechanical match actually is;
  confirmed with real data that both of this repo's currently-enriched
  vendor-doc relationships got ungrounded AI summaries as a result (the
  real match sits at character 7,870 of one file and 91,374 of another,
  both past the fixed window). `planning/ROADMAP.md`'s Post-MVP table
  updated: 28 appended after 27, no renumbering. Planning only, no code
  changed.

- **Phase 27**: a cloned vendor's own embedded upstream doc files
  (`README*.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`,
  `MIGRATION.md` at its clone root, `vendor/<name>/src/`) are now
  registered as `doc_artifacts` rows (`kind='vendor_doc'`,
  `origin='vendor_upstream'` — new CHECK values, `_SCHEMA_VERSION` "3" →
  "4"), via new `doc_mapping.collect_vendor_upstream_doc_artifacts`. Every
  downstream mechanism picks them up unchanged: they're eligible
  `mentions_artifact` targets for Phase 21's mention-detection and
  Phase 22's AI-enriched relationship summaries, appear in `query
  relations`, and `check` gained a new "Vendor docs with no detected
  relations" section. Root-level files only, deliberately not a
  recursive scan of a vendor's own `docs/` folder. Confirmed against
  this repo: 28 real vendor-doc rows registered across all four tracked
  vendors, with no impact on Phase 15's existing `vendor/`
  usage-detection exclusion. See `decisions/0041`.

- **Phase 26**: `usage.detect_python_imports` now upgrades a plain
  `import X` (or `import X as alias`) to symbol-level usage evidence when
  the code actually accesses an attribute of it (`X.Attr(...)`) — an
  additive second AST pass, the vendor-level `DetectedImport` from the
  `import` statement itself is unchanged. Only the immediate attribute
  off the bound name resolves (`X.sub.Attr` → `sub`, not `Attr`),
  mirroring `ImportFrom`'s existing first-dotted-component-only rule.
  Fixes real noise this repo's own `check` output had: 35 real
  `anthropic` symbols (`Anthropic`, `AnthropicError`, etc.) showing as
  "documented but unused" purely because this project imports `anthropic`
  as a module and accesses attributes on it, which the detector
  previously couldn't resolve past the module level.

- Planning: two new future phases found via a `/discovery` dogfooding
  session against this repo itself, each with its own real, confirmed
  evidence (not guessed) — `planning/phase-26-symbol-level-resolution-
  for-attribute-usage.md` (a plain `import X` followed by `X.Attr(...)`
  never resolves to a symbol-level usage edge, confirmed: all 6
  `anthropic` `uses_edges` rows in this repo have `symbol_id = NULL`,
  causing 35 real symbols to show as "documented but unused") and
  `planning/phase-27-register-embedded-vendor-docs.md` (a cloned vendor's
  own upstream docs — confirmed: 30+ real files under `vendor/*/src/` in
  this repo — have no `doc_artifacts` row at all, so Phase 21/22's
  relationship detection/enrichment never applies to them).
  `planning/ROADMAP.md`'s Post-MVP table updated: 26/27 appended after
  24/25, no renumbering needed. Planning only, no code changed.

### Fixed

- `/discovery`'s generated body overstated what its `allowed-tools`
  frontmatter guarantees: confirmed against actual Claude Code behavior
  (not assumed) that the pre-approval grant covers only the single turn
  that invokes the command — it clears once the reply is sent, and
  nothing re-applies it or blocks `Write`/`Edit`/`ExitPlanMode` on a later
  turn in the same conversation. `render_discovery_command` (`commands.py`)
  and `architecture/overview.md` now say so explicitly and instruct Claude
  to hold the read-only posture deliberately for the rest of the session,
  not assume the frontmatter still enforces it past the first reply. See
  `decisions/0040`.

### Added

- **Phase 23, Part A** (packaging/release readiness — the actual PyPI
  publish is Part B, held for explicit confirmation): `pyproject.toml`
  bumped to `version = "1.0.0"`, `classifiers` corrected to
  `Development Status :: 4 - Beta`, `[project.urls]` added
  (Homepage/Repository/Issues). `README.md`'s Status section and feature
  list updated to reflect phases 0-22 all `done`, including the Phase
  21/22 spec-doc relationship detection that had no README mention at
  all. New `examples/toy-project` — a small real project with real
  `requests`/`click` usage, plus `examples/README.md` quoting real
  `codecompass` output captured against it. New `decisions/0039`: v1.0
  ships without a dedicated docs site (`README.md` + `docs/*.md` on
  GitHub only), a deliberate, revisitable deferral, not an oversight.
  Verified: a real `python -m build` wheel installs cleanly into a fresh
  throwaway venv independent of this repo's editable dev install, and
  `codecompass --help` runs from it.

- **Phase 22**: batched AI enrichment now runs over Phase 21's
  mechanically-detected spec-doc relationships too, gated strictly on
  those already-proven candidates (new `relation_enrichment.py`, sibling
  to `enrichment.py`, same batched forced-tool-use call shape). Folded
  into the existing Phase B cost/consent prompt — one disclosure, one
  `--yes`/`--budget` gate, covering vendor/symbol enrichment and
  relationship enrichment together. `codecompass query relations` now
  shows each relation's AI-enriched `ai_summary` when one exists, else
  "mentioned, not yet enriched". New `doc_relation_enrichment` table is
  keyed by plain natural-key strings with **no foreign key** to
  `doc_artifacts` (which is fully deleted/reinserted every rebuild, unlike
  the upserted `vendors`/`symbols`) — see `decisions/0038` for why, and
  for the non-negotiable boundary this phase establishes: the AI-generated
  summary is written only to the graph, **never into a spec doc's own
  file** — `relation_enrichment.apply_results` doesn't even accept a
  `project_root`, so it structurally cannot write one.

- **Phase 21**: a project's own human-authored spec docs (README,
  `ARCHITECTURE.md`, `docs/**/*.md`, `architecture/**/*.md`,
  `decisions/**/*.md`, `spec/**/*.md`, `specs/**/*.md`, `rfcs/**/*.md`,
  `*.spec.md`) are now detected as `doc_artifacts` rows
  (`kind='spec_doc'`, `origin='project'`, new module `spec_docs.py`) and
  mechanically linked to tracked vendors and other doc artifacts
  (Skills, `.mdc` rules, dependency docs) via a new `doc_relations_edges`
  table and `doc_mapping.build_doc_relations_edges` — the same
  word-boundary mention heuristic already used elsewhere, no AI call.
  New `codecompass query relations <name>` (a spec-doc path, or a
  vendor/Skill name for the reverse lookup); `check` gained a "Spec docs
  with no detected relations" report-only section. `doc_artifacts`'
  `kind`/`origin` CHECK constraints widened (`_SCHEMA_VERSION` "2" →
  "3"). See `decisions/0037`.

### Fixed

- **Phase 20**: the root `CLAUDE.md` routing table, tool-level Skill, and
  discovery command now always refresh *after* AI enrichment finishes
  (success or budget-abort), not before — a vendor enriched during the
  same `codecompass`/`sync` invocation no longer shows stale
  pre-enrichment status until a second run. New `cli._refresh_generated_
  artifacts`, called from a `try/finally` around `_maybe_run_enrichment`
  in both `_bootstrap` and `sync`'s whole-project branch — the latter
  previously never regenerated these artifacts at all. Closes the
  graph/enrichment ordering gap flagged after Phase 18 and confirmed
  during this project's first live enrichment run.

### Added

- Planning: `planning/v1.0-initial-release-roadmap.md` — the path-to-v1.0
  umbrella plan, plus two new phase plans it introduces: `planning/
  phase-21-spec-doc-detection-and-relationship-graph.md` (mechanical
  detection of a project's own README/`docs/`/`architecture/`/`decisions/`
  etc. as graph nodes, linked to dependency docs and skills via the
  existing mention-heuristic pattern) and `planning/
  phase-22-ai-enriched-cross-artifact-relationships.md` (a batched AI call
  summarizing *how* each of those mechanically-detected relationships
  connects, gated on Phase 21's candidates only, folded into the existing
  Phase B cost/consent flow, never writing to a spec doc's own file).
  `planning/ROADMAP.md`'s Post-MVP table updated: Phases 21/22 inserted;
  former Polish phase moves to 23 (now the v1.0 release phase itself);
  former routing/rollup and MCP phases move to 24/25, deferred past the
  v1.0 release line (proposed, not locked — see the roadmap doc's "Why
  this order" section). Planning only, no code changed.

- Planning: `planning/phase-20-refresh-generated-artifacts-after-
  enrichment.md` — a future plan for the remaining piece of the graph/
  enrichment ordering gap (routing table, tool Skill, `undo`/`query
  skills` freshness immediately after a vendor's first enrichment).
  `planning/ROADMAP.md`'s Post-MVP table updated: new Phase 20 inserted,
  former 20/21/22 shift to 21/22/23. Planning only, no code changed.

### Fixed

- The tool-level Skill (`.claude/skills/codecompass/SKILL.md`) listed
  `codecompass query vendors|vendor|symbol|skills` as one bare line with
  no guidance on what each subcommand does, no mention of `--json`, and
  no pointer to `context-graph.db`'s schema for ad hoc queries — found by
  direct inspection, unlike `/discovery`'s much richer equivalent
  content. `skill.py`'s `render_tool_skill` now explains each `query`
  subcommand, the raw-`sqlite3` escape hatch, and points at `/discovery`.

- **`codecompass sync` crashed on any second run once a vendor had been
  git-cloned** — `source_resolution._git_clone`'s naive
  `shutil.rmtree(dest)` hit a `PermissionError` re-cloning over a git
  repo's own read-only `.git/objects/pack/*` files (Windows). Found via
  the first real end-to-end run of this project against a live
  Anthropic API key. Fixed by promoting `undo`'s (Phase 18,
  `decisions/0036`) best-effort rmtree helper —
  clears the read-only bit and retries, reports genuine failures instead
  of guessing — to `source_resolution.rmtree_best_effort`, shared by
  both callers instead of duplicated; `cli.py`'s local copy removed.
- **A vendor's `OVERVIEW.md` never appeared on its first-ever
  enrichment**, only from the *next* whole-project sync — `sync_vendor`
  (Phase A) only ever writes it from an enrichment record that already
  existed *before* that run, and on a first enrichment nothing was in
  the graph yet when Phase A ran. Also found via the same live run.
  Fixed: `enrichment.apply_results` (Phase B) now writes `OVERVIEW.md`
  itself, right where `conversational_overview` is freshest, instead of
  waiting a full sync cycle. Regression test simulates a vendor's first
  enrichment with no prior `OVERVIEW.md` on disk.

- A `depth = surface` vendor whose source clone fails no longer shows a
  misleading "## Description — Description unavailable" section in its
  `CLAUDE.md` — `_render_description_section` now gates on `depth is
  FULL` before ever looking at `description_error`, since Phase 13 made
  cloning (and therefore `description_error`) universal, decoupling it
  from whether a description was ever attempted. Caught during
  independent verification of Phase 13, not by automated tests (nothing
  before Phase 13 could produce this combination, so nothing asserted
  its absence) — see `planning/v0.2-implementation-execution-plan.md`
  for the reinforced verification step this prompted.

### Fixed

- A whole-project `sync` re-run silently erased Phase B's AI-enrichment
  content from `CLAUDE.md` — `sync_vendor` rebuilt every vendor's file
  from scratch via a digest that never carried enrichment data, gated on
  a `Depth` value nothing has set since `promote` was removed in Phase
  15. Shipped on `main` since that phase; caught while implementing
  Phase 16. Fixed per `decisions/0035`: `sync_vendor` now reads a
  vendor's current enrichment from the context graph before building its
  digest, so a from-scratch re-render reproduces existing enrichment
  instead of erasing it. Regression test syncs an enriched vendor twice
  and confirms the Description section survives.
- `usage.py`'s project-source scan didn't exclude `vendor/` — since
  Phase 13, every tracked vendor's own upstream source clones into
  `vendor/<name>/src/` inside that same walk, and a vendor's own source
  very often self-references its own package name, registering as a
  false-positive "the project uses this vendor" signal for nearly every
  vendor on every run. Fixed by adding `"vendor"` to
  `_PROJECT_PRUNE_DIR_NAMES` (Phase 15), with a regression test. Caught
  by the implementing subagent's own end-to-end testing before it ever
  reached the orchestrating session's independent review.
- `chat.py`'s "no grounded description yet" hint still referenced
  `codecompass promote <vendor>`, a command removed in Phase 15 — reworded
  to point at `sync`.

### Added

- **Phase 19: chat demotion + governance docs — MVP (v0.2) complete,
  all eleven phases (9-19) `done`.** Implements
  `planning/phase-19-chat-demotion-and-governance-docs.md` and
  `decisions/0034`. `README.md` rewritten around the v0.2 primary
  workflow (bare `codecompass` → clone + disclosed usage-driven
  enrichment → `codecompass query`/`/discovery`/generated Skills,
  `chat` explicitly secondary). `architecture/overview.md`'s opening
  summary, "Chat REPL" (now framed per `decisions/0034`, historical
  pointer to superseded `decisions/0012` left unedited — append-only),
  "Two consumption modes", "Multi-tool export", "Staleness checking",
  "Retrofitting to existing projects", "Cost model", and "Known
  footguns" sections, plus `docs/cli-reference.md`, corrected against
  the fully-built system — roughly a dozen stale `promote`/`Depth`/
  pre-rework references found and fixed in total, including two
  present-tense instructions to run a deleted `codecompass promote`
  command. `chat.py`/`skill.py`/`discovery.py` docstrings updated to
  match (no logic changes). `pytest`: 366 passed, 1 skipped throughout;
  `ruff check .` clean.
- **Phase 18: `undo` command** — implements
  `planning/phase-18-undo-command.md` and new `decisions/0036`. New
  `codecompass undo [--yes] [--dry-run]`: graph-backed enumeration
  (every `doc_artifacts` row tagged `codecompass_tool`/
  `codecompass_vendor`, never `third_party`) with a pattern-based
  fallback when no `context-graph.db` exists yet; strips root
  `CLAUDE.md`'s routing-table marker block in place rather than deleting
  the file; never runs a git command or commits on the user's behalf.
  Fixes a Windows-specific bug found during implementation: naive
  `rmtree` silently left a cloned vendor's read-only `.git/objects/`
  files behind while reporting success — `_rmtree_best_effort` clears
  the read-only bit, retries, and reports genuine leftovers instead.
  `pytest`: 366 passed, 1 skipped; `ruff check .` clean.
- **Phase 17: `/discovery` slash command** — implements
  `planning/phase-17-discovery-slash-command.md`. New
  `src/codecompass/commands.py`, generating
  `.claude/commands/discovery.md`: `allowed-tools` scoped to
  `Read`/`Grep`/`Glob` plus a narrow `codecompass query`/`check`/`sqlite3
  context-graph.db` allowlist (no `Write`/`Edit`), with the read-only
  constraint also repeated in plain instructional text. `graph.py`'s
  `doc_artifacts.kind` widened to include `'slash_command'`
  (`_SCHEMA_VERSION` bump + migration for an already-existing database).
  `skill_scan.py` indexes the new file. Two minor, documented scope gaps
  found and correctly left alone rather than silently expanded: the
  plan's claimed three `write_tool_skill` trigger points are actually
  two; `query skills` doesn't yet surface the new artifact kind.
  `pytest`: 355 passed, 1 skipped; `ruff check .` clean.
- **Phase 16: retire `Depth`** — implements `planning/phase-16-retire-depth.md`
  and `decisions/0031`/`0035`. `core.py`'s `Depth` enum deleted;
  `VendorConfig` narrowed to `(name, ecosystem)`; `config.py` tolerates a
  legacy `depth =` line in `vendor.toml` silently rather than erroring;
  `discovery.py`/`cli.py` updated to match.
  `src/codecompass/grounded_description.py` (and its test file) deleted
  — `codecompass.enrichment` (Phase 14) fully replaces its role. `pytest`:
  340 passed, 1 skipped (down from 361 — the deleted module's tests and
  two now-obsolete budget tests account for the difference); `ruff
  check .` clean; `grep -rn "Depth\b" src/` returns zero hits.
- **Phase 15: CLI rewire** — implements `planning/phase-15-cli-rewire.md`
  and `decisions/0033`. `promote` removed entirely. Bare `codecompass`
  and whole-project `sync` gain `--yes`/`--budget` and auto-trigger Phase
  B (disclose/confirm, then batched enrichment) right after Phase A's
  free work. New `query {vendors|vendor|symbol|skills}` command group
  (Rich tables or `--json`). `check` gains report-only coverage-gap
  sections — unused vendors, documented-but-unused/used-but-undocumented
  symbols, orphaned third-party skill mentions — **`--strict`'s exit code
  unaffected**, still version-drift severity only. `index.py`/`skill.py`
  migrated from `Depth`-keyed to graph-derived enrichment status (new
  `graph.has_enrichment`). `pytest`: 361 passed, 1 skipped; `ruff
  check .` clean.
- **Phase 14: batched enrichment (Phase B)** — implements
  `planning/phase-14-batched-enrichment.md`. New
  `src/codecompass/enrichment.py`: `select_candidates` (two-tier
  DB-hash + `CLAUDE.md`-file-hash cache check, per `decisions/0032`),
  `plan_batches`, batched forced-tool-use enrichment
  (`run_enrichment_batches`), `apply_results` (writes to the graph,
  updates `CLAUDE.md` in place via new `claude_md.
  update_description_section`/`read_enrichment_hash`, generates
  per-vendor Skill/`.mdc` via a minimal `VendorDigest`),
  `estimate_cost`/`check_budget` reworked to scale with batch count.
  Library-only — not yet wired into `cli.py`/`sync.py` (Phase 15).
  `grounded_description.py` untouched, still active for `depth = full`
  vendors until Phase 15/16. `pytest`: 336 passed, 1 skipped; `ruff
  check .` clean.
- **Phase 13: universal source cloning** — implements
  `planning/phase-13-universal-source-cloning.md` and `decisions/0033`.
  `sync.sync_vendor` restructured: cloning now runs unconditionally for
  every vendor (previously gated on `depth = full`), independent of
  grounded-description generation (still `depth`-gated, additionally
  requiring this run's own clone to have succeeded). `FILETREE.md`/
  `filetree.json`/the symbol index now render from the clone root when
  available, with the existing local-install fallback — a real, visible
  output change for every vendor, not just previously-`FULL` ones.
  `pytest`: 299 passed, 1 skipped; `ruff check .` clean.
- **Phase 12: doc & wide skill mapping** — implements
  `planning/phase-12-doc-and-wide-skill-mapping.md`. New
  `src/codecompass/doc_mapping.py` (`collect_vendor_doc_artifacts`,
  `build_documents_edges`, `build_routes_via_edges`,
  `build_depends_on_edges`) and new `src/codecompass/skill_scan.py`
  (`scan_skills` — indexes **every** skill under `.claude/skills/` and
  `.cursor/rules/`, not just codecompass-generated ones, via a minimal
  custom frontmatter extractor with no new YAML dependency;
  `build_skill_mentions_edges` — word-boundary, not substring, matching
  against tracked vendor names and source-file basenames).
  `sync.rebuild_project_graph` now populates every table in the graph,
  not just vendors/symbols/uses. Manually confirmed against this repo's
  own `.claude/skills/codecompass/SKILL.md` and `vendor/*/deptree.json`.
  `pytest`: 296 passed, 1 skipped; `ruff check .` clean.

- **Phase 11: project-source usage detection** — implements
  `planning/phase-11-project-source-usage-detection.md`. New
  `src/codecompass/usage.py`: `detect_python_imports` (`ast`-based),
  `detect_npm_imports`/`detect_rust_imports` (regex), `DetectedImport`,
  `resolve_project_usage`. `filetree._iter_files` made public as
  `iter_source_files(root, *, prune_dirs=..., prune_globs=...)`, zero
  behavior change for existing callers. New
  `sync.rebuild_project_graph`, wired into `cli.py` at exactly two
  whole-project call sites (bare bootstrap, `sync` with no vendor arg) —
  `sync <vendor>` and `check --fix` leave the graph untouched, per
  `decisions/0025`. Manually confirmed against this repo's own source:
  correct symbol-level resolution (e.g. `rich.console.Console`), correct
  zero-usage detection for a subprocess-only dependency (`pipdeptree`),
  and single-vendor sync leaves `context-graph.db` untouched. `pytest`:
  270 passed, 1 skipped; `ruff check .` clean.

- **Phase 10: SQLite graph foundation** — implements
  `planning/phase-10-sqlite-graph-foundation.md` and `decisions/0032`.
  New `src/codecompass/graph.py`: the full 9-table + `meta` schema,
  `init_schema`, `open_graph`, 9 row dataclasses, `rebuild_deterministic`
  (upserts vendors/symbols by natural key so `vendor_enrichment`/
  `symbol_enrichment` survive a rebuild despite their `ON DELETE CASCADE`
  foreign keys — a real bug caught during implementation, not anticipated
  in the plan, now locked in with dedicated regression tests), 7 query
  functions (`unused_vendors`, `documented_but_unused`,
  `used_but_undocumented`, `vendor_profile`, `symbol_profile`,
  `skills_index`, `enrichment_candidates`), and
  `record_enrichment`/`record_symbol_enrichment`. Library-only — not yet
  called from `sync.py`/`cli.py` (starts Phase 11). `context-graph.db`
  added to `.gitignore`. `pytest`: 241 passed, 1 skipped; `ruff check .`
  clean.

### Changed

- **MVP (v0.2) phase order corrected**: "Retire `Depth`" moves from
  Phase 10 to **Phase 16** — it was originally sequenced before anything
  existed to replace the eight call sites that currently read it
  (`sync.py`, `grounded_description.py`, `cli.py`, `index.py`,
  `skill.py`, `claude_md.py`, `chat.py`, `discovery.py`); it's only safe
  once phases 13-15 replace all of them. The graph/usage-detection/
  mapping/cloning/enrichment/CLI phases shift from 11-16 down to 10-15;
  phases 17-19 unaffected. Bookkeeping only, no code — caught and fixed
  before any Phase 10 code was written. See `planning/ROADMAP.md`'s
  renumbering note for the full old→new table, including which of
  `decisions/0031`-`0034`'s internal "Phase N" citations are now stale
  (not editable — append-only).
- **Phase 9: renamed the package from `depcompass` to `codecompass`**
  (`decisions/0029`, `planning/phase-9-rename-to-codecompass.md`) —
  mechanical only, zero behavior change. `src/depcompass/` moved to
  `src/codecompass/` (`git mv`, preserving blame); the console script is
  now `codecompass`; every internal import, the root `CLAUDE.md` routing
  marker (`<!-- codecompass:start/end -->`), the tool-level Skill
  (`.claude/skills/codecompass/`), and all prose in `README.md`,
  `CONTRIBUTING.md`, `docs/`, and `architecture/overview.md` updated to
  match. `decisions/*.md` and `CHANGELOG.md`'s prior entries are
  deliberately untouched (append-only / historical record). Full test
  suite (218 passed, 1 skipped) and `ruff check .` both green under the
  new name; verified end-to-end with a fresh `pip install -e ".[dev]"`
  and a bare `codecompass` + `codecompass sync` run against this repo
  itself.
- Phase 10 planning: `planning/phase-10-sqlite-graph-foundation.md` — the
  new `graph.py` module (SQLite schema, `init_schema`,
  `rebuild_deterministic`, read-only query functions), per
  `decisions/0032`. Library-only; not yet wired into `sync.py`/`cli.py`.
  Planning only, no code changed.
- **Phases 11-19 planning: the rest of MVP (v0.2) is now fully
  implementation-ready.** Nine new plan files, each grounded in the
  actual current source, covering the whole arc in dependency order:
  `phase-11-project-source-usage-detection.md` (new `usage.py`;
  `filetree._iter_files` becomes public `iter_source_files` with
  configurable prune sets; new `sync.rebuild_project_graph`, wired into
  bare bootstrap and whole-project `sync` only), `phase-12-doc-and-
  wide-skill-mapping.md` (new `doc_mapping.py` + `skill_scan.py`,
  including the project-wide, not-just-codecompass-generated skill scope
  expansion; word-boundary matching, no new YAML dependency),
  `phase-13-universal-source-cloning.md` (splits cloning from grounded-
  description generation in `sync_vendor` — cloning becomes
  unconditional, description stays `depth`-gated until Phase 15),
  `phase-14-batched-enrichment.md` (new `enrichment.py` replacing
  `grounded_description.py`; batched candidate selection, two-tier
  cache-hash skip logic, a new `claude_md.update_description_section`
  for in-place `CLAUDE.md` updates instead of full `VendorDigest`
  reconstruction), `phase-15-cli-rewire.md` (the integration phase:
  `promote` removed, bare `codecompass` gains `--yes`/`--budget` for
  Phase B's auto-triggered consent gate, new `query` command group,
  `check`/`index`/`skill.py` migrated to graph-backed enrichment status),
  `phase-16-retire-depth.md` (now safe — the `Depth` enum/field finally
  removed, `vendor.toml`'s legacy `depth=` line tolerated on read),
  `phase-17-discovery-slash-command.md` (new `commands.py`, `/discovery`
  generated alongside the tool Skill), `phase-18-undo-command.md` (new
  `undo [--yes] [--dry-run]`, graph-backed enumeration with a
  pattern-based fallback when no graph exists yet, never commits), and
  `phase-19-chat-demotion-and-governance-docs.md` (README/architecture
  rewritten around the graph+Skills+`/discovery` as primary, MVP (v0.2)
  closes out). Every `planning/ROADMAP.md` row for phases 11-19 flips
  from `not started` to `planned` with its plan file linked. Planning
  only, no implementation code changed — implementation proceeds
  strictly in this order starting from Phase 10, since each later
  phase's plan assumes the previous ones' code already exists.
- `planning/ROADMAP.md` renumbered: the context graph (Phase 9,
  sub-phases 9a-9e) is inserted ahead of the previously-unplanned
  project-root REPL routing/rollup work, which shifts from Phase 9 to
  **Phase 10** (former Phase 10/11 — polish, MCP — shift to 11/12).
  Bookkeeping only, no code; all shifted phases were `not started`, so
  this is a clean renumber, not a rewrite of in-flight work — same
  precedent as the Phase 7-era renumbering below.
- MVP milestone expanded from phases 0-6 to phases 0-8 (`decisions/0022`)
  — bookkeeping only, no code. Phase 8 (the chat REPL, `decisions/0012`'s
  "actual product") structurally depends on Phase 7's outputs (Skill
  files, dual-audience content shape), so both move from
  `planning/ROADMAP.md`'s Post-MVP table into its MVP table together;
  `v0.1` now tags only once Phase 8 is `done`, not Phase 6.
  `CLAUDE.md` §6, `CONTRIBUTING.md`, `docs/cli-reference.md`,
  `architecture/overview.md`, and `README.md` updated to match; no phase
  was renumbered, only table membership and milestone-boundary text.

### Added

- **MVP (v0.2) planning: rename to codecompass, retire `promote`/`Depth`,
  SQLite relationship graph, `/discovery`, `undo`** — planning only, no
  code changed. Supersedes the Phase 9 context-graph planning entry below
  (that plan was never implemented; its four plan files are deleted —
  recoverable from git history — while its five ADRs stay, append-only;
  see `planning/ROADMAP.md`'s "Superseded planning" note). New
  `planning/phase-9-rename-to-codecompass.md`
  (mechanical rename, zero behavior change) and six new ADRs:
  `decisions/0029` (rename announcement), `decisions/0030` (MVP milestone
  redefined — v0.2 spans phases 9-19, `planning/ROADMAP.md`'s new MVP
  (v0.2) table), `decisions/0031` (`Depth` retired — enrichment becomes
  usage-driven, not a manual per-vendor toggle, superseding
  `decisions/0001`), `decisions/0032` (context graph moves from a single
  JSON file to SQLite, superseding `decisions/0024`), `decisions/0033`
  (`promote` retired — universal source cloning plus an auto-triggered,
  still cost-disclosed/confirmable batched enrichment step replaces it,
  superseding `decisions/0018` and partially `decisions/0017`), and
  `decisions/0034` (chat demoted from "the actual product" to a secondary,
  unchanged-code subcommand — the graph, generated Skills, and the new
  `/discovery` command become primary, superseding `decisions/0012`).
  `planning/ROADMAP.md` restructured: former Post-MVP phases 9a-9e
  superseded (retained, not deleted); new MVP (v0.2) table added spanning
  phases 9-19 (rename → depth retirement → SQLite graph foundation →
  usage detection → doc/skill mapping → universal cloning → batched
  enrichment → CLI rewire → `/discovery` → `undo` → chat demotion/docs);
  former routing/rollup, polish, and MCP-server phases renumbered
  10→20, 11→21, 12→22.
- Phase 9 planning (superseded — see entry above): context graph
  (sub-phases 9a-9d) — planning only, no
  code changed. New `planning/phase-9a-vendor-presence-graph.md` (vendor-
  level `uses` edges, dead-dependency detection surfaced via `check`),
  `planning/phase-9b-symbol-usage-graph.md` (symbol-level `uses`, reusing
  existing per-ecosystem symbol extraction rather than re-deriving it),
  `planning/phase-9c-doc-skill-mapping.md` (`DocArtifact` nodes,
  `documents`/`routes_via`/`depends_on` edges, coverage-gap reporting),
  and `planning/phase-9d-llm-enrichment.md` (optional, off-by-default
  LLM enrichment: usage-purpose labels, clustering, a `DOCUMENTS` quality
  delta, file-role summaries, `EXPLAINS` chunk retrieval, a
  trigger-accuracy proxy). Five new ADRs, `decisions/0024`-`0028`:
  context-graph storage model (single root-level `context-graph.json`),
  its cache-invalidation trigger (rebuilds only on bare `sync`/bootstrap,
  never incrementally), Phase 9d's optional/deterministic-gated posture
  (explicitly not closing `decisions/0013`'s outstanding trigger-accuracy
  harness item), `EXPLAINS`-vs-`decisions/0023` reconciliation
  (coexistence — `chat.py` is untouched), and usage-cluster
  classification's draft-only, never-auto-written posture (deferred to a
  future Phase 9e, not part of this pass). A future Phase 9e is
  identified in `planning/ROADMAP.md` but deliberately not planned in
  implementation detail this session — it needs real field data from 9d.
- Single-vendor chat REPL (Phase 8): implements
  `planning/phase-8-chat-repl.md` and `decisions/0023` — **all eight MVP
  phases (0-8) are now complete.** New `depcompass chat <vendor>`: a
  terminal REPL that grounds every answer on the vendor's already-
  persisted `vendor/<name>/CLAUDE.md` (required) and `OVERVIEW.md`
  (optional, present once `promote`d), read directly as text — never
  calls `sync`/`promote` itself, so starting a session never re-clones
  or re-runs AI generation. Works at any depth; a vendor with no
  `OVERVIEW.md` yet gets thinner grounding plus a one-line hint to run
  `promote`, not a hard block. Plain multi-turn text completion against
  `claude-haiku-4-5-20251001` — no forced tool-use, no file-exploration
  loop. New `src/depcompass/chat.py`. Bare project-root `chat` (no
  vendor name), Tier 1/2 routing, and the whole-project dependency
  rollup remain Phase 9, not built here.
- Phase 8 plan (`planning/phase-8-chat-repl.md`) and `decisions/0023` —
  planning only, no code changed (written in the session before this
  implementation).
- Zero-question bootstrap & `promote` (Phase 7): implements
  `planning/phase-7-bootstrap-and-promote.md` and `decisions/0017`-
  `0021` — MVP phases 0-7 are now complete. Bare `depcompass` (no
  subcommand) auto-discovers manifests (`package.json`, `pyproject.toml`,
  new `requirements.txt` support, `Cargo.toml`), writes/refreshes
  `vendor.toml` at `depth = surface` with no prompts or AI calls, and
  regenerates trees, the routing table, and a new unconditional
  tool-level Skill (`depcompass.skill.write_tool_skill`,
  `decisions/0020`, `.claude/skills/depcompass/SKILL.md`). Refreshing an
  already-bootstrapped project only syncs newly-discovered vendors —
  already-tracked ones, including any `depth = full`, are left untouched.
  New `depcompass promote <vendor> [--yes]`: the sole cost-disclosure/
  confirmation point (`decisions/0018`); on confirmation, escalates a
  vendor to `depth = full`, resolves and clones its real upstream
  repository (`depcompass.source_resolution`, `decisions/0021`),
  generates a grounded description (`depcompass.grounded_description`,
  replacing `gap_analysis.py` — `decisions/0019`), writes its per-vendor
  Skill and Cursor `.mdc` export (`depcompass.skill`, `decisions/0013`),
  and refreshes the routing table. Idempotent on an already-`full`
  vendor. `context_path` removed from `VendorConfig`/`vendor.toml` —
  generation is now unconditional for `depth = full`, not gated on a
  project-supplied field. `VendorDigest.gap_analysis`/
  `gap_analysis_error` renamed to `technical_description`/
  `description_error`. `vendor/<name>/src/` is now cloned from the
  vendor's upstream repository for `depth = full` vendors (refines
  `decisions/0004`'s snapshot-not-reference concern), falling back to
  the old local-install-sourced copy if source resolution fails. Each
  adapter gained `repository_url()`, resolved from already-local package
  metadata (no registry network call): npm's `package.json` `repository`
  field (respecting monorepo `directory`), Python's installed
  `Project-URL` metadata, Cargo's `cargo metadata` `repository` field. A
  PyPI vendor with no resolvable repository URL fails `promote` loudly
  rather than falling back to a source tarball.
- Phase 7 plan (`planning/phase-7-bootstrap-and-promote.md`) and five new
  ADRs — planning only, no code changed. Reconciles an external MVP-
  redefinition design doc against actual repo state (correcting the
  doc's mistaken premise that `depth = full` generation compares a
  dependency's source against the model's own training knowledge — the
  real mechanism, superseded here, compared API surface against a
  project-supplied `context_path`). `decisions/0017`: bare `depcompass`
  auto-discovers manifests and bootstraps `vendor.toml` at `SURFACE`
  with no prompts or AI calls; re-running it refreshes idempotently.
  `decisions/0018`: new `depcompass promote <vendor>` becomes the sole
  point that costs money or requires confirmation, bundling source
  resolution, generation, Skill + Cursor `.mdc` export, and an `index`
  refresh. `decisions/0019`: `FULL`-depth generation becomes grounded
  description sourced from material retrieved at `promote` time,
  replacing `context_path`-gated gap analysis (`decisions/0003`'s Haiku
  model-tier choice is unaffected). `decisions/0020`: a templated,
  unconditionally-generated tool-level Skill distinct from per-vendor
  Skills. `decisions/0021`: PyPI source resolution fails loudly rather
  than falling back to a source tarball when no repository URL resolves.
  `planning/ROADMAP.md`'s former Phase 9 (Skills + Cursor export) and
  Phase 10 (`init` bulk-discovery refinement) rows are folded into the
  new Phase 7 and removed as separate rows; later phases renumbered
  accordingly (all were `not started`).
- Staleness checking (Phase 6): `depcompass check [--strict] [--fix]` is
  real — the last MVP phase, so MVP phases 0-6 are now complete. New
  `depcompass.staleness` module: `check_all`/`check_vendor` compare a
  vendor's persisted `**Installed version:**` against the ecosystem
  adapter's live read, classifying the delta via a small custom
  `major.minor.patch` parser into `Severity.NONE`/`PATCH`/`MINOR`/`MAJOR`/
  `UNKNOWN` per `decisions/0005`'s patch-silent/minor-warns/major-hard-
  fails policy (`UNKNOWN` — an unparseable version string on either side —
  is treated as a hard-fail case). Also detects transitive-only
  (DEPTREE) drift by diffing a vendor's persisted `deptree.json` against a
  freshly built live tree when the vendor's own root version is
  unchanged — informational only, never affects `--strict`'s exit code.
  Bare `check` (no flags) is report-only and always exits 0; `--strict` is
  the CI gate (non-zero on `MAJOR`/`UNKNOWN`/a failed live-version read);
  `--fix` regenerates every stale vendor via the same `sync_vendor` `sync`
  itself uses (including gap analysis for `depth = full` vendors),
  isolating one vendor's adapter failure from the rest of the batch.
  `--strict` and `--fix` are mutually exclusive. New shared
  `claude_md.read_installed_version` helper, de-duplicating a regex
  `index.py` previously kept privately.
- AI-gated gap analysis (Phase 5): `depcompass.gap_analysis` — a single
  forced-tool-use Anthropic call per qualifying vendor
  (`generate_gap_analysis`), pinned to the dated snapshot
  `claude-haiku-4-5-20251001` rather than `decisions/0003`'s rolling
  alias, producing structured dual-audience output (technical analysis +
  conversational overview + an optional action pointer) in one call/cost
  (`decisions/0012`); `estimate_cost`/`check_budget` support `sync
  --budget <amount>`, aborting the whole run before any API call if
  projected cost is too high. `VendorDigest` gains
  `conversational_overview`, `gap_analysis_error`, `action_pointer_file`,
  and `action_pointer_note`. `sync_vendor` calls gap analysis for `depth
  = full` + `context_path` vendors, catching failures locally (the
  vendor still gets its full deterministic output, with an explicit
  "unavailable" note in `CLAUDE.md`) so one bad call doesn't block the
  rest of `sync`; a successful call additionally writes a new
  `vendor/<name>/OVERVIEW.md`. `claude_md.py`'s Gap analysis section is
  back, no longer omitted. `filetree.py`'s renderers gain an optional
  `action_pointer` parameter, closing Phase 3's deferred FILETREE-to-
  gap-analysis cross-linking loop. New ADR `decisions/0016` records that
  no test in this project ever makes a real Anthropic API call.
- Initial project scaffolding (Phase 0): MIT license, Python packaging
  (setuptools, `src/depcompass/` layout, `requires-python >=3.11`),
  process-rules `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`,
  `architecture/overview.md`, nine architecture decision records
  (`decisions/0001`-`0009`), forward-looking `docs/cli-reference.md` and
  `docs/config-schema.md`, and an empty `tests/` skeleton. No CLI
  functionality is implemented yet.
- Core data models and `vendor.toml` parsing (Phase 1): `depcompass.core`
  (`VendorConfig`, `Ecosystem`, `Depth`, `DepNode`, `VendorDigest`),
  `depcompass.config` (fail-fast `vendor.toml` parsing via `tomllib`), and
  a `depcompass.cli` skeleton with all 5 planned commands registered as
  stubs. Two new ADRs (`decisions/0010`, `decisions/0011`).
- `planning/ROADMAP.md`: a full-roadmap phase-status table (all 13
  phases, MVP milestone vs post-MVP), distinct from `planning/CONTEXT.md`'s
  current-phase-only session-resumption view.
- Phase 2 plan (`planning/phase-2-ecosystem-adapters.md`): scopes the
  `EcosystemAdapter` ABC and npm/Python/Cargo adapter implementations.
  Adapter code itself is not yet implemented.
- Deterministic tree generation (Phase 3): `depcompass.symbols`
  (`Symbol(name, purpose)` plus `extract_python_symbols`,
  `extract_rust_symbols`, a new `extract_npm_symbols`, and
  `purpose_for_file` with a generic comment-marker fallback);
  `depcompass.deptree` (`render_deptree_markdown`/`render_deptree_json` —
  diamond-dependency dedup, dev-only collapsing to a count, an explicit
  depth-cap collapse notice); `depcompass.filetree`
  (`render_filetree_markdown`/`render_filetree_json`/`build_symbol_index`
  — pruned directory walk, per-file purpose annotations, a capped flat
  symbol index). New ADR `decisions/0015` records the reuse-adapter-
  parsing extraction strategy. `adapters/cargo.py` and `adapters/python.py`
  now call into `symbols.py` instead of keeping private extraction copies.
- Real `init`/`sync`/`index` commands (Phase 4): `depcompass.adapters.get_adapter`
  dispatch; `depcompass.claude_md.render_vendor_claude_md` (per-vendor
  `CLAUDE.md` template — Metadata with the load-bearing `**Installed
  version:**` line, Grounding preamble, API surface, Known gotchas
  sourced from `DepNode.side_effects`, Quick links; Gap analysis section
  omitted until Phase 5); `depcompass.sync` (`sync_vendor`/`sync_all` —
  per-vendor orchestration writing `FILETREE.md`/`DEPTREE.md`/
  `filetree.json`/`deptree.json`/`CLAUDE.md` under `vendor/<name>/`, plus
  a pruned `vendor/<name>/src/` snapshot copy for `depth = full`);
  `depcompass.index` (`load_routing_rows`/`render_routing_table`/
  `update_root_claude_md` — idempotent marker-based routing-table
  injection that reads persisted per-vendor `CLAUDE.md` files rather than
  re-running `sync`); `depcompass.discovery` (`discover_npm`/
  `discover_python`/`discover_cargo`/`write_vendor_toml` — manifest-based
  `vendor.toml` bootstrap for `init --scan`, erroring rather than
  overwriting an existing file). `VendorDigest` gains a `side_effects`
  field. `cli.py`'s `init`/`sync`/`index` commands are wired to this real
  logic; `_write_claude_md` stub removed.
- Ecosystem adapters (Phase 2): `depcompass.adapters` — `EcosystemAdapter`
  ABC and a shared `_run_json` subprocess seam (`base.py`); `NpmAdapter`,
  `PythonAdapter`, and `CargoAdapter` implementing `installed_version`,
  `source_location`, `readme_and_api_surface`, and `dependency_tree`
  against `npm ls`, `pipdeptree`, and `cargo metadata` respectively.
  `pipdeptree` added as a real dependency. New ADR `decisions/0014`
  records the fixture-mocked testing strategy, which caught two real
  cross-platform subprocess bugs during implementation (see Fixed,
  below). The Cargo adapter is unverified against real `cargo` output —
  no Rust toolchain is available in this dev environment.

### Fixed

- `_run_json`'s subprocess seam now resolves the target tool via
  `shutil.which` before invoking it, fixing two real bugs surfaced by
  Phase 2's live smoke tests: on Windows, a bare `npm` couldn't be
  launched by `subprocess.run` without a shell (it resolves to a `.cmd`
  shim); a bare `pipdeptree` wasn't reliably on `PATH` outside an
  activated venv (now invoked as `sys.executable -m pipdeptree`).

### Removed

- `depcompass.gap_analysis` module and `VendorConfig.context_path` field
  (Phase 7) — replaced by `depcompass.grounded_description` and
  `depcompass.source_resolution` (`decisions/0019`, `decisions/0021`).
  An existing `vendor.toml` with `context_path` lines still parses
  cleanly (the field is simply ignored, not rejected); `depth = full`
  no longer requires it.
- `VendorDigest.is_stale` (Phase 6) — the property, its `_stale` field,
  and the Phase-1 docstring promising a future staleness check would
  populate it. `check` (Phase 6) never builds a `VendorDigest`, so no code
  path could ever set it; `depcompass.staleness.VendorStaleness` replaces
  it as `check`'s own return type.

### Changed

- `index.py`'s `load_routing_rows` (Phase 6) now calls the new shared
  `claude_md.read_installed_version` instead of keeping its own private
  copy of the `**Installed version:**` regex — behavior-preserving,
  de-duplication only.
- `filetree.render_filetree_markdown`/`render_filetree_json` (Phase 5)
  gain an optional `action_pointer: tuple[str, str] | None = None`
  keyword — additive and non-breaking; every existing Phase 3/4 call
  site and test is unaffected.
- `docs/cli-reference.md`'s `init --scan` syntax (Phase 4): corrected from
  one flag followed by space-separated files to a repeated flag
  (`--scan a --scan b`) — the originally documented syntax isn't how a
  named Click/Typer option works.
- `index`'s implementation deviates from `planning/phase-4-sync-index-init.md`'s
  literal `render_routing_table(digests: list[VendorDigest])` signature:
  it reads persisted per-vendor `CLAUDE.md` files instead of accepting
  fresh digests, so it never re-runs `sync` — re-running `sync` inside
  `index` would make it silently pay gap-analysis AI cost once Phase 5
  lands. See `architecture/overview.md`'s Known footguns.
- `CargoAdapter.readme_and_api_surface()`'s output format (Phase 3):
  extracted items now render as `name: purpose` instead of the raw `pub
  fn ...` signature line, as a consequence of switching to
  `symbols.extract_rust_symbols`'s name-based extraction. See
  `decisions/0015`.
- `CLAUDE.md` and `CONTRIBUTING.md` now require keeping
  `planning/ROADMAP.md` in sync: added to it when a phase's plan file is
  created, marked `done` when a phase finishes.
- **Design decision, not yet shipped**: the chat REPL (Phases 7-8) is now
  designed as a primary consumption mode for vendor digests, not a
  convenience layer. Phase 5's gap analysis will produce dual-audience
  output (technical + a conversational overview, same call/cost); Phase
  8's REPL will load a project-wide dependency rollup unconditionally at
  session start rather than routing to it. See `decisions/0012`.
- **Design decision, not yet shipped**: Agent Skills become the primary
  multi-tool export target (Phase 9), one Skill per `FULL`-depth vendor,
  addressing a reliability gap in the `CLAUDE.md` routing table's soft
  "consult this digest" instruction. Cursor `.mdc` export and the
  `CLAUDE.md` routing table are retained as fallbacks, not replaced.
  Phase 8's REPL Tier 1 routing will consume the same generated Skill
  description text Phase 9 produces, rather than independently-authored
  matching, and the REPL gains an explicit escalation path to the
  generated Skill folder for questions exceeding digest-only scope. See
  `decisions/0013`.
