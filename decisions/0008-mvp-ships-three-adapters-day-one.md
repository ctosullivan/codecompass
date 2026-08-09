# 0008. MVP ships npm, Python, and Cargo adapters on day one

## Status

Accepted

## Context

Ecosystem support could be rolled out incrementally (e.g. npm first,
validate the approach, then add Python and Cargo later) or all at once.

## Decision

The MVP (roadmap phases 0-6) ships all three adapters — npm, Python, and
Cargo — from the start, rather than an npm-first incremental rollout.

## Alternatives considered

- **npm-first incremental rollout**, adding Python and Cargo as later,
  separate milestones. Rejected — depcompass's core value proposition is
  ecosystem-agnostic grounding for AI agents; committing to three adapters
  from the outset forces the `EcosystemAdapter` interface to actually
  generalize across meaningfully different tooling (`npm ls --json` vs
  `pipdeptree --json` vs `cargo metadata --json`, `.d.ts` vs `.pyi` vs
  `pub` signatures) before any single ecosystem's assumptions get baked
  into the shared interface. An npm-first approach risks shipping an
  adapter abstraction that quietly assumes npm-shaped answers everywhere.

## Consequences

- More upfront implementation work in Phase 2 (three adapters instead of
  one) before the deterministic tree-generation and `sync`/`check` loop
  can be demonstrated end-to-end.
- The adapter interface (`installed_version`, `source_location`,
  `readme_and_api_surface`, `dependency_tree`) is validated against three
  different tool ecosystems before MVP ships, reducing the risk of a
  costly interface redesign once a fourth ecosystem is added post-MVP.
- Local dev/testing for the Cargo adapter specifically requires `cargo`/
  `rustc` to be installed — as of Phase 0 scaffolding, this toolchain is
  not present in the primary dev environment, which is a Phase 2 setup
  concern to flag, not a Phase 0 blocker.
