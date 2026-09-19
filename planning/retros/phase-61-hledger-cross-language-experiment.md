# Phase 61 retro — hledger cross-language experiment

- **Date:** 2026-09-19
- **Commit(s):** `9f8b510` (the `HaskellAdapter.repository_url()` fix); this phase's own closeout commit, see `planning/CONTEXT.md`
- **Agents used:** two independent `general-purpose` dispatches (baseline, treatment — deliberately not `context-evaluator`/`reference-project-tester` roles, since these needed to be genuinely fresh agents under test, matching Phase 54b's own precedent), `context-evaluator` (independent ground-truth verification, including a real fixture built and run live against both the pinned `hledger` binary and Ledgerkit's own CLI), `reference-project-tester` (friction filing against the real sync output), `knowledge-curator` (triage)

## Where we are

Stage F (`decisions/0056`), gated on nothing. Phase 60 shipped and
independently validated the first external CodeCompass adapter. Phase
61 is Stage F's second phase: does a real, working Haskell adapter
actually help an agent do the cross-language behavioural-equivalence
task Phase 54b's own plan named as this phase's real purpose, and does
it do better than Phase 54b's own curated-document-layer result?

## Goal

Re-run Phase 54b's own `depth:`/`--depth` behavioural-reconstruction
question using real Haskell-side structural information (the Phase 60
adapter) instead of the curated document layer, and separately test
whether CodeCompass helps an agent relate that understanding to
Ledgerkit's own Python reimplementation as the same behavioural concept
in two languages — scored two-part-plus-overall, with symmetric
baseline/treatment inputs and a measured (not asserted) rediscovery
comparison, per this phase's own amended methodology.

## Scope delivered vs planned

Delivered exactly as the twice-amended plan scoped:

- Fixed the one required prerequisite: `HaskellAdapter.repository_url()`
  now sets `RepositoryLocation.subdirectory` for a monorepo member (two
  new fixture tests; the existing live smoke test's own assertion
  updated to match). Full suite: 615 passed (2 pre-existing, unrelated
  skips), `ruff`/`check_user_docs.py --strict` clean.
- Tracked both `hledger-lib` and `hledger` (not `hledger-lib` alone) as
  real vendors in a disposable Ledgerkit scratch copy
  (`ledgerkit-scratch-61`), via a real `codecompass sync --yes --budget
  0`. Confirmed live: `depends_on_edges` shows a real `hledger →
  hledger-lib` edge, with zero new code, exactly as the plan's own §1
  claimed.
- Symmetry protocol executed and verified, not merely designed: both
  hledger and Ledgerkit's pinned commits confirmed unchanged since Phase
  54b; a real, live-confirmed gap (`resolve_and_clone` has no
  commit-pinning support, so the network-cloned vendor source landed on
  the *current* upstream HEAD, not the pinned tag) closed via a manual
  `git checkout <sha>` in both vendor clones, with `FILETREE.md`/
  `filetree.json` regenerated afterward to match (a real, disclosed
  extra step the plan's own §2.1a anticipated in principle but didn't
  spell out in this much operational detail — see "What didn't work").
  Byte-for-byte `diff` confirmed the treatment's re-pinned vendor source
  and the baseline's real local checkout were identical afterward.
- Two fresh, independent agent dispatches on the identical, two-part
  task, each producing a required file-read log.
- `context-evaluator`'s independent, three-verdict-block evaluation
  (`planning/reference-projects/ledgerkit/03-hledger-cross-language-evaluation.md`),
  including a real, live-run fixture that settled the one substantive
  factual disagreement between the two agent reports.
- `reference-project-tester`'s friction pass over the real sync output,
  filing two real observations (`OBS-015`, `OBS-016`).
- Three candidate learnings filed (`L-026`, `L-027`, `L-028`), routed to
  `knowledge-curator`.

**One deviation, disclosed, not a shortfall**: the plan's own
Verification wording claimed the §4 fix would make the raw
`vendor/hledger-lib/src/` directory itself contain only `hledger-lib`'s
own files. This is not what `resolve_and_clone` does or has ever done
(confirmed: its own docstring says `subdirectory` only changes the
*returned* `tree_root` value, never prunes the raw clone) — a real
planning-time overclaim, caught by `reference-project-tester`, not by
the lead's own earlier verification (which checked `FILETREE.md`, the
actually-correct, actually-relevant artifact, and stopped there without
also checking the plan's own literal words against the raw directory).
See "What didn't work."

## What was achieved

A real, working, second Haskell vendor coexisting with the first in one
project, with correct cross-vendor dependency edges, for zero new
`src/codecompass` code beyond the one real bug fix this phase needed.
A real, empirically-grounded answer to Phase 61's own two central
questions:

1. **Part 1 (does real structural information beat the document layer):
   marginally yes on verdict, no on advantage.** Treatment reached a
   full PASS (Phase 54b's own treatment got PASS WITH GAPS, missing
   `Stats.hs` entirely) — but `context-evaluator` traced this
   improvement to "the right file is now physically present in the
   vendor clone" (this phase's own scope decision to track `hledger` as
   well as `hledger-lib`), not to anything the generated `CLAUDE.md`/
   `DEPTREE.md` explained. Context advantage: **LOW**, same as Phase
   54b's own result, for a different underlying reason.
2. **Part 2 (does it help cross-language recognition): no, not
   materially.** Ledgerkit isn't a tracked vendor, so no generated
   digest was ever in play for this half at all — confirmed both agents
   read the same raw source. Context advantage: **effectively NULL**.

**Outcome shape (b)** — helped Part 1 navigation, marginally; did not
help Part 2 cross-language recognition — exactly the shape this phase's
own amendment (§2.6) was written to make legible, and it is what
actually occurred. Overall: **PASS WITH GAPS, LOW**.

**Rediscovery comparison: no measurable reduction.** Treatment read
essentially the same ~14 raw source files baseline did, *plus* three
generated artifacts, one of which (`vendor/hledger/CLAUDE.md`) it
itself disclosed as contributing nothing to Part 1's actual question.

**A real, previously-unrecorded Ledgerkit correctness gap was found and
independently, empirically confirmed**: `ledgerkit.reports.stats()`
computes its commodity count/list without the same
`account_excluded_by_depth` check its own account count/list uses,
under-excluding relative to hledger's real `stats --depth N` (confirmed
live by `context-evaluator` against both the real pinned `hledger`
1.52.4 binary and Ledgerkit's own CLI, with a real fixture journal built
for the purpose). This gap existed undetected in Ledgerkit's own
internal compatibility record (`LK-COMPAT-QUERY-DEPTH-STATS-001.yaml`,
marked `status: verified`, which only ever checked the Accounts field).
This finding belongs to Ledgerkit's own project, not CodeCompass's —
recorded here for completeness and because it's genuinely interesting,
not acted on (no fix was made to the real Ledgerkit repository; only a
disposable scratch copy was ever touched).

## What worked

- **Real, live empirical verification settled a genuine disagreement
  the two static reports alone could not.** `context-evaluator` built
  a real fixture and ran both the pinned `hledger` binary and Ledgerkit's
  CLI live to confirm the commodity-count divergence, rather than
  trusting either agent's own (correctly hedged, in treatment's case)
  static-source claim. This is exactly the "inspect the target directly,
  never trust the report" discipline the evaluator role exists for,
  and it caught something a purely-static comparison would have left
  as "plausible but unconfirmed."
- **The symmetry protocol's own real execution surfaced a real,
  disclosed methodological risk exactly as predicted** — the
  `resolve_and_clone`-has-no-commit-pinning gap was not hypothetical;
  the network clone really did land on a different commit than the
  pinned tag, and would have silently broken the experiment's own
  "only intended difference is CodeCompass's context" invariant if the
  amendment hadn't specified checking for it.
- **`context-evaluator`'s own explicit check for agent-diligence
  confounds** (Part 2's real divergence traced to "both agents had
  equal raw access; one read more carefully," not to CodeCompass)
  avoided a real, easy evaluation error — crediting a tool for an
  outcome it didn't cause. Filed as `L-027`, a genuinely new
  methodological lesson for future single-trial reference-project
  comparisons.

## What didn't work

- **The plan's own Verification wording overclaimed what the §4 fix
  produces at the raw-filesystem level** (see "Scope delivered vs
  planned"). The lead's own earlier live check (during implementation)
  verified `FILETREE.md`/the symbol index/`filetree.json` — the actually
  load-bearing artifacts — and stopped there, without re-reading the
  plan's own literal words closely enough to notice they named the raw
  `vendor/<name>/src/` directory specifically. `reference-project-tester`
  caught this independently. No functional consequence (the real,
  correct behaviour was already achieved and already verified via the
  right artifacts) — but a real gap between what the plan claimed and
  what was actually checked, worth naming plainly rather than quietly
  correcting after the fact.
- **The symmetry protocol's own "check and re-pin" step needed an
  unplanned follow-up** (regenerating `FILETREE.md`/`filetree.json`
  after the manual `git checkout`, since those were rendered from the
  pre-checkout, wrong-commit clone) that the plan's own §2.1a described
  in principle ("verified via `git rev-parse HEAD` equality... before
  either agent is dispatched") but didn't spell out needed a *second*
  regeneration step beyond the checkout itself. Caught and fixed before
  either agent was dispatched, so it didn't affect either report's own
  validity — but cost real extra implementation time not accounted for
  in the plan's own sequencing.

## Lessons learnt

A methodology amendment that adds real rigor (symmetric inputs, a
required file-read log, two-part scoring) earns its own keep by
surfacing exactly the kind of finding it was designed to catch — but
rigor at the *design* level doesn't substitute for rigor at the
*execution-checking* level: the raw-clone-scoping overclaim and the
FILETREE-regeneration gap were both real gaps between the amended
plan's own careful design and what the lead actually verified during
implementation, not failures of the amendment itself. The broader
lesson (`L-027`): a two-agent, single-trial comparison is a real,
useful signal but not a controlled experiment — any observed quality
delta between conditions needs its own causal check (do both conditions
actually have access to the decisive evidence?) before being attributed
to the variable under test, exactly the check `context-evaluator`
performed here and that a less careful evaluation could easily have
skipped.

## Process-improvement feedback

Dispatching `reference-project-tester` and `context-evaluator` in
parallel (rather than sequentially) worked well here — they inspect
genuinely disjoint material (real sync artifacts/database vs. the two
agent reports/live ground truth) and produced complementary, not
redundant, findings (`OBS-015`/`OBS-016` on the generated-artifact side;
the commodity-divergence finding and the agent-diligence-confound check
on the evaluation side). No process friction to report otherwise.

## Candidate learnings filed

`L-026` (adapter-generated digests answer "what exists," not "what does
it do" — third independent occurrence), `L-027` (single-trial
baseline/treatment comparisons can't cleanly separate tool contribution
from agent diligence), `L-028` (`resolve_and_clone`'s `subdirectory`
scopes the rendered view, not the raw clone — a documentation gap in
this phase's own plan, not a new code defect) — all in
`planning/learnings/inbox.md`, triaged by `knowledge-curator`.
`OBS-015`/`OBS-016` in `planning/context-observations/inbox.md`,
filed by `reference-project-tester`.

## Where we're going

Phase 62 (adapter-interface consolidation) now has a second real
adapter-interface data point beyond Phase 60's own single-vendor
validation: coexisting sibling vendors sharing one repository URL work
correctly for digests/dependency edges, at the cost of a real, disclosed
duplicated-clone inefficiency (already named in this phase's own review
gate). `CG-008` (`_collect_vendor_symbols`'s own gap) remains untouched
and unaffected by this phase's own result — Part 1's LOW rating traces
to the generated digest's own real content limits (`L-026`), not to the
graph's own missing symbol table, so fixing `CG-008` would not by itself
have changed this phase's own Part 1 result. **This phase does not
resolve GATE DD and does not complete or bypass Phases 55-59** — both
remain exactly as open as before. This phase's own real findings (a
working two-vendor monorepo case; a genuine, if modest, navigational
LOW advantage; a null cross-language advantage; a real methodological
lesson about single-trial comparisons) are additional evidence for
GATE DD's eventual decision and for how future reference-project
evaluations should be designed, not a substitute for either.

## Time / cost note

One extended session. No AI API spend (`--budget 0` throughout; agent
dispatches are Claude Code subagents, not billed Anthropic-API
enrichment calls). Real toolchain cost: the `hledger` package's own
export-scan took noticeably longer than `hledger-lib`'s did in Phase 60
(more command modules to two-pass-scan, and — noticed live via `ps
aux`, not investigated further — `_analyze()` appears to re-spawn a
full adapter subprocess per `EcosystemAdapter` method call rather than
reusing one `analyze_project` result across `dependency_tree()`/
`readme_and_api_surface()`, plausibly Phase 62's own kind of finding,
not filed as a candidate here since it wasn't independently confirmed
under time pressure this session).
