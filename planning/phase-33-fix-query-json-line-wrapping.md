# Phase 33: Fix invalid JSON from `query --json`'s Rich line-wrapping

## Status

`done`

## Context

Found during the `/discovery` session testing Phase 21/22/27/28/29's
relationship-graph quality: `codecompass query vendor anthropic --json`
produces output that fails `json.loads()` with `Invalid control character`.
Root cause confirmed directly (not assumed): every `query` subcommand's
`--json` branch does `console.print(json.dumps(payload, indent=2))` —
using the shared Rich `Console` instance, which word-wraps printed text by
inserting real line breaks to fit the terminal/default width (confirmed
against `vendor/rich/src/docs/source/console.rst`: "Rich word wraps text
you print by inserting line breaks. You can disable this behavior by
setting `soft_wrap=True`"). When a JSON string value is long enough to
cross that width, Rich's wrap point lands *inside* the string's content,
inserting a literal newline where the JSON has none — producing text that
looks like formatted JSON but doesn't parse.

This is why no existing test caught it: every current `--json` test fixture
is small enough (short vendor/symbol names, short test digests) that no
printed line ever reaches the wrap width, so `json.loads(result.output)`
has always passed in tests. It reproduces reliably against this repo's own
real data (`anthropic` has 1,545 symbols and several long `purpose`
strings) but not against any existing fixture.

## Scope

**Covers:**
- Every `console.print(json.dumps(...))` call site in `cli.py`'s `query`
  subcommands (`vendors`, `vendor`, `symbol`, `skills`, `relations` — five
  sites) gains `soft_wrap=True`, matching Rich's own internal
  `Console.print_json` (`self.print(json_renderable, soft_wrap=True)`) —
  not a new pattern invented for this fix, the same one Rich uses
  internally for exactly this case.
- A regression test with a value long enough to actually cross Rich's
  default wrap width, proving the bug reproduces without the fix and
  parses cleanly with it (a short-fixture test wouldn't actually exercise
  the bug, per Context above).

**Explicitly does not cover:**
- Any change to what data `--json` returns — output *content* is
  unaffected, only whether printing it corrupts it.
- The separate, unrelated `check` version-drift question raised in the
  same `/discovery` session — investigated and confirmed **not** a bug:
  `staleness.check_vendor`'s "live" column reads the ecosystem adapter's
  *currently-installed* version in this environment (`adapter.
  installed_version()`), not a PyPI-latest lookup; this repo's local
  `.venv` genuinely has `anthropic==0.109.1` installed
  (`importlib.metadata.version("anthropic")` confirmed it directly),
  older than the `0.121.0` recorded at an earlier sync — real environment
  drift, working as designed. No code change, no plan needed.

## Design decisions

- **`soft_wrap=True`, not a separate non-Rich print path.** Keeps every
  `--json` call site using the same `console` object and one-line change,
  rather than introducing a second output mechanism (e.g. `print()`/
  `sys.stdout.write`) that would need its own encoding/newline handling.
  Mirrors Rich's own `print_json` precedent exactly.

## Files

- `src/codecompass/cli.py` — `soft_wrap=True` on the five `console.print(json.dumps(...))` call sites.
- `tests/test_cli.py` — one new regression test with a long enough value to actually cross the wrap width.
- `CHANGELOG.md` — `[Unreleased]` entry, `Fixed` category.

## Verification

- `pytest` passes, including the new regression test (confirmed to fail
  against the pre-fix code, not just pass against the post-fix code).
- `ruff check .` clean.
- Live dogfood: re-run `codecompass query vendor anthropic --json` against
  this repo's real graph and confirm `python -c "import json,sys;
  json.load(sys.stdin)"` accepts the output cleanly.
- Core-logic diff read directly against this plan before marking `done`.
