# Retro: adopting codecompass-template into tinytodo

## Where things stood before this

tinytodo was a small, already-working, single-file CLI with one commit
and two passing tests, no planning/decisions/docs scaffolding at all.

## Goal

Adopt `codecompass-template`'s working conventions into tinytodo, and
actually use its heavier-weight optional knowledge workflow
(assertions/snapshots/conceptual docs) on one real, non-obvious design
choice already in the code: `_next_id`'s id-never-reused-after-delete
behavior.

## What happened

Adopted the template's `CLAUDE.md`, `.gitignore`, `vendor.toml`, `docs/`,
`decisions/`, `planning/` into tinytodo. Kept tinytodo's own `README.md`
rather than overwriting it with the template's self-descriptive one, and
didn't copy the template's `LICENSE` (that's this project's own choice to
make, not something to inherit silently). Filled in `docs/architecture.md`
for real rather than leaving the skeleton. Skipped steps 2-4 of
"Adopting this template" (installing CodeCompass, `codecompass sync`,
`codecompass query ...`) since CodeCompass itself isn't installed here —
expected, and clearly flagged as a separate install by the template's own
README, not a defect.

Used the heavier workflow on `_next_id`: wrote
`decisions/0001-task-ids-are-never-reused.md`,
`planning/knowledge/assertions/task-ids-001.md` (citing real file/line
evidence plus one ad hoc manual behavioral check that found a real,
untested caveat), attempted to freeze it as
`planning/knowledge/snapshots/task-ids@v1.toml` (only partially possible
— see "what didn't work"), and wrote `docs/task-ids.md` from the
snapshot per `docs/conceptual-documentation-guide.md`'s guidance.

## What worked

- The template's own docs made each step's purpose clear without needing
  to guess — especially `docs/mechanical-isolation.md`'s "two checks, not
  one" framing and `conceptual-documentation-guide.md`'s "cite the
  snapshot, not the live knowledge base" rule, both of which were
  directly usable, not just descriptive.
- Writing the Assertion record surfaced a real gap in tinytodo's own test
  suite (the delete-everything-resets-to-1 caveat has no regression
  test) that a casual read of the code wouldn't have forced out — the
  Evidence section's demand for a precise citation is what pushed
  checking it by hand instead of taking the docstring's word for it.

## What didn't work

- The snapshot step genuinely can't be fully completed without a commit
  to freeze against, and this exercise's own rules say not to commit.
  Worked around it by freezing what was actually committed already
  (`src/tinytodo.py`, `tests/test_tinytodo.py` at `df80660`) for real,
  and marking the assertion record's own entry `UNCOMMITTED` rather than
  inventing a revision for it. This isn't a template defect — a snapshot
  is inherently a freeze of committed history — but it's worth knowing
  going in: you can't try the snapshot step in a sandbox that forbids
  committing and get a fully "real" result out of it.
- Step 1 ("copy its contents into your own project") silently collides
  with any existing project's own `README.md` — fixed directly in the
  template, see below.

## Anything worth remembering

Logged as a candidate in `planning/knowledge/learnings.md`: the
`_next_id` delete-everything-resets-to-1 caveat has no regression test.

## What's next

If this project kept going: commit everything from this session,
install CodeCompass for real and run `codecompass sync` / `query`
against tinytodo, and add the missing regression test flagged above.
