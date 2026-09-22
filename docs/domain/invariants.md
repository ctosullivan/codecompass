---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Invariants

Cross-cutting rules pulled up from individual concept pages' own
"Invariants" sections — collected here because they hold *across*
multiple concepts, not because they're more important than a
concept-local rule. Each still cites the concept page(s) it came from;
this page is a convenience index, not a separate source of truth.

See [`concepts/invariant.md`](concepts/invariant.md) for why "invariant"
itself is not a formal record kind, and for the three distinct senses
this word carries in the repository (of which this file is sense 3).

## The evidentiary model (Observation → Evidence → Claim → Decision → Requirement)

- **A support/contradict judgment is recorded only on a Claim, never on
  the Evidence it cites.** Evidence is neutral by design — the same
  Evidence record can be cited as `supporting_evidence` on one Claim and
  `contradicting_evidence` on a competing Claim without being rewritten
  either way. *(`concepts/evidence.md`, `concepts/claim.md`)*
- **A Claim's `supersedes` field only ever names another Claim, never a
  Decision.** A Decision's `supersedes` field only ever names another
  Decision, never a Claim. **A Decision can never make a Claim wrong or
  supersede it** — it can only agree with, or deliberately diverge from,
  an unchanged, still-valid Claim. Mechanically enforced by
  `scripts/check_knowledge_base.py`. *(`concepts/claim.md`,
  `concepts/decision.md`)*
- **A factual correction to observed behaviour is always a new Claim,
  never a Decision.** Only an independent re-derivation or an explicit
  user Decision moves a Claim past `supported` into `verified` — never
  the agent that first wrote it. *(`concepts/claim.md`)*
- **Contradicting evidence, once recorded, is retained beside supporting
  evidence** — never silently discarded, even once a Claim is marked
  `supported`. *(`concepts/claim.md`)*
- **A Decision is the one record kind only a human/project-owner
  authors or explicitly ratifies.** Per Phase 63D's own 2026-09-20
  amendment: **no agent or lead may stand in for the actual user/domain
  owner on a genuine domain/product ambiguity, from Phase 63D onward** —
  narrower than Phase 54c's own original allowance, which had permitted
  exactly that stand-in during CodeCompass's own dogfooding.
  *(`concepts/decision.md`)*
- **A Requirement always cites exactly one Decision** — never
  free-floating, unauthorised implementation guidance — and its own
  `status` reaches `verified` only after real, direct post-implementation
  revalidation, never merely because the code was written.
  *(`concepts/requirement.md`)*
- **No record kind in this model carries a numeric confidence score.**
  Every "how sure are we" question is answered by a closed `status`
  enum, one per record kind, never a float or percentage.
  *(`concepts/claim.md`, `concepts/provenance.md`)*

## Provenance (realized differently per mechanism, never unified)

- **Every Phase 54c record kind's own `performed_by`/`derived_by`/
  `decided_by`-style field uses the identical field shape whether the
  actor was an agent dispatch or a human** — provenance-by-actor-type is
  a value, never a different schema. *(`concepts/observation.md`,
  `concepts/provenance.md`)*
- **No provenance field anywhere in this model is, or has ever been
  proposed as, a numeric confidence score** — provenance answers "from
  what," never "how sure." *(`concepts/provenance.md`)*

## The context graph (`context-graph.db`)

- **`context-graph.db` is never written to by an agent's subjective
  interpretation** — only by deterministic detection
  (`rebuild_deterministic`) or the narrowly-scoped enrichment writers.
  This holds regardless of which sense of "context" a given piece of
  work means. *(`concepts/context.md`)*
- **An agent-suggested relationship is not an edge, ever, until
  promoted** through a separately-gated ADR process. It is captured only
  in `planning/context-gaps/`, never staged in any graph table.
  *(`concepts/relationship-edge.md`)*
- **A relationship's existence (an edge row) and commentary about that
  relationship (an enrichment row) are always separate tables with
  separate lifecycles.** No edge table carries free-text AI commentary
  inline; no enrichment table asserts a relationship exists on its own —
  it only ever elaborates on one the edge tables already proved.
  *(`concepts/relationship-edge.md`)*
- **Every edge table foreign-keys to its node tables with `ON DELETE
  CASCADE`** — `rebuild_deterministic` never needs to manually clear
  dependent tables in a specific order. *(`concepts/relationship-edge.md`)*

## Context packets and digests (never generated from each other)

- **A context packet is only ever produced from records reachable from
  a `design.md` in `status: APPROVED`** — never from a `proposed` or
  still-under-review design. It never itself writes to
  `context-graph.db`, `src/`, or any record's own `status` field.
  *(`concepts/context-packet.md`)*
- **A digest is regenerated on every `sync`, for every tracked vendor,
  unconditionally** — there is no "stale digest, skip regeneration"
  path. Its deterministic portion never depends on whether AI enrichment
  has ever run for that vendor. *(`concepts/digest.md`)*
- **Neither a digest nor a context packet is a generalisation of the
  other** — different producer, trigger, storage location, gate, and
  audience (see the comparison table on
  [`concepts/digest.md`](concepts/digest.md)).

## Adapters, vendors, and ecosystems

- **Every `VendorConfig.ecosystem` value maps to exactly one adapter
  class** via `get_adapter`'s closed, total dispatch table — never a
  fallback or "no adapter found" case for any of the four `Ecosystem`
  members. *(`concepts/vendor.md`, `concepts/ecosystem.md`,
  `concepts/adapter.md`)*
- **A `VendorConfig` carries no path information at all** — it names
  *what* is tracked, never *where* on disk it resolves to; path
  resolution is entirely the adapter's own job, performed fresh on every
  call (real consequence: one `project_root` can legitimately contain
  source for multiple distinct vendors, in the monorepo case).
  *(`concepts/vendor.md`, `concepts/adapter.md`)*
- **An external-process adapter's Python-side class stays a thin
  dispatcher** — real ecosystem-specific logic never lives twice (once
  in the external process, once reimplemented in `src/codecompass/`).
  *(`concepts/adapter.md`)*
- **A protocol response carries either a `result` key or an `error`
  key, never both, never neither**; an `analyze_project` result section
  is present only if the adapter declared the matching capability at
  `initialize`. *(`concepts/protocol.md`, `concepts/capability.md`)*
