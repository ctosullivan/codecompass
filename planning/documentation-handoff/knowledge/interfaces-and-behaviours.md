# Interfaces And Behaviours (handoff selection, 4 of 4 selected slugs with real content)

Each section below is the real, current, mechanically-rendered content from one selected knowledge slug's own canonical records — never hand-written prose. See `../INDEX.md` for the selection criteria.

---

## Source: `codecompass-domain` — Project-wide domain knowledge

# codecompass-domain — interfaces and behaviours

<!-- codecompass-knowledge: CL-ADPT-002 semantic-sha256:c34510ed785e7241e3c8a7ecf034465cccc4cc363b4e04b9cdaf1ca696d19ded projection-sha256:228b950a8190c8fca43d733a022eb0c4586afd7398e01c1c691393182531ad04 -->
### CL-ADPT-002

Two EcosystemAdapter implementation strategies coexist by deliberate design, not as one superseding the other: (1) in-process (npm, Python, Cargo) -- an importable Python class inside src/codecompass/ shelling out to native ecosystem tooling; (2) external-process (Haskell, the reference implementation) -- a thin in-process dispatcher for simple manifest reads, delegating all real ecosystem-specific logic to an independent OS process speaking a small JSON-Lines protocol, motivated by ecosystems (e.g. a hypothetical proprietary COBOL adapter) whose implementation cannot or should not be in-process, GPL-covered Python code. decisions/0002 (the first strategy) is explicitly "not superseded" by decisions/0057 (the second) -- in-process remains the default, lower-overhead strategy.

Supporting evidence: [EV-ADPT-002, EV-ADPT-003, EV-ADPT-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-ADPT-005 semantic-sha256:8c6bc39637d554373e9d62429ad0cdd1e7ee25132100c0c04778074bbaab3418 projection-sha256:2905fb23849c6d5cf4055e9888d349b82c018f8de71a36db7f99c36923027b95 -->
### CL-ADPT-005

Ecosystem, vendor, and adapter are three related but distinct concepts. Ecosystem is a fixed, closed 4-member enum (npm, python, cargo, haskell) -- a category, not a thing you configure per project. A vendor is one tracked dependency: a VendorConfig(name, ecosystem) entry from vendor.toml, belonging to exactly one Ecosystem (e.g. VendorConfig(name="hledger-lib", ecosystem=Ecosystem.HASKELL)). An adapter is the EcosystemAdapter subclass implementing ecosystem-specific logic for one Ecosystem value (e.g. HaskellAdapter for Ecosystem.HASKELL) -- constructed fresh per (VendorConfig, project_root) via get_adapter, not itself configured or tracked as project state the way a vendor is. Concretely: many vendors can share one Ecosystem (multiple Haskell vendors all use Ecosystem.HASKELL) and therefore share one adapter *class*, but each vendor still gets its own adapter *instance*, scoped to that vendor's own config and project_root. Edge case: the "one vendor, one adapter instance" relationship is not a structural filesystem guarantee -- HaskellAdapter's own monorepo resolution (_resolve_package_dir) shows a single project_root can host multiple vendors' worth of source (e.g. hledger-lib/hledger/hledger-ui all inside one `hledger` checkout), and the adapter instance itself is responsible for narrowing project_root down to the one subdirectory matching its own vendor's name before any other method call is meaningful.

Supporting evidence: [EV-ADPT-005, EV-ADPT-002]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-EVID-010 semantic-sha256:26390b5192ac79bb6e9ea83611a2196d003e76d5cfc4e382d4d03faeb33098aa projection-sha256:607f0c7632666d03d4391d0c6c15ce118e8fb3208efee49ade0a179cbd259efa -->
### CL-EVID-010

This codebase has at least FIVE genuinely distinct "something was noticed/recorded" mechanisms, each at a different trust/purpose level, distinguishable by real evidence rather than by name alone: (1) Phase 54c's `kind: observation` (OBS-<feature>-NNN) -- a primary-research act of looking, feeding an Evidence/Claim, written under planning/knowledge/<slug>/, never itself authoritative; (2) `planning/context-gaps/` -- "a relationship CodeCompass's context should represent but mechanical detection doesn't/can't," prose captured only in planning/, explicitly never entering context-graph.db (decisions/0051), promoted only via the learning lifecycle to a Stage C/E gated roadmap decision; (3) `planning/context-observations/` -- "how real context experience went" with an edge that ALREADY EXISTS (EDGE_USEFUL/UNHELPFUL/ MISLEADING/STALE/REDUNDANT), the explicit inverse scope of (2) (experience with edges that exist vs. requests for edges that don't), confusingly reusing the literal "OBS-" id-prefix from (1) for an unrelated shape; (4) `planning/learnings/` -- "how we should work," a project-process lesson queue reviewed by the same `knowledge-curator` as (2)/(3) but routing to a different destination set (tests/ADRs/ docs/CLAUDE.md/skills/roadmap rows, never a detection heuristic or graph capability); (5) AI-authored graph enrichment (vendor_enrichment/symbol_enrichment/doc_relation_enrichment) -- interpretive content an AI produces ABOUT AN ALREADY-PROVEN graph fact, written through `apply_results()`, tagged only by a `model` column, explicitly "never a fact CodeCompass proves" (decisions/0054) -- the only one of the five that writes anywhere inside context-graph.db itself, and the only one with no Observation/ Evidence/Claim-style narrative chain behind it at all. None of the five is interchangeable with, or a special case of, another; each has its own destination, its own write boundary, and (for 1-4) its own queue file(s).

Supporting evidence: [EV-EVID-007, EV-EVID-008, EV-EVID-009, EV-EVID-010, EV-EVID-011]
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

---

## Source: `doc-origin-pinned-reference` — Doc-origin pinned-reference tracking (a real CodeCompass capability)

# doc-origin-pinned-reference — interfaces and behaviours

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

---

## Source: `first-party-source-symbols` — First-party source/symbol indexing (a real CodeCompass capability)

# first-party-source-symbols — interfaces and behaviours

<!-- codecompass-knowledge: CL-FPSS-003 semantic-sha256:ffcd040d6eb8c25fefadae9bce540b5a3fe5ccd71b08316d4d33a08a516ab5f0 projection-sha256:5cf9d7798d244089a4b9a2131d84c4d9fb2534a06ab6d2f7e8ba19230bb3617e -->
### CL-FPSS-003

The five-state SymbolIndexStatus model (indexed/indexed_partial/ unsupported/parse_error/unreadable) exists to prevent a bare empty symbols list from ambiguously standing in for more than one real cause. indexed and indexed_partial are distinguished purely by extraction *technique fidelity*, never by whether anything was found: indexed means a real structural parser (Python's ast.parse) ran and either succeeded (possibly finding zero symbols) or the extractor never reaches this status if parsing itself failed; indexed_partial means a coarse line-scan/regex heuristic ran (Rust, JS, TypeScript) -- a technique with no real parse step, so it can never fail structurally the way ast.parse can, and is dispatched unconditionally on successful file read regardless of what (if anything) it finds. unsupported means no extractor exists for the file's language at all (Haskell today) -- the file is never even opened. parse_error is Python-specific (ast.parse raising SyntaxError) since Rust/JS/TS have no real parse step to fail. unreadable applies to any language (OSError or UnicodeDecodeError on read). No code path in this module ever returns indexed_partial for Python or indexed for Rust/JS/TS -- the mapping from language to indexed-vs-indexed_partial is fixed, not content-dependent.

Supporting evidence: ["EV-FPSS-006", "EV-FPSS-007", "EV-FPSS-020"]
Status: status=supported, evidence_support_state=supported
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

---

## Source: `haskell-api-surface-extraction` — Haskell API surface extraction (a real CodeCompass capability)

# haskell-api-surface-extraction — interfaces and behaviours

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
