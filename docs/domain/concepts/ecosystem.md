---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Ecosystem

## Definition

`Ecosystem` (`src/codecompass/core.py`) is a `StrEnum` with exactly
four members: `NPM = "npm"`, `PYTHON = "python"`, `CARGO = "cargo"`,
`HASKELL = "haskell"`. Its own one-line docstring: "Package ecosystem a
vendor belongs to." It is a **fixed, closed category** — not
configuration, not a per-project setting, and not something a vendor
or an adapter can invent a new value for at runtime (`EV-ADPT-005`).

See `vendor.md` and `adapter.md` for the full three-way disambiguation
this concept is part of.

## What it is NOT

- **Not a `vendor`.** A vendor *belongs to* one ecosystem; the
  ecosystem itself names a category of package manager, not any
  specific tracked dependency.
- **Not an `adapter`.** An ecosystem is a value; an adapter is a class
  implementing logic for that value. `get_adapter` maps each
  `Ecosystem` member to exactly one adapter class — the mapping is
  closed and total, but the enum member and the class are two
  different kinds of thing (data vs. code).
- **Not the same thing as the external adapter protocol's own
  `ecosystem` field.** This is the concept's own most important
  disambiguation — see "Counterexample" below: the wire protocol's
  `ecosystem` field (returned by an external adapter's `initialize`
  response) is explicitly **free text**, with no closed enum defined at
  the protocol-specification level (SCHEMA.md, quoted verbatim: "this
  protocol does not define a closed ecosystem enum"). CodeCompass's own
  internal `Ecosystem` type and the protocol's own wire field share a
  name and a rough meaning, but are two independently-defined things —
  one closed, one open.

## Invariants

- Exactly four members exist, and every `VendorConfig.ecosystem` value
  is one of them — never a fifth, never a free string, at the
  CodeCompass-internal level (`EV-ADPT-005`).
- `get_adapter`'s dispatch table is total over all four members — no
  `Ecosystem` value exists that fails to resolve to an adapter class
  (`EV-ADPT-001`).

## Example

`Ecosystem.HASKELL` is the enum member both `VendorConfig(name="hledger-lib",
ecosystem=Ecosystem.HASKELL)` (a vendor) and `HaskellAdapter` (an
adapter, via `get_adapter`) are keyed on.

## Counterexample / edge case

**The wire protocol's `ecosystem` field and CodeCompass's own
`Ecosystem` enum are two independent, currently-unreconciled values.**
`ExternalAdapterProcess.ecosystem` (set from an external adapter's
`initialize` response) is stored but **never subsequently read,
compared against `core.Ecosystem`, or used for any dispatch or
validation decision anywhere in `src/codecompass/`** — confirmed by a
direct grep of every `.ecosystem` attribute access in
`src/codecompass/adapters/*.py` and `sync.py` (`OBS-ADPT-017`,
`EV-ADPT-010`). Adapter dispatch is driven entirely by
`VendorConfig.ecosystem` (fixed on the CodeCompass side, via
`vendor.toml`, before any adapter process is even spawned). This means:
nothing in the current implementation would detect or surface an
external adapter reporting an `ecosystem` string that disagrees with
the `Ecosystem` value CodeCompass configured it under — the wire field
is currently write-only telemetry from CodeCompass's own perspective.
This is a real, observed gap in the current implementation, not merely
a specification looseness.

## Relationships

- **is-the-category-that** `vendor.md` belongs to (one ecosystem, many
  vendors).
- **determines** which `adapter.md` class `get_adapter` selects.
- **shares-a-name-but-not-a-definition-with** the external adapter
  protocol's own free-text `ecosystem` field (`protocol.md`) — see
  "Counterexample" above.

## References

- `EV-ADPT-001`, `EV-ADPT-005`, `EV-ADPT-010` —
  `planning/knowledge/codecompass-domain/`
- `CL-ADPT-005`, `CL-ADPT-009` — `planning/knowledge/codecompass-domain/`
- `src/codecompass/core.py:13-19`
- `src/codecompass/adapters/__init__.py:1-32`
- `src/codecompass/adapters/external_process.py:49-84`
- `protocol/codecompass-adaptor-protocol/SCHEMA.md:48-54`
