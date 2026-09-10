# Promoted learnings log

Append-only. One line per promoted candidate. **Pointers, not content** —
the content lives in the artifact named here.

Format: `L-NNN | YYYY-MM-DD | <classification> | <artifact> @ <commit>`

Example: `L-017 | 2026-10-01 | invariant | tests/test_usage.py::test_vendor_dir_excluded @ abc1234`

---

L-001 | 2026-09-10 | invariant | tests/test_check_user_docs.py::TestReadmePhaseCount::test_ignores_done_phases_in_redefined_v1_section + scripts/check_user_docs.py::check_readme_phase_count @ c22d8e4
L-002 | 2026-09-10 | workflow | planning/agent-led-workflow.md step 12 + .claude/agents/knowledge-curator.md "Hard rules" (lead-runs-the-confirming-check handoff) @ feat(phase-43)
L-005 | 2026-09-10 | project-rule | .claude/agents/docs-maintainer.md "Hard rules" (check whether a file is generated before editing) @ feat(phase-43)

<!-- L-002 and L-005 landed in the Phase 43 commit; replace `feat(phase-43)`
     with the real short hash once the lead commits. (check_generated_artifacts_match_source,
     the invariant half of L-005, is Phase 43b — not yet logged.) -->
