# Phase 70 drift audit — release redefined CodeCompass v1

**Auditor:** docs-reconstructor (independent, MODE 1 per-phase drift audit)
**Re-audit of:** the three findings from this file's own prior version
(`DRIFT — 3 findings`, 2 blocking + 1 non-blocking), after fixes landed
in the working tree (`README.md`, `examples/README.md`).

**Verdict: NO DRIFT.** All 3 prior findings confirmed fixed by direct
re-read of current file content (not by trusting any agent's account of
what it changed). Mechanical checks re-run fresh and pass.

## Method

Read `README.md` and `examples/README.md` in full directly, independent
of any summary of what was changed. Diffed each against the prior
audit's quoted "was" text to confirm the "now" text is actually present
on disk, not merely claimed. Re-ran both maintainer scripts fresh rather
than trusting a prior run. Grepped the full current-truth doc set
(`README.md`, `examples/README.md`, `docs/*.md`, `architecture/*.md`,
`ai-docs/*.md`) for `not yet published`, `pre-release`, `Pre-release`,
`once published`, and `dev0` to catch anything missed outside the three
originally-flagged lines.

## Finding-by-finding re-verification

### 1. `README.md`'s "## Status" section — FIXED

Current text (`README.md:7-9`):

> **Released.** `codecompass` `1.0.0` is published on PyPI as the
> `codecompass-context` distribution (the installed CLI command and the
> Python package you `import` are both still `codecompass`).

This replaces the prior "**Pre-release, not yet published.**" claim and
the further-down "All publishing is held until then — the first PyPI
release will be that redefined v1 (`1.0.0`)" future-tense framing, which
is now: "released after a blank-slate documentation reconstruction and
an independent audit (`planning/v1-closeout.md`)" — correctly past
tense, correctly cites the closeout doc.

- **Distribution vs. import/CLI name split, confirmed still correct**:
  the section explicitly says the published PyPI distribution is
  `codecompass-context` while "the installed CLI command and the Python
  package you `import` are both still `codecompass`" — matches
  `pyproject.toml`'s actual `name = "codecompass-context"` with the
  `codecompass` console-script entry point and package directory
  unchanged.
- **`phases 0-N` claim**: `README.md:10` reads "The **foundation**
  (phases 0-38) is complete" — verified mechanically, not just read, per
  below.

### 2. `README.md`'s dev-install comment — FIXED

Current text (`README.md:62`):

```bash
pip install -e ".[dev]"    # editable local dev install; the published package is codecompass-context
```

No longer asserts the package is unpublished; correctly names
`codecompass-context` as the real published package alongside the local
editable-install instruction.

### 3. `examples/README.md`'s "once published" qualifier — FIXED

Current text (`examples/README.md:31`):

```bash
./.venv/Scripts/pip install -e path/to/codecompass    # or: pip install codecompass-context
```

The stale "once published" qualifier has been dropped entirely (not
just reworded) — the line now states the alternative real-install
command with no publish-status claim attached, which is accurate and
doesn't need one.

## Mechanical checks (re-run fresh, not reused from any prior report)

```
$ python scripts/check_user_docs.py --strict
check_user_docs: no findings
(exit 0)

$ python scripts/check_knowledge_base.py
check_knowledge_base: no findings
(exit 0)
```

`check_user_docs.py --strict` includes `check_readme_phase_count`, which
mechanically parses README's `phases 0-N` claim against the highest
phase number marked `done` in `planning/ROADMAP.md`'s foundation tables
(excluding the "Redefined CodeCompass v1" heading section, i.e. phases
39+, per that check's own documented scope). README currently claims
`phases 0-38`; `planning/ROADMAP.md` row 38 ("Final polish: redundancy
cleanup") is marked `done` and is the highest-numbered `done` row before
the Redefined-v1 heading — the claim and the roadmap agree, confirmed by
the check passing with zero findings, not by inspection alone.

## Grep sweep for any missed instance

```
grep -rn "not yet published\|pre-release\|Pre-release\|once published\|dev0" \
  README.md examples/README.md docs/*.md architecture/*.md ai-docs/*.md
```

One hit: `architecture/overview.md:927` — "No epoch support, no
pre-release-ordering [support]" — this is `staleness.py`'s generic
semver-parsing-limitation documentation for *third-party* dependency
version strings, unrelated to CodeCompass's own release status. Already
confirmed clean by the prior audit pass; re-confirmed here. No other
hits anywhere in the current-truth doc set.

## What was checked and found clean (carried forward, re-confirmed)

- CLI command name and Python import package: still `codecompass`
  everywhere (README's own `codecompass <subcmd>` usage, `ai-docs/`,
  `docs/cli-reference.md`) — correctly unaffected by the distribution
  rename.
- No lingering `1.0.0.dev0` / `dev0` string anywhere in current-truth
  docs.
- `CHANGELOG.md`'s internal correctness and `planning/CONTEXT.md` /
  `planning/ROADMAP.md` governance bookkeeping remain out of this
  per-phase drift audit's current-truth doc scope, as in the prior pass.

## Domain-claim staleness check (step 5)

Unchanged from the prior pass: none of the 18 `docs/domain/concepts/*.md`
pages' own references blocks cite `pyproject.toml`, the distribution
name, `codecompass-context`, or `PyPI`. No domain-claim staleness
candidates from this phase.

## Note on working-tree state at time of this re-audit

The three fixes above are present in the working tree
(`git status`: `M README.md`, `M examples/README.md`) but had not yet
been committed at the time of this re-audit. This report verifies file
*content* on disk, independent of commit state — the lead should commit
these two files (with a changelog entry per CLAUDE.md §3, since they are
user-facing doc corrections to a landed phase) before treating Phase 70
as fully closed per CLAUDE.md §5's "docs updated" and "drift audit finds
no misdescribing doc" conditions.

## Scope note

Checked: `README.md`, `examples/README.md` in full, re-grepped against
the full current-truth doc set (`docs/`, `architecture/`, `ai-docs/`)
for the same stale-publish-status patterns as the original pass, plus a
fresh run of both maintainer mechanical checks. Did not re-verify the
actual PyPI listing myself in this re-audit (unchanged fact from the
original pass, not something this content re-check needed to redo). Did
not re-review `CHANGELOG.md` or `planning/CONTEXT.md`/`ROADMAP.md`
correctness — out of this audit's current-truth doc list, as before.
