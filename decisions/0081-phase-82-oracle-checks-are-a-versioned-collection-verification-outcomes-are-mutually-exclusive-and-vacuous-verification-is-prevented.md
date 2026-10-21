# 0081. Phase 82's oracle contract gains a versioned, multi-check collection; PASS/FAIL/GAP/INVALID are made mutually exclusive by explicit precedence; vacuous verification is structurally prevented; tested-subject digesting is scoped and specified precisely

## Status

Accepted (2026-10-21, direct user request — "CodeCompass Orchestrator —
Correct Phase 82 Plan and Proceed with Implementation"). Extends, does not
reverse, `decisions/0080` (the derived epistemic view and the oracle-
result identity fields it introduced both stand unchanged). Corrects four
remaining structural gaps in `planning/phase-82-contract-and-evidence-
foundation.md` found by direct review against the real schema and the
real Ledgerkit checkout, not by further abstract design. This ADR also
records the explicit authorisation to proceed with Phase 82
implementation — superseding §9's "requires explicit maintainer approval
before any code is written" gate, which is satisfied by this same
governing prompt.

## Context

**Verified current state**: `HEAD` was exactly `2750752` before this
amendment, confirmed against the governing prompt's own stated starting
commit (`2750752...`) with zero drift. Phase 82 remained `planned`, not
implemented, before this ADR — confirmed by `grep -r` across `src/`
finding no `oracle`, `contract`, or `epistemic_profile` symbol anywhere,
and no `planning/contracts/` directory.

Four structural gaps remained in the plan `decisions/0080` left otherwise
correct:

**A. The plan named a singular `check_reference`/`scope`/`required` on
the contract while simultaneously requiring "multiple checks across
distinct conditions."** A contract with exactly one check cannot express
"verified under integer inputs, untested under fractional inputs" (the
very example `decisions/0080` used to justify scope-qualified
verification) — the contract schema itself needed a `checks:` collection,
not a single check masquerading as the whole contract. Reviewing real
Ledgerkit test coverage for `balance_from_spec`
(`~/projects/ledgerkit/tests/test_reports.py::TestBalanceFromSpec`,
confirmed present this session) found two genuinely distinct, already-
passing scopes worth pinning: single-section aggregation
(`test_single_section_rows_and_subtotal`) and multi-section aggregation
with sign inversion (`test_multi_section_correct_values`) — these become
the contract's first two real checks, not invented fixtures.

**B. PASS/FAIL/GAP/INVALID were defined in prose but not given a
mechanical precedence/aggregation rule.** Without an explicit rule, an
implementation could plausibly let a `FAIL` be silently reported as `GAP`
("well, there's no *passing* result") or an `INVALID` run be dropped
entirely from aggregation (indistinguishable from "never ran"). The
governing prompt's own definitions are adopted verbatim and given a
deterministic precedence order (Decision §2 below) so a validator, not
prose, decides.

**C. Nothing prevented an empty required-check set, a missing contract,
or an unresolvable evidence chain from producing `status: verified`
anyway** — `decisions/0080`'s own
`check_verified_status_cites_passing_oracle_result` was specified against
"every `required: true` check," which is vacuously true for a contract
with zero checks or no contract at all. Separately, twelve pre-existing
records already carry `status: verified` from before this phase existed
(`REQ-DOCORIGIN-001/002/003`, `REQ-HSAPI-001` through `-006`,
`CL-DEPTH-001`, `CL-FPSS-006/007` — confirmed by direct `grep` this
session), none of which has or needs an oracle contract. These must not
be silently grandfathered forever (the governing prompt's own "rather
than silently accepted" instruction) nor retroactively broken by a check
that didn't exist when they were written.

**D. `tested_subject_digest`'s own contents and boundaries were named in
principle (`decisions/0080` §2) but never pinned to actual files**,
leaving "the oracle's own relevant source tree" undefined for a real
contract. Direct inspection of `balance_from_spec`'s own import graph
(`ledgerkit/reports.py`'s module-level imports, confirmed this session)
gives the real, closed dependency set this ADR names below — not
Ledgerkit's entire package, which would make the digest unnecessarily
brittle to unrelated changes (e.g. a CLI formatting change) without
making it any more precise about what was actually exercised.

## Decision

### 1. `oracle-contract.yaml` gains an explicit, versioned `checks:` collection

```yaml
schema_version: 1
contract_id: REQ-<slug>-NNN
tested_paths:        # D — exactly what tested_subject_digest covers
  - ledgerkit/reports.py
  - ledgerkit/models.py
  - ledgerkit/parser.py
  - ledgerkit/query/ast.py
  - ledgerkit/query/depth.py
  - ledgerkit/query/eval.py
  - ledgerkit/query/regex.py
  - ledgerkit/query/compat.py
checks:
  - check_id: <stable, contract-local identity, e.g. "single-section-expense-subtotal">
    scope: <free-text condition set, e.g. "single-section expense aggregation">
    execution_provider: pytest
    check_reference: <a pytest node id>
    test_input_paths:  # D — exactly what test_input_digest covers for THIS check
      - tests/test_reports.py
      - tests/fixtures/filtered.journal
    required: true
```

`contract_id` is the single, unambiguous name for "the accepted contract"
— the earlier plan's `contract_id`/`oracle_contract_id` duplication is
resolved by making `oracle_contract_id` (on a result) always and only
mean "the `contract_id` of the `oracle-contract.yaml` this result was
evaluated against," never a second, independent identity. `checks` is a
flat list, each with its own stable `check_id` (contract-local, not
globally unique — qualified by `contract_id` wherever cited), own
`scope`, own `execution_provider`, own `check_reference`, own `required`
flag, and — new — its own `test_input_paths`, since two checks against
the same implementation can legitimately read different fixtures (the
earlier single-check design had nowhere to put this per-check). No
provider-plugin system is introduced: `execution_provider` remains a
closed, named value (`pytest` is the only one Phase 82 implements), not
an extensible registry — adding a second provider kind is a future
phase's decision, made when a second real need exists, per
`conditional-generalisation.md`'s own discipline.

An `oracle-result.yaml` names exactly one `check_id` (not the whole
contract) and must carry a `scope` equal to that check's own `scope` —
checked mechanically (§8 below), closing the "oracle results
unambiguously identify the exact check and accepted contract version
tested" requirement.

### 2. PASS/FAIL/GAP/INVALID: mutually exclusive by explicit precedence and aggregation rule

**Per-result outcome** (unchanged from the governing prompt's own
definitions, now load-bearing, not merely descriptive):

- **PASS** — a valid execution (resolvable tested-subject/test-input
  digests, resolvable raw output, matching scope) satisfies the check.
- **FAIL** — a valid execution demonstrates the check is *not* satisfied.
- **INVALID** — the execution or its supporting evidence cannot be
  trusted or validated (unresolvable digest, tampered/missing raw output,
  mismatched scope, missing `invalid_reason`).
- **GAP** — never a per-result outcome a run produces about itself; see
  below.

**Per-result precedence, evaluated in this fixed order** — the first
rule that applies wins, and later rules never override an earlier one:

1. If the execution's `tested_subject_digest`, `test_input_digest`,
   `oracle_contract_content_hash`, or `raw_output_sha256` cannot be
   independently recomputed to match what is recorded → `INVALID`
   (regardless of what the run's own `outcome` field claims).
2. Else if `scope` does not match the named check's own `scope` →
   `INVALID` (a result cannot silently count toward a different
   condition than the one it actually ran under).
3. Else the recorded `outcome` (`PASS`/`FAIL`/`INVALID`, as the execution
   itself determined) stands.

**A `FAIL` or `INVALID` result is never reclassified as "missing
evidence."** `GAP` is reserved exclusively for the aggregate,
per-check-per-scope determination, never written by an execution about
itself:

**Aggregate, per `(contract_id, check_id)`** — computed by the validator,
never trusted from a self-reported field (continuing
`decisions/0080`'s own "the validator computes GAP, it does not merely
echo it"):

- **GAP** iff `required: true` and no result satisfies precedence rule 3
  with `outcome: PASS` — this is the *only* path to `GAP`; a `FAIL`
  result existing for that check does not change this to "worse than
  GAP," it coexists (both facts are true and both are reported: *a
  FAIL was observed, and the required check currently has no passing
  evidence*).
- **Aggregate assurance status for a contract** is the union of its own
  per-check states, never collapsed to one value: "2/2 required checks
  PASS," "1/2 PASS, 1/2 GAP," "1/2 PASS, 1/2 FAIL (a real regression),"
  are three different, distinguishable aggregate reports — exactly
  mirroring §1's per-scope `verified_scopes`/`known_gap_scopes` split
  from `decisions/0080`, now stated as the aggregation rule that produces
  it, not merely its output shape.

This closes the governing prompt's "a failed or invalid run must never
be silently reclassified as merely missing evidence" requirement
mechanically: `FAIL` and `INVALID` are per-result facts that persist in
the record set forever (new Evidence/oracle-result files, never
overwritten — Phase 81's own existing conflict-retention discipline,
reused unchanged); `GAP` is a separately-computed aggregate fact about
the *absence* of a passing result, and computing it never consults or
overwrites a `FAIL`/`INVALID` result's own outcome field.

### 3. Vacuous verification is structurally prevented; existing `verified` records are an explicit, named compatibility class

`check_verified_status_cites_passing_oracle_result` (`decisions/0080`) is
corrected to fail closed, not vacuously pass, on each of:

- **Empty or absent required-check set**: a record whose contract has
  zero `required: true` checks, or no resolvable `oracle-contract.yaml`
  at all, **can never satisfy `status: verified`** under this check — a
  missing mandatory check set is treated as "nothing has been verified,"
  never as "nothing was required."
- **Unresolvable evidence chain**: a `test_ref` that does not resolve to
  a real, schema-valid `oracle-result.yaml` is treated identically to no
  evidence at all, never silently skipped.

**Compatibility policy for the twelve pre-existing `status: verified`
records** (named explicitly, per the governing prompt's own "rather than
silently accepted or destructively rewritten" instruction):
`check_verified_status_cites_passing_oracle_result` applies **only to a
record whose owning slug (`planning/knowledge/<slug>/`) has a
`planning/contracts/<slug>/` directory in the first place.** A slug with
no contract directory is untouched by this check — its pre-existing
`status: verified` records keep exactly the meaning they always had, not
downgraded and not reinterpreted. This is a **named, explicit,
documented exemption**, not a silent grandfather clause: every one of
the twelve records is listed above, in this ADR's own Context section,
so a future reader can find them without re-deriving the list, and a
future phase may choose to require contracts project-wide once real use
justifies that cost (`conditional-generalisation.md`'s own discipline —
not pre-committed here). `balance-from-spec` (this phase's own one real
contract) is the only slug this check actually gates today.

### 4. `tested_subject_digest`/`test_input_digest` are scoped to named, reviewable file lists, not an entire package

Per §1's `tested_paths` (contract-level, what implementation is being
verified) and per-check `test_input_paths` (what fixture/test-code
defines the check) — both explicit, committed, human-reviewable lists,
not a directory glob that could silently grow or shrink its own meaning.
**Dirty worktrees, changed fixtures, stale results, and unavailable
inputs** are handled identically at digest-computation time: any named
path that cannot be read (missing file, unreadable, or — for a future
non-file-based provider — any other unresolvable input) makes the digest
computation itself fail, and the calling run is recorded `INVALID` with
an explicit `invalid_reason` naming the unresolvable path; a digest is
never computed over a partial file set and presented as if complete. A
dirty worktree does not need special-case detection: the digest is
always computed from whatever bytes are actually on disk at run time
(matching Phase 81B's own `payload_tree_sha256` precedent, which has the
same property) — a dirty worktree simply produces a different, equally
valid digest than a clean one, which is exactly the mechanism that makes
a dirty-worktree run distinguishable from a clean-commit run in the first
place (`decisions/0080`'s own original rationale for choosing a content
digest over a commit SHA). **Historically valid evidence is distinguished
from evidence applicable to the current implementation** purely by digest
comparison: an old `PASS` result's own `tested_subject_digest` either
matches the live, current digest (still applicable) or it does not (the
result remains a true historical fact — never deleted, never
"corrected" — but is excluded from the current aggregate GAP/PASS
computation in §2, which only ever considers results whose digests match
the implementation's *current* state).

### 5. Explicit authorisation to implement

This governing prompt explicitly approves proceeding with Phase 82
implementation after the corrections above, incorporating
`decisions/0080`'s derived epistemic model and strengthened oracle-result
identity design unchanged. `planning/phase-82-contract-and-evidence-
foundation.md` §9's prior "requires explicit maintainer approval before
any code is written" gate is satisfied by this same instruction — no
further sign-off step is inserted before implementation begins.

## Alternatives considered

- **A provider-plugin registry for `execution_provider`** (so a future
  property-test or static-checker provider could register itself).
  Rejected: no second provider exists yet; the governing prompt itself
  names "avoid designing a general-purpose execution-provider framework"
  — a closed, single-value field costs nothing to extend later (add a
  second accepted value) and nothing is lost by not building the
  registry now.
- **A single aggregate `verified: bool` per contract**, computed from all
  checks' own worst-case outcome. Rejected: collapses exactly the
  scope-qualified distinction `decisions/0080` §1 already established as
  load-bearing — "2/2 PASS" and "1/2 PASS, 1/2 FAIL" must stay
  distinguishable, not both reduced to `False`.
- **Retroactively requiring an oracle contract for the twelve existing
  `status: verified` records**, to make the new check universally
  enforced from day one. Rejected: none of those records' own subject
  matter has anything resembling a pinned external reference-project
  oracle scenario; manufacturing one purely to satisfy a new validator
  would be evidence invented to fit a rule, the opposite of this
  project's own evidentiary discipline.
- **Silently exempting any future `status: verified` record with no
  contract**, rather than naming today's twelve explicitly. Rejected:
  the governing prompt's own instruction requires this be an
  *explicitly documented* policy — an open-ended, unnamed exemption would
  let the gap grow invisibly; naming the twelve now and tying the
  exemption to "no contract directory exists for this slug" (a
  mechanically checkable condition, not an ad hoc allow-list) keeps the
  policy auditable going forward.

## Consequences

- `planning/phase-82-contract-and-evidence-foundation.md` gains a new
  §14 recording this amendment, and §5/§8/§9 are updated to reflect the
  `checks:` collection, the precedence/aggregation rule, the
  compatibility policy, and the removal of §9's implementation-blocking
  gate (superseded by this ADR's §5).
- `src/codecompass/oracle.py` (new), `scripts/check_contracts.py` (new),
  and additions to `src/codecompass/knowledge_intermediate.py` and
  `scripts/check_knowledge_base.py` are this ADR's own implementation —
  built in the same work session as this ADR, not deferred.
- `decisions/0078`, `0079`, and `0080` are not edited.
