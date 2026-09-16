# Phase 54 retro — Heterogeneous reference-material experiment

- **Date:** 2026-09-16
- **Commit(s):** (this phase's own closeout commit, see `planning/CONTEXT.md`)
- **Agents used:** `context-evaluator` (independent baseline/treatment
  rating), `reference-project-tester` (context-observations/gaps
  filing), `knowledge-curator` (triage), `release-phase-auditor` (final
  pass).

## Where we are

Stage D's substantive goal, finally run for real. The user's own prompt
resolved the open Stage D-vs-Stage-F/G strategic decision (Phase 51's
retro) in Stage D's favour, and named exactly the objective Stage D's
own pre-existing sketch already described.

## Goal

Test whether CodeCompass can pin and expose external hledger reference
material so it materially improves an agent's context for a real
Ledgerkit task, without prematurely committing to a new graph ontology
— via a real, reproducible ingestion pipeline and a genuine two-run
comparison task, independently evaluated.

## Scope delivered vs planned

Delivered exactly as scoped in
`planning/phase-54-heterogeneous-reference-material-experiment.md`: the
ingestion pipeline (`references.toml`/resolve/lock/fetch-cache/extract,
kept outside `src/codecompass/`), the chosen task (`tag:` query-term
semantics brief, Ledgerkit's own next explicitly-deferred Stage C query
feature), a real two-run comparison (baseline vs. treatment),
independent `context-evaluator` rating of both, and every real friction
point filed via Phase 52's context-observation/context-gap queues. One
real deviation from the plan's own expectation, disclosed honestly
rather than hidden: the plan expected the outcome to be a clean
positive, negative, or inconclusive result on the *mechanism*; what
actually happened was a genuine methodological defect in the
*experiment's own execution* (a mis-drawn extraction line range),
independently caught by the evaluator, that determined the treatment
run's verdict as much as the mechanism itself did.

## What was achieved

1. **A real, tested, working ingestion pipeline**
   (`planning/reference-projects/ledgerkit/reference-experiment/`, 13
   passing tests) implementing the full
   `references.toml → resolve → lock → fetch/cache → extract → index`
   shape against the real, live-confirmed pinned hledger clone (tag
   `1.52.4`, commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`) —
   idempotent, content-hash-verified, and rejecting a stale/mismatched
   local clone rather than silently trusting it.
2. **A real two-run comparison task**, both sides genuinely attempted
   (not simulated): baseline used a live `WebFetch` of hledger.org plus
   a local-clone grep, mirroring Ledgerkit's own real
   `hledger-researcher` workflow exactly; treatment used only
   CodeCompass's `query relations` output and the ingested,
   provenance-tagged extraction files, against a scratch copy of
   Ledgerkit (never the real clone).
3. **Four real, evidence-backed findings about CodeCompass's own
   mechanisms**, none assumed in advance:
   - Detection (`dev-docs/**/*.md` glob, Phase 49's fix) generalises to
     externally-ingested content with zero code change (`OBS-007`).
   - Mechanical `mentions_artifact` relation detection structurally
     cannot relate two `spec_doc`-kind artifacts to each other, in any
     project, because `spec_doc` rows never get a `name` (`CG-004`).
   - `doc_artifacts.origin`'s closed enum has no value for
     externally-pinned reference material — it's indistinguishable from
     a project's own hand-authored prose (`CG-005`).
   - A working alternative relation mechanism — parsing a compat-register
     entry's own structured `evidence.ref` citations and matching them
     against the pinned extraction's file+line-range — was built,
     tested, and demonstrated real against the actual, already-published
     `LK-COMPAT-QUERY-DATE-001.yaml` (`OBS-008`), entirely outside
     `src/codecompass/`.
4. **An independent, ground-truth-checked evaluation** (`context-evaluator`,
   never trusting either brief's self-report): baseline **PASS WITH
   GAPS**, treatment **FAIL**, context-advantage **LOW** — with full,
   specific, independently-re-derived evidence for every claim in the
   verdict, not an impression.
5. **A real defect caught, root-caused, and fixed within the same
   phase, not hidden**: the treatment run's own extracted manual excerpt
   silently excluded one of three tag-inheritance rules its own
   description claimed to contain — independently caught by
   `context-evaluator`, filed as `L-020`, fixed (`references.toml`
   corrected, artifact regenerated, a new regression test added), with
   the original FAIL verdict and the uncorrected brief both preserved
   as the honest historical record, per this project's own "don't
   retroactively edit an evaluation's basis" convention (matching
   Phases 45/46's own FAIL verdicts, never edited after their root
   causes were later fixed).

## What worked

- **Grounding the chosen task in Ledgerkit's own real, current,
  unstarted work** (`tag:`, explicitly named as deferred in its own
  `ROADMAP.md`) rather than inventing a scenario — this is exactly what
  made the comparison meaningful rather than a toy: a real
  `hledger-researcher`-shaped brief, checkable against real, existing
  sibling evidence (`LK-COMPAT-QUERY-DATE-001.yaml`'s own citation
  format).
- **Dispatching independent evaluation and letting it find something
  real**, rather than treating the phase's own write-up as sufficient.
  `context-evaluator`'s FAIL verdict is the single most valuable output
  of this phase — it caught a defect the lead's own two brief documents
  did not catch, and it caught it by doing exactly what its role
  requires: checking ground truth directly, not trusting either brief's
  self-report.
- **Testing the cheapest hypothesis first, every time**: detection
  before relation, existing-mechanism reuse before a new schema value,
  demonstrating the YAML-evidence fallback against real already-
  published data rather than a synthetic fixture. Every escalation in
  this phase was earned by a real negative result, not assumed.
- **Not softening the FAIL verdict.** The temptation to quietly fix the
  line-range bug and re-run before anyone saw the FAIL was real and
  explicitly resisted — the plan's own "treat negative or inconclusive
  results as valid evidence" instruction, applied to the phase's own
  execution, not just to the mechanism's outcome.

## What didn't work

- **The experiment's own manual line-range selection was itself an
  unvalidated, error-prone step** — exactly the kind of thing an
  ingestion pipeline promising "provenance you can trust without
  re-checking" should not itself introduce. This is not a mechanism
  failure so much as a methodology gap in how *this phase* built its
  own test fixture — worth generalising (see `L-020`) rather than
  treating as a one-off transcription slip.
- **The baseline's own real `WebFetch` step was also imprecise** (it
  omitted the account-level tag-inheritance rule), which somewhat
  flattens the comparison's own contrast — both runs had a real accuracy
  gap this phase surfaced, from different causes (AI-summarization loss
  vs. a mis-drawn extraction boundary), neither of which is a CodeCompass
  detection/relation defect per se.

## Lessons learnt

1. **A content-hash-pinned artifact's hash proves the content hasn't
   silently changed; it does not prove the content's boundary matches
   what the artifact's own description claims about it.** These are two
   different guarantees, and conflating them is exactly the "confidently
   wrong, presented authoritatively" failure mode this project's own
   evaluation rubric treats as worse than an honest, disclosed gap
   (`L-020`).
2. **Testing a relation-detection hypothesis against a project's real,
   already-published structured data (a compat-register YAML) is a
   stronger validation than testing against an invented fixture** — the
   `match_compat_register_evidence` demonstration's credibility comes
   specifically from matching real, independently-authored citations,
   not a fixture built to match.
3. **A phase whose own deliverable is "evidence for a later decision"
   should treat a defect in its own evidence-gathering process as
   first-class evidence too** — this phase's most durable output may
   turn out to be `L-020`'s general lesson about extraction-pipeline
   self-validation, not the narrower `tag:`-specific verdict.

## Process-improvement feedback

None new for the agent-led workflow itself — `context-evaluator` and
`reference-project-tester` both worked exactly as their briefs describe,
including `context-evaluator` correctly refusing to soften a FAIL it
found real evidence for. Worth naming as a positive confirmation of the
existing independence discipline (`CLAUDE.md` §8: "evaluation agents...
never repair what they are judging"), not a new rule.

## Candidate learnings filed

- **`L-020`** — content-hash pinning vs. boundary-correctness, filed
  `candidate`.
- **`CG-004`** — `mentions_artifact` cannot relate two `spec_doc`
  artifacts, filed `candidate`.
- **`CG-005`** — `origin` enum has no externally-pinned-reference value,
  filed `candidate`.
- **`OBS-007`/`OBS-008`/`OBS-009`** — filed, `resolved`/`recorded` as
  applicable (see `planning/context-observations/inbox.md`).

## Where we're going

- **Next: unclear, genuinely, same as after Phases 52/53.** This phase
  *did* produce real evidence toward the Stage D-vs-Stage-F/G question
  (unlike 52/53, which were explicitly orthogonal to it) — but the
  evidence is mixed, not a clean mandate either way. Two independently
  small, precedented fixes (`CG-004`'s `name` population, `CG-005`'s
  `origin` value) are each fundable on their own narrow terms regardless
  of the broader Stage E ontology question. The YAML-evidence-matching
  fallback is promising but under-evidenced (tested against only one
  real feature family, `date:`/`tag:`) — not yet ready to generalise.
- **Trajectory:** Phase 55/GATE DD now has real, specific evidence to
  weigh (not a hypothetical), including one genuinely humbling data
  point (`L-020`) about how easy it is for a pinned-provenance mechanism
  to still be wrong in a way that looks more trustworthy than it is.

## Time / cost note

Single session. No AI enrichment spend — the ingestion pipeline itself
makes no AI calls (mechanical extraction only); one real `WebFetch` call
(the baseline's manual fetch) and one real `context-evaluator`/
`reference-project-tester` agent dispatch each. `pytest` for the new
experiment module: 13 passed (outside the main `src/codecompass/` suite,
which is unaffected — no `src/` change this phase). `ruff check .` clean
across the new files. `check_user_docs.py --strict` clean throughout.
