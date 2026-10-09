# CodeCompass

**CodeCompass builds and maintains grounded, version-pinned dependency reference documentation for AI coding agents.** It inspects the packages a project actually depends on, renders deterministic structural facts about them (file trees, dependency trees, public API surfaces), optionally layers on AI-generated plain-language descriptions where the project's own source code proves a dependency is actually used, and publishes the result as files an agent (or a human) can read directly — plus a queryable SQLite graph, generated Agent Skills, Cursor rules, and a guided-exploration slash command.

This README and the accompanying `docs/` tree were reconstructed from the project's current source, tests, configuration, and a prepared evidence package — see each page's own notes for what is directly verified against source versus what remains an open question. Where the evidence does not resolve something, this documentation says so explicitly rather than guessing.

## Package names — two different ones, on purpose

- **PyPI distribution name:** `codecompass-context` (`pyproject.toml`'s `[project].name`). This is the name you `pip install`.
- **Import package / CLI command name:** `codecompass` (the `src/codecompass/` package; the `pyproject.toml` entry point is `codecompass = "codecompass.cli:app"`).

Nothing in the available evidence explains *why* these differ (e.g. a PyPI name collision with another project) — this is stated as a fact, not a mystery solved. Use `codecompass-context` wherever you need the installable name, and `codecompass` wherever you need the command or the Python import.

`pip install codecompass-context` is confirmed, by an external check performed outside this reconstruction's own workspace, to be a real, currently-published package on PyPI (version `1.0.0` at the time of that check), whose metadata matches this project's own `pyproject.toml` description and GitHub links.

## Installation

```bash
pip install codecompass-context
```

Requires **Python ≥3.11** (`pyproject.toml`'s `requires-python`, and `decisions/0009`, referenced by the project's own decision log). Python 3.11+ is relied on specifically because `tomllib` (standard library since 3.11) replaces a third-party TOML-reading dependency (`config.py`, `discovery.py`).

Runtime dependencies (from `pyproject.toml`): `typer>=0.27`, `rich>=15`, `anthropic>=0.109`, `pipdeptree>=4.2`, `pyyaml>=6.0`. Development/test dependencies: `pytest`, `ruff`, `jsonschema`.

## Quick start

From the root of a project you want CodeCompass to analyze:

```bash
codecompass
```

With no subcommand, `codecompass`:

1. Auto-discovers dependency manifests at the project root (`package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `package.yaml`) and writes or refreshes `vendor.toml` — no questions asked, no AI calls.
2. Clones each newly-discovered dependency's own upstream source and renders its deterministic digest (`vendor/<name>/CLAUDE.md`, `FILETREE.md`, `DEPTREE.md`, plus JSON mirrors) — still no AI calls.
3. Rebuilds the project-wide context graph (`context-graph.db`), detecting which vendors your own project code actually imports.
4. If any vendor is **usage-proven** (your code genuinely imports it) and not yet AI-enriched, it discloses an estimated cost and asks you to confirm before making any Anthropic API call. `--yes` skips the prompt; `--budget <USD>` caps spend and aborts (before any call) if the estimate exceeds it.

See `docs/getting-started.md` for a full walkthrough, including a real captured example run against a minimal two-dependency project.

AI enrichment (step 4 above) requires `ANTHROPIC_API_KEY` to be set in the environment — the project's own Anthropic SDK calls (`enrichment.py`, `relation_enrichment.py`, `chat.py`) construct `anthropic.Anthropic()` with no explicit credential argument, relying on the SDK's own standard environment-variable convention.

## What CodeCompass is — in one paragraph

CodeCompass tracks a project's dependencies ("vendors") against a small, closed set of package **ecosystems** (`npm`, `python`, `cargo`, `haskell`), using one **adapter** per ecosystem to extract real facts: installed version, source location, dependency tree, and a mechanically-extracted public API surface. It renders these facts into a per-vendor **digest** (`vendor/<name>/CLAUDE.md` and siblings), and — only once your own project's source code is proven to actually use a dependency — can layer a batched, cost-disclosed AI call on top to add a plain-language technical description. All of this is also recorded in a queryable SQLite **context graph** (`context-graph.db`), and surfaced to AI coding agents via generated Agent Skills, Cursor `.mdc` rules, and a read-only `/discovery` slash command. See `docs/concepts/` for CodeCompass's own vocabulary in more depth.

## Status and maturity — stated plainly, not reconciled

`pyproject.toml` declares `version = "1.0.0"` **and** `classifiers = ["Development Status :: 4 - Beta", ...]` simultaneously. These are two different, independent signals (semantic version vs. PyPI maturity classifier) that disagree on how mature the project is. Nothing in the available evidence resolves which one should be trusted more — both facts are reported here rather than one being silently preferred.

The project's own decision log records (`decisions/0048`) that its "v1" milestone was explicitly redefined as a **product-validation milestone, not a packaging milestone** — consistent with a project that is versioned 1.0.0 while still self-describing as Beta.

CodeCompass ships without a dedicated documentation site; this `README.md` plus the `docs/*.md` tree, rendered by GitHub, is the whole of its documentation delivery for v1.0 (`decisions/0039`).

## Supported ecosystems

A fixed, closed four-member enum (`src/codecompass/core.py::Ecosystem`): **npm**, **python**, **cargo**, **haskell**. Each has exactly one adapter class, selected by a closed dispatch table (`src/codecompass/adapters/__init__.py::get_adapter`) — never by naming convention, plugin discovery, or a config string.

- **npm, python, cargo** — *in-process* adapters: ordinary importable Python classes inside `src/codecompass/adapters/` that shell out to the ecosystem's own native tooling (`npm ls`, `pipdeptree`, `cargo metadata`).
- **haskell** — an *external-process* adapter: CodeCompass's own `HaskellAdapter` is a thin dispatcher that reads `package.yaml` directly and then delegates all real Haskell-specific analysis (dependency-tree construction via `stack`, API-surface extraction from `.hs` source) to an independent OS subprocess — `codecompass-adaptor-haskell`, a separate, publicly-hosted, GPL-3.0-or-later repository checked out as a git submodule — speaking a small JSON-Lines wire protocol.

Both strategies are deliberate, current, and coexist by design (`decisions/0002`, `decisions/0057`) — the external-process strategy is not a replacement for the in-process one; it exists for ecosystems whose real analysis logic cannot or should not live inside CodeCompass's own GPL-covered Python process.

## Repository layout you'll actually touch

- `src/codecompass/` — the installed package.
- `adapters/haskell/` — git submodule: the reference external Haskell adapter (`codecompass-adaptor-haskell`, GPL-3.0-or-later). Requires `git submodule update --init` and a working `stack build` to use.
- `protocol/codecompass-adaptor-protocol/` — git submodule: the canonical specification (schemas, conformance vectors) for the external adapter wire protocol. Licensed **MIT** — different from both CodeCompass itself and the Haskell adapter, both GPL-3.0-or-later. This is a real, checked difference, not an assumption.
- `tests/` — the test suite (`pytest`).
- `scripts/` — maintainer-only tooling, not part of the installed `codecompass` package (see `docs/development/contributing.md`).
- `examples/toy-project/` — a tiny, two-dependency (`click`, `requests`) real Python project used to demonstrate CodeCompass's own output; see `docs/getting-started.md`.

<!-- codecompass-grounded-by: CL-KNOW-001 region:intermediate-knowledge-layer -->
CodeCompass also supports a persistent, human/tool-editable Markdown
layer over a project's own structured knowledge (concepts, invariants,
behaviours, open questions) — editable by you, ChatGPT, Copilot, Claude
Code, or an ordinary Git PR, mechanically detected and reconciled back
against evidence before anything becomes canonical; `codecompass
knowledge apply` is the sole, mechanically-revalidating write path,
never bypassable by an external tool's or an agent's own say-so. See
[`docs/workflows/knowledge-reconciliation-loop.md`](docs/workflows/knowledge-reconciliation-loop.md)
— that guide is itself grounded in and reconciled against the same
underlying knowledge, so this README never becomes a second, divergent
description of what's canonical.
<!-- /codecompass-grounded-by -->

## Documentation map

- `docs/getting-started.md` — install, first run, a real captured example.
- `docs/concepts/` — CodeCompass's own domain vocabulary: adapter, vendor/ecosystem, context, digest, protocol/capability, and the evidence/knowledge record model.
- `docs/architecture/` — system overview, component map, data/control flow (including the context-graph schema).
- `docs/workflows/` — the sync/enrichment pipeline and the knowledge-reconciliation loop, end to end.
- `docs/reference/` — CLI reference, `vendor.toml` configuration, the external adapter wire protocol, and symbol-extraction behaviour.
- `docs/development/` — contributing conventions, testing.
- `docs/edge-cases-and-compatibility.md`, `docs/tests-and-acceptance.md`, `docs/decisions.md`, `docs/limitations.md`, `docs/open-questions.md` — cross-cutting material required for a complete picture, including everything this reconstruction could **not** resolve from available evidence.

## License

GPL-3.0-or-later (`pyproject.toml`; `decisions/0053` records the relicensing; `decisions/0055` records that contributor licensing terms were chosen to preserve future re/dual-licensing options). The external adapter *protocol* repository (`protocol/codecompass-adaptor-protocol/`) is licensed **MIT**, independently of CodeCompass's own license — checked directly against that submodule's own `LICENSE` file, not assumed to match.
