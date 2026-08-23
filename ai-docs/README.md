# codecompass — AI agent overview

This file is for an AI agent that's just landed in this repository — either
using codecompass in a project, or contributing to codecompass itself — and
needs a fast, accurate picture of what it does before reading further. See
[`ai-docs/CLAUDE.md`](CLAUDE.md) for where to go next depending on what
you're here to do.

## What it is

codecompass generates grounded, version-pinned reference docs for a
project's actual dependencies, so an agent doesn't have to answer questions
about them from training-data memory (which drifts the moment a library
ships a new release). It inspects what's really installed (npm, PyPI,
Cargo), clones each dependency's own upstream source, and produces
per-vendor digests plus a SQLite context graph of vendors, symbols, usage,
and how a project's own docs relate to them.

## What it does

- **Deterministic, always-free output for every tracked vendor**: file
  tree, dependency tree, public API surface (from the vendor's own type
  stubs/docstrings), a pinned source clone. No AI, no cost, runs on every
  `sync`.
- **Usage-driven AI enrichment** ("Phase B") for vendors your project's
  source actually imports: a grounded description, a conversational
  overview, per-symbol purposes — sourced from the vendor's own upstream
  repository, not the model's training knowledge. Cost-disclosed,
  confirmable, budget-cappable.
- **A queryable context graph** (`context-graph.db`) linking vendors,
  symbols, real `(file, line)` usage sites, generated docs/Skills, and a
  project's own hand-authored docs — via `codecompass query` or, inside
  Claude Code, the generated `/discovery` slash command.
- **Mechanical relationship detection** between a project's own docs
  (README, `architecture/`, `decisions/`, etc.) and the dependencies/Skills
  they mention, optionally AI-summarized (*how* they relate, never *whether*
  they do).
- **Staleness checking** (`codecompass check`) against installed versions,
  and a clean `undo` of everything it generated.

## What it does NOT do

- **It never invents a relationship that isn't mechanically detected
  first.** AI enrichment only describes *how* a relationship relates —
  which relationships exist is decided entirely by deterministic
  word-boundary matching, never by a model. (`decisions/0031`,
  `decisions/0045`)
- **It never writes AI-generated content into your own hand-authored
  files.** A spec doc's relationship summary is written only to the
  gitignored graph — codecompass has no code path that writes back into a
  README, an ADR, or any other file you wrote yourself. (`decisions/0038`)
- **AI enrichment is optional, not required for the tool to function.**
  Every deterministic output (trees, API surface, the graph, staleness
  checking, generated Skills) works fully with `ANTHROPIC_API_KEY` unset.
  (`decisions/0026`)
- **`/discovery`'s read-only posture is a convention, not a mechanical
  guarantee past its first turn.** Its tool grants are read-only for the
  turn that invokes it, but nothing in Claude Code re-applies that
  restriction to later turns in the same conversation — the read-only
  discipline afterward is prompt-level, not enforced. (`decisions/0040`)
- **It doesn't classify or cluster dependencies by concept/topic** — no
  semantic grouping, no embeddings, nothing beyond mechanical name/symbol
  matching anywhere in the graph.
- **It doesn't touch git.** No commits, no `git add`/`rm`, ever — including
  in `undo`.

## Example prompts

| You ask | codecompass gives you |
|---|---|
| "Is my `requests` digest stale?" | `codecompass check` (or `--strict` for a CI-style exit code) |
| "What does this project actually use `anthropic` for?" | `codecompass query vendor anthropic` — real usage sites, or the generated Skill at `.claude/skills/codecompass-anthropic/` |
| "Does anything in this repo mention `typer`?" | `codecompass query relations typer` |
| "How does `architecture/overview.md` relate to my dependencies?" | `codecompass query relations architecture/overview.md` |
| "Set this project up with codecompass from scratch" | bare `codecompass` — zero-question bootstrap, see `docs/cli-reference.md` |
| "Explore what codecompass knows about this project, read-only" | `/discovery`, inside a Claude Code session |
