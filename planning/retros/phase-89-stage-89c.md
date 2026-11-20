# Phase 89 Stage 89C retro — Task B pre-registered controlled comparison

- **Date:** 2026-11-21
- **Commit(s):** `b0b2ef8` (final amended plan + review), plus this
  stage's own closeout commit(s)
- **Agents used:** `general-purpose` ×1 (focused plan re-review),
  `fork` ×3 (mechanical setup/packet generation, independent
  acceptance-test/`OracleResult` verification, blinded-materials
  preparation), `general-purpose` ×2 (control/treatment development
  arms), `context-evaluator` ×1, `release-phase-auditor` ×1,
  `knowledge-curator` ×1 (learnings triage)

## Where we are

Phase 89 (Incremental Knowledge and Documentation Reconciliation) has
now run its full planned arc: Stage 89A (detection/reconciliation
mechanism, implemented and twice correctively audited to PASS), Stage
89B (the contradiction-gap kind plus a real documentation-reconciliation
cascade demonstration, implemented and audited to PASS), and now Stage
89C — the controlled comparison Stage 89A/89B's own pre-registration
(`planning/retros/phase-89-ledgerkit-two-task-demonstration.md`) existed
specifically to let this phase answer: does Task A's own reconciled
knowledge measurably help a *second*, independent development decision?
Stage 89C's plan went through three independent review/amendment rounds
before being treated as implementation-ready (control-arm packet
omission and a reference-checkout digest incompatibility found by a
second dispatch; an overbroad blinding check and a silent-re-pin risk
found by a third). That third dispatch's own explicit authorisation then
carried the plan through actual execution — this retro covers that
execution.

## Goal

Execute the pre-registered Task B controlled comparison exactly as
specified: two isolated development arms (control = pre-Task-A-
reconciliation context packet, treatment = post-Task-A-reconciliation
packet) implement `ReportSpec.with_combined_section` on an otherwise
identical, pinned Ledgerkit baseline; independently verify both against
a pinned 11-method acceptance suite and a genuine `OracleResult`; have
an independent, allocation-blinded `context-evaluator` compare them;
have an independent `release-phase-auditor` check the whole procedure's
own fidelity; and apply the pre-registered success criterion honestly,
in either direction.

## Scope delivered vs planned

Delivered exactly as planned, with no scope substitution: both plan
corrections (Part A of the governing dispatch) were made and
independently re-reviewed before any arm was dispatched (Part B's own
gate); the full pre-registered trial then ran end to end (Parts C/D);
results were persisted and the pre-registration itself was appended
with the real outcome, never retrospectively edited (Part E). One
deviation from a strict reading of the plan's own artifact-location
convention: the two development arms' environments lacked the `.venv`/
`pytest` setup the plan's prose assumed (`oracle.run_pytest_check`'s own
documented symlink-and-`PYTHONPATH` mechanism) — both arms independently
discovered this and fell back to `python3 -m unittest`, which the
existing `unittest.TestCase`-based suite fully supports; this was
corrected for and not a defect in either arm's own work, but the
independent verification step (§6) and the context-evaluator/auditor
both deliberately used the real symlinked `.venv` + `pytest` path so the
durable `OracleResult` and the pinned acceptance suite were genuinely
run the way the plan specifies, not merely re-described from each arm's
own improvised substitute.

## What was achieved

A complete, genuine, independently-verified and independently-audited
run of the pre-registered Task B comparison exists. The result is a
**credible negative finding, not a contaminated or inconclusive one**:
all three of the pre-registration's own success signals (acceptance-test
divergence, evaluator verdict, evaluator rating) came out tied, so the
positive exit gate (§7 of the pre-registration) was **not met**. The
proximate cause — both arms independently re-derived the correct answer
from a short, direct read of `balance_from_spec`'s own source, aided by
the task's own pinned framing sentence, regardless of which context
packet either received — was itself independently confirmed by the
evaluator and the auditor, not asserted by the lead. Phase 89's own
roadmap-level positive exit gate (§9 of its own plan) is correspondingly
**not met** by this trial; Phase 89 is not marked `done`.

## What worked

- **The three-round plan-correction/re-review cycle, completed before
  any arm was dispatched, caught real defects that would have silently
  invalidated this exact trial** — most importantly the reference-
  checkout digest-incompatibility defect (second amendment), which
  would have kept the post-Task-A packet's own required-scope-gap count
  at the same value as the pre-Task-A one, making the two packets
  genuinely, silently indistinguishable on the one dimension this whole
  experiment depends on. Catching this *before* execution, rather than
  discovering a null result was actually a setup bug after the fact,
  is exactly what the independent-reproduction requirement (the
  governing dispatch's own Part B) is for.
- **Using forked (not fresh) agents for the purely mechanical
  pipeline stages** (clone/equivalence/reconciliation/packet generation;
  acceptance-test + `OracleResult` verification; blinded-materials
  preparation) kept three large blocks of repetitive command output
  out of the lead's own context while still letting those stages
  inherit full plan context — each one ran its exact pinned procedure
  correctly on the first attempt.
- **Independently re-deriving every mechanical claim, three separate
  times** (the setup fork, then the evaluator, then the auditor, each
  blind to or independent of the others' own derivation) caught a real
  defect no single pass caught on its own: the allocation-blinding leak
  in raw oracle transcripts was invisible to the redaction step's own
  self-check, but was caught independently by both the evaluator and
  the auditor before it could have mattered.
- **Both development arms' own reports explicitly distinguished "the
  packet says X" from "I independently confirmed X by reading the
  source myself"** — this is exactly the discipline `L-027`'s equal-
  access check depends on being able to observe, and it was present in
  both arms' own self-reports without being specifically prompted for
  beyond the standard observable-research-trace requirement.

## What didn't work

- **The redaction sweep for the blinded evaluator materials checked a
  fixed string list but didn't verify its own completeness against
  every file *type* a sensitive string could appear in** — it redacted
  structured JSON correctly but missed the same information surviving
  unredacted inside raw, unstructured oracle-subprocess transcript
  files. This cost nothing in this specific run (the result was a tie
  regardless, and both independent downstream readers caught it), but
  it is exactly the kind of gap that would matter in a future trial
  with a genuinely asymmetric result. Filed as `L-139`.
- **Neither development arm's assigned environment had the `.venv`/
  `pytest` setup the plan's prose implicitly assumed** — a minor
  friction, self-corrected by both arms without affecting their own
  correctness, but it meant the plan's own §4.1 "identical tool access"
  table entry was technically under-specified (it names `Bash` without
  stating what's actually installed in the scratch clone it's handed).
- **The packet's own `summary` truncation silently contradicts its own
  `bounds.truncated` flag** (`L-140`) — found only because the
  evaluator happened to read the packet closely enough to notice a
  summary cut off mid-word; this is a real, if minor, CodeCompass
  defect that none of Phase 82/84's own original implementation or
  review work caught, surfaced as a side effect of an unrelated
  experiment rather than by testing that code path directly.

## Lessons learnt

The single biggest lesson this stage reconfirms is procedural, not
technical: **a controlled comparison's own validity depends entirely on
whether the decisive fact is actually hard to reach without the
treatment being tested** — Task B was deliberately designed so the
correct design boundary followed from a short, direct source read
*regardless* of context-packet content, which is precisely why both
arms tied. This is not a flaw in this trial's own execution (every
procedural check passed); it is a property of the *task selected*, now
empirically confirmed rather than assumed. A future trial intending to
demonstrate a positive effect should deliberately select or construct a
task where the decisive fact is genuinely costly to re-derive from
scratch (e.g., buried in a less obvious code path, or requiring
cross-file reasoning a short local read would not surface), not merely
one where reconciled Evidence happens to exist.

## Process-improvement feedback

- A future allocation-blinded trial's own redaction step should
  explicitly enumerate every file type/location a sensitive string
  could appear in (structured JSON, prose reports, *and* raw
  subprocess/tool-output transcripts) and verify its own completeness
  against that enumeration, not just run one grep pattern and assume
  coverage.
- The plan's own §4.1 equivalence table should name what's actually
  installed in a fresh development-arm scratch clone (or explicitly
  disclaim it, if genuinely unpredictable) rather than implicitly
  assuming a `.venv`/`pytest` setup that neither this run's control nor
  treatment clone actually had.

## Candidate learnings filed

`L-139` (redaction-sweep file-type coverage gap), `L-140`
(`get_context_packet` summary-truncation/`bounds.truncated` mismatch) —
both filed to `planning/learnings/inbox.md`, triaged by
`knowledge-curator` (see that dispatch's own disposition, recorded in
the inbox entries themselves and `planning/ROADMAP.md`'s
future-improvement backlog if promoted).

## Where we're going

Stage 89C is now complete (technically implemented, independently
verified, and independently audited — Gates 1 and 2 of the plan's own
§14 are met) but its own positive result was **not** demonstrated (Gate
3 is not met, and Phase 89's own roadmap-level exit gate is
correspondingly not met). Per the governing dispatch's own explicit
instruction, this is recorded honestly as a negative finding about this
specific mechanism and task — not reinterpreted, not retried with a
different task to chase a different answer, and not treated as proof
that CodeCompass's knowledge/assurance capabilities lack value more
generally. The next decision (whether/how to design a follow-up trial
with a task more likely to expose a real effect, or to treat this
question as answered-for-now and move to Phase 90) is a strategic
choice for a future, separately authorised session — not made here.
Phase 90 is explicitly not started by this work.

## Time / cost note

One session, roughly 8 agent dispatches (1 focused plan re-review, 3
mechanical forks, 2 development arms, 1 evaluator, 1 auditor, 1
learnings triage) plus the lead's own plan-amendment and documentation
work. No per-dispatch time tripwire was exceeded; full exploratory
token/tool-call/wall-clock figures per dispatch are recorded in
`planning/reference-projects/ledgerkit/
08-stage-89c-task-b-controlled-comparison.md`'s own "Exploratory
cost/usefulness metrics" section.
