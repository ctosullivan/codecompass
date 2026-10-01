---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Relationship / edge

## Definition

A **relationship**, precisely, is a real, typed row in one of
`context-graph.db`'s six edge tables (`src/codecompass/graph.py`):

| Table | Connects | Notes |
|---|---|---|
| `uses_edges` | `source_file → vendor`/`symbol` | `symbol_id` nullable (vendor-level usage with no resolved symbol) |
| `documents_edges` | `doc_artifact → symbol` | nullable `chunk_id` |
| `skill_mentions_edges` | `doc_artifact → vendor`/`source_file` | both nullable, independently |
| `routes_via_edges` | `vendor → doc_artifact` | `UNIQUE(vendor_id, doc_artifact_id)` |
| `depends_on_edges` | `vendor → vendor` | `UNIQUE(vendor_id, depends_on_vendor_id)` |
| `doc_relations_edges` | `doc_artifact → vendor`/`doc_artifact` | `relation_kind` CHECK'd to `'mentions_dependency'`\|`'mentions_artifact'`; nullable `chunk_id` |

Every one of these tables (except the natural-key-upserted `vendors`/
`symbols`/`source_files` nodes they reference) is wiped and reinserted by
`rebuild_deterministic` on every whole-project `sync` — a relationship,
in this precise sense, is always a *current, mechanically re-provable*
fact, never a standing record of something once true (`CL-CTXT-003`,
`EV-CTXT-003`). "Precisely six" names *content-graph* edges specifically
— two further Phase-76 foreign keys pass the same lifecycle test for a
structurally different reason; see "What this is NOT" item 3 below.

## What this is NOT

This project deliberately keeps three neighbouring things **out** of this
precise meaning, even though casual language could call any of them a
"relationship":

1. **An agent-suggested relationship is not an edge, ever, until
   promoted.** `decisions/0051`: "An agent's suggested relationship is
   an observation with provenance. It is captured in
   `planning/context-gaps/` and nowhere else." It never enters
   `context-graph.db` — no staging table, no `source='agent_inference'`
   column, no write path from a `context-gaps/` entry into any graph
   table. It becomes a real edge (or a new graph capability) only
   through a separately-gated ADR process (a mechanical-detection
   decision or a future graph-capability decision — the old "Stage
   C"/"Stage E" phase-group labels are retired, `decisions/0062`, but
   the same gated-ADR promotion mechanism `decisions/0051` describes
   still applies), never silently. The decision names the exact risk
   this boundary prevents:
   an ungated agent-suggested edge would be "indistinguishable, three
   phases later, from a mechanically-proven one" (`EV-CTXT-012`).
2. **An enrichment record commenting on a relationship is not itself an
   edge.** `doc_relation_enrichment` describes an already-real
   `doc_relations_edges` row (an AI-written `ai_summary` plus a
   closed-taxonomy `relation_label`) but carries **no foreign key to
   `doc_artifacts` at all** — a deliberate design choice
   (`decisions/0038`) confirmed by a real, dedicated test
   (`test_doc_relation_enrichment_has_no_foreign_key`,
   `tests/test_graph.py:1611-1621`) that asserts
   `PRAGMA foreign_key_list(doc_relation_enrichment)` returns empty.
   `doc_relations_edges` is wiped every sync; `doc_relation_enrichment`
   survives every sync (it holds paid AI spend). These are structurally
   different kinds of row with different lifecycles, not merely
   described differently in prose (`EV-CTXT-011`).
3. **A git-topology relationship row (`git_worktrees.repository_id`,
   `git_submodules.parent_repository_id`) is a different kind of thing
   from these six, even though it also passes this page's own lifecycle
   test.** Both columns are real, typed `... REFERENCES
   git_repositories(id) ON DELETE CASCADE` foreign keys, and
   `rebuild_deterministic` wipes and reinserts all three Phase-76
   git-topology tables (`git_repositories`, `git_worktrees`,
   `git_submodules`) exactly as unconditionally as it does the six edge
   tables above (`src/codecompass/graph.py:1013-1054`) — "current,
   mechanically re-provable, never a standing record" holds for these
   rows too. What keeps them out of the "six edge tables" count is a
   different, substantive line: every one of the six tables above has
   at least one endpoint among the four content entities a vendor/doc/
   symbol query traverses (`vendors`, `symbols`, `source_files`,
   `doc_artifacts`); `git_worktrees`/`git_submodules` reference only
   `git_repositories`, a self-contained entity that no content table
   ever references and that never references any content table back
   (confirmed by an exhaustive grep of every `REFERENCES` clause in the
   schema). `decisions/0063`, the ADR that introduced these tables,
   independently confirms this is a considered design choice, not an
   implementation accident: it explicitly rejects widening `vendors`/
   `doc_artifacts` to hold this data, titles its own second Decision
   point "Mechanical facts only — no semantic relationship edges," and
   gives git topology a wholly separate CLI query surface
   (`codecompass query topology`) that shares no code path or traversal
   with `codecompass query relations` (the six edge tables' own query
   surface). This project therefore keeps "git-topology relationship
   row" (self-describing the project's own repository structure) and
   "content-graph edge" (connecting two first-class content entities) as
   two conceptually and operationally separate families that happen to
   share one implementation detail — the wipe-and-reinsert-every-sync
   lifecycle — not as members of one six-or-more-member set
   (`CL-CTXT-006`, superseding no prior record — this line was never
   stated anywhere in the corpus before this record).

So "relationship," used casually, spans at least four tiers: a
mechanically-proven content-graph edge (real, current, re-provable,
connecting two content entities); a git-topology relationship row (real,
current, re-provable, but self-describing the project's own repository
structure rather than connecting content entities); an agent-suggested
candidate (provenance-carrying observation, never a graph fact); and
enrichment commentary about an edge (AI-authored interpretation, never
itself a fact or an edge). This structure is assembled here from
separately-documented mechanisms — it was not stated as one taxonomy
anywhere in the repository before this phase (`DE-CTXT-003`,
`DE-CTXT-006`).

## Invariants

- Every edge table foreign-keys to `vendors`/`symbols`/`doc_artifacts`/
  `source_files` with `ON DELETE CASCADE` — `rebuild_deterministic`
  never needs to manually clear dependent tables in a specific order.
- No edge table is ever written to based on an agent's subjective
  judgement that a relationship exists — only mechanical detection
  (import/usage scanning, doc/Skill mapping, doc-mention regex/keyword
  matching) populates any of the six tables.
- A relationship's *existence* (an edge row) and commentary *about* that
  relationship (an enrichment row) are always separate tables with
  separate lifecycles — no edge table ever carries free-text AI
  commentary inline, and no enrichment table ever asserts a relationship
  exists on its own (it only ever elaborates on one the edge tables
  already proved).

## Example

A project's own `architecture/overview.md` mentioning `codecompass.
skill.py` produces a real `doc_relations_edges` row
(`relation_kind='mentions_artifact'`, or `'mentions_dependency'` for a
vendor mention) once `sync` runs — mechanically detected by
`doc_mapping.build_doc_relations_edges`, queryable via `codecompass
query relations`, and wiped/reinserted on the next sync.

## Counterexample / fuzzy boundary

**Genuinely fuzzy**: is a `routes_via_edges` row (vendor routed to a
Skill) the "same kind" of relationship as a `doc_relations_edges` row
(a doc mentioning a vendor)? Both are literally "an edge in the graph,"
but they represent conceptually different relationship *kinds*
(routing/exposure vs. documentation-mention) with no shared
`relation_kind`-style typing across tables — `doc_relations_edges` has
its own closed `relation_kind` enum, but `routes_via_edges`/
`skill_mentions_edges`/`depends_on_edges` do not, because each table's
own name already encodes its one relationship kind. Whether this
project considers "relationship" a single concept with six real
instantiations, or six genuinely separate concepts that all happen to
be implemented as a foreign-keyed table, is not settled anywhere in the
repository's own prose — flagged as an open observation, not resolved
here (`docs/domain/open-questions.md`).

## Relationships (to other concepts — no pun avoided, it is unavoidable)

- **Is graphed by**: [`context.md`](context.md) sense 1
  (`context-graph.db`).
- **Is never conflated with**: an agent-suggested candidate
  (`planning/context-gaps/`) or enrichment commentary
  (`vendor_enrichment`/`symbol_enrichment`/`doc_relation_enrichment`) —
  both are related concepts likely covered by this phase's evidence/
  observation/claim cluster and by `decisions/0051`/`0054`, not
  re-derived in full here.
- **Is never conflated with**: a git-topology relationship row
  (`git_worktrees`/`git_submodules`, Phase 76) — same wipe-and-reinsert
  lifecycle, but self-describing the project's own repository structure
  rather than connecting two first-class content entities; see "What
  this is NOT" item 3 above and `decisions/0063`.
- **Is cited by**: an Evidence record's `source_ref` (see
  [`reference.md`](reference.md) sense (c)) when a Claim's evidence is a
  specific edge-table row or schema location.

## References

- `CL-CTXT-003` / `DE-CTXT-003` — `planning/knowledge/codecompass-domain/`
- `CL-CTXT-006` / `DE-CTXT-006` (git-topology disambiguation, Phase 80) —
  `planning/knowledge/codecompass-domain/`
- `EV-CTXT-003`, `EV-CTXT-004`, `EV-CTXT-011`, `EV-CTXT-012`,
  `EV-CTXT-019`, `EV-CTXT-020` — `planning/knowledge/codecompass-domain/`
- `OBS-CTXT-017`, `OBS-CTXT-018`, `OBS-CTXT-019`, `OBS-CTXT-020` —
  `planning/knowledge/codecompass-domain/`
- `src/codecompass/graph.py:50-430` (schema), `:935-1084`
  (`rebuild_deterministic`), `:244-287` (git-topology schema)
- `tests/test_graph.py:1611-1621`
  (`test_doc_relation_enrichment_has_no_foreign_key`)
- `decisions/0051-agent-suggested-context-is-captured-not-graphed.md`
- `decisions/0038-relation-enrichment-natural-key-only-no-fk-never-writes-spec-docs.md`
- `decisions/0063-git-repository-topology-as-a-new-graph-capability.md`
- `architecture/overview.md:688-734`
