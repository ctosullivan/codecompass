# codecompass

Grounded, version-pinned dependency reference docs for AI coding agents.

## Status

**MVP (v0.2) complete (phases 0-19, `decisions/0022`/`decisions/0030`)**,
not yet tagged/released. Bare `codecompass`, `init`, `sync`, `index`,
`check`, `query`, `chat`, and `undo` are all fully implemented. `promote`
was removed in Phase 15 (`decisions/0033`) — its former jobs (clone,
enrich, generate Skill) are now automatic outcomes of bootstrap/`sync`.
See [`planning/`](planning/) for phase-by-phase status.

## What it is

AI coding agents (Claude Code, Cursor) tend to answer questions about your
dependencies from training-data memory, which drifts out of date the moment
a library ships a new release. codecompass closes that gap: it inspects the
dependencies actually installed in your project (npm, PyPI, crates.io),
clones each one's upstream source, and generates per-vendor `CLAUDE.md`
digests — grounded in the exact pinned version you're running — that an
agent can consult instead of guessing. It also builds a SQLite context
graph of your project's vendors, symbols, and actual usage, exposed to both
humans and agents through `codecompass query` and a generated `/discovery`
slash command.

## Core idea

Running codecompass gets you, for every tracked dependency:
- A **file tree** and **dependency tree** of the vendor's source, deduplicated
  and pruned for token efficiency — always free, no AI calls.
- A **public API surface** extracted from the vendor's own type
  definitions/docstrings/stubs, and a **pinned source snapshot**, cloned
  from the vendor's own upstream repository, for standalone consultation
  — both free, for every vendor, no escalation step required.
- For vendors your project's own source actually imports: **usage-driven
  AI enrichment** — a grounded description sourced from the vendor's own
  upstream repository (not your project's docs or the model's training
  knowledge), a conversational overview, and an action pointer into the
  vendor's source. Auto-triggered after bootstrap/`sync`, but gated behind
  a disclosed cost estimate and a confirmation prompt (`--yes` to skip it,
  `--budget` to cap spend).
- A **context graph** (`context-graph.db`, SQLite) recording every vendor,
  symbol, usage edge, and generated doc artifact — queryable via
  `codecompass query` or, inside a Claude Code session, the generated
  `/discovery` slash command.
- **Generated Skills** (`.claude/skills/`) and Cursor `.mdc` rules for
  enriched vendors, plus a tool-level Skill and `/discovery` command
  generated unconditionally — the steady-state way an agent consumes
  codecompass's output without you doing anything further.
- A **routing table** injected into your project's root `CLAUDE.md` so an
  agent knows which vendor digest to consult and when.
- **Staleness checking** that flags when a digest no longer matches the
  installed version, severity-aware (patch/minor/major).

## Supported ecosystems

npm, PyPI, and Cargo — all three ship from day one (see
[`decisions/0008`](decisions/0008-mvp-ships-three-adapters-day-one.md)).

## Quick example

Bootstrapping a project is one command:

```bash
codecompass
```

That auto-discovers manifests (`package.json`, `pyproject.toml`,
`requirements.txt`, `Cargo.toml`), writes `vendor.toml`, clones every
vendor's source, and generates trees + the root `CLAUDE.md` routing table
+ the tool-level Skill + `/discovery` — no prompts, no AI calls. If any
tracked vendor is actually imported by your project's source and isn't
enriched yet, codecompass then discloses an estimated cost and asks to
confirm before spending anything on AI enrichment for just those vendors.
Re-running it later is a free, idempotent refresh.

```bash
codecompass --yes                # skip the enrichment confirmation prompt
codecompass --budget 1.00        # cap estimated enrichment spend (USD)
```

From there, the graph and generated Skills are the steady-state way to
consult what codecompass knows:

```bash
codecompass query vendor turndown
codecompass check --strict
```

Inside a Claude Code session, typing `/discovery` gives an agent a guided,
read-only way to explore the same graph. `codecompass chat <vendor>` is
also available — a lightweight, digest-only terminal REPL for a quick
question outside any agent session — but it's a secondary, narrower tool,
not the primary way to consult codecompass's output.

See [`docs/cli-reference.md`](docs/cli-reference.md) for the full command
reference.

## How it works

See [`architecture/overview.md`](architecture/overview.md) for the full
design: data model, ecosystem adapters, tree generation, usage-driven
enrichment, the context graph, generated Skills/`/discovery`, the two
consumption modes (standalone vendor folder vs. routed from project root),
staleness checking, and the chat REPL.

## Installation

Not yet published to PyPI. For local development:

```bash
pip install -e ".[dev]"
```

## Documentation

- [`docs/cli-reference.md`](docs/cli-reference.md) — CLI command reference
- [`docs/config-schema.md`](docs/config-schema.md) — `vendor.toml` schema
- [`architecture/overview.md`](architecture/overview.md) — system design
- [`decisions/`](decisions/) — architecture decision records

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the process this project
follows (plan-before-implementing, kept-in-sync docs, changelog discipline).

## Roadmap

See [`planning/`](planning/) for the phase-by-phase roadmap and current
status (`planning/CONTEXT.md` reflects the current state).

## License

MIT — see [`LICENSE`](LICENSE).
