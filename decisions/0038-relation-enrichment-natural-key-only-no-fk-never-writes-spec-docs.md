# 0038. `doc_relation_enrichment` is natural-key-only with no foreign key, and never writes to a spec doc

## Status

Accepted

## Context

Phase 22 (`planning/phase-22-ai-enriched-cross-artifact-relationships.md`)
adds AI enrichment over the `doc_relations_edges` rows Phase 21
(`decisions/0037`) mechanically detects: for each spec doc <-> dependency
or spec doc <-> doc-artifact relationship already proven to exist, ask an
AI call to explain, in a sentence or two, *how* the two relate — the same
"mechanical detection first, AI enrichment only over what it proved"
gating this project already applies to vendor/symbol enrichment
(`decisions/0031`/`0033`), generalized from vendors to relationships.

Two design questions needed settling before implementation:

1. **How does the new enrichment table survive `rebuild_deterministic`?**
   Phase 10 established the precedent for this exact problem —
   `vendor_enrichment`/`symbol_enrichment` survive every whole-project
   rebuild by holding a foreign key to `vendors.id`/`symbols.id`, and
   `rebuild_deterministic` upserts `vendors`/`symbols` *by natural key*
   (`INSERT ... ON CONFLICT(name) DO UPDATE`) rather than deleting and
   reinserting them, which keeps their integer id — and therefore the
   enrichment row's foreign key — valid across a rebuild. Does the new
   `doc_relation_enrichment` table follow the same shape, with a foreign
   key to `doc_artifacts.id`?
2. **Where does the AI-generated relationship summary get written?** Every
   other enrichment output this project generates (`technical_
   description`, `conversational_overview`, per-symbol `purpose`) ends up
   both in the graph *and* in a codecompass-owned generated file
   (`vendor/<name>/CLAUDE.md`, `OVERVIEW.md`, a Skill). A spec doc is
   different: it's the user's own hand-authored content, not a
   codecompass-generated artifact.

## Decision

**`doc_relation_enrichment` is keyed by plain natural-key TEXT columns
(`source_doc_path`, `target_vendor_name`, `target_doc_path`), with no
foreign key at all — a deliberate departure from the Phase 10 precedent.**
The reason the vendor/symbol fix doesn't transplant cleanly here:
`rebuild_deterministic` deletes and unconditionally reinserts every
`doc_artifacts` row on *every* call (`DELETE FROM doc_artifacts`, no
upsert branch) — because doc artifacts churn far more than vendors/symbols
do (a spec doc can be renamed, split, or deleted between syncs in a way a
tracked dependency rarely is). Switching `doc_artifacts` to upsert-by-path
purely to support this one new table would be a real, higher-risk change
to code four other tables (`documents_edges`, `skill_mentions_edges`,
`routes_via_edges`, `doc_relations_edges`) already cascade from. Instead:
don't reference `doc_artifacts.id` at all. `doc_relation_enrichment` keys
on the same path strings `graph.py`'s own module docstring already
prefers ("Row dataclasses reference each other by natural key ... rather
than by pre-assigned integer id") — a path surviving a rename is not this
table's problem to solve; a path that disappears just leaves an orphaned
enrichment row that no query ever surfaces (harmless, matching `vendor_
enrichment`'s own tolerance of an eventually-orphaned row if a vendor is
removed from `vendor.toml` outside a rebuild — never actively pruned by
this project's existing code either).

One consequence of going natural-key-only surfaced during implementation,
not anticipated up front: SQL's `UNIQUE` constraint treats every `NULL` as
distinct from every other `NULL`, including another `NULL` in the same
column. `doc_relation_enrichment` has exactly one of `target_vendor_name`/
`target_doc_path` set per row (mirroring `doc_relations_edges` itself), so
a naive `INSERT ... ON CONFLICT(source_doc_path, target_vendor_name,
target_doc_path) DO UPDATE` — the upsert shape `record_enrichment` already
uses for `vendor_enrichment` — would never actually detect a conflict
against an existing row whose non-matching column is `NULL`: it would
silently insert a duplicate row on every re-enrichment of the same
relationship instead of updating in place. `record_relation_enrichment`
sidesteps this by deleting any existing row for the exact triple (matched
with SQL's NULL-safe `IS`, not `=`) and then inserting fresh, wrapped in
one transaction. `relation_enrichment_candidates`'s own join against this
table uses the same NULL-safe `IS` comparison for the same reason — a
plain `=` join would never match an already-cached row either.

**The AI-generated summary is written *only* to `doc_relation_enrichment`
(the gitignored graph) — never into a spec doc's own file.** codecompass
reads a spec doc's text (the same way it already reads a consuming
project's own source for usage detection) but gains no write path to one
here, or ever. This mirrors the root `CLAUDE.md` boundary (`CLAUDE.md` §0:
only touched via presented-diff approval) but is stricter: codecompass has
*no* write path to a spec doc at all, approved or not. Enforced
structurally, not just by convention: `relation_enrichment.apply_results`
doesn't accept a `project_root` parameter, so it has no filesystem handle
to a spec doc even if a future edit tried to add one without also
widening this function's signature — a caller would have to deliberately
add the parameter back, which is a visible, reviewable diff, not an
accidental one-line write slipped into existing code.

## Alternatives considered

- **Switch `doc_artifacts` to upsert-by-path**, matching `vendors`/
  `symbols`, so a straightforward FK-based `doc_relation_enrichment` (like
  `vendor_enrichment`) would just work. Rejected: `doc_artifacts` is the
  cascade root for four other edge tables, all currently written assuming
  a full delete-and-reinsert every rebuild; switching that assumption is a
  real, separately-risky change with no relation to this phase's actual
  goal, better left alone unless a concrete need for it emerges on its
  own.
- **A committed-file cache fallback**, the way vendor enrichment survives
  a fresh clone via a hash line embedded inside the committed `vendor/
  <name>/CLAUDE.md` (Phase 14). Rejected for this phase: there is no
  codecompass-owned file to embed a cache-hash line into — spec docs are
  never written to, by the boundary above — so this fallback has no
  analogous target. A fresh clone re-pays for relationship enrichment
  once; accepted for v1 since these are short summaries over a small,
  usage-proven candidate set, much cheaper to regenerate than the
  description Phase 14 originally solved this problem for. Revisit only
  if real cost complaints surface.
- **Fold relationship enrichment into `codecompass.enrichment`** rather
  than a sibling `relation_enrichment.py` module. Rejected: a relationship
  candidate's shape (a doc pair plus two text excerpts) is different
  enough from a vendor candidate's shape (a vendor plus its used symbols)
  that sharing one module's functions would mean threading a
  type-discriminated candidate through every function — a worse fit than
  this project's existing preference for small, single-purpose modules
  (`usage.py`, `doc_mapping.py`, `skill_scan.py`, `spec_docs.py`). The two
  modules do share the batched forced-tool-use *call machinery* shape
  (client setup, retry, schema pattern) — ported near-verbatim, the same
  way `enrichment.py` itself ported that shape from the now-deleted
  `grounded_description.py` — rather than literally sharing code, since
  `enrichment._call_anthropic` is hardcoded to that module's own
  constants and exception type.

## Consequences

- `doc_relation_enrichment` rows for a relationship whose source spec doc
  or target has since been renamed/removed become orphaned — invisible to
  every query, never actively pruned, the same tolerance `vendor_
  enrichment` already has for a vendor removed from `vendor.toml`. Not
  revisited unless it becomes a real, observed problem.
- `record_relation_enrichment`'s delete-then-insert is two statements
  instead of one `INSERT ... ON CONFLICT`, which is marginally more I/O
  per write — accepted given the write volume here (a handful of
  relationship rows per run, gated by usage-proven mechanical detection)
  is nowhere near a scale where that matters.
- Every future table that might want to "survive `rebuild_deterministic`"
  by referencing `doc_artifacts` faces the same choice this ADR made:
  either accept `doc_artifacts` staying delete-and-reinsert (and go
  natural-key-only, watching for the NULL-uniqueness gotcha on any
  nullable natural-key column), or take on the separate risk of switching
  `doc_artifacts` to upsert-by-path. This ADR doesn't resolve that
  tradeoff generally, only for this one table.
- The never-write-to-spec-docs boundary is permanent, not just a Phase 22
  choice — no future phase should add a write path to a spec doc without
  first revisiting this ADR and the root `CLAUDE.md`'s own doc-sync rules,
  which already treat hand-authored project content as something this
  tool observes, not edits.
