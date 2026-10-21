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

**Amended same day (`decisions/0079`, direct user request — "CodeCompass
v2 Planning Amendment — Cross-Project Semantic Overlays")**: reviewed
Phases 82-88 for future compatibility with a generic cross-project
semantic overlay capability (comparing independently-built project
knowledge models, e.g. Ledgerkit/hledger/Ledger/Beancount's shared
accounting concepts — PTA is the motivating use case, not an
architectural dependency). **No Phase 82-88 scope or exit gate
changed.** One real, federation-independent defect was found and fixed
in Phase 82's own not-yet-implemented plan: `epistemic_source`'s
originally-proposed four values (`intended|observed|verified|uncertain`)
were not actually mutually exclusive — corrected to an ordinal scale
(`intended < observed < verified`) with `uncertain` removed (already
covered by the existing `status` field) —
`planning/phase-82-contract-and-evidence-foundation.md` §12. Federation
identity is carried by a new, external, per-project project-identity
envelope (`decisions/0079` §2) — zero change to any existing or
Phase-82-planned canonical record. A new, explicitly gated Post-v2
Cross-Project Semantic Overlay track is recorded
(`planning/post-v2-cross-project-overlay-backlog.md`, seven candidate
stages, each with its own falsifiable exit gate) — not part of the
mandatory Phase 82-88 sequence, not authorised for implementation. Real
repository state checked, not assumed: only `ledgerkit` and `hledger`
exist as local checkouts in this environment; `ledger/ledger` and
Beancount's repository/licence/version state is explicitly unverified
and named as such, not assumed.

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

**Cross-Project Semantic Overlays planning amendment**, 2026-10-21,
direct user request, planning only, one session (same day as, and
amending, the v2 strategic roadmap above): confirmed `HEAD` was still
exactly `bb10927` (the prior session's final commit) with zero drift
before amending anything → wrote `decisions/0079` (three-layer model —
Layer A project-specific knowledge unchanged, Layer B new optional
Domain Concept records, Layer C new Cross-Project Mapping records; a
project-qualified reference envelope external to every existing/planned
canonical record; a six-type relationship enum with explicit
directionality, dropping two of the prompt's eight illustrative names
after finding they overlapped with other fields rather than naming a
distinct relationship shape; the `epistemic_source` correction, found
independent of federation) → amended
`planning/phase-82-contract-and-evidence-foundation.md` §4/§9 in place
and added §12 recording the amendment's own rationale (ordinal
`intended < observed < verified` scale replacing the original,
incorrectly-exclusive four-value enum; `uncertain` removed) — confirmed
no other part of Phase 82's plan, including its exit gate, needed to
change → wrote `planning/post-v2-cross-project-overlay-backlog.md`
(seven candidate stages with falsifiable exit gates, honest
verified-vs-unverified prerequisite check — only `ledgerkit`/`hledger`
exist locally, `ledger`/Beancount do not — dependencies on the Haskell
adapter and Wiki tracks named without blocking either, full risk list)
→ updated `planning/v2-roadmap.md` (a "Federation-compatibility review"
section covering Phases 82-88 individually, none of which changed scope
or exit gate, plus a pointer to the new Post-v2 track) → updated
`planning/v2-migration-assessment.md` (the project-identity envelope is
additive, zero migration) → updated `planning/ROADMAP.md` (Phase 82's
row annotated with the correction; a new Post-v2 track pointer, not a
new numbered phase) → this `planning/CONTEXT.md` overwrite →
`CHANGELOG.md` entry. No `src/codecompass/` file, test, or
`context-graph.db` schema was touched; no repository was created; no
Phase 82-88 phase was renumbered or expanded; Phase 82 implementation
has still not begun.

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
`epistemic_source` field name, now an ordinal three-value scale per
§12's amendment, and confirmation that `reports.py::balance_from_spec`
is the right pinned Ledgerkit scenario). Per the governing prompt's own
explicit instruction, Phase 82 implementation has **not** begun and
should not begin without that approval.

Other open items requiring a human/lead decision, none currently claimed
by a drafted plan or phase number:

- Whether to fund any Post-v2 Cross-Project Semantic Overlay stage
  (`planning/post-v2-cross-project-overlay-backlog.md`) — explicitly not
  authorised by this amendment; Stage 1 cannot begin before Phase 82 is
  `done` regardless.

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
