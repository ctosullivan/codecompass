# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

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

### Added

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
