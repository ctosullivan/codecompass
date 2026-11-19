# Phase 89 Stage 89B retro — the new gap kind and the documentation-cascade demonstration

- **Date:** 2026-11-19
- **Commit(s):** (pending — see completion report for exact status)
- **Agents used:** general-purpose (×~16, real semantic/editorial doc
  reviews), knowledge-curator (learnings triage), release-phase-auditor
  (Part A re-verification and Stage 89B audit)

## Where we are

Phase 89 (Incremental Knowledge and Documentation Reconciliation) is
split into three stages. Stage 89A (detection, durable Evidence,
human-approved canonical reconciliation) was implemented, corrected
twice, and independently audited **PASS**, landing at commit `61591f4`.
This dispatch ("Final Stage 89A Verification and Phase 89B
Implementation") first re-verified that committed state (Part A —
see `planning/retros/_audit-phase-89-stage-89a.md`'s third audit
section for the process-completeness findings that surfaced and were
fixed), then proceeded to Stage 89B: the one new `find_gaps` gap kind
the plan names (`claim_contradicted_by_fresh_check`) and the end-to-end
documentation-invalidation cascade that Stage 89A's own reconciliation
mechanism feeds into via the pre-existing, unmodified Phase 87
machinery. Overall project state after this stage: CodeCompass can now
surface a pending, unreviewed contradiction through its consolidated
knowledge API, and has been shown, live, to propagate a real source
change through detection → verified Evidence → reviewed canonical
knowledge → precisely-targeted documentation invalidation →
reviewed, accurate republication, for both of the project's two real
detector pathways.

## Goal

Implement Stage 89B's one named new primitive (plan §5.4) and
demonstrate the full documentation-reconciliation cascade (plan §6.2's
doc-invalidation leg) end to end against real Ledgerkit data, without
redesigning Stage 89A, reimplementing Phase 87's documentation
machinery, or beginning Stage 89C.

## Scope delivered vs planned

Delivered exactly what the plan's own Stage 89B entry (§7) names:
- `Gap.label` (new, additive field) and `source_reconciliation.
  pending_contradicting_findings` + its wiring into `knowledge_api.
  find_gaps` as the new `claim_contradicted_by_fresh_check` kind.
- The end-to-end Task-A documentation-invalidation demonstration for
  **both** detectors (the plan names doing this for the Task-A
  scenario specifically; this round additionally exercised detector
  (a)'s own regression pathway through the same cascade, which the
  plan's §6.2 lists as the "existing-coverage positive control" the
  dispatch's own Part C explicitly also requires).
- The disposable-schema-governed-document fallback (no real grounded
  region citing any `CL-BFS-*` Claim exists yet), exactly as the plan's
  own §6.2 anticipated as a named, non-manufactured contingency.

**Deviation, disclosed**: the plan's own Stage 89B unit-test list names
"an end-to-end scratch-copy run of the full §3 diagram ... for both
detectors" as the test; this round additionally produced a second,
real artifact not explicitly named in the plan — a live demonstration
of the `concurrent_conflict` protection path (a human-edited region
colliding with a concurrently-reconciled Claim), surfaced naturally by
doing the full regression cascade honestly rather than engineered.
Reported as a bonus finding, not scope creep — no new mechanism was
built to produce it; it is the pre-existing Phase 87 concurrency model
doing exactly what it already does.

## What was achieved

- 11 new, targeted unit tests for the new gap kind
  (`tests/test_knowledge_api.py::TestClaimContradictedByFreshCheckGap`),
  covering: correct `"regression"`/`"newly_discovered_failure"` label
  pass-through; a supporting (PASS) finding never misreported as a
  contradiction; already-applied and rejected items never reported;
  a tampered/invalid result excluded; duplicate pending manifests
  deduplicated to one gap; a stale duplicate already resolved via a
  sibling manifest correctly suppressed; aggregate and superseded
  Claims never reported here (Stage 89A's own scope-eligibility rule
  respected); and a direct read-only guarantee check.
- A real, live Ledgerkit demonstration of the new gap kind against a
  genuine regression (`CL-BFS-002`), correctly labelled `"regression"`,
  visible before review and gone after a reviewed `apply`
  (`planning/retros/phase-89-stage-89b-ledgerkit-demonstration.md`).
- A real, live documentation cascade for detector (b) (`CL-BFS-004`,
  newly-covered) and detector (a) (`CL-BFS-002`, a genuine regression),
  both through the actual `docs compile`/`record-review`/`publish`/
  `maintain` CLI, including the real AI composer and independent
  `general-purpose`-dispatch reviews — not a mocked or hand-authored
  shortcut.
- A disposable, three-section schema-governed document exercising all
  three real `GroundedRegionFinding` outcomes this demonstration could
  reach in sequence: `new` → `noop` → `claims_changed` →
  (`gap_blocked` at compile time, correctly) → `concurrent_conflict`
  (after a hand-edit) — never auto-resolved past a point a human should
  decide.

## What worked

- **Running the real pipeline, not a synthetic fixture built to pass,
  surfaced two real, reproducible gaps in the existing Phase 87
  composer prompt** (under-hedging a `partially_supported` Claim's own
  test-coverage status in a register reviewers accept; adding
  plausible mechanism detail beyond an oracle-run record's own stated
  scope) that a hand-crafted "it just works" demonstration would never
  have found. This is the same lesson Stage 89A's own retro already
  drew from its real demonstration catching two implementation bugs a
  synthetic unit suite missed — now confirmed a second time, one layer
  up the stack (documentation generation, not reconciliation).
- **The existing, unmodified `contradiction` gap check and
  `concurrent_conflict` classification both fired correctly, unprompted,
  the moment this demonstration's own real state genuinely reached
  them** — no new code was needed to protect against auto-generating
  prose for a contested Claim or silently overwriting a human edit;
  Phase 87's own pre-existing machinery already does this.
- **The "draft patching" pattern** (hand-editing a pending review's own
  `tagged_draft` and recomputing its hash via the real, unmodified
  `doc_compiler`/`oracle` functions, then re-dispatching review against
  the patched text) that Phase 87C's own retro first named as an
  established lead-orchestration activity scaled cleanly to a
  multi-round iteration loop here too.

## What didn't work

- Iterating purely by re-running the real AI composer (hoping sampling
  variance would fix an editorial/semantic finding) did not reliably
  converge — two consecutive re-compiles of `overlapping-patterns`
  reproduced variations of the same heading/overclaim problems rather
  than progressing. Switching to direct lead draft-patching (informed
  by the specific reviewer finding) converged in every case; pure
  re-roll did not.
- One review round (`overlapping-patterns`, round 2's semantic check)
  produced a spurious UNSUPPORTED finding caused by this session's own
  abbreviated record excerpt in that round's review prompt, not a real
  defect in the draft — caught and corrected the next round by
  supplying the record's full, verbatim text. A process note, not a
  pipeline defect: a reviewer can only be as accurate as the evidence
  it is actually given.

## Lessons learnt

A documentation-composer system prompt tuned against one Claim's own
historical failure modes (Phase 87C's own three-round tightening,
already baked into `build_system_prompt`) does not automatically
generalize to a *different* Claim with a *different* evidence shape
(here: a partially-confirmed, source-only Claim, rather than Phase 87C's
fully-supported one) — the same "a fix scoped to one shape doesn't
generalize to a different shape" pattern this phase's own Stage 89A
history already demonstrated for audit checklists (see that stage's
own retro addendum and the new candidate learning filed for it) is now
also true of the composer prompt itself, one layer up the pipeline.

## Process-improvement feedback

- Give a reviewer dispatch the record's exact, full, verbatim field
  values every time, never a hand-summarised excerpt — the one
  spurious finding this round produced came directly from an
  abbreviation, not from the reviewer's own judgment.
- `docs compile` recompiles every section in a schema on each call,
  even ones that are already correctly `noop` — harmless here (an
  unrelated section's unchanged redraft was simply never published),
  but worth a future, narrow enhancement (compile only sections named,
  or only ones `docs maintain` actually flagged) if this pipeline sees
  heavier real use.

## Candidate learnings filed

One new candidate learning naming the composer-prompt-generalization
finding above (see `planning/learnings/inbox.md` for its exact id,
filed alongside this stage's own triage of `L-135`/`L-136` from Stage
89A — see `_audit-phase-89-stage-89a.md`'s third audit section for why
those needed triage at all).

## Where we're going

Stage 89C (Task B's own pre-registered controlled comparison) is the
only remaining piece of Phase 89's own roadmap exit gate (plan §8,
gate 2/3) — explicitly **not** started, attempted, or altered by this
stage, per this dispatch's own authorisation boundary. Task B's
pre-registration (`planning/retros/phase-89-ledgerkit-two-task-
demonstration.md`) is unchanged. Phase 89 remains `in progress`.

## Time / cost note

A single long session. Real cost drivers, disclosed rather than
estimated: ~16 real `general-purpose` review dispatches (~39k tokens/
~20s each, per this session's own measured `<usage>` figures — roughly
600k tokens combined), 2 real `docs compile` AI-composer calls (one per
cascade round touching `overlapping-patterns`, each a genuine Anthropic
API call via the project's own clean-room broker), plus the lead's own
orchestration time (scratch setup, two full real CLI detect→verify→
apply sequences, draft patching across up to 4 rounds for one section,
and this write-up). No retries beyond the documented review-iteration
rounds themselves.
