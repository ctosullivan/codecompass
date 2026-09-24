# Phase 71: Post-v1 documentation refresh — plan

**Status:** done (2026-09-25).

**First post-v1 phase — not part of the redefined-v1 milestone group**
(that group, `decisions/0048`, Phases 39–70, is closed). Direct user
request, 2026-09-24: a ground-up documentation refresh reflecting the
now-final, shipped v1 state, since much current-facing content still
describes an in-progress or pre-release project.

## 0. What this phase is, and isn't

**A rewrite of current-facing, user/contributor-oriented documentation
against verified current behaviour — not a second blank-slate
reconstruction from zero.** Phases 64–65 already did the full
blank-slate derivation-and-reconciliation cycle for `architecture/` and
most of `docs/`, and that material is recent (this session) and
already verified fresh at Phase 68's own milestone-level audit. This
phase's real job is narrower and different in kind: **`README.md`
and `planning/ROADMAP.md` were explicitly excluded from Phase 64/65's
own scope** (`README.md` because the shadow-proposal reconciliation
never adopted a full README rewrite; `ROADMAP.md` because it is
governance bookkeeping, not a current-truth product doc in
`documentation-lifecycle.md`'s own sense) — and Phase 70's own drift
audit just found real, user-facing staleness in exactly `README.md`
(now fixed, minimally). This phase does the *thorough* version of that
fix, plus `planning/CONTEXT.md`'s own further reduction, plus a
consistency sweep of everything else current-facing.

**Historical material is explicitly out of scope and must not be
rewritten**: `decisions/*` (append-only), `planning/retros/*`,
`planning/v1-redefinition/*`, `planning/reference-projects/*`,
`planning/knowledge/*`, `planning/learnings/*`, `docs/domain/*`
(Phase 63D's own approved, evidence-backed corpus — current-truth
*content*, not something this phase re-derives or edits), `CLAUDE.md`.
These are read *as input* (verified current behaviour and evidence),
never rewritten as if they were stale product docs.

## 1. Scope

### 1.1 `README.md` — full rewrite

Ground-up, using already-fresh, already-verified material as primary
input rather than re-deriving from scratch:
`architecture/module-map.md`/`core-data-model.md`/`adapter-interface.md`/
`context-graph-schema.md`/`sync-and-enrichment-pipeline.md`,
`docs/quickstart.md`/`cli-reference.md`/`config-schema.md`/
`developer/`/`protocol-adapter/`, `docs/domain/glossary.md` (for the
evidence/provenance model, cited not re-derived), `planning/v1-closeout.md`
(shipped-state summary, reference-project evaluation results),
`decisions/0048` (the v1 redefinition itself, for positioning
language). Live-verify anything not already covered by that material
directly against `src/`/tests/real command output — don't chain
derivations uncritically.

Must cover, per the user's own explicit list: purpose; current
capabilities; architecture at a useful (not exhaustive) level;
installation/usage (the real `pip install codecompass-context` /
`codecompass` split, verified); supported ecosystems/adapters
(npm/Python/Cargo/Haskell — in-process vs. external-process, per
`docs/domain/concepts/adapter.md`); the evidence/provenance model (a
plain-language summary, linking to `docs/domain/` for depth, not
restating it in full); limitations (drawn from
`planning/CONTEXT.md`'s own "Known standing gaps," honestly, not
softened); project status and **realistic v1 positioning** — explicitly
**not** overstating Ledgerkit's own measured context advantage
(PASS WITH GAPS / **LOW**, with a stated structural reason, per
`planning/v1-closeout.md` §5) or claiming any capability that remains
merely planned (GATE DD/Stage E, Phases 24/25/48/50 — all deferred, not
shipped).

**Mechanical constraint**: `scripts/check_user_docs.py::check_readme_phase_count`
requires a `phases 0-N` claim in `README.md`'s own text, cross-checked
against `ROADMAP.md`'s foundation table — keep one unobtrusive mention
(e.g. in a brief "project history" note, not prominent v1-era framing)
so the rewrite doesn't silently disable an existing, working drift
check. Not proposing to change the check itself — out of this phase's
own scope (a `scripts/` behaviour change the user didn't ask for).

### 1.2 `planning/ROADMAP.md` — concise current-state restructure

Replace the full phase-by-phase historical status table (currently 412
lines, Phase 0 through 70) with: a short "v1.0.0 shipped" summary
(pointing at `planning/v1-closeout.md` for the full historical
record — nothing is lost, it already lives there and in git history),
the still-relevant **deferred/not-funded items with their own revisit
triggers** (GATE DD/Stage E, Phases 24/25/48/50 — these are the parts
of the old table with genuine forward-looking value), and a **new,
short, currently-empty post-v1 tracking section** for whatever comes
next. The detailed phase-by-phase table itself is not deleted from the
project — it remains fully readable via git history at any pre-Phase-71
commit and via `planning/v1-redefinition/roadmap.md`'s own
per-stage detail (already a durable planning document, unaffected by
this phase).

### 1.3 `planning/CONTEXT.md` — further reduction

Already rewritten to ~94 lines at Phase 66/70 (down from ~2450). Review
against `CLAUDE.md` §4's own literal four fields once more now that v1
is shipped — the "Current phase" section's own multi-bullet stage
recap is now obsolete framing (there is no more "Stage G in progress");
replace with the minimum needed for a future session to resume
sensibly: current state in 1-2 sentences, what was just completed,
next concrete step. The "Known standing gaps" list stays (genuinely
current-state facts, not phase history).

### 1.4 Consistency sweep — other current-facing docs

Read `docs/`, `architecture/README.md`/`overview.md`, `ai-docs/*.md`,
`CONTRIBUTING.md`, `examples/README.md` for any remaining reference to
the project as unreleased, in-progress, or version `1.0.0.dev0`, and
for any link/cross-reference that breaks once `README.md`/`ROADMAP.md`
are restructured. Fix only what's genuinely inconsistent with the
shipped state — not a second full rewrite of already-fresh material.

## 2. Dispatch strategy

1. **Lead** drafts `README.md` directly (a synthesis document
   requiring the full arc of this project, not delegatable) and
   `planning/ROADMAP.md`'s restructure.
2. **A fork**, independent consistency review: read the new
   `README.md`/`ROADMAP.md` against `src/`, real `--help` output,
   `planning/v1-closeout.md`, and `docs/domain/`, checking specifically
   for (a) any overstated capability or context-advantage claim, (b)
   any claim contradicted by verified behaviour, (c) any broken
   internal link. Reports findings; does not fix them itself.
3. **Lead**, informed by 2: fixes findings, finalizes
   `planning/CONTEXT.md`'s own reduction, does the consistency sweep
   (§1.4).
4. **`docs-reconstructor`** (MODE 1, per-phase drift audit): the
   standard independent audit, scoped to this phase's real diff.

## 3. Files created/changed

- `README.md` — full rewrite.
- `planning/ROADMAP.md` — restructured (historical table replaced by a
  concise summary + pointer + the still-relevant deferred-item rows).
- `planning/CONTEXT.md` — further reduced.
- Possibly `docs/`, `architecture/README.md`, `ai-docs/*.md`,
  `CONTRIBUTING.md`, `examples/README.md` — only where the consistency
  sweep (§1.4) finds a genuine, specific inconsistency.
- Standard closeout: `planning/retros/phase-71-post-v1-documentation-refresh.md`
  (retro), `planning/retros/_drift-audit-phase-71.md` (per-phase drift
  audit), `planning/learnings/inbox.md` (any candidates),
  `planning/CONTEXT.md`, `CHANGELOG.md`, `planning/ROADMAP.md` (this
  phase's own row, in the new, concise post-v1 tracking section).

**Explicitly not touched**: `decisions/*`, `planning/retros/*`
(existing files), `planning/v1-redefinition/*`, `planning/reference-projects/*`,
`planning/knowledge/*`, `planning/learnings/*` (existing entries —
only new candidates this phase itself raises get added),
`docs/domain/*`, `CLAUDE.md`, `src/codecompass/` (no behaviour change).

## 4. Verification

1. `README.md` covers every item the user's own request named, each
   grounded in a citation to real project state (a file, a command, a
   test) — not asserted from memory.
2. No capability described as shipped that is actually deferred/
   conditional (GATE DD/Stage E, Phases 24/25/48/50) — spot-checked
   against `planning/v1-closeout.md`'s own "what was deferred" section.
3. Ledgerkit's own real evaluation result (PASS WITH GAPS / LOW
   advantage) is stated accurately, not rounded up.
4. `scripts/check_user_docs.py --strict` passes (link resolution,
   the `readme_phase_count` check, ADR cross-references, fenced example
   validity) — the single highest-risk mechanical check for this
   specific phase, given the scale of the rewrite.
5. `scripts/check_knowledge_base.py` passes (nothing here should touch
   the knowledge base, but confirmed anyway).
6. Full `pytest` unchanged (expect 625 passed / 2 skipped — no
   `src/codecompass/` change).
7. The independent fork review's own findings are addressed before
   closeout, not merely reported.
8. Per-phase drift audit: expected `NO DRIFT` once the above lands
   (this phase's entire point is closing drift, so a clean audit is
   the actual goal, not merely an expected default).
9. Closeout: retro, `knowledge-curator` learning triage,
   `release-phase-auditor` DoD pass (standard single-phase — no
   milestone-level audit needed, that was Phase 68's own one-time job).

## 5. Deferred (explicitly out of scope for this phase)

- Any `src/codecompass/` behavioural change.
- Rewriting `docs/domain/` (frozen, Phase 63D's own approved corpus).
- Rewriting any historical planning/retro/ADR content.
- Deciding GATE DD or funding any deferred phase.
- Changing `scripts/check_user_docs.py`'s own check logic (kept
  compatible, not modified).
