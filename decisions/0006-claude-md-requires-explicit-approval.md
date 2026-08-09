# 0006. Root CLAUDE.md requires explicit approval before any edit

## Status

Accepted

## Context

Every other doc folder (`docs/`, `architecture/`, `decisions/`,
`planning/CONTEXT.md`) is updated in the same commit as the change that
affects it, without a separate approval step — see `CLAUDE.md` §2. Root
`CLAUDE.md` itself is different: it's the file every future session (human
or AI) reads automatically and trusts unconditionally as the source of
truth for how work proceeds.

## Decision

`CLAUDE.md` is the one file exempted from same-commit auto-sync. Any
change to it — a new process rule, a changed convention, a small wording
correction, no matter how minor — must be presented to the user as a diff
and receive explicit approval before it is written or committed. It is
never folded silently into an unrelated commit alongside the change that
prompted it.

## Alternatives considered

- **Treat `CLAUDE.md` like `docs/`/`architecture/`/`decisions/`** (auto-sync
  in the same commit as whatever change prompted the update). Rejected —
  this removes the one human checkpoint on the file with the most leverage
  over every future session's behavior. An unreviewed drift in `docs/` is
  locally contained; an unreviewed drift in `CLAUDE.md` compounds silently
  across every subsequent session that loads it.

## Consequences

- Any phase whose implementation surfaces a need to change a process rule
  must pause implementation, present the proposed `CLAUDE.md` diff, and
  wait for approval before continuing — this is a deliberate friction
  point, not an oversight to streamline away.
- `CONTRIBUTING.md` restates the same rules for human contributors, but is
  not itself subject to this approval gate (it's user-facing
  documentation, not the file sessions trust unconditionally) — it follows
  the normal same-commit sync rule instead.
