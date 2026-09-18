# Context packet: `doc_artifacts.origin` value for externally-sourced, pinned reference material

Feature: `doc-origin-pinned-reference` | Context gap: `CG-005` | Design: `design.md` (`status: APPROVED`, approved by "project owner (lead standing in for this dogfooding run)")

This packet is a compacted implementation input, not a copy of `design.md`.
It is deliberately smaller — read `design.md` only if this packet turns out
to be insufficient, and log the gap in `packet-sufficiency.md`.

## 1. Goal

`doc_artifacts.origin` is meant to record where a documentation artifact
actually came from, but today cannot distinguish a project's own
hand-authored docs from externally-sourced, tool-ingested reference
material pinned at an upstream commit — both currently read
`origin='project'`. The concrete driving instance is the six
`hledger-tag-query-*.md` files under
`planning/reference-projects/ledgerkit/reference-experiment/extracted/`,
pinned at hledger commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`. Add a
schema-level classification for this material and make CodeCompass assign
it automatically. (`CG-005`, `OBS-DOCORIGIN-001`)

## 2. Approved semantics (compacted)

- `doc_artifacts.origin` is a closed CHECK enum, widened exactly twice
  before (Phase 21 added `'project'`, Phase 27 added `'vendor_upstream'`)
  via one generic migration function that drops and recreates
  `doc_artifacts` on a `_SCHEMA_VERSION` bump — safe because the table is
  fully repopulated on every whole-project sync. Add a sixth value the
  same way: `'pinned_reference'`. (`CL-DOCORIGIN-001`, `EV-DOCORIGIN-001`)
- Every other real `origin` consumer in `src/codecompass/` was traced
  (write sites in `doc_mapping.py`, read sites in `doc_mapping.py`/
  `cli.py`, kind-filtered queries in `graph.py`) and confirmed
  unaffected by adding a new enum value — each write site is an
  unconditional per-caller constant, and each read site matches an
  explicit closed value/pair, falling through unchanged for any value it
  doesn't name. No consumer other than the write site itself needs to
  change. (`CL-DOCORIGIN-001`, `DE-DOCORIGIN-001`, `EV-DOCORIGIN-003/004/005`)
- The ingested material already carries a uniform, mechanically
  parseable YAML frontmatter block (`reference`, `source_url`,
  `requested_ref`, `resolved_commit`, `fetch_method`, `path`, `lines`,
  `content_hash`, `extracted_at`) — a real signal `scan_spec_docs` does
  not read today (it only ever finds an H1 or falls back to the filename
  stem; frontmatter is inert to it, not merely unread). No path- or
  config-based signal exists as an alternative. (`CL-DOCORIGIN-002`,
  `EV-DOCORIGIN-002/006/007`)
- **Decided** (`DEC-DOCORIGIN-001`, agrees with `CL-DOCORIGIN-001`,
  approved): name the value `pinned_reference`, scoped as a provenance
  *class* ("externally-sourced reference material, revision-pinned and
  materialized into the project tree by a tool") rather than narrowed to
  "git" in the name — the fetch mechanism is a separate concern from the
  provenance class the column records, so no further schema change would
  be needed if a non-git source is ever built. Detection is **automatic**:
  teach `scan_spec_docs` to parse a leading YAML frontmatter block and
  check for both a `resolved_commit` key and a `source_url` key — not a
  manual/config-driven override, because the two-field signal is real,
  mechanical, and uniquely present in ingested content, whereas a manual
  flag is weaker (a human could forget it).
- Reusing `vendor_upstream` for this material is ruled out, and not just
  on semantic grounds: `DocArtifactRow.vendor_name` is resolved via an
  unguarded dict subscript (`vendor_ids[d.vendor_name]`, no `.get()`, no
  `try`/`except`) inside `_insert_doc_artifacts` — a `vendor_name` naming
  a vendor absent from `vendors` (exactly this material's situation, no
  `vendor.toml` entry) raises an **uncaught `KeyError` that aborts the
  sync**. (`CL-DOCORIGIN-003`, `DE-DOCORIGIN-003`, `EV-DOCORIGIN-003`,
  `OBS-DOCORIGIN-011`)
- No explicit backfill/migration step is needed for already-synced
  databases: `doc_artifacts` is dropped and fully repopulated on every
  whole-project sync, so the new classification is applied automatically
  the next time affected files are synced. (`DEC-DOCORIGIN-001`)

## 3. Requirements (verbatim, all `status: approved`, all under `DEC-DOCORIGIN-001`)

**REQ-DOCORIGIN-001**
> `doc_artifacts.origin`'s CHECK constraint MUST accept a new value,
> 'pinned_reference', added via the existing
> `_migrate_doc_artifacts_constraints` mechanism (one more
> `_SCHEMA_VERSION` bump), following the exact Phase 17/21/27 precedent.
> No other origin consumer in `src/codecompass/` requires any change for
> this addition alone.

**REQ-DOCORIGIN-002**
> `scan_spec_docs` MUST assign `origin='pinned_reference'` (instead of
> 'project') to a `dev-docs/**/*.md`-glob-matched file whose leading
> content is a YAML frontmatter block (delimited by `---` lines) that
> contains both a `resolved_commit` key and a `source_url` key. A file
> with no such frontmatter, or frontmatter missing either key, MUST keep
> the existing `origin='project'` behaviour unchanged.

**REQ-DOCORIGIN-003**
> A new test fixture (a frontmatter-bearing .md file under a test
> project's dev-docs/ tree) MUST exercise `scan_spec_docs`'s new
> `origin='pinned_reference'` branch directly, closing the real,
> currently-missing test-coverage gap `CL-DOCORIGIN-002`/`EV-DOCORIGIN-008`
> identified. Every existing test asserting `origin='project'` for
> frontmatter-free fixtures MUST continue to pass unchanged.

## 4. Behavioural examples (verbatim, Given/When/Then)

**REQ-DOCORIGIN-001's example:**
```
Given a fresh context-graph.db at the previous schema version
When codecompass sync runs against a project containing at least one
  file that will be classified with origin='pinned_reference'
Then the database migrates to the new schema version and the row is
  inserted successfully, with no CHECK constraint violation.
```

**REQ-DOCORIGIN-002's example:**
```
Given a file under a project's dev-docs/ tree beginning with:
  ---
  reference: hledger
  source_url: https://github.com/simonmichael/hledger
  resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
  ---
When scan_spec_docs processes it
Then the resulting doc_artifacts row has origin='pinned_reference'.

Given an ordinary hand-authored dev-docs/*.md file with no frontmatter
When scan_spec_docs processes it
Then the resulting row has origin='project', exactly as today.
```

**REQ-DOCORIGIN-003's example:**
```
Given the existing test_spec_docs.py test suite
When the new frontmatter-detection branch is added
Then a new test (e.g. test_scan_spec_docs_pinned_reference_frontmatter)
  asserts origin='pinned_reference' for a frontmatter-bearing fixture,
  and every pre-existing origin='project' assertion still passes.
```

## 5. Invariants

- No `origin` consumer other than `scan_spec_docs` itself (the write
  site) needs to change for this addition. (`REQ-DOCORIGIN-001`,
  `CL-DOCORIGIN-001`)
- `vendor_upstream` is never reused for this material, in any form — it
  stays exactly as it is; reuse risks a confirmed `KeyError` crash at
  sync time given this material's actual shape. (`CL-DOCORIGIN-003`,
  `DEC-DOCORIGIN-001`)
- Detection is automatic/mechanical (frontmatter parsing), never a
  manual or config-driven override. (`DEC-DOCORIGIN-001`)
- A file with no frontmatter, or frontmatter missing either
  `resolved_commit` or `source_url`, MUST keep `origin='project'`
  unchanged. (`REQ-DOCORIGIN-002`)
- Every existing `origin='project'` test assertion for frontmatter-free
  fixtures MUST continue to pass. (`REQ-DOCORIGIN-002`,
  `REQ-DOCORIGIN-003`, `EV-DOCORIGIN-008`)
- No explicit backfill/migration step for already-synced databases — the
  drop-and-recreate-on-sync mechanism already handles it.
  (`DEC-DOCORIGIN-001`)

## 6. Relevant architecture (pointers, not an essay)

- The `doc_artifacts.origin`/`kind` CHECK-enum widening pattern: one
  generic, version-comparison-driven migration function handles any
  prior schema version by drop-and-recreate, not a bespoke per-value
  migration — established Phase 17 (`kind` only), extended Phase 21
  (`kind`+`origin`), extended Phase 27 (`kind`+`origin` again). This
  feature follows that precedent exactly for a sixth `origin` value.
- The reference-ingestion pipeline
  (`planning/reference-projects/ledgerkit/reference-experiment/`) is the
  one existing real producer of this material's shape; it is
  Git-commit-pinned only today (no working non-Git fetch path), which is
  why the new value's *name* is deliberately not scoped to "git" even
  though its only current producer is git-based. (`CL-DOCORIGIN-004`,
  `EV-DOCORIGIN-009`)
- Detection is purely path-based today (`dev-docs/**/*.md` glob, Phase
  49) with zero content inspection; this feature adds the first
  content-level (frontmatter) signal `scan_spec_docs` has ever used.

## 7. Relevant symbols / files / dependencies

- `src/codecompass/graph.py` — `doc_artifacts` table CHECK-enum
  definition; `_migrate_doc_artifacts_constraints` (the migration
  mechanism to extend); `DocArtifactRow` dataclass; `_insert_doc_artifacts`
  (the unguarded `vendor_ids[d.vendor_name]` lookup, relevant only to
  confirm why `vendor_upstream` must not be reused); `spec_docs_without_relations`
  / `vendor_docs_without_relations` (kind-filtered, confirmed unaffected).
- `src/codecompass/spec_docs.py::scan_spec_docs` — the write site to
  change: currently assigns `origin="project"` as an unconditional
  literal constant; needs a frontmatter-parsing branch. `_extract_title`
  and `_DEFAULT_GLOBS` in the same file are relevant context but
  unaffected (title extraction already ignores frontmatter cleanly;
  the glob is unchanged).
- `src/codecompass/doc_mapping.py` — `collect_vendor_doc_artifacts`,
  `collect_vendor_upstream_doc_artifacts` (other unconditional `origin`
  write sites, confirmed unaffected), `build_doc_relations_edges`'
  skill-preference branch (the one `origin`-reading branch, scoped to
  Skill-kind rows only, confirmed unaffected).
- `src/codecompass/cli.py` — `_print_coverage_gap_sections`,
  `query_skills`, `_graph_backed_undo_paths` (three `origin`-reading
  sites, all scoped to Skill-kind rows or an explicit unrelated
  two-value list; confirmed unaffected).
- `tests/test_spec_docs.py` — existing `origin=="project"` assertions
  (frontmatter-free fixtures); add the new
  `test_scan_spec_docs_pinned_reference_frontmatter`-style test here.
- `tests/test_doc_mapping.py` — hand-constructed `DocArtifactRow`
  fixtures for unrelated matching-logic tests; not scan_spec_docs
  coverage, no change needed.
- Real example frontmatter shape (for building a test fixture):
  `planning/reference-projects/ledgerkit/reference-experiment/extracted/hledger-depth-query-manual-section.md`
  and `.../hledger-query-hs-matchesaccount.md` (frontmatter keys:
  `reference`, `source_url`, `requested_ref`, `resolved_commit`,
  `fetch_method`, `path`, `lines`, `content_hash`, `extracted_at`).
- No new dependency is named or required by any record in this
  knowledge base — a frontmatter-parsing approach (hand-rolled `---`
  delimiter + key scan, vs. a YAML library) is not resolved here; see
  §10.

## 8. Existing tests

- `tests/test_spec_docs.py` — `test_scan_spec_docs_finds_root_level_named_files`
  and siblings assert `origin == "project"` against plain,
  frontmatter-free fixtures written via a local `_write()` helper; these
  must keep passing unchanged.
- `tests/test_doc_mapping.py` — multiple hand-constructed
  `DocArtifactRow(origin="project")` inputs exercising
  `build_doc_relations_edges`'s matching logic; unrelated to
  `scan_spec_docs`'s own assignment behaviour, no coverage either way.
- No existing test exercises a frontmatter-bearing fixture or asserts
  any value other than `project` for `scan_spec_docs` output — this is
  the gap `REQ-DOCORIGIN-003` closes. (`EV-DOCORIGIN-008`)

## 9. Non-goals

- Changing any `origin` consumer other than the write site itself.
- Extending `pinned_reference` (or an equivalent) to `vendor_doc`-kind
  rows in this phase — `vendor_upstream` stays exactly as it is.
- Implementing a non-Git ("url"-sourced) fetch method in the reference
  pipeline — the name is chosen to not require a future schema change if
  this is ever built, but building it is out of scope here.
- Reusing `vendor_upstream` for this material in any form.
- A manual/config-driven override mechanism for assigning
  `pinned_reference` — rejected in favour of automatic frontmatter
  detection.
- An explicit backfill/migration step for already-synced databases.
- Retroactively auditing/fixing every file in the repository for
  correct `origin` classification beyond the `CG-005` material itself.

## 10. Deliberate upstream differences

**None apply to this feature.** Unlike a feature such as `hledger
depth:` semantics, this is an internal CodeCompass schema/classification
gap with no external "upstream" whose behaviour is being matched or
deviated from. No Decision record in this knowledge base addresses an
upstream-vs-target divergence, so there is nothing to state here beyond
this plain confirmation. (`design.md` §12)

## 11. Unresolved questions (honestly disclosed)

- **Partial-key frontmatter is not covered by any record.** `REQ-DOCORIGIN-002`
  states that a frontmatter block containing only one of `resolved_commit`
  and `source_url` keeps `origin='project'` (both keys are required for
  the new classification) — but no Observation, Evidence, or Claim in
  this knowledge base addresses whether such partial frontmatter actually
  occurs in practice anywhere, and `DEC-DOCORIGIN-001` was not asked to
  resolve it. Implement exactly the both-keys rule `REQ-DOCORIGIN-002`
  states; do not generalize beyond it without a new Observation/Claim
  first. (`design.md` §8, §9)
- **Frontmatter-parsing mechanism is unspecified.** No record says
  whether to hand-roll a minimal `---`-delimited key scan (matching this
  project's existing precedent of avoiding new parsing dependencies where
  a hand-rolled check suffices, e.g. `reference_pipeline.py`'s
  `load_references_toml`) or use a YAML library. This is an
  implementation-mechanism choice, not a behavioural ambiguity the
  knowledge base left open — `REQ-DOCORIGIN-002`'s observable contract
  (which two keys, which values of `origin` result) is unambiguous either
  way.

## 12. Provenance references

Every id this packet draws from:

- **Observations:** OBS-DOCORIGIN-001, OBS-DOCORIGIN-002, OBS-DOCORIGIN-003,
  OBS-DOCORIGIN-004, OBS-DOCORIGIN-005, OBS-DOCORIGIN-006, OBS-DOCORIGIN-007,
  OBS-DOCORIGIN-008, OBS-DOCORIGIN-009, OBS-DOCORIGIN-010, OBS-DOCORIGIN-011
- **Evidence:** EV-DOCORIGIN-001, EV-DOCORIGIN-002, EV-DOCORIGIN-003,
  EV-DOCORIGIN-004, EV-DOCORIGIN-005, EV-DOCORIGIN-006, EV-DOCORIGIN-007,
  EV-DOCORIGIN-008, EV-DOCORIGIN-009
- **Claims:** CL-DOCORIGIN-001, CL-DOCORIGIN-002, CL-DOCORIGIN-003,
  CL-DOCORIGIN-004
- **Derivations:** DE-DOCORIGIN-001, DE-DOCORIGIN-002, DE-DOCORIGIN-003,
  DE-DOCORIGIN-004
- **Decision:** DEC-DOCORIGIN-001
- **Requirements:** REQ-DOCORIGIN-001, REQ-DOCORIGIN-002, REQ-DOCORIGIN-003
- **Context gap:** CG-005 (`planning/context-gaps/inbox.md:267-363`)
