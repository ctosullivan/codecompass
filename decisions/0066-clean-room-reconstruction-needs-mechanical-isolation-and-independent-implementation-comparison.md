# 0066. Clean-room conceptual understanding and documentation reconstruction needs mechanical isolation and an independent implementation-reconstruction step, not prompt discipline alone

## Status

Accepted (2026-09-30, direct user instruction).

## Context

`decisions/0060` formalized Scope → Plan → Domain → Design → Implement
and, at its Domain stage, built a real, working mechanism: `context-
researcher` derives Observation/Evidence/Claim/Derivation records from
evidence; `domain-skeptic` adversarially reviews them; the actual user/
domain owner approves a `docs/domain/` corpus (Phase 63D). Phase 64 then
derived a "blank-slate" documentation proposal from current project
reality, explicitly instructed (in its own dispatch prompt and in
`.claude/agents/docs-reconstructor.md`'s MODE 2 section) not to treat
`README.md`/`architecture/overview.md` as a starting structure.

Direct inspection of what Phase 64 actually built, for this decision,
finds a real, previously-undiagnosed gap: **the "don't read the old
docs" instruction was never mechanically enforced.** `docs-reconstructor`
MODE 2's own dispatch is "read-only toward src/tests/current docs" (its
own phrasing) — meaning it retains full `Read`/`Grep`/`Bash` access to
every file in the working tree, including `docs/`, `README.md`,
`architecture/`, and `CHANGELOG.md`, and is trusted by prompt alone not
to use that access as a starting point. `agent-led-development.md`'s own
write-boundary table states `context-researcher`'s **read** scope as
"everything" — no boundary at all beyond the role's own stated
methodology. Neither role's charter, as currently defined, could survive
an adversarial question of "how do you know the agent didn't anchor on
the legacy narrative it was told to ignore" — there is no persisted
access-log, no boundary-verification step, and no way to detect (let
alone recover from) contamination after the fact.

Separately, no phase to date has performed a genuinely **independent
implementation reconstruction** — recovering the as-built architecture
from primary evidence (source, tests, schema, config, build/CI, runtime
observation) *before* consulting any reviewed conceptual model, then
classifying alignment. Phase 64's per-cluster dispatches derived
documentation content directly from source, but never produced a
standalone "what does the code actually do" artifact checked *against*
Phase 63D's own approved domain corpus for agreement, partial agreement,
conflict, absence, or insufficient verification. The comparison direction
was one-way (docs derived from code), not adversarial in both directions.

Direct user instruction (2026-09-30): hardened the mechanism with
mechanical (not merely prompted) evidence-layer isolation, a genuinely
independent implementation-reconstruction-and-comparison step, a more
granular per-assertion record shape (stable ID, kind, basis, evidence,
justification, examples/counterexamples, dependencies, uncertainty,
separately-tracked evidence-support and human-review states), a human
understanding-review packet distinct from the raw record store, and a
portable, CodeCompass-agnostic version of the whole workflow for
`codecompass-template`. Full specification:
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`.

## Decision

1. **Reuse the existing Claim record shape, extended with optional
   fields — no new record kind, no new database, no graph subsystem.**
   `planning/knowledge/<topic-slug>/` Claim records gain: `assertion_kind`
   (`definition`/`relationship`/`rule`/`invariant`/`state_transformation`/
   `boundary`), `basis` (`directly_stated`/`inferred`/`proposed_policy`/
   `observed_behaviour`), `examples`, `counterexamples`, `depends_on`
   (assertion IDs), `open_questions`, `evidence_support_state`
   (`supported`/`partially_supported`/`unsupported`/`conflicting`), and
   `human_review_state` (`unreviewed`/`accepted`/`qualified`/`rejected`/
   `superseded`) — the last two kept explicitly separate, per the user's
   own instruction that evidence completeness and human acceptance are
   different facts about the same record. `Observation`/`Evidence`/
   `Derivation` are unchanged. This is `decisions/0062`'s own "reuse the
   existing record shape rather than designing a new one" discipline,
   applied here as it was to Priority B's own future productisation.

2. **A new human-readable "understanding-review" artifact is rendered
   from the assertion records, not hand-authored separately** — topic
   scope/coverage, plain-language concepts and relationships, rules/
   boundaries/exceptions, worked examples, alternative interpretations,
   focused reviewer questions, and an evidence appendix mapping
   statements to assertion IDs and sources. Human corrections are
   recorded against assertion IDs in a `review-decisions.md` log
   (matching `context-gaps/inbox.md`'s own append-in-place curation-note
   convention — no new logging mechanism), with disposition
   (`accepted`/`qualified`/`rejected`/`superseded`) and, for a
   superseded record, a **new** record whose `supersedes` field names the
   old one — reusing the Domain-stage re-entry mechanism
   `development-methodology.md` already defines, not a second one. A
   published, versioned snapshot (scope, source revisions, accepted
   interpretations, unresolved items) is what later designs/docs cite —
   never a live, unversioned file.

3. **Mechanical isolation is achieved by curated, `.git`-free filesystem
   exports built from an explicit allow-list manifest, not by dispatch-
   prompt instruction alone.** Four scopes, each its own export: Domain/
   Understanding reconstruction (authorised knowledge sources — ADRs and
   phase-plan intent sections, explicitly labelled as intent/rationale,
   never proof of current behaviour; explicitly excluding narrative
   `README.md`/`docs/`/`architecture/`/`ai-docs/` prose and any
   unsupported inherited interpretation); Implementation reconstruction
   (source, tests, schema, config, package metadata, CI/build files,
   runtime observation; excluding all narrative documentation and,
   critically, excluding the reviewed Understanding snapshot itself until
   the as-built reconstruction is complete); Documentation writing
   (reviewed Understanding snapshot + Implementation-reconstruction
   output + an approved documentation-architecture outline only); Legacy
   reconciliation (available only once the complete clean-room first
   draft is preserved by commit). This is a real, disclosed, honestly-
   scoped mechanism, not a claim of OS-level sandboxing this project's
   available tools cannot provide: no `.git` directory in an export means
   no git-history path back to excluded material; an unrevealed main-
   checkout path in the dispatch means no filesystem path back either;
   neither prevents a sufficiently determined tool call from attempting
   an escape, so every dispatch also persists its own observable read/
   query trace (reusing Phase 78's own just-established observable-
   research-trace convention, `phase-78-...md` §5.3.4, rather than
   inventing a second one) and a mechanical boundary-verification check
   (the export's own file listing against its manifest; the trace's own
   paths against the export). **A detected boundary breach voids the
   affected stage's own output and requires a restart with a fresh export
   and a fresh agent — never a retroactive claim that contamination
   "probably didn't matter."**

4. **One new agent role, `implementation-reconstructor`** — recovers the
   as-built architecture (modules, APIs/CLI, data/persistence,
   dependencies, runtime paths, extension points, build/config, tests,
   limitations) from the Implementation-reconstruction export alone, with
   no access to the reviewed Understanding model at that stage. A second,
   independent step — assigned to `domain-skeptic`, extending its
   existing adversarial "does this hold up" charter from
   concept-vs-concept contradiction to concept-vs-implementation
   alignment, rather than adding a second new role for a job one existing
   role's mandate already generalizes to — classifies each relevant
   behaviour `aligned`/`partial`/`conflicting`/`not_implemented`/
   `insufficiently_verified` against the reviewed snapshot. Neither step
   may revise the other's own output to force agreement.
   `implementation-reconstructor`'s full charter is specified in the
   phase plan; its `.claude/agents/implementation-reconstructor.md` file
   and `agent-led-development.md` §2.15 catalogue entry are that phase's
   own implementation deliverables (matching how this ADR's own §2.13
   precedent, `domain-skeptic`, was catalogued before its file existed).

5. **`docs-reconstructor`'s MODE 2 is extended, not replaced or
   duplicated.** For a topic with a reviewed Understanding snapshot and
   an Implementation-reconstruction report, MODE 2 is dispatched into the
   Documentation-writing export (item 3) and produces the complete first
   draft before any legacy content is consulted. For any topic without
   both of those inputs yet, MODE 2's existing (unhardened) behaviour is
   unchanged — this decision does not require every future blank-slate
   dispatch to have a full assertion-backed Understanding snapshot behind
   it, only that when one exists, the hardened path is used.
   `docs-maintainer`'s existing reconciliation charter (Phase 65's own
   precedent — lead + `docs-maintainer`, no new role) is extended with an
   explicit five-way historical-claim classification (`supported`/
   `stale_or_contradicted`/`rationale_requiring_verification`/
   `useful_example`/`obsolete`) and a hard ordering rule: reconciliation
   never starts before the clean-room draft is committed. `context-
   evaluator`'s existing "inspect the target directly, establish ground
   truth independently" charter is reused, unchanged, for verifying
   documentation-only answers against real repository evidence — no new
   role for this either.

6. **This is not Priority B.** `decisions/0062`'s Priority B ("lightweight
   claim/evidence/contradiction model... for a downstream user's own
   project") is a future, not-yet-planned capability of the *shipped*
   `codecompass` tool — a `context-graph.db`/CLI change letting a
   downstream user record claims about their *own* project at runtime.
   This decision, and the phase implementing it, make **no
   `src/codecompass/` change at all** — every artifact is a planning
   document, a `docs/domain/` page, an agent brief, or a
   `codecompass-template` file. It self-applies and hardens the
   *project's own development methodology* (`decisions/0060`) and
   delivers a portable, CodeCompass-agnostic version of that methodology
   to the template; it is evidence toward Priority B's eventual
   productisation, never a substitute for planning it.

7. **The template gets portable instructions and minimal templates only**
   — evidence manifests, assertions, understanding review, review
   decisions, implementation comparison, legacy reconciliation, and
   documentation verification — with no CodeCompass-specific agent
   roster, history, or governance requirement, and explicit guidance on
   establishing mechanical isolation with whatever tools a downstream
   project actually has, including an honest fallback (documented,
   detectable, restart-on-breach discipline) for a project whose tools
   cannot enforce a hard boundary at all. This continues `decisions/0060`
   item 7's own portability property and Phase 77's own template
   delivery, not a new principle.

## Alternatives considered

- **Keep isolation prompt-only, add only the record-schema and role
  changes.** Rejected: this is precisely the gap the user's own direct
  inspection of Phase 64 found real and unaddressed — a prompt telling an
  agent to ignore content it can still read is not a boundary, it is a
  request, and this project's own established pattern (never let the
  producer certify its own output) argues for the same rigor applied to
  *what an agent can see*, not only *what it is told to do with what it
  sees*.
- **Full OS-level sandboxing (containers, filesystem namespaces) for
  every dispatch.** Rejected as disproportionate to what this phase's own
  available tools can build and verify: Claude Code's tool-permission
  model does not provide a directory-jail primitive this project can rely
  on. The curated-export-plus-trace-plus-breach-restart design is the
  most rigorous mechanism actually achievable with available tools,
  honestly disclosed as such rather than overclaimed.
- **A second new agent role for the implementation-vs-understanding
  comparison step, instead of extending `domain-skeptic`.** Rejected:
  `domain-skeptic`'s existing charter ("searches for internal
  contradictions... between concepts") already generalizes cleanly to
  "between a concept and an independently reconstructed implementation" —
  the same reasoning `decisions/0060` itself used to justify creating
  `domain-skeptic` in the first place (a genuinely uncovered job, not a
  stretch) argues against inventing a fourth adversarial role here when a
  third one's mandate already reaches.
- **Fold this into Priority B's own future planning instead of a
  separate phase now.** Rejected per the user's own explicit instruction
  to distinguish the two: this phase is methodology hardening plus a
  template deliverable, not a runtime capability of the shipped tool —
  conflating them would misrepresent both this phase's real, bounded
  scope and Priority B's own, larger, not-yet-evidenced one.

## Consequences

- New files: `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`,
  this decision record, the phase's own saved initiating-prompt file.
- `development-methodology.md` and `documentation-lifecycle.md` each gain
  a short, dated forward-pointing amendment note (their own existing
  convention) — their substantive content is not rewritten by this
  decision.
- No `src/codecompass/` change. No `context-graph.db` schema change. No
  new database or graph subsystem, per the user's own explicit
  instruction.
- The phase's own implementation (the actual `.claude/agents/
  implementation-reconstructor.md` file, the extended `docs-reconstructor`/
  `domain-skeptic`/`docs-maintainer` briefs, the real Understanding/
  Implementation-reconstruction/documentation dispatches, and the
  `codecompass-template` additions) is that phase's own scoped work, not
  started by this decision, and requires its own plan-file review per
  `CLAUDE.md` §1 before implementation begins (already satisfied by the
  phase plan named above, written in this same commit).
