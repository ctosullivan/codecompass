# Phase 74: Priority B provenance hardening (`L-031` + `L-032`) — plan

**Status:** in progress (2026-09-27).

Second concrete post-v1 phase, continuing directly from Phase 73 per
the user's own instruction to proceed with implementation. Closes the
two already-scoped, already-evidenced Priority B hardening items named
together in `planning/ROADMAP.md`'s own Future-improvement backlog and
Priority B row (`decisions/0062`): `L-031` (`symbol_enrichment` has no
producer-attribution column) and `L-032` (the external adapter wire
protocol's `ecosystem`/`capabilities` fields received but never
validated). Both were fully scoped by `domain-skeptic`'s own Phase 63D
review — this phase implements the fix each entry already names, not a
fresh design exercise.

## 0. What this phase is, and isn't

Two small, independent, additive fixes bundled into one phase because
both are Priority B's own named "first hardening items" and both are
cheap: no new design, no schema-generalisation question, no GATE
ceremony (both already carry a concrete fix in their own backlog
entry). **Not in scope**: any broader provenance/claim-evidence model
work (that's Priority B's own larger, unplanned productisation effort,
`decisions/0062`) — this phase closes two specific, disclosed gaps in
the *existing* mechanically-vs-inferred provenance discipline, nothing
more.

## 1. Scope

### 1.1 `L-031` — `symbol_enrichment.model`

Add a nullable `model` column to `symbol_enrichment`
(`src/codecompass/graph.py`), via a new `_migrate_symbol_enrichment_model_column`
function mirroring `_migrate_symbols_export_kind_note_columns`'s own
`ALTER TABLE ... ADD COLUMN` shape (never drop/recreate — this table
holds paid AI enrichment output that must survive every migration).
**Nullable, not `NOT NULL` with a fabricated backfill default** — unlike
`vendor_enrichment.model`/`doc_relation_enrichment.model` (both
`NOT NULL` from their own first schema version), a pre-existing
`symbol_enrichment` row's real producer was never recorded; inventing a
value now would fabricate certainty this project's own provenance
discipline (`decisions/0051`, `decisions/0054`) explicitly rejects. An
honest `NULL` ("producer unknown, predates this column") is the correct
backfill. `record_symbol_enrichment` gains a required `model: str`
parameter for every new write going forward; `enrichment.py`'s one real
call site passes the already-existing `_MODEL` constant (identical to
`record_enrichment`'s own `model=_MODEL`).

Not exposed via any `codecompass query` surface — `vendor_enrichment.model`
isn't either (checked directly), so this stays a pure provenance-recording
fix, matching `L-031`'s own literal, minimal ask.

### 1.2 `L-032` — external adapter `ecosystem`/`capabilities` validation

`src/codecompass/adapters/external_process.py::ExternalAdapterProcess.initialize`
gains a required `expected_ecosystem: str` keyword-only parameter,
validated against the wire response's own `ecosystem` field —
mirroring the existing `protocol_version` mismatch check immediately
above it in the same method (same unconditional posture, not an
opt-in). Every reported `capabilities` entry is validated against this
module's own closed `CAPABILITIES` set unconditionally. Both raise
`AdapterError` on mismatch, matching the existing error-message style.
`adapters/haskell.py`'s one real call site passes
`expected_ecosystem=self.config.ecosystem` (a `core.Ecosystem` `StrEnum`
member, which compares equal to the wire's plain string).

## 2. Files created/changed

- `src/codecompass/graph.py` — `symbol_enrichment` schema (new `model`
  column), new migration function, `open_graph` wiring,
  `record_symbol_enrichment` signature.
- `src/codecompass/enrichment.py` — one call-site update.
- `src/codecompass/adapters/external_process.py` — `initialize` gains
  ecosystem/capability validation.
- `src/codecompass/adapters/haskell.py` — one call-site update.
- `tests/test_graph.py` — new migration test (mirrors the Phase 62
  `export_kind`/`note` migration test's own shape); existing
  `record_symbol_enrichment` call site updated with `model=`.
- `tests/fixtures/fake_adapter.py` — two new `FAKE_ADAPTER_MODE` values
  (`bad_ecosystem`, `bad_capability`).
- `tests/test_adapters_external_process.py` — every existing
  `.initialize()` call site updated with `expected_ecosystem="fake"`;
  two new tests for the mismatch cases.
- Standard closeout: `planning/CONTEXT.md`, `CHANGELOG.md`,
  `planning/ROADMAP.md` (Phase 74 row; `L-031`/`L-032` flipped to
  `done` in the Future-improvement backlog), retro, drift audit report,
  learning triage.

## 3. Verification

1. New migration test: a pre-Phase-74 `symbol_enrichment` table (no
   `model` column) with one real enrichment row survives migration,
   backfilled `model = NULL`; a fresh write after migration stores a
   real `model` value.
2. Existing `test_rebuild_deterministic_never_touches_symbol_enrichment`
   updated (adds `model=`) and still passes — confirms
   `record_symbol_enrichment`'s new required parameter doesn't disturb
   the "enrichment survives every rebuild" invariant.
3. `enrichment.py::apply_results` — its own existing test coverage
   (`tests/test_enrichment.py`) still passes unchanged, confirming the
   real call site (not just the isolated function) now writes a real
   `model` value, per `CLAUDE.md` §1's requirement.
4. Two new `test_adapters_external_process.py` tests: an ecosystem
   mismatch raises `AdapterError`; an unrecognized capability raises
   `AdapterError`. All 7 existing tests in that file still pass with
   `expected_ecosystem=` added.
5. `tests/test_adapter_haskell.py`'s existing coverage of `_analyze`
   (which calls the real `initialize()` through `HaskellAdapter`) still
   passes unchanged, confirming the real call site supplies a valid
   `expected_ecosystem` and existing fixture data doesn't trip the new
   capability check.
6. `scripts/check_user_docs.py --strict` and
   `scripts/check_knowledge_base.py` pass.
7. Full `pytest`, `ruff check .` clean.
8. `docs-reconstructor` per-phase drift audit — dispatch prompt
   explicitly states the required persisted report path
   (`planning/retros/_drift-audit-phase-74.md`, per Phase 72's `L-056`).
9. `L-031`/`L-032` flipped to `status: promoted`/landed in
   `planning/learnings/inbox.md` and `promoted.md`, with a real commit
   SHA (not the "this phase's own closeout commit" placeholder, since
   this phase's own commits will exist by closeout time).
10. Standard closeout: retro, `knowledge-curator` triage,
    `release-phase-auditor` DoD pass.

## 4. Deferred (explicitly out of scope for this phase)

- Any broader Priority B productisation (the claim/evidence model for
  downstream users) — a separate, much larger, unplanned effort.
- Surfacing `symbol_enrichment.model`/`vendor_enrichment.model` via any
  `codecompass query` command — no existing evidence this is needed;
  `vendor_enrichment.model` itself isn't surfaced either.
- Validating any other external-adapter wire field beyond
  `ecosystem`/`capabilities` (e.g. `adapter_name`/`adapter_version`
  format) — not named by `L-032`, no evidence it's needed.
