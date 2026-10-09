# Edge cases and compatibility

## Monorepo resolution is not a filesystem guarantee

The relationship "one vendor, one adapter instance" does not mean "one vendor, one project directory." `HaskellAdapter._resolve_package_dir` demonstrates this directly: a single `project_root` can host multiple vendors' worth of source at once (e.g. `hledger-lib`/`hledger`/`hledger-ui` all inside one `hledger` monorepo checkout). The adapter instance itself narrows `project_root` down to the one subdirectory whose own `package.yaml` declares the matching vendor name, before any other method call on it is meaningful — and must set a `subdirectory` field on the resolved `RepositoryLocation` in that case, or downstream source resolution would clone the *whole* monorepo as if it were that one vendor's own source tree (a real, previously-shipped bug this was fixed to avoid).

## External adapter ecosystem mismatch — a closed, historical gap

Earlier in the project's history, nothing checked an external adapter's wire-reported `ecosystem` string (free text, by protocol design) against the `Ecosystem` value CodeCompass had configured that adapter under. This has been fixed: `ExternalAdapterProcess.initialize` now requires an `expected_ecosystem` argument and raises `AdapterError` on disagreement, and also rejects any reported `capabilities` entry outside the protocol's own closed four-value set. See `docs/concepts/protocol-and-capability.md`.

## Rust/JS/TS coarse-scan false positives

Both `symbols.py`'s and `source_symbols.py`'s Rust/JS/TS extractors use a line-scan/regex technique with no real parse step (`indexed_partial`, see `docs/reference/symbol-extraction.md`). Two concrete, confirmed false-positive shapes exist:
- A multi-line Rust raw-string literal whose own interior line happens to match the anchored declaration pattern.
- A plain `/* ... */` block comment in JS/TS containing commented-out declaration-like text (only `/**` JSDoc comments are specially recognized as comments by this scanner — a plain block comment is not).

Both are silent: the symbol row is created with no diagnostic distinguishing it from a genuine declaration.

## Python extraction is top-level-only

`source_symbols.py`'s Python extractor walks only `ast.iter_child_nodes(tree)` — a module's own direct children. A method defined inside a class, or a function nested inside another function, is never visited and never emitted as its own row.

## Haskell export-list scanning — three deliberately scoped limitations

1. A `module <Name>` re-export entry only resolves file-locally (against this same file's own `import ... as <Name>` aliases); a genuine cross-file resolution of a differently-named module's own export list is never attempted.
2. A CPP-conditional-gated export-list entry is flagged `"undetermined"` rather than resolved either way — the scanner cannot evaluate the preprocessor condition from the file's own text alone, since it depends on which version of an external package the file is actually compiled against.
3. A module with no export list at all is reliably *detected*, but its top-level bindings are not *enumerated* in this version of the scanner — it reports zero symbols plus a diagnostic, by design, not by omission.

## Dependency trees are never deduplicated at the source — only at render time

Every adapter's `dependency_tree()` method returns the full, raw, un-deduplicated tree exactly as the underlying tool reports it — a diamond dependency appears in full, repeated, at every real position in the tree. Deduplication into "see X above" back-references happens only in `deptree.py`'s own rendering step, never earlier. A cycle (a real edge back to an already-visited node, confirmed to occur in `stack dot` output) is guarded against infinite recursion at the adapter level (both the Cargo adapter and the Haskell external adapter's own `Adapter.Deps` module implement an explicit cycle guard) — the repeated edge still appears once at its own real depth, with its own nested children stopped (an empty array), rather than the edge being pretended away.

## Unverified adapter: Cargo

`src/codecompass/adapters/cargo.py`'s own module docstring states directly: **"Unverified against real cargo output — no Rust toolchain in this dev environment... Built entirely against the `_run_json` seam so its parsing logic is unit-tested via hand-written fixture JSON modeled on cargo's public schema docs."** This is a real, disclosed limitation, not an inference — treat the Cargo adapter's behaviour against a real `cargo metadata` invocation as unverified until a Rust toolchain confirms it directly.
