# Phase 81 (third corrective pass) — independent completion audit

- **Auditor:** release-phase-auditor (independent subagent pass)
- **Date:** 2026-10-08
- **HEAD audited:** `de8e627` (branch `main`)
- **Commits in scope:** `34f81fc` (implementation) + `de8e627` (learning-triage
  retro update). Prior history (`a420541`..`d96fec1`) is the already-audited
  second corrective pass, not re-litigated here except to confirm this pass's
  diff didn't touch it.
- **Verdict: PASS**

Per `.claude/agents/release-phase-auditor.md` item 10 (`L-086`), this pass's
own newly-written code was treated as full audited scope — every claim below
was independently re-derived from the actual code and tests, not taken from
the commit message, ADR, or retro's own account.

## 1. Defect 1 — Requirement candidate-presence check (decisions/0075 point 1)

Read `_requirement_proposal_validity`, `_CandidateIdentity`,
`_derive_candidate_identity`, and `_apply_candidate_addition` in full
(`src/codecompass/knowledge_intermediate.py:1954-2147`).

- `_derive_candidate_identity` is called exactly once per candidate
  (`_apply_candidate_addition` line 2069), **before** the live-text
  `_candidate_text_present` check (line 2071), for every candidate shape
  (explicit `Type: Requirement`, `Type: Intent`, plain prose) — confirmed by
  reading the branching logic: all three return paths of
  `_derive_candidate_identity` are reached before the presence check, and the
  presence check's own fallback search (`_find_existing_promoted_record`)
  uses that one identity's `kind`/`decision`, never a separately recomputed
  value.
- Only after `text_present` is true does control reach the type-specific
  apply (`_apply_requirement_proposal` for `identity.kind == "requirement"`,
  the ordinary Claim-creation path otherwise) — confirmed by reading lines
  2100-2147.
- `test_deleted_requirement_candidate_with_no_match_fails_closed`
  (`tests/test_knowledge_intermediate.py:1596`) genuinely asserts more than
  a falsy result: `result.applied == []`, `"race" in result.skipped[0].reason`,
  `records_after == records_before`, **and** `not any(r.startswith("REQ-")
  for r in records_after)` — a real, specific assertion that zero REQ-
  records were created, not merely that the call "failed".
- `test_deleted_requirement_candidate_already_applied_is_safe_noop`
  (line 1624) genuinely pre-creates a real `REQ-DEMOSLUG-099.yaml` with the
  **same statement** ("Add Y.") **and same decision** (`DEC-DEMO-001`) as the
  deleted candidate would have produced, then asserts apply reports success
  pointing at that exact id and that no second REQ- record exists afterward.
  This is a real idempotency test, not a stub.
- `test_ordinary_claim_candidate_disappearance_still_fails_closed` (line
  1659) is present, unrelated to the Requirement path, and passes — the fix
  did not disturb plain-Claim disappearance behaviour.

All three tests pass in isolation and as part of the full 73-test module run
(see §9 below).

## 2. Defect 2 — grounding cited-id membership (decisions/0075 point 2 & 3)

Read `detect_grounded_region_changes` (lines 336-420) and
`_apply_doc_region_edit` (lines 625-700+) in full.

- `membership_changed = sorted(ids) != sorted(base_cited_ids)` (line 396) is
  genuinely order-insensitive (uses `sorted()`, not sequence equality) and
  add/remove-sensitive, folded into `structural_changed = region_changed or
  membership_changed` (line 408) — a membership-only change produces `case =
  "doc_candidate"`, never `"noop"` (confirmed by the case-table logic at
  lines 409-416).
- `claims_changed` is correctly restricted to `common_ids = set(ids) &
  set(base_cited_ids)` (lines 402-407), so an added/removed id is never
  double-counted as "its own content changed."
- `_apply_doc_region_edit`'s new check (lines 652-660) compares
  `sorted(cited_ids)` (live) against `sorted(item.get("cited_ids", []))`
  (manifest snapshot) immediately after the region-text-hash check and
  before the per-id content-hash check, failing closed (no record, no
  baseline write) on any mismatch — same order-insensitive policy as
  detection.
- `test_removing_a_cited_id_is_not_noop` (line 1710) genuinely asserts
  `findings[0].case == "doc_candidate"` (not just `!= "noop"`) on first
  detection, **and** re-runs detection a second time to confirm the finding
  stays `"doc_candidate"` (not silently cleared) — matching decisions/0074
  point 1's non-acknowledgement-by-detection discipline.
- `test_adding_a_cited_id_is_not_noop` (line 1726) is the add-side mirror
  and passes.
- `test_reordering_cited_ids_only_is_noop` (line 1737) genuinely swaps the
  order of the same two ids and asserts `case == "noop"` — confirms the
  order-insensitive policy is implemented via `sorted()` comparison, not a
  stricter sequence check that would wrongly flag reorders.
- `test_membership_removed_before_apply_fails_closed` (line 1774) genuinely
  mutates membership *between* `write_doc_candidates_to_manifests` and
  `apply_manifest`, with the region's own prose already changed too (so it
  isolates the membership check specifically) — asserts `result.applied ==
  []`, `"membership" in result.skipped[0].reason`, and that the only records
  in the slug afterward are the two pre-existing `CL-X-001`/`CL-X-002` (zero
  stray records).
- `test_membership_reordered_only_does_not_block_apply` (line 1800) performs
  the identical sequence but only reorders (not removes) the cited ids
  between detection and apply, and asserts `len(result.applied) == 1` —
  confirms the apply-time check is itself order-insensitive, matching
  detection's own policy.

## 3. Regression: stable `region:<id>` identity (decisions/0074 point 10)

`git diff d96fec1 34f81fc -- tests/test_knowledge_intermediate.py` is purely
additive (new hunk starts at line 1579, appending 244 new lines; nothing
before that line changed). `TestStableGroundedRegionIdentity` is therefore
untouched by this pass, and its 2 tests pass
(`pytest -k TestStableGroundedRegionIdentity` → `2 passed`).
`git diff d96fec1 34f81fc -- src/codecompass/knowledge_intermediate.py`
confirms `_region_state_key`, `_check_no_duplicate_region_ids`, and
`_locate_live_region` are not among the changed hunks — only
`detect_grounded_region_changes`, `_apply_doc_region_edit`,
`_apply_requirement_proposal` (factored), the new `_CandidateIdentity`/
`_derive_candidate_identity`, and `_apply_candidate_addition` were touched.

## 4. Full test/lint/strict-check results (independently re-run, not trusted from commit message)

- `.venv/bin/python -m pytest -q` → **853 passed, 2 skipped in 223.66s**
  (matches the commit message's claim exactly — independently re-run, not
  assumed).
- `.venv/bin/python -m pytest tests/test_knowledge_intermediate.py -q` →
  **73 passed** (matches the claimed count).
- `.venv/bin/ruff check src/ tests/ scripts/` → **All checks passed!**
- `.venv/bin/python scripts/check_knowledge_base.py --strict` → one finding,
  `info`-level, `knowledge-base-snapshot-current-divergence` on
  `CL-FPSS-007` (`first-party-source-symbols`) — this is the pre-existing,
  unrelated finding the task explicitly flagged as expected; confirmed it is
  not in any file this pass touched.
- `.venv/bin/python scripts/check_user_docs.py --strict` → **no findings**.

## 5. Docs accuracy (spot-checked against real code, not trusted from drift-audit report)

- `docs/cli-reference.md`'s `doc-select-candidates`/`apply` section now
  describes "the region's own text, the *set* of cited records
  (order-insensitive...), and every cited record's own content" being
  re-verified at apply, failing closed if any of the three moved — this
  matches the actual three checks read in `_apply_doc_region_edit`
  (region-text hash, cited-id-set, per-id content hash) in that exact order.
- `docs/codecompass-knowledge-workflow.md`'s new bullet on "the marker's own
  cited-id list changes" correctly describes order-insensitivity and
  add/remove-sensitivity, matching `membership_changed`'s actual
  implementation.
- Both the CLI reference's `doc-select-candidates` subcommand name and
  `cli.py`'s actual `@knowledge_app.command("doc-select-candidates")`
  registration were cross-checked and match.

## 6. ADR / protected-file / changed-file-scope checks

- `decisions/0075-knowledge-layer-third-corrective-pass.md` is new,
  append-only, explicitly "refines, rather than reverses"
  `decisions/0071`-`0074`.
- `git diff d96fec1 de8e627 --stat -- decisions/0071* decisions/0072*
  decisions/0073* decisions/0074* CLAUDE.md` → **empty** — confirms no past
  ADR's original content was touched and no CLAUDE.md change occurred in
  this pass's commits, as expected (none was needed).
- `git diff d96fec1 34f81fc --stat` (implementation commit) touched exactly:
  `CHANGELOG.md`, `decisions/0075-*.md` (new), `docs/cli-reference.md`,
  `docs/codecompass-knowledge-workflow.md`, `planning/CONTEXT.md`,
  `planning/ROADMAP.md`, `planning/phase-81-intermediate-knowledge-layer.md`,
  `planning/retros/phase-81-third-corrective-pass.md` (new),
  `src/codecompass/knowledge_intermediate.py`,
  `tests/test_knowledge_intermediate.py`. `git diff 34f81fc de8e627` touched
  only `planning/retros/phase-81-third-corrective-pass.md` (the
  learning-triage update). Both match `decisions/0075`'s own "Consequences"
  section and the task's expected scope — no scope creep.
- `CHANGELOG.md` has a `[Unreleased]` → `### Added` → `Phase 81` entry
  describing the layer as a whole (this is the same running Phase 81 entry
  updated across all three corrective passes, consistent with this
  project's established pattern for a reopened phase, not a new/duplicate
  entry).
- `planning/CONTEXT.md` accurately reflects the current, honest state: Phase
  81 `reopened` for a third pass, both defects described correctly, "next
  concrete step" naming the fresh independent completion audit as the
  remaining gate — accurate as of the state prior to this audit running.
- `planning/ROADMAP.md`'s Phase 81 row status is `reopened`, not
  prematurely flipped to `done` before this audit — correct per CLAUDE.md
  §5's ordering requirement.
- `planning/phase-81-intermediate-knowledge-layer.md`'s top-of-file status
  and "Third corrective-pass amendment note" accurately summarize
  `decisions/0075` and correctly state §4.4/§9 are unaffected in substance.

## 7. Retro shape (planning/retros/phase-81-third-corrective-pass.md)

Checked section-by-section against `planning/retros/TEMPLATE.md`: Where we
are, Goal, Scope delivered vs planned, What was achieved, What worked, What
didn't work, Lessons learnt, Process-improvement feedback, Candidate
learnings filed, Where we're going, Time/cost note — all present and
substantive (not stubs), including a "Real dogfood validation" section
beyond the template's own minimum. One minor, non-blocking cosmetic gap: the
header's `**Commit(s):**` field is still a placeholder ("this pass's own
implementation + validation commit(s), recorded at closeout") rather than
the actual hashes (`34f81fc`, `de8e627`) — harmless since it will be filled
by the terminal `roadmap-context-curator` reconciliation commit, but worth
closing out at that step rather than leaving indefinitely.

## 8. Knowledge-curator triage (spot-checked, not blindly accepted)

The retro's "Candidate learnings filed" section claims both retro-surfaced
observations are adequately covered by `L-075` (CLAUDE.md §1, scope≠depth
for fail-closed checks), `L-087` (persisted-state detection-vs-
acknowledgement), and `L-085` (two-part filter/gate mechanisms). Checked
`planning/learnings/promoted.md`: all three ids exist and are described
there consistently with how the retro invokes them. The reasoning —
declining a third near-duplicate CLAUDE.md §1 amendment for a
concurrency-identity-completeness point already covered by an existing
project rule, and declining a generic single-source-of-truth code-review
observation as not CodeCompass-specific — is defensible, not a rubber stamp:
both candidates genuinely restate principles already codified rather than
surfacing a new, distinct recurring failure shape. Context-gap/observation
queues were checked and correctly judged not applicable (both defects are
internal implementation bugs, not context-graph/mechanical-detection gaps).

## 9. docs-reconstructor NO DRIFT (spot-checked, not re-run from scratch)

Per the task's framing this ran in-session and was not persisted to a
separate file this pass (acceptable — only `release-phase-auditor`'s own
report has a hard persistence requirement). Spot-checked its implicit scope
by independently reading `docs/cli-reference.md` and
`docs/codecompass-knowledge-workflow.md`'s actual diffs (§5 above) and
confirming they match the real code; found no drift myself in the files
this pass touched. Did not re-run a full README/ai-docs reconstruction
(out of scope for a per-phase drift check; that is a milestone activity).

## Summary of what was independently re-derived (not trusted from any report)

- Both defects' fixes, read directly from source, confirmed structurally
  correct and ordered exactly as decisions/0075 claims.
- All 8 new tests read in full and confirmed to assert the specific,
  non-trivial conditions the task asked about (zero-records-created, not
  merely falsy; genuine pre-existing-duplicate idempotency; stays-pending
  across repeated detection; order-insensitive via `sorted()`, not stricter
  sequence equality).
- Full test suite (853 passed/2 skipped), module suite (73 passed), ruff,
  `check_knowledge_base.py --strict`, `check_user_docs.py --strict` all
  independently re-run with results matching what was claimed.
- Git diffs across both commits in scope confirm no protected-file drift,
  no undeclared scope creep, and that `TestStableGroundedRegionIdentity`
  and its backing functions are untouched.

## Verdict: PASS

No blocking gaps found. One non-blocking cosmetic observation: the retro's
own `**Commit(s):**` header field is still a placeholder and should be
filled with the real hashes (`34f81fc`, `de8e627`) as part of the terminal
`roadmap-context-curator` reconciliation commit that flips Phase 81 back to
`done`.

This audit's own pass covers commits `34f81fc` and `de8e627` only. Per
CLAUDE.md §5's exemption, the upcoming terminal reconciliation commit
(ROADMAP.md → `done`, CONTEXT.md current-state rewrite, phase plan file
Status line) does not void this PASS provided it touches nothing else; any
other change touching audited scope after this point requires a fresh
audit.
