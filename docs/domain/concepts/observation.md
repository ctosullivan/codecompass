---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Observation

## Definition

An **Observation** record (`OBS-<feature>-NNN`) is a single, dated,
reproducible **act of looking** — running a command, reading a specific
file, fetching a specific URL — recorded with exact inputs, outputs,
tool/tool version, and repository revision
(`planning/phase-54c-evidence-knowledge-workflow.md` §2.2). It is
**never itself a claim about behaviour**; several Observations are what
an Evidence record (or, directly, a Claim) cites. Its `status` field is
always `recorded` — an Observation is not itself promoted or
contradicted; only the Evidence/Claims built on it can be.

**A user or reviewer who runs an example themselves and records the
result produces the identical record shape** — the same fields, the
same kind — differing only in the `performed_by` field's value, never a
different record kind and never routed through a Decision instead
(`phase-54c-evidence-knowledge-workflow.md` §3's "user-run tests are
first-class" rule). Whether the act of looking was performed by a
dispatched agent or by a human is a fact about *who*, not *what kind of
record this is*.

## What Observation is NOT

This is the concept with the most real, name-based confusion risk in
this codebase — the literal id-prefix "OBS-" is reused for an unrelated
record shape (`CL-EVID-002`, `EV-EVID-010`):

- **Not a `planning/context-observations/inbox.md` entry.** Those
  entries are also literally titled `OBS-NNN` (e.g. `OBS-016`), but
  record something structurally different: **experience with an edge
  that already exists** in `context-graph.db` (was it useful,
  misleading, stale, redundant — `EDGE_USEFUL`/`EDGE_UNHELPFUL`/
  `EDGE_MISLEADING`/`EDGE_STALE`/`EDGE_REDUNDANT`), not a primary-
  research act of looking at a feature's own behaviour. The two share
  zero field names (`EV-EVID-010`). This id-prefix collision is **not**
  the same collision already named in `v1-redefinition/roadmap.md`'s
  Stage E section (which is about graph-level `Evidence`/`Observation`/
  `Claim`/`Decision`, a different pair of concepts) — it is a second,
  independently-found one (`CL-EVID-002`, `DE-EVID-002`).
- **Not a `planning/context-gaps/` entry.** A context-gap records a
  *believed-missing relationship*, not an act of looking at something
  that exists; it has its own, entirely different field set (origin,
  edge, edge kind, "could mechanical detection ever catch this?",
  etc. — `EV-EVID-009`) and is never promoted into an Evidence/Claim at
  all — its promotion path is a Stage C/E gated roadmap decision.
- **Not a `planning/learnings/` entry.** A learning is "how we should
  work" (a process/workflow lesson about CodeCompass's own
  development); an Observation is "what was found" about a researched
  feature's own behaviour.
- **Not AI-authored graph enrichment.** Enrichment
  (`vendor_enrichment`/`symbol_enrichment`/`doc_relation_enrichment`)
  is interpretive content an agent *produces* about an already-proven
  graph fact — the end product of reasoning — not a record of the act
  of looking that produced it. Enrichment has no Observation-shaped
  antecedent at all (`EV-EVID-008`, `EV-EVID-014`).

## Invariants

- `status` is always `recorded` — never promoted, never contradicted,
  never superseded at the Observation level itself
  (`phase-54c-evidence-knowledge-workflow.md` §2.2).
- `method` is one of `executable | source_read | doc_read | test_run`;
  `tool`/`tool_version` are populated only when `method` makes them
  applicable (correctly left `null` on every real `source_read`/
  `doc_read` Observation checked — `planning/retros/phase-54c-
  evidence-knowledge-workflow.md`'s own answer to "which provenance
  fields were necessary").
- A user-run test is recorded identically to an agent-run one — only
  `performed_by` differs.

## Example

`OBS-DEPTH-002`
(`planning/knowledge/hledger-depth/OBS-DEPTH-002.yaml`): "Ran `hledger
balance --depth 2` against a hand-built nested test journal... and
compared output to the unrestricted run," with `tool: hledger`,
`tool_version: "1.52.4-g33fa849e7-20260910"`, and a `raw_result` stating
exactly what was printed — no interpretation of *why* offered here; that
belongs to `EV-DEPTH-001`/`CL-DEPTH-001`.

## Counterexample / edge case

`OBS-EVID-013`/`EV-EVID-010` found `planning/context-observations/
inbox.md`'s own template literally uses `### OBS-NNN` as its entry
heading — a genuine surface-level collision with this record kind's own
id prefix, inside the *same* repository, that a newcomer skimming both
directories' file listings could easily mistake for the same mechanism.
Nothing in either directory's own README currently cross-references the
other to warn of this — this page is the first place the collision is
named in writing.

## Relationships

- **Feeds → Evidence** (`observations:` field) and, less commonly,
  directly informs a Claim's derivation without an intermediate
  Evidence record when the schema calls for a direct source/doc/test
  citation instead.
- **Id-prefix collides with, but is otherwise unrelated to →
  `planning/context-observations/` entries** (see above).
- **Sibling-but-distinct from → `planning/context-gaps/` entries and
  `planning/learnings/` entries** — three different "something was
  noticed" queues at three different trust/purpose levels
  (`CL-EVID-010`).
- **Distinct from → the graph-level `Observation` entity-kind
  candidate** named alongside `Evidence`/`Claim`/`Decision` in Phase
  57's Stage E design sketch — same word, different scope and purpose
  (see `evidence.md`'s matching section).

## References

- `planning/knowledge/codecompass-domain/CL-EVID-002.yaml`,
  `DE-EVID-002.yaml`, `EV-EVID-001.yaml`, `EV-EVID-009.yaml`,
  `EV-EVID-010.yaml`, `EV-EVID-014.yaml`, `OBS-EVID-013.yaml`.
- `planning/phase-54c-evidence-knowledge-workflow.md:108-349` (schema),
  `:350-414` (§3, the Context Researcher role and "user-run tests are
  first-class" rule).
- Real example records: `planning/knowledge/hledger-depth/OBS-DEPTH-001.yaml`
  through `OBS-DEPTH-005.yaml`.
- `planning/context-observations/README.md`, `TEMPLATE.md`,
  `inbox.md:1-85` (the colliding "OBS-016" entry).
- `planning/context-gaps/README.md`, `inbox.md:1042-1144` (`CG-001`).
- `planning/learnings/README.md`.
- `decisions/0054-agent-driven-enrichment-is-a-second-non-authoritative-producer.md`.
