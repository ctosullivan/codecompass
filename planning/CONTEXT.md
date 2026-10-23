# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and
`planning/retros/` for history; per `CLAUDE.md` §4, this file is for
session-resumption, not a project history.

## Current phase

**Phase 82 — Contract and Evidence Foundation — is `done`, including two
corrective passes that together fixed seven real assurance defects found
by two separate independent post-completion reviews of the shipped
code.** The v2 dependency root (`planning/v2-roadmap.md`) is now real:
one evidence-linked behavioural contract for
`ledgerkit/reports.py::balance_from_spec` exists end to end — Requirement
→ Claims → Evidence citing real source locations → a versioned,
multi-check oracle contract → real `PASS` results against the current,
unmodified `~/projects/ledgerkit` checkout → a real, demonstrated `FAIL`
against a deliberately mutated scratch copy — now with current-vs-
historical verification genuinely distinguished, execution-failure
classification backed by pytest's own structured report (including
correctly rejecting an all-skipped execution), immutable per-run
evidence, strict oracle-schema type/value enforcement (type validated
before enum membership, closing an uncaught-`TypeError` path), and both
strict validators failing closed when their own required verification
modules cannot be imported. `decisions/0078`-`0083` govern this phase's
design; none of Phases 83-91 has begun. **The v2 roadmap itself was
realigned 2026-10-23** (`decisions/0084`, "CodeCompass Orchestrator — v2
Strategic Roadmap Realignment," around Knowledge-Driven Software
Development) — see "What was just completed" below; Phase 82's own
design/implementation/corrective-pass history above is unaffected.

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
- `decisions/0083` — a second, further corrective pass against the
  already-corrected code, triggered by a separate independent review:
  an all-skipped pytest execution could classify `PASS` (pytest's own
  junit-xml counts a skip toward its `tests` total); both strict
  validators reported a broken required oracle/knowledge-module import as
  merely informational, letting `--strict` report success while every
  oracle check was silently skipped; `parse_oracle_result` checked
  `outcome`'s enum membership against a `set` before confirming its type,
  so an unhashable malformed value raised an uncaught `TypeError`. Does
  not reopen `decisions/0080`/`0081`/`0082`'s own design.

**What exists now, concretely**:

- `src/codecompass/oracle.py` (shipped, corrected twice): `OracleContract`/
  `OracleCheck`/`OracleResult` schema parsing (real YAML, `pyyaml`, now
  with strict type/value enforcement — a real boolean required for
  `required`, a supported `schema_version`/`execution_provider` checked
  at parse time, malformed YAML caught as a controlled error, `outcome`'s
  type validated before its enum membership so an unhashable malformed
  value can never raise an uncaught `TypeError`, every optional field
  type-checked), Phase 81B-style content digesting (`compute_tree_digest`,
  reusing `_canonical_digest_of_hashes`'s construction) scoped to each
  contract's own explicit `tested_paths`/`test_input_paths`, one
  `pytest` execution provider (pins the target repo's own interpreter
  and `PYTHONPATH` — confirmed necessary this phase, see `L-101`;
  classifies outcomes from pytest's own structured `--junit-xml` report,
  not a bare exit code — see `L-102`; rejects an all-skipped execution as
  `INVALID`, requiring at least one genuinely executed test before
  `PASS`; a subprocess-launch failure is caught and classified `INVALID`
  rather than propagating uncaught), immutable per-run
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
  into `derive_epistemic_profile` instead of a hardcoded `None`. Both
  also now fail closed when their own required `codecompass.oracle`/
  `knowledge_intermediate` import fails outright — previously
  informational, letting `--strict` report success while every oracle
  check was silently skipped entirely.
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
- 77 new tests total across the original implementation and both
  corrective passes (`tests/test_oracle.py`, `tests/test_check_contracts.py`,
  plus additions to `tests/test_knowledge_intermediate.py` and
  `tests/test_check_knowledge_base.py`), covering every one of the
  governing prompt's original twelve required verification scenarios,
  the first corrective pass's own four defect-specific negative controls,
  and the final corrective pass's own three (all-skipped execution,
  both strict validators' import fail-closed behaviour, outcome-type-
  before-membership plus optional-field type validation and a
  subprocess-launch failure).

`decisions/0062`'s Priority A-F framework remains superseded as the
primary strategic framework by `decisions/0078`. Phase 81B (clean-room
redocumentation, `done`) and Phase 81 (the intermediate knowledge layer
Phase 82 directly extends, `done`) are reused-foundation background,
unmodified by Phase 82 — full detail in `planning/ROADMAP.md`'s own rows
and each phase's retro.

## What was just completed

**v2 roadmap realignment**, 2026-10-23, direct user request
("CodeCompass Orchestrator — v2 Strategic Roadmap Realignment," a
planning-only task — explicit stop condition: "do not proceed to
implementation without explicit approval"). Reviewed the actual
repository state (Phase 77/79-81B/82 implementation status,
`decisions/0078`-`0083`, the existing `query`/`knowledge`/`enrich` CLI
surface, `src/codecompass/` module list) and confirmed, by direct
inspection rather than assumption: no MCP server, no consolidated
knowledge-query API, and no documentation compiler exist anywhere in
this codebase; no `planning/phase-83-*.md` (or later) plan file exists.
Produced `decisions/0084`, which: (1) decides the consolidated-
knowledge-API architecture — one new, typed read/traversal library in
front of the *existing, unchanged* physical stores (`context-graph.db`,
`planning/knowledge/`, `planning/contracts/`), explicitly declining a
new database or external store for v2; (2) inserts four new phases
(Consolidated Knowledge API, Self-Curation, Knowledge-Placement Review,
Documentation Compiler) between Phase 83 and the former MCP phase; (3)
merges the former Phase 84 (MCP) and former Phase 85 (persistent
knowledge/reconciliation) into one phase, extended to also reconcile
compiled documentation; (4) renumbers the former Phases 86-88
(Comparative Trials / External Validation / v2.0 Release) to 89-91,
content unchanged; (5) confirms Phase 82 and Phase 83 are themselves
unchanged, and that `decisions/0079`'s post-v2 cross-project overlay
track is unaffected. Updated, in the same session: `planning/
v2-roadmap.md` (substantially rewritten — new Phase 84-88 roadmap-depth
sections, renumbered 89-91, updated dependency graph/adoption-levels/
federation-review/deferred-scope sections); `planning/ROADMAP.md`'s v2
table (new rows 84-91); `planning/v2-evaluation-methodology.md` (dated
amendment: a documentation-quality metric and a concise-repository-
instructions comparison baseline, per the governing prompt's own §9);
`planning/v2-migration-assessment.md` (phase-number cross-references
corrected throughout; substantive additive-only posture unchanged,
if anything strengthened); `planning/post-v2-cross-project-overlay-
backlog.md` (two phase-number cross-references updated, no stage/
risk/exit-gate changed). No `planning/phase-83-*.md` or later plan file
was written — per `CLAUDE.md` §1, each of Phases 83-91 still requires
its own plan file, scoped against evidence current when it is actually
next, before any implementation begins. No `src/codecompass/` or
`context-graph.db` change was made. This is a single-session planning
deliverable with no independent audit dispatched (the governing prompt's
own deliverable list is planning artefacts, not implementation subject
to `CLAUDE.md` §5's DoD gate) — a human/lead decision on whether to fund
Phase 83 (or any later phase) next remains open, named in "Next concrete
step" below.

**Phase 82 final corrective pass** (prior session, 2026-10-22, six
commits `65840ca`/`04c0ed2`/`97ef607`/`4407b38`/`9e828c1`/`33b1e39`):
fixed three further assurance weaknesses (all-skipped pytest execution
misclassified `PASS`; both strict validators failing open on a broken
required import; `parse_oracle_result` checking enum membership before
type, raising an uncaught `TypeError` on malformed `outcome`), each with
real negative controls, independently audited **PASS**. Full detail
preserved in `planning/retros/phase-82-final-corrective-pass.md` and
`decisions/0083` — summarised here only to the extent needed for
session resumption; superseded as "what was just completed" by the
realignment above.

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
- One non-blocking residual remains from the first Phase 82 corrective
  pass's own independent audit (the other — an all-skipped pytest run
  classifying `PASS` — was fixed by the final corrective pass,
  `decisions/0083`): `derive_epistemic_profile` reports a required check
  whose cited result's digest mismatches an *existing-but-wrong* decoy
  directory via `known_gap_scopes` rather than the more precise
  `unconfirmed_scopes` (the fail-closed `status: verified` rejection
  still fires correctly either way — a labelling imprecision, not a
  safety gap). A candidate for whoever next touches `oracle.py`'s
  execution-provider logic (Phase 83); not named by either corrective
  pass's own governing prompt, so not reopened or touched by either.
- `L-103` (retained, `planning/learnings/inbox.md`): a Python `in`/
  `not in`-against-a-`set` membership check is only safe once the checked
  value's type is confirmed first (`hash()` runs before the comparison
  and raises on an unhashable value). No second live instance exists in
  the current codebase (confirmed by a repo-wide `knowledge-curator`
  grep) — worth re-checking the next time a new closed-enum/status check
  is added against externally-sourced or YAML-parsed input.

## Next concrete step

**Phase 83 (Semantic Change Assurance) is next, not yet phase-planned —
unchanged by the 2026-10-23 realignment.** Per `CLAUDE.md` §1, writing
`planning/phase-83-*.md` is the required next step before any Phase 83
implementation begins — scoped against evidence current at that time
(`planning/v2-roadmap.md` records only roadmap-depth sequencing for it:
detect a deliberately-introduced Ledgerkit semantic regression Phase
82's own contract should catch, without falsely claiming complete
verification elsewhere in the same report; needs Phase 82's real
contract/oracle-result schema to know what a change could violate and
how to report a gap). After Phase 83, the realigned sequence
(`decisions/0084`) is: 84 (Consolidated Knowledge API and Query CLI) →
85 (Self-Curation and Knowledge-Quality Validation) → 86 (Knowledge-
Placement and Code-Quality Review) → 87 (Documentation Schema and
Knowledge-Compiled Documentation) → 88 (Agent Integration, MCP, and
Incremental Reconciliation — merges the former MCP and reconciliation
phases) → 89 (Comparative Development Trials) → 90 (External Validation
and Adoption) → 91 (v2.0 Hardening and Release). None of 84-91 is
phase-planned; each gets its own `CLAUDE.md` §1 plan file when it is
actually next.

Other open items requiring a human/lead decision, none currently claimed
by a drafted plan or phase number:

- Whether to fund any Post-v2 Cross-Project Semantic Overlay stage
  (`planning/post-v2-cross-project-overlay-backlog.md`) — explicitly not
  authorised by any amendment to date; Stage 1 cannot begin before Phase
  82 is `done` — it now is, but no further authorisation has been given.
  Unaffected by the 2026-10-23 realignment (`decisions/0084` §5).
- Priority A's own narrowly-scoped follow-up trial, sketched (not
  started) in `planning/phase-78-amendment-followup-plan.md` — now
  superseded in strategic priority by Phase 83/85's own, sharper
  change-assurance/self-curation framing (`decisions/0078`,
  `decisions/0084`), but not deleted; still available if a human
  decision prefers it first.
- The "Strict mechanical isolation for documentation-reconstruction
  stages" backlog item — `resolved` (Phase 81B Amendment 4), no further
  action pending. Phase 87's documentation compiler reuses this same
  isolation mechanism rather than reopening it.
- `L-101` (promoted, `planning/learnings/promoted.md`): an oracle
  execution mechanism must pin the interpreter and `PYTHONPATH` of the
  exact tree it executes, or a sibling checkout's own editable package
  install silently shadows a scratch mutation — already landed in
  `oracle.py`, recorded for any future execution-provider work (Phase
  83).
- `L-102` (promoted, `planning/learnings/promoted.md`): classify a
  subprocess oracle's outcome from its own structured report (e.g.
  pytest's `--junit-xml`), never from a bare exit code alone — already
  landed in `oracle.py::_classify_pytest_junit`, recorded for any future
  second execution provider (Phase 83).
- `L-103` (retained, `planning/learnings/inbox.md`): validate a value's
  type before checking its membership against a closed `set` — no
  current second instance to fix, but worth re-checking the next time a
  new closed-enum/status check is added against raw/YAML-parsed input
  (Phase 83's own future execution-provider work, or Phase 84's new
  knowledge-API query parsing, are the most likely triggers).
