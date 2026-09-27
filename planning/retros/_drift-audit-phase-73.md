# Drift audit — Phase 73 (`mentions_artifact` filename-based matching, closes `CG-006`)

**Mode:** 1 (per-phase docs-drift audit).
**Range audited:** `6861250` (plan) .. `07c8475` (CG-006 status flip) —
i.e. `6861250`, `0f3337d`, `29ced55`, `07c8475`.
**Verdict: DRIFT — 1 finding** (non-blocking).

Formed independently: I read the four commits' diffs directly
(`git show`) and re-derived the current behaviour of
`doc_mapping.build_doc_relations_edges` and
`relation_enrichment._relation_needles`/`_select_source_excerpt` from
the code itself before checking any doc, and before reading
`docs-maintainer`'s own reconciliation report.

## What actually changed (observable-behaviour summary)

1. `doc_mapping.build_doc_relations_edges` (`0f3337d`): a `mentions_artifact`
   target that isn't matched by its `.name` is now also tried against its
   filename and filename-stem (each gated by `_is_specific_enough`,
   reused from `spec_docs`). Net effect: `codecompass query relations`
   can now surface `mentions_artifact` edges for doc-to-doc citations by
   filename, which previously produced zero edges.
2. `relation_enrichment._relation_needle` → `_relation_needles` (`29ced55`,
   a follow-on fix to the same phase): the excerpt-centering
   re-derivation used during AI enrichment of a `doc_relations_edges` row
   now tries the same three candidate strings in the same priority order
   (name, then filename, then stem) rather than only the target's `name`
   field, for the no-chunk fallback path. Net effect: a headerless source
   doc that cites a target only by filename no longer silently
   degrades to the first-4,000-characters excerpt during enrichment.
3. `CG-006` flipped to `promoted-to-roadmap` in
   `planning/context-gaps/inbox.md` / `planning/learnings/promoted.md`
   (`07c8475`) — not a current-truth doc in this audit's scope
   (`README.md`, `docs/`, `architecture/`, `ai-docs/`), not checked
   further here.

No CLI flag, config schema, or generated-file format changed. No new
relation kind, no new table, no new eligibility rule for which artifacts
can be match targets (unnamed artifacts are still excluded, unchanged).

## Docs checked (grep for `mentions_artifact`, `build_doc_relations_edges`,
`_relation_needle`, `word-boundary`, `doc_relations_edges`)

- `README.md` — no hits.
- `ai-docs/README.md:50` — generic statement ("which relationships exist
  is decided entirely by deterministic word-boundary matching, never by
  a model") — still true, doesn't claim a specific matching strategy.
  **No drift.**
- `docs/domain/concepts/relationship-edge.md` — describes the six edge
  tables, `mentions_artifact`'s CHECK constraint, and gives
  `architecture/overview.md` mentioning `codecompass.skill.py` as its
  worked example. Doesn't describe *how* the match string is chosen
  (name vs. filename vs. stem) at all, so widening the match strategy
  doesn't falsify anything here. **No drift**, confirms
  `docs-maintainer`'s finding.
- `architecture/context-graph-schema.md:61-75` — describes the
  `relation_kind` CHECK, the two self-mention exclusions, and uses "a
  doc's own first-heading title, once used as its `name`, is trivially
  present in that same doc's own text" as the *illustrative reason* the
  self-mention exclusion exists. This is exemplary framing, not a claim
  that title/`name` is the only string ever matched — and the exclusion
  itself is applied via `artifact.path == row.path` before any string
  comparison runs, so it correctly excludes filename/stem self-matches
  too, unchanged. **No drift**, confirms `docs-maintainer`'s finding.
- `architecture/overview.md:660-720` (name extraction / specificity
  guard, self-mention exclusions) — describes `name` extraction
  (title-or-stem, gated by `_is_specific_enough`) and the doc/vendor
  relation-source allow-set. Doesn't assert that matching a
  `mentions_artifact` target is restricted to `name` alone. **No
  drift**, confirms `docs-maintainer`'s finding.
- `architecture/sync-and-enrichment-pipeline.md:100-146` — step 4
  ("Mention detection... is word-boundary, not substring") and the
  Phase-B excerpt-centering paragraph ("re-deriving the same
  word-boundary match `doc_mapping.build_doc_relations_edges` found,"
  "falling back to a first-N-characters slice only if **the needle**
  can no longer be found") are both phrased generically enough (singular
  "the needle"/"the match," no claim it's specifically the `name` field)
  to remain true after both `0f3337d` and `29ced55` — the underlying
  mechanism they describe (re-derive whatever string triggered
  detection, center on it, fall back if nothing found) is unchanged in
  shape, only widened in which strings are tried. **No drift.**

## The one finding: `architecture/historical-notes.md:70-93`

This page is explicitly, deliberately historical-narrative-framed (see
its own header, lines 1-11): "here \[phase-chronology framing\] is the
correct format, because the story itself is the point. See
`overview.md` for the current-state description." That caveat covers
most of the page. But its closing sentence of the relationship-enrichment
section is a **present-tense, current-state claim**, not history:

> "The needle-re-derivation-plus-fixed-window logic from step 1 was not
> deleted — **it remains the fallback for any candidate without a
> chunk** (a headerless source doc, or a match spanning more than one
> chunk)." (lines 91-93)

— and step 1, the logic this sentence says still applies, is described
as operating on a single needle: "the target vendor's name for a
`mentions_dependency` relationship, or **the target doc artifact's own
`name` field** for a `mentions_artifact` relationship" (lines 72-74).

After `29ced55`, this is no longer what the fallback does for
`mentions_artifact`: `_relation_needles` (plural, renamed from
`_relation_needle`) now tries the target's `name`, then filename, then
stem, in that order, and `_select_source_excerpt` uses whichever is
found — precisely to fix the case this page's own "step 1" describes as
current ("this is why that fallback still exists in today's code," line
84, itself still true) failing silently for a filename-only citation in
a headerless doc. `overview.md`, the page this document points readers
to for current state, does not describe the needle/excerpt-centering
mechanism at all (`grep` for `needle`/`_select_source_excerpt` there
returns nothing), so `historical-notes.md`'s step-1 description is, in
practice, the only place in `architecture/` that describes this
fallback's exact current behaviour — and it now describes an obsolete,
narrower version of it (name-only, not name-then-filename-then-stem).

- **File/line:** `architecture/historical-notes.md:72-74` (needle
  description) and `:91-93` (the "it remains the fallback" claim that
  makes lines 72-74 a current-state assertion, not pure history).
- **Sentence that's now wrong (as a description of current behaviour):**
  "the target doc artifact's own `name` field for a `mentions_artifact`
  relationship" — omits the filename/stem candidates `29ced55` added.
- **What the code actually does:**
  `relation_enrichment._relation_needles` (`src/codecompass/relation_enrichment.py`)
  returns `[name, filename, stem]` (skipping any that are absent/equal)
  for `mentions_artifact`, and `_select_source_excerpt` tries each in
  order.
- **Blocking or non-blocking:** **non-blocking**. This is an internal
  architecture doc (not `README.md`/`docs/` user-facing surface); the
  misdescription understates the fallback's robustness rather than
  overstating it (a reader would wrongly believe the CG-006-adjacent
  gap in enrichment excerpts is still only partially fixed, not that
  something works that doesn't) — no user-facing false statement
  results. Still a genuine current-truth doc sentence made false by this
  phase's own diff, so recorded as a finding, not waived.

## Domain-claim staleness candidates (step 5)

`docs/domain/` exists (`docs/domain/concepts/*.md`), so this check
applies. I grepped every `docs/domain/concepts/*.md` file for
`doc_mapping.py`, `relation_enrichment.py`,
`build_doc_relations_edges`, `_relation_needle`, `mentions_artifact` and
inspected each hit's **References block** specifically (not just body
prose), since that's the step-5 trigger:

- `docs/domain/concepts/relationship-edge.md` — References block cites
  `src/codecompass/graph.py:50-360`/`:1184-1226` and
  `tests/test_graph.py:1426-1436`, none of which this phase's diff
  touched (`graph.py` and `test_graph.py` are both untouched by
  `0f3337d`/`29ced55`). **Not a candidate.**
- `docs/domain/concepts/derivation.md` — body prose quotes
  `DE-DOCORIGIN-001`'s own narration, which happens to mention
  `doc_mapping.py` (about the unrelated `origin`-enum write-site
  audit, not `mentions_artifact` matching), but its References block
  cites only `planning/knowledge/...` yaml records and
  `.claude/agents/context-researcher.md`, not `src/codecompass/doc_mapping.py`
  itself, and the behaviour it describes (origin-enum write sites) is
  untouched by this phase's diff either way. **Not a candidate.**

No domain-claim staleness candidates from this phase.

## Scope note

Checked: every current-truth doc hit for the changed
functions/behaviour (`grep` across `README.md`, `docs/`, `architecture/`,
`ai-docs/`), read against the actual diffs in `0f3337d`/`29ced55`, plus
the domain-corpus staleness check per step 5. Not checked: `decisions/*`
(out of this audit's scope by role definition — ADRs are append-only and
not "current-truth docs" in the same sense); `planning/context-gaps/inbox.md`
and `planning/learnings/promoted.md` (touched by `07c8475`, but planning
artifacts, not the `README.md`/`docs/`/`architecture/`/`ai-docs/` set
this audit covers); test files (not documentation).
