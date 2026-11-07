# Phase 87 Stage 87B retro — Genuine knowledge-change demonstration, concurrency guard, and comparator

- **Date:** 2026-11-07
- **Commit(s):** `0f6a268` (the implementation this demonstration ran
  against), plus this retro's own closeout commits.
- **Agents used:** `Plan` (three independent planning-review rounds —
  §P/§Q/§R), `general-purpose` (×5 real dispatches: the compiled-arm
  semantic-support and editorial-quality reviews, the comparator-arm's
  own draft-writing dispatch, and its semantic-support and
  editorial-quality reviews).

## Where we are

Stage 87A (knowledge compilation, one bounded section) and Stage 87A's
own hardening pass are both complete and independently audited. Stage
87B's plan was independently reviewed and corrected three times (§P:
two blocking factual errors found and fixed; §Q: seven further
findings found and fixed; §R: five more findings found and fixed,
including a materially strengthened publication-concurrency design)
before this governing task explicitly authorised implementation. This
retro covers the real, end-to-end knowledge-change demonstration
(plan's own §O.E) and its comparator — the deliverable the plan's own
stage gate treats as mandatory evidence, not optional polish.

## Goal

Demonstrate, against real production knowledge and a real,
independently-verified gap, that CodeCompass can detect a genuine
knowledge change, correctly re-verify and republish the affected
section, and reconcile cleanly afterward — while never touching
production canonical knowledge directly (an isolated git worktree) and
never silently suppressing or altering the real, unrelated
`intermediate-knowledge-layer` `doc_candidate` finding that predates
this stage entirely.

## What was achieved

**The knowledge gap was real, not manufactured.** `CL-CTXT-005`'s own
statement described `sync_vendor`'s digest rendering but never
mentioned its real, already-implemented, already-tested
clone-failure fallback (`src/codecompass/sync.py:128-153`, exercised
directly by the real, passing
`test_sync_vendor_source_resolution_failure_falls_back_to_local_snapshot`,
`tests/test_sync.py:275-298`) — confirmed by direct reading before
this demonstration began, not assumed.

**The full real cycle ran in an isolated `git worktree`
(`/tmp/codecompass-stage87b-demo`, branch `stage87b-demo-worktree`,
discarded after the demonstration per the plan's own instruction),
never touching the live repository's own `planning/knowledge/`:**

1. `CL-CTXT-005.yaml` amended in place (new `EV-CTXT-021` evidence
   added, citing the exact source/test lines above) — the real
   controlled lifecycle, not a hand-waved shortcut.
2. `detect_grounded_region_changes` correctly reported `claims_changed`
   for `readme-md-vendor-digest-concept` and, unaffected,
   **`doc_candidate` for `intermediate-knowledge-layer`** — unchanged
   from before the amendment, confirmed by direct comparison.
3. `docs compile` produced a real draft from the amended knowledge
   (one real clean-room broker call).
4. Two independent reviews — semantic-support/completeness and
   editorial-quality, dispatched exactly as Stage 87A's own precedent
   requires — both passed **on the first attempt** (see "Comparator"
   below for why this is noteworthy, not merely lucky).
5. `docs record-review` persisted both verdicts, hash-bound to the
   exact draft/evidence/schema identity.
6. `docs publish` **exercised the new publication-time concurrency
   guard for real** — `claims_changed` → proceed, exactly as
   specified — and published successfully.
7. A subsequent `docs maintain` reported `noop` for the republished
   region and, still, `doc_candidate` for `intermediate-knowledge-
   layer` — reconciliation genuinely correct, not merely hoped for.
8. A byte-for-byte `diff` against the pre-demonstration `README.md`
   confirmed **every line outside the one republished region is
   identical** — not asserted, directly diffed.
9. Exactly one reconciliation manifest exists in the worktree
   afterward — the same, real, pre-existing one from Stage 87A's own
   demonstration — confirming the idempotency fix held throughout a
   real multi-step run, not only in a synthetic unit test.

**The real, published update** (full text in
`planning/retros/phase-87-stage-87b-knowledge-change-demonstration-evidence/`):
a new second paragraph describing the clone-failure fallback, added to
the "Digest" section (the compiler also renamed the heading from
"Understanding Digests" to "Digest" — a stylistic choice of the
model's own, not a factual change, left as-is since the independent
editorial review raised no objection to it).

## Comparator (plan's own §O.E, corrected per finding A)

A separate, isolated worktree (`/tmp/codecompass-stage87b-comparator`,
also discarded afterward) was seeded with the **identical** starting
revision and the **identical** knowledge amendment, and a fresh
`general-purpose` dispatch was asked to perform the *exact same task* —
update `README.md`'s digest section to reflect the new fact — with no
compiler, no schema, no citation tags, no clean-room isolation,
directly editing the file by hand. Confirmed afterward: it touched
only the one section, preserved the grounding markers exactly, and
touched no other file.

**Real result, not fabricated or cherry-picked**: the comparator's
draft **passed** independent semantic-support review (every sentence
traced to `CL-CTXT-005` and independently re-verified against the real
code/tests) but **failed** independent editorial review — for a
register problem ("the Digest doesn't simply go missing or silently
render as if the clone had succeeded... so a Digest built this way is
distinguishable...") that reads exactly like an audit-report
conclusion rather than plain documentation prose. This is, point for
point, the same failure mode Stage 87A's own writing contract
(`compile_doc_section.build_system_prompt`) was specifically,
surgically hardened against after its own real 3-round demonstration
(filed as `L-119`). The compiled arm's draft passed the identical
editorial bar on its first attempt.

**Honest limits of this comparison, stated plainly**: this is one
real case, not Stage 87C's own matched-baseline experiment — no
blinding, no pre-registered rubric, no statistical claim. It is not
evidence that the compiler always outperforms direct human/agent
editing; it is evidence that, on this one real task, the compiler's
own accumulated editorial-quality guardrail caught a genuine register
problem a general-purpose dispatch reproduced independently, and the
compiler's own output did not have that problem. Whether this
generalises is exactly Stage 87C's own question to answer, not this
stage's.

## Bounded cost/value log

| Step | Dispatch | Tokens | Tool uses | Wall-clock |
|---|---|---|---|---|
| Compiled arm: draft compile | 1 real clean-room broker call | not captured (the broker's own response usage was not surfaced by this CLI invocation — disclosed as unavailable, not estimated) | — | not separately timed |
| Compiled arm: semantic review | 1st attempt | **lost to a transient rate-limit error, no result delivered** | — | — |
| Compiled arm: semantic review | 2nd attempt (succeeded) | 55,673 | 5 | 89.3s |
| Compiled arm: editorial review | 1st attempt (succeeded) | not captured (usage data for this dispatch was not surfaced before a later, unrelated rate-limit interruption — disclosed as unavailable) | — | — |
| Comparator arm: draft writing | 1 dispatch | 49,754 | 10 | 42.2s |
| Comparator arm: semantic review | 1 dispatch | 55,642 | 8 | 86.9s |
| Comparator arm: editorial review | 1 dispatch | 40,933 | 1 | 47.5s |

- **Rejected drafts**: compiled arm, 0 (contrast with Stage 87A's own
  real demonstration, which needed 3 rounds before a passing draft —
  this is anecdotal, not a controlled before/after comparison, since
  the writing contract itself changed between the two demonstrations).
  Comparator arm: its own single draft failed editorial review; no
  second attempt was made (out of scope for this comparator's own
  task, which is to produce one draft under the same conditions the
  compiler's own one real attempt had).
- **Factual errors found before publication**: zero, in either arm —
  both drafts' claims held up to independent, code-level
  re-verification.
- **Human correction effort**: zero manual edits to the compiled
  draft (it was published exactly as the model produced it, having
  passed both independent reviews). Zero manual edits attempted on the
  comparator's draft either (this retro reports its failure; fixing it
  was not this comparator's own task).
- **Maintenance effort after the real knowledge change, end to end**:
  one real worktree setup, one knowledge amendment, one compile call,
  two review dispatches, one publish, one maintain run — completed in
  a single session with zero rejected drafts, materially less overhead
  than Stage 87A's own first real demonstration (three compile rounds,
  six review dispatches).
- **Resulting documentation usefulness**: both the knowledge-compiled
  update and the onboarding-exercise evidence (§O.F criterion 2,
  reported in the implementation closeout) describe genuinely real,
  independently-verified system behaviour; the compiler's own
  published section is, per the editorial-quality comparator finding
  above, measurably cleaner on this one case.

## What worked

- **A single, well-evidenced, genuinely-searched-for knowledge gap**
  (not a placeholder) made the entire demonstration honest end to end
  — every reviewer's own independent re-verification against the real
  source/test lines came back clean because the fact itself was real.
- **The isolated-worktree design held up exactly as specified**: the
  real production `planning/knowledge/codecompass-domain/` was never
  touched; `git worktree remove` cleanly discarded both arms afterward
  with nothing left behind.
- **The idempotency and project-wide-discovery fixes (§O.D points 1-2)
  were exercised for real, not only in unit tests**: the pre-existing
  `intermediate-knowledge-layer` candidate was detected, left alone,
  and never duplicated across the whole multi-step real run.
- **The new publication-time concurrency guard (§O.D point 3) was
  exercised for real on its `claims_changed`-proceeds branch** — the
  first time this code path ran against anything other than a
  synthetic fixture.
- **The comparator's own failure is itself the most valuable single
  finding of this whole exercise**: independent, real evidence that
  the compiler's accumulated editorial hardening is not vacuous —
  it would have caught, on this held-out case, exactly the register
  problem it was built to catch.

## What didn't work

- **A transient rate-limit error interrupted the first semantic-review
  dispatch**, delivering no result at all; a straightforward retry
  succeeded. Not a defect in the pipeline itself, but worth naming:
  the orchestrator (the lead) must treat a dispatch that returns no
  result as needing a retry, never as an implicit "unsupported" or
  "fail," which would have been a false negative here.
- **Two dispatches' own token/tool-use/duration usage data were not
  captured** (one lost to the same rate-limit interruption, one
  simply not surfaced before it). Disclosed honestly above rather than
  estimated or omitted silently.
- **The real clean-room broker call's own usage/cost figures are not
  currently surfaced by `docs compile`'s CLI output at all** — a real,
  named gap in this stage's own cost-accounting instrumentation,
  distinct from the rate-limit-related gaps above. A future pass could
  have `compose_section`/`docs compile` print the broker response's
  own `usage` field if present, closing this gap without needing new
  infrastructure (the data already exists in the broker's own
  response, just never printed or logged).

## Lessons learnt

No new candidate learning filed from this demonstration specifically
— the one real process point above (treat a dispatch returning no
result as needing a retry, not as a verdict) is already covered by
ordinary agent-dispatch hygiene rather than being a new, generalisable
rule for this project's own learning log.

## Process-improvement feedback

The agent-led workflow's own independence discipline produced its
single most concrete piece of evidence yet that it matters in
practice: the comparator — written by a dispatch with no awareness of
Stage 87A's own writing-contract hardening — independently reproduced
the exact register problem that hardening targeted, and a third,
independent reviewer (also with no such awareness) caught it. Neither
the comparator nor its own reviewer were primed to find this; the
match is real, not engineered.

## Where we're going

This real knowledge-change demonstration and its comparator, together
with the earlier concurrency/idempotency/harness work (commit
`0f6a268`), complete Stage 87B's own mandatory real-demonstration
requirements. Remaining before Stage 87B can be marked complete: a
`docs-reconstructor` drift audit, an independent `release-phase-
auditor` pass against the final implementation commit, and the usual
`CLAUDE.md` §5 paper trail (`CONTEXT.md`, `ROADMAP.md`, `CHANGELOG.md`).
Stage 87C (the complete publication suite, the real matched-baseline
experiment) remains separately planned, not authorised, and untouched
by this stage's own work.

**One further, honestly-disclosed item, not acted on in this stage**:
`CL-CTXT-005`'s real amendment (the clone-failure-fallback fact) is a
genuine, evidence-backed improvement to this project's own actual
canonical knowledge — it was not fabricated for this demonstration,
and the underlying fact is true of the real, current codebase. It was
deliberately *not* merged into production `planning/knowledge/
codecompass-domain/CL-CTXT-005.yaml` as part of this stage, per the
plan's own explicit "never against production canonical knowledge"
instruction for this demonstration. Whether to separately propose this
as a real knowledge-curation candidate is a decision for the lead/user
outside this stage's own authorisation — named here explicitly so it
is not lost, never silently decided either way.

## Addendum: independent audit FAIL, fix, re-audit (2026-11-07, same day)

An independent `release-phase-auditor` pass against the implementation
commit (`0f6a268`) plus this closeout's own uncommitted changes
returned **FAIL** on one real, genuinely consequential gap, after
confirming everything else (full suite, strict validators, the
doc-drift fixes, the learnings triage, scope boundaries, protected-file
drift) held up under direct re-verification. Full audit trail:
`planning/retros/_audit-phase-87-stage-87b.md`.

**The finding**: the plan's own §O.D point 3 named six required
regression tests for the publication-time concurrency guard. Only four
existed. The missing one — "two concurrent `docs publish` invocations
against the same project serialise correctly through the lock" — had
survived three independent planning reviews (including §R, the same
day as implementation) without ever being built.

**Writing the missing test surfaced a real, previously-undetected
implementation gap, not just a missing test.** Reproduced directly
before fixing anything: a document mutation injected between the
initial `detect_grounded_region_changes` call (inside the lock) and
the write itself was silently overwritten — the "write-boundary
revalidation" the plan and this stage's own closeout both claimed
existed in fact ran only once, before the decision, with nothing
re-checking the live state a second time immediately before the write.
The same gap existed on the knowledge side: a cited record changing in
that same window was indistinguishable, to the existing mechanism, from
a legitimate `claims_changed` republish, because `claims_changed` is
*supposed* to be allowed — only the separate, pre-lock evidence/schema-
section freshness check could tell a fresh republish apart from a
now-stale one, and that check was never re-run inside the lock either.

**Fix**: both checks (the grounded-region detect-and-decide, and the
evidence/schema-section freshness check) now run a second time, inside
the lock, immediately before the write — not only before the lock is
acquired. This narrows, but — disclosed honestly in `_doc_publish_
lock`'s own docstring rather than assumed away — does not fully close,
the remaining window between that second check and the write itself;
a full transactional write would close it completely and was
deliberately not built, matching this stage's own smallest-coherent-
change instruction. Three new regression tests, all confirmed to fail
against the pre-fix code first: the concurrency test (`max_concurrent
== 1`, confirmed `2 == 1` with the lock disabled); a document-edit-at-
the-write-boundary test (confirmed the human edit was clobbered before
the second check existed); a cited-knowledge-change-at-the-write-
boundary test (same confirmation, knowledge side). Full suite: 1337
passed, 2 skipped (up from 1334). Ruff, `check_doc_schema.py --strict`,
`check_user_docs.py --strict` all re-confirmed clean.

**Two secondary, non-blocking observations, also corrected**: the
implementation commit's own message claimed "47 new regression tests"
(real delta: 40, confirmed by the auditor via `git diff` and the
1294→1334 suite count) and "6 pre-existing [ruff findings]" (real:
176, confirmed via a disposable comparison worktree at the pre-
implementation commit — the conclusion, no regression introduced, was
correct; the number was not). Not amended in the already-written
commit message (this project's own established practice carries a
discovered inaccuracy forward as a correction in the changelog/retro
rather than rewriting commit history); corrected in `CHANGELOG.md`'s
own Stage 87B entry instead.

**Re-audit**: a fresh `release-phase-auditor` dispatch, re-verifying
the fix directly rather than trusting this account, returned **PASS**
(see below). Stage 87B's own closure is genuinely gated on that
second, clean pass — not on this fix being merely applied.

No change to the real knowledge-change demonstration or comparator
findings above; both ran and were verified before this concurrency
gap was found, and neither touches `docs publish`'s concurrency guard
in a way this fix affects (the demonstration's own publish call
exercised the `claims_changed`-proceeds branch with no concurrent
writer and no intervening mutation — the scenario this fix addresses
never arose there).
