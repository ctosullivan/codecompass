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

## 2. The roster

Eleven agent definitions exist; a twelfth (`domain-skeptic`, §2.13) is
planned for Phase 63D and not yet created. Only 4–5 are active in a
typical internal phase. All are `.claude/agents/<name>.md` with
model/tools/isolation frontmatter.

Started at seven, "prune at GATE DA". GATE DA (Phase 43) kept all seven
with no pruning; Phase 43c added the eighth (`context-health-planner`)
with cause — `decisions/0049` permits a roster addition that doesn't
reverse a fixed point, and GATE DA's "roster stays at 7" was about not
*pruning*, not a cap on adding. Phase 52 added the ninth
(`context-enrichment-agent`), same rationale, cause named in
`decisions/0054` — a narrow content-authoring role kept deliberately
separate from `knowledge-curator`'s investigation-only remit, not an
expansion of any existing agent's scope. Phase 54c added a tenth and
eleventh (`context-researcher`, `documentation-agent`, §2.11–2.12) —
never previously catalogued in this document, a gap corrected here
(`decisions/0060`), not a new addition at time of correction. Phase 63D
plans a twelfth (`domain-skeptic`, §2.13), same "narrow role for a job
no existing brief naturally covers" rationale as `decisions/0054`'s own.

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

### 2.7 `docs-reconstructor` — independent docs check (two modes)
The *independent* counterweight to `docs-maintainer`, who both edits the
docs and self-certifies them.

- **Per-phase drift audit (every phase, `CLAUDE.md` §5 DoD condition).**
  Read-only. Given the phase's diff (not `docs-maintainer`'s summary of
  it), find every current-truth doc sentence (`README.md`, `docs/`,
  `architecture/`, `ai-docs/`) the change made false, scoped to what
  actually changed about observable system behaviour. Verdict `NO DRIFT`
  / `DRIFT — n findings`; findings go back to `docs-maintainer`, then
  re-audit. Report at `planning/retros/_drift-audit-phase-NN.md`.
  `NO DRIFT` is fine and common for a `planning/`- / internal-only phase.
- **Blank-slate reconstruction (milestones only — Phase 64).**
  Independently reconstruct the documentation that *ought* to exist, from
  authoritative project reality (source, tests, CLI `--help`,
  config/schema, generated outputs, ADRs, current planning state) —
  deliberately as though the current narrative docs did not exist. It
  must *not* read `README.md` / `architecture/overview.md` as a starting
  structure. Output: a shadow proposal under
  `planning/v1-docs-reconstruction/` (proposed docs + `concepts-to-retire.md`).
- **Never edits** `docs/` / `README.md` / `architecture/` / `ai-docs/` /
  `CLAUDE.md` / `decisions/*` / `src/`. Findings and proposals only.
- **Tools:** read/search + Bash (read-only) + Write to its own report /
  `planning/v1-docs-reconstruction/`.
- **Active in:** every phase (drift audit); Phase 64 + future milestones
  (blank-slate).

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
  applicable; **the `docs-reconstructor` per-phase drift audit ran and
  its findings (if any) were fixed**; **a substantive phase retro exists
  at `planning/retros/phase-N-<slug>.md`**; `CHANGELOG.md` entry present
  and correct; `CONTEXT.md` reflects new state; `ROADMAP.md` marks the
  phase; **no protected-file drift**; **candidate learnings triaged**
  (incl. any from the retro); for reference-project phases, a
  context-eval report exists.
- **Tools:** read/search + run tests/lint + Write only its own audit
  report file.
- **Active in:** every phase where the lead wants an independent DoD
  check (all non-trivial phases); mandatory at Phase 65.

### 2.9 `context-health-planner` — forward-looking context adequacy (added Phase 43c)
- **Question:** is the context CodeCompass currently holds *adequate for
  the roadmap phases coming up* — fresh (recorded vs installed version,
  graph rebuilt since the last relevant change), grounded (source +
  enrichment), complete (usage + docs mapped), low-noise?
- **Method:** reads `context-graph.db` and **runs `codecompass query`**
  (read-only commands only — no `sync`, no `--yes`), cross-references
  `planning/ROADMAP.md` + `v1-redefinition/roadmap.md`. Writes
  `planning/context-health.md` and nothing else.
- **Distinct from `roadmap-context-curator`** (planning-doc *truth* —
  what's done, what's next) and **from `context-evaluator`** (per-task
  context *quality*, judged by direct inspection, never using
  CodeCompass). This agent asks "is the graph in good enough shape for
  what we're about to do".
- **Rule:** an empty / near-empty graph is a valid expected finding
  (both reference projects have ≈0 runtime deps) — it never recommends
  work to make the graph look fuller than the project warrants. If its
  read suggests a relationship is wrong or missing, it files a
  `planning/context-gaps/` candidate (`decisions/0051`), never "corrects"
  the graph.
- **Tools:** read/search + read-only `codecompass query` + Write to
  `planning/context-health.md` only. No `src/`, no `decisions/`, no
  `CLAUDE.md`, no other planning file.
- **Active in:** stage boundaries; before any phase that leans on
  CodeCompass context (reference-project phases, Phase 60).

### 2.10 `context-enrichment-agent` — agent-authored edge enrichment (added Phase 52)
- **Question:** for a `doc_relations_edges` row CodeCompass has already
  mechanically proven exists, what does it mean — a grounded
  `ai_summary`/`relation_label`, written from the real excerpted source
  text? Never whether the relationship exists at all.
- **Method:** reads `select_candidates`'s pending list (via
  `codecompass query relations` on the source doc, or direct file
  inspection), writes a grounded interpretation, calls
  `codecompass enrich apply` — the CLI itself, not agent instruction,
  rejects anything that isn't already a real, pending, mechanically
  detected candidate (`decisions/0054` §4).
- **Distinct from `knowledge-curator`**: this agent authors interpretive
  content for an edge that already exists; `knowledge-curator` never
  produces edge content, only investigates observations about edges
  (correctness/usefulness). Kept as two roles deliberately, per
  `decisions/0054`'s "separation of concerns" reasoning — the same
  reason a new narrow role was added rather than extending an existing
  one.
- **Rule:** never invents a relationship; no tool access to
  `context-graph.db` other than through `enrich apply`; no
  `src/codecompass/` writes.
- **Tools:** Read, Grep, Glob, Bash — `codecompass query`/`codecompass
  enrich apply` only; no direct DB writes, no `src/` writes.
- **Active in:** phases exercising agent-driven enrichment when no
  `ANTHROPIC_API_KEY` is available or the automated path isn't desired
  (Phase 52 on).

### 2.11 `context-researcher` — behaviour-first primary research (added Phase 54c; catalogued here `decisions/0060`)
- **Question:** for one named feature or behavioural question, what is
  actually true — derived from evidence, not assumed from documentation?
- **Method:** behaviour-first — when executable behaviour exists, runs
  representative examples/edge cases itself before reading
  documentation, then traces every real implementation path that could
  explain what was observed, never stopping at the first plausible one.
  Iterates (observe ↔ trace ↔ test ↔ refine) rather than running once.
- **Writes** structured Observation/Evidence/Claim/Derivation records
  under `planning/knowledge/<feature-slug>/` (Phase 54c's own six record
  kinds, `phase-54c-evidence-knowledge-workflow.md` §2.2) — never a
  graph fact, never a Decision (only the human/lead makes those).
- **Two applications** (`development-methodology.md`): feature-scoped
  (Phase 54c's original shape) and, from Phase 63D, project-scoped —
  investigating CodeCompass's own domain concepts for `docs/domain/`.
- **Tools:** Read, Grep, Glob, Bash, Write.
- **Active in:** any phase running the Domain stage of
  Scope→Plan→Domain→Design→Implement (Phase 60, 63D on).

### 2.12 `documentation-agent` — pre-implementation design proposal (added Phase 54c; catalogued here `decisions/0060`)
- **Question:** given an `APPROVED`-reachable knowledge base for one
  feature, what design should a human review before any code is
  written?
- **Method:** projects `design.md` — a human-readable, ordinary-language
  design document — from whatever `planning/knowledge/<feature-slug>/`
  records already exist. Never invents content the knowledge base
  doesn't already support; never softens an honest "we don't know" into
  a confident-sounding guess.
- **Distinct from `docs-maintainer`**: `docs-maintainer` reconciles
  EXISTING current-truth docs against VERIFIED implementation, post-hoc;
  this role authors a proposal FROM research, before implementation, at
  a different point in the lifecycle. `design.md` is a projection of the
  knowledge base, never an independent source of truth — it is
  regenerated from the knowledge base as that base is corrected, never
  hand-edited out of step with it (`phase-54c-evidence-knowledge-workflow.md` §5.2).
- **Tools:** Read, Grep, Glob, Write.
- **Active in:** the Design stage of Scope→Plan→Domain→Design→Implement,
  for any feature with an `APPROVED`-reachable knowledge base.

### 2.13 `domain-skeptic` — independent adversarial domain review (planned Phase 63D, `decisions/0060`, amended 2026-09-20)
- **Question:** does a domain-corpus (or `design.md`) draft actually
  hold up — every material claim evidenced, no internal contradiction,
  no missing edge case — before it reaches the actual user/domain owner?
- **Method:** reads a draft with no obligation to agree with it;
  challenges every claim lacking a citable Observation/Evidence record;
  actively searches for contradictions between concepts and for missing
  edge cases/counterexamples; attempts to resolve what it finds through
  further evidence or a real behavioural experiment (pointing
  `context-researcher` at a specific check, or running one itself)
  before treating anything as escalation-worthy; escalates to **the
  actual user/domain owner** only genuine, unresolved domain/product
  ambiguities, each with the evidence gathered, the real alternatives,
  and their consequences.
- **Escalation rule (amended 2026-09-20): no stand-in.** Neither
  `domain-skeptic` nor the lead nor any other agent may rule on a
  genuine ambiguity in the user's place, including during CodeCompass's
  own dogfooding. `domain-skeptic` has exactly two outcomes per finding:
  resolve it fully with evidence (no longer an ambiguity), or escalate
  it and leave it explicitly open pending the actual user — never a
  third option of deciding it itself. This narrows Phase 54c's own §5.1
  precedent (which permitted the lead to stand in for CodeCompass's own
  dogfooding); that allowance does not extend to this role.
- **Distinct from `context-evaluator`/`docs-reconstructor`/
  `release-phase-auditor`**: those three independently verify,
  respectively, task-context quality against a real target, documentation
  drift against verified behaviour, and Definition-of-Done conditions —
  none is scoped to "argue against a concept's own stated definition for
  internal contradiction," the job this role exists for
  (`decisions/0060`'s own "separation of concerns" reasoning, reapplied
  from `decisions/0054`).
- **Rule:** never repairs what it reviews — reports findings back,
  matching every other independent-review role's own posture. **Write
  boundary, stated precisely**: read-only toward source code,
  implementation, design content, and the approved domain corpus itself
  (`docs/domain/`) — never edits any of them, under any circumstance.
  May **only** append new Observation/Evidence records for checks it
  resolves itself (a grep, a real command, a test) — exactly like
  `context-researcher`'s own record shapes and write boundary, never a
  Claim/Derivation/Decision (those need fuller derivation work or the
  user's own ruling) — and write its own review-findings report.
  Nothing else.
- **Tools:** Read, Grep, Glob, Bash (read-only: `codecompass query`,
  tests, greps — no `sync`/`--yes`, no `enrich apply`, no
  `src/codecompass/` writes, no edits to `docs/domain/`), Write (scoped
  to exactly its own review report and `planning/knowledge/**` records
  when resolving a finding itself).
- **Not created by `decisions/0060` itself** — planned for Phase 63D's
  own implementation, per that phase's own Files section, matching how
  Phase 52 planned `context-enrichment-agent` before creating it.
- **Active in:** the Domain stage of Scope→Plan→Domain→Design→Implement,
  from Phase 63D on; re-invoked at **Phase 65** against any domain-claim
  staleness candidate accumulated since (`documentation-lifecycle.md`
  §4.1, added 2026-09-20) — the same role and write boundary, not a
  second one.

### 2.14 Roles deliberately NOT created
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
| `docs-reconstructor` | the phase diff + code/`--help` (drift audit); source/tests/CLI/schema/ADRs, not narrative docs (blank-slate) | its drift-audit report / `planning/v1-docs-reconstruction/` | CLI `--help`, tests (read-only) | **yes** — independent of `docs-maintainer` |
| `release-phase-auditor` | everything | its audit report only | tests/lint, re-runs plan verification | **yes** — read-only, no repair |
| `context-health-planner` | `context-graph.db`, `codecompass query` output, `ROADMAP.md` | `planning/context-health.md` only | read-only `codecompass query` (no `sync`/`--yes`) | partial — uses CodeCompass, writes one planning file |
| `context-enrichment-agent` | source doc excerpts, `codecompass query relations` output | nothing directly — `context-graph.db` only via `codecompass enrich apply` | `codecompass query`, `codecompass enrich apply` | no — participant, but the CLI itself enforces its trust boundary mechanically |
| `context-researcher` | everything (behaviour-first: runs real examples/commands before reading docs) | `planning/knowledge/<slug>/**` only | real examples/commands/tests as evidence | partial — independent investigation, but not adversarial toward its own findings |
| `documentation-agent` | `planning/knowledge/<slug>/**` | `planning/knowledge/<slug>/design.md` only | — | no — participant, projects from the knowledge base only |
| `domain-skeptic` (planned, Phase 63D) | source, implementation, design, approved domain corpus (read-only toward all four — never edits any) | its review report / `planning/knowledge/**` Observation-Evidence only (only when resolving a finding itself; never a Claim/Derivation/Decision) | read-only `codecompass query`, tests, greps | **yes** — independent of `context-researcher`/`documentation-agent`, never repairs what it reviews, never rules on a genuine ambiguity in the user's place |

**No agent** writes `CLAUDE.md`, `decisions/*` (except the lead via the
ADR process), or `src/` (except the lead / ad-hoc implementer subagent).
The **phase retro** (`planning/retros/phase-N-*.md`) is the lead's
artifact — no agent writes it.

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

## 6. Definition-of-Done integration (`CLAUDE.md` §5)

`CLAUDE.md` §5 was amended (gate G4, Phase 40; extended by the user's
2026-09-10 request, Phase 41). It now also requires, **per phase**:

| Added DoD condition | Owner |
|---|---|
| an independent `docs-reconstructor` per-phase **drift audit** finds no current-truth doc left misdescribing the system (findings fixed + re-audited) | `docs-reconstructor` |
| a substantive **phase retro** at `planning/retros/phase-N-<slug>.md` — every `planning/retros/TEMPLATE.md` section, incl. **Where we are** (arc/stage context) and **Where we're going** (next phase, gate ahead, trajectory); a few lines for a trivial phase | lead |
| candidate learnings (incl. any from the retro) **triaged** promote/retain/merge/discard | `knowledge-curator` |
| an independent **`release-phase-auditor` pass** (or explicit lead confirmation for a trivial phase) verifies the preceding rather than trusting the implementer's report | `release-phase-auditor` |

| Phase type | Additional |
|---|---|
| Reference-project / evaluation phase | a `context-evaluator` report exists and is linked; `reference-project-tester` findings filed as candidate learnings |
| Milestone-closeout phase (65–67) | `release-phase-auditor` verdict `PASS` / `PASS WITH NON-BLOCKING OBSERVATIONS` (a `FAIL` blocks); the milestone-closeout checklist complete |

The six original conditions are unchanged. Exact wording:
`decisions/0050` and `CLAUDE.md` §5.

## 7. The 14-step fresh-session workflow (→ `planning/agent-led-workflow.md`)

1. Inspect the repository.
2. `roadmap-context-curator` establishes current project state.
3. Identify the next **approved** work (a phase with a plan file + an
   open row + any gate resolved).
4. Retrieve useful CodeCompass context where appropriate (dogfooding);
   log the use in `planning/context-use-log.md` (LOW/MODERATE/HIGH vs the
   default pathway); file any un-representable relationship in
   `planning/context-gaps/` (`decisions/0051`); before a context-leaning
   phase, dispatch `context-health-planner`.
5. Delegate bounded specialist work.
6. Implement / coordinate implementation.
7. Obtain independent testing/evaluation (`context-evaluator` /
   `reference-project-tester` / `release-phase-auditor` as applicable);
   the lead re-verifies independently regardless.
8. `docs-maintainer` reconciles current documentation.
9. `docs-reconstructor` runs the independent per-phase drift audit;
   findings → back to step 8, then re-audit.
10. `roadmap-context-curator` reconciles `ROADMAP.md` / `CONTEXT.md` /
    `CHANGELOG.md`.
11. The **lead** writes the phase retro (`planning/retros/phase-N-<slug>.md`).
12. `knowledge-curator` triages candidate learnings (incl. the retro's).
13. Obtain independent completion audit (`release-phase-auditor`).
14. Refuse to mark work complete when the gate fails — fix, or re-scope
    with an ADR, then re-audit.
