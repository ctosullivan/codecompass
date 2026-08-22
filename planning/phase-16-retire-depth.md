# Phase 16: Retire `Depth`

## Scope

**Revised from the original version of this plan.** The first attempt at
implementing this phase found `Depth` was *not* fully behaviorally inert
after Phase 15, contrary to this file's original premise and
`planning/CONTEXT.md`'s "now safe" framing — `sync.py`, `claude_md.py`,
and `grounded_description.py` still gated real behavior on it, and
investigating why surfaced a real bug already on `main`: since Phase 15,
a whole-project `sync` re-run silently erases Phase B's enrichment
content from `CLAUDE.md`, because `sync_vendor` rebuilds each vendor's
file from scratch via a digest that never carries enrichment data, gated
on a `Depth` value nothing sets anymore. See `decisions/0035` for the
full account and the fix this revision incorporates. The originally-scoped
mechanical removal (`core.py`/`config.py`/`discovery.py`/`cli.py`) is
still exactly as small as first planned — it just isn't sufficient on its
own anymore.

**Covered:**
- **New, per `decisions/0035`, must land before the mechanical removal
  below (deleting `Depth` first would break these call sites):**
  - `src/codecompass/sync.py` — `sync_vendor` stops calling
    `grounded_description.generate_grounded_description` entirely. Before
    building its `VendorDigest`, it looks up this vendor's current
    enrichment record via `graph.vendor_profile(conn, config.name)`
    (read-only — open the graph the same cheap way `check`/`index`
    already do) and, if one exists, populates
    `technical_description`/`conversational_overview`/
    `action_pointer_file`/`action_pointer_note` from it. If no
    `context-graph.db` exists yet (a project that's never run a
    whole-project sync), this lookup is skipped gracefully, same as
    `index.py`'s existing "no graph yet" fallback.
  - `src/codecompass/claude_md.py` — `_render_description_section` drops
    its `Depth` gate; falls back to its own existing pattern: `if not
    digest.technical_description: return None`. The `**Depth:**`
    metadata line is removed (already planned).
  - `src/codecompass/grounded_description.py` and
    `tests/test_grounded_description.py` — **deleted**, not left as dead
    code. `enrichment.py` fully replaces its role; nothing calls it once
    `sync_vendor` no longer does.
  - `src/codecompass/enrichment.py` — `apply_results`'s minimal-digest
    construction drops its `Depth.FULL` placeholder (`VendorConfig(name,
    ecosystem)`, no third argument once `core.py`'s change below lands).
- **The original mechanical removal**, now safe once the above lands:
  - `src/codecompass/core.py` — delete the `Depth` enum entirely.
    `VendorConfig` narrows from `(name, ecosystem, depth)` to `(name,
    ecosystem)`. No replacement field — enrichment status lives in the
    graph (`decisions/0031`).
  - `src/codecompass/config.py` — `_parse_entry` stops calling
    `_require_enum(..., "depth", Depth)`; `VendorConfig(name=name,
    ecosystem=ecosystem)` construction drops `depth=`. A legacy
    `vendor.toml` entry with a `depth = "surface"`/`depth = "full"` line
    is **silently tolerated and ignored** on read — the parser simply
    never looks at that key, so it doesn't raise `ConfigError`. No
    migrate command.
  - `src/codecompass/discovery.py` — `render_vendor_block` stops emitting
    the `depth = "..."` line; every `VendorConfig(...)` construction site
    drops `depth=`; drop the now-unused `Depth` import.
  - `src/codecompass/cli.py` — drop the `Depth` import; update the
    remaining construction site (bootstrap's new-vendor `VendorConfig(...)`)
    to drop `depth=`.
- Full-repo sweep: `grep -rn "Depth\b" src/ tests/` and `grep -rn
  "\.depth\b" src/ tests/` should return **zero** hits after all of the
  above (outside `config.py`'s tolerance-parsing comment referencing the
  legacy TOML key by name, and outside `decisions/*.md`/historical
  `planning/phase-*.md`/`CHANGELOG.md` entries).
- This repo's own `vendor.toml` (4 entries, each still carrying a
  `depth = "surface"` line) is a real, immediate test case for the
  tolerate-on-read behavior — not just a fixture.
- Tests: `tests/test_core.py`, `tests/test_config.py`,
  `tests/test_discovery.py`, `tests/test_cli.py` updated to construct
  `VendorConfig` without `depth=`; `tests/test_config.py` gains a legacy
  `depth = "full"` fixture case (parses successfully, field simply
  absent from the result); `tests/test_sync.py` updated for
  `sync_vendor`'s new graph-lookup behavior (a vendor with an existing
  enrichment record gets its Description section reproduced on a plain
  re-sync — the direct regression test for the bug `decisions/0035`
  describes; a vendor with none, or no graph at all, gets no Description
  section, same as today); `tests/test_claude_md.py` updated for the
  gate's new truthiness-only logic (its existing surface-vendor
  regression test from Phase 13 should still pass unchanged in spirit —
  confirm it does, don't just assume).

**Explicitly deferred / out of scope:**
- No new caching/staleness logic for the graph lookup — `sync_vendor`
  already re-reads other persisted state (adapter calls, deptree.json)
  fresh on every call; this is the same posture, not a new pattern.
- Removing `enrichment.py`'s two-tier hash-based skip logic (Phase 14) —
  unrelated and unaffected by this change; that logic decides whether
  *Phase B* re-enriches, not what Phase A's deterministic resync shows.

## Design decisions

See `decisions/0035` for the graph-lookup/`grounded_description.py`
retirement reasoning in full, and `decisions/0031`'s Alternatives
considered for why `config.py` tolerates rather than migrates a legacy
`depth =` line (unchanged from the original plan).

## Files

- `src/codecompass/sync.py` — `sync_vendor` reads enrichment from the
  graph before building its digest; no more
  `grounded_description` import/call.
- `src/codecompass/claude_md.py` — `_render_description_section`'s gate
  simplified; `**Depth:**` line removed.
- `src/codecompass/grounded_description.py` — deleted.
- `src/codecompass/enrichment.py` — minimal-digest construction
  simplified.
- `src/codecompass/core.py` — `Depth` enum deleted, `VendorConfig`
  narrowed.
- `src/codecompass/config.py` — `depth` parsing dropped, tolerant of a
  legacy key.
- `src/codecompass/discovery.py`, `src/codecompass/cli.py` — `Depth`
  import + construction sites updated.
- `tests/test_core.py`, `tests/test_config.py`, `tests/test_discovery.py`,
  `tests/test_cli.py`, `tests/test_sync.py`, `tests/test_claude_md.py`
  updated; `tests/test_grounded_description.py` deleted; new legacy-
  `vendor.toml` fixture case in `tests/test_config.py`.
- `docs/config-schema.md` — `depth` field removed from the documented
  schema, with a note that a legacy file containing it still loads
  without error. `architecture/overview.md`'s "Core data model",
  "Grounded description", and "Tree generation" sections updated to
  reflect `grounded_description.py`'s retirement and `sync_vendor`'s new
  graph-lookup step. `planning/ROADMAP.md`, `planning/CONTEXT.md`,
  `CHANGELOG.md`.

## Verification

- `pytest` — full suite passes, including the new legacy-`vendor.toml`
  tolerance case and the re-sync-preserves-enrichment regression test.
- `ruff check .` — clean.
- `grep -rn "Depth" src/ tests/` returns zero hits outside `config.py`'s
  tolerance logic (a string key reference, not the type).
- Manual, against this repo's own real `vendor.toml` (still carrying
  `depth = "surface"` on all four entries): run `codecompass sync`,
  confirm it parses without error and behaves identically to a
  `depth`-free file.
- Manual, the direct proof of `decisions/0035`'s fix: enrich a real
  vendor (via bare `codecompass` or `sync` with `--yes`, in a scratch
  project — real API cost), confirm its `CLAUDE.md` has a Description
  section, then run `codecompass sync` (whole-project) again and confirm
  the Description section is still there afterward, not blanked.
