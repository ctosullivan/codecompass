# Phase 0: Repository Scaffolding

## Scope

**Covered:**
- Licensing and packaging metadata: `LICENSE`, `.gitignore`,
  `pyproject.toml`, empty `src/depcompass/` package placeholder.
- Top-level docs: `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`.
- Process rules: `CLAUDE.md` (written and committed only after explicit
  user approval, per its own §0 rule).
- `architecture/overview.md` — living design doc.
- `decisions/0001` through `0009` — ADRs for every major decision already
  made, plus the new min-Python-3.11 decision made during this phase.
- `docs/cli-reference.md`, `docs/config-schema.md` — forward-looking stubs
  for the planned CLI surface and config format.
- `planning/CONTEXT.md` and this plan file.
- Empty `tests/` skeleton (no test files yet — nothing to test).

**Explicitly deferred:**
- Any implementation code (`core.py`, adapters, CLI commands) — Phase 1
  onward.
- CI workflow (`.github/workflows/*.yml`) — deferred to Phase 6, when
  `depcompass check` (the command CI is meant to gate on) actually exists.
  A placeholder CI job now would either run against zero tests (a
  misleading green) or need special-casing that's thrown away once real
  tests land.
- Resolution of whether `vendor/<name>/src/` snapshots are committed to
  git or gitignored-and-regenerated — deferred to the Phase 1 plan file
  per the original spec's §6.

## Files

- `LICENSE` — MIT, Cormac O' Sullivan, 2026.
- `.gitignore` — Python standard ignores + `vendor/` + `.env`.
- `pyproject.toml` — setuptools backend, `src/depcompass/` layout,
  `requires-python = ">=3.11"`, deps (`typer`, `rich`, `anthropic`), `dev`
  extra (`pytest`, `ruff`), entry point `depcompass = "depcompass.cli:app"`.
- `src/depcompass/__init__.py` — empty placeholder.
- `README.md` — project pitch, status, doc pointers.
- `CONTRIBUTING.md` — process rules restated for human contributors.
- `CHANGELOG.md` — Keep a Changelog format, `[Unreleased]` section.
- `CLAUDE.md` — canonical process rules; approved by user before commit.
- `architecture/overview.md` — full system design transcription.
- `decisions/0001`-`0009` — ADRs, one per major decision.
- `docs/cli-reference.md` — planned CLI commands, phase-tagged.
- `docs/config-schema.md` — `vendor.toml` schema.
- `tests/README.md` — explains the empty test directory.
- `planning/CONTEXT.md` — session-resumption state.
- `planning/phase-0-repo-scaffolding.md` — this file.

## Verification

- `git log --oneline` shows 8 commits, in order:
  `chore(phase-0): initialize project metadata and licensing` →
  `docs(phase-0): add README and CONTRIBUTING` →
  `docs(phase-0): add process rules CLAUDE.md` →
  `docs(phase-0): add architecture overview` →
  `docs(phase-0): record foundational architecture decisions` →
  `docs(phase-0): add CLI reference and config schema stubs` →
  `chore(phase-0): scaffold test package skeleton` →
  `chore(phase-0): record phase-0 plan and initial changelog entry`.
- `python -c "import tomllib; print('ok')"` succeeds, confirming the
  3.11+ stdlib assumption holds.
- Every file in the Files list above exists at its expected path.
- `CHANGELOG.md` has a non-empty `[Unreleased]` section.
- Every `decisions/000N-*.md` file has Status/Context/Decision/
  Alternatives considered/Consequences sections.
- `CLAUDE.md`'s content was shown to and explicitly approved by the user
  before it was committed (confirmed: approved via AskUserQuestion before
  commit 3).
- `planning/CONTEXT.md` correctly names Phase 1 as the next step.

## Status

done
