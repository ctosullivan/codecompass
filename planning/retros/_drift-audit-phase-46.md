# Drift audit — Phase 46 (CodeCompass during a genuine Ledgerkit task)

**Auditor:** docs-reconstructor (MODE 1, per-phase, read-only)
**Base:** working tree vs HEAD `b0717ee` (everything below is uncommitted)
**Plan:** `planning/phase-46-ledgerkit-tasks.md`
**Date:** 2026-09-13

## Verdict

**NO DRIFT.**

## What actually changed about the system

Formed independently from `git status`/`git diff --stat` and full diff
text, not from `docs-maintainer`'s or any other agent's summary:

- New `planning/reference-projects/ledgerkit/01-query-semantics.md` — a
  genuine-task evaluation (hledger 1.52 query-term semantics), two
  sections (`reference-project-tester` friction log +
  `context-evaluator` context-quality evaluation), verdict **FAIL**,
  advantage LOW (negative).
- New `planning/phase-47-consolidate-findings.md` (GATE DB phase plan).
- Modified `planning/reference-projects/ledgerkit.md` (Evaluations table
  row `01` added).
- Modified `planning/context-gaps/inbox.md` (+`CG-003` — external
  `hledger.org` manual has zero CodeCompass representation, no glob fix
  could ever cover it).
- Modified `planning/context-use-log.md` (+1 dated entry, corroborating
  `CG-002`/`L-016` on a live task).
- Modified `planning/learnings/inbox.md` (+`L-017` — live `WebFetch` of a
  large external manual is an expensive, unreliable fallback for
  section-specific content).
- `git diff --stat` + `git status --porcelain` confirm every
  touched/added path is under `planning/`. **No path under
  `src/codecompass/`, `tests/`, `docs/`, `architecture/`, `ai-docs/`, or
  `README.md`.** No CLI behaviour, config schema, generated-file format,
  module responsibility, data model, default, or user-facing error
  message changed.

This is an evaluation phase about an *external* project's use of
CodeCompass. It re-confirms `CG-002` (already filed, already audited as
NO DRIFT in Phase 45) on a live task and files a new, narrower gap
(`CG-003`) and a new learning (`L-017`), both about capabilities
CodeCompass does not have — not about capabilities it claims to have.
There is no current-truth doc describing manual-fetching/vendoring or
claiming full `dev-docs/**` coverage for any current-truth doc to newly
contradict.

## Verification performed (not trusting `docs-maintainer`'s account)

- `git diff --stat` / `git status --porcelain` — full list of touched
  paths, confirmed none under the four current-truth doc roots.
- Read the full diff hunks directly (`context-gaps/inbox.md`,
  `context-use-log.md`, `learnings/inbox.md`, `ledgerkit.md`) plus the
  full text of both new files (`01-query-semantics.md`,
  `phase-47-consolidate-findings.md`), independently of any prior
  agent's summary.
- Independently re-checked the source-code premises the new findings
  rest on, rather than trusting the plan file's or evaluation's account:
  - `src/codecompass/spec_docs.py::_DEFAULT_GLOBS` (lines 21-33) —
    confirmed unchanged since the Phase 45 audit: `README.md`,
    `ARCHITECTURE.md`, `REQUIREMENTS.md`, `PRD.md`, `docs/**/*.md`,
    `architecture/**/*.md`, `decisions/**/*.md`, `spec/**/*.md`,
    `specs/**/*.md`, `rfcs/**/*.md`, `*.spec.md`, `ai-docs/**/*.md`. No
    `dev-docs/**/*.md` entry — `CG-002`'s premise (and its extension to
    nested `dev-docs/**` paths) holds. No mechanism anywhere in this
    codebase fetches or vendors external web documents (no `WebFetch`
    equivalent, no manual-caching code) — `CG-003`'s premise ("no
    representation in any form") holds by absence.
  - Confirmed the diff makes **no** claim that any `src/` behaviour
    changed — both new plan-adjacent entries (`CG-003`, `L-017`) are
    scoped explicitly as "graph-capability" / "future-improvement"
    candidates, not descriptions of current behaviour that could
    misalign with a doc.
- `python scripts/check_user_docs.py --strict` → `no findings`.

## Current-truth product docs checked (README.md, docs/, architecture/, ai-docs/)

| Check | Result |
|---|---|
| `grep -rniE "ledgerkit\|reference.project\|dev-docs\|hledger" README.md docs/ architecture/ ai-docs/ CONTRIBUTING.md` | Four hits, none falsified: `README.md:16` — generic "validated against real external reference-project work", names no specific project/finding, still true. `README.md:205-206` — `decisions/0053`'s GPL relicensing rationale ("aligning with hledger's own licence family ahead of deeper source-assisted, hledger-facing development work"), a licensing decision unrelated to whether CodeCompass can represent the hledger manual (`CG-003`) — no contradiction. `CONTRIBUTING.md:94,128` — generic references to the reference-project/`context-evaluator`/`reference-project-tester` roles and DoD process, unaffected by this specific evaluation's content. |
| `ai-docs/README.md` query-relations examples (lines 72-74) | Both examples (`query relations typer`, `query relations architecture/overview.md`) use paths that *are* covered by `_DEFAULT_GLOBS`/vendor tracking; the doc makes no claim of blanket coverage over arbitrary paths like `dev-docs/**` or external manuals. `CG-002`/`CG-003` don't contradict anything stated here. |
| `docs/cli-reference.md`'s `query relations` "not found" description and `query vendors` description | Unchanged since the Phase 45 audit (no `docs/` diff in this phase); still literally accurate — the doc doesn't claim the error message distinguishes "never scanned" from "typo," and `L-016`/`CG-002`/`CG-003` are all about that undocumented ambiguity/gap, not a doc that asserts otherwise. |
| `architecture/overview.md`'s spec-doc-detection glob enumeration | No diff in this phase; the pre-existing (Phase 45-noted) `ai-docs/**/*.md` omission from the prose list is untouched and unrelated to `CG-003` (which is about content with no glob-representable form at all, not a glob-list omission). |
| Reverse check — did this diff make any existing current-truth-doc sentence false without anyone touching that doc? | None found. No current-truth doc makes a claim about hledger-manual representation, `WebFetch` reliability, or full `dev-docs/**` coverage that this diff's findings (`CG-003`, `L-017`, the `CG-002` recurrence) contradict. |

## Scope note

- Confirmed `docs-maintainer`'s "no current-truth doc needs an edit"
  finding independently, from the diff and source directly (including
  re-deriving the `_DEFAULT_GLOBS` and no-manual-fetching premises
  myself), not from its summary.
- Did not re-litigate whether `01-query-semantics.md`'s two-section
  structure (friction log + reconstructed context-quality evaluation,
  following a `Write`-vs-`Write` race) is internally well-formed or
  faithfully reconstructed — read it end-to-end and it is coherent as a
  single report, but assessing the *process* gap itself (concurrent
  agents racing a `Write` to one path) is a retro/process-improvement
  matter, not a docs-drift one.
- Did not audit `planning/**` content's internal correctness, template
  compliance, or whether `CG-003`/`L-017` are well-formed/correctly
  classified entries — that's `release-phase-auditor` /
  `knowledge-curator` territory, not this drift audit's.
- Did not re-check `CLAUDE.md`/`decisions/*` — out of this audit's
  target-doc set and untouched by this diff.
