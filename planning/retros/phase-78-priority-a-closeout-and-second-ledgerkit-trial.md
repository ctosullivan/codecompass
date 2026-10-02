# Phase 78 retro — Priority A backlog rationalisation + second Ledgerkit validation trial

## Goal

Audit every open Priority A backlog/context-gap item, design and run a
second, differently-shaped Ledgerkit trial testing `CG-001`'s own
first-party-relationship hypothesis for real (with its evidence bar
fixed in advance), and apply the resulting, independently-confirmed
Priority A exit decision — closure or one narrowly-scoped follow-on,
never decided by assertion.

## Delivered vs. planned

Everything in the plan's own Definition of Done (§10) delivered:

1. The plan, already drafted and twice-amended, was approved by direct
   user instruction ("Implement phase 78 plan") and its §0 verified
   current state re-confirmed live before any dispatch.
2. The trial ran to an applicable result: seed-then-fork scratch clones,
   fixture-equivalence confirmed clean, Stage 1 discovery/design
   dispatched for both arms with clean read-scope-symmetric boundary
   checks, Stage 2's independent `context-evaluator` assessment
   completed and persisted (PASS WITH GAPS, advantage LOW, `CG-001`
   outcome **not-recurred** on a confirmed-applicable task), Stage 3
   correctly not run per the evaluator's own documented, evidence-based
   call.
3. §7.2's decision gate was applied by an independent `knowledge-curator`
   triage — not a rubber-stamp of the Stage 2 report, but a genuine
   second independent re-derivation of both load-bearing claims directly
   against the real schema/code and both agents' own contemporaneous
   research traces. **Branch A fired**: Priority A closed (`decisions/0069`).
4. §3's backlog disposition table was re-confirmed, item by item, not
   assumed — `CG-010`'s own independent maintenance-backlog funding
   explicitly unaffected.
5. Standard closeout sequence running now (this retro, learning triage,
   docs drift audit, independent completion audit, terminal
   reconciliation).
6. `planning/ROADMAP.md` will reflect the real outcome once the terminal
   reconciliation lands — not marked `done` until the independent audit
   passes, per `CLAUDE.md` §5.

## What went well, worth keeping

**The three-stage trial restructuring (the plan's own second-revision
fix for its first draft's methodological confound) worked exactly as
intended.** Discovery/design comparison, then an independent evaluation
sufficient on its own to decide the exit question, with an optional
implementation check delegated to the evaluator's own non-self-interested
judgement rather than the lead's. The evaluator declined Stage 3 with a
specific, evidenced reason (the question was already decisively
answered; remaining open questions were product-design uncertainties
unrelated to CodeCompass availability) — exactly the kind of judgement
call the plan's own §8 anticipated needing a non-self-interested party
for, and it worked on the first real attempt.

**The observable-research-trace requirement (§5.3.4) produced genuine,
independently-checkable corroboration, not just paperwork.** The
treatment agent's own trace recorded its CodeCompass queries as coming
*after*, and explicitly as confirmation of, work already done by direct
reading — written before any evaluator existed to shape that framing.
Both the Stage 2 evaluator and the Stage 7.2 `knowledge-curator` triage
independently cited this same contemporaneous detail as corroborating
evidence for the cost-parity finding, rather than relying on either
agent's own after-the-fact characterization of how hard the task felt.
This is the trace requirement doing exactly the job it was designed for.

**Two independent, non-rubber-stamp verification passes on the single
most consequential finding (the `CG-001` outcome) both converged on the
same result via genuinely different evidence paths** — the Stage 2
evaluator re-ran `query relations` live and read the schema; the
`knowledge-curator` triage separately re-read the schema and
`_resolve_relations` directly, plus both agents' own traces. Neither
treated the other's conclusion as sufficient on its own.

## What was real friction, not a defect

**`codecompass`'s zero-question bootstrap tried to estimate AI-enrichment
cost for 388 doc-relationship mentions even though Ledgerkit has zero
third-party dependencies**, and aborted cleanly against `--budget 0`.
This is correct, intended behavior (the budget gate exists precisely to
prevent unconfirmed spend) and not a defect — but it meant the first
sync attempt (with `--yes`, which does *not* also cap budget) failed with
an unrelated-looking Anthropic SDK authentication error before the real
budget-gate message was reached. A future reference-project trial setup
should reach for `--budget 0` (or a small explicit cap) directly, rather
than `--yes`, when no API key is configured in the dispatch environment
and the trial doesn't need AI-enriched descriptions — saves one failed
attempt.

## Candidate learnings

Filed to `planning/learnings/inbox.md` for `knowledge-curator` triage:

- **L-081** (workflow, likely promotable): for a reference-project trial
  setup with no Anthropic API key configured in the dispatch environment,
  use `codecompass --budget 0` (or a small explicit cap) directly rather
  than `--yes` — the latter does not itself cap enrichment spend and will
  surface an unrelated-looking SDK authentication error before reaching
  the real, intended budget-gate message, on any project with doc content
  for CodeCompass to consider enriching (vendor count is irrelevant — doc-
  relation enrichment can still be estimated with zero vendors tracked).
- **L-082** (workflow, confirms rather than corrects): the three-stage
  trial structure (discovery/design comparison → an evaluation sufficient
  on its own to decide the exit question → an optional implementation
  check whose go/no-go is the evaluator's own call, never the lead's) is
  a sound general shape for any future comparative CodeCompass-advantage
  trial, not specific to this one Ledgerkit task — confirmed working
  cleanly on its first real exercise, including the evaluator correctly
  declining the optional stage with a specific, evidenced reason rather
  than defaulting to running it "to be thorough."

## Links

- Plan: `planning/phase-78-priority-a-closeout-and-second-ledgerkit-trial.md`
- Closure ADR: `decisions/0069-priority-a-closed-cg-001-tested-and-not-recurred.md`
- Trial reports: `planning/reference-projects/ledgerkit/06-*.md`
- `CG-001`'s own closeout note: `planning/context-gaps/inbox.md`
