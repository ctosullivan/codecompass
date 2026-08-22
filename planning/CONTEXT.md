# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 18: `undo` command — done.** Phases 0-17 remain `done`. Executing
MVP (v0.2) per `planning/v0.2-implementation-execution-plan.md`.

## What was just completed

Implemented `planning/phase-18-undo-command.md`: new `codecompass undo
[--yes] [--dry-run]` in `cli.py`. Two enumeration strategies — graph-
backed (every `doc_artifacts` row tagged `codecompass_tool`/
`codecompass_vendor`, never `third_party`, resolved to real paths, plus
every tracked vendor's `vendor/<name>/` dir) when `context-graph.db`
exists, a pattern-based fallback (exact `skill.py`/`commands.py` naming
conventions) when it doesn't. Root `CLAUDE.md`'s routing-table marker
block is stripped in place (`index.py`'s marker regex, run in reverse),
never the whole file. Never runs a git command. New ADR `decisions/0036`.

Two real findings, both correctly handled: (1) a Windows-specific bug —
a naive `shutil.rmtree(..., ignore_errors=True)` silently left a cloned
vendor's read-only `.git/objects/pack/*` files behind while still
reporting success; fixed with `_rmtree_best_effort` (clears the
read-only bit, retries, reports actual leftovers instead of claiming
false success) — found and fixed within this phase's own scope. (2) **A
real, pre-existing ordering gap from Phase 15, found but correctly left
unfixed** (out of this phase's scope) — `_bootstrap`/`sync` rebuild the
graph and regenerate the tool Skill/routing table *before*
`_maybe_run_enrichment` runs, so a vendor's newly-written per-vendor
Skill/`.mdc` (and its `Enriched: yes` status) isn't reflected anywhere
generated until the *next* whole-project sync. Reproduced directly:
`undo --dry-run` immediately after a vendor's first-ever enrichment omits
its brand-new Skill directory. Self-corrects on the next sync — not
data-destructive, just one-run-stale. See "Still outstanding" below.

Verified independently: `pytest` 366 passed/1 skipped, `ruff check .`
clean. Read `cli.py`'s full `undo` implementation and `decisions/0036`
directly — confirmed the `origin` filter is exact (not a broader `LIKE`
pattern), confirmed `_dedupe_contained` correctly avoids double-deleting
nested paths, confirmed Skill directories (not just `SKILL.md`) are
targeted so `references/` subdirectories aren't orphaned.

## Next concrete step

Implement `planning/phase-19-chat-demotion-and-governance-docs.md`
next — the last phase of MVP (v0.2): README/architecture rewritten
around the graph+Skills+`/discovery` as primary, chat framed as
secondary, `chat.py` itself unchanged. Mostly documentation. Once done,
mark all of phases 9-19 `done` in `planning/ROADMAP.md` and note that
MVP (v0.2)'s own tag remains a separate, not-yet-made decision
(`decisions/0030`), same posture `decisions/0022` already established
for `v0.1`.

**Still outstanding, not a blocker but worth remembering:**
- **From Phase 18**: the graph/enrichment ordering gap described above —
  `_maybe_run_enrichment` runs after the graph rebuild and routing-table/
  tool-Skill regen it should ideally precede (or be followed by a second,
  cheap catch-up pass). Affects `undo`'s freshness immediately after a
  vendor's first enrichment, `query skills`'s freshness, and the routing
  table's `Enriched` column's freshness, all the same way. Worth a small,
  deliberate fix (likely: re-run the graph rebuild + index/tool-Skill
  regen after `_maybe_run_enrichment`, not before) — not attempted at the
  tail of this arc, deliberately.
- **From Phase 17**: `write_tool_skill` (and now `write_discovery_command`)
  only fire at two points (`_bootstrap`, `index()`) — `sync()`'s
  whole-project branch never regenerates either artifact. `codecompass
  query skills` hard-filters to `kind='skill'`, so `/discovery`'s own
  `slash_command`-kind graph row never surfaces through it (confirmed
  present via direct `sqlite3` read). Neither blocks anything.
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter against real
  `cargo metadata` output and a real crate — currently entirely
  unverified. Relevant to Phase 13's universal cloning.
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `enrichment.py` (batched calls) and `chat.py` have never been run
  against the real Anthropic API in this environment — a human must do
  this manually at least once before trusting output quality
  (`decisions/0016`). Phase 15's manual verification step is where this
  first becomes reachable end-to-end; not yet actually exercised against
  a live key as of this session.
- `staleness.py`'s version parser has no real PEP 440/semver correctness
  — flag if it misclassifies a real-world version string.
- A formal trigger-accuracy evaluation harness for per-vendor Skills
  (`decisions/0013`) remains outstanding.
- Cursor `.mdc` export has no `globs` field — documented future
  refinement, not implemented.
- Whether/when to cut the `v0.1` tag is a separate, not-yet-made decision
  (`decisions/0022`); `v0.2`'s tag is not before Phase 19 is `done`
  (`decisions/0030`).
- None of this repo's own four tracked vendors have ever been through a
  real Phase B enrichment run (no vendor's `CLAUDE.md` has a Description
  section yet). Three of them (`rich`, `typer`, `anthropic`) are
  genuinely imported by `src/codecompass/` and confirmed as real
  `uses_edges` (Phase 11's verification) — the moment bare `codecompass`
  or `sync` runs against this repo with a real `ANTHROPIC_API_KEY` and
  `--yes` (or a confirmed prompt), those three become real
  `enrichment_candidates`. `pipdeptree` is invoked only as a subprocess,
  never imported, so it correctly never becomes a candidate.
- `vendor/` is currently absent from this checkout (gitignored, freely
  regeneratable — `decisions/0010`; not a repeat of an earlier session's
  file-loss incident). `vendor.toml` (tracked) is intact. Running
  `codecompass sync` regenerates everything.
