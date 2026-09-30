# Coding-context packet: first-party-source-symbols

**Snapshot cited:** `first-party-source-symbols@v2`
(`planning/knowledge/first-party-source-symbols/snapshots/snapshot-v2.toml`).
Originally assembled against `@v1`; re-cited against `@v2` after a
comparison-mode pass added `CL-FPSS-008` (see new bullet below) — no
other content in this packet changed as a result.

**Source discipline (per this session's task instructions, Phase 79
clean-room workflow, `decisions/0066`):** every fact below is drawn only
from the snapshot's cited assertions — the 7 Claim records
(`CL-FPSS-001`–`CL-FPSS-007`), the Evidence records each Claim cites as
`supporting_evidence`, and each Claim's own `derivation` (`DE-FPSS-*`)
record. Nothing here was pulled from `design.md`, an ADR, the
implementation-reconstruction report, `adversarial-review.md`, or a live
read of `src/`.

**Departure from the standard Phase 54c gate, disclosed up front:** the
normal packet-assembly input is "records reachable from `design.md`'s own
`APPROVED` state." No `design.md`, `DEC-`, or `REQ-` record exists yet for
this topic — this pilot's frozen source is the Claim layer directly, per
this session's explicit instructions. Accordingly, "approved semantics"
below is compacted from the Claims at `status: supported`/`status:
verified` in the snapshot, not from an approved design document, and
there is no Decision/Requirement layer to cite for "deliberate upstream
differences" or verbatim Given/When/Then Requirements — both sections
below say so explicitly rather than inventing content to fill the shape.

## Goal

Add support for extracting first-party symbols from a new language the
project doesn't currently support, in a way that is consistent with how
`first-party-source-symbols` already models per-language extraction
fidelity, symbol identity, and status — without silently degrading the
meaning of `SymbolIndexStatus` or the schema's uniqueness guarantee for
existing languages.

## Approved semantics (compacted from supported/verified Claims)

- **`Language` is a separate, narrow concept from `core.Ecosystem`.**
  `Language` (a `StrEnum` defined in `source_symbols.py` itself, not
  `core.py`) exists specifically because `core.Ecosystem` cannot
  distinguish JavaScript from TypeScript (both collapse to one NPM
  package-ecosystem value there), and first-party symbol-kind extraction
  needs that distinction (only TypeScript can declare
  `interface`/`type`). The module never imports or references
  `core.Ecosystem`. [`CL-FPSS-001`]
- **Exposure classification is a strict, per-language subset of a
  five-value vocabulary** (public/restricted/internal/
  conventional_private/unknown), never the full five values from any one
  real extractor. Python: public or conventional_private only. Rust:
  public, restricted, or internal only (never conventional_private).
  JS/TS: public or internal only. `unknown` is a schema-level allowance
  no real extractor ever produces. [`CL-FPSS-002`]
- **`SymbolIndexStatus` has five states, and the
  indexed/indexed_partial split is about technique fidelity, never about
  whether anything was found.** `indexed` = a real structural parser ran
  (Python's `ast.parse`); a file that fails to parse never reaches
  `indexed`, it reaches `parse_error` instead. `indexed_partial` = a
  coarse line-scan/regex heuristic ran (today: Rust, JS, TypeScript) —
  a technique with no real parse step, so it is dispatched
  unconditionally on successful file read regardless of what (if
  anything) is found, and it can **never** fail structurally the way
  `ast.parse` can (so it never returns `parse_error`). `unsupported` =
  no extractor exists for the file's language at all — **Haskell is the
  concrete, current example**: the file is never even opened.
  `unreadable` applies to any language on `OSError`/
  `UnicodeDecodeError`. The language→status mapping is fixed, not
  content-dependent: no code path returns `indexed_partial` for Python
  or `indexed` for Rust/JS/TS. [`CL-FPSS-003`]
- **Symbol identity is occurrence-based, not name-based:**
  `UNIQUE(source_file_id, name, kind, line)` at the schema level, and
  `SourceSymbol.line` is a required `int` (never `None`/optional) in the
  dataclass. This exists specifically because ordinary function
  overloading (`@typing.overload` in Python; repeated signature
  declarations in TypeScript) produces multiple individually-real
  declarations that legitimately share one `(source_file_id, name,
  kind)` triple but occupy distinct lines — a name-only or
  name+kind-only identity key would make the second such declaration
  collide with the first as a uniqueness violation. A real, unmodified
  overloaded Python function (2 `@overload` stubs + 1 implementation)
  and a real overloaded TypeScript function (2 signature-only
  declarations + 1 implementation) each produce exactly 3 rows, same
  name/kind, distinct lines, none dropped. [`CL-FPSS-004`]
- **The coarse (`indexed_partial`) regex technique has a real, narrow,
  reproducible false-positive boundary, not just a documented-in-prose
  risk.** Confirmed *not* to be defeated by: a declaration's parameter
  list spanning multiple physical lines (the regex only needs to match
  the keyword+name text on the line where the declaration's own name
  first appears); a single-line `//` comment or single-line string
  literal containing declaration-like text (both item regexes anchor
  with `^` against each line's own stripped leading content). Confirmed
  to genuinely, silently produce a false-positive `source_symbols` row
  for: a multi-line Rust raw-string literal (`r#"..."#`) whose own
  interior line matches the anchored pattern; a plain `/* ... */` block
  comment in JS/TS (as opposed to a `/**` JSDoc comment, which the
  extractor does specially recognize) — commented-out declarations
  inside are scanned as if they were real code. Both false positives
  leave `status` at `indexed_partial` and `diagnostic` at `None`, with
  nothing in the returned data distinguishing them from genuine
  declarations. [`CL-FPSS-007`, depends on `CL-FPSS-003`]
- **The two existing `indexed_partial`-family extractors (Rust, JS/TS)
  have known, undocumented scope/fidelity gaps a new extractor copying
  their pattern should not silently repeat**: Python's own extractor is
  top-level-only (no descent into class/function bodies — not itself a
  template for this task, but the general lesson applies); and a JS/TS
  `const` binding's `kind` is recorded literally as `"const"` regardless
  of what it's bound to (never inspects the right-hand side), making
  `export const foo = () => {}` schema-indistinguishable from a plain
  constant. Neither gap is mentioned by the ADR/plan — both were found by
  independent code inspection. A new extractor should decide its own
  scope (top-level-only vs. nested) and `kind`-assignment precision
  deliberately, not by uncritically mirroring the existing regex
  extractors' unexamined shortcuts. [`CL-FPSS-008`]

## Requirements

No `REQ-` records exist for this topic in the cited assertions — there
is no Decision/Requirement layer yet, only supported/verified Claims.
The task-relevant, schema-enforced facts a new extractor must satisfy
(the nearest equivalent to a Requirement here) are:

1. Every emitted symbol row's `(name, kind, line)` combination must be
   distinct from every other row this extractor emits for the same
   file — `line` must be a real, populated `int`, never `None` and never
   a placeholder (e.g. `0` or the declaration-block's start line reused
   across an overload set), because `line` is part of the schema's own
   uniqueness key and is the *only* thing that disambiguates two
   legitimately-repeated declarations (`CL-FPSS-004`).
2. The extractor's returned status for a successfully-read file must be
   `SymbolIndexStatus.INDEXED_PARTIAL`, not `INDEXED`, if the technique
   is a line-scan/regex heuristic rather than a real structural parser
   (`CL-FPSS-003`) — see "Answers to the frozen task" below.
3. The extractor's exposure values must come from a fixed, disjoint,
   per-language subset decided for the new language, not the full
   five-value vocabulary and not another language's subset
   (`CL-FPSS-002`).

## Behavioural examples

No `REQ-`-owned Given/When/Then records exist for this topic. The
closest available material is each Claim's own `examples`/
`counterexamples` field, reproduced verbatim below (not reformatted into
Given/When/Then, since the source records themselves aren't in that
shape):

- "a syntactically valid, symbol-free Python file → INDEXED with
  symbols=() (real test)" [`CL-FPSS-003`]
- "a Python file with a genuine SyntaxError → PARSE_ERROR with a
  populated diagnostic and symbols=() (real test)" [`CL-FPSS-003`]
- "a Haskell file, however well-formed, → UNSUPPORTED without ever being
  opened (real test)" [`CL-FPSS-003`]
- "a real @typing.overload-stacked Python `foo` (two @overload stubs +
  one implementation) produces 3 rows named foo, each at a distinct
  line, none dropped (real execution)"; the same for a real overloaded
  TypeScript `foo` [`CL-FPSS-004`]
- "a Rust file containing a multi-line raw string whose interior line
  reads `pub fn embedded_in_string() {}` produces a real, silent
  false-positive `embedded_in_string` row (real probe)"; "a TS file
  containing a plain `/* ... */` block comment around
  `export function commented_out(): void {}` produces a real, silent
  false-positive `commented_out` row (real probe)" [`CL-FPSS-007`]
- counterexamples (do **not** trigger a false positive): "a genuinely
  multi-line function signature is handled correctly"; "a single-line
  comment or string containing declaration-like text is handled
  correctly" [`CL-FPSS-007`]

## Invariants

- `SourceSymbol.line` is a required `int` in every emitted row — never
  optional, never `None` (`CL-FPSS-004`).
- `(source_file_id, name, kind, line)` must be unique per file at the
  schema level; the graph-layer sync computes existing/incoming sets as
  4-tuples and upserts on that same key (`CL-FPSS-004`, citing
  `EV-FPSS-012`/`EV-FPSS-017`).
- A given language's `SymbolIndexStatus` outcomes are fixed per
  extraction technique, not content-dependent: a regex/line-scan
  extractor must never return `INDEXED` (reserved for a real structural
  parse) and can never legitimately return `PARSE_ERROR` (there is no
  parse step to fail) — its only two reachable outcomes are
  `INDEXED_PARTIAL` (successful read) and `UNREADABLE` (read failure)
  (`CL-FPSS-003`).
- Exposure values emitted must stay within whatever fixed, disjoint
  subset of the five-value vocabulary is decided for the new language —
  never `unknown` in practice unless that value is deliberately reserved
  the same way the existing three extractors reserve it (unreachable
  from real code) (`CL-FPSS-002`).

## Relevant architecture (pointers only)

- `Language` / `SymbolIndexStatus` enums and the per-language dispatch
  logic live in `source_symbols.py`, separate from `core.py`'s
  `Ecosystem` enum — these are two deliberately unrelated concepts, not
  interchangeable (`CL-FPSS-001`).
- The schema-level uniqueness constraint and the sync/upsert logic that
  enforces it live at the graph layer (`graph_schema_fragment.py` per
  the cited evidence; the real module is `graph.py`), downstream of
  whatever `source_symbols.py` extraction produces (`CL-FPSS-004`,
  `EV-FPSS-012`, `EV-FPSS-017`).

## Relevant symbols/files/dependencies

- `Language(StrEnum)` — 5 members today: `PYTHON`, `RUST`, `JAVASCRIPT`,
  `TYPESCRIPT`, `HASKELL` (values: "python"/"rust"/"javascript"/
  "typescript"/"haskell"). **Haskell already has a `Language` member but
  no extractor** — it is the concrete, currently-real instance of "a
  language the project doesn't support yet" (`CL-FPSS-001`,
  `EV-FPSS-002`, `CL-FPSS-003`).
- `SymbolIndexStatus(StrEnum)` — 5 members: `INDEXED`, `INDEXED_PARTIAL`,
  `UNSUPPORTED`, `PARSE_ERROR`, `UNREADABLE` (`EV-FPSS-006`).
- `_extract_python_source_symbols` — the one extractor function named
  explicitly in the cited evidence; uses real `ast.parse`; returns
  `INDEXED`/`PARSE_ERROR`/`UNREADABLE`; **never** returns
  `INDEXED_PARTIAL` (`EV-FPSS-006`).
- The Rust extractor (matches items via a module-level `_RUST_ITEM_RE`
  regex, anchored with `^` per stripped line) and the JS/TS extractor
  (matches items via a module-level `_JS_FAMILY_ITEM_RE` regex, same
  anchoring, one function apparently serving both JavaScript and
  TypeScript given the shared "JS_FAMILY" regex name) — both return
  `INDEXED_PARTIAL`/`UNREADABLE` only, never `INDEXED`/`PARSE_ERROR`
  (`EV-FPSS-006`, `EV-FPSS-008`, `EV-FPSS-009`). **The cited evidence
  names these two regex constants but does not give the enclosing
  functions' own literal identifiers** — see "Unresolved questions."
- `SourceSymbol` dataclass — `line` is a required `int` field, never
  `Optional[int]` (`CL-FPSS-004`).
- `SourceSymbolRow` (graph layer) — six fields:
  `source_file_path, name, kind, line, purpose, exposure`
  (`EV-FPSS-017`).
- `source_symbols` table — `UNIQUE(source_file_id, name, kind, line)`,
  `line INTEGER NOT NULL` (`EV-FPSS-012`, `EV-FPSS-017`).
- `_sync_source_symbols` — upserts via
  `INSERT ... ON CONFLICT(source_file_id, name, kind, line) DO UPDATE`,
  computing existing/incoming sets as 4-tuples (`EV-FPSS-012`).

## Existing tests

- `tests/test_source_symbols.py` — 17 tests, cited as covering: one test
  per `SymbolIndexStatus` state, the full per-language exposure mapping
  (including `test_rust_extraction_is_indexed_partial_with_full_exposure_model`,
  asserting all three `pub(...)` forms map to `restricted`), and the
  Python/TypeScript overload-identity cases
  (`EV-FPSS-005`, `EV-FPSS-020`). A new-language extractor should follow
  this file's own existing per-state/per-exposure/per-identity test
  shape rather than inventing a new one.

## Non-goals

- Replacing or converging `Language` with `core.Ecosystem` — they are
  deliberately separate concepts for a stated reason (`CL-FPSS-001`);
  do not "simplify" by reusing `Ecosystem`.
- Producing `exposure='unknown'` from a real extraction path — every
  existing real extractor treats this value as unreachable
  (`CL-FPSS-002`); a new extractor should either also treat it as
  unreachable or explicitly justify why it differs.
- Achieving real-parser (`INDEXED`) fidelity from a first, coarse
  implementation — a naive first implementation is expected to be
  `INDEXED_PARTIAL`, and silently mislabeling it `INDEXED` would
  misrepresent technique fidelity the existing model deliberately
  distinguishes (`CL-FPSS-003`).

## Deliberate upstream differences

None available — no `DEC-` records exist for this topic in the cited
assertions, and none of the seven Claims describe a chosen deviation
from an external upstream (this is an internal CodeCompass subsystem,
not a compatibility-with-an-external-tool feature). Not applicable here,
stated rather than omitted silently.

## Unresolved questions (honestly disclosed)

- **Exact function identifiers for the Rust and JS/TS extractors are not
  in the cited evidence.** `EV-FPSS-006`/`EV-FPSS-008`/`EV-FPSS-009` name
  the regex constants (`_RUST_ITEM_RE`, `_JS_FAMILY_ITEM_RE`) and
  describe each function's behaviour precisely, but no cited record
  gives the enclosing function's own name the way `EV-FPSS-006` names
  `_extract_python_source_symbols` for Python. A coding agent using this
  packet will need to locate the actual function by its documented
  behaviour (dispatches unconditionally on read success, returns
  `INDEXED_PARTIAL`/`UNREADABLE` only, uses the named regex anchored to
  line-start) rather than by name alone.
- **Whether "a new language" should mean wiring up Haskell specifically
  (already a `Language` member, currently `UNSUPPORTED`) or adding a
  sixth `Language` member for a language not yet enumerated at all** is
  not resolved by the cited Claims — both are consistent with the
  frozen task wording. `CL-FPSS-003` makes Haskell the concrete,
  already-real instance of "a language the project doesn't support
  yet," so this packet treats that as the primary, best-evidenced
  reading, while noting that a genuinely new `Language` member would
  additionally need to follow `CL-FPSS-001`'s pattern (a new StrEnum
  value, kept independent of `core.Ecosystem`).
- `CL-FPSS-007` itself records an open question about whether its two
  reproduced false-positive shapes (multi-line raw string, plain block
  comment) are the only ones, or merely two of possibly several
  unenumerated ones — a new coarse extractor for another language should
  expect its own, not-yet-discovered analogues of this same class of
  boundary case, not assume these two are exhaustive.

## What was deliberately left out, and why

- **`CL-FPSS-005`** (`meta.source_index_version` project-level marker
  semantics) — excluded. It concerns project-level "has this project
  ever been indexed under Phase-77-aware code" bookkeeping in
  `rebuild_deterministic`/`cli.py`, not per-file extraction mechanics;
  adding one new language's extractor does not touch this marker's write
  or gate paths.
- **`CL-FPSS-006`** (nullable-everywhere migration contract for
  `source_files`'s four Phase-77 columns) — excluded. It concerns
  schema-migration mechanics for columns that already exist
  (`language`, `content_hash`, `symbol_index_status`,
  `symbol_index_diagnostic`); adding a new language's extraction logic
  reuses these existing, already-nullable columns and requires no new
  column or migration.
- **`CL-FPSS-002`'s full per-language exposure enumeration detail**
  (e.g. the exact eight Rust `pub(...)` sub-forms) — compacted to "a
  fixed, disjoint per-language subset" rather than reproduced in full;
  the task needs the *shape* of the rule (pick a disjoint subset for the
  new language) more than the Rust-specific enumeration, which is
  available in `CL-FPSS-002`/`EV-FPSS-003`/`EV-FPSS-004` directly if
  needed.
- Raw Observation-level detail, the full research narrative in each
  Derivation's `method` field, and `CL-FPSS-001`/`CL-FPSS-004`/
  `CL-FPSS-005`'s own internal `open_questions` about `core.Ecosystem`'s
  and `graph.py`'s real content (since closed by later evidence,
  `EV-FPSS-016`/`EV-FPSS-017`, already folded into the compacted
  semantics above rather than left as live doubt).

## Answers to the frozen coding-context task

1. **Which existing extractor function is the right template to copy?**
   One of the two coarse, regex/line-scan extractors — the Rust
   extractor (`_RUST_ITEM_RE`) or the JS/TS extractor
   (`_JS_FAMILY_ITEM_RE`) — **not** `_extract_python_source_symbols`.
   The Python extractor is `ast.parse`-based (real structural parsing);
   a "naive/coarse first implementation" for a new language matches the
   Rust/JS-TS technique family (unconditional dispatch on successful
   read, anchored-regex line matching, no real parse step to fail)
   (`CL-FPSS-003`, `CL-FPSS-007`).
2. **What `SymbolIndexStatus` value should a naive/coarse first
   implementation use?** `SymbolIndexStatus.INDEXED_PARTIAL` on
   successful read (with `UNREADABLE` on `OSError`/
   `UnicodeDecodeError`) — never `INDEXED` (reserved for real structural
   parsing) and never `PARSE_ERROR` (there is no parse step for this
   technique to fail) (`CL-FPSS-003`).
3. **What is the minimum schema-relevant fact that must be true of every
   symbol row this new extractor produces?** Every row's
   `(source_file_id, name, kind, line)` 4-tuple must be unique within
   the file, and `line` must be a real, populated `int` — never `None`
   — because `line` is the only field that disambiguates multiple
   legitimately-repeated declarations (e.g. overloads) sharing the same
   `name`/`kind` (`CL-FPSS-004`).

## Provenance references

`CL-FPSS-001`, `CL-FPSS-002`, `CL-FPSS-003`, `CL-FPSS-004`,
`CL-FPSS-007`, `CL-FPSS-008`, `DE-FPSS-001`, `DE-FPSS-002`, `DE-FPSS-003`,
`DE-FPSS-004`, `DE-FPSS-007`, `DE-FPSS-008`, `EV-FPSS-001`, `EV-FPSS-002`,
`EV-FPSS-003`, `EV-FPSS-004`, `EV-FPSS-005`, `EV-FPSS-006`,
`EV-FPSS-007`, `EV-FPSS-008`, `EV-FPSS-009`, `EV-FPSS-010`,
`EV-FPSS-011`, `EV-FPSS-012`, `EV-FPSS-016`, `EV-FPSS-017`,
`EV-FPSS-020`, `EV-FPSS-021`, `EV-FPSS-022`, `EV-FPSS-023`.

Not cited (deliberately excluded, see above):
`CL-FPSS-005`, `CL-FPSS-006`, `DE-FPSS-005`, `DE-FPSS-006`,
`EV-FPSS-013`, `EV-FPSS-014`, `EV-FPSS-015`, `EV-FPSS-018`,
`EV-FPSS-019`.
