# Documentation lifecycle plan (required outputs 6 and 12)

Redefines documentation management as a **lifecycle** — incremental
maintenance during development *plus* blank-slate renewal at milestones —
rather than perpetual incremental patching that accretes caveats.

Implemented by Phase 42 (incremental + closeout gate) and Phase 60–61
(blank-slate reconstruction + reconciliation). Owned by `docs-maintainer`
(incremental) and `docs-reconstructor` (blank-slate).

## 1. Three distinct documentation roles

### 1.1 Current truth — active documentation
`README.md`, `docs/`, `architecture/`, `ai-docs/`. Describes CodeCompass
**as it exists now**. Explicitly allowed to be substantially rewritten,
reorganised, consolidated, split, or **deleted**. It must **not** be
forced to explain every historical way CodeCompass once worked.
> Current documentation earns its place by accurately and economically
> explaining the current project.

Current visible debt this is meant to fix: `architecture/overview.md` is
**1,954 lines** and already shows the accretion pattern (historical
notes, "superseded by" pointers, "Phase N added… later Phase M changed…"
narration inline). That is decision history living in a current-truth
doc.

### 1.2 Decision history — ADRs
`decisions/`. Preserves **why** the project evolved as it did.
Append-only (`CLAUDE.md` §2). A superseded ADR stays as a historical
record — it is **not** rewritten to pretend the old decision never
happened; it gets a short addendum pointing at its successor, and the
successor states the reversal.

### 1.3 Historical milestone state — git tags / releases + closeout artifacts
Git tags/releases are the primary archive of complete historical source +
documentation state. The active repo does **not** carry full duplicate
documentation trees to preserve history. Where useful, a milestone may
add a concise closeout artifact (see §5): a closeout report, an
architecture summary, a release-doc bundle, a retired-concept note.

## 2. Incremental maintenance during development (the everyday half)

On any phase that changes CLI behaviour, config schema, generated-file
formats, or system design:

1. The implementing work updates affected `docs/` / `architecture/` /
   `README.md` / `ai-docs/` **in the same commit** (`CLAUDE.md` §2 —
   unchanged).
2. `docs-maintainer` then reconciles: checks the doc change against the
   **verified** implementation (not the plan's intent); rewrites weak
   prose; **removes** now-false statements; **resists** adding "note:
   since Phase N this also…" — if a paragraph is now wrong, fix the
   paragraph, don't annotate it.
3. Deterministic doc checks run (`scripts/check_user_docs.py`, extended
   in Phase 42): every CLI command documented; README phase/feature
   claims consistent with `ROADMAP.md`; every `VendorConfig`/schema field
   documented; `ai-docs/` files present and non-empty; **internal links
   resolve; fenced example commands are real commands** (new in Phase 42).
4. `release-phase-auditor` (or lead) confirms as part of DoD.

Goal of this half: **keep current documentation accurate during
development.** It is only half.

## 3. Blank-slate reconstruction (the milestone half) — Phase 60

At major milestones, `docs-reconstructor` approaches CodeCompass **as
though the current narrative documentation did not exist**.

- **Inputs (authoritative project reality only):** current `src/`;
  tests; CLI behaviour / `--help`; config / schema; generated outputs
  (a real `vendor/`, a real `context-graph.db`, generated Skills,
  `/discovery`); ADRs; current `architecture/` *(read for facts, not for
  narrative structure)*; current planning/project state.
- **It does not read `README.md` / `architecture/overview.md` as a
  starting structure** — the point is a fresh derivation of what a new
  user, contributor, maintainer, and AI coding agent each need, and how
  the current system should be explained from scratch.
- **Output:** a temporary/shadow proposal under
  `planning/v1-docs-reconstruction/` — proposed `README.md`, proposed
  `docs/` set, proposed `architecture/` set, an explicit list of concepts
  the current docs spend words on that the current *system* no longer
  justifies.
- **It does not overwrite anything.**

## 4. Reconciliation — Phase 61

Compare, deliberately:

```
current project reality  →  blank-slate reconstruction
              VERSUS
        existing active documentation
```

For **each** current doc (and each proposed doc), a recorded decision:
**retain / rewrite / consolidate / split / replace / remove / preserve
only in historical state (tag + closeout)**.

The output is a reconciliation table
(`planning/v1-docs-reconstruction/reconciliation.md`) with a one-line
rationale per doc, then the lead + `docs-maintainer` action it. This is
what prevents:

```
old explanation + later caveat + later exception + migration note
+ correction + additional caveat = technically defensible, conceptually poor
```

Expected large item at the redefined-v1 milestone: `architecture/overview.md`
split into a lean current-state document + the historical/superseded
narration moved out (to ADR addenda where it's rationale, or simply
dropped where git history already covers it).

## 5. Milestone documentation closeout gate — Phase 66

A checklist file `planning/milestone-closeout-checklist.md` (created in
Phase 42), executed at Phase 66:

1. deterministic documentation checks pass;
2. blank-slate reconstruction done (Phase 60);
3. comparison / reconciliation done (Phase 61);
4. obsolete current documentation deleted (not annotated);
5. link / example / reference validation passes;
6. architecture documentation review — current-state only, history
   removed;
7. ADR status review — superseded ADRs marked (not rewritten); any
   decision made during the milestone that lacks an ADR gets one;
8. final current-doc freeze for the milestone (no further current-doc
   edits until after the tag, except fixes to what the freeze itself
   surfaces);
9. milestone closeout artifact written where useful
   (`planning/v1-closeout.md`: architecture summary, what shipped, what
   deferred + revisit triggers, key ADRs, reference-project evaluation
   results);
10. git tag / release preserving the complete historical state.

## 6. ADR lifecycle (unchanged mechanism, explicit here)

- New ADR whenever a phase involves a non-obvious tradeoff (`CLAUDE.md`
  §2) — including tradeoffs surfaced by reference-project evidence, not
  only ones known up front.
- Reversal → new numbered ADR + addendum on the old one. Never edit a
  past ADR's original content.
- Phase 61 step 7 is a *review*, not a rewrite — it checks that every
  superseded ADR carries its pointer and every milestone decision has a
  record.

## 7. What does not change

- `CLAUDE.md` §0 (protected-file approval) applies to `CLAUDE.md` itself
  regardless of anything here. `docs-reconstructor` and `docs-maintainer`
  never touch it.
- `CLAUDE.md` §2's same-commit rule for the *incremental* half.
- The `decisions/` append-only rule.
- `decisions/0039` (ship without a dedicated docs site) stands unless a
  Stage F finding supersedes it — the reconstruction may *recommend* a
  site if real reference-project/user friction showed up, via a new ADR.
