# Completion audit — Phase 73 (`mentions_artifact` filename-based matching, closes `CG-006`)

**Auditor:** `release-phase-auditor`, independent pass.
**Audited state:** current `main` HEAD at audit time (`9a14753`),
covering Phase 73's own commits `6861250` (plan), `0f3337d` (core fix),
`29ced55` (follow-on fix), `07c8475` (`CG-006` status flip), `38d577c`
(drift audit report + `historical-notes.md` fix).

**Verdict: PASS WITH NON-BLOCKING OBSERVATIONS** (one finding — a
metadata/tracking-field inconsistency, not a functional or user-facing
doc defect).

This is a fresh, independent re-audit dispatched specifically because no
`_audit-phase-73.md` had ever been persisted (`L-060`); Phase 73's actual
`ROADMAP.md`/plan-file `done` flip (`76c441f`) happened before any
`release-phase-auditor` pass ran at all. This report is that pass,
run now against the current tree.

## 1. Plan file re-read and Verification section re-run

Plan: `planning/phase-73-doc-relations-filename-matching.md`.

1. `tests/test_doc_mapping.py` new unit tests — present, pass (see §2).
2. `tests/test_sync.py` new integration test through the real call site
   (`sync.py::rebuild_project_graph`) — present, pass.
3. Existing `mentions_artifact` tests unaffected — pass (full suite run,
   see §2; no regression).
4. `scripts/check_user_docs.py --strict` and `check_knowledge_base.py`
   — re-run now (see §2); no Phase-73-attributable finding.
5. Full `pytest` — re-run now (see §2).
6. `ruff check .` — clean (see §2).
7. `docs-reconstructor` per-phase drift audit — ran
   (`planning/retros/_drift-audit-phase-73.md`), found 1 finding
   (`architecture/historical-notes.md`), fixed in the same phase
   (`38d577c`). Independently re-read the fix: `historical-notes.md`'s
   closing paragraph now correctly describes `_relation_needles`
   (plural) trying name/filename/stem in order — matches
   `relation_enrichment.py`'s actual current code. **Confirmed fixed,
   not merely claimed.**
8. `CG-006` status in `planning/context-gaps/inbox.md` — **not fully
   flipped** (see Finding 1 below).
9. Standard closeout (retro, `knowledge-curator` triage,
   `release-phase-auditor` pass) — retro and triage present; this
   report is the auditor pass.

## 2. Commands re-run against the current working tree

- `pytest -q`: `1 failed, 640 passed, 2 skipped`. The one failure
  (`tests/test_check_user_docs.py::test_no_false_positives_against_real_repo`)
  is **not** a Phase 73 regression — it fails because
  `_audit-phase-71.md`/`_audit-phase-72.md` don't yet exist and
  `planning/CONTEXT.md` still carries stale "pending audit" language,
  both being closed by a separate, parallel dispatch and a lead
  reconciliation pass respectively (per this dispatch's own brief). This
  report's own existence closes the `phase 73` half of that check's
  `done_phases_have_audit_report` finding.
- `ruff check .`: `All checks passed!`
- `python scripts/check_user_docs.py --strict`: 5 findings, all
  attributable to phases 71/72/74 and `CONTEXT.md`'s pending-audit
  language (see above) — **no new finding attributable to Phase 73**.
- `python scripts/check_knowledge_base.py`: no findings.

## 3. `docs/domain/` staleness re-check (independent, against current HEAD)

Phase 73 touched no `docs/domain/` content (confirmed: `git show --stat`
on all five Phase 73 commits shows no `docs/domain/` path). Grepped
`docs/domain/` for `mentions_artifact`, `build_doc_relations_edges`,
`_relation_needle(s)` — the two hits found
(`relationship-edge.md`, `derivation.md`) were already checked by the
Phase 73 drift audit and confirmed not stale (neither describes the
matching *strategy* in a way this phase's widening falsifies). No
staleness found against current HEAD.

## 4. Retro accuracy

`planning/retros/phase-73-doc-relations-filename-matching.md` — commit
list (`6861250`, `0f3337d`, `29ced55`, `07c8475`, `38d577c`) is complete
and accurate; nothing relevant to Phase 73 landed after it. (Phase 73 is
unaffected by the later `da1b56b` fix — that commit is scoped entirely
to `docs/domain/concepts/provenance.md`'s `CL-EVID-008`/`013` citations,
a Phase 74 concern, not cited or implicated anywhere in Phase 73's own
scope.) **No retro update required for Phase 73.**

## 5. `CG-006` tracking accuracy

`planning/learnings/promoted.md` line 52: `CG-006 | 2026-09-27 |
detection-improvement | ... @ 0f3337d` — correct, real commit SHA, not a
placeholder.

**Finding 1 (non-blocking): `CG-006`'s own `- **status:**` field in
`planning/context-gaps/inbox.md` (the entry's own structured field, not
its prose) still literally reads `candidate`**, even though the same
entry's later "Phase 73 closure" narrative note explicitly states
"Status: `candidate` → `promoted-to-roadmap`". This is inconsistent with:

- The plan's own Verification item 8 ("`CG-006`'s own status ...
  flipped to `promoted-to-roadmap`").
- This file's own established convention for a resolved entry — compare
  `CG-008`'s field, which literally reads `- **status:**
  promoted-to-roadmap — fix implemented Phase 62 (2026-09-19).`
  (`CG-002`/`CG-004`/`CG-006`-adjacent entries follow the same pattern).

The prose narrative is correct and complete; only the scannable
structured field was never actually edited. One-line fix:
`planning/context-gaps/inbox.md`'s `CG-006` entry's `- **status:**` line
should read `promoted-to-roadmap — fix implemented Phase 73 (2026-09-27)`
(or equivalent), matching sibling entries.

**Severity assessment:** non-blocking. This is an internal
planning-tracking artifact, not a current-truth doc a user or a fresh
agent would rely on to understand system behavior — the substantive
record (the `promoted.md` line, the narrative closure note, the actual
code fix) is correct and complete. Recorded as a finding because it's a
real, concrete, unambiguous mismatch against the plan's own explicit
verification item, not because it affects DoD substance.

## 6. Protected-file drift / changed-file scope check

`git show --stat` on every Phase 73 commit (`6861250`, `0f3337d`,
`29ced55`, `07c8475`, `38d577c`): no `CLAUDE.md`, no `decisions/*` touched.
Changed files match the plan's "Files created/changed" section exactly:
`src/codecompass/doc_mapping.py`, `src/codecompass/relation_enrichment.py`,
`tests/test_doc_mapping.py`, `tests/test_sync.py`,
`tests/test_relation_enrichment.py`, `architecture/historical-notes.md`
(explicitly conditional in the plan — "only if the consistency check ...
finds a stale description" — and it did), plus standard closeout files
(`planning/ROADMAP.md`, `planning/context-gaps/inbox.md`,
`planning/learnings/promoted.md`, retro, drift audit report). **No scope
creep.**

## 7. Reference-project / context-evaluator applicability

Not applicable — Phase 73 is not a reference-project or
context-evaluation phase.

## Summary

Phase 73's actual deliverable (filename/stem matching in
`build_doc_relations_edges`, the `relation_enrichment.py` follow-on fix)
is real, tested through its production call site, drift-audited clean
(after one fix), and correctly documented. The one gap found — `CG-006`'s
own structured `status:` field left at `candidate` instead of
`promoted-to-roadmap` despite the narrative saying otherwise — is a
real, concrete, easily-fixed inconsistency, but does not misdescribe
system behavior to any user or agent and does not block this phase's
substantive completion.

**Verdict: PASS WITH NON-BLOCKING OBSERVATIONS.**

Required before this note is fully closed out (does not block Phase 73
remaining `done`, but should be fixed at the next convenient commit):

1. `planning/context-gaps/inbox.md`: flip `CG-006`'s own `- **status:**`
   field from `candidate` to `promoted-to-roadmap — fix implemented
   Phase 73 (2026-09-27)`, matching sibling entries' convention.
