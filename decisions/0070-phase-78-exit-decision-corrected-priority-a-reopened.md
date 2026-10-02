# 0070. Phase 78's Priority A exit decision is corrected: its own
`CG-001` evidence rule was logically insufficient; Priority A is
reopened, not closed

## Status

Accepted (corrective amendment, 2026-10-02, direct user request,
following a post-completion review of `decisions/0069`). **Supersedes
`decisions/0069` — that ADR's own text is preserved unedited as the
historical record of what was decided and why at the time; this ADR
corrects its conclusion, per `CLAUDE.md` §2's append-only rule.**

## Context

`decisions/0069` closed Priority A (task-context completeness) as a
strategic capability-building track, based on Phase 78's own second
Ledgerkit trial returning a `CG-001` outcome of `not-recurred`. A
post-completion review found that trial's own evidence rule — defined in
the Phase 78 plan's own §4 Outcome 2 — was **logically insufficient**:

> "the treatment agent completes the chain-tracing step with existing
> Phase-77 surfaces... at a cost the independent `context-evaluator`
> rates no worse than the baseline agent's own direct exploration."

This defines `not-recurred` by **relative cost-parity between the two
arms**, not by **absolute materiality** (would a plausible relationship
capability have actually avoided real, avoidable work?). The flaw: both
arms could incur the *same, substantial* manual-reconstruction cost
*precisely because* CodeCompass lacks the relevant capability — relative
parity between two arms that both lack the capability proves nothing
about whether the capability, if built, would help. Cost-parity is valid
evidence for the **separate** context-advantage question (how did
treatment do relative to baseline); it was wrongly used to decide the
**`CG-001` outcome** question as well, conflating two questions the
original plan itself never actually distinguished at the decision-rule
level (only at the reporting-format level, in its own §6's closing row).

A second, independent flaw: the trial's own producer/consumer chain
(`parser.py` → `Journal` → `loader.py` → `reports.py::balance_from_spec`
→ `cli.py`) mixed one **existing** relationship a capability could in
principle expose (`ReportSpec`/`ReportSection`, `models.py:198-237`,
already consumed by `balance_from_spec`, `reports.py:600`) with **four
proposed, not-yet-existing** relationships (a new parser branch, a new
`Journal` field, a new `loader.py` extension, a new CLI command) that no
relationship-indexing capability, however complete, could ever discover
— designing new code is not a retrieval task. The original evaluation
and exit-decision triage did not separate these, overstating how much of
the trial's own effort actually tested `CG-001`'s real hypothesis.

A third flaw, named in the same review: the Phase 78 plan's own §4
Outcome 1 treats a differently-shaped, independent occurrence as
"satisfying `context-gaps/README.md`'s own recurrence bar" for *positive*
evidence (`recurred`), while the exit-decision triage's own reasoning
applied the opposite rule for *negative* evidence (`not-recurred`),
declining to let a differently-shaped instance move `CG-001`'s own
status in that direction. This asymmetry is corrected below (§ "Symmetric
evidence rule").

### Corrective re-evaluation (no re-run, existing evidence only)

A fresh, independent re-evaluation
(`planning/reference-projects/ledgerkit/07-cg001-corrective-reevaluation.md`)
re-analysed the *existing* Stage 1/Stage 2 reports — no agent was
re-dispatched against Ledgerkit, real or scratch — applying a corrected
framework that separates two questions and reassesses applicability
honestly:

- **`CG-001` outcome, judged by absolute materiality**: on the one
  genuine existing-relationship question the trial actually exercised
  (`ReportSpec`/`ReportSection` ↔ `balance_from_spec`), the treatment
  agent's own full-file reads (needed anyway for the design task)
  supplied the answer at near-zero marginal cost; the two failing
  `query relations` calls cost a self-corrected few seconds, confirmed
  against the treatment report's own trace. **Not-recurred, on this one
  tested link.**
- **Context advantage (a genuinely separate question)**: **LOW,
  unchanged** — baseline comparison is legitimate evidence here, and
  decisive: both arms independently derived the identical chain at
  comparable depth, with zero CodeCompass access on the baseline side.
- **Applicability, assessed honestly — the decisive finding for this
  ADR**: **partial, not adequate.** Only one of the five chain links the
  trial actually traced (`ReportSpec`/`ReportSection` ↔
  `balance_from_spec`) is a genuine existing-relationship question any
  capability could in principle answer. The other four are proposed,
  not-yet-existing design work outside any indexing capability's
  possible scope. The single largest cost in the whole trial (tracing
  `parser.py`'s own directive-dispatch order — the treatment agent's own
  "single most important read") is intra-function control flow, not a
  symbol/file/test/doc relationship at all, and was paid identically by
  the baseline agent with zero CodeCompass access — confirmed intrinsic
  to the codebase, not a tooling gap.

### Applying the corrected decision tree

The corrective amendment's own decision tree treats a **partial**
applicability finding the same as an inconclusive one for the purpose of
deciding Priority A's own exit question — a trial that only thinly
exercises the actual hypothesis, with most of its apparent cost coming
from un-indexable new-code design work, **cannot carry a strategic
track-closure decision**, even where the one thin slice it did test
happens to read `not-recurred`. This is not a rejection of the
re-evaluation's own materiality finding (which stands, and is recorded
below as real, genuine evidence) — it is a recognition that a single,
mostly-inapplicable trial is too weak a test of the broader `CG-001`
hypothesis to settle a whole priority track's own future, one way or the
other.

**Priority A is therefore reopened, not closed.** `decisions/0069`'s own
closure — "Priority A... is closed as a strategic capability-building
track... its own success criterion is judged met" — is withdrawn. The
accumulated evidence (Phases 75/76/77's own LOW-to-MODERATE results,
plus this trial's own partial, inconclusive-strength `not-recurred` data
point) justifies **pausing further Priority A capability investment as
not currently justified by demonstrated marginal benefit** — a materially
weaker, more honest claim than "the success criterion is met" — while
leaving the door open for a better-targeted trial, named below, before
any further strategic decision is made either way.

## Decision

1. **`decisions/0069` is superseded.** Its own text is left unedited as
   the historical record of the (corrected) original decision; it is no
   longer the operative statement of Priority A's own status.
2. **Priority A (task-context completeness) is reopened** — not closed,
   not newly funded either. No new Priority A capability is built on
   today's evidence. The track's own status is: **further investment not
   currently justified by demonstrated marginal benefit, pending one
   additional, better-targeted trial** (named below) before a real exit
   decision (closure or a narrowly-scoped follow-on) is made.
3. **`CG-001`'s own inbox entry stays `candidate`**, unaffected in status
   by this trial's result, consistent with — and now made explicitly
   symmetric by — the rule below.
4. **Symmetric evidence rule, replacing the Phase 78 plan's own
   asymmetric §4 Outcome 1 language**: a differently-shaped,
   independently-derived instance of `CG-001`'s own broader §2.6
   hypothesis — on a different project, a different concrete
   producer/consumer chain — is evidence about the **broader
   hypothesis**, tracked at the Priority-A/track level (via ADRs and
   `CONTEXT.md`, not via `CG-001`'s own status field), **regardless of
   whether its own result reads `recurred` or `not-recurred`.** It never
   by itself transitions `CG-001`'s own `status` field in either
   direction. `CG-001`'s own status changes only on direct evidence
   about its own founding edge (`graph.py::skills_index` ↔
   `cli.py::query_skills` ↔ `skill.py::render_tool_skill`) — recurring,
   or conclusively ruled out. This corrects the plan's own §4 Outcome 1
   language, which described a differently-shaped positive result as
   "satisfying the recurrence bar" without the same explicit
   track-level/entry-level separation the exit-decision triage later
   applied (correctly, but only in one direction) to the negative result
   actually obtained.
5. **A narrowly-scoped follow-up trial is named, not run, by this ADR**:
   a task exercising an **already fully-wired, existing** cross-module
   relationship, with no new-code design work diluting the measurement
   — candidate identified and live-verified (not invented): Ledgerkit's
   own backlogged "full `stats` query support" / "`stats`:
   per-reporting-interval output" work (`ROADMAP.md`, Stage D), which
   extends an **already-existing, already-wired** chain
   (`cli.py`'s existing `stats` command → `models.py::Journal.stats()`
   → `reports.py::stats()`/`JournalStats`, all confirmed live to exist
   today — unlike the `ReportSpec`-parsing task's own four not-yet-
   existing links). A bounded plan for this follow-up is sketched
   separately (`planning/phase-78-amendment-followup-plan.md`) for
   review — **not approved, not started, not part of this ADR's own
   decision**.

## Alternatives considered

- **Retain Priority A's closure with corrected rationale** (the
  corrective amendment's own first possible outcome). Rejected: the
  re-evaluation's own honest applicability finding is **partial**, not
  adequate — per the corrective amendment's own explicit decision
  structure, a partial/inconclusive-strength result cannot justify
  retaining a strategic closure, even where the thin slice actually
  tested reads `not-recurred`. Retaining closure on this evidence would
  repeat, in a new, subtler form, the same mistake `decisions/0069`
  itself was found to have made: treating a trial's own stated
  conclusion as sufficient without checking whether the trial's own
  design actually supported that conclusion.
- **Treat the `CG-001` outcome (`not-recurred`) and reopen `CG-001`'s own
  inbox status to reflect it.** Rejected: this would repeat the
  asymmetry being corrected here — a differently-shaped instance was
  never going to move `CG-001`'s own status field positively either (per
  the plan's own cited precedent, Phase 43c/47/75), so it should not be
  allowed to do so negatively.
- **Run a third trial immediately rather than first recording this
  correction.** Rejected: the corrective amendment's own instruction is
  explicit — stop after committing the corrected documentary/planning
  state; any follow-up is planned, not executed, pending review.

## Consequences

- `planning/ROADMAP.md`'s Priority A row is corrected to describe
  reopening (further investment not currently justified, pending one
  better-targeted trial), not closure.
- `planning/context-gaps/inbox.md`'s `CG-001` entry gains a further
  curation note recording this correction, without altering its own
  prior entries.
- `planning/reference-projects/ledgerkit.md`'s own row 06 gains a
  cross-reference to this correction and the planned row 07 follow-up.
- `decisions/0069` remains on record, unedited, as the historical
  account of the original (now-corrected) decision and its own
  reasoning — a future reader comparing the two sees exactly what
  changed and why.
- If the narrowly-scoped follow-up (§ Decision, point 5) runs and
  produces an applicable result, it supersedes this ADR with a new
  numbered one recording the real exit decision — closure, or the
  smallest evidence-supported follow-on capability — per this project's
  own established append-only pattern (`decisions/0066`→`0067`→`0068`
  precedent).
