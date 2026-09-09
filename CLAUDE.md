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

When the agent-led development model is in effect (§8), establishing
"current project state" and "the next approved work" is the
`roadmap-context-curator`'s step, and a phase is not started until any
human-decision gate recorded against it in
`planning/v1-redefinition/README.md` §7 is resolved.

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
`architecture/`, `decisions/` updated as applicable + an independent
`docs-reconstructor` per-phase drift audit finds no current-truth doc
(`README.md`, `docs/`, `architecture/`, `ai-docs/`) left misdescribing
the system, scoped to what the phase changed (the full blank-slate
reconstruction stays a milestone activity) + changelog entry added
+ `planning/CONTEXT.md` reflects the new state + `planning/ROADMAP.md`
marks the phase `done` + a phase retro report exists at
`planning/retros/phase-N-<slug>.md` (goal, delivered vs planned, lessons
learnt, process-improvement feedback; a few lines suffice for a trivial
phase) + candidate learnings from the phase — including any surfaced by
the retro — have been triaged by the `knowledge-curator` (promote /
retain / merge / discard, per `planning/learnings/`) + an independent
`release-phase-auditor` pass (or, for a trivial phase, an explicit lead
confirmation) verifies the preceding conditions rather than trusting the
implementing agent's report. For a reference-project or
context-evaluation phase, a `context-evaluator` report exists and is
linked from the phase's exit note. Not done until all of these.

## 6. Commits and milestones

- One logical change per commit: `type(phase-N): summary`.
- Changelog entries land in the same commit as the change, referencing the
  matching phase tag.
- Milestones are roadmap phase *groups*, not individual phases — the MVP
  (v0.1, phases 0-8) and MVP (v0.2, phases 9-19) are each one milestone.
  Only when a milestone's last phase is marked `done` do we promote
  `[Unreleased]` to a dated release section and cut a version tag for
  that milestone. Not after every phase.
- The redefined-CodeCompass-v1 effort (`planning/v1-redefinition/`) is one
  further milestone group; its stages A–F tag/release only on group
  completion (Phase 67). "CodeCompass v1" as a product milestone is
  distinct from the `pyproject.toml` version string.
- `planning/CONTEXT.md` is the tie-breaker if commits, changelog, and
  milestones ever drift.

## 7. No AI attribution in commits

Commits never include an AI assistant as co-author, contributor, or
attribution trailer, regardless of how much of a change it authored. Fixed
convention, not reconsidered case by case.

## 8. Agent-led development model

CodeCompass is developed by a lead Claude Code session acting as project
lead, delegating bounded work to a small set of specialist agents defined
in `.claude/agents/`. The full model — roles, write boundaries,
independence requirements, how results return to the lead — is
`planning/v1-redefinition/agent-led-development.md`; the per-session
procedure is `planning/agent-led-workflow.md`.

Fixed points:

- **Claude Code orchestrates; CodeCompass never spawns or coordinates
  agents.**
- Specialist agents operationalise the *existing* governance mechanisms
  (this file, `ROADMAP.md`, `CONTEXT.md`, ADRs, `architecture/`, tests,
  `CHANGELOG.md`, §5's DoD, §0's protected-file rule). No agent maintains
  a private parallel system.
- Evaluation and audit agents inspect their target directly, never via
  CodeCompass, and never repair what they are judging.
- No agent writes this file, `decisions/*`, or `src/` (the lead owns
  those; ADRs go through §2's process; `src/` changes are the lead's or an
  ad-hoc implementer subagent's).
- **An agent observation is not authoritative because an agent recorded
  it** — it enters the learning lifecycle (`planning/learnings/`,
  `planning/v1-redefinition/learning-lifecycle.md`) as a candidate; only
  curation plus evidence promotes it into a test, ADR, doc, roadmap row,
  rule, or skill. Agent persistent memory is a per-agent working aid,
  never a source of truth.

---

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the same rules restated for
human contributors. See [`ai-docs/README.md`](ai-docs/README.md) for a
capability/boundary overview of what codecompass itself does and doesn't
do, aimed at an agent orienting to this project rather than working on it.


<!-- codecompass:start -->
The table below lists dependencies with a generated reference digest under `vendor/<name>/`. Consult the linked digest before relying on training knowledge for these libraries.

| Vendor | Path | Version | Enriched | Deps | Consult when |
|---|---|---|---|---|---|
| anthropic | `vendor/anthropic/` | 0.109.1 | yes | [DEPTREE.md](./vendor/anthropic/DEPTREE.md) | API questions and known gotchas |
| pipdeptree | `vendor/pipdeptree/` | 4.2.1 | no | [DEPTREE.md](./vendor/pipdeptree/DEPTREE.md) | general usage questions |
| rich | `vendor/rich/` | 15.0.0 | yes | [DEPTREE.md](./vendor/rich/DEPTREE.md) | API questions and known gotchas |
| typer | `vendor/typer/` | 0.27.1 | yes | [DEPTREE.md](./vendor/typer/DEPTREE.md) | API questions and known gotchas |
<!-- codecompass:end -->
