# The `EcosystemAdapter` interface

Part of the `architecture/` reference set. See [`overview.md`](overview.md)
for the system-at-a-glance entry point; the rest of this set:
[`module-map.md`](module-map.md), [`core-data-model.md`](core-data-model.md),
[`context-graph-schema.md`](context-graph-schema.md),
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md).

See [`docs/domain/concepts/adapter.md`](../docs/domain/concepts/adapter.md)
for what "adapter" means and how it relates to "vendor"/"ecosystem" — this
page is the implementation: the abstract contract, the four concrete
classes, and how the two coexisting strategies (in-process,
external-process) actually differ in code. This is a different sense of
"adapter" from the **host-output adapters** described in `overview.md`'s
"Module tiers" section (Claude Skills, `/discovery`, the root `CLAUDE.md`
routing table), which render already-computed content into tool-specific
formats rather than abstracting a package manager — see
[`module-map.md`](module-map.md#two-informal-senses-of-adapter-in-this-codebase).

## The contract (`adapters/base.py:25-97`)

```python
class EcosystemAdapter(ABC):
    def __init__(self, config: VendorConfig, project_root: Path) -> None: ...

    @abstractmethod
    def installed_version(self) -> str: ...
    @abstractmethod
    def source_location(self) -> Path: ...
    @abstractmethod
    def readme_and_api_surface(self) -> str: ...
    @abstractmethod
    def repository_url(self) -> RepositoryLocation | None: ...
    @abstractmethod
    def dependency_tree(self) -> DepNode: ...

    def symbols(self) -> list[Symbol]:  # concrete, overridable
        ...
```

Five abstract methods every adapter must implement; one concrete,
overridable method (`symbols()`) with a real default body — a future
adapter that doesn't implement structured extraction is not forced to (no
`TypeError` at construction). The default walks the vendor's own source
tree (`iter_source_files`) and dispatches each file through
`symbols.extract_symbols_for_file` by ecosystem — exactly the
walk+extract pairing `sync.py::rebuild_project_graph` used to perform
itself before this method was added here.

`repository_url()` is explicitly documented as **never a network call**
(`decisions/0021`) — resolved from locally-available package metadata
only. Returning `None` means this ecosystem's local metadata carries no
repository information at all; `source_resolution.py` treats that as
fail-loud, not a fallback trigger.

`dependency_tree()` returns the raw, fully-expanded tree — **not
deduplicated**; diamond dependencies repeat in full exactly as the
underlying tool reports them. Dedup into "see X above" back-references is
`deptree.py`'s rendering concern, not the adapter's tree-construction
concern.

## Dispatch (`adapters/__init__.py:18-31`)

```python
_ADAPTER_BY_ECOSYSTEM: dict[Ecosystem, type[EcosystemAdapter]] = {
    Ecosystem.NPM: NpmAdapter,
    Ecosystem.PYTHON: PythonAdapter,
    Ecosystem.CARGO: CargoAdapter,
    Ecosystem.HASKELL: HaskellAdapter,
}

def get_adapter(config: VendorConfig, project_root: Path) -> EcosystemAdapter:
    return _ADAPTER_BY_ECOSYSTEM[config.ecosystem](config, project_root)
```

A closed, total dispatch table — every `Ecosystem` member maps to exactly
one class, never a naming convention or plugin discovery mechanism. This
is the single place `codecompass` decides which adapter class to
construct; every caller (`sync.py`, `staleness.py`) goes through this
function rather than importing a concrete adapter class directly.

## Strategy 1 — in-process (npm, Python, Cargo)

Three adapters, each an importable Python class inside
`src/codecompass/adapters/`, shelling out to each ecosystem's own native
tooling via the shared `_run_json` seam (`adapters/base.py:100-138`):

| Adapter | Native tool | Symbol extraction | Real per-ecosystem quirk |
|---|---|---|---|
| `NpmAdapter` (`npm.py`) | `npm ls --json --all` | `.d.ts` regex scan (`symbols.extract_npm_symbols`), capped at 5 files | `dev_only` cross-references the root project's `devDependencies` by name at *every* depth, not propagated to a marked node's own children |
| `PythonAdapter` (`python.py`) | `sys.executable -m pipdeptree --output json-tree` | `.pyi` stubs where present, else static `ast` parsing of `__all__`/docstrings | `dev_only` is always `False` — `pipdeptree` output carries no dev/runtime distinction, a structural difference from npm, not an oversight |
| `CargoAdapter` (`cargo.py`) | `cargo metadata --format-version 1` | Coarse line-based `pub fn`/`pub struct`/`pub enum`/`pub trait` scan (`symbols.extract_rust_symbols`) | No standardized doc-comment extraction assumed; misses multi-line signatures; unverified against real `cargo` output (fixture-only tests) |

`_run_json` resolves `cmd[0]` via `shutil.which` before invoking it — not
just a nicer error message: several real tools this seam invokes
(notably `npm`) are `.cmd` shims on Windows, which `CreateProcess` can't
launch directly by bare name; resolving first gives the correctly-
extensioned path so plain `shell=False` works cross-platform. Tests
monkeypatch this function per-adapter-module to inject fixture JSON
instead of invoking a real toolchain
([`decisions/0014`](../decisions/0014-adapter-tests-use-fixture-mocking-not-live-subprocesses.md)).
See each adapter module's own docstring for the full per-ecosystem detail
this table intentionally doesn't restate (a docstring can't drift
silently from its own code the way separate prose could).

MVP ships all three adapters on day one rather than starting npm-only —
see
[`decisions/0008`](../decisions/0008-mvp-ships-three-adapters-day-one.md)
and
[`decisions/0002`](../decisions/0002-adapter-approach-differs-per-ecosystem.md).

## Strategy 2 — external-process (Haskell, the reference implementation)

`HaskellAdapter` (`adapters/haskell.py`) is a **thin dispatcher**, the
first adapter that is **not** an in-process Python class implementing
ecosystem-specific logic directly:

- `installed_version()`, `repository_url()` — read `package.yaml`
  directly via `yaml.safe_load()` (a simple manifest-key lookup, the same
  class of generic, ecosystem-adjacent code `discovery.py` already does
  for every other ecosystem's own manifest — not "Haskell-specific
  implementation code" any more than `tomllib.load()` on a TOML file is
  "Rust-specific," per `decisions/0057`).
- `dependency_tree()`, `readme_and_api_surface()`, `symbols()` — all
  three delegate to `_analyze()`, which spawns (or reuses a per-instance
  cache of) an `ExternalAdapterProcess`, sends one `analyze_project`
  request, and converts the JSON response into `DepNode`/`Symbol`
  objects.

**Per-instance caching** (`_cached_analysis`, `adapters/haskell.py:53`):
each of the three delegating methods independently calls `_analyze()`;
the cache means at most one real external-process round trip per
`HaskellAdapter` instance, populated once and reused by whichever method
a caller invokes. The cache is deliberately **not cross-instance** —
`sync_vendor` and `rebuild_project_graph` each construct their own
separate `HaskellAdapter`, so the same project still pays for the
external process twice per `sync` run; this redundancy is an accepted,
disclosed inefficiency, not fixed by this cache.

**Monorepo package-root resolution** (`_resolve_package_dir`,
`adapters/haskell.py:154-179`): if `project_root` itself is the package
(its own `package.yaml` declares the matching name), use it directly.
Otherwise search immediate subdirectories for the one whose own
`package.yaml` declares `name: <config.name>` — the adapter is **never**
handed a monorepo root and asked to figure out which subdirectory is the
real package; that resolution happens on the CodeCompass side, before
the external process is ever invoked (`decisions/0057` §"Monorepo
package roots"). `repository_url()` sets
`RepositoryLocation.subdirectory` whenever this resolves to somewhere
other than `project_root` itself. `resolve_and_clone`'s own
`subdirectory` handling only scopes the *rendered* view, never the raw
on-disk clone — see `overview.md`'s "Known footguns".

**Locating the built executable** (`_adapter_executable`,
`adapters/haskell.py:237-278`): finds `stack` on `PATH`, locates the
`adapters/haskell/` git submodule by searching upward from this module's
own file location, runs `stack path --local-install-root` inside it, and
expects `bin/codecompass-adaptor-haskell-exe` under that root. Every
failure mode (`stack` missing, submodule not checked out, `stack build`
never run) raises `AdapterError` with a message pointing at
[`docs/external-adapters.md`](../docs/external-adapters.md).

## What genuinely needs isolation, and what doesn't

`decisions/0057`'s own stated boundary, confirmed by reading
`adapters/haskell.py` directly: manifest-key lookups
(`installed_version`, `repository_url`) stay in-process because they are
generic, low-risk metadata reads. What actually requires the external
process is real ecosystem-specific *logic* — resolving `stack`'s own
build-plan/dependency-tree semantics, and parsing real `.hs` source to
determine a module's exported API surface. `HaskellAdapter` itself never
reimplements either; both live only in the external process
(`adapters/haskell/src/Adapter/Deps.hs`, `Adapter/Scanner.hs`).

## Cross-reference

The external process's own wire shape (`initialize`/`analyze_project`/
`shutdown`, the four capability-gated result sections, error codes,
versioning), the three-repository submodule layout, and the local
build/version-compatibility setup are documented in
[`docs/external-adapters.md`](../docs/external-adapters.md) and
[`decisions/0057`](../decisions/0057-external-process-adapter-protocol.md)/[`decisions/0058`](../decisions/0058-adapter-protocol-and-haskell-adapter-as-separate-repositories.md),
not here — this page stops at "the Python-side adapter delegates to
`ExternalAdapterProcess`," which is the architectural boundary; the
protocol itself is a separate, independently-versioned contract.
