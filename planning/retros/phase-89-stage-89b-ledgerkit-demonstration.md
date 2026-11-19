# Phase 89 Stage 89B — real Ledgerkit documentation-cascade demonstration log

2026-11-19. All commands below ran against disposable scratch copies
under `/tmp/.../phase89b-demo/` — a disposable `cp -r ~/projects/
ledgerkit <scratch>/ledgerkit` (never a git clone, never the real
checkout) paired with a disposable scratch "project root"
(`<scratch>/project/`) containing its own copies of `planning/
knowledge/balance-from-spec/` and `planning/contracts/balance-from-spec/`
(never the real codecompass knowledge base) plus one new, disposable
schema-governed document (`docs/demo/balance-from-spec-notes.md` +
`.schema.yaml`). The real `~/projects/ledgerkit` checkout's own `git
status --porcelain`/`git rev-parse HEAD` (`a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`)
were confirmed clean and unchanged both before and after this
demonstration. The real codecompass repository's own `planning/
knowledge/balance-from-spec/` and `planning/contracts/balance-from-spec/`
were confirmed untouched throughout (`git status --porcelain` against
both paths returns nothing).

Graph re-sync used the same lighter-weight, established technique as
the Stage 89A demonstrations (a direct `sqlite3`/`python3 -c` `UPDATE
source_files SET content_hash = ?`), never the full indexing/enrichment
pipeline this demonstration does not exercise.

All CLI commands used the real `codecompass` binary
(`/home/cormac/projects/codecompass/.venv/bin/codecompass`), run from
the disposable project root against the disposable Ledgerkit checkout
via `--repo-root`. `docs compile` genuinely invoked the real AI
composer (`cleanroom_broker.run_inference`) for every draft shown
below — no mocked or hand-written composer output anywhere in this log
except where explicitly marked "lead draft-patch" (see "Review
iteration" below).

## Setup: a disposable schema-governed document

`docs/demo/balance-from-spec-notes.md.schema.yaml` (schema_version 1,
three sections, each `required_knowledge` naming exactly one real
Claim): `overlapping-patterns` → `CL-BFS-004`, `single-section-subtotal`
→ `CL-BFS-001`, `multi-section-sign-inversion` → `CL-BFS-002` (the third
section was added mid-demonstration, once detector (a)'s own real
regression scenario was being set up, so it could cite a Claim the
mutation would actually affect — `CL-BFS-001`'s own check is unaffected
by the sign-inversion mutation, confirmed by direct test execution
before relying on it, see "Detector (a)" below).

No real grounded documentation region citing any `CL-BFS-*` Claim
exists anywhere in the real repository today (confirmed: `grep -rl
"grounded-by"` across every tracked doc, cross-checked against
`CL-BFS` — no hits) — the plan's own disclosed fallback (§6.2/dispatch
§5) for exactly this case. This disposable document was never inserted
into the real `docs/`/`architecture/` tree.

## Review iteration (semantic-support + editorial-quality)

Every section went through the real, two-independent-dispatch review
gate (`general-purpose` agents, matching Phase 87C's own established
precedent of using that agent type for both review dimensions) before
any publish. Several genuinely FAILed on the first attempt and needed
real iteration — reported honestly below, not smoothed into a clean
first-pass narrative:

- **`overlapping-patterns` (CL-BFS-004, `partially_supported` at the
  time)** took **4 rounds** to reach a double-PASS: round 1 overclaimed
  the behaviour as a tested guarantee with no hedge (semantic
  UNSUPPORTED) and used defensive, repetitive phrasing (editorial
  FAIL); round 2's lead-patched hedge sentence was semantically correct
  but editorially read as meta-commentary/disclaimer (editorial FAIL),
  and separately (due to an abbreviated record excerpt in that round's
  own review prompt, a methodological artifact on this demonstration's
  part, not a defect in the draft) a spurious semantic UNSUPPORTED on
  unrelated mechanism detail that round 3's full-record re-review
  confirmed was actually fine; round 3's mid-sentence hedge still read
  as self-referential epistemic-provenance framing (editorial FAIL);
  round 4 rephrased the same fact as direct reader-facing advice ("this
  path has no dedicated test yet, so verify independently if your
  workflow depends on...") and passed both dimensions. Every
  intermediate draft was a real **lead draft-patch** (hand-editing the
  pending review JSON's `tagged_draft`/recomputing `draft_sha256` via
  the real `doc_compiler.strip_citation_tags`/`oracle.sha256_text`
  functions, the same "draft patching" pattern Phase 87C's own retro
  already named as an established lead-orchestration activity) between
  AI-composed attempts, not a repeated raw re-compile — `docs compile`
  itself was run twice for this section (round 1, and later again after
  Task A's own evidence change, see below); rounds 2-4 were lead
  patches of the same underlying draft.
- **`single-section-subtotal` (CL-BFS-001, `supported`)** took 2
  rounds: round 1 had a stray `##` heading (violating the composer's
  own "no headings" instruction) and test-provenance meta-commentary
  (editorial FAIL on both counts, though semantically SUPPORTED);
  round 2 (lead draft-patch: heading removed, provenance sentence
  replaced with a single plain behavioural sentence) passed both
  dimensions.
- **`multi-section-sign-inversion` (CL-BFS-002, `supported`)** took 3
  rounds: round 1 had a stray heading (fixed by the lead before first
  review) plus added, unevidenced mechanism detail ("inverted via sign
  flipping", "merged into a single consistent total" — semantic
  UNSUPPORTED, editorial PASS); round 2 (lead draft-patch, mechanism
  detail removed) was semantically SUPPORTED but its added test-
  provenance sentence read as meta-commentary for this audience
  (editorial FAIL); round 3 (lead draft-patch, provenance sentence cut
  entirely, one plain behavioural sentence) passed both dimensions.

**This iteration is itself a real, disclosed Stage 89B finding, not
incidental noise**: the composer's own system prompt does not yet
reliably hedge a `partially_supported` Claim's own test-coverage status
in a register independent reviewers accept as "reader-facing advice"
rather than "meta-commentary" on the first or even second attempt, and
separately tends to add plausible-sounding mechanism detail beyond an
oracle-run record's own stated scope. Both are genuine, reproducible
gaps in the *existing* Phase 87 composer prompt (`scripts/
compile_doc_section.py::build_system_prompt`), discovered by actually
running the real pipeline against real evidence rather than a synthetic
fixture built to pass on the first try. Fixing the shared composer
prompt itself is explicitly out of Stage 89B's own scope (not a named
deliverable, and would be an uncontrolled change to Phase 87's own
already-reviewed mechanism); recorded here, and as a candidate learning
(see `planning/learnings/inbox.md`), for a future session to pick up.

All three sections' initial baselines were established and published
through the real CLI (`docs record-review` ×2 per final round, `docs
publish`, `docs maintain` confirming `established_new`/`noop` as
appropriate) before any Task A change ran.

## Detector (b) — CL-BFS-004, the real Task A scenario

1. Added the real, pinned `overlapping-account-patterns-no-double-count`
   test (`test_section_accounts_overlapping_patterns_no_double_count` —
   `accounts=("food", "groceries")` against the real fixture's
   `expenses:food:groceries` (150.00) and `expenses:food:coffee` (9.00)
   postings, asserting `subtotal == Decimal("159.00")`) to the scratch
   Ledgerkit. Confirmed it passes directly under the scratch checkout's
   own `.venv/bin/pytest` before using it in any CodeCompass command.
2. `codecompass knowledge detect-changes balance-from-spec --repo-root
   <ledgerkit> --probe-coverage --json` → `"newly_coverable":
   [{"check_id": "overlapping-account-patterns-no-double-count",
   "claim_id": "CL-BFS-004"}]`.
3. `codecompass knowledge verify-changes balance-from-spec --repo-root
   <ledgerkit>` → one-item manifest, `record_id = "CL-BFS-004"`,
   `contributing_labels = ["newly_covered"]`, `contributing_target_fields
   = ["supporting_evidence"]`, citing a real, freshly-executed, PASS
   `OracleResult` with its own `run_id`.
4. `find_gaps` (sanity check of the new gap kind against this *positive*
   scenario) correctly reports **zero** `claim_contradicted_by_fresh_
   check` gaps — a `PASS` is never surfaced as a pending contradiction.
5. Accepted (`decision = "accept"`) and applied (`codecompass knowledge
   apply`) → `CL-BFS-004.evidence_support_state` → `supported`, new
   citation `EV-BALANCEFROMS-004` (`evidence_kind: test`).
6. `codecompass docs maintain docs/demo/balance-from-spec-notes.md.schema.yaml`
   → `claims_changed: ['id:balance-from-spec-notes-md-overlapping-patterns']`,
   **`single-section-subtotal` and (at that point, before section 3
   existed) nothing else reported — the unrelated region was correctly
   left `noop`.**
7. Recompiled (`docs compile`, a real second AI-composer call, now
   given `CL-BFS-004`'s updated fields), reviewed (2 independent
   dispatches, SUPPORTED/PASS — the Claim's own authored `statement`
   text is itself stale, "not yet tested", by this mechanism's own
   explicit, disclosed design (it never rewrites authored prose, only
   citations and `evidence_support_state`); both reviewers were briefed
   on this explicitly and correctly treated the machine-derived fields,
   not the stale prose, as authoritative), and published.
8. **Published result**:
   > When `balance_from_spec` evaluates a posting against a section's
   > account patterns, it treats the pattern list as a single OR gate:
   > if any pattern in `section.accounts` matches the posting's
   > account, the posting is appended once and checked no further
   > against the remaining patterns. The implementation does not loop
   > over each matching pattern to count or append the posting multiple
   > times — a posting is included at most once per section regardless
   > of how many of its patterns match.

   This accurately reflects the Claim's now-`supported` state (no
   hedge needed — it's genuinely test-confirmed now) and correctly
   describes only the mechanism CL-BFS-004 itself states.

## Detector (a) — CL-BFS-002, the real regression scenario

1. Confirmed baselines were established (`--establish-baselines`) at
   the *original*, unmutated `ledgerkit/reports.py` state first — a
   baseline established after mutating would incorrectly treat the
   mutated state as the reference point.
2. Applied the real sign-inversion mutation (`reports.py`'s own
   `if section.invert: rows = {k: -v for k, v in rows.items()}` block
   replaced with a no-op). Confirmed directly via the scratch
   checkout's own `pytest`: `test_multi_section_correct_values` (the
   `multi-section-income-expense-subtotal` check's own body) genuinely
   **FAILs** (`Decimal('-6000.00') != Decimal('6000.00')`);
   `test_single_section_rows_and_subtotal` (the `single-section-
   expense-subtotal` check's own body, no `invert` section at all)
   is **unaffected** — confirming this mutation is correctly scoped to
   only one of the two existing required checks, which is why a third
   schema section (`multi-section-sign-inversion` → `CL-BFS-002`,
   the Claim this check's own Evidence bridges to) was added rather
   than reusing `single-section-subtotal`.
3. Re-synced the graph. `detect-changes --json` → `"changed": [{"path":
   "ledgerkit/reports.py", "resolution": "symbol_change", ...}]`.
4. `verify-changes` → one-item manifest, `record_id = "CL-BFS-002"`,
   `contributing_labels = ["regression"]` (a historical `PASS` existed
   for this exact check before this fresh, genuine `FAIL` —
   `CL-BFS-002` was already `evidence_support_state: supported`),
   `contributing_target_fields = ["contradicting_evidence"]`, citing a
   real, freshly-executed, FAIL `OracleResult`.
5. **`find_gaps` (the new `claim_contradicted_by_fresh_check` gap
   kind, exercised live, before any human review)**:
   ```json
   {
     "kind": "claim_contradicted_by_fresh_check",
     "subject_id": "CL-BFS-002",
     "scope": "multi-section-income-expense-subtotal",
     "reason": "CL-BFS-002 has a pending, unapplied source_reconciliation
       manifest item (...) proposing contradicting Evidence from check
       'multi-section-income-expense-subtotal' (...) that has not yet
       been reviewed",
     "label": "regression"
   }
   ```
   Correctly labelled `"regression"` (a real historical `PASS` existed).
   The pending manifest/Claim files were confirmed byte-identical before
   and after this `find_gaps` call (`md5sum`) — purely read-only, no
   canonical mutation from detection alone.
6. Accepted and applied → `CL-BFS-002.evidence_support_state`:
   `supported` → **`conflicting`** (both the original supporting
   Evidence, `EV-BFS-001`/`EV-BFS-003`, and the new contradicting
   Evidence, `EV-BALANCEFROMS-005`, now cited — the historical support
   is never silently erased). `find_gaps` re-run immediately after:
   **zero** `claim_contradicted_by_fresh_check` gaps remain for this
   Claim — a reviewed, applied item is never reported as still pending.
7. `docs maintain` → `claims_changed:
   ['id:balance-from-spec-notes-md-multi-section-sign-inversion']`;
   **both other regions correctly `noop`.**
8. **A genuine, valuable negative finding**: attempting `docs compile`
   on this section at this point returns `gap_blocked` —
   `find_section_gaps` (pre-existing Phase 87 machinery, unmodified)
   correctly refuses to auto-generate prose for a Claim with live
   `contradicting_evidence`, via its own existing `contradiction` gap
   check (not the new Stage 89B gap kind — that one only ever reports a
   *pending, unapplied* finding; this Claim's contradiction is already
   applied and canonical). This is the documentation pipeline correctly
   declining to regenerate automated prose for a genuinely contested
   Claim rather than silently asserting a settled fact either way — an
   explicit human editorial decision is required, exactly as intended.
9. **Human editorial resolution, exercised for real**: hand-edited the
   published region's own prose directly in `docs/demo/balance-from-
   spec-notes.md` to honestly state the conflict (the original passing
   evidence, the new regression, and that the original evidence is
   preserved, not discarded). Re-ran `docs maintain` →
   **`concurrent_conflicts: ['id:balance-from-spec-notes-md-multi-
   section-sign-inversion']`** — both the region's own prose (hand-
   edited) and its cited Claim's own content (the regression) changed
   since the last baseline, in the same window, so `detect_grounded_
   region_changes`'s own pre-existing, unmodified concurrency model
   correctly classifies this as `concurrent_conflict`, not a plain
   `doc_candidate` — reported for lead resolution only, never
   auto-resolved either way (confirmed directly against `doc_compiler.
   decide_publish_safety`'s own documented behaviour for this case).
   Left in this state deliberately, as the honest, demonstrated outcome
   of a genuinely concurrent real-world edit — not forced to a clean
   publish, since doing so would exercise a different (and, for this
   demonstration, unnecessary) resolution path than the one a real
   editorial conflict naturally produces.

## Negative controls confirmed live, incidentally and directly

- **Unrelated-region protection**: across every `docs maintain` call in
  this log, a region not citing the just-changed Claim was reported
  `noop`, never `claims_changed`/`doc_candidate` — confirmed on both
  cascades (detector (b)'s change left `single-section-subtotal`
  `noop`; detector (a)'s change left `overlapping-patterns` and
  `single-section-subtotal` both `noop`).
- **Pending contradiction is read-only**: `find_gaps`'s new gap kind
  never mutated the manifest or the Claim (confirmed by hash, step 5
  above, and separately by the dedicated unit-test suite, see
  `tests/test_knowledge_api.py::TestClaimContradictedByFreshCheckGap::
  test_scan_is_read_only`).
- **Historical contradiction never silently disappears**: `CL-BFS-002`'s
  own `evidence_support_state` is `conflicting`, not reverted to
  `supported`, after the regression was accepted — the published
  (hand-edited) prose states this explicitly rather than claiming the
  scope is still simply "correct."
- **Human editorial protection**: the `concurrent_conflict` outcome
  above is itself a live demonstration of this guarantee — a region a
  human has just edited is never silently overwritten by a competing,
  automatically-detected change.
- **Aggregate-Claim scope protection carries through unmodified**: not
  separately re-demonstrated in this log (already covered exhaustively
  by the Stage 89A second-corrective-pass demonstration and by this
  round's own `pending_contradicting_findings` unit tests, which
  include a dedicated aggregate-Claim-is-never-reported-here case) —
  cited rather than repeated, per this project's own "don't duplicate
  a demonstration the unit suite already exercises with full fidelity"
  convention (Stage 89A's own retro states the same principle).

## Confirmation

`~/projects/ledgerkit` confirmed clean and at
`a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` both before and after this
demonstration. The real `codecompass` repository's own `planning/
knowledge/balance-from-spec/` and `planning/contracts/balance-from-spec/`
directories were never written to — `git status --porcelain` against
both paths returns nothing throughout. Every write happened against the
disposable scratch copies named above.
