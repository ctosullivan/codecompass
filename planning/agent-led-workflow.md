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

   **Whenever a dispatched agent's report will need to be referenced by
   a later dispatch this same phase** (a multi-agent comparison such as
   baseline/treatment, or any downstream evaluator/auditor role that
   will need to see it), **write that report to disk immediately on
   receipt** — before drafting any further dispatch prompt, whether or
   not that later prompt has been drafted yet. Treat this as the default
   action taken the moment a report arrives, not a rule to recall later
   while writing the prompt that will reference it. Confirmed necessary
   twice, in consecutive phases: `L-063` (Phase 75) and `L-064` (Phase
   76, the very next phase that needed the rule) each involved a
   dispatch prompt falsely claiming a fresh subagent could see
   conversation-only content — in both cases a "never claim X" caveat
   added only to step 7 (the point of *drafting* the dispatch prompt)
   was not consulted before writing the very next prompt it governed.
   Moving the actionable step to the point of report *receipt* (here)
   removes the need to recall a prohibition at the moment of temptation;
   step 7's own existing rule still applies as a second line of defense,
   but should not be relied on as the only place this discipline lives.
6. **Implement or coordinate implementation.** The lead implements
   directly, or dispatches one `general-purpose` implementer subagent per
   the `v0.2-implementation-execution-plan.md` pattern (foreground, exact
   plan, run its own `pytest`/`ruff`, report).

   **Before asking the user to type, `export`, or otherwise enter a real
   credential or secret via an interactive `!` shell command for this
   agent's own subsequent tool use, verify with a harmless probe that
   the proposed mechanism actually bridges the user's shell into this
   agent's own tool environment** — e.g. ask the user to `export` an
   innocuous test value first and confirm this agent's own tool calls
   can see it (`echo $SOME_TEST_VAR`), *before* requesting the real
   secret. Neither shell environment variables nor a config file (e.g.
   `~/.pypirc`) written from the user's interactive shell are guaranteed
   to bridge into this agent's own tool-call environment, and discovering
   that only *after* asking for the real value risks the value being
   typed directly into the visible conversation transcript. Confirmed at
   Phase 70 (`L-046`): a malformed `export` command exposed a real PyPI
   token in the transcript once, before the isolation was understood; no
   misuse occurred (the token was rotated as a precaution) but the probe
   above would have caught the isolation harmlessly first. If the probe
   shows no bridge exists, do not ask for the real secret at all — hand
   the credential-requiring action itself to the user's own shell instead
   (the token/secret never needs to enter this agent's own context), the
   posture Phase 70 ultimately used correctly.
7. **Obtain independent testing/evaluation.**
   - Internal phase → `release-phase-auditor` (read-only DoD check).
   - Reference-project phase → `reference-project-tester` (friction) +
     `context-evaluator` (context-quality report, inspecting the target
     directly).
   The lead **re-verifies independently regardless**: re-run
   `pytest`/`ruff`, read the actual diff for the core logic change,
   confirm the changed-file list matches the plan's Files section.

   **A dispatch prompt must never claim a fresh subagent already has
   access to content that exists only in the dispatching session's own
   conversation history** — a fresh subagent has no visibility into
   prior turns or tool results of the dispatching session unless that
   content is pasted directly into the dispatch prompt or written to a
   file the subagent can read. When a multi-agent comparison (e.g.
   baseline/treatment) produces reports a downstream evaluator will need
   to reference, write each prior agent's full report to disk
   immediately on receipt (e.g. under
   `planning/reference-projects/<project>/`), before dispatching the
   downstream evaluator, and point it at the file path rather than
   asserting the content is "already in this conversation." Confirmed at
   Phase 75 (`L-063`): a `context-evaluator` dispatch prompt claimed
   exactly this, incorrectly; the evaluator's own independent
   ground-truth methodology absorbed the gap harmlessly that time, but
   this should not be relied on twice, and neither scratch clone in that
   instance retained any fallback trace of either prior agent's work.
   **See also step 5's own receipt-time action, added after this rule's
   first real-world violation at Phase 76 (`L-064`).**
8. **Reconcile current documentation.** Dispatch `docs-maintainer` with
   the phase diff. It fixes wrong paragraphs (not appends caveats),
   deletes false statements, runs the deterministic doc checks.
9. **Independent docs-drift audit.** Dispatch `docs-reconstructor` in
   per-phase mode with the phase diff (not `docs-maintainer`'s summary).
   It reports `NO DRIFT` or a list of current-truth doc sentences the
   change made false. Any finding → back to `docs-maintainer` (step 8),
   then re-audit. `NO DRIFT` is fine and common for a `planning/`- or
   internal-only phase. **State explicitly in the dispatch prompt that
   its report must be written to
   `planning/retros/_drift-audit-phase-N.md`** — do not rely on
   `docs-reconstructor.md`'s own agent-definition file to guarantee the
   write happens. A first dispatch of this exact step at Phase 72
   produced a substantive verbal finding but no persisted file, caught
   only by `release-phase-auditor`'s independent DoD audit, not by any
   step in this workflow's own sequence (`L-056`).
10. **Reconcile roadmap and context state (interim).** Dispatch
    `roadmap-context-curator`: overwrite `CONTEXT.md` and add the
    `CHANGELOG.md` entry reflecting implementation + docs-audit progress
    so far. **Do not flip the `ROADMAP.md` row to `done` here** —
    `CLAUDE.md` §5's DoD requires the retro (step 11), triage (step 12),
    and completion audit (step 13) to all exist first, and none of them
    do yet at this point in the sequence. This step keeps `CONTEXT.md`
    current mid-phase; it is not the phase's final reconciliation.
    **This must be a real dispatch of `roadmap-context-curator`, not the
    lead editing `ROADMAP.md`/`CONTEXT.md`/the plan file's own Status
    line directly** — hand-patching these files yourself removes the one
    check whose entire charter is "never mark a phase `done` because
    code was written... only if every DoD condition actually holds; if
    one doesn't, say so and leave it not-done" (`.claude/agents/roadmap-context-curator.md`),
    letting the lead's own momentum toward calling something finished go
    unchecked. Confirmed a real, repeated failure at Phases 70-74
    (`L-060`): the lead self-served every `ROADMAP.md`/`CONTEXT.md`/plan-
    file edit directly for five consecutive phases, and twice flipped a
    `ROADMAP.md` row and plan-file Status line to `done` (step 14's own
    action) before step 13's completion audit had run at all — this is
    the same failure step 11's own `L-006` cross-reference already warns
    against ("don't hand-patch the planning docs yourself; that
    drifts"), recurring here at the phase-completion transition
    specifically, the single highest-stakes place for it to recur.
    `scripts/check_user_docs.py::check_done_phases_have_audit_report`
    and `check_context_not_stale_about_pending_audit` now catch the
    observable symptom mechanically, but dispatching the actual role
    remains the right fix, not a check to satisfy after the fact.
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
    fix the named gaps, or re-scope with a new ADR, then re-audit. **A
    `PASS WITH NON-BLOCKING OBSERVATIONS` verdict's own named
    observations, once fixed, still require a fresh confirmation pass
    before flipping to `done`** — "non-blocking" describes that specific
    verdict's own gate decision, not a license to skip verifying the fix
    it named. **Any substantive commit landing after a stored verdict
    and before the `done`-flip — fixing an observation, or anything
    else that touches audited scope — voids that verdict**; re-audit
    against the new state rather than treating the earlier PASS as still
    covering it. Confirmed necessary at Phases 73/74 (`L-060`): a
    `PASS WITH NON-BLOCKING OBSERVATIONS` verdict's one named finding
    (two stale citations) was fixed in a further commit that was never
    itself re-audited before the state was pushed — the fix could
    equally have introduced a new problem, and nothing would have caught
    it.

    **One explicit, narrow exemption to "any commit voids the verdict"**
    (`CLAUDE.md` §5, corrected post-Phase-76-closeout): the terminal
    `roadmap-context-curator` reconciliation commit itself — flipping
    `planning/ROADMAP.md`'s phase row to `done`, overwriting
    `planning/CONTEXT.md`'s current-state section, and updating the
    phase plan file's own Status line, **and nothing else** — is not
    "audited scope" for this purpose, since the audit is required
    precisely so this commit can be made; treating it as self-
    invalidating made the gate impossible to ever satisfy, a real,
    confirmed contradiction (Phase 76's own post-closeout corrective
    pass). Concretely: only on a verdict obtained *against the exact
    state about to be marked `done`* does the lead **re-dispatch
    `roadmap-context-curator` for the final reconciliation** — flip the
    `ROADMAP.md` row to `done` now that every DoD condition genuinely
    holds, and confirm `CONTEXT.md` reflects the retro/triage/audit
    outcomes. **Before treating the phase as done, the lead reads the
    curator's actual diff (`git diff --stat` is sufficient) and confirms
    it touches only those three named targets** — no `CHANGELOG.md`
    content change, no `docs/`/`architecture/`/`decisions/*` edit, no
    `src/`/test change, no `planning/learnings/**`/
    `planning/context-gaps/**` edit, no other file. If the curator's own
    commit touches anything outside that enumerated set, the audit is
    voided exactly as any other post-audit commit would void it, and
    must be repeated against the new state before `done` is genuinely
    reached. Only once this check passes does the lead commit
    (`type(phase-N): summary`, no AI attribution — `CLAUDE.md` §7) and
    move to the next phase.

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
