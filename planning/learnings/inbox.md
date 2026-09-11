# Learnings inbox

The live queue. New candidates go at the top. Format: `TEMPLATE.md`.
Curation rules: `planning/v1-redefinition/learning-lifecycle.md`.

Statuses: `candidate` → `evidence-gathering` → `promoted` / `retained` /
`merged:<id>` / `discarded`.

---

### L-008 — a prose/text-matching check needs its false-positive regression tests before its true-positive one

- **origin:** Phase 43b (`check_no_deleted_names_as_live`'s first design
  iteration; retro "What didn't work" #1 + Lesson 1)
- **date:** 2026-09-11
- **project_revision:** `<Phase 43b commit>`
- **observation:** the first implementation of
  `check_no_deleted_names_as_live` used a naive "flag any line containing
  a retired name" heuristic and produced ~30 false positives when run
  against this repo's own real docs (which legitimately discuss retired
  concepts historically at length — exactly the failure mode L-003/L-004's
  own description of the problem already implied). The design was
  iterated to prose-unit matching with a historical-marker vocabulary,
  calibrated until a manual run produced zero false positives, *before*
  any regression test was written. The false-positive-shaped tests
  (`test_does_not_flag_historically_framed_mention`,
  `test_ignores_fenced_code_examples`) were written after the design
  settled, not before, so the ordering wasn't literally
  false-positive-test-first — but the manual-testing equivalent of that
  discipline (test against false positives before against true positives)
  is what caught the flaw cheaply, in minutes, rather than in a later
  audit round. This is a reusable authoring discipline for *any future
  check that pattern-matches over prose* (not just this one) — including,
  plausibly, Stage C's mechanical-detection heuristics for context gaps
  (`planning/context-gaps/`), which will also be text/pattern matching
  over code/docs and share the same false-positive risk shape.
- **evidence:** `planning/retros/phase-43b-standing-doc-drift-checks.md`
  "What didn't work" #1 and Lesson 1 ("A 'detect stale/retired content'
  check needs a false-positive test suite before its true-positive
  one"); `tests/test_check_user_docs.py::TestNoDeletedNamesAsLive`
  (`test_does_not_flag_historically_framed_mention` L397,
  `test_ignores_fenced_code_examples` L418) as the landed artifact
  demonstrating the calibrated design.
- **classification:** project-rule
- **status:** candidate
- **recurrence:** first occurrence
- **curation (Phase 43b triage, 2026-09-11, knowledge-curator):**
  provenance accepted — the retro text and the named tests both exist as
  cited. **Outcome: retain**, not promote. Real and specific, with a
  plausible destination (a short authoring note in
  `.claude/skills/docs-sync/SKILL.md`, which already lists both Phase 43b
  checks as items 13-14: "when adding a new `check_user_docs.py` rule
  that pattern-matches over prose, write and run the false-positive case
  — 'does this fire on content that is correctly discussing the matched
  term historically/in a code example' — before writing the true-positive
  regression test; a naive first design commonly over-fires on exactly
  this project's own history-narrating docs, per
  `check_no_deleted_names_as_live`'s first iteration") — but single
  occurrence, and the curator has no write access to `.claude/skills/`
  (outside `planning/learnings/**`/`planning/context-gaps/**`/draft files
  under `planning/`) to land it directly. Not promoted until either (a)
  the lead/`docs-maintainer` adds the note and a commit exists to log
  here, or (b) a second prose-matching check hits the same false-positive
  trap, at which point recurrence makes the case stronger. Considered and
  **declined to file** a second candidate for the retro's other "what
  didn't work" item (the plan's retired-names list being factually
  imprecise, `_RAW_TEXT_CHAR_CAP`/`_DOCS_FILE_CAP` surviving): that item
  is not a gap needing a new mechanism — it's a single-occurrence
  successful application of an *already-existing* project discipline
  ("verify against `src/`, not the candidate's prose", which the retro
  itself notes the `_iter_learning_candidates`/ADR-cross-reference checks
  already model) catching an error before it landed. Filing a learning
  for a discipline that already exists and worked as intended would be
  filing to have filed one, not because there's an unaddressed gap.
- **promoted_to:** — (retained; destination is a `docs-sync/SKILL.md`
  authoring note, pending lead action or recurrence)

### L-007 — a plan's "Done when" should separate "the mechanism exists" from "the mechanism has produced output"

- **origin:** Phase 43c (retro lesson 2 + "what didn't work" #2;
  `knowledge-curator` triage)
- **date:** 2026-09-11
- **project_revision:** f47f3e2 (Phase 43c plan commit)
- **observation:** Phase 43c's plan Verification said the
  `context-health-planner` agent "runs once for real and produces the
  `context-health.md` above". The agent was *created* this phase, so the
  lead wrote the first `context-health.md` by hand (running the same
  `codecompass query` commands) and the agent's first genuine solo run
  slipped to before Phase 45. "An agent will own X" and "X has been
  produced by that agent this phase" are different commitments; a plan
  that conflates them lets an artifact land with a stubbed first
  datapoint and no gate catching the gap. Same shape as the same plan's
  §2 over-scoping (it predicted three `conditional-generalisation.md`
  edits; one was needed).
- **evidence:** `planning/phase-43c-agent-context-pathways.md`
  Verification vs. `planning/retros/phase-43c-agent-context-pathways.md`
  "What didn't work" #2 and "Where we're going" (agent's first real run
  deferred to before Phase 45); `planning/context-health.md`'s first
  assessment is lead-written narrative, not an agent report.
- **classification:** workflow
- **status:** retained
- **recurrence:** first occurrence (the §2 over-scoping item in the same
  retro is a weaker related instance of plan-estimate imprecision)
- **curation (Phase 43c triage, 2026-09-11, knowledge-curator):**
  provenance accepted — both sources are this phase's own plan + retro,
  cross-checked against `planning/context-health.md` (first assessment is
  lead narrative, no agent header). **Outcome: retain.** Real and
  specific but single-instance and not yet actionable; the candidate
  destination is a one-line addition to the plan-file guidance (CLAUDE.md
  §1 / the `agent-led-workflow.md` step-1 plan template: "Done-when
  distinguishes 'the mechanism exists' from 'the mechanism has produced
  output this phase'"). That is a CLAUDE.md-class change and needs
  recurrence evidence before it is worth proposing via
  `planning/v1-redefinition/proposed-governance-changes.md`. Revisit at
  the Phase 47 bulk review or on the next occurrence.
- **promoted_to:** — (retained; revisit Phase 47 or on recurrence)

### L-006 — the curator reconciles *before* the retro, but a GATE/retro can change the plan

- **origin:** Phase 43 (dogfood; `release-phase-auditor` FAIL ×3 on
  planning-doc bookkeeping)
- **date:** 2026-09-10
- **project_revision:** d34a486
- **observation:** the 14-step workflow runs `roadmap-context-curator`
  (step 10) *before* the lead writes the retro (step 11). For most phases
  that's fine. But a **GATE phase** (or any retro that schedules a
  follow-up phase or records roster amendments) *changes the roadmap*
  after step 10 — so the curator's reconciliation is already stale when
  it lands. Phase 43's `release-phase-auditor` FAILed 3 times, entirely
  on planning-doc bookkeeping the lead then hand-patched piecemeal
  (missing `43b` ROADMAP row — `phase-43b` was created after the curator
  ran; `v1-redefinition/roadmap.md` GATE DA outcome — the curator read
  "roadmap.md" as `ROADMAP.md`; `43b` absent from the CONTEXT forward
  path — written before the retro existed; then the CONTEXT fix left the
  file self-contradictory). The lead is a poor substitute for the
  curator on multi-file planning-doc consistency.
- **evidence:** `planning/retros/_audit-phase-43.md` — 3 audit rounds,
  every FAIL a planning-doc gap, zero code defects.
- **classification:** workflow
- **status:** promoted
- **recurrence:** first occurrence (but note: the auditor has caught a
  planning-doc gap on *every* phase 41–43 — 41 plan Files, 42 obs, 43 ×3)
- **curation (Phase 43b follow-up triage, 2026-09-11, knowledge-curator):**
  dispatched specifically to close the gap the `release-phase-auditor`
  flagged (`planning/retros/_audit-phase-43b.md` observation 3): L-006 was
  committed to being triaged at Phase 43b's own triage but the first
  triage pass (which covered L-003/L-004/L-005) missed it. Verified two
  things independently, by reading the artifacts directly (no Bash
  available):
  1. **The amendment landed, textually, exactly as the `promoted_to` note
     describes.** `planning/agent-led-workflow.md` step 11 now reads:
     "If the retro schedules a follow-up phase, amends the roster or
     workflow, or otherwise changes the plan — re-dispatch
     `roadmap-context-curator` after writing it (step 10's reconciliation
     is now stale). Don't hand-patch the planning docs yourself; that
     drifts (GATE DA, Phase 43 — L-006)." `.claude/agents/roadmap-context-curator.md`
     "Hard rules" now opens with "Reconcile *every* planning doc, not just
     the top three," names `ROADMAP.md`/`CONTEXT.md`/`CHANGELOG.md` *and*
     `v1-redefinition/roadmap.md`, the phase's own `phase-N-*.md` status
     line, and any new `phase-*.md` a retro just scheduled, and
     cites "(GATE DA, Phase 43 — L-006)" as its own provenance. Both
     match the `promoted_to` note verbatim in substance.
  2. **The dispatching task's stronger claim — that the specific
     "re-dispatch after a plan-changing retro" clause fired and caught a
     premature `done` twice (43c and 43b) — does not hold up on a close
     read, and I'm not accepting it uncritically.** Re-reading both
     retros directly: `phase-43c-agent-context-pathways.md`'s own
     "Candidate learnings filed" section states outright "L-006 stays
     parked — its disposition confirmation is scheduled for Phase 43b
     triage… 43c's roster change was resolved *before* the
     `roadmap-context-curator` ran, so it did not re-trigger L-006's
     staleness pattern" — i.e., 43c is documented, in its own retro, as a
     case where the amendment's specific trigger condition (a
     *post*-curator-run plan change) never fired. Phase 43b's own retro
     "Where we're going" section doesn't schedule a new follow-up phase
     or amend the roster/workflow either — it just confirms "no gate
     blocks Phase 44." So neither phase is actually a case of the
     re-dispatch clause activating; the `release-phase-auditor`'s reports
     for both phases show the curator's step-10 run correctly holding
     `ROADMAP.md`/`v1-redefinition/roadmap.md`/the phase-plan status line
     at "in progress" pending retro+triage+audit — which is just the
     *ordinary* step-10 phase-end job (§5's "only if every DoD condition
     holds"), not the amendment's new re-dispatch mechanism specifically.
  3. **What the evidence *does* support, on the corrected reading: the
     amendment's broader remedy — multi-doc reconciliation instead of the
     lead hand-patching — has demonstrably worked, twice, on the exact
     failure shape L-006 recorded.** Phase 43 itself needed a 3-round
     `release-phase-auditor` trail (FAIL → FAIL → PASS), every FAIL a
     planning-doc bookkeeping gap across `ROADMAP.md` /
     `v1-redefinition/roadmap.md` / `CONTEXT.md`. Since the amendment
     landed, both Phase 43c (`_audit-phase-43c.md`) and Phase 43b
     (`_audit-phase-43b.md`) passed their `release-phase-auditor` audit on
     the **first round** (both "PASS WITH NON-BLOCKING OBSERVATIONS," no
     FAIL), with every named planning doc (`ROADMAP.md`,
     `v1-redefinition/roadmap.md`, the phase-plan status line,
     `CONTEXT.md`) found internally consistent (the only outstanding items
     in both were the expected pre-commit "still says in-progress, flip
     in the closeout commit" state and commit-hash placeholders — not
     bookkeeping contradictions). That is a real before/after: the
     specific defect pattern L-006 evidenced (planning-doc drift the lead
     alone couldn't keep straight) has not recurred across two
     subsequent phases. **Outcome: promote**, on this corrected basis —
     the amendment landed and the general remedy it encodes is working —
     while flagging that the narrower "re-dispatch after a plan-changing
     retro" trigger specifically remains untested (no retro since Phase
     43 has actually changed the plan *after* the curator's step-10 run)
     and should be watched the next time a GATE or retro does schedule a
     follow-up phase after step 10.
- **promoted_to:** `planning/agent-led-workflow.md` step 11 +
  `.claude/agents/roadmap-context-curator.md` "Hard rules" (re-dispatch
  after a plan-changing retro; reconcile every planning doc) @ `<commit>`
  — *lead fills the real short hash for the Phase 43 commit these landed
  in*.

### L-005 — `docs-maintainer` edited a generated file (it doesn't distinguish generated vs hand-authored)

- **origin:** Phase 43 (dogfood; `docs-maintainer` first *editing* use)
- **date:** 2026-09-10
- **project_revision:** 99c415c (+ Phase 43 commit)
- **observation:** `docs-maintainer` was asked to reconcile
  `.claude/skills/codecompass/SKILL.md` and edited it directly. That
  file is **git-tracked but generated** by
  `src/codecompass/skill.py::render_tool_skill` (written by `codecompass
  index`/bootstrap) — a direct edit is overwritten on the next `sync`,
  and the tracked file silently diverges from its generator meanwhile.
  The real fix belonged in `skill.py`. `docs-maintainer`'s brief lists
  the files it "may write" but says nothing about which are generated.
  (The agent *did* flag `.claude/commands/discovery.md` as generated and
  out of scope — so it has some awareness, just not applied
  consistently.)
- **evidence:** `.claude/skills/codecompass/SKILL.md` is in
  `git ls-files` (tracked) and not in `git check-ignore`; its content is
  produced by `render_tool_skill` (`tests/test_skill.py`); no test
  asserts the tracked file matches the generator, so drift is silent.
  The lead reverted the manual edit, fixed `skill.py`, and regenerated.
- **classification:** project-rule (the `docs-maintainer` brief rule —
  **promoted this phase**) + invariant (a `check_user_docs.py` rule that
  tracked generated artifacts match their generator output — tracked for
  Phase 43b as `check_generated_artifacts_match_source`)
- **status:** promoted
- **recurrence:** first occurrence
- **curation (Phase 43 GATE DA triage, 2026-09-10, knowledge-curator):**
  provenance accepted; evidence verified independently —
  `.claude/skills/codecompass/SKILL.md` exists at a checked-in path, its
  frontmatter `description` reads "generated by codecompass", and its
  body is produced by `src/codecompass/skill.py::render_tool_skill`
  (written to disk at `skill.py:129`,
  `(skill_dir / "SKILL.md").write_text(render_tool_skill(configs, project_root), …)`);
  `tests/test_skill.py` exercises `render_tool_skill` but no test asserts
  the tracked file equals the generator output, so drift is silent — the
  claim stands (the Phase 43 retro + `phase-43a` Files section assert the
  file is git-tracked; `git ls-files` not runnable here). **Split per
  GATE DA:**
  1. *project-rule part* — **promoted this phase.**
     `.claude/agents/docs-maintainer.md` "Hard rules" gained
     "**Before editing any file, check whether it is *generated*.**",
     naming `.claude/skills/codecompass/SKILL.md` explicitly and routing
     the fix to the generator (`src/…`, the lead's job). Logged in
     `promoted.md`.
  2. *invariant part* — a `check_generated_artifacts_match_source` rule
     in `check_user_docs.py` is now concrete scope in
     `planning/phase-43b-standing-doc-drift-checks.md` §2 (not a vague
     option). Not `promoted` until Phase 43b lands it + its test.
- **promoted_to:** `.claude/agents/docs-maintainer.md` "Hard rules"
  (generated-file check) @ d34a486 — *lead fills the real short
  hash*. Invariant part: pending Phase 43b.
- **curation (Phase 43b triage, 2026-09-11, knowledge-curator):**
  **invariant half now also promoted.** Verified independently:
  `check_generated_artifacts_match_source` is live in
  `scripts/check_user_docs.py` (L701-764, CHECKS list L781), comparing
  `.claude/skills/codecompass/SKILL.md` against
  `skill.render_tool_skill(...)` and `.claude/commands/discovery.md`
  against `commands.render_discovery_command()` — exactly the two
  artifacts named in `planning/phase-43b-standing-doc-drift-checks.md`
  §2, with the root `CLAUDE.md` routing table and per-vendor
  `codecompass-*` Skills explicitly noted as out of scope (not
  bare-function-reconstructable) rather than silently dropped. 4
  regression tests in
  `tests/test_check_user_docs.py::TestGeneratedArtifactsMatchSource`
  (L429-462), including `test_clean_against_real_repo` (L458) — this
  repo's own tracked `SKILL.md`/`discovery.md` verified to currently
  match their generators, closing the exact silent-drift failure mode
  this candidate recorded (`docs-maintainer` hand-editing
  `SKILL.md` in Phase 43). Both halves of L-005 (project-rule +
  invariant) are now closed; status updated to `promoted` in full.

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
- **status:** promoted
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
- **curation (Phase 43 GATE DA triage, 2026-09-10, knowledge-curator):**
  GATE DA ruled on the L-003 + L-004 cluster. Rather than broadening the
  `docs-reconstructor` drift-audit scope, it scheduled **Phase 43b** — a
  concrete, planned phase (`planning/phase-43b-standing-doc-drift-checks.md`,
  runs before Phase 44) — to add a **`check_no_deleted_names_as_live`**
  rule to `check_user_docs.py`: a hand-maintained list of retired names
  (`grounded_description`, `_RAW_TEXT_CHAR_CAP`, `Depth.FULL`,
  `depth = full`, `codecompass promote`, …) that must not appear as live
  in `README.md` / `docs/` / `architecture/` / `ai-docs/`. That is the
  standing-content complement to the diff-scoped audit and directly
  covers this candidate's `architecture/**` domain. Stays **retained →
  promoted-pending**: promote (with a `promoted.md` line) only once
  Phase 43b actually lands the check. The §C-specific fix remains a
  Phase 61 obligation (or gets pulled into 43b if clean — see the 43b
  plan's judgment call).
- **moves forward when:** Phase 43b implements `check_no_deleted_names_as_live`
  (now a concrete scheduled phase, not a vague GATE DA option) — then log
  the check + its regression test here and in `promoted.md`. Independently,
  Phase 61 landing the §C corrections also moves it forward (log that
  commit too). If Phase 43b slips past the Phase 47 bulk review, force
  promote/discard.
- **curation (Phase 43b triage, 2026-09-11, knowledge-curator):**
  **promoted — both halves closed.** Verified independently:
  (1) `check_no_deleted_names_as_live` is live in
  `scripts/check_user_docs.py` (CHECKS list, L780) and scoped to exactly
  L-004's own domain, `architecture/**` (via `_iter_doc_files`'s `docs`,
  `ai-docs`, `architecture`, `examples` dirs + `README.md`/
  `CONTRIBUTING.md`) — this is squarely inside L-004's original evidence
  location (`architecture/overview.md`), not by analogy the way L-003's
  case is. 5 regression tests in
  `tests/test_check_user_docs.py::TestNoDeletedNamesAsLive` (L387-426),
  including `test_clean_against_real_repo` (L425) and a
  false-positive-shaped `test_does_not_flag_historically_framed_mention`
  (L397) — directly answering this candidate's own evidence shape (a doc
  that "narrates decision history" and must not be flagged for doing so
  correctly). (2) L-004's originally-cited evidence — the 4
  self-contradictory `architecture/overview.md` passages (items 33-36)
  — is fixed, per
  `planning/v1-redefinition/architecture-split-candidates.md` L17-20 and
  L367-369 ("the 4 corrections were resolved in Phase 43b, leaving 32
  still outstanding for Phase 61"), independently re-verified by
  `docs-reconstructor`'s drift audit (`planning/retros/_drift-audit-phase-43b.md`,
  reported NO DRIFT — could not re-run myself, no Bash; trusting the
  retro's and the plan file's own reported result).
- **promoted_to:** `scripts/check_user_docs.py::check_no_deleted_names_as_live`
  + `tests/test_check_user_docs.py::TestNoDeletedNamesAsLive` (the
  general-mechanism half) + `architecture/overview.md` §"Known Footguns"
  / `architecture-split-candidates.md` §C items 33-36 (the
  motivating-evidence half) @ `<commit>` — *lead fills the real short
  hash for the Phase 43b commit*.

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
- **curation (Phase 43 GATE DA triage, 2026-09-10, knowledge-curator):**
  GATE DA did not assign `planning/**` prose an owner or extend the
  drift-audit scope; instead it treated the L-003 + L-004 cluster as
  promotable via **Phase 43b**'s `check_no_deleted_names_as_live` rule
  (`planning/phase-43b-standing-doc-drift-checks.md` §2). Note the scope
  gap: that check as planned targets `README.md` / `docs/` /
  `architecture/` / `ai-docs/`, not `planning/**` prose — so it resolves
  L-004's domain squarely and L-003's only by analogy. Stays **retained
  → promoted-pending**. If a second stale-prose item is caught in
  `planning/**` specifically, that recurrence reopens the
  prose-ownership question separately.
- **moves forward when:** Phase 43b implements `check_no_deleted_names_as_live`
  (now a concrete scheduled phase, not a vague GATE DA option) — log it
  here and in `promoted.md` when it lands, **or** a second stale-prose
  item in `planning/**` is caught incidentally (recurrence → reopen
  prose-ownership). If still unresolved at the Phase 47 bulk review,
  force a promote/discard.
- **curation (Phase 43b triage, 2026-09-11, knowledge-curator):**
  `check_no_deleted_names_as_live` landed — verified directly in
  `scripts/check_user_docs.py::_iter_doc_files` (L333-342): it walks
  `README.md`, `CONTRIBUTING.md`, and `docs/` / `ai-docs/` /
  `architecture/` / `examples/`. **`planning/**` is not in that list.**
  L-003's own evidence (the stale `planning/learnings/README.md` "not yet
  operational" line, Phase 41) was a `planning/**` doc — squarely outside
  this check's scope. Confirms the Phase 43 GATE DA note's own caveat: the
  check "resolves L-004's domain squarely and L-003's only by analogy."
  It does not by analogy either, on inspection — `_RETIRED_NAMES` /
  `_HISTORICAL_MARKERS` matching logic is domain-agnostic, but the
  *file-selection* (`_iter_doc_files`) is the actual scope boundary, and
  it structurally excludes `planning/**`. **Outcome: split, not a clean
  promote.**
  1. The *general pattern half* shared with L-004 (a diff-scoped drift
     check has a standing-content blind spot; GATE DA's remedy shape —
     "a `check_user_docs.py` deleted-names-as-live rule" — is now proven
     workable) is real and now has landed evidence in the `architecture/**`
     instance. Credit that shared insight to **L-004's promotion** (below)
     rather than double-counting here.
  2. L-003's own specific claim — "no independent check on `planning/**`
     narrative-doc accuracy" — **remains true and unresolved.** No
     `planning/**` file is in `_iter_doc_files`'s scope, so nothing
     mechanical watches for a repeat of the exact incident L-003 records.
     **Status stays `retained`**, no longer "promoted-pending Phase 43b"
     (that pending resolution didn't materialize as hoped) — the gap is
     open-ended: extending `_iter_doc_files` to `planning/**` was never in
     scope for any phase and would need its own design (planning docs are
     allowed to describe *retired* things narratively far more than
     product docs are, e.g. superseded ADRs' summaries in roadmap prose —
     a blunt deleted-names-as-live rule over `planning/**` risks far more
     false positives than the product-doc version's own first draft did).
     Not proposing that extension without a second concrete incident to
     calibrate against, per L-003's own "moves forward when" clause.
  3. **Recurrence check:** no second `planning/**` stale-prose incident
     has been caught since Phase 41. The clause "a second stale-prose item
     in `planning/**` is caught incidentally" has not fired.
  4. **Phase 47 bulk-review flag:** L-003 has now been retained across
     Phases 41, 42, and 43b (3 phases) without promotion or discard —
     approaching but not yet past the ~3-phase staleness threshold this
     agent's brief asks it to flag. Note for Phase 47: if still
     unresolved then, force a promote (a scoped `planning/**`
     drift-check design) or discard (accept the gap as a known, bounded
     residual risk given `planning/**` isn't current-truth in the same
     sense product docs are).
- **promoted_to:** — (retained; `planning/**` scope gap still open,
  unrelated to Phase 43b's landed check; flagged for Phase 47 bulk review)

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
- **classification:** workflow (a documented "lead runs the confirming
  check" handoff step) + scoped-rule (the `knowledge-curator` brief
  amendment)
- **status:** promoted
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
- **curation (Phase 43 GATE DA triage, 2026-09-10, knowledge-curator):**
  **promoted.** GATE DA chose the "lead runs the confirming check"
  handoff over read-only Bash — `tools:` can't scope Bash to read-only,
  and the v0.2 file-deletion incident makes unrestricted Bash a real
  risk. Landed this phase:
  - `planning/agent-led-workflow.md` step 12 now requires the curator's
    final message to end with an explicit "lead: run `<command>` to
    confirm" line, and states the lead runs it before accepting the
    triage.
  - `.claude/agents/knowledge-curator.md` "Hard rules" gained the
    matching "**You have no Bash.** … end your report with an explicit
    'lead: run `<command>` to confirm' line" rule.
  This is now the 3rd occurrence (every Stage A triage — Phases 41, 42,
  43); the recurrence trigger below is satisfied. Logged in `promoted.md`.
- **moves forward when:** resolved — promoted this phase.
- **promoted_to:** `planning/agent-led-workflow.md` step 12 +
  `.claude/agents/knowledge-curator.md` "Hard rules" @ d34a486
  — *lead fills the real short hash*.

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
