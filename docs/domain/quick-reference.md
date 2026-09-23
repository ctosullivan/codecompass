---
status: derived (Phase 65, direct-quote compression of `glossary.md`; no new domain content, no separate domain-owner review)
---

# Quick reference: CodeCompass domain terms

One line per term, for the "I met this word in CLI output / a generated
file / a code comment, what does it mean" case. Every line is a
verbatim or near-verbatim quote from
[`glossary.md`](glossary.md) — the corpus's own existing "one paragraph
per concept" summary, compressed here one step further into a scannable
table. **This table is not a new definition of anything** — where it
shortens the glossary's own sentence, it does so by cutting
cross-references, not by changing meaning; read the linked concept page
for the full definition, invariants, and edge cases.

| Term | Meaning (quoted from `glossary.md`) | Full page |
|---|---|---|
| **Evidence** | "a neutral record of what was found — never whether it supports or contradicts anything" | [`concepts/evidence.md`](concepts/evidence.md) |
| **Claim** | "an agent's interpretation built from Evidence... the only record kind allowed to say 'this supports/contradicts this reading'" | [`concepts/claim.md`](concepts/claim.md) |
| **Derivation** | "records the reasoning *process* behind one Claim — not just its conclusion" | [`concepts/derivation.md`](concepts/derivation.md) |
| **Observation** | "the single, dated act of looking (running a command, reading a file) that Evidence is built from" | [`concepts/observation.md`](concepts/observation.md) |
| **Decision** | "the one record kind only a human/project-owner authors — it chooses what the project does about a Claim, and can never make a Claim wrong" | [`concepts/decision.md`](concepts/decision.md) |
| **Requirement** | "the specific, testable statement a coding agent implements against, always tracing back through a Decision to the Claim/Evidence behind it" | [`concepts/requirement.md`](concepts/requirement.md) |
| **Invariant** | "not a formal record kind at all — it's a plain-English label attached to at least three unrelated artifacts in this repository, with no requirement they ever coincide" | [`concepts/invariant.md`](concepts/invariant.md) |
| **Provenance** | "('who produced this, from what') is... never a unified schema — it's realized three structurally different ways depending on which mechanism you're looking at" | [`concepts/provenance.md`](concepts/provenance.md) |
| **Context** | "an umbrella word spanning at least five genuinely distinct things in this project — there is no single artifact you can point to and call 'the context'" | [`concepts/context.md`](concepts/context.md) |
| **Context packet** | "Phase 54c's curated, per-feature Implement-stage artifact, produced only after a `design.md` reaches `APPROVED`" | [`concepts/context-packet.md`](concepts/context-packet.md) |
| **Digest** | "`VendorDigest`, generated unconditionally on every `sync` for every tracked vendor" — neither is a generalisation of the other | [`concepts/digest.md`](concepts/digest.md) |
| **Relationship / edge** | "precisely, a real, typed row in one of `context-graph.db`'s six edge tables — deliberately distinct from an agent-suggested candidate (never a graph fact until promoted) and from AI enrichment commentary about an edge (never itself a fact)" | [`concepts/relationship-edge.md`](concepts/relationship-edge.md) |
| **Reference** | "used in three unrelated senses: a graph-level provenance classification, an entire external 'reference project'... and a plain citation field inside an Evidence record" | [`concepts/reference.md`](concepts/reference.md) |
| **Vendor** | "one tracked dependency — a `(name, ecosystem)` pair, pure configuration data with no logic of its own" | [`concepts/vendor.md`](concepts/vendor.md) |
| **Ecosystem** | "the fixed, closed 4-member category (npm/Python/Cargo/Haskell) a vendor belongs to" | [`concepts/ecosystem.md`](concepts/ecosystem.md) |
| **Adapter** | "the code implementing ecosystem-specific logic for one ecosystem value — either an in-process Python class, or a thin dispatcher delegating to an independent external process" | [`concepts/adapter.md`](concepts/adapter.md) |
| **Protocol** | "the wire contract an external-process adapter speaks — closed methods, closed capabilities, closed error codes, JSON Lines framing" | [`concepts/protocol.md`](concepts/protocol.md) |
| **Capability** | "one of exactly four protocol-level strings an adapter declares to gate which result sections it may return — a much narrower, stricter concept than casually calling something a CodeCompass 'feature'" | [`concepts/capability.md`](concepts/capability.md) |
| **Connector** | "not a real, distinct CodeCompass concept at all... if you mean 'the thing CodeCompass uses to talk to an ecosystem,' the correct term is **adapter**" | [`concepts/connector.md`](concepts/connector.md) |

## Note on "adapter" specifically

Two unrelated CodeCompass documentation senses of the bare word
"adapter" coexist — the `EcosystemAdapter` sense in this table, and
`architecture/overview.md`'s own separate "host-output adapter" label
for `skill.py`/`commands.py`/`index.py` (a documentation classification
with no source-level counterpart). See
[`concepts/adapter.md`](concepts/adapter.md)'s own "What it is NOT"
section for the full disambiguation. If you see "adapter" used for the
host-output-renderer sense elsewhere, that's this second, unrelated
sense — not a second `EcosystemAdapter` implementation.
