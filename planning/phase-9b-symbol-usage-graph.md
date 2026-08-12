# Phase 9b: Context graph — symbol-level usage

## Scope

**Covered:**
- `src/depcompass/usage.py` — extends (does not replace) 9a's three
  detectors in place: `detect_python_imports`, `detect_npm_imports`,
  `detect_rust_imports` upgrade their return type from a bare
  `set[str]` of vendor/module names to a structured usage record per
  file — which specific imported names were bound, and at which line —
  while keeping the same function names and the same per-ecosystem
  detection technique established in 9a (no new parsing strategy
  introduced here, only richer extraction from the same walk).
- `src/depcompass/context_graph.py` — adds `SymbolNode(id: str, vendor:
  str, name: str, purpose: str | None)`. Symbol identity is **reused
  data, not new extraction**: each `SymbolNode` is sourced from the
  corresponding `EcosystemAdapter.readme_and_api_surface()` call already
  made during `sync_vendor` — the same data already rendered into each
  vendor's `CLAUDE.md` "Public API surface" section. This is the
  brainstorm's `Symbol` node claim ("existing per-ecosystem extraction")
  holding up as accurate, in contrast to `USES` edges, which are
  genuinely new (see `planning/phase-9a-vendor-presence-graph.md`'s
  Scope section and the plan's discrepancy notes).
  **Open implementation question, not resolved by this plan**: confirm
  `readme_and_api_surface()`'s exact return shape during implementation.
  If it already exposes clean `(name, purpose)` pairs, reuse it directly;
  if not, add a minimal accessor on the adapter rather than duplicating
  `symbols.py`'s extraction logic a second time.
  Upgrades the `uses` edge (introduced vendor-level in 9a) to
  `SourceFile → Symbol`, keyed on the specific `SymbolNode.id`s a file's
  detected imports resolve to, rather than just the owning vendor. A file
  that imports a vendor but references no symbol `readme_and_api_surface()`
  captured (e.g. an internal/undocumented name) still gets a vendor-level
  `uses` edge (9a's original shape, retained as a fallback) rather than
  being dropped.
- Tests: `tests/test_usage.py`, `tests/test_context_graph.py` — extended
  in place with symbol-level cases, not new files.

**Explicitly deferred:**
- Re-export/aliasing resolution — a symbol imported under a local alias,
  or re-exported through an intermediate project module before reaching
  its actual use site, is not traced back to its origin. Same posture as
  the existing `.mdc` `globs` gap: an accepted, explicitly stated
  limitation for v1, not silently dropped. A file using such a symbol
  still gets whatever edge 9a/9b's direct-import detection can establish
  (typically the vendor-level fallback above), just not a precise
  symbol-level edge.
- Doc/Skill/dependency mapping — Phase 9c.
- Any LLM enrichment — Phase 9d.

## Design decisions

- Confirms and applies the plan's discrepancy finding directly: vendor-
  side symbol extraction (`symbols.py`) already exists and is reused via
  `readme_and_api_surface()`; project-side usage detection (`usage.py`)
  is the new code this phase (and 9a before it) actually introduces.
- This phase's cost — an `ast`/regex walk over the whole project source,
  now also resolving detected names against each vendor's known symbol
  list — remains zero-AI-call and bounded. It follows 9a's "always full
  rebuild, no incremental diffing" posture (`decisions/0025`) unchanged;
  9b does not introduce a new caching mechanism to offset its marginally
  higher per-file cost over 9a's presence-only check.
- Symbol identity is deliberately reused rather than re-derived, keeping
  9b's actual new-code surface narrow: extending three existing
  detection functions' return types, plus resolving detected names
  against an existing data source.

## Files

- `src/depcompass/usage.py` — extended (see Scope above).
- `src/depcompass/context_graph.py` — extended (`SymbolNode`, upgraded
  `uses` edge shape).
- `src/depcompass/adapters/*.py` — touched only if
  `readme_and_api_surface()` needs the minimal accessor noted above;
  otherwise unchanged.
- `tests/test_usage.py`, `tests/test_context_graph.py` — extended.
- Same-commit docs: `architecture/overview.md`'s "Context graph" section
  (extended to describe symbol-level `uses`), `planning/ROADMAP.md`,
  `planning/CONTEXT.md`, `CHANGELOG.md`.

## Verification

- `pytest` — full suite passes, including the extended test files.
- `ruff check .` — clean.
- Manual — a scratch project with a Python file doing
  `from <vendor> import SpecificExport`, where `SpecificExport` is a
  name known to appear in that vendor's `readme_and_api_surface()`
  output: run `depcompass sync` (bare), inspect `context-graph.json`
  directly, confirm the `uses` edge names `SpecificExport` specifically
  (by its `SymbolNode.id`), not just the owning vendor. Add a second
  file importing an undocumented/internal name from the same vendor and
  confirm it falls back to a vendor-level `uses` edge rather than being
  dropped from the graph entirely.
