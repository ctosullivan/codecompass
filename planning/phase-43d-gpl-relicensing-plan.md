# Phase 43d: GPL-3.0-or-later relicensing plan

**Status:** planned (plan committed 2026-09-12; mechanics pending gate G12)

A Stage-A bridge phase from the 2026-09-12 realignment
(`planning/v1-redefinition/realignment-2026-09.md`). Plans the licence
transition MIT → GPL-3.0-or-later, aligning CodeCompass with `hledger`'s
own confirmed licence family, ahead of deeper Ledgerkit-facing,
source-assisted development work.

## Depends on

- None technically (independent of 43b/43c). Requested by the
  2026-09-12 realignment task.

## Scope

**In scope — this commit (planning only):**

- `planning/v1-redefinition/licence-migration.md` — the full plan
  (current-state audit, mechanical changes, source-assisted development
  / provenance policy, historical-integrity note, verification steps).
- Draft ADR `decisions/0053` in
  `planning/v1-redefinition/proposed-governance-changes.md` §C (not yet
  written to `decisions/`).
- This plan file + `planning/ROADMAP.md` row + `CHANGELOG.md` entry
  (per `CLAUDE.md` §1/§2/§3).

**In scope — a later commit, only once gate G12 resolves:**

- `LICENSE` — replace MIT text with the canonical GPL-3.0-or-later
  `COPYING` text + standard "how to apply" notice (name, copyright line,
  "or (at your option) any later version").
- `pyproject.toml` — `license = { text = "GPL-3.0-or-later" }`; classifier
  `License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)`.
- `README.md` — `## License` section updated.
- `CONTRIBUTING.md` — short note: contributions made under the current
  licence; no separate CLA (single-maintainer project).
- `decisions/0053` moved from `proposed-governance-changes.md` to
  `decisions/`, `Status: Accepted`.
- `CHANGELOG.md` `[Unreleased]` entry for the actual change.

**Explicitly out of scope:**

- Any change to `src/codecompass/`.
- Rewriting any git tag or historical commit (none exist under any
  published licence — `licence-migration.md` §5).
- Adding a `check_user_docs.py` rule asserting a specific licence string
  — worth considering once the change lands, not a precondition to plan
  or execute it.

## Verification

**This commit:** `python scripts/check_user_docs.py --strict` clean;
`licence-migration.md` and the ADR draft committed; no `LICENSE`/
`pyproject.toml`/`README.md` change yet (confirm via `git diff`).

**Once G12 resolves and the mechanical edits land:** `pyproject.toml`
parses (`pip install -e .` still succeeds); `git log` shows one normal,
dated commit; `CHANGELOG.md` entry present; `python scripts/check_user_docs.py --strict`
still clean.

## Done when

**Plan committed (this phase, now):** `licence-migration.md` +
`decisions/0053` draft + this file + `ROADMAP.md` row + `CHANGELOG.md`
entry exist. Standard agent-led closeout (retro, drift audit,
knowledge-curator triage, `release-phase-auditor` pass) applies to the
*planning* deliverable — the phase is not "done" in the mechanical sense
until gate G12 resolves one way or the other (approved and executed, or
explicitly declined and recorded as such).

**Mechanical implementation (only after G12 approval):** the file
changes in §"Scope" land in one commit; ADR flips to `Accepted`;
`ROADMAP.md` row flips to `done`.
