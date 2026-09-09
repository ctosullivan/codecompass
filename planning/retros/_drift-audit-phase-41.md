# Drift audit — Phase 41

**Auditor:** docs-reconstructor (MODE 1, per-phase independent drift audit)
**Date:** 2026-09-10
**Base:** `c22d8e4` (HEAD) vs uncommitted working tree
**Verdict:** `NO DRIFT`

## What the phase changed (verified against the diff)

`git diff --stat c22d8e4` + `git status` show 17 modified tracked files and
new untracked paths. Grouped by kind:

- **Governance / process:** `CLAUDE.md` §5 (DoD gains a per-phase retro +
  per-phase docs-drift audit condition), mirrored into `CONTRIBUTING.md`;
  `decisions/0050-phase-retros-and-per-phase-docs-drift-audit.md` (new);
  `.claude/agents/{docs-reconstructor,knowledge-curator,release-phase-auditor}.md`;
  `.claude/skills/docs-sync/SKILL.md`; `planning/agent-led-workflow.md`;
  `planning/v1-redefinition/{agent-led-development,documentation-lifecycle,proposed-governance-changes}.md`;
  `planning/phase-41-learning-lifecycle.md`; `planning/ROADMAP.md`
  (phase-41 row title/status).
- **Learnings lifecycle content:** `planning/learnings/{README,inbox,promoted}.md`,
  new `planning/learnings/candidates/` directory.
- **New retro artifact area:** `planning/retros/` (`README.md`, `TEMPLATE.md`).
- **Maintainer-only tooling:** `scripts/check_user_docs.py` gains
  `check_learnings_candidate_fields`, `check_promoted_learnings_logged`,
  `check_stale_evidence_gathering`, `check_phase_retros_present`, plus an
  informational-vs-blocking `--strict` distinction; `tests/test_check_user_docs.py`
  adds coverage for those.

## Why this is NO DRIFT

The per-phase audit is scoped to *observable product behaviour*: the
`codecompass` CLI, its flags, config schema, generated-file formats, and
the context graph.

1. **No `src/codecompass/` change.** `git diff --stat c22d8e4` lists no
   file under `src/`. The phase plan and diff touch only `.claude/`,
   `planning/`, `decisions/`, `scripts/`, `tests/`, `CLAUDE.md`,
   `CONTRIBUTING.md`. Product runtime behaviour is unchanged, so no
   current-truth product doc can have been falsified.

2. **`scripts/check_user_docs.py` is not a product surface.** Its module
   docstring (unchanged in intent, reaffirmed this phase) states: "Not
   shipped, not a `codecompass` subcommand." It is a maintainer-repo lint
   over CodeCompass's *own* docs (Phase 36 precedent). Its new checks
   (learnings-hygiene, retro presence) inspect `planning/` artifacts only.
   No `codecompass` CLI command wraps or exposes it.

3. **No current-truth doc mentions the changed concepts.** `grep` for
   `check_user_docs`, `retros`, `learnings/` across `README.md`, `docs/`,
   `architecture/`, `ai-docs/` returns no matches — these are internal
   governance concepts that the product docs never described, so there is
   nothing to make stale.

4. **DoD / retro / drift-audit rules are governance, not product.** The
   `CLAUDE.md` §5 and `CONTRIBUTING.md` edits describe how contributors
   and agents work, not how the tool behaves. `CLAUDE.md` and
   `decisions/` are outside this auditor's remit and outside product-doc
   scope.

5. **Reverse check.** No pre-existing sentence in `README.md`, `docs/`,
   `architecture/`, or `ai-docs/` becomes false as a side effect: none of
   them reference the learnings lifecycle, the retro artifact, the DoD
   condition list, or `scripts/check_user_docs.py`'s rule set.

## Scope note

- **Checked:** full working-tree diff vs `c22d8e4` (`git diff`,
  `git diff --stat`, `git status` untracked); the full diff of
  `scripts/check_user_docs.py`; `grep` of `README.md`, `docs/**`,
  `architecture/**`, `ai-docs/**` for every concept the phase introduced
  or renamed (`check_user_docs`, `retros`, `learnings/`); the ROADMAP
  phase-41 row change.
- **Deliberately excluded:** `.claude/**`, `planning/**`, `CLAUDE.md`,
  `CONTRIBUTING.md`, `decisions/**`, `scripts/**`, `tests/**` as targets
  for *rewrite* — they are process/governance and this phase made no
  accompanying `src/codecompass/` behaviour change, so per the audit
  charter they implicate no product documentation. `scripts/check_user_docs.py`
  was read (not skipped) precisely to confirm it remains maintainer-only
  tooling with no product-surface leakage.
- **Blocking findings:** none.
- **Non-blocking findings:** none.
