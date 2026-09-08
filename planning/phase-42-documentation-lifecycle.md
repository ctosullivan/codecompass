# Phase 42: Documentation lifecycle (incremental + closeout gate)

**Status:** planned

Stage A. Operationalises the *everyday* half of the documentation
lifecycle and defines the *milestone* closeout gate. Blank-slate
reconstruction itself is Phase 60. Design:
`planning/v1-redefinition/documentation-lifecycle.md`.

## Depends on

- Phase 40 done (`docs-maintainer` agent exists).
- **G4 (§5 DoD parts)** — if draft A2 (the three DoD additions) didn't
  land in Phase 40, land it here (present the exact diff, `CLAUDE.md`
  §0).

## Scope

**In scope:**

- `docs-maintainer` agent brief finalised: the current-truth principle;
  "fix the wrong paragraph, don't append a caveat"; the boundary (no
  ADRs, no `CLAUDE.md`, no blank-slate work); which files it may write
  (`docs/`, `architecture/`, `README.md`, `ai-docs/`, `CONTRIBUTING.md`).
- `scripts/check_user_docs.py` extended with deterministic doc checks
  (`documentation-lifecycle.md` §2 step 3):
  - every internal Markdown link in `README.md` / `docs/` / `ai-docs/` /
    `architecture/` / `CONTRIBUTING.md` resolves to an existing file
    (and anchor, where feasible);
  - fenced code blocks tagged as shell/`bash` that invoke `codecompass`
    use a real subcommand/flag (cross-check against the Typer app's
    registered commands);
  - every ADR in `decisions/` has a `Status:` line; every ADR that says
    "supersedes"/"superseded by" names a real sibling file.
  New tests for each.
- `planning/milestone-closeout-checklist.md` — new: the 10-step
  documentation-completion gate (`documentation-lifecycle.md` §5),
  written as an actionable checklist a future Phase 66 session executes.
- Apply the approved `CLAUDE.md` §5 diff (A2) if not already applied;
  mirror into `CONTRIBUTING.md`.
- Run the new checks against the current repo and **fix whatever they
  legitimately flag** (expect some stale links / examples given
  `architecture/overview.md`'s size) — `docs-maintainer` does this,
  and it's the phase's own first real use of the agent.
- ADR: none expected; write one only if a check's scope decision is a
  real tradeoff (e.g. anchor-checking false positives).

**Explicitly deferred / out of scope:**

- Blank-slate reconstruction — Phase 60.
- The `architecture/overview.md` split — Phase 61 (this phase may *flag*
  candidate sections but does not restructure it).
- Any `src/codecompass/` change.

## Design decisions

- **Deterministic checks only** — no AI in `check_user_docs.py`, same as
  every existing rule (Phase 36). Link/example/ADR-status checks are all
  mechanical.
- **The closeout checklist is a file, not code** — it involves judgement
  (reconciliation decisions) that shouldn't be mechanised.
- **Fix-what-it-flags is in scope** — shipping the checker without
  cleaning the current violations would leave `--strict` red.

## Files

- `.claude/agents/docs-maintainer.md` — brief finalised
- `scripts/check_user_docs.py` — link / example / ADR-status checks
- `tests/test_check_user_docs.py` — new tests
- `planning/milestone-closeout-checklist.md` — new
- `CLAUDE.md` — §5 (gate G4, §0 approval) if not already done
- `CONTRIBUTING.md` — mirror
- `docs/`, `architecture/`, `README.md`, `ai-docs/` — fixes for whatever
  the new checks flag
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` — curator

## Verification

- `python scripts/check_user_docs.py --strict` passes on the current
  repo *after* fixes.
- Introduce a broken internal link → `--strict` fails naming it → revert
  → passes. (Test + one live demonstration.)
- Introduce a fenced `codecompass frobnicate` example → flagged → revert.
- `planning/milestone-closeout-checklist.md` reviewed by
  `release-phase-auditor` as executable-as-written.
- `pytest` / `ruff check .` clean.

## Done when

Standard DoD (incl. amended §5) + verification + `release-phase-auditor`
PASS + candidate learnings triaged.
