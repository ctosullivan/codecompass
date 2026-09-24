# Phase 70: Release redefined CodeCompass v1 — plan

**Status:** planned (2026-09-24).

**Stage G, seventh and final phase · COMMITTED (gate G9)**
(`planning/v1-redefinition/roadmap.md`). Gated on Phase 69 completing
— **done 2026-09-24, PASS**, unblocked. **Irreversible — explicit user
go-ahead already given** (2026-09-24, verbatim: "Yes, proceed with the
release").

## 0. What this phase is

Executes `planning/milestone-closeout-checklist.md`'s own step 11: the
actual release. This is the first-ever publish of CodeCompass to
PyPI — `G2-b` held every prior phase back from this exact point. Once
`twine upload` completes, the published distribution cannot be
deleted from PyPI (only yanked, which still leaves the version number
permanently reserved and the yanked files still resolvable by exact
version pin) — this step is genuinely irreversible in the way every
earlier phase's plan has consistently flagged it to be.

## 1. Pre-flight, checked directly before any action

- `pyproject.toml`'s current version: `1.0.0.dev0`.
- No git tag exists yet (`git tag -l` — empty).
- `codecompass` is not yet a published name on PyPI (`pip index
  versions codecompass` — no matching distribution found), confirming
  this is genuinely the first publish, not a re-publish.
- `twine` is **not installed** in `.venv` — needs installing
  (`pip install twine`, a local, reversible action) before it can run.
- **No PyPI credentials are configured in this environment** — no
  `~/.pypirc`, no `TWINE_USERNAME`/`TWINE_PASSWORD`/`TWINE_API_KEY`/
  `TWINE_PASSWORD` environment variables. **This is a real, blocking
  dependency**: `twine upload` cannot run without real credentials
  (an API token is PyPI's own recommended method), and this plan does
  not assume how the user wants to supply them — that's asked
  separately, not decided here.
- Full test suite must be green immediately before the version bump
  (the last possible check before an irreversible action) — not
  assumed still-green from Phase 69's own closing run.

## 2. Scope

1. **Drop `.dev0`**: `pyproject.toml`'s `version` field,
   `1.0.0.dev0` → `1.0.0`. This is the only source change.
2. **`CHANGELOG.md`**: promote `[Unreleased]` to a dated `## [1.0.0] -
   2026-09-24` section, **flattened to canonical Keep-a-Changelog type
   grouping** (`Added` / `Changed` / `Fixed` across the whole release,
   not the per-phase subsections this effort accumulated) — per the
   checklist's own explicit step-11 instruction. A fresh, empty
   `[Unreleased]` section is added above it for whatever comes next.
3. **Build the distribution**: `python -m build` (already available)
   — produces a real sdist + wheel in `dist/`.
4. **Verify the build** before uploading anything: install the built
   wheel into a scratch venv, confirm `codecompass --help` runs, confirm
   `pip show codecompass` reports `1.0.0` and `License: GPL-3.0-or-later`
   — the same live-verification discipline Phase 43d already
   established for the relicensing, applied here to the actual
   artifact about to be published.
5. **`twine upload`** — the actual, irreversible publish. Requires
   real credentials (§1) — **not attempted until the user has answered
   how to supply them.**
6. **`git tag v1.0.0`**, pushed to `origin` — after the publish
   succeeds, not before (so the tag never points at a commit whose
   published artifact turned out broken and had to be re-cut under a
   new version number).
7. **Public positioning change** (gate G10, already implicitly
   resolved by the user's own go-ahead — this phase does not re-litigate
   whether to position CodeCompass as released, only executes the
   already-approved release itself).

## 3. Files created/changed

- `pyproject.toml` (version bump — the only `src/`-adjacent change).
- `CHANGELOG.md` (dated `1.0.0` section, flattened; fresh `[Unreleased]`).
- Standard closeout: `planning/retros/phase-70-release-v1.md` (retro),
  `planning/CONTEXT.md`, `planning/ROADMAP.md`.

**Explicitly not touched**: `docs/`, `README.md`, `architecture/`,
`ai-docs/`, `decisions/*`, `CLAUDE.md`, `docs/domain/`, and no other
`src/codecompass/` file (this is a version-number release, not a
feature phase — the freeze declared at Phase 69 holds for everything
except the two files this phase's own scope names).

## 4. Verification

1. Pre-flight checks (§1) all confirmed immediately before acting, not
   assumed from an earlier phase's own state.
2. Full `pytest` green immediately before the version bump.
3. The built wheel installs cleanly in a scratch venv and reports the
   correct version/license/behaviour live — not assumed from the
   source tree alone.
4. `twine upload` succeeds, confirmed by checking the real PyPI page
   for `codecompass` afterward (not just a locally-reported "success").
5. `git tag v1.0.0` exists locally and on `origin` after the tag push.
6. `CHANGELOG.md`'s new `1.0.0` section correctly flattens every prior
   per-phase `[Unreleased]` subsection into canonical
   `Added`/`Changed`/`Fixed` grouping — spot-checked against a sample
   of the original per-phase entries to confirm nothing was dropped in
   the flattening.
7. Closeout: retro; a lighter lead-confirmation in place of a full
   `release-phase-auditor` dispatch (matching Phase 68's own established
   proportionality principle for a phase whose own action is inherently
   a one-way door already gated by explicit user approval, not a
   candidate for a FAIL→fix→re-audit cycle after the fact).

## 5. Sequencing note — why the order in §2 matters

Build and verify (steps 3–4) happen **before** `twine upload` (step 5),
which happens **before** the git tag (step 6) — deliberately, so that:
- A broken build is caught before anything irreversible happens.
- If `twine upload` itself fails partway (a real possibility with
  network/credential issues), no tag exists yet pointing at a commit
  whose publish didn't actually complete, avoiding a confusing
  "tagged but not actually published" state.
