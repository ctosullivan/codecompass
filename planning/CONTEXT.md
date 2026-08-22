# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 19: Chat demotion + governance docs — done. MVP (v0.2) is
complete — all eleven phases (9-19) are `done`.** Phases 0-8 (v0.1) were
already `done`. `codecompass` now: renames complete; auto-clones every
tracked vendor; detects real project-source usage; maps docs/skills/
dependencies into a SQLite graph; auto-triggers disclosed, confirmable
batched AI enrichment for usage-proven vendors only; exposes all of it
via `codecompass query`, `/discovery`, and generated Skills; can `undo`
itself cleanly; and frames chat as a secondary, unchanged tool rather
than the product. `promote` and `Depth` are fully retired.

## What was just completed

Implemented `planning/phase-19-chat-demotion-and-governance-docs.md` —
the arc's closing, docs-only phase. `README.md` rewritten around the new
primary workflow (bare `codecompass` → clone + disclosed usage-driven
enrichment → `codecompass query`/`/discovery`/generated Skills, `chat`
explicitly secondary). `architecture/overview.md`: opening summary,
"Chat REPL" (now framed per `decisions/0034`, with a historical pointer
to superseded `decisions/0012` — not edited, append-only), "Two
consumption modes", "Multi-tool export", "Staleness checking",
"Retrofitting to existing projects", and "Cost model" sections all
corrected against the fully-built system. `docs/cli-reference.md` given
a full read-through, not just a grep, for stale prose. `chat.py`/
`skill.py` module docstrings updated (no logic changes — confirmed via
the full test suite staying green).

Ten stale `promote`/`Depth`/pre-rework references were found and fixed
across `README.md`/`architecture/overview.md`/`docs/cli-reference.md` —
full list in `CHANGELOG.md`'s entry, not repeated here. **Two more found
by the implementer but correctly left unfixed as out-of-scope for this
phase's named Files list — I judged them small and safe enough to fix
directly myself, given this is the arc's last phase**: `architecture/
overview.md`'s "Known footguns" section had two bullets giving present-
tense instructions to run `codecompass promote` and describing `git` as
required "for `promote`" — both referencing a deleted command; corrected
to describe the current batched-enrichment/universal-cloning reality.
`discovery.py`'s `write_vendor_toml`/`rewrite_vendor_toml` docstrings
still said "everything at `depth = surface`" and described `promote`
persisting a depth change — corrected; `rewrite_vendor_toml` is now
documented as unused-but-kept (its only caller, `promote`, was retired
in Phase 15) rather than silently misleading about what calls it.

Verified independently: `pytest` 366 passed/1 skipped throughout (docs
phase, unaffected as expected; re-confirmed after my own supplementary
fixes too), `ruff check .` clean.

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
- The graph/enrichment ordering gap from Phase 15/18: `_maybe_run_enrichment`
  runs after the graph rebuild and routing-table/tool-Skill regen it
  should ideally precede (or be followed by a second, cheap catch-up
  pass). Affects `undo`'s freshness immediately after a vendor's first
  enrichment, `query skills`'s freshness, and the routing table's
  `Enriched` column's freshness, all the same way — self-corrects on the
  next whole-project sync, not data-destructive. Worth a small, deliberate
  fix; a natural candidate for the first real post-MVP session.
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
- **`enrichment.py`'s batched calls and `chat.py` have never been run
  against the real Anthropic API in this environment** — a human must do
  this manually at least once before trusting output quality
  (`decisions/0016`). This repo's own tracked vendors (`rich`, `typer`,
  `anthropic`) are genuinely used by `src/codecompass/` and confirmed as
  real `uses_edges` (Phase 11) — running bare `codecompass`/`sync` here
  with a real `ANTHROPIC_API_KEY` would be the first real end-to-end
  validation. Not yet done as of this session.
- `staleness.py`'s version parser has no real PEP 440/semver correctness.
- A formal trigger-accuracy evaluation harness for per-vendor Skills
  (`decisions/0013`) remains outstanding.
- Cursor `.mdc` export has no `globs` field — documented future
  refinement, not implemented.
- `vendor/` is currently absent from this checkout (gitignored, freely
  regeneratable — `decisions/0010`). `vendor.toml` (tracked) is intact.
  Running `codecompass sync` regenerates everything.
