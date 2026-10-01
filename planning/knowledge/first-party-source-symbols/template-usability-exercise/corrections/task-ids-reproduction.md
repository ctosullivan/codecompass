# Correction evidence: `tinytodo`'s task-id reuse claim was false

Phase 79 sixth amendment, 2026-10-01. Corrects a false conceptual claim
produced by the original template-usability exercise's own clean-room
research, in `../tinytodo-after-adoption/`'s own
`planning/knowledge/assertions/task-ids-001.md`, `docs/task-ids.md`, and
`decisions/0001-task-ids-are-never-reused.md` — all three claimed task
ids are "never reused... including after the task holding it is
deleted" (narrowed, still wrongly, to "as long as the task list hasn't
been fully emptied"). Independently reproduced here, directly against
the real, unmodified `tinytodo-after-adoption/src/tinytodo.py`, in an
isolated temporary store (never the committed `todo.json`-less working
tree — this exercise's own project ships no `todo.json` at all; every
run below used a fresh, disposable directory).

## The implementation being tested

```python
def _next_id(tasks: list[Task]) -> int:
    if not tasks:
        return 1
    return max(t.id for t in tasks) + 1
```

`max(t.id for t in tasks) + 1`, computed over the **current, live** task
list — not a persisted "highest id ever assigned" counter, regardless of
what the module's own docstring claims about the two being
indistinguishable.

## Reproduction 1 (the exact sequence named in the sixth-amendment prompt)

```
add "first"   -> id 1
add "second"  -> id 2
delete(2)                      # delete the id-2 task specifically
add "third"   -> ?
```

Real output:

```
after add/add: [(1, 'first'), (2, 'second')]
after deleting task 2 : [(1, 'first')]
new task id: 2
all tasks: [(1, 'first'), (2, 'third')]

CLAIM WAS: ids never reused, even after a task is deleted
REALITY: new task id 2 == deleted task id 2 -> True
```

**The new task received id 2 — the just-deleted task's own id — while
task 1, a different, unrelated task, was still live.** The list was
never emptied at any point. This directly falsifies the original
assertion's own Statement and its "Counterexamples" section's specific
claim that no such case exists.

## Representative deletion cases

### Case A — delete a non-highest (middle/lowest) id

```
add "t1" -> 1; add "t2" -> 2; add "t3" -> 3
delete(1)                      # delete the LOWEST id, not the highest
add "t4" -> ?
```

Real output: `ids after delete(1)+add: [2, 3, 4] -> new id 4 (reused 1? False)`

No reuse — this is the case the exercise's own original, narrower test
(`test_ids_are_never_reused_after_delete`) happened to exercise, and it
genuinely does pass. The original test's defect was never testing the
*other* case below, which is the one that actually breaks the headline
claim.

### Case B — delete the highest id (3 tasks present, list not emptied)

```
add "t1" -> 1; add "t2" -> 2; add "t3" -> 3
delete(3)                      # delete the HIGHEST id
add "t4" -> ?
```

Real output: `ids after delete(3)+add: [1, 2, 3] -> new id 3 (reused 3? True)`

Reuse occurs, with two other tasks (ids 1, 2) still live. This is the
general case the original claim said couldn't happen.

### Case C — delete every task (empty the store), then add

```
add "t1" -> 1; add "t2" -> 2
delete(1); delete(2)
add "t_new" -> ?
```

Real output: `new id after emptying store: 1 (reused either 1 or 2? True)`

Reuse occurs here too — but this specific case **is** the one the
original docstring/assertion/docs page already disclosed as a known,
accepted limitation ("deleting every task and starting fresh resets the
counter"). This case was not itself wrong; it's included here for
completeness, to show it's consistent with the real implementation and
was never the actual gap.

## The real, implemented guarantee

Not "ids are never reused" (the original claim), and not "ids are never
reused unless the list is fully emptied" (the original claim's own
"corrected, narrower" restatement, also false — see Case B, where the
list is never emptied and reuse still occurs). The actual guarantee,
precisely:

**An id is safe from reuse only if the task holding it is deleted while
a strictly higher id is still live in the list at that moment.** Deleting
whichever task currently holds the maximum live id — regardless of how
many other, lower-numbered tasks exist or survive — makes that id
available for reuse by the very next `add`. This is a materially weaker
guarantee than either version of the original claim, and specifically
the *opposite* of what a reader would need to know before relying on an
id staying retired after deleting the task that currently happens to be
most recently added or highest-numbered — often the most likely task to
be deleted first in ordinary use (e.g. "clear my most recent todo").

## Why the original adversarial check missed this

The original assertion's own "Counterexamples" section reasoned: "`max(...)+1`
over a non-empty list can never produce an id already present, since by
definition it exceeds every id in the list, live or not." This is a
real logical error, not a missing test — it conflates "exceeds every id
*currently* in the list" (true, trivially, by definition of `max`) with
"exceeds every id *ever assigned*" (false in general, exactly when the
deleted task held the current maximum). No search was actually performed
along the one axis that distinguishes the two claims (*which* id gets
deleted — the current maximum, or not) — the only two scenarios tested
(delete a non-maximum id; empty the whole list) both happen to leave the
claim looking true. This is a concrete illustration of why this
project's own clean-room workflow calls for independent, adversarial
review as a separate step, never trusting a single research pass's own
"I looked for a counterexample and found none" to be itself a
sufficient check — the original tinytodo exercise's instructions did not
include dispatching a second, independent adversarial-review pass on its
own research output, unlike the real CodeCompass pilot this template
exists to support.

## Scope note

This file, and the correction notices it's cited from, are the sixth
amendment's own real, independently-reproduced evidence. The commands
above were run directly against the real, unmodified
`tinytodo-after-adoption/src/tinytodo.py`, in a disposable temporary
directory created and destroyed for this purpose, never against the
committed `df80660` tinytodo project (which ships no `todo.json` of its
own). No file under `tinytodo-after-adoption/src/` or `tests/` was
modified by this correction — only the three documents that drew a false
conclusion from (correctly) reading that unmodified source.
