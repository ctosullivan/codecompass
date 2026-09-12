# Redefined-v1 roadmap — Stages A–G (phases 39–70)

Companion to [`README.md`](README.md). This is the roadmap-level detail;
`planning/ROADMAP.md` carries the at-a-glance status table (updated in the
same commit as this package, per `CLAUDE.md` §2, with the new milestone
group appended — historical tables untouched, no renumbering of phases
0–38 or 24–25).

**Amended 2026-09-12** (`realignment-2026-09.md`, gate G11): Stage B is
now **Ledgerkit**, not Technical Clipper; a new Stage F runs Technical
Clipper as a later cross-ecosystem regression check; two new Stage A
bridge phases (43d, 43e) were added. Phases 39–43c are **unchanged,
`done`, not renumbered** — only phases 44 onward (none started; no
`phase-45.md`+ files exist yet) were renumbered, same precedent as the
Phase-9→16 "Retire `Depth`" reorder this project already did once. Full
rationale: `realignment-2026-09.md`.

## Scope labels

Every phase carries one:

- **COMMITTED** — will happen; only the human-decision gates in
  `README.md` §7 can stop it.
- **EXPERIMENTAL** — the *activity* is committed, the *findings* are not;
  its outputs are candidate learnings, not architecture.
- **CONDITIONAL** — happens only if a named gate resolves in favour; may
  be dropped entirely.
- **DEFERRED** — on the roadmap, not scheduled; revisit trigger named.

## How this maps onto the existing roadmap

| Existing | Disposition |
|---|---|
| Phases 0–38 (`done`) | Unchanged. Collectively the **foundation**. Historical tables in `ROADMAP.md` stay as-is. |
| Phase 23 Part B (publish, paused) | **Superseded.** Gate G2 → G2-b: no release happens until Phase 70 (renumbered from 67 by the 2026-09-12 realignment). Phase 23's row is marked "Part A done; Part B superseded — first publish is redefined v1 (Phase 70)". |
| Phase 24 (chat routing/rollup) | **DEFERRED.** Revisit as a Stage C candidate iff Stage B finds project-root context routing is a recurring need. Not renumbered. |
| Phase 25 (MCP server) | **DEFERRED.** Revisit post-redefined-v1, informed by real CLI/Skill usage. Not renumbered. |
| "v1.0 scope notes" in `ROADMAP.md` | Retitled "foundation-release scope notes" (wording only; no content deleted). |

---

## STAGE A — Redefine v1 & make CodeCompass agent-led  · COMMITTED

Goal: CodeCompass is developed by a lead session + a small specialist
agent team, with continuous doc/roadmap maintenance, systematic learning
capture, and an independent completion audit — proven on a real change.

Time tripwire: if Stage A exceeds ~6 working sessions, re-scope (the
roster is probably too big — prune per GATE DA). **Actual:** Phases
39–43 took ~5 sessions; GATE DA passed with no pruning. Phases 43b + 43c
(user-requested, ~1–2 sessions each) push the total past the tripwire —
but the cause is added scope, not roster bloat (43c does add an 8th
agent, `context-health-planner`, but with a specific named concern and
user approval — not drift), so the tripwire's remedy (prune) doesn't
apply. Noted, not a concern.

### Phase 39 — Reconcile repo state + versioning realignment · COMMITTED
- **Plan:** `planning/phase-39-reconcile-v1-redefinition.md`
- **Depends on:** gates G1 ✅, G2 ✅ (→ G2-b), G3, G5.
- **Does:** ratify this package; apply the versioning realignment
  (`pyproject.toml` `1.0.0` → `1.0.0.dev0`); restructure `ROADMAP.md`
  (append Stage A–F group, retitle foundation notes, mark Phase 23 Part B
  superseded, defer 24/25); move approved ADR drafts (`0048`, `0049`)
  into `decisions/`. **No release, no tag, no dated CHANGELOG section**
  (G2-b). No `src/` changes.
- **Exit:** `ROADMAP.md` shows the new group; `pyproject.toml` reads
  `1.0.0.dev0`; ADRs `0048`/`0049` committed; `[Unreleased]` still
  undated.

### Phase 40 — Specialist agent roster + lead workflow · COMMITTED
- **Plan:** `planning/phase-40-specialist-agents.md`
- **Depends on:** gate G4 (agent-related parts), G5 (`0049`).
- **Does:** create `.claude/agents/*.md` for the approved roster
  (`agent-led-development.md` §2 — start minimal: `context-evaluator`,
  `reference-project-tester`, `docs-maintainer`,
  `roadmap-context-curator`, `knowledge-curator`, `release-phase-auditor`;
  `docs-reconstructor` created here but only exercised at milestones).
  Write `planning/agent-led-workflow.md` (the fresh-session procedure —
  12 steps as first written; grew to 14 in Phase 41 with the drift-audit
  and retro steps). Add the `CLAUDE.md` §8 draft to the G4 diff.
- **Exit:** agents load; a smoke delegation (lead → `roadmap-context-curator`
  → verify) round-trips; workflow doc committed.

### Phase 41 — Project-learning lifecycle · COMMITTED
- **Plan:** `planning/phase-41-learning-lifecycle.md`
- **Depends on:** G4 (§8 learning parts), G5.
- **Does:** finalise `planning/learnings/` (README + inbox + template +
  `promoted/` log); wire `knowledge-curator` to it; ADR `0050`
  (learning-lifecycle) if the curation rules involve a non-obvious
  tradeoff. `docs-sync` skill extended with a learnings-hygiene check
  (stale candidates, missing provenance).
- **Exit:** one real observation from Phases 39–40 captured as a candidate
  learning end-to-end and triaged (promote/retain/discard) by the curator.

### Phase 42 — Documentation lifecycle · COMMITTED
- **Plan:** `planning/phase-42-documentation-lifecycle.md`
- **Depends on:** G4 (DoD parts).
- **Does:** write `planning/documentation-lifecycle.md`'s process into an
  operational form — `docs-maintainer` agent brief; a
  `scripts/check_user_docs.py` extension for deterministic doc checks
  (link validity, example-command validity, ADR-status coverage);
  define the **milestone documentation closeout gate** (11 steps as
  built) as a checklist file `planning/milestone-closeout-checklist.md`.
  No blank-slate reconstruction yet (that is Phase 60).
- **Exit:** deterministic doc checks run green on the current repo;
  closeout checklist committed; `docs-maintainer` used for real on the
  Phase 42 doc changes themselves.
- **Status:** done (2026-09-10). `--strict` clean; 543 passed / 1
  skipped; drift audit NO DRIFT; `release-phase-auditor` PASS WITH
  NON-BLOCKING OBSERVATIONS.

### Phase 43 — Dogfood the agent-led loop · COMMITTED
- **Plan:** `planning/phase-43-dogfood-agent-led-workflow.md` +
  `planning/phase-43a-query-skills-widen-kinds.md` (the change spec).
- **Depends on:** 40, 41, 42.
- **Did:** user chose the `query skills` widening (surface `cursor_mdc` +
  `slash_command` rows — closes the Phase 17 gap; the first
  `src/codecompass/` change since the redefinition began). Ran it through
  the full **14-step workflow** (`planning/agent-led-workflow.md`).
- **Status:** done (2026-09-10). Full suite 545 passed / 1 skipped;
  drift audit NO DRIFT; `release-phase-auditor` **PASS WITH NON-BLOCKING
  OBSERVATIONS** after a 3-round trail — **FAIL → FAIL → PASS** (first
  pass: 3 planning-doc bookkeeping gaps; re-audit #1: the CONTEXT fix left
  the file self-contradictory on Phase 43's status; re-audit #2: PASS).
  Every gap was planning-doc bookkeeping the lead hand-patched after the
  `roadmap-context-curator`'s step-10 pass went stale, none a code defect
  — the evidence behind **L-006**.
- **Exit / GATE DA — passed.** The agent-led model works: **roster stays
  at 7, no pruning** (`context-evaluator` / `reference-project-tester`
  carried forward, first use is Stage B). **4 amendments landed this
  phase:** (1) `planning/agent-led-workflow.md` step 12 + the
  `knowledge-curator` brief — curator "lead runs the confirming check"
  handoff (from L-002); (2) `docs-maintainer` brief "check if a file is
  generated before editing" (from L-005); (3) `docs-maintainer` brief
  "fix, don't caveat" may mean *delete the paragraph* (retro lesson 3);
  (4) `planning/agent-led-workflow.md` step 11 + the
  `roadmap-context-curator` brief — re-dispatch the curator after a
  plan-changing retro and reconcile *every* planning doc incl. this file
  (`v1-redefinition/roadmap.md`), from **L-006**. Two `check_user_docs.py`
  rules from GATE DA (`check_no_deleted_names_as_live` from L-003/L-004;
  `check_generated_artifacts_match_source` from L-005) scheduled as
  **Phase 43b**, to run before Phase 44. Candidate learning **L-006**
  filed this phase (the curator reconciles at step 10, before the retro,
  but a GATE/retro can change the plan) — a `candidate`, its disposition
  confirmed at Phase 43b's triage. Retro:
  `planning/retros/phase-43-dogfood-agent-led-workflow.md`.

### Phase 43b — Standing doc-drift checks (from GATE DA) · COMMITTED
- **Plan:** `planning/phase-43b-standing-doc-drift-checks.md`
- **Depends on:** 43 (GATE DA).
- **Does:** implement the two `check_user_docs.py` rules GATE DA decided —
  `check_no_deleted_names_as_live` (the standing-content complement to the
  diff-scoped per-phase drift audit) and
  `check_generated_artifacts_match_source`. A ~1-session tooling phase;
  runs before Stage B so the drift gaps found during Stage A are closed
  first.
- **Status:** **done (2026-09-11).** Both checks live in
  `scripts/check_user_docs.py` (14 rules total, 46 tests in that module,
  +9), clean (0 findings) against this repo's own docs;
  `.claude/skills/docs-sync/SKILL.md` lists them as items 13-14. The
  in-implementation judgment call (fix `architecture/overview.md` §C's 4
  self-contradictions now, or defer to Phase 61) resolved **in favour of
  fixing now** — all 4 corrected and verified against `src/` directly,
  closing that part of L-004's Phase-61 obligation early
  (`architecture-split-candidates.md` §C, Count 36→32 outstanding).
  Verifying the plan's own retired-names list against `src/` surfaced a
  correction to GATE DA's own proposal: `_RAW_TEXT_CHAR_CAP`/
  `_DOCS_FILE_CAP` were never actually deleted (only re-attributed from
  `grounded_description.py` to `enrichment.py`); only
  `_ESTIMATED_COST_PER_CALL_USD` was renamed. Independently re-verified:
  `pytest` 554 passed / 1 skipped (was 545, +9), `ruff` clean,
  `check_user_docs.py --strict` clean; `docs-reconstructor` per-phase
  drift audit → **NO DRIFT** (`planning/retros/_drift-audit-phase-43b.md`).
  `knowledge-curator` triage: L-004 → `promoted`, L-005's invariant half →
  `promoted`, L-003 → stays `retained` (flagged for the Phase 47 bulk
  review), L-008 (new) → `retained`; a follow-up dispatch also closed
  L-006's outstanding disposition (`promoted`; carried over from Phase 43,
  landed in `f6cc86d`, not this phase's own commit).
  `release-phase-auditor` → **PASS WITH NON-BLOCKING OBSERVATIONS**
  (`planning/retros/_audit-phase-43b.md`) — no blocking gap; 4 non-blocking
  observations (stale "triage has not yet run" wording in `CONTEXT.md` /
  the plan / this file; the retro's "Where we're going" pre-empting the
  verdict; L-006 missed by the first triage pass; commit-hash
  placeholders), all addressed in this closeout commit. Retro:
  `planning/retros/phase-43b-standing-doc-drift-checks.md`.

### Phase 43c — Agent context-suggestion pathways + context-health planning · COMMITTED
- **Plan:** `planning/phase-43c-agent-context-pathways.md`
- **Depends on:** 43 (GATE DA). Independent of 43b — either order, both
  before Phase 44. Requested by the user 2026-09-11.
- **Does:** a **Stage A→B bridge** — instrument the agent-led dev process
  so CodeCompass's *own* development produces context-quality signal
  (the same signal Stage B gathers from Technical Clipper, starting now):
  (1) `planning/context-gaps/` — a capture pathway for relationships an
  agent believes CodeCompass should represent but mechanical detection
  cannot; (2) `planning/context-use-log.md` + a `agent-led-workflow.md`
  step-4 amendment — a per-use record of what CodeCompass context gave vs.
  what the agent's *default pathway* (grep / read / `--help`) would have,
  rated LOW/MODERATE/HIGH (`context-quality-evaluation.md` §5); (3)
  `planning/context-health.md` + a proposed **`context-health-planner`**
  agent — a forward-looking "is the context adequate for the upcoming
  roadmap" assessment. `decisions/0051`: agent-suggested context is
  captured as reviewable candidates, **never written to
  `context-graph.db`** — the determinism-first boundary
  (`decisions/0031`/`0037`/`0045`) applied to a new input source.
- **Boundary:** **no `src/codecompass/` change.** No agent-inference
  edges, no task-oriented retrieval feature — those are Stage C
  (Phase 48/49, GATE DB) / Stage E (Phase 56/57, GATE DD), each with an
  ADR. This phase builds the pathways and gathers evidence for those
  gated decisions (`conditional-generalisation.md` §2.1/§2.4/§2.6).
- **Human-decision point:** the `context-health-planner` agent —
  approve an 8th agent, or keep it a lead/curator function? (GATE DA said
  "roster stays at 7" re: pruning, not adding.) **Resolved 2026-09-11:
  8th agent approved (Option A).**
- **Status:** **done (2026-09-11).** All deliverables built
  (`planning/context-gaps/` + `CG-001`, `planning/context-use-log.md` +
  step-4 amendment, `planning/context-health.md`,
  `.claude/agents/context-health-planner.md`, `decisions/0051` Accepted,
  briefs + `agent-led-development.md` §2.9/§3/§7 +
  `conditional-generalisation.md` §1.2). `--strict` clean; `pytest` 545
  passed / 1 skipped; `ruff` clean; no `src/` or test change.
  `docs-reconstructor` drift audit → NO DRIFT.
  `knowledge-curator` triage: `CG-001` → `candidate` (provenance
  verified), `L-007` filed → `retained`. `release-phase-auditor` →
  **PASS WITH NON-BLOCKING OBSERVATIONS**
  (`planning/retros/_audit-phase-43c.md`). Retro:
  `planning/retros/phase-43c-agent-context-pathways.md`.
- **Tracked commitment (from the audit):** `context-health.md`'s first
  assessment was lead-written; the `context-health-planner` agent's first
  genuine solo run is **before Phase 45**, on the reference-project clone
  once registered — **now Ledgerkit** (see the Phase 45 stanza; amended
  by the 2026-09-12 realignment, was Technical Clipper).

### Phase 43d — GPL-3.0-or-later relicensing plan · COMMITTED (plan) / CONDITIONAL (mechanics)
- **Plan:** `planning/phase-43d-gpl-relicensing-plan.md`
- **Depends on:** none technically; requested by the 2026-09-12
  realignment task.
- **Does:** plans the licence transition MIT → GPL-3.0-or-later, aligning
  with `hledger`'s own confirmed `GPL-3.0-or-later` SPDX declaration
  (`realignment-2026-09.md` §1.2). Full detail:
  `licence-migration.md`. Single copyright holder, no third-party
  contributions, no bundled upstream source (`vendor/` is gitignored) —
  legally simple; the actual file edits (`LICENSE`, `pyproject.toml`,
  `README.md`) are **held behind gate G12** and do not land in this
  phase unless/until approved.
- **Exit (plan-only):** `licence-migration.md` committed; ADR draft
  `decisions/0053` staged in `proposed-governance-changes.md` §C, not yet
  written to `decisions/`.
- **Exit (mechanics, once G12 resolves):** `LICENSE`/`pyproject.toml`/
  `README.md` updated in one dated commit; `decisions/0053` moved to
  `Accepted`; `CHANGELOG.md` entry added.
- **Status:** planned (plan committed 2026-09-12; mechanics pending G12).

### Phase 43e — Reusable agent-led adoption blueprint · COMMITTED
- **Plan:** `planning/phase-43e-agent-led-adoption-blueprint.md`
- **Depends on:** Stage A complete (39–43c) — the blueprint is extracted
  from CodeCompass's own working practice, not designed fresh.
- **Does:** writes `adoption-blueprint.md` — the reusable roster/
  workflow/permissions/entry-point/knowledge-curation template Ledgerkit
  (and later projects) can adopt, with an explicit
  generic / project-specific / optional / CodeCompass-generated /
  manually-governed split. No `CLAUDE.md` change, no ADR (a planning
  artifact, same shape as Phase 43c).
- **Exit:** `adoption-blueprint.md` committed; **gate G13** (light —
  no governance-file change, but it becomes a cross-project contract
  once Ledgerkit applies it).
- **Status:** planned (content drafted 2026-09-12 as part of this
  realignment; formal phase closeout — retro, triage, audit — pending
  the user's go-ahead to execute Stage A's remaining bridge work).

---

## STAGE B — Ledgerkit baseline  · COMMITTED protocol, EXPERIMENTAL findings

**Amended 2026-09-12 — this stage was Technical Clipper; Technical
Clipper moves to Stage F.** Ledgerkit's real technical dependencies span
local Python source, the `hledger` executable, its manuals, journal
syntax, query semantics, and compatibility tests — a stronger test of
CodeCompass's distinctive value than a conventional package-graph repo
(`realignment-2026-09.md` §3). This stage's content is `ledgerkit-plan.md`
(previously written for the old Stage D slot), renumbered down, otherwise
unchanged in substance.

Goal: honest evidence on whether the *current* CodeCompass supplies
trustworthy, materially-useful context during genuine Ledgerkit
development.

Time tripwire: aim for 4–8 evaluated tasks in Phase 46; if fewer than 3
genuine tasks are available on Ledgerkit's roadmap, that itself is a
finding — proceed to Stage C early with whatever evidence exists.

### Phase 44 — Reference-project protocol + context-quality eval spec · COMMITTED
- **Plan:** `planning/phase-44-reference-project-protocol.md`
- **Does:** finalise `planning/v1-redefinition/reference-project-protocol.md`
  and `context-quality-evaluation.md` into operational form: a
  `planning/reference-projects/` directory with a `README.md` (registry),
  a per-evaluation report template, and the registration record schema
  (repo URL, pinned commit, CodeCompass revision, task, context supplied,
  eval verdict, gaps). Brief the `context-evaluator` and
  `reference-project-tester` agents against it. **Amended 2026-09-12:**
  its Files section now writes `planning/phase-45-ledgerkit-baseline.md`
  (was `phase-45-technical-clipper-baseline.md`) — no other change; the
  protocol itself was always project-agnostic.
- **Exit:** template + registry committed; a dry-run evaluation of
  CodeCompass *against its own repo* using the template produces a
  coherent report (sanity check of the instrument, not a real datapoint).

### Phase 45 — Register Ledgerkit + baseline · EXPERIMENTAL
- **Plan:** `planning/phase-45-ledgerkit-baseline.md` (written when Phase 44 done)
- **Does:** clone `ledgerkit` at a pinned commit into a scratch location
  (never into this repo); run CodeCompass against it as-is; record
  exactly what it discovers (expected: pure-Python, stdlib-only —
  near-empty package context; the real context is the `hledger`
  executable, its manuals, journal syntax, 1.52 compatibility, all
  outside CodeCompass's current model). `context-evaluator` produces a
  **baseline context-quality report** for 2–3 representative
  "what does this project depend on / what governs this behaviour"
  questions. `ledgerkit-plan.md` §1/§2 (inspection findings, confirmed
  live 2026-09-12: Milestone 5 "CLI Filter Flags" is next `[PLANNED]`).
- **Exit:** `planning/reference-projects/ledgerkit.md` created with the
  registration record + baseline report. First real datapoint on the
  redefined-v1 hypothesis (`README.md` §1.7).
- **Also (tracked from the Phase 43c audit):** the `context-health-planner`
  agent runs for the **first time for real** here — a forward-looking
  `planning/context-health.md` assessment against the freshly-registered
  Ledgerkit clone (expected honest finding: "the graph is nearly empty;
  here is what CodeCompass cannot represent", each un-representable
  dependency filed as a `planning/context-gaps/` entry per
  `decisions/0051`). Phase 43c created the agent but the lead wrote its
  first (own-repo) assessment by hand; this is its first solo run.

### Phase 46 — CodeCompass during genuine Ledgerkit tasks · EXPERIMENTAL
- **Plan:** `planning/phase-46-ledgerkit-tasks.md`
- **Does:** for each of N genuine tasks drawn from Ledgerkit's own
  roadmap (its root `ROADMAP.md` — confirmed live: **Milestone 5, "CLI
  Filter Flags", `[PLANNED]`**, wiring the existing `Query` dataclass to
  `--account`/`--date-from`/`--date-to`/`--payee`/`--depth` CLI flags
  across `balance`/`register`/`accounts`/`stats` — a genuine, real,
  already-scoped task, not one invented for this evaluation): the lead
  attempts the task *using CodeCompass context*; the
  `reference-project-tester` records friction (bypass, manual search,
  stale/incorrect/missing relationship, excess noise, un-representable
  dependency) **and** adds `planning/context-use-log.md` entries per
  `decisions/0051`'s existing instrument; the `context-evaluator`
  **independently inspects the Ledgerkit repo** (not via CodeCompass) and
  rates the supplied context per `context-quality-evaluation.md`
  (PASS / PASS WITH GAPS / FAIL + LOW/MODERATE/HIGH advantage). Ledgerkit's
  own context-curator role (`adoption-blueprint.md` §1) — if adopted by
  this point — files any actionable finding per
  `codecompass-feedback-ingestion.md`.
- **Exit:** one evaluation report per task under
  `planning/reference-projects/ledgerkit/`; any `validation/codecompass/findings/CC-LK-NNN`
  filed.

### Phase 47 — Consolidate recurring friction · EXPERIMENTAL → decision
- **Plan:** `planning/phase-47-consolidate-findings.md`
- **Does:** `knowledge-curator` reviews all Phase 45–46 candidate
  learnings, `planning/context-gaps/` entries, and any
  `validation/codecompass/findings/` reports; promotes anything with
  recurrence/evidence to a **confirmed finding**; maps each to a roadmap
  implication.
- **Exit / GATE DB:** a written findings summary
  (`planning/reference-projects/ledgerkit/findings.md`) + a decision
  (gate G6) on which Stage C phases are funded and their scope. **Valid
  outcomes include "advantage is LOW across the board — fund no Stage C
  improvements; proceed to deeper Ledgerkit dogfooding (Stage D) to test
  the broader hypothesis directly"** and **"advantage is already HIGH —
  minimal Stage C, go straight to hardening."**

---

## STAGE C — Improve the existing product  · CONDITIONAL on GATE DB

Each phase below exists **only if** GATE DB's findings support it. Scope
is set by the findings, not pre-written here. Sketches only — unchanged
in substance from the pre-realignment plan, now Ledgerkit-driven instead
of Technical-Clipper-driven.

### Phase 48 — Task-oriented context retrieval · CONDITIONAL
- If "context is dependency-centric, not task-centric" recurs: add a
  retrieval entry point that takes a task description and returns a small
  context map (local impl + callers/callees + relevant tests + dep +
  version + APIs used + relevant docs + relevant ADRs + known gaps),
  built from graph joins already present + whatever minimal new edges the
  findings justify. ADR required. Optimise for small + high-confidence +
  routes to evidence, not completeness.

### Phase 49 — Graph / context quality · CONDITIONAL
- If "stale/incorrect/misleading relationship" or "excess noise" recurs:
  targeted fixes — dependency-use relationship precision, context
  selection/ranking, noise reduction, freshness surfacing. Each backed by
  a specific confirmed finding. Also where a `planning/context-gaps/`
  entry reaches `recurred` (`decisions/0051`) and is promoted here.

### Phase 50 — Shared-agent context / entry-point improvements · CONDITIONAL
- If "specialist agents re-discover the same relationships" recurs:
  a common grounded project map the roster consumes, or a refinement to
  the Claude-entry-point hierarchy (`adoption-blueprint.md` §3). Hard
  constraint (`README.md` §1.9, R6): must not become opaque alternative
  project-memory — canonical knowledge stays in reviewable artifacts;
  this only indexes/connects them.

### Phase 51 — Re-run Ledgerkit evaluation · EXPERIMENTAL
- Re-run Phase 46's task evaluation(s) (same tasks, same instrument)
  after Stage C changes.
- **Exit / GATE DC:** did measured context quality / advantage improve?
  If not, revert or defer the Stage C changes that didn't pay off.
  **If Stage D evidence later proves weak, the plan may legitimately
  terminate near here: a measured improvement over the foundation
  (phases 0–38) baseline, re-validated on a real external project, is a
  defensible redefined v1 — proceed to Stage F/G and ship it as `1.0.0`
  (`README.md` R14).**

---

## STAGE D — Deeper Ledgerkit dogfooding  · EXPERIMENTAL

Goal: decide whether v1 scope must exceed package-source grounding,
using continued real Ledgerkit Core development (not a one-off baseline
task) as the evidence source.

### Phase 52 — Continue genuine Ledgerkit Core development · EXPERIMENTAL
- Further real Ledgerkit tasks beyond Phase 46's single baseline task
  (its own roadmap's next milestones after Milestone 5, confirmed live
  at this phase — the repo will have moved). Apply the agent-led
  adoption blueprint (`adoption-blueprint.md`) if not already applied at
  Stage B. Continues feeding `planning/context-use-log.md`,
  `planning/context-gaps/`, and `validation/codecompass/findings/`.

### Phase 53 — Heterogeneous doc / reference / manual dependencies · EXPERIMENTAL
- Test whether CodeCompass can usefully index + relate *reference
  material* (hledger manuals, journal-format spec, command docs) to
  Ledgerkit's local implementation and compatibility tests — as evidence
  nodes with provenance, without a schema commitment. `ledgerkit-plan.md`
  §"Doc/reference test".

### Phase 54 — External executable / behavioural context · EXPERIMENTAL
- Ledgerkit-specific tooling (not CodeCompass) runs `hledger`, builds
  fixtures, does differential tests — the hledger executable remains an
  **independent behavioural oracle** throughout, per
  `licence-migration.md` §4, regardless of the relicensing. CodeCompass's
  role under test: can it *consume and relate* that evidence ("behaviour
  X: documented by manual §Y, observed by experiment Z, implemented by
  ledgerkit/foo.py, verified by test_bar")? `ledgerkit-plan.md`
  §"Behavioural test". Also measures the **usefulness** (not just
  correctness) of any agent-suggested relationships this generates,
  per `decisions/0051`'s two-property evaluation (correctness/confidence
  vs. context usefulness — a relationship can be true but not useful).

### Phase 55 — Decide on broader abstractions + refine the blueprint · EXPERIMENTAL → decision
- **Exit / GATE DD (gate G7):** a written decision
  (`planning/reference-projects/ledgerkit/findings.md`) answering:
  is a generalised technical-dependency concept necessary for v1? is
  first-class provenance/evidence necessary? **What is the smallest model
  that covers the demonstrated need?** Approve the abstraction ADR(s) or
  record "not justified — package-source model + Stage C improvements is
  v1". `conditional-generalisation.md` structures this decision.
- **Also:** revise `adoption-blueprint.md` with whatever Ledgerkit's
  actual adoption experience surfaced (`adoption-blueprint.md` §10) —
  the blueprint is not treated as finished after Phase 43e's first draft.

---

## STAGE E — Implement the minimum justified generalisation  · CONDITIONAL on GATE DD

Only the abstractions GATE DD names. `conditional-generalisation.md`
carries candidate designs; none is committed here.

### Phase 56 — Technical-dependency abstraction · CONDITIONAL
- Introduce the minimal generalisation (e.g. a `technical_dependency`
  concept with a small closed `kind` set — `package` + whatever else
  earned it). Additive schema change; `package` stays a first-class kind.
  ADR required.

### Phase 57 — Provenance / evidence features · CONDITIONAL
- Introduce only the provenance distinctions GATE DD justified (e.g.
  distinguishing source-derived fact / doc statement / observed behaviour
  / test result / ADR / agent inference; per-claim version + evidence
  route + confidence state). Not the full `Dependency`/`Evidence`/
  `Observation`/`Claim`/`Verification`/`Decision` ontology unless
  demonstrably required.

### Phase 58 — Migrate package/source functionality into the final model · CONDITIONAL
- `migration.md` §3: npm/PyPI/Cargo discovery, pinned vendor source,
  usage analysis, the graph, generated Skills, `query`/`check`/`undo`,
  `chat` — all keep working. Prefer wrapping over rewriting. Any CLI
  breaking change → gate G8 + its own ADR.

### Phase 59 — Re-validate against Ledgerkit · EXPERIMENTAL
- Re-run the Ledgerkit evaluation scenarios (Phases 46/53/54) against the
  generalised model.
- **Exit / GATE DE:** existing capability preserved, new capability
  proven (Ledgerkit context advantage moved up). FAIL → fix or narrow
  Stage E before Stage F. **Technical Clipper regression is deliberately
  a separate stage (F, next)** — do not fold it in here; a change that
  looks fine against Ledgerkit alone may still be accounting-specific.

---

## STAGE F — Cross-ecosystem regression: Technical Clipper  · COMMITTED protocol, EXPERIMENTAL findings

**New stage (2026-09-12 realignment).** Technical Clipper was the old
Stage B; it moves here, unevaluated so far (Stage B never ran against it —
confirmed: `planning/reference-projects/` doesn't exist yet). Its role
changes from "first proof point" to **the check that Ledgerkit-driven
changes generalise** — package/vendor context still strong, relationship
types generalise, no accounting-specific overfit, entry points still
lean, ordinary modern repositories still cheap to navigate. This stage's
content is `reference-project-protocol.md`'s existing Technical-Clipper
material (§1, §2.3's task pool, §3's outputs), renumbered down, otherwise
unchanged in substance — do not invent new Technical Clipper product
work merely to create a test; use its existing, still-real backlog
(confirm live at Phase 60 — its state may have moved since the 2026-09-09
inspection).

### Phase 60 — Register Technical Clipper + baseline · EXPERIMENTAL
- Same shape as Phase 45, against `technical-clipper` at a pinned commit,
  confirmed live at this phase. `reference-project-protocol.md` §1/§2.1.

### Phase 61 — Genuine Technical Clipper task(s) · EXPERIMENTAL
- One or more real tasks from Technical Clipper's own roadmap/deferred
  work (`reference-project-protocol.md` §2.3's candidate pool, reconfirmed
  live), run against the **post-Ledgerkit-evolved** CodeCompass. Same
  procedure as Phase 46 (`reference-project-protocol.md` §2.4).

### Phase 62 — Consolidate: does it generalise? · EXPERIMENTAL
- `knowledge-curator` + `context-evaluator` assess: package/vendor
  context still strong; relationship/evidence concepts introduced by
  Stage E generalise beyond accounting/hledger; no excessive noise from
  new abstractions; generated entry points remain useful; ordinary
  modern repositories still cheap to navigate (this task's explicit
  overfitting checklist).

### Phase 63 — Decision · EXPERIMENTAL → decision
- **Exit / GATE DF (new):** fix only *general* problems supported by
  evidence — a Technical-Clipper-specific special case is not a valid
  Stage E/F output. If a genuine regression is found, it blocks Stage G
  until fixed or explicitly, narrowly scoped away with its own ADR.

---

## STAGE G — v1 consolidation  · COMMITTED once F completes

**Renumbered from the old Stage F** (was Phases 60–67; now 64–70) to make
room for the new Stage F above. Content unchanged except one addition
(an explicit self-dogfood confirmation folded into Phase 67, not a
separate phase — Stages D and F already did the heavy Ledgerkit/Technical
Clipper re-validation work, so this stage's version is a final
confirmation, not a repeat). (If Stage D/E were skipped per GATE DD,
Stage G runs against the Stage C product instead — the checklist is
identical.)

### Phase 64 — Blank-slate documentation reconstruction · COMMITTED
- `docs-reconstructor` agent, deliberate blank-slate posture
  (`documentation-lifecycle.md` §"Blank-slate reconstruction"). Produces a
  **shadow doc proposal** under `planning/v1-docs-reconstruction/`, not an
  overwrite.

### Phase 65 — Architecture + ADR reconciliation · COMMITTED
- Reconcile `architecture/overview.md` against current reality; ADR
  status review (mark superseded ADRs, don't rewrite them). Decide
  retain/rewrite/consolidate/split/replace/remove per doc
  (`documentation-lifecycle.md` §"Reconciliation").
- **Concrete input:** `planning/v1-redefinition/architecture-split-candidates.md`
  (the `docs-maintainer`'s Phase 42 catalogue). **§C's 4
  self-contradictory items were already fixed at Phase 43b** — only
  §A/§B's 32 remaining history-shaped passages are this phase's job.

### Phase 66 — Roadmap + context reconciliation · COMMITTED
- `roadmap-context-curator`: `ROADMAP.md` + `CONTEXT.md` reflect the
  shipped v1; deferred work (Phases 24/25, anything dropped at gates)
  clearly parked with revisit triggers.

### Phase 67 — Final validation: self-dogfood + Ledgerkit + Technical Clipper · EXPERIMENTAL (gates v1)
- A **lightweight confirmation pass**, not a full re-run (Stages D and F
  already did that work): re-verify CodeCompass's own dogfooding signal
  (`planning/context-health.md`, `planning/context-use-log.md`) is
  current; re-confirm Ledgerkit's final evaluation numbers
  (`planning/reference-projects/ledgerkit/`) and Technical Clipper's
  (`planning/reference-projects/technical-clipper/`) still hold against
  the code as shipped. Target: no FAIL verdicts on either; advantage
  MODERATE+ on the majority of tasks across both, or an explicit written
  justification for shipping below that bar.

### Phase 68 — Independent release audit · COMMITTED (FAIL blocks)
- `release-phase-auditor`, read-only, full Definition-of-Done audit
  across every Stage A–G phase's exit criteria + the milestone-closeout
  checklist. Verdicts: `PASS` / `PASS WITH NON-BLOCKING OBSERVATIONS` /
  `FAIL`. **`FAIL` prevents Phase 69/70.** Auditor does not fix anything.

### Phase 69 — Milestone closeout · COMMITTED
- `planning/milestone-closeout-checklist.md` executed: deterministic doc
  checks; reconciliation applied (Phase 64–65 decisions actioned);
  obsolete current docs removed; links/examples validated; a **milestone
  closeout report** (`planning/v1-closeout.md` — architecture summary,
  what shipped, what deferred, key ADRs, evaluation results); current-doc
  freeze.

### Phase 70 — Release redefined CodeCompass v1 · COMMITTED (gate G9)
- Drop `.dev0`: `pyproject.toml` `1.0.0.dev0` → `1.0.0`; `twine upload`
  (**the first-ever publish** — G2-b held everything until here); `v1.0.0`
  tag; `[Unreleased]` → dated `1.0.0` section; public positioning change
  (gate G10). Irreversible-action posture identical to the old Phase 23
  Part B pause.

---

## Minimum viable redefined v1 (fallback path — mitigates R14)

If evidence is weak or time runs short, the smallest thing that still
legitimately counts as "redefined v1":

1. Stage A complete (agent-led, proven — including the relicensing
   decision resolved one way or the other, and the adoption blueprint
   written).
2. Stage B complete (Ledgerkit evaluated honestly; findings published
   even if the verdict is "LOW advantage on this task").
3. At least one **measured** improvement over the foundation
   (phases 0–38) baseline, re-validated on Ledgerkit (a trimmed Stage C +
   Phase 51).
4. Stage F run at least once against Technical Clipper (confirming no
   regression from whatever Stage C changes landed), even if Stages D/E
   are skipped.
5. Stage G closeout + independent audit (Phases 64–70), scoped to what
   shipped; ship as `1.0.0` (first-ever publish).

That is a defensible v1: *"CodeCompass, built agent-led, measurably
improved on real external work, with honest published evidence of where
it does and doesn't add advantage, and confirmed not to have overfit to a
single ecosystem."* Deeper Ledgerkit dogfooding (Stage D) and
generalisation (Stage E) become v1.x if evidence doesn't clearly justify
them now. The plan should take this path rather than delay v1
indefinitely chasing the broader hypothesis.
