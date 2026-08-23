# 0045: Typed relation labels describe, they don't detect

## Status

Accepted.

## Context

Phase 22 already writes a free-text `ai_summary` describing *how* a
mechanically-proven `doc_relations_edges` row relates (Phase 21/29's
mention-detection, gated strictly on candidates the mechanical pass
already found real). Prose alone isn't filterable or groupable — there
was no way to ask "show me every relation where a spec doc explains usage
of a dependency" versus "show me every relation where it configures one"
without re-reading every summary by eye.

The obvious next step — asking the same enrichment call to also emit a
structured label — raises the same question this project has answered
consistently since 9a-9c and `decisions/0031`: is AI allowed to influence
*which* relationships exist, or only to *describe* ones a mechanical pass
already proved real? Phase 21's mechanical-only spec-doc detection and
Phase 22's gating on Phase 21's candidates already drew that line for
detection generally; this phase needed to draw it again specifically for
labeling, since a sufficiently expressive label taxonomy could quietly
turn into a second detection mechanism (e.g. a label like
`"related_to_x"` where `x` is something the mechanical pass never found).

## Decision

`relation_label` is a **closed, five-value enum**:
`documents_configuration_of`, `explains_usage_of`, `contrasts_with`,
`supersedes`, `other`. The model picks exactly one per relationship, in
the same batched forced-tool-use call that already produces `ai_summary`
— no new call, no new cost beyond the marginal token cost of one more
output field per relationship.

Any label the model returns that isn't in this set — a genuinely invented
label despite the tool schema's own `enum` constraint on the field, a
missing field, a malformed value — is silently normalized to `'other'` by
`relation_enrichment._normalize_relation_label`. This never raises, per
this project's established "never raises, degrades to a safe default"
posture (`staleness._parse_version`, `skill_scan._extract_scalar`): an
enrichment run covering dozens of relationships shouldn't fail because
one label came back malformed, and forced tool use is not a hard
guarantee that `enum` is honored — the code must not assume it.

**The set of relationships that get labeled is unchanged from Phase
21/29.** `relation_label` is computed only for candidates
`graph.relation_enrichment_candidates` already returns — rows
`doc_mapping.build_doc_relations_edges`'s mechanical word-boundary match
already proved. The label describes an edge that already exists; it
cannot create one, and nothing in this phase's code path lets a label (or
its absence) add or remove a `doc_relations_edges` row.

The existing free-text `ai_summary` is kept, not replaced — the label is
additive, for filtering/grouping; the summary remains the human-readable
explanation `query relations` already showed, and dropping it would lose
real information Phase 28's excerpt-centering fix specifically improved
the accuracy of.

## Consequences

- `query relations` gains a `relation_label` field (JSON) / "Label"
  column (human table) alongside the existing summary.
- `doc_relation_enrichment` gains a `relation_label TEXT CHECK (...)`
  column, added via `ALTER TABLE ... ADD COLUMN` on an existing database
  (not a drop-and-recreate) — this table holds paid AI spend that must
  survive a migration, unlike `doc_artifacts`, which is fully rewritten
  by the next `rebuild_deterministic` regardless. Pre-existing rows get
  `relation_label = NULL` until their next natural re-enrichment cycle;
  no backfill script, consistent with this project's "let the natural
  refresh cycle handle it" posture used elsewhere (cache invalidation on
  vendor sync/spec-doc change, the existing two-axis staleness model).
- The detection-vs-description boundary held since `decisions/0031` is
  reaffirmed, not reopened, by this phase. A future phase closing the
  still-open gap this boundary leaves (a doc that discusses a vendor
  conceptually without naming it — word-boundary matching can't catch
  that) needs its own ADR arguing the specific gap and the
  false-positive/cost tradeoff of letting AI participate in detection —
  not a quiet extension of the label taxonomy here.

## Alternatives considered

- **Free-form label text instead of a closed enum.** Rejected: defeats
  the purpose (filtering/grouping needs a small, known vocabulary) and
  reopens exactly the "could become detection" risk this decision exists
  to avoid — an unconstrained label is one prompt-engineering nudge away
  from smuggling in a new candidate relation kind.
- **Reject/drop a relationship whose label comes back malformed**, rather
  than falling back to `'other'`. Rejected: would make one bad label
  destroy an already-mechanically-proven, already-paid-for relationship's
  summary too, coupling two independent pieces of output for no benefit
  — the summary can still be perfectly good even when the label parse
  fails.
