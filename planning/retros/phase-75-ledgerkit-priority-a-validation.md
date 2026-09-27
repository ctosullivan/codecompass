# Phase 75 retro — Priority A Ledgerkit validation

- **Date:** 2026-09-27
- **Commit(s):** (this phase's own closeout commit(s) — see git log for exact SHAs)
- **Agents used:** two independent general-purpose agents (baseline, treatment), `context-evaluator`, `knowledge-curator`, `docs-reconstructor`, `release-phase-auditor`, `roadmap-context-curator`

## Where we are

Post-v1, Priority A track (`decisions/0062`). Phase 73 landed the first
concrete Priority A deliverable (`CG-006`'s filename-matching fix,
detection-improvement scale). This phase is the first **real-task
validation** of Priority A's own core premise — that post-Phase-73
CodeCompass gives a fresh agent a measurable task-context advantage on
genuine Ledgerkit work — using the project's own established
baseline-vs-treatment reference-project methodology
(`reference-project-protocol.md` §2, reusing Phase 54b's shape). It
follows directly on a separate, same-session root-cause fix to a
phase-closeout process defect (`planning/retros/_root-cause-closeout-defect.md`,
`L-060`/`L-061`) that also touched Phases 71-74's own final DoD status —
that work is complete and independent of this phase's own findings.

## Goal

Determine, with real evidence rather than Phase 72's own anticipation,
whether current CodeCompass materially helps a fresh agent understand a
genuine Ledgerkit task, and decide from that evidence whether `CG-001`,
`CG-007`, or something smaller/different is the actual next justified
Priority A capability.

## Scope delivered vs planned

Delivered exactly as scoped in `planning/phase-75-ledgerkit-priority-a-validation.md`:
task selection (hledger's `cur:` query term) with documented genuineness
rationale; two independent scratch clones (baseline, no CodeCompass;
treatment, CodeCompass synced, 0 vendors, no AI enrichment — no API key
in this environment); two independently-dispatched fresh agents, run
sequentially with no cross-contamination; an independent
`context-evaluator` pass establishing its own ground truth against the
real Ledgerkit and real hledger source; a lead gap analysis against all
eight of the user's named Part 6 dimensions; explicit `CG-001`/`CG-007`
disposition plus a newly-filed `CG-009`; an explicit next-phase
recommendation. No deviation from scope — no `cur:` implementation was
attempted (correctly out of scope), and no CodeCompass capability was
built (the plan's own "unless a tiny evaluation-enabling correction
proves necessary" escape hatch was never triggered — nothing about the
experiment's own validity required a mid-experiment fix).

One scope note, not a deviation: `context-evaluator` was dispatched
without direct access to the baseline/treatment agents' own raw
SubagentHandback message content (a dispatch-prompt limitation, not a
data-loss — the two scratch clones and the real repositories were still
fully available) — see "What didn't work" below.

## What was achieved

A real, independently-verified answer to the Priority A validation
question: **PASS WITH GAPS, advantage LOW**. Full report:
`planning/reference-projects/ledgerkit/04-cur-query-priority-a-validation.md`.
`CG-001` was provisionally moved from `candidate` to `recurred` by the
lead's own gap analysis, then independently reversed back to `candidate`
by `knowledge-curator`'s own same-phase triage (the evaluation report's
own `context-evaluator` section had already recommended
cross-reference-not-promotion using this entry's own established
precedent) — the lead reviewed and concurred with the reversal; `CG-001`
stays `candidate`, retained as a third cross-reference for its own
task-oriented-retrieval hypothesis. A new, structurally-confirmed
context gap (`CG-009`: zero first-party-source symbol index, any
ecosystem) was filed and independently verified by direct code-reading
(`sync.py::rebuild_project_graph`, `graph.py`'s `symbols.vendor_id NOT
NULL` constraint), not merely reported, and confirmed `candidate` by
`knowledge-curator`'s own triage.
`CG-007` received an explicit "no new evidence" cross-reference note,
correctly not conflated with the different mechanism `CG-009` names. A
new process learning (`L-062`) was filed documenting a real
methodological confound (read-access asymmetry between baseline and
treatment dispatch environments) that this phase's own plan had
anticipated in principle (`L-027`) and that `context-evaluator`
confirmed in practice, on the treatment run's single most
impressive-looking finding.

## What worked

- **The `L-027` agent-diligence-variance check, written into the plan
  before either agent was dispatched, did exactly its job.** Without it,
  the treatment agent's flashy `Query.hs` anchored-matching discovery
  would very plausibly have been credited to CodeCompass in a less
  careful write-up — it wasn't CodeCompass's finding at all, and
  `context-evaluator` proved this two ways (equal filesystem read
  access; the fact was already in the manual the baseline had already
  fetched). Writing this check into the plan *before* seeing either
  result, rather than deciding post-hoc whether to apply scrutiny, is
  what made the negative finding credible rather than convenient.
- **Independent, ground-truth-establishing evaluation outperformed both
  dispatched agents' own self-reports.** `context-evaluator` found a
  *more* decisive fact than either agent (the hledger 1.52 manual
  already had the anchored-matching behaviour in plain English) by
  reading more carefully than either dispatched agent had, and named a
  real structural gap (`CG-009`) that neither agent's own report framed
  as a graph-schema question. This is itself live, fresh evidence for
  `decisions/0062`'s Priority E (independent context evaluation is
  already this project's single most consistently validated
  mechanism) — see the next-phase recommendation.
- **Sequential (not parallel) dispatch of baseline-then-treatment, into
  separately-cloned scratch copies, structurally prevented
  cross-contamination** — confirmed by reading both reports for any
  sign one referenced the other; none found.
- **Reusing the exact Phase 54b baseline/treatment shape**, rather than
  designing a new comparison methodology, meant no time was spent
  re-litigating "how should this evaluation be structured" — the
  precedent already answered it.

## What didn't work

- **The `context-evaluator` dispatch prompt said both agents' full raw
  reports were "already in this conversation's history" — they weren't
  present in the fresh subagent's own context.** `context-evaluator`
  compensated correctly (by re-deriving ground truth independently
  rather than stalling or guessing), but this was a real dispatch-prompt
  error, not a designed fallback — a fresh subagent has no access to the
  dispatching session's own conversation transcript unless the content
  is placed directly in the prompt or in a file the agent can read. The
  reports existed only as message content in the lead's own
  conversation, never written to disk, so `context-evaluator` had
  nothing to read even if it had looked. No harm resulted this time
  because the evaluator's own methodology (independent ground-truth
  establishment, not trusting either report) is robust to this gap by
  design — but it should not be relied on twice.
- **Neither scratch clone retained any durable trace of either agent's
  own investigation** (`git status` clean in both, per
  `context-evaluator`'s own note) — the two reports exist only as this
  session's own conversational content. This made the above gap worse
  than it needed to be: there was no fallback file for `context-evaluator`
  to read even after the prompt's own claim proved wrong.

## Lessons learnt

See `L-062` (filed this phase): a baseline/treatment dispatch prompt
that scopes *writes* to a scratch clone but says nothing about *reads*
leaves both agents with equal, unscoped filesystem read access — which
is fine for either agent's own task performance, but is a hidden threat
to a *comparison's* validity, since one agent's broader search habit
(not the tool under test) can then produce the single most attributed-
sounding finding. The `L-027` check catches this after the fact; scoping
reads symmetrically (or disclosing that they're intentionally
unscoped) up front would prevent needing to catch it at all.

A second, process-level lesson (not filed as its own `L-NNN`, folded
into how future dispatches are written): a subagent dispatch prompt
must never claim the agent already has access to conversation content
that exists only in the dispatching session's own context — either
paste the actual content into the prompt, or write it to a file first
and point the agent at the file.

## Process-improvement feedback

Write baseline/treatment agents' full reports to disk (e.g. under
`planning/reference-projects/<project>/`) immediately on receipt, before
dispatching any downstream evaluator that will need to reference them —
this phase's own delay (reports existed only as conversation content
when `context-evaluator` was dispatched) is exactly the gap named above.
No other workflow friction this phase — the corrected closeout sequence
from the earlier Phase 73/74 root-cause fix (drift audit → interim
reconciliation → retro → learning triage → completion audit → only-on-
PASS final reconciliation) is being followed for this phase's own
closeout as the first real test of that fix.

## Candidate learnings filed

`L-062` (baseline/treatment read-access-scope confound, promoted to
`reference-project-protocol.md` §2.2) and `L-063` (a subagent dispatch
prompt must never claim a fresh agent already has access to
conversation-only content, filed by `knowledge-curator` from the
retro's own "What didn't work" observation, promoted to
`agent-led-workflow.md` step 7). Also: `CG-009` filed to
`planning/context-gaps/inbox.md` (by `context-evaluator`, confirmed
`candidate` by `knowledge-curator` triage); `CG-001`'s provisional status
change (`candidate` → `recurred`), made directly by the lead's own gap
analysis, was independently reversed back to `candidate` by
`knowledge-curator`'s own triage and confirmed by the lead — see "What
was achieved" above.

## Where we're going

Recommended Phase 76: a second, differently-shaped Priority A
validation trial (ideally exercising `CG-001`'s original
intra-`src`-module motivating shape, or a reference-project corpus less
self-descriptively organized than Ledgerkit's `dev-docs/planning/
core-redefinition/NN-title.md` convention) — not a capability build, and
not abandonment of Priority A. This **changes** rather than confirms
Phase 72's own anticipated trajectory (`decisions/0062` expected `CG-001`/
`CG-007` to be the likely next funded work; this phase's real evidence
instead recommends one more validation trial before any funding
decision, per this project's own `L-027`/recurrence-bar discipline).
No gate/decision-record ambiguity: this is squarely within the lead's
existing authority (an evidence-based roadmap recommendation, not a
protected-file or domain-ambiguity decision).

## Time / cost note

One extended session, continued across a context-compaction boundary.
Real AI subagent spend: two general-purpose dispatches (baseline,
treatment) plus one `context-evaluator` dispatch, each a genuine
multi-tool-call investigation (up to ~670s/73 tool calls for the longest
of the three) — no shortcuts taken on any of them. No `src/` regression
risk this phase (no code changed), so no extended test-suite runtime
beyond the standard `pytest`/`ruff`/`check_user_docs.py --strict` sweep
at closeout.
