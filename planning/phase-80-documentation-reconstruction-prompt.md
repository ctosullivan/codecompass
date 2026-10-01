# Phase 80 initiating prompt (verbatim, 2026-10-02)

Saved per this project's own established convention of preserving a
verbatim initiating prompt. This prompt both corrects two remaining
Phase 79 defects and launches a new phase (numbered 80 at the time of
writing — see `planning/ROADMAP.md` for the actual assigned number)
applying the same documentation process broadly to CodeCompass itself
and, more lightly, to `codecompass-template`.

---

Correct the remaining Phase 79 defects, then apply the documentation process broadly to the real CodeCompass project and its template repository.

Repositories:

* https://github.com/ctosullivan/codecompass
* https://github.com/ctosullivan/codecompass-template — retain MIT licensing

Assume no knowledge of previous conversations or external testing. Inspect current HEADs; the known baseline is CodeCompass 9ce39e0 and template 70f0a12. Read repository instructions and relevant Phase 79 records. Save this prompt verbatim under planning/.

Objective

Produce accurate, understandable current-state documentation from one evidence-backed knowledge foundation. That foundation supplies both project documentation and coding-context packets, avoiding duplicate research.

Understanding belongs directly in active documentation. Do not introduce a separate understanding-review document or human-approval gate. Use the existing workflow and checks; concentrate on documentation quality rather than adding governance machinery.

1. Correct the known defects first

Snapshot validation in scripts/check_knowledge_base.py still accepts historical files with no record identity. Conditions such as if real_id and real_id != expected_id reject mismatches while allowing absent fields.

Independently reproduce this in a disposable Git fixture: point an Assertion slot, then an Evidence slot, at a committed plain file containing no id or kind, using its correct historical hash. Require blocking findings.

Generalize the correction across Assertions, supporting/contradicting Evidence and Derivations. Every entry must have a valid structure, required field types, resolvable historical content, matching historical ID and expected kind. Check missing, empty, malformed and substituted values at each level. Preserve informational handling of legitimate current-record divergence.

The second template exercise's ID-reuse explanation also remains overgeneralized. Inspect:

planning/knowledge/first-party-source-symbols/template-usability-exercise-2/

Against its bundled pre-fix implementation, reproduce:

* Add 1,2,3 → delete 2, then 3 → add: the new ID is 2.
* Add 1,2,3,4 → delete 4, then 1 → add: the new ID is previously used 4.

The correct explanation is that the candidate equals max(current IDs)+1, or 1 for an empty list; reuse depends on whether that candidate was assigned previously. It cannot be determined solely from which task was most recently deleted.

Correct the shared assertion and its derived documentation/packet. Preserve historical artifacts with explicit corrections and use new assertion/snapshot versions where required. Verify short operation sequences against a reference model tracking all previously assigned IDs. Have an independent reviewer actively try to falsify the revised claims.

2. Run broader reconstruction on CodeCompass itself

Record the broader run in the roadmap under the next appropriate phase, with a bounded implementation plan, then proceed without another planning round-trip.

Cover the documentation needed by users, contributors, maintainers and coding agents: purpose, concepts, architecture, installation, configuration, principal workflows, CLI usage, source/dependency context, provenance, limitations and extension points. Select the structure from verified material rather than inheriting existing headings.

Use primary evidence: implementation, tests, schemas, executable behavior, authoritative references and decisions clearly labelled as intent/rationale. Reuse canonical knowledge records after checking their evidence and freshness.

Preserve stage separation:

1. Research and review the shared knowledge foundation; freeze snapshots.
2. Independently reconstruct implementation behavior without the conceptual model or legacy narrative.
3. Compare the two.
4. Produce and commit a complete fresh documentation draft before reading legacy documentation for reconciliation.
5. Reconcile, publish and remove or redirect superseded active pages.

Use fresh dispatches and explicit input boundaries. Record scope manifests, access evidence and achieved isolation. Best-effort separation is permitted; strict isolation remains UNMET unless mechanically demonstrated. Never equate observed compliance with enforced isolation.

3. Apply the process to the template, with lighter documentation

The template needs a concise adoption README, a small architecture/purpose explanation and only the essential workflow guidance. Consolidate overlapping instructions and provide a short worked example where useful.

Keep detailed evidence, drafts and audit records outside the everyday adoption path. Avoid importing CodeCompass's phase history, specialist-agent roster, governance requirements or mandatory heavyweight ceremony.

Identify template files that are primary product artifacts and disclose any necessary access to existing explanatory material. Validate usefulness through a fresh adopter exercise rather than treating those files' own claims as proof.

Check adoption into both a new and an existing project. Preserve project identity, licensing choices and existing instructions. Fix usability defects in the template itself.

4. Verify useful outcomes and close accurately

For each repository, freeze practical reader questions before evaluating the published documentation. Independently check answers against primary evidence and fix factual errors, omissions and ambiguous instructions.

On CodeCompass, also assess a bounded coding-context packet generated from the same foundation. Keep documentation accuracy and coding-context advantage as separate results.

Run relevant tests and existing strict checks. Audit consequential claims, citation traceability, draft-before-reconciliation ordering and stale active documentation. Reconcile roadmap, context, changelog and retros with actual outcomes.

Keep unrelated runtime work, Priority B and Phase 78 unchanged. Finish with commit references, published documentation locations, verification evidence, unresolved limitations and separate workflow-completion and strict-isolation verdicts.
