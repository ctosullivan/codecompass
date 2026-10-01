# codecompass — implementation reconstruction (from the bounded export only)

Model-blind reconstruction, Phase 80 Stage 2. Export:
`/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/phase80-reconstruction-export`.
All evidence below comes only from the files in that export and from
actually running its code (pip install, pytest, import attempts) in an
isolated scratch venv. No narrative docs, ADRs, or planning files were
read.

## 0. Headline finding: the export is not a runnable whole

`src/codecompass/cli.py` and `src/codecompass/sync.py` (and transitively
`adapters/base.py` and `adapters/python.py`, via `codecompass.symbols`/
`codecompass.filetree`) import a long list of sibling modules that are
**not present** in this export: `enrichment`, `relation_enrichment`,
`chat`, `index`, `skill`, `source_resolution`, `staleness`, `filetree`,
`symbols`, `git_topology`, `skill_scan`, `source_symbols`, `spec_docs`,
`usage`, `claude_md`, `deptree`, `doc_mapping`, and
`adapters/{cargo,haskell,npm}.py`. Confirmed by actually installing the
export (`pip install -e ".[dev]"`) into a scratch venv and running it:

- `codecompass --help` and `python -c "import codecompass.cli"` both
  fail: `ImportError: cannot import name 'enrichment' from 'codecompass'`.
- `pytest --collect-only`: 5 of 10 test files fail to even import —
  `test_cli.py`, `test_sync.py`, `test_adapters_base.py`,
  `test_adapters_dispatch.py`, `test_adapter_python.py` — each tracing
  back to one of the missing modules above (e.g. `test_adapter_python.py`
  fails via `adapters/__init__.py` → `adapters/base.py` →
  `from codecompass.filetree import iter_source_files`).
- The remaining 5 test files (`test_commands.py`, `test_config.py`,
  `test_core.py`, `test_discovery.py`, `test_graph.py`) collected and
  ran: **116 passed, 1 failed**. The one failure
  (`test_load_valid_vendor_config`) is `FileNotFoundError` for
  `tests/fixtures/vendor.toml` — the export's `tests/` directory has no
  `fixtures/` subdirectory at all, so this is an export-completeness gap,
  not a real code defect.

So `graph.py`, `config.py`, `discovery.py`, `commands.py`, and `core.py`
were confirmed end-to-end by running their real tests. `cli.py`,
`sync.py`, and the adapter layer could only be reconstructed by reading,
since none of them actually execute in this environment — this report
does not guess at the content of the missing modules; it only reports
what the present code imports from them and what their docstrings/call
sites imply about their contracts.

## 1. Modules (what's actually in the export, and their real job)

- **`core.py`** — ecosystem-agnostic data model only: `Ecosystem`
  (`StrEnum`: npm/python/cargo/haskell), `VendorConfig` (frozen
  `name`+`ecosystem`, nothing else — confirmed by
  `test_core.py::test_vendor_config_narrowed_to_name_and_ecosystem` and
  its frozen-ness test), `RepositoryLocation` (`url`, optional
  `subdirectory`), `DepNode` (mutable dependency-tree node with
  independent default `children`/`side_effects` lists — verified by
  test), `VendorDigest` (the aggregate per-vendor sync output struct,
  fields populated by different later phases per its own docstring).
- **`config.py`** — parses `vendor.toml` via stdlib `tomllib` into
  `list[VendorConfig]`. Fail-fast `ConfigError` on first bad entry
  (missing `name`, invalid `ecosystem`). A legacy `depth` key is
  silently ignored (no migration, no warning) — confirmed by the code
  path, not just a comment.
- **`discovery.py`** — manifest-based dependency discovery feeding
  `vendor.toml` generation. Five discoverers, one per manifest type:
  `discover_npm` (package.json deps+devDeps), `discover_python`
  (pyproject.toml `[project.dependencies]`, PEP 508 names stripped of
  version/extras/markers — explicitly does **not** scan
  `[project.optional-dependencies]`), `discover_requirements_txt`
  (line-based, skips comments/`-`-prefixed pip options),
  `discover_cargo` (Cargo.toml deps+dev-deps), `discover_haskell`
  (package.yaml/hpack via real PyYAML `safe_load`, explicitly does not
  expand `when:`-block conditional deps). `discover_manifest_paths` does
  a non-recursive root-level scan for known manifest filenames.
  `write_vendor_toml` refuses to overwrite an existing file;
  `append_vendor_toml` is the idempotent-refresh path. Output format is
  hand-rolled TOML text (`render_vendor_block`), not a round-trip-
  preserving writer.
- **`commands.py`** — despite the generic name, this file does exactly
  one thing: generates `.claude/commands/discovery.md`, a Claude Code
  custom slash command (`/discovery`). Purely templated/deterministic
  string-building (`render_discovery_command`) plus a writer
  (`write_discovery_command`) that creates `.claude/commands/` and
  overwrites the file. Fully covered and passing in `test_commands.py`
  (10 tests): frontmatter shape, `allowed-tools` excludes Write/Edit,
  mentions canned `query`/`check` commands and the sqlite3 escape hatch,
  repeats the read-only constraint, idempotent overwrite.
- **`graph.py`** (2428 lines) — the SQLite persistence layer for
  `context-graph.db`. This is the largest and most load-bearing module
  in the export. See §3 below.
- **`sync.py`** (502 lines) — per-vendor and whole-project orchestration:
  `sync_vendor`, `sync_all`, `rebuild_project_graph`. Cannot run in this
  export (missing deps), but fully readable; see §2/§6 (runtime paths)
  below — traced from source and from its own test file's intent
  (though that test file doesn't execute here), explicit about which
  claims are "read, not run."
- **`adapters/base.py`** — `AdapterError` exception, abstract
  `EcosystemAdapter` base class, and the shared `_run_json` subprocess
  seam. See §4.
- **`adapters/python.py`** — the one concrete adapter present. See §4.
- **`adapters/__init__.py`** — a one-function dispatch table
  (`get_adapter`) keyed by `Ecosystem`, referencing
  `CargoAdapter`/`HaskellAdapter`/`NpmAdapter`/`PythonAdapter` — only the
  last of which is in this export.
- **`cli.py`** (1520 lines) — Typer app; see §2 for the full confirmed
  command surface (confirmed by reading signatures/docstrings directly,
  not by running `--help`, since that fails here).
- `__init__.py` is empty.

## 2. CLI/API surface (from `cli.py`'s real Typer decorators/signatures — not runnable here, see §0)

Top-level `app = typer.Typer(...)`, plus two sub-apps: `query_app`
(mounted as `query`) and `enrich_app` (mounted as `enrich`).

- **Bare `codecompass`** (`@app.callback(invoke_without_command=True)`)
  — options `--yes` (bool), `--budget` (float|None). Runs `_bootstrap`:
  discover manifests → write/append `vendor.toml` → `sync_all` on
  newly-discovered vendors only → `rebuild_project_graph` →
  `_maybe_run_enrichment` (an AI-cost-gated, confirmable step reading
  `codecompass.enrichment`/`codecompass.relation_enrichment`, both
  absent from this export) → `_refresh_generated_artifacts` (always
  runs, even on enrichment abort).
- **`init`** — `--scan PATH` (repeatable, required),
  `--output/vendor_toml PATH` (default `vendor.toml`). Explicit
  scripted/CI equivalent of auto-discovery; errors if `vendor.toml`
  already exists.
- **`sync [VENDOR]`** — optional positional vendor name, `--yes`,
  `--budget`. No name = whole-project sync (rebuilds graph, may trigger
  enrichment); named = single-vendor only, never touches the graph or
  triggers enrichment (an explicit design choice documented in the
  code, referenced but not independently verifiable from this export).
- **`index`** — no args. Regenerates the CLAUDE.md routing table + tool
  Skill + discovery command from current `vendor.toml` state (calls into
  `codecompass.index`/`codecompass.skill`, both absent here).
- **`check`** — `--strict`, `--fix` (mutually exclusive). Staleness
  table + report-only coverage-gap sections (unused vendors,
  documented-but-unused/used-but-undocumented symbols, orphaned skill
  mentions, spec/vendor docs without relations) if `context-graph.db`
  exists. With no flags always exits 0.
- **`query vendors`** — `--unused`, `--json`. Lists `vendors` table rows
  joined against `graph.unused_vendors`/`graph.has_enrichment`.
- **`query vendor NAME`** — `--json`. Calls `graph.vendor_profile`.
- **`query symbol NAME`** — `--json`. Calls `graph.symbol_profile`
  (symbol names not globally unique across vendors).
- **`query skills`** — `--unused-mentions`, `--json`. Calls
  `graph.skills_index`.
- **`query relations NAME`** — `--json`. Resolves `NAME` as a spec-doc
  path, then a vendor name, then any other doc-artifact `name`, in that
  order (`_resolve_relations`); also shows a "Package code" trace via
  `graph.doc_code_trace`.
- **`query topology`** — `--json`. Reads `graph.topology_profile`; three
  distinct "not indexed" states are rendered honestly rather than
  collapsed (db absent / db present but never topology-synced /
  genuinely indexed).
- **`query source PATH`** — `--json`. Reads `graph.source_file_profile`;
  gated on `meta.source_index_version` being present (never triggers a
  rebuild itself).
- **`query source-symbol NAME`** — `--json`. Reads
  `graph.source_symbol_profile`.
- **`chat VENDOR`** — calls `codecompass.chat.run_chat` (absent from
  export) grounded only in already-generated
  `vendor/<name>/CLAUDE.md`/`OVERVIEW.md`; never regenerates anything.
- **`undo`** — `--yes`, `--dry-run`. Best-effort removal of everything
  codecompass generated: tracked `vendor/<name>/` dirs, `vendor.toml`,
  `context-graph.db`, every `doc_artifacts` row tagged
  `codecompass_tool`/`codecompass_vendor` (never `third_party`), plus a
  fallback pattern-based enumeration (`.claude/skills/codecompass-*`,
  `.cursor/rules/codecompass-*.mdc`, `.claude/commands/discovery.md`)
  when no graph exists yet. Strips (does not delete) a marker-delimited
  routing-table block from the root `CLAUDE.md`, leaving hand-written
  content around it untouched. Never invokes git.
- **`enrich apply ENTRIES_FILE --agent NAME`** — reads a JSON list of
  `{source_doc_path, target_vendor_name?, target_doc_path?, ai_summary,
  relation_label}` objects and writes them as agent-authored (non-API)
  enrichment, but only for entries that exactly match a currently-pending
  candidate from `relation_enrichment.select_candidates` (absent from
  export) — a real mechanical trust boundary, not just an instruction: a
  nonexistent or already-enriched-and-unchanged edge is rejected and
  reported, and the command exits non-zero if anything was rejected.
- A former `promote` command is confirmed gone:
  `test_cli.py::test_promote_command_removed` asserts Typer's standard
  "no such command" error.

`query`/`enrich` subcommands that need the graph use a consistent
"open-or-note" pattern (`_open_graph_or_note`/`_graph_session`): a
missing `context-graph.db` prints a one-line yellow note and returns
cleanly rather than crashing or silently creating an empty DB.

**CORRECTION (2026-10-02, found by an independent `context-evaluator`
assessment of a coding-context packet built from this report — see
`_part4-coding-context-packet-evaluation.md`): this is an
overgeneralization, not accurate for every `query` subcommand.**
`query topology`/`query source`/`query source-symbol` actually use a
*different* helper, `_open_graph_if_exists` (`cli.py:895-912`), not
`_open_graph_or_note`/`_graph_session` — confirmed by direct, independent
re-reading of `cli.py`. `_open_graph_if_exists` prints nothing itself
(each caller renders its own specific "not yet indexed" outcome) and is
additionally gated on `meta.source_index_version`/topology-sync state,
which `_open_graph_or_note` has no equivalent of. This distinction is
exactly the kind of thing a model-blind, read-only reconstruction (this
export could not execute `cli.py` — see §0) is vulnerable to missing:
both helpers *look* similar at a skim (same `None`-on-missing-db
contract) and the difference only matters at the call-site level this
summary paragraph over-collapsed. The rest of this report's claims about
these three commands remain accurate; only this one shared-helper
generalization is wrong. Not fixed in place — left as the historical
record of what this reconstruction actually said, per this project's own
correction-notice convention.

## 3. Data & persistence — `graph.py`'s schema (confirmed live via `test_graph.py`, 75 tests, 100% passing in isolation)

SQLite file `context-graph.db`, schema version string `"11"`
(`meta.schema_version`, now purely informational — see below).
`_SCHEMA_SQL` creates (idempotent `CREATE TABLE IF NOT EXISTS`):

- `meta` (key/value)
- `vendors` (name UNIQUE, ecosystem CHECK IN npm/python/cargo/haskell,
  installed_version, repository_url/subdirectory, source_resolved,
  source_resolution_error, last_synced_at)
- `source_files` (path UNIQUE; language/content_hash/
  symbol_index_status/symbol_index_diagnostic all nullable;
  `symbol_index_status` CHECK IN indexed/indexed_partial/unsupported/
  parse_error/unreadable)
- `source_symbols` (occurrence-keyed: `UNIQUE(source_file_id, name,
  kind, line)`, `line NOT NULL`; `exposure` CHECK IN public/restricted/
  internal/conventional_private/unknown)
- `symbols` (`UNIQUE(vendor_id, name)`, `export_kind` default
  `'export'`, `note`)
- `uses_edges` (source_file_id, vendor_id, nullable symbol_id, nullable
  line)
- `doc_chunks`, `doc_artifacts` (`path` UNIQUE; `kind` CHECK IN
  claude_md/overview/skill/cursor_mdc/slash_command/spec_doc/vendor_doc;
  `origin` CHECK IN codecompass_tool/codecompass_vendor/third_party/
  project/vendor_upstream/pinned_reference)
- `documents_edges`, `skill_mentions_edges`, `routes_via_edges` (UNIQUE
  vendor+doc), `depends_on_edges` (UNIQUE vendor pair)
- `doc_relations_edges` (`relation_kind` CHECK IN mentions_dependency/
  mentions_artifact; UNIQUE source+target_vendor+target_doc)
- `vendor_enrichment`, `symbol_enrichment`, `doc_relation_enrichment`
  (the three "survive every rebuild" tables — see below; `relation_label`
  CHECK against the closed `RELATION_LABELS` tuple:
  documents_configuration_of/explains_usage_of/contrasts_with/
  supersedes/other)
- `git_repositories`, `git_worktrees`, `git_submodules` (Git topology —
  fully clear-and-reinsert each rebuild, no cross-rebuild identity)

**Core rebuild function: `rebuild_deterministic(conn, **row_sequences)`.**
Confirmed by running `test_graph.py` directly:

- Wipes and reinserts every *edge/leaf* table unconditionally
  (`doc_relations_edges`, `depends_on_edges`, `routes_via_edges`,
  `skill_mentions_edges`, `documents_edges`, `uses_edges`, `doc_chunks`,
  `doc_artifacts`, plus all three git_* tables) inside one transaction.
- **Upserts** `vendors`, `symbols`, `source_files`, `source_symbols` by
  natural key (name; vendor+name; path; file+name+kind+line
  respectively) — confirmed:
  `test_rebuild_deterministic_preserves_vendor_id_across_rebuilds` and
  `test_source_files_upserted_by_natural_key_preserves_id_across_rebuilds`
  both pass, proving ids are stable across repeated rebuilds for
  unchanged rows. Stale rows (present before, absent from the new
  fixture) are explicitly deleted — confirmed by
  `test_rebuild_deterministic_removes_vendors_and_symbols_no_longer_present`
  and `test_source_files_removed_from_fixture_are_deleted`.
- `rebuild_deterministic` run twice with identical input produces
  identical row counts
  (`test_rebuild_deterministic_is_repeatable_without_duplicating_rows`)
  — genuinely idempotent.
- **Never touches** `vendor_enrichment`/`symbol_enrichment`/
  `doc_relation_enrichment` — confirmed directly:
  `test_rebuild_deterministic_never_touches_vendor_enrichment`/
  `..._symbol_enrichment` write an enrichment row, rebuild again, and
  assert the row is byte-identical before/after. This is the real
  mechanism by which paid AI-enrichment output survives a plain
  mechanical `sync`.
- Writes `meta.last_deterministic_rebuild_at` (always), and
  conditionally `meta.git_topology_status`/`git_topology_reason` and
  `meta.source_index_version` only when the caller actually supplies
  them — confirmed by `test_source_index_version_absent_until_explicitly_supplied`
  and `..._written_even_with_zero_source_files` (the latter proves
  "indexed, zero results" is distinguishable from "never indexed").

**Migrations** — six in-place migration functions run unconditionally
at every `open_graph()` (`_migrate_doc_artifacts_constraints`,
`_migrate_doc_relation_enrichment_relation_label`,
`_migrate_vendors_ecosystem_constraint`,
`_migrate_symbols_export_kind_note_columns`,
`_migrate_symbol_enrichment_model_column`,
`_migrate_source_files_columns`), each self-gated by **direct schema
introspection** (`PRAGMA table_info`, or inspecting `sqlite_master.sql`
text for a specific CHECK value), **not** by comparing
`meta.schema_version` — the code's own comments say this was
deliberately changed after `meta.schema_version` was found (via git log,
per the comment — not independently verifiable here) to have been
bumped twice for unrelated schema changes, which would have falsely
triggered migrations. All six migrations are exercised directly in
`test_graph.py` against hand-built pre-migration schemas (e.g.
`test_open_graph_migrates_pre_phase_60_vendors_constraint`,
`test_open_graph_migrates_pre_phase_74_symbol_enrichment_preserves_rows`)
and all of them were run — they pass. Two migration strategies are used
depending on data-loss risk: `ALTER TABLE ... ADD COLUMN` for anything
that would otherwise cascade-delete enrichment data through a foreign
key, versus drop-and-recreate only for `doc_artifacts`/
`documents_edges`/`doc_relations_edges`, which are fully rewritten on
every sync anyway so there's nothing to lose. `vendors`' CHECK-constraint
widening (for `'haskell'`) uses a copy-into-new-table-and-rename
approach since SQLite can't `ALTER` a CHECK constraint directly.

## 4. Adapter pattern (`adapters/base.py` + `adapters/python.py`)

`EcosystemAdapter` (ABC) requires four abstract methods:
`installed_version() -> str`, `source_location() -> Path`,
`readme_and_api_surface() -> str`, `repository_url() ->
RepositoryLocation | None`, `dependency_tree() -> DepNode`. (The
abstractness is genuinely enforced —
`test_ecosystem_adapter_rejects_incomplete_subclass` instantiates a
deliberately incomplete subclass and asserts `TypeError`; this test ran
and passed.) A fifth method, `symbols() -> list[Symbol]`, is **concrete,
not abstract**, with a default implementation that walks
`source_location()` via `iter_source_files` (from the missing
`filetree.py`) and dispatches each file through
`extract_symbols_for_file` (from the missing `symbols.py`) — so a new
adapter is not forced to implement structured symbol extraction.

The shared subprocess seam `_run_json(cmd, cwd)`: resolves `cmd[0]` via
`shutil.which` first (explicitly to handle Windows `.cmd` shims safely
without a shell), runs it with `capture_output=True, text=True,
check=False`, and raises `AdapterError` for a missing tool, non-zero
exit (message includes stripped stderr), or invalid JSON stdout. All
four of its own unit tests (`test_adapters_base.py`) ran directly and
passed, including the one real (non-monkeypatched) case:
`_run_json(["definitely-not-a-real-command-xyz"], ...)` genuinely raises
`AdapterError` with "not found".

`PythonAdapter` (the only concrete adapter present):
`installed_version`/`source_location` via `importlib.metadata`/
`importlib.util.find_spec`, raising `AdapterError` if the package isn't
installed in-process. `repository_url` reads already-local
`Project-URL` metadata entries (no network call), checking labels in
fixed priority order `("source", "repository", "code", "github",
"homepage")`, case-insensitively; returns `None` if nothing matches.
`dependency_tree` shells out to `python -m pipdeptree --output
json-tree --packages <name>` (via `sys.executable`, not a bare
`pipdeptree` on PATH) and converts the JSON tree to `DepNode`s;
`dev_only` is always left `False` (pipdeptree's tree output doesn't
carry that distinction) — confirmed directly via
`test_dev_only_always_false`, which asserts `False` on every node
including children. `readme_and_api_surface` prefers up to 5 `.pyi`
stub files (`_PYI_FILE_CAP`) concatenated verbatim if present;
otherwise statically `ast.parse`s `__init__.py` for `__all__` plus
per-symbol purposes via `extract_python_symbols` (from the missing
`symbols.py`) — deliberately chosen over actually importing the
package, to avoid executing module-level side effects. Tests depending
on `tests/fixtures/*` (missing from export) or that transitively import
`codecompass.symbols` could not run, but `installed_version`/
`source_location`/`repository_url`/`_run_json` behavior was confirmed
live against the real `pytest` package installed in the scratch venv.

**Dispatch**: `adapters/__init__.py::get_adapter(config, project_root)`
is the single construction point, keyed by a `dict[Ecosystem,
type[EcosystemAdapter]]` — `test_adapters_dispatch.py` (unrunnable here,
but readable) asserts this dispatches correctly and passes
`config`/`project_root` straight through.

## 5. Configuration

`config.py::load_vendor_config(path)` is the only configuration entry
point: parses `vendor.toml`'s `[[vendor]]` array-of-tables via stdlib
`tomllib` (confirming the `pyproject.toml` comment "no `tomli`
dependency ... `tomllib` is available" — `requires-python = ">=3.11"`).
Each entry requires `name` (str) and `ecosystem` (must be one of the
`Ecosystem` enum values); anything else is ignored. Fail-fast on the
first bad entry. No environment-variable or CLI-flag-driven config
beyond the vendor.toml path itself (`cli.py::_load_config` defaults to
`Path("vendor.toml")` relative to cwd).

## 6. Runtime paths (traced by reading, confirmed only where the code actually ran)

- **`codecompass sync` (whole-project)**: `cli.py::sync` →
  `_load_config()` → `sync_all(configs, cwd)` (loops `sync_vendor` per
  config) → (whole-project only) `rebuild_project_graph(configs, cwd)`
  → `_maybe_run_enrichment` → `_refresh_generated_artifacts`. This call
  chain was confirmed to exist exactly as described by reading `cli.py`
  directly; it could not be executed end-to-end since
  `enrichment`/`relation_enrichment`/`index`/`skill`/
  `commands.write_discovery_command` dependencies are only partially
  present (only `commands.write_discovery_command` is actually in this
  export).
- **`sync_vendor`** (readable, not runnable here): construct adapter via
  `get_adapter` → read `installed_version`/`readme_and_api_surface`/
  `dependency_tree`/`source_location` → create `vendor/<name>/` → clone
  upstream source via `resolve_and_clone` (missing module), falling back
  to a local-install copy (`_copy_source_snapshot`) on failure,
  recording `description_error` — this is a clone failure, explicitly
  *not* a description failure, since there's no AI call inside
  `sync_vendor` at all anymore (its docstring states this directly and
  the code has no AI-call code path) — then read-only-looks-up this
  vendor's existing `vendor_enrichment` row from the graph (if
  `context-graph.db` exists) to populate the digest's description
  fields, renders `DEPTREE.md`/`deptree.json`/`FILETREE.md`/
  `filetree.json`/`CLAUDE.md` (+`OVERVIEW.md` if an enrichment exists)
  unconditionally, fully overwriting every file every call —
  deterministic, no diffing.
- **`rebuild_project_graph`** (readable, not runnable here): for every
  config, builds a `VendorRow` + that vendor's `SymbolRow`s via
  `adapter.symbols()`; runs `usage.resolve_project_usage` (missing) to
  produce `UsesEdgeRow`s, resolving detected symbol names only against
  each vendor's own already-collected symbol-name set (else falls back
  to a vendor-level edge with `symbol_name=None`); runs
  `source_symbols.discover_source_files`+
  `extract_source_symbols_for_file` (missing) over every recognized
  first-party file regardless of `vendor.toml`; collects doc-artifact
  rows from four independent sources
  (`doc_mapping.collect_vendor_doc_artifacts`,
  `collect_vendor_upstream_doc_artifacts`, `skill_scan.scan_skills`,
  `spec_docs.scan_spec_docs` — all missing); derives chunk/edge rows
  from those; runs `git_topology.detect_git_topology` (missing); and
  finally calls `graph.rebuild_deterministic` once with everything. A
  documented, accepted inefficiency: the source-file walk for symbols
  and the vendor-usage walk each independently traverse the project
  tree once rather than being merged.
- **`query`/`enrich`/`undo`/`check` commands**: fully self-contained
  inside `cli.py` + `graph.py`; these were traced completely and, for
  the `graph.py` half, confirmed by running the matching tests.

## 7. Extension points (confirmed from what's actually visible)

- **New ecosystem adapter**: subclass `EcosystemAdapter`
  (`adapters/base.py`), implement the five abstract methods (optionally
  override `symbols()` if the default walk+extract approach doesn't
  apply — the code comments cite a hypothetical "external-process"
  adapter, e.g. for a language with no in-process extractor, as the
  reason this one method is concrete not abstract), then register it in
  `adapters/__init__.py`'s `_ADAPTER_BY_ECOSYSTEM` dict and add the new
  value to `core.py`'s `Ecosystem` enum and `graph.py`'s
  `vendors.ecosystem` CHECK constraint (with an accompanying migration,
  following the existing `_migrate_vendors_ecosystem_constraint` pattern
  that widened it for `'haskell'`). `PythonAdapter` is the concrete,
  working reference implementation for this interface.
- **New CLI command**: add an `@app.command()`
  (or `@query_app.command()`/`@enrich_app.command()`) function in
  `cli.py`, following the existing pattern of a plain function with
  Typer-annotated parameters, printing via the shared `rich.Console`
  instance, and raising `typer.Exit(code=1)` on failure rather than
  letting exceptions propagate. Commands needing ordinary graph access
  should use the existing `_graph_session`/`_open_graph_or_note`
  context-manager pattern rather than opening `sqlite3.connect`
  directly, to get the established "graceful note, no traceback, no
  silent empty-DB creation" behavior for free. **Correction added
  2026-10-02** (see this file's own correction note in §2 above): a
  command that also needs to distinguish "database exists but this
  specific thing was never indexed" (as `query topology`/`query source`/
  `query source-symbol` all do) should follow `_open_graph_if_exists`
  (`cli.py:895-912`) instead — a related but distinct helper this
  report originally failed to name as a separate pattern.
- **New graph row/table**: add a dataclass row type in `graph.py` next
  to the existing ones, a `CREATE TABLE IF NOT EXISTS` clause in
  `_SCHEMA_SQL`, an insertion/sync helper function (`_insert_*` for
  clear-and-reinsert tables, `_sync_*` for upserted-by-natural-key
  tables), wire it into `rebuild_deterministic`'s signature and body,
  and — if the new table must survive a rebuild (like
  `vendor_enrichment`) — key it by a plain natural-key TEXT column, not
  a foreign key to a table that gets wiped, per
  `doc_relation_enrichment`'s own documented precedent.
- **New manifest ecosystem discovery**: add a
  `discover_<ecosystem>(manifest: Path) -> list[str]` function in
  `discovery.py` and register it (plus the manifest filename) in
  `_MANIFEST_HANDLERS`.

## 8. Limitations — genuine gaps confirmed from the evidence itself

- **This export cannot run `cli.py`, `sync.py`, or the adapter package
  as a whole** — confirmed by direct `ImportError`s against real,
  present code, not inference. `AdapterError` dispatch, `get_adapter`,
  and all of `PythonAdapter`'s fixture-backed tests are untestable here
  for the same transitive reason (`adapters/base.py` itself imports the
  two missing modules `filetree`/`symbols`, so even importing
  `adapters.python` alone fails).
- **`tests/fixtures/` is entirely absent from the export** — this breaks
  `test_config.py::test_load_valid_vendor_config` (confirmed:
  `FileNotFoundError`) and would also break several
  `test_adapter_python.py` tests (`pipdeptree_json_tree.json`,
  `sample.pyi`, `sample_module_with_all.py`) had that file been
  importable at all.
- **`discover_python` does not scan
  `[project.optional-dependencies]`** — stated directly in its own
  docstring as a known, documented limitation, not inferred.
- **`discover_haskell` does not expand hpack's `when:`-block conditional
  dependencies** — likewise stated directly in the docstring as an
  accepted, out-of-scope gap.
- **`config.py` silently tolerates and discards a legacy `depth` key**
  with no warning or migration — by construction (the parser simply
  never reads that key), not a bug per se, but a real silent-acceptance
  behavior worth flagging: a user with a stale `vendor.toml` field gets
  no signal that it's being ignored.
- **`PythonAdapter.dependency_tree()`'s `dev_only` is always `False`**,
  confirmed live by `test_dev_only_always_false` — pipdeptree's JSON
  tree output doesn't distinguish dev dependencies, so this adapter
  cannot populate that `DepNode` field meaningfully; it's a real,
  structural ecosystem-tooling limitation, not an oversight the code
  tries to hide (the docstring says `dev_only` is "left False for
  pipdeptree" as an intentional "safe default over forced complexity").
- **No test in this export exercises a `NotImplementedError`/explicit
  `TODO`** — none found in any of the included files;
  `EcosystemAdapter`'s abstract methods raise Python's standard
  `TypeError` at instantiation time (via `ABC`), not at call time, which
  is the one place "incompleteness" is enforced at all, and it's
  enforced correctly (confirmed by test).
- **Schema-migration safety depends entirely on direct introspection,
  and the code's own comments claim `meta.schema_version` was
  previously bumped for unrelated changes and silently caused incorrect
  migration triggers twice** — this could not be independently verified
  (it cites `git log`, not available in this export), but the current
  code's defense against it (checking real `CREATE TABLE`/`PRAGMA
  table_info` state rather than a version number) is directly confirmed
  by the passing migration tests.
- **Could not determine** the actual behavior of `enrichment.py`,
  `relation_enrichment.py`, `chat.py`, `index.py`, `skill.py`,
  `source_resolution.py`, `staleness.py`, `filetree.py`, `symbols.py`,
  `git_topology.py`, `skill_scan.py`, `source_symbols.py`,
  `spec_docs.py`, `usage.py`, `claude_md.py`, `deptree.py`, or
  `doc_mapping.py`, or the `npm`/`cargo`/`haskell` adapters — these were
  deliberately excluded from the export; only the calling code's
  imports, call signatures, and docstring-stated expectations of them
  are available (e.g. "`resolve_and_clone` falls back on
  `SourceResolutionError`", "`extract_symbols_for_file(path, ecosystem)`
  returns `Symbol` objects with `.name`/`.purpose`/`.export_kind`/
  `.note`", "`usage.resolve_project_usage(project_root, configs)` yields
  `(rel_path, DetectedImport)` pairs with `.vendor`/`.symbol_name`/
  `.line`"). These are reported as inferred call contracts only, not as
  confirmed implementations.

## Files consulted

All under
`/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/phase80-reconstruction-export/`:
`pyproject.toml`;
`src/codecompass/{__init__.py,cli.py,commands.py,config.py,core.py,discovery.py,graph.py,sync.py}`;
`src/codecompass/adapters/{__init__.py,base.py,python.py}`;
`tests/{test_adapter_python.py,test_adapters_base.py,test_adapters_dispatch.py,test_cli.py,test_commands.py,test_config.py,test_core.py,test_discovery.py,test_graph.py,test_sync.py}`.
