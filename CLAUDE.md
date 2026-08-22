# CLAUDE.md

This file governs how work on codecompass proceeds across sessions. If this
file and any other guidance (planning docs, prior conversation context)
disagree, this file wins.

## 0. This file is the one exception to same-commit doc-sync

Every other doc folder (`docs/`, `architecture/`, `decisions/`,
`planning/CONTEXT.md`, `planning/ROADMAP.md`) is updated in the same
commit as the change that affects it — see §2. This file is not. **Any change to this file, however
small, must be presented to the user as a diff and receive explicit
approval before it is written or committed.** No silent edits, no folding
a CLAUDE.md tweak into an unrelated commit. This file is what every future
session trusts unconditionally on load; unreviewed drift here compounds
silently across every subsequent session in a way drift elsewhere doesn't.

## 1. Plan before implementing

Before writing code for any roadmap phase, write `planning/phase-N-<name>.md`
describing scope (including what's explicitly deferred), files to be
created/changed, and how the phase will be verified as done. Do not begin
implementation until that file exists. Add the phase's row/status to
`planning/ROADMAP.md` in the same commit as the plan file. If writing the
plan surfaces an assumption not already settled, pause and ask before
proceeding from plan to code.

## 2. Kept-in-sync docs, same commit

- **`docs/`** — user-facing usage docs. Update when CLI behavior, config
  schema, or generated file formats change.
- **`architecture/`** — living internal design docs describing *current
  state*, not history.
- **`decisions/`** — ADRs, one per significant decision, numbered
  sequentially. Append-only: a reversed decision gets a *new* numbered file
  that supersedes the old one; never edit a past ADR's original content.
  Write a new ADR whenever a phase involves a non-obvious tradeoff, not
  only for decisions already known at project start.
- **`planning/CONTEXT.md`** — current session-resumption state (§4).
- **`planning/ROADMAP.md`** — full-roadmap phase-status table (all
  phases, not just the current one). Updated whenever a phase starts (§1),
  finishes (§5), or its scope changes.

All of the above update in the same commit as the change that touches
them — not as a follow-up.

## 3. Changelog, every change

`CHANGELOG.md` follows Keep a Changelog + SemVer. Every phase adds an entry
under `[Unreleased]`, categorized, in the same commit as the change. Don't
batch multiple phases into one entry.

## 4. Context save, end of every session

At the end of each change or natural stopping point, update
`planning/CONTEXT.md` (a single running file) with: current phase +
status, what was just completed (2-3 sentences), any decisions made that
weren't already documented, and the next concrete step. Overwrite the
current-state section each time — don't append indefinitely.

## 5. Definition of done, per phase

Code implemented + plan file's verification step passes + `docs/`,
`architecture/`, `decisions/` updated as applicable + changelog entry added
+ `planning/CONTEXT.md` reflects the new state + `planning/ROADMAP.md`
marks the phase `done`. Not done until all six.

## 6. Commits and milestones

- One logical change per commit: `type(phase-N): summary`.
- Changelog entries land in the same commit as the change, referencing the
  matching phase tag.
- Milestones are roadmap phase *groups*, not individual phases — the MVP
  (v0.1, phases 0-8) and MVP (v0.2, phases 9-19) are each one milestone.
  Only when a milestone's last phase is marked `done` do we promote
  `[Unreleased]` to a dated release section and cut a version tag for
  that milestone. Not after every phase.
- `planning/CONTEXT.md` is the tie-breaker if commits, changelog, and
  milestones ever drift.

## 7. No AI attribution in commits

Commits never include an AI assistant as co-author, contributor, or
attribution trailer, regardless of how much of a change it authored. Fixed
convention, not reconsidered case by case.

---

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the same rules restated for
human contributors.


<!-- codecompass:start -->
The table below lists dependencies with a generated reference digest under `vendor/<name>/`. Consult the linked digest before relying on training knowledge for these libraries.

| Vendor | Path | Version | Enriched | Deps | Consult when |
|---|---|---|---|---|---|
| anthropic | `vendor/anthropic/` | 0.121.0 | yes | [DEPTREE.md](./vendor/anthropic/DEPTREE.md) | API questions and known gotchas |
| pipdeptree | `vendor/pipdeptree/` | 4.2.0 | no | [DEPTREE.md](./vendor/pipdeptree/DEPTREE.md) | general usage questions |
| rich | `vendor/rich/` | 15.0.0 | yes | [DEPTREE.md](./vendor/rich/DEPTREE.md) | API questions and known gotchas |
| typer | `vendor/typer/` | 0.27.1 | yes | [DEPTREE.md](./vendor/typer/DEPTREE.md) | API questions and known gotchas |
<!-- codecompass:end -->
