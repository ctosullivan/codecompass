# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 16: Retire `Depth` — done.** Phases 0-15 remain `done`. Executing
MVP (v0.2) per `planning/v0.2-implementation-execution-plan.md`: one
implementation subagent per phase, independently re-verified, one commit
per phase, strictly in order.

## What was just completed

**This phase required a re-plan mid-stream — worth remembering the shape
of that, not just the outcome.** The first implementation attempt
correctly stopped without making changes: `Depth` was not actually fully
behaviorally inert after Phase 15 as the original plan assumed —
`sync.py`, `claude_md.py`, and `grounded_description.py` still gated real
behavior on it. Investigating why surfaced a real bug already on `main`
since Phase 15: a whole-project `sync` re-run silently erased Phase B's
enrichment content from `CLAUDE.md`, because `sync_vendor` rebuilt every
vendor's file from scratch via a digest that never carried enrichment
data, gated on a `Depth` value nothing sets anymore now that `promote` is
gone. Wrote `decisions/0035` and revised
`planning/phase-16-retire-depth.md` to fix this properly before
continuing — see that ADR for the full reasoning.

Implemented the revised plan: `sync_vendor` now looks up a vendor's
current enrichment from the context graph (read-only, gracefully skipped
if no `context-graph.db` exists) before building its `VendorDigest`, so a
from-scratch re-render reproduces existing enrichment instead of erasing
it — directly fixing the bug above, with a regression test that syncs
twice and confirms the Description section survives. `grounded_description.py`
and its test file are deleted (not orphaned) — `enrichment.py` fully
replaces its role. `claude_md._render_description_section`'s gate
simplified to pure `technical_description` truthiness (no more `Depth`
check, and no longer conflates a clone failure with a description
failure — `decisions/0035`'s reasoning). Then the originally-planned
mechanical removal: `Depth` enum deleted from `core.py`,
`VendorConfig` narrowed to `(name, ecosystem)`, `config.py` tolerates a
legacy `depth =` line silently, `discovery.py`/`cli.py` updated.

**Blast radius was much larger than either plan version's Files list**
(flagged explicitly by the implementer, not hidden): deleting `Depth`
broke `chat.py` (a real source bug — `config.depth.value` in the REPL's
banner line) and required mechanical `depth=`-kwarg removal across 14
test files never named in the plan. Fixed mechanically, not redesigned;
`sync_all`'s now-meaningless `budget` parameter (no AI call happens in
`sync_vendor`'s path anymore — the one remaining AI budget gate is
Phase B's, already in `cli.py`) and two tests whose premise depended on
it were removed as genuinely obsolete, confirmed by reading their
original content before agreeing they no longer test anything real.

Verified independently: `pytest` 340 passed/1 skipped (down from 361 —
`test_grounded_description.py`'s tests and the two obsolete budget tests
account for the reduction, confirmed deliberate not accidental), `ruff
check .` clean, `grep -rn "Depth\b"` returns zero hits in `src/` and only
a docstring + negative-assertion string in `tests/`. Read `sync.py`'s,
`cli.py`'s, and `claude_md.py`'s full diffs directly and confirmed the
regression test for the bug fix does what it claims (syncs an enriched
vendor twice, asserts the Description section survives the second sync).

## Next concrete step

Implement `planning/phase-17-discovery-slash-command.md` next — new
`commands.py`, `/discovery` generated alongside the tool Skill at the
same trigger points. Same pattern: dispatch, re-verify independently
(read the diff), doc-sync, commit, push. Then 18-19, strictly in order.

**Still outstanding, not a blocker but worth remembering:**
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter against real
  `cargo metadata` output and a real crate — currently entirely
  unverified. Relevant to Phase 13's universal cloning.
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `grounded_description.py`/`chat.py` have never been run against the
  real Anthropic API in this environment — a human must do this manually
  at least once, specifically against Phase 14's *batched* call shape,
  before trusting output quality (`decisions/0016`). Phase 15's manual
  verification step is the first point this becomes reachable end-to-end.
- `staleness.py`'s version parser has no real PEP 440/semver correctness
  — flag if it misclassifies a real-world version string.
- A formal trigger-accuracy evaluation harness for per-vendor Skills
  (`decisions/0013`) remains outstanding.
- Cursor `.mdc` export has no `globs` field — documented future
  refinement, not implemented.
- Whether/when to cut the `v0.1` tag is a separate, not-yet-made decision
  (`decisions/0022`); `v0.2`'s tag is not before Phase 19 is `done`
  (`decisions/0030`).
- This repo's own `rich` vendor never got its `depth = full`
  promotion/per-vendor Skill regenerated after an earlier session's
  file-loss incident (fully resolved otherwise, see git history around
  commit `f2f92bd` if the full account is ever needed) — harmless for
  phases 10-13's purposes, becomes relevant once Phase 14/15's manual
  enrichment verification step needs a real usage-proven vendor to test
  against (any of the four currently-tracked ones will do, once this
  repo's own source actually imports them somewhere `usage.py` can see).
