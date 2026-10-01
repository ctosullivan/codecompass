# Evidence (supplementary): independent adversarial review of id-reuse-001

This is a new Evidence record, not an edit to `id-reuse-001.md`'s own
`Statement`. It was produced by an independent review dispatch re-running
the claim's three cited scenarios and testing eight additional scenarios
the original record did not cover, directly against the real
`src/tinytodo.py` at commit `641daf64be3e6ef7daec0d57c08ac17fd52bc708`
(repo: tinytodo2, branch `main`, clean working tree). No claim, derivation,
or decision is made here — see `id-reuse-001.md` for the governing
assertion, and `planning/knowledge/documentation-verification.md` for the
reviewer's full findings.

## Basis

`observed_behaviour` — every item below was produced by running the real
`add`/`delete`/`_next_id` implementation, not by re-reading the docstring
or the assertion's own prose.

## Evidence

1. **Re-derivation of the assertion's own three scenarios**, run fresh in
   an isolated scratch directory (Python 3.13.5), reproduced the exact
   reported outcomes verbatim:
   - Scenario A (delete non-max id 1 from `[1,2,3]`, add): new id `4`.
     Matches.
   - Scenario B (delete max id 3 from `[1,2,3]`, add): new id `3`
     (equals the just-deleted id). Matches.
   - Scenario C (delete all of `[1,2]`, add): new id `1`. Matches.

2. **Eight additional scenarios**, not in the original record, run the
   same way, to test whether "reuse iff the deleted task held the
   current maximum id" generalizes beyond the three original cases:
   - D — delete max, then add twice (`[1,2,3]` → delete 3 → add → `3`
     [reuse] → add → `4` [no reuse, since 3 is now the live max]).
   - E — delete a *middle* id, 4 tasks present (`[1,2,3,4]` → delete 2 →
     add → `5`). No reuse — consistent with the rule, since id 2 was
     never the max.
   - F — delete max, add (reuse), then delete a nonexistent id (no-op),
     then add again: no further reuse (next id `4`, fresh).
   - G — full-empty-then-reuse, followed by a second max-delete-then-
     reuse cycle in the same run: both reuse exactly as predicted, with
     no dependence on the earlier reuse having already happened.
   - H — delete of a nonexistent id (`delete(99)`) is a no-op (`False`
     return, confirmed against `delete`'s own `len(remaining) ==
     len(tasks)` guard) and does not disturb subsequent id assignment.
   - I — single-task add/delete/add (the minimal case of the
     fully-emptied pattern): reuses id `1`, consistent with Scenario C,
     not a new behaviour class.
   - J — a reused id (`3`, reused in an earlier step) is later itself
     deleted non-max-first then the new max deleted: no-reuse and reuse
     fire exactly where the general rule predicts, with no special
     behaviour tied to an id's own reuse history.
   - K — deleting an id that was itself the product of an earlier reuse,
     at a time when it is again the current max, reuses it a second time
     (`3` → delete → add → `3` again). Confirms the function carries no
     memory of an id's reuse history, exactly as the assertion's
     `_next_id`-reads-only-the-current-list reasoning predicts.
   - L — delete non-max (no reuse) immediately followed by emptying the
     list via a second delete (reuse): the two behaviours coexist in one
     run exactly as the general rule predicts, with no interaction
     effect between them.

   All eight additional scenarios are consistent with the assertion's
   stated general rule ("reuse occurs iff the deleted task held the
   current maximum id at the moment of deletion; otherwise the surviving
   maximum, untouched by the deletion, still determines a strictly new
   next id") and surfaced no counterexample to it, no missed case, and no
   case where a previously-reused id behaves differently from a
   never-reused one.

3. **Source re-confirmation of "no separate counter" claim**: grepped
   `src/tinytodo.py` for `counter`, `global`, and any second persisted
   path beyond `STORE_PATH`; confirmed only one state file
   (`todo.json`, via `STORE_PATH`) exists, `_next_id` takes only the
   freshly-`_load()`-ed `tasks` list as input, and there is no
   module-level or on-disk high-water-mark state anywhere in the file.

4. **Literal (not hand-reproduced) execution of both existing tests**:
   `pytest` is confirmed still unavailable in this review's environment
   (`python3 -m pytest` → `No module named pytest`, matching the
   original record's own environment note), but both test functions'
   *actual bodies* from `tests/test_tinytodo.py` (not a paraphrase) were
   imported and executed directly against the real `tinytodo` module
   with a minimal stand-in for pytest's `tmp_path`/`monkeypatch`
   fixtures (a real temp directory, a `chdir`-only monkeypatch
   substitute). Both passed exactly as asserted:
   - `test_ids_are_never_reused_after_delete` — passes (exercises only
     the non-maximum-delete path, confirming the original record's gap
     claim that this test does not cover Scenario B).
   - `test_fresh_store_starts_at_one` — passes (does not delete anything
     first, confirming it does not test the reset-after-full-deletion
     path either).
   This is strictly more direct than the original record's hand
   reproduction, since the real test code itself ran, not an
   independently-retyped equivalent of it — and it reaches the same
   conclusion.

## Conclusion of this evidence record

All of the above corroborates `id-reuse-001.md`'s `Statement`,
`Justification`, `Examples`, and `Counterexamples` sections without
finding any discrepancy, missed scenario, or overstatement. See
`planning/knowledge/documentation-verification.md` for the full review
report and its verdict on the assertion's `status` and
`evidence_support_state` fields.
