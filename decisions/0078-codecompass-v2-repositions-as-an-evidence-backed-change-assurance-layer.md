# 0078. CodeCompass v2 repositions as an evidence-backed software change assurance layer, superseding Priorities A-F as the primary post-v1 strategic framework

## Status

Accepted (2026-10-21, direct user request — "CodeCompass v2 — Strategic
Roadmap Revision and Implementation Planning").

## Context

`decisions/0062` (Phase 72) established six post-v1 priority tracks
(A-F) ordered by task-context-completeness evidence from Ledgerkit's own
Stage C work. Priority A (task context completeness) closed strategically
at Phase 78 (`decisions/0069`, corrected by `decisions/0070`); Priority D
(documentation-first workflow) substantially advanced through Phases
79-81B (clean-room methodology, the persistent intermediate-knowledge
layer, the hardened clean-room preparation/isolation machinery). B, C, E,
F remain unplanned.

The user's governing prompt for this phase explicitly instructs: "review
and comprehensively revise the existing CodeCompass v2 roadmap." **Direct
repository inspection found no such roadmap already committed anywhere
in this repository** — no file, ADR, or `ROADMAP.md` section named `v2`,
`Wiki`, `Pi-local`, `hybrid orchestration`, `DAG scheduling`,
`source-blind`, or `contract Wiki` exists in `codecompass`'s or
`codecompass-template`'s git history (`git grep` across both repositories'
tracked Markdown found zero matches beyond an unrelated SemVer URL). No
`src/codecompass/` module or `pyproject.toml` dependency implements or
references contracts, an oracle, change-impact analysis, or MCP. The
prompt itself states "Assume no knowledge of any external conversation.
This prompt provides the governing strategic direction" — so this ADR
treats the governing prompt as the sole source of the v2 strategic
direction, not as a revision of anything previously committed here. This
honest finding is recorded per the governing prompt's own instruction not
to assume prior work exists simply because it is described as existing.

What genuinely does exist, and is reused rather than rebuilt:

- **Phase 81's intermediate knowledge layer** (`src/codecompass/
  knowledge_intermediate.py`): the canonical `planning/knowledge/<slug>/`
  Observation/Evidence/Claim/Derivation/Decision/Requirement record
  model, with Claim fields `assertion_kind`
  (`definition|relationship|rule|invariant|state_transformation|
  boundary|workflow|constraint`), `status`
  (`proposed|supported|contradicted|superseded|verified`), `basis`,
  `evidence_support_state`, `contradicting_evidence`, `depends_on`. This
  is the closest existing substrate to "behavioural contracts," but its
  `status` enum conflates *epistemic confidence* with *source of
  claim* — see Decision point 1 below for why this matters.
- **Phase 81B's clean-room isolation machinery**
  (`scripts/prepare_cleanroom_branch.py`,
  `scripts/verify_cleanroom_isolation.py`, the broker protocol): a
  working model for bounding an agent's execution/information authority,
  directly relevant to v2's "Governed autonomy" adoption level.
  Independently hardened this same month (Amendment 5) to be
  content-addressed, exact-revision, and non-circular — the same
  rigour v2's manifest/provenance work should match, not re-derive.
- **`decisions/0051`/`0054`** (mechanical-vs-inferred provenance),
  **`decisions/0065`** (first-party source/symbol indexing,
  `source_files`/`source_symbols`), **`git_topology.py`** (Phase 76):
  real source/symbol/dependency graph primitives a change-impact
  capability can build on, not duplicate.
- **`planning/context-gaps/`**, **`context-evaluator`**,
  **`context-quality-evaluation.md`**: the project's own established
  evidence-gate and evaluation-methodology discipline, directly reusable
  for v2's Phase 86 comparative trials rather than inventing a new one.
- **Ledgerkit** (`~/projects/ledgerkit`, a real, independent, mature
  sibling repository with its own `tests/`, `dev-docs/`, `knowledge/`),
  already CodeCompass's established reference project across Phases
  45-78 — the concrete, available substrate for every "genuine Ledgerkit
  development task" the v2 phases require, not a project to newly adopt.

Nothing this ADR does rewrites or reopens Phase 81, 81B, or any `done`
phase's history. Priority A's strategic closure, Priority D's Phase
79-81B deliverables, and every existing ADR stand unmodified.

## Decision

**CodeCompass v2 repositions the project's stated purpose**: from a
context-grounding tool that helps an agent understand a codebase, to
*an evidence-backed software change assurance layer that connects
project intent, implementation evidence, and behavioural contracts;
gives coding agents the context they need; independently evaluates
proposed changes; and preserves verified project understanding across
development cycles.* CodeCompass does not compete with frontier coding
agents at writing code — it makes them more reliable across many
development cycles. The governing loop is **Understand → Specify →
Assess Impact → Implement → Verify → Reconcile**.

**This ADR supersedes `decisions/0062` as the primary forward-looking
strategic framework** (0062's own content, evidence, and Priority A-F
history are not rewritten — append-only, per `CLAUDE.md` §2). Priorities
A-F map forward as follows, so no existing commitment is silently lost:

| Priority | v2 destination |
|---|---|
| A (closed) | Its evidence (task-context completeness is real but structurally LOW-to-MODERATE under current capabilities) is the direct empirical justification for Phase 83 (semantic change-impact) and Phase 85 (reconciliation) — a different, sharper capability than Priority A's own context-retrieval framing, not a reopening of the closed track. |
| B (unplanned) | **Absorbed into Phase 82** (behavioural contracts extend, not replace, the Claim/Requirement productisation B already named). |
| C (unplanned) | **Absorbed into Phase 83** (verification-gap/uncertain-dependency reporting is C's "convertible to a concrete task" idea, scoped to change-impact rather than open-ended gap-hunting). |
| D (Phases 79-81B done; template/workflow packaging open) | **Absorbed into Phase 84 (MCP) and Phase 87 (adoption)** — the "downstream user's own process" half of D that Phases 79-81B did not yet deliver. |
| E (unplanned) | **Absorbed into Phase 82C (oracle) and Phase 83** (an independent oracle plus assurance reports is a stronger, executable version of E's "repeatable context-evaluator protocol" idea). |
| F (unplanned) | **Absorbed into Phase 86** (comparative trials formalise exactly the reproducibility/advantage-over-default-pathway discipline F named, at a larger scale). |

Full phase sequencing, dependency graph, and per-phase deliverables:
`planning/v2-roadmap.md`. Phase 82's implementation-ready plan:
`planning/phase-82-contract-and-evidence-foundation.md`.

**1. INTENDED / OBSERVED / VERIFIED / UNCERTAIN are a new dimension,
not a relabelling of the existing `status` field.** The governing
prompt requires these be kept explicitly separate and never conflated.
The existing Claim `status` enum (`proposed|supported|contradicted|
superseded|verified`) answers "how much evidence supports this
statement" — an orthogonal question to "who is the source of this
statement" (a maintainer's accepted requirement vs. behaviour the
implementation exhibits vs. behaviour a check has demonstrated). A Claim
can be `supported` (good evidence) while still being merely `OBSERVED`
(the evidence is "the code does X," not "a check confirms X under
defined conditions"), and a `REQ-`-prefixed Requirement record is
already structurally closer to `INTENDED` than any Claim is. Phase 82's
plan proposes the smallest schema delta that keeps both axes visible
without duplicating the existing Requirement/Claim split — a design
decision for that plan to finalise and for the maintainer to approve
before implementation, not pre-committed here.

**2. No parallel contract/evidence database.** Behavioural contracts
extend the existing `planning/knowledge/<slug>/` canonical record
format and `context-graph.db`'s existing source/symbol/evidence tables
(`source_files`, `source_symbols`, `symbol_enrichment`,
`doc_relations_edges`) — never a new store. `conditional-generalisation.md`'s
"smallest model" discipline, already applied twice (Phase 54c's original
design, Phase 79's extension), applies a third time here.

**3. The oracle is a judge, not a contestant.** The independent
behavioural oracle (Phase 82C) evaluates a candidate change's own test
run but never accepts a change's own self-reported test modifications as
authoritative — accepted checks are pinned and protected from the agent
under evaluation, mirroring the clean-room writer/validator separation
Phase 81B already proved out (the validator never trusts the thing it
validates).

**4. MCP is additive and read-mostly, not a new orchestration
surface.** `CodeCompass never spawns or coordinates agents` (`CLAUDE.md`
§8) extends unchanged to v2: the MCP interface (Phase 84) exposes
retrieval/impact/oracle-execution capabilities to whichever agent calls
it; it does not replace Claude Code's own harness, add a scheduler, or
grant a coding agent authority to redefine its own acceptance criteria.

**5. Level 2 (Assurance) is the v2 product target, not Level 3
(Governed autonomy).** The existing clean-room isolation mechanism is
reused when governed autonomy is actually exercised (Phase 86's
source-blind research arm, if run), but ordinary CodeCompass adoption
never requires it.

**6. Numerical improvement claims wait for Phase 86 evidence.** No
specific percentage or cost target is set anywhere in this roadmap;
Phase 86 defines the measurement methodology first
(`planning/v2-evaluation-methodology.md`) and reports neutral or
negative results exactly as readily as positive ones.

## Alternatives considered

- **Treat Priority A-F as still-primary and layer contracts/oracle/MCP
  on top as a seventh priority.** Rejected: the governing prompt's
  reframing is a change of *what CodeCompass is for*, not an additional
  track alongside the old framing — layering would leave two competing
  north stars with overlapping but not identical success criteria
  (Priority A's "task context completeness" vs. v2's "verified change
  assurance"), which is itself confusing to a future session reading
  `ROADMAP.md` cold.
- **Rewrite `decisions/0062` in place to reflect the new framing.**
  Rejected: `CLAUDE.md` §2's ADR convention is explicitly append-only —
  a reversed or superseded decision gets a new numbered file, never an
  edit to the original's content.
- **Fabricate a "mapping from the superseded v2 roadmap" to satisfy the
  governing prompt's literal request.** Rejected: no such roadmap exists
  to map from; inventing one to look complete would itself be the kind
  of unverified claim this whole repositioning exists to prevent. The
  honest finding (no prior v2 roadmap in this repository) is reported
  instead, in this ADR and in the completion report.

## Consequences

- `planning/ROADMAP.md` gains a new "v2 — evidence-backed change
  assurance (Phases 82-88)" section; its existing "Post-v1 priorities
  (A-F)" section is annotated (not rewritten) to point here.
- Phase 82 is `planned` (this ADR plus `planning/phase-82-contract-and-
  evidence-foundation.md`); Phases 83-88 are sequenced in
  `planning/v2-roadmap.md` but not yet individually phase-planned —
  each gets its own `CLAUDE.md` §1 planning pass, with a fresh scoping
  review against evidence current at that time, when it is actually
  next (matching `decisions/0062`'s own established convention for
  Priority A).
- No `src/codecompass/` or `context-graph.db` schema change is made by
  this ADR. Phase 82's plan proposes specific schema deltas for
  maintainer approval before any implementation begins.
- If Phase 86's comparative trial evidence contradicts this ADR's
  governing hypothesis (an independent evidence/verification layer
  improves reliability net of overhead), that result is reported
  honestly and a further ADR revisits v2's scope — this ADR does not
  pre-commit to a release regardless of evidence.
