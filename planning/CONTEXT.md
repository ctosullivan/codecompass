# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 3: Deterministic tree generation — planned, not yet implemented.
This is still the next phase to actually build.** Phase 4 is also now
planned (see below) but is blocked on Phase 3's code existing, so it does
not change what happens next.

## What was just completed

Wrote and reviewed `planning/phase-4-sync-index-init.md` (plan-only
session, per `CLAUDE.md` §1 — mirrors the Phase 2/3 plan-writing sessions'
precedent). Scope: real `init`/`sync`/`index` command logic replacing
their current `cli.py` stubs — a new `get_adapter` dispatch factory
(`adapters/__init__.py`); `sync.py` orchestrating each vendor (adapter
calls, Phase 3's tree renderers, a pruned `vendor/<name>/src/` snapshot
copy for `depth = full`, per-vendor `CLAUDE.md` templating via a new
`claude_md.py`); `index.py`'s idempotent marker-based routing-table
injection into the project root `CLAUDE.md`; and `discovery.py`'s
manifest-based `vendor.toml` bootstrap for `init --scan`. Confirmed with
the user that `init` belongs in Phase 4 (matching `cli.py`'s existing
`_PHASE_BY_COMMAND` mapping and `docs/cli-reference.md`, which both
already said so) even though `planning/ROADMAP.md`'s old Phase 4 row text
only named `sync`/`index` — that row text is corrected in this commit.
**Phase 4 has a hard blocking dependency on Phase 3's code (`symbols.py`/
`deptree.py`/`filetree.py`) actually existing** — `sync.py` calls directly
into Phase 3's renderers, which are still only planned. `planning/ROADMAP.md`
and `CHANGELOG.md` updated in the same commit as the plan file, per
`CLAUDE.md` §1/§2/§3. **No command implementation code has been written
yet** — that's a separate, later session, and cannot start before Phase 3
is implemented.

## Decisions made this session not already captured in an ADR

- None — Phase 4's design decisions (init in scope, looser snapshot
  pruning than FILETREE's, gap-analysis section omitted not stubbed,
  known-gotchas sourced from `DepNode.side_effects`, hand-rolled TOML
  writing, error-not-overwrite on existing `vendor.toml`) are all recorded
  in `planning/phase-4-sync-index-init.md`'s Design decisions section;
  none rise to ADR-worthy architectural tradeoffs on their own.
- Phase 3's decisions (extraction approach, `deptree.json` shape) remain
  as recorded previously — the extraction-approach one is still slated to
  become a new ADR once Phase 3 is actually implemented, per that plan
  file's Same-commit doc updates list. Unchanged by this session.

## Next concrete step

**Implement `planning/phase-3-tree-generation.md` first** — `symbols.py` +
tests, then the `cargo.py`/`python.py` adapter refactor onto it, then
`deptree.py` + tests, then `filetree.py` + tests, then the new ADR, then
Phase 3's doc/changelog/context closeout. Only once that's done and
merged does `planning/phase-4-sync-index-init.md` become implementable:
`get_adapter` dispatch, then `claude_md.py` + tests, then `sync.py` +
tests, then `index.py` + tests, then `discovery.py` + tests, then `cli.py`
wiring + `test_cli.py`, then Phase 4's doc/changelog/context closeout.

**Still outstanding, not a blocker for either phase but worth
remembering**: once a Rust toolchain is available anywhere in the
pipeline, `decisions/0014` requires validating the Cargo adapter's
fixture assumptions and regex-based `pub` extraction against real `cargo
metadata` output and a real crate — currently entirely unverified.
