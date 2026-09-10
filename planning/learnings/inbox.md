# Learnings inbox

The live queue. New candidates go at the top. Format: `TEMPLATE.md`.
Curation rules: `planning/v1-redefinition/learning-lifecycle.md`.

Statuses: `candidate` → `evidence-gathering` → `promoted` / `retained` /
`merged:<id>` / `discarded`.

---

### L-004 — the per-phase docs-drift audit is diff-scoped, so standing rot is invisible to it

- **origin:** Phase 42 (documentation lifecycle; `docs-maintainer` first real use)
- **date:** 2026-09-10
- **project_revision:** cd433f9 (+ Phase 42 commit)
- **observation:** the per-phase `docs-reconstructor` drift audit
  (`decisions/0050`) checks whether *this phase's diff* made a
  current-truth doc false. It cannot catch a doc that was **already**
  false before the phase and that no diff touches. `docs-maintainer`,
  reconciling Phase 42, found **4 passages in `architecture/overview.md`
  (Section C of `architecture-split-candidates.md`)** that describe
  deleted code (`grounded_description.py`, `_RAW_TEXT_CHAR_CAP`, the
  `Depth`/`depth = full` field) as live — errors that have survived
  every phase since Phase 16 (~25 phases) because no phase's diff went
  near those sentences. Same shape as L-003 (planning/** prose) — a
  diff-scoped check has a standing-rot blind spot.
- **evidence:** `planning/v1-redefinition/architecture-split-candidates.md`
  §C items 33–36; `architecture/overview.md` Known Footguns section vs.
  the same file's `## Grounded description — retired` / `## Cost model`
  sections (self-contradictory).
- **classification:** future-improvement
- **status:** retained
- **recurrence:** first occurrence of this specific instance; second
  instance of the *pattern* shared with L-003 (see cluster note below).
- **curation (Phase 42 triage, 2026-09-10, knowledge-curator):**
  provenance accepted — evidence verified independently:
  `src/codecompass/grounded_description.py` does not exist (no file);
  `architecture/overview.md` §"Grounded description — retired" (L247) and
  §"Cost model" state `sync_vendor` makes no AI call ever, while the same
  file's Known Footguns (L1903–1913) still lists "Grounded description is
  fully regenerated … on every `sync` run" and `grounded_description.py`'s
  `_RAW_TEXT_CHAR_CAP` / `_DOCS_FILE_CAP` / `_ESTIMATED_COST_PER_CALL_USD`
  as live — self-contradictory; `Depth` / `VendorConfig.depth` are absent
  from `src/` entirely (`config.py` L41 shows `depth` is a legacy key
  that only parses), confirming split-candidates §C items 35–36 as
  false-as-live. `architecture-split-candidates.md` §C (items 33–36)
  exists and says what this candidate claims.
  **Outcome: retain**, split two ways:
  1. *The specific §C errors* are already escalated — catalogued in
     `planning/v1-redefinition/architecture-split-candidates.md` §C as
     Phase 61 input and recorded in `CONTEXT.md` "Still outstanding"
     (Phase 42). Recommendation handed to `roadmap-context-curator`: also
     pin "Phase 61 must fix architecture-split-candidates.md §C items
     33–36 as corrections, verified against `src/`" into the durable
     Phase 61 stanza of `planning/v1-redefinition/roadmap.md`, since
     CONTEXT.md's outstanding section is overwritten each session. Not
     the curator's file to write.
  2. *The general blind spot* (diff-scoped drift audit misses standing
     content) is the same insight as L-003 — see cluster note. The
     process choice (a `check_user_docs.py` "deleted-names must not
     appear as live" grep-rule / a between-milestones full-doc read /
     accept-and-wait-for-Phase-66) is a **GATE DA (Phase 43)** decision.
- **cluster:** L-003 + L-004 = the "standing-rot blind-spot" pair. Same
  shape (a diff-/product-scoped check has no eyes on content no diff
  touches); different scope (L-003 `planning/**` prose, no owner; L-004
  `architecture/**`, owned by `docs-maintainer`) and different fix, so
  **kept separate, not merged**. Both feed one GATE DA decision.
- **moves forward when:** GATE DA (Phase 43) rules on a standing-content
  complement to the drift audit, **or** a third instance of the pattern
  appears, **or** Phase 61 lands the §C corrections (then log the
  `architecture/overview.md` correction commit here and in `promoted.md`).
  If unresolved at the Phase 47 bulk review, force promote/discard.
- **promoted_to:** — (retained; §C fix tracked for Phase 61)

### L-003 — no independent check on `planning/**` narrative-doc accuracy

- **origin:** Phase 41 (first agent-led loop; `knowledge-curator` observation)
- **date:** 2026-09-10
- **project_revision:** c22d8e4 (+ Phase 41 commit)
- **observation:** `docs-maintainer` owns only `docs/`/`architecture/`/
  `README.md`/`ai-docs/`/`CONTRIBUTING.md`; the per-phase drift audit is
  scoped to *product* docs. `planning/**` prose (large and growing —
  `v1-redefinition/`, phase plans, workflow docs) has no independent
  accuracy check. `knowledge-curator` incidentally caught
  `planning/learnings/README.md`'s stale "not yet operational" status
  this phase; nothing systematic would have.
- **evidence:** the stale line
  (`planning/learnings/README.md` pre-Phase-41 "Status" section) was
  found only because the curator read broadly, not by any check or
  agent remit.
- **classification:** uncertain
- **status:** retained
- **recurrence:** pattern recurred — see the Phase 42 curation note below
  (L-004 is a second instance of the same diff-scoped blind-spot shape,
  in `architecture/**` rather than `planning/**`).
- **curation (Phase 41 follow-up triage, 2026-09-10):** confirmed
  **retain**. Real gap, not yet actionable — the resolution is a GATE DA
  process decision (Phase 43), not a promotable artifact today. Not
  merged with L-002: different subject (tool permissions vs. doc-accuracy
  ownership) and different owners.
- **curation (Phase 42 triage, 2026-09-10):** confirmed **retain**,
  unchanged. Pattern recurrence noted: **L-004** (Phase 42) is a second
  instance of the same shape — a diff-scoped check blind to standing
  content no diff touches — but in `architecture/**` (a current-truth
  product doc that *does* have an owner and a scheduled Phase 61 fix),
  not `planning/**` prose. Kept **separate, not merged**: different
  scope, owner, and fix. Treat L-003 + L-004 as one "standing-rot
  blind-spot" cluster for the GATE DA decision — together they are the
  evidence that the diff-scoped drift audit needs a standing-content
  complement.
- **moves forward when:** GATE DA rules on `planning/**` prose ownership
  (extend `docs-reconstructor` drift-audit scope to
  `planning/v1-redefinition/` + `planning/*.md` / make it the
  `roadmap-context-curator`'s remit / declare it lead responsibility and
  say so), **or** a second stale-prose item in `planning/**` is caught
  incidentally or discovered late (recurrence → promote to whichever
  option GATE DA favours). If still unresolved at the Phase 47 bulk
  review, force a promote/discard.
- **promoted_to:** — (retained pending GATE DA, Phase 43 — options in
  `planning/retros/phase-41-learning-lifecycle-and-retros.md`)

### L-002 — `knowledge-curator` can't run the mechanical check it reasons about

- **origin:** Phase 41 (first agent-led loop)
- **date:** 2026-09-10
- **project_revision:** c22d8e4 (+ Phase 41 commit)
- **observation:** `knowledge-curator`'s `tools:` frontmatter is
  `Read, Grep, Glob, Edit, Write` (no Bash, by design). During the L-001
  triage it edited `planning/learnings/promoted.md` to resolve a
  `check_user_docs.py` finding but could not run the checker to confirm;
  it traced the check logic by hand and flagged it for the lead.
- **evidence:** the agent's own report ("I could not execute the checker
  (Bash is disabled in this session)").
- **classification:** uncertain
- **status:** retained
- **recurrence:** 2nd occurrence — Phase 42 triage (2026-09-10,
  `knowledge-curator`): while editing L-004's provenance in `inbox.md`,
  the curator again could not run `python scripts/check_user_docs.py`
  (Bash disabled for this session and its subagents) and traced the four
  learnings checks by hand instead. This is the "2nd occurrence" trigger
  named in "moves forward when" below — GATE DA (Phase 43) now has a
  concrete recurrence, not just the Phase 41 first instance.
- **curation (Phase 41 follow-up triage, 2026-09-10):** confirmed
  **retain**. Genuine, but the fix is a GATE DA choice between two
  designs (read-only Bash in the `knowledge-curator` `tools:` frontmatter
  vs. a documented "lead runs the confirming check" handoff step in
  `agent-led-workflow.md`) — neither is a promotable artifact until that
  choice is made. A `tools:` change would be a `.claude/` scoped-rule
  edit (lead finalises); the handoff would be a workflow-doc edit. Not
  merged with L-003 (unrelated subject).
- **moves forward when:** GATE DA (Phase 43) picks one of the two
  designs, **or** a later triage again edits `promoted.md` / candidate
  provenance and cannot self-verify the `check_user_docs.py` result
  (2nd occurrence → recurrence, promote the chosen design). If still
  unresolved at the Phase 47 bulk review, force a promote/discard.
- **promoted_to:** — (retained pending GATE DA — options: read-only Bash
  for the curator, or a documented "lead runs the confirming check"
  handoff)

### L-001 — `check_readme_phase_count` conflated "highest done phase" with "product completeness"

- **origin:** Phase 40 (standing up the agent-led roster)
- **date:** 2026-09-09
- **project_revision:** 9ca97ed (observed); fixed in c22d8e4
- **observation:** `scripts/check_user_docs.py::check_readme_phase_count`
  required README's "phases 0-N" claim to equal `max(done phase in
  ROADMAP)`. The redefined-v1 Stage A–F phases (39+) are a
  process/validation milestone group, not product features — every one
  of them marked `done` would have forced a misleading README bump
  ("phases 0-43 done!" implies more shipped product than exists) or left
  the `--strict` DoD gate permanently red across Stage A.
- **evidence:** the check FAILs the moment Phase 40's ROADMAP row flips
  to `done` while README honestly says "phases 0-38" (the foundation).
  Fixed in this phase's commit by excluding ROADMAP content from the
  `## Redefined CodeCompass v1` heading onward; regression test
  `tests/test_check_user_docs.py::TestReadmePhaseCount::test_ignores_done_phases_in_redefined_v1_section`.
- **classification:** invariant (the fix + regression test landed with
  Phase 40; this entry records *why*)
- **status:** promoted
- **recurrence:** first occurrence
- **promoted_to:**
  `tests/test_check_user_docs.py::TestReadmePhaseCount::test_ignores_done_phases_in_redefined_v1_section`
  + `scripts/check_user_docs.py::check_readme_phase_count` @ c22d8e4
  (logged in `promoted.md`, Phase 41 triage 2026-09-10)
