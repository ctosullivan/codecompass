# Phase 43b retro — Two `check_user_docs.py` rules from GATE DA

- **Date:** 2026-09-11
- **Commit(s):** `3b7f27a` (`feat(phase-43b): two check_user_docs.py
  rules from GATE DA + arch.md fix`)
- **Auditor verdict:** **PASS WITH NON-BLOCKING OBSERVATIONS**
  (`planning/retros/_audit-phase-43b.md`) — no blocking gap; every
  re-run check matched independently (`pytest` 554/1, `ruff` clean,
  `--strict` clean, both new checks called directly return `[]`, the 4
  `architecture/overview.md` fixes re-verified against `src/`, the
  auditor's own violation-injection spot-check caught both). 4
  non-blocking observations, all closeout wording: (1) `CONTEXT.md` /
  plan status / `roadmap.md` said triage "has not yet run" when it
  demonstrably had (L-003/L-004/L-005) — corrected in this closeout
  commit; (2) the retro's "Where we're going" pre-empted this verdict —
  reconciled here; (3) **L-006** was committed to being triaged at Phase
  43b but the first triage pass missed it — a follow-up
  `knowledge-curator` dispatch closed this; (4) commit-hash placeholders
  — filled in this commit.
- **Agents used:** `docs-maintainer` (the §C fix), `docs-reconstructor`
  (per-phase drift audit), `roadmap-context-curator`, `knowledge-curator`
  (L-003/L-004/L-005 disposition, then a follow-up pass for L-006),
  `release-phase-auditor`
- **Reports:** `_drift-audit-phase-43b.md`, `_audit-phase-43b.md`

## Where we are

- **Redefined-v1, the Stage A→B seam** — the second of two user-requested
  bridge phases between Stage A (39-43, done, GATE DA passed) and Stage B
  (44+). Phase 43c (agent context-suggestion pathways) landed first;
  this phase is independent of it, GATE-DA-scheduled rather than
  user-requested.
- **Built directly on:** GATE DA (Phase 43's retro) named these two
  checks as the concrete remedy for two clusters of findings accumulated
  across Stage A: the "standing-rot blind-spot" pair (**L-003 + L-004** —
  a diff-scoped drift audit can't see pre-existing false content no
  phase's diff touches) and **L-005**'s invariant half (a generated file
  can be hand-edited and silently drift from its generator, as
  `docs-maintainer` did to `.claude/skills/codecompass/SKILL.md` in
  Phase 43).
- **State after this phase:** `check_user_docs.py` has 14 rules (46
  tests, +9). The 4 concretely-diagnosed `architecture/overview.md`
  self-contradictions (L-004's motivating evidence) are fixed, verified
  against `src/`. Both remaining GATE DA-scheduled checks are live and
  clean. Next: Phase 44, Stage B begins.

## Goal

Implement the two `check_user_docs.py` rules GATE DA decided on:
`check_no_deleted_names_as_live` (promotes L-003+L-004) and
`check_generated_artifacts_match_source` (promotes L-005's invariant
half). The plan left one judgment call open: whether to also fix
`architecture/overview.md` §C's 4 self-contradictions here or leave them
to Phase 61.

## Scope delivered vs planned

Delivered, plus the judgment call resolved **in favour of fixing now**:

- **§C's 4 items were fixed this phase**, not deferred. Each was small,
  independently verifiable against `src/` in isolation (unlike the
  broader §A/§B history-shaped trims, which need the full Phase 61
  restructuring context to do well) — the plan's own criterion for
  "decide during implementation: if fixing §C here is clean, do it."
  Verifying against `src/` surfaced a **correction to GATE DA's own
  proposed retired-names list**: `_RAW_TEXT_CHAR_CAP` and `_DOCS_FILE_CAP`
  are *not* retired — both constants still exist, unchanged, in
  `enrichment.py`. Only their *module attribution*
  (`grounded_description.py`) and one *renamed* sibling constant
  (`_ESTIMATED_COST_PER_CALL_USD` → `_ESTIMATED_COST_PER_BATCH_USD`) were
  stale. Item 34's fix is a re-attribution + rename, not the deletion the
  candidate-learning entry's phrasing ("describes constants in a deleted
  module") implied.
- **The `check_no_deleted_names_as_live` design changed during
  implementation.** The plan didn't specify a matching algorithm; a
  naive "flag any line containing a retired name" design was tried first
  and immediately produces ~30 false positives (this file narrates its
  own implementation history extensively and *correctly* — bare name
  matching can't tell "grounded_description was retired in Phase 16"
  from "grounded_description regenerates on every sync"). Iterated to: a
  small "historical marker" vocabulary, matched against the whole
  **prose unit** (a wrapped bullet or blank-line-delimited paragraph),
  not a fixed line window — calibrated against this repo's real prose
  until it produced zero false positives, confirmed by a positive-case
  test that a genuinely live-sounding claim still gets caught.

## What was achieved

- `check_no_deleted_names_as_live` + `check_generated_artifacts_match_source`
  live in `scripts/check_user_docs.py`, both blocking, both clean (0
  findings) against this repo's own docs, and `.claude/skills/docs-sync/SKILL.md`
  lists them as items 13-14. 9 new tests (5 + 4), including one
  `test_clean_against_real_repo` per check (the same "does the check fire
  on itself" discipline the module already used) and one
  false-positive-shaped regression test each (a historically-framed
  mention that must NOT fire; a fenced code example that must NOT fire).
- `architecture/overview.md`'s 4 self-contradictory passages (items
  33-36) are corrected, each verified against `src/codecompass/sync.py`,
  `enrichment.py`, and `core.py` directly — by the lead first, then
  independently by `docs-maintainer` applying the fix, then independently
  again by `docs-reconstructor`'s drift audit.
- `planning/v1-redefinition/architecture-split-candidates.md` §C marked
  resolved; its Count line updated (36 → 32 still outstanding for
  Phase 61).

## What worked

- **Verifying the plan's own proposed retired-names list against `src/`
  before implementing it**, rather than transcribing GATE DA's
  Phase-43-retro phrasing verbatim. `_RAW_TEXT_CHAR_CAP`/`_DOCS_FILE_CAP`
  turned out to still exist — if the check had used the plan's literal
  wording ("constants in a deleted module") as its retired-names list, it
  would have flagged every legitimate current mention of those two
  constants in `enrichment.py`'s own future documentation, false-positive
  noise from day one. The `_iter_learning_candidates`/ADR-cross-reference
  checks already model this "verify against src/, not against the
  candidate's prose" discipline; this phase applied it one level up, to
  the plan itself.
- **Building the check, testing it against the real repo, and iterating
  the design before writing a single regression test.** The naive
  line-window version's 9 false positives were caught by manual testing
  in minutes, not by a later audit round — cheaper feedback loop than
  Phase 43's 3-round auditor FAIL trail.
- **`docs-maintainer` and `docs-reconstructor` running on the *same*
  diagnosed fixes independently found nothing new to disagree on** — the
  lead's upfront `src/` verification (sync.py/enrichment.py/core.py) held
  up under both an independent apply and an independent audit.
- **Deciding to fix §C now, in scope, rather than deferring.** The 4
  items were small and self-contained; deferring them to Phase 61 would
  have meant carrying 4 more phases of known-false documentation for no
  reason, and Phase 61's actual job (the §A/§B restructuring) doesn't
  need these 4 fixed first or get easier by having them deferred.

## What didn't work

- **The first version of `check_no_deleted_names_as_live` was
  under-designed.** A "flag any line with a retired name" heuristic is
  the obvious first attempt and it's wrong for a documentation file that
  legitimately discusses its own history at length — this should have
  been anticipated from L-003/L-004's own description of the problem
  (this file "narrates decision history"), not discovered by running the
  check and counting false positives. Lesson: for any check operating on
  *prose*, write the "does it false-positive on our own legitimately
  correct content" test **first**, before the detection logic.
  `docs-maintainer`, applying the fix independently, hit the same 9 false
  positives against an earlier draft of the check and correctly flagged
  it back rather than silently working around it — exactly the
  "don't repair what you're evaluating" discipline paying off, from the
  other direction (an implementer flagging a tooling gap, not an auditor).
- **The plan's candidate retired-names list description ("constants in a
  deleted module") was imprecise** and would have produced a wrong check
  if implemented literally. Not a large cost here (caught before
  landing), but a reminder that GATE DA retro language is a pointer to
  investigate, not a spec to transcribe.
- **The lead's step-12 `knowledge-curator` dispatch omitted L-006**,
  despite `planning/CONTEXT.md` explicitly committing (during Phase 43's
  closeout) to confirm L-006's disposition "at Phase 43b triage." The
  first triage pass only named L-003/L-004/L-005 in its prompt. Caught by
  the `release-phase-auditor`, not by the lead — a small instance of the
  exact pattern L-006 itself is about (a planning-doc commitment that
  quietly goes stale). Fixed with a targeted follow-up `knowledge-curator`
  dispatch rather than hand-patching. Lesson: when drafting a triage
  dispatch, grep `inbox.md` for *any* candidate whose `promoted_to` or
  prior curation note names "this phase" as its resolution point, not
  just the ones the plan explicitly anticipated.

## Lessons learnt

1. **A "detect stale/retired content" check needs a false-positive test
   suite before its true-positive one** — the failure mode (flagging
   correct historical narration as a live-claim error) is the whole
   reason the check exists to be careful about, so proving it doesn't
   trigger on genuinely correct prose is the harder and more important
   half of validating it.
2. **"Verify the plan's own factual claims against `src/`, not just the
   implementation's" is a recursive application of the project's
   standing discipline.** `_RAW_TEXT_CHAR_CAP` surviving under a new
   module was invisible from the retro's summary alone; only checking
   `enrichment.py` directly surfaced it.
3. **Prose-structure-aware matching (bullet/paragraph units) beats a
   fixed line window for markdown.** This doc's bullets can wrap 5+
   lines and back-to-back bullets have no blank-line separator between
   them — a fixed window either under- or over-reaches depending on
   paragraph length; matching the actual markdown unit is more correct
   and not meaningfully more code.
4. **A "fix now vs. defer" judgment call should default to fixing when
   the fix is independently verifiable in isolation** — §C's items didn't
   need Phase 61's broader restructuring context, so deferring them would
   have been pure cost (more phases of known-false docs) for no benefit.

## Process-improvement feedback

- No new agent-boundary or workflow friction this phase — `docs-maintainer`
  correctly stayed inside the exact 3 edits specified, correctly flagged
  the check's false positives back to the lead instead of working around
  them, and correctly left the out-of-scope §A/§B material untouched.
  `docs-reconstructor`'s drift audit had, for the first time, a
  genuinely substantive independent-verification job on `architecture/overview.md`
  content (not just "nothing changed") — same shape as Phase 43's first
  real drift-audit use.

## Candidate learnings filed

- **L-004** and **L-005**'s invariant half — triaged (`knowledge-curator`,
  Phase 43b): both **promoted** (the checks + `architecture/overview.md`
  §C corrections; `promoted.md` lines added).
- **L-003** — triaged: stays **retained**. The check's `_iter_doc_files`
  scope (`README.md`/`docs/`/`ai-docs/`/`architecture/`/`examples/`/
  `CONTRIBUTING.md`) structurally excludes `planning/**`, so L-003's own
  originally-cited evidence (a stale line in
  `planning/learnings/README.md`) is outside what this phase's check
  covers — it resolves L-004's domain, not L-003's, confirming the
  earlier curation note's "by analogy only" caveat. Flagged for the
  Phase 47 bulk review (3rd consecutive phase retained without
  promote/discard).
- **L-008** (new, filed at triage) — from this retro's "what didn't
  work": write the false-positive test *before* the true-positive one
  for any prose-matching check. **Retained** (single occurrence);
  recommended destination is an authoring note in
  `.claude/skills/docs-sync/SKILL.md`.

## Where we're going

- **Next: Phase 44** — Stage B begins, now that this closeout (auditor
  **PASS WITH NON-BLOCKING OBSERVATIONS**, L-006 follow-up triage) lands
  in the same commit. The reference-project protocol + context-quality
  evaluation spec become operational templates + a registry; briefs
  `context-evaluator` and `reference-project-tester` for their first real
  use; writes the Phase 45 plan.
- **No gate blocks Phase 44.** Both Stage A→B bridge phases (43b, 43c)
  are `done` as of this commit.
- **Trajectory: confirmed.** Nothing here reshapes Stage B. The
  `context-health-planner`'s first genuine solo run (tracked from Phase
  43c) still lands before Phase 45, on the Technical Clipper clone.

## Time / cost note

One session. No `src/codecompass/` change → `pytest` 554 passed / 1
skipped (was 545, +9), `ruff` clean. `check_user_docs.py --strict` clean,
including both new checks against this repo's own real docs. No
CodeCompass product-side AI spend. Together, 43b + 43c pushed Stage A's
adjacent-phase count past the `roadmap.md` "~6 sessions" tripwire, but
per that note the cause is added user-requested scope, not roster bloat —
the tripwire's remedy (prune the roster) doesn't apply.
