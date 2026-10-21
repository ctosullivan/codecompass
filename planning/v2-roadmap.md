# CodeCompass v2 — strategic roadmap (Phases 82-88)

Direct user request, 2026-10-21. Rationale, epistemic-dimension design,
and Priority A-F reconciliation: `decisions/0078`. This file is the
dependency-aware phase sequence and per-phase planning content required
before any Phase 82-88 implementation begins. **No implementation has
occurred under this file** — see `CLAUDE.md` §1: a phase begins only
once its own `planning/phase-N-*.md` exists and, for 83-88, has not yet
been written.

**Honest baseline** (established by direct repository inspection before
writing this roadmap, not assumed from any prior document — none
existed): no `src/codecompass/` module, `pyproject.toml` dependency, or
committed planning artifact implements or names a behavioural contract,
an independent oracle, change-impact analysis, or an MCP server before
this file. `decisions/0062`'s Priority A-F framework is the closest
prior strategic content; Phase 81's intermediate-knowledge layer and
Phase 81B's clean-room isolation machinery are the closest prior
technical content. Nothing below claims those as already delivering v2
capabilities — they are reused foundations, named explicitly per phase.

## Governing loop and objective

**Understand → Specify → Assess Impact → Implement → Verify →
Reconcile.** CodeCompass's job is steps 1, 2, 3, 5, and 6; step 4
(writing code) stays the coding agent's. Success is measured by
demonstrably improving the correctness, efficiency, and cumulative
maintainability of real software changes — not feature count,
orchestration complexity, graph size, or local-model usage.

## Adoption levels

| Level | Capability | v2 phases |
|---|---|---|
| 1 — Advisory | Knowledge retrieval, evidence tracing, context compilation | 82, 84 |
| 2 — Assurance (principal v2 product objective) | Change-impact evaluation, independent checks, assurance reports | 82, 83, 84 |
| 3 — Governed autonomy (optional, not a prerequisite for ordinary adoption) | Bounded workspaces, execution policies, routing — reuses Phase 81B's isolation mechanism only when actually exercised | 86's optional source-blind arm only |

## Dependency graph

```
Phase 82 (Contract and Evidence Foundation)
    │  behavioural contracts + oracle contract/result schema + pinned
    │  Ledgerkit scenarios — everything downstream cites a real contract
    ▼
Phase 83 (Semantic Change Assurance)
    │  needs 82's contracts to know what a change could violate;
    │  needs 82's oracle schema to report verification gaps
    ▼
Phase 84 (Agent Integration and MCP) ──────┐
    │  needs 82+83's capabilities to expose │ Phase 85 can run concurrently
    │  something real over MCP              │ with 84 — both consume 82+83,
    ▼                                        │ neither depends on the other
Phase 85 (Persistent Knowledge and          │
Incremental Reconciliation) ◄───────────────┘
    │  needs 84's genuine dev-task evidence (first task) to have
    │  something to reconcile for the second task's benefit
    ▼
Phase 86 (Comparative Development Trials)
    │  needs 84 (knowledge-assisted arm) and 83 (assurance-assisted arm)
    │  both genuinely operable, and 85's reconciliation benefit measurable
    ▼
Phase 87 (External Validation and Adoption)
    │  needs 86's evidence to know whether there is anything worth
    │  asking an external developer to adopt
    ▼
Phase 88 (v2.0 Hardening and Release)
```

No phase after 82 is scoped in `CLAUDE.md` §1 implementation-ready
detail here — each gets its own plan file, written against evidence
current when it is actually next, per `decisions/0062`'s own established
precedent (Priority A's scope was re-derived at Phase 75, not resumed
unchanged from Phase 48).

## Phase 82 — Contract and Evidence Foundation

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
3. **Architectural changes.** New optional Claim/Requirement fields for
   the INTENDED/OBSERVED/VERIFIED/UNCERTAIN dimension (exact field name
   and enum proposed in the Phase 82 plan, pending maintainer approval);
   a new, minimal oracle-contract/oracle-result file schema under
   `planning/contracts/<slug>/`; no `context-graph.db` schema change.
4. **Deliverables.** See Phase 82 plan §3.
5. **Prerequisites.** None beyond this ADR's approval — Phase 82 is the
   dependency root.
6. **Sequence / excluded.** Excludes MCP exposure (84), change-impact
   traversal (83), and any multi-contract aggregate reporting (83).
7. **Tests.** Deterministic unit tests for schema validation (including
   a minimal-content/empty-contract edge case per `CLAUDE.md` §1 L-070),
   a demonstrably failing negative control against a real Ledgerkit
   function.
8. **Dogfood scenario.** One real, currently-true Ledgerkit behavioural
   contract (candidate: `ledgerkit/reports.py`'s `balance_from_spec`,
   already studied at Phase 78's trial — confirmed to exist by direct
   inspection of the sibling checkout this session).
9. **Exit gate.** A real Ledgerkit behavioural contract is traceable to
   its supporting evidence and independently testable, including a
   demonstrably failing negative control.
10. **Risks.** The INTENDED/OBSERVED/VERIFIED schema delta is the one
    genuinely novel design decision in this phase — named as requiring
    explicit maintainer approval before implementation (see this
    document's own closing section).

## Phase 83 — Semantic Change Assurance

*First major value demonstration.* Not yet phase-planned; scoped here
at roadmap depth only.

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
6. **Excluded.** MCP exposure (84); any model-routing or scheduling
   concept (explicitly deferred, §"Deferred scope" below).
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

## Phase 84 — Agent Integration and MCP

Not yet phase-planned.

1. **Objective / value.** An existing frontier coding agent (Claude
   Code first) completes a genuine Ledgerkit change using CodeCompass
   context and assurance through a standard interface, not a bespoke
   workflow.
2. **Reused.** Everything from 82/83; no new scheduler, no replacement
   for Claude Code's own harness (`CLAUDE.md` §8's "CodeCompass never
   spawns or coordinates agents" applies unchanged).
3. **Architectural changes.** A minimal, read-mostly MCP server
   (contract retrieval, evidence/provenance tracing, impact assessment,
   context-packet compilation, bounded context expansion, oracle
   execution/result retrieval, gap reporting) — new dependency on an MCP
   library requires its own licence-compatibility check before adoption
   (GPL-3.0-or-later project; confirm the chosen MCP SDK's licence is
   compatible before pinning it — named as a pre-implementation check,
   not assumed clear here).
4. **Deliverables.** MCP tool surface; adaptive task-specific context
   packets (reuses `context-quality-evaluation.md`'s existing rubric,
   not a new one); a genuine Ledgerkit development task run through it.
5. **Prerequisites.** Phase 83 complete.
6. **Excluded.** Any CodeCompass-specific agent orchestration beyond
   exposing existing capabilities as callable tools; local/offline
   model routing (explicitly deferred).
7. **Tests.** Protocol-contract tests against the MCP schema; a
   malicious/untrusted-content handling test (repository content and
   MCP responses must be treated as potentially untrusted instructions,
   never auto-executed as commands).
8. **Dogfood scenario.** Claude Code performs one real Ledgerkit change
   using only the MCP surface for CodeCompass context/assurance.
9. **Exit gate.** The agent completes a genuine development change
   using CodeCompass's context and independent assurance through
   supported interfaces — not merely "the MCP server starts."
10. **Risks.** Scope creep toward a second scheduler is the named
    failure mode this phase must actively resist (§6 of the governing
    prompt: "avoid excessive framework design before proving real use").

## Phase 85 — Persistent Knowledge and Incremental Reconciliation

Not yet phase-planned. Can run concurrently with Phase 84 (both depend
only on 82+83); ordered after 84 here because Phase 86 needs 85's
"second task benefits from the first" evidence, which needs a genuine
first task to already exist (Phase 84's dogfood run).

1. **Objective / value.** A second genuine Ledgerkit task measurably
   benefits from knowledge reconciled during the first.
2. **Reused.** Phase 81's reconciliation machinery
   (`knowledge_intermediate.py`, the dual-hash anchor, the existing
   `CONFLICT` state) — extended to trigger from source/test *changes*,
   not only from manual projection edits, which is the one genuinely
   new mechanism this phase adds.
3. **Architectural changes.** A change-detection trigger (source/test
   diff → affected-knowledge invalidation) layered on the existing
   reconciliation flow; no new canonical store.
4. **Deliverables.** Stale-claim/contradiction detection on real code
   change; targeted doc-impact identification (reuses `spec_docs.py`);
   cross-phase provenance.
5. **Prerequisites.** Phase 84's first genuine dev task (for something
   real to invalidate/reconcile) and Phase 82/83's contract/impact
   machinery.
6. **Excluded.** A general-purpose event bus or scheduler for triggering
   reconciliation — this phase triggers on an explicit, narrow source/
   test-change signal only, matching `CLAUDE.md` §1's L-087 "observing a
   change differs from acting on it" discipline already load-bearing in
   this project.
7. **Tests.** A real source change that should invalidate a specific
   prior Claim, verified to actually do so; a source change that should
   *not* invalidate an unrelated Claim, verified to leave it alone
   (the false-positive control is as load-bearing as the true-positive
   one).
8. **Dogfood scenario.** A second genuine Ledgerkit task performed after
   the first, where the agent's context packet visibly reflects
   knowledge reconciled from the first task's own real findings.
9. **Exit gate.** That second task measurably benefits — evidenced, not
   asserted (e.g., a context-evaluator comparison against a control
   packet withholding the reconciled knowledge).
10. **Risks.** "Measurably benefits" needs a concrete, pre-registered
    measurement before the task runs, or the exit gate degrades into
    post-hoc narrative — Phase 85's own plan must define this, borrowing
    Phase 86's methodology document rather than inventing a separate one.

## Phase 86 — Comparative Development Trials

Not yet phase-planned. Full trial design (arms, metrics, controls,
baseline methodology): `planning/v2-evaluation-methodology.md`
(required separately per the governing prompt's own §7; referenced, not
duplicated, here).

1. **Objective / value.** Produce reproducible evidence on whether
   CodeCompass improves verified development outcomes net of total
   overhead — the central, falsifiable test of this ADR's own governing
   hypothesis.
2. **Reused.** `context-quality-evaluation.md`'s "advantage over the
   default pathway" metric (already this project's most consistently
   validated practice per `decisions/0062`'s own evidence); Ledgerkit as
   the shared task substrate across all three arms.
3. **Architectural changes.** None required beyond what 82-85 already
   deliver — this phase is evaluation, not new capability.
4. **Deliverables.** Three-arm comparison (conventional / knowledge-
   assisted / assurance-assisted) on comparable tasks; a reproducible
   report, published whether the result is positive, neutral, or
   negative.
5. **Prerequisites.** Phases 83, 84, 85 all genuinely operable.
6. **Excluded.** Production source-blind coding (the optional arm is
   bounded/research-only, not a release dependency); any numeric
   improvement target set in advance of this phase's own baseline.
7. **Tests.** N/A in the usual code-test sense — the "test" is the trial
   protocol's own pre-registration discipline (methodology fixed before
   results are seen).
8. **Dogfood scenario.** The trial itself, against real Ledgerkit tasks.
9. **Exit gate.** Reproducible evidence, reported honestly including a
   neutral/negative outcome.
10. **Risks.** Confounding cost/ability differences between arms
    (model, task, baseline, oracle, tooling permissions, resource
    ceilings must be held comparable) — the dominant named risk in the
    governing prompt itself; `v2-evaluation-methodology.md` exists
    specifically to fix this before any run.

## Phase 87 — External Validation and Adoption

Not yet phase-planned.

1. **Objective / value.** An unfamiliar developer adopts CodeCompass on
   an independent repository and completes an evidence-backed,
   independently verified change.
2. **Reused.** `codecompass-template` (already populated, Phase 77);
   the agent-led adoption blueprint (`planning/v1-redefinition/
   adoption-blueprint.md`).
3. **Architectural changes.** Hardened MCP permission/security surface;
   CLI usability/failure-recovery passes — no new core capability.
4. **Deliverables.** A CodeCompass self-development trial; one genuinely
   independent external project validated (selected on value/maturity/
   cost at the time, not pre-committed to the Haskell adapter); updated
   `codecompass-template` onboarding; documented supported/unsupported
   project types.
5. **Prerequisites.** Phase 86's evidence exists (positive, neutral, or
   negative — this phase still runs to validate adoption mechanics even
   on a neutral Phase 86 result, since usability and verified-outcome
   evidence are distinct questions).
6. **Excluded.** Any commitment to the Haskell adapter specifically.
7. **Tests.** Reproducibility/compatibility checks on the external
   project; a fresh-session onboarding test mirroring this project's own
   established clean-environment discipline.
8. **Dogfood scenario.** The external-project adoption itself.
9. **Exit gate.** An unfamiliar developer completes a real, evidence-
   backed, independently verified change in an independent repository.
10. **Risks.** Picking an external project for symbolic reasons (e.g.
    "it uses a different language") rather than genuine adoption value —
    named explicitly against in the governing prompt.

## Phase 88 — v2.0 Hardening and Release

Not yet phase-planned.

1. **Objective / value.** A reproducible, usable, model-neutral
   open-source change-assurance system, with demonstrated value beyond
   its own repository.
2. **Reused.** Existing release discipline (`CLAUDE.md` §6's milestone/
   tag convention, `v1-closeout.md`'s own closeout shape as a template).
3. **Architectural changes.** Public contract/MCP/assurance-result
   interface stabilisation and versioning (see `planning/v2-migration-
   assessment.md`); no new capability.
4. **Deliverables.** Migration/compatibility arrangements; security and
   isolation review; end-to-end regression; documentation/packaging;
   template compatibility; published benchmark methodology and results;
   explicit known limitations; release-readiness review.
5. **Prerequisites.** Phase 87 complete.
6. **Excluded.** Any feature not already delivered by 82-87 — this
   phase hardens and ships, it does not add scope.
7. **Tests.** Full end-to-end regression across both repositories.
8. **Dogfood scenario.** The release process itself.
9. **Exit gate.** Gated on evidence and explicit completion of every
   prior exit gate — never on the nominal phase number alone (the
   governing prompt's own explicit instruction).
10. **Risks.** Pressure to ship on schedule rather than evidence — this
    roadmap records the counter-rule explicitly so a future session
    cannot silently drop it.

## Federation-compatibility review (amendment, 2026-10-21, `decisions/0079`)

Direct user request to review Phases 82-88 for future compatibility with
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
  extended by `decisions/0080` §3 with a `publisher_id`/`authority`
  distinction), never injected into Phase 82's own records. Two
  corrections were made, both independent of federation, across two
  same-day amendments: the originally-proposed `epistemic_source` field
  was first corrected to an ordinal scale, then found still incorrect
  (intent/observation/verification are independent predicates, not an
  orderable scale) and **removed entirely**, replaced by a derived,
  read-time view reusing Phase 81's existing
  `derive_provenance_label`-style pattern (`decisions/0080`;
  `planning/phase-82-contract-and-evidence-foundation.md` §§4, 12-13).
  Oracle-result identity was separately strengthened to bind to the
  exact tested subject (a content digest, not a bare commit reference)
  rather than merely a baseline/contract name. Still requires the same
  maintainer approval its original proposal already needed — not a new,
  additional gate.
- **83 (Semantic Change Assurance)**: reviewed — impact traversal stays
  project-local by design (§ above: "does not introduce a new graph
  table unless real-use evidence shows a gap"). Future extension point
  named, not built: a cross-project mapping citing one of Phase 83's own
  impact-traversal findings is a legitimate future Layer C evidence
  source, requiring no change to Phase 83 itself.
- **84 (Agent Integration and MCP)**: reviewed — the MCP tool surface
  (contract retrieval, impact assessment, oracle execution, context-
  packet compilation) is not designed around an implicit single-project
  assumption (each call already takes a project/workspace context
  implicitly, via whichever repository `codecompass` is pointed at).
  Forward-looking note: a future federated MCP capability would add a
  `project_id` parameter to existing calls rather than a parallel tool
  set — named for Stage 1/2's own future planning, not designed now.
- **85 (Persistent Knowledge and Incremental Reconciliation)**:
  reviewed — project-scoped invalidation and provenance boundaries are
  already Phase 85's own design (source/test change in *this* project
  invalidates *this* project's own knowledge). The post-v2 track's own
  invalidation rule (`post-v2-cross-project-overlay-backlog.md`'s
  "Verification and reconciliation model") extends this boundary
  explicitly: a change to one project's Layer A records may flag a
  Layer C mapping for re-review, but never directly rewrites another
  project's own Layer A records. No change to Phase 85's own scope.
- **86 (Comparative Development Trials)**: reviewed — **the existing
  three-arm design (conventional / knowledge-assisted / assurance-
  assisted) is unchanged.** Cross-project overlay capability does not
  exist yet when Phase 86 is expected to run and must not be introduced
  as an unmeasured, uncontrolled advantage in any arm — if a future
  overlay capability is real and mature by the time Phase 86 actually
  executes, including it would require a new, explicitly named fourth
  arm or a documented methodology amendment
  (`planning/v2-evaluation-methodology.md`), never a silent addition to
  Arm B or C's existing definition.
- **87 (External Validation and Adoption)**: reviewed — independent
  adoption on a genuinely independent repository remains the primary
  gate, unchanged. Confirmed explicitly: **neither the Haskell adapter
  nor any cross-project overlay capability is required for Phase 87's
  exit gate** — an external-project portability observation arising
  incidentally during Phase 87 may be recorded, but is optional
  commentary, not a precondition.
- **88 (v2.0 Hardening and Release)**: reviewed — public interface
  stabilisation covers only what Phases 82-87 actually deliver. This
  review adds one explicit constraint: **Phase 88's documentation must
  not describe federation/overlay capabilities as available** — the
  post-v2 track is, by design, not implemented by v2.0 release time
  unless a future, separate decision pulls a specific stage forward
  with its own plan and exit-gate evidence.

## Post-v2: Cross-Project Semantic Overlay track

**Explicitly gated, not part of the mandatory Phase 82-88 sequence.**
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

Per the governing prompt's §5, each item below is recorded as
**deferred**, sourced from the governing prompt itself (none of these
existed as a prior committed backlog item in this repository — see
`decisions/0078`'s Context section). Revisit trigger is the same for all
unless noted: "Phase 86 evidence, or a specific post-v2 user request,
shows this item is now load-bearing for a real task."

| Item | Status | Note |
|---|---|---|
| Full Pi-local documentation generation | deferred | Local inference remains a legitimate post-v2 opportunity (governing prompt §5), not discarded. |
| Complete visual Contract Wiki | deferred | A textual/Markdown projection (reusing Phase 81's intermediate-knowledge rendering) is in scope for Phase 82-85; a *visual* interface is not. |
| Pi-local 3B model optimisation | deferred | No local/offline model is available in this environment today (same standing gap `strict-isolation-for-documentation-reconstruction.md` already names). |
| General-purpose DAG scheduling | deferred | Directly contradicts `CLAUDE.md` §8's "CodeCompass never spawns or coordinates agents" unless and until that fixed point itself is revisited. |
| Sophisticated hybrid model routing | deferred | No evidence yet that routing (vs. a single frontier model, per Phase 84) is the bottleneck. |
| Predictive model allocation | deferred | Same as above. |
| Comprehensive autonomous workflow orchestration | deferred | Same `CLAUDE.md` §8 constraint as DAG scheduling. |
| Production source-blind coding | deferred, optional research arm only | Phase 86 may run a *bounded* research-only instance; never a v2 release dependency. |
| Full Haskell/hledger integration | deferred | Phase 87 explicitly does not assume the Haskell adapter is the first external proof. |
| Advanced commercial analytics | deferred | Out of scope for an open-source generic mechanism; preserved as a distinct, optional, externally-built layer (governing prompt §6's open-source/proprietary separation). |

## What this roadmap does not do

- It does not mark any Phase 82-88 row `done` — none has been
  implemented.
- It does not reopen or rewrite Phase 81, 81B, or any prior `done`
  phase.
- It does not commit to a numerical improvement target anywhere —
  `planning/v2-evaluation-methodology.md` defines measurement before any
  benchmark is run, per the governing prompt's own explicit instruction.
