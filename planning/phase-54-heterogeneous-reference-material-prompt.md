Act as the CodeCompass orchestrator and plan the next phase according to the current roadmap goals, using the repository’s present state, current phase numbering, planning conventions, ADRs, recent retrospectives, and LedgerKit evaluation evidence.

Do not assume this prompt’s suggested mechanism is the final design. First confirm what the roadmap currently requires for the next phase and plan against that objective.

The expected roadmap goal is the heterogeneous reference dependency / doc-reference experiment: test whether CodeCompass can make external technical references—especially hledger manuals/specification material—materially useful to agents working on real LedgerKit tasks, without prematurely committing to a broad new graph ontology.

Use the following ingestion mechanism as a design hypothesis to evaluate during planning:

references.toml
    ↓
resolve requested version/tag
    ↓
immutable commit/hash
    ↓
references.lock
    ↓
fetch/cache
    ↓
extract selected files/sections
    ↓
index with provenance
    ↓
relate to LedgerKit code/tests/docs

Prefer a Git-backed reference source for hledger where practical. Resolve a human-friendly hledger version/tag to an exact commit SHA and preserve source, requested ref, resolved commit, selected paths/sections and content hashes. Consider local project references and URL + SHA-256 only where appropriate.

The orchestrator should:

1. inspect the current CodeCompass roadmap and confirm the exact next-phase objective;
2. inspect current CodeCompass and LedgerKit state before choosing an experiment;
3. select one genuine LedgerKit task where external hledger reference material matters;
4. design the smallest reproducible reference-ingestion experiment needed to satisfy the roadmap goal;
5. reuse existing CodeCompass graph, discovery, provenance and enrichment mechanisms where possible;
6. avoid introducing a generic TechnicalDependency ontology unless the experiment demonstrates it is necessary;
7. use the Phase 52 context lifecycle to record useful, irrelevant, misleading and missing context;
8. define an evaluation comparing agent behaviour/context discovery with and without the ingested reference;
9. treat negative or inconclusive results as valid evidence;
10. identify what evidence this phase must produce for the roadmap’s later generalisation gate.

The key question remains:

Can CodeCompass reproducibly pin and expose external technical reference material so that it materially improves an agent’s context for a real LedgerKit task?

Produce the normal next-phase planning artefacts and follow the standard CodeCompass planning, implementation, independent evaluation, audit, documentation and retrospective process. Do not begin implementation until the phase plan has been produced and reviewed.
