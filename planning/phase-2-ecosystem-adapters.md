# Phase 2: Ecosystem Adapters

## Scope

**Covered:**
- `src/depcompass/adapters/base.py` — `EcosystemAdapter` ABC (four
  abstract methods), `AdapterError`, and a shared `_run_json` subprocess
  seam that tests monkeypatch to inject fixture JSON.
- `src/depcompass/adapters/npm.py`, `python.py`, `cargo.py` — one adapter
  class per ecosystem, each implementing `installed_version`,
  `source_location`, `readme_and_api_surface`, `dependency_tree`.
- `pyproject.toml` — add `pipdeptree` to `dependencies` (bundled, not an
  external prerequisite like npm/cargo).
- Tests: one file per adapter plus `tests/test_adapters_base.py`, using
  hand-written fixture JSON so no adapter's core tests require a real
  npm/cargo toolchain. npm and Python additionally get a live smoke test
  (skipped automatically if the tool isn't present); Cargo's live smoke
  test is written but inert in this environment today.
- New ADR: `decisions/0013` recording the fixture-mocking testing
  strategy and its explicit tradeoff (doesn't catch real-world tool
  output drift). (Renumbered from 0012 — that number was claimed by
  `decisions/0012-conversational-first-repl-design.md`, recorded before
  Phase 2 implementation began.)
- Same-commit doc updates: `architecture/overview.md` (Adapter interface
  section gets real signatures; Known footguns gains Phase 2-specific
  entries), `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md`.

**Explicitly deferred:**
- Diamond-dependency deduplication / "see X above" back-references —
  Phase 3's tree-*rendering* concern. Adapters return the raw,
  fully-expanded tree exactly as the underlying tool reports it.
- Rendering `FILETREE.md`/`DEPTREE.md` from `DepNode` — Phase 3.
- Wiring adapters into `sync`/`init`/`check` CLI commands — Phase 4.
- Copying `vendor/<name>/src/` snapshots (uses `source_location()` as its
  source, but the copy mechanism is Phase 4).
- `rustdoc --output-format json` investigation for Cargo API-surface
  extraction (decisions/0002 flagged this as a future refinement) — not
  attempted now; no toolchain available locally to validate its shape
  against. Phase 2 uses regex-based `pub` signature scanning instead.
- Transitive `dev_only` propagation for npm (a transitive dependency of a
  dev-only direct dependency isn't marked `dev_only` in Phase 2) —
  documented limitation, not solved now.
- `docs/config-schema.md` / `docs/cli-reference.md` changes — expected
  none, since adapters are a library layer with no CLI or config-schema
  surface yet; confirm this holds during implementation rather than
  assuming it silently.

## Design decisions

- **Cargo toolchain unavailable locally** (flagged in `planning/CONTEXT.md`
  going into this phase): resolved by testing all three adapters'
  core parsing logic against hand-written fixture JSON via the `_run_json`
  monkeypatch seam, rather than requiring real subprocess output. Recorded
  as `decisions/0013` since this is an explicit, real gap — fixtures can
  drift from real tool output undetected until a live test (or a human)
  catches it.
- **`pipdeptree`** added as a real dependency (pip-installable, unlike the
  npm/cargo system toolchains depcompass can't bundle).
- **Python API-surface fallback** uses static `ast` parsing of source for
  `__all__`/docstring extraction, not `importlib.import_module` +
  `inspect` — importing arbitrary installed code purely to generate docs
  would execute unrelated module-level side effects for a read-only `sync`
  step. More code, strictly safer.
- **Python version/location** via `importlib.metadata` /
  `importlib.util.find_spec` — no subprocess needed, still satisfies
  decisions/0002's "installed package metadata" framing.
- **Cargo API-surface** via regex scan for `pub fn`/`pub struct`/
  `pub enum`/`pub trait` (+ preceding `///` doc comment) — explicitly
  coarse, will misparse multi-line signatures. Confirmed working, correct
  tool invocations for npm/Python by actually running them live in this
  dev environment before finalizing this plan:
  - `npm ls <name> --json --all` is required — bare `npm ls --json`
    truncates to top-level only on npm 10.8.2.
  - `pipdeptree --output json-tree --packages <name>` is required — flat
    `--json`/`-o json` (deprecated) lists every installed package with
    only direct deps each, the wrong shape for a single-rooted tree.
  - Confirmed a real npm package (`turndown`) ships no `.d.ts` at all —
    handling a missing `.d.ts` gracefully is a common case, not a
    hypothetical edge case.
- **`dev_only` differs meaningfully per ecosystem** — npm: direct
  `devDependencies` only. Python: always `False` (pipdeptree output
  carries no such field — a real structural difference from npm, not an
  oversight). Cargo: derived from the resolve graph's per-edge `"kind"`
  field (`"dev"` vs `null`) — a cleaner per-edge signal than npm has.

## Files

- `src/depcompass/adapters/__init__.py` — package init.
- `src/depcompass/adapters/base.py` — `EcosystemAdapter(ABC)` constructed
  with `(config: VendorConfig, project_root: Path)`; abstract methods
  `installed_version() -> str`, `source_location() -> Path`,
  `readme_and_api_surface() -> str`, `dependency_tree() -> DepNode`.
  `AdapterError(Exception)`. `_run_json(cmd: list[str], cwd: Path) -> dict
  | list` — wraps `FileNotFoundError`, non-zero exit, and
  `json.JSONDecodeError` into `AdapterError` with a clear message.
- `src/depcompass/adapters/npm.py` — `NpmAdapter`. Version/location from
  `node_modules/<name>/package.json` directly (no subprocess). Tree from
  `npm ls <name> --json --all`, recursively walked, no dedup. `dev_only`
  from the root `package.json`'s `devDependencies`. API surface from
  README + up to 5 `.d.ts` files (sorted for determinism). `side_effects`
  from `package.json`'s `scripts.postinstall`, if present.
- `src/depcompass/adapters/python.py` — `PythonAdapter`. Version/location
  via `importlib.metadata`/`importlib.util.find_spec`. Tree from
  `pipdeptree --output json-tree --packages <name>`, recursively walked,
  no dedup. `dev_only` always `False`. API surface prefers `.pyi` stubs
  (same 5-file cap as npm), else falls back to `ast`-based
  `__all__`/docstring extraction from module source.
- `src/depcompass/adapters/cargo.py` — `CargoAdapter`. Version/location
  via `cargo metadata --format-version 1 --no-deps`. Tree via full
  `cargo metadata --format-version 1`, walking `resolve.nodes` cross-
  referenced against `packages` (cycle-guarded with a `visited` set — a
  defensive detail, not the Phase 3 semantic dedup). `dev_only` from each
  edge's `"kind"` field. API surface via regex `pub` scan over `.rs`
  files under `src/`. **Explicitly unverified against real cargo output**
  — see Verification.
- `tests/fixtures/` — new: `npm_ls.json`, `npm_package_root.json`,
  `npm_package_with_postinstall.json`, `sample.d.ts`, `sample_readme.md`,
  `pipdeptree_json_tree.json`, `sample.pyi`, `sample_module_with_all.py`,
  `cargo_metadata.json` (hand-written against cargo's public schema docs,
  not verified against real output), `sample_lib.rs`.
- `tests/test_adapters_base.py` — `_run_json` success/missing-tool/
  non-zero-exit/invalid-JSON paths; confirms the ABC rejects an
  incomplete subclass.
- `tests/test_adapter_npm.py` — fixture-driven tree/dev_only/API-surface/
  side_effects tests; `.d.ts` 5-file-cap test; missing-package
  `AdapterError` test; a live smoke test guarded by
  `@pytest.mark.skipif(shutil.which("npm") is None, ...)`.
- `tests/test_adapter_python.py` — mirrors npm's structure: fixture-driven
  tree test; `.pyi`-present and `.pyi`-absent-falls-back-to-`ast` tests;
  `dev_only`-always-`False` assertion; missing-package `AdapterError`
  test; a live smoke test against an already-installed dependency
  (`pytest`) — always runnable, no `skipif` needed.
- `tests/test_adapter_cargo.py` — fixture-driven tree/dev_only/pub-
  extraction tests only (no live smoke test will actually run in this
  environment); regex-extraction test against `sample_lib.rs` asserting
  current behavior including the documented multi-line-signature miss.
- `pyproject.toml` — add `"pipdeptree"` to `dependencies`.
- `decisions/0013-adapter-tests-use-fixture-mocking-not-live-subprocesses.md`.
- `architecture/overview.md`, `planning/ROADMAP.md`,
  `planning/CONTEXT.md`, `CHANGELOG.md` — updated in place.

## Verification

- `pip install -e ".[dev]"` succeeds with `pipdeptree` installing.
- `pytest` — full suite passes, count increases from the current 16.
- `ruff check .` — clean, including the new `adapters/` package.
- **Real npm smoke test**: `npm install` a small real package (e.g.
  `lodash`) into a scratch dir, construct `NpmAdapter` against it, call
  all four methods — confirm non-trivial, correct output.
- **Real Python smoke test**: construct `PythonAdapter` for `pytest`
  (already installed in this repo's `.venv`) against `Path.cwd()` —
  confirm `installed_version()` matches `importlib.metadata.version()`
  directly and `dependency_tree()`'s root has real children (`pluggy`,
  `iniconfig`, etc.).
- Trigger `AdapterError` once per adapter (nonexistent package name) and
  confirm the message is clear.
- `decisions/0013` has Status/Context/Decision/Alternatives
  considered/Consequences sections matching the existing ADR template.
- `architecture/overview.md`'s Known footguns section lists every new
  Phase 2 limitation (npm `dev_only` not transitive, Python `dev_only`
  always `False`, Cargo regex extraction misses multi-line signatures,
  Cargo adapter unverified against real cargo output).
- **Follow-up once a Rust toolchain is available anywhere in the
  pipeline** (not blocking this phase, but must happen before the Cargo
  adapter is trusted): confirm real `cargo metadata --format-version 1`
  output actually matches `cargo_metadata.json`'s assumed field names/
  nesting; run the Cargo live smoke test for the first time; validate
  regex-based `pub` extraction against a real crate with nontrivial
  generics.

## Status

not started
