# 0002. Adapter approach differs per ecosystem

## Status

Accepted

## Context

`EcosystemAdapter` defines a common interface (`installed_version`,
`source_location`, `readme_and_api_surface`, `dependency_tree`), but npm,
PyPI, and crates.io have no shared lockfile format, no shared "public API
surface" convention, and no shared dependency-tree tooling output shape.

## Decision

Each adapter implements the common interface using whatever native tooling
its ecosystem already provides, rather than a single unified parsing
strategy:

- **npm** — `package.json` + `npm ls --json` for version/tree; README +
  `.d.ts` files (capped at 5 files) for API surface.
- **Python** — `pip show` / installed package metadata for version;
  `pipdeptree --json` for tree; `.pyi` stubs where present, else top-level
  docstrings/`__all__` exports, for API surface.
- **Cargo** — `cargo tree` / `cargo metadata --json` for version/tree;
  public (`pub`) function/struct signatures for API surface (with
  `rustdoc --output-format json` as a candidate refinement, not assumed
  up front).

Each ecosystem's adapter is expected to need its own judgment calls — the
npm adapter's approach is not assumed to transfer directly to Python or
Cargo.

## Alternatives considered

- **Hand-rolled parsers per manifest format**, ignoring each ecosystem's
  own `--json`-capable tooling. Rejected — reinvents what package managers
  already expose, and would need to track upstream manifest format changes
  independently instead of inheriting them for free.
- **A single unified "API surface" extraction heuristic** (e.g. purely
  regex/AST-based across all three languages). Rejected — npm has `.d.ts`
  as a strong canonical signal that Python and Cargo don't have equivalents
  of; forcing one heuristic across all three would produce a weaker result
  for npm and no better a result for the others.

## Consequences

- Three adapter implementations with meaningfully different internals,
  not three thin wrappers around one shared parser.
- Adding a fourth ecosystem later means writing a new adapter from
  scratch's ecosystem-native tooling, not extending a generic parser.
- The `.d.ts` 5-file cap and the Python/Cargo API-surface fallbacks are
  first-pass heuristics, expected to need tuning once tested against real
  packages (see `architecture/overview.md`'s Known footguns section).
