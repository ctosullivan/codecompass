# Architecture

This file describes your project's *current* architecture — what it
actually is today, not its history and not where it's headed. Replace
this whole file's content as your project takes real shape; the
headings below are a starting skeleton, not a required structure.

## What this project is

One or two paragraphs: what does this project do, who is it for, what's
the core idea.

## How it's put together

The main pieces (modules, services, whatever your project's own shape
is) and how they relate. Keep this at the level a newcomer needs to
orient themselves — not a restatement of the source code.

## Key dependencies

What this project depends on, and why each one is here. Once you're
tracking dependencies with CodeCompass (`vendor.toml`), `codecompass
query vendors` gives you this mechanically; this section is for the
*reasoning* a mechanical listing can't capture — why this dependency
over an alternative, what it's specifically used for.

## Decisions

Significant, non-obvious tradeoffs belong in `decisions/` (one file per
decision, see `decisions/README.md`), not duplicated here. Link to the
relevant ones if it helps a reader.

---

## On this repository's relationship to CodeCompass

This template is maintained alongside
[CodeCompass](https://github.com/ctosullivan/codecompass) but is a
separate, MIT-licensed repository — not a redistribution of
CodeCompass's own GPL-3.0-or-later source or documentation. Nothing in
this template's own text is copied from CodeCompass's; the *shape* of
the working conventions it packages (plan before you code, keep docs in
sync, a running context file, a lightweight learnings log) reflects
general, widely-used development practice, freely reusable regardless
of what license governs the tool that happens to consume `vendor.toml`.
A project using this template may itself be licensed however its own
owner chooses — GPL, a permissive license, or kept entirely proprietary
— independent of both CodeCompass's license and this template's own.
