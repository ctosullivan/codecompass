# 0032. Context graph stored in SQLite, not a single JSON file

## Status

Accepted

## Context

`decisions/0024` chose a single root-level `context-graph.json` file over
any database, reasoning that the graph's only consumers at the time were
`check`'s report-only coverage sections — a flat, git-diffable file was
simpler and sufficient. That plan (former phases 9a-9d) was never
implemented.

This rework's spec requires the graph to support real relationship
queries — a new `codecompass query {vendors|vendor|symbol|skills}` CLI
command, and the tool-level Skill's own instructions to Claude for
answering "what depends on what" / "what uses this symbol" / "what skills
relate to this vendor" questions. A flat JSON tree does not support
join-shaped queries (vendor × symbol × uses × docs × skills) without
duplicating ad hoc traversal code per query type — precisely the
complexity `decisions/0024` was written before this rework's query
surface existed to weigh against.

## Decision

The context graph persists as a SQLite database, `context-graph.db`, at
the project root — schema in `planning/phase-11-sqlite-graph-foundation.md`
(vendors, source_files, symbols, uses_edges, doc_artifacts,
documents_edges, skill_mentions_edges, routes_via_edges, depends_on_edges,
plus two enrichment tables). It is gitignored and rebuilt deterministically
on every whole-project `sync`/bootstrap — `decisions/0025`'s "rebuild only
on whole-project sync, never incrementally, never diffed" posture carries
forward unchanged, just retargeted from "overwrite one JSON file" to "wipe
and rewrite every deterministic table inside one transaction." The two
enrichment tables (`vendor_enrichment`, `symbol_enrichment`) are
deliberately excluded from that rebuild so Phase B output survives a
Phase A refresh.

## Alternatives considered

- **Generate a SQLite file FROM a still-JSON source of truth** (JSON
  stays git-tracked and diffable; the DB is a derived, gitignored index
  rebuilt from it). Considered during this rework's planning interview
  and explicitly rejected: it adds two representations to keep in sync,
  in a project that otherwise commits to "one deterministic source,
  regenerate everything else on demand" (`vendor/<name>/src/` snapshots,
  trees, digests all follow this pattern already).
- **Keep the flat JSON file and layer ad hoc query code on top.**
  Rejected — doesn't scale to the join-shaped queries `query vendor
  <name>` needs to answer in one call.

## Consequences

- `context-graph.db` is gitignored, extending `decisions/0010`'s existing
  precedent (`vendor/<name>/src/` snapshots are also gitignored as
  cheaply regeneratable).
- The file's git-diffability — `decisions/0024`'s original reason for
  choosing JSON — is given up. This is offset for the one piece of state
  that isn't cheaply regeneratable (paid AI enrichment output) by a
  separate caching mechanism: a hash line written into each vendor's
  *committed* `CLAUDE.md`, detailed in the Phase 15 (`planning/
  phase-15-batched-enrichment.md`) plan, so enrichment isn't silently
  re-purchased after a fresh clone even though the DB itself doesn't
  survive one.
- `decisions/0024` and `decisions/0025` are superseded by this ADR (0025's
  rebuild-trigger *reasoning* is explicitly carried forward, not
  discarded); neither is edited (append-only).
- `graph.py` (Phase 11) is a new module with no prior-art equivalent in
  this codebase — the never-built `context_graph.py` design from the
  former phase-9a/9b/9c plans is the closest existing reference and is
  translated into SQL tables rather than dataclasses.
