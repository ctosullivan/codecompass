# codecompass-domain — invariants and constraints

<!-- codecompass-knowledge: CL-ADPT-006 semantic-sha256:68a6628f083e31e8c91556ff21182ae8e2ffb9613504f6cac542fdaef9570f1f projection-sha256:b312a848e12e30b9dff5af0d5068f407e81c3b08df68a3bb098e7124f8d7b2f4 -->
### CL-ADPT-006

"capability" and "feature" are not interchangeable in this project. capability is the external adapter wire protocol's own specific, closed term: one of exactly four strings (dependencies, symbols, observations, diagnostics), declared by an adapter once at initialize, gating which of analyze_project's result sections that adapter may legitimately return. "feature" has no such role anywhere in this project -- it is ordinary, unscoped English used throughout ADRs/plans/roadmap prose for "a thing CodeCompass does or delivers," with no enumeration, no handshake, and no schema constraint attached to it. Casually calling something a CodeCompass "feature" (e.g. "the symbols() feature") is not wrong English, but it is never the same claim as declaring a protocol "capability" -- only the external adapter protocol has capabilities in this closed-set sense.

Supporting evidence: [EV-ADPT-009]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-007 semantic-sha256:8068d179a58a5df8ed964e8ebc024b9a48f9be14c8f26ba29b6bcfb87a12c451 projection-sha256:75f80db530658a85a1c50fbb503276c0d37fda1ef7f103a0a38bc58c4cd77c75 -->
### CL-ADPT-007

"adapter" is itself a genuinely fuzzy boundary inside this project's own documentation, not just relative to neighbouring terms: this project's own architecture doc names two distinct senses sharing the bare word "adapter" -- the ecosystem adapter (EcosystemAdapter, a real ABC with real subclasses in src/codecompass/adapters/) and the "host-output adapter" (skill.py/commands.py/index.py, a purely expository classification label with no corresponding class, interface, or shared base anywhere in source). A reader who encounters the bare word "adapter" in this project without a qualifying phrase cannot tell which sense is meant from the word alone; architecture/overview.md itself already flags this explicitly, which is independent confirmation this is a known, real ambiguity in this project's own vocabulary, not one this research invented.

Supporting evidence: [EV-ADPT-007]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-009 semantic-sha256:224479ff6311071dcbe88562848cb2e74d84bae1c18e5244d3726496e592d5e8 projection-sha256:30f5b6be5881ba6b8949df2d42079232362ee0fb9df2d652c1eedd523d5a2a95 -->
### CL-ADPT-009

The external adapter protocol's own `ecosystem` field (returned in an adapter's initialize response) is deliberately unconstrained free text at the protocol-specification level (SCHEMA.md states outright "this protocol does not define a closed ecosystem enum"), in contrast to CodeCompass's own internal Ecosystem enum (a closed 4-member set). In the current implementation this is not merely a specification looseness but an observed, currently-inert gap: the wire-reported value is stored on ExternalAdapterProcess.ecosystem after initialize() but is never subsequently read, compared against core.Ecosystem, or used for any dispatch or validation decision anywhere in src/codecompass/ -- dispatch is driven entirely by VendorConfig.ecosystem, fixed on the CodeCompass side before the adapter process is even spawned. This is a genuine edge case worth naming on the ecosystem/protocol concept pages: nothing currently prevents an external adapter from reporting an `ecosystem` string that disagrees with the Ecosystem value CodeCompass configured it under, and no observed behaviour would currently detect or surface that disagreement.

Supporting evidence: [EV-ADPT-010]
Status: status=superseded
Provenance: HISTORICAL
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-011 semantic-sha256:6d68314362a0466de8ac90a922c3e456c11c8e85b411035a5a5cbb6a1b72c411 projection-sha256:2438842edccccfec88278da4647d640d0b3c8eea5cf2281e497558288aff3a7b -->
### CL-ADPT-011

The external adapter protocol's own `ecosystem` field (returned in an adapter's initialize response) remains deliberately unconstrained free text at the protocol-specification level (SCHEMA.md still states outright "this protocol does not define a closed ecosystem enum"), in contrast to CodeCompass's own internal Ecosystem enum (a closed 4-member set) -- that part of CL-ADPT-009's statement is unaffected and does not need re-deriving. But CL-ADPT-009's further claim that this was, in the current implementation, "an observed, currently-inert gap" with "no observed behaviour" to detect a mismatch is false as of Phase 74 (`L-032`, landed `050e366993a8831beda9f3a729bbdbaae22cc029`): `ExternalAdapterProcess.initialize` now takes a required keyword-only `expected_ecosystem: str` argument and, immediately after setting `self.ecosystem` from the wire response, raises `AdapterError` ("external adapter ecosystem mismatch: CodeCompass configured this adapter under {expected_ecosystem!r}, adapter responded with {self.ecosystem!r}") if the two disagree (`src/codecompass/adapters/external_process.py:53-98`, directly re-confirmed by this record's own derivation). `HaskellAdapter._analyze` -- the one production call site -- passes `expected_ecosystem=self.config.ecosystem`, a real `core.Ecosystem` value fixed via `vendor.toml` before the adapter process is even spawned (`src/codecompass/adapters/haskell.py:184-195`), and `grep` confirms it is the only construction/call site of `ExternalAdapterProcess`/`initialize` anywhere in `src/codecompass/`. The wire field is therefore no longer write-only telemetry from CodeCompass's own perspective: something in the current implementation now does detect and surface an external adapter reporting an `ecosystem` string that disagrees with the `Ecosystem` value CodeCompass configured it under, contradicting CL-ADPT-009's own "nothing currently prevents ... no observed behaviour would currently detect" language precisely. Narrower point preserved unchanged from CL-ADPT-009: adapter *dispatch* (`get_adapter`) is still driven entirely by `VendorConfig.ecosystem`, never by the wire-reported value -- this fix adds a validation check at `initialize` time, not a new dispatch path. The two values remain independently-typed things (one free text, one closed enum); they are now compared for equality at one point, not unified into one type. This Claim supersedes CL-ADPT-009 for exactly this reason: the protocol-specification half of CL-ADPT-009's statement is still accurate, but its implementation-behaviour half was overtaken by a real `src/` change the published concept pages (`capability.md`, `protocol.md`, `ecosystem.md`, `open-questions.md` item 10) already correctly reflect -- this record closes the one place that fix was never mechanically carried through: the Claim record itself.

Supporting evidence: [EV-ADPT-010, EV-ADPT-012]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-CTXT-006 semantic-sha256:3365005b33ffc344e2183e07e5c2bff143ad9c8ba18e26dc023d9c2cfc0fdeed projection-sha256:4739331675d03e1d7a649a88ac5eeb1fa9076eccc1ca27725ddd4064222d8569 -->
### CL-CTXT-006

relationship-edge.md's Definition ("a relationship, precisely, is a real, typed row in one of context-graph.db's six edge tables ... wiped and reinserted by rebuild_deterministic on every whole-project sync") is incomplete, not merely unclear, against Phase 76's git-topology schema when judged purely against its own stated test: `git_worktrees.repository_id` and `git_submodules.parent_repository_id` are real, typed, FK'd rows that `rebuild_deterministic` also wipes and reinserts unconditionally on every sync (EV-CTXT-019) -- satisfying the Definition's literal lifecycle criterion exactly as fully as any of the named six. However, a real, substantive, previously-unstated architectural line does exist and does distinguish these two columns from the six named edge tables, rather than this being an arbitrary omission (EV-CTXT-020): every one of the six edge tables has at least one endpoint among the four content entities a vendor/doc/symbol query traverses (vendors, symbols, source_files, doc_artifacts); git_worktrees/git_submodules connect only to git_repositories, a self-contained Phase-76 entity that no content table ever references and that never references any content table. decisions/0063, the ADR introducing these tables, explicitly frames them as "mechanical facts only -- no semantic relationship edges," deliberately rejected modelling them via vendors/doc_artifacts, and gave them a wholly separate CLI query surface (`codecompass query topology`) with no shared code path or traversal with `codecompass query relations` (the six edge tables' own query surface). This Claim resolves the disambiguation question named by the Phase 80 freshness review (relationship-edge.md's own "precisely six" count) in favour of interpretation (b): there is a real, principled reason git-topology rows are a structurally different thing from the six content-graph edge tables (self-describing the project's own repository structure vs. connecting two first-class content entities a vendor/doc/symbol query would traverse), not merely an arbitrary gap -- but this distinction has never been stated anywhere in the corpus before this record, and relationship-edge.md's own silence on git-topology rows is therefore a real, if narrow, content gap, not a false statement (the "six" count is accurate once this previously-implicit line is made explicit, not before). This Claim does not decide whether a future graph capability might ever need to treat these as the same family -- only describes the current, evidenced state of the implementation and its own governing ADR.

Supporting evidence: [EV-CTXT-019, EV-CTXT-020]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->


## Candidate additions

Add new domain knowledge, edge cases, invariants, or open questions below, strictly between the two marker comments. Content outside this region — including this paragraph — is never read as knowledge; it is just narrative framing CodeCompass leaves untouched.

Plain prose becomes an unclassified Claim (a factual hypothesis, not yet evidence-backed) — this is the default and the common case. Merely mentioning a Decision id anywhere in your prose does NOT make your addition a Requirement, and merely using the word "should" or "must" does NOT make it declared intent — both need the explicit structured forms below.

To propose a REQUIREMENT, start the block with a line reading exactly "Type: Requirement", followed by:
  Decision: <id of an existing, already-approved Decision>
  Statement: <the requirement itself, one line>
  Example: <a Given/When/Then acceptance example>
CodeCompass never invents a Decision on your behalf — a missing or not-yet-approved Decision id, or an Example that doesn't structurally read as Given/When/Then, falls back to an ordinary Claim using your Statement text, never a fabricated placeholder example.

To declare project INTENT (a proposed policy, not yet a fact about the system), start the block with a line reading exactly "Type: Intent", followed by the intended behaviour as plain prose on the lines after it.

Anything else — plain prose with no Type: header — stays an unclassified Claim until a reviewer looks at it.

<!-- codecompass-candidates:start --><!-- codecompass-candidates:end -->
