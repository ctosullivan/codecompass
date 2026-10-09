# Concepts: ecosystem, vendor, and `vendor.toml`

These three concepts are related but distinct, and worth keeping apart:

## Ecosystem

A fixed, closed four-member enum (`src/codecompass/core.py::Ecosystem`): `npm`, `python`, `cargo`, `haskell`. A *category*, not something you configure per project — it names which package ecosystem a given vendor belongs to, and therefore which adapter class handles it.

## Vendor

One tracked dependency: a `VendorConfig(name, ecosystem)` entry from `vendor.toml`, belonging to exactly one `Ecosystem`. For example: `VendorConfig(name="hledger-lib", ecosystem=Ecosystem.HASKELL)`.

`VendorConfig` is deliberately narrow — just `name` and `ecosystem` — as of a project history point referenced as `decisions/0031`/`decisions/0035`: an earlier per-vendor `depth` toggle (`SURFACE`/`FULL`, which used to gate a pinned source snapshot and an AI-generated description) was retired. Cloning is now unconditional for every tracked vendor, and AI enrichment is usage-driven (see `docs/workflows/sync-and-enrichment-pipeline.md`), not a per-vendor configuration flag. A legacy `vendor.toml` entry still carrying a `depth = "..."` key continues to parse without error — the field is simply never read (`src/codecompass/config.py`).

## Adapter (for cross-reference)

See `docs/concepts/adapter.md`. Many vendors can share one `Ecosystem` (and therefore one adapter *class*), but each vendor still gets its own adapter *instance*, scoped to that vendor's own configuration and project root.

## `vendor.toml` — the file format

A project's own tracked-dependency manifest. See `docs/reference/configuration.md` for the full field reference.
