# 0016. Gap-analysis tests never call the live Anthropic API

## Status

Accepted

## Context

Phase 5 adds `depcompass.gap_analysis`, the only module in this project
that calls an external, non-free API. Phase 2 faced an analogous
"how do we test something that talks to the outside world" question for
the npm/Python/Cargo adapters, and resolved it with a fixture-mocking
primary strategy plus a small number of *free* live smoke tests
(`decisions/0014`) — `npm install lodash`, and a Python adapter run
against this repo's own already-installed `pytest`, both cost nothing
and need no credential beyond what's already present in a normal dev
environment.

Gap analysis doesn't have a free equivalent. Every real call to
`claude-haiku-4-5-20251001` costs money and requires a valid
`ANTHROPIC_API_KEY` to be present in whatever environment runs the test
suite — including CI, where such a key becoming a required secret for
`pytest` to pass is a meaningfully different commitment than "npm happens
to be installed."

## Decision

No test in this project's suite ever makes a real Anthropic API call —
not even one guarded, opt-in smoke test the way Phase 2 kept for npm and
Python. Every test exercising `gap_analysis.generate_gap_analysis` (and
by extension `sync_vendor` for `depth = full` vendors) monkeypatches the
`_call_anthropic` seam (`src/depcompass/gap_analysis.py`), the same role
`_run_json` plays for the ecosystem adapters. A smaller set of tests
exercises `_call_anthropic` itself against a fake `anthropic.Anthropic`
client (constructed in-test, not a real network client) to verify the
tool-use response parsing and SDK-error-wrapping logic without going
over the network.

## Alternatives considered

- **One opt-in, `skipif`-guarded live smoke test**, mirroring Phase 2's
  pattern (e.g. `pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"))`).
  Rejected — unlike a missing `npm` binary, a present `ANTHROPIC_API_KEY`
  doesn't imply "this call is free to make." A smoke test that silently
  starts spending real money the moment a key happens to be present in
  the environment (e.g. a developer's global shell profile, or a future
  CI secret added for an unrelated reason) is a worse failure mode than
  a smoke test that's simply always skipped in practice.
- **Record-and-replay cassettes** (e.g. VCR-style fixture recording of
  real API responses). Rejected for this phase — adds a new test
  dependency and a cassette-maintenance burden for a single module, when
  a fixed fake tool-use response already exercises the same parsing code
  path. Worth revisiting if gap analysis grows meaningfully more complex
  response handling later.

## Consequences

- `gap_analysis.py`'s prompt/schema correctness against the *real* model
  (does `claude-haiku-4-5-20251001` reliably honor the forced tool-use
  schema exactly as designed, does the technical/conversational split
  actually read well) is **not validated by the automated test suite at
  all** — this is an accepted, explicit gap, the same shape as
  `decisions/0014`'s accepted gap for the Cargo adapter, but for a
  different underlying reason (cost, not toolchain availability).
- A human must manually run `depcompass sync` against a real `depth =
  full` + `context_path` vendor with a real `ANTHROPIC_API_KEY` at least
  once before trusting this phase's output quality — noted in
  `planning/phase-5-gap-analysis.md`'s Verification and
  `planning/CONTEXT.md`, not just here.
- If Anthropic changes the tool-use response shape in a future SDK
  version, or `claude-haiku-4-5-20251001` is deprecated, nothing in CI
  will catch it — this is the same category of risk
  `decisions/0014` already accepted for `npm ls`/`pipdeptree`/`cargo
  metadata` output drift, now extended to the Anthropic API surface.
