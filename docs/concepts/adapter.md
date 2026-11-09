# Concept: adapter

| Ecosystem | Adapter class | Strategy |
|---|---|---|
| `npm` | `NpmAdapter` | in-process |
| `python` | `PythonAdapter` | in-process |
| `cargo` | `CargoAdapter` | in-process |
| `haskell` | `HaskellAdapter` | external-process |

This table is deterministically derived from `get_adapter`'s own closed dispatch table (`src/codecompass/adapters/__init__.py`) — kept here as a quick-reference lookup, outside the compiled region below, since it is mechanical fact rather than something knowledge-compilation composition needs to restate in prose.

<!-- codecompass-grounded-by: CL-ADPT-001 CL-ADPT-002 CL-ADPT-012 region:adapter-md-adapter-concept -->
## Adapters

An adapter is a concrete subclass of `EcosystemAdapter`, defined in `src/codecompass/adapters/base.py`. Each adapter is constructed per `(VendorConfig, project_root)` pair, and it implements five abstract methods -- `installed_version`, `source_location`, `readme_and_api_surface`, `repository_url`, and `dependency_tree` -- along with one concrete, overridable method, `symbols()`. There is exactly one adapter class per `Ecosystem` enum member, and that class is always selected through `get_adapter`'s closed dispatch table rather than through naming convention, plugin discovery, or a configuration string.

It helps to keep three related concepts separate when working with adapters: ecosystem, vendor, and adapter. `Ecosystem` is a fixed, closed four-member enum (npm, python, cargo, haskell) representing a category rather than something configured per project. A vendor is a single tracked dependency -- a `VendorConfig(name, ecosystem)` entry from `vendor.toml` -- and each vendor belongs to exactly one `Ecosystem`. An adapter is the `EcosystemAdapter` subclass that implements the ecosystem-specific logic for one `Ecosystem` value, constructed fresh for each `(VendorConfig, project_root)` pair via `get_adapter`, and it is not itself tracked as project state the way a vendor is. Because many vendors can share one `Ecosystem`, they also share one adapter class, but each vendor still receives its own adapter instance scoped to that vendor's config and project root. This instance-per-vendor relationship is not guaranteed by filesystem layout alone: `HaskellAdapter`'s own monorepo resolution logic, `_resolve_package_dir`, shows that a single `project_root` can host source for multiple vendors at once -- e.g. `hledger-lib`, `hledger`, and `hledger-ui` all living inside one `hledger` checkout -- so an adapter instance is responsible for narrowing the shared `project_root` down to the subdirectory that matches its own vendor before any other method call is meaningful. If a `vendor.toml` entry names an ecosystem string outside the four-member enum, that entry is rejected at config-load time, before `get_adapter`'s dispatch table is ever reached.

Two implementation strategies for adapters coexist by design, and neither supersedes the other (`decisions/0002` governs the first strategy; `decisions/0057` adds the second, explicitly not superseding it). The in-process strategy, used for npm, Python, and Cargo, is an importable Python class inside `src/codecompass/` that shells out to native ecosystem tooling. The external-process strategy, used for Haskell as the reference implementation, keeps only a thin in-process dispatcher for simple manifest reads and delegates all ecosystem-specific logic to an independent OS process communicating over a small JSON-Lines protocol. This second strategy exists for ecosystems whose implementation cannot or should not live in-process as GPL-covered Python code, such as a hypothetical proprietary COBOL adapter. The in-process strategy remains the default, lower-overhead choice, and adopting the external-process strategy for Haskell did not replace or deprecate it.
<!-- /codecompass-grounded-by -->

<!-- codecompass-grounded-by: CL-ADPT-007 region:adapter-md-adapter-term-ambiguity -->
## Understanding "Adapter" in This Project

When you see the word "adapter" in this codebase, check the surrounding context, because it refers to two distinct things. The first is the ecosystem adapter, implemented as `EcosystemAdapter`, an abstract base class with real subclasses located in `src/codecompass/adapters/`. The second is the "host-output adapter," a label applied to `skill.py`, `commands.py`, and `index.py`; this is a purely expository classification with no corresponding class, interface, or shared base in the source. The bare word "adapter" alone does not tell you which sense is meant.
<!-- /codecompass-grounded-by -->

## A related, but non-existent, term: "connector"

"Connector" names nothing in CodeCompass's source, tests, or configuration. If you encounter it in a CodeCompass context, the most likely intended referent is either the broader Claude/MCP ecosystem's own "connector" concept (a hosted integration CodeCompass has not implemented — no MCP-related code exists anywhere in `src/codecompass/`), or CodeCompass's own "adapter" (the actual, evidenced mechanism nearest in meaning).
