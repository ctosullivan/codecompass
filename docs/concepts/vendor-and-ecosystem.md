# Concepts: ecosystem, vendor, and `vendor.toml`

These three concepts are related but distinct, and worth keeping apart:

<!-- codecompass-grounded-by: CL-ADPT-004 CL-ADPT-012 region:vendor-and-ecosystem-md-ecosystem-vendor-adapter -->
## Ecosystems, Vendors, and Adapters

CodeCompass organizes its support for external dependencies around three distinct concepts: ecosystem, vendor, and adapter. An ecosystem is a fixed, closed category with exactly four members -- npm, python, cargo, and haskell -- and it is not something configured on a per-project basis. A vendor is a single tracked dependency, represented as a `VendorConfig(name, ecosystem)` entry defined in `vendor.toml`, and every vendor belongs to exactly one ecosystem, for example `VendorConfig(name="hledger-lib", ecosystem=Ecosystem.HASKELL)`. An adapter is an `EcosystemAdapter` subclass that implements the ecosystem-specific logic for one particular `Ecosystem` value, such as `HaskellAdapter` for `Ecosystem.HASKELL`.

These three concepts relate to each other in a specific way. Multiple vendors can share the same ecosystem -- several Haskell vendors all use `Ecosystem.HASKELL` -- and in that case they also share the same adapter class. However, each vendor is still given its own adapter instance, constructed fresh for that vendor via `get_adapter`, scoped to that vendor's own configuration and project root rather than being tracked as persistent project state the way a vendor entry is. This "one vendor, one adapter instance" pattern is not guaranteed by the filesystem layout itself: a single project root can contain source for more than one vendor, as seen in `HaskellAdapter`'s monorepo resolution logic (`_resolve_package_dir`), where one `hledger` checkout hosts `hledger-lib`, `hledger`, and `hledger-ui` together. Because of this, an adapter instance is responsible for narrowing its assigned project root down to the specific subdirectory matching its own vendor's name before any of its other methods can be called meaningfully. If a `vendor.toml` entry names an ecosystem string outside the four-member enum, that entry is rejected at config-load time, before `get_adapter`'s dispatch table is ever reached.

If you encounter the term "connector" while working with CodeCompass, it does not refer to any distinct mechanism in this project -- it names nothing in the source tree, documentation, architecture notes, or ADRs. The actual, implemented mechanism for ecosystem-specific dependency handling is the adapter, either as the `EcosystemAdapter` base class or as the external-process protocol client built on it.
<!-- /codecompass-grounded-by -->

`VendorConfig` is deliberately narrow — just `name` and `ecosystem` — as of a project history point referenced as `decisions/0031`/`decisions/0035`: an earlier per-vendor `depth` toggle (`SURFACE`/`FULL`, which used to gate a pinned source snapshot and an AI-generated description) was retired. Cloning is now unconditional for every tracked vendor, and AI enrichment is usage-driven (see `docs/workflows/sync-and-enrichment-pipeline.md`), not a per-vendor configuration flag. A legacy `vendor.toml` entry still carrying a `depth = "..."` key continues to parse without error — the field is simply never read (`src/codecompass/config.py`). (This paragraph is deliberately outside the compiled region above: no formal knowledge record currently cites this specific backward-compatibility fact — see the Stage 87C plan's own §S.6 for the evidence trail — so it stays human-authored rather than compiled without a citation.)

## `vendor.toml` — the file format

A project's own tracked-dependency manifest. See `docs/reference/configuration.md` for the full field reference.
