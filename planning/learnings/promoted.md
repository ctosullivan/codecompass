# Promoted learnings log

Append-only. One line per promoted candidate. **Pointers, not content** —
the content lives in the artifact named here.

Format: `L-NNN | YYYY-MM-DD | <classification> | <artifact> @ <commit>`

Example: `L-017 | 2026-10-01 | invariant | tests/test_usage.py::test_vendor_dir_excluded @ abc1234`

---

L-001 | 2026-09-10 | invariant | tests/test_check_user_docs.py::TestReadmePhaseCount::test_ignores_done_phases_in_redefined_v1_section + scripts/check_user_docs.py::check_readme_phase_count @ c22d8e4
L-002 | 2026-09-10 | workflow | planning/agent-led-workflow.md step 12 + .claude/agents/knowledge-curator.md "Hard rules" (lead-runs-the-confirming-check handoff) @ d34a486
L-005 | 2026-09-10 | project-rule | .claude/agents/docs-maintainer.md "Hard rules" (check whether a file is generated before editing) @ d34a486
L-004 | 2026-09-11 | future-improvement | scripts/check_user_docs.py::check_no_deleted_names_as_live + tests/test_check_user_docs.py::TestNoDeletedNamesAsLive + architecture/overview.md "Known Footguns" §C corrections (items 33-36) @ 3b7f27a
L-005 | 2026-09-11 | invariant | scripts/check_user_docs.py::check_generated_artifacts_match_source + tests/test_check_user_docs.py::TestGeneratedArtifactsMatchSource @ 3b7f27a
L-006 | 2026-09-10 | workflow | planning/agent-led-workflow.md step 11 + .claude/agents/roadmap-context-curator.md "Hard rules" (re-dispatch after a plan-changing retro; reconcile every planning doc) @ f6cc86d
L-011 | 2026-09-12 | invariant | scripts/check_user_docs.py::check_generated_artifacts_match_source + tests/test_check_user_docs.py::TestGeneratedArtifactsMatchSource::test_skill_comparison_skipped_without_graph_db @ 80162fd
L-013 | 2026-09-12 | workflow | planning/agent-led-workflow.md step 10 (interim reconciliation, no longer flips the row) + step 14 (re-dispatch for final reconciliation) @ 3bd9257
L-018 | 2026-09-13 | workflow | planning/agent-led-workflow.md step 5 (never dispatch two agents to Write the same shared file path concurrently) @ TBD-this-phase-commit

<!-- L-002 and prior L-005 (project-rule half) landed in the Phase 43
     commit; replace `d34a486` if it's not the actual Phase 43 commit hash.
     L-006 landed in `f6cc86d` ("docs(phase-43): GATE DA amendment 4
     (L-006) + planning-doc reconciliation"), the follow-up commit that
     actually wrote the agent-led-workflow.md step 11 / roadmap-context-
     curator.md amendment — not `d34a486` (feat(phase-43), the code
     change + GATE DA verdict itself, which predates the amendment).
     Confirmed via `git show --stat f6cc86d`. -->
