# Phase 39: Reconcile repo state + versioning realignment

**Status:** planned

Part of the redefined-v1 effort (`planning/v1-redefinition/`), Stage A.
This phase changes **no `src/` code** and **publishes nothing** (gate
G2-b) — it ratifies the redefinition, realigns the version string and
roadmap, and lands the two foundational ADRs.

## Depends on (human-decision gates — `planning/v1-redefinition/README.md` §7)

- **G1** — ✅ decided 2026-09-09: `pyproject.toml` `1.0.0` → `1.0.0.dev0`.
- **G2** — ✅ decided 2026-09-09 → **G2-b**: hold all publishing until
  redefined v1 (Phase 67). No build, no `twine`, no tag, no dated
  CHANGELOG section in this phase.
- **G3** — approve the `ROADMAP.md` restructuring shape (still open).
- **G5** — approve ADR drafts `0048` and `0049`
  (`planning/v1-redefinition/proposed-governance-changes.md` §B) (still
  open).

If G3 or G5 is unresolved, stop and ask — do not proceed on assumption.

## Scope

**In scope:**

- Ratify the `planning/v1-redefinition/` package (it becomes the
  governing plan for the redefined-v1 milestone).
- `pyproject.toml`: `version = "1.0.0"` → `"1.0.0.dev0"`. Keep
  `Development Status :: 4 - Beta`.
- `ROADMAP.md`: append a new milestone-group table "Redefined
  CodeCompass v1 — Stages A–F (phases 39–67)" summarising
  `planning/v1-redefinition/roadmap.md`; add rows for phases 39–44 with
  plan-file links and status; retitle each existing "**v1.0 scope
  note**" block to "**Foundation-release scope note**" (wording change
  only — no content removed); add a one-paragraph "Redefinition note"
  explaining the split between the internal v1 milestone and the wheel
  version, pointing at `planning/v1-redefinition/README.md` §2.
- Existing Phases 24/25: change their status note to "**deferred** —
  revisit as redefined-v1 Stage C candidate (24) / post-redefined-v1
  (25); see `planning/v1-redefinition/roadmap.md`". **No renumbering.**
- Phase 23 row: "Part A done; Part B **superseded** — first publish is
  redefined v1 (Phase 67), per gate G2-b".
- `README.md`, `docs/cli-reference.md` header, `ai-docs/README.md`,
  `ai-docs/CLAUDE.md`: replace the "v1.0.0 in progress, phases 0-38"
  framing with "phases 0–38 (the foundation) done; CodeCompass v1
  redefined as a product-validation milestone, in progress — see
  `planning/v1-redefinition/`; **not yet released**" (`migration.md` §1
  step 2). `docs-maintainer` does this pass.
- `decisions/0048` (redefined-v1 milestone) and `decisions/0049`
  (agent-led development model): move the approved drafts from
  `proposed-governance-changes.md` §B into `decisions/`, `Status:
  Accepted`.
- `CHANGELOG.md`: `[Unreleased]` entry for this phase (planning/version
  realignment). `[Unreleased]` stays **undated** (G2-b — nothing is
  released).
- `planning/CONTEXT.md`: overwrite current-state section.

**Explicitly deferred / out of scope:**

- Any `CLAUDE.md` edit — the §8 / §5 / §1 changes are gate G4, landed in
  Phases 40–42, not here (`proposed-governance-changes.md` §A). `0048`'s
  §6 milestone note (A4) is also a G4 item.
- Creating `.claude/agents/` — Phase 40.
- The `planning/learnings/` scaffold already exists (created with this
  package); making it *operational* is Phase 41.
- Any `src/codecompass/` change.

## Design decisions

- **`1.0.0.dev0`, not `0.4.0`:** gate G2-b holds all publishing until
  Phase 67, so no `0.4.0` will ever be released — labelling the in-repo
  version `0.4.0` would invent a phantom release. `1.0.0.dev0` says
  accurately "in development toward the 1.0.0 Phase 67 ships", and
  matches the project's prior practice (`version = "0.1.0.dev0"` before
  Phase 23, `decisions/0047`). Phase 67 drops `.dev0`.
- **Historical roadmap tables are not rewritten** — the MVP (v0.1),
  MVP (v0.2), and Post-MVP tables stay verbatim; only the "v1.0 scope
  note" prose blocks are retitled and a new group table is appended.
  Preserves the renumbering-note audit trail the project relies on.
- **Phase 23 disposition:** Part A stays `done`. Part B is superseded —
  the first publish is redefined v1 (Phase 67).
- **No release in this phase** (G2-b) — no `python -m build`, no
  `twine`, no `git tag`, no dated `CHANGELOG.md` section.

## Files

- `pyproject.toml` — version bump to `1.0.0.dev0`.
- `planning/ROADMAP.md` — new group table, retitled notes, 24/25 status,
  Phase 23 disposition, rows 39–44.
- `README.md`, `docs/cli-reference.md`, `ai-docs/README.md`,
  `ai-docs/CLAUDE.md` — framing pass (`docs-maintainer`).
- `decisions/0048-redefined-v1-milestone.md` — new (from draft).
- `decisions/0049-agent-led-development-model.md` — new (from draft).
- `CHANGELOG.md` — `[Unreleased]` entry (undated).
- `planning/CONTEXT.md` — current-state overwrite.

## Verification

- `pytest` and `ruff check .` still clean (no code changed — confirms
  nothing broke).
- `python scripts/check_user_docs.py --strict` passes (README
  phase/version claims now consistent).
- `pyproject.toml` reads `version = "1.0.0.dev0"`.
- `ROADMAP.md` renders: the new group table is present; no phase 0–38 or
  24–25 number changed; every "v1.0 scope note" now reads "Foundation-release
  scope note"; Phase 23 row updated.
- `decisions/0048` and `0049` exist with `Status: Accepted` and match the
  approved drafts.
- `git tag -l` unchanged (still empty); `CHANGELOG.md` has no dated
  section.
- `planning/CONTEXT.md` reflects: Phase 39 done, Stage A in progress,
  next step = Phase 40.

## Done when

All six standard DoD conditions (`CLAUDE.md` §5) + the phase verification
above. No independent-auditor requirement yet (the auditor agent doesn't
exist until Phase 40); the lead confirms directly.
