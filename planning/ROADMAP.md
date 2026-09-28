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
| **A — Task context completeness** | Reliably answer "what does a fresh agent need to safely understand, design, implement, or review this specific change?" (producers/consumers, siblings, execution/behavioural paths, tests, docs/ADRs, upstream references, compatibility gaps, explicit uncertainty). Absorbs Phase 48, `CG-001`/`CG-006`/`CG-007`. | A `context-evaluator` PASS or PASS WITH GAPS (not FAIL) on a real reference-project task specifically because task-relevant context was surfaced, not merely present in the graph. | Detection fix landed ([`phase-73`](phase-73-doc-relations-filename-matching.md), `CG-006`). Real-task validation run: [`Phase 75`](phase-75-ledgerkit-priority-a-validation.md) — `context-evaluator` verdict **PASS WITH GAPS, advantage LOW** on a genuine Ledgerkit task (`04-cur-query-priority-a-validation.md`); the one flashy treatment finding was confirmed agent-diligence variance (`L-027`), not a CodeCompass contribution. `CG-001` stays `candidate` — a provisional `recurred` call was made, then independently reversed by `knowledge-curator`'s own same-phase triage (the report's own `context-evaluator` section had already recommended cross-reference-not-promotion using this entry's own established precedent), reviewed and concurred by the lead; retained as a third cross-reference for its own §2.6 hypothesis, not promoted. `CG-007` unchanged (no new evidence this task). New gap `CG-009` filed (zero first-party-source symbol index — the dominant reason CodeCompass helped with none of the task's technical core). Recommended next step: a second, differently-shaped Priority A trial before any funding decision, not immediate implementation. A capability build followed instead, at direct user request: [`Phase 76`](phase-76-git-repository-topology.md) (Git repository topology awareness) — `context-evaluator` verdict **PASS WITH GAPS, advantage MODERATE**, the strongest Priority A result to date. New gaps `CG-010`/`CG-011` filed, both `candidate`. `CG-009` (zero first-party-source symbol index) is now planned: [`Phase 77`](phase-77-first-party-source-and-template.md) — precedes, does not replace, the second differently-shaped Ledgerkit trial this row's own history recommended (that trial's `CG-001` motivating shape needs first-party *relationships*, Phase 77's own explicitly-deferred follow-on). |
| **B — Lightweight claim/evidence/contradiction model** | Productise Phase 54c's already-proven, already-durable-recommended Observation/Evidence/Claim model for a *downstream user's own project* (not `planning/knowledge/`'s internal-only use). Also exercises the contradiction-handling machinery against real conflicting evidence for the first time. | A downstream-facing claim can be recorded with ≥1 evidence item, a closed status value, and — for at least one real case — a genuine contradiction surfaced rather than silently resolved. | Hardening landed: [`planning/phase-74-provenance-hardening.md`](phase-74-provenance-hardening.md) (`L-031`/`L-032`). The broader productisation itself remains not yet planned. |
| **C — Context gap detection and research tasks** | Productise `planning/context-gaps/`'s already-proven candidate→recurred→promoted lifecycle for gaps in a *target* project's own context, convertible into a concrete task. | A gap identified in a real target project is expressible as an actionable task without hand-authoring a new template each time. | Not yet planned. |
| **D — Documentation-first development workflow** | Package the proven Scope→Plan→Domain→Design→Implement workflow *shape* (`decisions/0060`) — not CodeCompass's own specific agent roster — as guidance a downstream user's process could adopt, reusing `query`/Skill/graph capabilities. | A downstream user can follow research→evidence map→design→review→packet→implementation→verification→retro→knowledge-update using only already-shipped CodeCompass surfaces plus documented convention, no new agent required. | First concrete deliverable planned: [`Phase 77`](phase-77-first-party-source-and-template.md) — `codecompass-template` (`https://github.com/ctosullivan/codecompass-template`, already exists, currently empty) is being populated and delivered as a real, usable MIT-licensed scaffold by that phase, not merely designed. Investigation found no new runtime tooling required, documented convention/empty scaffolding only, matching this priority's own success criterion closely. |
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
| **`CG-007`** — symbol-level cross-reference between pinned reference-doc excerpts | candidate | A second independent occurrence (a different pair of pinned excerpts, or a different reference project). |
| **`CG-009`** — `symbols` table has no path for a project's own first-party source, any ecosystem (filed Phase 75) | candidate, addressed by [`Phase 77`](phase-77-first-party-source-and-template.md) (planned, not yet done — triage/closure happens at that phase's own closeout via real Ledgerkit evidence, not by this row's own edit) | Superseded by Phase 77's own DoD once it closes. |
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
| 75 | **Priority A Ledgerkit validation** — real-task evaluation (implementing hledger's `cur:` query term in Ledgerkit's own query engine), baseline vs. CodeCompass-assisted, independently rated by `context-evaluator`. Verdict: **PASS WITH GAPS, advantage LOW**. `CG-001` stays `candidate` (a provisional `recurred` call was reversed on `knowledge-curator` re-verification); new gap `CG-009` filed and confirmed `candidate`; two new process learnings promoted (`L-062`, `L-063`). Full plan: `planning/phase-75-ledgerkit-priority-a-validation.md`. Retro: `planning/retros/phase-75-ledgerkit-priority-a-validation.md`. | done | [`planning/phase-75-ledgerkit-priority-a-validation.md`](phase-75-ledgerkit-priority-a-validation.md) |
| 76 | **Git repository topology awareness (worktrees + submodules)** — direct user request, new Priority A capability. Three new `context-graph.db` tables (`git_repositories`, `git_worktrees`, `git_submodules`, schema version 9→10), a new `git_topology.py` detection module, and `codecompass query topology`, so a fresh agent can distinguish worktrees of one repository from separate projects and a submodule's parent-pinned commit from its actual checked-out state — validated against this project's own real submodules (`decisions/0058`) and a disposable test worktree/clone. Independently rated by `context-evaluator`: **PASS WITH GAPS, advantage MODERATE** — the strongest Priority A result to date. New gaps `CG-010`/`CG-011` filed; process learning `L-064` filed (a genuine recurrence of `L-063`). Also fixed a real pre-existing bug found via live testing: `_migrate_doc_artifacts_constraints` fired on any unrelated `schema_version` bump. Does not redefine deferred Phase 24 (chat project-root routing) — a different capability, cross-referenced only. **Reopened 2026-09-28** (same day as the original `done` mark) for a narrowly-scoped corrective pass after direct user review found three real post-closeout defects: (1) the CLI `query topology` text renderer collapsed several nullable/unresolved topology facts (`is_dirty`, `revision_matches_pin`, submodule `child_is_dirty`) into false-certainty negatives; (2) the documented Git minimum-version floor was wrong (2.5, not the real 2.7 — `git worktree list`/`git remote get-url` require Git 2.7.0, `decisions/0064` superseding `decisions/0063` point 8); (3) `CLAUDE.md` §5's own closeout rule was internally self-contradictory, fixed with an explicit exemption (user-approved diff). All three fixes landed on `main` (`feaaaa0`, `db33352`, `bb21122`, plus process-operationalization commit `6d668db` filing `L-065` and plan-amendment commit `a89920d`), full test suite/`ruff`/both doc-check scripts clean. Closeout sequence completed: phase-retro corrective-pass addendum (`924bea5`); fresh independent `docs-reconstructor` drift audit, **NO DRIFT** (`planning/retros/_drift-audit-phase-76-corrective.md`, `0db424a`); `knowledge-curator` triage of `L-065` — **promoted**, confirmed sound and complete against all three landed artifacts (`f7016e9`); fresh independent `release-phase-auditor` completion audit of the corrective pass itself — **PASS WITH NON-BLOCKING OBSERVATIONS** (`planning/retros/_audit-phase-76-corrective.md`, `71231ea`), its one blocking precondition (committing the `L-065` triage) resolved before this terminal reconciliation. **Restored to `done`** by this reconciliation. Full plan (including corrective-pass amendment): `planning/phase-76-git-repository-topology.md`. Retro: `planning/retros/phase-76-git-repository-topology.md`. Original independent `release-phase-auditor` completion audit of the phase's original scope (superseded by the reopening, not re-litigated): **PASS WITH NON-BLOCKING OBSERVATIONS** (`planning/retros/_audit-phase-76.md`). | done | [`planning/phase-76-git-repository-topology.md`](phase-76-git-repository-topology.md) |
| 77 | **First-party source awareness (`CG-009`) + a usable `codecompass-template`** — direct user request, new Priority A capability + Priority D's first concrete, delivered scaffold. `source_files` gains a first-party **`language`** concept (Python/Rust/JavaScript/TypeScript/Haskell — deliberately not a reuse of `core.Ecosystem`, which cannot distinguish JS from TS) plus an explicit four-state symbol-indexing outcome (`indexed`/`unsupported`/`parse_error`/`unreadable`, never a bare empty list standing in for failure); new `source_symbols` table with occurrence-based identity (`UNIQUE(source_file_id, name, kind, line)`, chosen after live-verifying that a name-only key crashes real `sync` on genuine function overloads, confirmed on both Python `@overload` and TypeScript); first-party extraction covers implementation scope (non-exported/private top-level declarations included, `visibility` recorded, never filtered out) via a new `source_symbols.py` module, and `codecompass query source`/`query source-symbol`. Amended 2026-09-28: **`codecompass-template`** (`https://github.com/ctosullivan/codecompass-template`, confirmed to already exist, empty) is now populated and delivered as a real, usable MIT-licensed scaffold by this phase itself, not merely designed — validated against a real clone of the real repository. Three required validations (the real template repository, Ledgerkit, CodeCompass dogfooding) plus an independent Priority A task-context evaluation. Explicitly precedes, does not replace, the second differently-shaped Ledgerkit Priority A trial Phase 75 recommended. Full plan: `planning/phase-77-first-party-source-and-template.md`. | planned | [`planning/phase-77-first-party-source-and-template.md`](phase-77-first-party-source-and-template.md) |

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
