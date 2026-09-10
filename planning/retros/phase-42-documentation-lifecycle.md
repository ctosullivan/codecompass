# Phase 42 retro — Documentation lifecycle (incremental + closeout gate)

- **Date:** 2026-09-10
- **Commit:** `feat(phase-42)` (hash in a follow-up)
- **Auditor verdict:** PASS WITH NON-BLOCKING OBSERVATIONS
  (`_audit-phase-42.md`) — all §5 DoD conditions hold. 3 advisory
  observations: (1) CHANGELOG per-phase stacking vs canonical
  type-grouping — folded into `milestone-closeout-checklist.md` step 11
  as a Phase 67 action; (2) checklist step 11 overlaps Phase 67 —
  clarified in the checklist; (3) `release-phase-auditor` brief said
  "At Phase 65" for the checklist which runs at Phase 66 — brief
  reworded. All three addressed this commit.
- **Agents used:** `docs-maintainer` (first real use — reconciliation +
  36-item `architecture/overview.md` split-candidate catalogue),
  `docs-reconstructor` (per-phase drift audit → **NO DRIFT**),
  `roadmap-context-curator` (CHANGELOG/CONTEXT/ROADMAP; NO-GO on `done`
  until closeout complete), `knowledge-curator` (L-004 triage → retained,
  clustered with L-003), `release-phase-auditor` (DoD audit)
- **Reports:** `_drift-audit-phase-42.md` (NO DRIFT), `_audit-phase-42.md`

## Where we are

- **Redefined-v1 Stage A** ("make CodeCompass agent-led"), phase 4 of 5.
  Foundation = phases 0–38 (shipped, unpublished — gate G2-b holds all
  release until Phase 67).
- **Built directly on:** Phase 40 created the `docs-maintainer` and
  `docs-reconstructor` agents; Phase 41 gave `check_user_docs.py` the
  `Finding.strict` (blocking vs informational) mechanism and added the
  per-phase drift audit as a DoD condition. Phase 42 operationalises the
  *everyday half* of the documentation lifecycle those pieces were built
  for: the `docs-maintainer` brief in usable form, three more
  deterministic doc checks, and the milestone closeout gate as a
  concrete checklist.
- **State after this phase:** the documentation lifecycle is fully
  specified end to end — per-phase (incremental `docs-maintainer` +
  independent drift audit) and per-milestone (blank-slate reconstruction
  Phase 60 → reconciliation Phase 61 → closeout checklist Phase 66).
  `check_user_docs.py` now has 12 rules. Stage A has one phase left
  (43: dogfood a real code change → GATE DA).

## Goal

Operationalise the everyday half of `documentation-lifecycle.md`: finalise
the `docs-maintainer` brief, add deterministic link/example/ADR checks to
`check_user_docs.py`, and write `planning/milestone-closeout-checklist.md`
(the Phase 66 gate). Blank-slate reconstruction stays Phase 60.

## Scope delivered vs planned

Delivered as scoped. Deviations:

- **No `CLAUDE.md` change.** The plan said "apply the approved §5 diff
  (A2) if not already applied" — it was applied in Phase 40, so this
  phase touches no protected file.
- **The new checks flagged nothing on the current repo.** The plan
  expected "some stale links / examples given `architecture/overview.md`'s
  size". Reality: all 77 internal links resolve, all fenced `codecompass`
  examples are valid, all 49 ADRs have a Status and every
  `decisions/NNNN` cross-reference resolves. So `docs-maintainer`'s
  "fix what it flags" step was a no-op — its first real use was instead
  (a) confirming Phase 42's diff touched no current-truth doc, and
  (b) producing the `architecture/overview.md` split-candidate catalogue.
- **`docs-maintainer` surfaced 4 pre-existing self-contradictions** in
  `architecture/overview.md` (Known Footguns describes the deleted
  `grounded_description.py` / its constants / `Depth.FULL` as live).
  These are ~25 phases old, not caused by Phase 42, and deferred to
  Phase 61 (the architecture reconciliation) per the "do not restructure
  `architecture/overview.md`" rule — but they are real current-truth
  errors. Escalated: `CONTEXT.md` "Still outstanding", candidate
  learning **L-004**.
- **New planning file not in the plan's Files list:**
  `planning/v1-redefinition/architecture-split-candidates.md` (the
  `docs-maintainer`'s Phase 61 input). Added to the plan's Files section.

## What was achieved

- `check_user_docs.py`: `check_internal_links_resolve`,
  `check_fenced_codecompass_examples`, `check_adr_status_and_supersedes`
  + a shared fence-state line iterator + `_codecompass_command_names`
  (parses `@app.command`, `@query_app.command`, and
  `app.add_typer(name=…)`). +11 tests. Live-demoed catching a broken
  link + `codecompass frobnicate` + `query bogus`, then reverting.
- `.claude/agents/docs-maintainer.md` — operational brief: current-truth
  principle, the new checks, "flag `architecture/overview.md` split
  candidates, don't restructure", "no current-truth doc affected" is a
  valid output.
- `planning/milestone-closeout-checklist.md` — the 11-step Phase 66 gate,
  each step with an owner and a "done" signal; the tag/release step is a
  human-decision gate.
- `planning/v1-redefinition/architecture-split-candidates.md` — 36
  catalogued passages (5 section-level, 27 trims, 4 corrections) for
  Phase 61.

## Lessons learnt

1. **The docs were already clean.** The expectation that
   `architecture/overview.md`'s size would produce link/example
   violations was wrong — the *mechanical* checks (links, examples, ADR
   refs) pass. What's actually wrong with that file is *semantic*:
   history-narration and 4 factual self-contradictions, neither of which
   a mechanical check detects. The value of Phase 42 is the
   `docs-maintainer` reading + cataloguing, not the checker output.
2. **The per-phase drift audit has a standing-rot blind spot** (→ L-004,
   near-duplicate of L-003). It's diff-scoped: a doc that was already
   false, and that no phase's diff touches, is invisible to it. The 4
   `architecture/overview.md` self-contradictions survived Phases 16–41.
   Mitigations already exist (milestone-closeout checklist step 6 is a
   full architecture read; Phase 61 will fix §C) but the gap is real
   for the ~20 phases in between.
3. **`docs-maintainer`'s first real use produced a large, useful
   artifact** (the 36-item catalogue) even though it made zero edits.
   The role earns its keep on *assessment*, not just editing — worth
   noting for GATE DA.
4. **Phase 42 changed no product behaviour**, so the drift audit and
   `docs-maintainer` reconciliation were both quick "nothing to do here"
   — the designed cheap path for a governance/tooling phase held again
   (same as Phase 41).

## Process-improvement feedback

- **Consider a between-milestones full-doc read**, not just at Phase 66 —
  or accept that standing rot waits for the milestone. GATE DA should
  decide; L-003 + L-004 are the evidence. A cheap option: a
  `check_user_docs.py` grep-rule for a small hand-maintained list of
  "names of deleted things that must not appear as live" (`Depth`,
  `grounded_description`, `promote` — already partly covered by Phase
  38's audit, but not enforced).
- **The plan's "expect some stale links / examples" was an untested
  assumption.** Plan verification steps that assume the checker *will*
  find something should be softer ("run the checks; fix anything real")
  — otherwise a clean result reads like the check is broken.
- `docs-maintainer` ran ~262k subagent tokens reading
  `architecture/overview.md` (1,954 lines) end to end. Proportionate for
  the catalogue it produced, but a signal that a full read of that file
  is expensive — another reason Phase 61's split matters.

## Candidate learnings filed

- **L-004** — the per-phase docs-drift audit is diff-scoped, so
  pre-existing standing rot in a current-truth doc is invisible to it
  (evidence: 4 `architecture/overview.md` self-contradictions describing
  deleted code as live, ~25 phases old). Near-duplicate shape with L-003.
  Curator to weigh merge / promote-to-Phase-61-scope.

## Where we're going

- **Next: Phase 43** (dogfood the agent-led loop). No gate blocks it.
  The lead picks **one real, small CodeCompass code change** (candidates
  in the plan: `CLAUDE.md` → `ai-docs/README.md` pointer; `query skills`
  surfacing `slash_command` rows; `/discovery` whole-project `sync`
  trigger gap; the pending `ai-docs/` enrichment run) and runs it through
  the full 14-step workflow, then **GATE DA**: did each role earn its
  keep? Phase 42 pre-loads GATE DA with two more inputs — `docs-maintainer`
  earns its keep on assessment not editing (lesson 3), and the
  standing-rot blind spot (L-004).
- **Phase 43 will be the first phase to actually change `src/codecompass/`**
  since the redefinition began — so it's the first real test of the
  `docs-maintainer` *editing* path and the drift audit *finding*
  something, not just confirming "nothing changed".
- **Trajectory: confirmed.** Stage A is on track to close at Phase 43.
  The accumulated GATE DA inputs (L-002 curator Bash, L-003/L-004
  standing-rot blind spots, the triage/retro ordering inversion, the
  process-weight watch, `docs-maintainer` value-is-assessment) are the
  agenda for the GATE DA retro. Nothing reshapes Stage B–F.
- **Phase 61 gains a concrete input** (`architecture-split-candidates.md`)
  and a concrete obligation (fix §C's 4 corrections, verified against
  `src/`).

## Time / cost note

One session. 5 agent dispatches (`docs-maintainer` the heaviest at ~262k
subagent tokens for the full `architecture/overview.md` read). Full
`pytest` 543 passed / 1 skipped. No CodeCompass product-side AI spend.
Roughly the length of Phase 41 — the `architecture/overview.md` catalogue
was the bulk of the work.
