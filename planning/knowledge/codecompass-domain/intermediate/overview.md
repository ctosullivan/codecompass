# codecompass-domain — overview

<!-- codecompass-knowledge: CL-ADPT-001 semantic-sha256:cf7790b7a636ed9f1c2d951734c886e8d2481da9e59af4c91c593e4080084775 projection-sha256:26cd9ca855f342b346e50038561cbd8c220b3768eee03ed8e081a435fd842e40 -->
### CL-ADPT-001

An "adapter" in CodeCompass's own ecosystem-integration sense is a concrete subclass of EcosystemAdapter (src/codecompass/adapters/base.py), constructed per (VendorConfig, project_root), implementing five abstract methods (installed_version, source_location, readme_and_api_surface, repository_url, dependency_tree) plus one concrete, overridable method (symbols(), Phase 62). Exactly one adapter class exists per Ecosystem enum member, selected by get_adapter's closed dispatch table -- never chosen by any other mechanism (naming convention, plugin discovery, config string).

Supporting evidence: [EV-ADPT-001, EV-ADPT-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-002 semantic-sha256:ec0c8620c30f3c9adedbc406c5e312efe008539c7439762b72120c54124fbb56 projection-sha256:228b950a8190c8fca43d733a022eb0c4586afd7398e01c1c691393182531ad04 -->
### CL-ADPT-002

Two EcosystemAdapter implementation strategies coexist by deliberate design, not as one superseding the other: (1) in-process (npm, Python, Cargo) -- an importable Python class inside src/codecompass/ shelling out to native ecosystem tooling; (2) external-process (Haskell, the reference implementation) -- a thin in-process dispatcher for simple manifest reads, delegating all real ecosystem-specific logic to an independent OS process speaking a small JSON-Lines protocol, motivated by ecosystems (e.g. a hypothetical proprietary COBOL adapter) whose implementation cannot or should not be in-process, GPL-covered Python code. decisions/0002 (the first strategy) is explicitly "not superseded" by decisions/0057 (the second) -- in-process remains the default, lower-overhead strategy.

Supporting evidence: [EV-ADPT-002, EV-ADPT-003, EV-ADPT-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-003 semantic-sha256:91b32b490ed513ee53db2eb896adb22199c182b15dae40a44d689b5d5fe64938 projection-sha256:cf46f9c335941320495232ca4fc4bbfa7c21a7e4eac620cb596547077007aae1 -->
### CL-ADPT-003

"protocol" (in this cluster's specific referent) names the external adapter wire protocol defined by decisions/0057 and canonicalized by protocol/codecompass-adaptor-protocol/SCHEMA.md: JSON-Lines framing, one outstanding request at a time (v1), a closed 3-method set (initialize, analyze_project, shutdown), a closed 4-value capability set gating what analyze_project may return, and a closed 4-value error-code set. It is deliberately not gRPC, not a network service, not a plugin registry, and not a versioned SDK -- explicitly named as premature by decisions/0057 itself. `protocol_version` (an integer negotiated at initialize) is a distinct concept from the protocol repository's own semver release version -- the former is the wire contract identifier, the latter can advance independently (documentation/example/conformance-test changes) without the wire contract itself changing.

Supporting evidence: [EV-ADPT-003, EV-ADPT-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-004 semantic-sha256:2349624b91e90dfab7c01b9878017500e119684970cf27f0bdaf646161675a21 projection-sha256:79ef62c02eb6eaf678a35b607c12de8ba9d9d067d3b0e903476bbde694df831a -->
### CL-ADPT-004

"connector" is not a real, distinct CodeCompass concept -- it names nothing in src/, docs/, architecture/, ai-docs/, any decisions/*.md ADR body, or tests/. Its only in-repository occurrences are (a) this Phase 63D research effort's own planning-document lists of terms *to investigate* (never used or defined as a term there either), and (b) one unrelated occurrence inside a vendored third-party SDK's own generated reference digest, describing an Anthropic-product field ("tunnel connector token") that has no relationship to CodeCompass's adapter machinery. If a reader encounters "connector" in a CodeCompass context, the most likely source of confusion is either (i) the broader Claude/MCP ecosystem's own use of "connector" for a hosted integration (a concept this project has never implemented -- MCP work is deferred, Phase 25, not started, and no MCP-related code exists in src/codecompass/ at this revision), or (ii) CodeCompass's own "adapter" (EcosystemAdapter or the external-process protocol client), which is the actual, evidenced mechanism nearest in meaning.

Supporting evidence: [EV-ADPT-004]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-005 semantic-sha256:dfa8664717c3d1fdd20668d45e8e7e8f035cec9a5ac1ab2ec12c2dda09af580e projection-sha256:2905fb23849c6d5cf4055e9888d349b82c018f8de71a36db7f99c36923027b95 -->
### CL-ADPT-005

Ecosystem, vendor, and adapter are three related but distinct concepts. Ecosystem is a fixed, closed 4-member enum (npm, python, cargo, haskell) -- a category, not a thing you configure per project. A vendor is one tracked dependency: a VendorConfig(name, ecosystem) entry from vendor.toml, belonging to exactly one Ecosystem (e.g. VendorConfig(name="hledger-lib", ecosystem=Ecosystem.HASKELL)). An adapter is the EcosystemAdapter subclass implementing ecosystem-specific logic for one Ecosystem value (e.g. HaskellAdapter for Ecosystem.HASKELL) -- constructed fresh per (VendorConfig, project_root) via get_adapter, not itself configured or tracked as project state the way a vendor is. Concretely: many vendors can share one Ecosystem (multiple Haskell vendors all use Ecosystem.HASKELL) and therefore share one adapter *class*, but each vendor still gets its own adapter *instance*, scoped to that vendor's own config and project_root. Edge case: the "one vendor, one adapter instance" relationship is not a structural filesystem guarantee -- HaskellAdapter's own monorepo resolution (_resolve_package_dir) shows a single project_root can host multiple vendors' worth of source (e.g. hledger-lib/hledger/hledger-ui all inside one `hledger` checkout), and the adapter instance itself is responsible for narrowing project_root down to the one subdirectory matching its own vendor's name before any other method call is meaningful.

Supporting evidence: [EV-ADPT-005, EV-ADPT-002]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-006 semantic-sha256:25f24ebe1fb7ffd844d2f9f7b626b77af9b1b6b733fb7f7ff044b26c06028014 projection-sha256:b312a848e12e30b9dff5af0d5068f407e81c3b08df68a3bb098e7124f8d7b2f4 -->
### CL-ADPT-006

"capability" and "feature" are not interchangeable in this project. capability is the external adapter wire protocol's own specific, closed term: one of exactly four strings (dependencies, symbols, observations, diagnostics), declared by an adapter once at initialize, gating which of analyze_project's result sections that adapter may legitimately return. "feature" has no such role anywhere in this project -- it is ordinary, unscoped English used throughout ADRs/plans/roadmap prose for "a thing CodeCompass does or delivers," with no enumeration, no handshake, and no schema constraint attached to it. Casually calling something a CodeCompass "feature" (e.g. "the symbols() feature") is not wrong English, but it is never the same claim as declaring a protocol "capability" -- only the external adapter protocol has capabilities in this closed-set sense.

Supporting evidence: [EV-ADPT-009]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-007 semantic-sha256:70cc3f2061b8446eec891b378625ae1a95f7147839cd2ffb63947a1c69c399a5 projection-sha256:75f80db530658a85a1c50fbb503276c0d37fda1ef7f103a0a38bc58c4cd77c75 -->
### CL-ADPT-007

"adapter" is itself a genuinely fuzzy boundary inside this project's own documentation, not just relative to neighbouring terms: this project's own architecture doc names two distinct senses sharing the bare word "adapter" -- the ecosystem adapter (EcosystemAdapter, a real ABC with real subclasses in src/codecompass/adapters/) and the "host-output adapter" (skill.py/commands.py/index.py, a purely expository classification label with no corresponding class, interface, or shared base anywhere in source). A reader who encounters the bare word "adapter" in this project without a qualifying phrase cannot tell which sense is meant from the word alone; architecture/overview.md itself already flags this explicitly, which is independent confirmation this is a known, real ambiguity in this project's own vocabulary, not one this research invented.

Supporting evidence: [EV-ADPT-007]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-008 semantic-sha256:c6c34c3fe9fbdde405054562d73d7544e41eb79a08cda9c398fa15d3ac7b64cb projection-sha256:59382ed84872b8e812da859299389b47a24a2724322b08f5e1e7ada2cbf207ae -->
### CL-ADPT-008

There is an unresolved naming contradiction between decisions/0058's own stated repository names for the two new external-adapter repositories ("codecompass-adapter-protocol", "codecompass-adapter-haskell" -- adapter spelling, used consistently throughout that ADR's Decision/Consequences sections) and the actually implemented, checked-out artifacts (.gitmodules' own submodule names/remote URLs, the real checked-out directory path, and every in-repository code comment naming these repositories -- all consistently "codecompass-adaptor-protocol"/"codecompass-adaptor-haskell", adaptor spelling). This is a real documentation-vs-implementation mismatch on a simple factual question (what is this repository actually called), not a matter of interpretation -- I could not determine from evidence available inside this repository alone which spelling is the intended/canonical one going forward, or whether decisions/0058 itself needs a correcting amendment or a new ADR entry recording the rename. Left open rather than guessed at.

Supporting evidence: [EV-ADPT-008]
Contradicting evidence: [EV-ADPT-008]
Status: status=superseded
Provenance: HISTORICAL
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-009 semantic-sha256:dfd9139cc26a18385aa374aa70ad5c79597705f6bffe8cc83afc380b521789ca projection-sha256:30f5b6be5881ba6b8949df2d42079232362ee0fb9df2d652c1eedd523d5a2a95 -->
### CL-ADPT-009

The external adapter protocol's own `ecosystem` field (returned in an adapter's initialize response) is deliberately unconstrained free text at the protocol-specification level (SCHEMA.md states outright "this protocol does not define a closed ecosystem enum"), in contrast to CodeCompass's own internal Ecosystem enum (a closed 4-member set). In the current implementation this is not merely a specification looseness but an observed, currently-inert gap: the wire-reported value is stored on ExternalAdapterProcess.ecosystem after initialize() but is never subsequently read, compared against core.Ecosystem, or used for any dispatch or validation decision anywhere in src/codecompass/ -- dispatch is driven entirely by VendorConfig.ecosystem, fixed on the CodeCompass side before the adapter process is even spawned. This is a genuine edge case worth naming on the ecosystem/protocol concept pages: nothing currently prevents an external adapter from reporting an `ecosystem` string that disagrees with the Ecosystem value CodeCompass configured it under, and no observed behaviour would currently detect or surface that disagreement.

Supporting evidence: [EV-ADPT-010]
Status: status=superseded
Provenance: HISTORICAL
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-010 semantic-sha256:6b97abddf0bb2069356b6b608e8b430598173e7842a1c4063c80dd099f7b266c projection-sha256:3fc2856a4fa623f6ffddd5ccc2673e0493c9673c0dacde46cef5393c399f21b4 -->
### CL-ADPT-010

decisions/0058's own "adapter"-spelled repository names ("codecompass-adapter-protocol", "codecompass-adapter-haskell") are a pre-implementation drafting typo, not a live, unresolved naming question. The ADR's own commit (886dc6ef..., 2026-09-19 09:29:33 +0800) predates, by five hours the same day, the commit that actually created and checked out the two real external repositories (41bae257..., 2026-09-19 14:29:49 +0800) -- so the "adapter" spelling was written aspirationally before either repository existed. "codecompass-adaptor-protocol" and "codecompass-adaptor-haskell" (the "adaptor" spelling) are the real, live, public GitHub repositories this project actually depends on -- confirmed independently reachable with real commit history and a real v0.1.0 tag each -- and every downstream artifact (.gitmodules, the checked-out submodule paths, every module docstring in base.py/external_process.py/haskell.py) has used "adaptor" consistently, unchanged, since the single commit that introduced them. This claim resolves and supersedes CL-ADPT-008's own "I could not determine which spelling is canonical" conclusion with new evidence CL-ADPT-008 did not have. This claim does not decide whether decisions/0058's own text should receive a corrective ADR entry -- that editorial choice belongs to whoever owns decisions/*.md, not to this record.

Supporting evidence: [EV-ADPT-008, EV-SKEP-001]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-011 semantic-sha256:b8bd54e0238417bf8ee7b63c1feaaa0157f7cc9c6abb6df88cbfa52cdef16cb9 projection-sha256:2438842edccccfec88278da4647d640d0b3c8eea5cf2281e497558288aff3a7b -->
### CL-ADPT-011

The external adapter protocol's own `ecosystem` field (returned in an adapter's initialize response) remains deliberately unconstrained free text at the protocol-specification level (SCHEMA.md still states outright "this protocol does not define a closed ecosystem enum"), in contrast to CodeCompass's own internal Ecosystem enum (a closed 4-member set) -- that part of CL-ADPT-009's statement is unaffected and does not need re-deriving. But CL-ADPT-009's further claim that this was, in the current implementation, "an observed, currently-inert gap" with "no observed behaviour" to detect a mismatch is false as of Phase 74 (`L-032`, landed `050e366993a8831beda9f3a729bbdbaae22cc029`): `ExternalAdapterProcess.initialize` now takes a required keyword-only `expected_ecosystem: str` argument and, immediately after setting `self.ecosystem` from the wire response, raises `AdapterError` ("external adapter ecosystem mismatch: CodeCompass configured this adapter under {expected_ecosystem!r}, adapter responded with {self.ecosystem!r}") if the two disagree (`src/codecompass/adapters/external_process.py:53-98`, directly re-confirmed by this record's own derivation). `HaskellAdapter._analyze` -- the one production call site -- passes `expected_ecosystem=self.config.ecosystem`, a real `core.Ecosystem` value fixed via `vendor.toml` before the adapter process is even spawned (`src/codecompass/adapters/haskell.py:184-195`), and `grep` confirms it is the only construction/call site of `ExternalAdapterProcess`/`initialize` anywhere in `src/codecompass/`. The wire field is therefore no longer write-only telemetry from CodeCompass's own perspective: something in the current implementation now does detect and surface an external adapter reporting an `ecosystem` string that disagrees with the `Ecosystem` value CodeCompass configured it under, contradicting CL-ADPT-009's own "nothing currently prevents ... no observed behaviour would currently detect" language precisely. Narrower point preserved unchanged from CL-ADPT-009: adapter *dispatch* (`get_adapter`) is still driven entirely by `VendorConfig.ecosystem`, never by the wire-reported value -- this fix adds a validation check at `initialize` time, not a new dispatch path. The two values remain independently-typed things (one free text, one closed enum); they are now compared for equality at one point, not unified into one type. This Claim supersedes CL-ADPT-009 for exactly this reason: the protocol-specification half of CL-ADPT-009's statement is still accurate, but its implementation-behaviour half was overtaken by a real `src/` change the published concept pages (`capability.md`, `protocol.md`, `ecosystem.md`, `open-questions.md` item 10) already correctly reflect -- this record closes the one place that fix was never mechanically carried through: the Claim record itself.

Supporting evidence: [EV-ADPT-010, EV-ADPT-012]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-CTXT-001 semantic-sha256:75c33ffea722df5c2d454ba8f814b5339bcbfccb6865f908126895b35c0b612c projection-sha256:7743299f692378eb1528083cf57f22927d79c06221a469a87cc127a9ffe42f77 -->
### CL-CTXT-001

"Context" has no single canonical meaning in this project -- it names at least five genuinely distinct, related-but-not-interchangeable things, none of which is reducible to another: (1) context-graph.db, the deterministic SQLite persistence layer of vendors/symbols/edges; (2) "the context CodeCompass supplies to an agent" generally -- digests, graph query output, generated Skills, /discovery, chat answers, i.e. everything a consuming agent might read, an informal umbrella rather than one artifact; (3) a "context packet" (context-packet.md), Phase 54c's own specific, curated, feature-scoped Implement-stage artifact; (4) context-health.md / context-use-log.md and the context-quality-evaluation.md report -- three distinct instruments for assessing or logging how well (2) is working, none of which is (2) itself; (5) "context" as a plain English word inside unrelated agent names (roadmap-context-curator) where it means planning-doc state, not runtime context at all. The project's own closest-to-canonical top-level statement (ai-docs/ README.md) already treats "context graph" and "digest" as two separate, coordinate outputs rather than collapsing them into one "context" concept, which is consistent with, not contradicted by, this five-way split.

Supporting evidence: [EV-CTXT-001, EV-CTXT-003, EV-CTXT-004, EV-CTXT-005, EV-CTXT-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-CTXT-002 semantic-sha256:ebe338b18509e54c3c2586f4fd8a4c77a63bacfb36fd04f6245447495b59981b projection-sha256:05bb59d03458c42f05e1d20ff35c8d7d1a63d6ea28f2f3bf848079be070c9583 -->
### CL-CTXT-002

A "context packet" (context-packet.md) is a narrowly-defined, feature-scoped, curated Markdown artifact -- produced once per feature by a knowledge-curator mode, only after that feature's design.md reaches status APPROVED, deliberately smaller than design.md, living at planning/knowledge/<feature-slug>/ context-packet.md, and citing every substantive assertion back to a CL-/EV-/DE-/REQ- id. It is mechanically and purposively distinct from a "digest" (VendorDigest, see CL-CTXT-005): a digest is generated unconditionally on every whole-project sync, for every tracked vendor, by deterministic rendering plus a read-only lookup of existing AI enrichment, and lives under vendor/<name>/; a context packet is generated once, by a curation step gated on human/lead APPROVED-status review, and lives under planning/knowledge/. No context-packet.md is ever produced automatically the way a digest is, and no digest is ever gated on a design.md's own APPROVED status.

Supporting evidence: [EV-CTXT-001, EV-CTXT-002, EV-CTXT-009, EV-CTXT-010, EV-CTXT-013, EV-CTXT-014]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-CTXT-003 semantic-sha256:13ef6a5758a951392caea2934ad27b31fd042b657643ba7a63eeb9133d0d3ff9 projection-sha256:c12e12c0bda5981a7d1a87071ffa9a301441425a3852e9b11d82e0804945445e -->
### CL-CTXT-003

"Relationship" and "edge" are used precisely in context-graph.db's own schema (a real, typed row in one of six edge tables -- uses_edges, documents_edges, skill_mentions_edges, routes_via_edges, depends_on_edges, doc_relations_edges -- each deterministically detected and rebuilt on every whole-project sync) but are deliberately NOT used for two neighbouring things this project keeps structurally separate: (a) an agent-suggested relationship (planning/context-gaps/) is explicitly never written into context-graph.db at all (decisions/0051) -- it is an "observation with provenance," promoted to a real edge (or a new graph capability) only through a separately-gated ADR process, never silently; (b) an enrichment record commenting on an already-real relationship (doc_relation_enrichment, describing a doc_relations_edges row) is not itself an edge and carries no foreign key to doc_artifacts at all, by deliberate design (decisions/0038), proven by a dedicated test. A "relationship" in casual project language can mean any of these three tiers (mechanically-proven edge; agent-suggested candidate; AI commentary about an edge), and only the first is ever a context-graph.db row.

Supporting evidence: [EV-CTXT-003, EV-CTXT-004, EV-CTXT-011, EV-CTXT-012]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-CTXT-004 semantic-sha256:e00c7cc8050d72dee8e924ca769297f8dae239eb33b6cfa789b1993828fc08ea projection-sha256:7b1ea757334cac04c76695ac230efb4a4eb5b0f627f62982a8a6d584ab64fa8a -->
### CL-CTXT-004

"Reference" is used in at least three genuinely distinct senses in this project, none of which is reducible to another, and never cross-linked or disambiguated in one place before this phase: (a) a doc_artifacts.origin='pinned_reference' row -- a graph-level provenance CHECK-enum value (Phase 54c/CG-005/decisions-adjacent, added via the same generic migration mechanism as 'project'/ 'vendor_upstream') classifying externally-sourced, revision-pinned material a tool materialized into the project tree; (b) a "reference project" (Ledgerkit, Technical Clipper) -- a whole external, real, registered codebase used as ground truth for context-quality evaluation, per a repeatable registration/task-pool protocol; (c) a citation/pointer field (source_ref/doc_ref/test_ref on an Evidence record, or the "references block" required on every docs/domain concept page) resolving to a real file:line location so a claim can be walked back to primary evidence. All three are real, currently populated with real content, and a newcomer reading "reference" cold in this repository has no single place that names all three side-by-side before this concept page.

Supporting evidence: [EV-CTXT-003, EV-CTXT-007, EV-CTXT-008]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-CTXT-005 semantic-sha256:234bebf28720c2b1dc7cd3c116a5472d0d2dfd904f85145a85e359775fdded2c projection-sha256:5fbc0a132ab6cc4c969c7573c7d7ec8653993a566f05b5c7e2af242073f716f7 -->
### CL-CTXT-005

"Digest" is a real, named code concept (VendorDigest, src/codecompass/core.py) -- a per-vendor aggregate combining deterministic, always-free output (file tree, dependency tree, API surface) with a read-only lookup of that vendor's existing AI enrichment (technical description, conversational overview, action pointer) -- rendered by sync_vendor into DEPTREE.md/deptree.json, FILETREE.md/filetree.json, OVERVIEW.md (conditionally), and CLAUDE.md under vendor/<name>/, unconditionally on every whole-project sync for every tracked vendor. This is confirmed as real, currently-produced output (not only a design description) by a real generated file on disk in this exact repository (vendor/typer/CLAUDE.md) matching the described rendering section-by-section. The word "digest" is, however, used informally in the project's own prose in three overlapping ways that are never explicitly distinguished in one place: the VendorDigest object itself, the full persisted per-vendor file set collectively, and specifically a vendor's own CLAUDE.md text ("digest text"). None of these three informal usages contradicts another -- they are nested, not competing -- but the looseness is real and worth naming rather than silently smoothing over.

Supporting evidence: [EV-CTXT-006, EV-CTXT-009, EV-CTXT-010, EV-CTXT-013, EV-CTXT-014]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-CTXT-006 semantic-sha256:abd80c1e7f63603073316e2492ae491ea81e47f9da913ad63af0487fea90502e projection-sha256:4739331675d03e1d7a649a88ac5eeb1fa9076eccc1ca27725ddd4064222d8569 -->
### CL-CTXT-006

relationship-edge.md's Definition ("a relationship, precisely, is a real, typed row in one of context-graph.db's six edge tables ... wiped and reinserted by rebuild_deterministic on every whole-project sync") is incomplete, not merely unclear, against Phase 76's git-topology schema when judged purely against its own stated test: `git_worktrees.repository_id` and `git_submodules.parent_repository_id` are real, typed, FK'd rows that `rebuild_deterministic` also wipes and reinserts unconditionally on every sync (EV-CTXT-019) -- satisfying the Definition's literal lifecycle criterion exactly as fully as any of the named six. However, a real, substantive, previously-unstated architectural line does exist and does distinguish these two columns from the six named edge tables, rather than this being an arbitrary omission (EV-CTXT-020): every one of the six edge tables has at least one endpoint among the four content entities a vendor/doc/symbol query traverses (vendors, symbols, source_files, doc_artifacts); git_worktrees/git_submodules connect only to git_repositories, a self-contained Phase-76 entity that no content table ever references and that never references any content table. decisions/0063, the ADR introducing these tables, explicitly frames them as "mechanical facts only -- no semantic relationship edges," deliberately rejected modelling them via vendors/doc_artifacts, and gave them a wholly separate CLI query surface (`codecompass query topology`) with no shared code path or traversal with `codecompass query relations` (the six edge tables' own query surface). This Claim resolves the disambiguation question named by the Phase 80 freshness review (relationship-edge.md's own "precisely six" count) in favour of interpretation (b): there is a real, principled reason git-topology rows are a structurally different thing from the six content-graph edge tables (self-describing the project's own repository structure vs. connecting two first-class content entities a vendor/doc/symbol query would traverse), not merely an arbitrary gap -- but this distinction has never been stated anywhere in the corpus before this record, and relationship-edge.md's own silence on git-topology rows is therefore a real, if narrow, content gap, not a false statement (the "six" count is accurate once this previously-implicit line is made explicit, not before). This Claim does not decide whether a future graph capability might ever need to treat these as the same family -- only describes the current, evidenced state of the implementation and its own governing ADR.

Supporting evidence: [EV-CTXT-019, EV-CTXT-020]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-001 semantic-sha256:d3481a6c13a535b77038c0d36108b3d45d1d33ae3eb64c1d264562f7b2ac1a4a projection-sha256:05d3d38ab9fda6fce731f702dba9838eca87972f377062ec5ba9fafea2cf22f7 -->
### CL-EVID-001

An "Evidence" record (EV-<feature>-NNN), in Phase 54c's own model, is a strictly NEUTRAL package of one or more Observations (or a direct source/doc/test citation) describing what was found -- it never itself asserts that it supports or contradicts anything. That relationship belongs only to whichever Claim later cites it via `supporting_evidence`/`contradicting_evidence`, and the same Evidence record may legitimately support one Claim while contradicting a different, competing Claim without being rewritten either way. This is the current, deliberately-amended intended meaning (the original pre-amendment design let Evidence itself carry a support/contradict tag; the 2026-09-18 amendment made it structurally neutral before any implementation began). "Evidence" in this specific formal sense is distinct from the loose, ordinary-English use of "evidence" elsewhere in this repository (e.g. decisions/0051's "reviewable, provenance-carrying prose observations" or context-gaps' own "evidence trail" language), which predates and is not built from this schema.

Supporting evidence: [EV-EVID-001, EV-EVID-002, EV-EVID-013]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-002 semantic-sha256:3c8fa343a15161be744e571e2d14f01089a0e02ae649dbada6b12a2dbd61edf5 projection-sha256:d1f1b65bd33977f95ef64778411c3fc183dc90578710637afdb8d39c6154d8a5 -->
### CL-EVID-002

An "Observation" record (OBS-<feature>-NNN), in Phase 54c's own model, is a single, dated, reproducible act of looking -- running a command, reading a specific file, fetching a specific URL -- never itself a claim about behaviour; its own `status` field is always `recorded` (it is never itself promoted or contradicted; only the Evidence/Claims built on it can be). A user or reviewer who runs an example themselves and records the result produces the identical record shape, differing only in the `performed_by` field's value, never a different record kind and never routed through a Decision instead. This formal, schema'd sense of "Observation" is genuinely different from three other things in this repository that could be mistaken for it: (1) planning/context-observations/inbox.md entries, which reuse the literal id-prefix "OBS-" for an unrelated record shape (logging experience with an already-existing graph edge, not a primary-research act of looking); (2) planning/context-gaps/ entries, which record a believed-missing relationship, not an act of looking; (3) AI-authored graph enrichment, which is interpretive content an agent produces about an already-proven fact, not a record of having looked at something.

Supporting evidence: [EV-EVID-001, EV-EVID-009, EV-EVID-010, EV-EVID-014]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-003 semantic-sha256:d84d748566f8f592e429064e4478a5326c0625c1c1558c424a5ac23210e472e1 projection-sha256:276c01b607f310745c1af08798ba19e4ca512c88dd65b6f585c6f0472131efb8 -->
### CL-EVID-003

A "Claim" record (CL-<feature>-NNN), in Phase 54c's own model, is an agent's interpretation built from one or more Evidence records -- the ONLY place a support/contradict relationship is recorded (never on Evidence itself, CL-EVID-001). Its `status` enum (proposed|supported|contradicted|superseded|verified) is the only place "how sure are we" is recorded, with no numeric confidence score anywhere. Its `supersedes` field only ever names a prior Claim, never a Decision (structural hard rule, mechanically enforced by scripts/check_knowledge_base.py); a Claim about observed behaviour is revised only by a new Claim backed by new/reinterpreted Evidence or Derivation, never by a Decision. As a genuinely fuzzy, currently- unresolved boundary: every real Claim produced under this model to date (across all three feature directories) has `contradicting_ evidence: []` and `supersedes: null` -- the mechanism for retaining a real contradiction, or for one Claim genuinely revising a prior one, is structurally checked but has never yet been exercised with real content (EV-EVID-004), so this claim's own account of how that mechanism behaves under real disagreement is honestly untested, not merely theoretical. This formal "Claim" is also a distinct concept from the same word used as a candidate GRAPH-LEVEL entity kind in Phase 57's own Stage E design sketch (CL-EVID-009 documents that collision directly) -- both represent "an interpretation with provenance" in the abstract, but at different scopes (file-based development-process record vs. a proposed context-graph.db table about a target project's own dependencies) and neither is built from or reducible to the other.

Supporting evidence: [EV-EVID-002, EV-EVID-003, EV-EVID-004, EV-EVID-005, EV-EVID-006]
Status: status=superseded
Provenance: HISTORICAL
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-004 semantic-sha256:69ff9719a52900fe41521637d317b923957503f62033ed7b2475e94738f70acc projection-sha256:13416536a3d4d53a8fc002243340e556ae781d7119e69824d1d23c9fe8e39440 -->
### CL-EVID-004

A "Derivation" record (DE-<feature>-NNN) records the reasoning PROCESS that produced a Claim -- which files/paths were traced, in what order, and (per this role's own governing brief and the real L-024 learning it produced) what a researcher initially got wrong and how the mistake was caught -- not merely the Claim's own conclusion restated. It is deliberately a narrative field, not a formal proof object, and cites Evidence ids via `inputs`, never Observation ids directly. In every real instance found in this corpus so far, the Claim↔Derivation relationship is exactly 1:1 (one Derivation per Claim, each record naming the other back) -- the schema's own singular `derivation:`/`claim:` fields imply this, but nothing in the schema or the validator actually forbids a future Derivation from being cited as the reasoning behind more than one Claim if two Claims genuinely shared the same reasoning process; no such instance has ever occurred, so whether 1:1 is a real invariant of this model or simply an untested coincidence of small proving cases is a genuine, currently-unresolved boundary question -- an honest "none found yet" for a real N:1 or 1:N counterexample, not a confirmed rule.

Supporting evidence: [EV-EVID-002]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-005 semantic-sha256:504768b5678a2311ede48463ad9b34dad9c2851c5b1f0f3e32dd16349fd8b5b9 projection-sha256:a9158cf62fd2eb905c16f02ce75d1865b65a3b83b36298dc76924a5132be9879 -->
### CL-EVID-005

A "Decision" record (DEC-<feature>-NNN), in Phase 54c's own model, is the ONE record kind only a human/project-owner authors or explicitly ratifies -- it records CHOSEN target-project behaviour, never a revision of factually observed upstream behaviour, and its own `supersedes` field only ever names a prior Decision, never a Claim (the same structural hard rule as CL-EVID-003, enforced mechanically). A significant, currently-real edge case: EVERY Decision record produced under this model to date (DEC-DOCORIGIN-001, DEC-HSAPI-001) was authored by the lead explicitly standing in for the actual user/project-owner role, disclosed plainly in each record's own `decided_by` field and in that phase's own retro -- this model's own "only a human authors this" property has therefore never yet been tested against a real, independent, non-standing-in human decision-maker anywhere in this repository's history as of this research. This matters going forward specifically because Phase 63D itself (development-methodology.md, amended 2026-09-20) explicitly withdraws the lead's stand-in permission for genuine domain/product ambiguities from this point on: any new Decision produced under this methodology from Phase 63D onward must be either a real ruling by the actual user, or the ambiguity stays an open question rather than becoming a Decision record at all -- a stricter bar than every real Decision record on file currently meets.

Supporting evidence: [EV-EVID-003, EV-EVID-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-006 semantic-sha256:5652fcf659b97c4d8e5e20ac2adb82d3f5db016b2ccb85c446599d2a90928eb9 projection-sha256:5f3babca320bff594773d969b81030f54ad6ef2f86875f2a0428ffc5c1f1570b -->
### CL-EVID-006

A "Requirement" record (REQ-<feature>-NNN), in Phase 54c's own model, is implementation-facing and testable -- the thing a coding agent actually implements against -- always citing the Decision that authorises it (and, through it, the Claim/Evidence chain behind that Decision), with a Given/When/Then `example` field and a closed `status` enum (proposed|approved|implemented|verified). It is a narrower, more specific concept than "invariant": a Requirement is one single testable statement traceable to exactly one Decision (REQ-DOCORIGIN-001 → DEC-DOCORIGIN-001), whereas a project-wide invariant (docs/domain/invariants.md, this phase's own deliverable) is a cross-cutting rule that need not trace to any single Decision or Requirement at all -- the two concepts overlap (a Requirement's own behaviour, once implemented, often amounts to enforcing something that could also be phrased as an invariant) but are not the same record kind and are not interchangeable citations.

Supporting evidence: [EV-EVID-002, EV-EVID-012]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-007 semantic-sha256:13e31da4fbeb54a60d2f16048e944b57d1715403bac20ddb891b245cf808e01a projection-sha256:56a6c4c3786b324eefd7ec4d9d64622f0aeea0cb300f53f8a49ef960789bc04b -->
### CL-EVID-007

"Invariant" is NOT one of Phase 54c's six formal record kinds and has no dedicated schema anywhere in this repository. As used across this codebase today, it names at least three distinct artifacts with three different promotion/citation mechanisms and no requirement that they ever coincide for a given rule: (a) `planning/learnings/`'s own `invariant` classification value, meaning "a required behavioural invariant of CodeCompass's own code," whose correct promotion destination is a regression test (learning-lifecycle.md §4); (b) a narrative "things that must stay true" subsection inside a per-feature `design.md`/`context-packet.md`, which is a subset of that document's own content and never itself a separately-citable record id; (c) the project-wide `docs/domain/invariants.md` file this very phase (63D) produces, explicitly defined as cross-cutting rules "pulled up from individual concept docs where a rule isn't concept-local." All three share the ordinary-English sense of "a rule that must stay true," but a rule recorded in one is not automatically present, or even expected to be present, in either of the other two. This is a genuinely fuzzy concept boundary this research surfaces rather than resolves: whether these three senses should eventually be unified, cross-referenced, or deliberately kept separate is a real, open documentation-design question this Claim does not settle.

Supporting evidence: [EV-EVID-011, EV-EVID-012]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-008 semantic-sha256:c84a5100a1713f0d1b2c5653272bc3322ee5c6e61579f78a2033d90affb6b33b projection-sha256:66141896d8ffd2897960c85032a36d59aeecfe22a6bd593720d5df85d1461074 -->
### CL-EVID-008

"Provenance" is never a record kind of its own anywhere in this codebase -- it is a cross-cutting property, realized with a structurally different concrete shape in each of at least three mechanisms: Phase 54c's own records carry a named, method-conditional set of provenance fields (repository_revision; source_ref/doc_ref/ test_ref; performed_by/derived_by/decided_by; tool/tool_version; timestamp -- §2.3's own adopted list); the three enrichment tables carry a single `model` TEXT column each (absent entirely on symbol_enrichment); context-gaps/context-observations entries carry four narrative fields (origin, date, codecompass_revision, project). All three are "provenance" in the ordinary sense of "who/what produced this, when, from what" but there is no shared schema, base type, or record kind unifying them, and no evidence that unifying them has ever been proposed or attempted in this repository's history.

Supporting evidence: [EV-EVID-013, EV-EVID-014]
Status: status=superseded
Provenance: HISTORICAL
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-009 semantic-sha256:38faf4998df9c40eb85d3a1bed65e264c527cb41ddc919fbf1b4460f09027d49 projection-sha256:73543ba1ab66ca38ee7e353ab738da3b30116d2c8f9187e071f37453000c3d50 -->
### CL-EVID-009

A real, already-named naming collision exists, and is deliberately unresolved, between Phase 54c's file-based Evidence/Observation/ Claim/Decision records (planning/knowledge/<slug>/, CodeCompass's own development-process knowledge, the subject of this whole cluster) and Phase 57's own candidate GRAPH-LEVEL (context-graph.db) entity-kind proposal using the identical names to represent provenance about OTHER PROJECTS' technical dependencies (v1-redefinition/roadmap.md's Stage E section, conditional on GATE DD). These are genuinely different concepts sharing four words: the file-based kinds are narrative YAML records about CodeCompass's own reasoning process, written by context-researcher/documentation-agent/knowledge-curator, never queryable via `codecompass query`; the graph-level candidate kinds (not yet built, not funded, conditional on a gate that has not been decided) would be structured, queryable database rows about a target project's own dependency provenance, built by a future Stage E schema change. The roadmap itself already states the correct resolution path: Stage E's own future Domain stage must either pick genuinely distinct names or explicitly justify sharing the terms with a stated disambiguation rule -- NOT a decision this research makes, since resolving it requires GATE DD funding decisions explicitly out of Phase 63D's own scope (per that phase's plan §1's own "out of scope" list: "resolving GATE DD or Stage E's own generalisation question"). This Claim documents the collision as real, evidenced, and open -- it is this cluster's single most important open question and is carried forward to docs/domain/open-questions.md verbatim, not silently resolved by naming a preference here.

Supporting evidence: [EV-EVID-006]
Status: status=superseded
Provenance: HISTORICAL
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-010 semantic-sha256:d1c352e6c48ee4140912c4d6c5e93f606a59ea6159dae409652fe2a62f6d2c07 projection-sha256:607f0c7632666d03d4391d0c6c15ce118e8fb3208efee49ade0a179cbd259efa -->
### CL-EVID-010

This codebase has at least FIVE genuinely distinct "something was noticed/recorded" mechanisms, each at a different trust/purpose level, distinguishable by real evidence rather than by name alone: (1) Phase 54c's `kind: observation` (OBS-<feature>-NNN) -- a primary-research act of looking, feeding an Evidence/Claim, written under planning/knowledge/<slug>/, never itself authoritative; (2) `planning/context-gaps/` -- "a relationship CodeCompass's context should represent but mechanical detection doesn't/can't," prose captured only in planning/, explicitly never entering context-graph.db (decisions/0051), promoted only via the learning lifecycle to a Stage C/E gated roadmap decision; (3) `planning/context-observations/` -- "how real context experience went" with an edge that ALREADY EXISTS (EDGE_USEFUL/UNHELPFUL/ MISLEADING/STALE/REDUNDANT), the explicit inverse scope of (2) (experience with edges that exist vs. requests for edges that don't), confusingly reusing the literal "OBS-" id-prefix from (1) for an unrelated shape; (4) `planning/learnings/` -- "how we should work," a project-process lesson queue reviewed by the same `knowledge-curator` as (2)/(3) but routing to a different destination set (tests/ADRs/ docs/CLAUDE.md/skills/roadmap rows, never a detection heuristic or graph capability); (5) AI-authored graph enrichment (vendor_enrichment/symbol_enrichment/doc_relation_enrichment) -- interpretive content an AI produces ABOUT AN ALREADY-PROVEN graph fact, written through `apply_results()`, tagged only by a `model` column, explicitly "never a fact CodeCompass proves" (decisions/0054) -- the only one of the five that writes anywhere inside context-graph.db itself, and the only one with no Observation/ Evidence/Claim-style narrative chain behind it at all. None of the five is interchangeable with, or a special case of, another; each has its own destination, its own write boundary, and (for 1-4) its own queue file(s).

Supporting evidence: [EV-EVID-007, EV-EVID-008, EV-EVID-009, EV-EVID-010, EV-EVID-011]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-011 semantic-sha256:9082a79f06a13e5e185bf943e787844194378ed8d310ee6e28e3a731dc4b95fc projection-sha256:4cf996ccf6102de3fc43413e3ea5e084d8cedb2ec7b2b6b10a06d37078f234f2 -->
### CL-EVID-011

A real, already-named naming collision exists, and is deliberately unresolved, between Phase 54c's file-based Evidence/Observation/ Claim/Decision records (planning/knowledge/<slug>/, CodeCompass's own development-process knowledge, the subject of this whole cluster) and a candidate GRAPH-LEVEL (context-graph.db) entity-kind proposal using the identical names to represent provenance about OTHER PROJECTS' technical dependencies (originally sketched in v1-redefinition/ roadmap.md's old "Stage E" section, §2.4 "provenance/evidence" of planning/v1-redefinition/conditional-generalisation.md, conditional on GATE DD). These are genuinely different concepts sharing four words: the file-based kinds are narrative YAML records about CodeCompass's own reasoning process, written by context-researcher/documentation- agent/knowledge-curator, never queryable via `codecompass query`; the graph-level candidate kinds (not yet built, not funded, conditional on a gate that has not been decided) would be structured, queryable database rows about a target project's own dependency provenance. This Claim documents the collision as real, evidenced, and open -- it is this cluster's single most important open question and is carried forward to docs/domain/open-questions.md verbatim, not silently resolved by naming a preference here. This Claim supersedes CL-EVID-009 for exactly one reason, narrower than the substantive collision itself: CL-EVID-009's own statement named the future resolution vehicle as "Stage E's own future Domain stage," and `decisions/0062` (Phase 72) explicitly retires the old "Stage E" phase-group label project-wide -- post-v1 work is now organised into Priority A-F, not lettered stages (`planning/ROADMAP.md`'s "Post-v1 priorities (A-F)" section). The candidate design this collision concerns (`conditional- generalisation.md` §2.4, "provenance/evidence") is re-homed by `planning/pre-v1-disposition.md` §7's own disposition table specifically to **Priority B** -- not to an unnamed future stage, and not resolved. GATE DD itself remains exactly as open as before: `decisions/0062`'s own words are "GATE DD is not resolved by this decision." The corrected resolution path is therefore: the candidate design's own future Domain stage, whichever Priority phase eventually takes it up (currently re-homed to Priority B by `pre-v1-disposition.md` §7, per `decisions/0062`) must either pick genuinely distinct names or explicitly justify sharing the terms with a stated disambiguation rule -- still NOT a decision this research makes, since resolving it requires GATE DD funding decisions and whichever future Priority-B phase plan takes up this candidate design, exactly as far outside this research's own scope as before. Nothing about the collision's reality, evidence, or open status has changed; only the name of the future phase-group vehicle has, because that phase-group itself no longer exists under its old name.

Supporting evidence: [EV-EVID-006, EV-SKEP-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-012 semantic-sha256:9ca0495809323b346c4e3193dfe9a012e3af502b8d999898c69ca9e891b30119 projection-sha256:592827d6ef9cd78174eac27f303cb1e617c1de9a5ae2b2263620fd4f6f458c8e -->
### CL-EVID-012

A "Claim" record (CL-<feature>-NNN), in Phase 54c's own model, is an agent's interpretation built from one or more Evidence records -- the ONLY place a support/contradict relationship is recorded (never on Evidence itself, CL-EVID-001). Its `status` enum (proposed|supported|contradicted|superseded|verified) is the only place "how sure are we" is recorded, with no numeric confidence score anywhere. Its `supersedes` field only ever names a prior Claim, never a Decision (structural hard rule, mechanically enforced by scripts/check_knowledge_base.py); a Claim about observed behaviour is revised only by a new Claim backed by new/reinterpreted Evidence or Derivation, never by a Decision. As a genuinely fuzzy, currently- unresolved boundary: every real Claim produced under this model before Phase 72 had `contradicting_evidence: []`, and until this Claim (and its sibling CL-EVID-011) every real Claim also had `supersedes: null` -- CL-EVID-011/CL-EVID-012 are this model's first real exercise of the Claim-supersedes-Claim mechanism with real content (a narrow, mechanical resolution-mechanism correction, not a substantive reversal), so this claim's own account of how that mechanism behaves under a genuine contradiction (as opposed to a citation-freshness correction) remains honestly untested, not merely theoretical. This formal "Claim" is also a distinct concept from the same word used as a candidate GRAPH-LEVEL entity kind in a candidate design originally sketched in `planning/v1-redefinition/roadmap.md`'s old "Stage E" section, `conditional-generalisation.md` §2.4 (CL-EVID-011, superseding CL-EVID-009, documents that collision directly) -- both represent "an interpretation with provenance" in the abstract, but at different scopes (file-based development-process record vs. a proposed context-graph.db table about a target project's own dependencies) and neither is built from or reducible to the other. This Claim supersedes CL-EVID-003 for the same narrow reason CL-EVID-011 supersedes CL-EVID-009: CL-EVID-003's own statement named the colliding graph-level design as "Phase 57's own Stage E design sketch," and `decisions/0062` (Phase 72) retires the "Stage E" phase-group label project-wide -- the candidate design itself (`conditional-generalisation.md` §2.4) is unaffected and is now re-homed to Priority B by `planning/pre-v1-disposition.md` §7, per `decisions/0062`. Everything else in CL-EVID-003's original statement -- the Claim-schema account, the untested-mechanism disclosure, the fact of the naming collision itself -- is unchanged and re-asserted here.

Supporting evidence: [EV-EVID-002, EV-EVID-003, EV-EVID-004, EV-EVID-005, EV-EVID-006, EV-SKEP-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-013 semantic-sha256:237fff7f4077c01482957a2253a952d9c6d3c09218e170bc059db7c8500cb2b0 projection-sha256:f515ec13fc7013de84a9afbc93e7ed4b5bec783c7f1d944c3c7ea681aeaf4ec8 -->
### CL-EVID-013

"Provenance" is never a record kind of its own anywhere in this codebase -- it is a cross-cutting property, realized with a structurally different concrete shape in each of at least three mechanisms: Phase 54c's own records carry a named, method-conditional set of provenance fields (repository_revision; source_ref/doc_ref/ test_ref; performed_by/derived_by/decided_by; tool/tool_version; timestamp -- §2.3's own adopted list); the three enrichment tables each carry a single `model` TEXT column; context-gaps/context- observations entries carry four narrative fields (origin, date, codecompass_revision, project). All three are "provenance" in the ordinary sense of "who/what produced this, when, from what" but there is no shared schema, base type, or record kind unifying them, and no evidence that unifying them has ever been proposed or attempted in this repository's history. This Claim supersedes CL-EVID-008 for exactly one reason, narrower than the substantive cross-cutting-provenance conclusion itself: CL-EVID-008's own statement described `symbol_enrichment` as having its `model` column "absent entirely" -- true at the time it was written (repository_revision "working tree, 2026-09-23") but made false by Phase 74 (`L-031`, landed at `050e366993a8831beda9f3a729bbdbaae22cc029`): `_migrate_symbol_enrichment_model_column` (`src/codecompass/graph.py:515-549`) now adds a nullable `model TEXT` column via `ALTER TABLE` (never drop/recreate), and `record_symbol_enrichment` (`src/codecompass/graph.py:1583-1608`) now requires a real `model` argument for every new write, with its one production call site (`src/codecompass/enrichment.py:427`) supplying the real Anthropic model id. The three enrichment tables are therefore no longer asymmetric in *whether* they carry a producer column -- all three now do. A real, narrower asymmetry remains and is not closed by Phase 74: `vendor_enrichment.model`/`doc_relation_enrichment.model` are `TEXT NOT NULL` from their own first schema version, while `symbol_enrichment.model` is nullable, and every row written *before* this migration honestly backfills `NULL` (an accurate "producer unknown, predates this column," not a fabricated value) rather than being retroactively attributed. A pre-Phase-74 `symbol_enrichment` row therefore remains provenance-unknown in a way no sibling-table row (`NOT NULL` since inception) can be. This narrower point was not investigated further here (e.g. whether a one-time backfill heuristic is worth pursuing) and is not decided by this record either way. Nothing about the broader cross-cutting-provenance conclusion changes: it never rested on `symbol_enrichment`'s specific column count, and the three mechanisms (Phase 54c records, enrichment tables, context-gaps/context-observations) remain structurally incompatible with each other exactly as before.

Supporting evidence: [EV-EVID-013, EV-EVID-014, EV-EVID-015]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-KNOW-001 semantic-sha256:d7ce3fe1957f6d44c1e5700c6057e1f321678d0b37e9a95e064f9fa16ba12e32 projection-sha256:7418b59b8dbfcf81ff7f5a0fb5d5fcc5dc5f61678f60289e1b6452c503adffc0 -->
### CL-KNOW-001

CodeCompass provides a persistent, bidirectional intermediate knowledge layer: planning/knowledge/<slug>/ canonical records are projected into human/tool-editable Markdown under planning/knowledge/<slug>/intermediate/*.md, edits are mechanically detected (never comparing a canonical record's own hash against a rendered projection's own hash directly), a human or agent review stage is required before any canonical mutation, and `codecompass knowledge apply` is the sole, mechanically-revalidating write path -- never bypassable by an external tool's or an agent's own say-so.

Supporting evidence: [EV-KNOW-001]
Status: status=supported
Provenance: OBSERVED
<!-- /codecompass-knowledge -->


## Candidate additions

Add new domain knowledge, edge cases, invariants, or open questions below, strictly between the two marker comments. Content outside this region — including this paragraph — is never read as knowledge; it is just narrative framing CodeCompass leaves untouched.

To propose a Requirement rather than a Claim, cite an existing, already-approved Decision id explicitly (e.g. "per DEC-ARCH-003") — CodeCompass never invents a Decision on your behalf; without a cited, approved Decision, your addition becomes a Claim.

<!-- codecompass-candidates:start --><!-- codecompass-candidates:end -->
