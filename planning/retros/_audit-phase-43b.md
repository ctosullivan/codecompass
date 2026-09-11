# Release-phase audit — Phase 43b (two `check_user_docs.py` rules from GATE DA)

**Verdict: PASS WITH NON-BLOCKING OBSERVATIONS**

Audited against `planning/phase-43b-standing-doc-drift-checks.md`,
`CLAUDE.md` §5 (as amended), `agent-led-development.md` §2.8/§6. Working
tree audited (not yet committed), base `fe3c1b8`.

## What I re-ran myself

1. `pytest` → `554 passed, 1 skipped in 146.60s` — matches the phase's
   claim (was 545, +9) exactly.
2. `ruff check .` → `All checks passed!`
3. `python scripts/check_user_docs.py --strict` → `check_user_docs: no
   findings`.
4. Called `check_no_deleted_names_as_live(ROOT)` and
   `check_generated_artifacts_match_source(ROOT)` **directly** (not via
   the aggregate `--strict` exit code) → both return `[]` independently.
   Confirms neither check's clean result is masking a finding the other
   check happens to also produce.
5. **Independent violation-injection spot-check** (not just trusting the
   9 new tests): built a temp fixture with `codecompass promote` in
   live-sounding prose → correctly flagged
   (`no_deleted_names_as_live`, `'codecompass promote' appears with no
   historical marker...`). Built a temp copy of `.claude/` with a
   hand-edit appended to `SKILL.md` → correctly flagged
   (`generated_artifacts_match_source`, `... does not match
   skill.render_tool_skill(...)`). Both checks demonstrably do what they
   claim.
6. **Verified all 4 `architecture/overview.md` fixes against `src/`
   myself**, not the retro/CHANGELOG's characterization:
   - `sync.py::sync_vendor` docstring: "no AI call is ever made from this
     function" — confirms the deleted "grounded description is
     re-purchased on every `sync` run" bullet was false. Correct fix.
   - `enrichment.py`: `_RAW_TEXT_CHAR_CAP = 50_000` (L49),
     `_DOCS_FILE_CAP = 5` (L50), `_ESTIMATED_COST_PER_BATCH_USD = 0.02`
     (L45) all exist exactly as the corrected text states;
     `_ESTIMATED_COST_PER_CALL_USD` does not exist anywhere in the
     source tree. Correct fix (re-attribution + rename, not deletion).
   - `core.py::VendorConfig`: fields are exactly `name: str` and
     `ecosystem: Ecosystem` — no `depth` field. Correct fix.
   - `sync.py`'s copy/clone path: unconditional overwrite, no `depth`
     branch. Correct fix.
7. Confirmed `_iter_doc_files`'s actual scope
   (`scripts/check_user_docs.py:329-330`): `_DOC_DIRS = ("docs",
   "ai-docs", "architecture", "examples")`, `_DOC_ROOT_FILES =
   ("README.md", "CONTRIBUTING.md")` — no `planning/**`. This confirms
   L-003's curation reasoning (that the new check resolves L-004's domain
   but not L-003's) is factually correct, not asserted.
8. `python -m pytest tests/test_check_user_docs.py -q` → `46 passed`
   (matches "14 rules total, 46 tests, +9" claim). `CHECKS` list in
   `scripts/check_user_docs.py` has exactly 14 entries.
9. `git status`/`git diff HEAD -- CLAUDE.md`/`git diff HEAD --
   decisions/` — `CLAUDE.md` unchanged, no `decisions/*` touched.
   Changed-file set: `.claude/skills/docs-sync/SKILL.md`,
   `CHANGELOG.md`, `architecture/overview.md`, `planning/CONTEXT.md`,
   `planning/ROADMAP.md`, `planning/learnings/{inbox,promoted}.md`,
   `planning/phase-43b-*.md`, `planning/v1-redefinition/{roadmap.md,
   architecture-split-candidates.md}`, `scripts/check_user_docs.py`,
   `tests/test_check_user_docs.py`, plus new
   `planning/retros/{phase-43b-*.md,_drift-audit-phase-43b.md}`. Exactly
   matches the plan's Files section + the explicitly-decided-in-plan §C
   fix. **No `src/` change.** No scope creep found.

## DoD conditions checked

- Code implemented, tests added, both new checks independently clean and
  independently correct (spot-checked, not just trusted). **Holds.**
- `architecture/` updated correctly (verified against `src/` directly,
  not just the retro's word). **Holds.**
- `docs/`/`decisions/` — not applicable this phase (plan correctly scoped
  neither as in-scope); confirmed untouched. **Holds.**
- `CHANGELOG.md` — two distinct `[Unreleased]` entries under `Fixed` and
  `Added`, both labeled "Phase 43b" and clearly separated from the
  adjacent "Phase 43" entries — not batched. **Holds.**
- `planning/ROADMAP.md` marks the phase — currently `in progress`
  (correct/expected pending this audit's verdict landing in the closeout
  commit).
- Independent `docs-reconstructor` drift audit exists
  (`planning/retros/_drift-audit-phase-43b.md`), substantive (re-derived
  each fix against `src/` independently, checked for reverse-drift across
  18 grep hits, re-ran the tools itself), verdict **NO DRIFT**. **Holds.**
- Phase retro exists (`planning/retros/phase-43b-standing-doc-drift-checks.md`),
  every TEMPLATE.md section filled substantively, including Where we are
  / What worked / What didn't work / Where we're going. **Holds** (see
  observation below on one section's accuracy).
- Candidate learnings triaged: L-004 → `promoted` (matching `promoted.md`
  line present, `@ <commit>` placeholder — expected pre-commit); L-005's
  invariant half → `promoted` (matching `promoted.md` line present); L-003
  → correctly stays `retained`, reasoning independently verified against
  `_iter_doc_files`'s real scope (see #7 above); L-008 (new) → `retained`,
  present with origin/date/project_revision/observation/evidence/
  classification/status/recurrence/promoted_to fields all filled.
  **Holds for the four learnings named in my task brief.** See observation
  on L-006 below.

## Non-blocking observations (should be corrected in the closeout commit)

1. **Stale claim about the knowledge-curator step's own completion.**
   `planning/CONTEXT.md`, `planning/phase-43b-standing-doc-drift-checks.md`'s
   status line, and `planning/v1-redefinition/roadmap.md`'s Phase 43b
   stanza all currently state that "`knowledge-curator` triage of
   L-003/L-004/L-005's invariant half (workflow step 12) ... [has] not yet
   run." This is factually wrong as submitted: the triage demonstrably
   *did* run — `planning/learnings/inbox.md` and `promoted.md` contain
   substantive, dated (`2026-09-11`) `knowledge-curator` curation entries
   for L-003, L-004, and L-005's invariant half, each independently
   re-verifying evidence against the actual code. Only step 13
   (`release-phase-auditor`, this report) was genuinely outstanding.
   Recommend correcting the wording in all three files as part of the
   closeout commit, rather than leaving an inaccurate record of what
   already happened.
2. **Retro's "Where we're going" section asserts completion ahead of
   this audit.** `planning/retros/phase-43b-standing-doc-drift-checks.md`
   states "Both Stage A→B bridge phases (43b, 43c) are now done" and "No
   gate blocks Phase 44" — written before this audit had run (the same
   retro's header still carries `Auditor verdict: <filled after
   release-phase-auditor>`). Harmless once this PASS lands in the same
   commit, but as submitted it's an assertion made ahead of the event it
   depends on.
3. **L-006 (filed Phase 43, still `status: candidate`) was explicitly
   committed to this phase's triage and wasn't addressed.**
   `planning/CONTEXT.md`'s already-existing (pre-Phase-43b) text — from
   Phase 43c's own closeout — states "L-006 stays scheduled for Phase
   43b's own triage." Phase 43b's actual `knowledge-curator` run
   triaged L-003, L-004, L-005, and filed L-008, but did not touch L-006
   (still `candidate`, no new curation entry). This isn't a violation of
   `CLAUDE.md` §5's literal wording (L-006 is neither "from the phase" nor
   "surfaced by [this] retro"), but it is an unmet forward commitment
   recorded in a DoD-governed doc, silently dropped rather than
   explicitly deferred/rescheduled. Recommend either triaging L-006 now
   (it's a small workflow-amendment confirmation, likely quick) or
   amending `CONTEXT.md` to explicitly reschedule it with a reason,
   rather than leaving the commitment unaddressed and undocumented.
4. Commit-hash / `@ <commit>` placeholders in the retro, `promoted.md`,
   and the plan file are expected pre-commit artifacts, not a gap — flag
   only so the lead remembers to fill them at commit time.

None of these four items reflect a defect in the shipped checks, tests,
or the `architecture/overview.md` corrections — all of that was
independently re-verified above and is correct. They are planning-doc
accuracy/bookkeeping items that should be swept up in the same commit
that records this verdict and flips the phase to `done`.

## Files most relevant to this audit

- `C:\Users\user\Dev\Python\Devcompass\planning\phase-43b-standing-doc-drift-checks.md`
- `C:\Users\user\Dev\Python\Devcompass\scripts\check_user_docs.py`
- `C:\Users\user\Dev\Python\Devcompass\tests\test_check_user_docs.py`
- `C:\Users\user\Dev\Python\Devcompass\architecture\overview.md`
- `C:\Users\user\Dev\Python\Devcompass\planning\v1-redefinition\architecture-split-candidates.md`
- `C:\Users\user\Dev\Python\Devcompass\planning\retros\phase-43b-standing-doc-drift-checks.md`
- `C:\Users\user\Dev\Python\Devcompass\planning\retros\_drift-audit-phase-43b.md`
- `C:\Users\user\Dev\Python\Devcompass\planning\learnings\inbox.md`
- `C:\Users\user\Dev\Python\Devcompass\planning\learnings\promoted.md`
- `C:\Users\user\Dev\Python\Devcompass\planning\CONTEXT.md`
- `C:\Users\user\Dev\Python\Devcompass\planning\ROADMAP.md`
- `C:\Users\user\Dev\Python\Devcompass\planning\v1-redefinition\roadmap.md`
- `C:\Users\user\Dev\Python\Devcompass\CHANGELOG.md`
