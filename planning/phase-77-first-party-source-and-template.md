# Phase 77: First-party source awareness + `codecompass-template` — plan

**Status:** planned (2026-09-28).

Direct user request, two connected goals: (1) make a project's own
first-party source (files + top-level symbols) a first-class,
non-vendor-gated object in `context-graph.db`, closing the structural gap
`CG-009` documented; (2) design (not yet create) a separate,
MIT-licensed `codecompass-template` repository that packages the proven
downstream-adoption workflow shape without inheriting CodeCompass's own
GPL implementation or internal governance corpus. Planning only — no
`src/` change, no external repository created, per explicit instruction.

## 0. Verified current state (read live, not assumed)

- HEAD at plan time: `e11afa7` (Phase 76's corrective pass, `done`,
  pushed).
- `planning/ROADMAP.md`'s Phase 76 row: `done`. `planning/CONTEXT.md`
  consistent with it. No phase currently `in progress`. No
  `planning/phase-77-*.md` existed before this file — **77 is the
  correct next phase number**, not assumed from the prompt's own
  wording but confirmed by `ls planning/phase-*.md` (highest existing:
  76) and a repo-wide search finding no other "Phase 77" reference
  anywhere.
- `CG-009` (`planning/context-gaps/inbox.md`): `status: candidate`,
  filed Phase 75, re-verified live for this plan (see §1) — still
  accurate, not stale.
- Current schema version: `"10"` (`graph.py::_SCHEMA_VERSION`, set by
  Phase 76). Next: `"11"`.
- Latest ADR: `decisions/0064`. Next: `0065`.
- CodeCompass's own license: GPL-3.0-or-later (`LICENSE`,
  `pyproject.toml`), single committer (`decisions/0055`'s own research,
  unchanged) — relevant to §10.

## 1. Problem statement & evidence — verified, not assumed

Re-derived directly from current source, not taken from `CG-009`'s own
prose on faith:

- `graph.py:66-69` — `source_files` is `(id, path UNIQUE)` only, no
  `ecosystem`, no content identity, no symbol relationship of its own.
- `graph.py:71-79` — `symbols.vendor_id INTEGER NOT NULL REFERENCES
  vendors(id) ON DELETE CASCADE` — structurally forces every symbol row
  to belong to a tracked vendor. No project is ever itself a `vendors`
  row.
- `sync.py::rebuild_project_graph` (`sync.py:287-330`) — `symbol_rows`
  is built by iterating `configs: list[VendorConfig]` only, calling
  `adapter.symbols()` once per tracked vendor. `source_file_rows` is
  built from `usage.resolve_project_usage(project_root, configs)`'s own
  output — **only files where a detected import matched a tracked
  vendor name** (`sync.py:318-330`). A file with no vendor-matching
  import never becomes a `source_files` row today, regardless of how
  much first-party code it contains.
- Live-reproduced the exact `CG-009` symptom against this repository's
  own architecture (not re-run against Ledgerkit at plan time — that is
  §11's own validation step, not a planning-time action): `graph.py`'s
  own `rebuild_deterministic`, `detect_git_topology`, or any other
  first-party function/class in `src/codecompass/` is equally
  unqueryable via `codecompass query symbol` today, for the exact same
  structural reason `CG-009` names for Ledgerkit's `Posting`/`Amount`/
  `Tag` — this is not a Ledgerkit-specific gap, it is universal across
  every project CodeCompass has ever been run against, including its
  own dogfooding case.
- **Confirmed: this is not fixed by tracking more vendors.** The
  `adapter.symbols()` walk only ever touches `adapter.source_location()`
  — a vendor's own installed package directory — never the calling
  project's own tree, for any ecosystem, at any vendor count including
  zero.

`CG-009` stands verified, current, and unresolved. This phase directly
targets it.

## 2. Goals and non-goals

**Goals:**

1. A project's own first-party source files become durable,
   ecosystem-tagged `context-graph.db` rows, independent of `vendor.toml`
   content (works identically at 0 tracked vendors).
2. A project's own first-party top-level symbols (functions, classes,
   and ecosystem-equivalent constructs) become durable, queryable rows
   with `kind` and `line`, for ecosystems with a reliable in-process
   extractor.
3. Two small, explicit, additive CLI query commands expose this
   surface, without touching existing `query symbol`/`query vendor`
   compatibility.
4. A design (not yet a repository) for `codecompass-template`, an
   MIT-licensed, minimal downstream-adoption scaffold.
5. Real, independent validation: a zero-vendor template fixture, a real
   Ledgerkit clone, and CodeCompass's own dogfooding — plus one
   lightweight independent task-context evaluation.

**Non-goals (explicitly deferred, not implemented this phase):**

- Function/method call graphs, control/data flow, inheritance graphs,
  local symbol-reference resolution.
- Cross-file first-party import relationships (`source_file → imports →
  source_file`).
- Test-to-production-code relationships, doc-to-source relationships.
- Any semantic/AI-derived code understanding, embeddings, or
  whole-project summarisation of first-party code.
- Nested/member symbols (a class's own methods, a module's local
  helpers) — first-party symbol extraction stays **top-level only**,
  matching the existing vendor-symbol extractors' own established scope
  exactly (§6).
- Creating, initializing, or publishing the `codecompass-template`
  repository itself.
- Closing `CG-009` by lead fiat — closure goes through the normal
  context-gap lifecycle (`knowledge-curator` triage +
  `context-evaluator`-backed evidence from §11's own validations), not
  "code was added."

## 3. Proposed data model

Two new tables, extending `source_files` and adding `source_symbols` —
**not** a nullable `symbols.vendor_id`. Rationale (evidence-based, not
merely the semantic-distinction argument the task prompt already
anticipated):

- **Semantic**: a vendor symbol answers "what does this dependency's
  API surface offer"; a first-party symbol answers "what does this
  project itself implement." Conflating them into one table with an
  optional owner would force every future field (`export_kind`, vendor
  usage-count joins, `symbol_enrichment`) to either apply ambiguously to
  both kinds or grow a second discriminator column anyway — no
  simplification, only ambiguity.
- **Migration risk**: SQLite cannot relax a column's `NOT NULL`
  constraint via `ALTER TABLE` — doing so would require the same
  drop-and-rebuild-with-data-copy shape Phase 76's corrective pass just
  replaced for `doc_artifacts` specifically because it was a real,
  demonstrated risk (`decisions/0064`, `decisions/0063` point 6). A
  fully separate new table needs only `CREATE TABLE IF NOT EXISTS` — no
  existing row is ever touched, no destructive-migration risk exists at
  all. This is the stronger, concrete argument for the separate-table
  design.
- **Backwards compatibility**: zero interaction with `vendors`,
  `symbols`, `symbol_enrichment`, or `uses_edges` — every existing query
  path is structurally unreachable from the new tables and vice versa.

### 3.1 `source_files` (extended, not replaced)

```sql
CREATE TABLE IF NOT EXISTS source_files (
  id            INTEGER PRIMARY KEY,
  path          TEXT NOT NULL UNIQUE,
  ecosystem     TEXT NOT NULL CHECK (ecosystem IN ('npm','python','cargo','haskell')),
  content_hash  TEXT
);
```

- `ecosystem` reuses the exact same `Ecosystem` enum/CHECK vocabulary
  `vendors.ecosystem` already uses (`core.Ecosystem`) — no new type. A
  file's ecosystem is determined by its own suffix (`.py`→python,
  `.rs`→cargo, `.js/.jsx/.ts/.tsx/.mjs/.cjs`→npm, `.hs`→haskell),
  **independent of `vendor.toml`** — the same suffix-dispatch pattern
  `usage.detect_imports_for_file` already uses, confirmed live (§0/§6).
  This is what makes the zero-vendor acceptance test possible: ecosystem
  tagging never consults tracked-vendor configuration at all.
- `content_hash` (nullable — `None` only on a read failure, matching
  every extractor's own "never raise" convention) is a deterministic
  hash of the file's own current text, computed once per sync. Included
  now as cheap, low-risk, forward-looking provenance (matching
  `doc_chunks.content_hash`'s own precedent) for a concrete future
  consumer the follow-on relationship phase will need (detecting whether
  a file changed since a prior sync, without re-diffing full content) —
  not consumed by any query this phase adds.
- **`source_files` broadens from "files with a detected vendor usage"
  to "every recognized first-party source file"** — a strict superset
  of today's population. `uses_edges.source_file_id`'s own FK is
  unaffected: it already resolves against whatever `source_file_ids`
  mapping the current rebuild produced, so a larger `source_files` set
  changes nothing about how `uses_edges` rows resolve.

### 3.2 `source_symbols` (new)

```sql
CREATE TABLE IF NOT EXISTS source_symbols (
  id             INTEGER PRIMARY KEY,
  source_file_id INTEGER NOT NULL REFERENCES source_files(id) ON DELETE CASCADE,
  name           TEXT NOT NULL,
  kind           TEXT NOT NULL,
  line           INTEGER,
  purpose        TEXT,
  UNIQUE (source_file_id, name)
);
CREATE INDEX IF NOT EXISTS idx_source_symbols_file ON source_symbols(source_file_id);
```

- `kind` is deliberately **not** `CHECK`-constrained to a fixed
  enumeration — unlike `vendors.ecosystem`/`export_kind` (small, stable,
  already-closed sets), the kind vocabulary is per-ecosystem and will
  grow as ecosystem support grows (Python: `function`/`class`; Rust:
  `function`/`struct`/`enum`/`trait`; npm/TS: `function`/`class`/
  `interface`/`const`/`type`/`enum`) — constraining it now would force a
  schema migration for every future ecosystem's own kind vocabulary,
  which the extensibility goal doesn't justify.
- `line` is nullable in the schema (an ecosystem extractor that can't
  cheaply produce a line number could still emit a symbol without one)
  but every extractor this phase actually ships (§6) always populates
  it — no extractor produces a `None` line in practice today.
- `purpose` is the same "docstring/doc-comment when deterministically
  available" concept `symbols.Symbol.purpose` already has — reused
  logic, not reinvented (§6).
- `UNIQUE (source_file_id, name)` mirrors `symbols`'s own
  `UNIQUE (vendor_id, name)` precedent exactly, including its
  known-and-accepted limitation (a file with two same-named top-level
  declarations collides; the existing vendor-symbol table has carried
  the identical limitation since Phase 2 without it ever mattering in
  practice).
- **No `export_kind` column.** `export_kind`'s own docstring
  (`symbols.py:30-41`) already states it "must not become... a stand-in
  for a future intrinsic symbol-type concept" — `source_symbols.kind`
  is exactly that intrinsic concept, kept on its own dedicated,
  purpose-built table rather than retrofitted onto the field the
  existing docstring explicitly protects.

### 3.3 Why a distinct extraction type, not a `kind` field on `symbols.Symbol`

The task's own framing asks this directly. Decision: **a distinct
dataclass/module**, not an intrinsic `kind` field added to
`symbols.Symbol`. Reasoning:

- Every existing call site of `symbols.Symbol` (four extractors, all of
  `filetree.py`'s purpose-annotation logic, every `adapter.symbols()`
  implementation) has no concept of `kind` and would need to either
  populate a meaningless default or be threaded through unnecessarily.
- `Symbol.export_kind`'s docstring already draws this exact line — adding
  `kind` to the same dataclass one field over from a doc comment that
  says "this must never become a kind field" is confusing, not
  economical.
- Reuse happens at the **extraction technique** level (§6), not the
  **dataclass** level — exactly matching the user's own instruction to
  "reuse existing ecosystem extractors where sensible" without forcing
  a shared type onto two genuinely different producers.

## 4. Migration strategy (Phase 76's corrected discipline, not schema-version-triggered destructive migration)

- `_SCHEMA_VERSION`: `"10"` → `"11"`.
- **`source_files`**: existing rows need two new columns
  (`ecosystem`, `content_hash`) added via `ALTER TABLE source_files ADD
  COLUMN ...` — SQLite supports adding a nullable column cheaply and
  safely. **Never drop-and-recreate `source_files`** — it is
  referenced by `uses_edges.source_file_id ON DELETE CASCADE`, and a
  careless recreate would cascade-delete every `uses_edges` row, the
  exact class of destructive-migration risk `decisions/0064` (Phase 76's
  own corrective pass) just fixed for `doc_artifacts`. A new
  introspection-based check — `_source_files_schema_is_current(conn)`,
  checking `PRAGMA table_info(source_files)` for the two new columns,
  mirroring `_doc_artifacts_schema_is_current`'s exact pattern — gates a
  new `_migrate_source_files_columns(conn)` that runs `ALTER TABLE ADD
  COLUMN` only when a column is genuinely missing, decoupled from
  `meta.schema_version`'s own value exactly as `decisions/0064`
  requires. Existing rows get `ecosystem = NULL`/`content_hash = NULL`
  until the next `rebuild_deterministic` call repopulates them for real
  (every real production call path always calls `rebuild_deterministic`
  immediately after `open_graph`, so this transient state is never
  user-visible in practice — same posture `git_topology`'s own
  "not yet indexed" design already established).
- Because `ecosystem` should end up `NOT NULL` for every row `sync`
  actually produces, but `ALTER TABLE ADD COLUMN` in SQLite cannot add a
  `NOT NULL` column without a default to a non-empty table in one step,
  the added column is created nullable at the schema level and
  populated for real by `rebuild_deterministic`'s own unconditional
  `source_files` upsert immediately after — the same "meta.schema_version
  becomes purely informational, updated unconditionally" posture
  `decisions/0064` established. (If investigation at implementation time
  finds SQLite's `ALTER TABLE ADD COLUMN ... NOT NULL DEFAULT ...`
  variant is simpler and equally safe, that is an implementation
  refinement, not a plan change — the constraint on *behaviour* is what
  matters: never drop the table, never lose an existing `uses_edges`
  row.)
- **`source_symbols`**: brand new table, `CREATE TABLE IF NOT EXISTS`
  only — no existing data, no migration risk, identical posture to
  Phase 76's own three new tables.
- **`source_files`/`source_symbols` upsert by natural key** (`path`;
  `(source_file_id, name)` respectively) — **not** cleared-and-reinserted
  like `source_files` is today. This is a deliberate behaviour change
  from `source_files`'s current disposable-every-rebuild treatment,
  needed to satisfy the task's own explicit requirement ("stable enough
  natural keys to support later relationships without unnecessary
  identity churn") and to leave room for a future `source_symbol`-keyed
  enrichment table (not built this phase) the same way
  `vendors`/`symbols` already support `vendor_enrichment`/
  `symbol_enrichment` today. Mirrors `_sync_vendors`/`_sync_symbols`'s
  exact upsert-by-natural-key shape (`graph.py`), not
  `_insert_source_files`'s current delete-then-insert shape. A row whose
  path/name no longer appears in the current rebuild is deleted
  (correctly cascading away any future per-symbol enrichment for
  something that no longer exists) — identical posture to how
  `vendors`/`symbols` already handle removal today.
- **`uses_edges` behaviour is completely unaffected** — same FK, same
  resolution mechanism, strictly more `source_files` rows to resolve
  against, never fewer.
- **`symbols`/`symbol_enrichment`/`vendor_enrichment` behaviour is
  completely unaffected** — no column, constraint, or row in these
  tables changes at all.
- **A project with no `vendor.toml` (0 tracked vendors) still builds
  full first-party `source_files`/`source_symbols` state** — the new
  discovery walk (§6) takes `project_root` only, never `configs`,
  confirmed by design (unlike `resolve_project_usage`, which legitimately
  needs `configs` to filter to *tracked* vendor names).
- `rebuild_deterministic`'s new `source_symbols` parameter defaults to
  `()`, matching `doc_chunks`/`git_repositories`'s own established
  backwards-compatibility precedent for any existing test/caller that
  doesn't pass it.

## 5. Source detection/extraction approach

New module: **`src/codecompass/source_symbols.py`** — mirrors
`usage.py`'s own architectural role (a project-facing counterpart to
`symbols.py`'s vendor-facing extractors), Layer 2 (mechanical
detection, no AI, no shared state).

### 5.1 File discovery — reused walk, broadened prune-set choice verified live

`discover_source_files(project_root: Path) -> list[tuple[str, Ecosystem]]`
walks `project_root` via `filetree.iter_source_files(project_root,
prune_dirs=<project prune set>)`, classifying each file's ecosystem by
suffix (same mapping `usage.detect_imports_for_file` already uses).

**Verified, not assumed, which prune set to reuse**: `filetree.py`'s own
default prune set (`_PRUNE_DIR_NAMES`) excludes `test`/`tests`/
`__tests__`/`fixtures` — correct for rendering a *vendor's* `FILETREE.md`
(tests are noise there), but wrong here: the task explicitly requires
"preserve first-party tests as source." `usage.py`'s own
`_PROJECT_PRUNE_DIR_NAMES` (already used by `resolve_project_usage`)
excludes only build/dependency noise (`node_modules`, `dist`, `build`,
`.git`, `__pycache__`, `.venv`, `venv`, `vendor`) and **does not** prune
tests — confirmed by reading `usage.py`'s own comment, which already
states this exact rationale for the identical reason. **First-party
discovery reuses `usage._PROJECT_PRUNE_DIR_NAMES`**, not
`filetree._PRUNE_DIR_NAMES` — a project's own test file remains a
first-class source file, satisfying this requirement for free via
existing, already-reasoned precedent rather than a new decision.

**Walk-sharing note (implementation-level, not schema-affecting)**:
`resolve_project_usage` already performs an equivalent walk today. The
sync orchestration should walk the project tree once per sync, feeding
both import-usage detection and first-party file/symbol extraction from
that single pass — exact refactor shape left to implementation, but the
requirement (no second full-tree walk) is a plan-level constraint, not
an afterthought.

### 5.2 Symbol extraction — reusing existing ecosystem techniques, verified live

`SourceSymbol` dataclass (new, in `source_symbols.py`):

```python
@dataclass(frozen=True)
class SourceSymbol:
    name: str
    kind: str
    line: int | None
    purpose: str | None = None
```

`extract_source_symbols_for_file(path: Path, ecosystem: Ecosystem) ->
list[SourceSymbol]` dispatches per ecosystem, reusing the **same
underlying scanning technique** each existing `symbols.py` extractor
already uses (AST walk for Python, line-scan for Rust, regex export-scan
for npm) — not calling the existing functions unmodified (their return
type has no `kind`/`line`), but not inventing new parsing infrastructure
either: `ast.iter_child_nodes`/`ast.FunctionDef`/`ast.ClassDef` for
Python, the same `_RUST_PUB_PREFIXES` line-scan for Rust, the same
`_NPM_EXPORT_RE` regex for npm — each now also recording which branch
matched (`kind`) and the node/match's own line number.

**Live-verified before committing to npm/TypeScript support** (a real
finding, not an assumption copied from the task prompt): the existing
`extract_npm_symbols` regex (`_NPM_EXPORT_RE`) is gated to `.d.ts` files
only by `extract_symbols_for_file`'s own dispatcher — but the regex
*itself* has no declaration-file-specific assumption. Tested directly
against a representative regular `.ts` implementation file
(`export function add(...) {...}`, `export class Widget {...}`, a
non-exported function, a non-exported const):

```
Symbol(name='add', purpose='Adds two numbers together.', export_kind='export', note=None)
Symbol(name='Widget', purpose=None, export_kind='export', note=None)
Symbol(name='MAX', purpose=None, export_kind='export', note=None)
```

Correctly extracted every exported declaration (with JSDoc), correctly
skipped both non-exported ones. **npm/TypeScript first-party extraction
is genuinely supported this phase** — for `.ts`/`.tsx`/`.js`/`.jsx`/
`.mjs`/`.cjs` files, matching `_NPM_SOURCE_SUFFIXES` already defined in
`usage.py`, scoped to top-level `export`ed declarations only (the
regex's own existing, accepted scope — a first-party module-private
function is not captured, an honest, disclosed limitation matching this
extractor's existing behaviour for vendors, not a new one introduced
here).

- **Python** (`.py`): `extract_python_source_symbols` — `kind`
  = `"function"` (`FunctionDef`/`AsyncFunctionDef`) or `"class"`
  (`ClassDef`), `line = node.lineno`, `purpose =
  ast.get_docstring(node)`. Top-level only, identical scope to
  `extract_python_symbols`.
- **Rust** (`.rs`): `extract_rust_source_symbols` — `kind` from which
  `_RUST_PUB_PREFIXES` entry matched (`"function"`/`"struct"`/
  `"enum"`/`"trait"`), `line` from the matched line's own position,
  `purpose` from a preceding `///` block, identical scope to
  `extract_rust_symbols`.
- **npm/TypeScript** (`.js`/`.jsx`/`.ts`/`.tsx`/`.mjs`/`.cjs`):
  `extract_npm_source_symbols` — `kind` from which `_NPM_EXPORT_RE`
  alternative matched (`function`/`class`/`interface`/`const`/`type`/
  `enum`), `line` from the matched line's own position, `purpose` from a
  leading JSDoc block. **Exported top-level declarations only** — see
  above.
- **Haskell** (`.hs`): **file recognition only, no symbol extraction**.
  No in-process Haskell parser exists anywhere in this codebase — Phase
  76's own precedent (bare repositories: "declared unsupported, honestly,
  rather than building fallback support with no evidence calling for
  it") applies directly. A recognized `.hs` file still gets a
  `source_files` row (`ecosystem='haskell'`), with zero `source_symbols`
  rows — the CLI (§7) renders this as an explicit, honest "no symbol
  extractor available for this ecosystem" state, never a silent empty
  result indistinguishable from "genuinely has no top-level symbols."
  Building Haskell first-party extraction would require either a new
  in-process parser (out of scope — no evidence justifies the
  investment) or routing through the existing external-adapter-process
  protocol for a *first-party* file, a materially different integration
  shape than the adapter protocol's current vendor-only design —
  explicitly deferred, not fabricated.

## 6. CLI / query design

Two new, additive `query` subcommands — **`query symbol` is completely
unmodified**, confirmed by design: its own `symbol_profile` output has a
`Vendor` column with no first-party equivalent, and unifying the two
would either need a synthetic "self" vendor row (explicitly rejected by
the acceptance test: "no fake/self vendor is required simply to
represent project code") or a schema-breaking column addition to an
existing, stable query. Investigation supports keeping the namespaces
separate, not unifying them.

- **`codecompass query source <path>`** — every first-party fact known
  about one source file: `ecosystem`, whether an extractor exists for it
  (explicit `"no symbol extractor for <ecosystem> yet"` state, not a
  bare empty list, when applicable), its own `source_symbols` (name,
  kind, line, purpose), and its own recorded vendor usage (a
  cross-reference to `uses_edges`, mirroring `query vendor`'s existing
  usage-site rendering) if any. `--json` supported, matching every other
  `query` subcommand.
- **`codecompass query source-symbol <name>`** — every `source_symbols`
  row named `name`, across every first-party file (names aren't
  globally unique across files, same posture `query symbol` already
  has across vendors): name, kind, source file path, line, purpose.
  `--json` supported.
- No special "not yet indexed" handling is needed (unlike Phase 76's
  `query topology`): `source_files`/`source_symbols` populate on
  **every** ordinary `sync`, not an opt-in analysis pass — the existing
  shared `_graph_session`/`_open_graph_or_note` helper every other
  `query` subcommand already uses is sufficient and should be reused
  unmodified, a simpler integration than Phase 76's own.
- New `graph.py` query functions: `source_file_profile(conn, path) ->
  dict | None` and `source_symbol_profile(conn, name) -> list[dict]`,
  mirroring `symbol_profile`'s/`topology_profile`'s own existing shape
  and conventions exactly.

## 7. Relationship to the current roadmap

- **Priority A (task-context completeness)** — this phase's primary
  home, per direct instruction. Directly closes the structural blocker
  `CG-009` named and the concrete mechanism Phase 75's own Ledgerkit
  trial hit (CodeCompass could supply zero context about Ledgerkit's own
  implementation core — `Posting`/`Amount`/`Tag` — because none of it
  was ever indexed as a symbol at all, independent of the `cur:` task's
  own specifics).
- **`CG-009`** — this phase is its direct, evidence-gathering response.
  Closure itself goes through the normal lifecycle (§11's Ledgerkit
  validation feeds `knowledge-curator`/`context-evaluator`, not a
  lead-declared "done because code was added").
- **Priority D (documentation-first downstream workflow)** — §9's
  template design is this priority's **first concrete deliverable**,
  not merely "naturally related." `planning/ROADMAP.md`'s own Priority D
  success criterion ("a downstream user can follow
  research→evidence→design→review→packet→implementation→verification→
  retro→knowledge-update using only already-shipped CodeCompass surfaces
  plus documented convention, no new agent required") is close to a
  verbatim match for what §9 below designs. This phase's own retro
  should flip Priority D's `ROADMAP.md` status cell from "Not yet
  planned" to a link to this plan, per that table's own "How this file
  is kept in sync" rule.
- **Phase 76's own evidence** (narrowly-motivated capabilities
  outperform broad graph expansion, MODERATE advantage — the strongest
  Priority A result to date) directly shaped this phase's own scope
  discipline: first-party *objects* only, relationships explicitly
  deferred to a follow-on (§13), matching the same "narrow, concrete,
  evaluated" shape that produced Phase 76's own result rather than
  Phase 72's originally-anticipated broader trajectory.
- **The previously-recommended "second, differently-shaped Priority A
  Ledgerkit trial"** (Phase 75's own closeout recommendation,
  `planning/CONTEXT.md`'s own still-live, not-yet-phase-numbered item):
  **this phase precedes it; it does not constitute or fully satisfy
  it.** That recommendation specifically named exercising `CG-001`'s own
  "intra-`src`-module" motivating shape — `CG-001` is defined
  (`planning/context-gaps/README.md`) as "a local-code ↔ local-code link
  that is one *feature* spread across files, which the graph does not
  join" (its own worked example: `skill.py` ↔ `graph.skills_index` ↔
  `cli.py::query_skills`). That is squarely a **relationship** between
  first-party objects — this phase's own explicitly-deferred follow-on
  scope (§13), not this phase's own. A `CG-001`-shaped trial is
  structurally impossible to run meaningfully today (there is nothing
  for such a trial to join, since the individual first-party objects
  don't exist as queryable facts yet) and remains impossible until a
  relationship phase exists. What this phase's own §11.2 Ledgerkit
  validation *does* provide is genuine, real, independent Priority A
  evidence from Ledgerkit again — but evaluating `CG-009` specifically,
  not `CG-001`. **Recommendation: the second, `CG-001`-shaped trial
  stays exactly where Phase 75 left it — recommended, live, not yet
  phase-numbered — and should be reconsidered once this phase's own
  follow-on (§13) makes a `CG-001`-shaped task answerable at all.**
  `planning/CONTEXT.md` should say this explicitly, not silently drop
  the recommendation.

## 8. `codecompass-template` — design

Tentative name: `codecompass-template`. A **separate** repository
(design only this phase — not created, not initialized, not pushed).

### 8.1 Purpose and shape

Lets a downstream project adopt the *proven workflow shape* — research/
evidence → plan → design → implement → verify → retro → update knowledge
(`decisions/0060`'s own Scope→Plan→Domain→Design→Implement methodology,
generalized) — without inheriting CodeCompass's own 76-phase history,
specialist-agent roster (12 named roles as of this plan), or
CodeCompass-only knowledge (`planning/learnings/`,
`planning/context-gaps/`, milestone-specific rules, GATE machinery).

### 8.2 Sketch structure (design sketch, not a required literal tree — confirmed against the task's own framing)

```
codecompass-template/
├── LICENSE                    (MIT, §10)
├── README.md                  (what this template is, how to adopt it)
├── CLAUDE.md                  (minimal: plan-before-code, doc-sync, DoD — no GATE/priority/phase-group machinery)
├── vendor.toml                (empty/commented example — CodeCompass populates it via discovery)
├── .gitignore                 (context-graph.db, vendor/, generated Skills/slash-commands — never committed)
├── docs/
│   └── architecture.md        (a starting current-state doc template, not CodeCompass's own content)
├── decisions/
│   ├── README.md              (append-only ADR convention, generic)
│   └── TEMPLATE.md
└── planning/
    ├── ROADMAP.md              (empty phase table + the sync rules, generic)
    ├── CONTEXT.md              (empty current-state skeleton)
    ├── retros/
    │   └── TEMPLATE.md
    ├── knowledge/
    │   └── README.md           (generic "learnings inbox" convention, not CodeCompass's own learnings)
    └── context-gaps/
        └── README.md           (generic "context gap" convention, decoupled from CodeCompass-specific GATE DB/DD language)
```

### 8.3 What is explicitly NOT copied

- The full `.claude/agents/*` specialist roster (12 roles) — the
  template documents the **workflow shape** as plain convention a human
  or any agent can follow with ordinary tools (`query`, generated
  Skills, the graph), not a prescribed agent cast. A downstream project
  that wants a similar agent-led model can build its own roster suited
  to its own scale, same as CodeCompass's own
  `planning/v1-redefinition/agent-led-development.md` is CodeCompass-
  specific, not a universal prescription.
- Historical phase machinery, milestone-group/stage-letter naming,
  GATE-DA/DB/DD-style deliberation gates — CodeCompass-specific process
  scar tissue, not a reusable convention.
- `planning/learnings/inbox.md`/`promoted.md`'s own **content**
  (CodeCompass's own 65 learnings) — only the *convention* (a
  candidate→promoted lifecycle) is packaged, as an empty, documented
  template.
- Any generated artifact: `context-graph.db`, `vendor/<name>/`,
  generated Skills/slash-commands, `.claude/skills/codecompass*/`. A
  clean template checkout produces none of these — they appear only
  after a downstream project runs `codecompass init`/`sync` itself. This
  is the acceptance test's own architectural check (§11.1) applied to
  the template's own repository hygiene too.

### 8.4 What Priority D productisation actually needs

Per the task's own explicit steer ("prefer documented convention/
templates over building new runtime tooling unless evidence shows
tooling is required") and per `planning/ROADMAP.md`'s own Priority D
open question ("how much of this actually needs product tooling vs.
remaining a documented convention," `ledgerkit-stage-c-learnings.md`
#8): **investigation finds no evidence any new runtime tooling is
required.** Every mechanism the template packages already exists and
ships today as ordinary CodeCompass surfaces a downstream project gets
for free once it installs the tool: `codecompass init`/`sync`/`query`,
generated per-vendor Skills, the `/discovery` slash command, and — after
this phase — `query source`/`query source-symbol`. The template's own
job is **documentation and empty scaffolding only** — no new CLI
command, no new Python module, nothing under `src/codecompass/` is
required to make the template real. This directly and cheaply confirms
Priority D's own success criterion.

## 9. MIT licensing / provenance approach

**Fixed requirement, applied, not reconsidered**: `codecompass-template`
ships its own `LICENSE` (MIT) and its reusable material is authored to
be genuinely, unambiguously MIT-compatible.

**Legal note, for clarity, not as license to skip the discipline
below**: CodeCompass has exactly one copyright holder to date
(`decisions/0055`'s own research, unchanged) — that same person could,
strictly speaking, dual-license their own original text under both
GPL-3.0-or-later and MIT without rewriting a word, since dual-licensing
one's own original work carries no incompatibility risk. **This plan
does not rely on that fact.** The task's own instruction is to author
template material as fresh MIT content and rewrite CodeCompass-derived
wording from first principles — followed here for a concrete, practical
reason beyond the legal minimum: it keeps `codecompass-template`'s own
provenance unambiguous for every downstream adopter (GPL, permissive,
and proprietary projects alike), with no reader ever needing to trace
back through CodeCompass's own licensing history or the specific
authorship chain to trust the template's MIT terms.

Applying the task's own required identification, file by file:

| Template file | Provenance | Treatment |
|---|---|---|
| `LICENSE` (MIT) | New — standard MIT text | Authored fresh, standard boilerplate |
| `README.md` | New | Fresh prose describing the template's own purpose/adoption steps — no CodeCompass README text reused |
| `CLAUDE.md` | Rewritten from principles | The **general workflow concept** (plan-before-code, same-commit doc-sync, retro-on-completion) is a process idea, not copyrightable expression — the template's own version is freshly worded for a minimal, generic project, not CodeCompass's own 8-section, phase/priority/gate-laden text |
| `vendor.toml` | New | An empty/commented example — `vendor.toml`'s own schema is CodeCompass's own config format, not prose; a commented example file is trivial, functional boilerplate, not a copyrightability question |
| `.gitignore` | New | A generic ignore-list; CodeCompass's own `.gitignore` entries for `vendor/`/`context-graph.db`/generated Skills are facts about file paths, not protectable expression, but the file itself is authored fresh rather than copied verbatim |
| `docs/architecture.md` | New | A minimal starting-point template (headings + "describe current state here" guidance), not any of CodeCompass's own actual architecture content |
| `decisions/README.md`, `decisions/TEMPLATE.md` | Rewritten from principles | The append-only-ADR **convention** is a process idea (already documented as reusable in CodeCompass's own `CLAUDE.md` §2, itself following the widely-used public ADR convention popularized by Michael Nygard — not CodeCompass's own invention to begin with); the template's own README/TEMPLATE text is freshly worded, shorter, with no CodeCompass-specific numbering history or cross-references |
| `planning/ROADMAP.md`, `planning/CONTEXT.md` | Rewritten from principles | The **shape** (a phase-status table; a session-resumption current-state doc) is reused as a documented pattern; the actual template file ships empty/skeletal, with fresh instructional prose, not CodeCompass's own accumulated ~110-line current-state summary or its own historical sync rules |
| `planning/retros/TEMPLATE.md` | Rewritten from principles | CodeCompass's own retro template's **section list** (where we are / goal / delivered vs planned / worked / didn't work / lessons / feedback / candidate learnings / where we're going) is a reusable structural idea; the template's own version is freshly worded and shorter (no candidate-learning-lifecycle cross-references CodeCompass's own template carries) |
| `planning/knowledge/README.md`, `planning/context-gaps/README.md` | Rewritten from principles | The candidate→promoted lifecycle **concept** is reused; wording, GATE-DB/DD terminology, and every CodeCompass-specific cross-reference is dropped and rewritten generically |

**General principle applied throughout**: general workflow ideas, process
shapes, and documented conventions are not copyrightable expression and
are freely reusable; CodeCompass's own specific prose, phase-numbering
history, internal cross-references, and accumulated project-specific
detail are copyrightable expression and are never copied — every
template file is freshly authored, shorter, and generic.

**No generated CodeCompass artifact is ever distributed with the
template** — confirmed by design (§8.3), not merely asserted: the
template's own `.gitignore` excludes exactly the paths a real
`codecompass init`/`sync` run would produce, and the template repository
itself never runs `codecompass sync` before being published, so no such
file is ever created inside it to begin with.

**Provenance documentation for future contributors**: `codecompass-
template`'s own `README.md` states explicitly, near the top: this
template is MIT-licensed and independently authored; it is designed to
be adopted by projects under any license, including proprietary ones;
it is maintained alongside CodeCompass (GPL-3.0-or-later) but is not
itself a redistribution of CodeCompass's own source or documentation. A
short note in CodeCompass's own `README.md`/`ai-docs/README.md`
(current-truth docs, updated same-commit per `CLAUDE.md` §2) cross-links
the template and states the same license boundary, so a reader of either
repository sees the separation stated from both sides.

**Final architecture, preserved exactly as required**:

```
CodeCompass implementation   — GPL-3.0-or-later
codecompass-template         — MIT
downstream project           — chooses its own compatible license
```

## 10. Validation fixtures — three real validations required

All three follow the existing scratch-clone discipline
(`planning/v1-redefinition/reference-project-protocol.md` §2.2): a
project fixture is cloned/created into a scratch location outside this
repository, never added to CodeCompass's own tree/`vendor.toml`/
`context-graph.db`, and fully cleaned up afterward (§16).

### 10.1 Template / zero-vendor project — the architectural acceptance test

- Build a small, real (not synthetic-for-testing-only) source tree from
  the `codecompass-template` design (§9) in a scratch directory — since
  the real repository doesn't exist yet, this is a scratch scaffold
  matching §9's own sketch, not a clone of a published repo.
- Add a handful of real, representative first-party Python files (a
  module with 2-3 functions/classes, a test file) — **zero entries in
  `vendor.toml`**.
- Run `codecompass sync` (editable install).
- **Verify**: `source_files` rows exist for the added files;
  `source_symbols` rows exist for their top-level functions/classes;
  `codecompass query source <path>` and `query source-symbol <name>`
  both return real data; `vendors`/`symbols` tables are empty (0 rows) —
  **no fake/self vendor row was created anywhere**, confirmed by direct
  `sqlite3` inspection of `context-graph.db`, not only CLI output.

### 10.2 Ledgerkit validation — directly tests whether `CG-009` is resolved

- Clone Ledgerkit fresh at plan-time-unknown-but-implementation-time-
  resolved HEAD (never hardcode Phase 75's own pinned `6c90b4c` as
  current — **re-resolve `Posting`/`Amount`/`Tag`'s real current file
  paths at clone time**, since Ledgerkit's own development has continued
  since Phase 75). Last-known locations from `CG-009`'s own evidence:
  `ledgerkit/models.py::Posting`, `::Amount`, `ledgerkit/query/ast.py::Tag`
  — confirm these still hold, or find their real current location, at
  implementation time.
- Run `codecompass sync` against the fresh clone (0 or whatever vendors
  Ledgerkit currently tracks — irrelevant to this test, since first-party
  discovery never consults `vendor.toml`).
- **Verify**: `codecompass query source-symbol Posting` / `Amount` /
  `Tag` (or their real current names) return real, correct data —
  right file, right kind, right line, docstring if present.
- **Do not close `CG-009` because this test passes.** Feed the result
  into the normal context-gap lifecycle: an independent
  `context-evaluator` (or `knowledge-curator`, whichever this project's
  process currently uses for gap-closure evidence — confirm against
  `planning/context-gaps/README.md`'s own "How it feeds the gates"
  section at closeout time) reviews the evidence and makes the actual
  status-transition call, the same discipline every prior gap closure
  in this project has followed.

### 10.3 CodeCompass dogfooding

- Run the feature against CodeCompass's own working tree (already
  installed, no clone needed — this repository *is* the fixture).
- Resolve real, current first-party symbol names at implementation time
  (not hardcoded from this plan) — candidates already known to exist as
  of this plan's own writing: `git_topology.detect_git_topology`,
  `sync.rebuild_project_graph` (confirm these are still the real,
  current names/locations when implementation actually runs `sync`).
- **Verify**: both become queryable via `query source-symbol`, with
  correct file/line/kind, alongside CodeCompass's own already-tracked
  vendor symbols (`anthropic`, `rich`, `typer`, `pipdeptree`) — both
  surfaces coexisting in the same `context-graph.db`, confirming no
  interference between vendor and first-party symbol namespaces.

## 11. Independent evaluation methodology

A lightweight Priority A evaluation, reusing the seed-then-fork fixture
design and pre-dispatch equivalence check Phase 76's own third amendment
established (`planning/phase-76-git-repository-topology.md` §15) — the
same evaluation shape as Phase 76's own MODERATE-advantage trial, not a
new methodology invented for this phase.

- **Fixture**: the §10.1 template project (or another clean, small,
  genuinely representative fixture — Ledgerkit is a second, valid
  option if a suitably self-contained task exists there) — normalized
  once, forked into baseline-clone/treatment-clone, scenario constructed
  identically-but-independently in each after the fork.
- **Task shape** (per direct instruction): locate where a feature is
  implemented, identify its principal first-party symbols/files, and
  identify where an external dependency is used.
- **Baseline**: normal repository/tool access (grep, file reads,
  `--help`).
- **Treatment**: same access, plus `codecompass query source`/
  `query source-symbol`/`query symbol` for the task.
- **Measured** (exactly as instructed, no token-savings claim unless
  tokens are actually counted): factual completeness (did it find the
  real implementation files/symbols); missed implementation files/
  symbols (a concrete, countable miss list); count of exploratory
  reads/searches/tool calls in each arm; whether the treatment arm did
  *additional* repository exploration after consulting CodeCompass
  context (a signal the context alone wasn't sufficient, matching
  Phase 75's own `L-027` diligence-variance discipline); first-pass
  correctness; review/correction cycles, where practically observable.
- **Evaluator**: `context-evaluator`, inspecting the target directly
  (never trusting either arm's own report), per this project's
  established, repeatedly-validated protocol — not a new evaluation
  mechanism.
- **Read-scope symmetry** stated explicitly in the dispatch prompt for
  both arms (`L-062`, `reference-project-protocol.md` §2.2) — and, per
  `L-064`/`L-065`'s own hard-won lesson, **any prior agent's report
  needed by a downstream dispatch is written to disk immediately on
  receipt**, before the next dispatch prompt is drafted (`planning/
  agent-led-workflow.md` step 5's own new rule, landed at Phase 76's
  corrective pass) — applied here as the first real exercise of that
  rule since it landed.

## 12. Ecosystem scope summary (no fabricated symmetry)

| Ecosystem | File recognition | Symbol extraction | Basis |
|---|---|---|---|
| Python (`.py`) | Yes | Yes — function/class, top-level | `ast`-based, reuses `extract_python_symbols`'s own technique |
| Rust (`.rs`) | Yes | Yes — function/struct/enum/trait, top-level | Line-scan, reuses `extract_rust_symbols`'s own technique |
| npm/TypeScript (`.js`/`.jsx`/`.ts`/`.tsx`/`.mjs`/`.cjs`) | Yes | Yes — **exported top-level declarations only** | Regex reuse of `_NPM_EXPORT_RE`, **live-verified** against a real `.ts` file (§6) — a genuine, confirmed capability, not an assumption |
| Haskell (`.hs`) | Yes | **No — explicitly unsupported, not fabricated** | No in-process parser exists; external-adapter-process integration for first-party files is a materially different, out-of-scope undertaking |

## 13. Likely follow-on phase (explicitly deferred, not scoped or promised here)

Relationships **among** first-party objects this phase creates — real
opportunities recorded for a future phase to scope for real, once this
phase's own evaluation (§11) shows which are actually valuable:

- `source_file → imports → source_file` (first-party import graph —
  the natural next step once files are objects; likely reuses
  `usage.py`'s own already-proven per-ecosystem import-parsing
  techniques, now pointed at first-party targets instead of vendor
  names).
- `source_symbol → references/calls → source_symbol` (the actual
  call-graph capability explicitly out of scope this phase).
- `test → tests → source_symbol/source_file` (a real, concrete, and
  probably valuable next step, since this phase already keeps first-
  party tests as source rather than pruning them — the natural next
  question is *what does a given test actually exercise*).
- `doc → documents → source_symbol` (extending `doc_mapping.py`'s
  already-proven `documents_edges` mechanism, currently vendor-symbol-
  only, to first-party symbols too).
- This is very likely the shape that finally makes a genuine
  `CG-001`-shaped trial possible (§7) — a strong hint for that
  follow-on's own eventual scoping, not a commitment made here.

No detailed scope, schema, or timeline is assigned to any of these here
— per direct instruction, this section exists to record the
opportunity, not to plan it.

## 14. Files expected to change

- **New**: `src/codecompass/source_symbols.py`.
- **`src/codecompass/graph.py`**: `_SCHEMA_VERSION` "10"→"11";
  `source_files` table gains `ecosystem`/`content_hash` columns (ALTER,
  not recreate); new `source_symbols` table; `SourceFileRow` extended
  with `ecosystem`/`content_hash`; new `SourceSymbolRow` dataclass;
  `_source_files_schema_is_current`/`_migrate_source_files_columns`
  (new, mirroring Phase 76's `_doc_artifacts_schema_is_current`
  pattern); `_sync_source_files`/`_sync_source_symbols` (new,
  upsert-by-natural-key, mirroring `_sync_vendors`/`_sync_symbols`);
  `rebuild_deterministic` gains a `source_symbols` parameter (default
  `()`); new `source_file_profile`/`source_symbol_profile` query
  functions.
- **`src/codecompass/sync.py`**: `rebuild_project_graph` — replace the
  vendor-usage-gated `source_file_paths` collection with a full
  first-party discovery pass (`source_symbols.discover_source_files`),
  feeding both `source_file_rows`+`source_symbol_rows` and the existing
  `uses_edges` detection (now resolved against the broader
  `source_file_ids` mapping); walk-sharing refactor with
  `usage.resolve_project_usage` per §6's own note.
- **`src/codecompass/cli.py`**: new `query source`/`query source-symbol`
  commands + rendering functions.
- **`src/codecompass/skill.py`**: generated tool Skill gains the two new
  command lines + the two new table names (matching Phase 76's own
  precedent for `query topology`).
- **`docs/cli-reference.md`**: new `query source [--json]`/
  `query source-symbol [--json]` sections.
- **`architecture/context-graph-schema.md`**: `source_files`/
  `source_symbols` sections updated/added; the current, stale
  description ("Every project source file with at least one detected
  `uses_edges` row") corrected.
- **`architecture/overview.md`**: a new "First-party source awareness"
  subsection, matching the existing "Git repository topology" one's own
  shape.
- **`architecture/module-map.md`**: add `source_symbols.py` to Layer 2's
  module list. **Also fix a pre-existing, unrelated drift found while
  reading this file for this plan**: it currently omits `git_topology.py`
  entirely (added Phase 76) — worth fixing in the same touch, flagged
  here rather than silently left for a future phase to rediscover.
- **`decisions/0065-<slug>.md`** (new ADR — table design, migration
  approach, ecosystem-scope decisions, npm/TS live-verification finding).
- **`README.md`, `ai-docs/README.md`**: new capability bullets + the
  `codecompass-template` cross-link/license-boundary note (§9).
- **`CHANGELOG.md`**: `[Unreleased]` entry.
- **`planning/ROADMAP.md`**: new Phase 77 row; Priority A's own status
  cell updated; Priority D's status cell flipped from "Not yet planned"
  to link this plan (per §7).
- **`planning/CONTEXT.md`**: current-state update, including the
  explicit "precedes, does not replace" note on the second Ledgerkit
  trial (§7).
- **`planning/context-gaps/inbox.md`**: `CG-009` gets a triage note once
  §10.2's evidence exists (closeout time, not now).

## 15. Tests

- **New `tests/test_source_symbols.py`**: file-discovery walk (prune-set
  behaviour, including the explicit "tests are kept" case), per-ecosystem
  extraction (Python/Rust/npm real fixtures, including the npm
  export-vs-non-export distinction verified live in §6), the Haskell
  file-recognized-no-symbols case, ecosystem classification by suffix
  independent of any `vendor.toml` content.
- **`tests/test_graph.py`** additions: schema migration safety (the
  `_migrate_source_files_columns` equivalent of Phase 76's own migration
  regression test — an existing pre-migration fixture's `uses_edges` rows
  must survive); `source_files`/`source_symbols` upsert-by-natural-key
  behaviour (an unchanged path/name keeps its `id` across two
  `rebuild_deterministic` calls; a removed one is deleted); new
  `source_file_profile`/`source_symbol_profile` query function tests.
- **`tests/test_sync.py`** additions: a real-call-site test (per
  `CLAUDE.md` §1's L-021 rule) exercising `rebuild_project_graph`
  end-to-end with a real fixture tree and confirming `source_files`/
  `source_symbols` are genuinely populated — not only the extraction
  functions in isolation; a **zero-vendor** real-call-site test,
  confirming first-party state builds with an empty `vendor.toml`.
- **`tests/test_cli.py`** additions: `query source`/`query source-symbol`
  — found/not-found/`--json` cases, the Haskell "no extractor" rendering
  case.
- Full existing suite (694 tests as of Phase 76's own close) must
  continue to pass unmodified in substance — this phase adds no change
  to any existing vendor/symbol/uses_edges behavior.

## 16. Documentation / ADR requirements

- `decisions/0065` (new ADR, per `CLAUDE.md` §2 — a genuinely
  non-obvious tradeoff: separate-table vs. nullable-FK, upsert-by-
  natural-key vs. clear-and-reinsert, npm/TS scope decision with its
  live-verification evidence, Haskell's explicit non-support).
- `docs/`, `architecture/` updates per §14, same commit as the code
  (`CLAUDE.md` §2).
- An independent `docs-reconstructor` per-phase drift audit before
  closeout (`CLAUDE.md` §5).
- `codecompass-template`'s own design content (§8-§10) is fully
  contained in this plan file — no separate design doc needed until the
  repository itself is actually created (a future phase's own scope).

## 17. Rollback / cleanup requirements

- Every scratch clone/fixture created for §10's three validations is
  built outside this repository (scratchpad or a sibling directory,
  never inside `codecompass`'s own tree, never added to `vendor.toml`)
  and is fully deleted once its validation completes — matching
  `reference-project-protocol.md` §2.2 exactly, and Phase 76's own
  mandatory-cleanup precedent for its disposable worktree/clone.
- No git worktree, branch, or remote is created against this repository
  itself for this phase's own validation work.
- The `codecompass-template` design itself creates no artifact anywhere
  this phase — confirmed by its own non-goal (§2): no repository
  created, no files written outside this plan document and (at
  implementation time) this project's own `planning/`/`architecture/`/
  `docs/`/`decisions/` updates.
- A migration-safety test fixture (an old-schema `.db` file built for
  the `_migrate_source_files_columns` regression test, §15) is an
  in-repository *test* fixture, not a scratch clone — no special cleanup
  beyond the test suite's own normal `tmp_path` discipline.

## 18. Human decision gates

**None identified.** Candidates considered and resolved by evidence
rather than escalated:

- *Separate table vs. nullable `vendor_id`* — resolved by the migration-
  risk argument (§3), not merely the semantic one the task already
  anticipated; both point the same direction, no genuine tension.
- *Whether npm/TypeScript is in scope* — resolved by live verification
  (§6), not assumption; the evidence answered the question the task
  itself flagged as open.
- *GPL/MIT content separation policy* — the task itself already fixed
  the policy (rewrite from principles, don't copy); this plan applies it
  file-by-file (§9), it does not need to re-decide it.
- *CLI command naming* — the task explicitly delegated this choice
  ("may change if existing conventions suggest something better");
  `query source`/`query source-symbol` directly match the existing
  `query vendor`/`query symbol` naming convention, no escalation needed.
- *Whether this phase replaces the second Ledgerkit trial* — resolved by
  direct comparison against `CG-001`'s own documented scope (§7); a
  reasoned "precedes, does not replace" conclusion, not an
  irresolvable ambiguity.
- *Actually creating/publishing `codecompass-template`* — not a planning
  gate (no action is taken now); creating and pushing a new external
  repository is a hard-to-reverse, externally-visible action that will
  need its own explicit confirmation at the point implementation
  actually reaches it, per this session's own standing git-safety
  norms — noted here so it isn't forgotten, not escalated now.

## 19. Implementation sequence (for the eventual implementation phase, not run now)

1. `source_symbols.py` (discovery + per-ecosystem extraction + tests) —
   verifiable in complete isolation from the graph.
2. `graph.py` schema/migration/query-function changes + migration
   regression test.
3. `sync.py::rebuild_project_graph` wiring (real-call-site test,
   zero-vendor real-call-site test).
4. `cli.py` query commands + `skill.py` Skill update + CLI tests.
5. Docs/ADR/architecture updates, same commits as the code they
   describe.
6. §10.1 template/zero-vendor validation (architectural acceptance
   test) — first, since it's the cheapest and most direct proof the
   design works before spending effort on the other two.
7. §10.3 CodeCompass dogfooding validation — second, no external clone
   needed.
8. §10.2 Ledgerkit validation — third, the one requiring a fresh
   external clone and path re-resolution.
9. §11 independent task-context evaluation.
10. `CG-009` triage (not closure-by-fiat) using §10.2's evidence.
11. Full closeout sequence per `CLAUDE.md` §5/`planning/
    agent-led-workflow.md`'s corrected 14 steps (as amended by Phase
    76's own corrective pass): docs-maintainer → docs-reconstructor
    drift audit → interim `roadmap-context-curator` reconciliation →
    retro → `knowledge-curator` triage → independent
    `release-phase-auditor` → only-on-PASS final `roadmap-context-
    curator` reconciliation (scoped per `CLAUDE.md` §5's own narrow
    three-target exemption) → push.

## 20. Verification commands

```bash
.venv/bin/pytest -q
.venv/bin/ruff check .
python3 scripts/check_user_docs.py --strict
python3 scripts/check_knowledge_base.py
```

Plus the three live validations (§10) and the independent evaluation
(§11) — none of these are mechanical checks a script can run; each
requires a real fixture and, for §10.2/§11, real external clones.

## 21. Definition of Done

Per `CLAUDE.md` §5, unabridged: code implemented; plan's own
verification (§20) passes; `docs/`/`architecture/`/`decisions/` updated;
independent `docs-reconstructor` drift audit finds `NO DRIFT`; changelog
entry added; `planning/CONTEXT.md` reflects the new state; a substantive
phase retro exists; candidate learnings (including anything this phase's
own evaluation surfaces) triaged by `knowledge-curator`; `CG-009` triaged
(promoted/closed/retained — never closed by lead assertion alone) using
real evidence from §10.2; a `context-evaluator` report exists and is
linked for §11's own evaluation; independent `release-phase-auditor`
pass (`PASS`/`PASS WITH NON-BLOCKING OBSERVATIONS`); only then does
`planning/ROADMAP.md` mark Phase 77 `done`, via a genuinely fresh
`roadmap-context-curator` dispatch, scoped per `CLAUDE.md` §5's own
narrow terminal-reconciliation exemption (§0's own corrected rule,
verified still consistent across `CLAUDE.md`/`planning/
agent-led-workflow.md`/`.claude/agents/roadmap-context-curator.md` at
the point this phase actually closes). All disposable scratch
clones/fixtures (§17) confirmed cleaned up before the phase is marked
done. `codecompass-template` remains **undesigned-beyond-this-plan** —
not created — until a future phase explicitly takes that up.
