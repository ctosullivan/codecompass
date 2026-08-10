# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
- Phase 3 plan (`planning/phase-3-tree-generation.md`): scopes deterministic
  `FILETREE.md`/`DEPTREE.md` (+ JSON sidecar) generation from Phase 2's
  `DepNode` trees and `source_location()` paths — a new `symbols.py`
  module for per-ecosystem, no-AI purpose/symbol extraction, plus
  `deptree.py` and `filetree.py` renderers. Tree-generation code itself is
  not yet implemented.
- Phase 4 plan (`planning/phase-4-sync-index-init.md`): scopes real
  `init`/`sync`/`index` command logic — manifest-based vendor discovery,
  per-vendor orchestration (adapters + Phase 3's tree renderers + a
  pruned `vendor/<name>/src/` snapshot copy + `CLAUDE.md` templating),
  and idempotent root `CLAUDE.md` routing-table injection. Blocked on
  Phase 3 actually being implemented first; command code itself is not
  yet implemented.
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
