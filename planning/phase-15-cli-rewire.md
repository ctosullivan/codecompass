# Phase 15: CLI rewire

## Scope

This is the integration phase — every library built in Phases 10-14
(`graph.py`, `usage.py`, `doc_mapping.py`/`skill_scan.py`, universal
cloning, `enrichment.py`) becomes reachable from the actual CLI here.
Deliberately the largest phase in this arc, for the same reason Phase 7
(bootstrap + `promote`) was the largest phase in the original MVP: it's
where independently-built pieces get wired together into one coherent,
user-facing flow.

**Covered:**
- `src/codecompass/cli.py`:
  - **`promote` command removed entirely.** Its three former jobs
    (clone, enrich, generate Skill) are now automatic outcomes of
    bootstrap/`sync` below.
  - **Top-level `main` callback (bare `codecompass`) gains `--yes`
    and `--budget` options** — it currently has none. After the existing
    zero-cost Phase A work (`_bootstrap`'s discovery +
    `sync_all(new_configs, ...)` + `rebuild_project_graph` from Phases
    11-12), call `enrichment.select_candidates(conn)`; if non-empty,
    disclose estimated cost (`enrichment.estimate_cost`) and prompt for
    confirmation via `typer.confirm` unless `--yes`, then
    `run_enrichment_batches` + `apply_results` (respecting `--budget`
    via `check_budget`, aborting *before* any call if exceeded — same
    contract `check_budget` already guarantees). This is the literal
    mechanism behind `decisions/0033`: Phase A's zero-question guarantee
    is preserved *for Phase A specifically*; Phase B auto-triggers right
    after but keeps a real consent gate.
  - **`sync` command**: the whole-project branch (`vendor is None`)
    gains the same Phase B trigger as bare bootstrap, after
    `rebuild_project_graph`. The single-vendor branch (`sync <vendor>`)
    is unaffected — no graph rebuild, no enrichment trigger, exactly
    `decisions/0025`'s posture.
  - **`init --scan`**: unaffected in this phase (still the explicit,
    stricter-contract manifest-scan synonym); Phase A/B triggering is
    bare-bootstrap/`sync`-specific, not `init`'s concern, matching its
    existing scope boundary.
  - **New `query` command group**:
    - `query vendors [--unused] [--json]` — `graph.py`'s vendor list +
      enrichment status (and `unused_vendors` filtering).
    - `query vendor <name> [--json]` — `graph.vendor_profile`.
    - `query symbol <name> [--json]` — `graph.symbol_profile`.
    - `query skills [--unused-mentions] [--json]` — `graph.skills_index`.
    - Default rendering: Rich tables (reusing this project's existing
      `Table`/`Console` conventions from `check`'s output); `--json`
      dumps the raw dict/list. If `context-graph.db` doesn't exist yet,
      each subcommand prints a one-line note pointing at `sync` rather
      than a traceback — same graceful-skip posture `check`'s new
      section (below) uses.
  - **`check`**: gains report-only sections, skipped with a one-line
    note if `context-graph.db` doesn't exist — "Unused vendors"
    (`graph.unused_vendors`), "Documented but unused" /
    "Used but undocumented" (`graph.documented_but_unused`/
    `used_but_undocumented`), and "Third-party skill mentions with no
    backing vendor/symbol" (a `skill_scan`-derived query). **None of
    these affect `--strict`'s exit code** — confirmed via this rework's
    planning interview; `--strict` stays scoped to version-drift
    severity only, exactly as today.
  - `_bootstrap`'s `VendorConfig(name=..., ecosystem=..., depth=
    Depth.SURFACE)` construction (both here and in `discovery.py`) is
    **not** changed in this phase — `Depth` retirement is Phase 16,
    sequenced *after* this phase specifically so this phase's diff stays
    scoped to CLI/behavior wiring, not data-model shrinkage.
- `src/codecompass/index.py`:
  - `_CONSULT_WHEN_BY_DEPTH` → `_CONSULT_WHEN_BY_ENRICHED: dict[bool,
    str]` (`True`: "API questions and known gotchas", `False`: "general
    usage questions") — keyed by a new `enriched: bool` field on
    `RoutingRow`, sourced from a lightweight `graph.has_enrichment(conn,
    vendor_name) -> bool` query (Phase 10 gains this alongside its other
    query functions — small addition, noted here since it's this phase
    that first needs it).
  - `render_routing_table`'s "Depth" column → "Enriched" column
    (`config.depth.value` → `"yes"`/`"no"` from the new field).
  - `load_routing_rows` — still reads persisted `CLAUDE.md` for
    `version` exactly as today (cheap, side-effect-free, no graph
    rebuild triggered), additionally opens the graph read-only for the
    enrichment-status lookup. Gracefully falls back to `"no"` if
    `context-graph.db` doesn't exist yet (a project that's only run
    `init`/one `sync <vendor>`, never a whole-project sync) rather than
    erroring.
- `src/codecompass/skill.py`:
  - `render_tool_skill`: drops the `promote` bullet, adds
    `codecompass query`; drops `full_count`/the Depth-keyed vendor table
    column, replaced with an enrichment-count summary
    ("N tracked, M enriched") and an "Enriched" column, sourced the same
    way `index.py`'s routing table now is.
  - `write_vendor_skill`/`write_cursor_mdc`'s **call sites** move from
    `promote` (deleted) to Phase 14's `enrichment.apply_results` — no
    change to `render_vendor_skill`/`render_cursor_mdc`'s own logic
    (Phase 14 already designed `apply_results` to call them with a
    minimal `VendorDigest`).
- Tests: `tests/test_cli.py` gains coverage for the new `--yes`/`--budget`
  bootstrap flow, `promote`'s removal (asserting the command no longer
  exists), and the new `query` command group. `tests/test_index.py`,
  `tests/test_skill.py` updated for the Depth→Enriched column swap.

**Explicitly deferred / out of scope:**
- Deleting `Depth`/`vendor.toml`'s `depth` field — Phase 16 (this phase
  only stops *reading* it for display purposes in `index.py`/`skill.py`;
  `core.py`/`config.py`/`discovery.py` are untouched here).
- `/discovery`, `undo` — Phases 17-18.
- Any change to `chat.py`'s framing/docs — Phase 19 (`chat.py`'s one
  `promote`-referencing hint string was already reworded during Phase 9's
  rename pass, ahead of `promote`'s actual removal here — confirm it
  still reads sensibly now that `promote` is genuinely gone).

## Design decisions

**Why bare bootstrap gains flags it never had before**: `decisions/0033`
requires Phase B to auto-trigger right after Phase A, but Phase B is a
real cost/consent point — it needs the same disclose-and-confirm
mechanics `promote` used to provide, and `promote` no longer exists to
provide them. Adding `--yes`/`--budget` to the top-level callback (rather
than, say, only to `sync`) is necessary because *bare* `codecompass` is
itself a Phase A+B trigger point per this rework's spec, not just `sync`.

**`check --strict`'s scope is a deliberate non-change**, confirmed twice
during this rework's planning (once in the original interview, once
implicitly by every phase plan in this arc treating coverage-gap
reporting as report-only) — worth restating here since this is the phase
that actually implements it, not just plans it.

## Files

- `src/codecompass/cli.py` — `promote` removed; `main` callback gains
  `--yes`/`--budget` + Phase B trigger; `sync`'s whole-project branch
  gains the same; new `query` command group; `check` gains coverage-gap
  sections.
- `src/codecompass/graph.py` — add `has_enrichment(conn, vendor_name) ->
  bool` query function (small addition to Phase 10's existing set).
- `src/codecompass/index.py`, `src/codecompass/skill.py` — Depth→Enriched
  swaps as above.
- `tests/test_cli.py`, `tests/test_index.py`, `tests/test_skill.py`
  updated; `tests/test_graph.py` extended for `has_enrichment`.
- `docs/cli-reference.md` — `promote` removed, `query` documented, bare
  bootstrap's new `--yes`/`--budget` documented. `architecture/overview.md`
  — "Retrofitting to existing projects" and "Cost model" sections
  rewritten around the new Phase A/B flow; `decisions/0033` cross-linked.
  `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md`.

## Verification

- `pytest` — full suite passes.
- `ruff check .` — clean.
- Manual, against a **scratch** project (not this repo — this phase's
  first real end-to-end Phase B trigger will cost real API money the
  first time it's exercised, per `decisions/0016`'s "a human must run
  this against the real API at least once" precedent): run bare
  `codecompass` against a small real project with 2-3 dependencies
  actually imported in its source; confirm the cost-disclosure prompt
  appears, confirm with `y`, confirm `CLAUDE.md`'s Description sections
  populate, per-vendor Skills appear under `.claude/skills/codecompass-
  <vendor>/`, and `codecompass query vendor <name>` returns a populated
  profile. Re-run bare `codecompass` immediately after — confirm zero
  new API calls (the cache-hit path from Phase 14).
- Confirm `codecompass --help` no longer lists `promote`, and `codecompass
  promote anything` fails with Typer's standard "no such command" error.
- Confirm `check --strict`'s exit code is unaffected by a project with
  real coverage gaps (an unused vendor present) — still governed by
  version-drift severity alone.
