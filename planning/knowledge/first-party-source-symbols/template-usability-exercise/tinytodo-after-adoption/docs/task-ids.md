# Task ids

Every task has an integer `id`, assigned once when it's added
(`add` -> `_next_id` in `src/tinytodo.py`) and never changed afterward.

## The guarantee

Within one `todo.json`'s continuous history — that is, for as long as the
file has had at least one task in it since it was last empty — an id,
once assigned, is never handed to a different task. Deleting a task
retires its id permanently for that stretch of history; `complete` and
`delete` never reassign ids either.

This matters in practice because a task's id often gets written down
somewhere outside tinytodo itself — a commit message, a chat log, a
note — before the task is deleted. If a deleted task's id could be
reused, a reference like "closed in #3" would become ambiguous as soon
as some unrelated new task also became #3.

## The limit

The guarantee is cheaper than it sounds: tinytodo keeps no separate
record of "the highest id ever assigned." The next id is always one more
than the highest id *currently in the file*
(`max(t.id for t in tasks) + 1`). That's indistinguishable from "highest
id ever assigned" right up until the task list becomes completely empty
— at which point there's nothing left in `todo.json` to infer the prior
high-water mark from, and the next task added gets id `1` again, exactly
like a brand-new store would.

So the real guarantee is narrower than "ids are never reused, full
stop": it's "ids are never reused as long as the task list hasn't been
fully emptied out in between." Delete every task and start over, and the
counter silently resets.

## Why it's built this way, not with a persisted counter

A persisted "highest id ever assigned" counter would close the
reset-on-empty gap and make the guarantee hold unconditionally. tinytodo
doesn't do this — it's judged more state than a tool this small
currently justifies. See `decisions/0001-task-ids-are-never-reused.md`
for the full tradeoff.

## What's actually been checked here

- Ids are not reused while at least one other task still exists: checked
  by an automated test
  (`tests/test_tinytodo.py:9-18`,
  `test_ids_are_never_reused_after_delete`).
- A fresh store's first task gets id 1: checked by an automated test
  (`tests/test_tinytodo.py:21-25`, `test_fresh_store_starts_at_one`).
- The reset-to-1-after-emptying-everything behavior described above: only
  confirmed by a one-off manual check, not by a committed, repeatable
  test. If `_next_id` were ever changed in a way that broke this
  specifically, nothing in the test suite today would catch it.

This page is written from, and every claim above traces to,
`planning/knowledge/snapshots/task-ids@v1.toml#task-ids-001` — cite that
snapshot version, not this page or the live assertion record, if you need
to check what was actually known and verified at the time this was
written. (That snapshot itself is only partially frozen in the strict
sense the snapshot format wants — see its own header note — because the
assertion record it cites hasn't been committed in this exercise; treat
this page as accurate to the live state as of 2026-10-01 regardless.)
