# Phase 78 amendment — corrective review of the exit decision

A post-completion review (direct user request, 2026-10-02, following
Phase 78's terminal commit `3b751c8`) found the original exit decision's
own evidence rule logically insufficient. This record documents the
correction. **The original trial and its evidence are preserved
unaltered** — `planning/reference-projects/ledgerkit/06-*.md` are
untouched; this amendment adds new evidence (`07-cg001-corrective-reevaluation.md`)
and a new decision (`decisions/0070`), it does not rewrite history.

## What was found wrong

1. **The `CG-001` `not-recurred` rule (Phase 78 plan §4 Outcome 2) was
   defined by relative cost-parity** ("a cost... no worse than the
   baseline agent's own direct exploration"), not absolute materiality.
   Both arms could incur the same substantial cost precisely *because*
   CodeCompass lacks the relevant capability — cost-parity between two
   arms that both lack it proves nothing about whether the capability,
   if built, would help. This is valid evidence for context advantage
   (a separate question); it was wrongly used to decide `CG-001`'s own
   outcome too.
2. **The trial's own task conflated existing and proposed relationships.**
   Of the five chain links both agents derived, only one
   (`ReportSpec`/`ReportSection` ↔ `balance_from_spec`) already existed
   and was therefore a genuine test of whether a relationship-indexing
   capability would help; the other four were new-code design work no
   such capability could ever shorten. Neither the original Stage 2
   evaluation nor the exit-decision triage separated these, overstating
   how thoroughly the trial actually tested the hypothesis.
3. **An asymmetric evidence rule**: the plan's own §4 Outcome 1 treated a
   differently-shaped positive result as satisfying the recurrence bar,
   while the exit-decision triage declined to apply the same logic to
   the negative result actually obtained — correct in isolation, but
   never stated as a general, symmetric rule applying to both
   directions.

## What was done

1. A fresh, independent re-evaluation of the **existing** trial evidence
   (no re-run, no new dispatch against Ledgerkit, real or scratch) —
   `planning/reference-projects/ledgerkit/07-cg001-corrective-reevaluation.md`.
   Separated `CG-001`'s outcome (absolute materiality: not-recurred, on
   the one tested existing relationship, at near-zero marginal cost) from
   context advantage (LOW, unchanged, baseline comparison legitimate
   here specifically) from applicability (**partial**, not adequate — the
   decisive finding).
2. Per the corrective amendment's own explicit decision structure, a
   **partial** applicability finding is treated the same as inconclusive
   for deciding Priority A's own exit question — it cannot carry a
   strategic closure decision, regardless of which way the one thin
   slice actually tested reads. **Priority A is reopened**, not closed.
3. `decisions/0069` is superseded by `decisions/0070` (preserved
   unedited, per `CLAUDE.md` §2's append-only rule) — the new ADR states
   the corrected conclusion, the symmetric evidence rule (a differently-
   shaped instance tests the broader hypothesis at the track level only,
   never `CG-001`'s own status field, in either direction), and names a
   narrowly-scoped follow-up candidate task (not run): Ledgerkit's own
   backlogged `stats` query-support extension, every one of whose
   relevant relationships already exists today — live-verified before
   being named.
4. `CG-001`'s inbox entry, `planning/ROADMAP.md`'s Priority A row,
   `planning/CONTEXT.md`, `CHANGELOG.md`, and
   `planning/reference-projects/ledgerkit.md` all reconciled to describe
   reopening accurately, without altering the original trial's own
   evidence.
5. A bounded sketch for the named follow-up trial
   (`planning/phase-78-amendment-followup-plan.md`) — explicitly not
   approved, not started, flagged for review.

## Lessons

- **A decision rule defined by relative comparison (treatment vs.
  baseline) can silently substitute for a question that actually needs
  absolute judgment (would a capability have helped at all).** The two
  only coincide when at least one arm has the capability being tested;
  when neither arm's available tooling can answer the specific question
  at hand, cost-parity is guaranteed by construction and tells you
  nothing. Any future trial's own evidence-bar definition should name
  which of its own criteria require absolute judgment versus relative
  comparison, explicitly, before the trial runs — not conflate them into
  one "cost no worse than baseline" test.
- **A producer/consumer chain spanning both existing and proposed code
  needs its own existing/proposed split stated before the trial, not
  discovered afterward.** A capability-advantage trial's own task
  selection should prefer, or at minimum flag in advance, tasks whose
  entire relevant relationship graph already exists — a design task will
  always mix genuine retrieval questions with inherent, un-shortcuttable
  design effort, diluting the measurement in ways that are easy to miss
  if the chain is only examined after the fact.
- **An evidence rule stated for one outcome direction needs an explicit
  check for the opposite direction before being treated as symmetric.**
  The original plan's own recurrence-bar language was written thinking
  about what would count as positive evidence; nobody checked, until
  this review, whether the same language would produce a coherent answer
  for negative evidence too.

## Links

- Superseded ADR: `decisions/0069-priority-a-closed-cg-001-tested-and-not-recurred.md`
  (preserved unedited)
- Corrective ADR: `decisions/0070-phase-78-exit-decision-corrected-priority-a-reopened.md`
- Corrective re-evaluation: `planning/reference-projects/ledgerkit/07-cg001-corrective-reevaluation.md`
- Follow-up sketch (unapproved): `planning/phase-78-amendment-followup-plan.md`
- Original Phase 78 retro (unaffected, historical): `planning/retros/phase-78-priority-a-closeout-and-second-ledgerkit-trial.md`
- Governing prompt: `planning/phase-78-amendment-corrective-exit-decision-prompt.md`
