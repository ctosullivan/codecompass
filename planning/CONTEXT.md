# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and
`planning/retros/` for history; per `CLAUDE.md` §4, this file is for
session-resumption, not a project history.

## Current phase

**Phase 82 — Contract and Evidence Foundation — is `done`, including a
corrective pass that fixed four real assurance defects found by
independent post-completion review of the shipped code.** The v2
dependency root (`planning/v2-roadmap.md`) is now real: one evidence-
linked behavioural contract for `ledgerkit/reports.py::balance_from_spec`
exists end to end — Requirement → Claims → Evidence citing real source
locations → a versioned, multi-check oracle contract → real `PASS`
results against the current, unmodified `~/projects/ledgerkit` checkout
→ a real, demonstrated `FAIL` against a deliberately mutated scratch
copy — now with current-vs-historical verification genuinely
distinguished, execution-failure classification backed by pytest's own
structured report, immutable per-run evidence, and strict oracle-schema
type/value enforcement. `decisions/0078`-`0082` govern this phase's
design; none of Phases 83-88 has begun.

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
- `decisions/0082` — a later, separate corrective pass against the
  already-`done` Phase 82's own *shipped code* (not its plan): fixes
  current-vs-historical verification conflation, execution-failure
  misclassification (bare pytest exit code instead of its own structured
  `--junit-xml` report), destructive oracle-result/raw-output overwrite,
  and insufficient oracle-schema type/value enforcement. Does not reopen
  `decisions/0080`/`0081`'s own design.

**What exists now, concretely**:

- `src/codecompass/oracle.py` (shipped, corrected): `OracleContract`/
  `OracleCheck`/`OracleResult` schema parsing (real YAML, `pyyaml`, now
  with strict type/value enforcement — a real boolean required for
  `required`, a supported `schema_version`/`execution_provider` checked
  at parse time, malformed YAML caught as a controlled error), Phase
  81B-style content digesting (`compute_tree_digest`, reusing
  `_canonical_digest_of_hashes`'s construction) scoped to each
  contract's own explicit `tested_paths`/`test_input_paths`, one
  `pytest` execution provider (pins the target repo's own interpreter
  and `PYTHONPATH` — confirmed necessary this phase, see `L-101`;
  classifies outcomes from pytest's own structured `--junit-xml` report,
  not a bare exit code — see `L-102`), immutable per-run
  `<check_id>--<run_id>` result/raw-output naming, the
  `evaluate_result_precedence`/`aggregate_contract` PASS/FAIL/GAP/
  INVALID rule, and `accept_baseline` (the one explicit, never-automatic
  baseline-minting action, `CLAUDE.md` §1 L-087).
- `knowledge_intermediate.py::derive_epistemic_profile` (zero new
  persisted fields): INTENDED/OBSERVED/VERIFIED/CONTESTED, each computed
  independently, reusing `derive_provenance_label`'s own id-resolution
  helpers. Now also reports `unconfirmed_scopes` — a required scope
  whose only citation is a historically recorded `PASS` that could not
  be reconfirmed against a live, reachable `repo_root` — distinct from
  both `verified_scopes` (confirmed current) and `known_gap_scopes` (no
  evidence at all).
- `scripts/check_contracts.py` (maintainer script) and
  `check_knowledge_base.py::check_verified_status_cites_passing_oracle_
  result` (check): schema, cross-reference, tamper-evidence, GAP-
  aggregate, and depth-not-scope validators. The `status: verified`
  check applies **only** to a slug with a `planning/contracts/<slug>/`
  directory — a named, explicit compatibility exemption covers every
  pre-existing `status: verified` record (`REQ-DOCORIGIN-001/002/003`,
  `REQ-HSAPI-001`-`006`, `CL-DEPTH-001`, `CL-FPSS-006/007`), confirmed
  untouched. Both scripts now fail closed (a blocking finding, not
  informational) when current verification is claimed but the Ledgerkit
  checkout is unavailable to confirm it — `check_contracts.py --strict`
  via a new `contract-current-verification-unconfirmable` finding,
  `check_knowledge_base.py` via a real `--ledgerkit-root` flag threaded
  into `derive_epistemic_profile` instead of a hardcoded `None`.
- One real contract: `planning/knowledge/balance-from-spec/` (1 REQ, 3
  CL, 3 EV, 1 DEC, 1 OBS) + `planning/contracts/balance-from-spec/`
  (contract + four committed, real `PASS` oracle-result files across two
  runs — the original two, immutably preserved, plus two from a later
  re-run during the corrective pass — each independently re-verified
  byte-identical-on-digest by an independent audit).
- `scripts/run_balance_from_spec_oracle.py` (maintainer script, like
  `prepare_cleanroom_branch.py`) — re-runs the real oracle against a
  given Ledgerkit checkout, writing one new, permanent result/raw-output
  file pair per execution, never overwriting a prior run's own evidence.
- 65 new tests total across both the original implementation and the
  corrective pass (`tests/test_oracle.py`, `tests/test_check_contracts.py`,
  plus additions to `tests/test_knowledge_intermediate.py` and
  `tests/test_check_knowledge_base.py`), covering every one of the
  governing prompt's original twelve required verification scenarios
  plus the corrective pass's own four defect-specific negative controls.

`decisions/0062`'s Priority A-F framework remains superseded as the
primary strategic framework by `decisions/0078`. Phase 81B (clean-room
redocumentation, `done`) and Phase 81 (the intermediate knowledge layer
Phase 82 directly extends, `done`) are reused-foundation background,
unmodified by Phase 82 — full detail in `planning/ROADMAP.md`'s own rows
and each phase's retro.

## What was just completed

**Phase 82 corrective pass**, 2026-10-22, direct user request
("CodeCompass Orchestrator — Phase 82 Corrective Pass"), one session,
eight commits (`078196c` ADR `decisions/0082` + plan §15; `098b312`
implementation; `8fc066e` retro + candidate learning `L-102`; `ae3731d`
regression tests landing a gap `knowledge-curator` found in `L-102`'s own
triage; `5aebe10` a one-line `promoted.md` hash fix; `63c4dd7` retro
expanded to full `TEMPLATE.md` shape after the first audit's own FAIL;
`59942e6` the passing re-audit's own record; this `CONTEXT.md`/
`ROADMAP.md`/plan-status-line reconciliation is the terminal commit).
Fixed four real assurance defects an independent post-completion review
found in Phase 82's *shipped code* (not its plan, which the original
phase had already corrected and implemented together): (A) current
verification could be asserted from a historically recorded `PASS`
alone, with no live reconfirmation against the real implementation; (B)
`run_pytest_check` converted any nonzero pytest exit code into `FAIL`,
misclassifying missing dependencies/collection errors/invalid node ids
as behavioural defects; (C) oracle-result/raw-output files were
overwritten on every re-run despite each carrying a unique `run_id`; (D)
`required: "false"` (a string) was silently accepted as truthy, and
`schema_version`/`execution_provider` had no parse-time validation.

Independent audits: `docs-reconstructor`'s per-phase drift audit
returned **CLEAN** (zero findings — all doc edits independently
verified against the real code). `release-phase-auditor`'s first
completion-audit pass returned **FAIL** on one gap — the corrective-pass
retro wasn't populated against every `planning/retros/TEMPLATE.md`
section — after adversarially re-deriving and falsification-testing
every one of the four defect fixes and finding all of them solid (plus
two non-blocking residuals outside this pass's own scope, see below).
Retro rewritten to full template shape (`63c4dd7`); a fresh
`release-phase-auditor` re-audit confirmed the gap closed and nothing
else had drifted. Verdict: **PASS** (`planning/retros/_audit-phase-82-
corrective-pass-reaudit.md`), with two explicitly-recorded non-blocking
residuals for future execution-provider work: an existing-but-wrong
decoy directory reports via `known_gap_scopes` rather than the more
precise `unconfirmed_scopes` (the fail-closed guarantee still holds
either way); an all-skipped pytest run still classifies as `PASS`
(pre-existing behaviour, not a regression this pass introduced).

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
- Two non-blocking residuals found by the Phase 82 corrective-pass
  independent audit, neither a regression and neither in that pass's own
  named scope: `derive_epistemic_profile` reports a required check whose
  cited result's digest mismatches an *existing-but-wrong* decoy
  directory via `known_gap_scopes` rather than the more precise
  `unconfirmed_scopes` (the fail-closed `status: verified` rejection
  still fires correctly either way — a labelling imprecision, not a
  safety gap); `oracle.py::_classify_pytest_junit` still classifies an
  all-skipped pytest run as `PASS` (pytest's own junit-xml counts a skip
  in `tests`, and no assertion ever actually ran) — pre-existing
  behaviour, not introduced by the corrective pass. Both are candidates
  for whoever next touches `oracle.py`'s execution-provider logic
  (Phase 83/84).

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
- `L-102` (promoted, `planning/learnings/promoted.md`): classify a
  subprocess oracle's outcome from its own structured report (e.g.
  pytest's `--junit-xml`), never from a bare exit code alone — already
  landed in `oracle.py::_classify_pytest_junit`, recorded for any future
  second execution provider (Phase 83/84).
