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
- A docs-site reversal of `decisions/0039` (Phase 60/61), only if
  reference-project friction shows up.
- The redefined-v1 release itself may warrant a closeout ADR (Phase 66).
