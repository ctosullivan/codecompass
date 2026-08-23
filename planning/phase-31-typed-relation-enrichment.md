# Phase 31: Typed relation kinds for AI-enriched doc relations

## Status

`done` — depended on Phase 30 (queries the `used_at`/`doc_code_trace`
data this phase's enrichment prompt can optionally cite as grounding
context, per Design decisions below). Not otherwise blocking.

## Context

Phase 22's `relation_enrichment.py` already writes a one- or two-sentence
free-text `ai_summary` describing *how* a mechanically-proven
`doc_relations_edges` row relates (spec doc/vendor doc → vendor or another
doc artifact) — strictly gated on candidates Phase 21/29's mechanical
mention-detection already proved real. This phase does not touch
*detection*: it only makes the *description* of an already-proven relation
more structured, replacing (or accompanying) free text with a label drawn
from a small closed taxonomy.

This preserves the invariant held everywhere else in this project since
9a-9c: AI classifies or describes candidates the mechanical pass already
found; it never gets to propose a new candidate relation. That boundary
is deliberate (`decisions/0031`, Phase 21's mechanical-only detection,
Phase 22's gating on Phase 21's candidates) and this phase does not
reopen it — semantic-similarity/embedding-based candidate *discovery* is
a different, larger decision, explicitly out of scope here (see Scope).

## Scope

**Covers:**
- A closed `relation_label` enum on top of the existing free-text
  `ai_summary`: `documents_configuration_of`, `explains_usage_of`,
  `contrasts_with`, `supersedes`, `other`.
- Prompt change in `relation_enrichment.py` to request structured
  `{relation_label, summary}` JSON instead of prose-only.
- A `relation_label` column on `doc_relation_enrichment`
  (`CHECK` constraint against the enum), schema version bump.
- Any label the model returns that isn't in the enum is stored as
  `other` — never raises, matches this project's established "never
  raises, degrades to a safe default" posture (`_parse_version`,
  `_extract_scalar`).
- `query relations` output shows the label alongside the existing summary.

**Explicitly does not cover:**
- Any change to *which* relations get enriched — still exactly Phase
  21/29's mechanically-proven candidate set, no new selection logic.
- Embedding- or LLM-driven candidate *discovery* for relations that were
  never mechanically detected (e.g. a doc that discusses a vendor
  conceptually without naming it). This is a real, named gap — word-
  boundary mention-matching can't catch it — but closing it means AI
  participating in detection, not just description, which is a boundary
  this project has held everywhere else. If pursued, it gets its own ADR
  arguing the specific gap it closes and the false-positive/cost tradeoff,
  not a quiet extension of this phase.
- Re-enriching already-enriched rows retroactively as part of this phase's
  rollout — see Verification for how existing rows are handled.

## Design decisions

- **Closed enum, `other` fallback, no new detection.** Consistent with
  every other AI-boundary decision in this project.
- **Existing free-text `ai_summary` is kept, not replaced.** The label is
  additive — `relation_label` for filtering/querying, `ai_summary` for the
  human-readable one-liner `query relations` already shows. Dropping the
  prose in favor of the label alone would lose real information (Phase
  28's excerpt-centering fix specifically improved that prose's accuracy;
  no reason to discard it).
- **Optional grounding context from Phase 30.** The enrichment prompt may
  cite `doc_code_trace`'s package-code usage sites (e.g. "this vendor is
  actually called at 3 sites in this project") as additional context for
  the summary/label call, if Phase 30 is done first — but the phase does
  not hard-depend on it; without Phase 30, enrichment runs exactly as it
  does today, just with the label added.
- **Excerpt source stays Phase 28's needle-centering for now.** Phase 32
  (doc chunking) will later swap the excerpt source to the matched
  chunk's own text when available, falling back to Phase 28's approach
  otherwise — the same additive-upgrade-then-fallback shape Phase 28
  itself used against Phase 22. This phase does not need to anticipate
  that; it ships against what exists today.
- **Existing rows are not migrated.** `doc_relation_enrichment` rows
  written before this phase simply have `relation_label = NULL` until
  their next natural re-enrichment cycle (cache invalidation on vendor
  sync or spec-doc change, per the existing two-axis staleness model) —
  no backfill script, consistent with this project's "don't invent a
  migration path a natural refresh cycle already provides" posture.

## Files

- `src/codecompass/relation_enrichment.py` — prompt change; parse
  structured JSON response; validate/fallback the label.
- `src/codecompass/graph.py` — `doc_relation_enrichment` gains
  `relation_label TEXT CHECK (...)`; schema version bump; `query
  relations`'s underlying query includes the new column.
- `src/codecompass/cli.py` — `query relations` output shows the label.
- `decisions/0045-typed-relation-labels-not-new-detection.md` (new,
  numbered after whatever Phase 30 adds) — records the closed-taxonomy
  choice, the `other` fallback, and explicitly reaffirms the
  AI-enrichment-not-detection boundary this phase deliberately does not
  cross.
- `tests/test_relation_enrichment.py` — enum validation, `other`
  fallback on an unrecognized label, and that existing free-text-only
  behavior still round-trips cleanly for the transition period.
- `docs/cli-reference.md` / `architecture/overview.md` — document the new
  field.
- `CHANGELOG.md` — `[Unreleased]` entry, `Added` category.

## Verification

- `pytest` passes, new tests included.
- `ruff check .` clean.
- Live re-enrichment run against this repo's real candidates (`sync
  --yes`, disclosed cost, same gate as always): confirm `relation_label`
  populates within the enum for every newly-enriched row.
- Manually spot-check 2-3 real labels against the actual relationship in
  this repo's own docs — same standard Phase 28 used ("read the real
  surrounding text directly") — not just "tests pass."
- Confirm an intentionally-adversarial/ambiguous case (mock or real) that
  can't cleanly fit the enum falls back to `other` without raising.
- Core-logic diff read directly against this plan before marking `done`.

**Confirmed live** (this phase's actual implementation): cleared and
forced a real re-enrichment run over this repo's 39 real relationships
(~$0.04). Every row got a valid label within the enum, 0 NULL/invalid.
Two spot-checked labels (`decisions/0016-gap-analysis-tests-never-call-
the-live-anthropic-api.md` → `anthropic`, labeled `contrasts_with`;
`decisions/0034-chat-demoted-graph-and-skills-are-primary.md` → the tool
Skill, labeled `supersedes`) were confirmed grounded by reading the real
decision text directly, not just trusting the label.
