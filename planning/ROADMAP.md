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

## Post-v1 priorities (A-F)

**Established Phase 72 (`decisions/0062`), replacing the old "Deferred /
not-funded" list above.** Real evidence from Ledgerkit's own Stage C
work (`planning/ledgerkit-stage-c-learnings.md`) shows post-v1
CodeCompass should optimise for **task-context completeness**, not graph
size or feature breadth — most of the mechanisms these priorities need
already exist, proven, as CodeCompass's own internal development
tooling (`planning/knowledge/`, `context-gaps/`, `context-evaluator`);
none has ever been offered to a downstream user of the shipped tool.
Full disposition of every pre-v1 item these priorities absorb, merge, or
leave as backlog: **[`pre-v1-disposition.md`](pre-v1-disposition.md)**.
GATE DD is **not** resolved by this list — see `decisions/0062`'s own
"Decision" section for exactly what remains open.

| Priority | Scope | Success criterion | Status |
|---|---|---|---|
| **A — Task context completeness** | Reliably answer "what does a fresh agent need to safely understand, design, implement, or review this specific change?" (producers/consumers, siblings, execution/behavioural paths, tests, docs/ADRs, upstream references, compatibility gaps, explicit uncertainty). Absorbs Phase 48, `CG-001`/`CG-006`/`CG-007`. | A `context-evaluator` PASS or PASS WITH GAPS (not FAIL) on a real reference-project task specifically because task-relevant context was surfaced, not merely present in the graph. | First concrete step landed: [`planning/phase-73-doc-relations-filename-matching.md`](phase-73-doc-relations-filename-matching.md) (`CG-006`). `CG-001`/`CG-007` — the harder task-oriented-retrieval/execution-path work — remain unplanned. |
| **B — Lightweight claim/evidence/contradiction model** | Productise Phase 54c's already-proven, already-durable-recommended Observation/Evidence/Claim model for a *downstream user's own project* (not `planning/knowledge/`'s internal-only use). Also exercises the contradiction-handling machinery against real conflicting evidence for the first time. | A downstream-facing claim can be recorded with ≥1 evidence item, a closed status value, and — for at least one real case — a genuine contradiction surfaced rather than silently resolved. | Hardening landed: [`planning/phase-74-provenance-hardening.md`](phase-74-provenance-hardening.md) (`L-031`/`L-032`). The broader productisation itself remains not yet planned. |
| **C — Context gap detection and research tasks** | Productise `planning/context-gaps/`'s already-proven candidate→recurred→promoted lifecycle for gaps in a *target* project's own context, convertible into a concrete task. | A gap identified in a real target project is expressible as an actionable task without hand-authoring a new template each time. | Not yet planned. |
| **D — Documentation-first development workflow** | Package the proven Scope→Plan→Domain→Design→Implement workflow *shape* (`decisions/0060`) — not CodeCompass's own specific agent roster — as guidance a downstream user's process could adopt, reusing `query`/Skill/graph capabilities. | A downstream user can follow research→evidence map→design→review→packet→implementation→verification→retro→knowledge-update using only already-shipped CodeCompass surfaces plus documented convention, no new agent required. | Not yet planned. Open question named in `ledgerkit-stage-c-learnings.md` #8: how much of this actually needs product tooling vs. remaining a documented convention. |
| **E — Independent context evaluation** | Offer a repeatable version of the `context-evaluator`/`packet-sufficiency.md` protocol for downstream adoption. | A fresh, independent reviewer (human or agent) can assess packet sufficiency using a documented, repeatable procedure, not bespoke judgment each time. | Not yet planned. |
| **F — Clean-environment reproducibility and context-quality measurement** | Formalise the already-proven scratch-clone/fresh-agent discipline into a repeatable check; keep `context-quality-evaluation.md`'s existing advantage-over-default-pathway metric as primary — explicitly not graph size or edge count. | A context packet can be checked for fresh-session reproducibility mechanically, not only by case-by-case phase diligence. | Not yet planned. |

**Backlog, not absorbed into A-F** (real, not silently dropped, each
with its own revisit trigger — full detail
`pre-v1-disposition.md` §3-4, §9-10):

| Item | Status | Revisit trigger |
|---|---|---|
| **Phase 24** — project-root-aware REPL routing + whole-project context | deferred | Reference-project evidence showing project-root context routing is a recurring real need. |
| **Phase 25** — MCP server (`query_vendor`) | deferred | Real post-v1 CLI/Skill usage patterns informing whether an MCP surface would add value. |
| **Phase 50 remainder** — shared-agent context/entry-point improvements not covered by Priority A/D | not funded | New evidence emerging from post-v1 use. |
| **`CG-003`** — external reference-manual zero representation | candidate | A second independent occurrence, or independent second filing (`context-gaps/README.md`'s own bar). |
| **§2.5 `browser_api`/`platform_api` kind** | deferred indefinitely | Already resolved at `decisions/0056` — only reopens if a real browser/platform-API reference project is separately picked up. |

## Post-v1 development

The redefined-v1 milestone group (Phases 39–70) is complete and
released (`v1.0.0`, `planning/v1-closeout.md`). Phases from here are
ordinary, non-milestone-group development, tracked the same way as any
prior phase — plan file, this table, closeout — but no longer counted
toward any milestone-group tag/release gate.

| Phase | Description | Status | Plan |
|---|---|---|---|
| 71 | **Post-v1 documentation refresh** — direct user request, 2026-09-24. `README.md` rewritten ground-up against verified current v1 state; `ROADMAP.md` restructured (this section) to replace stale phase-status material with a concise current-state view; `CONTEXT.md` further reduced; a consistency sweep of other current-facing docs; two `docs/domain/` citation staleness cases and one stale `CLAUDE.md` §2 description found and fixed. Full plan: `planning/phase-71-post-v1-documentation-refresh.md`. Retro: `planning/retros/phase-71-post-v1-documentation-refresh.md`. | done | [`planning/phase-71-post-v1-documentation-refresh.md`](phase-71-post-v1-documentation-refresh.md) |
| 72 | **Ledgerkit Stage C learnings capture + post-v1 roadmap realignment** — direct user request, 2026-09-27. Records the real learnings from Ledgerkit's own Stage C work (studied at Phases 54/54b/54c/61) as a durable document (`planning/ledgerkit-stage-c-learnings.md`); a new ADR (`decisions/0062`) records the resulting prioritisation pivot; `planning/pre-v1-disposition.md` dispositions every material pre-v1 item; this file's own "Deferred/not-funded" and "Future-improvement backlog" sections replaced by a Priority A-F post-v1 structure (below); a domain-corpus staleness cluster (4 locations, 2 Claim-record supersessions) found and fixed. Full plan: `planning/phase-72-stage-c-learnings-and-roadmap-realignment.md`. Retro: `planning/retros/phase-72-stage-c-learnings-and-roadmap-realignment.md`. | done | [`planning/phase-72-stage-c-learnings-and-roadmap-realignment.md`](phase-72-stage-c-learnings-and-roadmap-realignment.md) |
| 73 | **`mentions_artifact` filename-based matching (closes `CG-006`)** — first concrete Priority A deliverable. Extends `build_doc_relations_edges` to also match a target doc's filename/stem, not only its title, closing a real gap found on `CG-004`'s own original motivating pair; a follow-on gap in relation-enrichment excerpt selection found and fixed in the same phase. Full plan: `planning/phase-73-doc-relations-filename-matching.md`. Retro: `planning/retros/phase-73-doc-relations-filename-matching.md`. | done | [`planning/phase-73-doc-relations-filename-matching.md`](phase-73-doc-relations-filename-matching.md) |
| 74 | **Priority B provenance hardening (`L-031` + `L-032`)** — adds `symbol_enrichment.model` (nullable, honest-gap backfill) and validates the external adapter protocol's `ecosystem`/`capabilities` fields against what CodeCompass configured; both gaps closed across 11 current-truth/domain-corpus doc locations. Full plan: `planning/phase-74-provenance-hardening.md`. Retro: `planning/retros/phase-74-provenance-hardening.md`. | done | [`planning/phase-74-provenance-hardening.md`](phase-74-provenance-hardening.md) |

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

Currently empty: `L-031`/`L-032` (the only two entries this table ever
held) are now owned by Phase 74's own row above, removed from here per
the sync rule below.

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
- When a Post-v1 priority (A-F) gets its first real
  `planning/phase-N-*.md`, flip that priority's own "Status" cell from
  "Not yet planned" to a link to the new phase file, in the same commit
  that adds the phase's own row to "Post-v1 development" above — the
  priority row itself is never removed (it names the ongoing track, the
  phase row names one concrete step within it).
