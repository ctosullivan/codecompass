# Phase 13: Universal source cloning

## Scope

**Covered:**
- `src/codecompass/sync.py` — `sync_vendor` restructured to split two
  decisions that today are combined behind one `if config.depth is
  Depth.FULL:` gate:
  1. **Cloning now happens unconditionally**, for every vendor — the gate
     around `resolve_and_clone`/`_copy_source_snapshot` is removed.
     Cloning itself costs nothing (no AI call); the only reason it was
     ever depth-gated was that it existed solely to feed grounded
     description, which *was* depth-gated. Extends
     `decisions/0004`/`0010`'s "clone the upstream repo, don't reference
     a local install" posture from `FULL`-only vendors to all of them.
  2. **Grounded-description generation stays gated on `config.depth is
     Depth.FULL`** — unchanged in this phase. `Depth` is not retired
     until Phase 16, and `promote` (the only thing that ever sets
     `depth = FULL`) is not removed until Phase 15; Phase 14's batched
     `enrichment.py` doesn't get wired in until Phase 15 either. This
     phase's *only* behavior change is: cloning is universal, enrichment
     eligibility is not.
  - `resolve_and_clone`'s success/failure result is now tracked
    independently of whether description generation runs — a `depth =
    surface` vendor that fails to clone still falls back to
    `_copy_source_snapshot(source_location, src_dest)` exactly as a
    `depth = full` vendor already does today, just without ever
    attempting a description call.
  - `FILETREE.md`/`filetree.json` generation switches from always reading
    `adapter.source_location()` (the locally-installed package) to
    reading the clone root (`repo_root`) when cloning succeeded, falling
    back to `source_location()` when it didn't — same fallback semantics
    already established for the `src/` snapshot itself, now also applied
    to the tree-rendering source. This is a real, visible output change
    for every vendor: `FILETREE.md` now reflects the vendor's actual
    upstream repository (README, docs, tests, examples included) rather
    than a possibly-trimmed local install, for every tracked vendor, not
    just previously-`FULL` ones.
  - `VendorDigest.description_error` continues to carry a clone failure's
    message when cloning fails (unchanged field reuse — no new field
    needed), independent of whether a description was ever going to be
    attempted for that vendor.
- `src/codecompass/source_resolution.py` — **no logic changes.**
  `resolve_and_clone`/`_git_clone`/`SourceResolutionError`'s fail-loud,
  no-sdist-fallback contract carries forward unchanged in substance; only
  `sync_vendor` (its caller) changes how often it's invoked.

**Explicitly deferred / out of scope:**
- Retiring `Depth` or removing `promote` — Phase 15/16.
- Wiring batched enrichment — Phase 14 (library) / Phase 15 (CLI).
- Any change to `claude_md.py`'s Description section rendering —
  unaffected; it still keys off `digest.technical_description`/
  `description_error`, both still populated (or not) exactly as before,
  just now independent of whether a clone happened.

## Design decisions

**Splitting "clone" from "describe" is the direct mechanism behind
`decisions/0033`'s "clone-for-all replaces promote's clone" — implemented
here, ahead of `promote`'s actual removal (Phase 15), by design.** Landing
this as its own small phase, rather than folding it into Phase 15's
larger CLI rewire, keeps the description-vs-clone behavior split reviewable
in isolation: after this phase, `pytest` should show every vendor — not
just `depth = full` ones — getting a real `vendor/<name>/src/` clone and
a clone-sourced `FILETREE.md`, while `CLAUDE.md`'s Description section
and per-vendor Skill generation remain exactly as depth-gated as they are
today. This isolates one clearly-verifiable behavior change per commit,
consistent with every other phase in this arc.

## Files

- `src/codecompass/sync.py` — `sync_vendor` restructured as above.
- `tests/test_sync.py` — new coverage: a `depth = surface` vendor now
  gets a real `src/` clone attempt and clone-sourced `FILETREE.md`;
  existing `depth = full` behavior (description still gated) unchanged;
  clone-failure fallback behavior unchanged in substance, now exercised
  for surface vendors too.
- `architecture/overview.md` — "Tree generation" section updated:
  `FILETREE.md`'s source is now the clone (with fallback), not
  unconditionally `source_location()`, for every vendor. "Grounded
  description" section's opening sentence clarified: cloning is no
  longer exclusive to this section's scope. `planning/ROADMAP.md`,
  `planning/CONTEXT.md`, `CHANGELOG.md`.

## Verification

- `pytest` — full suite passes.
- `ruff check .` — clean.
- Manual, against this repo itself: run `codecompass sync` (whole
  project — all four tracked vendors currently `depth = surface`),
  confirm every vendor now has a real `vendor/<name>/src/` directory
  (previously only a `depth = full` vendor would), and that none of them
  triggered a grounded-description call (no `OVERVIEW.md` appears for any
  of them, no API cost incurred) — the concrete proof the clone/describe
  split behaves as designed, not just by code inspection.
- Confirm `git` absence still surfaces as a clear `SourceResolutionError`
  (unchanged behavior, now reachable for every vendor instead of only
  `depth = full` ones) rather than a cryptic subprocess failure.
