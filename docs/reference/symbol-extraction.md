# Reference: symbol extraction

CodeCompass extracts symbols in two structurally separate directions, for two different purposes. Keeping these apart matters — they use different models and different vocabularies.

## Vendor-facing: a dependency's own public API surface (`symbols.py`, the Haskell `Adapter.Scanner`)

Per-ecosystem, no-AI, mechanical extraction of what a *dependency* exposes — used to render a vendor's `## Public API surface` section and to populate the context graph's `symbols` table.

- **Rust** (`extract_rust_symbols`): a coarse line-based scan for `pub fn`/`pub struct`/`pub enum`/`pub trait` items, paired with an immediately preceding `///` doc-comment block.
- **Python** (`extract_python_symbols`): `ast`-based scan of a file's top-level `def`/`class` statements, paired with their own docstring.
- **npm** (`extract_npm_symbols`): regex scan of a `.d.ts` file for `export function/class/interface/const/type/enum <name>`, paired with a leading `/** ... */` JSDoc block's first content line.
- **Haskell** (external — `Adapter.Scanner` in `codecompass-adaptor-haskell`): a comment-stripping, identifier-tokenising scan over a module's export-list span (`module Name (...)  where`), independently confirmed (`:browse` cross-check against a real compiler) sufficient for the baseline shapes — bare identifiers in either comma style, `Type(..)` (expands to every real data constructor), Haddock `-- * Section` headers, commented-out entries.

  Beyond the baseline, several real, named complications exist and are handled with an explicit, deliberate policy, not silently:
  - A `module <Name>` re-export entry is recorded as occurring, with file-local alias resolution only (matching this same file's own `import ... as <Name>` lines) — never a cross-file read of the aliased module's own export list.
  - A name gated inside a `#if`/`#endif` C-preprocessor conditional is flagged `kind: "undetermined"` rather than silently included or excluded — the scanner cannot evaluate the condition from the file's own text alone.
  - A module with **no** export list at all (`module Name where`) is reliably detected as such but its top-level bindings are **not enumerated** in this version — it contributes zero symbols plus a diagnostic, by explicit design, not an omission.
  - Purpose-pairing is a genuine two-pass algorithm: collect exported names from the header first, then separately locate each name's own definition site anywhere later in the file body and check *that* site's preceding `-- | ...` comment — Haskell structurally decouples where a name is declared exported from where it's documented, unlike Rust's single-forward-scan approach.
  - A package's own `exposed-modules` list (explicit in `package.yaml`, or hpack's own default of "every module in `source-dirs` minus `other-modules`") is resolved first — a module not in a package's exposed set contributes no symbols regardless of its own export list.

The wire protocol's `kind: "export"|"reexport"|"undetermined"` field (see `docs/reference/protocols.md`) is exactly how this classification crosses the external-adapter process boundary; `HaskellAdapter.symbols()` converts it directly into CodeCompass's own `Symbol.export_kind` field.

## Project-facing: the consuming project's own first-party implementation symbols (`source_symbols.py`)

A structurally different question — "what does *this project* implement," not "what does a dependency expose" — extracted independent of `vendor.toml`, with every top-level declaration included (not filtered to only "public" ones), and a separate `exposure` classification recorded per symbol instead.

A dedicated five-value classification, `Language` (`python`/`rust`/`javascript`/`typescript`/`haskell`), exists specifically because `core.Ecosystem` cannot distinguish JavaScript from TypeScript (both collapse to the single `npm` package-ecosystem value), while symbol-kind extraction genuinely needs that distinction.

### `SymbolIndexStatus` — a five-state result, never a bare ambiguous empty list

| Status | Meaning |
|---|---|
| `indexed` | A real structural parser ran (`ast.parse`, Python only) and either succeeded (possibly finding zero symbols) or never reaches this status if parsing failed. |
| `indexed_partial` | A coarse line-scan/regex heuristic ran (Rust, JS, TS) — no real parse step, so it can never fail structurally, and runs unconditionally once the file is read regardless of what it finds. |
| `unsupported` | No extractor exists for this language at all (Haskell, currently) — the file is never even opened. |
| `parse_error` | Python-specific — `ast.parse` raised `SyntaxError`. |
| `unreadable` | Any language — `OSError`/`UnicodeDecodeError` on read. |

`indexed`/`indexed_partial` are distinguished purely by **technique fidelity**, never by whether anything was found — the mapping from language to one or the other is fixed, not content-dependent.

### Exposure classification — strict, per-language disjoint subsets

| Language | Values actually produced |
|---|---|
| Python | `public` (no leading underscore) or `conventional_private` (leading underscore) |
| Rust | `public` (bare `pub`), `restricted` (any `pub(crate)`/`pub(super)`/`pub(in path)`/`pub(self)` form), or `internal` (no modifier) |
| JS/TS | `public` (leading `export` present) or `internal` (absent) |

`unknown` is a schema-level allowance for a hypothetical future, less-certain extractor — none of the three real extractors above ever produces it. `conventional_private` is deliberately distinct from `internal`: the former names a naming *convention* a caller can freely ignore; the latter names a language-enforced non-visibility default.

### Confirmed, real extraction-fidelity limitations

- A multi-line Rust raw-string literal whose own interior line happens to match the anchored item pattern produces a genuine false-positive `source_symbols` row. A plain `/* ... */` block comment in JS/TS (as opposed to a `/**` JSDoc comment, which *is* specially recognized) is not treated as a comment at all, so a commented-out declaration inside one also produces a genuine false positive. Both are silent — `status` stays `indexed_partial`, `diagnostic` stays `None`.
- Python extraction is **top-level-only** — no recursive descent into a class's or function's own body, so a method or a nested function is never visited or emitted as its own row.
- A JS/TS `const` binding's `kind` is recorded literally as `"const"`, never `"function"`, regardless of the right-hand side — `export const foo = () => {}` is schema-indistinguishable from `export const PI = 3.14`.

### Occurrence-based symbol identity

`source_symbols`'s identity is `(source_file_id, name, kind, line)`, never name alone — specifically so ordinary function overloading (Python's `@typing.overload`, TypeScript's repeated signature declarations) produces multiple, individually real rows rather than a uniqueness collision or a silently-merged/overwritten single row. `line` is never `None` — an extractor that cannot determine a location for a candidate does not emit a row for it at all.
