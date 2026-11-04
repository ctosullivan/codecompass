# Phase 87 Stage 87A hardening retro — Secure the publication path

- **Date:** 2026-11-04
- **Commit(s):** the hardening implementation/test/docs commit(s) on
  this branch following `ad46d16`, plus this retro's own closeout
  commits (CHANGELOG, learnings, CONTEXT/ROADMAP reconciliation).
- **Agents used:** `knowledge-curator` (candidate learning triage),
  `docs-reconstructor` (focused drift audit), `release-phase-auditor`
  (final independent audit of this hardening pass).

## Where we are

Stage 87A (Phase 87, the knowledge-compilation stage within the
redefined v2 roadmap) was implemented, demonstrated three times
against the real repository, and independently audited to PASS WITH
NON-BLOCKING OBSERVATIONS in the previous session (`ad46d16`). A
follow-up governing task then re-examined the publication path itself
— not the compiled content, knowledge resolution, or the real
demonstration's own output, all independently reconfirmed sound before
this pass began — and found three further integration defects, plus
one audit-sequencing gap in the prior pass's own closeout. This retro
covers correcting those four findings. It does not reopen Stage 87A's
own demonstrated value or its stage gate (§D.4), and does not begin
Stage 87B.

## Goal

Harden Stage 87A's publication mechanism so that publication cannot
bypass evidence, verification, or write boundaries, without
introducing a new agent, database, approval framework, or sandbox —
then independently re-audit the actual final state, closing the prior
pass's own audit-sequencing gap going forward.

## Scope delivered vs planned

All four corrections named in the governing task were delivered:

- **§N.A** — `docs publish` no longer accepts a manually typed verdict
  string. A new `docs record-review` command persists each
  independent review bound by hash to the exact pending draft,
  evidence, and schema section; `docs publish` validates that
  persisted record instead.
- **§N.B** — `doc_compiler.resolve_publication_target` confines every
  compiler-owned write to `README.md` or `docs/**/*.md`, resolving
  symlinks before comparing against the project root; enforced at both
  schema-validation and publish time.
- **§N.C** — `compose_section`'s broker prompt is now built from the
  packet re-read from its own verified on-disk file, not the in-memory
  object; the ephemeral staging directory is always removed, success
  or failure.
- **§N.D** — no retroactive rewrite of the prior, already-closed audit
  record (preserved as historical evidence); this pass's own final
  `release-phase-auditor` dispatch audits the true final commit,
  closing the gap going forward rather than papering over the prior
  one.

Nothing beyond the four named findings was touched. No new sandbox,
broker, agent, or knowledge store was introduced, consistent with the
governing task's own explicit constraint.

## What was achieved

Three real implementation defects, each reproduced by a regression
test that was confirmed to fail against the pre-hardening code (by
stashing only the source changes and running the new tests against
the prior commit) before the fix, then confirmed passing after: 13 of
the 21 new tests were run this way directly; the remainder are purely
additive coverage (e.g. a legitimate-publication positive control)
that could not fail against old code in the same sense since the
command/function they exercise did not previously exist in that form.
Full suite: 1290 passed, 2 skipped (up from 1275 passed before this
pass). Ruff clean on every touched file (the same 6 pre-existing,
unrelated findings remain, confirmed via a before/after diff, not
assumed). Schema, knowledge-placement, knowledge-base, contracts, and
user-docs validators all exit clean; the Phase 85 self-knowledge-
quality baseline (35 informational/known findings) is unchanged,
retained rather than suppressed. The real, previously-published
`README.md` "Understanding Digests" section and its
`codecompass-grounded-by` marker are unaffected and were reconfirmed
intact.

## What worked

- **Reproducing each defect as a failing test before fixing it, then
  mechanically confirming the failure** (via `git stash` on source
  files only, keeping the new tests) **rather than asserting it** —
  this caught that several of the new tests would only have exercised
  genuinely new code paths (e.g. `docs record-review` did not exist at
  all before this pass), which is itself useful evidence that the
  defects were real integration gaps, not pre-existing edge cases a
  looser test would have already covered.
- **A single, reusable path-validation function
  (`resolve_publication_target`) used at both schema-validation and
  publish time**, rather than two independently-maintained checks —
  the governing task's own explicit instruction, and a design choice
  that paid off immediately: `check_doc_schema.py` catching an unsafe
  `document` field at authoring time is strictly better than only
  catching it when a publish is actually attempted.
- **Closing the audit-sequencing gap procedurally rather than by
  rewriting history** — the prior, already-closed audit record stays
  intact as historical evidence; this pass's own final audit is simply
  required to cover the true final commit, which is the discipline
  that should have applied originally.

## What didn't work

Nothing novel surfaced beyond the three implementation defects named
in the governing task's own findings — this pass was itself a
correction, not a discovery exercise, so "what didn't work" is mostly
the same root cause named in `L-119`'s own process lesson from the
prior pass (DoD bookkeeping deferred under demonstration pressure) —
this time avoided by doing the paper trail (CHANGELOG, retro,
learnings, CONTEXT/ROADMAP) before the final audit runs, not after.

## Lessons learnt

See candidate learning filed below for the one generalizable technical
takeaway from this pass (`compose_section`'s own defect).

## Process-improvement feedback

The agent-led workflow continues to work as designed: a follow-up,
independently-scoped review (not the implementer re-reading its own
work) is what found all four defects here, exactly as the prior
session's own `release-phase-auditor` dispatch found the DoD gap. No
tool or agent-boundary friction.

## Candidate learnings filed

`L-120` — filed to `planning/learnings/inbox.md`, this pass,
2026-11-04; see that file's own entry and `knowledge-curator`'s
curation notes.

## Where we're going

Stage 87B's own implementation-ready plan is drafted next (plan's own
§O), independently reviewed, and committed separately from this
hardening pass — implementation itself remains unauthorised. Stage 87C
and Phases 88-92 remain untouched. Phase 87 overall remains `not done`.

## Time / cost note

One session, no real billed model-inference calls (the hardening is
purely mechanical/CLI-level; the real clean-room broker was never
invoked during this pass, since no new compilation round was run).
