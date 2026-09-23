---
status: PROPOSAL (Phase 64, Cluster C — durable, user-facing derivation of an existing internal document)
---

# Development-process category — reconstruction proposal

## What this is, and what it is not

This directory proposes a **durable, user-facing** version of
[`planning/v1-redefinition/development-methodology.md`](../../v1-redefinition/development-methodology.md)
(hereafter "the source document") — the Scope → Plan → Domain → Design →
Implement process CodeCompass uses to develop itself, per
[`decisions/0060`](../../../decisions/0060-scope-plan-domain-design-implement-methodology.md).

**This is not a new process.** Every stage, rule, and table below
traces to a specific section of the source document, cited inline. What
this dispatch changed is presentation, for the reason
`planning/phase-64-blank-slate-documentation-reconstruction.md` states:
the source document currently lives inside `planning/v1-redefinition/`
— a tree scoped to one internal planning effort (the "redefined
CodeCompass v1" milestone group) — and reads as an internal artifact of
that effort (cross-referencing specific phase numbers, GATE names, and
same-week amendment history). A reader who is not already following
that effort — a new contributor to this project, or someone at a
different project entirely evaluating whether to adopt the process —
should not need to understand `planning/v1-redefinition/`'s own
internal bookkeeping to use the process itself.

## What changed, specifically

1. **Split into three files by durability**, rather than one document
   mixing all of it:
   - [`process.md`](process.md) — the five stages, the traceability
     spine, and the re-entry rules: the part that travels to any
     project, per the source document's own "Portability" section.
   - [`minimum-viable-adoption.md`](minimum-viable-adoption.md) — the
     source document's own lightweight-equivalent table for a project
     with none of CodeCompass's own scaffolding, promoted to its own
     file since it is the part most directly useful to an outside
     reader deciding whether this process is worth adopting at all.
   - [`codecompass-instantiation.md`](codecompass-instantiation.md) —
     everything that is specifically *how CodeCompass itself* runs the
     process (agent role names, `docs/domain/`-specific freshness
     mechanics, roadmap phase citations) — kept, but clearly separated,
     for the contributor persona who does need to know how this project
     specifically works.
2. **Dropped, deliberately, as non-durable**: the source document's own
   same-week amendment history (e.g. "corrected 2026-09-20," "this
   document's own three same-week amendments") and its "Where this gets
   exercised before v1" section (a running tally of which CodeCompass
   phases have used the process so far, current only as of the source
   document's own last edit). Both are genuinely useful — as evidence
   that the process has been exercised for real, not merely proposed —
   but they are process-*history*, not the process itself, and would go
   stale immediately in a document meant to stay durable. They remain
   fully available at the source document's own location; nothing here
   deletes or supersedes them.
3. **Generalized away CodeCompass-specific framing where the underlying
   point is not CodeCompass-specific** — for example, the source
   document's "Why five stages, not the existing two" section frames the
   gap in terms of `CLAUDE.md` §1's own Scope/Plan requirement
   specifically; [`process.md`](process.md)'s equivalent section keeps
   the substance (most projects already do some version of Scope and
   Plan informally; what is commonly missing is a dedicated,
   evidence-based Domain stage and an independently-reviewed Design
   stage before code) while citing `CLAUDE.md` §1 as CodeCompass's own
   example of that pattern, not as a precondition for the process itself.

No rule, stage, record shape, or table value was changed, added, or
removed from the source document's own substance — only re-framed for a
reader outside `planning/v1-redefinition/`. Where this proposal's
wording differs from the source document's own wording, the citation
next to it points at the exact source passage so a reader can check.
