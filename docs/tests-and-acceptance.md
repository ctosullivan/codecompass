# Tests and acceptance behaviour

Requirement-shaped formal acceptance criteria exist in the available evidence for two capabilities: doc-origin pinned-reference tracking and Haskell API-surface extraction. Both sets below are reproduced from the project's own canonical requirement records, each authorised by a named, approved Decision, each currently `verified`.

## Doc-origin pinned-reference tracking

Authorised by `DEC-DOCORIGIN-001` (approved) — decides to name the new `doc_artifacts.origin` value `pinned_reference`, implement automatic detection in `scan_spec_docs` via frontmatter-key presence, scope the fix to `spec_doc`-kind rows only (no change to `vendor_doc` handling), and require no backfill migration since `doc_artifacts` is fully repopulated on every whole-project sync.

| Id | Requirement | Status |
|---|---|---|
| `REQ-DOCORIGIN-001` | `doc_artifacts.origin`'s CHECK constraint must accept a new value, `'pinned_reference'`, added via the existing migration mechanism, with no change required to any other `origin` consumer for this addition alone. | verified |
| `REQ-DOCORIGIN-002` | `scan_spec_docs` must assign `origin='pinned_reference'` to a `dev-docs/**/*.md`-glob-matched file whose leading content is a YAML frontmatter block containing both a `resolved_commit` key and a `source_url` key. A file with no such frontmatter, or missing either key, must keep the existing `origin='project'` behaviour unchanged. | verified |
| `REQ-DOCORIGIN-003` | A new test fixture must exercise `scan_spec_docs`'s new branch directly, closing a previously-missing test-coverage gap; every existing test asserting `origin='project'` for frontmatter-free fixtures must continue to pass unchanged. | verified |

## Haskell API surface extraction

Authorised by `DEC-HSAPI-001` (approved) — adopts all six of the governing design document's own recommended answers unchanged, including the baseline comment-stripping-and-tokenising scan mechanism, ratified by `CL-HSAPI-001`'s own compiler-verified sufficiency check.

| Id | Requirement | Status |
|---|---|---|
| `REQ-HSAPI-001` | For the baseline export-list shapes (bare identifiers in either comma style, `Type(..)` all-constructors expansion, Haddock `-- * Section` headers, whole-line commented-out entries), the scanner must produce exactly the exported-name set a real GHC `:browse` would report. | verified |
| `REQ-HSAPI-002` | A `module <Name>` entry must be recorded as a re-export occurrence, never asserted as a flattened, fully-resolved name list. If `<Name>` matches a file-local `import ... as <Name>` alias, the real module(s) it covers in this file are additionally recorded. No cross-file read is ever performed. | verified |
| `REQ-HSAPI-003` | A `#if`/`#endif` CPP-conditional span inside an export list must cause the enclosed entry/entries to be flagged `"undetermined"`, never silently included or excluded. | verified |
| `REQ-HSAPI-004` | Before scanning any module's export list, the adapter must determine whether that module is part of the package's own exposed surface (explicit `exposed-modules`, or hpack's own default). A module outside the exposed set must contribute no symbols, regardless of its own export list. | verified |
| `REQ-HSAPI-005` | A module with no export list at all must be reliably detected as such, with no false positives/negatives, but must not have its top-level bindings enumerated in this version — contributing zero symbols plus one diagnostic. | verified |
| `REQ-HSAPI-006` | Purpose-pairing must use a two-pass algorithm: collect exported names from the header first, then separately locate each name's own definition site in the file body and record the nearest preceding `-- | ...` comment there — independent of the name's position in the export list. A name with no such comment correctly reports `purpose: null`, not an error. | verified |

## First-party source/symbol indexing

No formal Decision/Requirement records exist in the available evidence for this capability, unlike the two above — its only authorising reference is a bare ADR title (`decisions/0065`) plus a Phase-77 plan document not visible to this reconstruction. Its real behaviour is exhaustively confirmed instead by the unit test suite (`tests/test_source_symbols.py`, `tests/test_graph.py`) and documented directly from source in `docs/reference/symbol-extraction.md`.
