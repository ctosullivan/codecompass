# Phase 83: Semantic Change Assurance — plan

Governing prompt: "CodeCompass Orchestrator — Approve v2 Roadmap and Plan
Phases 83–84" (2026-10-24). Roadmap-depth scope: `planning/v2-roadmap.md`
§"Phase 83" (unchanged by `decisions/0084`/`0085`). This file is the
`CLAUDE.md` §1 implementation-ready plan that section only sketched.
Planning only — no implementation begins from this file without separate,
explicit approval (governing prompt §7).

## 0. Verified current state (read live, not assumed)

Per the governing prompt's own instruction ("do not assume historical
test fixtures or repository state remain valid"), the following was
re-confirmed directly this session, not carried over from Phase 82's own
retro:

- **Phase 82 is `done`, unreopened.** `planning/contracts/balance-from-
  spec/oracle-contract.yaml` (`contract_id: REQ-BFS-001`) has two
  required checks (`single-section-expense-subtotal`,
  `multi-section-income-expense-subtotal`), both against
  `tests/fixtures/filtered.journal`, `tested_paths` spanning
  `ledgerkit/{reports,models,parser}.py` and all four
  `ledgerkit/query/*.py` modules. Six real, immutable `PASS` oracle-result
  files exist across two runs (2026-10-21, 2026-10-22).
- **Ledgerkit's HEAD is `7224bb5` (2026-10-03T00:51:43+08:00)**, unchanged
  since the Phase 82 contract was pinned. `ledgerkit/reports.py` was last
  modified at `dcac520` (2026-09-26), before the graph rebuild below — not
  stale relative to HEAD.
- **Ledgerkit has its own, separate `context-graph.db`** at
  `~/projects/ledgerkit/context-graph.db` — this is the project's own
  self-sync, distinct from (and not to be confused with) CodeCompass's own
  self-referential `context-graph.db` in this repository. CodeCompass's
  own graph has no real knowledge of Ledgerkit at all (confirmed: zero
  `vendors` rows for it; the only two `source_files` path matches are
  CodeCompass's own `planning/reference-projects/ledgerkit/` fixture
  files, not the real project). **Any impact-assessment tooling this
  phase builds must point explicitly at the target repository's own
  graph — `~/projects/ledgerkit/context-graph.db` for this phase's
  scenario — never assume it can read CodeCompass's own.** This corrects
  an ambiguity in `planning/v2-roadmap.md`'s own Phase 83 scoping text
  ("Reused: ... `source_symbols`/`doc_relations_edges` for
  source-to-contract traceability"), which does not name whose graph.
- Ledgerkit's own graph (`meta`: `schema_version=11`,
  `last_deterministic_rebuild_at=2026-10-02T13:44:43Z`,
  `source_index_version=1`) has 42 `source_files` and 322
  `source_symbols` rows, confirmed current against `reports.py`'s own
  last real change. It records `reports.py::balance_from_spec` (line
  600), `_aggregate_posting_amounts` (261), `_matches_pattern` (213), and
  every other top-level declaration in the file, by `(source_file.path,
  name, kind, line)`.
- **No first-party call-graph exists.** `uses_edges` (the only
  first-party-reference edge table in the schema) requires a non-null
  `vendor_id` — it records a first-party file's use of a *vendored
  package* symbol, never one first-party symbol calling another. Ledgerkit
  itself has zero `vendors` rows (no synced dependencies), so `uses_edges`
  is empty there regardless. **There is no existing edge recording that
  `balance_from_spec` calls `_aggregate_posting_amounts`, or that either
  is "related to" the oracle contract, anywhere in the graph schema.**
  This is a real, confirmed gap, not a hypothetical one — `conditional-
  generalisation.md`'s own discipline ("don't add a graph table until
  real use shows a gap") is satisfied: §3 below resolves it without a new
  table.
- Ledgerkit's own test suite is large and already substantially
  behaviour-complete for `balance_from_spec`: `tests/test_reports.py`'s
  `TestBalanceFromSpec` class (33 test methods across it and its sibling
  `TestBalanceFromSpecOuterQueryConvergence`/`TestReportSectionHledger
  RegexValidation` classes) covers single/multi-section aggregation,
  sign inversion, depth truncation, exclude patterns, elided postings,
  empty sections, outer-query convergence, and malformed-pattern
  rejection. A genuine, demonstrable blind spot was found by direct
  reading (not assumed) — see §2.

## 1. Objective / user value

Demonstrate, against real Ledgerkit behaviour, that CodeCompass can:
(a) assess which of a project's own documented behavioural obligations a
proposed/applied change could put at risk, distinguishing *structural*
proximity (same file) from *genuine* behavioural risk (the change touches
a symbol a real Requirement's evidence chain actually depends on);
(b) independently execute the right checks and report PASS/FAIL/GAP/
INVALID without overstating what was actually confirmed; and (c) catch a
real semantic regression that passes Ledgerkit's own full, already
extensive test suite unmodified — the first point in this project's
history where CodeCompass demonstrably catches something a competent
project's own ordinary tests do not.

## 2. The confirmed blind spot (grounds the dogfood scenario, §7)

`ledgerkit/reports.py::balance_from_spec` (line 644-668) includes a
posting when it matches **any** of `section.accounts`'s patterns (OR
union, `_matches_pattern`, infix/case-insensitive per
`compile_hledger_regex`'s own docstring). The function's own docstring
documents this as a deliberate behavioural contract: "Section-level
account patterns are OR-combined within each section." Every real
`ReportSection(accounts=(...))` construction in the codebase and its
test suite — `ledgerkit/models.py:227-228` (the built-in income-statement
spec), `tests/test_dataframe.py`, and every `tests/test_reports.py`
construction — uses either one pattern, or multiple **non-overlapping**
patterns (e.g. `"income:salary"` / `"expenses:housing"`). The **one**
test that constructs multiple patterns in a single section
(`test_section_multiple_accounts_patterns_or_union`, line 810) asserts
only membership (`assertIn`/`assertNotIn`), never a subtotal — so it
cannot detect a posting being counted more than once. **No test anywhere
in Ledgerkit would catch a regression that double-counts a posting
matching two or more of `section.accounts`'s own patterns.** This is a
real, confirmed, previously-undocumented-as-a-check gap — not a
constructed strawman: `expenses:food:groceries` matches both `"food"` and
`"groceries"` under the real infix-search semantics, so
`accounts=("food", "groceries")` already reproduces it with the real
pinned fixture (`tests/fixtures/filtered.journal`'s `£150.00` groceries
posting).

## 3. Architectural changes — impact assessment without a new graph table

A new, bounded capability resolving §0's confirmed gap without adding a
call-graph edge table (disproportionate to this phase; §"Risks" revisits
this if future phases show it's still insufficient):

1. **File-level scope check** (already real): has anything in
   `contract.tested_paths` changed at all? Reuses
   `oracle.compute_tree_digest` unchanged — a changed `tested_subject_
   digest` is the existing, sufficient signal that *something* in scope
   changed; no new mechanism needed for this level.
2. **Symbol-level localisation** (new, no schema change): given a set of
   changed line ranges per file (explicit `path:start-end` input this
   phase, not a `git diff` parser — see §6), resolve each range to the
   enclosing symbol using the target graph's own `source_symbols` table:
   a symbol's span runs from its own recorded `line` to one less than the
   next symbol's `line` in the same file (ordered by `line`) — a pure
   query over an existing column, not a new one.
3. **Claim-level relevance** (reuses an existing, curated convention): a
   touched symbol counts as *behaviourally relevant* to a Requirement only
   if some `EV-*.yaml` under that Requirement's slug cites it via the
   existing `"<path>:<line> def|class <symbol>"` `source_ref` convention
   (the same regex `scripts/check_contracts.py::check_source_ref_symbol_
   depth` already parses and validates) — reused directly, not
   reimplemented. A touched symbol with **no** citing Evidence record is
   reported as **structural proximity only**; a touched symbol **with** a
   citing Evidence record is reported as **genuine behavioural risk**,
   naming the Requirement(s)/contract(s)/check(s) it threads through.
4. **Evidence-backed identification of affected contracts** (deliverable):
   for every genuinely-relevant Requirement found in step 3, identify
   its oracle contract and, when `--run-checks` is passed, execute every
   `required: true` check via the existing `oracle.evaluate_check`/
   `aggregate_contract` pipeline — unmodified, Phase 82's own PASS/FAIL/
   GAP/INVALID semantics preserved exactly (§5 below addresses
   point 5 of the planning requirements explicitly).
5. **Missing/stale/insufficient evidence, explicit** (new): a touched
   file/symbol inside `contract.tested_paths` with **no** check whose own
   `check_reference`/`test_input_paths` actually exercises the specific
   construct that changed (confirmed by requiring the check's own
   `test_input_paths` to include the file whose relevant branch changed —
   a conservative, explicit heuristic, not an attempt at precise static
   coverage analysis) is reported as an explicit **GAP**, never silently
   rounded up to PASS and never silently dropped from the report. A
   target graph whose `meta.last_deterministic_rebuild_at` cannot be
   confirmed current against the live checkout (no re-sync evidence) is
   likewise reported as a **stale-index** finding, not trusted silently.

This reuses exactly: `oracle.py`'s digest/evaluate/aggregate pipeline,
`source_symbols`'s existing natural columns, and `check_contracts.py`'s
existing source-ref-to-symbol regex. It adds no new `context-graph.db`
table, no new persisted field, and no provider-plugin framework.

## 4. Deliverables

1. `scripts/assess_change_impact.py` (maintainer script, like
   `scripts/run_balance_from_spec_oracle.py` — not a shipped
   `codecompass` subcommand; Phase 83 is explicitly allowed to use an ad
   hoc path per `planning/v2-roadmap.md`'s own Phase 83 scoping, not
   blocked on Phase 84's stable API). Inputs: `--repo-root` (the target
   checkout, e.g. `~/projects/ledgerkit`), `--graph-db` (defaults to
   `<repo-root>/context-graph.db`), `--changed path:start-end` (repeatable
   explicit line ranges — see §6 for why this phase does not parse a real
   `git diff`), `--slug` (the `planning/knowledge/<slug>/` directory to
   check relevance against), `--run-checks` (optional: actually executes
   relevant required oracle checks rather than only reporting relevance).
   Produces a machine-readable JSON report (per changed range: file,
   enclosing symbol if any, relevant Requirement ids if any, classification
   — `structural_only` / `behavioural_risk` / `gap` / `stale_index` —
   and, when `--run-checks` was passed, the real PASS/FAIL/GAP/INVALID
   aggregate) and a human-readable text summary of the same.
2. One new behavioural obligation formalised under the existing
   `planning/knowledge/balance-from-spec/` slug: a new Requirement
   (`REQ-BFS-002`, tentative id — see §10 for the one genuinely open
   naming/contract-file decision) stating the OR-union/no-double-count
   obligation identified in §2, with its own Claim/Evidence/Observation
   records following the exact `REQ-BFS-001` precedent (`derived_by`,
   `repository_revision`, `basis: observed_behaviour`, etc.).
3. One new, real Ledgerkit test (proposed name:
   `TestBalanceFromSpec::test_section_accounts_overlapping_patterns_no_
   double_count`, using `accounts=("food", "groceries")` against the
   pinned `filtered.journal` fixture, asserting the `£150.00` groceries
   posting is counted exactly once) and one new required oracle check
   referencing it, closing the gap identified in §2 for real, not only in
   a scratch copy.
4. A written demonstration report (`planning/retros/phase-83-...` per
   `CLAUDE.md` §5, at closeout) walking through §7's four scenarios with
   real tool output, not paraphrased.

## 5. Dependencies and prerequisites

Phase 82, complete and approved `done` (confirmed §0). No dependency on
Phase 84 (the consolidated knowledge API) — this phase queries
`source_symbols`/`oracle.py` directly, exactly as `planning/v2-
roadmap.md`'s own Phase 83 entry already specifies, confirmed still
correct by this plan's own architecture (§3).

## 6. Explicit exclusions / non-goals

- **No new `context-graph.db` table or schema change** (§3's whole point).
- **No first-party call-graph / inter-procedural static analysis.** Symbol
  localisation is line-range-to-nearest-declaration only; it does not
  attempt to know that `balance_from_spec` *calls*
  `_aggregate_posting_amounts` — only that both are declared in a
  `tested_paths` file. If a future phase's real use shows this coarseness
  insufficient (e.g. a change several call-frames deep that this
  heuristic misses), that is this phase's own named residual risk (§9),
  not pre-solved here.
- **No `git diff` parsing.** Changed-line input is explicit
  (`--changed path:start-end`) this phase; auto-deriving it from a real
  diff is a natural but separate follow-on, deliberately deferred to keep
  this phase bounded (`decisions/0081`'s own "avoid designing a
  general-purpose ... framework" discipline, applied here to diff
  ingestion).
- **No MCP exposure, no model-routing/scheduling concept** (roadmap's own
  exclusions, unchanged).
- **No `codecompass` CLI command.** `assess_change_impact.py` stays a
  maintainer script in this phase, matching `run_balance_from_spec_
  oracle.py`'s own precedent; promoting it to a shipped subcommand (and
  to Phase 84's API) is that phase's own, later decision (§"Cross-phase
  compatibility" below).
- **Not a general-purpose coverage-gap finder.** §3 point 5's GAP
  detection is scoped to the one slug/contract under test, not a
  whole-project audit.

## 7. Tests and independently reproducible negative controls

All four, run against **disposable scratch copies** of
`~/projects/ledgerkit` (Phase 82's own established technique,
`run_pytest_check`'s `PYTHONPATH`-pinning already makes this safe) —
**never the real checkout** for the regression/negative-control runs; the
one change that *is* proposed for the real checkout is the new test in
deliverable 4.3 above, run first in a scratch copy to prove it behaves as
intended before being proposed for real inclusion.

1. **The regression** (positive detection). Apply the double-counting
   patch to `balance_from_spec`'s OR-union loop in a scratch copy. Run
   Ledgerkit's full existing `pytest tests/` — expect **100% pass**,
   demonstrating the "ordinary feature-test baseline does not detect it"
   claim directly, not by assertion. Run the new oracle check (§4.3)
   against the same scratch copy — expect **FAIL**. Run
   `assess_change_impact.py --changed ledgerkit/reports.py:644-668
   --run-checks` — expect classification `behavioural_risk` (the touched
   lines fall inside `balance_from_spec`, cited by `EV-BFS-004`) and the
   new check's real FAIL surfaced in the aggregate.
2. **Correct-change negative control** (no false regression). In a
   second scratch copy, make an unrelated, genuinely safe change inside
   `reports.py`'s `tested_paths` scope — e.g. a clarifying comment inside
   `register()` (not `balance_from_spec`). Run the new oracle check —
   expect **PASS** (unchanged behaviour). Run `assess_change_impact.py`
   with the comment's line range — expect classification
   `structural_only` (same file, but the touched lines fall inside
   `register`, which no `EV-BFS-*` record cites), explicitly distinct from
   `behavioural_risk`.
3. **Incomplete-evidence scenario** (explicit GAP, not false assurance).
   Pick a real, in-scope change to `ledgerkit/query/regex.py` (a
   `tested_paths` member) touching a validation branch that neither
   existing required check's `test_input_paths` exercises. Run
   `assess_change_impact.py` against it — expect classification `gap`,
   with the report naming exactly which obligation has no covering check,
   not a silent PASS and not an omission.
4. **Independent evaluation.** A fourth run compares
   `assess_change_impact.py`'s own report against the real pytest/oracle
   output it reports on, by direct inspection (mirroring `context-
   evaluator`'s and `v2-evaluation-methodology.md`'s own established
   "never trust the tool's self-report alone" discipline) — confirming
   the FAIL in scenario 1 is a real pytest failure, not merely the
   script's own claim of one.

## 8. Dogfood scenario

Scenario 1 above, run end to end against the real, genuine Ledgerkit
checkout's own fixture and test conventions (not a synthetic toy
project) — the deliberately-introduced regression, caught by a
newly-identified, evidence-backed obligation that Ledgerkit's own
(already extensive) test suite does not cover, is the dogfood scenario
itself, satisfying the governing prompt's own requirement directly.

## 9. Acceptance criteria / exit gate

- Scenario 1 (§7.1) demonstrates a real FAIL from the new check against a
  real scratch-copy regression, while Ledgerkit's full real test suite
  stays green on the same scratch copy — both captured verbatim in the
  demonstration report (§4.4), not paraphrased.
- Scenario 2 (§7.2) demonstrates the same new check does **not**
  false-positive on an unrelated, correct change, and that
  `assess_change_impact.py` classifies it `structural_only`, not
  `behavioural_risk`.
- Scenario 3 (§7.3) demonstrates an explicit `gap` classification,
  distinguishable in the tool's own machine-readable output from both
  `PASS` and `FAIL`.
- The real Ledgerkit test proposed in deliverable 4.3 is reviewed and, if
  accepted, lands in the real `~/projects/ledgerkit` checkout (a
  cross-repository action — see §10) as a genuine, durable closing of the
  gap, not only a scratch-copy demonstration.
- No existing Phase 82 safeguard regresses: immutable per-run evidence,
  current-vs-historical distinction, non-vacuous PASS, fail-closed
  INVALID handling — all exercised unchanged through `oracle.evaluate_
  check`/`aggregate_contract`, confirmed by re-running Phase 82's own
  existing test suite (`tests/test_oracle.py`, `tests/test_check_
  contracts.py`) unmodified and green after this phase's changes.

## 10. Risks, alternatives, and unresolved decisions

**Risks.**
- The coarse "same file, cited-symbol-or-not" heuristic (§3.3) will
  under-detect a regression several call-frames away from any cited
  symbol, and over-detect when a cited symbol's own line range is large
  (e.g. a 90-line function) and the real change is in an unrelated
  branch within it. Named explicitly, not hidden — a real limitation of
  staying proportional (§6), revisited only if a later phase's real use
  shows it matters.
- Proposing a change to the real `~/projects/ledgerkit` checkout (a
  separate project, also the user's own) is a cross-repository action.
  Per this session's own operating discipline around hard-to-reverse/
  shared-system actions, this plan treats landing the new test in the
  real checkout as requiring its own explicit go-ahead at implementation
  time, separate from this plan's own approval — not assumed here.

**Alternatives considered.**
- *A full first-party call-graph table.* Rejected for this phase: a
  disproportionate new persisted capability for one demonstration,
  contradicting `conditional-generalisation.md`'s own discipline; the
  line-range/cited-symbol heuristic resolves the confirmed gap (§0)
  without it.
- *Reusing CodeCompass's own `context-graph.db`.* Rejected — directly
  refuted by §0's own direct inspection (it has no real Ledgerkit data).
- *A synthetic, invented regression scenario* rather than the real
  OR-union gap. Rejected — the governing prompt explicitly requires
  inspecting the live checkout before committing to a scenario; the
  OR-union gap is real, confirmed, and already present, not manufactured.

**Unresolved decisions (recorded, not invented).**
- Whether the new check belongs in the existing `planning/contracts/
  balance-from-spec/oracle-contract.yaml` (requiring `REQ-BFS-001`'s own
  `statement` to be edited to cover the third scope — no precedent yet
  for editing a `status: implemented` Requirement's statement in place)
  or a second contract file under the same slug (no precedent yet for
  more than one oracle-contract file per slug directory) — left to Phase
  83's own first implementation commit, with either choice fully
  consistent with `check_contracts.py`'s existing validators.
- Whether `assess_change_impact.py` should eventually become a Phase 84
  API consumer (reading contract/evidence data through the new interface
  instead of `oracle.py`/`knowledge_intermediate.py` directly) once Phase
  84 exists — recorded as the one genuine cross-phase integration point
  (see the coordination note in the closeout report), not committed here
  since Phase 83 must not depend on Phase 84 (§5).

## 11. Verification (how this phase is confirmed done)

`.venv/bin/python -m pytest` run against the real `~/projects/ledgerkit`
checkout's own `.venv` for the regression/negative-control/GAP scenarios
(§7, each independently reproducible from this plan's own exact
instructions); `scripts/assess_change_impact.py`'s own new tests
(`tests/test_assess_change_impact.py`, fixture-based, no live Ledgerkit
network/process dependency for the unit-level tests, mirroring `check_
contracts.py`'s own test style); Phase 82's existing test suite re-run
green; `docs/`/`architecture/` updated for whatever `assess_change_
impact.py` adds (a new maintainer-script entry, matching how `run_
balance_from_spec_oracle.py` is documented); `CHANGELOG.md` entry;
`planning/ROADMAP.md`/`planning/CONTEXT.md` updated; a `planning/retros/
phase-83-semantic-change-assurance.md` retro; `release-phase-auditor`
PASS against this exact plan's own verification steps before
`planning/ROADMAP.md` marks Phase 83 `done` (`CLAUDE.md` §5).
