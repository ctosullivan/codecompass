# Phase 43: Dogfood the agent-led loop on a real change

**Status:** done (2026-09-10) — **GATE DA passed** (retro:
`planning/retros/phase-43-dogfood-agent-led-workflow.md`); roster stays at
7, no pruning, **4 amendments** landed + Phase 43b scheduled; candidate
learning **L-006** filed. `release-phase-auditor` reached PASS WITH
NON-BLOCKING OBSERVATIONS after a 3-round trail — **FAIL → FAIL → PASS**
(first pass: 3 planning-doc bookkeeping gaps — 43b ROADMAP row,
`v1-redefinition/roadmap.md` GATE DA outcome, 43b in the CONTEXT forward
path; re-audit #1: the CONTEXT fix left the file self-contradictory on
Phase 43's status; re-audit #2: PASS).

Stage A, final phase. Runs **one real, small CodeCompass change** through
the entire 14-step agent-led workflow (`planning/agent-led-workflow.md`),
then retros the roster. **GATE DA** — Stage B does not start until this
phase's retro is done and the roster/workflow amended.

**Chosen change (user, 2026-09-10):** widen `codecompass query skills` to
surface `cursor_mdc` + `slash_command` `doc_artifacts` rows (option 2
from the shortlist below) — the **first `src/codecompass/` change since
the redefinition began**. Spec:
[`phase-43a-query-skills-widen-kinds.md`](phase-43a-query-skills-widen-kinds.md).

## Depends on

- Phases 40, 41, 42 done (roster, learnings, doc lifecycle all
  operational).

## Scope

**In scope:**

- **The user picks the target change** from this shortlist (all are real,
  small, already-identified in `planning/CONTEXT.md`):
  1. Root `CLAUDE.md` → `ai-docs/README.md` one-line pointer
     (`CONTEXT.md` "Next concrete step" #3) — **note:** touches
     `CLAUDE.md`, so this doubles as a live test of the §0 approval flow
     through an agent-led phase. Good candidate for that reason.
  2. `query skills` / `graph.skills_index` surfacing `slash_command`
     rows (`architecture/overview.md` "current status of this gap";
     `CONTEXT.md`).
  3. `/discovery` written at the whole-project `sync` trigger point too
     (the documented Phase 17 gap).
  4. AI-enrichment run for the 5 pending `ai-docs/` mechanical
     relationships (`CONTEXT.md` "Next concrete step" #4) — smallest,
     but exercises the cost/consent path.
- Execute the chosen change through **every** workflow step
  (`planning/agent-led-workflow.md`):
  - `roadmap-context-curator` establishes state + confirms the change is
    approved work (write its own phase plan `planning/phase-43a-<slug>.md`
    if the change is non-trivial — a nested plan, or fold into this file
    if truly one-line);
  - lead implements (or dispatches an implementer subagent);
  - `context-evaluator` / `reference-project-tester` are **N/A** for an
    internal change — `release-phase-auditor` does the independent check
    in their place;
  - `docs-maintainer` reconciles affected docs;
  - `roadmap-context-curator` updates `ROADMAP.md` / `CONTEXT.md` /
    `CHANGELOG.md`;
  - `knowledge-curator` triages every candidate learning the phase
    produced (there will be several — this is the first full run);
  - `release-phase-auditor` full DoD audit; `FAIL` → fix + re-audit;
  - lead commits.
- **Retro** (`GATE DA`): a written assessment in
  `planning/learnings/` + a `CONTEXT.md` note answering:
  - Did each active role earn its keep? Which to prune, merge, or
    re-scope?
  - Did the auditor catch anything the lead missed?
  - Did the curator's triage produce anything worth promoting immediately?
  - Where did the workflow have friction (handoffs, unclear boundaries,
    tool-permission gaps)?
- Amend `.claude/agents/*` and `planning/agent-led-workflow.md` per the
  retro **in this phase's commit(s)**.

**Explicitly deferred / out of scope:**

- Any reference-project work — Stage B.
- More than one target change — one is the point; batching defeats the
  "prove the loop on low stakes" goal.

## Design decisions

- **One change, fully.** The value is exercising the whole loop, not the
  change itself.
- **The retro can shrink the roster.** If `docs-reconstructor` or a
  curator role added nothing, say so and mark it dormant/removed. The
  roster was always "start here, prune at GATE DA".
- **If the workflow itself proves too heavy for a one-line change**,
  that's a finding — the workflow should have a documented "trivial
  change" fast path, and this phase adds it.

## Files

- `planning/phase-43a-<slug>.md` — nested plan for the chosen change (if
  non-trivial)
- source / test / doc files for the chosen change
- `.claude/agents/*` — retro amendments
- `planning/agent-led-workflow.md` — retro amendments (+ trivial-change
  fast path if needed)
- `planning/learnings/inbox.md` + `promoted.md` — the phase's learnings
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` — curator
- `planning/v1-redefinition/roadmap.md` — GATE DA outcome recorded

## Verification

- The chosen change ships: its own verification passes; `pytest` /
  `ruff check .` clean.
- Every workflow step has a visible artifact (curator summary, auditor
  report, curator triage entries, doc reconciliation diff).
- `release-phase-auditor` final verdict is `PASS` or `PASS WITH
  NON-BLOCKING OBSERVATIONS`.
- The retro exists and names concrete roster/workflow amendments (even
  if the amendment is "no change needed — all roles earned their keep").
- `planning/CONTEXT.md` shows: Stage A complete, GATE DA passed, next =
  Phase 43b (the two `check_user_docs.py` rules GATE DA scheduled), then
  Phase 44.

## Done when

Standard DoD + verification + GATE DA retro complete + roster/workflow
amended per retro.
