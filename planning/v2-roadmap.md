# CodeCompass v2 — strategic roadmap (Phases 82-92)

Direct user request, 2026-10-21. Rationale, epistemic-dimension design,
and Priority A-F reconciliation: `decisions/0078`. This file is the
dependency-aware phase sequence and per-phase planning content required
before any Phase 82-92 implementation begins. **No implementation has
occurred under this file beyond Phase 82** — see `CLAUDE.md` §1: a phase
begins only once its own `planning/phase-N-*.md` exists, and no such
file exists yet for 83-92.

**Realigned 2026-10-23** (`decisions/0084`, "CodeCompass Orchestrator —
v2 Strategic Roadmap Realignment") around **Knowledge-Driven Software
Development**: Phase 82 and Phase 83 are unchanged; four new phases
(Consolidated Knowledge API, Self-Curation, Knowledge-Placement Review,
Documentation Compiler) are inserted ahead of Agent Integration/MCP,
which merges with the old Persistent-Knowledge-and-Reconciliation phase
and moves later in the sequence; the former Phases 86-88 are renumbered
89-91 with their own content unchanged.

**Corrected the same day** (`decisions/0085`, "CodeCompass Orchestrator —
Corrective Amendment to v2 Knowledge-Driven Development Roadmap"), after
re-verifying Phase 82/83 unchanged: Phase 84 gains an explicit, nine-
point logical knowledge model and a narrowed, read-only-first CLI scope;
Phase 86 gains a formal Knowledge Placement Policy table and three named
enforcement classes; Phase 87 gains a specified minimum documentation
suite, a versioned schema, and a corrected (no longer historically-
assumed) quality baseline; the merged Phase 88 is split back into an
MCP-only Phase 88 and a reconciliation-only Phase 89, since the two are
independently deliverable; the former Phases 89-91 are renumbered 90-92;
Phase 90's own evaluation methodology is strengthened (Arm A included in
documentation-quality measurement, the concise-instructions comparator
made mandatory for the principal conclusion, cumulative benefit measured
across a task sequence, not one task). Full rationale and both old-to-
new mapping tables: `decisions/0084`, `decisions/0085`. This section
replaces, not merely annotates, the prior versions of this file's Phase
84-91 content — the full historical text remains in git history at the
commits preceding each amendment.

**Honest baseline** (established by direct repository inspection before
writing the original version of this roadmap, re-confirmed at both
amendments): before Phase 82, no `src/codecompass/` module,
`pyproject.toml` dependency, or committed planning artifact implemented
or named a behavioural contract, an independent oracle, change-impact
analysis, or an MCP server. Phase 82 has since shipped a real contract/
oracle foundation (`decisions/0080`-`0083`). As of this latest amendment,
no `src/codecompass/` module implements a consolidated knowledge-query
API, a documentation compiler, or an MCP server — `decisions/0085`'s own
Context section reconfirms this by direct inspection of the real CLI
(`query`/`knowledge`/`enrich` remain three independent `typer.Typer()`
sub-apps with no shared interface), not assumption. Nothing below claims
any of Phases 83-92 as already delivering v2 capabilities — each is a
planned, not-yet-built phase, named explicitly, reusing real existing
foundations where named.

## Governing loop and objective

**Understand → Specify → Assess Impact → Implement → Verify →
Reconcile.** CodeCompass's job is steps 1, 2, 3, 5, and 6; step 4
(writing code) stays the coding agent's. Success is measured by
demonstrably improving the correctness, efficiency, and cumulative
maintainability of real software changes — not feature count,
orchestration complexity, graph size, or local-model usage. The central,
falsifiable hypothesis this whole roadmap tests (`decisions/0084`):
project knowledge should compound across development tasks, making
software progressively easier to understand, modify, verify, and
maintain, while delivering measurable benefit *after* accounting for its
own knowledge-management overhead — reported neutrally or negatively if
Phase 90's evidence says so (§ below).

## Adoption levels

| Level | Capability | v2 phases |
|---|---|---|
| 1 — Advisory | Knowledge retrieval, evidence tracing, context compilation, generated documentation | 82, 84, 87, 88 |
| 2 — Assurance (principal v2 product objective) | Change-impact evaluation, independent checks, assurance reports | 82, 83, 88 |
| 3 — Governed autonomy (optional, not a prerequisite for ordinary adoption) | Bounded workspaces, execution policies, routing — reuses Phase 81B's isolation mechanism only when actually exercised | 90's optional source-blind arm only |

## Dependency graph

```
Phase 82 (Contract and Evidence Foundation) — done
    │  behavioural contracts + oracle contract/result schema + pinned
    │  Ledgerkit scenarios — everything downstream cites a real contract
    ▼
Phase 83 (Semantic Change Assurance)
    │  first major value demonstration on top of 82's foundation,
    │  sequenced before further infrastructure investment
    ▼
Phase 84 (Consolidated Knowledge API and Query CLI)
    │  one typed, read-only traversal interface in front of
    │  context-graph.db + planning/knowledge/ + planning/contracts/ —
    │  unifies the model, not the storage (decisions/0084 §1, formalised
    │  decisions/0085 §1); CLI migration is incremental, not wholesale
    │  (decisions/0085 §2)
    ▼
Phase 85 (Self-Curation and Knowledge-Quality Validation)
    │  dogfoods the learning/curation lifecycle against CodeCompass's
    │  own implementation, via 84's API and 83's oracle
    ▼
Phase 86 (Knowledge-Placement and Code-Quality Review)
    │  advisory placement/quality review layered on 85's checks, per a
    │  formal Knowledge Placement Policy (decisions/0085 §4)
    ▼
Phase 87 (Documentation Schema and Knowledge-Compiled Documentation)
    │  schema-driven compiler, clean-room composition (reuses 81B's
    │  broker), independent validation, complete minimum documentation
    │  suite required at closeout (decisions/0085 §5-6)
    ▼
Phase 88 (Agent Integration and MCP)        Phase 89 (Incremental
    │  MCP server consumes 84's API +         Knowledge and Documentation
    │  83's impact analysis + 87's doc        Reconciliation)
    │  surface                                 │  change-detection trigger
    │                                           │  on 84's API + 87's doc
    │                                           │  surface — independent
    ▼                                           ▼  of MCP transport (0085 §3)
    └─────────────────┬──────────────────────────┘
                       ▼
Phase 90 (Comparative Development Trials)
    │  needs 83/84/87/88/89 (knowledge + assurance + MCP + documentation
    │  + reconciliation) all genuinely operable; methodology strengthened
    │  (decisions/0085 §7)
    ▼
Phase 91 (External Validation and Adoption)
    │  needs 90's evidence to know whether adoption is worth asking
    ▼
Phase 92 (v2.0 Hardening and Release)
```

No phase after 82 is scoped in `CLAUDE.md` §1 implementation-ready
detail here — each gets its own plan file, written against evidence
current when it is actually next, per `decisions/0062`'s own established
precedent (Priority A's scope was re-derived at Phase 75, not resumed
unchanged from Phase 48).

## Phase 82 — Contract and Evidence Foundation (done)

Full implementation-ready plan: `planning/phase-82-contract-and-
evidence-foundation.md`. Summary against the required 10-point
structure:

1. **Objective / value.** A behavioural contract (a specific Ledgerkit
   function's documented, versioned obligation) becomes a first-class,
   evidence-linked record that a check can pass or fail against — the
   foundation every later phase cites.
2. **Reused.** `knowledge_intermediate.py`'s Requirement/Claim record
   model, `source_files`/`source_symbols` (Phase 77), the real Ledgerkit
   sibling checkout, `context-evaluator`'s existing evidence-discipline
   conventions.
3. **Architectural changes.** No new field on any Claim/Requirement
   record — INTENDED/OBSERVED/VERIFIED/CONTESTED is a derived, read-time
   view (`decisions/0080`); a new, versioned, multi-check
   oracle-contract/oracle-result file schema under
   `planning/contracts/<slug>/`, with a deterministic PASS/FAIL/GAP/
   INVALID precedence rule (`decisions/0081`); no `context-graph.db`
   schema change.
4. **Deliverables.** See Phase 82 plan §3.
5. **Prerequisites.** None beyond this ADR's approval — Phase 82 is the
   dependency root.
6. **Sequence / excluded.** Excludes MCP exposure (88), change-impact
   traversal (83), and any multi-contract aggregate reporting (83).
7. **Tests.** Deterministic unit tests for schema validation (including
   a minimal-content/empty-contract edge case per `CLAUDE.md` §1 L-070),
   a demonstrably failing negative control against a real Ledgerkit
   function.
8. **Dogfood scenario.** One real, currently-true Ledgerkit behavioural
   contract (`ledgerkit/reports.py::balance_from_spec`).
9. **Exit gate.** A real Ledgerkit behavioural contract is traceable to
   its supporting evidence and independently testable, including a
   demonstrably failing negative control.
10. **Risks.** The oracle-result identity fields and the PASS/FAIL/GAP/
    INVALID aggregation rule are this phase's own genuinely novel design
    surface — specified in `decisions/0080`/`0081` and explicitly
    authorised for implementation by the same governing prompt that
    produced `decisions/0081`.

**Status: `done`.** Implemented, independently audited (PASS WITH
NON-BLOCKING OBSERVATIONS), two independent corrective passes
(`decisions/0082`/`0083`) fixed seven real assurance defects found by
two separate post-completion reviews, each independently re-audited to
PASS. Full detail: `planning/ROADMAP.md`'s own Phase 82 row.

## Phase 83 — Semantic Change Assurance

*First major value demonstration.* Not yet phase-planned; scoped here
at roadmap depth only. **Unchanged by the 2026-10-23 realignment** —
sequenced first because it is the next-available, already-scoped
demonstration of real assurance value on Phase 82's foundation, before
further infrastructure investment (`decisions/0084` §2).

1. **Objective / value.** Answer "what existing project obligations
   could this proposed change violate?" for a real, deliberately
   introduced Ledgerkit regression — the first point where CodeCompass
   demonstrably catches something the project's own ordinary test suite
   does not flag as a behavioural concern (distinct from "the tests
   fail," which the ordinary suite already reports).
2. **Reused.** Phase 82's contracts/oracle; `source_symbols`/
   `doc_relations_edges` for source-to-contract traceability;
   `git_topology.py` is not needed (no multi-repository change in
   scope).
3. **Architectural changes.** A new, generic source→contract impact
   traversal (reuses existing graph edges; does not introduce a new
   graph table unless Phase 82's real-use evidence shows a gap — a
   decision for Phase 83's own plan, not pre-committed here per
   `conditional-generalisation.md`'s discipline). Machine-readable
   (structured) and human-readable assurance report formats.
4. **Deliverables.** Impact-relationship derivation; PASS/FAIL/GAP/
   INVALID assurance-report outcome semantics (Phase 82's oracle-result
   schema extended, not replaced); protected acceptance/regression
   checks (a coding agent cannot edit the checks that will grade it).
5. **Prerequisites.** Phase 82 complete and approved `done`.
6. **Excluded.** MCP exposure (88); any model-routing or scheduling
   concept (explicitly deferred, §"Deferred scope" below); the
   consolidated knowledge API (84) — Phase 83 may use whatever ad hoc
   query path it needs and is not blocked waiting for 84.
7. **Tests.** The deliberately-introduced-regression scenario itself is
   the test; a false-negative control (an intentionally correct change
   must not be flagged FAIL); an incomplete-evidence control (GAP must
   be distinguishable from PASS, not silently rounded up).
8. **Dogfood scenario.** A deliberately introduced Ledgerkit semantic
   regression, missed by Ledgerkit's own ordinary feature-test baseline.
9. **Exit gate.** CodeCompass detects that regression without falsely
   claiming complete verification elsewhere in the same report.
10. **Risks.** Conflating "the diff touches this file" (structural) with
    "this contract is actually at risk" (semantic) — the same
    structural-proximity trap Priority A's own evidence (`L-026`,
    `CG-007`) already found and named; Phase 83's plan must address this
    directly, not inherit the gap silently.

## Phase 84 — Consolidated Knowledge API and Query CLI

Not yet phase-planned. **New** (`decisions/0084` §1-2); logical model
formalised and CLI scope narrowed (`decisions/0085` §1-2).

1. **Objective / value.** One stable, **read-only**, typed read/
   traversal interface over the project's existing knowledge —
   mechanical graph facts (`context-graph.db`), reconciled Observation/
   Evidence/Claim/Derivation/Decision/Requirement records (`planning/
   knowledge/`), and behavioural contracts/oracle results (`planning/
   contracts/`) — so every later consumer (self-curation, placement
   review, the documentation compiler, and eventually MCP) queries one
   interface instead of independently reconstructing `context-graph.db`
   SQL or a `planning/knowledge/` YAML walk. New knowledge search/
   retrieval/traversal/evidence/gap-query CLI operations are this
   phase's first deliverable; migrating any existing `query`/`knowledge`/
   `enrich` command onto the API is incremental and optional, decided
   command by command (`decisions/0085` §2), never a wholesale
   requirement.
2. **Reused.** `knowledge_intermediate.py`'s existing record model and
   id-resolution helpers (`derive_provenance_label`,
   `derive_epistemic_profile`); `graph.py`'s existing `context-graph.db`
   access; `oracle.py`'s existing contract/result parsing; every
   existing `query`/`knowledge`/`enrich` command as the acceptance
   baseline any migrated command must keep behaviourally compatible
   with; `decisions/0079` §5's existing schema-versioned portable-export
   shape, reused directly for this phase's own export format rather than
   inventing a second one.
3. **Architectural changes.** A new, logical knowledge model, formalised
   in full by `decisions/0085` §1: stable, project-qualified record and
   relationship identities (reusing existing `REQ-`/`CL-`/`EV-`/`OBS-`/
   `DE-`/`DEC-` ids and `context-graph.db`/oracle-contract ids, no new id
   scheme); an explicit canonical-vs-derived/presentation-only
   distinction (canonical: `context-graph.db`, `planning/knowledge/`,
   `planning/contracts/`, accepted ADRs; derived: rendered Markdown
   projections, the presentation cache, generated documentation);
   explicit authoritative sources per knowledge kind, with an ADR
   establishing intent only, never proving implementation behaviour on
   its own; exposure of existing source-revision/snapshot-identity/
   provenance fields (oracle content digests, frozen-snapshot commit
   SHAs, the presentation cache's dual hashes); `derive_epistemic_profile`
   reused unchanged for the four epistemic dimensions; exposure of
   existing contradiction/open-question/staleness fields
   (`contradicting_evidence`, `open_questions`, `unconfirmed_scopes`/
   `known_gap_scopes`), newly detectable *across* record kinds in one
   traversal; a consistently typed three-way response shape
   (result / empty / gap) for missing or insufficient knowledge;
   versioned, machine-readable export targeting `decisions/0079` §5's
   existing portable-snapshot schema. **The API has no mutation path at
   all** — `knowledge apply`, `enrich apply`, `doc-acknowledge-*`, and
   `oracle.py::accept_baseline` remain the only ways to write, unchanged
   and unreachable through this API (`decisions/0085` §1 point 7). **No
   `context-graph.db` schema change and no new database** — this is a
   read-only library in front of existing storage, per `decisions/0084`
   §1's architectural decision, confirmed not reopened by `decisions/
   0085`.
4. **Deliverables.** The API module; new CLI operations for knowledge
   search, retrieval, traversal, evidence-tracing, and gap-querying,
   with machine-readable output suitable for a coding agent; any
   existing command migrated onto the API only where doing so
   demonstrably removes duplicated logic (case by case, not mandated);
   deterministic-first design (LLM inference used only for genuinely
   semantic operations the API itself cannot resolve mechanically).
5. **Prerequisites.** Phase 82 complete. Does not require Phase 83
   (sequenced after it per the governing prompt's own explicit
   ordering, not because of a hard dependency).
6. **Excluded.** MCP exposure (88, consumes this API rather than
   rebuilding it); any new persisted storage; any knowledge-mutation
   capability (explicitly structural, `decisions/0085` §1 point 7, not
   merely a stated intention); wholesale migration of every existing
   `query`/`knowledge`/`enrich` command; Layer B/C federation constructs
   (`decisions/0079`) — the API's traversal shape should not *preclude* a
   future federated caller, but building federation support now is out
   of scope.
7. **Tests.** Backward-compatibility tests for any command that *is*
   migrated (identical observable output against a representative input
   set); explicit negative-path tests for every new API operation (a
   malformed query, a non-existent id, a traversal with no results —
   each must return the defined empty/gap/error shape, never silently
   collapse into another); new tests for the API's own traversal/
   contradiction/gap detection against real `planning/knowledge/` and
   `context-graph.db` content (this project's own corpus, not a
   synthetic fixture only).
8. **Dogfood scenario.** The API is used, not merely built, against this
   project's own real corpus: a consumer retrieves a real architectural
   decision, `balance-from-spec`'s associated implementation facts, its
   real Phase 82 contract, its provenance, and any verification
   limitation, all through the one interface — and the response
   distinguishes, for this real case, approved intent from verified
   implementation (`decisions/0085` §1's required acceptance criteria).
9. **Exit gate.** A fresh caller (a test, a script, or an agent) can
   answer "what does this project know about X, and how confident are
   we" through the one new interface alone, without reading
   `context-graph.db`'s schema or `planning/knowledge/`'s file layout
   directly — demonstrated, not merely asserted, against a real query —
   and §8's dogfood scenario succeeds without MCP existing.
10. **Risks.** Building an API that is a thin, redundant wrapper adding
    no real value over direct access — mitigated by requiring at least
    one genuinely new capability this phase delivers that no existing
    command already provides (contradiction/gap/staleness detection
    across record kinds, which no current `query` sub-verb does today),
    and by the dogfood scenario's own real-corpus proof requirement
    (`decisions/0085` §2).

## Phase 85 — Self-Curation and Knowledge-Quality Validation

Not yet phase-planned. **New** (`decisions/0084` §2-3).

1. **Objective / value.** CodeCompass develops an accurate, queryable
   understanding of its own implementation, architecture, behavioural
   obligations, and limitations — the "dogfood this workflow against
   CodeCompass itself" requirement — using ordinary development
   investigation as the source of new knowledge candidates, not a
   separate research exercise.
2. **Reused.** The existing learning/context-gap lifecycle
   (`planning/learnings/`, `planning/context-gaps/`,
   `learning-lifecycle.md`); `knowledge-curator`'s existing promote/
   retain/merge/discard discipline; Phase 84's API for traversal; Phase
   83's oracle for any claim about CodeCompass's own behaviour that
   needs independent confirmation.
3. **Architectural changes.** None to canonical storage. A new,
   repeatable self-curation *procedure* (not a new record kind): a
   development task surfaces a candidate observation about CodeCompass's
   own implementation exactly as it already would for an external
   reference project; the candidate enters the existing lifecycle;
   promotion requires the same independent-evidence bar every other
   promotion in this project's history already requires
   (`decisions/0084` §3 — explicitly never "the self-curation agent said
   so").
4. **Deliverables.** A demonstrated, repeatable self-curation pass
   against a real, bounded slice of CodeCompass's own `planning/
   knowledge/` corpus (candidates found, triaged, a nonzero number
   promoted with real independent evidence, at least one declined with
   a recorded reason); a knowledge-quality validation check (staleness/
   contradiction detection via Phase 84's API) runnable on demand, not
   only during a dedicated phase.
5. **Prerequisites.** Phase 84's API.
6. **Excluded.** Any change to the promotion bar itself (no new,
   weaker, self-curation-specific exemption); full-project continuous
   background curation (this phase demonstrates the loop works on a
   bounded slice, it does not commit to running it on every commit).
7. **Tests.** A real candidate finding independently verified true and
   promoted; a real candidate finding independently checked and found
   false or unsupported, declined with a recorded reason (the negative
   control — self-curation must be shown capable of saying no to
   itself, not only yes).
8. **Dogfood scenario.** The self-curation pass itself, against
   CodeCompass's own `planning/knowledge/` and `src/codecompass/`.
9. **Exit gate.** At least one real, previously-unrecorded fact about
   CodeCompass's own implementation is correctly promoted into canonical
   knowledge with independent evidence, and at least one candidate is
   correctly declined — both via the existing, unmodified promotion
   lifecycle.
10. **Risks.** Circularity (an agent's self-report being mistaken for
    verification) — the single named risk the governing prompt itself
    raises; mitigated structurally by requiring every promoted self-
    curation finding to cite the same kind of independent evidence
    (a real oracle result, a real reproduced grep/test, a human
    confirmation) every other promotion in this project already
    requires, never the self-curation pass's own narrative alone.

## Phase 86 — Knowledge-Placement and Code-Quality Review

Not yet phase-planned. **New** (`decisions/0084` §2); enforcement classes
and placement-policy table formalised (`decisions/0085` §4).

1. **Objective / value.** Help coding agents and reviewers decide where
   information belongs, per a formal Knowledge Placement Policy, and
   flag concrete defect patterns (architectural rationale embedded
   unnecessarily in code comments; undocumented requirements/invariants;
   contradictions with accepted decisions; missing interface
   documentation; unnecessary abstractions). **Placement is never
   interpreted as "appears only once"** — a critical invariant may
   legitimately live in a comment, a contract, and documentation at once
   with one consistent meaning; this phase flags inconsistency, not
   repetition.
2. **Reused.** The `Finding`-with-`strict`-flag pattern `decisions/0082`/
   `0083` already hardened in `check_contracts.py`/
   `check_knowledge_base.py`; Phase 85's self-curation infrastructure;
   Phase 84's read-only API for cross-referencing a comment's claim
   against canonical knowledge; this project's own existing comment
   discipline (comment only when the WHY is non-obvious) as the
   placement rule for the "non-obvious local comments" category below,
   not a new rule.
3. **Architectural changes.** A documented Knowledge Placement Policy
   mapping eight categories onto this project's real artifacts:
   implementation logic → `src/codecompass/*.py`; interface
   documentation/docstrings → module/function docstrings; non-obvious
   local comments → inline comments; architectural rationale/approved
   decisions → `decisions/*.md`; behavioural requirements/invariants →
   `planning/knowledge/<slug>/` Requirement records and `planning/
   contracts/<slug>/` oracle contracts; verification evidence →
   `planning/contracts/<slug>/*.yaml` results and Evidence records;
   human-oriented project documentation → `docs/**`/`README.md`/
   `ai-docs/**`; historical design context → `decisions/*.md`/`planning/
   retros/`. Three named enforcement classes (`decisions/0085` §4):
   **mechanical** (deterministic, independently reproducible — e.g. a
   comment citing a nonexistent or contradicted `decisions/NNNN` —
   strict/blocking where policy requires); **behavioural** (a violation
   demonstrated via an accepted executable contract or real oracle
   result); **semantic/editorial** (LLM-assisted verbosity/abstraction/
   placement judgment — **always advisory** unless converted into an
   independently testable requirement). **A prose contradiction with an
   accepted ADR is never classified mechanically proven merely because
   an LLM judges it contradictory** — that is semantic/editorial by
   construction unless a real, citable mechanical check backs it.
4. **Deliverables.** The placement policy document; a placement/quality
   review runnable against a real diff or a real slice of the codebase;
   at least one real, previously-unflagged placement defect found and
   fixed in CodeCompass's own source as the dogfood proof.
5. **Prerequisites.** Phase 85.
6. **Excluded.** Any new mandatory verbosity/length rule; any change
   making an LLM judgment a merge-blocking gate on its own say; treating
   placement policy as a single-location-only rule (§1 above).
7. **Tests.** A deliberately-constructed placement defect (e.g. an
   ADR-worthy rationale buried in a source comment) correctly flagged;
   **two** negative controls — an ordinary, appropriately-scoped comment
   correctly left unflagged, **and** a real or constructed example where
   extensive implementation comments are legitimately appropriate (e.g.
   `oracle.py`'s own non-obvious subprocess/digest-handling comments)
   also correctly left unflagged — both as load-bearing as the
   true-positive case, matching this project's consistent discipline for
   every prior validator (`CLAUDE.md` §1 L-070/L-075).
8. **Dogfood scenario.** The review run against CodeCompass's own
   `src/codecompass/` and `planning/knowledge/`.
9. **Exit gate.** At least one real placement defect in CodeCompass's
   own codebase is found and corrected as a direct result of this
   phase's review, with both false-positive controls demonstrated clean.
10. **Risks.** Scope creep into a general code-style linter (explicitly
    not this phase's job — deterministic style/quality tooling already
    exists via `ruff`); subjective LLM judgment being mistaken for an
    objective gate, or a legitimate multi-location invariant being
    mistaken for duplication — both mitigated by §3's three-class split
    and §1's explicit "not single-location" clarification.

## Phase 87 — Documentation Schema and Knowledge-Compiled Documentation

Not yet phase-planned. **New** (`decisions/0084` §2); minimum suite,
schema, and baseline methodology specified (`decisions/0085` §5-6).

1. **Objective / value.** Professional project documentation — clear,
   concise, useful for its stated audience, not merely technically
   accurate Markdown — becomes an explicit, repeatable output of the
   canonical knowledge system, via a user-defined, versioned schema
   (audience, purpose, required sections, depth/verbosity, tone/style,
   required examples, evidence requirements, acceptance criteria —
   Diátaxis as a default reference shape, not a mandatory structure), not
   a one-off clean-room exercise repeated by hand each time.
2. **Reused.** Phase 81B's clean-room isolation and broker
   (`prepare_cleanroom_branch.py`/`verify_cleanroom_isolation.py`/
   `cleanroom_broker.py`) for independent composition, unchanged; Phase
   79/80's existing clean-room methodology (frozen snapshot → model-blind
   reconstruction → comparison → publication) as the compiler's own
   internal pipeline shape, now schema-driven and reusable rather than
   bespoke; `spec_docs.py`'s existing project-document tracking; Phase
   84's read-only API for section→knowledge mapping and gap detection;
   `context-quality-evaluation.md`'s existing advantage-over-default-
   pathway rubric for the coding-context side of validation; this
   project's existing filenames/directory conventions, retained where
   they already serve the required purpose (`decisions/0085` §5).
3. **Architectural changes.** A versioned documentation-schema format; a
   compiler pipeline (`decisions/0085` §5): retrieve accepted knowledge
   through Phase 84's API only → resolve relevant evidence → map
   knowledge to required schema sections → identify material gaps
   *before* writing → generate bounded, section-specific knowledge
   packets → compose each section through the existing clean-room broker
   → independently validate technical claims and executable examples →
   assess usefulness/clarity/audience suitability as a step distinct
   from factual validation → preserve provenance on demand without
   cluttering ordinary prose. **No second documentation knowledge
   store** — the compiler reads Phase 84's API and `planning/knowledge/`
   only; it does not cache or duplicate canonical facts.
4. **Deliverables.** The schema format and compiler; two documented
   modes — **clean reconstruction** (no access to existing narrative
   documentation, matching Phase 79/80's own model-blind discipline;
   legacy docs usable only as a gap detector, every candidate gap
   independently verified before acting on it) and **incremental
   maintenance** (*manually triggered* updates to affected sections after
   an accepted knowledge change, preserving approved human editorial
   improvements, never treating old prose as evidence of current
   implementation — change-*driven*, automatic maintenance is Phase 89's
   own distinct capability, not required here); a provenance mechanism
   available on demand (reusing Phase 81's `codecompass-grounded-by`-
   style marker convention); an editorial-quality assessment step
   distinct from factual-grounding validation. **The complete minimum
   publication suite is required at closeout** (`decisions/0085` §5):
   README.md (problem, value, capabilities, installation, first steps);
   Getting Started (`docs/getting-started.md`, a tested tutorial);
   Concepts (`docs/concepts/*.md`, extended with an explicit page on
   epistemic distinctions and the reconciliation loop — a named gap, not
   assumed already covered); Architecture (`docs/architecture/
   overview.md`/`components.md`/`data-and-control-flow.md`); Reference
   (`docs/reference/cli.md`/`configuration.md`, generated deterministically
   where practical — currently hand-maintained, an improvement
   opportunity, not assumed solved); Contributor Guide
   (`CONTRIBUTING.md`/`docs/development/contributing.md`). The bounded
   first demonstrator (§8 below) stays README-plus-selected-support only;
   the full suite is a closeout requirement, not a demonstrator
   requirement.
5. **Prerequisites.** Phase 84 (knowledge API); Phase 86 (placement
   policy informs what belongs in generated documentation vs. elsewhere).
6. **Excluded.** A complete visual Wiki (already deferred); automatic,
   change-driven documentation maintenance (Phase 89); any change to
   canonical semantics from a presentation-only documentation edit
   (reusing Phase 81's existing presentation/semantics split, unchanged).
7. **Tests.** A fail-closed check that factually-ungrounded generated
   prose is rejected before publication (an empty or near-empty
   knowledge base for a schema section must produce an explicit gap
   report, never fabricated filler, per `CLAUDE.md` §1 L-070); a real
   manually-triggered incremental-maintenance run that updates exactly
   the section affected by a real knowledge change and leaves unrelated
   sections untouched (the false-positive control); an independent
   reader evaluation; at least one successful clean-environment
   onboarding exercise (`decisions/0085` §6, both now required, not
   optional).
8. **Dogfood scenario.** The required first demonstrator: a new README
   and small supporting documentation set for CodeCompass itself,
   generated from a user-defined schema and curated canonical knowledge,
   in clean-reconstruction mode; the complete minimum suite (§4) is then
   produced before closeout.
9. **Exit gate.** The demonstrator and full suite meet the governing
   prompt's own acceptance bar, independently assessed: an unfamiliar
   developer can understand what CodeCompass does and why; install/
   quick-start instructions demonstrably work; current functionality is
   distinguished from future plans; technical claims trace to legitimate
   evidence; unsupported claims/contradictions are identified, not
   hidden; the README does not resemble an audit report. **Documentation
   quality is measured against a reproducible baseline defined at this
   phase's own planning time** (`decisions/0085` §6) — matched
   requirements, pinned revisions, a fixed reader-task evaluation, an
   independent editorial rubric, technical-accuracy/grounding checks,
   tested installation/examples, correction count/severity, and human
   editing/review time — reusing Phase 80's own historical effort only if
   it can be reliably reconstructed against this standard, and running a
   fresh matched comparison instead if it cannot. **No historical effort
   estimate is invented and no improvement claim is made from
   incomparable measurements.** Reader usefulness is assessed
   independently of, not instead of, factual correctness.
10. **Risks.** Producing an accurate-but-unhelpful "investigation report
    disguised as documentation"; a generated README drifting toward this
    project's own dense, audit-log-style internal planning prose
    (`CONTEXT.md`/`ROADMAP.md`'s own style is explicitly not a template
    for reader-facing documents, `decisions/0085` §5) — both mitigated by
    the explicit, separate editorial-quality assessment step and by
    excluding excessive provenance/implementation-history/internal-
    planning detail from generated prose by construction.

## Phase 88 — Agent Integration and MCP

Not yet phase-planned. **Split from the old merged Phase 88** (which
itself merged old Phase 84/Agent-Integration-and-MCP and old Phase 85/
Persistent-Knowledge-and-Reconciliation, `decisions/0084` §2) **back into
an MCP-only phase, since MCP and reconciliation are independently
deliverable** (`decisions/0085` §3). Reconciliation is now Phase 89,
below.

1. **Objective / value.** An existing frontier coding agent (Claude Code
   first) completes a genuine Ledgerkit change using CodeCompass's
   knowledge, assurance, and generated documentation through a standard
   interface, not a bespoke workflow.
2. **Reused.** Everything from 82-87, consumed through Phase 84's API —
   this phase **must not duplicate** Phase 84's retrieval/traversal logic
   or Phase 83's impact-analysis logic inside the MCP server itself
   (`decisions/0085` §3's explicit constraint); no replacement for Claude
   Code's own harness (`CLAUDE.md` §8's "CodeCompass never spawns or
   coordinates agents" applies unchanged).
3. **Architectural changes.** A minimal, bounded, read-mostly MCP server
   built directly on Phase 84's knowledge API: contract retrieval,
   evidence/provenance tracing, context compilation, impact assessment
   via Phase 83, oracle execution/result retrieval (controlled
   verification execution, not arbitrary execution), gap reporting,
   documentation retrieval via Phase 87; permission and untrusted-content
   handling as a first-class design concern, not an afterthought; a new
   dependency on an MCP library requires its own licence-compatibility
   check before adoption (GPL-3.0-or-later project). No general-purpose
   event bus or scheduler.
4. **Deliverables.** MCP tool surface, consuming Phase 84's API and
   Phase 83's impact analysis rather than reimplementing them; adaptive
   task-specific context packets (reuses `context-quality-evaluation.md`'s
   existing rubric); permission/untrusted-content handling; a genuine
   Ledgerkit development task completed through the supported interface.
5. **Prerequisites.** Phase 84 (API), Phase 83 (impact analysis), Phase
   87 (documentation surface to retrieve).
6. **Excluded.** Any CodeCompass-specific agent orchestration beyond
   exposing existing capabilities as callable tools; local/offline model
   routing; a general-purpose event bus or scheduler; incremental
   reconciliation itself (Phase 89 — independently deliverable, not a
   prerequisite of this phase or vice versa).
7. **Tests.** Protocol-contract tests against the MCP schema; a
   malicious/untrusted-content handling test (repository content and MCP
   responses treated as potentially untrusted instructions, never
   auto-executed).
8. **Dogfood scenario.** Claude Code performs one real Ledgerkit change
   using only the MCP surface for CodeCompass context/assurance/
   documentation.
9. **Exit gate.** The agent completes a genuine development change using
   CodeCompass's context, independent assurance, and documentation
   through supported interfaces — not merely "the MCP server starts."
10. **Risks.** Scope creep toward reimplementing Phase 84/83's own logic
    inside the server instead of consuming it — the single named risk
    this phase must actively resist (`decisions/0085` §3).

## Phase 89 — Incremental Knowledge and Documentation Reconciliation

Not yet phase-planned. **Split from the old merged Phase 88** — this is
the reconciliation half, carrying forward the old Phase 85's full
original content (`decisions/0084` §2's merge, now un-merged by
`decisions/0085` §3). **Operates independently of MCP transport** — does
not require Phase 88.

1. **Objective / value.** A second genuine Ledgerkit development task
   measurably benefits from knowledge (and compiled documentation)
   reconciled during an earlier task, via source/test change detection
   that identifies affected canonical knowledge, reports staleness and
   conflicts explicitly, maps documentation sections to the knowledge
   they depend on, and invalidates/regenerates only the affected
   documentation — while preserving unrelated documents and accepted
   editorial changes.
2. **Reused.** `knowledge_intermediate.py`'s existing reconciliation flow
   (the dual-hash anchor, the `CONFLICT` state), extended to trigger from
   source/test *changes*, not only manual projection edits; `spec_docs.py`
   and Phase 87's own section→knowledge mapping for documentation-impact
   identification; Phase 84's read-only API for affected-knowledge
   lookup; no new scheduler.
3. **Architectural changes.** A change-detection trigger (source/test
   diff → affected-knowledge *and* affected-documentation-section
   invalidation) layered on the existing reconciliation flow — no
   general-purpose event bus or scheduler, matching `CLAUDE.md` §1's
   L-087 "observing a change differs from acting on it" discipline. This
   is the capability that upgrades Phase 87's own *manually triggered*
   incremental-maintenance mode into *change-driven* maintenance
   (`decisions/0085` §3's explicit distinction) — it does not replace or
   redesign Phase 87's compiler.
4. **Deliverables.** Stale-claim/contradiction/stale-documentation-
   section detection on a real code change; targeted doc-impact
   identification; section-to-knowledge dependency mapping; targeted
   documentation invalidation and regeneration; preservation of unrelated
   documents and accepted editorial changes; a demonstrated second
   genuine Ledgerkit task that visibly benefits from knowledge reconciled
   from an earlier one.
5. **Prerequisites.** Phase 84 (API), Phase 87 (documentation surface to
   reconcile). **Not Phase 88** — confirmed independently deliverable
   (`decisions/0085` §3/§8).
6. **Excluded.** The MCP surface itself (Phase 88); any general-purpose
   event bus or scheduler for reconciliation triggers; any change to
   Phase 87's own clean-reconstruction/manual-incremental-maintenance
   modes.
7. **Tests.** A real source change that should invalidate a specific
   prior Claim and/or documentation section, verified to actually do so;
   a source change that should *not* invalidate an unrelated Claim/
   section, verified to leave it alone (the false-positive control is as
   load-bearing as the true-positive one).
8. **Dogfood scenario.** One real Ledgerkit task, followed by a second
   genuine Ledgerkit task where the agent's context packet and
   documentation visibly reflect knowledge reconciled from the first
   task's own real findings — run through the ordinary CLI/API surface,
   not dependent on Phase 88's MCP server existing.
9. **Exit gate.** The second task measurably benefits from the first,
   evidenced (e.g. a `context-evaluator` comparison against a control
   packet withholding the reconciled knowledge), not asserted — achieved
   without any dependency on an MCP server.
10. **Risks.** "Measurably benefits" needing a concrete, pre-registered
    measurement defined before the second task runs, borrowing Phase
    90's own methodology document rather than inventing a separate one;
    conflating this phase's own change-driven trigger with Phase 87's
    already-shipped manual mode (named explicitly in §3 to prevent this).

## Phase 90 — Comparative Development Trials

**= old Phase 89 (itself old Phase 86, `decisions/0084`'s renumbering),
renumbered again by `decisions/0085` §8; methodology strengthened, not
replaced.** Not yet phase-planned. Full trial design (arms, metrics,
controls, baseline methodology): `planning/v2-evaluation-methodology.md`,
amended twice — 2026-10-23 (`decisions/0084` §4, a documentation-quality
metric and a concise-repository-instructions comparison baseline) and
again the same day (`decisions/0085` §7: Arm A is now included in
documentation-quality measurement rather than excluded; the
concise-instructions comparator is now mandatory for the principal
net-efficiency conclusion, not merely optional; cumulative benefit is
measured across a genuine sequence of successive tasks, not one task) —
the existing three-arm design, held-comparable conditions, and
pre-registration discipline are otherwise unchanged.

1. **Objective / value.** Produce reproducible evidence on whether
   CodeCompass improves verified development outcomes net of total
   overhead — the central, falsifiable test of this roadmap's own
   governing hypothesis.
2. **Reused.** `context-quality-evaluation.md`'s "advantage over the
   default pathway" metric; Ledgerkit as the shared task substrate
   across all arms.
3. **Architectural changes.** None required beyond what 82-89 already
   deliver — this phase is evaluation, not new capability.
4. **Deliverables.** Three-arm comparison (conventional / knowledge-
   assisted / assurance-assisted) on a successive sequence of comparable
   tasks, now also reporting documentation-quality/maintenance overhead
   for every arm including Arm A, and a mandatory concise-instructions
   comparison point run under equivalent conditions; a reproducible
   report, published whether the result is positive, neutral, or
   negative.
5. **Prerequisites.** Phases 83, 84, 87, 88, and **89** all genuinely
   operable — Phase 89 is newly required here (`decisions/0085` §8):
   measuring cumulative/subsequent-task knowledge reuse needs a real
   reconciliation capability to measure reuse against.
6. **Excluded.** Production source-blind coding (the optional arm is
   bounded/research-only, not a release dependency); any numeric
   improvement target set in advance of this phase's own baseline; the
   concise-instructions comparator counting as a v2 release dependency on
   its own, even though it is now mandatory for the principal conclusion.
7. **Tests.** N/A in the usual code-test sense — the "test" is the trial
   protocol's own pre-registration discipline.
8. **Dogfood scenario.** The trial itself, against a real sequence of
   Ledgerkit tasks.
9. **Exit gate.** Reproducible evidence, reported honestly including a
   neutral/negative outcome, with the mandatory concise-instructions
   comparison and Arm A's own documentation-outcome score both present
   in the report.
10. **Risks.** Confounding cost/ability differences between arms (model,
    task, baseline, oracle, tooling permissions, resource ceilings must
    be held comparable) — fixed in advance by
    `planning/v2-evaluation-methodology.md`.

## Phase 91 — External Validation and Adoption

**= old Phase 90 (itself old Phase 87), renumbered only; content
unchanged.** Not yet phase-planned.

1. **Objective / value.** An unfamiliar developer adopts CodeCompass on
   an independent repository and completes an evidence-backed,
   independently verified change.
2. **Reused.** `codecompass-template`; the agent-led adoption blueprint
   (`planning/v1-redefinition/adoption-blueprint.md`).
3. **Architectural changes.** Hardened MCP permission/security surface;
   CLI usability/failure-recovery passes — no new core capability.
4. **Deliverables.** A CodeCompass self-development trial; one genuinely
   independent external project validated (selected on value/maturity/
   cost at the time); updated `codecompass-template` onboarding,
   including the Phase 84-89 adoption levels once Level 2 is real
   enough to document honestly; documented supported/unsupported project
   types.
5. **Prerequisites.** Phase 90's evidence exists (positive, neutral, or
   negative — this phase still runs to validate adoption mechanics).
6. **Excluded.** Any commitment to the Haskell adapter specifically.
7. **Tests.** Reproducibility/compatibility checks on the external
   project; a fresh-session onboarding test.
8. **Dogfood scenario.** The external-project adoption itself.
9. **Exit gate.** An unfamiliar developer completes a real, evidence-
   backed, independently verified change in an independent repository.
10. **Risks.** Picking an external project for symbolic reasons rather
    than genuine adoption value.

## Phase 92 — v2.0 Hardening and Release

**= old Phase 91 (itself old Phase 88), renumbered only; content
unchanged.** Not yet phase-planned.

1. **Objective / value.** A reproducible, usable, model-neutral
   open-source change-assurance system, with demonstrated value beyond
   its own repository.
2. **Reused.** Existing release discipline (`CLAUDE.md` §6's milestone/
   tag convention, `v1-closeout.md`'s own closeout shape as a template).
3. **Architectural changes.** Public contract/MCP/knowledge-API/
   assurance-result interface stabilisation and versioning (see
   `planning/v2-migration-assessment.md`); no new capability.
4. **Deliverables.** Migration/compatibility arrangements; security and
   isolation review; end-to-end regression; documentation/packaging;
   template compatibility; published benchmark methodology and results;
   explicit known limitations; release-readiness review.
5. **Prerequisites.** Phase 91 complete.
6. **Excluded.** Any feature not already delivered by 83-91 — this phase
   hardens and ships, it does not add scope.
7. **Tests.** Full end-to-end regression across both repositories.
8. **Dogfood scenario.** The release process itself.
9. **Exit gate.** Gated on evidence and explicit completion of every
   prior exit gate — never on the nominal phase number alone.
10. **Risks.** Pressure to ship on schedule rather than evidence.

## Federation-compatibility review (amendment, 2026-10-21, `decisions/0079`; re-confirmed 2026-10-23, `decisions/0084` §5 and `decisions/0085` §8)

Direct user request to review this roadmap for future compatibility with
a generic cross-project semantic overlay capability, without renumbering,
expanding, or weakening any existing exit gate. **None of the phases
below changes scope, sequence, or exit gate as a result of this
review** — each entry records the review finding, and a forward-looking
note where one is needed. Full overlay design: `decisions/0079`; full
stage sequence: `planning/post-v2-cross-project-overlay-backlog.md`.

- **82 (Contract and Evidence Foundation)**: reviewed — contract
  identity (`REQ-`/`CL-`/`EV-` IDs) and evidence references stay
  project-local and need no change; federation identity is carried
  externally by a project-identity envelope (`decisions/0079` §2,
  extended by `decisions/0080` §3). Unchanged by this realignment.
- **83 (Semantic Change Assurance)**: reviewed — impact traversal stays
  project-local by design. Unchanged by this realignment.
- **84 (Consolidated Knowledge API and Query CLI)**: reviewed — the API
  is project-local by design (`decisions/0084` §1); its traversal shape
  should not preclude a future federated caller targeting a different
  project's export, but this is a forward-compatibility consideration
  for Phase 84's own plan, not a capability built now.
- **85 (Self-Curation and Knowledge-Quality Validation)**: reviewed —
  operates entirely within one project's own Layer A knowledge; no
  federation surface.
- **86 (Knowledge-Placement and Code-Quality Review)**: reviewed — same
  as 85.
- **87 (Documentation Schema and Knowledge-Compiled Documentation)**:
  reviewed — consumes Layer A knowledge only; a future federated Wiki
  (post-v2) would reuse this phase's compiler's own validation
  discipline, not its canonical knowledge, matching the Wiki's own
  "read-only projection, never a fourth canonical store" constraint
  (`decisions/0079` §1).
- **88 (Agent Integration and MCP)**: reviewed — the MCP tool surface is
  not designed around an implicit single-project assumption (each call
  already takes a project/workspace context implicitly). Forward-looking
  note unchanged from the original review: a future federated MCP
  capability would add a `project_id` parameter to existing calls rather
  than a parallel tool set.
- **89 (Incremental Knowledge and Documentation Reconciliation)**:
  reviewed — operates entirely within one project's own Layer A
  knowledge; no federation surface. The reconciliation invalidation rule
  this phase carries forward from the old Phase 85 (via the old merged
  Phase 88) is the same rule `post-v2-cross-project-overlay-backlog.md`'s
  own "Invalidation" section cites by number — updated to Phase 89 by
  this amendment, with no change to the rule itself.
- **90 (Comparative Development Trials)**: reviewed — the existing
  three-arm design is unchanged. Cross-project overlay capability does
  not exist yet when this phase is expected to run and must not be
  introduced as an unmeasured, uncontrolled advantage in any arm.
- **91 (External Validation and Adoption)**: reviewed — independent
  adoption on a genuinely independent repository remains the primary
  gate, unchanged. Neither the Haskell adapter nor any cross-project
  overlay capability is required for this phase's exit gate.
- **92 (v2.0 Hardening and Release)**: reviewed — public interface
  stabilisation covers only what Phases 83-91 actually deliver. This
  phase's documentation must not describe federation/overlay
  capabilities as available, unchanged from the original review.

## Post-v2: Cross-Project Semantic Overlay track

**Explicitly gated, not part of the mandatory Phase 82-92 sequence.**
CodeCompass should eventually support independently constructed project
knowledge models that can be overlaid and compared through explicit,
evidence-backed semantic relationships — generic capability, with
Ledgerkit/hledger/Ledger/Beancount (PTA) as the motivating, not
architecturally required, use case. Full design: `decisions/0079`. Full
seven-stage sequence (portable snapshot/identity proof → Ledgerkit/
hledger comparison → Ledger compatibility/differential verification →
backend-independent API implications → natural-language query model
implications → read-only federated Wiki visualisation → Beancount/
unrelated-domain generalisation trial), dependencies, risks, and each
stage's own falsifiable exit gate:
[`planning/post-v2-cross-project-overlay-backlog.md`](post-v2-cross-project-overlay-backlog.md).
No stage begins without its own future `CLAUDE.md` §1 plan file.

## Deferred scope (not lost, not silently absorbed)

Per the original governing prompt's §5 and re-confirmed by both the
2026-10-23 realignment and its same-day corrective amendment, each item
below is recorded as **deferred**. Revisit trigger is the same for all
unless noted: "Phase 90 evidence, or a specific post-v2 user request,
shows this item is now load-bearing for a real task."

| Item | Status | Note |
|---|---|---|
| Full Pi-local documentation generation | deferred | Local inference remains a legitimate post-v2 opportunity, not discarded. |
| Complete visual Contract Wiki | deferred | A textual/Markdown projection (Phase 87's compiler, reusing Phase 81's rendering) is in scope for 82-89; a *visual* interface is not. |
| Pi-local 3B model optimisation | deferred | No local/offline model is available in this environment today. |
| General-purpose DAG scheduling | deferred | Directly contradicts `CLAUDE.md` §8's "CodeCompass never spawns or coordinates agents" unless and until that fixed point itself is revisited. |
| Sophisticated hybrid model routing | deferred | No evidence yet that routing (vs. a single frontier model) is the bottleneck. |
| Predictive model allocation | deferred | Same as above. |
| Comprehensive autonomous workflow orchestration | deferred | Same `CLAUDE.md` §8 constraint as DAG scheduling. |
| Production source-blind coding | deferred, optional research arm only | Phase 90 may run a *bounded* research-only instance; never a v2 release dependency. |
| Full Haskell/hledger integration | deferred | Phase 91 explicitly does not assume the Haskell adapter is the first external proof. |
| Advanced commercial analytics | deferred | Out of scope for an open-source generic mechanism; preserved as a distinct, optional, externally-built layer. |
| Broad language adapters beyond what already exists | deferred | No new adapter work is in scope for Phases 83-92; a reference-project trial finding a real gap is the revisit trigger. |

## What this roadmap does not do

- It does not mark any Phase 83-92 row `done` — none has been
  implemented.
- It does not reopen or rewrite Phase 81, 81B, or Phase 82 (`done`), or
  change Phase 83's own agreed objective or exit criteria.
- It does not commit to a numerical improvement target anywhere —
  `planning/v2-evaluation-methodology.md` defines measurement before any
  benchmark is run.
- It does not renumber, reopen, or weaken any Post-v2 Cross-Project
  Semantic Overlay stage's own exit gate (`decisions/0084` §5,
  reconfirmed `decisions/0085` §8).
