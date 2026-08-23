# Phase 38: Final polish — redundancy cleanup

## Scope

Requested directly by the user: a final polish pass focused on
redundancies, ahead of finishing Phase 23 Part B (the v1.0 release
itself). Two research passes were run against the real repo first (not
assumptions) — a full roadmap/state review, then a targeted 5-category
redundancy/dead-code audit (dead references to retired concepts,
duplicate logic, unused/unpinned dependencies, doc staleness, test-suite
overlap). Three of five categories were clean. Two turned up concrete,
real findings, acted on here:

**Changed:**
- `src/codecompass/cli.py` — two structural dedups, both intra-file (not
  cross-module, so no new coupling introduced):
  - Extracted `_not_found_error(name) -> NoReturn`, replacing two
    verbatim-duplicate `"[red]error:[/red] {name!r} not found in
    context-graph.db"` + `typer.Exit(code=1)` blocks (`query_vendor`,
    `query_relations`).
  - Extracted `_graph_session(project_root)`, a `@contextlib.
    contextmanager` wrapper around `_open_graph_or_note` — collapses the
    open/`if None: return`/try/finally scaffold that was hand-repeated
    across 6 call sites (`_print_coverage_gap_sections`, `query_vendors`,
    `query_vendor`, `query_symbol`, `query_skills`, `query_relations`)
    down to one `with` block plus the still-necessary `None` check per
    site.
- `vendor.toml` — stripped 4 dead `depth = "surface"` lines (the retired
  `Depth` field, silently ignored on read since Phase 16, `decisions/
  0031`/`0035`; confirmed `config.py`'s `_parse_entry` never reads it).
  This is the project's own dependency manifest, not a third party's.
- `pyproject.toml` — added lower-bound version pins to all 4 runtime
  dependencies (`typer>=0.27`, `rich>=15`, `anthropic>=0.109`,
  `pipdeptree>=4.2`, no upper bounds), previously fully unpinned. See
  `decisions/0047` for the reasoning and the live verification that this
  is safe against `anthropic`'s real 1.0.0 (a genuine breaking major
  version, confirmed via `vendor/anthropic/src/MIGRATION.md`).

**Explicitly investigated, no change made:**
- The word-boundary mention-regex (`re.search(rf"\b{re.escape(needle)}\b",
  text)`) appears near-identically across `doc_mapping.py` (4 sites),
  `skill_scan.py` (2 sites), `relation_enrichment.py` (1 site). Not
  extracted: `decisions/0038` already documents this project's deliberate
  preference for small, single-purpose modules over shared abstractions
  in this exact area, and the duplicated expression is a single trivial
  line, not an error-prone one. Extracting a cross-module helper for it
  would run against the project's own stated convention for a marginal
  gain.
- Dead references to retired concepts (`Depth`, `promote`,
  `grounded_description`, `gap_analysis`, `context_path`, `is_stale`):
  audited, all clean — every reference in `src/`/`tests/` is either a
  regression test proving the removal, or a historical comment.
- Doc staleness: `docs/cli-reference.md` and `architecture/overview.md`
  both audited against the real current module/command list — no gaps.
  `README.md`'s status line separately re-verified directly and found
  already accurate.
- Test-suite overlap: 30 test files audited, none duplicate-purpose.

## Files

- `src/codecompass/cli.py`
- `vendor.toml`
- `pyproject.toml`
- `decisions/0047-lower-bound-dependency-pins-for-v1.md` (new)
- `README.md` — one-line phase-count fix (`0-37` → `0-38`), caught by this
  phase's own `check_user_docs.py` verification step below.
- `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md`

## Verification

- `pytest`: 520 passed, 1 skipped (Cargo smoke test, no toolchain
  available — pre-existing, unrelated) — confirmed before and after.
- `ruff check .`: clean.
- Manual CLI smoke test: `query vendor <bad-name>` and `query relations
  <bad-name>` both still print the identical error and exit code 1;
  `query vendors`, `query symbol <name>` still work end-to-end against
  this repo's real `context-graph.db`.
- `codecompass check` run against this repo itself after stripping
  `vendor.toml`'s `depth` lines — ran clean, confirming the parser really
  does ignore the field (not just in theory).
- Packaging smoke test re-run after the dependency-pin change: `python -m
  build --wheel`, installed into a fresh throwaway venv, `codecompass
  --help` works; confirmed the pinned versions resolve as expected
  (`pip show` against the fresh venv).
- `anthropic`'s real MIGRATION.md (`vendor/anthropic/src/MIGRATION.md`,
  "Migrating to v1") checked line-by-line against all three of
  codecompass's own `_call_anthropic` implementations
  (`enrichment.py`/`relation_enrichment.py`/`chat.py`) — none touch any
  removed/changed parameter (`temperature`/`top_p`/`top_k`,
  `output_format`, `with_raw_response`, `tool_runner`, Bedrock, streaming
  `isinstance` checks). The lower-bound-only pin is confirmed safe in
  practice, not just in theory.
- `python scripts/check_user_docs.py --strict` run as part of this
  phase's own verification: caught `README.md`'s phase-count line still
  reading "phases 0-37" once the ROADMAP row above bumped the highest
  `done` phase to 38 — fixed inline (same catch category `docs(phase-37)`
  hit previously), then re-ran clean (0 findings, exit 0).
