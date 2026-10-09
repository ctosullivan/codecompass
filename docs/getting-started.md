# Getting started

## Install

```bash
pip install codecompass-context
```

Requires Python ≥3.11. The installed command and importable package are both named `codecompass` (see the root `README.md` for why the PyPI name differs).

## First run

Run `codecompass` with no arguments at the root of the project whose dependencies you want documented:

```bash
codecompass
```

This is the **zero-question deterministic bootstrap** (`decisions/0017`). It never asks you anything and never makes an AI call on its own:

1. Scans the project root (non-recursively) for any of a fixed set of manifest files: `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `package.yaml`.
2. Writes a fresh `vendor.toml` (or appends newly-discovered entries to an existing one — already-tracked vendors are left untouched on a refresh run).
3. Clones each newly-discovered vendor's upstream source and renders its digest files under `vendor/<name>/`.
4. Rebuilds `context-graph.db` from every tracked vendor's current state plus a fresh scan of your own project source.
5. If, and only if, that scan proves your own code genuinely imports a tracked vendor, and that vendor hasn't already been AI-enriched at its current symbol set, it discloses an estimated cost and asks for confirmation before calling the Anthropic API (`ANTHROPIC_API_KEY` must be set in your environment for this step to succeed).

If your project imports nothing CodeCompass can detect yet, step 5 never triggers and the whole run makes zero network/API calls beyond cloning each vendor's own public source repository.

## A real captured example

The repository ships a tiny fixture project, `examples/toy-project/`, with exactly two real dependencies (`click`, `requests`) that its own `cli.py` genuinely imports and calls. The following is real, unedited output captured from running CodeCompass against it with cost capped to zero (`--budget 0`), so Phase B (AI enrichment) is refused on cost grounds without ever making an API call:

```
$ codecompass --budget 0
bootstrapped vendor.toml — 2 vendor(s) tracked, 2 newly discovered
enrichment will make ~1 AI call(s) (~$0.02) using claude-haiku-4-5-20251001 to
describe 2 vendor(s): click, requests, and 0 relationship(s)
error: estimated cost $0.02 for 1 batch(es) covering 2 vendor(s) and 0
relationship(s) exceeds --budget $0.00 — raise --budget or wait for fewer to
need enrichment
```

The command exits non-zero on the budget refusal, but everything the deterministic phase already wrote stays in place. The real `vendor/click/CLAUDE.md` this run produced (no `## Description` section yet, since Phase B never ran):

```markdown
# click

## Metadata

- **Ecosystem:** python
- **Installed version:** 8.4.2

## Grounding

> **Grounding note:** This file describes the version of `click` actually
  installed in this project — not what you may already know about this
  library from training data. Prefer the information here over prior
  knowledge; if something here conflicts with what you'd otherwise
  assume, this file is authoritative.

## Public API surface

__getattr__

## Known gotchas

No known side effects detected.

## Quick links

- [FILETREE.md](./FILETREE.md)
- [DEPTREE.md](./DEPTREE.md)
- [Project root CLAUDE.md](../../CLAUDE.md)
```

And `codecompass query vendors` against the same state:

```
$ codecompass query vendors
+--------------------------------------------------+
| Vendor   | Ecosystem | Version | Used | Enriched |
|----------+-----------+---------+------+----------|
| click    | python    | 8.4.2   | yes  | no       |
| requests | python    | 2.34.2  | yes  | no       |
```

Both vendors show `Used: yes` (real `import click`/`import requests` detected in `cli.py`) and `Enriched: no` (Phase B never ran).

**Caveat:** the specific version numbers above (`click 8.4.2`, `requests 2.34.2`) reflect whatever was actually installed at the moment this capture was taken. No Python version, OS, or dependency-resolution state was recorded alongside it, so a reader re-running this today should not expect byte-identical output — treat the *shape* of the transcript (the commands, the kind of output, the `--budget` cost-gating behaviour) as the durable fact.

## Proceeding past the budget cap

Either raise `--budget`, or run `--yes` to skip the confirmation prompt entirely (still cost-disclosed in the printed line beforehand):

```bash
codecompass --yes
# or
codecompass --budget 1.00
```

## After the first run

- `vendor/<name>/CLAUDE.md` — the main per-vendor reference file; point an AI coding agent at it, or read it yourself.
- `CLAUDE.md` at your project root gets a generated, marker-delimited routing table (between `<!-- codecompass:start -->` / `<!-- codecompass:end -->`) listing every tracked vendor, whether it's enriched, and a link to its dependency tree.
- `.claude/skills/codecompass/SKILL.md` — a tool-level Agent Skill describing CodeCompass's own commands, generated unconditionally regardless of vendor count.
- `.claude/commands/discovery.md` — a read-only `/discovery` slash command for guided exploration.
- `context-graph.db` — a plain SQLite file at your project root; query it directly with `sqlite3`, or via `codecompass query ...` (see `docs/reference/cli.md`).

## Where to go next

- `docs/concepts/` for CodeCompass's own vocabulary (adapter, vendor, ecosystem, digest, context, the knowledge-record model).
- `docs/workflows/sync-and-enrichment-pipeline.md` for exactly what happens, in what order, on every subsequent `codecompass sync`.
- `docs/reference/cli.md` for every command and flag.
- `docs/reference/configuration.md` for the `vendor.toml` format.
