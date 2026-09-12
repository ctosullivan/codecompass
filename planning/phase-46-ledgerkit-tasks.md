# Phase 46: CodeCompass during a genuine Ledgerkit task

**Status:** done (2026-09-13) — see `planning/retros/phase-46-ledgerkit-tasks.md`

Stage B, third phase (EXPERIMENTAL — `planning/v1-redefinition/roadmap.md`).
Runs the full per-task procedure (`reference-project-protocol.md` §2.4)
for the first time against Ledgerkit: the lead attempts a genuine Ledgerkit
task using CodeCompass context; `reference-project-tester` records live
friction; `context-evaluator` independently rates the supplied context.

## Depends on

- Phase 45 done: Ledgerkit registered, baseline evaluated
  (`planning/reference-projects/ledgerkit.md`), `CG-002` filed.
- **A genuine, already-scoped Ledgerkit task, confirmed live at this
  phase's own start** — not assumed from this plan file. Phase 45's
  registration record already demonstrated that Ledgerkit's roadmap can
  move between planning and implementation (Milestone 5 →
  `[SUPERSEDED]` the same day the desk assessment was written); this
  plan's candidate below is a starting hypothesis, not a commitment.

## Candidate task (reconfirm live before starting)

At Phase 45's registration time (pinned commit `a3cf2a7`), Ledgerkit's
Stage B ("Core model — journal/accounting model review,
Editor-compatibility confirmation") was `[PLANNED]` but **not yet scoped
or approved** (per the live clone's own `CONTEXT.md`: "Stage B isn't yet
scoped/approved"). Per `reference-project-protocol.md` §2.3, a task must
be genuine and already real — not invented to exercise CodeCompass — so
Stage B itself cannot be assumed as this phase's task until Ledgerkit's
own process has scoped it.

A concrete, already-named, already-scoped alternative exists and is the
**recommended candidate**: Stage A's own closeout explicitly named an
open, non-blocking follow-up (`CONTEXT.md`: "the finer-grained
`hledger-compatibility.md` rows (dates, amount formats, comments,
transaction fields, ...) into the compat-register — open follow-up, not
a blocker"). This is:

- **Genuine** — named by Ledgerkit's own Stage A closeout, not invented
  for this evaluation.
- **Well-scoped** — migrate specific narrative rows from
  `dev-docs/hledger-compatibility.md` into structured
  `dev-docs/compat-register/*.yaml` entries (25 already exist as
  `status: proposed`; pattern is established, not novel).
- **A strong test of `CG-002`'s real-world stakes**: the task's primary
  source material is exactly the file CodeCompass currently cannot see
  (`dev-docs/hledger-compatibility.md`) plus structured YAML CodeCompass
  has never modeled (`dev-docs/compat-register/`) — this is precisely
  the scenario `context-health.md`'s Phase 45 assessment predicted LOW
  advantage for, and precisely the scenario a fixed CG-002 (if promoted)
  would need to actually help with.

**At this phase's start:** re-inspect the live Ledgerkit repo. If Stage B
has since been scoped and approved (plausible — the peer development
session on Ledgerkit was active throughout Phase 45), prefer whichever
task is genuinely current and already scoped over this candidate. If
neither exists, the candidate above is not itself invented for
CodeCompass — it was independently named by Ledgerkit's own process — so
it remains a valid choice per §2.3's rule even if it isn't the literal
"next" item.

## Scope

**In scope:**

- Lead attempts the confirmed genuine task, using CodeCompass context
  wherever it would plausibly help (this task's primary source material
  is `dev-docs/`-resident, so — per Phase 45's finding — CodeCompass is
  expected to contribute little-to-nothing unless `CG-002` has been
  triaged/fixed by this point; that expectation itself is data, not a
  reason to skip trying).
- `reference-project-tester` records, live, every instance of: bypassing
  CodeCompass, a manual search done because context was missing, a
  stale/incorrect relationship, excessive noise, an un-representable
  dependency, context no better than direct inspection
  (`reference-project-protocol.md` §2.4 step 3). Adds
  `planning/context-use-log.md` entries per the existing instrument.
- `context-evaluator` **independently** inspects the Ledgerkit repo at
  the task's pinned commit (not via CodeCompass) and rates the supplied
  context per `context-quality-evaluation.md`.
- If Ledgerkit's own `context-curator` role / `validation/codecompass/`
  mechanism (confirmed live at Phase 45 — already adopted from
  `adoption-blueprint.md`) has by this point filed any finding of its
  own, cross-reference it per `codecompass-feedback-ingestion.md` rather
  than duplicating it.
- Report lands at `planning/reference-projects/ledgerkit/01-<task-slug>.md`.
- Any new un-representable dependency → `planning/context-gaps/` entry.
- §2.7 non-invasiveness check, in writing: confirm any change made to
  the Ledgerkit working copy is something its own maintainers would want
  on its own merits (i.e. the task's real deliverable), and that no
  CodeCompass repair was made by the tester to force an evaluation to
  pass.

**Explicitly deferred / out of scope:**

- Any `src/codecompass/` change — Stage C improvements are conditional
  on GATE DB (Phase 47), which this phase feeds but does not pre-empt.
- Fixing `CG-002` or any other filed gap — this phase *measures*, it
  does not react.
- Registering or touching Technical Clipper (Stage F).

## Design decisions

- **The task is confirmed live, not fixed by this plan file** — the same
  discipline Phase 45 itself required after Milestone 5 turned out to be
  superseded between planning and execution.
- **A LOW-advantage or FAIL result here is expected and valuable, not a
  failure of the phase** — Phase 45's baseline (including a genuine
  **FAIL** on the compatibility-governance question, `00-baseline.md`
  Q2) already predicts this. The point of Phase 46 is confirming whether
  that holds under a real task, not producing a better number.
- **CodeCompass never repairs itself mid-evaluation** — if `CG-002`'s
  absence blocks the task, that's recorded as friction, not silently
  worked around by the lead manually pre-reading `dev-docs/` and
  crediting CodeCompass for it.

## Files

- `planning/reference-projects/ledgerkit/01-<task-slug>.md` — new
  (context-quality evaluation report)
- `planning/context-use-log.md` — updated
- `planning/learnings/inbox.md` — any new candidate learnings
- `planning/context-gaps/inbox.md` — any new gap entries
- `planning/reference-projects/ledgerkit.md` — Evaluations table row `01`
  added
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` — curator
- `planning/phase-47-consolidate-findings.md` — written now that a real
  task's evidence exists (per `CLAUDE.md` §1, before Phase 47 starts)

## Verification

- The task is confirmed genuine (drawn from Ledgerkit's own roadmap/
  backlog/closeout notes, not invented) — stated explicitly in the report.
- `context-evaluator` confirms ground truth by direct inspection of the
  Ledgerkit clone, not via `codecompass query`/`check`.
- §2.7 non-invasiveness check written and satisfied.
- `pytest` / `ruff check .` clean (no `src/codecompass/` change expected).
- `python scripts/check_user_docs.py --strict` clean.

## Done when

Standard DoD + verification + Phase 47's plan file exists +
`release-phase-auditor` PASS + learnings (and any `context-gaps` entries)
triaged.
