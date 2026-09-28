# Docs-drift audit — Phase 77 (First-party source awareness) — RE-AUDIT

Independent re-audit, per `documentation-lifecycle.md` §2.5 and CLAUDE.md
§5. This supersedes the initial audit below the original commit range;
this pass verifies commits `04b87c2` (direct doc fixes for the three
findings below), `68e80b3` (`domain-skeptic`'s independent
citation-currency review — Evidence records only, no `docs/domain/`
edits, per its own write boundary), and `41ed6aa` (the lead applying
every fix `domain-skeptic` named). Every claim below was checked against
the real current source (`src/codecompass/graph.py`,
`src/codecompass/sync.py`, `src/codecompass/source_symbols.py`,
`tests/test_graph.py`, `architecture/overview.md`) directly — not against
the commit messages' own claims.

## Verdict: NO DRIFT

All three original findings are fixed correctly, all five domain-corpus
citation fixes (plus the two further pre-existing-but-unrelated broken
citations found and fixed alongside them) check out exactly against real
line numbers, and no new drift was introduced by any of the three
commits.

### Finding 1 (from the prior audit) — RESOLVED, verified

`architecture/context-graph-schema.md`'s "Migrations" section now reads
"## Migrations — why six separate functions, not one" / "`open_graph`
runs six migration functions" and its bulleted enumeration adds
`_migrate_source_files_columns`, described as adding `source_files`'s
four new nullable columns (`language`, `content_hash`,
`symbol_index_status`, `symbol_index_diagnostic`) via `ALTER TABLE ADD
COLUMN`, never drop/recreate, because of the `uses_edges.source_file_id
ON DELETE CASCADE` risk.

Verified directly against `graph.py`:
- `grep -n "^def _migrate\|def open_graph"` confirms exactly six
  `_migrate_*` functions exist (`_migrate_doc_artifacts_constraints`,
  `_migrate_doc_relation_enrichment_relation_label`,
  `_migrate_symbols_export_kind_note_columns`,
  `_migrate_symbol_enrichment_model_column`,
  `_migrate_source_files_columns`, `_migrate_vendors_ecosystem_constraint`)
  and `open_graph` (lines 893-918) calls all six in sequence (lines
  903-908) before `init_schema`.
- Read `_migrate_source_files_columns`'s full body (lines 754-803):
  checks `source_files`'s existence, reads `PRAGMA table_info`, and adds
  exactly the four named columns via `ALTER TABLE ... ADD COLUMN` inside
  a single `with conn:` transaction — no `DROP`/`CREATE`/recreate logic
  anywhere in it. The doc's description matches the real function body
  exactly, including the CHECK constraint on `symbol_index_status`
  reproduced verbatim.

### Finding 2 (minor observation, prior audit) — RESOLVED, verified

`architecture/overview.md`'s CORE module-tier list (line 175) now reads
"...`usage.py`, `git_topology.py` (Phase 76), `source_symbols.py` (Phase
77), `source_resolution.py`, ..." — both modules the prior audit flagged
as missing are present, plus an explanatory parenthetical about the
`git_topology.py` omission predating this phase and being fixed
opportunistically.

### Finding 3 (wording nit, prior audit) — RESOLVED, verified

`README.md` (lines 161-163) now reads "cross-language exposure
classification (\`public\`/\`restricted\`/\`internal\`/
\`conventional_private\`/\`unknown\`)" — all five real values, correctly
backtick-quoted. Verified against `graph.py`'s live CHECK constraint on
`source_symbols.exposure` (lines 102-106):
`'public','restricted','internal','conventional_private','unknown'` —
exact match, five values, same order.

## Domain-corpus citation fixes — spot-checked (all five, plus two extra)

The dispatch asked for at least three spot-checks; all five named fixes
plus both of the additional pre-existing-but-unrelated broken citations
`domain-skeptic` found were independently verified against real current
line numbers (not the commit message's own claim):

1. **`reference.md`**: `graph.py:143-161` — read directly: lines 143-161
   are exactly the `doc_artifacts` `CREATE TABLE` statement including the
   `origin` CHECK enum (`'codecompass_tool','codecompass_vendor',
   'third_party','project','vendor_upstream','pinned_reference'`),
   closing at line 161. Exact match.
2. **`context.md`** and **`relationship-edge.md`** schema citation,
   `graph.py:50-430`: `_SCHEMA_SQL` itself now runs 48-288 (was 48-248
   pre-Phase-77, a +40 shift matching the phase's first hunk); the old
   citation (`50-360`) already extended ~112 lines past the schema's own
   end into the row-dataclass block, ending just before
   `SkillMentionEdgeRow`'s last field (old line 362). The new citation
   (`50-430`) preserves the identical intent post-shift: `graph.py`
   line 430 is one line before `SkillMentionEdgeRow`'s own last field
   (line 431) — the same near-exact stopping point, correctly
   re-derived from the real diff hunks rather than a rough guess.
3. **`relationship-edge.md`**'s `rebuild_deterministic` citation,
   corrected from a stale, already-wrong-pre-Phase-77 `1184-1226` to
   `935-1084`: `grep -n "^def rebuild_deterministic"` confirms it starts
   at line 935; line 1084 is the function's last statement (a blank line
   at 1084 precedes `_sync_vendors`'s `def` at line 1085) — exact
   function bounds. The same commit's exception-list prose fix
   ("except the natural-key-upserted `vendors`/`symbols`/`source_files`
   nodes") was verified against `rebuild_deterministic`'s real body:
   no `DELETE FROM source_files` exists anywhere in it, and
   `_sync_source_files` (line 1169) is genuinely an upsert-by-natural-key
   (`path`) function, docstring-confirmed ("mirrors `_sync_vendors`'s
   exact shape ... not the old clear-and-reinsert treatment"). The two
   further corrections in this file — `tests/test_graph.py:1611-1621`
   (function starts at line 1611 per `grep`, body ends exactly at 1621)
   and `architecture/overview.md:688-734` (the "## Context graph" heading
   is exactly at line 688; the section's own content ends exactly at
   line 734, immediately before "## Doc chunking"'s bold-lead-in at line
   736) — both confirmed exact.
4. **`provenance.md`**: all four shifted `graph.py` citations verified
   exact — `204-222` (vendor_enrichment lines 204-214 + symbol_enrichment
   lines 216-222, the two enrichment tables together), `205-215`
   (vendor_enrichment table bounds), `216-222` (symbol_enrichment table
   bounds, "five columns" claim confirmed:
   `id, symbol_id, purpose, model, generated_at`), and the corrected
   `204-243, 717-751` (204-243 spans all three enrichment tables —
   vendor_enrichment, symbol_enrichment, doc_relation_enrichment — ending
   at doc_relation_enrichment's own close; 717-751 is
   `_migrate_symbol_enrichment_model_column`'s exact real body, confirmed
   the pre-existing `515-549` citation this replaced actually pointed at
   the wrong function, `_migrate_doc_artifacts_constraints`, not this
   one).
5. **`digest.md`**: `sync.py:162-204` for `sync_vendor` — confirmed this
   is a real, in-bounds sub-span of `sync_vendor` (which itself spans
   lines 107-206ish), covering the enrichment-lookup-to-digest-
   construction portion (`graph_conn.close()` through
   `VendorDigest(...)`'s own construction, ending right before the
   `OVERVIEW.md` write) — a deliberate sub-range consistent with the old
   citation's own shape (`160-202`, shifted by the phase's real +2-line
   `sync.py` import-block delta), not a new or broader claim.

## Independence / write-boundary check

`git show 68e80b3 --stat` confirms `domain-skeptic`'s own commit touches
only `planning/knowledge/codecompass-domain/EV-*.yaml` and its own retro
file — zero edits to `docs/domain/concepts/*.md` itself, consistent with
its fixed write boundary (`decisions/0060`). The actual `docs/domain/`
edits landed in the separate `41ed6aa` commit, authored by the lead
applying the fixes — the process the dispatch describes checks out
exactly as claimed.

## No new drift introduced

`git diff 5398eb3..41ed6aa --stat` shows only the eight files expected
(`README.md`, `architecture/context-graph-schema.md`,
`architecture/overview.md`, five `docs/domain/concepts/*.md` files) plus
Evidence/retro records under `planning/`, which are not current-truth
system docs in the audited sense. No other file was touched by these
three commits, so none of the prior audit's other "verified correct"
findings (context-graph-schema.md's First-party source tables section,
overview.md's own First-party source awareness section, module-map.md's
module/line counts, cli-reference.md's `query source`/`query
source-symbol` behavior, the `codecompass-template` link, decisions/0065,
the `.claude/skills/codecompass/SKILL.md`/`CHANGELOG.md` sweep) could
have been invalidated — none of that content changed since the original
pass.

One out-of-scope observation, not a drift finding: a fourth commit,
`4fb9483` ("phase retro"), landed after the three under review, adding
`planning/retros/phase-77-first-party-source-and-template.md` only —
pure `planning/` content, not a current-truth doc, outside this audit's
scope.

## Scope note

Checked: all three original findings' fixes, all five named domain-corpus
citation fixes plus the two additional ones found alongside them (seven
total citation corrections, all spot-checked against real line numbers —
exceeding the dispatch's "at least three" ask), the independence/
write-boundary claim for `domain-skeptic`'s commit, and a diff-stat sweep
for unintended collateral changes. Not re-verified: the domain concept
pages' own *substantive* correctness beyond citation currency (still
`domain-skeptic`'s domain, not this audit's, per Mode 1 §5), and the new
Evidence YAML records' own internal schema validity (not a documentation
current-truth claim in the audited sense).
