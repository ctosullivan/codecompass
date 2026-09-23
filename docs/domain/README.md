---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
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
   differs from its neighbours. **[`quick-reference.md`](quick-reference.md)**
   compresses it one step further into a one-line-per-term table, quoted
   directly from the glossary — reach for it when you just met a term in
   CLI output or a generated file and want the fastest possible answer.
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

**Approved 2026-09-23** by the actual user/domain owner, subject to
four corrections identified during review and applied the same day
(two content over-generalisations on
[`concepts/provenance.md`](concepts/provenance.md)/
[`concepts/evidence.md`](concepts/evidence.md) about which enrichment
tables actually carry a `model` provenance column; a stale file-path
reference on [`concepts/requirement.md`](concepts/requirement.md); a
planning-status inconsistency across `planning/ROADMAP.md`/the phase
plan, unrelated to this corpus's own content). Every page now carries
`status: APPROVED (2026-09-23, actual user/domain owner, subject to
corrections applied same day)`.

`domain-skeptic`'s own independent adversarial review ran once before
approval
([`planning/retros/_domain-skeptic-review-phase-63d.md`](../../planning/retros/_domain-skeptic-review-phase-63d.md))
and found no genuine, unresolved domain/product ambiguity requiring the
actual user's attention — every open item in
[`open-questions.md`](open-questions.md) was reviewed and accepted as
correctly left open, not requiring a ruling.

## Freshness

This corpus is a point-in-time conclusion, not a fact that stays true
forever. See
[`development-methodology.md`](../../planning/v1-redefinition/development-methodology.md)'s
own "Domain-corpus freshness and reconciliation" section for when and
how it gets reconsidered — reusing existing checkpoints (a per-phase
drift-audit check, retros, and a milestone reconciliation pre-v1; a
per-feature gate post-v1), never a new standing "domain watcher"
process.
