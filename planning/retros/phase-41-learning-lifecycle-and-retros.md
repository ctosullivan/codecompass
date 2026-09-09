# Phase 41 retro — Project-learning lifecycle + phase retros + per-phase docs-drift gate

- **Date:** 2026-09-10
- **Commit:** `a4525a3` (`feat(phase-41)`)
- **Agents used:** `knowledge-curator` (L-001 triage + L-002/L-003
  follow-up), `docs-reconstructor` (per-phase drift audit → NO DRIFT),
  `roadmap-context-curator` (ROADMAP/CONTEXT/CHANGELOG),
  `release-phase-auditor` (DoD audit → PASS WITH NON-BLOCKING
  OBSERVATIONS)
- **Reports:** `_drift-audit-phase-41.md`, `_audit-phase-41.md`

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

## Time / cost note

One session. 4 background/foreground agent dispatches (~27k + pending
subagent tokens). No AI spend on the CodeCompass product side (no
enrichment run). Longer than a "learning lifecycle only" phase would have
been — the scope growth roughly doubled it.
