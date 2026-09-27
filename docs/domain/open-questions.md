---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Open questions

Every genuinely unresolved item this domain reconstruction found, after
real attempted resolution — never resolved by guessing, never silently
dropped. An item appears here only after `domain-skeptic`'s own
independent review confirmed it has no current behavioural consequence
and does not need the actual user/domain owner's attention right now.
None of these blocked approving the rest of the corpus.

An item here stays here until a Decision record resolves it, or a new
Claim genuinely settles it with further evidence — never removed
silently, only marked resolved with a pointer to what resolved it
(matching the traceability spine's own
[re-entry rules](../../planning/v1-redefinition/development-methodology.md)).

## Terminology looseness (no current behavioural consequence found)

1. **The five senses of "context"** ([`concepts/context.md`](concepts/context.md)).
   No single canonical definition exists in the repository; the closest
   thing to one (`ai-docs/README.md`'s own opening line) treats "context
   graph" and "digest" as separate nouns, consistent with, not
   contradicted by, the five-way split. Whether this umbrella term needs
   a formal vocabulary fix, or whether the looseness is harmless, is a
   product/naming decision, not something evidence alone resolves.
   *(`CL-CTXT-001`)*
2. **Three informal senses of "digest"** ([`concepts/digest.md`](concepts/digest.md))
   — the `VendorDigest` object, the full persisted per-vendor file set,
   and specifically the vendor's own `CLAUDE.md` text. Nested, not
   contradictory, but never defined side by side in one place. A
   style/terminology question, not a factual one. *(`EV-CTXT-010`)*
3. **Is "relationship" one concept with six instantiations, or six
   separate concepts that happen to share a foreign-keyed-table
   implementation?** ([`concepts/relationship-edge.md`](concepts/relationship-edge.md)).
   `doc_relations_edges` has its own closed `relation_kind` enum;
   `routes_via_edges`/`skill_mentions_edges`/`depends_on_edges` do not,
   because each table's own name already encodes its one relationship
   kind. Not settled anywhere in the repository's own prose; no
   behavioural consequence either way. *(`CL-CTXT-003`)*
4. **Should the three senses of "invariant" ever be cross-referenced or
   unified?** ([`concepts/invariant.md`](concepts/invariant.md)) — a
   `planning/learnings/` classification value, a per-feature `design.md`
   narrative subsection, and this corpus's own `invariants.md`
   (below). Independently real and independently well-evidenced; nothing
   in Phase 54c's model or Phase 63D's own plan states whether they
   ought to coincide. A documentation-design question. *(`CL-EVID-007`)*
5. **Is Claim/Derivation's observed 1:1 pairing a real invariant of the
   model, or an untested property of three small proving cases?**
   ([`concepts/derivation.md`](concepts/derivation.md)) — nothing in the
   schema or `scripts/check_knowledge_base.py` actually forbids a future
   Derivation explaining more than one Claim; no such instance has ever
   occurred to test it either way. *(`CL-EVID-004`)*
6. **Is a bare, unqualified "adapter" in this project's own prose
   ambiguous between `EcosystemAdapter` and the doc-only "host-output
   adapter" classification label?** ([`concepts/adapter.md`](concepts/adapter.md))
   — `architecture/overview.md` already flags this itself; the second
   sense has no source-level counterpart at all (zero hits for the word
   "adapter" in `skill.py`/`commands.py`/`index.py`). A naming-clarity
   observation about existing prose, not a code-level ambiguity.
   *(`EV-ADPT-007`, `CL-ADPT-007`)*

## Deferred to a future phase, already managed

7. **The graph-level vs. file-based `Evidence`/`Observation`/`Claim`/
   `Decision` naming collision** — a candidate design for
   `context-graph.db`-level provenance entity kinds (originally sketched
   as part of the redefined-v1 effort's own "Stage E," now re-homed to
   Priority B, `decisions/0062`; `planning/pre-v1-disposition.md` §7)
   reuses the exact names Phase 54c's file-based model already uses, for
   an entirely different purpose (a queryable database row about another
   project's dependencies, vs. a file-based record of CodeCompass's own
   development-process reasoning). Already named and explicitly deferred
   to whichever future Priority B phase takes up this candidate design's
   own Domain stage — the collision itself is documented, unresolved,
   and unaffected by the retirement of the old "Stage E" phase-group
   label; only the label naming its future resolution vehicle changed.
   Whichever future phase takes this up must resolve it — either picking
   genuinely distinct names for the graph-level concepts, or explicitly
   justifying sharing the terms with a stated disambiguation rule — not
   silently overload them a second time. The original collision is
   still documented at `planning/v1-redefinition/roadmap.md:1061-1087`
   (historical, unedited).
   *(`evidence.md`, `observation.md`, `claim.md`, `decision.md`, each
   own "What X is NOT" section; `CL-EVID-012`, `CL-EVID-011`)*

## Documentation cross-reference gaps (not domain ambiguities)

8. **`planning/context-observations/inbox.md` entries are literally
   id-prefixed `OBS-NNN`**, colliding textually with Phase 54c's own
   `OBS-<feature>-NNN` Observation record prefix, despite completely
   different field shapes and purposes (confirmed independently by
   `domain-skeptic`: `planning/context-observations/TEMPLATE.md:6` uses
   `### OBS-NNN` as its own entry heading). Nothing about *meaning* is
   actually unclear — an Observation and a context-observation are
   [correctly distinguished](concepts/observation.md) — only that
   neither directory's own README cross-references the other to warn of
   the surface-level collision. Recommended fix (documentation polish,
   not a domain question): a one-line cross-reference note in each
   directory's own README. *(`CL-EVID-002`, `EV-EVID-010`)*

## Known implementation gaps, not domain-meaning ambiguities

These were real `src/codecompass/` gaps this research found incidentally
while investigating what a concept *means* — they did not affect the
domain corpus's own definitions and were routed to
`planning/learnings/inbox.md` as future-improvement candidates
(`L-031`, `L-032`) for `knowledge-curator` to triage (matching Phase
63D's own scope boundary: evidence and documentation only, no `src/`
change at the time). Both have since been resolved, at Phase 74 — kept
here, prefixed **RESOLVED**, rather than silently removed, per this
file's own re-entry convention:

9. **RESOLVED (Phase 74, closes `L-031`) — `symbol_enrichment` now has
   a provenance column.** Previously: `symbol_enrichment` carried no
   provenance column at all, unlike `vendor_enrichment`/`doc_relation_
   enrichment` (`model TEXT NOT NULL`). As of Phase 74, `symbol_
   enrichment.model` exists (`src/codecompass/graph.py:176-182`), and
   `record_symbol_enrichment` requires a real `model` argument for
   every new write (its one production call site, `enrichment.py:427`,
   supplies it). Residual, narrower point not closed by this fix:
   `symbol_enrichment.model` is nullable and every pre-Phase-74 row
   backfills an honest `NULL`, unlike the two sibling `NOT NULL`
   columns — see [`concepts/provenance.md`](concepts/provenance.md)'s
   own Counterexample section. *(`EV-EVID-015`, `OBS-EVID-017`–`019`,
   superseding the prior `OBS-EVID-011`-documented gap.)*
10. **RESOLVED (Phase 74, closes `L-032`) — the external protocol's
    wire-level `ecosystem` field and `capabilities` list ARE now
    validated against their own closed sets.** Previously:
    `ExternalAdapterProcess.ecosystem` was set and never subsequently
    read/compared anywhere in `src/codecompass/`, and the `capabilities`
    tuple was stored with no membership check. As of Phase 74,
    `initialize()` requires an `expected_ecosystem` argument and raises
    `AdapterError` on a mismatch, and separately raises `AdapterError`
    on any `capabilities` entry outside the module's own closed
    `CAPABILITIES` set. `HaskellAdapter`'s one production call site
    passes the real `core.Ecosystem` value. Fully closed — no residual
    gap found. See [`concepts/ecosystem.md`](concepts/ecosystem.md) and
    [`concepts/capability.md`](concepts/capability.md)'s own
    Counterexample sections. *(`EV-ADPT-011`, `EV-ADPT-012`,
    `OBS-ADPT-018`–`020`, superseding the prior `OBS-ADPT-005`/
    `OBS-ADPT-017`-documented gaps.)*
