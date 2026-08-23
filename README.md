# codecompass

Grounded, version-pinned dependency reference docs for AI coding agents.

## Status

**Pre-release, v1.0.0 in progress (phases 0-37 all `done`; Phase 23 Part B —
the actual PyPI publish — is now the only thing left before a `v1.0` tag,
paused for explicit user confirmation).** Bare `codecompass`, `init`, `sync`,
`index`, `check`, `query`, `chat`, and `undo` are all fully implemented.
`promote` was removed in Phase 15 (`decisions/0033`) — its former jobs
(clone, enrich, generate Skill) are now automatic outcomes of
bootstrap/`sync`. Not yet published to PyPI. See [`planning/`](planning/)
for phase-by-phase status.

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

If you're an AI agent rather than a human reader, see
[`ai-docs/README.md`](ai-docs/README.md) for a capability/boundary overview
and example prompts, and [`ai-docs/CLAUDE.md`](ai-docs/CLAUDE.md) as an
entrypoint.

## Setup

- **Python `>=3.11`** (see `pyproject.toml`).
- **`git` installed and on `PATH`** — required locally; every tracked
  vendor's source is cloned from its own upstream repository
  (`decisions/0021`).
- **`ANTHROPIC_API_KEY`** — optional. Read automatically from the
  environment by the `anthropic` SDK (nothing in codecompass passes an
  explicit key). Only needed if you want AI enrichment (Phase B, below) or
  `codecompass chat` to run; everything else works with it unset.

```bash
pip install -e ".[dev]"    # not yet published to PyPI — local dev install
```

## AI enrichment vs. no-AI usage

Everything below is **free and always-on, no API key needed**: file trees,
dependency trees, public API surface extraction, pinned source snapshots,
the SQLite context graph, staleness checking (`check`), the generated
Skills scaffold and root `CLAUDE.md` routing table, `/discovery`, and
`undo`. This is "Phase A" — it runs on every `codecompass`/`sync` call, no
prompts, no cost.

**Phase B** — usage-driven AI enrichment — only runs for vendors your
project's own source actually imports, and only after disclosing an
estimated cost and getting your confirmation (`--yes` to skip the prompt,
`--budget` to cap spend). It adds: a grounded vendor description, a
conversational overview, per-symbol purposes, and AI-generated summaries of
how your own docs relate to your dependencies. Skip it entirely with
`--budget 0` — Phase A's output is unaffected either way.

Real output from running `codecompass --budget 0` (from
[`examples/README.md`](examples/README.md), which also shows what Phase B
adds once you drop `--budget 0`):

```
$ codecompass --budget 0
bootstrapped vendor.toml — 2 vendor(s) tracked, 2 newly discovered
enrichment will make ~1 AI call(s) (~$0.02) using claude-haiku-4-5-20251001 to
describe 2 vendor(s): click, requests, and 0 relationship(s)
error: estimated cost $0.02 for 1 batch(es) covering 2 vendor(s) and 0
relationship(s) exceeds --budget $0.00 — raise --budget or wait for fewer to
need enrichment
```

Exit code is non-zero (Phase B was refused on cost grounds), but everything
Phase A already wrote — trees, `CLAUDE.md`, the cloned source snapshot, the
routing table, `context-graph.db` — stays in place; nothing rolls back.

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
- **Spec-doc relationship detection**: your own hand-authored docs
  (README, `ARCHITECTURE.md`, `docs/**/*.md`, `decisions/**/*.md`, etc.)
  are scanned and mechanically linked to the vendors and Skills they
  mention — no AI call. For any relationship that mention-detection
  proves real, usage-driven AI enrichment (same gate as above) can add a
  one- or two-sentence summary of *how* the two relate — written only to
  the graph, never back into your spec doc's own file. Both are queryable
  via `codecompass query relations`.
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
codecompass query relations architecture/overview.md
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

## Documentation

- [`docs/cli-reference.md`](docs/cli-reference.md) — CLI command reference
- [`docs/config-schema.md`](docs/config-schema.md) — `vendor.toml` schema
- [`architecture/overview.md`](architecture/overview.md) — system design
- [`decisions/`](decisions/) — architecture decision records
- [`examples/`](examples/) — a small, real worked example with real
  codecompass output, for skimming without installing anything
- [`ai-docs/`](ai-docs/) — a capability/boundary overview and entrypoint for
  an AI agent orienting to this project (see "What it is" above)

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the process this project
follows (plan-before-implementing, kept-in-sync docs, changelog discipline).

## Roadmap

See [`planning/`](planning/) for the phase-by-phase roadmap and current
status (`planning/CONTEXT.md` reflects the current state).

## License

MIT — see [`LICENSE`](LICENSE).
