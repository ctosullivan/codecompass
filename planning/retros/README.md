# Phase retros

One retro per phase, authored by the lead at phase end:
`planning/retros/phase-NN-<slug>.md`. Producing it is a Definition-of-Done
condition (`CLAUDE.md` §5). Format: [`TEMPLATE.md`](TEMPLATE.md).

## Why

- **Process feedback has somewhere to go.** Friction in the workflow
  itself (unclear agent boundaries, a step that added nothing, a handoff
  that dropped context) is captured while it's fresh, not lost.
- **Lessons surface into the learning lifecycle.** The
  `knowledge-curator` reads each retro during triage and files anything
  promotable as a candidate learning (`planning/learnings/`).
- **GATE DA and later consolidation points have real material.** Phase 43
  (GATE DA) asks "did each role earn its keep?" — the accumulated retros
  are the evidence.

## What a retro is / isn't

- **Is:** a short, honest record that also *orients* a future session in
  the arc — **where we are** (this phase's place in the stage/milestone,
  what the previous phase(s) set up, the state now), goal, what actually
  shipped vs. the plan, **what worked** (keep doing) and **what didn't
  work** (stop / fix), the generalizable lessons, concrete
  process-improvement suggestions, and **where we're going** (the next
  phase(s), any gate ahead, whether the trajectory was confirmed or
  changed).
- **Isn't:** a status report (that's `CONTEXT.md`, which is overwritten —
  retros accumulate as a running narrative), a changelog entry (that's
  `CHANGELOG.md`), or a place for canonical decisions (those go to
  ADRs / docs via the curator).

Full section list: [`TEMPLATE.md`](TEMPLATE.md).

A **trivial phase** gets a few lines — "where we are" in one sentence,
goal, "shipped as planned", "what worked / didn't: nothing notable",
"no process notes", "next: phase N". Don't pad it.

## Lifecycle

```
phase ends
   ↓
lead writes planning/retros/phase-NN-<slug>.md   (DoD condition)
   ↓
knowledge-curator reads it during triage → candidate learnings
   ↓
release-phase-auditor confirms it exists and is substantive
   ↓
GATE DA (Phase 43) + later points: retros reviewed in bulk for
process changes (roster pruning, workflow edits, CLAUDE.md proposals)
```

Retros are **not** rewritten after the fact — they're dated records, like
ADRs and ROADMAP renumbering notes.
