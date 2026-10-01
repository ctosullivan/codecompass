# Project context

This file reflects the *current* state of the project — overwrite the
section below at each stopping point rather than appending to it.
History belongs in git log and `planning/retros/`, not here.

## Current state

Just adopted `codecompass-template` into this pre-existing project
(2026-10-01). Copied in `CLAUDE.md`, `.gitignore`, `vendor.toml`,
`docs/`, `decisions/`, `planning/`. Kept tinytodo's own `README.md`
as-is rather than overwriting it with the template's self-descriptive
one, and did not add the template's `LICENSE` (license choice belongs to
this project's own owner, not something to inherit silently from a
template). CodeCompass itself is not installed in this environment, so
`vendor.toml` stays empty and the CLI-dependent adoption steps
(`codecompass sync`, `query source` / `query vendor`) were skipped —
expected, not a gap, until someone actually installs and runs it here.

Also used the template's heavier-weight optional knowledge workflow on
one real thing: `_next_id`'s id-never-reused-after-delete design in
`src/tinytodo.py`. Wrote `decisions/0001-task-ids-are-never-reused.md`,
`planning/knowledge/assertions/task-ids-001.md`,
`planning/knowledge/snapshots/task-ids@v1.toml`, and `docs/task-ids.md`.
The snapshot is only partially frozen in the strict sense the format
wants: its own source-evidence citations (`src/tinytodo.py`,
`tests/test_tinytodo.py`) are genuinely frozen against the real commit
`df80660`, but the assertion record itself is still uncommitted in this
working tree, so there's no commit yet to freeze *it* against — a
property of what a snapshot is (a freeze of committed history), not a
workflow mistake.

Next concrete step, if this project kept going: commit the adopted
template files and the knowledge-workflow artifacts, which would let the
snapshot's own `task-ids-001` entry get a real `repository_revision`
instead of `UNCOMMITTED`.

## Known gaps / rough edges

- The reset-to-1-after-deleting-every-task behavior documented in
  `docs/task-ids.md` / `decisions/0001` is only confirmed by a one-off
  manual check, not a committed regression test — flagged as an open
  question in `planning/knowledge/assertions/task-ids-001.md`.
- `vendor.toml` is empty and no `context-graph.db`/`vendor/` exist —
  CodeCompass has never actually been run against this project.
