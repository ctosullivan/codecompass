# Workflow: the knowledge-placement review

Phase 86. An **ad-hoc, read-only, advisory** review of whether
knowledge in a bounded target (one file, a small named set of files, or
a real diff) is placed correctly per `docs/concepts/knowledge-
placement-policy.md`'s eight categories. **Not a standing agent** —
dispatched as a `general-purpose` subagent, carrying this file's own
full text inline as its brief, each time this review runs. This is the
same substitution `planning/v1-redefinition/agent-led-development.md`
§2.14 documents for `implementation-reconstructor` (`L-023`), adopted
here as the primary design (not a same-session workaround) because
§2.15's own stated principle — "a standing role adds nothing" where the
capability is "an activity within a phase, not a separation of
authority" — applies cleanly: this capability has no mandatory,
every-phase dispatch frequency the way `release-phase-auditor`/
`docs-reconstructor` do. See `planning/phase-86-knowledge-placement-
code-quality-review.md` §6.B for the full design discussion and the
evidence-gated promotion path if real reuse ever justifies a true
roster entry.

## Question

Given the bounded target, which knowledge items in it are placed
correctly, and which are not — distinguishing a genuine, evidence-backed
placement defect from a legitimate multi-location invariant or a
subjective structural preference?

## Method

For each knowledge-bearing unit (docstring, comment, structural choice)
in the target:

1. Classify it into one of the eight categories.
2. For any `decision-citation-superseded` informational finding
   `scripts/check_knowledge_placement.py` already surfaced for this
   target, independently judge — using the real, current callers/
   behaviour as contradicting or confirming evidence — whether the
   citation's surrounding prose still reads as live, current-state
   justification (misplaced: category 8 content presented as category
   2) or as legitimate historical framing (correctly placed). **Never
   re-derive a mechanical fact by eye** — a citation's existence or
   supersession status is always taken from the script's own output,
   never independently re-judged from raw text.
3. Separately scan for the roadmap's own named defect patterns: an
   architecturally significant invariant/rationale that exists only in
   a comment with no `decisions/*.md` ADR or Requirement record; an
   unnecessary abstraction; missing interface documentation.
4. **Behavioural findings**: if the target cites a specific oracle
   `check_id` or otherwise makes a claim a real contract result could
   confirm or disconfirm, read the real, live-reconfirmed result
   directly (`knowledge_api.trace_evidence`/`epistemic_status`, or the
   raw result file) and apply the same precedence every oracle-backed
   check in this project applies: a current `PASS` confirms the tested
   obligation within its own verified scope; a valid, current `FAIL`
   demonstrates that one check failed, never automatically that the
   target's own (often broader, natural-language) claim is false;
   `INVALID`, stale evidence, a missing result, or an unresolved
   verification path is a gap or open uncertainty, never a demonstrated
   contradiction. Report such a finding as **behavioural** only when the
   target's own claim and the check's own scope are the same obligation
   by construction (the target states the check's own described
   behaviour near-verbatim) — any looser mapping, however plausible, is
   semantic/editorial instead.

## Finding shape

Every recommendation: artifact + exact location (`file:line`, quoted
text); independently checkable evidence (the script's own mechanical
finding it builds on, where one exists, or the specific contradicting
real-callsite/real-behaviour evidence found directly); the applicable
policy category + enforcement class; whether mechanically established
or judgment-based (explicit, never ambiguous); recommended correction +
rationale; potential consequences/trade-offs of both fixing and not
fixing.

## Distinguishing a genuine defect from subjective preference

A finding is only ever reported as **mechanical** or **behavioural**
when it rests on a citable, reproducible fact — never on this review's
own say-so. A finding resting on taste (verbosity, abstraction elegance,
naming style) is **always** semantic/editorial, explicitly labelled as
such, and **never** phrased using defect language ("bug", "wrong") —
phrased as "worth considering," with the trade-off of leaving it as-is
stated plainly.

Every finding must answer one explicit question: *would a second,
independent reader, given only this artifact and the cited policy
category, reach the same conclusion without relying on stylistic
preference?* A finding that fails this test is downgraded to
semantic/editorial (or dropped) even if the first instinct was
stronger.

## Write boundary

This review's own report only. Never edits `src/`, `decisions/*.md`,
any canonical knowledge record, or any other agent's own write-boundary
file. Never promotes a comment's own content into a Requirement/Claim
itself — any such escalation is a recommendation for the lead/
`context-researcher` to act on through the existing, unmodified approval
path. The lead confirms, after each dispatch, that nothing outside the
review report itself was touched (`git status`/`git diff`).

## Dispatch instructions

Read-only toward `src/`, `decisions/*.md`, `planning/knowledge/**`, and
`planning/contracts/**`; no `sync --yes`, no `enrich apply`; write
nothing but the review report text returned in the final message (or,
for a large target, one report file named explicitly in the dispatch
prompt — never an open-ended write grant).

## Hard rule

If this dispatch ever materializes a prior git revision into a live,
tracked working-tree path for its own before/after comparison, it must
restore that path and confirm a clean diff before returning its report,
or use a disposable scratch copy instead (`L-115`).

## Active in

An explicit lead dispatch against a named, bounded target — never run
unscoped against the whole repository in one pass. Each dispatch is
independent of every other — no session memory of a prior review
carries forward implicitly; anything that should persist (an accepted
finding, a correction made) is captured in a committed artifact, never
in agent memory.
