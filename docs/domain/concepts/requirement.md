---
status: DRAFT — pending domain-skeptic review and actual-user approval
---

# Requirement

## Definition

A **Requirement** record (`REQ-<feature>-NNN`) is **implementation-
facing and testable** — "the thing a coding agent actually implements
against" (`planning/phase-54c-evidence-knowledge-workflow.md` §2.2). It
always cites the `decision:` that authorises it, and through that
Decision, the Claim/Evidence chain behind it. It carries a Given/When/
Then `example` and a closed `status` enum (`proposed | approved |
implemented | verified`).

## What Requirement is NOT

- **Not a Decision.** A Decision chooses target-project behaviour in
  the abstract; a Requirement is the specific, testable statement that
  implements that choice.
- **Not the same thing as an "invariant."** A Requirement is narrower
  and more specific: one single testable statement, traceable to
  exactly one Decision. A project-wide invariant
  (`docs/domain/invariants.md`, this phase's own deliverable) is a
  cross-cutting rule that need not trace to any single Decision or
  Requirement at all. The two overlap in effect — a correctly
  implemented Requirement often *is* an invariant, once shipped and
  tested — but they are not the same record kind and are not
  interchangeable citations (`invariant.md`; `CL-EVID-006`).
- **Not itself a test.** A Requirement's `example` is a Given/When/Then
  scenario a test should exercise; the requirement is the record that
  motivates the test, not the test file itself.

## Invariants

- `decision:` names exactly one Decision — a Requirement is never
  free-floating, unauthorised implementation guidance.
- `status` only ever reaches `verified` after real, direct
  post-implementation revalidation (re-running the Observations that
  established the original understanding against the shipped code) —
  never merely because the code was written
  (`phase-54c-evidence-workflow.md` §8).

## Example

`REQ-DOCORIGIN-001`
(`planning/knowledge/doc-origin-pinned-reference/REQ-DOCORIGIN-001.yaml`):
"`doc_artifacts.origin`'s CHECK constraint MUST accept a new value,
`pinned_reference`... No other origin consumer in `src/codecompass/`
requires any change for this addition alone," citing
`decision: DEC-DOCORIGIN-001`, with a Given/When/Then example and
`status: verified` (confirmed via a real `context-graph.db` rebuild,
per the phase's own Verification section, not merely asserted).

## Counterexample / edge case

The `packet-sufficiency.md` log for this same feature
(`planning/knowledge/doc-origin-pinned-reference/packet-sufficiency.md`)
records a real gap directly relevant to this concept: implementing
`REQ-DOCORIGIN-001` (a schema/migration Requirement) broke six
pre-existing tests in `tests/test_graph.py` that hard-code the schema
version literal — a real consumer of the *migration mechanism* itself
that no Observation/Evidence/Claim/Derivation record in the knowledge
base had ever inspected, because the Context Researcher's own
consumer-trace covered every **code** consumer of `origin` exhaustively
but not every **test file** asserting a schema-version literal. This
produced `L-024`, now promoted directly into
`.claude/agents/context-researcher.md` step 6. The edge case this
surfaces for Requirement specifically: a Requirement's own citation
chain (Decision → Claim → Derivation → Evidence → Observation) can be
fully internally consistent and still miss a real downstream test
consumer that the chain never happened to trace — "traceable" and
"complete" are not the same property.

## Relationships

- **Authorised by → Decision.**
- **Traceable back through → Claim/Evidence/Observation** (via the
  Decision it cites).
- **Compacted into → a context packet's own "requirements" section**
  (`planning/phase-54c-evidence-knowledge-workflow.md` §6) — verbatim,
  not summarized further.
- **Overlaps with, but is not the same record kind as → invariant**
  (see "What Requirement is NOT," above).

## References

- `planning/knowledge/codecompass-domain/CL-EVID-006.yaml`,
  `DE-EVID-006.yaml`, `EV-EVID-002.yaml`, `EV-EVID-012.yaml`.
- `planning/phase-54c-evidence-knowledge-workflow.md:279-296` (schema),
  `:698-737` (§8, implementation and revalidation loop).
- Real example records:
  `planning/knowledge/doc-origin-pinned-reference/REQ-DOCORIGIN-001.yaml`
  through `REQ-DOCORIGIN-003.yaml`;
  `planning/knowledge/haskell-api-surface-extraction/REQ-HSAPI-001.yaml`
  through `REQ-HSAPI-006.yaml`.
- `planning/knowledge/doc-origin-pinned-reference/packet-sufficiency.md`
  (Gap 1/Gap 2 — the real schema-migration test-file omission).
- `planning/learnings/promoted.md` (`L-024`) and
  `.claude/agents/context-researcher.md` step 6.
