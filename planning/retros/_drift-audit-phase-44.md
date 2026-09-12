# Drift audit — Phase 44 (reference-project protocol + context-quality eval spec)

**Auditor:** docs-reconstructor (MODE 1, per-phase, read-only)
**Base:** working tree vs HEAD `bf6db6e` (nothing committed yet)
**Plan:** `planning/phase-44-reference-project-protocol.md`
**Date:** 2026-09-12

## Verdict

**NO DRIFT.**

## What actually changed about the system

Reviewed the actual working-tree diff directly (not any agent's summary of it):

- New `planning/reference-projects/{README,TEMPLATE-registration,
  TEMPLATE-evaluation,_instrument-dry-run}.md` — the reference-project
  registry and evaluation templates, plus a labelled self-test dry-run.
- New `planning/phase-45-ledgerkit-baseline.md`.
- Appended entries to `planning/context-use-log.md` (Phase 44 dry-run
  retrieval) and `planning/learnings/inbox.md` (L-012, a candidate
  learning about `query symbol`'s single-symbol granularity).
- **Side effect, not phase scope:** running `codecompass sync --budget 0`
  on this fresh checkout (no `vendor/`/`context-graph.db` existed, no
  `ANTHROPIC_API_KEY` set) mechanically regenerated two generated-content
  blocks:
  - `CLAUDE.md`'s vendor table (between `<!-- codecompass:... -->`
    markers): anthropic 0.109.1→1.5.0, pipdeptree 4.2.1→4.2.5, rich
    15.0.0→15.0.0, typer 0.27.1→0.27.2; all four `Enriched` flipped
    yes/no→no (three vendors were previously enriched under a different
    environment's committed state; this environment has no API key, so
    Phase A only, no enrichment ran).
  - `.claude/skills/codecompass/SKILL.md`'s vendor table and heading
    (`## Vendors (4 tracked, 3 enriched)` → `(4 tracked, 0 enriched)`),
    same version bumps, same enriched-flag flips.

**No `src/codecompass/` change, no test change, no CLI/flag/config-schema/
generated-file-format/data-model/default/user-facing-error-message
change.** `git diff --stat` confirms no path under `src/` or `tests/`.

## Verification performed (not trusting the diff's own narrative)

- **Real `.venv` install cross-check** (the standard this audit was told
  to hold the regenerated tables to — not a prior committed state, which
  was stale for a different environment):
  `.venv/bin/pip show {anthropic,pipdeptree,rich,typer}` →
  `1.5.0`, `4.2.5`, `15.0.0`, `0.27.2` respectively. Matches both
  regenerated tables exactly.
- **No `ANTHROPIC_API_KEY` set** in this environment (`env | grep -i
  ANTHROPIC` empty) → "0 enriched" / all `no` is the correct mechanical
  output of a Phase-A-only `sync --budget 0`, not an error.
- **Internal self-consistency:** SKILL.md's heading count ("4 tracked, 0
  enriched") matches its own table body; CLAUDE.md's table and SKILL.md's
  table agree with each other on all four versions and all four enriched
  flags.
- `python scripts/check_user_docs.py --strict` → `no findings`.

## Current-truth product docs checked (README.md, docs/, architecture/, ai-docs/)

| Check | Result |
|---|---|
| Does any product doc assert this repo's own vendor table contents, specific version pins, or an enrichment count/state ("4 tracked, 3 enriched", etc.)? | No. `grep -rn "enriched"` across `README.md`, `docs/`, `architecture/`, `ai-docs/` returns only generic mechanism descriptions (e.g. "enriched yet, codecompass then discloses...", "AI-enriched `ai_summary`", "unenriched vendor") — none pins a specific count or version for *this* repo's own dependencies. The generated tables that did change (`CLAUDE.md`, `SKILL.md`) are explicitly out of this audit's scope (they are generated content between markers, not narrative product docs) but were spot-checked above for self-consistency and installed-version accuracy anyway per the task brief. |
| Does any product doc name a Stage B reference project (e.g. "Technical Clipper") that Phase 44's own realignment note retargeted to Ledgerkit? | No. `grep -rln "Technical Clipper"` across `README.md`/`docs/`/`architecture/`/`ai-docs/` returns nothing — the retarget lives entirely in `planning/` (the phase plan's own amendment note, `planning/v1-redefinition/realignment-2026-09.md`), which is this phase's own self-synced territory, not product-doc scope. |
| Does `README.md`'s "reference-project work" mention (line 16) name a specific project, phase count, or protocol detail this diff could falsify? | No — it's a one-clause pointer to `planning/v1-redefinition/`, unaffected by which project is registered or what templates exist under it. |
| `docs/cli-reference.md`'s `--budget` description (lines 12-122) vs. observed `sync --budget 0` behaviour | Matches: "`--budget <amount>` caps estimated AI spend... If the estimate exceeds `--budget`... [enrichment skipped, rest unaffected]" — consistent with what was actually run (Phase A completed, zero enrichment, no error). |
| `ai-docs/README.md`'s example Q&A rows referencing `anthropic`/`typer` (lines 72-73) | Generic usage examples ("What does this project use `anthropic` for?" → run this command), not assertions about this repo's *current* enrichment state. Still accurate as instructions. |
| Reverse check — did the change make an existing product-doc sentence false without anyone touching that doc? | None found. No product doc described a vendor count, version, or enrichment status specific to this repo's present state, so the regenerated tables (a real, correct state change) had nothing to falsify. |

## Scope note

- Deliberately did not audit `planning/**` (including the four new
  `planning/reference-projects/*.md` files, `planning/phase-45-*.md`,
  `context-use-log.md`, `learnings/inbox.md` themselves) for internal
  correctness beyond checking whether they claim anything about
  README/docs/architecture/ai-docs (they don't) — that content is this
  phase's own self-synced deliverable and `planning/`'s internal
  consistency (template completeness, dry-run report quality) is the
  release-phase-auditor's / lead's job, not this drift audit's.
- Did check `CLAUDE.md` and `.claude/skills/codecompass/SKILL.md` even
  though they're generated content, not narrative docs, because the task
  brief specifically asked for an internal-consistency + real-install
  cross-check on them; found them consistent.
- Did not read any other agent's account of what it changed; formed the
  view above directly from `git diff`, `.venv/bin/pip show`, `env`, and
  `scripts/check_user_docs.py --strict`.
