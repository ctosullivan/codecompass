# `vendor.toml` config schema

Derived directly from `src/codecompass/core.py`'s `VendorConfig`
dataclass and `src/codecompass/config.py`'s `load_vendor_config`/
`_parse_entry` parsing logic — not from any existing doc's description
of the format.

`vendor.toml` lives at the root of the project CodeCompass is run
against, with one `[[vendor]]` table per tracked dependency.

## Fields

`VendorConfig` (`src/codecompass/core.py:22-35`) is a frozen dataclass
with **exactly two fields**:

| Field | Type | Required | Real validation |
|---|---|---|---|
| `name` | string | yes | Any non-missing value is accepted as-is — `config.py`'s `_require_field` only checks the key is present, not that the string matches anything (no format check, no existence check against the ecosystem's own package index). |
| `ecosystem` | string | yes | Must be one of the four `Ecosystem` enum members (`src/codecompass/core.py:13-19`): `npm`, `python`, `cargo`, `haskell`. Anything else raises `ConfigError` naming the vendor and listing the valid values. |

No other field is read by `load_vendor_config`. A vendor.toml carrying a
legacy `depth = "surface"`/`depth = "full"` key (retired
`decisions/0031`/`decisions/0035`) still parses without error or
warning — `_parse_entry` simply never looks at that key.

## Real file, this checkout

```toml
[[vendor]]
name = "anthropic"
ecosystem = "python"

[[vendor]]
name = "pipdeptree"
ecosystem = "python"

[[vendor]]
name = "rich"
ecosystem = "python"

[[vendor]]
name = "typer"
ecosystem = "python"
```

(this repository's own real `vendor.toml`, tracking its own four
dependencies).

## Validation behaviour

Parsing is **fail-fast** (`config.py`'s `ConfigError` docstring): the
first invalid `[[vendor]]` entry raises, naming the vendor label (its
own `name` if present, else `entry #N`) and the specific problem. It
does not collect every issue in the file first — fix one, re-run, see
the next.

```
$ codecompass sync    # vendor.toml has ecosystem = "ruby"
error: vendor.toml: vendor 'foo' has invalid ecosystem 'ruby' (expected one of: npm, python, cargo, haskell)
```

(exact message format from `config.py`'s `_require_enum`).

## What determines the rest, per vendor

Nothing else in `vendor.toml` controls what a vendor gets — everything
else is either unconditional or usage-driven, read from
`context-graph.db` rather than from config:

- **Cloning and deterministic digest generation** happen for every
  tracked vendor on every `sync`, unconditionally (`decisions/0033`) —
  there is no per-vendor opt-out.
- **AI enrichment** (a vendor's grounded `Description` section,
  `OVERVIEW.md`, per-symbol purposes, and a generated Skill) is
  triggered only for vendors the context graph shows are actually
  imported/used by your own project source, with no current enrichment
  — never by a `vendor.toml` flag (`decisions/0031`). See
  [`docs/domain/concepts/vendor.md`](../../../docs/domain/concepts/vendor.md)
  for the full domain-level definition of what a "vendor" is and isn't,
  and [`docs/domain/concepts/adapter.md`](../../../docs/domain/concepts/adapter.md)
  for how `ecosystem` maps to the code that actually talks to each
  vendor's ecosystem tooling.

## Writing `vendor.toml` yourself

Two ways: `codecompass init --scan <manifest> [...]` (explicit,
errors if `vendor.toml` already exists), or just running bare
`codecompass` (auto-discovers manifests at the project root and
idempotently extends an existing `vendor.toml`, appending only
newly-discovered dependencies — see [`quickstart.md`](quickstart.md)).
Either way, every discovered dependency is written as a bare
`name`/`ecosystem` pair — safe to run immediately against a large
existing dependency list, since writing the file itself never clones
anything or calls the Anthropic API (that happens on `sync`/bare
`codecompass`'s own later steps, not on discovery/writing).

Hand-editing is also fine — it's plain TOML, parsed with the standard
library's `tomllib` (no extra dependency needed, since
`requires-python >=3.11`, per `pyproject.toml`'s own comment).
