# 0062. Post-v1 priorities are task-context completeness first, ordered Priority A-F, not the old Stage E/graph-capability grouping

## Status

Accepted (Phase 72, direct user request, 2026-09-27).

## Context

Redefined-v1 (`decisions/0048`, Phases 39-70) closed with one major
decision gate deliberately left open: **GATE DD** (`planning/v1-redefinition/conditional-generalisation.md`)
— whether `context-graph.db`'s technical-dependency/provenance schema
needs a generalised ontology (a `technical_dependency` kind, an
`executable` kind, a `reference_doc` kind, first-class provenance). Stage
G was explicitly allowed to proceed without resolving it
(`decisions/0056`: "if Stage D/E were skipped per GATE DD, Stage G runs
against the Stage C product instead"), and `planning/v1-closeout.md` §3
records it as intentionally still open, with "new evidence... showing a
generalised provenance concept is actually needed" as its own stated
revisit trigger.

That evidence now exists, distilled in `planning/ledgerkit-stage-c-learnings.md`
from real work already done at Phases 54, 54b, 54c, 55, 60, and 61
against Ledgerkit's own Stage C (query-language) development. Eleven
concrete learnings emerge, most already substantially validated:

1. Every formally-evaluated Ledgerkit instance advantage-rated LOW; the
   two formal FAILs were both "context wasn't complete enough for the
   task," not "the graph wasn't big enough" (`findings.md` §1-2).
2. Execution/behavioural-path modelling (`CG-007`, `L-026`, three
   independent occurrences) is a real, unaddressed gap — structural
   proximity (imports, directory adjacency) is not what determines
   relevance.
3. Content-hash pinning proves an excerpt hasn't changed, not that its
   boundary is complete (`L-020`, already a promoted invariant).
4. A minimal Claim/Evidence/provenance model (Observation, Evidence,
   Claim, Derivation, Decision, Requirement) already exists, proven
   real at Phase 60/63D, and its own retro recommends promoting it to a
   **durable, file-based convention** — but only as
   `planning/knowledge/`'s own internal CodeCompass-development
   mechanism, never offered to a downstream user of the shipped tool.
5. That same model's contradiction-handling machinery is real but
   "structurally-checked... experimentally unproven" per its own retro
   — never exercised with genuine conflicting evidence.
6. Mechanical-vs-inferred provenance is already a well-executed
   project value (`decisions/0051`, `0054`), with two known, cheap,
   already-scoped gaps (`L-031`, `L-032`).
7. `planning/context-gaps/` already implements first-class,
   convertible-to-roadmap gap tracking — again, only for CodeCompass's
   own graph, never for a downstream project's.
8. The Scope→Plan→Domain→Design→Implement workflow
   (`decisions/0060`) already *is* the documentation-first sequence the
   Stage C evidence calls for — again, CodeCompass's own meta-process,
   not a shipped capability.
9. Independent context evaluation (`context-evaluator`,
   `packet-sufficiency.md`) is the single most consistently validated
   practice in this project's history, rated by its own retro as "the
   single highest-value mechanism this phase tested" — again internal
   only.
10. Clean-environment reproducibility is proven, load-bearing discipline
    (every reference-project phase; Phase 67's 4/4 fresh-agent test),
    but has no formalised, repeatable check.
11. `context-quality-evaluation.md` already measures advantage over "the
    default pathway" rather than graph size — the practiced metric
    already matches what should be optimised for.

**The pattern across all eleven**: this project has already built,
proven, and internally validated most of the mechanisms the user's
prioritisation request asks for — Observation/Evidence/Claim tracking,
context-gap lifecycles, independent evaluation, documentation-first
workflow, reproducibility discipline. **None of them has ever been
offered as a capability of the shipped `codecompass` tool to a
downstream user working on their own project.** They exist entirely as
this project's own development-process tooling. This is the single
largest concrete finding this ADR acts on.

Separately, `CG-001` (task-oriented retrieval edges — "what matters for
this task" cannot be built from existing graph data) remains at a single
occurrence, not yet corroborated to this project's own `context-gaps/README.md`
recurrence bar ("recurs, or is filed independently by two agents"). The
qualitative Stage C narrative above is compelling but is a different,
broader evidence class than a formal `context-gaps` recurrence —
this ADR is explicit that it does not treat the qualitative narrative as
satisfying a bar the project's own formal instrument has not
independently confirmed.

## Decision

**Post-v1 CodeCompass optimises for task-context completeness first,
not graph completeness or feature breadth**, realised as six ordered
priority tracks (`planning/ROADMAP.md`'s own "Post-v1 priorities"
section carries the live, maintained version of this list; this ADR
records the decision and its evidence, not the list's day-to-day
detail):

- **Priority A — Task context completeness.** Can CodeCompass reliably
  answer "what does a fresh agent need to safely understand, design,
  implement, or review this specific change?" Directly re-homes
  CodeCompass's own old Phase 48 (task-oriented context retrieval,
  not-funded at GATE DB for insufficient evidence at the time) and
  `CG-001`/`CG-006`/`CG-007`, now with materially more evidence behind
  the *category* of need even where individual gap entries have not
  individually recurred.
- **Priority B — Lightweight claim/evidence/contradiction model.**
  Productise Phase 54c's already-proven, already-durable-recommended
  Observation/Evidence/Claim model for a downstream user's own project,
  not `planning/knowledge/`'s internal-only use. Deliberately reuses the
  existing record shape rather than designing a new one
  (`conditional-generalisation.md`'s own "smallest model" discipline
  applies to this productisation exactly as it applied to the model's
  original design). Also closes `L-031`/`L-032` (cheap, already scoped)
  and finally exercises the contradiction-handling machinery against
  real conflicting evidence.
- **Priority C — Context gap detection and research tasks.**
  Productise `planning/context-gaps/`'s already-proven lifecycle for a
  downstream project's own unknowns, convertible into concrete tasks.
- **Priority D — Documentation-first development workflow support.**
  Package the proven Scope→Plan→Domain→Design→Implement workflow
  *shape* (not CodeCompass's own specific agent roster) as guidance a
  downstream user's process could adopt, reusing `query`/Skill/graph
  capabilities rather than duplicating them.
- **Priority E — Independent context evaluation.** Offer a repeatable
  version of the `context-evaluator`/`packet-sufficiency.md` protocol
  for downstream adoption.
- **Priority F — Clean-environment reproducibility and context-quality
  measurement.** Formalise the already-proven scratch-clone/fresh-agent
  discipline into a repeatable check; keep `context-quality-evaluation.md`'s
  existing "advantage over the default pathway" metric as primary,
  explicitly not graph size/edge count.

**GATE DD is not resolved by this decision.** The old Stage E phase
grouping (Phases 56-59, `technical_dependency`/`executable`/
`reference_doc`/provenance schema generalisation) is **superseded as a
phase group** — its candidate designs (`conditional-generalisation.md`
§2.1-2.4) are not discarded, they are re-homed under whichever Priority
above actually needs them, decided when that Priority's own phase is
planned, not pre-committed here. Individual graph-capability candidates
(`CG-001`, `CG-003`, `CG-006`, `CG-007`) remain exactly at their current
evidence status — this ADR does not promote any of them past what
`context-gaps/README.md`'s own recurrence bar requires.

**No `src/codecompass/` schema change is made by this ADR.** This is a
prioritisation decision, not a funding decision for any specific schema
change — consistent with the user's own explicit instruction not to
implement roadmap capabilities in this phase.

## Alternatives considered

- **Resolve GATE DD now, in full, funding the union of Stage E's
  candidate designs.** Rejected: most individual `context-gaps`
  candidates have not independently crossed this project's own
  recurrence bar; funding a schema generalisation on the qualitative
  Stage C narrative alone, without also meeting the project's own
  established evidence discipline, would repeat exactly the premature-
  generalisation mistake `conditional-generalisation.md` was written to
  prevent.
- **Leave GATE DD exactly as open as before, with no new prioritisation
  at all.** Rejected: the Stage C evidence is real and the user's
  request is explicit that the highest-value capabilities it
  demonstrates should be prioritised first — declining to act on
  well-evidenced internal mechanisms that have simply never been
  productised would waste real, already-proven work.
- **Treat Priorities A-F as six new phases to plan immediately.**
  Rejected (out of this phase's own scope, per the user's own
  instruction not to implement roadmap capabilities here): only
  Priority A is named as the recommended next concrete phase
  (`planning/ROADMAP.md`); the rest are tracks with success criteria,
  not yet phase-planned.

## Consequences

- `planning/ROADMAP.md`'s "Deferred / not-funded" and "Future-improvement
  backlog" sections are replaced by a "Post-v1 priorities (A-F)"
  structure; the still-relevant deferred items (Phase 24, 25, 50, the
  GATE DD graph-capability candidates) are re-homed under whichever
  priority actually informs them, per `planning/pre-v1-disposition.md`.
- `planning/v1-redefinition/conditional-generalisation.md` gains a dated
  amendment note (its own existing convention) pointing here; its
  content is not rewritten — Stage E's candidate designs remain the
  substantive technical content for whichever future Priority A/B phase
  needs them.
- The first concrete recommended next phase is Priority A, informed by
  but not identical to old Phase 48 — a fresh scoping pass is required
  when that phase is actually planned (`CLAUDE.md` §1), re-verifying
  current evidence rather than resuming Phase 48's old, GATE-DB-vintage
  scope unchanged.
- If a future phase resolves GATE DD's remaining graph-capability
  questions, or changes this priority ordering based on new evidence, it
  supersedes this ADR with a new numbered one (`CLAUDE.md` §2
  append-only rule).
