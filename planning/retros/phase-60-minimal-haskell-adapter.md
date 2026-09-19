# Phase 60 retro — Minimal external Haskell adapter

- **Date:** 2026-09-19
- **Commit(s):** (this phase's own closeout commit(s), see `planning/CONTEXT.md`); plus independent commits in `codecompass-adaptor-protocol` and `codecompass-adaptor-haskell`
- **Agents used:** `context-researcher` (real Haskell export-semantics research against the pinned `hledger` checkout, `planning/knowledge/haskell-api-surface-extraction/`), `documentation-agent` (`design.md`), `knowledge-curator` (context-packet assembly + sufficiency assessment; a second dispatch to triage `CG-008`)

## Where we are

Stage F (`decisions/0056`), gated on nothing (a separate axis from Stage
E/GATE DD). Phase 60 is Stage F's first real phase: build a fourth
`EcosystemAdapter`, but — per two direct amendments before implementation
began — as the reference implementation of a genuinely **external**
adapter, in **separate, differently-licensed public repositories**,
rather than another in-process Python class. That architecture is now
real: `codecompass-adaptor-protocol` (MIT) and `codecompass-adaptor-haskell`
(GPL-3.0-or-later) both exist as real, separate, pushed GitHub
repositories, checked out as git submodules at
`protocol/codecompass-adaptor-protocol/` and `adapters/haskell/`.

## Goal

Prove CodeCompass can discover/invoke an external adapter, negotiate its
capabilities, request project analysis, receive language-neutral
structured results, ingest them with zero Haskell-specific logic in
`src/codecompass/`, preserve evidence/provenance across the process
boundary, and pass the real `hledger-lib` validation — without resolving
GATE DD or completing Phases 55-59, which stay open.

## Scope delivered vs planned

Delivered essentially the full amended plan:

- Both repositories created, real, public, with their own `LICENSE`/
  `README.md`/`CHANGELOG.md`/CI, pushed independently.
- `codecompass-adaptor-protocol`: `SCHEMA.md`, 7 JSON schemas, 7 worked
  examples, 16 conformance vectors (8 valid, 8 invalid) — all locally
  validated with `jsonschema` before every push.
- `codecompass-adaptor-haskell`: real Stack project (library +
  executable + test suite), implementing `initialize`/`analyze_project`/
  `shutdown`, dependency-tree construction via real `stack dot`/`stack ls
  dependencies`, and the full export-list scanner (`REQ-HSAPI-001`
  through `-006`).
- CodeCompass core: `Ecosystem.HASKELL`, `vendors.ecosystem` CHECK
  widened (`_SCHEMA_VERSION` 7→8, via a **non-destructive** table-rebuild
  migration, not the usual drop-and-recreate — see "What worked" below),
  `discovery.py`'s `package.yaml` discoverer (real `PyYAML`),
  `external_process.py` (generic protocol client), `haskell.py` (thin
  dispatcher), dispatch-table wiring.
- Full Phase 54c workflow run for the API-surface-extraction question:
  13 Observations, 11 Evidence, 6 Claims, 6 Derivations, 1 Decision
  (`DEC-HSAPI-001`, adopting all 6 of `design.md`'s recommendations), 6
  Requirements — all now `status: verified`.
- Fixture tests (Python: `test_adapters_external_process.py`,
  `test_adapter_haskell.py`, `test_discovery.py`/`test_graph.py`
  additions; Haskell: 10 hspec tests against real hledger-lib excerpts)
  plus a real, live end-to-end confirmation.
- `docs/external-adapters.md`, `architecture/overview.md`, `docs/config-schema.md`
  updated; `decisions/0059` (new — the `symbols.kind`/`note` wire
  extension, discovered necessary mid-implementation, not anticipated by
  either prior ADR).

**Audit cycle, disclosed in full**: `release-phase-auditor`'s first pass
returned **FAIL** on two real, narrow gaps, not softened to observations:
(1) `planning/ROADMAP.md` and `docs/external-adapters.md` both stated
`0.1.0` was already tagged when neither repository actually had a tag
yet (`git tag -l` and `git ls-remote --tags` both empty at audit time) —
a real case of documentation getting ahead of the plan's own "tag only
after successful validation" ordering; (2) `L-025` (this phase's own
candidate learning) had been filed but never triaged. Both fixed
immediately: `v0.1.0` is now a real, pushed, annotated tag in both
repositories (confirmed via `git ls-remote --tags` against each real
remote), each repo's own `CHANGELOG.md` dated to match;
`knowledge-curator` triaged `L-025`. Everything else the auditor
independently re-ran — the full test suite, `ruff`, `check_user_docs.py
--strict`, both repositories' own real CI runs via the GitHub API, a
spot-check of `REQ-HSAPI-002`/`-003` against the real Scanner.hs code,
`CG-008`'s triage writeup, `CLAUDE.md`'s protected-file diff, and that
Phases 55-59/GATE DD were not silently touched — passed clean on the
first pass.

## What was achieved

A real, live, independently-verified round trip: `codecompass sync
--yes --budget 0` against a scratch project tracking `hledger-lib`
(symlinked, not copied, into the pinned `hledger` monorepo) produced a
correct `vendors` row (`installed_version=1.52.4`,
`repository_url=https://github.com/simonmichael/hledger`, resolved via
the `github:` hpack shorthand) and a per-vendor `CLAUDE.md` correctly
rendering all 1347 real symbols the external adapter reported, including
`[reexport]`/`[undetermined]` markers and real Haddock-sourced purposes.
The 48-name export set for `Hledger.Data.AccountName` was independently
re-verified against a **live** `stack ghci :browse` run during this
retro's own writing, not merely trusted from the research phase, and
matched exactly (set equality, zero diff either direction).

## What worked

- **Running the real toolchain at every step, not assuming.** The
  `stack dot`/`stack ls dependencies` TARGET-scoping finding (`L-025`)
  would have shipped a silently-wrong dependency tree for every
  monorepo-hosted package if the bare-command form from the original
  planning pass had gone unquestioned — caught only because the
  implementation step re-ran the real commands against the real
  monorepo rather than trusting the plan's own inline example.
- **The Phase 54c workflow, under real implementation pressure, held up
  well on its second real test.** `context-researcher`'s corpus-wide
  investigation surfaced four real `module <Name>` resolution shapes, a
  CPP-gated export entry, and the export-order/doc-comment decoupling —
  none of which the task's own framing anticipated — and every one
  translated cleanly into a `REQ-` that the Haskell scanner satisfies,
  verified against real `:browse` output, not just against the research's
  own paraphrase.
- **The knowledge-curator's packet-sufficiency check caught a real,
  load-bearing gap before implementation started**: the wire schema
  (`analyze_project-response.json`) was never inspected by the Haskell
  research (which worked entirely from the source-code side), so
  `symbols` had no field for a re-export or undetermined entry.
  `decisions/0059` closed this in one small, additive, pre-0.1.0 schema
  change — cheap specifically because it was caught before, not after,
  a real release tag existed.
- **Writing the `vendors`-CHECK-widening migration as an explicit
  table-rebuild (never drop-and-recreate)** paid for its own extra
  complexity: `vendor_enrichment`/`symbol_enrichment` (paid AI output)
  are FK'd to `vendors.id` with `ON DELETE CASCADE`, and every *other*
  schema-version bump in this project's history has been safe to
  drop-and-recreate specifically because `doc_artifacts` has no such
  precious child — `vendors` does. Recreating in place (matching row
  ids preserved) is real, tested (`test_open_graph_migrates_pre_phase_60_vendors_constraint`),
  and doesn't repeat the doc_artifacts-style migration by copy-paste
  where it would have silently destroyed real enrichment data on a
  populated database.

## What didn't work

- **Not anticipating the wire-schema/research disconnect earlier.**
  Nothing in `decisions/0057`'s own original protocol design, nor in the
  research task's own framing, prompted a check of "does the wire schema
  actually have somewhere to put this richer result" until the
  knowledge-curator's own sufficiency pass caught it — a research task
  scoped purely to "what does Haskell source really do" has no natural
  reason to also inspect a JSON Schema file three directories away. Cost
  one extra ADR and one extra protocol-repo commit; would have cost a
  real implementation rewrite if caught only after `app/Main.hs` was
  written against the old three-field schema.
- **`_collect_vendor_symbols` not calling `readme_and_api_surface()`
  was only discovered by actually running `codecompass sync` and
  querying the resulting database directly** — nothing in `decisions/0057`,
  the Phase 60 plan, or any test written before this point exercised
  that specific path. Filed as `CG-008`, routed to Phase 62 by direct
  instruction rather than fixed here — correct per scope, but a reminder
  that "the adapter's own output is correct" and "the adapter's output
  reaches every consumer that should see it" are two different claims,
  and this phase's own plan verification wording ("the resulting
  `context-graph.db` row's content") was satisfied by the `vendors` row
  alone without that gap being visible from the plan text itself.

## Lessons learnt

A new architectural boundary (external process, separate repository)
doesn't just relocate an adapter's *implementation* — it also
foregrounds every place the *host* previously reached into an adapter's
internals informally. `_collect_vendor_symbols`'s own separate
Python-side symbol-extraction path was invisible as a design gap while
every adapter was in-process (an in-process adapter's own extractor and
`symbols.py`'s dispatcher could, in principle, always be unified further
without anyone noticing they weren't); it became visible immediately
once an adapter's real output had to cross a process boundary to reach
the same table. Building the first external adapter is itself a forcing
function for finding these latent seams — expect Phase 62's own
interface-consolidation work to surface more of them, not fewer, the
more of `EcosystemAdapter`'s implicit assumptions get tested against a
process boundary instead of a shared Python call stack.

## Process-improvement feedback

Dispatching `context-researcher`/`documentation-agent`/`knowledge-curator`
as real, separate agent calls (rather than the lead performing all three
roles informally) surfaced two genuine findings — the four
`module <Name>` shapes and the wire-schema gap — that a single-pass,
single-actor research-and-build effort plausibly would have missed or
discovered later, mid-implementation, at higher cost. The three-role
separation earned its own overhead again this phase, on a second real
test.

## Candidate learnings filed

`L-025` (`planning/learnings/inbox.md`) — the `stack dot`/`stack ls
dependencies` `TARGET`-scoping requirement for monorepo packages.
Triaged by `knowledge-curator`: **retained**, not promoted — the fix is
already live and already documented at its own point of use
(`Adapter/Deps.hs`'s own header haddock states the same invariant), and
no further regression-test artifact is warranted since the only call
site hardcodes the package name as a literal `TARGET` argument (no
silent-regression path exists without visibly rewriting that literal).
`CG-008` (`planning/context-gaps/inbox.md`) — the `_collect_vendor_symbols`/
`extract_symbols_for_file` gap. Triaged by `knowledge-curator`:
**promoted-to-roadmap** (`graph_capability_gap`), routed to Phase 62,
whose own roadmap stanza already names it.

## Where we're going

`0.1.0` is now tagged in both new repositories, cut immediately after
`release-phase-auditor`'s re-audit confirmed the two fixes above — the
plan's own "tag only after successful validation" ordering, followed
literally. Phase 61 (hledger cross-language experiment) can now
register `hledger-lib` as a real tracked vendor and ask Phase 54b's own
central question (does CodeCompass help recognise that two
differently-implemented things are the same behaviour) using a real,
working adapter rather than a hypothetical one. Phase 62
(adapter-interface consolidation) now has concrete evidence to assess,
including `CG-008`'s own named question. **This phase does not resolve
GATE DD and does not complete or bypass Phases 55-59** — those remain
exactly as open as before this phase started; this phase's own real
findings (the external-process architecture holding up under real
implementation, the Phase 54c workflow's second successful real test,
the `_collect_vendor_symbols` gap) are additional evidence for GATE DD's
eventual decision, not a substitute for it.

## Time / cost note

One extended session. No AI API spend (Phase 54c's own agent dispatches
are Claude Code subagents, not billed Anthropic-API enrichment calls;
the real end-to-end `codecompass sync` was run with `--budget 0`,
guaranteeing zero real enrichment spend). Real toolchain cost: one cold
`stack build` compiling the adapter's own dependency closure from
scratch (a few minutes, similar order to the earlier `aeson`
smoke-test's own cold-build cost); all subsequent builds were warm and
fast (single-digit seconds).
