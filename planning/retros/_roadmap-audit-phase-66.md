# `ROADMAP.md` full-table audit — Phase 66, §1.1

**Auditor:** `roadmap-context-curator` (dispatched sub-agent). **Date:**
2026-09-24. **Scope:** `planning/phase-66-roadmap-context-reconciliation.md`
§1.1 — read every row of `planning/ROADMAP.md`, Phase 0 through Stage G,
cross-checked against `git log`, `planning/retros/`, plan files, and
`planning/v1-redefinition/roadmap.md`. This is a findings list only — no
fix applied here; the lead reviews and applies.

## Method

- Read `planning/ROADMAP.md` in full (both halves, lines 1-408).
- Listed `planning/retros/` and `planning/*.md` and cross-checked every
  `done` row's retro citation against an actual file on disk.
- Cross-checked deferred/not-funded/CONDITIONAL rows' revisit-trigger
  wording against later phases' actual outcomes (git-log-dated), to
  confirm nothing recurred/resolved without the row catching up.
- Read `planning/v1-redefinition/roadmap.md`'s Stage G intro (the
  "if Stage D/E were skipped per GATE DD, Stage G runs against the Stage
  C product instead" text) and Phase 55/48/50 stanzas directly, since the
  plan names this as the citation this phase should confirm reads clearly.
- Spot-checked `planning/CONTEXT.md`'s tail (its own "Next concrete step"
  section) against `ROADMAP.md` row 66 and the actual repo state, since
  a same-session L-034/L-038-shaped gap would show up as a disagreement
  between the two files, not only within one row's own prose.

## Findings

### F1 — Header's own status-value legend omits "not funded", which two live rows use verbatim

`ROADMAP.md` line 10-13 defines the closed status vocabulary: `not
started` / `planned` / `in progress` / `done` / `deferred` / `superseded`.
Rows 48 and 50 (Post-MVP → redefined-v1 table) both literally read
**`not funded`** in the Status column — a value absent from the file's
own defining legend. This is exactly the "status field vs. its own prose
(here: the file's own header prose)" class of gap named in the dispatch
brief (L-034/L-038's shape), just at the document-header level rather
than a single row. The phase-66 plan's own dispatch text treats
"deferred/not-funded/CONDITIONAL" as a recognized three-way class, so
"not funded" is clearly an intentional, load-bearing distinction from
plain "deferred" (GATE-B non-funding vs. general parking) — the fix is
almost certainly to add `not funded` to the legend line, not to change
the rows. Low severity, but a real inconsistency between the file's own
stated vocabulary and its own table. **Recommend:** add `not funded
(a CONDITIONAL/gated row a funding gate explicitly declined — revisit
trigger named in the row)` to the Status-values legend line.

### F2 — `v1-redefinition/roadmap.md`'s Phase 55b stanza describes `L-021` as "drafted, not yet approved" — now stale

`planning/v1-redefinition/roadmap.md` line ~1033-1035 (Phase 55b's done
account, dated 2026-09-17) reads: *"A process-lesson candidate (`L-021`)
proposes a `CLAUDE.md` §1 amendment requiring a test through a function's
real production call site... — drafted, not yet approved."* This is now
false: `L-021` **was** approved and applied — `planning/learnings/promoted.md`
line 25 records `L-021 | 2026-09-17 | project-rule | CLAUDE.md §1 +
CONTRIBUTING.md ... @ 899449d`, and `CLAUDE.md` §1 itself, as currently
checked into the tree, contains the exact amendment text with an explicit
`(Phase 55b — L-021.)` citation. Unlike the file's deliberate "dated
scope note" / "renumbering note" passages (which are explicitly framed as
historical snapshots and correctly left unedited per the append-only
convention), this sentence sits inside Phase 55b's *live, present-tense*
status account with no "as of [date]" framing, so a reader hits a
flatly wrong claim about current reality. **Recommend:** a small
follow-up clause (not a rewrite of the historical sentence) noting
`L-021` was subsequently approved and applied to `CLAUDE.md` §1 — same
treatment this file already gives other superseded-in-place claims.
This is technically in `v1-redefinition/roadmap.md`, not `ROADMAP.md`
itself, but the dispatch brief and the curator's own hard rules both
call out that "roadmap.md" means both files.

### F3 — `ROADMAP.md` row 55 (GATE DD) doesn't link the reconciliation package that is its actual working document

`planning/phase-55-evidence-reconciliation.md` exists, is explicitly
titled as GATE DD's evidence-reconciliation package, is directly cited
from `v1-redefinition/roadmap.md`'s Phase 55b stanza ("Full account:
`planning/phase-55-evidence-reconciliation.md` §G"), and is the document
GATE DD's eventual decision will actually be made from. `ROADMAP.md`'s
own row 55 Plan-file column reads `—` (none). This isn't wrong per se —
the reconciliation doc isn't a `CLAUDE.md` §1 implementation plan for a
single unit of work (its own first line says so: "not a phase plan for a
single unit of work"), so the `—` isn't a contradiction of the status
column. But since the doc exists and is load-bearing for this exact row,
leaving it uncited is a minor completeness gap. **Recommend (optional,
non-blocking):** link `phase-55-evidence-reconciliation.md` from row 55's
Plan-file column or its own prose, so a reader lands on GATE DD's actual
working document instead of a bare dash.

### F4 — `planning/CONTEXT.md`'s current tail says Phase 66 is "not yet planned" — already stale as of this session's own first commit

`planning/CONTEXT.md` line 2220 currently reads: *"Next: Phase 66
(roadmap + context reconciliation), not yet planned"*. This was
overtaken by this session's own first action: commit `598460c`
(`plan(phase-66): roadmap + context reconciliation`, per `git log`)
already added `planning/phase-66-roadmap-context-reconciliation.md` and
flipped `ROADMAP.md` row 66 to `planned` in the same commit, per
`CLAUDE.md` §1. This is a `ROADMAP.md`-vs-`CONTEXT.md` disagreement of
the exact shape `ROADMAP.md`'s own "How this file is kept in sync"
section calls "a bug to fix immediately" — flagged here for the lead's
already-scoped `CONTEXT.md` rewrite (§1.2 of this phase's plan) rather
than fixed in this dispatch, since `CONTEXT.md` is explicitly the lead's
own direct-work item this phase, not this audit's file to touch.
Out of strict `ROADMAP.md`-table scope, included because it's a live
disagreement between the two files this curator role exists to catch.

## Confirmed clean (checked, no issue found)

- **Retro existence for every `done` phase that requires one.** Every
  `done` phase from Phase 41 onward (the point `CLAUDE.md` §5's retro
  requirement took effect, per the amendment `ROADMAP.md` itself
  documents as "applied in Phase 41") has a real file under
  `planning/retros/phase-N-*.md` — verified by directory listing, not
  by trusting each row's own citation: 41, 42, 43, 43b, 43c, 43d, 43e,
  44, 45, 46, 47, 49, 51, 52, 53, 54, 54b, 54c, 55b, 60, 61, 62, 63, 63D,
  64, 65 all confirmed present. Phases 0-40 (and 39/40 themselves)
  predate the retro requirement and correctly have none — not a gap.
  (43d/43e's retros reuse a plan-file-shaped filename inside `retros/`,
  but their content is genuine retro content, confirmed by reading both.)
- **Audit-report existence, where required.** Phases with a standalone
  `_audit-phase-N.md`/`_drift-audit-phase-N.md` pair: 41, 42, 43, 43b,
  43c, 43d/43e (combined), 44, 45, 46, 47, 49, 51, 52, 53, 55b, 62, 63,
  63D, 64, 65 — all present. Phases 54, 54b, 54c, 60, 61 have no
  standalone `_audit-phase-N.md` file, but each one's own retro embeds
  an explicit `release-phase-auditor` verdict inline (verified by
  grep: 54 → "PASS (first round)"; 54b → PASS WITH GAPS-equivalent
  language embedded in the evaluation write-up; 54c → "Round 2: PASS
  WITH NON-BLOCKING OBSERVATIONS"; 60 → "release-phase-auditor's re-audit
  confirmed the two fixes above"; 61 → PASS WITH GAPS cited). `CLAUDE.md`
  §5 requires "an independent `release-phase-auditor` pass... verifies
  the preceding conditions," not a specifically-named separate file —
  so this is a filename-convention variance across the session, not a
  DoD gap. Not flagged as an error; noted only in case the lead wants
  consistent naming going forward.
- **Revisit-trigger wording, Phases 24/25/48/50.** All four still read
  accurately as of 2026-09-24:
  - Phase 24 — "revisit as a redefined-v1 Stage C candidate only if
    reference-project evidence shows project-root context routing is a
    recurring need." Stage C (Phases 44-51) has since run to completion
    without ever specifically testing this hypothesis (`grep` of Phase
    47's own findings/retro shows zero mentions of "project-root" or
    "routing") — the trigger's *substance* hasn't fired, so "deferred"
    remains correct, but the trigger names a stage that has since closed.
    Worth a lead judgment call on whether to reword "Stage C" → "no
    stage has tested this yet" for precision, though this is a
    precision nit, not a factual error (Stage C could in principle still
    be read as "the stage during which this could have surfaced, and
    didn't" rather than "a future stage still to come").
  - Phase 25 — "revisit post-redefined-v1, informed by real CLI/Skill
    usage." No stage-specific claim to go stale; still accurate.
  - Phase 48 — "not funded... revisit if `CG-001`'s hypothesis
    independently recurs." Confirmed via `context-gaps/inbox.md` and
    `findings.md`: `CG-001` is still `candidate`, still single-occurrence,
    no second real-project occurrence recorded through Phase 65. Accurate.
  - Phase 50 — "not funded... if 'specialist agents re-discover the same
    relationships' recurs." No evidence of recurrence found in any later
    phase's retro. Accurate.
- **Stage E (56-59) / GATE DD (55) recorded as intentionally, legitimately
  open.** `ROADMAP.md` rows 55 and 56-59 correctly show `not started` with
  an explicit `CONDITIONAL (GATE DD)` label rather than a bare, unexplained
  gap. The roadmap's own already-settled design for "what if this never
  resolves before v1 ships" is confirmed present and legible at
  `planning/v1-redefinition/roadmap.md` line 1690-1692 ("If Stage D/E
  were skipped per GATE DD, Stage G runs against the Stage C product
  instead — the checklist is identical") — this reads as a deliberate,
  already-ratified fallback design, not an oversight or an abandoned
  commitment. Phases 60-65 (all done, all Stage F/G work) each explicitly
  restate "does not resolve GATE DD, does not complete or bypass Phases
  55-59" in their own row prose, which is itself further evidence this
  is being tracked deliberately every time, not silently forgotten.
  Nothing to fix here — this phase's own job (per its plan's explicit
  framing) is to confirm this reads clearly, not re-litigate it, and it
  does.
- **No other row-level status/prose contradiction found.** Checked every
  row's Label vs. Status vs. prose combination across both tables (MVP
  v0.1, MVP v0.2, Post-MVP, redefined-v1 Stages A-G, future-improvement
  backlog): all internally consistent. Rows for split/partial phases
  (23: "Part A done; Part B superseded") and compound labels (47/55:
  "EXPERIMENTAL → decision") are non-enum but self-explanatory composites
  of already-legend-defined words, consistently used the same way every
  time they occur — not flagged as errors, distinct in kind from F1's
  entirely-undefined "not funded" value.
- **`L-031`/`L-032` future-improvement backlog rows.** Both confirmed
  still `not started` / unscheduled in `planning/learnings/promoted.md`
  — no later phase has claimed either. Table entries accurate.
- **Cross-references checked live:** `decisions/0056` (cited by the
  Phase 66 plan for "not gated on GATE DD, a separate axis") — confirmed,
  line 112-113 states exactly that. `planning/v1-redefinition/development-methodology.md`
  (cited by Phase 63D's row) — exists. `decisions/0060` (Phase 63D's own
  bridge-numbering ADR) — exists.

## Bottom line

The table is **not fully clean** — two small, real issues (F1: legend
omission for "not funded"; F2: one stale present-tense claim in
`v1-redefinition/roadmap.md`'s Phase 55b stanza) plus two optional/
non-blocking completeness notes (F3: Phase 55's missing plan-file
cross-link; F4: a `CONTEXT.md`-side staleness this phase's own §1.2 work
already plans to fix). None of these represent a phase wrongly marked
`done`, a missing retro, or a genuinely misleading row — this session's
own discipline of updating `ROADMAP.md` same-commit with every phase held
up under a full re-check back to Phase 0. F1 and F2 are the only two
items that plausibly warrant a same-phase fix; F3 is optional; F4 is
explicitly the lead's own §1.2 CONTEXT.md-rewrite work, not a new
`ROADMAP.md` finding.
