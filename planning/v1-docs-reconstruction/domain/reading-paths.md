---
status: PROPOSAL (Phase 64, Cluster C — reorganization only)
---

# Reading paths into `docs/domain/`

Four entry sequences into the same, unchanged
[`docs/domain/`](../../../docs/domain/) content, one per reader profile
this blank-slate reconstruction is scoped to serve. Nothing below
restates a definition — every step is a link into the real page; read
that page for the actual content.

## 1. New user (met a term in CLI output or a generated file, wants a fast answer)

Start at [`quick-reference.md`](quick-reference.md), find the term, stop
there unless curious — the quick-reference line already cites the full
page if more is wanted. Do not start at `docs/domain/README.md` or
`docs/domain/glossary.md` for this profile; both are written for a
deeper pass than "what does this word mean in the message I just read."

## 2. Contributor writing a new ecosystem adapter

The corpus's own concepts directory is alphabetical, which is the wrong
order for this task — the real dependency chain a new adapter author
needs to understand, in order, is:

1. [`docs/domain/concepts/ecosystem.md`](../../../docs/domain/concepts/ecosystem.md)
   — the fixed, closed 4-member category a new adapter would need a
   fifth member added to (a `src/codecompass/` change and an ADR, not a
   docs change — see the concept page's own "closed" invariant).
2. [`docs/domain/concepts/vendor.md`](../../../docs/domain/concepts/vendor.md)
   — what `vendor.toml` actually configures, and, critically, what it
   does *not* configure (no path information at all).
3. [`docs/domain/concepts/adapter.md`](../../../docs/domain/concepts/adapter.md)
   — the two coexisting implementation strategies (in-process vs.
   external-process), and `get_adapter`'s closed dispatch table.
4. [`docs/domain/concepts/protocol.md`](../../../docs/domain/concepts/protocol.md)
   — required only for the external-process strategy: the JSON-Lines
   wire contract, closed method/error-code sets.
5. [`docs/domain/concepts/capability.md`](../../../docs/domain/concepts/capability.md)
   — required only alongside protocol.md: the four-value capability set
   gating which result sections an external adapter may return.

Then read [`docs/domain/examples.md`](../../../docs/domain/examples.md)'s
own worked example 2 ("One vendor query, five concepts in motion") for
all five moving together in one real call sequence.

## 3. Maintainer doing a docs-drift audit or domain-corpus freshness check

Per `development-methodology.md`'s own "Domain-corpus freshness and
reconciliation" section (see this dispatch's own
[development-process](../development-process/) category for the durable
version of that section), a per-phase drift audit or a future feature's
Domain stage needs to check whether a changed file/symbol/behaviour is
cited in a concept page's own references block. For that task:

1. [`docs/domain/invariants.md`](../../../docs/domain/invariants.md) —
   cross-cutting rules; check first, since a violated invariant is the
   highest-severity kind of staleness.
2. [`docs/domain/open-questions.md`](../../../docs/domain/open-questions.md)
   — already-known unresolved items; check whether the change touches
   one of these before treating it as a new finding.
3. The specific `docs/domain/concepts/*.md` page(s) whose references
   block cites the changed file/symbol — per `documentation-lifecycle.md`
   §"Domain-corpus freshness and reconciliation," this is a **domain-claim
   staleness candidate** to name in the audit report, not itself a
   drift finding.

## 4. AI coding agent doing a feature's own Domain stage (`development-methodology.md`)

Before starting fresh Domain-stage research on a new feature, per the
[development-process](../development-process/) category's own
"minimum viable adoption" and freshness-gate sections:

1. [`docs/domain/glossary.md`](../../../docs/domain/glossary.md) — check
   whether the feature's own subject matter is already a settled
   project-wide concept (skip re-deriving it if so; cite the existing
   page instead).
2. The specific `docs/domain/concepts/*.md` page(s) that match, reading
   each one's own "Counterexample / edge case" and "What it is NOT"
   sections in full — these are exactly the sections most likely to
   contain a fact a fast skim would miss.
3. [`docs/domain/open-questions.md`](../../../docs/domain/open-questions.md)
   — check whether a relied-on concept currently carries an open
   staleness candidate; per the post-v1 per-feature freshness gate, the
   feature's own Design stage may not start on top of an unresolved one.
4. Only once (1)-(3) find no existing answer: proceed to feature-scoped
   Domain-stage research (`planning/knowledge/<feature-slug>/`), per
   `development-methodology.md`'s own Domain stage.

## Full research pass (kept as `docs/domain/`'s own order — no change proposed)

[`docs/domain/README.md`](../../../docs/domain/README.md)'s own
"How to read this" order — glossary → concepts → invariants → examples →
open-questions → references — remains correct for a reviewer or
`context-researcher` doing a complete pass over the corpus. This
dispatch found no reason to change it; a reader doing genuinely full
research is well served by depth-first, one section at a time, exactly
as it already stands.
