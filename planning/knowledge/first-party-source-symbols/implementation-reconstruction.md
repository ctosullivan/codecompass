# As-built reconstruction: first-party source/symbol subsystem

Reconstructed from primary evidence only, per `TASK.md` in this same
directory. Inputs consulted, in full, freshly re-read for this pass:
`src/codecompass/source_symbols.py`, `src/codecompass/graph_schema_fragment.py`,
`tests/test_source_symbols.py`, `pyproject.toml`. No other file was read or
consulted — no ADR, no planning doc, no README, no git history, no prior
reviewed conceptual model, and no memory of this export's earlier
(truncated) state was relied on. Where the code's own comments/docstrings
*name* something outside this export (an ADR, `sync.py`, `cli.py`, a
planning doc), that reference is reported as "the code claims X exists" —
never treated as evidence for what X actually contains, since I have not
read it.

**Note on this revision:** this export was corrected since a prior
reconstruction pass. That pass reported `SourceSymbolRow` as missing
`line`/`purpose`/`exposure` fields that `_sync_source_symbols` reads off
it — an apparent internal inconsistency. Re-reading the export fresh: this
is **no longer present**. See §3 and the dedicated note below for the
verification.

---

## 1. Modules

`source_symbols.py` is a single flat module with four sections, in file
order:

1. **Vocabulary types** (lines 51–113): `Language` (`StrEnum`: PYTHON,
   RUST, JAVASCRIPT, TYPESCRIPT, HASKELL), `SymbolIndexStatus` (`StrEnum`:
   INDEXED, INDEXED_PARTIAL, UNSUPPORTED, PARSE_ERROR, UNREADABLE), plus
   private suffix tables (`_JS_FAMILY_SUFFIXES`, `_TS_SUFFIXES`,
   `_LANGUAGE_BY_SUFFIX`) and three compiled regexes (`_RUST_ITEM_RE`,
   `_JS_FAMILY_ITEM_RE`, `_JS_FAMILY_JSDOC_START_RE`).
2. **Result shapes** (lines 116–146): two frozen dataclasses,
   `SourceSymbol` (one occurrence) and `SourceFileExtraction` (one file's
   outcome: status + diagnostic + symbols tuple).
3. **Discovery** (lines 149–169): `discover_source_files`, a thin
   suffix-classification wrapper over `iter_source_files`.
4. **Extraction** (lines 172–293): one public dispatcher,
   `extract_source_symbols_for_file`, plus three private per-language
   workers: `_extract_python_source_symbols` (real `ast` parse),
   `_extract_rust_source_symbols` (line-scan + regex), and
   `_extract_js_family_source_symbols` (line-scan + regex, shared by both
   JS and TS).

Each worker's responsibility is identical in shape: read the file
defensively, walk it once, and return a `SourceFileExtraction` — never an
exception, never a bare list standing in for more than one cause.

`graph_schema_fragment.py` is explicitly **not** a module of its own — its
own header (lines 1–9) states it is a curated, non-contiguous extract of
six named blocks copied verbatim out of `graph.py` (at the project's main
HEAD `b4641cc`), each with its own cited real line range. It supplies: DDL
for two tables (Block 1), two persistence-row dataclasses (Block 2), a
column-migration function (Block 3), two upsert/sync functions (Blocks 4
and 5), and two query functions (Block 6). Block 6's own header states
that a third function, `doc_code_trace`, follows immediately in the real
file but is **deliberately excluded in full** — "out of this topic's
scope" — and the block visibly ends cleanly after `source_symbol_profile`
(line 335) with no dangling or cut-off signature. This is a correction
from a prior version of this export, where the fragment reportedly ended
mid-way through a `doc_code_trace` signature; that dangling fragment is
not present in the file as now read.

## 2. APIs / surface

From `source_symbols.py`, everything a caller can actually reach:

- `Language` (`StrEnum`) — `PYTHON`, `RUST`, `JAVASCRIPT`, `TYPESCRIPT`,
  `HASKELL`.
- `SymbolIndexStatus` (`StrEnum`) — `INDEXED`, `INDEXED_PARTIAL`,
  `UNSUPPORTED`, `PARSE_ERROR`, `UNREADABLE`.
- `SourceSymbol(name: str, kind: str, line: int, purpose: str | None = None, exposure: str | None = None)`
  — frozen dataclass. `line` is never `None` by construction: an extractor
  unable to determine a line for a candidate does not emit a row for it at
  all (stated explicitly in the docstring, and consistent with every
  extractor's code).
- `SourceFileExtraction(status: SymbolIndexStatus, diagnostic: str | None, symbols: tuple[SourceSymbol, ...])`
  — frozen dataclass, the return type of every extraction call.
- `discover_source_files(project_root: Path) -> list[tuple[str, Language]]`
  — every recognized first-party source file under `project_root`, as
  `(relative_posix_path, Language)` pairs.
- `extract_source_symbols_for_file(path: Path, language: Language) -> SourceFileExtraction`
  — the single public entry point for extraction; dispatches by
  `Language` to one of three private workers or returns `UNSUPPORTED`
  directly.

Everything else (`_extract_python_source_symbols`,
`_extract_rust_source_symbols`, `_extract_js_family_source_symbols`, the
suffix tables, the regexes) is prefixed `_` — private, not part of the
surface a caller is meant to use directly. `extract_source_symbols_for_file`
is the only sanctioned way to reach per-language behavior.

From `graph_schema_fragment.py` (i.e. from `graph.py`, per its cited
blocks):

- `SourceFileRow(path: str, language: str | None = None, content_hash: str | None = None, symbol_index_status: str | None = None, symbol_index_diagnostic: str | None = None)`
  — frozen dataclass, one `source_files` row, keyed by `path`.
- `SourceSymbolRow(source_file_path: str, name: str, kind: str, line: int, purpose: str | None = None, exposure: str | None = None)`
  — frozen dataclass, one `source_symbols` row, keyed by
  `(source_file_path, name, kind, line)`.
- `_migrate_source_files_columns(conn) -> None` — private, adds Phase-77's
  four new nullable columns to a pre-existing `source_files` table.
- `_sync_source_files(conn, source_files) -> dict[str, int]` — private,
  upserts `source_files` by `path`, returns `{path: id}`.
- `_sync_source_symbols(conn, source_symbols, source_file_ids) -> None` —
  private, upserts `source_symbols` by `(source_file_id, name, kind, line)`.
- `source_file_profile(conn, path: str) -> dict | None` — public query,
  one file's full first-party profile plus its vendor usages.
- `source_symbol_profile(conn, name: str) -> list[dict]` — public query,
  every symbol row named `name` across every first-party file.

All the `_sync_*`/`_migrate_*` functions are private (module-internal in
the real `graph.py`); only the two `*_profile` functions and the two
dataclasses are a plausible external surface, consistent with `graph.py`
being the schema/persistence layer rather than a caller-facing API.

## 3. Data / persistence

Two tables, defined with `CREATE TABLE IF NOT EXISTS` (Block 1):

**`source_files`**
```
id                      INTEGER PRIMARY KEY
path                    TEXT NOT NULL UNIQUE
language                TEXT
content_hash            TEXT
symbol_index_status     TEXT CHECK (IN 'indexed','indexed_partial','unsupported','parse_error','unreadable')
symbol_index_diagnostic TEXT
```
`language`, `content_hash`, `symbol_index_status`, `symbol_index_diagnostic`
are all nullable with no default, on both a fresh table and a migrated one
— the fragment's own comments cite this as a deliberate, previously
corrected contract (decisions/0065, referencing decisions/0064 as the
prior-established pattern). I have not read either ADR; I report only that
the code's comments assert this and that the schema/migration code is
mutually consistent with the claim (see below).

**`source_symbols`**
```
id             INTEGER PRIMARY KEY
source_file_id INTEGER NOT NULL REFERENCES source_files(id) ON DELETE CASCADE
name           TEXT NOT NULL
kind           TEXT NOT NULL
line           INTEGER NOT NULL
purpose        TEXT
exposure       TEXT CHECK (IN 'public','restricted','internal','conventional_private','unknown')
UNIQUE (source_file_id, name, kind, line)
```
plus `idx_source_symbols_file` on `source_file_id`. Identity is
occurrence-based: `(source_file_id, name, kind, line)`, not name alone —
`line` is `NOT NULL`, matching `SourceSymbol.line`'s own non-null
guarantee in `source_symbols.py`.

**Verification of the previously-reported inconsistency (now resolved):**
`_sync_source_symbols` (Block 5) reads six fields off each `SourceSymbolRow`
it's given: `s.source_file_path`, `s.name`, `s.kind`, `s.line`, `s.purpose`,
`s.exposure` (used both to build the `incoming` identity set and as bind
parameters for the `INSERT ... ON CONFLICT ... DO UPDATE SET purpose =
excluded.purpose, exposure = excluded.exposure`). `SourceSymbolRow` as
defined in this export (Block 2, lines 82–97) now declares exactly those
six fields: `source_file_path: str`, `name: str`, `kind: str`, `line: int`,
`purpose: str | None = None`, `exposure: str | None = None`. Every field
`_sync_source_symbols` reads is present on the dataclass. **There is no
inconsistency in the corrected export** — the dataclass and its one
real consumer agree exactly. (The prior report's finding was accurate
against the export it was given at the time, which was missing `line`,
`purpose`, and `exposure` from the dataclass definition; that was a
curation/extraction defect in producing the export, not a defect in the
real `graph.py`, and it is not reproducible against this corrected copy.)

`_sync_source_files` similarly upserts by `path` (the natural key),
deleting rows whose path is no longer present in the incoming set,
otherwise `INSERT ... ON CONFLICT(path) DO UPDATE`. `_sync_source_symbols`
does the same at row-level: computes `existing - incoming` (by 4-tuple
identity) and deletes those, then upserts everything incoming. Both
"mirror `_sync_vendors`/`_sync_symbols`'s exact shape" per their own
docstrings (a claim about code outside this export — not independently
verifiable here, but self-consistent with the pattern shown).

`_migrate_source_files_columns` uses `PRAGMA table_info` to detect already
existing columns before `ALTER TABLE ... ADD COLUMN`, additive-only, never
drop-and-recreate — the code matches its own stated rationale (protecting
`uses_edges.source_file_id ON DELETE CASCADE` from an accidental
cascade-delete via table recreation). It returns early (no-op) if
`source_files` doesn't exist yet at all.

`source_file_profile` and `source_symbol_profile` are read-only queries;
neither writes anything. `source_file_profile` joins `source_symbols` (by
`source_file_id`) and separately `uses_edges`/`vendors`/`symbols` (left
join on `symbols`, so a vendor usage with no resolved symbol still
appears, `symbol` slot would be `None`). `source_symbol_profile` joins
`source_symbols` to `source_files` and returns every match for a bare
`name`, across files — names are explicitly not assumed globally unique.

## 4. Dependencies

`source_symbols.py` imports:
- stdlib: `ast`, `re`, `dataclasses.dataclass`, `enum.StrEnum`,
  `pathlib.Path`, plus `from __future__ import annotations`.
- first-party: `codecompass.filetree.iter_source_files`,
  `codecompass.usage._PROJECT_PRUNE_DIR_NAMES`.

Neither `filetree.py` nor `usage.py` is in this export, so their internals
are not directly inspectable. What's inferable purely from call-site
behavior plus the tests: `iter_source_files(project_root, prune_dirs=...)`
yields `Path` objects under `project_root` (accepts a `prune_dirs`
keyword); `_PROJECT_PRUNE_DIR_NAMES` is a set/collection of directory
names that, per the module docstring, covers "build/dependency noise and
the unconditionally-cloned `vendor/` directory only" — and per
`test_discover_source_files_keeps_tests_prunes_build_noise`, this set
prunes `node_modules/` and `vendor/` but does **not** prune `tests/`
(a real first-party test file surfaces in the result: `"tests/test_a.py"
in result`). This is stated in the module docstring as a deliberate
contrast with `filetree._PRUNE_DIR_NAMES` (said to additionally prune
`test`/`tests`/`__tests__`/`fixtures`) — that comparison names code
outside the export and is not independently verified here, only
consistent with the one test that exercises it.

`graph_schema_fragment.py`'s visible code uses `sqlite3.Connection` (type
hint only — no `import sqlite3` line appears, consistent with this being
an extracted fragment, not the whole file) and `Sequence` (used
unqualified in two signatures, likewise no visible import — same reason).
No external/third-party imports appear in either file.

## 5. Runtime paths

Traced for a representative Python file (the shape exercised most by the
tests, and the only language with a real AST-based path):

1. Caller has a `project_root: Path`. Calls `discover_source_files(project_root)`.
2. That calls `iter_source_files(project_root, prune_dirs=_PROJECT_PRUNE_DIR_NAMES)`,
   filters each yielded path by `path.suffix` against `_LANGUAGE_BY_SUFFIX`
   (skipping anything not in the map, e.g. `.txt`), and returns
   `(relative_posix_path, Language)` pairs for everything recognized.
3. For each `(rel_path, language)` pair, caller (not shown in this export)
   presumably calls `extract_source_symbols_for_file(full_path, language)`.
4. For `Language.PYTHON`, this dispatches to `_extract_python_source_symbols`:
   reads the file as UTF-8 (catching `OSError`/`UnicodeDecodeError` →
   `UNREADABLE`), `ast.parse`s it (catching `SyntaxError` → `PARSE_ERROR`),
   then iterates only `ast.iter_child_nodes(tree)` — i.e. **direct children
   of the module node only** — collecting `FunctionDef`/`AsyncFunctionDef`/
   `ClassDef` nodes. For each: `kind` is `"function"` or `"class"`;
   `exposure` is `"conventional_private"` if the name starts with `_`,
   else `"public"` (binary — no `"restricted"`, `"internal"`, or
   `"unknown"` ever produced by this path); `purpose` is
   `ast.get_docstring(node)` (may be `None`); `line` is `node.lineno`.
   Returns `SourceFileExtraction(INDEXED, None, tuple(symbols))` — even
   when `symbols` is empty (confirmed distinct from failure by
   `test_python_extraction_indexed_with_zero_symbols_is_distinguishable_from_failure`).
5. Caller (again, not shown) presumably converts the resulting
   `(project, file, SourceFileExtraction)` data into a `SourceFileRow` and
   a list of `SourceSymbolRow`s (note: `SourceSymbol` itself has no
   `source_file_path` field — that has to be supplied externally, since
   it's not something the extractor knows), then calls `_sync_source_files`
   followed by `_sync_source_symbols(conn, rows, source_file_ids)` — the
   latter needs the `{path: id}` map the former returns, so the ordering
   is forced by the function signatures themselves.
6. `_sync_source_files` diffs existing vs. incoming `path`s, deletes
   stale rows, then upserts every incoming row via
   `INSERT ... ON CONFLICT(path) DO UPDATE`, and returns `{path: id}` read
   back from the table.
7. `_sync_source_symbols` diffs existing vs. incoming
   `(source_file_id, name, kind, line)` 4-tuples, deletes stale ones, then
   upserts every incoming row via
   `INSERT ... ON CONFLICT(source_file_id, name, kind, line) DO UPDATE SET purpose=…, exposure=…`.
8. Later, a read path: `source_file_profile(conn, path)` looks up the
   `source_files` row by `path`; if absent, returns `None`. Otherwise
   builds `symbols` (all `source_symbols` rows for that file, ordered by
   `line, name`) and `vendor_usages` (joined from `uses_edges`/`vendors`,
   left-joined to `symbols` — the vendor API-surface table, distinct from
   `source_symbols`), returning one combined dict.

For Rust and JS/TS files, steps 3–4 instead go through
`_extract_rust_source_symbols` / `_extract_js_family_source_symbols`: a
single pass over `source.splitlines()`, tracking a small amount of
"doc comment pending" state line-to-line, matching each stripped line
against a single compiled regex anchored at line start (`^...`), never
parsing multi-line constructs. Both always return `INDEXED_PARTIAL` on a
successful read (never `INDEXED` — that status is Python-only in this
code), or `UNREADABLE` on a read failure. Neither has a `PARSE_ERROR`
path at all — there is no failure mode distinct from "unreadable" for
these two, since a regex/line-scan never "fails to parse" the way
`ast.parse` can raise `SyntaxError`.

For an unrecognized `Language` value reaching `extract_source_symbols_for_file`
(in practice, `Language.HASKELL` today — see §9), the function's final
`return` fires directly: `SourceFileExtraction(UNSUPPORTED, None, ())`,
without ever touching the filesystem.

## 6. Extension points

The real, existing pattern for adding a new language:

1. Add a new `Language` enum member.
2. Add its file suffix(es) to `_LANGUAGE_BY_SUFFIX`.
3. Add a branch in `extract_source_symbols_for_file` dispatching to a new
   `_extract_<lang>_source_symbols(path) -> SourceFileExtraction` worker.
4. Write that worker to follow the established contract: catch
   read failures → `UNREADABLE`; catch structural failures (if a real
   parser is used) → `PARSE_ERROR`; otherwise return `INDEXED` (real
   parser) or `INDEXED_PARTIAL` (regex/line-scan), with a `tuple[SourceSymbol, ...]`
   (possibly empty) and never `None` for `symbols`.
5. `Language.HASKELL` already exists as exactly this kind of half-added
   extension point today: the enum member and the suffix mapping (`.hs`)
   are both present, so `discover_source_files` recognizes and reports
   `.hs` files with `Language.HASKELL` — but no
   `_extract_haskell_source_symbols` worker exists and
   `extract_source_symbols_for_file` has no `Language.HASKELL` branch, so
   it falls through to the final `UNSUPPORTED` return. This is a live,
   in-code illustration of "recognized but not yet extracted," and the
   most direct model for what adding e.g. Go or Java would look like:
   discovery and extraction are already decoupled steps in this code, not
   just in theory.

On the persistence side, the extension point for a new "profile" query or
additional stored fact would plausibly follow `source_file_profile`'s /
`source_symbol_profile`'s pattern (a `SELECT` shaped into a list of dicts),
and a new nullable column would follow `_migrate_source_files_columns`'s
additive `ALTER TABLE ... ADD COLUMN` pattern — but nothing in this export
demonstrates a *second* instance of either pattern being added later, so
this is inference from one example each, not confirmed repetition.

## 7. Build / configuration

From `pyproject.toml`:
- `requires-python = ">=3.11"` — consistent with `source_symbols.py`'s use
  of `enum.StrEnum` (Python 3.11+) and PEP 604 `X | None` unions (used
  throughout, e.g. `language: str | None = None`), and with
  `from __future__ import annotations` being present anyway (belt-and-braces,
  or a residual habit — both syntaxes are already valid at the stated
  floor).
- Package: `codecompass-context` v1.0.0, GPL-3.0-or-later, classifiers
  claim Python 3.11/3.12/3.13 support.
- Runtime dependencies: `typer`, `rich`, `anthropic`, `pipdeptree`,
  `pyyaml` — none of these are imported by either file in this export.
- Dev dependencies: `pytest`, `ruff`, `jsonschema` — `pytest` is what
  `test_source_symbols.py` is written against (plain `assert`, `tmp_path`
  fixture — standard pytest, no custom fixtures/plugins visible in this
  file).
- `[tool.pytest.ini_options]`: `testpaths = ["tests"]`; a `smoke` marker
  is declared ("exercises a real external tool (npm/cargo)... skipped
  automatically when the tool isn't present") but `test_source_symbols.py`
  does not use it — none of its tests are marked `smoke`, and none touch
  npm/cargo; everything here runs against files written directly into
  `tmp_path`.
- `[tool.ruff]`: `line-length = 100`, `target-version = "py311"`,
  lint selects `["E", "F", "I", "UP"]` (pycodestyle errors, pyflakes,
  isort, pyupgrade) — consistent with the modern-syntax style seen in
  both source files (`X | None`, `StrEnum`, no `Optional`/`Union` imports).
- `packages.find where = ["src"]` — matches this export's own `src/codecompass/...`
  layout.
- No `tomli` dependency, with an explicit comment explaining why
  (`tomllib` is stdlib at the stated Python floor) — this is about TOML
  parsing elsewhere in the real project, not used by either file in this
  export; noted only because it's the one dependency-adjacent comment in
  the file.

## 8. Tests

`tests/test_source_symbols.py` — 16 tests, all plain functions using
`tmp_path`, no mocks. What each actually asserts (not just its name):

**Discovery (4 tests):**
- `test_discover_source_files_classifies_every_supported_language` — one
  file per language suffix (`.py .rs .js .ts .hs`) plus one `.txt`; asserts
  each recognized suffix maps to the *correct* `Language` member (identity
  via `is`, not just truthiness) and that `.txt` is excluded from the
  result entirely (not present as a key, not mapped to `None`).
- `test_discover_source_files_distinguishes_js_from_ts` — `.jsx` → JAVASCRIPT,
  `.tsx` → TYPESCRIPT specifically (confirms the JS/TS suffix split is
  real, not both landing on one language).
- `test_discover_source_files_keeps_tests_prunes_build_noise` — a file
  under `tests/` is present in the result; files under `node_modules/`
  and `vendor/` are absent (checked via path-prefix, e.g.
  `not any(p.startswith("node_modules/") for p in result)`). This is the
  one test that actually exercises the "keep tests, prune build/vendor
  noise" claim from the module docstring.
- `test_discover_source_files_works_with_zero_vendor_config` — asserts,
  via a comment in the test itself, that `discover_source_files` takes
  only `project_root` (no vendor-config parameter exists at all) —
  the zero-vendor independence claim is enforced by the function's own
  signature, not by passing an empty config value.

**Python extraction (5 tests):**
- `..._is_indexed_with_full_scope` — a module with a public function
  (with docstring), a `_private` function, and a public class; asserts
  `status == INDEXED`, `diagnostic is None`, correct `kind` per symbol,
  `exposure` split correctly (`public` / `conventional_private`), and
  `purpose` pulled from the real docstring text.
- `..._indexed_with_zero_symbols_is_distinguishable_from_failure` — a file
  with only `x = 1` (no functions/classes at all); asserts `status ==
  INDEXED` (not some failure status) with `symbols == ()` — confirms
  empty-but-successful is a real, distinct outcome.
- `test_python_syntax_error_is_parse_error_not_empty_result` — a
  deliberately broken `def broken(:` ; asserts `status == PARSE_ERROR`,
  `diagnostic is not None`, `symbols == ()`.
- `test_python_unreadable_file` — invalid UTF-8 bytes; asserts `status ==
  UNREADABLE`, `diagnostic is not None`.
- `test_python_overload_produces_distinct_rows_never_crashes` — three
  `def foo` declarations (two `@overload`-decorated + one real
  implementation); asserts exactly 3 rows named `foo`, on 3 distinct
  lines. Note: this test does not touch decorator-awareness at all — the
  extractor doesn't inspect `@overload` specially; it simply records every
  top-level `FunctionDef` node regardless of decorators, so three
  same-named `def`s produce three rows for any reason, not specifically
  because `@overload` was recognized.

**Rust extraction (3 tests):**
- `..._is_indexed_partial_with_full_exposure_model` — one `pub fn` (with a
  `///` doc comment immediately above), one each of `pub(crate)`,
  `pub(super)`, `pub(in crate::module)`, `pub(self)`, and two
  no-modifier items; asserts `status == INDEXED_PARTIAL`, bare `pub` →
  `public`, every `pub(...)` variant → `restricted` (all four modifier
  forms collapse to the same `restricted` value — the regex captures the
  distinction but the classification logic only distinguishes bare-`pub`
  vs. any-parenthesized vs. none), no modifier → `internal`, and that the
  `///` doc line attached correctly to the immediately-following item's
  `purpose`.
- `..._overload_like_repeated_declarations_produce_distinct_rows` — two
  differently-named functions (`foo`, `foo_two`) — despite the name, this
  does not test same-name repetition at all; it only confirms two
  distinct declarations both surface.
- `test_rust_unreadable_file` — invalid UTF-8; asserts `status == UNREADABLE`.
  (No Rust `PARSE_ERROR` test exists — consistent with there being no
  `PARSE_ERROR` branch in `_extract_rust_source_symbols` at all, per §5.)

**JS/TS extraction (4 tests):**
- `..._js_..._is_indexed_partial_with_export_based_exposure` — an
  `export function`, a non-exported function, an `export class`; asserts
  `INDEXED_PARTIAL` and exposure exactly `public` iff `export`-prefixed,
  `internal` otherwise.
- `..._ts_..._supports_interface_type_enum_and_jsdoc` — asserts a JSDoc
  `/** ... */` comment attaches as `purpose` to the following `export
  function`; `interface`/`type`/`enum` are each classified with `kind`
  equal to that literal keyword; a non-exported `type` gets `internal`.
- `test_ts_overload_produces_distinct_rows_never_crashes` — three
  `function foo` signatures (two overload declarations + one
  implementation, TS syntax); asserts 3 rows, 3 distinct lines — same
  shape/limitation note as the Python overload test: this is regex line
  matching, not signature-aware overload resolution; any three same-named
  matching lines would produce three rows.
- `test_js_unreadable_file` — invalid UTF-8; asserts `UNREADABLE`.
  (No JS/TS `PARSE_ERROR` test either, for the same structural reason.)

**Haskell (1 test):**
- `test_haskell_is_unsupported_not_a_silent_empty_result` — a valid,
  trivial `.hs` file; asserts `status == UNSUPPORTED`, `diagnostic is
  None`, `symbols == ()`. This is the one test that directly exercises
  the fall-through branch of `extract_source_symbols_for_file` described
  in §5/§9.

No test in this file touches `graph_schema_fragment.py`'s schema, sync, or
query functions at all — everything in that file is untested *within this
export* (a separate `test_graph.py` is referenced by
`_migrate_source_files_columns`'s own docstring as covering the
migration's nullability contract, but that file is not part of this
export and was not read).

## 9. Limitations (evidence-based, not inferred)

- **Haskell is recognized but never extracted.** `Language.HASKELL` and
  the `.hs` suffix mapping exist, so `discover_source_files` reports `.hs`
  files — but `extract_source_symbols_for_file` has no Haskell branch and
  falls through to `UNSUPPORTED` unconditionally, confirmed by
  `test_haskell_is_unsupported_not_a_silent_empty_result`. Any other
  suffix absent from `_LANGUAGE_BY_SUFFIX` (e.g. `.go`, `.java`, `.rb`,
  `.txt`) is invisible even earlier — `discover_source_files` itself never
  reports it, so it never even reaches `extract_source_symbols_for_file`.
- **Python extraction is top-level only.** `_extract_python_source_symbols`
  iterates `ast.iter_child_nodes(tree)` — direct children of the module
  node only. A function nested inside another function, or a method
  defined inside a class, is never visited or emitted as its own symbol
  (a `ClassDef` itself is captured, but nothing inside its body is
  descended into). No test in this file exercises a nested/method case,
  and the code has no recursive descent into class or function bodies —
  this is a structural limitation of the current code, not just an
  untested edge case.
- **`exposure: 'unknown'` is schema-legal but never produced.** The
  `source_symbols.exposure` `CHECK` constraint allows `'unknown'` as a
  fifth value, but none of the three extractors ever assign it (or
  `None`): Python always emits `public` or `conventional_private`; Rust
  always emits `public`, `restricted`, or `internal`; JS/TS always emits
  `public` or `internal`. `'unknown'` exists in the schema's vocabulary
  with no producing code path in this export.
- **Rust/JS/TS extraction is coarse, single-line, regex-based —
  `INDEXED_PARTIAL`, not `INDEXED`, by design.** Both workers process one
  physical line at a time against a single anchored regex
  (`^(modifier)?\s*(kind)\s+(name)`-shaped). Any declaration whose keyword
  and name don't appear together on one line as the pattern expects (a
  signature split across lines, an unusual formatting style) is silently
  not matched — not reported as any kind of partial failure, since
  `INDEXED_PARTIAL` is the status for the whole file regardless of how
  many individual items the regex actually caught. There is no
  `PARSE_ERROR` outcome for either language at all (no test exercises one,
  and no code path produces one) — a genuinely malformed Rust/JS/TS file
  that still decodes as UTF-8 is simply scanned line-by-line with whatever
  matches; there is no structural validity check to fail.
- **JS/TS "const" declarations are classified by keyword, not by what
  they hold.** `_JS_FAMILY_ITEM_RE` matches `const` as one of its `kind`
  alternatives; a `const` holding an arrow function (e.g. `export const
  foo = () => {}`) is captured — but its `kind` would be recorded as
  `"const"`, not `"function"`, since the regex only captures the leading
  keyword, never inspects the right-hand side. No test in this file
  actually exercises a `const`-arrow-function case, so this is inferred
  directly from the regex definition, not from an observed test result.
- **No glue code between extraction and persistence is present in this
  export.** `source_symbols.py` produces `SourceSymbol`/`SourceFileExtraction`
  objects; `graph_schema_fragment.py`'s `_sync_source_files`/
  `_sync_source_symbols` consume `SourceFileRow`/`SourceSymbolRow` objects
  (a different, though field-compatible, pair of dataclasses — notably,
  `SourceSymbol` itself has no `source_file_path` field, so building a
  `SourceSymbolRow` requires a caller to supply that separately, e.g. from
  the file being processed). No function in this export converts one pair
  into the other, and no function in this export calls
  `discover_source_files`/`extract_source_symbols_for_file` and then
  `_sync_source_files`/`_sync_source_symbols` in sequence. The
  `_migrate_source_files_columns` docstring *names* `sync.py::rebuild_project_graph`
  as the real production call site that wires this together, and
  `source_file_profile`'s docstring *names* `cli.py::query_source` as
  checking `meta.source_index_version` before calling it — but neither
  `sync.py` nor `cli.py` is part of this export, so those two claims are
  reported here only as "the code asserts this exists," not verified.
  This gap is unchanged by the export's correction (it was never about
  the truncation bug) and remains the one genuinely unverifiable link in
  the whole traced runtime path in §5.
- **No test in this export exercises `graph_schema_fragment.py` at all**
  (see §8) — its schema, migration, sync, and query behavior is read
  directly from source only, with no test evidence corroborating any of
  it from this export's contents alone.

---

## Corrected-vs-prior summary

Both specific defects named in the re-dispatch instructions are confirmed
fixed by direct re-reading of the export as it now stands:

1. `SourceSymbolRow` (Block 2, `graph_schema_fragment.py:82-97`) now
   declares all six fields `_sync_source_symbols` (Block 5) reads:
   `source_file_path`, `name`, `kind`, `line`, `purpose`, `exposure`. No
   inconsistency remains between the dataclass and its one real consumer
   in this export.
2. Block 6 (`source_file_profile`/`source_symbol_profile`) ends cleanly at
   line 335, with an explicit header comment stating `doc_code_trace` is
   deliberately excluded in full rather than left dangling. No cut-off
   signature is present.

All other findings from the prior pass — Haskell recognized-but-unsupported,
Python's top-level-only extraction scope, `exposure: 'unknown'` being
schema-legal but never produced, the Rust/JS/TS coarse regex/line-scan
approach and its lack of a `PARSE_ERROR` outcome, and the absence of any
extraction-to-persistence glue code in this export — were re-verified
directly against the corrected files during this pass and remain accurate
as described above.
