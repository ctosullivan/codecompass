# Quickstart

CodeCompass generates version-pinned reference material for your
project's actual dependencies — grounded in what's really installed,
not an AI's training-data memory of the package — and wires that
material into places a coding agent (or you) will actually look:
`vendor/<name>/` on disk, a routing table injected into your project's
root `CLAUDE.md`, generated Claude Code Skills, and a queryable
`context-graph.db`.

This walks through what actually happens on a real run, using this
project's own real `python`-ecosystem vendors as the worked example
(`pyproject.toml`'s `anthropic`, `pipdeptree`, `rich`, `typer` — see
[`examples/README.md`](../examples/README.md) for a from-scratch minimal
example with `requests`/`click` if you'd rather start with something
smaller).

## 1. Install

```bash
pip install codecompass
```

Requires Python ≥3.11 (`pyproject.toml`'s `requires-python`). Optional:
set `ANTHROPIC_API_KEY` in your environment if you want the AI-enrichment
step (below) to run — CodeCompass's Python-side code never reads this
variable itself; it constructs a bare `anthropic.Anthropic()` client
(`src/codecompass/chat.py`, `src/codecompass/enrichment.py`,
`src/codecompass/relation_enrichment.py`), and the `anthropic` SDK reads
the key from the environment on its own. Without it set, everything
free (see Phase A below) still works; only the AI-enrichment step fails.

## 2. Run it — no flags, no config file needed

From your project's root (wherever `pyproject.toml`/`package.json`/
`Cargo.toml`/`requirements.txt`/`package.yaml` lives):

```bash
codecompass
```

This is a **zero-question bootstrap** (`src/codecompass/cli.py`'s
`main`/`_bootstrap`) that runs in two phases, back to back:

**Phase A (always free, no prompts, no AI call):**

1. Scans the project root for known manifest files and auto-discovers
   every dependency (`src/codecompass/discovery.py`:
   `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`,
   `package.yaml`).
2. Writes (or idempotently extends) `vendor.toml` — one `[[vendor]]`
   block per discovered dependency.
3. Clones each new vendor's upstream source and generates its
   dependency tree, file tree, and `CLAUDE.md` digest under
   `vendor/<name>/`.
4. Rebuilds `context-graph.db` (a SQLite file at your project root) from
   the whole project's current state.
5. Refreshes the root `CLAUDE.md` routing table and writes the
   tool-level Skill (`.claude/skills/codecompass/SKILL.md`).

**Phase B (usage-driven AI enrichment — costs money, always disclosed
and confirmable):** if Phase A's graph rebuild finds a vendor your own
project source actually imports/uses, with no up-to-date AI-generated
description yet, CodeCompass prints the estimated cost and the model
it'll use, then asks:

```
enrichment will make ~1 AI call(s) (~$0.02) using claude-haiku-4-5-20251001 to
describe 2 vendor(s): click, requests, and 0 relationship(s)
Proceed? [y/n]:
```

(a real transcript, [`examples/README.md`](../examples/README.md)).
Answer `y`, or skip the prompt entirely with `--yes`, or cap spend up
front with `--budget <amount>` (checked *before* any API call — if the
estimate exceeds it, Phase B aborts with a non-zero exit, and everything
Phase A already wrote is unaffected). `--budget 0` is a convenient way to
try CodeCompass without spending anything at all.

## 3. See what it produced

```bash
codecompass query vendors
```

A real result from this exact checkout (no Phase B run yet):

```
┏━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━┳━━━━━━━━━━┓
┃ Vendor     ┃ Ecosystem ┃ Version ┃ Used ┃ Enriched ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━╇━━━━━━━━━━┩
│ anthropic  │ python    │ 1.5.0   │ yes  │ no       │
│ pipdeptree │ python    │ 4.2.5   │ no   │ no       │
│ rich       │ python    │ 15.0.0  │ yes  │ no       │
│ typer      │ python    │ 0.27.2  │ yes  │ no       │
└────────────┴───────────┴─────────┴──────┴──────────┘
```

`Used` reflects real, detected `import` usage in your own project
source — `pipdeptree` shows `no` here because nothing in
`src/codecompass/` actually imports it directly (it's invoked as a
subprocess: `python -m pipdeptree`, per
`src/codecompass/adapters/python.py`). This matters: only vendors shown
`Used: yes` are ever candidates for AI enrichment or a generated Skill.

Read one vendor's own generated digest directly:

```bash
cat vendor/anthropic/CLAUDE.md
```

Ask an ad hoc question against the context graph:

```bash
codecompass query vendor anthropic
codecompass query symbol Anthropic
```

Or, inside a Claude Code session working on this project, type
`/discovery` — a generated, read-only slash command
(`.claude/commands/discovery.md`) that guides an agent through the same
exploration without ever writing or editing anything.

## 4. Keep it current

Re-run whenever dependencies change:

```bash
codecompass sync          # regenerate everything, re-check for new enrichment candidates
codecompass check         # report-only staleness + coverage-gap table, always exits 0
codecompass check --strict  # CI gate: non-zero exit on major/unclassifiable version drift
```

## 5. Undo, if you want to stop using it

```bash
codecompass undo --dry-run   # see what would be removed, touches nothing
codecompass undo             # remove it (best-effort; asks for confirmation unless --yes)
```

`undo` never runs a git command — committing the resulting working-tree
change is left to you (`src/codecompass/cli.py`'s `undo` command,
`decisions/0036`).

## Where to go next

- [`cli-reference.md`](cli-reference.md) — every command and flag, in
  full.
- [`config-schema.md`](config-schema.md) — every `vendor.toml` field.
- [`docs/domain/concepts/`](domain/concepts/) (this project's approved
  domain corpus) — what "vendor," "adapter," "digest," and "context
  packet" precisely mean, if a term above was unfamiliar.
