# Architecture

This file describes your project's *current* architecture — what it
actually is today, not its history and not where it's headed. Replace
this whole file's content as your project takes real shape; the
headings below are a starting skeleton, not a required structure.

## What this project is

tinytodo is a tiny, single-file command-line todo list. It stores tasks
in a local `todo.json` file in the current directory. It's deliberately
minimal: no priorities, no due dates, no categories — just a description
and a done flag.

## How it's put together

Everything lives in `src/tinytodo.py`:

- `Task` — a small dataclass (`id`, `description`, `done`).
- `_load` / `_save` — read and write the whole task list to/from
  `todo.json` as JSON. No incremental updates; every command loads the
  full list, mutates it, and rewrites the whole file.
- `_next_id` — assigns the id for a newly-added task. See
  `decisions/0001-task-ids-are-never-reused.md` for why this isn't just
  "count of tasks + 1", and `docs/task-ids.md` for the fuller conceptual
  writeup (guarantee, limit, and what's actually been checked).
- `add` / `complete` / `delete` / `list_tasks` — the four operations,
  each a thin wrapper around load-mutate-save.
- `main` — a hand-rolled argv dispatcher (not using a CLI framework;
  there are only four commands).

## Key dependencies

None beyond the Python standard library (`json`, `dataclasses`,
`pathlib`). This project doesn't currently use CodeCompass to track any
third-party dependency — `vendor.toml` is present (adopted from
`codecompass-template`) but starts empty, matching reality.

## Decisions

Significant, non-obvious tradeoffs belong in `decisions/` (one file per
decision, see `decisions/README.md`), not duplicated here. Link to the
relevant ones if it helps a reader.

- `decisions/0001-task-ids-are-never-reused.md` — why `_next_id` doesn't
  reuse a deleted task's id, and the tradeoff this creates (ids are not a
  dense 1..N sequence; the "never reused" guarantee only holds within one
  `todo.json`'s continuous history).

---

## On this repository's relationship to CodeCompass

This template is maintained alongside
[CodeCompass](https://github.com/ctosullivan/codecompass) but is a
separate, MIT-licensed repository — not a redistribution of
CodeCompass's own GPL-3.0-or-later source or documentation. Nothing in
this template's own text is copied from CodeCompass's; the *shape* of
the working conventions it packages (plan before you code, keep docs in
sync, a running context file, a lightweight learnings log) reflects
general, widely-used development practice, freely reusable regardless
of what license governs the tool that happens to consume `vendor.toml`.
A project using this template may itself be licensed however its own
owner chooses — GPL, a permissive license, or kept entirely proprietary
— independent of both CodeCompass's license and this template's own.
