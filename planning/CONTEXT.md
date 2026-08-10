# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 3: Deterministic tree generation — planned (plan file written,
not yet implemented).**

## What was just completed

Wrote and reviewed `planning/phase-3-tree-generation.md` (plan-only
session, per `CLAUDE.md` §1 — mirrors the Phase 2 plan-writing session's
precedent). Scope: a new `src/depcompass/symbols.py` module generalizing
the per-ecosystem parsing adapters already do for API-surface extraction
(Cargo's `_extract_pub_items`, Python's `ast`-based `__all__`/docstring
extraction) into reusable per-file symbol/purpose extractors, plus a new
npm `.d.ts` export scan that doesn't exist yet; `src/depcompass/deptree.py`
(diamond dedup, dev-only collapsing, depth-capped `DEPTREE.md` +
`deptree.json`, the JSON sidecar mirroring the same deduplicated/capped
shape rather than the adapter's raw tree); `src/depcompass/filetree.py`
(pruned `FILETREE.md` + `filetree.json` with purpose annotations, plus a
capped flat symbol index). `adapters/cargo.py`/`python.py` will be
refactored to call into `symbols.py` rather than keeping private copies of
that logic, with no behavior change to either adapter's public methods.
Two design questions were resolved via user interview before finalizing
the plan: extraction reuses adapter parsing per-ecosystem (not one generic
heuristic), and `deptree.json` mirrors `DEPTREE.md`'s deduplicated/capped
view (not the adapter's full raw tree). `planning/ROADMAP.md` and
`CHANGELOG.md` updated in the same commit as the plan file, per
`CLAUDE.md` §1/§2/§3. **No tree-generation code has been implemented
yet** — that's a separate, later session.

## Decisions made this session not already captured in an ADR

- None yet — the two design decisions above (extraction approach,
  `deptree.json` shape) are recorded in `planning/phase-3-tree-generation.md`'s
  Design decisions section; the extraction-approach one is also slated to
  become a new ADR (number confirmed against actual repo state) once
  implementation actually happens, per the plan file's Same-commit doc
  updates list.

## Next concrete step

Implement `planning/phase-3-tree-generation.md`: `symbols.py` + its tests
first (everything else depends on it), then the `cargo.py`/`python.py`
adapter refactor onto it (existing Phase 2 tests must keep passing
unchanged), then `deptree.py` + tests, then `filetree.py` + tests, then
the new ADR, then the doc/changelog/context closeout — same
commit-per-logical-change pattern as Phases 0-2.

**Still outstanding, not a Phase 3 blocker but worth remembering**: once
a Rust toolchain is available anywhere in the pipeline, `decisions/0014`
requires validating the Cargo adapter's fixture assumptions and regex-
based `pub` extraction against real `cargo metadata` output and a real
crate — currently entirely unverified.
