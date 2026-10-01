# Phase 80 Part 4 — frozen reader questions

Written and committed BEFORE evaluating the published documentation
against them, per the governing prompt's explicit instruction: "freeze
practical reader questions before evaluating the published
documentation." These are not retroactively adjusted after seeing how
well the docs answer them.

## CodeCompass (`/home/cormac/projects/codecompass`)

**User**

1. How do I install CodeCompass and get my first dependency digest?
2. What's the difference between `codecompass sync` (no argument) and
   `codecompass sync <vendor-name>`?
3. Where does CodeCompass store its generated state, and is any of it
   meant to be committed to git?
4. If I haven't run `codecompass sync` yet, what happens when I run
   `codecompass query vendors`?

**Contributor**

5. How do I add support for a new ecosystem (a new adapter)?
6. If I add a new table to the graph schema, what do I need to wire it
   into, and what test coverage is expected?

**Maintainer**

7. Does `codecompass sync` ever delete or lose previously-paid AI
   enrichment data?
8. How are schema migrations decided — by a version number, or
   something else? What happens if that number gets bumped by mistake
   for an unrelated change?

**Coding agent orienting to this codebase**

9. Is a symbol name unique across the whole project, or only within one
   tracked dependency?
10. What does CodeCompass explicitly say it does *not* do (its
    documented limitations)?

## codecompass-template (`https://github.com/ctosullivan/codecompass-template`)

11. My project already has a `CLAUDE.md` with real, specific rules in
    it. What should I do when adopting this template?
12. Do I need to adopt `optional-clean-room-workflow/` to use this
    template at all?
13. What's the very first command I should run after copying this
    template into my project?
14. My project has no dependency manifest yet (no `package.json`/
    `pyproject.toml`/etc.). Is that a problem for adopting this
    template?
15. Can I use this template if my own project is GPL-licensed, or does
    it require MIT?

These 15 questions will be answered independently from the published
documentation alone (not from source), then each answer will be checked
against primary evidence (the real source/tests), with any factual
error, omission, or ambiguity found in the documentation fixed directly.
