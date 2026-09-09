# Phase 41 retro — Project-learning lifecycle + phase retros + per-phase docs-drift gate

- **Date:** 2026-09-10
- **Commit:** `a4525a3` (`feat(phase-41)`)
- **Agents used:** `knowledge-curator` (L-001 triage + L-002/L-003
  follow-up), `docs-reconstructor` (per-phase drift audit → NO DRIFT),
  `roadmap-context-curator` (ROADMAP/CONTEXT/CHANGELOG),
  `release-phase-auditor` (DoD audit → PASS WITH NON-BLOCKING
  OBSERVATIONS)
- **Reports:** `_drift-audit-phase-41.md`, `_audit-phase-41.md`

## Where we are

- **Redefined-v1 Stage A** ("make CodeCompass agent-led"), phase 3 of 5
  (`planning/v1-redefinition/roadmap.md`). Foundation = phases 0–38
  (shipped, unpublished — gate G2-b holds all release until Phase 67).
- **Built directly on:** Phase 39 ratified the redefinition (ADRs
  0048/0049, `version → 1.0.0.dev0`); Phase 40 stood up the specialist
  agent roster + `agent-led-workflow.md` + `CLAUDE.md` §8, but its live
  smoke delegation was deferred. Phase 41 is where the roster was
  *actually used* for the first time — the learning lifecycle it
  operationalises is the pipeline Phase 40's `knowledge-curator` needed,
  and L-001 (raised in Phase 40) was the first candidate through it.
- **State after this phase:** the agent-led loop is proven end-to-end on
  a real phase (its own). `CLAUDE.md` §5 now has the full per-phase DoD:
  drift audit + retro + learning triage + independent auditor. Stage A
  has 2 phases left (42: documentation lifecycle; 43: dogfood a real code
  change → GATE DA).

## Goal

Make `planning/learnings/` operational (first real use of the learning
lifecycle), and add the two per-phase closeout mechanisms the user
requested on 2026-09-10: a lead-authored phase retro report and an
independent per-phase docs-drift audit. Both become `CLAUDE.md` §5 DoD
conditions.

## Scope delivered vs planned

Delivered as scoped in the (rewritten) plan file. Deviations:

- **Scope grew mid-phase.** Phase 41 was originally "project-learning
  lifecycle (operational)". The user's 2026-09-10 request folded in the
  retro artifact + the per-phase drift audit + a second `CLAUDE.md` §5
  amendment. The plan file was rewritten and the ROADMAP row renamed
  before implementation (per `CLAUDE.md` §1's allowance for scope changes
  to unstarted phases). Net: one phase now carries three related
  closeout mechanisms instead of one — defensible (they're all
  per-phase, learning-adjacent) but it's the second time Stage A has
  absorbed a feature request (Phase 40 absorbed the `check_user_docs.py`
  fix as L-001).
- **`decisions/0050` was written** (the plan said "only if a non-obvious
  tradeoff surfaces"). The retro/drift-audit tradeoff — per-phase process
  weight vs. drift protection, with "milestone-only reconstruction + trust
  self-cert" as the rejected alternative — is genuinely non-obvious, so
  the ADR is warranted.
- **Same-day template refinement (user request, 2026-09-10, after the
  `feat(phase-41)` commit):** the retro `TEMPLATE.md` gained **Where we
  are** and **Where we're going** sections so retros orient a future
  session in the arc, not just report a phase in isolation. This retro
  was updated to add them; `agent-led-workflow.md` step 11,
  `release-phase-auditor` / `agent-led-development.md` retro-content
  descriptions, and `retros/README.md` updated to match. `CLAUDE.md`
  §5's illustrative parenthetical was left as-is (already non-exhaustive
  — it omits "candidate learnings filed" / "time-cost" too;
  `TEMPLATE.md` is the authoritative section list). Landed as a
  `docs(phase-41)` follow-up commit.
- **One `docs-maintainer` step was skipped** — Phase 41 changed no
  current-truth product docs (`README.md`/`docs/`/`architecture/`/
  `ai-docs/`), only `planning/`, `.claude/`, `CLAUDE.md`, `CONTRIBUTING.md`,
  `decisions/`, `scripts/`, `tests/`. `docs-maintainer` had nothing to
  reconcile; the `docs-reconstructor` drift audit still ran (and is
  expected to return `NO DRIFT` with a scope note — the designed cheap
  path for a non-product phase).

## What was achieved

- `planning/learnings/` operational: `candidates/` subdir, `README.md`
  status corrected, `knowledge-curator` brief finalised, **L-001 triaged
  end-to-end** (confirmed promotion → `promoted.md` pointer line).
- `planning/retros/` created (README + TEMPLATE); every phase from 41 on
  produces a retro; enforced by `check_user_docs.py` for `done` phases
  ≥ 41 and by `release-phase-auditor`.
- `docs-reconstructor` dual mode: per-phase drift audit (every phase) +
  milestone blank-slate (Phase 60). The independent counterweight to
  `docs-maintainer`'s self-certification.
- `CLAUDE.md` §5 gained two conditions (approved diff); `CONTRIBUTING.md`
  mirrored; `decisions/0050`.
- `scripts/check_user_docs.py`: `Finding.strict` (info vs blocking), 4 new
  checks (learnings provenance, promoted-log consistency, stale-evidence
  [info], retro presence), + tests (26 pass, was 22).
- Workflow doc 12 → 14 steps; `agent-led-development.md` +
  `documentation-lifecycle.md` updated.

## Lessons learnt

1. **`knowledge-curator` has no Bash** (by design — `tools: Read, Grep,
   Glob, Edit, Write`). It could not run `check_user_docs.py` to confirm
   its own `promoted.md` edit resolved the finding; it traced the check
   logic instead and flagged it for the lead. For triage this is
   *mostly* fine, but "confirm the mechanical check now passes" is a
   natural part of the curator's job it currently can't do. → candidate
   learning **L-002**.
2. **The curator caught a drift item outside `docs-maintainer`'s scope.**
   It noticed `planning/learnings/README.md`'s "Status" section was stale
   ("Not yet operational — activated by Phase 41"). `docs-maintainer`
   only owns `docs/`/`architecture/`/`README.md`/`ai-docs/`/`CONTRIBUTING.md`
   — nothing owns `planning/**` doc accuracy except the lead and
   `roadmap-context-curator` (and only for ROADMAP/CONTEXT). The
   per-phase drift audit is scoped to *product* docs too. So stale prose
   in `planning/` (which is large and growing) has no independent check.
   → candidate learning **L-003**.
3. **Retro (step 11) ran after triage (step 12) this phase** — inverted —
   because L-001 was blocking the test suite and had to be resolved
   before the phase could be verified. The workflow assumes triage comes
   after the retro so the curator can mine it. When a candidate learning
   blocks verification, that ordering can't hold. Handled here by filing
   the retro-surfaced observations (L-002, L-003) as candidates for a
   short follow-up triage rather than a full second curator dispatch.
   → the workflow should acknowledge this inversion explicitly.
4. **Process weight is proportionate here but bears watching.** Phase 41
   dispatched 4 agents for closeout on a genuinely medium-sized phase —
   fine. The concern is a *medium* phase that isn't trivial enough for
   the fast path but where 4 dispatches feel heavy. No evidence of that
   yet; flag for GATE DA.

## Process-improvement feedback

- **Add a "blocking learning" note to `planning/agent-led-workflow.md`:**
  when a candidate learning blocks phase verification (e.g. a failing
  check), resolve it via an early `knowledge-curator` pass *before* the
  retro, then do a short follow-up triage of retro-surfaced candidates.
  Don't force the full 14-step order.
- **Consider giving `knowledge-curator` read-only Bash** (or a documented
  "the lead runs the confirming check" handoff). Currently implicit.
- **`planning/**` prose accuracy has no owner.** Options for GATE DA:
  extend the drift audit's scope to `planning/v1-redefinition/` +
  `planning/*.md` (not the phase plans / retros / ADR-like files, which
  are dated records), or make it explicitly the `roadmap-context-curator`'s
  remit, or accept it as lead responsibility and say so.
- The trivial-change fast path (added Phase 40, updated Phase 41) has not
  been exercised yet — Phase 43's dogfood target might be a good first
  test of it if a genuinely one-line change is picked.

## Candidate learnings filed

- **L-002** — `knowledge-curator` cannot run the mechanical check it
  reasons about (no Bash). Filed `retain` pending GATE DA.
- **L-003** — no independent check on `planning/**` narrative-doc
  accuracy. Filed `retain` pending GATE DA.

## Where we're going

- **Next: Phase 42** (documentation lifecycle) — no gate blocks it.
  Delivers the `docs-maintainer` brief in operational form,
  `check_user_docs.py` link / example-command / ADR-status checks, and
  `planning/milestone-closeout-checklist.md` (executed later at Phase 66).
  Phase 41 unblocked it by proving the `docs-maintainer` ↔
  `docs-reconstructor` split works and by giving `check_user_docs.py` the
  `Finding.strict` mechanism the new checks will reuse.
- **Then Phase 43** dogfoods the whole 14-step loop on one real,
  user-chosen CodeCompass code change, then **GATE DA**: did each role
  earn its keep? Phase 41 pre-loaded that decision with 4 concrete
  inputs — L-002, L-003, the triage/retro ordering inversion, and the
  "process weight on a medium phase" watch item.
- **Trajectory: confirmed, with two open scoping questions for GATE DA**
  (curator Bash; `planning/**` prose ownership) and a mild scope-creep
  signal (Stage A has absorbed two feature requests). Nothing that
  reshapes Stage B–F.

## Time / cost note

One session. 4 background/foreground agent dispatches (~27k + pending
subagent tokens). No AI spend on the CodeCompass product side (no
enrichment run). Longer than a "learning lifecycle only" phase would have
been — the scope growth roughly doubled it.
