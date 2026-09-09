# Learnings inbox

The live queue. New candidates go at the top. Format: `TEMPLATE.md`.
Curation rules: `planning/v1-redefinition/learning-lifecycle.md`.

Statuses: `candidate` → `evidence-gathering` → `promoted` / `retained` /
`merged:<id>` / `discarded`.

---

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
- **recurrence:** first occurrence
- **curation (Phase 41 follow-up triage, 2026-09-10):** confirmed
  **retain**. Real gap, not yet actionable — the resolution is a GATE DA
  process decision (Phase 43), not a promotable artifact today. Not
  merged with L-002: different subject (tool permissions vs. doc-accuracy
  ownership) and different owners.
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
- **recurrence:** first occurrence
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
