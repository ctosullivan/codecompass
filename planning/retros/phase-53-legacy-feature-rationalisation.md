# Phase 53 retro — Legacy feature rationalisation

- **Date:** 2026-09-14
- **Commit(s):** `df7014a` (`docs(phase-53)`, plan + roadmap retarget), plus
  this closeout commit (dead-code removal + architecture doc addition).
- **Agents used:** `docs-maintainer` (architecture reconciliation),
  `docs-reconstructor` (drift audit), `knowledge-curator` (triage),
  `release-phase-auditor` (final pass).

## Where we are

Stage C is done; Stage D's own substantive goal remains an open
strategic decision (Phase 51's retro), unaffected by this phase. This
phase's scope came from a direct user request — a full legacy-feature
audit of everything CodeCompass has shipped since Phase 0 — retargeting
this roadmap slot from Stage D's original "heterogeneous doc/reference/
manual dependencies" sketch, the same findings/decision-driven-scope
precedent Phases 49 and 52 already established.

## Goal

Inventory every runtime feature, classify it (CORE/ADAPTER/TRANSITIONAL/
DEPRECATED/REDUNDANT/REQUIRES EVALUATION), map redundancy, propose a
target architecture, and reach a per-feature KEEP/NARROW/GENERALISE/
MERGE/DEPRECATE/REMOVE/DEFER decision with evidence — with implementation
gated on explicit user review of the plan's product-direction
recommendations, not decided unilaterally.

## Scope delivered vs planned

Delivered exactly as scoped in
`planning/phase-53-legacy-feature-rationalisation-plan.md`: a full
inventory (15 features/subsystems), a 3-item redundancy map, a
documentation-level target-architecture grouping (CORE/AGENT/HOST-OUTPUT
ADAPTERS — deliberately *not* a `src/` restructuring, per the prompt's
own scope exclusions), and six per-feature recommendations. At the
review gate, the user approved all three recommended options
(keep direct-API enrichment unchanged; keep `chat.py` unchanged; defer
the two doc-only findings to a documentation note rather than new
tooling) — the plan's one pre-approved-shape action (remove dead code)
and the doc-only deferrals were then implemented in this closeout.
Nothing was implemented before the gate; nothing beyond what was
approved was implemented after it.

## What was achieved

1. **The inventory itself** — the first time every one of CodeCompass's
   23 runtime modules + 5-module `adapters/` package + 3 planning queues
   has been catalogued in one place with purpose, caller, evidence, and
   classification side by side. This surfaced one genuinely dead function
   (`discovery.py::rewrite_vendor_toml`, unused since `promote`'s Phase
   15 retirement) that had sat, correctly self-documented as unused, for
   38 subsequent phases without ever being acted on.
2. **`discovery.py::rewrite_vendor_toml` removed**, along with its
   dedicated test — 11 lines + 1 test, zero other callers, zero doc
   references, confirmed by `docs-reconstructor`'s independent grep.
3. **`architecture/overview.md` gained a `## Module tiers: CORE, AGENT,
   HOST-OUTPUT ADAPTERS` section** — the first place in the repo that
   states, as a single coherent grouping, which modules are host-agnostic
   core logic, which are interchangeable enrichment producers, and which
   are Claude-Code/Cursor-specific output renderers. Plus a one-sentence
   disambiguation of "adapter" (ecosystem package-manager sense,
   pre-existing) from "host-output adapter" (this phase's new sense), and
   a caveat naming the Skill/`/discovery`/CLI-docs command-list
   duplication as a real, small, hand-synced maintenance burden.
4. **A genuine product-direction decision reached at the review gate,
   not unilaterally**: direct-API enrichment and `chat.py` both stay
   exactly as they are, on the evidence that neither has been shown
   broken or harmful by anything this phase (or any prior reference-
   project evaluation) found — only *unavailable in this one development
   environment* (no configured `ANTHROPIC_API_KEY`), which Phase 52's
   agent-driven path already and sufficiently addresses for this
   project's own dogfooding, without requiring either legacy module's
   removal.
5. **Two now-stale planning-doc pointers corrected**: `CG-003`/`L-017`
   were previously routed to "Stage E/Phase 53" in `CONTEXT.md` and
   `planning/reference-projects/ledgerkit/findings.md`; since this
   phase's own retarget took that number, both were updated to point at
   "a future Stage D/E phase, number unresolved" instead of a now-wrong
   specific number.

## What worked

- **Treating "requires evaluation" as a real, distinct outcome from
  "keep" or "remove."** Several features (direct-API enrichment,
  `chat.py`) had a plausible case for removal *and* a plausible case for
  keeping — forcing the plan itself to pick one would have meant
  unilaterally deciding a product question. Presenting three real options
  at the gate (not a single recommendation dressed as the only choice)
  produced a clean, fast, genuinely-informed decision.
- **Setting an explicit evidence bar for REMOVE before doing the
  inventory**, not after: "no known caller *and* no reference-project
  evidence" turned out to cleanly separate the one real dead-code case
  from every other candidate, which had at least one of the two.
- **Checking the "initial-chat" candidate against the actual codebase
  before writing a recommendation for it** — grepping first rather than
  assuming the prompt's phrasing pointed at real code caught that this
  candidate has never actually shipped, which would have been an
  embarrassing thing to get wrong in a rationalisation plan meant to be
  authoritative about what exists.

## What didn't work

- Nothing new this phase. The one friction point worth naming isn't a
  failure so much as a scale mismatch: a request this broad ("scrutinise
  everything the project has ever shipped") naturally produces mostly
  "keep, no evidence of a problem" verdicts once evidence-based removal
  is the bar — a useful, honest result, but one that could read as an
  anticlimax against the size of the request. Naming this explicitly
  rather than manufacturing more removals to look more thorough.

## Lessons learnt

1. **A legacy-feature audit's most valuable output can be "confirmed
   fine, here's the evidence" as often as "remove this."** Padding the
   removal count to look more thorough than the evidence supports would
   have been a worse outcome than five honest KEEP/DEFER verdicts plus
   one small, clean removal.
2. **When a prompt names a candidate by a concept ("initial-chat
   functionality") rather than a file, verify the concept actually
   corresponds to shipped code before writing a recommendation about it**
   — the correct finding was "this doesn't exist," not a KEEP/REMOVE
   judgment about something that was never built.
3. **A "target architecture" doesn't have to mean a `src/`
   restructuring.** Stating an existing, already-implicit grouping
   explicitly in a doc gave the prompt's "clearer core product boundary"
   goal (retro question 7) real value without any of the churn a literal
   package reorganisation would have cost — matching this project's own
   standing "don't refactor beyond what a task requires" convention
   turned toward its own architecture-review process.

## Process-improvement feedback

None new for the agent-led workflow itself. The plan-then-explicit-gate-
then-implement structure (distinct from most phases' plan-then-implement)
worked cleanly using the existing `AskUserQuestion` mechanism — no new
process machinery was needed to support a phase whose plan is mostly
recommendations rather than a fixed implementation.

## Candidate learnings filed

None new this phase — the process worked as designed, with no surprising
friction to capture as a `learnings/` candidate. (Contrast with Phase 52,
which surfaced `L-019` from a genuine live-demo anomaly; this phase's
work was desk investigation plus one small, unsurprising code removal.)

## Where we're going

- **Next: unclear, genuinely, and unaffected by this phase.** The Stage
  D-vs-Stage-F/G strategic decision (Phase 51's retro) remains exactly as
  open as it was before Phase 52 and Phase 53 both retargeted their
  roadmap slots to unrelated scope. Stage D's own substantive goal
  (heterogeneous doc/reference/manual dependencies against Ledgerkit) has
  no phase number assigned to it now that both 52 and 53 are spent —
  whichever path the user picks next, it starts at Phase 54 or later.
- **Trajectory:** this phase reduces standing technical debt (one dead
  function) and clarifies the project's own self-description
  (`architecture/overview.md`'s new tier grouping) without changing
  behavior or resolving the open Stage D/F/G fork — purely additive
  clarity, like Phase 52 before it.

## Retrospective questions (per the governing prompt)

1. **Which features were genuinely redundant?** Exactly one:
   `discovery.py::rewrite_vendor_toml` — dead code with zero callers
   since `promote`'s Phase 15 retirement, zero doc references, self-
   documented as unused for 38 phases. No other feature met the REMOVE
   evidence bar (no caller *and* no reference-project signal).
2. **Which features initially appeared redundant but proved valuable?**
   Direct-API vendor/symbol/relation enrichment (`enrichment.py`,
   `relation_enrichment.py`) — plausible to suspect Phase 52's
   agent-driven path made these redundant, but they remain the only path
   that has ever produced real enrichment content in any environment with
   a configured `ANTHROPIC_API_KEY` (including this project's own
   self-dogfooded `vendor/*/CLAUDE.md`); Phase 52's fixture demo never
   touched or threatened this. `chat.py` similarly looked like a natural
   removal candidate (zero reference-project evidence of use, never run
   against a real API in this environment) but `decisions/0034` had
   already weighed exactly this tradeoff and chose keep-as-secondary, on
   reasoning this phase's investigation found no new evidence to unseat.
3. **How much architecture/configuration/code was simplified?** Modestly,
   by design: 11 lines of dead code + 1 test removed; one new
   documentation section clarifying an already-implicit module grouping
   (no code moved, no package restructured). This phase's evidence bar
   (proven redundancy, not suspected redundancy) intentionally limited
   removal to what the evidence actually supported.
4. **Were any user-visible capabilities lost?** No. The one removal
   (`rewrite_vendor_toml`) had no caller and was never exposed through any
   CLI command, so no user-visible behavior existed to lose.
5. **Did rationalisation reduce duplicated responsibility?** Not by code
   change this phase (no duplication met the evidence bar for
   consolidation), but the inventory *named* the one real duplication
   found (the Skill/`/discovery`/CLI-docs command-list triplication) as a
   tracked, documented maintenance burden for the first time, rather than
   three independently-evolving copies with no cross-reference between
   them.
6. **Did any removal expose unexpected coupling?** No — `pytest`/`ruff`
   stayed clean before and after with no other change required, matching
   the pre-removal analysis that found zero callers.
7. **Did CodeCompass's core product boundary become clearer?** Yes — the
   new CORE/AGENT/HOST-OUTPUT ADAPTERS section is the first place this
   boundary is stated explicitly as a named grouping rather than left
   implicit across 23 modules' individual docstrings, and it disambiguates
   a real terminology collision (`adapters/` package vs. "adapter" as a
   concept) that had never been flagged before.
8. **What remaining transitional architecture should be revisited
   later?** `chat.py` remains the one module that doesn't cleanly fit
   CORE/AGENT/HOST-OUTPUT ADAPTERS (flagged as SECONDARY, a genuine
   fourth category) — worth revisiting only if real usage evidence ever
   appears, per `decisions/0034`'s own standing position. The
   Skill/`/discovery`/CLI-docs command-list triplication (§5.5 of the
   plan) is now a named, deferred item for whenever a future `query`
   subcommand addition next touches it.
9. **Did the phase produce evidence for the next roadmap decision?** No —
   consistent with Phase 52, this phase produces no new evidence toward
   the Stage D-vs-Stage-F/G decision (Phase 51's retro). It is a
   self-contained architecture review of already-shipped code, not a
   Ledgerkit-facing evaluation; the strategic decision remains exactly as
   open as it was.

## Time / cost note

Single session, continuing directly from Phase 52 (same day). No AI
enrichment spend — this phase's own investigation was direct code
reading, not enrichment. `pytest` 567 passed / 2 skipped (from 569
collected, down 1 from the removed test), `ruff check .` clean,
`check_user_docs.py --strict` clean throughout.

## Closeout audit trail

`release-phase-auditor` ran **multiple rounds** (see
`planning/retros/_audit-phase-53.md` for the full report and final
verdict) — a longer trail than Phase 43's own "FAIL → FAIL → PASS" GATE
DA precedent, though the same shape: every gap found was governance-doc
bookkeeping, never a code or substance defect.

- **Round 1 (FAIL):** `CHANGELOG.md` still read "Plan only, awaiting
  review gate; no code changed yet" after the dead-code removal and
  architecture-doc addition had already landed — a document in the tree
  asserting something false about the code's actual state. Also flagged:
  no persisted `planning/retros/_drift-audit-phase-53.md` existed despite
  the audit having been run, breaking the independently-checkable
  evidence trail the per-phase drift-audit step exists to provide.
- **Round 2 (FAIL):** both prior gaps confirmed fixed, but the same
  re-check surfaced `planning/ROADMAP.md` row 53 and
  `planning/CONTEXT.md`'s "What was just completed"/"Next concrete step"
  sections *also* still describing the phase as unimplemented/awaiting
  the review gate — the identical root defect (a governance doc
  asserting "not yet done" post-implementation) surviving in two more
  files the first fix pass hadn't touched.
- **Round 3 (FAIL):** `ROADMAP.md`/`CONTEXT.md` confirmed brought
  current, and this round wrote the audit's own persisted report
  (`planning/retros/_audit-phase-53.md`, the first round to do so — the
  omission itself had been part of round 1's finding). But the same
  stale-claim defect recurred a *fourth* time: `planning/
  v1-redefinition/roadmap.md`'s own Phase 53 stanza still read
  "Retargeted (2026-09-14), plan awaiting review gate — not yet done"
  and "No implementation has happened yet" — a file the round-2 fix pass
  believed it had covered but hadn't (it had fixed `ROADMAP.md` and
  `CONTEXT.md`, not the separate `v1-redefinition/roadmap.md` stanza).
  Fixed, and a full-repo grep re-run to confirm no fifth file carries the
  same pattern.
- **Round 4 (FAIL):** the `v1-redefinition/roadmap.md` fix confirmed
  landed correctly — but a fifth instance of the same defect class
  surfaced, this time self-referentially: `planning/CONTEXT.md`'s own
  Phase 53 paragraph mischaracterized the *audit trail itself*, claiming
  "FAIL → FAIL → PASS across three rounds" and "both flipped to `done`
  in this commit" when there had by then been four rounds (round 3 was a
  FAIL, not the third-and-final PASS the sentence implied), across more
  than one commit. Fixed by rewording `CONTEXT.md`'s claim to point at
  this retro and the persisted audit report for the exact round count
  and verdict, rather than asserting a specific number inline that a
  further round could immediately falsify again — breaking the pattern
  going forward rather than chasing it one more time.
- **Round 5 (FAIL):** the round-4 fix's *structure* (pointing
  `CONTEXT.md` at the audit report rather than asserting a round
  count/verdict inline) held, but its wording still smuggled in a new
  specific, checkable claim — "never the same file twice, but the same
  defect class each time" — which was itself false (`CONTEXT.md` was
  the subject of two separate FAILs, round 2 and round 4, not one; round
  4's actual defect wasn't "asserting not yet implemented," it was a
  wrong claim about the audit's own round count). Fixed by removing the
  characterization entirely rather than attempting a third, more-precise
  version of it — the sentence now states only that a multi-round trail
  happened and where to find its record, with no claim left to falsify.
- **Subsequent rounds, if any, and the final verdict:** see
  `planning/retros/_audit-phase-53.md`, which is the authoritative,
  continuously-updated record — this retro intentionally does not
  duplicate the exact final round count/verdict inline, for the same
  reason the round-4/round-5 fixes above gave.

This is itself a small, honest process finding: **fixing a "doc says
X, code now says not-X" gap in one file doesn't guarantee every other
file making the same claim got fixed too** — the DoD's own multi-file
reconciliation step (`CHANGELOG.md` + `CONTEXT.md` + `ROADMAP.md`, all
three, every phase) exists precisely because a single-file fix is an
easy place to stop early. Not filed as a new `learnings/` candidate
(per `knowledge-curator`'s own reasoning above, this is the standing
"verify independently, every time" discipline working as designed, not
a new gap in it) — but worth naming here for anyone reading this retro
who wonders why the audit trail has three rounds instead of one.
