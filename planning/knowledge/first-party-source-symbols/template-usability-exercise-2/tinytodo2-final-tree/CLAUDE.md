# CLAUDE.md

This file governs how work on this project proceeds. If it disagrees
with anything else, it wins.

## 1. Plan before implementing

Before starting any non-trivial piece of work, write a short plan
describing what you intend to do, what's explicitly out of scope, and
how you'll know it's actually done. For a genuinely small change (a typo,
a one-line config fix), skip this — use judgment, and if in doubt, write
the short plan anyway.

If planning surfaces a real, unresolved question only a human can
answer, stop and ask before proceeding, rather than guessing and moving
on.

## 2. Keep documentation in sync, same change

When a change affects `docs/architecture.md`, a decision recorded under
`decisions/`, or anything else described elsewhere in this project,
update that description in the same change — not as a follow-up "when I
get to it" item. Documentation that describes the current system should
never describe a past version of it.

## 3. Record real decisions

When a change involves a non-obvious tradeoff — a choice that isn't
simply "the only reasonable option" — write a short decision record
under `decisions/` (see `decisions/README.md` for the format). Decision
records are append-only: if a past decision is later reversed, write a
new one that supersedes it; don't edit the old one's own content.

## 4. Keep a running context file

`planning/CONTEXT.md` should always reflect the current state of the
project: what's being worked on, what was just finished, what's next.
Overwrite its current-state section at each stopping point — don't let
it grow into an undifferentiated history. `planning/ROADMAP.md` is the
at-a-glance table of what's done, in progress, or planned; keep the two
in agreement.

## 5. Close the loop

When a piece of work finishes, write a few lines in `planning/retros/`
covering what the goal was, what actually happened, and anything you'd
do differently next time. If the work surfaced something worth
remembering — a real gotcha, a pattern that worked well, a genuine gap
in the tools you were using — add it to `planning/knowledge/` or
`planning/context-gaps/` as appropriate (see each directory's own
`README.md`) rather than letting it live only in your own memory of the
session.

## 6. Commits

One logical change per commit, with a message that says what changed and
why. Don't hold unrelated changes for a single large commit. Don't force-
push, rewrite shared history, or skip commit hooks without being
explicitly asked to.
