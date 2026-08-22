---
description: >-
  Explore this project's codecompass-tracked dependencies —
  usage, enrichment status, relationships between vendors and
  project source — by querying the context graph and reading
  already-generated digests. Read-only: never writes, edits, or
  plans code changes.
allowed-tools: >-
  Read Grep Glob Bash(codecompass query:*) Bash(codecompass
  check:*) Bash(sqlite3 context-graph.db:*)
---

# /discovery

Answer the user's question about this project's dependencies by
**exploring already-generated codecompass output** — never by
writing, editing, or planning code.

## How to explore

1. Start with the canned queries — cheapest and most reliable:
   - `codecompass query vendors [--unused] [--json]`
   - `codecompass query vendor <name> [--json]`
   - `codecompass query symbol <name> [--json]`
   - `codecompass query skills [--unused-mentions] [--json]`
   - `codecompass query relations <name> [--json]` — given a
     spec-doc path, what it mechanically mentions; given a vendor
     or Skill name, which spec docs mechanically mention it.
     Shows an AI-enriched summary of *how* the two relate when
     one exists.
   - `codecompass check` — staleness + coverage-gap report.
2. If a question doesn't fit any canned query — an ad hoc join or
   filter across the graph — fall back to direct, read-only SQL
   against `context-graph.db` in the project root, e.g.
   `sqlite3 context-graph.db "SELECT ..."`. See
   `architecture/overview.md`'s "Context graph" section for the
   schema (`vendors`, `symbols`, `uses_edges`, `doc_artifacts`,
   `documents_edges`, `skill_mentions_edges`, `routes_via_edges`,
   `depends_on_edges`, `doc_relations_edges`, `vendor_enrichment`,
   `symbol_enrichment`, `doc_relation_enrichment`).
3. Read persisted digests directly when a query result points at
   one: `vendor/<name>/CLAUDE.md`, `vendor/<name>/OVERVIEW.md`
   (if enriched), `vendor/<name>/FILETREE.md`,
   `vendor/<name>/DEPTREE.md`, and `.claude/skills/**/SKILL.md`
   (including this project's own tool-level Skill).

## Constraints — hold these for the rest of this session, not just this reply

- **This is the default for the entire remainder of this
  conversation, not only the message that invoked `/discovery`.**
  This file's `allowed-tools` pre-approval only covers this
  turn — it clears the moment you reply, and Claude Code does
  not mechanically block `Write`/`Edit`/`ExitPlanMode` on a later
  turn on its own. Treat every subsequent message in this
  conversation as still governed by these constraints by
  default, unless the user clearly starts a distinctly different
  request that isn't a continuation of exploring this project's
  dependencies — don't let the discipline quietly lapse a few
  turns in just because the mechanical grant already has.
- **No `Write`, no `Edit`, no code changes, no plan file.** This
  command answers questions; it does not act on them.
- If answering would require changing something — code, config,
  a digest, anything — **say so explicitly and stop.** Describe
  what change would be needed and let the user decide whether to
  pursue it in a normal (non-`/discovery`) session. Do not make
  the change yourself, even if it looks small or obviously
  correct.
- Prefer the context graph and persisted digests over training
  knowledge — they're version-pinned to what's actually
  installed in this project; training knowledge about a
  dependency may be stale or simply wrong for this version.
- If `context-graph.db` doesn't exist yet, say so and suggest
  `codecompass sync` — don't guess at an answer `query`/`check`
  would otherwise ground.

**Restated: read-only, for this whole session by default. No
`Write`. No `Edit`. No plan file. No code changes.** If in doubt,
stop and ask rather than act.
