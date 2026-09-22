---
status: DRAFT — pending domain-skeptic review and actual-user approval
---

# Invariant

## Definition

"Invariant" is **not one of Phase 54c's six formal record kinds** and
has **no dedicated schema** anywhere in this codebase
(`OBS-EVID-015`, `EV-EVID-012`). It is, instead, a plain-English label
— "a rule that must stay true" — that this repository currently attaches
to **at least three distinct artifacts**, each with its own
promotion/citation mechanism, with **no requirement that they ever
coincide** for a given rule (`CL-EVID-007`):

1. **`planning/learnings/`'s own `invariant` classification value** —
   one of eleven closed values a candidate learning can take, meaning
   specifically "this is a required behavioural invariant of
   CodeCompass's own code," whose correct promotion destination is a
   regression **test** (`planning/v1-redefinition/learning-lifecycle.md`
   §4).
2. **A narrative "things that must stay true" subsection** inside a
   per-feature `design.md`/`context-packet.md`
   (`phase-54c-evidence-knowledge-workflow.md` §6) — a *subset* of that
   document's own content, never itself a separately-citable record id.
   No real `design.md` in the current corpus even has its own
   "## Invariants" heading; invariant-like statements are folded into
   each one's "Behavioural rules and precedence" section instead
   (`OBS-EVID-015`).
3. **The project-wide `docs/domain/invariants.md` file** — this very
   phase's (63D's) own deliverable, explicitly defined as "cross-cutting
   rules that hold across multiple concepts (pulled up from individual
   concept docs where a rule isn't concept-local)"
   (`planning/phase-63d-domain-reconstruction.md` §3).

## What Invariant is NOT

- **Not a seventh record kind alongside Observation/Evidence/Claim/
  Derivation/Decision/Requirement.** This was this research's own
  initial, incorrect assumption, corrected by direct inspection
  (`DE-EVID-007`) — `planning/phase-63d-domain-reconstruction.md` §1
  lists "invariant" in the same in-scope concept list as the six formal
  kinds, with no visual distinction, which invites exactly this
  mistake.
- **Not a Requirement.** A Requirement is a single, specific, testable
  statement always traceable to exactly one Decision; an invariant (in
  any of the three senses above) need not trace to any Decision at all
  (`requirement.md`).
- **Not necessarily present in more than one of the three senses at
  once.** A rule recorded as a `planning/learnings/` `invariant`
  classification is not automatically also a per-feature design.md
  invariant or a `docs/domain/invariants.md` entry, and vice versa —
  nothing in this codebase links the three.

## Invariants (about this concept itself)

- No `kind: invariant` record has ever existed, or is checked for, by
  `scripts/check_knowledge_base.py` (`OBS-EVID-004`, `OBS-EVID-015`).
- Every real `planning/learnings/` entry classified `invariant` names
  a *code-behavioural* rule (e.g. "a re-`sync` must not silently drop a
  vendor's rows"), never a *domain-terminology* rule of the kind this
  Phase 63D corpus is producing.

## Example

`planning/learnings/promoted.md`'s `L-001` entry:
`invariant | tests/test_check_user_docs.py::TestReadmePhaseCount::
test_ignores_done_phases_in_redefined_v1_section... @ c22d8e4` — a real,
promoted `invariant`-classified learning, landed as a regression test,
exactly matching sense (1) above.

## Counterexample / edge case

This concept's own boundary is the fuzziest one in this cluster,
honestly: whether the three senses above **should** eventually be
cross-referenced, unified under one schema, or deliberately kept
separate is a real, open documentation-design question this research
surfaces but does not settle (`CL-EVID-007`). It is not a contradiction
between existing evidence — all three senses are independently real and
independently well-evidenced — but a genuine design gap: nothing in
Phase 54c's own model or Phase 63D's own plan states whether, for
example, every `docs/domain/invariants.md` entry ought to also exist (or
be checked for existence) as a `planning/learnings/` `invariant`-class
entry once it is established as project-wide truth. This is named here
as an open question, not resolved by inventing a rule that isn't
evidenced.

## Relationships

- **Pulled up from → individual `docs/domain/concepts/*.md` pages' own
  "Invariants" sections**, per this file's own sense (3).
- **Promotes (in sense 1) to → a regression test**, via
  `planning/learnings/`'s own classification→destination table.
- **Narrower than an invariant, but citable in support of one →
  Requirement** (see `requirement.md`).
- **Distinct from, but easily conflated with → a Claim's own
  "supported/verified" status** — an invariant, in any of the three
  senses, is a *statement of a rule*; a Claim's status is a statement
  of *how confident this research is* in a specific factual
  proposition. A rule can be recorded as an invariant without ever
  being backed by a formal Claim record, and vice versa.

## References

- `planning/knowledge/codecompass-domain/CL-EVID-007.yaml`,
  `DE-EVID-007.yaml`, `EV-EVID-011.yaml`, `EV-EVID-012.yaml`,
  `OBS-EVID-014.yaml`, `OBS-EVID-015.yaml`.
- `planning/v1-redefinition/learning-lifecycle.md:63-81` (§4's
  classification table, the `invariant → test` row).
- `planning/learnings/README.md:1-57`.
- `planning/learnings/promoted.md` (`L-001`, a real promoted
  `invariant`-classified learning).
- `planning/phase-54c-evidence-knowledge-workflow.md:584` (the only
  structured mention of "invariants" in the governing plan — one
  bullet in §6's context-packet section list).
- `planning/phase-63d-domain-reconstruction.md:196-198` (§3's own
  definition of `docs/domain/invariants.md`).
