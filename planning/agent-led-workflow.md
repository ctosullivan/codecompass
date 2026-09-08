# Agent-led workflow — the per-session procedure

How a fresh Claude Code session runs a phase of CodeCompass work, as
project lead, using the specialist agents in `.claude/agents/`. Referenced
by `CLAUDE.md` §8. Design rationale:
`planning/v1-redefinition/agent-led-development.md`.

This complements — does not replace — `planning/v0.2-implementation-execution-plan.md`'s
subagent-delegation-with-independent-verification pattern. That document's
core rule still holds: **verify independently, every time, not just when
something feels off.**

## The roster (`.claude/agents/`)

| Agent | Role | Writes | Independent? |
|---|---|---|---|
| `roadmap-context-curator` | planning-state truth (`ROADMAP.md` / `CONTEXT.md` / `CHANGELOG.md`) | `planning/**`, `CHANGELOG.md` | no |
| `docs-maintainer` | current-truth docs vs verified implementation | `docs/`, `architecture/`, `README.md`, `ai-docs/`, `CONTRIBUTING.md` | no |
| `knowledge-curator` | project-learning lifecycle (`planning/learnings/`) | `planning/learnings/**`, `planning/` drafts | no |
| `reference-project-tester` | exercise CodeCompass on a real project; file friction | `planning/learnings/**`, `planning/reference-projects/**` | partial |
| `context-evaluator` | rate context quality by inspecting the target directly | its report only | yes |
| `release-phase-auditor` | read-only Definition-of-Done audit | its report only | yes |
| `docs-reconstructor` | blank-slate doc reconstruction (milestones only) | `planning/v1-docs-reconstruction/` only | yes |

**No agent** writes `CLAUDE.md`, `decisions/*`, or `src/`. The lead owns
those (ADRs via `CLAUDE.md` §2's process; `CLAUDE.md` via §0;
`src/` directly or via an ad-hoc `general-purpose` implementer subagent).

A typical internal phase uses 3 agents (`roadmap-context-curator`,
`docs-maintainer`, `release-phase-auditor`) plus `knowledge-curator`. A
reference-project phase adds `reference-project-tester` and
`context-evaluator`.

## The 12 steps

1. **Inspect the repository.** `git log`, `git status`, the test state.
2. **Establish current project state.** Dispatch `roadmap-context-curator`
   with "summarise current state + the next approved phase". It returns a
   reconciled statement (current phase, blocking gate if any, next step).
3. **Identify the next approved work.** A phase with a
   `planning/phase-N-*.md` file, an open `ROADMAP.md` row, and every
   human-decision gate against it (`planning/v1-redefinition/README.md`
   §7) resolved. If a gate is open, stop and ask the user — do not
   proceed on assumption.
4. **Retrieve useful CodeCompass context** where dogfooding it would
   plausibly help this phase (query the graph, read a generated Skill).
   Capture anything surprising as a candidate learning.
5. **Delegate bounded specialist work.** One agent = one artifact. Give
   each a self-contained prompt (the phase plan path, exact scope, what
   to return). Run in the background unless the next step strictly
   depends on the result.
6. **Implement or coordinate implementation.** The lead implements
   directly, or dispatches one `general-purpose` implementer subagent per
   the `v0.2-implementation-execution-plan.md` pattern (foreground, exact
   plan, run its own `pytest`/`ruff`, report).
7. **Obtain independent testing/evaluation.**
   - Internal phase → `release-phase-auditor` (read-only DoD check).
   - Reference-project phase → `reference-project-tester` (friction) +
     `context-evaluator` (context-quality report, inspecting the target
     directly).
   The lead **re-verifies independently regardless**: re-run
   `pytest`/`ruff`, read the actual diff for the core logic change,
   confirm the changed-file list matches the plan's Files section.
8. **Reconcile current documentation.** Dispatch `docs-maintainer` with
   the phase diff. It fixes wrong paragraphs (not appends caveats),
   deletes false statements, runs the deterministic doc checks.
9. **Reconcile roadmap and context state.** Dispatch
   `roadmap-context-curator` (phase-end job): flip the `ROADMAP.md` row
   *only if every DoD condition holds*, overwrite `CONTEXT.md`, add the
   `CHANGELOG.md` entry.
10. **Triage candidate learnings.** Dispatch `knowledge-curator` over
    every candidate the phase raised: promote / retain / merge / discard,
    with drafts for promotions and `promoted.md` pointer lines.
11. **Obtain independent completion audit.** `release-phase-auditor`
    final pass: re-runs verification, checks all DoD conditions, checks
    for protected-file drift and scope creep. Verdict `PASS` / `PASS WITH
    NON-BLOCKING OBSERVATIONS` / `FAIL`.
12. **Refuse to mark work complete when the gate fails.** A `FAIL` →
    fix the named gaps, or re-scope with a new ADR, then re-audit. Only
    on `PASS` (or `PASS WITH NON-BLOCKING OBSERVATIONS`) does the lead
    commit (`type(phase-N): summary`, no AI attribution — `CLAUDE.md` §7)
    and move to the next phase.

## Conflict resolution

When two agents disagree (e.g. `docs-maintainer` and
`roadmap-context-curator` on whether a phase is done; `context-evaluator`
says FAIL but `reference-project-tester` found the context useful), the
**lead** resolves it on the evidence and records the resolution — a
candidate learning at minimum, plus a `CONTEXT.md` note.

## Trivial-change fast path

For a genuinely one-line change (a doc typo, a pointer, a single-line
config fix) the full loop is overkill. Fast path: lead implements → lead
runs `pytest`/`ruff`/`check_user_docs --strict` → `roadmap-context-curator`
updates `CONTEXT.md`/`CHANGELOG.md` → lead's explicit self-confirmation
stands in for the auditor (per `CLAUDE.md` §5's "or, for a trivial phase,
an explicit lead confirmation") → commit. `knowledge-curator` triage is
still run if the change raised any learning. If in doubt whether a change
is trivial, it isn't — use the full loop.

## Persistent agent memory

Specialist agents may keep persistent memory to work effectively across
invocations. It is a working aid, **never a source of truth** — canonical
knowledge lives only in reviewable repository artifacts and external
evidence. If an agent's memory and the repo disagree, the repo wins and
the divergence is filed as a candidate learning (it usually means a
promotion step was skipped).
