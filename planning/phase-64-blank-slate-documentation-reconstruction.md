# Phase 64: Blank-slate documentation reconstruction — plan

**Status:** done (2026-09-23). See
`planning/retros/phase-64-blank-slate-documentation-reconstruction.md`
(retro), `planning/retros/_drift-audit-phase-64.md` (docs-reconstructor
drift audit — NO DRIFT), and `planning/retros/_audit-phase-64.md`
(release-phase-auditor) for the full closeout record.

**Stage G's first phase** (`planning/v1-redefinition/roadmap.md`,
`decisions/0060`). Gated on Phase 63D completing — **done 2026-09-23,
PASS**, unblocked. Not gated on GATE DD (a separate axis, per
`decisions/0056`).

## 0. What this phase is, and isn't

Per `planning/v1-redefinition/documentation-lifecycle.md` §3 and
`decisions/0060`: `docs-reconstructor`, in its MILESTONE mode, derives
**a fresh proposal** of what CodeCompass's documentation ought to be —
approaching the system as though its current narrative documentation
(`README.md`, `docs/`, `architecture/`) did not exist — from
authoritative project reality (`src/`, tests, CLI `--help`, config
schema, generated artifacts, ADRs, current planning state), **with one
deliberate exception**: domain terminology is not re-derived. Phase
63D's own approved `docs/domain/` corpus is authoritative for what
CodeCompass's concepts mean, and this phase consumes it rather than
guessing at meaning a more careful, evidence-backed, adversarially-
reviewed pass already settled.

**This phase produces a shadow proposal only, under
`planning/v1-docs-reconstruction/`. It never overwrites `docs/`,
`README.md`, `architecture/`, or `ai-docs/`.** Comparing the proposal
against current active documentation and deciding retain / rewrite /
consolidate / split / replace / remove per document is Phase 65's job
(`documentation-lifecycle.md` §4), not this one's. **No
`src/codecompass/` change.**

## 1. A real, disclosed gap this phase must close before dispatching

`.claude/agents/docs-reconstructor.md`'s own MODE 2 section (blank-slate
reconstruction) predates `decisions/0060` and does not yet reflect two
things that ADR already settled:

1. Domain terminology is an explicit exception to "derive everything
   fresh" — the brief's current text says to derive the whole picture
   from `src/`/tests/etc. with no carve-out for `docs/domain/`.
2. The output is organized into **six documentation categories**
   (domain / architecture / user / developer / protocol-adapter /
   development-process — `documentation-lifecycle.md` §1.4), not the
   three-way `README.md`/`docs/`/`architecture/` + `concepts-to-retire.md`
   split the brief currently names.

This phase's own Files section (§3) amends the brief to match the
already-authoritative governing docs before any dispatch happens — the
same kind of pre-dispatch brief correction Phase 63D made to
`context-researcher.md` and `docs-reconstructor.md`'s MODE 1 section.

## 2. Dispatch strategy

Three parallel `docs-reconstructor` (MODE 2) dispatches, each independent
and read-only toward `src/`/tests/current docs, each writing only its
own assigned subtree under `planning/v1-docs-reconstruction/` — matching
Phase 63D's own successful three-cluster pattern (splitting a large
derivation task without diluting any one dispatch's focus, while still
requiring each to cross-reference neighbouring categories it touches):

- **Cluster A — User + Developer.** Derive, from `codecompass --help`
  (every subcommand), `pyproject.toml`, the `vendor.toml` schema, and
  real generated artifacts (a real `vendor/`, `context-graph.db`,
  generated Skills, `/discovery`): a proposed user-facing `docs/` set
  (CLI reference, config schema, quickstart) and developer-facing
  content (writing a new adapter, the test/lint/release workflow).
- **Cluster B — Architecture + Protocol/adapter.** Derive, from
  `src/codecompass/` + tests + the context-graph schema in `graph.py`:
  a proposed `architecture/` set (current-state only, no history) and
  the protocol/adapter section (the external-process wire protocol,
  `decisions/0057`-`0059`, superseding `docs/external-adapters.md`'s
  own current content where it's stale).
- **Cluster C — Domain (reorganize, not re-derive) + Development-process.**
  Reads `docs/domain/` directly and reorganizes it for this proposal's
  own presentation needs (no new investigation, no new claims); derives
  a durable, user-facing version of
  `planning/v1-redefinition/development-methodology.md` (the
  Scope → Plan → Domain → Design → Implement process itself, made
  presentable outside the `v1-redefinition/`-scoped planning tree).

Each dispatch also proposes retirement candidates for its own area
(concepts the *current* docs spend words on that the *current system*
no longer justifies); the lead consolidates all three into one
`concepts-to-retire.md` rather than each cluster writing a fragment.

After all three land, the lead reads across all six categories for
cross-cluster consistency (do Cluster A's and Cluster B's proposals use
domain terms the same way `docs/domain/` defines them? does the
protocol/adapter section duplicate content Cluster A's user docs already
cover?) before closing the phase — this is a lead synthesis pass, not a
`domain-skeptic` dispatch (that role's own charter is domain-*meaning*
adversarial review, already discharged at Phase 63D; this is a
structural/presentation consistency check over a docs proposal, a
different kind of check).

## 3. Files created/changed

- **`.claude/agents/docs-reconstructor.md`** — MODE 2 section amended:
  explicit `docs/domain/` consumption exception; six-category output
  structure; drop the stale three-way + `concepts-to-retire.md`-only
  framing.
- **`planning/v1-docs-reconstruction/README.md`** (new) — index: what
  this shadow proposal is, its six-category structure, explicitly not
  yet applied to real docs (that's Phase 65).
- **`planning/v1-docs-reconstruction/domain/`** (new) — `docs/domain/`
  content reorganized for this proposal's presentation, cross-linked to
  the other five categories.
- **`planning/v1-docs-reconstruction/architecture/`** (new) — proposed
  current-state architecture set.
- **`planning/v1-docs-reconstruction/docs/`** (new) — proposed user +
  developer content.
- **`planning/v1-docs-reconstruction/protocol-adapter/`** (new) —
  proposed external-integration content.
- **`planning/v1-docs-reconstruction/development-process/`** (new) —
  proposed durable, user-facing development-methodology content.
- **`planning/v1-docs-reconstruction/concepts-to-retire.md`** (new) —
  lead-consolidated retirement candidates across all three clusters.
- Standard closeout: `planning/retros/phase-64-blank-slate-documentation-reconstruction.md`
  (retro), `planning/retros/_drift-audit-phase-64.md` (per-phase drift
  audit — expected `NO DRIFT`, since no current-truth doc or `src/` is
  touched this phase), `planning/retros/_audit-phase-64.md`
  (`release-phase-auditor`), `planning/learnings/inbox.md` (any
  candidates), `planning/CONTEXT.md`, `CHANGELOG.md`,
  `planning/ROADMAP.md` (this row).

**Explicitly not touched**: `docs/`, `README.md`, `architecture/`,
`ai-docs/`, `src/codecompass/`, `decisions/*`, `CLAUDE.md`.

## 4. Verification

Since this phase produces a proposal rather than changing system
behaviour, "done" is verified differently from a `src/`-changing phase:

1. **Completeness**: all six categories present under
   `planning/v1-docs-reconstruction/`, each grounded in a citation to
   real project state (a file path, a `--help` transcript, a test, an
   ADR) — not asserted from memory of what CodeCompass "probably" does.
   Spot-check: pick 5 concrete claims across the three clusters and
   verify each against the actual current `src/`/`--help` output
   directly (the lead's own check, not trusting each dispatch's
   self-report).
2. **No overwrite occurred**: `git diff --stat` shows no change under
   `docs/`, `README.md`, `architecture/`, or `ai-docs/`.
3. **No `src/codecompass/` change**: `git diff --stat` confirms.
4. **Domain consumption, not re-derivation**: the domain category cites
   `docs/domain/concepts/*.md` directly rather than re-stating
   independently-derived definitions; spot-check at least 3 domain terms
   against `docs/domain/`'s own text for agreement.
5. **Standard mechanical checks unaffected**: `python
   scripts/check_user_docs.py --strict`, `python
   scripts/check_knowledge_base.py`, and full `pytest` all still pass at
   the pre-phase baseline (623 passed, 2 skipped) — this phase adds no
   test surface of its own (no `src/` change) but must not have broken
   anything incidentally (e.g. a stray edit outside
   `planning/v1-docs-reconstruction/`).
6. **Per-phase drift audit** (`docs-reconstructor` MODE 1, independent
   dispatch, not the same context as any MODE 2 cluster above): confirm
   `NO DRIFT` — expected, since no current-truth doc changed.
7. **Closeout**: retro, `knowledge-curator` learning triage,
   `release-phase-auditor` DoD pass, matching every prior phase this
   milestone group.

## 5. Deferred (explicitly out of scope for this phase)

- Actually rewriting/replacing any current-truth doc — Phase 65.
- ADR status review/reconciliation — Phase 65.
- `ROADMAP.md`/`CONTEXT.md` full milestone reconciliation — Phase 66.
- Any `src/codecompass/` change.
- Re-running `domain-skeptic` or re-opening Phase 63D's own domain
  investigation — this phase consumes that corpus as settled input.
