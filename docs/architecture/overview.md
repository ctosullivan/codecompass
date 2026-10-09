# Architecture overview

CodeCompass is a single Python package (`src/codecompass/`) exposed through one Typer CLI entry point (`codecompass`, `src/codecompass/cli.py`). It has no server component and no persistent background process — every invocation is a single run against the current working directory, treated as the target project root.

## The three main subsystems

1. **Ecosystem adapters** (`src/codecompass/adapters/`) — one class per `Ecosystem`, extracting real facts (installed version, source location, dependency tree, API surface) about one tracked dependency at a time. See `docs/concepts/adapter.md`.
2. **Deterministic rendering and the context graph** — tree renderers (`deptree.py`, `filetree.py`), mechanical symbol/usage/doc-relationship detectors (`symbols.py`, `source_symbols.py`, `usage.py`, `spec_docs.py`, `doc_mapping.py`, `skill_scan.py`, `git_topology.py`), and a SQLite persistence layer (`graph.py`) that a full-rebuild orchestrator (`sync.py::rebuild_project_graph`) assembles on every whole-project sync. None of this ever makes an AI call.
3. **AI enrichment** (`enrichment.py`, `relation_enrichment.py`) — a strictly separate, cost-gated, usage-driven layer that reads the deterministic graph's own usage evidence to decide what, if anything, is worth describing with an Anthropic API call, and writes its own result back into a small set of tables the deterministic rebuild never touches.

## Foundational design choices

- **Deterministic work is always free; AI work always requires disclosed consent.** The bare `codecompass` bootstrap (step 1–3 of `docs/getting-started.md`) never makes an API call. Only usage-proven vendors (vendors your own project code actually imports) become AI-enrichment candidates, and even then only after a cost estimate is printed and confirmed (or `--yes`/`--budget` is supplied). This split runs through the whole codebase — see `decisions/0017`, `decisions/0031`, `decisions/0033`.
- **Two adapter-implementation strategies coexist by design** — in-process (npm/Python/Cargo) and external-process (Haskell). See `docs/concepts/adapter.md`.
- **The context graph survives a whole-project rebuild selectively.** Most tables are fully wiped and rewritten on every sync (`rebuild_deterministic`); vendors/symbols/source-files/source-symbols are *upserted by natural key* so their integer ids survive unchanged across reruns; the three AI-enrichment tables are never touched by a rebuild at all. See `docs/architecture/data-and-control-flow.md`.
- **A persistent, bidirectional knowledge layer sits alongside, not inside, the context graph.** `planning/knowledge/<slug>/` canonical records and `context-graph.db` are two structurally separate systems with no shared schema — a project-level decision (referenced as `decisions/0071`) explicitly keeps the knowledge layer's canonical model outside the context graph.
- **A consuming AI agent's primary interface is generated artifacts, not a live API.** Per-vendor digests, a tool-level Agent Skill, per-vendor Agent Skills, Cursor `.mdc` rules, and a read-only `/discovery` slash command are all files CodeCompass writes to disk; `codecompass chat <vendor>` (a secondary REPL) grounds itself only on already-persisted digest files, never on a live reconstruction.

## What CodeCompass explicitly does not do

- No MCP (Model Context Protocol) integration exists anywhere in the source.
- No network service, no plugin marketplace, no remote execution for the external adapter protocol — stated as a deliberate non-goal of that protocol's own specification.
- `codecompass` never writes AI-generated content into a spec doc (your own hand-authored documentation) — a non-negotiable boundary for the relationship-enrichment pipeline specifically (see `docs/workflows/sync-and-enrichment-pipeline.md`).
