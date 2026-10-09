# Testing

## Running the suite

```bash
pytest
```

`pyproject.toml` sets `testpaths = ["tests"]`. One test module roughly per `src/codecompass/` module (e.g. `tests/test_sync.py`, `tests/test_graph.py`, `tests/test_knowledge_intermediate.py`), plus test modules for the maintainer-only `scripts/` tooling (`tests/test_check_knowledge_base.py`, `tests/test_check_user_docs.py`, `tests/test_prepare_cleanroom_branch.py`, `tests/test_cleanroom_broker.py`, `tests/test_cleanroom_prompt_assembler.py`), imported directly by file path since `scripts/` is deliberately not an importable package.

## Fixtures

`tests/fixtures/` holds shared, hand-written input fixtures — sample manifests, lock files, a small real demo project (`tests/fixtures/ledgerkit_lifecycle_demo/`, demonstrating the full context-edge enrichment lifecycle across two cycles against a local project, including one honestly-recorded investigation hiccup, not a cleaned-up idealized transcript) — reused across several test modules rather than duplicated per module.

## The `smoke` marker

```toml
markers = [
    "smoke: exercises a real external tool (npm/cargo) — network/toolchain dependent, skipped automatically when the tool isn't present",
]
```

Tests marked `@pytest.mark.smoke` (and conditionally `@pytest.mark.skipif`) exercise a real toolchain directly — e.g. a live `cargo`/`npm`/`stack` invocation — rather than the fixture-mocked subprocess seam every other adapter test uses. They skip cleanly, not fail, when the required tool/submodule/reference checkout isn't present. This is the deliberate, stated default test strategy (adapter tests use fixture-mocking as the *primary* strategy, with live-subprocess smoke tests as a secondary, environment-dependent confirmation).

## Protocol conformance

`tests/test_protocol_conformance.py` validates the `codecompass-adaptor-protocol` submodule's own `conformance/manifest.json` vectors against its own JSON Schemas (via the `jsonschema` package) directly from the Python side — skips cleanly if the submodule isn't checked out. It also confirms the exact wire shape `HaskellAdapter` parses (`entry["name"]`, `entry.get("purpose")`, `entry["module"]`, `entry.get("kind")`, `entry.get("note")`) validates against the schema's own `symbols` definition.

## The Haskell adapter's own test suite

`adapters/haskell/test/Spec.hs`, run via `hspec` (declared in `codecompass-adaptor-haskell.cabal`'s `test-suite` stanza). Exercises `Adapter.Scanner` against real, trimmed excerpts from `hledger-lib`'s actual source (`AccountName.hs`, `Hledger.hs`, `Types.hs`, used under GPL-3.0-or-later as real-world fixtures, attributed in each fixture file's own header comment) plus two synthetic fixtures (`NoExportList.hs`, `TypeAllCtors.hs`), and `Adapter.Deps` against recorded real-shaped `stack dot`/`stack ls dependencies` text — not a live `stack` invocation, so these tests run without a toolchain present.
