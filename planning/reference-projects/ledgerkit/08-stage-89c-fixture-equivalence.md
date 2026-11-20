# Phase 89 Stage 89C — pre-dispatch fixture-equivalence and packet-contamination check

Per `planning/phase-89-stage-89c-task-b-controlled-comparison.md` §4.2
and §5. Run before either development arm is dispatched. All commands
executed against disposable scratch state
(`<scratchpad>/stage89c-exec/`) — the real `~/projects/ledgerkit`
checkout and the real `planning/knowledge/balance-from-spec`/
`planning/contracts/balance-from-spec` were never written to (confirmed
both before and after, `git status --short` clean in this repository
throughout).

## Pin check (§1's corrected pinning language)

- Pinned baseline SHA: `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`.
- `git -C ~/projects/ledgerkit cat-file -e a7740fd04fe1814d2a557bfcb67a9a775a4a22f9^{commit}`
  → exit 0 (checkoutable).
- **Real checkout's own current `HEAD`, recorded for transparency only,
  never substituted**: `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` —
  matches the pinned SHA exactly; `git status --short` clean. No drift
  has occurred as of this run.

## §4.2 — seed, fork, equivalence

- Seed clone: `git clone /home/cormac/projects/ledgerkit
  <scratch>/ledgerkit-seed`, checked out to the pinned SHA.
- Forked into `ledgerkit-control` and `ledgerkit-treatment` before
  either was touched.
- Both clones' `git rev-parse HEAD` → `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`.
- `diff -rq --exclude=.git ledgerkit-control ledgerkit-treatment` →
  **empty**.
- No `context-graph.db`/`.claude/commands`/`.claude/skills` in either
  clone — confirmed by direct find.

## §5.2 — shared reference checkout and Task A reconciliation

- One shared clone, `ledgerkit-reference`, pinned SHA, used for **both**
  the reconciliation step and both packet-generation calls below (never
  a separate pristine clone — the digest-compatibility fix).
- Added the pinned test
  `test_section_accounts_overlapping_patterns_no_double_count` to
  `tests/test_reports.py`'s `TestBalanceFromSpec` class (asserts
  `accounts=("food", "groceries")` → `subtotal == Decimal("159.00")`,
  confirming the groceries/coffee postings are each counted once despite
  matching both OR-combined patterns).
- Confirmed directly under the clone's own symlinked `.venv` with
  `PYTHONPATH` override: the new test passes in isolation (`1 passed`);
  the full suite passes with no regression (`936 passed, 14 subtests
  passed`).
- `codecompass knowledge detect-changes balance-from-spec --repo-root
  <ledgerkit-reference> --probe-coverage --json` (run from
  `project-post`, a disposable copy of the real `planning/knowledge/
  balance-from-spec`+`planning/contracts/balance-from-spec`) →
  `"newly_coverable": [{"check_id":
  "overlapping-account-patterns-no-double-count", "claim_id":
  "CL-BFS-004"}]` — exactly as expected.
- `codecompass knowledge verify-changes balance-from-spec --repo-root
  <ledgerkit-reference>` → one-item manifest, `record_id = "CL-BFS-004"`,
  `contributing_labels = ["newly_covered"]`, a real `+dirty` repository
  revision embedding both digests.
- Accepted (`decision = "accept"`) and applied (`codecompass knowledge
  apply`) → `applied: recomputed evidence_support_state='supported';
  evidence: EV-BALANCEFROMS-004`.
- **Confirmed mechanically, not assumed**: `CL-BFS-004.yaml` in
  `project-post` now reads `evidence_support_state: supported`,
  `supporting_evidence: [EV-BFS-001, EV-BALANCEFROMS-004]` (was
  `partially_supported`, `[EV-BFS-001]` in `project-pre`). The Claim's
  own authored `statement` text is **byte-identical, modulo
  whitespace/line-wrap normalisation**, between `project-pre` and
  `project-post` — confirmed by direct `" ".join(text.split())`
  comparison in Python (`True`).

## §5.3 — packet generation

```
( cd project-pre  && codecompass knowledge context CL-BFS-004 --repo-root <ledgerkit-reference> --json ) > control-packet.json
( cd project-post && codecompass knowledge context CL-BFS-004 --repo-root <ledgerkit-reference> --json ) > treatment-packet.json
```

Each call run in its own explicit `cd` subshell. `cmp` confirms the two
output files are **not** byte-identical (differ at byte 960 / line 23).
`control-packet.json`: 94 lines. `treatment-packet.json`: 114 lines.

## §5.4 — mechanical contamination check

`diff <(jq -S . control-packet.json) <(jq -S . treatment-packet.json)`
produced **exactly** the three allowed differences and nothing else:

1. **Genuine treatment information** — one additional item in
   `treatment-packet.json`: `id: "EV-BALANCEFROMS-004"`, `kind:
   "evidence"`, `summary` citing the overlapping-pattern check, its own
   `consistency.source_revision` embedding the expected `+dirty
   (tested_subject_digest=..., test_input_digest=...)` string.
2. **Derived metadata change caused by item 1** — `CL-BFS-004`'s own
   `consistency.knowledge_revision`: `ca41ecd3...` (pre) →
   `4c2653a1...` (post).
3. **The genuine required mechanical signal** — `CL-BFS-004`'s own
   `consistency.reasons`: `"3 required scope(s) have no passing
   evidence at all"` (pre) → `"2 required scope(s) have no passing
   evidence at all"` (post).

`CL-BFS-004`'s own `consistency.status` and `consistency.evidence_currency`
do **not** appear in the diff — confirmed identical in both packets
(both `"unconfirmed"`/`"absent"`, exactly as §1's own corrected finding
predicts). Every other item's own `summary`/`consistency` is
byte-identical between the two packets. **No difference outside the
three allowed categories was found — the contamination check passes.**

## Conclusion

Both scratch clones are verified equivalent; the shared reference
checkout genuinely contains the pinned Task A test and genuinely
produced a real `PASS`-backed reconciliation; the two context packets
differ **only** in the three permitted ways. Setup is clean —
proceeding to dispatch of both development arms.
