# Drift audit — Phase 42 (documentation lifecycle, Stage A)

**Auditor:** docs-reconstructor (MODE 1, per-phase drift audit)
**Input:** working tree vs `git` HEAD `cd433f9` (phase not yet committed)
**Date:** 2026-09-10

## Verdict

**NO DRIFT.**

## What this phase's diff actually changed

Files touched (working tree vs `cd433f9`):

| File | Nature of change |
|---|---|
| `scripts/check_user_docs.py` | +3 deterministic checks (internal-link resolution, fenced `codecompass` example-command validity, ADR Status / cross-ref integrity) + wiring |
| `tests/test_check_user_docs.py` | +11 tests for the above |
| `.claude/agents/docs-maintainer.md` | agent brief finalised (checks list, "don't restructure overview.md", "no current-truth doc affected" output path) |
| `.claude/skills/docs-sync/SKILL.md` | +3 checklist items mirroring the new checks |
| `planning/v1-redefinition/documentation-lifecycle.md` | §5 reworded to point at the new checklist file |
| `planning/learnings/inbox.md` | candidate learning L-004 filed |
| `planning/milestone-closeout-checklist.md` | new (planning) |
| `planning/v1-redefinition/architecture-split-candidates.md` | new (planning catalogue for Phase 61) |

**No change to `src/codecompass/`.** No change to `README.md`, `docs/`,
`architecture/`, `ai-docs/`, `CONTRIBUTING.md`, or `CHANGELOG.md` in this
diff.

## Observable product-behaviour changes

**None.** Nothing in the diff alters the `codecompass` CLI surface,
flags, config schema (`VendorConfig` / `vendor.toml`), context-graph
schema, generated-file formats (`vendor/`, `context-graph.db`, Skills,
`/discovery`), defaults, or user-visible error messages.

`scripts/check_user_docs.py` is maintainer-only tooling — it is not part
of the shipped `codecompass` package and is not a documented product
feature (Phase 36 precedent). Its new checks change the maintainer's
local/CI workflow, not product behaviour. `grep` across `README.md`,
`docs/`, `architecture/`, `ai-docs/` for `check_user_docs` /
`scripts/check` / "deterministic doc" returns no hits, so no current-truth
product doc describes this tool at all.

## Forward check (docs describing changed behaviour)

No changed behaviour is product-facing, so there is no current-truth
product-doc sentence to re-verify.

## Reverse check (change silently falsifies an untouched doc sentence)

Considered whether the new script behaviour, the agent-brief wording, the
SKILL.md items, or the planning-doc edits make any existing sentence in
`README.md` / `docs/` / `architecture/` / `ai-docs/` false. They do not:
those docs do not reference the checker, the docs-maintainer/docs-sync
workflow, or the milestone closeout gate. The lifecycle machinery lives
entirely in `planning/` and `.claude/`.

## Scope note

- **Checked:** full working-tree diff vs `cd433f9` including the two
  untracked planning files; `grep` of all four current-truth doc trees
  for the checker, the new subcommand-introspection behaviour, ADR-status
  concepts, and internal-link tooling; confirmed `src/codecompass/`
  untouched and the CLI surface unchanged.
- **Deliberately not treated as Phase 42 drift:** the 36 history-narration
  passages + 4 self-contradictions in `architecture/overview.md`
  catalogued in
  `planning/v1-redefinition/architecture-split-candidates.md`. These
  pre-date Phase 42, are deferred to Phase 61, and are tracked by
  candidate learning L-004. A per-phase drift audit is scoped to what the
  phase's own diff changed; pre-existing accretion is exactly what L-004
  and the Phase 60/61 blank-slate cycle exist to address.
- **Not in this audit's remit:** whether the phase's own DoD artifacts
  (CHANGELOG entry, ROADMAP/CONTEXT updates, CLAUDE.md §5 / CONTRIBUTING
  mirror from gate G4) are complete — that is the `release-phase-auditor`'s
  check. This audit only concerns product-doc truth.
