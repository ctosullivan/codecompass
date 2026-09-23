---
status: PROPOSAL (Phase 64, Cluster C — durable reframing; CodeCompass-specific content, kept separate per process.md's own portability split)
---

# How CodeCompass itself runs this process

[`process.md`](process.md) describes the portable core of the
Scope → Plan → Domain → Design → Implement process. This page is the
part that is specifically *how CodeCompass, this project, currently
expresses it* — useful to a contributor working in this repository, not
required for another project adopting the process itself. Everything
here traces to
[`development-methodology.md`](../../v1-redefinition/development-methodology.md)
(the source document) or `decisions/0060`.

## Stage → artifact map

| Stage | Primary artifact in this repository | Owner/role |
|---|---|---|
| Scope | A phase's own stated goal + acceptance criteria | the lead (or the requester) |
| Plan | `planning/phase-N-*.md` | the lead |
| Domain | `planning/knowledge/<slug>/` records (feature-scoped); `docs/domain/` (project-wide concepts) | `context-researcher`, reviewed by `domain-skeptic` |
| Design | `design.md` (+ Requirement/Decision records) | `documentation-agent`, reviewed by the human/lead |
| Implement | `context-packet.md` → code + tests | `knowledge-curator` (packet assembly), then the coding agent (lead or a delegated implementer) |
| *(downstream, unchanged by this process)* | drift audit, retro, learning triage, definition-of-done audit | `docs-reconstructor`, the lead, `knowledge-curator`, `release-phase-auditor` |

*(source: "Stage → artifact map (summary)")*

## Two record fields specific to this project's traceability spine

`process.md`'s traceability-spine section describes tracking where a
requirement was implemented and what verifies it, in whatever shape a
project's own records take. In this project specifically, those are two
optional fields on the existing Requirement record: `implemented_at` (a
file:line or commit reference, populated once a Requirement's status
moves to `implemented`) and `test_ref` (a test id or path, populated
once it moves to `verified`). *(source: "Traceability spine," the two
new optional Requirement fields)*

## The domain-corpus freshness mechanism

CodeCompass's own project-wide Domain-stage output
([`docs/domain/`](../../../docs/domain/), Phase 63D) is treated as a
point-in-time conclusion, not a permanent fact, and is reconsidered at
three existing checkpoints rather than through a new standing process:

1. **Per-phase drift audit** — the same independent audit that checks
   whether a phase's change made any current-truth doc false also
   checks whether the phase touched a file, symbol, or behaviour that a
   `docs/domain/concepts/*.md` page's own references block cites. A hit
   is flagged as a **domain-claim staleness candidate** — not itself a
   finding that something is wrong, only that it's now worth a second
   look.
2. **Retro** — a real staleness candidate gets named in the phase's own
   retrospective report, like any other honestly-disclosed finding.
3. **A one-time milestone reconciliation** (Phase 65 in this project's
   own roadmap) re-reviews every staleness candidate accumulated since
   the corpus was last approved, resolving what it can with fresh
   evidence and escalating only genuine remaining ambiguities to the
   actual domain/product owner.

Because a one-time milestone reconciliation does not recur forever, this
project also runs a **per-feature freshness gate** after that milestone:
before a future feature's own Domain-stage research relies on a domain
concept carrying an outstanding staleness candidate, that candidate must
be resolved during that same feature's Domain stage — not deferred, and
not silently built on top of as though settled. *(source:
"Domain-corpus freshness and reconciliation," and its "Post-v1:
per-feature freshness gate" subsection)*

## The one governance tightening worth knowing about

Earlier in this project's history, during its own early, single-person
dogfooding, the lead was explicitly permitted to stand in for the actual
project owner when ruling on a domain ambiguity, with that stand-in
disclosed in the record. As of the point the source document was
written, **that allowance was withdrawn**: no agent or lead may rule on
a genuine domain/product ambiguity in the actual owner's place, from
that point forward, including during further dogfooding. Every real
Decision record produced before that point was made this way; every one
made after it must be a real ruling by the actual owner, or the
ambiguity stays explicitly open. *(source: stage 3's "New: independent
adversarial review" section, and `decision.md`'s own counterexample in
[`docs/domain/concepts/decision.md`](../../../docs/domain/concepts/decision.md)
for the concrete record-level evidence of this — cited here since it is
the same fact the domain corpus's own Decision page independently
documents from the artifact side)*

This is named here specifically because it is the one place this
project's own history shows the "no stand-in" rule was *not* always
true — worth knowing for a contributor reading an older Decision record
and wondering why its own provenance note discloses a stand-in that a
newer record would not be allowed to.

## Track record referenced by the source document

The source document names specific phases where this process (or parts
of it) has actually been exercised, as evidence the process works in
practice rather than only on paper — including a planned fresh-agent
acceptance test at this project's own final v1 validation phase, checking
whether someone with no prior context can discover this process,
recognize genuinely unresolved uncertainty as such, and produce a
sensible design for a small real change. That tally is itself
CodeCompass-roadmap-specific and changes as more phases land; see the
source document's own "Where this gets exercised before v1" section for
the current count rather than duplicating a number here that would go
stale.
