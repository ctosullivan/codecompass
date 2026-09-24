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

**CodeCompass v1.0.0 is released.** The redefined-v1 milestone group
(`decisions/0048`, Phases 39–70) is complete: published to PyPI as the
`codecompass-context` distribution (CLI command and Python import
package both stay `codecompass`), tagged `v1.0.0`. Full roadmap:
`planning/ROADMAP.md`. Closeout record: `planning/v1-closeout.md`
(architecture summary, what shipped, what was deferred with revisit
triggers, key ADRs, reference-project evaluation results, distilled
process lessons).

- **Foundation (Phases 0–38) + Stages A–G (Phases 39–70)**: all done.
  Current-state description of what CodeCompass does:
  `architecture/module-map.md` and `docs/quickstart.md`, not this file.
- **GATE DD (Phase 55) remains open, intentionally, post-v1** — Stage
  E (Phases 56–59) is `CONDITIONAL` on it and may never fund; this is
  the roadmap's own already-settled design, not an oversight.
- **Phases 24/25/48/50 remain deferred/not-funded, post-v1** — revisit
  triggers stated in `planning/ROADMAP.md`'s own rows.
- **The documentation freeze (declared at Phase 69) is lifted** — the
  `v1.0.0` tag it was conditioned on now exists.

## What was just completed

**Phase 70 — release redefined CodeCompass v1 — done (2026-09-24).**
Published `codecompass-context` 1.0.0 to PyPI (confirmed live via the
real PyPI JSON API); `v1.0.0` tagged and pushed; `CHANGELOG.md`
flattened to a dated `[1.0.0]` release section. One drift-audit fix
cycle: `README.md`'s own release-status claims were mistakenly left
out of the phase's initial scope, found and fixed. One learning
promoted (`L-046`). Full detail:
`planning/retros/phase-70-release-v1.md`.

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

**Phase 71 (post-v1 documentation refresh), direct user request
2026-09-24**: a ground-up rewrite of current-facing documentation
against the now-final, shipped v1 state — `README.md`, a simplified
`planning/ROADMAP.md`, this file reduced further, and a consistency
sweep of other current-facing docs/indexes/examples. Historical
material (retros, ADRs, evaluation evidence) stays as a historical
record, not rewritten. Its own plan does not yet exist and must be
written per `CLAUDE.md` §1 before implementation begins. This is the
first phase of CodeCompass's ordinary post-v1 development — no longer
part of the redefined-v1 milestone group, which is closed.
