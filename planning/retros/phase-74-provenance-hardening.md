# Phase 74 retro — Priority B provenance hardening (`L-031` + `L-032`)

- **Date:** 2026-09-27.
- **Commit(s):** `1dc228f` (plan + ROADMAP row), `050e366`
  (implementation: `symbol_enrichment.model`, adapter
  ecosystem/capability validation), `40e7718` (documentation closeout —
  6 current-truth doc locations + 5 `docs/domain/` locations fixed,
  `CL-EVID-008`→`CL-EVID-013` supersession), `3d0ed30` (learnings
  log/ROADMAP landing).
- **Agents used:** `docs-maintainer` (initial reconciliation — see "What
  didn't work"), `docs-reconstructor` (per-phase drift audit),
  `domain-skeptic` (domain-corpus freshness, twice — Stage E cluster
  spillover check and the L-031/L-032 gap-closure cluster),
  `context-researcher` (Claim supersession, `CL-EVID-008`→`CL-EVID-013`).

## Where we are

Second concrete implementation phase, continuing directly from Phase 73
per direct user instruction. Both fixes were already fully scoped by
`domain-skeptic`'s own Phase 63D review — no fresh design needed.

## Goal

Close `L-031` (`symbol_enrichment` has no producer-attribution column)
and `L-032` (external adapter wire protocol's `ecosystem`/`capabilities`
fields received but never validated).

## Scope delivered vs planned

Delivered as planned. `symbol_enrichment.model` added nullable (an
honest backfill for pre-existing rows whose real producer was never
recorded — not a fabricated `NOT NULL` default, a deliberate design
choice this phase's own plan named upfront). `ExternalAdapterProcess.initialize`
gained a required `expected_ecosystem` parameter and closed-set
capability validation, both raising `AdapterError` unconditionally,
matching the existing `protocol_version` check's own posture.

## What was achieved

Both fixes landed with full test coverage through their real production
call sites (`enrichment.py`, `haskell.py`). Both were also documented as
currently-open gaps across **eleven** current-truth and domain-corpus
locations (`README.md` twice, `architecture/context-graph-schema.md`,
two developer-facing protocol docs, and five `docs/domain/` concept
pages plus two `open-questions.md` items) — all found and fixed this
phase, four of the five domain-corpus locations fully closed, one
(`provenance.md`) correctly stated with its own narrower residual
nullability caveat rather than declared fully closed.

## What worked

- **`domain-skeptic`'s adversarial verification caught a real nuance
  the lead's own plan missed**: `symbol_enrichment.model`'s nullability
  is a genuine, narrower residual asymmetry with its sibling tables
  (which are `NOT NULL` from inception) — the domain-corpus replacement
  text states this explicitly rather than letting a "gap now closed"
  edit overclaim full symmetry. This is exactly the adversarial
  scrutiny this role exists to provide, working on the lead's own
  freshly-written code, not just on inherited planning-doc citations.
- **The find-vs-revise write-boundary split, established at Phase 72,
  worked cleanly a second time**: `domain-skeptic` named the exact
  fixes but never touched `docs/domain/`; `context-researcher` revised
  the one affected Claim record (`CL-EVID-008`→`CL-EVID-013`); the lead
  applied the concept-page text. No confusion about who does what.

## What didn't work

**The initial `docs-maintainer` reconciliation pass, dispatched before
the domain-corpus check, missed six real current-truth doc locations**
(`README.md` twice, `architecture/context-graph-schema.md`,
`docs/developer/writing-an-adapter.md`,
`docs/protocol-adapter/integrating-a-new-external-adapter.md` twice) —
all caught only by `docs-reconstructor`'s independent drift audit
afterward, not by the reconciliation step meant to catch them first.
This is a real process gap, not merely the audit working as designed:
`docs-maintainer`'s own dispatch prompt asked it to check `README.md`,
`docs/`, `architecture/`, `ai-docs/`, and `CONTRIBUTING.md`, and it
reported finding nothing needing a fix — but two of the six misses were
in `README.md` itself, the most prominent current-truth doc in the
project. Unlike Phase 71/72's own rework (a missing report file, an
incomplete domain-corpus fix), this is the first instance this session
of the *ordinary* reconciliation step itself under-delivering on a
straightforward, non-edge-case doc update.

## Lessons learnt

**A `docs-maintainer` dispatch that names specific files it already
checked (as a courtesy, to save the audit re-deriving them) may cause
the audit to over-trust that specific list rather than doing its own
full sweep** — this phase's own `docs-reconstructor` dispatch prompt
explicitly listed the files `docs-maintainer` said it checked, and the
audit's own report shows it re-verified those specific files
independently but then went on to find six *more* the prompt hadn't
named. The audit worked correctly here despite the risk, but the
near-miss shape (a courtesy list narrowing what gets re-checked) is
worth naming. Left for `knowledge-curator`'s own independent assessment
of whether this generalizes to a rule (e.g., "never list what another
agent already checked in an audit's own dispatch prompt, to avoid
anchoring its search") or was already a non-issue given `docs-reconstructor`'s
own report shows it searched broadly regardless.

## Process-improvement feedback

Consider whether `docs-maintainer`'s own dispatch should more
explicitly instruct a full-repository grep for every changed
symbol/behavior name (not just a directory sweep) when a phase changes
a widely-cited mechanism like `ExternalAdapterProcess.initialize` or
`symbol_enrichment` — a `knowledge-curator` question, not decided here.

## Candidate learnings filed

None directly by the lead — the lesson above is described but
deliberately left for `knowledge-curator`'s own independent triage.

## Where we're going

Priority B's own broader productisation (a downstream-user-facing
claim/evidence model) remains entirely unplanned — this phase closed
only the two already-scoped hardening items, per its own explicit
"deferred" section.

## Time / cost note

Five agent dispatches: `docs-maintainer`, `docs-reconstructor`,
`domain-skeptic` (twice), `context-researcher`. Two independent `src/`
fixes, documented across eleven current-truth/domain-corpus locations.
