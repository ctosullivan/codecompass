# Phase 44: Reference-project protocol + context-quality eval spec

**Status:** planned

Stage B, first phase. Turns
`planning/v1-redefinition/reference-project-protocol.md` and
`context-quality-evaluation.md` into operational templates and a registry.
No reference project is registered yet (that is Phase 45).

## Depends on

- Phase 43 done / GATE DA passed (roster amended).

## Scope

**In scope:**

- Create `planning/reference-projects/`:
  - `README.md` — the registry: a table of registered reference projects
    (name, URL, starting revision, current status, link to its record)
    and a short "how a reference-project evaluation runs" pointing at the
    protocol doc.
  - `TEMPLATE-registration.md` — the per-project registration record
    schema (`reference-project-protocol.md` §2.1: repo URL, starting
    revision, per-evaluation pinned revision, CodeCompass revision, and
    the per-task fields).
  - `TEMPLATE-evaluation.md` — the per-task context-quality evaluation
    report structure (`context-quality-evaluation.md` §2, verbatim as a
    fill-in template).
- Finalise the `context-evaluator` and `reference-project-tester` agent
  briefs against these templates (they were created in Phase 40 with
  placeholder method sections).
- **Instrument sanity check:** run a dry-run evaluation of CodeCompass
  *against its own repo* using `TEMPLATE-evaluation.md` for one question
  (e.g. "what does this project use `typer` for and at what version").
  This is **not a real datapoint** — it checks the template produces a
  coherent, complete report and that the `context-evaluator`'s
  "inspect directly, don't use CodeCompass to check CodeCompass" rule is
  followable. Store it at
  `planning/reference-projects/_instrument-dry-run.md` clearly labelled
  as a self-test.
- ADR: none expected.

**Explicitly deferred / out of scope:**

- Cloning / registering Technical Clipper — Phase 45.
- Any real evaluation datapoint.
- Any `src/codecompass/` change (this is all `planning/` + `.claude/`).

## Design decisions

- **Templates, not prose.** A future session fills in a template; it
  doesn't re-derive the structure from the design docs.
- **The dry-run is a self-test, not evidence** — labelled as such so it's
  never aggregated into findings.
- **`planning/reference-projects/` is the home for all Stage B/D
  evaluation output** — keeps it out of `planning/v1-redefinition/`
  (which is the plan) and out of the repo root.

## Files

- `planning/reference-projects/README.md` — new
- `planning/reference-projects/TEMPLATE-registration.md` — new
- `planning/reference-projects/TEMPLATE-evaluation.md` — new
- `planning/reference-projects/_instrument-dry-run.md` — new (self-test)
- `.claude/agents/context-evaluator.md` — brief finalised
- `.claude/agents/reference-project-tester.md` — brief finalised
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` — curator
- `planning/phase-45-technical-clipper-baseline.md` — written now that
  the protocol is concrete (per `CLAUDE.md` §1, before Phase 45 starts)

## Verification

- `python scripts/check_user_docs.py --strict` clean (new files linked,
  links resolve).
- The dry-run report is complete against `TEMPLATE-evaluation.md` — every
  section filled, a verdict and an advantage rating present, and the
  "could a fresh session get this cheaply?" question answered.
- `context-evaluator` confirms (in the dry-run) it reached its ground
  truth by direct inspection, not by running `codecompass query`.
- `pytest` / `ruff check .` clean.

## Done when

Standard DoD + verification + Phase 45's plan file exists +
`release-phase-auditor` PASS + learnings triaged.
