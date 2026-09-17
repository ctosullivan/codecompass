# Verbatim governing prompt — Phase 54b behavioural-understanding expansion

Saved exactly as given, per this project's own established practice of
never paraphrasing a governing prompt (a prior session caught and fixed
exactly this mistake during the Phase 55 evidence-reconciliation
planning session — see that phase's own prompt file's history).

---

Review the current CodeCompass roadmap and plan an update that incorporates the behavioural-understanding lessons from Ledgerkit Stage C Phase 5, particularly the depth: compatibility investigation.

The roadmap should retain its current evidence-first sequencing and Haskell-first direction, but refine the next relevant phases as follows:

* Expand Phase 54b so the Ledgerkit LK-COMPAT-QUERY-DEPTH-001 case becomes a concrete behavioural-understanding experiment, not just a provenance/reference-ingestion test.
* Test whether CodeCompass helps an agent reconstruct observable behaviour across all relevant execution paths and entry points, including command-specific exceptions such as the differing depth: behaviour across balance, register, accounts, stats, and print.
* Evaluate whether structured CodeCompass context prevents premature conclusions based on locally plausible source evidence.
* Capture behavioural claims with evidence such as documentation, implementation paths, observed executable behaviour, Ledgerkit implementation, and independent verification where available.
* Add an explicit experiment criterion for execution-path completeness: did the agent identify and inspect all materially relevant behavioural entry points before reaching a conclusion?
* Use the existing agent-suggested edge, context-gap, observation, review, and audit mechanisms wherever possible. Do not introduce a new behaviour ontology, claim system, execution graph, or large set of relationship types during Phase 54b unless strictly required for the experiment.
* Treat shortcomings discovered during the experiment as evidence to inform GATE DD. Repeated, independently supported representation gaps should determine whether Phase 57 needs first-class provenance, behavioural, or technical-dependency abstractions.
* Carry the findings forward into Phase 60 Haskell adapter requirements, particularly the ability to expose enough structural information for agents to trace behaviour from entry points through implementation.
* Refine Phase 61 so the hledger/Ledgerkit cross-language experiment tests whether CodeCompass can reconstruct and compare a real behavioural concept across Haskell and Python, using the existing depth: case or another suitably evidenced Ledgerkit compatibility question.
* Preserve the principle that new abstractions must be justified by experiment evidence rather than designed speculatively.

The broader hypothesis to reflect in the roadmap is:

CodeCompass should help agents build an evidence-backed understanding of how observable system behaviour emerges from code, documentation, tests, configuration, and execution paths — not merely map source-code dependencies.

Update the roadmap only where justified by this learning. Preserve existing phase numbering and sequencing unless there is a strong architectural reason to change them. Clearly distinguish changes to immediate phase scope from hypotheses that should remain deferred until GATE DD.

Prepare the normal phase-planning artefacts and save the updated plan/planning prompt in the appropriate planning directory, following the existing CodeCompass planning and retrospective processes.
