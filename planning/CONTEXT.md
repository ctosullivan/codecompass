# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 15: CLI rewire — done.** Phases 0-14 remain `done`. Executing
MVP (v0.2) per `planning/v0.2-implementation-execution-plan.md`: one
implementation subagent per phase, independently re-verified, one commit
per phase, strictly in order.

## What was just completed

Implemented `planning/phase-15-cli-rewire.md` — the integration phase,
the largest in this arc. `cli.py`: `promote` removed entirely; bare
`codecompass` and whole-project `sync` both gain `--yes`/`--budget` and
auto-trigger Phase B (`enrichment.select_candidates` →
disclose/confirm → `run_enrichment_batches`/`apply_results`) right after
Phase A's free work; new `query {vendors|vendor|symbol|skills}` command
group (Rich tables or `--json`, graceful "run sync first" note if no
graph exists); `check` gains report-only coverage-gap sections
(confirmed **`--strict`'s exit code is untouched** — still governed by
version-drift severity alone, verified directly in the diff, not just
by description). `index.py`/`skill.py` migrated from `Depth`-keyed to
graph-derived `has_enrichment` status (new `graph.has_enrichment`), both
using a genuine read-only SQLite connection rather than `graph.open_graph`
— correctly reasoned that `open_graph` creates the file and issues
schema DDL, which would violate `index`'s own "must stay cheap and
side-effect-free" documented design principle.

**A second real, high-stakes bug was caught — this time by the
implementing subagent itself, during its own end-to-end testing, not by
orchestrator review**: `usage.py`'s project-source prune set didn't
exclude `vendor/` — but since Phase 13, every tracked vendor's own
upstream source clones into `vendor/<name>/src/` inside that same walk.
A vendor's own source very often self-references its own package name,
which registered as false-positive "the project uses this vendor"
evidence for nearly every vendor on every run — silently defeating the
entire "usage-driven, not everything" premise this whole rework is built
on (`decisions/0031`). Fixed by adding `"vendor"` to
`_PROJECT_PRUNE_DIR_NAMES`, with a regression test. Also fixed in
passing: `chat.py`'s "no grounded description yet" hint still literally
said `` `codecompass promote {name}` `` (a command this phase deletes) —
reworded to point at `sync`.

Verified independently: `pytest` 361 passed/1 skipped, `ruff check .`
clean, `git diff --stat` matches. Read the full `cli.py`/`index.py`/
`skill.py`/`graph.py`/`chat.py`/`usage.py` diffs directly (not just test
output) given this phase's size and the Phase 13 lesson about green
tests not catching everything — confirmed the `--strict` exit-code
preservation, the graph connection lifecycle (sequential opens/closes,
no concurrency issue), and the vendor-prune fix's regression test
firsthand.

## Next concrete step

Implement `planning/phase-16-retire-depth.md` next — now safe: `core.py`/
`config.py`/`discovery.py` finally lose `Depth`/`VendorConfig.depth`,
since Phase 15 removed every remaining behavioral consumer. Same
pattern: dispatch, re-verify independently (read the diff), doc-sync,
commit, push. Then 17 through 19, strictly in that order.

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
