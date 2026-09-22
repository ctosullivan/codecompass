---
status: DRAFT — pending domain-skeptic review and actual-user approval
---

# Context packet

## Definition

A **context packet** (`context-packet.md`) is Phase 54c's own specific,
narrowly-scoped Implement-stage artifact: a curated, deliberately
smaller-than-`design.md` Markdown compaction of one feature's own
knowledge-base records, produced by a `knowledge-curator` mode only
after that feature's `design.md` reaches `status: APPROVED`, living at
`planning/knowledge/<feature-slug>/context-packet.md`
(`planning/phase-54c-evidence-knowledge-workflow.md` §6; `CL-CTXT-002`).

Its fixed section list: goal, approved semantics (compacted, not
copied), requirements (verbatim `REQ-` ids), behavioural examples
(Given/When/Then, verbatim), invariants, relevant architecture (a
pointer list), relevant symbols/files/dependencies (read `context-
graph.db` read-only if useful, never write to it), existing tests,
non-goals, deliberate upstream differences, unresolved questions
(disclosed honestly), and a provenance-references block resolving to
every `REQ-`/`DEC-`/`CL-` id it draws from.

**Explicitly excluded** from a context packet: the full research
narrative, rejected alternatives, raw Observation/Evidence detail, or
anything not reachable from an `APPROVED` record. The whole point is
that a coding agent should not need to independently rediscover the
entire feature — which requires the packet to be *smaller* than
`design.md`, not a renamed copy of it.

## What this is NOT

- **Not `design.md`.** `design.md` is the fuller, citation-carrying
  research projection an approving reviewer reads; the context packet is
  what a coding agent implements against, once `design.md` is approved.
  If the packet turns out insufficient, the coding agent reads
  `design.md` next and logs the gap in `packet-sufficiency.md` — the
  packet is not meant to be the only thing ever consulted, only the
  first and usually-sufficient thing.
- **Not a digest** (see [`digest.md`](digest.md)). A digest
  (`VendorDigest`) is generated unconditionally, on every whole-project
  `sync`, for every tracked vendor, by deterministic rendering plus a
  read-only lookup of existing AI enrichment, and lives under
  `vendor/<name>/`. A context packet is generated once, per feature, by
  a curation step gated on `design.md` reaching `APPROVED`, and lives
  under `planning/knowledge/<feature-slug>/`. Neither is a generalisation
  of the other — they solve different problems (grounding an agent about
  an external dependency vs. handing a coding agent exactly what it
  needs to implement one already-designed change).
- **Not `context-graph.db` content**, and never regenerated from it
  mechanically — the graph may be *cited* read-only inside a packet
  (e.g. `query symbol`/`query relations` output) but the packet itself
  is never a database export.
- **Not raw Evidence/Observation detail.** A packet cites `CL-`/`EV-`/
  `DE-`/`REQ-`/`DEC-` ids for traceability but does not inline their
  full content — that is what makes it "compacted," not merely
  "renamed."

## Invariants

- A context packet is only ever produced from records reachable from a
  `design.md` in `status: APPROVED` (or a `status: approved`/
  `implemented` Requirement) — never from a `proposed` or still-under-
  review design.
- A context packet never itself writes to `context-graph.db`, `src/`, or
  any record's own `status` field — it is a read-and-compact step.
- Every substantive assertion in a context packet resolves to a real
  `CL-`/`EV-`/`DE-`/`REQ-`/`DEC-` id in that same feature's knowledge
  folder — a packet with an uncited assertion is a defect in the
  packet, not an acceptable shortcut.

## Example

`planning/knowledge/doc-origin-pinned-reference/context-packet.md`, a
real, already-shipped instance: it opens "This packet is a compacted
implementation input, not a copy of `design.md`," and every substantive
bullet ends with a parenthetical citation (e.g. "`(CL-DOCORIGIN-001,
EV-DOCORIGIN-001)`") back to a specific record (`OBS-CTXT-003`,
`EV-CTXT-002`).

## Counterexample / fuzzy boundary

**None found that breaks the packet/digest or packet/design.md
boundary itself** — those two boundaries are structurally enforced (a
packet requires `design.md`'s own `APPROVED` gate; nothing else produces
one). The genuinely fuzzy edge found in this research is upstream of the
packet, not in it: `packet-sufficiency.md` (the running log of "what did
the coding agent have to consult that wasn't already in the packet") is
*not itself* part of the packet, but its entire purpose is to measure
whether the packet/context-packet boundary was drawn in the right place
for a given feature. Whether a recurring `packet-sufficiency.md` gap
should be treated as "the packet-assembly step missed something
reachable" versus "the knowledge base itself never captured it" is
explicitly left as a case-by-case judgment in Phase 54c's own text, not
a mechanically-decidable rule — an honest, still-open boundary rather
than a defect this page can resolve.

## Relationships

- **Downstream of**: the Domain and Design stages'
  Observation/Evidence/Claim/Derivation/Decision/Requirement records for
  one feature (`development-methodology.md`'s Domain/Design stages).
- **Distinct from**: [`digest.md`](digest.md) (different mechanism,
  trigger, storage location, and audience — see above),
  [`context.md`](context.md) (the packet is one narrow instance inside
  the broader "context" umbrella, never a synonym for it).
- **Feeds**: the Implement stage — the coding agent (the lead, or a
  delegated implementer) implements against the packet and logs gaps in
  `packet-sufficiency.md`.

## References

- `CL-CTXT-002` / `DE-CTXT-002` — `planning/knowledge/codecompass-domain/`
- `EV-CTXT-001`, `EV-CTXT-002`, `EV-CTXT-009`, `EV-CTXT-010`,
  `EV-CTXT-013`, `EV-CTXT-014` — `planning/knowledge/codecompass-domain/`
- `planning/phase-54c-evidence-knowledge-workflow.md` §6, §6.1
- `planning/knowledge/doc-origin-pinned-reference/context-packet.md`
- `planning/knowledge/doc-origin-pinned-reference/packet-sufficiency.md`
