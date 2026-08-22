# Phase 27: Register embedded vendor docs

## Scope

Found during the same `/discovery` exploration session as Phase 26, from
a direct question: "what about docs embedded in vendor packages — are
these being registered?" Confirmed by inspecting this repo's own
`vendor/` tree and `context-graph.db` directly: a cloned vendor's own
upstream repo commonly ships real documentation alongside its source —
`vendor/anthropic/src/` has `README.md`, `MIGRATION.md`, `CONTRIBUTING.md`,
`SECURITY.md`, `api.md`, `helpers.md`, `tools.md`; `vendor/rich/src/` has
~20 README translations plus `FAQ.md`/`AI_POLICY.md`/`CONTRIBUTING.md`;
`vendor/typer/src/` has a whole `docs/` folder (`features.md`,
`alternatives.md`, `index.md`, etc.). None of these ~30+ real files have a
`doc_artifacts` row — only the 7 codecompass-*generated*
`CLAUDE.md`/`OVERVIEW.md` files under `vendor/*/` do.

This is **by design, not an oversight** — `usage.py`'s
`_PROJECT_PRUNE_DIR_NAMES` (reused by `spec_docs.py`, `decisions/0037`)
explicitly includes `"vendor"`, so every scanner that walks the consuming
project's tree prunes `vendor/` entirely before looking for spec docs.
That pruning is still correct for its original purpose — Phase 15 added
`"vendor"` to this set specifically to stop every vendor's own cloned
source (self-referencing its own package name) from registering as false
"project uses this vendor" evidence (see `planning/CONTEXT.md`'s account
of that fix). This phase does **not** propose undoing that pruning — it
proposes a *separate*, narrower mechanism specifically for a vendor's own
top-level doc files, not a general re-opening of `vendor/` to every
existing project-tree scanner.

One thing already partially happens today, worth naming so this phase
doesn't duplicate it: `enrichment.py`'s material-gathering step already
*reads* a vendor's own embedded docs as raw input when synthesizing that
vendor's `technical_description` (confirmed directly — `vendor/rich/
CLAUDE.md`'s Description section cites `README.cn.md` by name). This
phase is about making those files independently *queryable graph nodes*
with their own relationships — not about enrichment's one-shot use of
them as source material, which is unaffected either way.

**Covered:**
- New `doc_artifacts.kind = 'vendor_doc'`, `origin = 'vendor_upstream'` —
  both CHECK constraints widen again (`_SCHEMA_VERSION` "3" → "4",
  extending `_migrate_doc_artifacts_constraints`'s existing
  generalized-migration pattern from Phase 21 — no new migration function
  needed, just another value in the same widening). `origin=
  'vendor_upstream'` is deliberately distinct from `codecompass_vendor`
  (codecompass-*generated* content) — this is upstream-*authored* content
  codecompass merely indexes, the same origin-semantics distinction
  `project` (Phase 21) already draws for this project's own spec docs
  versus codecompass's generated output.
- New scan step (a small addition to `sync.rebuild_project_graph`, not a
  new top-level module — this is a narrower, single-purpose scan than
  `spec_docs.scan_spec_docs`'s whole-project glob, scoped per-vendor to
  exactly `vendor/<name>/src/` root-level markdown, not a recursive
  project-wide search): for each tracked, cloned vendor, glob a small
  fixed set of common top-level doc filenames directly under its clone
  root (`README*.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`,
  `MIGRATION.md`) — deliberately *not* a recursive `**/*.md` glob (would
  sweep up a vendor's own `node_modules`/build output/nested package docs
  inside a monorepo-shaped clone) and deliberately *not* every language's
  doc-folder convention (`docs/`) in the first version — see Design
  decisions for why root-level-only is the right starting scope.
- Reuse `doc_relations_edges`/`build_doc_relations_edges`'s existing
  mechanism unchanged: a vendor doc becomes eligible as a `doc_relations_
  edges` source the same way a spec doc already is, so `mentions_
  dependency`/`mentions_artifact` edges and — gated on those, per Phase
  22's existing usage-proven-only posture — `doc_relation_enrichment`
  relationship summaries all apply to vendor docs with zero new machinery.
  This is the core reason this phase is scoped the way it is: register
  vendor docs as one more source of `doc_artifacts` rows, and every
  downstream mechanism (Phase 21's mention-detection, Phase 22's AI
  enrichment, `query relations`, `check`'s coverage-gap section) already
  works for any `doc_artifacts` row without change.
- `codecompass query skills`/`query relations` and `check`'s "Spec docs
  with no detected relations" section (or a close sibling — confirm at
  implementation time whether reusing that exact section or adding a
  parallel "Vendor docs with no detected relations" one reads better,
  since `kind='vendor_doc'` isn't a `kind='spec_doc'` row) surface these
  new artifacts alongside existing ones.

**Explicitly deferred / out of scope:**
- Recursive doc-folder scanning (`docs/**/*.md` inside a vendor's clone,
  the way `spec_docs.py` does for the *consuming* project) — root-level
  files only for v1 of this feature; see Design decisions.
- AI enrichment *of the vendor doc's own content* (a technical description
  of what the vendor doc itself says, distinct from Phase 22's
  relationship-summary enrichment, which already applies once the doc
  artifact exists) — out of scope; `doc_relation_enrichment` already
  covers "how does this vendor doc relate to X," which is the actual gap
  found. A vendor doc's *own* standalone summary is a different, unasked-
  for feature.
- Any change to `enrichment.py`'s existing one-shot use of vendor docs as
  raw description-synthesis material — unaffected, continues exactly as
  today.

## Design decisions

**Root-level doc files only, not a recursive scan of a vendor's own
`docs/` folder.** Considered mirroring `spec_docs.py`'s glob set
(`docs/**/*.md`, etc.) applied inside each vendor's clone. Rejected for
v1: a vendor's own clone is arbitrary upstream content, not something
this project controls the shape of — `typer`'s `docs/` folder alone has 8
files, and a larger dependency could have hundreds nested arbitrarily
deep, none of it curated the way this project's own `docs/` is. Starting
with a small, fixed, well-known top-level filename set (the same kind of
files essentially every real-world repo has at its root, regardless of
language/ecosystem) is a conservative, high-signal starting scope that
avoids indexing noise (a vendor's internal design docs, translated
READMEs at scale, etc.) without needing per-vendor configuration. Revisit
recursive scanning only if root-level files prove insufficient in
practice.

**A per-vendor scan folded into `sync.rebuild_project_graph`, not a new
top-level module.** `spec_docs.py` earned its own module because it scans
the *whole consuming project* with a broad glob set and its own exclusion
logic. This phase's scan is narrower and inherently vendor-scoped (one
fixed filename set, applied once per tracked vendor's already-known clone
root) — closer in shape to `collect_vendor_doc_artifacts` (which already
builds `doc_artifacts` rows per vendor in `doc_mapping.py`) than to
`spec_docs.scan_spec_docs`. Implement as a sibling function next to
`collect_vendor_doc_artifacts` in `doc_mapping.py`, not a new module,
unless the actual implementation reveals it doesn't fit that shape.

**Reuse `doc_relations_edges`/enrichment unchanged, register don't
rebuild.** The whole point of this phase is that Phase 21/22's machinery
already generalizes to any `doc_artifacts` row — the fix is purely "make
these files exist as rows," not "build parallel detection/enrichment
paths for vendor docs." Keeping the *kind* of the improvement small and
targeted (one new scan producing rows in the existing shape) is what lets
this stay a contained phase rather than growing into a second parallel
enrichment surface.

## Files

- `src/codecompass/graph.py` — CHECK-constraint widening (`kind=
  'vendor_doc'`, `origin='vendor_upstream'`), `_SCHEMA_VERSION` "3"→"4".
- `src/codecompass/doc_mapping.py` — new vendor-doc scan function
  (sibling to `collect_vendor_doc_artifacts`).
- `src/codecompass/sync.py` — wire the new scan into
  `rebuild_project_graph`, feeding its output into the existing
  `doc_artifacts`/`build_doc_relations_edges` pipeline unchanged.
- `src/codecompass/cli.py` — `check`'s coverage-gap section (confirm
  scope at implementation time, per Covered above).
- `architecture/overview.md` — "Context graph" section update.
- `decisions/` — new ADR: the root-level-only scope decision and the
  `vendor_upstream` vs. `codecompass_vendor`/`project` origin distinction
  are both non-obvious tradeoffs worth recording (`CLAUDE.md` §2).
- `tests/test_doc_mapping.py`, `tests/test_graph.py`, `tests/test_sync.py`
  (or wherever `rebuild_project_graph`'s integration tests live).

## Verification

- `pytest`/`ruff check .` — full suite passes.
- Manual, against this repo itself (the established dogfooding pattern):
  re-run a whole-project `sync`, confirm `vendor/anthropic/src/README.md`
  (and siblings) now appear as `doc_artifacts` rows with
  `kind='vendor_doc'`, `origin='vendor_upstream'`; confirm `query
  relations` works against one of them; confirm a `check` run surfaces
  them in whatever coverage-gap section this phase lands on; confirm
  `vendor/`'s existing false-positive-usage exclusion (Phase 15's fix)
  still holds — this phase's new scan must not resurrect that bug by
  accidentally feeding vendor doc content into usage detection, which it
  shouldn't, since it only ever produces `doc_artifacts` rows, never
  `uses_edges`.
