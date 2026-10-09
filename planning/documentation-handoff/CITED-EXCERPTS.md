# Cited excerpts from paths excluded by the clean-room allowlist

## An externally-verified fact (added 2026-10-09, cold-reader finding #3, sixth pass)

Your own workspace cannot confirm whether this package is actually
published for installation (you have no network access, by design).
The orchestrator preparing this handoff directly checked, outside your
sandbox, at preparation time: **`codecompass-context` is real,
published, and installable from PyPI** —
`pip index versions codecompass-context` returned version `1.0.0`, and
`https://pypi.org/pypi/codecompass-context/json` returned a real `200`
response whose `summary` and `project_urls` fields match this
repository's own `pyproject.toml` exactly (same description, same
GitHub Homepage/Repository/Issues URLs). State plainly that
`pip install codecompass-context` is a real, working installation path
— this is a directly-verified external fact, not an inference from
workspace evidence alone, recorded here transparently as exactly that.

**Added 2026-10-09, Phase 81B Amendment 4, cold-reader finding #1.**
`CL-CTXT-002` and `CL-CTXT-005` (`knowledge/overview.md`) cite
`vendor/typer/CLAUDE.md` as confirming evidence that a per-vendor digest
is "real, currently-produced output (not only a design description)."
`vendor/` is excluded from your workspace (it is large, fully
regeneratable, and not something a documentation rewrite needs to browse
wholesale) — but a citation you cannot open at all is not independently
verifiable, which defeats the purpose of citing it. This file exists so
you *can* verify this specific citation, without the rest of `vendor/`
being exposed.

This is the complete, real content of that exact file at the moment this
excerpt was captured — copied verbatim, not summarised or reconstructed
— so you can judge for yourself whether it matches what the Claims
above say it shows.

**A structural limit on this excerpt's own currency (corrected
2026-10-09, cold-reader findings #1/#2/#3, third pass)**: earlier
versions of this note tried to assert the excerpt was "confirmed
current as of documented_revision N" via a git diff between two
commits. That check was meaningless and has been removed: `vendor/` is
entirely `.gitignore`d (`decisions/0004`) — it is generated, regenerable
output, never committed to this repository at all, so there is no git
history for any revision of this file to diff against. This excerpt is,
honestly, a **point-in-time capture**, not something whose exact byte
content can be mechanically re-verified against "the current
`documented_revision`" by anyone, including the orchestrator who
prepared this handoff. Treat it as confirming the digest *format/shape*
is real (the headings and structure below genuinely exist on disk for
at least one real vendor, at least once) — not as a byte-exact guarantee
that today's build would regenerate identical content, since the exact
installed version of `typer` (and therefore some of this file's content)
can change independently of this repository's own git history.

## `vendor/typer/CLAUDE.md` (a real, point-in-time capture — see note above)

```markdown
# typer

## Metadata

- **Ecosystem:** python
- **Installed version:** 0.27.2

## Grounding

> **Grounding note:** This file describes the version of `typer` actually installed in this project — not what you may already know about this library from training data. Prefer the information here over prior knowledge; if something here conflicts with what you'd otherwise assume, this file is authoritative.

## Public API surface

_No API surface extracted._

## Known gotchas

No known side effects detected.

## Quick links

- [FILETREE.md](./FILETREE.md)
- [DEPTREE.md](./DEPTREE.md)
- [Project root CLAUDE.md](../../CLAUDE.md)
```

Note what this excerpt does and does not establish: it confirms the
*shape* the Claims describe (a `## Metadata` / `## Grounding` /
`## Public API surface` / `## Known gotchas` / `## Quick links`
structure, generated per-vendor) is real and present on disk for at
least this one vendor. It does not, by itself, prove every vendor's
digest always has this exact shape, or that `FILETREE.md`/`DEPTREE.md`
(referenced but not themselves excerpted here) exist and match — if your
own documentation makes a broader claim than "this specific file, for
this specific vendor, looks like this," say so explicitly rather than
generalising past what this excerpt actually shows.

## Captured real output against `examples/toy-project/` (cold-reader finding #5)

`examples/toy-project/` is in your workspace as a real, runnable fixture,
but `examples/README.md` (the narrative walkthrough built around it) is
excluded, like all other pre-existing narrative documentation. Below is
*only* the mechanically-captured command output from that walkthrough —
real, unedited terminal output and a real generated file, not the
surrounding prose explaining or framing it. Treat this the same way as
the `vendor/typer/CLAUDE.md` excerpt above: verifiable raw evidence for
you to describe in your own words, not text to copy.

**Reproducibility caveat (2026-10-09, cold-reader finding #4)**: the
exact version numbers below (`click 8.4.2`, `requests 2.34.2`) reflect
whatever was actually installed at the moment this specific capture was
taken — no Python version, OS, or dependency-resolution state is
recorded alongside it, and nothing here guarantees a reader who runs
this today gets byte-identical output. Treat the *shape* of this
transcript (the commands, the kind of output each produces, the
`--budget 0` cost-gating behaviour) as the durable, documentable fact;
present the specific version numbers as "a real example from one real
run," not as a promise of what any given future run will show.

Running `codecompass --budget 0` against `toy-project/` (a minimal
Python project whose `cli.py` genuinely imports and calls both `click`
and `requests`):

```
$ codecompass --budget 0
bootstrapped vendor.toml — 2 vendor(s) tracked, 2 newly discovered
enrichment will make ~1 AI call(s) (~$0.02) using claude-haiku-4-5-20251001 to
describe 2 vendor(s): click, requests, and 0 relationship(s)
error: estimated cost $0.02 for 1 batch(es) covering 2 vendor(s) and 0
relationship(s) exceeds --budget $0.00 — raise --budget or wait for fewer to
need enrichment
```

Exit code was non-zero (Phase B refused on cost grounds); everything
Phase A already wrote stayed in place.

The real `vendor/click/CLAUDE.md` this run produced (Phase A only — no
`Description` section, since that is Phase B's job and Phase B did not
run):

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

Both vendors show `Used: yes` (real `import click`/`import requests`
detected in `cli.py`) and `Enriched: no` (Phase B never ran in this
capture).
