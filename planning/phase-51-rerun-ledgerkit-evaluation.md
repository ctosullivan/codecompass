# Phase 51: Re-run Ledgerkit evaluation — GATE DC

**Status:** done (2026-09-14)

Stage C's closing phase (EXPERIMENTAL — `planning/v1-redefinition/roadmap.md`).
Re-runs Phase 45's baseline Q2 and Phase 46's genuine task — same
questions, same instrument — against Ledgerkit's current state, now that
Phase 49's fix (`CG-002`/`L-016`) has landed, to measure whether context
quality actually improved. Exits at **GATE DC**: did it? If not, revert
or defer the Stage C change.

## Depends on

- Phase 49 done: the fix is live in `src/codecompass/`.

## Live re-check (done at this phase's own start, per established practice)

Ledgerkit has moved again since Phase 46's pinned commit (`9c33e37`):
latest is `05218e3` ("docs: confirm and pin the hledger reference
binary"). More significantly, **Stage C Phase 1 — the exact task Phase
46 evaluated — is now `[DONE]`**: `hledger-researcher`'s semantics brief
(`dev-docs/planning/core-redefinition/17-query-semantics-brief.md`) has
been written, and a standalone, tested `ledgerkit/query/` subpackage
(AST, parser, evaluator) now implements `acct:`/`desc:`/`date:`(simple)/
`depth:`/`status:`/`not:` — not yet wired into `reports.py`/`cli.py`.
This is a stronger, not weaker, position for re-evaluation: there is now
*more* real content in `dev-docs/` for the fixed glob coverage to
actually surface, not less.

## Scope

**In scope:**

- Pin Ledgerkit at `05218e3acced83dd8e980206668ca5ee83ebf103` for this
  phase's re-evaluation (same scratch clone, re-synced from scratch).
- **Re-run Phase 45's baseline Q2** ("what governs Ledgerkit's
  hledger-1.52 journal-format compatibility?") — same question,
  `dev-docs/hledger-compatibility.md`.
- **Re-run Phase 46's genuine task** ("hledger 1.52 query-term
  semantics") — same question, now additionally checking whether the
  new `17-query-semantics-brief.md` (which didn't exist at Phase 46's
  pinned commit) is also correctly surfaced, since it lives in the same
  previously-invisible `dev-docs/` tree.
- `context-evaluator` independently re-inspects the live clone at the
  new pinned commit and re-rates both questions per
  `context-quality-evaluation.md`, blind to what verdict would be
  "convenient" — a genuine re-evaluation, not a confirmation exercise.
- Direct comparison table: Phase 45/46's original verdict+advantage vs.
  this phase's — did the FAIL move to PASS/PASS WITH GAPS? Did the
  advantage rating move off LOW(negative)?
- **Exit / GATE DC**: did measured context quality improve? Record the
  answer plainly, including if it's "no" or "only partially."
- If the fix genuinely didn't help (e.g., new content exists but a
  different mechanical limitation still blocks it), that's valid GATE DC
  evidence to revert/defer/refine the Phase 49 change — not something to
  round up.
- Append a short dated entry to
  `planning/reference-projects/ledgerkit/findings.md` recording GATE DC's
  outcome (per Phase 49's own plan file, which deferred this append here).

**Explicitly deferred / out of scope:**

- Any further `src/codecompass/` change **unless** GATE DC finds the
  Phase 49 fix needs revision — that would be a new, separately-scoped
  fix, not silently folded into this phase.
- Wiring Ledgerkit's own `ledgerkit/query/` subpackage into
  `reports.py`/`cli.py` — that's Ledgerkit's own next Stage C step, not
  this evaluation's concern.
- Stage D (Phases 52–55) scoping — only happens after this phase's
  result is in, and only if warranted.
- Registering or touching Technical Clipper (Stage F).

## Design decisions

- **A genuine re-evaluation, not a victory lap.** `context-evaluator` is
  briefed the same way as always — inspect directly, don't assume the
  fix worked, rate honestly even if that means "still FAIL" or "improved
  but not enough."
- **Same questions, not new ones.** Re-running the identical Phase 45/46
  questions is what makes this a controlled before/after comparison
  rather than a fresh, incomparable datapoint.
- **The new `17-query-semantics-brief.md` is a bonus check, not the
  primary measurement** — it's genuinely new content (didn't exist at
  Phase 46's pinned commit), so its visibility is evidence the fix works
  going forward, distinct from confirming it retroactively fixed the
  original two failing cases.

## Files

- `planning/reference-projects/ledgerkit/00-baseline.md` — a dated
  re-evaluation section appended for Q2 (not overwriting the original)
- `planning/reference-projects/ledgerkit/01-query-semantics.md` — a
  dated re-evaluation section appended (not overwriting the original)
- `planning/reference-projects/ledgerkit/findings.md` — GATE DC outcome
  appended (per Phase 49's own deferral note)
- `planning/reference-projects/ledgerkit.md` — Evaluations table updated
  with the re-run rows
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` — curator
- A Stage D scoping note or `planning/phase-52-*.md`, only if GATE DC's
  result plus other evidence justifies continuing — not written
  speculatively

## Verification

- Both re-evaluations independently ground-truthed by `context-evaluator`
  via direct inspection of the Ledgerkit clone, not via `codecompass
  query`/`check`.
- The before/after comparison is explicit and honest — no rounding a
  "partially improved" result up to "fixed."
- `pytest` / `ruff check .` clean (no `src/codecompass/` change expected
  unless GATE DC finds a revision is needed).
- `python scripts/check_user_docs.py --strict` clean.

## Done when

Standard DoD + verification + GATE DC outcome recorded in `findings.md`
+ `release-phase-auditor` PASS + learnings/context-gaps triaged (if any
new ones surface).
