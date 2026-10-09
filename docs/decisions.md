# Decisions and current status

This is a mechanical title+status index over the project's own architectural decision log (`decisions/*.md`), not a hand-synthesized rationale per decision — most of the 74 real ADRs that exist have no fuller rationale text recoverable from the available evidence, and this page lists them honestly as a title and status only, per the project's own documented guidance for exactly this situation. Fuller rationale is given in the body text elsewhere in this `docs/` tree only for the handful of decisions whose own reasoning was directly supplied as evidence (notably `decisions/0002`, `0017`, `0031`, `0033`, `0035`, `0038`, `0057`, `0058`, `0059`, `DEC-DOCORIGIN-001`, `DEC-HSAPI-001`).

**A confirmed numbering gap:** this index runs `0001`–`0075` with no `0044` — a real, confirmed absence (checked directly against the project's own history, not a rendering artefact), most likely a reserved number never filled during drafting rather than a withdrawn-and-deleted decision. There is nothing to cite if a documentation claim ever needs "0044" specifically.

**A known limitation of this table:** the Status column is read mechanically from each ADR's own first-line status field only, never cross-checked against whether some *later*, higher-numbered ADR's own title announces that it supersedes an earlier one by title alone. A real, confirmed example: `0019` shows `Accepted` below, but `0061`'s own title states it is superseded by `0035`. Scan later-numbered titles for a "supersedes NNNN"/"NNNN is superseded by" pattern before trusting this table's Status column at face value for anything load-bearing.

| ADR | Title | Status |
|---|---|---|
| 0001 | Depth is per-vendor, not global | Accepted |
| 0002 | Adapter approach differs per ecosystem | Accepted |
| 0003 | Use claude-haiku-4-5 for gap analysis | Accepted |
| 0004 | FULL vendors get a copied source snapshot, not a node_modules reference | Accepted |
| 0005 | Severity-aware staleness, not binary | Accepted |
| 0006 | Root CLAUDE.md requires explicit approval before any edit | Accepted |
| 0007 | No AI attribution in commits | Accepted |
| 0008 | MVP ships npm, Python, and Cargo adapters on day one | Accepted |
| 0009 | Minimum supported Python is 3.11 | Accepted |
| 0010 | `vendor/<name>/src/` snapshots are gitignored and regenerated, not committed | Accepted |
| 0011 | Core data models use stdlib dataclasses, not pydantic | Accepted |
| 0012 | Conversational-first REPL design | Accepted |
| 0013 | Agent Skills as the shared context-selection source for multi-tool export, REPL routing, and REPL escalation | Accepted |
| 0014 | Adapter tests use fixture-mocking, not live subprocesses, as the primary strategy | Accepted |
| 0015 | Symbol/purpose extraction reuses per-ecosystem adapter parsing, not a generic heuristic | Accepted |
| 0016 | Gap-analysis tests never call the live Anthropic API | Accepted |
| 0017 | Zero-question deterministic bootstrap | Accepted |
| 0018 | `promote` is the sole reactive depth-escalation and cost-disclosure point | Accepted |
| 0019 | Grounded description replaces gap analysis for FULL-depth generation | Accepted (see note: `0061` states this is superseded by `0035`) |
| 0020 | Tool-level Skill, generated unconditionally | Accepted |
| 0021 | PyPI packages without a resolvable repository URL fail `promote` rather than falling back to a source tarball | Accepted |
| 0022 | MVP expands to phases 0-8 | Accepted |
| 0023 | Chat grounds on persisted digest files, not live regeneration | Accepted |
| 0024 | Context graph stored as a single root-level file, not per-vendor | Accepted |
| 0025 | Context graph rebuilds only on whole-project `sync`, never incrementally | Accepted |
| 0026 | Context-graph enrichment (9d) is optional, deterministic-gated, and does not close `0013`'s harness item | Accepted |
| 0027 | `EXPLAINS` chunk retrieval coexists with, does not replace, `0023`'s whole-file chat grounding | Accepted |
| 0028 | Usage-cluster classification is draft-only, never auto-written, deferred to a future phase | Accepted |
| 0029 | Package renamed depcompass → codecompass | Accepted |
| 0030 | MVP redefined: v0.2 spans phases 9-19 | Accepted |
| 0031 | `Depth` retired; enrichment is usage-driven, not a per-vendor toggle | Accepted |
| 0032 | Context graph stored in SQLite, not a single JSON file | Accepted |
| 0033 | `promote` retired; universal cloning + auto-triggered, disclosed consent is the sole cost point | Accepted |
| 0034 | Chat demoted; the graph, generated Skills, and `/discovery` are the primary interface | Accepted |
| 0035 | `sync_vendor` reads enrichment from the graph; `grounded_description.py` retired | Accepted |
| 0036 | `undo` is a best-effort, origin-tag-driven filesystem cleanup, not a transactional rollback | Accepted |
| 0037 | Spec docs are a new `doc_artifacts`/`doc_relations_edges` shape, detected by fixed default globs | Accepted |
| 0038 | `doc_relation_enrichment` is natural-key-only with no foreign key, and never writes to a spec doc | Accepted |
| 0039 | v1.0 ships without a dedicated docs site — README + `docs/*.md` rendered on GitHub only | Accepted |
| 0040 | `/discovery`'s read-only posture is mechanically enforced for one turn, held by prose for the rest of the session | Accepted |
| 0041 | Vendor-embedded upstream docs are a new `doc_artifacts` kind, root-level files only | Accepted |
| 0042 | Relationship-enrichment excerpts re-derive the match position at enrichment time | Accepted |
| 0043 | Vendor docs become relationship sources: a closed allow-set, plus a self-mention exclusion | Accepted |
| 0044 | *(no record exists — confirmed numbering gap, see above)* | — |
| 0045 | Typed relation labels describe, they don't detect | Accepted |
| 0046 | Heading-based doc chunking, additive and nullable throughout | Accepted |
| 0047 | Lower-bound-only dependency pins for v1.0 | Accepted |
| 0048 | Redefined v1 is a product-validation milestone, not a packaging milestone | Accepted |
| 0049 | Agent-led development model — lead session + small specialist roster | Accepted |
| 0050 | Phase retros and a per-phase independent docs-drift audit as DoD conditions | Accepted |
| 0051 | Agent-suggested context is captured as reviewable candidates, never written to the context graph | Accepted |
| 0052 | Ledgerkit is the next reference project, not Technical Clipper | Accepted |
| 0053 | Relicense CodeCompass to GPL-3.0-or-later | Accepted |
| 0054 | Agent-driven enrichment is a second, non-authoritative producer feeding the existing enrichment tables | Accepted |
| 0055 | Contributor licensing terms preserve future re/dual-licensing options | Accepted |
| 0056 | Cross-language validation via a minimal Haskell adapter, not Technical Clipper | Accepted |
| 0057 | A second adapter-implementation strategy: external-process adapters over a small JSON protocol | Accepted |
| 0058 | The adapter protocol and the Haskell adapter are separate, differently-licensed public repositories, checked out as submodules | Accepted |
| 0059 | `analyze_project`'s `symbols` entries gain an optional `kind`/`note` pair | Accepted |
| 0060 | Formalize Scope → Plan → Domain → Design → Implement as the v1 development methodology | Accepted |
| 0061 | `decisions/0019` is superseded by `decisions/0035` | Accepted |
| 0062 | Post-v1 priorities are task-context completeness first, ordered Priority A-F | Accepted |
| 0063 | Git repository topology (worktrees, submodules) is a new, separate graph capability | Accepted |
| 0064 | `decisions/0063` point 8 is superseded: Git 2.7, not 2.5, is the real minimum version | Accepted |
| 0065 | First-party source is language-classified, occurrence-identified, and honestly graded by extraction fidelity | Accepted |
| 0066 | Clean-room conceptual understanding is published from one shared, correctly-schemaed knowledge foundation, isolated by a verified mechanism | Accepted (amended three times same date; superseded for post-implementation defects by `0067`) |
| 0067 | A later amendment's post-implementation corrections are a new ADR, not an in-place edit to `0066` | Accepted |
| 0068 | A further amendment is a new ADR, by the same reasoning `0067` established | Accepted |
| 0069 | Priority A (task-context completeness) is closed | Accepted (corrected by `0070`) |
| 0070 | Priority A's exit decision is corrected: reopened | Accepted (supersedes `0069`) |
| 0071 | The knowledge layer's canonical model stays outside the context graph | Accepted |
| 0072 | The knowledge-reconciliation loop adds zero new persisted canonical fields | Accepted |
| 0073 | The knowledge-reconciliation implementation is corrected (first corrective pass) | Accepted (refines, not reverses, `0071`/`0072`) |
| 0074 | The knowledge-reconciliation implementation is corrected a second time | Accepted (refines, not reverses, `0071`/`0072`/`0073`) |
| 0075 | The knowledge-reconciliation implementation is corrected a third time | Accepted (refines, not reverses, `0071`–`0074`) |
