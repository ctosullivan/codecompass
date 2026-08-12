# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 9a: Context graph — vendor presence detection — planned, not yet
implemented.** All eight MVP phases (0-8) remain `done` (`decisions/0022`);
this session is post-MVP planning only. Phase 9 was renumbered this
session: the context graph (9a-9e) is now Phase 9, and the previously-
unplanned routing/rollup work (formerly Phase 9) shifted to Phase 10 —
see `planning/ROADMAP.md`'s renumbering notes.

## What was just completed

Planned Phase 9's context graph in full (9a-9d implementation-ready,
9e identified but deliberately not planned yet) — no implementation code
was written this session, per `CLAUDE.md` §1. Wrote four plan files:
`planning/phase-9a-vendor-presence-graph.md` (vendor-level `uses` edges +
dead-dependency detection via `check`), `planning/
phase-9b-symbol-usage-graph.md` (upgrades `uses` to symbol-level, reusing
existing per-ecosystem symbol extraction rather than re-deriving it),
`planning/phase-9c-doc-skill-mapping.md` (`DocArtifact` nodes,
`documents`/`routes_via`/`depends_on` edges, coverage-gap reporting), and
`planning/phase-9d-llm-enrichment.md` (optional, off-by-default LLM
layer: usage-purpose labels, clustering, `EXPLAINS` chunk retrieval,
trigger-accuracy proxy). Wrote five new ADRs, `decisions/0024`-`0028`:
storage model (single root-level `context-graph.json`, not per-vendor),
cache-invalidation trigger (rebuilds only on bare `sync`/bootstrap, never
incrementally), 9d's optional/deterministic-gated posture (and its
trigger-accuracy proxy explicitly *not* closing `decisions/0013`'s
outstanding harness item), `EXPLAINS`-vs-`decisions/0023` reconciliation
(coexistence, `chat.py` untouched), and usage-cluster classification's
draft-only/never-auto-written posture (deferred to a future Phase 9e).
Renumbered `planning/ROADMAP.md`'s Post-MVP table: former Phase 9
(routing/rollup) → 10, former 10/11 (polish, MCP) → 11/12; all were
`not started`, so this is a clean renumber, not a rewrite of in-flight
work.

Two discrepancies between the brainstorm input this planning session
started from and the real repo state were caught and corrected rather
than silently reconciled: the brainstorm misattributed ADR 0008 as the
Agent-Skills-context-selection decision (it's actually `decisions/0013`;
0008 is the adapter-ecosystem-coverage ADR), and it assumed a top-level
`skills/` directory exists for draft Skill suggestions, which it does
not — Skills live only at `.claude/skills/<name>/`.

## Decisions made this session not already captured in an ADR

- None — every real design decision from this session (storage model,
  cache-invalidation trigger, 9d's posture, `EXPLAINS` reconciliation,
  usage-cluster classification's deferral) is captured in `decisions/
  0024`-`0028`. The Phase 9/10/11/12 renumbering itself was handled as a
  `planning/ROADMAP.md`-note-level change, not a new ADR, matching the
  precedent set by the prior Phase 7-era renumbering (recorded only in
  ROADMAP's note, not a dedicated ADR).

## Next concrete step

Implement `planning/phase-9a-vendor-presence-graph.md` first — it
establishes the shared `context_graph.py`/`usage.py` model that 9b, 9c,
and 9d each extend in place rather than duplicate. 9b/9c/9d should be
implemented in that order (each plan file's Scope section states what it
extends from the previous one). Phase 9e (usage-cluster classification)
is intentionally not planned yet — `decisions/0028` requires 9d to ship
and produce real field data before its ratio-gate threshold and
confidence calibration can be meaningfully chosen.

**Still outstanding, not a blocker but worth remembering**:
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter's fixture
  assumptions (including `repository_url()`) and regex-based `pub`
  extraction against real `cargo metadata` output and a real crate —
  currently entirely unverified, and `promote`'s end-to-end flow against
  a real Cargo vendor is likewise untested.
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `depcompass.grounded_description` (Phase 7) and `depcompass.chat`
  (Phase 8) have never been run against the real Anthropic API in this
  environment — a human must do this manually at least once before
  trusting output quality (`decisions/0016`).
- `staleness.py`'s custom version parser (Phase 6) has no real PEP 440 or
  full-semver correctness — flag if it misclassifies a real-world version
  string once used against real projects.
- A formal trigger-accuracy evaluation harness for per-vendor Skills
  (`decisions/0013`'s Consequences) remains outstanding — Phase 9d's
  trigger-accuracy proxy (`decisions/0026`) is an explicit interim
  stopgap, not a resolution of this item; do not treat it as closed.
- Cursor `.mdc` export has no `globs` field (description-based relevance
  only) — glob scoping to wherever a vendor is actually imported in the
  consuming codebase is a documented future refinement, not implemented.
- `chat` has no conversation-length capping, no streaming, and no
  cumulative-cost display — all explicitly deferred in
  `planning/phase-8-chat-repl.md`, revisit if real usage shows a need.
- Whether/when to cut the `v0.1` tag and promote `CHANGELOG.md`'s
  `[Unreleased]` section to a dated release (`CLAUDE.md` §6) is still a
  separate, not-yet-made decision — unaffected by this session's
  post-MVP planning work.
