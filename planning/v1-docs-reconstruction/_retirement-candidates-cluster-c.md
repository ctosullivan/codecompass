---
status: PROPOSAL (Phase 64, Cluster C's own retirement-candidate input — the lead consolidates this with Clusters A and B into `concepts-to-retire.md`)
---

# Cluster C retirement candidates (domain + development-process)

## Domain half: none

`docs/domain/` was approved 2026-09-23, the same day as this dispatch.
It has not existed long enough to accrete content the current system no
longer justifies — the phase's own brief predicted this
("the domain corpus is recent and unlikely to have retirement
candidates"), and this dispatch's full read of all 19 concept pages plus
`glossary.md`/`invariants.md`/`examples.md`/`open-questions.md`/
`references.md` found nothing to propose retiring. Two items worth
noting for the lead's awareness, neither a retirement candidate:

- `docs/domain/open-questions.md` already contains an item (#6) about
  whether "adapter" is ambiguous between two senses in this project's
  own prose — that is a *content* observation already correctly
  captured in the approved corpus, not something for this cluster to
  re-flag as a retirement candidate.
- The corpus's own `open-questions.md` items #9 and #10 are real
  `src/codecompass/` implementation gaps (missing `symbol_enrichment`
  provenance column; unvalidated wire-protocol `capabilities`/`ecosystem`
  fields), already routed to `planning/learnings/inbox.md` per the
  corpus's own scope boundary. Not a documentation retirement question
  either way.

## Development-process half: none found, checked directly

The phase's own brief raised this as a real possibility ("development-
process content in `planning/v1-redefinition/` predating the
methodology's own naming might [be a retirement candidate]"). This
dispatch checked directly, rather than assuming either way:

- Searched `planning/v1-redefinition/agent-led-development.md`,
  `README.md`, and `roadmap.md` for any description of a development
  process that pre-dates or duplicates
  `development-methodology.md`'s own Scope → Plan → Domain → Design →
  Implement naming. Every hit found is a cross-reference *to*
  `development-methodology.md` (or a citation of the specific stage
  names it defines) — none is a competing or superseded description of
  the process itself.
- `planning/phase-54c-evidence-knowledge-workflow.md` (the pre-naming
  origin of the Domain/Implement-stage record mechanics) is not a
  retirement candidate either: `development-methodology.md` itself
  states explicitly that it "does not restate Phase 54c's own detailed
  record shapes, agent briefs, or lifecycle mechanics — those stay
  defined once, in that plan and in `.claude/agents/*.md`, and are only
  pointed to here." Phase 54c's plan remains the detailed reference
  `development-methodology.md` itself depends on; retiring it would
  break the document this proposal is built from.

**Conclusion**: no retirement candidate found in either half of this
cluster's own scope. This is a checked "none," not an unchecked
assumption — see the greps and full-page reads this report is grounded
in, described in this dispatch's own final report to the lead.
