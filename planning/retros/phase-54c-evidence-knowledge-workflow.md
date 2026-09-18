# Phase 54c retro — Evidence-backed, knowledge-based, documentation-first workflow

- **Date:** 2026-09-18
- **Commit(s):** (this phase's own closeout commit, see `planning/CONTEXT.md`)
- **Agents used:** `context-researcher` — dispatched exactly once, for
  the primary proving case's own research, as `general-purpose` with
  the role's brief embedded, since the newly-created agent type wasn't
  yet loaded into the dispatcher's registry at that point in the
  session (see "What didn't work"); never re-dispatched under its own
  real type, since that research was already complete by the time the
  registry refreshed. `documentation-agent` (real type, two dispatches:
  initial `design.md`, then a full regeneration — not a hand-patch —
  after the review step added the Decision/Requirements).
  `knowledge-curator` (real type, two dispatches: the new
  packet-assembly mode, and the phase's own normal learnings triage). A
  fresh `general-purpose` dispatch for the "can another agent explain a
  claim" verification. `release-phase-auditor` (real type, two
  dispatches: an initial FAIL on this retro's own "Where we are"/
  "Candidate learnings filed" sections, and a re-audit PASS WITH
  NON-BLOCKING OBSERVATIONS after both were corrected).

## Where we are

Stage D (deeper Ledgerkit dogfooding) closed out with Phase 54b's own
result: two fresh agents (baseline vs. CodeCompass-assisted) both
reached the same correct, complete answer to a real hledger behavioural
question, at LOW context advantage — a real, disclosed curation-
completeness gap, not a mechanism failure. That result, plus every
Ledgerkit-facing finding accumulated since Phase 45, is the evidence
Phase 55's own GATE DD decision (is a generalised technical-dependency/
provenance graph ontology needed for v1?) is meant to weigh — a decision
this project has deliberately left open rather than forced.

Directly after Phase 54b closed, the user asked for something bigger
than any single GATE DD candidate design: a full evidence-backed,
knowledge-based, documentation-first *development workflow*
(Observation/Evidence/Claim/Derivation/Decision/Requirement, plus a
Context Researcher → Documentation Agent → review gate → context packet
→ coding agent → revalidation loop), usable for both CodeCompass's own
development and downstream projects like Ledgerkit. That request was
planned as Phase 54c — a bridge phase between Phase 54b and Phase 55's
still-open gate, deliberately scoped to *inform* GATE DD rather than
pre-empt it — then amended once before implementation per direct user
feedback (Evidence neutrality, the Decision/Claim boundary, two agent
roles instead of three, a context-packet sufficiency log, and an
explicit hedge against overclaiming the methodology's general value from
two bounded proving cases alone).

This retro covers that amended plan's **implementation**: both proving
cases (`CG-005`, `hledger-depth`) run for real, per the user's own
"Implement the next phase" instruction. After this phase, Stage D is
fully closed, GATE DD remains open with a materially richer evidence
package, and Phase 60 (the next unstarted, ungated phase) is next.

## Goal

Test a bounded, reversible evidence/knowledge model and documentation-
first workflow — not decide the model's final architecture. Two proving
cases: `CG-005` (primary, full loop, tests workflow **mechanics**) and a
retroactive `hledger-depth` reconstruction (secondary, tests
knowledge→documentation **fidelity**). Per the amended plan's own
explicit hedge, neither case — nor both together — is meant to be final
proof of the methodology; that remains Phase 60/61's job, under genuine
uncertainty this phase deliberately didn't attempt to manufacture.

## Scope delivered vs planned

Delivered exactly as the amended plan scoped: the six record kinds
(§2.2), file-based storage under `planning/knowledge/`, two new agent
briefs (`context-researcher.md`, `documentation-agent.md`), one new
`knowledge-curator` mode (packet assembly, not a third role),
`scripts/check_knowledge_base.py`, the full `CG-005` implementation, and
the retroactive `hledger-depth` reconstruction. One real, disclosed
deviation from the plan's own assumption: the plan assumed dispatching
the two new agent *types* directly; in practice, a freshly-created
`.claude/agents/*.md` file isn't loaded into this session's dispatcher
registry until some point after creation (observed empirically — the
first `context-researcher` dispatch attempt failed with "Agent type not
found," a later one for the same role succeeded once the registry had
refreshed). Worked around by embedding the role brief's full content
into a `general-purpose` dispatch for the first research pass; the real
`context-researcher`/`documentation-agent`/`knowledge-curator` types
were used correctly for every dispatch after the registry refreshed.

## What was achieved

1. **A real, working knowledge base for `CG-005`**: 11 Observation, 9
   Evidence, 4 Claim, 4 Derivation, 1 Decision, 3 Requirement records,
   `design.md` (regenerated once after review, never hand-patched),
   `context-packet.md`, `packet-sufficiency.md`.
2. **A real, small implementation**: `doc_artifacts.origin` gains
   `pinned_reference` (`_SCHEMA_VERSION` 6→7), `spec_docs.py::scan_spec_docs`
   gains automatic frontmatter-based detection
   (`_has_pinned_reference_frontmatter`, `_detect_origin`). 6 new tests
   (4 in `tests/test_spec_docs.py`, 2 in `tests/test_graph.py`, mirroring
   the established Phase 17/21/27 fresh-DB + migration test pattern). 587
   tests pass, `ruff`/`check_user_docs.py --strict`/`check_knowledge_base.py --strict`
   all clean.
3. **Real end-to-end behavioural confirmation**, not just unit tests: a
   synthetic scratch project confirmed the schema migration and both
   branches (frontmatter present → `pinned_reference`; absent →
   `project`); separately, re-running `codecompass sync` against Phase
   54b's own real scratch Ledgerkit copy confirmed **all 19 real ingested
   files** now read `origin='pinned_reference'` while Ledgerkit's
   hand-authored docs stayed `project` — `CG-005`'s own original,
   real-world motivating instance is closed for real.
4. **A real, honest secondary proving case**: the retroactive
   `hledger-depth` `design.md`, built entirely from Phase 54b's
   already-verified evidence (no new dispatch), correctly and completely
   states the same three-way behavioural split (clip / partial-exclude /
   inert) Ledgerkit's real, shipped Stage C Phase 5 work independently
   arrived at — a genuine, verified fidelity result.
5. **A real, independently-verified traceability test**: a fresh
   `general-purpose` agent, given only `CL-DOCORIGIN-003`'s citation
   chain (no other context), correctly and specifically reconstructed
   the claimed `KeyError`-crash mechanism, its file/line evidence, and
   the distinction between the crash and silent-invariant-violation
   failure modes — a genuine PASS, not asserted.
6. **`CG-005` promoted** in `planning/context-gaps/inbox.md`, pointing at
   the full evidence trail.

## What worked

- **The neutral-Evidence / Claim-owns-support-or-contradict split**
  (this session's own amendment) held up cleanly in practice —
  `context-researcher`'s Evidence records read as plain factual
  statements throughout, with no drift back toward embedding a
  support/contradict judgement on the Evidence side.
- **The Decision-never-supersedes-a-Claim hard rule** was easy to follow
  correctly once reviewing: `DEC-DOCORIGIN-001` cleanly used
  `agrees_with_claim`, never `supersedes`, and `check_knowledge_base.py`'s
  own mechanical check for this rule found nothing to flag.
- **Regenerating `design.md` from scratch, not hand-patching**, worked
  exactly as designed — the second `documentation-agent` dispatch
  produced a document that correctly reflected the new Decision/
  Requirement records while preserving every citation to the unchanged
  underlying Claims, and explicitly marked what had changed (§9's
  "history and resolution" restructuring) rather than silently deleting
  the prior open-question framing.
- **The packet-sufficiency log caught something real and specific**: not
  a vague "the packet could have been better," but two concrete,
  actionable gaps (an entire test file never named; an established test
  pattern described narratively but not pointed at its own file) —
  exactly the kind of signal §6.1 was designed to surface, and a much
  stronger result than a word-count comparison would have given.
- **Reusing Phase 54b's already-verified evidence for the secondary
  proving case cost almost nothing** (five Observation, three Evidence,
  one Derivation/Claim record, all reconstructed from an existing
  report) and produced a real, checkable fidelity result.

## What didn't work

- **Newly-created agent briefs weren't immediately dispatchable.** The
  first `context-researcher` dispatch failed outright ("Agent type
  'context-researcher' not found") despite `.claude/agents/context-researcher.md`
  already being committed to the working tree — the dispatcher's agent
  registry appears to load at some point other than "the moment the file
  exists," and this session had no way to force a refresh. Worked around
  by dispatching `general-purpose` with the role's full brief embedded
  in the prompt for that one research pass; the real agent type became
  available later in the same session for every subsequent dispatch, for
  reasons this session doesn't have visibility into (not something to
  guess at further).
- **Neither proving case exercised `contradicting_evidence` or a real
  Claim-level `supersedes` with actual content.** Every Claim in both
  feature directories ended with an empty `contradicting_evidence` list
  and `supersedes: null` — the model's "retain contradictory evidence
  without silently resolving it" property is real and structurally
  checked (`check_knowledge_base.py`), but was never exercised with a
  genuine contradiction in this phase. This is a real, disclosed gap in
  what this phase's own evidence can support, not a claim of untested
  success.
- **Neither proving case tested "does the design-document review catch
  a real misunderstanding before implementation."** `CG-005`'s own
  research was correct from the outset (nothing to catch); the
  retroactive `hledger-depth` case is, by its own design, not a fresh
  review at all. This question (§10, bullet 7) is honestly left
  unanswered by this phase, not answered positively by default.

## Lessons learnt

A phase that dogfoods its own newly-created infrastructure (new agent
types, in this case) should expect and plan for an activation-timing gap
between "the file is written" and "the file is dispatchable" — and
should have a disclosed fallback (embedding the brief in a
`general-purpose` dispatch) ready rather than treating the first
dispatch failure as a blocker. This is a real, generalisable operational
finding, distinct from anything about the evidence model itself.

Separately: designing two proving cases up front to specifically avoid
manufacturing a contradiction or a real review-catches-a-mistake moment
(in the name of boundedness and reuse) has a real cost — it leaves two
of the plan's own ten evaluation questions honestly unanswered rather
than weakly-positive. This was the right trade for a first, bounded
experiment (per the amended plan's own explicit hedge against
overclaiming), but the next phase that uses this model should pick at
least one case where a real contradiction or misunderstanding is
plausible, specifically to exercise the properties this phase couldn't.

## Process-improvement feedback

The amendment made to this plan before implementation (Evidence
neutrality, the Decision/Claim boundary, two roles not three, the
sufficiency log) all paid for themselves directly in this run — none of
the three would have been easy to retrofit after real records existed
using the old shapes, and the packet-sufficiency log's two findings
would have had no home to be recorded in without §6.1 existing from the
start. Reviewing a plan once, carefully, before the first real record is
written is cheap; correcting a live knowledge model's own shape after
records accumulate would not have been.

## Answers to the plan's §10 questions (verbatim from the governing prompt's §9)

1. **What forms of evidence were actually useful?** Feature-dependent,
   not universal: `CG-005` (an internal schema/code question) used
   `source_read` observations exclusively — no executable evidence was
   relevant or gathered. The retroactive `hledger-depth` case used both
   `source_read` and `executable` observations (reused from Phase 54b's
   real binary runs). Neither case needed a `doc_read`-only chain in
   isolation. **Finding: the researcher should not default to gathering
   every evidence kind "for completeness" — which kinds matter is a real
   property of the feature, decided during research, not assumed up
   front.**
2. **Which provenance fields were necessary?** Every field in §2.3's
   adopted list was populated at least once across both feature
   directories, except: `tool`/`tool_version` on `source_read`
   Observations (correctly left `null` — not applicable to that method,
   confirming these fields are method-conditional, not universally
   required, exactly as §2.2's own comment anticipated). One field
   speculatively sketched in the amended plan (`deviates_from_claim` on
   Decision, as an alternative to `agrees_with_claim`) was never actually
   needed — `DEC-DOCORIGIN-001` only ever needed to *agree with* a Claim,
   never to deliberately diverge from one. **Recommendation: don't add
   `deviates_from_claim` as a standing field until a Decision genuinely
   needs it — `agrees_with_claim`'s absence would be equally clear
   signal.**
3. **Can another agent explain why an important claim is believed?**
   **Yes, verified for real** — a fresh `general-purpose` dispatch, given
   only `CL-DOCORIGIN-003`'s five-record citation chain and nothing else,
   correctly and specifically reconstructed the claimed `KeyError`
   mechanism, its exact file/line evidence, and the crash-vs-silent-
   violation distinction, without guessing or filling gaps (its own
   stated verdict). A genuine pass, not a vibe check.
4. **Can claims be traced back to primary evidence?** Yes, both
   structurally (`check_knowledge_base.py`'s cross-reference-resolution
   check found zero dangling references across either feature directory,
   throughout every edit this phase made) and substantively (question 3's
   own test).
5. **Can contradictory evidence be retained without silently resolving
   it?** **Not tested with real content** — see "What didn't work." The
   mechanism exists and is mechanically checked, but no genuine
   contradiction arose in either proving case to exercise it against.
6. **Can user corrections update the knowledge model cleanly?** Yes,
   demonstrated for real: the review step added one Decision and three
   Requirements without touching any existing Observation/Evidence/Claim/
   Derivation record, and `design.md` was cleanly regenerated (not
   hand-patched) to reflect them, verified by rereading the regenerated
   document and by `check_knowledge_base.py`.
7. **Does the design-document review catch misunderstandings before
   implementation?** **Not tested** — see "What didn't work." Neither
   proving case presented a real misunderstanding for review to catch.
8. **Is the resulting coding-agent context smaller and more actionable
   than raw repository context?** Yes, measured concretely:
   `context-packet.md` (~210 lines) vs. `design.md` (455 lines), and —
   the stronger signal — `packet-sufficiency.md` logged exactly two real,
   specific, actionable gaps during implementation, not a vague
   "something was missing" or (more concerning) zero gaps logged despite
   real ones existing.
9. **Can implementation results update the knowledge model without
   losing historical provenance?** Yes, demonstrated: all three
   Requirements moved `approved` → `verified` (in place, one-line
   status edits, per §2.4's own convention) after real end-to-end
   confirmation; `design.md` gained a new §15 appended, not overwriting
   anything; `CG-005`'s own `context-gaps/inbox.md` entry gained a
   promotion note appended below its own original filing, unchanged.
10. **Does this improve development quality enough to justify making the
    model permanent?** **Scoped honestly, per the amended plan's own
    explicit hedge**: workflow *mechanics* worked end to end without
    breaking down (`CG-005`), and knowledge→documentation *fidelity* held
    for a known-correct case (`hledger-depth`). Neither result, nor both
    together, answers whether the workflow improves development quality
    under genuine uncertainty — that test remains Phase 60/61's, not
    this phase's, exactly as the amended plan anticipated before this
    run even started.

## Durable-vs-experimental recommendation (per the plan's own framing: this phase's single most important deliverable)

Recommended to the user for ratification, not decided here:

| Piece | Recommendation | Why |
|---|---|---|
| The six record kinds (Observation/Evidence/Claim/Derivation/Decision/Requirement), as amended (neutral Evidence, Decision-never-supersedes-Claim) | **Promote to durable, file-based convention** — reuse for the next feature this workflow is applied to, without a schema/shape change | Held up cleanly under real use, including under the review-and-regeneration cycle; the amendment's own three structural fixes all paid for themselves directly, with no further shape problems found |
| File-based storage under `planning/knowledge/`, not `context-graph.db` | **Keep experimental/provisional, revisit only if evidence demands a query capability YAML files can't give** | No cost was found this phase from staying file-based; nothing yet demonstrates a real need for graph-backed storage |
| `context-researcher`, `documentation-agent` as distinct roles | **Promote to durable roles** — but note the registry-activation-timing gap as an open, unresolved operational question, not a reason to doubt the roles themselves | Both produced real, well-cited, honest output; the activation gap is a dispatch-mechanism issue, not a role-design issue |
| `knowledge-curator`'s new packet-assembly mode (not a third role) | **Promote to durable** — the mode stayed cleanly bounded (mechanical compaction, correctly refused to resolve an unresolved ambiguity itself) and produced a genuinely smaller, useful packet | Validates the amendment's own "extend before adding a third role" choice directly |
| The `packet-sufficiency.md` log | **Promote to durable, mandatory per feature implemented via this workflow** | Found two real, specific, actionable gaps on its very first real use — the single highest-value mechanism this phase tested |
| The `contradicting_evidence`/Claim-`supersedes` machinery | **Keep as structurally-checked but experimentally unproven** — do not claim it "works," since it was never exercised with real content | Honest gap, not a finding either way; the next phase using this model should deliberately pick a case likely to produce a real contradiction |
| The review-gate lifecycle (`DRAFT`→...→`VERIFIED`) | **Promote to durable** — the state transitions (including the backward-allowed `IMPLEMENTING`→`RESEARCHED` case, though not exercised this phase) matched real usage cleanly | No friction found; `design.md`'s own frontmatter tracked state correctly throughout |
| Whether this workflow "improves development quality" generally | **Not yet decided — deliberately left open** | Per the amended plan's own explicit hedge; Phase 60/61 is the next, harder test, under genuine uncertainty this phase didn't attempt to manufacture |

## Candidate learnings filed

Both real findings this retro surfaces were filed and triaged by
`knowledge-curator`'s normal pass, and both were promoted:

- **`L-023`** — a newly-created `.claude/agents/*.md` file is not
  immediately dispatchable by its own type name (the agent-registry
  activation-timing gap). Promoted into `planning/agent-led-workflow.md`
  step 5 (a disclosed fallback: dispatch `general-purpose` with the new
  role's brief embedded for the first pass, retry the real type name
  later in the same session).
- **`L-024`** — a context packet's own "existing tests" section must
  check for a schema/migration mechanism's own dedicated test file, not
  just the feature's own code-path test file (the `tests/test_graph.py`
  gap, root-caused to `context-researcher`'s own consumer-trace covering
  code consumers exhaustively but not test files asserting a
  schema-version literal). Promoted directly into
  `.claude/agents/context-researcher.md` step 6.

Both entries are logged in `planning/learnings/promoted.md`; both have
full curation notes in `planning/learnings/inbox.md`.

## Where we're going

GATE DD (Phase 55) now has this phase's own durable-vs-experimental
recommendation as a concrete evidence input, alongside Phase 54b's own
result. Phase 60 (minimal Haskell adapter) remains the next unstarted,
ungated phase. If GATE DD or a future session picks up this workflow for
a second feature, it should deliberately choose one likely to produce a
genuine contradiction or a real pre-implementation misunderstanding —
the two properties this phase's own bounded proving cases couldn't
honestly test.

## Time / cost note

Eight dispatches across this phase: one `context-researcher`
(embedded-brief `general-purpose` dispatch, ~355s, 60 tool uses — the
most expensive single dispatch, consistent with genuine primary
research); two `documentation-agent` dispatches (~140s/~130s); one
`knowledge-curator` packet-assembly dispatch (~131s); one verification
dispatch (~29s, 6 tool uses — notably cheap, since it was scoped to
exactly five small files); one `knowledge-curator` learnings-triage
dispatch (~235s, 26 tool uses); two `release-phase-auditor` dispatches
(~412s/~140s — the first round's own FAIL, correctly caught, cost more
than the fix it required). The lead's own implementation work
(schema change, detection logic, 6 new tests, two real end-to-end sync
runs) was comparable in size to a normal small bounded phase — the workflow's
overhead was the knowledge-base construction and review steps, not the
implementation itself.

## `release-phase-auditor` verdict

**Round 1: FAIL.** Every artifact outside this retro checked out cleanly
(re-ran `pytest`/`ruff`/`check_user_docs.py --strict`/
`check_knowledge_base.py --strict`, independently reproduced the real
end-to-end `codecompass sync` claim twice, verified the structural
hard-rule and Evidence-neutrality properties directly against the
committed records, confirmed no `CLAUDE.md`/`decisions/*` drift) — but
this retro's own "Where we are" was a stub with no arc/stage
orientation, and "Candidate learnings filed" falsely stated nothing was
filed when `L-023`/`L-024` were both already promoted. Both fixed
(above). **Round 2: PASS WITH NON-BLOCKING OBSERVATIONS** — confirmed
both fixes accurate against the actual `planning/learnings/inbox.md`/
`promoted.md` state; found one further, non-blocking internal
inconsistency (this retro's own dispatch count, "Time / cost note") —
fixed in the same pass, not re-audited a third time.
