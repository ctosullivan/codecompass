# Writing a new ecosystem adapter

Grounded in `src/codecompass/adapters/base.py` (the interface itself),
`src/codecompass/adapters/npm.py` (a real in-process implementation),
and `src/codecompass/adapters/haskell.py` (the real external-process
implementation, plus `src/codecompass/adapters/external_process.py`).
See [`docs/domain/concepts/adapter.md`](../domain/concepts/adapter.md)
for what "adapter" means as a domain concept before reading this — this
page is about *implementing* one, not defining the term.

## The interface: `EcosystemAdapter`

`src/codecompass/adapters/base.py` defines the abstract base class every
ecosystem implements. Constructed as `Adapter(config: VendorConfig,
project_root: Path)`. Five abstract methods, one concrete/overridable:

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

    def symbols(self) -> list[Symbol]:
        # concrete default: walks source_location() via
        # extract_symbols_for_file per-ecosystem; override if your
        # ecosystem needs a different extraction path (see "Two
        # implementation strategies" below).
        ...
```

(exact signatures, `base.py`'s `EcosystemAdapter` class).

What each abstract method is really responsible for, per the real
implementations:

- **`installed_version()`** — the version string actually installed
  *in this project*, never a network lookup. `NpmAdapter` reads
  `node_modules/<name>/package.json`; `HaskellAdapter` reads a resolved
  `package.yaml`'s `version` key directly.
- **`source_location()`** — filesystem path to the installed package's
  own source, used later to build `vendor/<name>/src/` snapshots.
- **`readme_and_api_surface()`** — one rendered string combining a
  README (if found) and whatever API-surface signal your ecosystem can
  extract cheaply (`.d.ts` files for npm, `.pyi`/AST fallback for
  Python, the external process's own `symbols` response for Haskell).
- **`repository_url() -> RepositoryLocation | None`** — resolved
  **only from locally-available package metadata**, never a network
  call (`decisions/0021`) — `None` if the ecosystem's local metadata
  carries nothing usable; callers treat that as fail-loud, not a
  fallback trigger. Set `RepositoryLocation.subdirectory` if your
  ecosystem can express "this package lives in a subdirectory of a
  larger repo" (npm's `repository.directory`; Haskell's own monorepo
  case — see `HaskellAdapter.repository_url`'s docstring for the real
  worked example, a `hledger` monorepo containing `hledger-lib`).
- **`dependency_tree() -> DepNode`** — the **raw, fully-expanded** tree
  rooted at this vendor. Deliberately **not deduplicated** — diamond
  dependencies appear repeated, exactly as the underlying tool reports
  them (`base.py`'s own docstring). Rendering that into "see X above"
  back-references is a separate, later concern (tree rendering), not
  this method's job.
- **`symbols()`** — deliberately **concrete, not abstract**, so a new
  adapter that doesn't implement structured extraction isn't forced to
  (no `TypeError` at construction). The default walks `source_location()`
  and dispatches each file through `codecompass.symbols
  .extract_symbols_for_file(path, self.config.ecosystem)` — which means
  adding structured symbol extraction for an **in-process** ecosystem
  means adding a branch there, in `src/codecompass/symbols.py`, not
  overriding `symbols()` itself.

## Register it

One line in `src/codecompass/adapters/__init__.py`'s closed dispatch
table:

```python
_ADAPTER_BY_ECOSYSTEM: dict[Ecosystem, type[EcosystemAdapter]] = {
    Ecosystem.NPM: NpmAdapter,
    Ecosystem.PYTHON: PythonAdapter,
    Ecosystem.CARGO: CargoAdapter,
    Ecosystem.HASKELL: HaskellAdapter,
}
```

plus a new `Ecosystem` enum member in `src/codecompass/core.py` and a
new manifest-discovery entry in `src/codecompass/discovery.py`'s
`_MANIFEST_HANDLERS` (so bare `codecompass`/`init --scan` can
auto-discover the new ecosystem's dependencies at all). `get_adapter` is
the single dispatch point every call site uses — it's total over every
`Ecosystem` member by construction, never a fallback/"no adapter found"
branch.

## Two implementation strategies — pick one

Real, currently coexisting, and neither supersedes the other
(`decisions/0002`, `decisions/0057`):

### 1. In-process (npm, Python, Cargo)

A plain Python class inside `src/codecompass/adapters/`, shelling out to
the ecosystem's own native tooling via the shared `_run_json(cmd, cwd)`
seam — resolves `cmd[0]` via `shutil.which` first (so it works
cross-platform without a shell, and gives a clear "tool not found"
`AdapterError` rather than an OS-level failure), then parses stdout as
JSON, raising `AdapterError` on a non-zero exit or invalid JSON.
`NpmAdapter.dependency_tree` is the clearest real example:

```python
def dependency_tree(self) -> DepNode:
    data = _run_json(
        ["npm", "ls", self.config.name, "--json", "--all"],
        cwd=self.project_root,
    )
    ...
```

**Testing an in-process adapter**: tests monkeypatch the adapter
module's own `_run_json` (e.g. `codecompass.adapters.npm._run_json`)
to inject fixture JSON instead of invoking a real toolchain
(`decisions/0014`) — see `tests/test_adapters_base.py` for the pattern
used to test `_run_json` itself (fake `subprocess.run` + fake
`shutil.which`), and `tests/test_adapter_npm.py`/`test_adapter_python.py`/
`test_adapter_cargo.py` for per-ecosystem fixture tests built on top of
it.

### 2. External-process (Haskell — the reference implementation)

A **thin Python-side dispatcher** handling only simple, generic manifest
reads directly (`HaskellAdapter` reads `package.yaml` with plain
`yaml.safe_load` — a real ecosystem-adjacent manifest lookup, not
ecosystem-specific *logic* in the sense that matters), and delegates
everything that embodies real ecosystem-specific logic (dependency-tree
resolution, `.hs` API-surface/symbol extraction) to an independent OS
process spoken to only through
`src/codecompass/adapters/external_process.py`'s `ExternalAdapterProcess`
— a fully generic JSON-Lines client that carries **zero**
ecosystem-specific knowledge (confirmed: grepping that file for any
ecosystem name returns nothing) and is reusable, unmodified, by any
future external adapter.

```python
def _analyze(self) -> dict:
    if self._cached_analysis is None:
        executable = _adapter_executable(self.project_root)
        process = ExternalAdapterProcess([str(executable)])
        process.initialize()
        try:
            self._cached_analysis = process.analyze_project(
                self._resolve_package_dir(), self.config.name
            )
        finally:
            process.shutdown()
    return self._cached_analysis
```

(`haskell.py`'s `_analyze`, real code, per-instance-cached so
`dependency_tree()`/`readme_and_api_surface()`/`symbols()` don't each
independently re-run the whole external analysis).

**Choose this strategy when** the ecosystem's own real tooling doesn't
exist as a friendly CLI you can shell out to and parse JSON from
directly (Haskell has no single canonical `--json` dependency-tree
command the way `npm ls --json` or `pipdeptree --output json-tree` do),
or when the extraction logic is substantial enough that it deserves its
own independently-versioned, independently-tested project rather than
living inside `src/codecompass/`.

**The wire protocol itself** (the JSON-Lines request/response shapes,
`initialize`/`analyze_project`, `protocol_version` negotiation, the
`kind`/`note` symbol fields) is out of this page's scope — see
[`../protocol-adapter/wire-protocol.md`](../protocol-adapter/wire-protocol.md)
and `decisions/0057`–`0059` for the full contract. What this page covers
is only the Python-side dispatcher half: reading a manifest, resolving
the package's real on-disk root (including the monorepo case — see
`HaskellAdapter._resolve_package_dir` for the real algorithm), and
delegating to `ExternalAdapterProcess`. For building a **second**
external-process adapter (not just consuming this pattern), see
[`../protocol-adapter/integrating-a-new-external-adapter.md`](../protocol-adapter/integrating-a-new-external-adapter.md).

**Testing an external-process adapter**: `tests/test_adapter_haskell.py`
covers the thin dispatcher's own real logic (`package.yaml` reads via
real `yaml.safe_load()`, not mocked; monorepo package-root resolution)
directly; the delegated half is covered separately by
`tests/test_adapters_external_process.py`'s own fixture tests plus a
`stack`/submodule-gated live smoke test that only runs when the real
toolchain and submodule checkout are present (see that test file's own
skip conditions).

## Checklist for a new adapter

1. Add the new `Ecosystem` enum member (`src/codecompass/core.py`).
2. Add a manifest-discovery entry (`src/codecompass/discovery.py`'s
   `_MANIFEST_HANDLERS` + a `discover_<ecosystem>` function).
3. Implement `EcosystemAdapter`'s five abstract methods — pick the
   in-process or external-process strategy above.
4. Register the class in `src/codecompass/adapters/__init__.py`'s
   `_ADAPTER_BY_ECOSYSTEM`.
5. If in-process and you want structured symbols: add a branch to
   `codecompass.symbols.extract_symbols_for_file`. If external-process,
   override `symbols()` to convert the wire response the way
   `HaskellAdapter.symbols()` does.
6. Write fixture tests mirroring the existing per-ecosystem test module
   (`tests/test_adapter_<ecosystem>.py`) — per `CLAUDE.md`'s own rule
   (§1), if you're wiring new behaviour into an existing call site
   (`get_adapter`, `sync_vendor`), your plan/tests must exercise that
   real call site directly, not just the new class in isolation.
7. Update `docs/config-schema.md`'s ecosystem list and
   `docs/cli-reference.md` if the CLI surface changes at all (it
   shouldn't, for a pure new-ecosystem addition — `ecosystem` is
   already a free-standing enum value in the schema).
