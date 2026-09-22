---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Derivation

## Definition

A **Derivation** record (`DE-<feature>-NNN`) records the reasoning
**process** that produced a Claim — "the derivation process that
produced them," in the governing prompt's own words
(`planning/phase-54c-evidence-knowledge-workflow.md` §2.2) — not just
the Claim's own conclusion restated. It is deliberately a **narrative
field**, not a formal proof object, explicitly avoiding "the complex
probabilistic confidence system" the governing prompt warns against. It
cites the Evidence records it reasoned from (`inputs:`) and the one
Claim it explains (`claim:`).

## What Derivation is NOT

- **Not a restatement of the Claim.** A Derivation that only repeats
  the Claim's own conclusion in different words is not doing its job —
  its value is in showing *which files were traced, in what order, and
  what was initially got wrong and how the mistake was caught*
  (`.claude/agents/context-researcher.md` step 5/6; `L-024`, the real
  learning this exact failure mode produced during Phase 54c's own
  first real run).
- **Not Evidence.** Evidence records what was found; Derivation records
  how the researcher moved from a set of Evidence records to one
  specific interpretation.
- **Not itself a citable, standalone unit of "the reasoning trail" the
  way a design.md's "known uncertainties" section is** — a Derivation
  belongs to exactly one Claim (`claim:` field, singular), and no real
  instance in this corpus has ever been cited from more than one
  Claim's own `derivation:` field.

## Invariants

- One `derivation:` field per Claim, one `claim:` field per Derivation
  — every real pair checked in this corpus points back at each other
  correctly (`EV-EVID-002`).
- `inputs:` names Evidence ids, never raw Observation ids directly —
  the Derivation reasons from synthesized Evidence, not from
  unprocessed acts of looking.
- `performed_by` is the same field shape whether the actor was an
  agent dispatch or a human standing in for one — matching every other
  provenance field in this model.

## Example

`DE-DOCORIGIN-001`
(`planning/knowledge/doc-origin-pinned-reference/DE-DOCORIGIN-001.yaml`)
explicitly narrates: "grepped `origin` across all of
`src/codecompass/*.py` (not just `graph.py`/`spec_docs.py`) and read
every hit: two more origin-write sites in `doc_mapping.py`... For each,
checked specifically whether introducing a sixth enum value could
silently break it" — this is the *process*, distinct from
`CL-DOCORIGIN-001`'s own, shorter statement of the resulting
conclusion.

## Counterexample / edge case

**Every real Claim/Derivation pair found in this corpus (11 pairs
across three feature directories) is exactly 1:1** — one Derivation per
Claim, each naming the other back. The schema's own singular
`derivation:`/`claim:` fields suggest this is intentional, but **nothing
in the schema or `scripts/check_knowledge_base.py` actually forbids** a
future Derivation from explaining more than one Claim, if two Claims
genuinely shared the same underlying reasoning process. No such
instance has ever occurred. Whether strict 1:1 is a real invariant of
this model, or simply an untested property of three small proving
cases, is an honest, currently-open question this research surfaces
rather than resolves (`CL-EVID-004`, `DE-EVID-004`).

A second, related honest gap: the governing methodology's own retro
names "can another agent explain why an important claim is believed"
as a real, passed test (a fresh agent, given only `CL-DOCORIGIN-003`'s
citation chain, correctly reconstructed the mechanism) — but that test
has been run exactly once, against one Derivation, in this project's
history. It is real evidence the mechanism *can* work, not evidence
that it reliably *does* across many Derivations of varying quality.

## Relationships

- **Explains → Claim** (1:1 in every instance so far — see above).
- **Reasons from → Evidence** (`inputs:` field).
- **Analogous in spirit to, but structurally distinct from → the
  reasoning narrative inside an ADR's own "Context"/"Alternatives
  considered" sections** (`decisions/*.md`) — both explain *why*, but a
  Derivation is scoped to one feature-behavioural Claim and lives in
  `planning/knowledge/`, never in `decisions/`.
- **Has no graph-level naming-collision counterpart** — Phase 57's own
  Stage E candidate design (`v1-redefinition/roadmap.md`) names
  `Evidence`/`Observation`/`Claim`/`Decision` as possible graph-level
  entity kinds but never `Derivation` — the reasoning-process concept
  specifically has not (yet) been proposed for graph-level
  representation.

## References

- `planning/knowledge/codecompass-domain/CL-EVID-004.yaml`,
  `DE-EVID-004.yaml`, `EV-EVID-002.yaml`.
- `planning/phase-54c-evidence-knowledge-workflow.md:231-249` (schema).
- Real example records:
  `planning/knowledge/hledger-depth/DE-DEPTH-001.yaml`;
  `planning/knowledge/doc-origin-pinned-reference/DE-DOCORIGIN-001.yaml`
  through `DE-DOCORIGIN-004.yaml`.
- `.claude/agents/context-researcher.md` step 5 ("traces every real
  implementation path... not stopping at the first plausible one") and
  step 6 (the schema/migration-mechanism test-file check added
  directly from `L-024`).
- `planning/learnings/promoted.md` (`L-024`) and
  `planning/learnings/inbox.md` (`L-024`'s own curation note — the real
  instance of a Derivation initially missing a consumer, caught during
  implementation, not during research).
- `planning/retros/phase-54c-evidence-knowledge-workflow.md:237-243`
  (the "can another agent explain a claim" test, run once, passed).
