# Phase 79 — Clean-room conceptual understanding + documentation reconstruction (methodology hardening + template delivery)

**Status: planned. Planning only — implementation (dispatching agents,
building exports, touching either repository's real content) does not
begin until this plan is reviewed and approved.**

Direct user request, 2026-09-30. Full initiating prompt saved verbatim:
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction-prompt.md`.
Governing ADR: `decisions/0066`.

---

## 0. Verified current state (read live for this plan)

- **CodeCompass HEAD:** `d241268` on `main`, working tree clean (before
  this commit). Phase 78 (Priority A backlog rationalisation + second
  Ledgerkit trial) is `planned`, twice-amended, **not yet executed** —
  this phase does not touch, reorder, or depend on it. Phases 71-77 are
  `done`.
- **No existing planned clean-room documentation phase found.** Searched
  `planning/ROADMAP.md`, `planning/CONTEXT.md`, `decisions/`,
  `planning/v1-redefinition/`, `planning/context-gaps/inbox.md`,
  `planning/learnings/inbox.md` for "clean-room"/"concept-understanding"/
  "independent implementation reconstruction" — no hits. This is a new
  phase, not an amendment to a competing one.
- **Closest prior art, read in full**: `decisions/0060` (names Scope →
  Plan → Domain → Design → Implement; adds `context-researcher`,
  `domain-skeptic`); `planning/phase-63d-domain-reconstruction.md`
  (done — built `docs/domain/`, the project's own approved domain
  corpus, via `context-researcher` + `domain-skeptic` + real human/
  domain-owner review); `planning/phase-64-blank-slate-documentation-
  reconstruction.md` (done — `docs-reconstructor` MODE 2 derived a
  shadow doc proposal under `planning/v1-docs-reconstruction/` from
  current project reality); `planning/phase-65-architecture-adr-
  reconciliation.md` (done — lead + `docs-maintainer` compared the
  shadow proposal against active docs, decided retain/rewrite/
  consolidate/split/replace/remove per document).
- **A real, disclosed gap found by direct inspection of that prior art**
  (the driving finding behind `decisions/0066`): `.claude/agents/
  docs-reconstructor.md` MODE 2's own text says it is "read-only toward
  src/tests/current docs" — meaning it retains full read access to
  `docs/`/`README.md`/`architecture/` while being *told* not to treat
  them as a starting structure. `planning/v1-redefinition/agent-led-
  development.md`'s own write-boundary table states `context-researcher`'s
  read scope as literally "everything." Neither is mechanically isolated
  from legacy narrative — the isolation is a dispatch-prompt instruction,
  not an enforced boundary. No boundary-verification step, no persisted
  access-log, no breach-detection/restart protocol exists anywhere in the
  current mechanism.
- **The existing Claim record schema**, read directly
  (`planning/knowledge/codecompass-domain/CL-ADPT-002.yaml` and others):
  `id`, `kind`, `statement`, `derivation`, `supporting_evidence`,
  `contradicting_evidence`, `derived_by`, `repository_revision`,
  `timestamp`, `status` (`supported`/`superseded`), `supersedes`. No
  `assertion_kind` taxonomy, no `basis` field, no `examples`/
  `counterexamples`, no `depends_on`, no `open_questions`, and — the
  specific gap the user's own instruction names — **no separate
  human-review-state field**; `status` conflates evidence-support with
  record lifecycle, and human review is currently tracked only at
  whole-page granularity (`docs/domain/concepts/*.md`'s own frontmatter,
  `status: APPROVED (date, actual user/domain owner)`), never per
  assertion.
- **`docs-maintainer`/Phase 65's own reconciliation precedent**: lead +
  `docs-maintainer`, comparing a shadow proposal against active docs, no
  new role — reused here, extended with an explicit historical-claim
  classification taxonomy (§8.3) and a strict draft-before-reconciliation
  ordering rule the prior phase did not need (Phase 64's proposal and
  Phase 65's reconciliation were already sequential phases; this phase
  makes the ordering an explicit, checked gate within one phase).
- **`codecompass-template`** (cloned fresh for this plan,
  `https://github.com/ctosullivan/codecompass-template`, current default
  branch, 13 tracked files): `README.md`, `LICENSE` (MIT), `CLAUDE.md`,
  `vendor.toml`, `.gitignore`, `docs/architecture.md`,
  `decisions/{README.md,TEMPLATE.md}`, `planning/ROADMAP.md`,
  `planning/CONTEXT.md`, `planning/retros/TEMPLATE.md`,
  `planning/knowledge/README.md` (currently a lightweight, generic
  learnings-log concept — **not** the Observation/Evidence/Claim model in
  any form), `planning/context-gaps/README.md`. No existing template
  content anywhere describes an understanding-assertion, review-packet,
  implementation-comparison, or documentation-verification workflow.
- **Priority A/D context** (`decisions/0062`, `planning/ROADMAP.md`):
  Priority D's own success criterion ("a downstream user can follow
  research→evidence map→design→review→packet→implementation→
  verification→retro→knowledge-update using only already-shipped
  CodeCompass surfaces plus documented convention, no new agent
  required") is what this phase's template deliverable directly serves.
  Priority B ("lightweight claim/evidence/contradiction model... for a
  *downstream user's own project*") is explicitly **not** this phase —
  see §2 and `decisions/0066` item 6 for the drawn line.

## 1. Problem statement

CodeCompass has run the Domain/Design stages of its own methodology for
real (Phase 63D's domain corpus; countless per-feature `design.md`s) and
has run a blank-slate documentation derivation for real (Phase 64/65).
Both worked. Neither is mechanically isolated from the material it is
instructed to disregard, neither produces a formally comparable
"independently reconstructed implementation" artifact checked against
the reviewed conceptual model in both directions, and the record schema
that carries a domain concept's evidence has no field distinguishing
"the evidence supports this" from "a human has actually looked at this."
This phase closes those three specific gaps — not by inventing a new
subsystem, but by extending the record shape that already exists,
introducing one genuinely new, narrowly-scoped agent role, hardening two
existing roles' own input boundaries mechanically, and reusing every
other mechanism (the supersedes-chain, the observable-research-trace
discipline Phase 78 just established, the append-in-place curation-note
pattern `context-gaps/inbox.md` already uses) rather than duplicating
them.

The exercise is proven once, on one real, bounded, currently-uncovered
CodeCompass topic, and packaged as a portable, CodeCompass-agnostic
workflow for `codecompass-template` — not applied retroactively to the
whole `docs/domain/` corpus or the whole `planning/v1-docs-reconstruction/`
proposal, which would be disproportionate to what this phase needs to
demonstrate.

## 2. Goals, non-goals, and the Priority B distinction

**Goals:**

1. Extend the existing Observation/Evidence/Claim/Derivation record
   shape with the fields needed to carry a stable-ID, kind-classified,
   evidence-and-basis-labelled, dependency-aware, separately
   evidence-supported/human-reviewed assertion — reusing the shape, not
   replacing it (§3).
2. Produce a human-readable understanding-review packet, rendered from
   the assertion records, for one real, bounded CodeCompass topic — with
   a real review gate, real recorded corrections, and a published,
   versioned, cited snapshot (§4).
3. Design and build genuinely mechanical (not prompt-only) isolation for
   four distinct evidence scopes, with a persisted manifest, an
   observable trace, a boundary-verification check, and a breach/restart
   protocol (§5).
4. Independently reconstruct the as-built implementation for the same
   topic, from primary evidence only, before comparing it against the
   reviewed understanding — then classify alignment honestly in both
   directions (§6).
5. Produce a complete, legacy-blind first documentation draft for the
   topic, preserve it, then reconcile legacy material against it — never
   the reverse order (§7).
6. Run a fresh documentation-only question exercise against the new
   docs, and independently verify the preserved answers against real
   repository evidence (§7.4).
7. Add the minimal, evidence-graph-reusing dependency tracking needed to
   show a source change's downstream consumers without a new database
   (§9).
8. Deliver a portable, CodeCompass-agnostic version of the whole
   workflow to `codecompass-template`, with explicit guidance for a
   downstream project whose own tools cannot enforce a hard boundary
   (§10).

**Non-goals (explicitly out of scope this phase):**

- No `src/codecompass/` change, no `context-graph.db` schema change, no
  new database, no graph subsystem, no comprehensive ontology — per the
  user's own explicit instruction and `decisions/0066` item 6.
- No re-application of the hardened workflow to the whole `docs/domain/`
  corpus or the whole `planning/v1-docs-reconstruction/` proposal. One
  topic, proven once, this phase.
- No change to Phase 78's own scope, ordering, or execution — that plan
  stands unmodified and unblocked by this one.
- No numerical confidence scores anywhere in the assertion schema or the
  review packet, per the user's own explicit instruction.
- No fabricated or lead-stood-in human review. Every review gate below
  names the actual required reviewer; completion is explicitly pending
  wherever that reviewer has not yet acted (§11).

**This is not Priority B — the line, stated once, precisely** (per
`decisions/0066` item 6): Priority B is a future, not-yet-planned
capability of the *shipped* `codecompass` tool — a runtime, `src/`-level
change letting a *downstream user* record and query claims about *their
own* project's data through the tool itself. This phase makes zero
`src/` changes; every artifact is a planning document, a `docs/domain/`
page, an agent brief, or a `codecompass-template` file. It hardens and
self-applies CodeCompass's own **development methodology**
(`decisions/0060`), delivers a Priority D template artifact, and
produces evidence relevant to Priority B's eventual planning — it is not
that planning, and does not pre-empt it.

## 3. Assertion record schema (extends the existing Claim shape)

No new record kind. `Observation`/`Evidence`/`Derivation` are unchanged.
A Claim record used as a project-understanding **assertion** gains these
optional fields (omitted entirely for an ordinary feature-scoped Claim
that isn't part of an understanding-review exercise, so nothing about
existing `planning/knowledge/codecompass-domain/*.yaml` files needs
migrating):

| Field | Values / shape | Purpose |
|---|---|---|
| `assertion_kind` | `definition` \| `relationship` \| `rule` \| `invariant` \| `state_transformation` \| `boundary` | What *kind* of statement this is — the user's own required taxonomy. |
| `basis` | `directly_stated` \| `inferred` \| `proposed_policy` \| `observed_behaviour` | How the statement was arrived at — reuses `development-methodology.md`'s existing "documented intent ≠ implemented behaviour ≠ historical decision ≠ current intended meaning ≠ unresolved uncertainty" distinction, made a structured field instead of prose-only. |
| `examples` | list of short strings/citations | Concrete cases that illustrate the assertion. |
| `counterexamples` | list of short strings/citations | Cases that test or bound it — required whenever a plausible one exists; an empty list is a claim "none found," not "not considered." |
| `depends_on` | list of assertion IDs | Explicit dependency edges between assertions, reusing the same ID-citation mechanism `supporting_evidence`/`derivation` already use — not a new graph, a new *use* of an existing field shape. |
| `open_questions` | list of short strings | Genuinely unresolved matters — distinct from `contradicting_evidence` (evidence exists and conflicts) and from an ordinary gap (no evidence yet); this is "we looked, and a real question remains." |
| `evidence_support_state` | `supported` \| `partially_supported` \| `unsupported` \| `conflicting` | Whether the *evidence* backs the statement — independent of whether a human has reviewed it. |
| `human_review_state` | `unreviewed` \| `accepted` \| `qualified` \| `rejected` \| `superseded` | Whether the *actual reviewer* has acted on it — independent of evidence quality, per the user's own explicit instruction that these are different facts. Defaults to `unreviewed`; only the real reviewer (§4.3) ever sets it to anything else. |

**No numerical confidence score anywhere in this table** — `evidence_support_state`
and `human_review_state` are closed, small enums, never a number, per the
user's own explicit instruction.

`status` (`current`/`superseded`) keeps its existing meaning (record
lifecycle) and is not renamed — `human_review_state: superseded` and
`status: superseded` are set together, at the same moment, for the same
reason (a correction produced a replacement record), never independently.

This schema extension is documented once, in
`development-methodology.md`'s own Domain section (§12 below), not
duplicated into a second schema document.

## 4. Understanding-review packet, human review gate, and snapshot

### 4.1 The review packet (rendered, not hand-authored)

For the validation topic (§13), `context-researcher` produces the
assertion records (§3) under `planning/knowledge/<topic-slug>/`, then a
single rendered Markdown packet, `planning/knowledge/<topic-slug>/
understanding-review.md`, containing exactly the sections the user's own
instruction names: topic scope and source coverage; concepts and
relationships in plain language; rules, boundaries, exceptions, and
transformations; worked examples that test the interpretation;
alternative interpretations and unresolved decisions (from
`open_questions`); focused questions for the human reviewer; and an
evidence appendix mapping every material statement to its assertion ID
and source citation. A diagram (Mermaid, inline Markdown) is used only
where it clarifies a relationship the prose already states — the packet
is read top-to-bottom by a human, never a raw record dump or a request to
audit a graph.

### 4.2 Adversarial review before the human sees it

`domain-skeptic` reviews the packet exactly per its existing charter
(`agent-led-development.md` §2.13, unchanged): challenges every
assertion lacking a citable Evidence record, hunts for internal
contradictions and missing counterexamples, resolves what it can itself
(a grep, a real command, a re-dispatch of `context-researcher` at a named
sub-question), and only then hands the packet forward — with every
remaining `open_questions` entry intact, never quietly resolved on the
packet's behalf.

### 4.3 The human review gate — named precisely

**Reviewer: the actual user/domain owner — the same standing established
at Phase 63D, never the lead, never any agent standing in
(`development-methodology.md`'s "no stand-in" rule, unchanged, reused
here exactly).** The packet is presented; the reviewer records, per
assertion, a disposition: `accepted` (as stated), `qualified` (accepted
with a stated correction), `rejected` (the assertion is wrong), or
`superseded` (a different assertion replaces it). Every correction is
recorded in `planning/knowledge/<topic-slug>/review-decisions.md` —
reusing `context-gaps/inbox.md`'s own append-in-place curation-note
format (date, reviewer, assertion ID, disposition, rationale), not a new
log format. A `rejected` or `superseded` disposition produces a **new**
Claim record whose `supersedes` field names the old one (the existing
Domain-stage re-entry mechanism, `development-methodology.md`'s own
"Traceability without silent rewriting" section — reused, not
duplicated); the old record stays on disk, `status: superseded`,
`human_review_state: superseded`, permanently citable.

**This gate is not fabricated and is not optional for completion.**
During execution, the packet (§4.1) plus `domain-skeptic`'s own review
(§4.2) are completed *before* the review request is made — matching the
user's own explicit instruction. Every assertion not yet acted on by the
real reviewer stays `human_review_state: unreviewed`, visibly, in both
the record and the rendered packet — never silently treated as accepted.
If the review has not genuinely occurred by the time this phase's own
Definition of Done is checked, **the phase is not done** (§11).

### 4.4 The published snapshot

Once review is complete (or the reviewer has explicitly deferred specific
items, recorded as such — not silently dropped), a snapshot is published:
`planning/knowledge/<topic-slug>/understanding-snapshot-v1.md`, naming
its own scope, the exact source revisions it was built against, every
`accepted`/`qualified` interpretation, and every item still genuinely
open. Every later design, doc, or comparison in this phase (and any
future phase) cites `<topic-slug>@snapshot-v1` plus the specific
assertion IDs it relies on — never the live, mutable record store
directly, so a later correction (§9) has a stable prior version to be a
correction *of*.

## 5. Mechanical isolation — four scopes, one mechanism

**Mechanism** (per `decisions/0066` item 3): a curated, `.git`-free
filesystem export, built from an explicit allow-list manifest, placed
under the session scratchpad — never inside either repository's own
tracked tree — with no `.git` directory (so there is no history path to
excluded material) and no disclosure, in the dispatch prompt, of the main
checkout's own path (so there is no filesystem path back to it either).
This is `decisions/0066`'s own disclosed, honestly-scoped mechanism — not
a claim of OS-level sandboxing this project's tools cannot build.

| Scope | Permitted inputs | Explicitly excluded |
|---|---|---|
| **Understanding reconstruction** | `decisions/*.md` relevant to the topic; the relevant phase plan file(s)' own Scope/Problem-statement/Decision sections (labelled, in the export's own manifest header, as intent/rationale evidence, never proof of current behaviour); `src/codecompass/` and `tests/` for the topic's own files (needed to ground assertions in real evidence, not narrative); existing `docs/domain/` pages only if the topic genuinely extends one (named explicitly in the manifest, not a blanket allowance) | `README.md`, `docs/` (outside `docs/domain/`), `architecture/`, `ai-docs/`, `CHANGELOG.md`, any prior `planning/retros/*.md` narrative prose, any unsupported inherited summary |
| **Implementation reconstruction** | `src/codecompass/` (topic-relevant modules), `tests/` (topic-relevant), the relevant `graph.py` schema fragment, `pyproject.toml`, `vendor.toml` schema, CI/build config, real generated artifacts (a real `vendor/`, a real synced `context-graph.db` for the topic), runtime observation (`codecompass --help`, real command output) | **All** narrative documentation (`README.md`, `docs/`, `architecture/`, `ai-docs/`, ADRs) and, critically, the Understanding snapshot itself — this stage must not see the reviewed model before independently reconstructing what the code does |
| **Documentation writing** | The published, reviewed Understanding snapshot (§4.4) + its cited assertion IDs; the Implementation-reconstruction report + alignment classification (§6); an approved documentation-architecture outline (§7.1) | All legacy narrative documentation, unconditionally, until §7.3's reconciliation stage |
| **Legacy reconciliation** | Everything from the Documentation-writing scope, **plus** the legacy narrative documentation it was withheld from until now | Nothing withheld at this stage — this is the one scope where full access is correct, precisely because the clean-room draft it will be compared against is already committed and cannot be silently rewritten by what this stage sees |

**Per-dispatch, persisted (under `planning/knowledge/<topic-slug>/
isolation/`):**

- `<scope>.manifest` — the exact allow-list used to build that scope's
  export, and the source revision each file was taken at.
- `<scope>.access-log.md` — the dispatched agent's own observable
  research trace (files read, searches run, commands executed — reusing
  Phase 78's own §5.3.4 convention verbatim, not a second format).
- `<scope>.boundary-check.md` — a mechanical post-hoc check: does the
  export's own file listing match the manifest exactly (nothing extra
  slipped in), and does the access-log ever name a path outside the
  export directory (it structurally cannot, if the export is genuinely
  isolated and the trace is honest — this check exists to catch a
  process error in building the export, not to police the agent).

**Breach protocol**: if a boundary-check finds an export containing an
unlisted file, or a trace naming an out-of-scope path, that stage's own
output is discarded, the export is rebuilt correctly, and a fresh agent
re-runs the stage. **No stage's output is ever treated as clean-room
after a detected breach, retroactively rationalized as harmless.** This
is a named, checked Definition-of-Done condition (§11), not a best-effort
aspiration.

**Disclosed limitation, stated once, honestly**: this mechanism prevents
an agent from having a *readable path* to excluded content; it does not
prevent a sufficiently adversarial tool call from attempting to escape
the export directory (e.g. `cat ../../original-repo/README.md` if the
agent somehow guessed the relative path). No control in this phase
detects that specific attempt in real time — only after the fact, via the
access-log review. This is disclosed, not hidden, and is exactly the
"what to do when your tools cannot fully enforce it" case the template
(§10) must also document for downstream projects with even fewer
controls available.

## 6. Independent implementation reconstruction and comparison

### 6.1 New role: `implementation-reconstructor`

**Charter**: given only the Implementation-reconstruction export (§5),
recover the as-built architecture — covering, at minimum, modules, APIs/
CLI surface, data and persistence (schema, migrations), dependencies,
runtime paths (what actually executes when a command runs), extension
points, build/configuration, tests (what they actually assert), and
known limitations (what the evidence shows is *not* handled). Output:
`planning/knowledge/<topic-slug>/implementation-reconstruction.md`. No
access to the reviewed Understanding snapshot at this stage — the point
is a reconstruction uninfluenced by what the concept model claims,
checked against it only afterward.

**Write boundary**: its own report only, plus (if it needs to run a real
command to confirm something — e.g. `codecompass query source-symbol` on
a live synced database inside its own export) no other write access.
**Tools**: Read, Grep, Glob, Bash (read-only — no `sync --yes` against
anything outside its own export, no `enrich apply`, no `src/` writes).

Not created by this planning phase — its `.claude/agents/
implementation-reconstructor.md` file is this phase's own implementation
deliverable (§14), matching how `domain-skeptic` was planned at
`decisions/0060` and built at Phase 63D.

### 6.2 Comparison and classification — extends `domain-skeptic`, not a second new role

Once the as-built report (§6.1) is frozen (committed), a **fresh**
`domain-skeptic` dispatch (not the same instance that reviewed the
Understanding packet, to avoid anchoring either direction) receives both
the reviewed Understanding snapshot (§4.4) and the frozen as-built report,
and classifies every relevant behaviour named in either artifact:

- **`aligned`** — the reviewed assertion and the as-built evidence agree.
- **`partial`** — they agree on part of the behaviour, diverge on a
  specific, named part.
- **`conflicting`** — they genuinely disagree; neither side is silently
  preferred.
- **`not_implemented`** — the assertion describes intended/proposed
  behaviour (per its own `basis` field) that the as-built evidence shows
  does not exist.
- **`insufficiently_verified`** — neither artifact has enough evidence to
  classify confidently; recorded honestly as such, not forced into one of
  the other four.

**Neither the Understanding model nor the Implementation reconstruction
is silently revised to force agreement** — per the user's own explicit
instruction. A `conflicting` or `not_implemented` finding produces a
recorded discrepancy (`planning/knowledge/<topic-slug>/alignment-report.md`),
which becomes a new `open_questions` entry on the relevant assertion (for
the actual reviewer, next time the topic is revisited) and a flagged
section in the documentation-writing stage's own approved outline (§7.1)
— it does not retroactively edit the already-published Understanding
snapshot (which stays versioned and immutable) or the frozen as-built
report.

## 7. Clean-room documentation reconstruction and legacy reconciliation

### 7.1 Documentation-architecture outline (before writing starts)

A short outline (arc42/C4-inspired architecture views; Diátaxis-style
categories for user-facing content — used selectively, only where they
clarify, per the user's own "selectively where useful" instruction, not
adopted wholesale as a mandatory template) is drafted from the reviewed
Understanding snapshot and the alignment report, and approved (lead
review — this is a structural/editorial call, not a domain-truth
question, so it does not require the actual user/domain-owner gate §4.3
already used) before any writing dispatch happens.

### 7.2 Clean-room first draft

`docs-reconstructor` MODE 2, dispatched into the Documentation-writing
export (§5), produces the complete first draft under
`planning/v1-docs-reconstruction/<topic-slug>/` (reusing the existing
shadow-proposal location, not a new one), clearly distinguishing — per
the user's own instruction — domain concepts (cite the Understanding
snapshot), project policies (cite the relevant Decision/ADR, labelled as
intent/rationale), supported behaviour (cite the alignment report's
`aligned`/`partial` findings), and future intentions (cite
`not_implemented` findings explicitly as such, never presented as
current). **This draft is committed to `main` before the next step
begins** — the mechanical ordering gate named in §11.

### 7.3 Legacy reconciliation — only after the draft is preserved

`docs-maintainer` (+ the lead, Phase 65's own precedent, no new role),
now given full access to both the preserved clean-room draft and the
legacy narrative documentation, classifies every relevant historical
claim in the legacy docs:

- **`supported`** — the legacy text is still accurate; the clean-room
  draft already says the same thing, or is silently missing a true
  detail worth folding in.
- **`stale_or_contradicted`** — the legacy text is now wrong; not
  restored.
- **`rationale_requiring_verification`** — the legacy text states a
  *reason* for something that needs checking against real evidence
  before being trusted (a documented-intent claim, not yet a Claim
  record) — becomes a `context-researcher` follow-up question if worth
  pursuing, not silently accepted.
- **`useful_example`** — a concrete illustration worth keeping even
  though the surrounding prose isn't authoritative — re-grounded in
  evidence before being folded into the clean-room draft, never copied
  verbatim on the strength of having existed.
- **`obsolete`** — describes something no longer true or no longer
  present; recorded, not restored.

**Re-grounding, not default restoration**: any legacy claim folded into
the final documentation must cite real evidence (a Claim ID, a source
citation, a test) at the point it's incorporated — "it was already in the
old docs" is never itself the citation. Output:
`planning/v1-docs-reconstruction/<topic-slug>/reconciliation.md`
(Phase 65's own file-naming precedent, scoped to this topic).

### 7.4 Documentation-only answering and independent verification

A fresh `general-purpose` agent, given read access to *only* the final
(post-reconciliation) documentation tree for the topic — no `src/`, no
tests, no other docs — is asked a set of real, user-relevant questions
about the topic and answers using only what it can read. Its answers are
preserved verbatim (`planning/knowledge/<topic-slug>/documentation-qa.md`).
**`context-evaluator`**, reused unchanged (its existing charter already
is "inspect the target directly, establish ground truth independently"),
then independently checks each preserved answer against real repository
evidence, recording: correct / unsupported claim / missing information /
ambiguous — persisted as
`planning/knowledge/<topic-slug>/documentation-qa-verification.md`. No
new agent role for either step.

## 8. Reused mechanisms — named explicitly, not re-derived

To keep this phase's own footprint minimal (per its own non-goals, §2):

- **Evidence-layer separation** (Knowledge sources / Project understanding
  / Implementation evidence) is `development-methodology.md`'s existing
  "documented intent ≠ implemented behaviour ≠ historical decision ≠
  current intended meaning ≠ unresolved uncertainty" distinction, made
  structural via the `basis` field (§3) rather than prose-only.
- **The supersedes-chain and re-entry rules** (§4.3, §6.2) are
  `development-methodology.md`'s own "Traceability without silent
  rewriting" section, unchanged.
- **The observable-research-trace requirement** (§5) is Phase 78's own
  §5.3.4, reused verbatim, not a second format.
- **The append-in-place curation-note convention** (§4.3's
  `review-decisions.md`) is `context-gaps/inbox.md`'s own established
  pattern.
- **ADRs as intent/rationale evidence, not behaviour proof** (§5's
  manifest labelling) is already this project's own working assumption
  (every ADR here records a decision *at the time*, never a live claim
  about current code) — made an explicit, checked manifest label rather
  than an implicit convention.

## 9. Versioning and downstream propagation (minimal, evidence-graph-reusing)

No new dependency database. When a source change affects an assertion:

1. The affected assertion(s) are found the same way any citation is found
   today — `grep` for the assertion ID across
   `planning/knowledge/**`, `planning/v1-docs-reconstruction/**`, and any
   `design.md` that cites it (the existing citation mechanism, not a new
   index).
2. A **review delta** note is written at the point of correction
   (`planning/knowledge/<topic-slug>/review-decisions.md`, §4.3's own
   log, or a dedicated delta entry if the correction didn't come through
   human review — e.g. a `context-researcher` re-derivation triggered by
   new Evidence): old assertion ID → new assertion ID (if superseded),
   what evidence changed, why, and the list of citing artifacts found in
   step 1 that now need reassessment.
3. **"Needs reassessment" and "proven incorrect" are distinguished
   explicitly, per the user's own instruction**: a citing artifact is
   listed as *proven incorrect* only if it asserted the specific thing the
   new evidence contradicts; otherwise it is listed as *needs
   reassessment* — a citing artifact is never silently assumed still
   correct just because it wasn't the one directly corrected.

This is the "minimal practical dependency tracking justified by this
phase" the user's own instruction asks for — a documented procedure using
`grep` and the existing citation fields, not a new dependency graph.

## 10. Template delivery (`codecompass-template`)

**Preserves the existing MIT licence and the template's own lightweight
role** — no CodeCompass-specific agent roster, history, or governance
requirement anywhere in the added content, per the user's own explicit
instruction.

**New files** (added at implementation time, not by this planning
commit):

- `planning/knowledge/assertions/TEMPLATE.md` — the portable assertion
  shape (§3's fields, in plain prose/YAML-optional form — no requirement
  to use YAML specifically, since a downstream project may not want a
  parallel machine-readable store at all).
- `planning/knowledge/understanding-review/TEMPLATE.md` — the review
  packet shape (§4.1).
- `planning/knowledge/review-decisions/TEMPLATE.md` — the correction-log
  shape (§4.3), with the four dispositions defined plainly.
- `planning/knowledge/implementation-comparison/TEMPLATE.md` — the
  as-built-vs-understanding comparison shape (§6), including the
  five-way alignment classification.
- `planning/knowledge/legacy-reconciliation/TEMPLATE.md` — the five-way
  historical-claim classification (§7.3).
- `planning/knowledge/documentation-verification/TEMPLATE.md` — the
  Q&A-and-verification shape (§7.4).
- **`docs/mechanical-isolation.md`** — the one genuinely new piece of
  guidance, not a template but an explanation: how to build a curated,
  `.git`-free export by hand or by simple script; what to exclude for
  each of the four scopes (§5's table, generalized to remove
  CodeCompass-specific paths); how to persist a manifest and a read-trace
  even without any agent tooling (a checklist a human can follow: "list
  the files you gave the isolated session access to, list what you told
  it not to use, ask it afterward what it actually opened, compare"); and
  — the user's own explicit requirement — **what to do when your tools
  cannot enforce isolation at all**: document the intended boundary
  anyway, ask the agent (or person) doing the work to self-report what it
  actually consulted, treat any admission of having read excluded
  material as a breach requiring a redo (§5's own protocol, stated for a
  much lower-tooling context), and never claim "clean-room" for a pass
  that had no real boundary, honestly labelling it "best-effort
  isolation" instead.
- `README.md` gains one short cross-link to `docs/mechanical-isolation.md`
  and the new `planning/knowledge/` subdirectories, matching Phase 77's
  own light-touch cross-linking precedent.

**Not added**: any reference to `context-researcher`/`domain-skeptic`/
`implementation-reconstructor`/`docs-reconstructor`/`docs-maintainer` by
name, any reference to this project's own phase numbers or ADRs, any
requirement that a downstream project use Claude Code specifically —
matching `decisions/0060` item 7's portability property, unchanged.

## 11. Definition of Done / review gates

Numbered so each gate's own status is checkable independently:

1. **Schema extension documented** (§3, in `development-methodology.md`)
   — mechanical, no human gate.
2. **Understanding packet complete and adversarially reviewed**
   (`domain-skeptic`, §4.2) — mechanical/agent gate.
3. **Human review gate — the actual user/domain owner reviews the
   packet, real corrections recorded, real dispositions assigned.**
   **This is the one genuinely human-blocking gate in this phase.**
   Completion is explicitly pending while any material assertion remains
   `human_review_state: unreviewed` without the reviewer having
   explicitly deferred it. **Do not fabricate this gate's completion.**
4. **Published snapshot exists** (§4.4), citing the real review outcome
   — mechanical, gated on 3.
5. **Implementation reconstruction complete, isolation-verified, no
   detected breach** (§6.1, §5) — mechanical/agent gate, independent of
   3-4 (can run in parallel with human review); its own alignment
   classification (§6.2) should use the *reviewed* snapshot where gate 3
   has completed by the time it runs, and is explicitly re-checked
   against the final snapshot before the documentation-writing stage
   begins if it was run provisionally against a pre-review draft.
6. **Clean-room draft committed before reconciliation begins** (§7.2) —
   mechanical ordering gate, checked via commit timestamps/`git log`.
7. **Legacy reconciliation complete, every incorporated legacy claim
   re-grounded in cited evidence** (§7.3) — mechanical/agent gate.
8. **Documentation-only Q&A run and independently verified** (§7.4) —
   mechanical/agent gate.
9. **No unrecovered boundary breach** across any of the four isolation
   scopes (§5) — a detected-and-restarted breach is fine; an undetected
   one discovered later voids this gate until redone.
10. **Standard closeout** (`CLAUDE.md` §5, unchanged): docs drift audit,
    phase retro, learning triage, independent `release-phase-auditor`
    completion audit (PASS or PASS WITH NON-BLOCKING OBSERVATIONS),
    terminal `roadmap-context-curator` reconciliation.

**Gate 3 is the load-bearing one.** If the actual user/domain owner has
not reviewed the packet by the time every other gate is otherwise
satisfied, this phase is reported as **not done**, with every other
gate's own status stated plainly — matching the user's own explicit
instruction to keep completion pending rather than treat mechanical
progress as a substitute for a required human review.

## 12. Files expected to change

### 12.1 This planning commit (now)

- **New:** this file; `decisions/0066-...md`; `planning/phase-79-...-
  prompt.md` (the verbatim initiating prompt).
- **`planning/ROADMAP.md`:** new Phase 79 row (status `planned`);
  Priority D's status cell gains a pointer to this phase as its next
  concrete template deliverable.
- **`planning/CONTEXT.md`:** current-state section updated.
- **`planning/v1-redefinition/development-methodology.md`:** short, dated
  amendment note pointing here (not a rewrite).
- **`planning/v1-redefinition/documentation-lifecycle.md`:** short, dated
  amendment note pointing here (not a rewrite).

### 12.2 At implementation time (later commits, not this one) — CodeCompass repository

- `.claude/agents/implementation-reconstructor.md` (new).
- `.claude/agents/domain-skeptic.md` (extended: comparison mode, §6.2).
- `.claude/agents/docs-reconstructor.md` (MODE 2 extended: mechanical
  export input, §5, §7.2).
- `.claude/agents/docs-maintainer.md` (extended: five-way historical-
  claim classification, §7.3; draft-before-reconciliation ordering rule).
- `planning/v1-redefinition/agent-led-development.md` (§2.15 new
  `implementation-reconstructor` catalogue entry; §2.13 `domain-skeptic`
  entry extended; write-boundary table gains a row and an amended one).
- `planning/knowledge/<topic-slug>/**` (assertion records, review packet,
  review decisions, snapshot, implementation-reconstruction report,
  alignment report, isolation manifests/access-logs/boundary-checks,
  documentation Q&A + verification).
- `docs/domain/` (only if the validation topic's assertions genuinely
  extend the existing corpus — decided at execution time against the
  real topic, not pre-committed here).
- `planning/v1-docs-reconstruction/<topic-slug>/` (clean-room draft +
  reconciliation report).
- Standard closeout files (retro, drift-audit report, learnings, audit
  report).

### 12.3 At implementation time — `codecompass-template` repository

- The six new `TEMPLATE.md` files and `docs/mechanical-isolation.md`
  named in §10.
- `README.md` cross-link update.

## 13. Validation topic

**Proposed: CodeCompass's own first-party source/symbol subsystem**
(`source_files`/`source_symbols`, `Language`, `exposure`,
`symbol_index_status`, `codecompass query source`/`query source-symbol`
— Phase 77, `decisions/0065`), confirmed real and available directly
against this repository:

- Real knowledge sources exist: `decisions/0065` and
  `planning/phase-77-first-party-source-and-template.md`'s own Scope/
  Decision sections (intent/rationale evidence, per §5's manifest
  labelling).
- Real implementation evidence exists: `src/codecompass/
  source_symbols.py`, the `source_files`/`source_symbols` schema in
  `graph.py`, `tests/test_source_symbols.py`, `codecompass query source`/
  `query source-symbol`.
- Real legacy narrative exists to reconcile against: `docs/cli-reference.md`'s
  `query source`/`query source-symbol` sections,
  `architecture/context-graph-schema.md`'s first-party-source section,
  `README.md`'s own bullet — all authored at Phase 77, giving this
  phase's clean-room draft something genuine to compare against, not a
  strawman.
- Not yet covered by `docs/domain/`'s own Phase-63D-era corpus (predates
  Phase 77) — a genuinely new topic for the assertion model, not a
  re-litigation of already-approved concepts.
- Self-contained: one subsystem, one schema addition, one CLI surface —
  "a coherent, materially useful topic," not the whole domain, per the
  user's own instruction.

**Honest scoping note**: this topic's "knowledge sources" layer is thin
(an ADR and a phase plan, no external manual) because CodeCompass's own
domain, for this topic, genuinely has no external reference material —
this is a real, disclosed limitation of what this validation can prove
about the *external-manual* case specifically (the fuller case
`codecompass-template`'s own guidance must still support, e.g. Ledgerkit-
with-the-hledger-manual). The mechanism itself (assertion schema, review
gate, isolation, implementation comparison, clean-room writing,
reconciliation, verification) is fully exercised regardless; only the
richness of one input layer is topic-dependent.

**Confirmed at plan time, re-confirmed live at dispatch time**: this
topic is real and its source material exists in this exact repository —
not invented for the exercise, per the user's own explicit instruction.

## 14. Roadmap placement

Tracked in `planning/ROADMAP.md`'s "Post-v1 development" table as an
ordinary phase (matching Phases 71/72's own precedent of governance/
methodology phases that aren't themselves "the next Priority A/B/etc.
step" but are tracked the same way). Cross-referenced from Priority D's
own status cell as its next concrete deliverable (matching Phase 77's own
citation pattern), not listed as a new lettered priority — this phase is
methodology hardening + a template deliverable, not itself one of the six
ordered tracks.

## 15. Human decision gates

**One real judgment call, presented for review, not a blocking
ambiguity**: the choice of validation topic (§13). Resolved by direct
evidence (the topic's own real knowledge/implementation/legacy-narrative
material all confirmed to exist) rather than assertion — if reviewed and
rejected, a different real, currently-uncovered topic is substituted
without otherwise changing this plan's design.

**The load-bearing gate is not a planning-time question at all** — it is
§11 gate 3, the actual user/domain-owner review, which happens during
execution, not now. This plan defines exactly what that gate requires; it
does not, and cannot, satisfy it in advance.

**No other human-decision gate was found requiring a stop before this
plan could be written.**

## 16. Rollback / cleanup requirements

- Every isolated export (§5) lives under the session scratchpad, never
  inside either repository's tracked tree, and is deleted once its
  stage's own output is committed and its manifest/access-log/
  boundary-check are persisted.
- No generated CodeCompass runtime artifact (`context-graph.db`,
  `.claude/skills/`, `.claude/commands/`) is committed anywhere by this
  phase in either repository, beyond what the Implementation-reconstruction
  export genuinely needs to inspect (and that export itself is deleted
  per the above).

## 17. Verification commands

- `.venv/bin/pytest -q` (unaffected by this planning-only commit).
- `.venv/bin/ruff check .`
- `python3 scripts/check_user_docs.py --strict`
- `python3 scripts/check_knowledge_base.py`
- At implementation time: each scope's own `<scope>.boundary-check.md`
  (§5) — export listing vs. manifest, access-log vs. export directory —
  run before that scope's output is treated as valid.
