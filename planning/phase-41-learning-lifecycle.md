# Phase 41: Project-learning lifecycle + phase retros + per-phase docs-drift gate

**Status:** done (2026-09-10) — `release-phase-auditor` verdict: **PASS
WITH NON-BLOCKING OBSERVATIONS** (`planning/retros/_audit-phase-41.md`);
4 advisory observations, all addressed or filed for GATE DA.

Stage A. Makes `planning/learnings/` operational, adds the two per-phase
closeout mechanisms the user requested (a phase retro report + an
independent docs-drift audit), and dogfoods the agent-led loop for the
first time. Design: `planning/v1-redefinition/learning-lifecycle.md`,
`planning/v1-redefinition/documentation-lifecycle.md`,
`planning/v1-redefinition/agent-led-development.md`.

## Depends on

- Phase 40 done (agent roster + `CLAUDE.md` §8 exist).
- **CLAUDE.md §5 amendment approved** (user, 2026-09-10) — the two new
  DoD conditions (per-phase `docs-reconstructor` drift audit; phase
  retro report). Applied in this phase's commit.

## Scope

**In scope — learning lifecycle:**

- Finalise the `planning/learnings/` scaffold: confirm `README.md`,
  `inbox.md`, `TEMPLATE.md`, `promoted.md`; add `candidates/` with a
  `.gitkeep`.
- `knowledge-curator` brief finalised against the real files.
- `scripts/check_user_docs.py` — learnings-hygiene checks
  (`learning-lifecycle.md` §6): every candidate has all required fields;
  every `status: promoted` candidate has a `promoted.md` line; flag
  candidates stale in `evidence-gathering`. Report-only by default;
  `--strict` gates. New tests.
- `.claude/skills/docs-sync/SKILL.md` — mention the new checks.

**In scope — phase retros (user request, 2026-09-10):**

- New `planning/retros/` folder: `README.md` (what a retro is, how it
  feeds GATE DA) + `TEMPLATE.md` (Goal · Scope delivered vs planned +
  deviations · What was achieved · Lessons learnt · Process-improvement
  feedback · Candidate learnings filed · Time/cost note).
- Every phase from here on produces `planning/retros/phase-N-<slug>.md`,
  authored by the lead at phase end; a few lines suffice for a trivial
  phase. `knowledge-curator` mines it for candidate learnings.
- `scripts/check_user_docs.py` — a check: the highest `done` phase in
  ROADMAP's foundation + redefinition tables has a matching retro file
  (report-only unless `--strict`; skip phases before this one).

**In scope — per-phase docs-drift gate (user request, 2026-09-10):**

- `.claude/agents/docs-reconstructor.md` — add a **per-phase drift-audit
  mode** (read-only; scoped to what the phase changed + what references
  it; independent of `docs-maintainer`). Milestone blank-slate mode
  unchanged.
- `planning/v1-redefinition/documentation-lifecycle.md` — new §2.5
  documenting the per-phase independent drift audit.
- `planning/agent-led-workflow.md` — insert the drift-audit step
  (after `docs-maintainer`) and the retro step (before triage);
  renumber.
- `planning/v1-redefinition/agent-led-development.md` — update §2.7
  (dual mode), §2.8 (auditor also checks retro + drift-audit exist), §6
  (DoD table), §7 (step list).

**In scope — governance:**

- `CLAUDE.md` §5 — apply the approved diff (two new conditions). **This
  is the one protected-file change; already approved.**
- `CONTRIBUTING.md` — mirror.
- `decisions/0050` — ADR for the learning lifecycle **and** the
  phase-retro / per-phase-drift-audit tradeoff (process weight vs drift
  protection + systematic learning capture; alternative — milestone-only
  reconstruction + trusting self-cert — rejected).

**In scope — dogfood (first real use of the loop):**

- Run Phase 41's own closeout through the real agents:
  `docs-reconstructor` drift audit → `roadmap-context-curator` updates
  ROADMAP/CONTEXT/CHANGELOG → lead writes `planning/retros/phase-41-*.md`
  → `knowledge-curator` triages L-001 + any Phase 41 candidates →
  `release-phase-auditor` DoD audit.

**Explicitly deferred / out of scope:**

- CodeCompass indexing `planning/learnings/` or `planning/retros/` as
  graph artifacts — Stage C/E candidate.
- Any `src/codecompass/` change.
- Retro *consolidation* into process changes — that is GATE DA (Phase
  43) and later consolidation points, not here.

## Design decisions

- **`inbox.md` transient, `promoted.md` the only long-lived learnings
  file** (pointers only) — enforced by the hygiene check.
- **The curator recommends; the lead finalises** high-stakes promotions
  (tests, ADRs, `CLAUDE.md` proposals).
- **`docs-reconstructor` gets a second, lightweight mode** rather than a
  new agent — full blank-slate reconstruction every phase would swamp
  small phases and duplicate `docs-maintainer`; a *scoped, independent*
  drift check is the right weight and closes the real gap (nothing
  currently checks `docs-maintainer`'s self-cert).
- **The retro is the lead's artifact**, not an agent's — only the lead
  saw the whole phase. The curator consumes it.
- **Hygiene / retro-presence checks are report-only unless `--strict`** —
  same posture as every existing `check_user_docs.py` rule.

## Files

- `planning/retros/README.md`, `planning/retros/TEMPLATE.md` — new
- `planning/retros/phase-41-learning-lifecycle-and-retros.md` — new (this
  phase's own retro); `planning/retros/_drift-audit-phase-41.md`,
  `planning/retros/_audit-phase-41.md` — agent reports
- `planning/learnings/candidates/.gitkeep` — new; `planning/learnings/README.md`
  (status → operational), `inbox.md` (L-001/L-002/L-003),
  `promoted.md` (L-001 line)
- `.claude/agents/knowledge-curator.md` — brief finalised (also reads retros)
- `.claude/agents/docs-reconstructor.md` — per-phase drift-audit mode
- `.claude/agents/release-phase-auditor.md` — checks the two new DoD
  conditions (retro + drift audit)
- `.claude/skills/docs-sync/SKILL.md` — new checks noted
- `scripts/check_user_docs.py` — `Finding.strict` + learnings-hygiene +
  retro-presence checks
- `tests/test_check_user_docs.py` — new tests
- `CLAUDE.md` — §5 (approved 2026-09-10 diff)
- `CONTRIBUTING.md` — mirror
- `decisions/0050-phase-retros-and-per-phase-docs-drift-audit.md` — new
- `planning/agent-led-workflow.md` — 12 → 14 steps
- `planning/v1-redefinition/agent-led-development.md`,
  `documentation-lifecycle.md`, `proposed-governance-changes.md` — updated
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` — via
  `roadmap-context-curator`

## Verification

- `python scripts/check_user_docs.py --strict` passes on the repo after
  this phase (valid inbox, L-001 promoted with a `promoted.md` line,
  Phase 41 retro present).
- A deliberately malformed candidate → `--strict` fails clearly → remove
  → passes (test + one live demo).
- A missing retro for the highest `done` phase → `--strict` flags it
  (test).
- **End-to-end dogfood, actually executed (not described):** `knowledge-curator`
  triages L-001 to an outcome; `promoted.md` gets its pointer line;
  `docs-reconstructor` produces a drift-audit verdict for Phase 41's
  doc changes; `release-phase-auditor` returns PASS / PASS WITH
  NON-BLOCKING OBSERVATIONS.
- `pytest` / `ruff check .` clean.

## Done when

Standard DoD (as amended — incl. Phase 41's own retro + drift audit +
`release-phase-auditor` PASS) + verification above + the end-to-end
dogfood actually run.
