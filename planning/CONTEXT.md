# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and
`planning/retros/` for history; per `CLAUDE.md` §4, this file is for
session-resumption, not a project history.

## Current phase

**Phase 82 — Contract and Evidence Foundation — is `done`.** The v2
dependency root (`planning/v2-roadmap.md`) is now real: one evidence-
linked behavioural contract for `ledgerkit/reports.py::balance_from_spec`
exists end to end — Requirement → Claims → Evidence citing real source
locations → a versioned, multi-check oracle contract → real `PASS`
results against the current, unmodified `~/projects/ledgerkit` checkout
→ a real, demonstrated `FAIL` against a deliberately mutated scratch
copy. `decisions/0078`-`0081` govern this phase's design; none of
Phases 83-88 has begun.

- `decisions/0078` — the original v2 repositioning.
- `decisions/0079` — the Cross-Project Semantic Overlay track's
  three-layer model and project-qualified reference envelope (post-v2,
  still not authorised to implement).
- `decisions/0080` — corrects Phase 82's epistemic-state design to a
  derived, read-time view (no new persisted field) and strengthens
  oracle-result identity to bind to the exact tested subject via a
  content digest.
- `decisions/0081` — corrects four remaining structural gaps found by
  direct review: a singular check replaced by an explicit, versioned
  `checks:` collection; PASS/FAIL/GAP/INVALID given a deterministic
  precedence/aggregation rule (`GAP` is strictly an aggregate, never a
  per-result field); vacuous verification structurally prevented, with
  a named, explicit compatibility exemption for twelve pre-existing
  `status: verified` records that predate this mechanism; tested-
  subject/test-input digests scoped to explicit, reviewable file lists.
  **Also explicitly authorised Phase 82 implementation in the same
  session** — the first v2 session where planning correction and
  implementation happened together rather than across separate,
  maintainer-gated sessions.

**What exists now, concretely**:

- `src/codecompass/oracle.py` (new, shipped): `OracleContract`/
  `OracleCheck`/`OracleResult` schema parsing (real YAML, `pyyaml`), Phase
  81B-style content digesting (`compute_tree_digest`, reusing
  `_canonical_digest_of_hashes`'s construction) scoped to each
  contract's own explicit `tested_paths`/`test_input_paths`, one
  `pytest` execution provider (pins the target repo's own interpreter
  and `PYTHONPATH` — confirmed necessary this phase, see `L-101`), the
  `evaluate_result_precedence`/`aggregate_contract` PASS/FAIL/GAP/
  INVALID rule, and `accept_baseline` (the one explicit, never-automatic
  baseline-minting action, `CLAUDE.md` §1 L-087).
- `knowledge_intermediate.py::derive_epistemic_profile` (new function,
  zero new persisted fields): INTENDED/OBSERVED/VERIFIED/CONTESTED, each
  computed independently, reusing `derive_provenance_label`'s own
  id-resolution helpers.
- `scripts/check_contracts.py` (new maintainer script) and
  `check_knowledge_base.py::check_verified_status_cites_passing_oracle_
  result` (new check): schema, cross-reference, tamper-evidence, GAP-
  aggregate, and depth-not-scope validators. The new `status: verified`
  check applies **only** to a slug with a `planning/contracts/<slug>/`
  directory — a named, explicit compatibility exemption covers every
  pre-existing `status: verified` record (`REQ-DOCORIGIN-001/002/003`,
  `REQ-HSAPI-001`-`006`, `CL-DEPTH-001`, `CL-FPSS-006/007`), confirmed
  untouched by this phase.
- One real contract: `planning/knowledge/balance-from-spec/` (1 REQ, 3
  CL, 3 EV, 1 DEC, 1 OBS) + `planning/contracts/balance-from-spec/`
  (contract + two committed, real `PASS` oracle-result files, re-run and
  re-verified byte-identical-on-digest by the independent audit).
- `scripts/run_balance_from_spec_oracle.py` (maintainer script, like
  `prepare_cleanroom_branch.py`) — re-runs the real oracle against a
  given Ledgerkit checkout.
- 53 new tests (`tests/test_oracle.py`, `tests/test_check_contracts.py`,
  plus additions to `tests/test_knowledge_intermediate.py` and
  `tests/test_check_knowledge_base.py`), covering every one of the
  governing prompt's twelve required verification scenarios.

`decisions/0062`'s Priority A-F framework remains superseded as the
primary strategic framework by `decisions/0078`. Phase 81B (clean-room
redocumentation, `done`) and Phase 81 (the intermediate knowledge layer
Phase 82 directly extends, `done`) are reused-foundation background,
unmodified by Phase 82 — full detail in `planning/ROADMAP.md`'s own rows
and each phase's retro.

## What was just completed

**Phase 82 implementation**, 2026-10-21, direct user request
("CodeCompass Orchestrator — Correct Phase 82 Plan and Proceed with
Implementation"), one session, five commits (`d945864` planning
corrections/`decisions/0081`; `ebca4bf` implementation; `62b2f39` retro +
candidate learning `L-101`; `63f4d84` knowledge-curator triage,
promoted; `a450bfe` docs-drift fixes; `a3d4045` independent audit
records; this `CONTEXT.md`/`ROADMAP.md`/plan-status-line reconciliation
is the terminal commit). Corrected the plan's four remaining structural
gaps, then implemented, verified, and closed out the same session — the
first v2 phase where the governing prompt itself explicitly authorised
proceeding straight to implementation rather than stopping for a
separate maintainer-approval round trip.

Independent audits: `docs-reconstructor`'s per-phase drift audit found
3 non-blocking doc-sync gaps (two maintainer-tooling docs omitting new
Phase 82 scripts/tests; `docs/decisions.md`'s ADR index stopping at
`0075`, a pre-existing gap this phase extended rather than left) — all
three fixed in `a450bfe`. `release-phase-auditor`'s completion audit
independently re-ran the real oracle (byte-identical digests on
re-execution), the real negative control, the full test suite (980
passed, 2 skipped — both pre-existing), `ruff`, and all three strict
validators; deliberately broke vacuous-verification prevention (removed
a committed oracle-result, confirmed the new check newly flags it,
restored); confirmed `CLAUDE.md` untouched and every `decisions/0078`-
`0081` file append-only. Verdict: **PASS WITH NON-BLOCKING
OBSERVATIONS** (the one gap — no standalone written drift-audit record
— backfilled in the same closeout as `planning/retros/_drift-audit-
phase-82.md`).

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
  **Note from Phase 82**: this project's own `.venv` is where `pytest`
  actually lives — the bare `python3`/`/usr/bin/python` on this machine
  has no `pytest` installed; always invoke tests via `.venv/bin/python
  -m pytest`, not a bare `python`/`pytest` on `$PATH`.
- Several `.claude/agents/*.md` files still reference the now-deleted
  `docs/domain/` and a bare `architecture/overview.md` (now
  `docs/architecture/overview.md`) as if current — filed as `L-098`
  (`planning/learnings/inbox.md`), not yet acted on (editing
  agent-workflow definitions is its own, separate decision).

## Next concrete step

**Phase 83 (Semantic Change Assurance) is next, not yet phase-planned.**
Per `CLAUDE.md` §1, writing `planning/phase-83-*.md` is the required
next step before any Phase 83 implementation begins — scoped against
evidence current at that time (`planning/v2-roadmap.md` records only
roadmap-depth sequencing for it: detect a deliberately-introduced
Ledgerkit semantic regression Phase 82's own contract should catch,
without falsely claiming complete verification elsewhere in the same
report; needs Phase 82's real contract/oracle-result schema to know what
a change could violate and how to report a gap).

Other open items requiring a human/lead decision, none currently claimed
by a drafted plan or phase number:

- Whether to fund any Post-v2 Cross-Project Semantic Overlay stage
  (`planning/post-v2-cross-project-overlay-backlog.md`) — explicitly not
  authorised by any amendment to date; Stage 1 cannot begin before Phase
  82 is `done` — it now is, but no further authorisation has been given.
- Priority A's own narrowly-scoped follow-up trial, sketched (not
  started) in `planning/phase-78-amendment-followup-plan.md` — now
  superseded in strategic priority by Phase 83/85's own, sharper
  change-assurance framing (`decisions/0078`), but not deleted; still
  available if a human decision prefers it first.
- The "Strict mechanical isolation for documentation-reconstruction
  stages" backlog item — `resolved` (Phase 81B Amendment 4), no further
  action pending.
- `L-101` (promoted, `planning/learnings/promoted.md`): an oracle
  execution mechanism must pin the interpreter and `PYTHONPATH` of the
  exact tree it executes, or a sibling checkout's own editable package
  install silently shadows a scratch mutation — already landed in
  `oracle.py`, recorded for any future execution-provider work (Phase
  83/84).
