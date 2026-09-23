# `vendor.toml` config schema

> `codecompass.config.load_vendor_config()` parses this format, and
> `init`/bare `codecompass`/`sync`/`index`/`check` read/write it for real
> — see [`docs/cli-reference.md`](cli-reference.md). `promote` was removed
> in Phase 15 ([`decisions/0033`](../decisions/0033-promote-retired-universal-cloning-and-auto-triggered-consent.md)):
> AI enrichment is now usage-driven and automatic, not a per-vendor field
> or a separate command.

`vendor.toml` lives at the root of the consuming project and has one table
per tracked dependency.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Dependency name, as published (e.g. `turndown`, `requests`, `serde`). |
| `ecosystem` | string, one of `npm` \| `python` \| `cargo` \| `haskell` | yes | Which `EcosystemAdapter` handles this vendor. `haskell` (Phase 60) is handled by an **external adapter process**, not in-process Python — see [`docs/external-adapters.md`](external-adapters.md). |

No other fields are read. Historical fields (`context_path`, `depth`)
removed in Phase 7/16 are safely ignored if present — see
[`decisions/0031`](../decisions/0031-depth-retired-enrichment-is-usage-driven.md).

## What every tracked vendor gets

Every vendor listed in `vendor.toml` gets, on `sync`: metadata + public
API surface, a pinned source snapshot at `vendor/<name>/src/` (sourced
from the vendor's own upstream repository —
[`decisions/0021`](../decisions/0021-pypi-source-resolution-fails-loudly.md)),
and generated dependency/file trees. A vendor additionally gets a
Description section (technical description, conversational overview, and
an optional action pointer) once usage-driven AI enrichment has run for
it — automatic, cost-disclosed, and confirmable, triggered from bare
`codecompass` or a whole-project `sync`
([`decisions/0031`](../decisions/0031-depth-retired-enrichment-is-usage-driven.md)).

## Example

```toml
[[vendor]]
name = "turndown"
ecosystem = "npm"

[[vendor]]
name = "lodash"
ecosystem = "npm"

[[vendor]]
name = "requests"
ecosystem = "python"

[[vendor]]
name = "serde"
ecosystem = "cargo"

[[vendor]]
name = "hledger-lib"
ecosystem = "haskell"
```

## Validation

Parsing is **fail-fast**: the first invalid vendor entry (a missing
required field, or an `ecosystem` value outside the allowed set) raises an
error naming the vendor and the specific problem. Parsing does not
continue on to collect every issue in the file before reporting — fix the
first error and re-run to see the next one, if any.

## Notes

- Bare `codecompass` and `codecompass init --scan` both write every
  discovered dependency as a bare `name`/`ecosystem` entry — safe and free
  to run immediately on a large existing dependency list. Bare
  `codecompass` additionally auto-discovers manifests and refreshes an
  existing `vendor.toml` idempotently, without touching already-tracked
  vendors' generated output —
  [`decisions/0017`](../decisions/0017-zero-question-deterministic-bootstrap.md).
- See `architecture/overview.md` for what `sync` produces on disk, and
  what changes once a vendor has been AI-enriched.
