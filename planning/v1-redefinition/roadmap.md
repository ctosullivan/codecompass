# Redefined-v1 roadmap — Stages A–F (phases 39–67)

Companion to [`README.md`](README.md). This is the roadmap-level detail;
`planning/ROADMAP.md` carries the at-a-glance status table (updated in the
same commit as this package, per `CLAUDE.md` §2, with the new milestone
group appended — historical tables untouched, no renumbering of phases
0–38 or 24–25).

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
| Phase 23 Part B (publish, paused) | **Superseded.** Gate G2 → G2-b: no release happens until Phase 67. Phase 23's row is marked "Part A done; Part B superseded — first publish is redefined v1 (Phase 67)". |
| Phase 24 (chat routing/rollup) | **DEFERRED.** Revisit as a Stage C candidate iff Stage B finds project-root context routing is a recurring need. Not renumbered. |
| Phase 25 (MCP server) | **DEFERRED.** Revisit post-redefined-v1, informed by real CLI/Skill usage. Not renumbered. |
| "v1.0 scope notes" in `ROADMAP.md` | Retitled "foundation-release scope notes" (wording only; no content deleted). |

---

## STAGE A — Redefine v1 & make CodeCompass agent-led  · COMMITTED

Goal: CodeCompass is developed by a lead session + a small specialist
agent team, with continuous doc/roadmap maintenance, systematic learning
capture, and an independent completion audit — proven on a real change.

Time tripwire: if Stage A exceeds ~6 working sessions, re-scope (the
roster is probably too big — prune per GATE DA).

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
- **Status:** planned.

---

## STAGE B — Validate existing CodeCompass against real work  · COMMITTED protocol, EXPERIMENTAL findings

Goal: honest evidence on whether the *current* CodeCompass supplies
trustworthy, materially-useful context during genuine Technical Clipper
development.

Time tripwire: aim for 4–8 evaluated tasks in Phase 46; if fewer than 3
genuine tasks are available on Technical Clipper's roadmap, that itself is
a finding — proceed to Ledgerkit earlier.

### Phase 44 — Reference-project protocol + context-quality eval spec · COMMITTED
- **Plan:** `planning/phase-44-reference-project-protocol.md`
- **Does:** finalise `planning/v1-redefinition/reference-project-protocol.md`
  and `context-quality-evaluation.md` into operational form: a
  `planning/reference-projects/` directory with a `README.md` (registry),
  a per-evaluation report template, and the registration record schema
  (repo URL, pinned commit, CodeCompass revision, task, context supplied,
  eval verdict, gaps). Brief the `context-evaluator` and
  `reference-project-tester` agents against it.
- **Exit:** template + registry committed; a dry-run evaluation of
  CodeCompass *against its own repo* using the template produces a
  coherent report (sanity check of the instrument, not a real datapoint).

### Phase 45 — Register Technical Clipper + baseline · EXPERIMENTAL
- **Plan:** `planning/phase-45-technical-clipper-baseline.md` (written when Phase 44 done)
- **Does:** clone `technical-clipper` at a pinned commit into a scratch
  location (never into this repo); run CodeCompass against it as-is;
  record exactly what it discovers (expected: ~7 devDependencies, 0
  runtime deps, near-empty enrichment) and what its context graph looks
  like. `context-evaluator` produces a **baseline context-quality report**
  for 2–3 representative "what does this project depend on" questions.
- **Exit:** `planning/reference-projects/technical-clipper.md` created with
  the registration record + baseline report. First real datapoint on the
  §1.2(2) hypothesis.

### Phase 46 — CodeCompass during genuine Technical Clipper tasks · EXPERIMENTAL
- **Plan:** `planning/phase-46-technical-clipper-tasks.md`
- **Does:** for each of N genuine tasks drawn from Technical Clipper's own
  roadmap / deferred work / real bugs (`reference-project-protocol.md`
  §"Task selection" — e.g. a detector-robustness fix, an adapter-coverage
  extension, a fenced-code-block edge case): the lead attempts the task
  *using CodeCompass context*; the `reference-project-tester` records
  friction (bypass, manual search, stale/incorrect/missing relationship,
  excess noise, un-representable dependency); the `context-evaluator`
  **independently inspects the Technical Clipper repo** (not via
  CodeCompass) and rates the supplied context per
  `context-quality-evaluation.md` (PASS / PASS WITH GAPS / FAIL +
  LOW/MODERATE/HIGH advantage).
- **Exit:** one evaluation report per task under
  `planning/reference-projects/technical-clipper/`.

### Phase 47 — Consolidate recurring friction · EXPERIMENTAL → decision
- **Plan:** `planning/phase-47-consolidate-findings.md`
- **Does:** `knowledge-curator` reviews all Phase 45–46 candidate
  learnings; promotes anything with recurrence/evidence to a **confirmed
  finding**; maps each confirmed finding to a roadmap implication.
- **Exit / GATE DB:** a written findings summary
  (`planning/reference-projects/technical-clipper/findings.md`) +
  a decision (gate G6) on which Stage C phases are funded and their
  scope. **Valid outcomes include "advantage is LOW across the board —
  fund no Stage C improvements; proceed to Stage D to test the broader
  hypothesis directly"** and **"advantage is already HIGH — minimal Stage
  C, go straight to hardening."**

---

## STAGE C — Improve the existing product  · CONDITIONAL on GATE DB

Each phase below exists **only if** GATE DB's findings support it. Scope
is set by the findings, not pre-written here. Sketches only:

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
  a specific confirmed finding.

### Phase 50 — Shared-agent context · CONDITIONAL
- If "specialist agents re-discover the same relationships" recurs:
  a common grounded project map the roster consumes. Hard constraint
  (`README.md` §1.9, R6): must not become opaque alternative
  project-memory — canonical knowledge stays in reviewable artifacts;
  this only indexes/connects them.

### Phase 51 — Re-run Technical Clipper evaluation · EXPERIMENTAL
- Re-run Phase 46's task evaluations (same tasks, same instrument) after
  Stage C changes.
- **Exit / GATE DC:** did measured context quality / advantage improve?
  If not, revert or defer the Stage C changes that didn't pay off.
  **If Stage D evidence later proves weak, the plan may legitimately
  terminate near here: a measured improvement over the foundation
  (phases 0–38) baseline, re-validated on a real external project, is a
  defensible redefined v1 — proceed to Stage F and ship it as `1.0.0`
  (`README.md` R14).**

---

## STAGE D — Test the broader product hypothesis  · EXPERIMENTAL

Goal: decide whether v1 scope must exceed package-source grounding, using
a project whose real dependencies are mostly not packages.

### Phase 52 — Register Ledgerkit + baseline · EXPERIMENTAL
- Same shape as Phase 45, against `ledgerkit` at a pinned commit.
  Expected baseline: CodeCompass finds ~0 meaningful package context;
  the real context (`hledger` exe, manuals, journal syntax, 1.52
  compatibility) is entirely outside its model. Record precisely.

### Phase 53 — Heterogeneous doc / reference / manual dependencies · EXPERIMENTAL
- Test whether CodeCompass can usefully index + relate *reference
  material* (hledger manuals, journal-format spec, command docs) to
  Ledgerkit's local implementation and compatibility tests — as evidence
  nodes with provenance, without a schema commitment. `ledgerkit-plan.md`
  §"Doc/reference test".

### Phase 54 — External executable / behavioural context · EXPERIMENTAL
- Ledgerkit-specific tooling (not CodeCompass) runs `hledger`, builds
  fixtures, does differential tests. CodeCompass's role under test:
  can it *consume and relate* that evidence ("behaviour X: documented by
  manual §Y, observed by experiment Z, implemented by ledgerkit/foo.py,
  verified by test_bar")? `ledgerkit-plan.md` §"Behavioural test".

### Phase 55 — Decide on broader abstractions · EXPERIMENTAL → decision
- **Exit / GATE DD (gate G7):** a written decision
  (`planning/reference-projects/ledgerkit/findings.md`) answering:
  is a generalised technical-dependency concept necessary for v1? is
  first-class provenance/evidence necessary? **What is the smallest model
  that covers the demonstrated need?** Approve the abstraction ADR(s) or
  record "not justified — package-source model + Stage C improvements is
  v1". `conditional-generalisation.md` structures this decision.

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

### Phase 59 — Re-validate · EXPERIMENTAL
- Re-run **both** Technical Clipper (Phase 46 tasks) and Ledgerkit
  (Phase 53–54 scenarios) against the generalised model.
- **Exit / GATE DE:** existing capability preserved (no regression in the
  Technical Clipper numbers), new capability proven (Ledgerkit context
  advantage moved up). FAIL → fix or narrow Stage E before Stage F.

---

## STAGE F — Define the real v1 release boundary  · COMMITTED once E completes

(If Stage D/E were skipped per GATE DD, Stage F runs against the Stage C
product instead — the checklist is identical.)

### Phase 60 — Blank-slate documentation reconstruction · COMMITTED
- `docs-reconstructor` agent, deliberate blank-slate posture
  (`documentation-lifecycle.md` §"Blank-slate reconstruction"). Produces a
  **shadow doc proposal** under `planning/v1-docs-reconstruction/`, not an
  overwrite.

### Phase 61 — Architecture + ADR reconciliation · COMMITTED
- Reconcile `architecture/overview.md` (currently 1,954 lines, accreted)
  against current reality; ADR status review (mark superseded ADRs,
  don't rewrite them). Decide retain/rewrite/consolidate/split/replace/
  remove per doc (`documentation-lifecycle.md` §"Reconciliation").
- **Concrete input:** `planning/v1-redefinition/architecture-split-candidates.md`
  (the `docs-maintainer`'s Phase 42 catalogue — 36 history-shaped
  passages).
- **Concrete obligation (from Phase 42 / L-004):** fix
  `architecture-split-candidates.md` **§C items 33–36** as *corrections*
  (not just trims) — `architecture/overview.md` currently describes the
  deleted `grounded_description.py`, its constants, and `Depth` /
  `depth = full` as live code, contradicting the same file's own
  "Grounded description — retired" / "Cost model" sections. Verify each
  against `src/` before rewording.

### Phase 62 — Roadmap + context reconciliation · COMMITTED
- `roadmap-context-curator`: `ROADMAP.md` + `CONTEXT.md` reflect the
  shipped v1; deferred work (Phases 24/25, anything dropped at gates)
  clearly parked with revisit triggers.

### Phase 63 — Technical Clipper final validation · EXPERIMENTAL (gates v1)
- Full Phase 46 evaluation suite, current code. Target: no FAIL verdicts;
  advantage MODERATE+ on the majority of tasks, or an explicit written
  justification for shipping below that bar.

### Phase 64 — Ledgerkit final validation · EXPERIMENTAL (gates v1, where in scope)
- Same, for whatever Ledgerkit scope Stage E delivered. Skipped cleanly
  (with a note) if GATE DD deferred all Ledgerkit-driven scope.

### Phase 65 — Independent release audit · COMMITTED (FAIL blocks)
- `release-phase-auditor`, read-only, full Definition-of-Done audit
  across every Stage A–F phase's exit criteria + the milestone-closeout
  checklist. Verdicts: `PASS` / `PASS WITH NON-BLOCKING OBSERVATIONS` /
  `FAIL`. **`FAIL` prevents Phase 66/67.** Auditor does not fix anything.

### Phase 66 — Milestone closeout · COMMITTED
- `planning/milestone-closeout-checklist.md` executed: deterministic doc
  checks; reconciliation applied (Phase 60–61 decisions actioned);
  obsolete current docs removed; links/examples validated; a **milestone
  closeout report** (`planning/v1-closeout.md` — architecture summary,
  what shipped, what deferred, key ADRs, evaluation results); current-doc
  freeze.

### Phase 67 — Release redefined CodeCompass v1 · COMMITTED (gate G9)
- Drop `.dev0`: `pyproject.toml` `1.0.0.dev0` → `1.0.0`; `twine upload`
  (**the first-ever publish** — G2-b held everything until here); `v1.0.0`
  tag; `[Unreleased]` → dated `1.0.0` section; public positioning change
  (gate G10). Irreversible-action posture identical to the old Phase 23
  Part B pause.

---

## Minimum viable redefined v1 (fallback path — mitigates R14)

If evidence is weak or time runs short, the smallest thing that still
legitimately counts as "redefined v1":

1. Stage A complete (agent-led, proven).
2. Stage B complete (Technical Clipper evaluated honestly; findings
   published even if the verdict is "LOW advantage on a small repo").
3. At least one **measured** improvement over the foundation
   (phases 0–38) baseline, re-validated on Technical Clipper (a trimmed
   Stage C + Phase 51).
4. Stage F closeout + independent audit (Phases 60–67), scoped to what
   shipped; ship as `1.0.0` (first-ever publish).

That is a defensible v1: *"CodeCompass, built agent-led, measurably
improved on real external work, with honest published evidence of where
it does and doesn't add advantage."* Stage D/E become v1.x. The plan
should take this path rather than delay v1 indefinitely chasing the
broader hypothesis.
