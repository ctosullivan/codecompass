# Phase 73: `mentions_artifact` filename-based matching (closes `CG-006`) — plan

**Status:** in progress (2026-09-27).

First concrete Priority A deliverable (`planning/ROADMAP.md`'s "Post-v1
priorities (A-F)" table, `decisions/0062`), continuing directly from
Phase 72's realignment per the user's own instruction to proceed to
implementation. Not a resumption of old Phase 48's broad scope —
exactly the "smallest justified fix" class this project has repeatedly
funded without a fresh GATE ceremony (Phase 49/`CG-002`, Phase 55b/
`CG-004`), already named by `decisions/0062` as informing Priority A by
name.

## 0. What this phase is, and isn't

Closes `CG-006` (`planning/context-gaps/inbox.md`): `mentions_artifact`
detection only word-boundary-matches a target doc's *title* (`.name`),
never its *filename* — a real, independently-confirmed gap found on the
exact real-world pair `CG-004`'s own fix was motivated by
(`17-query-semantics-brief.md` cites `07-query-regex.md` by filename,
never by title; zero edge produced even after `CG-004`'s fix landed).
`CG-006`'s own "smallest candidate" is explicit and narrow: extend the
existing per-artifact matching to also try each target's filename
(basename, and basename-without-extension) alongside its existing
`name` check — no new table, no new relation kind, no widened
eligibility (artifacts with no `name` at all stay excluded, unchanged).

**Not in scope**: widening which artifacts are eligible match targets
(only already-named artifacts, exactly as today); a general filename-
matching mode for other relation kinds (`mentions_dependency`); any
graph-capability/schema change (this is `detection-improvement`,
Stage-C-scale per `CG-006`'s own classification).

## 1. Scope

`src/codecompass/doc_mapping.py::build_doc_relations_edges`: for each
`named_artifacts` target not yet matched by its `.name`, also try its
path's filename (`Path(artifact.path).name`, e.g. `"07-query-regex.md"`)
and stem (`Path(artifact.path).stem`, e.g. `"07-query-regex"`) as
additional word-boundary patterns, each gated through the existing
`spec_docs._is_specific_enough` noise filter (reused, not duplicated —
the same "reject a single bare generic word" rule that already protects
title-based matching from `README.md`/`index.md`-style false positives
applies identically here: a filename like `readme.md` must not become a
universal match target any more than the bare title "readme" already
isn't). Same relation kind (`mentions_artifact`), same self-mention
exclusion (`artifact.path == row.path`), same chunk-attribution helper.

**Known, disclosed limitation** (not fixed by this phase): two files
with the identical basename in different directories are indistinguishable
by this matching strategy — a citation of one could theoretically match
the other. Noted in the function's own docstring, not silently left
undocumented; the existing title-based matching has an analogous
limitation (two docs sharing an identical title) and this project has
never treated that as blocking either.

### 1.1 Follow-on fix, found by `docs-maintainer`'s independent review

`src/codecompass/relation_enrichment.py::_relation_needle` re-derives
the match string for excerpt-centering during enrichment, but was not
updated for this phase's own widened detection — a headerless source
doc (no chunk to prefer) citing a target only by filename/stem would
silently fall back to the worse first-N-characters excerpt, reintroducing
the exact failure mode Phase 28 fixed. Renamed to `_relation_needles`
(plural), now tries every candidate string in the same priority order
detection does (name, then filename, then stem), using whichever is
still found in the current text. A direct, in-scope completeness fix
for this same phase's own change (`L-055`'s own lesson — check every
consumer of a widened match, not just the primary edge-creation path —
applied here to a different sub-system), not deferred to a later phase.

## 2. Files created/changed

- `src/codecompass/doc_mapping.py` — `build_doc_relations_edges`
  extended; docstring updated.
- `src/codecompass/relation_enrichment.py` — `_relation_needle` renamed
  `_relation_needles`, widened to try filename/stem too (§1.1 follow-on
  fix).
- `tests/test_doc_mapping.py` — new unit test(s): filename match
  produces an edge; stem-only match produces an edge; a generic
  filename (`readme.md`) does not; the existing title-match tests are
  unaffected (title still tried first/independently).
- `tests/test_sync.py` — new integration test through the real
  production call site (`rebuild_project_graph`), per `CLAUDE.md` §1's
  own requirement whenever a phase adds behavior to a function with a
  real call site — mirrors
  `test_rebuild_project_graph_relates_two_spec_docs_to_each_other`'s own
  shape exactly, using a filename citation instead of a title citation.
- `tests/test_relation_enrichment.py` — new regression test for the
  §1.1 follow-on fix (headerless doc, filename-only citation, excerpt
  correctly centers on the filename mention).
- `docs/cli-reference.md` / `architecture/` — only if the consistency
  check (step 4 below) finds a stale description of `mentions_artifact`
  detection's own current matching strategy.
- Standard closeout: `planning/CONTEXT.md`, `CHANGELOG.md`,
  `planning/ROADMAP.md` (Phase 73 row; `CG-006` status flip in
  `context-gaps/inbox.md`), retro, drift audit report, learning triage.

## 3. Verification

1. `tests/test_doc_mapping.py`'s new unit test(s) pass, exercising
   `build_doc_relations_edges` directly.
2. `tests/test_sync.py`'s new integration test passes, exercising the
   real call site (`sync.py::rebuild_project_graph`) — not just the
   isolated function, per `CLAUDE.md` §1.
3. Every existing `test_doc_mapping.py`/`test_sync.py` test involving
   `mentions_artifact` still passes unchanged (no regression to
   title-based matching, self-mention exclusion, or chunk attribution).
4. `scripts/check_user_docs.py --strict` and
   `scripts/check_knowledge_base.py` pass.
5. Full `pytest` — expect 625 + new tests, 2 skipped.
6. `ruff check .` clean.
7. `docs-reconstructor` per-phase drift audit: `NO DRIFT` expected
   (internal detection-heuristic change, no CLI/config/output-format
   change) — but checked directly, not assumed.
8. `CG-006`'s own status in `planning/context-gaps/inbox.md` flipped to
   `promoted-to-roadmap`, with a `promoted.md` line added once this
   phase's closeout commit lands (matching the `CG-002`/`CG-004`
   precedent exactly).
9. Standard closeout: retro, `knowledge-curator` learning triage,
   `release-phase-auditor` DoD pass. **Per Phase 72's own `L-056`: the
   `docs-reconstructor` dispatch prompt must explicitly state the
   required persisted report path
   (`planning/retros/_drift-audit-phase-73.md`).**

## 4. Deferred (explicitly out of scope for this phase)

- `CG-001` (task-oriented retrieval edges) and `CG-007` (execution-path/
  symbol-level cross-references) — genuinely harder, less-evidenced
  Priority A candidates; not bundled in, per this project's own
  narrow-scope discipline.
- Any change to `mentions_dependency` matching (vendor names) — CG-006
  is specifically about `mentions_artifact`'s target-matching strategy.
- A `vendor.toml`-style configurable matching mode — no evidence yet
  that hard-coded filename/stem matching is insufficient.
