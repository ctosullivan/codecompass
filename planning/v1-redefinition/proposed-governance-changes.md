# Proposed governance changes (feeds README §7 gates G4, G5)

Per `CLAUDE.md` §0, **any** change to `CLAUDE.md` must be presented as a
diff and explicitly approved before it is written or committed. This file
holds those proposed diffs (§A) and the ADR drafts (§B).

**Status:** all applied.
- §A (the `CLAUDE.md` §1/§5/§8/§6 + `CONTRIBUTING.md` changes) — approved
  (gate G4) and applied in **Phase 40**.
- A further `CLAUDE.md` §5 amendment (per-phase docs-drift audit + phase
  retro) — approved 2026-09-10 and applied in **Phase 41**.
- §B ADRs `0048`/`0049` — published **Phase 39**; `0050` — published
  **Phase 41**.

This file is now a historical record of what was proposed;
`CLAUDE.md` / `CONTRIBUTING.md` / `decisions/` are authoritative.
**§C's drafts were approved 2026-09-12** (gates G11/G12, "Proceed as
recommended") and are now `Accepted` at
[`decisions/0052`](../../decisions/0052-ledgerkit-is-the-next-reference-project-not-technical-clipper.md)
and
[`decisions/0053`](../../decisions/0053-relicense-to-gpl-3.0-or-later.md).
**§E (`L-050`) and §F (`L-065`)** are further, later `CLAUDE.md`
corrections approved and landed the same way, outside any lettered gate
(both are factual/consistency corrections of an already-false or
self-contradictory claim about a doc `CLAUDE.md` itself governs, not new
rules needing gate-style deliberation).

---

## A. Proposed `CLAUDE.md` changes (gate G4)

Three edits. Approve independently if preferred — A2 (DoD) and A3 (§8)
can land in different phases.

### A1 — §1 "Plan before implementing": add curator/auditor touchpoints

> **Add, after the existing paragraph:**
>
> When the agent-led development model is in effect (§8), establishing
> "current project state" and "the next approved work" is the
> `roadmap-context-curator`'s step, and a phase is not started until any
> human-decision gate recorded against it in
> `planning/v1-redefinition/README.md` §7 is resolved.

### A2 — §5 "Definition of done, per phase": add three conditions

> **Current text ends:** "…`planning/ROADMAP.md` marks the phase `done`.
> Not done until all six."
>
> **Proposed — replace "all six" and append:**
>
> Code implemented + plan file's verification step passes + `docs/`,
> `architecture/`, `decisions/` updated as applicable + changelog entry
> added + `planning/CONTEXT.md` reflects the new state +
> `planning/ROADMAP.md` marks the phase `done` + **candidate learnings
> from the phase have been triaged by the `knowledge-curator` (promote /
> retain / merge / discard, per `planning/learnings/`)** + **an
> independent `release-phase-auditor` pass (or, for a trivial phase, an
> explicit lead confirmation) verifies the preceding conditions rather
> than trusting the implementing agent's report**. For a
> reference-project or context-evaluation phase, **a `context-evaluator`
> report exists and is linked from the phase's exit note**. Not done
> until all of these.

### A3 — new §8 "Agent-led development model"

> **Add as a new section (renumbering nothing — §8 is new):**
>
> ## 8. Agent-led development model
>
> CodeCompass is developed by a lead Claude Code session acting as
> project lead, delegating bounded work to a small set of specialist
> agents defined in `.claude/agents/`. The full model — roles, write
> boundaries, independence requirements, how results return to the lead —
> is `planning/v1-redefinition/agent-led-development.md`; the per-session
> procedure is `planning/agent-led-workflow.md`.
>
> Fixed points:
> - **Claude Code orchestrates; CodeCompass never spawns or coordinates
>   agents.**
> - Specialist agents operationalise the *existing* governance
>   mechanisms (this file, `ROADMAP.md`, `CONTEXT.md`, ADRs,
>   `architecture/`, tests, `CHANGELOG.md`, §5's DoD, §0's protected-file
>   rule). No agent maintains a private parallel system.
> - Evaluation and audit agents inspect their target directly, never via
>   CodeCompass, and never repair what they are judging.
> - No agent writes this file, `decisions/*`, or `src/` (the lead owns
>   those; ADRs go through §2's process; `src/` changes are the lead's or
>   an ad-hoc implementer subagent's).
> - **An agent observation is not authoritative because an agent recorded
>   it** — it enters the learning lifecycle
>   (`planning/learnings/`, `planning/v1-redefinition/learning-lifecycle.md`)
>   as a candidate; only curation plus evidence promotes it into a test,
>   ADR, doc, roadmap row, rule, or skill. Agent persistent memory is a
>   per-agent working aid, never a source of truth.

### A4 (optional) — §6 milestone note

> **Add to §6, after the MVP milestone sentence:**
>
> The redefined-CodeCompass-v1 effort (`planning/v1-redefinition/`) is one
> further milestone group; its stages A–F tag/release only on group
> completion (Phase 67), same posture as the MVP groups. "CodeCompass v1"
> as a product milestone is distinct from the `pyproject.toml` version
> string, which tracks published wheels under ordinary SemVer.

### A5 — §5 second amendment (approved 2026-09-10, applied Phase 41)

Presented to and approved by the user on 2026-09-10. Two conditions
inserted into §5's list. Preserved here verbatim as the historical
record; authoritative text is `CLAUDE.md` §5 + `decisions/0050`.

**Condition 1, inserted after "`docs/`, `architecture/`, `decisions/`
updated as applicable":**

> an independent `docs-reconstructor` per-phase drift audit finds no
> current-truth doc (`README.md`, `docs/`, `architecture/`, `ai-docs/`)
> left misdescribing the system, scoped to what the phase changed (the
> full blank-slate reconstruction stays a milestone activity)

**Condition 2, inserted after "`planning/ROADMAP.md` marks the phase
`done`" (and the learnings-triage clause reworded to "including any
surfaced by the retro"):**

> a phase retro report exists at `planning/retros/phase-N-<slug>.md`
> (goal, delivered vs planned, lessons learnt, process-improvement
> feedback; a few lines suffice for a trivial phase)

Mirrored into `CONTRIBUTING.md`'s "Definition of done" section + a note
in its "Agent-led development model" section (Phase 41 commit).

### `CONTRIBUTING.md` mirror

`CONTRIBUTING.md` restates these rules for humans (its own header says
so). Whatever subset of A1–A5 is approved, mirror it into
`CONTRIBUTING.md` in the **same commit** (the existing
`decisions/0022`/`0030` precedent for keeping the two in sync).

---

## B. ADR drafts (gate G5)

> **`0048` and `0049` were approved (gate G5, 2026-09-09) and are now
> `Accepted` at
> [`decisions/0048-redefined-v1-is-a-product-validation-milestone.md`](../../decisions/0048-redefined-v1-is-a-product-validation-milestone.md)
> and
> [`decisions/0049-agent-led-development-model.md`](../../decisions/0049-agent-led-development-model.md)
> (Phase 39). `0050` was published in Phase 41
> ([`decisions/0050-phase-retros-and-per-phase-docs-drift-audit.md`](../../decisions/0050-phase-retros-and-per-phase-docs-drift-audit.md)).
> The published ADRs are authoritative; the drafts below are kept for
> context.**

### Draft `decisions/0048` — Redefined v1 milestone

- **Status:** ✅ Accepted (Phase 39, 2026-09-09) — see published ADR.
- **Context:** `pyproject.toml` says `1.0.0`; nothing is published; no
  tags; `v0.1`/`v0.2` never cut. The internal "v1.0"
  (`planning/v1.0-initial-release-roadmap.md`) is a *packaging* milestone
  — publish the npm/PyPI/Cargo package-source tool. `decisions/0039`
  itself notes there are no external users and any decision now is
  speculative. Both chosen reference projects have ≈0 runtime package
  dependencies, so the current model produces near-empty output for the
  first two real targets.
- **Decision:** Redefine "CodeCompass v1" as a **product-validation
  milestone** (`planning/v1-redefinition/`): CodeCompass is developed
  agent-led (Stage A), validated against real external reference-project
  work (Technical Clipper, then Ledgerkit), improved from that evidence,
  generalised only as far as evidence justifies, and released after a
  blank-slate documentation reconstruction and an independent audit.
  All publishing is held until that release (gate G2-b): CodeCompass has
  never been published, and the first-ever PyPI release is the redefined
  v1, shipped as `1.0.0` at Phase 67. In the interim `pyproject.toml`
  carries `1.0.0.dev0`.
- **Alternatives considered:** (a) publish `1.0.0` now as planned —
  rejected: spends the "first stable public API" signal on an
  unvalidated snapshot and makes "v1" ambiguous; (b) keep the packaging
  definition, treat validation as v2 — rejected: the task explicitly
  calls for redefining v1, and a v1 that has never been pointed at a
  project it wasn't also developing can't credibly claim the "context
  layer for AI agents" positioning; (c) publish a `0.4.0` foundation
  release now for early external signal — considered and **not chosen**
  (gate G2-b): lower external surface area during a period of likely
  schema change was preferred over the early signal.
- **Consequences:** `ROADMAP.md` gains the Stage A–F group; existing
  Phases 24/25 become explicitly deferred (not renumbered); the "v1.0
  scope notes" are retitled; `CLAUDE.md` §6 gains a milestone note
  (A4, its own §0 approval); Phase 23 Part B is superseded (first
  publish = Phase 67); `CHANGELOG.md`'s `[Unreleased]` stays undated
  until Phase 67.

### Draft `decisions/0049` — Agent-led development model

- **Status:** ✅ Accepted (Phase 39, 2026-09-09) — see published ADR. The
  roster itself is still built in Phase 40.
- **Context:** CodeCompass is positioned as the context layer for AI
  development agents but is not itself developed agent-led; it has no
  independent evaluation of the context it produces and no systematic
  learning capture. `planning/v0.2-implementation-execution-plan.md`
  already records a subagent incident (read-only research agent deleted
  files) and an independent-verification rule.
- **Decision:** Adopt the agent-led model in
  `planning/v1-redefinition/agent-led-development.md`: a lead session +
  a capped roster (`context-evaluator`, `reference-project-tester`,
  `docs-maintainer`, `roadmap-context-curator`, `knowledge-curator`,
  `docs-reconstructor`, `release-phase-auditor`), with the write
  boundaries and independence requirements in that document, integrated
  into `CLAUDE.md` §5's DoD (A2) and a new §8 (A3).
- **Alternatives considered:** (a) keep ad-hoc subagent delegation —
  rejected: no independence, no continuous doc/roadmap maintenance, no
  learning capture, which every later stage needs; (b) a larger roster
  mirroring every SDLC activity — rejected: `README.md` §1.9 /
  `agent-led-development.md` §1, complexity risk R9, GATE DA prunes
  instead of pre-building; (c) CodeCompass orchestrates its own agents —
  rejected: hard non-goal.
- **Consequences:** `.claude/agents/` created; `planning/agent-led-workflow.md`
  created; GATE DA (Phase 43) may prune/merge roles; `knowledge-curator`
  owns `planning/learnings/`.

### `decisions/0050` — ✅ Accepted (Phase 41, 2026-09-10)

Published at
[`decisions/0050-phase-retros-and-per-phase-docs-drift-audit.md`](../../decisions/0050-phase-retros-and-per-phase-docs-drift-audit.md).
Covers the learning lifecycle **and** the two per-phase closeout
mechanisms the user added on 2026-09-10 (a lead-authored phase retro; an
independent per-phase docs-drift audit by `docs-reconstructor`), both new
`CLAUDE.md` §5 DoD conditions.

### `CLAUDE.md` §5 — second amendment (Phase 41)

The user approved a further §5 diff on 2026-09-10 (two conditions: the
per-phase drift audit; the phase retro). Applied in the Phase 41 commit,
mirrored into `CONTRIBUTING.md`. The exact text is in `CLAUDE.md` §5 and
`decisions/0050`.

### Further ADRs — written when their phase reaches a real tradeoff

- Task-oriented retrieval design (Phase 48), if funded.
- Each Stage E abstraction (Phases 56/57), one per abstraction, gate G7.
- Any CLI breaking change (gate G8).
- A docs-site reversal of `decisions/0039` (Phase 64/65), only if
  reference-project friction shows up.
- The redefined-v1 release itself may warrant a closeout ADR (Phase 69).

---

## C. 2026-09-12 realignment ADR drafts (gates G11, G12)

> **`0052` and `0053` were approved (gates G11/G12, 2026-09-12) and are
> now `Accepted` at
> [`decisions/0052`](../../decisions/0052-ledgerkit-is-the-next-reference-project-not-technical-clipper.md)
> and
> [`decisions/0053`](../../decisions/0053-relicense-to-gpl-3.0-or-later.md).
> The published ADRs are authoritative; the drafts below are kept for
> context.** See `realignment-2026-09.md` for the full reassessment
> these two decisions belong to.

### Draft `decisions/0052` — Ledgerkit is the next reference project, not Technical Clipper

- **Status:** ✅ Accepted (2026-09-12, gate G11) — see published ADR.
- **Context:** The original Stage B/D ordering (`decisions/0048`) put
  Technical Clipper first as "first proof point" and Ledgerkit second as
  "harder second proof point." Both were, at the time, un-evaluated
  hypotheses about which project better tests CodeCompass's distinctive
  value. Neither Stage B nor Stage D has started (`realignment-2026-09.md`
  §1.1 — `planning/reference-projects/` doesn't exist). Live re-inspection
  of both projects (§1.2/§1.3 of that document) confirms Ledgerkit's
  dependency shape (hledger executable, manuals, journal syntax, query
  semantics, compatibility tests, intentional divergences) is the
  stronger test of context *relating*, not just context *discovery* —
  and it has a concrete, already-scoped genuine next task (Milestone 5,
  "CLI Filter Flags") ready to use as the Stage B baseline immediately.
- **Decision:** Ledgerkit becomes Stage B (Phases 44–47) and the deeper
  Stage D (Phases 52–55); Technical Clipper becomes a new Stage F
  (Phases 60–63), run *after* Ledgerkit-driven changes land, explicitly
  to check they generalise rather than overfit to accounting/hledger.
  Phase numbers 45 onward are renumbered (none had started); GATE
  letters DB/DC/DD/DE keep their conceptual position, now scoped to
  Ledgerkit evidence; a new GATE DF covers Technical Clipper's
  regression decision. Full detail: `roadmap.md` (amended same commit).
- **Alternatives considered:** (a) keep Technical Clipper first, run
  Ledgerkit second as originally planned — rejected: the strategic
  redirection explicitly argues Ledgerkit is the stronger test, and
  nothing has been invested in a Technical-Clipper-first Stage B yet, so
  there is no sunk cost to protect; (b) run both simultaneously —
  rejected: dilutes the evidence-gated discipline (`README.md` R9, R11)
  that keeps each stage's findings attributable to one project; (c) drop
  Technical Clipper entirely — rejected: it remains the best available
  check against overfitting to a single ecosystem (`README.md` R10), a
  concern the reorder makes *more* relevant, not less.
- **Consequences:** `roadmap.md`, `ledgerkit-plan.md`,
  `reference-project-protocol.md`, `context-quality-evaluation.md`,
  `conditional-generalisation.md` amended (phase numbers, stage
  references); `planning/ROADMAP.md` / `planning/CONTEXT.md` amended;
  `decisions/0048` is not superseded (its core redefinition holds) —
  this ADR narrows one part of it (the reference-project ordering).

### Draft `decisions/0053` — Relicense CodeCompass to GPL-3.0-or-later

- **Status:** ✅ Accepted (2026-09-12, gate G12) — see published ADR.
  Full plan: `licence-migration.md`.
- **Context:** `hledger` — the compatibility reference Ledgerkit (and
  now, transitively, CodeCompass's own evidence-relating work) targets —
  is `GPL-3.0-or-later`, confirmed at the SPDX-field level in its own
  `package.yaml` files. CodeCompass is currently MIT, single copyright
  holder, no bundled third-party source, no other contributors. Aligning
  CodeCompass's own licence with hledger's family removes the need for
  an artificial clean-room boundary when a CodeCompass development agent
  inspects `hledger` source/docs/tests to understand behaviour it is
  helping relate for Ledgerkit's benefit.
- **Decision:** Relicense CodeCompass from MIT to GPL-3.0-or-later:
  `LICENSE` (canonical GPL-3.0-or-later text + standard notice block),
  `pyproject.toml` (`license` field + classifier), `README.md`
  (`## License` section), `CONTRIBUTING.md` (a short note on the
  licence and the absence of a separate CLA). No git tag or release is
  affected (none exist — `git tag -l` is empty). Source-assisted
  development policy (four categories: inspection / understanding /
  adapted implementation / directly translated material, each with its
  own attribution requirement) recorded in `licence-migration.md` §4 and
  carried into `adoption-blueprint.md` for adopting projects.
- **Alternatives considered:** (a) stay MIT, maintain an explicit
  clean-room boundary for any hledger-facing work — rejected: adds
  process friction (a boundary to police) for a project whose stated
  direction is deeper source-assisted evidence-relating work, without a
  compensating benefit (CodeCompass has no reason to prefer permissive
  redistribution terms — it isn't a library others embed commercially in
  a way MIT specifically protects); (b) dual-license (MIT + GPL) —
  rejected: adds real ongoing maintenance complexity (every future
  contribution would need to be dual-licensable) for a single-maintainer
  project with no evidence of demand for the MIT option; (c) relicense
  to a different copyleft licence (e.g. AGPL, LGPL) — rejected: the
  specific goal is *alignment with hledger's own licence family*, not
  copyleft in general, and hledger's own choice (GPL-3.0-or-later, not
  AGPL/LGPL) is the natural match.
- **Consequences:** `LICENSE`, `pyproject.toml`, `README.md`,
  `CONTRIBUTING.md` updated in one dated commit once G12 resolves;
  `CHANGELOG.md` gains an entry; no historical commit or release is
  rewritten (none published under any licence to date).

---

## D. 2026-09-17 proposed addition (Phase 55b — `L-021`)

**Status:** applied. Presented to the user via `AskUserQuestion`;
approved ("Approve as written"). `CLAUDE.md` §1 amended, mirrored into
`CONTRIBUTING.md`, in a follow-up commit after Phase 55b's own closeout.
This section is left as the historical proposal record, not rewritten.

### D1 — §1 "Plan before implementing": require a test through the real call site for a shape this project's own Phase 55b showed can otherwise ship broken

- **Context:** Phase 55b's first implementation attempt
  (`spec_docs.py::_extract_title` populating `doc_artifacts.name`) added
  every unit test its plan called for, all green on the first run, and
  was still completely non-functional in the real, running tool —
  `sync.py::rebuild_project_graph`'s own call to
  `build_doc_relations_edges` never included the new `spec_doc_rows`
  argument, so the real gap the phase existed to close still reproduced
  identically against the live Ledgerkit repository. Every new unit test
  called the changed function (or its caller-once-removed) directly,
  never through `sync.py`'s real production wiring — the one place the
  actual defect lived. Caught only by `context-evaluator`'s round-1
  independent pass re-running the real tool against real data, not by
  the lead's own confidence in the green suite. **Correction, caught by
  `release-phase-auditor`:** the phase's own approved plan
  (`phase-55-evidence-reconciliation.md` §G) did *not* name `sync.py`
  under "Affected architecture" at all — it named only `spec_docs.py`
  and explicitly called `doc_mapping.py` "untouched." Both `sync.py`'s
  wiring fix and `doc_mapping.py`'s substantive change were discovered
  necessary only during implementation, beyond what was actually
  presented to the user for approval — the approved plan was
  under-scoped, not merely under-tested. See
  `planning/learnings/inbox.md`'s `L-021` for the full account and
  independent re-verification.
- **Proposed text — append to §1, after the existing "If writing the
  plan surfaces an assumption not already settled, pause and ask before
  proceeding from plan to code" sentence:**

  > If a phase adds behavior to an existing function that already has a
  > real production call site, the plan's verification section must name
  > that call site explicitly and include at least one test that
  > exercises it directly — a test that only calls the changed function
  > in isolation is not sufficient on its own, no matter how thorough,
  > since it cannot catch the function's new behavior never actually
  > being wired into its caller. (Phase 55b — L-021.)

- **Alternatives considered:** (a) leave §1 as-is, treat this as a
  one-off caught-in-time incident — rejected: the retro itself frames
  the underlying principle as durable/general, not specific to this
  phase's code, and the failure mode (unit-test-green,
  production-broken) is exactly the kind of thing a green test suite
  gives no internal signal to distrust; (b) a broader "every phase must
  include an integration test" rule — rejected as over-broad for what
  this one incident evidences; scoped instead to the precise shape that
  actually failed (an existing function, a real call site, behavior
  added to it); (c) land this in `planning/agent-led-workflow.md`
  instead of `CLAUDE.md` §1 — considered, but this is about what a
  phase *plan's own content* must specify regardless of which agent or
  the lead writes it (unlike `L-006`/`L-013`/`L-018`, which are about the
  agent-orchestration procedure specifically), and `CLAUDE.md` §1 already
  governs plan content project-wide, so a targeted strengthening there
  fits better than a new agent-workflow step.
- **Consequences if approved:** `CLAUDE.md` §1 gains the sentence above;
  `CONTRIBUTING.md`'s mirrored "plan before implementing" section gets
  the same addition in the same commit (existing `decisions/0022`/`0030`
  precedent for keeping the two in sync); `planning/learnings/inbox.md`'s
  `L-021` flips to `status: promoted` with a `promoted.md` pointer line
  once the edit lands.

## E. 2026-09-25 proposed correction (Phase 71 — `L-050`)

**Status:** approved by the user and landed, 2026-09-25 (`CLAUDE.md` §2,
Phase 71 closeout). Filed by `knowledge-curator` during Phase 71's own
triage step, independent of the phase's own retro (which did not
surface this).

### E1 — §2 "Kept-in-sync docs, same commit": correct `planning/ROADMAP.md`'s own description to match Phase 71's approved restructure

- **Context:** `CLAUDE.md` §2 currently describes `planning/ROADMAP.md`
  as a "full-roadmap phase-status table (all phases, not just the
  current one)." Phase 71 (`4bc7c1d`, approved and landed) replaced
  `ROADMAP.md`'s 424-line phase-by-phase table with a ~113-line
  current-state summary; `ROADMAP.md`'s own new header states explicitly
  that full phase-by-phase history is "preserved in three places, not
  repeated here as a 70-row table" (`v1-closeout.md`,
  `v1-redefinition/roadmap.md`, git history). `CONTRIBUTING.md` and
  `ai-docs/CLAUDE.md`'s own descriptions of `ROADMAP.md` were already
  corrected to match this in `396118a` (that phase's own drift-audit-
  findings commit). `CLAUDE.md` §2 itself was not — and could not be,
  per §0, without this explicit approval step. Phase 71's own per-phase
  drift audit (`planning/retros/_drift-audit-phase-71.md` §3) found this
  exact tension and explicitly declined to resolve it, naming it "a
  possible tension between Phase 71's restructure and `CLAUDE.md` §2's
  own standing requirement, not just a wording fix in `CONTRIBUTING.md`."
  The phase's own retro never picked this back up. Full account:
  `planning/learnings/inbox.md`'s `L-050`.
- **Proposed text — replace the existing `planning/ROADMAP.md` bullet in
  §2:**

  > Current:
  > - **`planning/ROADMAP.md`** — full-roadmap phase-status table (all
  >   phases, not just the current one). Updated whenever a phase starts
  >   (§1), finishes (§5), or its scope changes.
  >
  > Proposed:
  > - **`planning/ROADMAP.md`** — full-roadmap, at-a-glance phase-status
  >   view: what's done, what's next, what's still just planned, plus
  >   deferred/not-funded items with revisit triggers. For a completed
  >   milestone group, full per-phase historical detail is preserved in
  >   that milestone's own closeout record (e.g. `v1-closeout.md`,
  >   `v1-redefinition/roadmap.md`) and git history, not repeated here as
  >   a row-per-phase table (established at Phase 71). Updated whenever a
  >   phase starts (§1), finishes (§5), or its scope changes.

- **Alternatives considered:** (a) leave §2 as-is and treat
  `CONTRIBUTING.md`/`ai-docs/CLAUDE.md`'s own corrections as sufficient —
  rejected: §2's own preamble is explicit that this file is "what every
  future session trusts unconditionally on load," and §0 treats
  unreviewed drift here as compounding silently, so leaving the more
  authoritative copy stale while fixing the two downstream mirrors is
  backwards; (b) a smaller edit that only drops the parenthetical "(all
  phases, not just the current one)" without adding the milestone-closeout
  pointer — considered, but the current three-doc precedent
  (`ROADMAP.md`'s own header, `CONTRIBUTING.md`, `ai-docs/CLAUDE.md`) all
  now explain *where* the historical detail lives, and §2 should not be
  the one place a reader is left to wonder; (c) wait for a second
  restructure before treating this as worth a governance change — rejected,
  this is not a new-rule proposal needing recurrence evidence, it is a
  correction of an already-false factual claim about a doc `CLAUDE.md`
  itself governs.
- **Consequences if approved:** `CLAUDE.md` §2's `planning/ROADMAP.md`
  bullet is replaced with the text above; `planning/learnings/inbox.md`'s
  `L-050` flips to `status: promoted` with a `promoted.md` pointer line
  once the edit lands.

## F. 2026-09-28 proposed correction (Phase 76 corrective pass — `L-065`)

**Status:** approved by the user and landed, 2026-09-28 (`CLAUDE.md` §5,
commit `feaaaa0`). Filed by the lead during a narrowly-scoped
post-closeout corrective pass on the already-`done` Phase 76, confirmed
sound by `knowledge-curator`'s own independent triage of `L-065`.

### F1 — §5 "Definition of done, per phase": fix a genuine internal contradiction between the audit-voiding rule and the terminal reconciliation commit it requires

- **Context:** `CLAUDE.md` §5 stated "any commit after the auditor's own
  pass that touches audited scope voids that pass and requires a fresh
  one before this transition happens." The same paragraph's own terminal
  step — a `roadmap-context-curator` reconciliation flipping
  `planning/ROADMAP.md`'s phase row to `done` — necessarily lands after
  the audit and necessarily touches `planning/ROADMAP.md`/
  `planning/CONTEXT.md`, files the auditor's own checklist item 2
  explicitly checks as part of "audited scope." Read literally, the one
  commit required to ever reach `done` voids the audit that authorizes
  it — a real, structural contradiction, not a hypothetical one: every
  phase closeout to date, including Phase 76's own original one
  (`8c053f7`→`b3abe07`), had informally judged the curator's diff "narrow
  enough" by eye, with no written standard to judge it against. Full
  account: `planning/learnings/inbox.md`'s `L-065`.
- **Proposed text — append to the existing final sentence of §5:**

  > Current:
  > — this is the terminal action of the sequence, not a condition the
  > auditor checks alongside the others; any commit after the auditor's
  > own pass that touches audited scope voids that pass and requires a
  > fresh one before this transition happens. Not done until all of
  > these.
  >
  > Proposed:
  > — this is the terminal action of the sequence, not a condition the
  > auditor checks alongside the others; any commit after the auditor's
  > own pass that touches audited scope voids that pass and requires a
  > fresh one before this transition happens — **with one explicit,
  > narrow exemption**: the terminal `roadmap-context-curator`
  > reconciliation commit itself (flipping `planning/ROADMAP.md`'s phase
  > row to `done`, overwriting `planning/CONTEXT.md`'s current-state
  > section, and updating the phase plan file's own Status line —
  > nothing else) is not "audited scope" for this purpose, since the
  > audit exists precisely to authorize that commit; treating it as
  > self-invalidating would make the gate impossible to ever satisfy. If
  > that commit touches anything beyond those three named targets (a
  > changelog entry, `docs/`, `architecture/`, `decisions/*`, `src/`,
  > tests, `planning/learnings/**`, `planning/context-gaps/**`, or any
  > other file), the audit is voided and must be repeated against the new
  > state, exactly as before — confirmed by the lead reading the commit's
  > actual diff before treating the phase as done. Not done until all of
  > these.

- **Alternatives considered:** (a) the corrective pass's own alternative
  model — a final post-curator audit pass instead of a pre-defined
  exemption list — was offered to the user and explicitly declined in
  favor of the exemption approach; (b) a broader "trust the curator's own
  judgment" fix — rejected, since it would reintroduce exactly the
  unrepeatable, ad hoc standard that let this contradiction go unnoticed
  through every prior phase closeout; (c) leaving §5 as-is and only
  documenting the exemption in `planning/agent-led-workflow.md` — rejected
  because `CLAUDE.md` explicitly wins over any other guidance when they
  disagree (its own preamble), so a workflow-doc-only fix would leave the
  higher-precedence document self-contradictory.
- **Consequences (already landed):** `CLAUDE.md` §5 carries the exemption
  clause above (`feaaaa0`); `planning/agent-led-workflow.md` step 14 and
  `.claude/agents/roadmap-context-curator.md` were updated to
  operationalize it (`6d668db`); `planning/learnings/inbox.md`'s `L-065`
  is `status: promoted` with a `promoted.md` pointer line, confirmed
  sound by an independent `knowledge-curator` triage pass that read all
  three affected documents directly and found no remaining ambiguity or
  contradiction.

## G. 2026-10-01 proposed addition (Phase 79 fifth amendment — `L-070`)

**Status:** approved by the user (explicit diff approval, 2026-10-01, per
`CLAUDE.md` §0) and landed. Filed by `knowledge-curator` during the
fifth-amendment triage pass, independent of (but alongside) the other
four candidate learnings that same addendum named.

### G1 — §1 "Plan before implementing": require a minimal-input edge-case test for any fail-closed validation/detection mechanism a phase's plan verifies

- **Context:** Phase 79's fourth revision redesigned
  `scripts/check_knowledge_base.py`'s snapshot-validation checks (§5.3)
  to fail closed against a real gap (hashing a live, legitimately-
  superseded file against its own historical content). The fifth
  revision, a direct review of the already-`done` result, found the
  redesign still didn't fail closed at a *different* edge of the same
  mechanism: it only ever validated assertion entries already *present*
  in a snapshot's own table, so a sidecar reduced to nothing but its own
  `snapshot_id` iterated zero entries and reported zero findings —
  indistinguishable from a genuinely complete, small snapshot. This is
  the second such gap found in the same checker across two consecutive
  revisions of the same ADR (the fourth revision's own list-validation
  fix, §4.2, had the same shape: a pattern-matching detector missing an
  indentless list shape its own pattern never matched). Both times, the
  fix that was approved and verified covered the exact scenario named in
  the defect report, not the minimal/empty-content case a maximally
  adversarial or accidental input could still produce. Full account:
  `planning/learnings/inbox.md`'s `L-070`;
  `decisions/0067` Decision item 1;
  `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  §0 "Fifth revision" entry 1 and "Fourth revision" entries 1-2.
- **Proposed text — append to §1, after the existing `L-021` sentence
  ("If a phase adds behavior to an existing function that already has a
  real production call site... (Phase 55b — L-021.)"):**

  > If a phase's verification step tests a fail-closed validation or
  > detection mechanism (a check meant to catch malformed, incomplete, or
  > malicious input), the plan's verification section must include a test
  > against the mechanism's own minimal-content edge case (e.g. an
  > empty, truncated, or otherwise maximally-reduced input that is still
  > technically well-formed enough to be accepted for processing) in
  > addition to the originally-named failure scenario — a test that only
  > covers the scenario the phase's own prose describes is not
  > sufficient on its own, since fixing one fail-open gap in a validation
  > mechanism can leave a different one at the mechanism's own edge
  > untested. (Phase 79 fifth amendment — L-070.)

- **Alternatives considered:** (a) leave §1 as-is, treat this as a
  one-off incident specific to `check_knowledge_base.py` — rejected: the
  same shape recurred twice within one phase across two genuinely
  different checks (snapshot validation, list validation), which is
  exactly the kind of cross-instance recurrence this project's own
  learning-lifecycle treats as sufficient for a project-wide rule, not a
  scoped one; (b) route this to `planning/agent-led-workflow.md` instead
  of `CLAUDE.md` §1 — considered, but mirrors `L-021`'s own reasoning
  (`proposed-governance-changes.md` §D) exactly: this is about what a
  phase *plan's own content* must specify regardless of which agent or
  the lead writes the check, not about agent-orchestration procedure, so
  it fits better alongside `L-021`'s own sentence in the same section
  than as a new workflow step; (c) a broader "every validation check
  needs exhaustive adversarial-input testing" rule — rejected as
  over-broad for what two incidents evidence; scoped instead to the
  precise shape that actually failed twice (a fail-closed check, a
  minimal/empty-content edge case the originally-named scenario didn't
  cover).
- **Consequences if approved:** `CLAUDE.md` §1 gains the sentence above;
  `CONTRIBUTING.md`'s mirrored "plan before implementing" section gets
  the same addition in the same commit (existing `decisions/0022`/`0030`
  precedent for keeping the two in sync); `planning/learnings/inbox.md`'s
  `L-070` flips to `status: promoted` with a `promoted.md` pointer line
  once the edit lands.

## H. 2026-10-01 proposed addition (Phase 79 sixth amendment — `L-075`)

**Status:** approved by the user (explicit diff approval, 2026-10-02, per
`CLAUDE.md` §0) and landed. Filed by `knowledge-curator` during the
sixth-amendment triage pass, alongside two other candidate learnings from
the same addendum (`L-076`/`L-077`, routed to
`.claude/agents/context-researcher.md` instead — see
`planning/learnings/inbox.md`) and one workflow-pattern candidate
(`L-078`, routed to `planning/v1-redefinition/agent-led-development.md`).

### H1 — §1 "Plan before implementing": extend the already-landed `L-070` sentence to also require testing a present key/entry's own *value validity*, not only a mechanism's minimal-content edge case

- **Context:** `L-070`'s own already-landed `CLAUDE.md` §1 sentence (§G
  above) requires a fail-closed check's verification step to test the
  mechanism's *minimal-content edge case* — an empty, truncated, or
  otherwise maximally-reduced input. Phase 79's sixth amendment found a
  *third* fail-open gap in the same checker lineage that this sentence,
  read literally, would not have required catching: `check_snapshot_completeness`'s
  own Evidence/Derivation closure check validated only that an expected
  key was *present*, never that its own value was well-formed or
  genuinely identified the record it claimed to. Two real attack shapes
  (a nested table silently replaced by a scalar string; an identity swap
  re-pointing a kept key at a different, genuinely-valid record) are
  neither empty nor truncated — both are normal-sized, well-formed-
  looking, and simply wrong. This is a *depth* gap, not a *scope* gap,
  and is a distinct failure shape from the one `L-070`'s own text names.
  Full account: `planning/learnings/inbox.md`'s `L-075`; `decisions/0068`
  item 1; `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  §0 "Sixth revision" entry 1.
- **Proposed text — append, as a new sentence, directly after the
  existing `L-070` sentence in §1 ("...can leave a different one at the
  mechanism's own edge untested. (Phase 79 fifth amendment — L-070.)"):**

  > The same verification step must also cover the mechanism's *depth*,
  > not only its *scope*: when a check confirms that some expected key,
  > field, or entry is present, the test must separately confirm that the
  > entry's own value is well-formed and genuinely identifies or matches
  > what it claims to — a scope fix (checking that the right things are
  > looked at) does not by itself fix a depth gap (how carefully what is
  > found is checked), and closing one does not imply the other is
  > closed. (Phase 79 sixth amendment — L-075.)

- **Alternatives considered:** (a) treat this as already covered by
  `L-070`'s own wording — rejected: independently re-read `CLAUDE.md`
  §1's actual landed text, and its "empty, truncated, or otherwise
  maximally-reduced input" framing does not reach a normal-sized,
  well-formed-looking, but substantively wrong value; a future phase
  following that sentence to the letter would not have been required to
  write the test that caught this bug; (b) replace `L-070`'s sentence
  entirely with a single broader one covering both scope and depth —
  rejected: `L-070` is already landed and user-approved as its own
  citable unit; appending rather than rewriting preserves that approval
  and the phase-attribution trail, matching how `L-021`/`L-070` were
  themselves appended to, not merged into, the paragraph before them; (c)
  route this to `planning/agent-led-workflow.md` instead of `CLAUDE.md`
  §1 — rejected for the same reason `L-021`/`L-070` gave: this is about
  what a phase *plan's own content* must specify regardless of which
  agent or the lead writes the check, not agent-orchestration procedure.
- **Consequences if approved:** `CLAUDE.md` §1 gains the sentence above,
  directly after the `L-070` sentence; `CONTRIBUTING.md`'s mirrored
  section gets the same addition in the same commit; `planning/learnings/inbox.md`'s
  `L-075` flips to `status: promoted` with a `promoted.md` pointer line
  once the edit lands.

## I. 2026-10-07 proposed addition (Phase 81 second corrective pass — `L-087`)

**Status:** approved by the user and landed (`CLAUDE.md`/`CONTRIBUTING.md`
commit `1c3981b`). Filed by
`knowledge-curator` during the Phase 81 second corrective-pass triage,
alongside `L-088` (§J) and a separate scoped-rule recommendation (`L-086`,
routed to `.claude/agents/release-phase-auditor.md` instead — see
`planning/learnings/inbox.md`).

### I1 — §1 "Plan before implementing": require a plan to state how detection differs from acknowledgement, for any new persisted "last-known-state" mechanism

- **Context:** `decisions/0074` point 1 found that `doc-select-candidates`
  advanced both `.grounding-state.toml` and `.doc-chunk-state.toml`
  immediately after every detection run, regardless of whether a finding
  was actually applied or acknowledged — a detected-but-unreviewed
  finding would silently vanish from the next run. This project had
  already independently learned "detection must never itself count as
  acknowledgement" twice before, for two different mechanisms (canonical
  Claim dedup; apply-time concurrency checks, both `decisions/0071`-`0073`)
  — but nothing required that lesson to be checked against a *new* such
  mechanism before it shipped, so it had to be rediscovered a third time
  by a corrective-pass review rather than caught at plan time. Full
  account: `planning/learnings/inbox.md`'s `L-087`; `decisions/0074` §1;
  `planning/retros/phase-81-second-corrective-pass.md` Lessons-learnt
  bullet 2.
- **Proposed text — append to §1, as a new sentence directly after the
  existing `L-075` sentence ("...closing one does not imply the other is
  closed. (Phase 79 sixth amendment — L-075.)"):**

  > If a phase's design introduces a mechanism that persists a
  > "last-known-state" used to decide whether something still needs
  > attention (a baseline, cache, or similar advisory marker), the plan
  > must state explicitly how observing a change differs from acting on
  > it — the persisted state may advance only when an explicit apply or
  > acknowledgement action succeeds, never merely because a detection/scan
  > step ran and found a difference. (Phase 81 second corrective pass —
  > L-087.)

- **Alternatives considered:** (a) treat this as fully covered by the two
  prior, already-landed architecture instances — rejected: both prior
  fixes live in `decisions/0071`-`0073`'s own design, not in `CLAUDE.md`
  §1's plan-content requirements, so a future phase introducing a fourth
  such mechanism has nothing in the governing plan-writing rule itself
  prompting the check; (b) route this to `architecture/overview.md`
  "Known footguns" instead — considered, but a footgun entry documents
  *current* architecture state, while this is a requirement on *future*
  plan content before code is written, matching `L-021`/`L-070`/`L-075`'s
  own placement in §1 rather than `architecture/`; (c) a broader
  "consider all prior ADRs before designing a new mechanism" rule —
  rejected as unenforceable and already implicitly required; scoped
  instead to the one specific, now-thrice-evidenced failure shape.
- **Consequences if approved:** `CLAUDE.md` §1 gains the sentence above;
  `CONTRIBUTING.md`'s mirrored section gets the same addition in the same
  commit; `planning/learnings/inbox.md`'s `L-087` flips to `status:
  promoted` with a `promoted.md` pointer line once the edit lands.

## J. 2026-10-07 proposed addition (Phase 81 second corrective pass — `L-088`)

**Status:** approved by the user and landed (`CLAUDE.md`/`CONTRIBUTING.md`
commit `1c3981b`). Filed by `knowledge-curator` alongside `L-087` (§I)
during the same triage.

### J1 — §1 "Plan before implementing": require an identity-convention check and an insertion/reordering test for any new tracked, re-orderable entity

- **Context:** `decisions/0074` point 10 found grounded-document-region
  baseline identity was purely positional (`"README.md::0"`) — fragile
  under insertion/reordering. This is the exact same failure mode this
  project had already corrected once before, for a different tracked
  entity (anchored intermediate-knowledge blocks, `decisions/0073`'s own
  stable-anchor work), mere hours earlier in the same effort. The two
  mechanisms were implemented separately with no shared identity
  convention, so the fix (a stable explicit id, falling back to positional
  identity only for an un-migrated case, failing closed on a duplicate id)
  had to be independently rediscovered rather than reused. Full account:
  `planning/learnings/inbox.md`'s `L-088`; `decisions/0074` §10;
  `planning/retros/phase-81-second-corrective-pass.md` Lessons-learnt
  bullet 3.
- **Proposed text — append to §1, as a new sentence directly after the
  `L-087` sentence proposed in §I above:**

  > If a phase introduces a new mechanism for tracking a mutable,
  > re-orderable entity (e.g., a document region, anchor, or similar
  > marker that can be inserted, deleted, or reordered), the plan must
  > state whether an existing identity convention elsewhere in the
  > codebase already solves this and, if a new one is introduced instead,
  > the plan's verification section must include a test exercising
  > insertion/reordering of that entity specifically, not only its
  > initial creation. (Phase 81 second corrective pass — L-088.)

- **Alternatives considered:** (a) treat this as a one-off, since the
  first instance (anchored knowledge blocks) was already fixed —
  rejected: the whole point of this filing is that the first fix did not
  generalise to the second mechanism, which is exactly what a plan-time
  check would have caught; (b) require a single shared identity module/
  helper instead of a plan-time question — considered as a stronger fix,
  but out of scope for a governance-doc change (that's a `src/`
  refactor the lead can pursue separately; this amendment only ensures
  the *question* gets asked at plan time, which is cheap and immediate);
  (c) fold into `L-087`'s own sentence as one combined rule — rejected:
  the two failure shapes (state-advancement discipline vs. entity-identity
  stability) are independent enough to warrant separate, separately-citable
  sentences, matching how `L-070`/`L-075` stayed separate despite both
  concerning the same checker.
- **Consequences if approved:** `CLAUDE.md` §1 gains the sentence above,
  directly after the `L-087` sentence; `CONTRIBUTING.md`'s mirrored
  section gets the same addition in the same commit; `planning/learnings/inbox.md`'s
  `L-088` flips to `status: promoted` with a `promoted.md` pointer line
  once the edit lands.
