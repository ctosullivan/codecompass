# 0074. Phase 81's knowledge-reconciliation implementation is corrected a
second time: baseline-advancement discipline, apply-time concurrency for
grounded documents, presentation/semantic doc edits, post-apply
grounding, stable region identity, type-aware dedup

## Status

Accepted (Phase 81 second corrective pass, 2026-10-07, direct user
request, following further post-completion review of the Phase 81
corrective pass `decisions/0073` itself shipped). **Refines, rather than
reverses, `decisions/0071`/`0072`/`0073`** — the architecture those three
ADRs establish is unchanged and remains approved. This ADR corrects
fourteen further implementation defects and gaps, all within the
already-approved design.

## Context

`decisions/0073`'s own corrective pass shipped, was dogfooded, and had
started its own closeout sequence when a usage-limit interruption left
Phase 81 `reopened` rather than `done`. A further, more detailed review
of that corrective pass itself — not of the original Phase 81 design —
found fourteen more real defects, mostly in the grounded-document
reconciliation path `decisions/0073` point 3 introduced, plus a few in
the external-candidate path points 6/7 touched. None required reopening
the architecture; all are behavioural corrections within it.

## Decision

### 1. Detection never acknowledges drift by observing it

`doc-select-candidates` previously advanced both
`.grounding-state.toml` and `.doc-chunk-state.toml` immediately after
every detection run, for both its "nothing to review" and "manifest
written" branches — meaning a `doc_candidate` that was detected but
never actually applied, or a `claims_changed` staleness flag that no one
had looked at, would vanish from the next detection run regardless.
Detection is observation, not acknowledgement.

The corrected rule: a baseline advances only for (a) a region seen for
the very first time (`"new"` — there is no prior state to lose by
establishing one), (b) a `doc_candidate` that is actually applied
(`_apply_doc_region_edit`, on success, for both the presentation-only and
semantic branches), or (c) a `claims_changed` finding explicitly
dismissed via the new `acknowledge_stale_grounded_region` function /
`codecompass knowledge doc-acknowledge-stale` command. The separate
advisory ungrounded-chunk tracker now only ever advances via the new,
explicit `codecompass knowledge doc-acknowledge-chunks` command — never
automatically. A `concurrent_conflict` is never auto-resolved at all; it
keeps being reported until the underlying facts genuinely change again,
exactly like the existing intermediate-doc anchor conflict case.
`detect_grounded_region_changes` itself remains entirely read-only.

### 2. Apply-time concurrency checks for grounded-document Claims

A `doc_region_edit` manifest item previously only recorded the grounded
region's own `base_region_hash`, re-checked at apply time. The cited
records themselves were never re-checked — a grounding Claim could change
between detection and apply with no protection at all. Each item now
also records `cited_hashes_at_detection` (parallel to `cited_ids`), and
`_apply_doc_region_edit` recomputes and compares every cited record's
current content hash immediately before writing, alongside the existing
region-text check. Either mismatching fails the apply closed with no
record created, exactly as the existing intermediate-doc anchor path
already does for its own analogous case.

### 3. Presentation-only vs. semantic grounded-document edits

Every accepted `doc_region_edit` previously created a new Claim
unconditionally — a pure wording/typo fix had no way to be acknowledged
without fabricating a redundant semantic record. Each item now carries an
explicit `semantic_change` field (default `false`, mirroring the existing
`anchor_edit` convention), set by the reviewer before accepting. `false`
acknowledges the edit as presentation-only: canonical knowledge is
untouched, no Claim is created, and only the region's own baseline
advances (the trigger required by point 1 above). `true` proceeds exactly
as before, creating a candidate Claim, never auto-promoted. As with the
intermediate-doc anchor's own `semantic_change`, this is always a
reviewer judgment call — never mechanically proven equivalence.

### 4. Post-apply grounding reconciliation

A semantic grounded-document edit's new Claim previously had no
connection back to the region that produced it — the region stayed
grounded only against the old, now-superseded Claim. `_apply_doc_region_edit`
now rewrites the region's own live marker to additionally cite the new
Claim (`grounded-by: CL-OLD, CL-NEW`), preserving the relationship to
prior knowledge rather than dropping it, and making the new Claim
deterministically discoverable from this region going forward via
`find_grounded_doc_regions`. A presentation-only edit's marker is left
untouched, since no new record was created to cite.

### 5. Corrected inline candidate instructions

The rendered `_CANDIDATE_INSTRUCTIONS` constant still described the
pre-`decisions/0073` rule ("cite an approved Decision id to get a
Requirement"), directly contradicting the real, already-implemented
`Type: Requirement`/`Type: Intent` protocol. Rewritten to state the real
rules explicitly: plain prose stays an unclassified Claim; a Decision id
merely mentioned in prose never creates a Requirement; the exact
`Type: Requirement` / `Decision:` / `Statement:` / `Example:` shape is
required for a Requirement, falling back to a Claim if the cited Decision
isn't real/approved or the example doesn't read as Given/When/Then; the
exact `Type: Intent` shape is required for declared policy/intent.
`docs/codecompass-knowledge-workflow.md` is updated to agree with this
exactly, word for word on the protocol itself.

### 6. Public template updated to the corrected workflow

`codecompass-template`'s `optional-intermediate-knowledge/README.md` and
`worked-example.md` predated every correction in `decisions/0073` and
this ADR. Both are rewritten to document `knowledge doc-select-candidates`,
`doc-acknowledge-stale`/`doc-acknowledge-chunks`, the explicit `Type:`
syntax, candidate consumption/idempotency, the `semantic_change`
distinction and post-apply grounding update for documentation edits,
stable `region:<id>` identity, and apply-time concurrency — committed and
pushed to the real public `ctosullivan/codecompass-template` default
branch (`bd2420d`), verified present via `git fetch`.

### 7. Intent-block control metadata no longer leaks into canonical content

`_apply_candidate_addition`'s `Type: Intent` path previously used the
raw candidate text — including the `"Type: Intent\n"` header line
itself — as the resulting Claim's own `statement`. `_parse_candidate_block`
now also returns the body with that header stripped, threaded through a
new `CandidateFinding.intent_statement` field and a matching
`intent_statement` manifest-item field, used instead of the raw text.
Structured control metadata must never leak into canonical semantic
content — the same principle `decisions/0073` point 6 already applied to
Requirement proposals' own header lines.

### 8. Fail closed when candidate text disappears before apply

`_apply_candidate_addition`'s "candidate text no longer present" branch
previously always reported `ok=True`, conflating two different
situations: the candidate was already reconciled (a matching canonical
record genuinely exists — legitimately a safe no-op), versus the
candidate text was manually deleted or edited after detection with no
matching record anywhere (an apply-time race or a stale manifest, which
must never be reported as success). The branch now only returns success
when a type-aware dedup match (point 9) is actually found; otherwise it
fails closed with an explicit apply-time-race message.

### 9. Type-aware deduplication

`_find_existing_promoted_record` matched purely on statement text,
meaning a pre-existing Claim could silently block an explicit, valid
Requirement proposal with identical wording (or vice versa) from ever
being created. It now takes an explicit `kind` parameter (default
`"claim"`, checked at every call site), plus an optional `decision`
parameter so two Requirements with identical statement text but
different authorising Decisions are never treated as the same
contribution. `_apply_anchor_edit`, `_apply_requirement_proposal`,
`_apply_candidate_addition`, and `_apply_doc_region_edit` all now pass
their own correct `kind` explicitly.

### 10. Stable grounded-region identity

Grounding-baseline identity was purely positional (`"README.md::0"`) —
fragile under any insertion or reordering of grounded regions within a
document. Markers may now carry an optional `region:<id>` token (e.g.
`<!-- codecompass-grounded-by: CL-X region:readme-sync-behaviour -->`);
`parse_grounding_markers` returns a third element exposing it, and
baseline identity prefers it when present (`_region_state_key`), falling
back to the old positional key for an un-migrated marker. Two markers
claiming the same explicit `region:<id>` fail closed
(`DuplicateGroundingRegionIdError`) rather than silently picking one. The
real `README.md`'s own pre-existing marker was migrated to
`region:intermediate-knowledge-layer`, with `.grounding-state.toml`
re-keyed to match (confirmed to re-detect as a clean `noop`, no spurious
drift from the migration itself).

## Consequences

- No canonical schema changed again — every correction above operates
  within the existing record format and the manifest/baseline files
  already introduced by `decisions/0072`/`0073`. Zero new persisted
  canonical fields, still.
- The `doc_region_edit` manifest item gained `region_id`,
  `cited_hashes_at_detection`, and `semantic_change` fields — all
  manifest-only, mirroring the existing `anchor_edit` item shape rather
  than inventing a second convention.
- `knowledge doc-select-candidates` no longer mutates any baseline file
  except to establish one for a genuinely new region; two new commands
  (`doc-acknowledge-stale`, `doc-acknowledge-chunks`) now own the
  explicit-acknowledgement step the old automatic behaviour collapsed
  away.
- 29 new/expanded tests added to `tests/test_knowledge_intermediate.py`
  (now 61 total), covering every correction above directly, including
  insertion/reordering under stable region identity, duplicate
  region-id rejection, detect-without-apply non-acknowledgement for both
  the doc-candidate and claims-changed cases, apply-time concurrency
  conflict on a cited grounding record, presentation-vs-semantic doc-edit
  branching, post-apply grounding discoverability, Intent-header
  stripping, candidate-disappearance fail-closed behaviour, and
  cross-kind dedup independence in both directions.
- `docs/codecompass-knowledge-workflow.md`,
  `planning/phase-81-intermediate-knowledge-layer.md`, and the public
  `codecompass-template` are all updated to describe this corrected
  behaviour as current.
