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
L-018 | 2026-09-13 | workflow | planning/agent-led-workflow.md step 5 (never dispatch two agents to Write the same shared file path concurrently) @ 329fa0a
L-016 | 2026-09-13 | future-improvement | src/codecompass/cli.py::_relations_not_found_error + tests/test_cli.py::test_query_relations_unscanned_file_gets_disambiguated_error @ 780e97b
CG-002 | 2026-09-13 | detection-improvement | src/codecompass/spec_docs.py::_DEFAULT_GLOBS + tests/test_spec_docs.py::test_scan_spec_docs_finds_dev_docs_directory @ 780e97b
L-020 | 2026-09-16 | invariant | planning/reference-projects/ledgerkit/reference-experiment/tests/test_reference_pipeline.py::test_tag_query_manual_excerpt_contains_all_three_inheritance_rules @ a4e58da
CG-004 | 2026-09-17 | detection-improvement | src/codecompass/spec_docs.py::_extract_title + src/codecompass/doc_mapping.py::build_doc_relations_edges (self-mention exclusion) + src/codecompass/sync.py::rebuild_project_graph (spec_doc_rows wiring) + tests/test_sync.py::test_rebuild_project_graph_relates_two_spec_docs_to_each_other @ 51e4469

<!-- L-002 and prior L-005 (project-rule half) landed in the Phase 43
     commit; replace `d34a486` if it's not the actual Phase 43 commit hash.
     L-006 landed in `f6cc86d` ("docs(phase-43): GATE DA amendment 4
     (L-006) + planning-doc reconciliation"), the follow-up commit that
     actually wrote the agent-led-workflow.md step 11 / roadmap-context-
     curator.md amendment — not `d34a486` (feat(phase-43), the code
     change + GATE DA verdict itself, which predates the amendment).
     Confirmed via `git show --stat f6cc86d`. -->
