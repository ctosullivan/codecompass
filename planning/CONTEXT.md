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
`L-031`/`L-032`) are both done, audited, and closed. **Phase 75**
(Priority A Ledgerkit validation, `planning/phase-75-ledgerkit-priority-a-validation.md`)
is the current work, `in progress`. Backlog, each with its own revisit
trigger: Phases 24/25, Phase 50's remainder, `CG-003`, the
`browser_api`/`platform_api` kind — full detail
`planning/pre-v1-disposition.md`.

## What was just completed

**Phases 71-74 are genuinely done, audited, and closed** — each now has
a fresh, independently-run, persisted `release-phase-auditor` completion
audit against its own final state (`planning/retros/_audit-phase-71.md`
PASS, `_audit-phase-72.md` PASS, `_audit-phase-73.md` PASS WITH
NON-BLOCKING OBSERVATIONS, `_audit-phase-74.md` PASS WITH NON-BLOCKING
OBSERVATIONS), closing a real process defect (`L-060`,
`planning/retros/_root-cause-closeout-defect.md`): across these four
phases the lead had flipped `ROADMAP.md`/plan-file status to `done`
before any completion audit ran, and — for Phase 71 — before one had
ever run at all. This reconciliation (`roadmap-context-curator`) is the
first genuinely independent DoD check these four phases have received;
it confirms, rather than assumes, that all `CLAUDE.md` §5 conditions now
hold for each.

**Phase 73 — `mentions_artifact` filename-based matching, closes
`CG-006`.** `build_doc_relations_edges` now also matches a named
target's filename/stem, not only its title (gated through the reused
`_is_specific_enough` noise filter), closing a real gap on the exact
pair `CG-004`'s own fix was motivated by. A follow-on gap
`docs-maintainer` found in the same phase (`relation_enrichment.py`'s
excerpt-needle re-derivation, not updated for the same widening) was
fixed, not deferred. The audit's one non-blocking finding (`CG-006`'s
own structured status field left at `candidate` despite its prose
already saying otherwise) was fixed at `157957b`.

**Phase 74 — Priority B provenance hardening, closes `L-031`+`L-032`.**
`symbol_enrichment.model` added (nullable — an honest backfill, not a
fabricated `NOT NULL` default, for rows whose real producer predates
this column). `ExternalAdapterProcess.initialize` now requires
`expected_ecosystem` and validates it plus `capabilities` against the
closed set, raising `AdapterError` on either mismatch. Both gaps were
documented as open across 11 current-truth/domain-corpus doc
locations — all found and fixed (`docs-reconstructor`'s drift audit
caught 6 the initial `docs-maintainer` pass missed; `domain-skeptic`
verified and named the fix for 5 `docs/domain/` locations, one Claim
supersession — `CL-EVID-008`→`CL-EVID-013`). Two further post-`done`
audit rounds found and fixed three more stale/contradictory
`docs/domain/` locations the original passes missed
(`evidence.md`, two `provenance.md` citations, an intra-file
contradiction in `capability.md`) — see `_audit-phase-74.md` and
`CHANGELOG.md` for the full account. A full independent re-read of all
six touched `docs/domain/` files plus corpus-wide grep sweeps found no
further instance of any of these patterns.

**Outstanding, not part of this reconciliation:** `L-060` itself
(`planning/learnings/inbox.md`, status `candidate`) remains untriaged —
it is a cross-phase (70-74) process learning, not owned by any one of
the four phases' own retros, and needs its own `knowledge-curator`
triage dispatch.

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

Phases 71-74 are closed (see above). **Phase 75** (Priority A Ledgerkit
validation — real-task evaluation of `cur:` query-term implementation
in Ledgerkit, baseline vs. CodeCompass-assisted, independently rated by
`context-evaluator`) is the current work, plan file `in progress`:
`planning/phase-75-ledgerkit-priority-a-validation.md`. Separately,
`L-060` (the phase-closeout process defect these four phases surfaced)
needs a `knowledge-curator` triage dispatch — it is not resolved by this
reconciliation. Beyond Phase 75, no phase is yet planned for the
remainder of Priority A-F — `CG-001`/`CG-007` and Priority B's own
broader claim/evidence productisation remain genuinely unplanned design
questions, not "smallest justified fix" work.
