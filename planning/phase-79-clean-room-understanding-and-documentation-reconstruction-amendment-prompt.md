# Phase 79 — amendment initiating prompt (verbatim, second revision)

Saved verbatim, 2026-09-30, per this repository's own established
convention for a saved initiating prompt (a sibling
`planning/phase-N-<name>-prompt.md`/`-amendment-prompt.md` file, matching
`planning/phase-54c-evidence-knowledge-workflow-prompt.md` and this same
phase's own original prompt file). No content below is edited,
summarized, or reformatted beyond this header. See
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction-prompt.md`
for the original initiating prompt this one amends.

---

You are the CodeCompass orchestrator. Assume no knowledge of prior conversations.
Amend the existing Phase 79 — Clean-room conceptual understanding + documentation reconstruction plan, originally committed at `ce7a69e`, and its governing ADR 0066. Work from current repository state:

* https://github.com/ctosullivan/codecompass
* https://github.com/ctosullivan/codecompass-template

Planning only. Do not implement, dispatch research agents or execute the pilot.
The revised objective is: one evidence-backed knowledge foundation supplies both coding context and project documentation, with conceptual understanding incorporated directly into the documentation and mechanical context separation preserved.
Make these amendments consistently throughout the plan, ADR, roadmap/context and related planning notes.

1. Integrate understanding into project documentation.
   * Remove the separate `understanding-review.md` deliverable, human-review gate and review-decisions workflow.
   * Conceptual documentation should explain definitions, relationships, rules, invariants, transformations, examples, counterexamples, assumptions, alternative interpretations and unresolved questions.
   * Include source coverage and traceable evidence references so readers can audit the understanding.
   * Do not require human acceptance before publication or phase completion. Preserve historical review metadata without treating it as a prerequisite. This does not replace the repository's ordinary planning/execution governance.
2. Use one shared knowledge foundation.
   * Reuse existing Observation/Evidence/Claim/Derivation records; do not create a parallel documentation-only assertion store.
   * Keep knowledge sources, conceptual interpretations, project policies and observed implementation behaviour distinct.
   * Generate task-specific coding packets and topic-level documentation from the same revisioned assertions and evidence.
   * Documentation discoveries must update canonical knowledge records before being incorporated into derived outputs.
   * Preserve original-source provenance through derivatives. Documentation prose alone must not become proof of a claim.
3. Fix assertion-schema compatibility.
   * Preserve existing Claim `status` values: `proposed`, `supported`, `contradicted`, `superseded`, `verified`; the original plan's `current/superseded` description is incorrect.
   * Specify optional concept fields and their validation: assertion kind, basis, examples/counterexamples, dependencies, open questions and qualitative evidence-support state.
   * Remove required human-review-state fields.
   * Use immutable knowledge snapshots and stable assertion identities/version references.
   * Changed statements require replacement versions; withdrawn assertions need not invent replacements. Preserve correction history.
   * Include compatible checker changes in implementation scope and require `check_knowledge_base.py --strict`.
4. Require actual mechanical isolation.
   * Curated `.git`-free exports are input packaging, not sufficient access enforcement. Withholding checkout paths and relying on agent-authored logs does not prevent unrestricted tools from reading excluded content.
   * Identify and verify an available sandbox, isolated runtime or restricted tool interface covering filesystem, search, commands and network access. Do not assume a particular mechanism is available.
   * Require preflight denial tests against known excluded material and observable tool activity.
   * Cover researchers, skeptics, documentation architects/writers and documentation-only answering agents.
   * Check indirect leakage through databases, symlinks, caches, import paths, auto-loaded instructions and inherited context.
   * Use fresh contexts, minimal neutral bootstrap instructions and designated output locations.
   * If enforcement is unavailable, label the run best-effort and leave strict clean-room acceptance unmet. Restart contaminated stages.
5. Preserve independent reconstruction and staged writing.
   * Reconstruct conceptual understanding from authorised sources.
   * Independently reconstruct implementation without seeing the conceptual model or legacy narrative.
   * Freeze both outputs before comparison; record aligned, partial, conflicting, not-implemented and insufficiently-verified findings without forcing agreement.
   * A fresh isolated documentation architect selects structure from those artifacts.
   * Preserve the complete initial draft before legacy reconciliation.
   * Publish the reconciled understanding and behaviour into active project documentation.
   * Make this the default ground-up documentation route; missing prerequisites must not silently invoke unrestricted legacy MODE 2.
   * Include `context-researcher` and all affected operational instructions in files-to-change.
6. Complete change propagation.
   * Define a minimal file-based traversal: changed source → evidence → assertions → dependent assertions → snapshots → coding packets/designs/docs.
   * Cover transitive dependencies and snapshot-level citations.
   * Preserve prior snapshots; distinguish "needs reassessment" from "proven incorrect."
   * Demonstrate one explicitly labelled controlled correction or source change propagating into both coding context and documentation. Actual human correction is not required.
7. Revise template delivery and acceptance criteria.
   * Preserve MIT licensing and lightweight, tool-independent guidance.
   * Provide coherent instructions and minimal templates for shared knowledge, snapshots, conceptual documentation, coding-context selection, isolation, implementation comparison, propagation, reconciliation and verification.
   * Remove proposed understanding-review/human-review-decision templates.
   * Require committed template deliverables and a fresh downstream usability exercise.
   * Freeze meaningful documentation/coding-context questions before answering; independently verify results and resolve material incorrect or unsupported claims.

Retain a bounded real-topic pilot, provisionally first-party source/symbol awareness. State that its largely internal intent sources do not validate the richer external-manual case. Describe the output as a complete topic-level pilot, not whole-project redocumentation.
Preserve Phase 78 commitments and avoid expanding into Priority B runtime implementation.
Commit the reconciled planning-only amendments. Report the commit SHA(s), material changes and remaining technical uncertainties. Stop before implementation.
