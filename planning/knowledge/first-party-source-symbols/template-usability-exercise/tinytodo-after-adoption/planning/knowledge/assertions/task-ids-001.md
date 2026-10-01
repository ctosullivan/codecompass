# Assertion: task-ids-001

**CORRECTION (2026-10-01, Phase 79 sixth amendment, CodeCompass
`planning/knowledge/first-party-source-symbols/`): the Statement below
is FALSE, independently reproduced and disproven.** It claimed "a task
id, once assigned, is never reassigned to a different task... including
after the task holding it is deleted," scoped only by "unless the task
list has been fully emptied." That scoping is itself still wrong. Real,
independently-run reproduction:

```
add "first"  -> id 1
add "second" -> id 2
delete(2)                      # delete the HIGHEST id, list NOT emptied
add "third"  -> id 2           # REUSED -- task 1 still exists
```

Both ids present after this sequence: `[(1, "first"), (2, "third")]` —
the original task-2 is gone, its id handed to an unrelated new task,
while task 1 (a different, still-live task) remains. The list was never
emptied. The assertion's own "Counterexamples" section claimed to have
"looked for a case where a deleted id gets reused *while other tasks
still exist* — found none," reasoning that `max(...)+1` over a
non-empty list "can never produce an id already present, since by
definition it exceeds every id in the list, live or not." That reasoning
conflates "exceeds every id *currently* in the list" with "exceeds every
id *ever* assigned" — exactly the distinction `_next_id`'s own docstring
claims to draw correctly and does not. The counterexample was not found
because it was not actually searched for along the one axis that matters
(which specific id gets deleted — highest vs. not), only varied along
irrelevant axes (how many tasks, which one tested first).

**The real, implemented guarantee** is narrower than either the original
Statement or its own "fixed" rescoping below: an id is safe from reuse
only if the task holding it is deleted while a *strictly higher* id is
still live (or added afterward before any further add). Deleting
whichever task currently holds the *highest* live id, at any point,
makes that id available for reuse by the very next `add` — regardless of
how many other tasks exist or survive. Full reproduction, including the
representative deletion cases below, is at
`../../../../corrections/task-ids-reproduction.md` in this same exercise
evidence tree. The rest of this file is preserved unedited as the
historical record of what this exercise originally (wrongly) concluded
and why — including the flawed reasoning above — not as current truth.

---

## Statement

Within one `todo.json`'s continuous history (i.e. since the file was last
empty), a task id, once assigned, is never reassigned to a different
task — including after the task holding it is deleted. The next id
`_next_id` hands out is always `max(current task ids) + 1`, not a count
of tasks or a persisted "highest ever assigned" counter; if every task is
deleted, the next id resets to 1, because nothing in `todo.json` retains
the prior high-water mark once the task list is empty.

## Kind

`invariant`

## Basis

`directly_stated` — `_next_id`'s own docstring in `src/tinytodo.py`
states both the guarantee and its limit outright, in these words.

## Evidence

- `src/tinytodo.py:36-55` — `_next_id`'s implementation
  (`max(t.id for t in tasks) + 1`, or `1` if `tasks` is empty) and its
  docstring, which states the "never reused" guarantee and names the
  delete-everything caveat explicitly.
- `tests/test_tinytodo.py:9-18` — `test_ids_are_never_reused_after_delete`:
  adds two tasks (ids 1, 2), deletes id 1, adds a third task, and asserts
  its id is 3 (not 1). Ran manually on 2026-10-01 (pytest unavailable in
  this environment; ran the test body directly with plain Python) —
  passed.
- `tests/test_tinytodo.py:21-25` — `test_fresh_store_starts_at_one`:
  confirms a brand-new store's first task gets id 1. Ran manually
  alongside the above — passed.
- Ad hoc manual check (2026-10-01, not currently a committed test): added
  two tasks (ids 1, 2), deleted *both*, then added a new task — its id
  was `1`, i.e. the id of the first, now-fully-forgotten task was reused.
  This is the exact scenario the docstring's caveat describes and it is
  **not** covered by either existing test — both only delete one task out
  of two, never emptying the list. Command run:
  `python3 -c "..."` against a fresh `tempfile.TemporaryDirectory()`,
  output: `c.id after deleting ALL tasks: 1`.

## Justification

The two existing tests directly exercise the "never reused while at
least one other task survives" half of the statement and both pass. The
ad hoc manual check directly exercises the "resets to 1 once the list is
fully emptied" half, which the docstring claims but no committed test
currently verifies — the evidence supports the full statement, but one
clause of it rests on an uncommitted, manual observation rather than a
regression-tested one.

## Examples

- Add "a" (id 1), add "b" (id 2), delete "a" → add "c": c gets id 3, not
  1 (tested).
- Add "a" (id 1) → delete "a" → add "b": b gets id 1, because the list
  was empty at the moment `_next_id` ran (observed manually, not tested).

## Counterexamples

Looked for a case where a deleted id gets reused *while other tasks still
exist* — found none; `max(...)+1` over a non-empty list can never produce
an id already present, since by definition it exceeds every id in the
list, live or not. The only way to get reuse is to empty the list first,
which is the documented, accepted caveat, not a counterexample to the
statement as scoped ("within one continuous history").

## Depends on

None.

## Open questions

The "resets to 1 after deleting everything" behavior has no regression
test. If `_next_id` were ever accidentally changed to persist a
high-water mark (closing that gap) or to break it further (e.g. starting
from 0), nothing would currently catch either change. Worth a
`test_id_resets_after_deleting_every_task` test — flagged as a candidate
in this project's own `planning/knowledge/` learnings log, not added to
`tests/` directly as part of this documentation exercise, since adding
tests wasn't the task at hand here.

## Evidence-support state

`partially_supported` — the "never reused while survivors exist" clause
is backed by a passing committed test; the "resets on full-empty" clause
is backed only by one manual, uncommitted observation.

## Status

`supported`

## Supersedes

(none)
