# 0060. Formalize Scope → Plan → Domain → Design → Implement as CodeCompass's own v1 development methodology, with a new Domain Reconstruction phase (63D) preceding blank-slate doc reconstruction

## Status

Accepted (2026-09-20).

## Context

Phase 54c built, and its own retro recommended promoting to **durable**,
a file-based development workflow: six flat record kinds (Observation,
Evidence, Claim, Derivation, Decision, Requirement,
`planning/knowledge/<feature-slug>/`), two new agent roles
(`context-researcher` — behaviour-first primary research;
`documentation-agent` — writes a pre-implementation `design.md`
projected from the knowledge base), a new bounded mode of
`knowledge-curator` (context-packet assembly), and a review-gate
lifecycle (`DRAFT → RESEARCHED → USER REVIEW → APPROVED → IMPLEMENTING →
VERIFIED`). Phase 60 reused it for real (Haskell API-surface
extraction, independently confirmed correct). Both `context-researcher`
and `documentation-agent` exist as real files in `.claude/agents/`, but
neither was ever added to `planning/v1-redefinition/agent-led-development.md`
(the project's own "full model" doc) — a real, pre-existing cataloguing
gap this decision also closes.

Two things remain true independently of that success:

1. **GATE DD (Phase 55, not started)** decides a *different*, narrower
   question — whether `context-graph.db`'s own technical-dependency/
   provenance schema needs a generalised ontology. It has never decided,
   and does not need to decide, whether Phase 54c's *development
   workflow* (how CodeCompass itself investigates, designs, and
   implements) becomes the project's own named, intended process. These
   are separable decisions; nothing about GATE DD being open should
   block the second, unrelated one.
2. **Phase 64 (blank-slate documentation reconstruction, Stage G) is
   upcoming** and, by its own explicit design
   (`documentation-lifecycle.md` §3), approaches CodeCompass "as though
   the current narrative documentation did not exist." That posture is
   right for *documentation structure*, but this project has never run
   a dedicated, evidence-backed pass over its own **domain concepts**
   specifically — and several terms recur across ADRs, plans, retros,
   and code comments (evidence, observation, claim, derivation,
   provenance, relationship/edge, context, context packet, adapter,
   connector, protocol, reference, decision, invariant) without a single
   place stating what each one means, where they overlap, and where they
   are currently conflated. Running Phase 64 without that groundwork
   risks Phase 64 informally re-deriving (or silently guessing at)
   terminology that already has real, evidenced meaning scattered across
   the repository — exactly the kind of "authoritative by default"
   trust in existing text this project's own evidence-first posture
   (`decisions/0014`, `decisions/0021`, the whole Phase 54c model) is
   built to avoid.

Direct user instruction (2026-09-20): insert a dedicated Domain
Reconstruction phase immediately before Phase 64, dogfooding CodeCompass
against its own repository to build an evidence-backed domain corpus;
name and formalize "Scope → Plan → Domain → Design → Implement" as
CodeCompass's own intended development methodology by v1; add an
adversarial/skeptic review step Phase 54c's model does not yet have
(its own §5 "user review" was filled by the lead standing in for the
user during CodeCompass's own dogfooding, never by an independent
agent); and ensure the resulting methodology, and any Skill/agent
instructions expressing it, remain adoptable by another project without
depending on CodeCompass-specific domain concepts or Claude-Code-specific
Skills.

## Decision

1. **Insert Phase 63D — Domain reconstruction** between Phase 63 (Stage
   F's own last phase) and Phase 64 (Stage G's first phase), using the
   letter-suffixed bridge-phase convention this project already
   established (43b/43c/43d/43e, 55b) rather than renumbering Stage G's
   64–70. Full plan: `planning/phase-63d-domain-reconstruction.md`.
   Gated on Phase 63/GATE DF completing (sequential, not parallel,
   matching "immediately before" literally) — **not** gated on GATE DD,
   exactly like Phases 60–63 before it (`decisions/0056`).

2. **Name and formalize "Scope → Plan → Domain → Design → Implement"**
   as CodeCompass's own intended v1 development methodology — full
   definition: `planning/v1-redefinition/development-methodology.md`.
   This does not reinvent Phase 54c's machinery; it **names, organizes,
   and extends** it:
   - *Scope* and *Plan* are not new — `CLAUDE.md` §1 and every existing
     `planning/phase-N-*.md` already are these two stages; this decision
     only gives them explicit names in the five-stage sequence.
   - *Domain* generalizes Phase 54c's per-feature `context-researcher`
     investigation (§2.2's six record kinds) to also support a
     **project-wide** domain corpus — Phase 63D's own deliverable — not
     only a single feature's own knowledge folder.
   - *Design* is Phase 54c's existing `documentation-agent` → `design.md`
     → review-gate lifecycle, unchanged.
   - *Implement* is Phase 54c's existing `knowledge-curator`
     packet-assembly mode → coding agent → revalidation loop, unchanged.

3. **Add a new agent role, `domain-skeptic`** — independent,
   read-only, adversarial review of a domain corpus (or, later, any
   `design.md`) for unsupported claims, internal contradictions, and
   missing edge cases/counterexamples, resolving what it can through
   further evidence or a behavioural experiment and escalating only
   genuine, unresolved ambiguities. This mirrors an already-repeated
   project pattern (`context-evaluator`, `docs-reconstructor`,
   `release-phase-auditor` — never let the producer certify its own
   output) applied to domain-concept claims specifically, a job none of
   those three roles' own briefs naturally covers (matching
   `decisions/0054`'s "separation of concerns" reasoning for why a
   narrow new role, not an extension, is the right shape here). Not
   created by this ADR — cataloged in `agent-led-development.md` §2.13
   and named in Phase 63D's own Files section; the actual
   `.claude/agents/domain-skeptic.md` is that phase's own implementation
   deliverable, matching how Phase 52 planned `context-enrichment-agent`
   before creating it.

4. **`docs/domain/` becomes the durable, primary home for CodeCompass's
   own domain corpus** — a glossary, per-concept documentation,
   invariants, examples/counterexamples, references, and open
   questions, in Markdown as the human-readable source of record. A
   lightweight machine-readable concept registry may accompany it
   (reusing Phase 54c's own YAML record shapes under
   `planning/knowledge/codecompass-domain/`, not a new schema) but never
   replaces the Markdown as the canonical meaning.

5. **Phase 64 is re-scoped** to explicitly consume Phase 63D's
   `docs/domain/` corpus (not independently rediscover domain
   terminology) and to separate six documentation categories: domain
   (what concepts mean), architecture (how they're implemented), user
   (how CodeCompass is used), developer (how it's extended),
   protocol/adapter (how external components integrate), and
   development-process (how Scope→Plan→Domain→Design→Implement itself
   operates). `documentation-lifecycle.md` is updated to reflect this
   as an explicit input/output, alongside a correction of that
   document's own stale phase numbers (it still says "Phase 60/61/66,"
   predating the Stage F/G +4 renumbering `decisions/0056` performed;
   the current numbers are 64/65/69).

6. **Stage E (56–59), if GATE DD funds it, and any other substantial
   pre-v1 design-bearing phase, should explicitly exercise
   Scope→Plan→Domain→Design→Implement** — so the methodology is
   validated by real, repeated pre-v1 use, not merely documented at the
   release boundary. Recorded as a note on Stage E's own roadmap entry,
   not a new gate or a retroactive requirement on phases already done.

7. **Portability is a hard property of the methodology's own
   definition, not an aspiration**: `development-methodology.md`
   describes the five stages, their artifacts, and their verification
   posture in terms any project could adopt (a plan file, a domain
   corpus, a reviewed design, a curated context packet, a
   post-implementation reconciliation step) — it does not require
   CodeCompass's own domain vocabulary (vendor/adapter/symbol/etc.) or
   Claude Code's own Skill mechanism as a precondition for another
   project to run the same process with different tooling. Durable
   project artifacts (plans, the domain corpus, ADRs, designs, evidence
   records) remain the canonical source of project knowledge in every
   case; Skills/agent instructions are one possible expression of *how*
   to execute the process with a given toolset, never the source of
   the knowledge itself.

## Alternatives considered

- **Fold domain reconstruction into Phase 64 itself, no separate
  phase.** Rejected: Phase 64's own blank-slate posture is about
  *documentation structure and rendering*; the user specifically wants
  a dedicated, evidence-and-adversarial-review pass over *domain
  meaning* first, whose approved output then feeds Phase 64 rather than
  being derived inside it under a different, unrelated set of
  concerns.
- **Wait for GATE DD before formalizing the methodology**, since Stage
  E is the other pending "generalize the model" decision. Rejected —
  GATE DD decides `context-graph.db`'s own schema generalization, a
  narrower and different-in-kind question from "what development
  process does this project use to build itself." Blocking a low-risk,
  high-value organizational decision on an unrelated, still-open
  evidence question serves no one.
- **Renumber Stage G to make room for the new phase as a plain
  sequential number**, shifting 64–70 to 65–71. Rejected per the user's
  own explicit non-disruptive-numbering instruction, and matching this
  project's own established precedent (43b–e, 55b) of letter-suffixed
  bridge phases instead of renumbering already-referenced phases.
- **Reuse `knowledge-curator` or `context-evaluator` for the
  adversarial domain-review step**, instead of a new role. Considered
  and rejected: both have differently-scoped existing jobs (queue
  triage/consolidation; task-context-quality rating by direct target
  inspection) that don't naturally stretch to cover "independently
  argue against a concept's own stated definition for internal
  contradiction or missing edge cases" — the same class of reasoning
  `decisions/0054` already applied when it added
  `context-enrichment-agent` as a fourth role rather than stretching a
  third.

## Consequences

- New files: `planning/v1-redefinition/development-methodology.md`,
  `planning/phase-63d-domain-reconstruction.md`.
- Updated: `planning/ROADMAP.md` (new 63D row), `planning/v1-redefinition/roadmap.md`
  (new Phase 63D section; Phase 64/Stage-E sections updated),
  `planning/v1-redefinition/documentation-lifecycle.md` (domain-corpus
  input, six-category separation, stale phase-number correction),
  `planning/v1-redefinition/agent-led-development.md` (§2.11
  `context-researcher`, §2.12 `documentation-agent` — cataloguing two
  already-existing, previously-uncatalogued roles — and new §2.13
  `domain-skeptic`; write-boundary table gains matching rows),
  `planning/v1-redefinition/README.md` (new gate **G14**, recording this
  restructuring as decided), `planning/CONTEXT.md`, `CHANGELOG.md`.
- Two stale phase-number references corrected as directly-adjacent
  bookkeeping: `.claude/agents/release-phase-auditor.md` ("mandatorily
  at Phase 65" → "Phase 68") and `.claude/agents/docs-reconstructor.md`
  ("MILESTONE (Phase 60 only)" → "Phase 64") — both predate the Stage
  F/G +4 renumbering and were never updated when it happened.
- No `src/codecompass/` change is made by this ADR — it is a
  roadmap/planning/governance revision. Phase 63D's own implementation
  (the actual domain corpus, the `domain-skeptic` agent file, any new
  `docs/domain/` content) is that phase's own scoped work, not started
  by this decision, and requires its own plan-file review per
  `CLAUDE.md` §1 before implementation begins (already satisfied by
  `planning/phase-63d-domain-reconstruction.md`, written in this same
  commit).
