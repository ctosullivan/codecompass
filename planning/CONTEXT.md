# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phases 0-22 are all `done` (v0.1, v0.2, and path-to-v1.0 phases 20-22).
Phase 23 (Polish/PyPI publish — the v1.0 release itself) is `in
progress`: Part A (packaging/release readiness) is `done`; Part B (the
actual publish) is deliberately paused for explicit user confirmation.**
`codecompass` now: auto-clones every tracked vendor; detects real
project-source usage; maps docs/skills/dependencies/spec-docs into a
SQLite graph with both mechanical and AI-enriched relationship edges;
auto-triggers disclosed, confirmable batched AI enrichment for
usage-proven vendors *and* relationships; exposes all of it via
`codecompass query`, `/discovery`, and generated Skills; can `undo`
itself cleanly; frames chat as secondary. `promote` and `Depth` are fully
retired. Packaging is release-ready (`version = "1.0.0"`, real wheel
verified installable in a clean venv) but **not yet published to PyPI,
and no `v1.0` tag has been cut.**

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

## What was just completed (Phases 20-22, path-to-v1.0)

All three implemented via the established dispatch-then-independently-
verify pattern (diff read directly against each plan, not just green
tests), per explicit user request ("implement the plans to initial
release stage"):

- **Phase 20**: `cli._refresh_generated_artifacts` (graph rebuild →
  routing table → tool Skill → discovery command), called from a
  `try/finally` around `_maybe_run_enrichment` in both `_bootstrap` and
  `sync`'s whole-project branch, so these artifacts always reflect
  post-enrichment state and `sync` regenerates them for the first time.
- **Phase 21**: new `spec_docs.py` (`scan_spec_docs`, fixed default glob
  set) classifies a project's own README/`docs/`/`architecture/`/
  `decisions/` etc. as `doc_artifacts` rows (`kind='spec_doc'`,
  `origin='project'`); new `doc_mapping.build_doc_relations_edges` +
  `graph.py`'s `doc_relations_edges` table mechanically link them to
  vendors/other doc artifacts; new `codecompass query relations <name>`.
  `decisions/0037`.
- **Phase 22**: new `relation_enrichment.py` (sibling to `enrichment.py`)
  runs batched AI enrichment over Phase 21's mechanically-proven edges
  only, folded into the same disclosed Phase B cost/consent prompt. New
  `doc_relation_enrichment` table is **natural-key-only, no foreign key**
  to `doc_artifacts` (which is fully deleted/reinserted every rebuild,
  unlike upserted `vendors`/`symbols` — a real departure from the Phase 10
  precedent, caught and resolved correctly). The non-negotiable boundary —
  AI summaries go only to the graph, never into a spec doc's own file —
  is enforced structurally: `apply_results` doesn't even accept a
  `project_root`. `query relations` now shows each `ai_summary` when
  present. `decisions/0038`. A real SQL NULL-uniqueness gotcha
  (`UNIQUE` treats every `NULL` as distinct) was found during
  implementation and fixed with delete-then-insert + NULL-safe `IS`
  matching, documented candidly in the ADR.

Verified independently throughout: `pytest` 371 → 398 → 440 passed (1
skipped throughout), `ruff check .` clean at every step, core-logic diffs
read directly (not just test output) against each plan. Phase 21's manual
dogfooding sync confirmed real spec docs detected/related in this repo.
Phase 22's live-API validation (a real `sync --yes`, 23 relationships
enriched for ~$0.02) confirmed genuinely grounded summaries and that the
non-negotiable never-write-to-a-spec-doc boundary held in practice
(`sha256` of the mentioned spec docs unchanged before/after).

**Phase 23, Part A, done**: user confirmed the version-number assumption
(`1.0.0`). `pyproject.toml` bumped, `README.md` brought current (found a
real gap: no README mention of Phase 21/22's spec-doc relationship
detection at all), new `examples/toy-project`, new `decisions/0039`
(v1.0 ships without a dedicated docs site). A real `python -m build`
wheel verified installable in a fresh throwaway venv, independent of this
repo's own editable dev install.

**Recent history, condensed**: reinstalled `codecompass` 1.0.0 into the
local `.venv` and confirmed it works end-to-end against this repo. Fixed
a real accuracy gap in `/discovery`'s own claims about `allowed-tools`
(confirmed via `claude-code-guide`, not assumed: the pre-approval grant
is single-turn only, clears on the next message — `decisions/0040`). Ran
a `/discovery` session against this repo and reported findings (what's
enriched, an honest quality assessment, whether embedded vendor docs get
registered), surfacing two real, evidence-backed gaps that became
`planning/phase-26-symbol-level-resolution-for-attribute-usage.md` and
`planning/phase-27-register-embedded-vendor-docs.md` (appended to the
Post-MVP table as 26/27, no renumbering). Notably held `/discovery`'s own
"no plan file, say so and stop" constraint correctly when first asked to
save that plan mid-session, and got explicit confirmation before writing.

**Most recently — Phase 26, done**: `usage.detect_python_imports` now
upgrades a plain `import X`/`import X as alias` to symbol-level usage
evidence via an additive second AST pass over `ast.Attribute` nodes
(`X.Attr(...)` → a symbol-level `DetectedImport` alongside the unchanged
vendor-level one from the `import` itself; only the immediate attribute
resolves, `X.sub.Attr` → `sub` not `Attr`). Four new tests in
`tests/test_usage.py`. `architecture/overview.md` updated. No ADR needed
— a straightforward additive change with no design call beyond what the
plan already settled. Verified independently: `pytest` 445 passed/1
skipped (up from 441), `ruff check .` clean, diff read directly against
the plan (matches exactly).

**Phase 27, done**: new `doc_mapping.collect_vendor_upstream_doc_
artifacts` registers a vendor's own embedded upstream docs (`README*.md`/
`CHANGELOG.md`/`CONTRIBUTING.md`/`SECURITY.md`/`MIGRATION.md`, root-level
only, at `vendor/<name>/src/`) as `doc_artifacts` rows (`kind=
'vendor_doc'`, `origin='vendor_upstream'`, `_SCHEMA_VERSION` "3"->"4"),
wired into `sync.rebuild_project_graph` so every downstream mechanism
(Phase 21 mention-detection, Phase 22 AI enrichment, `query relations`)
picks them up with zero further changes. New `graph.
vendor_docs_without_relations` correctly checks the *target* column, not
a copy of `spec_docs_without_relations`'s *source*-column query - a real,
correctly-reasoned distinction (a vendor doc is never a relation source,
only a target). New `decisions/0041`. Verified independently: `pytest`
457 passed/1 skipped (up from 445), `ruff check .` clean, core-logic diff
read directly. Confirmed against this repo's own real dogfooding data: 28
vendor-doc rows registered across all 4 tracked vendors (5 anthropic, 1
pipdeptree, 21 rich - including translated READMEs, a deliberate,
documented tradeoff - 1 typer), Phase 15's `vendor/` usage-exclusion
unaffected.

**Most recently**: re-synced this repo (`sync --yes` — 2 vendors and 15
relationships re-enriched, real ~$0.04 spend, `anthropic`/`typer`'s
`symbol_set_hash` correctly invalidated by Phase 26's new symbol-level
edges) and ran a fresh `/discovery` session testing real output quality.
Phase 26 confirmed working with real before/after data (`anthropic`'s
"documented but unused" list shrank from 35→32, correctly dropping
`Anthropic`/`AnthropicError`/`APIResponse` — the symbols this codebase
actually constructs/catches). Phase 27 confirmed mechanically working,
but its one live example (`vendor/anthropic/src/README.md`, matched from
two spec docs) surfaced a real, reproducible Phase 22 limitation: both
AI summaries are ungrounded, traced to the exact root cause — `relation_
enrichment.py`'s excerpt is always the source doc's first 4,000
characters, and both real matches sit at character 7,870 and 91,374
respectively, both past that window. Wrote `planning/phase-28-center-
relationship-excerpts-on-the-actual-match.md` (found via this live
testing, not guessed) — held `/discovery`'s own "no plan file" constraint
correctly again when first asked, then wrote it once the user explicitly
said to exit read-only. `planning/ROADMAP.md` updated: 28 appended after
27, no renumbering. **Not yet implemented.**

## Next concrete step

**Phase 23, Part B — the actual publish — is paused for explicit user
confirmation, not proceeded automatically.** Needs from the user before
this session acts: (1) go-ahead to actually run `twine upload` (optionally
`--repository testpypi` first as a dry run — worth offering), (2) go-ahead
to cut and push the `v1.0` git tag, (3) confirmation that `CHANGELOG.md`'s
`[Unreleased]` section should be promoted to a dated `v1.0` release
section at the same time. None of this should happen from a broad
"implement to release" instruction alone — claiming a PyPI package name
and pushing a public tag are genuinely irreversible.

Two decisions remain genuinely open, unrelated to Part B and not blocking
Phase 28 planning/implementation:

1. **Whether routing/rollup and MCP (now 24/25) really should be deferred
   past v1.0** — proposed in `planning/v1.0-initial-release-roadmap.md`'s
   "Why this order" section, not locked. Flagged back to the user, not
   decided unilaterally.
2. **Whether/when to implement Phase 28** — written as a future plan per
   the user's explicit request, not implemented yet; no urgency signal
   from the user either way. Implementing it will require deliberately
   forcing re-enrichment of the two already-cached (ungrounded)
   `anthropic README.md` relationships to actually verify the fix — see
   the plan's own Verification section for why a plain re-sync won't do
   that on its own.

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
