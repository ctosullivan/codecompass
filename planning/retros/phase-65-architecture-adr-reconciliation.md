# Phase 65 retro — Architecture + ADR reconciliation

- **Date:** 2026-09-23
- **Commit(s):** `5d4fa94` (plan + ROADMAP row split), `b94d175`
  (`decisions/0061`), `83f9069` (draft reconciliation table), `b48e7a9`
  (lead decisions on the table's two open items), `099df0e` (full
  execution: architecture + docs), `301e8b0` (drift-audit fix + report).
- **Agents used:** `docs-maintainer` (reconciliation table draft),
  `domain-skeptic` (freshness reconciliation), a `fork` (ADR status
  review), two parallel `docs-maintainer` dispatches (execution),
  `docs-reconstructor` (per-phase drift audit).

## Where we are

Stage G's second phase, immediately following Phase 64 (done,
2026-09-23, PASS). This phase compares Phase 64's blank-slate proposal
against the current active documentation and actually applies the
result — the first phase where `documentation-lifecycle.md` §4's full
retain/rewrite/consolidate/split/replace/remove cycle ran end to end,
not just the "produce a shadow proposal" half (Phase 64) or the
"produce an evidence-backed domain corpus" half (Phase 63D).

## Goal

Reconcile `architecture/overview.md` and the remaining current-truth
docs against Phase 64's own shadow proposal, document by document;
review all 59 ADRs for silent supersession; re-check `docs/domain/` for
staleness since Phase 63D's approval.

## Scope delivered vs planned

Delivered exactly as planned (§2.1–§2.4), plus the two open items the
plan's own draft reconciliation table surfaced and the lead resolved
before execution:

- **§2.1 ADR review**: all 59 ADRs checked. One genuine governance gap
  found (`decisions/0019` fully reversed by `decisions/0035` at Phase
  16, never formally declared) — fixed with a new ADR (`decisions/0061`),
  neither `0019`'s nor `0035`'s own original content edited, matching
  this project's own established append-only precedent.
- **§2.2 `architecture/overview.md` reconciliation**: all 32
  `architecture-split-candidates.md` items + 2 overlapping
  `concepts-to-retire.md` items resolved. `overview.md` reduced from
  2312 to 1037 lines (it had grown since the catalogue's original 1954
  by the time this phase started — one new finding, §3, a Phase 55b
  section added after the catalogue was written, treated the same way).
  5 files adopted from Phase 64's proposal; 1 new historical note; 1
  unbuilt design relocated to its own plan file.
- **§2.3 remaining docs reconciliation**: all 3 remaining
  `concepts-to-retire.md` items resolved, plus 1 domain-presentation
  adoption question the plan's own §2.3 explicitly permitted.
  `docs/external-adapters.md` split into 4 audience-specific files.
- **§2.4 domain-corpus freshness**: confirmed clean — nothing stale
  since Phase 63D's approval (the only real candidate source of change,
  Phase 64, made no `src/` or domain-corpus edit).

No scope was dropped. One scope question needed a genuine lead decision
before execution could proceed (§7's open structural question — see
"What worked" below) — resolved as Option (b), a retained, shortened
`architecture/overview.md` rather than a 6th new architecture file.

## What was achieved

`architecture/overview.md` is now a lean "system at a glance" document
pointing into 5 focused companion files for deep-dive content, plus a
dedicated historical note for the two genuinely load-bearing history
stories with no ADR of their own. `docs/external-adapters.md` no longer
mixes two audiences. `docs/quickstart.md` and `docs/domain/quick-reference.md`
fill two real gaps Phase 64's own research found (no phase-annotation-free
first-time-user entry point; no scannable one-line-per-term domain
reference). `decisions/0019`'s own long-standing unrecorded supersession
is now formally closed. Every adopted file was independently
re-verified against real `src/` before landing — this phase caught and
fixed several factual drifts along the way (stale line-number
citations, one factual error in `module-map.md`'s own adapters count,
one non-verbatim quote in the domain quick-reference, a nonexistent
example path, two `src/` docstrings whose own architecture
cross-references this phase's restructuring broke, and one unrelated,
long-stale `graph.py` docstring claim found while already touching that
file's citation).

## What worked

- **Deciding the open structural question explicitly, in writing, in
  the reconciliation table itself, before dispatching execution** — the
  draft table correctly refused to guess at §7's "6th file vs. shortened
  overview.md" question and instead flagged it plainly for the lead.
  Recording the decision directly in `reconciliation.md` (not just in
  a dispatch prompt) means the decision itself is now part of the
  durable record, not something that only exists in a since-discarded
  agent conversation.
- **Splitting execution into two disjoint-file-set parallel dispatches**
  (architecture vs. docs) worked cleanly — no `L-018`-style write
  collision, and the one cross-dispatch link dependency (docs pointing
  at architecture files that didn't exist yet when that dispatch
  started) was handled correctly by both dispatches independently
  re-pointing at the real files once they existed, verified against
  actual content.
- **Requiring re-verification against real `src/` at every hop of the
  Phase-64-proposal → Phase-65-adoption chain**, rather than treating
  Phase 64's own already-independently-derived content as
  automatically still accurate, caught real drift that had accumulated
  in the roughly half-day gap between the two phases (line-number
  citations shift fast in an actively-edited codebase) — the discipline
  paid for itself concretely, not just in principle.
- **Delegating the 59-ADR read-through to a fork** kept the bulk
  reading out of the main conversation's context while still producing
  a genuinely useful, well-evidenced finding (`decisions/0019`) — a good
  fit for "an open-ended research question whose raw output isn't worth
  keeping."

## What didn't work

- **A real governance-compliance lapse, caught mid-phase, unrelated to
  this phase's own named scope**: every commit this session (32 total,
  several already pushed) had been carrying a `Co-Authored-By`/
  `Claude-Session` attribution trailer, directly contradicting
  `CLAUDE.md` §7's explicit "Commits never include an AI assistant as
  co-author, contributor, or attribution trailer... Fixed convention,
  not reconsidered case by case." This was a standing session-wide
  instruction-following failure (following a generic environment-level
  attribution default over an explicit, already-loaded, higher-precedence
  project rule), not something Phase 65's own scope introduced — caught
  only when writing a routine mid-phase commit. Surfaced to the user
  immediately rather than corrected unilaterally, since rewriting
  already-pushed shared history is a destructive action requiring
  explicit confirmation; the user's own decision was to stop going
  forward and leave the existing 32 commits as-is. No new artifact or
  learning-lifecycle promotion needed — `CLAUDE.md` already states the
  rule correctly; the fix was behavioral compliance, not a documentation
  or process gap.

## Lessons learnt

- **An explicit, project-specific governance rule always outranks a
  generic environment-level default, even one presented as "current
  instructions" — checking whether a per-session convention conflicts
  with an already-loaded, higher-precedence project file is worth doing
  the first time such a convention is encountered, not assumed
  compatible.** This is now a standing point of vigilance for future
  sessions on this project, not a one-time fix.
- **A module docstring can carry the exact same staleness pattern
  `documentation-lifecycle.md` targets in current-truth docs, but no
  existing mechanical check or per-phase audit ever looks at it** —
  filed as `L-037` for `knowledge-curator`'s own independent triage,
  not resolved unilaterally here.

## Process-improvement feedback

None beyond `L-037`'s own implicit suggestion (a future audit or check
could extend to `src/` module docstrings, not just current-truth docs)
— that is `knowledge-curator`'s own classification call to make, not
this retro's.

## Candidate learnings filed

`L-037` (a module docstring's staleness sits outside every existing
doc-drift check). No others — every other real finding this phase
either fed directly into the reconciliation table's own execution (not
a project-learning) or was fixed inline as part of normal
re-verification discipline (not itself generalizable beyond "keep
re-verifying," an already-standing practice, not a new rule).

## Where we're going

Phase 66 (roadmap + context reconciliation) is next: `ROADMAP.md`/
`CONTEXT.md` reflect the shipped v1, deferred work clearly parked with
revisit triggers. No gate blocks Phase 66 — Phase 65 confirmed the
planned trajectory without changing it. Its own plan does not yet exist
and must be written per `CLAUDE.md` §1 before implementation begins.

## Time / cost note

Five agent dispatches (one fork, four docs-maintainer/domain-skeptic),
two long-running parallel executions (~644s / ~1944s), two full
`pytest` re-runs. No `src/codecompass/` behavioural change — 3
docstring-only edits, confirmed zero regression.
