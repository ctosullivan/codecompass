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

**Phase 22's live-API validation, now done**: ran a real `sync --yes`
against this repo — one Anthropic call, 23 relationships enriched
(~$0.02), genuinely grounded summaries (e.g. correctly identified `rich`
as used for terminal rendering, `typer` as the CLI framework, from real
`architecture/overview.md` content, verified via `query relations
architecture/overview.md --json`). `sha256` of `architecture/overview.md`/
`README.md`/`decisions/0037-*.md` confirmed byte-identical before and
after — the non-negotiable boundary held in practice, not just in mocked
tests. Only the tool Skill/discovery command (tracked generated
artifacts) regenerated, picking up the new `doc_relation_enrichment`
schema mention; committed separately.

## What was just completed (Phase 23, Part A)

User confirmed the one open assumption the plan flagged (version `1.0.0`,
over the alternative `0.3.0`). Implemented and verified independently:
`pyproject.toml` (`version = "1.0.0"`, `classifiers` → `4 - Beta`,
`[project.urls]` added), `README.md`'s Status/feature-list brought current
(including a real gap found: no README mention of Phase 21/22's spec-doc
relationship detection at all until now), new `examples/toy-project`
(real `requests`/`click` usage, real captured `codecompass` output in its
`README.md`, no generated artifacts committed — already covered by the
existing `vendor/` gitignore pattern), new `decisions/0039` (ship v1.0
without a dedicated docs site — a deliberate, revisitable deferral).
Packaging smoke test genuinely run, not assumed: a real `python -m build`
wheel installed into a fresh throwaway venv independent of this repo's
editable dev install, `codecompass --help` confirmed working from it.
`pytest` 440 passed/1 skipped (unchanged — no functional code touched),
`ruff check .` clean.

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

One decision remains genuinely open, unrelated to Part B and not blocking
it:

1. **Whether routing/rollup and MCP (now 24/25) really should be deferred
   past v1.0** — proposed in `planning/v1.0-initial-release-roadmap.md`'s
   "Why this order" section, not locked. Flagged back to the user, not
   decided unilaterally.

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
