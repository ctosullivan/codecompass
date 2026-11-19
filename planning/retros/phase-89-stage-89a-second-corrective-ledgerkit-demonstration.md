# Phase 89 Stage 89A second corrective pass — real Ledgerkit demonstration log

2026-11-18. All commands below were run against disposable scratch
copies under `/tmp/.../phase89a-defectAB-demo/` (`cp -r ~/projects/
ledgerkit <scratch>`, never a git clone, never the real checkout),
paired with a disposable scratch copy of the real `planning/knowledge/
balance-from-spec/` + `planning/contracts/balance-from-spec/`
directories (never the real `codecompass` knowledge base). `~/projects/
ledgerkit`'s own `git status --porcelain`/`git rev-parse HEAD`
(`a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`) were confirmed clean and
unchanged both before this demonstration began and again after it
completed. The real `codecompass` repository's own `planning/knowledge/
balance-from-spec/` and `planning/contracts/balance-from-spec/` were
confirmed untouched throughout (`git status --porcelain` against both
paths returns nothing).

All commands used the real CLI (`/home/cormac/projects/codecompass/
.venv/bin/codecompass knowledge ...`), run from the disposable
knowledge-root (`cc-root/`) against the disposable Ledgerkit checkout
(`ledgerkit/`) via `--repo-root`. Graph re-sync for the one edited
`.py` file was performed directly against the scratch checkout's own
copied `context-graph.db` (a raw `UPDATE source_files SET content_hash
= ? WHERE path = ?`), functionally identical to what a full `codecompass
sync` would record for that one file, matching the prior corrective
pass's own established, lighter-weight technique (never invoking the
full indexing/enrichment pipeline this demonstration does not exercise).

Real `CL-BFS-001`/`CL-BFS-002` are already `evidence_support_state:
supported` in the production knowledge base — a fresh re-confirmation
is a deliberate, documented no-op (`decisions/0096` §4.3), which would
mask the Claim-scope behaviour this demonstration is specifically
about. In this scratch copy only, both Claims' `status`/`evidence_
support_state` were temporarily set to `proposed`/`partially_supported`
before the demonstration (the same technique the first corrective
pass's own Ledgerkit demonstration log already used and disclosed).

## Steps 1-9 — the mandatory Claim-scope regression (dispatch §2)

**Step 1 — original state.** `CL-BFS-001`/`CL-BFS-002`: single-check
Claims, no `depends_on`. `CL-BFS-003`: `status: superseded`,
`depends_on: [CL-BFS-001, CL-BFS-002]`. `CL-BFS-005`: `status:
supported`, `evidence_support_state: partially_supported`, `depends_on:
[CL-BFS-001, CL-BFS-002]` — the contract's third required check
(`overlapping-account-patterns-no-double-count`) has no passing result
yet. `CL-BFS-004`: `partially_supported`, source-only Evidence, no test
coverage yet (detector (b)'s own scope).

Established baselines (`--establish-baselines`) for all three real
tracked files, confirming the non-Python fixture `tests/fixtures/
filtered.journal` gets a real baseline entry too, unaffected by this
corrective pass:

```
codecompass knowledge detect-changes balance-from-spec --repo-root <ledgerkit> --establish-baselines --json
```

**Step 2 — modify only `tests/test_reports.py`.** Added a real,
assertion-preserving comment inside
`test_single_section_rows_and_subtotal`. No other file in the scratch
Ledgerkit was touched.

**Step 3 — both existing checks detected.** After re-syncing the one
changed file's hash:

```
codecompass knowledge detect-changes balance-from-spec --repo-root <ledgerkit> --json
```

```json
{"path": "tests/test_reports.py", "resolution": "test_input_change", "check_id": "multi-section-income-expense-subtotal", "claim_ids": ["CL-BFS-002", "CL-BFS-003", "CL-BFS-005"]}
{"path": "tests/test_reports.py", "resolution": "test_input_change", "check_id": "single-section-expense-subtotal",      "claim_ids": ["CL-BFS-001", "CL-BFS-003", "CL-BFS-005"]}
```

Both checks sharing the file are reported independently (the first
corrective pass's own defect-A fix, unaffected by this round). This
`claim_ids` list is purely observational (`detect-changes` never
mutates anything) and deliberately still lists every Claim the shared
Evidence bridges to, including `CL-BFS-003`/`CL-BFS-005` — the new
Claim-scope gate added this round applies at `verify-changes`/`apply`
time, not to this purely informational detection output.

**Steps 4-6 — `verify-changes` applies the new scope gate.**

```
codecompass knowledge verify-changes balance-from-spec --repo-root <ledgerkit>
```

```
affected, not auto-reconciled: CL-BFS-005 (check 'multi-section-income-expense-subtotal', aggregate) -- CL-BFS-005.depends_on names other Claim(s) (CL-BFS-001, CL-BFS-002) -- its own truth is established by combining them, not by a single check's result alone
affected, not auto-reconciled: CL-BFS-005 (check 'single-section-expense-subtotal', aggregate) -- CL-BFS-005.depends_on names other Claim(s) (CL-BFS-001, CL-BFS-002) -- its own truth is established by combining them, not by a single check's result alone
manifest written: .../20261118T134125Z-source.toml (2 contributing finding(s))
```

The written manifest's `[[items]]` contain exactly `CL-BFS-001` and
`CL-BFS-002` — the two genuinely single-check-scoped Claims (step 4).
`CL-BFS-005` is recorded, for **both** checks, in a separate,
non-actionable `[[affected_claims]]` array — visible, never silently
discarded, but never turned into an applyable item (step 6).
`CL-BFS-003` (superseded) never appears anywhere in the manifest at
all — not in `items`, not in `affected_claims` (step 5): this
project's own existing convention already treats a superseded record
as dead, so there is nothing actionable to surface for it.

**Step 7 — accept and apply the check-specific items.** Both items'
`decision` set to `"accept"`:

```
codecompass knowledge apply <manifest>
```

```
applied: recomputed evidence_support_state='supported'; evidence: EV-BALANCEFROMS-004
applied: recomputed evidence_support_state='supported'; evidence: EV-BALANCEFROMS-005
```

**Step 8 — `CL-BFS-005` stays `partially_supported`.** Confirmed
directly: `grep evidence_support_state CL-BFS-005.yaml` →
`partially_supported`, unchanged from before `apply` — the contract's
third required check remains genuinely uncovered, exactly as the real
knowledge base's own narrative states, and this corrective pass never
silently advances it.

**Step 9 — no unrelated Claim/Evidence citation changes.** `md5sum`
before vs. after `apply` for `CL-BFS-003.yaml`, `CL-BFS-004.yaml`,
`CL-BFS-005.yaml`, `EV-BFS-001.yaml`, `EV-BFS-002.yaml`,
`EV-BFS-003.yaml`, `REQ-BFS-001.yaml`, `REQ-BFS-002.yaml`,
`DEC-BFS-001.yaml`, `DEC-BFS-002.yaml`, `OBS-BFS-001.yaml`: every one
byte-for-byte identical. Only `CL-BFS-001.yaml`/`CL-BFS-002.yaml`
changed (new citation + recomputed state), plus two new Evidence files
(`EV-BALANCEFROMS-004`/`005`).

A further, non-mandated but directly relevant observation: because
*both* checks sharing `tests/test_reports.py` were successfully,
validly accounted for this round (the first corrective pass's own
`baseline_eligible_test_input_paths` mechanism, unaffected by the new
Claim-scope gate — it tracks *checks*, never Claims), the shared
file's baseline correctly advanced to the post-edit hash once both
items were applied. Excluding the aggregate Claim `CL-BFS-005` from
mutation did not, and must not, block this legitimate check-level
baseline advancement.

## Step 10 — detector (b) for `CL-BFS-004` remains functional

Added the real, pinned `overlapping-account-patterns-no-double-count`
test (`test_section_accounts_overlapping_patterns_no_double_count`, per
`REQ-BFS-002`'s own example — the £150.00 `expenses:food:groceries`
posting under `accounts=("food", "groceries")`, asserting the section's
own subtotal is `159.00` — groceries counted once, plus the coffee
posting also matched by the `"food"` pattern, never groceries counted
twice) to the scratch Ledgerkit. Confirmed it passes directly under
`pytest` before using it in any CodeCompass command. Re-synced the
graph.

```
codecompass knowledge detect-changes balance-from-spec --repo-root <ledgerkit> --probe-coverage --json
```

```json
"newly_coverable": [{"check_id": "overlapping-account-patterns-no-double-count", "claim_id": "CL-BFS-004"}]
```

```
codecompass knowledge verify-changes balance-from-spec --repo-root <ledgerkit>
```

produced a one-item manifest for `CL-BFS-004` (the two now-`supported`
test-input-change checks are correctly re-proposed as no-ops and
produce nothing; `CL-BFS-005` is reported affected again, unchanged
behaviour). Accepted and applied:

```
applied: recomputed evidence_support_state='supported'; evidence: EV-BALANCEFROMS-006
```

`CL-BFS-004.evidence_support_state` → `supported`, a new citation
(`EV-BALANCEFROMS-006`) alongside the pre-existing source Evidence —
detector (b)'s own reconciliation pathway is completely unaffected by
this corrective pass's Claim-scope gate (its own target Claim,
`CL-BFS-004`, has no `depends_on` and bridges to exactly one check, so
it is `"eligible"` by construction).

## Confirmation

`~/projects/ledgerkit` confirmed clean and at
`a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` both before and after this
demonstration. The real `codecompass` repository's own `planning/
knowledge/balance-from-spec/` and `planning/contracts/balance-from-spec/`
directories were never written to — `git status --porcelain` against
both paths returns nothing throughout. Every write happened against the
disposable scratch copies named above.
