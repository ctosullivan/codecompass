# 0001. Depth is per-vendor, not global

## Status

Accepted

## Context

`Depth` (`SURFACE` vs `FULL`) controls whether a vendor only gets free
metadata/API-surface extraction or the full pinned-source-snapshot +
AI-generated gap analysis treatment. A real project can have dozens of
dependencies. Most of them are used as-is — imported, called, never
subclassed or patched — and only need surface info. A small handful are
actually extended, subclassed, or written custom rules against, and only
those justify the cost (in tokens and in the pinned-snapshot repo weight)
of `FULL`.

## Decision

`Depth` lives on `VendorConfig`, one setting per vendor entry in
`vendor.toml`. There is no global depth flag.

## Alternatives considered

- **A single global depth setting for the whole project.** Rejected — it
  forces an all-or-nothing tradeoff: either every dependency pays the
  `FULL` cost (unnecessary token/storage spend for the majority that are
  used as-is), or none do (no deep digest available for the few
  dependencies where it actually matters).

## Consequences

- `vendor.toml` entries are slightly more verbose (one `depth` field per
  vendor) than a single project-wide setting would be.
- `depcompass init --scan` can safely default every discovered dependency
  to `SURFACE` — cheap, no upfront cost decision required — and let
  promotion to `FULL` happen selectively and reactively later.
