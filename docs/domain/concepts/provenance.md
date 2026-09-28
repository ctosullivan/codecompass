---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Provenance

## Definition

"Provenance" — *who or what produced this, from what, and when* — is
**never a record kind of its own** anywhere in this codebase. It is a
**cross-cutting concern**, realized with a structurally different
concrete shape in each of at least three independent mechanisms
(`CL-EVID-013`, superseding `CL-EVID-008`; `EV-EVID-013`):

1. **Phase 54c's own records** carry a named, method-conditional set of
   provenance fields: `repository_revision`; `source_ref`/`doc_ref`/
   `test_ref`; `performed_by`/`derived_by`/`decided_by`;
   `tool`/`tool_version`; `timestamp`
   (`planning/phase-54c-evidence-knowledge-workflow.md` §2.3's own
   adopted-fields table).
2. **All three enrichment tables** — `vendor_enrichment`, `doc_relation_enrichment`,
   and (as of Phase 74, `L-031`) `symbol_enrichment` — now carry a
   `model` `TEXT` column (a real Anthropic model id, or
   `agent:<agent-name>` for agent-driven output, per `decisions/0054`).
   **A narrower asymmetry remains**: `vendor_enrichment.model`/
   `doc_relation_enrichment.model` are `NOT NULL` from their own first
   schema version, while `symbol_enrichment.model` is nullable — a
   pre-Phase-74 row's real producer was never recorded and honestly
   backfills `NULL` rather than a fabricated value, so a
   `symbol_enrichment` row written before this migration remains
   provenance-unknown in a way no sibling-table row can be
   (`src/codecompass/graph.py:204-222, 717-751`; see "Counterexample"
   below; `EV-EVID-015`).
3. **`context-gaps`/`context-observations` entries** carry four fixed
   narrative fields: `origin`, `date`, `codecompass_revision`,
   `project`.

## What Provenance is NOT

- **Not a shared schema, base type, or table.** No evidence was found,
  anywhere in this repository's history, of an attempt to unify these
  three mechanisms under one provenance concept — each was designed
  independently, for its own producer/consumer pair, at a different
  point in this project's history (enrichment: Phase 14/22/52;
  context-gaps: Phase 43c; Phase 54c's own fields: Phase 54c).
- **Not the same thing as a `status` field.** Provenance answers "where
  did this come from"; `status` (on Evidence/Claim/Decision/
  Requirement) answers "what is this record's own current standing" —
  two orthogonal properties every record with both fields keeps
  separate.
- **Not itself evidenced by a formal Claim about "provenance" as a
  unified system** — this page's own central Claim (`CL-EVID-013`,
  superseding `CL-EVID-008`) is precisely that no such unification
  exists, not a description of one.

## Invariants

- Every Phase 54c record kind that has a `performed_by`/`derived_by`/
  `decided_by`-style field uses the **identical field shape** whether
  the actor was an agent dispatch or a human — provenance-by-actor-type
  is recorded as a value, never as a different schema
  (`phase-54c-evidence-knowledge-workflow.md` §2.3).
- No provenance field anywhere in this model is, or has ever been
  proposed as, a numeric confidence score — provenance answers "from
  what," never "how sure."

## Example

`vendor_enrichment.model` (`src/codecompass/graph.py:205-215`): a single
`TEXT NOT NULL` column. A row with `model = 'claude-sonnet-...'` was
produced by a direct, budget-gated API call; a row with
`model = 'agent:context-enrichment-agent'` was produced by a Claude
Code subagent reasoning over the same kind of source excerpt
(`decisions/0054`). Every downstream reader (`query vendor`, `check`)
distinguishes the two using this one column — no separate provenance
record exists for either.

## Counterexample / edge case

**Closed as of Phase 74 (`L-031`) — `symbol_enrichment` now has a
`model` column.** `src/codecompass/graph.py:216-222` shows five
columns, not four: `id, symbol_id, purpose, model, generated_at`. The
column was added via `_migrate_symbol_enrichment_model_column` (an
`ALTER TABLE ... ADD COLUMN`, never a drop-and-recreate — this table
holds paid enrichment output that must survive migration). `record_
symbol_enrichment`, the table's only writer, now requires a real
`model` argument for every new write; its one production call site
(`enrichment.py:427`) supplies the real Anthropic model id used for
that batch (`EV-EVID-015`, `OBS-EVID-017`, `OBS-EVID-018`). It is no
longer accurate that a row written from this migration forward cannot
be attributed to a specific producer.

**Residual, narrower, still-real asymmetry**: unlike `vendor_
enrichment.model`/`doc_relation_enrichment.model` (both `TEXT NOT
NULL` from their own first schema version), `symbol_enrichment.model`
is nullable, and every row written before this migration backfills
`NULL` — an honest "producer unknown, predates this column," not a
retroactively fabricated value. A pre-Phase-74 `symbol_enrichment` row
therefore remains provenance-unknown in a way no `vendor_enrichment`/
`doc_relation_enrichment` row (`NOT NULL` since inception) can be.
Whether this residual nullability is itself worth resolving further
(e.g. a one-time backfill heuristic, or simply accepting it as
permanent history) was not investigated here and is not decided by
this record either way.

## Relationships

- **Realized differently by → every record/table kind in this
  cluster** (see Definition, above) — the unifying concept, not a
  unifying schema.
- **Distinct from, adjacent to → the graph-level provenance features**
  Phase 57's own Stage E candidate design sketches ("distinguishing
  source-derived fact / doc statement / observed behaviour / test
  result / ADR / agent inference; per-claim version + evidence route +
  confidence state," `v1-redefinition/roadmap.md:1081-1087`) — a
  future, not-yet-built, graph-level generalisation of exactly this
  concern, conditional on GATE DD, explicitly **not** the full
  ontology "unless demonstrably required."

## References

- `planning/knowledge/codecompass-domain/CL-EVID-013.yaml` (supersedes
  `CL-EVID-008.yaml`), `DE-EVID-013.yaml`, `EV-EVID-013.yaml`,
  `EV-EVID-014.yaml`, `EV-EVID-015.yaml`, `OBS-EVID-011.yaml`
  (superseded gap, see above), `OBS-EVID-016.yaml`, `OBS-EVID-017.yaml`,
  `OBS-EVID-018.yaml`, `OBS-EVID-019.yaml`.
- `planning/phase-54c-evidence-knowledge-workflow.md:320-336` (§2.3,
  the adopted provenance-fields table).
- `src/codecompass/graph.py:204-243, 717-751` (the real enrichment-table
  schema, including `symbol_enrichment`'s `model` column and its own
  migration function).
- `decisions/0054-agent-driven-enrichment-is-a-second-non-authoritative-producer.md`.
- `planning/context-gaps/README.md`,
  `planning/context-observations/README.md` (the four-field narrative
  provenance shape).
- `planning/v1-redefinition/roadmap.md:1081-1087` (Phase 57's own
  candidate graph-level provenance generalisation).
