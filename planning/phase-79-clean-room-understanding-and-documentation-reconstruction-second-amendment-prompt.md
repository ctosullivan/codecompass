# Phase 79 — second amendment initiating prompt (verbatim, third revision)

Saved verbatim, 2026-09-30, per this repository's own established
convention for a saved initiating prompt (a sibling
`planning/phase-N-<name>-...-prompt.md` file). No content below is
edited, summarized, or reformatted beyond this header. See
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction-prompt.md`
(original) and
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction-amendment-prompt.md`
(first amendment) for the prompts this one further amends.

---

You are the CodeCompass orchestrator. Assume no knowledge of prior conversations.

Amend the Phase 79 — Clean-room conceptual understanding + documentation reconstruction plan at commit 8965490, its governing ADR 0066, and affected roadmap/context/planning notes. Work from current ctosullivan/codecompass and ctosullivan/codecompass-template state.

Planning only. Do not implement, dispatch trial agents or execute validation.

Preserve the revised objective: one shared evidence-backed knowledge foundation supplies coding context and project documentation; conceptual understanding is incorporated directly into active documentation; no separate understanding-review artifact or human-acceptance gate is introduced.

Correct the following:

1. Strengthen isolation verification and reconcile completion criteria.
    * A failed read of one absolute path, reported by an agent, is insufficient to verify isolation.
    * Define observed preflight checks covering available filesystem, search, command, network and delegation routes, plus transferred content and inherited context.
    * Omitting network-specific tools does not restrict networking through Bash; address that bypass explicitly.
    * Tier 2 remains best-effort regardless of an incidental failed read.
    * Verify restrictions in the environment actually used; do not assume remote isolation or another mechanism is available.
    * Distinguish completed workflow/template deliverables from successful strict clean-room validation. If enforcement cannot be demonstrated, report partial completion and leave that validation unmet. Removing the human-review gate must not relax the technical isolation requirement.
2. Remove the circular publication dependency.
    * Comparison currently requires published understanding documentation, writing requires comparison, and publication follows writing.
    * Replace this with:
        canonical assertions → frozen knowledge snapshot → independent implementation reconstruction → comparison → documentation architecture/draft → legacy reconciliation → publication.
    * Comparison and initial writing consume the snapshot, not previously published conceptual prose.
    * Keep understanding in the final project documentation. The snapshot is an evidence/version artifact, not a separate review document or approval gate.
    * Preserve the first complete draft before exposing legacy narrative.
3. Specify concrete snapshots and complete source-change propagation.
    * Define the CodeCompass snapshot artifact, creation procedure, citation format and integrity validation. Include exact assertion/evidence versions, source revisions and relevant record state.
    * Ensure later record mutations cannot alter what an earlier snapshot represented.
    * Operationally cover:
        changed source → affected evidence → assertions → transitive dependencies → snapshots → coding packets/designs/documentation.
    * Define how source-to-evidence/assertion links are found, rather than starting from an assertion already identified manually.
    * Preserve "needs reassessment" versus "proven incorrect."
    * Run synthetic correction demonstrations in disposable fixtures, or specify complete restoration. Do not leave synthetic contradictions in canonical knowledge or published documentation.
4. Fix dependency validation.
    * The current checker detects dangling IDs in inline depends_on: [ID], but misses ordinary YAML block lists because it does not reconstruct multiline field values.
    * Either enforce/document a supported inline representation or extend parsing and validation.
    * Include meaningful checks for dangling dependencies and safe traversal of dependency cycles.
    * Remove the claim that all dependency representations already validate with zero code change. Keep strict validation and backward compatibility.
5. Separate alignment from verification.
    * An aligned classification must not automatically promote a Claim to verified.
    * Require claim-specific independent checking against primary evidence and record what was verified.
    * Implementation agreement cannot establish the validity of a domain rule or proposed policy.
    * Preserve alignment as a comparison finding and retain appropriate uncertainty/support states.
6. Validate coding context as well as documentation.
    * Freeze meaningful coding-context questions before evaluating a genuine, bounded task-specific packet generated from the same snapshot as the documentation.
    * Independently assess accuracy, sufficiency and explicit uncertainties against primary evidence.
    * Demonstrate more than shared citations or reassessment flags: the shared knowledge must supply useful task context, and a controlled change must reach both outputs.

Reconcile all affected sections, ADR statements, schemas, scope tables, files-to-change, template guidance and Definition of Done. Preserve MIT licensing, the bounded topic-level pilot, Phase 78 commitments and the separation from Priority B runtime implementation.

Commit the planning-only amendments. Report commit SHA(s), material corrections and remaining technical uncertainties. Stop before implementation.
