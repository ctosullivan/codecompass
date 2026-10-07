# Phase 81 second corrective pass — independent completion audit

**This file has been overwritten with a fresh, independent re-audit.**
The prior audit below this notice (audited HEAD `a9bcd02`) returned
**FAIL** on four verification/closeout-documentation integrity gaps. This
re-audit (audited HEAD `a420541`) independently re-derived whether each
of the four claimed fixes actually closes the gap found, and verdicts
**PASS**. The full prior FAIL report is preserved verbatim below the
line, per this project's own practice of not silently erasing audit
history.

---

## Re-audit (this pass)

- **Auditor:** `release-phase-auditor` (fresh, independent dispatch,
  distinct from the instance that returned the prior FAIL)
- **Audited HEAD:** `a420541` (`main`)
- **Scope:** `git log a9bcd02..a420541 --stat` — one commit, touching
  exactly `planning/CONTEXT.md`, `planning/retros/_audit-phase-81-second-corrective-pass.md`
  (the prior FAIL report itself, read as evidence not re-verified as a
  claim), `planning/retros/_drift-audit-phase-81-second-corrective-pass.md`,
  `planning/retros/phase-81-second-corrective-pass.md`, and
  `tests/test_knowledge_intermediate.py`. No `src/` file touched — the
  prior audit was explicit that production code needed no further
  change, and this commit honors that.

### Verdict: **PASS**

Every one of the four findings from the prior FAIL (Findings A, B, C, D)
was independently re-derived to be genuinely closed — not merely
re-asserted by this commit's own message. No new gap was found. The DoD
checklist as a whole is intact.

---

### Finding A (overstated test coverage) — independently confirmed fixed

Read the actual new/changed test code in
`tests/test_knowledge_intermediate.py` directly (not the commit message
or retro prose):

1. **`test_declared_intent_via_explicit_type_becomes_proposed_policy`**
   (line 1027) now reads the real produced record's `statement` field and
   asserts both `"Type: Intent" not in statement` and
   `statement.strip() == "The system should do X."` (lines 1046-1049) —
   genuinely exercises the header-stripping fix; the test would now fail
   if `item.get("intent_statement")` were not used. Cross-checked against
   the real code path it exercises
   (`_apply_candidate_addition`, `knowledge_intermediate.py:1981-1985`):
   `claim_statement = (item.get("intent_statement") or "").strip() or
   text` — the already-stripped body captured at detection, matching the
   test's own expectation exactly.

2. **`TestCandidateDisappearanceFailsClosed`** (line 1444) has two tests,
   genuinely covering both sides of the same branch, not a restatement:
   - `test_disappeared_candidate_with_no_match_fails_closed` (1448):
     detects a real candidate, writes a manifest, then deletes the
     candidate text from the live file with **no** matching canonical
     record created anywhere. Asserts `result.applied == []`,
     `"race" in result.skipped[0].reason`, and — critically, the *depth*
     check the prior audit's own governing rules (`L-075`) require — that
     `records_after == records_before`, i.e. genuinely zero records
     created, not merely a non-crash. Cross-checked against
     `_apply_candidate_addition` (`knowledge_intermediate.py:1989-2012`):
     the `not text_present` branch with no `existing` match returns
     `ApplyOutcome(False, item, "apply-time race: ...")` — exact string
     match for the `"race"` substring the test checks, and no write call
     precedes that return.
   - `test_disappeared_candidate_already_promoted_is_a_safe_noop` (1479):
     the genuine other half of the same branch — text is also gone from
     the live file, but this time a real matching `CL-DEMO-099.yaml`
     record exists. Asserts `result.applied[0].new_record_id ==
     "CL-DEMO-099"`, confirming the branch still succeeds when a true
     match exists rather than the fix over-correcting into always
     failing. This is a distinct scenario from the first test (different
     setup, different assertion, opposite outcome), not a restatement.

3. **`TestCrossKindDeduplicationIndependence`** (line 1520) has two
   tests, each genuinely creating a pre-existing record of one kind and a
   new candidate of the other kind with byte-identical statement text:
   - `test_preexisting_claim_does_not_block_new_requirement` (1524):
     writes a real `CL-PRE-001.yaml` Claim, then a candidate block with
     `Type: Requirement` / `Decision: DEC-DEMO-001` / `Statement:
     <same_text>` (identical to the pre-existing Claim's statement).
     Asserts the applied result's new id `startswith("REQ-")` and its
     statement equals `same_text` — a pre-existing Claim did not block
     creation of the Requirement.
   - `test_preexisting_requirement_does_not_satisfy_claim_dedup` (1557):
     the reverse — writes a real `REQ-PRE-001.yaml` Requirement, then an
     ordinary (not `Type:`-tagged) candidate with the identical text.
     Asserts the applied result's new id `startswith("CL-")` and its
     statement equals `same_text` — a pre-existing Requirement did not
     get mistaken for (or satisfy dedup against) the new Claim.
   Both assert the correct record **kind** (via id prefix) and the
   **statement content**, matching this audit brief's own bar. Cross-
   checked against `_find_existing_promoted_record`
   (`knowledge_intermediate.py:1746-1788`, `if record.kind != kind:
   continue`) and its call sites (`kind="claim"` vs `kind="requirement"`)
   — the tests exercise exactly the call-site-correctness the prior audit
   confirmed by reading code but found had "zero regression protection."
   That protection now exists.

**My own fresh test runs** (not trusting the commit's reported counts):

- `.venv/bin/python -m pytest tests/test_knowledge_intermediate.py -q` →
  **65 passed** — matches the claimed count exactly.
- `.venv/bin/python -m pytest -q` (full suite) → **845 passed, 2
  skipped** in 211.17s — matches the claimed count exactly, and is
  consistent with the prior audit's own 841-passed baseline plus these 4
  new tests (841 + 4 = 845).

Finding A is genuinely closed.

### Finding B (`planning/CONTEXT.md` stale) — independently confirmed fixed

Read `planning/CONTEXT.md`'s Phase 81 section directly (lines 8-105).
It now narrates, in order: the second reopening and its fourteen
corrections (unchanged from before); "a fresh per-phase docs-drift audit
has since run... NO DRIFT" and "learning/context-gap triage has also
run... three candidates filed and promoted" — both stated as **completed
fact**, not pending; then a new paragraph (lines 81-101) stating **"A
first independent completion audit... returned FAIL"**, naming all four
gaps found, and stating **"All four are now fixed"** with one sentence
per fix (tests added with the new count, this file's own update, the
drift-audit record's existence, the retro's expansion). The final line
(103-105) correctly states the next concrete step is a fresh independent
completion audit, since the prior one is voided by the fix commit. This
is an accurate, current, non-stale account of exactly the state this
audit itself is now verifying — it does not merely claim the fixes
happened, it correctly describes them at the right level of specificity
to be checked against reality (which I did above). Finding B is
genuinely closed.

### Finding C (no persisted drift-audit report) — independently confirmed fixed

Read `planning/retros/_drift-audit-phase-81-second-corrective-pass.md`
directly in full. It is a real, substantive, scoped record — not a
placeholder: names its own scope (commit `7a0e270`, specific doc files,
specific code symbols cross-checked), states a method (read the two docs
in full, cross-check against real code, grep sweep for stale patterns,
check `docs/domain/concepts/*.md` References blocks), and gives a
finding-by-finding account including the one real pre-existing gap it
found and fixed (`ai-docs/README.md`'s stale command list, fixed in
`42f9486`, confirmed via `git blame` to predate this pass).

I independently spot-checked two of its central claims rather than
trusting its own prose:

- `docs/codecompass-knowledge-workflow.md`: confirmed by direct read that
  it documents `region:<id>` syntax with duplicate-id fail-closed
  behaviour, the three real baseline-advancement triggers (first
  sighting / actual apply / explicit acknowledge command), the
  `semantic_change` true/false branching, and both
  `doc-acknowledge-stale`/`doc-acknowledge-chunks` commands — all
  present and worded consistently with the drift audit's own summary.
- `docs/cli-reference.md`: confirmed by direct read (`doc-select-candidates`,
  `doc-acknowledge-stale <doc> <region>`, `doc-acknowledge-chunks`,
  `semantic_change` field documentation) **and** by running the real
  live CLI (`.venv/bin/python -m codecompass.cli knowledge --help`),
  which lists `doc-select-candidates`, `doc-acknowledge-stale`,
  `doc-acknowledge-chunks` as real registered subcommands with
  descriptions matching the doc's own prose. No drift found between the
  live CLI, the doc, and the drift audit's own account of either.

Finding C is genuinely closed: a durable, checkable artifact exists and
its claims hold up under independent spot-check.

### Finding D (retro missing TEMPLATE.md sections) — independently confirmed fixed

Read `planning/retros/phase-81-second-corrective-pass.md` directly
against `planning/retros/TEMPLATE.md`'s own section list. Every required
section is now present with real, phase-specific content, not
boilerplate:

- Header: Date, Commit(s) (lists all five relevant commits plus "the
  post-audit fix commit(s) closing the findings below"), Agents used.
- **Where we are** — orients this phase within Priority D's trajectory,
  names what the first corrective pass established and what this one
  reviewed.
- **Goal**, **Scope delivered vs planned** (explicitly calls out the
  unplanned extra verification step and the unplanned second audit
  round), **What was achieved** (plus a bonus "Real dogfood validation"
  section beyond the template's minimum).
- **What worked** / **What didn't work** — genuinely distinct content,
  not a restatement of each other; "What didn't work" honestly names the
  overstated-coverage gap, the stale `CONTEXT.md`, and the missing
  drift-audit record as real process failures of this very pass, which
  is exactly the honest self-accounting the DoD's retro requirement
  exists for.
- **Lessons learnt** (four distinct, generalizable points, referencing
  `L-086`/`L-087`/`L-088` where relevant), **Process-improvement
  feedback** (two concrete, actionable suggestions, not vibes).
- **Candidate learnings filed** — names `L-086`/`L-087`/`L-088`
  explicitly.
- **Where we're going** — states this closes Phase 81 as a whole once
  the fresh audit passes, and that no stage gate is affected.
- **Time / cost note** — names three same-day sessions and the
  two-audit-round-trip cost explicitly.

This phase is substantive (fourteen defects, a new ADR, a public-repo
push, plus this audit-fix cycle itself) and the full template is applied
in full. Finding D is genuinely closed.

---

### Re-confirmed broader DoD checklist (not re-litigating the ten
code-behaviour checks the prior audit already ran to completion — spot
checks only, per the task brief)

| Condition | Result |
|---|---|
| `.venv/bin/ruff check src/ tests/ scripts/` | **PASS** — "All checks passed!" |
| `.venv/bin/python scripts/check_knowledge_base.py --strict` | **PASS** — exit 0; one `info`-level finding on `first-party-source-symbols` (`CL-FPSS-007` status drift, `verified` vs `supported`), unrelated to Phase 81, pre-existing, honestly labelled "expected and healthy" by the tool itself — matches the task brief's own expectation exactly. |
| `.venv/bin/python scripts/check_user_docs.py --strict` | **PASS** — "no findings", exit 0. |
| Full test suite | **PASS** — 845 passed, 2 skipped, my own fresh run. |
| `tests/test_knowledge_intermediate.py` alone | **PASS** — 65 passed, my own fresh run. |
| No protected-file drift beyond what's accounted for | **PASS** — `git diff a9bcd02..a420541 --name-only` shows exactly `planning/CONTEXT.md`, both `_audit`/`_drift-audit` retro files, `phase-81-second-corrective-pass.md`, and `tests/test_knowledge_intermediate.py`. Nothing in `src/`, no `decisions/*` touched at all (`git diff a9bcd02..a420541 -- decisions/ CLAUDE.md` is empty), no `CLAUDE.md` change in this range. |
| `L-086`/`L-087`/`L-088` still genuinely `status: promoted` | **PASS** — confirmed by direct read of `planning/learnings/inbox.md`: all three entries show `- **status:** promoted` in their own record. |

---

## What does NOT need to change

Nothing. The four findings from the prior FAIL are each independently
confirmed closed by direct reading of the actual test code, the actual
`CONTEXT.md` prose, the actual drift-audit file (cross-checked against
the live CLI and real docs), and the actual retro file against
`TEMPLATE.md`'s own section list — not by trusting the fix commit's own
description of itself. The underlying production code was already
confirmed correct by the prior audit and was untouched by this fix
commit (confirmed via `git diff --name-only`). No new gap, no
regression, no scope creep.

## Re-audit requirement

None further required for this specific scope. Per CLAUDE.md §5, any
further commit touching audited scope (the test file, `CONTEXT.md`, the
drift-audit record, the retro, or `src/`) would void this audit and
require a fresh pass before Phase 81 can be marked `done`. As of
`a420541`, Phase 81 (original implementation + both corrective passes)
has passed its completion audit and may proceed to the terminal
`roadmap-context-curator` reconciliation commit per CLAUDE.md §5's named
exemption.

---

---

## Prior audit (superseded — preserved verbatim for history)

# Phase 81 second corrective pass — independent completion audit

- **Auditor:** `release-phase-auditor` (fresh, independent dispatch)
- **Audited HEAD:** `a9bcd02` (`main`)
- **Scope:** the second corrective pass (`decisions/0074`), i.e. the
  implementation commit `7a0e270` plus everything after it up to and
  including `a9bcd02` — a drift-audit doc fix (`42f9486`), an L-086
  learning promotion (`2e1b5a7`/`939140e`), a user-approved CLAUDE.md §1
  amendment (`1c3981b`), and an L-087/L-088 learning-promotion record
  (`a9bcd02`).
- **Per CLAUDE.md §1's new amendment (`1c3981b`) and `.claude/agents/release-phase-auditor.md`
  item 10 (L-086)**: this corrective pass's own newly-written code was
  treated as full audited scope, not a lighter-touch re-check. Every
  claim below was independently re-verified by reading the actual
  `src/codecompass/knowledge_intermediate.py` / `cli.py` code and the
  actual test file — never taken from the ADR's or commit message's own
  prose.

## Verdict: **FAIL**

Four confirmed gaps, detailed below. None of them indicate the
*production code* for any of the fourteen corrections is wrong — every
one of the ten explicit code-behaviour checks this audit was asked to
perform (baseline-advancement semantics, apply-time concurrency,
presentation/semantic gating, post-apply grounding, type-aware dedup,
candidate-disappearance fail-closing, stable region identity, the public
template, the full test suite, lint/scripts) came back clean on direct
inspection. The FAIL is about **verification and closeout-documentation
integrity**: this phase's own authoritative documents (the ADR, the
retro, and indirectly the commit message) make specific, checkable claims
about test coverage that are false, and `planning/CONTEXT.md` has not
been updated past a point two closeout steps ago, which is itself a DoD
condition (CLAUDE.md §5) independently of whether the underlying code is
correct.

---

## 1. Baseline advancement semantics — PASS

Read `detect_grounded_region_changes` (knowledge_intermediate.py:336-396)
line by line: it only reads `.grounding-state.toml`
(`_read_simple_toml_tables`) and never calls `_write_region_baseline` or
any other mutator anywhere in its body — genuinely read-only, exactly as
its own docstring and `decisions/0074` point 1 claim.

`establish_new_region_baselines` (415-437): the loop body is gated by
`if finding.case != "new": continue` — the *only* case it ever writes a
baseline for.

`_apply_doc_region_edit` is the only place a `doc_candidate` baseline
advances: both its presentation-only branch (654-656) and both success
branches of its semantic branch (667-673, 699-705) call
`_write_region_baseline`; no other function in the module calls it for a
`doc_candidate`.

`acknowledge_stale_grounded_region` (440-469) is the only path that
advances a `claims_changed` baseline — confirmed it refuses (returns
`None`) for anything other than `finding.case == "claims_changed"`
(456-459), and `advance_doc_chunk_baseline` is the only path for the
ungrounded-chunk advisory, called nowhere automatically.

CLI check (`cli.py` `knowledge_doc_select_candidates`, 1681-1741):
confirmed it calls `establish_new_region_baselines` only (1707) — no
call anywhere in the command to `_write_region_baseline`,
`acknowledge_stale_grounded_region`, or `advance_doc_chunk_baseline`.
Two new, separate commands (`doc-acknowledge-stale`,
`doc-acknowledge-chunks`, 1744-1783) own those explicitly.

## 2. Grounded-doc apply-time concurrency — PASS

`_apply_doc_region_edit` (601-706): recomputes `current_region_hash` and
compares against `item.get("base_region_hash")` (613-620, region-text
check, pre-existing from `decisions/0073`), **then** separately
recomputes `current_hashes = _current_cited_hashes(project_root,
cited_ids)` and compares every `rid` in `cited_ids` against
`expected_hashes` built from `item.get("cited_hashes_at_detection")`
(624-635) — a genuinely new, independent check. Either mismatch returns
`ApplyOutcome(False, item, ...)` with no record written in between (no
`_write_record`/`_write_region_baseline` call precedes either `return`).
Confirmed live by test `test_apply_refuses_when_cited_claim_changes_before_apply`
(tests/test_knowledge_intermediate.py:1309), which mutates the cited
record's YAML after manifest-write and asserts zero new records exist
afterward.

## 3. Presentation-only vs semantic reconciliation — PASS

`_apply_doc_region_edit` line 647: `if not item.get("semantic_change",
False):` branches to the presentation-only path, which writes the
baseline but never calls `_write_record` or touches `records`/`new_id` —
confirmed no Claim-creation code is reachable in that branch. The
`semantic_change = True` path is the only one that reaches
`_find_existing_promoted_record(... kind="claim")` / `_write_record`.
Tests `test_presentation_only_edit_creates_zero_claims` and
`test_semantic_edit_creates_candidate_claim` (1357, 1376) both exercise
real detect→manifest→apply round trips and assert record counts, not
just mocked calls — genuine.

## 4. Post-apply grounding — PASS

`_add_cited_id_to_grounding_marker` (559-598) is called from both
success branches of the semantic-edit path (665, 697) — confirmed by
reading the call sites, not assuming from the docstring. Verified it
preserves an existing `region:<id>` token: line 587,
`suffix = f" region:{this_region_id}" if this_region_id else ""`, appended
*after* the rebuilt id list — so the rewritten header is
`"CL-OLD, CL-NEW region:<id>"`, not corrupted. The region's own content
hash used for the baseline (`region_hash_for_baseline`, computed once at
line 645 from the body between markers, never the header) is unaffected
by this header rewrite, preventing a self-inflicted redetection loop.
Test `test_new_claim_is_discoverable_from_region_after_reconciliation`
(1398) confirms via the real `find_grounded_doc_regions` lookup, not a
mocked parse.

## 5. Type-aware dedup — PASS (code), **test-coverage claim is false**

Code: `_find_existing_promoted_record` (1746-1788) takes `kind: str =
"claim"` and filters `if record.kind != kind: continue` (1777) before
ever comparing statement text. Every call site passes an explicit,
correct kind: `_apply_doc_region_edit` → `kind="claim"` (663);
`_apply_anchor_edit`'s semantic branch → `kind="claim", depends_on=record_id`
(1882-1884); `_apply_requirement_proposal` → `kind="requirement",
decision=decision_id` (1941-1943); `_apply_candidate_addition` → both its
disappeared-text branch (1998) and its normal path (2019) use
`kind="claim"`. All five call sites are correctly type-scoped.

**However**: despite `decisions/0074`'s own "Consequences" section and
`planning/retros/phase-81-second-corrective-pass.md` explicitly claiming
the 29 new tests cover "cross-kind dedup independence in both
directions," **no test in `tests/test_knowledge_intermediate.py` actually
exercises this.** A full-file grep for `kind="claim"`, `kind="requirement"`,
`cross`, `dedup`, or any scenario creating a pre-existing Requirement and
Claim with byte-identical statement text found nothing. This is a
genuine, checkable overclaim, not a close call — see Finding A below.

## 6. Candidate disappearance handling — PASS (code), **test-coverage claim is false**

Code: `_apply_candidate_addition`'s `text_present` branch (1989-2012)
only returns `ApplyOutcome(True, ...)` when
`_find_existing_promoted_record(records, claim_statement, kind="claim")`
actually finds a match (1998-2005); the `else` falls through to an
explicit `ApplyOutcome(False, item, "apply-time race: ...")` (2006-2012)
with no record created. Correctly implemented, matching `decisions/0074`
point 8 exactly.

**However**: the same retro/ADR claim this is covered by "candidate-
disappearance fail-closed behaviour" among the 29 new tests. A grep for
`apply-time race`, `no longer present`, and `_candidate_text_present`
across the test file returns **zero hits** for this specific code path
(the only "apply-time race" tests that exist, `TestApplyTimeRace`/
`TestGroundedDocApplyTimeConcurrency`, both cover the *anchor-edit* and
*grounded-doc* races, not the ordinary-candidate-text-disappeared race
this point is about). Another genuine overclaim — see Finding A.

## 7. Stable grounded-region identity — PASS

`parse_grounding_markers` (174-205) parses `region:<id>` via
`_REGION_ID_RE`. `DuplicateGroundingRegionIdError` is genuinely raised by
`_check_no_duplicate_region_ids` (216-235), called unconditionally at the
top of `detect_grounded_region_changes` (356) — not just claimed in a
docstring. Read `test_duplicate_region_ids_fail_closed` (1166) directly:
it writes two real markers sharing `region:dup` and asserts
`pytest.raises(ki.DuplicateGroundingRegionIdError)` on a real
`detect_grounded_region_changes` call — a genuine exercise, not a stub.
Read `test_region_id_survives_insertion_above` (1131) directly too: it
establishes a baseline, then inserts an entirely new grounded region
*above* the existing one in the live file, and asserts the original
region (now at a different positional index) is still recognised as
`"noop"` by its own id, while the new one is `"new"` — a real,
substantive insertion test, not a trivially-named one.

## 8. Public template state — PASS

```
cd codecompass-template && git fetch origin main && git log origin/main --oneline -3
bd2420d docs: update optional knowledge-layer docs for the corrected workflow
a429f04 feat: lightweight optional-intermediate-knowledge/ directory
68bae8e fix: close usability gaps found by a fresh-adopter exercise
```
`bd2420d` is genuinely present on the real `ctosullivan/codecompass-template`
remote. Spot-checked the rewritten `README.md`/`worked-example.md`
content against the real CLI behaviour verified in sections 1-7 above:
`doc-select-candidates`/`doc-acknowledge-stale`/`doc-acknowledge-chunks`,
the `semantic_change` field, `region:<id>` syntax, and `Type: Intent`
header-stripping are all described accurately and consistently with the
real code — no contradiction found.

## 9. Combination regression tests

- `.venv/bin/python -m pytest -q`: **841 passed, 2 skipped** — ran it
  myself to completion (208.65s), not trusting the reported "830 passed"
  figure from the ADR/commit message (the discrepancy is just that more
  commits landed test-suite-wide since `7a0e270`; nothing here is a
  regression).
- `.venv/bin/ruff check src/ tests/ scripts/`: **All checks passed!**
- `.venv/bin/python scripts/check_knowledge_base.py --strict`: one
  `info`-level finding, exit code 0 — unrelated to Phase 81
  (`first-party-source-symbols` slug, a pre-existing, honestly-labelled
  "expected and healthy" lifecycle-status divergence, not this phase's
  scope).
- `.venv/bin/python scripts/check_user_docs.py --strict`: **no
  findings**, exit code 0.

## Standard DoD checklist (CLAUDE.md §5)

| Condition | Result |
|---|---|
| Plan file's corrective-pass notes updated | **PASS** — `planning/phase-81-intermediate-knowledge-layer.md` Status line and amendment note accurately describe all ten corrective-pass items and the still-pending audit. |
| `docs/` updated and accurate | **PASS** — `docs/codecompass-knowledge-workflow.md` and `docs/cli-reference.md` both document `doc-acknowledge-stale`/`doc-acknowledge-chunks`, `semantic_change`, and `region:<id>` accurately, cross-checked directly against the real code. |
| New ADR exists, append-only | **PASS** — `decisions/0074` is new; `git log --oneline -- decisions/0071...md decisions/0072...md decisions/0073...md` shows each has exactly one commit (its own original creation) — none touched since. |
| Changelog entry added | **PASS** — a correctly-scoped, distinct `[Unreleased]` "Fixed" entry for "Phase 81 ... second corrective pass" exists, separate from the first corrective pass's own entry. |
| `planning/CONTEXT.md` reflects current state | **FAIL** — see Finding B. |
| Retro exists, template sections substantive | **FAIL (partial)** — see Finding D. |
| Candidate learnings triaged | **PASS** — `L-086`/`L-087`/`L-088` are all genuinely `status: promoted` in `planning/learnings/inbox.md`, with real landing commits cross-referenced in `planning/learnings/promoted.md` (`@ 2e1b5a7`, `@ 1c3981b` ×2) — verified the commits themselves exist and touch what they claim (`.claude/agents/release-phase-auditor.md` item 10; `CLAUDE.md`/`CONTRIBUTING.md` §1 additions). |
| No protected-file drift | **PASS** — the only `CLAUDE.md` change in the audited range is `1c3981b`, user-approved per the task framing and per §0's own citation in that commit's message; nothing else in the range touches `CLAUDE.md`. |
| Changed-file list matches plan scope | **PASS** — `git diff --name-only 7a0e270^..HEAD` shows only the expected set (src/cli.py, src/knowledge_intermediate.py, tests, docs, decisions/0074, CHANGELOG, CONTEXT, ROADMAP, learnings files, the retro, the plan file, README.md's own marker migration, ai-docs/README.md's drift fix, `.claude/agents/release-phase-auditor.md`, CLAUDE.md/CONTRIBUTING.md, `.grounding-state.toml`, and the governance-changes staging doc) — no scope creep. |
| Independent `docs-reconstructor` drift audit, NO DRIFT | **FAIL (unverifiable as persisted)** — see Finding C. |

---

## Findings requiring a fix before re-audit

**Finding A — overstated test coverage (the most serious finding).**
`decisions/0074`'s "Consequences" section and
`planning/retros/phase-81-second-corrective-pass.md` both explicitly
claim the 29 new tests cover "`Type: Intent` header-stripping,"
"candidate-disappearance fail-closed behaviour," and "cross-kind dedup
independence in both directions." None of these three are actually
tested:
1. The only test touching the `Type: Intent` path
   (`test_declared_intent_via_explicit_type_becomes_proposed_policy`,
   line 1027) never asserts `records[new_id].fields["statement"]` at
   all — it would pass identically whether or not the header-stripping
   fix (point 7) were present, since it only checks the unrelated
   `basis` field.
2. No test anywhere exercises `_apply_candidate_addition`'s "candidate
   text no longer present, no matching record" fail-closed branch
   (point 8) for an ordinary external candidate — the only
   "apply-time race" tests that exist cover the *anchor-edit* and
   *grounded-doc* races, a different code path entirely.
3. No test creates a Claim and a Requirement (or vice versa) with
   identical statement text and confirms neither blocks or satisfies
   the other's dedup check (point 9) — the `kind` parameter's own
   call-site correctness (confirmed correct by direct reading) has zero
   regression protection.

The underlying *code* for all three corrections is genuinely correct on
direct inspection — this is not a "the fix doesn't work" finding. It is
a "the project's own closeout documents assert verification that was
never actually performed" finding, which is exactly the class of defect
this project's own `L-070`/`L-075` (fail-closed mechanisms need edge-case
tests, including depth not just scope) and `L-086` (a corrective pass's
own new code is full audited scope, found precisely by not trusting a
prior pass's own self-report) exist to catch. **Required fix:** add three
tests — (a) assert the resulting Claim's `statement` does not contain
"Type: Intent" and equals exactly the stripped body; (b) a scenario where
a candidate block is detected, then deleted/edited in the live file
before apply with no matching canonical record, asserting the apply
fails closed with zero records created; (c) a scenario with a
pre-existing Claim and an explicit `Type: Requirement` proposal sharing
identical statement text (and the reverse), asserting both are created
as distinct records of their own kind.

**Finding B — `planning/CONTEXT.md` is one closeout step behind the
real state.** Its "Current phase" section (lines 8-72) still reads "Next
concrete step: run the remaining closeout sequence — fresh per-phase
docs-drift audit, learning/context-gap triage, and a fresh independent
completion audit" as if all three are still pending. In fact,
`git log --oneline -- planning/CONTEXT.md` shows it was last written at
`7a0e270` (the implementation commit itself) and never touched again,
even though the drift audit (`42f9486`, "found by this pass's own drift
audit") and the full learning triage (`2e1b5a7`, `939140e`, `1c3981b`,
`a9bcd02`) both landed afterward. CLAUDE.md §4/§5 require this file to
reflect current state; it currently describes two already-completed
steps as not-yet-done. **Required fix:** update `planning/CONTEXT.md`'s
Phase 81 narrative to state that the drift audit and learning triage are
complete, and that only this completion audit remained.

**Finding C — no persisted drift-audit report for the second corrective
pass.** Unlike the established convention for most other phases in this
project (`planning/retros/_drift-audit-phase-N.md`), there is no such
file for Phase 81 at all (original, first corrective pass, or second
corrective pass) — only `_audit-phase-81.md` (a *completion* audit, which
does mention a drift audit "ran mid-phase" for the *original*
implementation). For the second corrective pass specifically, the only
evidence a `docs-reconstructor` drift audit ran is a single commit
message's own passing remark in `42f9486` ("found by this pass's own
drift audit") — fixing one real `ai-docs/README.md` staleness. There is
no record of that audit's full scope, nor a final "NO DRIFT" verdict
confirming the fix actually closed it out, anywhere in `CONTEXT.md`, the
retro, or a standalone file. Given this project's own `L-060`-driven
principle that a durable, persisted artifact is what makes a completion
transition real rather than a conversational claim, this is a genuine
gap, independent of whether the fix itself was adequate (it was, on
inspection). **Required fix:** either produce a short
`planning/retros/_drift-audit-phase-81-second-corrective-pass.md`
recording the audit's scope and final NO-DRIFT verdict (even
retroactively, since the fix already landed), or explicitly document in
`CONTEXT.md`/the retro exactly what was checked and the final clean
result, so a future reader doesn't have to reconstruct this from one
commit message.

**Finding D — retro is missing several required TEMPLATE.md sections.**
`planning/retros/phase-81-second-corrective-pass.md` has only Goal /
Delivered / Real dogfood validation / Lessons learnt. Missing, relative
to `planning/retros/TEMPLATE.md`, for a phase this substantive (14
defects, a new ADR, a public-repo push, 29 claimed tests): a
Date/Commit(s)/Agents-used header; **Where we are** (which stage/
milestone this sits in, what the previous phase established); an
explicit **What worked** / **What didn't work** split (distinct from
"Lessons learnt"); **Process-improvement feedback**; **Candidate
learnings filed** (the learnings exist and are triaged — per Finding
check, L-086/087/088 — but the retro itself doesn't name them); **Where
we're going** (next phase, any gate ahead, whether this confirmed or
changed the trajectory); and a **Time/cost note**. This phase is not
"genuinely trivial" by this audit's own standing bar (fourteen real
defects, a new mechanism-level ADR, a public template push) so the full
template applies. **Required fix:** expand the retro with the missing
sections.

---

## What does NOT need to change

Every one of the ten code-behaviour checks (sections 1-8 above) passed
on direct, independent inspection of the real code and real tests — no
regression, no mis-wired call site, no silently-reintroduced defect from
the first corrective pass. The full test suite is genuinely green (841
passed, 2 skipped), lint is clean, both strict doc/knowledge-base checks
pass, the public template push is real and accurate, and the protected-
file/scope-creep checks are all clean. **Do not re-implement anything in
`src/codecompass/knowledge_intermediate.py` or `cli.py`** — the fix for
this FAIL is entirely in test coverage (Finding A) and closeout
documentation (Findings B, C, D).

## Re-audit requirement

Per CLAUDE.md §5, any commit that touches the findings above (new tests,
`CONTEXT.md`, a drift-audit record, the retro) voids this audit and
requires a fresh pass before Phase 81 can be marked `done` again.
