# Domain-skeptic citation-currency review — Phase 77 (First-party source awareness)

Scope: the five `docs/domain/concepts/*.md` pages the Phase 77
`docs-reconstructor` drift audit (`planning/retros/_drift-audit-phase-77.md`)
flagged as citing `src/codecompass/graph.py`/`sync.py` line ranges shifted
by this phase's diff. Every cited line range below was re-derived directly
from the real current file and the real pre-Phase-77 file (`git show
03f8519^:<path>`), using the full `@@` hunk accounting for each file, not
the audit's own rough summary. Re-derivation method: for each citation,
computed the cumulative net-line-change of every diff hunk preceding the
cited old line number, then confirmed the resulting new line number by an
exact verbatim text match between the old-file line and the new-file line
at the computed offset — never accepted a computed offset without that
match.

Per this role's fixed write boundary (read-only toward `docs/domain/`,
under any circumstance, including a one-line citation fix), **no edits
were made to any `docs/domain/concepts/*.md` file**, notwithstanding that
the dispatch explicitly invited a citation fix and, for
`relationship-edge.md`, a content addition. All five pages' own repair
work is named precisely below for the lead/`context-researcher`/
`docs-maintainer` to apply. Five new Evidence records were appended
capturing what I verified myself.

## Page 1 — `docs/domain/concepts/reference.md`

**Citation**: `src/codecompass/graph.py:104-122` (`doc_artifacts.origin`
CHECK enum).

**Finding**: Phase 77's first hunk (net +40 at old line 63) falls before
this citation, shifting it by the full +40. The `doc_artifacts` table
(the citation's real target, despite being labelled just "CHECK enum" —
the original 19-line span always covered the whole table, not only the
6-line `origin` CHECK) is now at `graph.py:143-161`; the `origin` CHECK
itself is lines 152-157.

**Fix**: `graph.py:104-122` -> `graph.py:143-161`.

No other staleness found on a full top-to-bottom re-read of this page.

## Page 2 — `docs/domain/concepts/context.md`

**Citation**: `src/codecompass/graph.py:50-360` (the schema, cited
generically for sense 1, `context-graph.db`).

**Finding**: old line 50 precedes all three early hunks (offset 0); old
line 360 (inside `SkillMentionEdgeRow`) falls after the first two hunks
(+40, +30 = +70). Confirmed exact: old line 360 == new line 430
(identical text, `doc_artifact_path: str`).

**Fix**: `graph.py:50-360` -> `graph.py:50-430`.

**Minor observation (not a citation error, not fixed)**: sense 1's own
informal description — "the deterministic SQLite persistence layer of
vendors, symbols, usage, docs, and their edges" — doesn't name first-party
source symbols (`source_symbols`, new this phase) as a sixth element.
The prose isn't phrased as an exhaustive enumeration, so this doesn't rise
to a drift finding, but it's worth `context-researcher` considering
whether sense 1's gloss should be widened now that the schema has a
genuinely new node-table category (a project's own top-level declarations,
distinct from both "symbols" (vendor API surface) and "usage" (an edge)).

## Page 3 — `docs/domain/concepts/relationship-edge.md`

**Citation A**: `src/codecompass/graph.py:50-360` (schema) — same fix as
context.md: -> `graph.py:50-430`.

**Citation B**: `src/codecompass/graph.py:1184-1226` (labelled
"`rebuild_deterministic`"). Under the full hunk accounting (offset +233 by
that point in the file — confirmed exact text match at both endpoints),
this shifts to `graph.py:1417-1459`. **But this citation was already wrong
before Phase 77**, in both the old and current file: that span falls
inside `_insert_doc_relations_edges`'s tail and
`_insert_git_repositories`/`_insert_git_worktrees` (Git-topology insert
helpers), never inside `rebuild_deterministic` itself. The real
`rebuild_deterministic` function is `graph.py:935-1084`; the actual
wipe-statements for the six edge tables this page enumerates are
`graph.py:1016-1021`.
**Recommended fix**: replace `:1184-1226 (rebuild_deterministic)` with
`:935-1084 (rebuild_deterministic)`, or more precisely `:1016-1021` if a
tighter citation to just the six `DELETE FROM` statements is preferred.

**Substantive content finding (not a citation issue)**: the Definition's
own parenthetical — "(except the natural-key-upserted `vendors`/`symbols`
nodes they reference)" — is now incomplete. Phase 77 changed
`source_files` from clear-and-reinsert to upsert-by-natural-key (mirroring
`vendors`/`symbols`; the pre-Phase-77 `rebuild_deterministic` body had
`DELETE FROM source_files` in its wipe block, the current body does not).
Two of the six edge tables (`uses_edges`, `skill_mentions_edges`)
reference `source_files` by FK. **The page's central claim is unaffected
and remains true** — all six edge tables are still unconditionally wiped
and reinserted every sync (verified directly against the current
`rebuild_deterministic` body) — only the exception list needs
`source_files` added: "(except the natural-key-upserted `vendors`/
`symbols`/`source_files` nodes they reference)". I did not apply this
edit myself — the dispatch explicitly authorized it for this page
specifically, but it conflicts with this role's fixed, absolute
read-only boundary toward `docs/domain/`, which I'm treating as
controlling over a task instruction. Naming it here instead.

**Two further pre-existing, Phase-77-independent citation errors**, found
only by the full top-to-bottom re-read this task required (not by
following the audit's own line-shift reasoning, since neither is a
line-shift problem):

- `tests/test_graph.py:1426-1436` (cited for
  `test_doc_relation_enrichment_has_no_foreign_key`) lands, in both
  revisions, inside an unrelated test
  (`test_skills_index_includes_cursor_mdc_and_slash_command`'s fixture
  code). The real function is at current `tests/test_graph.py:1611-1621`.
- `architecture/overview.md:1050-1320` doesn't correspond to any
  relationship-edge content in either revision — the pre-Phase-77 file
  was only ~1102 lines total, and old 1050-1102 is a "Known limitations"
  list about adapter/extractor quality, unrelated to edges. The real
  "Context graph" section (discussing `doc_relations_edges`/
  `build_doc_relations_edges`/`mentions_artifact`/`mentions_dependency`)
  is `architecture/overview.md:688-734`, untouched by Phase 77.

## Page 4 — `docs/domain/concepts/provenance.md`

**Citations**: `graph.py:164-182` (Definition point 2, inline),
`graph.py:165-175` (Example), `graph.py:176-182` (Counterexample),
`graph.py:164-203, 515-549` (References).

**Finding**: all of `164-182`/`165-175`/`176-182`/`164-203` are shifted
+40 by Phase 77's first hunk (confirmed exact text match at every
endpoint: old 164 == new 204 `CREATE TABLE ... vendor_enrichment`; old
182 == new 222 `symbol_enrichment`'s closing `);`; old 202 == new 242
`doc_relation_enrichment`'s closing `);`).

**`515-549` was already wrong before Phase 77**, in both revisions: that
span is `_migrate_doc_artifacts_constraints`'s own docstring — a fully
unrelated migration (Phases 17/21/27/32/54c `doc_artifacts`/`kind`/
`origin` CHECK widenings), nothing to do with `symbol_enrichment.model`.
The real `_migrate_symbol_enrichment_model_column` function is at current
`graph.py:717-751` (was old `647-683`).

**Fixes**:
- `164-182` -> `204-222`
- `165-175` -> `205-215`
- `176-182` -> `216-222`
- References: `164-203, 515-549` -> `204-243, 717-751`

No other staleness found on a full top-to-bottom re-read (the
`symbol_enrichment` nullable-`model` narrative and Phase-74 migration
description remain accurate; Phase 77 didn't touch any enrichment table).

## Page 5 — `docs/domain/concepts/digest.md`

**Citation**: `src/codecompass/sync.py:160-202` (`sync_vendor`).

**Finding**: Phase 77's only `sync.py` changes before `sync_vendor` are
two 1-line-net import hunks (old lines 26, 55); `sync_vendor`'s own body
is untouched (Phase 77's real `sync.py` work is inside
`rebuild_project_graph`, much later in the file). Net offset by old line
160 is +2 — confirmed exact text match at both endpoints (old 160 ==
new 162 `graph_conn.close()`; old 202 == new 204
`side_effects=list(...)`).

**Fix**: `sync.py:160-202` -> `sync.py:162-204`.

Also verified unaffected and left alone: `core.py:66-103` (`VendorDigest`,
a file Phase 77 never touched) and `architecture/overview.md:397-576`
(Phase 77's only hunk to that file starts at old line 826, well after this
range). No other staleness found on a full top-to-bottom re-read.

## New Evidence records appended

- `planning/knowledge/codecompass-domain/EV-CTXT-015.yaml` — full hunk
  accounting + corrected line numbers for `reference.md`/`context.md`/
  `relationship-edge.md`'s schema and `rebuild_deterministic` citations.
- `planning/knowledge/codecompass-domain/EV-CTXT-016.yaml` —
  `source_files`'s Phase 77 upsert-by-natural-key change and its effect
  on `relationship-edge.md`'s own exception-list parenthetical.
- `planning/knowledge/codecompass-domain/EV-CTXT-017.yaml` — the two
  pre-existing, Phase-77-independent broken citations in
  `relationship-edge.md` (`tests/test_graph.py`, `architecture/
  overview.md`).
- `planning/knowledge/codecompass-domain/EV-CTXT-018.yaml` — corrected
  `sync.py` line numbers for `digest.md`.
- `planning/knowledge/codecompass-domain/EV-EVID-016.yaml` — corrected
  `graph.py` line numbers for `provenance.md`, including the pre-existing
  wrong migration-function citation.

## What was not done (and why)

No `docs/domain/concepts/*.md` file was edited. This role's write
boundary (`decisions/0060`) is read-only toward the approved domain
corpus "under any circumstance, including to fix something you find
wrong — even an obviously-correct one-line fix to a concept page is not
yours to make; name it instead." The dispatching task explicitly invited
a citation fix on all five pages and a content addition on
`relationship-edge.md`; I'm treating that invitation as exceeding what a
task instruction can authorize for this role and have instead named every
fix precisely, above, ready to apply without further investigation.

No genuine ambiguity requiring escalation to the actual user/domain owner
was found — every finding above was fully resolved by direct source
inspection (a real `git show`/`grep`/`Read`), not left open.
