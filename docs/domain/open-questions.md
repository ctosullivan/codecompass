---
status: DRAFT — pending domain-skeptic review and actual-user approval
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

7. **The Stage E graph-level vs. file-based `Evidence`/`Observation`/
   `Claim`/`Decision` naming collision** — Phase 57's own candidate
   design for `context-graph.db`-level provenance entity kinds reuses
   the exact names Phase 54c's file-based model already uses, for an
   entirely different purpose (a queryable database row about another
   project's dependencies, vs. a file-based record of CodeCompass's own
   development-process reasoning). Already named and explicitly deferred
   to Stage E's own future Domain stage in
   `planning/v1-redefinition/roadmap.md`'s own Stage E entry — this
   corpus re-states, not re-litigates, an already-managed deferral.
   Whichever future phase builds Stage E must resolve this — either
   picking genuinely distinct names for the graph-level concepts, or
   explicitly justifying sharing the terms with a stated disambiguation
   rule — not silently overload them a second time.
   *(`evidence.md`, `observation.md`, `claim.md`, `decision.md`, each
   own "What X is NOT" section; `CL-EVID-003`, `CL-EVID-009`)*

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

These are real `src/codecompass/` gaps this research found incidentally
while investigating what a concept *means* — they do not affect the
domain corpus's own definitions and are routed to
`planning/learnings/inbox.md` as future-improvement candidates for
`knowledge-curator` to triage, not resolved here (matching Phase 63D's
own scope boundary: evidence and documentation only, no `src/` change):

9. **`symbol_enrichment` has no provenance column at all** — unlike
   `vendor_enrichment`/`doc_relation_enrichment`, which both carry a
   `model TEXT NOT NULL` column. `decisions/0054`'s own claim that all
   three enrichment tables uniformly distinguish producers "using a
   column that has existed since Phase 14" is factually wrong for
   `symbol_enrichment` specifically, independently re-confirmed by
   `domain-skeptic` against the real schema. See
   [`concepts/provenance.md`](concepts/provenance.md).
10. **The external protocol's wire-level `ecosystem` field, and its
    `capabilities` list, are received but never validated against their
    own closed sets** — `ExternalAdapterProcess.ecosystem` is set and
    never subsequently read/compared anywhere in `src/codecompass/`; the
    `capabilities` tuple is stored with no membership check against the
    protocol's own closed 4-value set. Both independently re-confirmed
    by `domain-skeptic` via direct grep. See
    [`concepts/ecosystem.md`](concepts/ecosystem.md) and
    [`concepts/capability.md`](concepts/capability.md).
