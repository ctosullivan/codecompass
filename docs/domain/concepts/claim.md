---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Claim

## Definition

A **Claim** record (`CL-<feature>-NNN`) is an agent's **interpretation**,
built from one or more Evidence records. It is the *only* place a
support/contradict relationship is recorded (`supporting_evidence`/
`contradicting_evidence`) — never on the Evidence side
(`evidence.md`). Its own `status` field
(`proposed | supported | contradicted | superseded | verified`) is the
only place "how sure are we" is recorded — there is no numeric
confidence score anywhere in this model
(`planning/phase-54c-evidence-knowledge-workflow.md` §2.2). A Claim
always cites the `derivation` (`derivation.md`) that produced it.

## What Claim is NOT

- **Not Evidence.** Evidence states what was found; a Claim states what
  that means, and is the only record kind allowed to say "this
  evidence supports/contradicts this interpretation."
- **Not a Decision.** A Claim is a factual proposition about *observed
  behaviour*; a Decision (`decision.md`) is a choice about *what the
  target project does about it*. Structurally: a Claim's `supersedes`
  field only ever names another Claim, never a Decision — a Decision
  can *agree with* or *deliberately diverge from* an unchanged Claim,
  but it can never make a Claim wrong or supersede it
  (`planning/phase-54c-evidence-knowledge-workflow.md` §5.2's hard
  rule, mechanically enforced by `scripts/check_knowledge_base.py`).
- **Not the graph-level "Claim" entity-kind candidate.** Phase 57's own
  Stage E design sketch (`v1-redefinition/roadmap.md`) proposes `Claim`
  as one of several possible *graph-level* (`context-graph.db`) entity
  kinds representing provenance about *other projects'* technical
  dependencies — genuinely different in scope (a queryable database row
  about a target project, vs. a file-based record of CodeCompass's own
  reasoning about a researched feature) from this record kind, sharing
  only the word. No resolution of this naming collision exists yet; it
  is explicitly deferred to Stage E's own future Domain stage
  (`CL-EVID-003`, `CL-EVID-009`).

## Invariants

- `supersedes` only ever names a prior **Claim**, never a Decision
  (structural hard rule, `scripts/check_knowledge_base.py`'s
  `check_supersedes_never_crosses_kind`).
- A Claim is never written directly to `status: verified` by
  `context-researcher` itself — only an independent re-derivation
  (`context-evaluator`-style) or an explicit user Decision moves a
  Claim past `supported` into `verified`
  (`phase-54c-evidence-knowledge-workflow.md` §3). Confirmed in
  practice: the one real `verified` Claim on file, `CL-DEPTH-001`, was
  set by `context-evaluator (Phase 54b independent evaluation
  dispatch)`, never by `context-researcher` (`EV-EVID-005`).
- Contradicting evidence, once recorded, is retained beside supporting
  evidence — never silently discarded, even once a Claim is marked
  `supported` (`phase-54c-evidence-knowledge-workflow.md` §2.2).

## Example

`CL-DOCORIGIN-001`
(`planning/knowledge/doc-origin-pinned-reference/CL-DOCORIGIN-001.yaml`):
"The smallest correct schema-level fix for `CG-005` is one new closed
`doc_artifacts.origin` CHECK-enum value... with no change required to
any other `origin` consumer in `src/codecompass/`" — `status: supported`,
citing four Evidence records and one Derivation
(`DE-DOCORIGIN-001`), which itself traces every real `origin` consumer
across the codebase, not just the one the original context-gap filing
already named.

## Counterexample / edge case

**Every real Claim produced under this model to date — across all
three feature directories (`hledger-depth`, `doc-origin-pinned-
reference`, `haskell-api-surface-extraction`) — has
`contradicting_evidence: []` and `supersedes: null`.** The mechanism
for retaining a genuine contradiction, or for one Claim actually
revising a prior one, is structurally checked
(`scripts/check_knowledge_base.py`) but has **never once been exercised
with real content**. The Phase 54c retro discloses this explicitly as a
real, honest gap, not a claim of untested success
(`EV-EVID-004`, `EV-EVID-006`). This is the single most important
"genuinely fuzzy boundary" finding for this concept: the model's most
distinctive claimed property (preserving disagreement rather than
resolving it) is real and enforced, but currently unproven by any real
example.

## Relationships

- **Built from → Evidence** (`supporting_evidence`/
  `contradicting_evidence`), **explained by → Derivation**
  (`derivation` field, 1:1 in every real instance so far — see
  `derivation.md`'s own counterexample section for the open question
  of whether that 1:1 shape is a real invariant or an untested
  coincidence).
- **Built upon by → Decision** (`agrees_with_claim`/, unused so far,
  `deviates_from_claim`) — never revised by one.
- **Authorises, through a Decision → Requirement.**
- **Same-word, different-scope collision with → the graph-level
  `Claim` entity-kind candidate** (Phase 57, Stage E, conditional on
  GATE DD) — see "What Claim is NOT," above.

## References

- `planning/knowledge/codecompass-domain/CL-EVID-003.yaml`,
  `DE-EVID-003.yaml`, `CL-EVID-009.yaml`, `DE-EVID-009.yaml`,
  `EV-EVID-002.yaml` through `EV-EVID-006.yaml`.
- `planning/phase-54c-evidence-knowledge-workflow.md:201-229` (Claim's
  own schema), `:495-525` (§5.2, the reviewer-action table and the
  hard rule).
- Real example records:
  `planning/knowledge/hledger-depth/CL-DEPTH-001.yaml` (the one real
  `verified` Claim);
  `planning/knowledge/doc-origin-pinned-reference/CL-DOCORIGIN-001.yaml`
  through `CL-DOCORIGIN-004.yaml`;
  `planning/knowledge/haskell-api-surface-extraction/CL-HSAPI-001.yaml`
  through `CL-HSAPI-006.yaml`.
- `scripts/check_knowledge_base.py:262-291`
  (`check_supersedes_never_crosses_kind`, the mechanical hard-rule
  check).
- `planning/retros/phase-54c-evidence-knowledge-workflow.md:164-178,249-261`
  (the untested contradicting-evidence/supersedes gap, disclosed
  honestly).
- `planning/v1-redefinition/roadmap.md:1061-1087` (the graph-level
  naming-collision note).
