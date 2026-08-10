# 0015. Symbol/purpose extraction reuses per-ecosystem adapter parsing, not a generic heuristic

## Status

Accepted

## Context

Phase 3 (`planning/phase-3-tree-generation.md`) needs two things with no
AI calls: a one-line purpose annotation per file in `FILETREE.md`, and a
flat greppable symbol index alongside it. Two approaches were on the
table: a single generic language-agnostic heuristic (first comment/
docstring line via common markers, symbol names via generic declaration-
keyword regexes) applied uniformly across every ecosystem, or reusing and
generalizing the per-ecosystem parsing the adapters (Phase 2) already do
for API-surface extraction — Cargo's `pub`/`///`-doc-comment scan, and
Python's `ast`-based `__all__`/docstring extraction.

## Decision

`src/depcompass/symbols.py` reuses and generalizes the adapters'
per-ecosystem parsing:
- `extract_rust_symbols` generalizes the Cargo adapter's former
  `_extract_pub_items` (Phase 2) from "one entry file" to "any file,"
  returning structured `Symbol(name, purpose)` objects instead of raw
  joined signature strings.
- `extract_python_symbols` generalizes the Python adapter's former
  `_ast_fallback` per-node loop (previously hardcoded to `__init__.py`
  only) the same way. `__all__` extraction stays adapter-local — it's
  module-level data, not a symbol.
- `extract_npm_symbols` is new: a regex scan of `.d.ts` files for
  `export function/class/interface/const/type/enum <name>` declarations
  plus a leading JSDoc first line. No npm equivalent existed in Phase 2 —
  `NpmAdapter.readme_and_api_surface` dumps whole `.d.ts` files rather
  than parsing declarations out of them.
- A generic leading-comment-marker fallback (`#`, `//`, `/*`, `"""`,
  `'''`) still covers files no ecosystem-specific extractor claims
  (README, LICENSE, config files) — the two approaches aren't mutually
  exclusive; ecosystem-specific parsing just takes priority when it
  applies.

`adapters/cargo.py` and `adapters/python.py` are updated to call into
`symbols.py` rather than keeping private copies of this logic.

## Alternatives considered

- **Single generic language-agnostic heuristic for every ecosystem.**
  Rejected as the primary strategy — it would ignore parsing logic
  Phase 2 already wrote and validated (including two real cross-platform
  bugs it surfaced, `decisions/0014`), and produce meaningfully less
  accurate symbol names/purposes for Python and Rust than `ast`/doc-
  comment-aware parsing already provides. Kept as the fallback for files
  no ecosystem parser claims, since something is needed for non-source
  files regardless of which primary strategy was chosen.
- **Leave the extraction logic duplicated** — one copy in each adapter
  (Phase 2 style), one copy in `filetree.py` (Phase 3). Rejected: two
  independently-maintained implementations of "how do I find pub Rust
  items" or "how do I find Python top-level defs" drift apart silently:
  a bug fixed in one place stays broken in the other.

## Consequences

- `symbols.py` is now coupled to per-ecosystem knowledge the same way
  `adapters/` already is — a fourth ecosystem added later needs both a
  new `EcosystemAdapter` subclass and a new `extract_*_symbols` function,
  not just the former.
- **`CargoAdapter.readme_and_api_surface()`'s rendered output format
  changed** as a direct consequence of switching to name-based (not raw-
  signature-based) extraction: items now render as `name: purpose`
  instead of the full `pub fn ...` signature line. `tests/test_adapter_cargo.py`
  was updated accordingly (see `planning/phase-3-tree-generation.md`'s
  Tests section, which anticipated this).
- **Incidental correctness improvement**: the old string-signature-based
  extraction's documented "misses multi-line signatures" limitation
  (`decisions/0002`, `tests/test_adapter_cargo.py`) no longer applies to
  name extraction — a function name is fully present on the opening `pub
  fn` line regardless of how many lines its parameter list spans, so
  `extract_rust_symbols` captures `multi_line_signature`'s full name where
  the old signature-text capture would have been truncated. The
  underlying coarse-scan approach (line-based `pub` prefix matching, no
  real parser) is otherwise unchanged and still has other blind spots
  (e.g. `pub(crate) fn`, attribute macros before a `pub` item).
- `extract_npm_symbols`'s regex-based JSDoc/export scan is new and,
  like the Cargo adapter's `pub` scan, is coarse — not validated against
  a wide range of real-world `.d.ts` authoring styles beyond the hand-
  written fixtures in `tests/fixtures/`.
