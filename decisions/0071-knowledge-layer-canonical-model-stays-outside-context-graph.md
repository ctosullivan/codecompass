# 0071. The Phase 81 knowledge layer's canonical model is
`planning/knowledge/`, not a `context-graph.db` schema extension

## Status

Accepted (Phase 81, 2026-10-07, direct user request).

## Context

Phase 81 introduces a persistent, bidirectional intermediate knowledge
layer: a human/tool-editable Markdown projection over CodeCompass's own
structured project knowledge (concepts, invariants, behaviours, open
questions), reconciled back against evidence before anything becomes
canonical. Two architectures were considered for where that canonical
knowledge actually lives:

1. Extend `context-graph.db`'s own schema with new tables for concepts,
   invariants, and behaviours, alongside its existing mechanical-fact
   tables.
2. Reuse `planning/knowledge/<slug>/`'s existing Observation/Evidence/
   Claim/Derivation/Decision/Requirement model (Phase 54c, extended by
   Phase 79), citing `context-graph.db` rows as evidence sources only.

`context-graph.db`'s own boundary has been reaffirmed, not reopened, at
every prior opportunity: it is a deterministically rebuilt store of
**mechanically-detected structural facts only** (`decisions/0024`,
`0025`, `0031`, `0037`, `0045`), and `decisions/0051` states this
explicitly: *"An agent's suggested relationship is an observation with
provenance. It is captured in `planning/context-gaps/` and nowhere
else... no agent, or any AI call, [gets] influence over the contents of
the graph."* Storing human/AI-authored semantic knowledge (a concept, an
invariant, a declared intent) as graph facts would break this boundary —
the graph would stop being purely mechanical the moment it held content
whose truth depends on review and evidence rather than on what `sync`
observed directly on disk.

`planning/knowledge/`'s existing model, by contrast, already has exactly
the properties this layer needs: a real status lifecycle distinguishing
fact (`Claim`) from intent (`Decision`), real evidence-citation
discipline, a file-based, Git-native identity already proven under three
rounds of fail-closed validator hardening (Phases 79/80), and a status
enum (`proposed`/`supported`/`contradicted`/`superseded`/`verified`)
that, on inspection, already expresses every epistemic state the new
reconciliation loop needs without any extension (see `decisions/0072`).

## Decision

The canonical knowledge model for Phase 81 is `planning/knowledge/`'s
existing six-record-kind corpus, reused unchanged.
`context-graph.db` remains exactly what it is today — a deterministic
store of mechanically-detected structural fact — and becomes one of
several **evidence sources** the knowledge layer's Evidence records cite
(by path and content hash, a capability that already exists), never a
container for the knowledge itself. No new `context-graph.db` table is
introduced for concepts, invariants, or behaviours.

## Consequences

- CodeCompass's two stores keep a clean, principled separation:
  `context-graph.db` answers "what does `sync` mechanically observe
  about this project right now," while `planning/knowledge/` answers
  "what does the project know, intend, require, and why, as reviewed and
  reconciled over time."
- The new bidirectional Markdown↔record reconciliation loop (Phase 81's
  own genuinely new mechanism) operates entirely within the existing,
  already-hardened `planning/knowledge/` validation path
  (`scripts/check_knowledge_base.py`), rather than requiring new
  graph-rebuild-safe migration/enrichment-table machinery.
- A future contributor proposing to fold semantic knowledge into
  `context-graph.db` — for ergonomic reasons, e.g. "query it the same
  way as everything else" — should read this ADR and `decisions/0051`
  first; the boundary is deliberate, not an oversight.
