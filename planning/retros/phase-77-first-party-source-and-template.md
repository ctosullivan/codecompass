# Phase 77 retro — First-party source awareness + `codecompass-template`

- **Date:** 2026-09-29
- **Commit(s):** `18cb251`, `fa47972` (second plan amendment), `03f8519`
  (implementation), `5993113` (template cross-link), `910fb35`
  (validation records), `b473e84` (baseline/treatment reports),
  `f75bd99` (context evaluation), `5398eb3` (CG-009 reassessment),
  `04b87c2`/`68e80b3`/`41ed6aa` (drift-audit fixes + domain-skeptic
  review) — plus this retro's own commit and the closeout sequence that
  follows it.
- **Agents used:** two general-purpose agents (baseline, treatment),
  `context-evaluator`, `knowledge-curator` (twice — `CG-009` reassessment,
  learning triage), `docs-reconstructor` (drift audit + re-audit),
  `domain-skeptic`, `release-phase-auditor`, `roadmap-context-curator`.

## Where we are

Post-v1, Priority A track (`decisions/0062`). Phase 76 (Git repository
topology) was this track's most recent capability build, closed and
corrected two days ago. This phase is the second: it directly targets
`CG-009` (filed Phase 75 — zero first-party-source symbol index, the
dominant reason CodeCompass's own Ledgerkit trial found none of the
task's technical core) and, at direct user request, also delivers
Priority D's first concrete artifact — a real, populated,
MIT-licensed `codecompass-template` repository.

## Goal

Make a project's own first-party source files and top-level
implementation symbols durable, queryable `context-graph.db` objects,
independent of `vendor.toml`, closing `CG-009` — and separately deliver
a genuinely usable `codecompass-template` scaffold at its own
already-existing (but previously empty) repository, packaging the
proven downstream-adoption workflow shape without CodeCompass's own
internal governance history.

## Scope delivered vs planned

Delivered, after two rounds of plan amendment (both made before
implementation began, at direct user request):

- **`source_files`/`source_symbols`**: a first-party `Language` concept
  (not a reuse of `core.Ecosystem`); an honest five-state
  `symbol_index_status` (`indexed`/`indexed_partial`/`unsupported`/
  `parse_error`/`unreadable`); occurrence-based symbol identity
  (`UNIQUE(source_file_id, name, kind, line)`, `line NOT NULL`); a
  five-value `exposure` classification (`public`/`restricted`/
  `internal`/`conventional_private`/`unknown`); a project-level
  `meta.source_index_version` marker.
- **CLI**: `query source`/`query source-symbol`, kept structurally
  separate from `query symbol`.
- **`codecompass-template`**: populated and pushed to its own real,
  existing remote — 13 files, MIT-licensed, independently authored.
- **Three real validations**: a fresh clone of the real template
  (zero-vendor acceptance test, plus an independent fresh-agent
  readability assessment — READY), CodeCompass's own dogfooding, and a
  fresh Ledgerkit clone (the principal `CG-009` evidence).
- **One independent Priority A evaluation**: PASS WITH GAPS, advantage
  LOW — see "What was achieved" below for why this is a genuine, honest
  result, not a shortfall in execution.
- **`CG-009` reassessment**: promoted to `promoted-to-roadmap`/resolved
  by independent `knowledge-curator` triage, not lead fiat.

No scope was dropped. Two amendment rounds (five corrections each)
happened entirely before implementation, at the user's own explicit
insistence on fixing schema/ontology/identity problems before code was
written — matching Phase 76's own precedent of catching expensive
problems at the cheapest point to fix them.

## What was achieved

A real, working, end-to-end capability, verified against three genuinely
different real targets (a populated template, CodeCompass's own 91-file/
1,165-symbol first-party tree, and Ledgerkit's real `Posting`/`Amount`/
`Tag`) — not synthetic fixtures. The independent Priority A evaluation's
own **LOW** advantage rating is itself a real, valuable, honestly-reported
finding: the specific task chosen (locate a `DataFrame`-export feature)
happened to require *method-level* symbols, nested inside classes — a
capability Phase 77 explicitly, deliberately, three-times-disclosed as
out of scope this phase (top-level only). The treatment agent did *more*
total work (17 calls vs. 13) for an equal-quality final answer, and the
independent evaluator confirmed this is the tool working exactly as
documented, not a defect — correctly declining to file a new context
gap for it. This is the same discipline that made Phase 75's own LOW
result credible rather than convenient, applied again here, on a
different capability, with the same honest outcome.

## What worked

- **Two full rounds of plan amendment before any code was written**
  caught real, expensive-to-fix-later problems at the cheapest point:
  the language-vs-ecosystem ontology mismatch, the fresh/upgraded
  nullability inconsistency, the name-only symbol-identity crash (**live-
  verified** on both a real Python `@overload` stack and a real
  overloaded TypeScript declaration before any schema was written), the
  binary exposure model's inability to represent Rust's real three-tier
  visibility, and the `indexed`/`indexed_partial` fidelity distinction.
  Every one of these was a real, demonstrated defect the live
  verification step caught, not a hypothetical.
- **`agent-led-workflow.md` step 5's own new rule — write a referenced
  agent's report to disk immediately on receipt — worked exactly as
  intended on its first real exercise since landing at Phase 76's own
  corrective pass.** Both the baseline and treatment reports were
  written to disk the moment each arrived, before the next dispatch
  prompt was drafted; the `context-evaluator` dispatch correctly pointed
  at real files, not a claimed conversation-history access. `L-064`'s
  own proposed fix is now confirmed working, not merely landed.
- **The independent `context-evaluator`'s own fresh reproduction of the
  treatment agent's self-disclosed limitation** (re-running `codecompass
  query source-symbol to_dataframe` itself, tracing the gap to
  `source_symbols.py`'s own `ast.iter_child_nodes` not descending into
  `ClassDef` bodies) is exactly the "establish ground truth directly,
  never trust either report" discipline this role exists for, and it
  correctly declined to file a gap that would have misused the
  context-gaps queue.
- **`domain-skeptic`'s own strict write-boundary discipline held under
  direct pressure** — the dispatch prompt explicitly invited it to fix
  citations and add content, and it declined both, handing back
  precise, independently-re-derived fixes instead. It also caught two
  citations that were **already broken before this phase**
  (`relationship-edge.md`'s own `rebuild_deterministic` citation, and
  `provenance.md`'s own `_migrate_symbol_enrichment_model_column`
  citation) — real, pre-existing drift this phase's own diff happened
  to surface by shifting the same file's other line numbers.
- **`knowledge-curator`'s `CG-009` reassessment was a genuine, evidenced
  decision, not a rubber stamp** — it read the real schema directly
  (confirmed no `vendor_id` FK on either new table), re-ran the
  zero-vendor acceptance test's own logic conceptually, and explicitly
  addressed why the separate LOW-advantage evaluation did *not* weigh
  against closure, rather than silently ignoring a result that could
  have looked like a complication.

## What didn't work

- **No real misfires this phase.** The closest candidate — needing two
  plan-amendment rounds before implementation — is not itself a failure;
  it's the plan-before-implementing discipline (`CLAUDE.md` §1) working
  as intended, catching real problems before they became expensive code
  changes.

## Lessons learnt

- **A binary classification (public/private, indexed/failed) is often
  the wrong first guess for a genuinely cross-language or cross-technique
  concept.** Both the exposure model and the indexing-status model
  started as binaries in the first amendment and needed a second round
  to become honest — Rust's real three-tier visibility and the real
  fidelity gap between a structural parser and a coarse heuristic don't
  fit two boxes. Worth checking for this shape explicitly (not just "is
  this nullable," but "is this genuinely binary") the next time a
  cross-language or cross-technique classification is designed.
- **Live-verifying a natural-key design against a real, ordinary language
  feature (not just an edge case) before committing to schema is cheap
  insurance.** The overload-collision risk would have been a real
  production crash on real code, not a hypothetical — confirmed in
  minutes with two small test files, before any schema was written.

## Process-improvement feedback

None beyond what's already captured above (the step-5 rule's own first
successful exercise). No new friction found in the agent-led workflow
itself this phase.

## Candidate learnings filed

None new this phase, beyond `CG-009`'s own reassessment (a context-gap
resolution, not a new `L-NNN`). The independent evaluation's own finding
(treatment did more work for an equal outcome on a method-level task) is
fully explained by Phase 77's own documented non-goal boundary and does
not warrant a new process learning — it's evidence the tool's own scope
disclosure is honest, not a gap in the tool or the process.

## Where we're going

`CG-009` is resolved. The natural next Priority A candidate is now the
relationship phase this project's own plan explicitly deferred
(`source_file → imports`, `source_symbol → references/calls`,
`test → tests`, `doc → documents`) — likely the shape that finally makes
a genuine `CG-001`-shaped trial possible, per Phase 77's own plan §7.
The previously-recommended second, differently-shaped Ledgerkit Priority
A trial remains live, unclaimed, and is **not** silently treated as
satisfied by this phase's own Ledgerkit-based evaluation (a different
task, a different question). `codecompass-template` now exists as a
real, validated artifact — a natural foundation for Priority C/D's own
further, not-yet-planned productisation work.

## Time / cost note

One extended session, spanning two plan amendments, full implementation,
real MIT template authorship and publication, three real validations
(one against a genuinely fresh clone plus an independent fresh-agent
readability assessment), one baseline/treatment/context-evaluator
Priority A trial, and a full closeout sequence including an independent
domain-corpus citation review. Real AI subagent spend: two dispatched
agents (baseline, treatment) plus `context-evaluator`, `docs-reconstructor`
(twice), `domain-skeptic`, `knowledge-curator` (twice), plus the standard
closeout roster — no shortcuts on any of them. Test suite grew by 39 new
tests (`test_source_symbols.py`) plus additions across three existing
test files; full suite 733 passed, 2 skipped throughout implementation.
