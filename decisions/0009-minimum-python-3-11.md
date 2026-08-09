# 0009. Minimum supported Python is 3.11

## Status

Accepted

## Context

The original project spec left the minimum supported Python version as an
open question to resolve during Phase 0 (it affects whether `tomllib`
stdlib parsing is available or a `tomli` dependency is needed for
`vendor.toml` parsing, and which type-hint syntax — `X | Y` unions,
`match` statements — can be used throughout the codebase).

## Decision

depcompass targets Python **>=3.11** as its minimum supported version.

## Alternatives considered

- **3.9 or 3.10.** Rejected — 3.10 would still require the `tomli`
  dependency as a fallback (`tomllib` isn't stdlib until 3.11) for
  marginal additional reach, and 3.9 would additionally lose modern
  `X | Y` union type-hint syntax throughout. depcompass is a greenfield
  tool with no existing user base to preserve compatibility for, so there
  is no compatibility cost to offset against the extra dependency and
  older syntax.
- **3.12.** Considered but not chosen — no feature depcompass actually
  needs (e.g. the `type` statement) requires 3.12 specifically; setting
  the floor there would narrow adoption today without a concrete benefit
  tied to a real requirement.

## Consequences

- `tomllib` (stdlib since 3.11) is used directly for `vendor.toml`
  parsing; no `tomli` dependency in `pyproject.toml`.
- Modern `X | Y` union type hints can be used throughout the codebase
  without `from __future__ import annotations` or `typing.Union`.
- `pyproject.toml` declares `requires-python = ">=3.11"`.
