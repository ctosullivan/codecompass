# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and
`planning/retros/` for history; per `CLAUDE.md` §4, this file is for
session-resumption, not a project history.

## Current phase

**Phase 83 — Semantic Change Assurance — is `done`** (2026-10-28,
`planning/ROADMAP.md`'s own row). Independently audited:
`release-phase-auditor` returned PASS on re-audit against commit
`d076023` (`planning/retros/_audit-phase-83.md`) — an initial FAIL pass
against the implementation commit `b1a8447` found two real gaps (a
missing fixture-driven test named by `decisions/0087` §2; no
`knowledge-curator` triage of two retro-surfaced learnings), both
genuinely fixed, independently re-verified, before the re-audit's PASS.
`scripts/assess_change_impact.py` now exists, built
entirely on Phase 82's unmodified `oracle.py`/`knowledge_
intermediate.py`: it resolves a changed source range to its enclosing
first-party symbol (gated on the target graph's own `source_files.
content_hash` matching the live file — `stale_index` otherwise),
classifies it `no_recorded_relationship`/`relevant_no_coverage_link`/
`behavioural_risk` purely from existing Evidence/Claim citation chains,
and, with `--run-checks`, freshly re-executes each applicable check and
reports `CONFIRMED_REGRESSION`/`INVALID_ASSESSMENT`/`VERIFIED_SCOPE`/
`VERIFICATION_GAP` from that one fresh result alone. Dogfooded for real:
a deliberately introduced OR-union double-counting mutation passes
Ledgerkit's full, unmodified 935-test suite 100% while a new, independent
check fails, and the tool itself reports `CONFIRMED_REGRESSION`. One
real, independently-demonstrated defect found and fixed along the way in
`scripts/check_contracts.py` (`decisions/0088`). **One outstanding,
separately-gated item**: the real Ledgerkit test has not landed in the
real `~/projects/ledgerkit` checkout — a cross-repository action still
requiring its own explicit authorisation, named explicitly, never
silently treated as done. Full detail: `planning/retros/phase-83-
semantic-change-assurance.md`, `decisions/0086`/`0087`/`0088`.

**Phase 82 — Contract and Evidence Foundation — is `done`**, including
two corrective passes that together fixed seven real assurance defects
found by two separate independent post-completion reviews of the shipped
code. The v2 dependency root (`planning/v2-roadmap.md`) is real: one
evidence-linked behavioural contract for `ledgerkit/reports.py::balance_
from_spec` exists end to end — Requirement → Claims → Evidence citing
real source locations → a versioned, multi-check oracle contract → real
`PASS` results against the current, unmodified `~/projects/ledgerkit`
checkout → a real, demonstrated `FAIL` against a deliberately mutated
scratch copy. `decisions/0078`-`0083` govern this phase's design; none of
Phases 84-92 has begun. **The v2 roadmap itself was realigned 2026-10-23**
(`decisions/0084`/`0085`) and **approved as governing, with Phase 83/84
planned, 2026-10-24** (`decisions/0086`/`0087` then corrected Phase 83's
own plan the same day and again on 2026-10-28, immediately before
implementation) — none of this reopened Phase 82's own design.

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

- `decisions/0086` — Phase 83's first corrective planning amendment
  (2026-10-24): replaces `test_input_paths`-based coverage inference with
  a Claim-mediated three-tier relevance/coverage model; fixes an
  impossible aggregate-`FAIL` expectation; adopts `source_files.
  content_hash` for revision consistency; resolves the new obligation's
  contract/Requirement identity by extending the existing contract in
  place, naming the resulting content-hash-invalidation cost explicitly.
- `decisions/0087` — Phase 83's second corrective planning amendment
  (2026-10-28, same session as implementation): fixes a precedence-
  reachability defect in `0086`'s own design (checking aggregate `GAP`
  before `INVALID` made `INVALID_ASSESSMENT` unreachable — classification
  now reads solely the one fresh result's own effective outcome); fixes
  the Ledgerkit scratch-copy demonstration's sequencing. Authorises
  Phase 83 implementation.
- `decisions/0088` — a real, independently-demonstrated defect found
  *during* Phase 83 implementation (not planning): `check_contracts.
  py::check_result_integrity` no longer blocks `--strict` on a historical
  result superseded by a current, different `PASS` for the same
  `check_id`. `src/codecompass/oracle.py` unmodified.

Phase 84's own plan (`planning/phase-84-consolidated-knowledge-api.md`)
is unaffected by any of the above and remains not authorised to
implement.

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
  check was silently skipped entirely. **Since `decisions/0088` (Phase
  83)**: `check_result_integrity`'s own blocking finding is downgraded to
  informational specifically when a different, current `PASS` already
  exists for the same `check_id` — a superseded historical result, found
  by actually extending a real contract for the first time.
- One real contract family: `planning/knowledge/balance-from-spec/` (2
  REQ, 5 CL — `CL-BFS-003` superseded by `CL-BFS-005`, Phase 83 — 3 EV, 2
  DEC, 1 OBS) + `planning/contracts/balance-from-spec/` (3 required
  checks as of Phase 83; 6 immutably-preserved historical result files
  across the two originally-required checks, now informationally
  superseded by 2 fresh ones under the extended contract's own content
  hash; the new third check has no result on file yet — its real test
  does not exist in the live Ledgerkit checkout).
- `scripts/run_balance_from_spec_oracle.py` (maintainer script, like
  `prepare_cleanroom_branch.py`) — re-runs the real oracle against a
  given Ledgerkit checkout, writing one new, permanent result/raw-output
  file pair per execution, never overwriting a prior run's own evidence.
  `--check-id` (repeatable, Phase 83) runs only the named check(s).
- `scripts/assess_change_impact.py` (Phase 83, maintainer script) —
  evidence-backed change-impact assessment: resolves a changed range to
  its enclosing symbol gated on `source_files.content_hash` matching live
  content; classifies `no_recorded_relationship`/`relevant_no_coverage_
  link`/`behavioural_risk` purely from existing Evidence/Claim citation
  chains; with `--run-checks`, freshly re-executes applicable checks and
  reports `CONFIRMED_REGRESSION`/`INVALID_ASSESSMENT`/`VERIFIED_SCOPE`/
  `VERIFICATION_GAP` from the one fresh result's own effective outcome
  alone, never the aggregate state or a historical result. Not a shipped
  `codecompass` command. 27 tests (`tests/test_assess_change_impact.py`).
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

**Phase 83 — Semantic Change Assurance — implemented**, 2026-10-28,
direct user request ("CodeCompass Orchestrator — Amend and Implement
Phase 83"). Full detail: `planning/retros/phase-83-semantic-change-
assurance.md` (actual commands/results/evidence); `decisions/0087`
(second corrective planning pass, fixing a precedence-reachability
defect in `0086`'s own design and authorising implementation) and
`decisions/0088` (one real defect found and fixed in `scripts/check_
contracts.py` during implementation itself). Summary: `scripts/assess_
change_impact.py` built and dogfooded end to end against real Ledgerkit
— a deliberately introduced OR-union double-counting mutation passes
Ledgerkit's full, unmodified 935-test suite 100% while a new,
independent check fails, and the tool itself reports `CONFIRMED_
REGRESSION` with the co-existing `GAP` aggregate shown explicitly, on a
disposable scratch copy (never the real checkout). `oracle-contract.yaml`
extended with one new required check; the resulting content-hash
invalidation of Phase 82's six historical results resolved by two fresh
re-runs. New knowledge records `REQ-BFS-002`/`DEC-BFS-002`/`CL-BFS-004`
(relevance only, no coverage claim yet); `CL-BFS-003` superseded by
`CL-BFS-005`. 1036 passed, 2 skipped — the full repository suite, green
(the +1 is the fixture-driven tamper test added to close the audit's
own named gap). Two retro-surfaced learnings triaged for real by
`knowledge-curator`: `L-104` (retained — the one real instance is
already fixed with its own tests, no second live instance found) and
`L-105` (promoted — a pre-existing regression test already guards it).
**One outstanding, separately-gated item, named explicitly, not silently
treated as done**: the real Ledgerkit test has not landed in the real
`~/projects/ledgerkit` checkout — a cross-repository action requiring
its own explicit authorisation. `planning/ROADMAP.md`'s Phase 83 row now
reads `done`.

**Phase 83 corrective planning amendment**, 2026-10-24 (same day as the
approval below), direct user request ("CodeCompass Orchestrator — Phase
83 Corrective Planning Amendment," planning-only — Phase 83 implementation
remains unauthorised). Independently re-inspected `src/codecompass/
oracle.py`, `graph.py`, `knowledge_intermediate.py::derive_epistemic_
profile`, `scripts/check_contracts.py`, and the real `planning/knowledge/
balance-from-spec/`/`planning/contracts/balance-from-spec/` record set,
rather than trusting the first pass's own prose, and found five concrete
defects (full grounding: `decisions/0086`):

- `test_input_paths` was being used to infer behavioural coverage; it
  only bounds a check's own test-input content digest. Replaced with a
  three-tier model read directly off each Claim's own `supporting_
  evidence` chain: `no_recorded_relationship` (no Evidence cites the
  touched symbol — explicitly *not* read as "safe"), `relevant_no_
  coverage_link` (a citing Evidence exists but no Claim bridges it to a
  check-resolving test-evidence), `behavioural_risk` (a Claim bridges
  both). `EV-BFS-001` already cites `balance_from_spec` this way — no new
  mechanism, an existing one simply put to use correctly.
- The plan expected a check's aggregate state to show `FAIL`;
  `CheckAggregate.state` (`oracle.py`) only ever takes `PASS`/`GAP`/
  `NOT_REQUIRED` — a required check with an observed `FAIL` and no
  `PASS` aggregates to `GAP` (`decisions/0081` §2, confirmed by direct
  reading). Replaced with an explicit four-way precedence —
  CONFIRMED_REGRESSION (any observed `FAIL`, highest precedence, never
  downgraded) / VERIFIED_SCOPE (aggregate `PASS`) / VERIFICATION_GAP
  (aggregate `GAP`) / INVALID_ASSESSMENT — that always shows a `FAIL`
  and its co-existing `GAP` aggregate state together, never one
  presented as if it erased the other.
- Revision consistency for changed-line coordinates had no concrete
  mechanism. `source_files.content_hash` (already populated,
  `sha256`-of-exact-bytes, identical construction to `oracle.
  sha256_file`) is reused: a touched file's live hash must match the
  graph's own recorded hash before its `source_symbols.line` data is
  trusted for symbol resolution; a mismatch reports `stale_index`
  explicitly rather than guessing.
- The new OR-union obligation's contract/Requirement placement was left
  undecided, and the option the first pass implied (a second contract
  file under the same slug) is not supported by `check_contracts.
  py::_iter_contract_slugs` (exactly one `oracle-contract.yaml` per
  slug). Resolved: extend the existing `oracle-contract.yaml`'s `checks:`
  list in place (same `contract_id: REQ-BFS-001`); a new, separate
  `REQ-BFS-002`/`DEC-BFS-002`/`CL-BFS-004` in the *same* knowledge slug
  states the third obligation without editing `REQ-BFS-001`'s own
  statement (Requirements have no supersession mechanism — confirmed by
  direct reading, `supersedes` is Claim/Decision-only) — schema-valid
  because `derive_epistemic_profile` matches via each record's own
  evidence-citation chain, never by requiring its `id` to equal the
  contract's `contract_id` (confirmed by direct reading).
- **Named for the first time**: extending the contract file changes its
  own content hash, which (via `evaluate_result_precedence` rule 1)
  invalidates all six of Phase 82's existing `PASS` results for the two
  pre-existing checks on next evaluation. Resolved as a required,
  bounded, one-time action in the same commit: re-run both pre-existing
  checks once against current Ledgerkit HEAD, producing fresh results
  under the new hash; the original six result files are never deleted or
  edited (Phase 82's own append-only discipline, unchanged) — a required
  before/after aggregate-state test is now part of the plan's own
  acceptance criteria.

Produced `decisions/0086` and rewrote `planning/phase-83-semantic-
change-assurance.md` in place (§0, §2-§13 materially revised; §1/§8's
substance preserved). No change to `src/codecompass/oracle.py`, `graph.
py`, or `knowledge_intermediate.py` — every correction is resolved by how
Phase 83's own (not-yet-written) tooling is specified to use these
modules' existing, unmodified behaviour; no defect was found in Phase
82's own shipped code. `decisions/0078`-`0085` are not edited.

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
- **Phase 83's new oracle check has no real result against the live
  `~/projects/ledgerkit` checkout** (`overlapping-account-patterns-
  no-double-count`, `REQ-BFS-002`/`CL-BFS-004`) — its `check_reference`
  names a test that does not yet exist there; landing it is a separate,
  explicitly authorised, cross-repository action, not yet given. Running
  `scripts/run_balance_from_spec_oracle.py --check-id overlapping-
  account-patterns-no-double-count` against the real checkout today
  would honestly report `INVALID` ("zero collected tests") — expected,
  not a defect, and not attempted/recorded in this phase.
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

**Phase 83 is `done`** (see "Current phase"/"What was just completed"
above) — its one remaining *outstanding, separately-gated* item
(landing the real test in `~/projects/ledgerkit`) was never part of its
own `CLAUDE.md` §5 completion gate — it is named, tracked, and requires
its own future, separate explicit authorisation whenever it is taken up.

**Phase 84 (Consolidated Knowledge API and Query CLI) is phase-planned
and implementation-ready**, approved 2026-10-24
(`planning/phase-84-consolidated-knowledge-api.md`). **Not authorised to
implement without a separate, explicit approval** — confirmed
independent of Phase 83 in both directions (neither phase's own plan
depends on the other). After it: 85 (Self-Curation and
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
