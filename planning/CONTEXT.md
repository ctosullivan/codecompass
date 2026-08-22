# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 17: `/discovery` slash command — done.** Phases 0-16 remain
`done`. Executing MVP (v0.2) per
`planning/v0.2-implementation-execution-plan.md`.

## What was just completed

Implemented `planning/phase-17-discovery-slash-command.md`: new
`src/codecompass/commands.py` (`render_discovery_command`/
`write_discovery_command`), generating `.claude/commands/discovery.md` —
frontmatter scopes `allowed-tools` to `Read`/`Grep`/`Glob` plus a
narrow `Bash(codecompass query:*)`/`Bash(codecompass check:*)`/
`Bash(sqlite3 context-graph.db:*)` allowlist (no `Write`/`Edit`), and
the body repeats the read-only constraint in plain instructional text
too — both mechanical and instructional, per the plan. `graph.py`'s
`doc_artifacts.kind` CHECK constraint widened to add `'slash_command'`
(`_SCHEMA_VERSION` "1"→"2"), with a migration in `open_graph` that
drops and recreates `doc_artifacts` for an already-existing older
database — safe, since that table (and everything cascading from it) is
fully rebuilt every whole-project sync anyway, and it has no FK
relationship to `vendor_enrichment`/`symbol_enrichment` to disturb.
`skill_scan.scan_skills` now also indexes the new file. Wired into
`cli.py` alongside `write_tool_skill`.

**Two legitimate scope gaps found and correctly left alone, not silently
worked around**: (1) the plan claimed `write_tool_skill` fires at three
points (`_bootstrap`, `index()`, `sync()`'s whole-project branch) — the
implementer greped and confirmed it's actually only two;
`write_discovery_command` was wired to match reality, not the plan's
inaccurate premise, and this is now documented in
`docs/cli-reference.md`/`architecture/overview.md`. (2) `codecompass
query skills` (Phase 15) hard-filters to `kind='skill'`, so the new
`slash_command`-kind row doesn't surface through it — confirmed present
via direct `sqlite3` read, left unmodified since fixing it wasn't in this
phase's scope. Both are minor, documented, low-priority — not blockers,
not silently patched over.

Verified independently: `pytest` 355 passed/1 skipped, `ruff check .`
clean. Read `graph.py`'s migration logic and the generated
`discovery.md`'s actual content directly — confirmed the migration
correctly cascades via `ON DELETE CASCADE` without touching enrichment
tables, and confirmed `CLAUDE.md`'s diff from this phase's dogfooding run
(bare `codecompass` against this repo) is confined entirely to the
mechanical routing-table block (a Depth→Enriched column rename
surfacing for the first time since Phase 15/16, since bare `codecompass`
hadn't been re-run here since) — no governance prose touched, so treated
as routine generated-artifact output, not a §0 approval case (consistent
with Phase 9's precedent, where only marker-delimiter text and prose
needed separate approval, not the table's row contents). `vendor/`
being absent from this checkout right now is expected, cosmetic drift in
a gitignored, freely-regeneratable directory — not a repeat of the
earlier session's file-loss incident; `vendor.toml` (tracked) is intact.

## Next concrete step

Implement `planning/phase-18-undo-command.md` next — new `undo [--yes]
[--dry-run]`, graph-backed enumeration of everything codecompass
generated (via `doc_artifacts.origin`) with a pattern-based fallback
when no graph exists yet, never commits on the user's behalf. Same
pattern: dispatch, re-verify independently (read the diff), doc-sync,
commit, push. Then Phase 19, closing out MVP (v0.2).

**Still outstanding, not a blocker but worth remembering:**
- Two minor, documented gaps from Phase 17, low-priority: `write_tool_skill`
  (and now `write_discovery_command`) only fire at two points
  (`_bootstrap`, `index()`) — `sync()`'s whole-project branch never
  regenerates either artifact, unlike the plan's original (inaccurate)
  premise of three trigger points. `codecompass query skills` hard-filters
  to `kind='skill'`, so `/discovery`'s own `slash_command`-kind graph row
  never surfaces through it (confirmed present via direct `sqlite3` read).
  Neither blocks anything; pick up only if they become a real annoyance.
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
