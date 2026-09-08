# Phase 41: Project-learning lifecycle (operational)

**Status:** planned

Stage A. Makes `planning/learnings/` operational and wires the
`knowledge-curator` to it. Design:
`planning/v1-redefinition/learning-lifecycle.md`.

## Depends on

- Phase 40 done (`knowledge-curator` agent exists).
- **G4 (§8 learning parts)** — the §8 paragraph on learnings being
  non-authoritative until promoted (draft A3) should already be in
  `CLAUDE.md` from Phase 40; confirm.

## Scope

**In scope:**

- Finalise the `planning/learnings/` scaffold (already created by the
  `v1-redefinition` package): confirm `README.md`, `inbox.md`,
  `TEMPLATE.md`, `promoted.md` match the design; add `candidates/` with a
  `.gitkeep` and a note on when to split out of `inbox.md`.
- `knowledge-curator` agent brief finalised against the real files:
  the accept step, the classification → destination table
  (`learning-lifecycle.md` §4), the promotion-recommendation-not-final-
  artifact rule, the merge/discard policy, the "evidence-gathering >3
  phases → decide" hygiene rule.
- `scripts/check_user_docs.py` extended with the learnings-hygiene checks
  (`learning-lifecycle.md` §6): every candidate has required fields;
  every `status: promoted` candidate has a `promoted.md` line; flag
  candidates stale in `evidence-gathering`. Report-only by default;
  `--strict` includes them in the exit gate. New tests for each check.
- `docs-sync` skill (`.claude/skills/docs-sync/SKILL.md`) updated to
  mention the new checks.
- ADR `0050` (learning lifecycle) **only if** a non-obvious tradeoff
  surfaces (`proposed-governance-changes.md` §B draft `0050`) — the
  "no giant learnings doc, promote into the owning artifact" choice vs. a
  durable curated KB is the likely candidate. Decide during
  implementation.

**Explicitly deferred / out of scope:**

- CodeCompass indexing `planning/learnings/` as a graph artifact —
  Stage C/E candidate (`learning-lifecycle.md` §7), not here.
- Any `src/codecompass/` change (`check_user_docs.py` is
  maintainer-only tooling outside `src/`, per Phase 36 precedent).

## Design decisions

- **`inbox.md` is transient, `promoted.md` is the only long-lived file**
  and holds pointers only. Enforced by the hygiene check, not just prose.
- **The curator recommends; it doesn't write final ADRs/tests.** Keeps
  the lead's judgement in the loop for high-stakes promotions.
- **Hygiene checks are report-only unless `--strict`** — same posture as
  every other `check_user_docs.py` rule (Phase 36).

## Files

- `planning/learnings/candidates/.gitkeep` — new
- `planning/learnings/README.md`, `TEMPLATE.md` — refined if needed
- `.claude/agents/knowledge-curator.md` — brief finalised
- `.claude/skills/docs-sync/SKILL.md` — updated
- `scripts/check_user_docs.py` — new checks
- `tests/test_check_user_docs.py` — new tests
- (maybe) `decisions/0050-project-learning-lifecycle.md`
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` — curator

## Verification

- `python scripts/check_user_docs.py --strict` passes on the current
  repo (empty inbox is valid).
- Add a deliberately malformed candidate → `--strict` fails with a clear
  message → remove it → passes. (Covered by a test, and demonstrated
  live once.)
- **End-to-end:** take one real observation from Phase 39/40 (e.g.
  something learned about the `ROADMAP.md` restructuring, or a rough
  edge in an agent brief), file it as a candidate via `TEMPLATE.md`, have
  `knowledge-curator` triage it to an outcome, and — if promoted —
  confirm `promoted.md` gets its pointer line and the target artifact
  actually changed.
- `pytest` (new tests pass) / `ruff check .` clean.

## Done when

Standard DoD + verification + the end-to-end triage above actually
executed (not just described) + `release-phase-auditor` confirms
(first real use of the auditor).
