# Source prompt — Context Edge Lifecycle and Audit Loop

Verbatim user planning prompt (2026-09-14), saved per its own final
instruction ("Save plan and this prompt to planning folder"). The
resulting plan is `planning/context-edge-lifecycle-plan.md`. Nothing in
this file has been edited or paraphrased — treat it as the requirements
brief, not as a design that's already been validated against the
repository.

---

CodeCompass Planning Prompt — Context Edge Lifecycle and Audit Loop

You are working on the current CodeCompass repository.

Your task is to plan the next development phase only. Do not begin implementation until the plan has been reviewed.

## Background

CodeCompass has evolved into an agent-driven, evaluated context system. Its purpose is not merely to generate documentation or a repository graph, but to help AI agents discover accurate, relevant project context while preserving a strong distinction between:

1. mechanically established facts;
2. AI-generated interpretation/enrichment;
3. agent observations and requests;
4. evaluation of whether context was useful.

The current project already contains several related mechanisms, including deterministic graph construction, relationship enrichment, context-gap recording, context-use/evaluation logging, and agent-led development workflows.

The next phase should unify these concepts into a simple, auditable context-edge lifecycle.

The goal is not to introduce autonomous graph mutation or a sophisticated knowledge-learning system.

The goal is to create a disciplined loop:

```
mechanical sync
    ↓
authoritative edges
    ↓
review/enrichment queue
    ↓
agent enrichment
    ↓
context consumed by agents
    ↓
usefulness / problems observed
    ↓
audit records
    ↓
investigation
    ↓
deterministic detector improvement where justified
    ↓
mechanical sync
```

The fundamental invariant must remain:

AI agents may observe, enrich, request, investigate and evaluate relationships, but authoritative graph edges must continue to originate from mechanical/deterministic rules.

## Phase objective

Design the smallest coherent architecture that provides:

* mechanical edge synchronisation;
* identification of new or changed edges needing review/enrichment;
* agent-driven enrichment of authoritative edges;
* explicit recording of requested/missing relationships;
* explicit recording of useful and unhelpful context;
* agent investigation of those observations;
* a durable audit trail;
* a path by which validated observations can lead to improved deterministic detection;
* clear separation between current graph state and historical observations.

The resulting system should make context itself observable, reviewable and improvable without weakening CodeCompass's deterministic trust boundary.

## Core design principle

Treat the following as different concepts.

### 1. Graph fact

A relationship mechanically established by CodeCompass.

Example:

```
reports.py
    INVOKES → hledger
```

This is authoritative because CodeCompass has deterministic evidence for it.

### 2. Enrichment

An AI-generated explanation of what an authoritative edge means or why it matters.

Example:

```
This invocation is LedgerKit's boundary to hledger's
balance-reporting behaviour.
```

Enrichment must never silently become graph truth.

### 3. Observation

Something learned from actual agent use of context.

Examples:

```
EDGE_USEFUL
EDGE_UNHELPFUL
EDGE_MISLEADING
EDGE_REQUESTED
EDGE_MISSING
EDGE_STALE
```

Observations describe agent experience, not authoritative graph state.

### 4. Investigation

An agent examines an observation and gathers evidence.

The investigation may conclude:

* the existing graph is correct and no action is required;
* retrieval/ranking should change;
* enrichment should change;
* an existing detector is faulty;
* a genuinely missing relationship exists;
* a new deterministic detector/rule should be proposed.

### 5. Detector change

If investigation demonstrates that CodeCompass ought to discover a relationship mechanically, that should result in a normal development change to CodeCompass.

The relationship only becomes authoritative when a subsequent mechanical sync detects it.

## Required lifecycle

Design an explicit lifecycle approximately equivalent to:

```
SYNC
 ↓
mechanically detected edge
 ↓
authoritative graph
 ↓
new/changed edge identified
 ↓
REVIEW / ENRICHMENT QUEUE
 ↓
context enrichment agent
 ↓
enriched edge
 ↓
real agent usage
 ↓
┌──────────────┬──────────────┬──────────────┐
│ useful       │ unhelpful    │ missing      │
│              │ misleading   │ requested    │
└──────┬───────┴───────┬──────┴──────┬───────┘
       │               │             │
       └───────────────┼─────────────┘
                       ↓
                audit observation
                       ↓
                context curator
                       ↓
                  investigation
                       ↓
          ┌────────────┴────────────┐
          │                         │
       no change                improvement
                                    ↓
                         deterministic rule/change
                                    ↓
                                  sync
```

Do not assume every edge requires human approval before entering the graph.

Mechanically detected relationships should remain authoritative according to existing CodeCompass rules.

Review/enrichment metadata is a separate concern.

## Edge review state

Consider whether authoritative edges should carry or be associated with lifecycle metadata such as:

```
unreviewed
enriched
used
questioned
```

Do not confuse this with whether the underlying edge is authoritative.

For example:

```
edge:
    reports.py → INVOKES → hledger
authority:
    mechanical
review_state:
    enriched
```

The plan should determine whether this state belongs in:

* the context database;
* a separate audit store;
* generated metadata;
* or some combination.

Prefer the simplest design that preserves rebuildability and provenance.

## Audit trail

The audit trail must survive graph regeneration.

CodeCompass's current graph should continue to represent current project state.

The audit mechanism should represent historical context experience.

Do not allow a full graph rebuild to erase information such as:

An agent requested relationship X, investigation Y occurred, detector Z was added, and later syncs began producing the edge.

Evaluate a small append-oriented format such as:

```
.codecompass/context-audit/
```

with records conceptually representing:

```
observations
investigations
resolutions
```

Possible implementation options include:

* JSONL;
* SQLite;
* Markdown/YAML records;
* reuse/generalisation of existing planning/context-gap infrastructure.

Do not choose a format simply because it is sophisticated.

Prefer:

* diffability;
* auditability;
* deterministic identifiers;
* easy agent access;
* human inspectability;
* low implementation complexity.

## Context observation model

Design a minimal observation schema.

Possible observation types:

```
edge_requested
edge_missing
edge_useful
edge_unhelpful
edge_misleading
edge_redundant
edge_stale
```

Avoid treating all negative feedback as equivalent.

An edge can be mechanically correct but unhelpful for a particular task.

For example:

```
README.md
    MENTIONS → click
```

may be true but irrelevant to a transaction-validation change.

The model should therefore distinguish at least:

```
edge correctness
```

from:

```
task usefulness
```

Do not delete or invalidate authoritative relationships merely because they were unhelpful for one task.

## Edge requests

A requested relationship is particularly important.

Example:

```
source:
    ledgerkit/query.py
requested relationship:
    GOVERNED_BY → hledger-query-semantics
reason:
    agent needed this relationship while implementing a task,
    but CodeCompass could not discover it
```

A request must not immediately create an authoritative edge.

Instead:

```
request
 ↓
investigation
 ↓
evidence gathered
 ↓
valid / unsupported / duplicate / retrieval problem
 ↓
if valid:
    propose deterministic detection mechanism
 ↓
normal implementation
 ↓
mechanical sync
 ↓
edge becomes authoritative
```

The plan should explicitly preserve this authority boundary.

## Investigation agent / context curator

Review the existing CodeCompass agent roster before introducing another role.

Prefer evolving an existing role, particularly the knowledge/context-curation responsibility, if appropriate.

The responsible agent should be able to:

* review new edge-enrichment work;
* inspect edge requests;
* investigate negative feedback;
* gather evidence;
* classify observations;
* recommend detector/retrieval/enrichment changes;
* document resolutions;
* link observations to resulting ADRs/issues/commits where appropriate.

It must not be allowed to:

* directly create authoritative graph edges;
* modify graph facts merely because it believes they are correct;
* approve its own interpretation as deterministic truth;
* bypass normal CodeCompass implementation/testing/review mechanisms.

Clearly define responsibilities and prohibitions.

## Enrichment queue

Plan how CodeCompass detects edges requiring enrichment.

Consider at minimum:

* newly created edge;
* edge whose underlying evidence changed;
* enrichment schema/version changed;
* enrichment absent;
* edge explicitly flagged for re-review.

Avoid unnecessary re-enrichment of unchanged relationships.

The plan should determine what stable identity/fingerprint is required to recognise:

```
same edge, unchanged
```

versus:

```
edge changed and should be reconsidered
```

Where possible, reuse existing CodeCompass hashing/staleness patterns rather than introducing another independent mechanism.

## Requested edge lifecycle

Define a small state machine.

For example:

```
requested
    ↓
investigating
    ↓
┌─────────────────────┬──────────────────────┐
│ unsupported         │ valid                │
│ duplicate           │ retrieval_issue      │
│ already_represented │ detector_gap         │
└─────────────────────┴──────────────────────┘
                              ↓
                         proposed_change
                              ↓
                           resolved
```

The exact states may differ.

Keep the state model small.

## Feedback lifecycle

Similarly, design how useful/unhelpful context feedback is handled.

Example:

```
edge_used
 ↓
agent records outcome
 ↓
useful / irrelevant / misleading / incomplete / stale
 ↓
investigation if required
```

Not every positive or negative observation needs an agent investigation.

Consider rules such as:

```
useful
→ record only
single irrelevant observation
→ record only
repeated irrelevant observations
→ investigate retrieval/ranking
misleading
→ investigate immediately
stale
→ investigate immediately
requested/missing
→ investigate
```

The planning phase should determine sensible initial behaviour without building premature automated optimisation.

## Separation of concerns

The plan must explicitly define the boundaries between:

```
graph builder
edge detector
graph storage
enrichment
retrieval/ranking
agent usage
evaluation
observation recording
investigation
CodeCompass development
```

Avoid allowing one subsystem to become responsible for everything.

In particular:

```
detector
→ establishes facts
enrichment agent
→ interprets facts
consumer agent
→ uses context
evaluation/consumer
→ reports context experience
context curator
→ investigates observations
developer agent
→ implements approved deterministic changes
```

## Integration with existing CodeCompass systems

Before proposing new files, commands, schemas or agents:

1. inspect the current repository;
2. identify all relevant existing mechanisms;
3. identify which should be reused;
4. identify which should be generalised;
5. identify which should be deprecated or merged.

At minimum inspect:

* context graph schema and sync lifecycle;
* deterministic edge generation;
* relationship enrichment;
* context-gap handling;
* context-use/evaluation logging;
* context-health mechanisms;
* agent-led workflow;
* candidate-learning lifecycle;
* relevant ADRs;
* existing CLI/query/discovery commands;
* current LedgerKit evaluation artefacts.

The preferred solution should consolidate existing mechanisms rather than creating parallel systems.

## LedgerKit as reference case

Use LedgerKit as the initial reference project.

Walk the proposed architecture through concrete scenarios.

### Scenario A — mechanical edge

CodeCompass discovers:

```
ledgerkit/report.py
    INVOKES → hledger
```

Expected lifecycle:

```
sync
→ authoritative edge
→ enrichment queued
→ enrichment written
→ available to agent
```

### Scenario B — useful edge

An agent uses this relationship to correctly find relevant hledger context.

Expected result:

```
edge_useful observation
```

No graph mutation required.

### Scenario C — irrelevant edge

A correct edge is surfaced for a task but provides no value.

Expected:

```
edge_unhelpful / irrelevant observation
```

The edge remains authoritative.

Repeated evidence might eventually justify retrieval/ranking changes.

### Scenario D — missing edge

An agent discovers that:

```
ledgerkit/query.py
```

should be linked to a particular hledger query specification, but CodeCompass cannot surface it.

Expected:

```
edge request
→ investigation
→ evidence
→ detector gap identified
→ deterministic implementation proposed
→ subsequent sync establishes edge
```

### Scenario E — misleading enrichment

The mechanical edge is correct but its AI-generated explanation is wrong.

Expected:

```
enrichment feedback
```

This should cause enrichment review, not invalidation of the underlying graph fact.

## CLI / agent interface

Determine whether new user-facing commands are required.

Possible conceptual operations include:

```
codecompass context audit
codecompass context observations
codecompass context review
codecompass context request ...
```

Do not add CLI surface unnecessarily.

Agent-driven operation may be better implemented through existing discovery/query interfaces plus structured project artefacts.

Recommend only the minimum surface required.

## Provenance

Every lifecycle object should be traceable.

Where feasible capture:

```
stable ID
timestamp
project/repository state
task/evaluation identifier
agent role
source edge
evidence
observation type
investigation outcome
resolution
related detector/ADR/change
```

Do not over-engineer this into a distributed event system.

A simple local audit trail is sufficient.

## Determinism and reproducibility

Preserve existing CodeCompass principles:

* graph facts remain mechanically reproducible;
* AI enrichment remains non-authoritative;
* audit records are explicit and attributable;
* agent observations cannot silently rewrite history;
* repeated sync does not create duplicate lifecycle events;
* IDs should be stable where appropriate;
* audit records should be deterministic enough to review and test.

## Testing requirements

The planning document must define tests for the lifecycle.

Include at least:

### Unit tests

* stable edge identity;
* identification of new/changed edges;
* observation schema validation;
* lifecycle state transitions;
* duplicate-request handling;
* audit persistence;
* rebuild does not erase audit history.

### Integration tests

* mechanical sync creates an edge;
* edge becomes eligible for enrichment;
* enrichment persists correctly;
* edge request is recorded;
* investigation can resolve request;
* no agent-created request becomes graph truth;
* later detector implementation allows sync to establish the requested relationship.

### Regression tests

Ensure existing:

* graph sync;
* enrichment;
* discovery;
* context-gap;
* evaluation;
* agent workflow

behaviour continues to work or is migrated intentionally.

### LedgerKit evaluation

Re-run suitable existing LedgerKit evaluations to verify that the lifecycle architecture does not merely work structurally but improves the project's ability to learn from context failures.

## Migration

The plan must identify how existing artefacts such as:

```
context-gaps/
context-use-log
context-health
candidate learnings
existing relationship enrichment
```

map into the new lifecycle.

Prefer migration/generalisation over duplication.

Document explicitly:

```
keep
generalise
rename
merge
deprecate
remove
```

for each existing mechanism.

## Scope control

Do NOT turn this phase into:

* autonomous graph learning;
* probabilistic edge truth;
* embeddings/vector search redesign;
* graph neural networks;
* automatic edge deletion based on agent feedback;
* self-modifying detector code;
* distributed event infrastructure;
* cloud telemetry;
* hosted services;
* a UI/dashboard;
* optimisation algorithms for ranking;
* automatic promotion of inferred relationships.

Those can be considered later if evidence justifies them.

This phase should remain intentionally boring and auditable.

## Key invariant

The architecture should make this impossible by design:

```
agent:
"I think A relates to B"
→ authoritative graph edge
```

The valid path is:

```
agent observation
→ audit record
→ investigation
→ evidence
→ deterministic detector/change
→ mechanical sync
→ authoritative graph edge
```

Treat this as a core CodeCompass trust guarantee.

## Deliverables

Produce a detailed planning package containing:

1. Current-state assessment
2. Proposed architecture
3. Data model
4. State machines
5. Agent responsibilities
6. Repository changes
7. Test plan
8. Migration plan
9. Phased implementation sequence
10. Success criteria

(Full sub-bullets for each: see the corresponding section in
`planning/context-edge-lifecycle-plan.md`, which answers each of these
in turn against the actual repository.)

## Planning constraints

Do not assume this prompt's suggested filenames, table names, or state names are correct.

Inspect the current implementation and adapt the design to CodeCompass's existing conventions.

Prefer:

* incremental evolution;
* reuse of current systems;
* simple local data;
* explicit authority boundaries;
* testability;
* human-reviewable history.

Avoid introducing abstractions that are not justified by a real current use case.

## Final design question

Use this question to assess the proposed architecture:

Can CodeCompass learn from the context agents actually need, without ever confusing an agent's opinion about a relationship with mechanically established project truth?

If the proposed design can answer that clearly and simply, it is likely on the right track.

Produce the plan for review before making any implementation changes.

Save plan and this prompt to planning folder.
