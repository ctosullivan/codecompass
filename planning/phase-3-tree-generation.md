# Phase 3: Deterministic Tree Generation

## Scope

**Covered:**
- `src/depcompass/symbols.py` — a `Symbol(name, purpose)` dataclass plus
  one no-AI, no-subprocess extractor per ecosystem
  (`extract_python_symbols`, `extract_rust_symbols`, `extract_npm_symbols`,
  each `Path -> list[Symbol]`), plus `purpose_for_file(path, ecosystem)`
  dispatching to the matching extractor with a generic
  leading-comment-marker fallback (`#`, `//`, `/* */`, `"""`) for files no
  ecosystem parser claims.
- `src/depcompass/deptree.py` — `render_deptree_markdown(root, *,
  max_depth=...)` and `render_deptree_json(root, *, max_depth=...)`,
  rendering a `DepNode` tree with diamond-dependency dedup (back-reference
  repeats), dev-only collapsing to a count, and an explicit depth-cap
  collapse notice.
- `src/depcompass/filetree.py` — `render_filetree_markdown(root,
  ecosystem)`, `render_filetree_json(root, ecosystem)`, and
  `build_symbol_index(root, ecosystem)`, walking a `source_location()`
  path with directory/file pruning and per-file purpose annotations.
- `src/depcompass/adapters/cargo.py`, `python.py` — refactored to call
  `symbols.py`'s extractors instead of keeping private copies
  (`_extract_pub_items`, `_extract_all`/`_ast_fallback` move out); no
  behavior change to either adapter's public methods.
- New ADR recording the reuse-adapter-parsing-over-generic-heuristic
  tradeoff (number confirmed against actual `/decisions` contents at
  implementation time — expected next after `0014`, per the
  numbering-collision lesson from Phase 2).
- Tests: `tests/test_symbols.py`, `tests/test_deptree.py`,
  `tests/test_filetree.py`, plus whatever minimal updates
  `tests/test_adapter_cargo.py`/`test_adapter_python.py` need so their
  existing assertions keep passing against the refactored extraction
  logic.
- Same-commit doc updates: `architecture/overview.md` (Tree generation
  section gets real signatures; Known footguns gains Phase 3-specific
  entries), `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md`.

**Explicitly deferred:**
- Writing `FILETREE.md`/`DEPTREE.md`/`filetree.json`/`deptree.json` to
  disk, and wiring any of this into `sync`/`init`/`check` — Phase 4.
  `deptree.py`/`filetree.py` return strings/dicts only.
- Populating `VendorDigest.file_tree`/`.dep_tree` from these renderers —
  Phase 4 (the fields exist today but stay unset until `sync` calls the
  renderers and assigns the result).
- Cross-linking `FILETREE.md` entries to gap-analysis action pointers —
  gap analysis doesn't exist until Phase 5; nothing to link to yet. Not
  stubbed with placeholder parameters now.
- `vendor/<name>/src/` snapshot copying — `filetree.py` walks whatever
  `Path` it's given (in practice, today, an adapter's raw
  `source_location()`); the copy mechanism itself is Phase 4.
- Switching `npm.py`'s own `readme_and_api_surface()` over to
  `extract_npm_symbols` — it works fine dumping whole `.d.ts` files today;
  Phase 3 only requires the extractor to exist and be correct for
  `filetree.py`'s use, not that npm's adapter adopt it internally.
- `docs/cli-reference.md`/`docs/config-schema.md` changes — expected none,
  since this phase adds no CLI or config-schema surface; confirm this
  holds during implementation rather than assuming it silently.

## Design decisions

- **Purpose-annotation / symbol-index extraction reuses and generalizes
  the per-ecosystem parsing adapters already do for API-surface
  extraction**, rather than one generic language-agnostic heuristic for
  all ecosystems. Cargo's existing `_extract_pub_items` and Python's
  existing `ast`-based `__all__`/docstring extraction generalize from
  "one entry file" to "any file in the tree" and move into `symbols.py`;
  npm gains a new `.d.ts`-based export scan it doesn't have today. A
  generic comment-marker fallback still covers non-source files
  (README, LICENSE, config files) neither approach is mutually exclusive
  with the other — ecosystem-specific parsing just takes priority when it
  applies. Chosen over a single generic heuristic for accuracy and to
  reuse already-validated parsing logic, at the cost of coupling
  `symbols.py`/`filetree.py` to per-ecosystem knowledge the way
  `adapters/` already is.
- **`deptree.json` mirrors `DEPTREE.md`'s deduplicated, depth-capped
  shape** (a repeat `name@version` node becomes `{"ref": "name@version"}`
  instead of a re-expanded subtree) rather than preserving the adapter's
  full raw tree — one consistent view for both human and machine
  consumers. A consumer needing the complete uncapped tree can call the
  adapter directly.
- **Three new flat top-level modules** (`symbols.py`, `deptree.py`,
  `filetree.py`), not a new package — matches the existing flat layout of
  `core.py`/`config.py`/`cli.py`. `adapters/` is a package because four
  files share one ABC; these three share no comparable base class.
- **Dev-only children always collapse to a count** at every level of
  `DEPTREE.md`, not just past some threshold — consistent, predictable
  output regardless of tree size.
- **Depth cap and symbol-index cap always emit an explicit collapse/"+N
  more" notice**, never a silent truncation — an agent reading the output
  must be able to tell an incomplete tree/index from a complete one.
- **Extraction functions never raise** — a file that fails to parse
  (e.g. a syntax error) returns `[]`/`None` rather than propagating an
  exception, since a bad annotation on one file shouldn't break tree
  generation for the rest of the vendor.

## Files

- `src/depcompass/symbols.py` — `Symbol(name: str, purpose: str | None)`
  dataclass; `extract_python_symbols`, `extract_rust_symbols`,
  `extract_npm_symbols` (each `Path -> list[Symbol]`); `purpose_for_file(path:
  Path, ecosystem: Ecosystem) -> str | None`.
- `src/depcompass/deptree.py` — `_DEPTREE_MAX_DEPTH` constant;
  `render_deptree_markdown(root: DepNode, *, max_depth: int =
  _DEPTREE_MAX_DEPTH) -> str`; `render_deptree_json(root: DepNode, *,
  max_depth: int = _DEPTREE_MAX_DEPTH) -> dict`.
- `src/depcompass/filetree.py` — `_PRUNE_DIR_NAMES`, `_PRUNE_FILE_GLOBS`,
  `_SYMBOL_INDEX_CAP` constants; `render_filetree_markdown(root: Path,
  ecosystem: Ecosystem) -> str`; `render_filetree_json(root: Path,
  ecosystem: Ecosystem) -> dict`; `build_symbol_index(root: Path,
  ecosystem: Ecosystem) -> str`.
- `src/depcompass/adapters/cargo.py` — `_extract_pub_items` removed,
  `readme_and_api_surface` calls `symbols.extract_rust_symbols`.
- `src/depcompass/adapters/python.py` — `_ast_fallback`/`_extract_all`
  removed, `readme_and_api_surface`'s fallback path calls
  `symbols.extract_python_symbols`.
- `tests/test_symbols.py` — one extractor at a time, reusing
  `tests/fixtures/sample.pyi`, `sample_lib.rs`, `sample.d.ts`,
  `sample_module_with_all.py`, plus a couple of small new fixtures for the
  generic fallback path.
- `tests/test_deptree.py` — hand-built `DepNode` trees (no fixtures/
  subprocess, same style as `tests/test_core.py`).
- `tests/test_filetree.py` — a synthetic directory tree built in
  `tmp_path`.
- `tests/test_adapter_cargo.py`, `tests/test_adapter_python.py` — updated
  only as needed to keep passing against the refactored extraction logic.
- New ADR (number to be confirmed against actual repo state at
  implementation time — see the collision-avoidance note in Files above).
- `architecture/overview.md`, `planning/ROADMAP.md`,
  `planning/CONTEXT.md`, `CHANGELOG.md` — updated in place.

## Verification

- `pytest` — full suite passes, count increases from the current 42; all
  pre-existing Phase 1/2 tests still pass unchanged after the extraction-
  logic refactor.
- `ruff check .` — clean, including the three new modules.
- `render_deptree_markdown`/`render_deptree_json` on a hand-built tree
  containing a genuine diamond (two branches sharing one `name@version`
  node) produce a back-reference on the second occurrence, not a
  re-expanded subtree.
- `render_deptree_markdown` on a tree deeper than `_DEPTREE_MAX_DEPTH`
  produces an explicit collapse notice, not silent truncation.
- `render_filetree_markdown` on a synthetic tree containing a
  `node_modules/`/`dist/` dir and a `.min.js` file confirms those are
  absent from the output.
- `build_symbol_index` on a synthetic tree exceeding `_SYMBOL_INDEX_CAP`
  produces a "+N more" notice, not a silently truncated list.
- The new ADR has Status/Context/Decision/Alternatives
  considered/Consequences sections matching the existing template.
- `architecture/overview.md`'s Known footguns section lists every new
  Phase 3 limitation (the three arbitrary/tunable constants, per-ecosystem
  symbol-extraction accuracy limits, gap-analysis cross-linking deferred).

## Status

planned — this plan file has been written and reviewed; no
tree-generation code has been implemented yet.
