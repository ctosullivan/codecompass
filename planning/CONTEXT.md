# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and
`planning/retros/` for history; per `CLAUDE.md` §4, this file is for
session-resumption, not a project history.

## Current phase

**No roadmap phase is `in progress`.** A v2 strategic roadmap exists
(`decisions/0078`, `planning/v2-roadmap.md`), repositioning CodeCompass
as an evidence-backed software change assurance layer (behavioural
contracts, semantic change-impact analysis, an independent oracle, MCP
exposure, persistent reconciled knowledge, lightweight/optional-
governance adoption levels) rather than a competing coding agent, plus
an explicitly gated, not-yet-authorised post-v2 Cross-Project Semantic
Overlay track (`decisions/0079`, `planning/post-v2-cross-project-
overlay-backlog.md`). **Planning only — no Phase 82-88 implementation
has begun, no repository was created, no phase was renumbered or
expanded.** Full amendment history and rationale lives in each
amendment's own ADR, not restated here:

- `decisions/0078` — the original v2 repositioning (no prior v2 roadmap
  existed in this repository before it; see that ADR's own Context
  section for the evidence).
- `decisions/0079` — the Cross-Project Semantic Overlay track's three-
  layer model (project-specific knowledge / shared domain concepts /
  cross-project mappings) and project-qualified reference envelope.
- `decisions/0080` — corrects Phase 82's epistemic-state design a
  second time (the field this ADR removes was itself a same-day
  correction of `decisions/0078`'s original proposal, found still
  wrong) and strengthens oracle-result identity; also extends
  `decisions/0079`'s envelope with a publisher/authority distinction and
  refines three Post-v2 overlay stages (hledger evidence-sourcing,
  Stage 5's design/empirical split, Stage 7's accounting-generalisation
  vs. domain-independence split).

**Current state of Phase 82** (`planned`,
`planning/phase-82-contract-and-evidence-foundation.md`): INTENDED/
OBSERVED/VERIFIED/CONTESTED is a **derived, read-time view** computed
from existing Phase 81 Requirement/Claim/Evidence/Observation records —
**no new field on any canonical record** — reusing
`knowledge_intermediate.py::derive_provenance_label`'s own already-
proven pattern. Oracle-result identity is bound to the exact tested
subject via a content digest (not a bare commit SHA, so a dirty
worktree cannot masquerade as a tested commit), with explicit fields
distinguishing a run's identity, the baseline it's measured against,
the contract/checks/inputs actually executed, and tamper-evident raw
output. Implementation requires explicit maintainer approval of the
plan's own §9 before it begins.

`decisions/0062`'s Priority A-F framework remains superseded as the
primary strategic framework by `decisions/0078` (content preserved
unedited, mapped forward there). Phase 81B (clean-room redocumentation,
`done`) and Phase 81 (the intermediate knowledge layer Phase 82 directly
extends, `done`) are reused-foundation background, unmodified by any v2
planning session — full detail in `planning/ROADMAP.md`'s own rows and
each phase's retro, not repeated here (established at Phase 71).

## What was just completed

**Corrective planning amendment**, 2026-10-21, direct user request
("CodeCompass v2 — Corrective Planning Amendment"), planning only, one
session: confirmed `HEAD` was exactly `47ab61c` (the prior session's
final commit) with zero drift before amending anything → read
`src/codecompass/knowledge_intermediate.py` and `scripts/check_
knowledge_base.py` directly (not only prior planning prose) and found
`derive_provenance_label` already solves the identical problem shape
Phase 82's epistemic field was trying to solve, and that `status:
verified` already existed, previously unenforced, on both Claim and
Requirement → wrote `decisions/0080` (epistemic state fully corrected to
a derived view after the prior ordinal-scale fix was itself found still
wrong; oracle-result identity bound to an exact tested-subject content
digest, not a commit reference; project-identity envelope extended with
`publisher_id`/`authority`) → rewrote
`planning/phase-82-contract-and-evidence-foundation.md` §4 in place
(removing `epistemic_source` entirely), strengthened §5's oracle-result
schema, added five new negative controls and a new validator rule to
§6/§8/§9/§10, and appended §13 recording this amendment's own rationale
and supersession chain → corrected three Post-v2 overlay stages in
`planning/post-v2-cross-project-overlay-backlog.md` (Stage 2: hledger
evidence without an implicit Haskell-adapter dependency; Stage 5: split
into a design-only exit gate with empirical comparison explicitly
deferred; Stage 7: split accounting-backend generalisation from the
genuinely-unrelated-domain validation required for any domain-
independence claim) and added a snapshot-authority-confusion risk →
updated `planning/v2-roadmap.md`'s Phase 82 federation-review entry,
`planning/v2-migration-assessment.md`, and `planning/ROADMAP.md`'s Phase
82 row and Post-v2 pointer → this `planning/CONTEXT.md` rewrite (also
consolidating three layered amendment narratives into one current-state
description, per §4's own overwrite discipline) → `CHANGELOG.md` entry.
`decisions/0078`/`0079` were not edited (append-only). No `src/
codecompass/` file, test, or `context-graph.db` schema was touched; no
repository was created; no Phase 82-88 phase was renumbered or expanded;
Phase 82 implementation has still not begun.

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
it begins** — specifically, §9's two open items: the derived-view
epistemic design itself (no field to name — confirm the approach,
including repurposing the pre-existing, previously-unenforced `status:
verified` value), and the oracle-result identity field set (`run_id`,
`tested_subject_digest`, `oracle_contract_content_hash`,
`test_input_digest`, `environment_descriptor`, `raw_output_sha256`,
`scope`) — plus confirmation that `reports.py::balance_from_spec` is the
right pinned Ledgerkit scenario. Per the governing prompt's own explicit
instruction, Phase 82 implementation has **not** begun and should not
begin without that approval.

Other open items requiring a human/lead decision, none currently claimed
by a drafted plan or phase number:

- Whether to fund any Post-v2 Cross-Project Semantic Overlay stage
  (`planning/post-v2-cross-project-overlay-backlog.md`) — explicitly not
  authorised by any amendment to date; Stage 1 cannot begin before Phase
  82 is `done` regardless.
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
