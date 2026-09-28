# Phase 77: First-party source awareness + `codecompass-template` — plan

**Status:** planned (2026-09-28, amended 2026-09-28).

Direct user request, two connected goals: (1) make a project's own
first-party source (files + top-level implementation symbols) a
first-class, non-vendor-gated object in `context-graph.db`, closing the
structural gap `CG-009` documents; (2) **deliver a genuinely usable,
MIT-licensed `codecompass-template` repository** — the repository
already exists at `https://github.com/ctosullivan/codecompass-template`
(confirmed empty, §0) — packaging the proven downstream-adoption
workflow shape without inheriting CodeCompass's own GPL implementation
or internal governance corpus. Planning only — no `src/` change, no
external-repository population, per explicit instruction for *this*
amendment pass; implementation (including populating the real template
repository) is the next, not-yet-started step.

**Amendment note (2026-09-28, same day as the initial plan `585f891`):**
this amendment corrects twelve issues a direct user review found:
(1) the template repository already exists and Phase 77 must deliver a
usable populated version of it, not merely a design; (2) `source_files`
needs a first-party **language** concept, not a reused **package-
ecosystem** concept — `core.Ecosystem`'s single `npm` value cannot
distinguish JavaScript from TypeScript, which first-party symbol
extraction genuinely needs to; (3) the nullable-vs-`NOT NULL` column
contract must be identical between a fresh and an upgraded database —
not "`NOT NULL` for new, nullable-until-repopulated for old"; (4)
first-party symbol scope must cover implementation, not just an API
surface — non-exported/private top-level declarations included, with
visibility recorded as a separate property, not used as a filter; (5)
`UNIQUE(source_file_id, name)` can crash a real sync on a genuine,
common language feature (function overloads) — **live-verified** on
both Python and TypeScript, not assumed; (6) empty-list ambiguity
(no symbols vs. extraction failure) is unacceptable for first-party
source and needed an explicit indexing-status model; (7)-(8) preserve
source-file identity/backwards-compatibility and the separate query
namespace; (9) validation must use the real template repository, not an
imaginary scratch scaffold; (10)-(11) preserve the three real
validations and the narrow non-goal boundary; (12) reconcile every
section against all of the above. Full detail inline below, at the
point each change actually lands.

## 0. Verified current state (read live, not assumed, re-verified for this amendment)

- HEAD at amendment time: `585f891` (Phase 77's initial plan, `planned`).
  Working tree clean.
- `planning/ROADMAP.md`/`planning/CONTEXT.md`: consistent, Phase 77
  `planned`, no phase `in progress`.
- `CG-009` (`planning/context-gaps/inbox.md`): `status: candidate`,
  unchanged since Phase 75 — still accurate (§1).
- Current schema version: `"10"`. Next: `"11"` (unchanged by this
  amendment).
- Latest ADR: `decisions/0064`. Next: `0065` (unchanged).
- **`https://github.com/ctosullivan/codecompass-template` — confirmed
  live via direct inspection: the repository exists and is genuinely
  empty** (no files, no README, no commits visible). This is not a
  future action to plan — it is the starting point implementation picks
  up from. Nothing was written to it during this planning amendment
  (read-only inspection only, per explicit instruction).
- Re-read `graph.py::_sync_vendors`/`_sync_symbols` directly (not from
  memory) to confirm the exact upsert-by-natural-key SQL shape this
  plan's §3/§4 now extends: both compute an `existing` set via `SELECT`,
  diff against `incoming`, `DELETE` anything stale, then
  `INSERT ... ON CONFLICT(...) DO UPDATE SET ...` for everything current.
  This pattern is reused, not reinvented, for `source_files`/
  `source_symbols` (§4).
- **Live-verified the overload-collision risk item 5 warns about**, on
  both ecosystems this plan supports — not assumed:
  - TypeScript, a real overloaded function declaration
    (`export function foo(a: string): void; export function foo(a:
    number): void; export function foo(a: string | number): void {
    ... }`) run through the existing `extract_npm_symbols` regex
    produces **three** `Symbol(name='foo', ...)` results, one per
    signature line.
  - Python, a real `@typing.overload`-stacked function (two `@overload`
    stub definitions plus the real implementation, all named `foo`) run
    through `extract_python_symbols` produces **three**
    `Symbol(name='foo', ...)` results, one per `def foo` occurrence.
  - **`UNIQUE(source_file_id, name)` would make either of these crash a
    real `codecompass sync`** on an `sqlite3.IntegrityError` the moment
    a second same-named row is inserted. This is not a hypothetical edge
    case — function overloading is ordinary, common code in both
    languages. §3.2 fixes this directly, with the natural key each
    verification's own distinct line numbers make safe.

## 1. Problem statement & evidence (unchanged by this amendment — still verified, still accurate)

- `graph.py:66-69` — `source_files` is `(id, path UNIQUE)` only.
- `graph.py:71-79` — `symbols.vendor_id INTEGER NOT NULL REFERENCES
  vendors(id) ON DELETE CASCADE` structurally forces every symbol row to
  belong to a tracked vendor.
- `sync.py::rebuild_project_graph` (`sync.py:287-330`) builds
  `source_file_rows` only from `usage.resolve_project_usage`'s own
  vendor-import-matched output — a file with no vendor-matching import
  never becomes a `source_files` row today, regardless of first-party
  content.
- Reproduced the exact `CG-009` symptom against this repository's own
  first-party code (`rebuild_deterministic`, `detect_git_topology`, ...)
  — the gap is universal, not Ledgerkit-specific, and not fixed by
  tracking more vendors.

`CG-009` stands verified, current, and unresolved. This phase directly
targets it.

## 2. Goals and non-goals

**Goals:**

1. A project's own first-party source files become durable,
   language-tagged `context-graph.db` rows, independent of `vendor.toml`
   content (works identically at 0 tracked vendors).
2. A project's own first-party **implementation** symbols — not merely
   an API surface — become durable, queryable rows with `kind`, `line`,
   and (where cheaply and reliably determinable) `visibility`, for
   languages with a reliable in-process extractor. Non-exported/private
   top-level declarations are included, not filtered out.
3. Every source file's own symbol-extraction outcome is explicitly,
   honestly represented — indexed (possibly with zero symbols),
   unsupported language, parse error, or unreadable — never a bare empty
   result standing in for more than one real cause.
4. Two small, explicit, additive CLI query commands expose this
   surface, without touching existing `query symbol`/`query vendor`
   compatibility, and without collapsing any nullable/unknown state into
   a false certainty (Phase 76's own corrected discipline, applied from
   first implementation here rather than fixed later).
5. **Deliver a genuinely usable, populated, MIT-licensed
   `codecompass-template` repository** at the real, already-existing
   `https://github.com/ctosullivan/codecompass-template` — not merely a
   design document.
6. Real, independent validation: a zero-vendor validation against a real
   clone of the now-populated template repository, a real Ledgerkit
   clone, and CodeCompass's own dogfooding — plus one lightweight
   independent task-context evaluation.

**Non-goals (explicitly deferred, not implemented this phase — unchanged
by this amendment):**

- Function/method call graphs, control/data flow, inheritance graphs,
  local symbol-reference resolution.
- Cross-file first-party import relationships (`source_file → imports →
  source_file`).
- Test-to-production-code relationships, doc-to-source relationships.
- Any semantic/AI-derived code understanding, embeddings, or
  whole-project summarisation of first-party code.
- Nested/member symbols (a class's own methods, a module's local
  helpers) — first-party symbol extraction stays **top-level only**.
  (Widened from "top-level, exported/public-equivalent only" to
  "top-level, implementation-inclusive" by this amendment — §5 — but the
  *top-level-only* boundary itself is unchanged: this phase still does
  not walk into class bodies or nested scopes.)
- Closing `CG-009` by lead fiat — closure goes through the normal
  context-gap lifecycle (§10.2, §21).
- The future first-party *relationship* graph (§13) — explicitly out of
  scope, unaffected by this amendment.

## 3. Proposed data model

Two new/extended tables — **not** a nullable `symbols.vendor_id`, for
the same evidence-based reasons as the initial plan (semantic distinction
+ migration risk, §3 of the original text, unchanged by this amendment).

### 3.1 `source_files` (extended, not replaced) — language, not ecosystem; nullable everywhere

```sql
CREATE TABLE IF NOT EXISTS source_files (
  id                      INTEGER PRIMARY KEY,
  path                    TEXT NOT NULL UNIQUE,
  language                TEXT,
  content_hash            TEXT,
  symbol_index_status     TEXT CHECK (
                            symbol_index_status IN (
                              'indexed','unsupported','parse_error','unreadable'
                            )
                          ),
  symbol_index_diagnostic TEXT
);
```

**Why `language`, not `ecosystem` — a real ontology mismatch, not a
naming preference.** `core.Ecosystem` has exactly one value covering
both JavaScript and TypeScript (`NPM` — it names a *package* ecosystem,
where both languages share one registry/toolchain). A project's own
first-party source file is genuinely, observably one or the other — a
`.js` file has no `interface`/`type` construct, a `.ts` file does — and
first-party symbol *kind* extraction (§5) genuinely differs between
them. Reusing `Ecosystem` here would either merge two languages that
need separate `kind` vocabularies, or force a new `Ecosystem` member
that means something different from every existing one (a *dependency*
package-manager concept gaining a non-dependency meaning). **A new,
narrow `Language` concept is introduced instead** — not a
"convenience reuse" of `Ecosystem`, an evidence-based rejection of it.

```python
class Language(StrEnum):
    """A first-party source file's own programming language — distinct
    from `core.Ecosystem` (a *package* ecosystem: npm covers both
    JavaScript and TypeScript dependencies identically, but a project's
    own first-party `.js` and `.ts` files are observably different
    languages with different symbol-kind vocabularies). Defined in
    `source_symbols.py`, not `core.py`, since this phase is its only
    consumer; promoting it to `core.py` is a trivial future move if a
    second consumer emerges — not preemptively done here.
    """

    PYTHON = "python"
    RUST = "rust"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    HASKELL = "haskell"
```

Suffix mapping (a genuine refinement over `usage.py`'s own
`_NPM_SOURCE_SUFFIXES`, which lumps `.js`/`.ts` together — first-party
discovery splits them): `.py`→`PYTHON`; `.rs`→`RUST`; `.js`/`.jsx`/
`.mjs`/`.cjs`→`JAVASCRIPT`; `.ts`/`.tsx`→`TYPESCRIPT` (`.d.ts` falls into
this bucket too — `Path.suffix` returns `.ts` for `foo.d.ts`, no special
case needed, confirmed by how Python's own `pathlib` suffix semantics
work); `.hs`→`HASKELL`.

**Nullable everywhere — fresh and upgraded databases identical, per
direct correction.** The initial plan proposed `ecosystem TEXT NOT NULL`
for a fresh schema while an upgraded database would transiently carry
`NULL` until repopulated — an inconsistency the amendment explicitly
rejects. **`language` (and `content_hash`/`symbol_index_status`/
`symbol_index_diagnostic`) are nullable in the schema itself, on every
database, new or upgraded, with no exception.** The contract:
`language` = a value from `Language` above, mechanically classified;
`NULL` = unresolved, legacy (a pre-Phase-77 row briefly present between
migration and the next rebuild), or a file recognized as source but not
mapped to any known `Language` (there is no such case today — every
recognized suffix maps to a `Language` — but the contract leaves room
for one without requiring a schema change). **Every row a genuinely
Phase-77-aware `sync` produces populates `language`** — the `NULL`
state is real but transient/exceptional, never the steady-state outcome
of an ordinary sync, on a fresh or upgraded database alike. This removes
the fresh/upgraded divergence entirely: there is exactly one schema-level
contract, applied identically regardless of a database's own history.

`symbol_index_status`/`symbol_index_diagnostic` — see §6 (the explicit
extraction-outcome model this amendment adds).

`content_hash` — unchanged from the initial plan: nullable, a
deterministic hash of the file's current text, forward-looking provenance
for a future relationship/staleness-detection consumer, not consumed by
any query this phase adds.

**`source_files` still broadens from "files with a detected vendor
usage" to "every recognized first-party source file"** — unchanged.
`uses_edges.source_file_id`'s FK is unaffected — unchanged.

### 3.2 `source_symbols` (new) — occurrence-based identity, implementation scope, optional visibility

```sql
CREATE TABLE IF NOT EXISTS source_symbols (
  id             INTEGER PRIMARY KEY,
  source_file_id INTEGER NOT NULL REFERENCES source_files(id) ON DELETE CASCADE,
  name           TEXT NOT NULL,
  kind           TEXT NOT NULL,
  line           INTEGER,
  purpose        TEXT,
  visibility     TEXT CHECK (visibility IN ('public','private')),
  UNIQUE (source_file_id, name, kind, line)
);
CREATE INDEX IF NOT EXISTS idx_source_symbols_file ON source_symbols(source_file_id);
```

**Duplicate-identity design — the occurrence approach, chosen with live
evidence (§0), not the logical-symbol (collapse) approach.** A natural
key of `(source_file_id, name)` alone — the initial plan's own choice —
would raise `sqlite3.IntegrityError` on the very first genuine function
overload `codecompass sync` ever encountered, live-confirmed above on
both Python and TypeScript. **Rejected the logical-symbol/collapse
alternative**: overloads are not duplicate facts to be merged into one
row with an arbitrary "which signature wins" rule — they are multiple,
individually real declarations, each at its own line, and collapsing
them would discard real information (a caller asking "what does line 43
declare" deserves a real answer, not a note that some other line won a
merge). **Adopted the occurrence approach**: `UNIQUE(source_file_id,
name, kind, line)` — each overload signature is a distinct row (distinct
`line`), the common single-declaration case behaves exactly as before
(one name, one kind, one line, one row, stable across an unedited file),
and no legitimate declaration can ever collide with another. Upsert
mirrors `_sync_symbols`'s own exact pattern (§0): compute the existing
`(source_file_id, name, kind, line)` tuple set via `SELECT`, diff against
the incoming set, `DELETE` anything stale, `INSERT ... ON CONFLICT(...)
DO UPDATE SET purpose = excluded.purpose, visibility =
excluded.visibility` for everything current — a genuinely identical
declaration (same file, name, kind, line) upserts cleanly across syncs;
a moved or removed declaration is deleted and, if still present
elsewhere, re-inserted at its new line as a "new" row (an honest
consequence of location being part of identity, not unnecessary churn —
no enrichment table hangs off `source_symbols.id` this phase, so no real
identity-preservation requirement is violated by this choice).

**`kind`**: unchanged reasoning from the initial plan — deliberately not
`CHECK`-constrained, a per-language, growing vocabulary.

**`visibility` (new field, this amendment)** — nullable, `CHECK
(visibility IN ('public','private'))`: a genuinely closed, two-value,
phase-owned vocabulary (unlike `kind`/`language`), so `CHECK`-constraining
it costs nothing in future extensibility. Populated per §5's own
per-language rules; `NULL` for a language/extractor with no deterministic
visibility signal (Haskell — no extractor at all; any future extractor
that doesn't yet compute it). **Recorded as a separate property, never
used to filter a symbol out of the table** — the explicit instruction
this amendment applies directly: a private/non-exported top-level
declaration is still a real row, with `visibility='private'`, not a
suppressed one.

**`purpose`, `line`** — unchanged reasoning from the initial plan.

**No `export_kind` column, still.** Unchanged: `source_symbols.kind` is
the intrinsic-kind concept `export_kind`'s own docstring says must not
be repurposed; `visibility` is a genuinely new, narrower property
(public/private), never conflated with either `kind` or vendor
`export_kind`.

### 3.3 Why a distinct extraction type, not a `kind`/`visibility` field on `symbols.Symbol`

Unchanged reasoning from the initial plan (§3.3 there) — reuse happens
at the extraction-technique level (§5), not the dataclass level; every
existing `symbols.Symbol` call site has no concept of `kind` or
`visibility` and gains nothing from carrying either.

## 4. Migration strategy (Phase 76's corrected discipline; nullable contract identical on fresh and upgraded databases)

- `_SCHEMA_VERSION`: `"10"` → `"11"` (unchanged).
- **`source_files`**: existing rows need four new columns (`language`,
  `content_hash`, `symbol_index_status`, `symbol_index_diagnostic`)
  added via `ALTER TABLE source_files ADD COLUMN ...` — all nullable, no
  default needed, since the schema-level contract is "nullable
  everywhere" (§3.1) with no fresh/upgraded divergence to reconcile.
  **Never drop-and-recreate `source_files`** — referenced by
  `uses_edges.source_file_id ON DELETE CASCADE`; a careless recreate
  would cascade-delete every `uses_edges` row, the exact class of risk
  `decisions/0064` fixed for `doc_artifacts`. `_source_files_schema_is_current(conn)`
  (checking `PRAGMA table_info(source_files)` for all four new columns,
  mirroring `_doc_artifacts_schema_is_current`'s exact introspection
  pattern) gates a new `_migrate_source_files_columns(conn)` that adds
  only genuinely-missing columns, decoupled from `meta.schema_version`'s
  own value, exactly as `decisions/0064` requires.
- **This amendment removes the initial plan's own `NOT NULL`-eventually
  posture entirely** — there is no longer a "the column should end up
  `NOT NULL` once populated" statement anywhere in this plan. The schema
  itself never enforces `language`/`content_hash`/`symbol_index_status`/
  `symbol_index_diagnostic` as `NOT NULL`, on a fresh `init_schema` call
  or an upgraded one — identical column definitions, identical
  nullability, identical `PRAGMA table_info` output, verified by a
  dedicated test (§15).
- **`source_symbols`**: brand new table, `CREATE TABLE IF NOT EXISTS`
  only — no migration risk, unchanged from the initial plan.
- **`source_files`/`source_symbols` upsert by natural key** — unchanged
  reasoning from the initial plan (§4 there), with `source_symbols`'s
  own key now `(source_file_id, name, kind, line)` per §3.2's corrected
  identity design, not `(source_file_id, name)`.
- **`uses_edges`/`symbols`/`symbol_enrichment`/`vendor_enrichment`
  behaviour completely unaffected** — unchanged.
- **A project with no `vendor.toml` still builds full first-party
  state** — unchanged.
- `rebuild_deterministic`'s new `source_symbols` parameter defaults to
  `()` — unchanged.

## 5. Source detection/extraction approach — implementation scope, not API-surface scope

New module: **`src/codecompass/source_symbols.py`** — unchanged
architectural role (Layer 2, project-facing counterpart to
`symbols.py`'s vendor-facing extractors).

### 5.1 File discovery — unchanged from the initial plan

`discover_source_files(project_root: Path) -> list[tuple[str, Language]]`
— same walk, same reused `usage._PROJECT_PRUNE_DIR_NAMES` prune set
(preserves first-party tests as source, §0/§5.1 of the initial plan,
unaffected by this amendment), now classifying by `Language` (§3.1)
instead of `Ecosystem`.

### 5.2 Extraction result — explicit success/failure, not a bare list (this amendment's new model, §6 below fully specifies it)

`extract_source_symbols_for_file(path: Path, language: Language) ->
SourceFileExtraction` — see §6 for the full `SourceFileExtraction`/
`SymbolIndexStatus` design. This subsection covers *what* each language
extracts; §6 covers *how success/failure is represented*.

```python
@dataclass(frozen=True)
class SourceSymbol:
    name: str
    kind: str
    line: int | None
    purpose: str | None = None
    visibility: str | None = None  # 'public' | 'private' | None
```

**Implementation scope, not API-surface scope — the core correction this
amendment makes.** The question for first-party source is "what does
this project implement," not "what does this dependency expose." Per
language:

- **Python** (`.py`): `extract_python_source_symbols`. **No scope change
  needed at all** — confirmed by re-reading `extract_python_symbols`
  directly: it already walks *every* top-level `FunctionDef`/
  `AsyncFunctionDef`/`ClassDef` via `ast.iter_child_nodes`, with no
  export/visibility filter of any kind (Python has no formal top-level
  export mechanism to filter on in the first place). The existing
  technique already satisfies "implementation, not API surface" for
  Python with zero widening. `kind` = `"function"`/`"class"`,
  `line = node.lineno`, `purpose = ast.get_docstring(node)`.
  **`visibility`** (new, cheap, reliable, and grounded in a real
  language-level convention, not a guess): `"private"` if
  `node.name.startswith("_")` (PEP 8's own leading-underscore
  convention — mechanically checkable, and the *only* Python convention
  with a real language-level consequence: `from module import *`
  actually excludes leading-underscore names), `"public"` otherwise.
- **Rust** (`.rs`): `extract_rust_source_symbols`. **Scope widened**
  from the initial plan: the existing vendor extractor's
  `_RUST_PUB_PREFIXES` line-scan matches only `pub fn`/`pub struct`/
  `pub enum`/`pub trait` — correct for a *vendor's* API surface, wrong
  for first-party implementation scope. The first-party variant matches
  the *same* four item keywords **with or without a leading `pub`**
  (`(?:pub\s+)?(fn|struct|enum|trait)\s+\w+`), recording
  `visibility='public'` when `pub` was present, `'private'` otherwise —
  a real, deterministic, zero-ambiguity signal (Rust's own visibility
  keyword, not a convention). `kind`/`line`/`purpose` (`///` doc
  comments) extracted identically to the vendor extractor's own
  technique.
- **JavaScript** (`.js`/`.jsx`/`.mjs`/`.cjs`) and **TypeScript**
  (`.ts`/`.tsx`): `extract_js_family_source_symbols` (one shared
  function — the underlying regex technique doesn't distinguish JS from
  TS syntax; `language` is determined by file suffix at the
  discovery/dispatch level, §3.1, not by which construct matched).
  **Scope widened**: the existing vendor extractor's `_NPM_EXPORT_RE`
  matches only a leading `export` keyword — correct for a vendor's own
  `.d.ts` declaration surface, wrong for first-party implementation
  scope. The first-party variant matches the same six construct keywords
  (`function`/`class`/`interface`/`const`/`type`/`enum`) **with or
  without a leading `export`** (`(?:export\s+)?(?:default\s+)?(?:declare\s+)?
  (function|class|interface|const|type|enum)\s+(\w+)`), recording
  `visibility='public'` when `export` was present, `'private'`
  otherwise. `kind`/`line`/`purpose` (leading JSDoc) extracted
  identically to the vendor extractor's own technique — **live-verified
  unchanged from the initial plan**: the base regex correctly extracts
  from real `.ts` implementation files (§0 of the initial plan's own
  verification stands; this amendment only widens the export
  requirement, not the underlying matching technique).
- **Haskell** (`.hs`): **file recognition only, no symbol extraction**
  — unchanged from the initial plan. No in-process Haskell parser
  exists; building one, or routing first-party files through the
  external-adapter-process protocol, is explicitly out of scope this
  phase, per Phase 76's own "declare unsupported honestly" precedent.

### 5.3 Walk-sharing note — unchanged from the initial plan

Sync orchestration should walk the project tree once, feeding both
import-usage detection and first-party file/symbol extraction from the
same pass — implementation-level detail, not a schema-affecting
constraint.

## 6. Explicit symbol-extraction outcome model (new section, this amendment)

The initial plan inherited the existing vendor-extractor convention
where an empty `list[Symbol]` means both "genuinely nothing here" and
"failed to parse/read" indistinguishably. **Unacceptable for first-party
source**, per direct instruction: a downstream developer actively
editing a file with a syntax error must never see a silent, misleading
"no symbols" result indistinguishable from a clean, symbol-free file.

**Modeled directly on `git_topology.RepositoryTopology`'s own precedent**
(a `status` + `reason` + data dataclass, Phase 76) — not a new pattern
invented for this phase:

```python
class SymbolIndexStatus(StrEnum):
    INDEXED = "indexed"
    UNSUPPORTED = "unsupported"
    PARSE_ERROR = "parse_error"
    UNREADABLE = "unreadable"


@dataclass(frozen=True)
class SourceFileExtraction:
    status: SymbolIndexStatus
    diagnostic: str | None
    symbols: tuple[SourceSymbol, ...]
```

- **`INDEXED`**: extraction ran to completion for a supported language.
  `symbols` may be **empty** — a real, valid, distinct outcome ("this
  file genuinely has no top-level implementation symbols"), never
  conflated with failure. `diagnostic` is `None`.
- **`UNSUPPORTED`**: no extractor exists for this file's `Language`
  (Haskell, today). `symbols` is always `()`. `diagnostic` is `None` — the
  *language itself* is the reason, already fully captured by
  `source_files.language`; no separate diagnostic text is needed.
- **`PARSE_ERROR`**: the language's own structural parser rejected the
  file — in practice, **Python-specific today**: `ast.parse` raising
  `SyntaxError`. Rust/JS/TS's own coarse line-scan/regex techniques have
  no real "parse" step to fail structurally (a malformed Rust/JS/TS file
  simply yields fewer or no matches, correctly surfacing as `INDEXED`
  with an empty/partial `symbols` tuple — an honest limitation of a
  non-parsing technique, not a defect this phase introduces or hides).
  `diagnostic` carries the caught exception's own message.
- **`UNREADABLE`**: the file itself could not be read (`OSError`,
  `UnicodeDecodeError`) — possible for any language. `diagnostic` carries
  the caught exception's own message.
- **No extraction error ever crashes `sync`** — every failure mode is
  caught inside `extract_source_symbols_for_file` itself and converted
  to a `SourceFileExtraction`, matching this codebase's own established
  "extractors never raise" convention (`symbols.py`'s own docstrings)
  extended, not violated, by making the failure *visible* instead of
  silently swallowed into `[]`.

`source_files.symbol_index_status`/`symbol_index_diagnostic` (§3.1)
persist exactly this outcome per file — the CLI (§7) renders all four
states honestly, never collapsing one into another.

## 7. CLI / query design

Unchanged separation decision from the initial plan: **`query symbol` is
completely unmodified** — the vendor-vs-first-party axis is real, a
synthetic "self" vendor remains rejected, no unification.

- **`codecompass query source <path>`** exposes, at minimum: `language`
  (or an explicit "unresolved" state if `NULL`), `content_hash` if
  present, `symbol_index_status` (one of the four states, rendered
  explicitly — e.g. `"parse error: <diagnostic>"`,
  `"no symbol extractor for <language>"`, `"unreadable: <diagnostic>"`,
  or the symbol list itself for `indexed`), its own `source_symbols`
  (name, kind, line, purpose, `visibility` — rendered as `public`/
  `private`/`unknown`, **never omitted or silently defaulted** when
  `NULL`, applying Phase 76's own corrected tri-state discipline from
  first implementation rather than fixing it after the fact), and its
  own recorded vendor usage (cross-referencing `uses_edges`, mirroring
  `query vendor`'s existing rendering). `--json` supported, with every
  nullable field emitted as JSON `null`, not coerced to a default or
  omitted.
- **`codecompass query source-symbol <name>`** exposes, at minimum:
  name, kind, source file path, line, purpose, the containing file's
  `language`, and `visibility` (again rendered as `public`/`private`/
  `unknown`, never collapsed). `--json` supported with the same explicit-
  null discipline.
- No special "not yet indexed" handling needed — unchanged from the
  initial plan; `source_files`/`source_symbols` populate on every
  ordinary `sync`.
- New `graph.py` query functions: `source_file_profile(conn, path) ->
  dict | None` and `source_symbol_profile(conn, name) -> list[dict]`.
- **Explicit cross-reference to the exact defect this amendment must not
  repeat**: Phase 76's own corrective pass (`decisions/0064` era, `db33352`)
  fixed `query topology` for precisely this class of bug — a nullable
  fact (`is_dirty`, `revision_matches_pin`) rendered via bare Python
  truthiness, silently turning `None` into a false `"clean"`/`"differs
  from pin"`. `query source`/`query source-symbol`'s own renderers reuse
  the same `_tri_state_label`-style helper `cli.py` already has for
  exactly this purpose, applied to `visibility` and to
  `symbol_index_status`'s own four-way rendering, from the very first
  implementation of these commands — not discovered and fixed in a later
  corrective pass.

## 8. `codecompass-template` — a real deliverable this phase, not a design-only artifact

**The repository already exists and is confirmed empty (§0).** This
phase populates it with a genuinely usable initial version — the
initial plan's "design only, not created" framing is retired by this
amendment; every statement in this section describes what Phase 77's
own implementation actually delivers into the real repository.

### 8.1 Purpose and shape — unchanged

Lets a downstream project adopt the proven workflow shape — understand →
research/evidence → plan → design → implement → verify → retro → update
knowledge — without inheriting CodeCompass's own phase history,
12-role specialist-agent roster, or CodeCompass-only knowledge.

### 8.2 Structure to actually populate (a concrete deliverable list, not a sketch)

```
codecompass-template/            (existing GitHub repo, currently empty)
├── LICENSE                      (MIT, §9)
├── README.md                    (what this template is, how to adopt it)
├── CLAUDE.md                    (minimal: plan-before-code, doc-sync, DoD — no GATE/priority/phase-group machinery)
├── vendor.toml                  (empty/commented example — CodeCompass populates it via discovery)
├── .gitignore                   (context-graph.db, vendor/, generated Skills/slash-commands — never committed)
├── docs/
│   └── architecture.md          (a starting current-state doc template)
├── decisions/
│   ├── README.md                (append-only ADR convention, generic)
│   └── TEMPLATE.md
└── planning/
    ├── ROADMAP.md                (empty phase table + the sync rules, generic)
    ├── CONTEXT.md                (empty current-state skeleton)
    ├── retros/
    │   └── TEMPLATE.md
    ├── knowledge/
    │   └── README.md             (generic "learnings inbox" convention)
    └── context-gaps/
        └── README.md             (generic "context gap" convention, no GATE DB/DD language)
```

Every file above is a real implementation deliverable for this phase —
not a sketch to revisit later.

### 8.3 What is explicitly NOT copied — unchanged

The full `.claude/agents/*` roster, historical phase machinery,
milestone-group/GATE-style gates, `planning/learnings/`'s own *content*
(only the convention), and any generated CodeCompass artifact
(`context-graph.db`, `vendor/<name>/`, generated Skills/slash-commands).

### 8.4 What Priority D productisation actually needs — unchanged, now delivered rather than merely found

Investigation (unchanged from the initial plan) found no evidence any
new runtime tooling is required — the template's job is documentation
and empty scaffolding only, using CodeCompass surfaces (`init`/`sync`/
`query`, generated Skills, `/discovery`, and — after this phase —
`query source`/`query source-symbol`) that already ship. This phase
*delivers* that scaffolding into the real repository, directly and
concretely satisfying Priority D's own success criterion rather than
merely describing how it could be satisfied.

## 9. MIT licensing / provenance approach — unchanged policy, now applied to a real delivered repository

The full file-by-file provenance table from the initial plan (§9 there)
is unchanged in substance and now describes what implementation actually
writes into the real repository, not a hypothetical:

| Template file | Provenance | Treatment |
|---|---|---|
| `LICENSE` (MIT) | New | Standard MIT boilerplate |
| `README.md` | New | Fresh prose, no CodeCompass README text reused |
| `CLAUDE.md` | Rewritten from principles | Reusable process idea (plan-before-code, same-commit doc-sync, retro-on-completion), freshly worded, minimal, no phase/priority/gate machinery |
| `vendor.toml` | New | Empty/commented example |
| `.gitignore` | New | Freshly authored, generic ignore-list |
| `docs/architecture.md` | New | A minimal starting-point template, not CodeCompass's own architecture content |
| `decisions/README.md`, `decisions/TEMPLATE.md` | Rewritten from principles | The append-only-ADR convention (itself not CodeCompass's own invention — the widely-used public ADR pattern) is reused; wording is fresh, shorter, no CodeCompass cross-references |
| `planning/ROADMAP.md`, `planning/CONTEXT.md` | Rewritten from principles | The shape is reused; ships empty/skeletal with fresh instructional prose |
| `planning/retros/TEMPLATE.md` | Rewritten from principles | Reusable section-list idea, freshly worded and shorter |
| `planning/knowledge/README.md`, `planning/context-gaps/README.md` | Rewritten from principles | The candidate→promoted lifecycle concept is reused; all CodeCompass-specific terminology/cross-references dropped |

**Legal note, unchanged**: CodeCompass's single copyright holder
(`decisions/0055`) could legally dual-license their own original text
without rewriting it — this plan does not rely on that, for the same
practical unambiguous-provenance reason the initial plan gave.

**No generated CodeCompass artifact is ever committed to the template
repository** — its own `.gitignore` excludes exactly the paths a real
`codecompass init`/`sync` run produces, and populating the template
(§8.2) never involves running `codecompass sync` *inside* the template
repository's own working tree before or during that population — only
the validation clone (§10.1) ever runs `sync`, and that clone is
disposable, not the template repository itself.

**Provenance documentation for future contributors** — unchanged:
`codecompass-template`'s own `README.md` states its MIT license,
independent authorship, and universal-adoption intent; CodeCompass's own
`README.md`/`ai-docs/README.md` cross-link it with the same boundary
stated from the other side.

**Final architecture, preserved exactly as required:**

```
CodeCompass implementation   — GPL-3.0-or-later
codecompass-template         — MIT
downstream project           — chooses its own compatible license
```

## 10. Validation fixtures — three real validations, using the real repository

### 10.1 Template validation — the architectural acceptance test, against the real repository

**Corrected from the initial plan's own "scratch scaffold" framing** —
the real repository now exists and this validation uses it directly:

1. Populate the real `codecompass-template` repository (§8.2) — commit
   and push to its own existing remote (a separate git identity from
   `codecompass`'s own repository/remote; cloned/worked on in a
   location entirely outside this repository's own working tree).
2. Obtain a **clean clone of the real, now-populated
   `codecompass-template` repository** into a scratch location.
3. Add a handful of real, representative first-party Python files
   (a module with 2-3 functions/classes including at least one
   leading-underscore "private" one, a test file) to the clone —
   **uncommitted, or committed to the scratch clone only, never pushed
   back to the template's own remote** — **zero entries in
   `vendor.toml`**.
4. Run `codecompass sync` (editable install) against the clone.
5. **Verify**: `source_files` rows exist for the added files with
   correct `language`/`symbol_index_status`; `source_symbols` rows exist
   for the top-level functions/classes, with the private one correctly
   `visibility='private'`; `codecompass query source <path>` and
   `query source-symbol <name>` both return real data with every field
   this plan specifies; `vendors`/`symbols` tables are empty (0 rows) —
   **no fake/self vendor row created**, confirmed by direct `sqlite3`
   inspection, not only CLI output.
6. **Also verify the template repository's own hygiene**: the clone's
   `git status`/`git log` shows no `context-graph.db`, `vendor/`, or
   generated Skill ever committed to the *template's own* history — only
   the scratch clone's own local, uncommitted (or locally-committed-and-
   discarded) working state ever contains them.
7. **Also verify the adoption workflow is genuinely understandable**: a
   fresh read of the populated template's own `README.md`/`CLAUDE.md`
   (by the lead, or ideally delegated to a fresh subagent with no prior
   context on this plan, matching this project's own "verify
   independently" discipline) should make the understand → research →
   plan → design → implement → verify → retro → update-knowledge shape
   clear without any CodeCompass-internal knowledge.

### 10.2 Ledgerkit validation — unchanged in substance, still the principal `CG-009` evidence

Fresh clone, real current HEAD, re-resolve `Posting`/`Amount`/`Tag`'s
real current locations (not hardcoded from Phase 75's own `6c90b4c`).
Verify `query source-symbol` returns correct data for each. **`CG-009`
is not closed by this test passing** — it goes through the normal
context-gap lifecycle (§21), the same discipline as the initial plan
required and this amendment does not weaken.

### 10.3 CodeCompass dogfooding — unchanged in substance

Run against CodeCompass's own working tree; resolve real, current
symbol names at implementation time (`detect_git_topology`,
`rebuild_project_graph`, or their current equivalents); verify
coexistence with existing vendor symbols in the same database.

## 11. Independent evaluation methodology — unchanged in substance, fixture reference updated

Same seed-then-fork methodology, same measured dimensions, same
`context-evaluator` protocol, same `L-062`/`L-064`/`L-065` read-scope/
report-to-disk discipline as the initial plan's §11. **Fixture**: now
explicitly the real, populated `codecompass-template` clone from §10.1
(or Ledgerkit, if a more suitable self-contained task exists there) —
no longer "the template project (or another... fixture)" hedged against
a not-yet-real repository.

## 12. First-party language/extraction scope summary (supersedes the initial plan's "ecosystem scope" table)

| Language | File recognition | Symbol extraction | Scope | Basis |
|---|---|---|---|---|
| Python (`.py`) | Yes | Yes | Every top-level `def`/`async def`/`class`, public and private (leading-underscore) alike | `ast`-based; no scope change needed — the existing technique already covers full implementation scope |
| Rust (`.rs`) | Yes | Yes | Every top-level `fn`/`struct`/`enum`/`trait`, public and private alike, `visibility` recorded | Line-scan, **widened** from `pub`-only to `pub`-or-not, `visibility` from the `pub` keyword itself |
| JavaScript (`.js`/`.jsx`/`.mjs`/`.cjs`) | Yes | Yes | Every top-level `function`/`class`/`interface`/`const`/`type`/`enum`, exported and non-exported alike, `visibility` recorded | Regex, **widened** from `export`-only to `export`-or-not, `visibility` from the `export` keyword itself |
| TypeScript (`.ts`/`.tsx`) | Yes | Yes | Same as JavaScript (shared extractor, language distinguished only by suffix) | Same regex technique, **live-verified** against a real `.ts` implementation file and a real overloaded-function `.ts` file (§0) |
| Haskell (`.hs`) | Yes | **No — explicitly unsupported** | `symbol_index_status='unsupported'` | No in-process parser exists; out of scope, not fabricated |

## 13. Likely follow-on phase — unchanged, not scoped here

Relationships among first-party objects (`source_file → imports →
source_file`, `source_symbol → references/calls → source_symbol`,
`test → tests → source_symbol/source_file`, `doc → documents →
source_symbol`) remain explicitly deferred, recorded as opportunity
only, per the initial plan's §13 (unchanged by this amendment). This
remains the most likely path to a genuine `CG-001`-shaped trial (§7 of
the initial plan, unaffected by this amendment).

## 14. Files expected to change

### 14.1 This repository (`codecompass`)

- **New**: `src/codecompass/source_symbols.py` (`Language`,
  `SymbolIndexStatus`, `SourceSymbol`, `SourceFileExtraction`,
  `discover_source_files`, `extract_source_symbols_for_file` +
  per-language functions).
- **`src/codecompass/graph.py`**: `_SCHEMA_VERSION` "10"→"11";
  `source_files` gains `language`/`content_hash`/`symbol_index_status`/
  `symbol_index_diagnostic` (all nullable, `ALTER TABLE ADD COLUMN`, no
  fresh/upgraded divergence, §4); new `source_symbols` table (§3.2);
  `SourceFileRow` extended; new `SourceSymbolRow` dataclass; migration
  helpers (§4); `_sync_source_files`/`_sync_source_symbols` (upsert by
  the corrected natural keys); `rebuild_deterministic` gains a
  `source_symbols` parameter (default `()`); new
  `source_file_profile`/`source_symbol_profile` query functions.
- **`src/codecompass/sync.py`**: `rebuild_project_graph` — full
  first-party discovery pass replacing the vendor-usage-gated one,
  feeding `source_file_rows`+`source_symbol_rows`, walk-sharing with
  `usage.resolve_project_usage`.
- **`src/codecompass/cli.py`**: new `query source`/`query source-symbol`
  commands + rendering, reusing the existing tri-state-label discipline
  (§7) from first implementation.
- **`src/codecompass/skill.py`**: generated tool Skill gains the two new
  command lines + table names.
- **`docs/cli-reference.md`**: new sections, including the explicit
  four-state `symbol_index_status` disclosure and `visibility` rendering.
- **`architecture/context-graph-schema.md`**: `source_files`/
  `source_symbols` sections, corrected stale description, the
  nullable-everywhere contract stated explicitly.
- **`architecture/overview.md`**: new "First-party source awareness"
  subsection.
- **`architecture/module-map.md`**: add `source_symbols.py`; also fix
  the pre-existing, unrelated omission of `git_topology.py` found while
  reading this file for the initial plan.
- **`decisions/0065-<slug>.md`** (new ADR — language-vs-ecosystem
  ontology decision, nullable-everywhere migration contract, occurrence-
  based symbol identity with the live overload evidence, implementation-
  vs-API-surface scope decision, explicit indexing-status model,
  Haskell's non-support).
- **`README.md`, `ai-docs/README.md`**: new capability bullets + the
  `codecompass-template` cross-link/license note.
- **`CHANGELOG.md`**: `[Unreleased]` entry.
- **`planning/ROADMAP.md`**, **`planning/CONTEXT.md`**: updated per this
  amendment (below).
- **`planning/context-gaps/inbox.md`**: `CG-009` triage note at closeout.

### 14.2 `codecompass-template` (separate repository, real deliverable)

Every file in §8.2's structure — a genuine implementation deliverable of
this phase, committed and pushed to its own existing remote, not part of
this repository's own diff/changed-file list, and not gated on a future
phase.

## 15. Tests

- **New `tests/test_source_symbols.py`**:
  - file discovery (prune-set behaviour, tests kept, `Language`
    classification by suffix — including `.js` vs `.ts` distinctness —
    independent of `vendor.toml` content);
  - Python/Rust/JS/TS extraction, including a **dedicated overload test
    per ecosystem** (a real overloaded function, at least Python
    `@overload` and one JS-family overloaded declaration, asserting
    multiple distinct rows are produced, none dropped, none crashing);
  - visibility extraction (Python leading-underscore, Rust `pub`
    presence/absence, JS/TS `export` presence/absence);
  - **`SourceFileExtraction` status coverage**: an indexed file with
    symbols; an indexed file with zero symbols (both must be `INDEXED`,
    distinguishable only by `symbols` being non-empty vs. empty, not by
    `status`); an unsupported language (Haskell); a genuine Python
    syntax error (`PARSE_ERROR`, `diagnostic` populated); an unreadable
    file (permissions or a deliberately undecodable byte sequence,
    `UNREADABLE`, `diagnostic` populated) — every one of the five
    required cases from the task's own instruction.
- **`tests/test_graph.py`** additions:
  - migration safety (`_migrate_source_files_columns` — an existing
    pre-migration fixture's `uses_edges` rows survive);
  - **a dedicated fresh-vs-upgraded nullability-contract test**: build a
    database via `init_schema` fresh, and a second database via the old
    (pre-Phase-77) schema then migrated, and assert
    `PRAGMA table_info(source_files)` returns **identical** column
    names/types/nullability for both — the concrete test this
    amendment's §3.1/§4 correction requires;
  - `source_files`/`source_symbols` upsert-by-natural-key behaviour,
    including the corrected `(source_file_id, name, kind, line)` key —
    an unchanged declaration keeps its `id`, a removed one is deleted, a
    genuine overload produces multiple stable rows across two
    `rebuild_deterministic` calls without collision;
  - new query function tests.
- **`tests/test_sync.py`** additions: real-call-site test (L-021) for
  `rebuild_project_graph`, including the zero-vendor case; **a dedicated
  real-call-site overload test** confirming `codecompass sync` does not
  raise on a fixture file containing a genuine function overload.
- **`tests/test_cli.py`** additions: `query source`/`query source-symbol`
  — found/not-found/`--json` cases, all four `symbol_index_status`
  renderings, `visibility` tri-state rendering (`public`/`private`/
  `unknown`, never collapsed).
- Full existing suite must continue to pass unmodified in substance.

## 16. Documentation / ADR requirements — unchanged in shape, content updated per this amendment

`decisions/0065` now records: the language-vs-ecosystem ontology
decision (with the JS/TS example), the nullable-everywhere migration
contract, the occurrence-based symbol identity (with the live overload
evidence from §0), the implementation-vs-API-surface scope decision, and
the explicit four-state indexing model. `docs/`/`architecture/` updates
per §14.1, same commit as the code. Independent `docs-reconstructor`
drift audit before closeout, unchanged. `codecompass-template`'s own
content is fully specified in §8-§9 — implementation writes it directly
into the real repository; no separate design doc is needed since this
plan *is* that design, now being executed rather than deferred.

## 17. Rollback / cleanup requirements

- Every scratch clone/fixture for §10's validations: built outside both
  `codecompass` and `codecompass-template`'s own working trees, never
  added to `vendor.toml`, fully deleted once validation completes —
  unchanged discipline from the initial plan.
- **Populating and pushing to `codecompass-template`'s own remote is a
  real, hard-to-reverse, externally-visible action** — per this
  session's own standing git-safety norms, it proceeds at implementation
  time with the same explicit-confirmation posture any other push to a
  shared/external remote already requires in this session; this plan
  authorizes *what* gets written (§8.2/§9), not a standing blanket
  authorization to push without that ordinary confirmation step.
- No git worktree, branch, or remote is created against `codecompass`'s
  own repository for this phase's validation work.
- A migration-safety test fixture (an old-schema `.db` file, §15) is an
  in-repository test fixture with normal `tmp_path` cleanup, not a
  scratch clone.

## 18. Human decision gates

**None identified**, re-confirmed for this amendment. All twelve
requested changes were resolved by direct evidence (live regex/AST
verification, the real repository's confirmed-empty state, established
migration-safety precedent) or by the task's own already-fixed policy
(MIT/GPL separation, template-is-now-a-deliverable) — none required
escalation. The one item genuinely outside this plan's own authority to
decide now — actually executing a push to `codecompass-template`'s real
remote — is not a planning-time gate; it is an ordinary execution-time
confirmation step (§17), the same as any other push this session already
treats that way.

## 19. Implementation sequence (for the eventual implementation phase, not run now)

1. `source_symbols.py` (discovery + per-language extraction +
   `SourceFileExtraction` model + overload/visibility/indexing-status
   tests) — verifiable in complete isolation.
2. `graph.py` schema/migration/query-function changes + the
   fresh-vs-upgraded nullability-contract test + migration regression
   test.
3. `sync.py::rebuild_project_graph` wiring (real-call-site test,
   zero-vendor test, overload real-call-site test).
4. `cli.py` query commands + `skill.py` update + CLI tests (all four
   indexing states, visibility tri-state).
5. Docs/ADR/architecture updates, same commits as the code.
6. **Populate and push `codecompass-template`** (§8.2/§9) to its own
   existing remote — a distinct, explicitly-confirmed action (§17).
7. §10.1 validation against a fresh clone of the now-real, populated
   template repository — first among the three validations, cheapest
   and most direct.
8. §10.3 CodeCompass dogfooding validation — second.
9. §10.2 Ledgerkit validation — third, requiring a fresh external clone
   and path re-resolution.
10. §11 independent task-context evaluation.
11. `CG-009` triage (not closure-by-fiat) using §10.2's evidence.
12. Full closeout sequence per `CLAUDE.md` §5/`planning/
    agent-led-workflow.md`'s corrected steps (Phase 76's own corrective-
    pass discipline): docs-maintainer → docs-reconstructor drift audit →
    interim `roadmap-context-curator` reconciliation → retro →
    `knowledge-curator` triage → independent `release-phase-auditor` →
    only-on-PASS final `roadmap-context-curator` reconciliation (scoped
    per `CLAUDE.md` §5's own narrow three-target exemption) → push.

## 20. Verification commands — unchanged

```bash
.venv/bin/pytest -q
.venv/bin/ruff check .
python3 scripts/check_user_docs.py --strict
python3 scripts/check_knowledge_base.py
```

Plus the three live validations (§10) and the independent evaluation
(§11) — not mechanical, each requires a real fixture and, for §10.1/
§10.2/§11, real external repository interaction.

## 21. Definition of Done

Per `CLAUDE.md` §5, unabridged, **corrected by this amendment to require
`codecompass-template` as a genuinely usable, populated repository, not
a plan**: code implemented; plan's own verification (§20) passes;
`docs/`/`architecture/`/`decisions/` updated; independent
`docs-reconstructor` drift audit finds `NO DRIFT`; changelog entry
added; `planning/CONTEXT.md` reflects the new state; a substantive phase
retro exists; candidate learnings triaged by `knowledge-curator`;
**`codecompass-template` exists at its real URL, populated per §8.2,
MIT-licensed, validated by a real clean clone (§10.1) confirming both
the zero-vendor first-party-source acceptance test and the template's
own repository hygiene (no generated CodeCompass state ever committed to
its history)**; `CG-009` triaged (promoted/closed/retained — never
closed by lead assertion alone) using real evidence from §10.2; a
`context-evaluator` report exists and is linked for §11; independent
`release-phase-auditor` pass (`PASS`/`PASS WITH NON-BLOCKING
OBSERVATIONS`); only then does `planning/ROADMAP.md` mark Phase 77
`done`, via a genuinely fresh `roadmap-context-curator` dispatch, scoped
per `CLAUDE.md` §5's own narrow terminal-reconciliation exemption. All
disposable scratch clones/fixtures (§17) confirmed cleaned up. **The
previously-recommended second, differently-shaped Ledgerkit Priority A
trial is not silently treated as satisfied by this phase** — it remains
live, unclaimed, to be reconsidered once the follow-on relationship
phase (§13) exists.
