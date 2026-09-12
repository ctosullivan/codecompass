# Phase 43e: Reusable agent-led adoption blueprint

**Status:** planned (content drafted 2026-09-12; formal phase closeout pending)

A Stage-A bridge phase from the 2026-09-12 realignment
(`planning/v1-redefinition/realignment-2026-09.md`). Writes the reusable
agent-led development blueprint CodeCompass hands to Ledgerkit (and
later adopting projects) — extracted and generalised from CodeCompass's
own working practice, not designed fresh.

## Depends on

- Stage A complete (Phases 39–43c, `done`) — the blueprint generalises
  from real practice, not from a hypothesis.

## Scope

**In scope:**

- `planning/v1-redefinition/adoption-blueprint.md` — recommended agent
  roles (mapped from CodeCompass's own 8-agent roster, with an explicit
  minimum-viable 5-role starting point for a Ledgerkit-sized project),
  responsibility/permission/independence boundaries, project entry-point
  strategy, CodeCompass-discovery + context-evaluation usage, the
  knowledge-curation workflow (generic shape, project-specific
  destinations), documentation lifecycle, independent completion
  gating, and feedback reporting to CodeCompass. Each recommendation
  tagged `[GENERIC]` / `[PROJECT-SPECIFIC]` / `[OPTIONAL]` /
  `[CODECOMPASS-GENERATED]` / `[MANUALLY-GOVERNED]`.
- This plan file + `planning/ROADMAP.md` row + `CHANGELOG.md` entry.

**Explicitly out of scope:**

- Any change to `.claude/agents/*.md`, `agent-led-development.md`, or
  `agent-led-workflow.md` — the blueprint *references* these, it does
  not modify CodeCompass's own roster or workflow.
- Standing up anything in the Ledgerkit repository itself — this phase
  produces the document CodeCompass hands over; applying it is
  Ledgerkit's own decision, at Stage B (Phase 45+).
- A large autonomous-development framework — explicitly scoped against
  in `adoption-blueprint.md` §0/§9.

## Verification

- `python scripts/check_user_docs.py --strict` clean.
- `adoption-blueprint.md` committed, cross-referenced from `README.md`'s
  documents table and `realignment-2026-09.md` §6.1.
- No `src/codecompass/` change, no test change (a `planning/` artifact
  only).

## Done when

Standard DoD (as amended) — plan committed; no governance-file change
(no `CLAUDE.md`/`decisions/*` edit, so no §0 gate); low-risk content, but
held alongside the rest of this realignment package until the user
reviews it (gate G13 — the blueprint becomes a cross-project contract
once Ledgerkit applies it, so it gets an explicit nod even without a
governance-file change). Full agent-led closeout (retro,
`docs-reconstructor` drift audit, `knowledge-curator` triage,
`release-phase-auditor` pass) applies once execution is approved.
