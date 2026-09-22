---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Glossary

One paragraph per concept, cross-linked to its own fuller page. Read
this first — it is the fastest way to see what each term means and how
it differs from its nearest neighbours, before going deeper into any
one page's own evidence, invariants, and edge cases.

## The evidentiary model

**[Evidence](concepts/evidence.md)** is a neutral record of what was
found — never whether it supports or contradicts anything. That
judgment belongs only to a **[Claim](concepts/claim.md)**, an agent's
interpretation built from Evidence, which is the only record kind
allowed to say "this supports/contradicts this reading." A
**[Derivation](concepts/derivation.md)** records the reasoning *process*
behind one Claim — not just its conclusion. An
**[Observation](concepts/observation.md)** is the single, dated act of
looking (running a command, reading a file) that Evidence is built
from. A **[Decision](concepts/decision.md)** is the one record kind
only a human/project-owner authors — it chooses what the project does
about a Claim, and can never make a Claim wrong. A
**[Requirement](concepts/requirement.md)** is the specific, testable
statement a coding agent implements against, always tracing back
through a Decision to the Claim/Evidence behind it.

**[Invariant](concepts/invariant.md)** is not a formal record kind at
all — it's a plain-English label attached to at least three unrelated
artifacts in this repository, with no requirement they ever coincide.
**[Provenance](concepts/provenance.md)** ("who produced this, from
what") is likewise never a unified schema — it's realized three
structurally different ways depending on which mechanism you're
looking at.

## Context, packaging, and relationships

**[Context](concepts/context.md)** is an umbrella word spanning at
least five genuinely distinct things in this project — there is no
single artifact you can point to and call "the context." A
**[context packet](concepts/context-packet.md)** is one narrow,
specific instance: Phase 54c's curated, per-feature Implement-stage
artifact, produced only after a `design.md` reaches `APPROVED`. A
**[digest](concepts/digest.md)** is a different, unrelated-in-mechanism
instance: `VendorDigest`, generated unconditionally on every `sync` for
every tracked vendor. Neither is a generalisation of the other. A
**[relationship / edge](concepts/relationship-edge.md)**, precisely, is
a real, typed row in one of `context-graph.db`'s six edge tables —
deliberately distinct from an agent-suggested candidate (never a graph
fact until promoted) and from AI enrichment commentary about an edge
(never itself a fact). **[Reference](concepts/reference.md)** is used
in three unrelated senses: a graph-level provenance classification, an
entire external "reference project" like Ledgerkit, and a plain
citation field inside an Evidence record or this corpus's own
references blocks.

## Adapters, protocol, and ecosystem boundaries

A **[vendor](concepts/vendor.md)** is one tracked dependency — a
`(name, ecosystem)` pair, pure configuration data with no logic of its
own. An **[ecosystem](concepts/ecosystem.md)** is the fixed, closed
4-member category (npm/Python/Cargo/Haskell) a vendor belongs to. An
**[adapter](concepts/adapter.md)** is the code implementing
ecosystem-specific logic for one ecosystem value — either an in-process
Python class, or a thin dispatcher delegating to an independent
external process. A **[protocol](concepts/protocol.md)** is the wire
contract an external-process adapter speaks — closed methods, closed
capabilities, closed error codes, JSON Lines framing. A
**[capability](concepts/capability.md)** is one of exactly four
protocol-level strings an adapter declares to gate which result
sections it may return — a much narrower, stricter concept than
casually calling something a CodeCompass "feature."
**[Connector](concepts/connector.md)** is not a real, distinct
CodeCompass concept at all — no source, test, or ADR in this repository
uses the word for any mechanism; if you mean "the thing CodeCompass
uses to talk to an ecosystem," the correct term is **adapter**.

## Where to go next

- [`invariants.md`](invariants.md) — cross-cutting rules pulled from
  several concept pages at once.
- [`examples.md`](examples.md) — full worked walkthroughs spanning
  several concepts.
- [`open-questions.md`](open-questions.md) — everything this research
  found genuinely unresolved, and why none of it needed escalating.
- [`references.md`](references.md) — the underlying evidence trail,
  grouped by kind of source.
- [`concepts/`](concepts/) — the full page for each term above.
