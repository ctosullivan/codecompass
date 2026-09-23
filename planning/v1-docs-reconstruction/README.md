---
status: PROPOSAL (Phase 64, done 2026-09-23) — a shadow documentation
  proposal, not live documentation. Nothing here has been applied to
  the real `docs/`, `README.md`, `architecture/`, or `ai-docs/`; that
  decision (retain / rewrite / consolidate / split / replace / remove,
  per document) is Phase 65's job (`documentation-lifecycle.md` §4).
---

# CodeCompass documentation reconstruction — shadow proposal

Phase 64's own output (`planning/phase-64-blank-slate-documentation-reconstruction.md`):
a fresh derivation of what CodeCompass's documentation ought to be,
approached as though the current narrative documentation
(`README.md`, `docs/`, `architecture/`) did not exist — **with one
deliberate exception: domain terminology is not re-derived.** Phase
63D's own approved `docs/domain/` corpus is authoritative for what
CodeCompass's concepts mean; this proposal consumes it rather than
guessing at meaning a more careful, evidence-backed, adversarially-
reviewed pass already settled (`decisions/0060`).

**No `src/codecompass/` change. No current-truth doc touched.** This
entire tree is new.

## The six documentation categories

Per `documentation-lifecycle.md` §1.4, organized here as six top-level
directories, produced by three parallel, independently-dispatched
`docs-reconstructor` runs (matching Phase 63D's own successful
three-cluster research pattern):

| Category | Directory | Cluster | Answers |
|---|---|---|---|
| **Domain** | [`domain/`](domain/) | C | What do CodeCompass's own concepts mean? (reorganized from `docs/domain/`, not re-derived) |
| **Architecture** | [`architecture/`](architecture/) | B | How are those concepts implemented? |
| **User** | [`docs/`](docs/) | A | How is CodeCompass used? |
| **Developer** | [`docs/developer/`](docs/developer/) | A | How is CodeCompass extended? |
| **Protocol/adapter** | [`protocol-adapter/`](protocol-adapter/) | B | How do external components integrate? |
| **Development-process** | [`development-process/`](development-process/) | C | How does Scope → Plan → Domain → Design → Implement operate? |

Each category's own `README.md` states its scope, its dispatch's own
grounding method, and the explicit "not yet applied" status.

## Cross-cluster consistency (lead pass, after all three dispatches landed)

Read across all six categories for structural/presentation consistency
— not a re-review of domain meaning (`domain-skeptic`'s own charter,
already discharged at Phase 63D), but a check that the three
independent dispatches agree with each other where their scopes touch:

- **Domain-term usage agrees.** Cluster A (`docs/`), Cluster B
  (`architecture/`, `protocol-adapter/`), and Cluster C's own
  `domain/quick-reference.md` all cite the same `docs/domain/concepts/*.md`
  pages for *adapter*, *vendor*, *digest*, *context packet*, and
  *ecosystem* rather than restating definitions independently — spot-checked
  across all three trees; no disagreement found.
- **The `docs/external-adapters.md` split candidate is genuinely
  cross-cluster, not duplicated work.** Cluster A flagged it from the
  developer-workflow side (overlap with `docs/developer/writing-an-adapter.md`);
  Cluster B flagged it from the protocol-wire side (overlap with
  `protocol-adapter/wire-protocol.md`) — independently, without reading
  each other's output. Both confirmed the file itself is currently
  accurate. Consolidated as one candidate in `concepts-to-retire.md`
  (item 5), not left as two separate, seemingly-contradictory findings.
- **The `ecosystem`/`capabilities` wire-validation gap was independently
  re-confirmed, not duplicated as a new finding.** Cluster B's own
  `protocol-adapter/wire-protocol.md` documents this gap from direct
  code reading (`external_process.py`); it is the same gap Phase 63D's
  own `domain-skeptic` review already routed to `planning/learnings/inbox.md`
  as `L-032` (promoted, Phase 63D closeout, into `planning/ROADMAP.md`'s
  "Future-improvement backlog"). No duplicate learning filed — this is
  corroboration of an already-tracked item, noted here for the record.
- **No overlap gap found**: every one of the six categories has content;
  no dispatch reported being unable to cover its assigned scope, and no
  topic (adapter authoring, wire protocol, CLI usage, config schema,
  process, domain meaning) was left uncovered by all three.
- **No contradiction found** between any two clusters' factual claims
  about the current system (module structure, schema, CLI behaviour) —
  each cluster derived its own area independently from source/tests/real
  command output, and where their scopes bordered each other (e.g.
  Cluster A's `writing-an-adapter.md` and Cluster B's
  `adapter-interface.md`, both describing `EcosystemAdapter`), both
  independently arrived at the same contract description.

## Retirement candidates

Consolidated from all three clusters' own findings:
[`concepts-to-retire.md`](concepts-to-retire.md). Five candidates
(one removal, two trims, one framing note, one split), all
presentation/scope questions — **no live factual error was found in any
cluster's own area**, corroborating rather than contradicting this
repository's own mechanical drift checks (`scripts/check_user_docs.py`).

## What happens next

Phase 65 (architecture + ADR reconciliation) compares this proposal
against the current active documentation, document by document, and
records a retain / rewrite / consolidate / split / replace / remove
decision for each (`documentation-lifecycle.md` §4) — the lead +
`docs-maintainer` then act on it. This phase does not pre-empt any of
those decisions; it is the raw material Phase 65 reconciles.
