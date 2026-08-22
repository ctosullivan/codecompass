# Phase 29: Vendor docs as relationship sources

## Scope

Found via direct user observation during a `/discovery` session testing
Phase 26-28's real output, confirmed against the actual current code (not
assumed): a vendor's own embedded upstream doc (`kind='vendor_doc'`,
Phase 27) is currently wired into the graph as **passive, indexed
content only** — it can be a `mentions_artifact` *target* (a spec doc
name-dropping it), but it is never itself a *source* of any relationship,
and it's explicitly excluded from symbol-mention detection entirely. Two
concrete gaps, both confirmed by reading the live code:

1. **`doc_mapping.build_documents_edges`'s kind filter excludes
   `vendor_doc`**: `if row.kind not in ("claude_md", "overview") or
   row.vendor_name is None: continue`. A vendor's own README — arguably
   the single most authoritative source for "this doc documents this
   symbol," since it's the upstream authors documenting their own API —
   never produces a `documents_edges` row. Only codecompass's own
   generated `CLAUDE.md`/`OVERVIEW.md` do.
2. **`doc_mapping.build_doc_relations_edges` only ever scans spec docs
   outward** (`decisions/0037`'s "spec-doc-outward-only" design, reaffirmed
   in `decisions/0041`). A vendor doc mentioning another tracked vendor,
   a Skill, or another vendor doc produces nothing — the relationship
   graph only lights up when *this* project's own docs happen to
   name-drop it, never when the vendor doc's own content does.

**Covered:**
- `build_documents_edges`: widen the kind filter to `("claude_md",
  "overview", "vendor_doc")`. `vendor_doc` rows already carry
  `vendor_name` (Phase 27), so no other change to this function is
  needed — a vendor's README now produces real `documents_edges` rows for
  every one of its own symbols it word-boundary-mentions, the same
  heuristic already applied to codecompass's own generated digests.
- `build_doc_relations_edges`: generalize its first parameter from
  `spec_doc_rows` to accept **both** spec docs and vendor docs as
  scannable sources — rename to `source_doc_rows: list[DocArtifactRow]`,
  process any row whose `kind` is in `{"spec_doc", "vendor_doc"}` (an
  explicit allow-set, not "everything not otherwise excluded" — see
  Design decisions for why this must stay a closed set). `sync.py`'s call
  site passes `spec_doc_rows + vendor_upstream_doc_rows` instead of just
  `spec_doc_rows`.
- **Self-mention exclusion, the one genuinely new piece of logic**: when
  the source row is a `vendor_doc` belonging to vendor `V`, skip emitting
  a `mentions_dependency` edge where the target vendor is also `V` — a
  package's own README mentioning its own name is guaranteed, universal,
  and adds no signal (unlike a spec doc mentioning a vendor, which is
  always meaningful evidence of a real relationship). No equivalent
  self-target exclusion is needed for `mentions_artifact` — a vendor doc
  word-boundary-matching *its own* `name` field against its own body text
  is already extremely unlikely (the `name` field is a synthetic
  `f"{vendor} {filename}"` string like `"anthropic README.md"`, not
  something a document's own prose would organically contain about
  itself) and not worth a special case without evidence it happens.
- Tests: `build_documents_edges` now processes a `vendor_doc` fixture and
  finds real symbol mentions in it; `build_doc_relations_edges` accepts a
  vendor-doc source and detects a `mentions_dependency` edge to a
  *different* tracked vendor, and confirms self-mention exclusion (a
  vendor doc mentioning its own vendor name produces no edge for that
  vendor specifically, while still detecting a different vendor it also
  mentions); a `mentions_artifact` case sourced from a vendor doc.

**Explicitly deferred / out of scope:**
- Any change to `graph.py`'s schema — `doc_relations_edges` already
  supports an arbitrary `doc_artifacts` row as `source_doc_artifact_id`;
  nothing there assumed "source is always a spec doc." This phase is
  pure `doc_mapping.py`/`sync.py` wiring, no migration needed.
- Any change to `relation_enrichment.py`'s AI-enrichment path — it
  already operates generically over whatever `doc_relations_edges`
  contains via `graph.relation_enrichment_candidates`, with no
  assumption about the source's `kind`. A vendor-doc-sourced relationship
  becomes an enrichment candidate automatically, same usage-proven gating
  as every other relationship.
- `check`'s coverage-gap sections — `spec_docs_without_relations` and
  `vendor_docs_without_relations` both already query by `kind`/column
  independent of this change; `vendor_docs_without_relations` specifically
  checks `target_doc_artifact_id`, which remains correct since a vendor
  doc's role as a *target* is unaffected by it also now being able to act
  as a *source*. No change needed there, confirm at implementation time
  this holds.
- Extending `skill_scan.build_skill_mentions_edges` similarly (a Skill
  mentioning a vendor doc, or vice versa) — a distinct, separately-scoped
  table (`skill_mentions_edges`) with its own narrower contract
  (`decisions/0037`'s "Alternatives considered" already rejected merging
  it with `doc_relations_edges`). Not touched here.

## Design decisions

**A closed allow-set (`{"spec_doc", "vendor_doc"}`), not "any kind not
explicitly excluded."** Considered making `build_doc_relations_edges`
scan *every* doc artifact kind as a potential source, now that it's
already generalized beyond spec docs alone. Rejected: a codecompass-
*generated* artifact (`claude_md`, `overview`, `skill`, `cursor_mdc`,
`slash_command`) being scanned as a relationship source would mean
codecompass's own templated output mentioning a vendor by name (which it
always does, structurally) creates edges describing codecompass talking
about itself — noise, not signal, the same reasoning behind the
self-mention exclusion above but at the level of "should this kind of
document even be eligible," not just "should this one self-referential
edge be suppressed." Keeping the source-kind set explicit and closed
means adding a new source kind later is a deliberate, visible one-line
change, not an accidental side effect of some other doc kind's origin
changing.

**Self-mention exclusion only for `mentions_dependency`, not
`mentions_artifact`, and only by vendor identity, not by path
comparison.** A vendor doc's *own* vendor is known directly from its
`DocArtifactRow.vendor_name` — comparing that to the target vendor name
being considered is a cheap, exact check with no edge cases. This is
narrower than a generic "never emit a self-referencing edge" rule (which
would also need to handle a vendor doc word-boundary-matching its own
`name` field, already addressed by argument above without needing code
for it) — solving exactly the one guaranteed-noise case found, not a
broader speculative one.

## Files

- `src/codecompass/doc_mapping.py` — `build_documents_edges`'s kind
  filter; `build_doc_relations_edges`'s parameter rename/generalization
  and the self-mention exclusion.
- `src/codecompass/sync.py` — updated call site (`spec_doc_rows +
  vendor_upstream_doc_rows` as the new combined source argument).
- `tests/test_doc_mapping.py` — new cases per Covered above.
- `architecture/overview.md` — "Context graph" section's description of
  `documents_edges`/`doc_relations_edges` updated to describe vendor docs
  as eligible sources, not just targets.
- `decisions/` — new ADR (next sequential number) covering the closed
  allow-set decision and the self-mention exclusion — both non-obvious
  tradeoffs.

## Verification

- `pytest`/`ruff check .` — full suite passes, including new cases.
- Manual, against this repo itself (the established dogfooding pattern):
  re-run a whole-project `sync`, then confirm via `codecompass query
  vendor anthropic --json` (or direct `sqlite3`) that `vendor/anthropic/
  src/README.md` now appears among `anthropic`'s `documenting_artifacts`
  (Part 1's fix); confirm via `sqlite3`/`query relations` that at least
  one `vendor_doc`-sourced row now exists in `doc_relations_edges` where
  none did before, and that no self-referencing `anthropic → anthropic`
  `mentions_dependency` edge was created from `vendor/anthropic/src/
  README.md` despite that file certainly mentioning "anthropic" itself
  repeatedly (the concrete proof the self-mention exclusion actually
  fires, not just passes a synthetic unit test).
