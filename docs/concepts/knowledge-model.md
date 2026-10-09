# Concept: the evidence/knowledge record model

CodeCompass ships a general-purpose, persistent, bidirectional **intermediate knowledge layer** (`src/codecompass/knowledge_intermediate.py`), exposed as the `codecompass knowledge` CLI subcommand group. It operates on whatever `planning/knowledge/<slug>/` directory tree exists under a project root — **including, but not limited to, CodeCompass's own repository**, per that module's own docstring. CodeCompass's own repository is both the primary place this capability is currently exercised and the thing most of the publicly-visible evidence about it happens to describe — be deliberate about which scope a given statement is really about.

## The six record kinds

A flat, file-based model: one record per YAML file, each carrying a `kind` field and an id with a matching prefix.

| Kind | Id prefix | What it is |
|---|---|---|
| Observation | `OBS-` | A single, dated, reproducible act of looking — running a command, reading a specific file. Never itself a claim about behaviour; its own `status` is always `recorded`. |
| Evidence | `EV-` | A strictly **neutral** package of one or more Observations (or a direct source/doc/test citation). Never itself asserts support or contradiction of anything — that relationship belongs only to a Claim that cites it. |
| Claim | `CL-` | An interpretation built from one or more Evidence records — the **only** place a support/contradict relationship is recorded. `status` ∈ `proposed`/`supported`/`contradicted`/`superseded`/`verified`. Its `supersedes` field only ever names another Claim (a structural hard rule). |
| Derivation | `DE-` | Records the *reasoning process* that produced a Claim — which files were traced, in what order — not merely the Claim's conclusion restated. Cites Evidence ids, never Observation ids directly. |
| Decision | `DEC-` | The **only** record kind a human/project-owner authors or ratifies. Records chosen project behaviour, never a revision of observed upstream fact. Its `supersedes` field only ever names another Decision (the same structural hard rule, in the other direction). |
| Requirement | `REQ-` | Implementation-facing and testable — what a coding agent actually implements against. Always cites the Decision that authorises it, with a Given/When/Then `example` field. `status` ∈ `proposed`/`approved`/`implemented`/`verified`. |

**A structural split, by design, not an omission:** the shipped `codecompass knowledge` CLI only ever creates or mutates `Claim` or `Requirement` records. `Observation`/`Evidence`/`Decision`/`Derivation` records are meant to be hand-authored YAML files following the documented schema — any text editor, no CodeCompass-specific tooling required — never produced through this CLI. If you are evaluating this as something to adopt wholesale on another project: there is no shipped validator for an adopting project's own `planning/knowledge/` tree beyond `knowledge_intermediate.py` itself — the maintainer-only `scripts/check_knowledge_base.py` is hard-coded to this one repository and is not something another project can simply point elsewhere.

## Provenance — a cross-cutting property, not a record kind of its own

"Provenance" never names a record kind — it is realized with a structurally different shape in at least three separate mechanisms:
- Formal knowledge records (above) carry a named, method-conditional set of provenance fields (`repository_revision`, `source_ref`/`doc_ref`/`test_ref`, `performed_by`/`derived_by`/`decided_by`, `tool`/`tool_version`, `timestamp`).
- The context graph's AI-enrichment tables (`vendor_enrichment`, `symbol_enrichment`, `doc_relation_enrichment`) each carry a single `model` TEXT column recording the producing model (or, for agent-driven enrichment, a literal `agent:<name>` string — see `docs/workflows/sync-and-enrichment-pipeline.md`). `symbol_enrichment.model` is nullable specifically to allow an honest `NULL` ("producer unknown") on rows written before this column existed; every new write always supplies a real value.
- Other narrative-provenance files elsewhere in the project's own history carry their own ad hoc field sets.

No shared schema unifies these — and no evidence suggests unifying them has ever been attempted.

## The intermediate projection and the reconciliation loop

See `docs/workflows/knowledge-reconciliation-loop.md` for the full mechanics: canonical records are rendered into editable Markdown, edits are mechanically detected via a dual-hash anchor (never comparing a semantic hash against a projection hash directly), a human/agent review stage is required, and `codecompass knowledge apply` is the sole, re-validating write path.

## "Invariant" is not a seventh record kind

"Invariant" is not one of the six formal kinds above and has no dedicated schema. As used across the project, it names at least three distinct things: a `planning/learnings/`-queue classification value meaning "a required behavioural invariant, promote to a regression test"; a narrative subsection inside a feature's own design document; and a project-wide cross-cutting-rules document this reconstruction cannot see directly. These three senses are not guaranteed to coincide.
