# Documentation target — required coverage, expected (not mandatory) structure

Per `planning/phase-81b-clean-room-redocumentation.md` §12.1. Adapt the
exact structure to your own evidence-based findings — do not mechanically
recreate this skeleton if your own research suggests a better
organisation; do cover everything named below somewhere.

```
README.md

docs/
  getting-started.md

  concepts/
    ... (CodeCompass's own domain vocabulary — adapter, vendor,
         ecosystem, context, evidence/observation/claim/decision/
         requirement, digest, provenance, and whatever else your own
         research in knowledge/ and the allowlisted source surfaces as
         a genuinely load-bearing concept)

  architecture/
    overview.md
    components.md
    data-and-control-flow.md

  workflows/
    ... (principal end-to-end workflows — e.g. the sync/enrichment
         pipeline, the knowledge-reconciliation loop, if your own
         research confirms these are current and real)

  reference/
    cli.md
    configuration.md
    protocols.md

  development/
    contributing.md
    testing.md
```

## Required coverage, regardless of final file structure

- Overview / purpose / terminology
- Architecture and major components
- Invariants and constraints
- Interfaces and behaviours
- Workflows and state transitions (where real material exists — see
  `knowledge/workflows-and-state-transitions.md`'s own honest scope)
- Edge cases and compatibility
- Tests and acceptance behaviour (where Requirement-shaped knowledge
  exists — see `knowledge/tests-and-acceptance.md`)
- Decisions and current status (via `knowledge/decisions-and-rationale.md`,
  never the raw ADR corpus, which you cannot see). **Clarified
  2026-10-09, cold-reader finding #3**: that file is a title+status
  index over the full decision history — genuine recoverable rationale
  text exists for only a handful of decisions (the ones discussed inside
  this handoff's own selected knowledge slugs); for the rest, list the
  title and current status honestly and do not fabricate a "why" that
  isn't there. A bare title+status line is a complete, correct entry for
  this section, not an incomplete one.
- Limitations (verify, do not invent — re-derive from current evidence,
  do not assume a limitation exists just because older documentation
  might have mentioned one)
- Open questions and conflicts (`OPEN-QUESTIONS.md`, plus anything you
  yourself cannot resolve)
- A source/evidence trail for your own major claims

## Explicitly not required

- A `docs/development/clean-room-redocumentation.md` page — this is the
  orchestrator's own responsibility to write later, once your output has
  been independently verified, and depends on information (the real
  isolation mechanism/tier achieved) that is not part of your own task.
