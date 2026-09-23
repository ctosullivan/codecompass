# Architecture (proposed, current-state-only)

**Status: shadow proposal, Phase 64 (Cluster B).** Not yet applied to
`architecture/`. Comparing this against the current `architecture/overview.md`
and deciding retain/rewrite/consolidate/split/replace/remove per document is
Phase 65's job, not this one's.

This set describes **how CodeCompass is structured today**, derived directly
from `src/codecompass/` and `tests/` — not from `architecture/overview.md`,
which was deliberately not read as a starting structure (see
`planning/phase-64-blank-slate-documentation-reconstruction.md` §0). No
historical "Phase N added..." narration is included; where a design choice
is non-obvious, the governing ADR is cited so a reader can go find the
history themselves rather than having it re-narrated here.

**Domain terminology exception**: this set does not redefine what a
"vendor," "adapter," "ecosystem," "digest," or "context" means — it cites
`docs/domain/concepts/*.md` for meaning and focuses on *how the code
implements* that meaning. Read the linked concept page first if a term is
unfamiliar.

## Contents

1. [`module-map.md`](module-map.md) — the module inventory: what each file
   under `src/codecompass/` is responsible for, and how responsibility is
   layered (core data model → detection/generation → orchestration → CLI).
2. [`core-data-model.md`](core-data-model.md) — the small set of
   ecosystem-agnostic dataclasses everything else is built from
   (`VendorConfig`, `Ecosystem`, `DepNode`, `VendorDigest`, `Symbol`).
3. [`adapter-interface.md`](adapter-interface.md) — the `EcosystemAdapter`
   contract, the four concrete adapters, and the two coexisting
   implementation strategies (in-process, external-process). For the
   external-process wire protocol itself, see
   `../protocol-adapter/wire-protocol.md`.
4. [`context-graph-schema.md`](context-graph-schema.md) — every table in
   `context-graph.db` (`src/codecompass/graph.py`), what populates it, and
   what survives a rebuild versus what doesn't.
5. [`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md) —
   what actually happens on a bare `codecompass` invocation and on
   `codecompass sync`: Phase A (free, deterministic) and Phase B (AI
   enrichment, cost-gated), traced through the real call graph.

## What this set deliberately does not cover

- CLI flags/usage and generated-artifact file formats from the user's
  point of view — that's Cluster A's `docs/` proposal.
- The external adapter wire protocol's own message-by-message shape and
  how to build a new external adapter — that's this same cluster's
  `../protocol-adapter/` set (kept separate from architecture because it
  has a different audience: an adapter *implementer*, not someone reading
  CodeCompass's own internals).
- Domain-concept definitions — `../domain/` (Cluster C, reorganizing
  `docs/domain/` itself, not re-derived here).
