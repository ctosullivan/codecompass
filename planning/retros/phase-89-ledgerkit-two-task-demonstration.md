# Phase 89 — Ledgerkit two-task demonstration: Task B pre-registration

Written and committed as a **Stage 89A deliverable**, before Stage 89B's
own Task-A demonstration runs — per the fifth/sixth planning amendment's
own sequencing fix (`planning/phase-89-incremental-knowledge-
documentation-reconciliation.md` §0.2.D/§6.3) and the governing
dispatch's §5 instruction: "Before executing Task A's substantive
demonstration, complete and commit the prospective Task B selection
record." Nothing below is adjusted after Task A's own outcome is known —
Task A's real demonstration (§6.1/§6.2 of the plan) has not yet been run
as of this record's own commit.

## 1. Task-selection rule, applied

Per the plan's own §6.3 protocol: run `codecompass knowledge gaps
balance-from-spec` (Phase 84's existing, unmodified `find_gaps` CLI
surface) against the real, current, **pre-Task-A** `balance-from-spec`
knowledge state; select the single gap with the lowest `(kind,
subject_id)` sort key, excluding any gap naming `CL-BFS-004` or
`overlapping-account-patterns-no-double-count` (Task A's own scope).

**Actual output, obtained this session, before any Task-A work**:

```
$ codecompass knowledge gaps balance-from-spec --json
17 gaps total, two kinds:
  stale_test_citation       EV-BFS-002 (single-section expense aggregation)
  stale_test_citation       EV-BFS-003 (multi-section income/expense aggregation with sign inversion)
  unverified_required_scope CL-BFS-001..005 × each of the contract's 3 required scopes (15 gaps)
```

Lowest `(kind, subject_id)` sort key is `("stale_test_citation",
"EV-BFS-002")` — not excluded (it names neither `CL-BFS-004` nor the
overlapping-pattern scope).

**Honest assessment, named plainly rather than mechanically applied**:
every one of these 17 gaps is a *knowledge-verification/maintenance*
finding — `stale_test_citation` means an already-recorded Evidence's
own cited result has gone digest-invalid under the live contract (the
same `oracle_contract_content_hash` drift `scripts/check_contracts.py`
already reports informationally, pre-existing and unrelated to Task A);
`unverified_required_scope` means a Claim cites no *currently-passing*
result for a required scope, for the identical reason. **None of these
17 gaps is an independently-motivated Ledgerkit development task** —
they are all symptoms of the same already-known, pre-existing
contract-hash drift, not a feature gap a developer would pick up and
implement. Selecting `EV-BFS-002`'s own staleness as "Task B" would not
exercise a genuine second development task at all — it would just be
re-running the *first* check again, the opposite of what the roadmap's
own "a second task benefits from the first" exit gate requires.

**Disposition**: the primary rule's own output, while non-empty, does
not satisfy the *intent* of "the genuine second Ledgerkit task" — the
plan's own pre-registered fallback applies.

## 2. Task B (fallback, pre-registered in the plan itself, §6.3)

**Task**: extend `ledgerkit.models.ReportSpec` with a new convenience
constructor — a "combined section" that merges two or more existing
`ReportSection`s' own `accounts` tuples into one new section (e.g.
`ReportSpec.with_combined_section(name, *sections)` or equivalent),
for a user who wants one subtotal spanning what were previously
separate sections (a real, plausible Ledgerkit feature request: "I want
one combined Food+Household row, not two separate ones").

**The concrete implementation decision this task forces**: when two
sections whose own `accounts` patterns can overlap (a posting matching
more than one of the *combined* set's patterns) are merged, must the
new constructor add its own deduplication logic, or can it safely reuse
`balance_from_spec`'s existing OR-union account-matching gate as-is?
Getting this wrong in either direction is a real, plausible bug: adding
unnecessary, incorrect deduplication logic (there's already a working
mechanism) is extra, risky, unneeded code; assuming no dedup is needed
without checking is privileging convenience over correctness.

**Task B's own independent acceptance test**: a new, narrowly-scoped
oracle check (authored before Task B's own implementation begins, under
the same `balance-from-spec` `oracle-contract.yaml`, reusing Phase 82's
unmodified mechanism) asserting the combined section's own subtotal
correctly counts an overlapping posting exactly once against a fixture
constructed specifically to exercise it — never informal pass/fail
judgement.

## 3. Why Task B could benefit from the precise Evidence Task A introduces

Task A's own real demonstration (§6.1 of the plan) upgrades `CL-BFS-
004`'s own `evidence_support_state` from `partially_supported` to
`supported`, citing a new, real, test-kind Evidence record (`EV-BFS-
004`) confirming — by independent, executed verification, not source
reading alone — that `balance_from_spec`'s existing account-matching
gate (`reports.py:663`, `if not any(_matches_pattern(pat, posting.
account) for pat in section.accounts): continue`) already correctly
counts an overlapping posting exactly once. This is exactly the fact
Task B's own implementation decision above turns on: an agent with
access to the *reconciled* (post-Task-A) knowledge state can correctly
answer "no, the combined-section constructor does not need its own
deduplication logic — the existing gate already handles it, and this is
now independently verified, not merely asserted from source reading" —
without re-deriving or re-verifying it from scratch. An agent working
from the *pre-Task-A* knowledge state sees `CL-BFS-004` only
`partially_supported`, with its own statement's own parenthetical
explicitly flagging the behaviour as "confirmed correct by direct
source reading (not yet by an independently executed oracle check...)"
— a materially weaker basis for the same implementation decision.

## 4. New behavioural fact vs. strengthened verification of an existing one

Task A **strengthens verification of an already-asserted fact** — it
does not introduce a new behavioural fact. `CL-BFS-004`'s own statement
already asserted, before Task A, that the existing implementation
counts a posting once regardless of overlapping patterns (derived from
direct source reading, `repository_revision: "ledgerkit@7224bb5c113cd
3aad7e86e994365703cd0070154"`). Task A adds the first-ever independent,
executed, behavioural confirmation of that same fact — changing *how
strongly supported* it is (`partially_supported` → `supported`,
source-kind evidence alone → source-kind plus test-kind evidence), not
*what is asserted*.

## 5. What is expected to differ between treatment and control

- **Development decision**: whether the treatment-arm agent's own
  implementation of the combined-section constructor includes
  unnecessary/incorrect deduplication logic the control-arm agent adds
  (having no independently-verified basis to omit it confidently).
- **Verification result**: Task B's own independent acceptance test
  (§2 above) passes for both arms' *correct* implementations, but is
  the mechanism that would actually catch a wrong deduplication
  decision either arm might make — recorded per arm regardless of
  which way each arm actually implements it.
- **Context-quality outcome**: a fresh, independent `context-evaluator`
  dispatch's own PASS/PASS WITH GAPS/FAIL verdict and LOW/MODERATE/HIGH
  context-advantage rating for each arm's own context packet,
  specifically on the question "does this packet let the agent decide
  the deduplication question correctly, with genuine (not merely
  asserted) justification."

## 6. Success criterion and minimum improvement (reused verbatim from the plan's own §6.3, Phase-89-owned, not borrowed from `planning/v2-evaluation-methodology.md`, which defines no such threshold)

The gate is met when **either** (i) the treatment arm's own acceptance-
test outcome is correct where the control arm's is not, **or** (ii) the
treatment arm's `context-evaluator` verdict is strictly better than the
control arm's own verdict on the fixed three-point scale (FAIL → PASS
WITH GAPS or PASS, or PASS WITH GAPS → PASS) **or** its context-
advantage rating is strictly higher on the fixed three-point scale (LOW
→ MODERATE or HIGH, or MODERATE → HIGH). A tie (identical verdict and
identical rating on both arms) does **not** satisfy the gate, regardless
of acceptance-test outcome agreement.

## 7. Contamination controls

Treatment packet: drawn from the post-Task-A-reconciliation knowledge
state. Control packet: an otherwise byte-identical packet drawn from
the pre-reconciliation snapshot, withholding exactly `EV-BFS-004`/
`CL-BFS-004`'s updated `evidence_support_state` field — never
withholding anything else. A fresh, independent `context-evaluator`
dispatch (never the implementing session) assembles and scores both
arms without being told which is treatment/control. The control arm's
own packet is mechanically generated by re-running the same packet-
assembly code against the pre-reconciliation commit, never hand-edited.
Zero unrelated content may differ between arms — checked mechanically
(a diff of the two packets outside the one named field is itself a
contamination finding, not a pass).

## 8. Explicit limitation, named honestly

Task B's own real-world motivation (a user wanting a "combined section"
convenience feature) is this plan's own invention for evaluation
purposes, not a Ledgerkit maintainer's own filed request — the primary,
objective `find_gaps`-driven selection rule found no genuine,
independently-motivated development task eligible at Stage 89A's own
start (§1), only knowledge-maintenance gaps. This is disclosed here
rather than papered over. The task is nonetheless concretely scoped,
its own acceptance test is real and independently executable, and its
dependence on Task A's own reconciled Evidence is genuine and
specifically named (§3) — not a task picked to flatter a result, since
neither arm's own outcome is known at the time this record is
committed.

## 9. Execution

Task B itself is **not executed** under this dispatch's own
authorisation (Stage 89A only) — its controlled comparison belongs to
Stage 89C. This record is the complete, committed pre-registration
Stage 89C's own implementer must execute against verbatim.
