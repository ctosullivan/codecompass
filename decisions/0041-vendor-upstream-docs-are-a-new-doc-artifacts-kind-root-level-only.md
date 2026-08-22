# 0041. Vendor-embedded upstream docs are a new `doc_artifacts` kind, root-level files only

## Status

Accepted

## Context

Phase 27 (`planning/phase-27-register-embedded-vendor-docs.md`) was found
during the same `/discovery` exploration session as Phase 26, from a
direct question: "what about docs embedded in vendor packages — are these
being registered?" Confirmed by inspecting this repo's own `vendor/` tree
and `context-graph.db` directly: a cloned vendor's own upstream repo
commonly ships real documentation alongside its source —
`vendor/anthropic/src/` has `README.md`, `MIGRATION.md`,
`CONTRIBUTING.md`, `SECURITY.md`, `api.md`, `helpers.md`, `tools.md`;
`vendor/rich/src/` has ~20 README translations plus
`FAQ.md`/`AI_POLICY.md`/`CONTRIBUTING.md`; `vendor/typer/src/` has a whole
`docs/` folder. None of these ~30+ real files had a `doc_artifacts` row —
only the 7 codecompass-*generated* `CLAUDE.md`/`OVERVIEW.md` files under
`vendor/*/` did.

This is by design, not an oversight: `usage.py`'s
`_PROJECT_PRUNE_DIR_NAMES` (reused by `spec_docs.py`, `decisions/0037`)
includes `"vendor"`, so every scanner that walks the consuming project's
tree prunes `vendor/` entirely, specifically to stop a vendor's own cloned
source (self-referencing its own package name) from registering as false
"project uses this vendor" evidence (Phase 15). That pruning is still
correct for its original purpose and this phase does not undo it — it
adds a *separate*, narrower mechanism specifically for a vendor's own
top-level doc files.

Two design questions needed settling before implementation:

1. **How much of a vendor's own doc tree should be indexed?** A vendor's
   clone can range from a single `README.md` to a whole `docs/` folder
   (`typer`) to dozens of translated READMEs sitting at the root
   (`rich`). Mirroring `spec_docs.py`'s recursive glob set
   (`docs/**/*.md`, etc.) inside each vendor's clone was the obvious
   first idea.
2. **What `origin` value does an indexed vendor doc get?** The existing
   `doc_artifacts.origin` values are `codecompass_tool`,
   `codecompass_vendor` (both codecompass-*generated*), `third_party` (a
   Skill/`.mdc` rule this project didn't write), and `project`
   (`decisions/0037` — this project's own hand-authored spec docs).

## Decision

**Root-level doc files only, matched against a small fixed filename set
(`README*.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`,
`MIGRATION.md`), no recursion into subdirectories.** A vendor's own clone
is arbitrary upstream content, not something this project controls the
shape of — `typer`'s `docs/` folder alone has 8 files, and a larger
dependency could have hundreds nested arbitrarily deep, none of it curated
the way this project's own `docs/` is. Starting with a small, fixed,
well-known top-level filename set (the kind of files essentially every
real-world repo has at its root, regardless of language or ecosystem) is
a conservative, high-signal starting scope that needs no per-vendor
configuration. `README*.md` (rather than the bare `README.md`) is a
deliberate small widening beyond the literal filename set named above, so
that a vendor whose canonical README isn't literally `README.md`
(`README.rst`, a bare `README`) doesn't need special-casing here — the
accepted cost is that a vendor with root-level translated READMEs (`rich`)
gets all of them indexed too, not just the English one. Implemented as
`doc_mapping.collect_vendor_upstream_doc_artifacts`, a sibling function to
`collect_vendor_doc_artifacts` rather than a new module — this scan is
narrower and inherently vendor-scoped (one fixed filename set applied once
per tracked vendor's already-known clone root), closer in shape to that
function than to `spec_docs.scan_spec_docs`'s whole-project glob.

The clone root globbed against is `vendor/<name>/src/` — where
`sync.sync_vendor`/`source_resolution.resolve_and_clone` actually write a
vendor's cloned source — not `vendor/<name>/` itself, which holds only
codecompass's own generated `CLAUDE.md`/`OVERVIEW.md`/`FILETREE.md`/
`DEPTREE.md`.

**A new `doc_artifacts.kind='vendor_doc'` and `origin='vendor_upstream'`,
both CHECK constraints widened again** (`_SCHEMA_VERSION` "3" → "4",
extending `_migrate_doc_artifacts_constraints`'s existing generalized
widening pattern from Phase 21 — no new migration function, just another
value in the same drop-and-recreate). `origin='vendor_upstream'` is
deliberately distinct from both `codecompass_vendor` (codecompass-
*generated* content — `CLAUDE.md`/`OVERVIEW.md`) and `project`
(`decisions/0037` — this *consuming* project's own hand-authored spec
docs): a vendor's embedded doc is upstream-*authored* content codecompass
merely indexes, belonging to neither existing bucket. Reusing
`codecompass_vendor` would have falsely implied codecompass wrote it;
reusing `project` would have conflated a third-party library's own docs
with this project's own.

**Reuse `doc_relations_edges`/enrichment unchanged — register, don't
rebuild.** A vendor doc becomes an eligible `mentions_artifact` *target*
the same way a per-vendor `CLAUDE.md`/`OVERVIEW.md` already is (added to
`build_doc_relations_edges`'s `other_doc_artifact_rows` argument in
`sync.rebuild_project_graph`), with zero changes to
`build_documents_edges`/`build_routes_via_edges`/`build_doc_relations_
edges` themselves. It is never a relation *source* — spec docs are the
only source `build_doc_relations_edges` ever scans from
(`decisions/0037`'s spec-doc-outward-only posture), which a vendor doc
does not change.

## Alternatives considered

- **Recursive doc-folder scanning** (`docs/**/*.md` inside a vendor's
  clone, mirroring `spec_docs.py`'s glob set applied to the *consuming*
  project). Rejected for v1: unlike this project's own `docs/`, a vendor's
  `docs/` folder shape is entirely outside this project's control and
  could be arbitrarily large/deep/noisy (a vendor's internal design docs,
  translated READMEs at scale inside a nested folder, etc.) — the same
  "too broad" reasoning `decisions/0037` already applied to rejecting a
  catch-all `**/*.md` default for spec docs, just one level further out.
  Revisit only if root-level files prove insufficient in practice.
- **A new top-level module** (`vendor_docs.py`), mirroring `spec_docs.py`.
  Rejected: `spec_docs.py` earned its own module because it scans the
  *whole consuming project* with a broad glob set and its own exclusion
  logic; this phase's scan is narrower and inherently vendor-scoped (one
  fixed filename set, applied once per tracked vendor's already-known
  clone root) — closer in shape to `collect_vendor_doc_artifacts`
  (already in `doc_mapping.py`) than to `spec_docs.scan_spec_docs`.
- **Reuse `origin='codecompass_vendor'`** for indexed vendor docs, since
  they live under the same `vendor/<name>/` tree codecompass already owns
  as a directory. Rejected — that value specifically means "codecompass
  generated this file's content" (`CLAUDE.md`/`OVERVIEW.md`), and a vendor
  doc's *content* is entirely upstream-authored; codecompass only chose to
  clone the repository and index this particular file. Blurring that
  distinction would make `origin='codecompass_vendor'` an unreliable
  signal for "was this text AI/template-generated," which
  `enrichment.py`'s existing material-gathering step (and any future
  reader) can currently assume.
- **Fold "Vendor docs with no detected relations" into the existing "Spec
  docs with no detected relations" `check` section**, since both are
  "some doc artifact with zero detected relations." Rejected: the two
  sections check opposite `doc_relations_edges` columns —
  `spec_docs_without_relations` looks at a spec doc's own *outgoing*
  mentions (`source_doc_artifact_id`, the only role a spec doc plays),
  while a vendor doc is only ever a relation *target*
  (`target_doc_artifact_id`) and never a source. A single merged query
  checking "no relation row at all, in either column" would be correct by
  accident for spec docs (which never appear as a target) but silently
  wrong in spirit — the heading "Spec docs with no detected relations"
  would no longer describe what the listed paths actually are. A parallel
  `graph.vendor_docs_without_relations` (checking `target_doc_artifact_id`
  specifically) keeps both sections' meaning precise at the cost of one
  more small function and one more report line.

## Consequences

- `enrichment.py`'s existing one-shot use of a vendor's embedded docs as
  raw material for synthesizing that vendor's `technical_description` is
  completely unaffected — it already reads these files directly off disk
  today (confirmed: `vendor/rich/CLAUDE.md`'s Description section cites
  `README.cn.md` by name) and continues to, independent of whether they
  also have a `doc_artifacts` row now.
- A vendor doc's *own* standalone AI-generated summary (a description of
  what the doc itself says, as opposed to Phase 22's "how does this doc
  relate to X" relationship summary) is not in scope here and not
  implemented — `doc_relation_enrichment` already covers the actual gap
  this phase closes ("is any project spec doc mechanically related to
  this vendor doc"); a standalone per-doc summary is a distinct, unasked-
  for feature.
- A vendor's embedded doc that doesn't match the fixed filename set (an
  unconventionally named root file, or anything inside a subdirectory —
  `typer`'s `docs/features.md`, for instance) stays invisible to
  `doc_artifacts`/`doc_relations_edges`/`query relations`/`check`'s
  coverage-gap section, the same accepted-tradeoff shape
  `decisions/0037` already documents for spec docs missing the default
  glob set.
- `README*.md` matching every root-level README variant, not just the
  canonical one, means a vendor with several language variants at its
  clone root (`rich`) gets all of them indexed as separate `doc_artifacts`
  rows, each independently eligible as a `mentions_artifact` target. This
  is a deliberate simplicity-over-precision tradeoff (see Decision above),
  not a bug; revisit only if it proves to be real query-result noise in
  practice.
