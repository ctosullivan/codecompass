# Phase 11: Project-source usage detection

## Scope

**Covered:**
- Small refactor first, no behavior change: `filetree.py`'s private
  `_iter_files(root)` becomes public `iter_source_files(root, *,
  prune_dirs=_PRUNE_DIR_NAMES, prune_globs=_PRUNE_FILE_GLOBS)` — same
  walk, now parameterizable. `render_filetree_markdown`,
  `render_filetree_json`, and `build_symbol_index` (its three existing
  callers) pass no overrides, so their output is byte-identical. This
  lets `usage.py` reuse the exact same deterministic, sorted, pruned-walk
  *shape* for the project's own source tree, with its *own* prune set
  (see Design decisions — project scanning must not exclude
  `tests`/`fixtures`, unlike a vendor's own source walk).
- `src/codecompass/usage.py` (new) — project-source-side import
  detection. Genuinely new capability: `symbols.py`'s extractors run in
  the opposite direction (pulling symbols *out of* a vendor's own
  source); nothing today inspects the *consuming* project's source at
  all.
  - `detect_python_imports(path: Path) -> list[DetectedImport]` —
    `ast.parse`, walk `ast.Import` (vendor-level only, no bound-name
    granularity — `import rich` binds no specific symbol) and
    `ast.ImportFrom` (`from rich.console import Console` — vendor
    candidate is the first dotted component of `module`, one
    `DetectedImport` per name in `names`, each carrying that bound name
    as a symbol candidate).
  - `detect_npm_imports(path: Path) -> list[DetectedImport]` — regex over
    `import { A, B } from "pkg"` (named — one entry per name),
    `import Default from "pkg"` / `import * as ns from "pkg"` /
    `require("pkg")` (vendor-level only, no symbol candidate — matching
    the coarse-regex posture already accepted for `extract_npm_symbols`).
  - `detect_rust_imports(path: Path) -> list[DetectedImport]` — regex
    over `use crate::Symbol;` (symbol candidate = `Symbol`) vs.
    `use crate::*;` / `use crate;` (vendor-level only).
  - `detect_imports_for_file(path: Path, ecosystem: Ecosystem) ->
    list[DetectedImport]` — dispatches by ecosystem, mirroring
    `symbols.extract_symbols_for_file`'s dispatch shape. Never raises — a
    file that fails to parse returns `[]`, same convention
    `symbols.py`'s extractors already follow.
  - `DetectedImport(vendor: str, symbol_name: str | None, line: int)` —
    `symbol_name=None` is the vendor-level fallback edge (a detected
    import that doesn't resolve to one specific bound name).
  - `resolve_project_usage(project_root: Path, configs: list[VendorConfig])
    -> list[tuple[str, DetectedImport]]` — walks the project root via
    `filetree.iter_source_files(project_root, prune_dirs=
    _PROJECT_PRUNE_DIR_NAMES)`, runs the matching ecosystem's detector
    per file, and **filters to only names matching a tracked vendor**
    (`configs`) — an import of an untracked package is not this
    project's concern. Returns `(relative_file_path, DetectedImport)`
    pairs; symbol-name-to-`symbol_id` resolution happens in `sync.py`
    (this module has no `graph.py` dependency — it only detects and
    filters against `configs`, keeping it independently unit-testable).
- `src/codecompass/sync.py` — new `rebuild_project_graph(configs:
  list[VendorConfig], project_root: Path) -> None`:
  1. For every config in `configs` (**all** tracked vendors, not just
     ones `sync_vendor` touched this run — the graph must reflect the
     full current state regardless of which vendors were just
     resynced): get its adapter, read `installed_version()`,
     `repository_url()` (already-existing, no-network-call method), and
     collect that vendor's own symbol list via
     `filetree.iter_source_files(adapter.source_location(), ...)` +
     `symbols.extract_symbols_for_file` per file (the same walk+extract
     pairing `build_symbol_index` already does internally — reused, not
     duplicated logic, just captured as structured `Symbol` objects
     instead of a rendered string).
  2. Call `usage.resolve_project_usage(project_root, configs)`, resolve
     each `DetectedImport.symbol_name` against that vendor's collected
     symbol list by name (matching `symbol_id`; `None` or no match stays
     a vendor-level fallback edge per `decisions/0031`'s uses-edges
     design).
  3. `graph.open_graph(project_root)` → `graph.rebuild_deterministic(conn,
     vendors=..., source_files=..., symbols=..., uses_edges=...,
     doc_artifacts=[], documents_edges=[], skill_mentions_edges=[],
     routes_via_edges=[], depends_on_edges=[])` — the doc/skill-mapping
     tables stay empty until Phase 12 extends this same call site with
     real data. Commit, close.
- `src/codecompass/cli.py` — two call sites, both **whole-project only**
  (`decisions/0025`'s posture, carried into `decisions/0032`):
  - `_bootstrap`: after `write_tool_skill(...)`, call
    `rebuild_project_graph(all_configs, project_root)` — using the full
    tracked list, not `new_configs`, since the graph must represent
    every tracked vendor regardless of what this particular bootstrap run
    newly discovered.
  - `sync` command: call `rebuild_project_graph(configs, Path.cwd())`
    **only when `vendor is None`** (the whole-project branch) — `sync
    <vendor>` (single-vendor) and `check --fix`'s per-vendor loop
    (already calling `sync_vendor` directly, never `sync_all`) leave the
    graph untouched, exactly as today's ADR 0025 already specifies.
- Tests: `tests/test_usage.py` (new) — fixture project-source trees per
  ecosystem (small temp dirs with varied import styles: named, default,
  wildcard, module-level), asserting exact `DetectedImport` output,
  including the "untracked package is filtered out" case.
  `tests/test_sync.py` gains coverage for `rebuild_project_graph` against
  a small fixture project + fixture vendor configs (using
  `graph.py`'s query functions from Phase 10 to assert on the resulting
  DB state, not just "it didn't crash"). `tests/test_filetree.py` gets a
  regression case confirming `iter_source_files`'s default-argument
  behavior is unchanged.

**Explicitly deferred / out of scope:**
- `doc_artifacts`/`documents_edges`/`skill_mentions_edges`/
  `routes_via_edges`/`depends_on_edges` population — Phase 12.
- Any CLI-visible output from the graph (`query`, `check`'s coverage-gap
  sections) — Phase 15.
- Alias/re-export resolution (a name re-exported through an intermediate
  module, or imported under an alias that obscures the originating
  vendor) — same accepted, explicitly-stated limitation the original
  (superseded) phase-9a/9b plans already carried; not solved here either.
- Universal source cloning (Phase 13) — this phase still reads each
  vendor's symbol list from `adapter.source_location()` (the local
  install), same as today's `FILETREE.md` generation; not yet from a
  clone.

## Design decisions

**Project-source scanning uses a different prune set than vendor-source
scanning.** `filetree._PRUNE_DIR_NAMES` excludes `test`/`tests`/
`__tests__`/`fixtures` — correct for a *vendor's* own source (its test
suite isn't API surface worth documenting) but wrong for the *consuming
project's* source: a project's own test files importing a vendor is
legitimate usage signal, and excluding it would systematically undercount
real usage. `usage.py` defines its own `_PROJECT_PRUNE_DIR_NAMES =
{"node_modules", "dist", "build", ".git", "__pycache__", ".venv", "venv"}`
— build/dependency noise only, no test exclusion — passed as
`iter_source_files`'s `prune_dirs` override.

**The graph rebuild is decoupled from `sync_all`'s per-vendor loop.**
An earlier design considered threading a `rebuild_graph: bool` flag
through `sync_all` itself, but `sync_all` is sometimes called with a
*subset* of configs (bare bootstrap's `new_configs` only) even on a
"whole-project" bootstrap run — the graph needs *all* tracked vendors'
data regardless. Making `rebuild_project_graph` a separate function,
called explicitly at the two whole-project call sites with the *full*
config list, avoids that mismatch entirely.

## Files

- `src/codecompass/filetree.py` — `_iter_files` → public
  `iter_source_files` with optional `prune_dirs`/`prune_globs`; its three
  existing internal callers updated to the new name, no behavior change.
- `src/codecompass/usage.py` (new).
- `src/codecompass/sync.py` — new `rebuild_project_graph`.
- `src/codecompass/cli.py` — two call sites in `_bootstrap` and `sync`.
- `tests/test_usage.py` (new), `tests/test_sync.py`, `tests/test_filetree.py`.
- `architecture/overview.md` — extend the "Context graph" section (added
  in Phase 10) with usage-detection's role; `planning/ROADMAP.md`,
  `planning/CONTEXT.md`, `CHANGELOG.md`.

## Verification

- `pytest` — full suite passes; no live API/network call anywhere in
  this phase's own code (usage detection is pure file parsing; the graph
  writes are local SQLite).
- `ruff check .` — clean.
- Manual, against this repo itself (a real Python project with real
  imports of `anthropic`, `typer`, `rich`, `pipdeptree`): run bare
  `codecompass`, then inspect `context-graph.db` directly (`sqlite3
  context-graph.db "select v.name, count(*) from uses_edges u join
  vendors v on v.id = u.vendor_id group by v.name"`) — confirm every
  vendor actually imported somewhere in `src/codecompass/` shows ≥1 use,
  and that symbol-level resolution worked for at least one `from X import
  Y` style import (e.g. `from rich.console import Console` in `chat.py`).
- Confirm `sync <vendor>` (single-vendor) leaves `context-graph.db`'s
  mtime unchanged — the concrete proof `decisions/0025`'s posture holds
  under the new storage backend, not just by code inspection.
