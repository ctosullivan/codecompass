# 0031. `Depth` retired; enrichment is usage-driven, not a per-vendor toggle

## Status

Accepted

## Context

`decisions/0001` made depth a per-vendor field so that most dependencies
stay cheap (`surface`) while a human manually escalates the few that
justify AI-generated depth (`full`, via `promote` — `decisions/0018`).
That design assumes a human can and will correctly judge, per vendor,
whether it's worth the cost — a judgment call the user has asked to
remove from the workflow entirely in this rework: enrichment should
target "attributes actually used in the project," determined by a new
static usage-detection layer (Phase 12), not a manually maintained flag.

## Decision

The `Depth` enum and `VendorConfig.depth` field are removed. There is no
replacement config field — a vendor's eligibility for AI enrichment is
computed at sync time from the SQLite graph's `uses_edges` table (does at
least one project source file reference this vendor / one of its
symbols), not stored as persistent per-vendor configuration.

## Alternatives considered

- **Keep `Depth` as a read-only override a user can still force (e.g.
  pin a vendor to always/never enrich regardless of detected usage).**
  Rejected for this rework — no concrete need for it has surfaced yet,
  and adding an override surface speculatively contradicts this project's
  general practice of not building for hypothetical future requirements.
  If real usage later shows detection false negatives/positives are
  common enough to need a manual pin, that's a future, evidence-driven
  addition, not part of this decision.
- **Rename `Depth` to something coarser (e.g. `tracked`/`enriched`) but
  keep it as stored, human-editable state.** Rejected — storing enrichment
  status in `vendor.toml` would drift from the SQLite graph's own
  `uses_edges`-derived truth the moment usage changes without a re-sync,
  reintroducing exactly the kind of staleness this rework's graph is
  meant to eliminate.

## Consequences

- `core.py`: `Depth` enum deleted; `VendorConfig` narrows to `name` +
  `ecosystem`.
- `config.py`: silently tolerates and ignores a legacy `depth = "..."`
  line in an existing `vendor.toml` on read, rather than erroring — no
  one-time migration command is provided.
- `claude_md.py` drops the `**Depth:**` metadata line; `index.py`'s
  routing table drops the "Depth" column (replaced by an
  enrichment-status column sourced from the graph); `staleness.py` is
  unaffected (it never referenced `Depth`).
- `skill.py`'s per-vendor Skill/`.mdc` generation gates on "≥1 enriched
  symbol" (graph-derived) instead of `depth is FULL` — this is a
  consequence of this decision, formalized further in
  `decisions/0033`.
- `decisions/0001` is superseded by this ADR; it is not edited (append-only).
