# 0029. Package renamed depcompass → codecompass

## Status

Accepted

## Context

The project has shipped an MVP (phases 0-8, `decisions/0022`) under the
name `depcompass` but has never published a release to PyPI — `v0.1` has
not been tagged. As part of a broader v0.2 rework (`decisions/0030`), the
project is renamed to `codecompass`, confirmed available as a PyPI package
name before this decision was made.

## Decision

The package, console script, and every generated-artifact name derived
from it (Skill directory/frontmatter, Cursor `.mdc` filenames, the root
`CLAUDE.md` routing-table marker comment) are renamed from `depcompass` to
`codecompass`, effective Phase 9 (`planning/phase-9-rename-to-codecompass.md`).

`decisions/0001`-`0028` are **not edited** — append-only per `CLAUDE.md`
§2. They predate this rename and their historical text continues to say
"depcompass" throughout. This is expected, not an inconsistency to
reconcile.

The repository/working-directory name ("Devcompass") is **not** renamed —
a deliberate scope boundary, not an oversight: it avoids touching paths
outside this rework's control (IDE workspace config, any external
references to the repo's location), and nothing about the package name
requires the containing folder to match.

## Alternatives considered

- **Ship `codecompass` as a thin re-export/alias of `depcompass`,
  preserving the old name as a compatibility shim.** Rejected — no `v0.1`
  has ever been published to PyPI, so there is no installed-base
  compatibility to preserve. An alias would add permanent indirection for
  a problem that doesn't exist yet.
- **Rename the repository/working directory to match.** Considered and
  explicitly rejected during this rework's planning interview — see
  Context above.

## Consequences

- ~180 code references across `src/depcompass/` (now `src/codecompass/`)
  and `tests/` are touched — see `planning/phase-9-rename-to-codecompass.md`
  for the full mechanical scope.
- Every later phase (10-22) in this rework is planned and implemented
  against the `codecompass` name from the start.
- A reader encountering "depcompass" in `decisions/0001`-`0028` or in
  `CHANGELOG.md`'s pre-Phase-9 entries should read that as historically
  accurate at the time it was written, not a bug.
