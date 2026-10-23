# 0084. CodeCompass v2 roadmap realigns around knowledge-driven software development: a consolidated knowledge query API, self-curation, knowledge-placement review, and a schema-driven documentation compiler are inserted ahead of MCP; Phases 83-88 are resequenced to 83-91

## Status

Accepted (2026-10-23, direct user request — "CodeCompass Orchestrator —
v2 Strategic Roadmap Realignment"). Amends `decisions/0078` (the v2
repositioning), extends `decisions/0079`/`0080`/`0081` (unchanged in
their own content — this ADR does not reopen Phase 82's design or its
two corrective passes, `decisions/0082`/`0083`). Planning only: this ADR
authorises no implementation. Each phase it introduces or renumbers
still requires its own `CLAUDE.md` §1 plan file, scoped against evidence
current when it is actually next, exactly as `decisions/0078`'s own
Consequences section already established for Phases 83-88 and as every
prior phase in this project (Priority A's Phase 75/78 re-scoping being
the most load-bearing precedent) already requires.

## Context

**Verified current state, re-inspected this session, not assumed**:
`HEAD` is `33b1e39`, the terminal reconciliation commit of Phase 82's
final corrective pass — confirmed clean working tree, confirmed in sync
with `origin/main`. Phase 82 is `done`. **No Phase 83-88 plan file
exists** (`ls planning/phase-83-*.md` through `phase-88-*.md`: none
found) — `planning/v2-roadmap.md` records only roadmap-depth 10-point
summaries for each, explicitly deferring full planning until each phase
is actually next. **No MCP server, no knowledge-query API module, and no
documentation compiler exist anywhere in `src/codecompass/`** (confirmed
by directory listing and grep: the package contains `oracle.py`,
`knowledge_intermediate.py`, `graph.py`, `source_symbols.py`,
`git_topology.py`, `spec_docs.py`, `enrichment.py`,
`relation_enrichment.py`, `doc_mapping.py`, `sync.py`, `cli.py`, and
sibling modules — no `mcp.py`, no unifying `knowledge_api.py` or
equivalent). The existing `codecompass query` surface is a **set of
independent, per-feature sub-verbs** added incrementally across phases
(`vendors`, `vendor`, `symbol`, `skills`, `relations`, `topology`,
`source`, `source-symbol`, `render`), each walking `context-graph.db`
or `planning/knowledge/` directly in its own command function — there
is no shared, stable, typed interface between them. `knowledge
select-candidates`/`knowledge apply`/`doc-*` (Phase 81) and
`enrich select-candidates`/`enrich apply` (earlier phases) are a second,
separately-evolved CLI surface over the same underlying
`planning/knowledge/` files, not unified with the `query` sub-app.

The governing prompt for this phase ("CodeCompass Orchestrator — v2
Strategic Roadmap Realignment") explicitly instructs treating CodeCompass's
objective as **Knowledge-Driven Software Development**: project knowledge
should compound across development tasks, making software progressively
easier to understand, modify, verify, and maintain, while delivering
measurable benefit net of its own management overhead. It requires: (1)
preserving Phase 82's completed, independently-verified foundation and
the intended capabilities of Phases 83-88, adjusting only sequence and
scope; (2) one logical canonical knowledge system, with declared intent,
observed implementation, independently verified behaviour, and
unverified hypothesis kept genuinely distinct — never collapsed into a
score or auto-promoted on an agent's own say; (3) a reusable,
stable knowledge-query interface, consumed (not independently
reconstructed) by the future MCP server, documentation compiler, and
Wiki; (4) knowledge curation as part of ordinary development, dogfooded
against CodeCompass itself, with self-curation never becoming circular
self-verification; (5) a Knowledge Placement Policy plus AI-assisted,
advisory (never a hard, untestable gate) code-quality/placement review;
(6) a schema-driven documentation compiler producing professional,
reader-useful documentation from curated knowledge, not narrative
rewritten from itself; (7) measurable documentation-quality outcomes,
demonstrated first on CodeCompass's own README/doc set; (8) forward
compatibility with the deferred MCP server and MIT Wiki without making
either a prerequisite for useful CLI/documentation value; (9) net
development-efficiency measurement, strengthening Phase 86's existing
trial methodology; (10) a realigned, dependency-aware phase sequence.

**What already satisfies several of these requirements and is reused,
not rebuilt**:

- **The epistemic-distinction requirement (2) is already solved.**
  `decisions/0080`'s `derive_epistemic_profile` (INTENDED/OBSERVED/
  VERIFIED-per-scope/CONTESTED, each an independently computed read-time
  predicate, never a persisted field or collapsed score) is exactly the
  "intent vs. observation vs. verification, never conflated" model this
  governing prompt asks for. Nothing in this ADR touches it.
- **The oracle/contract/evidence substrate (requirement 2's
  "behavioural contracts, invariants and tests") already exists**:
  `src/codecompass/oracle.py`, `planning/contracts/<slug>/`, two
  corrective passes' worth of hardening (`decisions/0082`/`0083`).
  Reused unchanged.
- **The self-curation discipline's "independent evidence, never
  circular" requirement (4) already has a working precedent**: every
  agent-recorded observation in this project enters
  `planning/learnings/` or `planning/context-gaps/` as a *candidate*,
  promoted only by `knowledge-curator` triage against real evidence
  (`CLAUDE.md` §8) — the project has never once let an agent's own
  assertion become authoritative. The new self-curation phase (§3 below)
  operationalises this discipline against CodeCompass's own
  implementation specifically; it does not invent a new promotion
  mechanism.
- **The clean-room composition requirement (6) already has a working
  broker and isolation mechanism**: Phase 81B's
  `prepare_cleanroom_branch.py`/`verify_cleanroom_isolation.py`/
  `cleanroom_broker.py` (`decisions/0076`/`0077`), already used once for
  a full project-wide documentation reconstruction (Phase 80) and once
  for a topic-level pilot (Phase 79's amendments). The documentation
  compiler reuses this mechanism; it does not design a new isolation
  boundary.
- **The Wiki-compatibility requirement (8) is already a named,
  deferred item**: `planning/v2-roadmap.md`'s "Deferred scope" table
  already lists "Complete visual Contract Wiki" as deferred, with a
  textual/Markdown projection (Phase 81's rendering) explicitly in
  scope instead. Unchanged by this ADR.
- **The federation/cross-project forward-compatibility requirement is
  already handled**: `decisions/0079` already gates cross-project
  overlays as an explicitly-authorised-later, generic post-v2 track with
  its own three-layer model. This ADR does not reopen it, and confirms
  (§5 below) that the new phases introduced here do not narrow its
  future options.

**What is genuinely missing, and is this ADR's actual new content**:
requirement (3)'s consolidated knowledge-query API does not exist (the
`query` sub-verbs are independent, not a stable interface); requirement
(4)'s *CodeCompass-self* dogfooded curation loop does not exist as a
phase (the general learning lifecycle exists, but nothing yet runs it
systematically against CodeCompass's own implementation); requirement
(5)'s Knowledge Placement Policy and AI-assisted placement review do not
exist; requirement (6)'s schema-driven documentation compiler does not
exist (Phase 79/80/81B proved the clean-room *methodology* works, but
each run was a bespoke one-off, not a reusable, schema-configurable
compiler); and the old roadmap (`decisions/0078`, Phases 83-88) sequenced
MCP (old Phase 84) immediately after semantic assurance (Phase 83), with
no API-consolidation or documentation-generation phase anywhere — not
because the old roadmap ruled these out, but because the governing
prompt that produced it did not ask for them. This is new strategic
content, not a correction of an error in `decisions/0078`.

## Decision

### 1. Architecture: one logical knowledge model, unchanged physical storage, a new consolidating API

**No new canonical store is created.** Per the governing prompt's own
constraint ("do not mandate a new database or separate repository
without demonstrating its value") and this project's own
`conditional-generalisation.md` discipline (already applied at Phase
54c, 79, and twice during Phase 82's own corrective passes), the
physical storage stays exactly where it already is:

| Knowledge | Current physical home | Unchanged by this ADR |
|---|---|---|
| Mechanical source/symbol/dependency/doc-relation facts | `context-graph.db` (SQLite) | Yes |
| Project-local Observation/Evidence/Claim/Derivation/Decision/Requirement records | `planning/knowledge/<slug>/*.md` (YAML front matter + Markdown) | Yes |
| Behavioural contracts and oracle results | `planning/contracts/<slug>/*.yaml` | Yes |
| Architectural/design rationale | `decisions/*.md` (ADRs), `docs/architecture/**` | Yes |
| Generated project documentation | `docs/**`, `README.md`, `ai-docs/**` | Yes |

**What is new is a logical, typed knowledge model and one consolidating
read/traversal API in front of these stores** (Phase 84, §2 below) — a
library, not a database: it answers "what does this project know, and
how confident are we," by querying the existing stores through a common
set of typed record shapes, and is the single place new consumers
(self-curation, placement review, the documentation compiler, and,
later, MCP) go for this, instead of each re-deriving its own
`context-graph.db` SQL or its own `planning/knowledge/` YAML walk. This
directly answers the governing prompt's own instruction to "distinguish
a unified logical knowledge model from the physical storage technology"
— the model is unified; the storage is not, and does not need to be,
until real use (not assumed in advance) demonstrates a specific gap a
consolidating API cannot itself close. Externalising canonical knowledge
out of the repository entirely (a separate service, a different
database) is **evaluated and explicitly declined for v2** on the same
evidence standard: nothing about Phases 83-91 below requires it, and
`decisions/0079` §5's portable export format (JSON snapshot, schema-
versioned, consumable without a running `codecompass` process) already
gives any future externalisation path — Post-v2 Stage 1, not this ADR —
a defined target shape to build toward without pre-building it now.

**Consumers of the one logical model**, present and future, all behind
the same interface, never reconstructing their own knowledge-walking
logic: the existing `query`/`knowledge`/`enrich` CLI sub-verbs (migrated
onto it, not duplicated — Phase 84); `knowledge-curator`/`context-
evaluator`/`domain-skeptic` (already exist, already independent, reuse
the API rather than hand-rolled greps where the API covers the same
ground); the self-curation loop (Phase 85); the knowledge-placement
reviewer (Phase 86); the documentation compiler (Phase 87); the MCP
server (Phase 88); and, **only if and when separately authorised**, a
future Wiki and the Post-v2 cross-project overlay's Layer C mapping
traversal (`decisions/0079`) — the API's own traversal/query shape is
designed to be generic over "one project's knowledge" so a later
federated caller could target a different project's export without a
redesign, but this is a named forward-compatibility consideration for
Phase 84's own plan to keep in mind, not a federation capability built
now.

**Declared intent / observed implementation / independently verified
behaviour / unverified hypothesis** remain exactly `decisions/0080`'s
four independently-computed predicates (INTENDED/OBSERVED/VERIFIED-per-
scope/CONTESTED) — the API surfaces this profile per-record on request;
it does not add a fifth state, a confidence score, or any mechanism that
could let an unverified observation become an accepted requirement
without passing through the existing Decision/Requirement approval path
unchanged.

### 2. Phase 83 is unchanged; Phases 84-88 are newly inserted/merged; old Phases 86-88 are renumbered 89-91

Full roadmap-depth (10-point) detail for each new/renumbered phase is
written directly into `planning/v2-roadmap.md` by this same commit, not
duplicated at length here. Summary mapping:

| New # | Name | Relation to old roadmap (`decisions/0078`) |
|---|---|---|
| 83 | Semantic Change Assurance | **Unchanged** — same objective, dependencies, exit gate as the old Phase 83. Sequenced first, per the governing prompt's own explicit ordering, because it is the next-available, already-scoped demonstration of real assurance value on top of Phase 82's contract/oracle foundation, before any further infrastructure investment. |
| 84 | Consolidated Knowledge API and Query CLI | **New.** Did not exist in the old roadmap. Builds the typed read/traversal interface (§1 above) and migrates existing `query`/`knowledge`/`enrich` sub-verbs onto it. |
| 85 | Self-Curation and Knowledge-Quality Validation | **New.** Dogfoods CodeCompass's own knowledge-curation lifecycle against CodeCompass's own implementation, using Phase 84's API for traversal and Phase 83's oracle for any behavioural assertion that needs independent confirmation — never a self-assertion alone. |
| 86 | Knowledge-Placement and Code-Quality Review | **New.** The Knowledge Placement Policy (governing prompt §5's table) plus an AI-assisted, advisory placement/quality reviewer, layered on Phase 85's self-curation checks and reusing the `Finding`-with-`strict`-flag pattern `decisions/0082`/`0083` already hardened (strict only for mechanically testable violations; advisory/non-blocking for subjective judgments, per the governing prompt's own explicit constraint against untestable hard gates). |
| 87 | Documentation Schema and Knowledge-Compiled Documentation | **New.** The schema-driven documentation compiler, clean-room composition (reusing Phase 81B's broker unchanged), independent validation, and the first demonstrator — a regenerated CodeCompass README/doc set, measured against Phase 80's own prior human-correction history as a concrete before/after comparison point. |
| 88 | Agent Integration, MCP, and Incremental Knowledge/Documentation Reconciliation | **Merges old Phase 84 (Agent Integration and MCP) and old Phase 85 (Persistent Knowledge and Incremental Reconciliation)**, per the governing prompt's own §10 point 8 grouping them as one sequence step. Extended to also cover documentation reconciliation (a changed Claim invalidates not only dependent knowledge but the documentation section compiled from it), since Phase 87 now exists to make that extension meaningful. Old Phase 84/85's own objectives, reuse list, exit gates, and risks are preserved, not dropped — see `planning/v2-roadmap.md`'s new §88 for the full carried-forward detail. |
| 89 | Comparative Development Trials | **= old Phase 86**, renumbered only. Objective, arms, and exit gate unchanged; methodology (`planning/v2-evaluation-methodology.md`) amended per §4 below, not replaced. |
| 90 | External Validation and Adoption | **= old Phase 87**, renumbered only. Unchanged. |
| 91 | v2.0 Hardening and Release | **= old Phase 88**, renumbered only. Unchanged, still gated on evidence and completion of every prior exit gate, never the nominal phase number. |

**Why insertion, not expansion-without-bound**: the governing prompt's
own §10 provides nine explicit sequence points; this table maps each
point to exactly one phase (87 absorbs points 5-7, which are tightly
coupled — a documentation compiler cannot be meaningfully validated or
demonstrated without being built first, so splitting them into separate
phases would create an artificial hand-off with no real intermediate
deliverable). Net phase count after 82: nine (83-91), not an open-ended
list — new phases are justified individually above, each against a
named governing-prompt requirement, not speculatively.

**None of Phases 83-91 is phase-planned by this ADR.** Each still
requires its own `planning/phase-N-*.md` under `CLAUDE.md` §1 before any
implementation begins, scoped against evidence current when it is
actually next — this ADR fixes the sequence and each phase's roadmap-
depth objective/reuse/deliverables/exit-gate, not its implementation
detail.

### 3. Self-curation is dogfooded, never circular

Phase 85's self-curation loop is explicitly bound by the same rule
already governing every other agent-recorded observation in this
project (`CLAUDE.md` §8): a candidate finding about CodeCompass's own
implementation — a stale Claim, a contradicted Requirement, a
placement defect — enters the existing `planning/learnings/`/
`planning/context-gaps/` lifecycle as a *candidate*; it becomes accepted
knowledge only through `knowledge-curator` triage against real,
independently checked evidence (a real grep, a real test run, a real
oracle result), exactly as every prior promotion in this project's
history already required. **A self-curation pass asserting "implementation
behaviour X is true" is never itself the evidence for X** — that
assertion must resolve to a real oracle result (Phase 83) or a real,
independently-reproduced observation, the same bar `decisions/0080`'s
VERIFIED predicate already enforces. No new exemption is created.

### 4. Evaluation methodology amendment: documentation quality and a concise-instructions baseline

`planning/v2-evaluation-methodology.md` gains two items the governing
prompt explicitly names in its §9 list that the existing methodology
(written for the old, MCP/reconciliation-first roadmap) did not yet
cover, added as a dated amendment to that file by this same commit, not
a rewrite of its existing arms/metrics:

- **Documentation quality and maintenance overhead** as its own metric,
  distinct from the existing "knowledge maintenance overhead" metric —
  Phase 87 is what makes this measurable at all; Arms B and C both now
  report it, Arm A does not (it has no CodeCompass-generated
  documentation to maintain).
- **A concise-repository-instructions baseline variant**, reported
  alongside the existing three arms rather than folded into Arm A: the
  same task attempted with only a short, hand-written instructions file
  (no CodeCompass knowledge, contracts, or MCP surface at all) — isolating
  whether CodeCompass's structured machinery earns its overhead over the
  cheapest plausible alternative, not only over nothing. This is a
  comparison point, not a fourth primary arm with its own full metric
  suite — the existing optional source-blind research arm's own "never a
  v2 release dependency" framing applies identically here.

Phase 86's own existing three-arm design, held-comparable conditions,
and pre-registration discipline are otherwise unchanged.

### 5. Post-v2 cross-project overlay track: confirmed unaffected

`decisions/0079`'s three-layer model, project-identity envelope, and
seven-stage backlog (`planning/post-v2-cross-project-overlay-backlog.md`)
are reviewed against this ADR's new phases (84-87) and found to need no
change: Phase 84's knowledge API is project-local by design (§1 above);
Phase 85's self-curation and Phase 86's placement review operate
entirely within one project's own Layer A knowledge; Phase 87's
documentation compiler consumes Layer A knowledge only. Phase 88's
"incremental knowledge/documentation reconciliation" (merged, §2 above)
is the same reconciliation surface the backlog's own invalidation rule
(`post-v2-cross-project-overlay-backlog.md`, "Invalidation" section)
already cites by reference to the old Phase 85 — that citation is
updated to the new Phase 88 number by this same commit, with no change
to the rule itself. The backlog's own "none blocks Phase 88's v2.0
release" sentence is updated to "Phase 91" for the same reason — a pure
renumbering, not a scope change.

## Alternatives considered

- **Sequence MCP (now Phase 88) immediately after Phase 83, as the old
  roadmap did, and treat the knowledge API/self-curation/placement-
  review/documentation-compiler work as internal implementation detail
  of Phase 88 rather than separate phases.** Rejected: each of these has
  its own falsifiable exit gate, its own genuinely distinct deliverable
  (a queryable API; a dogfooded curation record; a placement-review
  report; a generated, independently-validated documentation set), and
  the governing prompt's own §10 explicitly asks for the API and the
  documentation compiler to be built *before* MCP specifically so MCP
  consumes them rather than reconstructing equivalent logic inside the
  server. Folding them into Phase 88 would hide four genuinely separate
  pieces of value behind one phase's exit gate, the opposite of this
  project's own "falsifiable, narrow phase" discipline.
- **Build the consolidating knowledge API as a new database-backed
  service instead of a library over existing storage.** Rejected: no
  evidence yet that the existing file/SQLite split is a real bottleneck;
  the governing prompt itself warns against mandating new infrastructure
  without demonstrating its value, and `conditional-generalisation.md`'s
  own discipline applies here exactly as it has at every prior point
  this project faced the same kind of choice.
- **Leave the documentation compiler and knowledge-placement review as
  post-v2, deferred items**, since neither existed in the old roadmap
  at all. Rejected: the governing prompt's own §§5-7 treat these as core
  v2 essentials, not speculative extensions, and ties v2's own success
  criterion explicitly to documentation outcomes (§7) — deferring them
  would directly contradict the governing prompt this ADR exists to
  satisfy.
- **Renumber Phase 82's own two corrective passes or reopen
  `decisions/0080`/`0081` to retrofit the new API design into the
  already-shipped oracle/epistemic-profile code.** Rejected: nothing
  about this realignment requires it — Phase 82's shipped code becomes
  Phase 84's first, already-proven consumer of the pattern the new API
  generalises, not a defect to correct.

## Consequences

- `planning/v2-roadmap.md` is substantially rewritten by this same
  commit: Phase 82's summary is preserved verbatim; Phase 83's summary
  is preserved verbatim; new roadmap-depth sections are added for
  Phases 84-87; old Phase 84/85 content is merged into a new Phase 88
  section; old Phase 86/87/88 sections are renumbered 89/90/91 with
  their own content otherwise unchanged; the dependency graph, adoption-
  levels table, and federation-compatibility review section are updated
  to match.
- `planning/ROADMAP.md`'s "v2 — evidence-backed change assurance" table
  is updated: Phase 82's row is unchanged; a new row exists for each of
  83-91, each a one-line pointer to `planning/v2-roadmap.md`'s own
  detail (matching this file's own established convention for
  not-yet-phase-planned phases).
- `planning/CONTEXT.md`'s current-phase section records this ADR and the
  new phase numbering; "Next concrete step" is updated to confirm Phase
  83 (unchanged in content) is still next, with the new Phase 84-91
  sequence named for whoever picks up after it.
- `planning/v2-evaluation-methodology.md` gains a dated amendment (§4
  above) — its existing three-arm design, held-comparable conditions,
  and pre-registration discipline are not rewritten.
- `planning/v2-migration-assessment.md`'s phase-number cross-references
  (old 84/85/87/88) are updated to the new numbers (88/90/91); its
  substantive compatibility posture (additive-only through the knowledge
  API and documentation compiler, no `context-graph.db` migration, no
  existing CLI command removed) is unchanged and, if anything,
  strengthened — the new phases add new files/CLI surfaces, not new
  fields on existing canonical records.
- `planning/post-v2-cross-project-overlay-backlog.md`'s two phase-number
  cross-references are updated per §5 above; no stage, risk, or exit
  gate in that file changes.
- No `src/codecompass/` or `context-graph.db` change is made by this
  ADR. No Phase 82 artifact, ADR, retro, or audit record is edited.
  `decisions/0078`-`0083` are not edited.
- If a future phase's real evidence shows this ADR's own phase boundaries
  (e.g. Phase 86/87's split, or Phase 88's merge) are wrong, that
  phase's own plan supersedes the relevant part of this ADR with a new
  numbered decision, per `CLAUDE.md` §2's append-only convention — this
  ADR does not pre-commit the eventual implementation to its own current
  sequencing if real use says otherwise.
