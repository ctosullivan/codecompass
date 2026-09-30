# First-Party Source Symbols

## Documentation architecture for this page

This page is written as a single Diátaxis-style **explanation** document
(not a tutorial, not a how-to, not an exhaustive reference), because
every assertion available for this topic is either a *definition*, an
*invariant/rule*, or a *boundary* on fidelity — there is no step-by-step
task to walk through and no exhaustive parameter list to enumerate.
Within that explanation, the internal structure mirrors the
`assertion_kind` values the knowledge base itself already assigns, rather
than a generic "Overview / Usage / Reference" template that would force
an artificial task-oriented framing onto what is really a set of design
decisions and their consequences:

- **Definitions** (§2) — the three per-file/per-symbol vocabularies
  introduced for this feature (`Language`, exposure, `SymbolIndexStatus`).
- **Invariants** (§3) — the two properties the system is designed to hold
  unconditionally (symbol identity under overloading; the project-level
  "never indexed" marker).
- **Supporting contract** (§4) — the schema/migration rule that makes the
  invariants and definitions above safe to introduce into an existing
  database.
- **Known limitations** (§5) — boundaries on how far the above can be
  trusted, stated plainly rather than folded quietly into the
  definitions, because a reader deciding whether to rely on first-party
  symbol data needs these as prominently as the definitions themselves.
- **Open questions** (§6) — points the knowledge base itself flags as
  unresolved, carried forward rather than silently dropped.

Every substantive sentence below cites the specific claim it traces to,
as `first-party-source-symbols@v2#CL-FPSS-00N`. Sentences describing
*design intent* (what a decision was meant to achieve) are distinguished
from sentences describing *confirmed behaviour* (what the code actually
does) wherever the underlying claim itself draws that distinction.

## 1. What this concept is, and why it exists

"First-party source symbols" is CodeCompass's model of the
declarations (functions, classes, interfaces, types, enums, consts, and
similar) that appear in a project's own source files, as distinct from
its dependencies. The feature introduces its own narrow vocabulary
rather than reusing CodeCompass's pre-existing `core.Ecosystem` concept,
because `core.Ecosystem` is a *package-ecosystem* concept that cannot
distinguish JavaScript from TypeScript (both collapse to a single NPM
value), while symbol-kind extraction genuinely needs that distinction —
only TypeScript source can declare `interface`/`type` constructs
(`first-party-source-symbols@v2#CL-FPSS-001`). Extraction is supported,
at varying levels of technique fidelity, for five languages: Python,
Rust, JavaScript, TypeScript, and Haskell — though Haskell has no real
extractor at all today (`first-party-source-symbols@v2#CL-FPSS-001`,
`first-party-source-symbols@v2#CL-FPSS-003`).

## 2. Definitions

### 2.1 Language

`Language` is a new, five-value enumeration
(`python`/`rust`/`javascript`/`typescript`/`haskell`) defined in
`source_symbols.py` itself, not in `core.py`, and is not imported by nor
referenced from `core.Ecosystem` in either direction
(`first-party-source-symbols@v2#CL-FPSS-001`). It exists specifically to
carry the one distinction `core.Ecosystem` cannot: a `.ts` file
classifies as `Language.TYPESCRIPT` and is eligible to be scanned for
`interface`/`type` constructs, while a `.js` file classifies as
`Language.JAVASCRIPT` and is scanned by the same regex machinery but can
never match those two keywords in practice, since JavaScript has no such
syntax (`first-party-source-symbols@v2#CL-FPSS-001`).

### 2.2 Exposure

Exposure classification uses a five-value vocabulary —
`public`/`restricted`/`internal`/`conventional_private`/`unknown` — but
no single language's real extractor ever produces all five; each
language uses a strict, disjoint subset
(`first-party-source-symbols@v2#CL-FPSS-002`):

- **Python** produces only `public` (no leading underscore) or
  `conventional_private` (leading underscore) — e.g. `def public_fn():
  ...` classifies as `public`, `def _private_fn(): ...` classifies as
  `conventional_private` (`first-party-source-symbols@v2#CL-FPSS-002`).
- **Rust** produces `public` (bare `pub`), `restricted` (any
  `pub(crate)`/`pub(super)`/`pub(in path)`/`pub(self)` form), or
  `internal` (no modifier) — e.g. `pub fn foo() {}` is `public`,
  `pub(crate) fn bar() {}` is `restricted`, `fn internal_fn() {}` is
  `internal` (`first-party-source-symbols@v2#CL-FPSS-002`).
- **JavaScript/TypeScript** produce only `public` (leading `export`
  present, e.g. `export function add(...) {}`) or `internal` (absent,
  e.g. `function internalHelper() {}`)
  (`first-party-source-symbols@v2#CL-FPSS-002`).
- **`unknown`** is never produced by any of the three real extractors
  this module ships; it exists purely as a schema-level vocabulary
  allowance for a hypothetical future, less-certain extractor
  (`first-party-source-symbols@v2#CL-FPSS-002`).

`conventional_private` is deliberately distinct from `internal`: the
former names a naming *convention* a caller can freely ignore, the
latter names a language-enforced non-visibility default. Python's
leading-underscore convention is therefore never classified as
`internal` (`first-party-source-symbols@v2#CL-FPSS-002`).

### 2.3 SymbolIndexStatus

Every source file's extraction attempt records one of five statuses —
`indexed`, `indexed_partial`, `unsupported`, `parse_error`,
`unreadable` — so that an empty symbols list can never ambiguously stand
in for more than one real cause
(`first-party-source-symbols@v2#CL-FPSS-003`):

- **`indexed`** means a real structural parser (Python's `ast.parse`)
  ran and succeeded, whether or not it found any symbols; the extractor
  never reaches this status if parsing itself failed
  (`first-party-source-symbols@v2#CL-FPSS-003`).
- **`indexed_partial`** means a coarse line-scan/regex heuristic ran
  (Rust, JavaScript, TypeScript) — a technique with no real parse step,
  so it cannot fail structurally the way `ast.parse` can, and is
  dispatched unconditionally on a successful file read regardless of
  what, if anything, it finds
  (`first-party-source-symbols@v2#CL-FPSS-003`).
- **`unsupported`** means no extractor exists for the file's language at
  all (Haskell, as of this snapshot) — the file is never even opened
  (`first-party-source-symbols@v2#CL-FPSS-003`).
- **`parse_error`** is Python-specific (`ast.parse` raising
  `SyntaxError`), since Rust/JS/TS have no real parse step to fail
  (`first-party-source-symbols@v2#CL-FPSS-003`).
- **`unreadable`** applies to any language on `OSError` or
  `UnicodeDecodeError` while reading the file
  (`first-party-source-symbols@v2#CL-FPSS-003`).

The mapping from language to `indexed` vs. `indexed_partial` is fixed by
which technique that language's extractor uses, never content-dependent:
no code path returns `indexed_partial` for Python or `indexed` for
Rust/JS/TS (`first-party-source-symbols@v2#CL-FPSS-003`). For example, a
syntactically valid but symbol-free Python file is `indexed` with an
empty symbol list; a Python file with a genuine `SyntaxError` is
`parse_error` with a populated diagnostic and an empty symbol list; a
Haskell file, however well-formed, is `unsupported` without ever being
opened (`first-party-source-symbols@v2#CL-FPSS-003`).

## 3. Invariants

### 3.1 Occurrence-based symbol identity

Symbol identity is keyed on `(source_file_id, name, kind, line)`, with
`line` a required (never-`None`) integer, rather than on name (or
name+kind) alone
(`first-party-source-symbols@v2#CL-FPSS-004`). This exists to handle
ordinary function overloading — a real, common feature in both Python
(via `@typing.overload`) and TypeScript (via repeated signature
declarations) — where multiple declarations legitimately share one
`(source_file_id, name, kind)` triple but occupy distinct lines
(`first-party-source-symbols@v2#CL-FPSS-004`). A name-only identity key
would make the second such declaration collide with the first as a
uniqueness violation the moment a real project containing an overload
was synced; overloads are multiple *individually real* declarations, not
duplicate facts about one logical symbol, so an identity scheme able to
keep only one of them — whether by rejecting the insert or by silently
merging/overwriting — would discard information a caller inspecting a
specific line deserves an accurate answer about
(`first-party-source-symbols@v2#CL-FPSS-004`). Concretely, a real
`@typing.overload`-stacked Python function (two `@overload` stubs plus
one implementation) produces three rows sharing one name, each at a
distinct line, none dropped; the same holds for an overloaded TypeScript
function (`first-party-source-symbols@v2#CL-FPSS-004`).

### 3.2 The project-level "never indexed" marker

`meta.source_index_version`'s *absence* as a key (not a `NULL` value —
its total absence) is meant to mean "first-party source has never been
indexed under Phase-77-aware code," a state distinct from any per-file
`SymbolIndexStatus` value, and is meant to be written unconditionally on
every Phase-77-aware rebuild — even one that finds zero first-party
files — so that a genuine "not yet indexed" project state is never
confused with a genuine "indexed, but this symbol doesn't exist"
negative result (`first-party-source-symbols@v2#CL-FPSS-005`). This
started, in this knowledge base, as documented *design intent* only,
drawn from an ADR's "Decision" section and a plan's own "new, this
amendment" section, with no confirmed implementation in scope at the
time; a later review with full repository access confirmed the intent
is in fact implemented exactly as described: the sync path
unconditionally passes a version marker into the rebuild function, the
graph-writing path writes it whenever non-`None`, and the CLI's read
path gates on the key's absence before reading first-party file/symbol
data — including the "written even with zero first-party files" detail
(`first-party-source-symbols@v2#CL-FPSS-005`).

## 4. Supporting contract: adding this data to an existing database

The migration that adds first-party symbol support to `source_files`
(four new columns: language, content hash, index status, index
diagnostic) is nullable-everywhere, not "`NOT NULL` once populated":
each column is added via its own `ALTER TABLE ... ADD COLUMN` with no
`NOT NULL` constraint and no `DEFAULT`, gated by an introspection check
so only genuinely-missing columns are added — an idempotent, rerun-safe
design (`first-party-source-symbols@v2#CL-FPSS-006`). It never drops or
recreates `source_files`, specifically because `source_files.id` is
referenced elsewhere with `ON DELETE CASCADE`, and a drop/recreate would
cascade-delete dependent rows; the same four columns are declared
identically (all nullable, no `NOT NULL`) in the `CREATE TABLE` used for
a brand-new database, so a fresh and a migrated database end up with
identical column definitions
(`first-party-source-symbols@v2#CL-FPSS-006`). This fresh-vs-migrated
equivalence, and the migration's own safety, are independently confirmed
by a real, passing test suite, not merely asserted by the design
documentation that describes the migration's rationale
(`first-party-source-symbols@v2#CL-FPSS-006`).

## 5. Known limitations and fidelity boundaries

These limitations matter to anyone deciding how much to trust
first-party symbol data programmatically; they are stated here with the
same prominence as the definitions above rather than left as fine print.

### 5.1 `indexed_partial` extractors can produce silent false positives

The coarse, regex-based techniques behind `indexed_partial` (Rust,
JavaScript, TypeScript) are reproducibly defeatable, but in a narrower
and more specific way than a general warning about "unusual formatting"
might suggest (`first-party-source-symbols@v2#CL-FPSS-007`):

- A parameter list spanning multiple physical lines does **not**, by
  itself, defeat either extractor, because both regexes only need to
  match the keyword+name text on the line where a declaration's own name
  first appears (`first-party-source-symbols@v2#CL-FPSS-007`).
- A single-line `//` comment or single-line string literal containing
  declaration-like text does **not** produce a false match, because both
  item regexes anchor against each line's own stripped leading content
  (`first-party-source-symbols@v2#CL-FPSS-007`).
- A multi-line Rust raw-string literal whose interior line matches the
  anchored pattern **does** produce a genuine false-positive
  `source_symbols` row — e.g. a raw string embedding
  `pub fn embedded_in_string() {}` on its own line
  (`first-party-source-symbols@v2#CL-FPSS-007`).
- A plain `/* ... */` block comment in JS/TS — as opposed to a `/**`
  JSDoc comment, which is specially recognized — is not treated as a
  comment at all, so a commented-out declaration inside one **does**
  produce a genuine false-positive row
  (`first-party-source-symbols@v2#CL-FPSS-007`).

Both real false-positive shapes are silent: status stays
`indexed_partial`, the diagnostic stays unset, and nothing in the
returned extraction result distinguishes them from genuine declarations
(`first-party-source-symbols@v2#CL-FPSS-007`).

### 5.2 Structural scope limitations

Two further limitations exist independent of the false-positive boundary
above, affecting what is extracted at all rather than what is
misclassified (`first-party-source-symbols@v2#CL-FPSS-008`):

- **Python extraction is top-level-only.** Only the module's own direct
  children are visited, with no recursive descent into a class's or
  function's own body — so a method defined inside a class, or a
  function nested inside another function, is never visited and never
  emitted as its own symbol row
  (`first-party-source-symbols@v2#CL-FPSS-008`).
- **A JS/TS `const` binding's kind is always recorded literally as
  `"const"`, never `"function"`,** regardless of what it is bound to,
  because the extractor assigns kind directly from the matched keyword
  with no inspection of the right-hand side of an `=`. `export const
  useWidget = () => {}` is therefore schema-indistinguishable from
  `export const PI = 3.14`
  (`first-party-source-symbols@v2#CL-FPSS-008`).

Neither limitation is an untested edge case; both are structural
properties of how the extractors are built
(`first-party-source-symbols@v2#CL-FPSS-008`).

## 6. Open questions carried forward

- Whether `meta.git_topology_status` — the precedent
  `source_index_version`'s design is explicitly modeled on — actually
  behaves the way its own design assumes has not been checked as part of
  this topic (`first-party-source-symbols@v2#CL-FPSS-005`).
- Whether the two reproduced `indexed_partial` false-positive shapes
  (multi-line raw strings, plain block comments) are the exact ones the
  original design rationale intended to describe, or merely two of
  possibly several unenumerated ones, is unresolved
  (`first-party-source-symbols@v2#CL-FPSS-007`).
