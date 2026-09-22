---
status: DRAFT — pending domain-skeptic review and actual-user approval
---

# Adapter

## Definition

An **adapter**, in CodeCompass's ecosystem-integration sense, is a
concrete implementation of the `EcosystemAdapter` abstract base class
(`src/codecompass/adapters/base.py`), constructed per
`(VendorConfig, project_root)`. It implements five abstract methods
(`installed_version`, `source_location`, `readme_and_api_surface`,
`repository_url`, `dependency_tree`) plus one concrete, overridable
method (`symbols()`, Phase 62). Exactly one adapter class exists per
`Ecosystem` enum member (`npm`, `python`, `cargo`, `haskell`), selected
by `get_adapter`'s closed dispatch table
(`src/codecompass/adapters/__init__.py`) — never by naming convention,
plugin discovery, or a free-form config string.

**Two implementation strategies coexist, by deliberate design, neither
superseding the other** (`decisions/0002`, `decisions/0057`):

1. **In-process** (npm, Python, Cargo) — an importable Python class
   inside `src/codecompass/`, shelling out to each ecosystem's own
   native tooling (`npm ls --json`, `pipdeptree --json`, `cargo tree`).
2. **External-process** (Haskell, the reference implementation) — a
   thin in-process dispatcher (`HaskellAdapter`) handling simple
   manifest reads directly, delegating everything that embodies real
   ecosystem-specific *logic* (dependency-tree resolution, `.hs`
   API-surface extraction) to an independent OS process
   (`adapters/haskell/`, a separate GPL-3.0-or-later repository),
   spoken to only through a fully generic JSON-Lines client
   (`src/codecompass/adapters/external_process.py`) that carries **zero**
   ecosystem-specific knowledge and is reusable, unmodified, by any
   future external adapter.

## What it is NOT

- **Not a "vendor."** A vendor (`VendorConfig`) is *what* is tracked —
  one dependency, one `(name, ecosystem)` pair. An adapter is *how*
  CodeCompass talks to that dependency's ecosystem. See
  `vendor.md`/`ecosystem.md` for the full three-way disambiguation.
- **Not the only sense of "adapter" in this project's own
  documentation.** `architecture/overview.md` itself explicitly names a
  second, unrelated sense: **"host-output adapters"** — its own label
  for `skill.py`, `commands.py`, and `index.py`, format-specific
  renderers that "render already-computed content into tool-specific
  formats rather than abstracting a package manager." This second sense
  has **no corresponding class, ABC, or shared interface anywhere in
  source** (confirmed by grepping all three modules for the word
  "adapter" — zero hits, `EV-ADPT-007`). It exists only as an
  architecture-doc classification label. A bare, unqualified "adapter"
  in this project's own prose is genuinely ambiguous between these two
  senses — see "Counterexample" below.
- **Not "connector."** See `connector.md` — that word is not a
  distinct CodeCompass concept at all.
- **Not the wire protocol itself.** The adapter is the *code* (a class,
  or a process); the *protocol* is the contract that code speaks when
  it is the external-process kind. See `protocol.md`.

## Invariants

- Every `VendorConfig.ecosystem` value maps to exactly one adapter
  class via `get_adapter` — a closed, total dispatch table, never a
  fallback or "no adapter found" case for any of the four `Ecosystem`
  members (`EV-ADPT-001`).
- `symbols()` is deliberately **concrete, not abstract** on
  `EcosystemAdapter` — a future adapter that doesn't implement
  structured extraction is not forced to (no `TypeError` at
  construction); its default implementation walks the vendor's own
  source tree via `extract_symbols_for_file` (`EV-ADPT-001`).
- An external-process adapter's Python-side class stays a **thin
  dispatcher** — real ecosystem-specific logic never lives twice (once
  in the external process, once reimplemented in
  `src/codecompass/`) (`decisions/0057`, `EV-ADPT-002`).
- `src/codecompass/adapters/external_process.py` never mentions any
  specific ecosystem (Haskell, `stack`, `package.yaml`) anywhere in its
  own source (`EV-ADPT-002`).

## Example

`VendorConfig(name="hledger-lib", ecosystem=Ecosystem.HASKELL)` is
dispatched by `get_adapter` to `HaskellAdapter(config, project_root)`.
Calling `.installed_version()` reads `package.yaml` directly, in-process
(a simple manifest-key lookup). Calling `.dependency_tree()` or
`.symbols()` spawns (or reuses a cached) `ExternalAdapterProcess`,
sending an `analyze_project` request to the `codecompass-adaptor-haskell`
executable and converting its JSON response into `DepNode`/`Symbol`
objects (`EV-ADPT-002`).

## Counterexample / edge case

**The "one vendor → one adapter instance operating over its own,
self-contained directory" picture is not a structural guarantee.**
`HaskellAdapter._resolve_package_dir()` handles the real monorepo case:
a single `project_root` (e.g. a checkout of the `hledger` monorepo) can
contain source for *multiple* vendors (`hledger-lib`, `hledger`,
`hledger-ui`) at once. The adapter instance is responsible for
searching immediate subdirectories for the one whose own `package.yaml`
declares its *own* vendor's name, before any other method call is
meaningful — this is a documented, deliberate design point
(`decisions/0057`'s "Monorepo package roots" section), not a bug, but
it means an adapter's own `project_root` is not always its own vendor's
whole, exclusive source tree (`EV-ADPT-005`).

A second, genuinely fuzzy edge case: this project's own documentation
uses the bare word "adapter" for two unrelated things (`EV-ADPT-007`,
`CL-ADPT-007`) — see "What it is NOT" above. `architecture/overview.md`
flags this itself; it is not resolved further here, since it is a
naming-clarity observation about existing prose, not a code-level
ambiguity.

## Relationships

- **is-implemented-for** exactly one `ecosystem.md` value.
- **is-constructed-from** one `vendor.md` record (`VendorConfig`) plus a
  `project_root`.
- **speaks** `protocol.md`, only for the external-process strategy.
- **is-distinct-from** "host-output adapter" (a documentation label with
  no source-level counterpart) and "connector" (`connector.md`, not a
  real term here).

## References

- `EV-ADPT-001`, `EV-ADPT-002`, `EV-ADPT-005`, `EV-ADPT-007` —
  `planning/knowledge/codecompass-domain/`
- `CL-ADPT-001`, `CL-ADPT-002`, `CL-ADPT-005`, `CL-ADPT-007` —
  `planning/knowledge/codecompass-domain/`
- `src/codecompass/adapters/base.py:25-97`
- `src/codecompass/adapters/__init__.py:1-32`
- `src/codecompass/adapters/haskell.py:1-288`
- `src/codecompass/adapters/external_process.py:1-171`
- `decisions/0002-adapter-approach-differs-per-ecosystem.md`
- `decisions/0057-external-process-adapter-protocol.md`
- `architecture/overview.md:85-125, 226-275, 344-359`
- `tests/test_adapters_base.py`, `tests/test_adapters_dispatch.py`,
  `tests/test_adapter_haskell.py`
