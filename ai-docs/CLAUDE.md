# Start here

If you're an agent asked to work in or understand this repository, start
with [`ai-docs/README.md`](README.md) — a capability/boundary overview of
what codecompass does and doesn't do, with example prompts.

**This file does not replace or duplicate the root [`CLAUDE.md`](../CLAUDE.md).**
That file governs *how sessions work on this repository's own codebase* —
planning discipline, doc-sync rules, commit conventions. This file exists
only to point an agent to the right doc for what it's actually here to do:

- **Understanding what codecompass does, or using it in a project** →
  [`ai-docs/README.md`](README.md), then [`docs/cli-reference.md`](../docs/cli-reference.md).
- **Contributing code to codecompass itself** → root
  [`CLAUDE.md`](../CLAUDE.md) first (its rules govern the work), then
  [`architecture/overview.md`](../architecture/overview.md) for current
  system design.
- **Understanding why a design decision was made** →
  [`decisions/`](../decisions/) (ADRs, append-only, one per significant
  tradeoff).
- **Current project state** — what's done, what's next →
  [`planning/ROADMAP.md`](../planning/ROADMAP.md) (full phase table) and
  [`planning/CONTEXT.md`](../planning/CONTEXT.md) (current session-resumption
  state).
