# Development methodology: Scope → Plan → Domain → Design → Implement

`decisions/0060`. Names, organizes, and extends Phase 54c's own
already-recommended-durable machinery
(`planning/phase-54c-evidence-knowledge-workflow.md`,
`planning/retros/phase-54c-evidence-knowledge-workflow.md`) into a single
five-stage development methodology — the process CodeCompass intends to
both **use** and **document itself using**, by v1.

This document defines *what the stages are and what each one produces*.
It does not restate Phase 54c's own detailed record shapes, agent
briefs, or lifecycle mechanics — those stay defined once, in that plan
and in `.claude/agents/*.md`, and are only pointed to here.

## Why five stages, not the existing two

`CLAUDE.md` §1 already requires two of these (Scope is implicit in a
phase's own opening problem statement; Plan is the
`planning/phase-N-*.md` file itself). What was missing, until Phase 54c
built it experimentally, was an explicit place for **Domain**
(reconstructing what is actually true about the relevant subject matter,
with evidence) and **Design** (a reviewed proposal built on that domain
knowledge, not on an implementer's own untested assumptions) between
planning and coding. Phase 54c proved the mechanics work for a single
feature; this document promotes the same shape to a named, general
methodology and adds the one piece that was still missing — an
independent, adversarial review step before anything reaches the human
project owner.

## The five stages

### 1. Scope

Establish the objective, boundaries, desired outcome, and acceptance
criteria for a unit of work. Not a new artifact — this is what a phase's
own opening paragraph, or a feature request's own first exchange,
already does. **Output:** a stated goal and explicit non-goals, testable
enough that "is this done" has an answer.

### 2. Plan

Determine the research and delivery approach: what evidence sources are
relevant, what the real risks are, and how the work breaks down.
**Output:** `planning/phase-N-<name>.md` (`CLAUDE.md` §1) — scope,
what's explicitly deferred, files to be created/changed, and how the
phase will be verified as done. Unchanged from existing practice.

### 3. Domain

Reconstruct the relevant domain knowledge before any design is
attempted: terminology, concepts, rules, invariants, examples,
counterexamples, edge cases, references, and current uncertainties —
derived from evidence (source, tests, ADRs, plans, retros, and observed
behaviour), never from existing documentation treated as authoritative
by default.

**Mechanism — reuses Phase 54c's own six record kinds unchanged**
(Observation, Evidence, Claim, Derivation, Decision, Requirement;
`phase-54c-evidence-knowledge-workflow.md` §2.2), produced by
`context-researcher` (behaviour-first: runs real examples/experiments
before reading documentation, traces every real implementation path,
never stops at the first plausible one) under
`planning/knowledge/<slug>/`. Two applications, not two mechanisms:

- **Feature-scoped** (Phase 54c's original shape): one feature's own
  `planning/knowledge/<feature-slug>/`, feeding that feature's own
  Design stage. Unchanged.
- **Project-scoped** (new, Phase 63D): CodeCompass's own core domain
  concepts, evidence-backed the same way, but published as durable
  Markdown under `docs/domain/` (glossary, per-concept docs, invariants,
  examples/counterexamples, references, open questions) rather than
  staying inside one feature's own knowledge folder — because the
  concepts in scope (evidence, observation, claim, derivation,
  provenance, relationship/edge, context, context packet, adapter,
  connector, protocol, reference, decision, invariant, and others found
  along the way) are used across many features, not one.

**New: independent adversarial review**, before anything reaches the
user. `domain-skeptic` (`agent-led-development.md` §2.13) reads a
domain-corpus (or feature-knowledge) draft with no obligation to agree
with it, and:

- challenges every claim that lacks a citable Observation/Evidence
  record;
- searches for internal contradictions between concepts, and for edge
  cases/counterexamples the draft doesn't address;
- attempts to resolve what it finds through further evidence or a real
  behavioural experiment (re-dispatching `context-researcher` or running
  a check itself) rather than simply flagging and stopping;
- escalates to **the actual user/domain owner** — never the lead, never
  any agent standing in — **only** genuine, unresolved domain/product
  ambiguities: each presented with the evidence gathered, the real
  alternatives, and their consequences, concisely.

**Write boundary**: `domain-skeptic` is read-only toward source,
implementation, design content, and the approved domain corpus itself
— it never edits any of them. It may append new Observation/Evidence
records for checks it runs itself (same shapes and write boundary
`context-researcher` already has — never a Claim, Derivation, or
Decision, which require fuller derivation work or the user's own
ruling) and write its own review-findings report. Nothing else.

This is the one genuinely new mechanism this document adds to Phase
54c's own model — that model's own §5 "user review" step was filled by
the lead standing in for the user during CodeCompass's own dogfooding
(`phase-54c-evidence-knowledge-workflow.md` §5.1), never by an
independent agent. **`domain-skeptic` sits before that review step, not
instead of it, and — amendment, 2026-09-20 — the review step itself no
longer permits a lead/agent stand-in**: a genuine ambiguity can only be
ruled on by the actual user/domain owner. An agent (the lead included)
may fully resolve an item with evidence, or leave it explicitly
unresolved; ruling on it in the user's place is not a third option,
including during CodeCompass's own dogfooding. This narrows Phase 54c's
own §5.1 precedent, which allowed exactly that stand-in for
CodeCompass's own dogfooding case; that allowance does not carry
forward past this document.

**Output:** an approved domain baseline — for a feature, the existing
`APPROVED`-state knowledge folder; for the project as a whole, an
approved `docs/domain/` corpus (Phase 63D's own deliverable). "Approved"
means: `domain-skeptic` found no unresolved contradiction it could not
either fix with evidence or correctly characterize as a genuine open
question, and every such question is either ruled on by the actual
user/domain owner or honestly recorded as still open — approval never
requires an agent to have quietly answered a question only the user can
answer.

**Distinguishing what kind of claim something is** (Phase 54c's own
§5.3, reused unchanged): documented intent (what a doc says should
happen) ≠ implemented behaviour (what the code and tests actually do) ≠
historical decision (an ADR's own record of what was chosen and why, at
the time) ≠ current intended meaning (what the term means going
forward, per this stage's own approved output) ≠ unresolved uncertainty
(honestly left open, not guessed at). Each maps to a different evidence
trail — a documentation citation, a source/test citation, an ADR
citation, a Claim/Decision record, or an explicit open-questions entry
— never collapsed into one undifferentiated "current understanding."

### 4. Design

Produce a reviewed design based explicitly on the approved domain
knowledge and current-system evidence.

**Mechanism — reuses Phase 54c's own `documentation-agent` → `design.md`
→ review-gate lifecycle unchanged** (`DRAFT → RESEARCHED → USER REVIEW →
APPROVED → IMPLEMENTING → VERIFIED`,
`phase-54c-evidence-knowledge-workflow.md` §4, §5.1). A design
document: summarizes the domain context relevant to the change
(pointing at the approved Domain-stage output, not re-deriving it);
identifies requirements and decisions (Requirement/Decision records);
proposes tests; and preserves unresolved uncertainty explicitly rather
than silently inventing an answer where the Domain stage left one open.

**Output:** an `APPROVED` `design.md` plus its Requirement/Decision
records.

### 5. Implement

Provide the coding agent with a curated context packet based on the
approved Scope, Plan, Domain, and Design; implement and verify the
change; then reconcile any new evidence back into the project's
knowledge.

**Mechanism — reuses Phase 54c's own `knowledge-curator` packet-assembly
mode unchanged** (`phase-54c-evidence-knowledge-workflow.md` §6):
`context-packet.md`, smaller than the full research trail, reachable
only from `APPROVED` records. The coding agent (the lead, or a
delegated implementer) implements against it, logs any real gap in
`packet-sufficiency.md` (§6.1), and verifies per the plan's own
Verification section. **Downstream workflow is unchanged and preserved
in full**: the normal `CLAUDE.md` §5 Definition of Done (docs-drift
audit, retro, learning triage, `release-phase-auditor` pass) still
applies exactly as it does today — Scope→Plan→Domain→Design→Implement
adds two upstream stages (Domain, Design) before coding starts; it does
not replace or shorten anything downstream of "code implemented."

## Stage → artifact map (summary)

| Stage | Primary artifact | Owner/role |
|---|---|---|
| Scope | A phase's own stated goal + acceptance criteria | lead (or the requester) |
| Plan | `planning/phase-N-*.md` | lead |
| Domain | `planning/knowledge/<slug>/` records; `docs/domain/` for project-wide concepts | `context-researcher`, reviewed by `domain-skeptic` |
| Design | `design.md` (+ Requirement/Decision records) | `documentation-agent`, reviewed by the human/lead |
| Implement | `context-packet.md` → code + tests | `knowledge-curator` (packet), coding agent (lead/implementer) |
| *(downstream, unchanged)* | drift audit, retro, learning triage, DoD audit | `docs-reconstructor`, lead, `knowledge-curator`, `release-phase-auditor` |

## Portability — a hard property, not an aspiration

Another project must be able to adopt this process without depending on
any CodeCompass-specific domain concept (vendor, adapter, symbol, etc.)
or on Claude Code's own Skill mechanism specifically. What travels:

- The **five named stages** and what each one produces, as described
  above — tool-agnostic by construction.
- The **record shapes** (Observation/Evidence/Claim/Derivation/
  Decision/Requirement) — plain, closed-field data, storable as YAML,
  JSON, or any structured text; nothing about them names a CodeCompass
  concept.
- The **review posture** (an independent skeptic before the actual
  user/domain owner; preserve rather than silently resolve unresolved
  uncertainty; distinguish documented intent from implemented
  behaviour from historical decision from current meaning from open
  question; **no agent or lead stand-in for the user on a genuine
  ambiguity**) — a general evidentiary discipline, not a
  CodeCompass-domain rule.

What does **not** travel, and is not meant to: the specific agent
*names* (`context-researcher`, `domain-skeptic`, etc.) are this
project's own expression of the process using Claude Code's own
subagent mechanism. A project without that tooling implements the same
five stages with whatever review/delegation mechanism it has — a human
reviewer standing in for `domain-skeptic`'s own adversarial-review
*function* (never for the actual user's own decision authority — that
distinction holds regardless of tooling), a plain markdown file
standing in for a YAML record, and so on. **Skills or agent instructions
express *how* to perform the process with a given toolset; the durable
project artifacts (plans, domain corpus, ADRs, designs, evidence
records) remain the canonical source of domain knowledge, architecture,
decisions, evidence, and design** — a project reading only those
artifacts, with no access to this project's own `.claude/agents/`
directory, can still reconstruct what was known, decided, and why.

## Minimum viable adoption

A smaller project — one person, no agent roster, no `decisions/`-style
ADR process, no `ROADMAP.md`/`CONTEXT.md` machinery — can still run
Scope → Plan → Domain → Design → Implement without adopting any of
CodeCompass's own governance structure. The five stages are the
portable part (per Portability, above); everything CodeCompass adds on
top is optional scaffolding, not a precondition. A minimum viable
profile:

| Stage | CodeCompass's own expression | Minimum viable equivalent |
|---|---|---|
| Scope | A phase's own opening problem statement | One paragraph, anywhere durable (an issue, a commit message, the top of the plan file below) — the goal and what's explicitly out |
| Plan | `planning/phase-N-*.md` | One short file (or the top of a design doc) naming what will change and how it'll be checked |
| Domain | `context-researcher` → `planning/knowledge/<slug>/` records, reviewed by `domain-skeptic` | A short "what I found, and how I know" note — even a few bullet points citing a real file/line/command output — plus a second look by anyone else available (a colleague, or the same person coming back to it later with fresh eyes) who is deliberately asked to poke holes in it, not just skim it |
| Design | `documentation-agent` → `design.md`, reviewed by the user | A short written proposal (a paragraph is enough for a small change) that says what the Domain stage found, what will be built, and what's still unknown — read by the person who actually owns the decision before code is written |
| Implement | `knowledge-curator` → `context-packet.md` → coding agent → revalidation | Whoever writes the code reads the Domain note and the Design proposal first (not just the Plan), and after shipping, updates the Domain note with anything new that was learned — the "reconcile new evidence back" step, done by hand |

**What must not be dropped, even at this minimum**: the *order*
(domain understanding before design; design before code), the written
form (even one paragraph — not "it's in my head"), and the
independent-second-look step before a genuine ambiguity gets decided.
**What may be dropped**: dedicated agent roles, YAML record shapes
(plain prose is fine), a formal review-gate lifecycle with named
states, and any CodeCompass-specific concept. A team of one can still
distinguish "I read this in the docs" from "I tested this myself" from
"we decided to do X anyway" — that distinction, not the tooling around
it, is what the methodology actually protects.

## Where this gets exercised before v1

Named as evidence, not yet claimed as proven:

- **Phase 60** already reused the underlying record model for real
  (Haskell API-surface extraction), independently confirmed correct.
- **Phase 63D** (this document's own trigger) is the first
  **project-scoped** Domain-stage application, and the first real use
  of `domain-skeptic`.
- **Stage E (Phases 56–59)**, if GATE DD funds it, is recommended
  (`planning/v1-redefinition/roadmap.md`'s own Stage E entry) to
  explicitly run Scope→Plan→Domain→Design→Implement in full — a
  design-bearing generalisation decision is exactly the shape of work
  this methodology targets, and running it for real before v1 is what
  turns "documented methodology" into "validated methodology."
- **Phase 64** consumes Phase 63D's own domain corpus directly (see
  `planning/v1-redefinition/roadmap.md`'s Phase 64 entry and
  `documentation-lifecycle.md` §3) — the methodology's own first
  downstream consumer.
- **Phase 67** (final validation) is the place to state plainly, at
  v1, how many real times this methodology was exercised pre-release
  and what was found — not merely that it exists as a document.

Whether this methodology **improves development quality** generally
remains an open question, exactly as Phase 54c's own retro left it —
this document formalizes the *shape* of the process CodeCompass intends
to both use and demonstrate; it does not claim, in advance of further
evidence, that the shape is proven optimal.
