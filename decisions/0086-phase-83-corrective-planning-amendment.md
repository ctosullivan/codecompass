# 0086. Phase 83 corrective planning amendment: behavioural coverage is claim-mediated, not `test_input_paths`-inferred; FAIL is never downgraded to GAP; revision consistency reuses `source_files.content_hash`; the new obligation extends the existing contract in place

## Status

Accepted (2026-10-24, direct user request — "CodeCompass Orchestrator —
Phase 83 Corrective Planning Amendment"). Amends
`planning/phase-83-semantic-change-assurance.md` in place (the plan file
itself, not this ADR, carries the full revised design — this ADR records
why). Does not reverse `decisions/0078`-`0085`; corrects five structural
gaps in Phase 83's *own* first planning pass (produced the same day,
before implementation began — no code was written against the uncorrected
design). Planning amendment only: this ADR does not authorise Phase 83
implementation.

## Context

**Verified this session, not carried over**: Ledgerkit's HEAD is still
`7224bb5c113cd3aad7e86e994365703cd0070154` (2026-10-03T00:51:43+08:00),
unchanged since the prior planning pass — the regression scenario's own
grounding (§2 of the plan file) needed no re-verification. Ledgerkit's
working tree is *not* clean (`dev-docs/clean-room/compliance-log.md`
modified, an untracked `implementation-reconstruction/` directory) —
neither touches `ledgerkit/` package code, but this is itself evidence
for §4 below: a real checkout's git state and its actually-synced content
are two different things, confirming `oracle.py`'s own existing
content-digest-over-git-SHA design choice (`decisions/0081` §4) is the
right building block to reuse here too, not a coincidence specific to
Phase 82.

Direct re-reading of `src/codecompass/oracle.py`,
`src/codecompass/graph.py`, `src/codecompass/knowledge_intermediate.py`
(`derive_epistemic_profile`, line 1004), `scripts/check_contracts.py`,
and the real `planning/knowledge/balance-from-spec/`/`planning/contracts/
balance-from-spec/` record set found five concrete defects in the first
Phase 83 plan, each with a verified, grounded correction:

**A. `test_input_paths` was used as behavioural-coverage evidence; it
isn't one.** `test_input_paths` is the file list a check's
`test_input_digest` is computed over (`decisions/0081` §4) — a
file-integrity boundary, not a claim about what the test exercises. The
plan's GAP step conflated "this fixture file happens to be named in some
check" with "a check actually exercises the construct that changed."
Direct reading of `derive_epistemic_profile` (line 1082-1112) found the
real, already-existing mechanism that *does* establish this, unused by
the first plan: a Claim's own `supporting_evidence` list already bridges
a `source`-kind Evidence (naming an implementation symbol via
`source_ref`, e.g. `EV-BFS-001`: `"ledgerkit/reports.py:600 def
balance_from_spec"`) and a `test`-kind Evidence (naming a passing result
via `test_ref`, e.g. `EV-BFS-002`/`EV-BFS-003`) for the *same* behavioural
scope. This is exactly the curated, human-asserted, already-real
relationship the governing prompt asked for — "using existing knowledge
records and evidence relationships wherever sufficient" — not a new
mechanism.

**B. The plan's regression scenario expected a check's aggregate to show
`FAIL`; `aggregate_contract` has no `FAIL` state.** Direct reading of
`oracle.py` (`CheckAggregate.state`, line 781) confirms only three
aggregate states exist: `PASS`, `GAP`, `NOT_REQUIRED` — `GAP` is returned
whenever a required check has no passing result, *including* when a real
`FAIL` was observed (`decisions/0081` §2's own text: "a FAIL result
existing for that check does not change this to 'worse than GAP,' it
coexists"). `observed_outcomes` (plural, retained forever) is where a
real `FAIL` is visible; `state` (singular, aggregate) is where `GAP`
lives. The first plan's scenario 1 narrative ("the new check's real FAIL
surfaced in the aggregate") does not describe any value `aggregate_
contract` can actually produce.

**C. Revision consistency for changed-line coordinates had no concrete
mechanism — "graph rebuild timestamp" was the only signal named, and it
is repo-wide, not per-file.** Direct reading of `graph.py` (`source_files`,
line 73) found `content_hash` (`sha256` of the exact file bytes last
synced — `source_symbols.py`/`sync.py` line 366, identical construction
to `oracle.sha256_file`) already recorded per file. This is the minimal,
already-existing mechanism the governing prompt asked for in preference
to a new git-diff parser.

**D. The new obligation's contract/requirement placement was left
undecided, and the one option the first plan implicitly favoured (a
second `oracle-contract.yaml` under the same slug) is not supported by
`check_contracts.py::_iter_contract_slugs`**, which reads exactly one
`oracle-contract.yaml` per slug directory. Separately, `scripts/
check_knowledge_base.py`'s own `check_supersedes_never_crosses_kind`
confirms `supersedes` is a Claim/Decision-only field — a Requirement has
no supersession mechanism, so editing `REQ-BFS-001`'s own `statement` in
place (the first plan's other implicit option) has no precedent and no
safe alternative to an in-place edit of an already-`implemented` record.
Direct reading of `evaluate_result_precedence` (line 726) found the real,
previously unstated cost of the only schema-compliant option (extending
the existing `oracle-contract.yaml`'s `checks:` list in place): rule 1
recomputes `sha256_file(contract_path)` and compares it to each existing
result's own recorded `oracle_contract_content_hash` — appending even one
check changes the file's hash, which would make all six of Phase 82's
own already-accepted `PASS` results for the two existing checks
recompute to `INVALID` on next evaluation, not because anything about
those two checks changed, but because the file they're pinned against
did. This is real and must be named, not discovered during
implementation.

**E. The classification language (`structural_only`/`behavioural_risk`)
implied a touched symbol with no citation was "structurally safe."**
Direct re-reading of §0's own schema findings confirms no first-party
call-graph exists anywhere in `graph.py` — so "no Evidence cites this
symbol" can mean either "genuinely irrelevant" or "relevant, but nobody
has recorded that relationship yet," and the first plan's two-way split
could not tell these apart.

## Decision

### 1. Behavioural coverage is Claim-mediated, three-tier, and separate from relevance (corrects A, E)

A touched symbol's relevance/coverage classification has three tiers
(`planning/phase-83-semantic-change-assurance.md` §3.3-3.4 for the full
mechanics), replacing the two-way `structural_only`/`behavioural_risk`
split:

- **`no_recorded_relationship`** — no `source`-kind Evidence anywhere
  under the target slug cites this symbol via `source_ref`. Reported as
  exactly that — an absence of recorded knowledge, never "safe," never
  "structural only" (§8's own correction: absence of a relationship does
  not establish absence of risk).
- **`relevant_no_coverage_link`** — a `source`-kind Evidence cites the
  symbol, but no Claim citing that Evidence in its own `supporting_
  evidence` also cites a `test`-kind Evidence resolving (via `test_ref`
  → a real `OracleResult.check_id`) to any check. Relevance is
  established; behavioural coverage is not — reported as an explicit
  evidence limitation.
- **`behavioural_risk`** — a Claim cites both a `source`-kind Evidence
  naming the symbol and a `test`-kind Evidence resolving to a specific
  check. That check becomes "applicable" and, with `--run-checks`, is
  independently re-executed (§2 below).

### 2. Assurance-report semantics never let GAP absorb an observed FAIL (corrects B)

Deterministic precedence over an applicable check's real, freshly
executed results (never a historical/cached result for this purpose):

1. Any observed outcome (via `evaluate_result_precedence`, live
   `repo_root` supplied) is `FAIL` → **CONFIRMED_REGRESSION**. Highest
   precedence; never downgraded by rule 3 below.
2. Else the check's aggregate `state` (via `aggregate_contract`, same
   live `repo_root`) is `PASS` → **VERIFIED_SCOPE**.
3. Else the aggregate `state` is `GAP` → **VERIFICATION_GAP**.
4. Else any observed outcome is `INVALID` → **INVALID_ASSESSMENT**.

A report showing `CONFIRMED_REGRESSION` always also shows the underlying
aggregate `state` (which will usually be `GAP`, per `decisions/0081`
§2 — no passing result exists) *and* the observed `FAIL`, labelled as
two co-existing, independently true facts, exactly as `0081` §2 already
requires — never collapsed to one line that could read as "merely no
evidence."

### 3. Revision consistency reuses `source_files.content_hash` (corrects C)

No git-diff parser. A touched file's `--changed path:start-end` input is
accepted only when `sha256_file(repo_root / path)` (computed live) equals
the target graph's own `source_files.content_hash` for that path — i.e.
the index was built from exactly the content being assessed. On a
mismatch: `stale_index`, naming the file, and no attempt to resolve the
given line numbers against (possibly shifted) `source_symbols.line`
values. On a match: the given line numbers and `source_symbols.line`
share one coordinate system by construction (both describe the same
on-disk bytes), so resolution to an enclosing symbol is sound. This
requires the target graph to be freshly re-synced against the exact
checkout under assessment before `assess_change_impact.py` is run against
it — a precondition the tool itself checks and reports on per file,
rather than assumes.

### 4. The new obligation extends the existing contract and Requirement family in place; the content-hash cost is explicit and handled once (corrects D)

`planning/contracts/balance-from-spec/oracle-contract.yaml` gains one new
check (new `check_id`, same `contract_id: REQ-BFS-001`, same `tested_
paths`) rather than a second contract file or slug. `REQ-BFS-001`'s own
`statement` is **not** edited — it continues to describe exactly the two
scopes it always has. A new, separate Requirement (`REQ-BFS-002`) states
the third, OR-union obligation, in the *same* `planning/knowledge/
balance-from-spec/` slug, with its own new `DEC-BFS-002` (extending, not
superseding, `DEC-BFS-001`) and `CL-BFS-004`. `derive_epistemic_profile`
does not require a record's own `id` to equal the contract's
`contract_id` (confirmed by direct reading, line 1091-1112: it matches
purely via each record's own evidence-citation chain against whichever
`oracle_contract` object is passed to it) — so `REQ-BFS-002`/`CL-BFS-004`
are fully checkable against the same, single, extended contract file
without needing their own.

`CL-BFS-004` reuses `EV-BFS-001` unchanged as its source-evidence (it
already cites `balance_from_spec` as a whole — no new source citation is
needed) and adds exactly one new Evidence record, `EV-BFS-004`
(test-kind), once the new check has a real result.

**The content-hash cost, named and handled**: appending the new check
changes `oracle-contract.yaml`'s own `sha256`, which invalidates (via
`evaluate_result_precedence` rule 1) all six of Phase 82's existing
`PASS` results for the two pre-existing checks — not because those checks
changed, but because the file now hashes differently. This is accepted
as a bounded, explicit, one-time cost: immediately after committing the
extended contract file, both pre-existing checks are re-run once against
the current (unchanged) Ledgerkit HEAD, producing two fresh `OracleResult`
files carrying the new content hash. The original six result files are
never deleted or edited (append-only, unchanged from Phase 82's own
discipline) — they remain true historical facts, simply excluded from
the *current* aggregate the same way a `tested_subject_digest` mismatch
already excludes a stale result (`decisions/0081` §4's own "historically
valid vs. applicable-to-current" distinction, now shown to apply to a
contract-hash change too, not only a source change). A test asserting
exactly this (old results → `INVALID` against the new file; fresh results
→ `PASS`; aggregate for the two original checks is `PASS` again after the
fresh run) is required before Phase 83 can be considered to have
preserved Phase 82's guarantees.

## Alternatives considered

- **A second `oracle-contract.yaml`/slug for the new obligation** (the
  first plan's other implicit option). Rejected: avoids the content-hash
  cost entirely, but splits one function's behavioural contract across
  two independently-tracked contracts/slugs with duplicated `tested_
  paths`, and is not what `check_contracts.py`'s single-contract-per-slug
  model is built around — the governing prompt's own "do not invent an
  unsupported multi-contract directory structure" rules it out as the
  *supported* shape, and the duplication cost is worse than the bounded,
  one-time re-run cost of the chosen option.
- **Editing `REQ-BFS-001`'s own `statement` in place.** Rejected: no
  precedent for editing an `implemented` Requirement's statement, no
  supersession mechanism exists for Requirements at all (confirmed:
  `supersedes` is Claim/Decision-only), and it would retroactively change
  what an already-accepted record always meant.
- **Inferring coverage from `test_input_paths` membership** (the original
  design). Rejected outright per the governing prompt — confirmed by
  direct reading to establish file-integrity scope, not behavioural
  exercise.
- **A general git-diff parser for revision consistency.** Rejected for
  this phase: `source_files.content_hash` already gives an equivalent,
  per-file, already-computed signal; a diff parser solves a broader
  problem (line-shift tracking across a real diff) this phase's bounded
  scope does not need yet.

## Consequences

- `planning/phase-83-semantic-change-assurance.md` is rewritten in place
  (same file, new content) to carry this design — §0, §2, §3, §7, §8, §9,
  §10 all change materially; §1, §5, §6's substance is preserved.
- No change to `src/codecompass/oracle.py`, `graph.py`, or
  `knowledge_intermediate.py` — every correction above is resolved by how
  Phase 83's *own* new code (`scripts/assess_change_impact.py`, not yet
  written) uses these modules' existing, unmodified behaviour, confirming
  the governing prompt's "preserve the existing Phase 82 oracle-result
  schema... unless a verified defect requires a separately justified
  correction" — no such defect was found in Phase 82's own code.
- `decisions/0078`-`0085` are not edited.
