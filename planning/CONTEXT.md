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
design/implementation/corrective-pass history above is unaffected. **A
corrective amendment to that realignment landed the same day**
(`decisions/0085`, "CodeCompass Orchestrator — Corrective Amendment to
v2 Knowledge-Driven Development Roadmap") — see "What was just
completed" below; Phase 82/83 remain unaffected by this correction too.

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
- `decisions/0084` — realigns the v2 roadmap around Knowledge-Driven
  Software Development: inserts four new phases (Consolidated Knowledge
  API, Self-Curation, Knowledge-Placement Review, Documentation
  Compiler) ahead of the former MCP phase, merges MCP with the former
  reconciliation phase, renumbers the former Phases 86-88 to 89-91.
- `decisions/0085` — a same-day corrective amendment to `decisions/0084`:
  formalises Phase 84's logical knowledge model and narrows its CLI
  scope; formalises Phase 86's enforcement classes and placement policy;
  specifies Phase 87's minimum documentation suite and corrects its
  quality baseline; splits the merged Phase 88 back into an MCP-only
  Phase 88 and a reconciliation-only Phase 89 (independently
  deliverable); renumbers the former Phases 89-91 to 90-92; strengthens
  Phase 90's evaluation methodology. Does not reopen Phase 82/83 or
  `decisions/0084`'s own architecture decision (§1: one logical model,
  unchanged physical storage, no new database).

**The corrected v2 roadmap (Phases 82-92) was approved 2026-10-24** as
the governing strategic roadmap, direct user request ("CodeCompass
Orchestrator — Approve v2 Roadmap and Plan Phases 83-84"), subject to no
intervening material change (none found: Phase 82 remains `done`,
unreopened; Phase 83 remains next, unreopened). The same session
produced implementation-ready plans for Phase 83
(`planning/phase-83-semantic-change-assurance.md`) and Phase 84
(`planning/phase-84-consolidated-knowledge-api.md`) — see "What was just
completed" below. Neither is authorised to implement without separate,
explicit approval.

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

**v2 roadmap approval and Phase 83/84 planning**, 2026-10-24, direct user
request ("CodeCompass Orchestrator — Approve v2 Roadmap and Plan Phases
83-84," planning-only — explicit stop condition unchanged: neither phase
is authorised to implement). Re-verified, against live repository state
rather than the prior session's own retelling: Phase 82 still `done`,
unreopened; Phase 83 still next, unreopened; the CLI's `query`/
`knowledge`/`enrich` sub-apps unchanged; `context-graph.db`'s real
`rebuild_deterministic` behaviour (which tables are wholesale deleted and
reinserted on every sync vs. incrementally upserted by natural key);
Ledgerkit's HEAD (`7224bb5`) and its own separate `context-graph.db`
(confirmed CodeCompass's own self-referential graph has no real knowledge
of Ledgerkit at all — any Phase 83 tooling must point explicitly at
Ledgerkit's own graph). Approved the corrected roadmap (Phases 82-92,
`decisions/0084`/`0085`) as governing, subject to this confirmation.
Produced two new implementation-ready plan files:

- `planning/phase-83-semantic-change-assurance.md` — grounds the Phase 83
  dogfood scenario in a real, confirmed blind spot found by direct
  reading of Ledgerkit's own test suite: `reports.py::balance_from_spec`'s
  OR-union section-account matching can double-count a posting matching
  more than one of `section.accounts`'s own patterns, and no existing
  Ledgerkit test (including the one test that does construct multiple
  patterns) asserts the resulting arithmetic, only membership. Resolves
  "structural proximity vs. genuine behavioural risk" via symbol-line-
  range localisation against the target checkout's own graph, cross-
  referenced against existing `EV-*.yaml` `source_ref` citations — no new
  graph table, no call-graph.
- `planning/phase-84-consolidated-knowledge-api.md` — resolves the
  governing prompt's three mandatory architectural considerations by
  generalising already-shipped precedent rather than new infrastructure:
  stable identities reuse `decisions/0038`'s natural-key-table pattern
  (already solved once, for `doc_relation_enrichment`, for exactly the
  wholesale-rebuild-volatility problem); snapshot consistency reuses the
  `meta` table's existing revision fields, `_current_cited_hashes`, and
  `derive_epistemic_profile`'s existing three-way currency distinction;
  primary-authority-vs-derived-index is a pure classification tag over
  existing record kinds. One existing command (`query relations`) is
  migrated onto the new API as proof it is not a redundant wrapper; no
  other command is migrated.

Independent review of both plans against the governing prompt's own
§6 checklist found no material defect requiring correction before
closeout; see this session's own closing report for the point-by-point
record. No implementation of either phase was undertaken; no `src/`
change; `decisions/0078`-`0085` are not edited.

**v2 roadmap corrective amendment**, 2026-10-23 (same day as the
realignment below), direct user request ("CodeCompass Orchestrator —
Corrective Amendment to v2 Knowledge-Driven Development Roadmap," also
planning-only — explicit stop condition unchanged). Re-verified Phase
82 `done` and Phase 83 next/unchanged (no defect found in either, so
neither reopened), and re-confirmed by direct inspection that `query`/
`knowledge`/`enrich` remain three independent `typer.Typer()` sub-apps
with no shared interface. Produced `decisions/0085`, which: (1)
formalises Phase 84's logical knowledge model into nine explicit points
(identity, canonical-vs-derived status, authoritative sources,
provenance, epistemic dimensions, contradictions/gaps, read-only/
mutation separation, missing-knowledge handling, versioned export) and
narrows its CLI scope to incremental, optional migration with a
read-only-only API (no mutation path at all); (2) formalises Phase 86
into a Knowledge Placement Policy table (eight categories → this
project's real artifacts) and three named enforcement classes
(mechanical/behavioural/semantic-editorial, the last always advisory);
(3) specifies Phase 87's complete minimum documentation suite (README,
Getting Started, Concepts, Architecture, Reference, Contributor Guide,
mapped onto existing files), a versioned schema, and withdraws the
"materially less correction than Phase 80" comparison in favour of a
reproducible, matched baseline (or a fresh comparison if the historical
one can't be reconstructed); (4) splits the merged Phase 88 back into
an MCP-only Phase 88 and a reconciliation-only Phase 89, confirming
neither depends on the other; (5) renumbers the former Phases 89-91 to
90-92; (6) strengthens Phase 90's evaluation methodology (Arm A now
included in documentation-quality measurement; the concise-instructions
comparator now mandatory for the principal net-efficiency conclusion,
still not a release dependency; cumulative benefit measured across a
task sequence, not one task). Updated, in the same session: `planning/
v2-roadmap.md` (Phase 84/86/87 sections rewritten in place; old merged
Phase 88 replaced with two new sections 88/89; old 89-91 renumbered
90-92; dependency graph/adoption-levels/federation-review/deferred-scope
sections updated); `planning/ROADMAP.md`'s v2 table (rows 84-92);
`planning/v2-evaluation-methodology.md` (a second dated amendment, title
and cross-references renumbered 89→90); `planning/v2-migration-
assessment.md` and `planning/post-v2-cross-project-overlay-backlog.md`
(phase-number cross-references updated for the split/renumbering, no
substantive posture change); `docs/decisions.md` (new `0085` row);
`CHANGELOG.md` (new `[Unreleased]` entry). An explicit independent
review against the governing prompt's own ten-point closeout checklist
is recorded in `decisions/0085`'s own "Independent review" section,
including three honestly-recorded unresolved uncertainties left to each
named phase's own future planning time. No `planning/phase-83-*.md` or
later plan file was written; no `src/codecompass/` or `context-graph.db`
change was made; `decisions/0078`-`0084` are not edited.

**v2 roadmap realignment**, 2026-10-23, direct user request
("CodeCompass Orchestrator — v2 Strategic Roadmap Realignment," a
planning-only task). Reviewed the actual repository state (Phase
77/79-81B/82 implementation status, `decisions/0078`-`0083`, the
existing `query`/`knowledge`/`enrich` CLI surface, `src/codecompass/`
module list) and confirmed, by direct inspection rather than
assumption: no MCP server, no consolidated knowledge-query API, and no
documentation compiler exist anywhere in this codebase; no
`planning/phase-83-*.md` (or later) plan file exists. Produced
`decisions/0084`, which decided the consolidated-knowledge-API
architecture (one new, typed read/traversal library in front of the
existing, unchanged physical stores, no new database), inserted four new
phases, merged the former MCP and reconciliation phases, and renumbered
the former Phases 86-88 to 89-91. Full detail: `decisions/0084` itself.
**Superseded as "what was just completed" by the corrective amendment
above** — every phase-number and scope reference this realignment
introduced is further corrected there.

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
amendments above.

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

**Phase 83 (Semantic Change Assurance) and Phase 84 (Consolidated
Knowledge API and Query CLI) are both now phase-planned and
implementation-ready**, approved 2026-10-24 alongside the corrected
roadmap itself (see "What was just completed" above) —
`planning/phase-83-semantic-change-assurance.md` and `planning/phase-84-
consolidated-knowledge-api.md`. **Neither may begin implementation
without a separate, explicit approval** — the governing prompt that
produced both plans stopped deliberately short of authorising code.
Phase 83 is sequenced first (not a hard dependency: `planning/v2-
roadmap.md`'s Phase 84 entry and both new plan files confirm Phase 84
does not require Phase 83 either). After both: 85 (Self-Curation and
Knowledge-Quality Validation) → 86 (Knowledge-Placement and Code-Quality
Review, formal policy/enforcement classes) → 87 (Documentation Schema and
Knowledge-Compiled Documentation, minimum suite specified) → 88 (Agent
Integration and MCP, split from the old merged phase) → 89 (Incremental
Knowledge and Documentation Reconciliation, split from the old merged
phase, independent of MCP) → 90 (Comparative Development Trials,
methodology strengthened) → 91 (External Validation and Adoption) → 92
(v2.0 Hardening and Release). None of 85-92 is phase-planned yet; each
gets its own `CLAUDE.md` §1 plan file when it is actually next.

Other open items requiring a human/lead decision, none currently claimed
by a drafted plan or phase number:

- Whether to fund any Post-v2 Cross-Project Semantic Overlay stage
  (`planning/post-v2-cross-project-overlay-backlog.md`) — explicitly not
  authorised by any amendment to date; Stage 1 cannot begin before Phase
  82 is `done` — it now is, but no further authorisation has been given.
  Unaffected by either the realignment or its corrective amendment
  (`decisions/0084` §5, `decisions/0085` §8).
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
