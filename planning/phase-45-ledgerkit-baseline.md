# Phase 45: Register Ledgerkit + baseline evaluation

**Status:** done (2026-09-13) — see `planning/retros/phase-45-ledgerkit-baseline.md`

Stage B, second phase (EXPERIMENTAL —
`planning/v1-redefinition/roadmap.md`). Written now, per `CLAUDE.md` §1,
because Phase 44 made the reference-project protocol and its templates
concrete. First real datapoint on the redefined-v1 hypothesis
(`planning/v1-redefinition/README.md` §1.7).

## Depends on

- Phase 44 done: `planning/reference-projects/` (registry + both
  templates) exists; `context-evaluator` and `reference-project-tester`
  briefs finalised against them.

## Scope

**In scope:**

- **Register Ledgerkit**: clone
  `https://github.com/ctosullivan/ledgerkit` at a pinned commit into a
  **scratch location outside this repository** (the session scratchpad —
  never added to `vendor.toml` or `context-graph.db`,
  `reference-project-protocol.md` §2.2).
- **Reconfirm live** (the repo will have moved since the 2026-09-12
  desk/`gh` assessment in `planning/v1-redefinition/ledgerkit-plan.md`
  §1): current roadmap state, test layout, `dev-docs/` contents, current
  priorities. Update the registration record with what's actually true at
  the pinned commit, not the stale desk assessment.
- **Run CodeCompass against the clone as-is** (`codecompass init`/`sync`
  from the installed CLI) and record exactly what it discovers.
  Expected, per the existing inspection findings: a near-empty package
  graph (pure Python, stdlib-only; `pandas` an optional extra) — the real
  technical context (`hledger` executable behaviour, its manuals, journal
  syntax, the 1.52-compatibility contract) sits almost entirely outside
  what the current package-source model can represent. Record the actual
  result, not the prediction — if it's richer or poorer than expected,
  that's the finding.
- **Baseline context-quality report**: `context-evaluator` independently
  evaluates 2–3 representative "what does this project depend on / what
  governs this behaviour" questions against the pinned commit, using
  `TEMPLATE-evaluation.md`, per `context-quality-evaluation.md`.
- **`context-health-planner`'s first genuine solo run** (tracked forward
  from the Phase 43c retro/roadmap stanza): a forward-looking
  `planning/context-health.md` assessment against the freshly-registered
  Ledgerkit clone. Expected honest finding: "the graph is nearly empty;
  here is what CodeCompass cannot represent" — each un-representable
  dependency filed as a `planning/context-gaps/` entry
  (`decisions/0051`), not silently dropped.
- **Registration record**: `planning/reference-projects/ledgerkit.md`
  (from `TEMPLATE-registration.md`) + a `planning/reference-projects/README.md`
  registry-table row update (status: registered, link to the record).
- **§2.7 non-invasiveness check**, in writing: no change made to the
  Ledgerkit working copy beyond what a real task would require (none is
  required this phase — read-only registration + baseline), no
  CodeCompass repair made to force a result.

**Explicitly deferred / out of scope:**

- Attempting the genuine Milestone-5 task ("CLI Filter Flags") itself —
  that's Phase 46, which runs the full per-task procedure
  (`reference-project-protocol.md` §2.4) including
  `reference-project-tester`'s live friction log.
- Any `src/codecompass/` change — this phase only *measures* the current
  product; Stage C improvements are conditional on GATE DB (Phase 47).
- The deeper doc/executable/behavioural tests (Stage D, Phases 53–54).
- Registering or touching Technical Clipper (Stage F, Phase 60).

## Design decisions

- **Baseline is deliberately "as-is."** No tuning, no CodeCompass change
  in response to what registration/baseline surfaces — that would
  contaminate the very measurement Stage B exists to take. Findings feed
  GATE DB (Phase 47), not an immediate fix.
- **A near-empty or low-advantage result is an honest, expected outcome
  for this project shape, not a failure to hide** — `context-quality-evaluation.md`
  §5 says as much for small/package-graph-poor repos; the baseline report
  must say so plainly if that's what it finds, not round up.
- **The registration record's inspection findings supersede the desk
  assessment** wherever the live clone disagrees with
  `ledgerkit-plan.md`'s 2026-09-12 snapshot — that document already flags
  itself as due for reconfirmation.

## Files

- `planning/reference-projects/ledgerkit.md` — new (registration record)
- `planning/reference-projects/ledgerkit/00-baseline.md` — new (baseline
  context-quality report, from `TEMPLATE-evaluation.md`; more than one
  file if more than one question needs its own report)
- `planning/reference-projects/README.md` — registry row updated
- `planning/context-health.md` — updated (`context-health-planner`'s
  first solo run)
- `planning/context-gaps/inbox.md` (or new dated entries) — one per
  un-representable dependency found, if any
- `planning/learnings/inbox.md` — any candidate learning the baseline
  surfaces
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` — curator
- `planning/phase-46-ledgerkit-tasks.md` — written now that the baseline
  is concrete (per `CLAUDE.md` §1, before Phase 46 starts)

## Verification

- Working-copy discipline confirmed: the Ledgerkit clone lives outside
  this repository; `git status`/`git diff` here show no trace of it, and
  `vendor.toml`/`context-graph.db` don't reference it.
- `context-evaluator` confirms it reached ground truth by inspecting the
  Ledgerkit clone directly, not by running `codecompass query`/`check`.
- The registration record is complete against `TEMPLATE-registration.md`'s
  schema (repo URL, starting revision, CodeCompass revision, inspection
  findings, at least one evaluation row).
- `pytest` / `ruff check .` clean (no `src/codecompass/` change expected
  this phase — should be a no-op check).
- `python scripts/check_user_docs.py --strict` clean.

## Done when

Standard DoD + verification + the §2.7 non-invasiveness check written +
Phase 46's plan file exists + `release-phase-auditor` PASS + learnings
(and any `context-gaps` entries) triaged.
