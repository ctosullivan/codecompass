# Phase 65: Architecture + ADR reconciliation — plan

**Status:** planned (2026-09-23).

**Stage G, second phase** (`planning/v1-redefinition/roadmap.md`).
Gated on Phase 64 completing — **done 2026-09-23, PASS**, unblocked.
Not gated on GATE DD (a separate axis, per `decisions/0056`).

## 0. What this phase is, and isn't

Per `planning/v1-redefinition/documentation-lifecycle.md` §4: compare,
deliberately —

```
current project reality  →  blank-slate reconstruction (Phase 64)
              VERSUS
        existing active documentation
```

— and for **each** current doc (and each proposed doc), record a
decision: **retain / rewrite / consolidate / split / replace / remove /
preserve only in historical state (tag + closeout)**. Output a
reconciliation table (`planning/v1-docs-reconstruction/reconciliation.md`)
with a one-line rationale per doc, then the lead + `docs-maintainer`
**act on it in this same phase** (not deferred further — this phase's
own deliverable is the applied result, not only the table).

Also, per the roadmap's own Phase 65 entry: **ADR status review** (mark
superseded ADRs, don't rewrite them — ADRs stay append-only per
`CLAUDE.md` §2) and **domain-corpus freshness reconciliation**
(`development-methodology.md`'s own "Domain-corpus freshness and
reconciliation" section, added `decisions/0060` 2026-09-20) —
`domain-skeptic` re-checks every staleness candidate `docs-reconstructor`'s
per-phase drift audits have flagged since Phase 63D's corpus was
approved, resolving what it can with fresh evidence and escalating only
genuine remaining ambiguities to the actual user/domain owner.

**No new domain investigation** — Phase 63D's own corpus stays
authoritative; this phase only checks it for *drift since approval*, a
narrower question. **No new agent roles.** `src/codecompass/` changes
only where a documentation reconciliation genuinely requires touching
code comments/docstrings this phase's own scope covers (expected to be
none or minimal — this is a documentation phase).

## 1. Concrete inputs (already exist, no re-derivation)

- **`planning/v1-docs-reconstruction/`** (Phase 64's shadow proposal,
  28 files, all six documentation categories) — the "blank-slate
  reconstruction" side of the comparison.
- **`planning/v1-docs-reconstruction/concepts-to-retire.md`** — 5
  consolidated retirement candidates (1 removal, 2 trims, 1 framing
  note, 1 structural split), each already grounded against real source.
- **`planning/v1-redefinition/architecture-split-candidates.md`** — the
  Phase 42 `docs-maintainer` catalogue of 32 remaining history-shaped
  passages in `architecture/overview.md` (§A: 5 section-level; §B: 27
  passage-level). §C's 4 self-contradictory items were already fixed at
  Phase 43b — not this phase's job again. **Overlaps with
  `concepts-to-retire.md`**: item 1 there (`Grounded description —
  retired`) is the same section as this catalogue's §A.1; item 2 there
  (per-ecosystem adapter prose) overlaps this catalogue's item 12 (`Per-
  vendor CLAUDE.md structure`) and adjacent adapter-detail passages —
  cross-reference, don't duplicate the decision.
- **The current `decisions/` corpus** — 59 ADRs. 48 carry no
  "superseded" text in their own body (candidates to re-check for silent
  supersession); 11 already reference a superseding ADR (confirm those
  cross-references still resolve correctly, per
  `check_adr_status_and_supersedes` — a mechanical check, not this
  phase's own job to re-verify by hand beyond what that check already
  does).
- **`docs-reconstructor`'s per-phase drift audits since Phase 63D's
  corpus was approved** — `planning/retros/_drift-audit-phase-64.md`
  (the only one so far; found zero domain-claim staleness candidates).

## 2. Scope, by sub-task

### 2.1 ADR status review

Read all 59 ADRs. For each of the 48 without existing "superseded"
text: check whether its own decision has, in practice, been silently
reversed or replaced by a later phase's real implementation without a
formal superseding ADR ever being written (a genuine governance gap —
`CLAUDE.md` §2 requires a new numbered ADR for any reversal, not a
silent one). **Mark, don't rewrite**: if a genuine silent reversal is
found, write the new superseding ADR now (this is exactly the kind of
non-obvious tradeoff `CLAUDE.md` §2 already requires one for) — do not
edit the old ADR's own original content beyond adding the standard
short addendum pointing at its successor. For the 11 already marked
superseded: confirm via `check_adr_status_and_supersedes` (already
clean, re-run to confirm) that every cross-reference resolves.

### 2.2 `architecture/overview.md` reconciliation

Process all 32 `architecture-split-candidates.md` items plus
`concepts-to-retire.md`'s two overlapping items as one combined list —
for each, a retain/rewrite/consolidate/split/replace/remove decision.
Expected large outcome (named in advance by
`documentation-lifecycle.md` §4 itself): **split `architecture/overview.md`
into a lean current-state document plus a historical/superseded note**
— matching Phase 64's own `architecture/` shadow-proposal set
(`module-map.md`, `core-data-model.md`, `context-graph-schema.md`,
`sync-and-enrichment-pipeline.md`, `adapter-interface.md`) as the
current-state target shape, with genuinely load-bearing history (not
already captured in an ADR) moved to a dedicated historical note rather
than deleted outright, per `documentation-lifecycle.md` §1.3.

### 2.3 Remaining current-truth docs reconciliation

`docs/` (CLI reference, config schema, quickstart if one doesn't exist
yet), `docs/external-adapters.md`, `README.md`, `ai-docs/` — compared
against Phase 64's own `docs/`, `protocol-adapter/`, `domain/`,
`development-process/` proposals. Concrete inputs:
`concepts-to-retire.md` items 3 (`docs/config-schema.md` legacy-field
history), 4 (per-command phase/decision-status framing), 5
(`docs/external-adapters.md` split candidate). `docs/domain/` itself is
**not** reconciled against Phase 64's `domain/` proposal in the sense of
retain/rewrite — Phase 64's own `domain/` category is a reorganization
proposal for *presentation*, not a competing claim about meaning;
decide only whether any of that reorganization is worth adopting
alongside the existing `docs/domain/` corpus (e.g. a "quick reference"
page), not whether `docs/domain/`'s own content changes.

### 2.4 Domain-corpus freshness reconciliation

Dispatch `domain-skeptic` to re-check the one staleness candidate
surface available so far: `planning/retros/_drift-audit-phase-64.md`
found zero domain-claim staleness candidates, so this is expected to be
a short, confirmatory pass — verify that finding directly rather than
skip the step because it's expected to be empty. If genuinely nothing
has changed since Phase 63D's own approval that touches a `docs/domain/`
citation, say so plainly (matching `docs-reconstructor`'s own "NO DRIFT
is a fine and common verdict" precedent) rather than manufacture a
finding.

## 3. Files created/changed

- **`planning/v1-docs-reconstruction/reconciliation.md`** (new) — the
  full retain/rewrite/consolidate/split/replace/remove table, one row
  per document, covering §2.2 and §2.3's combined scope.
- **`architecture/overview.md`** — split per §2.2's decision (exact
  resulting file names decided during the phase, informed by Phase 64's
  own `architecture/` proposal shape).
- **`architecture/` historical note** (new file, name TBD by the
  reconciliation decision) — load-bearing history moved out of the
  current-state document.
- **`docs/`**, **`docs/external-adapters.md`**, **`README.md`**,
  **`ai-docs/`** — updated per §2.3's reconciliation decisions.
- **New ADR(s) under `decisions/`** — only if §2.1 finds a genuine
  silent reversal (not assumed in advance; may be zero).
- Standard closeout: `planning/retros/phase-65-architecture-adr-reconciliation.md`
  (retro), `planning/retros/_drift-audit-phase-65.md` (per-phase drift
  audit), `planning/retros/_audit-phase-65.md` (`release-phase-auditor`),
  `planning/learnings/inbox.md` (any candidates), `planning/CONTEXT.md`,
  `CHANGELOG.md`, `planning/ROADMAP.md`.

**Explicitly not touched**: `docs/domain/` (frozen, Phase 63D's own
approved corpus — only reconciled *from*, never edited here unless
`domain-skeptic`'s own freshness check finds a genuine, evidenced
staleness requiring a correction, which would follow that corpus's own
existing amendment process, not this phase's general reconciliation
one), `CLAUDE.md`, past ADRs' own original content (append-only).

## 4. Dispatch strategy

1. **`docs-maintainer`**, given `architecture-split-candidates.md`,
   `concepts-to-retire.md`, and Phase 64's full `planning/v1-docs-reconstruction/`
   tree: draft `reconciliation.md` (the full table, §2.2 + §2.3 scope) —
   a recommendation, not a final decision (`documentation-lifecycle.md`
   §4: "the lead + `docs-maintainer` act on it").
2. **Lead** reviews the draft table, decides each row, then dispatches
   `docs-maintainer` again (or applies directly, for a small enough
   change) to execute the decisions — the `architecture/overview.md`
   split being the largest single action.
3. **`domain-skeptic`**, in parallel with 1: the freshness reconciliation
   (§2.4) — independent of the reconciliation-table work, no shared file.
4. **Lead**, in parallel with 1/3: the ADR status review (§2.1) — a
   direct read-through, not delegated (ADRs are the lead's own write
   boundary per `CLAUDE.md` §8; the *review* can still be the lead's
   own direct work rather than a dispatch, since it requires judgment
   about whether a new ADR is warranted, the lead's call either way).

## 5. Verification

1. **`reconciliation.md` completeness**: every document named in
   `architecture-split-candidates.md`'s 32 items and
   `concepts-to-retire.md`'s 5 items has a recorded decision.
2. **`architecture/overview.md` no longer contains** any of the 32
   catalogued history-shaped passages in their original form — spot-check
   at least 10 of the 32 directly against the new file(s).
3. **Every current-truth doc change is verified against real `src/`**,
   not merely copied from Phase 64's proposal — Phase 64's own proposal
   was itself independently derived, but this phase's application step
   re-confirms at least the highest-risk claims (spot-check 5 across the
   changed files) rather than trusting a chain of two derivations
   uncritically.
4. **Standard mechanical checks**: `python scripts/check_user_docs.py
   --strict`, `python scripts/check_knowledge_base.py`,
   `check_adr_status_and_supersedes` specifically (part of the strict
   run), full `pytest` (expect 623 passed / 2 skipped unless a
   docstring/comment change in `src/` was genuinely required — named
   explicitly if so, not silently introduced).
5. **Per-phase drift audit** (`docs-reconstructor` MODE 1): confirm no
   *new* drift was introduced by this phase's own edits (a real risk,
   unlike Phase 64's own trivially-NO-DRIFT verdict, since this phase
   does touch current-truth docs).
6. **`domain-skeptic`'s freshness reconciliation report** exists and
   states plainly whether anything was found (expected: nothing, given
   Phase 64's own drift audit found zero staleness candidates) — a
   confirmed-empty result is a valid, complete answer, not a skipped step.
7. **Closeout**: retro, `knowledge-curator` learning triage,
   `release-phase-auditor` DoD pass.

## 6. Deferred (explicitly out of scope for this phase)

- `docs/domain/` content changes beyond what `domain-skeptic`'s own
  freshness check evidences and resolves (Phase 63D's own amendment
  process governs any such change, not a general Phase 65 rewrite).
- `planning/ROADMAP.md`/`planning/CONTEXT.md` full milestone
  reconciliation — Phase 66.
- Final self-dogfood + Ledgerkit + Stage F smoke-test re-confirmation —
  Phase 67.
- Any `src/codecompass/` behavioural change (only docstrings/comments,
  and only if a reconciliation decision genuinely requires touching
  one — not expected, but not pre-emptively ruled impossible either).
