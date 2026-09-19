# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Phase 61** (hledger cross-language experiment, done): fixed a real
  bug in already-tagged Phase 60 code —
  `HaskellAdapter.repository_url()` now sets
  `RepositoryLocation.subdirectory` for a monorepo member (previously it
  never set this field, so `resolve_and_clone` silently cloned the
  *whole* `hledger` monorepo into a single package's own
  `vendor/<name>/src/`, confirmed live; two new fixture tests, the
  existing live smoke test's own assertion updated). Tracked both
  `hledger-lib` and `hledger` (not `hledger-lib` alone — the real
  `balance`/`register`/`accounts`/`stats`/`print` command
  implementations live in the sibling `hledger` package) as real Haskell
  vendors in a disposable Ledgerkit scratch copy, via a real
  `codecompass sync --yes --budget 0` — confirmed live: `depends_on_edges`
  shows a real `hledger → hledger-lib` edge with zero new code.

  Ran a real, symmetric (recorded/verified commit hashes, byte-identical
  source, identical task/tools) two-agent comparison, scored
  two-part-plus-overall: **Part 1** (`depth:` behavioural
  reconstruction) — treatment PASS (Phase 54b's own was PASS WITH GAPS)
  at **LOW** context advantage, traced to `hledger` now being tracked as
  a vendor at all, not to anything the generated `CLAUDE.md`/`DEPTREE.md`
  explained; **Part 2** (cross-language equivalence recognition to
  Ledgerkit's own `DepthSpec`/`clip_account_name`) at **effectively
  NULL** advantage — Ledgerkit isn't a tracked vendor, so both agents
  worked from identical raw source. **Outcome shape (b)**: helped Part 1
  navigation marginally, did not materially help Part 2. Rediscovery
  comparison: **no measurable reduction**. A real, previously-unrecorded
  Ledgerkit correctness gap was found and empirically confirmed
  (`stats()`'s commodity count isn't depth-excluded the way hledger's
  real one is) — Ledgerkit's own issue, not acted on here.

  Three learnings filed and promoted: `L-026` (an adapter's generated
  digest answers "what exists," not "what it does" — a third independent
  occurrence) and `L-028` (`resolve_and_clone`'s `subdirectory` scopes
  the rendered view, not the raw clone) landed as new
  `architecture/overview.md` "Known footguns" bullets; `L-027` (a
  single-trial baseline/treatment comparison can't separate a tool's
  real contribution from agent-diligence variance) landed as a new
  ground rule in `planning/v1-redefinition/context-quality-evaluation.md`
  §1. Two context-observations filed (`OBS-015`, `OBS-016`). `usage.py`'s
  Haskell import detection investigated and **not built** — no real
  consumer in this phase's own task; the one relevant cross-vendor edge
  is already free via `depends_on_edges`. **Does not resolve GATE DD,
  does not complete or bypass Phases 55-59.** Retro:
  `planning/retros/phase-61-hledger-cross-language-experiment.md`.
  Evaluation:
  `planning/reference-projects/ledgerkit/03-hledger-cross-language-evaluation.md`.

- **Phase 60** (minimal external Haskell adapter, done): the reference
  implementation of a genuinely **external** CodeCompass adapter, built
  as two real, separate, publicly-hosted repositories —
  `codecompass-adaptor-protocol` (MIT — schemas/`SCHEMA.md`/examples/
  conformance vectors only, no code) and `codecompass-adaptor-haskell`
  (GPL-3.0-or-later, a real Stack project) — checked out as git
  submodules at `protocol/codecompass-adaptor-protocol/` and
  `adapters/haskell/` (`decisions/0057`, `decisions/0058`, `decisions/0059`).
  CodeCompass core gains `Ecosystem.HASKELL`, `discovery.py`'s
  `package.yaml` discoverer (real `PyYAML`), `external_process.py` (a
  fully generic JSON-Lines protocol client, zero ecosystem-specific
  knowledge), and `adapters/haskell.py` (a thin dispatcher — manifest
  reads plus monorepo package-root resolution, e.g. `hledger-lib/`
  inside the `hledger` monorepo — delegating dependency-tree/API-surface
  logic to the external process). `vendors.ecosystem` gains `'haskell'`
  via a new **non-destructive** migration (`_SCHEMA_VERSION` 7→8,
  table-rebuilt in place rather than dropped, protecting FK'd
  `vendor_enrichment`/`symbol_enrichment` rows). Phase 54c's
  evidence-backed workflow ran in full for Haskell API-surface
  extraction (`planning/knowledge/haskell-api-surface-extraction/`): the
  export-list scanner (`codecompass-adaptor-haskell`'s own
  `Adapter.Scanner`) handles bare/`Type(..)`/section-header/
  commented-out entries, `module <Name>` re-exports (with file-local
  alias resolution), CPP-gated entries (flagged `undetermined`, never
  guessed), the package's own `exposed-modules` filter, no-export-list
  detection, and two-pass purpose-pairing by body location — all six
  `REQ-HSAPI-*` records `verified` against real, live output. A real
  `codecompass sync` against `hledger-lib` (the pinned reference corpus)
  independently confirmed correct: its 48-name `Hledger.Data.AccountName`
  export set matches live `stack ghci :browse` output exactly. One real,
  disclosed gap found and routed, not fixed here by direct instruction:
  `sync.py::_collect_vendor_symbols` doesn't yet ingest an external
  adapter's own structured symbols into `context-graph.db`'s `symbols`
  table (`CG-008`, routed to Phase 62). New docs:
  `docs/external-adapters.md` (clone/submodule setup, version-
  compatibility matrix). **Does not resolve GATE DD and does not
  complete or bypass Phases 55-59**, which remain open. Retro:
  `planning/retros/phase-60-minimal-haskell-adapter.md`.

- **Phase 54c** (evidence-backed, knowledge-based, documentation-first
  workflow, done): a bounded, reversible experiment introducing a
  file-based Observation/Evidence/Claim/Derivation/Decision/Requirement
  model (`planning/knowledge/<feature-slug>/`), two new agent roles
  (`context-researcher`, `documentation-agent`) and a new
  packet-assembly mode on the existing `knowledge-curator` — no
  `context-graph.db` schema change beyond one incidental CHECK-enum
  value. **`doc_artifacts.origin` gains `pinned_reference`**
  (`_SCHEMA_VERSION` 6→7): `src/codecompass/spec_docs.py::scan_spec_docs`
  now automatically detects externally-sourced, revision-pinned
  reference material via a leading YAML frontmatter block carrying both
  a `resolved_commit` and a `source_url` key
  (`_has_pinned_reference_frontmatter`), instead of unconditionally
  assigning `origin='project'`. Closes `CG-004`'s sibling gap `CG-005`
  — verified via a real `codecompass sync` against Phase 54b's own
  scratch Ledgerkit copy: all 19 real ingested
  `dev-docs/hledger-reference/*.md` files now correctly read
  `origin='pinned_reference'`, while Ledgerkit's own hand-authored docs
  correctly stay `project`. Full research/design/review/packet trail
  and a retroactive knowledge→documentation fidelity check (against
  Phase 54b's `depth:` findings, matching Ledgerkit's real shipped
  outcome) are recorded under `planning/knowledge/`; a fresh-agent
  traceability test passed for real. Two real process gaps found and
  promoted: `L-023` (a newly-created agent type may not be immediately
  dispatchable mid-session) and `L-024` (a context packet's own
  "existing tests" section must check for schema/migration-mechanism
  test files, not just feature-code tests). The retro explicitly leaves
  two of the plan's ten evaluation questions unanswered rather than
  claiming untested success, and defers whether the workflow improves
  development quality generally to Phase 60/61's own genuine-uncertainty
  test. New tests: `tests/test_spec_docs.py` (4), `tests/test_graph.py`
  (2, mirroring the established Phase 17/21/27 enum-widening pattern).
  New tool: `scripts/check_knowledge_base.py`. No new ADR. See
  `planning/phase-54c-evidence-knowledge-workflow.md` and
  `planning/retros/phase-54c-evidence-knowledge-workflow.md`.

- **Phase 54b** (LedgerKit behavioural-understanding experiment, done):
  extended Phase 54's reference-ingestion pipeline with 11 new
  manual/source selections (all line ranges reconfirmed live against the
  pinned hledger clone) covering hledger's `depth:`/`--depth` behaviour
  across `balance`/`register`/`accounts`/`stats`/`print`. Two fresh,
  independently-dispatched agents (never the lead, who had already read
  Ledgerkit's real Stage C Phase 5 material to write the plan) ran the
  identical real task: a baseline with no CodeCompass, and a treatment
  using the new material indexed into a scratch Ledgerkit copy (pinned
  at real `HEAD` `c6168b2`). **Both reached the fully correct, complete
  answer** — three distinct behaviours (clip/aggregate for
  `balance`/`register`/`accounts`; genuine partial exclusion for
  `stats`; total inertness for `print`), independently confirmed by
  `context-evaluator` against the real pinned source/manual/binary:
  **baseline PASS, treatment PASS WITH GAPS, context advantage LOW** —
  the curated set omitted `Stats.hs` entirely (the one file covering the
  task's genuine exception), forcing a disclosed fallback exactly where
  it mattered most, while the baseline never hit that gap. Mechanical
  `codecompass query relations` again returned **zero** edges for all 19
  indexed files, even with `CG-004`'s fix live — a second, independent
  confirmation of `CG-006`/`OBS-008`'s structural ceiling. Both runs
  rated **complete** on the new execution-path-completeness criterion —
  neither reproduced Ledgerkit's own real, dated Stage C Phase 1
  premature-conclusion mistake, an honestly-reported negative result for
  the specific failure mode this phase was designed to catch. A real
  methodological near-miss was caught and fixed before either agent ran:
  an early draft of the extracted material's own labels/notes stated the
  correct answer directly (e.g. "THE TRAP", "THE EXCEPTION"), which
  would have silently invalidated the entire comparison — promoted as
  `L-022` into `reference-project-protocol.md` §2.4. Filed `CG-007`
  (symbol-level cross-references between pinned reference excerpts have
  no representable relation kind), `OBS-013`, `OBS-014`. No
  `src/codecompass/` change. See
  `planning/reference-projects/ledgerkit/findings.md`'s "Phase 54b"
  section and `planning/retros/phase-54b-ledgerkit-behavioural-understanding.md`.

### Planned

- **Phase 54c plan: evidence-backed, knowledge-based,
  documentation-first workflow** (planning only, no code, phase not
  started): a minimal, file-based (not `context-graph.db`)
  Observation/Evidence/Claim/Derivation/Decision/Requirement model
  (`planning/knowledge/<feature-slug>/`) plus a development workflow —
  Context Researcher → knowledge map → Documentation Agent →
  user-facing design document → user review gate (DRAFT → RESEARCHED →
  USER REVIEW → APPROVED → IMPLEMENTING → VERIFIED) → approved context
  packet → coding agent → behavioural revalidation → retro — usable for
  both CodeCompass's own development and downstream projects like
  Ledgerkit. Generalises `decisions/0051`'s and `decisions/0054`'s
  already-proven "agent-derived content stays outside the graph until
  promoted" boundary from graph edges/enrichment specifically to
  general behavioural knowledge; adapts Ledgerkit's own real
  `dev-docs/compat-register/*.yaml` evidence-kind/status shape as the
  direct template. Bounded proving case: `CG-005` (the `origin` enum
  extension, primary — small enough for a full loop within one
  experimental phase) plus a retroactive, no-new-dispatch check of
  Phase 54b's own `depth:` evidence against Ledgerkit's real, shipped
  outcome as a known-correct answer (secondary). Numbered as a bridge
  phase (54c) informing, not pre-empting, GATE DD (Phase 55). No new
  `context-graph.db` schema change beyond one incidental CHECK-enum
  value; no universal ontology, RDF/OWL, confidence scoring, or MCP
  work. **Amended 2026-09-18**, before implementation: Evidence made
  strictly neutral (support/contradict lives only on the Claim); a
  Decision can never supersede a Claim (only another Decision — a
  factual correction to observed behaviour is always a new Claim, never
  a Decision); user-run tests are first-class Observation/Evidence;
  `design.md`'s citation obligation is one-directional (every assertion
  resolves to knowledge, not every stored Claim need surface); resolved
  to two new agent roles (Context Researcher, Documentation Agent) plus
  an extended `knowledge-curator` packet-assembly mode, not three new
  roles; added a `packet-sufficiency.md` log measuring whether the
  packet actually reduces rediscovery; the two proving cases are now
  explicitly framed as testing workflow mechanics and documentation
  fidelity respectively, not final proof of the methodology, with Phase
  60/61 named as the first genuine-uncertainty test. See
  `planning/phase-54c-evidence-knowledge-workflow.md` and
  `planning/phase-54c-evidence-knowledge-workflow-prompt.md`.

- **Phase 54b plan: behavioural-understanding experiment** (planning
  only, no code, phase not started): expands Phase 54b's one-paragraph
  placeholder into a full plan
  (`planning/phase-54b-ledgerkit-behavioural-understanding-experiment.md`)
  using Ledgerkit's real Stage C Phase 5 evidence (`c6168b2`) — hledger's
  `depth:` query term resolves to three distinct behaviours across five
  commands (clip for balance/register/accounts, full depth-blindness for
  `print`, genuine exclusion for `stats`), and Stage C Phase 1 made a
  real, dated premature-conclusion mistake (classified from one
  function's signature without tracing any command's actual consumption)
  corrected only by a full six-file source trace at Phase 5. Refines the
  phase's objective to: test whether CodeCompass context helps an agent
  reach an execution-path-complete conclusion and avoid that exact
  mistake, using only existing mechanisms (Phase 54's reference-ingestion
  pipeline, the context-gap/context-observation queues,
  `context-evaluator`, plus one new phase-scoped evaluation criterion —
  "execution-path completeness" — not folded into the shared
  `context-quality-evaluation.md` instrument). No new ontology, claim
  system, or execution graph. Findings feed GATE DD's existing
  executable-kind (§2.2 → Phase 56) and provenance (§2.4 → Phase 57)
  hypothesis rows, not a new one, and carry forward as named design
  questions for Phase 60 (adapter API-surface sufficiency for
  entry-point tracing) and a refined Phase 61 (cross-language
  behavioural comparison via the same `depth:` case, not just "does the
  adapter parse Haskell"). Existing phase numbering/sequencing preserved
  throughout; no new ADR (refines scope inside `decisions/0056`'s
  existing framework). See `planning/phase-54b-ledgerkit-behavioural-understanding-prompt.md`
  for the full verbatim request.

- **Roadmap revision: cross-language validation strategy** (no phase
  number — planning/documentation only, no code): `decisions/0056`
  replaces Technical Clipper as Stage F's required cross-project
  validation target with a deliberately small Haskell `EcosystemAdapter`
  spike validated against hledger/Ledgerkit — already CodeCompass's
  central reference project, with a real Haskell toolchain (Stack
  3.11.1) confirmed available in this environment, unlike the still-
  stalled Cargo-toolchain situation (`decisions/0014`). Revised sequence:
  new bridge phase **54b** (LedgerKit reference/behaviour validation,
  Stage D) → Phase 60 (minimal Haskell adapter) → Phase 61 (hledger
  cross-language experiment) → Phase 62 (adapter-interface
  consolidation) → Phase 63 (lightweight ordinary-project smoke test,
  Technical Clipper now merely an optional candidate there, not
  dropped) → Phases 64-70 unchanged (Stage G v1 consolidation; Phase
  67's description now names the Stage F smoke test generically rather
  than Technical Clipper specifically). Rust and JavaScript/npm adapter
  maturation work is demoted to later, non-near-term ecosystem-expansion
  work — not required to drive v1 architecture or validation. Stage E
  (Phases 56-59, GATE DD) is explicitly untouched — a different axis of
  generalisation. Rationale: a new-ecosystem adapter validated against
  an already-central codebase is a stronger test of the future modular
  adapter architecture (potentially independently-licensed Python,
  Haskell, and proprietary COBOL adapters) than a same-ecosystem
  (TypeScript/npm) regression against Technical Clipper, whose own
  ecosystem CodeCompass already ships support for. See `decisions/0056`
  and `planning/v1-redefinition/roadmap.md` Stage F. Technical Clipper's
  registration/protocol material is preserved, not deleted, for optional
  later use.

- **Evidence-reconciliation planning session** (no phase number —
  planning only): reconstructed current CodeCompass and Ledgerkit state
  fresh from both repositories (Ledgerkit had advanced 5 commits past
  the pin every prior evaluation used). Recovered Ledgerkit's own
  first-ever real consumer-side CodeCompass evidence
  (`validation/codecompass/findings/CC-LK-001`, its live-repo `-q`/
  `--query` integration task) — PASS WITH GAPS, LOW advantage,
  independently corroborating Phase 54's `CG-004` (doc-to-doc relation
  gap) and `CG-003` (executable/behavioural evidence gap) from a
  genuinely different angle. Built a reconciliation matrix and
  recommends one small, doubly-corroborated fix (populate
  `doc_artifacts.name` for `spec_doc` rows) for implementation, with
  everything larger (executable-evidence representation, pinned-
  reference productisation) explicitly deferred pending cross-domain
  evidence. See `planning/phase-55-evidence-reconciliation.md`. **No
  code changed; a real phase-numbering conflict was surfaced, not
  silently resolved, for the user to decide.**

### Fixed

- **Phase 55b** (a bridge phase, not part of the Phase 55/Stage E
  sequence): `spec_docs.py::scan_spec_docs` now populates
  `doc_artifacts.name` for every `spec_doc` row (its own first H1
  heading, or filename stem, gated by a genericity check rejecting a
  bare single word like a project's own root README's `# ledgerkit`) —
  closing `CG-004`, doubly-corroborated by Phase 54's own experiment and
  Ledgerkit's independent, real-live-repo `CC-LK-001` finding.
  `doc_mapping.py::build_doc_relations_edges` gained a self-mention
  exclusion for `mentions_artifact` (a titled doc's own heading
  otherwise trivially matches itself). `sync.py`'s real production call
  now includes `spec_doc_rows` as a `mentions_artifact` target — the
  wiring gap a first implementation attempt missed, caught by an
  independent `context-evaluator` round-1 FAIL before it shipped, fixed,
  and re-verified in round 2 (PASS WITH NON-BLOCKING OBSERVATIONS) via a
  real before/after against the live Ledgerkit repository: 3 genuine
  edges now appear, zero false-positive noise. `CG-006` (matches by
  title text only, never filename) filed as a small, honestly-disclosed
  residual limitation, not claimed to be fixed by this change.

### Added

- **Phase 54** (heterogeneous reference-material experiment): a real,
  tested Git-backed reference-ingestion pipeline
  (`planning/reference-projects/ledgerkit/reference-experiment/`,
  deliberately outside `src/codecompass/` — evidence-gathering for
  Phase 55/GATE DD, not a shipped feature), resolving a human-friendly
  hledger tag to an exact pinned commit and extracting selected
  manual/source sections with content-hash provenance. Tested against
  one genuine Ledgerkit Stage C task (the `tag:` query-semantics brief,
  explicitly deferred there) with an independently-evaluated
  baseline-vs-treatment comparison: **treatment FAIL, baseline PASS
  WITH GAPS, context-advantage LOW** — not a mechanism failure but a
  real, caught-and-fixed extraction-boundary defect (a hand-drawn line
  range silently excluded a documented rule its own description claimed
  to include). Filed real findings: detection generalises to ingested
  content with zero schema change; mechanical `mentions_artifact`
  relation detection structurally cannot relate two `spec_doc`
  artifacts; the `origin` enum has no value for externally-pinned
  reference material; a working YAML-evidence-citation-matching relation
  fallback was demonstrated real (against Ledgerkit's own already-
  published compat-register data) but isn't wired into CodeCompass's
  graph. Resolves the Stage D-vs-Stage-F/G strategic decision (Phase
  51's retro) in Stage D's favour, by having actually run the test —
  genuinely mixed evidence, not a clean mandate either way. No
  `src/codecompass/` change.

### Removed

- **Phase 53** (legacy feature rationalisation): `discovery.py::
  rewrite_vendor_toml`, dead code with zero callers since the `promote`
  command's Phase 15 retirement (`decisions/0033`), plus its dedicated
  test. Reached via a full feature inventory (CORE / AGENT / HOST-OUTPUT
  ADAPTER classification) and redundancy map covering every runtime
  module — see `planning/phase-53-legacy-feature-rationalisation-plan.md`.
  At the review gate, direct-API vendor/symbol/relation enrichment and
  the `chat` REPL were both explicitly kept unchanged (real,
  non-hypothetical value; no evidence either is a problem), and two
  small duplication/naming findings were deferred to a documentation
  note rather than new tooling.

### Changed

- **Contributor licensing terms** (`decisions/0055`): `CONTRIBUTING.md`'s
  `## License` section now includes an explicit grant — a contributor
  retains copyright but grants the project owner an irrevocable,
  worldwide, royalty-free licence broad enough to relicense the
  contribution, including under proprietary terms — replacing the prior
  "no separate CLA" sentence. This preserves the project owner's ability
  to offer CodeCompass under alternative or commercial licence terms in
  future; it does not affect CodeCompass's own current licence
  (GPL-3.0-or-later) or any existing user's rights under it, and nothing
  has been contributed externally to date for it to apply to
  retroactively. `README.md`'s `## License` section gains a short,
  prominent pointer to this term. Documentation-only; no `src/` change.
- **Phase 53**: `architecture/overview.md` gains a new "Module tiers:
  CORE, AGENT, HOST-OUTPUT ADAPTERS" section naming the project's
  existing (previously implicit) module grouping, plus a one-sentence
  disambiguation of "adapter" (the ecosystem package-manager sense,
  `src/codecompass/adapters/`) from the phase's new "host-output
  adapter" sense (Claude Skills, `CLAUDE.md`, Cursor `.mdc`), plus a
  caveat naming the tool-level Skill / `/discovery` / `docs/
  cli-reference.md` `query`-subcommand-list triplication as a known,
  hand-synced maintenance burden.

### Added

- **Phase 52** (context edge lifecycle): a new `planning/context-observations/`
  queue generalises `context-use-log.md` (4 original entries migrated
  verbatim, reshaped with an explicit edge-correctness/task-usefulness
  split), and **agent-driven enrichment lands as a second,
  non-authoritative producer alongside the existing batched-API path**
  (`decisions/0054`), for use when no `ANTHROPIC_API_KEY` is available.
  `relation_enrichment.py::apply_results` gains a backward-compatible
  `model` keyword parameter (default unchanged; every existing call site
  and test unaffected). New CLI command `codecompass enrich apply` takes
  a JSON file of agent-authored `{source_doc_path, ai_summary,
  relation_label, ...}` entries plus `--agent <name>`, and **mechanically
  enforces the trust boundary itself**: it only accepts entries matching
  a currently-pending `relation_enrichment.select_candidates()` row,
  building the stored result from that candidate's own `content_hash`
  (never an agent-supplied one) — an agent cannot enrich a relationship
  that isn't already mechanically proven and pending. New agent role
  `.claude/agents/context-enrichment-agent.md` (the roster's ninth):
  reads pending candidates, writes grounded interpretive content from
  real excerpted source text, calls `enrich apply`; never invents a
  relationship, never touches a graph-fact table directly, no
  `src/codecompass/` writes. Demonstrated live, twice, against a new
  local fixture (`tests/fixtures/ledgerkit_lifecycle_demo/`, mirroring
  Ledgerkit's own real, previously-observed Skill-mention pattern) —
  deliberately not the live Ledgerkit clone, per explicit user
  direction — proving the `enrich apply` rejection path, the enrichment
  cache surviving a byte-identical mechanical graph rebuild, and a
  genuine stale-edge resubmission rejection. One real, honestly disclosed
  complication (a fixture-bootstrap content-hash artifact) was
  root-caused live and filed as a candidate learning (`L-019`). `pytest`
  567 passed / 2 skipped (+10), `ruff check .` clean, `check_user_docs.py
  --strict` clean. `docs-reconstructor` drift audit → DRIFT, 2
  non-blocking findings, both fixed before commit; `release-phase-auditor`
  → PASS WITH NON-BLOCKING OBSERVATIONS, including independently
  live-reproducing the two-cycle demonstration itself. This phase's scope
  came from a direct user request, not from resuming Stage D's own
  dogfooding fork — the Stage D-vs-Stage-F/G strategic decision (Phase
  51) remains open, unaffected.

- **Phase 51** (Stage C's closing phase — **GATE DC**): re-ran Phase 45's
  baseline Q2 and Phase 46's genuine task — same questions, same
  instrument — against Ledgerkit re-pinned at `05218e3` (its own Stage C
  Phase 1 had since landed, producing a brand-new file), to measure
  whether Phase 49's fix actually improved context quality. **Both
  original FAIL verdicts moved to PASS WITH GAPS**, and "would this have
  misled the agent" moved from yes to no for both — independently
  re-verified by `context-evaluator` via direct inspection and its own
  `codecompass`/`sqlite3` commands, not assumed from the fix landing.
  **Confirmed the fix generalises**: the new
  `17-query-semantics-brief.md` (didn't exist at Phase 46's pin) is also
  correctly tracked. **Advantage stayed LOW**: `query relations` only
  does literal vendor/Skill name-mention detection, and Ledgerkit has 0
  tracked vendors, so it structurally cannot surface a doc's actual
  content — the ceiling on this question class wasn't raised, and the fix
  was never scoped to raise it. Phase 49's fix is judged a success **on
  its own, narrow terms**, validating rather than calling into question
  the earlier "smallest justified fix" judgment (rejecting a more general
  configurable-glob mechanism). `planning/reference-projects/ledgerkit/findings.md`
  GATE DC section appended with the before/after comparison. **This
  completes Stage C in full** (Phase 48/50 not funded, Phase 49 done,
  Phase 51 done). No `src/codecompass/` change (measurement only). As a
  closeout addendum, resolved a Phase-47-committed revisit decision this
  phase's own scope hadn't touched: `L-015` stays `retained` (genuinely
  out of scope across five intervening phases; revisit trigger updated);
  `L-012` moved `retained` → `discarded` (7 phases old, three unclaimed
  corroboration opportunities, self-test-only by design — the lifecycle's
  "~3 phases, no new evidence" norm applied). `docs-reconstructor` drift
  audit → NO DRIFT; `release-phase-auditor` → PASS WITH NON-BLOCKING
  OBSERVATIONS (the one genuine gap it flagged — the dangling
  `L-012`/`L-015` commitment — is the addendum resolved above). `pytest`
  557 passed / 2 skipped, `ruff check .` clean, `check_user_docs.py
  --strict` clean. **Whether to continue into Stage D or proceed toward
  Stage F/G is a genuine strategic decision surfaced to the user, not
  resolved by this phase.**

### Fixed

- **Phase 49** (Stage C's first phase — GATE DB's funded fix): closes
  `CG-002` and `L-016`, both consolidated at Phase 47's GATE DB.
  `spec_docs.py::_DEFAULT_GLOBS` gains `"dev-docs/**/*.md"` — the exact
  Phase 37 `ai-docs/**/*.md` precedent applied a second time, this time
  from external Ledgerkit evidence (Phases 45/46). `cli.py::query_relations`'s
  not-found branch now calls a new `_relations_not_found_error`: a real
  on-disk file that simply wasn't detected as a spec/vendor doc gets an
  explicit, mechanism-naming message pointing at spec-doc glob coverage,
  instead of an authoritative-sounding bare "not found" indistinguishable
  from a genuine typo; `query vendor`/`query symbol`'s "not found" paths
  are untouched, correctly, since file-existence checking doesn't apply
  to a vendor/symbol name. **This is CodeCompass's first
  `src/codecompass/` change driven by external reference-project
  evidence** — the redefined v1's central hypothesis (`decisions/0048`)
  made concrete for the first time since Phase 43a's own-repo dogfood. 3
  new tests. Live-verified against the real Ledgerkit clone, independently
  reproduced by both the lead and the auditor from scratch: `dev-docs/`
  files (including a nested path) now resolve to an honest empty
  relations table instead of "not found"; a genuinely nonexistent name
  keeps the plain message; a still-uncovered real file
  (`knowledge/DOMAIN_RULES.md`) correctly triggers the new disambiguated
  message, confirming the fix generalises beyond the one directory it was
  evidenced against. `docs-maintainer` reconciled `architecture/overview.md`
  (glob enumeration) and `docs/cli-reference.md` (`query relations`
  error-behavior description). `docs-reconstructor` drift audit → NO
  DRIFT (also caught, and the lead fixed before commit, a mistaken ADR
  citation in `_relations_not_found_error`'s docstring); `release-phase-auditor`
  → PASS WITH NON-BLOCKING OBSERVATIONS (no blocking gap). `CG-002` stays
  `promoted-to-roadmap` with a closing note confirming the fix landed;
  `L-016` flipped `retained` → `promoted`. `pytest` 557 passed / 2 skipped
  (+3), `ruff check .` clean, `check_user_docs.py --strict` clean.

### Added

- **Phase 47** (Stage B's fourth and final phase — **GATE DB**): pure
  synthesis, no new evaluation. `knowledge-curator` bulk-reviewed every
  Phase 44–46 candidate learning and `context-gaps` entry and produced
  `planning/reference-projects/ledgerkit/findings.md` — 5 evaluated
  question/task instances, **2 formal FAIL verdicts** (both listed in
  full per the aggregation rule), **100% LOW context advantage** across
  every instance (two explicitly negative), and the `_DEFAULT_GLOBS`
  detection blind spot confirmed at **3 independent occurrences** (Phase
  37 own-dev, Phase 45 + 46 externally on Ledgerkit). **GATE DB ratified
  by the user** ("Ratify as recommended"): fund one narrow Stage C phase
  closing `CG-002` (`dev-docs/**/*.md` glob coverage) + `L-016`
  (`query relations` not-found disambiguation) —
  `planning/phase-49-spec-doc-coverage-and-error-disambiguation.md`,
  matching the roadmap's own pre-written Phase 49 sketch, not Phase 48's;
  Phase 48 (task-oriented context retrieval) and Phase 50 (shared-agent
  context/entry points) explicitly **not funded** — no corroborating
  evidence in the Phase 44–46 dataset; a more general
  `vendor.toml`-configurable spec-doc glob list explicitly rejected as
  premature at this evidence threshold; `CG-003`/`L-017` explicitly
  routed to Stage E/Phase 53, not this gate. `CG-002` moved to
  `promoted-to-roadmap`; `L-016` stays `retained` until Phase 49's fix
  actually lands. A genuine, unrelated pre-existing doc-drift fix landed
  as a side effect: `architecture/overview.md`'s `_DEFAULT_GLOBS`
  enumeration was missing the Phase 37 `ai-docs/**/*.md` addition,
  flagged-but-deferred by two prior phases' `docs-maintainer` reviews and
  finally corrected here, verified item-for-item against the real code.
  No other `src/codecompass/` change this phase (Phase 49 is
  CodeCompass's first `src/` change driven by external reference-project
  evidence). `docs-reconstructor` drift audit → NO DRIFT;
  `release-phase-auditor` → PASS WITH NON-BLOCKING OBSERVATIONS (no
  blocking gap). `pytest` 554 passed / 2 skipped, `ruff check .` clean,
  `check_user_docs.py --strict` clean.

- **Phase 46** (Stage B, third phase): ran the full per-task procedure
  (`reference-project-protocol.md` §2.4) against a genuine, live Ledgerkit
  task for the first time. Reconfirmed the task live at phase start, as
  hedged by the plan: Ledgerkit's own Stage B closed to `[DONE]` and Stage
  C opened within a day of Phase 45's pinned commit, so the task actually
  run was hledger 1.52 query-term semantics, not the plan's named
  compat-register-migration candidate. Because a real, concurrently-running
  Ledgerkit development session was producing the task's exact
  deliverable, the attempt was conducted as a read-only evaluation
  exercise — no file was written into the Ledgerkit clone.
  `planning/reference-projects/ledgerkit/01-query-semantics.md` —
  **CodeCompass's second FAIL verdict**, LOW (negative) advantage, and the
  first on genuinely in-progress work rather than a spot-check question:
  CodeCompass returned a complete blank (0 vendors, "not found" for both
  `dev-docs/` files), while Ledgerkit's own
  `dev-docs/planning/core-redefinition/07-query-regex.md` §7.1 already had
  the complete answer, found by one `grep` + file read. **`CG-002`**
  re-confirmed independently by both `reference-project-tester` and
  `context-evaluator`, extended to nested `dev-docs/**` paths. A new,
  structurally distinct gap, **`CG-003`**, filed: the external hledger.org
  manual itself has zero CodeCompass representation, no glob fix could
  ever cover it (`candidate`). Candidate learning **L-017** filed
  (retained): a live `WebFetch` fallback against the real hledger.org
  manual needed two attempts and still couldn't reliably extract the
  relevant section — a retrieval-cost finding for Phase 53's
  manual-as-fetched/vendored-text design question. A process incident
  surfaced during the phase (dispatching two agents to `Write`, not
  `Edit`, the same shared report file concurrently silently clobbered one
  agent's output) was filed as candidate learning **L-018** and
  **promoted** the same phase: `planning/agent-led-workflow.md` step 5 now
  explicitly forbids two agents `Write`-ing one shared path concurrently.
  `planning/phase-47-consolidate-findings.md` written — Stage B's decision
  phase (GATE DB), with a full evidence inventory assembled from Phases
  44–46. No `src/codecompass/` change. `docs-reconstructor` drift audit →
  NO DRIFT; `release-phase-auditor` → PASS WITH NON-BLOCKING OBSERVATIONS
  (no blocking gap). `pytest` 554 passed / 2 skipped, `ruff check .`
  clean, `check_user_docs.py --strict` clean.

- **Phase 45** (Stage B, second phase): registered **Ledgerkit** as
  CodeCompass's first external reference project and produced its first
  baseline evaluation. `planning/reference-projects/ledgerkit.md`
  (registration record, live-reconfirmed against a pinned commit —
  Ledgerkit's own "Core redefinition" landed the same day as the desk
  assessment it supersedes: Milestone 5 "CLI Filter Flags" is now
  `[SUPERSEDED]`) and `ledgerkit/00-baseline.md` (3 baseline
  context-quality questions). **Q2 is the redefined-v1 effort's first-ever
  FAIL verdict**: `codecompass query relations
  dev-docs/hledger-compatibility.md` returned a confident "not found in
  context-graph.db" for a real, current, 238-line file that is precisely
  Ledgerkit's own designated hledger-1.52-compatibility governance
  document, rather than an honest empty result. Root cause —
  `spec_docs._DEFAULT_GLOBS` has no `dev-docs/**/*.md` entry — filed as
  candidate context-gap **CG-002** (`recurred`: the same failure shape as
  Phase 37's `ai-docs/` glob fix, this time surfaced by an external
  project). A distinct symptom-layer finding — `query relations`'s "not
  found" error is indistinguishable from a genuine typo — filed as
  candidate learning **L-016** (retained). Q1's finding — `query vendors`
  gives no signal that `[project.optional-dependencies]` exist but are
  unscanned — filed as **L-015** (retained). Q1 and Q3 both verdict PASS
  WITH GAPS / advantage LOW, honest expected-thin results. The
  `context-health-planner`'s first genuine solo run
  (`planning/context-health.md`) predicted LOW context-advantage for
  Phase 46, with CG-002 directly load-bearing. `planning/phase-46-
  ledgerkit-tasks.md` written, explicitly hedged since Ledgerkit's own
  Stage B isn't yet scoped/approved and its roadmap already moved once
  mid-Phase-45. No `src/codecompass/` change. `docs-reconstructor` drift
  audit → NO DRIFT; `release-phase-auditor` → PASS WITH NON-BLOCKING
  OBSERVATIONS (no blocking gap). `pytest` 554 passed / 2 skipped, `ruff
  check .` clean, `check_user_docs.py --strict` clean.

- **Phase 44** (Stage B's first phase): the reference-project protocol and
  context-quality evaluation spec are now operational, not just prose.
  New `planning/reference-projects/README.md` (registry + "how an
  evaluation runs"), `TEMPLATE-registration.md`, `TEMPLATE-evaluation.md`.
  A real instrument dry-run (`_instrument-dry-run.md`) evaluated
  CodeCompass's own `typer` usage against itself — verdict **PASS WITH
  GAPS**, advantage **LOW**: every claim checked out against direct
  inspection, but a single-symbol `query symbol` call undersold `typer`'s
  actual usage breadth (the option/argument/exit/confirm surface, not
  just the two `Typer()` construction sites) — filed as candidate
  learning **L-012** (retained). The `context-evaluator` and
  `reference-project-tester` agent briefs were verified already
  consistent with the new templates (finalised as a side effect of Phase
  43c; no edit needed). `planning/phase-45-ledgerkit-baseline.md` written,
  retargeted to Ledgerkit's real current state (Milestone 5 "CLI Filter
  Flags" `[PLANNED]` next). Process amendment from candidate learning
  **L-013** (promoted): `planning/agent-led-workflow.md` step 10 is now
  an explicit *interim* roadmap/context reconciliation (never flips
  `ROADMAP.md` to `done`); step 14 is the *final* done-flipping
  reconciliation, run only after the retro/triage/audit steps. No
  `src/codecompass/` change. `docs-reconstructor` drift audit → NO DRIFT;
  `release-phase-auditor` → PASS WITH NON-BLOCKING OBSERVATIONS (both
  notes resolved/accounted for, no blocking gap). `pytest` 554 passed / 2
  skipped, `ruff check .` clean, `check_user_docs.py --strict` clean.

### Changed

- **BREAKING (licensing): Phases 43d + 43e** — gates G11/G12/G13 approved
  ("Proceed as recommended", 2026-09-12), executed the same session.
  **CodeCompass is now licensed GPL-3.0-or-later (was MIT)** — `LICENSE`
  replaced with the canonical GPL-3.0-or-later text (fetched verbatim
  from `hledgerorg/hledger`'s own `LICENSE` file, unmodified per the
  FSF's own instructions, plus a CodeCompass copyright/notice block);
  `pyproject.toml`'s `license` field and classifier updated (verified
  live: `pip install -e .` + `pip show codecompass` reports
  `License: GPL-3.0-or-later`); `README.md` and `CONTRIBUTING.md` gain
  License sections pointing at the rationale. `decisions/0052` (Ledgerkit
  is the next reference project, ratifying gate G11 — no file changes
  beyond the already-amended planning docs from the prior commit) and
  `decisions/0053` (the relicensing itself, ratifying gate G12) written
  as `Accepted`, superseding their proposed drafts in
  `proposed-governance-changes.md` §C. `planning/v1-redefinition/adoption-blueprint.md`
  approved as the version handed to Ledgerkit (gate G13, Phase 43e) — no
  content change from the prior commit, just the gate resolving.
  **Nothing published/tagged is affected** — no git tag exists, nothing
  has ever shipped to PyPI, so no historical release needs
  reconciling; individual past commits remain, as a historical fact,
  made under MIT at the time. `docs-reconstructor` drift audit → **NO
  DRIFT**; `knowledge-curator` triage filed **L-009** (fetch
  canonical upstream text for byte-fidelity, retained) and **L-010** (a
  reusable document should cite its justifying incidents + state a
  revision policy, retained). No `src/codecompass/` change, no test
  change; `ruff check .` clean, `python scripts/check_user_docs.py
  --strict` clean.

- **2026-09-12 realignment** (planning only — `planning/v1-redefinition/realignment-2026-09.md`,
  gate G11): reassessed and reordered the remaining redefined-v1 roadmap.
  **Ledgerkit is now Stage B** (the first external reference project;
  was Technical Clipper) — its dependency shape (the `hledger` executable,
  its manuals, journal syntax, query semantics, compatibility tests,
  intentional divergences) is the stronger test of CodeCompass's
  distinctive value, confirmed by live re-inspection this session:
  `hledger` is `GPL-3.0-or-later` (confirmed at the SPDX-field level),
  currently stable at 1.52.4 (1.99.x is a preview); Ledgerkit is MIT,
  single-copyright-holder, with a genuine next task already scoped on
  its own roadmap (Milestone 5, "CLI Filter Flags"). **Technical Clipper
  moves to a new Stage F** (cross-ecosystem regression, run after
  Ledgerkit-driven changes land, to check they generalise rather than
  overfit to accounting/hledger). Phases 39–43c are unchanged, `done`,
  not renumbered; phases 45–67 (none started — confirmed:
  `planning/reference-projects/` doesn't exist yet) are renumbered
  45–70 to make room for the new stage. GATE letters DB/DC/DD/DE keep
  their conceptual position (now scoped to Ledgerkit evidence); a new
  **GATE DF** covers Technical Clipper's regression decision.
  Two new Stage-A bridge phases: **43d** (GPL-3.0-or-later relicensing
  plan — CodeCompass is currently MIT, single copyright holder, no
  bundled third-party source, no other contributors to consult; the
  actual `LICENSE`/`pyproject.toml`/`README.md` edits are held behind
  **gate G12**, not made this session) and **43e** (a reusable agent-led
  adoption blueprint, extracted from CodeCompass's own 8-agent working
  practice, for Ledgerkit — and later projects — to adopt; **gate G13**).
  New planning artifacts: `licence-migration.md`, `adoption-blueprint.md`,
  `codecompass-feedback-ingestion.md` (the standard finding format +
  review process for a reference project's context-curator findings —
  Ledgerkit discovers problems, CodeCompass generalises them, promotion
  is never automatic). Draft ADRs `decisions/0052` (the reorder) and
  `decisions/0053` (the relicensing) staged in
  `proposed-governance-changes.md` §C, not yet written to `decisions/`.
  Amended for consistency: `ledgerkit-plan.md` (promoted from Stage D to
  Stage B, phase numbers), `reference-project-protocol.md` (Technical
  Clipper's specifics repositioned as Stage F), `conditional-generalisation.md`
  (flagged that Technical-Clipper-sourced evidence rows are now
  unavailable at GATE DD's original timing), `context-quality-evaluation.md`,
  `migration.md`, the package `README.md` (§1.6/1.7 swapped, §3's roadmap
  summary reordered, gates/risks tables extended). **No implementation
  from this realignment** — `CLAUDE.md` untouched, no `src/` change, no
  file under gate G12/G13 touched, `python scripts/check_user_docs.py --strict`
  clean throughout.

### Fixed

- **Phase 43b**: 4 self-contradictory passages in `architecture/overview.md`
  (catalogued as items 33-36 in
  `planning/v1-redefinition/architecture-split-candidates.md` §C,
  candidate learning L-004) described removed code as live, each verified
  against `src/` and corrected: a "grounded description is regenerated on
  every `sync` run" footgun deleted outright (`sync_vendor` never makes an
  AI call — confirmed by its own docstring); the adjacent
  `_RAW_TEXT_CHAR_CAP`/`_DOCS_FILE_CAP`/`_ESTIMATED_COST_PER_CALL_USD`
  bullet re-attributed from the deleted `grounded_description.py` to
  `enrichment.py` (which still carries the first two constants unchanged,
  with the third renamed to `_ESTIMATED_COST_PER_BATCH_USD`); a
  `sync_vendor` full-overwrite bullet's false `depth = full`/`FULL`
  qualifier removed (the behaviour is universal, unconditional since
  Phase 13); and a passage claiming `VendorConfig.depth` "is set to
  `Depth.FULL`" rewritten to match `enrichment.py`'s own already-correct
  docstring (`VendorConfig` has no `depth` field at all). Closes L-004's
  Phase-61 obligation early for these 4 items — the broader §A/§B
  history-shaped trims in that catalogue remain Phase 61's job.
  `docs-maintainer` applied the fixes from lead-verified source evidence;
  independent `docs-reconstructor` drift audit confirmed each against
  `src/` directly.

- **Phase 43**: `codecompass query skills` (and `graph.skills_index`) no
  longer hides non-Skill agent-context artifacts. The read-side query was
  hard-filtered to `WHERE kind = 'skill'`, so Cursor `.mdc` rules
  (`kind='cursor_mdc'`) and the `/discovery` slash command
  (`kind='slash_command'`) — both already indexed, both already carrying
  `skill_mentions_edges` — surfaced only through a raw `context-graph.db`
  read, even though the command's own docstring promised "Skill/`.mdc`
  rule". Widened to
  `WHERE kind IN ('skill', 'cursor_mdc', 'slash_command')`
  (`graph._SKILLS_INDEX_KINDS`); each returned row now carries its
  `kind`; `query skills` gains a **Kind** column (and `kind` in `--json`);
  the generated tool-Skill's `query skills` description
  (`skill.py::render_tool_skill` → `.claude/skills/codecompass/SKILL.md`)
  is reworded to match. Closes the gap the Phase 17 entry recorded as
  "`query skills` doesn't yet surface the new artifact kind" (that
  time-relative historical line is left as-is; this entry supersedes it).
  Confirmed live against this repo: `query skills` now returns 9 rows
  (5 Skills + 3 `.mdc` + `/discovery`) where it previously returned 5.
  +2 tests (`test_graph.py`, `test_cli.py`); full suite 545.
  `docs-maintainer` reconciled `docs/cli-reference.md` and
  `architecture/overview.md` (the stale "not widened in this phase"
  paragraph removed). This is the first `src/codecompass/` change since
  the v1 redefinition began; it was dogfooded through the full 14-step
  agent-led loop (Stage A's exit, GATE DA).

### Added

- **Phase 43b**: two `check_user_docs.py` rules GATE DA scheduled — the
  standing-content complement to the diff-scoped per-phase docs-drift
  audit (now 46 tests in that module, +9). `check_no_deleted_names_as_live`
  (promotes **L-003 + L-004**) flags a retired identifier/config value
  (`grounded_description`, `Depth.FULL`, `depth = full`,
  `_ESTIMATED_COST_PER_CALL_USD`, `codecompass promote`) appearing in a
  doc's prose with no historical marker anywhere in the same bullet or
  paragraph — judged at prose-unit granularity
  (`_iter_prose_units`, list-item-or-paragraph, fenced code excluded),
  not a fixed line window, after an initial line-window design produced
  9 false positives against this repo's own legitimately historical
  `architecture/overview.md` narration (caught independently by
  `docs-maintainer` during the §C fix below). `check_generated_artifacts_match_source`
  (promotes **L-005**'s invariant half) confirms `.claude/skills/codecompass/SKILL.md`
  byte-matches `skill.render_tool_skill(...)` and
  `.claude/commands/discovery.md` byte-matches
  `commands.render_discovery_command()`, against this repo's own real
  `vendor.toml`/`context-graph.db` — deliberately narrow (the root
  `CLAUDE.md` routing table and per-vendor Skills need full graph state a
  bare check can't reconstruct; out of scope, covered by the per-phase
  drift audit instead). Both clean (0 findings) against the current repo.
  `.claude/skills/docs-sync/SKILL.md` lists both as items 13-14.

### Changed

- **Phase 43**: GATE DA (Stage A's exit retro) kept the agent roster at 7
  with no pruning and landed **4 amendments** to the agent-led process
  docs: (1) `planning/agent-led-workflow.md` step 12 + the
  `knowledge-curator` brief now require the curator to end its report with
  an explicit "lead: run `<check>` to confirm" line, which the lead then
  runs (from candidate learning **L-002**); (2) the `docs-maintainer`
  brief gains a hard rule — before editing any file, check whether it is
  *generated from `src/`* (`.claude/skills/codecompass/SKILL.md`, the
  per-vendor Skill/`.mdc` exports, `.claude/commands/discovery.md`, and
  the root `CLAUDE.md` routing block are git-tracked but regenerated on
  `sync`, so a fix belongs in the generator — the lead's job — not the
  artifact), surfaced by candidate learning **L-005** during the first
  *editing* use of `docs-maintainer`; (3) the `docs-maintainer` brief now
  notes "fix, don't caveat" may mean *deleting* a paragraph whose only
  purpose was to explain a now-resolved gap; (4)
  `planning/agent-led-workflow.md` step 11 + the `roadmap-context-curator`
  brief now require re-dispatching the curator after a retro that changes
  the plan, reconciling *every* planning doc (incl.
  `planning/v1-redefinition/roadmap.md`), from candidate learning
  **L-006**. Two `check_user_docs.py` rules GATE DA specified
  (`check_no_deleted_names_as_live`,
  `check_generated_artifacts_match_source`) are scheduled as Phase 43b.
  Candidate learnings filed this phase: **L-005** (promoted — the brief
  rule above; its `check_user_docs.py` half is Phase 43b) and **L-006**
  (candidate — the curator reconciles before the retro, so a GATE/retro
  can stale its pass; disposition confirmed at Phase 43b triage). The
  `release-phase-auditor` reached PASS WITH NON-BLOCKING OBSERVATIONS
  after a 3-round FAIL → FAIL → PASS trail, every gap planning-doc
  bookkeeping. No `CLAUDE.md` change and no new ADR this phase (43a is a
  bug fix — the command did not match its own docstring — not a
  non-obvious tradeoff), and no release or tag (gate G2-b).
  Follow-up (user request): the phase-retro `TEMPLATE.md` gains **What
  worked** (keep doing) and **What didn't work** (stop / fix) sections
  between "What was achieved" and "Lessons learnt"; `agent-led-workflow.md`
  step 11, the `retros/README.md`, and the `release-phase-auditor` brief
  updated to match, and the Phase 43 retro backfilled.

- **Phase 43c**: a Stage A→B bridge (user request) that instruments the
  agent-led development process to produce context-quality signal from
  CodeCompass's own development. Three new `planning/` pathways, no
  `src/codecompass/` change:
  - `planning/context-gaps/` (`README.md`, `TEMPLATE.md`, `inbox.md`) —
    a capture pathway for relationships an agent believes the graph
    should hold but mechanical detection can't produce. First entry
    `CG-001` (the Phase 43 `skill.py` ↔ `graph.skills_index` ↔
    `cli.py::query_skills` "one feature, three modules" relationship,
    which `codecompass query relations` cannot surface — verified).
  - `planning/context-use-log.md` — a 4-line record per CodeCompass
    context retrieval: what it gave vs. the agent's default pathway
    (grep / read / `--help`), a LOW/MODERATE/HIGH advantage rating
    (`context-quality-evaluation.md` §5), and whether anything was
    misleading. First entry: the live Phase 43 `query skills` use (rated
    **LOW** — dogfooding the query layer on itself is a hard case).
    `planning/agent-led-workflow.md` step 4 amended to require an entry.
  - `planning/context-health.md` + the roster's **8th agent**,
    `context-health-planner` (`.claude/agents/context-health-planner.md`)
    — a forward-looking "is the graph adequate for the upcoming roadmap"
    assessment; runs `codecompass query` read-only, writes only that one
    file. First assessment: CodeCompass's own 4-dependency graph is
    healthy (all versions fresh, 3/4 enriched, `pipdeptree` correctly
    unused); no Stage A→B phase is gated on it; the graph that matters
    next is Technical Clipper's, expected near-empty.
  - `decisions/0051` — agent-suggested context is captured as reviewable
    candidates, **never written to `context-graph.db`**; it becomes
    authoritative only by promotion through the learning lifecycle into a
    mechanical-detection heuristic (Stage C / GATE DB) or a graph
    capability (Stage E / GATE DD), each with its own ADR. Extends the
    determinism-first boundary (`decisions/0031`/`0037`/`0045`) to a new
    input source.
  - `decisions/0049` Consequences gains a roster-extension note;
    `planning/v1-redefinition/agent-led-development.md` (§2.9 new, §3
    table, §7 step 4) and `conditional-generalisation.md` §1.2 updated;
    `knowledge-curator` + `reference-project-tester` briefs updated to
    own / feed the new pathways. `ROADMAP.md` row `43c` between `43b` and
    `44`. No `src/` change, no test change, no release (gate G2-b).
  - Agent-led closeout: `docs-reconstructor` drift audit → **NO DRIFT**;
    `knowledge-curator` triage → `CG-001` `candidate` (provenance
    verified by code-trace) + **L-007** filed `retained` ("a mechanism
    existing" ≠ "the mechanism produced output this phase" — the first
    `context-health.md` was lead-written, so the `context-health-planner`
    agent's first solo run is tracked for before Phase 45);
    `release-phase-auditor` → **PASS WITH NON-BLOCKING OBSERVATIONS**.
    Retro: `planning/retros/phase-43c-agent-context-pathways.md`.

### Added

- **Phase 42**: the everyday documentation lifecycle gains deterministic
  drift checks and the milestone gets a documentation-closeout gate.
  `scripts/check_user_docs.py` adds three checks (now 37 tests in that
  module, +11): `check_internal_links_resolve` (every relative Markdown
  link in `README.md` / `docs/` / `ai-docs/` / `architecture/` /
  `examples/` / `CONTRIBUTING.md` resolves to an existing file; `#anchor`
  fragments checked informationally), `check_fenced_codecompass_examples`
  (every fenced example line invoking `codecompass` uses a real
  subcommand or `query` subcommand, cross-checked against `cli.py`
  including `app.add_typer(name="query")`), and
  `check_adr_status_and_supersedes` (every `decisions/*.md` ADR has a
  `Status:` line; every `decisions/NNNN` cross-reference resolves).
  `--strict` is clean against the current repo. New
  `planning/milestone-closeout-checklist.md` — the 11-step Phase 66
  documentation-closeout gate, each step with an owner and a "done"
  signal. New `planning/v1-redefinition/architecture-split-candidates.md`
  — the `docs-maintainer`'s catalogue of 36 history-shaped passages in
  `architecture/overview.md` (including 4 that now contradict the rest of
  the same file by describing deleted code as live), input for the Phase
  61 reconciliation. Candidate learning **L-004** filed: the per-phase
  docs-drift audit is diff-scoped, so pre-existing standing rot is
  invisible to it.

### Changed

- **Phase 42**: the `docs-maintainer` agent brief is finalised — it runs
  the new link / example / ADR checks, flags `architecture/overview.md`
  split candidates for Phase 61 without restructuring the file itself,
  and may return "no current-truth doc affected" for a phase that changed
  no observable product behaviour. `.claude/skills/docs-sync/SKILL.md`
  documents the three new checks;
  `planning/v1-redefinition/documentation-lifecycle.md` §5 now points at
  the closeout checklist as its operational form. No `CLAUDE.md` change
  (§5 was already amended in Phases 40–41) and no `src/codecompass/`
  change.

### Added

- **Phase 41**: the project-learning lifecycle is operational and two new
  per-phase closeout mechanisms are in place. `planning/learnings/` gains
  a `candidates/` subdirectory; its `README.md` marks the lifecycle live;
  the `knowledge-curator` agent brief is finalised against the real files
  and now also mines phase retros for candidate learnings; candidate
  **L-001** was triaged end-to-end (promoted) and logged in
  `planning/learnings/promoted.md`. New `planning/retros/` (`README.md` +
  `TEMPLATE.md`) — every phase from here on gets a lead-authored
  `planning/retros/phase-N-<slug>.md`. New `decisions/0050` records the
  learning lifecycle plus the phase-retro / per-phase docs-drift-audit
  tradeoff. `.claude/agents/docs-reconstructor` gains a scoped, read-only
  per-phase drift-audit mode (its milestone blank-slate mode is
  unchanged); `release-phase-auditor` now also checks that the retro and
  drift audit exist; `knowledge-curator` reads retros.
  `planning/agent-led-workflow.md` grows from 12 to 14 steps;
  `planning/v1-redefinition/agent-led-development.md`,
  `documentation-lifecycle.md`, and `proposed-governance-changes.md` are
  updated to match. This is the first phase to exercise the agent-led
  loop for real. Follow-up (user request, same day): the retro
  `TEMPLATE.md` gains **Where we are** and **Where we're going** sections
  so each retro orients a future session in the arc (current + previous
  phase context, upcoming phase context), not just reports a phase in
  isolation.

### Changed

- **Phase 41**: `CLAUDE.md` §5 gained two Definition-of-Done conditions —
  a lead-authored phase retro (`planning/retros/phase-N-<slug>.md`) and an
  independent per-phase `docs-reconstructor` drift audit scoped to what
  the phase changed — approved 2026-09-10 and mirrored into
  `CONTRIBUTING.md`. `scripts/check_user_docs.py` gains a `Finding.strict`
  flag (blocking vs informational; `--strict` now fails only on blocking
  findings) and four new checks: learnings-candidate provenance-field
  coverage, `promoted.md` consistency for `status: promoted` candidates,
  stale `evidence-gathering` candidates (informational), and per-phase
  retro presence for phases marked `done` from 41 onward. New tests cover
  each; `.claude/skills/docs-sync/SKILL.md` notes the new checks.

### Added

- **Phase 40**: the agent-led development model is operational. New
  `.claude/agents/` roster — `context-evaluator`,
  `reference-project-tester`, `docs-maintainer`, `roadmap-context-curator`,
  `knowledge-curator`, `docs-reconstructor`, `release-phase-auditor` —
  each with explicit read/write boundaries and independence requirements.
  New `planning/agent-led-workflow.md` (the 12-step per-session procedure,
  a trivial-change fast path, and conflict resolution). `CLAUDE.md` gained
  §8 (agent-led model), a §1 paragraph, a §5 Definition-of-Done amendment
  (candidate-learning triage + independent `release-phase-auditor` pass +
  `context-evaluator` report for reference-project phases), and a §6
  milestone-group bullet — all approved (gate G4) and mirrored into
  `CONTRIBUTING.md`. `decisions/0049` records the model.

### Changed

- **Phase 40**: `scripts/check_user_docs.py::check_readme_phase_count`
  now excludes ROADMAP content from the `## Redefined CodeCompass v1`
  heading onward — the Stage A–F phases are a process/validation
  milestone group (`decisions/0048`) and marking them `done` must not
  force the README's foundation "phases 0-N" claim upward. Regression
  test added. `README.md` Status section reverted to "phases 0-38" (the
  foundation). Captured as candidate learning L-001.

- **Phase 39**: ratified the v1 redefinition. New ADRs `decisions/0048`
  (redefined v1 is a product-validation milestone, not a packaging one)
  and `decisions/0049` (agent-led development model). `pyproject.toml`
  `version` `1.0.0` → `1.0.0.dev0` — all publishing is held until the
  redefined-v1 release (Phase 67), which will be the first-ever PyPI
  publish, as `1.0.0` (gate G2-b). `planning/ROADMAP.md`: the
  "Redefined CodeCompass v1 — Stages A–F" section is now ratified (not
  "planning"); Phase 23 row marked "Part A done; Part B superseded";
  Phases 24/25 marked `deferred` (not renumbered); a reframing note added
  above the historical "v1.0 scope notes" clarifying "v1.0" there now
  means the foundation release (the notes themselves are unedited dated
  records). `README.md` Status section reframed. No `src/` change; no
  release, tag, or dated CHANGELOG section (G2-b). `CLAUDE.md` is
  untouched — its §8/§5/§1 changes are gate G4, landing in Phases 40–42.

### Added

- Planning: **`planning/v1-redefinition/`** — an umbrella planning package
  (same role `v1.0-initial-release-roadmap.md` played for phases 20–23,
  larger scope) that **redefines "CodeCompass v1"** from a packaging
  milestone (publish the npm/PyPI/Cargo package-source tool) to a
  product-validation milestone: CodeCompass developed agent-led, validated
  against real external reference-project work (Technical Clipper, then
  Ledgerkit), improved from that evidence, generalised only as far as
  evidence justifies, released after blank-slate documentation
  reconstruction and an independent audit. 11 planning docs + the
  `planning/learnings/` lifecycle scaffold + Stage A phase plans
  (`planning/phase-39-*.md` … `phase-43-*.md`) + `planning/phase-44-*.md`.
  `planning/ROADMAP.md` gains an additive "Redefined CodeCompass v1 —
  Stages A–F" section (phases 39–67). Key inputs: nothing has been
  published (no PyPI release, no git tags, `v0.1`/`v0.2` never cut,
  `pyproject.toml` at `1.0.0` only via Phase 23 Part A), and both proposed
  reference projects have ≈0 runtime package dependencies — so the current
  model produces near-empty output for the first two real targets.
  Decided this session (gates G1/G2): all publishing is **held until the
  redefined v1** — CodeCompass has never been published, and the
  first-ever PyPI release will be the redefined v1 as `1.0.0` (Phase 67);
  `pyproject.toml` moves `1.0.0` → `1.0.0.dev0` in the interim (Phase 39).
  **Planning only — no code, no governance file changed.** A proposed
  `CLAUDE.md` §8/§5/§1 diff and ADR drafts 0048/0049 are staged in
  `planning/v1-redefinition/proposed-governance-changes.md`, not applied;
  the restructuring and version realignment are Phase 39's job, gated on
  human decisions G1–G5.

### Changed

- **Phase 38**: final polish pass ahead of the v1.0 release. `cli.py`
  gained `_not_found_error()` and `_graph_session()` (a context manager),
  removing a verbatim-duplicated error block and a 6-times-repeated
  graph-connection open/close scaffold across the `query` subcommands.
  `vendor.toml` lost 4 dead `depth = "surface"` lines (the retired `Depth`
  field). `pyproject.toml`'s 4 runtime dependencies gained lower-bound
  version pins (`typer>=0.27`, `rich>=15`, `anthropic>=0.109`,
  `pipdeptree>=4.2`) — verified live against `anthropic`'s real `1.0.0`
  breaking release (`decisions/0047`). A 5-category redundancy audit found
  the rest of the codebase clean (no dead references to retired concepts,
  no stale docs beyond what's noted, no test-suite overlap); one
  duplicate-looking pattern (the word-boundary mention-regex across
  `doc_mapping.py`/`skill_scan.py`/`relation_enrichment.py`) was
  deliberately left as-is per `decisions/0038`'s existing small-module
  precedent.

### Added

- **Phase 35**: `README.md` gains a real Setup section (Python `>=3.11`,
  `git` as a required local dependency, `ANTHROPIC_API_KEY` as the optional
  env var gating AI enrichment — previously undocumented anywhere) and a
  standalone "AI enrichment vs. no-AI usage" section reusing
  `examples/README.md`'s real `--budget 0` transcript. New `ai-docs/`
  folder: `ai-docs/README.md` (capability/boundary overview for an agent,
  each "does NOT do" claim traced to a real ADR, plus example prompts) and
  `ai-docs/CLAUDE.md` (agent entrypoint, distinct from root `CLAUDE.md`).
  `CONTRIBUTING.md`'s stale "package has real modules" closing line
  removed. Requested directly by the user, added to v1.0's blocking scope.
- **Phase 36**: new maintainer-only `scripts/check_user_docs.py` (outside
  `src/codecompass/`, not a shipped feature) mechanically flags drift
  between this repo's own hand-authored docs and its own code: CLI command
  coverage in `docs/cli-reference.md`, README phase-count consistency with
  `planning/ROADMAP.md`, `ANTHROPIC_API_KEY` mention, `VendorConfig` field
  coverage in `docs/config-schema.md`, and `ai-docs/` file presence.
  Report-only by default, `--strict` for exit-code gating. New
  `.claude/skills/docs-sync/SKILL.md` instructs an agent to run it and fix
  findings by judgment, never mechanically — no auto-fix path exists.

### Fixed

- **Phase 37**: `spec_docs._DEFAULT_GLOBS` gains `"ai-docs/**/*.md"` — found
  live during this repo's own dogfooding sync right after Phase 35 created
  `ai-docs/README.md`/`ai-docs/CLAUDE.md`: neither was detected as a spec
  doc at all, so `query relations ai-docs/README.md` errored "not found in
  context-graph.db". Confirmed live: both files now resolve correctly and
  participate in mechanical relationship detection.

- **Phase 34**: `doc_chunking.chunk_markdown` no longer misdetects a
  `#`-prefixed comment inside a fenced code block (` ``` `/`~~~`) as a
  real markdown heading. Found via a `/discovery` session testing Phase
  30-33's real output quality: `docs/cli-reference.md`'s example fence
  containing `# Not a shell command...` was misdetected, corrupting the
  `heading` reported for the `typer` relation sourced from that doc.
  Scanning all 84 currently-chunkable doc artifacts found 37 such
  false-positive lines, 12 of which had already produced real bogus
  `heading_path` values on `vendor/anthropic/src/MIGRATION.md`'s
  `documents_edges` rows (e.g. `"After > Bedrock: a region is now
  required"` — a fake heading prepended to a real one). Fixed by tracking
  fence state and never treating a line inside one as a heading
  candidate. No backfill — the next whole-project `sync` naturally
  recomputes `doc_chunks` from scratch.

### Added

- **Phase 32**: new `doc_chunking.py` deterministically splits a
  chunkable doc artifact's (`claude_md`/`overview`/`vendor_doc`/
  `spec_doc`) markdown text into heading-scoped chunks — any heading
  level, root-first nested `heading_path` (`"Scope > Covers"`), no NLP,
  no embeddings. New `doc_chunks` table; `documents_edges`/`doc_relations_
  edges` each gain a nullable `chunk_id`, populated when a mechanical
  mention-detection match is attributable to exactly one chunk (`doc_
  mapping.py`'s existing whole-doc word-boundary passes gain an additive
  per-chunk pass). A doc with no headings at all produces zero chunks, so
  its matches naturally stay unattributed — no special-casing needed.
  Phase 30's `doc_code_trace`/`graph.doc_relations` (and `query
  relations`'s output) gain an optional `heading` field when a match has
  a `chunk_id`. `relation_enrichment.select_candidates` now uses the
  matched chunk's own text directly as the AI-enrichment excerpt when one
  exists, in place of Phase 28's needle-re-derivation-plus-fixed-window
  guess — which remains, unchanged, as the fallback for any edge without
  a chunk. `documents_edges`/`doc_relations_edges` migrate on an existing
  database via the same drop-and-recreate approach `doc_artifacts`'s
  migration already uses (both are always fully rewritten every sync
  regardless); `doc_relation_enrichment` (paid AI spend) is untouched by
  this phase. See `decisions/0046`.

- **Phase 31**: `doc_relation_enrichment` (Phase 22) gains a closed-
  taxonomy `relation_label` alongside its existing free-text `ai_summary`
  — `documents_configuration_of`, `explains_usage_of`, `contrasts_with`,
  `supersedes`, or `other`. The batched enrichment tool schema now
  requires a `relation_label` per result; any value the model returns
  outside the enum (missing, malformed, or invented despite the schema's
  own `enum` constraint) is normalized to `'other'`, never raises.
  Strictly gated on Phase 21/29's already-mechanically-proven candidates —
  no new candidate discovery, same detection-vs-description boundary held
  since `decisions/0031`. `query relations` shows the label alongside the
  summary in both human and `--json` output. Schema migrates an existing
  database via `ALTER TABLE ... ADD COLUMN` (not the drop-and-recreate
  `doc_artifacts` uses) since this table holds paid AI spend that must
  survive; pre-existing rows get `relation_label = NULL` until their next
  natural re-enrichment, no backfill. See `decisions/0045`.

- **Phase 30**: `codecompass query vendor`/`query symbol` now show real
  `(file, line)` usage locations ("Used at" — `used_at` in JSON), no
  longer just a bare `usage_count`. New `graph.doc_code_trace(conn,
  doc_path_or_vendor_name)` composes existing edges into a two-hop
  package-code trace — `documents_edges` → `symbols` → `uses_edges` for
  what a doc documents, and a doc's own outgoing `mentions_dependency`
  `doc_relations_edges` → `vendors` → `uses_edges` for what it mentions —
  surfaced in `query relations` as a new "Package code" section. Pure
  query-time joins over data already in the graph; no new table, no new
  detection, no AI call, same posture as `documented_but_unused`.
  `query relations --json`'s payload changes from a bare list to
  `{"relations": [...], "package_code": [...]}` — a relation and a usage
  site are different shapes that don't merge into one row; `query
  vendor`/`query symbol --json` gain `used_at` as one more key, purely
  additive. Confirmed live against this repo's real graph: `query symbol
  Console`'s `used_at` matches the real import-line locations `grep`
  finds; `query relations architecture/overview.md`'s "Package code"
  section lists real `typer` call sites in `cli.py`. See `planning/
  phase-30-bidirectional-code-traversal.md`.

### Fixed

- **Phase 33**: `codecompass query vendors|vendor|symbol|skills|relations
  --json` no longer emits invalid JSON. Every `--json` call site printed
  through the shared Rich `Console`, which word-wraps long printed text by
  inserting real line breaks; a value long enough to cross the wrap width
  (e.g. `anthropic`'s longer symbol `purpose` strings, confirmed live
  against this repo's real graph) got a literal newline inserted into it,
  corrupting the JSON. Fixed by adding `soft_wrap=True` to all five call
  sites — the same flag Rich's own `Console.print_json` uses internally
  for exactly this case. New regression test confirmed to fail against the
  pre-fix code and pass against the fix. Found via the same `/discovery`
  session that surfaced Phases 30-32 below; that session's other flagged
  item (a `check` version-drift reading that looked backwards) was
  investigated and confirmed not a bug — see `planning/
  phase-33-fix-query-json-line-wrapping.md`'s Context section.

### Added

- Planning: `planning/doc-graph-precision-roadmap.md` — a new umbrella
  plan (same role `v1.0-initial-release-roadmap.md` played for 20-23),
  plus three new phase plans it introduces: `planning/
  phase-30-bidirectional-code-traversal.md` (surface `uses_edges`'
  existing file/line data via a new `used_at` list and a `doc_code_trace`
  two-hop query — no new tables, no AI), `planning/
  phase-31-typed-relation-enrichment.md` (a closed `relation_label` enum
  alongside Phase 22's existing free-text `ai_summary`, gated on Phase
  21/29's already-mechanically-proven candidates only), and `planning/
  phase-32-doc-chunking.md` (deterministic heading-based split of doc
  artifacts into a new `doc_chunks` table, with a nullable, additive
  `chunk_id` on `documents_edges`/`doc_relations_edges`). All three hold
  the same detection-vs-description AI boundary established by
  `decisions/0031`. `planning/ROADMAP.md`'s Post-MVP table updated: 30/31/32
  appended after 29, no renumbering. At explicit user request, these three
  phases also expand v1.0's blocking scope — Phase 23 Part B (the actual
  publish) now waits on 30-32 reaching `done` too, alongside its existing
  confirmation gates. Planning only, no code changed.

- **Phase 29**: a vendor's own embedded upstream doc (`kind='vendor_doc'`,
  Phase 27) is no longer passive, indexed-only content — it now
  participates in the graph as a relationship *source*, symmetric to how
  spec docs already did. `build_documents_edges` now scans `vendor_doc`
  rows for symbol mentions too (a vendor's own README documenting its own
  API is now a real `documents_edges` source, confirmed live:
  `vendor/anthropic/src/README.md` now documents the `Anthropic` symbol).
  `build_doc_relations_edges` now accepts vendor docs as sources alongside
  spec docs, via a deliberately closed allow-set
  (`{"spec_doc", "vendor_doc"}` — codecompass-generated artifacts are
  excluded on purpose, since they'd only ever produce structural
  self-mentions, not signal), with a self-mention exclusion so a vendor's
  own README mentioning its own name never produces a
  `mentions_dependency` edge to itself (confirmed live against real data:
  zero such edges despite `vendor/anthropic/src/README.md` containing
  "anthropic"/"Anthropic" seven times). Confirmed live: 3 new
  vendor-doc-sourced relationships appeared on the first re-sync. See
  `decisions/0043`, which supersedes `decisions/0041`'s "a vendor doc is
  never a relation source" claim specifically (its actual root-level
  detection-scope decision is unaffected).

### Fixed

- **Phase 28**: `relation_enrichment.select_candidates` no longer always
  sends the spec doc's first 4,000 characters as AI grounding — it now
  re-derives the mechanical match's position (the same needle and regex
  shape `doc_mapping.build_doc_relations_edges` used to detect the
  relationship) and centers a 4,000-character window on it, falling back
  to the old first-N-characters slice only if the needle can no longer be
  found. Fixes a real, reproduced bug: this repo's own two currently-
  enriched `"anthropic README.md"` relationships had their real
  mechanical match at character 7,870 and 91,374 of their respective
  files, both past the old fixed window, producing plausible-sounding but
  ungrounded AI summaries. `graph.relation_enrichment_candidates` gained
  a `target_doc_artifact_name` column to support this. See `decisions/0042`.

- Planning: `planning/phase-28-center-relationship-excerpts-on-the-
  actual-match.md` — a future plan found via a live `/discovery` session
  testing Phase 26/27's real output quality. `relation_enrichment.
  select_candidates` always sends a spec doc's first 4,000 characters as
  grounding, regardless of where the mechanical match actually is;
  confirmed with real data that both of this repo's currently-enriched
  vendor-doc relationships got ungrounded AI summaries as a result (the
  real match sits at character 7,870 of one file and 91,374 of another,
  both past the fixed window). `planning/ROADMAP.md`'s Post-MVP table
  updated: 28 appended after 27, no renumbering. Planning only, no code
  changed.

- **Phase 27**: a cloned vendor's own embedded upstream doc files
  (`README*.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`,
  `MIGRATION.md` at its clone root, `vendor/<name>/src/`) are now
  registered as `doc_artifacts` rows (`kind='vendor_doc'`,
  `origin='vendor_upstream'` — new CHECK values, `_SCHEMA_VERSION` "3" →
  "4"), via new `doc_mapping.collect_vendor_upstream_doc_artifacts`. Every
  downstream mechanism picks them up unchanged: they're eligible
  `mentions_artifact` targets for Phase 21's mention-detection and
  Phase 22's AI-enriched relationship summaries, appear in `query
  relations`, and `check` gained a new "Vendor docs with no detected
  relations" section. Root-level files only, deliberately not a
  recursive scan of a vendor's own `docs/` folder. Confirmed against
  this repo: 28 real vendor-doc rows registered across all four tracked
  vendors, with no impact on Phase 15's existing `vendor/`
  usage-detection exclusion. See `decisions/0041`.

- **Phase 26**: `usage.detect_python_imports` now upgrades a plain
  `import X` (or `import X as alias`) to symbol-level usage evidence when
  the code actually accesses an attribute of it (`X.Attr(...)`) — an
  additive second AST pass, the vendor-level `DetectedImport` from the
  `import` statement itself is unchanged. Only the immediate attribute
  off the bound name resolves (`X.sub.Attr` → `sub`, not `Attr`),
  mirroring `ImportFrom`'s existing first-dotted-component-only rule.
  Fixes real noise this repo's own `check` output had: 35 real
  `anthropic` symbols (`Anthropic`, `AnthropicError`, etc.) showing as
  "documented but unused" purely because this project imports `anthropic`
  as a module and accesses attributes on it, which the detector
  previously couldn't resolve past the module level.

- Planning: two new future phases found via a `/discovery` dogfooding
  session against this repo itself, each with its own real, confirmed
  evidence (not guessed) — `planning/phase-26-symbol-level-resolution-
  for-attribute-usage.md` (a plain `import X` followed by `X.Attr(...)`
  never resolves to a symbol-level usage edge, confirmed: all 6
  `anthropic` `uses_edges` rows in this repo have `symbol_id = NULL`,
  causing 35 real symbols to show as "documented but unused") and
  `planning/phase-27-register-embedded-vendor-docs.md` (a cloned vendor's
  own upstream docs — confirmed: 30+ real files under `vendor/*/src/` in
  this repo — have no `doc_artifacts` row at all, so Phase 21/22's
  relationship detection/enrichment never applies to them).
  `planning/ROADMAP.md`'s Post-MVP table updated: 26/27 appended after
  24/25, no renumbering needed. Planning only, no code changed.

### Fixed

- `/discovery`'s generated body overstated what its `allowed-tools`
  frontmatter guarantees: confirmed against actual Claude Code behavior
  (not assumed) that the pre-approval grant covers only the single turn
  that invokes the command — it clears once the reply is sent, and
  nothing re-applies it or blocks `Write`/`Edit`/`ExitPlanMode` on a later
  turn in the same conversation. `render_discovery_command` (`commands.py`)
  and `architecture/overview.md` now say so explicitly and instruct Claude
  to hold the read-only posture deliberately for the rest of the session,
  not assume the frontmatter still enforces it past the first reply. See
  `decisions/0040`.

### Added

- **Phase 23, Part A** (packaging/release readiness — the actual PyPI
  publish is Part B, held for explicit confirmation): `pyproject.toml`
  bumped to `version = "1.0.0"`, `classifiers` corrected to
  `Development Status :: 4 - Beta`, `[project.urls]` added
  (Homepage/Repository/Issues). `README.md`'s Status section and feature
  list updated to reflect phases 0-22 all `done`, including the Phase
  21/22 spec-doc relationship detection that had no README mention at
  all. New `examples/toy-project` — a small real project with real
  `requests`/`click` usage, plus `examples/README.md` quoting real
  `codecompass` output captured against it. New `decisions/0039`: v1.0
  ships without a dedicated docs site (`README.md` + `docs/*.md` on
  GitHub only), a deliberate, revisitable deferral, not an oversight.
  Verified: a real `python -m build` wheel installs cleanly into a fresh
  throwaway venv independent of this repo's editable dev install, and
  `codecompass --help` runs from it.

- **Phase 22**: batched AI enrichment now runs over Phase 21's
  mechanically-detected spec-doc relationships too, gated strictly on
  those already-proven candidates (new `relation_enrichment.py`, sibling
  to `enrichment.py`, same batched forced-tool-use call shape). Folded
  into the existing Phase B cost/consent prompt — one disclosure, one
  `--yes`/`--budget` gate, covering vendor/symbol enrichment and
  relationship enrichment together. `codecompass query relations` now
  shows each relation's AI-enriched `ai_summary` when one exists, else
  "mentioned, not yet enriched". New `doc_relation_enrichment` table is
  keyed by plain natural-key strings with **no foreign key** to
  `doc_artifacts` (which is fully deleted/reinserted every rebuild, unlike
  the upserted `vendors`/`symbols`) — see `decisions/0038` for why, and
  for the non-negotiable boundary this phase establishes: the AI-generated
  summary is written only to the graph, **never into a spec doc's own
  file** — `relation_enrichment.apply_results` doesn't even accept a
  `project_root`, so it structurally cannot write one.

- **Phase 21**: a project's own human-authored spec docs (README,
  `ARCHITECTURE.md`, `docs/**/*.md`, `architecture/**/*.md`,
  `decisions/**/*.md`, `spec/**/*.md`, `specs/**/*.md`, `rfcs/**/*.md`,
  `*.spec.md`) are now detected as `doc_artifacts` rows
  (`kind='spec_doc'`, `origin='project'`, new module `spec_docs.py`) and
  mechanically linked to tracked vendors and other doc artifacts
  (Skills, `.mdc` rules, dependency docs) via a new `doc_relations_edges`
  table and `doc_mapping.build_doc_relations_edges` — the same
  word-boundary mention heuristic already used elsewhere, no AI call.
  New `codecompass query relations <name>` (a spec-doc path, or a
  vendor/Skill name for the reverse lookup); `check` gained a "Spec docs
  with no detected relations" report-only section. `doc_artifacts`'
  `kind`/`origin` CHECK constraints widened (`_SCHEMA_VERSION` "2" →
  "3"). See `decisions/0037`.

### Fixed

- **Phase 20**: the root `CLAUDE.md` routing table, tool-level Skill, and
  discovery command now always refresh *after* AI enrichment finishes
  (success or budget-abort), not before — a vendor enriched during the
  same `codecompass`/`sync` invocation no longer shows stale
  pre-enrichment status until a second run. New `cli._refresh_generated_
  artifacts`, called from a `try/finally` around `_maybe_run_enrichment`
  in both `_bootstrap` and `sync`'s whole-project branch — the latter
  previously never regenerated these artifacts at all. Closes the
  graph/enrichment ordering gap flagged after Phase 18 and confirmed
  during this project's first live enrichment run.

### Added

- Planning: `planning/v1.0-initial-release-roadmap.md` — the path-to-v1.0
  umbrella plan, plus two new phase plans it introduces: `planning/
  phase-21-spec-doc-detection-and-relationship-graph.md` (mechanical
  detection of a project's own README/`docs/`/`architecture/`/`decisions/`
  etc. as graph nodes, linked to dependency docs and skills via the
  existing mention-heuristic pattern) and `planning/
  phase-22-ai-enriched-cross-artifact-relationships.md` (a batched AI call
  summarizing *how* each of those mechanically-detected relationships
  connects, gated on Phase 21's candidates only, folded into the existing
  Phase B cost/consent flow, never writing to a spec doc's own file).
  `planning/ROADMAP.md`'s Post-MVP table updated: Phases 21/22 inserted;
  former Polish phase moves to 23 (now the v1.0 release phase itself);
  former routing/rollup and MCP phases move to 24/25, deferred past the
  v1.0 release line (proposed, not locked — see the roadmap doc's "Why
  this order" section). Planning only, no code changed.

- Planning: `planning/phase-20-refresh-generated-artifacts-after-
  enrichment.md` — a future plan for the remaining piece of the graph/
  enrichment ordering gap (routing table, tool Skill, `undo`/`query
  skills` freshness immediately after a vendor's first enrichment).
  `planning/ROADMAP.md`'s Post-MVP table updated: new Phase 20 inserted,
  former 20/21/22 shift to 21/22/23. Planning only, no code changed.

### Fixed

- The tool-level Skill (`.claude/skills/codecompass/SKILL.md`) listed
  `codecompass query vendors|vendor|symbol|skills` as one bare line with
  no guidance on what each subcommand does, no mention of `--json`, and
  no pointer to `context-graph.db`'s schema for ad hoc queries — found by
  direct inspection, unlike `/discovery`'s much richer equivalent
  content. `skill.py`'s `render_tool_skill` now explains each `query`
  subcommand, the raw-`sqlite3` escape hatch, and points at `/discovery`.

- **`codecompass sync` crashed on any second run once a vendor had been
  git-cloned** — `source_resolution._git_clone`'s naive
  `shutil.rmtree(dest)` hit a `PermissionError` re-cloning over a git
  repo's own read-only `.git/objects/pack/*` files (Windows). Found via
  the first real end-to-end run of this project against a live
  Anthropic API key. Fixed by promoting `undo`'s (Phase 18,
  `decisions/0036`) best-effort rmtree helper —
  clears the read-only bit and retries, reports genuine failures instead
  of guessing — to `source_resolution.rmtree_best_effort`, shared by
  both callers instead of duplicated; `cli.py`'s local copy removed.
- **A vendor's `OVERVIEW.md` never appeared on its first-ever
  enrichment**, only from the *next* whole-project sync — `sync_vendor`
  (Phase A) only ever writes it from an enrichment record that already
  existed *before* that run, and on a first enrichment nothing was in
  the graph yet when Phase A ran. Also found via the same live run.
  Fixed: `enrichment.apply_results` (Phase B) now writes `OVERVIEW.md`
  itself, right where `conversational_overview` is freshest, instead of
  waiting a full sync cycle. Regression test simulates a vendor's first
  enrichment with no prior `OVERVIEW.md` on disk.

- A `depth = surface` vendor whose source clone fails no longer shows a
  misleading "## Description — Description unavailable" section in its
  `CLAUDE.md` — `_render_description_section` now gates on `depth is
  FULL` before ever looking at `description_error`, since Phase 13 made
  cloning (and therefore `description_error`) universal, decoupling it
  from whether a description was ever attempted. Caught during
  independent verification of Phase 13, not by automated tests (nothing
  before Phase 13 could produce this combination, so nothing asserted
  its absence) — see `planning/v0.2-implementation-execution-plan.md`
  for the reinforced verification step this prompted.

### Fixed

- A whole-project `sync` re-run silently erased Phase B's AI-enrichment
  content from `CLAUDE.md` — `sync_vendor` rebuilt every vendor's file
  from scratch via a digest that never carried enrichment data, gated on
  a `Depth` value nothing has set since `promote` was removed in Phase
  15. Shipped on `main` since that phase; caught while implementing
  Phase 16. Fixed per `decisions/0035`: `sync_vendor` now reads a
  vendor's current enrichment from the context graph before building its
  digest, so a from-scratch re-render reproduces existing enrichment
  instead of erasing it. Regression test syncs an enriched vendor twice
  and confirms the Description section survives.
- `usage.py`'s project-source scan didn't exclude `vendor/` — since
  Phase 13, every tracked vendor's own upstream source clones into
  `vendor/<name>/src/` inside that same walk, and a vendor's own source
  very often self-references its own package name, registering as a
  false-positive "the project uses this vendor" signal for nearly every
  vendor on every run. Fixed by adding `"vendor"` to
  `_PROJECT_PRUNE_DIR_NAMES` (Phase 15), with a regression test. Caught
  by the implementing subagent's own end-to-end testing before it ever
  reached the orchestrating session's independent review.
- `chat.py`'s "no grounded description yet" hint still referenced
  `codecompass promote <vendor>`, a command removed in Phase 15 — reworded
  to point at `sync`.

### Added

- **Phase 19: chat demotion + governance docs — MVP (v0.2) complete,
  all eleven phases (9-19) `done`.** Implements
  `planning/phase-19-chat-demotion-and-governance-docs.md` and
  `decisions/0034`. `README.md` rewritten around the v0.2 primary
  workflow (bare `codecompass` → clone + disclosed usage-driven
  enrichment → `codecompass query`/`/discovery`/generated Skills,
  `chat` explicitly secondary). `architecture/overview.md`'s opening
  summary, "Chat REPL" (now framed per `decisions/0034`, historical
  pointer to superseded `decisions/0012` left unedited — append-only),
  "Two consumption modes", "Multi-tool export", "Staleness checking",
  "Retrofitting to existing projects", "Cost model", and "Known
  footguns" sections, plus `docs/cli-reference.md`, corrected against
  the fully-built system — roughly a dozen stale `promote`/`Depth`/
  pre-rework references found and fixed in total, including two
  present-tense instructions to run a deleted `codecompass promote`
  command. `chat.py`/`skill.py`/`discovery.py` docstrings updated to
  match (no logic changes). `pytest`: 366 passed, 1 skipped throughout;
  `ruff check .` clean.
- **Phase 18: `undo` command** — implements
  `planning/phase-18-undo-command.md` and new `decisions/0036`. New
  `codecompass undo [--yes] [--dry-run]`: graph-backed enumeration
  (every `doc_artifacts` row tagged `codecompass_tool`/
  `codecompass_vendor`, never `third_party`) with a pattern-based
  fallback when no `context-graph.db` exists yet; strips root
  `CLAUDE.md`'s routing-table marker block in place rather than deleting
  the file; never runs a git command or commits on the user's behalf.
  Fixes a Windows-specific bug found during implementation: naive
  `rmtree` silently left a cloned vendor's read-only `.git/objects/`
  files behind while reporting success — `_rmtree_best_effort` clears
  the read-only bit, retries, and reports genuine leftovers instead.
  `pytest`: 366 passed, 1 skipped; `ruff check .` clean.
- **Phase 17: `/discovery` slash command** — implements
  `planning/phase-17-discovery-slash-command.md`. New
  `src/codecompass/commands.py`, generating
  `.claude/commands/discovery.md`: `allowed-tools` scoped to
  `Read`/`Grep`/`Glob` plus a narrow `codecompass query`/`check`/`sqlite3
  context-graph.db` allowlist (no `Write`/`Edit`), with the read-only
  constraint also repeated in plain instructional text. `graph.py`'s
  `doc_artifacts.kind` widened to include `'slash_command'`
  (`_SCHEMA_VERSION` bump + migration for an already-existing database).
  `skill_scan.py` indexes the new file. Two minor, documented scope gaps
  found and correctly left alone rather than silently expanded: the
  plan's claimed three `write_tool_skill` trigger points are actually
  two; `query skills` doesn't yet surface the new artifact kind.
  `pytest`: 355 passed, 1 skipped; `ruff check .` clean.
- **Phase 16: retire `Depth`** — implements `planning/phase-16-retire-depth.md`
  and `decisions/0031`/`0035`. `core.py`'s `Depth` enum deleted;
  `VendorConfig` narrowed to `(name, ecosystem)`; `config.py` tolerates a
  legacy `depth =` line in `vendor.toml` silently rather than erroring;
  `discovery.py`/`cli.py` updated to match.
  `src/codecompass/grounded_description.py` (and its test file) deleted
  — `codecompass.enrichment` (Phase 14) fully replaces its role. `pytest`:
  340 passed, 1 skipped (down from 361 — the deleted module's tests and
  two now-obsolete budget tests account for the difference); `ruff
  check .` clean; `grep -rn "Depth\b" src/` returns zero hits.
- **Phase 15: CLI rewire** — implements `planning/phase-15-cli-rewire.md`
  and `decisions/0033`. `promote` removed entirely. Bare `codecompass`
  and whole-project `sync` gain `--yes`/`--budget` and auto-trigger Phase
  B (disclose/confirm, then batched enrichment) right after Phase A's
  free work. New `query {vendors|vendor|symbol|skills}` command group
  (Rich tables or `--json`). `check` gains report-only coverage-gap
  sections — unused vendors, documented-but-unused/used-but-undocumented
  symbols, orphaned third-party skill mentions — **`--strict`'s exit code
  unaffected**, still version-drift severity only. `index.py`/`skill.py`
  migrated from `Depth`-keyed to graph-derived enrichment status (new
  `graph.has_enrichment`). `pytest`: 361 passed, 1 skipped; `ruff
  check .` clean.
- **Phase 14: batched enrichment (Phase B)** — implements
  `planning/phase-14-batched-enrichment.md`. New
  `src/codecompass/enrichment.py`: `select_candidates` (two-tier
  DB-hash + `CLAUDE.md`-file-hash cache check, per `decisions/0032`),
  `plan_batches`, batched forced-tool-use enrichment
  (`run_enrichment_batches`), `apply_results` (writes to the graph,
  updates `CLAUDE.md` in place via new `claude_md.
  update_description_section`/`read_enrichment_hash`, generates
  per-vendor Skill/`.mdc` via a minimal `VendorDigest`),
  `estimate_cost`/`check_budget` reworked to scale with batch count.
  Library-only — not yet wired into `cli.py`/`sync.py` (Phase 15).
  `grounded_description.py` untouched, still active for `depth = full`
  vendors until Phase 15/16. `pytest`: 336 passed, 1 skipped; `ruff
  check .` clean.
- **Phase 13: universal source cloning** — implements
  `planning/phase-13-universal-source-cloning.md` and `decisions/0033`.
  `sync.sync_vendor` restructured: cloning now runs unconditionally for
  every vendor (previously gated on `depth = full`), independent of
  grounded-description generation (still `depth`-gated, additionally
  requiring this run's own clone to have succeeded). `FILETREE.md`/
  `filetree.json`/the symbol index now render from the clone root when
  available, with the existing local-install fallback — a real, visible
  output change for every vendor, not just previously-`FULL` ones.
  `pytest`: 299 passed, 1 skipped; `ruff check .` clean.
- **Phase 12: doc & wide skill mapping** — implements
  `planning/phase-12-doc-and-wide-skill-mapping.md`. New
  `src/codecompass/doc_mapping.py` (`collect_vendor_doc_artifacts`,
  `build_documents_edges`, `build_routes_via_edges`,
  `build_depends_on_edges`) and new `src/codecompass/skill_scan.py`
  (`scan_skills` — indexes **every** skill under `.claude/skills/` and
  `.cursor/rules/`, not just codecompass-generated ones, via a minimal
  custom frontmatter extractor with no new YAML dependency;
  `build_skill_mentions_edges` — word-boundary, not substring, matching
  against tracked vendor names and source-file basenames).
  `sync.rebuild_project_graph` now populates every table in the graph,
  not just vendors/symbols/uses. Manually confirmed against this repo's
  own `.claude/skills/codecompass/SKILL.md` and `vendor/*/deptree.json`.
  `pytest`: 296 passed, 1 skipped; `ruff check .` clean.

- **Phase 11: project-source usage detection** — implements
  `planning/phase-11-project-source-usage-detection.md`. New
  `src/codecompass/usage.py`: `detect_python_imports` (`ast`-based),
  `detect_npm_imports`/`detect_rust_imports` (regex), `DetectedImport`,
  `resolve_project_usage`. `filetree._iter_files` made public as
  `iter_source_files(root, *, prune_dirs=..., prune_globs=...)`, zero
  behavior change for existing callers. New
  `sync.rebuild_project_graph`, wired into `cli.py` at exactly two
  whole-project call sites (bare bootstrap, `sync` with no vendor arg) —
  `sync <vendor>` and `check --fix` leave the graph untouched, per
  `decisions/0025`. Manually confirmed against this repo's own source:
  correct symbol-level resolution (e.g. `rich.console.Console`), correct
  zero-usage detection for a subprocess-only dependency (`pipdeptree`),
  and single-vendor sync leaves `context-graph.db` untouched. `pytest`:
  270 passed, 1 skipped; `ruff check .` clean.

- **Phase 10: SQLite graph foundation** — implements
  `planning/phase-10-sqlite-graph-foundation.md` and `decisions/0032`.
  New `src/codecompass/graph.py`: the full 9-table + `meta` schema,
  `init_schema`, `open_graph`, 9 row dataclasses, `rebuild_deterministic`
  (upserts vendors/symbols by natural key so `vendor_enrichment`/
  `symbol_enrichment` survive a rebuild despite their `ON DELETE CASCADE`
  foreign keys — a real bug caught during implementation, not anticipated
  in the plan, now locked in with dedicated regression tests), 7 query
  functions (`unused_vendors`, `documented_but_unused`,
  `used_but_undocumented`, `vendor_profile`, `symbol_profile`,
  `skills_index`, `enrichment_candidates`), and
  `record_enrichment`/`record_symbol_enrichment`. Library-only — not yet
  called from `sync.py`/`cli.py` (starts Phase 11). `context-graph.db`
  added to `.gitignore`. `pytest`: 241 passed, 1 skipped; `ruff check .`
  clean.

### Changed

- **MVP (v0.2) phase order corrected**: "Retire `Depth`" moves from
  Phase 10 to **Phase 16** — it was originally sequenced before anything
  existed to replace the eight call sites that currently read it
  (`sync.py`, `grounded_description.py`, `cli.py`, `index.py`,
  `skill.py`, `claude_md.py`, `chat.py`, `discovery.py`); it's only safe
  once phases 13-15 replace all of them. The graph/usage-detection/
  mapping/cloning/enrichment/CLI phases shift from 11-16 down to 10-15;
  phases 17-19 unaffected. Bookkeeping only, no code — caught and fixed
  before any Phase 10 code was written. See `planning/ROADMAP.md`'s
  renumbering note for the full old→new table, including which of
  `decisions/0031`-`0034`'s internal "Phase N" citations are now stale
  (not editable — append-only).
- **Phase 9: renamed the package from `depcompass` to `codecompass`**
  (`decisions/0029`, `planning/phase-9-rename-to-codecompass.md`) —
  mechanical only, zero behavior change. `src/depcompass/` moved to
  `src/codecompass/` (`git mv`, preserving blame); the console script is
  now `codecompass`; every internal import, the root `CLAUDE.md` routing
  marker (`<!-- codecompass:start/end -->`), the tool-level Skill
  (`.claude/skills/codecompass/`), and all prose in `README.md`,
  `CONTRIBUTING.md`, `docs/`, and `architecture/overview.md` updated to
  match. `decisions/*.md` and `CHANGELOG.md`'s prior entries are
  deliberately untouched (append-only / historical record). Full test
  suite (218 passed, 1 skipped) and `ruff check .` both green under the
  new name; verified end-to-end with a fresh `pip install -e ".[dev]"`
  and a bare `codecompass` + `codecompass sync` run against this repo
  itself.
- Phase 10 planning: `planning/phase-10-sqlite-graph-foundation.md` — the
  new `graph.py` module (SQLite schema, `init_schema`,
  `rebuild_deterministic`, read-only query functions), per
  `decisions/0032`. Library-only; not yet wired into `sync.py`/`cli.py`.
  Planning only, no code changed.
- **Phases 11-19 planning: the rest of MVP (v0.2) is now fully
  implementation-ready.** Nine new plan files, each grounded in the
  actual current source, covering the whole arc in dependency order:
  `phase-11-project-source-usage-detection.md` (new `usage.py`;
  `filetree._iter_files` becomes public `iter_source_files` with
  configurable prune sets; new `sync.rebuild_project_graph`, wired into
  bare bootstrap and whole-project `sync` only), `phase-12-doc-and-
  wide-skill-mapping.md` (new `doc_mapping.py` + `skill_scan.py`,
  including the project-wide, not-just-codecompass-generated skill scope
  expansion; word-boundary matching, no new YAML dependency),
  `phase-13-universal-source-cloning.md` (splits cloning from grounded-
  description generation in `sync_vendor` — cloning becomes
  unconditional, description stays `depth`-gated until Phase 15),
  `phase-14-batched-enrichment.md` (new `enrichment.py` replacing
  `grounded_description.py`; batched candidate selection, two-tier
  cache-hash skip logic, a new `claude_md.update_description_section`
  for in-place `CLAUDE.md` updates instead of full `VendorDigest`
  reconstruction), `phase-15-cli-rewire.md` (the integration phase:
  `promote` removed, bare `codecompass` gains `--yes`/`--budget` for
  Phase B's auto-triggered consent gate, new `query` command group,
  `check`/`index`/`skill.py` migrated to graph-backed enrichment status),
  `phase-16-retire-depth.md` (now safe — the `Depth` enum/field finally
  removed, `vendor.toml`'s legacy `depth=` line tolerated on read),
  `phase-17-discovery-slash-command.md` (new `commands.py`, `/discovery`
  generated alongside the tool Skill), `phase-18-undo-command.md` (new
  `undo [--yes] [--dry-run]`, graph-backed enumeration with a
  pattern-based fallback when no graph exists yet, never commits), and
  `phase-19-chat-demotion-and-governance-docs.md` (README/architecture
  rewritten around the graph+Skills+`/discovery` as primary, MVP (v0.2)
  closes out). Every `planning/ROADMAP.md` row for phases 11-19 flips
  from `not started` to `planned` with its plan file linked. Planning
  only, no implementation code changed — implementation proceeds
  strictly in this order starting from Phase 10, since each later
  phase's plan assumes the previous ones' code already exists.
- `planning/ROADMAP.md` renumbered: the context graph (Phase 9,
  sub-phases 9a-9e) is inserted ahead of the previously-unplanned
  project-root REPL routing/rollup work, which shifts from Phase 9 to
  **Phase 10** (former Phase 10/11 — polish, MCP — shift to 11/12).
  Bookkeeping only, no code; all shifted phases were `not started`, so
  this is a clean renumber, not a rewrite of in-flight work — same
  precedent as the Phase 7-era renumbering below.
- MVP milestone expanded from phases 0-6 to phases 0-8 (`decisions/0022`)
  — bookkeeping only, no code. Phase 8 (the chat REPL, `decisions/0012`'s
  "actual product") structurally depends on Phase 7's outputs (Skill
  files, dual-audience content shape), so both move from
  `planning/ROADMAP.md`'s Post-MVP table into its MVP table together;
  `v0.1` now tags only once Phase 8 is `done`, not Phase 6.
  `CLAUDE.md` §6, `CONTRIBUTING.md`, `docs/cli-reference.md`,
  `architecture/overview.md`, and `README.md` updated to match; no phase
  was renumbered, only table membership and milestone-boundary text.

### Added

- **MVP (v0.2) planning: rename to codecompass, retire `promote`/`Depth`,
  SQLite relationship graph, `/discovery`, `undo`** — planning only, no
  code changed. Supersedes the Phase 9 context-graph planning entry below
  (that plan was never implemented; its four plan files are deleted —
  recoverable from git history — while its five ADRs stay, append-only;
  see `planning/ROADMAP.md`'s "Superseded planning" note). New
  `planning/phase-9-rename-to-codecompass.md`
  (mechanical rename, zero behavior change) and six new ADRs:
  `decisions/0029` (rename announcement), `decisions/0030` (MVP milestone
  redefined — v0.2 spans phases 9-19, `planning/ROADMAP.md`'s new MVP
  (v0.2) table), `decisions/0031` (`Depth` retired — enrichment becomes
  usage-driven, not a manual per-vendor toggle, superseding
  `decisions/0001`), `decisions/0032` (context graph moves from a single
  JSON file to SQLite, superseding `decisions/0024`), `decisions/0033`
  (`promote` retired — universal source cloning plus an auto-triggered,
  still cost-disclosed/confirmable batched enrichment step replaces it,
  superseding `decisions/0018` and partially `decisions/0017`), and
  `decisions/0034` (chat demoted from "the actual product" to a secondary,
  unchanged-code subcommand — the graph, generated Skills, and the new
  `/discovery` command become primary, superseding `decisions/0012`).
  `planning/ROADMAP.md` restructured: former Post-MVP phases 9a-9e
  superseded (retained, not deleted); new MVP (v0.2) table added spanning
  phases 9-19 (rename → depth retirement → SQLite graph foundation →
  usage detection → doc/skill mapping → universal cloning → batched
  enrichment → CLI rewire → `/discovery` → `undo` → chat demotion/docs);
  former routing/rollup, polish, and MCP-server phases renumbered
  10→20, 11→21, 12→22.
- Phase 9 planning (superseded — see entry above): context graph
  (sub-phases 9a-9d) — planning only, no
  code changed. New `planning/phase-9a-vendor-presence-graph.md` (vendor-
  level `uses` edges, dead-dependency detection surfaced via `check`),
  `planning/phase-9b-symbol-usage-graph.md` (symbol-level `uses`, reusing
  existing per-ecosystem symbol extraction rather than re-deriving it),
  `planning/phase-9c-doc-skill-mapping.md` (`DocArtifact` nodes,
  `documents`/`routes_via`/`depends_on` edges, coverage-gap reporting),
  and `planning/phase-9d-llm-enrichment.md` (optional, off-by-default
  LLM enrichment: usage-purpose labels, clustering, a `DOCUMENTS` quality
  delta, file-role summaries, `EXPLAINS` chunk retrieval, a
  trigger-accuracy proxy). Five new ADRs, `decisions/0024`-`0028`:
  context-graph storage model (single root-level `context-graph.json`),
  its cache-invalidation trigger (rebuilds only on bare `sync`/bootstrap,
  never incrementally), Phase 9d's optional/deterministic-gated posture
  (explicitly not closing `decisions/0013`'s outstanding trigger-accuracy
  harness item), `EXPLAINS`-vs-`decisions/0023` reconciliation
  (coexistence — `chat.py` is untouched), and usage-cluster
  classification's draft-only, never-auto-written posture (deferred to a
  future Phase 9e, not part of this pass). A future Phase 9e is
  identified in `planning/ROADMAP.md` but deliberately not planned in
  implementation detail this session — it needs real field data from 9d.
- Single-vendor chat REPL (Phase 8): implements
  `planning/phase-8-chat-repl.md` and `decisions/0023` — **all eight MVP
  phases (0-8) are now complete.** New `depcompass chat <vendor>`: a
  terminal REPL that grounds every answer on the vendor's already-
  persisted `vendor/<name>/CLAUDE.md` (required) and `OVERVIEW.md`
  (optional, present once `promote`d), read directly as text — never
  calls `sync`/`promote` itself, so starting a session never re-clones
  or re-runs AI generation. Works at any depth; a vendor with no
  `OVERVIEW.md` yet gets thinner grounding plus a one-line hint to run
  `promote`, not a hard block. Plain multi-turn text completion against
  `claude-haiku-4-5-20251001` — no forced tool-use, no file-exploration
  loop. New `src/depcompass/chat.py`. Bare project-root `chat` (no
  vendor name), Tier 1/2 routing, and the whole-project dependency
  rollup remain Phase 9, not built here.
- Phase 8 plan (`planning/phase-8-chat-repl.md`) and `decisions/0023` —
  planning only, no code changed (written in the session before this
  implementation).
- Zero-question bootstrap & `promote` (Phase 7): implements
  `planning/phase-7-bootstrap-and-promote.md` and `decisions/0017`-
  `0021` — MVP phases 0-7 are now complete. Bare `depcompass` (no
  subcommand) auto-discovers manifests (`package.json`, `pyproject.toml`,
  new `requirements.txt` support, `Cargo.toml`), writes/refreshes
  `vendor.toml` at `depth = surface` with no prompts or AI calls, and
  regenerates trees, the routing table, and a new unconditional
  tool-level Skill (`depcompass.skill.write_tool_skill`,
  `decisions/0020`, `.claude/skills/depcompass/SKILL.md`). Refreshing an
  already-bootstrapped project only syncs newly-discovered vendors —
  already-tracked ones, including any `depth = full`, are left untouched.
  New `depcompass promote <vendor> [--yes]`: the sole cost-disclosure/
  confirmation point (`decisions/0018`); on confirmation, escalates a
  vendor to `depth = full`, resolves and clones its real upstream
  repository (`depcompass.source_resolution`, `decisions/0021`),
  generates a grounded description (`depcompass.grounded_description`,
  replacing `gap_analysis.py` — `decisions/0019`), writes its per-vendor
  Skill and Cursor `.mdc` export (`depcompass.skill`, `decisions/0013`),
  and refreshes the routing table. Idempotent on an already-`full`
  vendor. `context_path` removed from `VendorConfig`/`vendor.toml` —
  generation is now unconditional for `depth = full`, not gated on a
  project-supplied field. `VendorDigest.gap_analysis`/
  `gap_analysis_error` renamed to `technical_description`/
  `description_error`. `vendor/<name>/src/` is now cloned from the
  vendor's upstream repository for `depth = full` vendors (refines
  `decisions/0004`'s snapshot-not-reference concern), falling back to
  the old local-install-sourced copy if source resolution fails. Each
  adapter gained `repository_url()`, resolved from already-local package
  metadata (no registry network call): npm's `package.json` `repository`
  field (respecting monorepo `directory`), Python's installed
  `Project-URL` metadata, Cargo's `cargo metadata` `repository` field. A
  PyPI vendor with no resolvable repository URL fails `promote` loudly
  rather than falling back to a source tarball.
- Phase 7 plan (`planning/phase-7-bootstrap-and-promote.md`) and five new
  ADRs — planning only, no code changed. Reconciles an external MVP-
  redefinition design doc against actual repo state (correcting the
  doc's mistaken premise that `depth = full` generation compares a
  dependency's source against the model's own training knowledge — the
  real mechanism, superseded here, compared API surface against a
  project-supplied `context_path`). `decisions/0017`: bare `depcompass`
  auto-discovers manifests and bootstraps `vendor.toml` at `SURFACE`
  with no prompts or AI calls; re-running it refreshes idempotently.
  `decisions/0018`: new `depcompass promote <vendor>` becomes the sole
  point that costs money or requires confirmation, bundling source
  resolution, generation, Skill + Cursor `.mdc` export, and an `index`
  refresh. `decisions/0019`: `FULL`-depth generation becomes grounded
  description sourced from material retrieved at `promote` time,
  replacing `context_path`-gated gap analysis (`decisions/0003`'s Haiku
  model-tier choice is unaffected). `decisions/0020`: a templated,
  unconditionally-generated tool-level Skill distinct from per-vendor
  Skills. `decisions/0021`: PyPI source resolution fails loudly rather
  than falling back to a source tarball when no repository URL resolves.
  `planning/ROADMAP.md`'s former Phase 9 (Skills + Cursor export) and
  Phase 10 (`init` bulk-discovery refinement) rows are folded into the
  new Phase 7 and removed as separate rows; later phases renumbered
  accordingly (all were `not started`).
- Staleness checking (Phase 6): `depcompass check [--strict] [--fix]` is
  real — the last MVP phase, so MVP phases 0-6 are now complete. New
  `depcompass.staleness` module: `check_all`/`check_vendor` compare a
  vendor's persisted `**Installed version:**` against the ecosystem
  adapter's live read, classifying the delta via a small custom
  `major.minor.patch` parser into `Severity.NONE`/`PATCH`/`MINOR`/`MAJOR`/
  `UNKNOWN` per `decisions/0005`'s patch-silent/minor-warns/major-hard-
  fails policy (`UNKNOWN` — an unparseable version string on either side —
  is treated as a hard-fail case). Also detects transitive-only
  (DEPTREE) drift by diffing a vendor's persisted `deptree.json` against a
  freshly built live tree when the vendor's own root version is
  unchanged — informational only, never affects `--strict`'s exit code.
  Bare `check` (no flags) is report-only and always exits 0; `--strict` is
  the CI gate (non-zero on `MAJOR`/`UNKNOWN`/a failed live-version read);
  `--fix` regenerates every stale vendor via the same `sync_vendor` `sync`
  itself uses (including gap analysis for `depth = full` vendors),
  isolating one vendor's adapter failure from the rest of the batch.
  `--strict` and `--fix` are mutually exclusive. New shared
  `claude_md.read_installed_version` helper, de-duplicating a regex
  `index.py` previously kept privately.
- AI-gated gap analysis (Phase 5): `depcompass.gap_analysis` — a single
  forced-tool-use Anthropic call per qualifying vendor
  (`generate_gap_analysis`), pinned to the dated snapshot
  `claude-haiku-4-5-20251001` rather than `decisions/0003`'s rolling
  alias, producing structured dual-audience output (technical analysis +
  conversational overview + an optional action pointer) in one call/cost
  (`decisions/0012`); `estimate_cost`/`check_budget` support `sync
  --budget <amount>`, aborting the whole run before any API call if
  projected cost is too high. `VendorDigest` gains
  `conversational_overview`, `gap_analysis_error`, `action_pointer_file`,
  and `action_pointer_note`. `sync_vendor` calls gap analysis for `depth
  = full` + `context_path` vendors, catching failures locally (the
  vendor still gets its full deterministic output, with an explicit
  "unavailable" note in `CLAUDE.md`) so one bad call doesn't block the
  rest of `sync`; a successful call additionally writes a new
  `vendor/<name>/OVERVIEW.md`. `claude_md.py`'s Gap analysis section is
  back, no longer omitted. `filetree.py`'s renderers gain an optional
  `action_pointer` parameter, closing Phase 3's deferred FILETREE-to-
  gap-analysis cross-linking loop. New ADR `decisions/0016` records that
  no test in this project ever makes a real Anthropic API call.
- Initial project scaffolding (Phase 0): MIT license, Python packaging
  (setuptools, `src/depcompass/` layout, `requires-python >=3.11`),
  process-rules `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`,
  `architecture/overview.md`, nine architecture decision records
  (`decisions/0001`-`0009`), forward-looking `docs/cli-reference.md` and
  `docs/config-schema.md`, and an empty `tests/` skeleton. No CLI
  functionality is implemented yet.
- Core data models and `vendor.toml` parsing (Phase 1): `depcompass.core`
  (`VendorConfig`, `Ecosystem`, `Depth`, `DepNode`, `VendorDigest`),
  `depcompass.config` (fail-fast `vendor.toml` parsing via `tomllib`), and
  a `depcompass.cli` skeleton with all 5 planned commands registered as
  stubs. Two new ADRs (`decisions/0010`, `decisions/0011`).
- `planning/ROADMAP.md`: a full-roadmap phase-status table (all 13
  phases, MVP milestone vs post-MVP), distinct from `planning/CONTEXT.md`'s
  current-phase-only session-resumption view.
- Phase 2 plan (`planning/phase-2-ecosystem-adapters.md`): scopes the
  `EcosystemAdapter` ABC and npm/Python/Cargo adapter implementations.
  Adapter code itself is not yet implemented.
- Deterministic tree generation (Phase 3): `depcompass.symbols`
  (`Symbol(name, purpose)` plus `extract_python_symbols`,
  `extract_rust_symbols`, a new `extract_npm_symbols`, and
  `purpose_for_file` with a generic comment-marker fallback);
  `depcompass.deptree` (`render_deptree_markdown`/`render_deptree_json` —
  diamond-dependency dedup, dev-only collapsing to a count, an explicit
  depth-cap collapse notice); `depcompass.filetree`
  (`render_filetree_markdown`/`render_filetree_json`/`build_symbol_index`
  — pruned directory walk, per-file purpose annotations, a capped flat
  symbol index). New ADR `decisions/0015` records the reuse-adapter-
  parsing extraction strategy. `adapters/cargo.py` and `adapters/python.py`
  now call into `symbols.py` instead of keeping private extraction copies.
- Real `init`/`sync`/`index` commands (Phase 4): `depcompass.adapters.get_adapter`
  dispatch; `depcompass.claude_md.render_vendor_claude_md` (per-vendor
  `CLAUDE.md` template — Metadata with the load-bearing `**Installed
  version:**` line, Grounding preamble, API surface, Known gotchas
  sourced from `DepNode.side_effects`, Quick links; Gap analysis section
  omitted until Phase 5); `depcompass.sync` (`sync_vendor`/`sync_all` —
  per-vendor orchestration writing `FILETREE.md`/`DEPTREE.md`/
  `filetree.json`/`deptree.json`/`CLAUDE.md` under `vendor/<name>/`, plus
  a pruned `vendor/<name>/src/` snapshot copy for `depth = full`);
  `depcompass.index` (`load_routing_rows`/`render_routing_table`/
  `update_root_claude_md` — idempotent marker-based routing-table
  injection that reads persisted per-vendor `CLAUDE.md` files rather than
  re-running `sync`); `depcompass.discovery` (`discover_npm`/
  `discover_python`/`discover_cargo`/`write_vendor_toml` — manifest-based
  `vendor.toml` bootstrap for `init --scan`, erroring rather than
  overwriting an existing file). `VendorDigest` gains a `side_effects`
  field. `cli.py`'s `init`/`sync`/`index` commands are wired to this real
  logic; `_write_claude_md` stub removed.
- Ecosystem adapters (Phase 2): `depcompass.adapters` — `EcosystemAdapter`
  ABC and a shared `_run_json` subprocess seam (`base.py`); `NpmAdapter`,
  `PythonAdapter`, and `CargoAdapter` implementing `installed_version`,
  `source_location`, `readme_and_api_surface`, and `dependency_tree`
  against `npm ls`, `pipdeptree`, and `cargo metadata` respectively.
  `pipdeptree` added as a real dependency. New ADR `decisions/0014`
  records the fixture-mocked testing strategy, which caught two real
  cross-platform subprocess bugs during implementation (see Fixed,
  below). The Cargo adapter is unverified against real `cargo` output —
  no Rust toolchain is available in this dev environment.

### Fixed

- `_run_json`'s subprocess seam now resolves the target tool via
  `shutil.which` before invoking it, fixing two real bugs surfaced by
  Phase 2's live smoke tests: on Windows, a bare `npm` couldn't be
  launched by `subprocess.run` without a shell (it resolves to a `.cmd`
  shim); a bare `pipdeptree` wasn't reliably on `PATH` outside an
  activated venv (now invoked as `sys.executable -m pipdeptree`).

### Removed

- `depcompass.gap_analysis` module and `VendorConfig.context_path` field
  (Phase 7) — replaced by `depcompass.grounded_description` and
  `depcompass.source_resolution` (`decisions/0019`, `decisions/0021`).
  An existing `vendor.toml` with `context_path` lines still parses
  cleanly (the field is simply ignored, not rejected); `depth = full`
  no longer requires it.
- `VendorDigest.is_stale` (Phase 6) — the property, its `_stale` field,
  and the Phase-1 docstring promising a future staleness check would
  populate it. `check` (Phase 6) never builds a `VendorDigest`, so no code
  path could ever set it; `depcompass.staleness.VendorStaleness` replaces
  it as `check`'s own return type.

### Changed

- `index.py`'s `load_routing_rows` (Phase 6) now calls the new shared
  `claude_md.read_installed_version` instead of keeping its own private
  copy of the `**Installed version:**` regex — behavior-preserving,
  de-duplication only.
- `filetree.render_filetree_markdown`/`render_filetree_json` (Phase 5)
  gain an optional `action_pointer: tuple[str, str] | None = None`
  keyword — additive and non-breaking; every existing Phase 3/4 call
  site and test is unaffected.
- `docs/cli-reference.md`'s `init --scan` syntax (Phase 4): corrected from
  one flag followed by space-separated files to a repeated flag
  (`--scan a --scan b`) — the originally documented syntax isn't how a
  named Click/Typer option works.
- `index`'s implementation deviates from `planning/phase-4-sync-index-init.md`'s
  literal `render_routing_table(digests: list[VendorDigest])` signature:
  it reads persisted per-vendor `CLAUDE.md` files instead of accepting
  fresh digests, so it never re-runs `sync` — re-running `sync` inside
  `index` would make it silently pay gap-analysis AI cost once Phase 5
  lands. See `architecture/overview.md`'s Known footguns.
- `CargoAdapter.readme_and_api_surface()`'s output format (Phase 3):
  extracted items now render as `name: purpose` instead of the raw `pub
  fn ...` signature line, as a consequence of switching to
  `symbols.extract_rust_symbols`'s name-based extraction. See
  `decisions/0015`.
- `CLAUDE.md` and `CONTRIBUTING.md` now require keeping
  `planning/ROADMAP.md` in sync: added to it when a phase's plan file is
  created, marked `done` when a phase finishes.
- **Design decision, not yet shipped**: the chat REPL (Phases 7-8) is now
  designed as a primary consumption mode for vendor digests, not a
  convenience layer. Phase 5's gap analysis will produce dual-audience
  output (technical + a conversational overview, same call/cost); Phase
  8's REPL will load a project-wide dependency rollup unconditionally at
  session start rather than routing to it. See `decisions/0012`.
- **Design decision, not yet shipped**: Agent Skills become the primary
  multi-tool export target (Phase 9), one Skill per `FULL`-depth vendor,
  addressing a reliability gap in the `CLAUDE.md` routing table's soft
  "consult this digest" instruction. Cursor `.mdc` export and the
  `CLAUDE.md` routing table are retained as fallbacks, not replaced.
  Phase 8's REPL Tier 1 routing will consume the same generated Skill
  description text Phase 9 produces, rather than independently-authored
  matching, and the REPL gains an explicit escalation path to the
  generated Skill folder for questions exceeding digest-only scope. See
  `decisions/0013`.
