# Phase 83: Semantic Change Assurance — plan

**Status:** done (2026-10-28, direct user request — "CodeCompass
Orchestrator — Amend and Implement Phase 83"). Independently audited:
`release-phase-auditor` returned PASS on re-audit against commit
`d076023` (`planning/retros/_audit-phase-83.md`), after an initial FAIL
pass against `b1a8447` was fully resolved (a missing fixture-driven test
and a real `knowledge-curator` triage of two retro-surfaced learnings).
**Corrective pass (2026-10-28, same day, post-completion source review —
"CodeCompass Orchestrator — Phase 83 Corrective Pass"):** three further
correctness defects in `scripts/assess_change_impact.py`, found by direct
inspection after the above audit had already passed, are fixed under
`decisions/0089` — see that ADR for the full defect/fix record. §3, §5,
and §7's deliverable description below are updated in place to describe
the corrected behaviour (this plan is also the as-built record, per its
own header below); the acceptance criteria in §12 gain three new items.
**One outstanding, separately-gated item remains, explicitly tracked, not
part of this phase's own completion**: the real Ledgerkit test has not
landed in the real `~/projects/ledgerkit` checkout — a cross-repository
action requiring its own future explicit authorisation.

Governing prompt: "CodeCompass Orchestrator — Approve v2 Roadmap and Plan
Phases 83–84" (2026-10-24), **amended** by "CodeCompass Orchestrator —
Phase 83 Corrective Planning Amendment" (2026-10-24, same day — see
`decisions/0086` for the five corrected gaps and their grounding),
**amended a second time** by "CodeCompass Orchestrator — Amend and
Implement Phase 83" (2026-10-28 — see `decisions/0087` for the
precedence-reachability defect and sequencing clarifications this pass
corrected), and **corrected a third time**, post-completion, by
"CodeCompass Orchestrator — Phase 83 Corrective Pass" (2026-10-28 — see
`decisions/0089` for the source-identity, range-coverage, and evidence-
validation defects this pass fixed). Roadmap-depth scope: `planning/
v2-roadmap.md` §"Phase 83" (unchanged by `decisions/0084`/`0085`). This
file is the `CLAUDE.md` §1 implementation-ready plan that section only
sketched. **Implementation is authorised as of the second amendment**
(`decisions/0087` §4) — this file now also serves as the as-built record
of what Phase 83 delivers, updated in the same session implementation
proceeds.

## 0. Verified current state (read live, not assumed, both passes)

Re-confirmed this session (the corrective-amendment pass), not merely
carried over:

- **Ledgerkit's HEAD is still `7224bb5c113cd3aad7e86e994365703cd0070154`**
  (2026-10-03T00:51:43+08:00), unchanged since the first planning pass —
  §2's regression scenario needed no re-grounding. **The working tree is
  not clean** (`dev-docs/clean-room/compliance-log.md` modified, an
  untracked `dev-docs/clean-room/implementation-reconstruction/`
  directory) — neither touches `ledgerkit/` package code, but it is live
  confirmation that "the checkout's git state" and "what was last synced
  into a graph" are two different things even in the ordinary case, not
  a hypothetical this plan needs to guard against only in principle (see
  §4).
- **Phase 82 is `done`, unreopened.** `planning/contracts/balance-from-
  spec/oracle-contract.yaml` (`contract_id: REQ-BFS-001`) has exactly two
  required checks today (`single-section-expense-subtotal`,
  `multi-section-income-expense-subtotal`); six real, immutable `PASS`
  oracle-result files exist across two runs (2026-10-21, 2026-10-22).
  `check_contracts.py::_iter_contract_slugs` confirms (by direct reading)
  **exactly one `oracle-contract.yaml` is read per slug directory** — a
  hard constraint this plan's §5 design works within, not around.
- **`EV-BFS-001` already cites `balance_from_spec` as a whole**, via the
  existing, already-validated `source_ref` convention: `"ledgerkit/
  reports.py:600 def balance_from_spec"`. `CL-BFS-001`/`CL-BFS-002` each
  cite `EV-BFS-001` (relevance) together with `EV-BFS-002`/`EV-BFS-003`
  respectively (a passing result for a specific check) in their own
  `supporting_evidence` lists. This is the real, already-existing,
  already-curated relationship §2 below builds on — not a new mechanism.
- **`source_files.content_hash`** (`graph.py` line 73-85) is a real,
  already-populated per-file column: `sha256` of the exact bytes last
  synced (`source_symbols.py`/`sync.py` line 366 — identical construction
  to `oracle.sha256_file`). This is the mechanism §4 below reuses for
  revision consistency.
- **`CheckAggregate.state`** (`oracle.py` line 776-826) takes exactly
  three values — `PASS`, `GAP`, `NOT_REQUIRED` — never `FAIL`. A required
  check with an observed `FAIL` and no `PASS` aggregates to `GAP`, with
  the `FAIL` retained in `observed_outcomes` (`decisions/0081` §2,
  confirmed by direct reading, not assumed). §2 below builds the
  assurance-report semantics around this fact explicitly.
- **`evaluate_result_precedence`'s rule 1** (`oracle.py` line 726-731)
  recomputes `sha256_file(contract_path)` — the whole `oracle-
  contract.yaml` file's own hash — and compares it to each stored
  result's `oracle_contract_content_hash`. Appending a check to that file
  changes the file's hash and therefore invalidates every existing
  result's recorded hash. §5 below names this cost explicitly rather than
  discovering it during implementation.
- **No first-party call-graph exists** (unchanged finding from the first
  pass): `uses_edges` requires a non-null `vendor_id`, so it records only
  first-party-file-uses-vendored-symbol relationships, never first-party-
  symbol-calls-first-party-symbol. `conditional-generalisation.md`'s own
  discipline ("don't add a graph table until real use shows a gap") is
  satisfied: §3/§5 below resolve this phase's needs without one.
- **Ledgerkit has its own, separate `context-graph.db`** at
  `~/projects/ledgerkit/context-graph.db`, distinct from CodeCompass's
  own self-referential graph (which holds zero real Ledgerkit knowledge).
  Any impact-assessment tooling this phase builds must point explicitly
  at the *target* repository's own graph — never assume it can read
  CodeCompass's own (unchanged finding, §6 makes the four distinct paths
  this requires explicit).
- **The confirmed blind spot (§2 below) is unchanged**: Ledgerkit's own
  test suite still does not assert the OR-union/no-double-count
  obligation anywhere.

## 1. Objective / user value

Unchanged from the first pass: demonstrate, against real Ledgerkit
behaviour, that CodeCompass can (a) assess which of a project's own
documented behavioural obligations a proposed/applied change could put
at risk, distinguishing *established relevance* (a real, curated
Evidence-to-symbol citation) from the *absence* of a recorded
relationship (never treated as proof of safety) and from *verified
behavioural coverage* (a Claim that also cites a check-resolving
test-evidence record); (b) independently execute the right checks and
report CONFIRMED_REGRESSION / VERIFIED_SCOPE / VERIFICATION_GAP /
INVALID_ASSESSMENT (§2) without ever letting a real `FAIL` be read as
"merely missing evidence"; and (c) catch a real semantic regression that
passes Ledgerkit's own full, already extensive test suite unmodified.

## 2. The confirmed blind spot (grounds the dogfood scenario, §8)

Unchanged from the first pass — re-verified, not re-derived:
`ledgerkit/reports.py::balance_from_spec` (line 644-668) includes a
posting when it matches **any** of `section.accounts`'s patterns (OR
union, `_matches_pattern`, infix/case-insensitive per `compile_
hledger_regex`'s own docstring) — documented by the function's own
docstring as deliberate: "Section-level account patterns are OR-combined
within each section." Every real `ReportSection(accounts=(...))`
construction in Ledgerkit's codebase and test suite uses either one
pattern or multiple **non-overlapping** patterns. The one test
constructing multiple patterns in a single section
(`test_section_multiple_accounts_patterns_or_union`, `tests/
test_reports.py:810`) asserts only membership (`assertIn`/`assertNotIn`),
never a subtotal — it cannot detect a posting counted more than once.
`accounts=("food", "groceries")` reproduces this with the real, pinned
`tests/fixtures/filtered.journal` fixture's `£150.00` groceries posting
(it matches both patterns under real infix-search semantics). No test
anywhere in Ledgerkit would catch this.

## 3. Behavioural-coverage model (corrects the blocking test-coverage defect — `decisions/0086` §1)

A touched symbol's classification is **three-tier**, and is kept
structurally separate from the *independent check execution outcome*
(§4). Neither `test_input_paths` nor file proximity nor a passing test
existing *somewhere* is ever used to infer coverage.

**3.1 Relevance** — does any `source`-kind Evidence under the target
knowledge slug cite the touched symbol? A `source`-kind Evidence
(`evidence_kind: source`) with a `source_ref` matching the existing
`"<path>:<line>[-<line2>] def|class <symbol>"` convention
(`check_contracts.py::_SOURCE_REF_WITH_SYMBOL_RE`, reused unchanged, not
reimplemented) *is* the recorded relevance relationship — nothing new is
introduced to represent it. **Corrected (`decisions/0089` §A):** a
citation only counts when the `source_ref`'s own `path` group, not only
its `symbol` group, matches the symbol actually being assessed (path
comparison normalised via `PurePosixPath(...).as_posix()` on both
sides) — two first-party files that happen to declare a same-named
symbol no longer inherit each other's Evidence.

**3.2 Coverage** — does any Claim whose own `supporting_evidence` cites
that relevance-establishing Evidence *also* cite a `test`-kind Evidence
(`evidence_kind: test`) whose `test_ref` resolves to a real
`OracleResult` naming a `check_id` in the slug's own `oracle-
contract.yaml`? This is read directly off each Claim's existing
`supporting_evidence` list — the exact mechanism `derive_epistemic_
profile` (line 1082-1112) already uses internally, reused by reading the
same records, not by adding a parallel path. **Corrected (`decisions/
0089` §C):** "resolves to a real `OracleResult`" is now actually
enforced, via `oracle.parse_oracle_result` (schema validation) plus a
check that the result's own `contract_id` matches the *live* contract
and its `scope` matches the named check's own `scope` — not merely that
a YAML mapping with a matching `check_id` key could be loaded. A result
failing any of these checks (malformed, wrong contract, wrong scope,
unknown check_id) establishes no coverage link; it never manufactures a
fresh verification outcome either way — that remains §4's job alone,
unaffected by this correction.

**3.3 Three classifications, mutually exclusive:**

| Classification | Condition | Meaning |
|---|---|---|
| `no_recorded_relationship` | No Evidence anywhere in the slug cites this symbol | **Not** "safe" — an absence of recorded knowledge; `decisions/0086` §1/§8's own correction: absence of a relationship is never read as evidence of safety |
| `relevant_no_coverage_link` | A citing Evidence exists, but no Claim bridges it to a check-resolving test-evidence | Relevance is established; behavioural coverage is not — an explicit evidence limitation |
| `behavioural_risk` | A Claim bridges a citing Evidence to a check-resolving test-evidence | That check is "applicable" and, with `--run-checks`, independently re-executed (§4) |

A `behavioural_risk` finding is never presented as comprehensive
interprocedural analysis — it names exactly the bounded relationship
found (which symbol, which Claim, which check), per `decisions/0086` §1.

## 4. Independent assurance-report semantics (corrects the blocking GAP/FAIL conflation — `decisions/0086` §2, precedence corrected again — `decisions/0087` §1)

For every check found `behavioural_risk`-applicable in §3, when
`--run-checks` is passed, the check is **freshly re-executed** (never
read from a historical result) via the unmodified `oracle.evaluate_
check` — exactly one fresh `OracleResult` is produced per applicable
check. Its *effective* outcome — via `oracle.evaluate_result_precedence`,
never its own raw `outcome` field — is always exactly one of `PASS`/
`FAIL`/`INVALID` (`evaluate_result_precedence` never returns `GAP` for a
single result). **Classification is determined solely by this fresh
effective outcome, never by the separately-computed aggregate `state`**
(`decisions/0081`'s own `aggregate_contract`, over every `OracleResult`
on file for the check, historical and fresh together) — the aggregate is
displayed alongside, for context, but is not itself a step in this
precedence, since `aggregate_contract` returns `GAP` for *any* required
check with no accepted `PASS`, including one whose only result is
`INVALID` — treating the aggregate as a precedence step would make
`INVALID_ASSESSMENT` unreachable (`decisions/0087`'s own corrected
defect, found in this plan's own prior revision before any code was
written against it). The corrected precedence — the first rule that
applies wins:

1. Fresh effective outcome is `FAIL` → **CONFIRMED_REGRESSION**. Highest
   precedence; never downgraded by any later rule or by the aggregate
   `state`.
2. Else fresh effective outcome is `INVALID` → **INVALID_ASSESSMENT** —
   reachable unconditionally whenever the one fresh execution itself
   could not be trusted or validated (corrupted/tampered raw output, a
   tested-subject/test-input digest mismatch, a scope mismatch, an
   all-skipped pytest execution per `decisions/0083`'s own existing,
   unmodified rule) — never routed through rule 4 merely because the
   aggregate also happens to compute `GAP` for an invalid result (it
   always does; that is shown alongside, not substituted).
3. Else fresh effective outcome is `PASS` → **VERIFIED_SCOPE**.
4. Else — no fresh result exists for this check at all (`--run-checks`
   was not passed, or §3 found no applicable check in the first place) →
   **VERIFICATION_GAP**. Reserved for *no verification was attempted*,
   never reused for an attempt that produced a real, if untrustworthy,
   outcome (that is rule 2's own, now-reachable, territory).

A `CONFIRMED_REGRESSION` or `INVALID_ASSESSMENT` report always shows the
underlying aggregate `state` alongside the classification — usually
`GAP` in both cases, for different underlying reasons, labelled as two
independently true, co-existing facts (`decisions/0081` §2's own
language), never collapsed into one line that could be misread as "no
evidence." A historical `PASS` on file for the same check never promotes
a fresh `FAIL`/`INVALID` past rules 1/2 — classification reads only the
one fresh result, never any historical one (`decisions/0087`'s own
explicit "do not allow historical results to mask a fresh failure").
Mixed results across *different* checks in one report (one `CONFIRMED_
REGRESSION`, one `VERIFIED_SCOPE`, one `VERIFICATION_GAP`) remain
independently visible per check — never collapsed to a single
project-wide verdict.

## 5. Revision consistency for changed-line coordinates (corrects the blocking revision-consistency gap — `decisions/0086` §3)

No `git diff` parser. Four revision concepts, named explicitly:

- **Baseline source revision** — the exact bytes `source_files.
  content_hash` was computed from, for the touched path, the last time
  the target graph was synced.
- **Candidate source revision** — `sha256_file(repo_root / path)`,
  computed live, at assessment time.
- **Revision represented by the source-symbol index** — identical to the
  baseline (`source_symbols.line` values were extracted from exactly the
  bytes `content_hash` describes).
- **Coordinate system for `--changed path:start-end`** — 1-indexed
  physical line numbers in the *candidate* file as it exists on disk at
  `repo_root` right now. This is only a safe coordinate system to resolve
  against `source_symbols.line` when candidate == baseline (below).

**Consistency rule**: for each touched path, compare the live `sha256_
file(repo_root / path)` to the target graph's own `source_files.
content_hash` for that path.
- **Match** → the index's `source_symbols.line` values describe exactly
  the content the given `--changed` ranges are coordinates into; symbol
  resolution (§3) proceeds.
- **Mismatch** → `stale_index`, naming the file; the given line numbers
  are **not** resolved against `source_symbols` (a changed file's own
  internal line numbers may have shifted in ways the stale index cannot
  reflect) — reported as an explicit limitation, never a best-effort
  guess.

This requires the target graph to be freshly re-synced against the exact
checkout under assessment before a meaningful (non-`stale_index`) report
can be produced — a precondition `assess_change_impact.py` checks and
reports on per file, not merely documents as an assumption.

A `--changed` range naming a path with no `source_files` row at all, or
a line range past the end of the resolved file's own extent, is reported
as an explicit "cannot map" finding — never silently defaulted to the
nearest symbol or silently dropped from the report. **Corrected
(`decisions/0089` §B):** both `start` *and* `end` are validated against
the resolved file's own extent (previously only `start` was). A changed
range is resolved against **every** indexed top-level symbol whose own
span (from its own line to one less than the next symbol's line, or EOF
for the last symbol) intersects `[start, end]` — not only the symbol
enclosing `start`. When the matched symbols' combined spans do not cover
the entire requested range (e.g. the range's own start lies in a
top-of-file region before any indexed symbol), the range is reported
`partially_resolved`, naming exactly which line(s) remain unmapped,
while still classifying and assessing every symbol that *was* matched —
a partial match is reported as partial, never silently discarded or
silently presented as complete. Applicable checks are deduplicated
across the matched symbols within one range (the same check triggered
by two touched symbols runs once), while each `AssuranceFinding` records
every symbol that made it applicable, so deduplication never erases
per-symbol provenance.

## 6. Requirement/contract identity for the new obligation (corrects the blocking identity gap — `decisions/0086` §4)

**Chosen design: extend the existing contract and Requirement family in
place** (Option A, over a second contract file/slug — both schema-
supportable in principle, but `check_contracts.py`'s `_iter_contract_
slugs` reads exactly one `oracle-contract.yaml` per slug, making a second
file under the same slug unsupported, and a genuinely separate slug would
duplicate `tested_paths` for what is the same underlying function's
contract; see `decisions/0086`'s own Alternatives section).

- `planning/contracts/balance-from-spec/oracle-contract.yaml` gains one
  new entry under `checks:` (tentative `check_id`: `overlapping-account-
  patterns-no-double-count`), same `contract_id: REQ-BFS-001`, same
  `tested_paths` (unchanged — the new check still only exercises
  `ledgerkit/reports.py`, already in that list).
- `REQ-BFS-001`'s own `statement` is **not edited** — it continues to
  describe exactly the two scopes it always has. A requirement has no
  supersession mechanism (`supersedes` is Claim/Decision-only, confirmed
  by direct reading of `check_supersedes_never_crosses_kind`), so editing
  it in place has no safe precedent and isn't used.
- A new, separate Requirement, `REQ-BFS-002`, states the third obligation
  (the OR-union/no-double-count scope), in the *same*
  `planning/knowledge/balance-from-spec/` slug. A new `DEC-BFS-002`
  (`decides`: CodeCompass additionally pins this third scope, identified
  via Phase 83's own gap-finding methodology — extends, does not
  supersede, `DEC-BFS-001`) and a new `CL-BFS-004` back it.
  `derive_epistemic_profile` does not require a record's own `id` to
  equal `contract_id` — confirmed by direct reading (line 1091-1112): it
  matches purely via each record's own evidence-citation chain against
  whichever `oracle_contract` is passed in. `REQ-BFS-002`/`CL-BFS-004` are
  therefore fully checkable against the one, now-extended contract file
  without needing a contract of their own.
- `CL-BFS-004` reuses `EV-BFS-001` **unchanged** as its relevance
  evidence (it already cites `balance_from_spec` as a whole) and adds
  exactly one genuinely new record, `EV-BFS-004` (`evidence_kind: test`),
  once the new check has a real result to cite.
- **The content-hash cost is explicit, bounded, and handled in the same
  commit**: appending the new check changes `oracle-contract.yaml`'s own
  `sha256`, which (via `evaluate_result_precedence` rule 1) invalidates
  all six of Phase 82's existing `PASS` results for the two pre-existing
  checks on next evaluation — not because those checks changed, but
  because the file they're pinned against did. Resolution, required as
  part of this phase's own deliverables (§7.5): immediately after the
  extended `oracle-contract.yaml` is committed, both pre-existing checks
  are re-run once against the current (unchanged) Ledgerkit HEAD,
  producing two fresh `OracleResult` files carrying the new content hash.
  The original six result files are **never deleted or edited**
  (append-only, Phase 82's own discipline, unchanged) — they remain true
  historical facts, simply excluded from the *current* aggregate exactly
  as a `tested_subject_digest` mismatch already excludes a stale result
  (`decisions/0081` §4). This is verified, not assumed: §9's test list
  includes the before/after aggregate-state check for both pre-existing
  checks.

## 7. Deliverables

**Implementation ordering** (governing prompt §C, 2026-10-28 amendment —
fixed, not left implicit): (1) extend `oracle-contract.yaml` with the new
check (§6); (2) immediately re-run the two *pre-existing* checks fresh
against the real, unmodified Ledgerkit HEAD, producing two new
`OracleResult` files under the new contract content hash, and confirm by
direct inspection that the aggregate `state` for both is `PASS` again
(§6's content-hash-cost resolution) — this step is **not** deferred past
the new check's own commit; (3) author `REQ-BFS-002`/`DEC-BFS-002`/
`CL-BFS-004` (§6) — `CL-BFS-004` cites `EV-BFS-001` only at this point
(relevance), since no real passing result for the new check exists yet;
`EV-BFS-004` (coverage) is **not** authored in this phase — authoring it
would promote a result that does not yet exist for real, and is deferred
until the separately authorised real Ledgerkit test lands (§10/§13); (4)
run the §11 scratch-copy mutation demonstration, entirely on disposable
copies, producing the real CONFIRMED_REGRESSION evidence this phase
exists to demonstrate — kept structurally apart from the canonical record
set in (3) (`planning/retros/`, never `planning/knowledge/` or
`planning/contracts/.../results/`), so an experimental, deliberately
failing scratch result is never reachable as if it were accepted project
evidence; (5) reconcile: re-run `scripts/check_contracts.py --strict` and
`scripts/check_knowledge_base.py --strict` against the real, now-extended
contract/knowledge state, confirming the only new findings are the
expected informational `contract-check-gap` for the new, not-yet-passing-
for-real check (never a blocking finding).

1. `scripts/assess_change_impact.py` (maintainer script, not a shipped
   `codecompass` subcommand — matching `run_balance_from_spec_
   oracle.py`'s own precedent). Inputs, each independently named per
   §9's cross-repository requirement: `--target-repo-root` (the checkout
   under assessment, e.g. `~/projects/ledgerkit`), `--target-graph-db`
   (defaults to `<target-repo-root>/context-graph.db` — explicitly never
   defaults to CodeCompass's own), `--knowledge-root` (defaults to this
   CodeCompass checkout's own root — where `planning/knowledge/` and
   `planning/contracts/` actually live; never assumed to be under
   `--target-repo-root`), `--slug` (the `planning/knowledge/<slug>/`
   directory to assess relevance against), `--changed path:start-end`
   (repeatable explicit line ranges in the *candidate* `--target-repo-
   root` content — see §5 for why this phase does not parse a real `git
   diff`), `--run-checks` (optional: executes applicable checks per §4
   rather than only reporting §3's classification).
   Produces a machine-readable JSON report (per changed range: file,
   enclosing symbol if resolvable, §3 classification, naming Requirement/
   Claim/Evidence ids where relevant, and — when `--run-checks` was
   passed — the §4 CONFIRMED_REGRESSION/VERIFIED_SCOPE/VERIFICATION_GAP/
   INVALID_ASSESSMENT classification with both the observed outcomes list
   and the aggregate state shown explicitly) and a human-readable text
   summary of the same.
2. `oracle-contract.yaml`'s one new check (§6), committed together with
   two freshly re-run `OracleResult` files for the two *pre-existing*
   checks (the content-hash-cost resolution, §6, not deferred).
3. New knowledge records under `planning/knowledge/balance-from-spec/`:
   `REQ-BFS-002`, `DEC-BFS-002`, `CL-BFS-004`, and — once the new
   Ledgerkit test (item 4) has a real result — `EV-BFS-004`. `EV-BFS-001`
   is reused unchanged (§6).
4. One new, real Ledgerkit test (proposed name:
   `TestBalanceFromSpec::test_section_accounts_overlapping_patterns_no_
   double_count`, `accounts=("food", "groceries")` against the pinned
   `filtered.journal` fixture, asserting the `£150.00` groceries posting
   is counted exactly once) — proposed for the real `~/projects/
   ledgerkit` checkout only after §8's comparison has been demonstrated
   on a scratch copy first (§8's own ordering requirement), and only with
   its own separate, explicit go-ahead (cross-repository action, §10).
5. A written demonstration report (`planning/retros/phase-83-...`, at
   closeout) walking through §8's scenarios with real tool output, not
   paraphrased, including the §6 content-hash-cost before/after aggregate
   states.

## 8. Dependencies and prerequisites

Unchanged: Phase 82 only, complete and `done`. No dependency on Phase 84
— this phase queries `source_files`/`source_symbols`/`oracle.py`/
`knowledge_intermediate.py` directly, confirmed still correct by this
amendment's own architecture (§3-§6).

## 9. Explicit exclusions / non-goals

Unchanged from the first pass, restated: no new `context-graph.db` table
or schema change (§3/§5 resolve this phase's needs without one); no
first-party call-graph / inter-procedural static analysis (symbol
localisation is line-range-to-nearest-declaration only, named as a
residual limitation, §12); no `git diff` parsing (§5 uses content-hash
comparison instead); no MCP exposure, no model-routing/scheduling
concept; no `codecompass` CLI command (`assess_change_impact.py` stays a
maintainer script); not a general-purpose coverage-gap finder (§3/§4's
GAP-adjacent findings are scoped to the one slug/contract under test).
**New, from this amendment**: no change to `oracle.py`, `graph.py`, or
`knowledge_intermediate.py` — every correction in this plan is resolved
by how `assess_change_impact.py` itself uses these modules' existing,
unmodified behaviour (`decisions/0086`'s own finding: no defect exists in
Phase 82's own code).

## 10. Tests and independently reproducible negative/mismatch controls

Run against **disposable scratch copies** of `~/projects/ledgerkit`
(Phase 82's own established technique) — never the real checkout for the
regression/negative-control/mismatch runs; the real checkout is touched
only for deliverable 4 (the new test), and only after §8's comparison and
only with separate authorisation.

1. **The regression** (positive detection, §4 rule 1). In a scratch copy,
   apply the double-counting patch to `balance_from_spec`'s OR-union
   loop; re-sync the target graph against this scratch copy (§5's own
   precondition). Run Ledgerkit's full existing `pytest tests/` —
   expect **100% pass**, demonstrating "the ordinary baseline does not
   detect it" directly, by execution, not by assertion. Run the new
   oracle check against the same scratch copy directly via pytest —
   expect a real `FAIL`. Run `assess_change_impact.py --changed
   ledgerkit/reports.py:644-668 --run-checks` — expect §3 classification
   `behavioural_risk` (via `EV-BFS-001`/`CL-BFS-004`) and §4
   classification **CONFIRMED_REGRESSION**, with the report explicitly
   also showing the aggregate `state` as `GAP` alongside it (§4's own
   "both facts shown" requirement) — not one or the other.
2. **Correct-change negative control** (no false regression). In a
   second scratch copy, make an unrelated, safe change inside `reports.
   py`'s `tested_paths` scope but outside `balance_from_spec` (e.g. a
   comment inside `register()`); re-sync. Run the new oracle check —
   expect **PASS**. Run `assess_change_impact.py` with the comment's line
   range — expect §3 classification `no_recorded_relationship` (no
   Evidence cites `register()`) — explicitly distinct from
   `behavioural_risk`, and explicitly *not* worded as "confirmed safe."
3. **No-recorded-relationship control, real** (replaces the first pass's
   mis-specified "GAP" scenario — relabelled honestly, per `decisions/
   0086` §1/E). A real, in-scope change to `ledgerkit/query/regex.py` (a
   `tested_paths` member with, confirmed by direct inspection, zero
   `source`-kind Evidence citing any of its symbols under this slug
   today). Run `assess_change_impact.py` against it — expect §3
   classification `no_recorded_relationship`, with the report stating
   plainly that no relationship is recorded, not that the change is safe.
4. **`relevant_no_coverage_link` control, fixture-based** (not a live
   scenario — honestly, no real instance of this tier currently exists
   in the `balance-from-spec` slug, since every symbol with relevance
   evidence today also has coverage; constructing a fake live instance
   would be invented evidence). A synthetic fixture slug under `tests/
   fixtures/` for `tests/test_assess_change_impact.py`'s own unit tests:
   one `source`-kind Evidence citing a symbol, one Claim citing only that
   Evidence (no companion `test`-kind Evidence). Expect §3 classification
   `relevant_no_coverage_link`.
5. **Stale-index / coordinate-mismatch controls** (§5). (a) Apply a
   mutation to a scratch copy but do **not** re-sync the target graph —
   run `assess_change_impact.py` — expect `stale_index`, naming the file,
   for every touched path. (b) Apply a mutation that inserts several
   lines above `balance_from_spec` in a scratch copy, confirm the
   content-hash mismatch is detected before any line-based resolution is
   attempted. (c) `--changed` naming a path absent from `source_files`,
   and a line number past the resolved file's own extent — expect an
   explicit "cannot map" finding in both cases, never a silent default.
6. **Content-hash-cost regression test** (§6). After extending `oracle-
   contract.yaml`, confirm via `evaluate_result_precedence` that the
   six pre-existing historical result files now independently recompute
   to `INVALID` (contract-hash mismatch) against the new file; after the
   required fresh re-run (§6/§7.2), confirm the aggregate `state` for
   both pre-existing checks is `PASS` again, and that all original six
   result files remain present, unmodified, and schema-valid.
7. **Independent evaluation.** A further run compares `assess_change_
   impact.py`'s own report against the real pytest/oracle output it
   reports on, by direct inspection (mirroring `context-evaluator`'s/
   `v2-evaluation-methodology.md`'s "never trust the tool's self-report
   alone" discipline) — confirming scenario 1's `FAIL` is a real pytest
   failure, not merely the script's own claim of one.
8. **`INVALID_ASSESSMENT` reachability, fixture-driven** (`decisions/
   0087` §2 — the corrected precedence's own required negative coverage,
   each its own case, never inferred from the positive-path tests alone):
   (a) a fresh tested-subject-digest mismatch; (b) a fresh corrupted/
   tampered `raw_output_sha256`; (c) a fresh scope mismatch between a
   result and its named check; (d) a fresh all-skipped pytest execution
   (`decisions/0083`'s own existing rule, surfaced here); (e) a fresh
   oracle-contract-content-hash mismatch. Each asserts **`INVALID_
   ASSESSMENT`** specifically — not merely "not CONFIRMED_REGRESSION" —
   confirming rule 2 of §4's precedence is actually reachable and is
   never pre-empted by the aggregate `state` independently computing
   `GAP` for the same invalid result (which it always does, and which
   must be visible in the report's own aggregate-state field alongside
   `INVALID_ASSESSMENT`, not as a substitute classification).
9. **`VERIFICATION_GAP`, genuine-absence case.** A changed range that
   resolves to `behavioural_risk` in §3 but is run *without*
   `--run-checks` — expect `VERIFICATION_GAP`, explicitly distinguished
   in the report's own text from scenario 8's `INVALID_ASSESSMENT`
   (no attempt at all, vs. an attempt that produced an untrustworthy
   result) — confirming rule 4 is reserved for genuine absence, not a
   catch-all for every non-`PASS`/non-`FAIL` case.

## 11. Dogfood scenario, and the reproducible regression-baseline ordering (`decisions/0086`/`0087`, governing prompt §7/§B)

Scenario 10.1, run end to end against the real Ledgerkit fixture/test
conventions, is the dogfood scenario. The comparison it demonstrates must
be captured **before** deliverable 4's new test is proposed for the real
checkout — adding the test to the real suite changes what "the ordinary
baseline" means from that point on. The new test must not merely be
excluded by a path filter from "the suite used to establish the original
coverage gap" — it must not exist in the tree that suite is run against
at all, by construction (`decisions/0087` §3):

1. A pristine scratch copy is made from Ledgerkit's pinned HEAD
   (`7224bb5c113cd3aad7e86e994365703cd0070154`) — no new test file
   anywhere in its tree. The original baseline is pinned here: the
   commit SHA above, and a `sha256` of `tests/test_reports.py` at this
   exact revision, both recorded verbatim in the demonstration report
   (§7.5) before anything else happens.
2. The mutation patch (recorded verbatim, not described) is applied to
   `ledgerkit/reports.py` only, in this scratch copy.
3. `pytest tests/` is run in **this exact tree** — the new check's own
   test file does not exist in it, so it cannot be included by
   construction. Captured verbatim as the frozen "original, unchanged
   complete suite" result.
4. Only now is the new check's own test function added, as a new file
   (`tests/test_phase83_overlap_regression.py` — never merged into
   `tests/test_reports.py` in the scratch copy, never committed to the
   real `~/projects/ledgerkit` checkout). Run directly by its own pytest
   node id against this mutated tree — expect `FAIL`.
5. A second, separately pinned scratch copy (clean HEAD, same new test
   file, no mutation) confirms the new check `PASS`es on correct code —
   both directions demonstrated, not only the failing one.
6. `assess_change_impact.py --run-checks` against the mutated scratch
   copy from step 4 — expect **CONFIRMED_REGRESSION** (§4).

**Named explicitly, not hidden**: the real `oracle-contract.yaml`'s new
check (§6/§7) has a `check_reference` naming this test's eventual *real*
intended location (`tests/test_reports.py::TestBalanceFromSpec::
test_section_accounts_overlapping_patterns_no_double_count`), which does
not exist in the real, live `~/projects/ledgerkit` checkout as part of
this phase — landing it there is a separately authorised action (§10/
§13). Running the new check for real against the live checkout today
would correctly, honestly classify `INVALID_ASSESSMENT` ("zero collected
tests" — `_classify_pytest_junit`'s own existing, unmodified behaviour
for an unresolvable node id); this is a known, trivially uninformative
outcome, not executed or recorded as a real `OracleResult` in this
phase, and is named as this phase's one explicit, outstanding,
unresolved gate — never silently treated as satisfied.

## 12. Acceptance criteria / exit gate

- Scenario 10.1 demonstrates a real `FAIL` from the new check against a
  real scratch-copy regression, reported as `CONFIRMED_REGRESSION` with
  its co-existing `GAP` aggregate state shown explicitly, while
  Ledgerkit's full real test suite stays green on the same scratch copy
  — captured verbatim in the demonstration report, per §11's ordering.
- Scenario 10.2 demonstrates no false positive, classified
  `no_recorded_relationship`, not `behavioural_risk`.
- Scenario 10.3 demonstrates a real `no_recorded_relationship` finding,
  distinguishable from both `behavioural_risk` and `relevant_no_
  coverage_link` in the tool's own machine-readable output.
- Scenario 10.4 demonstrates `relevant_no_coverage_link` against the
  fixture built for it, honestly labelled as fixture-based.
- Scenario 10.5 demonstrates `stale_index`/"cannot map" findings under
  both an un-re-synced mutation and a shifted-line mutation, never a
  silent best-effort guess.
- Scenario 10.6 demonstrates the content-hash-cost before/after state
  exactly as predicted in §6 — this is the one acceptance item that did
  not exist in the first planning pass.
- Scenario 10.8 demonstrates `INVALID_ASSESSMENT` is actually reachable
  under all five named fresh-invalid conditions, each shown alongside its
  own (near-always `GAP`) aggregate `state` without being mistaken for
  it — the one acceptance item added by the second corrective pass
  (`decisions/0087`).
- Scenario 10.9 demonstrates `VERIFICATION_GAP` is reserved for a genuine
  absence of any verification attempt, distinct from scenario 10.8's
  "attempted but untrustworthy."
- Scenario 10.10 (`decisions/0089` §A) demonstrates that two first-party
  files declaring an identically-named symbol do not inherit each
  other's Evidence — the symbol in the file *not* cited is
  `no_recorded_relationship`, never `relevant_no_coverage_link` or
  `behavioural_risk`, even though a same-named symbol elsewhere in the
  target repository genuinely is cited.
- Scenario 10.11 (`decisions/0089` §B) demonstrates that a `--changed`
  range crossing multiple top-level symbols resolves and independently
  assesses all of them, that a range extending past the file's own
  extent is rejected (`cannot_map`) on `end` exactly as it already was
  on `start`, and that a range partially outside every indexed symbol's
  span is reported `partially_resolved`, naming the unmapped line(s),
  rather than silently discarding the unmatched portion.
- Scenario 10.12 (`decisions/0089` §C) demonstrates that a referenced
  historical result failing schema validation, contract-identity
  matching, or scope matching never establishes `behavioural_risk` —
  the citing symbol falls back to `relevant_no_coverage_link` — while a
  structurally valid, correctly-scoped historical result continues to
  do so exactly as before.
- The real Ledgerkit test (deliverable 4) is reviewed and, if accepted,
  lands in the real checkout only after §11's ordering, with its own
  separate go-ahead (§13).
- No existing Phase 82 safeguard regresses: immutable per-run evidence,
  current-vs-historical distinction, non-vacuous verification, fail-
  closed `INVALID` handling — all exercised unchanged, confirmed by
  re-running Phase 82's existing test suite (`tests/test_oracle.py`,
  `tests/test_check_contracts.py`) unmodified and green after this
  phase's changes, including after the §6 contract extension.

**Corrective-pass re-validation, confirmed (2026-10-28, `decisions/
0089`)**: scenarios 10.1/10.2 were re-run end to end on fresh disposable
scratch copies (pinned Ledgerkit HEAD `7224bb5c1`, identical baseline
file hashes to the original run) after the §A/§B/§C fixes — same
mutation, same 935-passed original-suite result, same `300.00 != 150.00`
new-test failure, same `CONFIRMED_REGRESSION` from
`assess_change_impact.py` itself (fresh=FAIL, aggregate=GAP) on the
mutated copy and `VERIFIED_SCOPE` (fresh=PASS, aggregate=PASS) on the
clean one — using a disposable scratch knowledge-root distinct from
`planning/knowledge/`/`planning/contracts/` (per the standing cross-
repository safeguard, §13). Scenario 10.11's multi-symbol resolution was
additionally confirmed against real Ledgerkit data (`ledgerkit/
reports.py:490-600` resolves all three of `register`/`stats`/
`balance_from_spec`; `ledgerkit/reports.py:644-999999` is rejected
`cannot_map` on `end`). The real, canonical `planning/knowledge/`/
`planning/contracts/` trees were confirmed untouched (`git status`)
throughout.

## 13. Risks, alternatives, and unresolved decisions

**Risks** (first two unchanged from the first pass; third is new):
- The coarse "enclosing-symbol, cited-or-not" heuristic will under-detect
  a regression several call-frames away from any cited symbol, and
  over-detect when a cited symbol's own line range is large and the real
  change is in an unrelated internal branch. Named explicitly; revisited
  only if a later phase's real use shows it matters.
- Proposing a change to the real `~/projects/ledgerkit` checkout is a
  cross-repository, hard-to-reverse-in-spirit action (it's a separate
  project the user also owns) — requires its own explicit go-ahead at
  implementation time, not assumed here.
- **New**: the content-hash-cost resolution (§6) requires the two
  pre-existing checks to actually still pass when re-run against current
  Ledgerkit HEAD before Phase 83's own work can be considered complete —
  if either does not (e.g. an intervening, as-yet-undiscovered drift),
  that is itself a real finding this phase would surface, not a plan
  defect; named here so it is not mistaken for one if it occurs.

**Alternatives considered**: see `decisions/0086`'s own Alternatives
section (a second contract file/slug; editing `REQ-BFS-001` in place;
`test_input_paths`-based coverage inference; a general git-diff parser)
— each rejected with its grounding recorded there, not repeated here.

**Unresolved decisions (recorded, not invented)**:
- Whether `assess_change_impact.py` should eventually become a Phase 84
  API consumer once Phase 84 exists — recorded as the one genuine
  cross-phase integration point, not committed here (Phase 83 must not
  depend on Phase 84, §8).
- The exact tentative `check_id` (`overlapping-account-patterns-no-
  double-count`) and record ids (`REQ-BFS-002`/`DEC-BFS-002`/`CL-BFS-004`/
  `EV-BFS-004`) are proposed, not finalised — Phase 83's first
  implementation commit may adjust naming if a real conflict is found,
  without changing this plan's underlying design.

## 14. Verification (how this phase is confirmed done)

`.venv/bin/python -m pytest` run against the real `~/projects/ledgerkit`
checkout's own `.venv` for every scenario in §10 (each independently
reproducible from this plan's own exact instructions);
`scripts/assess_change_impact.py`'s own new tests
(`tests/test_assess_change_impact.py`, fixture-based for 10.4 and the
unit-level mechanics, no live Ledgerkit network/process dependency there,
mirroring `check_contracts.py`'s own test style); Phase 82's existing
test suite (`tests/test_oracle.py`, `tests/test_check_contracts.py`)
re-run green, including after the §6 contract extension and fresh
re-run; `docs/`/`architecture/` updated for `assess_change_impact.py` (a
new maintainer-script entry); `CHANGELOG.md` entry; `planning/
ROADMAP.md`/`planning/CONTEXT.md` updated; a `planning/retros/
phase-83-semantic-change-assurance.md` retro; `release-phase-auditor`
PASS against this exact plan's own verification steps before `planning/
ROADMAP.md` marks Phase 83 `done` (`CLAUDE.md` §5).
