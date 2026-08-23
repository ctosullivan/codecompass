# Phase 36: Maintainer-only docs-sync script + skill

## Status

`done`

## Context

Phase 35 fixes today's snapshot of `README.md`/`ai-docs/`, but nothing checks
that it stays true as the code moves — `architecture/overview.md` is *already*
stale relative to Phase 32's `doc_chunking.py`/`doc_chunks` table, a live
example of exactly the drift this phase targets. This project's own mechanical
mention-detection machinery (`sync.py`/`doc_mapping.py`/`doc_chunking.py`) is
the established house pattern for this kind of problem: deterministic
detection, no AI, human/agent judgment applies the actual fix. This phase
extends that same pattern to this repo's own hand-authored user-facing docs.

Confirmed maintainer-only per explicit user decision: this does **not**
become a shipped `codecompass` feature (no new CLI subcommand, no change to
`src/codecompass/`'s public surface) — it exists purely to keep this repo's
own docs in sync with its own code, a different concern from the product's
dependency-analysis roadmap.

Depends on Phase 35 (checks things it creates: `ai-docs/` existing,
`README.md` mentioning `ANTHROPIC_API_KEY`) — sequenced after it for that
reason, same dependency-ordering precedent as Phases 30→31→32.

Renumbering note: originally scoped as "Phase 35" during planning, renumbered
to 36 once Phase 34 (a same-numbered bug fix, unrelated to this work) was
found to have already claimed that number — see Phase 35's own renumbering
note for the same correction.

## Scope

**Covers:**
- `scripts/check_user_docs.py` — new, top-level, outside `src/codecompass/`.
  Confirmed safe with no packaging changes: `[tool.setuptools.packages.find]
  where = ["src"]` already excludes it from the wheel; `[tool.pytest.ini_
  options] testpaths = ["tests"]` and ruff's project-wide `[tool.ruff]`
  config pick up `scripts/*.py` and its test automatically. A small, fixed
  rule set, mechanical only, never edits a file or calls the Anthropic API:
  1. every `@app.command()`/`@query_app.command()` name in
     `src/codecompass/cli.py` (`init`, `sync`, `index`, `check`, `chat`,
     `undo`; `vendors`, `vendor`, `symbol`, `skills`, `relations`) has a
     corresponding mention in `docs/cli-reference.md`;
  2. the highest phase number marked `done` in `planning/ROADMAP.md` is
     consistent with the phase-count claim in `README.md`'s Status line
     (compare against the number itself, not by parsing free-text prose
     ranges);
  3. `README.md` mentions `ANTHROPIC_API_KEY` (fails today, before Phase 35
     lands — confirmed live by grep — a real, useful smoke test);
  4. every field on `VendorConfig` (`src/codecompass/core.py`: `name`,
     `ecosystem`) is mentioned in `docs/config-schema.md`'s Fields table
     (currently 2/2 — a regression guard, not a bug fix);
  5. every file directly under `ai-docs/` (created by Phase 35) exists and is
     non-empty.
  Report-only, human-readable output by default, mirroring `check`'s existing
  UX shape (`cli.py`'s `check` command). A `--strict` flag exits non-zero if
  any rule fails, for optional local/pre-commit use — no CI exists in this
  repo today, and this phase does not add one.
- `.claude/skills/docs-sync/SKILL.md` — new, in-repo only (project-local
  Skills aren't part of the shipped pip package, so this doesn't conflict
  with the maintainer-only constraint). Instructs an agent session to run
  the script, interpret each finding, and fix the actual doc content by
  hand/judgment — never auto-fix mechanically — then follow this project's
  normal per-phase discipline for whatever it touches. Mirrors
  `.claude/skills/codecompass/SKILL.md`'s terse frontmatter + cheat-sheet
  style.
- `tests/test_check_user_docs.py` (+ fixtures under `tests/fixtures/` as
  needed, matching the existing flat convention) — asserts the script
  doesn't false-positive against this repo's real current docs, and that a
  deliberately broken fixture (e.g. a copy of `docs/cli-reference.md` with a
  command heading stripped, or a copy of `README.md` with
  `ANTHROPIC_API_KEY` removed) is correctly flagged; `--strict`'s exit code
  checked both ways.
- `planning/ROADMAP.md`: this phase's row (status flips to `done` alongside
  Phase 35 once both land).

**Explicitly does not cover:**
- CI wiring (pre-commit hook config, GitHub Actions) — no CI exists in this
  repo today; this phase makes the script usable by a future one, not
  responsible for introducing one.
- Turning this into a shipped `codecompass` feature/subcommand — explicitly
  ruled out by the user.
- Auto-fixing anything the script flags — human/agent judgment applies
  fixes, per the project's established mechanical-detection/judgment-
  application split.
- Expanding the rule set beyond the five checks above — a maintainer smoke
  check, not an exhaustive doc linter.
- Anything `cli.py`'s existing `check` command already covers (consuming-
  project vendor/dependency staleness) — no overlap; this checks this
  repo's own hand-authored docs against its own code.

## Design decisions

- **Lives outside `src/codecompass/`, is not a `codecompass` subcommand.**
  Direct consequence of the user's explicit scoping decision — this is
  meta-tooling for maintaining codecompass's own docs, not a generalizable
  product feature for a consuming project's docs.
- **Report-only by default, `--strict` for exit-code gating** — deliberately
  mirrors `check`'s existing shape (`cli.py`) rather than inventing a new UX
  pattern, even though this script is unrelated code.
- **Never edits a file, never calls AI.** Consistent with `sync.py`/
  `doc_mapping.py`/`doc_chunking.py`'s existing mechanical-detection-only
  posture — a script flags; a human or an agent following the `docs-sync`
  skill applies the actual fix and its own judgment about wording.
- **Compare against the ROADMAP's highest-done phase number, not by parsing
  README's free-text phase-count prose.** The prose has already needed
  hand-updating multiple times as phases completed; a numeric comparison is
  the only reliably automatable check here.

## Files

- `scripts/check_user_docs.py` — new.
- `.claude/skills/docs-sync/SKILL.md` — new.
- `tests/test_check_user_docs.py` — new, plus fixtures under
  `tests/fixtures/` as needed.
- `planning/ROADMAP.md` — new Phase 36 row.
- `CHANGELOG.md` — new `[Unreleased]` entry.
- `planning/CONTEXT.md` — updated once both Phase 35 and 36 land.

## Verification

- Run the finished script against this repo's real current state and report
  what it actually flags: rule 3 expected to fail before Phase 35 lands and
  pass after; rules 1/2/4/5 expected to pass throughout (regression guards,
  not active bugs).
- `pytest tests/test_check_user_docs.py` passes, covering both the
  no-false-positive and flags-a-broken-fixture cases.
- `ruff check .` clean.
- One manual run of the `.claude/skills/docs-sync` skill in a real agent
  session, confirming it applies a sensible, judgment-based fix to a real
  flagged item rather than a mechanical rewrite.

**Confirmed live:** `python scripts/check_user_docs.py --strict` against
this repo's real current state reports **zero findings** and exits 0 (the
"clean" case for all five rules — expected, since Phase 35 already fixed the
one rule that was failing pre-Phase-35, the `ANTHROPIC_API_KEY` mention).
`pytest tests/test_check_user_docs.py` — 14 tests, covering all five rules'
positive and negative paths plus `--strict`'s exit-code behavior both ways —
all pass. `ruff check .` clean across the whole repo including the new
`scripts/` file. The skill's judgment-application step (item 2 in the
Verification list above) wasn't exercised against a real flagged item in
this session, since the script reports nothing to fix once Phase 35 has
landed — noted honestly rather than staged artificially; the next real
finding (a future doc/code drift) is this skill's first real workout.
