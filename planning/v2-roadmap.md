# CodeCompass v2 — strategic roadmap (Phases 82-91)

Direct user request, 2026-10-21. Rationale, epistemic-dimension design,
and Priority A-F reconciliation: `decisions/0078`. This file is the
dependency-aware phase sequence and per-phase planning content required
before any Phase 82-91 implementation begins. **No implementation has
occurred under this file beyond Phase 82** — see `CLAUDE.md` §1: a phase
begins only once its own `planning/phase-N-*.md` exists, and no such
file exists yet for 83-91.

**Realigned 2026-10-23** (`decisions/0084`, "CodeCompass Orchestrator —
v2 Strategic Roadmap Realignment") around **Knowledge-Driven Software
Development**: Phase 82 and Phase 83 are unchanged; four new phases
(Consolidated Knowledge API, Self-Curation, Knowledge-Placement Review,
Documentation Compiler) are inserted ahead of Agent Integration/MCP,
which merges with the old Persistent-Knowledge-and-Reconciliation phase
and moves later in the sequence; the former Phases 86-88 are renumbered
89-91 with their own content unchanged. Full rationale, the old-to-new
phase mapping table, and the architecture decision to keep physical
storage unchanged behind one new consolidating API: `decisions/0084`.
This section replaces, not merely annotates, the prior version of this
file's Phase 84-88 content — the full historical text remains in git
history at the commit preceding this realignment.

**Honest baseline** (established by direct repository inspection before
writing the original version of this roadmap, re-confirmed at this
realignment): before Phase 82, no `src/codecompass/` module,
`pyproject.toml` dependency, or committed planning artifact implemented
or named a behavioural contract, an independent oracle, change-impact
analysis, or an MCP server. Phase 82 has since shipped a real contract/
oracle foundation (`decisions/0080`-`0083`). As of this realignment, no
`src/codecompass/` module implements a consolidated knowledge-query API,
a documentation compiler, or an MCP server — `decisions/0084`'s own
Context section confirms this by direct `grep`/directory-listing
inspection, not assumption. Nothing below claims any of Phases 83-91 as
already delivering v2 capabilities — each is a planned, not-yet-built
phase, named explicitly, reusing real existing foundations where named.

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
Phase 89's evidence says so (§ below).

## Adoption levels

| Level | Capability | v2 phases |
|---|---|---|
| 1 — Advisory | Knowledge retrieval, evidence tracing, context compilation, generated documentation | 82, 84, 87, 88 |
| 2 — Assurance (principal v2 product objective) | Change-impact evaluation, independent checks, assurance reports | 82, 83, 88 |
| 3 — Governed autonomy (optional, not a prerequisite for ordinary adoption) | Bounded workspaces, execution policies, routing — reuses Phase 81B's isolation mechanism only when actually exercised | 89's optional source-blind arm only |

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
    │  one typed read/traversal interface in front of context-graph.db +
    │  planning/knowledge/ + planning/contracts/ — unifies the model,
    │  not the storage (decisions/0084 §1)
    ▼
Phase 85 (Self-Curation and Knowledge-Quality Validation)
    │  dogfoods the learning/curation lifecycle against CodeCompass's
    │  own implementation, via 84's API and 83's oracle
    ▼
Phase 86 (Knowledge-Placement and Code-Quality Review)
    │  advisory placement/quality review layered on 85's checks
    ▼
Phase 87 (Documentation Schema and Knowledge-Compiled Documentation)
    │  schema-driven compiler, clean-room composition (reuses 81B's
    │  broker), independent validation, first demonstrator (own README)
    ▼
Phase 88 (Agent Integration, MCP, and Incremental Reconciliation) ──┐
    │  MCP server consumes 84's API + 83's impact analysis + 87's    │
    │  documentation surface; reconciliation now covers both          │
    │  knowledge and compiled documentation                           │
    ▼                                                                 │
Phase 89 (Comparative Development Trials)                            │
    │  needs 83/84/88 (knowledge+assurance+MCP) and 87 (documentation │
    │  quality metric) all genuinely operable                         │
    ▼                                                                 │
Phase 90 (External Validation and Adoption)                          │
    │  needs 89's evidence to know whether adoption is worth asking   │
    ▼                                                                 │
Phase 91 (v2.0 Hardening and Release) ◄───────────────────────────────┘
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

Not yet phase-planned. **New** (`decisions/0084` §1-2).

1. **Objective / value.** One stable, typed read/traversal interface
   over the project's existing knowledge — mechanical graph facts
   (`context-graph.db`), reconciled Observation/Evidence/Claim/
   Derivation/Decision/Requirement records (`planning/knowledge/`), and
   behavioural contracts/oracle results (`planning/contracts/`) —
   so every later consumer (self-curation, placement review, the
   documentation compiler, and eventually MCP) queries one interface
   instead of independently reconstructing `context-graph.db` SQL or a
   `planning/knowledge/` YAML walk. Also replaces the existing `query`/
   `knowledge`/`enrich` CLI sub-verbs' independent, per-feature logic
   with calls onto the new API, without removing or breaking any
   existing command's observable behaviour.
2. **Reused.** `knowledge_intermediate.py`'s existing record model and
   id-resolution helpers (`derive_provenance_label`,
   `derive_epistemic_profile`); `graph.py`'s existing `context-graph.db`
   access; `oracle.py`'s existing contract/result parsing; every
   existing `query`/`knowledge`/`enrich` command as the acceptance
   baseline the migrated versions must keep behaviourally compatible
   with.
3. **Architectural changes.** A new, logical knowledge model (typed
   record shapes spanning the three physical stores above) and a new
   consolidating module (name TBD at Phase 84 planning time) exposing:
   lookup by id/concept/source-symbol/requirement; relationship
   traversal with supporting evidence; contradiction/gap/staleness
   identification (reusing, not duplicating, `derive_epistemic_profile`
   and the existing `CONFLICT`/`contradicting_evidence` machinery);
   applicable architecture/contract/constraint retrieval; versioned,
   machine-readable export; bounded, evidence-backed context-packet
   compilation (reusing `knowledge-curator`'s existing packet-assembly
   mode, Phase 54c). **No `context-graph.db` schema change and no new
   database** — this is a library in front of existing storage, per
   `decisions/0084` §1's explicit architectural decision.
4. **Deliverables.** The API module; a stable CLI surface over it with
   machine-readable output suitable for a coding agent; existing `query`/
   `knowledge`/`enrich` commands migrated onto it (old command names and
   output shapes preserved — this phase is additive/refactoring, not
   breaking); deterministic-first design (LLM inference used only for
   genuinely semantic operations the API itself cannot resolve
   mechanically, per the governing prompt's own explicit preference).
5. **Prerequisites.** Phase 82 complete. Does not require Phase 83
   (sequenced after it per the governing prompt's own explicit
   ordering, not because of a hard dependency).
6. **Excluded.** MCP exposure (88, consumes this API rather than
   rebuilding it); any new persisted storage; Layer B/C federation
   constructs (`decisions/0079`) — the API's traversal shape should not
   *preclude* a future federated caller, but building federation support
   now is out of scope.
7. **Tests.** Behavioural-compatibility tests proving each migrated CLI
   command's observable output is unchanged for a representative input
   set; new tests for the API's own traversal/contradiction/gap
   detection against real `planning/knowledge/` and `context-graph.db`
   content (this project's own corpus, not a synthetic fixture only).
8. **Dogfood scenario.** The API is used, not merely built: at minimum,
   one real `query`/`knowledge` command is migrated end to end and shown
   to produce identical output to its pre-migration version against this
   project's own real data.
9. **Exit gate.** A fresh caller (a test, a script, or an agent) can
   answer "what does this project know about X, and how confident are
   we" through the one new interface alone, without reading
   `context-graph.db`'s schema or `planning/knowledge/`'s file layout
   directly — demonstrated, not merely asserted, against a real query.
10. **Risks.** Building an API that is a thin, redundant wrapper adding
    no real value over direct access — mitigated by requiring at least
    one genuinely new capability this phase delivers that no existing
    command already provides (contradiction/gap/staleness detection
    across record kinds, which no current `query` sub-verb does today).

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

Not yet phase-planned. **New** (`decisions/0084` §2).

1. **Objective / value.** Help coding agents and reviewers decide where
   information belongs (source comment vs. docstring vs. canonical
   knowledge vs. ADR vs. generated documentation), per the governing
   prompt's own Knowledge Placement Policy table, and flag the concrete
   defect patterns it names (architectural rationale embedded
   unnecessarily in code comments; undocumented requirements/invariants;
   contradictions with accepted decisions; duplicated/inconsistent
   knowledge; missing interface documentation; unnecessary abstractions).
2. **Reused.** The `Finding`-with-`strict`-flag pattern `decisions/0082`/
   `0083` already hardened in `check_contracts.py`/
   `check_knowledge_base.py` (mechanically testable violations are
   `strict`/blocking; everything else is informational/advisory);
   Phase 85's self-curation infrastructure; Phase 84's API for cross-
   referencing a comment's claim against canonical knowledge.
3. **Architectural changes.** A documented Knowledge Placement Policy
   (the governing prompt's own table, adapted to this project's actual
   artifact names); a new advisory review check combining deterministic
   rules (e.g. a comment citing a decision number that doesn't exist or
   contradicts the cited decision — mechanically checkable) with
   LLM-assisted semantic review for genuinely subjective judgments
   (verbosity, unnecessary abstraction) — **the semantic half is never
   `strict`/blocking** without an explicit, testable criterion backing
   it, per the governing prompt's own constraint.
4. **Deliverables.** The placement policy document; a placement/quality
   review runnable against a real diff or a real slice of the codebase;
   at least one real, previously-unflagged placement defect found and
   fixed in CodeCompass's own source as the dogfood proof.
5. **Prerequisites.** Phase 85.
6. **Excluded.** Any new mandatory verbosity/length rule; any change
   making an LLM judgment a merge-blocking gate on its own say.
7. **Tests.** A deliberately-constructed placement defect (e.g. an ADR-
   worthy rationale buried in a source comment) correctly flagged;
   a deliberately-constructed non-defect (ordinary, appropriately-scoped
   comment) correctly left unflagged — the false-positive control is as
   load-bearing as the true-positive one, matching this project's
   consistent discipline for every prior validator (`CLAUDE.md` §1
   L-070/L-075).
8. **Dogfood scenario.** The review run against CodeCompass's own
   `src/codecompass/` and `planning/knowledge/`.
9. **Exit gate.** At least one real placement defect in CodeCompass's
   own codebase is found and corrected as a direct result of this
   phase's review, with the false-positive control demonstrated clean.
10. **Risks.** Scope creep into a general code-style linter (explicitly
    not this phase's job — deterministic style/quality tooling already
    exists via `ruff`); subjective LLM judgment being mistaken for an
    objective gate — the governing prompt's own named risk, mitigated by
    §3's strict/advisory split.

## Phase 87 — Documentation Schema and Knowledge-Compiled Documentation

Not yet phase-planned. **New** (`decisions/0084` §2).

1. **Objective / value.** Professional project documentation — clear,
   concise, useful for its stated audience, not merely technically
   accurate Markdown — becomes an explicit, repeatable output of the
   canonical knowledge system, via a user-defined schema (documents,
   audiences, required sections, style/tone/verbosity, mandatory
   examples and acceptance criteria), not a one-off clean-room exercise
   repeated by hand each time.
2. **Reused.** Phase 81B's clean-room isolation and broker
   (`prepare_cleanroom_branch.py`/`verify_cleanroom_isolation.py`/
   `cleanroom_broker.py`) for independent composition, unchanged; Phase
   79/80's existing clean-room methodology (frozen snapshot → model-blind
   reconstruction → comparison → publication) as the compiler's own
   internal pipeline shape, now schema-driven and reusable rather than
   bespoke; `spec_docs.py`'s existing project-document tracking; Phase
   84's API for section→knowledge mapping and gap detection;
   `context-quality-evaluation.md`'s existing advantage-over-default-
   pathway rubric for the coding-context side of validation.
3. **Architectural changes.** A documentation-schema format (what to
   produce, for whom, with what required sections/style/examples); a
   compiler that maps schema sections to required knowledge, retrieves
   evidence/requirements/verified facts via Phase 84's API, identifies
   material knowledge gaps *before* writing, assembles bounded,
   section-specific context packets, composes each section through the
   existing clean-room broker, and validates factual grounding,
   structure, links, and executable examples before publication. **No
   second documentation knowledge store** — the compiler reads Phase
   84's API and `planning/knowledge/`; it does not cache or duplicate
   canonical facts into its own format.
4. **Deliverables.** The schema format and compiler; two documented
   modes — **clean reconstruction** (no access to existing narrative
   documentation, matching Phase 79/80's own model-blind discipline;
   legacy docs usable only as a gap detector, every candidate gap
   independently verified before acting on it) and **incremental
   maintenance** (updates affected sections after an accepted knowledge
   change, preserving approved human editorial improvements, never
   treating old prose as evidence of current implementation); a
   provenance mechanism available on demand without cluttering main
   prose (reusing Phase 81's existing `codecompass-grounded-by`-style
   marker convention); an editorial-quality assessment step distinct
   from factual-grounding validation.
5. **Prerequisites.** Phase 84 (knowledge API); Phase 86 (placement
   policy informs what belongs in generated documentation vs. elsewhere).
6. **Excluded.** A complete visual Wiki (already deferred,
   `v2-roadmap.md`'s own "Deferred scope" table — this phase produces
   Markdown/text documentation only); any change to canonical semantics
   from a presentation-only documentation edit (a documentation edit
   proposing a new *fact* enters the existing knowledge-reconciliation
   process exactly as Phase 81 already requires; a wording-only
   improvement does not touch canonical records, reusing Phase 81's
   existing presentation/semantics split).
7. **Tests.** A fail-closed check that factually-ungrounded generated
   prose is rejected before publication (the mechanism's own minimal-
   content edge case per `CLAUDE.md` §1 L-070 — an empty or near-empty
   knowledge base for a schema section must produce an explicit gap
   report, never fabricated filler); a real incremental-maintenance run
   that updates exactly the section affected by a real knowledge change
   and leaves unrelated sections untouched (the false-positive control).
8. **Dogfood scenario.** The required first demonstrator (§7 below,
   governing prompt's own requirement): a new README and small
   supporting documentation set for CodeCompass itself, generated from a
   user-defined schema and curated canonical knowledge, in clean-
   reconstruction mode.
9. **Exit gate.** The demonstrator meets the governing prompt's own
   acceptance bar, independently assessed: an unfamiliar developer can
   understand what CodeCompass does and why; install/quick-start
   instructions demonstrably work; current functionality is
   distinguished from future plans; technical claims trace to legitimate
   evidence; unsupported claims/contradictions are identified, not
   hidden; and the output requires **materially less human correction**
   than Phase 80's own prior clean-room reconstruction required (a
   concrete, already-recorded before/after comparison point — Phase 80's
   retro documents its own real correction count). Reader usefulness is
   assessed independently of, not instead of, factual correctness.
10. **Risks.** Producing an accurate-but-unhelpful "investigation report
    disguised as documentation" — the governing prompt's own named
    failure mode; mitigated by the explicit, separate editorial-quality
    assessment step (§4) and by excluding excessive provenance/
    implementation-history/internal-planning detail from the generated
    prose by construction (provenance stays available on demand, never
    inline in the main narrative).

## Phase 88 — Agent Integration, MCP, and Incremental Reconciliation

Not yet phase-planned. **Merges the old Phase 84 (Agent Integration and
MCP) and old Phase 85 (Persistent Knowledge and Incremental
Reconciliation)**, per the governing prompt's own §10 point 8; extended
to also cover documentation reconciliation now that Phase 87 exists
(`decisions/0084` §2).

1. **Objective / value.** An existing frontier coding agent (Claude Code
   first) completes a genuine Ledgerkit change using CodeCompass's
   knowledge, assurance, and generated documentation through a standard
   interface, not a bespoke workflow; a second genuine Ledgerkit task
   measurably benefits from knowledge (and now documentation) reconciled
   during the first.
2. **Reused.** Everything from 82-87; `knowledge_intermediate.py`'s
   existing reconciliation flow (the dual-hash anchor, the `CONFLICT`
   state) extended to trigger from source/test *changes*, not only
   manual projection edits; no new scheduler, no replacement for Claude
   Code's own harness (`CLAUDE.md` §8's "CodeCompass never spawns or
   coordinates agents" applies unchanged).
3. **Architectural changes.** A minimal, read-mostly MCP server built
   directly on Phase 84's knowledge API (contract retrieval, evidence/
   provenance tracing, impact assessment via Phase 83, context-packet
   compilation, oracle execution/result retrieval, gap reporting,
   documentation retrieval via Phase 87) — new dependency on an MCP
   library requires its own licence-compatibility check before adoption
   (GPL-3.0-or-later project); a change-detection trigger (source/test
   diff → affected-knowledge *and* affected-documentation-section
   invalidation) layered on the existing reconciliation flow — no
   general-purpose event bus or scheduler, matching `CLAUDE.md` §1's
   L-087 "observing a change differs from acting on it" discipline.
4. **Deliverables.** MCP tool surface, consuming Phase 84's API rather
   than reimplementing retrieval/traversal logic; adaptive task-specific
   context packets (reuses `context-quality-evaluation.md`'s existing
   rubric); stale-claim/contradiction/stale-documentation-section
   detection on real code change; targeted doc-impact identification
   (reuses `spec_docs.py` and Phase 87's own section→knowledge mapping);
   cross-phase provenance; a genuine Ledgerkit development task run
   through the MCP surface, followed by a second genuine Ledgerkit task
   that visibly benefits from knowledge reconciled from the first.
5. **Prerequisites.** Phase 84 (API), Phase 83 (impact analysis), Phase
   87 (documentation surface to reconcile).
6. **Excluded.** Any CodeCompass-specific agent orchestration beyond
   exposing existing capabilities as callable tools; local/offline model
   routing; a general-purpose event bus or scheduler for reconciliation
   triggers.
7. **Tests.** Protocol-contract tests against the MCP schema; a
   malicious/untrusted-content handling test (repository content and MCP
   responses treated as potentially untrusted instructions, never
   auto-executed); a real source change that should invalidate a
   specific prior Claim and/or documentation section, verified to
   actually do so; a source change that should *not* invalidate an
   unrelated Claim/section, verified to leave it alone (the false-
   positive control is as load-bearing as the true-positive one).
8. **Dogfood scenario.** Claude Code performs one real Ledgerkit change
   using only the MCP surface for CodeCompass context/assurance/
   documentation, then a second genuine Ledgerkit task where the
   agent's context packet visibly reflects knowledge reconciled from the
   first task's own real findings.
9. **Exit gate.** The agent completes a genuine development change using
   CodeCompass's context, independent assurance, and documentation
   through supported interfaces — not merely "the MCP server starts" —
   and the second task measurably benefits from the first, evidenced
   (e.g. a `context-evaluator` comparison against a control packet
   withholding the reconciled knowledge), not asserted.
10. **Risks.** Scope creep toward a second scheduler (the named failure
    mode this phase must actively resist); "measurably benefits" needing
    a concrete, pre-registered measurement defined before the second
    task runs, borrowing Phase 89's own methodology document rather than
    inventing a separate one.

## Phase 89 — Comparative Development Trials

**= old Phase 86, renumbered only; content unchanged.** Not yet
phase-planned. Full trial design (arms, metrics, controls, baseline
methodology): `planning/v2-evaluation-methodology.md`, amended
2026-10-23 (`decisions/0084` §4) to add a documentation-quality metric
and a concise-repository-instructions comparison baseline — the
existing three-arm design, held-comparable conditions, and
pre-registration discipline are unchanged.

1. **Objective / value.** Produce reproducible evidence on whether
   CodeCompass improves verified development outcomes net of total
   overhead — the central, falsifiable test of this roadmap's own
   governing hypothesis.
2. **Reused.** `context-quality-evaluation.md`'s "advantage over the
   default pathway" metric; Ledgerkit as the shared task substrate
   across all arms.
3. **Architectural changes.** None required beyond what 82-88 already
   deliver — this phase is evaluation, not new capability.
4. **Deliverables.** Three-arm comparison (conventional / knowledge-
   assisted / assurance-assisted) on comparable tasks, now also
   reporting documentation-quality/maintenance overhead and a
   concise-instructions comparison point; a reproducible report,
   published whether the result is positive, neutral, or negative.
5. **Prerequisites.** Phases 83, 84, 87, 88 all genuinely operable.
6. **Excluded.** Production source-blind coding (the optional arm is
   bounded/research-only, not a release dependency); any numeric
   improvement target set in advance of this phase's own baseline.
7. **Tests.** N/A in the usual code-test sense — the "test" is the trial
   protocol's own pre-registration discipline.
8. **Dogfood scenario.** The trial itself, against real Ledgerkit tasks.
9. **Exit gate.** Reproducible evidence, reported honestly including a
   neutral/negative outcome.
10. **Risks.** Confounding cost/ability differences between arms (model,
    task, baseline, oracle, tooling permissions, resource ceilings must
    be held comparable) — fixed in advance by
    `planning/v2-evaluation-methodology.md`.

## Phase 90 — External Validation and Adoption

**= old Phase 87, renumbered only; content unchanged.** Not yet
phase-planned.

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
   including the Phase 84-88 adoption levels once Level 2 is real
   enough to document honestly; documented supported/unsupported project
   types.
5. **Prerequisites.** Phase 89's evidence exists (positive, neutral, or
   negative — this phase still runs to validate adoption mechanics).
6. **Excluded.** Any commitment to the Haskell adapter specifically.
7. **Tests.** Reproducibility/compatibility checks on the external
   project; a fresh-session onboarding test.
8. **Dogfood scenario.** The external-project adoption itself.
9. **Exit gate.** An unfamiliar developer completes a real, evidence-
   backed, independently verified change in an independent repository.
10. **Risks.** Picking an external project for symbolic reasons rather
    than genuine adoption value.

## Phase 91 — v2.0 Hardening and Release

**= old Phase 88, renumbered only; content unchanged.** Not yet
phase-planned.

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
5. **Prerequisites.** Phase 90 complete.
6. **Excluded.** Any feature not already delivered by 83-90 — this phase
   hardens and ships, it does not add scope.
7. **Tests.** Full end-to-end regression across both repositories.
8. **Dogfood scenario.** The release process itself.
9. **Exit gate.** Gated on evidence and explicit completion of every
   prior exit gate — never on the nominal phase number alone.
10. **Risks.** Pressure to ship on schedule rather than evidence.

## Federation-compatibility review (amendment, 2026-10-21, `decisions/0079`; re-confirmed 2026-10-23, `decisions/0084` §5)

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
- **88 (Agent Integration, MCP, and Incremental Reconciliation)**:
  reviewed — the MCP tool surface is not designed around an implicit
  single-project assumption (each call already takes a project/
  workspace context implicitly). Forward-looking note unchanged from the
  original review: a future federated MCP capability would add a
  `project_id` parameter to existing calls rather than a parallel tool
  set. The reconciliation invalidation rule this phase carries forward
  from the old Phase 85 is the same rule
  `post-v2-cross-project-overlay-backlog.md`'s own "Invalidation" section
  cites by number — updated to Phase 88 by this realignment, with no
  change to the rule itself.
- **89 (Comparative Development Trials)**: reviewed — the existing
  three-arm design is unchanged. Cross-project overlay capability does
  not exist yet when this phase is expected to run and must not be
  introduced as an unmeasured, uncontrolled advantage in any arm.
- **90 (External Validation and Adoption)**: reviewed — independent
  adoption on a genuinely independent repository remains the primary
  gate, unchanged. Neither the Haskell adapter nor any cross-project
  overlay capability is required for this phase's exit gate.
- **91 (v2.0 Hardening and Release)**: reviewed — public interface
  stabilisation covers only what Phases 83-90 actually deliver. This
  phase's documentation must not describe federation/overlay
  capabilities as available, unchanged from the original review.

## Post-v2: Cross-Project Semantic Overlay track

**Explicitly gated, not part of the mandatory Phase 82-91 sequence.**
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

Per the original governing prompt's §5 and re-confirmed by the
2026-10-23 realignment's own governing prompt, each item below is
recorded as **deferred**. Revisit trigger is the same for all unless
noted: "Phase 89 evidence, or a specific post-v2 user request, shows
this item is now load-bearing for a real task."

| Item | Status | Note |
|---|---|---|
| Full Pi-local documentation generation | deferred | Local inference remains a legitimate post-v2 opportunity, not discarded. |
| Complete visual Contract Wiki | deferred | A textual/Markdown projection (Phase 87's compiler, reusing Phase 81's rendering) is in scope for 82-88; a *visual* interface is not. |
| Pi-local 3B model optimisation | deferred | No local/offline model is available in this environment today. |
| General-purpose DAG scheduling | deferred | Directly contradicts `CLAUDE.md` §8's "CodeCompass never spawns or coordinates agents" unless and until that fixed point itself is revisited. |
| Sophisticated hybrid model routing | deferred | No evidence yet that routing (vs. a single frontier model) is the bottleneck. |
| Predictive model allocation | deferred | Same as above. |
| Comprehensive autonomous workflow orchestration | deferred | Same `CLAUDE.md` §8 constraint as DAG scheduling. |
| Production source-blind coding | deferred, optional research arm only | Phase 89 may run a *bounded* research-only instance; never a v2 release dependency. |
| Full Haskell/hledger integration | deferred | Phase 90 explicitly does not assume the Haskell adapter is the first external proof. |
| Advanced commercial analytics | deferred | Out of scope for an open-source generic mechanism; preserved as a distinct, optional, externally-built layer. |
| Broad language adapters beyond what already exists | deferred | No new adapter work is in scope for Phases 83-91; a reference-project trial finding a real gap is the revisit trigger. |

## What this roadmap does not do

- It does not mark any Phase 83-91 row `done` — none has been
  implemented.
- It does not reopen or rewrite Phase 81, 81B, or Phase 82 (`done`).
- It does not commit to a numerical improvement target anywhere —
  `planning/v2-evaluation-methodology.md` defines measurement before any
  benchmark is run.
- It does not renumber, reopen, or weaken any Post-v2 Cross-Project
  Semantic Overlay stage's own exit gate (`decisions/0084` §5).
