# `vendor.toml` config schema

> As of Phase 1, `depcompass.config.load_vendor_config()` parses this
> format (see [`planning/`](../planning/) for status). The CLI commands
> that read `vendor.toml` in normal use (`sync`, `check`, ...) are still
> stubs — see [`docs/cli-reference.md`](cli-reference.md).

`vendor.toml` lives at the root of the consuming project and has one table
per tracked dependency.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Dependency name, as published (e.g. `turndown`, `requests`, `serde`). |
| `ecosystem` | string, one of `npm` \| `python` \| `cargo` | yes | Which `EcosystemAdapter` handles this vendor. |
| `depth` | string, one of `surface` \| `full` | yes | See below. Set **per vendor** — not a project-wide setting (see [`decisions/0001`](../decisions/0001-depth-is-per-vendor-not-global.md)). |
| `context_path` | string | only for `depth = full` | Path to the consuming project's own README/spec, used to ground gap analysis. Without it, gap analysis output is generic and low-value — omitting it for a `full`-depth vendor is a configuration mistake, not a valid minimal config. |

## `depth` values

- **`surface`** — metadata + public API surface only. No AI call, no
  pinned source copy. The default for everything discovered by
  `depcompass init --scan`.
- **`full`** — everything `surface` produces, plus a pinned source
  snapshot at `vendor/<name>/src/` and an AI-generated gap analysis
  (requires `context_path`). Reserve this for the handful of dependencies
  you're actually extending, subclassing, or writing custom rules
  against — promote reactively, when you actually need the deeper digest,
  rather than batch-promoting everything up front.

## Example

```toml
[[vendor]]
name = "turndown"
ecosystem = "npm"
depth = "full"
context_path = "README.md"

[[vendor]]
name = "lodash"
ecosystem = "npm"
depth = "surface"

[[vendor]]
name = "requests"
ecosystem = "python"
depth = "surface"

[[vendor]]
name = "serde"
ecosystem = "cargo"
depth = "surface"
```

## Validation

Parsing is **fail-fast**: the first invalid vendor entry (a missing
required field, an `ecosystem`/`depth` value outside the allowed set, or
`depth = full` without `context_path`) raises an error naming the vendor
and the specific problem. Parsing does not continue on to collect every
issue in the file before reporting — fix the first error and re-run to
see the next one, if any.

## Notes

- `depcompass init --scan` writes every discovered dependency with
  `depth = "surface"` and no `context_path` — safe and free to run
  immediately on a large existing dependency list.
- Promoting a vendor to `depth = "full"` triggers an AI call on the next
  `sync`. If several vendors are promoted at once, `sync --budget <amount>`
  caps concurrent AI calls and prints an estimated cost before running.
- See `architecture/overview.md` for what `surface` and `full` actually
  produce on disk.
