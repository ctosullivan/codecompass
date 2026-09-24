# codecompass

Grounded, version-pinned dependency reference docs for AI coding agents.

## Status

**Released.** `codecompass` `1.0.0` is published on PyPI as the
`codecompass-context` distribution (the installed CLI command and the
Python package you `import` are both still `codecompass`). The
**foundation** (phases 0-38) is complete: the npm/PyPI/Cargo/Haskell
package/source-grounding tool — bare `codecompass`, `init`, `sync`,
`index`, `check`, `query`, `chat`, and `undo`, all fully implemented
(`promote` was removed in Phase 15, `decisions/0033`). Phase 52 added
`codecompass enrich apply`
(`decisions/0054`), a narrower agent/developer-facing command that lets a
Claude Code agent supply spec-doc relationship enrichment when no
`ANTHROPIC_API_KEY` is configured — see "Core idea" below.

"CodeCompass v1" was **redefined** (`decisions/0048`,
[`planning/v1-redefinition/`](planning/v1-redefinition/)) from a packaging
milestone into a *product-validation* milestone: CodeCompass developed
agent-led, validated against real external reference-project work,
improved from that evidence, and released after a blank-slate
documentation reconstruction and an independent audit
(`planning/v1-closeout.md`). See [`planning/ROADMAP.md`](planning/ROADMAP.md)
for current status and deferred/post-v1 work.

**Validated, honestly reported — not oversold.** CodeCompass was tested
against a real external project ([Ledgerkit](https://github.com/ctosullivan/ledgerkit))
at two points where its default context had previously given a wrong or
misleadingly-confident answer. Both
were fixed and the fix was re-confirmed live on a newer project pin.
The measured result is **PASS WITH GAPS, LOW context advantage** — real
and repeatable, but not dramatic: CodeCompass fixed a specific,
evidenced failure mode (a real file mistaken for untracked), not a
general "codecompass makes agents smarter" claim. The remaining
ceiling is structural (see "Limitations" below), not a defect. Full
results: `planning/v1-closeout.md` §5.

## What it is

AI coding agents (Claude Code, Cursor) tend to answer questions about your
dependencies from training-data memory, which drifts out of date the moment
a library ships a new release. codecompass closes that gap: it inspects the
dependencies actually installed in your project (npm, PyPI, crates.io,
and — via a separate external adapter — Haskell/Stack),
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
  explicit key). Only needed if you want vendor AI enrichment (Phase B,
  below) or `codecompass chat` to run; everything else works with it
  unset — including spec-doc relationship summaries, which have a
  separate, no-key-required path via `codecompass enrich apply` (see
  "Core idea" below).

```bash
pip install -e ".[dev]"    # editable local dev install; the published package is codecompass-context
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
  mention — no AI call, and it never invents a relationship that isn't
  mechanically detected first. For any relationship that mention-detection
  proves real, a one- or two-sentence AI summary of *how* the two relate
  can be added — either by codecompass's own batched Anthropic-API call
  (same gate as usage-driven enrichment above), or, for edges that call
  can't cover (no `ANTHROPIC_API_KEY` configured), a narrow Claude Code
  agent writing through the same non-authoritative path (`codecompass
  enrich apply`, `decisions/0054`). Either way the summary is written only
  to the graph, never back into your spec doc's own file. Both are
  queryable via `codecompass query relations`.
- **Generated Skills** (`.claude/skills/`) and Cursor `.mdc` rules for
  enriched vendors, plus a tool-level Skill and `/discovery` command
  generated unconditionally — the steady-state way an agent consumes
  codecompass's output without you doing anything further.
- A **routing table** injected into your project's root `CLAUDE.md` so an
  agent knows which vendor digest to consult and when.
- **Staleness checking** that flags when a digest no longer matches the
  installed version, severity-aware (patch/minor/major).

## Evidence & provenance

CodeCompass distinguishes two kinds of content, and never lets them
blur together:

- **Mechanically-detected facts** — dependency trees, file trees, API
  surfaces, spec-doc relationship *existence* (does your `README.md`
  mention `turndown`? — yes/no, by literal name-mention detection, no
  AI call, never invented). These are always correct relative to what's
  actually on disk and installed; there is no hallucination risk
  because there is no generation step.
- **AI-enriched content** — vendor descriptions, conversational
  overviews, per-symbol purposes, and relationship *summaries* (given a
  real, already-proven relationship, what does it mean?) are a
  separate, clearly-disclosed layer: gated behind an upfront cost
  estimate and your confirmation. Vendor descriptions and relationship
  summaries record **which model or agent produced them** (a real
  Anthropic model id, or `agent:<name>` for Claude-Code-agent-authored
  content, `decisions/0054`) so they're never confused with a
  mechanically-proven fact — per-symbol purposes currently do **not**
  carry this same producer tag, a known, disclosed asymmetry (tracked
  in [`planning/ROADMAP.md`](planning/ROADMAP.md)'s future-improvement
  backlog, not yet fixed). AI content is grounded in the vendor's own
  real, pinned upstream source — never your project's docs, and never
  the model's own training-data memory of the library.

This split — real fact vs. disclosed, attributed AI interpretation —
is CodeCompass's own core design principle, not an afterthought. It is
documented in full, evidence-by-evidence, in
[`docs/domain/`](docs/domain/) — a from-scratch investigation of what
CodeCompass's own concepts (evidence, observation, claim, provenance,
adapter, and others) actually mean in this codebase, derived from
source and tests rather than assumed.

## Supported ecosystems

npm, PyPI, and Cargo — all three ship from day one (see
[`decisions/0008`](decisions/0008-mvp-ships-three-adapters-day-one.md)).
Haskell/Stack is a fourth, added in Phase 60 — handled differently from
the other three: it runs as a separate external adapter process rather
than in-process Python code, checked out as git submodules (see
[`docs/external-adapters.md`](docs/external-adapters.md)).

## Quick example

Bootstrapping a project is one command:

```bash
codecompass
```

That auto-discovers manifests (`package.json`, `pyproject.toml`,
`requirements.txt`, `Cargo.toml`, `package.yaml`), writes `vendor.toml`, clones every
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

At a glance: a `VendorConfig` (name + ecosystem) is the unit of
tracking; each ecosystem has an **adapter** — either in-process Python
(npm/PyPI/Cargo) or a separate **external process** speaking a small
JSON protocol over stdin/stdout (Haskell/Stack, and the model for any
future ecosystem where in-process Python is the wrong fit, e.g. one
requiring a proprietary or non-redistributable toolchain). Every `sync`
rebuilds a SQLite **context graph** (`context-graph.db`) deterministically
from what's actually on disk — usage edges, spec-doc relationships,
vendor/symbol records — then, only for vendors actually used, offers
AI enrichment as a second pass. Generated Skills and the `/discovery`
command are rendered from that graph, not hand-maintained.

Full design: [`architecture/overview.md`](architecture/overview.md)
(current-state entry point) and its companion files
(`module-map.md`, `core-data-model.md`, `adapter-interface.md`,
`context-graph-schema.md`, `sync-and-enrichment-pipeline.md`) — data
model, ecosystem adapters, tree generation, usage-driven enrichment,
the context graph schema, generated Skills/`/discovery`, the two
consumption modes (standalone vendor folder vs. routed from project
root), staleness checking, and the chat REPL.

## Limitations

Honestly disclosed, not hidden:

- **Context advantage is measured LOW**, not high, on the one real
  external project tested end-to-end (Ledgerkit) — see "Status" above.
  CodeCompass fixes specific, evidenced gaps; it is not a general
  intelligence multiplier, and that hasn't been claimed or measured.
- **The Cargo adapter has never been validated against real `cargo
  metadata` output or a real crate** — no Rust toolchain has been
  available during this project's own development so far.
- **`extract_npm_symbols` is untested against real-world `.d.ts`
  authoring styles** beyond hand-written fixtures.
- **`codecompass chat` has never been run against the real Anthropic
  API** in this project's own development environment — implemented
  and unit-tested, not live-exercised.
- **`symbol_enrichment` rows carry no producer/model attribution**
  (see "Evidence & provenance" above) — a known, disclosed asymmetry
  with the other two enrichment tables, not yet fixed.
- **The external-adapter wire protocol's `ecosystem` and `capabilities`
  fields are received but not validated** against what CodeCompass
  itself expects — an adapter reporting a mismatched value is currently
  accepted uncomplainingly.
- **No formal trigger-accuracy evaluation exists yet** for when a
  generated per-vendor Skill should or shouldn't fire.
- **Cursor `.mdc` export has no `globs` field** — a documented future
  refinement, not implemented.

Full, current list (this one is not exhaustive of every open item):
`planning/ROADMAP.md`'s "Future-improvement backlog."

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

v1.0.0 is released. See [`planning/ROADMAP.md`](planning/ROADMAP.md)
for what's deferred and what's next, and
[`planning/v1-closeout.md`](planning/v1-closeout.md) for the full v1
milestone record. [`planning/CONTEXT.md`](planning/CONTEXT.md) reflects
current session-resumption state.

## License

GPL-3.0-or-later — see [`LICENSE`](LICENSE). Previously MIT; see
[`decisions/0053`](decisions/0053-relicense-to-gpl-3.0-or-later.md) for
the relicensing rationale (aligning with `hledger`'s own licence family
ahead of deeper source-assisted, hledger-facing development work).

> **Contributing?** CodeCompass remains GPL-3.0-or-later. External
> contributors retain copyright in their own contributions, which are
> additionally subject to the Contributor License Agreement in
> [`CONTRIBUTING.md`](CONTRIBUTING.md#contributor-license-agreement)
> (`decisions/0055`) — it permits the project owner to relicense
> contributed material under alternative or proprietary terms in
> future. This does not remove or restrict anyone's rights to existing
> GPL-licensed versions of CodeCompass.
