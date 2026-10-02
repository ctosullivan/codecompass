---
status: SKETCH FOR REVIEW. Not approved, not started, not part of
  `decisions/0070`'s own decision. Written per the Phase 78 corrective
  amendment's own explicit instruction (point 8: "plan one narrowly
  scoped follow-up... Do not repeat the full Phase 78 trial or invent an
  artificial benchmark") — the lead does not implement or dispatch
  anything against this sketch without further explicit approval.
---

# Phase 78 amendment follow-up (sketch) — a genuine existing-relationship-only Priority A trial

## Why this trial, and why not the Phase 78 one again

`decisions/0070` found Phase 78's own `ReportSpec`-parsing trial only
**partially** exercised `CG-001`'s real hypothesis: four of its five
derived producer/consumer chain links were proposed, not-yet-existing
design work (a new parser branch, a new `Journal` field, a new
`loader.py` extension, a new CLI command) that no relationship-indexing
capability could ever discover — only one link
(`ReportSpec`/`ReportSection` ↔ `balance_from_spec`) was a genuine,
already-existing relationship a capability could in principle expose.
This diluted the trial's own measurement: most of both agents' own
effort was inherent design work, not evidence about a tooling gap either
way.

**This follow-up's own task must have every relevant relationship
already exist today** — the task is to *extend or modify* already-wired,
already-cross-module-connected code, never to *design new* cross-module
structure. This is the one condition the Phase 78 trial's own task
selection did not satisfy.

## Candidate task — live-verified, not invented

**Ledgerkit's own backlogged "full `stats` query support" /
"`stats`: per-reporting-interval output"** (`ROADMAP.md`, Stage D
Reporting backlog). Verified live, 2026-10-02 (same session as this
sketch, against the real `/home/cormac/projects/ledgerkit` at its
current `HEAD`):

- `cli.py`'s `COMMANDS` tuple already includes `"stats"` and already
  dispatches it (`cli.py:451`) — the CLI consumer **already exists and
  is already wired**, unlike `ReportSpec`'s CLI consumer (which did not
  exist before Phase 78's own trial).
- `models.py:474`'s `Journal.stats(query: Query | None = None) ->
  JournalStats` **already exists** and is the model-layer entry point.
- `reports.py:496`'s `stats(...)` function and `reports.py:182`'s
  `JournalStats` dataclass **already exist** and are already consumed by
  `models.py::Journal.stats`.
- The backlog item itself ("full query support," "per-reporting-interval
  output") describes **extending an already-complete chain**, not
  building a new one — exactly the shape this follow-up needs.

A real agent given this task would need to trace an **already-existing**
`cli.py` → `models.py::Journal.stats` → `reports.py::stats`/
`JournalStats` chain to understand where the extension point is and what
it currently does — genuinely exercising `CG-001`'s own question
("could the agent determine, via CodeCompass alone, which functions
already reference/call which") on code that fully exists today, with
**zero conflation with new-code design effort** the way the `ReportSpec`
task had.

**Fallback, if live re-verification at dispatch time finds this task has
moved**: re-check Ledgerkit's own Stage D/backlog table directly (per the
reference-project protocol's own subordination rule, §2.3) for another
backlog item that extends, rather than originates, an existing
cross-module chain — do not substitute a task that reintroduces new-code
design dilution.

## Design (if approved) — reuses Phase 78's own corrected framework unchanged

1. **Same three-stage structure** (discovery/design comparison → an
   evaluation sufficient on its own to decide the question → an
   optional, evaluator-gated implementation check) — confirmed working
   cleanly at Phase 78 (`L-082`).
2. **Same read-scope-symmetry and observable-research-trace
   requirements** (Phase 78 plan §5.3.1, §5.3.4) — unchanged, already
   proven to produce genuine, independently-checkable corroboration.
3. **The corrected `CG-001` decision framework from `decisions/0070`
   applies from the start this time, not retrofitted after the fact**:
   the evaluator separates absolute materiality (`CG-001` outcome) from
   relative baseline comparison (context advantage) in its own original
   dispatch instructions, and the applicability question (does the task
   genuinely exercise only *existing* relationships, with no new-code
   design diluting the measurement) is checked and recorded explicitly
   *before* Stage 1 dispatch, not assessed only afterward.
4. **Exit-decision gate, inherited from `decisions/0070`**: an applicable
   `not-recurred` result on a task confirmed to test only existing
   relationships is what would actually justify Priority A's closure
   this time — the standard this follow-up is specifically designed to
   meet, which the `ReportSpec` trial did not.

## What this sketch does not decide

- Whether to actually run this trial at all (a human/lead decision,
  outside this sketch's own scope).
- The exact Stage 1 task-framing wording (would be drafted at
  approval time, mirroring Phase 78 plan §5.1's own level of detail).
- Anything about `CG-001`'s own eventual resolution — that remains
  genuinely open until a trial actually produces an applicable result,
  per `decisions/0070`.
