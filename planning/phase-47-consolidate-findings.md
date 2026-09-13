# Phase 47: Consolidate recurring friction — GATE DB

**Status:** done (2026-09-13)

Stage B, fourth and final phase (EXPERIMENTAL → decision —
`planning/v1-redefinition/roadmap.md`). `knowledge-curator` reviews every
Phase 45–46 candidate learning and `context-gaps` entry (plus any
`validation/codecompass/findings/` report Ledgerkit's own `context-curator`
has filed by then — none exist as of Phase 46), promotes anything with
recurrence/evidence to a confirmed finding, and maps each to a roadmap
implication. Exits at **GATE DB** (gate G6): a decision on which Stage C
phases, if any, are funded.

## Depends on

- Phase 46 done: one genuine-task evaluation exists
  (`planning/reference-projects/ledgerkit/01-query-semantics.md`).

## Evidence inventory going into this phase (for the curator's bulk review)

**Context-gaps** (`planning/context-gaps/inbox.md`):
- `CG-001` — own-dev, `candidate` (one feature, three `src/` modules,
  no joining edge).
- `CG-002` — Ledgerkit `dev-docs/**/*.md` invisible to spec-doc detection,
  `recurred` (Phase 45 + re-confirmed independently by both agents in
  Phase 46, including nested-path extension).
- `CG-003` — external `hledger.org` manual has zero representation, no
  glob fix could ever cover it, `candidate` (Phase 46).

**Candidate learnings** (`planning/learnings/inbox.md`):
- `L-012` — single-symbol `query symbol` undersells usage breadth
  (own-dev self-test), `retained`.
- `L-013` — workflow step 10/14 split, `promoted` (already landed,
  Phase 44).
- `L-015` — no CLI signal for unscanned optional-dependencies, `retained`.
- `L-016` — "not found" conflates coverage gap with typo, `retained`,
  independently re-confirmed on live work in Phase 46.
- `L-017` — external-manual `WebFetch` is an expensive, unreliable
  fallback for section-specific content, `candidate`/`retained` pending
  this phase's triage.

**Reference-project evaluation reports:**
- `planning/reference-projects/ledgerkit/00-baseline.md` — 3 questions:
  PASS WITH GAPS (Q1), **FAIL** (Q2), PASS WITH GAPS (Q3).
- `planning/reference-projects/ledgerkit/01-query-semantics.md` — 1
  genuine task: **FAIL**, LOW (negative) advantage. Also documents a
  process gap (two agents racing a `Write` to the same file path,
  reconstructed by the lead) — a workflow finding for the retro, not a
  `CG`/`L` entry.

**`context-health.md`:** predicted LOW advantage for Phase 46 in advance
(Phase 45's assessment) — confirmed correct by Phase 46's actual result.

**`validation/codecompass/findings/`** (Ledgerkit's own side): none filed
as of Phase 46 — re-check live at this phase's start.

## Scope

**In scope:**

- `knowledge-curator` reviews the full inventory above in bulk (per
  `learning-lifecycle.md`), decides what's now evidenced strongly enough
  to promote to a **confirmed finding**, and for each confirmed finding
  maps it to a specific roadmap implication (a Stage C phase's scope, or
  "no action justified yet").
- Particular attention to the two recurring shapes across both `CG-002`
  occurrences and both FAIL verdicts (Q2, task 01): "not found" reads as
  authoritative non-existence for content that is real, current, and
  load-bearing — recurred twice now on real work, not a one-off.
- A written findings summary at
  `planning/reference-projects/ledgerkit/findings.md`.
- **GATE DB decision** (gate G6): which Stage C phases (48–51) are
  funded, and their scope — set by the findings, not pre-written. Valid
  outcomes explicitly include "fund no Stage C improvements, proceed to
  deeper Ledgerkit dogfooding (Stage D) instead" and "advantage is
  already established as needing fixes — fund a specific, narrow Stage C
  phase" (e.g. a `_DEFAULT_GLOBS` generalisation phase, informed by
  `CG-002`'s curator note that a `vendor.toml`-configurable spec-doc glob
  list may be the more general fix than one more hard-coded entry).
- Re-inspect Ledgerkit live at this phase's start (roadmap has moved
  twice already across two phases) and confirm nothing material changed
  since Phase 46's pinned commit that would affect the findings'
  currency.

**Explicitly deferred / out of scope:**

- Actually implementing any Stage C fix — that's Phase 48+, conditional
  on this phase's own decision.
- Any `src/codecompass/` change in this phase itself.
- Stage D (deeper Ledgerkit dogfooding, Phases 52–55) — only scoped if
  GATE DB's outcome points there.

## Design decisions

- **This is a decision phase, not an implementation phase.** The
  curator's job is synthesis and a funding recommendation; the actual
  Stage C scope (if any) is written by the lead as a fresh plan file
  only after GATE DB resolves, per `CLAUDE.md` §1's "pause and ask before
  proceeding from plan to code" if the decision itself needs the user's
  input (a genuine funding/scope call, not a technical judgment the
  curator can make alone).
- **Two real FAIL verdicts across two independent tasks is treated as
  real recurrence evidence**, not two datapoints requiring a third before
  acting — `context-quality-evaluation.md` §6 already flags every FAIL as
  highest-priority regardless of count.

## Files

- `planning/reference-projects/ledgerkit/findings.md` — new
- `planning/learnings/inbox.md`, `planning/context-gaps/inbox.md` —
  triage outcomes, promotions
- `planning/learnings/promoted.md` — any landed promotions
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` — curator
- A new `planning/phase-48-*.md` (or a decision note that no Stage C
  phase is funded) — written once GATE DB resolves

## Verification

- Every `CG`/`L` entry in the inventory above has an explicit,
  independently-reasoned disposition (not "reviewed, no change").
- `findings.md` states the GATE DB decision explicitly and traces it to
  specific evidence, not vibes.
- `pytest` / `ruff check .` clean (no `src/codecompass/` change expected).
- `python scripts/check_user_docs.py --strict` clean.

## Done when

Standard DoD + verification + GATE DB decision recorded and (if it
authorizes new work) the next phase's plan file exists + `release-phase-auditor`
PASS + learnings/context-gaps triaged.
