---
status: PROPOSAL (Phase 64, Cluster C — reorganization only, not a re-derivation)
---

# Domain category — reconstruction proposal (reorganization, not re-derivation)

## What this is

This directory is **not a new investigation of what CodeCompass's
concepts mean.** Phase 63D already ran that investigation —
evidence-backed, adversarially reviewed by `domain-skeptic`, and
approved by the actual user/domain owner on 2026-09-23 — and its output,
[`docs/domain/`](../../../docs/domain/), is authoritative for meaning.
Per this phase's own plan (`planning/phase-64-blank-slate-documentation-reconstruction.md`
§0) and `decisions/0060`, this dispatch's job is narrower: **propose how
that same, unchanged content should be organized and entered** for the
blank-slate reconstruction's own presentation needs — a different
question from "what does 'adapter' mean," which stays answered exactly
as `docs/domain/concepts/adapter.md` already answers it.

Every substantive claim in this directory is either a direct citation to
a `docs/domain/` page, or a verbatim/near-verbatim excerpt from that
page's own text with a citation attached. Nothing here should be read
independently of the pages it points at — if this directory and
`docs/domain/` ever appear to disagree, `docs/domain/` is authoritative
and this directory has a bug (matching the standard `docs/domain/README.md`
already states for its own relationship to the underlying knowledge-base
records).

## What changed vs. `docs/domain/`'s own organization, and why

`docs/domain/README.md`'s own "How to read this" order — glossary →
concepts → invariants → examples → open-questions → references — is
built for one reader profile: someone doing full, careful research
(a `context-researcher` investigating a new feature, or a reviewer
checking the corpus itself). That order is kept **unchanged** here for
that reader (see [`reading-paths.md`](reading-paths.md)'s "Full research
pass" entry) — it does not need reinventing.

Three other reader profiles this blank-slate reconstruction is
explicitly scoped to serve (`planning/phase-64-blank-slate-documentation-reconstruction.md`,
quoting `documentation-lifecycle.md` §3's "new user, contributor,
maintainer, and AI coding agent") do not want that same order, or that
same level of detail, as their *first* stop:

1. **A new user** reading CLI output or a generated `vendor/<name>/CLAUDE.md`
   file meets domain terms (vendor, ecosystem, digest) without wanting a
   research-grade page for each one. They want a one-line definition
   with a pointer to go deeper only if curious.
2. **A contributor writing a new adapter** needs exactly five concept
   pages, in a specific dependency order (ecosystem → vendor → adapter →
   protocol → capability), not the corpus's own alphabetical
   `concepts/` directory listing or its glossary's own thematic
   clustering.
3. **An AI coding agent doing a feature's own Domain stage** (per
   `development-methodology.md`'s Domain stage, and the
   [development-process](../development-process/) category this same
   dispatch also covers) needs to know *which* project-wide concepts
   might already be settled before it starts fresh research on its own
   feature — and needs the staleness-check pointer
   (`docs/domain/open-questions.md`, `invariants.md`) already built into
   the corpus, surfaced explicitly rather than left to be found by
   reading every page.

This directory's own two files exist to serve those three profiles
without touching or restating `docs/domain/`'s own content:

- [`reading-paths.md`](reading-paths.md) — four entry sequences (new
  user, adapter contributor, maintainer/docs-drift, AI coding agent
  doing Domain-stage research), each just an ordered list of links into
  the real `docs/domain/` pages, with one sentence of "why this order"
  per path.
- [`quick-reference.md`](quick-reference.md) — a one-line-per-concept
  lookup table (a *shorter* projection of `docs/domain/glossary.md`,
  itself already "one paragraph per concept" — this is one further
  compression step for the scanning-while-coding use case), every line
  citing the concept page and, where the line quotes text, quoting it
  verbatim.

## Cross-links to the other five categories

See [`cross-links.md`](cross-links.md) for where this dispatch found (by
grep, against real current files, not assumption) that domain
terminology is already used outside `docs/domain/` itself — the
architecture, user/developer, and protocol/adapter categories (Clusters
A and B's own scope) should each cite the matching `docs/domain/concepts/`
page on first use of a term, rather than silently assuming the reader
already knows what "capability" or "digest" means in this project's own
specific senses.

## Retirement candidates from this half

None. See
[`../_retirement-candidates-cluster-c.md`](../_retirement-candidates-cluster-c.md)
for the reasoning (the domain corpus is four days old at the time of
this dispatch and has not yet had a chance to accrete anything the
current system doesn't justify).
