# Phase 4: `sync`, `index`, `init` Commands

## Scope

**Covered:**
- `src/depcompass/adapters/__init__.py` — `get_adapter(config: VendorConfig,
  project_root: Path) -> EcosystemAdapter`, the single dispatch point from
  `config.ecosystem` to `NpmAdapter`/`PythonAdapter`/`CargoAdapter`.
- `src/depcompass/sync.py` — `sync_vendor(config, project_root) ->
  VendorDigest` (orchestrates one vendor end to end: adapter calls, Phase
  3's tree renderers, the pruned `vendor/<name>/src/` snapshot copy for
  `depth = full`, per-vendor `CLAUDE.md` rendering, writing all five
  output files) and `sync_all(configs, project_root) -> list[VendorDigest]`.
- `src/depcompass/claude_md.py` — `render_vendor_claude_md(digest:
  VendorDigest) -> str`, the per-vendor `CLAUDE.md` template.
- `src/depcompass/index.py` — `render_routing_table(digests) -> str` and
  `update_root_claude_md(project_root, table_md) -> None` (idempotent
  marker-based injection).
- `src/depcompass/discovery.py` — `discover_npm`, `discover_python`,
  `discover_cargo` (manifest → dependency names) and `write_vendor_toml`
  (hand-rolled TOML serialization), for `init --scan`.
- `src/depcompass/cli.py` — `init`, `sync`, `index` wired to real logic;
  the `_write_claude_md` stub is removed.
- Tests: `tests/test_sync.py`, `test_claude_md.py`, `test_index.py`,
  `test_discovery.py`, `test_cli.py` (new — first CLI-level tests in the
  project, via Typer's `CliRunner`).
- Same-commit doc updates: `architecture/overview.md`, `docs/cli-reference.md`,
  `docs/config-schema.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md`,
  `CHANGELOG.md`.

**Explicitly deferred:**
- Any AI call — `sync`'s gap-analysis step is Phase 5. The `--budget` flag
  documented in `docs/cli-reference.md` for cost control is a Phase 5-only
  flag and is not added to the CLI in this phase.
- Staleness comparison — `index`'s routing table Version column shows the
  recorded version plainly, with no ✅/⚠ freshness indicator. Computing
  that indicator against the live installed version is `check`'s job
  (Phase 6); partially reimplementing it here would duplicate work Phase 6
  owns.
- The Gap analysis section of the per-vendor `CLAUDE.md` template — omitted
  entirely (not a placeholder) until Phase 5 has real output to render.
- `[project.optional-dependencies]` in `init --scan`'s Python manifest
  discovery — only `[project.dependencies]` is read.
- Merging `init --scan` into an existing `vendor.toml` — the command
  errors out if the target file already exists; a merge/update mode is a
  later-phase feature.
- Anything Phase 8/9's Skill-description-driven routing eventually
  supersedes — `index`'s "Consult when" column stays templated generic
  phrasing keyed off `depth`, not content-derived (see decisions/0013).

## Blocking dependency

**Phase 3 (`planning/phase-3-tree-generation.md`) is planned but not yet
implemented** as of this plan's writing — `src/depcompass/symbols.py`,
`deptree.py`, and `filetree.py` don't exist as code. `sync.py` calls
directly into `deptree.render_deptree_markdown`/`_json` and
`filetree.render_filetree_markdown`/`_json`/`build_symbol_index`, so
**Phase 4 implementation cannot begin until Phase 3 is actually
implemented and merged.** This plan file can exist ahead of that (same
precedent as planning Phase 2 while Phase 1 was still the most recently
shipped milestone), but it's a hard sequencing gate, not a formality —
also recorded in `planning/CONTEXT.md`'s next-step note.

## Design decisions

- **`init` is in scope for this phase**, alongside `sync`/`index` —
  matches `cli.py`'s existing `_PHASE_BY_COMMAND = {"init": 4, "sync": 4,
  "index": 4, ...}` mapping and `docs/cli-reference.md`, both already
  committed to this before this plan was written. `planning/ROADMAP.md`'s
  Phase 4 row previously read "sync and index commands" without naming
  `init`; confirmed with the user this was incomplete phrasing, not a
  deliberate exclusion, and corrected in the same commit as this plan
  file.
- **`vendor/<name>/src/` snapshot pruning is looser than `FILETREE.md`'s**
  — strips `node_modules`/`dist`/`build`/`.git`-style noise only, keeps
  `test`/`tests`/`__tests__`/`fixtures` directories. A `depth = full`
  vendor is one being extended or subclassed; its own test suite is often
  exactly what someone wants to reference in the standalone `cd
  vendor/<name> && claude` mode (decisions/0004), so the snapshot
  shouldn't hide it the way `FILETREE.md`'s more aggressive navigation
  view does.
- **Known gotchas (per-vendor `CLAUDE.md`) is deterministically derived
  from `DepNode.side_effects`** — the root node's side-effects list (e.g.
  npm's postinstall-script detection, already populated by Phase 2's
  `NpmAdapter`) — rather than left empty or invented. No side effects
  detected renders a fixed "no known side effects detected" line. Reuses
  data Phase 2 already produces instead of inventing a new no-AI content
  source.
- **`vendor.toml` writing uses hand-rolled minimal TOML serialization**,
  not a new third-party TOML-writer dependency — `tomllib` (stdlib,
  already used for reading) has no write support, but `init` produces a
  fresh, comment-free draft, not an edit-in-place of a hand-authored file,
  so a full round-trip-preserving writer library isn't needed. Consistent
  with decisions/0011's minimal-dependency preference.
- **`init` errors out rather than overwriting an existing `vendor.toml`**
  — it's a bootstrap command; silently clobbering a hand-edited config is
  destructive-by-default behavior to avoid. Re-running against an
  existing file to merge is a later-phase feature, not implemented now.
- **New library modules, not logic inlined into `cli.py`** — continues the
  existing pattern where `cli.py` stays a thin Typer wrapper delegating to
  `depcompass.config`/`depcompass.adapters`/etc. `sync.py`, `claude_md.py`,
  `index.py`, `discovery.py` are flat top-level modules, matching Phase
  3's module-layout precedent (no new package).

## Files

- `src/depcompass/adapters/__init__.py` — `get_adapter(config:
  VendorConfig, project_root: Path) -> EcosystemAdapter`.
- `src/depcompass/sync.py` — `sync_vendor`, `sync_all`. Deterministic and
  idempotent: every output file is fully overwritten each run, no diffing
  against previous output.
- `src/depcompass/claude_md.py` — `render_vendor_claude_md`. Sections, in
  order: Metadata (version/ecosystem/depth + the load-bearing
  `Installed version:` line `staleness.py` will regex against in Phase 6
  — exact format fixed here), Grounding preamble (fixed instructional
  text: pinned version is authoritative over training knowledge), Public
  API surface (`digest.api_surface`), Known gotchas (from
  `DepNode.side_effects`, per Design decisions), Quick links (relative
  links to `./FILETREE.md`, `./DEPTREE.md`, and a backlink to the project
  root `CLAUDE.md`). Gap analysis section omitted per Design decisions.
- `src/depcompass/index.py` — `render_routing_table` (Markdown table,
  columns Vendor/Path/Version/Depth/Deps/Consult when, plus the routing-
  instruction sentence above it) and `update_root_claude_md` (append
  markers + table on first run; `re.sub` with `re.DOTALL` to replace just
  the marked block on regeneration).
- `src/depcompass/discovery.py` — `discover_npm` (package.json
  `dependencies`+`devDependencies`), `discover_python` (pyproject.toml
  `[project.dependencies]`, stripping version specifiers/extras to bare
  names), `discover_cargo` (Cargo.toml `[dependencies]`+
  `[dev-dependencies]`), `write_vendor_toml` (errors if the target path
  already exists), and manifest→ecosystem dispatch by filename.
- `src/depcompass/cli.py` — `init(scan: list[Path])` (required `--scan`
  file list, no default auto-detection), `sync(vendor: str | None =
  typer.Argument(None))`, `index()`. `_write_claude_md` stub removed.
- `tests/test_sync.py`, `tests/test_claude_md.py`, `tests/test_index.py`,
  `tests/test_discovery.py`, `tests/test_cli.py` (new).
- `architecture/overview.md`, `docs/cli-reference.md`,
  `docs/config-schema.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md`,
  `CHANGELOG.md` — updated in place.

## Verification

- `pytest` — full suite passes, count increases from Phase 3's total.
- `ruff check .` — clean, including all new modules.
- End-to-end `sync` against a real installed package produces a
  `vendor/<name>/` directory with all five files, and the `CLAUDE.md`'s
  metadata line matches the installed version exactly.
- `index` run twice in a row against the same project: second run's root
  `CLAUDE.md` has one routing table (not two), and hand-written content
  outside the markers is untouched.
- `init --scan` against a small real `package.json`/`pyproject.toml`/
  `Cargo.toml` produces a `vendor.toml` that `load_vendor_config` (Phase
  1) parses without error.
- `init --scan` against a directory that already has a `vendor.toml`
  errors clearly and does not modify the existing file.
- A `depth = full` vendor's `vendor/<name>/src/` snapshot includes a
  `tests/`-named directory (if the real package has one) and excludes
  `node_modules`/`dist`.
- `architecture/overview.md`'s Known footguns section lists every new
  Phase 4 limitation described above.

## Status

planned — this plan file has been written and reviewed; no command
implementation code has been written yet. Blocked on Phase 3 actually
being implemented (see Blocking dependency above).
