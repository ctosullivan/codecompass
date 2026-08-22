# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 10: SQLite graph foundation — done.** All eight v0.1 MVP phases
(0-8) and Phase 9 (rename) remain `done`. Executing MVP (v0.2) per
`planning/v0.2-implementation-execution-plan.md`: one implementation
subagent per phase, independently re-verified, one commit per phase,
strictly in order.

## What was just completed

Implemented `planning/phase-10-sqlite-graph-foundation.md`: new
`src/codecompass/graph.py` — SQLite schema (9 tables + `meta`),
`init_schema`, `open_graph`, 9 row dataclasses, `rebuild_deterministic`,
7 query functions, `record_enrichment`/`record_symbol_enrichment`.
Library-only — not yet called from `sync.py`/`cli.py` (Phase 11+).

One real bug caught and fixed during implementation, not anticipated in
the plan: the schema's `ON DELETE CASCADE` from `vendors`/`symbols` to
`vendor_enrichment`/`symbol_enrichment` means a naive wipe-and-reinsert
of `vendors`/`symbols` on every rebuild would cascade-delete enrichment
too — directly contradicting the plan's "never touches enrichment"
requirement. Fixed by upserting vendors/symbols by natural key (name),
which preserves their integer id across a rebuild when the vendor/symbol
still exists, so referencing enrichment rows are never cascaded; only a
vendor/symbol genuinely absent from the new fixture is deleted (correctly
cascading its now-orphaned enrichment away). Locked in with dedicated
tests. `graph.py`'s module docstring and `rebuild_deterministic`'s
docstring both explain this.

Verified independently (not just the implementing subagent's own
report, per the execution plan): `pytest` 241 passed/1 skipped, `ruff
check .` clean, `git diff --stat` matches exactly the plan's Files list
(`.gitignore`, `architecture/overview.md`, new `graph.py` + `test_graph.py`
— nothing else touched), and a manual read of `graph.py` confirmed
parameterized queries throughout (the two internal f-string uses are over
fixed table/column-name literals, never external input).

## Next concrete step

Implement `planning/phase-11-project-source-usage-detection.md` next
(per `planning/v0.2-implementation-execution-plan.md`'s pattern: dispatch
one implementation subagent, re-verify independently, doc-sync, commit,
push). Then 12 through 19, strictly in that order — each phase's plan
assumes the previous ones' code already exists.

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
