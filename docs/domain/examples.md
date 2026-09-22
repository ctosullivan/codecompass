---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Worked examples

Full walkthroughs spanning several concepts, kept separate from each
concept page's own single-concept example so the connective tissue
between concepts is visible in one place. Every concept-local example
lives on that concept's own page instead — this file exists for the
cases where seeing the whole chain matters more than any one link in it.

## 1. From a real gap to shipped code: the full traceability spine

`CG-005` (`planning/context-gaps/inbox.md`) — a real, filed context gap
from Ledgerkit's own reference-project work — is the one feature in this
project's history with a complete, real instance of every link in the
[traceability spine](../../planning/v1-redefinition/development-methodology.md#traceability-spine):

| Link | Real record | What it says |
|---|---|---|
| Evidence | `EV-DOCORIGIN-001` | `doc_artifacts.origin`'s current CHECK enum has no value for externally-sourced, revision-pinned reference material |
| Claim | `CL-DOCORIGIN-001` | The smallest correct fix is one new closed enum value, `pinned_reference`, with no other `origin` consumer requiring a change |
| Design Decision | `DEC-DOCORIGIN-001` | Add `pinned_reference`; detection via a YAML-frontmatter check (`resolved_commit` + `source_url`); explicit non-goal recorded alongside |
| Requirement | `REQ-DOCORIGIN-001` | `doc_artifacts.origin`'s CHECK constraint MUST accept `pinned_reference`; a Given/When/Then example; `status: verified` |
| Implementation | `src/codecompass/graph.py`'s `_migrate_doc_artifacts_constraints`, `spec_docs.py::_has_pinned_reference_frontmatter` | The real code |
| Test | `tests/test_graph.py`, `tests/test_spec_docs.py` (real test files exercising the migration and the frontmatter detector) | The real verification |

Reading this table top to bottom answers "why does this code exist";
reading it bottom to top answers "what evidence justifies this
behaviour" — the same chain, walked in either direction, using only
ids this project already produces. See
[`concepts/reference.md`](concepts/reference.md) sense (a) for what
`pinned_reference` itself means, and
[`concepts/requirement.md`](concepts/requirement.md)'s own counterexample
for a real gap this same feature's own citation chain missed (a
schema-version test file no Derivation had traced) — the traceability
spine being fully populated does not mean it was complete on the first
attempt.

## 2. One vendor query, five concepts in motion

`codecompass sync` against a real Haskell vendor,
`VendorConfig(name="hledger-lib", ecosystem=Ecosystem.HASKELL)`, touches
five of this corpus's own concepts in one real call sequence:

1. **[`vendor.md`](concepts/vendor.md)**: the `VendorConfig` itself —
   just a `(name, ecosystem)` pair, no logic, no path.
2. **[`ecosystem.md`](concepts/ecosystem.md)**: `Ecosystem.HASKELL`, the
   fixed enum member this vendor belongs to.
3. **[`adapter.md`](concepts/adapter.md)**: `get_adapter` constructs a
   `HaskellAdapter(config, project_root)` — the external-process
   strategy, since Haskell has no in-process implementation.
4. **[`protocol.md`](concepts/protocol.md)**: calling
   `.dependency_tree()` or `.symbols()` sends a real `analyze_project`
   request over the JSON-Lines wire contract to the
   `codecompass-adaptor-haskell` executable.
5. **[`capability.md`](concepts/capability.md)**: the response's
   `dependencies`/`symbols` sections are present only because the
   external process declared those two capabilities at `initialize` —
   if it hadn't, `HaskellAdapter.dependency_tree()` would raise
   `AdapterError` instead of silently returning nothing.

No single concept page tells this whole story end to end; each
describes its own link correctly, but the sequence only becomes visible
by tracing one real call across all five.

## 3. The same word, four unrelated meanings, in one sentence

A sentence like *"the reference project's context includes a digest of
its own reference material"* is grammatically fine and uses "reference"
and "context" correctly in casual English — but it packs in four
technically distinct senses this corpus documents separately:

- "**reference** project" — [`reference.md`](concepts/reference.md)
  sense (b): a whole external codebase, e.g. Ledgerkit.
- "**context**" — [`context.md`](concepts/context.md) sense 2: the
  informal umbrella for everything an agent might read.
- "**digest**" — [`digest.md`](concepts/digest.md): one specific,
  per-vendor, deterministic-plus-enrichment rendering — not a synonym
  for "context," one instance of it.
- "**reference** material" — [`reference.md`](concepts/reference.md)
  sense (a): a `doc_artifacts.origin='pinned_reference'` row, the
  output of the reference-experiment ingestion pipeline that sits
  *between* senses (a) and (b).

This is not a contradiction — every sense is independently real and
independently well-evidenced — but it is exactly the kind of sentence
that reads as consistent while quietly relying on a reader already
knowing which of several real meanings applies to a repeated word.
Naming this explicitly is this corpus's own reason to exist.
