# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and
`planning/retros/` for history; per `CLAUDE.md` §4, this file is for
session-resumption, not a project history.

## Current phase

**CodeCompass v1.0.0 is released.** The redefined-v1 milestone group
(`decisions/0048`, Phases 0–70) is complete and closed: published to
PyPI as the `codecompass-context` distribution (CLI command and Python
import package both stay `codecompass`), tagged `v1.0.0`. Current-state
description of what CodeCompass does: `README.md`,
`architecture/module-map.md`, `docs/quickstart.md` — not this file.
Full status: `planning/ROADMAP.md`. Closeout record:
`planning/v1-closeout.md`.

Post-v1 work is organised into six priorities (A-F,
`planning/ROADMAP.md`'s "Post-v1 priorities" section, `decisions/0062`),
not lettered stages — task-context completeness (Priority A) is the
recommended next concrete phase. Backlog, each with its own revisit
trigger: Phases 24/25, Phase 50's remainder, `CG-003`, the
`browser_api`/`platform_api` kind — full detail
`planning/pre-v1-disposition.md`.

## What was just completed

**Phase 72 — Ledgerkit Stage C learnings capture + post-v1 roadmap
realignment — done (2026-09-27).** Direct user request:
`planning/ledgerkit-stage-c-learnings.md` (new) distils 11 learnings
from Ledgerkit's own Stage C work (studied at Phases 54/54b/54c/61)
into validated observations / design principles / existing-vs-proposed
capability / open hypotheses. `decisions/0062` (new ADR) records the
resulting prioritisation pivot — task-context completeness over graph
completeness — as six priorities (A-F). `planning/pre-v1-disposition.md`
(new) dispositions every material pre-v1 item (Phase 24/25/48/50, GATE
DD/Stage E, open `context-gaps`, `L-031`/`L-032`) so nothing was
silently dropped. `planning/ROADMAP.md`'s old "Deferred/not-funded" and
"Future-improvement backlog" framing replaced by the Priority A-F
structure; `conditional-generalisation.md` gained a dated amendment note
(content otherwise unchanged — GATE DD's own graph-schema questions
remain explicitly open, not resolved by this phase). A domain-corpus
staleness cluster surfaced by the drift audit (7 concept-page/
open-questions locations across two passes, plus the first real
exercise of the Claim-supersedes-Claim mechanism — `CL-EVID-011`/`012`
superseding `CL-EVID-009`/`003`) was found and fixed — the first
remediation commit was itself incomplete (3 sibling instances missed),
caught by `release-phase-auditor`'s own DoD pass finding the drift
audit's report file had never been persisted, then a redone audit
finding the remaining staleness. Closeout: `context-health-planner`
assessment, fork review, `docs-reconstructor` drift audit (two passes),
`domain-skeptic` freshness check (two passes), `context-researcher`
Claim revision, `knowledge-curator` triage (`L-051` promoted — extends
`L-048`'s citation rule to phase-group labels and Claim text).

## Known standing gaps (current-state facts, not phase history)

- Cargo adapter (`decisions/0014`) never validated against real `cargo
  metadata` output or a real crate — no Rust toolchain available yet.
- `extract_npm_symbols` untested against real-world `.d.ts` authoring
  styles beyond hand-written fixtures.
- `chat.py` never run against the real Anthropic API in this
  environment.
- `staleness.py`'s version parser has no real PEP 440/semver
  correctness — string comparison only.
- No formal trigger-accuracy evaluation harness for per-vendor Skills.
- Cursor `.mdc` export has no `globs` field.
- `symbol_enrichment` has no producer/model attribution (`L-031`,
  tracked in `planning/ROADMAP.md`'s future-improvement backlog).
- External-adapter wire protocol's `ecosystem`/`capabilities` fields
  received but not validated (`L-032`, same backlog).
- `vendor/` and a local `.venv/` exist in this checkout (both
  gitignored, freely regeneratable) — live artifacts, not fixtures.

## Next concrete step

Phase 72 is closed. No phase is yet planned for any of Priority A-F —
Priority A (task-context completeness) is the recommended first pick
(`ROADMAP.md`'s Post-v1 priorities table, `decisions/0062`), but needs
its own fresh `planning/phase-N-*.md` scoping pass, not a resumption of
old Phase 48's scope unchanged. Pending: Phase 72's `release-phase-auditor`
DoD pass, then push to `origin`.
