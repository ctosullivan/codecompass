# Assertion: id-reuse-001

**CORRECTION (2026-10-02): the Statement below is itself overgeneralized
and, in its specific causal claim, FALSE — independently reproduced and
disproven. Superseded by `id-reuse-002.md`.** It claimed reuse "happens
... whenever that deleted task held the highest id among the tasks live
at the moment of its deletion" — i.e. that whether a specific id gets
reused can be determined from which task was most recently deleted and
whether that task held the max at that moment. Two real counterexamples,
run against the real, unmodified pre-fix `_next_id`:

```
add 1, 2, 3 -> delete 2 (NOT the max at its own deletion -- 3 still is)
            -> delete 3 (now the max)
            -> add: new id = 2
```

By this assertion's own rule, deleting id 2 (not the max at that moment)
should never cause reuse, and deleting id 3 (the max at that moment)
should make *3* available for reuse. Neither prediction holds: the id
that actually gets reused is **2**, the one this assertion's own rule
said was safe — and a further `add` immediately after this sequence
produces id 4, never id 3, showing id 3 is never reused in this sequence
at all. The rule this assertion stated is not a looser approximation of
the truth; it makes a wrong prediction about *which specific id* gets
reused.

The actual mechanism (verified against a reference model tracking every
id ever assigned, across multiple sequences including both this one and
the add/add/add/add→delete-4→delete-1→add sequence): `_next_id` computes
one global candidate, `max(current live ids) + 1` (or `1` if the list is
empty), with **no memory of which specific task was most recently
deleted or whether it held the max** — whether that candidate happens to
be a reuse depends only on whether that specific number was ever
assigned before, which depends on the *entire* sequence of adds and
deletes, not on any single most-recent deletion. Full reproduction:
`../../../corrections/id-reuse-reference-model.md`. The rest of this
file is preserved unedited as the historical record of this exercise's
own second, still-incorrect attempt at generalizing `_next_id`'s real
behavior — not current truth.

---

## Statement

`_next_id` (`src/tinytodo.py:36-55`) does **not** implement "task ids
are never reused" as its own docstring (`src/tinytodo.py:37`) claims.
The function actually computes `max(id currently in the list) + 1` (or
`1` if the list is empty) — a function of the *currently present* ids
only, with no record of any id that has ever existed. As a direct
consequence, a brand-new task is assigned the id of a previously
deleted task whenever that deleted task held the highest id among the
tasks live at the moment of its deletion — this reuse happens even
while other, older tasks are still present in the list, not only in
the fully-emptied case the docstring explicitly calls out. Reuse does
**not** occur when the deleted task did not hold the current maximum
id — in that case the surviving maximum (unaffected by the deletion)
still determines the next id, which is strictly new.

## Kind

`boundary` (what the function's id-uniqueness guarantee does and does
not cover) — with a `rule`-kind component, since the docstring itself
asserts a claimed invariant ("ids are never reused") that this record
tests directly against the implementation.

## Basis

`observed_behaviour` — every finding below was produced by running the
real `_next_id`/`add`/`delete` implementation from
`src/tinytodo.py` directly (not by reading the docstring and trusting
it), against three independently constructed, representative delete
sequences.

## Evidence

- `src/tinytodo.py:36-55` — the real `_next_id` source and its
  docstring, as of commit `d287ee7889279198d1e0d94675af6c8240396bd9`
  (repo: tinytodo2, branch `main`, 2 commits, clean working tree at
  time of research).
- `src/tinytodo.py:58-63` (`add`) and `src/tinytodo.py:76-82`
  (`delete`) — the two real call sites that invoke `_next_id` and
  mutate the on-disk task list; both were exercised directly, not
  just `_next_id` in isolation.
- `tests/test_tinytodo.py:9-18`
  (`test_ids_are_never_reused_after_delete`) — the project's own
  existing test. It adds ids 1 and 2, deletes id **1** (the
  *non-maximum* id, since 2 is still live), adds again, and asserts
  the new id is 3. This is exactly Scenario A below — the one case
  where the docstring's claim does hold. The test suite has no case
  covering deletion of the current-maximum id with survivors present,
  and no case covering the fully-emptied list (that second gap is
  partially covered by a *different* test,
  `test_fresh_store_starts_at_one`, which only checks that a
  brand-new store starts at 1 — it does not delete anything first, so
  it does not test the reset-after-full-deletion behavior either).
  (Environment note: `pytest` is not installed in this sandbox —
  `python3 -m pytest` fails with `No module named pytest` — so this
  existing test file was not run via its own test runner. Its exact
  assertions were instead reproduced by hand, in order, against the
  live `tinytodo` module, which is a strictly more direct check of the
  same claim.)
- Three scenarios run directly against the real module
  (`import tinytodo`, `tinytodo.STORE_PATH` repointed to an isolated
  scratch directory per scenario, Python 3.13.5), each adding three
  (or two) tasks, deleting according to the scenario, then adding one
  more task and recording its id:

  **Scenario A — delete a non-maximum id, others (including the
  current max) remain.**
  Sequence: add "t1"(→1), add "t2"(→2), add "t3"(→3); delete(1);
  add "t4".
  Observed: ids after delete = `[2, 3]`; new task id = `4`;
  `new_id_equals_deleted_id = False`.

  **Scenario B — delete the current-maximum id, with other
  (non-maximum) tasks still present.**
  Sequence: add "t1"(→1), add "t2"(→2), add "t3"(→3); delete(3);
  add "t4".
  Observed: ids after delete = `[1, 2]`; new task id = `3`;
  `new_id_equals_deleted_id = True`.

  **Scenario C — delete every task, emptying the list entirely, then
  add.**
  Sequence: add "t1"(→1), add "t2"(→2); delete(1); delete(2);
  add "t3".
  Observed: ids after both deletes = `[]`; new task id = `1`;
  `new_id_equals_a (id 1) = True`.

## Justification

`_next_id`'s own implementation (`max(t.id for t in tasks) + 1` /
`1` if empty) only ever looks at the task list as it currently stands
on disk — it has no separate counter or high-water-mark record of ids
that existed in the past. Scenario B shows this directly: deleting
the task that happens to hold the current maximum id removes the only
evidence that id 3 was ever assigned, so the very next `add` recomputes
the max from the two survivors (ids 1 and 2) and reassigns exactly the
id that was just deleted — while two older tasks (ids 1, 2) are still
present and unaffected. This is a strictly more general failure of the
"never reused" guarantee than the fully-empty case: it requires no
special "list is now empty" condition, only that the deleted task was
the current maximum. Scenario C is the degenerate case of the same
root cause and is the one case the docstring's own final paragraph
already (correctly) concedes. Scenario A is the case that does not
reuse — because the deleted id was not the maximum, the surviving
maximum is untouched by the deletion and still produces a new, unused
id — and it is also the only case the project's existing test suite
actually exercises.

## Examples

- Scenario A (non-max delete): ids [1,2,3] → delete 1 → add → new id
  4. No reuse. (Matches `tests/test_tinytodo.py`'s existing test.)
- Scenario C (empty-then-add), restated per the docstring's own
  admission: ids [1,2] → delete 1, delete 2 → add → new id 1 (id 1
  reused). The docstring explicitly names this case as the known
  exception to its own "never reused" headline claim.

## Counterexamples

- **Scenario B is a real counterexample to the docstring's headline
  claim ("Task ids are never reused, even after a task is deleted")
  that the docstring's own caveat paragraph does not name or cover.**
  The docstring's caveat only describes the fully-emptied-list case
  ("deleting every task and starting fresh resets the counter to 0,
  because there's nothing left to infer the prior high-water mark
  from"). It does not mention — and, read literally, its second
  paragraph's claim that "the next id is always one more than the
  highest id *ever* assigned" directly contradicts — the case
  observed in Scenario B: deleting only the current-maximum task,
  while other, older, lower-numbered tasks remain, is enough on its
  own to reuse that id on the very next `add`. No full-list emptying
  is required. This is a real defect in the docstring's own stated
  guarantee, not merely an edge case it chose not to document in
  detail: the sentence "the next id is always one more than the
  highest id *ever* assigned, not one more than the highest id
  *currently present*" is factually false as a description of the
  code immediately below it — the implementation literally is "one
  more than the highest id currently present," full stop, with no
  separate tracking of ids ever assigned.
- Scenario A found no reuse — included here for completeness as a
  case genuinely checked and not contradicting the claim, per the
  template's instruction that an empty Counterexamples section means
  "looked and found none," not "didn't check." (This entry is not
  itself a counterexample; it is recorded to show Scenario A was
  checked, not skipped.)

## Depends on

(none)

## Open questions

- Is "ids are never reused" a product requirement this project
  actually needs, or is it dead/aspirational text in a docstring that
  was never validated against the implementation it describes? This
  record only establishes what the code *does*; whether the code
  should be changed (e.g. persisting a true high-water-mark counter
  separately from the task list) is a product decision this record
  does not make and is not entitled to make.
- Given Scenario B's result, is the project's existing test
  (`test_ids_are_never_reused_after_delete`) actually sufficient
  coverage for the claim its own name makes? As run by hand here, it
  only ever exercises the non-maximum-delete path (Scenario A) and
  would pass unchanged even though the maximum-delete path (Scenario
  B) reuses an id on the very next add.

## Evidence-support state

`conflicting` — the evidence directly supports the docstring's own
closing caveat about the fully-emptied case (Scenario C), but directly
contradicts the docstring's own headline claim and its "ids ever
assigned" reasoning (Scenario B), and separately confirms the one case
(Scenario A) where no reuse occurs. The statement above is not a single
uniform "true" or "false" verdict because the real behavior itself is
conditional, and the docstring's own text is internally inconsistent
about which conditions it covers.

## Status

`contradicted` — specifically, the docstring's headline sentence ("Task
ids are never reused, even after a task is deleted") and its "highest
id *ever* assigned" reasoning are contradicted by Scenario B's directly
observed behavior. The docstring's narrower, final-paragraph admission
about the fully-emptied case is not contradicted (see Scenario C).

## Supersedes

(none)
