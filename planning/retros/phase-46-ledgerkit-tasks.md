# Phase 46 retro — CodeCompass during a genuine Ledgerkit task

- **Date:** 2026-09-13
- **Commit(s):** `329fa0a` (`feat(phase-46)`)
- **Agents used:** `reference-project-tester`, `context-evaluator` (both
  dispatched concurrently), `docs-maintainer` (reconcile),
  `docs-reconstructor` (drift audit), `knowledge-curator` (triage),
  `release-phase-auditor` (final pass)

## Where we are

Stage B's third phase, and the first time the full per-task procedure
(`reference-project-protocol.md` §2.4) ran end to end: a real
development-shaped task, attempted, with `reference-project-tester`
recording friction live and `context-evaluator` independently rating the
result. Phase 45 established the baseline (thin/near-empty as expected,
plus one FAIL); this phase tests whether that pattern holds under actual
work, not just spot-check questions.

## Goal

Run the genuine-task procedure once against Ledgerkit: pick a real,
already-scoped task, attempt it using CodeCompass context, have
`reference-project-tester` record friction and `context-evaluator`
independently evaluate, write Phase 47's plan (GATE DB).

## Scope delivered vs planned

Delivered as planned, with the exact kind of live-repo movement Phase 45
already trained this project to expect: Ledgerkit's roadmap moved
**again** between Phase 45's pinned commit and this phase's start —
Stage B (which Phase 46's own plan file was hedged against, since it
wasn't yet scoped at Phase 45's time) closed to `[DONE]` entirely within
a day, and Stage C opened with Phase 1 already `[IN PROGRESS]`. The
plan's explicit hedge ("reconfirm live... prefer whichever task is
genuinely current") worked exactly as designed — the actual task run
(hledger 1.52 query-term semantics) is not the compat-register-migration
candidate the plan file named, and that's correct, not a deviation to
apologize for.

A second, deliberate scope adjustment: because a real, separate,
concurrently-running Ledgerkit development session was live and actively
producing the exact deliverable this task researches
(`17-query-semantics-brief.md`), this phase's "attempt" was conducted as
a **read-only evaluation exercise** — the lead did the cognitive work of
answering the question, using CodeCompass first and direct exploration
second, without writing anything into the Ledgerkit clone. This is a
tighter interpretation of non-invasiveness than strictly required
(§2.7 only forbids changes the maintainers wouldn't want; writing zero
files is a stricter, safer choice given the concurrency risk) — worth
naming explicitly since it's a judgment call a future phase might need to
make again if Ledgerkit's own session is live at the same time.

## What was achieved

- `planning/reference-projects/ledgerkit/01-query-semantics.md` —
  **CodeCompass's second FAIL verdict**, and the first on genuinely
  in-progress work rather than a spot-check question. CodeCompass
  returned zero context (not thin — a complete blank: 0 vendors, "not
  found" for both `dev-docs/` files). Ledgerkit's own
  `dev-docs/planning/core-redefinition/07-query-regex.md` §7.1 already
  had the complete, correct answer, found by one `grep` + file read.
- **`CG-002` re-confirmed independently by both agents**, extended to
  nested `dev-docs/**` paths, not just top-level files — moved from
  `candidate` to `recurred` at Phase 45, now with a second, independent
  confirming occurrence on live work.
- **`CG-003` filed** (new): even a fixed `CG-002` would only surface
  Ledgerkit's own prior *prose* about hledger — CodeCompass has zero
  representation of the external, non-package technical dependency
  (real hledger 1.52 behaviour/manual) that is the task's actual
  authoritative source. No glob fix could ever close this one.
- **`L-017` filed**: a live `WebFetch` against the real hledger.org
  manual, tried as a fallback, needed two attempts and still couldn't
  reliably extract the `not:`/AND-OR section from the large page — a
  real, evidenced retrieval-cost finding for Phase 53's "manual as
  fetched/vendored text" design question.
- `planning/phase-47-consolidate-findings.md` written — the Stage B
  decision phase (GATE DB), with a full evidence inventory assembled
  from Phases 44–46.

## What worked

- **Reconfirming the task live rather than trusting Phase 45's plan
  file** caught the second roadmap move before it wasted the phase on a
  now-superseded target — the same discipline that caught Milestone 5's
  supersession paid off again, one phase later, on a different scope
  (Stage B's entire closure).
- **Treating the concurrent live session as a real constraint, not an
  edge case to ignore** — reframing the task as read-only evaluation
  avoided both duplicating real work and risking any interference with
  it, while still producing a genuine, independently-evaluated result.
- **Two independent FAIL verdicts, same failure shape, different
  triggers** (a spot-check question in Phase 45, live in-progress work in
  Phase 46) is exactly the kind of recurrence `context-quality-evaluation.md`
  §6 says to weight as highest-priority GATE DB input — this phase
  supplied that recurrence for real, not hypothetically.

## What didn't work

- **Dispatching `reference-project-tester` and `context-evaluator`
  concurrently to write to the same shared file path was a mistake.**
  Both were instructed to check the file's current state before writing,
  but `Write` replaces the whole file rather than appending, so the
  second agent's write silently clobbered the first's content. The lead
  caught this only by reading the file afterward and cross-referencing
  it against `context-evaluator`'s own returned summary, and had to
  manually reconstruct the lost section. Had the lead not double-checked,
  `context-evaluator`'s independent verdict would have been silently
  lost from the permanent record while its task-completion summary
  claimed success.

## Lessons learnt

1. **Never dispatch two agents to `Write` (not `Edit`) the same file
   path concurrently** — `Write` is a full-file replace, so the second
   writer always wins regardless of instructions to "check first." Either
   sequence such dispatches (one writes, hands off, the other appends via
   `Edit`), or give each agent a distinct file and merge afterward.
2. **A background agent's own "success" report is not proof its write
   landed** — this phase's `context-evaluator` correctly reported writing
   its file, and did so successfully at the time, but a later write from
   a different process silently erased it. The lead's habit of reading
   the actual file after dispatch (not just trusting the returned
   summary) is what caught this — reinforces the project's existing
   "verify independently, every time" rule, extended to include
   verifying an agent's own claimed output actually persisted.
3. **A live, concurrently-developed reference project is a real
   operating condition for Stage B/D, not a hypothetical** — this
   session ran alongside Ledgerkit's own active development twice now
   (roadmap moved between Phase 44→45 desk assessment and clone time, and
   again between Phase 45→46). Any future reference-project phase should
   assume the target may be actively moving and plan file-write
   boundaries (and task selection) accordingly.

## Process-improvement feedback

**File the concurrent-write race as a workflow rule**, not a `CG`/`L`
entry (it's about the agent-led process, not CodeCompass's product):
`planning/agent-led-workflow.md` step 5 ("one agent = one artifact")
already implies this but doesn't say it explicitly for the case of two
different specialist roles asked to jointly produce one file. Recommend
an explicit addition: "if two agents must contribute to the same report
file, sequence them (one writes the file, the second is told to `Edit`-append
after confirming the first agent's dispatch completed), never dispatch
both to `Write` the same path concurrently."

## Candidate learnings filed

- **`CG-003`** — external hledger.org manual has zero representation, no
  glob fix could ever cover it.
- **`L-017`** — `WebFetch` of a large external manual is an expensive,
  unreliable fallback for section-specific content.
- (Process note, not a `CG`/`L`) — the concurrent-`Write` race, above,
  recommended as an `agent-led-workflow.md` step 5 clarification.

## Where we're going

- **Next: Phase 47** — consolidate all Phase 44–46 findings, GATE DB
  (gate G6): a funding decision on Stage C. The evidence base is now
  real: two independent FAIL verdicts of the identical failure shape,
  plus `CG-002`'s recurrence and `CG-003`'s structurally distinct
  external-dependency gap.
- **Trajectory: confirmed, strengthened.** Stage B's premise (Ledgerkit's
  real technical dependencies are almost entirely non-package) is no
  longer resting on one baseline spot-check — it's now demonstrated
  twice, once on a direct question and once on live in-progress work.

## Time / cost note

Single session, continuing directly from Phase 45 (same day). One
`WebFetch` retrieval attempt pair (two calls, both partial) against
hledger.org — no CodeCompass AI-enrichment spend. No `src/codecompass/`
change, no test change (full suite re-verified: 554 passed / 2 skipped,
`ruff` clean).
