# `_next_id` id-reuse behavior

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
below is cited to the frozen snapshot assertion `id-reuse@v1#id-reuse-001`
(which itself documents the independent adversarial-review evidence
corroborating it). No claim here goes beyond what that assertion states.

## The behavior is conditional, not a flat yes/no

`_next_id` computes the next task id as one more than the maximum id
*currently present* in the task list (or `1` if the list is currently
empty) — a function of the list as it stands at the moment of the call
only, with no separate record of ids that existed in the past
(`id-reuse@v1#id-reuse-001`). Because of this, whether a deleted task's
id gets reused by a later `add` depends entirely on whether that
deleted task held the current maximum id at the moment it was deleted
(`id-reuse@v1#id-reuse-001`):

- **Reuse occurs** when the deleted task held the current maximum id.
  The next `add` recomputes the maximum from the surviving tasks and
  reassigns exactly the id that was just deleted. This happens even
  when other, older, lower-numbered tasks are still present in the
  list — it is not limited to the case where the list has been emptied
  entirely (`id-reuse@v1#id-reuse-001`).
- **Reuse does not occur** when the deleted task did not hold the
  current maximum id. The surviving maximum is untouched by that
  deletion, so the next `add` still produces a strictly new,
  previously-unused id (`id-reuse@v1#id-reuse-001`).
- The fully-emptied-list case (delete every task, then add) is a
  special case of the same underlying rule: with no tasks left, the
  computed maximum resets to the "empty" default and the next added
  task receives id `1` again, reusing it if it was used before
  (`id-reuse@v1#id-reuse-001`).

Do not round this up to "ids can be reused" or round it down to "ids
cannot be reused" — both are false simplifications of what the
assertion actually says. The accurate statement is conditional: reuse
happens if and only if the deleted task held the current maximum id at
the time of its deletion; it does not happen otherwise
(`id-reuse@v1#id-reuse-001`).

## Relationship to the function's own docstring

`_next_id`'s own docstring claims "ids are never reused, even after a
task is deleted," and separately reasons that the next id is "always
one more than the highest id *ever* assigned" — not merely the highest
id currently present. The assertion found this headline claim and this
specific reasoning to be contradicted by the function's real, observed
behavior: the implementation is, literally, one more than the highest
id *currently present*, with no tracking of ids ever assigned
(`id-reuse@v1#id-reuse-001`). The docstring's own narrower, final-
paragraph admission — that deleting every task and starting fresh
resets the counter — is not contradicted; that case is consistent with
the assertion's findings. What the docstring's caveat does not name or
cover is the broader case: deleting only the current-maximum task,
while other, older tasks remain live, is sufficient on its own to
produce reuse, with no need for the list to be fully emptied
(`id-reuse@v1#id-reuse-001`).

## Basis for this page

The assertion's findings rest on direct execution of the real
`_next_id`, `add`, and `delete` implementation against constructed
delete sequences, not on reading the docstring and trusting its
description, and were independently re-derived and extended (eight
additional scenarios beyond the original three) by a separate
adversarial review that reproduced the same outcomes and found no
counterexample to the general rule stated above
(`id-reuse@v1#id-reuse-001`).

## Open question (not resolved by this page)

Whether "ids are never reused" is a product requirement this project
actually needs, or dead/aspirational docstring text that was never
validated against the implementation, is a product decision the
underlying assertion explicitly does not make and this page does not
make either (`id-reuse@v1#id-reuse-001`). This page documents only what
the code currently does, not what it should do.
