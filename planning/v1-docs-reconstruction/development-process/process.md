---
status: PROPOSAL (Phase 64, Cluster C — durable reframing; see README.md for what changed and why)
---

# The development process: Scope → Plan → Domain → Design → Implement

Every claim below cites the section of
[`development-methodology.md`](../../v1-redefinition/development-methodology.md)
(the source document) it is drawn from. This page presents the portable
core of the process — the part that does not depend on CodeCompass's
own tooling, agent roster, or ADR mechanism. See
[`codecompass-instantiation.md`](codecompass-instantiation.md) for how
CodeCompass itself currently runs each stage.

## Why a five-stage process

Two of these stages — deciding what you're building and how you'll
build it — are things most projects already do in some form, even
informally: a problem statement, a plan, an issue description. What is
commonly missing is an explicit place, *between* deciding what to build
and writing the code, for **Domain** (finding out what is actually true
about the relevant subject matter, with evidence, before designing
anything) and **Design** (a reviewed proposal built on that domain
knowledge, rather than on the implementer's own untested assumptions in
their head). CodeCompass's own governing rules require Scope and Plan
explicitly (`CLAUDE.md` §1, cited by the source document's own "Why five
stages" section); Domain and Design were the two stages that had to be
built and proven experimentally before they could be named as part of
the process (source: "Why five stages, not the existing two").

## The five stages

### 1. Scope

Establish the objective, boundaries, desired outcome, and acceptance
criteria for a unit of work. Not necessarily a dedicated artifact — this
can be a phase's opening paragraph, an issue's first description, or a
feature request's first exchange. **Output:** a stated goal and explicit
non-goals, testable enough that "is this done" has an answer. *(source:
stage 1)*

### 2. Plan

Determine the research and delivery approach: what evidence sources are
relevant, what the real risks are, and how the work breaks down.
**Output:** a plan document — scope, what's explicitly deferred, files
to be created/changed, and how the work will be verified as done.
*(source: stage 2)*

### 3. Domain

Reconstruct the relevant domain knowledge before any design is
attempted: terminology, concepts, rules, invariants, examples,
counterexamples, edge cases, references, and current uncertainties —
derived from evidence (source code, tests, prior decisions, retrospective
notes, and directly observed behaviour), **never from existing
documentation treated as authoritative by default**. *(source: stage 3,
opening paragraph)*

This stage produces six kinds of record (names below are the source
document's own; a project without this exact tooling can use plain
prose — see [`minimum-viable-adoption.md`](minimum-viable-adoption.md)):

- **Observation** — a single, dated act of looking (running a command,
  reading a specific file) with exact inputs, outputs, and enough
  provenance to reproduce it.
- **Evidence** — a *neutral* synthesis of one or more Observations (or a
  direct citation to source/docs/tests): states what was found, never
  whether it supports or contradicts anything.
- **Claim** — an interpretation built from Evidence. This is the *only*
  place a support/contradict judgment is recorded — never on the
  Evidence itself, so the same Evidence can support one Claim and
  contradict a competing one without being rewritten.
- **Derivation** — the reasoning *process* that produced a Claim, not
  just a restatement of its conclusion.
- **Decision** — the one record kind only a human/project-owner
  authors. It chooses what the project does about a Claim; it can never
  make the Claim wrong, and can only *agree with* or *deliberately
  diverge from* it.
- **Requirement** — a specific, testable statement a coding agent
  implements against, always tracing back through a Decision to the
  Claim/Evidence behind it.

*(source: stage 3, "Mechanism" — six record kinds carried over
unchanged from this project's own earlier experimental workflow)*

**Independent adversarial review, before anything reaches whoever owns
the decision.** A reviewer distinct from whoever did the Domain research
reads the draft with no obligation to agree with it, and:

- challenges every claim that lacks a citable Observation/Evidence
  record;
- searches for internal contradictions and for edge cases the draft
  doesn't address;
- tries to resolve what it finds through further evidence or a real
  behavioural check, rather than just flagging and stopping;
- escalates to **the actual person who owns the domain/product
  decision** — never a stand-in — only genuine, unresolved ambiguities,
  each presented with the evidence gathered, the real alternatives, and
  their consequences, concisely.

**No one may rule on a genuine domain/product ambiguity except the
actual owner of that decision.** Not the person doing the research, not
a reviewer, not whoever is leading the work — even if that person could
plausibly guess the right answer, and even during a project's own early,
informal iteration. An open question may be *resolved with more
evidence*, or *left explicitly open*; standing in for the actual
decision-owner's judgment is not a third option. *(source: stage 3,
"New: independent adversarial review," and its explicit 2026-09-20
tightening of an earlier, looser allowance — see
[`codecompass-instantiation.md`](codecompass-instantiation.md) for that
history if relevant to a specific project's own governance)*

**Output:** an approved domain baseline — every claim in it is either
backed by cited evidence, or is an honestly-recorded open question, and
every genuine ambiguity has been ruled on by the actual decision-owner
or explicitly left open. Approval never means an agent quietly answered
a question only the owner could answer. *(source: stage 3, "Output")*

**One more discipline worth keeping explicit**: distinguish *documented
intent* (what a doc says should happen) from *implemented behaviour*
(what the code and tests actually do) from *historical decision* (why
something was chosen, at the time) from *current intended meaning*
(what a term means going forward) from *unresolved uncertainty*
(honestly left open, not guessed at). Each of these needs a different
kind of evidence trail, and collapsing them into one undifferentiated
"current understanding" is exactly the failure mode this stage exists to
avoid. *(source: stage 3, closing paragraph)*

### 4. Design

Produce a reviewed design based explicitly on the approved domain
knowledge and current-system evidence: a document that summarizes the
relevant domain context (pointing at the Domain stage's own output, not
re-deriving it), identifies requirements and decisions, proposes tests,
and preserves unresolved uncertainty explicitly rather than silently
inventing an answer where the Domain stage left one open. **Output:** an
approved design plus its Requirement/Decision records. *(source: stage
4)*

### 5. Implement

Provide whoever writes the code with a curated, *compacted* summary of
the approved Scope, Plan, Domain, and Design — smaller than the full
research trail, containing only what's reachable from already-approved
records — implement and verify the change, then reconcile any new
evidence back into the project's own domain knowledge (record where the
change actually landed, and whether the original understanding held up).
**Nothing about this stage shortens or replaces whatever a project
already does after code is written** (its own review, testing, and
sign-off practices) — Domain and Design are two stages *added before*
coding starts, not a shortcut through what comes after. *(source: stage
5)*

## The traceability spine

For any behaviour that matters enough to argue about, six things should
be answerable, in either direction:

```
Evidence → Claim/Invariant → Design Decision → Requirement → Implementation → Test
```

Reading it forward answers "what does this evidence justify"; reading it
backward (Test → Requirement → Decision → Claim → Evidence) answers "why
does this code exist." Both directions use only identifiers a project
already produces under this process — no separate database or query
tool is required to make this walkable; a text search across the
project's own domain/plan/design records is sufficient at small-to-medium
scale. *(source: "Traceability spine")*

An **invariant** is not a separate kind of record — it is a Claim (or a
cross-cutting rule pulled from several Claims) that gets surfaced
prominently in a project's own durable domain documentation, precisely
because it is the kind of statement other work will keep depending on.
*(source: "Traceability spine" table, "Claim / Invariant" row)*

Two practical fields worth tracking on a Requirement once work reaches
Implement, whatever a project's own record format looks like: **where it
was actually implemented** (a file, line, or commit reference) and
**what verifies it** (a test id or path) — populated as the work
actually reaches those points, not predicted in advance. *(source:
"Traceability spine," the two Requirement fields)*

## Re-entry and replanning

This process is not strictly linear. Real work surfaces new evidence,
contradicted assumptions, infeasible designs, and implementation
findings after an earlier stage's own output was already approved. The
rule: **go back to the earliest stage whose own output is now known to
be wrong — no further than that — and come back down through the later
stages again**, rather than resuming them unchanged around the fix.

| If this happens | Re-enter | Because |
|---|---|---|
| New evidence contradicts a Claim or invariant the current work relies on | **Domain** | The underlying understanding is now suspect, not just what was built on it |
| An approved design's own requirement turns out infeasible, or implementation reveals the design solved the wrong problem — but the domain understanding it was built on still holds | **Design** | Re-enter Design specifically, not Domain, when domain understanding itself isn't in question |
| The chosen approach or work breakdown turns out wrong (a strategy, a layout, a tooling assumption) but the objective and domain understanding still hold | **Plan** | Replace the plan section known to be wrong rather than proceeding on it |
| The objective or boundary itself was mistaken | **Scope** | Rare — pause, restate the objective, get it re-approved, don't force a wrong objective through |

*(source: "Re-entry and replanning," "When to re-enter, and where" —
table condensed to drop CodeCompass-specific phase-number examples;
full examples remain at the source)*

**Traceability without silent rewriting.** Domain and Design artifacts
are never edited in place once approved — a superseded Claim, Decision,
or Requirement gets a *new* record whose own "supersedes" field names
the old one; the old record stays on disk, marked superseded, still
citable. Scope and Plan artifacts (a problem statement, a plan document)
may be edited directly when re-entered — a plan is disposable scaffolding
once its work ships, not a long-lived citable evidence record the way a
Claim or Decision is — but a genuine re-scope should still leave a stated
amendment note at the point of change, so a reader mid-document sees
that something changed and why. *(source: "Traceability without silent
rewriting")*

## Portability — what travels, and what doesn't

Another project can adopt this process without depending on any of
CodeCompass's own domain concepts or tooling. What travels:

- **The five named stages**, and what each one produces — described
  above without reference to any CodeCompass-specific concept.
- **The record shapes** (Observation/Evidence/Claim/Derivation/Decision/
  Requirement) — plain, closed-field data, storable as prose, YAML,
  JSON, or any structured text a project already uses.
- **The review posture**: an independent skeptical review before the
  actual decision-owner sees it; preserving rather than silently
  resolving unresolved uncertainty; distinguishing documented intent
  from implemented behaviour from historical decision from current
  meaning from open question; and — the one hard rule — no one stands in
  for the actual decision-owner on a genuine ambiguity, regardless of how
  informal the rest of a project's process is.

What does **not** travel, and isn't meant to: specific role or agent
names are one project's own expression of the process using its own
tooling. A project without that tooling runs the same five stages with
whatever review/delegation mechanism it has — a human reviewer standing
in for the independent-review *function* (never for the actual
decision-owner's own authority — that distinction holds regardless of
tooling), a plain markdown file standing in for a structured record, and
so on. **The durable project artifacts — plans, domain notes, decisions,
evidence, designs — remain the canonical source of what was known,
decided, and why; a project reading only those, with no access to
whatever tooling produced them, should still be able to reconstruct the
full picture.** *(source: "Portability — a hard property, not an
aspiration")*

See [`minimum-viable-adoption.md`](minimum-viable-adoption.md) for what
this looks like at the smallest realistic scale — no dedicated roles, no
formal review-gate states, no structured record schema at all.
