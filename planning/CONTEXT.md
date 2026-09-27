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
(Phase 73, `CG-006`), Priority B's first hardening step (Phase 74,
`L-031`/`L-032`), and Priority A's first real-task validation trial
(Phase 75) are all done, audited, and closed. **Phase 75 is the current
work and the most recently completed phase** — no phase is yet planned
beyond it. Backlog, each with its own revisit trigger: Phases 24/25,
Phase 50's remainder, `CG-003`, the `browser_api`/`platform_api` kind —
full detail `planning/pre-v1-disposition.md`.

## What was just completed

**Phase 75 — Priority A Ledgerkit validation (real-task evaluation, no
`src/` change).** A genuine baseline-vs-CodeCompass-assisted comparison
on hledger's `cur:` query-term design/discovery task in Ledgerkit's own
query engine, independently rated by `context-evaluator`:
**PASS WITH GAPS, advantage LOW**. `CG-001` stays `candidate`; a new
gap `CG-009` (zero first-party-source symbol index, any ecosystem) was
filed and confirmed `candidate`; `CG-007` got a "no new evidence"
cross-reference. Two process learnings landed: `L-062`
(baseline/treatment dispatch prompts must state read-scope symmetry
explicitly, `reference-project-protocol.md` §2.2) and `L-063` (a
dispatch prompt must never claim a fresh subagent already has access to
conversation-only content, `agent-led-workflow.md` step 7). Full
report: `planning/reference-projects/ledgerkit/04-cur-query-priority-a-validation.md`.
Recommended next step: a second, differently-shaped Priority A
validation trial before any funding decision on `CG-001`/`CG-007` (see
"Next concrete step" below) — not a capability build.

**Undocumented-elsewhere decisions from this phase's closeout, now
recorded here:**

- `CG-001`'s status has a provisional-then-reversed history worth
  remembering exactly: the lead's own gap analysis first moved it
  `candidate` → `recurred` on this phase's evidence; `knowledge-curator`'s
  own independent same-phase triage reviewed that call and reversed it
  back to `candidate` (the evaluation report's own `context-evaluator`
  section had already recommended cross-reference-not-promotion using
  this entry's own established precedent); the lead reviewed and
  concurred with the reversal. The final, authoritative record is
  `planning/context-gaps/inbox.md`'s own `CG-001` entry. This reversal
  was not propagated to four other artifacts on the first closeout
  attempt (`planning/reference-projects/ledgerkit/04-cur-query-priority-a-validation.md`,
  `planning/ROADMAP.md` (both the Priority A row and the `CG-009` row),
  `CHANGELOG.md`, and the phase retro) — `release-phase-auditor`'s first
  completion-audit pass caught this as a real `FAIL` (a cross-document
  propagation defect, not a fabrication); the lead fixed all four plus
  one more, and the re-audit (`planning/retros/_audit-phase-75.md`)
  confirmed every fix landed and swept the repository for the same
  defect class, finding nothing further.
- **Phase 75 is the first phase closed under the corrected closeout
  process** (the `L-060`/`L-061` root-cause fix landed just before this
  phase, `d4f5e0a`, itself following the discovery that Phases 70-74 had
  been self-serving this exact reconciliation step). This
  `roadmap-context-curator` reconciliation is itself part of confirming
  that fix holds — the corrected sequence (drift audit → interim
  reconciliation → retro → learning triage → completion audit →
  only-on-`PASS` final reconciliation) caught a real, non-trivial defect
  on its very first real exercise (the `CG-001` propagation `FAIL`
  above) rather than rubber-stamping the phase, which is direct evidence
  the fix is working as intended rather than merely present in the
  process documents.
- Independently re-confirmed at this reconciliation (not re-derived from
  the audit's own word alone): `pytest` (641 passed, 2 skipped),
  `ruff check .` (clean), `check_user_docs.py --strict` and
  `check_knowledge_base.py` (both clean), `planning/context-gaps/inbox.md`'s
  `CG-001` entry is internally consistent, `L-062`/`L-063` are genuinely
  present at both of their claimed destinations, and no protected file
  (`CLAUDE.md`, `decisions/*`) was touched this phase.

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
- `symbols` has no path for a project's own first-party source, any
  ecosystem (`CG-009`, filed Phase 75) — `vendor_id NOT NULL` FK means
  only tracked vendor dependencies are indexed, never a project's own
  code.
- `vendor/` and a local `.venv/` exist in this checkout (both
  gitignored, freely regeneratable) — live artifacts, not fixtures.

## Next concrete step

Phase 75 is closed. Recommended **Phase 76**: a second, differently-shaped
Priority A validation trial (per
`planning/reference-projects/ledgerkit/04-cur-query-priority-a-validation.md`'s
own "Next-phase recommendation" section) — ideally exercising `CG-001`'s
original intra-`src`-module motivating shape, or a reference-project
corpus less self-descriptively organized than Ledgerkit's own
`dev-docs/planning/core-redefinition/NN-title.md` convention — not a
capability build, and not abandonment of Priority A. No phase plan file
exists yet for this; per `CLAUDE.md` §1, one must be written before any
implementation/evaluation work begins. Beyond that, `CG-001`/`CG-007`
and Priority B's own broader claim/evidence productisation remain
genuinely unplanned design questions, not "smallest justified fix" work.
