# Examples

One small, real worked example — `toy-project/` — for skimming what
codecompass actually produces without installing anything yourself. This
is illustration, not a test fixture (`tests/` already covers that); the
output below is real, captured by running codecompass against
`toy-project/` in a throwaway environment.

## `toy-project/`

A minimal Python project with two real, well-known dependencies:

```
toy-project/
  pyproject.toml          # declares requests + click
  src/toy_project/
    __init__.py
    cli.py                 # imports and calls both — real usage, not just a listed dependency
```

`cli.py` is a tiny `click` command that calls `requests.get()` and prints
the status code — enough real usage for codecompass's usage-driven
enrichment selection (`decisions/0031`) to have something genuine to
detect, not just two names sitting in `pyproject.toml`.

## Try it yourself

```bash
cd examples/toy-project
python -m venv .venv
./.venv/Scripts/pip install -e path/to/codecompass    # or: pip install codecompass, once published
./.venv/Scripts/pip install requests click
./.venv/Scripts/codecompass --budget 0                 # Phase A only — no AI spend
```

`--budget 0` runs the free part (Phase A: discovery, cloning, trees,
routing table) and then cleanly aborts Phase B (AI enrichment) before
making any API call, since any nonzero estimated cost exceeds a $0
budget. Drop `--budget 0` (and confirm the prompt, or pass `--yes`) to
also let Phase B run and generate real per-vendor descriptions — that
step does call the Anthropic API and costs a small amount.

## What Phase A alone produces

Real output from running `codecompass --budget 0` against `toy-project/`:

```
$ codecompass --budget 0
bootstrapped vendor.toml — 2 vendor(s) tracked, 2 newly discovered
enrichment will make ~1 AI call(s) (~$0.02) using claude-haiku-4-5-20251001 to
describe 2 vendor(s): click, requests, and 0 relationship(s)
error: estimated cost $0.02 for 1 batch(es) covering 2 vendor(s) and 0
relationship(s) exceeds --budget $0.00 — raise --budget or wait for fewer to
need enrichment
```

Exit code is non-zero (Phase B was refused on cost grounds), but
everything Phase A already wrote stays in place — nothing rolls back.
That includes, per vendor, a deterministic `FILETREE.md`/`DEPTREE.md`/
`CLAUDE.md` and a cloned source snapshot under `vendor/<name>/src/`, plus
a root `CLAUDE.md` routing table and `context-graph.db`.

`vendor/click/CLAUDE.md` (Phase A only — no `Description` section yet,
since that's Phase B's job):

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

`codecompass query vendors` against the same run:

```
$ codecompass query vendors
+--------------------------------------------------+
| Vendor   | Ecosystem | Version | Used | Enriched |
|----------+-----------+---------+------+----------|
| click    | python    | 8.4.2   | yes  | no       |
| requests | python    | 2.34.2  | yes  | no       |
+--------------------------------------------------+
```

Both show `Used: yes` — codecompass detected `cli.py`'s real
`import click`/`import requests` — and `Enriched: no`, since Phase B
never ran here (the `--budget 0` run above declined it).

`codecompass check` reports both vendors current against their installed
versions, plus report-only coverage-gap sections (unused vendors,
documented-but-unused symbols, etc.) sourced from `context-graph.db`; see
[`docs/cli-reference.md`](../docs/cli-reference.md) for what each column
and section means.

## What Phase B adds (not run here — costs a small amount)

Run without `--budget 0` (and confirm, or pass `--yes`) and Phase B adds,
per vendor: a grounded `Description` section in `CLAUDE.md` (sourced from
the vendor's own upstream repository, not training-data memory), an
`OVERVIEW.md`, per-symbol purposes, and a generated Skill under
`.claude/skills/codecompass-<vendor>/`. See the main
[`README.md`](../README.md) and
[`architecture/overview.md`](../architecture/overview.md) for the full
picture.

## Note on generated output

`vendor/`, `vendor.toml`, `context-graph.db`, `CLAUDE.md`, and
`.claude/` — everything codecompass itself generates — are **not**
checked into this example. They're deterministic and regenerate for free
by running the commands above (`vendor/` and `context-graph.db` are
already project-wide gitignored — see the root `.gitignore`); keeping
them out of the repo avoids this example going stale the moment `click`
or `requests` ship a new release.
