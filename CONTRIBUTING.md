# Contributing to codecompass

This project follows a deliberately strict process, designed so that both
human contributors and AI coding sessions (which don't retain memory across
sessions) can pick up work without re-deriving context. The canonical,
session-facing copy of these rules lives in [`CLAUDE.md`](CLAUDE.md); this
document restates them for human contributors. The two should stay
conceptually identical — if you change one, check the other.

## Plan before implementing

Before writing code for any roadmap phase, a plan file must exist at
`planning/phase-N-<name>.md` describing:
- **Scope** — what this phase covers, and explicitly what it does not
  (deferred to a later phase).
- **Files** — new/changed files, one-line purpose each.
- **Verification** — concrete commands or test cases that confirm the phase
  is done. Not "it should work" — something you can actually run.
- **Status** — `not started` / `in progress` / `done`.

Don't begin implementation until that file exists. Add the phase's
row/status to [`planning/ROADMAP.md`](planning/ROADMAP.md) in the same
commit as the plan file. If writing the plan surfaces an assumption
that isn't already settled elsewhere, pause and ask before proceeding
from plan to code.

## The kept-in-sync docs

These docs track different aspects of the project and must each be
updated in the **same commit** as any change that affects them:

- **`docs/`** — user-facing usage documentation (CLI reference, config
  schema, generated file formats). Update when CLI behavior, config schema,
  or output formats change.
- **`architecture/`** — internal system design, describing *current state*
  (not history). Living documents, updated in place as the system evolves.
- **`decisions/`** — architecture decision records (ADRs), one file per
  significant decision, numbered sequentially (`0001-`, `0002-`, ...).
  **Append-only in practice**: a changed decision gets a *new* file that
  explicitly supersedes the old one — never edit a past ADR to reflect a
  reversal. Write a new ADR whenever a phase involves a non-obvious
  tradeoff call, not only for decisions already known at project start.
- **`planning/CONTEXT.md`** — current session-resumption state (see below).
- **`planning/ROADMAP.md`** — full-roadmap phase-status table (every
  phase, not just the current one). Updated whenever a phase starts,
  finishes, or its scope changes.

`CLAUDE.md` is **not** on this list — see the note on it below.

## Changelog discipline

`CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com) and
[Semantic Versioning](https://semver.org). Every phase adds an entry under
`[Unreleased]`, categorized (`Added`/`Changed`/`Fixed`/etc.), in the *same
commit* as the change it describes. Don't batch multiple phases into one
entry.

## Context-save discipline

At the end of each change (or natural stopping point), update
`planning/CONTEXT.md` — a single running file, not one per session — with:
- Current phase and its status.
- What was just completed, in 2-3 sentences.
- Any decisions made that weren't already captured in a plan file or ADR.
- What the next concrete step is.

Overwrite the "current state" section each time rather than appending
indefinitely — `CONTEXT.md` reflects *now*; the changelog and git history
are the log.

## Definition of done, per phase

A phase is done when: code is implemented, its plan file's verification
step passes, `docs/`, `architecture/`, and `decisions/` are updated as
applicable, a changelog entry is added, `planning/CONTEXT.md` reflects the
new state, and `planning/ROADMAP.md` marks the phase `done`. Not done
until all of these.

## Commit conventions

- One logical change per commit, message format `type(phase-N): summary`
  (e.g. `feat(phase-3): dedupe diamond dependencies in DEPTREE.md`,
  `docs(phase-0): add architecture overview`). A commit that doesn't map to
  a phase or a plan-file item usually means the plan file is incomplete.
- Changelog entries land in the same commit as the change they describe.
- **Milestones are roadmap phase groups, not individual phases.** MVP
  (v0.1, phases 0-8) and MVP (v0.2, phases 9-19) are each one milestone.
  Only when a milestone's last phase is marked `done` do we promote
  `[Unreleased]` to a dated release section in `CHANGELOG.md` and cut a
  version tag for that milestone — not after every phase.
- `planning/CONTEXT.md` is the tie-breaker if commits, changelog, and
  milestones ever drift apart.

## No AI attribution in commits

Commits must not include AI tools (Claude, or any other assistant) as a
co-author, contributor, or attribution trailer, regardless of how much of a
given change was AI-authored. This is a fixed project convention, not
something to reconsider case by case.

## A note on `CLAUDE.md`

`CLAUDE.md` is the one file exempted from the same-commit auto-sync rule
above. Every future session — human or AI — trusts it unconditionally, so
changes to it (however small) are proposed as a diff and require explicit
sign-off before they land, rather than being folded silently into whatever
other change prompted them.

## Proposing a new ADR

Add `decisions/000N-short-title.md` (next sequential number) with Status,
Context, Decision, Alternatives considered, and Consequences sections. If
the new ADR reverses an earlier one, state that explicitly in both the new
file and a short addendum note in the old one — don't edit the old
decision's original content.

## Local development

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

See [`README.md`](README.md)'s Setup section for external requirements
(Python version, `git`, the optional `ANTHROPIC_API_KEY`), and
[`planning/CONTEXT.md`](planning/CONTEXT.md) for current phase status.
