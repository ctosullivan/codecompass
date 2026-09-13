# Phase 51 retro — Re-run Ledgerkit evaluation (GATE DC)

- **Date:** 2026-09-14
- **Commit(s):** `0cc39e2` (`feat(phase-51)`)
- **Agents used:** `context-evaluator` (GATE DC re-evaluation),
  `docs-maintainer` (reconcile), `docs-reconstructor` (drift audit),
  `release-phase-auditor` (final pass)

## Where we are

Stage C's closing phase. Phase 49 spent Stage B's evidence on a narrow
fix; this phase closes the loop by measuring whether it actually worked.
This completes the redefined-v1's first full cycle: external evidence →
gated decision → narrow fix → independent re-verification.

## Goal

Re-run the same two questions that FAILed in Phases 45/46 — same
questions, same instrument — against Ledgerkit's current state, and
honestly determine whether context quality improved. Exit at GATE DC.

## Scope delivered vs planned

Delivered as planned, with one favorable surprise: Ledgerkit's roadmap
moved again (as it has every phase so far), but this time in a way that
*strengthened* the re-evaluation rather than complicating it — Ledgerkit
finished the exact Stage C work Phase 46 evaluated, producing a brand-new
file (`17-query-semantics-brief.md`) that didn't exist at the original
pin. Checking that new file against the fix was a stronger generalisation
test than re-running only the original two files would have been, and
wasn't something the plan anticipated in that specific form.

## What was achieved

- Both original FAILs (Phase 45's baseline Q2, Phase 46's genuine task)
  **moved to PASS WITH GAPS**, and "would this have misled the agent"
  moved from **yes** to **no** for both — independently re-verified by
  `context-evaluator` via direct inspection and its own `codecompass`/
  `sqlite3` commands, not assumed from the fix landing.
- **Confirmed the fix generalises**: the new `17-query-semantics-brief.md`
  (didn't exist at Phase 46's pin) is also correctly tracked now — this
  wasn't a two-file patch, it's a real mechanism change.
- **Honestly identified what didn't improve, and why it structurally
  can't with this fix**: `query relations` only does literal vendor/Skill
  name-mention detection; with 0 tracked vendors, it can never surface a
  doc's actual content, only whether it's tracked. Advantage stayed LOW
  across both re-runs — the ceiling on this class of question wasn't
  raised, and the fix was never supposed to raise it.
- `planning/reference-projects/ledgerkit/findings.md` GATE DC section
  appended: Phase 49's fix judged a success **on its own, narrow terms** —
  it closed exactly what it was scoped to close, and the earlier
  "smallest justified fix" judgment (rejecting a more general
  configurable-glob mechanism) is validated by this result, not called
  into question.

## What worked

- **Same questions, not new ones** — this is what made the before/after
  comparison a real controlled measurement rather than an incomparable
  fresh datapoint. The direct comparison table in `findings.md` makes the
  claim checkable at a glance.
- **Testing a brand-new, previously-nonexistent file** as a
  generalisation check, discovered opportunistically once the live
  re-check showed Ledgerkit had moved — this is stronger evidence than
  re-running only the original fixtures would have been, and cost nothing
  extra to do.
- **Refusing to round "PASS WITH GAPS, still LOW" up to a clean win** —
  `context-evaluator`'s brief explicitly asked for this, and the report
  delivers: the fix is a real success, stated plainly, without implying
  Ledgerkit-style questions are now well-served by CodeCompass overall.

## What didn't work

No misfires this phase. The evaluation ran cleanly and the result was
unambiguous in both directions (real improvement, real remaining limit).

## Lessons learnt

1. **Re-checking a reference project's live state before a re-evaluation
   phase can turn up evidence *stronger* than what the phase planned
   for**, not just risk of the plan going stale — this project's now four
   consecutive live-recheck experiences (Phases 45, 46, 49's smoke test,
   now 51) have all been informative, not just precautionary.
2. **A "did the fix work" phase should test generalisation, not just
   reproduce the original failing cases** — the new-file check is what
   turns "we fixed these two examples" into "we fixed a mechanism."

## Process-improvement feedback

None new this phase.

## Candidate learnings filed

None new. This phase is pure measurement of an already-filed, already-
promoted fix — no new `CG`/`L` entries expected or found.

**Addendum, caught by `release-phase-auditor`'s Phase 51 audit:** Phase
47's `findings.md` §6 had committed `L-012` and `L-015` to a
promote/discard/retain decision "at Phase 51's re-run," but this phase's
actual scope (re-running two specific hledger-content questions) never
touched either candidate's domain (dependency discovery, single-symbol
query breadth). Resolved as part of this phase's closeout rather than
left dangling: `L-015` stays `retained` (genuinely never in scope across
five intervening phases — not a "no evidence found" case, a "no
opportunity existed" case); `L-012` moved `retained` → `discarded` (now
7 phases old, three unclaimed corroboration opportunities, self-test-only
by its own design — the lifecycle's "~3 phases, no new evidence" norm
applied for real rather than deferred a third time).

## Where we're going — a strategic decision point, not a technical one

GATE DC's own exit language (`v1-redefinition/roadmap.md`) names this
explicitly as a legitimate stopping point: *"a measured improvement over
the foundation baseline, re-validated on a real external project, is a
defensible redefined v1."* Phase 49 is that measured improvement; Phase
51 is that re-validation. Two paths are both defensible from here:

- **Continue into Stage D (Phases 52–55)**: deeper Ledgerkit dogfooding —
  test whether CodeCompass can usefully relate heterogeneous content
  (docs, executable hledger behaviour, compatibility tests) as evidence
  nodes with provenance. This is a materially harder, more novel problem
  than glob coverage, and Phase 51's finding (the *structural* ceiling on
  `query relations` for 0-vendor projects) is exactly the kind of thing
  Stage D would need to address if it's to move the advantage rating past
  LOW at all.
- **Treat this as sufficient and proceed toward Stage F/G**: register
  Technical Clipper as the cross-ecosystem regression check, then
  blank-slate doc reconstruction and release. This accepts LOW advantage
  as the honest, evidenced result for small/dependency-poor projects and
  ships the redefined v1 on the strength of "agent-led development +
  evidence-driven fixing works, even if the advantage ceiling on this
  project shape is modest."

This is a genuine strategic call about how much further to invest before
shipping, not a technical judgment `findings.md` or this retro should
resolve alone — surfaced to the user for a decision.

## Time / cost note

Single session, continuing directly from Phase 49 (prior day; date
rolled over to 2026-09-14 mid-session). No AI enrichment spend
(mechanical-only `codecompass --budget 0` for the re-sync). No
`src/codecompass/` change this phase (measurement only). Full suite
re-verified: 557 passed / 2 skipped, `ruff` clean.
