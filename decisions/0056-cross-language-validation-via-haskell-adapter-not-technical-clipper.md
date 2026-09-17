# 0056. Cross-language validation via a minimal Haskell adapter, not Technical Clipper

## Status

Accepted (2026-09-17).

## Context

`decisions/0052` moved Technical Clipper (a zero-runtime-dependency
TypeScript/npm browser extension) to a new Stage F, reframed from "first
proof point" to "cross-ecosystem regression" — the check that
Ledgerkit-driven Stage C/D/E changes generalise rather than accidentally
becoming accounting-shaped. `planning/v1-redefinition/roadmap.md`'s
Stage F (Phases 60-63) implements this as a full reference-project
protocol run: register, one or more genuine tasks, consolidate, decide
(GATE DF).

Two things argue for revisiting this before Stage F ever runs (Stage D
is complete through Phase 55b; Stage F hasn't started):

1. **Technical Clipper's own substantive context (DOM APIs, Chromium MV3,
   CommonMark rendering) sits almost entirely outside any package graph
   CodeCompass could ever represent without inventing browser/platform-API
   modelling largely unrelated to this project's own core hypothesis**
   (dependency-source grounding). It tests whether CodeCompass's *existing*
   model overfits to Python/accounting — a real, valid question — but
   answering it doesn't exercise the actual mechanism most likely to
   reveal whether the adapter *architecture* itself (`decisions/0002`)
   generalises, since Technical Clipper's own ecosystem (npm) is already
   one of the three shipped-day-one adapters (`decisions/0008`) — it's a
   regression check on existing coverage, not a test of extending it.
2. **CodeCompass's own primary reference project, Ledgerkit, targets
   hledger — a real, substantial, unrepresented-ecosystem codebase
   (Haskell/Stack) already central to every Stage B-D evaluation this
   project has run.** A real Haskell toolchain is already present in
   this development environment (`stack`, confirmed working — the exact
   toolchain the pinned local hledger clone was built with), unlike the
   Cargo adapter's own multi-phase-long "no Rust toolchain available"
   gap (`decisions/0014`). Building a genuine fourth ecosystem adapter
   against a codebase this project already knows intimately (real
   compat-register evidence, real differential-testing workflow, real
   `package.yaml`/`.cabal` metadata already inspected during Phase 54)
   is a stronger, more concrete test of `decisions/0002`'s own claim
   ("adding a fourth ecosystem later means writing a new adapter from
   scratch's ecosystem-native tooling, not extending a generic parser")
   than a TypeScript regression check ever could be — and it does so
   using evidence and tooling this project already has in hand, not a
   second unrelated reference project's own separate context.

Separately: the Cargo adapter remains unvalidated against a real
toolchain (`decisions/0014`, still outstanding as of this ADR), and no
work has ever exercised the npm adapter beyond its own original MVP
build. Continuing to treat "deepen Rust/JS adapter maturity" as
roadmap-driving work, on top of a new cross-language adapter effort,
would split focus across three fronts at once for no evidenced
near-term benefit — nothing in this project's own evidence stream (six
consistent LOW-advantage Ledgerkit findings, zero Rust/JS-specific
findings of any kind) currently demands deeper Rust/JS validation ahead
of the Haskell question.

## Decision

Replace Stage F's cross-ecosystem-regression target: a minimal Haskell
`EcosystemAdapter` implementation, validated against hledger itself (the
same codebase every prior Ledgerkit-facing evaluation has already used),
becomes the primary remaining cross-project validation effort before v1
consolidation. Technical Clipper is not dropped — it remains a
registered, valid future reference project (`reference-project-protocol.md`'s
existing material is preserved, not deleted) — but it no longer drives
near-term roadmap sequencing or v1 architecture decisions. Rust
(Cargo) and JavaScript/TypeScript (npm) adapter *maturation* work
(deeper toolchain validation, broader real-world exercise) is
correspondingly demoted from near-term priority to later ecosystem
expansion work, picked up only if a real project incidentally requires
it (exactly as Ledgerkit's own zero-dependency shape has never required
either).

Revised Stage F sequence (`planning/v1-redefinition/roadmap.md`,
Phases 60-63, same numbers, new content — Stage G's own 64-70 numbering
is undisturbed):

1. **Minimal Haskell adapter** (Phase 60) — a real `EcosystemAdapter`
   implementation for Haskell/Stack, following `decisions/0002`'s own
   per-ecosystem-native-tooling precedent (`package.yaml`/`.cabal` for
   version/metadata, `stack ls dependencies`/`stack query` for the
   dependency tree, exported-module signatures for API surface) — no
   Haskell-specific logic added anywhere outside the adapter boundary.
2. **hledger cross-language experiment** (Phase 61) — track hledger (or
   `hledger-lib`) itself as a real CodeCompass-tracked vendor through the
   new adapter; generate real digests; evaluate materially the same way
   every Ledgerkit task has been evaluated (`context-quality-evaluation.md`'s
   instrument, independent `context-evaluator` rating).
3. **Adapter-interface consolidation** (Phase 62) — assess
   `EcosystemAdapter`'s own contract against what the Haskell adapter
   actually needed; the smallest justified interface change, if any
   (matching this project's own "smallest justified fix" discipline,
   not a speculative redesign).
4. **Lightweight ordinary-project smoke test** (Phase 63) — a
   deliberately small confirmation (not a full reference-project
   protocol run) that ordinary npm/Python/Cargo project support wasn't
   disturbed by anything Phases 60-62 changed. Technical Clipper remains
   an available, already-scouted candidate for this smoke test if
   convenient, but nothing about this phase requires it, and no
   Technical-Clipper-specific work is assumed.

Phase 67 (Stage G, final validation) is updated to reference this new
trio (self-dogfood + Ledgerkit + the Phase 63 smoke test) rather than
"Ledgerkit + Technical Clipper."

**Explicitly not touched by this decision**: Stage E (Phases 56-59, the
technical-dependency/provenance graph-ontology generalisation gated on
GATE DD/Phase 55) is a different axis of generalisation — this decision
does not fund, defer, or reshape it. GATE DD's own question stays open,
answered on its own evidence, independent of whether the Haskell
adapter spike proceeds.

## Alternatives considered

- **Keep Technical Clipper as Stage F's target, run the Haskell adapter
  work as an additional, later Stage.** Rejected: doing both in sequence
  delays the stronger, more evidence-grounded test (Haskell/hledger)
  behind a weaker one (Technical Clipper doesn't test the adapter
  interface's own generality at all, since npm is already shipped) for
  no benefit — Technical Clipper's own regression value is still
  available later, cheaply, as the Phase 63 smoke-test candidate.
- **Drop Technical Clipper entirely, deregister it.** Rejected: it
  remains a real, valid, already-registered reference project with real
  ongoing development (`reference-project-protocol.md`'s own material
  stays accurate and useful) — demoting its roadmap-driving role is not
  the same as declaring it worthless; "not required unless a real
  project incidentally needs it" preserves optionality at zero cost.
- **Fund deeper Rust/npm adapter validation now, alongside the Haskell
  work.** Rejected: no evidence currently demands it (the Cargo/npm gaps
  are known, disclosed, and non-blocking — nothing in six Ledgerkit
  evaluations or Phase 54/55b's work has ever been limited by them);
  splitting focus across three ecosystem-maturity fronts at once
  contradicts this project's own "smallest justified next step" posture.
- **Design the adapter-interface generalisation abstractly first, build
  the Haskell adapter to match.** Rejected — the entire point of this
  pivot is evidence-first: build the real adapter against real Haskell
  tooling, then consolidate the interface based on what was actually
  needed (Phase 62), not the reverse. Matches this project's own
  standing "prefer evidence-backed minimalism over ontology design"
  discipline, applied to the adapter layer instead of the graph layer.

## Consequences

- `planning/v1-redefinition/roadmap.md`: Stage D gains a numbered phase
  (54b) for the Ledgerkit reference/behaviour-validation work already
  sketched but previously unclaimed; Stage F's own header and Phases
  60-63 are rewritten for the new sequence, with the original
  Technical-Clipper content preserved below an amendment note (this
  project's own "retarget, don't delete" convention); Stage G's Phase 67
  updated.
- `planning/ROADMAP.md`'s condensed table, `planning/v1-redefinition/README.md`'s
  forward-looking roadmap summary and risk register (R10), and
  `planning/v1-redefinition/conditional-generalisation.md`'s
  Technical-Clipper-dependent evidence rows are updated to match —
  historical decision records (`realignment-2026-09.md`,
  `proposed-governance-changes.md`, `decisions/0052` itself) are left
  exactly as written, per this project's append-only convention.
- `reference-project-protocol.md`'s Technical Clipper material is not
  deleted — it remains accurate as a registration/protocol reference for
  if/when Technical Clipper is picked up again (Phase 63's smoke test,
  or later ecosystem-expansion work) — an amendment note at its top
  records that it no longer defines Stage F's own required content.
- The future modular-adapter framing this decision's title gestures at
  (independently licensed Python, Haskell, and proprietary COBOL
  adapters coexisting behind one stable interface) is aspirational
  context for *why* this test matters, not a commitment made by this
  ADR — no licensing, packaging, or plugin-boundary work is scoped here;
  that remains entirely Phase 62's (or a later phase's) evidence-driven
  call.
- No `src/codecompass/` change is made by this ADR itself — it is a
  roadmap/planning revision. The actual Haskell adapter implementation
  is Phase 60's own scoped work, not started by this decision.
