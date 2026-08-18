# Phase 16: Retire `Depth`

## Scope

Now safe — sequenced *after* phases 13-15 have already replaced every
call site that reads `Depth` for a real behavioral decision (cloning,
grounded description, per-vendor Skill gating, routing-table display,
`promote`'s existence). This phase is the trailing cleanup: delete the
now-genuinely-unused data-model concept. See `planning/ROADMAP.md`'s
renumbering note and `planning/CONTEXT.md` for the full account of why
this phase was moved from its originally-planned position (second in the
arc) to last-before-`/discovery`.

**Covered:**
- `src/codecompass/core.py` — delete the `Depth` enum entirely.
  `VendorConfig` narrows from `(name, ecosystem, depth)` to `(name,
  ecosystem)`. No replacement field — enrichment status lives in the
  graph (`decisions/0031`), not vendor config.
- `src/codecompass/config.py` — `_parse_entry` stops calling
  `_require_enum(..., "depth", Depth)`; `VendorConfig(name=name,
  ecosystem=ecosystem)` construction drops the `depth=` argument. A
  legacy `vendor.toml` with a `depth = "surface"`/`depth = "full"` line
  on an entry is **silently tolerated and ignored** on read — the parser
  simply never looks at that key anymore, so an unrecognized field
  doesn't raise `ConfigError`. No migrate command; the field is allowed
  to linger harmlessly in a hand-edited file (an explicit,
  previously-confirmed tradeoff — see `decisions/0031`'s Alternatives
  considered).
- `src/codecompass/discovery.py` — `render_vendor_block` stops emitting
  the `depth = "..."` line; `write_vendor_toml`/`_bootstrap`'s (in
  `cli.py`) `VendorConfig(name=name, ecosystem=ecosystem, depth=
  Depth.SURFACE)` construction sites drop the `depth=` kwarg and the now-
  unused `Depth` import.
- `src/codecompass/cli.py` — the `Depth` import and its one remaining
  construction site (bootstrap's new-vendor `VendorConfig(...)`, held
  back from Phase 15 specifically for this phase) updated.
- Full-repo sweep: `grep -rn "Depth\b" src/ tests/` (and `\.depth\b`)
  should return **zero** hits outside `config.py`'s tolerance-parsing
  comment/logic referencing the legacy field by name, and outside
  `decisions/*.md`/historical `planning/phase-*.md`/`CHANGELOG.md`
  entries (which correctly keep referencing `Depth` as historical fact —
  same treatment the Phase 9 rename already established for "depcompass"
  mentions).
- This repo's own `vendor.toml` (4 entries, each still carrying a
  `depth = "surface"` line from before this rework began) is a real,
  immediate test case for the tolerate-on-read behavior — not just a
  fixture.
- Tests: `tests/test_core.py`, `tests/test_config.py`,
  `tests/test_discovery.py`, `tests/test_cli.py` updated to construct
  `VendorConfig` without `depth=`; `tests/test_config.py` gains a new
  case loading a `vendor.toml` fixture with a legacy `depth = "full"`
  line, asserting it parses successfully and the field is simply absent
  from the resulting `VendorConfig`.

**Explicitly deferred / out of scope:**
- Nothing new — this phase's entire point is removal, not addition.
  Everything it removes was already made behaviorally inert by phases
  13-15.

## Design decisions

**Silently tolerate, never re-write.** `config.py` reads a legacy
`vendor.toml` without erroring, but nothing in this phase (or any later
one) rewrites an existing file to strip the stale `depth =` lines —
`rewrite_vendor_toml`/`append_vendor_toml` (still used by whatever
remains of vendor.toml persistence after `promote`'s removal) simply
never emit the field going forward, so a file only loses its `depth =`
lines the next time something in the codebase actually rewrites that
specific vendor's block, not proactively. This was flagged and
explicitly confirmed as the intended tradeoff during this rework's
original planning phase, not decided fresh here.

## Files

- `src/codecompass/core.py` — `Depth` enum deleted, `VendorConfig`
  narrowed.
- `src/codecompass/config.py` — `depth` parsing dropped, tolerant of a
  legacy key.
- `src/codecompass/discovery.py`, `src/codecompass/cli.py` — `Depth`
  import + construction sites updated.
- `tests/test_core.py`, `tests/test_config.py`, `tests/test_discovery.py`,
  `tests/test_cli.py` updated; new legacy-`vendor.toml` fixture case in
  `tests/test_config.py`.
- `docs/config-schema.md` — `depth` field removed from the documented
  schema, with a note that a legacy file containing it still loads
  without error. `architecture/overview.md`'s "Core data model" section
  — `Depth`/`VendorConfig.depth` bullets removed.
  `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md`.

## Verification

- `pytest` — full suite passes, including the new legacy-`vendor.toml`
  tolerance case.
- `ruff check .` — clean.
- `grep -rn "Depth" src/ tests/` returns zero hits outside
  `config.py`'s tolerance logic (which references the string `"depth"`
  as a dict key to ignore, not the type `Depth`, so this should in fact
  be a true zero).
- Manual, against this repo's own real `vendor.toml` (untouched since
  before this rework, still carrying `depth = "surface"` on all four
  entries): run `codecompass sync`, confirm it parses without error and
  behaves identically to a `depth`-free file — the concrete proof the
  tolerance behavior works against a real, not just fixture, legacy file.
