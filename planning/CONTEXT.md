# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and
`planning/retros/` for history; per `CLAUDE.md` §4, this file is for
session-resumption, not a project history.

## Current phase

**Phase 81B Amendment 4 is implemented and closed out; `planning/ROADMAP.md`'s
own `done` flip is the one remaining step**, pending a passing re-audit
(the first independent completion-audit pass, `planning/retros/_audit-phase-81b-amendment-4.md`,
returned **FAIL** — this file itself being stale was the blocking
finding; fixed in this same overwrite). Plan:
`planning/phase-81b-clean-room-redocumentation.md` §26.

Amendment 4 removed Phase 81B's original credential-provisioning
blocker by giving the sandbox an *inference capability* instead of a
*credential*: `scripts/cleanroom_broker.py`, a narrowly-scoped broker
that stays outside the sandbox, holds the real subscription
authentication, and exposes only a fixed `{system_prompt, messages} ->
{output}` protocol over a local Unix-socket IPC channel — verified, by
active test including a context-contamination canary, to keep every
credential and the orchestrator's own conversation out of the sandbox's
reach (`planning/phase-81b-broker-isolation-investigation.md`). One
narrow, content-neutral, non-suppressible account-level reminder
residual (email/date/token-budget/OS-type/generic security policy) was
found, named, and explicitly accepted by the user as non-disqualifying.

**This actually unblocked the full run, end to end:**

- 11 real cold-reader passes against the real handoff (10 rounds of
  genuine reconciliation — 6 of them real bugs in the clean-room
  tooling itself: git-submodule file tracking, a silently-drifting
  file-inclusion allow-list, a truncated mechanical table, stray YAML
  syntax leaking into generated prose, a missing allow-list entry, a
  doc-validator parsing gap) reached a genuine `SUFFICIENT` verdict —
  `planning/phase-81b-cold-reader-verdict.md`.
- The authoritative writer produced a complete, fresh documentation
  set inside the same verified boundary, preserved on
  `cleanroom/result-8325272` before any comparison with legacy
  documentation.
- An independent legacy-document gap review (never showing legacy
  prose to any writer) found 6 candidates, verified 5 as real, and
  reconciled them via a second isolated writer context —
  `planning/phase-81b-legacy-gap-review.md`.
- **Documentation disposition was actually executed**: `README.md`,
  the full `docs/` tree (24 files), and `ai-docs/` on this repository
  are now the clean-room reconstruction, not the pre-existing
  narrative (commit `7cb09c5`, 77 files changed). `CONTRIBUTING.md`
  was correctly left untouched (it mirrors `CLAUDE.md`'s own
  governance content, the same self-governing category, discovered
  only by reading its real content in depth — not ordinary narrative
  documentation the clean-room writer should have replaced).
  `codecompass-template`'s own sibling repository received a
  deliberately lighter pass (9 files, commit `dff3f4d` on that
  repository's own `origin/main`) —
  `planning/phase-81b-template-redocumentation.md`.
- The proven workflow is now documented at
  `docs/development/clean-room-redocumentation.md` — written only
  after the run had actually succeeded.
- A first-principles sweep against the 12 defect classes the user's
  own governing prompt named found none still present.
- Full test suite: 899 passed, 2 skipped. Lint clean.
  `check_user_docs.py --strict`: no findings.
  `check_knowledge_base.py --strict`: only pre-existing `(info)`-level
  snapshot-divergence findings.

The "Strict mechanical isolation for documentation-reconstruction
stages" backlog item (`planning/strict-isolation-for-documentation-
reconstruction.md`) is updated accordingly — isolation `VERIFIED`, and
now the authoritative-writer-run gap is also closed; see
`planning/ROADMAP.md`'s own backlog row for the current wording.

**Two items the first completion-audit pass found not yet filed,
fixed in this same session:**

1. `.claude/agents/docs-reconstructor.md`/`context-researcher.md`/
   `domain-skeptic.md`/`release-phase-auditor.md` still reference
   `docs/domain/` (now permanently deleted) and/or a bare
   `architecture/overview.md` (now `docs/architecture/overview.md`) as
   if current. This was disclosed in commit `7cb09c5`'s own message as
   explicitly deferred (editing agent-workflow definitions is out of
   this phase's own scope — the user's governing prompt named
   "multi-agent workflow" as something not to expand into), but was
   never actually filed as a learning/context-gap — now filed as
   `L-098` (see `planning/learnings/inbox.md`).
2. No ADR existed for the amendment's own central, non-obvious
   tradeoff (give the sandbox a capability, not a credential; accept a
   named, content-neutral context residual as non-disqualifying) —
   now `decisions/0076`.

Phase 81 itself (persistent bidirectional intermediate knowledge layer,
all three corrective passes) remains `done`, unmodified, not reopened by
Phase 81B. Full prior history for Phases 0 through 81 is in git history
and each phase's own retro/closeout record under `planning/retros/` —
not repeated here (established at Phase 71, `planning/ROADMAP.md` §2).

## What was just completed

Phase 81B Amendment 4's full implementation, across two sessions
(2026-10-09/10): broker build + isolation investigation (including a
real credential-leak-class defect found and fixed, the sandbox
inheriting the broker's own launch directory) → 11 cold-reader passes
to `SUFFICIENT` → the authoritative writer run, preserved → legacy-gap
review and reconciliation → real documentation disposition against
both repositories → the durable workflow document → a 12-class defect
sweep → full test/lint validation → an independent per-phase drift
audit (2 non-blocking observations: a self-disclosed `.claude/agents/`
staleness list, and widespread stale doc-path references inside
`src/codecompass/*.py` docstrings/error strings — both since fixed) →
learning triage (lead-performed directly; the dispatched
`knowledge-curator` subagent failed with a session-level rate limit) →
a phase retro update → a changelog rewrite → a first independent
completion audit (**FAIL** — this file's own staleness, plus the two
items named above) → the fixes in this same overwrite → a second,
narrow re-audit pass is the next step before `planning/ROADMAP.md`'s
own `done` flip.

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

**Dispatch a fresh, narrow independent completion-audit re-check**
against the commit that lands this overwrite plus `decisions/0076` and
`L-098`'s filing — the first pass (`planning/retros/_audit-phase-81b-amendment-4.md`)
returned `FAIL` specifically for this file's own staleness, which is
fixed in this same commit, and named two smaller, now-also-fixed gaps
(the missing ADR; the unfiled `.claude/agents/` learning). Per
`CLAUDE.md` §5, any commit touching audited scope voids a prior pass —
a fresh one (it can be narrow, confirming only the three named fixes,
matching the pattern already used once in this phase's own first
implementation round) is required before `planning/ROADMAP.md`'s Phase
81B row can flip to `done`.

Once that re-audit passes (`PASS` or `PASS WITH NON-BLOCKING
OBSERVATIONS`): flip `planning/ROADMAP.md`'s Phase 81B row to `done`,
update this file's own "Current phase" section to reflect that, and
update `planning/phase-81b-clean-room-redocumentation.md`'s own Status
line — the narrow, three-target terminal reconciliation commit
`CLAUDE.md` §5 names as exempt from re-auditing itself.

Phases 75 through 81 (not 81B) remain closed (`done`) and pushed to
`origin` — no further action needed on any of them per `CLAUDE.md` §6.

The next open items requiring a human/lead decision, unrelated to Phase
81B and none currently claimed by a drafted plan or phase number:

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
