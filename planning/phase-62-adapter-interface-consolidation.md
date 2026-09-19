# Phase 62: Adapter-interface consolidation — plan

**Status:** done (2026-09-19). `CG-008` closed. Implemented per the
amendment below; see `planning/retros/phase-62-adapter-interface-consolidation.md`
(retro), `planning/retros/_drift-audit-phase-62.md` (docs-reconstructor:
NO DRIFT), and `planning/retros/_audit-phase-62.md` (release-phase-auditor:
PASS WITH NON-BLOCKING OBSERVATIONS) for the full closeout record.

**Amended 2026-09-19** (direct user instruction, before implementation
began — scope, acceptance criteria, migration approach, caching design,
real `hledger` validation, and the `CG-008` objective are all preserved
unchanged; this amendment is one targeted semantic refinement, not a
redesign): the new core-model field this plan widens `Symbol`/`SymbolRow`
with is **renamed from `kind` to `export_kind`**, and is documented as
holding **export/exposure status**, deliberately distinct from a
symbol's own **intrinsic type**. `"export"`/`"reexport"`/`"undetermined"`
describe *how confidently an entry is known to be part of the public
surface*, not *what kind of thing the symbol is* — a distinction that
matters the moment a future adapter (the COBOL/mainframe case
`decisions/0056`/`0057` already name as this architecture's own
motivating future scenario) needs to represent real intrinsic-type
values (`program`, `paragraph`, `section`, `copybook`, and so on).
Reserving the generic name `kind` for export status now would leave no
good name free for that real future need, forcing an awkward rename or
a second, confusingly-named field later. The **external wire protocol's
own `kind` field is unchanged** (`codecompass-adaptor-protocol`,
`decisions/0059`) — no change to the two separate repositories, fully
backward compatible; `HaskellAdapter.symbols()` simply maps the wire's
`kind` value into the core model's `export_kind` field at the one point
they meet. See §2's own updated field definition for the full
documented semantics. Every other design choice in this plan (the
concrete-not-abstract `symbols()` method, the `ADD COLUMN` migration
shape, the per-instance cache, the `build_symbol_index` non-fix, the
`CG-008` closure criteria) is unchanged.

## 0. Why this phase, and why now

Stage F (`decisions/0056`), gated on nothing (a separate axis from Stage
E/GATE DD). Phases 60-61 built and validated the first external
CodeCompass adapter, then exercised it for real against a second,
sibling vendor. The roadmap named Phase 62 to do exactly what those two
phases couldn't do speculatively: **assess `EcosystemAdapter`'s own
contract (`decisions/0002`) against real evidence from actually building
and using a genuinely different kind of adapter** — the smallest
justified interface change, if any, not a speculative redesign
(`planning/v1-redefinition/roadmap.md`'s own Phase 62 stanza).

The concrete evidence already exists, named explicitly by Phase 60's own
closeout: **`CG-008`** (`planning/context-gaps/inbox.md`,
`status: promoted-to-roadmap`, `graph_capability_gap`) —
`sync.py::rebuild_project_graph`'s own `_collect_vendor_symbols`
populates `context-graph.db`'s `symbols` table via a code path
(`symbols.py::extract_symbols_for_file`) that dispatches per-ecosystem
with no Haskell branch, so it silently returns `[]` for every `.hs`
file — confirmed live in Phase 60, unaffected by Phase 61. This phase
resolves it.

## 1. Current-state inspection (real, re-verified this session)

**Confirmed: `CG-008` is still open, exactly as filed.** Re-read
`src/codecompass/symbols.py::extract_symbols_for_file` (a closed `if`
chain: Python/`.py`, Cargo/`.rs`, npm/`.d.ts`, `return []` otherwise) and
`src/codecompass/sync.py::_collect_vendor_symbols` (walks
`adapter.source_location()` via `iter_source_files`, calls
`extract_symbols_for_file(path, config.ecosystem)` per file) — both
unchanged since Phase 60's own finding.

**A real, pre-existing duplication this phase can remove, not just a
Haskell-shaped gap to patch.** `NpmAdapter`/`PythonAdapter`/`CargoAdapter`'s
own `readme_and_api_surface()` implementations *already* walk their own
source files and call `extract_npm_symbols`/`extract_python_symbols`/
`extract_rust_symbols` per file, internally, to build the rendered
README string (confirmed by reading all three: e.g. `cargo.py`'s
`readme_and_api_surface()` does `for rs_file in
sorted(src_dir.rglob("*.rs")): symbols = extract_rust_symbols(rs_file)`).
This is the **same walk-and-extract shape** `_collect_vendor_symbols`
already does *independently*, in `sync.py`, for the very same three
ecosystems. A `symbols()` method on the adapter interface removes this
duplication for all four ecosystems, not just adds one for Haskell.

**A real representational gap between the wire protocol and CodeCompass's
own core model.** `decisions/0059` (Phase 60) added optional
`kind`/`note` fields to the external protocol's own `symbols` wire
shape (`"export"`/`"reexport"`/`"undetermined"` + free-text note) —
confirmed live and working end-to-end in Phase 60/61 (real
`[reexport]`/`[undetermined]` markers rendered into `hledger`/
`hledger-lib`'s own `CLAUDE.md`). But `src/codecompass/symbols.py::Symbol`
and `src/codecompass/graph.py::SymbolRow` (and the `symbols` table
itself) only ever had `name`/`purpose` — there is currently **no way**
for this richer, already-computed information to reach
`context-graph.db` at all, even once `_collect_vendor_symbols` is fixed
to call the adapter, unless the core model is widened to hold it.

**Amendment: the core-model field is named `export_kind`, not `kind` —
a deliberate, narrower semantic than the wire's own field name.** The
wire's three values describe **export/exposure status** — how
confidently an entry is known to belong to the public surface — never
the symbol's own **intrinsic type** (function vs. type vs. module,
or, for a genuinely different future ecosystem, `program`/`paragraph`/
`section`/`copybook` for a COBOL/mainframe adapter, the exact future
case `decisions/0056`/`0057` already name as this architecture's own
motivating scenario). A generic core field literally named `kind` would
read, to any future adapter author, as "the symbol's type" — the far
more natural reading of that word — and would already be occupied by a
narrower export-status concept by the time a real intrinsic-type need
arrived, forcing an awkward rename or a second, confusingly-adjacent
field. Naming it `export_kind` now costs nothing (it's a brand-new
field, nothing depends on the name yet) and keeps `kind` itself free for
whatever a future adapter genuinely needs it to mean. The external wire
protocol's own field name is unchanged — this is a CodeCompass-core-only
naming choice, made at the one translation point
(`HaskellAdapter.symbols()`) where the wire's `kind` value is read and
placed into the core model's `export_kind` field.

**Migration shape, confirmed by reading the real schema**:
`symbol_enrichment.symbol_id REFERENCES symbols(id) ON DELETE CASCADE`
(`UNIQUE`) — the same "must never drop-and-recreate" concern
`decisions/`(Phase 61's own `vendors` migration) protected against.
`_sync_symbols` already upserts by `(vendor_id, name)` natural key,
preserving `id` (confirmed: `rebuild_deterministic`'s own docstring,
independently re-verified by reading `_sync_symbols` directly) — so a
plain `ALTER TABLE symbols ADD COLUMN export_kind TEXT` / `ADD COLUMN
note TEXT` is safe and sufficient, mirroring
`_migrate_doc_relation_enrichment_relation_label`'s own precedent
exactly, **not** the heavier `vendors`-table-rebuild precedent (no
FK-cascade risk from an `ADD COLUMN`, unlike a `CHECK`-constraint
widening).

**A real, disclosed cost specific to external-process adapters, found by
reading the code (not live-profiled this session).**
`HaskellAdapter.dependency_tree()` and `HaskellAdapter.readme_and_api_surface()`
each independently call `self._analyze()`, which spawns a **new**
external subprocess and re-runs the **entire** `analyze_project` request
(computing both `dependencies` and `symbols` server-side) every time,
even though each caller only ever reads one of the two fields. Adding a
third caller (`symbols()`, below) without addressing this would make it
worse, not better.

**A real, deliberately-scoped-out consumer, found by reading the code**:
`src/codecompass/filetree.py::build_symbol_index` (FILETREE.md's own
"flat symbol index" section) and `symbols.py::purpose_for_file` are a
**third and fourth** call site independently dispatching through
`extract_symbols_for_file`, entirely separate from
`_collect_vendor_symbols`. Both are per-file, synchronous, no-subprocess
functions with zero adapter awareness today — see §4 for why this phase
does not also fix them.

## 2. Design: `EcosystemAdapter.symbols()`

A new **concrete** (not abstract) method on the base class:

```python
def symbols(self) -> list[Symbol]:
    """Structured public-API-surface symbols for this vendor, for
    context-graph.db's own `symbols` table. Default: no symbols — a
    future adapter that doesn't implement structured extraction isn't
    forced to (no TypeError at construction), matching this project's
    own "safe default over forced complexity" posture elsewhere
    (RELATION_LABELS' 'other' fallback, dev_only defaulting False for
    pipdeptree, etc.).
    """
    return []
```

**Concrete, not abstract — a deliberate choice, not an oversight.**
Making this `@abstractmethod` would break construction of *any* future
adapter (in-process or external) that doesn't implement it, the moment
it's added — a real, avoidable risk to `decisions/0056`'s own aspirational
"independently-maintained future adapters" framing this phase is meant
to inform, not undermine.

**Each of the four adapters overrides it**, removing duplication rather
than adding it (§1):

- `NpmAdapter`/`PythonAdapter`/`CargoAdapter`: the existing per-file
  walk-and-extract loop, currently embedded in each one's own
  `readme_and_api_surface()`, moves into `symbols()`;
  `readme_and_api_surface()` then calls `self.symbols()` internally
  instead of re-walking — a real behaviour-preserving refactor (same
  extraction functions, same files walked), verified by existing tests
  continuing to pass unchanged.
- `HaskellAdapter.symbols()` calls the (now-cached, §3) `_analyze()`
  result's wire `symbols` list and converts each entry into
  `Symbol(name, purpose, export_kind=entry["kind"], note=entry["note"])`
  — real, already-computed data, no new Haskell-specific logic added to
  `src/codecompass/` (the conversion is a plain dict-to-dataclass
  mapping, the same class of "manifest-key reads aren't ecosystem logic"
  reasoning `decisions/0057` already established for `package.yaml`).
  This is the one place the wire's `kind` field name and the core's
  `export_kind` field name meet — read one, write the other, no other
  translation needed anywhere else in this phase.

**`Symbol`/`SymbolRow` gain two new optional fields**, generalizing
`decisions/0059`'s wire-level addition into CodeCompass's own core
model — **named `export_kind`, not `kind`** (amendment; see §1's own
full reasoning):

```python
@dataclass
class Symbol:
    name: str
    purpose: str | None = None
    export_kind: str = "export"   # "export" | "reexport" | "undetermined"
    note: str | None = None
```

**Deliberately narrow, documented semantics — not a general symbol
ontology.** `export_kind` records only how confidently an entry is
known to belong to the analyzed package's own public surface. It is
**not** a symbol-type/kind field (function vs. class vs. module, or any
future ecosystem's own intrinsic categories) — that concept, if
CodeCompass ever needs it, deserves its own separate field (a real
future name, `kind` itself among the candidates, is deliberately left
free by this choice) and its own real evidence before being designed,
matching this phase's own "smallest justified change, not a speculative
redesign" mandate. This phase does not attempt to anticipate what a
symbol-type field would look like for COBOL or any other future
ecosystem — it only avoids naming today's narrower field in a way that
would collide with that unbuilt future concept.

Additive and backward compatible: every existing extractor
(`extract_rust_symbols`/`extract_python_symbols`/`extract_npm_symbols`)
never sets anything but the default — their own call sites and tests
are unaffected.

**`symbols` table gains nullable `export_kind`/`note` columns** via
`ALTER TABLE symbols ADD COLUMN export_kind TEXT DEFAULT 'export'` /
`ADD COLUMN note TEXT` (new migration function,
`_migrate_symbols_export_kind_note_columns`, checked via `PRAGMA
table_info` the same way `_migrate_doc_relation_enrichment_relation_label`
is, `_SCHEMA_VERSION` 8→9). `_sync_symbols`'s own `INSERT ... ON
CONFLICT` widened to carry both columns through.

**`sync.py::rebuild_project_graph`'s own `_collect_vendor_symbols`
becomes `adapter.symbols()`** (converted to `SymbolRow`s, carrying
`export_kind`/`note` through) — this is the change that actually closes
`CG-008`: a real `codecompass sync` against a Haskell vendor now
produces real `symbols` table rows, with zero Haskell-specific logic
anywhere in `src/codecompass/` outside `adapters/haskell.py`'s own thin
conversion.

**`codecompass query vendor <name>`'s own symbol listing** (the
vendor-detail query in `graph.py`, `SELECT id, name, purpose FROM
symbols ...`) gains `export_kind`/`note` in its own output dict —
completing the fix end-to-end (database has it, the one real CLI
surface that already renders a vendor's own symbols shows it) rather
than leaving it half-wired.

## 3. Design: `HaskellAdapter`'s own internal analyze-result caching

A per-instance cache, entirely internal to `HaskellAdapter`, no
interface change:

```python
def __init__(self, config, project_root):
    super().__init__(config, project_root)
    self._cached_analysis: dict | None = None

def _analyze(self) -> dict:
    if self._cached_analysis is None:
        executable = _adapter_executable(self.project_root)
        process = ExternalAdapterProcess([str(executable)])
        process.initialize()
        try:
            self._cached_analysis = process.analyze_project(
                self._resolve_package_dir(), self.config.name
            )
        finally:
            process.shutdown()
    return self._cached_analysis
```

`dependency_tree()`, `readme_and_api_surface()`, and the new `symbols()`
all call `self._analyze()` — now at most **one** real external-process
round trip per adapter instance, however many of those three methods a
caller invokes on it.

**Explicitly not a cross-instance cache.** `sync.py`'s own two call
sites (`sync_vendor` and, separately, `rebuild_project_graph`) each
construct their **own** `HaskellAdapter` instance via `get_adapter(...)`
— this phase's own cache does not, and is not intended to, remove the
second, cross-instance external-process spawn between them. Real net
effect for one Haskell vendor in a whole-project `codecompass sync`:
**before** this phase, 2 spawns from `sync_vendor` alone (one each for
`dependency_tree()`/`readme_and_api_surface()`, each computing both
fields but using only one — real waste, and `rebuild_project_graph`'s
own call produced nothing for Haskell at all, `CG-008`); **after**, 1
spawn from `sync_vendor` (cached, all three methods share it) + 1 new,
genuinely necessary spawn from `rebuild_project_graph` (for `symbols()`,
closing `CG-008`) — the same total count, now doing real, non-duplicated
work end to end instead of half-wasted, half-missing work. Removing the
remaining cross-instance duplication would require restructuring
`sync.py`'s own two-pass orchestration (`sync_all` then
`rebuild_project_graph`) to share adapter instances across both —
a materially bigger, ecosystem-agnostic refactor this phase's own
"smallest justified fix" mandate does not extend to; named here as an
accepted, disclosed inefficiency, not chased further.

## 4. The disclosed, NOT-fixed gap: `build_symbol_index`/`purpose_for_file` still can't see Haskell symbols

`filetree.py::build_symbol_index` (FILETREE.md's own flat symbol index
section) and `symbols.py::purpose_for_file` (per-file purpose
annotations elsewhere in FILETREE.md's own rendering) are **per-file**,
synchronous, no-subprocess functions, called once per file during a
tree walk that has zero adapter awareness today — they take `(path,
ecosystem)`, not an adapter instance, and are shared, ecosystem-generic
tree-rendering plumbing used for every vendor, not just Haskell's.
Retrofitting them to consult an external adapter's own per-vendor
`analyze_project` result would mean either (a) spawning the external
process once *per file* during the tree walk (a real, severe
performance regression — the opposite direction from §3's own fix), or
(b) threading a pre-fetched, whole-vendor `Symbol` list through the
entire `FILETREE.md`-rendering call chain so each per-file call can look
itself up in it — a materially larger, invasive change to
`sync.py`/`filetree.py`'s own shared rendering path (touching every
ecosystem's own tree rendering, not just Haskell's) than "the smallest
justified interface change" this phase's own mandate covers.

**Consequence, named plainly, not left implicit**: after this phase,
`context-graph.db`'s own `symbols` table (and `codecompass query vendor
<name>`, the one real CLI surface reading it) correctly shows real
Haskell symbols, closing `CG-008`. `vendor/<name>/FILETREE.md`'s own
"flat symbol index" section — a *different*, purely-rendered artifact —
still shows nothing for a Haskell vendor's own files. This is a real,
deliberately accepted scope boundary, not an oversight discovered too
late: flagged in the review gate for visibility, and left as a
candidate for a future phase only if real use ever shows the FILETREE.md
gap specifically (as opposed to the graph's own `symbols` table, which
this phase does fix) actually matters.

## 5. What this phase deliberately does not build

- **No broader "plugin-style adapter boundary"/packaging/licensing
  commitment** (`decisions/0056`'s own aspirational framing, restated by
  the roadmap: "this phase produces the evidence, it does not itself
  commit to that broader packaging/licensing model"). This phase changes
  what the interface can express; it does not decide whether CodeCompass
  should formally support third-party or proprietary adapters.
- **No fix to `build_symbol_index`/`purpose_for_file`** (§4).
- **No cross-adapter-instance caching** (§3) — `sync_vendor` and
  `rebuild_project_graph` keep constructing separate adapter instances.
- **No change to the external adapter repositories themselves**
  (`codecompass-adaptor-haskell`/`codecompass-adaptor-protocol`) — the
  wire protocol (`decisions/0057`-`0059`) already carries everything
  `HaskellAdapter.symbols()` needs; this phase only changes how
  CodeCompass's own core *consumes* what the adapter already reports.
- **No `usage.py`/call-site-detection changes** — Phase 61's own
  already-settled non-scope (no real consumer found), unaffected and
  not reopened here.
- **No change to `Symbol`/`SymbolRow`'s `name`/`purpose` semantics** for
  the three existing in-process ecosystems — `export_kind`/`note` are
  pure additions, defaulted to today's implicit behaviour.
- **No general symbol-type/ontology field** (amendment, §2) — only the
  narrower export/exposure-status concept the wire protocol already
  reports is added; a future intrinsic-type field is left unbuilt and
  unnamed.

## Scope

**In scope:**

- `EcosystemAdapter.symbols()` (new, concrete, default `[]`) —
  `src/codecompass/adapters/base.py`.
- `Symbol` gains `export_kind`/`note` (`src/codecompass/symbols.py`);
  `SymbolRow` gains matching fields (`src/codecompass/graph.py`).
- `symbols` table migration (`ADD COLUMN export_kind`/`ADD COLUMN note`,
  `_SCHEMA_VERSION` 8→9); `_sync_symbols` widened.
- `NpmAdapter`/`PythonAdapter`/`CargoAdapter.symbols()` — refactored out
  of each one's own existing `readme_and_api_surface()`, which then
  calls `self.symbols()` internally; existing tests for all three
  updated only if their own internal structure requires it, not their
  observable behaviour.
- `HaskellAdapter.symbols()` (wire → `Symbol` conversion) and the
  per-instance `_analyze()` cache (§3).
- `sync.py::rebuild_project_graph`'s `_collect_vendor_symbols` →
  `adapter.symbols()` (closes `CG-008`).
- `graph.py`'s vendor-detail query's symbol listing gains `export_kind`/`note`.
- Fixture tests for all of the above (new `Symbol(export_kind=..., note=...)`
  cases; a migration test mirroring the existing
  `_migrate_doc_relation_enrichment_relation_label` test shape; a
  `_collect_vendor_symbols`→`adapter.symbols()` wiring test using a fake
  adapter, mirroring `tests/test_sync.py`'s existing
  `test_rebuild_project_graph_records_vendor_and_resolved_symbol_usage`
  shape); a real, `stack`/submodule-gated live re-confirmation that a
  real `codecompass sync` against `hledger-lib` now produces non-empty
  `symbols` table rows with correct `export_kind`/`note` values (the same
  scratch-symlink setup Phase 60/61 already established).
- `CG-008` marked resolved in `planning/context-gaps/inbox.md`
  (`curation` outcome updated, not re-triaged from scratch — the
  decision was already made at Phase 60's own closeout; this phase
  executes it).
- `architecture/overview.md` updated: the "External adapters" section
  gains a description of `symbols()`/the caching fix; the Adapter
  interface section's own five-method description becomes six (still
  describing `readme_and_api_surface`, `installed_version`,
  `source_location`, `repository_url`, `dependency_tree` as the
  required/abstract ones, `symbols` as the new optional/concrete one).
- `decisions/0002` is not edited (append-only) — a new ADR if this
  phase's own real implementation surfaces a non-obvious tradeoff beyond
  what's already decided here (expected: none, but not ruled out in
  advance).

**Explicitly deferred / out of scope:**

- `build_symbol_index`/`purpose_for_file`'s own Haskell gap (§4) —
  named, not silently dropped, and not scheduled to a specific future
  phase (matches Phase 61's own "don't schedule a fix for a
  hypothetical need" discipline — revisit only if real use shows it
  matters).
- Cross-adapter-instance caching / `sync.py`'s own two-pass
  orchestration (§3).
- Any packaging/licensing commitment for third-party or proprietary
  adapters (§5).
- Any change to the two external repositories.
- `usage.py` Haskell import/call-site detection (Phase 61's own settled
  non-scope).
- Resolving GATE DD, or completing/bypassing Phases 55-59 — unaffected
  by this phase, exactly as Phases 60/61 left them.

## Design decisions

- **`symbols()` is concrete with a `[]` default, not abstract** — a
  future adapter (in-process or external) that doesn't implement
  structured symbol extraction isn't forced to, and isn't broken at
  construction time. The interface widens without becoming stricter.
- **Refactor npm/Python/Cargo's own existing extraction into `symbols()`
  rather than leaving it duplicated in `readme_and_api_surface()`** —
  the duplication already existed before this phase (`_collect_vendor_symbols`
  and each adapter's own README rendering independently walked the same
  files); fixing Haskell's own gap is the trigger, but removing the
  pre-existing duplication for the other three ecosystems is the same
  change, not extra scope.
- **`export_kind`/`note` widen the core `Symbol`/`SymbolRow` model, not just
  the Haskell adapter's own conversion step** — generalizing
  `decisions/0059`'s wire-level addition into core matches this
  project's own precedent of core types staying ecosystem-agnostic
  (`decisions/0002`) rather than each ecosystem inventing its own
  parallel representation for the same underlying "how confident is
  this claim" concept.
- **`ADD COLUMN`, not a `vendors`-style table rebuild, for the `symbols`
  migration** — `symbol_enrichment`'s own `ON DELETE CASCADE` FK is the
  same real risk `vendors`' own migration protected against, but
  `ALTER TABLE ... ADD COLUMN` (unlike a `CHECK`-constraint widening,
  which SQLite has no `ALTER` form for) needs no drop-and-recreate at
  all — the lighter mechanism `_migrate_doc_relation_enrichment_relation_label`
  already established is directly reusable, unchanged.
- **A per-instance cache, not a cross-instance or on-disk one, for
  `HaskellAdapter._analyze()`** — closes the concrete, real, in-hand
  redundancy (one instance, three methods) without taking on the bigger,
  more invasive redesign a cross-instance cache would require.
- **`build_symbol_index`/`purpose_for_file` are explicitly not fixed**
  — the real architectural mismatch (per-file, no-subprocess,
  adapter-unaware functions vs. a per-vendor, subprocess-backed external
  adapter) makes a correct fix materially bigger than this phase's own
  mandate; naming the gap plainly is preferred over either silently
  leaving it or over-expanding this phase to close it speculatively.

## Files

- `src/codecompass/adapters/base.py` — `EcosystemAdapter.symbols()`
  (new, concrete).
- `src/codecompass/adapters/npm.py`, `python.py`, `cargo.py` —
  `symbols()` added (refactored out of `readme_and_api_surface()`).
- `src/codecompass/adapters/haskell.py` — `symbols()` added; `_analyze()`
  gains the per-instance cache; `__init__` override.
- `src/codecompass/symbols.py` — `Symbol` gains `export_kind`/`note`.
- `src/codecompass/graph.py` — `SymbolRow` gains `export_kind`/`note`;
  `_migrate_symbols_kind_note_columns` (new); `_SCHEMA_VERSION` 8→9;
  `_sync_symbols` widened; vendor-detail query's symbol listing gains
  `export_kind`/`note`.
- `src/codecompass/sync.py` — `_collect_vendor_symbols` →
  `adapter.symbols()`.
- `tests/test_adapter_npm.py`, `test_adapter_python.py`,
  `test_adapter_cargo.py` — confirm `symbols()`/`readme_and_api_surface()`
  behaviour unchanged after the refactor.
- `tests/test_adapter_haskell.py` — `symbols()` fixture tests
  (export_kind/note passthrough); the per-instance cache (a fake/counting
  `ExternalAdapterProcess` confirming exactly one `initialize`/
  `analyze_project` call across multiple method calls on one instance);
  the existing live smoke test extended to also assert on `symbols()`'s
  own export_kind/note values and, separately, a real post-sync
  `context-graph.db` check that `symbols` rows exist for `hledger-lib`.
- `tests/test_graph.py` — the new migration's own fresh-DB +
  pre-existing-DB test pair (mirroring the `doc_relation_enrichment`
  precedent); `_sync_symbols`'s own export_kind/note round-trip.
- `tests/test_sync.py` — `_collect_vendor_symbols`/`rebuild_project_graph`'s
  own symbol-population test extended or added for a fake adapter
  reporting `export_kind`/`note`.
- `planning/context-gaps/inbox.md` — `CG-008` marked resolved.
- `architecture/overview.md` — Adapter interface section, External
  adapters section, Known footguns (if the `build_symbol_index` gap
  warrants its own footgun bullet, matching `L-026`'s own precedent).
- `planning/retros/phase-62-adapter-interface-consolidation.md` (new) —
  the retro.

## Verification

- `pytest`/`ruff check .`/`check_user_docs.py --strict` all clean.
- `NpmAdapter`/`PythonAdapter`/`CargoAdapter`'s own existing tests pass
  unchanged (confirms the refactor is behaviour-preserving, not just
  "new tests pass").
- A fake-adapter-based test confirms `_collect_vendor_symbols`'s
  replacement (`adapter.symbols()`) actually reaches
  `rebuild_project_graph`'s own `SymbolRow` construction with `export_kind`/
  `note` intact.
- The new migration has both a fresh-DB acceptance test and a
  pre-existing-DB migration test (the established two-test pattern every
  prior schema widening in this file uses), confirming `symbol_enrichment`
  rows survive the migration untouched (an explicit assertion, not
  merely "no error raised").
- A real, live, `stack`/submodule-gated re-confirmation: a real
  `codecompass sync` against `hledger-lib` (the same scratch-symlink
  setup Phase 60/61 established) produces real, non-empty `symbols`
  table rows in the resulting `context-graph.db`, with at least one row
  showing `export_kind='reexport'` or `export_kind='undetermined'` (not
  just plain `'export'` rows) — checked directly via SQL, not assumed
  from the fixture tests passing.
- A real check that `HaskellAdapter._analyze()` is called at most once
  per adapter instance across a real `installed_version()` +
  `dependency_tree()` + `readme_and_api_surface()` + `symbols()` call
  sequence on the same instance (a counting fake process, or a real
  process-spawn count via the live smoke test's own instrumentation).
- `release-phase-auditor` PASS or PASS WITH NON-BLOCKING OBSERVATIONS.

## Done when

Standard DoD (`CLAUDE.md` §5) + `CG-008` is genuinely closed (a real
`codecompass sync` against a real Haskell vendor populates
`context-graph.db`'s `symbols` table correctly, independently checked,
not merely "the code compiles") + all three in-process adapters'
`readme_and_api_surface()` behaviour is unchanged after the refactor
(existing tests pass without modification to their own assertions) +
the per-instance `_analyze()` cache is real and tested, not just
designed + the `build_symbol_index`/`purpose_for_file` gap (§4) is
explicitly documented, not silently left + retro states plainly whether
this phase's own real experience supports or complicates
`decisions/0056`'s own aspirational "one stable interface, many
independently-maintained adapters" framing — the evidence this phase
was chartered to produce, stated honestly either way.

**Not done merely because `symbols()` exists and one test passes** —
done only once the real, live `hledger-lib` re-confirmation shows actual
`export_kind`/`note`-bearing rows in a real database, and the retro can state
plainly what, if anything, in `EcosystemAdapter`'s own contract still
doesn't fit a genuinely different (external-process) adapter shape.

---

## Review gate

Presented for review before implementation starts.

1. **`symbols()` as a new, concrete (not abstract) interface method** —
   a design choice made during this planning pass, not a direct
   instruction; flagged since it's the one actual interface surface
   change this phase makes, and the whole "does the interface generalise"
   question this phase exists to answer turns on it.
2. **Widening `Symbol`/`SymbolRow` with `export_kind`/`note` at the core-model
   level**, not just inside `HaskellAdapter`'s own conversion step — a
   judgment call that the wire protocol's own confidence-marking concept
   is generalizable, not Haskell-specific; flagged since it touches
   `graph.py`'s own schema (a migration) for every ecosystem, not just
   the one that currently populates non-default values.
3. **Explicitly not fixing `build_symbol_index`/`purpose_for_file`**
   (§4) — a real, disclosed scope boundary the plan asserts is
   correctly out of reach for "smallest justified fix," not a
   corner cut for expedience; flagged since it means Phase 62's own
   "adapter-interface consolidation" title doesn't fully close every
   Haskell-symbol-visibility gap, only the graph's own `symbols` table.
4. **A per-instance-only cache for `HaskellAdapter._analyze()`**, not a
   broader `sync.py` orchestration change — flagged since the disclosed
   remaining cross-instance duplication (§3) means this phase's own real
   external-process-spawn count doesn't actually drop, only its
   *usefulness* per spawn improves.
5. **Marking `CG-008` resolved as part of this phase's own closeout**,
   rather than a separate triage step — consistent with how the gap was
   already routed to this phase by name at Phase 60's own closeout, not
   a new decision being made here.
