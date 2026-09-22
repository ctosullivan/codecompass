---
status: DRAFT — pending domain-skeptic review and actual-user approval
---

# Vendor

## Definition

A **vendor** is one tracked dependency: a `VendorConfig` entry
(`src/codecompass/core.py`), a frozen dataclass of exactly
`(name: str, ecosystem: Ecosystem)`, sourced from one `[[vendor]]`
entry in `vendor.toml`. A vendor belongs to exactly one `Ecosystem`
value. `VendorConfig` was deliberately narrowed to just this pair in
Phase 16 (`decisions/0031`, `decisions/0035`), retiring an earlier
per-vendor `depth` (SURFACE/FULL) toggle field — cloning is
unconditional now, and AI enrichment is usage-driven rather than a
`vendor.toml` field (`EV-ADPT-005`).

**This is the "three related but distinct concepts" cluster** — see
`ecosystem.md` and `adapter.md` for the other two, and the worked
example below for how all three fit together.

## What it is NOT

- **Not an `Ecosystem`.** `Ecosystem` is a fixed, closed 4-member enum
  (a category); a vendor is one specific tracked dependency that
  *belongs to* one ecosystem value. Many vendors can share one
  ecosystem.
- **Not an `adapter`.** An adapter is the *code* implementing
  ecosystem-specific logic; a vendor is *data* — configuration state
  tracked in `vendor.toml`, with no logic of its own. An adapter
  instance is constructed *from* a vendor's `VendorConfig` plus a
  `project_root`, not the other way around.
- **Not itself a "package" in some general sense** — it is specifically
  CodeCompass's own tracked-dependency record, tied to this project's
  `vendor.toml` schema and to `context-graph.db`'s `vendors` table (the
  deterministic-facts side, out of this cluster's own investigation
  scope but the natural downstream consumer of a `VendorConfig`).

## Invariants

- Exactly two fields, always: `name`, `ecosystem`. No per-vendor
  strategy toggle exists anymore (retired Phase 16).
- A `VendorConfig`'s `ecosystem` value is always one of the four
  `Ecosystem` enum members — never a free string.
- `get_adapter(config, project_root)` is total over every valid
  `VendorConfig` — there is no vendor whose `ecosystem` value fails to
  resolve to an adapter class (`EV-ADPT-001`).

## Example

`VendorConfig(name="hledger-lib", ecosystem=Ecosystem.HASKELL)` is one
vendor entry. `Ecosystem.HASKELL` is the fixed enum member it belongs
to. `HaskellAdapter` is the adapter class `get_adapter` constructs for
*any* `VendorConfig` whose `ecosystem` is `Ecosystem.HASKELL` — a
second Haskell vendor (e.g. `VendorConfig(name="hledger", ecosystem=Ecosystem.HASKELL)`)
would share the same adapter *class* but get its own adapter
*instance*, scoped to its own name and `project_root` resolution
(`EV-ADPT-005`).

## Counterexample / edge case

**A shared `project_root` does not imply a one-to-one vendor-to-directory
mapping.** In a monorepo (e.g. the real `hledger` monorepo, containing
`hledger-lib`, `hledger`, and `hledger-ui` side by side), multiple
distinct vendors can share one `project_root` on disk; it is the
*adapter instance*, not the vendor record itself, that is responsible
for narrowing down to the correct subdirectory for its own vendor's
name (`HaskellAdapter._resolve_package_dir`, `decisions/0057`'s
"Monorepo package roots" section, `EV-ADPT-005`). A `VendorConfig`
itself carries no path information at all — it names *what* is tracked,
never *where* on disk it resolves to; that resolution is entirely the
adapter's own job, performed fresh on every call.

## Relationships

- **belongs-to** exactly one `ecosystem.md` value.
- **is-the-input-to** exactly one `adapter.md` instance per
  `(VendorConfig, project_root)` pair, via `get_adapter`.
- **is-distinct-from** both neighbors — see "What it is NOT" above.

## References

- `EV-ADPT-005` — `planning/knowledge/codecompass-domain/EV-ADPT-005.yaml`
- `CL-ADPT-005`, `DE-ADPT-005` —
  `planning/knowledge/codecompass-domain/`
- `src/codecompass/core.py:13-35`
- `decisions/0002-adapter-approach-differs-per-ecosystem.md`
- `decisions/0031`, `decisions/0035` (Phase 16 narrowing —
  cited by `core.py`'s own `VendorConfig` docstring, not independently
  re-read in full this cluster's own investigation)
