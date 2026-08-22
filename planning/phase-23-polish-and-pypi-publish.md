# Phase 23: Polish & PyPI publish

## Scope

The last phase of the path-to-v1.0 sequence (`planning/v1.0-initial-
release-roadmap.md`) — this phase *is* the release. Everything up to here
(phases 20-22) fixed bugs and added the spec-doc relationship graph;
nothing about that work is release-blocking on its own merits, but
shipping v1.0 with a known gap or a half-finished feature would mean
re-releasing almost immediately, which is why they came first.

Two very different kinds of work live in this one phase, split explicitly
because they carry very different risk:

**Part A — safe, reversible, implementable now:**
- `pyproject.toml` completeness pass: add `[project.urls]` (Homepage,
  Repository, Issues — currently absent entirely); review `classifiers`
  (currently `Development Status :: 2 - Pre-Alpha`, no longer accurate
  once phases 0-22 are all `done`); confirm `dependencies` have no
  accidental missing lower bounds; confirm `readme`/`license`/`authors`
  are correct (spot-checked already: `LICENSE` exists at the root,
  `readme = "README.md"` is set).
- A **version number decision, flagged explicitly, not decided
  unilaterally** — see Design decisions below. Current `version =
  "0.1.0.dev0"` was never bumped across the entire v0.1/v0.2 arc (both
  milestones shipped without a version bump, per `decisions/0022`'s
  "tag decision separate from phase completion" posture) — this phase
  can't defer that decision any further, since a real PyPI publish
  requires a real version string.
- README quality pass against the fully-built system (the same kind of
  pass Phase 19 did for `architecture/overview.md`/`docs/cli-reference.md`
  — check for anything describing a pre-Phase-19 state, verify install/
  quickstart instructions actually match the current CLI surface
  end-to-end).
- A minimal `examples/` directory: one small, real worked example (a toy
  project with 2-3 real dependencies) showing `codecompass`'s output —
  not a second test suite, just something a first-time visitor can look
  at without installing anything.
- Docs-site evaluation: a short written decision (a new ADR, not a built
  site) on whether v1.0 ships with a dedicated docs site (mkdocs/
  ReadTheDocs/etc.) or relies on `README.md` + `docs/*.md` rendered
  directly on GitHub — see Design decisions for the recommended answer.
- A packaging smoke test: `python -m build` succeeds and the resulting
  wheel installs cleanly into a fresh throwaway venv with `codecompass
  --help` working — catches a broken `pyproject.toml`/`MANIFEST`
  before the real, irreversible publish attempt.

**Part B — the actual publish, paused for explicit confirmation, not
executed automatically even under a broad "implement to release"
instruction:**
- Uploading to PyPI (`twine upload` or equivalent) claims the
  `codecompass` package name **permanently** — there is no meaningful
  "undo" for a first publish the way there is for a git commit. This is
  exactly the class of action this project's own operating rules (and the
  assistant's own standing instructions) require pausing on regardless of
  how broad the enclosing instruction was.
- Cutting the `v1.0` git tag and pushing it — visible externally the
  moment it's pushed, same posture.
- Promoting `CHANGELOG.md`'s `[Unreleased]` section to a dated `v1.0`
  release section — mechanically trivial, but only meaningful paired with
  an actual tag/publish, so grouped with Part B rather than Part A.

**Explicitly deferred / out of scope:**
- Routing/rollup (Phase 24) and MCP server (Phase 25) — already proposed
  deferred past v1.0 in the umbrella roadmap, unaffected by this phase.
- Any new CLI functionality — this phase is packaging/release readiness
  only, not new features.
- CI/CD publish automation (a GitHub Actions workflow that publishes on
  tag push) — worth having eventually, not required to *make* the first
  release, and building automation around an action that itself needs a
  human pause defeats the purpose. Revisit post-v1.0 if repeated manual
  releases prove it's worth automating.

## Design decisions

**Version number: recommend `1.0.0`, but this is the user's call, not
mine.** The project has used "v0.1"/"v0.2" as internal milestone *names*
throughout (`decisions/0022`, `decisions/0030`) without those necessarily
being the literal `pyproject.toml` version string — neither milestone was
ever actually tagged or published. Given this phase's own framing
("initial release," `planning/v1.0-initial-release-roadmap.md`) and that
SemVer's own convention treats 1.0.0 as "first stable public API," `1.0.0`
is the natural literal version to pair with the first real publish. An
alternative — `0.3.0` or similar, reserving `1.0.0` for after real
external users have exercised it — is equally defensible and not
automatically wrong. **Flagged to the user for an explicit choice before
Part A's version bump is actually written**, not assumed.

**Docs site: recommend deferring a dedicated site (mkdocs/ReadTheDocs),
shipping v1.0 with `README.md` + `docs/*.md` rendered on GitHub only.**
This project's documentation is already thorough and well-organized
(`README.md`, `docs/cli-reference.md`, `docs/config-schema.md`,
`architecture/overview.md`) and GitHub renders Markdown natively —a
dedicated site adds a build/deploy pipeline and a second place docs can
drift out of sync, for a project that doesn't yet have external users
whose navigation needs are known. Write this as a short ADR (ADR format,
not a build) so the reasoning is on record and the decision can be
revisited once real usage patterns are known, rather than silently never
having been considered.

**A worked example, not a second test suite.** `examples/` is for a human
skimming the repo to understand what the tool actually produces, not for
CI coverage (that's what `tests/` already does). One example, kept small
and real, is enough for v1.0 — more can be added later without needing a
phase.

## Files

- `pyproject.toml` — `[project.urls]`, `classifiers`, version bump (once
  confirmed).
- `README.md` — quality pass.
- `examples/` (new) — one worked example + its own short `README.md`
  explaining what it demonstrates.
- `decisions/` — new ADR for the docs-site deferral decision.
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` — Part A's
  completion; the `[Unreleased]` → dated-release promotion itself is Part
  B, held until publish is confirmed.

## Verification

- Part A: `python -m build` succeeds; the built wheel installs into a
  fresh throwaway venv (`python -m venv`, `pip install dist/*.whl`) and
  `codecompass --help` runs correctly from it. `pytest`/`ruff check .`
  still clean (no functional code changed, but confirms nothing broke).
  README's own quickstart steps followed literally against a scratch
  project and confirmed to work as written.
- Part B (only after explicit user confirmation, in a separate step):
  real `twine upload` (or `--repository testpypi` first, if the user
  wants a dry run against TestPyPI before the real index), followed by
  `pip install codecompass` from a clean environment to confirm the
  published package actually works: `codecompass --help` and a real
  `sync` against a scratch project.
