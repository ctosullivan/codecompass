# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phases 0-33 are all `done`.** Phase 23 (Polish/PyPI publish — the v1.0
release itself) is `in progress`: Part A (packaging/release readiness) is
`done`; Part B (the actual publish) remains paused for explicit user
confirmation — this is now the **only** thing between the current state
and a `v1.0` release. Phases 30-32 (doc-graph precision: bidirectional
traversal, typed relation labels, heading-based chunking), added to v1.0's
blocking scope at explicit user request, are all `done`; Phase 33 (a bug
fix found along the way) is also `done`. Nothing from this group blocks
Part B any longer.
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
exclusion (29). `pytest` climbed 367→468 across this arc, `ruff check .`
clean throughout, every phase live-verified against this repo's own real
graph, not just green tests.

**A `/discovery` session tested that graph's real relationship-data
quality** and found: full AI-enrichment coverage (39/39 relations
enriched); 3 spot-checked summaries all grounded in real text; `uses_edges`
already had real `(file, line)` data `query vendor --json` didn't expose
(confirmed the real gap Phase 30 targets); vendor-doc-as-source (29) works
but yields sparsely (1 of 28 vendor docs actually sources a relation);
and two incidental issues outside 30-32's scope — a `query --json`
Rich-wrapping bug, and a `check` version-drift reading that looked
backwards.

**Following that: a doc-graph precision planning pass** finalized three
attached draft phase plans (`planning/phase-30/31/32-*.md`) plus their
umbrella (`planning/doc-graph-precision-roadmap.md`) as committed plans,
and — per explicit user instruction — added all three to v1.0's blocking
scope alongside Phase 23.

**Then, at the user's request ("implement and fix bugs"), all four
phases were implemented, tested, and live-verified in one session:**

- **Phase 33** (`decisions`: none needed — a contained bug fix): every
  `codecompass query ... --json` call site printed pre-serialized JSON
  through the shared Rich `Console`, which word-wraps long printed text
  by inserting real line breaks — a value long enough to cross the wrap
  width got a literal newline inserted into it, corrupting the JSON.
  Fixed with `soft_wrap=True` on all five call sites, the same flag
  Rich's own `Console.print_json` uses internally. The session's other
  `/discovery`-flagged item (the version-drift reading) was investigated
  and confirmed **not** a bug: `check`'s "live" column reads the
  currently-installed version in this environment, not a PyPI-latest
  lookup, and this repo's `.venv` genuinely had an older `anthropic`
  installed than what was last recorded (`importlib.metadata` confirmed
  it directly) — no code change, no plan needed.

- **Phase 30** (`graph.py`, `cli.py`): `vendor_profile`/`symbol_profile`
  gained a `used_at` list (real `(file, line)` locations, not just a
  count); new `graph.doc_code_trace` composes `documents_edges`/
  `doc_relations_edges` with `uses_edges` into a two-hop package-code
  trace, surfaced in `query relations` as a new "Package code" section.
  `query relations --json`'s payload changed from a bare list to
  `{"relations": [...], "package_code": [...]}` — a deliberate, disclosed
  breaking change to that endpoint's shape (acceptable pre-1.0), noted
  directly in the phase's own plan file. Confirmed live: `query symbol
  Console`'s `used_at` matched real import-line locations `grep` found;
  `query relations architecture/overview.md`'s "Package code" section
  listed real `typer` call sites in `cli.py`.

- **Phase 31** (`relation_enrichment.py`, `graph.py`, `decisions/0045`):
  closed-taxonomy `relation_label` (`documents_configuration_of`/
  `explains_usage_of`/`contrasts_with`/`supersedes`/`other`) alongside
  the existing free-text `ai_summary`, strictly gated on Phase 21/29's
  already-mechanically-proven candidates. Any label outside the enum
  normalizes to `'other'`, never raises. `doc_relation_enrichment`
  migrated via `ALTER TABLE ADD COLUMN` (not drop-and-recreate — this
  table holds paid AI spend). Confirmed live: cleared and forced a real
  re-enrichment run over this repo's 39 real relationships (~$0.04); every
  row got a valid label, 0 NULL/invalid; 2 spot-checked labels
  (`decisions/0016`→`anthropic`, `decisions/0034`→the tool Skill)
  confirmed grounded against the real decision text.

- **Phase 32** (`doc_chunking.py` new, `graph.py`, `doc_mapping.py`,
  `relation_enrichment.py`, `decisions/0046`): deterministic heading-based
  markdown chunking (any heading level, root-first nested `heading_path`,
  zero chunks for a headerless doc by design). New `doc_chunks` table;
  nullable `chunk_id` on `documents_edges`/`doc_relations_edges`,
  populated only when a mechanical match is attributable to exactly one
  chunk. `doc_code_trace`/`query relations` gained an optional `heading`
  field. Enrichment excerpts now prefer the matched chunk's own text over
  Phase 28's fixed-window guess, which remains as the fallback, unchanged.
  `documents_edges`/`doc_relations_edges` migrated via the same
  drop-and-recreate approach `doc_artifacts` already uses (both always
  fully rewritten every sync). Confirmed live: chunked
  `architecture/overview.md`'s real ~1,600 lines into a correctly-nested
  structure; a real relation's excerpt now slices exactly from its
  matched chunk (`decisions/0016`→`anthropic`, verified byte-for-byte); a
  `chunk_id = NULL` relation still enriches correctly via the unchanged
  Phase 28 fallback; Phase 29's self-mention exclusion confirmed still
  correct under the new per-chunk pass (`vendor/anthropic/src/
  CHANGELOG.md` says "anthropic" 1,161 times, zero self-referencing
  edges, one real edge to `rich`).

Verified independently throughout all four: `pytest` climbed 469→502
passed (1 skipped throughout), `ruff check .` clean at every step,
core-logic diffs read directly against each plan before marking `done`,
every live-verification claim above checked against this repo's real
`context-graph.db`/files directly, not assumed.

**Not yet committed to git** — all of the above (Phases 30-33) is applied
to the working tree only; no commit has been made this session.

## Next concrete step

**Nothing from Phases 30-33 blocks anything anymore.** The two open items
are:

1. **Phase 23, Part B — the actual publish — remains paused for explicit
   user confirmation**, the only phase left before `v1.0`. Needs from the
   user: (1) go-ahead to actually run `twine upload` (optionally
   `--repository testpypi` first as a dry run), (2) go-ahead to cut and
   push the `v1.0` git tag, (3) confirmation that `CHANGELOG.md`'s
   `[Unreleased]` section should be promoted to a dated `v1.0` release
   section at the same time. None of this should happen from a broad
   "implement to release" instruction alone — claiming a PyPI package
   name and pushing a public tag are genuinely irreversible.
2. **This session's work is uncommitted.** Ask before committing (this
   session was not explicitly asked to commit) — a large multi-phase
   diff across `src/codecompass/{graph,cli,doc_mapping,relation_
   enrichment}.py`, new `doc_chunking.py`, `decisions/0045`/`0046`, and
   test/doc updates. Natural to split into 4 commits (one per phase,
   `type(phase-N): summary`, matching this project's established
   one-phase-one-commit convention) rather than one large commit.

**Two items from the `/discovery` session are now resolved**, not
outstanding: the `query --json` line-wrapping bug is fixed (Phase 33);
the version-drift reading was confirmed not a bug (see above).

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
- `vendor/` exists in this checkout with real, enriched content — a live
  artifact of past validation runs, not a fixture. Still gitignored and
  freely regeneratable (`decisions/0010`).
- A local `.venv/` exists at the project root (gitignored) with
  `codecompass` installed editable, for local testing.
