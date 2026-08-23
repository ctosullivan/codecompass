# Doc-graph precision roadmap: Phases 30-32

## Purpose

This is an umbrella planning doc, same role as
`planning/v1.0-initial-release-roadmap.md` played for phases 20-23: it
gives a fresh session the full shape and rationale of a related group of
phases before it reads (or finalizes) each phase's own plan file. It is
**not** itself one of the required per-phase plan files — `planning/
phase-30-*.md`, `phase-31-*.md`, and `phase-32-*.md` each still need to
exist and be marked `done` individually, per `CLAUDE.md`/`CONTRIBUTING.md`'s
plan-before-implementing rule.

## The three phases, in one paragraph each

- **Phase 30 — bidirectional traversal.** No new tables, no AI. `uses_edges`
  already stores `(source_file_id, vendor_id, symbol_id, line)`, fully
  indexed, but `vendor_profile`/`symbol_profile` currently collapse it to
  a bare `usage_count`. This phase surfaces the file/line data already
  there, and composes existing edges (`documents_edges` +
  `doc_relations_edges` + `uses_edges`) into a `doc_code_trace` query —
  "this doc/vendor is used at these real locations in the project."

- **Phase 31 — typed relation enrichment.** Extends Phase 22's existing
  free-text `ai_summary` with a closed-taxonomy `relation_label`
  (`documents_configuration_of` / `explains_usage_of` / `contrasts_with`
  / `supersedes` / `other`). Strictly gated on Phase 21/29's already-
  mechanically-proven candidates — no new candidate discovery, same
  boundary the project has held since `decisions/0031`.

- **Phase 32 — heading-based doc chunking.** Splits doc artifacts into
  heading-scoped chunks (deterministic, no NLP) and adds a nullable
  `chunk_id` to `documents_edges`/`doc_relations_edges`. Additive: rows
  without a resolvable chunk behave exactly as they do today. Once landed,
  it gives Phase 30's trace output a `heading` field and gives Phase 31's
  enrichment a precise chunk excerpt in place of Phase 28's needle-
  re-derivation fallback (which remains, as the fallback, not removed).

## Why this order

Ship the two independently-valuable, smaller phases first; let chunking
sharpen both afterward rather than blocking either behind a bigger schema
change up front. This isn't a new pattern for this project — it's the
same shape as two things that already happened:

- Phase 26 added symbol-level usage detection on top of Phase 11's
  coarser vendor-level detection, later, as an add-on — Phase 11 wasn't
  redesigned to anticipate it.
- Phase 28 added needle-centered excerpts on top of Phase 22's enrichment,
  later, as an add-on — Phase 22 wasn't redesigned to anticipate it either.

Phase 32 doing the same thing to both Phase 30 and Phase 31 at once is
consistent with that precedent, not a departure from it. The alternative
— building chunking first so 30/31 never need a follow-up touch — trades
a slightly cleaner history for delaying two independently shippable wins
behind a bigger, riskier schema change. Given this project's own
demonstrated preference for small, separately-verifiable phases over
front-loaded "do it right the first time" designs, order stands as
**30 → 31 → 32**.

Phase 31 does not hard-depend on Phase 30 (see Phase 31's own Context
section) — it can ship in either order relative to 30 if scheduling
demands it. Phase 32 hard-depends on both being done, since it modifies
files both phases touch.

## The boundary all three phases share

None of these three phases let AI participate in *detecting* a new
relation — only in describing (Phase 31) or locating (Phase 32) a
relation the mechanical pass already proved real. This is the same
determinism-first boundary held since 9a-9c, `decisions/0031`, Phase 21's
mechanical-only spec-doc detection, and Phase 22's gating on Phase 21's
candidates. A prior discussion identified the one real gap this boundary
leaves open — a doc that discusses a vendor conceptually without naming
it, which word-boundary matching can never catch — and deliberately
excluded closing that gap from all three of these phases. If it's ever
pursued, it needs its own ADR arguing the specific gap and the
false-positive/cost tradeoff of AI-driven candidate discovery, the same
rigor every other AI-boundary decision in this project has gotten. Do not
fold it into 30, 31, or 32 as a "while we're in here" addition.

## Relationship to v1.0 scope

At explicit user request, this group is added to v1.0's blocking scope
alongside Phase 23 — see `planning/ROADMAP.md`'s "v1.0 scope note" and
`planning/CONTEXT.md`. Phase 23 Part B (the actual PyPI publish, already
paused pending explicit confirmation) now also waits on Phases 30-32
reaching `done`, the same "don't re-release almost immediately after"
reasoning `planning/v1.0-initial-release-roadmap.md` used to order Phases
20-22 ahead of 23 originally. This does not change Phases 24/25's
deferred-past-v1.0 placement, which remains an open, separately-flagged
question in that document.

## What this session did

1. Read all three attached phase files in full.
2. Finalized each one's Scope/Files/Verification as real, committed plan
   files at `planning/phase-30-bidirectional-code-traversal.md`,
   `planning/phase-31-typed-relation-enrichment.md`, and
   `planning/phase-32-doc-chunking.md` — added each to `planning/
   ROADMAP.md` in the same commit, per the standing process.
3. Expanded v1.0's blocking scope to include these three phases, per
   explicit user instruction.

Implementation (in order: 30, then 31, then 32 — each with its own
changelog entry, its own `pytest`/`ruff` pass, and its own live dogfood
verification against this repo's real graph before being marked `done`)
has not started as of this planning pass.
