# 0036. `undo` is a best-effort, origin-tag-driven filesystem cleanup, not a transactional rollback

## Status

Accepted

## Context

Phase 18 (`planning/phase-18-undo-command.md`) adds `codecompass undo`, the
first command whose whole job is to *remove* what codecompass generated —
`vendor/<name>/` directories, `vendor.toml`, `context-graph.db`, every
generated Skill/`.mdc`/slash-command artifact, and the root `CLAUDE.md`
routing-table marker block. Nothing about how that removal should behave
was settled by an earlier decision: whether it should be transactional
(all-or-nothing), whether it should touch git, and how it should find
"everything codecompass generated" in the first place — a genuinely new
command with its own tradeoffs, not a natural extension of an existing
one.

Two enumeration strategies are needed, not one, because `undo` has to work
in a state a whole-project sync has never reached. The precise mechanism —
querying `context-graph.db`'s `doc_artifacts` table for every row whose
`origin` is `codecompass_tool`/`codecompass_vendor` (never `third_party`),
resolved to real paths — only exists once a whole-project sync has run at
least once. But the scenario `undo` most obviously exists for ("I ran
`init --scan`/one `sync`, didn't like the result, want to back out
immediately") is exactly the scenario where no graph exists yet. Refusing
to function without a graph would make `undo` useless in its own
motivating case, so a second, pattern-based fallback enumeration (matching
`skill.py`/`commands.py`'s exact generated-name conventions —
`.claude/skills/codecompass/`, `.claude/skills/codecompass-*/`,
`.cursor/rules/codecompass-*.mdc`, `.claude/commands/discovery.md`, plus
every vendor listed directly in `vendor.toml`) covers that gap. It's
strictly less precise (it can't distinguish a hand-renamed third-party
Skill that happens to collide with the naming pattern from one codecompass
actually generated), but that's a known, accepted tradeoff for the
fallback path only — the graph-backed path has no such ambiguity, since it
reads `origin` directly rather than pattern-matching a name.

## Decision

`undo` is explicitly a **best-effort filesystem cleanup**, not a
transactional rollback, and it **never touches git**:

- It enumerates a set of paths up front, prints the full list, and only
  then deletes (`shutil.rmtree`/`Path.unlink`) — never a lazy,
  as-you-go delete that could leave a half-cleaned tree if something
  fails partway through. But if one deletion does fail partway, `undo`
  does not roll back what it already removed, and re-running `undo` after
  a partial failure is not guaranteed to reconstruct or resume any
  particular prior state — it just re-enumerates and cleans up whatever
  is left.
- It never runs `git rm`/`git add`/`git status`, and never commits the
  resulting working-tree changes on the user's behalf. Committing (or
  not) the removal is left entirely to whoever ran `undo` — the same
  posture every other `codecompass` command already has toward git
  (none of them touch it either).
- The root `CLAUDE.md` marker block is stripped in place
  (`index.py`'s `_MARKER_BLOCK_RE`, run in reverse) rather than the file
  being deleted outright — hand-written content elsewhere in that file
  must survive `undo` untouched, and `undo`'s own confirmation prompt
  (shared with every other enumerated deletion) is the disclosure/consent
  step for that edit; no separate gate is layered on top of it.
- Enumeration never includes anything tagged `origin='third_party'` (graph
  path) or anything outside the exact generated-name patterns above
  (fallback path) — by construction, not as an after-the-fact filter.
  Getting this wrong in either direction is the one failure mode `undo`
  cannot be "best-effort" about: silently deleting a third-party or
  hand-written file is a strictly worse failure than leaving a
  codecompass-generated one behind.

## Alternatives considered

- **Require `context-graph.db` to exist; refuse to run otherwise.**
  Rejected — this would make `undo` unusable in exactly the scenario that
  motivates it (someone backing out before ever reaching a whole-project
  sync). The fallback path's reduced precision is an accepted cost for
  keeping `undo` usable that early.
- **Have `undo` run `git rm` (or `git add -A`) after deleting, so the
  removal shows up staged.** Rejected — every other `codecompass` command
  is a plain filesystem operation with no git awareness at all; giving
  `undo` alone a git dependency would be a new, unannounced capability
  boundary for this codebase, and would need its own error handling for
  "not a git repo"/"git not installed" that nothing else here has ever
  needed to solve.
- **Make `undo` transactional** (stage every deletion, apply only if all
  resolve cleanly, roll back otherwise). Rejected as unnecessary
  complexity for what's fundamentally a confirm-then-delete flow over
  plain files and directories — the only realistic partial-failure mode
  is a permissions error or a file locked by another process, and in
  either case leaving whatever succeeded deleted (rather than attempting
  to resurrect it) is the simpler, more honest behavior.

## Consequences

- `undo`'s docstring and `docs/cli-reference.md` state plainly that it is
  best-effort and never commits — anyone scripting around it (CI cleanup,
  a pre-commit hook) needs to run their own `git add`/`git commit` (or
  `git status` check) afterward if that's the desired end state.
- A future command that *does* want transactional or git-aware behavior
  (not currently planned) would need its own ADR — this decision only
  covers `undo` as shipped in Phase 18.
- The fallback path's precision gap (a hand-renamed third-party Skill
  matching the `codecompass-*` naming convention) is accepted, not solved,
  by this phase. If it proves to be a real-world problem, tightening the
  fallback path (e.g. requiring a matching frontmatter marker, not just a
  name) is a follow-up, not a Phase 18 blocker.
