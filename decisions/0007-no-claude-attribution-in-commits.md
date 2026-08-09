# 0007. No AI attribution in commits

## Status

Accepted

## Context

AI coding sessions do a substantial share of the implementation work on
this project. Git tooling conventionally offers a `Co-Authored-By:`
trailer for exactly this situation.

## Decision

Commits for this project never include an AI assistant (Claude, or any
other) as a co-author, contributor, or attribution trailer — no
`Co-Authored-By: Claude` line, no mention of Claude/Anthropic in commit
messages or a `CONTRIBUTORS` file — regardless of how much of a given
change was AI-authored.

## Alternatives considered

- **Standard `Co-Authored-By:` trailer**, as is common practice for
  AI-assisted commits elsewhere. Rejected per explicit user instruction.

## Consequences

- This is a fixed project convention, stated explicitly so it is not
  silently reconsidered in a later session that might otherwise default
  to adding attribution out of habit.
- Applies uniformly regardless of authorship share — there is no threshold
  ("mostly AI-written" vs "AI-assisted") that changes this rule.
