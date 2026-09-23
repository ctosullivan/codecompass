# The `EcosystemAdapter` interface

See `docs/domain/concepts/adapter.md` for what "adapter" means and how it
relates to "vendor"/"ecosystem"/"protocol" — this page is the
implementation: the abstract contract, the four concrete classes, and how
the two coexisting strategies (in-process, external-process) actually
differ in code. For the external-process wire protocol's own
message-by-message shape, see `../protocol-adapter/wire-protocol.md`.

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
overridable method (`symbols()`, Phase 62) with a real default body — a
future adapter that doesn't implement structured extraction is not
forced to (no `TypeError` at construction). The default walks the
vendor's own source tree (`iter_source_files`) and dispatches each file
through `symbols.extract_symbols_for_file` by ecosystem — exactly the
walk+extract pairing `sync.py::rebuild_project_graph` used to perform
itself before Phase 62 relocated it here.

`repository_url()` is explicitly documented as **never a network
call** (`decisions/0021`) — resolved from locally-available package
metadata only. Returning `None` means this ecosystem's local metadata
carries no repository information at all; `source_resolution.py` treats
that as fail-loud, not a fallback trigger.

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

A closed, total dispatch table — every `Ecosystem` member maps to
exactly one class, never a naming convention or plugin discovery
mechanism. This is the single place `codecompass` decides which adapter
class to construct; every caller (`sync.py`, `staleness.py`) goes through
this function rather than importing a concrete adapter class directly.

## Strategy 1 — in-process (npm, Python, Cargo)

Three adapters, each an importable Python class inside
`src/codecompass/adapters/`, shelling out to each ecosystem's own native
tooling via the shared `_run_json` seam (`adapters/base.py:100-138`):

| Adapter | Native tool | Symbol extraction |
|---|---|---|
| `NpmAdapter` (`npm.py`) | `npm ls --json` | `.d.ts` regex scan (`symbols.extract_npm_symbols`) |
| `PythonAdapter` (`python.py`) | `pipdeptree --json` | `ast`-based top-level `def`/`class` scan (`symbols.extract_python_symbols`) |
| `CargoAdapter` (`cargo.py`) | `cargo tree` | Coarse line-based `pub fn`/`pub struct`/`pub enum`/`pub trait` scan (`symbols.extract_rust_symbols`) |

`_run_json` resolves `cmd[0]` via `shutil.which` before invoking it —
not just a nicer error message: several real tools this seam invokes
(notably `npm`) are `.cmd` shims on Windows, which `CreateProcess` can't
launch directly by bare name; resolving first gives the correctly-
extensioned path so plain `shell=False` works cross-platform. Tests
monkeypatch this function per-adapter-module to inject fixture JSON
instead of invoking a real toolchain (`decisions/0014`).

## Strategy 2 — external-process (Haskell, the reference implementation)

`HaskellAdapter` (`adapters/haskell.py`) is a **thin dispatcher**:

- `installed_version()`, `repository_url()` — read `package.yaml`
  directly via `yaml.safe_load()` (a simple manifest-key lookup, the
  same class of generic, ecosystem-adjacent code `discovery.py` already
  does for every other ecosystem's own manifest — not "Haskell-specific
  implementation code" any more than `tomllib.load()` on a TOML file is
  "Rust-specific," per `decisions/0057`).
- `dependency_tree()`, `readme_and_api_surface()`, `symbols()` — all
  three delegate to `_analyze()`, which spawns (or reuses a per-instance
  cache of) an `ExternalAdapterProcess`, sends one `analyze_project`
  request, and converts the JSON response into `DepNode`/`Symbol`
  objects.

**Per-instance caching** (`_cached_analysis`, `adapters/haskell.py:53`):
before Phase 62, each of the three delegating methods independently
called `_analyze()`, spawning a full external subprocess and re-running
the entire `analyze_project` request every time, even though each caller
only reads one field. The cache is deliberately **not cross-instance** —
`sync_vendor` and `rebuild_project_graph` each construct their own
separate `HaskellAdapter`, so the same project still pays for the
external process twice per `sync` run; this redundancy is an accepted,
disclosed inefficiency, not fixed by this cache.

**Monorepo package-root resolution** (`_resolve_package_dir`,
`adapters/haskell.py:154-179`): if `project_root` itself is the package
(its own `package.yaml` declares the matching name), use it directly.
Otherwise search immediate subdirectories for the one whose own
`package.yaml` declares `name: <config.name>` — the adapter is
**never** handed a monorepo root and asked to figure out which
subdirectory is the real package; that resolution happens on the
CodeCompass side, before the external process is ever invoked
(`decisions/0057` §"Monorepo package roots"). `repository_url()` sets
`RepositoryLocation.subdirectory` whenever this resolves to somewhere
other than `project_root` itself.

**Locating the built executable** (`_adapter_executable`,
`adapters/haskell.py:237-278`): finds `stack` on `PATH`, locates the
`adapters/haskell/` git submodule by searching upward from this module's
own file location, runs `stack path --local-install-root` inside it, and
expects `bin/codecompass-adaptor-haskell-exe` under that root. Every
failure mode (`stack` missing, submodule not checked out, `stack build`
never run) raises `AdapterError` with a message pointing at
`docs/external-adapters.md`.

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
versioning) is documented in `../protocol-adapter/wire-protocol.md`, not
here — this page stops at "the Python-side adapter delegates to
`ExternalAdapterProcess`," which is the architectural boundary; the
protocol itself is a separate, independently-versioned contract
(`decisions/0058`).
