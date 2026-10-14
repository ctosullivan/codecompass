# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and
`planning/retros/` for history; per `CLAUDE.md` §4, this file is for
session-resumption, not a project history.

## Current phase

**Phase 81B is `done`.** Amendment 4 (2026-10-09/10) removed the
original credential-provisioning blocker and completed the
authoritative clean-room redocumentation this phase was always meant to
produce. A first independent completion-audit pass returned `FAIL`
(this file's own staleness at the time, plus a missing ADR and an
unfiled learning); all three were fixed, and a second, narrow re-audit
pass confirmed `PASS`.

**Amendment 5 (corrective, 2026-10-14, direct user request)** then
hardened the reusable clean-room preparation/isolation *machinery*
itself — explicitly without rerunning the cold-reader/writer/legacy-gap/
disposition cycle, and without touching either repository's current,
accepted documentation. Six real, confirmed defects were found by direct
code/branch inspection and fixed: (1) a broad allow-listed directory
(`tests/**`) swept in doc-shaped files with no per-file review, letting
five real narrative leaks through (`tests/README.md` plus four
`ledgerkit_lifecycle_demo` fixture docs) — fixed with a fail-closed
keep/exclude classification that fails the build closed on any future
unclassified doc-shaped file; (2) `documented_revision` was a trusted
claim, not enforced — `scripts/prepare_cleanroom_branch.py` now exports
every allow-listed path from the Git object database at the exact
declared revision (including pinned-gitlink submodule resolution, never
the working tree or the submodule's current checkout); (3) the manifest's
`handoff_commit` field tried to name its own eventual commit SHA
(circular by construction, confirmed one-commit-stale against a real
branch) — replaced with a non-circular, content-addressed
`payload_tree_sha256`/`payload_file_hashes` scheme (`decisions/0077`);
(4) manifest validation depended on the live parent repository and never
hashed the actual payload — now fully self-contained; (5) the Mode B
isolation preflight existed only as investigation prose — new
`scripts/verify_cleanroom_isolation.py` builds a real, disposable
namespace/`pivot_root` sandbox and actively tests all eleven conditions
named by the amendment's own governing instruction; (6) a test-module
docstring claimed hash-mismatch coverage that didn't exist — now
genuinely tested. The historical claim about Amendment 4's own writer
run is corrected accordingly: no longer "zero pre-existing narrative
prose of any kind," now naming the five real fixture-scale files found,
while confirming the real `README.md`/`docs/`/`architecture/`/`ai-docs/`
tree was never allow-listed at any point. Independently audited twice
(`planning/retros/_audit-phase-81b-amendment-5.md`): a main pass
(`PASS WITH NON-BLOCKING OBSERVATIONS` — one count error in the written
record, fixed) and a narrow re-audit confirming that fix (`PASS`).
`planning/ROADMAP.md`'s Phase 81B row is flipped to `done` in the same
commit as this overwrite. Plan:
`planning/phase-81b-clean-room-redocumentation.md` §26 (Amendment 4) and
§27 (Amendment 5, corrective).

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

Phase 81B Amendment 5 (corrective), 2026-10-14, direct user request,
in one session: investigated and confirmed six real mechanism defects
by direct code/branch inspection → recorded the corrective amendment in
the plan file (§27) before implementing → fixed `scripts/
prepare_cleanroom_branch.py` (exact-revision Git-object-database export
with pinned-gitlink submodule resolution; a fail-closed file-level
narrative classification gate for the three broad allow-listed
directories; a self-contained, content-addressed manifest scheme
replacing the circular `handoff_commit` field, `decisions/0077`) → added
`scripts/verify_cleanroom_isolation.py` (a repeatable, real-sandbox-
building preflight for all eleven named isolation conditions,
adversarially confirmed this session to genuinely catch a regression —
removing the sandbox launch's own `env -i` boundary was shown, by direct
manual test, to make the preflight actually fail) → 30 tests in
`tests/test_prepare_cleanroom_branch.py` (up from 11) and 9 new tests in
`tests/test_verify_cleanroom_isolation.py`, full suite 917 passed, lint
clean → retro/changelog/durable-workflow-doc hygiene → a real
`knowledge-curator` dispatch triaged two new learnings (L-099, L-100,
both promoted, each independently re-verified against the actual
source before promoting, not rubber-stamped) → a first independent
completion audit (`PASS WITH NON-BLOCKING OBSERVATIONS` — one real count
error in the written record: "six" leaked files claimed where the
mechanism's own enforced set has five; fixed) → a narrow independent
re-audit confirming that fix (`PASS`) → this terminal
`planning/ROADMAP.md`/`planning/CONTEXT.md`/plan-file-Status-line
reconciliation. Phase 81B's row in `planning/ROADMAP.md` is now `done`
again. Confirmed by both audits: zero changes to either repository's
current, accepted documentation output (`codecompass`'s `README.md`/
`docs/`/`ai-docs/`, and `codecompass-template`, still at `dff3f4d`) —
this amendment fixed the machine, not the product. All commits to be
pushed to `origin/main` immediately following this reconciliation
(§6's push-on-DoD-pass convention; `codecompass-template` needs no push,
since it was never touched).

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
closed (`done`) and pushed to `origin` — no further action needed on
any of them per `CLAUDE.md` §6. The one real, known, deliberately-
deferred gap Phase 81B's own closeout surfaced but did not fix —
several `.claude/agents/*.md` files referencing the now-deleted
`docs/domain/` and the moved `architecture/overview.md` as if current —
is filed and findable at `planning/learnings/inbox.md` `L-098`, not a
next concrete step to execute unilaterally (editing agent-workflow
definitions is its own, separate decision).

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
