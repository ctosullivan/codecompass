---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Connector

## Definition

**"Connector" is not a real, distinct CodeCompass concept.** A
repository-wide, case-insensitive search
(`grep -rni "connector" --include="*.py" --include="*.md"
--include="*.yaml" --include="*.yml" --include="*.toml" .`) finds no
use of this word to name any CodeCompass mechanism, class, table, or
concept anywhere in `src/`, `docs/`, `architecture/`, `ai-docs/`, any
`decisions/*.md` ADR body, or `tests/` (`EV-ADPT-004`).

Every occurrence of "connector" in this repository resolves to one of
exactly two categories:

1. **This Phase 63D research effort's own planning-document lists of
   candidate concepts to investigate** —
   `decisions/0060-scope-plan-domain-design-implement-methodology.md`,
   `planning/phase-63d-domain-reconstruction.md`,
   `planning/v1-redefinition/development-methodology.md`,
   `planning/v1-redefinition/roadmap.md`, `planning/ROADMAP.md`,
   `CHANGELOG.md` — every one of these lists "connector" alongside
   "adapter, protocol, reference, decision, invariant" purely as a term
   *to research*, never as a term already defined or used for a
   mechanism. (`planning/CONTEXT.md` also listed it at the time of this
   corpus's own approval, but no longer does — Phase 66 rewrote that
   file into a current-only document per `CLAUDE.md` §4, dropping its
   own historical phase-63D-planning narrative; verified 2026-09-24,
   `EV-SKEP-003`.)
2. **One unrelated hit inside a vendored third-party reference
   digest** — `.claude/skills/codecompass-anthropic/references/FILETREE.md:1242`
   describes a field (`beta_tunnel_token.py` — "A tunnel's connector
   token") inside Anthropic's own Python SDK, a vendored dependency's
   generated file-tree digest. This describes Anthropic's own SDK, not
   CodeCompass, and has no relationship to CodeCompass's own adapter
   machinery.

## What it might be confused with

- **The broader Claude/MCP ecosystem's own "connector" concept**
  (a hosted third-party integration a Claude client can attach to).
  CodeCompass has never implemented MCP — "MCP" is Phase 25 in
  CodeCompass's own roadmap, explicitly marked **deferred, not
  started**, and no MCP-related source file exists in
  `src/codecompass/` at this revision. A reader arriving from the
  wider Claude/MCP world with an existing notion of "connector" should
  not assume it maps onto anything CodeCompass currently builds.
- **CodeCompass's own `adapter`** (`adapter.md`) — the actual, evidenced
  mechanism nearest in meaning: something CodeCompass talks to over a
  boundary (a native tool, or an external process) to get ecosystem
  information. If a reader means "the thing CodeCompass uses to talk to
  npm/Cargo/Haskell," the correct CodeCompass term is **adapter**, not
  connector.

## Invariants

None — there is no mechanism to state an invariant about.

## Example

None — there is no real usage to draw an example from.

## Counterexample / edge case

None found. Unlike every other concept in this cluster (adapter,
protocol, vendor, ecosystem, capability — each has at least one real
implementation and at least one genuinely fuzzy edge case), this
concept's honest finding is a null result: no usage exists to draw an
edge case from. This is stated plainly per the phase's own instruction
to record "none found yet" rather than silence, and per the same
instruction never to invent a definition to fill the template.

## Relationships

- **is-not** `adapter.md` (the actual nearest CodeCompass concept).
- **is-not** anything related to `protocol.md` (the external adapter
  wire protocol never uses this word for its own `initialize`/
  `analyze_project`/`shutdown` methods or its `dependencies`/`symbols`/
  `observations`/`diagnostics` capability set).
- **has no relationship to** MCP, which is itself unimplemented in this
  project.

## References

- `EV-ADPT-004` — `planning/knowledge/codecompass-domain/EV-ADPT-004.yaml`
- `CL-ADPT-004`, `DE-ADPT-004` —
  `planning/knowledge/codecompass-domain/`
- `OBS-ADPT-009` (the grep itself, with every hit classified) —
  `planning/knowledge/codecompass-domain/OBS-ADPT-009.yaml`
- `decisions/0048-redefined-v1-is-a-product-validation-milestone.md`
  (Phase 25/MCP deferred, not renumbered)
