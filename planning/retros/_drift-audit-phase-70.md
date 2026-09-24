# Phase 70 drift audit — release redefined CodeCompass v1

**Auditor:** docs-reconstructor (independent, MODE 1 per-phase drift audit)
**Diff audited:** `git log c1495ac..HEAD` (5 substantive commits:
`c70cbc3` plan, `9dba747` version bump + CHANGELOG flatten, `4d3a4f2`
PyPI distribution rename, `4c09185`/`08eda6e` retro + learnings closeout)
`git diff --stat c1495ac..HEAD`

**Verdict: DRIFT — 3 findings** (2 blocking, 1 non-blocking)

## Method

Read the actual observable-behaviour change directly: `pyproject.toml`'s
`name` (`codecompass` → `codecompass-context`) and `version`
(`1.0.0.dev0` → `1.0.0`), confirmed via `git diff c1495ac..HEAD --
pyproject.toml`. Confirmed the real-world state via the phase's own retro
(`planning/retros/phase-70-release-v1.md`): the package is actually live
on PyPI as `codecompass-context` 1.0.0, and `v1.0.0` is tagged — this is
not a hypothetical/planned state, it is a completed, irreversible fact as
of this phase. Then grepped every current-truth doc
(`README.md`, `docs/**`, `architecture/**`, `ai-docs/**`) for `pip
install`, the bare distribution name, `pre-release`/`not yet published`,
and stale `dev0` version strings, independent of what
`docs-maintainer`'s own two fixes (`docs/quickstart.md`,
`examples/README.md`) claimed to have covered.

## Findings

### 1. `README.md:7` — BLOCKING

> **Pre-release, not yet published.** The **foundation** (phases 0-38) is
> complete: ...

and further down, `README.md:21-23`:

> All publishing is held until then — the first PyPI release will be that
> redefined v1 (`1.0.0`). See [`planning/`](planning/) for phase-by-phase
> status.

This entire "## Status" section describes CodeCompass as **not yet
published**, gating the eventual release on a future event ("the first
PyPI release will be that redefined v1"). That event has now happened —
`codecompass-context` 1.0.0 is live on PyPI, confirmed via the real PyPI
JSON API per this phase's own retro, and `v1.0.0` is tagged and pushed.
This is the single most user-facing, highest-visibility sentence in the
entire repository (top of `README.md`, under a heading literally titled
"Status") stating something that became false the moment this phase's
`twine upload` succeeded. `README.md` was not touched in this phase's
diff at all — this is a real gap, not a deliberate, justified exclusion.
The plan file (`planning/phase-70-release-v1.md` §3) explicitly lists
`README.md` under "Explicitly not touched," reasoning that this is "a
version-number release, not a feature phase." That reasoning holds for
`architecture/`, `decisions/`, `docs/domain/`, and ordinary `docs/`
content (nothing about the system's *behaviour* changed) — but the
Status section is not a behaviour description, it is a release-status
claim, and this phase's entire purpose was to change that exact fact.

### 2. `README.md:59` — BLOCKING

```bash
pip install -e ".[dev]"    # not yet published to PyPI — local dev install
```

Same underlying issue as finding 1, narrower scope: the inline comment
on the dev-install command asserts the package is "not yet published to
PyPI," which is now false. A new user reading this comment would be told
the wrong thing about whether a real, installable release exists — this
is exactly the class of statement `docs/quickstart.md`'s own fix (`pip
install codecompass-context`, this phase) implicitly corrects, but the
identical claim in `README.md` was missed.

### 3. `examples/README.md:31` — NON-BLOCKING

```bash
./.venv/Scripts/pip install -e path/to/codecompass    # or: pip install codecompass-context, once published
```

This phase's own commit (`4d3a4f2`) updated this line's distribution
name from `codecompass` to `codecompass-context` but left the qualifier
"once published" in place. The package has, as of this same phase, been
published — so "once published" is now stale (it should read something
like "now published" or drop the qualifier). Non-blocking because the
install instruction actually given (`pip install -e path/to/codecompass`
for local dev) is still correct and the comment doesn't tell a reader to
do anything wrong; it just describes the publish state incorrectly in a
low-visibility, secondary example file, not a first-line claim like
findings 1-2.

## What was checked and found clean

- Every `pip install` occurrence across `README.md`, `docs/`,
  `architecture/`, `ai-docs/`, `examples/` — grepped broadly, not limited
  to the two files this phase's own commit touched. Only the three
  findings above are stale; `docs/quickstart.md`'s own fix is correct and
  complete for that file.
- No lingering `1.0.0.dev0` / `dev0` string anywhere in current-truth
  docs — the version bump is otherwise fully reflected.
- `README.md:23`'s own forward-looking reference to "the first PyPI
  release will be that redefined v1 (`1.0.0`)" correctly names the
  version number `1.0.0` (not `dev0`) — it's the *tense* that's wrong
  (future instead of past), not the version number itself, consistent
  with finding 1.
- CLI command name and Python import package: confirmed still
  `codecompass` everywhere (README's own extensive `codecompass <subcmd>`
  usage, `ai-docs/README.md`, `docs/cli-reference.md`) — correctly
  unaffected by the distribution-name rename, nothing to fix here.
- `architecture/overview.md:927`'s mention of "pre-release-ordering" is
  about `staleness.py`'s generic semver-parsing limitations (an
  unrelated third-party version string concept), not a claim about
  CodeCompass's own release status — not a finding.

## Domain-claim staleness check (step 5)

Checked directly whether any `docs/domain/concepts/*.md` page's own
references block cites `pyproject.toml`, `PyPI`, the distribution name,
or `CHANGELOG.md` (the four files this phase's diff actually touches
plus the artifacts it produces). Grepped all 18 concept pages
(`adapter.md`, `capability.md`, `claim.md`, `connector.md`, `context.md`,
`context-packet.md`, `decision.md`, `derivation.md`, `digest.md`,
`ecosystem.md`, `evidence.md`, `invariant.md`, `observation.md`,
`protocol.md`, `provenance.md`, `reference.md`, `relationship-edge.md`,
`requirement.md`, `vendor.md`) for `pyproject.toml`, `distribution name`,
`codecompass-context`, and `PyPI`.

**No hits.** None of the domain-corpus concept pages cite this phase's
touched files or the packaging/distribution-name concept in their own
references blocks. No domain-claim staleness candidates from this phase.

## Scope note

Checked: all current-truth docs (`README.md`, `docs/`, `architecture/`,
`ai-docs/`) for install-command and release-status staleness following
the two real observable changes (distribution name, version number).
Did not re-check `CHANGELOG.md`'s own internal correctness (mechanical
flattening, verified byte-for-byte by the phase's own process per its
retro, and not itself a "current-truth doc" in the docs-drift sense —
it's a historical record, not a system description) or
`planning/CONTEXT.md` / `planning/ROADMAP.md` (governance bookkeeping,
out of this audit's current-truth doc list, and the lead/`docs-maintainer`
already updated `ROADMAP.md` per the diff). Did not re-verify the actual
PyPI listing myself (took the phase's own retro's claim of independent
JSON-API confirmation as read, consistent with this audit's remit being
doc-vs-code/reality drift, not re-doing the release verification itself).
