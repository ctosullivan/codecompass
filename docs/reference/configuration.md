# Configuration reference

## `vendor.toml`

The project's own tracked-dependency manifest, at the project root. Format:

```toml
[[vendor]]
name = "turndown"
ecosystem = "npm"

[[vendor]]
name = "requests"
ecosystem = "python"
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | The package name, exactly as the matching ecosystem adapter needs it (e.g. the PyPI distribution name for Python). |
| `ecosystem` | string | yes | One of `npm`, `python`, `cargo`, `haskell` — any other value raises a configuration error. |

A legacy `depth = "surface"`/`depth = "full"` key is silently tolerated on an existing entry (parses without error) but is never read — this field was retired; cloning is now unconditional and AI enrichment is usage-driven, not a per-vendor toggle.

Written/extended by `codecompass` (bare command) and `codecompass init --scan`; read by every other command. `codecompass init` errors if the target file already exists; the bare command instead idempotently appends any newly-discovered vendor to an existing file, leaving already-tracked entries untouched.

### A known, confirmed self-dogfooding gap

CodeCompass's own `vendor.toml` currently tracks `anthropic`, `pipdeptree`, `rich`, `typer` — but **not** `pyyaml`, despite `pyproject.toml` declaring it a required runtime dependency, genuinely imported in `discovery.py` and `adapters/haskell.py`. The root cause is a real, confirmed limitation in `PythonAdapter`: it uses one single `config.name` field for two different lookups that need two different strings for this specific package — `importlib.metadata.version()` needs the PyPI distribution name (`pyyaml`), while `importlib.util.find_spec()` needs the import name (`yaml`). Every other currently-tracked Python dependency happens to have an identical distribution and import name, which is why this split was never exposed before. This needs a schema change to `VendorConfig` to fix properly — not a one-line `vendor.toml` edit — and has not been fixed as of this writing.

## Environment variables

| Variable | Required for | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | Phase B AI enrichment (bare command / whole-project `sync`), `codecompass chat` | Read implicitly by the Anthropic Python SDK's own standard credential convention — CodeCompass's own code (`enrichment.py`, `relation_enrichment.py`, `chat.py`) constructs `anthropic.Anthropic()` with no explicit key argument. |

## Cost model for AI enrichment

A flat estimate of `$0.02` per Anthropic API *batch* (not per vendor or per relationship — several candidates can share one batched call), using `claude-haiku-4-5-20251001` throughout. Stated in the source as a rough, fixed placeholder, not live-queried pricing — not a guarantee of actual billed cost.
