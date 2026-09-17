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

### Phase 43d — GPL-3.0-or-later relicensing · COMMITTED
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
- **Exit (mechanics):** `LICENSE`/`pyproject.toml`/`README.md`/
  `CONTRIBUTING.md` updated in one dated commit; `decisions/0053` moved
  to `Accepted`; `CHANGELOG.md` entry added.
- **Status:** **done (2026-09-12).** Gate G12 approved ("Proceed as
  recommended"). `pip install -e .` reports `License: GPL-3.0-or-later`;
  `ruff check .` clean; `python scripts/check_user_docs.py --strict`
  clean. No historical commit/release rewritten (none exist under any
  licence).

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
- **Status:** **done (2026-09-12).** Gate G13 approved ("Proceed as
  recommended") — `adoption-blueprint.md` is the approved version handed
  to Ledgerkit.

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

**Outcome note (Phase 46 closeout, 2026-09-13):** Phase 46 evaluated
exactly **one** genuine task (query-term semantics), not 4–8 — the
tripwire's own "fewer than 3" condition is met. This is itself evidence
for Phase 47/GATE DB, not a scope failure: the single task delivered a
second independent FAIL verdict of the identical failure shape as Phase
45's baseline FAIL, which `context-quality-evaluation.md` §6 already
treats as highest-priority regardless of count, and Ledgerkit's own
roadmap moved twice across Phases 44–46 in ways that constrained how many
genuinely-scoped tasks were available to attempt. Phase 47's plan
(`planning/phase-47-consolidate-findings.md`) proceeds with this evidence
rather than waiting for more tasks, consistent with the tripwire's own
"proceed early with whatever evidence exists" instruction.

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
- **Status:** **done (2026-09-12).** `planning/reference-projects/`
  (`README.md`, `TEMPLATE-registration.md`, `TEMPLATE-evaluation.md`)
  built; `_instrument-dry-run.md` ran a real self-test (CodeCompass's own
  `typer` usage) — verdict **PASS WITH GAPS**, advantage **LOW** (no
  incorrect/misleading content, but single-symbol `query symbol` scope
  undersold `typer`'s actual usage breadth; filed as **L-012**, retained).
  `context-evaluator` / `reference-project-tester` briefs verified
  already consistent with the new templates (Phase 43c had already
  finalised them; no edit needed). `planning/phase-45-ledgerkit-baseline.md`
  written. `docs-reconstructor` drift audit → NO DRIFT;
  `release-phase-auditor` → PASS WITH NON-BLOCKING OBSERVATIONS (both
  non-blocking notes resolved/accounted for). No `src/codecompass/`
  change. Process amendment landed this phase from **L-013**:
  `agent-led-workflow.md` step 10 is now an explicit *interim*
  reconciliation (no `ROADMAP.md` `done` flip), step 14 the *final*
  done-flipping reconciliation, run after the retro/triage/audit steps.
  Retro: `planning/retros/phase-44-reference-project-protocol.md`. No
  gate blocks Phase 45.

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
- **Status:** **done (2026-09-13).** `planning/reference-projects/ledgerkit.md`
  (registration record, live-reconfirmed — Ledgerkit's own "Core
  redefinition" landed the same day as the stale desk assessment;
  Milestone 5 "CLI Filter Flags" is now `[SUPERSEDED]`, folded into a new
  Stage C) + `ledgerkit/00-baseline.md` (3 baseline questions). **Q2 is
  the redefined-v1 effort's first FAIL verdict:** a confident "not found
  in context-graph.db" for a real, current, 238-line file
  (`dev-docs/hledger-compatibility.md`) that is precisely Ledgerkit's own
  designated hledger-1.52-compatibility governance document — root cause
  `spec_docs.py::_DEFAULT_GLOBS` has no `dev-docs/**/*.md` entry, filed as
  **CG-002** (`recurred` — second occurrence of the same shape as Phase
  37's `ai-docs/` fix, this time from an external reference project) and
  a distinct symptom-layer finding **L-016** ("not found" indistinguishable
  from a typo, retained). Q1 (optional-dependencies silence, **L-015**,
  retained) and Q3 (no roadmap-summary mechanism, not a gap CodeCompass
  claims to fill) both PASS WITH GAPS / LOW advantage — honest,
  expected-thin results. `context-health-planner`'s first genuine solo run
  predicted LOW advantage for Phase 46, CG-002 load-bearing.
  `planning/phase-46-ledgerkit-tasks.md` written, explicitly hedged (see
  its own Phase 46 stanza amendment below). No `src/codecompass/` change.
  `docs-reconstructor` drift audit → NO DRIFT; `release-phase-auditor` →
  PASS WITH NON-BLOCKING OBSERVATIONS (no blocking gap; three advisory
  notes — the step-10 interim reconciliation had nothing substantive to
  say this single-session phase; the plan file's own status header now
  fixed; CG-002's context-gap-vs-learning classification is a flagged,
  defensible judgment call GATE DB inherits explicitly). Retro:
  `planning/retros/phase-45-ledgerkit-baseline.md`. No gate blocks Phase
  46.

### Phase 46 — CodeCompass during genuine Ledgerkit tasks · EXPERIMENTAL
- **Plan:** `planning/phase-46-ledgerkit-tasks.md`
- **Amended 2026-09-13 (Phase 45 closeout):** the "Does" bullet's named
  task, Milestone 5 "CLI Filter Flags", is now **stale** — Ledgerkit's own
  "Core redefinition" (discovered live at Phase 45 registration, same day
  as the desk assessment below) marked it `[SUPERSEDED]`, folded into a
  new Stage C. `planning/phase-46-ledgerkit-tasks.md`'s own recommended
  candidate is now the compat-register migration follow-up named by
  Ledgerkit's Stage A closeout — itself explicitly hedged, requiring live
  reconfirmation at this phase's own start, since Ledgerkit's roadmap has
  already moved once mid-Phase-45. Not rewriting the "Does" text below;
  treat it as superseded by this note and the plan file, per the same
  discipline this phase itself demonstrated.
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
- **Status:** **done (2026-09-13).** Reconfirmed live at phase start, as
  hedged above: Ledgerkit's Stage B closed to `[DONE]` entirely and Stage
  C opened (Phase 1 `[IN PROGRESS]`) within a day of Phase 45's pinned
  commit, so the task actually run was hledger 1.52 query-term semantics,
  not the plan's named compat-register-migration candidate — the plan's
  explicit hedge worked as designed. A live, concurrently-running
  Ledgerkit development session was producing the task's exact
  deliverable, so this phase's "attempt" was conducted as a **read-only
  evaluation exercise** (no file written into the Ledgerkit clone).
  `planning/reference-projects/ledgerkit/01-query-semantics.md` —
  **CodeCompass's second FAIL verdict**, LOW (negative) advantage, and the
  first on genuinely in-progress work rather than a spot-check question:
  CodeCompass returned a complete blank (0 vendors, "not found" for both
  `dev-docs/` files); Ledgerkit's own
  `dev-docs/planning/core-redefinition/07-query-regex.md` §7.1 already had
  the complete answer, found by one `grep` + file read. **`CG-002`**
  re-confirmed independently by both agents, extended to nested
  `dev-docs/**` paths. **`CG-003`** filed (new): the external hledger.org
  manual itself has zero CodeCompass representation, no glob fix could
  ever cover it. **`L-017`** filed (retained): a live `WebFetch` fallback
  against the real hledger.org manual needed two attempts and still
  couldn't reliably extract the relevant section — a retrieval-cost
  finding for Phase 53. `planning/phase-47-consolidate-findings.md`
  written — Stage B's decision phase (GATE DB), with a full evidence
  inventory from Phases 44–46. No `src/codecompass/` change. **What didn't
  work (retro):** dispatching `reference-project-tester` and
  `context-evaluator` concurrently to `Write` (not `Edit`) the same shared
  report path caused a silent clobber — the second `Write` replaced the
  first agent's section entirely; the lead caught it only by reading the
  file afterward and cross-referencing it against the clobbered agent's
  own returned summary, then manually reconstructed the lost section.
  Filed as **`L-018`** and **promoted** the same phase: `planning/agent-
  led-workflow.md` step 5 now explicitly forbids two agents `Write`-ing
  one shared path concurrently. `docs-reconstructor` drift audit → NO
  DRIFT; `release-phase-auditor` → PASS WITH NON-BLOCKING OBSERVATIONS (no
  blocking gap; two cosmetic observations — stale curation prose next to
  L-018's already-`promoted` status field, and a missing blank line in
  `context-use-log.md` — both fixed before commit). Retro:
  `planning/retros/phase-46-ledgerkit-tasks.md`. No gate blocks Phase 47,
  but Phase 47 itself exits at **GATE DB** — a funding decision that may
  need the user's input, not something to auto-proceed through.

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
- **Status:** **done (2026-09-13) — the label's own "→ decision" completed:
  this phase's job was pure synthesis of Phases 44–46's evidence, not new
  evaluation, and it closes once GATE DB itself resolves.**
  `knowledge-curator` produced `planning/reference-projects/ledgerkit/findings.md`
  (5 evaluated instances, 2 formal FAIL verdicts, 100% LOW advantage, the
  `_DEFAULT_GLOBS` blind spot confirmed at 3 independent occurrences) as an
  explicit recommendation, not a unilateral call. **GATE DB ratified by the
  user** ("Ratify as recommended"): fund one narrow Stage C phase closing
  `CG-002` + `L-016` (`planning/phase-49-spec-doc-coverage-and-error-disambiguation.md`,
  matching the roadmap's own pre-written Phase 49 sketch, not Phase 48's);
  Phase 48 (task-oriented context retrieval) and Phase 50 (shared-agent
  context) explicitly **not funded** — no corroborating evidence in the
  Phase 44–46 dataset; `CG-003`/`L-017` explicitly routed to Stage E/Phase
  53, not this gate. A genuine, unrelated pre-existing doc-drift fix
  (`architecture/overview.md`'s glob-list enumeration missing the Phase 37
  `ai-docs/**/*.md` addition) landed as a side effect of `docs-maintainer`'s
  review. No `src/codecompass/` change this phase (Phase 49 is
  CodeCompass's first). Verified: `pytest` 554 passed / 2 skipped, `ruff
  check .` clean, `check_user_docs.py --strict` clean. Closeout:
  `docs-reconstructor` drift audit (`planning/retros/_drift-audit-phase-47.md`)
  → **NO DRIFT**; `release-phase-auditor`
  (`planning/retros/_audit-phase-47.md`) → **PASS WITH NON-BLOCKING
  OBSERVATIONS** (no blocking gap; four advisory notes, all either already
  addressed or explicitly non-blocking). Retro:
  `planning/retros/phase-47-consolidate-findings.md`. **Stage B is now
  fully complete (Phases 44–47 all done). No gate blocks Phase 49.**

---

## STAGE C — Improve the existing product  · COMPLETE (GATE DB ratified 2026-09-13; GATE DC confirmed 2026-09-14)

Each phase below exists **only if** GATE DB's findings support it. Scope
is set by the findings, not pre-written here. Sketches only — unchanged
in substance from the pre-realignment plan, now Ledgerkit-driven instead
of Technical-Clipper-driven. **GATE DB resolved 2026-09-13** (Phase 47):
Phase 49 funded (narrow) and now `done`; Phase 48 and Phase 50 not
funded. **GATE DC resolved 2026-09-14** (Phase 51): Phase 49's fix
confirmed working, on its own narrow terms — Stage C is now **fully
complete** (Phase 48 not funded, Phase 49 done, Phase 50 not funded,
Phase 51 done). Whether to continue into Stage D or proceed toward
Stage F/G is an open strategic decision for the user (see Phase 51's
"Status" note below), not resolved by this stanza.

### Phase 48 — Task-oriented context retrieval · CONDITIONAL
- **GATE DB outcome (2026-09-13): not funded.** `planning/reference-projects/ledgerkit/findings.md`
  §4/§7: the only supporting signal is `CG-001` (own-dev, single
  occurrence) plus a "weak echo" in Phase 46's task 01 findings — not
  read as a genuine second occurrence. No retrieval entry point built
  this gate; revisit if `CG-001`'s hypothesis independently recurs.
- If "context is dependency-centric, not task-centric" recurs: add a
  retrieval entry point that takes a task description and returns a small
  context map (local impl + callers/callees + relevant tests + dep +
  version + APIs used + relevant docs + relevant ADRs + known gaps),
  built from graph joins already present + whatever minimal new edges the
  findings justify. ADR required. Optimise for small + high-confidence +
  routes to evidence, not completeness.

### Phase 49 — Graph / context quality · CONDITIONAL
- **GATE DB outcome (2026-09-13): funded, narrow.** `planning/reference-projects/ledgerkit/findings.md`
  §4/§7: `CG-002` reached `recurred` (3 occurrences: Phase 37 own-dev,
  Phase 45 + Phase 46 externally on Ledgerkit, the latter extending to
  nested `dev-docs/**` paths) — exactly this stanza's own trigger
  condition. Scope: `planning/phase-49-spec-doc-coverage-and-error-disambiguation.md`
  — add `"dev-docs/**/*.md"` to `_DEFAULT_GLOBS` (closes `CG-002`) +
  disambiguate `query relations`'s "not found" error from a genuine
  coverage gap (closes `L-016`, independently recurred twice). A more
  general `vendor.toml`-configurable glob list was explicitly considered
  and rejected as premature at this evidence threshold (2 earned hard-coded
  entries, not yet a pattern). `CG-003`/`L-017` explicitly out of scope
  (Stage E/GATE DD and Phase 53 respectively, not this gate).
- If "stale/incorrect/misleading relationship" or "excess noise" recurs:
  targeted fixes — dependency-use relationship precision, context
  selection/ranking, noise reduction, freshness surfacing. Each backed by
  a specific confirmed finding. Also where a `planning/context-gaps/`
  entry reaches `recurred` (`decisions/0051`) and is promoted here.
- **Status:** **done (2026-09-13).** Delivered exactly the narrow scope
  GATE DB funded, no more: `src/codecompass/spec_docs.py::_DEFAULT_GLOBS`
  gained `"dev-docs/**/*.md"` (closes `CG-002`), and
  `src/codecompass/cli.py` gained `_relations_not_found_error`, wired
  into `query_relations`'s not-found branch only — `query vendor`/`query
  symbol` untouched, correctly (closes `L-016`). 3 new tests. **This is
  CodeCompass's first `src/codecompass/` change driven by external
  reference-project evidence** — `decisions/0048`'s central hypothesis
  made concrete for the first time since Phase 43a's own-repo dogfood.
  Live-verified against the real Ledgerkit clone, independently, by both
  the lead and the auditor, from scratch each time: `dev-docs/` files
  (including a nested path) now resolve to an honest empty relations
  table instead of "not found"; a genuinely nonexistent name keeps the
  plain message; a still-uncovered real file
  (`knowledge/DOMAIN_RULES.md`) correctly triggers the new disambiguated
  message — confirming the fix generalises beyond the one directory it
  was evidenced against. One self-correction caught by the independent
  drift audit before commit: `_relations_not_found_error`'s docstring
  initially cited the wrong ADR (`decisions/0051`, unrelated) instead of
  `CG-002`/`L-016`/GATE DB. `docs-maintainer` reconciled
  `architecture/overview.md` (glob enumeration) and
  `docs/cli-reference.md` (`query relations` error-behavior
  description). `pytest` 557 passed / 2 skipped (+3), `ruff check .`
  clean, `check_user_docs.py --strict` clean. `docs-reconstructor` drift
  audit (`planning/retros/_drift-audit-phase-49.md`) → **NO DRIFT**;
  `release-phase-auditor` (`planning/retros/_audit-phase-49.md`) →
  **PASS WITH NON-BLOCKING OBSERVATIONS** (the only observations were the
  pending `roadmap-context-curator` reconciliation this closeout
  performs). `knowledge-curator` finalized: `CG-002` stays
  `promoted-to-roadmap` with a closing note confirming the fix landed;
  `L-016` flipped `retained` → `promoted`. Retro:
  `planning/retros/phase-49-spec-doc-coverage-and-error-disambiguation.md`.
  **Stage C now has its first completed phase; Phase 48/50 remain not
  funded.** No gate blocks Phase 51, but per this project's now-standard
  practice, Ledgerkit's current state should be re-confirmed live before
  committing to Phase 51's exact scope — its own roadmap has moved
  multiple times already (Phases 45/46).

### Phase 50 — Shared-agent context / entry-point improvements · CONDITIONAL
- **GATE DB outcome (2026-09-13): not funded.** `planning/reference-projects/ledgerkit/findings.md`
  §7: no supporting finding in the Phase 44–46 evidence base at all.
- If "specialist agents re-discover the same relationships" recurs:
  a common grounded project map the roster consumes, or a refinement to
  the Claude-entry-point hierarchy (`adoption-blueprint.md` §3). Hard
  constraint (`README.md` §1.9, R6): must not become opaque alternative
  project-memory — canonical knowledge stays in reviewable artifacts;
  this only indexes/connects them.

### Phase 51 — Re-run Ledgerkit evaluation · EXPERIMENTAL
- **Plan:** `planning/phase-51-rerun-ledgerkit-evaluation.md`
- Re-run Phase 46's task evaluation(s) (same tasks, same instrument)
  after Stage C changes.
- **Exit / GATE DC:** did measured context quality / advantage improve?
  If not, revert or defer the Stage C changes that didn't pay off.
  **If Stage D evidence later proves weak, the plan may legitimately
  terminate near here: a measured improvement over the foundation
  (phases 0–38) baseline, re-validated on a real external project, is a
  defensible redefined v1 — proceed to Stage F/G and ship it as `1.0.0`
  (`README.md` R14).**
- **Status: done (2026-09-14). GATE DC confirmed.** Re-ran Phase 45's
  baseline Q2 and Phase 46's genuine task — same questions, same
  instrument — against Ledgerkit re-pinned at `05218e3`. Both original
  FAILs **moved to PASS WITH GAPS**, and "would this have misled the
  agent" moved from yes to no for both, independently re-verified by
  `context-evaluator` via direct inspection and its own `codecompass`/
  `sqlite3` commands. **Confirmed the fix generalises**: the brand-new
  `17-query-semantics-brief.md` (didn't exist at Phase 46's pin) is also
  correctly tracked now. **Advantage stayed LOW**: `query relations` only
  does literal vendor/Skill name-mention detection, and Ledgerkit has 0
  tracked vendors, so it structurally cannot surface a doc's content —
  the ceiling on this question class wasn't raised, and the fix was never
  scoped to raise it. Phase 49's fix judged a success **on its own,
  narrow terms**; the earlier "smallest justified fix" judgment (rejecting
  a more general configurable-glob mechanism) is validated by this
  result, not called into question. No `src/codecompass/` change this
  phase (measurement only). As a closeout addendum, resolved a
  Phase-47-committed revisit decision the phase's own scope hadn't
  touched: `L-015` stays `retained` (genuinely out of scope across five
  intervening phases; revisit trigger updated to the next phase that
  actually exercises dependency discovery); `L-012` moved `retained` →
  `discarded` (7 phases old, three unclaimed corroboration opportunities,
  self-test-only by design — the lifecycle's "~3 phases, no new evidence"
  norm applied for real). `planning/reference-projects/ledgerkit/findings.md`'s
  triage table updated to match. Verified: `pytest` 557 passed / 2
  skipped, `ruff check .` clean, `check_user_docs.py --strict` clean.
  `docs-reconstructor` drift audit
  (`planning/retros/_drift-audit-phase-51.md`) → **NO DRIFT**;
  `release-phase-auditor` (`planning/retros/_audit-phase-51.md`) → **PASS
  WITH NON-BLOCKING OBSERVATIONS** (the one genuine gap it flagged — the
  dangling `L-012`/`L-015` commitment — is the addendum resolved above).
  Retro: `planning/retros/phase-51-rerun-ledgerkit-evaluation.md`.
  **This completes Stage C in full** (Phase 48/50 not funded, 49 done, 51
  done). **Whether to continue into Stage D (Phases 52–55) or treat this
  as sufficient and proceed toward Stage F/G is a genuine strategic
  decision surfaced to the user, not resolved by this phase** — see the
  retro's "Where we're going" section for both options laid out.

---

## STAGE D — Deeper Ledgerkit dogfooding  · EXPERIMENTAL

Goal: decide whether v1 scope must exceed package-source grounding,
using continued real Ledgerkit Core development (not a one-off baseline
task) as the evidence source.

**Amended 2026-09-14 — Phase 52's slot was retargeted.** At direct user
request during Phase 51's own retro window, Phase 52 implemented
`planning/context-edge-lifecycle-plan.md` (the context-observations
lifecycle + agent-driven enrichment, `decisions/0054`) instead of this
stage's pre-sketched "continue genuine Ledgerkit Core development" —
the same findings/decision-driven-scope precedent Phase 49 established
against its own pre-written Stage C sketch (see Phase 49's stanza
below). The original sketch text is left as written, unchanged, per
this project's "historical roadmap content is not rewritten" convention
— see Phase 52's own outcome note below it. **This retarget produces no
evidence toward Stage D's own goal or the Stage D-vs-Stage-F/G decision**
(Phase 51's retro) — that decision is still open, unaffected, and is not
resolved by this note. Whether Stage D's substantive goal (continued
live Ledgerkit dogfooding) still gets a phase slot, and under what
number, is part of that same open decision.

### Phase 52 — Continue genuine Ledgerkit Core development · EXPERIMENTAL
- Further real Ledgerkit tasks beyond Phase 46's single baseline task
  (its own roadmap's next milestones after Milestone 5, confirmed live
  at this phase — the repo will have moved). Apply the agent-led
  adoption blueprint (`adoption-blueprint.md`) if not already applied at
  Stage B. Continues feeding `planning/context-use-log.md`,
  `planning/context-gaps/`, and `validation/codecompass/findings/`.
- **Retargeted (2026-09-14), done.** Delivered
  `planning/phase-52-context-edge-lifecycle.md`'s scope instead of the
  sketch above (see the Stage D amendment note): the
  `context-observations/` lifecycle generalising
  `planning/context-use-log.md`; `decisions/0054`'s agent-driven
  enrichment (`relation_enrichment.py::apply_results`'s new `model`
  param, the new `codecompass enrich apply` CLI command, and the new
  ninth agent `context-enrichment-agent`); and a real, live, two-cycle
  demonstration against a local fixture
  (`tests/fixtures/ledgerkit_lifecycle_demo/`, `DEMO.md`) —
  **deliberately not the live Ledgerkit clone**, per explicit user
  direction, so this phase contributes no new Ledgerkit-dogfooding
  evidence. The live demo proved the `enrich apply` trust boundary
  (rejects a non-pending/stale edge), the enrichment cache surviving a
  mechanical graph rebuild byte-identically, and a genuine stale-edge
  rejection — plus one honestly disclosed, root-caused complication
  (`L-019`, a one-time fixture-bootstrap content-hash artifact).
  `pytest` 567 passed / 2 skipped, `ruff check .` clean,
  `check_user_docs.py --strict` clean. `docs-reconstructor` drift audit
  (`planning/retros/_drift-audit-phase-52.md`) → DRIFT, 2 non-blocking
  findings, both fixed before commit; `release-phase-auditor`
  (`planning/retros/_audit-phase-52.md`) → **PASS WITH NON-BLOCKING
  OBSERVATIONS**, including independently live-reproducing the two-cycle
  demonstration itself. Retro:
  `planning/retros/phase-52-context-edge-lifecycle.md`. **This phase is
  additive infrastructure, not a resolution of the open Stage
  D-vs-Stage-F/G decision** — see the Stage D amendment note above and
  Phase 51's retro.

### Phase 53 — Heterogeneous doc / reference / manual dependencies · EXPERIMENTAL

**Amended 2026-09-14 — this slot was also retargeted**, same
findings/decision-driven-scope precedent as Phase 52's retarget above and
Phase 49's against Stage C. At direct user request, Phase 53 instead
produced `planning/phase-53-legacy-feature-rationalisation-plan.md` — a
full feature inventory, redundancy map, and per-feature KEEP/REMOVE/
DEFER decisions across direct-API enrichment vs. Phase 52's agent-driven
path, chat, generated Skills, and dead code. The original sketch text
below is left as written, unchanged, per this project's "historical
roadmap content is not rewritten" convention. **This retarget produces
no evidence toward Stage D's own goal or the Stage D-vs-Stage-F/G
decision** (Phase 51's retro) — that decision remains open and
unaffected. Whether the heterogeneous-doc/reference sketch below still
gets a phase slot, and under what number, is part of that same open
decision — see Phase 52's identical note above.

**Retargeted (2026-09-14), done — review gate passed, implemented.**
`planning/phase-53-legacy-feature-rationalisation-plan.md` classifies
every runtime feature (CORE / AGENT / HOST-OUTPUT ADAPTER), maps three
real overlaps (Skill/`/discovery`/CLI-docs command-list duplication,
direct-API-vs-agent-driven relation enrichment by design, an
`adapters/`-naming collision), and reached one unambiguous action (remove
`discovery.py::rewrite_vendor_toml`, dead since `promote`'s Phase 15
retirement) plus five genuine product-direction recommendations
presented to the user at the review gate via `AskUserQuestion`. **All
three recommended options were approved**: direct-API vendor/symbol/
relation enrichment kept unchanged (real end-user-project value Phase
52's fixture demo doesn't touch); `chat.py` kept unchanged
(`decisions/0034`'s reasoning found no new evidence to unseat); the two
doc-only findings deferred to a documentation note rather than new
tooling. The never-built "initial-chat" concept was confirmed to have no
corresponding shipped code (Post-MVP Phase 20/24, `decisions/0048`) — no
action needed. **Implemented**: `rewrite_vendor_toml` + its test removed;
`architecture/overview.md` gained the "Module tiers: CORE, AGENT,
HOST-OUTPUT ADAPTERS" section, the adapter-terminology disambiguation,
and the command-list-duplication caveat. `pytest` 567 passed / 2 skipped,
`ruff check .` clean, `check_user_docs.py --strict` clean.
`docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-53.md`) → **NO DRIFT**.
`release-phase-auditor` (`planning/retros/_audit-phase-53.md`) → several
rounds, every gap found being governance-doc bookkeeping (stale
`CHANGELOG.md`/`ROADMAP.md`/`CONTEXT.md`/this very stanza still
describing the phase as unimplemented, one file at a time, after the
code had already landed), never a substance defect — see the audit
report and the phase's own retro's "Closeout audit trail" section for
the full, honest multi-round account and final verdict. Retro:
`planning/retros/phase-53-legacy-feature-rationalisation.md`, answering
all 9 of the governing prompt's specific retrospective questions.
Produces no evidence toward Stage D's own goal or the Stage D-vs-Stage-
F/G decision, exactly as disclosed above.

Original sketch (unchanged):

- Test whether CodeCompass can usefully index + relate *reference
  material* (hledger manuals, journal-format spec, command docs) to
  Ledgerkit's local implementation and compatibility tests — as evidence
  nodes with provenance, without a schema commitment. `ledgerkit-plan.md`
  §"Doc/reference test".

### Phase 54 — Heterogeneous reference-material experiment · EXPERIMENTAL

**Amended 2026-09-16 — this slot was also retargeted**, same
findings/decision-driven-scope precedent as Phases 52's and 53's
retargets above. The user's own prompt resolves the Stage D-vs-Stage-F/G
strategic decision (Phase 51's retro) in Stage D's favour, and its
requested scope — "test whether CodeCompass can make external technical
references... materially useful to agents working on real LedgerKit
tasks" — is word-for-word Phase 53's *own original sketch* below
("Heterogeneous doc / reference / manual dependencies"), not this
phase's own original "External executable / behavioural context" sketch.
Since Phase 53's slot is spent, and the two sketches' own original
ordering already put the doc/reference test immediately before the
behavioural/executable one, **Phase 54 is retargeted** to the
doc/reference work rather than inserting a fresh number — full reasoning
in `planning/phase-54-heterogeneous-reference-material-experiment.md`
§0. **This phase's own original sketch below is not discarded** — it
remains a valid future direction, just without a claimed phase number
now (alongside Phase 55's still-open, un-renumbered GATE DD).

**Retargeted (2026-09-16), done.** `planning/phase-54-heterogeneous-reference-material-experiment.md`
evaluated the user's proposed `references.toml → resolve → lock →
fetch/cache → extract → index → relate` ingestion pipeline against what
CodeCompass's existing graph/discovery mechanisms already cover, and
built/ran it for real: a tested pipeline
(`planning/reference-projects/ledgerkit/reference-experiment/`, kept
outside `src/codecompass/`), pinned live against the real, already-pinned
local hledger clone (`33fa849e...`, tag `1.52.4`), and a genuine two-run
comparison task (Ledgerkit's own Stage C `tag:` query-semantics brief,
explicitly deferred there) against a scratch copy of Ledgerkit, never the
real clone. **Independently evaluated by `context-evaluator`: baseline
PASS WITH GAPS, treatment FAIL, context-advantage LOW** — the FAIL
traces to a real, caught, and fixed extraction-boundary defect (a
hand-drawn line range silently excluded one of three documented rules),
not a mechanism defect; the pipeline's own hashes, idempotency, and its
YAML-evidence-matching relation fallback (demonstrated real against
Ledgerkit's own already-published `LK-COMPAT-QUERY-DATE-001.yaml`) all
independently confirmed sound. Detection generalises with zero schema
change; mechanical `mentions_artifact` structurally cannot relate two
`spec_doc` artifacts (`CG-004`); `origin`'s closed enum has no
externally-pinned-reference value (`CG-005`) — both filed as small,
independently-fundable candidates for Phase 55/GATE DD, not a mandate
for a broad new ontology. `L-020` (content-hash pinning proves an
excerpt hasn't changed, not that its boundary matches its own claimed
content) filed, `knowledge-curator` recommends promotion. No
`src/codecompass/` change. `release-phase-auditor` → **PASS** (first
round). Retro: `planning/retros/phase-54-heterogeneous-reference-material-experiment.md`.
**This phase resolves the Stage D-vs-Stage-F/G decision's own open
question by having actually run the Stage D test — the result is
genuinely mixed, not a clean mandate either way**, itself valid
evidence per the plan's own "treat negative or inconclusive results as
valid evidence" instruction.

Original sketch (unchanged):

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

### Phase 54b — LedgerKit reference/behaviour validation · EXPERIMENTAL

**Claimed 2026-09-17 (`decisions/0056`)** — this is the sketch
immediately above, finally given a phase number, as **sequence item 1**
of the revised validation strategy `decisions/0056` records ("LedgerKit
reference/behaviour validation → minimal Haskell adapter → hledger
cross-language experiment → adapter-interface consolidation →
lightweight ordinary-project smoke test → v1 consolidation"). Numbered
as a bridge phase (43d/43e, 55b precedent) between the Phase 54
reference-material experiment and Phase 55's own GATE DD, not a retarget
of either. Not started.

**Expanded 2026-09-18** (see full plan,
`planning/phase-54b-ledgerkit-behavioural-understanding-experiment.md`):
Ledgerkit's **Stage C Phase 5** (`c6168b2`, done 2026-09-17 — confirmed
live, Ledgerkit `HEAD` == `origin/main`) landed since this stanza was
first claimed and materially strengthens the evidence available —
a real, independently-verified investigation of hledger's `depth:`
query term showing **three distinct behaviours across five commands**
(clip for `balance`/`register`/`accounts`, full depth-blindness for
`print`, genuine exclusion for `stats`), and a real, dated instance of a
premature conclusion from locally-plausible-but-incomplete source
evidence (Stage C Phase 1 read one function's signature and wrongly
classified the behaviour as compatible, corrected only by a six-file
source trace at Phase 5). Phase 54b's objective is refined accordingly:
not "test relating an already-written provenance chain," but **test
whether CodeCompass's context helps an agent reconstruct
execution-path-complete behavioural understanding and avoid Phase 1's
own specific mistake**, using existing mechanisms only (Phase 54's
reference-ingestion pipeline, the context-gap/context-observation
queues, `context-evaluator`) — no new ontology, claim system, or
execution graph. Findings feed GATE DD's existing §2.2 (executable kind,
→ Phase 56) and §2.4 (provenance/evidence, → Phase 57) hypothesis rows,
not a new one, and carry forward as named requirements for Phase 60's
adapter design and Phase 61's cross-language comparison (see the plan's
§7-§9).

**Done (2026-09-18).** Two fresh, independently-dispatched agents (never
the lead, who had already read Ledgerkit's Stage C Phase 5 material)
ran the identical real task on the pinned hledger source
(`33fa849e...`, tag `1.52.4`): baseline with no CodeCompass; treatment
using 11 new manual/source excerpts (extending Phase 54's ingestion
pipeline) indexed into a scratch Ledgerkit copy (pinned at real `HEAD`
`c6168b2`). **Both reached the fully correct, complete answer**
(clip/aggregate for `balance`/`register`/`accounts`; genuine partial
exclusion for `stats`; total inertness for `print`) —
`context-evaluator` independently re-derived ground truth and rated
**baseline PASS, treatment PASS WITH GAPS, context advantage LOW**: the
curated set omitted `Stats.hs` entirely (the one file covering the
task's genuine exception), forcing a disclosed fallback exactly where it
mattered most, while the baseline never hit that gap working from full
raw source. Mechanical `query relations` again found **zero** edges for
all 19 indexed files, even with `CG-004`'s fix live (a second,
independent confirmation of `CG-006`/`OBS-008`'s structural ceiling).
**Execution-path-completeness: both runs rated `complete`** — neither
reproduced Stage C Phase 1's real premature-conclusion mistake, a
genuinely negative result for the specific failure mode this phase was
designed to catch, reported honestly rather than reframed as a win.
Filed `CG-007` (symbol-level cross-references between pinned reference
excerpts have no representable relation kind), `OBS-013`, `OBS-014`.
`L-022` (re-verify the actual rendering path, not just the authoring
interface, before dispatching hand-authored evaluation material to an
agent-under-test — caught during this phase's own construction, before
either agent ran) promoted into `reference-project-protocol.md` §2.4.
No `src/codecompass/` change. `release-phase-auditor` verdict and full
evidence: `planning/reference-projects/ledgerkit/findings.md`'s "Phase
54b" section; evaluation report:
`planning/reference-projects/ledgerkit/02-depth-behavioural-reconstruction-evaluation.md`;
retro: `planning/retros/phase-54b-ledgerkit-behavioural-understanding.md`.

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

### Phase 55b — Populate `doc_artifacts.name` for `spec_doc` rows (closes CG-004) · EXPERIMENTAL

**A bridge phase, not part of the Phase 55/Stage E sequence** —
numbered this way (43d/43e precedent) specifically so it doesn't
consume any of Stage E's own pre-written 56-59 sketch numbers below,
none of which matched its content, and doesn't require GATE DD (Phase
55) to resolve first. Full account:
`planning/phase-55-evidence-reconciliation.md` §G (the reviewed,
approved plan), `planning/phase-55b-spec-doc-name-population.md` (the
dedicated plan file), `planning/retros/phase-55b-spec-doc-name-population.md`
(the retro).

**Done (2026-09-17).** Closed `CG-004` — CodeCompass's existing
`mentions_artifact` relation-detection mechanism, unmodified, can now
relate two of a project's own docs to each other, since `spec_doc` rows
finally get a real `name` (their own H1 title, or filename stem, gated
by a genericity check). Doubly-corroborated going in (CodeCompass's own
Phase 54 experiment + Ledgerkit's independent, real-live-repo
`CC-LK-001` finding). A genuine mid-phase failure, caught by independent
evaluation and honestly retained in the record rather than smoothed
over: the first implementation attempt passed every unit test yet was
never actually wired into `sync.py`'s real production call, so the real
gap this phase existed to close still reproduced against the live
Ledgerkit repository — caught by `context-evaluator`'s round-1 pass,
fixed, and re-verified in round 2 (PASS WITH NON-BLOCKING OBSERVATIONS)
with a real before/after against the live repository: 3 genuine
`mentions_artifact` edges now appear, with a genericity guard
(`_is_specific_enough`) preventing the large-scale false-positive noise
a naive fix would have caused (quantified live at 55 hypothetical edges,
50 of them "every doc mentions README" purely because its own title is
the bare project name). Residual, honestly disclosed limitation: the
mechanism matches by title text only, not filename, so the original
`CC-LK-001` three files still show no relation to each other — filed as
`CG-006`, a small, independently-fundable follow-on of the same shape,
not urgent. A process-lesson candidate (`L-021`) proposes a `CLAUDE.md`
§1 amendment requiring a test through a function's real production call
site whenever a phase adds behaviour to it — drafted, not yet approved.
No `src/codecompass/` change beyond `spec_docs.py`/`doc_mapping.py`/
`sync.py`; no schema change; no new relation kind. Produces no evidence
toward the still-open GATE DD ontology question beyond what
`phase-55-evidence-reconciliation.md` already assembled — this phase
implemented the one item that didn't require resolving it first.

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
  Stage E before Stage F. **Cross-project/cross-language regression is
  deliberately a separate stage (F, next — a Haskell adapter spike as of
  `decisions/0056`, not Technical Clipper)** — do not fold it in here; a
  change that looks fine against Ledgerkit alone may still be
  accounting-specific or Python-package-shaped in a way a genuinely
  different ecosystem would expose.

---

## STAGE F — Cross-language adapter validation: Haskell spike  · EXPERIMENTAL

**Retargeted 2026-09-17 (`decisions/0056`) — Technical Clipper is no
longer this stage's target.** The general concept motivating this
retarget: a genuinely new-ecosystem adapter, built and validated against
a real, already-central codebase (hledger), is a stronger test of
`decisions/0002`'s own adapter-generality claim than a same-ecosystem
(npm) regression check — not "hledger executable support" or "Ledgerkit
compatibility YAML support" specifically; the concept generalises to any
future third-party ecosystem adapter (a hypothetical Rust, Go, or
COBOL adapter would face the identical interface-consolidation question
Phase 62 below asks). Full rationale: `decisions/0056`. Technical
Clipper is not dropped — see "Original Stage F content (preserved,
superseded as this stage's target)" below — it remains a registered,
valid reference project, explicitly available as Phase 63's smoke-test
candidate, just no longer roadmap-driving.

**Rust (Cargo) and JavaScript/npm adapter *maturation* work** (the
long-outstanding "no Rust toolchain available to validate Cargo against"
gap, `decisions/0014`; deeper real-world npm exercise) is correspondingly
demoted from near-term priority to later ecosystem-expansion work,
picked up only if a real project incidentally requires it — neither
drives this stage's or v1's architecture.

### Phase 60 — Minimal Haskell adapter · EXPERIMENTAL
- A real `EcosystemAdapter` implementation for Haskell/Stack, following
  `decisions/0002`'s own per-ecosystem-native-tooling precedent:
  `package.yaml`/`.cabal` for name/version/licence metadata (hpack
  format — already inspected against the real, pinned hledger clone
  during Phase 54: `hledger-lib/package.yaml` carries exactly this),
  `stack ls dependencies`/`stack query` for the dependency tree, exported
  top-level module signatures for a public-API-surface approximation
  (mirroring the Cargo adapter's own `pub`-scan precedent,
  `decisions/0015`). **No Haskell-specific logic anywhere outside the
  adapter boundary** — `codecompass.core`/`graph.py`/`sync.py` etc. stay
  exactly as ecosystem-agnostic as they are today; if this phase finds
  itself needing a core change, that is itself a finding for Phase 62,
  not something to build around silently. Real local toolchain already
  confirmed available (`stack`, used to build the pinned hledger clone
  itself) — unlike the Cargo adapter's own multi-phase-long
  toolchain-unavailability gap, this adapter can be tested against a
  real build from day one. New ADR if the interface needs any change to
  accommodate it (expected to be minimal or none, per `decisions/0002`'s
  own "each adapter implements the common interface using whatever
  native tooling its ecosystem already provides" design).
- **Amended 2026-09-18** (Phase 54b's plan, §8 — see
  `planning/phase-54b-ledgerkit-behavioural-understanding-experiment.md`):
  Phase 54b's findings on whether CodeCompass's document/reference-layer
  ingestion can surface *all* the real consumers of a concept like
  hledger's `Depth` (six source files across five commands, not just its
  defining module) become a **named evaluation question** for this
  adapter's own design — is exported-module-signature information alone
  sufficient for an agent to trace a behaviour from entry point through
  implementation, or is mechanical call-site/usage detection (the same
  shape as the existing Python/Cargo/npm import-usage detectors) also
  needed for Haskell? Answered with real evidence once the adapter
  exists, not decided speculatively here.

### Phase 61 — hledger cross-language experiment · EXPERIMENTAL
- Track hledger itself (or `hledger-lib` specifically, the most directly
  relevant package to Ledgerkit's own compatibility work) as a real
  CodeCompass-tracked vendor through the new Haskell adapter — real
  digests, real graph entries, generated the same way any npm/Python/
  Cargo vendor's are today. Independently evaluated the same way every
  Ledgerkit task has been (`context-quality-evaluation.md`'s instrument):
  does this materially help a real task (e.g. one of Ledgerkit's own
  Stage C query-semantics questions, or a `hledger-researcher`-style
  compat-register brief) compared with the existing manual
  fetch/grep-the-pinned-clone workflow Phase 54's own baseline already
  documented? Treat LOW advantage or a null result as valid evidence,
  same posture as every prior phase in this vein.
- **Refined 2026-09-18** (Phase 54b's plan, §9): the central test is not
  merely "does the adapter parse Haskell" (that is Phase 60's own DoD) —
  it is **whether CodeCompass helps an agent recognise that two
  differently-implemented things are the same behaviour.** Re-run Phase
  54b's own `depth:` behavioural-reconstruction question (or another
  Ledgerkit compatibility question with equally rich, independently-
  verified evidence, reconfirmed live at this phase's own start) using
  real Haskell-side structural information via the new adapter instead
  of Phase 54b's document-ingestion layer, and separately test whether
  CodeCompass can relate that reconstructed Haskell-side understanding to
  Ledgerkit's own Python implementation (`ledgerkit.query.depth.DepthSpec`,
  `clip_account_name`, etc.) as one behavioural concept realised in two
  languages. Phase 54b's own result is this phase's baseline for "how
  much better does real structural information do, compared to the
  document-ingestion layer alone."

### Phase 62 — Adapter-interface consolidation · EXPERIMENTAL
- Assess `EcosystemAdapter`'s own contract (`decisions/0002`) against
  what building and using the Haskell adapter actually required —
  the smallest justified interface change, if any (a new optional
  method, a relaxed assumption an existing method's docstring made that
  turned out npm/Python/Cargo-specific, etc.), not a speculative
  redesign. This is the concrete evidence input for whether the
  interface genuinely supports a plugin-style adapter boundary broad
  enough for independently-maintained future adapters (the aspirational
  framing `decisions/0056` names — Python/Haskell/proprietary-COBOL
  adapters coexisting behind one stable interface) — this phase produces
  the *evidence*, it does not itself commit to that broader packaging/
  licensing model.

### Phase 63 — Lightweight ordinary-project smoke test · EXPERIMENTAL
- A deliberately small confirmation — not a full reference-project
  protocol run — that ordinary npm/Python/Cargo project support wasn't
  disturbed by anything Phases 60-62 changed: bootstrap against one real
  ordinary project, confirm the existing three ecosystems still detect/
  digest/query correctly, no regression. Technical Clipper remains an
  available, already-registered, already-scouted candidate for this
  smoke test (`reference-project-protocol.md`'s existing material is
  still accurate) if convenient — using it here is explicitly optional,
  not required, and if used, the check stays lightweight (one bootstrap
  + one query, not the original Stage F's multi-task protocol).
- **Exit / GATE DF:** fix only *general* problems supported by evidence.
  If a genuine regression is found, it blocks Stage G until fixed or
  explicitly, narrowly scoped away with its own ADR — same bar the
  original GATE DF set, unchanged.

---

### Original Stage F content (preserved, superseded as this stage's target — `decisions/0056`)

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
work merely to create a test; use its existing, still-real backlog.

- **Phase 60 — Register Technical Clipper + baseline** — same shape as
  Phase 45, against `technical-clipper` at a pinned commit.
  `reference-project-protocol.md` §1/§2.1.
- **Phase 61 — Genuine Technical Clipper task(s)** — one or more real
  tasks from Technical Clipper's own roadmap/deferred work
  (`reference-project-protocol.md` §2.3's candidate pool), run against
  the post-Ledgerkit-evolved CodeCompass. Same procedure as Phase 46
  (`reference-project-protocol.md` §2.4).
- **Phase 62 — Consolidate: does it generalise?** — `knowledge-curator` +
  `context-evaluator` assess: package/vendor context still strong;
  relationship/evidence concepts introduced by Stage E generalise beyond
  accounting/hledger; no excessive noise from new abstractions; generated
  entry points remain useful; ordinary modern repositories still cheap to
  navigate.
- **Phase 63 — Decision** — Exit / GATE DF: fix only general problems
  supported by evidence — a Technical-Clipper-specific special case is
  not a valid Stage E/F output.

This content remains available as the basis for a future Technical
Clipper regression pass (Phase 63's own optional smoke-test candidate,
or later ecosystem-expansion work) — it is superseded as Stage F's
*required* content, not deleted.

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

### Phase 67 — Final validation: self-dogfood + Ledgerkit + the Stage F smoke test · EXPERIMENTAL (gates v1)
- **Updated 2026-09-17 (`decisions/0056`)**: references the revised
  Stage F below, not Technical Clipper specifically. A **lightweight
  confirmation pass**, not a full re-run (Stages D and F already did
  that work): re-verify CodeCompass's own dogfooding signal
  (`planning/context-health.md`, `planning/context-use-log.md`) is
  current; re-confirm Ledgerkit's final evaluation numbers
  (`planning/reference-projects/ledgerkit/`) and Phase 63's
  ordinary-project smoke test result still hold against the code as
  shipped. If Phase 63 used Technical Clipper as its smoke-test subject,
  re-confirm that specifically
  (`planning/reference-projects/technical-clipper/`); if it used a
  different ordinary project, re-confirm that one instead. Target: no
  FAIL verdicts on either; advantage MODERATE+ on the majority of tasks
  across both, or an explicit written justification for shipping below
  that bar.

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
4. Stage F run at least once — the Phase 63 ordinary-project smoke test
   at minimum (confirming no regression from whatever Stage C changes
   landed), even if Stages D/E or the fuller Phase 60-62 Haskell-adapter
   work are skipped (`decisions/0056`).
5. Stage G closeout + independent audit (Phases 64–70), scoped to what
   shipped; ship as `1.0.0` (first-ever publish).

That is a defensible v1: *"CodeCompass, built agent-led, measurably
improved on real external work, with honest published evidence of where
it does and doesn't add advantage, and confirmed not to have overfit to a
single ecosystem."* Deeper Ledgerkit dogfooding (Stage D) and
generalisation (Stage E) become v1.x if evidence doesn't clearly justify
them now. The plan should take this path rather than delay v1
indefinitely chasing the broader hypothesis.
