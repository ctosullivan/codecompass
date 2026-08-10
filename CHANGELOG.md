# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Phase 5 plan (`planning/phase-5-gap-analysis.md`): scopes the AI-gated
  gap-analysis step — a new `gap_analysis.py` (forced tool-use, dual
  technical/conversational output, model pinned to a dated Haiku 4.5
  snapshot, `--budget` pre-flight cost check), `VendorDigest` gaining
  `conversational_overview`/`gap_analysis_error`, `sync.py` wiring
  (including a new `vendor/<name>/OVERVIEW.md` output) and `claude_md.py`
  gaining back its Gap analysis section, and closing Phase 3's deferred
  FILETREE-cross-linking loop. No test will ever make a real Anthropic
  API call. Gap-analysis code itself is not yet implemented.
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

### Changed

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
