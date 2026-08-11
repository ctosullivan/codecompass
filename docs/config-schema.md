# `vendor.toml` config schema

> As of Phase 7, `depcompass.config.load_vendor_config()` parses this
> format, and `init`/`sync`/`index`/`promote` read/write it for real,
> including `promote`'s AI-gated grounded-description generation for
> `depth = full` vendors. `check` is fully implemented (Phase 6). `chat`
> is still a stub — see [`docs/cli-reference.md`](cli-reference.md).

`vendor.toml` lives at the root of the consuming project and has one table
per tracked dependency.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Dependency name, as published (e.g. `turndown`, `requests`, `serde`). |
| `ecosystem` | string, one of `npm` \| `python` \| `cargo` | yes | Which `EcosystemAdapter` handles this vendor. |
| `depth` | string, one of `surface` \| `full` | yes | See below. Set **per vendor** — not a project-wide setting (see [`decisions/0001`](../decisions/0001-depth-is-per-vendor-not-global.md)). |

`context_path` (a Phase 5 field, pointing at the consuming project's own
README/spec to ground gap analysis) was removed in Phase 7
([`decisions/0019`](../decisions/0019-grounded-description-replaces-gap-analysis.md)):
`depth = full` no longer requires or accepts any companion field.

## `depth` values

- **`surface`** — metadata + public API surface only. No AI call, no
  pinned source copy. The default for everything discovered by bare
  `depcompass` or `depcompass init --scan`.
- **`full`** — everything `surface` produces, plus a pinned source
  snapshot at `vendor/<name>/src/` (now sourced from the vendor's own
  upstream repository, not the local install —
  [`decisions/0021`](../decisions/0021-pypi-source-resolution-fails-loudly.md))
  and an AI-generated grounded description
  ([`decisions/0019`](../decisions/0019-grounded-description-replaces-gap-analysis.md)).
  Only reachable via `depcompass promote <vendor>`
  ([`decisions/0018`](../decisions/0018-promote-is-the-sole-reactive-depth-escalation-point.md))
  — the sole command that costs money or asks anything. Reserve this for
  the handful of dependencies you're actually extending, subclassing, or
  writing custom rules against.

## Example

```toml
[[vendor]]
name = "turndown"
ecosystem = "npm"
depth = "full"

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
required field, or an `ecosystem`/`depth` value outside the allowed set)
raises an error naming the vendor and the specific problem. Parsing does
not continue on to collect every issue in the file before reporting — fix
the first error and re-run to see the next one, if any.

## Notes

- Bare `depcompass` and `depcompass init --scan` both write every
  discovered dependency with `depth = "surface"` — safe and free to run
  immediately on a large existing dependency list. Bare `depcompass`
  additionally auto-discovers manifests and refreshes an existing
  `vendor.toml` idempotently, without touching already-tracked vendors
  (including any at `depth = "full"`) —
  [`decisions/0017`](../decisions/0017-zero-question-deterministic-bootstrap.md).
- `depcompass promote <vendor>` is the only way a vendor reaches
  `depth = "full"`; it discloses estimated cost and asks for
  confirmation before making any AI call. Re-running it on an
  already-`full` vendor regenerates in place rather than erroring.
- A `depth = "full"` vendor's source resolution can fail — most commonly
  for PyPI packages with no recognized repository URL in their published
  metadata. `promote` fails loudly for that vendor rather than falling
  back to a source tarball; the vendor stays at its current depth.
- Once a vendor is `depth = "full"`, an AI call runs on *every*
  subsequent `sync`, not just the next one — generation isn't cached.
  If several vendors are promoted, `sync --budget <amount>` refuses to
  run at all (rather than partially) once the estimated cost for that
  run exceeds the cap.
- See `architecture/overview.md` for what `surface` and `full` actually
  produce on disk.
