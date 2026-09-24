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

## Re-entry and replanning

Scope→Plan→Domain→Design→Implement is not strictly linear. Real work
surfaces new evidence, contradicted assumptions, infeasible designs, and
implementation findings after an earlier stage's own output was already
approved. This section defines when to go back, to which stage, and how
the superseded material stays traceable rather than silently rewritten
— added because the first three real uses of this methodology (Phase
54c, Phase 60, and this document's own three same-week amendments) all
needed exactly this and were handled ad hoc each time, without a stated
rule.

### When to re-enter, and where

Go back to the **earliest stage whose own output is now known to be
wrong** — no further than that, and once there, come back down through
the later stages again rather than resuming them unchanged around the
fix.

| Trigger | Re-enter | Why |
|---|---|---|
| New Observation/Evidence contradicts a Claim or invariant the current work relies on | **Domain** | The underlying understanding is now suspect, not just what was built on it — Phase 54c's own §5.2 "tests an example, finds it factually wrong" row, reused unchanged |
| An approved Design's own requirement turns out infeasible, or implementation reveals the design solved the wrong problem, while the domain understanding it was built on still holds | **Design** | Phase 54c's own `IMPLEMENTING → RESEARCHED` backward transition (§5.1), generalized: re-enter Design specifically (not Domain) when the domain understanding itself isn't in question |
| The chosen approach or work breakdown turns out wrong (a migration strategy, a file layout, a tooling assumption) but the objective and domain understanding still hold | **Plan** | This project's own repeatedly-exercised practice, formalized here — Phase 61 amended its plan twice, Phase 62 once, Phase 63D twice, all before implementation completed, each replacing a plan section known to be wrong rather than proceeding on it |
| The objective or boundary itself was mistaken — what looked like the right thing to build turns out not to be | **Scope** | Rare. Matches this project's own "retargets this slot" precedent (Phases 53/54) and its GATE-style re-decisions — pause, restate Scope, get it re-approved, don't force a wrong objective through |

A Domain re-entry that supersedes a Claim also puts every Decision built
on it — and, through each such Decision's own citing Requirements — back
under review, even though neither the Decision nor the Requirement was
itself edited. The traceability spine below (via each record's own
citation fields, walked forward from the superseded Claim) is what makes
"what else does this affect" answerable without re-reading everything.

### Traceability without silent rewriting

- **Domain and Design artifacts are never edited in place once
  approved.** A superseded Claim, Derivation, Decision, or Requirement
  gets a **new** record whose own `supersedes` field names the old one
  (Phase 54c §2.2/§2.4/§5.2, reused unchanged, not a new rule) — the old
  record stays on disk, `status: superseded`, permanently citable. This
  section names Phase 54c's existing mechanism as *the* answer to "how
  do I re-enter Domain/Design without losing the trail," rather than
  inventing a second one.
- **Scope and Plan re-entry may edit the plan file directly** — the
  pattern this project already uses (Phase 61/62/63D's own plan
  amendments). Git history, not an in-document `supersedes` chain, is
  the provenance for a pre-implementation plan: a plan file is
  disposable scaffolding once its phase ships, not a long-lived citable
  evidence record the way a Claim or Decision is. A genuine re-scope
  still gets a stated amendment note at the point of change (matching
  every amendment made under this methodology so far), so a reader
  mid-document sees that something changed and why — the mechanism is
  prose-plus-git-blame, deliberately not a new record kind.

## Traceability spine

For any behaviour that matters enough to argue about, six things should
be answerable, each mapping onto an existing record or artifact — no new
core schema:

```
Evidence → Claim/Invariant → Design Decision → Requirement → Implementation → Test
```

**Corrected 2026-09-20** — the original version of this section listed
Requirement before Design Decision, backwards relative to Phase 54c's
own actual citation direction: a Requirement's own `decision:` field
points *at* the Decision that authorizes it (§2.2 — "always traceable
back to the Decision... that justifies it"), so the Decision is
upstream of the Requirement it grounds, not downstream of it. The "why
this is enough" walk-backward example further down already had the
correct order (`Test → Requirement → Decision → Claim → Evidence`);
only the diagram and table above it were wrong. Fixed here to match
Phase 54c's own model exactly — no change to what any record cites, only
to how this document describes the chain.

| Link | Where it lives | Mechanism |
|---|---|---|
| Evidence | `EV-<slug>-NNN` (Phase 54c §2.2) | unchanged |
| Claim / Invariant | `CL-<slug>-NNN`; or a `docs/domain/invariants.md` entry citing the Claim it was pulled from | unchanged — "Invariant" is not a separate record kind, it is a Claim (or a cross-cutting rule drawn from several Claims) that domain documentation surfaces prominently, per Phase 63D's own `docs/domain/` layout |
| Design Decision | `DEC-<slug>-NNN`, `agrees_with_claim:` field pointing at the Claim it builds on (Phase 54c §2.2) | unchanged |
| Requirement | `REQ-<slug>-NNN`, `decision:` field pointing at the Design Decision that authorizes it (Phase 54c §2.2) | unchanged |
| Implementation | the Requirement's own `implemented_at` field | **new, optional field** on the existing Requirement record — a file:line or commit reference |
| Test | the Requirement's own `test_ref` field | **new, optional field** on the existing Requirement record — a test id/path |

**The two new optional Requirement fields are the only schema change
this section makes**, and both default to unset until the Implement
stage actually reaches them — populate `implemented_at` when a
Requirement's own `status` moves to `implemented`, `test_ref` when it
moves to `verified` (Phase 54c's own existing `proposed | approved |
implemented | verified` progression, unchanged). This is additive
widening of one already-existing record kind, the same shape of change
this project already makes routinely elsewhere (e.g. `Symbol`/
`SymbolRow` gaining `export_kind`/`note`, Phase 62) — not a new schema,
and, matching that same phase's own precedent, not judged to need a
dedicated ADR: it fits `decisions/0060`'s own already-stated "reuse
Phase 54c's record shapes unchanged" design decision closely enough
that no new non-obvious tradeoff is introduced.

Populating the two fields is the Implement stage's own existing
"reconcile new evidence back into the project's knowledge" step (this
document's own Implement-stage section, above) — not a new activity,
just two fields recording where that reconciliation already lands.

**Why this is enough, and why it isn't more**: the spine answers "why
does this code exist" (walk backward: Test → Requirement → Decision →
Claim → Evidence) and "what does this evidence justify" (walk forward)
using only identifiers this project already produces. It does not
require a graph, a database, or a new query surface — `grep` for an id
across `planning/knowledge/<slug>/` and `docs/domain/` is sufficient at
this project's current scale. If that stops being true, a future phase
can propose an indexed version with real evidence for why `grep` no
longer suffices — not before.

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

## Domain-corpus freshness and reconciliation

`docs/domain/`'s own approved content (Phase 63D) is a point-in-time
conclusion, not a fact that stays true forever. This section defines
when it should be reconsidered — reusing existing checkpoints, not
adding a new standing process.

**A material change triggers consideration, not automatic
invalidation.** A change to implementation, tests, an ADR, a reference
the corpus cites, or newly observed behaviour does not itself make a
domain claim wrong — it makes it worth asking whether it might have.
Three checkpoints already in this project's workflow are where that
question gets asked pre-v1, reusing existing mechanisms rather than
adding a new standing "domain watcher" process:

1. **Per-phase verification** (`CLAUDE.md` §5's own DoD, unchanged
   mechanism): `docs-reconstructor`'s existing per-phase drift audit
   gains one more check, at the same cost its existing checks already
   run at — if a phase's diff touches a file, symbol, or behaviour a
   `docs/domain/concepts/*.md` page's own references block cites, the
   audit report names it as a **domain-claim staleness candidate**,
   alongside its existing `NO DRIFT` / `DRIFT — n findings` verdict. A
   candidate is not a finding that something is wrong — only that it is
   now worth `domain-skeptic` looking again (below).
2. **Retro** (unchanged mechanism): a phase's own retro already reports
   what was found; a real staleness candidate from (1) gets named there
   exactly like any other honestly-disclosed finding, not silently
   dropped.
3. **Knowledge reconciliation — Phase 65** (`documentation-lifecycle.md`
   §4, amended): alongside comparing the blank-slate reconstruction
   against existing docs, Phase 65 re-invokes `domain-skeptic` — the
   same role Phase 63D introduces, not a new one — against every
   staleness candidate accumulated since the corpus was last approved.
   It resolves what it can with fresh evidence (a new Claim that
   `supersedes` the stale one, per the traceability spine above) and
   escalates only what remains a genuine ambiguity to the actual
   user/domain owner — the same no-stand-in rule Phase 63D itself
   established, unchanged here.
4. **Final closeout re-check** (`agent-led-workflow.md` step 13,
   `release-phase-auditor`'s own final DoD pass — unchanged mechanism,
   widened scope): before treating a phase's own final
   `ROADMAP.md`/`CONTEXT.md` status-bump commit (step 14) as closing the
   phase, `release-phase-auditor`'s final pass re-runs the same
   domain-staleness term check checkpoint (1) already uses, against the
   *full* current repository state — including any reconciliation prose
   already staged for that closeout commit — not only the pre-closeout
   diff checkpoint (1) covered mid-phase. Confirmed necessary at Phase
   66 (`L-040`): a closeout commit's own new `CONTEXT.md` sentence
   reintroduced a domain-corpus staleness term after the mid-phase
   reconciliation had already run clean; only the auditor's own
   independent, incidental re-check caught it.

**What does not change pre-v1**: `docs/domain/` is not re-derived from
scratch at every phase — that would defeat the point of having done
Phase 63D at all. Only the specific concepts a real, flagged change
touches are ever reconsidered, and only at the three checkpoints above.

### Post-v1: per-feature freshness gate (added 2026-09-20)

Phase 65 is a **one-time, milestone-scoped** event — it does not recur
for every feature built after v1 ships. Relying on "checkpoint 3 will
catch it eventually" stops being true the moment there is no more
"Phase 65" coming. This is the ongoing, per-feature equivalent, so a
staleness candidate flagged once does not sit unresolved indefinitely
for lack of a future reconciliation phase:

**Before a future feature's own Design stage relies on a domain concept
that has an outstanding staleness candidate against it, that candidate
must be resolved during the same feature's own Domain stage — not
deferred, and not built on top of as though it were settled.**
"Resolved" means what it always has in this section: either fixed with
fresh evidence (a new Claim that `supersedes` the stale one) or
explicitly escalated to the actual user/domain owner and ruled on —
never silently built on, and never quietly dropped.

This needs no new machinery, only a rule about *when Design may
proceed*: a feature's own `context-researcher`, investigating that
feature's Domain stage, already reads the `docs/domain/` concepts it is
about to rely on — checking each one's own open-staleness status
(`docs/domain/open-questions.md`, or wherever a per-phase drift-audit
candidate was last recorded) is one more thing it checks while already
there, not a separate pass. If a relied-on concept is currently stale,
that feature's Domain stage is not done, and its Design stage does not
start, until the candidate is resolved or the actual user has ruled on
it.

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
  and what was found — not merely that it exists as a document. Phase
  67 also gains a **fresh-agent acceptance test**
  (`planning/v1-redefinition/roadmap.md`'s own Phase 67 entry): a
  genuinely fresh agent, given repository access and no prior
  conversational context, must be able to discover this development
  process, locate the relevant domain and evidence material, recognise
  genuinely unresolved uncertainty as such (not guess past it), and
  produce a sensible design for one small, realistic change. This is
  the closest thing to an outside-observer test the methodology gets
  before v1 — everyone else exercising it up to that point is someone
  who already knows it exists. **Its FAIL consequence is scoped
  narrowly** (`roadmap.md`'s own Phase 67 entry, clarified 2026-09-20):
  it does not block the software release, which GATE DF/DD/G9 already
  govern independently — it blocks only the separate claim that
  CodeCompass v1 is itself a validated reference/model project for this
  methodology, until the specific discoverability gap is fixed and the
  test passes. **See `roadmap.md`'s own Phase 67 entry for a real,
  disclosed platform confound on this test's criterion 1** (`L-042`,
  Phase 67) before repeating it.

Whether this methodology **improves development quality** generally
remains an open question, exactly as Phase 54c's own retro left it —
this document formalizes the *shape* of the process CodeCompass intends
to both use and demonstrate; it does not claim, in advance of further
evidence, that the shape is proven optimal.
