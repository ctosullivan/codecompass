# `_next_id` id-reuse behavior

**CORRECTED (2026-10-02)**: this page previously stated that reuse is
determined by "whether the deleted task held the current maximum id at
the moment of its deletion." That rule was independently reproduced as
false (two counterexamples: `add 1,2,3 → delete 2, then 3 → add` yields
id `2`, not the rule's own predicted `3`, and id `3` is never reused in
that sequence) and has been replaced below with the corrected mechanism,
now cited to `id-reuse@v2#id-reuse-002`. See
`planning/knowledge/assertions/id-reuse-001.md`'s own correction notice
and `corrections/id-reuse-reference-model.md` for the full reproduction.

## Documentation architecture

This page is a single, narrow Diátaxis-style *reference* entry, not a
full six-category reconstruction: the entire permitted input is one
frozen assertion (`id-reuse@v1#id-reuse-001`) plus its own cited
supporting evidence, describing one function's behavior. A reference
page — "what the code actually does, by case" — fits that scope better
than a tutorial, how-to, or architecture-overview framing, none of which
apply to a single-function boundary claim. No other category (user,
developer, protocol, domain, process) is populated here, since nothing
in the input supports them.

## What this page is

A statement of what is actually known about `_next_id`'s id-reuse
behavior, as established by direct execution of the real implementation,
not by reading or trusting its own docstring. Every substantive claim
below is cited to the frozen snapshot assertion `id-reuse@v2#id-reuse-002`
(which itself documents the independent adversarial-review evidence
corroborating it). No claim here goes beyond what that assertion states.

## The behavior is conditional, not a flat yes/no — and not determined by any single deletion

`_next_id` computes exactly one thing on every call: `candidate =
max(id over the task list as it currently stands) + 1`, or `candidate =
1` if the list is currently empty — a function of the list's current
state only, with no separate record of ids that existed in the past
(`id-reuse@v2#id-reuse-002`). **Whether a given `add` reuses a
previously-assigned id is not determined by which task was most
recently deleted, or by whether that task held the maximum id at its
own deletion** — it is determined by whether `candidate`'s own specific
numeric value was ever assigned to any earlier, now-deleted task, which
depends on the complete history of every `add`/`delete` call in
sequence (`id-reuse@v2#id-reuse-002`):

- Confirmed counterexample to "look at the most recent deletion":
  `add 1,2,3 → delete 2 (not the max at that moment) → delete 3 (now
  the max) → add` produces new id **2** — the id whose own holding task
  was *not* the max at its own deletion — not `3`, and a further `add`
  immediately afterward produces `4`, never `3`: id `3` is never reused
  in this sequence at all (`id-reuse@v2#id-reuse-002`).
- The fully-emptied-list case (delete every task, then add) is a
  special case of the same underlying formula: with no tasks left, the
  candidate resets to `1`, reusing it if `1` was used before
  (`id-reuse@v2#id-reuse-002`).

Do not round this up to "ids can be reused" or round it down to "ids
cannot be reused," and do not summarize it as "whichever task was
deleted last/held the max determines what gets reused" — all three are
false simplifications. The accurate statement requires tracking the
full history of assigned ids: reuse happens exactly when the current
`max(live)+1` candidate was previously assigned to some now-deleted
task, nothing less and nothing more (`id-reuse@v2#id-reuse-002`).

## Relationship to the function's own docstring

`_next_id`'s own docstring claims "ids are never reused, even after a
task is deleted," and separately reasons that the next id is "always
one more than the highest id *ever* assigned" — not merely the highest
id currently present. The evidence found this headline claim and this
specific reasoning to be contradicted by the function's real, observed
behavior: the implementation is, literally, one more than the highest
id *currently present*, with no tracking of ids ever assigned
(`id-reuse@v2#id-reuse-002`). The docstring's own narrower, final-
paragraph admission — that deleting every task and starting fresh
resets the counter — is not contradicted; that case is consistent with
the evidence. What the docstring's caveat does not name or cover is the
broader case: reuse can occur with other, older tasks still live, with
no need for the list to be fully emptied — and precisely which id gets
reused is governed by the current live maximum at `add` time, not by
any single deletion's own circumstances (`id-reuse@v2#id-reuse-002`).

## Basis for this page

The evidence rests on direct execution of the real `_next_id`, `add`,
and `delete` implementation against constructed delete sequences, not on
reading the docstring and trusting its description, cross-checked
against an independent reference model that tracks every id ever
assigned (not inferring "ever assigned" from a single deletion event —
the mistake this page's own prior version made), and was independently
re-reviewed by a fresh dispatch explicitly tasked with trying to
falsify the corrected rule, which found no counterexample across 18
independently constructed sequences, several thousand individual
operations, and a CLI subprocess cross-check
(`id-reuse@v2#id-reuse-002`).

## Open question (not resolved by this page)

Whether "ids are never reused" is a product requirement this project
actually needs, or dead/aspirational docstring text that was never
validated against the implementation, is a product decision the
underlying assertion explicitly does not make and this page does not
make either (`id-reuse@v1#id-reuse-001`). This page documents only what
the code currently does, not what it should do.
