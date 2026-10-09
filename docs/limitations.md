# Limitations

Derived directly from current evidence — not carried forward from any assumption about what an older version of this project's documentation might have said.

## Adapters

- **Cargo**: unverified against real `cargo metadata` output — disclosed directly in `cargo.py`'s own module docstring (no Rust toolchain was available to confirm it against a real invocation; its parsing logic is unit-tested only against hand-written fixture JSON modeled on cargo's public schema).
- **npm, Cargo**: no minimum tool version is documented anywhere in the available evidence (unlike Python, `>=3.11`, or Git, `>=2.7`) — checked directly, genuinely absent, not merely hard to find.
- **Haskell (external adapter)**: no minimum Stack/GHC version is documented for consuming the submodule's own pinned `nightly-2026-09-01` resolver snapshot. Setup instructions beyond `git submodule update --init` + `stack build` are only breadcrumb-deep in the available evidence (the in-repository error strings point at an excluded, more detailed document this reconstruction cannot see).

## Self-dogfooding

CodeCompass's own `vendor.toml` does not track `pyyaml`, despite it being a real, required runtime dependency genuinely imported in two modules. The root cause is a real, specific limitation in `PythonAdapter`: it has no way to represent "the PyPI distribution name and the import name for this package differ" with the current `VendorConfig(name, ecosystem)` schema. See `docs/reference/configuration.md`.

## Knowledge layer

- The shipped `codecompass knowledge` CLI only ever creates/mutates `Claim` or `Requirement` records — `Observation`/`Evidence`/`Decision`/`Derivation` records must be hand-authored YAML, by design, not an incomplete feature.
- No shipped validator exists for an adopting project's own `planning/knowledge/` tree beyond `knowledge_intermediate.py` itself — the maintainer-only `scripts/check_knowledge_base.py` is hard-coded to this one repository.
- No captured end-to-end terminal transcript exists in the available evidence for the knowledge-reconciliation CLI workflow, unlike the sync/enrichment pipeline — its behaviour is fully specified in source and exhaustively unit-tested, but this documentation describes it from that, not from a worked session.

## Contributing / process material

Genuinely thin in the available evidence: the only process-relevant decisions are bare titles with no recoverable rationale beyond "no AI attribution in commits." No branch strategy, PR-review convention, or fuller commit convention is confirmed anywhere.

## Maturity signal

`pyproject.toml` simultaneously declares `version = "1.0.0"` and a `Development Status :: 4 - Beta` classifier — two independent maturity signals that disagree, with nothing in the available evidence resolving which should be trusted more.

## No dedicated documentation site

Stated as a deliberate v1.0 scope decision (`decisions/0039`), not an oversight: this `README.md` plus the `docs/*.md` tree, rendered on GitHub, is the whole of CodeCompass's documentation delivery for this release.

## Licensing is not uniform across the three repositories involved

CodeCompass itself and the reference Haskell adapter are both GPL-3.0-or-later; the external adapter *protocol* repository is **MIT** — a real, checked difference, not an assumption that related repositories under the same account share a license.
