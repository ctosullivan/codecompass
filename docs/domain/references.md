---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# References

A consolidated index of the primary evidence this corpus draws from.
Every concept page carries its own, more specific references block —
this page groups the same material by *kind of source* rather than by
concept, for whoever wants to check the underlying evidence trail
directly rather than one concept at a time.

## The evidentiary model itself

- `planning/phase-54c-evidence-knowledge-workflow.md` — the six record
  kinds' own schema definitions (§2.2), provenance fields (§2.3),
  historical-preservation rule (§2.4), the Context Researcher role
  (§3), the review-gate lifecycle and four-way distinction (§5),
  context-packet contract (§6).
- `planning/retros/phase-54c-evidence-knowledge-workflow.md` — the
  honest disclosure of what was, and wasn't, exercised by real use.
- `planning/v1-redefinition/development-methodology.md` — the named
  five-stage methodology this corpus is the first project-scoped
  application of; the traceability spine; the re-entry/replanning
  rules; the post-v1 per-feature freshness gate.
- `scripts/check_knowledge_base.py` — the mechanical validator
  enforcing the hard rules (Decision-never-supersedes-Claim, etc.)
  described on `concepts/claim.md`/`concepts/decision.md`.
- Real example knowledge-base directories:
  `planning/knowledge/hledger-depth/`,
  `planning/knowledge/doc-origin-pinned-reference/`,
  `planning/knowledge/haskell-api-surface-extraction/` — pre-existing,
  single-feature applications of the same model this corpus generalizes
  to project scope.
- `planning/knowledge/codecompass-domain/` — this corpus's own 135+
  Observation/Evidence/Claim/Derivation records, id-prefixed by cluster:
  `EVID` (the evidentiary model itself), `CTXT` (context/packaging/
  relationships), `ADPT` (adapters/protocol/ecosystem boundaries),
  `SKEP` (`domain-skeptic`'s own resolving evidence).

## Governance and process

- `CLAUDE.md` — the project's own governing rules; §0 (protected files,
  including `decisions/*`'s append-only discipline), §1 (plan before
  implementing), §2 (kept-in-sync docs), §8 (agent-led development).
- `decisions/0060-scope-plan-domain-design-implement-methodology.md` —
  the ADR formalizing Phase 63D, the five-stage methodology, and the
  `domain-skeptic` role's own escalation/write-boundary rules this
  corpus's own review was conducted under.
- `planning/v1-redefinition/agent-led-development.md` §2.13 —
  `domain-skeptic`'s own roster entry.
- `.claude/agents/context-researcher.md`, `.claude/agents/domain-skeptic.md` —
  the two agent roles that produced and reviewed this corpus.
- `planning/phase-63d-domain-reconstruction.md` — this phase's own
  plan, including its explicit concept list and `docs/domain/` layout.
- `planning/learnings/`, `planning/context-gaps/`,
  `planning/context-observations/` — the three adjacent "something was
  noticed" queues disambiguated on `concepts/observation.md`.

## Source code

- `src/codecompass/core.py` — `VendorConfig`, `Ecosystem`,
  `VendorDigest`.
- `src/codecompass/adapters/base.py`,
  `src/codecompass/adapters/__init__.py`,
  `src/codecompass/adapters/haskell.py`,
  `src/codecompass/adapters/external_process.py` — the adapter
  interface, dispatch, and external-process protocol client.
- `src/codecompass/graph.py` — `context-graph.db`'s own real schema:
  every edge table, `doc_artifacts`, and the three enrichment tables.
- `src/codecompass/sync.py` — `sync_vendor`, digest construction.
- `src/codecompass/enrichment.py` — AI-authored enrichment writers.
- `src/codecompass/spec_docs.py` — `pinned_reference` frontmatter
  detection.

## Decisions (ADRs)

- `decisions/0002` — adapter approach differs per ecosystem.
- `decisions/0031`, `decisions/0035` — Phase 16's `VendorConfig`
  narrowing.
- `decisions/0038` — relation enrichment is natural-key-only, no FK.
- `decisions/0051` — agent-suggested context is captured, not graphed.
- `decisions/0054` — agent-driven enrichment is a second,
  non-authoritative producer.
- `decisions/0057` — the external-process adapter protocol.
- `decisions/0058` — the adapter protocol and Haskell adapter as
  separate repositories (see `concepts/protocol.md`'s own resolved
  naming-drift finding, `CL-ADPT-010`).
- `protocol/codecompass-adaptor-protocol/SCHEMA.md` — the checked-out
  submodule that canonicalizes and supersedes `decisions/0057`'s own
  inline protocol description.

## Tests

- `tests/test_graph.py` — schema, migrations, the enrichment tables'
  own FK/provenance shape.
- `tests/test_adapters_base.py`, `tests/test_adapters_dispatch.py`,
  `tests/test_adapter_haskell.py`,
  `tests/test_adapters_external_process.py` — adapter/protocol
  behaviour, including `tests/fixtures/fake_adapter.py`'s real
  end-to-end protocol exercise.
- `tests/test_spec_docs.py` — `pinned_reference` detection.

## Real generated artifacts

- `vendor/typer/CLAUDE.md` (this exact repository) — a real digest,
  cited on `concepts/digest.md`.
- `planning/knowledge/doc-origin-pinned-reference/context-packet.md` — a
  real, already-shipped context packet, cited on
  `concepts/context-packet.md`.
