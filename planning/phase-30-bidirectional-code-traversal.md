# Phase 30: Expose vendor/doc → package-code traversal in the query layer

## Status

`done`

## Context

`uses_edges` already stores `source_file_id`, `vendor_id`, `symbol_id`, and
`line` — indexed on all three (`idx_uses_vendor`, `idx_uses_symbol`,
`idx_uses_source_file`). This is already a vendor/symbol → package-code
edge with line-level precision, populated by Phase 26's symbol-level usage
detection. `documents_edges` (doc_artifact → symbol) and
`doc_relations_edges` (`mentions_dependency`: spec_doc/vendor_doc →
vendor) already exist as well. Composing these gives a doc → symbol →
package-code path and a spec-doc → vendor → package-code path without any
new mechanical detection.

`graph.documented_but_unused`/`graph.used_but_undocumented` already
perform this exact `documents_edges` → `uses_edges` join internally to
power `check`'s coverage gate — so the traversal is already trusted and
already computed, just not exposed as a general, navigable query. Right
now `vendor_profile`/`symbol_profile` collapse `uses_edges` down to a bare
`usage_count` integer, discarding the file/line precision already stored
in the same table.

This phase is query-surface work only: no new tables, no new mechanical
detection, no new AI calls. It recombines data already in the graph, the
same category of change as Phase 20's `_refresh_generated_artifacts`.

**Related:** Phase 32 (doc chunking, planned after Phase 31) later adds an
optional chunk-level location to `doc_code_trace`'s output, additively —
this phase's whole-doc-level output remains valid and unchanged either
way; Phase 32 only adds a field when chunk data exists.

## Scope

**Covers:**
- Extending `vendor_profile`/`symbol_profile` to return actual
  `(source_file_path, line)` locations from `uses_edges`, not just a count.
- A new `graph.doc_code_trace(conn, doc_path_or_vendor_name)` function
  implementing the two-hop join:
  - `doc_artifacts` → `documents_edges` → `symbols` → `uses_edges` →
    `source_files` (vendor/vendor-doc side — "this doc documents symbol X,
    here's where the project calls it")
  - `doc_relations_edges` (`mentions_dependency`) → `vendors` →
    `uses_edges` → `source_files` (spec-doc **and** vendor-doc side, per
    `decisions/0043`'s `_DOC_RELATION_SOURCE_KINDS` — "this spec doc or
    vendor's own embedded doc mentions vendor Y, here's where the project
    actually uses it")
- Surfacing both in `codecompass query vendor`, `query symbol`, and
  `query relations` (human-readable and `--json` output).
- Updating `docs/cli-reference.md` and `architecture/overview.md`'s
  Context graph section to describe the new output fields.

**Explicitly does not cover:**
- Any new persisted edge table. This is a computed join at query time,
  same posture as `documented_but_unused` — not a new materialized edge,
  to avoid a third staleness axis to invalidate for something SQL can
  already answer cheaply at read time. If a design review later decides a
  materialized table is actually warranted (e.g. for performance on a very
  large graph), that's a new ADR, not an assumption baked into this phase.
- Symbol-level mention detection inside doc *text* (matching doc prose
  against symbol names beyond what `documents_edges`/`doc_relations_edges`
  already capture) — that's Tier 1 of a separate, not-yet-planned phase.
- Any AI/enrichment work — see Phase 31.
- `/discovery`'s own content — out of this phase's file list; flag if
  inspection surfaces a real gap there, per this project's established
  orchestrator/implementer split.

## Design decisions

- **Query-time join, not a stored edge.** Reuses existing indexes
  (`idx_uses_symbol`, `idx_uses_source_file`); no schema migration needed
  beyond confirming those indexes cover the new query shapes. If this
  turns out non-obvious in review, write `decisions/0044` documenting the
  computed-join-vs-materialized-table tradeoff explicitly — don't just
  fold the choice in silently.
- **`--json` parity.** Every existing `query` subcommand supports `--json`;
  the new fields (`used_at: [{path, line}, ...]`) must appear in both
  human and JSON output, consistent with existing subcommands.
- **No location data for a symbol with zero usage.** `used_at` is an empty
  list, not `null` or an error — mirrors `usage_count: 0`'s existing
  treatment for an unused symbol.
- **`query relations --json`'s payload becomes `{"relations": [...],
  "package_code": [...]}`, not a bare list** (found during implementation,
  not anticipated when this plan was drafted). `query vendor`/`query
  symbol` add `used_at` as one more key on their existing dict payloads —
  purely additive, no shape change. `query relations`'s existing payload
  was already a bare list of relation dicts, and a relation (a mention)
  and a usage site (a code location) are different shapes that don't
  merge into one row without inventing an artificial join — wrapping both
  lists in one object was the smallest change that keeps both, rather
  than picking one shape to force the other into. This is a real, if
  small, breaking change to `query relations --json`'s existing contract;
  acceptable pre-1.0 with no external consumers yet (same posture the
  project takes toward not maintaining compatibility shims). The seven
  existing tests asserting the old bare-list shape were updated in the
  same commit.

## Files

- `src/codecompass/graph.py` — extend `vendor_profile`/`symbol_profile`
  with a `used_at` list; add `doc_code_trace`.
- `src/codecompass/cli.py` — `query vendor`/`query symbol`/`query
  relations` output gains a "Used at" / "Package code" section.
- `docs/cli-reference.md` — document the new output fields for all three
  subcommands.
- `architecture/overview.md` — document the two-hop composition in the
  Context graph section; note explicitly that no new tables were added.
- `tests/test_graph.py` — new tests for `used_at` on both `vendor_profile`
  and `symbol_profile`, and for `doc_code_trace` covering both the
  vendor/vendor-doc path and the spec-doc path.
- `tests/test_cli.py` — new tests asserting the new sections appear in
  both human and `--json` output.
- `CHANGELOG.md` — `[Unreleased]` entry, `Added` category.

## Verification

- `pytest` passes, new test count reflected in the run.
- `ruff check .` clean.
- Live dogfood against this repo's own real graph: `codecompass query
  symbol Console` should list real `(file, line)` pairs matching what a
  manual `grep -rn "Console" src/` finds in this project's actual source
  — read the two side by side, don't just trust green tests.
- `codecompass query relations architecture/overview.md` should now show
  a "Package code" section listing real usage sites for whichever vendors
  that doc mechanically mentions.
- Core-logic diff read directly against this plan before marking `done`,
  per this project's standing verification pattern.
