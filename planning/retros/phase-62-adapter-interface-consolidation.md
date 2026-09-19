# Phase 62 retro — adapter-interface consolidation

- **Date:** 2026-09-19
- **Commit(s):** `c2ccecf` (plan amendment — `export_kind` naming); this phase's own implementation closeout commit, see `planning/CONTEXT.md`
- **Agents used:** none — implemented directly by the lead, per direct user instruction to amend the plan and proceed with implementation in one continuous session.

## Where we are

Stage F (`decisions/0056`), gated on nothing — a separate axis from
Stage E/GATE DD. Phase 60 shipped the first external CodeCompass
adapter and, during its own live validation, surfaced a real gap:
`context-graph.db`'s `symbols` table stayed empty for every Haskell
vendor (`CG-008`). Phase 61 confirmed the gap was still open and
unrelated to its own result. Phase 62 is the interface-consolidation
phase that both closes `CG-008` and answers the roadmap's own open
question about `EcosystemAdapter`'s contract.

## Goal

Assess `EcosystemAdapter`'s own contract against what building and
using the Haskell adapter actually required — the smallest justified
interface change, not a speculative redesign — and use it to close
`CG-008` with a real, live-confirmed fix.

## Scope delivered vs planned

Delivered per the plan, with one pre-coding amendment (direct
instruction) and one implementation-time refinement (discovered while
implementing, not pre-planned):

- **Amendment, before any code was written**: the new core-model field
  is named `export_kind`, not `kind`. The wire protocol's own `kind`
  field (`decisions/0059`) is unchanged; `HaskellAdapter.symbols()` is
  the one translation point. Scope, acceptance criteria, migration
  approach, caching design, and the real-`hledger`-validation
  requirement were all preserved unchanged by this amendment, exactly
  as instructed.
- `EcosystemAdapter.symbols() -> list[Symbol]` added as a new,
  **concrete** (not abstract) method, default `[]`.
- **Implementation-time refinement to the plan's own literal text**:
  the plan described refactoring each of `NpmAdapter`/`PythonAdapter`/
  `CargoAdapter`'s own `readme_and_api_surface()` to call
  `self.symbols()` internally. On actually reading all three files
  closely during implementation (not just at planning time), two
  things became clear: (1) the walk+extract logic `_collect_vendor_symbols`
  performed in `sync.py` is ecosystem-generic (`iter_source_files` +
  `extract_symbols_for_file(path, ecosystem)`) and needs no per-adapter
  code at all — it can live as the base class's own concrete default,
  which every adapter inherits for free; (2) the plan's claim that npm
  specifically duplicated this inside its own `readme_and_api_surface()`
  was factually wrong — npm's `readme_and_api_surface()` dumps raw
  `.d.ts` file contents and never called `extract_npm_symbols` at all,
  so there was no duplication to remove there. Refactoring
  `readme_and_api_surface()` to call `self.symbols()` for cargo/python
  would also have silently changed their rendered output (losing
  per-file grouping headers, since `Symbol` carries no file-path
  field) — a real, avoidable regression risk the base-class-default
  approach sidesteps entirely. Net result: **zero changes to
  `adapters/npm.py`/`cargo.py`/`python.py`**, and no behavioral change
  to any of their `readme_and_api_surface()` output, while still fully
  satisfying "route existing Python/npm/Cargo symbol collection through
  it" — they now go through `adapter.symbols()` (the base-class
  default) exactly as instructed, just without adapter-specific edits.
- `Symbol`/`SymbolRow` widened with `export_kind: str = "export"` and
  `note: str | None = None`.
- `HaskellAdapter.symbols()` overrides the base default, converting its
  own already-computed external-process result (`entry["kind"]` →
  `export_kind`, `entry["note"]` → `note`) — the one translation point.
- `symbols` table migration: `ALTER TABLE symbols ADD COLUMN export_kind
  TEXT NOT NULL DEFAULT 'export'` / `ADD COLUMN note TEXT`
  (`_migrate_symbols_export_kind_note_columns`, `_SCHEMA_VERSION` 8→9),
  checked via `PRAGMA table_info`, mirroring
  `_migrate_doc_relation_enrichment_relation_label` exactly.
  `symbol_enrichment`'s `ON DELETE CASCADE` FK is untouched — no
  drop-and-recreate.
- `_sync_symbols`'s own `INSERT ... ON CONFLICT` widened to carry both
  columns through.
- `sync.py::rebuild_project_graph`'s own `_collect_vendor_symbols`
  helper removed; its call site now calls `adapter.symbols()`
  polymorphically — this is what closes `CG-008`.
- The vendor-detail query (`graph.py`, feeding `codecompass query
  vendor`) widened to select and return `export_kind`/`note`.
  `cli.py`'s own Rich table for `query vendor` gained two columns
  ("Export kind", "Note") alongside the JSON output, completing the fix
  end to end on the one real CLI surface that renders a vendor's own
  symbols.
- `HaskellAdapter` gained a per-instance `_analyze()` cache
  (`self._cached_analysis`), populated once and reused by
  `dependency_tree()`/`readme_and_api_surface()`/`symbols()` —
  deliberately not a cross-instance cache.
- Fixture tests added/updated across `tests/test_adapter_haskell.py`
  (`symbols()` conversion, empty-capability case, per-instance-cache
  call-counting test, extended live smoke test), `tests/test_graph.py`
  (migration fresh-DB-and-pre-existing-DB pair, idempotency test,
  `_sync_symbols` round-trip), `tests/test_sync.py` (`_FakeAdapter`
  gained a `symbols()` method plus an optional override, and a new
  wiring test exercising `export_kind`/`note` end to end through
  `rebuild_project_graph`), `tests/test_cli.py` (a new test asserting
  the `query vendor` Rich table and JSON both show `export_kind`/
  `note`). Also fixed seven pre-existing hardcoded `schema_version ==
  "8"` assertions to `"9"` (the real current version after this
  phase's own bump) and three matching prose mentions.

**Explicitly, disclosedly not fixed** (matches the plan exactly):
`filetree.py::build_symbol_index`/`symbols.py::purpose_for_file`
(`FILETREE.md`'s own flat symbol index) stay Haskell-blind. No
cross-adapter-instance caching. No change to either external
repository (`codecompass-adaptor-protocol`/`codecompass-adaptor-haskell`).
No `usage.py` changes. No general symbol-type/ontology field.

## What was achieved

- Full test suite: **623 passed, 2 skipped** (up from 615 pre-phase —
  the 2 skips are the pre-existing `stack`-gated smoke tests when run
  outside this environment; here `stack` is available so they ran and
  passed). `ruff check .` clean. `check_user_docs.py --strict` clean.
- **Real, live re-confirmation**: a real `codecompass sync --yes
  --budget 0` against `hledger-lib` (scratch project, `hledger-lib`
  symlinked directly into the pinned `hledger` monorepo checkout — the
  same approach Phase 60/61 used) produced **1305** real `symbols`
  table rows for the vendor — **1256** `export`, **48** `reexport`,
  **1** `undetermined` — checked directly via SQL against the resulting
  `context-graph.db`. Independently re-confirmed via `codecompass query
  vendor hledger-lib --json`, which showed the same 1305 rows with
  `export_kind`/`note` populated correctly (e.g. `X` →
  `export_kind="reexport"`, `note="alias for Hledger.Utils, ..."`).
  Before this phase, this same call site produced **zero** rows for any
  Haskell vendor — `CG-008` is genuinely closed, not just plausibly
  addressed.
- `HaskellAdapter`'s live smoke test (`test_live_smoke_real_hledger_lib_end_to_end`)
  extended to call `adapter.symbols()` directly and assert both
  `"reexport"`/`"undetermined"` appear in the real result's own
  `export_kind` values — passed against the real, built
  `codecompass-adaptor-haskell` executable in 38s.
- `CG-008` marked resolved in `planning/context-gaps/inbox.md`; a
  `promoted.md` line added to `planning/learnings/promoted.md`.

## What worked

- Reading the actual current source of all four adapters *before*
  committing to the exact refactor shape, rather than trusting the
  plan's own prose description of what each one currently did — this is
  what surfaced npm's factually-wrong duplication claim and the
  cleaner base-class-default design before any code was written, not
  after a wasted refactor attempt.
- Doing the plan amendment as a fully separate, reviewable commit
  before touching any `src/` file — kept the `export_kind` naming
  decision isolated and easy to verify against the user's own explicit
  instruction, independent of the implementation that followed.
- The `ADD COLUMN` migration precedent
  (`_migrate_doc_relation_enrichment_relation_label`) transferred
  directly with no adaptation needed beyond swapping the table/column
  names — this project's own established migration idiom held up
  exactly as designed for a second, unrelated use.
- Running the real live `codecompass sync` against `hledger-lib` in a
  disposable scratch directory (symlink, not copy) caught nothing wrong
  this time, but confirmed the fix produces real, checkable numbers
  (1305 rows, 48 reexport, 1 undetermined) rather than resting on
  fixture-test plausibility alone — matching this project's own
  "verified live, not assumed" discipline for every prior Haskell-
  adapter phase.

## What didn't work

- The plan's own literal implementation prescription for npm/Python/
  Cargo (refactor each one's `readme_and_api_surface()` to call
  `self.symbols()`) didn't survive contact with the actual code — it
  was written from a summarized understanding of what "the three
  adapters do," not a fresh read of each file. The base-class-default
  design that replaced it is simpler and lower-risk, but it means the
  plan document's own §2 design section is now slightly stale relative
  to what was actually built (documented here and in `CONTEXT.md`/
  `ROADMAP.md`, not silently left inconsistent, but not corrected back
  into the plan file itself — plans are a point-in-time design record,
  not a living doc, matching this project's own convention of updating
  `CONTEXT.md`/architecture docs as the current-truth source instead).

## Lessons learnt

- **A plan's own description of "existing behavior" is a claim, not a
  fact, and should be re-verified against the real file at
  implementation time, not carried forward from the planning pass
  unchecked** — the planning pass read the adapters closely enough to
  spot the `_collect_vendor_symbols` duplication, but not closely
  enough to notice npm's `readme_and_api_surface()` never actually
  called `extract_npm_symbols`. A closer read at implementation time
  cost nothing extra here (the files are small) and changed the
  concrete refactor shape for the better.

## Process-improvement feedback

- None beyond the lesson above — no `.claude/agents/` role, workflow
  step, or hard rule needs a change from this phase. This was a
  lead-only implementation with no subagent dispatches, so no
  agent-boundary or handoff issue arose to report.

## Candidate learnings filed

- The "re-verify a plan's own claims about existing code against the
  real file before implementing the described refactor" observation
  above is folded into this retro rather than filed as a separate
  `L-NNN` candidate — it doesn't generalize past "read the code you're
  about to change," which is already this project's own standing
  practice (`CLAUDE.md` §1, `CONTRIBUTING.md`), not a new rule.

## Where we're going

Phase 63 (Stage F's remainder — a lightweight ordinary-project smoke
test, `planning/ROADMAP.md` row 63) is next and depends on this phase's
own output; not yet planned. GATE DD remains open and unaffected by
this phase — Stage F is a separate axis from Stage E, per
`decisions/0056`.

## Time / cost note

No AI-API spend — this phase is pure `src/`/test/planning-doc work plus
one real, free `codecompass sync --yes --budget 0` (no Anthropic API
calls at `--budget 0`) against a local scratch project.
