# Phase 43d retro — GPL-3.0-or-later relicensing

- **Date:** 2026-09-12
- **Commit(s):** `<hash>` (`feat(phase-43d+43e)`, the combined closeout commit)
- **Auditor verdict:** **PASS** (`planning/retros/_audit-phase-43d-43e.md`)
  — no blocking gaps. Independently re-verified: `pytest` 554/1, `ruff`
  clean, `check_user_docs --strict` clean, `pip show codecompass` →
  `License: GPL-3.0-or-later`; **byte-for-byte diffed the `LICENSE`
  text's GPL body against `hledgerorg/hledger`'s own `LICENSE` file —
  zero diff** (the fetch was genuinely verbatim, not paraphrased);
  `CLAUDE.md` untouched; no git tag, no amended commit. One non-blocking
  observation: `CONTEXT.md` was caught mid-edit during the audit (the
  same self-contradiction shape L-006 previously flagged) — settled and
  correct by the time of this commit.
- **Agents used:** `docs-reconstructor` (drift audit, shared with 43e),
  `knowledge-curator` (triage, shared with 43e), `release-phase-auditor`
- **Reports:** `_drift-audit-phase-43d-43e.md`, `_audit-phase-43d-43e.md`

## Where we are

- **Redefined-v1, post-realignment.** The 2026-09-12 realignment
  (`realignment-2026-09.md`, committed `411cda6`) surfaced three gates —
  G11 (roadmap reorder), G12 (this phase — relicensing), G13 (Phase
  43e's adoption blueprint) — and stopped short of implementing any of
  them, per the task's own "planning only" instruction. The user then
  approved all three in one message ("Proceed as recommended").
- **Built directly on:** `licence-migration.md`'s plan (written the same
  session, before approval) — current-state audit (MIT, single
  copyright holder, no bundled third-party source, no other
  contributors, MIT-only runtime deps) and hledger's own confirmed
  `GPL-3.0-or-later` SPDX declaration.
- **State after this phase:** CodeCompass is GPL-3.0-or-later. Next:
  Stage B (Phase 44) begins, now free to inspect `hledger` source
  without an artificial clean-room posture, per the stated purpose of
  this relicensing.

## Goal

Execute the licence transition MIT → GPL-3.0-or-later planned in
`licence-migration.md`, now that gate G12 is approved: `LICENSE`,
`pyproject.toml`, `README.md`, `CONTRIBUTING.md`, and `decisions/0053`.

## Scope delivered vs planned

Delivered exactly as planned in `licence-migration.md` §3 — no
deviation. One addition not explicitly itemised in the original plan
text: `CONTRIBUTING.md` gained its own `## License` section (the plan's
§3 table already listed `CONTRIBUTING.md` as in scope; this is the
concrete content).

## What was achieved

- `LICENSE` now holds the canonical, **verbatim** GPL-3.0-or-later text
  (fetched directly from `hledgerorg/hledger`'s own `LICENSE` file via
  `gh api`, not retyped or paraphrased — per the FSF's own instruction
  that the licence text itself must not be modified), preceded by a
  short CodeCompass-specific notice block (name, copyright line, the
  "or (at your option) any later version" clause).
- `pyproject.toml`'s `license` field and classifier updated; **verified
  live**: `pip install -e .` + `pip show codecompass` reports
  `License: GPL-3.0-or-later`.
- `README.md`, `CONTRIBUTING.md` updated; both point at `decisions/0053`
  for the rationale rather than re-arguing it inline.
- `decisions/0052` and `decisions/0053` written as `Accepted` (moved
  from proposed drafts in `proposed-governance-changes.md` §C, which is
  now updated to point at the published ADRs — the same pattern
  `decisions/0048`/`0049` followed at Phase 39).
- `ruff check .` clean; `python scripts/check_user_docs.py --strict`
  clean throughout every edit in this phase.

## What worked

- **Fetching the licence text directly from hledger's own repository**
  rather than from memory or a generic template — this guarantees
  byte-fidelity with the exact document hledger itself ships, which
  matters for a relicensing whose entire stated purpose is alignment
  with hledger's licence family specifically.
- **Doing the legal-simplicity audit in the planning phase (43d's plan),
  not during execution.** By the time gate G12 resolved, there was
  nothing left to investigate — single copyright holder, no bundled
  code, MIT-only deps — so execution was a same-session mechanical
  step with zero surprises.
- **Writing `decisions/0052`/`0053` from the already-written draft text**
  in `proposed-governance-changes.md` §C (written during planning,
  before approval) — no re-derivation needed at execution time, same
  discipline the original Phase 39 used for `0048`/`0049`.

## What didn't work

- Small timing wrinkle, not a real misfire: the `release-phase-auditor`
  was dispatched while `CONTEXT.md`'s final edits were still landing, so
  it transiently observed a stale "gates open" wording mid-edit (the same
  shape as L-006's original finding) before the file settled into its
  final, consistent state. Resolved by commit time; not filed as a new
  learning — no repeat of the actual L-006 failure mode (the lead
  hand-patching planning docs incorrectly), just an auditor dispatched a
  beat too early relative to a still-in-progress edit.

## Lessons learnt

1. **A licence change is a good candidate for "plan fully, gate once,
   execute in one shot"** rather than iterative implementation — there
   is no partial-credit version of "the licence is GPL", and the legal
   analysis (§2 of `licence-migration.md`) doesn't change based on how
   the mechanical edits are sequenced.
2. **Fetching upstream's own canonical text (rather than a
   locally-remembered template) is worth the extra `gh api` call** when
   the whole point of the change is alignment with that specific
   upstream — verified byte-parity is stronger evidence than "this is
   probably the same GPL text everyone uses."

## Process-improvement feedback

No process notes this phase — straightforward execution of an
already-approved, already-fully-specified plan.

## Candidate learnings filed

- **L-009** (filed at triage) — fetching externally-authoritative text
  (here, the licence text) from its canonical upstream source rather
  than from memory/a template, for byte-fidelity. **Retained** —
  scoped-rule; no clean owning artifact yet (revisit on a second
  incident).

## Where we're going

- **Next: Phase 44** — Stage B begins (Ledgerkit baseline), now able to
  inspect `hledger` source without a clean-room restriction. No further
  licence work is scheduled unless a future ADR revisits it.
- **Trajectory: confirmed.** This phase doesn't reshape any later stage
  — it removes a friction point (the clean-room boundary) ahead of
  Stage B/D's deeper source-assisted work.

## Time / cost note

Small phase, same session as the plan itself and Phase 43e. No
`src/codecompass/` change → no `pytest` regression risk; `ruff`/
`check_user_docs.py --strict` clean. One `gh api` call to fetch the
canonical licence text. No CodeCompass product-side AI spend.
