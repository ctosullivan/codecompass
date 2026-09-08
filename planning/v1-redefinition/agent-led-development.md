# Agent-led development plan (required output 4)

How CodeCompass becomes its own first agent-led development project.
Implemented by Phase 40 (roster + workflow) and proven by Phase 43
(dogfood). Governance hook: proposed `CLAUDE.md` §8
(`proposed-governance-changes.md`), proposed `decisions/0049`.

## 1. Principles

- **Claude Code (the lead session) orchestrates. CodeCompass does not.**
  CodeCompass never spawns or coordinates agents — that is an explicit
  non-goal (`README.md` §1.9). The orchestration layer is Claude Code /
  equivalent tooling.
- **Operationalise, don't duplicate.** The agent process runs on the
  *existing* mechanisms — `CLAUDE.md`, `ROADMAP.md`, `CONTEXT.md`, ADRs,
  `architecture/`, tests, `CHANGELOG.md`, per-phase DoD, `CLAUDE.md` §0
  protected-file approval. No agent gets a private parallel system.
- **The roster is small and earns its size.** An agent exists only where
  separation of **context** (it must not see / be biased by the lead's
  working state), **responsibility** (a distinct deliverable), or
  **authority** (read-only vs write; independent vs participant) adds
  real value. GATE DA prunes roles that didn't.
- **Independent means independent.** Evaluation/audit agents inspect the
  target directly; they never validate CodeCompass *using* CodeCompass,
  and never repair what they are judging. This is the direct lesson of
  `planning/v0.2-implementation-execution-plan.md`'s recorded incident (a
  read-only research subagent deleted files) and its resulting
  "verify independently, every time" rule.
- **An agent observation is not authoritative because an agent recorded
  it.** It enters the learning lifecycle (`learning-lifecycle.md`) as a
  candidate; only curation + evidence promotes it.

## 2. The roster (start here; prune at GATE DA)

Seven agent definitions, but only 4–5 are active in a typical phase. All
are `.claude/agents/<name>.md` with model/tools/isolation frontmatter.

### 2.1 Lead Claude session (not an agent file — the human-facing session)
Responsible for: understanding the requested phase; coordinating and
integrating implementation; delegating bounded work; resolving conflicts
between agent outputs; ensuring `CLAUDE.md` process is followed; the
final commit. Holds the only write access to `src/` during a phase by
default.

### 2.2 `context-evaluator` — independent context-quality judge
- **Question:** was the context CodeCompass supplied accurate, relevant,
  sufficiently complete, current, grounded, low-noise, and *materially*
  useful — and could a fresh Claude session have gotten equivalent
  context cheaply by ordinary repo inspection?
- **Method:** inspects the **target repository directly**. Must not run
  CodeCompass to check CodeCompass. Produces a report per
  `context-quality-evaluation.md` (PASS / PASS WITH GAPS / FAIL +
  LOW/MODERATE/HIGH advantage). Treats incorrect/misleading context as
  more serious than incomplete.
- **Tools:** read/search only + a clone of the target at a pinned commit.
  No Edit/Write to the CodeCompass repo except its own report file. No
  Bash that mutates.
- **Isolation:** fresh context each evaluation; not told the lead's
  hoped-for answer.
- **Active in:** Stages B, C (Phase 51), D, F (63/64).

### 2.3 `reference-project-tester` — exercises CodeCompass on real projects
- **Finds:** dependency-discovery failures; stale context; incorrect
  relationships; missing context; misleading generated info; places the
  implementing agent bypassed CodeCompass; technical dependencies
  CodeCompass can't represent; places direct inspection was easier.
- **Rule:** does **not** silently repair CodeCompass to make its own
  evaluation succeed — it files a finding.
- **Rule:** reference work is subordinate to the reference project's own
  roadmap; never adds a feature to Technical Clipper / Ledgerkit to make
  CodeCompass easier to test.
- **Tools:** read/search + run CodeCompass against the pinned target
  clone + write candidate-learning entries + its own findings files.
  No writes to CodeCompass `src/`.
- **Active in:** Stages B, D, and re-validation phases.
- **Distinct from `context-evaluator`:** the tester *uses* CodeCompass
  and reports friction; the evaluator *ignores* CodeCompass and rates the
  output's quality against ground truth. Different bias, different tools —
  worth two roles.

### 2.4 `docs-maintainer` — incremental current-doc reconciliation
- **During ordinary implementation:** reconcile affected `docs/`,
  `architecture/`, `README.md`, `ai-docs/` against the *verified*
  implementation; rewrite poor prose; remove obsolete statements; **do
  not** just append another caveat.
- **Boundary:** current-truth docs only. Not ADRs (append-only, lead +
  ADR process). Not `CLAUDE.md` (§0). Not blank-slate reconstruction
  (that's `docs-reconstructor`, milestones only).
- **Tools:** read/search + Edit/Write on `docs/`, `architecture/`,
  `README.md`, `ai-docs/`, `CONTRIBUTING.md`. Not `decisions/`, not
  `CLAUDE.md`, not `src/`.
- **Active in:** most phases.

### 2.5 `roadmap-context-curator` — planning-state truth
- Reconciles `ROADMAP.md`, `CONTEXT.md`, phase status, newly discovered
  work, scope changes, deferred work — **from project evidence**
  (git, tests, the actual diff), not from an agent's say-so.
- **Hard rule:** never marks a phase `done` because code was written —
  only when all six DoD conditions (`CLAUDE.md` §5, as amended) hold.
- Establishes "current state / next approved work" at the *start* of a
  fresh session (workflow step 2–3).
- **Tools:** read/search + Edit/Write on `ROADMAP.md`, `CONTEXT.md`,
  `CHANGELOG.md`, `planning/**`. Not `src/`, not `decisions/`, not
  `CLAUDE.md`.
- **Active in:** every phase (bookend).

### 2.6 `knowledge-curator` — the learning lifecycle owner
- Decides, per observation: **promote** (into the artifact that owns it —
  test / ADR / architecture doc / `CLAUDE.md` proposal / Claude rule /
  skill / roadmap / `CONTEXT.md` / `CHANGELOG.md`), **retain** as a
  candidate, **merge**, or **discard**.
- Owns `planning/learnings/`. Runs the consolidation in Phases 47 and 55.
- **Does not itself write the promoted artifact's final form** where that
  needs the lead's judgement (e.g. a new ADR) — it produces the
  promotion recommendation + draft; the lead or `docs-maintainer`
  finalises. It *does* directly maintain `planning/learnings/`.
- **Tools:** read/search + Edit/Write on `planning/learnings/**` + draft
  files under `planning/`. Proposes `CLAUDE.md` changes via
  `proposed-governance-changes.md`, never edits `CLAUDE.md`.
- **Active in:** every phase (triage step 10), heavy in 47/55.

### 2.7 `docs-reconstructor` — blank-slate milestone documentation
- At **major milestones only** (Phase 60): independently reconstruct the
  documentation that *ought* to exist, from authoritative project reality
  (source, tests, CLI `--help`, config/schema, generated outputs, ADRs,
  current architecture, current planning state) — deliberately as though
  the current narrative docs did not exist.
- Output: a **shadow/temporary proposal** under
  `planning/v1-docs-reconstruction/`. Never overwrites `docs/` directly.
- **Isolation:** should *not* read the current `README.md` /
  `architecture/overview.md` narrative first — the point is a fresh
  derivation. It may read them during the *reconciliation* step, not the
  reconstruction step.
- **Tools:** read/search + Write only under `planning/v1-docs-reconstruction/`.
- **Active in:** Phase 60 (and any future milestone).

### 2.8 `release-phase-auditor` — independent Definition-of-Done audit
- Final **read-only** DoD audit — per phase where the lead wants an
  independent check (Phase 43 uses it as the stand-in for the
  evaluator/tester), and mandatorily at Phase 65.
- Verdicts: `PASS` / `PASS WITH NON-BLOCKING OBSERVATIONS` / `FAIL`.
  **`FAIL` prevents completion.**
- **Does not repair** the implementation it evaluates — files the gap
  back to the lead.
- Checks: code implemented; plan-file verification step actually passes
  (re-runs it); `docs/`/`architecture/`/`decisions/` updated as
  applicable; `CHANGELOG.md` entry present and correct; `CONTEXT.md`
  reflects new state; `ROADMAP.md` marks the phase; **no protected-file
  drift**; **candidate learnings triaged**; for reference-project phases,
  a context-eval report exists.
- **Tools:** read/search + run tests/lint + Write only its own audit
  report file.
- **Active in:** Phase 43, 65, and any phase the lead flags.

### 2.9 Roles deliberately NOT created
- No "implementer" agent — the lead implements or delegates ad hoc to a
  general-purpose subagent per the existing
  `v0.2-implementation-execution-plan.md` pattern; a standing role adds
  nothing.
- No "security" / "performance" / "test-writer" agents — these are
  activities within a phase, not separations of authority. Use
  `/security-review`, `/code-review`, etc. as skills.
- No "orchestrator" agent — that is the lead, by design.

## 3. Permissions / write boundaries (summary table)

| Agent | Reads | Writes | Runs | Independent? |
|---|---|---|---|---|
| Lead | everything | everything (commits) | everything | n/a |
| `context-evaluator` | CodeCompass repo (read), pinned target clone | its report only | read-only tools; target clone inspection | **yes** — direct target inspection, blind to hoped answer |
| `reference-project-tester` | CodeCompass repo, pinned target clone | `planning/learnings/**`, `planning/reference-projects/**` findings | CodeCompass CLI against target | partial — uses CodeCompass, files findings, no `src/` writes |
| `docs-maintainer` | everything | `docs/`, `architecture/`, `README.md`, `ai-docs/`, `CONTRIBUTING.md` | tests/lint, deterministic doc checks | no — participant |
| `roadmap-context-curator` | everything | `ROADMAP.md`, `CONTEXT.md`, `CHANGELOG.md`, `planning/**` | git log/status | no — participant |
| `knowledge-curator` | everything | `planning/learnings/**`, `planning/` drafts | — | no — participant |
| `docs-reconstructor` | source/tests/CLI/schema/ADRs (not narrative docs, until reconciliation) | `planning/v1-docs-reconstruction/` only | CLI `--help`, tests | **yes** — blank-slate |
| `release-phase-auditor` | everything | its audit report only | tests/lint, re-runs plan verification | **yes** — read-only, no repair |

**No agent** writes `CLAUDE.md`, `decisions/*` (except the lead via the
ADR process), or `src/` (except the lead / ad-hoc implementer subagent).

## 4. How results return to the lead

- Each delegated agent produces **one artifact** (a report file, a set of
  doc edits, a set of planning-file edits, a set of learning entries) +
  a short structured summary in its final message.
- The lead **independently re-verifies** before integrating — re-run
  `pytest` / `ruff`, read the actual diff, confirm changed-file list
  matches the phase plan's Files section (the existing
  `v0.2-implementation-execution-plan.md` step 2, unchanged).
- **Conflicts between agents** (e.g. `docs-maintainer` and
  `roadmap-context-curator` disagree on whether a phase is done;
  `context-evaluator` says FAIL but `reference-project-tester` found it
  useful) are resolved by the lead, on the evidence, and the resolution
  is recorded (a candidate learning at minimum; a `CONTEXT.md` note).
- Agents run in the background by default; the lead does not block on one
  unless the next step strictly depends on it.

## 5. Persistent agent memory vs. repository truth

- Specialist agents **may** keep persistent memory to work effectively
  across invocations (e.g. `context-evaluator` remembering a target
  project's layout between evaluations).
- That memory is a **working aid, never a source of truth.** Canonical
  knowledge lives only in reviewable repository artifacts + external
  evidence (`learning-lifecycle.md` §"Promote into the owning artifact").
- Recalled memory is background context, not instruction (harness rule) —
  agents verify a memory-named file/flag still exists before relying on
  it.
- If an agent's memory and the repo disagree, the repo wins and the
  divergence is filed as a candidate learning (it usually means a
  promotion step was skipped).

## 6. Definition-of-Done integration (feeds gate G4 / `CLAUDE.md` §5)

Current `CLAUDE.md` §5 has six conditions. Proposed additions, applied
**per phase type**:

| Phase type | Added DoD conditions |
|---|---|
| Any phase | `release-phase-auditor` (or the lead, for trivial phases) confirms the six existing conditions hold **independently**; candidate learnings from the phase are triaged (promote/retain/merge/discard) by `knowledge-curator`. |
| Reference-project / evaluation phase | A `context-evaluator` report exists and is linked from the phase's exit note; `reference-project-tester` findings are filed as candidate learnings. |
| Milestone-closeout phase (65–67) | `release-phase-auditor` verdict is `PASS` or `PASS WITH NON-BLOCKING OBSERVATIONS` (a `FAIL` blocks); the milestone-closeout checklist is complete. |

These are additive — the six existing conditions are unchanged. Exact
wording is in `proposed-governance-changes.md` for gate G4.

## 7. The 12-step fresh-session workflow (→ `planning/agent-led-workflow.md`, Phase 40)

1. Inspect the repository.
2. `roadmap-context-curator` establishes current project state.
3. Identify the next **approved** work (a phase with a plan file + an
   open row + any gate resolved).
4. Retrieve useful CodeCompass context where appropriate (dogfooding).
5. Delegate bounded specialist work.
6. Implement / coordinate implementation.
7. Obtain independent testing/evaluation (`context-evaluator` /
   `reference-project-tester` / `release-phase-auditor` as applicable).
8. `docs-maintainer` reconciles current documentation.
9. `roadmap-context-curator` reconciles `ROADMAP.md` / `CONTEXT.md`.
10. `knowledge-curator` triages candidate learnings.
11. Obtain independent completion audit (`release-phase-auditor`).
12. Refuse to mark work complete when the gate fails — fix, or re-scope
    with an ADR, then re-audit.
