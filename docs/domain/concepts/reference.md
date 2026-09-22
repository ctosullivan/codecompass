---
status: DRAFT — pending domain-skeptic review and actual-user approval
---

# Reference

## Definition

"Reference" is used in at least **three genuinely distinct senses** in
this project, none reducible to another, and never cross-linked or
disambiguated in one place before this phase (`CL-CTXT-004`):

**(a) `doc_artifacts.origin='pinned_reference'`** — a graph-level
provenance CHECK-enum value (`src/codecompass/graph.py`), added
alongside `codecompass_tool`/`codecompass_vendor`/`third_party`/
`project`/`vendor_upstream` via the same generic
`_migrate_doc_artifacts_constraints` migration mechanism Phase 21/27
already used. It classifies a `spec_doc` row whose leading content is a
YAML frontmatter block carrying both a `resolved_commit` and a
`source_url` key (`spec_docs.py::_has_pinned_reference_frontmatter`) —
externally-sourced, revision-pinned reference material a tool
materialized into the project tree, added in Phase 54c to close `CG-005`
(`planning/context-gaps/inbox.md`). Distinct from `'project'` (hand-
authored) and never reusing `'vendor_upstream'` (which requires a
tracked `vendors` row this material deliberately has none of, and whose
unguarded `vendor_ids[d.vendor_name]` dict lookup would raise an
uncaught `KeyError` aborting the sync if it were reused here).

**(b) A "reference project"** — Ledgerkit, then Technical Clipper: a
whole external, real, cloned codebase registered and studied per
`planning/v1-redefinition/reference-project-protocol.md`'s repeatable
protocol (registration format §2.1, working-copy discipline §2.2, a
task pool §2.3, a per-task procedure §2.4). Used as ground truth for
`context-evaluator`'s own context-quality-evaluation reports. A
project-level unit — an entire repository, not a row or a field.

**(c) A citation/pointer field** — `source_ref`/`doc_ref`/`test_ref` on
an Evidence record (Phase 54c's own record model, `phase-54c-evidence-
knowledge-workflow.md` §2.2), or the "references block" every
`docs/domain/concepts/*.md` page (this corpus included) is required to
carry — a pointer resolving to a real file:line location so a claim can
always be walked back to primary evidence.

## What this is NOT

- **(a) is not (b).** `pinned_reference` is a single-row provenance
  classification inside `context-graph.db`; a "reference project" is an
  entire external codebase evaluated by a human/agent process that
  never touches this project's own `context-graph.db` schema at all.
- **(a) is not (c).** A `pinned_reference` row's own frontmatter (its
  `source_url`/`resolved_commit`) is itself a kind of citation, but it
  lives inside the *ingested content*, not inside an Evidence/Claim
  record's own schema field — the two citation mechanisms are unrelated
  in format and in which system reads them.
- **(b) is not (c).** Registering a reference project is a heavyweight,
  multi-session protocol; a `source_ref` is a one-line pointer inside a
  YAML record. Both use the word "reference" for "something we point
  at, or point back to, as ground truth," but at completely different
  scales.
- **A related-but-distinct fourth term**: `planning/reference-projects/
  ledgerkit/reference-experiment/`'s own resolve/lock/extract ingestion
  pipeline is not a fourth sense of "reference" — it is the *mechanism*
  that produces material later classified under sense (a)
  (`pinned_reference`) once ingested into a project's own tree. It sits
  between senses (a) and (b): it operates on a registered reference
  project (b) to produce pinned reference material (a).

## Invariants

- Sense (a) is a closed CHECK-enum value; a new sixth-or-later value is
  added only through `_migrate_doc_artifacts_constraints`'s existing
  `_SCHEMA_VERSION`-bump mechanism, never a bespoke migration path
  (`CL-DOCORIGIN-001`, an earlier feature-scoped Claim this corpus does
  not re-derive but does cite).
- Sense (b) requires a live, working local clone per
  `reference-project-protocol.md` §2.2 — a reference project is never
  evaluated from memory or from its own README alone.
- Sense (c) always resolves to a real, checkable location — a
  `source_ref`/`doc_ref`/`test_ref` (or a concept page's references
  block) that does not resolve to real content is a defect in the
  record/page, not an acceptable placeholder.

## Example

Sense (a): the six `hledger-tag-query-*.md` files under
`planning/reference-projects/ledgerkit/reference-experiment/extracted/`,
pinned at hledger commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`, are
exactly the concrete driving instance `CG-005`/Phase 54c named for
adding `origin='pinned_reference'`.

Sense (c): `EV-DOCORIGIN-001.yaml`'s `source_ref: "src/codecompass/
graph.py:102-120,363-390"` — a real, checkable pointer.

## Counterexample / fuzzy boundary

**None found that breaks any of the three senses' own boundaries** —
each is structurally distinct in scale, format, and consuming system.
The genuinely fuzzy point is the fourth, related "reference-experiment"
pipeline noted above: it is not a fourth sense, but it *produces* the
subject matter of sense (a) *from* an instance of sense (b), which means
a careless reading could plausibly conflate all three into "reference =
whatever came from outside this project." This page states the
distinction explicitly rather than letting that conflation stand
unaddressed.

## Relationships

- **(a)** is graphed inside [`relationship-edge.md`](relationship-edge.md)'s
  `doc_artifacts` table (a node, not an edge, but part of the same
  schema).
- **(b)** feeds `context-quality-evaluation.md` (see
  [`context.md`](context.md) sense 4).
- **(c)** is the mechanism every Evidence/Claim record in this very
  corpus (`planning/knowledge/codecompass-domain/`) uses to stay
  traceable back to primary evidence — including this page's own
  references block, below.

## References

- `CL-CTXT-004` / `DE-CTXT-004` — `planning/knowledge/codecompass-domain/`
- `EV-CTXT-003`, `EV-CTXT-007`, `EV-CTXT-008` —
  `planning/knowledge/codecompass-domain/`
- `src/codecompass/graph.py:104-122` (`doc_artifacts.origin` CHECK enum)
- `planning/v1-redefinition/reference-project-protocol.md:1-30`
- `planning/knowledge/doc-origin-pinned-reference/EV-DOCORIGIN-001.yaml`,
  `EV-DOCORIGIN-008.yaml`
- `planning/context-gaps/inbox.md:267-363` (`CG-005`)
- `planning/knowledge/doc-origin-pinned-reference/CL-DOCORIGIN-001.yaml`,
  `CL-DOCORIGIN-003.yaml` (earlier, feature-scoped Claims this page
  cites but does not re-derive)
