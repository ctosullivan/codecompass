# Source prompt — Phase 53: Legacy Feature Rationalisation

Verbatim user planning prompt (2026-09-14), saved per its own instruction
("save this prompt to `planning/`... produce and save the Phase 53
plan"). The resulting plan is
`planning/phase-53-legacy-feature-rationalisation-plan.md`. Nothing in
this file has been edited or paraphrased — treat it as the requirements
brief, not as a design or set of conclusions already validated against
the repository. This file exists specifically so the origin and intent
of Phase 53 remain auditable from the repository itself, not only from
chat history.

---

# CodeCompass Phase 53 — Legacy Feature Rationalisation

You are working in the current `CodeCompass` repository.

Implement the next normal CodeCompass development phase:

# Phase 53 — Legacy Feature Rationalisation

This phase should review CodeCompass's accumulated functionality against the architecture that now exists after Phase 52 and determine which features remain:

* **core**
* **adapter/integration**
* **transitional**
* **deprecated**
* **redundant**

The purpose is to simplify CodeCompass before further architectural expansion.

This is **not initially a deletion exercise**.

It is an architectural rationalisation exercise driven by current product direction, actual usage, existing evaluations, and the principle that CodeCompass should increasingly act as an **evidence-backed context system for AI agents**, rather than duplicating reasoning already available from those agents.

Normal CodeCompass phase, planning, implementation, audit, documentation, knowledge-curation and retrospective processes apply.

---

# Required planning artefacts

Before implementation, inspect the repository and produce the normal Phase 53 implementation plan.

Both of the following must be committed under `planning/`:

1. **A copy of this original planning prompt**
2. **The resulting Phase 53 implementation plan**

Follow existing repository naming conventions after inspecting recent phases.

If no stronger current convention exists, use names equivalent to:

```text
planning/phase-53-legacy-feature-rationalisation-prompt.md
planning/phase-53-legacy-feature-rationalisation-plan.md
```

The prompt file should preserve this request sufficiently faithfully that the origin and intent of the phase remain auditable.

Do not rely only on chat history.

The repository itself should contain both:

```text
why Phase 53 was requested
```

and:

```text
how Phase 53 was planned
```

---

# Background

CodeCompass has changed substantially from its original architecture.

Earlier versions placed more emphasis on:

* package/vendor dependency knowledge;
* generated dependency documentation;
* generated Claude Skills containing dependency context;
* initial-chat context generation;
* direct API-key-backed AI enrichment;
* AI prompts embedded inside CodeCompass;
* static context artefacts prepared before an agent knew exactly what it needed.

The project has since evolved toward an agent-driven and empirically evaluated architecture.

By Phase 52, the emerging responsibility boundary is approximately:

```text
CODECOMPASS

deterministic discovery
        ↓
authoritative context graph
        ↓
provenance / evidence
        ↓
task-oriented retrieval
        ↓
enrichment candidate selection
        ↓
validation / persistence
        ↓
context observations / audit
        ↓
evaluation


AI AGENT

task reasoning
enrichment
investigation
context selection
implementation
```

Phase 52 also established an important context lifecycle:

```text
mechanical context
        ↓
agent enrichment
        ↓
agent usage
        ↓
context feedback
        ↓
investigation
        ↓
deterministic improvement
        ↓
mechanical context
```

This means some older features may now duplicate responsibilities handled more naturally by the host coding agent or by newer CodeCompass mechanisms.

Phase 53 should identify and rationalise that duplication.

---

# Core question

For every significant existing feature or subsystem, ask:

> Does this still contribute directly to CodeCompass's current architectural purpose, or does it duplicate context, reasoning, orchestration or interpretation that is now better handled elsewhere?

A useful secondary test is:

> Does this feature establish evidence, preserve provenance, retrieve context, validate context, adapt CodeCompass to an agent environment, or measure whether context helped?

If yes, it is likely still valuable.

If instead it primarily:

* duplicates reasoning already performed by the host agent;
* pre-generates large amounts of context before they are needed;
* maintains a second implementation path to the same result;
* exists mainly because of an earlier architecture;
* increases provider/configuration/maintenance burden without improving the current evidence model;

then it may be transitional or redundant.

---

# Required current-state investigation

Do not begin by assuming the candidates listed below must be removed.

Inspect their current implementation, tests, documentation, callers and role in actual workflows.

At minimum review:

## AI/API enrichment

Inspect:

* direct LLM/API-key enrichment;
* provider/model configuration;
* API credential handling;
* prompt generation;
* parsing;
* automated enrichment application;
* the Phase 52 agent-driven enrichment path;
* candidate selection;
* enrichment validation;
* enrichment persistence.

Determine whether direct API enrichment remains justified now that an existing coding agent can perform the reasoning and submit structured enrichment back through CodeCompass.

Explicitly evaluate whether the preferred long-term boundary should become:

```text
CodeCompass:
candidate selection
validation
persistence

external agent:
reasoning
enrichment
```

rather than CodeCompass acting as an LLM client itself.

Do not remove direct API enrichment without evidence and migration consideration.

---

## Generated Claude Skills

Inspect all project-generated Claude Skills.

Distinguish between:

```text
Skill as context container
```

and:

```text
Skill as thin context-routing protocol
```

Evaluate whether generated Skills should remain but become smaller.

A future Skill may only need to tell the agent:

* CodeCompass is available;
* when it should be consulted;
* how to query it;
* how to inspect evidence;
* how to report missing/misleading context.

Determine whether large generated dependency summaries inside Skills remain useful.

---

## Initial-chat / project entry-point functionality

Review the generated initial-chat or project-orientation mechanisms.

Determine whether the function is still valuable as:

```text
project orientation
+
CodeCompass usage instructions
+
context health/status
+
routing to dynamic discovery
```

while retiring any behaviour that indiscriminately injects large static context bundles.

Do not assume the whole feature is redundant simply because its original implementation may be.

---

## Generated dependency/vendor documentation

Inspect generated dependency documentation and vendor reference material.

Classify separately:

1. artefacts required as grounded evidence or intermediate structured data;
2. artefacts intended primarily for direct AI consumption;
3. human-readable convenience output;
4. duplicated/stale static context.

Determine whether any generated documents remain important to:

* provenance;
* exact-version source grounding;
* graph construction;
* auditability;
* human inspection.

Do not delete evidence merely because it should no longer be injected into an agent's context.

---

## Vendor-centric abstractions

Review where `vendor` remains a foundational architectural concept.

The current direction increasingly involves technical contracts such as:

```text
package
tool/runtime
specification
schema
CLI
external executable
documentation
file format
API
test contract
```

Determine whether vendor-specific abstractions should:

* remain as a valid specialised node/type;
* be generalised;
* be wrapped by broader concepts;
* or be deprecated.

Avoid a large graph-schema redesign unless Phase 53 evidence shows it is required immediately.

This phase may classify future work without implementing all generalisation.

---

## Discovery and query mechanisms

Review:

* `/discovery`;
* generated discovery artefacts;
* graph queries;
* context retrieval commands;
* project entry points.

Identify duplication.

Determine which component should ultimately be the canonical route by which an agent asks:

> What context matters for this task?

Do not remove useful adapters merely to achieve conceptual purity.

---

## Context gaps, observations and learning

Review overlap among:

* `context-gaps/`;
* Phase 52 observations;
* context-use logs;
* context-health;
* candidate-learning lifecycle;
* retrospectives;
* evaluation findings.

Determine whether these represent legitimately distinct stages or historical duplication.

Where possible prefer:

```text
observation
    ↓
investigation
    ↓
learning candidate
    ↓
approved deterministic improvement
```

over several unrelated feedback systems recording essentially the same event.

Any consolidation must preserve existing audit history.

---

## Claude-specific core behaviour

Review whether Claude-specific assumptions exist inside core CodeCompass modules.

Distinguish:

```text
CodeCompass core
```

from:

```text
Claude adapter
Codex adapter
Cursor adapter
AGENTS.md adapter
other future agent adapter
```

Do not remove Claude support.

Instead determine whether current implementation places Claude-specific behaviour at the correct architectural boundary.

---

# Build a complete feature inventory

Phase 53 should produce a feature/subsystem inventory rather than evaluating only obvious candidates.

For each meaningful feature record:

```text
feature
purpose
original rationale
current implementation
current users/callers
current evidence of usefulness
architectural owner
overlap with newer functionality
maintenance burden
classification
recommended action
```

Use the following classifications.

## CORE

Essential to CodeCompass's product architecture.

Examples may include:

* deterministic detection;
* graph construction;
* provenance;
* evidence;
* validation;
* context retrieval;
* context evaluation.

## ADAPTER

Useful integration between CodeCompass and a particular host environment.

Potential examples:

* Claude Skill;
* `CLAUDE.md`;
* Cursor rules;
* `AGENTS.md`.

Adapters should preferably remain thin and should not become alternative knowledge stores.

## TRANSITIONAL

Still required temporarily because users/workflows depend on it, but not part of the intended long-term architecture.

These should have an explicit migration path.

## DEPRECATED

Intentionally retained temporarily but scheduled for removal.

Deprecation should include:

* documentation;
* replacement path;
* compatibility period where appropriate;
* tests for migration behaviour where necessary.

## REDUNDANT

No meaningful remaining responsibility.

Safe removal should still require proof that callers/tests/docs/workflows have been addressed.

---

# Evidence requirements

Do not classify features solely from architectural aesthetics.

Use evidence including:

* current source code;
* tests;
* documentation;
* agent instructions;
* current roadmap;
* context-use logs;
* LedgerKit evaluations;
* Phase 52 findings;
* Git history where useful;
* actual references/callers;
* configuration paths;
* generated artefacts;
* existing user-facing commands.

Where a feature's usefulness is genuinely uncertain, classify it as:

```text
REQUIRES EVALUATION
```

rather than guessing.

Specify the evaluation necessary to decide.

---

# Explicit candidate: API-key enrichment

Give API-key enrichment particular scrutiny.

The current hypothesis is that it may have become redundant because Phase 52 enables:

```text
mechanical edge
    ↓
pending enrichment
    ↓
existing coding agent
    ↓
structured proposal
    ↓
CodeCompass validation
    ↓
stored enrichment
```

instead of:

```text
CodeCompass
    ↓
external LLM API call
    ↓
stored enrichment
```

Benefits of retirement may include removal of:

* API-key management;
* model/provider configuration;
* HTTP behaviour;
* rate limits;
* API costs;
* provider-specific code;
* prompt/API maintenance;
* duplicated enrichment paths.

However, explicitly consider remaining standalone use cases such as:

```text
CI
non-agent CLI usage
scheduled enrichment
batch/offline workflows
```

Do not remove API enrichment merely because agent-driven enrichment is conceptually cleaner.

If evidence remains insufficient, recommend deprecation/evaluation rather than immediate deletion.

---

# Explicit candidate: rich generated Skills

Test the hypothesis that the correct future architecture is:

```text
thin Skill
    ↓
teaches agent how to use CodeCompass
    ↓
agent retrieves task-specific context dynamically
```

rather than:

```text
large generated Skill
    ↓
contains precomputed dependency knowledge
```

Retain useful project bootstrapping.

Avoid unnecessary context-window consumption and staleness.

---

# Explicit candidate: initial-chat functionality

Test whether it should evolve toward a compact project orientation such as:

```text
project identity
current graph/context status
available CodeCompass capabilities
important unresolved context gaps
instructions for task-specific discovery
```

rather than a large context dump.

Treat retirement and redesign as separate possibilities.

---

# Architectural target

Use Phase 53 to test whether CodeCompass should converge toward:

```text
CODECOMPASS CORE
├── deterministic discovery
├── graph / relationships
├── evidence & provenance
├── context retrieval
├── candidate selection
├── validation / persistence
├── context audit / observations
└── evaluation

AGENT
├── reasoning
├── enrichment
├── investigation
└── implementation

ADAPTERS
├── Claude Skill
├── CLAUDE.md
├── AGENTS.md
├── Cursor
└── future agent environments
```

Do not force the repository into this structure if inspection disproves part of it.

The phase exists specifically to test this model against the real implementation.

---

# Plan before implementation

The Phase 53 planning document should include:

## 1. Current-state architecture

Describe current major subsystems and how they interact.

## 2. Feature inventory

Complete classification table.

## 3. Redundancy map

Identify:

* duplicated responsibilities;
* parallel paths;
* obsolete abstractions;
* obsolete configuration;
* generated artefact duplication.

## 4. Proposed target architecture

Show responsibilities after rationalisation.

## 5. Decisions

For every candidate feature identify:

```text
KEEP
KEEP BUT NARROW
GENERALISE
MERGE
DEPRECATE
REMOVE
DEFER PENDING EVALUATION
```

Provide rationale and evidence.

## 6. Compatibility implications

Identify:

* CLI changes;
* configuration changes;
* generated-file changes;
* API changes;
* user migration;
* test migration;
* documentation migration.

## 7. Implementation sequence

Break accepted rationalisation work into bounded steps.

Do not perform unrelated feature development.

## 8. Evaluation requirements

Identify decisions requiring A/B or real-project testing.

## 9. Acceptance criteria

Define exactly when Phase 53 is complete.

---

# Implementation principles

Once the Phase 53 plan has passed the normal review gate, implement the approved rationalisation work.

Prefer deletion and simplification over replacement when functionality truly has no remaining responsibility.

Prefer consolidation over introducing new abstractions.

For example:

```text
BAD

old enrichment path
+
new enrichment path
+
new abstraction wrapping both forever
```

Prefer:

```text
GOOD

identify canonical path
↓
migrate callers
↓
deprecate legacy path
↓
remove when safe
```

Do not keep obsolete architecture merely to avoid touching tests.

Conversely, do not remove stable functionality solely to reduce line count.

---

# Tests

Any implementation changes must preserve the normal CodeCompass testing standards.

Add or update tests covering:

* removed/deprecated CLI behaviour;
* migration paths;
* generated artefact changes;
* thin Skill generation where applicable;
* initial-chat changes where applicable;
* enrichment behaviour;
* config validation;
* removal of API/provider dependencies if applicable;
* graph behaviour;
* context audit behaviour.

The complete suite must pass.

---

# Real-project validation

Use LedgerKit where appropriate.

Particularly valuable comparisons may include:

### Enrichment

```text
API-backed enrichment
vs
Phase-52 agent enrichment
```

Compare:

* correctness;
* usefulness;
* provenance;
* complexity;
* failure modes.

### Skills

```text
no CodeCompass instructions
vs
thin CodeCompass Skill
vs
existing rich generated Skill
```

Compare:

* whether CodeCompass is invoked appropriately;
* relevant context discovery;
* irrelevant context loading;
* task correctness;
* file/tool reads;
* token use where practical.

Do not build a large benchmark infrastructure purely for this phase.

Use the minimum evaluation sufficient to resolve architectural uncertainty.

---

# Documentation requirements

Update documentation so it describes the architecture after rationalisation rather than preserving obsolete concepts.

Check:

* README;
* architecture documentation;
* agent workflow;
* generated artefact documentation;
* command reference;
* configuration documentation;
* ADRs;
* roadmap/current planning context.

Clearly identify deprecated behaviour where applicable.

Do not leave dead features documented as current.

---

# ADR / decision records

Significant architectural retirements or changes should receive normal project decision records where warranted.

Particularly consider documenting decisions such as:

```text
CodeCompass no longer invokes LLM APIs directly
```

or:

```text
generated Skills are routing adapters rather than context stores
```

if Phase 53 actually reaches those conclusions.

Do not create ADRs before the investigation establishes the decision.

---

# Normal agent-led phase process

Follow the current CodeCompass agent-led development workflow.

This includes the normal responsibilities for:

* roadmap/context curation;
* implementation;
* independent testing/evaluation;
* documentation reconciliation;
* documentation drift review;
* knowledge curation;
* context-gap/observation handling;
* release-phase audit.

Do not allow the implementing agent to substitute for independent evaluation or completion audit.

---

# Retrospective

Phase 53 must go through the normal retrospective process.

The retrospective should answer at least:

1. Which features were genuinely redundant?
2. Which features initially appeared redundant but proved valuable?
3. How much architecture/configuration/code was simplified?
4. Were any user-visible capabilities lost?
5. Did rationalisation reduce duplicated responsibility?
6. Did any removal expose unexpected coupling?
7. Did CodeCompass's core product boundary become clearer?
8. What remaining transitional architecture should be revisited later?
9. Did the phase produce evidence for the next roadmap decision?

Store the retrospective using the repository's existing `planning/retros/` conventions.

Normal independent audit requirements apply before the phase is considered complete.

---

# Context observations

Because this phase directly examines how CodeCompass provides context to agents, use the Phase 52 lifecycle during Phase 53 itself.

If the development/evaluation agents find:

* missing context;
* irrelevant context;
* misleading enrichment;
* useful context;
* duplicated context;

record these through the appropriate current mechanism.

Phase 53 should therefore also serve as another real dogfooding exercise for the Phase 52 lifecycle.

Do not silently fix context problems without recording the evidence that revealed them.

---

# Scope exclusions

Do not use this phase to implement:

* broad new relationship types;
* embeddings/vector search;
* hosted infrastructure;
* multi-repository support;
* major MCP work;
* IDE interfaces;
* autonomous graph learning;
* a graph schema rewrite;
* sophisticated context ranking;
* unrelated LedgerKit features.

Those may become future work.

Phase 53 is about **reducing ambiguity and redundancy in what already exists**.

---

# Success criteria

Phase 53 is successful when:

1. The original planning prompt is preserved under `planning/`.
2. The reviewed implementation plan is preserved under `planning/`.
3. Every significant legacy/current subsystem has been inventoried.
4. Each has a documented architectural classification.
5. Redundant functionality has either been safely removed or given an explicit removal path.
6. Transitional functionality has a documented migration strategy.
7. Core functionality has a clearly stated responsibility.
8. Agent-specific functionality is clearly separated from CodeCompass core where appropriate.
9. Duplicate context/enrichment paths are reduced where evidence justifies doing so.
10. Existing users/workflows are protected through deliberate compatibility decisions.
11. Tests pass.
12. Documentation reflects the resulting architecture.
13. Independent audit passes.
14. The normal Phase 53 retrospective is completed.
15. Phase 52's context lifecycle is used during the work and any meaningful context findings are recorded.

---

# Desired outcome

At the end of this phase it should be substantially easier to answer:

> What is CodeCompass itself responsible for?

The ideal answer should resemble:

> **CodeCompass mechanically discovers and preserves evidence-backed project context, makes that context efficiently retrievable by agents, validates non-authoritative enrichment, and measures whether the supplied context was useful. The host agent remains responsible for reasoning.**

Do not assume that wording is correct merely because it appears in this prompt.

Use the Phase 53 review to determine whether the actual repository and evaluation evidence support it.

Begin by inspecting the current repository, current planning state, Phase 52 artefacts, recent retrospectives and relevant ADRs. Then save this prompt to `planning/`, produce and save the Phase 53 plan, and proceed through the normal gated phase lifecycle.
