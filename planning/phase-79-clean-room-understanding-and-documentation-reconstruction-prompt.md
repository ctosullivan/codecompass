# Phase 79 — initiating prompt (verbatim)

Saved verbatim, 2026-09-30, per the prompt's own explicit instruction to
save it "in the appropriate planning/prompts location" — this repository's
existing convention for a saved initiating prompt is a sibling
`planning/phase-N-<name>-prompt.md` file (e.g.
`planning/phase-54c-evidence-knowledge-workflow-prompt.md`), reused here
rather than introducing a new `planning/prompts/` directory. No content
below is edited, summarized, or reformatted beyond this header.

---

You are the CodeCompass orchestrator. Assume no knowledge of prior conversations. Work from the current repositories:

* https://github.com/ctosullivan/codecompass
* https://github.com/ctosullivan/codecompass-template

Plan the next phase to introduce auditable conceptual understanding and clean-room documentation reconstruction in CodeCompass, with a lightweight reusable workflow in the template. Produce and commit the plan first; do not implement until reviewed.

Inspect current roadmap, context, agents, knowledge/provenance mechanisms, decisions and template structure. Select the next available phase number. If a clean-room documentation phase is already planned, amend or consolidate it rather than creating competing workflows. Preserve outstanding Priority A commitments and distinguish this phase's scope from the broader future claims/evidence programme.

Objective

Make the project's current understanding of its subject matter explicit and reviewable by a human, similar to a design document. Then independently reconstruct the implemented system and produce documentation without anchoring on existing narrative.

The intended workflow is:

knowledge sources → explicit understanding → human review → independent implementation reconstruction → documentation architecture → clean-room writing → legacy reconciliation → fresh-agent verification

Introduce this initially through small workflow components and versioned artifacts using existing mechanisms. Do not assume a new graph subsystem, database or comprehensive ontology is necessary.

1. Separate three evidence layers

Maintain explicit distinctions between:

* Knowledge sources: manuals, specifications, reference material, examples and their provenance.
* Project understanding: interpretations, definitions, relationships, rules, assumptions and uncertainties derived from that material.
* Implementation evidence: source, tests, schemas, configuration and observed behaviour.

A domain rule, a product-policy decision and implemented behaviour are different assertions. Human acceptance does not establish objective truth or prove implementation correctness.

2. Produce a concept-understanding model

A fresh reconstruction role should derive the project's current working understanding from authorised knowledge sources.

Begin with a coherent, materially useful topic rather than attempting to model the entire domain. Record coverage and omissions explicitly.

Each material assertion should include:

* stable ID and precise statement;
* kind: definition, relationship, rule, invariant, state/transformation or boundary;
* evidence references with exact locations and source revisions;
* basis: directly stated, inferred, proposed policy or observed behaviour;
* concise justification connecting evidence to interpretation;
* examples and relevant counterexamples;
* dependencies on other assertions;
* uncertainty, conflicting evidence and unresolved questions;
* separate evidence-support and human-review states.

Do not invent numerical confidence scores or conceal conflicting interpretations. Preserve provenance through knowledge-base derivatives to their original sources. Unsupported inherited summaries remain provisional.

3. Generate a human understanding-review document

Create a readable review artifact from the model, containing:

* topic scope and source coverage;
* concepts and relationships in plain language;
* rules, boundaries, exceptions and transformations;
* worked examples that test the interpretation;
* alternative interpretations and unresolved decisions;
* focused questions for the human reviewer;
* an evidence appendix mapping material statements to assertion IDs and sources.

Use diagrams where they clarify relationships, but do not require humans to audit a raw graph.

Record human corrections against assertion IDs, preserving prior versions and the resulting dispositions: accepted, qualified, rejected or superseded.

Publish a reviewed snapshot identifying its scope, source revisions, accepted interpretations and unresolved items. Subsequent designs and documentation should cite the relevant snapshot and assertion IDs.

Do not fabricate human approval. Identify the review gate in the plan. During execution, complete the concrete review packet before requesting review; pending assertions must remain visibly unreviewed.

4. Preserve mechanical context separation

Prompt instructions alone are insufficient. Plan and implement enforceable evidence boundaries appropriate to the available agent tools.

Use isolated exports, restricted workspaces/tool access or equivalent controls. A separate clone/worktree alone is insufficient if the agent can still read the original checkout, Git history or excluded material.

Define distinct scopes:

* Understanding reconstruction: authorised domain sources and traceable derivatives; exclude legacy project explanations and unsupported inherited interpretations.
* Implementation reconstruction: source, tests, schemas, configuration, package metadata, CI/build files and runtime observations; exclude legacy narrative documentation.
* Documentation architecture/writing: reviewed understanding, independently reconstructed implementation evidence and approved documentation structure.
* Legacy reconciliation: old narrative becomes available only after the complete initial draft is preserved.
* Documentation answering: new documentation only.
* Answer verification: repository evidence plus the preserved answers.

Treat ADRs as separately labelled intent/rationale evidence, not proof of current behaviour.

Prevent indirect narrative leakage through agent instructions, planning summaries, cached context, generated indexes, knowledge-base derivatives, inherited conversation history and unrestricted repository/network tools. Allow necessary neutral task instructions through a minimal reviewed bootstrap.

Use fresh agent contexts at boundaries. Keep source comments and docstrings as implementation-adjacent evidence, but verify their claims against behaviour.

Persist permitted-input manifests, source revisions, access controls, observable read/query traces and artifact creation order. Demonstrate that excluded material is inaccessible through the available tools. Record boundary breaches and restart affected stages; do not claim clean-room validation after contamination.

5. Independently reconstruct and compare implementation

Recover the as-built architecture from primary implementation evidence before using the reviewed conceptual model to judge alignment.

Cover modules, APIs/CLI, data and persistence, dependencies, runtime paths, extension points, build/configuration, tests and limitations.

Then compare the independent reconstruction with reviewed understanding. Classify relevant behaviour as aligned, partial, conflicting, not implemented or insufficiently verified.

Do not force the architectural reconstruction to match the accepted conceptual model, or silently revise domain understanding to match existing code.

6. Reconstruct documentation from an empty destination

Design a new information architecture from the reviewed understanding and recovered implementation. Use arc42/C4-inspired architecture views and Diátaxis-style user-documentation categories selectively where useful.

A fresh writer produces a complete first draft without legacy narrative access. Clearly distinguish domain concepts, project policies, supported behaviour and future intentions.

Preserve that draft before a separate reconciler examines legacy docs. Classify historical claims as supported, stale/contradicted, rationale requiring verification, useful examples or obsolete material. Re-ground incorporated claims in evidence; do not restore old structure by default.

Run a fresh documentation-only question exercise. Independently verify the preserved answers against repository evidence, recording correctness, unsupported claims, missing information and ambiguity.

7. Versioning and downstream propagation

Source changes should identify affected assertions and dependent designs/docs for reassessment. They must not silently overwrite reviewed interpretations.

Generate review deltas showing changed evidence, changed understanding, rationale and affected consumers. Distinguish "needs reassessment" from "proven incorrect."

Introduce only the minimal practical dependency tracking justified by this phase.

8. Template delivery

Preserve codecompass-template's MIT licence and lightweight role.

Provide portable instructions and minimal templates for evidence manifests, assertions, understanding review, review decisions, implementation comparison, legacy reconciliation and documentation verification.

Avoid CodeCompass-specific history, agent rosters and governance requirements. Explain how downstream projects establish mechanical isolation, including what to do when their tools cannot enforce it.

Validation and completion

Plan validation on one meaningful CodeCompass knowledge topic and a complete clean-room documentation pass. Confirm the topic and source availability from the repository; do not invent a knowledge base.

Demonstrate:

* traceable conceptual assertions and a usable human review packet;
* enforceable, audited context boundaries;
* independent conceptual and implementation reconstruction;
* a human correction propagating into dependent artifacts when actual review occurs;
* separately labelled test corrections where needed—never presented as human approval;
* reconciliation occurring after the first draft;
* documentation-only answering with independent verification;
* template usability from a fresh downstream perspective.

Keep completion pending where an explicitly required human review has not occurred.

The plan must specify artifacts, role/input boundaries, acceptance criteria, review gates, roadmap placement, migration of existing workflows and changes in both repositories. Save this initiating prompt verbatim in the appropriate planning/prompts location.

Apply normal checks, retrospective, learning triage and independent completion audit during execution.

Stop after committing the planning-only changes. Report commit SHAs, the proposed phase, material decisions and concrete review gates. Do not dispatch implementation agents or begin the reconstruction trial yet.
