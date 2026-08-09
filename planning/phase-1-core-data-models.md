# Phase 1: Core Data Models & Config Parsing

## Scope

**Covered:**
- `src/depcompass/core.py` — `VendorConfig`, `Depth`, `Ecosystem`, `DepNode`,
  `VendorDigest` as stdlib dataclasses. `VendorDigest.is_stale` stays a
  documented stub (raises `NotImplementedError` until `staleness.check()`,
  Phase 6, populates it — not "fixed" with a default).
- `src/depcompass/config.py` — `load_vendor_config(path) -> list[VendorConfig]`,
  parsing `vendor.toml` via stdlib `tomllib`. Fail-fast validation: the
  first invalid vendor entry raises `ConfigError` naming the vendor and the
  problem, rather than collecting every error in the file.
- `src/depcompass/cli.py` — minimal Typer app satisfying the
  `depcompass.cli:app` entry point already declared in `pyproject.toml`.
  All 5 commands (`init`, `sync`, `index`, `check`, `chat`) are registered
  and visible in `depcompass --help`, each a stub that prints "not yet
  implemented, planned for Phase N" (matching the phase tags already in
  `docs/cli-reference.md`) and exits with a non-zero status. `_load_config`
  is implemented for real (calls `config.py`); `_write_claude_md` stays a
  `NotImplementedError` stub pending Phase 4.
- Resolve the open question from `decisions/0004`: `vendor/<name>/src/`
  pinned source snapshots are **gitignored and regenerated on `sync`**,
  not committed — recorded as `decisions/0010`.
- Record the dataclasses-over-pydantic choice as `decisions/0011`.
- Tests: `tests/test_core.py` (dataclass construction/validation, incl.
  `full` depth requiring `context_path`), `tests/test_config.py` (valid
  parse, missing required field, invalid `ecosystem`/`depth` values,
  malformed TOML syntax), using a `tests/fixtures/vendor.toml` sample.
- Same-commit doc updates per `CLAUDE.md` §2: `architecture/overview.md`'s
  Known footguns section (remove the now-resolved snapshot question),
  `docs/config-schema.md` (note fail-fast validation behavior),
  `docs/cli-reference.md` (commands now exist as stubs, not fully
  unimplemented), `CHANGELOG.md`, `planning/CONTEXT.md`.

**Explicitly deferred:**
- Ecosystem adapters (`EcosystemAdapter` ABC, npm/Python/Cargo
  implementations) — Phase 2.
- Actually generating `FILETREE.md`/`DEPTREE.md` — Phase 3.
- Real `sync`/`index` command logic — Phase 4.
- Gap analysis / Anthropic API calls — Phase 5.
- Staleness checking (`VendorDigest.is_stale` stays unpopulated) — Phase 6.
- Chat REPL logic — Phase 7/8.
- Actually writing `vendor/<name>/src/` snapshots to disk (the *mechanism*
  is decided this phase; the code that populates the directory doesn't
  exist until adapters + `sync` exist in Phase 2/4).

## Files

- `src/depcompass/core.py` — `Ecosystem` and `Depth` as `enum.StrEnum`
  (clean fit with `str`-valued TOML fields); `VendorConfig` (validates
  `full` depth requires `context_path` in `__post_init__`); `DepNode`
  (recursive, `children: list[DepNode]`, `side_effects: list[str]`);
  `VendorDigest` (aggregate + stubbed `is_stale` property).
- `src/depcompass/config.py` — `ConfigError(Exception)`;
  `load_vendor_config(path: Path) -> list[VendorConfig]` using `tomllib`.
- `src/depcompass/cli.py` — `app = typer.Typer()`; `init`/`sync`/`index`/
  `check`/`chat` stub commands; `_load_config`; `_write_claude_md` stub.
- `tests/fixtures/vendor.toml` — sample config (mirrors
  `docs/config-schema.md`'s example: one `full` npm vendor with
  `context_path`, one `surface` npm vendor, one `surface` python vendor,
  one `surface` cargo vendor).
- `tests/test_core.py`, `tests/test_config.py` — see Scope above.
- `decisions/0010-vendor-src-gitignored-and-regenerated.md` — resolves
  `decisions/0004`'s open question.
- `decisions/0011-dataclasses-over-pydantic-for-core-models.md`.
- `architecture/overview.md`, `docs/config-schema.md`,
  `docs/cli-reference.md` — updated in place (see Scope).
- `CHANGELOG.md`, `planning/CONTEXT.md` — updated at phase close.

## Verification

- `pip install -e ".[dev]"` succeeds; `depcompass --help` lists all 5
  commands.
- `pytest` — all `tests/test_core.py` and `tests/test_config.py` cases
  pass, including the negative cases (missing field, bad enum value,
  malformed TOML, `full` depth without `context_path` all raise with a
  clear message).
- `ruff check .` passes with no errors.
- Running any stub command (e.g. `depcompass sync`) prints a "not yet
  implemented, planned for Phase N" message and exits non-zero.
- `load_vendor_config(Path("tests/fixtures/vendor.toml"))` returns 4
  `VendorConfig` entries with the expected field values (manual or
  test-asserted).
- `decisions/0010` and `decisions/0011` each have Status/Context/Decision/
  Alternatives considered/Consequences sections.
- `architecture/overview.md`'s Known footguns section no longer lists the
  `vendor/<name>/src/` commit-vs-gitignore question as open.

## Status

done — all verification steps passed: 16/16 tests pass (`pytest`), `ruff
check .` is clean, `pip install -e ".[dev]"` + `depcompass --help` list
all 5 commands, `depcompass sync` (and the other 4) print a "not yet
implemented" message naming their phase and exit 1, and
`load_vendor_config` correctly parses the 4-entry fixture and rejects each
of the negative cases (missing field, bad enum value, malformed TOML,
`full` without `context_path`).
