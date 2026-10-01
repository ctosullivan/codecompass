# Configuration: `vendor.toml`

**Provenance tier: CONFIRMED-LIVE.** Source:
`phase80-implementation-reconstruction.md` §5, §1 (`config.py` entry).
`config.py` was one of the five modules whose real test file actually
collected and ran in the Stage 2 sandbox (`test_config.py`, part of the
116-passed set). The one test failure in that run
(`test_load_valid_vendor_config`, `FileNotFoundError`) was traced to a
missing fixture file in the bounded export, not a defect in `config.py`
itself — see `08-limitations-and-provenance.md`.

## Entry point

`config.py::load_vendor_config(path)` is the only configuration entry
point. There is no environment-variable or CLI-flag-driven configuration
beyond the path to `vendor.toml` itself, which defaults to
`Path("vendor.toml")` relative to the current working directory.

## File format

`vendor.toml` is parsed via Python's standard-library `tomllib` — no
third-party TOML dependency is involved (the project's own `pyproject.toml`
comment states this directly: `tomllib` is available because the project
requires Python ≥3.11). The schema is a `[[vendor]]` array-of-tables.

Each `[[vendor]]` entry requires:

- `name` (string)
- `ecosystem` (string, must be one of the closed `Ecosystem` enum
  values: `npm`, `python`, `cargo`, `haskell`)

Any other key is ignored.

```toml
[[vendor]]
name = "typer"
ecosystem = "python"

[[vendor]]
name = "some-npm-package"
ecosystem = "npm"
```

## Failure behavior

Parsing is fail-fast: the first invalid entry (missing `name`, or an
`ecosystem` value outside the closed enum) raises `ConfigError` and
parsing stops there — it does not collect and report every error in the
file at once.

## A known quirk: the legacy `depth` key

`config.py` silently tolerates and discards a legacy `depth` key if
present on a `[[vendor]]` entry. This is not a bug in the sense of
broken behavior — the parser simply never reads that key — but it is a
real silent-acceptance behavior worth knowing: if your `vendor.toml` still
has a `depth = ...` line from an older version of this project, it will
be parsed successfully and then quietly ignored, with no warning that it
had no effect.

## What this file does not cover

Vendor *discovery* (how `vendor.toml` gets generated or appended to in
the first place, from `package.json`/`pyproject.toml`/`requirements.txt`/
`Cargo.toml`/`package.yaml` manifests) is a separate, also
CONFIRMED-LIVE-tested concern (`discovery.py`) not detailed in this file;
see the reconstruction's own §1 for `discovery.py`'s five manifest
discoverers and their known gaps, and
`08-limitations-and-provenance.md` for the two documented discovery
limitations (optional Python dependencies are not scanned; hpack's
conditional Haskell dependencies are not expanded).
