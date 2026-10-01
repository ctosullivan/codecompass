# Assertion: id-reuse-002

Supersedes `id-reuse-001.md`, whose own causal claim ("reuse depends on
whether the most-recently-deleted task held the current maximum id")
was independently reproduced and disproven — see that file's own
correction notice and `../../../corrections/id-reuse-reference-model.md`
for the full counterexample evidence this assertion is built from.

## Statement

The pre-fix `_next_id` (`src/tinytodo.py:36-55` at commit `b6a1bb5`)
computes exactly one thing on every call: `candidate = max(id over the
*current*, live task list) + 1`, or `candidate = 1` if the list is
currently empty. This is the *entire* mechanism — there is no other
state, no memory of deletions, no tracking of "which task was most
recently removed." Whether a given `add` call's own `candidate` happens
to reuse a previously-assigned id is **not** determined by which task
was most recently deleted, or by whether that task held the maximum id
at its own deletion — it is determined by whether `candidate`'s own
specific numeric value was ever assigned to *any* earlier, now-deleted
task, which depends on the complete history of every `add`/`delete` call
in sequence, not on any single one of them in isolation.

## Kind

`invariant`

## Basis

`observed_behaviour` — verified by direct execution against the real,
unmodified pre-fix implementation, cross-checked against an independent
reference model that tracks every id ever assigned (not inferring
"ever assigned" from what's currently live, the same mistake
`id-reuse-001`'s own rule made).

## Evidence

- `src/tinytodo.py:36-55` at commit `b6a1bb5` — `_next_id`'s real
  implementation: `max(t.id for t in tasks) + 1` if `tasks` is
  non-empty, else `1`. No other state read or written.
- Direct reproduction of the two reported counterexamples:
  - `add 1,2,3 → delete 2, then 3 → add`: new id is **2** (not 3 — the
    id whose own holding task *was* the max at its own deletion is
    never reused in this sequence; the id whose own holding task was
    *not* the max at its own deletion is the one reused).
  - `add 1,2,3,4 → delete 4, then 1 → add`: new id is **4** (a reuse —
    in this specific sequence, matching what a "was it the max"
    heuristic would also predict, which is exactly why that heuristic
    survived a first, insufficiently adversarial review: it agrees with
    the truth often enough to look right from a small number of
    examples).
- A reference model (`Reference` class: `ever_assigned: set[int]`,
  `live_ids: set[int]`; `add()` computes `candidate = max(live_ids)+1 or
  1`, flags `candidate in ever_assigned` as the ground truth for reuse,
  then updates both sets; `delete(id)` only removes from `live_ids`,
  never from `ever_assigned`) run against 5 independent, non-trivial
  add/delete sequences, including both reported counterexamples: the
  real implementation's own returned id matched the reference model's
  own `candidate` computation in every single case, with no exception.
  Full transcript: `../../../corrections/id-reuse-reference-model.md`.

## Justification

The reference model's own `candidate` formula is definitionally
identical to what the real code computes (`max(live)+1` or `1`) — the
two matching on every tested sequence is not a coincidence, it is a
direct confirmation that the real code really does implement exactly
this formula and nothing more. The model's *separate* tracking of
`ever_assigned` (independent of `live_ids`) is what correctly classifies
whether a given candidate is a reuse — this is the piece `id-reuse-001`'s
own rule got wrong, because it tried to infer "was this specific id
freed up for reuse" from a single deletion event rather than from the
complete history of every id ever assigned.

## Examples

- `add 1,2,3 → delete 2 → delete 3 → add`: new id `2` (reused). Candidate
  after both deletes: `max({1}) + 1 = 2`. `2 ∈ ever_assigned = {1,2,3}` →
  reuse.
- `add 1,2,3,4 → delete 4 → delete 1 → add`: new id `4` (reused).
  Candidate: `max({2,3}) + 1 = 4`. `4 ∈ ever_assigned = {1,2,3,4}` →
  reuse.
- `add 1 → delete 1 → add`: new id `1` (reused — the fully-emptied case
  `id-reuse-001`'s own docstring quotation already got right).
- `add 1,2,3 → delete 1 → add`: new id `4` (not reused). Candidate:
  `max({2,3}) + 1 = 4`. `4 ∉ ever_assigned = {1,2,3}` → not a reuse.

## Counterexamples

None found against the corrected formula across 5 independently
constructed sequences (including both reported counterexamples to
`id-reuse-001`'s own rule) plus an independent adversarial review (see
`../../../corrections/id-reuse-reference-model.md` for that review's own
account) — every real result matched the reference model's own
`max(live)+1`/`ever_assigned` computation exactly, with zero deviation.

## Depends on

Supersedes: `id-reuse-001`.

## Open questions

None — `id-reuse-001`'s own open questions (whether "never reused" is a
real product requirement) remain open and apply equally here; this
assertion only corrects the *mechanism*, not that separate product
question.

## Evidence-support state

`supported`

## Status

`verified` — the specific causal mechanism (one global `max(live)+1`
candidate, reuse iff that specific number was ever assigned before) was
independently re-derived against a reference model and confirmed with
zero deviation across 5 sequences plus a separate adversarial review
pass, a materially higher bar than `id-reuse-001`'s own `contradicted`
status (which correctly identified that the docstring was wrong, but
not what the actual rule was).

## Supersedes

`id-reuse-001`
