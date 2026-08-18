# Phase 9: Rename to codecompass

## Scope

**Covered:**
- `git mv src/depcompass src/codecompass` (preserve blame), including
  `adapters/`. Every module's internal imports (`from depcompass.X import`
  → `from codecompass.X import`) across all ~15 modules.
- `pyproject.toml`: `[project].name = "codecompass"`,
  `[project.scripts] codecompass = "codecompass.cli:app"`. Confirmed
  available on PyPI (user-verified before this phase was planned).
- `index.py`'s routing-table marker comments: `<!-- depcompass:start/end -->`
  → `<!-- codecompass:start/end -->`. This touches the root `CLAUDE.md`
  file — per `CLAUDE.md` §0, the resulting diff to that specific file must
  be presented to the user and receive explicit approval before it's
  written, even though every other file in this phase is a mechanical,
  no-approval-needed rename.
- `skill.py`: `_TOOL_SKILL_DIR_NAME` (`"depcompass"` → `"codecompass"`),
  per-vendor skill naming (`depcompass-<vendor>` → `codecompass-<vendor>`),
  Cursor `.mdc` filename prefix (`depcompass-<vendor>.mdc` →
  `codecompass-<vendor>.mdc`).
- `chat.py`'s REPL banner/error strings that literally print "depcompass".
- Generated-artifact naming this repo already has on disk from its own
  prior bootstrap/promote runs: `.claude/skills/depcompass/` →
  `.claude/skills/codecompass/`, `.claude/skills/depcompass-rich/` →
  `.claude/skills/codecompass-rich/`, `.cursor/rules/depcompass-rich.mdc` →
  `.cursor/rules/codecompass-rich.mdc` — these are currently uncommitted
  local artifacts (from an earlier local `promote rich` run) and should be
  renamed alongside the source rather than left stale under the old name.
- `README.md`, `CONTRIBUTING.md`, `docs/*.md`, `architecture/overview.md`
  — prose find/replace pass (tool name, CLI examples, import examples).
- `tests/`: import paths in every test file, plus any assertion strings
  that check for literal `"depcompass"` output (Skill frontmatter, marker
  comments, CLI banner text) — update to `"codecompass"`.
- `src/depcompass.egg-info/` — a build artifact, not hand-edited; confirm
  it regenerates correctly as `codecompass.egg-info` after a fresh
  `pip install -e ".[dev]"`.
- Final grep sweep for stray `"depcompass"` mentions across the whole repo
  (badges, any `project_urls`, comments) before calling this phase done —
  excluding the two categories below.

**Explicitly deferred / out of scope:**
- `decisions/*.md` — **never edited**, append-only per `CLAUDE.md` §2.
  ADRs 0001-0028 predate this rename and keep saying "depcompass"
  throughout their historical text; `decisions/0029` (this phase's ADR)
  states this explicitly so it doesn't read as an inconsistency later.
- `CHANGELOG.md`'s existing dated/historical entries (everything above
  this phase's own new `[Unreleased]` entry) — Keep a Changelog entries
  describe what happened at the time; not rewritten retroactively. Only
  new entries from this phase forward say "codecompass".
- The repository/working-directory name ("Devcompass") — stays as-is, a
  deliberate decision made during this rework's planning interview, not
  an oversight.
- `vendor.toml`'s `depth` field, the `Depth` enum, `promote`, and every
  other behavioral/architectural change in this rework — **zero logic
  changes in this phase**. This phase's only bar is: does the tool behave
  identically under the new name. Depth retirement is Phase 10.
- No new ADRs beyond the rename announcement itself (`decisions/0029`) —
  the five other foundational ADRs for this rework (`0030`-`0034`) are
  written in this same planning pass because they're session-level
  architecture decisions later phases depend on, but they don't gate
  Phase 9's own implementation, which is purely mechanical.

## Design decisions

See `decisions/0029` for full reasoning. Summary: rename now, while the
package has never had a `v0.1` PyPI release — nothing to preserve
backward compatibility with, so a straight rename (not an alias/re-export
shim) is the right call. Landed first, ahead of every behavioral change in
this rework, so every later phase (10-22) is written and reviewed against
the new name from the start rather than threading the rename through
unrelated diffs.

## Files

Every file under `src/depcompass/` (moved to `src/codecompass/`) and
`tests/` (import paths only), plus: `pyproject.toml`, root `CLAUDE.md`
(marker comment only — requires explicit approval, see Scope above),
`README.md`, `CONTRIBUTING.md`, `docs/*.md`, `architecture/overview.md`,
and the uncommitted local generated artifacts listed under Scope
(`.claude/skills/depcompass*`, `.cursor/rules/depcompass-*.mdc`).
`decisions/*.md` and `CHANGELOG.md`'s existing entries are explicitly
**not** touched (see Explicitly deferred above).

## Verification

- `pytest` — full existing suite passes unchanged (import paths updated,
  zero assertions on behavior change) — the actual bar for this phase.
- `ruff check .` — clean under the new package path.
- Fresh install smoke test: in a clean venv, `pip install -e ".[dev]"`,
  confirm the `codecompass` console script resolves and `codecompass
  --help` lists the same commands as `depcompass --help` did before this
  phase, just under the new name.
- Run bare `codecompass` against this repo itself (the same
  bootstrap-on-own-repo pattern used to validate Phase 7): confirm the
  regenerated root `CLAUDE.md` uses `<!-- codecompass:start/end -->`, and
  `.claude/skills/codecompass/SKILL.md` / `.claude/skills/codecompass-rich/`
  are written correctly.
- `grep -rn "depcompass" src/ tests/ pyproject.toml README.md
  CONTRIBUTING.md docs/ architecture/` returns zero hits (excluding
  `decisions/` and historical `CHANGELOG.md` entries by design).
