# Docs-drift audit — Phase 63D (Domain reconstruction)

**Auditor:** `docs-reconstructor` (independent, read-only, per-phase mode).
**Scope:** commits `fef153b`, `f39a986`, `27bac36`, `507e6f6` against
`README.md`, `docs/`, `architecture/`, `ai-docs/` (the current-truth doc
surfaces per `documentation-lifecycle.md` §2.5).

## Verdict: NO DRIFT

## What the diff actually changed about the system

- New content-only documentation category, `docs/domain/` (19 concept
  pages + 6 integration files), and ~140 supporting evidence/claim/
  derivation records under `planning/knowledge/codecompass-domain/`.
  This is itself a doc surface, not a behaviour change to audit *against*.
- A new development-process agent, `.claude/agents/domain-skeptic.md`,
  and widened write-boundary text in `.claude/agents/context-researcher.md`
  and `.claude/agents/docs-reconstructor.md` (the "domain-claim
  staleness candidate" check this same file now performs, added by
  `fef153b`).
- One bug fix in `scripts/check_knowledge_base.py`
  (`check_cross_references_resolve`): cross-reference resolution now
  falls back to a project-wide id set (`all_known_ids`) when a citation
  doesn't resolve in the same feature directory, before reporting a
  dangling reference — fixing 11 false positives against this corpus's
  own legitimate cross-feature citations. Purely internal to a
  maintainer-only, non-shipped script's own logic; its own docstring
  behaviour contract ("Report-only by default... `--strict` exits 1 on
  a blocking finding") is unchanged.
- Four post-approval content corrections inside `docs/domain/` itself
  (`provenance.md`, `evidence.md`, `requirement.md`, a broken filename
  citation) plus a status flip from DRAFT to APPROVED across all 25
  `docs/domain/` files — all self-contained within the new corpus, not
  touching any of the four audited surfaces.
- Everything else in the diff (`CHANGELOG.md`, `planning/CONTEXT.md`,
  `planning/ROADMAP.md`, `planning/v1-redefinition/roadmap.md`,
  `planning/phase-63d-domain-reconstruction.md`,
  `planning/learnings/inbox.md`, `planning/retros/`,
  `planning/context-observations/README.md`) is planning/process
  tracking, not a current-truth doc surface.

## Checks performed against README.md / docs/ / architecture/ / ai-docs/

**1. Does the new `docs/domain/` category make anything in the four
surfaces stale ("what documentation exists" inventories)?**

README.md's `## Documentation` section (lines 196–205) lists
`docs/cli-reference.md`, `docs/config-schema.md`, `architecture/overview.md`,
`decisions/`, `examples/`, `ai-docs/` — it does not mention `docs/domain/`.
However, this list was **already non-exhaustive before this phase**: it
also never lists `docs/external-adapters.md`, which predates Phase 63D
by several phases and is linked from elsewhere in the same README
(line 146). Since the list was not presented as a complete inventory
before this phase and still isn't, Phase 63D did not turn any existing
true sentence false — there's no claim of completeness to falsify.
This is a pre-existing documentation-currency gap, not new drift, and
`docs/domain/README.md` itself explicitly defers the formal
category-reconciliation to Phase 64's blank-slate reconstruction
("the point of the split is that Phase 64's own blank-slate
documentation reconstruction considers each deliberately"). Flagging
for the lead's awareness only, not counted as a finding.

**2. Does `architecture/overview.md` need updating for `domain-skeptic`
or the widened `context-researcher`/`docs-reconstructor` write
boundaries?**

`architecture/overview.md` documents the *shipped system's* runtime
architecture (CORE/AGENT/HOST-OUTPUT ADAPTERS module tiers, the
`context-enrichment-agent` *runtime role* per `decisions/0054`, generated
Skills, the context graph, etc.) — it does not document the development
*process* agent roster (`context-researcher`, `docs-reconstructor`,
`domain-skeptic`, etc.) at all, anywhere, before or after this phase. That
roster is exclusively `planning/v1-redefinition/agent-led-development.md`'s
job (confirmed: `grep -n agent architecture/overview.md` returns only
runtime-mechanism hits — `context-enrichment-agent`'s ADR-0054 role,
generic "an agent" phrasing, Agent Skills — never a roster or role
catalog). Since `architecture/overview.md` made no claim about the
process-agent roster to begin with, it cannot have gone stale as a
result of this phase adding one more agent to that roster. No update
needed here.

(Out-of-scope observation, not part of this verdict: the roster count
sentence in `planning/v1-redefinition/agent-led-development.md` itself
— "Eleven agent definitions exist; a twelfth (`domain-skeptic`, §2.13)
is planned" — is now stale, since `domain-skeptic` exists (12 agent
files under `.claude/agents/` as of this audit). That file is not one
of the four current-truth surfaces this per-phase mode audits, so it's
noted here only as a heads-up for whoever next touches that file, not
as a drift finding.)

**3. Does any doc misdescribe `scripts/check_knowledge_base.py`'s own
behaviour after the cross-reference fix?**

`grep -rn check_knowledge_base` across `README.md`, `docs/`,
`architecture/`, `ai-docs/` returns zero hits outside `docs/domain/`
itself. The only references to the script are within the new corpus
(`docs/domain/references.md`, `open-questions.md`, `invariants.md`,
`concepts/derivation.md`, `concepts/invariant.md`, `concepts/claim.md`,
`concepts/decision.md`), all correctly describing it as "the mechanical
validator" enforcing the knowledge-base's structural hard rules —
consistent with its own docstring ("Maintainer-only smoke check...
Not part of the codecompass package... Not shipped, not a `codecompass`
subcommand"). None of the four audited surfaces reference the script at
all, so none could have been invalidated by the fix, and the new
corpus's own references remain accurate to the fixed behaviour.

## Scope note

What was checked: the full diff of all four commits (`git show --stat`
+ full diffs for the two content-bearing commits), the current content
of `README.md`'s documentation-inventory section, `architecture/overview.md`
(agent/roster mentions), `ai-docs/README.md` and `ai-docs/CLAUDE.md`
(no relevant hits), and every cross-reference to
`scripts/check_knowledge_base.py` across the four surfaces plus the new
corpus itself. What was deliberately not re-litigated: the correctness
of the domain corpus's own claims against source (that was
`domain-skeptic`'s job, already run per
`planning/retros/_domain-skeptic-review-phase-63d.md`, and the
subsequent actual-user review that produced the four `507e6f6`
corrections) — this audit's job is only whether the four *pre-existing*
current-truth surfaces were left misdescribing the system, not whether
the new corpus is itself accurate.

## Domain-claim staleness candidates

None. This check (documentation-lifecycle.md §2.5 step 5 / this agent's
own instructions) applies to *later* phases whose diffs touch a file,
symbol, or behaviour some `docs/domain/concepts/*.md` page's references
block cites — i.e. it starts applying from the *next* phase onward, now
that `docs/domain/` exists. Phase 63D is the phase that created
`docs/domain/`, so there is no prior corpus content for this phase's own
diff to have gone stale against.
