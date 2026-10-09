# CodeCompass — AI agent overview

This file is for an AI agent that has just landed in this repository —
either using CodeCompass in a project, or contributing to CodeCompass
itself — and needs a fast, accurate picture of what it does before
reading further. See [`ai-docs/CLAUDE.md`](CLAUDE.md) for where to go
next depending on what you're here to do.

## What it is

CodeCompass builds and maintains grounded, version-pinned dependency
reference documentation for AI coding agents. It inspects a project's
actual dependencies, renders deterministic structural facts about them
(file trees, dependency trees, public API surfaces), optionally layers
on AI-generated plain-language descriptions where the project's own
source proves a dependency is actually used, and publishes the result
as files an agent (or a human) can read directly — plus a queryable
SQLite context graph, generated Agent Skills, Cursor rules, and a
read-only guided-exploration slash command (`/discovery`).

See [`../README.md`](../README.md) for the full picture (installation,
package naming, supported ecosystems, repository layout) and
[`../docs/`](../docs/) for everything below in depth.

## What it does

- **Deterministic, always-free output** for every tracked vendor: file
  tree, dependency tree, public API surface, a pinned source clone — no
  AI, no cost, on every `sync`.
- **Usage-driven AI enrichment** ("Phase B") only for vendors a
  project's own source actually imports — cost-disclosed,
  confirmable, budget-cappable (`--budget`, `--yes`).
- **A queryable context graph** (`context-graph.db`) — vendors, symbols,
  real usage sites, generated docs/Skills, and a project's own
  hand-authored docs — via `codecompass query` or, inside Claude Code,
  `/discovery`.
- **Mechanical relationship detection** between a project's own docs and
  the dependencies/Skills they mention — never fabricated, deterministic
  word-boundary matching decides *whether* a relationship exists; AI
  only ever describes *how*.
- **Staleness checking** (`codecompass check`) and a clean `undo`.
- **Git repository topology awareness** (`codecompass query topology`) —
  read-only, persisted at the last `sync`, never live.
- **First-party source awareness** (`codecompass query source` /
  `query source-symbol`) — a project's own implementation symbols,
  independent of any tracked dependency.
- **A persistent, human/AI-tool-editable knowledge layer**
  (`codecompass knowledge ...`) — see
  [`../docs/workflows/knowledge-reconciliation-loop.md`](../docs/workflows/knowledge-reconciliation-loop.md).

## What it does NOT do

- Never invents a relationship that wasn't mechanically detected first.
- Never writes AI-generated content into a hand-authored file.
- AI enrichment is optional — every deterministic output works fully
  with `ANTHROPIC_API_KEY` unset.
- `/discovery`'s read-only tool restriction is mechanically enforced for
  the single turn that invokes it; nothing re-applies it to a later turn
  in the same conversation.
- Never mutates git state — no commits, no `git add`/`rm`, ever,
  including in `undo` (`query topology` reads persisted state, never
  invokes `git` itself).

See [`../docs/limitations.md`](../docs/limitations.md) and
[`../docs/open-questions.md`](../docs/open-questions.md) for everything
this isn't certain of.

## Where to look for something specific

| You want to know | See |
|---|---|
| How to install/run it | [`../docs/getting-started.md`](../docs/getting-started.md) |
| CLI flags/commands | [`../docs/reference/cli.md`](../docs/reference/cli.md) |
| `vendor.toml`/config shape | [`../docs/reference/configuration.md`](../docs/reference/configuration.md) |
| The external adapter wire protocol | [`../docs/reference/protocols.md`](../docs/reference/protocols.md) |
| System architecture | [`../docs/architecture/`](../docs/architecture/) |
| Domain vocabulary (adapter, vendor, digest, ...) | [`../docs/concepts/`](../docs/concepts/) |
| Adopting CodeCompass without its own governance overhead | [`codecompass-template`](https://github.com/ctosullivan/codecompass-template) (separate, MIT-licensed) |
