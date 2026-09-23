---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Decision

## Definition

A **Decision** record (`DEC-<feature>-NNN`) is the **one record kind
only a human/project-owner authors or explicitly ratifies**
(`planning/phase-54c-evidence-knowledge-workflow.md` §2.2). It records
**chosen target-project behaviour** — never a revision of what was
factually observed upstream. It names what it agrees with
(`agrees_with_claim`) or, if applicable, what it deliberately diverges
from — but never *supersedes* a Claim; a Decision's own `supersedes`
field only ever names a prior **Decision** (§5.2's hard rule,
mechanically enforced).

## What Decision is NOT

- **Not a Claim, and never a substitute for one.** A Claim is a
  factual proposition about observed behaviour; a Decision is what the
  target project chooses to do about it. A Decision can only ever
  *agree with* or *deliberately diverge from* an unchanged, still-valid
  Claim — it cannot make a Claim wrong (`claim.md`).
- **Not a `context-gaps`/`context-observations` promotion outcome
  directly.** Those queues promote into a Stage C/E *roadmap* decision
  (an ADR, a new detection heuristic, a new graph capability) — a
  different, project-architecture-scoped kind of decision from a
  per-feature Decision record inside one `planning/knowledge/<slug>/`
  directory, even though both are, in the end, "the project owner
  choosing something."
- **Not the graph-level "Decision" entity-kind candidate.** Phase 57's
  own Stage E design sketch names `Decision` as a possible graph-level
  entity kind alongside `Evidence`/`Observation`/`Claim`, for a
  different purpose (provenance about other projects' dependencies) —
  the same naming collision documented on `claim.md`/`evidence.md`,
  unresolved, deferred to Stage E's own future Domain stage
  (`CL-EVID-009`).
- **Not (as of this research) ever actually authored by an independent
  human reviewer in this project's own history** — see the
  counterexample below.

## Invariants

- `supersedes` only ever names a prior **Decision**, never a Claim
  (mechanically enforced, `scripts/check_knowledge_base.py`).
- A Decision never resolves a factual contradiction between Claims —
  it can only choose which already-evidenced Claim the project builds
  on (`phase-54c-evidence-knowledge-workflow.md` §2.2).
- Per Phase 63D's own 2026-09-20 amendment
  (`development-methodology.md`), **no agent or lead may stand in for
  the actual user/domain owner on a genuine domain/product ambiguity,
  including during CodeCompass's own dogfooding, from Phase 63D
  onward** — narrower than Phase 54c's own original §5.1 allowance.

## Example

`DEC-DOCORIGIN-001`
(`planning/knowledge/doc-origin-pinned-reference/DEC-DOCORIGIN-001.yaml`)
names the new `doc_artifacts.origin` value (`pinned_reference`), the
detection mechanism to implement, and an explicit non-goal — citing
`agrees_with_claim: CL-DOCORIGIN-001` and `supersedes: null`. Its own
leading YAML comment discloses: "Reviewed by the lead, standing in for
the user/project-owner role for this Phase 54c dogfooding run
(disclosed explicitly in the phase retro...)."

## Counterexample / edge case

**Every real Decision record produced under this model to date —
`DEC-DOCORIGIN-001` and `DEC-HSAPI-001`, the only two that exist — was
authored by the lead explicitly standing in for the actual user/
project-owner role**, disclosed identically in both records' own
`decided_by` field ("project owner (lead standing in for this
dogfooding run — see retro)") and in each phase's own retro. This
means the model's own foundational property — "the ONE record kind
only a human authors" — has **never yet been tested against a real,
independent, non-standing-in human decision-maker** anywhere in this
repository's history as of this research (`CL-EVID-005`, `EV-EVID-003`).

This matters concretely, going forward: Phase 63D's own amendment (see
Invariants, above) explicitly withdraws the lead's stand-in permission
for genuine ambiguities from this point on. Any *new* Decision produced
under this exact methodology, from Phase 63D onward, must therefore
either be a real ruling by the actual user, or the ambiguity stays an
explicitly open question rather than becoming a Decision record at all
— a stricter bar than either real Decision currently on file was held
to.

## Relationships

- **Agrees with (or deliberately diverges from) → Claim**
  (`agrees_with_claim`, never `supersedes`).
- **Authorises → Requirement** (`decision:` field on the Requirement).
- **Only ever supersedes → a prior Decision.**
- **Same-word, different-scope collision with → the graph-level
  `Decision` entity-kind candidate** (Phase 57, Stage E) — see "What
  Decision is NOT," above.
- **Narrower cousin of → a Stage C/E gated roadmap decision** reached
  via `context-gaps`/learning-lifecycle promotion — both are "the
  project owner choosing something," at different scopes (one
  feature's behaviour vs. project architecture).

## References

- `planning/knowledge/codecompass-domain/CL-EVID-005.yaml`,
  `DE-EVID-005.yaml`, `EV-EVID-003.yaml`, `EV-EVID-006.yaml`.
- `planning/phase-54c-evidence-knowledge-workflow.md:250-278` (schema),
  `:495-549` (§5.2/§5.3, the reviewer-action table and the four-way
  distinction).
- `planning/v1-redefinition/development-methodology.md:78-116` (the
  2026-09-20 amendment withdrawing the lead's stand-in permission for
  genuine escalations).
- Real example records:
  `planning/knowledge/doc-origin-pinned-reference/DEC-DOCORIGIN-001.yaml`;
  `planning/knowledge/haskell-api-surface-extraction/DEC-HSAPI-001.yaml`.
- `planning/v1-redefinition/roadmap.md:1061-1087` (the graph-level
  naming-collision note).
- `planning/context-gaps/README.md:38-67` ("How it feeds the gates" —
  the separate, project-architecture-scoped decision path).
