# 0085. Corrective amendment to the v2 knowledge-driven-development roadmap: the logical knowledge model is formalised, Phase 84's CLI scope is narrowed, the merged Phase 88 is split into MCP and reconciliation, placement-policy enforcement classes are clarified, the documentation suite and its quality baseline are specified, and Phases 83-91 are resequenced to 83-92

## Status

Accepted (2026-10-23, direct user request — "CodeCompass Orchestrator —
Corrective Amendment to v2 Knowledge-Driven Development Roadmap").
Amends `decisions/0084` (does not reopen it; `decisions/0084`'s own
architecture decision in §1 — one logical knowledge model, unchanged
physical storage, a new consolidating API, no new database — is
preserved and formalised further, not reversed). Extends
`decisions/0078`/`0079`/`0080`/`0081` unchanged. Does not touch
`decisions/0082`/`0083` or reopen Phase 82. Planning only: this ADR
authorises no implementation. Every phase it amends or renumbers still
requires its own `CLAUDE.md` §1 plan file before implementation begins.

## Context

**Verified current state, re-inspected this session, not assumed**:
`HEAD` is `ae4c486` (the `decisions/0084` realignment commit), clean
working tree, in sync with `origin/main`. Phase 82 is confirmed `done`
(`planning/ROADMAP.md`'s own Phase 82 row: implemented, independently
audited PASS, two further corrective passes each independently
re-audited PASS). **Phase 83 is confirmed next and unchanged** —
`planning/CONTEXT.md`'s own "Next concrete step" section and
`planning/v2-roadmap.md`'s own Phase 83 section both independently say
so; no evidence found of any defect in Phase 83's own scope or exit
criteria, so per the governing prompt's own explicit instruction, Phase
83 is **not reopened or redefined** by this ADR. No `planning/
phase-83-*.md` or later plan file exists (confirmed by directory
listing). No `src/codecompass/mcp.py`, `knowledge_api.py`, or
documentation-compiler module exists (confirmed by directory listing of
`src/codecompass/`: `adapters/`, `chat.py`, `claude_md.py`, `cli.py`,
`commands.py`, `config.py`, `core.py`, `deptree.py`, `discovery.py`,
`doc_chunking.py`, `doc_mapping.py`, `enrichment.py`, `filetree.py`,
`git_topology.py`, `graph.py`, `index.py`, `knowledge_intermediate.py`,
`oracle.py`, `relation_enrichment.py`, `skill.py`, `skill_scan.py`,
`source_resolution.py`, `source_symbols.py`, `spec_docs.py`,
`staleness.py`, `symbols.py`, `sync.py`, `usage.py` — no new module
since `decisions/0084`).

**Confirmed directly against the real CLI** (`src/codecompass/cli.py`):
`query_app`, `enrich_app`, and `knowledge_app` are three **independently
defined `typer.Typer()` sub-apps** (lines 54/56/60), each with its own
command functions reading `context-graph.db` or `planning/knowledge/`
directly (`query vendors`/`vendor`/`symbol`/`skills`/`relations`/
`topology`/`source`/`source-symbol`; `knowledge render`/
`select-candidates`/`apply`/`status`/`doc-select-candidates`/
`doc-acknowledge-stale`/`doc-acknowledge-chunks`; `enrich apply`) — this
independently reconfirms `decisions/0084`'s own Context section: there
is no shared interface between them today, exactly as that ADR
described. `knowledge_intermediate.py` already provides
`derive_epistemic_profile` (INTENDED/OBSERVED/VERIFIED/CONTESTED,
read-time only) and `derive_provenance_label`, already consumes
`contradicting_evidence`/`open_questions`-style fields, and already
reconciles a dual-hash (`base_semantic_hash`/`base_projection_hash`)
presentation/semantics split (`decisions/0073`/`0074`) — all reused by
this ADR's formalised logical model (§1), none rebuilt.

A follow-up governing prompt ("CodeCompass Orchestrator — Corrective
Amendment to v2 Knowledge-Driven Development Roadmap") reviewed
`decisions/0084`'s own output and identified six specific corrections,
summarised here and addressed in full below: (1) Phase 84's own
consolidated knowledge API lacked an explicit logical model specifying
identity, canonical-vs-derived status, authoritative sources per
knowledge kind, provenance/snapshot identity, and export versioning;
(2) Phase 84's CLI-migration scope ("migrate `query`/`knowledge`/
`enrich` onto it") risked an unbounded refactor and a second, informal
mutation path; (3) the merged Phase 88 (MCP + reconciliation) bundled
two independently testable capabilities behind one exit gate; (4) Phase
86's mechanical/behavioural/semantic enforcement split needed sharper
definition and an explicit "appearing more than once is not a defect"
clarification; (5) Phase 87's minimum documentation deliverable and
editorial bar were underspecified; (6) Phase 87's "materially less
human correction than Phase 80" comparison point, and Phase 89
(renumbered 90 by this ADR)'s arm-exclusion/optional-baseline framing,
were methodologically weak. None of these six findings reopens Phase
82, changes Phase 83, or reverses `decisions/0084`'s own architecture
decision — each is a refinement of a phase that was, by design,
deliberately left at roadmap depth rather than implementation-ready
detail (`decisions/0084` §2's own "none of Phases 83-91 is phase-planned
by this ADR").

## Decision

### 1. The logical knowledge model is formalised (Phase 84)

`decisions/0084` §1 already decided the architecture: one logical,
typed knowledge model in front of unchanged physical storage
(`context-graph.db`, `planning/knowledge/`, `planning/contracts/`), no
new database. This ADR does not revisit that decision — it specifies
the model itself, answering the nine points the corrective prompt names,
each mapped to a real, already-existing mechanism wherever one exists
rather than inventing a parallel concept:

1. **Stable, project-qualified record identities and relationship
   identities.** Record identity is the existing `REQ-`/`CL-`/`EV-`/
   `OBS-`/`DE-`/`DEC-` id scheme (`planning/knowledge/<slug>/`), a
   `context-graph.db` row's own primary key (`source_files.id`,
   `source_symbols.id`, `doc_relations_edges.id`, etc.), or a
   `planning/contracts/<slug>/` oracle-contract/result's own
   `contract_id`/`check_id`/`run_id` triple — the API assigns no new id
   scheme. "Project-qualified" is satisfied today by the fact that every
   id is scoped to one repository checkout; a future federated caller
   qualifies it externally via `decisions/0079`'s project-identity
   envelope, never by rewriting the id itself. Relationship identity
   reuses existing typed edges (`doc_relations_edges`, a Claim's own
   `depends_on`/`contradicting_evidence`/`observations` fields) — the
   API exposes these as typed, traversable edges; it does not invent a
   new edge table.
2. **Canonical versus derived or presentation-only information.**
   Canonical: `context-graph.db` rows, `planning/knowledge/<slug>/*.md`
   records, `planning/contracts/<slug>/*.yaml` contract/result files,
   accepted `decisions/*.md` ADRs. Derived/presentation-only: rendered
   Markdown projections (`knowledge_intermediate.py::render_slug`/
   `render_block`), the presentation-wording cache
   (`PresentationEntry`), and Phase 87's generated documentation output.
   The API tags every returned record with this distinction and always
   resolves a canonical query to the underlying record/row/file, never
   to a rendered projection — a rendered page is never itself a source
   the API reads *from*.
3. **Authoritative sources per knowledge kind.** Implementation facts:
   `context-graph.db`'s mechanical facts and an oracle result's
   `VERIFIED` outcome — never an ADR, never a comment, never generated
   prose. Approved requirements: a Requirement record whose `status:
   verified` cites either a passing oracle result (`planning/
   contracts/<slug>/`) or an approved Decision it legitimately traces to
   — `check_knowledge_base.py`'s existing `check_verified_status_cites_
   passing_oracle_result` already enforces this; the API surfaces the
   same check's result, it does not re-derive a separate notion of
   "approved." Architectural intent: an accepted `decisions/*.md` ADR —
   **an ADR establishes design intent, and the API labels it exactly
   that; an ADR's existence or acceptance never independently proves
   implementation behaviour**, which is exactly what
   `derive_epistemic_profile`'s INTENDED-vs-VERIFIED separation already
   enforces and this ADR does not change. Verification evidence: a real
   oracle-result file plus the Evidence record(s) it is cited from.
4. **Source revisions, knowledge-snapshot identities, and provenance.**
   The API exposes, never re-derives: an oracle-result's own content
   digest (`oracle.py::compute_tree_digest`, scoped to a contract's
   explicit `tested_paths`/`test_input_paths`); Phase 79/80/81B's
   existing frozen-snapshot convention (a `documented_revision`-style
   pinned commit SHA) for any knowledge-snapshot identity a future
   consumer needs; the presentation cache's own `base_semantic_hash`/
   `base_projection_hash` pair for a rendered block's provenance. No new
   snapshot or revision-identity mechanism is introduced.
5. **Independent epistemic dimensions.** Exactly `decisions/0080`'s
   `derive_epistemic_profile` (INTENDED/OBSERVED/VERIFIED-per-scope/
   CONTESTED), unchanged, reused by reference — `decisions/0084` §1
   already said this and this ADR does not revisit it.
6. **Contradictions, unresolved questions, uncertainty, and stale
   evidence.** The API surfaces, unchanged: a Claim's own
   `contradicting_evidence` field; a Claim's own `open_questions` field
   (Phase 79's extension); an oracle contract's `GAP`/`INVALID` outcome;
   `derive_epistemic_profile`'s own `unconfirmed_scopes` (a required
   check whose only citation is a historical `PASS` that could not be
   reconfirmed live) distinct from `known_gap_scopes` (no evidence at
   all) and `verified_scopes` (confirmed current). No new contradiction
   or staleness concept is introduced; the API's genuinely new value
   here (per `decisions/0084`'s own Phase 84 risk mitigation) is
   detecting these *across* record kinds in one traversal, something no
   existing `query` sub-verb does today.
7. **Read-only queries versus controlled knowledge mutations.** The API
   is a **read-only surface, full stop.** Every existing mutation path —
   `knowledge apply`, `enrich apply`, `doc-acknowledge-stale`/
   `doc-acknowledge-chunks`, `oracle.py::accept_baseline` — is
   preserved exactly as it exists today and is **not** reachable through
   the new API. This directly answers §2's own required acceptance
   criterion that the API "must not introduce an alternative route for
   agents to promote unverified claims": it cannot, because it has no
   write path at all.
8. **Consistent treatment of missing or insufficient knowledge.** A
   defined, typed "gap" response — reusing the existing GAP/
   `known_gap_scopes` naming convention — distinct from both an empty
   result (the query is well-formed, nothing matches) and an error (the
   query itself is invalid). Every traversal method returns one of these
   three shapes consistently; none is allowed to silently collapse into
   another (the same "never silently round up" discipline `decisions/
   0081`'s GAP-aggregation rule already established for oracle results).
9. **Versioned, machine-readable exports.** The API's export function
   targets the same schema-versioned JSON shape `decisions/0079` §5
   already specifies for a portable project snapshot (consumable with no
   running `codecompass` process) — not a new export format. This is
   the direct mechanism by which a future MCP server, documentation
   compiler, or Wiki consumes the API without the API itself needing to
   anticipate each consumer's shape, and the direct mechanism by which a
   future federated snapshot export (Post-v2 Stage 1) reuses this
   format rather than redesigning it.

**Required acceptance criteria** (added to Phase 84's own exit gate,
§5 below): a consumer must be able to retrieve, through the one API, a
real architectural decision (an existing `decisions/*.md` ADR),
`balance-from-spec`'s own associated implementation facts, its real
Phase 82 contract, its provenance, and any verification limitation —
and the API's response must make visible, for at least one real case,
where approved intent and verified implementation *agree* and
(if a real example exists; a documented absence is an acceptable,
honestly-reported answer if none does) where they would *disagree* —
not merely two separately-labelled fields that happen never to be
exercised against each other.

### 2. Phase 84's CLI-migration scope is narrowed

The old Phase 84 deliverable ("existing `query`/`knowledge`/`enrich`
commands migrated onto it... old command names and output shapes
preserved") is replaced with a bounded, incremental scope:

- **Priority**: a stable, **read-only**, typed query API (§1 above)
  first. New CLI operations for knowledge search, retrieval, traversal,
  evidence-tracing, and gap-querying are the first milestone's actual
  deliverable.
- **Existing CLI command names, output structures, and exit semantics
  are preserved unconditionally** — not merely as a migration
  constraint, but because most existing commands are **not required to
  migrate at all** by this phase. A command migrates onto the new API
  only where doing so demonstrably removes duplicated logic, decided
  case by case against the real command, not mandated wholesale.
- **Mutation stays behind existing validated write paths.** `knowledge
  apply`, `enrich apply`, and oracle baseline acceptance are explicitly
  out of scope for this phase's API — §1 point 7 already makes this
  structural, not just a stated intention.
- **Required tests**: backward-compatibility tests for any command that
  *is* migrated (identical observable output against a representative
  input set — unchanged from the old Phase 84 language) **and** explicit
  negative-path tests (a malformed query, an id that does not exist, a
  traversal with no results) for every new API operation — not only the
  happy path.
- **The first milestone's own proof of usefulness is retrieval against
  this project's real corpus** (`planning/knowledge/`, `context-graph.db`,
  `planning/contracts/`) — not a wrapper demonstrated only against a
  synthetic fixture, and not gated on MCP existing. `decisions/0084`'s
  own Phase 84 risk (§10, "thin, redundant wrapper") is strengthened by
  this requirement, not replaced.

### 3. The merged Phase 88 is split: MCP and reconciliation are independently deliverable

`decisions/0084` §2 merged the old Phase 84 (MCP) and old Phase 85
(reconciliation) into one Phase 88, reasoning that "the governing
prompt's own §10 point 8 groups them as one sequence step." The
corrective prompt is explicit that this bundled two separable
capabilities behind one exit gate and must be undone. **Phase 88 is
split back into two phases**, neither one a prerequisite for the
other's own exit gate:

- **New Phase 88 — Agent Integration and MCP.** A minimal, bounded MCP
  interface over Phase 84's API: contract, evidence, context, impact
  (Phase 83), and documentation (Phase 87) retrieval; controlled
  verification execution; permission and untrusted-content handling; a
  genuine Ledgerkit development task completed through the supported
  interface. **Must consume Phase 84's and Phase 83's existing services,
  never duplicate them** — the corrective prompt's own explicit
  constraint. Full 10-point detail: `planning/v2-roadmap.md`.
- **New Phase 89 — Incremental Knowledge and Documentation
  Reconciliation.** Source/test change detection; identification of
  affected canonical knowledge; explicit staleness/conflict reporting;
  section-to-knowledge dependency mapping; targeted documentation
  invalidation and regeneration; preservation of unrelated documents and
  accepted editorial changes; a demonstrated second development task
  benefiting from previously reconciled knowledge. **Operates
  independently of MCP transport** — its own exit gate is satisfied by a
  real source change correctly invalidating specific knowledge/
  documentation and a real unrelated change correctly leaving the rest
  alone, none of which requires an MCP server to exist or run. Its
  prerequisites are Phase 84 (API) and Phase 87 (documentation surface
  to reconcile) only — **not Phase 88** — matching the same
  dependency-correctness the corrective prompt's own closeout checklist
  names explicitly ("whether MCP and reconciliation are genuinely
  independently deliverable"). Full 10-point detail: `planning/
  v2-roadmap.md`.
- **Clarification carried from Phase 87**: Phase 87 may demonstrate
  *manually triggered* incremental documentation updates (its own
  incremental-maintenance mode, already specified); Phase 89 is what
  introduces *change-driven* (automatic, detection-triggered)
  maintenance. These are not the same capability and Phase 87's own
  exit gate does not require the latter.
- **Nothing from the old merged Phase 88 is dropped** — every
  deliverable, test, and risk the old Phase 88 section named is
  preserved, reassigned to whichever of the two new phases it actually
  belongs to (MCP-specific items to 88; reconciliation-specific items to
  89), per `planning/v2-roadmap.md`'s own rewritten sections.

### 4. Phase 86's enforcement classes are clarified

`decisions/0084`'s own Phase 86 section already distinguished
`strict` (mechanically testable) from advisory/informational
(subjective) findings, reusing the `Finding`-with-`strict`-flag pattern.
This ADR sharpens that split into three named classes and adds a
formal Knowledge Placement Policy mapping the corrective prompt's own
eight categories onto this project's real artifact names:

| Category | This project's artifact |
|---|---|
| Implementation logic | `src/codecompass/*.py` source itself |
| Interface documentation and docstrings | module/function docstrings |
| Non-obvious local comments | inline code comments — this project's own existing comment discipline (comment only when the WHY is non-obvious, never restate the WHAT) is the placement rule for this category, not a new one |
| Architectural rationale and approved decisions | `decisions/*.md` (ADRs) |
| Behavioural requirements and invariants | `planning/knowledge/<slug>/*.md` Requirement records and `planning/contracts/<slug>/` oracle contracts |
| Verification evidence | `planning/contracts/<slug>/*.yaml` oracle-result files and `planning/knowledge/<slug>/` Evidence records |
| Human-oriented project documentation | `docs/**`, `README.md`, `ai-docs/**` (Phase 87's compiled output lands here) |
| Historical design context | `decisions/*.md` (append-only), `planning/retros/`, `architecture/historical-notes.md` where it exists |

**Enforcement classes**:

- **Mechanical** — objective, deterministic, independently reproducible
  (e.g. a comment citing a `decisions/NNNN` number that does not exist,
  or whose cited ADR's own first-line status contradicts the comment's
  claim about it). May block where policy explicitly requires.
- **Behavioural** — a violation demonstrated through an accepted
  executable contract or independently verifiable evidence (e.g. a
  docstring's claimed behaviour contradicted by a real oracle `FAIL`).
  Blocks only on real evidence, never on assertion.
- **Semantic/editorial** — AI-assisted judgment of verbosity,
  abstraction quality, placement appropriateness, or architectural
  consistency. **Always advisory** unless and until a specific instance
  is converted into an independently testable requirement (at which
  point it is no longer this class) — the governing prompt's own
  explicit constraint, unchanged from `decisions/0084`.

**Explicit clarifications, both directions**: knowledge placement is
**not** a requirement that information appear exactly once — a critical
invariant may legitimately live in a code comment, a behavioural
contract, and human documentation simultaneously, with one consistent
underlying meaning; flagging that as duplication would be a false
positive. Conversely, **a prose contradiction with an accepted
architectural decision is never classified as mechanically proven
merely because an LLM judges it contradictory** — that judgment is
semantic/editorial by construction unless a real, citable mechanical
check (e.g. the ADR-number-and-status check above) backs it.

**Required controls, both directions**: a deliberately-constructed
placement defect (unchanged from `decisions/0084`'s own Phase 86 test
requirement) **and** a positive control — a real or constructed example
where extensive implementation comments are legitimately appropriate
(e.g. `oracle.py`'s own non-obvious subprocess/digest-handling comments)
— correctly left unflagged, so the reviewer is shown capable of saying
no to a plausible-looking false positive, not only yes to a true one.

### 5. Phase 87's minimum documentation suite, schema, and compilation pipeline are specified

**Minimum publication suite**, mapped onto this project's own existing
filenames (retained, not replaced, per the governing prompt's own
explicit allowance):

| Document | Required purpose | This project's existing file |
|---|---|---|
| README.md | Problem, product value, current capabilities, installation, first steps | `README.md` |
| Getting Started | A tested, practical first-use tutorial | `docs/getting-started.md` |
| Concepts | Canonical knowledge, evidence, contracts, epistemic distinctions, reconciliation | `docs/concepts/*.md` (extended — a new page explicitly covering epistemic distinctions and the reconciliation loop is a named gap this phase must fill, not assumed already complete) |
| Architecture | Major components, responsibilities, data flows, design principles | `docs/architecture/overview.md`, `components.md`, `data-and-control-flow.md` |
| Reference | Accurate CLI/configuration information, generated deterministically where practical | `docs/reference/cli.md`, `configuration.md` (currently hand-maintained — generating these deterministically from the real Typer command tree is this phase's own improvement opportunity, not assumed solved) |
| Contributor Guide | Development conventions, workflow, testing, verification, knowledge-placement expectations | `CONTRIBUTING.md` / `docs/development/contributing.md` |

The first demonstrator stays bounded (README plus a small selected
supporting set, unchanged from `decisions/0084`), but **the complete
minimum suite above is required before Phase 87's own closeout** — not
merely the demonstrator. The objective is this coherent, maintainable
document set, not an expansive documentation website or a reproduction
of internal planning history (`CONTEXT.md`/`ROADMAP.md`'s own dense,
audit-log-style prose is explicitly **not** a template the compiler may
draw stylistic cues from for reader-facing documents).

**User-defined documentation schema** (versioned, per document): intended
audience; document purpose; required sections; expected depth/
approximate verbosity; tone and editorial style; required examples;
evidence requirements; acceptance criteria. Diátaxis is a default
reference shape, not a mandatory structure — a project may define its
own.

**Compilation pipeline** (the compiler must, in order): (1) retrieve
accepted knowledge through Phase 84's API only; (2) resolve relevant
source/verification evidence; (3) map knowledge to required schema
sections; (4) identify material knowledge gaps *before* writing; (5)
generate bounded, section-specific knowledge packets; (6) compose each
section through the existing clean-room broker (Phase 81B, unchanged);
(7) independently validate technical claims and executable examples;
(8) assess usefulness, clarity, and audience suitability as a distinct
step from factual validation; (9) preserve provenance on demand without
cluttering ordinary prose. The clean-room writer does not access
existing narrative documentation when reconstructing from scratch
(unchanged discipline, Phase 79/80's own precedent); legacy
documentation is usable only as a gap detector, with every candidate gap
independently re-established as fact before acting on it, never trusted
as evidence on its own. Presentation-only edits and genuine semantic
knowledge changes are distinguished using the existing reconciliation
model (`decisions/0074`'s `semantic_change` field) — unchanged.

**Editorial requirements**: value and purpose before implementation
detail; concise explanations suitable for an unfamiliar developer; clear
separation between current and planned functionality; tested examples;
minimal internal development history; consistent terminology;
appropriate links to detailed reference material rather than inlining
it; no unsupported claims or fabricated capabilities. **The README must
not resemble an audit report.** Editorial quality is assessed
independently of, not instead of, factual correctness — unchanged from
`decisions/0084`, now made an explicit, separately-scored step.

### 6. Phase 87's documentation-quality baseline is corrected

`decisions/0084`'s own Phase 87 exit gate required "materially less
human correction than Phase 80's own prior clean-room reconstruction" —
the corrective prompt correctly identifies that Phase 80's retro records
its own real correction count but was never designed as a standardised
baseline for a fair before/after comparison (different scope, no pinned
revision discipline built for comparison purposes, no fixed
reader-task/rubric). **This comparison point is withdrawn as a
stand-alone success criterion.** In its place, Phase 87's exit gate
requires a **reproducible baseline**, defined at Phase 87's own planning
time, covering: identical or appropriately matched documentation
requirements; pinned source and knowledge revisions; a fixed reader-task
evaluation; an independently defined editorial-quality rubric; technical
accuracy and grounding checks; tested installation and example
execution; the number and severity of corrections required; human
editing/review time; and any unresolved errors or unsupported claims.
**If Phase 80's own historical editing effort cannot be reliably
reconstructed against this standard, Phase 87 runs a fresh, matched
baseline comparison instead of reusing Phase 80's number** — no
historical effort estimate is invented, and no improvement claim is made
from incomparable measurements. An independent reader evaluation and at
least one successful clean-environment onboarding exercise are both
required, not optional.

### 7. Phase 90 (renumbered from 89)'s evaluation methodology is strengthened

Three corrections to `planning/v2-evaluation-methodology.md`, added as a
further dated amendment to that file by this same commit (not a rewrite
of its existing three-arm design, which is unchanged again):

- **Comparable documentation outcomes across every arm, including Arm
  A.** The existing methodology's own prior amendment (`decisions/0084`
  §4) reported the new documentation-quality metric "for Arms B and C...
  not reported for Arm A, which has none" — the corrective prompt is
  explicit that Arm A's *absence* of CodeCompass-generated documentation
  is not a reason to exclude it from measurement. Arm A is now scored on
  the same documentation-quality/effort/maintenance-cost rubric against
  whatever documentation outcome it actually produces (including a
  scored "produced none" outcome where that is what genuinely happens) —
  every arm receives an equivalent documentation deliverable requirement
  and acceptance criteria, not a different standard.
- **A mandatory concise-repository-instructions comparator.** The
  existing optional "concise-repository-instructions baseline" is now
  **mandatory for the principal net-efficiency evaluation** — it is run
  under the same task, resource, and evaluation conditions as the three
  primary arms, and the trial's overall net-efficiency conclusion is not
  valid without it. It remains, exactly as before, **never a v2 release
  dependency on its own** — a result favouring this baseline over
  CodeCompass does not block v2.0, it is reported with equal prominence,
  per the existing honesty standard.
- **Cumulative benefit measured across successive tasks, not one task.**
  The trial design must include a genuine sequence of related
  development tasks (not a single task) so that whether knowledge
  retained from an earlier task reduces later effort can actually be
  observed, recording for each task: independently accepted changes;
  regressions and rework; token/execution costs; elapsed time; human
  investigation/review time; knowledge construction/reconciliation
  costs; documentation generation/maintenance costs; initial setup/
  integration costs (amortised across the real number of tasks run, not
  the first alone — unchanged from the existing methodology); reuse of
  previously accepted knowledge; and correctness/maintainability
  outcomes. The existing metric 11 ("subsequent knowledge reuse") is
  generalised from "a second task" to "the full task sequence," not
  replaced.

The principal criterion remains, unchanged: improved verified,
maintainable software changes per unit of total effort, after netting
overhead against apparent gains — no numerical target is set in advance
of this phase's own baseline.

### 8. Phases 83-91 are resequenced to 83-92

| Phase | Name | Relation to `decisions/0084`'s own sequence |
|---|---|---|
| 82 | Contract and Evidence Foundation | Unchanged, `done`. |
| 83 | Semantic Change Assurance | **Unchanged** — content, dependencies, and exit gate not reopened, per direct verification (§ Context above) that no defect was found in its own scope. |
| 84 | Consolidated Knowledge API and Query CLI | Same phase number; architecture formalised (§1) and CLI-migration scope narrowed (§2) in place. |
| 85 | Self-Curation and Knowledge-Quality Validation | **Unchanged.** No defect identified; the corrective prompt names no correction to this phase. |
| 86 | Knowledge-Placement and Code-Quality Review | Same phase number; enforcement classes and placement-policy table formalised (§4). |
| 87 | Documentation Schema and Knowledge-Compiled Documentation | Same phase number; minimum suite, schema, and baseline methodology specified (§5-6). |
| 88 | Agent Integration and MCP | **Split out** of the old merged Phase 88 (§3) — MCP only. |
| 89 | Incremental Knowledge and Documentation Reconciliation | **Split out** of the old merged Phase 88 (§3) — reconciliation only; **= old Phase 85's original content**, carried forward via `decisions/0084`'s own merge and now un-merged. |
| 90 | Comparative Development Trials | **= old Phase 89** (itself `= decisions/0084`'s renumbering of the original Phase 86), renumbered only; methodology strengthened (§7), not replaced. |
| 91 | External Validation and Adoption | **= old Phase 90**, renumbered only; content unchanged. |
| 92 | v2.0 Hardening and Release | **= old Phase 91**, renumbered only; content unchanged. |

**Dependency correctness, explicitly checked**: Phase 88 (MCP) depends
on 84, 83, 87. Phase 89 (Reconciliation) depends on 84, 87 — **not** 88,
confirming the two are genuinely independently deliverable in either
order; the roadmap sequences 88 before 89 for narrative flow only, not
because either blocks the other. Phase 90 (trials) depends on 83, 84,
87, 88, **and now 89** (the cumulative-benefit metric, §7, needs a real
reconciliation capability to measure reuse against) — this is a
correction to `decisions/0084`'s own old-Phase-89 prerequisite list,
which did not yet name the reconciliation phase as a prerequisite
because it had not yet been split out. Phase 91 depends on Phase 90's
evidence. Phase 92 depends on Phase 91's completion. No cycle exists.

**Every previous v2 capability remains accounted for**: nothing named in
`decisions/0084`'s own Phase 84-91 sections (now 84-92) is dropped by
this ADR — §1-§7 above sharpen scope and add missing specification;
none removes a deliverable, test, or exit-gate component. Cross-project
overlay compatibility (`decisions/0079`, confirmed unaffected by
`decisions/0084` §5) is re-confirmed unaffected by this ADR too: none of
§1-§8 above changes any canonical record shape, federation identity
mechanism, or Post-v2 stage's own exit gate — the only cross-reference
needing an update is the two phase-number citations in
`planning/post-v2-cross-project-overlay-backlog.md` (old Phase 88's
reconciliation citation now points to Phase 89; old "Phase 91" release
citation now points to Phase 92), both pure renumbering.

## Independent review

Performed before committing, per the governing prompt's own §12, against
every file this ADR touches:

1. **Completed work preserved?** Yes — Phase 82/83 sections of
   `planning/v2-roadmap.md` are not edited by this commit; `decisions/
   0078`-`0084` are not edited (append-only, `CLAUDE.md` §2).
2. **Dependency-correct sequence?** Yes — checked explicitly in §8 above;
   Phase 90's own prerequisite list is corrected to include the newly
   split-out Phase 89, which `decisions/0084`'s own old sequencing could
   not have named.
3. **Every previous v2 capability accounted for?** Yes — the old merged
   Phase 88's full deliverable/test/risk list is reproduced in full
   across the new Phase 88/89 sections in `planning/v2-roadmap.md`, none
   dropped; confirmed by direct comparison against the pre-amendment
   text read at the start of this session.
4. **Logical architecture avoids competing sources of truth?** Yes — §1
   point 2's explicit canonical-vs-derived split, plus point 7's
   read-only-only API, directly close the two ways a competing-authority
   problem could arise (a rendered projection being read as source; a
   new informal mutation path).
5. **MCP and reconciliation independently deliverable?** Yes — confirmed
   by prerequisite-list inspection in §8; neither names the other.
6. **Documentation suite sufficiently specified, not overscoped?** Yes —
   §5's table maps every required document onto an existing file or
   names the specific gap to fill; no new document outside the six named
   purposes is introduced.
7. **Documentation-quality acceptance criteria measurable?** Yes — §6
   replaces an unmeasurable historical comparison with a reproducible,
   concretely-itemised baseline protocol.
8. **Comparative trials fairly account for overhead?** Yes — §7's three
   corrections (Arm A inclusion, mandatory baseline, multi-task
   cumulative measurement) directly close the three gaps the corrective
   prompt named.
9. **Current versus proposed capabilities distinguished?** Yes — this
   ADR's own Context section re-confirms, by direct inspection, that no
   Phase 83-91(92) capability exists in `src/codecompass/` yet; nothing
   in §1-§8 claims otherwise.
10. **Every affected cross-reference consistent?** Checked via a
    project-wide grep sweep across every file this ADR's own commit
    touches for the string "Phase 8" and "Phase 9" after editing,
    confirming no stale old-numbering survives outside an explicit
    historical "old Phase N" citation. Recorded as a verification step
    in this same commit's own change list (`planning/CONTEXT.md`).

**Unresolved uncertainties, recorded honestly rather than resolved by
assertion**: (a) whether Phase 87's own documentation-schema format
should be YAML or a lighter inline convention is left to Phase 87's own
planning time, not pre-decided here; (b) whether `docs/reference/cli.md`
generation should be fully automatic or a validated-but-hand-reviewed
process is likewise left to Phase 87's own plan; (c) the exact number
and shape of Phase 90's successive-task sequence (how many tasks, how
related) is explicitly deferred to Phase 90's own planning time, per
`planning/v2-evaluation-methodology.md`'s own existing "what this
document does not do" discipline, unchanged by this amendment.

## Alternatives considered

- **Leave Phase 84's CLI-migration scope as "migrate everything" and
  rely on phase-planning-time judgement to narrow it.** Rejected: the
  corrective prompt's own risk framing ("large, unnecessary refactor...
  potentially bypassing established mutation controls") is a real,
  specific, structural risk identifiable now, not something to discover
  mid-implementation; narrowing it now costs nothing and removes a
  concrete hazard.
- **Keep Phase 88 merged and simply add more detail to its existing
  exit gate.** Rejected: no amount of added detail resolves the
  structural problem that MCP and reconciliation are independently
  testable and one should not block on the other's own implementation
  timeline or defect discovery — the corrective prompt's own explicit
  instruction to check "whether MCP and reconciliation are genuinely
  independently deliverable" cannot be satisfied by anything short of
  an actual split.
- **Treat Phase 80's correction count as "close enough" for Phase 87's
  baseline, with a caveat noted.** Rejected: the corrective prompt is
  explicit that inventing or stretching a historical estimate to support
  an improvement claim is not acceptable; a fresh, matched baseline is
  more work but is the only honest option when the historical measure
  was never designed for this comparison.
- **Renumber only the two split phases (88→88/89) and leave 89-91
  untouched, creating a numbering gap instead of a full shift.**
  Rejected: a gap would break this project's own established
  "docs/decisions.md documents real numbering gaps, never creates a new
  one casually" discipline (the existing `0044` gap is already flagged
  as a confirmed historical artefact, not a precedent to repeat) and
  would make every future cross-reference to "Phase 89/90/91" ambiguous
  against two different meanings across this project's own history.

## Consequences

- `planning/v2-roadmap.md` is amended: Phase 82/83 sections unchanged;
  Phase 84's deliverables/exit-gate narrowed and its architectural-
  changes section expanded with the formalised logical model; Phase 85
  section unchanged; Phase 86's architectural-changes section gains the
  placement-policy table and three named enforcement classes; Phase 87's
  deliverables/exit-gate gain the minimum-suite table, schema fields,
  and corrected baseline methodology; the old merged Phase 88 section is
  replaced with two new sections (88 — MCP, 89 — Reconciliation); the old
  Phase 89/90/91 sections are renumbered 90/91/92 with content otherwise
  unchanged; the dependency graph, adoption-levels table, and
  federation-compatibility review section are updated to match.
- `planning/ROADMAP.md`'s v2 table rows 84-91 are updated/renumbered to
  84-92.
- `planning/CONTEXT.md`'s current-phase and "next concrete step" sections
  record this ADR and the new numbering; "what was just completed" is
  updated.
- `planning/v2-evaluation-methodology.md` gains a second dated amendment
  (§7 above); title/cross-references renumbered Phase 89→90 throughout.
- `planning/v2-migration-assessment.md`'s phase-number cross-references
  are updated for the 88-split and the 89/90/91→90/91/92 shift; its
  substantive compatibility posture is unchanged.
- `planning/post-v2-cross-project-overlay-backlog.md`'s two phase-number
  citations are updated (reconciliation: Phase 88→89; release: Phase
  91→92); no stage, risk, or exit gate changes.
- `docs/decisions.md` gains a new `0085` row.
- `CHANGELOG.md` gains one `[Unreleased]` entry for this planning-only
  change.
- No `src/codecompass/` or `context-graph.db` change is made. No Phase
  82 artifact, ADR, retro, or audit record is edited. `decisions/0078`-
  `0084` are not edited.
- If a future phase's real evidence shows this ADR's own boundaries
  wrong (e.g. the 88/89 split, or the formalised logical model's own
  nine points), that phase's own plan supersedes the relevant part with
  a new numbered decision, per `CLAUDE.md` §2.
