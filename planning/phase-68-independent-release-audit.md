# Phase 68: Independent release audit — plan

**Status:** planned (2026-09-24).

**Stage G, fifth phase · COMMITTED (FAIL blocks)** (`planning/v1-redefinition/roadmap.md`).
Gated on Phase 67 completing — **done 2026-09-24, PASS**, unblocked.
Not gated on GATE DD (a separate axis, per `decisions/0056`).

## 0. What this phase is, and isn't

Per the roadmap's own Phase 68 entry: `release-phase-auditor`,
**read-only**, runs a full Definition-of-Done audit across every Stage
A–G phase's own exit criteria, plus the milestone-closeout checklist
(`planning/milestone-closeout-checklist.md`, steps 1–7 — steps 8–11 are
Phase 69/70's own job, not this phase's). **`FAIL` prevents Phase
69/70** — the actual milestone closeout and release. The auditor does
not fix anything it finds wrong; findings return to the lead.

This is a **milestone-level** audit, not 68 individual per-phase
re-audits from scratch. Its real job: confirm the aggregate compliance
record is genuine (every phase that should have a retro/audit report
does, and a sample of them actually hold up under direct
re-verification), not merely that files with the right names exist.

## 1. A real, disclosed staleness to fix before dispatching

`planning/milestone-closeout-checklist.md`'s own text still says "for
the redefined-v1 effort that is **Phase 66**" (step 1's own header) and
names "Phase 66"/"Phase 67" for the documentation-closeout/release
split (step 11) — both predate the Phase 63D insertion and the Stage
F/G +4 renumbering (`decisions/0056`/`decisions/0060`). Current,
correct numbers: the documentation-closeout half is **Phase 69**; the
tag/release half (step 11, gate G9) is **Phase 70**. Fixed in this
phase's own Files section before dispatching the auditor, so it isn't
auditing against a stale document.

## 2. Scope

### 2.1 Per-phase DoD compliance, milestone-wide

For every phase from **Phase 41 onward** (`planning/agent-led-workflow.md`'s
retro requirement began there — Phases 0–40 correctly have none, per
Phase 66's own roadmap audit finding): confirm a retro exists at
`planning/retros/phase-N-*.md`. For phases with a standalone
`_audit-phase-N.md` file, confirm it exists and states a real verdict.
For phases without one (a handful of early ones embed the verdict
inline in the retro instead, per Phase 66's own prior audit finding) —
confirm the retro's own text actually states a real, independent
verdict, not merely "looks done."

**Not a re-run of every individual audit.** Spot-check a representative
sample (the auditor's own judgment on which — at minimum, one phase per
stage: A, B, C, D-skip/E-skip, F, and each of 63D/64/65/66/67 already
audited this session) by re-reading the retro + audit report and
confirming they're substantive, not stubs, and that their own stated
verdict wasn't later contradicted by anything (e.g. a later phase's
retro flagging an unresolved gap in an earlier one that was never
closed).

### 2.2 Milestone-closeout checklist, steps 1–7

- **Step 1** (deterministic checks pass): re-run
  `python scripts/check_user_docs.py --strict` — expect clean, as it
  has been throughout this session.
- **Step 2** (blank-slate reconstruction done): confirm Phase 64's own
  shadow proposal (`planning/v1-docs-reconstruction/`) satisfies this —
  it does, already closed.
- **Step 3** (reconciliation done): confirm Phase 65's own
  `reconciliation.md` + applied decisions satisfy this — already
  closed.
- **Step 4** (obsolete docs deleted, not annotated): spot-check that
  Phase 65's own removals (e.g. `architecture/overview.md`'s "Grounded
  description — retired" section) were genuinely deleted, not left as
  an "outdated" wrapper note.
- **Step 5** (link/example validation): re-run
  `check_user_docs.py --strict`; spot-check `docs/quickstart.md`'s own
  steps against the real running system (Phase 65 already adopted and
  verified this file — confirm it still holds).
- **Step 6** (architecture docs, current-state only): read
  `architecture/overview.md` and the five Phase-65-adopted files
  end-to-end; confirm no "Phase N added... later changed..." narration
  remains.
- **Step 7** (ADR status review): confirm `check_adr_status_and_supersedes`
  passes; confirm `decisions/0061` (added Phase 65, closing the
  `0019`/`0035` gap) is itself sound; spot-check no *new* silent
  reversal has crept in since Phase 65's own full 59-ADR review
  (Phases 66/67 added no new ADRs, so this should be a quick
  confirmation, not a re-review).

**Steps 8–11 are explicitly out of scope** — the freeze declaration,
bulk retro review, closeout artifact, and the actual tag/release are
Phase 69/70's own jobs.

### 2.3 Verdict

`PASS` / `PASS WITH NON-BLOCKING OBSERVATIONS` / `FAIL`, per the
roadmap's own stated scale. A `FAIL` blocks Phase 69/70 until fixed and
re-audited — matching every prior FAIL→fix→re-audit cycle this session
(Phase 64's own first pass, for instance).

## 3. Files created/changed

- **`planning/milestone-closeout-checklist.md`** — the two stale phase
  numbers fixed (§1 above).
- Standard closeout: `planning/retros/_audit-phase-68.md` (this *is*
  the phase's own primary deliverable — the milestone-level DoD audit
  report), `planning/retros/phase-68-independent-release-audit.md`
  (the phase's own retro, distinct from the audit report), any
  `planning/retros/_drift-audit-phase-68.md` (expected `NO DRIFT` —
  this phase, being read-only itself, touches no current-truth doc
  beyond the one stale-number fix), `planning/learnings/inbox.md` (any
  candidates), `planning/CONTEXT.md`, `CHANGELOG.md`,
  `planning/ROADMAP.md`.

**Explicitly not touched**: `docs/`, `README.md`, `architecture/`,
`ai-docs/`, `src/codecompass/`, `decisions/*`, `CLAUDE.md`,
`docs/domain/`.

## 4. Verification

1. The milestone-closeout-checklist's own stale numbers are fixed and
   verified against the current roadmap.
2. `release-phase-auditor`'s own report addresses every item in §2.1
   and §2.2 explicitly, not a generic "looks fine."
3. Any `FAIL` finding gets a fix and a re-audit before this phase is
   considered done.
4. Standard mechanical checks: `check_user_docs.py --strict`,
   `check_knowledge_base.py`, full `pytest` (expect 623 passed / 2
   skipped, no `src/codecompass/` change this phase).
5. Per-phase drift audit run as standard practice.
6. Closeout: retro, `knowledge-curator` learning triage, this phase's
   *own* independent confirmation that the audit itself was genuine
   (a lighter lead-confirmation, not a second full `release-phase-auditor`
   dispatch auditing the auditor — matching this project's own
   proportionality principle for a phase whose entire deliverable
   already *is* an independent audit).

## 5. Deferred (explicitly out of scope for this phase)

- The actual milestone-closeout artifact, doc freeze, and bulk retro
  review (Phase 69).
- The version bump, tag, and `twine upload` (Phase 70 — an explicit,
  irreversible human-decision gate, G9, requiring the actual user's own
  go-ahead, not the lead's).
- Deciding GATE DD.
- Any `src/codecompass/` change.
