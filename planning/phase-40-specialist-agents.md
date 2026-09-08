# Phase 40: Specialist agent roster + lead workflow

**Status:** done (2026-09-09)

## Outcome note

- Gate G4 approved (user: "Proceed"). `CLAUDE.md` gained §8 (agent-led
  model), a §1 paragraph (curator/gate touchpoint), a §5 DoD amendment
  (learning triage + independent audit + context-eval for
  reference-project phases), and a §6 milestone-group bullet. Mirrored
  into `CONTRIBUTING.md`. This landed A1+A2+A3+A4 together rather than
  splitting A2 to Phase 42.
- `.claude/agents/` created: `context-evaluator`,
  `reference-project-tester`, `docs-maintainer`,
  `roadmap-context-curator`, `knowledge-curator`, `docs-reconstructor`,
  `release-phase-auditor`. `planning/agent-led-workflow.md` written
  (12-step procedure + trivial-change fast path + conflict resolution).
- Small forced fix: `scripts/check_user_docs.py::check_readme_phase_count`
  now excludes the "Redefined CodeCompass v1" ROADMAP section (Stage
  A–F phases are a process milestone, not product) + regression test.
  Captured as candidate learning **L-001**.
- **Live smoke delegation deferred:** not spawned speculatively (standing
  "don't spawn agents unless asked" instruction). The roster's first
  real exercise is Phase 41, whose DoD already requires a
  `release-phase-auditor` pass. Agent files validated structurally
  (frontmatter, name==filename, tool sets).

Stage A. Creates the specialist agent definitions and the fresh-session
workflow doc. Design: `planning/v1-redefinition/agent-led-development.md`.

## Depends on

- Phase 39 done (`0049` accepted).
- **G4 (agent-related parts)** — approve `CLAUDE.md` §8 (draft A3) and
  the §1 touchpoint (draft A1) in
  `planning/v1-redefinition/proposed-governance-changes.md`. §5 (A2) can
  land here or in Phase 42 — coordinate with the user.

## Scope

**In scope:**

- Create `.claude/agents/` with one definition per roster member
  (`agent-led-development.md` §2), frontmatter per role (model, tools,
  isolation, write scope):
  - `context-evaluator.md`
  - `reference-project-tester.md`
  - `docs-maintainer.md`
  - `roadmap-context-curator.md`
  - `knowledge-curator.md`
  - `release-phase-auditor.md`
  - `docs-reconstructor.md` (created now, exercised only at milestones)
- Each definition encodes: its question/deliverable, its method, its
  **read/write boundaries** (the §3 table), its independence requirement,
  what artifact it returns, and the explicit prohibitions (no `CLAUDE.md`,
  no `decisions/*`, no `src/`; evaluators never use CodeCompass to check
  CodeCompass; auditor/tester never repair what they judge).
- `planning/agent-led-workflow.md` — the 12-step fresh-session procedure
  (`agent-led-development.md` §7), written so a cold session can follow it
  without this conversation.
- Apply the approved `CLAUDE.md` §8 + §1 diff (gate G4) — presented again
  as the exact final diff before writing, per `CLAUDE.md` §0.
- Mirror the approved subset into `CONTRIBUTING.md`.
- ADR: none new (covered by `0049`), unless a roster/permission tradeoff
  surfaces during writing.

**Explicitly deferred / out of scope:**

- `planning/learnings/` operationalisation — Phase 41.
- Documentation-lifecycle tooling — Phase 42.
- Actually running a full phase through the workflow — Phase 43.
- Any `src/` change.

## Design decisions

- **Seven definitions, ~4–5 active per phase.** `docs-reconstructor` and
  `context-evaluator`/`reference-project-tester` are dormant until their
  stage. Creating them now keeps the roster reviewed as one set.
- **GATE DA (Phase 43) is expected to prune.** Do not over-engineer the
  briefs — they will be revised after the first real use.
- **Tool scoping is real, not advisory.** Where the harness supports
  per-agent `tools:` frontmatter, evaluator/auditor/reconstructor get
  no-Edit/no-Write-outside-their-report configs. This is the direct
  mitigation of the `v0.2-implementation-execution-plan.md` subagent
  incident.
- **`roadmap-context-curator` is the only agent that writes
  `ROADMAP.md`/`CONTEXT.md`/`CHANGELOG.md`** — keeps cross-phase state
  authored with full-arc knowledge (the existing undelegated-bookkeeping
  principle from `v0.2-implementation-execution-plan.md` step 4, now
  assigned to a dedicated agent rather than kept on the lead).

## Files

- `.claude/agents/context-evaluator.md` — new
- `.claude/agents/reference-project-tester.md` — new
- `.claude/agents/docs-maintainer.md` — new
- `.claude/agents/roadmap-context-curator.md` — new
- `.claude/agents/knowledge-curator.md` — new
- `.claude/agents/release-phase-auditor.md` — new
- `.claude/agents/docs-reconstructor.md` — new
- `planning/agent-led-workflow.md` — new
- `CLAUDE.md` — §8 added, §1 touchpoint added (gate G4, §0 approval)
- `CONTRIBUTING.md` — mirror
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` — updated
  by `roadmap-context-curator`

## Verification

- Each agent file loads without error (the harness lists it as an
  available agent type).
- **Smoke delegation:** lead dispatches `roadmap-context-curator` with
  "summarise current project state and the next approved phase"; it
  returns a summary consistent with `ROADMAP.md`/`CONTEXT.md`; lead
  independently confirms. Round-trip works.
- **Boundary check:** dispatch `context-evaluator` with a trivial task
  and confirm (by its tool availability / a deliberate probe) it cannot
  Write outside its report path.
- `CLAUDE.md` diff applied matches exactly what was approved; `git diff
  CLAUDE.md` reviewed against the approved text.
- `python scripts/check_user_docs.py --strict` clean.
- `pytest` / `ruff check .` clean.

## Done when

Standard DoD + verification above + the first candidate learning(s) from
this phase captured in `planning/learnings/inbox.md` (even though
curation is still manual until Phase 41).
