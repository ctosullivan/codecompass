# 0094. Knowledge Placement Policy enforcement: ad-hoc reviewer dispatch, two deferred checks, and a no-synthetic-substitute real-dogfood rule

## Status

Accepted

## Context

Phase 86 (`decisions/0084` §2, formalised `decisions/0085` §4) asked
for a Knowledge Placement Policy plus an enforcement surface with three
named classes (mechanical, behavioural, semantic/editorial). The
phase's own plan (`planning/phase-86-knowledge-placement-code-quality-
review.md`) went through four independent-review rounds before
implementation began, each surfacing a non-obvious tradeoff this ADR
records.

## Decision

**1. The semantic/editorial reviewer is an ad-hoc dispatch, never a new
standing agent.** `docs/workflows/knowledge-placement-review.md`'s own
full text is pasted inline as a `general-purpose` subagent's dispatch
prompt each time this review runs — never a 14th `.claude/agents/*.md`
roster file. The first planning draft proposed a standing agent,
arguing from independence alone; independent review found that
independence and a stable, repeatable charter are both already
satisfiable by the project's own existing `L-023` substitution pattern
(`planning/v1-redefinition/agent-led-development.md` §2.14), and that
this capability — unlike `release-phase-auditor`/`docs-reconstructor`,
both dispatched on every single phase's own DoD — has no comparable
mandatory reuse frequency yet. Promotion to a true roster entry remains
a named, evidence-gated future escalation (not pre-committed) if real
reuse ever makes brief-drift a material risk.

**2. `docstring-contradicted-by-oracle-result` is deferred, not
shipped.** The original design proposed a mechanical/behavioural script
check: cross-reference a docstring's cited `check_id` against a real
oracle result, reporting a contradiction whenever the only result found
was `FAIL` or `INVALID`. This conflates two things this project's own
Oracle semantics (`decisions/0081`-`0083`) do not license: `INVALID`
means the check itself could not establish a verdict (evidence of
uncertainty), never a demonstrated falsity; and a bare `check_id`
citation does not, by itself, establish that a docstring *asserts* the
cited check's own specific behaviour. Shipping it would have required
inventing a new mandatory annotation convention solely to make the
check safe — rejected. Behavioural review remains one of the three
enforcement classes, performed instead by the ad-hoc reviewer directly
reading real Phase 82-84 evidence with the correct PASS/FAIL/INVALID
precedence, never through a dedicated checker.

**3. `decision-citation-status-mismatch` is deferred, not shipped.**
The original design proposed a mechanical check comparing a comment's
own bracketed status assertion (e.g. `decisions/0057 (rejected)`)
against the cited ADR's real, current `## Status` field, blocking on a
literal mismatch. The project's own real corpus already demonstrates
why this is unsafe: `decisions/0019`'s own `## Status` field has stood
`Accepted`, unedited, since it was written (`CLAUDE.md` §2's append-only
rule), while `decisions/0061` independently records that `0019` is, in
effect, superseded. A comment candidly noting `decisions/0019
(historical rationale)` — an accurate description of *effective*
status — would literally disagree with the recorded `Accepted` field
and be wrongly blocked. Shipping this check safely would require either
resolving recorded-vs-effective status first (already
`decision-citation-superseded`'s own job, informational) or inventing a
new annotation convention distinguishing the two — neither acceptable
without a demonstrated real use case. Deferred, evidence-gated, not
prohibited.

**4. The real-dogfood exit gate can never be satisfied by a constructed
fixture.** `planning/v2-roadmap.md`'s own Phase 86 exit gate requires at
least one real, previously-unflagged placement defect found **and
corrected**. An earlier planning draft left ambiguous whether a
constructed-fixture "full pipeline demonstration" could stand in if no
real defect existed. Resolved explicitly: a constructed fixture is
valid for the unit/integration test suite only; the real-dogfood gate
either uses a genuinely different real instance (found by widening the
search to another bounded subsystem) or is reported honestly unmet,
never papered over with synthetic evidence.

**5. Citation extraction is `ast`/`tokenize`-based, with supersession
attribution scoped to four ADR sections.** `scripts/check_knowledge_
placement.py` recognises a `decisions/NNNN` citation only inside a real
docstring (`ast.get_docstring(node, clean=False)` — the raw text; the
`clean=True` default silently discards leading blank lines before
line-offset counting, which would misreport a multiline docstring's own
citation line) or a real `#` comment (`tokenize`), never an ordinary
string literal. Supersession attribution scans an ADR's own title line,
`## Status`, `## Decision`, and `## Consequences` sections only —
verified against the real corpus to match exactly 8 files
(`decisions/0031/0032/0033/0034/0043/0061/0070/0078`), with
`decisions/0027`'s "is **not** superseded" and `decisions/0058`'s
`## Context`-only mention confirmed as negative controls, and a
`decisions/0032` conjunction ("X and Y are superseded") disclosed,
rather than silently incomplete, as only capturing the number
immediately adjacent to the verb.

## Alternatives considered

- **Ship all four originally-proposed checks, accepting the semantic-
  inference risk.** Rejected — each failure mode above is a real,
  demonstrated false-blocking risk against this project's own actual
  corpus, not a hypothetical.
- **Promote the ad-hoc reviewer to a standing agent now, pre-emptively.**
  Rejected per `decisions/0081` §3's own repeated pattern: a future
  phase may require this once real reuse justifies the cost; not
  pre-committed here.
- **Allow a constructed fixture to satisfy the real-dogfood gate when no
  real defect is found.** Rejected — this would permit every future
  phase using this exit-gate pattern to manufacture a passing result
  rather than honestly reporting a gate as unmet.

## Consequences

- `scripts/check_knowledge_placement.py` ships with two mechanical
  checks (`decision-citation-exists`, blocking; `decision-citation-
  superseded`, informational) plus an always-blocking
  `knowledge-placement-unparseable-source-file` diagnostic. No new
  behavioural check exists in this script.
- `docs/concepts/knowledge-placement-policy.md` and `docs/workflows/
  knowledge-placement-review.md` are the two new documentation
  deliverables recording the policy and the ad-hoc reviewer's own
  brief, respectively.
- The real dogfood (`planning/retros/phase-86-knowledge-placement-code-
  quality-review.md`) records the specific real defect found, the
  independent adjudication, the lead's own correction, and the
  post-fix re-verification.
- If a later phase's real usage shows either deferred check, or the
  ad-hoc-dispatch design, needs revisiting, that phase's own plan
  supersedes the relevant part of this ADR with a new numbered one, per
  `CLAUDE.md` §2.
