# 0043. Vendor docs become relationship sources: a closed allow-set, plus a self-mention exclusion

## Status

Accepted

## Context

Phase 29 (`planning/phase-29-vendor-docs-as-relationship-sources.md`) was
found via direct user observation during a `/discovery` session testing
Phase 26-28's real output, confirmed against the live code, not assumed.
A vendor's own embedded upstream doc (`doc_artifacts.kind='vendor_doc'`,
Phase 27/`decisions/0041`) was wired into the graph as **passive, indexed
content only**: eligible as a `mentions_artifact` *target* (a spec doc
name-dropping it), but never itself a relationship *source*, and
explicitly excluded from `documents_edges` symbol-mention detection too.
Two concrete gaps, both confirmed against the live code:

1. `doc_mapping.build_documents_edges`'s kind filter was
   `("claude_md", "overview")` — a vendor's own README, arguably the most
   authoritative source for "this doc documents this symbol" (the
   upstream authors documenting their own API), never produced a
   `documents_edges` row.
2. `doc_mapping.build_doc_relations_edges` only ever scanned spec docs
   outward (`decisions/0037`'s spec-doc-outward-only design, reaffirmed
   by `decisions/0041`'s "It is never a relation source" — see
   **Consequences** below for how this ADR supersedes that specific
   claim). A vendor doc mentioning another tracked vendor, a Skill, or
   another vendor doc produced nothing.

`build_documents_edges`'s fix was mechanical — `vendor_doc` rows already
carry `vendor_name` (Phase 27), so widening the kind filter was the whole
change. `build_doc_relations_edges` required two real decisions.

## Decision

**`build_doc_relations_edges` now accepts a closed allow-set of source
kinds, `{"spec_doc", "vendor_doc"}` (`_DOC_RELATION_SOURCE_KINDS`), not
"any kind not otherwise excluded."** Its first parameter is renamed
`spec_doc_rows` → `source_doc_rows` to reflect the widened contract, and
`sync.rebuild_project_graph`'s call site passes `spec_doc_rows +
vendor_upstream_doc_rows`.

Considered making the function scan *every* doc-artifact kind as a
potential source, now that it's already generalized beyond spec docs
alone. Rejected: a codecompass-*generated* artifact (`claude_md`,
`overview`, `skill`, `cursor_mdc`, `slash_command`) mentioning a vendor by
name is structural — codecompass's own templates always name-drop the
vendor they were generated for — not signal. Scanning those as sources
would produce edges describing codecompass talking about itself, the same
noise-not-signal reasoning behind the self-mention exclusion below, but at
the level of "should this kind of document even be eligible" rather than
"should this one self-referential edge be suppressed." An explicit,
closed set means adding a new source kind later is a deliberate, visible
one-line change, not an accidental side effect of some other doc kind's
origin changing.

**Self-mention exclusion: a `vendor_doc` source row never produces a
`mentions_dependency` edge targeting its own vendor.** When the source row
is a `vendor_doc` belonging to vendor `V`, `V`'s own name is skipped when
matching against tracked vendor names. A package's own README mentioning
its own name is guaranteed, universal, and adds no signal — unlike a spec
doc mentioning a vendor, or a vendor doc mentioning a *different* tracked
vendor, both of which are real evidence of a relationship.

This is narrower than a generic "never emit a self-referencing edge"
rule in two ways, both deliberate:

- **Only `mentions_dependency`, not `mentions_artifact`.** A vendor doc's
  own `name` field is a synthetic `f"{vendor} {filename}"` string (e.g.
  `"anthropic README.md"`), not something a document's own prose would
  organically contain about itself — already extremely unlikely to
  self-match, and not worth a special case without evidence it happens.
- **Only by vendor identity, not by path comparison.** A vendor doc's own
  vendor is known directly from `DocArtifactRow.vendor_name` — comparing
  that to the target vendor name being considered is a cheap, exact check
  with no edge cases (no path normalization, no worrying about a vendor
  with multiple doc files). Solves exactly the one guaranteed-noise case
  found, not a broader speculative one.

The exclusion does not apply to `spec_doc` sources at all — a spec doc has
no `vendor_name` of its own to compare against, so the condition
(`row.kind == "vendor_doc" and row.vendor_name == vendor_name`) is simply
never true for one.

## Alternatives considered

- **Scan every doc-artifact kind as a source** (drop the allow-set
  entirely). Rejected — see Decision above: codecompass-generated
  artifacts would create self-referential noise edges.
- **A generic "never emit a self-referencing edge" rule** covering both
  `mentions_dependency` and `mentions_artifact` via some shared
  identity/path check. Rejected as broader than the evidence supports —
  the `mentions_artifact` case isn't a real problem (see Decision above),
  and inventing a path-based identity check for a case that doesn't occur
  would be speculative complexity with no observed benefit.
- **Suppress the self-mention edge at read time** (in `graph.py`'s query
  layer or `cli.py`'s `query relations` rendering) rather than at
  detection time. Rejected: `doc_relations_edges` is a purely mechanical,
  fully-rebuilt-every-sync table (`decisions/0025`) — "this edge shouldn't
  exist" is a detection-time judgment about what counts as signal, not a
  presentation-time filter. Keeping the exclusion in
  `build_doc_relations_edges` means every reader (CLI, future `check`
  sections, direct SQL) sees a graph that's already correct, rather than
  each needing to know to re-apply the same filter.

## Consequences

- **Supersedes `decisions/0041`'s "It is never a relation source — spec
  docs are the only source `build_doc_relations_edges` ever scans from"**
  claim specifically. `decisions/0041`'s actual subject — the root-level,
  fixed-filename-set scope of *which* vendor files get a `doc_artifacts`
  row at all — is unchanged by this phase; only its downstream claim about
  a vendor doc's role in `doc_relations_edges` is reversed.
  `graph.vendor_docs_without_relations` (which checks
  `target_doc_artifact_id`) remains correct regardless: a vendor doc's
  role as a *target* is unaffected by it also now being eligible as a
  *source*.
- `relation_enrichment.py` needed no change: `graph.
  relation_enrichment_candidates` already operates generically over
  whatever `doc_relations_edges` contains, with no assumption about the
  source row's `kind` — a vendor-doc-sourced relationship becomes an
  enrichment candidate automatically, same usage-proven gating as every
  other relationship.
- A future new source kind (e.g. extending `skill_mentions_edges`-style
  scanning to some other doc kind) must add itself explicitly to
  `_DOC_RELATION_SOURCE_KINDS` — the allow-set does not grow implicitly.
