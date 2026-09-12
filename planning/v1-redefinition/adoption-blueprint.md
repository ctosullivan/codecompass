# Agent-led development adoption blueprint (required output 6)

Gate **G13** (`realignment-2026-09.md` §7). Written at Phase 43e. What
CodeCompass hands to a project that wants to adopt the same development
methodology — Ledgerkit first, others later. **Extracted and
generalised from CodeCompass's own working practice
(`agent-led-development.md`, `agent-led-workflow.md`, `.claude/agents/*.md`),
not invented fresh** — every recommendation below is something
CodeCompass has actually run, not a hypothesis.

**Explicitly not** a large autonomous-development framework. It is a
practical project-development protocol: a roster shape, a workflow, a
set of write boundaries, and a place for CodeCompass-specific tooling to
plug in. A project can adopt the whole thing, part of it, or none of it.

## 0. How to read this document

Each recommendation is tagged:

- **[GENERIC]** — applies to any project, no CodeCompass dependency.
- **[PROJECT-SPECIFIC]** — the *shape* generalises, the *content* is
  per-project (e.g. "a compatibility register" is generic; hledger's
  specific compatibility categories are Ledgerkit's own).
- **[OPTIONAL]** — valuable but not load-bearing; skip if it doesn't earn
  its cost for a smaller project.
- **[CODECOMPASS-GENERATED]** — an artifact CodeCompass itself produces
  (a Skill, a routing table, `/discovery`) that the adopting project
  should treat as read-only / regenerated, never hand-edited
  (CodeCompass's own `check_generated_artifacts_match_source`, Phase 43b,
  is the concrete lesson behind this rule — a real incident, not a
  hypothetical).
- **[MANUALLY-GOVERNED]** — a human-approval checkpoint, same posture as
  CodeCompass's own `CLAUDE.md` §0.

## 1. Recommended agent roles [GENERIC shape, PROJECT-SPECIFIC content]

CodeCompass's roster grew to 8 roles over 5 real phases (39–43c), each
added only where separation of **context**, **responsibility**, or
**authority** earned its keep (`agent-led-development.md` §1). Do not
start a new project with all 8 — start smaller and let real friction
justify each addition, the same way CodeCompass itself did (GATE DA
explicitly kept the roster capped rather than growing it further without
cause).

**Minimum viable roster for a project like Ledgerkit** (mapping this
task's suggested roles onto what actually exists in CodeCompass):

| Suggested role (this task's prompt) | CodeCompass equivalent | Adopt as |
|---|---|---|
| upstream/source researcher | *(new — no direct CodeCompass equivalent; CodeCompass doesn't have an "upstream" it's reimplementing)* | **[PROJECT-SPECIFIC]** — Ledgerkit's version reads hledger docs/source/tests, records what it learned with provenance, and stops (does not implement) |
| compatibility/specification researcher | *(new, closely related to the above — may be the same agent)* | **[PROJECT-SPECIFIC]** — could merge with the upstream researcher for a project Ledgerkit's size; split only if the two roles start fighting for the same context window in practice |
| implementation agent | the lead itself, or an ad-hoc `general-purpose` implementer subagent | **[GENERIC]** — CodeCompass deliberately has **no standing "implementer" agent**; the lead implements directly or delegates ad hoc, per phase (`agent-led-development.md` §2.9). Recommend the same for Ledgerkit — a standing implementer role added nothing when CodeCompass tried the alternative in its own precedent design |
| compatibility/differential tester | `reference-project-tester` (generalised) | **[GENERIC shape]** — CodeCompass's `reference-project-tester` already "exercises the tool against a real project, files friction, never silently repairs it"; Ledgerkit's version does the same against `hledger`'s executable output, with "friction" reframed as "unexplained mismatch" |
| documentation maintainer | `docs-maintainer` | **[GENERIC]** — unchanged shape: reconciles current-truth docs against verified implementation, checks generated-vs-hand-authored before editing |
| context curator | *(new — see `codecompass-feedback-ingestion.md`)* | **[PROJECT-SPECIFIC]** — this is Ledgerkit's *own* new role, not a CodeCompass one; it converts Ledgerkit's CodeCompass friction into the standard finding format CodeCompass's own review process expects (§5 below) |
| roadmap/project-state curator | `roadmap-context-curator` | **[GENERIC]** — unchanged shape, but Ledgerkit's `CONTEXT.md` is explicitly "throwaway... overwritten completely" (its own `CLAUDE.md`) rather than accreting the narrative CodeCompass's does; the curator's *reconcile-from-evidence* discipline still applies, its output format doesn't need to match CodeCompass's |
| knowledge curator | `knowledge-curator` | **[GENERIC shape, PROJECT-SPECIFIC destination]** — the promotion-destination table (§4) differs: Ledgerkit routes to `knowledge/DECISIONS.md`/`EDGE_CASES.md`/`ANTIPATTERNS.md`/`DOMAIN_RULES.md` instead of an ADR folder, since that's where Ledgerkit's own governance already puts this class of knowledge |
| release/phase auditor | `release-phase-auditor` | **[GENERIC]** — unchanged: independent, read-only, re-runs verification, never repairs what it audits |
| *(not listed by this task, but load-bearing in CodeCompass)* | `docs-reconstructor` (drift audit + milestone blank-slate) | **[OPTIONAL]** — valuable once a project accumulates enough narrative-doc surface to drift (CodeCompass needed it by Phase 41); Ledgerkit's `dev-docs/`/`docs/` split may earn this sooner than expected given its own `CLAUDE.md`'s explicit same-response doc-sync rule already fights the same drift CodeCompass's audit catches |
| *(not listed, but the newest CodeCompass role)* | `context-health-planner` | **[OPTIONAL, CODECOMPASS-SPECIFIC]** — this role exists to judge whether *CodeCompass's own context* is adequate for upcoming work; it only makes sense once a project is actually consuming CodeCompass, i.e. it's an artifact of adoption, not something Ledgerkit stands up independently |

**Recommended Ledgerkit-adoption starting roster (5, not 8):** an
upstream/compatibility researcher (merged), `reference-project-tester`
-equivalent (the differential tester, since Ledgerkit's compatibility
work makes this the highest-value role from day one), `docs-maintainer`
-equivalent, `roadmap-context-curator`-equivalent, `knowledge-curator`
-equivalent + the context curator responsibility folded into it
initially (split only if the volume of CodeCompass-feedback findings
grows enough to justify a dedicated role — the same "start minimal, add
with cause" discipline CodeCompass applied to itself).

## 2. Responsibilities, permissions, independence [GENERIC]

Port CodeCompass's own fixed points verbatim — they are not
CodeCompass-specific, they are properties of *any* agent-led development
process that wants independent verification to mean something:

- **The main session orchestrates; the tool being developed never
  orchestrates its own agents.** (For Ledgerkit: Ledgerkit's library code
  never spawns or coordinates agents — Claude Code does, same as
  CodeCompass §1.9's non-goal.)
- **Evaluation/audit agents inspect their target directly, never through
  the tool under test, and never repair what they are judging.**
  (Ledgerkit's differential tester runs the real `hledger` executable and
  compares Ledgerkit's own output — it does not ask Ledgerkit's own
  parser to validate Ledgerkit's own parser.)
- **No agent writes the project's protected governance file** (Ledgerkit's
  `CLAUDE.md`) **or the project's decision-history artifact** (Ledgerkit's
  `knowledge/DECISIONS.md`, playing the role CodeCompass's `decisions/`
  ADRs play) **or the library/application source directly** — those are
  the lead's job, or an ad-hoc implementer subagent's, per phase.
- **An agent observation is not authoritative because an agent recorded
  it.** It is a candidate, promoted only through curation + evidence
  (§4).
- **Agents may keep persistent memory as a working aid; it is never a
  source of truth.** If an agent's memory and the repository disagree,
  the repository wins, and the divergence itself becomes a candidate
  observation (this is verbatim CodeCompass's own policy — see
  `agent-led-development.md` §5).

## 3. Project entry points [GENERIC pattern, mostly CODECOMPASS-GENERATED once adopted]

The hierarchy this task specifies —

```
project CLAUDE.md / agent entry point
        ↓
CodeCompass discovery
        ↓
task-specific context map
        ↓
relevant Skills / graph relationships
        ↓
primary evidence
```

— is exactly CodeCompass's own existing shape (root `CLAUDE.md` routing
table → `/discovery` → generated Skills/`.mdc` → `vendor/<name>/src/` as
primary evidence). Ledgerkit adopts it **by running CodeCompass against
itself**, not by hand-building an equivalent — once CodeCompass indexes
Ledgerkit's own dependencies (hledger as whatever technical-dependency
kind Stage B/C settles on; its Python stdlib usage; its own compatibility
tests), the routing table and Skills CodeCompass generates *are*
Ledgerkit's entry points. **[CODECOMPASS-GENERATED]** — Ledgerkit's own
`CLAUDE.md` gains a pointer section the same way CodeCompass's own root
`CLAUDE.md` ends with one to `ai-docs/README.md`; it does not duplicate
CodeCompass's routing table by hand.

**A fresh agent working in Ledgerkit should quickly learn:** where
CodeCompass context is available (the routing table pointer); when to
use it (a task touching a tracked dependency); how to interpret
relationship states (deterministic vs. agent-suggested — `decisions/0051`'s
distinction, unchanged); when to go straight to primary evidence instead
(anything CodeCompass doesn't yet track, or a `LOW`-advantage case per
`context-quality-evaluation.md`).

## 4. Knowledge-curation workflow [GENERIC shape, PROJECT-SPECIFIC destinations]

CodeCompass's lifecycle, unchanged:

```
observation → candidate learning → evidence/recurrence → curation → promote / retain / discard
```

Destination table, generalised (CodeCompass's left column vs. Ledgerkit's
right column, as an example of the same shape landing in different
artifacts):

| Classification | CodeCompass destination | Ledgerkit destination |
|---|---|---|
| behavioural invariant | regression test | regression test (`tests/`) |
| compatibility behaviour | *(new for Ledgerkit)* | compatibility register + test (this task's required output 9) |
| architecture rationale | ADR (`decisions/`) | `knowledge/DECISIONS.md` |
| current architecture | `architecture/` | `dev-docs/architecture.md` |
| recurring agent instruction | `CLAUDE.md` proposal (gated, §0) | `CLAUDE.md` proposal (Ledgerkit's own equivalent gate, if it has one — confirm at adoption time) |
| repeatable workflow | Skill | Skill (`.claude/skills/`, same mechanism, project-agnostic) |
| future work | `ROADMAP.md` row | `ROADMAP.md` row (Ledgerkit's own milestone table) |
| unresolved state | `CONTEXT.md` | `CONTEXT.md` (Ledgerkit's is explicitly throwaway/overwritten — same overwrite discipline, no accretion) |
| user-visible change | `CHANGELOG.md` | `CHANGELOG.md` |
| CodeCompass issue | *(n/a — CodeCompass has no "upstream" of its own)* | actionable CodeCompass report → **this repository's** review process (`codecompass-feedback-ingestion.md`) |
| unsupported observation | discard | discard |

## 5. CodeCompass discovery usage + context-evaluation workflow [GENERIC]

Unchanged from CodeCompass's own Stage-B methodology
(`context-quality-evaluation.md`, `reference-project-protocol.md` §2):
a genuine task from the adopting project's *own* roadmap; CodeCompass
context captured verbatim; an independent evaluator (inspecting the
target directly, never validating CodeCompass with CodeCompass) rates
PASS/PASS WITH GAPS/FAIL and LOW/MODERATE/HIGH advantage; friction
becomes a candidate observation, not an immediate fix.

## 6. Documentation lifecycle [GENERIC]

Incremental maintenance during normal phases (update affected docs,
compatibility records, architecture, project state in the same commit);
blank-slate reconstruction at major milestones (ask "what documentation
would this project need if none existed today", reconstruct from
authoritative evidence, reconcile against current docs, allow
rewrite/consolidate/split/replace/delete); ADRs (or the adopting
project's equivalent — Ledgerkit's `knowledge/DECISIONS.md`) as
append-only decision history; git tags/releases as the historical
archive, not duplicated active documentation.

## 7. Independent completion gating [GENERIC]

Per-phase: an independent audit (CodeCompass's `release-phase-auditor`
shape) re-runs verification and checks every Definition-of-Done
condition, rather than trusting the implementer's own report; a `FAIL`
blocks completion; the auditor never repairs what it audits. This is the
single most load-bearing property in CodeCompass's own experience —
`release-phase-auditor` caught a real gap on every phase it ran during
Stage A (Phases 41, 42, 43, 43b, 43c) — and is the first thing worth
adopting even before a full roster, if a project can only take one piece
of this blueprint.

## 8. Feedback reporting to CodeCompass [PROJECT-SPECIFIC process, GENERIC format]

Full spec: `codecompass-feedback-ingestion.md`. Ledgerkit's context
curator produces findings in CodeCompass's standard format; CodeCompass
(this repository) reviews, classifies, and decides — Ledgerkit never
directly edits CodeCompass in response to its own friction (this task's
explicit rule, and consistent with `reference-project-tester`'s existing
"never silently repairs CodeCompass to make its own evaluation pass"
rule, generalised to a second project doing the reporting).

## 9. What this blueprint deliberately does not standardise

- **Exact roster size or names** for the adopting project — §1 is a
  mapping exercise, not a mandate. A smaller project may run 3 roles; a
  larger one might eventually need more, added the same evidence-gated
  way CodeCompass added its 8th.
- **The adopting project's own file layout** — Ledgerkit's `knowledge/`
  folder is not replaced by `decisions/`; the *lifecycle*, not the
  *filesystem shape*, is what's generic.
- **Whether the adopting project needs a `context-health-planner`
  equivalent** — that role only exists because CodeCompass consumes its
  own context graph; it is not a general agent-led-development
  requirement, it's specific to being the tool that generates the
  context in question.

## 10. Revision policy

This blueprint is itself subject to the learning lifecycle: real friction
from Ledgerkit adopting it becomes a candidate observation like anything
else (`codecompass-feedback-ingestion.md` covers the CodeCompass-facing
half of that; Ledgerkit's own knowledge-curator equivalent handles the
Ledgerkit-facing half). Expect this document to be revised after Stage B
(Phase 47) with whatever Ledgerkit's actual adoption experience surfaced
— it is deliberately not treated as finished on first write.
