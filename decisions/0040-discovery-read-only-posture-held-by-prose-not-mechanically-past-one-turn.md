# 0040. `/discovery`'s read-only posture is mechanically enforced for one turn, held by prose for the rest of the session

## Status

Accepted

## Context

`/discovery` (Phase 17, `planning/phase-17-discovery-slash-command.md`)
was designed as a read-only exploration entry point: its frontmatter's
`allowed-tools` grants `Read`/`Grep`/`Glob` plus narrowly-scoped
`Bash(codecompass query:*)`/`Bash(codecompass check:*)`/`Bash(sqlite3
context-graph.db:*)`, with `Write`/`Edit` deliberately absent, and its
body repeats "no Write, no Edit, no plan file" several times.

A user request ("the custom discovery slash command should be a
read-only session by default — not making changes to code or creating
plans") prompted actually verifying, rather than assuming, what `allowed-
tools` guarantees in current Claude Code. The answer, confirmed against
Claude Code's own documentation rather than inferred: `allowed-tools` is a
**pre-approval grant scoped to the single turn that invokes the
command** — it clears the moment the next message is sent, and nothing
in Claude Code re-applies it or blocks `Write`/`Edit`/`ExitPlanMode` on a
later turn in the same conversation on its own. There is also no
frontmatter field, "mode," or other mechanism to lock an entire session to
read-only from a slash command — the only thing that persists across
turns is project-wide permission deny rules, configured outside any
command file.

So the original implementation was already doing the mechanically-correct
thing for the turn it actually controls, but its prose ("hold these for
the whole exchange, not just once") didn't say *why* that discipline has
to be deliberate rather than assuming the frontmatter already covers it —
a gap between what the file implies and what Claude Code actually
guarantees.

## Decision

**Keep single-turn `allowed-tools` as the mechanical floor, and make the
body text explicitly teach Claude that it, not the frontmatter, is
responsible for holding the read-only posture for the rest of the
session.** The Constraints section now states directly: `allowed-tools`
clears after this turn, Claude Code does not mechanically block
`Write`/`Edit`/`ExitPlanMode` afterward, and every later message in the
conversation should be treated as still governed by `/discovery`'s rules
by default — unless the user clearly starts a distinctly different
request that isn't a continuation of exploring the project — rather than
letting the discipline quietly lapse once the mechanical grant already
has.

**Do not attempt project-wide permission deny rules as an alternative.**
That would be the only way to get a genuinely mechanical whole-session
lock, but it applies to the *entire project*, not just conversations that
started with `/discovery` — a much blunter instrument that would also
block `Write`/`Edit` in every normal, non-exploratory Claude Code session
in the project, which is not what was asked for and not something
codecompass should configure on a user's behalf without being asked.

## Alternatives considered

- **Leave the prose as it was** ("hold these for the whole exchange, not
  just once") without explaining *why* — rejected once the actual Claude
  Code behavior was confirmed: a vague "hold this" instruction is weaker
  than one that explains the mechanical grant has already cleared and
  says so plainly, the same way this project generally prefers explaining
  the *why* behind a constraint over stating it as a bare rule.
- **Write project-level permission deny rules** (e.g. a generated
  `.claude/settings.json` snippet denying `Write`/`Edit` outright) as part
  of what codecompass generates. Rejected: this would restrict every
  Claude Code session in the project, not just ones exploring via
  `/discovery` — conflating "one exploratory command should stay
  read-only" with "this whole project should never let Claude write code,"
  which is a far larger behavior change than the request asked for and
  not codecompass's call to make unilaterally.
- **Do nothing, treat the existing implementation as already sufficient.**
  Rejected — the existing implementation's own docstring claimed
  `allowed-tools` made the posture "mechanical, not just instructional"
  without qualifying that this only holds for one turn, which is not
  accurate to how Claude Code actually behaves and could mislead a future
  session maintaining this code into overstating the guarantee.

## Consequences

- `/discovery`'s read-only guarantee is, and remains, **prompt-level
  discipline for everything past the first turn** — a well-written,
  explicit instruction, not a mechanical wall. A sufficiently adversarial
  or confused follow-up message could still, in principle, get a model to
  make an edit mid-`/discovery`-session; this ADR doesn't change that
  ceiling, only makes the actual guarantee honestly documented instead of
  overstated.
- If Claude Code ever adds a real session-scoped read-only mode (a
  frontmatter field or slash-command mechanism that persists past one
  turn), this ADR should be revisited and `/discovery`'s generation
  updated to use it — the current approach is the best available given
  today's feature set, not a permanent architectural preference for
  prose over mechanism.
- No change to `allowed-tools` itself — it still correctly excludes
  `Write`/`Edit` for the one turn it governs, and every canned `query`/
  `check`/`sqlite3` escape hatch stays exactly as scoped.
