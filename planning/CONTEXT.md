# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**MVP (v0.2) is complete (phases 9-19, all `done`). Phases 20-21 of the
path-to-v1.0 sequence are now also `done`.** Phase 22 (AI-enriched
cross-artifact relationships) is planned, not yet implemented; Phase 23
(Polish/PyPI publish, the release itself) has no plan file yet.
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

**One more real gap found by inspection, fixed inline, not deferred**:
the tool-level Skill (`.claude/skills/codecompass/SKILL.md`) listed
`codecompass query vendors|vendor|symbol|skills` as one bare line with
no per-subcommand guidance, no mention of `--json`, and no pointer to
`context-graph.db`'s schema for ad hoc queries — unlike `/discovery`'s
much richer content. `skill.py`'s `render_tool_skill` expanded to explain
each `query` subcommand, mention the raw-`sqlite3` escape hatch and the
schema table names, and point at `/discovery` itself. New test
(`test_render_tool_skill_explains_each_query_subcommand_and_escape_hatch`
in `tests/test_skill.py`); this repo's own `.claude/skills/codecompass/
SKILL.md` regenerated via `codecompass index` to match.

**Wrote `planning/phase-20-refresh-generated-artifacts-after-enrichment.md`**
— a proper future plan for the graph/enrichment ordering gap's remaining
piece (see "Still outstanding" below), rather than leaving it as a bare
`CONTEXT.md` note. `planning/ROADMAP.md`'s Post-MVP table updated: new
Phase 20 inserted, former 20/21/22 (routing/rollup, polish, MCP) shift to
21/22/23 — same clean-renumber pattern this project has used repeatedly,
noted inline in the table.

**Most recently: a path-to-v1.0 planning pass**, at explicit user request
("draft a plan to get to initial release," plus a new requirement to
recognize AI-enriched edges between dependency docs, spec docs, and custom
skills). Produced `planning/v1.0-initial-release-roadmap.md` (umbrella),
`planning/phase-21-spec-doc-detection-and-relationship-graph.md` (new —
mechanical detection of a project's own spec docs as graph nodes, linked
to dependency docs/skills via the existing mention-heuristic pattern), and
`planning/phase-22-ai-enriched-cross-artifact-relationships.md` (new — a
batched AI call summarizing *how* each Phase 21 edge relates, gated on
Phase 21's candidates only). `planning/ROADMAP.md`'s Post-MVP table
updated again: 21/22 inserted, Polish moved to 23 (proposed as the actual
release phase), routing/rollup and MCP pushed to 24/25 (proposed deferred
past v1.0 — not a locked decision, see "Next concrete step"). Planning
only — no code changed, nothing implemented.

## What was just completed (Phase 20)

Implemented per its plan file, via the same dispatch-then-independently-
verify pattern used throughout the v0.2 arc: new `cli._refresh_generated_
artifacts(project_root, configs)` (graph rebuild → routing table → tool
Skill → discovery command), called from a `try/finally` wrapped around
`_maybe_run_enrichment` in both `_bootstrap` and `sync`'s whole-project
branch — so it runs whether enrichment succeeds, is declined, has nothing
to do, or aborts on budget. `sync`'s whole-project branch now regenerates
these artifacts for the first time ever (previously only `_bootstrap`/
`index` did). Three new regression tests in `tests/test_cli.py`
(same-invocation post-enrichment freshness, zero-candidate `sync` still
refreshing, `undo --dry-run` seeing a just-written per-vendor Skill
immediately). `architecture/overview.md`'s "Retrofitting to existing
projects"/"Cost model" sections updated. Verified independently: `pytest`
371 passed/1 skipped (up from 367), `ruff check .` clean, diff read
directly against the plan (matches exactly, no scope drift).

## What was just completed (Phase 21)

Implemented per its plan file and verified independently (diff read
directly against the plan, not just green tests): new `spec_docs.py`
(`scan_spec_docs`, fixed default glob set, reuses `usage.
_PROJECT_PRUNE_DIR_NAMES` for exclusion rather than a third copy); new
`doc_mapping.build_doc_relations_edges` (spec-doc-outward word-boundary
scan against vendor names and other doc artifacts' `name` fields); new
`graph.py` table `doc_relations_edges` plus a generalized `doc_artifacts`
CHECK-constraint migration (`_migrate_doc_artifacts_constraints`,
`_SCHEMA_VERSION` "2"→"3", widens both `kind` +`'spec_doc'` and `origin`
+`'project'`); new `codecompass query relations <name>` (forward lookup
from a spec-doc path, reverse lookup from a vendor/Skill name); `check`
gained a "Spec docs with no detected relations" section; tool
Skill/`/discovery` template/`architecture/overview.md`/`docs/
cli-reference.md` all updated; new `decisions/0037` covers the two real
design calls (dedicated table vs. extending `documents_edges`/
`skill_mentions_edges`; fixed default globs vs. a manifest file).
Verified independently: `pytest` 398 passed/1 skipped (up from 371),
`ruff check .` clean, manual dogfooding sync against this repo confirmed
real spec docs detected and related (e.g. `architecture/overview.md` →
`mentions_dependency` edges to all four tracked vendors).

## Next concrete step

**Implementing the path-to-v1.0 sequence, phase by phase, per user
request ("implement the plans to initial release stage").** Phase 22
(AI-enriched cross-artifact relationships) is next — its verification
step requires one real, disclosed live API call against this repo, same
posture as the earlier live-enrichment validation session. Phase 23
(Polish/PyPI publish) still has no plan file — write it per `CLAUDE.md`
§1 before implementing it, and note its *actual* publish step is a
hard-to-reverse, externally-visible action (claiming a PyPI package name
forever) that must pause for explicit user confirmation, not proceed
automatically even under a broad "implement to release" instruction.

Three decisions remain genuinely open, none blocking Phase 22
implementation from starting immediately:

1. **Cutting the `v0.2` git tag and promoting `CHANGELOG.md`'s
   `[Unreleased]` section to a dated release** (`CLAUDE.md` §6,
   `decisions/0030`) — now *applicable* (all of phases 9-19 are `done`),
   but not yet decided or acted on, same posture `decisions/0022`
   established for `v0.1` (also still untagged). This is a user decision,
   not something to act on unilaterally. Note `v1.0` supersedes this as
   the actual target release if pursued directly — whether an interim
   `v0.2` tag still gets cut is an open question, not answered here.
2. **Whether routing/rollup and MCP (now 24/25) really should be deferred
   past v1.0** — proposed in `planning/v1.0-initial-release-roadmap.md`'s
   "Why this order" section, not locked. Flagged back to the user, not
   decided unilaterally.
3. **Phase 23 (Polish/PyPI publish)** has no plan file yet — needs one
   before implementation per `CLAUDE.md` §1, same as every other phase.

**Still outstanding, not a blocker but worth remembering:**
- The graph/enrichment ordering gap (routing table/tool Skill/`undo`
  freshness immediately after a vendor's first enrichment) is **resolved
  by Phase 20** (above).
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
