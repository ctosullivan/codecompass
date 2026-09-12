# 0052. Ledgerkit is the next reference project, not Technical Clipper

## Status

Accepted (2026-09-12, gate G11). Full plan:
`planning/v1-redefinition/realignment-2026-09.md`.

## Context

The original Stage B/D ordering (`decisions/0048`) put Technical Clipper
first as "first proof point" and Ledgerkit second as "harder second
proof point." Both were, at the time, un-evaluated hypotheses about
which project better tests CodeCompass's distinctive value. Neither
Stage B nor Stage D had started (`planning/reference-projects/` did not
exist). Live re-inspection of both projects
(`realignment-2026-09.md` §1.2/§1.3) confirms Ledgerkit's dependency
shape (hledger executable, manuals, journal syntax, query semantics,
compatibility tests, intentional divergences) is the stronger test of
context *relating*, not just context *discovery* — and it has a
concrete, already-scoped genuine next task (Milestone 5, "CLI Filter
Flags") ready to use as the Stage B baseline immediately.

## Decision

Ledgerkit becomes Stage B (Phases 44–47) and the deeper Stage D (Phases
52–55); Technical Clipper becomes a new Stage F (Phases 60–63), run
*after* Ledgerkit-driven changes land, explicitly to check they
generalise rather than overfit to accounting/hledger. Phase numbers 45
onward are renumbered (none had started); GATE letters DB/DC/DD/DE keep
their conceptual position, now scoped to Ledgerkit evidence; a new GATE
DF covers Technical Clipper's regression decision. Full detail:
`planning/v1-redefinition/roadmap.md`.

## Alternatives considered

- **Keep Technical Clipper first, run Ledgerkit second as originally
  planned.** Rejected: the strategic redirection explicitly argues
  Ledgerkit is the stronger test, and nothing has been invested in a
  Technical-Clipper-first Stage B yet, so there is no sunk cost to
  protect.
- **Run both simultaneously.** Rejected: dilutes the evidence-gated
  discipline (`README.md` R9, R11) that keeps each stage's findings
  attributable to one project.
- **Drop Technical Clipper entirely.** Rejected: it remains the best
  available check against overfitting to a single ecosystem
  (`README.md` R10), a concern the reorder makes more relevant, not less.

## Consequences

- `planning/v1-redefinition/roadmap.md`, `ledgerkit-plan.md`,
  `reference-project-protocol.md`, `context-quality-evaluation.md`,
  `conditional-generalisation.md`, `README.md`, `migration.md` amended
  (phase numbers, stage references).
- `planning/ROADMAP.md` / `planning/CONTEXT.md` amended.
- Two new Stage-A bridge phases added (43d, 43e — unrelated to this
  ADR's subject but landed in the same realignment).
- `decisions/0048` is **not superseded** — its core redefinition (agent-led
  development, evaluated relationships, real reference-project work,
  evidence-driven improvement, generalisation checks against a
  materially different second project) holds unchanged. This ADR
  narrows one part of it: the reference-project ordering.
