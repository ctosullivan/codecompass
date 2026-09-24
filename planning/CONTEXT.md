# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` (every phase,
categorized) and `planning/retros/` (every phase's own full retro:
goal, delivered vs planned, lessons learnt, process feedback) for the
log of how it got here. Per `CLAUDE.md` §4, this file exists for
session-resumption, not as a project history — do not re-narrate a
`done` phase's own closeout here once its retro exists; point at the
retro instead.

**Rewritten in full at Phase 66** (2026-09-24), replacing an
append-only history that had grown to ~2450 lines, contradicting this
file's own governing rule above (flagged by Phase 65's own
`release-phase-auditor` audit, `planning/retros/_audit-phase-65.md`).
Nothing was lost in the rewrite — a dedicated cross-check (a `fork`
dispatch, Phase 66) read the full prior file against every retro,
ADR, and `CHANGELOG.md` entry it narrated and confirmed every
substantive fact is preserved durably elsewhere; the prior file's own
full text remains in git history at any commit before this one.

## Current phase

**"CodeCompass v1" is a redefined product-validation milestone**
(`decisions/0048`), not the `pyproject.toml` version string: CodeCompass
developed agent-led, validated against real external reference-project
work, improved from that evidence, generalised only as far as evidence
justifies, then released after blank-slate doc reconstruction and an
independent audit. Full roadmap: `planning/ROADMAP.md` (phase-by-phase
status table) and `planning/v1-redefinition/roadmap.md` (per-stage
detail).

- **Foundation (Phases 0–38)**: done. The npm/PyPI/Cargo
  package-source-grounding tool — auto-clones tracked vendors, detects
  real project-source usage, maps docs/skills/dependencies into a
  SQLite context graph with AI-enriched relationships, exposes it via
  `codecompass query`/`/discovery`/generated Skills. Current-state
  description: `architecture/module-map.md` and `docs/quickstart.md`
  (Phase 64/65's own reconstructed documentation), not this file.
- **Stages A–F (Phases 39–63)**: done. Agent-led development model
  operational (`.claude/agents/`, `planning/agent-led-workflow.md`);
  GPL-3.0-or-later relicensing; Ledgerkit + Technical-Clipper reference
  evaluation cycles; the evidence-backed Scope→Plan→Domain→Design→Implement
  methodology formalized (`decisions/0060`); a real external Haskell
  adapter (two separate repositories) as the reference implementation
  of a genuinely external adapter.
- **Phase 63D (Domain reconstruction)**: done. `docs/domain/` — the
  approved, evidence-backed corpus for what CodeCompass's own concepts
  mean — is now the durable input every later phase consumes rather
  than re-derives.
- **Stage G (Phases 64–70), in progress**: 64 (blank-slate doc
  reconstruction), 65 (architecture + ADR reconciliation), 66 (roadmap
  + context reconciliation), and 67 (final validation — fresh-agent
  acceptance test scored 4/4 PASS) done. 68 (independent release audit)
  through 70 (release) not yet started.
- **GATE DD (Phase 55) remains open, intentionally** — Stage E
  (Phases 56–59, the "minimum justified generalisation") is
  `CONDITIONAL` on it and may never fund; this is the roadmap's own
  already-settled design ("if Stage D/E were skipped per GATE DD,
  Stage G runs against the Stage C product instead," `v1-redefinition/roadmap.md`),
  not an oversight. Every Stage F/G phase since Phase 60 independently
  confirms it does not resolve or require GATE DD.
- **Phases 24/25 (project-root REPL routing; MCP server) remain
  deferred** past v1 (`decisions/0048`) — revisit triggers: 24 if
  reference-project evidence shows recurring need, 25 post-v1 informed
  by real CLI/Skill usage. **Phases 48/50 (task-oriented context
  retrieval; shared-agent context) are not funded** (GATE DB, Phase
  47 — insufficient evidence) — revisit if new evidence emerges.

## What was just completed

**Phase 67 — final validation — done (2026-09-24).** Fixed this
checkout's own stale `context-graph.db` (21 phases untouched);
re-confirmed Ledgerkit's fix live on a newer pin; fresh-agent
acceptance test scored 4/4 PASS. Three learnings promoted
(`L-040`/`L-041`/`L-042`). Full detail:
`planning/retros/phase-67-final-validation.md`.

## Known standing gaps (carried forward — not phase history, still true)

- Cargo adapter (`decisions/0014`) has never been validated against
  real `cargo metadata` output or a real crate — no Rust toolchain has
  been available in this environment yet.
- `extract_npm_symbols` is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `chat.py` has never been run against the real Anthropic API in this
  environment.
- `staleness.py`'s version parser has no real PEP 440/semver
  correctness — string comparison only.
- A formal trigger-accuracy evaluation harness for per-vendor Skills
  (`decisions/0013`) remains outstanding.
- Cursor `.mdc` export has no `globs` field — documented future
  refinement, not implemented.
- `doc_chunks`' per-chunk `content_hash` (Phase 32) is computed and
  available but not yet consumed for cache-invalidation grain
  (`decisions/0046`) — `select_candidates` still hashes a relation's
  full source-doc text.
- The fenced-code-block fix (Phase 34) tracks only ` ``` `/`~~~`
  fences, not indented (4-space) blocks — not a practical gap, since
  the heading regex requires `#` at column 0.
- `vendor/` exists in this checkout with real, enriched content — a
  live artifact of past validation runs, gitignored, freely
  regeneratable (`decisions/0010`).
- A local `.venv/` exists at the project root (gitignored) with
  `codecompass` installed editable, for local testing.

## Next concrete step

**Dispatch `release-phase-auditor` for Phase 67's final independent
DoD audit** (drift audit and learning triage already complete). Once
that returns PASS or PASS WITH NON-BLOCKING OBSERVATIONS, proceed into
**Phase 68 (independent release audit)**: `release-phase-auditor`,
read-only, a full Definition-of-Done audit across every Stage A–G
phase's own exit criteria plus the milestone-closeout checklist — a
`FAIL` prevents Phases 69/70. Its own plan does not yet exist and must
be written per `CLAUDE.md` §1 before implementation begins. GATE DD
remains open and unaffected (a separate axis from Stage F/63D/G, per
`decisions/0056`/`decisions/0060`).
