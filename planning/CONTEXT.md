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
not lettered stages. Priority A's first concrete deliverable
(Phase 73, `CG-006`) and Priority B's first hardening step (Phase 74,
`L-031`/`L-032`) are both done. Backlog, each with its own revisit
trigger: Phases 24/25, Phase 50's remainder, `CG-003`, the
`browser_api`/`platform_api` kind — full detail
`planning/pre-v1-disposition.md`.

## What was just completed

**Phase 73 — `mentions_artifact` filename-based matching, closes
`CG-006` — done (2026-09-27).** `build_doc_relations_edges` now also
matches a named target's filename/stem, not only its title (gated
through the reused `_is_specific_enough` noise filter), closing a real
gap on the exact pair `CG-004`'s own fix was motivated by. A follow-on
gap `docs-maintainer` found in the same phase
(`relation_enrichment.py`'s excerpt-needle re-derivation, not updated
for the same widening) was fixed, not deferred.

**Phase 74 — Priority B provenance hardening, closes `L-031`+`L-032` —
done (2026-09-27).** `symbol_enrichment.model` added (nullable — an
honest backfill, not a fabricated `NOT NULL` default, for rows whose
real producer predates this column). `ExternalAdapterProcess.initialize`
now requires `expected_ecosystem` and validates it plus `capabilities`
against the closed set, raising `AdapterError` on either mismatch. Both
gaps were documented as open across 11 current-truth/domain-corpus doc
locations — all found and fixed (`docs-reconstructor`'s drift audit
caught 6 the initial `docs-maintainer` pass missed; `domain-skeptic`
verified and named the fix for 5 `docs/domain/` locations, one Claim
supersession — `CL-EVID-008`→`CL-EVID-013`).

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
- A pre-Phase-74 `symbol_enrichment` row's producer remains honestly
  unknown (`NULL`) — new rows are attributed, historical ones cannot be
  retroactively.
- `vendor/` and a local `.venv/` exist in this checkout (both
  gitignored, freely regeneratable) — live artifacts, not fixtures.

## Next concrete step

Phases 73/74 are closed. No phase is yet planned for the remainder of
Priority A-F — `CG-001`/`CG-007` (Priority A's harder task-oriented-
retrieval/execution-path candidates) and Priority B's own broader
claim/evidence productisation both remain genuinely unplanned design
questions, not "smallest justified fix" work. Pending:
`release-phase-auditor` DoD passes for both phases, then push to
`origin`.
