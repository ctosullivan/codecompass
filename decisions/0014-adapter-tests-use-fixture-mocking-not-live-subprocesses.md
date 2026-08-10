# 0014. Adapter tests use fixture-mocking, not live subprocesses, as the primary strategy

## Status

Accepted

## Context

The npm, Python, and Cargo adapters (`decisions/0008`) all shell out to
ecosystem-native tooling (`npm ls --json`, `pipdeptree --output
json-tree`, `cargo metadata --format-version 1`). The Cargo toolchain
(`cargo`/`rustc`) is not installed in the primary dev environment — a gap
flagged as early as `decisions/0008`'s Consequences section — which would
otherwise block writing any *tested* Cargo adapter code at all.

## Decision

All three adapters' core parsing logic is tested against hand-written
fixture JSON, injected via monkeypatching a shared `_run_json` seam
(`src/depcompass/adapters/base.py`) that every adapter module imports and
calls. No real toolchain is required for any adapter's core tests.

npm and Python additionally get a small number of live smoke tests where
the toolchain is actually present in this environment (`npm install` a
real package; construct the Python adapter against an already-installed
dependency like `pytest`) — both ran successfully during Phase 2
implementation. Cargo's live smoke test is written and guarded with
`pytest.mark.skipif(shutil.which("cargo") is None, ...)` — present and
ready, but does not execute in this environment today.

## Alternatives considered

- **Require Cargo as a hard Phase 2 setup dependency.** Rejected — adds
  environment-setup burden unrelated to a docs-generation tool, and
  doesn't resolve the immediate blocker.
- **Skip Cargo adapter tests entirely until a toolchain is available.**
  Rejected — `decisions/0008` already committed to shipping all three
  adapters together in the MVP; untested-but-written code shipping
  silently is worse than clearly flagged fixture-only coverage with an
  explicit follow-up noted (see Consequences).

## Consequences

- Fixture-based tests do **not** catch real-world drift in `npm ls
  --json`, `pipdeptree --output json-tree`, or `cargo metadata
  --format-version 1` output format — if any of these tools changes its
  JSON shape in a future version, these tests keep passing against a
  stale fixture while the real adapter silently breaks against live
  output. This is an accepted, explicit gap: mitigated for npm/Python by
  the live smoke tests (which did catch two real discrepancies during
  Phase 2 implementation — see below — and will catch future drift the
  next time they run), left as an open risk for Cargo until its toolchain
  is available anywhere in the pipeline.
- **This approach already proved its worth during implementation**:
  building against fixtures first, then validating with live smoke tests,
  surfaced two real bugs fixtures alone would have hidden — (1) on
  Windows, `npm` resolves to a `.cmd` shim that `subprocess.run` can't
  launch by bare name without a shell (fixed by resolving via
  `shutil.which` before invoking); (2) a bare `pipdeptree` isn't
  reliably on `PATH` outside an activated venv, fixed by invoking it as
  `sys.executable -m pipdeptree` instead. Both fixes live in
  `src/depcompass/adapters/base.py` and `python.py` respectively, and
  neither would have been caught by fixture-only testing.
- A future maintenance task should periodically re-verify fixtures
  against real tool output, not just once at Phase 2 — this is not a
  one-time validation.
- Once a Rust toolchain is available anywhere in the pipeline (local dev
  or CI), a follow-up should: confirm real `cargo metadata
  --format-version 1` output actually matches
  `tests/fixtures/cargo_metadata.json`'s assumed field names/nesting; run
  the Cargo live smoke test for the first time; validate the regex/line-
  based `pub` extraction against a real crate with nontrivial generics.
