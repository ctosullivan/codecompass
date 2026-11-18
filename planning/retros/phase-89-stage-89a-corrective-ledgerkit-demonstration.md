# Phase 89 Stage 89A corrective pass — real Ledgerkit demonstration log

2026-11-18. All commands below were run against disposable scratch
copies under `/tmp/phase89a-corrective-demo/` (`cp -r ~/projects/
ledgerkit <scratch>`, never a git clone, never the real checkout), each
paired with a disposable scratch copy of the real `planning/knowledge/
balance-from-spec/` + `planning/contracts/balance-from-spec/`
directories (never the real `codecompass` knowledge base). `~/projects/
ledgerkit`'s own `git status --short`/`git log --oneline -1` were
confirmed clean, at `a7740fd`, both before this session's work began and
again after every demonstration below completed.

Graph re-sync for an edited `.py` file was performed directly against
each scratch checkout's own copied `context-graph.db` (a raw `UPDATE
source_files SET content_hash = ? WHERE path = ?`, functionally
identical to what a full `codecompass sync` would record for that one
file, without invoking the full indexing/enrichment pipeline this
demonstration does not exercise).

All commands used the real CLI (`/home/cormac/projects/codecompass/
.venv/bin/codecompass knowledge ...`), confirmed via `codecompass.
__file__` to resolve to the live, editable `src/codecompass/` tree
carrying this corrective pass's own changes.

## 1–3. Shared test-input change affecting multiple existing checks

Scratch: `kr-shared` + `ledgerkit` (shared copy, test-input edit applied
and kept for the remaining scenarios below).

Both `single-section-expense-subtotal` and `multi-section-income-
expense-subtotal` already have real citing Evidence in the production
knowledge base (`EV-BFS-002`, `EV-BFS-003`) and both already list
`tests/test_reports.py` + `tests/fixtures/filtered.journal` as
`test_input_paths` in the real `oracle-contract.yaml` — the exact
shared-file shape the dispatch names. Both production Claims
(`CL-BFS-001`, `CL-BFS-002`) are already `evidence_support_state:
supported` in the real knowledge base, which would make a fresh
re-confirmation a deliberate, documented no-op (§4.3) — masking the
dual-attribution behaviour this demonstration is specifically about. In
this scratch copy only, both Claims' `evidence_support_state`/`status`
were set to `partially_supported`/`proposed` before the demonstration,
so a fresh PASS genuinely produces a manifest-worthy finding for each.

Established baselines (`--establish-baselines`), confirming the
non-Python fixture `tests/fixtures/filtered.journal` gets a real
baseline entry too (bounded check 1, see §7 below for its own dedicated
demonstration).

Added a real, assertion-preserving comment to `tests/test_reports.py`
(inside `test_single_section_rows_and_subtotal`), re-synced the graph,
and ran:

```
codecompass knowledge detect-changes balance-from-spec --repo-root <ledgerkit> --json
```

Result — **both** checks sharing the file are reported as independent
findings, each correctly bridged to its own Claim:

```
{"path": "tests/test_reports.py", "resolution": "test_input_change", "check_id": "multi-section-income-expense-subtotal", "claim_ids": ["CL-BFS-002", "CL-BFS-003", "CL-BFS-005"]}
{"path": "tests/test_reports.py", "resolution": "test_input_change", "check_id": "single-section-expense-subtotal",      "claim_ids": ["CL-BFS-001", "CL-BFS-003", "CL-BFS-005"]}
```

The pre-corrective-pass code (`_tracked_test_input_paths` returning a
single-valued `{path: check_id}` dict) would have silently reported
only ONE of these two — whichever check `contract.checks` iterates to
last (`multi-section-income-expense-subtotal`), permanently hiding
`single-section-expense-subtotal`'s own drift. This is the defect-A
regression, reproduced live against the real contract.

`verify-changes` executed both checks for real (`pytest`, not a
collection probe) and wrote a 3-item manifest (`CL-BFS-001`, `CL-BFS-002`,
`CL-BFS-005` — the last citing both checks, since it cites both
EV-BFS-002 and EV-BFS-003). `baseline_eligible_test_input_paths`
correctly included `tests/test_reports.py` (both checks' fresh results
were successfully, validly re-verified this run).

Annotated the manifest: `decision: accept` for `CL-BFS-001` only,
`decision: reject` for `CL-BFS-002` and `CL-BFS-005`. Ran:

```
codecompass knowledge apply <manifest>
```

Result: `CL-BFS-001`'s item applied (new Evidence `EV-BALANCEFROMS-004`,
`evidence_support_state` → `supported`); the other two skipped
(`rejected at review`). `source-baseline.toml`'s own entry for
`tests/test_reports.py` was confirmed **unchanged** — still the
*pre-edit* hash, not the new one — even though one sibling check was
fully, successfully reconciled. This is the shared-baseline-eligibility
fix: a shared file's baseline never advances merely because one of
several affected checks was reconciled.

Re-ran `verify-changes` (re-proposing the two rejected checks, since
`CL-BFS-001`'s own check is now a no-op — already `supported`),
accepted both resulting items, applied them. Only then did `source-
baseline.toml`'s entry for `tests/test_reports.py` advance to the new,
post-edit hash — confirming the baseline is free to advance once every
check sharing the file has genuinely, successfully reconciled, however
many separate manifests/apply calls that takes.

## 4. A genuinely tampered `OracleResult` rejected during `apply`

Scratch: `kr-tamper` (fresh knowledge-root, same edited `ledgerkit`).
Added the real `overlapping-account-patterns-no-double-count` test
(`test_section_accounts_overlapping_patterns_no_double_count`, per
`REQ-BFS-002`'s own pinned example — £150.00 `expenses:food:groceries`
posting, `accounts=("food", "groceries")`, asserting it contributes
exactly once) to the scratch Ledgerkit, confirmed it passes under
`pytest` directly, re-synced the graph. `detect-changes --probe-
coverage` correctly reported it `newly_coverable` → `CL-BFS-004`.
`verify-changes` executed it for real and produced a manifest item for
`CL-BFS-004`. Annotated `decision: accept`, then appended a line to the
cited run's own `raw_output_ref` `.txt` file (`echo "TAMPERED BY DEMO"
>> <raw file>`) — tampering it *after* persistence, *before* `apply`.

```
codecompass knowledge apply <manifest>
```

Result:

```
skipped: cited result for check 'overlapping-account-patterns-no-double-count'
failed re-validation: raw_output_ref '...' content does not match its
own recorded raw_output_sha256 -- tampered or corrupted
```

`CL-BFS-004`'s `evidence_support_state` stayed `partially_supported`
(untouched); no new Evidence record was created. This is defect B's
fix — `evaluate_result_precedence`'s own raw-output-hash check,
genuinely reused at the apply-time canonical write boundary, reproduced
live via the real `apply` command (not a unit-level helper call).

## 5. Interrupted post-Claim-write reconciliation recovering correctly

Scratch: `kr-retry`. Verified and applied the same real newly-coverable
finding (`CL-BFS-004`) once, normally — `evidence_support_state` →
`supported`, one new Evidence record (`EV-BALANCEFROMS-004`). Then, in
the manifest file, set that item's own `state` back to `"pending"` —
exactly the on-disk state a crash *after* the Claim write succeeded but
*before* the caller durably recorded `state="applied"` would leave.

```
codecompass knowledge apply <manifest>
```

Result: `applied: already applied -- recovered from an interrupted
retry (Evidence and Claim already reflect this exact approved item)`.
No duplicate Evidence record, Claim's `supporting_evidence`/
`evidence_support_state` unchanged from the first apply. This is
defect C's fix, reproduced live via the real `apply` command.

## 6. A real human Claim edit still refused as a concurrent conflict

Scratch: `kr-concurrent` (fresh). Verified the same finding, accepted
the item, then — **before ever applying it** — hand-edited `CL-BFS-
004.yaml` directly on disk (appended a comment line, changing its own
content hash) to simulate a human reviewing/annotating the Claim
concurrently with the review step. Ran `apply`:

```
skipped: apply-time race: the Claim changed since detection
(base_claim_hash no longer matches) -- refusing to write; re-run
`knowledge detect-changes`/`verify-changes` and review again
```

No Evidence created. This confirms the idempotent-recovery pre-check
(§5 above) is correctly scoped: it only ever short-circuits once this
*exact* item's own Evidence already exists and is already cited
correctly in the live Claim — a pre-first-apply concurrent edit (no
Evidence yet) always falls through to the ordinary race check and is
refused, exactly as before this corrective pass. (A related, explicitly
non-destructive boundary case was also observed and is worth recording
for a future reader: hand-editing an *unrelated* field on a Claim
*after* its own item has already been fully, successfully applied does
not block a subsequent idempotent retry of that same already-complete
item — correct, since that retry would write nothing and so cannot
discard the concurrent edit either; it is a different scenario from
this one, not a weaker version of it.)

## 7. A changed non-Python oracle input detected

Scratch: `kr-fixture` (fresh knowledge-root, established baselines
against the clean, unedited `ledgerkit` first). Appended a new,
legitimate transaction to `tests/fixtures/filtered.journal` only —
`tests/test_reports.py` untouched. `tests/fixtures/filtered.journal` has
no Python source and so no `source_files` row in `context-graph.db` at
all.

```
codecompass knowledge detect-changes balance-from-spec --repo-root <ledgerkit> --json
```

Result: the fixture change is reported as a `test_input_change` finding
for both sharing checks — **not** `stale_graph_index`. This is bounded
check 1's fix, reproduced against the real fixture file.

## 8. Original detector A and detector B demonstrations continue to work

**Detector A** (scratch `kr-detA` + fresh `ledgerkit-detA`): established
baselines on the *clean* checkout first, then removed `reports.py`'s
own `if section.invert:` sign-inversion guard — the same mutation the
original Stage 89A demonstration used. Confirmed `pytest` genuinely
fails (`test_multi_section_correct_values`: `Decimal('-6000.00') !=
Decimal('6000.00')`). `detect-changes` → `symbol_change`; `verify-
changes` → one finding, `label="regression"`, `target_field=
"contradicting_evidence"`; accepted and applied →
`evidence_support_state` → `conflicting`. Reversed the mutation
(`git checkout -- ledgerkit/reports.py` in the *scratch* copy only),
re-synced, re-ran `detect-changes`/`verify-changes` → `label=
"re_confirmed"`, `target_field="supporting_evidence"`; accepted and
applied. `evidence_support_state` correctly stayed `conflicting` (not
silently reset to `supported`) — the historical `contradicting_
evidence` entry from the regression is never dropped, matching this
project's own existing, documented cumulative-state design
(`decisions/0096`) — unchanged by this corrective pass. The full
mutation → FAIL → reconciliation → reversal → PASS → reconciliation
cycle behaves identically to the original Stage 89A audit's own
reproduction.

**Detector B**: re-exercised directly as part of §4 and §5 above
(the real `overlapping-account-patterns-no-double-count` check,
`CL-BFS-004`) rather than as a separate, redundant fresh run — both
confirm the newly-coverable pathway (a required check with zero citing
Evidence, upgraded via a real, independently executed `pytest` run)
continues to work exactly as the original Stage 89A demonstration
established.

## Confirmation

`~/projects/ledgerkit`: `git status --short` empty, `git log --oneline
-1` → `a7740fd` (unchanged) — confirmed again after every scenario
above. No command in this log was ever run with `--repo-root` pointing
at that path.
