# Adversarial falsification attempt: `id-reuse-002`

**Role**: domain-skeptic (fresh dispatch, no memory of how `id-reuse-002`
was produced).

**Target**: `planning/knowledge/assertions/id-reuse-002.md` — the claim
that the pre-fix `_next_id` (`src/tinytodo.py:36-55` at commit
`b6a1bb5`) computes `candidate = max(current live ids) + 1` (or `1` if
empty) on every call, with "is this a reuse" determined solely by
whether `candidate`'s own numeric value was *ever* assigned to any
earlier task (live or since-deleted) — never by which task was most
recently deleted or whether that task held the max at its own deletion.

## What I checked

1. **Read the real pre-fix source directly**, not the assertion's own
   quotation of it: `git show b6a1bb5:src/tinytodo.py` in the target
   repo (`/tmp/claude-1000/.../scratchpad/exercise2-repro/`). Confirmed
   `_next_id` is exactly:

   ```python
   def _next_id(tasks: list[Task]) -> int:
       if not tasks:
           return 1
       return max(t.id for t in tasks) + 1
   ```

   and confirmed `add()`/`delete()` each do a fresh `_load()` from
   `todo.json`, call `_next_id`/filter, then `_save()` — i.e. the only
   state that exists at all, anywhere, is the current contents of
   `todo.json` (the current live task list). No counter file, no cache,
   no in-memory carry-over between calls. This independently confirms
   the assertion's "no other state" claim at the source level, not just
   by trusting its quotation.

2. **Wrote my own independent reference implementation** from the
   assertion's prose (not copied from the assertion's own `Reference`
   class description): a model with `ever_assigned: set[int]` and
   `live: set[int]`, where `add()` computes `candidate = max(live)+1`
   or `1`, marks `candidate in ever_assigned` as ground truth for reuse,
   then updates both sets, and `delete(id)` only discards from `live`.

3. **Extracted the real commit `b6a1bb5` source into an isolated
   scratch copy** (`/tmp/.../scratchpad/id-reuse-falsify/tinytodo_prefix.py`)
   and ran it directly — both by importing its `add`/`delete`/
   `list_tasks` functions in a Python harness against isolated temp
   working directories (fresh `todo.json` per sequence), and separately
   via its actual CLI entry point (`python3 tinytodo.py add/delete/list`
   as subprocesses) as a cross-check that the import-based harness
   wasn't exercising a different code path than real usage would.

4. **Ran 18 distinct sequences I designed myself** (not the assertion's
   own two reported counterexamples, not its four "Examples"), comparing
   the real code's returned id against my reference model's predicted
   candidate on every single `add` call, and real/reference agreement on
   every `delete`'s return value:

   - `repeated_delete_readd_same_slots` — delete id 3 then re-add, delete
     id 2 then re-add, repeated 10 times in a row (candidate flip-flops
     between two slots under many iterations).
   - `middle_out_delete_all_10` — 10 tasks, deleted in a scrambled
     middle-out order (5,6,4,7,3,8,2,9,1,10), then 5 more adds.
   - `delete_nonexistent_interleaved` — deletes of ids that were never
     assigned (999, 42) and double-deletes of an already-deleted id (1),
     interleaved with real adds.
   - `keep_first_alive_then_kill_it_last` — kill ids 2-6 first while id 1
     and a growing max survive, add twice more, then finally delete id 1
     last and add again (tests whether "most specifically the long-lived
     survivor's own removal order" leaks into the formula — it doesn't).
   - `descending_delete_all_15_then_20_adds` / `ascending_delete_all_15_then_20_adds`
     — delete all 15 tasks in strict descending and then strict
     ascending id order, each followed by 20 more adds (walks the
     `ever_assigned` set back down from both directions).
   - `reset_to_one_repeated_dynamic` — fully empty the list and refill
     it 4 times in a row (tests the "resets to 1" claim under repetition,
     not just once).
   - `always_delete_the_one_just_added_dynamic` — add then immediately
     delete the just-added task, 8 times in a row (never any reuse
     possible in this shape — checks the formula doesn't spuriously
     predict a reuse here).
   - `fuzz_seed_{1,2,3,4,5,100,999,12345,54321,777}_len40` — 10
     independent pseudo-random sequences of 40 operations each (~55%
     add, ~36% delete-a-real-live-id, ~9% delete-an-invalid-id), id
     choice for delete drawn from the actual live set returned by
     `list_tasks()` at each step.
   - Two further ad hoc checks run outside the harness file: 10 more
     fuzz sequences of **200** steps each (seeds 2000-2009, heavier
     delete bias) and one sequence interleaving `complete()` calls
     (marking tasks done) between adds/deletes, to confirm the `done`
     flag has no bearing on `_next_id`'s id arithmetic.
   - One CLI subprocess cross-check (`tinytodo.py add/add/add/delete 2/
     delete 3/add/list`) reproducing the assertion's own first reported
     example end-to-end through the real command-line entry point, not
     just via direct function import — result matched (`#2` reused),
     confirming the import-based harness isn't exercising a different
     path than real usage would.

   Total: roughly 18 scripted sequences + 10 extra 200-step fuzz runs +
   1 `complete()`-interleaving check + 1 CLI cross-check, covering
   several thousand individual add/delete operations.

## Result

**Zero mismatches** between the real code's returned id (and real
delete's success/failure) and my independently-written reference
model's prediction, across every sequence above, including the 200-step
high-volume fuzz runs and the deliberately adversarial
delete-order/delete-nonexistent/repeated-reset/complete-interleaving
shapes.

This is consistent with the assertion being a **correct, complete**
description of the mechanism: given that `_next_id` is a pure function
of "`tasks`, the current live list loaded fresh from `todo.json` this
call" with no other state read anywhere in `add`/`delete`/`_load`/
`_save`, the `max(live)+1`-or-`1` formula combined with an
"ever-assigned-before" reuse criterion is not just empirically matching
by luck — it is the only possible behaviour a stateless `max(live ids)+1`
computation can produce, and my harness's reference model is a direct,
independently-derived restatement of that same arithmetic fact. I did
not find a sequence where "which task was most recently deleted" or
"whether that task held the max id at its own deletion" produces a
different, correct prediction that the `max`/`ever_assigned` formula
gets wrong — every attempt to construct such a sequence (deliberately
targeting the max-holder's deletion timing, order-of-deletion effects,
and repeated reset-to-empty cycles) produced results the simpler formula
already predicted correctly.

## Verdict

**The claim survived this falsification attempt.** I did not find a
counterexample. No new Evidence record is needed beyond what
`id-reuse-002.md` already cites, since my own independent re-derivation
corroborates rather than contradicts it — it adds confirmatory evidence
volume but surfaces no new fact requiring the assertion's own `status`
or `Evidence-support state` to change. I am not recommending any edit to
`id-reuse-002.md` itself (out of this role's write boundary regardless),
and I am not escalating anything to the domain owner, since no genuine
ambiguity was found — only agreement between the claim and the real,
directly-executed code.

## Scratch artifacts (not part of this repo; for reproducibility only)

- `/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/id-reuse-falsify/tinytodo_prefix.py`
  — unmodified `src/tinytodo.py` as of commit `b6a1bb5`, extracted via
  `git show`.
- `/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/id-reuse-falsify/harness.py`
  — the 18-sequence harness plus independent reference model described
  above.
- `/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/id-reuse-falsify/cli_test/`
  — CLI subprocess cross-check directory.
