# Phase 43b: two `check_user_docs.py` rules from GATE DA

**Status:** planned

A small tooling phase (~1 session) decided at **GATE DA** (Phase 43's
retro, `planning/retros/phase-43-dogfood-agent-led-workflow.md`). Runs
before Phase 44 so the standing-content and generated-artifact drift
gaps surfaced during Stage A are closed before Stage B's external work
begins.

## Depends on

- Phase 43 `done` (GATE DA passed).

## Scope

**In scope — `scripts/check_user_docs.py`:**

1. **`check_no_deleted_names_as_live`** (promotes **L-003 + L-004** — the
   "standing-rot blind-spot" cluster). A hand-maintained list of names of
   removed concepts that must not appear in current-truth docs
   (`README.md`, `docs/`, `architecture/`, `ai-docs/`) *as live* —
   initial list: `grounded_description`, `_RAW_TEXT_CHAR_CAP`,
   `Depth.FULL`, `depth = full`, `depth = "full"`, `codecompass promote`
   / `promote <vendor>`. Blocking. The list lives next to the check with
   a comment pointing at the ADR / phase that retired each. This is the
   *standing-content* complement to the diff-scoped per-phase
   `docs-reconstructor` drift audit — the audit catches what a diff
   breaks; this catches what was already broken and no diff touches.
   - Scope note: exclude `architecture/overview.md` §C's 4 known items
     from *blocking* until Phase 61 fixes them? No — the point is to
     force the fix. If the check goes red on §C, that's correct; Phase
     43b either fixes those 4 sentences (small, verified against `src/`)
     or Phase 61's obligation moves earlier. **Decide during
     implementation:** if fixing §C here is clean, do it (and close
     L-004's Phase 61 obligation early); if it needs the broader Phase 61
     context, seed the check's allowlist with those 4 line anchors +
     a `# TODO(phase-61)` and a test that the allowlist is non-empty only
     for known-tracked items.

2. **`check_generated_artifacts_match_source`** (promotes **L-005**).
   The git-tracked generated artifacts match their generator output:
   `.claude/skills/codecompass/SKILL.md` == `skill.render_tool_skill(...)`,
   `.claude/commands/discovery.md` == `commands.render_discovery_command()`.
   (The root `CLAUDE.md` routing-table block and per-vendor
   `codecompass-*` skills are regenerated from graph state that isn't
   reconstructable in a bare check — out of scope; note why.) Blocking.
   Catches the silent drift L-005 exposed (a hand edit, or a `skill.py`
   change without regen).

**In scope — tests:** one per check (positive + negative).

**In scope — docs:** `.claude/skills/docs-sync/SKILL.md` lists the two
new checks; `CHANGELOG.md` `[Unreleased]`.

**Out of scope:**

- Any `src/codecompass/` change (unless fixing §C's 4 sentences turns
  out to belong here — a judgment call above).
- Broadening beyond the two checks GATE DA named.

## Verification

- `python scripts/check_user_docs.py --strict` — passes after the phase
  (either §C is fixed, or the allowlist mechanism is in place with a
  test guarding it).
- Each new check: introduce a violation → flagged → revert.
- `pytest` / `ruff check .` clean.

## Done when

Standard DoD (as amended). Full agent-led loop — but this is a small
tooling phase, so the trivial-ish fast path may apply for the closeout
(lead judgement; if §C fixes land here it's not trivial).
