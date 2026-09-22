---
status: DRAFT — pending domain-skeptic review and actual-user approval
---

# CodeCompass domain corpus

This directory documents what CodeCompass's own core concepts *mean* —
evidence, observation, claim, adapter, context, and so on — derived from
source, tests, ADRs, plans, retros, and observed behaviour, never from
treating existing prose as authoritative by default. It exists because
several of these terms already had real, evidenced meaning scattered
across the repository, in inconsistent or overlapping ways, before any
one place stated what each one means, where they overlap, and where
they are currently conflated.

Produced by Phase 63D ("Domain reconstruction",
[`decisions/0060`](../../decisions/0060-scope-plan-domain-design-implement-methodology.md)),
the first project-wide application of the
[Scope → Plan → Domain → Design → Implement](../../planning/v1-redefinition/development-methodology.md)
methodology's own Domain stage.

## How this differs from `docs/` and `architecture/`

- **This directory (`docs/domain/`) answers "what does this concept
  mean."** Example: what is an adapter, and how is it different from a
  vendor or an ecosystem.
- **[`architecture/`](../../architecture/) answers "how is it
  implemented."** Example: how `sync.py` wires an adapter into the
  graph — assuming the reader already knows what an adapter *is*.
- **[`docs/`](../) answers "how do I use CodeCompass."** Example: the
  CLI reference, the config schema.

A single physical file may still serve more than one of these
purposes economically — the point of the split is that Phase 64's own
blank-slate documentation reconstruction considers each deliberately,
not that every category needs a dedicated file from day one.

## How to read this

1. **[`glossary.md`](glossary.md)** first — one paragraph per concept,
   cross-linked. The fastest way to see what each term means and how it
   differs from its neighbours.
2. **[`concepts/`](concepts/)** — one full page per concept: definition,
   what it is NOT (explicit disambiguation from its nearest neighbours),
   invariants, a worked example, a counterexample or edge case (or an
   honest "none found yet"), relationships to other concepts, and a
   references block resolving to real evidence.
3. **[`invariants.md`](invariants.md)** — cross-cutting rules pulled up
   from several concept pages at once, where a rule isn't concept-local.
4. **[`examples.md`](examples.md)** — full worked walkthroughs spanning
   several concepts, for the cases where seeing the whole chain matters
   more than any one link in it.
5. **[`open-questions.md`](open-questions.md)** — everything this
   research found genuinely unresolved, why none of it needed
   escalating to the actual user/domain owner, and what would need to
   change for that to be reconsidered.
6. **[`references.md`](references.md)** — the underlying evidence
   trail, grouped by kind of source rather than by concept.

## Provenance

Every claim in this corpus traces back to a real
Observation/Evidence/Claim/Derivation record under
[`planning/knowledge/codecompass-domain/`](../../planning/knowledge/codecompass-domain/)
(Phase 54c's own record model, reused unchanged, generalized here from a
single feature's own knowledge folder to project-wide scope — no new
schema). The Markdown here is the human-readable projection of those
records, not an independent source of truth in its own right — if this
page and a cited record ever disagree, the record is authoritative,
and the page has a bug.

## Status

Every page in this corpus is currently marked
`status: DRAFT — pending domain-skeptic review and actual-user
approval`. `domain-skeptic`'s own independent adversarial review has
run once
([`planning/retros/_domain-skeptic-review-phase-63d.md`](../../planning/retros/_domain-skeptic-review-phase-63d.md))
and found no genuine, unresolved domain/product ambiguity requiring the
actual user's attention. This corpus becomes **approved** once the
actual user/domain owner has reviewed it and its open questions.

## Freshness

This corpus is a point-in-time conclusion, not a fact that stays true
forever. See
[`development-methodology.md`](../../planning/v1-redefinition/development-methodology.md)'s
own "Domain-corpus freshness and reconciliation" section for when and
how it gets reconsidered — reusing existing checkpoints (a per-phase
drift-audit check, retros, and a milestone reconciliation pre-v1; a
per-feature gate post-v1), never a new standing "domain watcher"
process.
