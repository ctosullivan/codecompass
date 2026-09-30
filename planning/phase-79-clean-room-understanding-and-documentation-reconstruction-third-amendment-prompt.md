# Phase 79 — third amendment initiating prompt (verbatim, fourth revision, approved to proceed)

Saved verbatim, 2026-10-01, per this repository's own established
convention for a saved initiating prompt (a sibling
`planning/phase-N-<name>-...-prompt.md` file). No content below is
edited, summarized, or reformatted beyond this header. See the three
prior prompt files for this same phase (original, first amendment,
second amendment) for what this one further amends.

---

You are the CodeCompass orchestrator. Assume no knowledge of prior conversations.

Proceed with Phase 79, using the plan at commit 0025dec and ADR 0066, after applying the amendments below. Work from current state in:

* https://github.com/ctosullivan/codecompass
* https://github.com/ctosullivan/codecompass-template

The overall approach is approved subject to these corrections. Amend and commit the plan/ADR first, then implement and validate the amended phase without requesting another planning review.

Preserve the agreed scope: one evidence-backed knowledge foundation supplies coding context and project documentation; conceptual understanding lives directly in documentation; no separate understanding-review artifact or human-acceptance gate; mechanical separation and its demonstrated limits remain explicit.

Required amendments

1. Fix historical snapshot integrity.
    * Comparing snapshot hashes against current canonical records conflicts with legitimate status updates such as supersession or withdrawal.
    * Preserve the actual historical record content, through immutable copies or exact Git revisions, and validate snapshots against that preserved content.
    * Distinguish snapshot corruption from current-record divergence or evidence staleness. Legitimate updates must not invalidate an intact historical snapshot.
    * Preserve the referenced Evidence/Derivation records and original-source locators/revisions needed to reconstruct the supporting evidence—not only Claim hashes.
    * Add meaningful verification that normal supersession preserves historical integrity, historical-content tampering is detected, and current changes trigger reassessment.
2. Make list validation fail closed.
    * The proposed block-list check misses comments, blank lines and valid indentless YAML lists.
    * Validate the supported representation directly: every present list-valued field must use the permitted inline form.
    * Cover those bypasses, malformed values and dangling references. Preserve compatibility with valid existing records.
3. Demonstrate propagation from a changed source.
    * The current fixture changes an assertion, so it does not exercise source-to-evidence discovery.
    * Include relevant source, Evidence/Derivation/Claim records, historical snapshots, a coding packet and documentation in the disposable fixture.
    * Change the fixture's source and demonstrate:
        source → evidence → assertions → transitive dependents → snapshots → both outputs.
    * Include a dependency cycle to verify termination and a snapshot-level citation to verify consumer discovery.
    * Keep synthetic changes outside canonical knowledge and published docs; delete the fixture after preserving the demonstration report.
4. Correct two remaining statements.
    * Remove Phase 78 from prior LOW-advantage precedent: it is still planned and has not been evaluated.
    * Reconcile roadmap/context wording with model-blind implementation reconstruction. That stage must not consume the conceptual snapshot; comparison and writing consume it afterward.

Execution and closeout

Implement the amended workflow, topic-level pilot, checker changes and portable template deliverables. Preserve MIT licensing and Phase 78's scope.

Run appropriate tests for the new validation/versioning behaviour, strict knowledge/documentation checks and normal repository checks. Independently assess both the documentation and a genuine task-specific coding packet drawn from the same snapshot.

Maintain fresh contexts and scoped inputs. Report isolation labels from observed evidence; never claim strict clean-room validation where only best-effort separation was achieved. Keep workflow/template completion and strict isolation validation separately reported.

Complete the normal retrospective, learning triage, drift audit, independent completion audit and roadmap/context reconciliation.

Report commit SHA(s) for both repositories, delivered artifacts, validation results, and any remaining technical limitations. Do not expand into Priority B runtime implementation or whole-project redocumentation.
