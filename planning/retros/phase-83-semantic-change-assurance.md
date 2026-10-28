# Phase 83 retro — Semantic Change Assurance

- **Date:** 2026-10-28
- **Commit(s):** `597f819` (second corrective plan amendment, decisions/0087 — landed the prior session), plus this session's implementation commit(s) (see `git log`, immediately preceding/following this file's own commit)
- **Agents used:** none dispatched mid-implementation; `release-phase-auditor` and a documentation-drift review run at closeout per `CLAUDE.md` §5 (see "Where we're going" / the closeout report for their verdicts)

## Where we are

v2's dependency root (`planning/v2-roadmap.md`) now has its first phase
built directly on Phase 82's oracle/evidence foundation, not merely
planned against it. Phase 82 shipped `oracle.py`'s contract/result
schema and PASS/FAIL/GAP/INVALID precedence; Phase 83 is the first real
*consumer* of that machinery beyond Phase 82's own two pinned checks —
extending the same `balance-from-spec` contract with a third, and
building the first change-impact-assessment tool on top of it, without
touching `oracle.py`, `graph.py`, or `knowledge_intermediate.py`
themselves. Two corrective planning passes preceded implementation
(`decisions/0086`, `0087`) — both found real design defects by direct
source reading before any code existed, not after.

## Goal

Demonstrate, against real Ledgerkit behaviour, that CodeCompass can
assess which documented behavioural obligations a change could put at
risk (distinguishing established relevance from the absence of a
recorded relationship, never read as proof of safety), independently
re-execute the right checks, and catch a real semantic regression that
passes Ledgerkit's own full, unmodified test suite.

## Scope delivered vs planned

Everything in `planning/phase-83-semantic-change-assurance.md` shipped,
plus one real, independently-demonstrated defect fix the plan did not
anticipate:

- `scripts/assess_change_impact.py` — built exactly to the plan's §3-§7
  design (three-tier relevance/coverage classification; revision
  consistency via `source_files.content_hash`; the corrected four-way
  assurance precedence from `decisions/0087`).
- `planning/contracts/balance-from-spec/oracle-contract.yaml` extended
  with the new `overlapping-account-patterns-no-double-count` check.
- Two fresh `OracleResult`s for the two *pre-existing* checks
  (`single-section-expense-subtotal--20261028T075132259723Z-bfd29ce3`,
  `multi-section-income-expense-subtotal--20261028T075133080206Z-c9165dee`),
  both real `PASS` against the current, unmodified
  `~/projects/ledgerkit` (HEAD `7224bb5c113cd3aad7e86e994365703cd0070154`).
- New knowledge records `REQ-BFS-002`, `DEC-BFS-002`, `CL-BFS-004` —
  `CL-BFS-004` deliberately cites only `EV-BFS-001` (relevance); no
  `EV-BFS-004` was authored, since no real passing result against the
  live checkout exists yet for the new check (its `check_reference`
  names a test that does not exist there — a separately authorised,
  outstanding action, never silently treated as done).
- `CL-BFS-003` (status `verified`, statement "satisfies *every* required
  check in its own oracle contract") correctly became un-satisfiable the
  moment the contract gained a third required check with no passing
  result yet — `scripts/check_knowledge_base.py --strict` caught this
  immediately, as designed. Superseded by `CL-BFS-005`, an honest,
  narrower claim about the two checks that do currently pass.
- `tests/test_assess_change_impact.py` — 27 new tests, independent of
  `~/projects/ledgerkit` except one marked group (the fake "target repo"
  pattern from `tests/test_oracle.py`, reused).
- **Not planned, found during implementation**: `scripts/check_
  contracts.py::check_result_integrity` unconditionally blocked `--strict`
  on any historical result whose own recorded hash no longer matched
  current reality — including one superseded by a different, current
  `PASS` for the same `check_id`. Extending the real contract for the
  first time since Phase 82 shipped exposed this immediately (confirmed
  by actually doing it, not by inspection alone): all six pre-existing
  result files blocked `--strict` with no available remedy short of
  deleting historical evidence, which `decisions/0081`/`0082` both
  forbid. Fixed (`decisions/0088`): downgraded to informational
  specifically when a current `PASS` for the same `check_id` exists
  elsewhere; stays blocking, unchanged, when it doesn't. Two new tests
  lock in both directions.
- `scripts/run_balance_from_spec_oracle.py` gained one small, bounded
  addition: `--check-id` (repeatable), so the two pre-existing checks
  could be re-run without also attempting the new one (which has no real
  test to exercise yet).
- `tests/test_oracle.py`'s own `test_real_contract_passes_both_checks_
  against_unmodified_checkout` hardcoded `len(contract.checks) == 2` —
  updated to assert the two originally-required checks still pass for
  real, and separately asserts the new third check's own honest,
  current `INVALID` state (never silently hidden or assumed `PASS`).

No scope was dropped. The one deliberately deferred item — landing the
real Ledgerkit test — remains exactly as the plan always said: a
separate, explicitly authorised, cross-repository action, reported here
as outstanding, never silently treated as satisfied.

## What was achieved

The dogfood scenario ran for real, not as a thought experiment:

1. **Baseline pinned**: Ledgerkit HEAD `7224bb5c113cd3aad7e86e994365703cd0070154`;
   `sha256(reports.py)` = `97e22d5895ee5d1bd8b52df1def6517139fdd2a4b3b83ea178302ba212919930`;
   `sha256(tests/test_reports.py)` = `44d803f243f502fcb9891ac4820f831df868606f7c378cc16d565786a1e46007`.
2. **Mutation applied** to a disposable scratch copy only (never the real
   checkout): `section.accounts`'s OR-union inclusion gate (`reports.py`
   line 663) changed from a single boolean `any(...)` append to counting
   matching patterns and appending once per match — the exact
   double-counting defect the governing prompt named.
3. **Original, unmodified Ledgerkit suite run against the mutation,
   before the new test file existed anywhere in that tree**: `935
   passed, 1 warning, 14 subtests passed in 4.97s` — **100% pass**,
   confirming the claimed blind spot by execution, not assertion.
4. **New check added** (`tests/test_phase83_overlap_regression.py`, a
   new file, never merged into `test_reports.py`) — run directly: `1
   failed` against the mutation (`Decimal('300.00') != Decimal('150.00')`
   — the posting counted twice); `1 passed` against a second, clean
   scratch copy of the same test — both directions demonstrated.
5. **`assess_change_impact.py` itself**, run against the mutated scratch
   copy (its own freshly `codecompass sync`'d graph, confirmed via
   matching `content_hash`), with a disposable scratch knowledge-root
   bridging the new check (never touching the real canonical knowledge
   base): classified `ledgerkit/reports.py:659-666` as `behavioural_risk`,
   freshly re-executed the applicable check, and reported
   `CONFIRMED_REGRESSION (fresh=FAIL, aggregate=GAP, observed=['FAIL',
   'FAIL'])` — both facts shown side by side, exactly as `decisions/
   0086`/`0087` specify.
6. **Negative control**, real: a harmless comment inside `register()` in
   a third scratch copy — full suite `936 passed` (one more than above,
   since this copy also carries the new test file, which also passes);
   new check `1 passed`; `assess_change_impact.py` classified the touched
   range `no_recorded_relationship` — not `behavioural_risk`, no false
   positive.
7. **`no_recorded_relationship`, real** (`ledgerkit/query/regex.py`,
   `validate_hledger_regex`) and **`stale_index`, real** (an unsynced
   edit after the graph was last rebuilt) and **a missing/unreadable
   graph database** (found to crash uncaught — fixed to fail closed with
   an explicit `cannot_map` finding, a real defect found by testing the
   tool against its own edge case, not merely asserting it handles it).
8. **Content-hash-cost resolution, real**: extending the contract
   produced exactly the predicted `contract-result-integrity-mismatch`
   blocking findings against all six historical results; re-running the
   two pre-existing checks produced two fresh `PASS` results; `check_
   contracts.py --strict` exits `0` again, with the six old results now
   informational (superseded), never deleted.

Both `scripts/check_contracts.py --strict` and `scripts/check_knowledge_
base.py --strict` exit `0` against the final state (24 pre-existing
informational knowledge-base findings, unchanged from before this phase;
7 informational contract findings, all expected and named).

## What worked

- **Reading the real `check_contracts.py`/`knowledge_intermediate.py`
  source before designing the classification mechanism** (rather than
  re-deriving from the plan's own prose) found the exact existing
  Evidence/Claim bridge the plan's corrective passes had already
  identified in principle — implementing it was then a direct, almost
  mechanical translation, and it worked correctly on the first real run
  against live Ledgerkit data.
- **Running the tool against the real, unmutated checkout first**,
  before any scratch-copy work, caught the `knowledge_root` parameter-
  threading bug (test_ref resolution used the hardcoded `ROOT` instead
  of the passed `knowledge_root`) immediately and cheaply — it would
  otherwise have silently produced a wrong `relevant_no_coverage_link`
  classification in the full demonstration, discovered far later.
- **Extending a real, already-shipped contract for the first time**
  (rather than only reasoning about it) surfaced the `check_result_
  integrity` defect that no amount of design review would have found,
  because the scenario (two generations of results for one check_id,
  one stale) had simply never existed in this repository before.
- **The fake-target-repo pattern already established in `tests/
  test_oracle.py`** (a `tmp_path` with a tiny implementation + test file,
  no Ledgerkit dependency) ported directly to `tests/test_assess_
  change_impact.py`'s own assurance-precedence tests, keeping 27 of the
  new tests fast and Ledgerkit-independent.

## What didn't work

- My own first draft of the new regression test asserted a `subtotal`
  value (`150.00`) that was simply wrong — I hadn't accounted for `"food"`
  also substring-matching `expenses:food:coffee` (a second, unrelated
  posting), which legitimately contributes to the same section's
  subtotal. Caught immediately by actually running the test against
  correct code and getting `159.00` back, not by review. Fixed by
  asserting the specific `rows["expenses:food:groceries"]` value instead
  of the section's own subtotal — a more precisely targeted assertion
  for this exact defect, and the right fix in retrospect, not a
  workaround.
- The first `assess_change_impact.py --run-checks` run against the
  mutated scratch copy, using only the *real* canonical knowledge base
  (no `EV-BFS-004`), correctly but unhelpfully reported `relevant_no_
  coverage_link` for the new obligation and only re-ran the two
  pre-existing (and genuinely unaffected) checks — a reminder that the
  tool's own end-to-end `CONFIRMED_REGRESSION` demonstration required
  building a second, disposable scratch knowledge-root with its own
  bridging evidence, not just a scratch Ledgerkit copy. This was
  anticipated by the plan in spirit (`--knowledge-root` existing at all)
  but not spelled out as a concrete step — worth naming explicitly for
  any future phase doing a similar demonstration.

## Lessons learnt

- A contract/evidence system with a "historical facts are never deleted"
  discipline needs every validator that consumes `evaluate_result_
  precedence` to independently account for *supersession*, not just the
  schema design that introduced the discipline — `decisions/0081`
  established the aggregation-layer behaviour correctly; `check_
  contracts.py`'s own separate integrity check needed its own, later fix
  for the same principle. A discipline stated once in an ADR does not
  automatically propagate to every later consumer of the mechanism it
  describes.
- When a tool accepts a "knowledge root" or similar distinct-from-target
  path as a first-class input specifically to support disposable/
  alternate knowledge sources, every internal path resolution must
  thread that parameter through explicitly — a single hardcoded fallback
  to the tool's own install location silently defeats the whole feature,
  and will not be caught by any test that happens to use the default.

## Process-improvement feedback

None of substance. The two-pass corrective planning (`decisions/0086`
then `0087`) before implementation began meant the actual build phase
hit no architectural surprises — only the one validator defect, which
is exactly the kind of thing planning review cannot find (it requires
doing the thing for real).

## Candidate learnings filed

Filed to `planning/learnings/inbox.md`: `L-104` (the `check_result_
integrity` supersession gap — assessed by `knowledge-curator` 2026-10-28,
outcome **retain**: the one real instance is already fixed with its own
two regression tests; no second live instance found across the other
three consumers of `evaluate_result_precedence`) and `L-105` (the
`classify_symbol` `knowledge_root` threading gap — assessed by
`knowledge-curator` 2026-10-28, outcome **promote**: a pre-existing
regression test already exercises and would catch this exact scenario;
logged in `planning/learnings/promoted.md`).

## Where we're going

Phase 84 (Consolidated Knowledge API) remains next in sequence, confirmed
independent of Phase 83 in both directions (`planning/phase-83-*.md` §8,
`planning/phase-84-*.md` §5). The one unresolved, cross-phase-adjacent
question named in Phase 83's own plan — whether `assess_change_impact.py`
should eventually consume Phase 84's API once it exists — remains
exactly that: unresolved, not committed to either way. The one
outstanding gate specific to Phase 83 itself: the real Ledgerkit test
(`tests/test_reports.py::TestBalanceFromSpec::test_section_accounts_
overlapping_patterns_no_double_count`) has not landed in the real
`~/projects/ledgerkit` checkout — that remains a separate, explicitly
authorised, cross-repository action, not part of this phase's own scope
and not silently treated as done.

## Time / cost note

Single session, continuing directly from the prior session's two
planning-corrective passes. No AI API spend (no `codecompass sync`
enrichment phase was triggered — `--budget 0` on every scratch-copy
sync). Nothing ran unexpectedly long except the pre-existing, unrelated
real-network `test_sync_whole_project` test already in this repo's own
full suite.

## Corrective pass (2026-10-28, post-completion source review — `decisions/0089`)

Governing prompt: "CodeCompass Orchestrator — Phase 83 Corrective Pass."
Three suspected defects, named without being told they were already
confirmed, were verified real by direct reading of the shipped
`scripts/assess_change_impact.py` (commit `5132529`) before any code
changed, each reproduced with a standalone script run against the
unfixed code (not merely inspected):

1. **`classify_symbol()` matched Evidence by symbol name alone** — a
   `source_ref` citing `other.py`'s `target_function` was accepted as
   relevant to `impl.py`'s own, identically-named `target_function`
   (reproduced: `classify_symbol` returned `relevant_no_coverage_link`
   where `no_recorded_relationship` was correct).
2. **`resolve_changed_range()` resolved only the symbol enclosing
   `changed.start`, and never validated `changed.end`** — a range
   spanning `helper` (line 1) and `target_function` (line 5) returned
   only `helper`; a range `5-99999` against a 6-line file resolved as if
   `end` had never been read.
3. **`classify_symbol()` accepted a referenced result via a bare
   `yaml.safe_load`, with no schema/contract-identity/scope validation**
   — a YAML file with only `check_id: chk-a` / `outcome: PASS` (missing
   every other required `OracleResult` field) established
   `behavioural_risk`.

Fixed in `scripts/assess_change_impact.py` only (`oracle.py`/`graph.py`/
`knowledge_intermediate.py` untouched, confirmed by `git status` and by
this pass's own design — see `decisions/0089`): `classify_symbol` gains
`source_path` (path-qualified Evidence matching, normalised via
`PurePosixPath`) and `oracle_mod` (routes the referenced result through
the real `parse_oracle_result` plus explicit `contract_id`/`check_id`/
`scope` validation, never a parallel parser); `resolve_enclosing_symbol`
is replaced by `resolve_intersecting_symbols`/`compute_symbol_spans`,
resolving every symbol whose span intersects the full requested range,
validating `end` against the file's own extent exactly as `start`
already was, and introducing `partially_resolved` for a range only
partly covered by indexed symbols (naming the unmapped lines explicitly,
never discarding them). `assess()` now classifies every resolved symbol
independently and deduplicates applicable checks per range while
recording `contributing_symbols` per `AssuranceFinding`, so
deduplication never erases per-symbol provenance.

**Tests.** 18 new tests added directly reproducing/closing each defect
(`TestClassifySymbolSourceIdentity`, `TestClassifySymbolEvidenceValidation`,
`TestComputeSymbolSpans`, `TestResolveIntersectingSymbols`, plus new
cases in `TestResolveChangedRange` for multi-symbol/EOF/partial-coverage/
dedup) — `tests/test_assess_change_impact.py` now has 46 tests, all
passing. Full repository suite: `1054 passed, 2 skipped` (up from `1036
passed, 2 skipped` at Phase 83's original closeout — the 18 new tests).
`tests/test_oracle.py`/`tests/test_check_contracts.py` (Phase 82)
unmodified and green. `check_contracts.py --strict` / `check_knowledge_
base.py --strict` / `check_user_docs.py --strict` all exit `0`, with the
same findings as before this pass (unchanged counts: 7 informational
contract findings, 24 informational knowledge-base findings, 0 docs
findings) — this pass added no new knowledge records or contract
entries, so no new informational findings were expected or seen.

**Ledgerkit re-demonstration**, entirely on disposable scratch copies
(never the real checkout): pinned Ledgerkit HEAD `7224bb5c113cd3
aad7e86e994365703cd0070154`, `sha256(reports.py)`/`sha256(test_reports.py)`
identical to the original demonstration's own pinned values, confirming
the baseline had not drifted. The same OR-union double-counting mutation
(`section.accounts`'s match gate changed from a single boolean `any(...)`
append to counting matches and appending once per match) was re-applied;
Ledgerkit's full, original, unmodified suite — the new test file
genuinely absent from the tree at this point — passed `935 passed, 1
warning, 14 subtests passed`, identical to the original run. The new
test, added only afterward as its own file
(`tests/test_phase83_overlap_regression.py`, never merged into
`test_reports.py`, never committed to the real checkout), failed
`Decimal('300.00') != Decimal('150.00')` against the mutation and passed
against a second, clean scratch copy — both directions, identical to the
original run. `scripts/assess_change_impact.py --run-checks`, against
the corrected implementation and a fresh disposable scratch knowledge-
root (never `planning/knowledge/`/`planning/contracts/`), reported
`CONFIRMED_REGRESSION` (fresh=FAIL, aggregate=GAP) against the mutated
copy and `VERIFIED_SCOPE` (fresh=PASS, aggregate=PASS) against the clean
one. The defect-B fix was additionally confirmed against real,
unmutated Ledgerkit data (not only the synthetic fixtures in `tests/
test_assess_change_impact.py`): `--changed ledgerkit/reports.py:490-600`
resolved all three real top-level symbols it crosses (`register`,
`stats`, `balance_from_spec`); `--changed ledgerkit/reports.py:644-
999999` was rejected `cannot_map` on `end`, naming the real file's own
696-line extent. The real `planning/knowledge/balance-from-spec/` and
`planning/contracts/balance-from-spec/` trees were confirmed untouched
(`git status --short`) throughout — the scratch knowledge-root's own
`EV-BFS-004`/patched contract/placeholder result exist only under a
scratchpad path, never committed.

**Candidate learning filed**: `L-106` (`planning/learnings/inbox.md`,
status `candidate`, pending `knowledge-curator` triage) — all three
defects share one underlying shape: code that reused only part of an
existing, fully-specified identity/validation convention (the
`source_ref` path group; `oracle.parse_oracle_result`'s own full
validation; a range's own `end` coordinate) passed every test and one
prior independent audit, because every test and audit scenario happened
to exercise only the part that *was* reused.

**Independent audit.** See `planning/retros/_audit-phase-83.md`'s own
corrective-pass section for the full, separately-run verdict.

**Outstanding, unaffected by this pass**: the real Ledgerkit test still
has not landed in the real `~/projects/ledgerkit` checkout — exactly as
outstanding as before this corrective pass, not expanded or narrowed by
it.
