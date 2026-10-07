# 0075. Phase 81's knowledge-reconciliation implementation is corrected a
third time: candidate-presence validation applies before all
candidate-type branches; grounded-document concurrency identity includes
cited-record membership

## Status

Accepted (Phase 81 third corrective pass, 2026-10-08, direct user
request, following further post-completion review of the second
corrective pass `decisions/0074` itself shipped). **Refines, rather than
reverses, `decisions/0071`/`0072`/`0073`/`0074`** — the architecture those
four ADRs establish is unchanged and remains approved. This ADR is an
implementation correction already implied by `decisions/0074`'s own
stale-manifest and apply-time-concurrency principles, not a new
architectural decision: both defects below are the same invariant
(detection/presence must be re-checked at apply time; concurrency
identity must cover everything a reconciled edit actually depends on)
applied more completely than `decisions/0074` itself managed to apply it.

## Context

A further review of `decisions/0074`'s own work found two remaining
defects, both narrow gaps in applying principles `decisions/0074` had
already established elsewhere in the same codebase:

1. `decisions/0074` point 8 established that an ordinary candidate's
   disappearance before apply must fail closed unless a genuinely
   matching canonical record exists — but `_apply_candidate_addition`
   checked this only for the fallback Claim path. An explicit, *valid*
   `Type: Requirement` candidate branched into `_apply_requirement_proposal`
   before this check ever ran, so a Requirement could still be created
   from a manifest whose own live candidate text had already been deleted
   or materially changed.
2. `decisions/0074` point 2 established that a grounded document's
   apply-time concurrency check must cover every cited record's own
   content hash, not just the region's own text — but neither detection
   nor apply ever compared the cited-id *set itself* against its own
   baseline. Removing (or adding) a cited id from a grounding marker,
   with the region's own prose and every still-cited record's own content
   both unchanged, was silently classified `"noop"` at detection and
   passed silently at apply — the grounding *relationship* had changed
   even though no byte of tracked content had.

## Decision

### 1. Candidate-presence validation before all candidate-type branches

`_apply_candidate_addition` previously derived a candidate's own
intended Claim statement in each branch separately (Requirement,
Intent, plain), with the live-text presence/race check applied only to
the Claim-shaped fallback. A new `_CandidateIdentity` value (kind,
statement, decision) is now derived exactly once per candidate —
via `_derive_candidate_identity`, which reuses a new, side-effect-free
`_requirement_proposal_validity` helper (factored out of
`_apply_requirement_proposal` itself) — **before** the live-text presence
check runs. The presence check, and its own "search for an already-
applied equivalent, else fail closed" fallback, now always run first,
using that one identity's own `kind`/`decision` for the type-aware dedup
lookup. Only once text presence is confirmed does control proceed to the
real, type-specific apply (`_apply_requirement_proposal` for a
Requirement, the ordinary Claim-creation path otherwise) — reusing the
identical identity already derived, never re-deriving it.

### 2. Grounded-region concurrency identity includes cited-id membership

`detect_grounded_region_changes` now additionally computes
`membership_changed = sorted(current cited ids) != sorted(baseline cited
ids)` — explicitly order-insensitive (reordering `CL-A, CL-B` to `CL-B,
CL-A` is never a change) but add/remove-sensitive. A changed membership
is treated as a `structural_changed` signal exactly like a changed
region body (`region_changed`), producing `case = "doc_candidate"` —
never silently `"noop"` — through the same existing review/apply flow a
prose edit already uses (a reviewer still decides `semantic_change`
true/false, same honesty as before). Per-id content-drift detection
(`claims_changed`) is now computed only over ids cited in *both* the
baseline and the live marker, so a newly-added or just-removed id is
never double-counted as "its own content changed" too.

`_apply_doc_region_edit` gained a matching apply-time check: immediately
after the region-text-hash check and before the per-id content-hash
check, it compares `sorted(live cited_ids)` against
`sorted(item["cited_ids"])` (the manifest's own detection-time snapshot)
and fails closed — no record created, no baseline advanced — on any
mismatch, with the same order-insensitive policy as detection.

### 3. Stable region identity is unaffected

`region:<id>` parsing, `_region_state_key`, `_check_no_duplicate_region_ids`,
and `_locate_live_region` are untouched by this ADR. Region identity (what
the region *is*) and grounding membership (what canonical knowledge
*currently grounds* it) remain distinct concepts, exactly as before —
insertion above an existing region, moving a region, and duplicate-id
rejection all continue to work exactly as `decisions/0074` point 10
established.

## Consequences

- No canonical schema changed. No new persisted field, no new manifest
  item kind. The `doc_region_edit` item's existing `cited_ids` field
  (already present since `decisions/0074` point 2) is reused as-is for
  the membership check — no new field was needed.
- `_apply_requirement_proposal`'s own body is now three lines shorter
  (its validity check moved to the new, independently-testable
  `_requirement_proposal_validity`), with identical external behaviour
  for every case that already worked correctly.
- 8 new tests added to `tests/test_knowledge_intermediate.py` (73 total):
  a deleted valid Requirement candidate with no match fails closed and
  creates nothing; a deleted valid Requirement candidate with a genuine
  already-applied equivalent is a safe no-op; the existing ordinary-Claim
  disappearance behaviour is unaffected; removing a cited id is not
  `noop` and stays pending across repeated detection; adding a cited id
  is not `noop`; reordering cited ids only is `noop` (the documented
  order-insensitive policy); a membership change between detection and
  apply fails the apply closed with zero stray records; a mere reorder
  between detection and apply does not block the apply.
