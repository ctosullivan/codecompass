# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phases 0-34 are all `done`.** Phase 23 (Polish/PyPI publish — the v1.0
release itself) is `in progress`: Part A (packaging/release readiness) is
`done`; Part B (the actual publish) remains paused for explicit user
confirmation — this is now the **only** thing between the current state
and a `v1.0` release. Phases 30-32 (doc-graph precision: bidirectional
traversal, typed relation labels, heading-based chunking), added to v1.0's
blocking scope at explicit user request, are all `done`; Phases 33 and 34
(both bug fixes found via live `/discovery` dogfooding) are also `done`.
Nothing from this group blocks Part B any longer.
`codecompass` now: auto-clones every tracked vendor; detects real
project-source usage (vendor- and symbol-level); maps docs/skills/
dependencies/spec-docs/vendor-docs into a SQLite graph with both
mechanical and AI-enriched relationship edges, now with real `(file,
line)` code-usage traversal, typed relation labels, and heading-scoped
doc chunking sharpening both; auto-triggers disclosed, confirmable
batched AI enrichment for usage-proven vendors *and* relationships;
exposes all of it via `codecompass query`, `/discovery`, and generated
Skills; can `undo` itself cleanly; frames chat as secondary. `promote` and
`Depth` are fully retired. Packaging is release-ready (`version =
"1.0.0"`, real wheel verified installable in a clean venv) but **not yet
published to PyPI, and no `v1.0` tag has been cut.**

## What was just completed

**Path-to-v1.0 phases 20-23 Part A, and Phases 26-29 (all found via live
`/discovery` sessions), condensed** — see git history / `CHANGELOG.md`
for full detail: graph/enrichment ordering fixed (20); mechanical
spec-doc detection and `query relations` (21); AI-enriched relationship
summaries (22); packaging brought to release-ready (23A); symbol-level
usage resolution for `import X` + `X.Attr(...)` (26); vendor upstream
docs registered as `doc_artifacts` (27); enrichment excerpts centered on
the real mechanical match instead of the file's opening (28); vendor docs
became relationship *sources*, not just targets, with a self-mention
exclusion (29). `pytest` climbed 367→468 across this arc.

**Doc-graph precision arc (Phases 30-32), condensed** — planned together
(`planning/doc-graph-precision-roadmap.md`), added to v1.0's blocking
scope at explicit user request, implemented and live-verified in one
session:
- **30**: `vendor_profile`/`symbol_profile` gained a `used_at` list (real
  `(file, line)` locations); new `graph.doc_code_trace` composes edges
  into a two-hop package-code trace, surfaced in `query relations` as a
  new "Package code" section. `query relations --json`'s payload changed
  from a bare list to `{"relations": [...], "package_code": [...]}` — a
  deliberate, disclosed pre-1.0 breaking change.
- **31**: closed-taxonomy `relation_label` (`documents_configuration_of`/
  `explains_usage_of`/`contrasts_with`/`supersedes`/`other`) alongside
  the existing free-text `ai_summary`, gated on already-mechanically-
  proven candidates only; any out-of-enum label normalizes to `'other'`.
  `doc_relation_enrichment` migrated via `ALTER TABLE ADD COLUMN` (paid
  AI spend, must survive). `decisions/0045`.
- **32**: new `doc_chunking.py`, deterministic heading-based markdown
  chunking; new `doc_chunks` table; nullable `chunk_id` on
  `documents_edges`/`doc_relations_edges`. Enrichment excerpts prefer the
  matched chunk's own text over Phase 28's fixed-window guess (which
  remains as fallback). `documents_edges`/`doc_relations_edges` migrated
  via drop-and-recreate (always fully rewritten every sync anyway).
  `decisions/0046`.

Verified independently throughout: `pytest` climbed 469→502 passed,
`ruff check .` clean at every step, core-logic diffs read directly
against each plan, every live-verification claim checked against this
repo's real `context-graph.db`/files directly. Committed as one commit
per phase (`fix(phase-33)`, `feat(phase-30)`, `feat(phase-31)`,
`feat(phase-32)`, plus a `docs:` commit for this file), pushed to
`origin/main`.

**Most recently — a second `/discovery` session tested Phase 30-33's real
output quality** and found Phase 30/31/33 all working correctly on real
data (used_at/package-code locations verified against `grep`; all 39
relation labels valid and 2 spot-checked as grounded; `query --json`
confirmed parseable). It also found a **real bug in Phase 32**:
`doc_chunking.chunk_markdown`'s heading regex had no awareness of fenced
code blocks (` ``` `/`~~~`), so a `#`-prefixed comment inside an example
fence (e.g. `docs/cli-reference.md`'s `# Not a shell command...`) got
misdetected as a real heading — corrupting `heading_path` both for the
bogus chunk itself and for whatever real heading followed it. Scanning
all 84 chunkable doc artifacts found 37 such false-positive lines, 12 of
which had already produced real bogus headings on `vendor/anthropic/src/
MIGRATION.md`'s `documents_edges` rows (e.g. `"After > Bedrock: a region
is now required"`, a fake heading prepended to a real one).

**Phase 34, done**: fixed by tracking fence state in `chunk_markdown` and
never treating a line inside one as a heading candidate — deliberately a
simple toggle (any line starting with ` ``` ` or `~~~`), not a full
markdown parser, consistent with this project's mechanical-detection
posture elsewhere. No backfill; the next whole-project `sync` naturally
recomputes `doc_chunks`. Three new regression tests (two confirmed to
fail against the pre-fix code). `pytest` 502→505 passed, `ruff check .`
clean. **Confirmed live**: re-synced this repo after the fix —
`docs/cli-reference.md`'s `typer` relation now reports the real heading
(`` `codecompass undo [--yes] [--dry-run]` ``, not the fabricated one);
`vendor/anthropic/src/MIGRATION.md`'s previously-bogus headings now show
real chains (`"Migrating to v1 > Bedrock: a region is now required"`).
Committed as `fix(phase-34)`.

## Next concrete step

**Nothing outstanding blocks anything.** The two open items are:

1. **Phase 23, Part B — the actual publish — remains paused for explicit
   user confirmation**, the only phase left before `v1.0`. Needs from the
   user: (1) go-ahead to actually run `twine upload` (optionally
   `--repository testpypi` first as a dry run), (2) go-ahead to cut and
   push the `v1.0` git tag, (3) confirmation that `CHANGELOG.md`'s
   `[Unreleased]` section should be promoted to a dated `v1.0` release
   section at the same time. None of this should happen from a broad
   "implement to release" instruction alone — claiming a PyPI package
   name and pushing a public tag are genuinely irreversible.
2. **Confirm before pushing this session's Phase 34 commit** (and this
   `CONTEXT.md` update) to the remote — not yet pushed as of this update.

One decision remains genuinely open, unrelated to the above and not
blocking anything currently in flight:
1. **Whether routing/rollup and MCP (24/25) really should be deferred
   past v1.0** — proposed in `planning/v1.0-initial-release-roadmap.md`'s
   "Why this order" section, not locked. Flagged back to the user, not
   decided unilaterally.

**Still outstanding, not a blocker but worth remembering:**
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter against real
  `cargo metadata` output and a real crate — currently entirely
  unverified.
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `chat.py` has still never been run against the real Anthropic API in
  this environment.
- `staleness.py`'s version parser has no real PEP 440/semver correctness.
- A formal trigger-accuracy evaluation harness for per-vendor Skills
  (`decisions/0013`) remains outstanding.
- Cursor `.mdc` export has no `globs` field — documented future
  refinement, not implemented.
- `doc_chunks`' per-chunk `content_hash` (Phase 32) isn't yet consumed
  for cache-invalidation grain — `select_candidates` still hashes a
  relation's *full* source-doc text against the target's text, unchanged
  since Phase 22. Computed correctly and available for a future phase if
  chunk-grain cache invalidation is ever pursued (noted in
  `decisions/0046`), not wired up now.
- The fenced-code-block fix (Phase 34) only tracks ` ``` `/`~~~` fences,
  not indented (4-space) code blocks — not a gap in practice, since a
  heading regex requires `#` at column 0, which an indented block's
  content can never satisfy.
- `vendor/` exists in this checkout with real, enriched content — a live
  artifact of past validation runs, not a fixture. Still gitignored and
  freely regeneratable (`decisions/0010`).
- A local `.venv/` exists at the project root (gitignored) with
  `codecompass` installed editable, for local testing.
