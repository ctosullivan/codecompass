# 0001. Task ids are never reused after a task is deleted

## Status

Accepted (2026-10-01).

## Context

Every task needs a stable integer id so `complete <id>` and `delete <id>`
can refer to a specific task from the command line. The obvious, simplest
implementation would assign ids densely — `len(tasks) + 1`, or the count
of tasks ever added — which keeps ids as a tidy `1..N` sequence as long as
nothing is ever deleted.

But tinytodo tasks get referenced outside the tool itself: a completed
task's id shows up in a commit message, a chat log, or a note, before the
task is deleted. If a deleted task's id were handed to a brand-new,
unrelated task, an old external reference to "#3" would become ambiguous
— it could mean the original task or whatever new task now holds that
number.

## Decision

`_next_id` (`src/tinytodo.py`) always returns one more than the highest
id *currently present* in the task list (`max(t.id for t in tasks) + 1`),
and ids are never reassigned once a task holding them is deleted. In
practice this produces the "never reused" guarantee with no extra
persisted state, because within a single `todo.json`'s continuous
history the highest id ever assigned is always exactly the highest id
currently present until something is deleted — and `_next_id` is only
ever called to produce a new, larger id, never to backfill a gap left by
a deletion.

## Alternatives considered

- **Dense `len(tasks) + 1` ids.** Simpler, and ids stay naturally
  compact. Rejected: this actively reuses a deleted task's old id as soon
  as the list shrinks back down, which is exactly the ambiguity this
  decision exists to avoid.
- **Persist a separate "highest id ever assigned" counter in
  `todo.json`.** Would make the "never reused" guarantee hold even across
  a delete-everything-then-start-over cycle. Rejected for now as more
  state than tinytodo's scope justifies — see Consequences below for the
  gap this leaves.

## Consequences

- Ids are not a dense `1..N` sequence once any task has ever been
  deleted; there will be gaps. This is intentional and documented in
  `_next_id`'s own docstring.
- The module keeps no record of "highest id ever assigned" beyond what's
  inferable from the current task list. This means the guarantee only
  holds within a single `todo.json`'s continuous history: deleting every
  task and then adding a new one resets the counter to 1, because there's
  nothing left in the file to infer the prior high-water mark from. A
  project that needed the guarantee to survive a delete-everything cycle
  would need to add persisted counter state, which is a real design
  change, not a bug fix.
