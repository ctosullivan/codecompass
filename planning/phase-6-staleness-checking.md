# Phase 6: Staleness Checking

## Scope

**Covered:**
- `src/depcompass/claude_md.py` — new `read_installed_version(claude_md_path:
  Path) -> str | None` (the `**Installed version:**` regex + file read,
  moved here from `index.py` since `claude_md.py` already owns the file
  format it targets).
- `src/depcompass/index.py` — `load_routing_rows` updated to call
  `claude_md.read_installed_version` instead of its own private regex —
  de-duplication, no behavior change.
- `src/depcompass/core.py` — `VendorDigest` loses `is_stale`/`_stale` (see
  Design decisions).
- `src/depcompass/staleness.py` (new) — `Severity` enum, `_parse_version`,
  `classify`, `VendorStaleness` dataclass, `check_vendor`, `check_all`.
- `src/depcompass/cli.py` — `check [--strict] [--fix]` real implementation,
  replacing the stub.
- Tests: `tests/test_staleness.py` (new), plus updates to
  `tests/test_claude_md.py`, `tests/test_index.py` (confirms the refactor
  is non-breaking), `tests/test_cli.py`, and wherever `VendorDigest.is_stale`
  was previously exercised.
- Same-commit doc updates: `architecture/overview.md` (Core data model,
  Staleness checking, Known footguns sections), `docs/cli-reference.md`,
  `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md`.

**Explicitly deferred:**
- Real PEP 440 / full semver correctness (epochs, complex pre-release
  ordering) — the custom parser only extracts a leading `major.minor.patch`
  integer triple.
- A `--budget` flag on `check --fix` — not part of the documented CLI
  surface for `check`; `--fix` has no spend cap of its own in this phase.
- Fixing `sync_vendor`'s existing uncaught-`AdapterError` behavior — out of
  scope for this phase; `check`'s own read path and `--fix`'s CLI loop add
  their own isolation without touching `sync_vendor`.
- Any live validation of the Cargo adapter (still blocked on no local Rust
  toolchain, unrelated to this phase).

## Design decisions

- **Small custom version parser, no new dependency.** Regex-extracts a
  leading `major.minor.patch` integer triple (tolerating a `v` prefix and
  any trailing pre-release/build suffix) — consistent with this project's
  established dependency-avoidance (`decisions/0009`, `decisions/0011`).
  Two version strings whose numeric triples match classify as `NONE`
  severity even if the raw strings differ, since `decisions/0005` is about
  *semantic* delta, not string equality. Either string failing to parse a
  leading triple yields `UNKNOWN` severity rather than crashing or
  guessing — treated as a hard-fail case under `--strict` (see below),
  since an unclassifiable version is a "can't verify" state, not a "safe
  to ignore" one.
- **Bare `check` is report-only, always exits 0.** Prints the
  severity-classified table for a human running it locally. `--strict` is
  the only mode that turns MAJOR-or-worse (or an adapter read failure, or
  `UNKNOWN` severity) into a non-zero exit — the deliberate CI gate,
  matching `decisions/0005`'s exact wording ("`check --strict` exits
  non-zero") and `docs/cli-reference.md`'s existing "pure gate ... intended
  for CI" framing. `--strict` and `--fix` are mutually exclusive — gating
  and regenerating are different jobs; passing both is a clear config
  error (exit 1, nothing written).
- **Transitive drift is a full diff, not a root-only comparison.** `check`
  reads each vendor's persisted `deptree.json`, calls the adapter's
  `dependency_tree()` fresh (a local subprocess/metadata read — no AI, no
  network beyond what the adapter already does at `sync` time), and
  flattens both into `name -> set[version]` maps. Reuses
  `deptree.render_deptree_json`'s already-deduplicated shape for the live
  side, so only one flattening function is needed against both persisted
  and live JSON. If the *root* differs, that's the ordinary severity
  classification. If the root matches but any other node's flattened map
  differs, that's reported as a separate `transitive_drift: bool` flag —
  informational only, never affects exit code (even under `--strict`),
  consistent with `decisions/0005` treating transitive-only drift as lower
  risk than a vendor's own version bump.
- **`--fix` reuses `sync_vendor` as-is, unmodified.** Full regeneration per
  stale vendor, including a fresh (re-purchased) gap analysis for
  `depth = full` vendors — no new code path inside `sync.py`. The cost
  implication is the same one `sync`'s own docs already state. `check`'s
  own CLI loop (not `sync_vendor` itself) wraps each `--fix` regeneration
  in `try/except AdapterError`, isolating one vendor's failure from the
  rest of the batch — mirroring the isolation pattern `sync_vendor`
  already uses internally for `GapAnalysisError`, applied one layer up
  since `sync_vendor` isn't being touched.
- **`VendorDigest.is_stale` is removed** (`is_stale` property, `_stale`
  field, and the docstring paragraph promising Phase 6 would populate it).
  `index.py` (Phase 4) already established that routing/staleness-style
  commands read persisted per-vendor `CLAUDE.md` files rather than
  building full `VendorDigest` objects, specifically to stay cheap and
  side-effect-free. `check` has the identical constraint — it must not
  trigger `sync`/gap-analysis cost just to report staleness — so it never
  constructs a `VendorDigest` either, leaving the Phase-1 `is_stale` stub
  with no code path that could ever populate it. Rather than leave a
  documented-but-permanently-dead stub (contradicting `core.py`'s own
  docstring promise), it's deleted; `staleness.py` introduces its own
  `VendorStaleness` dataclass instead, mirroring `index.py`'s
  `RoutingRow`. Not ADR-worthy — this doesn't reverse a previously-recorded
  decision, it retires a speculative field that turned out not to fit once
  Phase 4 committed to the persisted-file-read pattern.
- **`read_installed_version` is promoted out of `index.py` into
  `claude_md.py`.** `claude_md.py` already owns the per-vendor `CLAUDE.md`
  format (`render_vendor_claude_md`), including the load-bearing
  `**Installed version:**` line, so it should own reading that line back
  too. `index.py`'s `load_routing_rows` is updated to call the shared
  helper instead of keeping its own private regex — de-duplication only,
  `index`'s behavior is unchanged.

## Files

- `src/depcompass/claude_md.py` — `_INSTALLED_VERSION_RE` (moved from
  `index.py`), `read_installed_version`.
- `src/depcompass/index.py` — `load_routing_rows` calls the shared helper;
  its own copy of the regex is deleted.
- `src/depcompass/core.py` — `VendorDigest.is_stale`/`_stale` removed;
  docstring updated to point at `depcompass.staleness.VendorStaleness` /
  `depcompass check` instead.
- `src/depcompass/staleness.py` (new) — `Severity` (`StrEnum`: `NONE`,
  `PATCH`, `MINOR`, `MAJOR`, `UNKNOWN`); `_parse_version(version: str) ->
  tuple[int, int, int] | None`; `classify(recorded: str, live: str) ->
  Severity`; `VendorStaleness` (`config`, `recorded_version: str | None`,
  `live_version: str | None`, `severity: Severity`, `transitive_drift:
  bool`, `error: str | None`); `check_vendor(config, project_root) ->
  VendorStaleness`; `check_all(configs, project_root) ->
  list[VendorStaleness]`.
- `src/depcompass/cli.py` — `check(strict: bool = False, fix: bool =
  False)`: errors on `--strict` + `--fix` together; renders a Rich `Table`
  (Vendor, Recorded, Live, Severity, Notes) styled per severity; bare mode
  always exits 0; `--strict` exits 1 on any `MAJOR`/`UNKNOWN`/`.error`
  vendor; `--fix` regenerates every vendor where `recorded_version !=
  live_version` (including never-synced) or `transitive_drift` is set, via
  `sync_vendor`, isolating `AdapterError` per vendor, exiting 1 if any
  regenerated vendor failed (adapter error or `gap_analysis_error`).
- `tests/test_staleness.py` — new.
- `tests/test_claude_md.py`, `tests/test_index.py`, `tests/test_cli.py` —
  extended/updated.
- `architecture/overview.md`, `docs/cli-reference.md`,
  `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md` — updated in
  place.

## Verification

- `pytest` — full suite passes, count increases from Phase 5's 136; no
  test makes a real Anthropic API call or a real subprocess call (adapter
  seams stay monkeypatched, same convention as Phases 2-5).
- `ruff check .` — clean, including the new module.
- A hand-built vendor with a patch-only live delta: bare `check` shows it
  as `NONE`/unflagged; `--strict` still exits 0.
- A hand-built vendor with a minor delta: shown as a warning row; both
  bare `check` and `check --strict` exit 0 (minor never hard-fails per
  `decisions/0005`).
- A hand-built vendor with a major delta: shown as a failure row; bare
  `check` exits 0, `check --strict` exits 1.
- A hand-built vendor whose root version is unchanged but whose persisted
  `deptree.json` and live tree disagree on a child node's version:
  `transitive_drift` is `True`, and this never flips `--strict`'s exit
  code on its own.
- `check --strict --fix` together errors clearly, nothing written.
- `check --fix` against a mix of a stale vendor and a fresh one:
  regenerates only the stale one's `vendor/<name>/` contents in place,
  leaves the fresh one untouched, exits 0.
- `check --fix` with one vendor's adapter monkeypatched to raise
  `AdapterError`: the other vendors still get fixed, the broken one is
  reported, exit code is non-zero.
- `architecture/overview.md`'s Known footguns section lists every new
  Phase 6 limitation: the version parser's known correctness gaps
  (no real PEP 440/epoch/prerelease-ordering support), the
  bare-`check`-always-exits-0 behavior, and the `is_stale` removal.

## Status

planned — implementation not yet started.
