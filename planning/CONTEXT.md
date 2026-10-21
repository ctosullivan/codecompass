# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and
`planning/retros/` for history; per `CLAUDE.md` §4, this file is for
session-resumption, not a project history.

## Current phase

**No roadmap phase is `in progress`.** A v2 strategic roadmap was
established 2026-10-21 (direct user request, `decisions/0078`,
`planning/v2-roadmap.md`), repositioning CodeCompass as an evidence-
backed software change assurance layer (behavioural contracts, semantic
change-impact analysis, an independent oracle, MCP exposure, persistent
reconciled knowledge, and lightweight/optional-governance adoption
levels) rather than a competing coding agent. **Planning only — no
Phase 82-88 implementation has begun**, per the governing prompt's own
explicit instruction. Direct repository inspection this session found no
pre-existing "v2 roadmap," Wiki/MCP/hybrid-orchestration track, or
Pi-local plan committed anywhere in this repository before now
(`decisions/0078`'s own Context section records the evidence for this);
the new roadmap is grounded entirely in genuine current repository state
plus the governing prompt's own content, not in any prior artifact.
`decisions/0062`'s Priority A-F framework is superseded as the primary
strategic framework (content preserved unedited, mapped forward in
`decisions/0078`). Phase 82 ("Contract and Evidence Foundation") is
`planned` (`planning/phase-82-contract-and-evidence-foundation.md`);
Phases 83-88 are sequenced at roadmap depth in `planning/v2-roadmap.md`
but not yet individually phase-planned. Phase 82's own plan proposes one
schema delta (`epistemic_source`, an optional Claim/Requirement field)
requiring explicit maintainer approval before any implementation begins.

**Phase 81B is `done`** (clean-room project redocumentation from
intermediary knowledge, completed 2026-10-09/10 via Amendment 4's
inference-broker mechanism, hardened 2026-10-14 by Amendment 5's
corrective pass on the preparation/isolation machinery itself — six real
defects found and fixed, independently audited twice, `PASS`). Full
detail: `planning/ROADMAP.md`'s own Phase 81B row,
`planning/phase-81b-clean-room-redocumentation.md`, and
`planning/retros/phase-81b-clean-room-redocumentation.md` — not repeated
here (Phase 81B is reused-foundation background for the current v2 work,
not itself current). Phase 81 (the persistent intermediate knowledge
layer the contract model in Phase 82 directly extends) remains `done`,
unmodified. Full prior history for Phases 0 through 81B is in git
history and each phase's own retro/closeout record under
`planning/retros/` (established at Phase 71, `planning/ROADMAP.md` §2).

## What was just completed

**v2 strategic roadmap revision and implementation planning**,
2026-10-21, direct user request, planning only, one session:
inspected actual current repository state across both `codecompass` and
`codecompass-template` (found no pre-existing v2 roadmap, Wiki/MCP/
hybrid/Pi-local plan, contract/oracle code, or MCP dependency anywhere —
an honest finding, not an assumption) → wrote `decisions/0078` (the
strategic ADR: new objective, the governing Understand→Specify→Assess
Impact→Implement→Verify→Reconcile loop, six architectural priorities,
explicit INTENDED/OBSERVED/VERIFIED/UNCERTAIN separation design
decision, and a full Priority A-F → v2 mapping so no existing commitment
from `decisions/0062` is silently lost) → wrote `planning/v2-roadmap.md`
(dependency graph for Phases 82-88, adoption levels, 10-point structure
per phase, a deferred-scope table for everything the governing prompt
named as out of scope for now) → wrote the implementation-ready
`planning/phase-82-contract-and-evidence-foundation.md` (behavioural
contract format reusing the existing Requirement/Claim record model;
the proposed `epistemic_source` schema delta; a minimal oracle-contract/
oracle-result schema; a pinned Ledgerkit reference scenario — candidate
`reports.py::balance_from_spec`, confirmed to exist by direct inspection
of the real sibling checkout — plus its required negative control;
baseline-run identity design respecting `CLAUDE.md` §1's L-087
non-auto-advance rule; deterministic validation including the L-070
minimal-content edge case and the L-075 depth check) → wrote
`planning/v2-migration-assessment.md` (compatibility/versioning/
`codecompass-template`/documentation-maintenance implications — additive
and non-breaking through Phase 85) → wrote
`planning/v2-evaluation-methodology.md` (Phase 86's three-arm comparative
trial design, fixed before any benchmark runs) → updated
`planning/ROADMAP.md` (new "v2 — evidence-backed change assurance"
section with Phase 82-88 rows; the Priority A-F section annotated,
not rewritten, with a pointer to `decisions/0078`) → this
`planning/CONTEXT.md` overwrite → `CHANGELOG.md` entry. No `src/
codecompass/` file, test, or `context-graph.db` schema was touched; no
Phase 82-88 implementation has begun, per the governing prompt's own
explicit instruction to stop after committing planning artefacts.

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
- A submodule pin/checkout mismatch has no field distinguishing
  committed-parent-state divergence from purely local uncommitted
  checkout state (`CG-010`, filed Phase 76) — `codecompass query
  topology` gives the two SHAs and a match/mismatch verdict, but
  determining *why* they differ still requires `git status`/`git diff
  --cached` directly.
- A sibling worktree's dirtiness, when unprobed/stale, is honestly
  reported as such but carries no inline CLI signal that this could be
  the case — only `--help` text documents the sync-time-snapshot
  guarantee (`CG-011`, filed Phase 76).
- `vendor/` and a local `.venv/` exist in this checkout (both
  gitignored, freely regeneratable) — live artifacts, not fixtures.
- Several `.claude/agents/*.md` files still reference the now-deleted
  `docs/domain/` and a bare `architecture/overview.md` (now
  `docs/architecture/overview.md`) as if current — filed as `L-098`
  (`planning/learnings/inbox.md`), not yet acted on (editing
  agent-workflow definitions is its own, separate decision).

## Next concrete step

**Phase 82 implementation requires explicit maintainer approval before
it begins** — specifically, approval of `planning/phase-82-contract-and-
evidence-foundation.md` §9's open decisions (principally the
`epistemic_source` field name/enum, and confirmation that
`reports.py::balance_from_spec` is the right pinned Ledgerkit scenario).
Per the governing prompt's own explicit instruction, Phase 82
implementation has **not** begun and should not begin without that
approval.

Other open items requiring a human/lead decision, none currently claimed
by a drafted plan or phase number:

- Priority A's own narrowly-scoped follow-up trial, sketched (not
  started) in `planning/phase-78-amendment-followup-plan.md` — now
  superseded in strategic priority by Phase 83/85's own, sharper
  change-assurance framing (`decisions/0078`), but not deleted; still
  available if a human decision prefers it first.
- The "Strict mechanical isolation for documentation-reconstruction
  stages" backlog item — `resolved` (Phase 81B Amendment 4), no further
  action pending.
- Phases 83-88 each need their own `CLAUDE.md` §1 planning pass, re-
  scoped against evidence current at that time, once Phase 82 is `done`
  — not drafted in detail yet (`planning/v2-roadmap.md` records only
  roadmap-depth sequencing for them, deliberately).
