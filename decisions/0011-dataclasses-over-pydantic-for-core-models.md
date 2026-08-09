# 0011. Core data models use stdlib dataclasses, not pydantic

## Status

Accepted

## Context

`depcompass.core`'s data model types (`VendorConfig`, `Depth`, `Ecosystem`,
`DepNode`, `VendorDigest`) need some validation — e.g. `VendorConfig`
rejecting `depth = full` without a `context_path` — and need to be easy to
construct from parsed `vendor.toml` data. Pydantic offers declarative
field validation and dict-to-model parsing out of the box, at the cost of
a new runtime dependency; stdlib `dataclasses` require writing validation
by hand (typically in `__post_init__`) but add nothing to the dependency
list.

## Decision

Core data models are implemented as stdlib `dataclasses` (`VendorConfig`
frozen; `DepNode` and `VendorDigest` mutable, since they're built up
incrementally by later phases), with validation in `__post_init__`
methods rather than a validation library.

## Alternatives considered

- **Pydantic.** Rejected for Phase 1 — the current validation surface is
  small (a handful of required fields, one enum-value check per field, one
  cross-field constraint on `VendorConfig`), which `dataclasses` handle
  without meaningful extra code. Avoiding an extra runtime dependency for
  a still pre-MVP tool keeps the dependency footprint consistent with the
  minimal-dependencies posture already set in
  [`decisions/0009`](0009-minimum-python-3-11.md) (stdlib `tomllib` over
  `tomli`).

## Consequences

- `depcompass.config`'s parsing code does its own field-presence and
  enum-conversion checks (`_require_field`, `_require_enum`) before
  constructing a `VendorConfig`, rather than getting that for free from a
  pydantic model.
- If a later phase's validation needs grow substantially — e.g. deeply
  nested structures, cross-file schema validation — that's a case to
  revisit this decision explicitly with a new ADR, not to reach for
  pydantic piecemeal without recording why.
