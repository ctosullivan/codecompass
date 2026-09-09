# 0050. Phase retros and a per-phase independent docs-drift audit as DoD conditions

## Status

Accepted (Phase 41, user request 2026-09-10).

## Context

`decisions/0049` established the agent-led development model with a
`docs-reconstructor` scoped to **milestone-only** blank-slate
documentation reconstruction (Phase 60), and a learning lifecycle
(`planning/learnings/`) owned by the `knowledge-curator`.

Two gaps surfaced immediately, before the model's first real use:

1. **Nothing independent checks documentation between milestones.**
   `docs-maintainer` both edits the current-truth docs and certifies them
   accurate as part of its own step. A milestone reconstruction 20+
   phases away is the only external check — long enough for drift to
   accumulate and compound, which is exactly the failure mode `CLAUDE.md`
   §0 warns about for `CLAUDE.md` itself and `documentation-lifecycle.md`
   warns about for `architecture/overview.md` (already 1,954 lines of
   accreted history-in-a-current-doc).
2. **Process feedback had nowhere to go.** Friction in the workflow
   itself — an unclear agent boundary, a step that added nothing, a
   handoff that dropped context — was only capturable ad hoc as a
   candidate learning, with no per-phase prompt to look for it. GATE DA
   (Phase 43) asks "did each role earn its keep?" but had no accumulated
   evidence to answer from.

## Decision

Two additive `CLAUDE.md` §5 Definition-of-Done conditions, every phase:

**1. An independent per-phase docs-drift audit.** `docs-reconstructor`
gains a second mode: given the phase's *diff* (not `docs-maintainer`'s
summary), it independently checks whether any current-truth doc
(`README.md`, `docs/`, `architecture/`, `ai-docs/`) now misdescribes the
system, scoped to what actually changed about observable behaviour.
Verdict `NO DRIFT` / `DRIFT — n findings`; findings go back to
`docs-maintainer` and it re-audits. Read-only — it never edits or
proposes a rewrite. The milestone blank-slate mode is unchanged. Full
spec: `planning/v1-redefinition/documentation-lifecycle.md` §2.5,
`.claude/agents/docs-reconstructor.md`.

**2. A phase retro report.** The lead authors
`planning/retros/phase-N-<slug>.md` at phase end (a few lines for a
trivial phase): goal, scope delivered vs planned + deviations, what was
achieved, lessons learnt, process-improvement feedback, candidate
learnings filed, time/cost. The `knowledge-curator` reads it during
triage and files anything promotable. Retros are dated records — not
rewritten after the fact. They are reviewed in bulk at GATE DA and every
milestone closeout for actual process changes (workflow edits, roster
pruning, `CLAUDE.md` proposals). Template + lifecycle:
`planning/retros/README.md`, `planning/retros/TEMPLATE.md`.

Both are enforced mechanically where possible: `scripts/check_user_docs.py`
gains a check that every `done` phase (number ≥ 41) has a retro file, and
`release-phase-auditor` checks both conditions as part of its DoD audit.

Also in this ADR's scope, the learning lifecycle itself
(`planning/v1-redefinition/learning-lifecycle.md`), made operational in
this phase: candidate learnings are cheap to capture in
`planning/learnings/inbox.md` but **not authoritative** until the
`knowledge-curator` promotes them into the artifact that owns each (test
/ ADR / architecture doc / `CLAUDE.md` proposal / rule / skill / roadmap
row / `CONTEXT.md` / `CHANGELOG.md`). `planning/learnings/promoted.md` is
an append-only pointer log — the only long-lived learnings file; there is
deliberately **no** giant permanent "AI learnings" document.

## Alternatives considered

- **Milestone-only reconstruction + trust `docs-maintainer`'s
  self-certification between milestones** (the `decisions/0049` state).
  Rejected — drift compounds silently across phases, and the whole point
  of an independent-audit posture (`v0.2-implementation-execution-plan.md`'s
  recorded rule) is that self-reports are not enough.
- **Run the full blank-slate reconstruction every phase.** Rejected — a
  from-scratch re-derivation of every doc would swamp a one-line phase,
  duplicate `docs-maintainer`'s work, and produce rewrite proposals no
  one asked for. The scoped drift audit is the right weight; the
  blank-slate renewal stays a milestone activity.
- **A new dedicated "docs-auditor" agent.** Rejected — the drift audit
  and the blank-slate reconstruction are the same concern (independent
  verification of documentation against reality) at two scopes; one agent
  with two modes keeps the roster small (`decisions/0049`, GATE DA).
- **Fold retro content into `planning/CONTEXT.md`.** Rejected —
  `CONTEXT.md` is overwritten each phase (`CLAUDE.md` §4); retros must
  accumulate as dated records to be reviewable in bulk.
- **Make the retro an agent's artifact.** Rejected — only the lead saw
  the whole phase, including the parts no single agent touched. The
  curator *consumes* the retro; it doesn't write it.
- **A durable curated knowledge base instead of "promote into the owning
  artifact".** Rejected — a second place knowledge lives is a second
  place it drifts from the code; the owning artifact (a test, an ADR) is
  where a future session actually looks.

## Consequences

- `CLAUDE.md` §5 gains two conditions (approved diff, Phase 41);
  `CONTRIBUTING.md` mirrors it.
- New `planning/retros/` folder (README + TEMPLATE + one file per phase
  from 41 on). New `planning/learnings/candidates/` for when `inbox.md`
  gets unwieldy.
- `.claude/agents/docs-reconstructor.md` (dual mode),
  `.claude/agents/release-phase-auditor.md` (checks both new conditions),
  `.claude/agents/knowledge-curator.md` (reads retros),
  `planning/agent-led-workflow.md` (12 → 14 steps), and
  `planning/v1-redefinition/agent-led-development.md` +
  `documentation-lifecycle.md` all updated.
- `scripts/check_user_docs.py` gains `Finding.strict` (informational vs
  blocking findings), learnings-provenance + promoted-log checks, and the
  retro-presence check.
- Per-phase process weight goes up by roughly one agent dispatch (the
  drift audit) plus one short lead-authored file (the retro). Accepted as
  the cost of not letting docs and process feedback drift. If GATE DA
  (Phase 43) finds either mechanism isn't earning its keep, a new ADR
  supersedes this one.
