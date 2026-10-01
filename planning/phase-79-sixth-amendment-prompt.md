# Phase 79 sixth-amendment prompt (verbatim, 2026-10-01)

Saved per this project's own established convention of preserving a
verbatim initiating prompt for a plan amendment.

---

Amend and complete Phase 79 in these repositories:

* CodeCompass: https://github.com/ctosullivan/codecompass
* MIT template: https://github.com/ctosullivan/codecompass-template

You have no access to the conversation or external testing behind this request. All necessary context is below. Independently reproduce the reported defects and verify your fixes.

Use current HEADs; the known baseline is CodeCompass 1e7d3d5 and template 70f0a12. Read the Phase 79 plan, relevant ADRs, implementation and audit records. Save this prompt verbatim under planning/.

Purpose and boundaries

Phase 79 introduces one evidence-backed knowledge foundation serving both coding-context packets and active project documentation. Conceptual understanding belongs directly in those documents. There is no separate understanding-review document or human-approval gate.

Preserve this sequence: research and adversarial review → frozen knowledge snapshot → independent, model-blind implementation reconstruction → comparison → documentation draft → legacy reconciliation → publication and independent evaluation. Preserve mechanical context separation and report isolation actually achieved. Strict isolation remains UNMET wherever boundaries are only best-effort.

The existing pilot is under planning/knowledge/first-party-source-symbols/. Amend the existing plan and implement these corrections directly:

1. Close nested snapshot-validation gaps.
    Inspect scripts/check_knowledge_base.py, particularly check_snapshot_completeness and _iter_snapshot_entries. Nested keys can currently count as captured evidence even when their values are malformed or identify the wrong historical record.
    Build a disposable Git fixture containing committed Claims, Evidence and Derivation records plus a complete snapshot with correct historical hashes. Verify the baseline passes, then independently test:
    * Replace a required nested Evidence table with a scalar string.
    * Keep the key EV-TEST-001, but point its entry to EV-TEST-002 and supply that second record's correct hash.
    * Repeat equivalent malformed-entry and identity-substitution cases for Derivations.
    Require actionable blocking findings for these cases. Validate every nested entry's structure, required field types, historical ID and record kind against its pinned Git content. Preserve passing behavior for complete snapshots and legitimate current supersession or withdrawal. Add regression tests using real disposable Git repositories.
2. Correct the downstream exercise's false conceptual claim.
    Inspect template-usability-exercise/tinytodo-after-adoption/ beneath the pilot directory. Its assertion and docs/task-ids.md claim IDs cannot be reused while another task remains. The implementation computes max(current IDs) + 1.
    Reproduce this sequence in an isolated temporary store:
    add tasks 1 and 2 → delete task 2 → add another task.
    Check whether the new task receives ID 2 while task 1 remains.
    Record the result as evidence and correct the assertion, documentation and exercise conclusions. Distinguish intended guarantees from implemented behavior. Independently verify representative deletion cases, including deleting the highest ID and emptying the store. Preserve the original exercise as historical evidence with clearly identified corrections.
3. Complete the template workflow exercise.
    The current exercise prohibited commits, leaving the snapshot UNCOMMITTED; several downstream templates were inspected rather than exercised.
    Run a fresh, bounded non-CodeCompass exercise in a disposable Git repository permitting local commits. Give fresh dispatches only their permitted inputs. Produce a valid frozen snapshot, model-blind implementation reconstruction, comparison, conceptual documentation and task-specific coding-context packet. Independently assess both outputs and demonstrate source-change propagation to both through the shared foundation.
    Preserve inputs, outputs, scope/access evidence, findings and reproducible fixture history or setup. Fix discovered template usability defects. Report achieved isolation honestly per scope.

Run relevant tests, both strict knowledge/documentation checks and an independent completion re-audit. Reconcile the plan, roadmap, context, retro and changelog with verified outcomes; report any remaining unmet requirements explicitly.

Keep Phase 78 unchanged, preserve the template's MIT licence and lightweight adoption model, and avoid runtime or Priority B expansion. Finish with commit references, verification results and separate workflow-completion and strict-isolation verdicts.
