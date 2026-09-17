You are working in the current CodeCompass repository:

https://github.com/ctosullivan/codecompass

The primary reference project is the current Ledgerkit repository:

https://github.com/ctosullivan/ledgerkit

Your task is to plan the next CodeCompass development phase by synthesising the latest committed evidence from CodeCompass itself and from Ledgerkit’s real use of CodeCompass during development.

This is a planning and evidence-reconciliation session.

Do not begin broad implementation.

Do not rely on previous chat history, summaries, assumptions, or this prompt as evidence for product behaviour.

All material conclusions must be reconstructed from the current repositories and their committed project artifacts.

If repository evidence conflicts with assumptions implicit in this prompt, repository evidence wins.

1. Establish current CodeCompass state

Inspect the current CodeCompass main branch before deciding what the next phase should be.

At minimum inspect:

* CLAUDE.md;
* planning/CONTEXT.md;
* planning/ROADMAP.md;
* current v1-redefinition material;
* the latest completed phase plan;
* the latest phase retro;
* latest audit / closeout artifacts;
* planning/context-gaps/;
* planning/context-observations/;
* planning/learnings/;
* reference-project records;
* Ledgerkit reference-project records specifically;
* current ADRs / decisions;
* current graph schema;
* current relationship/edge model;
* relationship states and usefulness evaluation;
* agent-suggested relationship mechanisms;
* generated Claude entry points;
* /discovery;
* current agent briefs;
* current test/validation state.

Record the exact CodeCompass revision inspected.

Determine from current repository evidence:

1. the latest completed phase;
2. the next unresolved roadmap gate;
3. which observations remain provisional;
4. which findings have recurred;
5. which findings have already been promoted;
6. which ideas remain explicitly deferred;
7. which roadmap items are still conditional;
8. which old assumptions have been superseded by newer experiments.

Do not assume the next phase number before completing this inspection.

2. Reconstruct the latest CodeCompass experiment

Identify the most recent completed CodeCompass phase that tested broader technical/reference context.

Read the complete evidence package, including as applicable:

* phase plan;
* implementation;
* experiment fixtures;
* baseline outputs;
* treatment outputs;
* independent context evaluation;
* retro;
* audit;
* context-gap records;
* context-observation records;
* candidate learnings;
* reference-project findings;
* roadmap consequences.

Reconstruct directly from these artifacts:

* what hypothesis was tested;
* why it was tested;
* what mechanism was introduced or prototyped;
* what existing CodeCompass functionality was reused;
* what worked;
* what failed;
* what remained unsupported;
* whether the graph/schema needed modification;
* whether provenance limitations surfaced;
* whether relationship limitations surfaced;
* whether structured evidence proved more useful than prose/name matching;
* whether context quality materially improved;
* what was deliberately left to the next decision gate.

Do not treat a technically successful prototype as evidence that the capability belongs in v1.

Treat LOW context advantage and negative results as valid evidence.

3. Establish current Ledgerkit state independently

Now inspect the current Ledgerkit main branch.

Do not rely on the Ledgerkit revision previously tested by CodeCompass if Ledgerkit has advanced since then.

At minimum inspect:

* CLAUDE.md;
* CONTEXT.md;
* ROADMAP.md;
* current Stage C state;
* the most recently completed Ledgerkit phase;
* its phase plan;
* amendments to that phase;
* its retro;
* validation/codecompass/;
* current CodeCompass findings;
* compatibility-register entries touched by the phase;
* knowledge/DECISIONS.md;
* knowledge/EDGE_CASES.md;
* query implementation;
* query/report/CLI integration;
* differential-testing evidence;
* current hledger source/reference process;
* current hledger executable/oracle process;
* context-curator specification;
* current agent-development process.

Record the exact Ledgerkit revision inspected.

4. Recover Ledgerkit’s CodeCompass evidence from Ledgerkit itself

From committed Ledgerkit evidence, reconstruct exactly how CodeCompass performed during the real development phase.

Determine:

* what genuine development task CodeCompass was used for;
* what CodeCompass supplied;
* which entry points were used;
* what relationships it exposed;
* what relationships were missing;
* what implementation context the agent still had to locate manually;
* whether any CodeCompass context was incorrect;
* whether anything was stale or misleading;
* how much noise was present;
* what context advantage was recorded;
* what verdict was recorded;
* whether CodeCompass materially influenced the resulting implementation;
* what technical evidence actually proved most important to the phase;
* whether those evidence sources were representable in CodeCompass;
* whether internal project-document relationships were visible;
* whether external executable behaviour was representable;
* what recommendation Ledgerkit made about future CodeCompass use;
* which CodeCompass findings were produced.

Also inspect whether the planned evaluation process was followed.

If an “independent” evaluation was actually performed by the lead session rather than a separate evaluator, record that limitation.

Do not discard the evidence solely because the process was imperfect, but distinguish:

* evidence quality;
* process quality;
* conclusion confidence.

5. Recover the non-CodeCompass lessons from the Ledgerkit phase

The latest Ledgerkit development phase may also have discovered facts about how technical context should be represented.

Inspect the committed evidence for lessons involving:

* source-code understanding;
* documentation;
* compatibility claims;
* executable behaviour;
* differential testing;
* tests;
* ADRs/decisions;
* edge cases;
* intentional divergences;
* previously incorrect project knowledge.

Pay particular attention to cases where:

documentation said one thing
source suggested another thing
executable behaviour revealed something more nuanced

Determine whether CodeCompass currently has a way to represent those evidence layers and their relationships.

Do not use any particular compatibility example from this prompt as assumed evidence.

Recover examples from the repository itself.

6. Compare the two evidence streams

Create a reconciliation matrix.

For every significant pressure point, record:

Finding / pressure point
Evidence from latest CodeCompass phase
Evidence from current Ledgerkit phase
Independent recurrence?
YES / NO / PARTIAL
Impact on real agent work
Existing CodeCompass mechanism
Smallest plausible improvement
Requires graph/schema change?
YES / NO / UNKNOWN
Requires a new evidence/dependency concept?
YES / NO / UNKNOWN
Confidence:
LOW / MODERATE / HIGH
Recommendation:
IMPLEMENT / EXPERIMENT / RETAIN / DEFER / DISCARD

Be strict about independence.

Do not count:

* the same observation copied between repositories;
* a Ledgerkit finding that merely quotes a CodeCompass experiment;
* multiple artifacts from one experiment;

as independent corroboration.

7. Resolve the current CodeCompass roadmap gate

Identify the actual next unresolved roadmap gate from the current CodeCompass repository.

Use the combined evidence package to answer:

What is the smallest CodeCompass generalisation now justified by real project evidence?

Do not assume a broad technical-dependency ontology is required.

Possible outcomes may include:

* no architecture change yet;
* improve project-artifact relationships only;
* support structured evidence/citations;
* add first-class externally pinned references;
* improve provenance representation;
* run an executable/behavioural evidence experiment;
* implement a narrow subset of these;
* collect more evidence before changing architecture.

Recommend only what current evidence supports.

If the gate requires human approval, prepare the recommendation but do not silently resolve it.

8. Evaluate project-artifact relationships

Investigate whether CodeCompass currently handles relationships between project-authored artifacts adequately.

Examples may include:

* research brief → implementation plan;
* plan → implementation;
* ADR → source;
* compatibility record → implementation;
* compatibility record → test;
* edge-case record → regression test;
* retro → follow-up work.

Determine whether real CodeCompass/Ledgerkit evidence shows these links would materially improve future task context.

Prefer mechanical signals where available, including:

* explicit file references;
* IDs;
* structured front matter;
* machine-readable compatibility records;
* documented evidence fields.

Do not jump immediately to embeddings or semantic similarity.

9. Evaluate structured evidence and citations

Inspect whether Ledgerkit already records technical evidence in structured form.

Determine whether CodeCompass could derive high-confidence relationships from fields such as:

source file
line/reference
manual section
test reference
version
commit
executable observation
compatibility ID
decision ID

Assess whether consuming structured citations would provide higher-value, lower-noise relationships than free-text mention detection.

Consider relationship forms conceptually such as:

SUPPORTED_BY
VERIFIED_BY
DOCUMENTED_BY
IMPLEMENTED_BY
CONSTRAINED_BY
EXPLAINED_BY

but do not adopt these names merely because they appear here.

Derive the minimum useful relationship vocabulary from current evidence.

10. Evaluate pinned external references

Inspect the latest CodeCompass experiment’s handling of external material.

Determine whether evidence now supports first-class handling of technical references that are not ordinary package dependencies.

Potential examples include:

* upstream manuals;
* specifications;
* source repositories;
* exact Git commits/tags;
* selected reference documents;
* external technical standards;
* immutable content snapshots.

If justified, define the minimum stable abstraction needed.

Require:

* exact identity;
* version/revision where material;
* source provenance;
* reproducible retrieval;
* content integrity where appropriate;
* clear distinction from project-authored documents.

Do not automatically productise an experimental prototype unchanged.

11. Evaluate executable / behavioural evidence

Explicitly investigate whether current evidence justifies CodeCompass supporting executable behaviour as technical context.

Inspect Ledgerkit’s actual use of its upstream executable reference.

Determine:

* whether executable behaviour materially corrected or supplemented source/document understanding;
* whether it discovered bugs;
* whether it corrected compatibility claims;
* whether future agents would benefit from knowing that an observation came from executable verification;
* whether CodeCompass currently loses this information.

If evidence supports further work, decide whether the next step should be:

* another experiment;
* a narrow representation;
* integration with structured compatibility evidence;
* or deferral.

A possible conceptual chain is:

executable
    ↓
version / revision
    ↓
command + fixture
    ↓
observed behaviour
    ↓
supports / contradicts
    ↓
claim / compatibility record

Do not implement this representation merely because it appears attractive.

First prove the abstraction generalises beyond hledger.

Identify at least several plausible non-hledger use cases, such as:

* compiler behaviour;
* database CLI behaviour;
* protocol tools;
* language runtimes;
* format converters;
* command-line utilities;
* API behaviour under versioned execution.

12. Reassess provenance

Determine whether CodeCompass can currently distinguish sufficiently between:

* local project source;
* local project documentation;
* generated CodeCompass artifacts;
* package/vendor source;
* externally pinned source/reference material;
* agent suggestion;
* structured project claim;
* executable observation;
* test evidence.

If current provenance enums or data structures cannot express an evidenced distinction, propose the minimum extension.

Avoid broad schema churn.

A provenance enhancement should exist because an agent needs to make a different trust decision based on the distinction.

13. Preserve relationship trust states

Any proposed improvement must retain CodeCompass’s existing trust model.

Maintain clear separation between:

* deterministic relationships;
* mechanically derived relationships;
* agent-suggested relationships;
* evaluated/accepted relationships;
* rejected relationships;
* observations;
* authoritative project claims where applicable.

Do not let an LLM-generated relationship silently become equivalent to a mechanically established citation.

Similarly:

A citation is evidence that a relationship is asserted or supported; it does not automatically prove that the underlying claim is correct.

Preserve routes to primary evidence.

14. Reassess Claude entry points

Inspect whether the current generated Claude entry points were useful in Ledgerkit.

Assess separately:

* root routing guidance;
* /discovery;
* generated Skills;
* graph query outputs;
* dependency/source context;
* relationship explanations.

Determine whether their architecture is still appropriate.

The intended direction should remain lightweight:

project entry point
       ↓
task discovery
       ↓
small context map
       ↓
primary evidence

Do not solve weak context by dumping more generated text into CLAUDE.md.

15. Decide what remains out of scope

Reassess, but do not automatically fund:

* embeddings;
* vector search;
* semantic similarity;
* general RAG;
* task-oriented retrieval;
* shared-agent memory/context;
* MCP;
* IDE integration;
* automatic graph mutation by agents;
* universal ontology;
* multi-repository graph;
* hosted service;
* general autonomous-development orchestration.

For each, use:

CURRENT EVIDENCE:
SUPPORTED / NOT SUPPORTED / MIXED
DECISION:
FUND / EXPERIMENT / DEFER / REJECT

16. Define the next validation loop

Any funded CodeCompass improvement must have a real reference-project validation loop.

Prefer a before/after comparison against a previously observed weakness.

For example:

existing Ledgerkit task
        ↓
current CodeCompass baseline
        ↓
CodeCompass improvement
        ↓
same or equivalent task/context query
        ↓
independent context evaluator
        ↓
compare:
accuracy
relevance
completeness
grounding
noise
manual rediscovery
context advantage

Do not measure success primarily through:

* number of nodes;
* number of edges;
* graph density;
* generated documents;
* feature count.

The primary success question is:

Does a fresh development agent receive materially better grounded context than before?

17. Decide whether Ledgerkit remains the next validation target

Do not automatically continue testing on Ledgerkit.

Inspect the current roadmap and decide whether the next validation target should be:

Ledgerkit again

Use this if the proposed improvement directly addresses a well-documented Ledgerkit weakness and creates a useful before/after comparison.

Technical Clipper

Use this if Ledgerkit evidence is sufficiently saturated and a cross-ecosystem generalisation check is now more valuable.

Repository:

https://github.com/ctosullivan/technical-clipper

Another experiment

Use this if a major architectural question still needs isolation before testing on a full project.

No new reference-project work

Use this if v1 consolidation is now more valuable.

Explain the evidence for the choice.

18. Do not overfit to Ledgerkit

For any feature motivated by Ledgerkit, state the general concept separately from the Ledgerkit instance.

For example, prefer:

versioned external executable used as behavioural evidence

over:

hledger executable support

Prefer:

structured evidence relationship between project claim and pinned upstream source

over:

Ledgerkit compatibility YAML support

Before promoting an abstraction into product architecture, identify how it applies to at least one materially different technical domain.

19. Feed findings into the correct CodeCompass knowledge lifecycle

Use existing project mechanisms rather than introducing duplicate stores.

Classify new findings into:

* context gap;
* context observation;
* candidate learning;
* regression requirement;
* roadmap candidate;
* architecture decision;
* implementation task;
* rejected hypothesis.

Promote findings only when evidence meets current project rules.

Examples:

incorrect behaviour
    → regression test
recurring graph limitation
    → roadmap / architecture candidate
one-off observation
    → observation
architectural commitment
    → ADR
repeatable workflow
    → Skill / documented procedure

20. Documentation implications

If the next phase changes CodeCompass’s technical context model, plan corresponding updates to:

* product positioning;
* architecture docs;
* graph model docs;
* provenance documentation;
* relationship-state documentation;
* generated Claude guidance;
* reference-project instructions.

Do not accumulate historical caveats indefinitely.

Follow the current documentation lifecycle and milestone reconstruction policy.

21. Required planning outputs

Produce artifacts consistent with current CodeCompass conventions.

At minimum produce:

A. Current-state reconciliation

Record:

* CodeCompass revision;
* Ledgerkit revision;
* latest CodeCompass completed phase;
* latest Ledgerkit completed phase;
* next CodeCompass gate;
* current roadmap state.

B. Latest CodeCompass phase summary

Explain:

* hypothesis;
* mechanism;
* evidence;
* success/failure;
* unresolved questions.

C. Ledgerkit consumer-evidence summary

Explain:

* genuine task;
* CodeCompass result;
* manual rediscovery;
* context advantage;
* important missing context;
* process limitations;
* resulting findings.

D. Combined evidence matrix

Show corroboration and independence.

E. Gate recommendation

For each candidate improvement classify:

* IMPLEMENT;
* EXPERIMENT;
* RETAIN;
* DEFER;
* DISCARD.

Provide evidence for each.

F. Minimum justified architecture change

If any.

Describe:

* problem;
* evidence;
* smallest solution;
* why a larger solution is unnecessary;
* migration implications;
* trust/provenance implications.

G. Proposed next phase plan

Define:

* objective;
* scope;
* non-goals;
* affected architecture;
* agent roles;
* implementation sequence;
* tests;
* independent evaluation;
* reference-project validation;
* Definition of Done.

H. Roadmap update proposal

Identify:

* phases added;
* phases reordered;
* displaced work;
* deferred work;
* unchanged work;
* human gates.

I. Risks

Explicitly assess:

* overfitting to Ledgerkit;
* premature ontology;
* graph noise;
* stale references;
* source/reference provenance;
* citation ≠ truth;
* schema churn;
* evaluation independence;
* context overhead;
* recreating information an agent could cheaply discover directly.

22. Planning discipline

Use this decision hierarchy:

Is there real evidence of a problem?
        │
       no
        ↓
      defer
       yes
        ↓
Does the problem materially affect agent context?
        │
       no
        ↓
 retain observation
       yes
        ↓
Does the problem recur/generalise?
        │
       no
        ↓
 experiment / collect evidence
       yes
        ↓
What is the smallest deterministic fix?
        ↓
prototype
        ↓
re-evaluate on real task
        ↓
promote only if context improves

Prefer deterministic relationships over inference wherever the project already contains structured evidence.

Prefer structured project knowledge over LLM reconstruction.

Prefer evidence-backed minimalism over ontology design.

23. Human decision gates

Surface rather than silently resolve material decisions involving:

* graph/schema redesign;
* new first-class technical-dependency categories;
* provenance-model changes;
* relationship ontology changes;
* major v1 scope expansion;
* release-boundary change;
* governance changes;
* protected CLAUDE.md modifications.

Prepare recommendations and diffs where appropriate.

Do not implement gated decisions before approval.

Definition of success for this planning session

The session is complete when:

1. current CodeCompass state has been reconstructed from repository evidence;
2. current Ledgerkit state has been reconstructed independently;
3. the latest CodeCompass phase has been fully understood;
4. Ledgerkit’s real consumer-side CodeCompass evidence has been recovered directly;
5. Ledgerkit’s broader technical-context lessons have been examined;
6. duplicate evidence has been separated from independent corroboration;
7. the current roadmap gate has a complete evidence package;
8. project-artifact relationships have been assessed;
9. structured evidence/citation ingestion has been assessed;
10. pinned external-reference support has been assessed;
11. executable/behavioural evidence has been assessed;
12. provenance requirements have been assessed;
13. Claude entry-point usefulness has been reassessed;
14. every major candidate capability is classified as IMPLEMENT / EXPERIMENT / RETAIN / DEFER / DISCARD;
15. the smallest justified next architecture change has been identified—or the evidence explicitly supports no change;
16. the next validation target has been selected based on evidence;
17. roadmap consequences are explicit;
18. human decision gates are explicit;
19. no broad implementation has begun prematurely;
20. the next approved implementation phase could be executed using only the repository and resulting planning artifacts.

The guiding evidence principle is:

Use the repositories as the record of truth. Do not turn remembered discussions into product requirements.

The guiding architecture principle is:

Promote the smallest mechanically grounded capability that repeated real development demonstrates agents actually need.

The guiding CodeCompass principle is:

CodeCompass should earn its place by reducing meaningful discovery work while remaining accurate, version-correct, low-noise and traceable to primary evidence.

The guiding reference-project principle is:

Ledgerkit exposes real context pressure. CodeCompass experiments with general solutions. Independent evaluation determines whether those solutions materially improve agent context. Only then should they become product architecture.
