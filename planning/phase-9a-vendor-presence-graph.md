# Phase 9a: Context graph — vendor presence detection

## Scope

**Covered:**
- `src/depcompass/context_graph.py` (new) — the shared data model every
  later 9b/9c/9d sub-phase extends in place, not replaces:
  - `SourceFileNode(path: str)`, `VendorNode(name: str, ecosystem:
    Ecosystem, depth: Depth)` — dataclasses, JSON-serializable.
  - `UsesEdge(source_file: str, vendor: str)` — for 9a, vendor-level
    presence only: "this file references this vendor somewhere," no
    symbol granularity (that's 9b's upgrade, in place, to the same edge
    type).
  - `ContextGraph` — the aggregate: `nodes: dict[str, list]` (keys
    `source_files`, `vendors`, and — added by later sub-phases —
    `symbols`, `doc_artifacts`), `edges: dict[str, list]` (key `uses`
    for 9a; `documents`/`routes_via`/`depends_on` added by 9c),
    `enrichment: dict | None = None` (always `None` until 9d,
    `decisions/0026`). `to_json() -> str` / `write(path: Path) -> None` /
    `read(path: Path) -> ContextGraph`.
  - `build_context_graph(project_root: Path, configs: list[VendorConfig])
    -> ContextGraph` — pure, deterministic, no AI calls. For 9a: walks
    project source (reusing `filetree.py`'s existing `_PRUNE_DIR_NAMES`/
    `_iter_files`-style traversal conventions, scoped to the *project*
    root rather than a vendor's source snapshot), calls into
    `usage.py`'s detectors per file per ecosystem, and records a `UsesEdge`
    whenever a tracked vendor name is detected.
- `src/depcompass/usage.py` (new) — per-ecosystem, **project-source-side**
  detection. This is genuinely new code; `depcompass.symbols`'s existing
  extractors run in the opposite direction (pulling symbols *out of* a
  vendor's own source for `FILETREE.md`/`CLAUDE.md` rendering) and there
  is no existing import/usage detection over a *consuming* project's
  source anywhere in this codebase (confirmed: no JS/TS `import`/
  `require` regex, no Rust `use` regex exist today):
  - `detect_python_imports(path: Path) -> set[str]` — `ast.parse`, walk
    `ast.Import`/`ast.ImportFrom` nodes, collect top-level module names
    (matching `symbols.py`'s existing `ast`-based style).
  - `detect_npm_imports(path: Path) -> set[str]` — regex over
    `import ... from "<pkg>"` and `require("<pkg>")`, matching the
    existing `.d.ts`-regex posture already accepted for
    `extract_npm_symbols` (a full JS/TS parser is not introduced).
  - `detect_rust_imports(path: Path) -> set[str]` — regex over
    `use <crate>::`, matching the existing `pub`-regex posture already
    accepted for `extract_rust_symbols`.
  - A small dispatcher, `detect_imports_for_file(path, ecosystem) ->
    set[str]`, mirroring `symbols.extract_symbols_for_file`'s dispatch
    shape.
- `src/depcompass/sync.py` — `sync_all` (the bare, no-vendor-argument
  path, and by extension bare `depcompass`'s bootstrap, `decisions/0017`)
  calls `build_context_graph` once after every vendor has synced, then
  writes `context-graph.json` at the project root
  (`decisions/0024`, `decisions/0025`). `sync_vendor` (the single-vendor
  path used by `sync <name>`, `promote`, and `check --fix`'s per-vendor
  loop) is **not** changed and does **not** touch the graph.
- `src/depcompass/cli.py` — `check`'s report gains a new, report-only
  section: "Unused vendors" — any `VendorConfig` with zero `uses` edges
  in the persisted `context-graph.json`. Never affects `--strict`'s exit
  code (same treatment `check` already gives transitive-only drift). If
  `context-graph.json` doesn't exist (project never synced with graph
  support), the section is silently skipped with a one-line note
  pointing at `sync`.
- Tests: `tests/test_context_graph.py`, `tests/test_usage.py` (new) —
  pure unit tests against fixture project-source trees. Zero AI calls
  anywhere in 9a's construction path, so none of `decisions/0016`'s
  monkeypatch machinery is needed here (simpler than that concern, which
  only applies once a consumer *uses* AI-generated content — not the
  case for 9a).
- Same-commit docs: `architecture/overview.md` (new "Context graph"
  section, describing 9a's scope only — later sub-phases extend it in
  place), `docs/cli-reference.md` (`check`'s new report section),
  `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md`.

**Explicitly deferred:**
- Symbol-level usage edges — Phase 9b (`planning/
  phase-9b-symbol-usage-graph.md`).
- Doc/Skill/dependency mapping (`DocArtifact` nodes,
  `documents`/`routes_via`/`depends_on` edges) — Phase 9c (`planning/
  phase-9c-doc-skill-mapping.md`).
- Any LLM enrichment — Phase 9d (`planning/phase-9d-llm-enrichment.md`,
  `decisions/0026`).
- Per-vendor rendered view files derived from the graph — explicitly out
  of scope, `decisions/0024`.
- mtime/hash-based incremental caching — explicitly out of scope,
  `decisions/0025`.
- Re-export/aliasing resolution (a name re-exported through an
  intermediate module, or imported under an alias that obscures the
  originating vendor) — deferred, same posture as the existing `.mdc`
  `globs` gap noted in `architecture/overview.md`'s Known footguns: an
  accepted limitation, stated explicitly, not silently ignored.

## Design decisions

See `decisions/0024` (storage model) and `decisions/0025` (cache
invalidation trigger) for full reasoning. Summary:
- The context graph lives in one root-level `context-graph.json`, not
  fragmented per vendor — `uses` edges are inherently project-wide.
- Only bare `depcompass sync` and bare `depcompass` rebuild the graph.
  `sync <vendor>`, `promote <vendor>`, and `check --fix`'s per-vendor
  resyncs deliberately leave it untouched and therefore potentially
  stale relative to that one vendor until the next whole-project sync —
  an accepted, documented gap, not a bug.
- `check` reads the persisted file; it never rebuilds the graph itself.
- 9a's detection is presence-only (did this file reference this vendor
  at all) — deliberately coarser than 9b's symbol-level edges, kept as a
  separate, smaller increment so "unused vendor" detection ships and is
  verifiable before the more involved symbol-level work.

## Files

- `src/depcompass/context_graph.py` (new) — see Scope above.
- `src/depcompass/usage.py` (new) — see Scope above.
- `src/depcompass/sync.py` — wire `build_context_graph` into `sync_all`
  only; `sync_vendor` unchanged.
- `src/depcompass/cli.py` — `check`'s new "Unused vendors" report
  section; reads `context-graph.json` via `context_graph.read`.
- `tests/test_context_graph.py` (new), `tests/test_usage.py` (new).
- `architecture/overview.md`, `docs/cli-reference.md`,
  `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md` — updated
  in place, same commit (`CLAUDE.md` §2).

## Verification

- `pytest` — full suite passes, including the two new test files; no
  live API call anywhere (none are made in 9a's construction path at
  all).
- `ruff check .` — clean, including the two new modules.
- Manual, against a scratch project with `vendor.toml` declaring two
  Python vendors — one actually `import`ed somewhere in the project's
  source, one declared but never imported:
  - `depcompass sync` (bare) — confirm `context-graph.json` is created
    at the project root, contains a `uses` edge for the imported vendor
    and none for the unused one.
  - `depcompass check` (bare) — confirm the "Unused vendors" section
    lists exactly the unused vendor, and the command still exits 0.
  - `depcompass sync <the-used-vendor>` (single-vendor) — confirm
    `context-graph.json`'s mtime is unchanged afterward, demonstrating
    the accepted staleness gap from `decisions/0025` concretely, not
    just by code inspection.
  - Delete `context-graph.json` and run `depcompass check` — confirm the
    "Unused vendors" section is skipped with a one-line note, not an
    error.
