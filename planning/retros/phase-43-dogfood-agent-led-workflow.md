# Phase 43 retro — Dogfood the agent-led loop + GATE DA

- **Date:** 2026-09-10
- **Commit:** `d34a486` (`feat(phase-43)`)
- **Auditor verdict:** first pass **FAIL** on 3 planning-doc bookkeeping
  gaps (missing `43b` ROADMAP row; `v1-redefinition/roadmap.md` GATE DA
  outcome not recorded; `43b` absent from the CONTEXT forward path) — the
  code + closeout were fully green. All 3 fixed; **re-audit PASS**. The
  independent auditor caught real gaps the lead had missed, again
  (see "What worked" + lesson 2).
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
  4 small amendments and no roster pruning. **Phase 43b** (two
  `check_user_docs.py` rules GATE DA scheduled) runs next, then Stage B
  (reference-project validation) starts at Phase 44.

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

## What worked

- **The full loop on a real product change.** Every agent produced
  distinct, load-bearing output — unlike Phases 41–42 where "nothing to
  reconcile" made them look like overhead. This is the shape the model
  was built for.
- **Pausing during 43a scoping to read the docstring.** The documented
  gap was `slash_command`-only; checking `query skills`'s own docstring
  revealed it already promised `.mdc` coverage the filter never
  delivered — so the *correct* small fix was all 3 kinds. A 5-minute
  check found the right scope.
- **Regenerating `.claude/skills/codecompass/SKILL.md` from `skill.py`**
  rather than hand-editing → a clean single-line diff that byte-matches
  the generator (the auditor verified this explicitly).
- **Live-verifying against the real `context-graph.db`** (9 rows vs 5) —
  fast, concrete confidence the change did what it should, before any
  test.
- **The `docs-reconstructor` drift audit in "verify real edits" mode.**
  First phase it had actual doc edits to check against code (not just
  "nothing changed") — it independently confirmed all 3 `docs-maintainer`
  rewrites were accurate.
- **The `knowledge-curator` "lead runs the check" handoff** — it had
  worked informally 3× (curator traces the check by hand, ends with
  "lead: run X"); GATE DA just formalised what was already working.
- **The independent auditor.** Caught 3 real bookkeeping gaps + 1
  self-contradiction the lead had missed. Worth every one of its 3
  rounds.

## What didn't work

- **The lead hand-patching planning docs.** After the
  `roadmap-context-curator`'s step-10 pass, the retro scheduled Phase 43b
  and a 4th amendment; the lead then patched `ROADMAP.md` /
  `v1-redefinition/roadmap.md` / `CONTEXT.md` piecemeal and got it wrong
  3 times (missing 43b row, wrong "roadmap.md" file, self-contradictory
  CONTEXT). Every audit FAIL was self-inflicted bookkeeping. → **L-006**;
  the fix is to re-dispatch the curator after a plan-changing retro, not
  hand-patch.
- **`docs-maintainer` editing the generated `SKILL.md` directly** — a
  wasted round-trip (revert → fix `skill.py` → regenerate). Its brief
  didn't tell it to check whether a file is generated. → **L-005**,
  brief amended.
- **Writing the retro, then not re-checking whether it changed the
  plan.** The retro is step 11, *after* the curator (step 10) — so a
  retro that schedules a follow-up or amends the roster leaves step 10
  stale. Discovered only via the auditor's FAILs.
- **Minor:** the `43a` plan said "+3 tests"; actual delta is 2 new test
  functions + assertions added to 3 existing ones. Sloppy wording the
  auditor flagged.

## Lessons learnt

The generalizable takeaways (phase-specific detail is in "What worked /
didn't" above):

1. **The agent-led loop's cost/value ratio tracks how "real" the phase
   is.** Governance phases (41–42): agents look like overhead. Product
   phases (43): each earns its keep. Don't judge the model on governance
   phases.
2. **Independent verification consistently beats the lead's
   self-assessment** — the auditor caught a real gap on *all three*
   phases it ran (41, 42, 43), and Phase 43's 3-round FAIL trail was
   entirely bookkeeping the lead authored and thought was fine. The
   lesson isn't "the lead is careless" — it's "the person who did the
   work is structurally bad at auditing it, so don't skip the
   independent pass".
3. **A step that runs before an input it depends on is a latent bug.**
   The curator (step 10) runs before the retro (step 11); a retro that
   changes the plan makes step 10 stale (L-006). Same shape as L-003/
   L-004 (a diff-scoped check runs before standing content it should
   see). Watch for "X validates Y, but Y can still change after X".
4. **Agents apply their rules unevenly.** `docs-maintainer` correctly
   flagged one generated file (`discovery.md`) and edited another
   (`SKILL.md`) in the same task. A rule stated once isn't a rule
   applied consistently — spell out the check (L-005).
5. **"Fix, don't caveat" has a corner case:** when a paragraph's whole
   purpose was to explain a now-resolved gap, the fix is to *delete* it,
   not reword it. Amended into the `docs-maintainer` brief.

## Process-improvement feedback

Consolidated into GATE DA below.

## GATE DA — did each role earn its keep?

**Verdict: the model works. Roster stays at 7. 4 small amendments, no
pruning.** (The 4th — L-006 — was surfaced *by* GATE DA's own audit
rounds, which is fitting.)

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
   now-resolved gap (from lesson 5 / "what didn't work") — landed this
   phase.
4. **`agent-led-workflow.md` step 11 + `roadmap-context-curator` brief:
   re-dispatch the curator after a retro that changes the plan; the
   curator reconciles *every* planning doc incl.
   `v1-redefinition/roadmap.md`** (from L-006 — the 3 audit-round FAILs
   were all planning-doc bookkeeping the lead hand-patched after the
   curator's step-10 pass went stale) — landed this phase.

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
- **L-006** — the curator reconciles at step 10, *before* the retro
  (step 11), but a GATE/retro can schedule a follow-up phase or amend
  the roster → step 10's work is stale when it lands. Surfaced by the
  `release-phase-auditor`'s 3 FAIL rounds (all planning-doc bookkeeping
  the lead then hand-patched — badly). **Amendment landed this phase:**
  `agent-led-workflow.md` step 11 gains "re-dispatch
  `roadmap-context-curator` after the retro if it changed the plan";
  the curator brief gains "reconcile *every* planning doc incl.
  `v1-redefinition/roadmap.md`". Filed as a `candidate` — Phase 43b's
  triage confirms the disposition (it post-dates this phase's step 12).

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
