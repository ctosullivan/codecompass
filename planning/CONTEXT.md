# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and
`planning/retros/` for history; per `CLAUDE.md` §4, this file is for
session-resumption, not a project history.

## Current phase

**No roadmap phase is currently in progress.** Phase 81B (clean-room
project redocumentation from intermediary knowledge) is **closed, result
`blocked`** — implemented in full through its own plan's required first
step, then correctly stopped at that plan's own hard gate
(`planning/phase-81b-clean-room-redocumentation.md` §6.3/§18/§21) rather
than completed or downgraded to best-effort. Full account:
`planning/retros/phase-81b-clean-room-redocumentation.md` (retro) and
`planning/phase-81b-mode-b-isolation-investigation.md` (the investigation
itself). Independently audited: `planning/retros/_audit-phase-81b.md`,
**PASS WITH NON-BLOCKING OBSERVATIONS**, both observations since closed
in a follow-up commit, re-confirmed by a narrow second audit pass.

What was delivered, for real, against this repository: knowledge
preparation (`documented_revision` `46601a1` — 26 of 30 previously-
unclassified `codecompass-domain` Claims given a real `assertion_kind`,
the measured root cause of 88% of the rendered projection defaulting
into `overview.md`; all five knowledge slugs rendered fresh); an
explicit-allowlist, fail-closed-validated clean-room branch-preparation
tool (`scripts/prepare_cleanroom_branch.py`, 8 tests, sources its file
list from `git ls-files` after a real raw-filesystem-walk bug was found
and fixed); a real, pushed clean-room branch (`cleanroom/redoc-46601a1`,
`handoff_commit` `468cffa4e013e56ad17df6c7536dd32a5774cd4b`), confirmed
via Mode A diff review and a genuine `.git`-free `git archive`
extraction; a rigorous Mode B isolation investigation (Linux namespaces +
`pivot_root`) actively verified against every named escape route
(filesystem, parent-path traversal, `.git` history, branches/remotes,
network, filesystem/environment credentials, MCP, agent context) except
one — no separately-scoped model-API credential (or local/offline model)
exists in this environment to operate an AI writer inside the verified
boundary; and `codecompass-template`'s own documentation disposition
report. Per the plan's own Amendment 1 hard gate, the authoritative
writer run, cold-reader, result branches, and documentation disposition
execution correctly did not proceed. No current-truth documentation
(`README.md`/`docs/`/`architecture/`/`ai-docs/`) was touched by this
phase, confirmed by an independent per-phase drift audit (NO DRIFT).

The "Strict mechanical isolation for documentation-reconstruction
stages" backlog item (`planning/strict-isolation-for-documentation-
reconstruction.md`) is updated with this real, substantive, more precise
result (isolation `VERIFIED`, writer-run `BLOCKED` for a distinct,
named, infrastructure reason) — see `planning/ROADMAP.md`'s own backlog
row. It remains `candidate, not funded, not scheduled`; its revisit
trigger is now specifically a separately-scoped model-API credential (or
a local/offline model) becoming available, not a further isolation-
mechanism attempt (that part is now solved).

Phase 81 itself (persistent bidirectional intermediate knowledge layer,
all three corrective passes) remains `done`, unmodified, not reopened by
Phase 81B. Full prior history for Phases 0 through 81 is in git history
and each phase's own retro/closeout record under `planning/retros/` —
not repeated here (established at Phase 71, `planning/ROADMAP.md` §2).

## What was just completed

Phase 81B's full implementation-through-blocked-closeout sequence in one
session (2026-10-08): planning (three same-day amendments, fourteen
corrections total, all recorded in place in the plan file itself) →
knowledge preparation → the real branch-preparation tool and its tests →
the real pushed clean-room branch → the Mode B isolation investigation
(a genuine, newly-tested namespace/`pivot_root` mechanism, with a real
credential leak found and fixed during testing) → `codecompass-
template`'s own disposition report → a per-phase docs-drift audit (NO
DRIFT) → a learning-triage pass (`knowledge-curator`; L-089 and L-090
promoted and landed as code fixes + regression tests in
`scripts/prepare_cleanroom_branch.py`/`tests/test_prepare_cleanroom_branch.py`;
L-091 retained, not yet actionable as a standalone artifact) → a full
phase retro → a changelog entry → an independent completion audit
(`release-phase-auditor`, PASS WITH NON-BLOCKING OBSERVATIONS, both
observations closed in a follow-up commit and re-confirmed) → this
terminal `planning/ROADMAP.md`/`planning/CONTEXT.md`/plan-file-Status-
line reconciliation. All commits pushed to `origin/main`.

## Known standing gaps (current-state facts, not phase history)

- Cargo adapter (`decisions/0014`) never validated against real `cargo
  metadata` output or a real crate — no Rust toolchain available yet.
- `extract_npm_symbols` untested against real-world `.d.ts` authoring
  styles beyond hand-written fixtures.
- `chat.py` never run against the real Anthropic API in this
  environment.
- `staleness.py`'s version parser has no real PEP 440/semver
  correctness — string comparison only.
- No formal trigger-accuracy evaluation harness for per-vendor Skills.
- Cursor `.mdc` export has no `globs` field.
- A pre-Phase-74 `symbol_enrichment` row's producer remains honestly
  unknown (`NULL`) — new rows are attributed, historical ones cannot be
  retroactively.
- A submodule pin/checkout mismatch has no field distinguishing
  committed-parent-state divergence from purely local uncommitted
  checkout state (`CG-010`, filed Phase 76) — `codecompass query
  topology` gives the two SHAs and a match/mismatch verdict, but
  determining *why* they differ still requires `git status`/`git diff
  --cached` directly.
- A sibling worktree's dirtiness, when unprobed/stale, is honestly
  reported as such but carries no inline CLI signal that this could be
  the case — only `--help` text documents the sync-time-snapshot
  guarantee (`CG-011`, filed Phase 76).
- `vendor/` and a local `.venv/` exist in this checkout (both
  gitignored, freely regeneratable) — live artifacts, not fixtures.

## Next concrete step

**No roadmap phase is currently active.** Phases 75 through 81B are all
closed (`done` or, for 81B, its own honest `blocked` terminal state) and
pushed to `origin` — no further action needed on any of them per
`CLAUDE.md` §6.

The next open items requiring a human/lead decision, none currently
claimed by a drafted plan or phase number:

- Priority A's own narrowly-scoped follow-up trial, sketched (not
  started) in `planning/phase-78-amendment-followup-plan.md` — an
  existing-relationship-only task (Ledgerkit's own `stats` query-support
  extension).
- Priorities B/C/E/F (`decisions/0062`'s own "not yet planned" state).
- The "Strict mechanical isolation for documentation-reconstruction
  stages" backlog item (`planning/strict-isolation-for-documentation-
  reconstruction.md`) — **not** a next concrete step to execute now; it
  remains `candidate, not funded, not scheduled`, revisited only when a
  separately-scoped model-API credential or a local/offline model
  becomes available in this project's own working environment (Phase
  81B already solved the isolation-mechanism half of this gap — see
  "Current phase" above).
