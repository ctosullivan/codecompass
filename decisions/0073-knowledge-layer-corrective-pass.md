# 0073. Phase 81's knowledge-reconciliation implementation is corrected:
targeted refresh, idempotent apply, grounded-document reconciliation,
honest provenance

## Status

Accepted (Phase 81 corrective pass, 2026-10-07, direct user request,
following post-completion review of the already-`done` Phase 81).
**Refines, rather than reverses, `decisions/0071`/`0072`** — the
architecture those two ADRs establish (canonical knowledge in
`planning/knowledge/`, `context-graph.db` mechanical-only, zero new
persisted canonical fields, dual-hash concurrency identity) is unchanged
and remains approved. This ADR corrects nine real implementation defects
a post-completion review found, none of which required reopening the
architecture itself.

## Context

Phase 81 shipped, was dogfooded, drift-audited, and independently
completion-audited (PASS WITH NON-BLOCKING OBSERVATIONS,
`planning/retros/_audit-phase-81.md`) the same day it was implemented.
A second, more adversarial post-completion review — outside that first
audit's own scope — found nine real defects, listed with their
corrections below. Each is a behavioural bug or an overly permissive
default, not a flaw in the underlying design the first two ADRs
established.

## Decision

### 1. Targeted refresh, never whole-slug

`apply_automatic_refreshes` called whole-slug `render_slug` the moment
*any* anchor needed a safe refresh (`canonical_changed=true,
projection_edited=false`) — regenerating every block in every file of
the slug, including a block a human/external tool had just edited but
not yet captured in a manifest. `render_slug` reconstructs every block
from scratch; a pending edit sitting in the live file at that moment was
silently overwritten before the next `detect_anchor_changes` call could
ever see it as a `"candidate"`.

**Corrected**: `refresh_safe_anchors` (replacing `apply_automatic_refreshes`
as the real implementation; the old name is kept as a thin alias) takes
anchor classifications that were already computed, then performs
targeted, per-block substitution (`_replace_anchor_blocks`) — only the
named `record_id`s' own blocks are rewritten; every other byte in the
file, including a `"candidate"` or `"concurrent_conflict"` block in the
*same* file, is untouched. The CLI's own `select-candidates` command now
classifies every anchor once, refreshes only the safe-refresh set from
that one classification, and builds the manifest from the same,
unmutated classification — never re-detecting after a destructive
whole-file write.

### 2. Idempotent, consumable reconciliation

Re-applying an already-accepted manifest, or letting an already-applied
candidate's raw text sit untouched in its own candidate region, could
each create a duplicate canonical record.

**Corrected**, with no new ledger file — the manifest and the candidate
region are each their own source of truth for "has this already
happened":

- The manifest's own `state` field becomes real, not merely descriptive:
  `pending` → (Stage 2) `reviewed`/`accepted`/`rejected` → `applied`.
  `apply_manifest` checks `state == "applied"` first and skips
  immediately, then — on a genuinely new success — rewrites the whole
  manifest in place (`_serialize_manifest`, a general read-modify-write
  serializer this ADR also introduces) recording `state = "applied"`,
  `applied_record_id`, and `applied_at`.
  A different manifest proposing the same content is still caught by
  `_find_existing_promoted_record`, a content-addressed dedup check
  scanning existing records by exact `statement` match (and, for an
  anchor edit, by `depends_on` too) — reusing the canonical records
  themselves rather than a parallel ledger.
- A candidate-region contribution, once promoted, has its own raw text
  removed from the live candidate region (`_consume_candidate_text`) —
  the record is now the one place that content's provenance lives; a
  later `select-candidates` run naturally no longer finds it.
- An anchor edit, once applied (either branch — presentation-only or
  promoted to a new competing Claim), has its own original block
  re-rendered in place (`_refresh_single_anchor_after_apply`, reusing the
  same targeted substitution point 1 introduces) so its own
  `base_projection_hash` is brought back in sync with what is now live,
  preventing the same edit from being rediscovered as new.
- **Documented, deterministic choice for identical-text duplicates**: two
  candidate blocks with byte-identical text (after trimming) are treated
  as the *same* contribution. Applying one consumes both occurrences and
  creates exactly one record; this is a documented design choice, not an
  accident of the dedup mechanism.

### 3. Grounded project-document regions now participate in real reconciliation

`find_grounded_doc_regions` could *identify* that a README/CONTRIBUTING
region cites a Claim, but a factual edit to that region never became a
reconciliation candidate — the bidirectional flow §9.2 describes was
only ever built in one direction.

**Corrected**: a new baseline file, `.grounding-state.toml` (project-wide,
under `planning/knowledge/`), tracks each grounded region's own content
hash plus its cited records' own content hashes. `detect_grounded_region_changes`
classifies every region into `noop`/`doc_candidate` (the region's own
prose changed, its Claims didn't)/`claims_changed` (the reverse)/
`concurrent_conflict` (both) — the same four-case shape §1.5 already
established for intermediate-doc anchors, applied to docs. A
`doc_candidate` is written into the *owning slug's own* reconciliation
manifest (`write_doc_candidates_to_manifests`, a new `doc_region_edit`
item kind) and flows through the exact same `apply_manifest` machinery
— no second, parallel apply path. `claims_changed` is surfaced
read-only ("potentially stale, worth a documentation review"); a
`concurrent_conflict` is reported and neither side is touched, exactly
like an intermediate-doc concurrent conflict.

### 4. Honest, real advisory grounding coverage

The original `knowledge status` grounding report only showed a static
region count and which cited records were `contradicted` — never
"changed" anything, despite the plan's own §9.6 calling for "changed
grounded regions" and "changed ungrounded regions needing review."

**Corrected**: `detect_doc_chunk_changes` reuses `doc_chunking.chunk_markdown`
directly (the same heading-based chunker `context-graph.db`'s own
`doc_chunks` table is built from — reused, not reimplemented) against a
second persisted baseline (`.doc-chunk-state.toml`), classifying every
changed chunk as overlapping an explicit grounding marker or not.
`knowledge status` now reports real counts for both, plus the detail
list. Still purely advisory: no canonical mutation, ever, from this
path.

### 5. Presentation override can no longer be the only visible representation of meaning

`presentation_only` was already correctly never written onto the
canonical record — but a rendered block showing cached wording gave an
agent/dev-context consumer no way to see the record's own actual
canonical statement at all.

**Corrected**: when a block is rendered using a presentation-cache
override, the record's own canonical statement is additionally embedded
as a machine-facing HTML comment
(`<!-- codecompass-canonical-statement: ... -->`) — invisible to an
ordinary rendered-Markdown reader, present in the raw text any
agent/dev-context consumer actually reads (`extract_canonical_statement`
reads it back out). `docs/codecompass-knowledge-workflow.md` now states
explicitly that `presentation_only` is a reviewer classification, never
mechanically proven semantic equivalence.

### 6. Requirement proposals require explicit, structured intent

Any candidate-region text merely *mentioning* an approved `DEC-*` id
anywhere in its own prose was treated as a Requirement proposal, and a
placeholder Given/When/Then ("to be refined during review") was
auto-generated as if that were a complete acceptance example.

**Corrected**: a Requirement is only ever proposed from an explicit,
structured block whose first line is exactly `Type: Requirement`,
followed by `Decision:`/`Statement:`/`Example:` lines
(`_parse_candidate_block`). `_apply_requirement_proposal` additionally
requires the cited Decision to resolve to a real, `approved` record and
the Example to structurally contain the words "given", "when", and
"then" (a deliberately minimal, non-semantic check) — an incomplete or
merely-implicit proposal is preserved as an ordinary Claim, using its own
`Statement:` text where present, never silently dropped and never
completed with a fabricated example.

### 7. External candidates are unclassified factual hypotheses by default

Every externally-sourced candidate Claim — whether from a candidate
region or a promoted semantic edit — was unconditionally written with
`basis: proposed_policy`, collapsing "the system currently does X, not
yet checked" and "the system should do X" into the same, intent-implying
classification.

**Corrected**: `basis` is now omitted by default on a new external
candidate — an honestly unclassified factual hypothesis — and
`derive_provenance_label` gains a new rendering-time-only label,
`UNCLASSIFIED`, for exactly this case (never persisted, same as every
other provenance label this phase introduced). `basis: proposed_policy`
is set only when Stage 2 review explicitly says so for a promoted
semantic edit (`proposed_basis` manifest field), or when a candidate-
region block opts in explicitly with a `Type: Intent` first line
(`CandidateFinding.declared_intent`). Classification now always comes
from an explicit act, never merely from being external.

### 8. Provenance derivation walks the real Evidence→Observation link

`derive_provenance_label`'s `basis: directly_stated` branch used
`Evidence.evidence_kind` (`source`/`test`/`behavioural`) as a proxy for
"this evidence traces to a real Observation." The real schema
(`docs/domain/concepts/evidence.md`) already has the actual link: "One
Evidence record cites one or more Observations via its own
`observations:` field, or cites source/doc/test directly... when no
discrete Observation exists to point at" — so a direct-source Evidence
with `evidence_kind: source` and no Observation at all was being
mislabelled `OBSERVED`.

**Corrected**: the function now resolves each cited Evidence's own
`observations:` field against real, resolvable `kind: observation`
records. All relevant evidence tracing to a real Observation →
`OBSERVED`; a mixed chain → `MIXED`; a direct citation with no
Observation at all → the existing cautious `DECLARED` fallback, exactly
as the rest of this function already treats ambiguity.

### 9. Template delivery verified against the real public repository

The first completion audit recorded the `codecompass-template` commit
(`a429f04`) as committed locally but not pushed (HTTPS remote, no stored
credentials). This corrective pass re-checked the actual public
`ctosullivan/codecompass-template` repository directly, confirmed the
commit was still genuinely absent there, and pushed it successfully via
the repository's own SSH remote (which does work in this environment,
unlike HTTPS) — the public default branch now contains it, verified by
a fresh `git fetch`. The remote URL was also updated to SSH so this does
not recur.

## Consequences

- No canonical schema changed again — every correction above operates
  entirely within the existing record format and the manifest/baseline
  files this phase already introduced. `decisions/0072`'s own "zero new
  persisted canonical fields" holds exactly as before.
- The manifest file itself is now the durable, mechanically-checkable
  record of what reconciliation has and hasn't done yet — a genuine new
  property this phase's original design did not have, closing a real gap
  rather than adding complexity for its own sake.
- `docs/codecompass-knowledge-workflow.md` and
  `planning/phase-81-intermediate-knowledge-layer.md` are both updated to
  describe this corrected behaviour as current, not aspirational — see
  the corrective-pass note at the top of the plan file for exactly what
  changed and why.
- Expanded regression coverage (`tests/test_knowledge_intermediate.py`)
  now exercises combinations the original suite tested only in
  isolation — a safe refresh alongside a pending edit or a conflict in
  the *same* file, apply-twice and apply-then-detect-again idempotency,
  grounded-document reconciliation in both directions plus its own
  conflict case, and the corrected basis/provenance/Requirement
  semantics directly against real-shaped records.
