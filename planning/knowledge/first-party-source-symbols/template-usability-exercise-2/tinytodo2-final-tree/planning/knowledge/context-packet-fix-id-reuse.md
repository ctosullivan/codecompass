# Coding-context packet: fix `_next_id` so a deleted task's id is never reused

A packet assembled from a frozen knowledge snapshot for one specific,
bounded coding task — not a topic overview of `tinytodo.py`.

**CORRECTED (2026-10-02)**: this packet previously described the bug's
precise trigger as "the deleted task held the current maximum id at the
moment of its deletion," and separately claimed reviewer scenarios D/G/
J/K ruled out any dependency on prior reuse history or repeated cycles.
Both statements were independently reproduced as false: whether reuse
occurs is governed by the current live maximum at `add` time (across
the *entire* history of adds/deletes), never by any single deletion
event in isolation — see `id-reuse-002.md`'s own correction of
`id-reuse-001.md` and `../../corrections/id-reuse-reference-model.md`
for the full counterexample. **The recommended fix approach below
(persist a high-water-mark counter) is unaffected by this correction**
— it eliminates reuse unconditionally regardless of the precise trigger
rule — but the bug-mechanism description and the regression-test
rationale that follow have been corrected to match the real mechanism.

## The task

Fix `_next_id` (`src/tinytodo.py`) so that a deleted task's id is
genuinely never reused, matching the original (currently false)
docstring claim — without breaking the existing two tests
(`tests/test_tinytodo.py`).

## Snapshot cited

`id-reuse@v2` (superseding `id-reuse@v1`, which cited `id-reuse-001`'s
own since-corrected rule) — frozen at `repository_revision_at_freeze =
76adc71` (the correction commit). If the live knowledge base or the live
repository has moved past this version since, that divergence is
expected and informational — it doesn't invalidate this packet, but
staleness against a later revision should be rechecked before relying on
it further.

## Assertions included, and why each one

- **`id-reuse-002`** (`planning/knowledge/assertions/id-reuse-002.md`)
  — the governing assertion, superseding `id-reuse-001` (whose own
  causal rule, "reuse depends on whether the most-recently-deleted task
  held the current maximum id," was independently reproduced as false —
  see `id-reuse-001.md`'s own correction notice). Included in full
  because it is the only record that states *why* the bug happens (no
  persisted high-water-mark, only `max(current live ids) + 1`) and the
  precise, history-dependent condition under which reuse actually
  occurs (the current candidate was ever assigned before — not "list
  became empty," and not "the most recently deleted task held the max").
  The task cannot be done correctly without this causal mechanism;
  without it, a fix might only patch the fully-emptied case the
  docstring already (correctly) admits, leaving the more general defect
  in place.
- **`id-reuse-001-review-evidence.md`** (supplementary evidence) —
  included for two specific, task-relevant facts it adds, with one of
  its own original claims now corrected:
  1. Independent re-confirmation that `src/tinytodo.py` has **no
     separate counter, no module-level state, and only one persisted
     file (`todo.json`, via `STORE_PATH`)** — this directly bounds the
     fix: there is currently nowhere for a high-water mark to live, so
     the fix must add storage, not just change an expression.
  2. Confirmation that the two existing tests were executed literally
     (not hand-retyped) and still only exercise the non-maximum-delete
     path — raising confidence that the "existing two tests don't
     break" and "existing two tests don't already catch this" claims
     are solid, not an artifact of the original record's own
     hand-reproduction method.
  3. **Corrected**: this evidence file's own scenarios D/G/J/K were
     originally read as confirming "no hidden interaction with an id's
     own reuse history" under the old (wrong) "most recent deletion"
     rule. That reading does not carry over to the corrected mechanism
     — reuse genuinely does depend on the complete add/delete history,
     not on any single event — so this packet no longer cites those
     scenarios as evidence of "no interaction effects." They remain
     valid as raw observations; only their interpretation under the old
     rule is withdrawn.

## What was deliberately left out

- **The live source code and live test file.** Per this task's own
  scope, the packet draws only on what `id-reuse-001.md` and its review
  evidence already quote/paraphrase (line ranges, the docstring's exact
  claim sentence, the two existing tests' exact behaviour) — it does not
  independently re-read `src/tinytodo.py` or `tests/test_tinytodo.py`.
  Anyone implementing from this packet should expect to open those two
  files directly when writing the actual diff; the packet orients, it
  does not substitute for reading the five-line function being changed.
- **Other `planning/knowledge/` records** (`documentation-verification.md`,
  `implementation-reconstruction.md`, `alignment-report.md`) — none of
  these are cited by `id-reuse@v2`'s own snapshot manifest, so none are
  in scope for this packet regardless of topical adjacency.
- **The eight additional lettered scenarios (D–L)** from the review
  evidence, verbatim — only the *corrected, generalized rule* is carried
  into this packet below: reuse occurs iff the current `max(live)+1`
  candidate was ever assigned before, which depends on the full
  add/delete history, not on any single deletion event. The
  scenario-by-scenario narrative is detail the task doesn't need once
  the rule itself is stated and trusted.
- **The assertion's first Open Question** ("is 'ids are never reused' a
  product requirement this project actually needs, or dead/aspirational
  docstring text?"). The frozen task already answers this for us — fix
  the code to match the docstring's claim — so re-litigating whether
  the requirement is worth having would reopen a scope question this
  packet's task statement has already closed.
- **The precise textual self-contradiction inside the docstring**
  (the assertion's `Counterexamples` section's close reading of "ids
  *ever* assigned" vs. "ids *currently present*"). Useful for someone
  rewriting the docstring's prose, but the task only requires making the
  claim true, not auditing the claim's own wording — one line below
  (in "Non-goals") flags that the docstring text will still need a
  look, without importing the full textual analysis.

## What the packet establishes

### The actual bug, precisely

`_next_id` computes `max(id of every task currently in the on-disk
list) + 1` (or `1` if the list is empty). It has **no separate
high-water-mark counter or any other record of ids that existed in the
past** — confirmed by direct source inspection (no `counter`, no second
persisted file, no module-level state; the function's only input is the
freshly-loaded `tasks` list).

Consequence: a newly added task reuses a previously-deleted task's id
whenever that candidate number (`max(current live ids) + 1`) was ever
assigned to some earlier, now-deleted task — this is **not** determined
by which task was most recently deleted, or by whether that task held
the maximum id at its own deletion. It depends on the complete history
of every add/delete call in sequence. This fires even while other,
older, lower-numbered tasks are still live, and is not limited to the
fully-emptied-list case the docstring's own closing paragraph already
(correctly) concedes; that case is simply the degenerate instance of the
same root cause (`candidate = 1` once the list is empty).

Directly observed counterexample to "look at the most recent deletion":
ids `[1,2,3]` → delete `2` (not the max at that moment — `3` still is)
→ delete `3` (now the max) → add → new id is **`2`**, not `3`. The task
whose own deletion "held the max" (`3`) is never reused in this
sequence at all; the task whose own deletion did *not* hold the max
(`2`) is the one that gets reused. A further add immediately afterward
produces `4`, confirming `3` stays permanently unreused in this
sequence. Verified against a reference model tracking every id ever
assigned, across 5 sequences plus an independent 18-sequence
falsification attempt, with zero deviation from the `max(live)+1`/
`ever-assigned-before` formula.

### An approach that would close it

Replace "derive the next id from whatever the current list's maximum
happens to be" with "read and advance a **persisted high-water-mark
counter that is never affected by deletion**."

Concretely:

- **New state needed**: a counter value (e.g. `next_id` or
  `last_assigned_id`) that is incremented on every `add` and never
  decremented or recomputed from the task list on `delete`.
- **Where it lives**: the review evidence confirms there is currently
  exactly one persisted file, `todo.json` (via `STORE_PATH`), and no
  other state anywhere in the module. The natural place for the new
  counter is inside that same file — e.g. restructuring its top-level
  shape from a bare task list to an object holding both the task list
  and the counter (`{"next_id": N, "tasks": [...]}`), rather than
  introducing a second state file. `_next_id` would then read and
  return the persisted counter's current value and immediately persist
  `counter + 1` back to `todo.json`, instead of calling
  `max(t.id for t in tasks)`.
- **Bootstrap behaviour**: a fresh store (no counter present yet) must
  still initialize the counter so the first id is `1`, preserving
  `test_fresh_store_starts_at_one`.
- This is a genuine state/format change to the on-disk store, not a
  pure code-expression fix — any implementation plan should say so
  explicitly rather than presenting it as a one-line change.

### Test case(s) needed to actually catch a regression of this specific bug

The existing two tests do **not** cover this:
`test_ids_are_never_reused_after_delete` deletes id `1` from `[1, 2]`
(the non-maximum id, Scenario A) — the one case that was never broken —
and `test_fresh_store_starts_at_one` never deletes anything at all. A
fix could regress and both would still pass.

New case(s) required:

1. **Direct regression test for Scenario B**: add three tasks (ids `1`,
   `2`, `3`); delete the task holding the *current maximum* id (`3`),
   leaving `1` and `2` live; add a new task; assert its id is **not**
   `3` (i.e. is `4`). This exercises one real reuse case — deleting the
   max while older tasks survive — the current test suite has no
   equivalent of.
2. **Multi-deletion regression test (required, not merely
   recommended)**: add three tasks (ids `1`, `2`, `3`); delete `2` (not
   the max at that moment), then delete `3` (now the max); add a new
   task; assert its id is `2`, **not** `3`. This is the counterexample
   that falsifies a fix (or a test) built around "reuse happens iff the
   *most recently deleted* task held the max" — a plausible-looking but
   wrong simplification this packet's own earlier draft made. A fix
   that merely special-cases "the task that was deleted right before
   this add" rather than genuinely tracking a persisted high-water mark
   could pass case 1 above while still failing this one.
3. **Multi-cycle persistence check** (recommended, not strictly
   required to catch the base bug but needed to catch a fix that
   "accidentally" avoids reuse once without truly persisting a
   high-water mark): repeat delete-the-current-max → add → assert
   no-reuse for a second cycle in the same run (mirrors review-evidence
   scenario D/G), so a fix that merely nudges `max()` by one in some ad
   hoc way, rather than tracking a real persisted counter, cannot pass
   by coincidence.
4. **Persistence-across-reload check** (recommended if the fix persists
   the counter to disk, which the approach above requires): after an
   add/delete/add sequence, reload the store from disk (simulating a
   fresh process) and confirm the next id still continues from the
   high-water mark rather than resetting — this is the test that would
   catch an implementation that keeps the counter only in memory
   instead of in `todo.json`.

The existing fully-emptied-list behaviour (Scenario C, reuse of id `1`
after emptying the list) is *not* something to newly test for
reuse-freedom under this task's fix — the docstring's own caveat already
names it as the known exception, and whether the fix is meant to close
that case too or leave it as documented behaviour is itself unresolved
(see Non-goals below).

### Non-goals (explicitly out of scope for this packet's task)

- Rewriting the docstring's prose/self-contradiction is not covered
  here; once the code is fixed, the docstring's claim becomes true, but
  its own internal wording issue (see id-reuse-001's Counterexamples
  section) is a documentation task, not named as part of this bounded
  coding task.
- Whether the fully-emptied-list case (Scenario C) should *also* stop
  reusing ids (i.e., whether the docstring's own caveat is something to
  preserve or eliminate) is an open product question the cited assertion
  explicitly declines to resolve. This packet does not resolve it either
  — a persisted high-water-mark counter that is never reset would
  naturally also close Scenario C as a side effect, but that is a
  consequence to flag during implementation, not a requirement this
  packet asserts.

## Independent assessment

Not yet performed. Per the governing template, this packet is a draft
until an evaluator who inspects `src/tinytodo.py` and
`tests/test_tinytodo.py` directly rates whether it gave a genuine
advantage over no packet (LOW / MODERATE / HIGH) and flags anything
material missing. That assessment is out of scope for packet assembly
itself and is not performed by the assembling agent.
