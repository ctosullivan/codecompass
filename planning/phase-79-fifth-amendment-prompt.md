# Phase 79 fifth-amendment prompt (verbatim, 2026-10-01)

Saved per this project's own established convention of preserving a
verbatim initiating prompt for a plan amendment.

---

Amend and complete Phase 79 in these repositories:

* CodeCompass: https://github.com/ctosullivan/codecompass
* MIT template: https://github.com/ctosullivan/codecompass-template

The implementation review covered CodeCompass 1ca49a3 and template 8868ba9. Inspect current HEADs before editing. Save this prompt verbatim under planning/.

Preserve the approved objective: one evidence-backed knowledge foundation supplies coding-context packets and project documentation. Conceptual understanding belongs directly in active documentation, with no separate understanding-review document or human-approval gate. Preserve model-blind implementation reconstruction, draft-before-legacy-reconciliation ordering and mechanical context separation.

Amend the existing plan and implement the following corrections without another planning round-trip:

1. Make snapshot validation fail closed.
    scripts/check_knowledge_base.py currently validates only entries present in a snapshot. A sidecar reduced to only snapshot_id returns no findings; missing Evidence/Derivation tables are not checked against historical Claims.
    Validate required metadata, table types, assertion inventory, record identity and the complete Evidence/Derivation closure required by the snapshot schema. Detect incomplete or truncated snapshots rather than accepting the remaining hashes. Invalid structures must produce actionable findings, not exceptions.
    Continue hashing historical Git content. Legitimate current supersession or withdrawal must preserve historical integrity and produce only informational divergence.
    Add meaningful disposable-Git-fixture tests for incomplete snapshots, omitted closure entries, malformed structures, tampering and legitimate lifecycle changes.
2. Restore citations in published documentation.
    The first-party source explanations in architecture/overview.md and architecture/context-graph-schema.md lack links to their frozen knowledge foundation.
    Add concise snapshot/assertion references using first-party-source-symbols@v2#<assertion-id>, with navigable links or a section-level reference mapping. Cover both incorporated concepts and newly documented limitations. Verify that each reference resolves to the correct snapshot membership and historical supporting records. Keep understanding within these active pages.
3. Correct isolation evidence and closeout reporting.
    The audit reports "strict clean-room isolation: PASS" despite achieving only best-effort. The persisted preflight is an agent handback, and required per-scope manifests, raw transcripts, access logs and boundary checks are absent.
    Inventory available evidence. Never fabricate historical transcripts or present a later rerun as evidence of the original execution. Perform fresh scoped checks where feasible, preserve their actual evidence and distinguish them from the original pilot.
    Report workflow completion separately from isolation achieved. Strict isolation remains UNMET wherever boundaries were not mechanically enforced; honest labelling alone does not constitute strict-isolation success.
4. Demonstrate downstream template usability.
    A fresh-clone link check does not satisfy the planned exercise. Dispatch a fresh agent given only the updated template and a small invented non-CodeCompass project. Have it attempt the workflow, record completed steps and blockers, and fix discovered usability defects. Preserve the exercise report. Keep the template lightweight, independently usable and MIT-licensed.

Run relevant tests and both strict knowledge/documentation checks, obtain an independent completion re-audit, then reconcile the plan, roadmap, context, retro and changelog with the actual results. Keep Phase 78 unchanged and avoid Priority B or runtime expansion.

Finish with commit references, validation results, unresolved limitations and separate workflow-completion and strict-isolation verdicts.
