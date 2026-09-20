# Phase 63D: Domain reconstruction — plan

**Status:** plan only, not started. Do not begin implementation until
this plan is reviewed (`CLAUDE.md` §1).

**Sits between Phase 63 (Stage F's own last phase) and Phase 64 (Stage
G's first phase)** — a letter-suffixed bridge phase (matching
43b/43c/43d/43e, 55b precedent), not a renumbering of Stage G's 64–70.
Gated on Phase 63/GATE DF completing (sequential — "immediately before"
Phase 64, literally). **Not gated on GATE DD** (Phase 55) — a different,
unrelated axis, exactly like Phases 60–63 before it (`decisions/0056`).
See `decisions/0060` for the full rationale behind inserting this phase
and formalizing the methodology it is the first project-scoped
application of.

## 0. Why this phase, and why now

Phase 64 (blank-slate documentation reconstruction) approaches
CodeCompass "as though the current narrative documentation did not
exist" (`documentation-lifecycle.md` §3) — the right posture for
*documentation structure*, but CodeCompass has never run a dedicated,
evidence-backed pass over its own **domain concepts** specifically.
Several terms recur across ADRs, plans, retros, and code without a
single place stating what each means, where they overlap, and where
they are currently used inconsistently. Running Phase 64 without that
groundwork risks it informally re-deriving (or silently guessing at)
terminology that already has real, evidenced meaning scattered across
the repository.

This phase reuses `planning/v1-redefinition/development-methodology.md`'s
**Domain** stage — Phase 54c's own Observation/Evidence/Claim/
Derivation/Decision/Requirement model and `context-researcher` role,
generalized here from a single feature's own knowledge folder to a
**project-wide** application — plus one genuinely new mechanism,
`domain-skeptic`, an independent adversarial reviewer this project has
not had before.

## 1. Scope of the domain investigation

**In scope — the concepts named directly by this phase's own brief**,
each to be defined, evidenced, and distinguished from its neighbors:
evidence, observation, claim, derivation, provenance, relationship/edge,
context, context packet, adapter, connector, protocol, reference,
decision, invariant.

**Also in scope — concepts `context-researcher` is expected to surface
during real investigation**, not an exhaustive list decided in advance
(the whole point of evidence-first investigation is not pre-committing
to what will be found), but named here as likely candidates given
already-known overlaps in this repository:

- `vendor` vs. `adapter` vs. `ecosystem` (three related but distinct
  concepts already in `core.py`/`decisions/0002`, never defined
  side-by-side in one place).
- `symbol` vs. `export_kind` vs. a future intrinsic symbol-*type*
  concept (Phase 62's own `export_kind` naming decision already
  surfaced this distinction for one pair; the domain corpus should
  state it generally).
- `context-gaps` vs. `context-observations` vs. `learnings` (three
  queues, `planning/context-gaps/`, `planning/context-observations/`,
  `planning/learnings/`, each holding a different *kind* of "something
  noticed" record — genuinely different, but easy for a newcomer to
  conflate).
- `digest` (a rendered per-vendor output: `CLAUDE.md`/`FILETREE.md`/
  `DEPTREE.md`) vs. `context packet` (Phase 54c's own curated,
  Implement-stage artifact) — both are "a bundle of context for an
  agent," produced by very different mechanisms for different
  purposes.
- `capability` (the external adapter wire protocol's own term,
  `decisions/0057`) vs. a CodeCompass "feature."
- `enrichment` (AI-authored `vendor_enrichment`/`symbol_enrichment`/
  `doc_relation_enrichment` content) vs. `observation`/`claim` (Phase
  54c's own evidentiary records) — both are "an agent said something
  about X," but with very different trust/provenance postures
  (`decisions/0051`).
- **A specific, already-found collision, not hypothetical**: Stage E's
  own `conditional-generalisation.md`/Phase 57 candidate design already
  names `Evidence`/`Observation`/`Claim`/`Decision` as possible
  **graph-level** (`context-graph.db`) entity kinds for representing
  provenance about *other projects'* dependencies — the same names
  Phase 54c's file-based model (`planning/knowledge/`, reused by this
  phase) already uses for CodeCompass's own development-process
  records, for an entirely different purpose. This phase's own
  `evidence.md`/`observation.md`/`claim.md`/`decision.md` concept pages
  must document this collision explicitly (see
  `v1-redefinition/roadmap.md`'s Stage E entry).

**Out of scope**: rewriting or restructuring any existing ADR, plan, or
architecture doc content (Phase 64/65 do that, consuming this phase's
own output); inventing new CodeCompass features or graph tables to
represent any concept found here; resolving GATE DD or Stage E's own
generalisation question (a different, unrelated decision); building the
`docs/domain/` corpus for a downstream project (Ledgerkit, Technical
Clipper) — this phase is CodeCompass's own self-dogfood only.

## 2. Method

1. **`context-researcher`** investigates each in-scope concept
   behaviour-first (`phase-54c-evidence-knowledge-workflow.md` §3):
   greps/reads real usage across `src/`, `tests/`, `decisions/`,
   `planning/`, `architecture/`, and `CLAUDE.md` itself; where a
   concept has observable behaviour (e.g. how `context-graph.db` stores
   a "relationship," how an adapter's wire protocol frames "evidence"),
   runs or reads the real thing rather than trusting a doc's own
   description of it. Produces Observation/Evidence/Claim/Derivation
   records under `planning/knowledge/codecompass-domain/` (Phase 54c's
   own record shapes, unchanged — see that plan's §2.2), one record set
   per concept or tightly-related concept cluster.
2. For each concept, the resulting Claim records must state:
   domain rules/invariants that hold; at least one concrete example;
   at least one counterexample or edge case where the concept's
   boundary is genuinely fuzzy (or a note that none was found, not
   silence); and its relationships to neighboring concepts (subsumes,
   overlaps with, is-conflated-with, is-distinct-from).
3. Every Claim record distinguishes, per
   `development-methodology.md`'s own Domain-stage section: documented
   intent (a doc says X) vs. implemented behaviour (the code/tests do
   X) vs. historical decision (an ADR chose X, at the time) vs. current
   intended meaning (this phase's own approved conclusion) vs.
   unresolved uncertainty (honestly left open). A Claim that only
   restates what a doc already says, without an independent
   source/test/behaviour check, is not sufficient on its own — matching
   this project's own "existing documentation is not authoritative by
   default" instruction for this phase specifically.
4. **`domain-skeptic`** (new role, §4 below) reviews the resulting
   draft corpus independently: challenges every Claim lacking a citable
   Evidence record; searches for contradictions between concepts
   (e.g. does the `context packet` write-up implicitly contradict how
   `enrichment` is described elsewhere in the same corpus?); searches
   for missing edge cases the draft doesn't address. Where it can
   resolve what it finds — by pointing `context-researcher` at a
   specific further check, or running one itself (a grep, a test run,
   a `codecompass query` invocation) — it does, and the corpus is
   revised. Where it genuinely cannot (a real product/domain ambiguity,
   not a researchable fact), it escalates to **the actual user/domain
   owner**: the concept in question, the evidence gathered so far, the
   real alternative readings, and the consequence of picking each.
   **Amendment (2026-09-20): neither the lead nor any agent may stand
   in for the user on a genuine escalation, including during
   CodeCompass's own dogfooding.** This narrows Phase 54c's own §5.1
   precedent (which explicitly allowed the lead to stand in "for
   CodeCompass's own dogfooding case") — that allowance is not carried
   forward here. An agent (the lead included) may only: (a) resolve an
   item itself, by producing enough Observation/Evidence to make it no
   longer a genuine ambiguity (a fully evidence-resolved Claim, not an
   escalation at all), or (b) leave it **explicitly unresolved** in
   `docs/domain/open-questions.md`, awaiting the actual user. Neither
   option involves an agent or the lead *ruling* on a real
   domain/product ambiguity in the user's place.
5. **The actual user/domain owner** — never the lead standing in —
   rules on any escalated ambiguity. If the user is genuinely
   unavailable when this phase runs, the escalation stays open in
   `docs/domain/open-questions.md` rather than being decided by anyone
   else; the corpus can still be approved with open questions recorded
   honestly (§6), it just cannot be approved by having an agent quietly
   answer a question only the user can answer. Each real ruling becomes
   a Decision record, never a silent edit to a Claim (Phase 54c's own
   hard rule, §5.2, reused unchanged: a Decision never supersedes a
   Claim about what is factually true; it only says what the project's
   own current intended meaning is, agreeing with or deliberately
   diverging from an unchanged Claim).
6. Once `domain-skeptic` finds no unresolved contradiction it cannot
   either fix or correctly characterize as a genuine open question, and
   every escalation has either a recorded user ruling or an honest,
   still-open entry in `docs/domain/open-questions.md`, the corpus is
   **approved** and published as durable Markdown under `docs/domain/`
   — approval never requires every open question to be closed, only
   that none was silently closed by the wrong party.

## 3. `docs/domain/` layout

```
docs/domain/
  README.md          — index: what this directory is, how to read it,
                        how it relates to architecture/ and docs/
  glossary.md         — one-paragraph definition per concept, cross-
                        linked; the first thing a newcomer (human or
                        agent) should read
  concepts/
    evidence.md
    observation.md
    claim.md
    derivation.md
    provenance.md
    relationship-edge.md
    context.md
    context-packet.md
    adapter.md
    connector.md
    protocol.md
    reference.md
    decision.md
    invariant.md
    <any further concepts context-researcher's own investigation
     surfaces, per §1>
  invariants.md        — cross-cutting rules that hold across multiple
                         concepts (pulled up from individual concept
                         docs where a rule isn't concept-local)
  examples.md           — worked examples and counterexamples that don't
                         fit naturally inside one concept's own page
  open-questions.md     — every genuinely unresolved ambiguity, its
                         evidence, its alternatives, and (once ruled on)
                         its resolution — never deleted once answered,
                         only marked resolved with a pointer to the
                         Decision record
  references.md         — pointers into the actual evidence trail (which
                         ADR, plan, retro, source file, or test grounds
                         each concept's own definition) — this file is
                         what makes every claim in this corpus
                         traceable back to primary evidence, matching
                         Phase 54c's own provenance discipline
```

Each `concepts/<name>.md` file has a consistent shape: definition,
what it is NOT (explicit disambiguation from its nearest neighbors),
invariants, example, counterexample/edge case (or an honest "none found
yet"), relationships to other concepts, and a references block
(pointers into `planning/knowledge/codecompass-domain/`'s own
Evidence/Claim ids, and into the real source/ADR/test locations those
ids themselves cite).

A machine-readable concept registry (Phase 54c's own YAML shapes,
already used for the underlying `planning/knowledge/codecompass-domain/`
records) is the existing mechanism for anything a script might someday
want to parse; `docs/domain/`'s own Markdown is never regenerated from
YAML mechanically as part of this phase — it is written by
`context-researcher`/the lead from the approved knowledge base, the
same "projection, not the same file, but never contradicting it" stance
`design.md` already takes toward its own knowledge base
(`phase-54c-evidence-knowledge-workflow.md` §4).

## 4. New role: `domain-skeptic`

Independent. Never produces or repairs the corpus it reviews — reports
findings back (mirrors `docs-reconstructor`/`release-phase-auditor`'s
own posture). Given a domain-corpus draft (or, in later Design-stage
use, a `design.md`):

- Checks every material claim for a citable Observation/Evidence
  record; flags any that has none.
- Actively searches for contradictions — between two concept pages in
  the same corpus, or between the corpus and directly-checkable source/
  test/ADR content.
- Actively searches for missing edge cases/counterexamples a concept
  page's own definition would predict should exist, but doesn't
  mention.
- For each finding, attempts resolution first (dispatch/point
  `context-researcher` at a specific further check, or run one
  directly — a grep, a real command, a test) before treating it as
  something to escalate.
- Escalates only what genuinely cannot be resolved by more evidence —
  a real domain/product ambiguity — presented concisely to **the
  actual user/domain owner**: the concept, the evidence so far, the
  real alternatives, and the consequence of each. **`domain-skeptic`
  itself never rules on a genuine ambiguity** — it either resolves an
  item fully with evidence (at which point it is no longer an
  ambiguity) or escalates it and leaves it open pending the user; it
  has no third option of deciding on the user's behalf.

**Write boundary, stated precisely (amendment, 2026-09-20)**:
`domain-skeptic` is **read-only with respect to source code, `src/`
implementation, `design.md`/design content, and the approved domain
corpus itself (`docs/domain/`)** — it never edits any of these, under
any circumstance, including to fix something it finds wrong. It may
**only**:

1. **Append** new Observation/Evidence records under
   `planning/knowledge/codecompass-domain/` when it resolves a finding
   through a check it runs itself (a grep, a real command, a test) —
   same record shapes, same write boundary `context-researcher` already
   has; `domain-skeptic` gets no different Observation/Evidence format
   for checks it runs itself, and never writes a Claim, Derivation, or
   Decision record (those require either `context-researcher`'s own
   fuller derivation work or the actual user's own ruling, never
   `domain-skeptic`'s unilateral say-so).
2. **Write its own review findings**:
   `planning/retros/_domain-skeptic-review-phase-63d.md` (mirroring
   `docs-reconstructor`'s own `_drift-audit-phase-N.md` naming).

Tools: Read, Grep, Glob, Bash (read-only invocations against source/
implementation: `codecompass query`, tests, greps — no `sync`/`--yes`,
no `enrich apply`, no `src/codecompass/` writes, no edits to
`docs/domain/`), Write (scoped to exactly the two outputs above).

## Scope

**In scope:**
- `planning/knowledge/codecompass-domain/` — Observation/Evidence/
  Claim/Derivation/Decision records for every concept in §1, produced
  by `context-researcher`.
- `.claude/agents/domain-skeptic.md` (new agent file) — the role
  described in §4, cataloged in advance by `decisions/0060` and
  `agent-led-development.md` §2.13.
- `docs/domain/` (new directory) — the approved, durable Markdown
  corpus per §3's layout.
- `planning/retros/_domain-skeptic-review-phase-63d.md` — the
  independent review report.
- The normal phase retro
  (`planning/retros/phase-63d-domain-reconstruction.md`), `CG`/learning
  triage if this phase's own review surfaces any, `docs-reconstructor`
  drift audit (scoped: does anything in `docs/domain/` misdescribe
  current `README.md`/`docs/`/`architecture/`/`ai-docs/` content, or
  vice versa?), and `release-phase-auditor` DoD pass.
- `planning/ROADMAP.md`/`planning/CONTEXT.md`/`CHANGELOG.md` updates
  marking this phase done, once it is.

**Explicitly deferred / out of scope:**
- Rewriting `architecture/overview.md`, `README.md`, or any existing
  ADR content — Phase 64/65's own job, consuming this phase's output.
- Building `docs/domain/` content for any project other than
  CodeCompass itself.
- Resolving GATE DD or funding Stage E.
- Any `src/codecompass/` change — this phase produces documentation and
  evidence records only; if `context-researcher`'s own investigation
  surfaces a real code-level gap (matching this project's own
  `context-gaps` precedent), it is filed to `planning/context-gaps/inbox.md`
  exactly like any other phase's incidental finding, not fixed inline.

## Design decisions

- **Reuse Phase 54c's record shapes unchanged, applied project-wide.**
  No new schema — a new schema would be exactly the kind of
  "speculative generalisation ahead of evidence" this project's own
  discipline warns against, and Phase 54c's retro already found the
  six kinds held up cleanly under real use.
- **`domain-skeptic` is a new, narrow role, not a `context-researcher`
  self-review or a `knowledge-curator` extension.** Matches
  `decisions/0054`'s precedent: a genuinely different job (adversarial
  challenge of already-produced content) from either existing role's
  own brief (primary investigation; queue triage).
- **`docs/domain/` is Markdown-primary, YAML-secondary** — per the
  user's own explicit instruction. The YAML records already exist for
  provenance/traceability; the Markdown is what a human or a
  general-purpose agent actually reads.
- **Escalate only genuine ambiguities, not every open Claim.** A Claim
  correctly marked `contradicted` or left with an honestly-unresolved
  edge case is not automatically an escalation — only cases
  `domain-skeptic` cannot make further evidence-based progress on
  reach the actual user/domain owner, matching Phase 54c's own "don't
  paper over a real gap, but don't manufacture escalations either"
  posture.
- **No agent or lead stand-in for the user on a genuine escalation**
  (amendment, 2026-09-20 — narrows Phase 54c's own §5.1 precedent,
  which allowed the lead to stand in during CodeCompass's own
  dogfooding; that allowance does not carry forward to this phase). An
  agent may only fully resolve an item with evidence (making it no
  longer an escalation) or leave it explicitly open
  (`docs/domain/open-questions.md`) — never rule on it in the user's
  place.

## Files

- `planning/knowledge/codecompass-domain/*.yaml` (new — Observation/
  Evidence/Claim/Derivation/Decision records, one set per concept or
  cluster).
- `docs/domain/README.md`, `docs/domain/glossary.md`,
  `docs/domain/concepts/*.md`, `docs/domain/invariants.md`,
  `docs/domain/examples.md`, `docs/domain/open-questions.md`,
  `docs/domain/references.md` (new).
- `.claude/agents/domain-skeptic.md` (new).
- `planning/retros/_domain-skeptic-review-phase-63d.md` (new).
- `planning/retros/phase-63d-domain-reconstruction.md` (new, the phase
  retro).
- `planning/retros/_drift-audit-phase-63d.md`,
  `planning/retros/_audit-phase-63d.md` (new — the standard per-phase
  independent audits, written to their standard location from the
  start, closing the gap found during Phase 62's own closeout
  consistency check).
- `planning/ROADMAP.md`, `planning/v1-redefinition/roadmap.md`,
  `planning/CONTEXT.md`, `CHANGELOG.md` (status flip to done).

## Verification

- Every concept named in §1 has a `docs/domain/concepts/<name>.md` page
  with all of: definition, disambiguation from neighbors, invariants,
  example, counterexample/edge case (or explicit "none found"),
  relationships, and a references block resolving to real
  Evidence/Claim ids and real source/ADR/test locations — spot-checked
  directly (open the cited file/line, confirm it says what the concept
  page claims).
- `domain-skeptic`'s own review report exists, names what it checked,
  what it resolved itself (with the new Observation/Evidence it
  produced), and what it escalated (if anything) — and every escalation
  either has a corresponding **actual user/domain owner** ruling
  recorded as a Decision record, or is honestly recorded as still open
  in `docs/domain/open-questions.md` — never a ruling made by the lead
  or any agent standing in for the user.
- No concept page's own Claims rest solely on "a doc says so" —
  independently confirm at least one concept page's own central claim
  by checking its cited source/test directly, not merely trusting the
  page (the lead does this for at least 2-3 concepts as a spot audit,
  matching this project's own "verify independently, every time" rule,
  `agent-led-workflow.md`'s opening line).
- `python scripts/check_user_docs.py --strict` — extended if useful to
  check `docs/domain/` internal links resolve (matching its existing
  "internal links resolve" check for `docs/`), not required to gain new
  concept-specific checks this phase doesn't itself need.
- Standard DoD: `docs-reconstructor` drift audit (NO DRIFT expected,
  scoped narrowly — this phase adds a new directory, it should not
  make any *existing* current-truth doc newly false), phase retro,
  learning triage, `release-phase-auditor` pass (`PASS` or `PASS WITH
  NON-BLOCKING OBSERVATIONS` required before Phase 64 begins).

## Done when

- `docs/domain/` exists, approved, with every concept in §1 (plus
  whatever `context-researcher` genuinely found along the way)
  documented per the Verification section above.
- Every escalated ambiguity has either a recorded actual-user ruling or
  an honest, still-open entry in `docs/domain/open-questions.md` — none
  was resolved by the lead or any agent standing in for the user.
- `domain-skeptic`'s review found no remaining unresolved contradiction
  it could not either fix or correctly characterize as an open
  question.
- The retro, drift audit, learning triage, and `release-phase-auditor`
  pass all exist and the auditor's verdict is `PASS` or `PASS WITH
  NON-BLOCKING OBSERVATIONS`.
- `planning/ROADMAP.md`/`planning/v1-redefinition/roadmap.md`/
  `planning/CONTEXT.md`/`CHANGELOG.md` all mark this phase done, and
  Phase 64's own plan (written when Phase 64 actually starts) can
  reference `docs/domain/` as an existing, approved input rather than
  needing to rediscover it.

## Review gate

Flagged for explicit review before implementation begins, per
`CLAUDE.md` §1:

1. **The `domain-skeptic` role is new** — a fourth "independent review"
   role alongside `context-evaluator`/`docs-reconstructor`/
   `release-phase-auditor`. Confirmed not redundant with any of them
   (§4, Design decisions) but worth the reviewer's own explicit
   agreement before a fourth such role is created.
2. **`docs/domain/` as a new top-level durable directory**, sibling to
   `docs/`/`architecture/`, rather than a subdirectory of one of them
   (e.g. `docs/domain/` vs. `architecture/domain/`). Chosen because the
   user's own request named `docs/domain/` directly and because this
   content is neither "how to use CodeCompass" (`docs/`) nor "how
   CodeCompass is implemented" (`architecture/`) but a third, distinct
   thing both of those depend on — flagged for confirmation, not
   assumed uncontroversial.
3. **Scope boundary**: this phase produces evidence/documentation only,
   never a `src/codecompass/` change, even if `context-researcher`'s
   own investigation surfaces a real code-level gap (routed to
   `context-gaps/inbox.md` instead, per existing practice) — confirmed
   consistent with the user's own framing ("dogfood CodeCompass against
   its own repository," not "extend CodeCompass").
