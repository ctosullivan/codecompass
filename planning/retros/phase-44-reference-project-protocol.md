# Phase 44 retro — Reference-project protocol + context-quality eval spec

- **Date:** 2026-09-12
- **Commit(s):** *(pending — this phase's closeout commit)*
- **Agents used:** `roadmap-context-curator` (state confirmation),
  `context-evaluator` (instrument dry-run), `docs-maintainer` (reconcile),
  `docs-reconstructor` (drift audit), `knowledge-curator` (triage),
  `release-phase-auditor` (final pass)

## Where we are

Stage A (39–43e) is fully `done`; this is **Stage B's first phase**. The
2026-09-12 realignment reordered Stage B to run against **Ledgerkit**
instead of Technical Clipper, but this phase's own content is unchanged
by that reorder — `reference-project-protocol.md` and
`context-quality-evaluation.md` were always project-agnostic; only the
downstream target of the plan file this phase writes (Phase 45) moved.
This phase turns two previously prose-only design docs into operational
machinery: a registry directory, two fill-in templates, and a first live
exercise of the instrument (a self-test, not a real datapoint) — the
scaffolding every later Stage B/D/F evaluation report will be built from.

## Goal

Turn `reference-project-protocol.md` + `context-quality-evaluation.md`
into operational templates and a registry; finalise the
`context-evaluator` and `reference-project-tester` agent briefs against
them; run an instrument sanity-check dry-run; write Phase 45's plan file.
No reference project registered yet — that's Phase 45.

## Scope delivered vs planned

Delivered as planned, with one honest correction to the plan's own
premise: the plan describes the two agent briefs as having "placeholder
method sections" from Phase 40 that need finalising. On inspection, both
briefs (`.claude/agents/context-evaluator.md`,
`.claude/agents/reference-project-tester.md`) were already fully fleshed
out — no placeholder markers, no TODOs — and already referenced the exact
template filenames created this phase
(`TEMPLATE-evaluation.md`, `planning/reference-projects/`). This appears
to be a side effect of Phase 43c's own brief updates ("own / feed the new
pathways"). **No edits were needed** — "finalise the briefs" was
satisfied by verification, not by writing new content. This is recorded
explicitly rather than silently treated as "nothing to do."

One unplanned but necessary step: this checkout had **no
`context-graph.db`/`vendor/` at all** (a genuinely fresh clone — both are
gitignored). Running the instrument dry-run required rebuilding the graph
first (`codecompass sync --budget 0`, mechanical-only, no
`ANTHROPIC_API_KEY` set), which as a side effect regenerated `CLAUDE.md`'s
auto-generated routing table and `.claude/skills/codecompass/SKILL.md`'s
vendor table to reflect this environment's real installed versions and
the (accurate) "0 enriched" state. This is expected generated-artifact
behaviour, not a manual edit to `CLAUDE.md`'s governed content — but it
is technically a change to `CLAUDE.md`, so it's called out explicitly
here and was presented to the user as an explicit diff before the closeout
commit, consistent with §0's letter even though the change originates
from the tool's own generator, not an editorial hand.

## What was achieved

- `planning/reference-projects/README.md` (registry + "how an evaluation
  runs"), `TEMPLATE-registration.md`, `TEMPLATE-evaluation.md`.
- `planning/reference-projects/_instrument-dry-run.md` — a real dry-run
  of the instrument, evaluating CodeCompass's own `typer` usage against
  itself. Verdict **PASS WITH GAPS**, advantage **LOW** — every claim
  checked out against direct inspection (no incorrect/misleading
  content), but a single-symbol `query symbol` call materially
  undersold the breadth of actual `typer` usage (the option/argument/
  exit/confirm surface, not just the two `Typer()` app-construction
  sites). Confirmed: the `context-evaluator` reached ground truth by
  direct inspection only, never running a `codecompass` command itself.
- `planning/phase-45-ledgerkit-baseline.md` written, retargeted to
  Ledgerkit's real current state (Milestone 5 "CLI Filter Flags"
  `[PLANNED]` next).
- `context-evaluator` / `reference-project-tester` briefs verified
  already consistent with the new templates — no edit needed.
- `planning/context-use-log.md` gained a real Stage-B-adjacent entry
  (the dry-run's own retrieval, rated LOW — an honest, expected result
  for a single-file single-dependency self-test).
- **L-012** filed: `query symbol`'s single-symbol scope and the
  unreproducible `usage_count` figure, surfaced by the dry-run itself —
  a genuine product-quality observation from testing the *instrument*,
  distinct from (and not to be confused with) a Ledgerkit-driven finding.

## What worked

- **Running the dry-run for real, not just describing the template** —
  it immediately surfaced a real, specific gap (`query symbol`'s
  single-symbol scope) that a purely theoretical template review would
  never have found. This validates the phase's own design decision
  ("templates, not prose") by demonstrating the template actually forces
  useful rigor once filled in with real data.
- **Verifying "finalise the briefs" instead of assuming edits were
  needed** — grepping for placeholder markers before touching anything
  avoided speculative, unnecessary rewrites of already-correct agent
  briefs.

## What didn't work

- The plan's own premise about the agent briefs ("placeholder method
  sections") was stale by the time this phase ran — a minor
  plan-vs-reality drift, not a process failure, but worth naming so a
  future phase doesn't assume a plan file's background claims are
  automatically still true at implementation time.

## Lessons learnt

1. **A plan file's background/rationale claims can go stale between
   writing and implementation** (here: "placeholder method sections"
   from Phase 40, actually already fixed by Phase 43c) — always verify
   the plan's premises against current repo state before acting on them,
   not just its scope list.
2. **An instrument self-test is only worth running if it's run for
   real** — a dry-run against genuinely fresh CodeCompass output (this
   checkout had no graph at all) is a better sanity check than one run
   against a warm, already-familiar cache, precisely because it forces
   confronting the actual mechanical-only, no-enrichment baseline state.
3. **Mechanical regeneration of `CLAUDE.md`'s generated block is a real
   change to a §0-protected file, even though it's tool-generated, not
   hand-edited** — worth flagging explicitly to the user rather than
   silently folding it into a commit, even when the project's own
   generated-artifact-drift check (`check_generated_artifacts_match_source`)
   already guards its internal consistency.

## Process-improvement feedback

The 14-step workflow lists step 10 (roadmap/context reconciliation)
before step 11 (retro), 12 (triage), and 13 (audit) — but `CLAUDE.md` §5's
DoD requires the retro, triage, and audit to all exist before a phase is
marked `done`. In practice (this phase and prior ones), the curator's
*final, "flip to done"* dispatch has to happen **after** steps 11–13, not
at step 10's position in the list. Worth a small workflow-doc clarification:
step 10 as a mid-phase informational update (if state needs it) is
separate from the final done-flipping reconciliation, which happens once
per phase near the end regardless of the step numbering. Filed as a
candidate learning for `knowledge-curator` to consider promoting into an
`agent-led-workflow.md` clarification.

## Candidate learnings filed

- **L-012** — `query symbol`'s single-symbol scope undersells a vendor's
  actual usage breadth; `usage_count` isn't independently reproducible by
  grep. Filed from the instrument dry-run.
- One additional candidate (this retro's own process-improvement note
  above, re: step 10 vs. 11–13 ordering) — to be filed by
  `knowledge-curator` at triage from this retro's contents, per step 12's
  instruction to mine the retro itself.

## Where we're going

- **Next: Phase 45** (`planning/phase-45-ledgerkit-baseline.md`) —
  register Ledgerkit at a pinned commit, run CodeCompass against it
  as-is, `context-evaluator` baseline report, `context-health-planner`'s
  first genuine solo run. No gate blocks it.
- **Trajectory: confirmed.** No change to Stage B's shape from this
  phase's findings — the instrument works as designed; its one gap
  (single-symbol query granularity) is exactly the kind of evidence
  Stage C (GATE DB) exists to weigh, not something to react to now.

## Time / cost note

Single session. `codecompass sync --budget 0` ran once (mechanical only,
$0 spend — no `ANTHROPIC_API_KEY` set in this environment). No other AI
spend. No `src/codecompass/` change, no test change (full suite
re-verified: 554 passed / 2 skipped, `ruff` clean).
