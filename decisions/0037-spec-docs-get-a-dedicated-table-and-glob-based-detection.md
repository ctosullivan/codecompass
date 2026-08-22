# 0037. Spec docs are a new `doc_artifacts`/`doc_relations_edges` shape, detected by fixed default globs

## Status

Accepted

## Context

Phase 21 (`planning/phase-21-spec-doc-detection-and-relationship-graph.md`)
adds the first half of a new three-way relationship feature requested
alongside the path-to-v1.0 roadmap: a project's own human-authored spec
docs (README, `ARCHITECTURE.md`, `docs/**/*.md`, `decisions/**/*.md`, etc.)
mechanically linked to the two node types the context graph already knows
about — tracked vendors and generated/third-party doc artifacts (Skills,
`.mdc` rules, per-vendor `CLAUDE.md`/`OVERVIEW.md`). Part 2 (AI enrichment
of the edges this phase detects) is deliberately deferred to Phase 22:
enrichment should only ever run over relationships mechanical detection has
already proven exist, mirroring `decisions/0031`/`0033`'s "usage-proven,
not manually toggled" gating, generalized from vendor enrichment to
relationship enrichment.

Two design questions had more than one reasonable answer and needed
settling before implementation, not during it:

1. **Where do "a spec doc mentions X" edges live?** The graph already has
   two tables that superficially look close: `documents_edges` (a doc
   artifact documenting one *symbol*) and `skill_mentions_edges` (a
   *Skill* mechanically mentioning a vendor and/or source file).
2. **How does codecompass know which files in a project *are* spec docs?**
   There's no existing convention to lean on — unlike vendor detection
   (driven by manifest files) or Skill detection (driven by
   `.claude/skills/**/SKILL.md`'s fixed location), "spec doc" is a much
   fuzzier category that varies by project.

## Decision

**A new table, `doc_relations_edges`, not an extension of `documents_edges`
or `skill_mentions_edges`.** It has the same two-nullable-target shape
`skill_mentions_edges` already established (`target_vendor_id`/
`target_doc_artifact_id`, exactly one set per row, `relation_kind`
distinguishing `'mentions_dependency'` from `'mentions_artifact'`) — not a
new pattern, just applied to a new source-node kind (`doc_artifacts` rows
with `kind='spec_doc'`, `origin='project'`, both newly added CHECK-constraint
values). `doc_artifacts.kind`/`origin` widen the same way Phase 17 widened
`kind` alone: a recreate-the-table migration
(`_migrate_doc_artifacts_constraints`, generalized from Phase 17's
`_migrate_doc_artifacts_kind_constraint` to cover either column),
`_SCHEMA_VERSION` "2" → "3".

**Default-glob detection, not a manifest/marker file the user has to
maintain.** `spec_docs.scan_spec_docs` globs a fixed default pattern set
(`README.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md`, `PRD.md`,
`docs/**/*.md`, `architecture/**/*.md`, `decisions/**/*.md`, `spec/**/*.md`,
`specs/**/*.md`, `rfcs/**/*.md`, `*.spec.md`) on every whole-project sync,
the same "driven by the rebuild that already runs" posture every other
graph-populating scan in this codebase already has. No `vendor.toml`
configurability yet — ship the fixed list, widen it only once a real
project shows the defaults are wrong for it.

## Alternatives considered

- **Fold spec-doc mentions into `documents_edges`.** Rejected —
  `documents_edges` specifically means "this artifact documents this
  *symbol*" (narrower); a spec doc mentioning a vendor by name usually
  isn't naming an individual symbol, so reusing this table would either
  require a fake/null symbol row or silently widen what the table's
  existing callers (`vendor_profile`'s `documenting_artifacts`) can assume
  a row means.
- **Fold spec-doc mentions into `skill_mentions_edges`.** Rejected —
  that table is narrowly scoped to *Skills* as the source (its own name
  says so), and `skills_index`'s existing contract reads every row under
  that assumption. Widening its semantics to "any doc artifact mentions
  any other doc artifact" would blur that contract for an existing caller
  rather than extend it cleanly.
- **A hand-maintained manifest listing which files are specs** (e.g. a
  `spec-docs.toml` the user edits directly). Rejected for the same reason
  a hand-maintained `undo`-target file list was rejected in Phase 18
  (`decisions/0036`): it drifts the moment a spec doc is added, removed,
  or renamed and nobody remembers to update the manifest. Convention-based
  detection, driven by the same rebuild that already runs on every sync,
  stays correct automatically.
- **A single catch-all `**/*.md` default**, rather than the specific
  named-file/named-directory list above. Rejected as too broad — it would
  sweep up READMEs inside `vendor/<name>/src/` clones, third-party
  `node_modules` docs, and any other incidental markdown a project happens
  to contain, none of which are *this project's own* spec docs. The
  narrower, explicit list is a closer match to what "spec doc" actually
  means for a typical project, at the cost of missing an unconventionally
  named one — an accepted tradeoff given the configurability escape hatch
  is deliberately deferred, not foreclosed.

## Consequences

- Consolidating all three "doc artifact mentions X" edge tables
  (`documents_edges`, `skill_mentions_edges`, `doc_relations_edges`) into
  one general table is a future option if real duplication pain shows up
  across all three, but is explicitly not pursued now — no evidence of
  that pain yet, and each table currently guarantees a narrower, simpler
  contract to its own callers.
- A spec doc that doesn't match any of the fixed default glob patterns
  (an unconventionally named or located file) is invisible to
  `doc_relations_edges`/`query relations`/`check`'s coverage-gap section
  until either the file is moved to a matching location or a future phase
  adds `vendor.toml` configurability for the pattern set.
- Direction is spec-doc-outward only in this phase (a Skill's or
  dependency doc's own body mentioning a spec doc by name is not scanned
  for) — a deliberate, separately-trackable follow-up, not resurrected
  here; see the phase plan's Explicitly deferred section.
- Phase 22's relationship enrichment has a concrete, mechanically-verified
  edge set to enrich over as soon as this phase ships — no separate
  "does this relationship actually exist" check needed before spending on
  it, the same usage-proven gating `decisions/0031`/`0033` already
  established for vendor enrichment.
