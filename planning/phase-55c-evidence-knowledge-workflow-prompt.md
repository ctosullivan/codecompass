# Verbatim governing prompt — evidence-backed, knowledge-based, documentation-first workflow

Saved exactly as given, per this project's established practice of never
paraphrasing a governing prompt.

---

Plan the next CodeCompass phase to introduce an evidence-backed, knowledge-based, documentation-first development workflow for both CodeCompass itself and downstream projects such as Ledgerkit.

The goal is not to build a large universal ontology or redesign the whole graph immediately. The phase should introduce the smallest useful architecture that allows CodeCompass to distinguish mechanically observed facts, behavioural evidence, inferred claims, user-approved decisions, and derived knowledge while preserving provenance.

The intended development workflow is:

Roadmap goal
→ Context Researcher
→ Evidence-backed knowledge map
→ Documentation Agent
→ User-facing design document
→ User review/testing/correction
→ Knowledge base updated
→ Approved implementation context packet
→ Coding Agent
→ Normal implementation/test/review process
→ Behavioural revalidation
→ Knowledge/documentation refresh
→ Retro

Use a narrowly scoped real feature as the proving case where practical, such as depth behaviour in Ledgerkit/hledger or an equivalent bounded CodeCompass feature.

1. Evidence and knowledge model

Design a minimal first-class model around at least:

* Observation
* Evidence
* Claim
* Derivation
* Decision
* Requirement

Keep deterministic structural graph relationships intact. Do not replace the existing graph unnecessarily.

The architecture should distinguish approximately:

* deterministic structural facts, such as symbols, imports, calls and dependencies;
* experimentally observed behaviour;
* documentation/source/test evidence;
* agent-derived interpretations or claims;
* user/project-owner decisions;
* implementation requirements.

An agent-derived claim must not silently become a fact. Claims should retain their supporting and contradicting evidence and the derivation process that produced them.

Provenance should capture only the fields demonstrated to be useful by the experiment, but should consider items such as:

* source/artifact;
* repository revision or commit;
* location/symbol;
* method of observation;
* tool/adapter used;
* timestamp where relevant;
* agent/process responsible for derivation;
* parent evidence/claims;
* status such as proposed, supported, contradicted, superseded or verified.

Preserve historical derivation rather than destructively overwriting previous claims.

2. Behaviour-first Context Researcher

Define or evolve the Context Researcher so that feature research begins with observable behaviour where executable behaviour exists.

For a feature such as depth, the researcher should:

* identify the intended development goal from the roadmap;
* establish actual executable behaviour with representative examples and edge cases;
* record exact inputs, outputs, environment/version/commit and results;
* convert observations into evidence-backed records;
* trace the implementation paths that explain the observed behaviour;
* trace relevant tests, documentation, dependencies and historical information;
* identify contradictions, ambiguities and knowledge gaps;
* perform additional targeted experiments when source inspection reveals new questions;
* build an evidence-backed concept/knowledge map rather than merely returning relevant files.

Research should be iterative:

observe ↔ trace ↔ test ↔ refine

Existing documentation should be treated as evidence rather than unquestioned ground truth.

3. Documentation-first phase gate

Introduce a Documentation Agent that consumes the research/knowledge model before implementation begins.

Its main output should be a user-facing design document that explains CodeCompass's current understanding of the feature in ordinary language.

The design document should include, where relevant:

* feature purpose and concepts;
* observed current/upstream behaviour;
* syntax/API forms;
* behavioural rules and precedence;
* important interactions and dependencies;
* architecture/implementation concepts;
* examples;
* edge cases;
* known uncertainties;
* contradictions between behaviour, source, tests or documentation;
* proposed behaviour for the target project;
* intentional differences from upstream behaviour;
* non-goals;
* acceptance criteria.

Where possible, statements should be written as testable examples such as Given / When / Then cases or executable commands.

The design document is a human-readable projection of the knowledge base, not an independent source of truth.

4. User review and knowledge correction

Introduce an explicit review gate before substantial implementation.

Suggested lifecycle:

DRAFT
→ RESEARCHED
→ USER REVIEW
→ APPROVED
→ IMPLEMENTING
→ VERIFIED

The user/project owner should be able to:

* test examples;
* challenge the researcher's interpretation;
* correct misunderstood behaviour;
* choose between alternative semantics;
* identify desired deviations from upstream behaviour;
* add constraints or non-goals.

User corrections should update structured knowledge wherever practical rather than existing only as edits to Markdown.

Record significant decisions explicitly, including rationale and what previous proposal/claim they supersede.

It must remain possible to distinguish:

Observed upstream behaviour
≠ interpreted behaviour
≠ desired target-project behaviour
≠ implementation decision

This distinction is particularly important for Ledgerkit, which interoperates with the hledger ecosystem without necessarily needing to reproduce every implementation detail.

5. Approved context packet for coding agents

Once the design is approved, have the Context Curator produce a deliberately compact implementation packet for the coding agent.

It should contain only implementation-relevant material such as:

* goal;
* approved semantics;
* requirements;
* behavioural examples;
* invariants;
* relevant architecture;
* relevant symbols/files/dependencies;
* existing tests;
* non-goals;
* deliberate upstream differences;
* unresolved questions, if any;
* provenance references back to the evidence/knowledge graph.

The coding agent should not need to independently rediscover the entire feature before implementation.

The context packet should remain traceable back to the knowledge/evidence model.

6. Implementation and verification loop

After implementation:

* run normal development, testing and review processes;
* rerun the behavioural examples/experiments that established the initial understanding;
* compare approved expected behaviour with actual implemented behaviour;
* identify whether discrepancies represent implementation bugs, incorrect design assumptions, or incomplete upstream understanding;
* update claims, evidence, requirements and documentation accordingly;
* preserve provenance showing how understanding evolved.

Where practical, make documentation examples executable or derived from executable fixtures so stale examples can be detected automatically.

Longer-term, aim for relationships such as:

Requirement
→ documented by design section
→ demonstrated by example
→ tested by test
→ implemented by symbol/change
→ verified by behaviour

Do not over-engineer this traceability in the first phase; establish the smallest useful form first.

7. Architecture constraints

Preserve compatibility with the broader CodeCompass direction:

* language adapters should eventually emit observations/evidence rather than directly asserting semantic truth;
* the evidence/knowledge layer should be language-neutral;
* future Python, Haskell, SQL/data and enterprise/mainframe adapters should be able to contribute evidence using the same contract;
* the design should not assume MCP is required;
* MCP may later expose mature CodeCompass operations such as querying claims, evidence, derivations and context packets, but should not drive the underlying knowledge model.

Avoid premature work on:

* a universal ontology;
* RDF/OWL unless justified by actual requirements;
* complex probabilistic confidence systems;
* automatic conflict resolution;
* distributed graph architecture;
* generic enterprise knowledge ingestion;
* MCP-specific architecture;
* wholesale replacement of the current graph.

8. Dogfooding

The workflow should be usable both:

1. to develop CodeCompass itself; and
2. to develop downstream projects such as Ledgerkit.

CodeCompass should increasingly be developed using the same evidence-backed workflow that it intends to provide to other coding agents.

Ledgerkit/hledger should remain an important external proving ground because it allows CodeCompass to demonstrate whether it can reconstruct and safely modify behaviour in a mature external system.

9. Phase experiment and success criteria

Design the phase as a bounded experiment rather than assuming the final architecture in advance.

Use the experiment to answer:

* What forms of evidence were actually useful?
* Which provenance fields were necessary?
* Can another agent explain why an important claim is believed?
* Can claims be traced back to primary evidence?
* Can contradictory evidence be retained without silently resolving it?
* Can user corrections update the knowledge model cleanly?
* Does the design-document review catch misunderstandings before implementation?
* Is the resulting coding-agent context smaller and more actionable than raw repository context?
* Can implementation results update the knowledge model without losing historical provenance?
* Does this improve development quality enough to justify making the model permanent?

The phase retrospective should explicitly recommend which parts become durable CodeCompass architecture and which should remain experimental.

10. Planning requirements

Prepare a concrete implementation plan for this phase.

Follow the project's normal phase, planning, validation and retrospective conventions.

The plan should:

* inspect the current CodeCompass architecture first;
* reuse existing graph, enrichment, evidence and agent-loop mechanisms wherever sensible;
* identify which current components need extension rather than replacement;
* identify migrations/backwards-compatibility concerns;
* define the minimal data model;
* define researcher/documentation/curator responsibilities and boundaries;
* define the user review gate;
* define the context-packet contract;
* select a bounded proving feature;
* specify tests and success/failure criteria;
* keep the implementation incremental and reversible;
* save the planning prompt and resulting plan in the normal planning location;
* update the roadmap so the evidence/knowledge/documentation-first model is incorporated into subsequent Haskell-adapter and downstream Ledgerkit work if the experiment succeeds.

Do not begin implementation during this planning task.

The plan should favour empirical discovery over speculative architecture: introduce enough structure to preserve the knowledge generated by current behavioural experiments, then allow the evidence from those experiments to determine the mature model.
