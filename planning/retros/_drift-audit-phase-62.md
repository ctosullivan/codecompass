# Docs-drift audit — Phase 62 (adapter-interface consolidation)

- **Diff audited:** `c2ccecf..96428a8` (c2ccecf is plan-amendment-only,
  no `src/` changes; 96428a8 is the full implementation).
- **Verdict: NO DRIFT.**

## What actually changed about the system (from the diff, verified against code)

- `EcosystemAdapter` gained a sixth method, `symbols() -> list[Symbol]`,
  **concrete** (not abstract) — confirmed by reading
  `src/codecompass/adapters/base.py`: exactly 5 `@abstractmethod`s
  (`installed_version`, `source_location`, `readme_and_api_surface`,
  `repository_url`, `dependency_tree`) plus the new concrete `symbols()`.
- `HaskellAdapter` gained `__init__` with `self._cached_analysis` and a
  `symbols()` override converting wire `kind`/`note` → core
  `export_kind`/`note`.
- `Symbol`/`SymbolRow` gained `export_kind: str = "export"` and
  `note: str | None = None`.
- `context-graph.db`'s `symbols` table gained `export_kind`/`note`
  columns via `ALTER TABLE ADD COLUMN` migration; `_SCHEMA_VERSION`
  8→9; `_sync_symbols` and `vendor_profile`'s SELECT widened.
- `codecompass query vendor`'s Rich table gained "Export kind"/"Note"
  columns (`--json` output already carried whatever `vendor_profile`
  returns).
- `sync.py::rebuild_project_graph` now calls `adapter.symbols()` instead
  of the removed private `_collect_vendor_symbols` — this is what
  actually closes CG-008 (Haskell vendors' symbols now reach the graph).
- `filetree.py::build_symbol_index` / `symbols.py::purpose_for_file`
  (FILETREE.md's own symbol index) were **explicitly not touched** and
  remain Haskell-blind — confirmed by their unchanged signatures
  `(path, ecosystem)` in the diff.

## Docs checked (current-truth: README.md, docs/, architecture/, ai-docs/)

Grepped for `symbols`, `export_kind`, `kind`, `_SCHEMA_VERSION`,
`schema_version`, `SymbolRow`, `EcosystemAdapter`, `query vendor`,
`Haskell`, `EcosystemAdapter` across all four trees, then read every hit
in context:

- `architecture/overview.md` — already updated in this same commit
  (Adapter interface section: "five abstract methods... plus one
  concrete method, `symbols()`"; the `export_kind`-vs-`kind` naming
  rationale; the per-instance `_analyze()` cache note; the
  Symbol/purpose-extraction section; the "Populating the graph" section
  now describing `adapter.symbols()` instead of the removed
  `_collect_vendor_symbols`; the disclosed FILETREE.md/`build_symbol_index`
  gap note). Checked each of these sentences against the actual code
  (base.py's abstractmethod count, haskell.py's `symbols()`/`_analyze()`,
  sync.py's `rebuild_project_graph`, filetree.py's unchanged signatures)
  — all accurate, nothing stale, nothing overclaimed.
- `docs/cli-reference.md` — `query vendor`'s description ("one vendor's
  full profile: its symbols, total usage count...") stays correct at its
  existing level of granularity; it never enumerated per-symbol columns,
  so the new `export_kind`/`note` columns don't falsify anything written
  there. The `kind` field mentioned near `query skills` (line 131/157) is
  `doc_artifacts.kind` — an unrelated, pre-existing concept (skill/
  cursor_mdc/slash_command), not the new `Symbol.export_kind` — no
  naming collision or confusion introduced by this phase's docs. `query
  symbol` (a different command, backed by the untouched `symbol_profile`)
  is correctly left as-is since Phase 62 didn't touch it.
- `docs/config-schema.md`, `docs/external-adapters.md` — describe the
  Haskell adapter's build/versioning/submodule mechanics, none of which
  Phase 62 touched; still accurate.
- `README.md` — only describes ecosystems/features at a high level
  ("vendors, symbols, and actual usage"; "Haskell/Stack ... via a
  separate external adapter"); no per-field claims to go stale.
- `ai-docs/README.md`, `ai-docs/CLAUDE.md` — same high-level scope as
  README.md; no drift.
- `CONTRIBUTING.md` — no mentions of `EcosystemAdapter`, `symbols`, or
  schema version; not implicated.

No instance found of a current-truth doc describing the *old* five-method
abstract-only `EcosystemAdapter` contract, the old `Symbol(name, purpose)`
two-field shape, `_SCHEMA_VERSION == "8"` as current, the removed
`_collect_vendor_symbols` helper, or a two-column `query vendor` symbols
table, anywhere outside `architecture/overview.md` (which was already
correctly updated).

## Scope note

Checked: every observable-behavior change in the diff (new adapter
method + its default/override, widened `Symbol`/`SymbolRow`/`symbols`
table/migration, widened CLI table, the `rebuild_project_graph` call-site
swap) against `README.md`, `docs/**`, `architecture/**`, `ai-docs/**`.
Deliberately not re-litigated: `planning/**` prose (CONTEXT.md, ROADMAP.md,
retro, context-gaps/inbox.md, learnings/promoted.md) — those are
plan/process records, not "current-truth" docs under CLAUDE.md §5, and
are the docs-maintainer/lead's own self-report I was told not to read as
a starting point for my own view (I formed the "what changed" list from
the diff and code directly, not from the commit message or retro prose,
then read those planning files only afterward as confirmation, not
input). Not re-checked: `decisions/*` (out of scope for this agent's
write/audit boundary; also not "current-truth" system-behavior docs in
the CLAUDE.md §5 sense) and `CHANGELOG.md` (a change log, not a
current-state description).
