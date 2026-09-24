# Phase 71 retro — Post-v1 documentation refresh

- **Date:** 2026-09-24 to 2026-09-25.
- **Commit(s):** `657dceb` (plan), `4bc7c1d` (README.md rewrite,
  ROADMAP.md restructure, CONTEXT.md reduction), `0e36123` (independent
  fork-review findings fixed), `396118a` (per-phase drift audit findings
  fixed + report), `40fc074` (domain-corpus staleness reconciliation).
- **Agents used:** a fork (independent consistency review), a
  `docs-reconstructor` per-phase drift audit, `domain-skeptic` (domain-
  corpus freshness reconciliation, `L-040`).

## Where we are

First post-v1 phase, direct user request: `README.md`, `ROADMAP.md`,
`CONTEXT.md`, and the rest of the current-facing doc surface still
described a pre-release/in-progress project after `v1.0.0` shipped at
Phase 70.

## Goal

Ground-up rewrite of current-facing documentation against verified
current behaviour: `README.md` (purpose, capabilities, architecture,
install/usage, ecosystems, evidence/provenance, limitations, realistic
v1 positioning), `ROADMAP.md` (concise current-state view replacing the
full historical table), `CONTEXT.md` (further reduced), plus a
consistency sweep of everything else current-facing — without rewriting
historical material (ADRs, retros, `docs/domain/`, `v1-redefinition/`).

## Scope delivered vs planned

Delivered as planned, with no scope amendments. `README.md` was
rewritten ground-up citing `architecture/`, `docs/`,
`planning/v1-closeout.md`, and `decisions/0048` rather than re-derived
from memory. `ROADMAP.md`'s 424-line phase-by-phase table (not 412, as
the plan estimated — corrected during the independent review) was
replaced with a ~113-line current-state summary, full history preserved
in `v1-closeout.md`, `v1-redefinition/roadmap.md`, and git. `CONTEXT.md`
was reduced again to `CLAUDE.md` §4's literal four fields. One
mechanical check (`check_readme_phase_count`) needed rewriting as a
direct, necessary consequence of the ROADMAP restructure removing the
row-table structure it scanned — judged in-scope (the phase's own
restructure caused the breakage) rather than an unrelated change, per
the user's own explicit instruction to avoid the latter.

## What was achieved

`README.md` now states project status accurately ("Released," not
"Pre-release"), adds an "Evidence & provenance" section and a
"Limitations" section (8 concrete, honestly-disclosed gaps) that did
not exist before, and positions the Ledgerkit validation result
accurately (PASS WITH GAPS / LOW advantage, not rounded up).
`ROADMAP.md` and `CONTEXT.md` no longer duplicate `v1-closeout.md`'s
own historical record. Two stale cross-references (`ai-docs/CLAUDE.md`,
`CONTRIBUTING.md`) describing `ROADMAP.md` as a "full phase table" were
caught and fixed by the per-phase drift audit. Two domain-corpus
citations that referenced the now-restructured `ROADMAP.md` and a test
this phase deleted were caught by the domain-freshness reconciliation
check and fixed in `docs/domain/concepts/connector.md` and
`invariant.md` (content unchanged, citations updated). Full `pytest`:
625 passed, 2 skipped, unchanged throughout.

## What worked

- **Self-review caught two real drafting errors before they landed.**
  A first README.md draft fabricated Ledgerkit's repo URL
  (`github.com/simonmichael/hledger`, a guess) instead of checking this
  project's own recorded evaluation files for the real one
  (`github.com/ctosullivan/ledgerkit`) — caught by grepping
  `planning/reference-projects/ledgerkit/*.md` before committing,
  per the standing rule never to fabricate URLs. A second draft
  overstated `symbol_enrichment`'s own provenance ("every enriched row
  records which model...") when that table is a known, disclosed gap
  (`L-031`) — caught on re-read before committing. Both are evidence the
  self-review step is doing real work, not a formality.
- **The domain-corpus freshness-reconciliation mechanism (`L-040`)
  caught a second real case** beyond the one it was originally written
  for at Phase 66 (`CONTEXT.md`/`EV-SKEP-003`) — this phase's own
  `ROADMAP.md` restructure and test deletion each broke a `docs/domain/`
  citation that had nothing to do with domain meaning. Both were
  content-preserving citation fixes, confirmed via `domain-skeptic`'s
  own direct `grep`/`git show` checks rather than assumed. The mechanism
  is now proven across two independent triggering phases, not a
  one-off.
- **Treating the mechanical-check breakage as an in-scope consequence,
  not an unrelated change**, matched the user's own explicit instruction
  from the prior (packaging-rename) request and this project's own
  established judgment calls at similar junctures — fixed with full new
  test coverage rather than either abandoning the check or padding
  `ROADMAP.md` with stale rows just to keep it passing.

## What didn't work

The plan's own §1.2 estimate of `ROADMAP.md`'s row-table size (412
lines) was off by 12 lines against the real pre-restructure count (424,
confirmed via `git show 4bc7c1d~1 | wc -l`) — caught by the independent
fork review, not by the lead's own drafting. A minor inaccuracy with no
real consequence (it only affected a line-count claim inside
`CONTEXT.md`'s own prose), but a reminder to verify exact figures
against a live command rather than an approximate earlier read when a
prose claim states a specific number.

## Lessons learnt

No new candidate learning beyond what's already covered by existing
practice: the self-review catches (fabricated URL, overstated
provenance) are exactly what the "independent review before committing"
step in this project's own workflow exists to catch, and they were
caught. The domain-freshness reconciliation mechanism's second
successful catch is confirmation of `L-040`'s own value, not a new
lesson. Left for `knowledge-curator`'s own independent triage rather
than the lead pre-deciding there's nothing to file.

## Process-improvement feedback

None beyond the lesson above.

## Candidate learnings filed

None directly by the lead — deliberately left for `knowledge-curator`'s
own independent assessment of whether the self-review catches or the
domain-freshness mechanism's second confirmation warrant a promoted
entry (e.g., a `project-rule` reinforcing "verify a specific numeric
claim against a live command before stating it," or simply confirming
existing rules already cover this and nothing new is needed).

## Where we're going

Post-v1 development continues under the same agent-led model; no
milestone-group implications (`decisions/0048`'s group closed at Phase
70). Deferred items and their revisit triggers remain unchanged:
GATE DD/Stage E, Phases 24/25/48/50 (`ROADMAP.md`'s own "Deferred /
not-funded" table).

## Time / cost note

One fork dispatch (independent consistency review, required a retry
after a session rate-limit reset), one `docs-reconstructor` dispatch
(per-phase drift audit), one `domain-skeptic` dispatch (freshness
reconciliation, 2 candidates confirmed and fixed).
