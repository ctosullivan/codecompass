# Documentation verification: first-party-source-symbols

Frozen per `codecompass-template`'s `documentation-verification/TEMPLATE.md`
shape. Questions written now, **before** the topic's documentation is
published, so the fresh Q&A dispatch's answers can't be shaped by having
watched the doc get written.

## Documentation-only Q&A — frozen questions

1. What is `Language`, and why is it a separate concept from the
   pre-existing `core.Ecosystem`?
2. What are the five possible values of `symbol_index_status`, and what
   is the practical difference between `indexed` and `indexed_partial`?
3. What are the five possible values of a first-party symbol's
   `exposure`, and give one real example of each that the documentation
   cites.
4. A function is declared twice in the same file via `@overload`. Does
   this project's first-party symbol tracking record one row or two for
   it? Why?
5. If `meta.source_index_version` has never been set for a project, what
   does that mean, and how would a caller find out?
6. Name one thing this subsystem is documented as NOT handling (a
   limitation), and what actually happens when that case is hit.

## Coding-context task — frozen scope

**Task**: "Add support for extracting first-party symbols from a new
language the project doesn't currently support." Using only a
coding-context packet generated from this topic's frozen snapshot (not
the full documentation, not the source code directly), identify: which
existing extractor function is the right template to copy, what the
`SymbolIndexStatus` value should be set to for a naive/coarse first
implementation, and what the minimum schema-relevant fact is that must be
true of every symbol row this new extractor produces.

## Results

Independent verification performed directly against `src/codecompass/
source_symbols.py`, `src/codecompass/graph.py`, `src/codecompass/cli.py`,
`src/codecompass/core.py`, `tests/test_source_symbols.py`, and
`tests/test_graph.py` at the current working-tree commit — never by
running `codecompass query`/`check` against the doc-derived answers
themselves. Per §5's rule, this is a real accuracy check, not a
formality.

### 1. `Language` vs `core.Ecosystem` — **WRONG**

The fresh answer states: *"`Language` is separate from `core.Ecosystem`
because `core.Ecosystem` has only one value (`NPM`) covering both
JavaScript and TypeScript identically."*

`src/codecompass/core.py:13-19` shows `Ecosystem` actually has **four**
values:

```python
class Ecosystem(StrEnum):
    NPM = "npm"
    PYTHON = "python"
    CARGO = "cargo"
    HASKELL = "haskell"
```

`architecture/core-data-model.md:19-21` independently confirms the same
four-value enum, so this isn't a case of two docs disagreeing — it's the
real source code and a *second* architecture doc both contradicting this
answer. The truthful claim (`Ecosystem.NPM`, one of the enum's four
values, covers both JS and TS dependencies identically) is correct and
is exactly why `Language` needed to exist as a separate, finer-grained
concept — but "`core.Ecosystem` has only one value" is a factually wrong
statement about the enum's actual size, stated with full confidence.

**This is not the fresh dispatch's own inference error** — it is a
verbatim documentation defect. `architecture/overview.md:845` itself
reads: *"`core.Ecosystem` has one value (`NPM`) covering both JavaScript
and TypeScript dependencies identically."* The fresh agent faithfully
relayed what the published doc says; the doc itself is wrong. This
should be corrected in `architecture/overview.md` (e.g. "of
`core.Ecosystem`'s four values, `NPM` covers both..." or "`core.
Ecosystem.NPM` covers...").

### 2. Five `symbol_index_status` values — **CONFIRMED**

`SymbolIndexStatus` (`source_symbols.py:66-79`) has exactly the five
named values: `INDEXED`, `INDEXED_PARTIAL`, `UNSUPPORTED`, `PARSE_ERROR`,
`UNREADABLE`. Dispatch in `extract_source_symbols_for_file`
(`source_symbols.py:172-185`) confirms the practical split exactly as
claimed: Python goes through `_extract_python_source_symbols`, which
calls `ast.parse` (a real structural parser) and always returns
`INDEXED` on success; Rust and JS/TS go through
`_extract_rust_source_symbols`/`_extract_js_family_source_symbols`,
both plain line-by-line regex scans, both always returning
`INDEXED_PARTIAL` on success. Matches the enum's own docstring verbatim.

### 3. Five `exposure` values with per-language examples — **CONFIRMED**

Verified against each extractor directly:
- Rust (`_extract_rust_source_symbols`, `source_symbols.py:221-254`):
  `modifier is None` → `"internal"`; `modifier.strip() == "pub"` →
  `"public"`; any other modifier text (covers `pub(crate)`, `pub(super)`,
  `pub(self)`, `pub(in path)`) → `"restricted"`. Exactly matches the
  claimed `pub`→public, `pub(crate)`→restricted, no-modifier→internal
  examples.
- JS/TS (`_extract_js_family_source_symbols`, `source_symbols.py:
  257-293`): `exposure = "public" if exported else "internal"` — no
  leading `export` keyword → `"internal"`, matching the claim.
- Python (`_extract_python_source_symbols`, `source_symbols.py:
  188-218`): `"conventional_private" if node.name.startswith("_") else
  "public"` — matches the claim exactly.
- `"unknown"` as a literal stored value: confirmed **never produced** by
  any extractor — grepped all of `source_symbols.py` for the string and
  found no assignment. It appears only (a) in the schema's `CHECK`
  constraint as one of five allowed values
  (`graph.py:101-105`) and (b) as a CLI *display*-time fallback for a
  `NULL` column value (`cli.py::_render_exposure`, `_render_symbol_index_
  status`) — never as a value an extractor writes to the database. The
  claim is accurate on this specific point.

### 4. `@overload` twice → two rows, keyed `(source_file_id, name, kind, line)` — **CONFIRMED**

`source_symbols` schema (`graph.py`, near the `CREATE TABLE
source_symbols` block) has `UNIQUE (source_file_id, name, kind, line)`
with `line INTEGER NOT NULL`, exactly as claimed. The Python extractor
(`_extract_python_source_symbols`) does not inspect decorators at all —
it emits one `SourceSymbol` per top-level `FunctionDef`/
`AsyncFunctionDef`/`ClassDef` node regardless of `@overload`, keyed by
its own `lineno`. Two same-named top-level function declarations at two
distinct lines therefore produce two distinct rows under this key, with
no collision. Directly verified by two existing tests:
- `tests/test_source_symbols.py::
  test_python_overload_produces_distinct_rows_never_crashes` — three
  same-named top-level defs (two `@overload` stubs + one real
  implementation) produce three rows at three distinct lines (the
  general case this project actually exercises; a literal
  "declared-twice" case with no implementation follows the identical
  mechanism and would produce exactly two).
- `tests/test_graph.py::
  test_source_symbols_occurrence_identity_handles_overload_without_
  collision` — three `SourceSymbolRow`s sharing `name="foo"` at three
  distinct lines are written via `rebuild_deterministic` with no
  `sqlite3.IntegrityError`, confirming the schema-level key matches the
  claim.

### 5. `meta.source_index_version` absence and the `cli.py` read path — **CONFIRMED**

`cli.py::query_source` (line ~1094) and `cli.py::query_source_symbol`
(line ~1157) both open the graph and immediately check
`graph.get_meta(conn, "source_index_version") is None`; if so, they
close the connection and print/return the explicit "not indexed yet, run
`codecompass sync`" message (`_render_source_not_indexed`) without ever
calling `graph.source_file_profile`/`graph.source_symbol_profile`, let
alone any sync/rebuild function. Both commands are read-only past that
check — no rebuild is invoked on this path, exactly as claimed.
`meta.source_index_version` is written only inside
`graph.rebuild_deterministic` when a caller (`sync.py`) explicitly
supplies `source_index_version`; verified by
`tests/test_graph.py::test_source_index_version_absent_until_explicitly_
supplied`, which shows the key is absent after a rebuild that omits the
parameter and present only once supplied.

### 6. Multi-line Rust raw-string false positive — **CONFIRMED**

Hand-traced `_RUST_ITEM_RE` (`source_symbols.py:99-102`) against a
constructed example:

```rust
fn real_one() {}
let s = r#"
pub fn not_real() {
"#;
fn another() {}
```

`_extract_rust_source_symbols` scans line-by-line with no lexical
awareness of raw-string delimiters (`r#"..."#`) — it only tracks `///`
doc-comment accumulation, nothing else. Line 3 (`pub fn not_real() {`,
the raw string's interior) matches `_RUST_ITEM_RE` and produces a
genuine `SourceSymbol(name="not_real", kind="fn", exposure="public",
line=3)` despite being inside a string literal, not real Rust source.
The whole-file extractor unconditionally returns
`status=SymbolIndexStatus.INDEXED_PARTIAL, diagnostic=None` regardless of
any interior false match (there is no per-row validity flag), so the
false-positive row is genuinely silent — `symbol_index_status` stays
`indexed_partial`, `symbol_index_diagnostic` stays `NULL`, matching the
claim exactly. This also matches `architecture/context-graph-schema.md`
lines 259-262 word-for-word (same limitation, same example construct),
so this claim is doubly confirmed: by direct code trace and by the
published doc being right on this specific point.

### Summary

| # | Verdict |
|---|---|
| 1 | **WRONG** — `core.Ecosystem` has 4 values, not 1; defect traces to `architecture/overview.md:845` itself |
| 2 | CONFIRMED |
| 3 | CONFIRMED |
| 4 | CONFIRMED |
| 5 | CONFIRMED |
| 6 | CONFIRMED |

5 of 6 answers are fully accurate against the live system. Answer 1 is
confidently wrong on a checkable, concrete fact (the size of an enum)
and the error did not originate with the fresh Q&A dispatch — it is
present verbatim in the published `architecture/overview.md:845` text
the dispatch was restricted to. Recommend correcting
`architecture/overview.md`'s "First-party source awareness" section
(the sentence beginning "`core.Ecosystem` has one value (`NPM`)...") to
state that `NPM` is one of `Ecosystem`'s several values, not that the
enum itself has only one value. No other documentation defect was found
in the sections covering these six questions.
