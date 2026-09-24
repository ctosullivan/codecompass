# Roadmap

Tracks every roadmap phase and its completion status. This file is kept
up to date **with every change that affects phase scope or status** — see
`CLAUDE.md` §2. Unlike `planning/CONTEXT.md` (which reflects only the
*current* phase in detail for session-resumption), this file is the
full-roadmap, at-a-glance view: what's done, what's next, what's still
just planned.

Status values: `not started` / `planned` (a `planning/phase-N-*.md` file
exists) / `in progress` / `done` / `deferred` (on the roadmap, not
scheduled — revisit trigger named in the row) / `not funded` (a gate
explicitly declined to fund it, per evidence at the time — revisit
trigger named in the row) / `superseded` (replaced by a later decision
— ADR named in the row).

## v1.0.0 — shipped (2026-09-24)

CodeCompass's full phase-by-phase history through v1.0.0 is preserved
in three places, not repeated here as a 70-row table:

- **[`v1-closeout.md`](v1-closeout.md)** — the milestone closeout
  record: architecture summary, what shipped, what was deferred (with
  revisit triggers), key ADRs, reference-project evaluation results,
  distilled process lessons.
- **[`v1-redefinition/roadmap.md`](v1-redefinition/roadmap.md)** — full
  per-stage detail for the redefined-v1 effort (Stages A–G, Phases
  39–70).
- **Git history** — every phase's own commit(s), retro
  (`retros/phase-N-*.md`), and (where applicable) independent audit
  report, at any commit before Phase 71.

In brief: the **foundation** (phases 0-38) is the npm/PyPI/Cargo
package-source-grounding tool. **Stages A–G** (Phases 39–70,
`decisions/0048`) redefined "CodeCompass v1" from a packaging milestone
into a *product-validation* one — developed agent-led, validated
against a real external reference project (Ledgerkit), improved from
that evidence, released after a blank-slate documentation
reconstruction and an independent milestone-level audit
(`retros/_audit-phase-68.md`, verdict **PASS**). Published to PyPI as
the `codecompass-context` distribution, `1.0.0`, tagged `v1.0.0`,
2026-09-24 (`retros/phase-70-release-v1.md`).

## Deferred / not-funded (post-v1 revisit candidates)

Real, evidenced items intentionally not pursued — each with its own
stated trigger for revisiting, not silently dropped:

| Item | Status | Revisit trigger |
|---|---|---|
| **GATE DD / Stage E** — a generalised technical-dependency/provenance abstraction (Phase 55's own decision, never made either way; Phases 56–59 conditional on it) | not started | New evidence that a generalisation beyond Stage C's own concrete work is actually needed, not merely plausible. GATE DD is a separate axis from Stage F/G, explicitly independent of whether those stages proceed (`decisions/0056`, `decisions/0060`) — Stage G's own release did not require resolving it, and CodeCompass shipped either way. |
| **Phase 24** — project-root-aware REPL routing + whole-project context + dependency rollup at session start | deferred | Reference-project evidence showing project-root context routing is a recurring real need (`decisions/0048`). |
| **Phase 25** — MCP server (`query_vendor`) | deferred | Real post-v1 CLI/Skill usage patterns informing whether an MCP surface would add value (`decisions/0048`). |
| **Phase 48** — task-oriented context retrieval | not funded | New evidence — none found across Phases 44–46's own evaluation (`CG-001`, single-occurrence, own-dev only). |
| **Phase 50** — shared-agent context/entry-point improvements | not funded | New evidence — none found across Phases 44–46's own evaluation. |

Full original reasoning for each: git history (any commit before
Phase 71) and the ADRs/retros each item's own original phase entry
cited.

## Post-v1 development

The redefined-v1 milestone group (Phases 39–70) is complete and
released (`v1.0.0`, `planning/v1-closeout.md`). Phases from here are
ordinary, non-milestone-group development, tracked the same way as any
prior phase — plan file, this table, closeout — but no longer counted
toward any milestone-group tag/release gate.

| Phase | Description | Status | Plan |
|---|---|---|---|
| 71 | **Post-v1 documentation refresh** — direct user request, 2026-09-24. `README.md` rewritten ground-up against verified current v1 state; `ROADMAP.md` restructured (this section) to replace stale phase-status material with a concise current-state view; `CONTEXT.md` further reduced; a consistency sweep of other current-facing docs. Historical material (retros, ADRs, evaluation evidence, `docs/domain/`) preserved as historical record, not rewritten. Full plan: `planning/phase-71-post-v1-documentation-refresh.md` | in progress | [`planning/phase-71-post-v1-documentation-refresh.md`](phase-71-post-v1-documentation-refresh.md) |

## Future-improvement backlog (unscheduled)

Findings that the learning lifecycle
(`planning/v1-redefinition/learning-lifecycle.md` §4) classified
`future-improvement` land here once `knowledge-curator` recommends
promotion — this is that classification's roadmap destination, finalised
by `roadmap-context-curator` per that section. A row here has **no phase
number and is not scheduled**; it becomes a numbered phase only if/when
someone plans one, at which point its row is replaced by the phase's own
row elsewhere in this file (per the "How this file is kept in sync"
section below) rather than left duplicated here. Full evidence lives in
the originating `planning/learnings/inbox.md` entry (and, once the lead
records it, `planning/learnings/promoted.md`); this table only tracks
existence and status.

| ID | Finding | Classification | Status | Notes |
|---|---|---|---|---|
| L-031 | `symbol_enrichment` has no producer-attribution column, unlike `vendor_enrichment`/`doc_relation_enrichment` (both carry `model TEXT NOT NULL`) — `symbol_enrichment` rows currently cannot be attributed to a specific producer (agent or automated API call) at all. Add a `model` column via an additive migration (mirroring `_migrate_symbols_export_kind_note_columns`'s `ADD COLUMN` pattern, Phase 62), or explicitly document the asymmetry as an intentional simplification if a rationale is found. Origin: `L-031` (Phase 63D, `domain-skeptic`'s own review). | FUTURE-IMPROVEMENT | not started | — |
| L-032 | `ExternalAdapterProcess.initialize()` receives `ecosystem` and `capabilities` from an external adapter's wire response (`external_process.py:83-84`) but never validates either: `ecosystem` is never compared against the `core.Ecosystem` value CodeCompass configured the adapter under, and `capabilities` is never checked against the protocol's own closed 4-value set already defined in the same file (`CAPABILITIES`). An adapter reporting a mismatched `ecosystem` string or an unrecognized capability is currently accepted uncomplainingly. Add a membership/equality check in `initialize()`, raising `AdapterError` on mismatch (matching the existing `protocol_version` mismatch handling immediately above it in the same method). Origin: `L-032` (Phase 63D, `domain-skeptic`'s own review). | FUTURE-IMPROVEMENT | not started | — |

## How this file is kept in sync

- Starting a phase: add its plan-file link here and flip status to
  `planned` or `in progress` in the same commit that adds
  `planning/phase-N-*.md` (per `CLAUDE.md` §1).
- Finishing a phase: flip status to `done` in the same commit that marks
  the phase's own plan file `done` (per `CLAUDE.md` §5's definition of
  done).
- Scope changes to any unstarted phase (a roadmap phase gets split,
  reordered, or redefined): update the relevant row(s) here in the same
  commit as whatever decision or ADR records the change.
- This table is the source of truth for "what phase are we on" — if it
  ever disagrees with `planning/CONTEXT.md`, treat that as a bug to fix
  immediately, not a discrepancy to reconcile later.
- A `future-improvement`-classified learning is added to the "Future
  improvement backlog" table above by `roadmap-context-curator`, once
  `knowledge-curator` recommends promotion (`learning-lifecycle.md` §4),
  in the same pass that updates `planning/learnings/inbox.md`'s status
  and `promoted.md`. When a backlog row is later turned into a real
  phase, remove the backlog row in the same commit that adds the phase's
  own row and plan file.
