# Historical notes

Part of the `architecture/` reference set, but unlike its siblings this
page is deliberately **historical**, not current-state: it narrates two
past behavior changes that are genuinely load-bearing for understanding
*why* today's code looks the way it does, but that have no ADR of their
own to point to. Everywhere else in `architecture/`, phase-chronology
framing ("used to X, now Y") is treated as a defect to be rewritten into
plain present tense — here it is the correct format, because the story
itself is the point. See [`overview.md`](overview.md) for the
current-state description of both mechanisms discussed below.

## Routing-table / tool-Skill refresh timing

**Symptom, confirmed directly during this project's own first live
enrichment run**: after a vendor was usage-driven AI-enriched inside a
single `codecompass sync` or bare `codecompass` invocation, the root
`CLAUDE.md` routing table and the tool-level Skill still showed
`Enriched: no` for that vendor until a separate `codecompass index` was
run afterward.

**Cause**: the routing table and the tool-level Skill were regenerated
*before* the enrichment step ran, not after it. Both artifacts are
derived from `context-graph.db`'s `has_enrichment` query, and the graph
itself had already been rebuilt before enrichment — but the *rendering*
of the routing table and tool Skill happened at the wrong point in the
sequence, reading a graph that hadn't yet been rebuilt a second time to
pick up what enrichment had just written. `sync`'s whole-project branch
had a separate bug on top of this: it never called this regeneration
step at all — only `index` and bare `codecompass` did.

**Fix**: `cli._refresh_generated_artifacts` now runs once, unconditionally,
at the very end of the whole bare-`codecompass`/`sync` invocation — after
the enrichment step returns, regardless of whether it succeeded, was
declined, or was budget-aborted (a `try`/`finally` around the enrichment
call guarantees this). It performs a second, full
`rebuild_project_graph` pass (not a partial update — the graph's rebuild
function has no partial-update mode) before re-deriving the routing
table and tool Skill from it. This also means `context-graph.db` picks
up any Skill/`.mdc` file enrichment just wrote in the same invocation —
fixing `codecompass undo`'s graph-backed enumeration and `codecompass
query skills` missing a vendor's brand-new per-vendor Skill until the
next whole-project sync. `sync`'s whole-project branch now shares the
same post-enrichment call `_bootstrap` already had.

See `planning/phase-20-refresh-generated-artifacts-after-enrichment.md`
for the original investigation — this is the only existing pointer to
this fix; no ADR was ever written for it, since it is a bug fix to an
existing mechanism's sequencing, not a new design tradeoff.

## Relationship-enrichment excerpt centering

**Original behavior**: when `codecompass.relation_enrichment` asked an AI
call to explain how a spec doc relates to something it had already
mechanically proven a mention of, the excerpt of source text sent to the
model was always a fixed `source_text[:4_000]` slice — the first 4,000
characters of the file, regardless of where in the file the actual
mechanical mention (the word-boundary match that created the
`doc_relations_edges` row in the first place) landed.

**Problem, confirmed against this repo's own data**: for a mention that
occurred past that 4,000-character offset — this repository's own two
`"anthropic README.md"` relationships both did — the model never saw the
sentence that actually triggered the relationship at all. It produced a
plausible-sounding but ungrounded summary based on whatever unrelated
content happened to be in its fixed window instead.

**Fix, in two steps**:

1. `relation_enrichment.select_candidates` was changed to re-derive the
   same needle the mechanical detection step originally matched (the
   target vendor's name for a `mentions_dependency` relationship, or the
   target doc artifact's own `name` field for a `mentions_artifact`
   relationship), re-run the identical word-boundary search against the
   source text, and — when found — slice a window *centered* on the
   match (1,000 characters before, 3,000 after; the asymmetric split
   favors context that typically follows a mention) instead of the
   file's start. The match position is deliberately re-derived at
   enrichment time rather than persisted from the original detection
   step, so the purely-mechanical `doc_relations_edges` table stays free
   of any enrichment-specific data (`decisions/0042`). A needle that can
   no longer be found (the file changed since the last graph rebuild)
   falls back to the original first-N-characters slice, non-fatal — this
   is why that fallback still exists in today's code, not because anyone
   still prefers it.
2. Once heading-based document chunking (`doc_chunking.py`,
   `decisions/0046`) existed, the excerpt selection was refined further:
   when the matched edge has an attributed chunk (its own heading-scoped
   slice of the source doc), that chunk's own text is used directly,
   with no character cap, in preference to the fixed-window guess above.
   The needle-re-derivation-plus-fixed-window logic from step 1 was not
   deleted — it remains the fallback for any candidate without a chunk
   (a headerless source doc, or a match spanning more than one chunk).

Both steps are described in present tense as current behavior in
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md)'s
"Phase B" section; this note exists only to explain *why* the fallback
path still contains fixed-window slicing logic that might otherwise look
like an oversight rather than a deliberate, still-reachable fallback.
