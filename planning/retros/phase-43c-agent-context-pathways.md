# Phase 43c retro — Agent context-suggestion pathways + context-health planning

- **Date:** 2026-09-11
- **Commit(s):** `f7b80ee` (`docs(phase-43c): agent context-suggestion
  pathways + context-health planning`) — the plan + ROADMAP row + first
  CHANGELOG draft were committed separately at `f47f3e2`
  (`docs(phase-43c): plan …`)
- **Auditor verdict:** **PASS WITH NON-BLOCKING OBSERVATIONS**
  (`planning/retros/_audit-phase-43c.md`) — no blocking gap; all
  re-run verification matched (`pytest` 545/1, `ruff` clean, `--strict`
  clean, `CLAUDE.md` untouched, `CG-001` provenance exact-match). 4
  non-blocking observations: (1) `context-health.md` lead-written not
  agent-run — now a tracked before-Phase-45 commitment; (2) status flips
  to `done` in this commit; (3) retro hash placeholder; (4) the §2
  over-scoping the retro already notes.
- **Agents used:** `docs-reconstructor` (per-phase drift audit),
  `roadmap-context-curator` (step 10 + reconciliation), `knowledge-curator`
  (triage — CG-001 + L-007), `release-phase-auditor`
- **Reports:** `_drift-audit-phase-43c.md` (NO DRIFT), `_audit-phase-43c.md`
  (PASS WITH NON-BLOCKING OBSERVATIONS)

## Where we are

- **Redefined-v1, the Stage A→B seam.** Foundation = phases 0–38
  (shipped, unpublished — G2-b). Stage A (39–43, "make CodeCompass
  agent-led") is complete and GATE DA passed. Two user-requested bridge
  phases sit between Stage A and Stage B: **43b** (standing-doc-drift
  `check_user_docs.py` rules — still `planned`) and **43c** (this phase).
  They're independent; neither blocks the other; both land before
  Phase 44.
- **Built directly on:** GATE DA (Phase 43) established the agent-led loop
  as the working process and left `conditional-generalisation.md` §1.2 as
  the open question Stage B/D will answer on evidence — *does CodeCompass
  need a generalised dependency model, first-class provenance,
  task-oriented retrieval?* Phase 43 also produced the concrete
  motivating case (the lead reasoning about `skill.py` ↔
  `graph.skills_index` ↔ `cli.py` as one feature the graph can't join).
  43c turns that one-off into a standing capture pathway.
- **State after this phase:** the agent-led process now emits three kinds
  of context-quality signal from CodeCompass's *own* development —
  un-representable relationships (`planning/context-gaps/`), per-use
  advantage-vs-default (`planning/context-use-log.md`), and forward-looking
  graph adequacy (`planning/context-health.md`, owned by the new 8th
  agent `context-health-planner`). `decisions/0051` fixes the boundary:
  none of this is ever written to `context-graph.db`. Next: Phase 43b,
  then Stage B (Phase 44).

## Goal

Instrument the agent-led development process so CodeCompass's own
development produces the same context-quality evidence Stage B will
gather from Technical Clipper — starting now, from work already in
flight. Introduce a pathway for agents to *suggest* relationships the
graph is missing, a per-use context-vs-default-pathway evaluation, and a
forward-looking context-health assessment owned by a dedicated planner.
**Capture and evidence only — no `src/` change.**

## Scope delivered vs planned

Delivered as planned. Deviations:

- **The 8th-agent decision was resolved before implementation, not in the
  retro.** The plan flagged it as a human-decision point ("approve
  `context-health-planner`, or keep it a lead/curator function"); the
  user chose Option A (approve the agent) when approving the phase, so it
  was built as an agent from the start rather than provisionally.
- **`decisions/0049` touched.** The plan said "append a one-line
  roster-extension note to `0049`'s Consequences *only if* the roster
  changes" — it changed, so the note landed (append-only, Consequences
  section only, not the Decision).
- Nothing dropped or deferred beyond what the plan already listed as out
  of scope (any `src/` change, a scoring/dashboard, backfilling
  `context-use-log.md` for Phases 39–43).

## What was achieved

- **`planning/context-gaps/`** exists with a real first entry (`CG-001` —
  the `skill.py` ↔ `graph.skills_index` ↔ `cli.py::query_skills` trio),
  and it is a *worked* example, not just a template: the claim "the graph
  can't represent this" is backed by `codecompass query relations
  src/codecompass/skill.py` → `error: … not found in context-graph.db`.
- **`planning/context-use-log.md`** exists with a real first entry — the
  live Phase 43 `query skills` use, rated **LOW** advantage honestly
  (dogfooding the query layer on itself is a hard case for the tool), and
  `agent-led-workflow.md` step 4 now mandates an entry per phase.
- **`planning/context-health.md`** exists with a real first assessment:
  CodeCompass's own 4-dependency graph is healthy (versions fresh, 3/4
  enriched, `pipdeptree` correctly unused), *and* the useful
  forward-looking finding — no Stage A→B phase is gated on CodeCompass's
  own context; the graph that matters next is Technical Clipper's,
  expected near-empty.
- **`context-health-planner`** is the roster's 8th agent, with a tight
  boundary (read-only `codecompass query`, writes one file, files
  `context-gaps/` rather than editing the graph).
- **`decisions/0051`** extends the determinism-first boundary
  (`0031`/`0037`/`0045`) to a new input source without reopening it.

## What worked

- **Requiring one real datapoint per artifact, not just a template.**
  The plan's verification bar ("a `context-gaps/` entry for an actual
  missing relationship; a `context-use-log.md` entry for the actual
  Phase 43 use; a first real `context-health.md`") forced the pathways to
  be exercised immediately. `CG-001` surfaced a genuine, checkable gap;
  the `context-use-log` entry came out **LOW** and saying so is the
  point.
- **Resolving the 8th-agent decision up front.** Asking the user to pick
  Option A/B *before* implementation (rather than building it provisionally
  and retrofitting) meant one clean pass — the agent file, the roster
  table, `agent-led-development.md` §2.9/§3/§7, and the `0049` note all
  landed consistent.
- **Reusing `context-quality-evaluation.md` §5 verbatim** for the
  `context-use-log` advantage scale — one vocabulary across the light
  per-use log and the heavy `context-evaluator` report, so Stage B's
  aggregation can pool internal + external datapoints.
- **Writing `decisions/0051` before the artifacts.** Fixing the "never
  graphed" boundary first meant every downstream file (`context-gaps/`
  README, the curator brief, the planner brief) could just point at the
  ADR instead of re-arguing it.
- **`context-graph.db` spot-check for `CG-001`.** `codecompass query
  relations src/codecompass/skill.py` erroring "not found" is concrete
  proof the gap is real, not asserted — cheap and decisive.

## What didn't work

- **The plan file predicted `conditional-generalisation.md`
  §2.1/§2.4/§2.6 all needed touching; only §1.2 actually did.** The
  candidate designs in §2 didn't change — 43c gathers evidence *for*
  those designs, it doesn't alter them. Minor over-scoping in the plan's
  Files list.
- **`context-health.md`'s first assessment is partly a stub.** The plan
  says the `context-health-planner` agent "runs once for real and
  produces the `context-health.md` above" — but the agent was created
  *this* phase, and the lead wrote the first assessment by hand (running
  the same `codecompass query` commands). The agent's first genuine solo
  run is deferred to before Phase 45 (on the Technical Clipper clone),
  which is arguably the more honest first use anyway.
- No other misfires — the phase was small, self-contained, and
  `planning/`-only.

## Lessons learnt

1. **A capture pathway is only worth shipping with its first real
   entry.** An empty `TEMPLATE.md` + `README.md` proves nothing; the
   `CG-001` / `context-use-log` / `context-health` entries are what show
   the pathway can hold a real observation and route it somewhere. Build
   the instrument and use it in the same phase.
2. **"An agent will own X" and "X gets done this phase" are different
   commitments.** Creating `context-health-planner` doesn't mean its
   first real run happened — the lead stubbed the first assessment.
   Distinguish "the mechanism exists" from "the mechanism has produced
   output" in a plan's Done-when.
3. **Evidence-gathering phases should name the gate they feed, explicitly.**
   43c's whole value is realised at GATE DB (Phase 47) and GATE DD
   (Phase 55). Every artifact it created points forward at those gates
   (`context-gaps/README.md`'s hypothesis table, `0051`, the §1.2 note) —
   so the deciding session finds the evidence instead of starting cold.
4. **The determinism boundary keeps getting tested from new angles**
   (`0031` depth, `0037` spec-docs, `0045` labels, now `0051`
   agent-suggested edges). Each time the answer is the same shape:
   capture with provenance, promote only through a gate, never let AI
   write graph structure. That consistency is worth protecting — a new
   input source gets a new ADR, not a quiet extension.

## Process-improvement feedback

- **Step 4 of the workflow now does more** (retrieve context → log the
  use → maybe file a context-gap → maybe dispatch `context-health-planner`).
  That's a reasonable amount for one step, but if it grows further it
  should split. Watch it over the next few phases.
- The `context-health-planner` sits at step 4 ("before a context-leaning
  phase") but its natural cadence is *stage boundaries*, which don't map
  cleanly onto the 14-step per-phase loop. Phase 44 should confirm
  whether "dispatch it in the phase before a reference-project phase" is
  the right trigger or whether it wants its own entry in the stage-gate
  checklist.

## Candidate learnings filed

- **CG-001** (context-gap, not a learning) — filed to
  `planning/context-gaps/inbox.md`. Triaged (Phase 43c,
  `knowledge-curator`): provenance verified by code-trace, **outcome
  `candidate`** (first occurrence, single observer — needs a 2nd
  occurrence / independent observer to reach `recurred`), classification
  `unsure` split two ways (B↔C generated-artifact link →
  detection-improvement / GATE DB, overlaps Phase 43b's
  `check_generated_artifacts_match_source`; the "one feature, N modules"
  framing → graph-capability / GATE DD, `conditional-generalisation.md`
  §2.6). First datapoint for the §2.6 hypothesis-table row.
- **L-007** (filed at triage, from "what didn't work" lesson 2) —
  *"the mechanism exists" ≠ "the mechanism produced output this phase"*
  (`context-health-planner` was created but its first real solo run is
  Phase 45). **Outcome: `retained`** — `workflow` classification;
  candidate destination is one-line plan-template guidance, but it's
  CLAUDE.md-class and needs recurrence before a
  `proposed-governance-changes.md` entry. Revisit at Phase 47 / on
  recurrence.
- L-006 stays parked — its disposition confirmation is scheduled for
  **Phase 43b** triage (Phase 43 GATE DA note), not 43c. 43c's roster
  change was resolved *before* the `roadmap-context-curator` ran, so it
  did not re-trigger L-006's staleness pattern.

## Where we're going

- **Next: Phase 43b** (the standing-doc-drift `check_user_docs.py` rules
  from GATE DA — `check_no_deleted_names_as_live`,
  `check_generated_artifacts_match_source`). Independent of 43c; ~1
  session. Then **Phase 44** — Stage B begins.
- **Gate ahead:** GATE DB (Phase 47) and GATE DD (Phase 55) are what
  43c's three pathways feed. 43c does not affect *whether* those gates
  fire — it changes what evidence is on the table when they do. No
  §7 human-decision gate blocks 43b or 44.
- **Before Phase 45:** the `context-health-planner` agent runs for real
  on the Technical Clipper clone once it's registered (its first genuine
  solo use — see "what didn't work").
- **Trajectory: confirmed.** 43c is additive instrumentation; it doesn't
  reshape any stage. The redefinition's central question (is CodeCompass
  context trustworthy and materially better than the default pathway?) is
  still answered in Stage B — 43c just makes CodeCompass's own repo one
  more source of data for it.

## Time / cost note

Small phase, one session, `planning/` + `.claude/agents/` + one ADR only.
No `src/` change → `pytest` 545 passed / 1 skipped and `ruff` clean
unchanged from baseline; `check_user_docs.py --strict` clean. No
CodeCompass product-side AI spend. Does not move the Stage A time
tripwire meaningfully (43b + 43c together are the ~1–2 added sessions
already noted in `v1-redefinition/roadmap.md`).
