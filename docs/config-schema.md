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
| `ecosystem` | string, one of `npm` \| `python` \| `cargo` | yes | Which `EcosystemAdapter` handles this vendor. |

No other fields are read. `context_path` (a Phase 5 field) was removed in
Phase 7 ([`decisions/0019`](../decisions/0019-grounded-description-replaces-gap-analysis.md)).
`depth` (the original per-vendor `surface`/`full` toggle,
[`decisions/0001`](../decisions/0001-depth-is-per-vendor-not-global.md))
was removed in Phase 16
([`decisions/0031`](../decisions/0031-depth-retired-enrichment-is-usage-driven.md),
[`decisions/0035`](../decisions/0035-sync-vendor-reads-enrichment-from-graph-grounded-description-retired.md)):
cloning a vendor's upstream source is now unconditional for every vendor
(Phase 13, `decisions/0033`), and AI enrichment is selected from actual
usage evidence in the context graph, not a config flag. A legacy
`vendor.toml` that still carries a `depth = "surface"`/`depth = "full"`
line keeps parsing without error — the parser simply never looks at that
key. No migration and no warning; the line is just inert.

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
