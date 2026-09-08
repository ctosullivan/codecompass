# 0048. Redefined v1 is a product-validation milestone, not a packaging milestone

## Status

Accepted (Phase 39, `planning/v1-redefinition/`).

## Context

The repository's internal "v1.0" (`planning/v1.0-initial-release-roadmap.md`,
Phase 23) means one thing: publish the npm/PyPI/Cargo package/source-
grounding tool to PyPI and cut a `v1.0` tag. Phase 23 Part A (packaging
readiness) is `done`; Part B (the publish) has been paused for explicit
confirmation for several phases.

Three facts made this the wrong place to plant the v1 flag:

1. **Nothing has ever been published.** No PyPI release, no git tags,
   `v0.1`/`v0.2` never cut (`decisions/0022`, `0030`). There is no public
   release history to preserve — the redefinition is unconstrained by it.
2. **No evidence of value.** `decisions/0039` itself records that the
   project has no external users and any decision made now "is
   necessarily speculative." Every phase since 20 was found by
   CodeCompass dogfooding *itself* — a single Python project with four
   dependencies. The tool has never been pointed at a project it wasn't
   also developing.
3. **The first two intended real targets don't fit the model.** The
   redefined-v1 planning session inspected both reference projects:
   Technical Clipper (`https://github.com/ctosullivan/technical-clipper`)
   has 0 runtime dependencies and ~7 build-only devDependencies;
   Ledgerkit (`https://github.com/ctosullivan/ledgerkit`) is pure Python
   with 0 runtime dependencies. Their real technical context is browser
   extension / DOM APIs and the CommonMark spec (Technical Clipper); the
   `hledger` executable, its manuals, and journal syntax (Ledgerkit).
   CodeCompass's current package/source model produces a near-empty
   result for both.

Publishing `1.0.0` now would spend SemVer's "first stable public API"
signal on an unvalidated snapshot and make "v1" mean two different things
(the published wheel vs. the internal milestone).

## Decision

**Redefine "CodeCompass v1" as a product-validation milestone**, planned
in full in `planning/v1-redefinition/` (umbrella package; `roadmap.md`
stages A–F, phases 39–67):

- **Stage A** — CodeCompass becomes agent-led (a lead session + a small
  specialist agent roster; `decisions/0049`), with continuous
  doc/roadmap maintenance, a project-learning lifecycle, and an
  independent completion audit, dogfooded on a real change.
- **Stage B** — validate the *current* CodeCompass against genuine
  Technical Clipper development work, with independent context-quality
  evaluation.
- **Stage C** — improve the existing product, *only* where Stage B
  evidence supports it (gated).
- **Stage D** — test the broader hypothesis against Ledgerkit
  (heterogeneous docs / executable / behavioural context).
- **Stage E** — implement the *minimum* generalisation Stage D justifies
  (gated; may be empty).
- **Stage F** — blank-slate documentation reconstruction, architecture/
  ADR/roadmap reconciliation, final reference-project validation,
  independent release audit, milestone closeout, release.

**Versioning:**

- All publishing is **held until the redefined v1** (gate G2 → G2-b).
  CodeCompass has never been published; the first-ever PyPI release is
  the redefined v1, shipped as `1.0.0` at Phase 67.
- In the interim `pyproject.toml` carries **`1.0.0.dev0`** — accurately
  "in development toward the 1.0.0 Phase 67 ships", consistent with the
  project's prior practice (`version = "0.1.0.dev0"` before Phase 23,
  `decisions/0047`). Phase 67 drops the `.dev0` suffix.
- `CHANGELOG.md`'s `[Unreleased]` section is not promoted to a dated
  section until Phase 67.
- Milestone-grouping convention holds (`CLAUDE.md` §6,
  `decisions/0022`/`0030`): stages A–F are one milestone group; the
  `v1.0.0` tag is cut only on group completion.

**Phase 23 disposition:** Part A stays `done`. Part B is **superseded** —
the first publish is the redefined v1 (Phase 67). Phases 24 (chat
routing/rollup) and 25 (MCP) are marked **deferred** (not renumbered) —
24 a Stage C candidate conditional on reference-project evidence, 25
post-redefined-v1.

**The exact breadth of v1** (whether it generalises beyond package/source
grounding, and how far) is deliberately **not decided here** — it is the
output of Stages B–D's evidence gates (`planning/v1-redefinition/
conditional-generalisation.md`), not an input.

## Alternatives considered

- **Publish `1.0.0` now as planned (the existing Phase 23 Part B).**
  Rejected: spends the "first stable public API" signal on a snapshot
  that has never been validated against a real external project, and
  makes "v1" ambiguous between the wheel and the milestone.
- **Keep the packaging definition of v1; treat validation as v2.**
  Rejected: the redefinition was explicitly requested, and a v1 that has
  never been pointed at a project it wasn't also developing cannot
  credibly carry the "context layer for AI development agents"
  positioning the redefined product direction adopts.
- **Publish a `0.4.0` foundation release now** for early external
  signal, holding `1.0.0` for the redefined v1. Considered and **not
  chosen** (gate G2-b): lower external surface area during a period of
  likely schema change was preferred over the early signal. Recorded as
  a revisitable preference, not a one-way door — if the publishing hold
  starts to bite, an interim `0.x` release can still be cut.
- **Bump `pyproject.toml` to `0.4.0` rather than `1.0.0.dev0`.**
  Rejected: under G2-b no `0.4.0` will ever be released, so labelling the
  in-repo version `0.4.0` invents a phantom release; `1.0.0.dev0` is
  accurate.

## Consequences

- `planning/ROADMAP.md` gains a "Redefined CodeCompass v1 — Stages A–F"
  milestone-group section (phases 39–67); historical tables and the
  dated "v1.0 scope notes" are **not edited** (same treatment superseded
  ADRs get) — a single reframing note above them says "v1.0" there now
  means the foundation release.
- `pyproject.toml` reads `1.0.0.dev0`; `README.md` / `docs/cli-reference.md`
  / `ai-docs/` reframed from "v1.0.0 in progress" to "phases 0–38 (the
  foundation) done; CodeCompass v1 redefined as a product-validation
  milestone, in progress — not yet released."
- `CLAUDE.md` §6 gains a milestone note distinguishing "CodeCompass v1"
  (the product milestone) from the `pyproject.toml` version string — a
  separate, `CLAUDE.md` §0-gated change (gate G4), not bundled into
  Phase 39.
- The agent-led development model is a hard prerequisite (`decisions/0049`,
  Stage A) before any large speculative architecture work.
- Later stages (C, E) are explicitly revisable based on earlier stages'
  findings; the plan carries a defined "minimum viable redefined v1"
  fallback so it can conclude with a modest, real, shipped improvement
  rather than delay v1 indefinitely.
- If a future phase re-opens the publishing hold or the milestone
  definition, it supersedes this ADR with a new numbered one
  (`CLAUDE.md` §2 append-only rule).
