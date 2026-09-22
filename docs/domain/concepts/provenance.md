---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Provenance

## Definition

"Provenance" — *who or what produced this, from what, and when* — is
**never a record kind of its own** anywhere in this codebase. It is a
**cross-cutting concern**, realized with a structurally different
concrete shape in each of at least three independent mechanisms
(`CL-EVID-008`, `EV-EVID-013`):

1. **Phase 54c's own records** carry a named, method-conditional set of
   provenance fields: `repository_revision`; `source_ref`/`doc_ref`/
   `test_ref`; `performed_by`/`derived_by`/`decided_by`;
   `tool`/`tool_version`; `timestamp`
   (`planning/phase-54c-evidence-knowledge-workflow.md` §2.3's own
   adopted-fields table).
2. **Two of the three enrichment tables** — `vendor_enrichment` and
   `doc_relation_enrichment` — each carry a single `model` `TEXT`
   column (a real Anthropic model id, or `agent:<agent-name>` for
   agent-driven output, per `decisions/0054`). **`symbol_enrichment`
   carries no provenance column at all** — a real asymmetry within the
   same mechanism, not a uniform property of "the enrichment tables" as
   a group (`src/codecompass/graph.py:165-182`; see "Counterexample"
   below).
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
  unified system** — this page's own central Claim (`CL-EVID-008`) is
  precisely that no such unification exists, not a description of one.

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

`vendor_enrichment.model` (`src/codecompass/graph.py:165-175`): a single
`TEXT NOT NULL` column. A row with `model = 'claude-sonnet-...'` was
produced by a direct, budget-gated API call; a row with
`model = 'agent:context-enrichment-agent'` was produced by a Claude
Code subagent reasoning over the same kind of source excerpt
(`decisions/0054`). Every downstream reader (`query vendor`, `check`)
distinguishes the two using this one column — no separate provenance
record exists for either.

## Counterexample / edge case

`symbol_enrichment` (`src/codecompass/graph.py:177-182`) has **no
provenance column at all** — `id, symbol_id, purpose, generated_at`,
four columns, none naming a producer. This is a real, structural
asymmetry within the *same* enrichment mechanism decisions/0054
describes as uniformly distinguishable "using a column that has existed
since Phase 14" — that statement is accurate for
`vendor_enrichment`/`doc_relation_enrichment`, but not, on direct
inspection, for `symbol_enrichment`, which has no `model` column to
read at all (`OBS-EVID-011`). Whether this is a genuine gap
(`symbol_enrichment` rows currently cannot be attributed to a specific
producer at all, agent or automated) or an intentional simplification
this research did not find a stated rationale for is left as an
observed, unresolved fact — not something this research resolves,
since resolving it would require deciding whether to add a column,
which is a `src/codecompass/` change out of this phase's own scope.

## Relationships

- **Realized differently by → every record/table kind in this
  cluster** (see Definition, above) — the unifying concept, not a
  unifying schema.
- **Distinct from, adjacent to → the graph-level provenance features**
  Phase 57's own Stage E candidate design sketches ("distinguishing
  source-derived fact / doc statement / observed behaviour / test
  result / ADR / agent inference; per-claim version + evidence route +
  confidence state," `v1-redefinition/roadmap.md:1080-1086`) — a
  future, not-yet-built, graph-level generalisation of exactly this
  concern, conditional on GATE DD, explicitly **not** the full
  ontology "unless demonstrably required."

## References

- `planning/knowledge/codecompass-domain/CL-EVID-008.yaml`,
  `DE-EVID-008.yaml`, `EV-EVID-013.yaml`, `EV-EVID-014.yaml`,
  `OBS-EVID-011.yaml`, `OBS-EVID-016.yaml`.
- `planning/phase-54c-evidence-knowledge-workflow.md:320-336` (§2.3,
  the adopted provenance-fields table).
- `src/codecompass/graph.py:165-203` (the real enrichment-table
  schema, including `symbol_enrichment`'s missing `model` column).
- `decisions/0054-agent-driven-enrichment-is-a-second-non-authoritative-producer.md`.
- `planning/context-gaps/README.md`,
  `planning/context-observations/README.md` (the four-field narrative
  provenance shape).
- `planning/v1-redefinition/roadmap.md:1080-1086` (Phase 57's own
  candidate graph-level provenance generalisation).
