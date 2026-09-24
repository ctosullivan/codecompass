# Domain-corpus freshness reconciliation — Phase 71

`domain-skeptic` dispatch, triggered by Phase 71's own per-phase drift
audit (`planning/retros/_drift-audit-phase-71.md` §5), which surfaced two
domain-claim staleness candidates in the approved `docs/domain/` corpus.
Both are narrow, mechanical citation-freshness checks against an
already-approved corpus, not new investigation into what any concept
*means* — neither turned out to be a genuine ambiguity, so nothing here
is escalated to the user.

## What I checked

1. **`docs/domain/concepts/connector.md`'s Definition section, item 1**
   (its citation list of planning documents that list "connector" purely
   as a research-candidate term) — read the current page in full,
   `grep -ni "connector" planning/ROADMAP.md` directly, `git show
   9ce200f:planning/ROADMAP.md | grep -n connector` to find the original
   source of the citation, re-ran the same grep against the other five
   files the page currently cites, and re-ran the page's own
   repository-wide grep (from `EV-ADPT-004`) to confirm its central claim
   is unaffected.
2. **`docs/domain/concepts/invariant.md`'s "Example" section** (its
   citation of a specific test as `L-001`'s landed example) — read the
   current page in full, `grep -n` for the cited class and method in
   `tests/test_check_user_docs.py`, read the full current
   `TestReadmePhaseCount` class, `git show
   c22d8e4:tests/test_check_user_docs.py` to confirm the cited test
   existed with that exact name at the commit `L-001` cites, and `git
   show 4bc7c1d -- tests/test_check_user_docs.py` to see the exact diff
   that removed it and what replaced it.

## What I resolved myself

### Finding 1 — `connector.md`'s `planning/ROADMAP.md` citation is stale (confirmed)

`connector.md`'s Definition section item 1 lists six planning documents
as all currently listing "connector" purely as a research-candidate term:
`decisions/0060-scope-plan-domain-design-implement-methodology.md`,
`planning/phase-63d-domain-reconstruction.md`,
`planning/v1-redefinition/development-methodology.md`,
`planning/v1-redefinition/roadmap.md`, `planning/ROADMAP.md`,
`CHANGELOG.md`.

Verified directly: `planning/ROADMAP.md` no longer contains the string
"connector" anywhere (`grep -ni "connector" planning/ROADMAP.md` — no
output, exit 1). The original citation traced to the old Phase 63D row
(`git show 9ce200f:planning/ROADMAP.md`, line 352), which Phase 71's
restructure deleted along with the entire 424-line phase-by-phase table
(replaced with a 113-line summary). The other five files in the list
still contain "connector" in the same usage
(`decisions/0060-...md:44`, `planning/phase-63d-domain-
reconstruction.md:48,194`, `planning/v1-redefinition/
development-methodology.md:75`, `planning/v1-redefinition/
roadmap.md:1561`, `CHANGELOG.md:120,210`). The page's central,
substantive claim ("'Connector' is not a real, distinct CodeCompass
concept") rests on `EV-ADPT-004`'s own repository-wide grep of `src/`,
`docs/`, `architecture/`, `ai-docs/`, `decisions/`, and `tests/`, which I
re-ran in full and which is entirely unaffected — this is a stale
citation, not a domain-meaning change.

This is the **second recurrence of the exact same fragility class**
`EV-SKEP-003`/`OBS-SKEP-004` already documented at Phase 66 for
`planning/CONTEXT.md`'s rewrite. `connector.md`'s illustrative citation
list depends on the live content of fast-moving planning documents that
this project's own post-v1 process keeps restructuring.

**New evidence recorded**: `planning/knowledge/codecompass-domain/
OBS-SKEP-005.yaml` (the grep/git-show checks), `planning/knowledge/
codecompass-domain/EV-SKEP-004.yaml` (what it shows, and the exact
correction needed).

**Exact correction needed** (for the lead to apply — I do not write to
`docs/domain/`): in `docs/domain/concepts/connector.md`, Definition
section item 1, remove `` `planning/ROADMAP.md`, `` from the six-file
list (leaving five), and extend the existing parenthetical that already
covers `planning/CONTEXT.md`'s identical Phase 66 breakage to also cover
this one. Concretely, replace:

```
   `decisions/0060-scope-plan-domain-design-implement-methodology.md`,
   `planning/phase-63d-domain-reconstruction.md`,
   `planning/v1-redefinition/development-methodology.md`,
   `planning/v1-redefinition/roadmap.md`, `planning/ROADMAP.md`,
   `CHANGELOG.md` — every one of these lists "connector" alongside
   "adapter, protocol, reference, decision, invariant" purely as a term
   *to research*, never as a term already defined or used for a
   mechanism. (`planning/CONTEXT.md` also listed it at the time of this
   corpus's own approval, but no longer does — Phase 66 rewrote that
   file into a current-only document per `CLAUDE.md` §4, dropping its
   own historical phase-63D-planning narrative; verified 2026-09-24,
   `EV-SKEP-003`.)
```

with:

```
   `decisions/0060-scope-plan-domain-design-implement-methodology.md`,
   `planning/phase-63d-domain-reconstruction.md`,
   `planning/v1-redefinition/development-methodology.md`,
   `planning/v1-redefinition/roadmap.md`,
   `CHANGELOG.md` — every one of these lists "connector" alongside
   "adapter, protocol, reference, decision, invariant" purely as a term
   *to research*, never as a term already defined or used for a
   mechanism. (`planning/CONTEXT.md` also listed it at the time of this
   corpus's own approval, but no longer does — Phase 66 rewrote that
   file into a current-only document per `CLAUDE.md` §4, dropping its
   own historical phase-63D-planning narrative; verified 2026-09-24,
   `EV-SKEP-003`. `planning/ROADMAP.md` also listed it, via the old
   Phase 63D row, but no longer does — Phase 71 replaced the entire
   phase-by-phase table with a concise summary, dropping that row;
   verified 2026-09-25, `EV-SKEP-004`.)
```

I'd also flag to `context-researcher` (not a decision for me to make):
given this is the second time this exact citation list has gone stale
from an unrelated planning-document restructure, a more durable citation
form for this list — e.g. pinning to the Phase-63D-era git revision
rather than "current state of documents known to still be actively
restructured post-v1" — may be worth considering next time this page is
touched. This is a process suggestion, not a finding, and not something
I'm treating as blocking.

### Finding 2 — `invariant.md`'s cited example test no longer exists (confirmed)

`invariant.md`'s "Example" section cites `tests/
test_check_user_docs.py::TestReadmePhaseCount::
test_ignores_done_phases_in_redefined_v1_section` as `L-001`'s real,
landed example of an `invariant`-classified learning.

Verified directly: `TestReadmePhaseCount` still exists as a class
(`tests/test_check_user_docs.py:67`), but the cited method no longer
exists anywhere in the file — the class's current three methods are
`test_flags_mismatch`, `test_no_finding_when_consistent`, and a new
`test_flags_missing_roadmap_claim`. `git show
c22d8e4:tests/test_check_user_docs.py` confirms the cited test existed
with that exact name at the commit `L-001` cites. `git show 4bc7c1d --
tests/test_check_user_docs.py` shows Phase 71 deleted it outright: it
asserted that `done` rows under a "Redefined CodeCompass v1" heading
were excluded from the README's foundation phase-count scan — logic
that no longer exists, because Phase 71 rewrote
`check_readme_phase_count` to compare README's and ROADMAP's own
"phases 0-N" prose claims directly rather than scanning per-phase `done`
rows at all (ROADMAP.md no longer has per-phase rows in that form). The
replacement test, `test_flags_missing_roadmap_claim`, exercises
different behaviour entirely (a missing prose claim, not a done-phase
computation) and does not stand in for the deleted one.

This is a stale citation, not a domain-meaning change: `invariant.md`'s
substantive claim — that `L-001` is a real, promoted
`invariant`-classified learning that landed as a regression test,
matching sense (1) of the page's own three-sense definition — remains
true as a historical fact. `L-001` (`planning/learnings/promoted.md`)
records a real promotion event; the rule it encoded was real at the
time, and its regression-test form was later superseded when Phase 71
restructured the behaviour it protected. What's stale is purely
`invariant.md`'s own choice of a currently-inspectable code line to
point readers at.

**New evidence recorded**: `planning/knowledge/codecompass-domain/
OBS-SKEP-006.yaml` (the grep/git-show checks), `planning/knowledge/
codecompass-domain/EV-SKEP-005.yaml` (what it shows, and why the
replacement content is `context-researcher`'s call, not mine).

**Why I'm not naming a single mechanical replacement**: two live options
exist, and picking between them is synthesis work, not a citation swap:

- (a) Reword the Example to describe `L-001` as a *historical* promoted
  example — cite `planning/learnings/promoted.md`'s own `L-001` entry
  and note that its original regression test was later superseded by
  Phase 71's behavioural change, stating that fact rather than silently
  repointing to a different, unrelated test.
- (b) Find a currently-live `invariant`-classified `promoted.md` entry
  whose regression test still exists verbatim, and cite that instead.

Choosing between (a) and (b) — and, if (b), verifying every other
`promoted.md` `invariant`-classified entry's current test status — is
`context-researcher`'s own synthesis work per this role's write
boundary, not something I can resolve unilaterally with a single grep.
I'm naming this precisely as `context-researcher`'s next concrete step,
not escalating it to the user: it is a researchable fact-finding task
(which `promoted.md` entries still have live tests), not a genuine
product/domain ambiguity.

**Exact correction still needed** (for the lead to apply, after
`context-researcher` picks (a) or (b) and drafts replacement text): in
`docs/domain/concepts/invariant.md`, the "## Example" section
(currently lines 65-71), replace the stale test citation per whichever
of the two options `context-researcher` selects. I am not drafting the
replacement prose myself, per this role's own write boundary (a
Claim/Derivation-level judgement about what counts as the "right"
replacement example is `context-researcher`'s job, not mine).

## What I escalated

Nothing. Both candidates resolved to confirmed, evidenced stale
citations with either a fully mechanical fix (Finding 1) or a precisely
named next step for `context-researcher` (Finding 2) — neither is a
genuine product/domain ambiguity requiring the actual user/domain
owner's judgement.

## New records produced

- `planning/knowledge/codecompass-domain/OBS-SKEP-005.yaml`
- `planning/knowledge/codecompass-domain/EV-SKEP-004.yaml`
- `planning/knowledge/codecompass-domain/OBS-SKEP-006.yaml`
- `planning/knowledge/codecompass-domain/EV-SKEP-005.yaml`

All four validate clean against `scripts/check_knowledge_base.py`
(`check_knowledge_base: no findings`).
