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
| `docs-reconstructor` | per-phase docs-drift audit (every phase); blank-slate reconstruction (milestones) | its report / `planning/v1-docs-reconstruction/` | yes |
| `context-health-planner` | forward-looking "is the graph adequate for upcoming phases" assessment | `planning/context-health.md` only | partial |

**No agent** writes `CLAUDE.md`, `decisions/*`, or `src/`. The lead owns
those (ADRs via `CLAUDE.md` §2's process; `CLAUDE.md` via §0;
`src/` directly or via an ad-hoc `general-purpose` implementer subagent).
The **lead** authors the phase retro (step 11) — no agent does.

A typical internal phase uses `roadmap-context-curator`, `docs-maintainer`,
`docs-reconstructor` (drift audit), `knowledge-curator`, and
`release-phase-auditor`. A reference-project phase adds
`reference-project-tester` and `context-evaluator`.

## The 14 steps

1. **Inspect the repository.** `git log`, `git status`, the test state.
   **Before the first commit of a session, check whether any
   session-level or environment-provided convention (e.g. a default
   commit-attribution trailer) conflicts with an already-loaded,
   higher-precedence project rule.** `CLAUDE.md` always wins over a
   generic environment default per its own §0 — but that precedence
   only protects the project if something actually prompts the
   comparison. Confirmed necessary at Phase 65 (`L-038`): a session-wide
   attribution-trailer default silently contradicted `CLAUDE.md` §7 for
   32 commits, several already pushed to shared history before the
   conflict was noticed and could not be cleanly undone. No mechanical
   check catches this (`check_user_docs.py` does not inspect commit
   trailers); only an explicit comparison at session start does.
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
   - **If any CodeCompass context was retrieved, add a
     `planning/context-observations/` entry** before moving on (Phase 52,
     `planning/context-observations/TEMPLATE.md` — supersedes the old
     `context-use-log.md` 4-liner): what was retrieved, the edge
     identity, the edge-correctness/task-usefulness split, what the
     *default pathway* (grep / file read / `--help`) would have
     surfaced, a LOW/MODERATE/HIGH advantage rating
     (`context-quality-evaluation.md` §5), and whether anything was wrong
     or misleading. **If no CodeCompass context was used this phase, log
     a one-line "not used — <why>" entry** (also a datapoint). This is
     lighter than a `context-evaluator` report on purpose. (Phase 43c,
     reshaped Phase 52.)
   - **If you notice a relationship CodeCompass *should* represent but
     mechanical detection can't produce**, file a
     `planning/context-gaps/` entry (`decisions/0051` — it never enters
     `context-graph.db`; it feeds GATE DB/DD). (Phase 43c.)
   - Before a phase that leans on CodeCompass context (a reference-project
     phase, or Phase 60), dispatch **`context-health-planner`** for a
     forward-looking adequacy assessment (`planning/context-health.md`).
   - **Also dispatch `context-health-planner` at every stage boundary**
     (Stage C→D, the Stage E-skipped transition into Stage F, Stage F→G,
     and any future boundary `planning/v1-redefinition/roadmap.md`'s own
     stage grouping defines) — not only immediately before a phase that
     leans on CodeCompass context. This closes a real gap between the
     role's own charter (`.claude/agents/context-health-planner.md`'s
     frontmatter, and `agent-led-development.md` §2.9, both already state
     "stage boundaries" as part of this role's cadence) and this step's
     own prior text, which named only the context-leaning-phase trigger —
     the cadence existed in name, in two documents, but was never
     operationalized here. Confirmed necessary at Phase 67 (`L-041`):
     `planning/context-health.md` went 21 phases (46-66), spanning at
     least three real stage boundaries, without an update, because
     nothing in this step ever invoked the cadence the role's own
     definition already promised. A stage boundary with no material
     change since the last assessment is a valid dispatch outcome too —
     an explicit one-line "no action — nothing changed since the last
     assessment" entry in `planning/context-health.md`'s own History
     section is sufficient; this bullet does not require a full
     re-assessment report every single time, only that the check
     actually happens.
5. **Delegate bounded specialist work.** One agent = one artifact. Give
   each a self-contained prompt (the phase plan path, exact scope, what
   to return). Run in the background unless the next step strictly
   depends on the result. **If two different specialist roles must both
   contribute to one shared report file, never dispatch both to `Write`
   that path concurrently** — `Write` replaces the whole file, so
   whichever call lands second always wins regardless of instructions to
   "check the file's current state first," and the loss is silent: the
   earlier agent's own success report gives no signal that its content
   was later overwritten. Sequence them instead — one agent `Write`s the
   file first, and only once its dispatch has fully completed is the
   second told to `Edit`-append its section — or, if both must genuinely
   run concurrently, give each its own file and merge them afterward
   once both complete. (Phase 46 — L-018.)

   **If this phase created a new `.claude/agents/*.md` file in this same
   session, its real type name may not be immediately dispatchable.**
   The dispatcher's own agent registry appears to load at some point
   other than "the moment the file exists," and there is no known way to
   force a refresh. Observed at Phase 54c: the first dispatch of a
   newly-created type failed with `Agent type '<name>' not found`
   despite the file already being committed to the working tree; the
   same type dispatched correctly later in the same session, for reasons
   not visible from within the session. Do not treat the first failure
   as a blocker — fall back to dispatching `general-purpose` with the
   new role's full brief embedded in the prompt for that first pass, and
   retry the real type name on a later dispatch; it has, so far, always
   become available later in the same session. (Phase 54c — L-023.)

   **Before dispatching a milestone-scoped agent brief (one exercised
   once per milestone rather than every phase — e.g. `docs-reconstructor`
   MODE 2), re-read it against every ADR/decision landed since its own
   last edit.** A brief exercised rarely is structurally more likely to
   have drifted behind a later ADR amendment than one exercised every
   phase, because normal use never forces a re-read. Confirmed twice: at
   Phase 63D (`context-researcher.md`, `docs-reconstructor.md` MODE 1,
   both amended pre-dispatch for `decisions/0060`) and at Phase 64
   (`docs-reconstructor.md` MODE 2, same ADR, same pre-dispatch fix).
   Neither mechanical check catches this; only re-reading the brief
   while writing the plan that will dispatch it does. (Phase 64 —
   L-036.)

   **Any phase that splits work across multiple parallel, independently-
   dispatched agent clusters must include an explicit post-dispatch
   consistency pass — after all clusters land, before closing the
   phase — checking for agreement, contradiction, and duplication
   across cluster boundaries.** This is a distinct step from each
   cluster's own within-scope correctness, and from any dedicated
   adversarial-review dispatch (e.g. `domain-skeptic`) that may also
   run against the integrated result. Confirmed twice: Phase 63D
   (`domain-skeptic` dispatched against the integrated corpus, not each
   cluster separately) and Phase 64 (an explicit lead synthesis pass,
   named in the phase's own plan in advance) each caught something —
   independent corroboration in one case, a duplicate-vs-corroboration
   distinction in the other — that no single cluster's own review would
   have surfaced. (Phase 64 — L-035.)

   **Never suggest, in a dispatch prompt, that a target agent may make an
   exception to its own hard, unconditional write-boundary rule — even
   for a case that looks obviously safe.** A role's write-boundary rule
   (e.g. `domain-skeptic`'s "never edits the approved domain corpus,
   under any circumstance, including to fix something you find wrong")
   exists precisely because "this specific case is obviously fine" is a
   judgment call the role itself is not supposed to make — a dispatch
   prompt that invites the exception is a real drafting mistake even if
   the agent's own charter holds and no harm results. Confirmed at Phase
   66 (`L-039`): a dispatch prompt to `domain-skeptic` suggested "you may
   resolve this yourself... a one-line citation fix is not a change to
   any claim's own meaning"; the agent correctly declined and named the
   fix instead, but the prompt itself should never have offered the
   exception. Before dispatching any role with an unconditional
   "never edits X" or "its report only" write column (the roster table
   above), re-read the prompt for any suggestion — however small — that
   the role could act outside that boundary this one time.
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
9. **Independent docs-drift audit.** Dispatch `docs-reconstructor` in
   per-phase mode with the phase diff (not `docs-maintainer`'s summary).
   It reports `NO DRIFT` or a list of current-truth doc sentences the
   change made false. Any finding → back to `docs-maintainer` (step 8),
   then re-audit. `NO DRIFT` is fine and common for a `planning/`- or
   internal-only phase.
10. **Reconcile roadmap and context state (interim).** Dispatch
    `roadmap-context-curator`: overwrite `CONTEXT.md` and add the
    `CHANGELOG.md` entry reflecting implementation + docs-audit progress
    so far. **Do not flip the `ROADMAP.md` row to `done` here** —
    `CLAUDE.md` §5's DoD requires the retro (step 11), triage (step 12),
    and completion audit (step 13) to all exist first, and none of them
    do yet at this point in the sequence. This step keeps `CONTEXT.md`
    current mid-phase; it is not the phase's final reconciliation.
    **If this phase's work must be presented to the actual user/domain
    owner for approval before the phase can be called done** (a
    Domain-stage corpus, a `design.md` needing sign-off, or any other
    mid-phase human-decision gate), **dispatch `roadmap-context-curator`
    once more immediately before that presentation**, not only at step
    10's own regular interim point. This pass must cover the same scope
    as any other reconciliation (the phase's own `planning/phase-N-*.md`
    Status line and the `ROADMAP.md` row, not `CONTEXT.md` alone) —
    updating `CONTEXT.md` correctly while leaving `ROADMAP.md`/the plan
    file's own Status line stale is a real, visible inconsistency a human
    reviewer will notice before the lead does, confirmed at Phase 63D
    (`L-034`): `CONTEXT.md` said "corpus complete, awaiting approval"
    while `ROADMAP.md` and the phase plan still said "not started"/"plan
    only," caught only by the actual user's own review.
11. **Write the phase retro.** The lead authors
    `planning/retros/phase-N-<slug>.md` from `TEMPLATE.md` — **where we
    are** (arc/stage context, what the previous phase set up, state now),
    goal, delivered vs planned + deviations, what was achieved, **what
    worked** (keep doing) / **what didn't work** (stop / fix), lessons
    learnt, process-improvement feedback, candidate learnings filed,
    **where we're going** (next phase(s), gate ahead, trajectory
    confirmed/changed), time/cost. A few lines for a trivial phase. Only
    the lead can write this (only the lead saw the whole phase).
    **If the retro schedules a follow-up phase, amends the roster or
    workflow, or otherwise changes the plan** — re-dispatch
    `roadmap-context-curator` after writing it (step 10's reconciliation
    is now stale). Don't hand-patch the planning docs yourself; that
    drifts (GATE DA, Phase 43 — L-006).
12. **Triage candidate learnings.** Dispatch `knowledge-curator` over
    every candidate the phase raised **and the retro's contents**:
    promote / retain / merge / discard, with drafts for promotions and
    `promoted.md` pointer lines. **The curator has no Bash** — whenever
    its edits to `planning/learnings/**` are meant to clear a mechanical
    check (`check_user_docs.py`, a test), its final message must end with
    an explicit "**lead: run `<command>` to confirm**" line, and the
    lead runs it before accepting the triage. (GATE DA, Phase 43 —
    L-002.)
13. **Obtain independent completion audit.** `release-phase-auditor`
    final pass: re-runs verification, checks all DoD conditions
    (including the drift audit ran + the retro exists), checks for
    protected-file drift and scope creep. Verdict `PASS` / `PASS WITH
    NON-BLOCKING OBSERVATIONS` / `FAIL`.
14. **Refuse to mark work complete when the gate fails.** A `FAIL` →
    fix the named gaps, or re-scope with a new ADR, then re-audit. Only
    on `PASS` (or `PASS WITH NON-BLOCKING OBSERVATIONS`) does the lead
    **re-dispatch `roadmap-context-curator` for the final
    reconciliation** — flip the `ROADMAP.md` row to `done` now that every
    DoD condition genuinely holds, and confirm `CONTEXT.md` reflects the
    retro/triage/audit outcomes — then commit (`type(phase-N): summary`,
    no AI attribution — `CLAUDE.md` §7) and move to the next phase.

## When a candidate learning blocks phase verification

Sometimes a candidate learning *is* the thing failing the plan's
verification step (e.g. a `check_user_docs.py` finding that a promotion
wasn't logged). The 14-step order assumes triage (step 12) comes after
the retro (step 11) so the curator can mine it — but here triage has to
happen earlier to unblock verification. That's fine: run an early
`knowledge-curator` pass to resolve the blocking candidate, finish
verification, write the retro, then do a **short follow-up triage** of
any candidates the retro itself surfaces. Don't force the strict order.
(First seen in Phase 41 — L-001 blocked the test suite; see that phase's
retro.)

## Conflict resolution

When two agents disagree (e.g. `docs-maintainer` and
`roadmap-context-curator` on whether a phase is done; `context-evaluator`
says FAIL but `reference-project-tester` found the context useful), the
**lead** resolves it on the evidence and records the resolution — a
candidate learning at minimum, plus a `CONTEXT.md` note.

## Trivial-change fast path

For a genuinely one-line change (a doc typo, a pointer, a single-line
config fix) the full loop is overkill. Fast path: lead implements → lead
runs `pytest`/`ruff`/`check_user_docs --strict` → lead does the drift
check inline (a one-line change rarely drifts a doc; note it either way)
→ `roadmap-context-curator` updates `CONTEXT.md`/`CHANGELOG.md` → lead
writes a 3-line retro (`planning/retros/phase-N-*.md`: goal, "shipped as
planned", "no process notes") → lead's explicit self-confirmation stands
in for the auditor (per `CLAUDE.md` §5's "or, for a trivial phase, an
explicit lead confirmation") → commit. `knowledge-curator` triage is
still run if the change raised any learning. If in doubt whether a change
is trivial, it isn't — use the full loop.

## Persistent agent memory

Specialist agents may keep persistent memory to work effectively across
invocations. It is a working aid, **never a source of truth** — canonical
knowledge lives only in reviewable repository artifacts and external
evidence. If an agent's memory and the repo disagree, the repo wins and
the divergence is filed as a candidate learning (it usually means a
promotion step was skipped).
