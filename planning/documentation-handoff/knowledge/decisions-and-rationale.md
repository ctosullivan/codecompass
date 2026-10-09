# Decisions and rationale (mechanical index, not a synthesis)

A mechanically-generated title + status index over every ADR in `decisions/*.md` — **not** a hand-synthesized one-line rationale per decision (74 ADRs exist; genuinely summarising each one's own rationale is real synthesis work this preparation pass does not attempt rather than guess at). The writer consumes this index plus, where a specific decision's own reasoning materially matters to a documentation claim, the real file it points at — never the full ADR corpus wholesale (per the clean-room allowlist, `decisions/**` itself is excluded from the writer's own visible filesystem).

**Numbering gap, checked directly (2026-10-09, cold-reader finding #3)**:
this index runs `0001`–`0075` with no row for `0044` — confirmed a real
gap, not a rendering artefact: `git log --all --diff-filter=A -- decisions/0044*`
and the equivalent `--diff-filter=D` search both return nothing, so
`decisions/0044` was never created, committed, or deleted anywhere in
this repository's own history. The most likely honest explanation is a
reserved number never filled during drafting, not a withdrawn decision
that was deleted outright — but this preparation pass has no stronger
evidence than that, and says so rather than guessing further. If a
documentation claim ever needs to cite "0044" specifically, there is
nothing to cite.

**Known limitation, named explicitly (2026-10-09, cold-reader finding
#2)**: the "Status" column below is read mechanically from each ADR's
own first-line status field only — it is never cross-checked against
whether some *later*, higher-numbered ADR's own title announces that it
supersedes an earlier one. A real example exists in this exact table:
`0019` shows status `Accepted`, but `0061`'s own title literally reads
"`decisions/0019` is superseded by `decisions/0035`." This index cannot
tell you, in general, which other rows have the same undetected-
supersession problem — if you need to state a decision's *current*
force confidently, scan later-numbered titles for a "supersedes NNNN" or
"NNNN is superseded by" pattern before trusting this table's own Status
column at face value, rather than assuming the mechanical column is
always already reconciled.

| ADR | Title | Status (full, untruncated) |
|---|---|---|
| `0001-depth-is-per-vendor-not-global.md` | 0001. Depth is per-vendor, not global | Accepted |
| `0002-adapter-approach-differs-per-ecosystem.md` | 0002. Adapter approach differs per ecosystem | Accepted |
| `0003-haiku-for-gap-analysis.md` | 0003. Use claude-haiku-4-5 for gap analysis | Accepted |
| `0004-vendor-src-snapshot-not-node-modules-reference.md` | 0004. FULL vendors get a copied source snapshot, not a node_modules reference | Accepted |
| `0005-severity-aware-staleness.md` | 0005. Severity-aware staleness, not binary | Accepted |
| `0006-claude-md-requires-explicit-approval.md` | 0006. Root CLAUDE.md requires explicit approval before any edit | Accepted |
| `0007-no-claude-attribution-in-commits.md` | 0007. No AI attribution in commits | Accepted |
| `0008-mvp-ships-three-adapters-day-one.md` | 0008. MVP ships npm, Python, and Cargo adapters on day one | Accepted |
| `0009-minimum-python-3-11.md` | 0009. Minimum supported Python is 3.11 | Accepted |
| `0010-vendor-src-gitignored-and-regenerated.md` | 0010. `vendor/<name>/src/` snapshots are gitignored and regenerated, not committed | Accepted |
| `0011-dataclasses-over-pydantic-for-core-models.md` | 0011. Core data models use stdlib dataclasses, not pydantic | Accepted |
| `0012-conversational-first-repl-design.md` | 0012. Conversational-first REPL design | Accepted |
| `0013-agent-skills-as-shared-context-selection-source.md` | 0013. Agent Skills as the shared context-selection source for multi-tool export, REPL routing, and REPL escalation | Accepted |
| `0014-adapter-tests-use-fixture-mocking-not-live-subprocesses.md` | 0014. Adapter tests use fixture-mocking, not live subprocesses, as the primary strategy | Accepted |
| `0015-symbol-extraction-reuses-adapter-parsing-per-ecosystem.md` | 0015. Symbol/purpose extraction reuses per-ecosystem adapter parsing, not a generic heuristic | Accepted |
| `0016-gap-analysis-tests-never-call-the-live-anthropic-api.md` | 0016. Gap-analysis tests never call the live Anthropic API | Accepted |
| `0017-zero-question-deterministic-bootstrap.md` | 0017. Zero-question deterministic bootstrap | Accepted |
| `0018-promote-is-the-sole-reactive-depth-escalation-point.md` | 0018. `promote` is the sole reactive depth-escalation and cost-disclosure point | Accepted |
| `0019-grounded-description-replaces-gap-analysis.md` | 0019. Grounded description replaces gap analysis for FULL-depth generation | Accepted |
| `0020-tool-level-skill-generated-unconditionally.md` | 0020. Tool-level Skill, generated unconditionally | Accepted |
| `0021-pypi-source-resolution-fails-loudly.md` | 0021. PyPI packages without a resolvable repository URL fail `promote` rather than falling back to a source tarball | Accepted |
| `0022-mvp-expands-to-phases-0-8.md` | 0022. MVP expands to phases 0-8 | Accepted |
| `0023-chat-grounds-on-persisted-files-not-live-regeneration.md` | 0023. Chat grounds on persisted digest files, not live regeneration | Accepted |
| `0024-context-graph-stored-as-single-root-level-file.md` | 0024. Context graph stored as a single root-level file, not per-vendor | Accepted |
| `0025-context-graph-rebuilds-only-on-whole-project-sync.md` | 0025. Context graph rebuilds only on whole-project `sync`, never incrementally | Accepted |
| `0026-context-graph-enrichment-is-optional-and-deterministic-gated.md` | 0026. Context-graph enrichment (9d) is optional, deterministic-gated, and does not close decisions/0013's harness item | Accepted |
| `0027-explains-edges-coexist-with-whole-file-chat-grounding.md` | 0027. `EXPLAINS` chunk retrieval coexists with, does not replace, decisions/0023's whole-file chat grounding | Accepted |
| `0028-usage-cluster-classification-is-draft-only-and-deferred.md` | 0028. Usage-cluster classification is draft-only, never auto-written, and deferred to a future 9e | Accepted |
| `0029-package-renamed-depcompass-to-codecompass.md` | 0029. Package renamed depcompass → codecompass | Accepted |
| `0030-mvp-redefined-v0.2-spans-phases-9-19.md` | 0030. MVP redefined: v0.2 spans phases 9-19 | Accepted |
| `0031-depth-retired-enrichment-is-usage-driven.md` | 0031. `Depth` retired; enrichment is usage-driven, not a per-vendor toggle | Accepted |
| `0032-context-graph-stored-in-sqlite.md` | 0032. Context graph stored in SQLite, not a single JSON file | Accepted |
| `0033-promote-retired-universal-cloning-and-auto-triggered-consent.md` | 0033. `promote` retired; universal cloning + auto-triggered, disclosed consent is the sole cost point | Accepted |
| `0034-chat-demoted-graph-and-skills-are-primary.md` | 0034. Chat demoted; the graph, generated Skills, and `/discovery` are the primary interface | Accepted |
| `0035-sync-vendor-reads-enrichment-from-graph-grounded-description-retired.md` | 0035. `sync_vendor` reads enrichment from the graph; `grounded_description.py` retired | Accepted |
| `0036-undo-is-best-effort-cleanup.md` | 0036. `undo` is a best-effort, origin-tag-driven filesystem cleanup, not a transactional rollback | Accepted |
| `0037-spec-docs-get-a-dedicated-table-and-glob-based-detection.md` | 0037. Spec docs are a new `doc_artifacts`/`doc_relations_edges` shape, detected by fixed default globs | Accepted |
| `0038-relation-enrichment-natural-key-only-no-fk-never-writes-spec-docs.md` | 0038. `doc_relation_enrichment` is natural-key-only with no foreign key, and never writes to a spec doc | Accepted |
| `0039-v1.0-ships-without-a-dedicated-docs-site.md` | 0039. v1.0 ships without a dedicated docs site — `README.md` + `docs/*.md` rendered on GitHub only | Accepted |
| `0040-discovery-read-only-posture-held-by-prose-not-mechanically-past-one-turn.md` | 0040. `/discovery`'s read-only posture is mechanically enforced for one turn, held by prose for the rest of the session | Accepted |
| `0041-vendor-upstream-docs-are-a-new-doc-artifacts-kind-root-level-only.md` | 0041. Vendor-embedded upstream docs are a new `doc_artifacts` kind, root-level files only | Accepted |
| `0042-relation-enrichment-excerpts-re-derive-match-position-at-enrichment-time.md` | 0042. Relationship-enrichment excerpts re-derive the match position at enrichment time, don't persist it from Phase 21 | Accepted |
| `0043-vendor-docs-become-relationship-sources-closed-allow-set-plus-self-mention-exclusion.md` | 0043. Vendor docs become relationship sources: a closed allow-set, plus a self-mention exclusion | Accepted |
| `0045-typed-relation-labels-not-new-detection.md` | 0045: Typed relation labels describe, they don't detect | Accepted. |
| `0046-doc-chunking-heading-based-additive.md` | 0046: Heading-based doc chunking, additive and nullable throughout | Accepted. |
| `0047-lower-bound-dependency-pins-for-v1.md` | 0047: Lower-bound-only dependency pins for v1.0 | Accepted. |
| `0048-redefined-v1-is-a-product-validation-milestone.md` | 0048. Redefined v1 is a product-validation milestone, not a packaging milestone | Accepted (Phase 39, `planning/v1-redefinition/`). |
| `0049-agent-led-development-model.md` | 0049. Agent-led development model — lead session + small specialist roster | Accepted (Phase 39 records it; the roster itself is built in Phase 40). Full design: `planning/v1-redefinition/agent-led-development.md`. |
| `0050-phase-retros-and-per-phase-docs-drift-audit.md` | 0050. Phase retros and a per-phase independent docs-drift audit as DoD conditions | Accepted (Phase 41, user request 2026-09-10). |
| `0051-agent-suggested-context-is-captured-not-graphed.md` | 0051. Agent-suggested context is captured as reviewable candidates, never written to the context graph | Accepted (Phase 43c, user request 2026-09-11). |
| `0052-ledgerkit-is-the-next-reference-project-not-technical-clipper.md` | 0052. Ledgerkit is the next reference project, not Technical Clipper | Accepted (2026-09-12, gate G11). Full plan: `planning/v1-redefinition/realignment-2026-09.md`. |
| `0053-relicense-to-gpl-3.0-or-later.md` | 0053. Relicense CodeCompass to GPL-3.0-or-later | Accepted (2026-09-12, gate G12). Full plan: `planning/v1-redefinition/licence-migration.md`. |
| `0054-agent-driven-enrichment-is-a-second-non-authoritative-producer.md` | 0054. Agent-driven enrichment is a second, non-authoritative producer feeding the existing enrichment tables | Accepted (Phase 52, user request 2026-09-14, during the context-edge- lifecycle implementation — `planning/context-edge-lifecycle-plan.md`, `planning/phase-52-context-edge-lifecycle.md`). |
| `0055-contributor-licensing-terms-preserve-future-relicensing.md` | 0055. Contributor licensing terms preserve future re/dual-licensing options | Accepted (2026-09-15). |
| `0056-cross-language-validation-via-haskell-adapter-not-technical-clipper.md` | 0056. Cross-language validation via a minimal Haskell adapter, not Technical Clipper | Accepted (2026-09-17). |
| `0057-external-process-adapter-protocol.md` | 0057. A second adapter-implementation strategy: external-process adapters over a small JSON protocol | Accepted (2026-09-19). |
| `0058-adapter-protocol-and-haskell-adapter-as-separate-repositories.md` | 0058. The adapter protocol and the Haskell adapter are separate, differently-licensed public repositories, checked out as submodules | Accepted (2026-09-19). |
| `0059-symbol-kind-field-for-reexport-and-undetermined-entries.md` | 0059. `analyze_project`'s `symbols` entries gain an optional `kind`/`note` pair | Accepted (2026-09-19). |
| `0060-scope-plan-domain-design-implement-methodology.md` | 0060. Formalize Scope → Plan → Domain → Design → Implement as CodeCompass's own v1 development methodology, with a new Domain Reconstruction phase (63D) preceding blank-slate doc reconstruction | Accepted (2026-09-20). |
| `0061-decisions-0019-superseded-by-0035.md` | 0061. `decisions/0019` is superseded by `decisions/0035` | Accepted |
| `0062-post-v1-priorities-are-task-context-completeness-first.md` | 0062. Post-v1 priorities are task-context completeness first, ordered Priority A-F, not the old Stage E/graph-capability grouping | Accepted (Phase 72, direct user request, 2026-09-27). |
| `0063-git-repository-topology-as-a-new-graph-capability.md` | 0063. Git repository topology (worktrees, submodules) is a new, separate graph-capability addition — mechanical facts only, per-worktree database isolation, no schema-version-diff migration triggering | Accepted (2026-09-28). |
| `0064-git-2.7-not-2.5-is-phase-76s-real-minimum-version.md` | 0064. `decisions/0063` point 8 is superseded: Git 2.7, not 2.5, is Phase 76's real minimum version — a direct `git --version` check replaces the rejected alternative | Accepted (2026-09-28, corrective pass). |
| `0065-first-party-source-is-language-classified-occurrence-identified-and-honestly-graded.md` | 0065. First-party source is language-classified (not ecosystem-classified), occurrence-identified (not name-identified), and honestly graded by extraction fidelity | Accepted (2026-09-29). |
| `0066-clean-room-reconstruction-needs-mechanical-isolation-and-independent-implementation-comparison.md` | 0066. Clean-room conceptual understanding is published directly into documentation from one shared, correctly-schemaed knowledge foundation, isolated by a verified — and honestly limited — mechanism, not prompt discipline alone | Accepted (2026-09-30, direct user instruction). **Amended in place three times, same date, direct user instruction each time.** Not yet acted upon by any implementation until this fourth revision's own approval, so each amendment through the third revision is a pre-implementation correction, not a reversal of shipped work — edited directly rather than superseded by a new numbered decision, consistent with `CLAUDE.md` §2's append-only rule applying to decisions that have already informed real, executed work. **This fourth revision corrects four further defects found in the third**, approves the overall approach subject to those corrections, and proceeds directly into implementation — see the dated addendum at the end of the Decision section for what changed this time and why this is the point past which the ADR's own content stops being purely pre- implementation. **Post-implementation note (2026-10-01): four defects found in the shipped result are corrected by `decisions/0067`, a new ADR, not a fifth in-place edit here** — per `0067`'s own reasoning, this ADR has already informed real, executed, `done`-flipped work, so its own content below is left exactly as the fourth revision wrote it. |
| `0067-phase-79-post-implementation-corrections-are-a-new-adr-not-an-in-place-edit.md` | 0067. Phase 79's fifth amendment corrects `decisions/0066`'s own post-implementation defects via a new ADR, not an in-place edit | Accepted (2026-10-01, direct user instruction). **Post-implementation note (2026-10-01): three further defects found in the shipped fifth-amendment result are corrected by `decisions/0068`, a new ADR, not a sixth in-place edit here** — by the exact same reasoning this ADR's own Decision section gives for not editing `decisions/0066`: this ADR has already informed real, executed, reconciled work, so its own content below is left exactly as originally written. |
| `0068-phase-79-sixth-amendment-is-a-new-adr-same-reasoning-as-0067.md` | 0068. Phase 79's sixth amendment is a new ADR, by the same reasoning `0067` established for the fifth | Accepted (2026-10-01, direct user instruction). |
| `0069-priority-a-closed-cg-001-tested-and-not-recurred.md` | 0069. Priority A (task-context completeness) is closed; `CG-001`'s own | Accepted (Phase 78, 2026-10-02, direct user request — "Implement phase 78 plan" — following an independent `knowledge-curator` triage of the trial's real result: `planning/reference-projects/ledgerkit/06-priority-a-exit-decision-triage.md`). |
| `0070-phase-78-exit-decision-corrected-priority-a-reopened.md` | 0070. Phase 78's Priority A exit decision is corrected: its own | Accepted (corrective amendment, 2026-10-02, direct user request, following a post-completion review of `decisions/0069`). **Supersedes `decisions/0069` — that ADR's own text is preserved unedited as the historical record of what was decided and why at the time; this ADR corrects its conclusion, per `CLAUDE.md` §2's append-only rule.** |
| `0071-knowledge-layer-canonical-model-stays-outside-context-graph.md` | 0071. The Phase 81 knowledge layer's canonical model is | Accepted (Phase 81, 2026-10-07, direct user request). |
| `0072-knowledge-reconciliation-adds-zero-canonical-fields.md` | 0072. The Phase 81 reconciliation loop adds zero new persisted fields | Accepted (Phase 81, 2026-10-07, direct user request, following two same-day amendments to the Phase 81 plan). |
| `0073-knowledge-layer-corrective-pass.md` | 0073. Phase 81's knowledge-reconciliation implementation is corrected: | Accepted (Phase 81 corrective pass, 2026-10-07, direct user request, following post-completion review of the already-`done` Phase 81). **Refines, rather than reverses, `decisions/0071`/`0072`** — the architecture those two ADRs establish (canonical knowledge in `planning/knowledge/`, `context-graph.db` mechanical-only, zero new persisted canonical fields, dual-hash concurrency identity) is unchanged and remains approved. This ADR corrects nine real implementation defects a post-completion review found, none of which required reopening the architecture itself. |
| `0074-knowledge-layer-second-corrective-pass.md` | 0074. Phase 81's knowledge-reconciliation implementation is corrected a | Accepted (Phase 81 second corrective pass, 2026-10-07, direct user request, following further post-completion review of the Phase 81 corrective pass `decisions/0073` itself shipped). **Refines, rather than reverses, `decisions/0071`/`0072`/`0073`** — the architecture those three ADRs establish is unchanged and remains approved. This ADR corrects fourteen further implementation defects and gaps, all within the already-approved design. |
| `0075-knowledge-layer-third-corrective-pass.md` | 0075. Phase 81's knowledge-reconciliation implementation is corrected a | Accepted (Phase 81 third corrective pass, 2026-10-08, direct user request, following further post-completion review of the second corrective pass `decisions/0074` itself shipped). **Refines, rather than reverses, `decisions/0071`/`0072`/`0073`/`0074`** — the architecture those four ADRs establish is unchanged and remains approved. This ADR is an implementation correction already implied by `decisions/0074`'s own stale-manifest and apply-time-concurrency principles, not a new architectural decision: both defects below are the same invariant (detection/presence must be re-checked at apply time; concurrency identity must cover everything a reconciled edit actually depends on) applied more completely than `decisions/0074` itself managed to apply it. |
