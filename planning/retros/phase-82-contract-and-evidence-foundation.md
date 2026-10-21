# Phase 82 retro — Contract and Evidence Foundation

- **Date:** 2026-10-21
- **Commit(s):** `d945864` (planning corrections, `decisions/0081`),
  `ebca4bf` (implementation).
- **Agents used:** none during implementation (lead-authored, direct
  user authorisation to proceed); `docs-reconstructor` and
  `release-phase-auditor` dispatched for independent closeout checks
  (see those reports).

## Where we are

Phase 82 is the dependency root of the entire v2 roadmap
(`planning/v2-roadmap.md`) — every later phase (83-88) cites a real
behavioural contract, oracle schema, and epistemic view that only exist
after this phase. Three prior sessions (this same day) produced the
strategic repositioning (`decisions/0078`), a cross-project-overlay
amendment (`decisions/0079`), and a corrective amendment
(`decisions/0080`) — all planning-only, explicitly deferring
implementation pending maintainer approval. This phase's own governing
prompt corrected four remaining structural gaps (`decisions/0081`) and
explicitly authorised proceeding straight to implementation in the same
session, which is what actually happened here for the first time in the
v2 effort.

## Goal

Correct the Phase 82 plan's remaining defects (a singular oracle check
masquerading as a multi-condition contract; an unspecified PASS/FAIL/
GAP/INVALID precedence rule; no protection against vacuous verification;
an unscoped tested-subject digest), then implement, verify, and close
out one real, evidence-linked Ledgerkit behavioural contract end to end.

## Scope delivered vs planned

Delivered exactly the plan's own §1 scope, nothing from §83/84's
deferred list: a behavioural-contract record format reusing existing
REQ-/CL-/EV- ids; a derived (never persisted) epistemic view; a
versioned, multi-check oracle-contract/oracle-result schema; one pinned
Ledgerkit scenario with two genuinely distinct, already-passing scopes
and a real negative control; baseline-identity fields with an
explicit, never-automatic acceptance action; deterministic validators
for every new artifact kind. No `context-graph.db` change, no MCP
exposure, no change-impact traversal — all correctly out of scope and
untouched.

One deviation from the plan's own original §2 framing, decided
mid-implementation rather than left implicit: the plan anticipated a
single `check_reference`; this phase (per `decisions/0081`) pinned
**two** real checks (`test_single_section_rows_and_subtotal`,
`test_multi_section_correct_values`) to actually exercise the
multi-check collection and scope-qualified verification the corrected
plan requires — a strictly additive choice within the same one-contract
vertical slice, not scope creep.

## What was achieved

- `src/codecompass/oracle.py` (new, shipped): contract/result schema
  parsing, Phase 81B-style content digesting scoped to explicit file
  lists, one `pytest` execution provider, the PASS/FAIL/GAP/INVALID
  precedence/aggregation rule, baseline acceptance.
- `knowledge_intermediate.py::derive_epistemic_profile` (new): the
  derived INTENDED/OBSERVED/VERIFIED/CONTESTED view, zero new persisted
  fields, reusing `derive_provenance_label`'s own resolution helpers.
- `scripts/check_contracts.py` (new) and `check_knowledge_base.py::
  check_verified_status_cites_passing_oracle_result` (new): deterministic
  validators, including the depth-not-scope symbol check and the named
  compatibility exemption for twelve pre-existing `status: verified`
  records.
- One real contract: `planning/knowledge/balance-from-spec/` (REQ/3×CL/
  3×EV/DEC/OBS) + `planning/contracts/balance-from-spec/` (contract +
  two real, committed `PASS` results against the live, unmodified
  `~/projects/ledgerkit`).
- 53 new tests across four files, including a genuine `FAIL` against a
  disposable, deliberately mutated scratch copy of Ledgerkit (never the
  real checkout) and every one of the governing prompt's twelve required
  verification scenarios.

## What worked

- Reviewing the real `~/projects/ledgerkit` test suite before inventing
  a fixture (§2's own discipline) paid off immediately: two genuinely
  distinct, already-passing scopes (`test_single_section_rows_and_
  subtotal`, `test_multi_section_correct_values`) were sitting right
  there, needing no new test code in Ledgerkit at all.
- Writing `derive_epistemic_profile` as a thin wrapper reusing
  `derive_provenance_label`'s own id-resolution walk (rather than a
  parallel implementation) kept the new function small and meant the
  six required epistemic test scenarios (plan §10) all passed on the
  first real run once the data model was right.
- Running the real oracle against the real checkout *before* writing
  the final committed knowledge records let the actual digests/hashes
  be baked into the committed `oracle-result.yaml` files honestly,
  rather than hand-fabricated placeholder values later found wrong.

## What didn't work

- The first two attempts to run the oracle against `~/projects/ledgerkit`
  failed for environment reasons unrelated to the design itself: first,
  `codecompass`'s own interpreter had no `pytest` installed (fixed by
  preferring the target repo's own `.venv/bin/python`); then Ledgerkit's
  own `.venv` had no `pytest` either (fixed by `pip install pytest` into
  that local, gitignored venv). Neither was a design defect, but both
  cost real time that a documented "how to run Phase 82's oracle"
  prerequisite note would have saved a future session.
- The negative-control test initially silently passed the *wrong* thing:
  a scratch copy's mutation had no effect because Ledgerkit's own
  editable pip install shadowed it via `sys.path`. This surfaced as a
  confusing, unrelated-looking failure before the real cause was traced
  — filed as `L-101`.

## Lessons learnt

An oracle that re-executes a target project's own test suite against an
independently-mutated scratch copy must explicitly control *both* the
interpreter *and* the import path of the exact tree being executed —
`cwd` alone is not sufficient once the target project has its own
editable package installation anywhere on `sys.path`. This is a general
property of this class of mechanism, not a Ledgerkit quirk (`L-101`).

## Process-improvement feedback

None — this phase ran as a single, lead-authored implementation session
following an already-corrected plan; no agent-handoff friction to
report. The explicit "amendment + implementation-authorisation in one
prompt" pattern (`decisions/0081`) worked cleanly: the plan's own §9
open-decisions section converted directly into a resolved-decisions
record with no re-litigation needed.

## Candidate learnings filed

`L-101` (`planning/learnings/inbox.md`) — oracle execution must pin
interpreter + `PYTHONPATH` to the exact tree under test.

## Where we're going

Phase 83 (Semantic Change Assurance) is next, not yet phase-planned —
it needs this phase's real contract/oracle-result schema to know what a
change could violate and how to report a verification gap. Nothing in
this phase's outcome changes Phase 83-88's planned sequencing or exit
gates; the v2 roadmap's own dependency graph stands as written.

## Time / cost note

One session, same day as the three prior v2 planning sessions. No AI
spend beyond this session's own token usage. The two environment-setup
detours (pytest missing in two different interpreters) were the only
real time cost beyond the design/implementation work itself.
