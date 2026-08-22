# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**MVP (v0.2) is complete — all eleven phases (9-19) are `done`.**
Phases 0-8 (v0.1) were already `done`. `codecompass` now: renames
complete; auto-clones every tracked vendor; detects real project-source
usage; maps docs/skills/dependencies into a SQLite graph; auto-triggers
disclosed, confirmable batched AI enrichment for usage-proven vendors
only; exposes all of it via `codecompass query`, `/discovery`, and
generated Skills; can `undo` itself cleanly; and frames chat as a
secondary, unchanged tool rather than the product. `promote` and `Depth`
are fully retired. **The first real end-to-end run against a live
Anthropic API key has now happened** (against this repo itself, in a
local `.venv`) — see below.

## What was just completed

Two things, back to back: Phase 19 (docs-only, closing the MVP v0.2 arc)
and, immediately after, the first real end-to-end validation against a
live `ANTHROPIC_API_KEY` — an item that had sat in "still outstanding"
since Phase 15. Both real bugs that validation surfaced are now fixed,
not just logged.

**Phase 19** (`planning/phase-19-chat-demotion-and-governance-docs.md`):
`README.md`, `architecture/overview.md`, `docs/cli-reference.md`
corrected against the fully-built system — roughly a dozen stale
`promote`/`Depth`/pre-rework references found and fixed (full list in
`CHANGELOG.md`). Two more, found by the implementer but out of that
phase's named Files list, were small and safe enough to fix directly:
`architecture/overview.md`'s "Known footguns" section had two bullets
giving present-tense instructions to run a deleted `codecompass promote`
command; `discovery.py`'s `write_vendor_toml`/`rewrite_vendor_toml`
docstrings still described the retired `depth`/`promote` mechanics.

**Live validation** — ran `codecompass sync --yes` in a fresh local
`.venv` against this repo's own real `vendor.toml` (after cleaning up a
stale, broken `depcompass` editable install predating the Phase 9
rename). Real batched enrichment succeeded: one Anthropic API call
(~$0.02) correctly enriched exactly the three usage-proven vendors
(`rich`, `typer`, `anthropic`) and correctly skipped `pipdeptree`
(subprocess-only, never imported) — genuinely grounded output, verified
by reading `vendor/rich/CLAUDE.md`'s Description section and the
generated `codecompass-rich`/`-typer`/`-anthropic` Skills directly.

Two real bugs found and fixed on the spot, both now covered by
regression tests, neither caught by any test before because nothing
before this exercised a second real sync after a real clone/enrichment:
1. **`sync` crashed on any second run** once a vendor had been
   git-cloned — `source_resolution._git_clone`'s naive `shutil.rmtree`
   hit the same Windows read-only-packfile `PermissionError` `undo`
   (Phase 18) already had to solve. Fixed by promoting `undo`'s
   best-effort rmtree helper to `source_resolution.rmtree_best_effort`,
   shared by both callers instead of duplicated — `cli.py`'s local copy
   deleted.
2. **A vendor's `OVERVIEW.md` never appeared on its first-ever
   enrichment**, only from the next whole-project sync —
   `enrichment.apply_results` now writes it directly instead of relying
   on `sync_vendor`'s next-run catch-up. This was the same underlying
   "graph/enrichment ordering" class of gap already flagged after Phase
   18, now with a concrete second manifestation — see "Still outstanding"
   below for what of that gap remains.

Verified independently throughout: `pytest` 367 passed/1 skipped (up
from 366 — the new `OVERVIEW.md` regression test), `ruff check .` clean,
and the fixes re-confirmed against this repo's real state a second time
(`sync --yes` re-run: no crash, `OVERVIEW.md` present, Phase B correctly
skipped re-enrichment via its cache — no wasted spend).

## Next concrete step

**MVP (v0.2) is done.** No phase is currently in progress. Two decisions
remain genuinely open, both explicitly deferred rather than accidentally
skipped:

1. **Cutting the `v0.2` git tag and promoting `CHANGELOG.md`'s
   `[Unreleased]` section to a dated release** (`CLAUDE.md` §6,
   `decisions/0030`) — now *applicable* (all of phases 9-19 are `done`),
   but not yet decided or acted on, same posture `decisions/0022`
   established for `v0.1` (also still untagged). This is a user decision,
   not something to act on unilaterally.
2. **What comes after** — `planning/ROADMAP.md`'s Post-MVP table (phases
   20-22: project-root routing/rollup consuming the new graph, polish/
   PyPI publish, MCP server) is unstarted and unplanned in implementation
   detail. Whether/when to start Phase 20 is the next real decision point
   once (1) above is resolved, or independently of it.

**Still outstanding, not a blocker but worth remembering:**
- **The graph/enrichment ordering gap is now only *partially* resolved.**
  `OVERVIEW.md`'s piece is fixed (above). What remains: `_maybe_run_
  enrichment` still runs after the graph rebuild and routing-table/
  tool-Skill regen it arguably should precede (or be followed by a
  second, cheap catch-up pass) — so `undo`'s enumeration and the routing
  table's `Enriched` column still lag by one sync cycle immediately after
  a vendor's *first* enrichment (self-corrects on the next whole-project
  sync, not data-destructive). A natural candidate for the first real
  post-MVP session.
- `write_tool_skill`/`write_discovery_command` only fire at two points
  (`_bootstrap`, `index()`) — `sync()`'s whole-project branch never
  regenerates either. `codecompass query skills` hard-filters to
  `kind='skill'`, so `/discovery`'s own `slash_command`-kind graph row
  never surfaces through it. Neither blocks anything.
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter against real
  `cargo metadata` output and a real crate — currently entirely
  unverified.
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `chat.py` has still never been run against the real Anthropic API in
  this environment (`enrichment.py`'s batched path now has been, per
  above) — worth doing once, now that `vendor/rich/OVERVIEW.md` actually
  exists to ground a fuller `chat rich` session.
- `staleness.py`'s version parser has no real PEP 440/semver correctness.
- A formal trigger-accuracy evaluation harness for per-vendor Skills
  (`decisions/0013`) remains outstanding.
- Cursor `.mdc` export has no `globs` field — documented future
  refinement, not implemented.
- `vendor/` now exists in this checkout with real, enriched content
  (`rich`/`typer`/`anthropic` all have Description sections and
  `OVERVIEW.md`; `pipdeptree` is deliberately unenriched) — a live
  artifact of the validation run above, not a fixture. Still gitignored
  and freely regeneratable (`decisions/0010`) — don't treat its current
  presence as something that must be preserved.
- A local `.venv/` now exists at the project root (gitignored) with
  `codecompass` installed editable, for local testing outside whatever
  environment a given session happens to default to.
