# 0047: Lower-bound-only dependency pins for v1.0

## Status

Accepted.

## Context

`pyproject.toml`'s `dependencies` list (`typer`, `rich`, `anthropic`,
`pipdeptree`) has never carried a version specifier of any kind, across
the entire v0.1/v0.2 development arc. That was tolerable while
codecompass was never installed by anyone but its own contributors from
an editable checkout; it stops being tolerable once `pip install
codecompass` is a real, public first impression (Phase 23 Part B) — an
unpinned install resolves whatever the newest release of each dependency
happens to be at install time, with no floor and no record of what was
actually verified to work.

## Decision

Add a lower bound to each of the four runtime dependencies, matching the
version this repo's own vendor digests have actually verified/enriched
against (visible in the generated root `CLAUDE.md` routing table):
`typer>=0.27`, `rich>=15`, `anthropic>=0.109`, `pipdeptree>=4.2`. No
upper bound on any of them.

A lower bound alone, not an exact pin (`==`) and not a capped range
(`<X`), because codecompass is a library-shaped CLI tool other projects
install alongside their own dependencies — an exact pin would fight
every downstream project's own resolver the moment they need a newer
`rich`/`typer` for something else, for a "verified against" guarantee
that only ever holds for this one repo's own `.venv` anyway.

**This choice was verified against a real breaking change, not assumed
safe.** While testing the fresh-venv install smoke test for this same
phase, `pip` resolved `anthropic` to `1.0.0` — a genuine major version
with real breaking changes (`vendor/anthropic/src/MIGRATION.md`,
"Migrating to v1": the legacy Text Completions API removed,
`temperature`/`top_p`/`top_k` removed from `messages.create()`,
`output_format` reshaped, `.with_raw_response` return types changed,
`tool_runner(compaction_control=...)` removed, the HTTP layer moved to
`httpx2`). Every one of codecompass's three `_call_anthropic`
implementations (`enrichment.py`, `relation_enrichment.py`, `chat.py`)
was checked line-by-line against that migration guide: all three use
only `anthropic.Anthropic()`, `client.messages.create(model=,
max_tokens=, system=, messages=, tools=, tool_choice=)` (or the same
without `tools=`/`tool_choice=` for `chat.py`'s plain multi-turn call),
`anthropic.AnthropicError`, and `response.content` block iteration —
none of it touches any parameter or return type the v1 migration
changed. The lower-bound-only choice is therefore confirmed safe against
a real, currently-installable major version, not just assumed safe from
SemVer good faith.

## Consequences

- A fresh `pip install codecompass` today resolves `anthropic==1.0.0`
  (and current `typer`/`rich`/`pipdeptree`), not the `0.109.1`/`15.0.0`/
  `0.27.1`/`4.2.1` this repo's own vendor digests were generated against
  — expected and accepted under a lower-bound-only policy, verified not
  to break codecompass's own usage as of this phase.
- No CI or tooling currently re-runs this compatibility check when a
  dependency ships its next major version. If `anthropic` (the dependency
  most central to codecompass's own AI-enrichment code paths) ships a
  future breaking release that does touch one of these three call sites,
  it would surface as an `EnrichmentError`/`ChatError` at runtime, not a
  build-time failure — not revisited now, since no CI/CD automation
  exists yet for this project at all (explicitly deferred, `planning/
  phase-23-polish-and-pypi-publish.md`).
- `vendor.toml`'s own per-vendor entries remain unpinned by design
  (`decisions/0031`/`0035` retired the `Depth` field that used to be the
  closest thing to a version knob there) — this decision only concerns
  `pyproject.toml`'s installable-package dependency list.

## Alternatives considered

- **Leave fully unpinned.** Rejected — flagged explicitly to the user
  ahead of this phase; the user chose lower-bound pins over the status
  quo for the first public release.
- **Exact pins (`==`).** Rejected — see Decision above; would make
  codecompass a difficult dependency for any project that also needs a
  newer `rich`/`typer` for unrelated reasons.
- **Upper-bound caps (`<2`, etc.), preemptively guarding against a future
  major version.** Rejected for this phase — codecompass's own usage of
  all four libraries is narrow and already verified compatible with the
  next major version that actually exists (`anthropic` 1.0.0, checked
  above); pre-emptively capping a dependency that hasn't broken anything
  yet trades a real, current benefit (letting users get security fixes
  and improvements) for a hypothetical future one. Revisit per-dependency
  if a real incompatibility is ever found.
