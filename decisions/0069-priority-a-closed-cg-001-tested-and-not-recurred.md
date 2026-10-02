# 0069. Priority A (task-context completeness) is closed; `CG-001`'s own
relationship hypothesis was tested for real and did not recur

## Status

Accepted (Phase 78, 2026-10-02, direct user request — "Implement phase
78 plan" — following an independent `knowledge-curator` triage of the
trial's real result:
`planning/reference-projects/ledgerkit/06-priority-a-exit-decision-triage.md`).

## Context

`decisions/0062` opened Priority A (task-context completeness) as the
first of six post-v1 priority tracks, naming `CG-001` (task-oriented
retrieval edges — "what matters for this task" cannot be built from
existing graph data) as its founding, still-uncorroborated evidence.
Four real validations followed:

- Phase 73 (`CG-006`, filename-matching) — a detection fix, Stage-C
  scale, unrelated to `CG-001` directly.
- Phase 75 (Ledgerkit `cur:` query-term design) — `context-evaluator`
  verdict PASS WITH GAPS, advantage LOW. A provisional `CG-001`
  `recurred` call was made and then independently reverted by a
  `knowledge-curator` re-verification: the instance was a different
  concrete edge, on a different project, from `CG-001`'s own founding
  A↔B↔C edge — per this entry's own established recurrence-bar
  discipline, a cross-reference to the broader hypothesis, not a
  recurrence of this entry itself.
- Phase 76 (Git repository topology) — PASS WITH GAPS, advantage
  MODERATE, the strongest Priority A result to date. New gaps `CG-010`/
  `CG-011` filed (Git-topology maintenance backlog, independently
  fundable, unrelated to `CG-001`).
- Phase 77 (first-party source/symbol awareness) — PASS WITH GAPS,
  advantage LOW. `CG-009` (zero first-party-source symbol path)
  resolved. Its own plan explicitly deferred first-party *relationship*
  edges as "the most likely path to a genuine `CG-001`-shaped trial" —
  not committed to, not built.

Phase 78 claimed that deferred follow-on: it defined, in advance of
running any trial, a precise three-outcome evidence bar for `CG-001`'s
own hypothesis (`recurred` / `not-recurred` / `task-not-applicable`,
Phase 78 plan §4), then ran a second, differently-shaped Ledgerkit trial
(a genuine, currently-unimplemented Stage D task — journal-comment
`ReportSpec` parsing) structured specifically to exercise a real
producer/consumer chain of the same shape `CG-001` originally named,
using current CodeCompass (including Phase 77's `query source`/`query
source-symbol`).

The trial produced an applicable result (not `task-not-applicable`):
both a baseline agent (no CodeCompass) and a treatment agent (full
current CodeCompass) independently derived the identical real
producer/consumer chain (`parser.py` → `Journal` → `reports.py::balance_from_spec`
→ `cli.py`). CodeCompass's existing surfaces genuinely could not answer
the relationship question (`query relations ReportSpec`/`balance_from_spec`
both error "not found in context-graph.db" — confirmed by the schema
itself: no edge table exists between two `source_symbols` rows, or
between a `source_symbol` and anything else, anywhere in
`context-graph.db`). Despite this, the treatment agent reconstructed the
chain at no greater cost than the baseline's own direct exploration
(confirmed by both agents' own contemporaneous research traces, not
self-report alone, and independently cross-checked by both the trial's
own Stage 2 `context-evaluator` and a further independent
`knowledge-curator` re-verification). This is Outcome 2
(`not-recurred`) exactly as Phase 78's plan defined it in advance.

`CG-001`'s own inbox entry is **not** moved to `recurred` by this result
— applying the same edge-recurrence discipline this entry's own three
prior triage passes have consistently held (a different concrete edge,
on a different project, is the broader hypothesis being tested again,
not this entry's own founding edge recurring). It stays `candidate`,
reopenable by a genuinely new, differently-shaped occurrence. What this
trial's result *does* establish, at the track level: the one remaining
open question behind Priority A's own continued investment — whether
`CG-001`'s hypothesis would, once actually tested on a real task with a
pre-registered evidence bar, justify building new relationship-graph
capability — has now been tested for real, and found not to clear its
own bar.

## Decision

**Priority A (task-context completeness) is closed as a strategic
capability-building track.** Its own success criterion is judged met: an
independent `context-evaluator` PASS-or-PASS-WITH-GAPS record now exists
across three structurally different capability areas (query semantics —
Phase 75; Git repository topology — Phase 76; first-party source — Phase
77), at LOW-to-MODERATE advantage, never a FAIL and never a misleading
claim — plus, now, an explicit, pre-registered, evidence-checked
negative result on the one remaining open hypothesis (`CG-001`,
Phase 78). No new Priority A capability is funded on narrative alone
going forward; Priority A is not reopened absent new evidence of a
different, not-yet-tested shape.

**This closure is strategic, not operational.** It does not affect:

- `CG-010`'s own independent, already-evidenced Git-topology
  maintenance-backlog funding (`decisions/0062`'s §3.1 distinction,
  Phase 78 plan — ordinary maintenance within a capability Priority A
  already shipped is never gated on whether the track that funded it
  originally is still open to *new* capability-building).
- `CG-011`, if it ever independently recurs — the same maintenance-class
  disposition would apply.
- Any already-shipped Priority A capability (Git topology, first-party
  source, filename-matching) — all continue to be maintained on their
  own ordinary evidence.
- Priorities B-F (`decisions/0062`), which proceed on their own,
  unrelated schedule.

## Alternatives considered

- **Fund the smallest `CG-001`-shaped relationship edge anyway, on the
  strength of three prior LOW/MODERATE/LOW results plus this trial's
  qualitative narrative.** Rejected: Phase 78's plan explicitly
  pre-registered the evidence bar before running the trial specifically
  to avoid deciding this by narrative or assertion after the fact
  (`conditional-generalisation.md`'s premature-generalisation discipline,
  the same one `decisions/0062` already applied). The trial's own
  applicable result is a `not-recurred` outcome by that pre-registered
  bar; funding anyway would repeat exactly the mistake the bar was
  designed to prevent.
- **Run a third trial before deciding.** Rejected: Phase 78's own plan
  names this as the second, differently-shaped trial explicitly
  requested to settle the question (Phase 75's own retro, and Phase 77's
  own deferred-item note, both called for exactly this before any
  funding decision); a third trial without new reason to doubt this
  one's result would not meet the bar of "new evidence of a different,
  not-yet-tested shape" this ADR itself sets for reopening Priority A.
- **Treat this trial's `not-recurred` result as moving `CG-001`'s own
  inbox status.** Rejected by the independent `knowledge-curator` triage
  (`planning/reference-projects/ledgerkit/06-priority-a-exit-decision-triage.md`):
  this trial is a different concrete edge on a different project, which
  this entry's own three prior triage passes have consistently treated
  as evidence for the broader hypothesis, not a transition of this
  entry's own status, in either direction.

## Consequences

- `planning/ROADMAP.md`'s Priority A row is updated to record closure
  and this rationale.
- `planning/context-gaps/inbox.md`'s `CG-001` entry carries this trial's
  closeout note, status unchanged at `candidate`.
- `CG-010`/`CG-011` continue on their own independent, already-stated
  maintenance-backlog disposition (`decisions/0062` §3.1 cross-reference),
  unaffected.
- If a future phase surfaces new evidence of a genuinely different,
  not-yet-tested shape bearing on task-context completeness, it
  supersedes this ADR with a new numbered one (`CLAUDE.md` §2
  append-only rule), per `decisions/0062`'s own precedent for how this
  priority track is revisited.
