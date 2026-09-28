# 0065. First-party source is language-classified (not ecosystem-classified), occurrence-identified (not name-identified), and honestly graded by extraction fidelity

## Status

Accepted (2026-09-29).

## Context

Phase 77 (`planning/phase-77-first-party-source-and-template.md`) makes
a project's own first-party source files and top-level implementation
symbols durable, queryable `context-graph.db` objects, independent of
`vendor.toml` — closing `CG-009` ("a project's own first-party classes/
functions are not queryable as symbols" — `symbols.vendor_id` is
structurally `NOT NULL`, and `source_files` was populated only from
detected vendor-import sites).

Five genuinely non-obvious design questions came up during planning and
two rounds of direct review, recorded here rather than left as implicit
code-level choices — the same discipline `decisions/0063` established
for Phase 76.

## Decision

**1. `source_symbols` is a new, separate table — not a nullable
`symbols.vendor_id`.** A vendor symbol answers "what does this
dependency's API surface offer"; a first-party symbol answers "what does
this project itself implement." Conflating them would force every
future vendor-symbol field to apply ambiguously to both kinds or grow a
second discriminator anyway. More concretely: SQLite cannot relax a
column's `NOT NULL` constraint via `ALTER TABLE` — doing so would
require the same drop-and-rebuild-with-data-copy shape `decisions/0064`
just replaced for `doc_artifacts` specifically because it was a real,
demonstrated risk. A fully separate table needs only `CREATE TABLE IF
NOT EXISTS` — no existing row is ever touched, no destructive-migration
risk exists at all.

**2. A first-party *language*, not a reused dependency *package
ecosystem*.** `core.Ecosystem` has exactly one value (`NPM`) covering
both JavaScript and TypeScript dependencies identically — correct for a
package manager, wrong for classifying a project's own source: a `.js`
file has no `interface`/`type` construct, a `.ts` file does, and
first-party symbol-*kind* extraction genuinely differs between them.
`source_symbols.Language` (`python`/`rust`/`javascript`/`typescript`/
`haskell`) is a new, narrow concept defined in `source_symbols.py`
itself, not `core.py` — this module is its only consumer today;
promoting it to `core.py` is a trivial future move if a second consumer
emerges, not preemptively done here.

**3. `source_files`'s four new columns (`language`, `content_hash`,
`symbol_index_status`, `symbol_index_diagnostic`) are nullable
identically on a fresh and an upgraded database — no exception, no
transitional `NOT NULL`.** An earlier design considered `NOT NULL` for a
freshly-created schema while an upgraded database would carry `NULL`
until repopulated — direct review correctly rejected this as an
unjustified fresh/upgraded divergence. The actual contract: `NULL` means
unresolved/legacy; a genuinely Phase-77-aware `sync` always populates
all four for every row it produces. Verified directly (`test_graph.py`):
`PRAGMA table_info(source_files)` returns identical column definitions
whether the database was created fresh or migrated from a pre-Phase-77
shape.

**4. Symbol identity is occurrence-based — `UNIQUE(source_file_id, name,
kind, line)`, `line NOT NULL` — not name-only.** Live-verified, not
assumed: a real `@typing.overload`-stacked Python function and a real
overloaded TypeScript function declaration each produce three
same-named, same-kind declarations at three distinct lines. A
name-only natural key would raise `sqlite3.IntegrityError` on the very
first genuine overload any `codecompass sync` encountered — function
overloading is ordinary, common code, not a hypothetical edge case. The
logical-symbol/collapse alternative (merge same-name declarations into
one row, pick a winner) was rejected: overloads are not duplicate facts
to be merged with an arbitrary "which signature wins" rule — they are
multiple, individually real declarations, and collapsing them would
discard real information a caller asking "what does line 43 declare"
deserves a real answer to. `line NOT NULL` follows directly: a symbol's
identity is partly defined by its own location, so a location-less
occurrence is a contradiction in terms — an extractor unable to
determine a line for a candidate does not emit a row for it at all.

**5. `exposure` is a five-value, genuinely cross-language
classification (`public`/`restricted`/`internal`/`conventional_private`/
`unknown`) — not a public/private binary.** An initial binary design was
itself too simplistic once Rust's real three-tier visibility model is
considered: `pub(crate)` is neither "public" (it isn't visible outside
the crate) nor "private" (it *is* visible to the rest of the crate) —
collapsing it into either would misrepresent a real, distinct concept.
Live-verified against eight representative Rust declarations (bare
`pub`, all three `pub(...)` forms, and three no-modifier forms), all
eight classified correctly by one regex capturing the full modifier
text. Python's leading-underscore convention maps to
`conventional_private` — deliberately distinct from `internal` (which
means a language itself enforces non-visibility): a naming *convention*
a determined caller can freely ignore is not the same fact as a
compiler/runtime-enforced boundary, and conflating them would overstate
Python's own guarantee. JS/TS maps `export` to `public`, its absence to
`internal` (no `restricted`-equivalent tier exists for these languages).
`unknown` is reserved for a future, less-certain extractor — not
actually produced by any extractor this phase ships. Recorded as a
separate property, never used to filter a symbol out of the table:
first-party extraction answers "what does this project implement," not
"what public API does this dependency expose" — `export_kind`'s own
docstring already states it must not become a stand-in for an intrinsic
symbol-type/visibility concept, and `exposure` is exactly that concept,
kept on its own dedicated table rather than retrofitted onto the field
that docstring explicitly protects.

**6. Extraction fidelity is honestly graded — `indexed` vs.
`indexed_partial`, not one undifferentiated "success" state.** Python's
`ast`-based extraction is a real structural parser (`indexed`);
Rust/JS/TS's line-scan/regex techniques are coarse heuristics
(`indexed_partial`) — a multi-line signature, an unusual formatting
style, or (rarely) a false match inside a string/comment can defeat
them, the same honest limitation the pre-existing vendor extractors
already carry, now surfaced rather than implied away. `unsupported`
(Haskell — no in-process parser exists), `parse_error` (Python-specific
— `ast.parse` raising `SyntaxError`; the coarse techniques have no real
parse step to fail structurally), and `unreadable` (any language) are
distinguishable failure states — never a bare empty `symbols` list
standing in for more than one real cause. Modeled directly on
`git_topology.RepositoryTopology`'s own status+reason+data shape, not a
new pattern invented for this phase.

**7. A project-level `meta.source_index_version` marker, distinct from
per-file `symbol_index_status`.** An upgraded pre-Phase-77 database can
have `source_files`/`source_symbols` gain their new schema (via
migration) without ever being repopulated by a Phase-77-aware `sync` —
in that state, `source_symbols` is genuinely, structurally empty, and
`query source-symbol Posting` returning "not found" would be
indistinguishable from a real, freshly-indexed project genuinely lacking
that symbol. Directly mirrors `meta.git_topology_status`'s own
absence-means-never-synced precedent: a plain version marker (`"1"`
today, not a multi-state status enum — first-party discovery has no
"could the structure be enumerated at all" failure mode the way Git
topology detection does), written unconditionally whenever a genuinely
Phase-77-aware rebuild runs, regardless of whether any first-party files
were found. `query source`/`query source-symbol` check for this key's
absence before ever reading `source_files`/`source_symbols`, remaining
read-only throughout (never invoking a rebuild).

**8. `query source`/`query source-symbol` stay structurally separate
from `query symbol`.** `symbol_profile`'s own output has a `Vendor`
column with no first-party equivalent; unifying the two would need
either a synthetic "self" vendor row (explicitly rejected — no fake
vendor is created to represent a project's own code) or a schema-
breaking change to an existing, stable query. The vendor-vs-first-party
axis is real, not arbitrary.

**9. Haskell remains file-recognized, symbol-extraction-unsupported.**
No in-process Haskell parser exists anywhere in this codebase; building
one, or routing first-party files through the existing
external-adapter-process protocol (currently vendor-only), is a
materially larger undertaking no evidence justifies this phase. A
recognized `.hs` file still gets a `source_files` row
(`symbol_index_status='unsupported'`), never a fabricated or silently
dropped result.

## Alternatives considered

- **Reuse `core.Ecosystem` for `source_files.language`.** Rejected — a
  real ontology mismatch (JS/TS collapse), not merely a naming
  preference; see point 2.
- **A name-only `UNIQUE(source_file_id, name)` symbol key.** Rejected —
  live-verified to crash on genuine, ordinary overloaded declarations;
  see point 4.
- **A binary `public`/`private` exposure model.** Rejected — cannot
  correctly represent Rust's real three-tier visibility without
  misrepresenting `pub(crate)`; see point 5.
- **Treating `indexed_partial` results as equally complete to `indexed`
  ones.** Rejected — a real, material fidelity difference between a
  structural parser and a coarse heuristic that the original design
  implicitly hid; see point 6.
- **Skipping a project-level index-version marker, relying on per-file
  `symbol_index_status` alone.** Rejected — a whole-project "has
  indexing ever run" fact and a per-file "what happened when it did"
  fact answer different questions; an upgraded-but-never-resynced
  database has no per-file rows to check in the first place.

## Consequences

- Schema version `"10"` → `"11"`; `source_files` gains four nullable
  columns, one new `source_symbols` table, one new `meta` key. No change
  to any vendor-facing table's columns or constraints.
- `_migrate_source_files_columns` (introspection-based, `ALTER TABLE ADD
  COLUMN` only, never drop/recreate) joins this project's existing
  migration-safety discipline (`decisions/0064`) — `source_files.id` is
  referenced by `uses_edges.source_file_id ON DELETE CASCADE`, so a
  careless recreate would have cascaded away every usage edge.
- `codecompass query source [--json]`/`query source-symbol [--json]` are
  new, permanent CLI surfaces; `.claude/skills/codecompass/SKILL.md`'s
  generated content names them unconditionally.
- `usage.resolve_project_usage` and `source_symbols.discover_source_files`
  each walk the project tree once, independently — a known, accepted
  minor inefficiency, not merged in this phase since correctness doesn't
  depend on it and doing so would touch `usage.py`'s own well-tested,
  unrelated walk logic for a performance-only gain no evidence yet calls
  for.
- `CG-009` is not closed by this ADR or by this phase's own code landing
  — closure goes through the normal context-gap lifecycle, using real
  Ledgerkit validation evidence (`planning/phase-77-first-party-source-and-template.md`
  §10.2), the same discipline every prior gap closure in this project
  has followed.
