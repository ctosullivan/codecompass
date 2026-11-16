# Phase 89: Incremental Knowledge and Documentation Reconciliation — plan

## 0. Status

**Planning only. Implementation not authorised.** Drafted 2026-11-16,
independently of MCP transport, as the Phase 88 acceptance-exercise
dispatch's own §3-§6 instructions require.

**Amended once** (2026-11-16), after an independent `Plan`-type review
(`planning/retros/_review-phase89-plan.md`) returned **NOT READY** on
two blocking findings: (1) §4.4/§5.3's original draft claimed the new
reconciliation-apply step "reuses" `_apply_requirement_proposal`'s own
field-update pattern — false by direct reading; every existing
apply-path function in `knowledge_intermediate.py` only ever creates a
brand-new competing record, never mutates an existing one in place,
and the codebase's own documented convention says so explicitly. The
original draft also left an unaddressed self-conflict risk (two
accepted reconciliation items against the same Claim in one batch would
spuriously trip the reused whole-file-hash conflict check against each
other, not only against a genuine human edit). Fixed in §4.4/§4.8/§5.1/
§5.3 below: the deviation from "never mutate in place" is now narrowly
scoped (exactly two machine-derived fields, never `statement`/
`derivation`), explicitly disclosed and justified rather than
mischaracterised as reuse, and the self-conflict risk is closed by
merging same-Claim findings into one manifest item at proposal time
rather than ever producing two. (2) `apply_manifest` has one real
production call site (`cli.py::knowledge_apply_manifest`, `codecompass
knowledge apply`) and `CLAUDE.md` §1's L-021 requires this plan's own
verification section to name and test through it directly — the
original Stage 89A test list did not; fixed in §7 below. Two
non-blocking inventory inaccuracies in the original §1.1 (undercounting
`apply_manifest`'s real recognised kinds and `find_gaps`'s real gap-kind
taxonomy) are also corrected in place.

**Re-reviewed** (2026-11-16, fresh independent `Plan`-type dispatch,
full re-verification from scratch against real source, not taken on
trust from either the plan's or the first review's own account):
**READY WITH NON-BLOCKING OBSERVATIONS** (`planning/retros/
_review-phase89-plan.md`, "Re-review" section). Both blocking findings
confirmed genuinely resolved. The re-review also caught that the first
correction's own `find_gaps` gap-kind count (said "seven") was itself
still wrong — the real count `find_gaps` itself emits is six, now
corrected in §1.1 below — and surfaced two further, real, non-blocking
write-semantics gaps the merge-based fix introduced (a merged item
with disagreeing fresh outcomes never specified which field(s) to
write; a merged item's own multi-record write had no idempotency guard
against a crash-and-retry duplicating an already-written Evidence
record) — both resolved in place in §4.8/§5.3/§9 below by reusing two
more already-existing project mechanisms (`evidence_support_state:
"conflicting"`; the same `_find_existing_promoted_record` idempotency
check every other apply-path function already uses), per the
reviewer's own recommendation, rather than triggering a third full
review round. **This plan is READY.** Implementation remains
unauthorised pending a separate, explicit go-ahead.

**Amended a third time** (2026-11-16, fresh independent-orchestrator
dispatch, "Phase 89 Final Planning Amendment"): a from-scratch,
line-by-line source re-verification — not trusting either prior round's
own account — found that this plan's own §6.1 Task A walkthrough rested
on an assumption that **does not hold**, plus a more fundamental reason
the Evidence-identity design in the second amendment above was still
unsound, a real exit-gate overclaim, and a real baseline/sync-ordering
gap. See §0.1 immediately below for exactly what was found and why;
§1.2, §3, §4.1-§4.4, §4.8, §5.1-§5.4, §6, and §9 are rewritten in place
accordingly. **This plan is NOT YET re-reviewed following this
amendment** — a fresh independent `Plan`-type dispatch against the
amended text (§9) is required before READY can be re-claimed; the
second amendment's own READY verdict above applied to the plan as it
stood *before* this round and no longer describes the plan's current
text.

**Re-reviewed** (2026-11-16, fresh independent `Plan`-type dispatch,
full re-verification from scratch, not taken on trust from the plan's
or any prior review's own account): **NOT READY**, on two new blocking
findings in §4.4's `evidence_support_state` recomputation rule
(`planning/retros/_review-phase89-plan.md`, "Re-review (second
amendment round)" section) — every finding from the first two review
rounds, and this round's own re-verification of §0.1.A-D, was
independently re-confirmed resolved/sound. Blocking Finding 1:
`"contradicted"` is not a valid `evidence_support_state` value (the
real, closed enum is `{"supported", "partially_supported",
"unsupported", "conflicting"}`, `scripts/check_knowledge_base.py` line
209-214) — `"contradicted"` is a `Claim.status` value, a different
field entirely. Blocking Finding 2: the rule's own single-Claim scope
and its one worked application in §6.1 (a cross-Claim "sibling Claims
under the same Requirement family" notion) contradicted each other,
independently falsified against this project's own pre-existing
`CL-BFS-001`/`CL-BFS-002`/`CL-BFS-003`/`CL-BFS-005` records. **Amended
a fourth time** (same session): §4.4's rule rewritten in place to fix
Finding 1 (`"unsupported"`, not `"contradicted"`) and Finding 2 (a
purely local, single-Claim-scoped test — whether `supporting_evidence`
contains at least one `evidence_kind: "test"` record — replacing the
undefined cross-Claim notion; directly validated against every real
record this mechanism can actually reach, including why it never
reaches the whole-contract-scoped `CL-BFS-003`/`CL-BFS-005` at all);
§6.1 step 8's worked walkthrough corrected to match.

**Re-reviewed a fourth time** (2026-11-16, fresh independent `Plan`-type
dispatch, scoped focus on the fourth amendment's own corrected text,
full independent re-verification, not taken on trust): **READY WITH
NON-BLOCKING OBSERVATIONS** (`planning/retros/_review-phase89-plan.md`,
"Re-review (fourth amendment, focused)" section). Both of the third
round's blocking findings confirmed genuinely resolved, independently
re-derived from the real `CL-BFS-00{1,2,4}` records, not re-asserted.
Three further non-blocking items the review surfaced — (i) the
recomputation rule's own evidence-kind partition is sound only for
contract-governed Claims (confirmed structurally true today, since this
mechanism can only ever reach a contract-governed Claim, but not
previously stated as an explicit scope limit); (ii) nothing previously
stopped a human mistakenly adding the new `check_id` field to a
multi-check Requirement, which would silently resolve to every one of
its `depends_on` Claims at once; (iii) the Stage 89A test list named
the Blocking-Finding-1 regression test ambiguously — have all been
folded in directly in §4.4/§5.1/§7/§9 below, per the reviewer's own
recommendation, rather than triggering a fifth review round.

**Amended a fifth time** (2026-11-16, fresh independent-orchestrator
dispatch, "Phase 89 Planning Corrections and Independent Verification"):
a from-scratch, direct-source/direct-Ledgerkit re-verification —
assuming no knowledge of any prior conversation, not trusting any
earlier round's own account — found five further, genuine
implementation-readiness defects the four prior rounds did not reach,
because each targeted a different layer of the design (the detection
mechanism's own output shape, not its routing logic; the real Ledgerkit
test bodies, not just the knowledge records describing them; the actual
document this plan cites, not the plan's own paraphrase of it; the CLI
surface's real side effects, not its prose description). See §0.2
immediately below for exactly what was found, with direct evidence for
each; §4.1, §4.3, §4.4, §4.10, §5.1, §5.3, §6.1-§6.4, §7, §9 are amended
accordingly.

**Re-reviewed** (2026-11-16, fresh independent `Plan`-type dispatch,
full re-verification from scratch against real source, real Ledgerkit
tests, and the real evaluation-methodology document, not taken on trust
from the plan's or any prior review's own account): **NOT READY**, on
one new blocking finding and two factual errors in the fifth
amendment's own stated verification (`planning/retros/
_review-phase89-plan.md`, "Independent review — fifth amendment"
section). Findings B, C, D independently re-confirmed sound exactly as
stated. Finding A's core diagnosis and fix confirmed sound, but the
paragraph's own "zero call sites" claims were themselves wrong — found
via a non-recursive `src/codecompass/*.py` glob that silently skipped
the `mcp/` subdirectory; `write_oracle_result` and `assess()` each have
exactly one real call site, in `src/codecompass/mcp/tools.py` (lines
466 and 342 respectively), re-verified directly, now corrected in
place — the conclusion (the fix is sound and backward-compatible) is
unchanged, since `mcp/tools.py:342`'s own call passes `run_checks=
False`, never reaching the code path the new parameter affects. The
same review independently found a further, real specification gap in
`_capture`'s own design (keyed by `check_id` alone, when `assess()`'s
own `run_check_assurance` loop runs once per `(range, check_id)` pair,
not once per `check_id` globally — a second range contributing the same
`check_id` would silently overwrite the first's captured result) —
closed with a per-`(range, check_id)` accumulation fix. **Blocking
finding E**: §7's own CLI-boundary test description asserted
`detect-changes` spawns zero subprocesses "with and without
`--probe-coverage`" — directly contradicting §4.10's own description of
`--probe-coverage` spawning a real `pytest --collect-only` subprocess,
a self-contradiction of the same character as the third review round's
own Blocking Findings (falsifiable without external facts, purely from
the plan's own two sections disagreeing). **Amended a sixth time**
(same session): §0.2.A corrected in place with the real call-site
facts; `_capture`'s design corrected to per-`(range, check_id)`
accumulation (§4.4/§5.1), with a new, dedicated multi-range regression
test (§7); §7's CLI-boundary test split into two separate,
non-contradictory assertions (without the flag: zero subprocesses; with
the flag: exactly one collection-only subprocess, zero files either
way).

**Re-reviewed** (2026-11-16, fresh independent `Plan`-type dispatch,
focused on the sixth amendment's own three targeted fixes, each
independently re-verified directly against real source rather than
taken on trust): **READY WITH NON-BLOCKING OBSERVATIONS**
(`planning/retros/_review-phase89-plan.md`, "Independent review — sixth
amendment" section). All three fixes confirmed sound: the CLI-boundary
test's own two assertions no longer contradict §4.10; the corrected
call-site facts re-verified independently by the reviewer's own fresh
`grep` (`mcp/tools.py:466`/`:342`); the multi-range `_capture` fix
confirmed coherent and closes the gap, directly re-traced against
`change_impact.py:510-586`'s own real loop structure. Two further,
genuinely non-blocking items (a missing §9 risk-register entry for the
`_capture` redesign; an off-by-one line citation, "line 347" for what is
actually line 348) folded in directly below rather than triggering a
seventh review round, per this project's own established practice for
non-blocking editorial observations. **This plan is READY.**
Implementation remains unauthorised pending a separate, explicit
go-ahead.

### 0.1 What this amendment found, and why the prior draft was wrong

**A. The Task A walkthrough's core assumption is false, source-verified
directly.** §6.1's prior text assumed `change_impact.assess(run_checks=
True)` would, on its own, discover the newly-added Ledgerkit test and
propose upgrading `CL-BFS-004`. Tracing `classify_symbol`/`assess`
line-by-line (`change_impact.py:318-415`, `510-586`) against the real
`CL-BFS-004.yaml` (`supporting_evidence: [EV-BFS-001]`, a **source**-kind
Evidence only) and the real `oracle-contract.yaml` (a `required: true`
third check whose `check_reference` names a test that does not yet
exist) proves this mechanism **structurally cannot** do what the prior
walkthrough assumed: `assess()`'s own `check_contributors` (line
549-561) is populated *exclusively* from `behavioural_risk`-tier
`ClaimFinding`s, and a finding only reaches `behavioural_risk` when
`classify_symbol`'s own `test_evidence_check_id` bridge (line 371-394)
already has an entry for it — built *exclusively* from **pre-existing**
test-kind Evidence records that already cite a resolvable
`OracleResult`. `CL-BFS-004` has no such Evidence yet — that is the
entire, real, previously-documented point of the gap this task exists
to close (`DEC-BFS-002`'s own rationale). So `assess(run_checks=True)`
classifies `CL-BFS-004` as `relevant_no_coverage_link` (exactly as it
already is today) and **never calls `run_check_assurance` for the new
check at all** — not a hypothetical edge case, a structural
precondition the prior walkthrough never actually traced. §4.1-§4.3,
§5.1, §6.1 below are rewritten around a second, genuinely new detector
this gap requires.

**B. The Evidence-identity/idempotency design was unsound, for a reason
more fundamental than the one the second amendment already disclosed.**
Direct grep across `src/codecompass/*.py` confirms **zero existing call
sites** create a new Evidence record programmatically (`_next_id(sdir,
"EV")` never appears anywhere) — every existing apply-path function
only ever creates a new *Claim*. `_find_existing_promoted_record`
(`knowledge_intermediate.py:2103-2145`) is explicitly typed: it matches
by `kind` (`"claim"` by default) against a record's own `statement`
field — Evidence records have no `statement` field at all (they have
`what_it_shows`), so this helper cannot be reused for Evidence identity
under any parameterisation; this is a type mismatch, not merely an
imperfect fit. Separately, and newly discovered this round:
`apply_manifest`'s own per-item `state: "applied"` persistence (the
mechanism the second amendment's §4.8 leaned on for crash safety) is
**buffered for the whole manifest, not written per item** —
`manifest_path.write_text(...)` runs exactly once, after the entire
`for item in data.get("items", [])` loop completes
(`knowledge_intermediate.py:2542-2543`) — so a crash partway through a
multi-item batch leaves **every** item in that run's own `state` field
exactly as it was before the run started, including items that had
already been successfully applied earlier in the very same crashed run.
The real, load-bearing crash-safety guarantee in this codebase today is
therefore never "the manifest's own persisted state flag" — it is each
individual `_apply_*` function's own idempotent, content-based dedup
against the canonical records themselves (`_find_existing_promoted_
record`, safe to re-run because it is re-checked fresh on every call,
against disk state, not against the manifest's own bookkeeping).
Phase 89's new apply branch must provide the equivalent guarantee for
Evidence from scratch, there being no existing Evidence-identity
convention to mirror. §4.4, §4.8, §5.3 below are rewritten accordingly.

**C. The exit-gate / negative-result question was a real, confirmed
inaccuracy, not a defensible interpretation.** `planning/v2-roadmap.md`
§9 (line 702-705, re-read directly) states the exit gate in one
sentence: "The second task measurably benefits from the first,
evidenced... not asserted — achieved without any dependency on an MCP
server." No clause there, or in `decisions/0085` §3, permits an
honestly-reported negative result to satisfy this gate. §6.3/§8/§9
below now distinguish three genuinely separate questions the prior §8
conflated into one.

**D. The baseline/sync-ordering gap is real, with a concrete failure
mode.** §4.1's prior detector reads a file's hash from `repo_root`'s own
`context-graph.db` (`source_files.content_hash`) and compares it against
the persisted baseline. `change_impact.py::resolve_changed_range` (line
206-290), re-read directly, already has to guard against exactly this
value going stale — it independently recomputes the *live* on-disk hash
(`oracle_mod.sha256_file(live_path)`) and reports a distinct
`"stale_index"` status whenever it disagrees with the graph's own
recorded value, precisely because `codecompass sync` populates that
column and nothing keeps it current automatically. §4.1's prior detector
**never performed this same live-vs-graph check before trusting the
graph's own recorded hash as "current"** — a source file edited after
the last `sync` but before detection runs would be compared against the
baseline using a *stale* graph-recorded hash, silently reporting
"unchanged" even though the file genuinely changed on disk. §4.1, §5.1,
§5.2 below close this by requiring the same live-hash cross-check
`resolve_changed_range` already performs, reused directly, before any
baseline comparison is trusted.

**Two further semantic corrections (dispatch §3), independently
verified:**

- `change_impact.py::run_check_assurance` (line 436-478) labels *any*
  fresh effective `FAIL` `CONFIRMED_REGRESSION` unconditionally — it
  never checks whether a historical `PASS` for the same `check_id` ever
  existed. Every existing use of this classification in `decisions/
  0086`/`0087`/`planning/phase-83-semantic-change-assurance.md`
  (re-read directly) is written for the scenario where a prior `PASS`
  did exist and a mutation broke it — the term is accurate there.
  `decisions/0087` §1 deliberately fixes *historical PASS never masking
  a fresh FAIL*, not the reverse question this amendment raises (a fresh
  FAIL with **no** historical PASS at all — a newly discovered failure,
  not a demonstrated regression). Per this amendment's own governing
  dispatch, Phase 83's own classification is left **completely
  unmodified** — relabelling `CONFIRMED_REGRESSION` itself would be
  exactly the kind of Phase-83-semantics change this plan must not make,
  and it is not Task A's own scenario, which expects a `PASS`, not a
  `FAIL` — instead, §4.3 below adds a narrow, additive, Phase-89-level
  distinction, read from data `change_impact.py` already returns
  unchanged (`AssuranceFinding.observed_outcomes`/`aggregate_state`),
  surfaced alongside the unmodified classification, never in place of
  it.
- A disposable, schema-governed document proves the *mechanism*
  (`detect_grounded_region_changes` correctly fires `claims_changed`)
  but proves nothing about whether real documentation content a real
  Ledgerkit task would actually consult got measurably better. §6.2/§6.3
  below now require both pieces of evidence separately, never one
  standing in for the other.

### 0.2 Fifth amendment — five further defects, independently verified
this round against real source, real Ledgerkit tests, and the real
methodology document (not the plan's own prior paraphrase of any of
them)

**A. Detector (a)'s own design cannot actually retain the fresh
`OracleResult` it depends on — source-verified directly.** §5.1's
`propose_reconciliation` (detector (a) branch) was written to "re-walk
`assess()`'s own returned `range_reports[]...assurance[]`" to recover a
fresh result's `run_id`/`raw_output_ref` for Evidence construction. This
is impossible as designed: `AssuranceFinding` (`change_impact.py:
424-433`) carries `check_id`/`classification`/`fresh_effective_outcome`/
`fresh_invalid_reason`/`aggregate_state`/`observed_outcomes`/
`contributing_symbols` — **no `run_id`, no `raw_output_ref`, no digests**.
`run_check_assurance` (`change_impact.py:436-478`) computes a real,
fully-populated `fresh_result: OracleResult` (line 445,
`oracle_mod.evaluate_check(...)`) but **returns only the `AssuranceFinding`
summary** — `fresh_result` itself goes out of scope and is discarded the
moment the function returns.

**Correction (independent fifth-round review, confirmed directly — an
earlier version of this paragraph's own grep used a non-recursive
`src/codecompass/*.py` glob and wrongly reported zero call sites for
both functions below; re-run recursively, the real counts are
different, though the conclusion they support is unchanged)**:
`oracle.write_oracle_result` has exactly **one** real call site —
`src/codecompass/mcp/tools.py:466`, inside `oracle_execute_check` (a
Phase 88 MCP tool, real production code, not a maintainer script) —
which already follows the exact `evaluate_check(...)` →
`write_oracle_result(...)` sequence this amendment's own fix requires,
a stronger, in-repository precedent than the standalone
`scripts/run_balance_from_spec_oracle.py:92` script alone. `change_
impact.assess` similarly has exactly **one** real call site outside
`change_impact.py` itself — `src/codecompass/mcp/tools.py:342` — but it
passes `run_checks=False` (line 348), meaning `run_check_assurance` is
never invoked from that call site at all (`assess()`'s own `if run_
checks: ... else: finding = AssuranceFinding(..., classification=
"VERIFICATION_GAP", ...)` branch, `change_impact.py`, re-read directly)
— so this real caller is genuinely unaffected by the fix below
regardless of what parameter is added, not merely "unaffected because
it doesn't pass the new parameter." `run_check_assurance` itself has
**zero** call sites outside `change_impact.py` (this part of the
original grep was correct). So the previous draft's own detector-(a)
proposal logic had no actual source of the data it needed — not a
missing call, a structurally absent return value. **Fix (§4.4/§5.1/§5.3
below)**: a small, additive, backward-compatible result-capture
mechanism — `run_check_assurance(..., on_fresh_result:
Callable[[OracleResult], None] | None = None)` and `assess(...,
on_fresh_result: ... = None)`, threaded through unchanged otherwise,
invoked with the real `fresh_result` at the exact point it is computed,
before it would otherwise be discarded. The one real existing caller of
`assess()` (`mcp/tools.py:342`) is unaffected both because it does not
pass this parameter and because its own `run_checks=False` means the
code path that would invoke the callback never executes for it either
— two independent reasons, not one, that today's behaviour is preserved
exactly (dispatch requirement 6). An alternative considered and
rejected: having `propose_reconciliation` independently re-call
`oracle.evaluate_check` a second time for the same check, outside
`assess()`, to recover provenance — rejected because it means the
*classification* a human reviews and the *Evidence* actually written
could come from two genuinely different real runs of the same check
(never guaranteed identical, since each run is its own independent
execution, `decisions/0082` §C), a correctness gap strictly worse than
one additive, opt-in parameter with zero effect on any existing caller.

**A further, independently-found specification gap (fifth-round
review, folded in here rather than left implicit)**: `assess()`'s own
`check_contributors`/`run_check_assurance` loop (`change_impact.py:
526-578`) runs **inside** `for c in changed:` — re-initialised per
range, not once per `check_id` globally across the whole call. If the
same `check_id` is contributed by findings from two different ranges in
one `propose_reconciliation` call (plausible once detector (a) batches
multiple drifted files in one run), `run_check_assurance` executes
**twice** for that `check_id` — two genuinely separate real runs, two
distinct `run_id`s — and a capture mechanism keyed by `check_id` alone
would silently let the second overwrite the first in memory, losing the
first range's own result even though a finding for that range still
exists in `range_reports[]`. **Fix**: `_capture` (§5.1) accumulates a
`list[OracleResult]` per `check_id` (never overwrites), and
`propose_reconciliation` matches each `ClaimFinding` to its own
specific captured result by `(range index, check_id)` — the finding's
own known position in `range_reports[]` — never by `check_id` alone.
Not exercised by this plan's own worked walkthroughs (§6.1/§6.2's
`CL-BFS-001`/`CL-BFS-002`/`overlapping-account-patterns-no-double-count`
map to distinct `check_id`s throughout), so not a defect in any control
this plan actually runs, but a real gap in `propose_reconciliation`'s
own specification that Stage 89A's implementer must close before a
multi-range batch is handled correctly — named here as a stated
mechanism requirement, not deferred to an ADR-only note (§7's own new
regression test, below, covers it directly).

**B. Detector selection conflated three distinct states — source-verified
against `scripts/check_contracts.py`'s own real `current_pass_check_ids`
computation.** The fourth-amendment text gated detector (b) on "zero
currently-valid historical `OracleResult`" for a required check — but
that same condition is also true of a check that **was** previously
covered (real citing test-kind Evidence exists) whose historical result
has since gone `INVALID` under `oracle.evaluate_result_precedence`
(e.g. its `test_input_digest` no longer matches current reality,
`decisions/0088`'s own named, expected state, re-read directly in
`scripts/check_contracts.py` lines 212-237/290-300). That check already
has an Evidence bridge; it is detector (a)'s own re-verification
scenario, not a newly-coverable one — but the fourth-amendment's own
gate for detector (b) would incorrectly also match it, since
`current_pass_check_ids` (line 290-300, re-read directly) only ever asks
"is there a currently-valid PASS," never "has this check ever had any
citing Evidence at all," which are different questions. **Fix (§4.1(b)/
§5.1 below)**: detector (b)'s own gate is corrected to the one condition
that actually distinguishes "never yet covered" from the other two —
**zero existing `evidence_kind: "test"` Evidence record anywhere under
the slug whose `test_ref` resolves to a result for this `check_id`**
(the exact same bridge-presence test `classify_symbol`'s own
`test_evidence_check_id` already performs, §0.1.A, reused as the
detector-selection gate itself rather than reinvented) — never "zero
currently-valid result." This is deterministic and the two detectors'
own gates are now provably mutually exclusive by construction: a check
either has a citing Evidence record (detector (a)'s own exclusive
scope, regardless of whether that Evidence's cited result is currently
valid, stale, or invalid) or it does not (detector (b)'s own exclusive
scope) — never both, never neither undecidably. A previously-covered
check whose result has gone stale is now unambiguously detector (a)'s
own re-verification scenario (reported via the existing `"stale_test_
citation"` `find_gaps` kind, unchanged, §1.1), never misrouted to
detector (b) merely because no fresh PASS currently exists for it.

**C. The detector-(a) positive control's own named mutation cannot
fail the tests it claims to fail — verified directly against the real
Ledgerkit checkout, not the knowledge records describing it.** §6.2's
"True-positive control, detector (a)" proposed reproducing `DEC-BFS-002`'s
own OR-union double-counting mutation and expecting
`test_single_section_rows_and_subtotal`/`test_multi_section_correct_values`
to fail. Read directly: `test_single_section_rows_and_subtotal`
(`tests/test_reports.py:706-720`) uses exactly one account pattern per
section (`accounts=("expenses",)`); `test_multi_section_correct_values`
(line 742-748) uses the two-section spec `_income_expenses_spec`
(line 697-704), itself exactly one pattern per section
(`accounts=("income",)`, `accounts=("expenses",)`); the one existing
test with more than one pattern in a section,
`test_section_multiple_accounts_patterns_or_union` (line 810-824), uses
two patterns (`"income:salary"`, `"expenses:housing"`) that never match
the same posting and the test asserts only row membership, never
subtotal arithmetic. `reports.py:663`'s real matching gate (`if not
any(_matches_pattern(pat, posting.account) for pat in section.accounts):
continue`) is a single boolean membership check, appending a matching
posting exactly once regardless of pattern count — an OR-union
double-counting mutation changes behaviour **only** for a posting that
matches more than one pattern in the same section's own `accounts`
tuple, a condition **none** of the three real tests above ever
construct. This is not a new observation about the mutation — it is
exactly what `DEC-BFS-002`'s own rationale already states in this
project's own knowledge base ("the one existing test constructing
multiple OR-combined account patterns... asserts only posting
membership, never the resulting subtotal arithmetic — so no test
anywhere in Ledgerkit would catch [this]") — the fourth amendment's own
§6.2 control contradicted this project's own already-recorded finding
without re-checking it. **Fix (§6.2 below)**: the detector-(a) positive
control uses a different, narrow, genuinely test-breaking mutation —
removing the `if section.invert:` guard at `reports.py:685-686` (making
sign inversion unconditional instead of gated) — verified directly
against the real test assertions: `test_single_section_rows_and_subtotal`
(Expenses section, `invert=False`, asserts `subtotal == Decimal
("1359.00")`) would compute `Decimal("-1359.00")` under the mutation and
fail; `test_multi_section_correct_values`'s own `expense_result` (same
section, same assertion) fails identically, while `income_result`
(`invert=True`) is unaffected by this specific mutation (its own correct
behaviour already negates unconditionally for that section, so removing
the guard changes nothing for it) — the whole test still fails, since
it asserts both subtotals in one test body. This mutation is entirely
independent of the overlapping-pattern code path (a different, unrelated
few lines), so it never interferes with — and is retained strictly
separate from — detector (b)'s own overlapping-pattern mutation
(§6.1, unchanged, genuinely exercises the condition it names).

**D. Task B's own pre-registration cited a threshold the named document
does not define, and separately pre-registered too late to be a genuine
pre-registration at all — both verified directly.** `planning/
v2-evaluation-methodology.md`, read in full this round: it defines three
arms, held-comparable conditions, eleven metrics, and a pre-registration
discipline for *Phase 90's own future trial* — it contains no numeric
scale, scoring rubric, or named "minimum-meaningful-difference" value
for any metric; its own closing section states this explicitly ("It does
not set a numeric target for any metric above... no numerical target is
set in advance of this phase's own baseline"). §6.3's prior text citing
"the methodology document's own existing minimum-meaningful-difference
threshold" named something that does not exist. Separately, and newly
found this round: §6.3's own pre-registration was to happen "at Stage
89C's own start" (its literal text) — but Stage 89C (§7) runs *after*
Stage 89B, which is where Task A's own real demonstration (§6.1) runs —
so the prior text's own stated timing would pre-register Task B
*after* Task A's outcome is already known, the exact failure mode
pre-registration exists to prevent, not merely an imprecise phrase.
**Fix (§6.3/§7 below)**: (i) the false citation is removed, replaced
with a concrete success criterion built from an instrument this project
already has and already uses qualitatively elsewhere —
`context-evaluator`'s existing PASS/PASS WITH GAPS/FAIL verdict and
LOW/MODERATE/HIGH context-advantage rating (`.claude/agents/
context-evaluator.md`'s own stated output, unchanged, reused not
reinvented) — stated as this plan's own, explicitly-owned threshold,
never attributed to a document that does not define one; (ii) the
pre-registration record (task selection rule, success criterion,
treatment/control design) is now a named **Stage 89A deliverable**,
written and committed *before* Stage 89A's own detection/verification
work for Task A begins, not deferred to Stage 89C.

**E. The proposed `detect-changes` CLI command was described as
read-only while its own design already called `change_impact.assess
(run_checks=True)` — a real, test-executing, file-writing operation,
not an inspection.** §4.10's prior text said `detect-changes` "is
read-only" and, in the same sentence, "runs `change_impact.assess
(run_checks=True)`" — `run_checks=True` is exactly what makes
`run_check_assurance`/`oracle.evaluate_check`/`run_pytest_check` execute
a real `pytest` subprocess against the target repository and write a raw
output file to disk (`oracle.py:746-784`, unconditional on every call,
not an opt-in the caller controls once this path is reached) — genuinely
not read-only, and, once Finding A's fix lands, this same path would
also persist a structured `OracleResult` YAML. Separately, `pytest
--collect-only` (detector (b)'s own coverability probe, §5.1) executes
arbitrary repository Python at module-import time (`conftest.py`,
module-level code) — not a security sandbox, and not "read-only" in any
meaningful sense either, only "does not run test bodies." **Fix (§4.10/
§5.1 below)**: the single command is split into the five layers
dispatch §2.E names, each with its own, named, minimal side-effect
boundary — see §4.10 below for the corrected command set and §7 for the
new regression test proving the purely-observational layer never
executes a subprocess or writes a file.

**F. Independent verification required.** As with every prior amendment
round, a fresh independent `Plan`-type review of this round's own
amended text is required before this plan can be reclaimed READY — see
dispatch §4's own requirement, actioned after the amendments below are
in place.

## 1. Verified current state (re-confirmed this session, not assumed)

- Phase 88 (Agent Integration and MCP) is `done` (`planning/ROADMAP.md`,
  `planning/CONTEXT.md`). A real-agent MCP acceptance exercise for Phase
  88 was completed in this same session —
  `planning/retros/phase-88-mcp-real-client-acceptance.md` — independent
  of this plan; Phase 89 does not depend on it or on MCP at all.
- Phase 84 (knowledge API) and Phase 87 (documentation schema/
  compilation) are both `done` — the two real prerequisites named by
  `decisions/0085` §3 and `planning/v2-roadmap.md`'s own Phase 89
  section (lines ~115-155 there). **Phase 89 does not depend on Phase
  88** — confirmed independently deliverable, re-verified directly
  against `planning/v2-roadmap.md` rather than assumed from this
  dispatch's own framing.
- `decisions/0085` §3 is the governing split decision: the old merged
  Phase 88 was split into Phase 88 (MCP, done) and Phase 89 (this plan),
  "independently deliverable... carries forward the former Phase 85's
  full original content." §3 names the architectural constraint this
  plan must honour: build a **change-driven trigger** layered on the
  **existing** reconciliation flow — never a new scheduler, event bus,
  competing knowledge store, or documentation compiler, and never a
  redesign of Phase 87's own compiler.

### 1.1 Source-verified capability inventory (direct source reading this
session, not assumed from any plan's own prior description)

- **`src/codecompass/knowledge_intermediate.py`** (Phase 81, packaged):
  - `detect_anchor_changes`/`write_manifest`/`apply_manifest` — the
    existing three-stage reconciliation flow (detect → human-reviewed
    manifest with `decision: "accept"/"reject"` → apply, the *only*
    stage allowed to write a canonical record, re-validating
    mechanically rather than trusting the review stage's own say-so).
    Today this flow's only detector is `detect_anchor_changes` (dual-
    hash: canonical-record hash vs. rendered-Markdown-projection hash,
    §1.5 of Phase 81's own plan) — triggered by a human/tool edit to an
    `intermediate/*.md` projection, **never** by a source-code or test
    change. This is the flow Phase 89 extends with a *second* detector,
    not replaces.
  - `detect_grounded_region_changes` — the Phase 87 five-state
    (`new`/`noop`/`doc_candidate`/`claims_changed`/`concurrent_conflict`)
    documentation-region reconciliation. Critically: `claims_changed`
    already fires whenever a cited Claim/Evidence/Decision record's own
    **file content hash** (`_current_cited_hashes`,
    `knowledge_intermediate.py:315-320`) differs from the hash recorded
    in `.grounding-state.toml` at the region's last baseline — it has
    **no dependency on MCP, on `docs maintain`'s own caller, or on how
    the Claim's content came to change**. This means: once a Claim's own
    file is correctly updated by anything, this *already-shipped,
    unmodified* mechanism correctly cascades that into documentation
    invalidation. Phase 89 therefore needs **zero new doc-reconciliation
    code** — only a correct way to get the Claim's file updated in the
    first place, on a real source/test change, with human approval.
  - **Corrected by independent review**: `apply_manifest`'s real
    dispatch already recognises **three** kinds today, not two —
    `write_manifest`'s own `"anchor_edit"`/`"candidate_addition"`, plus
    a third, `"doc_region_edit"`, written not by `write_manifest` but by
    a separate, already-existing **sibling writer function**,
    `write_doc_candidates_to_manifests` (called from `docs maintain`).
    This is the real precedent §9's own "sibling writer vs. extend
    `write_manifest`" question needed and the original draft missed
    citing: Phase 89 adds its fourth kind, `"source_reconciliation"`
    (§5.3), via its own new sibling writer function,
    `write_source_reconciliation_manifest` — mirroring `write_doc_
    candidates_to_manifests`'s own already-production pattern exactly,
    not extending `write_manifest` itself (§9's open question, now
    resolved by this precedent rather than left undecided).
- **`src/codecompass/change_impact.py`** (Phase 83, relocated/packaged
  at Phase 88): `classify_symbol` resolves a changed `(symbol, path)`
  pair against citing `source`-kind Evidence, then against Claims whose
  `supporting_evidence` cites that Evidence, tiered
  `no_recorded_relationship`/`relevant_no_coverage_link`/
  `behavioural_risk` — and, for `behavioural_risk` findings with a
  resolvable `test`-kind Evidence bridging to a real oracle check,
  `assess(..., run_checks=True)` re-executes that check fresh and
  classifies `CONFIRMED_REGRESSION`/`VERIFIED_SCOPE`/`VERIFICATION_GAP`/
  `INVALID_ASSESSMENT` from the **fresh result's own effective outcome
  alone** (`decisions/0087` §1, never the aggregate). **This already is
  the "source/test change → affected canonical knowledge, staleness
  distinguished from unrelated change" primitive** (planning decisions
  #1-#3 below) for a change whose `changed[path:start-end]` range is
  already known. What it does **not** do: discover *which* ranges
  changed on its own (it is handed an explicit range, by design — no
  `git diff` parsing, Phase 83's own stated non-goal), and it never
  writes anything back to `planning/knowledge/` (by design — read-only
  classification).
- **`src/codecompass/graph.py`**: `source_files.content_hash` (Phase 77,
  confirmed present in the schema this session,
  `graph.py:77/139/238/794-795`) is already populated by `codecompass
  sync` for any project (including a target repo like Ledgerkit, once
  *that* repo has its own synced `context-graph.db` — already a stated
  precondition of `change_impact.assess`, unchanged here). This is the
  one new primitive's own data source (§5.1) — no new schema, no new
  table.
- **`src/codecompass/knowledge_api.py`** (Phase 84): `find_gaps`'s `Gap`
  taxonomy is the existing, extensible gap-reporting shape. **Corrected
  twice by independent review** (the first correction's own count was
  itself still wrong, caught by a fresh re-review that traced every
  `Gap(kind=...)` append directly): `find_gaps` itself (plus its own
  helper, `_find_gaps_for_slug_contract`) actually emits **six** kinds —
  `contradiction`/`dangling_evidence_reference`/`dangling_dependency_
  reference`/`missing_contract`/`unverified_required_scope`/
  `stale_test_citation` — not the four named in the original draft nor
  the seven claimed in the first correction. The shared `Gap` dataclass's
  own type-comment (`knowledge_api.py:140-141`) documents a seventh
  value, `missing_evidence`, but that one is emitted only by a
  *different*, sibling function, `trace_evidence` — never by
  `find_gaps` itself; the original and first-corrected drafts both
  conflated "kinds the shared `Gap` type names across every producer"
  with "kinds `find_gaps` itself emits." Independently re-verified,
  twice, that Phase 89's proposed new kind,
  `claim_contradicted_by_fresh_check` (§5.4), is genuinely distinct from
  the two adjacent existing ones, not duplicative: `"contradiction"`
  fires on an *already-recorded, already-promoted*
  `contradicting_evidence`/`status=contradicted` state; `"stale_test_
  citation"` fires on a *cited* result being digest-invalid while an
  *uncited* current result passes. Neither covers this phase's own new
  condition — a *pending, unapplied* manifest item proposing a fresh
  `CONFIRMED_REGRESSION` that nobody has reviewed yet. Phase 89 reuses
  the same `Gap` dataclass and `find_gaps`'s existing scan loop — not a
  parallel report format.
- **Phase 87 `docs` CLI sub-app** (`cli.py`): `compile`/`maintain`/
  `publish`/`record-review` are **unchanged by this plan** — Phase 89
  never touches `doc_compiler.py`, `spec_docs.py`'s own section-mapping
  logic, or the clean-room composition step. `docs maintain`'s existing
  discovery (every `**/*.schema.yaml`) and its existing five-state
  reconciliation already do the documentation half of this phase's own
  objective, for free, once a Claim's file is correctly updated.

### 1.2 Newly verified this round (direct source/record tracing, not
assumed from either prior amendment's own account)

- **`apply_manifest`'s per-item `state: "applied"` write is buffered for
  the whole batch, not persisted per item.** `manifest_path.write_text
  (_serialize_manifest(data), ...)` (`knowledge_intermediate.py:
  2542-2543`) runs exactly once, *after* the entire `for item in
  data.get("items", [])` loop finishes — every item's in-memory `state`
  mutation (line 2535-2538) before that point is lost if the process
  crashes mid-loop, even for items already successfully applied earlier
  in the same run. The real, already-existing crash-safety guarantee in
  this codebase is each `_apply_*` function's own idempotent,
  content-based dedup against the canonical records on disk
  (`_find_existing_promoted_record`), re-checked fresh on every call —
  never the manifest's own bookkeeping field. §4.4/§4.8/§5.3 are
  rewritten to provide the equivalent guarantee for the new Evidence-
  writing branch, since no existing convention already does.
- **No existing code path creates a new Evidence record.** Grepped
  directly: `_next_id(sdir, "EV"` has zero matches anywhere in `src/
  codecompass/`. Every existing `apply_manifest` branch
  (`_apply_anchor_edit`/`_apply_candidate_addition`) only ever creates a
  new *Claim*. Phase 89's `"source_reconciliation"` branch is the first
  mechanized Evidence-creation path this codebase will have — stated
  plainly, not characterised as extending an existing pattern.
- **`classify_symbol`/`assess(run_checks=True)` cannot discover a check
  that no Evidence record has ever yet cited.** Traced directly against
  the real `CL-BFS-004`/`oracle-contract.yaml` records (§0.1.A): the
  `behavioural_risk` tier — the only tier `assess()`'s own
  `check_contributors` reads from (`change_impact.py:559-561`) — is only
  reached via `classify_symbol`'s own `test_evidence_check_id` bridge
  (line 371-394), built exclusively from Evidence records that already
  cite a resolvable `OracleResult`. A required check with **zero**
  citing Evidence (today's real state for `overlapping-account-
  patterns-no-double-count`) is invisible to this entire pathway. This
  pathway remains fully valid, unchanged, and still Phase 89's own
  primary mechanism for its *other*, already-working case — a source
  change to a scope that **already has** a test-Evidence bridge (e.g.
  `CL-BFS-001`/`CL-BFS-002`, both already bridged via `EV-BFS-002`/
  `EV-BFS-003`) — see §4.1/§6.2's "re-verification" scenario below.
- **No structural field links a specific oracle `check_id` to the
  specific Requirement/Claim it is pinned for, when more than one check
  shares one contract.** `oracle-contract.yaml`'s own `contract_id`
  (`scripts/check_contracts.py::check_contract_id_resolves`, line
  127-148) resolves to exactly one governing `REQ-` record **for the
  whole contract** (here, `REQ-BFS-001`) — not per-check. `REQ-BFS-002`
  governs the contract's *third* check, but nothing machine-checkable
  says so today; the only existing link is informal prose (`REQ-BFS-002.
  yaml`'s own statement happens to embed the literal string
  `"overlapping-account-patterns-no-double-count"`, which happens to
  equal that check's `check_id` — a convention, not a schema field,
  and not even used consistently: `CL-BFS-001`/`CL-BFS-002`'s own
  equivalent prose embeds the check's `scope` text, not its `check_id`).
  §4.2/§5.1 add one small, additive, optional field to close this
  specific, real gap.
- **`oracle.py`'s own `evaluate_result_precedence`** (line 865-929,
  re-read directly) already recomputes `test_input_digest` against
  `check.test_input_paths` (which already lists `tests/test_reports.py`)
  for an *existing* result, and already reports `INVALID` when it
  disagrees with what is currently on disk — this is the already-shipped
  mechanism for "an existing result's own test file changed under it,"
  genuinely distinct from "no result has ever existed for this check at
  all" (Task A's real scenario, §0.1.A). Phase 89 reuses the former
  unchanged for the re-verification scenario and adds the latter as a
  new, narrow, separate detector (§4.1/§5.1).

## 2. Objective

A real source or test change to a target repository (Ledgerkit) is
**detected**, the canonical knowledge it affects is **identified** and,
on explicit human approval, **reconciled** (new Evidence added, a
Claim's `evidence_support_state` updated — never silently overwritten),
and the documentation sections that depend on that knowledge are
correctly **invalidated and selectively regenerated** — while every
unrelated document, Claim, and previously accepted editorial change is
left untouched. A second genuine Ledgerkit development task then
measurably benefits from the knowledge reconciled during a first one.
Matches `planning/v2-roadmap.md`'s Phase 89 section and `decisions/0085`
§3 exactly; this plan operationalises it, corrects nothing in it.

## 3. Architecture

Two sibling detectors feed one shared manifest writer — not one
detector trying to cover both cases, since §0.1.A proves they are
genuinely different conditions with different evidence shapes:

```
Target repo source/test change (Ledgerkit, or any CodeCompass-indexed
project)
      │
      ├─────────────────────────────────────────────────────────┐
      ▼                                                           ▼
[NEW] detect_source_changes()                      [NEW] detect_newly_
  -- re-verification of an            coverable_checks()
  ALREADY test-Evidence-bridged         -- a required check (oracle-
  scope (e.g. CL-BFS-001/002 via        contract.yaml) with ZERO citing
  EV-BFS-002/003). For each               Evidence yet, whose own
  tracked source file: FIRST            check_reference test now
  cross-checks the graph's own          genuinely collects in
  recorded source_files.content_hash    repo_root (a `pytest
  against the LIVE on-disk hash         --collect-only` probe, never a
  (reusing oracle.sha256_file exactly   full run) -- i.e. a previously-
  as change_impact.resolve_changed_     uncovered, REQUIRED obligation
  range already does, §0.1.D) --        has just become coverable by a
  reports a distinct "stale_graph_      genuine new test. Resolves the
  index" finding and refuses to         check_id -> governing Claim via
  compare against the baseline at all   REQ-*.check_id (NEW, optional,
  if they disagree (never silently      additive Requirement field,
  trusting a graph not yet re-synced    §4.2/§5.1) -> REQ's own
  by that repo's own `codecompass       depends_on. This is Task A's own
  sync`). Only once confirmed fresh     real scenario (§0.1.A) --
  does it compare the graph's own       assess()'s existing
  content_hash against the persisted   behavioural_risk/
  per-slug baseline                     check_contributors pathway
  (source-baseline.toml, §5.2).         cannot reach an uncovered check,
  produces: list[(path,start,end)]      by construction (§1.2).
  candidate changed ranges              produces: list[(check_id,
      │                                 claim_id)] newly-coverable pairs
      ▼                                         │
change_impact.assess(changed=...,               ▼
  run_checks=True)  (Phase 83,          oracle.evaluate_check(...) run
  REUSED, UNCHANGED)                     directly (Phase 82, REUSED,
      │  produces: per-range            UNCHANGED) -- the check's own
      │  Claim/Requirement findings,     fresh OracleResult
      │  tiered no_recorded_
      │  relationship /
      │  relevant_no_coverage_link /
      │  behavioural_risk, and for
      │  behavioural_risk with a
      │  bridging check, a fresh
      │  CONFIRMED_REGRESSION /
      │  VERIFIED_SCOPE /
      │  VERIFICATION_GAP /
      │  INVALID_ASSESSMENT
      │  classification -- each
      │  additionally annotated
      │  (NEW, §4.3) with whether a
      │  historical PASS for this
      │  exact check_id existed
      │  BEFORE this fresh result
      │  (observed_outcomes, Phase
      │  83's own existing return
      │  data, unchanged) --
      │  distinguishing a genuine
      │  regression from a newly
      │  discovered failure, never
      │  relabelling Phase 83's own
      │  classification itself
      └─────────────────────┬─────────────────────┘
                             ▼
[NEW, narrow] write_source_reconciliation_manifest(...)
      — a new SIBLING WRITER function (mirroring the already-production
        write_doc_candidates_to_manifests exactly, §1.1's corrected
        inventory — not an extension of write_manifest itself). Takes
        findings from EITHER detector above, uniformly. ONE manifest
        item PER CLAIM (never per-finding): every CONFIRMED_REGRESSION/
        qualifying VERIFIED_SCOPE finding against the SAME Claim in one
        detection run is merged into that one item's own list of
        proposed new-Evidence citations, closing the self-conflict risk
        below by construction (never two pending items racing the same
        Claim's own hash). Each contributing finding carries its own
        oracle run's full identity (contract_id, check_id, run_id,
        raw_output_ref — §4.4/§5.3's new Evidence-identity mechanism).
        state="pending", decision="undecided" (Phase 81's existing
        3-stage review convention, REUSED)
      │
      ▼  (human sets decision: "accept"/"reject", exactly as today)
apply_manifest()   (Phase 81, REUSED — one new recognised `kind`, §5.3;
                     writes one new Evidence record PER contributing
                     finding, append-only, FIRST checking a new, narrow
                     Evidence-identity helper keyed on (contract_id,
                     check_id, run_id) — not _find_existing_promoted_
                     record, which is typed for claim/requirement
                     statement-text matching and cannot represent
                     Evidence identity at all (§0.1.B/§4.4) — so a crash
                     partway through a merged item's own multi-record
                     write is safe to retry without duplicating evidence
                     already written, exactly the same real guarantee
                     every existing _apply_* function already provides
                     for its own record kind, provided here for the
                     first time for Evidence specifically + a narrowly-
                     scoped, EXPLICITLY DISCLOSED deviation from this
                     flow's own "never mutate, always create a
                     competing record" convention: appends to the
                     Claim's own contradicting_evidence/
                     supporting_evidence fields ONLY (each append itself
                     idempotency-checked, §4.8) and RECOMPUTES
                     evidence_support_state from the Claim's own FULL,
                     accumulated contradicting_evidence/
                     supporting_evidence contents after the append —
                     never merely from this batch's own findings, so an
                     earlier batch's contradiction can never silently
                     disappear (§4.4/§4.7) — statement/derivation/
                     timestamp/every other field is never touched; see
                     §4.4 for why this specific, narrow exception is
                     justified rather than built around. Only ever runs
                     after explicit human "accept")
      │
      ▼  (the Claim's own file content hash has now genuinely changed)
detect_grounded_region_changes() → docs maintain → docs compile/publish
      (Phase 87, COMPLETELY UNCHANGED — already reacts correctly to any
       cited Claim's content hash changing, regardless of cause)
```

No new scheduler, event bus, knowledge store, or documentation
compiler. The one new module (`src/codecompass/source_reconciliation.py`,
§5) is two thin sibling detectors plus one shared new sibling manifest
writer plus one new `apply_manifest` branch; everything else in the
diagram above is Phase 81/82/83/87/84 code, unmodified.

## 4. Required planning decisions

### 4.1 How source/test changes are detected, identified, and compared
with known baselines

**Two genuinely different conditions (§0.1.A), two sibling detectors —
not one trying to cover both:**

**(a) `detect_source_changes(project_root, slug, *, repo_root)`
(§5.1) — re-verifying an already-covered scope.** For every `source`/
`test`-kind Evidence record under `slug` whose `source_ref`/`test_ref`
names a file under `repo_root`: **first**, confirm `repo_root`'s own
`context-graph.db` is actually fresh for that file — recompute the
*live* on-disk hash (`oracle.sha256_file`, reused directly, exactly the
function `change_impact.resolve_changed_range` already calls for this
same purpose) and compare it against the graph's own recorded
`source_files.content_hash`; a disagreement is reported as a distinct
`"stale_graph_index"` finding and that file is **excluded from this
run's comparison entirely** (never compared against the baseline using
a hash already known to be stale — §0.1.D). Only once confirmed fresh
is the graph's own `content_hash` compared against the hash persisted in
`source-baseline.toml` the last time this slug was reconciled. A file
with no baseline entry is reported `new` (first-ever reconciliation for
that file) and its baseline is *not* established by detection alone
(mirrors `detect_grounded_region_changes`'s own `"new"`-is-read-only
rule exactly — establishing a baseline is a separate, explicit act,
`establish_source_baseline`, never a side effect of looking). The
required order is therefore always: edit source/test → `codecompass
sync` (in `repo_root`) → `detect_source_changes` — stated explicitly as
a documented precondition, and fail-closed (a `"stale_graph_index"`
finding, never a silent false negative) when violated, rather than
trusted to always happen in that order. No `git diff` parsing — content-
hash comparison only, Phase 83's own already-established technique.
Feeds into `change_impact.assess(changed=..., run_checks=True)`
unchanged — valid for a scope **already** bridged by test-Evidence (e.g.
`CL-BFS-001`/`CL-BFS-002`), not for a never-yet-covered one (§0.1.A).

**(b) `detect_newly_coverable_checks(project_root, slug, *, repo_root)`
(§5.1) — a required check closing real coverage for the first time.**
**Detector-selection gate, corrected this round (§0.2.B) — three
distinct states, verified separately, not one collapsed condition:**
"no currently-valid historical `OracleResult`" (`scripts/
check_contracts.py`'s own `current_pass_check_ids` computation,
re-read directly, lines 290-300) is **true of two genuinely different
situations** — (i) a check that has never had any citing Evidence at
all, and (ii) a check that **does** already have a citing Evidence
record (detector (a)'s own scope) whose historical result has simply
gone stale or `INVALID` under `oracle.evaluate_result_precedence`
(`decisions/0088`'s own named, expected state — re-verified directly,
`scripts/check_contracts.py` lines 212-237). Gating detector (b) on
"currently-valid historical result" alone would wrongly also match (ii),
misrouting an already-bridged, already-Evidenced check away from
detector (a)'s own re-verification pathway. **The corrected gate**:
for every `required: true` check in the slug's own `oracle-contract.yaml`
with **zero existing `evidence_kind: "test"` Evidence record anywhere
under the slug whose `test_ref` resolves to a result for this exact
`check_id`** — the same bridge-presence test `classify_symbol`'s own
`test_evidence_check_id` (`change_impact.py:371-394`) already performs,
reused directly as the detector-selection gate itself, never
reinvented, and never substituted for "no currently-valid result": probe
whether `check.check_reference`'s named test now actually collects in
`repo_root` (`pytest --collect-only -q <check_reference>`, a new,
narrow use of the existing subprocess machinery `oracle.run_pytest_check`
already uses — a collection probe, never a run, so a collecting-but-
still-failing test is distinguished from a test that does not exist at
all; `pytest --collect-only` is **not** read-only in any strict sense —
it executes repository Python at module-import time, named explicitly
as a known, unmitigated risk in §4.10/§9 below). A check that now
collects is "newly coverable" — this is Task A's own real scenario
(§0.1.A, §6.1). **Deterministic precedence, now provably exhaustive and
mutually exclusive**: a required check either has at least one citing
test-kind Evidence record (detector (a)'s own exclusive scope,
regardless of whether that Evidence's own cited result is currently
valid, stale, or invalid — a stale/invalid case is detector (a)'s own
re-verification finding, reported via the existing, unchanged
`"stale_test_citation"` `find_gaps` kind, §1.1, never routed to detector
(b)) or it has none (detector (b)'s own exclusive scope, regardless of
whether any historical result file happens to exist for it at all — a
check could, in principle, have a `FAIL`-only result on disk with no
Evidence ever citing it; detector (b) still owns it, since "has Evidence"
and "has a result file" are different questions, and only the former
gates routing). A check cannot be in both states at once by this
corrected test, so the two detectors' own outputs never overlap or
need reconciling against each other — closing the original ambiguity
the fourth amendment's own gate left open.

### 4.2 How changes map to Claims/Requirements/Evidence/Decisions and
dependent documentation regions

**For detector (a) (an already-bridged scope)**: reused unchanged —
`change_impact.classify_symbol` (Claim/Requirement mapping, via existing
`source_ref`/`supporting_evidence` citations) and `detect_grounded_
region_changes` (documentation-region mapping, via existing `cited_ids`
grounding markers). No new mapping table for this case — both already
exist and already key off the same canonical record ids.

**For detector (b) (a newly-coverable, previously-uncovered required
check)**: `classify_symbol`'s own bridge cannot be used — that is
exactly what is missing (§0.1.A/§1.2). **One small, additive, optional
field** closes this, rather than a new mapping table or a prose-matching
heuristic: `check_id` on a Requirement record, naming the exact
`oracle-contract.yaml` `check_id` that Requirement pins (set once, by a
human, at the same moment a Decision pins a new required scope — e.g.
`REQ-BFS-002.yaml` would carry `check_id: overlapping-account-patterns-
no-double-count`, backfilled as a narrow, editorial, non-semantic
addition to an already-existing record, the same class of safe
bookkeeping addition §4.4 below already justifies for Evidence
citations). `detect_newly_coverable_checks` resolves `check_id` → every
Requirement naming it → that Requirement's own existing, unchanged
`depends_on` → the governing Claim(s) — three already-existing,
structural lookups chained together, with exactly one new field added
to make the first link machine-checkable instead of informal prose.
This field is optional and additive to the Requirement schema
(`knowledge_intermediate.py`'s requirement field table, §5.1) — a
Requirement naming no `check_id` is unaffected, and `contract_id`'s own
existing one-contract-to-one-REQ mapping (`scripts/check_contracts.py::
check_contract_id_resolves`) is untouched, continuing to answer a
different question (which Requirement a contract as a whole is *for*)
from the one `check_id` now answers (which Requirement a specific check
*within* that contract is for).

### 4.3 Distinguishing genuine staleness from unrelated changes, missing
evidence, newly-closed coverage, and contradictions

**For detector (a)**, reusing `change_impact`'s existing tiers with no
new semantics:
- **Unrelated**: `no_recorded_relationship` — no citing Evidence found
  for the changed symbol. Not reported as a reconciliation candidate.
- **Missing evidence**: `relevant_no_coverage_link` — a Claim cites the
  changed symbol but no test-kind Evidence bridges to a real check.
  Reported via the existing `relevant_no_coverage_link` gap-adjacent
  classification (unchanged) — a coverage gap, not staleness; Phase 89
  never fabricates a check to close this. (This is also exactly
  `CL-BFS-004`'s own current tier, §0.1.A — which is precisely why
  detector (a) can never be the mechanism that closes it; only detector
  (b) can.)
- **Genuine contradiction (real staleness)**: a `behavioural_risk`
  finding whose fresh, re-executed outcome is `CONFIRMED_REGRESSION`,
  **and** a historical `PASS` for this exact `check_id` is present in
  `AssuranceFinding.observed_outcomes` (Phase 83's own existing return
  data, read, never recomputed) — i.e. the checked behaviour genuinely
  used to pass and a fresh run now fails. This is the only tier this
  plan's own manifest ever proposes writing back as a **contradiction**
  (§4.4).
- **Newly discovered failure, not a regression (§0.1's semantic
  correction)**: a `CONFIRMED_REGRESSION` finding (Phase 83's own
  classification, left completely unmodified) whose `observed_outcomes`
  contains **no** historical `PASS` for this `check_id` — i.e. this
  check has never yet been confirmed passing at all; a fresh `FAIL` is
  real and still proposed as contradicting Evidence (the Claim it
  bears on genuinely is unconfirmed-or-worse), but the manifest item
  and the new `find_gaps` kind (§5.4) label it `"newly_discovered_
  failure"` rather than `"regression"`, so a human reviewer is never
  told something broke that was never shown to have worked. `change_
  impact.py` itself is not touched — this label is computed once, in
  `source_reconciliation.py`, from data `assess()` already returns.
- A fresh `VERIFICATION_GAP` (no fresh result yet) or `INVALID_
  ASSESSMENT` (the check itself errored) is reported as a finding but
  never proposed as a reconciliation, since neither establishes a real
  contradiction or confirmation.
- **Re-confirmation, not staleness**: a fresh `VERIFIED_SCOPE` against a
  Claim whose `evidence_support_state` was already `supported` is a
  no-op for reconciliation purposes (nothing contradicted, nothing to
  write) — but a fresh `VERIFIED_SCOPE` against a Claim previously
  `partially_supported`/`unconfirmed` (i.e. closing a real, previously
  recorded gap) **is** proposed, since that is new, materially useful
  evidence a human should be able to accept into the record.

**For detector (b)**: a "newly coverable" check that, once actually
executed (§5.1), evaluates `PASS` is proposed as new **supporting**
Evidence for the check's own governing Claim (via §4.2's `check_id`
bridge) — this is Task A's own real scenario (§6.1), genuinely new
knowledge, not a contradiction of anything. A "newly coverable" check
that evaluates `FAIL` on its first-ever real execution is reported via
the same `"newly_discovered_failure"` label immediately above (there
being, by definition, no historical `PASS` for a check detector (b)
only ever fires on in the first place) — proposed as contradicting
Evidence against the Claim, never silently discarded just because the
check is new.

### 4.4 How canonical knowledge is reconciled without silently
overwriting previously accepted facts

Only through the existing, append-only `apply_manifest` flow (§3's
diagram), extended with one new item `kind`.

**Result provenance (new this round, §0.2.A)**: a manifest item's own
cited `(contract_id, check_id, run_id, raw_output_ref)` identity now
always names an `OracleResult` that was independently persisted and
round-trip-verified at `verify-changes` time (§4.10 layer 4, before the
manifest item was ever written), never one reconstructed from
`AssuranceFinding`'s own summary fields — which structurally cannot
carry it (`change_impact.py:424-433`, no `run_id`/`raw_output_ref` field
exists on that dataclass at all). The mechanism: `change_impact.assess`/
`run_check_assurance` gain one new, additive, optional parameter,
`on_fresh_result: Callable[[str, OracleResult], None] | None = None`
(default `None`, every existing call site unaffected — there are none
in `src/` today outside `change_impact.py` itself, confirmed by direct
grep, so this is a safe, backward-compatible extension, not a behaviour
change for anything that exists), invoked with the real, fully-populated
`fresh_result` at the exact point `run_check_assurance` computes it
(`change_impact.py:445`), before it would otherwise be discarded on
return. `source_reconciliation.propose_reconciliation` (§5.1) is the
first and, for this phase, only caller that passes this parameter.
`apply_manifest`'s own new branch (§5.3) re-validates the cited result
against live contract/file state exactly as before — this provenance
fix changes *where the data comes from*, never *how it is
re-validated*.

**Evidence identity (rewritten this round, §0.1.B)**: a new Evidence
record's own identity for idempotency purposes is the tuple
`(contract_id, check_id, run_id)` — the oracle run that produced it,
never a prose-text match. `_find_existing_promoted_record` is **not**
used here and cannot be: it is typed to match `kind="claim"` (or
`"requirement"`) records against their own `statement` field; Evidence
records have no `statement` field, and there is no existing Evidence-
creation call site anywhere in this codebase to mirror (§1.2) — this is
new, stated plainly, not characterised as reuse of an existing pattern.
A new, narrow helper, `_find_existing_evidence_for_run(records, slug,
contract_id, check_id, run_id)`, scans the slug's existing `evidence_
kind="test"` records, resolves each one's `test_ref` to its cited
`OracleResult` (`oracle.parse_oracle_result`, unmodified — the same
parse `classify_symbol` already performs) and compares `run_id`
directly — an exact-identity check, not a content/statement match,
because two separate real runs of the same check can legitimately
produce byte-identical raw output while still being two distinct,
independently-citable runs (`decisions/0082` §C's own immutable
per-run naming already establishes this is expected, not an edge case
to collapse away). This is checked **before every individual Evidence
write** inside a merged item's own multi-finding apply (§5.3) — not
once per item — because (§0.1.B, newly discovered this round)
`apply_manifest`'s own per-item `state: "applied"` flag is buffered for
the whole manifest and only written to disk once the entire batch's
loop completes (`knowledge_intermediate.py:2542-2543`); a crash midway
through one merged item's own multiple internal writes is not covered
by that flag at all, exactly the same way a crash between two *separate*
existing items is already only ever safe because of each item's own
record-level dedup, never the manifest's own bookkeeping. The Claim-
side append (below) gets its own, second, independent idempotency
check for the identical reason — a crash can land between the Evidence
write and the Claim update, or between the Claim update and the next
finding's Evidence write, and each must be independently safe to retry.

**A disclosed, narrowly-scoped deviation, not a mischaracterisation
(corrected after independent review found the original draft's "reuse"
claim false)**: every existing `apply_manifest` item kind today
(`"anchor_edit"`, `"candidate_addition"`, `"doc_region_edit"`) follows
this project's own explicit, established convention — "a semantic edit
never overwrites the original record directly... it always creates a
new, competing candidate [record] instead" (`_apply_anchor_edit`'s own
docstring, `knowledge_intermediate.py`). That convention exists to
protect against *semantic reinterpretation*: a human or tool proposing
different *wording* for what a Claim asserts (its `statement`/
`derivation` fields) must never silently overwrite the original — a
reviewer must see the new wording as a distinct, competing proposal.
**This is deliberately not what a `"source_reconciliation"` item
does.** It never touches `statement`/`derivation`/`timestamp`/any
authored prose field. It writes a **new** Evidence record per
contributing finding (next available `EV-<slug>-NNN` id, via the
existing `_next_id` helper, unmodified, guarded by the identity check
above — itself fully consistent with the existing append-only
convention, no deviation needed there) citing the fresh oracle
`run_id`/`raw_output_ref`, and then, for the *same* existing Claim,
appends each new Evidence id to exactly one of `contradicting_evidence`/
`supporting_evidence` (guarded by its own idempotency check: skip the
append if that exact Evidence id is already present in the target
field) and **recomputes** `evidence_support_state` **in place** — from
the Claim's own full, post-append `contradicting_evidence`/
`supporting_evidence` contents, **never from only this batch's own new
findings** — so a contradiction accepted in an earlier batch can never
be silently dropped just because the current batch's own findings
happen to all be supporting (dispatch's own explicit "historical
contradictions must not silently disappear" requirement).

**Amended a fourth time (2026-11-16, same dispatch, after a fresh
independent re-review found two new, concrete defects in the
recomputation rule stated immediately below in the second/third
amendments — `planning/retros/_review-phase89-plan.md`, "Re-review
(second amendment round)"): the rule itself is corrected in place.**
Blocking Finding 1: `"contradicted"` is not a valid `evidence_support_
state` value — verified directly against `scripts/check_knowledge_
base.py`'s own `_OPTIONAL_ENUM_FIELDS["claim"]["evidence_support_
state"]` (line 209-214), the real, closed, already-enforced set is
`{"supported", "partially_supported", "unsupported", "conflicting"}`;
`"contradicted"` is a `status`-field value (`_STATUS_ENUMS["claim"]`,
line 170), never an `evidence_support_state` one. Blocking Finding 2:
the rule as previously stated read *only* this one Claim's own fields
(correct, and still true below) but its one worked application (§6.1)
reasoned about "every required contract scope... across sibling
Claims" — a cross-Claim notion the rule itself never licenses and that
names no actual, implementable grouping mechanism anywhere in this
codebase. Independently falsified against this project's own
pre-existing ground truth: `CL-BFS-001.yaml`/`CL-BFS-002.yaml` are
*already* `evidence_support_state: supported` today, each citing only
**one** of the contract's three required checks' own evidence —
neither covers "every required contract scope," so a literal
whole-contract reading would incorrectly recompute `"partially_
supported"` for either, were it ever re-run against them. `CL-BFS-003.
yaml`/`CL-BFS-005.yaml` are confirmed to be this project's own existing,
*separate*, dedicated records for the distinct "every required check in
the whole contract is satisfied" assertion (`CL-BFS-003`:
`status: superseded`; `CL-BFS-005`: `evidence_support_state:
partially_supported`, explicitly because it covers only two of the
contract's now-three required checks) — confirming "this one scope is
covered" and "the whole contract is covered" are two genuinely
different, already-existing notions in this exact knowledge base, not
one the corrected rule below needs to unify: this plan's own new write
path (§4.1(a)/§4.1(b)/§5.1, both detectors) only ever resolves to a
single-check-scoped Claim like `CL-BFS-004` (via the new `check_id` →
`REQ.depends_on` chain, §4.2, which by construction names exactly one
check per Requirement) — it never reaches a whole-contract-scoped Claim
like `CL-BFS-003`/`CL-BFS-005` at all, since no Requirement naming such
a Claim in its own `depends_on` will ever carry a single `check_id`
(confirmed: `REQ-BFS-001`, which `CL-BFS-001`/`CL-BFS-002`/`CL-BFS-003`
all `depends_on`, is itself a *two-check* requirement by its own
statement — it could never meaningfully carry one `check_id` either).
**The corrected rule, scoped correctly to a single-check Claim, the
only kind this mechanism ever writes to**: non-empty
`contradicting_evidence` and non-empty `supporting_evidence` both ⇒
`"conflicting"`; non-empty `contradicting_evidence` alone, empty
`supporting_evidence` ⇒ `"unsupported"` (fixing Finding 1); empty
`contradicting_evidence`, and `supporting_evidence` contains at least
one `evidence_kind: "test"` record ⇒ `"supported"` (fixing Finding 2 —
a purely local, single-Claim test, no cross-Claim reasoning); empty
`contradicting_evidence`, `supporting_evidence` non-empty but every
cited record is `evidence_kind: "source"` (relevance established,
behavioural coverage not yet — exactly `CL-BFS-004`'s own real,
pre-Task-A state) ⇒ `"partially_supported"`; both fields empty ⇒
`"unsupported"`. Directly validated against every real record this
mechanism can actually reach: `CL-BFS-001`/`CL-BFS-002` (test-kind
Evidence present ⇒ `"supported"`, matching their real current state);
`CL-BFS-004` before Task A (`EV-BFS-001` only, source-kind ⇒
`"partially_supported"`, matching its real current state); `CL-BFS-004`
after Task A (`EV-BFS-004` added, test-kind, `PASS` ⇒ `"supported"`,
§6.1's own intended result, now reached by a sound, implementable,
single-Claim rule rather than an undefined cross-Claim one).

**Scope of this rule, named explicitly (fourth-review-round non-blocking
observation (c), folded in rather than deferred)**: the two-branch
partition above over `supporting_evidence`'s own evidence-kind
composition (contains a `test`-kind record vs. every record is
`source`-kind) is sound for exactly the Claims this mechanism can ever
actually reach — those bridged via an oracle-contract-governed
`check_id`/`classify_symbol` path — and is **not** claimed as a
general-purpose `evidence_support_state` convention beyond that. This
project's own `evidence_kind` taxonomy has three further real values in
active use (`documentation`, `executable`, `behavioural` — confirmed by
direct grep, `planning/knowledge/first-party-source-symbols/` uses all
three for Claims this rule's two branches do not cover), and at least
one real, pre-existing Claim in that other slug (`CL-FPSS-008`, source-
kind Evidence only, already `evidence_support_state: supported`) would
be mis-recomputed if this rule were ever applied to it. This never
happens: `first-party-source-symbols` has no `oracle-contract.yaml`
(`planning/contracts/` contains exactly one subdirectory,
`balance-from-spec`), and `change_impact.assess()` short-circuits
before ever calling `classify_symbol` when a slug has no contract
(`change_impact.py:510-546`) — so this rule is structurally confined,
by the same contract-gating every other part of this mechanism already
requires, to Claims it is actually sound for. Stated here so a future
reader never lifts this rule out of context and applies it as a
general `evidence_support_state` convention for an uncontracted slug.

This is new,
previously-unmechanized behaviour for this codebase (no existing
apply-path function does this — confirmed directly, §1.2) and this
plan states that plainly rather than citing a non-existent precedent.
It is justified, not merely asserted, on a narrower ground than "reuse":
humans already make exactly this edit by hand today, routinely and
without controversy, whenever new evidence for an existing Claim
arrives (e.g. `CL-BFS-004.yaml`'s own `evidence_support_state:
partially_supported` field was itself set this way, by a human, outside
any tool) — a citation-list/derived-status update is bookkeeping this
project's own authors already treat as safe to make directly, never a
reinterpretation of what the Claim asserts. Phase 89 mechanizes an
already-accepted human editing pattern; it does not invent a new class
of record mutation this project has never tolerated. Every item starts
`decision: "undecided"`; only a human-set `"accept"` causes
`apply_manifest` to write anything, and `apply_manifest` re-validates
every cited fresh result against the live contract (re-running nothing,
just re-checking file state) before writing, exactly as it already does
for `"anchor_edit"` items — never trusting the manifest's own say-so.
The self-conflict risk this deviation would otherwise create (§4.8) is
closed at the source, by construction: §3's writer merges every finding
against the *same* Claim into that Claim's own single manifest item, so
`apply_manifest` never processes two pending items racing the same
Claim's own content hash within one run.

### 4.5 How generated documentation is invalidated and selectively
regenerated

Entirely by the existing, unmodified §1.1 cascade: once §4.4's apply
step changes a Claim's file content, `detect_grounded_region_changes`
reports `claims_changed` for every region citing it (and only those
regions — an unrelated region's own cited Claims are untouched, so its
case is `noop`); `docs maintain` writes the resulting `doc_region_edit`
manifest items; `docs compile`/`publish` regenerate only those specific
sections, through the existing citation-scope/review/publish gates
(semantic + editorial review, hash-bound publish, publication-lock),
all completely unchanged. Phase 89 contributes no code to this half at
all — it only ever gets a Claim's file to change, correctly and with
provenance, for a new kind of reason.

### 4.6 Preserving user-approved editorial changes, unrelated regions,
and manually maintained content

Guaranteed by §4.5's reuse: a `concurrent_conflict`/`doc_candidate`
region (a prior human edit) is still refused from automatic
regeneration by `docs maintain`'s own existing, unmodified refusal rule
— this plan introduces no new write path that could bypass it. A
manually maintained (non-schema-governed) document is never discovered
by `docs maintain` at all (unchanged discovery scope) and is therefore
categorically unreachable by this entire reconciliation chain.

### 4.7 Provenance, version identity, conflict states, reproducibility

Every new artefact (the source baseline file, the new manifest kind,
the new Evidence record(s), the one new `check_id` field on a
Requirement) carries the same provenance conventions already
established elsewhere in this project — a full `(contract_id, check_id,
run_id)` identity plus `raw_output_ref` for every triggering oracle
result (Phase 82's existing `OracleResult` schema, unmodified — §4.4's
own Evidence-identity mechanism reads exactly these fields, never a
narrower subset), the target repo's own git HEAD via the same
`_git_head_revision`-style helper `knowledge_api.py` already uses
(Phase 88's own pattern, reused independently of MCP), and the
manifest's own `manifest_id`/`created` fields (Phase 81's existing
convention, unmodified format). No new provenance scheme.

### 4.8 Behaviour after interrupted, repeated, ambiguous, or conflicting
reconciliation attempts

- **Interrupted**: the source baseline only advances
  (`advance_source_baseline_after_apply`, mirroring `advance_region_
  baseline_after_publish`'s own "only after the write itself actually
  succeeds" rule, `CLAUDE.md` §1's L-087) after `apply_manifest` reports
  a real, successful write for every accepted item in the batch — a
  crash or partial failure mid-apply leaves the baseline exactly where
  it was, so a re-run of detection reports the same findings again
  rather than silently treating an unfinished reconciliation as done.
  **Item-internal partial write — rewritten this round (§0.1.B): this is
  not a narrow edge case solved by reusing `_find_existing_promoted_
  record`, which cannot represent Evidence identity at all (no
  `statement` field), and relying on the manifest's own `state:
  "applied"` flag is not a safety net either — that flag is buffered
  for the *whole batch* and only ever written to disk once, after the
  entire item loop completes (`knowledge_intermediate.py:2542-2543`,
  §0.1.B) — so a crash can lose that flag's own update for an item that
  already fully, successfully applied earlier in the very same run, not
  only for a merged item's own internal multi-write.** The real
  guarantee (§4.4) is two independent, content-based re-checks against
  the canonical records on disk themselves, run on every attempt
  regardless of what the manifest's own bookkeeping claims: (1) before
  writing a new Evidence record for a contributing finding,
  `_find_existing_evidence_for_run` (§4.4, new) checks whether an
  Evidence record already exists citing this exact `(contract_id,
  check_id, run_id)`, skipping the write if found; (2) before appending
  an Evidence id to the target Claim's `contradicting_evidence`/
  `supporting_evidence` field, the apply step checks whether that exact
  id is already present, skipping the append if found. Together these
  make every one of a merged item's own internal writes independently
  safe to retry, in any order of partial completion, with or without
  the manifest's own `state` flag having been persisted at all.
- **Repeated**: re-running detection against an already-pending,
  unresolved manifest item reports the same findings again (by design —
  detection is read-only, §4.1) rather than silently suppressing them; a
  *second* `write_source_reconciliation_manifest` call for a check/run
  already named in an existing pending item does not create a duplicate
  manifest entry, mirroring `docs maintain`'s own existing idempotency
  guarantee for `doc_region_edit` items.
- **Ambiguous, across different Claims** (a changed symbol maps to more
  than one *distinct* Claim): every distinct Claim gets its own,
  independently-decided manifest item — this plan never collapses
  findings against different Claims into one silent resolution.
- **Ambiguous, against the SAME Claim** (a Claim maps to more than one
  behavioural_risk check, with agreeing or disagreeing fresh outcomes):
  deliberately **not** reported as separate items — §3/§4.4's writer
  merges every finding against one Claim into that Claim's own single
  manifest item (listing each contributing check/run_id), closing by
  construction the self-conflict risk an original draft of this plan
  left open (independent review, Blocking Finding 1's second part):
  two items racing the same Claim's own content hash within one
  `apply_manifest` batch could otherwise spuriously trip the reused
  whole-file-hash conflict check against each other, not only against a
  genuine human edit. One Claim, one item, one hash check, by
  construction — no race is possible. **Disagreeing-outcomes case,
  found by independent re-review (non-blocking, resolved here rather
  than left open)**: when a merged item's own contributing findings
  disagree (one `CONFIRMED_REGRESSION`, one qualifying `VERIFIED_SCOPE`,
  against the same Claim in the same batch), the apply step (§5.3)
  writes to **both** `contradicting_evidence` and `supporting_evidence`
  and sets `evidence_support_state` to the existing, already-used
  `"conflicting"` value (`knowledge_intermediate.py:1211-1214`, the same
  value that already feeds the existing CONTESTED classification
  elsewhere in this codebase) — reused, not invented, for exactly the
  case it already exists to name. A merged item is never silently
  resolved toward whichever outcome happens to be listed first.
- **Conflicting** (a human has directly hand-edited the same Claim's
  file between detection and apply): `apply_manifest`'s existing
  re-validation (unchanged) already detects this the same way it
  already detects a concurrent `"anchor_edit"` conflict — reported, not
  silently overwritten. This is now the *only* way a `"source_
  reconciliation"` item's conflict check can genuinely fire, since the
  bullet above already closes the self-inflicted version of the same
  symptom.

### 4.9 Deterministic vs. judgement vs. human-approval operations

- **Deterministic**: content-hash comparison (§4.1), graph-freshness
  cross-check (§4.1/§5.1), the `pytest --collect-only` coverability
  probe (§5.1 — collects or does not, no judgement involved), symbol/
  Claim mapping (§4.2), tier classification (§4.3), fresh check
  execution and its own outcome (reused, unmodified Phase 82/83 code),
  the `evidence_support_state` recomputation (§4.4 — a pure function of
  the Claim's own accumulated citation fields, never a choice).
- **Requires human judgement, surfaced not resolved**: whether an
  ambiguous multi-Claim/multi-check finding should be split, merged, or
  deferred — this plan reports every such case explicitly rather than
  guessing; which second Ledgerkit task genuinely exercises Task A's
  reconciled knowledge (§6.3, pre-registered by a human before Task A
  runs).
- **Requires explicit human approval before any write**: every single
  `"source_reconciliation"` manifest item's `decision` field (§4.4) —
  there is no `--yes`/auto-accept mode in this plan's own MVP scope
  (named explicitly as a non-goal, §10); the one-time `check_id`
  backfill onto a Requirement record (§4.2/§5.1) is itself always a
  human edit, never written by any tool this plan introduces.

### 4.10 Modularity and CLI/API callability, independent of MCP

**Corrected this round (§0.2.E)**: the prior single `detect-changes`
command was described as read-only while its own design already called
`change_impact.assess(run_checks=True)` — a real `pytest`-executing,
file-writing operation (`oracle.py:746-784`, unconditional once reached,
never an opt-in the caller controls) — not an inspection. Dispatch §2.E
requires five separately-named layers, each with its own minimal,
stated side-effect boundary; the command surface below provides exactly
those five, as two CLI commands (not five) because layers 3-4 are never
meaningfully separable in practice (a verification run's own fresh
result is either persisted immediately, with its own integrity re-check,
or it is not persisted at all — there is no safe intermediate state to
expose as its own command) and layer 5 already exists:

1. **Observation of file, baseline and graph state** —
   `codecompass knowledge detect-changes SLUG --repo-root PATH [--json]`
   (new). Genuinely read-only: for detector (a), the graph-freshness
   cross-check (§4.1(a)) and the baseline-vs-graph `content_hash`
   comparison only — **never** calls `change_impact.assess(...)`, with
   or without `run_checks`, since even `run_checks=False` would still
   invoke `classify_symbol` against live records, a correctness-neutral
   but unnecessary coupling this layer avoids entirely by calling
   neither. For detector (b), scans `oracle-contract.yaml` and existing
   Evidence records only (the corrected gate, §0.2.B/§4.1(b)) — **no**
   `pytest --collect-only` probe at this layer. Spawns zero subprocesses
   and writes zero files; a regression test (§7) asserts this directly
   (no `subprocess`/`pytest` invocation observed, no file created under
   `results/`, `reconciliation/`, or `scratch-assessments/`) for both
   detectors, on every code path including the one that finds candidate
   findings.
2. **Optional test-collection probes** — `codecompass knowledge
   detect-changes SLUG --repo-root PATH --probe-coverage` (new flag on
   the same command). Adds detector (b)'s own `pytest --collect-only`
   step (§4.1(b)/§5.1) for every check layer 1 found with no citing
   Evidence. Still writes no result/manifest file — a probe's own exit
   code is reported, never persisted as a finding about the check's
   outcome. Explicitly **not** a sandbox: `pytest --collect-only`
   executes `conftest.py` and module-level repository code at import
   time (§0.2.E, §9) — this flag's own help text and this plan's §9 both
   name this acknowledged, unmitigated risk plainly, never implying
   collection is safe merely because it does not run test bodies.
3. **Explicitly authorised verification execution** +
   4. **`OracleResult` persistence and reconciliation-manifest
   creation** — `codecompass knowledge verify-changes SLUG --repo-root
   PATH [--json]` (new, separate command — never implied by, or a flag
   on, `detect-changes`). Re-runs layer 1's own observation (never
   trusting a prior `detect-changes` call's own output as current), then:
   for detector (a)'s findings, calls `change_impact.assess(changed=...,
   run_checks=True, on_fresh_result=...)` (§4.4/§5.1's new, additive,
   opt-in capture parameter, §0.2.A) — a real `pytest` execution, named
   as such; for detector (b)'s findings (re-probed fresh at this layer,
   never reusing a stale layer-2 result), calls `oracle.evaluate_check`
   directly — also a real `pytest` execution. For every fresh
   `OracleResult` captured, immediately (§5.1/§5.3): persists it via
   `oracle.write_oracle_result` to the slug's own `results/` directory
   (the same directory existing committed results already live in,
   `decisions/0082`'s own immutable per-run naming applying unchanged),
   then round-trips it (`oracle.parse_oracle_result` + `oracle.
   evaluate_result_precedence` against the just-written path) to confirm
   the persisted YAML and its referenced raw-output file are both
   genuinely intact and agree with the in-memory result that produced
   them (dispatch requirement 4) — a disagreement is a persistence-
   integrity failure, reported and **not** carried forward into a
   manifest item (fail-closed: never propose a reconciliation referencing
   a result that cannot be independently re-read from disk, dispatch's
   own "do not generate Evidence referencing a result that exists only
   in memory" requirement, extended here to the manifest-item stage
   since Evidence itself is not constructed until apply time). Only once
   persistence is confirmed does `write_source_reconciliation_manifest`
   (§5.3) write the manifest item, `state="pending"`,
   `decision="undecided"` — exactly as today.
5. **Separately approved canonical knowledge mutation** —
   `codecompass knowledge apply MANIFEST_PATH` — **already exists**
   (Phase 81/84); recognises the new `"source_reconciliation"` `kind`
   automatically once §5.3 adds it to `apply_manifest`'s own dispatch,
   no new CLI surface needed here at all. This remains the *only*
   command in this entire chain that ever writes a new Evidence record
   or mutates a Claim's own fields, and only ever on a human-set
   `decision: "accept"`, unchanged.

Every one of these is a plain, synchronous library call
(`src/codecompass/source_reconciliation.py` + `knowledge_intermediate.
apply_manifest`) — callable from a script, a test, or a future MCP tool
exactly the same way `knowledge_api`'s existing functions already are,
with no MCP dependency anywhere in the import graph. Not a new top-level
command, not an MCP tool (`decisions/0085` §3's own exclusion,
re-confirmed) — `detect-changes` (now layers 1-2) and `verify-changes`
(layers 3-4) are the only genuinely new CLI surface this plan adds.

## 5. New primitives (genuinely missing, narrowly scoped)

### 5.1 `src/codecompass/source_reconciliation.py` (new module)

**Two sibling detectors (§0.1.A, §4.1) — never one trying to cover
both:**

- `detect_source_changes(project_root, slug, *, repo_root) ->
  list[SourceChangeFinding]` — §4.1(a)'s baseline-diff detector, for
  an **already** test-Evidence-bridged scope. For each tracked source/
  test file: **first**, `_check_graph_index_fresh(repo_root, path)`
  (new, narrow — recomputes `oracle.sha256_file(repo_root / path)` and
  compares it against the graph's own recorded `source_files.
  content_hash`, exactly the comparison `change_impact.resolve_
  changed_range` already performs for the identical purpose) — a
  disagreement is reported as `"stale_graph_index"` and that file is
  excluded from this run, never silently compared against the baseline
  using a value already known to be stale (§0.1.D). Only once confirmed
  fresh does it read `source-baseline.toml` via the existing `_read_
  simple_toml_tables` (imported from `knowledge_intermediate`, not
  duplicated) and compare the graph's own `content_hash` against the
  persisted baseline; for each drifted file, resolves a `changed[path:
  start-end]` range (the file's own full line range if no finer-grained
  range is recorded — Phase 83's own existing line-range convention)
  and returns it, annotated with the record(s) that cite it.
- `detect_newly_coverable_checks(project_root, slug, *, repo_root) ->
  list[NewlyCoverableCheck]` — §4.1(b)'s new detector, for a **never
  yet covered** required check (Task A's own real scenario, §0.1.A).
  **Gate corrected this round (§0.2.B)**: for every `required: true`
  check in the slug's `oracle-contract.yaml` with **zero existing
  `evidence_kind: "test"` Evidence record whose `test_ref` resolves to
  a result for this `check_id`** — the same bridge-presence test
  `classify_symbol`'s own `test_evidence_check_id` already performs
  (`change_impact.py:371-394`), reused as the gate itself, **never**
  "no currently-valid historical `OracleResult`" (`current_pass_check_
  ids`-style — that condition is also true of a previously-covered check
  whose result has simply gone stale, detector (a)'s own scope, not this
  detector's; §0.2.B/§4.1(b)): probes `pytest --collect-only -q <check.
  check_reference>` against `repo_root` (new use of the subprocess
  pattern `oracle.run_pytest_check` already establishes — a collection
  probe, zero test execution, so an exit code of `0` means only "this
  node id now resolves to a real test," never anything about its
  outcome; **not** read-only in a strict sense — collection executes
  repository Python at import time, §4.10/§9). A check that now collects
  is returned,
  resolved to its governing Claim(s) via the new `check_id` → `REQ.
  check_id` → `REQ.depends_on` chain (§4.2/below). **Fail-closed guard
  (fourth review round's non-blocking observation (e), folded in as a
  mechanism requirement, not left as an ADR-only note)**: before
  resolving, confirms the matching Requirement's own `depends_on` has
  length exactly 1 — nothing in `check_knowledge_base.py` otherwise
  stops a human from mistakenly adding `check_id` to a multi-check
  Requirement (e.g. `REQ-BFS-001`), which would silently resolve to
  every one of its `depends_on` Claims at once, including a
  whole-contract-scoped one `check_id` was never meant to reach. A
  `depends_on` of length other than 1 on a `check_id`-bearing
  Requirement is reported as a configuration error (never silently
  proceeding against multiple Claims).
- `propose_reconciliation(project_root, slug, findings, *, repo_root,
  knowledge_root) -> Path | None` — called only from `verify-changes`
  (§4.10 layers 3-4), never from `detect-changes` (layers 1-2). For
  detector (a)'s findings: calls `change_impact.assess(changed=[f.range
  for f in findings], run_checks=True, on_fresh_result=_capture, ...)`
  (Phase 83's own signature, extended this round with one new, additive,
  opt-in parameter, §0.2.A/§4.4 — the one real existing caller of
  `assess()`, `mcp/tools.py:342`, neither passes this parameter nor
  reaches the code path that would invoke it (`run_checks=False`
  there), so it is unaffected on both counts, §0.2.A; `_capture` is a
  local closure **accumulating** each real `OracleResult` it receives
  into a `list[OracleResult]` keyed by `check_id` — never overwriting —
  because `assess()`'s own `run_check_assurance` loop runs once per
  `(range, check_id)` pair, not once per `check_id` globally
  (`change_impact.py:526-578`), so the same `check_id` can legitimately
  be captured more than once in one call if it is contributed by more
  than one range), re-walks `assess()`'s own returned `range_reports[].
  symbol_classifications[].claims[]` (each `ClaimFinding` already carries
  `check_id`, and each `range_reports[]` entry's own list index is the
  finding's own range index) to recover the claim↔check link, and for
  each `CONFIRMED_REGRESSION`/qualifying `VERIFIED_SCOPE` finding: looks
  up its own real, captured `OracleResult` by `(range index, check_id)`
  — consuming the matching entry from `_capture`'s own per-`check_id`
  list in range order, never by `check_id` alone, which would
  mismatch a finding to the wrong range's own run once more than one
  range contributes the same `check_id` (never reconstructed from
  `AssuranceFinding`'s own summary fields, which structurally cannot
  carry it, §0.2.A — dispatch requirement 5), then
  **persists it** (`oracle.write_oracle_result`, §4.10 layer 4) and
  round-trip-verifies the write (§4.10) *before* this finding is ever
  included in anything passed to `write_source_reconciliation_manifest`
  below; also annotates it with whether a historical `PASS` for that
  `check_id` already existed before this fresh result
  (`AssuranceFinding.observed_outcomes`, read not recomputed — §4.3's
  "newly discovered failure" distinction). For detector (b)'s findings:
  calls `oracle.evaluate_check` directly (Phase 82, unmodified) against
  each newly-coverable check — this is the one point in this whole
  module where a check is executed for a reason *other than* re-walking
  an existing `assess()` call, because detector (b)'s own findings, by
  definition, have no existing `assess()`-reachable bridge to re-walk
  (§0.1.A) — its own returned `OracleResult` is persisted and
  round-trip-verified the identical way. Both detectors' own findings
  are then grouped by `claim_id` (§4.8's "ambiguous, same Claim" rule —
  never one item per finding, always one item per distinct Claim) and
  passed, uniformly, to `write_source_reconciliation_manifest` (§5.3, a
  new **sibling writer function**, mirroring the real, already-production
  `write_doc_candidates_to_manifests` exactly, §1.1's corrected
  inventory; `write_manifest` itself is left untouched).
- `establish_source_baseline(...)` /
  `advance_source_baseline_after_apply(...)` — mirror
  `establish_new_region_baselines`/`advance_region_baseline_after_publish`
  exactly (§4.8). A file reported `new` (no baseline entry, detector
  (a)) and a check reported newly-coverable (detector (b)) are both
  read-only findings on their own — neither establishes or advances any
  baseline as a side effect of being observed (`CLAUDE.md` §1 L-087).
- **One small, additive, optional field on the Requirement record
  schema**: `check_id` (§4.2) — added to `knowledge_intermediate.py`'s
  existing requirement field table alongside `decision`/`depends_on`,
  optional, defaulting to absent for every existing Requirement that
  does not name one. `REQ-BFS-002.yaml` is backfilled with `check_id:
  overlapping-account-patterns-no-double-count` as part of this stage's
  own deliverables — a narrow, editorial, non-semantic addition to an
  already-existing record (the statement/derivation/every other field
  is untouched), the same class of safe bookkeeping change §4.4 already
  justifies for Evidence citations.

### 5.2 `source-baseline.toml` (new, per-slug persisted file)

`planning/knowledge/<slug>/reconciliation/source-baseline.toml` — same
directory Phase 81's manifests already live in, same TOML read/write
helpers, a sibling format to `.grounding-state.toml`
(`{path: {content_hash: str, last_reconciled: iso8601}}`). Not a
canonical record; not committed-knowledge content — exactly the same
classification `.grounding-state.toml` already has. A file present in
the baseline but now absent on disk (deleted/renamed) is reported as
its own distinct finding, `"deleted"` — never silently dropped from the
baseline and never conflated with `"new"` (the opposite condition). A
file outside `oracle-contract.yaml`'s own `tested_paths`/
`test_input_paths`/Evidence `source_ref`/`test_ref` set is never
tracked at all (no baseline entry is ever created for it) — this
detector's own scope is exactly the files this slug's existing records
already name, never a repository-wide scan. The graph-freshness check
(§5.1) is always evaluated before baseline comparison, per file, never
once for the whole repository — a graph that is fresh for one tracked
file and stale for another (a partial `sync`) must not let the stale
one's comparison borrow the fresh one's result.

### 5.3 `write_source_reconciliation_manifest` (new sibling writer),
`_find_existing_evidence_for_run` (new Evidence-identity helper), and
one new `apply_manifest` item kind: `"source_reconciliation"`

`write_source_reconciliation_manifest(project_root, slug, findings_by_
claim)` — a new function in `source_reconciliation.py`, structurally
mirroring the real, already-production `write_doc_candidates_to_
manifests` (called from `docs maintain`, §1.1's corrected inventory),
not an addition to `write_manifest` itself. One item per **Claim**
(§4.8), each listing every contributing finding's own full `(contract_
id, check_id, run_id, raw_output_ref)` identity, its `"newly_discovered_
failure"`/`"regression"`/`"newly_covered"` label (§4.3), and target
`contradicting_evidence` vs. `supporting_evidence` field,
`state="pending"`, `decision="undecided"`.

`_find_existing_evidence_for_run(records, contract_id, check_id, run_id)
-> str | None` (§4.4, new, in `knowledge_intermediate.py` alongside
`_find_existing_promoted_record` as a sibling, not a replacement) —
scans existing `evidence_kind="test"` records, resolves each one's
`test_ref` to its cited `OracleResult` (`oracle.parse_oracle_result`,
unmodified) and returns the first whose `(contract_id, check_id,
run_id)` matches exactly, or `None`. This is the genuinely new
Evidence-identity mechanism §0.1.B's finding requires — stated plainly
as new, not a parameterisation of the existing, differently-typed
helper.

A small, additive change to `knowledge_intermediate.apply_manifest`'s
existing dispatch (currently `"anchor_edit"` / `"candidate_addition"` /
`"doc_region_edit"`, §1.1's corrected inventory) — a new `elif
item["kind"] == "source_reconciliation":` branch that, on `decision ==
"accept"`: (a) re-validates every cited fresh oracle result still
parses and still belongs to the named contract/check (reusing `oracle.
parse_oracle_result` + the same contract-identity checks `classify_
symbol` already applies — never trusting the manifest's own cached
fields); (b) for each contributing finding, in order, **first** calls
`_find_existing_evidence_for_run` — if it already returns an id, this
finding's own Evidence write is skipped (already applied, safe retry);
otherwise writes one new Evidence record via the existing `_write_
record`/`_next_id` helpers, unmodified (fully consistent with this
project's own append-only convention); (c) for each newly-written **or**
already-existing Evidence id from (b), checks whether it is already
present in the target Claim's `contradicting_evidence`/`supporting_
evidence` field before appending — a second, independent idempotency
check, since (b) and (c) can each independently have already completed
or not on a prior crashed attempt (§0.1.B/§4.4/§4.8); (d) **the one
disclosed, narrowly-scoped deviation named in §4.4**: after every
contributing finding's own append (if any) is applied, **recomputes**
`evidence_support_state` from the Claim's own full, post-append
`contradicting_evidence`/`supporting_evidence` contents (§4.4's exact
rule — never from this batch's findings alone). The Claim's own
`statement`/`derivation`/every other field is never touched, and (per
§4.8) this is always the *only* pending item for this Claim in this
batch, so the existing whole-file-hash conflict check, re-run once
immediately before this write, can only ever genuinely fire against a
real, independent human edit — never against this item's own sibling.
On `decision == "reject"`: no write, item state becomes `"rejected"`,
mirroring the existing `"anchor_edit"` reject path exactly.

### 5.4 One new `find_gaps` gap kind: `"claim_contradicted_by_fresh_check"`

A Claim with a *pending, unapplied* `"source_reconciliation"` manifest
item proposing contradicting Evidence against it (labelled, per §4.3,
either `"regression"` — a historical `PASS` for that check existed
before the fresh `FAIL` — or `"newly_discovered_failure"` — it did not)
is reported by `find_gaps` as this new gap kind, carrying that label —
surfacing "this canonical fact is believed true but a fresh check
already disagrees and nobody has reviewed it yet," and *which* of the
two it is, without requiring a caller to separately know to go look in
`reconciliation/*.toml`. Reuses the existing `Gap` dataclass and `find_
gaps`'s existing scan loop/response shape verbatim; the label is a new
field on the `Gap` payload, additive, never a change to an existing
`Gap` kind's own shape.

## 6. Two-task Ledgerkit evaluation (the real-world exit gate)

Runs against **disposable scratch copies** by default (§6.4) — matching
Phase 88's own already-established, pre-authorised convention and this
dispatch's own instruction to distinguish evidentiary strength by
authorisation level, never assuming it.

### 6.1 Task A — a genuine development change produces new/changed
knowledge (source-verified walkthrough, rewritten this round — §0.1.A)

Reuse the exact, real, already-identified Ledgerkit gap this project's
own knowledge already names: `ledgerkit/reports.py::balance_from_spec`'s
`overlapping-account-patterns-no-double-count` scope (`REQ-BFS-002`/
`DEC-BFS-002`/`CL-BFS-004`/`EV-BFS-001`). This is **detector (b)'s own
scenario** (§4.1/§5.1), traced here concretely, input by input:

1. **Starting state (real, re-read this round)**: `CL-BFS-004.yaml`:
   `supporting_evidence: [EV-BFS-001]`, `contradicting_evidence: []`,
   `evidence_support_state: partially_supported`. `REQ-BFS-002.yaml`:
   no `check_id` field yet. `oracle-contract.yaml`'s third check,
   `overlapping-account-patterns-no-double-count`, `required: true`,
   `check_reference: tests/test_reports.py::TestBalanceFromSpec::
   test_section_accounts_overlapping_patterns_no_double_count` — no
   result file for this `check_id` exists anywhere under `planning/
   contracts/balance-from-spec/results/`.
2. **Backfill (Stage 89A's own deliverable, §4.2/§5.1)**: add
   `check_id: overlapping-account-patterns-no-double-count` to
   `REQ-BFS-002.yaml`.
3. **Set-up**: a fresh, disposable Ledgerkit scratch copy pinned at the
   real checkout's current HEAD; `codecompass sync` run against it
   (populating `source_files.content_hash` in its own `context-graph.
   db`); the new test function added to `tests/test_reports.py` in
   *this scratch copy only* (never the real `~/projects/ledgerkit`,
   §6.4), reusing Phase 88's own already-documented procedure for
   writing exactly this test.
4. **`detect_newly_coverable_checks(project_root, "balance-from-spec",
   repo_root=<scratch copy>)`** (`codecompass knowledge detect-changes
   --probe-coverage`, §4.10 layers 1-2): iterates `oracle-contract.yaml`'s
   checks; for `overlapping-account-patterns-no-double-count`, confirms
   **zero existing `evidence_kind: "test"` Evidence record whose
   `test_ref` resolves to a result for this `check_id`** (true — the
   corrected gate, §0.2.B; not "zero valid historical results," which
   this check also trivially satisfies today only because it has *never*
   had *any* result at all, not because of staleness); probes `pytest
   --collect-only -q tests/test_reports.py::TestBalanceFromSpec::
   test_section_accounts_overlapping_patterns_no_double_count` against
   the scratch copy — now collects (exit `0`), where it would have
   failed to collect before step 3. Resolves `check_id` →
   `REQ-BFS-002` (via step 2's new field) → `depends_on: [CL-BFS-004]`.
   Returns one `NewlyCoverableCheck(check_id=..., claim_id=CL-BFS-004)`.
5. **`propose_reconciliation`** (`codecompass knowledge verify-changes`,
   §4.10 layers 3-4): calls `oracle.evaluate_check` directly against the
   scratch copy for this check — a real pytest run, producing a fresh
   `OracleResult` with a real `run_id` and `outcome: PASS` (the test
   genuinely passes against the unmodified, correct `reports.py`).
   **Persists it immediately** (`oracle.write_oracle_result`, to
   `planning/contracts/balance-from-spec/results/overlapping-account-
   patterns-no-double-count--<run_id>.yaml`) and round-trip-verifies the
   write (`oracle.parse_oracle_result` + `oracle.evaluate_result_
   precedence` against the just-written path, confirming it still
   evaluates `PASS` and its `raw_output_ref` file's hash matches — §0.2.A/
   §4.10) before this finding is included in anything written next.
   Labels this finding `"newly_covered"` (§4.3 — a `PASS` is never a
   "regression" or a "newly discovered failure").
6. **`write_source_reconciliation_manifest`**: one new manifest item,
   `kind="source_reconciliation"`, `record_id=CL-BFS-004`, one
   contributing finding (`contract_id=REQ-BFS-001`, `check_id=
   overlapping-account-patterns-no-double-count`, this run's `run_id`,
   its own now-persisted `raw_output_ref`, label `"newly_covered"`,
   target field `supporting_evidence`), `state="pending"`,
   `decision="undecided"`.
7. **Human review**: `decision` set to `"accept"`.
8. **`apply_manifest`** (`codecompass knowledge apply`, §4.10 layer 5):
   re-parses the manifest's own cited, already-persisted result file
   (`oracle.parse_oracle_result`, re-validating it still parses and
   still belongs to the named contract/check — never trusting the
   manifest's own cached fields) → `_find_existing_evidence_for_run`
   finds nothing (first time) → writes a new Evidence record,
   `EV-BFS-004` (`evidence_kind: test`, `test_ref` naming this run's own
   now-persisted result file, `repository_revision` the scratch copy's
   pinned HEAD) → checks
   `CL-BFS-004`'s own `supporting_evidence` for `EV-BFS-004` (absent) →
   appends it, giving `supporting_evidence: [EV-BFS-001, EV-BFS-004]`
   → recomputes `evidence_support_state` from the full, now-updated
   field contents (§4.4's corrected, single-Claim rule): `contradicting_
   evidence` is empty, and `supporting_evidence` now contains
   `EV-BFS-004`, an `evidence_kind: "test"` record → sets `"supported"`
   (a real change from `"partially_supported"` — `EV-BFS-001` alone was
   `source`-kind only; `EV-BFS-004` is the first `test`-kind Evidence
   this Claim has ever had).
9. **Result**: `CL-BFS-004.yaml` has genuinely new, changed knowledge —
   a new Evidence record exists on disk, a Claim's own
   `evidence_support_state` field changed, and (§4.5) `CL-BFS-004`'s own
   content hash has changed, ready for `detect_grounded_region_changes`
   to react to, unchanged, on whatever documentation cites it.

### 6.2 Reconciliation — precision checks (the true-positive and
false-positive controls)

- **True-positive control, detector (b) (Task A itself, §6.1)**: steps
  1-9 above, confirmed end to end against a real scratch copy.
- **True-positive control, detector (a) (the already-working
  re-verification path, §0.1.A/§4.1) — mutation corrected this round
  (§0.2.C)**: the OR-union double-counting mutation `DEC-BFS-002`
  describes does **not** fail either of `CL-BFS-001`/`CL-BFS-002`'s own
  required checks — verified directly against the real test bodies:
  `test_single_section_rows_and_subtotal` (`tests/test_reports.py:
  706-720`) and `test_multi_section_correct_values` (line 742-748, via
  `_income_expenses_spec`, line 697-704) each use exactly one account
  pattern per section, and `reports.py:663`'s real matching gate is a
  single boolean membership check — an overlap-counting mutation only
  changes behaviour for a posting matching *more than one* pattern in
  the same section, a condition neither test ever constructs; this
  matches `DEC-BFS-002`'s own already-recorded rationale exactly ("no
  test anywhere in Ledgerkit would catch [this]"), which the prior
  draft's control contradicted without re-checking. **Corrected
  mutation**: remove the `if section.invert:` guard at `reports.py:
  685-686`, making sign inversion unconditional — verified directly
  against the real assertions: `test_single_section_rows_and_subtotal`
  (Expenses section, `invert=False`, asserts `subtotal == Decimal
  ("1359.00")`) computes `Decimal("-1359.00")` under the mutation and
  fails; `test_multi_section_correct_values`'s own `expense_result`
  (same section, same assertion) fails identically in the same test
  body (its `income_result`, `invert=True`, is coincidentally unaffected
  by this specific mutation — its own correct behaviour already negates
  unconditionally for that section — but the test still fails overall,
  since both subtotals are asserted together). This mutation is entirely
  independent of the overlapping-pattern code path, so it never
  interferes with, and is kept strictly separate from, detector (b)'s
  own overlapping-pattern mutation (§6.1 step 3, unchanged — genuinely
  exercises the condition it names, confirmed above it is the *correct*
  kind of change for that purpose, just the wrong one for *this*
  control). With the corrected mutation in a second scratch copy: run
  `codecompass sync`, confirm `detect_source_changes` reports the
  changed range, confirm `change_impact.assess(run_checks=True,
  on_fresh_result=...)` reaches `behavioural_risk` for `CL-BFS-001`/
  `CL-BFS-002` (already bridged via `EV-BFS-002`/`EV-BFS-003`) and
  produces a fresh `CONFIRMED_REGRESSION` for both checks' own
  `check_id`s — labelled `"regression"`, not `"newly_discovered_
  failure"` (§4.3), since a historical `PASS` for these checks already
  exists — with both fresh `OracleResult`s persisted and round-trip-
  verified (§0.2.A/§4.10) exactly as Task A's own path. Mutation
  reversed (the `if` guard restored): both checks' own fresh execution
  returns to `PASS`, confirmed independently as its own regression test
  (§7) — a mutation this plan's own control relies on must be shown to
  be reversible, not merely applicable once.
- **Documentation-invalidation control**: confirm `docs maintain`
  subsequently reports `claims_changed` for any doc region citing
  `CL-BFS-004` (none exist today per the Phase 88 plan's own §18.2
  finding — if still none at demonstration time, this control runs
  against a temporary, disposable schema-governed document created for
  this demonstration alone, citing `CL-BFS-004`, so the invalidation
  pathway is genuinely exercised end to end, not merely asserted to
  exist in principle). This proves the *mechanism* fires — §6.3 below
  separately requires evidence the resulting documentation content is
  actually better for a real task, per §0.1's second semantic
  correction.
- **False-positive control**: make a second, genuinely unrelated,
  disposable-scratch-copy-only change to Ledgerkit (e.g. a comment-only
  edit or a change to an unrelated report function with no citing
  Evidence) and confirm both detectors report nothing proposable
  (`no_recorded_relationship`/no newly-coverable check found), and that
  every unrelated Claim and doc region's own case remains `noop` — the
  false-positive control is exactly as load-bearing as the
  true-positive ones, per `planning/v2-roadmap.md`'s own Phase 89 §7.

### 6.3 Task B — three separate questions, pre-registered before Task A
even runs (§0.1.C — rewritten this round)

**Three genuinely separate gates, never conflated into one (dispatch
§2.C)**:

1. **Technical completion**: the mechanism (detectors, manifest,
   apply branch, doc cascade) runs end to end without error on Task A
   and Task B. This alone is a Stage 89A/89B deliverable, not the
   phase's own exit gate.
2. **A valid, completed evaluation**: Task B's own controlled
   comparison (below) actually ran, both arms were genuinely assessed,
   and no contamination occurred (below). This can be true even if (3)
   is not — a well-run experiment that finds no effect is still a valid
   evaluation, honestly reported.
3. **The roadmap's own positive exit gate** (`planning/v2-roadmap.md`
   §9, quoted exactly, re-read directly this round): "The second task
   measurably benefits from the first, evidenced... not asserted." This
   gate is satisfied **only** when the treatment arm beats the control
   arm by at least the pre-registered minimum improvement below — **a
   negative or inconclusive result, however honestly reported, does
   not satisfy it.** §8 below states plainly what happens if (3) is
   not met.

**Corrected this round (§0.2.D)**: the prior text cited "the methodology
document's own existing minimum-meaningful-difference threshold" —
`planning/v2-evaluation-methodology.md`, re-read in full this round,
defines no such threshold; it explicitly states it "does not set a
numeric target for any metric" and reserves that decision for Phase 90's
own future baseline. Attributing an invented number to that document
would be exactly the "inventing a pre-existing standard" dispatch §2.D
prohibits — the threshold below is instead stated plainly as this plan's
own, Phase-89-owned criterion, built from an instrument this project
already has (`context-evaluator`'s own existing qualitative output),
never borrowed from a document that does not define one. Separately
corrected: the prior text's own "pre-registered... before Task A even
runs" heading was contradicted by its own body, which deferred the
*actual task selection* to "Stage 89C's implementation time" — after
Stage 89B, where Task A's own real demonstration (§6.1) already ran
(§7). **The pre-registration record below (task-selection rule,
success criterion, treatment/control design) is a named Stage 89A
deliverable (§7) — written, committed to this plan file, and reviewed
*before* Stage 89A's own detection/verification work for Task A begins**
— not merely before "Task A's outcome is examined," which was too late
given the staged implementation order.

**Pre-registered as a Stage 89A deliverable, before Task A's own
detection/verification work begins (dispatch §2.D, timing corrected
§0.2.D)**:
- **Task-selection rule (objective, mechanical, fixed now)**: at Stage
  89A's own start, run `codecompass knowledge gaps balance-from-spec`
  (Phase 84's existing, unmodified `find_gaps` CLI surface) against the
  real, current, **pre-Task-A** `balance-from-spec` knowledge state;
  Task B is the single gap reported with the numerically lowest
  `(kind, record_id)` sort key (a fixed, pre-stated, deterministic
  tie-break — never a human's in-the-moment judgement), **excluding**
  any gap naming `CL-BFS-004` or `overlapping-account-patterns-no-
  double-count` (Task A's own named scope, §6.1, never eligible to also
  be Task B). If `find_gaps` reports no other eligible gap at that time,
  Task B falls back to a named, concretely-scoped contingency task fixed
  here now, not invented after the fact: extending `ReportSpec` with a
  convenience "combined section" constructor that merges two or more
  existing sections' own account-pattern tuples into one new section
  (a real, plausible Ledgerkit feature whose correct implementation
  depends on understanding whether the underlying OR-union matching gate
  already safely dedupes an overlapping posting — exactly the fact Task
  A's own reconciliation concerns, §6.1). Either way, the selected task's
  own identity is recorded in `planning/retros/
  phase-89-ledgerkit-two-task-demonstration.md` at Stage 89A's own
  close, before Stage 89B's Task-A demonstration runs.
- **Task B's own independent acceptance test**: if the selected task
  names an existing or newly-authored oracle check under `balance-from-
  spec`'s own `oracle-contract.yaml`, that check is reused unmodified
  (Phase 82's existing mechanism, never informal pass/fail judgement);
  if the selected task requires a check that does not yet exist (likely
  for the fallback task above), a narrowly-scoped new check is authored
  and pinned to the contract *before* Task B's own implementation begins
  — the same discipline Task A's own third check already followed
  (`DEC-BFS-002`).
- **The reconciled knowledge expected to matter**: `CL-BFS-004`'s own
  upgraded `evidence_support_state`/new `EV-BFS-004` citation (§6.1) —
  stated explicitly so contamination (below) can be checked against a
  named fact, not a vague "the reconciled state."
- **Treatment/control**: (treatment) a context packet for Task B drawn
  from the post-reconciliation knowledge state; (control) an otherwise
  byte-identical packet drawn from the pre-reconciliation snapshot,
  withholding exactly `EV-BFS-004`/`CL-BFS-004`'s updated field — never
  withholding anything else, so the comparison isolates Task A's own
  effect.
- **Measurable, independently assessable success criterion and minimum
  improvement (Phase-89-owned, not attributed elsewhere)**: Task B's own
  independent acceptance test (above) — does the treatment-arm change
  pass it where the control-arm change does not — **and** a fresh,
  independent `context-evaluator` dispatch's own existing, real output
  for each arm: a PASS/PASS WITH GAPS/FAIL verdict and a LOW/MODERATE/
  HIGH context-advantage rating (`context-evaluator`'s own stated
  deliverable, unchanged, reused exactly as every other reference-
  project evaluation in this project already uses it — never a new
  numeric scale invented for this comparison alone). **Minimum
  improvement, defined here, by this plan, explicitly**: the gate is met
  when **either** (i) the treatment arm's acceptance-test outcome is
  correct where the control arm's is not, **or** (ii) the treatment
  arm's `context-evaluator` verdict is strictly better than the control
  arm's own verdict on that same fixed three-point scale (FAIL →
  PASS WITH GAPS or PASS, or PASS WITH GAPS → PASS) **or** its
  context-advantage rating is strictly higher on that same fixed
  three-point scale (LOW → MODERATE or HIGH, or MODERATE → HIGH) — a
  tie (identical verdict and identical rating on both arms) does **not**
  satisfy the gate, regardless of acceptance-test outcome agreement.
- **Evaluation procedure and contamination controls**: a fresh,
  independent `context-evaluator` dispatch (never the implementing
  session) assembles and scores both arms without being told which is
  treatment/control (blinded ordering); the control arm's own packet is
  mechanically generated by re-running the same packet-assembly code
  against a checked-out pre-reconciliation commit/snapshot, never
  hand-edited to remove the fact (removing hand-editing risk of
  accidentally also removing something else); zero unrelated content
  may differ between arms (checked mechanically, a diff of the two
  packets outside the one named field is a contamination finding, not
  a pass); Task B's own task-selection rule (above) is itself evaluated
  for contamination risk — since it runs *before* Task A, it cannot by
  construction be biased by Task A's own outcome, but its own exclusion
  rule (never selecting Task A's own gap) is logged explicitly as the
  one deliberate, disclosed narrowing of the otherwise-objective rule.
- **No productivity/time claim** is made from this comparison alone —
  matching this dispatch's own instruction and this project's own
  established precedent (Phase 87C's comparator found scope
  completeness without claiming a net time/cost advantage; Phase 90 is
  the only phase authorised to attempt that broader claim).

### 6.4 Authorisation and evidentiary strength

Entirely feasible, and run by default, on **disposable scratch copies**
only — no real Ledgerkit commit is required for Task A, the
reconciliation, or Task B's controlled comparison; every control named
above is independently reproducible from a fresh scratch copy pinned at
a stated revision, exactly as Phase 88's own demonstration was. If, at
implementation time, landing Task A's own new Evidence/oracle-result
pair in the **real** `~/projects/ledgerkit` checkout is desired for
stronger evidentiary weight, that is a **separate, explicit,
cross-repository authorisation** this plan does not request and must
not assume — named here as a possible future strengthening, not a
precondition of this phase's own exit gate, which the scratch-copy
version alone already satisfies per `planning/v2-roadmap.md`'s own
Phase 89 §9 ("achieved without any dependency on an MCP server" — and,
by the same reasoning, without any dependency on a real cross-repository
write either).

## 7. Staged implementation plan

**Stage 89A — Detection and the manifest extension** (§5.1-§5.3, §4.1-
§4.4, §4.7-§4.10). Deliverables: `source_reconciliation.py`
(`detect_source_changes`/`detect_newly_coverable_checks`/
`propose_reconciliation`/`write_source_reconciliation_manifest`/
baseline helpers); `source-baseline.toml` format; the new, optional,
additive `check_id` field on the Requirement schema (plus the
`REQ-BFS-002.yaml` backfill, §5.1); `_find_existing_evidence_for_run`
(new Evidence-identity helper, §5.3); the one new, additive, default-
`None` `on_fresh_result` parameter on `change_impact.assess`/
`run_check_assurance` (§0.2.A/§4.4); the new `"source_reconciliation"`
`apply_manifest` branch; `codecompass knowledge detect-changes`
(layers 1-2, including the new `--probe-coverage` flag) and
`codecompass knowledge verify-changes` (layers 3-4, new, §4.10) CLI
commands; the Stage 89A ADR (§9) covering all **four** genuinely new
tradeoffs (the in-place-mutation deviation, the first-ever Evidence-
creation path, the new Requirement field, and the `on_fresh_result`
capture parameter); **Task B's own pre-registration record** (§6.3,
written and committed to `planning/retros/
phase-89-ledgerkit-two-task-demonstration.md` at this stage's own
close, before Stage 89B's Task-A demonstration runs — §0.2.D's
sequencing fix). Tests: the true-positive (both detector (a), with the
corrected sign-inversion mutation, and detector (b), §6.2) and
false-positive controls run against disposable Ledgerkit scratch
copies, standalone (not yet wired to documentation); a
mutation-reversibility test (the corrected detector-(a) mutation,
§6.2, reverted, confirmed both `single-section-expense-subtotal`/
`multi-section-income-expense-subtotal` return to `PASS` — the direct
regression test for §0.2.C); a detector-selection-gate test (a required
check with an *existing* citing test-kind Evidence record whose result
has gone `INVALID`/stale, confirmed routed to detector (a)'s own
re-verification path, never misreported by detector (b) as "newly
coverable" merely because no currently-valid result exists — the direct
regression test for §0.2.B, distinguishing this from the
newly-coverable-check test below); a result-persistence-and-provenance
test (`verify-changes` against a real scratch-copy check, confirmed a
structured `OracleResult` YAML is written to the slug's own `results/`
directory via `oracle.write_oracle_result`, round-trips through
`oracle.parse_oracle_result`, and the resulting manifest item's own
cited `run_id`/`raw_output_ref` match the persisted file exactly — the
direct regression test for §0.2.A, replacing the previous, impossible
"re-walk `assess()`'s own return value" design); a multi-range
capture test (two findings for the *same* `check_id` arising from two
*different* `changed[]` ranges in one `propose_reconciliation` call,
confirmed `_capture` retains both results and each finding is matched
to its own correct run by `(range index, check_id)`, never one
silently overwriting the other — the direct regression test for the
fifth-round independent review's own multi-range finding, §4.4); a
**CLI-boundary test, corrected this round (the fifth-round independent
review's own blocking finding — the prior text asserted zero
subprocesses "with and without `--probe-coverage`," directly
contradicting §4.10's own description of what `--probe-coverage` does)**
— two separate assertions, not one: (i) `detect-changes` **without**
`--probe-coverage` spawns zero subprocesses and writes zero files under
`results/`/`reconciliation/`/`scratch-assessments/`, on every code
path including one that finds candidate findings; (ii) `detect-changes`
**with** `--probe-coverage`, run against a scratch copy with exactly
one required check lacking citing Evidence, spawns **exactly one**
`pytest --collect-only` subprocess for that check (never a full test
run, confirmed via the subprocess's own invocation arguments, never
merely its exit code) and still writes **zero** files anywhere (a
probe's own exit code is reported, never persisted) — together the
direct regression test for §0.2.E, distinguishing both from
`verify-changes`, which the same test suite confirms *does* spawn a
real, full-run subprocess and write both a result and a manifest file
when run against the identical scratch-copy fixture); a
stale-graph-index test (a file edited
without an intervening `codecompass sync`, confirmed `detect_source_
changes` reports `"stale_graph_index"` and excludes that file, never
silently comparing a stale hash — the direct regression test for
§0.1.D); a newly-coverable-check test (a required check with zero
existing citing test-kind Evidence, §0.2.B, whose test now collects,
confirmed `detect_newly_coverable_checks` finds it and resolves it to
the correct Claim via the new `check_id` field — the direct regression
test for §0.1.A, distinct from the detector-selection-gate test above,
which covers the *opposite* case of existing-but-stale Evidence); an
interrupted-apply test (§4.8, crash mid-batch leaves the baseline
unchanged, confirmed by re-running detection and seeing the same
findings again); a multi-Claim-mapping test (one changed symbol → two
distinct Claims, each its own independently-decided item); a
same-Claim-merge test (two findings against one Claim, confirmed merged
into that Claim's own single item, never two racing items); a
disagreeing-outcomes test (a merged item whose contributing findings
include both a `CONFIRMED_REGRESSION` and a qualifying `VERIFIED_
SCOPE`, confirmed written to both `contradicting_evidence` and
`supporting_evidence` with `evidence_support_state` recomputed to
`"conflicting"`); a cumulative-state test (a Claim with an *existing*
`contradicting_evidence` entry from an earlier batch; a *new* batch
adds only supporting Evidence; confirmed `evidence_support_state` is
recomputed to `"conflicting"`, never silently reset to `"supported"` —
the direct regression test for §0.1's "historical contradictions must
not silently disappear" requirement); a **contradicting-evidence-only
test** (named explicitly, per the fourth review round's own test-
adequacy observation (d), rather than left implicit inside a generic
"enum-validity" test that might not actually drive this exact branch:
a Claim with non-empty `contradicting_evidence` and empty `supporting_
evidence`, confirmed the recomputation writes `"unsupported"`, never
`"contradicted"` — the direct regression test for the third review
round's Blocking Finding 1, exercising the function through this exact
branch, not merely asserting the literal string set is valid); an
`evidence_support_state` enum-validity test (confirmed every value
§4.4's corrected rule can ever write — `"unsupported"`/`"partially_
supported"`/`"supported"`/`"conflicting"` — passes `scripts/check_
knowledge_base.py`'s own `check_optional_enum_fields`); a
source-vs-test-Evidence test (a Claim whose `supporting_evidence`
contains only `evidence_kind: "source"` records recomputes to
`"partially_supported"`; the same Claim, with one `evidence_kind:
"test"` record appended, recomputes to `"supported"` — the direct
regression test for the third review round's Blocking Finding 2,
reproducing `CL-BFS-004`'s own real before/after state); an
Evidence-identity-retry test
(`_find_existing_evidence_for_run` confirmed to find an already-written
Evidence record by `(contract_id, check_id, run_id)` and skip
re-creating it on a simulated retry — the direct regression test for
§0.1.B, replacing the prior, unsound reliance on `_find_existing_
promoted_record`); a Claim-append-retry test (the same Evidence id
already present in `contradicting_evidence`/`supporting_evidence`,
confirmed the append is skipped rather than duplicated, independently
of whether the Evidence record itself was newly written or already
existed); a conflicting-edit test (a Claim hand-edited between
detection and apply, confirmed refused, mirroring the existing
`"anchor_edit"` conflict test); a multi-check-Requirement-guard test
(a `check_id` added to a Requirement whose own `depends_on` names more
than one Claim, confirmed `detect_newly_coverable_checks` reports a
configuration error and resolves nothing, rather than silently
returning every one of those Claims — the direct regression test for
the fourth review round's non-blocking observation (e)). **`CLAUDE.md`
§1's L-021, explicitly
satisfied**: `apply_manifest` has exactly one real production call
site, `cli.py::knowledge_apply_manifest` (`codecompass knowledge apply
MANIFEST_PATH`) — at least one Stage 89A test invokes that real CLI
command directly against a manifest containing a `"source_
reconciliation"` item (via this project's own existing `typer`
CLI-testing convention), not only `apply_manifest()` called in
isolation as a library function. Independent audit checkpoint:
`release-phase-auditor` (stage-level — persisted report at `planning/
retros/_audit-phase-89-stage-89a.md` before this stage is treated as
closed).

**Stage 89B — The new gap kind and the documentation-cascade
demonstration** (§5.4, §6.1-§6.2's doc-invalidation leg, §4.5-§4.6).
Deliverables: `find_gaps`'s new `claim_contradicted_by_fresh_check`
gap kind (carrying the `"regression"`/`"newly_discovered_failure"`
label, §4.3); the end-to-end Task-A demonstration including the
documentation-invalidation control (§6.2, including its own
disposable-schema-governed-document fallback if no real grounded
region exists yet). Tests: the new gap kind's own unit tests,
including one asserting the `"regression"` vs `"newly_discovered_
failure"` label is correct in each of the two cases (a historical
`PASS` present vs absent for the check); an end-to-end scratch-copy run
of the full §3 diagram, start to finish, for both detectors. Independent
audit checkpoint: stage-level `release-phase-auditor` pass, persisted
per the same convention.

**Stage 89C — Task B and the pre-registered controlled comparison**
(§6.3). Task B's own selection, success criteria, and treatment/control
design are **already fixed**, Stage 89A's own deliverable (§0.2.D) —
this stage never selects or redefines them, only executes against the
already-committed record. Deliverables: Task B's own implementation
(the task Stage 89A's own pre-registration record named or the rule it
fixed resolved to); the controlled comparison itself, run against that
already-pre-registered design; `planning/retros/phase-89-ledgerkit-two-
task-demonstration.md` updated with the actual run's own results
(appended to the pre-registration record already present from Stage
89A, never replacing it). Independent verification: a fresh
`context-evaluator` dispatch reproducing the comparison's own
control/treatment packets directly (never trusting the implementing
session's own report), exactly as Phase 88's own Ledgerkit demonstration
was independently re-verified — and confirming directly that the task
actually run matches Stage 89A's own pre-registered record verbatim
(never substituted or adjusted after Task A's own outcome became known).

**Terminal closeout**: learnings triage, phase retro (full
`TEMPLATE.md` structure, per the `L-134`/Phase-88-retro precedent of
what "complete" actually means here), whole-phase `release-phase-auditor`
pass against the exact commit to be marked done, then — and only then —
`planning/ROADMAP.md`'s Phase 89 row flips to `done` (`CLAUDE.md` §5,
unchanged).

## 8. Definition of Done (mapped to the governing exit gate — three
gates, never conflated, §0.1.C/§6.3)

Matches `CLAUDE.md` §5, plus `planning/v2-roadmap.md`'s own Phase 89 §9
exit gate specifically, with the three questions kept explicitly
separate throughout:

1. **Technical completion** (a Stage 89A/89B gate, not the phase's own
   exit gate): every stage's own tests pass (including the detector
   (a)/detector (b) true-positive controls and the false-positive
   control, §6.2); the Task-A walkthrough (§6.1) runs end to end
   against a disposable scratch copy with no error; no new doc-
   compilation/scheduler/knowledge-store code exists anywhere in the
   diff (an independent auditor confirms this directly against the
   real diff); `docs/`, `architecture/`, `decisions/*` updated for the
   Stage 89A ADR (§9); phase retro filed; learnings triaged.
2. **A valid, completed Task B evaluation** (§6.3): the pre-registered
   criteria (named *before* Task A ran) were followed exactly, both
   arms were genuinely assessed by an independent `context-evaluator`
   dispatch, and the contamination controls (§6.3) held — a fresh,
   independent `release-phase-auditor`/`context-evaluator` pass
   confirms this directly, never trusting the implementing session's
   own account.
3. **The roadmap's own positive exit gate**: the pre-registered minimum
   improvement (§6.3) was actually met. **If it was not**: this plan's
   own closeout states that plainly (no overclaim, matching this
   project's own Phase 87C precedent) and `planning/ROADMAP.md`'s Phase
   89 row does **not** flip to `done` on that basis alone — gates 1 and
   2 being satisfied closes the *implementation* work (and may be
   recorded as such, e.g. "implemented, exit gate not yet met"), but
   `CLAUDE.md` §5's "only once every one of the above genuinely holds"
   rule means a roadmap exit gate stated in `planning/v2-roadmap.md`
   itself is one of "the above" for *this* phase specifically, and a
   negative result on it is a new, separate, explicit decision point
   (redesign Task B, pick a different reconciled fact, or defer/amend
   the exit gate itself via a new ADR) — never silently absorbed into
   "done" by the mere fact that the mechanism itself worked.

A fresh, independent `release-phase-auditor` pass against the exact
commit about to be marked done is required regardless of which of the
three gates above the phase actually reaches.

## 9. Risks and unresolved decisions

- **§6.3's Task B selection** is pre-registered as a **Stage 89A**
  deliverable, *before Stage 89A's own Task-A detection/verification
  work begins* — corrected this round (§0.2.D): the fourth amendment's
  own "at Stage 89C's own start" timing was, by this plan's own staged
  order (§7), *after* Task A's real demonstration already ran in Stage
  89B, contradicting the "before Task A itself runs" principle stated in
  the same paragraph. Fixing it any later than Stage 89A's own start
  would be a form of picking the result before the experiment, the
  opposite of what pre-registration is for.
- **A negative Task B result is a real, open risk, not hand-waved
  away** (§0.1.C/§8): this plan does not know, and cannot know in
  advance, whether the pre-registered minimum improvement will actually
  be met. §8 states explicitly what happens if it is not — a new
  decision point, never a silent downgrade of the exit gate's own
  wording.
- **Resolved by independent review** (no longer open): `write_manifest`
  itself is left untouched; a new sibling writer, `write_source_
  reconciliation_manifest`, is introduced instead, mirroring the real,
  already-production `write_doc_candidates_to_manifests` precedent
  rather than a hypothetical either/or.
- **Resolved by a second independent review round** (no longer open):
  a merged item's own disagreeing-outcome write uses the existing
  `evidence_support_state: "conflicting"` value, never an invented one.
- **Resolved by a third independent review round** (no longer open):
  §4.4's `evidence_support_state` recomputation rule wrote an invalid
  enum value (`"contradicted"`, a `Claim.status` value, not an
  `evidence_support_state` one) and relied on an undefined cross-Claim
  "sibling Claims under the same Requirement family" notion for its one
  worked application (§6.1) — both fixed in place with a corrected,
  purely local, single-Claim rule (`"unsupported"` for the invalid
  value; "does `supporting_evidence` contain an `evidence_kind: "test"`
  record" for the cross-Claim notion), directly validated against every
  real record this mechanism can reach (`CL-BFS-001`/`CL-BFS-002`/
  `CL-BFS-004`) and explicitly scoped to never reach the whole-contract
  Claims (`CL-BFS-003`/`CL-BFS-005`) that use this same field name for a
  genuinely different, pre-existing purpose. The same review round
  found three further non-blocking items, all folded in directly rather
  than deferred to a fifth review round: (i) the rule's own
  evidence-kind partition is sound only for contract-governed Claims,
  now stated explicitly in §4.4; (ii) the `depends_on`-length-1
  fail-closed guard on a `check_id`-bearing Requirement, now a stated
  mechanism requirement of `detect_newly_coverable_checks` itself
  (§5.1), not merely an ADR note — nothing in `check_knowledge_base.py`
  would otherwise reject a human mistakenly adding `check_id` to a
  multi-check Requirement; (iii) §7's test list now names a distinct
  contradicting-evidence-only test rather than leaving it implicit
  inside a generically-named enum-validity test.
- **Superseded this round (§0.1.B)**: the second amendment's own fix for
  merged-item retry safety (reusing `_find_existing_promoted_record`)
  is replaced — that helper cannot represent Evidence identity at all
  (no `statement` field). The real mechanism is now `_find_existing_
  evidence_for_run`, a new, narrow, Evidence-specific identity helper
  (§4.4/§5.3), plus a second, independent idempotency check on the
  Claim-side append — not because the second amendment's instinct
  (idempotent retry) was wrong, but because the specific helper it
  named was never capable of doing this.
- **Superseded this round (§0.1.A)**: the original/second amendment's
  own Task A walkthrough, relying solely on `change_impact.assess
  (run_checks=True)`, is replaced by a second, genuinely new detector,
  `detect_newly_coverable_checks` (§4.1/§5.1), for exactly the class of
  scenario (a required check with zero prior citing Evidence) that
  pathway structurally cannot reach. `detect_source_changes`/`assess()`
  remain valid, unchanged, for the re-verification scenario they were
  always actually capable of (§6.2's second true-positive control).
- **Whether an ADR is required**: **yes**, one Stage 89A ADR covering
  **four** genuinely new tradeoffs together (widened again this round,
  was three): (a) the disclosed, narrowly-scoped in-place-mutation
  deviation (§4.4) from this project's otherwise-universal "never
  mutate, always create a competing record" convention; (b) this
  codebase's first-ever mechanized Evidence-creation path, with its own
  new, narrow identity convention (§4.4/§5.3) rather than reuse of an
  existing one (§0.1.B); (c) the new, optional, additive `check_id`
  field on the Requirement schema and the informal-prose-matching gap it
  closes (§4.2/§5.1); (d) **new this round (§0.2.A)**: the additive,
  default-`None` `on_fresh_result` parameter on `change_impact.assess`/
  `run_check_assurance` — this codebase's first instance of Phase 83's
  own classification pathway being extended, even non-invasively, to let
  a caller recover the real `OracleResult` that pathway already computes
  internally but has never before exposed; the alternative considered
  and rejected (re-executing the same check a second time, independently,
  purely to recover provenance) is named explicitly so a future reader
  does not re-propose it without re-deriving why it was rejected
  (§0.2.A). All four are genuinely new, previously-untaken decisions in
  this codebase, not routine extensions of an existing mechanism —
  `CLAUDE.md` §2's "non-obvious tradeoff" trigger applies to each.
  Drafting it is Stage 89A's own first task, not assumed or pre-written
  here.
- **The `pytest --collect-only` probe's own failure modes** (new risk,
  this round, §5.1) are not yet exhaustively enumerated here (a
  genuinely malformed `check_reference`, a collection error unrelated
  to the target test's own existence, a `conftest.py`-level import
  error elsewhere in the target repo) — Stage 89A's own test list
  (§7) must cover at least "does not yet exist" (exit non-zero,
  reported as "not yet coverable", never conflated with the check
  itself failing) and "exists and collects cleanly" (§6.1 step 4); a
  third case (collection errors for an unrelated reason) is named here
  as a known gap for Stage 89A's own implementer to close with a
  fail-closed "cannot determine coverability" finding, never a silent
  false negative.
- **Superseded this round (§0.2.A)**: `propose_reconciliation`'s own
  prior design ("re-walks `assess()`'s own returned `range_reports[]...
  assurance[]`" to recover `run_id`/`raw_output_ref`) is replaced — the
  data it needed was never present in `assess()`'s own return shape
  (`AssuranceFinding` has no `run_id`/`raw_output_ref` field at all,
  `change_impact.py:424-433`). The real mechanism is now the additive
  `on_fresh_result` capture parameter (§4.4/§5.1), not a richer
  re-walk of existing data that was never going to contain it.
- **Resolved by a fifth independent review round** (no longer open):
  `_capture`'s own first design keyed captured `OracleResult`s by
  `check_id` alone — unsound, since `assess()`'s own `run_check_
  assurance` loop runs once per `(range, check_id)` pair, not once per
  `check_id` globally (`change_impact.py:526-578`), so a second range
  contributing the same `check_id` would silently overwrite the first's
  captured result. Fixed in place: `_capture` now accumulates a
  `list[OracleResult]` per `check_id`, and `propose_reconciliation`
  matches each finding to its own result by `(range index, check_id)`,
  never `check_id` alone (§4.4/§5.1), with a dedicated multi-range
  regression test (§7). The same review round also found and fixed two
  factual errors in this plan's own verification of §0.2.A (a
  non-recursive grep had wrongly reported zero call sites for `oracle.
  write_oracle_result`/`change_impact.assess`; both have exactly one
  real call site each, in `src/codecompass/mcp/tools.py`, now cited
  correctly) and one genuine blocking self-contradiction between §4.10
  and §7's own CLI-boundary test description (now split into two
  separate, non-contradictory assertions).
- **Superseded this round (§0.2.B)**: detector (b)'s own prior gate
  ("zero currently-valid historical `OracleResult`") is replaced — that
  condition does not distinguish "never covered" from "previously
  covered, now stale," and would have misrouted the latter away from
  detector (a)'s own re-verification pathway. The real gate is now
  "zero existing citing test-kind Evidence record" (§4.1(b)/§5.1), the
  same bridge-presence test `classify_symbol` already performs.
- **Superseded this round (§0.2.C)**: the detector-(a) positive
  control's own prior mutation (OR-union double-counting,
  `DEC-BFS-002`'s own scenario) is replaced for this specific purpose —
  verified directly against the real test bodies, it cannot fail either
  of the two tests it was claimed to fail, confirming `DEC-BFS-002`'s
  own already-recorded rationale rather than contradicting it. The real
  control mutation is now the unconditional-sign-inversion change
  (§6.2); the original mutation is retained, unchanged, as detector
  (b)'s own scenario (§6.1), which it was always correctly suited to.
- **Open risk, not yet closed (§0.2.D)**: Task B's own fallback task
  (a `ReportSpec` "combined section" constructor, §6.3) is this plan's
  own proposed contingency, not a task independently confirmed to be
  something Ledgerkit's own maintainers would actually want — named
  here as a plausible, concretely-scoped stand-in whose own acceptance
  test is authored fresh before Task B begins (§6.3), should the
  primary, objective `find_gaps`-driven selection rule return nothing
  eligible; Stage 89A's own implementer must re-confirm at pre-
  registration time whether a real, independently-motivated Ledgerkit
  gap is available before falling back to it.
- **Open risk, not yet closed (§0.2.A)**: the `on_fresh_result` capture
  parameter is new, untested machinery threaded through two existing
  Phase 83 functions — Stage 89A's own test list (§7) includes a direct
  regression test for it (the result-persistence-and-provenance test),
  but its interaction with `assess()`'s own existing exception handling
  (what happens if `on_fresh_result` itself raises, e.g. a disk-full
  condition during the persistence step it triggers) is not yet
  specified here and is named as a Stage 89A implementation-time
  decision, not resolved by this plan.

## 10. Explicit non-goals

- Phase 90 (comparative development trials) — not implemented,
  attempted, or anticipated beyond borrowing its already-published
  methodology document for §6.3's measurement design, exactly as this
  dispatch's own instruction requires.
- Any reopening of Phase 88's MCP architecture, trust model, or tool
  surface — Phase 89 is independently deliverable and touches none of
  `src/codecompass/mcp/`.
- Any reopening of Phase 87's clean-room reconstruction mode or manual
  incremental-maintenance mode — both remain exactly as they are;
  `docs compile`/`maintain`/`publish` gain a new *trigger* for their
  existing, unmodified behaviour, never new behaviour of their own.
- A `git diff`-parsing change-detection mechanism — content-hash
  comparison only, matching Phase 83's own already-settled choice.
- An automatic (`--yes`/no-review) reconciliation-apply mode — every
  write requires explicit human `"accept"`, no exception, in this
  phase's own MVP scope.
- Landing anything in the real `~/projects/ledgerkit` checkout — the
  two-task demonstration runs on disposable scratch copies only unless
  a separate, explicit cross-repository authorisation is given (§6.4).
- Any change to `change_impact.py::run_check_assurance`'s own
  `CONFIRMED_REGRESSION`/`VERIFIED_SCOPE`/`VERIFICATION_GAP`/
  `INVALID_ASSESSMENT` classification (§0.1's semantic correction) —
  the `"regression"`/`"newly_discovered_failure"`/`"newly_covered"`
  distinction is computed entirely in `source_reconciliation.py`, from
  data Phase 83 already returns unchanged, never by modifying Phase
  83's own classification function or its return shape. (This is
  distinct from, and not contradicted by, §4.4/§5.1's one new, additive,
  default-`None` `on_fresh_result` parameter on `assess`/
  `run_check_assurance`, §0.2.A — that parameter changes neither
  function's classification logic nor its own return value for any
  existing or future caller that does not pass it; it exists solely to
  let a caller that explicitly opts in also observe the real
  `OracleResult` already computed internally, which neither function's
  return shape has ever been able to carry.)
