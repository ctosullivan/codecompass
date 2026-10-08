# codecompass-domain — overview

<!-- codecompass-knowledge: CL-ADPT-001 semantic-sha256:5b103bc9208bec0684c7b171ecc6f3fa1cd73437b558e5ce117ea8a13d825f8c projection-sha256:26cd9ca855f342b346e50038561cbd8c220b3768eee03ed8e081a435fd842e40 -->
### CL-ADPT-001

An "adapter" in CodeCompass's own ecosystem-integration sense is a concrete subclass of EcosystemAdapter (src/codecompass/adapters/base.py), constructed per (VendorConfig, project_root), implementing five abstract methods (installed_version, source_location, readme_and_api_surface, repository_url, dependency_tree) plus one concrete, overridable method (symbols(), Phase 62). Exactly one adapter class exists per Ecosystem enum member, selected by get_adapter's closed dispatch table -- never chosen by any other mechanism (naming convention, plugin discovery, config string).

Supporting evidence: [EV-ADPT-001, EV-ADPT-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-003 semantic-sha256:750cdfc98126c0b8002843c485a87b42d1a471b48c7af70f797c0e9c967ae097 projection-sha256:cf46f9c335941320495232ca4fc4bbfa7c21a7e4eac620cb596547077007aae1 -->
### CL-ADPT-003

"protocol" (in this cluster's specific referent) names the external adapter wire protocol defined by decisions/0057 and canonicalized by protocol/codecompass-adaptor-protocol/SCHEMA.md: JSON-Lines framing, one outstanding request at a time (v1), a closed 3-method set (initialize, analyze_project, shutdown), a closed 4-value capability set gating what analyze_project may return, and a closed 4-value error-code set. It is deliberately not gRPC, not a network service, not a plugin registry, and not a versioned SDK -- explicitly named as premature by decisions/0057 itself. `protocol_version` (an integer negotiated at initialize) is a distinct concept from the protocol repository's own semver release version -- the former is the wire contract identifier, the latter can advance independently (documentation/example/conformance-test changes) without the wire contract itself changing.

Supporting evidence: [EV-ADPT-003, EV-ADPT-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-004 semantic-sha256:2418deed4b885d82c146fd03be6fd3dcd6ed23980a197ca7717d3410cc79778f projection-sha256:79ef62c02eb6eaf678a35b607c12de8ba9d9d067d3b0e903476bbde694df831a -->
### CL-ADPT-004

"connector" is not a real, distinct CodeCompass concept -- it names nothing in src/, docs/, architecture/, ai-docs/, any decisions/*.md ADR body, or tests/. Its only in-repository occurrences are (a) this Phase 63D research effort's own planning-document lists of terms *to investigate* (never used or defined as a term there either), and (b) one unrelated occurrence inside a vendored third-party SDK's own generated reference digest, describing an Anthropic-product field ("tunnel connector token") that has no relationship to CodeCompass's adapter machinery. If a reader encounters "connector" in a CodeCompass context, the most likely source of confusion is either (i) the broader Claude/MCP ecosystem's own use of "connector" for a hosted integration (a concept this project has never implemented -- MCP work is deferred, Phase 25, not started, and no MCP-related code exists in src/codecompass/ at this revision), or (ii) CodeCompass's own "adapter" (EcosystemAdapter or the external-process protocol client), which is the actual, evidenced mechanism nearest in meaning.

Supporting evidence: [EV-ADPT-004]
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

<!-- codecompass-knowledge: CL-ADPT-010 semantic-sha256:6b97abddf0bb2069356b6b608e8b430598173e7842a1c4063c80dd099f7b266c projection-sha256:3fc2856a4fa623f6ffddd5ccc2673e0493c9673c0dacde46cef5393c399f21b4 -->
### CL-ADPT-010

decisions/0058's own "adapter"-spelled repository names ("codecompass-adapter-protocol", "codecompass-adapter-haskell") are a pre-implementation drafting typo, not a live, unresolved naming question. The ADR's own commit (886dc6ef..., 2026-09-19 09:29:33 +0800) predates, by five hours the same day, the commit that actually created and checked out the two real external repositories (41bae257..., 2026-09-19 14:29:49 +0800) -- so the "adapter" spelling was written aspirationally before either repository existed. "codecompass-adaptor-protocol" and "codecompass-adaptor-haskell" (the "adaptor" spelling) are the real, live, public GitHub repositories this project actually depends on -- confirmed independently reachable with real commit history and a real v0.1.0 tag each -- and every downstream artifact (.gitmodules, the checked-out submodule paths, every module docstring in base.py/external_process.py/haskell.py) has used "adaptor" consistently, unchanged, since the single commit that introduced them. This claim resolves and supersedes CL-ADPT-008's own "I could not determine which spelling is canonical" conclusion with new evidence CL-ADPT-008 did not have. This claim does not decide whether decisions/0058's own text should receive a corrective ADR entry -- that editorial choice belongs to whoever owns decisions/*.md, not to this record.

Supporting evidence: [EV-ADPT-008, EV-SKEP-001]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-CTXT-001 semantic-sha256:92e9a6c41f02b6496175f2623b9f4942ddb2624e39d83edd99bda84225013d1c projection-sha256:7743299f692378eb1528083cf57f22927d79c06221a469a87cc127a9ffe42f77 -->
### CL-CTXT-001

"Context" has no single canonical meaning in this project -- it names at least five genuinely distinct, related-but-not-interchangeable things, none of which is reducible to another: (1) context-graph.db, the deterministic SQLite persistence layer of vendors/symbols/edges; (2) "the context CodeCompass supplies to an agent" generally -- digests, graph query output, generated Skills, /discovery, chat answers, i.e. everything a consuming agent might read, an informal umbrella rather than one artifact; (3) a "context packet" (context-packet.md), Phase 54c's own specific, curated, feature-scoped Implement-stage artifact; (4) context-health.md / context-use-log.md and the context-quality-evaluation.md report -- three distinct instruments for assessing or logging how well (2) is working, none of which is (2) itself; (5) "context" as a plain English word inside unrelated agent names (roadmap-context-curator) where it means planning-doc state, not runtime context at all. The project's own closest-to-canonical top-level statement (ai-docs/ README.md) already treats "context graph" and "digest" as two separate, coordinate outputs rather than collapsing them into one "context" concept, which is consistent with, not contradicted by, this five-way split.

Supporting evidence: [EV-CTXT-001, EV-CTXT-003, EV-CTXT-004, EV-CTXT-005, EV-CTXT-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-CTXT-002 semantic-sha256:237073c5b57d43a6be3e5a3dd6c4156ff503bb3a09432bbcedd40b3dc63cde3d projection-sha256:05bb59d03458c42f05e1d20ff35c8d7d1a63d6ea28f2f3bf848079be070c9583 -->
### CL-CTXT-002

A "context packet" (context-packet.md) is a narrowly-defined, feature-scoped, curated Markdown artifact -- produced once per feature by a knowledge-curator mode, only after that feature's design.md reaches status APPROVED, deliberately smaller than design.md, living at planning/knowledge/<feature-slug>/ context-packet.md, and citing every substantive assertion back to a CL-/EV-/DE-/REQ- id. It is mechanically and purposively distinct from a "digest" (VendorDigest, see CL-CTXT-005): a digest is generated unconditionally on every whole-project sync, for every tracked vendor, by deterministic rendering plus a read-only lookup of existing AI enrichment, and lives under vendor/<name>/; a context packet is generated once, by a curation step gated on human/lead APPROVED-status review, and lives under planning/knowledge/. No context-packet.md is ever produced automatically the way a digest is, and no digest is ever gated on a design.md's own APPROVED status.

Supporting evidence: [EV-CTXT-001, EV-CTXT-002, EV-CTXT-009, EV-CTXT-010, EV-CTXT-013, EV-CTXT-014]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-CTXT-003 semantic-sha256:4231ffa1218e88c7201b7cb25177c408884f0507422106e7929ba8e3a8e5a78e projection-sha256:c12e12c0bda5981a7d1a87071ffa9a301441425a3852e9b11d82e0804945445e -->
### CL-CTXT-003

"Relationship" and "edge" are used precisely in context-graph.db's own schema (a real, typed row in one of six edge tables -- uses_edges, documents_edges, skill_mentions_edges, routes_via_edges, depends_on_edges, doc_relations_edges -- each deterministically detected and rebuilt on every whole-project sync) but are deliberately NOT used for two neighbouring things this project keeps structurally separate: (a) an agent-suggested relationship (planning/context-gaps/) is explicitly never written into context-graph.db at all (decisions/0051) -- it is an "observation with provenance," promoted to a real edge (or a new graph capability) only through a separately-gated ADR process, never silently; (b) an enrichment record commenting on an already-real relationship (doc_relation_enrichment, describing a doc_relations_edges row) is not itself an edge and carries no foreign key to doc_artifacts at all, by deliberate design (decisions/0038), proven by a dedicated test. A "relationship" in casual project language can mean any of these three tiers (mechanically-proven edge; agent-suggested candidate; AI commentary about an edge), and only the first is ever a context-graph.db row.

Supporting evidence: [EV-CTXT-003, EV-CTXT-004, EV-CTXT-011, EV-CTXT-012]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-CTXT-004 semantic-sha256:da906b87338d296b7ffb415b172faf47bda7801b5ebc4b6d02308e5a1f2b8360 projection-sha256:7b1ea757334cac04c76695ac230efb4a4eb5b0f627f62982a8a6d584ab64fa8a -->
### CL-CTXT-004

"Reference" is used in at least three genuinely distinct senses in this project, none of which is reducible to another, and never cross-linked or disambiguated in one place before this phase: (a) a doc_artifacts.origin='pinned_reference' row -- a graph-level provenance CHECK-enum value (Phase 54c/CG-005/decisions-adjacent, added via the same generic migration mechanism as 'project'/ 'vendor_upstream') classifying externally-sourced, revision-pinned material a tool materialized into the project tree; (b) a "reference project" (Ledgerkit, Technical Clipper) -- a whole external, real, registered codebase used as ground truth for context-quality evaluation, per a repeatable registration/task-pool protocol; (c) a citation/pointer field (source_ref/doc_ref/test_ref on an Evidence record, or the "references block" required on every docs/domain concept page) resolving to a real file:line location so a claim can be walked back to primary evidence. All three are real, currently populated with real content, and a newcomer reading "reference" cold in this repository has no single place that names all three side-by-side before this concept page.

Supporting evidence: [EV-CTXT-003, EV-CTXT-007, EV-CTXT-008]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-CTXT-005 semantic-sha256:e09d9fe6ed46148b4d01ac5342c377f043bfc5b842f03802b3975dd47c3280b3 projection-sha256:5fbc0a132ab6cc4c969c7573c7d7ec8653993a566f05b5c7e2af242073f716f7 -->
### CL-CTXT-005

"Digest" is a real, named code concept (VendorDigest, src/codecompass/core.py) -- a per-vendor aggregate combining deterministic, always-free output (file tree, dependency tree, API surface) with a read-only lookup of that vendor's existing AI enrichment (technical description, conversational overview, action pointer) -- rendered by sync_vendor into DEPTREE.md/deptree.json, FILETREE.md/filetree.json, OVERVIEW.md (conditionally), and CLAUDE.md under vendor/<name>/, unconditionally on every whole-project sync for every tracked vendor. This is confirmed as real, currently-produced output (not only a design description) by a real generated file on disk in this exact repository (vendor/typer/CLAUDE.md) matching the described rendering section-by-section. The word "digest" is, however, used informally in the project's own prose in three overlapping ways that are never explicitly distinguished in one place: the VendorDigest object itself, the full persisted per-vendor file set collectively, and specifically a vendor's own CLAUDE.md text ("digest text"). None of these three informal usages contradicts another -- they are nested, not competing -- but the looseness is real and worth naming rather than silently smoothing over.

Supporting evidence: [EV-CTXT-006, EV-CTXT-009, EV-CTXT-010, EV-CTXT-013, EV-CTXT-014]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-001 semantic-sha256:1e1afa5c5424a08931e92c9992406d6779c0b07c84ce022dc7a9b8f90fcdcd51 projection-sha256:05d3d38ab9fda6fce731f702dba9838eca87972f377062ec5ba9fafea2cf22f7 -->
### CL-EVID-001

An "Evidence" record (EV-<feature>-NNN), in Phase 54c's own model, is a strictly NEUTRAL package of one or more Observations (or a direct source/doc/test citation) describing what was found -- it never itself asserts that it supports or contradicts anything. That relationship belongs only to whichever Claim later cites it via `supporting_evidence`/`contradicting_evidence`, and the same Evidence record may legitimately support one Claim while contradicting a different, competing Claim without being rewritten either way. This is the current, deliberately-amended intended meaning (the original pre-amendment design let Evidence itself carry a support/contradict tag; the 2026-09-18 amendment made it structurally neutral before any implementation began). "Evidence" in this specific formal sense is distinct from the loose, ordinary-English use of "evidence" elsewhere in this repository (e.g. decisions/0051's "reviewable, provenance-carrying prose observations" or context-gaps' own "evidence trail" language), which predates and is not built from this schema.

Supporting evidence: [EV-EVID-001, EV-EVID-002, EV-EVID-013]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-002 semantic-sha256:5f1efa44f199fdeae8ee152339e82b850f19cc4f4500d14467cff032d88fedfc projection-sha256:d1f1b65bd33977f95ef64778411c3fc183dc90578710637afdb8d39c6154d8a5 -->
### CL-EVID-002

An "Observation" record (OBS-<feature>-NNN), in Phase 54c's own model, is a single, dated, reproducible act of looking -- running a command, reading a specific file, fetching a specific URL -- never itself a claim about behaviour; its own `status` field is always `recorded` (it is never itself promoted or contradicted; only the Evidence/Claims built on it can be). A user or reviewer who runs an example themselves and records the result produces the identical record shape, differing only in the `performed_by` field's value, never a different record kind and never routed through a Decision instead. This formal, schema'd sense of "Observation" is genuinely different from three other things in this repository that could be mistaken for it: (1) planning/context-observations/inbox.md entries, which reuse the literal id-prefix "OBS-" for an unrelated record shape (logging experience with an already-existing graph edge, not a primary-research act of looking); (2) planning/context-gaps/ entries, which record a believed-missing relationship, not an act of looking; (3) AI-authored graph enrichment, which is interpretive content an agent produces about an already-proven fact, not a record of having looked at something.

Supporting evidence: [EV-EVID-001, EV-EVID-009, EV-EVID-010, EV-EVID-014]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-003 semantic-sha256:6d3c6d3e2c1d9c0c8224e4dc46b04b315eea56e26dcf61250a05171437847c1d projection-sha256:276c01b607f310745c1af08798ba19e4ca512c88dd65b6f585c6f0472131efb8 -->
### CL-EVID-003

A "Claim" record (CL-<feature>-NNN), in Phase 54c's own model, is an agent's interpretation built from one or more Evidence records -- the ONLY place a support/contradict relationship is recorded (never on Evidence itself, CL-EVID-001). Its `status` enum (proposed|supported|contradicted|superseded|verified) is the only place "how sure are we" is recorded, with no numeric confidence score anywhere. Its `supersedes` field only ever names a prior Claim, never a Decision (structural hard rule, mechanically enforced by scripts/check_knowledge_base.py); a Claim about observed behaviour is revised only by a new Claim backed by new/reinterpreted Evidence or Derivation, never by a Decision. As a genuinely fuzzy, currently- unresolved boundary: every real Claim produced under this model to date (across all three feature directories) has `contradicting_ evidence: []` and `supersedes: null` -- the mechanism for retaining a real contradiction, or for one Claim genuinely revising a prior one, is structurally checked but has never yet been exercised with real content (EV-EVID-004), so this claim's own account of how that mechanism behaves under real disagreement is honestly untested, not merely theoretical. This formal "Claim" is also a distinct concept from the same word used as a candidate GRAPH-LEVEL entity kind in Phase 57's own Stage E design sketch (CL-EVID-009 documents that collision directly) -- both represent "an interpretation with provenance" in the abstract, but at different scopes (file-based development-process record vs. a proposed context-graph.db table about a target project's own dependencies) and neither is built from or reducible to the other.

Supporting evidence: [EV-EVID-002, EV-EVID-003, EV-EVID-004, EV-EVID-005, EV-EVID-006]
Status: status=superseded
Provenance: HISTORICAL
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-004 semantic-sha256:4af54aba3abb2ebcf6a220f17ff22396dff50bc28766c6971b4d7e7fd9f075a2 projection-sha256:13416536a3d4d53a8fc002243340e556ae781d7119e69824d1d23c9fe8e39440 -->
### CL-EVID-004

A "Derivation" record (DE-<feature>-NNN) records the reasoning PROCESS that produced a Claim -- which files/paths were traced, in what order, and (per this role's own governing brief and the real L-024 learning it produced) what a researcher initially got wrong and how the mistake was caught -- not merely the Claim's own conclusion restated. It is deliberately a narrative field, not a formal proof object, and cites Evidence ids via `inputs`, never Observation ids directly. In every real instance found in this corpus so far, the Claim↔Derivation relationship is exactly 1:1 (one Derivation per Claim, each record naming the other back) -- the schema's own singular `derivation:`/`claim:` fields imply this, but nothing in the schema or the validator actually forbids a future Derivation from being cited as the reasoning behind more than one Claim if two Claims genuinely shared the same reasoning process; no such instance has ever occurred, so whether 1:1 is a real invariant of this model or simply an untested coincidence of small proving cases is a genuine, currently-unresolved boundary question -- an honest "none found yet" for a real N:1 or 1:N counterexample, not a confirmed rule.

Supporting evidence: [EV-EVID-002]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-005 semantic-sha256:4ac28f5ca1be1ef5cf8a8e7c9079df2052d7fa784a39607423161459fca0e12f projection-sha256:a9158cf62fd2eb905c16f02ce75d1865b65a3b83b36298dc76924a5132be9879 -->
### CL-EVID-005

A "Decision" record (DEC-<feature>-NNN), in Phase 54c's own model, is the ONE record kind only a human/project-owner authors or explicitly ratifies -- it records CHOSEN target-project behaviour, never a revision of factually observed upstream behaviour, and its own `supersedes` field only ever names a prior Decision, never a Claim (the same structural hard rule as CL-EVID-003, enforced mechanically). A significant, currently-real edge case: EVERY Decision record produced under this model to date (DEC-DOCORIGIN-001, DEC-HSAPI-001) was authored by the lead explicitly standing in for the actual user/project-owner role, disclosed plainly in each record's own `decided_by` field and in that phase's own retro -- this model's own "only a human authors this" property has therefore never yet been tested against a real, independent, non-standing-in human decision-maker anywhere in this repository's history as of this research. This matters going forward specifically because Phase 63D itself (development-methodology.md, amended 2026-09-20) explicitly withdraws the lead's stand-in permission for genuine domain/product ambiguities from this point on: any new Decision produced under this methodology from Phase 63D onward must be either a real ruling by the actual user, or the ambiguity stays an open question rather than becoming a Decision record at all -- a stricter bar than every real Decision record on file currently meets.

Supporting evidence: [EV-EVID-003, EV-EVID-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-006 semantic-sha256:91471cd5bb8ed9986a919cbc80e5c18d6f4ca38ee078b302a08a33b2250f2d9e projection-sha256:5f3babca320bff594773d969b81030f54ad6ef2f86875f2a0428ffc5c1f1570b -->
### CL-EVID-006

A "Requirement" record (REQ-<feature>-NNN), in Phase 54c's own model, is implementation-facing and testable -- the thing a coding agent actually implements against -- always citing the Decision that authorises it (and, through it, the Claim/Evidence chain behind that Decision), with a Given/When/Then `example` field and a closed `status` enum (proposed|approved|implemented|verified). It is a narrower, more specific concept than "invariant": a Requirement is one single testable statement traceable to exactly one Decision (REQ-DOCORIGIN-001 → DEC-DOCORIGIN-001), whereas a project-wide invariant (docs/domain/invariants.md, this phase's own deliverable) is a cross-cutting rule that need not trace to any single Decision or Requirement at all -- the two concepts overlap (a Requirement's own behaviour, once implemented, often amounts to enforcing something that could also be phrased as an invariant) but are not the same record kind and are not interchangeable citations.

Supporting evidence: [EV-EVID-002, EV-EVID-012]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-007 semantic-sha256:413d1d1ae6424e5b6139f1e8165da624ec34b6bceafc271a2361eec96e75f694 projection-sha256:56a6c4c3786b324eefd7ec4d9d64622f0aeea0cb300f53f8a49ef960789bc04b -->
### CL-EVID-007

"Invariant" is NOT one of Phase 54c's six formal record kinds and has no dedicated schema anywhere in this repository. As used across this codebase today, it names at least three distinct artifacts with three different promotion/citation mechanisms and no requirement that they ever coincide for a given rule: (a) `planning/learnings/`'s own `invariant` classification value, meaning "a required behavioural invariant of CodeCompass's own code," whose correct promotion destination is a regression test (learning-lifecycle.md §4); (b) a narrative "things that must stay true" subsection inside a per-feature `design.md`/`context-packet.md`, which is a subset of that document's own content and never itself a separately-citable record id; (c) the project-wide `docs/domain/invariants.md` file this very phase (63D) produces, explicitly defined as cross-cutting rules "pulled up from individual concept docs where a rule isn't concept-local." All three share the ordinary-English sense of "a rule that must stay true," but a rule recorded in one is not automatically present, or even expected to be present, in either of the other two. This is a genuinely fuzzy concept boundary this research surfaces rather than resolves: whether these three senses should eventually be unified, cross-referenced, or deliberately kept separate is a real, open documentation-design question this Claim does not settle.

Supporting evidence: [EV-EVID-011, EV-EVID-012]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-008 semantic-sha256:da034e82d06ee812d36879a027dd36d6994da7fa6fc7fc599fd0836c8fb6cec0 projection-sha256:66141896d8ffd2897960c85032a36d59aeecfe22a6bd593720d5df85d1461074 -->
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

<!-- codecompass-knowledge: CL-EVID-011 semantic-sha256:9082a79f06a13e5e185bf943e787844194378ed8d310ee6e28e3a731dc4b95fc projection-sha256:4cf996ccf6102de3fc43413e3ea5e084d8cedb2ec7b2b6b10a06d37078f234f2 -->
### CL-EVID-011

A real, already-named naming collision exists, and is deliberately unresolved, between Phase 54c's file-based Evidence/Observation/ Claim/Decision records (planning/knowledge/<slug>/, CodeCompass's own development-process knowledge, the subject of this whole cluster) and a candidate GRAPH-LEVEL (context-graph.db) entity-kind proposal using the identical names to represent provenance about OTHER PROJECTS' technical dependencies (originally sketched in v1-redefinition/ roadmap.md's old "Stage E" section, §2.4 "provenance/evidence" of planning/v1-redefinition/conditional-generalisation.md, conditional on GATE DD). These are genuinely different concepts sharing four words: the file-based kinds are narrative YAML records about CodeCompass's own reasoning process, written by context-researcher/documentation- agent/knowledge-curator, never queryable via `codecompass query`; the graph-level candidate kinds (not yet built, not funded, conditional on a gate that has not been decided) would be structured, queryable database rows about a target project's own dependency provenance. This Claim documents the collision as real, evidenced, and open -- it is this cluster's single most important open question and is carried forward to docs/domain/open-questions.md verbatim, not silently resolved by naming a preference here. This Claim supersedes CL-EVID-009 for exactly one reason, narrower than the substantive collision itself: CL-EVID-009's own statement named the future resolution vehicle as "Stage E's own future Domain stage," and `decisions/0062` (Phase 72) explicitly retires the old "Stage E" phase-group label project-wide -- post-v1 work is now organised into Priority A-F, not lettered stages (`planning/ROADMAP.md`'s "Post-v1 priorities (A-F)" section). The candidate design this collision concerns (`conditional- generalisation.md` §2.4, "provenance/evidence") is re-homed by `planning/pre-v1-disposition.md` §7's own disposition table specifically to **Priority B** -- not to an unnamed future stage, and not resolved. GATE DD itself remains exactly as open as before: `decisions/0062`'s own words are "GATE DD is not resolved by this decision." The corrected resolution path is therefore: the candidate design's own future Domain stage, whichever Priority phase eventually takes it up (currently re-homed to Priority B by `pre-v1-disposition.md` §7, per `decisions/0062`) must either pick genuinely distinct names or explicitly justify sharing the terms with a stated disambiguation rule -- still NOT a decision this research makes, since resolving it requires GATE DD funding decisions and whichever future Priority-B phase plan takes up this candidate design, exactly as far outside this research's own scope as before. Nothing about the collision's reality, evidence, or open status has changed; only the name of the future phase-group vehicle has, because that phase-group itself no longer exists under its old name.

Supporting evidence: [EV-EVID-006, EV-SKEP-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-012 semantic-sha256:5de6823616a74f94bfc00235cf40facf3ba2e6492b26a49f77545eac181b3078 projection-sha256:592827d6ef9cd78174eac27f303cb1e617c1de9a5ae2b2263620fd4f6f458c8e -->
### CL-EVID-012

A "Claim" record (CL-<feature>-NNN), in Phase 54c's own model, is an agent's interpretation built from one or more Evidence records -- the ONLY place a support/contradict relationship is recorded (never on Evidence itself, CL-EVID-001). Its `status` enum (proposed|supported|contradicted|superseded|verified) is the only place "how sure are we" is recorded, with no numeric confidence score anywhere. Its `supersedes` field only ever names a prior Claim, never a Decision (structural hard rule, mechanically enforced by scripts/check_knowledge_base.py); a Claim about observed behaviour is revised only by a new Claim backed by new/reinterpreted Evidence or Derivation, never by a Decision. As a genuinely fuzzy, currently- unresolved boundary: every real Claim produced under this model before Phase 72 had `contradicting_evidence: []`, and until this Claim (and its sibling CL-EVID-011) every real Claim also had `supersedes: null` -- CL-EVID-011/CL-EVID-012 are this model's first real exercise of the Claim-supersedes-Claim mechanism with real content (a narrow, mechanical resolution-mechanism correction, not a substantive reversal), so this claim's own account of how that mechanism behaves under a genuine contradiction (as opposed to a citation-freshness correction) remains honestly untested, not merely theoretical. This formal "Claim" is also a distinct concept from the same word used as a candidate GRAPH-LEVEL entity kind in a candidate design originally sketched in `planning/v1-redefinition/roadmap.md`'s old "Stage E" section, `conditional-generalisation.md` §2.4 (CL-EVID-011, superseding CL-EVID-009, documents that collision directly) -- both represent "an interpretation with provenance" in the abstract, but at different scopes (file-based development-process record vs. a proposed context-graph.db table about a target project's own dependencies) and neither is built from or reducible to the other. This Claim supersedes CL-EVID-003 for the same narrow reason CL-EVID-011 supersedes CL-EVID-009: CL-EVID-003's own statement named the colliding graph-level design as "Phase 57's own Stage E design sketch," and `decisions/0062` (Phase 72) retires the "Stage E" phase-group label project-wide -- the candidate design itself (`conditional-generalisation.md` §2.4) is unaffected and is now re-homed to Priority B by `planning/pre-v1-disposition.md` §7, per `decisions/0062`. Everything else in CL-EVID-003's original statement -- the Claim-schema account, the untested-mechanism disclosure, the fact of the naming collision itself -- is unchanged and re-asserted here.

Supporting evidence: [EV-EVID-002, EV-EVID-003, EV-EVID-004, EV-EVID-005, EV-EVID-006, EV-SKEP-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-013 semantic-sha256:4a320d728ced99cb2e7efb1a7cb59a4b76507c67181a2812a42db13c266efd63 projection-sha256:f515ec13fc7013de84a9afbc93e7ed4b5bec783c7f1d944c3c7ea681aeaf4ec8 -->
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

Plain prose becomes an unclassified Claim (a factual hypothesis, not yet evidence-backed) — this is the default and the common case. Merely mentioning a Decision id anywhere in your prose does NOT make your addition a Requirement, and merely using the word "should" or "must" does NOT make it declared intent — both need the explicit structured forms below.

To propose a REQUIREMENT, start the block with a line reading exactly "Type: Requirement", followed by:
  Decision: <id of an existing, already-approved Decision>
  Statement: <the requirement itself, one line>
  Example: <a Given/When/Then acceptance example>
CodeCompass never invents a Decision on your behalf — a missing or not-yet-approved Decision id, or an Example that doesn't structurally read as Given/When/Then, falls back to an ordinary Claim using your Statement text, never a fabricated placeholder example.

To declare project INTENT (a proposed policy, not yet a fact about the system), start the block with a line reading exactly "Type: Intent", followed by the intended behaviour as plain prose on the lines after it.

Anything else — plain prose with no Type: header — stays an unclassified Claim until a reviewer looks at it.

<!-- codecompass-candidates:start --><!-- codecompass-candidates:end -->
