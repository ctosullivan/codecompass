# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 3: Deterministic tree generation — done.** Phase 4 (`init`/
`sync`/`index` commands) is planned and its blocking dependency on Phase
3's code is now resolved — Phase 4 is implementable next.

## What was just completed

Implemented `planning/phase-3-tree-generation.md` in full: `depcompass.symbols`
(`Symbol(name, purpose)` plus `extract_python_symbols`, `extract_rust_symbols`,
a new `extract_npm_symbols`, and `purpose_for_file` with a generic
comment-marker fallback for files no ecosystem parser claims);
`adapters/cargo.py`/`python.py` refactored to call into it instead of
keeping private extraction copies; `depcompass.deptree`
(`render_deptree_markdown`/`render_deptree_json` — diamond-dependency
dedup via back-references, dev-only children always collapsed to a count,
an explicit depth-cap collapse notice); `depcompass.filetree`
(`render_filetree_markdown`/`render_filetree_json`/`build_symbol_index` —
a pruned, deterministic directory walk, per-file purpose annotations, a
capped flat symbol index with an explicit "+N more" notice). New ADR
`decisions/0015` records the reuse-adapter-parsing extraction strategy.
`architecture/overview.md`, `planning/ROADMAP.md`, and `CHANGELOG.md`
updated to match. All tests pass (68 total: 67 passed, 1 skipped — the
Cargo live smoke test, unchanged from Phase 2 — up from 42 at the end of
Phase 2), `ruff check .` is clean.

**One real, disclosed behavior change surfaced during implementation**
(documented in `architecture/overview.md`'s Known footguns and
`decisions/0015`'s Consequences, not just here): switching
`CargoAdapter.readme_and_api_surface()` to the new name-based
`extract_rust_symbols` changed its output format from raw `pub fn ...`
signature lines to `name: purpose`. `tests/test_adapter_cargo.py` was
updated to match — this was anticipated and explicitly permitted by the
phase-3 plan's Tests section, not an unplanned deviation. The same switch
also incidentally *resolved* the previously-documented "misses multi-line
signatures" limitation for name capture, since a function's name is fully
present on the opening `pub fn` line regardless of how long its signature
runs.

## Decisions made this session not already captured in an ADR

- None beyond what's captured in `decisions/0015` and
  `planning/phase-3-tree-generation.md` — the Cargo output-format change
  and the incidental multi-line-signature fix are implementation
  consequences of that ADR's decision, not separate architectural
  tradeoffs, recorded as footguns/Consequences rather than new ADRs.

## Next concrete step

Implement `planning/phase-4-sync-index-init.md` — its blocking dependency
(Phase 3's `symbols.py`/`deptree.py`/`filetree.py` existing as real code)
is now satisfied. Order per that plan: `get_adapter` dispatch
(`adapters/__init__.py`), then `claude_md.py` + tests, then `sync.py` +
tests, then `index.py` + tests, then `discovery.py` + tests, then
`cli.py` wiring + `test_cli.py`, then Phase 4's doc/changelog/context
closeout.

**Still outstanding, not a Phase 4 blocker but worth remembering**: once
a Rust toolchain is available anywhere in the pipeline, `decisions/0014`
requires validating the Cargo adapter's fixture assumptions and regex-
based `pub` extraction against real `cargo metadata` output and a real
crate — currently entirely unverified. Additionally, `extract_npm_symbols`
(new in Phase 3) is untested against real-world `.d.ts` authoring styles
beyond hand-written fixtures — worth revisiting once real npm packages
with richer `.d.ts` files are exercised (e.g. during Phase 4's end-to-end
`sync` verification).
