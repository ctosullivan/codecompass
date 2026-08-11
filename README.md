# depcompass

Grounded, version-pinned dependency reference docs for AI coding agents.

## Status

**Pre-MVP, under active development.** The MVP spans phases 0-8
(`decisions/0022`); phases 0-6 are done — `init`, `sync`, `index`, and
`check` are fully implemented. Phase 7 (`promote`) is planned but not
yet implemented; Phase 8 (the `chat` REPL) is not started. See
[`planning/`](planning/) for phase-by-phase status.

## What it is

AI coding agents (Claude Code, Cursor) tend to answer questions about your
dependencies from training-data memory, which drifts out of date the moment
a library ships a new release. depcompass closes that gap: it inspects the
dependencies actually installed in your project (npm, PyPI, crates.io) and
generates per-vendor `CLAUDE.md` digests — grounded in the exact pinned
version you're running — that an agent can consult instead of guessing.

## Core idea

For each dependency you configure, depcompass can generate:
- A **file tree** and **dependency tree** of the vendor's source, deduplicated
  and pruned for token efficiency — always free, no AI calls.
- A **public API surface** extracted from the vendor's own type
  definitions/docstrings/stubs.
- Optionally (`depth = full`), an AI-generated **gap analysis** comparing the
  vendor's API against how *your* project actually uses it, plus a **pinned
  source snapshot** for standalone consultation.
- A **routing table** injected into your project's root `CLAUDE.md` so an
  agent knows which vendor digest to consult and when.
- **Staleness checking** that flags when a digest no longer matches the
  installed version, severity-aware (patch/minor/major).

## Supported ecosystems

npm, PyPI, and Cargo — all three ship in the MVP from day one (see
[`decisions/0008`](decisions/0008-mvp-ships-three-adapters-day-one.md)).

## Quick example (planned)

> These commands are not yet implemented — see
> [`docs/cli-reference.md`](docs/cli-reference.md) for current status per
> command.

```bash
depcompass init --scan package.json pyproject.toml Cargo.toml
depcompass sync
depcompass check --strict
depcompass chat turndown
```

## How it works

See [`architecture/overview.md`](architecture/overview.md) for the full
design: data model, ecosystem adapters, tree generation, gap analysis, the
two consumption modes (standalone vendor folder vs. routed from project
root), staleness checking, and the chat REPL.

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
