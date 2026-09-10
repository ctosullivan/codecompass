# Phase 43 retro — Dogfood the agent-led loop + GATE DA

- **Date:** 2026-09-10
- **Commit:** `feat(phase-43)` (hash in a follow-up)
- **Auditor verdict:** first pass **FAIL** on 3 planning-doc bookkeeping
  gaps (missing `43b` ROADMAP row; `v1-redefinition/roadmap.md` GATE DA
  outcome not recorded; `43b` absent from the CONTEXT forward path) — the
  code + closeout were fully green. All 3 fixed; **re-audit PASS**. The
  independent auditor caught its own gap, again (lesson 4).
- **Agents used:** `docs-maintainer` (first *editing* use → surfaced L-005),
  `docs-reconstructor` (per-phase drift audit → **NO DRIFT**, first run
  that verified real doc edits), `roadmap-context-curator`,
  `knowledge-curator` (L-005 triage), `release-phase-auditor`
- **Reports:** `_drift-audit-phase-43.md` (NO DRIFT), `_audit-phase-43.md`

## Where we are

- **Redefined-v1 Stage A** ("make CodeCompass agent-led"), phase 5 of 5 —
  the last. Foundation = phases 0–38 (shipped, unpublished — G2-b).
- **Built directly on:** Phases 39–42 stood up and specified the whole
  agent-led model (roster, workflow, learning lifecycle, documentation
  lifecycle, DoD amendments). Every prior Stage A phase changed only
  `planning/` / `.claude/` / tooling. Phase 43 is the first to change
  `src/codecompass/` — and the first to run the full loop against a real
  product change, which is the point: prove the model on real stakes
  before Stage B points it at external reference projects.
- **State after this phase:** Stage A is complete. The agent-led model
  has been exercised end to end 3 times (Phases 41, 42, 43) with
  progressively more real work each time. GATE DA (below) is passed with
  3 small amendments and no roster pruning. Stage B (reference-project
  validation) starts at Phase 44.

## Goal

Run **one real, small CodeCompass code change** through the entire
14-step agent-led workflow, then retro the roster (**GATE DA**). The
chosen change (user): widen `codecompass query skills` to surface
`cursor_mdc` + `slash_command` `doc_artifacts` rows — closing the
documented Phase 17 gap.

## Scope delivered vs planned

Delivered. Deviations:

- **The change grew slightly during scoping** — the documented gap was
  `slash_command` (`/discovery`) only, but `query skills`'s own docstring
  already promised `.mdc` coverage that the `WHERE kind = 'skill'` filter
  never delivered. So the fix widened to all three agent-context kinds
  (`skill`, `cursor_mdc`, `slash_command`), which is the *correct* small
  change (the command now matches its docstring), recorded in `43a`'s
  scope with the reasoning.
- **`docs-maintainer` edited a generated file** (`.claude/skills/codecompass/SKILL.md`,
  produced by `skill.py`). Caught by the lead before the drift audit;
  fixed in `skill.py` + regenerated. → **L-005**; `docs-maintainer`'s
  brief amended this phase with a "check if a file is generated before
  editing" rule.
- **No ADR** — this was a bug fix (command didn't match its docstring),
  not a non-obvious tradeoff.

## What was achieved

- `graph.skills_index` / `codecompass query skills` surface Skills +
  Cursor `.mdc` rules + `/discovery`, each tagged with its `kind` (new
  "Kind" table column, `--json` `kind` field). Verified live against this
  repo: 9 rows where it showed 5. +2 tests (545 suite green).
- `skill.py`'s generated tool-Skill text + `.claude/skills/codecompass/SKILL.md`
  (regenerated), `docs/cli-reference.md`, `architecture/overview.md`
  (`/discovery` section + `## Context graph` bullet) all reconciled.
- **The agent-led model is proven on a real `src/` change** — the loop
  produced correct code, correct docs, an independent NO-DRIFT
  verification of those docs, a real learning (L-005), and a passing
  independent DoD audit.

## Lessons learnt

1. **The loop earns its keep on a real change.** Phases 41–42 (governance
   phases) made the agents look like overhead — "NO DRIFT, nothing to
   reconcile" every step. Phase 43 (a real product change) is where each
   agent produced distinct, load-bearing value: `docs-maintainer`
   rewrote 3 docs, `docs-reconstructor` *independently verified* those
   rewrites against the code (not just "nothing changed"), the auditor
   re-ran the live demos. The model was designed for phases like this,
   not phases like 41–42.
2. **`docs-maintainer` doesn't distinguish generated from hand-authored
   docs** (L-005). It edited `.claude/skills/codecompass/SKILL.md`
   (generated from `skill.py`). It *did* correctly flag
   `.claude/commands/discovery.md` as generated — so it has partial
   awareness, just not applied consistently. The `.claude/skills/` path
   looks like a doc directory; the fact it's generated is only obvious
   from `skill.py`. Brief amended.
3. **`docs-maintainer` self-reported friction with "fix, don't caveat".**
   Its two flagged cases were genuine: (a) the `architecture/overview.md`
   paragraph it fixed *was itself* a standing caveat ("this gap exists,
   see CONTEXT.md") whose whole reason to exist evaporated — minimal-fix
   vs. delete-what-the-system-no-longer-justifies pulled opposite ways;
   (b) `docs/cli-reference.md`'s per-phase "added in Phase N" Status
   lines are the exact anti-pattern the brief warns against, but a
   pre-existing file-wide convention. It chose consistency + flagged the
   style. Both are good judgement; the brief could acknowledge that
   "fix, don't caveat" sometimes means "delete the paragraph".
4. **The independent auditor has caught a real gap every phase**
   (41: plan Files omission + missing verbatim-diff record; 42: 3
   observations; 43: TBD). Strongest single signal that the independent
   DoD audit is worth its cost.
5. **`knowledge-curator` still can't run a check** (L-002, now 3rd
   occurrence — every triage). It edits `planning/learnings/**` to
   resolve a `check_user_docs.py` finding, then can't confirm.

## Process-improvement feedback

Consolidated into GATE DA below.

## GATE DA — did each role earn its keep?

**Verdict: the model works. Roster stays at 7. 3 small amendments, no
pruning.**

| Agent | Stage A usage | Verdict |
|---|---|---|
| `roadmap-context-curator` | every phase | **Keep.** Authored `CHANGELOG`/`CONTEXT` with full-arc knowledge no single-phase view has; caught NO-GOs and small inconsistencies (`roadmap.md` step count, plan/ROADMAP status drift) the lead would have missed. |
| `docs-maintainer` | Phases 42–43 | **Keep.** Value is *both* assessment (the 36-item Phase 42 catalogue, zero edits) *and* editing (Phase 43, 3 docs). Surfaced L-005 about its own brief. |
| `docs-reconstructor` (drift audit) | every phase | **Keep.** Cheap "NO DRIFT" on governance phases (correct, ~1 pass); real independent verification of doc edits on Phase 43. The cheap runs are genuinely cheap. |
| `knowledge-curator` | every phase | **Keep, with amendment.** Triaged L-001…L-005 well; L-002 (no Bash) recurred every phase → amendment 1. |
| `release-phase-auditor` | every phase | **Keep.** Caught a real gap every single phase. |
| `context-evaluator` | not yet used | **Carry forward.** First use is Stage B (Phase 45). Cannot assess. |
| `reference-project-tester` | not yet used | **Carry forward.** First use is Stage B (Phase 46). Cannot assess. |

**Amendments (landed this phase — `planning/agent-led-workflow.md` +
briefs):**

1. **`knowledge-curator` → "lead runs the confirming check" handoff,
   formalised** (from L-002). *Not* giving it Bash — the risk the
   no-Bash design mitigates (the `v0.2` file-deletion incident) is real,
   and `tools:` can't scope Bash to read-only. Instead: the curator's
   output must end with an explicit "lead: run `X` to confirm" line
   whenever its edits should clear a mechanical check, and the workflow's
   triage step (12) says the lead runs it. This is what already happened
   3×; now it's the documented contract. L-002 → resolved.
2. **`docs-maintainer` brief: "check if a file is generated before
   editing"** (from L-005) — landed this phase.
3. **`docs-maintainer` brief: "fix, don't caveat" may mean *delete the
   paragraph*** when the paragraph's whole purpose was to explain a
   now-resolved gap (from lesson 3) — landed this phase.

**GATE DA decisions recorded but NOT implemented this phase** (small
`check_user_docs.py` additions — scheduled as **Phase 43b**, a quick
tooling phase before Phase 44, so Stage A's dogfood doesn't sprawl):

- A "deleted-names must not appear as live in current-truth docs" rule
  (hand-maintained list: `grounded_description`, `Depth`, `Depth.FULL`,
  `promote`, `depth = full`) — the standing-content complement to the
  diff-scoped drift audit (promotes **L-003 + L-004**).
- A "tracked generated artifacts match their generator output" rule
  (`.claude/skills/codecompass/SKILL.md` == `render_tool_skill(...)`;
  `.claude/commands/discovery.md` == `render_discovery_command()`) —
  catches the silent drift L-005 exposed.

**Stage-A time check:** ~5 working sessions (39–43), under the `roadmap.md`
"~6 sessions or re-scope" tripwire. Stage A absorbed 2 mid-stream feature
requests (Phase 41's retro/drift-audit; the Phase 41 "Where we are"
sections) — noted, not a problem at this size.

## Candidate learnings filed

- **L-005** — `docs-maintainer` edited a generated file. Triaged this
  phase: brief rule landed (project-rule part promoted); the
  generated-artifact drift check is a Phase 43b item.

## Where we're going

- **Next: Phase 43b** (a quick tooling phase, ~1 session) — implement the
  two `check_user_docs.py` rules GATE DA decided on (deleted-names,
  generated-artifact drift). Then **Phase 44** — Stage B begins: the
  reference-project protocol + context-quality evaluation spec into
  operational form, briefing `context-evaluator` and
  `reference-project-tester` (their first real use).
- **Stage B is the real test of the redefinition's thesis** — whether
  CodeCompass supplies trustworthy, materially-useful context on genuine
  external work (Technical Clipper), or whether a fresh Claude session
  gets equivalent context from a couple of searches. The two carried-
  forward agents get exercised there.
- **Trajectory: confirmed.** GATE DA passed cleanly; the agent-led model
  is the working development process for the rest of the redefined-v1
  effort. Nothing reshapes Stages B–F.
- **Phase 61 obligation still stands** (fix `architecture/overview.md` §C
  self-contradictions — L-004).

## Time / cost note

One long session. The full 14-step loop with 4 agent dispatches for a
~40-line `src/` change is heavier than the change, but that ratio is the
*point* of a dogfood phase and won't hold for typical phases (most won't
touch product docs, so `docs-maintainer` + a deep drift audit are cheap).
Full `pytest` 545 passed / 1 skipped. No CodeCompass product-side AI
spend.
