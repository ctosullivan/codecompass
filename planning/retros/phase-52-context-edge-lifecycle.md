# Phase 52 retro — Context edge lifecycle: observations queue + agent-driven enrichment

- **Date:** 2026-09-14
- **Commit(s):** `b488f1d` (`feat(phase-52)`)
- **Agents used:** `docs-maintainer` (reconcile), `docs-reconstructor`
  (drift audit), `context-enrichment-agent` (new, exercised live),
  `knowledge-curator` (triage), `release-phase-auditor` (final pass)

## Where we are

Stage C is done (Phase 51/GATE DC). This phase implements
`planning/context-edge-lifecycle-plan.md` — the planning package from
earlier the same day — with two real-time scope extensions the user
requested during implementation: agent-driven enrichment (since no
`ANTHROPIC_API_KEY` is available in this environment) and a local
fixture demonstration (not the live Ledgerkit clone). This is
CodeCompass's largest single-phase scope since Phase 43's original
agent-led-loop dogfood: a new ADR, a new agent, a new CLI command, a
planning-artifact reshape, and a real, live, two-cycle demonstration —
all in one phase, at explicit user direction rather than split across
several.

## Goal

Implement the context-observations lifecycle (generalising
`context-use-log.md`), add agent-driven enrichment as a second producer
alongside the automated API path, and demonstrate the whole loop working
against a local fixture across multiple cycles, with a durable audit
trail.

## Scope delivered vs planned

Delivered essentially as scoped in `planning/phase-52-context-edge-lifecycle.md`,
with one deliberate, disclosed narrowing: agent-driven enrichment was
built for `doc_relations_edges`/`doc_relation_enrichment` only
(`relation_enrichment.py`), not vendor/symbol-level enrichment
(`enrichment.py`) — the plan's own "explicitly deferred" section named
this up front as unnecessary complexity (vendor enrichment requires
cloned vendor source material and writes files to disk; doc-relation
enrichment is DB-only and fully sufficient to demonstrate Scenario A).

One real, unplanned complication surfaced and was handled transparently
rather than smoothed over: an intended "resubmit an unchanged edge,
prove rejection" test step instead produced a legitimate re-application,
traced live to a one-time content-hash artifact in the fixture's own
bootstrap order (a hand-written placeholder Skill file mechanically
overwritten mid-sync). Root-caused, documented (`L-019`,
`DEMO.md` step 9), and then genuinely re-verified with a clean
resubmission once the transient had settled — the rejection path *is*
proven, just one step later than originally expected.

## What was achieved

1. **`decisions/0054`** — agent-driven enrichment accepted as a second,
   non-authoritative producer, distinguished from the automated path by
   the pre-existing `model` column (`agent:<name>` vs. a real Anthropic
   model string) — zero schema change.
2. **`src/codecompass/relation_enrichment.py::apply_results`** gained an
   optional `model` parameter, backward-compatible, every existing call
   site unaffected (verified: 2 new tests, full suite still 567/2).
3. **`codecompass enrich apply`** — a new CLI command that mechanically
   enforces the trust boundary: it only accepts entries matching a
   currently-pending `select_candidates()` row, rejecting anything else
   with a clear reason. **Proven live, not just in unit tests**: a real
   run against a real local fixture correctly rejected a genuinely stale
   resubmission with exit code 1.
4. **`.claude/agents/context-enrichment-agent.md`** — a new, narrow role,
   deliberately kept separate from `knowledge-curator` per the user's own
   "consider appropriate separation of concerns" instruction: it produces
   interpretive content for edges that already exist; it never
   investigates observations, never touches a graph-fact table, and has
   no write path into `context-graph.db` other than the CLI command
   itself.
5. **`planning/context-observations/`** — generalises
   `context-use-log.md`'s four real entries (migrated verbatim, reshaped
   with an explicit edge-correctness/task-usefulness split the old format
   couldn't express) plus two new real entries from the live
   demonstration. `knowledge-curator`'s brief extended to triage it as a
   third queue, converging on the same investigation outcomes
   `context-gaps/` already uses.
6. **A real, live, two-cycle demonstration** (`tests/fixtures/ledgerkit_lifecycle_demo/`,
   `DEMO.md`): mechanical sync → real pending edge → agent-driven
   enrichment → visible via `query relations` with correct provenance →
   a second cycle proving the audit trail survives a graph rebuild
   byte-identical → a genuine, reproducible rejection of a stale
   resubmission.

## What worked

- **Grounding the fixture in Ledgerkit's own already-confirmed real
  content** (the `dev-docs/**` → codecompass-Skill mention pattern,
  independently observed real in Phases 45/46) rather than inventing a
  scenario — made the demonstration genuinely representative, not a toy.
- **Enforcing the trust boundary in the CLI itself, not by agent
  instruction** — this is what actually produced a *provable* guarantee:
  the live demo's rejection wasn't "the agent behaved well," it was "the
  command refused," independently checkable by anyone re-running it.
- **Investigating the unexpected acceptance immediately rather than
  papering over it** — root-causing it live (via direct hash
  recomputation and an `md5sum`-based idempotency check) turned a test
  hiccup into a genuine, documented, honest finding (`L-019`) rather than
  a silently-edited-away inconvenience.

## What didn't work

- The fixture's own bootstrap order (hand-writing a placeholder file that
  the tool under test then mechanically regenerates mid-run) created a
  real, if minor, source of confusion during the demo — worth naming as
  a methodology lesson (`L-019`) so a future fixture author starts from
  either a fully-hand-authored file the tool never touches, or lets the
  tool generate it from nothing, rather than the hybrid that caused this.

## Lessons learnt

1. **When a test/demo scenario touches a mechanism the tool itself
   mechanically regenerates, seed it from nothing or fully-hand-authored
   content — never a placeholder that overlaps with what the tool would
   generate anyway.** The overlap is what created the transient.
2. **An unexpected result during a live demonstration is itself
   evidence, not noise to route around** — the honest path (investigate,
   document, then re-verify cleanly) produced a stronger, more credible
   demonstration than a silently-retried "clean" run would have.
3. **A CLI-level trust-boundary check is only as convincing as a live,
   reproducible failure case, not just a passing unit test** — the unit
   tests (written first) proved the logic in isolation; the live demo's
   real rejection is what actually demonstrates the guarantee holds
   end-to-end.

## Process-improvement feedback

None new for the agent-led workflow itself. The scope-extension pattern
(user redirects mid-scoping, lead writes a fresh ADR + phase plan before
implementing, per `CLAUDE.md` §1's "pause and ask before proceeding from
plan to code" applied to the redirect itself) worked cleanly and is worth
naming as the right response to a mid-planning scope change, though not
yet worth a formal rule — one clean instance, not a recurring pattern.

## Candidate learnings filed

- **`L-019`** — a fixture bootstrapped from a hand-written placeholder
  the tool also mechanically regenerates causes a one-time content-hash
  "false churn." Filed `candidate`.

## Where we're going

- **Next: unclear, genuinely** — this phase's scope came from a direct
  user request rather than the pre-existing Stage D/E/F/G sequence. The
  Stage D-vs-Stage-F/G strategic decision from Phase 51's own retro is
  still open and unaffected by this phase's work (this phase's fixture
  demonstration deliberately did not touch the live Ledgerkit clone, so
  it produces no new evidence toward that specific decision). Whether
  Phase 53+ resumes that fork, or continues extending the context-edge
  lifecycle further (e.g. wiring `context-enrichment-agent` into real
  Ledgerkit dogfooding once Stage D is chosen), is the lead's/user's call
  at the next session.
- **Trajectory: this phase is additive, not a redirection of Stage
  D/E/F/G's own open question.** The lifecycle infrastructure built here
  is available to whichever path gets chosen next.

## Time / cost note

Single session, continuing directly from Phase 51 (same day). Real API
spend: **zero** — the entire agent-driven enrichment demonstration used
a Claude Code agent's own reasoning, not an Anthropic API call, precisely
because `ANTHROPIC_API_KEY` isn't available in this environment. This is
itself a small, honest data point for `decisions/0054`'s own motivating
case: a self-hosted tool's own development environment not having a
configured key is a real, non-hypothetical situation the new pathway
directly addresses. `pytest` 567 passed / 2 skipped (+10 from 557),
`ruff` clean, `check_user_docs.py --strict` clean.
