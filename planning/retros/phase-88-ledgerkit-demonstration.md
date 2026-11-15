# Phase 88 §12 — Real Ledgerkit Development Demonstration

**What this is**: the real, end-to-end exercise of discovering a genuine
behavioural gap in Ledgerkit, writing the missing regression test,
assessing change-impact, and executing the oracle check — entirely
through the Stage 88A/88B MCP tool surface, using `codecompass.mcp.tools`
functions directly (the same code the real `codecompass mcp-serve`
process dispatches to) as the stand-in for a connected coding agent.

**Scope constraint, honoured throughout**: the real
`~/projects/ledgerkit` checkout was never modified. Per the governing
task's own explicit instruction ("Do not modify the real Ledgerkit
checkout without separate explicit approval... A scratch-copy
demonstration may proceed where permitted, but must be identified as
weaker evidence"), and per the plan's own pre-authorised §12.2
fallback, this demonstration ran against **disposable scratch copies**
only. **This is the weaker, scratch-copy variant, not the real-change
variant** — it does not close Ledgerkit's real, outstanding
`overlapping-account-patterns-no-double-count` gap; it proves the new
test and the full MCP chain are correct and ready to apply, pending
separate, explicit cross-repository authorisation to land them in the
real checkout.

## What was done

1. **Scratch setup**: `cp -r ~/projects/ledgerkit` twice (`correct`,
   `mutated`), both pinned at the real checkout's own current HEAD
   (`a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` — re-confirmed fresh, not
   assumed from the plan's own earlier-recorded, now-stale HEAD).
   Verified both copies' own `pytest`/`.venv` run correctly in isolation.
   A disposable knowledge-root (`planning/contracts/balance-from-spec/`
   + `planning/knowledge/balance-from-spec/`, copied and locally
   `git init`'d for `_git_head_revision` provenance) kept this
   demonstration's own oracle results entirely separate from the real,
   committed `planning/contracts/balance-from-spec/results/`.

2. **Discovery through MCP** (`mcp_tools.knowledge_get`,
   `mcp_tools.oracle_list_checks`, `mcp_tools.impact_classify_change`):
   confirmed `REQ-BFS-001`'s third check,
   `overlapping-account-patterns-no-double-count`, is a real `GAP`;
   retrieved `CL-BFS-004` (the current implementation's exact gate,
   `reports.py` line ~663), `EV-BFS-001` (the function's location and
   role), `CL-BFS-005` (which checks already pass), and — the single
   most materially informing record — `DEC-BFS-002`, which states the
   one existing sibling test
   (`test_section_multiple_accounts_patterns_or_union`) asserts posting
   *membership* only, never the resulting subtotal *arithmetic*.

3. **New test written**, directly shaped by that context: `tests/
   test_reports.py::TestBalanceFromSpec::
   test_section_accounts_overlapping_patterns_no_double_count` asserts
   the actual computed row amount
   (`section_result.rows["expenses:food:groceries"] ==
   Decimal("150.00")`) and the section subtotal (`Decimal("159.00")`) —
   not merely `assertIn`, precisely because `DEC-BFS-002` named that
   exact gap in the sibling test's own style. Uses the real fixture's
   already-present overlapping posting (`expenses:food:groceries`,
   matching both the `"food"` and `"groceries"` section-account
   patterns).

4. **`impact_classify_change`** (via MCP) against `ledgerkit/
   reports.py:600-690` in the `correct` scratch target: classified
   `balance_from_spec` `behavioural_risk` for the two already-covered
   checks, `relevant_no_coverage_link` for the then-still-unverified
   third scope — accurate for the state at that moment (no oracle
   result for the new check existed yet).

5. **`oracle_execute_check`** (via MCP, `--enable-execution` equivalent)
   against the `correct` scratch target: **`outcome: PASS`,
   `aggregate_state: PASS`**. Against the `mutated` scratch target
   (Phase 83's own already-documented double-counting mutation —
   `reports.py`'s single boolean account-pattern gate changed to count
   matching patterns and append once per match — re-applied, not
   reinvented): **`outcome: FAIL`, `aggregate_state: GAP`** (the
   aggregate correctly degrades to `GAP` here, not a stale `PASS`,
   because `evaluate_result_precedence` re-validates the earlier
   `correct`-target result's own digests against the *current*
   `repo_root` supplied — `mutated`'s differing content — finding a
   mismatch; this is the existing, unmodified currency-checking logic
   working exactly as designed, not a new behaviour).

## Independent verification (not self-certified)

A fresh, independent reviewer (`context-evaluator`), with no access to
this session's own conversation, reproduced the negative control from
scratch and separately assessed context relevance:

- **Reproduced directly with `pytest`**, not trusting this session's
  own script output: `correct` copy — new test passes in isolation;
  full suite **936 passed, 0 failed**. `mutated` copy — new test fails
  with exactly `AssertionError: Decimal('300.00') != Decimal('150.00')`;
  full suite **1 failed, 935 passed** — the new test is the *only*
  failure, confirming the existing Ledgerkit suite is genuinely,
  execution-confirmed blind to this defect (matching Phase 83's own
  already-recorded figures exactly).
- **Independently read** `ledgerkit/reports.py:600-690` and
  `tests/test_reports.py`'s sibling test directly (ground truth, not
  via CodeCompass) and judged `DEC-BFS-002`'s claim "literally true and
  materially relevant... genuine, non-rubber-stamp, non-post-hoc
  relevance."
- **Confirmed** `git status`/`git diff` in the real
  `~/projects/ledgerkit` checkout are both empty.
- **Confirmed** the real, committed `planning/contracts/
  balance-from-spec/results/` contains only the two already-known,
  separately-added Stage 88B verification files, and zero
  `overlapping-account-patterns-no-double-count` results — the
  disposable-knowledge-root isolation held.

**Verdict**: all three claims (the new test is a real, correct
regression test; the cited knowledge context was genuinely relevant,
not post-hoc; the real checkout was never touched) independently
verified, no weakening findings.

## Context-quality assessment (plan §12.3)

Folded into the same independent review above (`context-evaluator`'s
own charter: inspect the target repo directly to establish ground
truth, never run CodeCompass to check CodeCompass). Result: the
retrieved context (`DEC-BFS-002` specifically) was correct, relevant,
and materially used — not merely retrieved and ignored. This is
distinct from, and does not retroactively re-litigate, §18.2's own
earlier correction (the `docs_get_grounded_region` tool genuinely has
no *published-documentation* region relevant to this task; the
materially-informing context here comes from `knowledge_get`-surfaced
Claim/Evidence/Decision records instead, exactly as §18.2 redirected).

## Effort and overhead (recorded where feasible, §12.4 — not a
productivity claim)

Development effort: roughly one working session's worth of discovery,
test design, and scratch-environment setup, folded into this same
session alongside Stage 88A/88B implementation — not separately timed
or isolated, so no precise figure is claimed. Verification overhead:
two full scratch-copy pytest runs (~9s each) plus two independent-review
dispatches. No token-consumption metering was available to this agent
directly; no economic or productivity comparison is claimed or implied
— that is Phase 90's own, separately gated scope (§12.4).

## What remains outstanding

- **The real `~/projects/ledgerkit` checkout is unchanged.** Landing
  this exact test (byte-identical to the scratch copy's own addition)
  and, if desired, the underlying `balance_from_spec` fix (none is
  needed here — the real implementation is already correct; this
  demonstration closes a *test-coverage* gap, not a *behavioural* bug)
  requires a separate, explicit cross-repository authorisation this
  task was not given. Until then, `CL-BFS-005`'s own honest statement
  — the third required check has no passing result against the real
  checkout — remains true and unrevised.
- No change was made to `planning/knowledge/balance-from-spec/` or
  `planning/contracts/balance-from-spec/` (the disposable copy used for
  this demonstration is scratch-only, never merged back) — the real
  corpus's own `CL-BFS-005`/gap state is intentionally left exactly as
  it was before this demonstration, since the underlying fact it
  describes (no real passing result yet) has not changed.
