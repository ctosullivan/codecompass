# Phase 43c: Agent context-suggestion pathways + context-health planning

**Status:** planned

Stage A→B **bridge phase** (user request, 2026-09-11). Runs after Phase
43b, before Phase 44 (Stage B). Instruments the agent-led development
process so CodeCompass's *own* development produces context-quality
signal — the same signal Stage B will gather from Technical Clipper, but
starting now, from real work already in flight.

## Why this, why now

Stage B (Phases 44–47) validates the current CodeCompass against genuine
external work and asks: *is the context trustworthy, and materially
better than an agent's default pathway (grep / read / `--help`)?* Three
things would make that evaluation richer and earlier if introduced now:

1. **Agents notice missing relationships while they work** — e.g. during
   Phase 43 the lead reasoned about `skill.py` ↔ `graph.skills_index` ↔
   `cli.py query_skills` as one feature, a relationship CodeCompass's
   mechanical detection has no way to represent. Right now that
   observation evaporates. A **capture pathway** turns it into a
   reviewable candidate that feeds the GATE DB decision on whether
   agent-suggested edges are worth building
   (`planning/v1-redefinition/conditional-generalisation.md` §2.1/§2.6).

2. **Context-vs-default is measurable during real dev**, not only in
   dedicated reference-project evaluations. Every time the lead or an
   agent retrieves CodeCompass context, there is a counterfactual — what
   the default pathway would have surfaced — and a LOW/MODERATE/HIGH
   advantage. Capturing it per-use gives Stage B a volume of small
   datapoints from CodeCompass's own repo alongside Technical Clipper's.

3. **Context health is a forward-looking question** — for the phases
   coming up, which dependencies / relationships matter, and is their
   context fresh / grounded / complete? Nobody currently owns that view.

**Hard boundary (this phase does not cross it):** no `src/codecompass/`
change. No agent-inference edges in `context-graph.db`. No task-oriented
retrieval feature. Those are Stage C/E decisions, gated on GATE DB
evidence, each needing its own ADR
(`conditional-generalisation.md` §2.1, §2.4, §2.6). This phase builds the
*pathways and the evidence*, not the product feature.

## Scope

**In scope — 1. Agent context-suggestion capture pathway**

- New `planning/context-gaps/` — a log of relationships an agent believes
  should exist in CodeCompass's context but that mechanical detection
  does not / cannot produce.
  - `README.md` — what belongs here, what doesn't, how it feeds GATE DB.
  - `TEMPLATE.md` — per-suggestion record: stable id (`CG-NNN`); the
    edge (`A ↔ B`, kind: dependency↔dependency, dependency↔local-code,
    doc↔code, behaviour↔test, …); the agent's reasoning; the task /
    phase that surfaced it; **could mechanical detection ever catch this?**
    (yes-with-better-heuristics / no-conceptual-only / unsure); CodeCompass
    revision; status (`candidate` / `recurred` / `promoted-to-roadmap` /
    `discarded`).
  - `inbox.md` — the live queue.
- Any agent or the lead may append. The `knowledge-curator` reviews
  `context-gaps/` alongside `learnings/` at each phase's triage step and
  in the Phase 47 consolidation — a recurring suggestion, or one hit by
  two agents, becomes evidence for GATE DB.
- **These are observations, never authoritative.** They do not enter
  `context-graph.db`. (ADR `0051`, below.)

**In scope — 2. Context-vs-default-pathway evaluation (per use)**

- New `planning/context-use-log.md` — one short entry each time the lead
  or an agent retrieves CodeCompass context during real work:
  - what was asked / retrieved (a `query` result, a generated Skill, a
    `/discovery` read);
  - what the **default pathway** would have surfaced (the grep / file
    read / `--help` an agent without CodeCompass would have run) — stated
    concretely, not hand-waved;
  - **advantage: LOW / MODERATE / HIGH** (reusing
    `planning/v1-redefinition/context-quality-evaluation.md` §5's
    definitions) + one sentence;
  - whether the CodeCompass context contained anything **wrong or
    misleading** (the highest-priority signal).
- `planning/agent-led-workflow.md` **step 4** ("retrieve useful
  CodeCompass context") amended: if context was retrieved, add a
  `context-use-log.md` entry before moving on. Lightweight — 4 lines, not
  a `context-evaluator` report. If no CodeCompass context was used this
  phase, note that too (also a datapoint).
- `.claude/agents/reference-project-tester.md` brief: its friction log in
  Stage B feeds the *same* `context-use-log.md` format (one instrument,
  internal + external).

**In scope — 3. Context-health planning**

- New `planning/context-health.md` — a forward-looking assessment,
  refreshed at stage boundaries and before any phase that leans on
  CodeCompass context:
  - for the next ~3–5 roadmap phases, which tracked dependencies /
    relationships / generated artifacts matter;
  - their current state — freshness (installed vs recorded version),
    grounding (source cloned, enrichment present), completeness (usage
    detected, docs mapped), noise;
  - **gaps relative to where the project is going** (incl. anything from
    `context-gaps/` that a near-term phase would hit);
  - recommended actions (re-sync, enrich, or "no action — upcoming work
    doesn't lean on CodeCompass context").
- **Owner — decision for this phase (recommendation: a new
  `context-health-planner` agent).** It must read `context-graph.db` /
  run `codecompass query` (so it cannot be a `context-evaluator` mode —
  that agent is barred from using CodeCompass) and cross-reference
  `planning/ROADMAP.md`. Distinct concern from `roadmap-context-curator`
  (planning-doc truth) and `context-evaluator` (per-task quality by
  direct inspection). Alternative: a lead + `roadmap-context-curator`
  collaboration, no new agent — cheaper, keeps the roster at 7, but
  splits a single concern across two owners. **Recommend the new agent**;
  flag the tradeoff for the user.

**In scope — governance**

- `decisions/0051` — **agent-suggested context is captured as reviewable
  candidates, never written to the context graph.** The determinism-first
  boundary (`decisions/0031`, `0037`, `0045`) applied to a new input
  source: an agent's suggested edge is an observation with provenance,
  authoritative only if promoted via the learning lifecycle into a
  mechanical detection improvement (Stage C) or a graph feature (Stage E,
  with its own ADR). Non-obvious tradeoff → ADR.
- `planning/v1-redefinition/agent-led-development.md` — add
  `context-health-planner` to §2 / §3 (if the new agent is chosen);
  update §7 step list for the step-4 amendment.
- `decisions/0049` addendum note only if the roster changes (append a
  short "roster extended in Phase 43c" line to `0049`'s Consequences —
  *not* an edit to its Decision; per `CLAUDE.md` §2 append-only, a note
  is allowed).
- `planning/v1-redefinition/conditional-generalisation.md` §1.2 — mark
  that agent-suggested-edge evidence collection has *started* (Phase 43c),
  so the GATE DD/DB session knows where to look.

**Explicitly deferred / out of scope**

- **Any `src/codecompass/` change** — no `agent_suggested_edges` table,
  no `source='agent_inference'` provenance column, no AI edge detection,
  no task-oriented retrieval. Stage C (Phase 48/49) / Stage E (Phase
  56/57), gated on GATE DB / GATE DD, each with an ADR.
- Building a scoring / dashboard for context health — `context-health.md`
  is prose + a table, judgement not mechanised (same posture as
  `milestone-closeout-checklist.md`).
- Retro-fitting `context-use-log.md` entries for Phases 39–43 — start
  from now; one worked example from Phase 43 for the template is enough.
- `context-evaluator` changes — its Stage B per-task reports are
  unchanged; `context-use-log.md` is the lighter, higher-volume
  complement, not a replacement.

## Design decisions

- **Capture, don't build.** Every deliverable here is a `planning/`
  artifact + a workflow step. The point is to have evidence in hand when
  GATE DB asks "should CodeCompass do task-oriented retrieval / accept
  agent-suggested edges?" — not to pre-answer it.
- **One evaluation instrument, two sources.** `context-use-log.md` is
  used by the lead during CodeCompass's own dev *and* by
  `reference-project-tester` during Stage B. `context-quality-evaluation.md`'s
  LOW/MODERATE/HIGH scale is reused verbatim.
- **`context-gaps/` is a sibling of `learnings/`, not part of it.** A
  learning is "how we should work"; a context-gap is "what the graph is
  missing". Different destination (a detection heuristic / a graph
  feature vs. a test / ADR / rule). The `knowledge-curator` reviews both.
- **New agent for context-health, recommended but flagged.** The concern
  is real and distinct; the cost is an 8th agent 3 phases after GATE DA
  said "roster stays at 7" (that was about not *pruning* — it doesn't
  forbid adding with cause, but the user should weigh in).
- **This phase is a bridge, numbered 43c** (after 43b, before 44) to
  avoid renumbering Stage B–F. 43b and 43c are independent; either order,
  both before Phase 44.

## Files

- `planning/context-gaps/README.md`, `TEMPLATE.md`, `inbox.md` — new
- `planning/context-use-log.md` — new (+ one worked Phase 43 example)
- `planning/context-health.md` — new (first real assessment against the
  current roadmap)
- `.claude/agents/context-health-planner.md` — new (if the new agent is
  chosen)
- `planning/agent-led-workflow.md` — step 4 amendment (+ roster table if
  the agent is added)
- `.claude/agents/reference-project-tester.md`,
  `.claude/agents/knowledge-curator.md` — brief updates
- `decisions/0051-agent-suggested-context-is-captured-not-graphed.md` — new
- `decisions/0049-*.md` — append a one-line roster-extension note to
  Consequences (only if the agent is added)
- `planning/v1-redefinition/agent-led-development.md`,
  `conditional-generalisation.md` — updated
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md`,
  `planning/v1-redefinition/roadmap.md`, retro + agent reports — via the
  agent-led closeout

## Verification

- The 4 planning artifacts (`context-gaps/`, `context-use-log.md`,
  `context-health.md`, and — if chosen — the agent file) exist with real,
  usable templates.
- **One real datapoint captured for each, not just described:**
  - a `context-gaps/` entry for an actual missing relationship (e.g. the
    `skill.py`/`graph.py`/`cli.py` "one feature, three modules"
    relationship the lead reasoned about in Phase 43);
  - a `context-use-log.md` entry for the lead's *actual* live use of
    `codecompass query skills` during Phase 43 (vs. what `grep -rn "kind
    ="` would have shown) with an honest advantage rating;
  - a first `context-health.md` against the real current roadmap — which
    will likely conclude "CodeCompass's own 4-dependency graph is healthy
    but Stage B (Technical Clipper) doesn't lean on it" — an honest,
    useful finding.
- If the `context-health-planner` agent is chosen: it runs once for real
  and produces the `context-health.md` above.
- `python scripts/check_user_docs.py --strict` clean (new planning files
  linked; new ADR has a Status line).
- `pytest` / `ruff check .` unchanged and clean (no `src/` change).

## Done when

Standard DoD (as amended) — retro (incl. **what worked / what didn't**),
per-phase `docs-reconstructor` drift audit (expected NO DRIFT — no
product-doc change), `knowledge-curator` triage of any candidates + the
first `context-gaps/` entries, independent `release-phase-auditor` PASS.
Human-decision point surfaced in the retro / to the user: **the
`context-health-planner` agent — approve, or keep it a lead/curator
function?**
