# Phase 5: AI-Gated Gap Analysis

## Scope

**Covered:**
- `src/depcompass/gap_analysis.py` — `GapAnalysisError`, `GapAnalysis`
  dataclass (`technical`, `conversational_overview`, `action_pointer_file`,
  `action_pointer_note`), a monkeypatch-friendly `_call_anthropic(system_prompt,
  user_prompt) -> dict` seam using forced tool-use for structured
  dual-audience output, `generate_gap_analysis(config, api_surface,
  project_root) -> GapAnalysis`, `estimate_cost(vendor_count) -> float`,
  `check_budget(configs, budget) -> None`.
- `src/depcompass/core.py` — `VendorDigest` gains `conversational_overview:
  str | None` and `gap_analysis_error: str | None`. The existing
  `gap_analysis: str | None` field (Phase 1) is populated for real.
- `src/depcompass/sync.py` — `sync_vendor` calls gap analysis for `depth =
  full` + `context_path` vendors, catching failures locally so the
  vendor's deterministic output still gets written; writes
  `vendor/<name>/OVERVIEW.md` when a conversational overview exists;
  `sync_all` gains a `budget` keyword and runs `check_budget` before any
  vendor is touched.
- `src/depcompass/claude_md.py` — Gap analysis section (technical text +
  action pointer, or an explicit "unavailable" note on failure) re-added
  to the per-vendor template.
- `src/depcompass/filetree.py` — `render_filetree_markdown`/
  `render_filetree_json` gain an optional `action_pointer` parameter,
  closing the FILETREE-cross-linking loop Phase 3 deferred.
- `src/depcompass/cli.py` — `sync --budget <amount>`; exits non-zero if
  any vendor's gap analysis failed this run.
- New ADR: the no-live-API-call testing strategy (number confirmed
  against actual repo state at implementation time — expected next after
  `0015`).
- Tests: `tests/test_gap_analysis.py`, plus updates to `tests/test_sync.py`,
  `tests/test_claude_md.py`, `tests/test_filetree.py`, `tests/test_cli.py`.
  `_call_anthropic` is monkeypatched everywhere — no test makes a real
  Anthropic API call.
- Same-commit doc updates: `architecture/overview.md` (Gap analysis,
  Per-vendor CLAUDE.md structure, Tree generation, Cost model, Known
  footguns sections), `docs/cli-reference.md`, `docs/config-schema.md`,
  `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md`.

**Explicitly deferred:**
- Anything Phase 8's REPL rollup does with `OVERVIEW.md`'s content —
  Phase 5 only produces and persists it; consuming it is Phase 8's job
  (`decisions/0012`).
- Real, live-queried Anthropic pricing for `--budget`'s cost estimate —
  a fixed, documented, rough placeholder constant is used instead.
- Caching/diffing gap analysis across `sync` runs — every run for a
  `depth = full` + `context_path` vendor re-purchases a fresh AI call, by
  design, consistent with every other `sync` output being fully
  regenerated each run (Phase 4).
- A partial-run/skip `--budget` mode — exceeding the budget aborts the
  entire run before any API calls, not a partial best-effort run.

## Design decisions

- **Model reference pinned to the dated snapshot
  `claude-haiku-4-5-20251001`**, not the rolling `claude-haiku-4-5` alias
  `decisions/0003` names literally — avoids gap-analysis output silently
  changing character if Anthropic updates what the alias resolves to,
  consistent with depcompass's own reason for existing. A plan-level
  refinement of `decisions/0003`'s model-*tier* choice (unchanged), not a
  new ADR.
- **`--budget` overrun aborts the whole run before any API calls** —
  prints the estimate vs. budget, exits non-zero, writes nothing this
  invocation (not even other vendors' free deterministic output). Simple
  and predictable over a partial-run/skip model.
- **A single vendor's gap-analysis failure doesn't abort the batch** — the
  failure is caught inside that vendor's own sync step; its deterministic
  output still gets written (with an explicit "unavailable" note in
  `CLAUDE.md`, not a silent omission); remaining vendors still run;
  `sync` exits non-zero at the end if anything failed.
- **FILETREE cross-linking is implemented now**, closing the loop Phase 3
  explicitly deferred — Phase 5 is the natural owner since it produces
  the action-pointer data that feature needs, and no later roadmap phase
  claims it. The `action_pointer` parameter defaults to `None`, so
  existing Phase 3/4 callers and tests are unaffected.
- **One API call, forced tool-use, structured dual-audience output** —
  more reliable than one prompt plus regex-splitting markdown sections
  for the technical/conversational split, still "same call, same cost"
  per `decisions/0012`.
- **The conversational overview persists to a new `vendor/<name>/OVERVIEW.md`**,
  sibling to the existing per-vendor files, written only on success for a
  `depth = full` vendor. Not part of `CLAUDE.md`, which stays agent-facing
  technical content only (`decisions/0012`).
- **No live Anthropic API calls in the automated test suite, ever** —
  unlike Phase 2's free npm/pytest live smoke tests, a real call here
  costs real money and needs a live key. `_call_anthropic` is
  monkeypatched in every test. Recorded as a new ADR since this is a
  distinct, non-obvious, cost-driven tradeoff (not just
  toolchain-availability-driven like `decisions/0014`).
- **`context_path` content is truncated to an arbitrary, documented,
  tunable character cap** before entering the prompt — same treatment as
  every other cap already in this project (Phase 2's file caps, Phase 3's
  symbol-index cap).
- **`--budget`'s cost estimate is a fixed, clearly-labeled rough
  placeholder constant**, not live-queried pricing — flagged in code and
  docs as approximate, not a guarantee of actual billed cost.

## Files

- `src/depcompass/gap_analysis.py` — `GapAnalysisError`; `GapAnalysis`
  dataclass; `_call_anthropic` seam (builds `anthropic.Anthropic()`,
  reads `ANTHROPIC_API_KEY` from the environment automatically, forced
  tool-use call, wraps SDK exceptions); `generate_gap_analysis`;
  `estimate_cost`; `check_budget`.
- `src/depcompass/core.py` — `VendorDigest.conversational_overview`,
  `VendorDigest.gap_analysis_error`.
- `src/depcompass/sync.py` — gap-analysis call site in `sync_vendor`
  (after `api_surface`, before tree rendering, so the action pointer is
  available for `filetree` calls); `OVERVIEW.md` writing; `sync_all`'s
  `budget` keyword and pre-flight `check_budget` call.
- `src/depcompass/claude_md.py` — Gap analysis section rendering
  (technical + action pointer, or the explicit unavailable note).
- `src/depcompass/filetree.py` — `action_pointer: tuple[str, str] | None
  = None` parameter on `render_filetree_markdown`/`render_filetree_json`.
- `src/depcompass/cli.py` — `sync --budget`; non-zero exit when any
  digest has `gap_analysis_error` set.
- `tests/test_gap_analysis.py` — new.
- `tests/test_sync.py`, `tests/test_claude_md.py`, `tests/test_filetree.py`,
  `tests/test_cli.py` — extended.
- New ADR (number to be confirmed against actual repo state at
  implementation time).
- `architecture/overview.md`, `docs/cli-reference.md`,
  `docs/config-schema.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md`,
  `CHANGELOG.md` — updated in place.

## Verification

- `pytest` — full suite passes, count increases from Phase 4's total; no
  test makes a real Anthropic API call.
- `ruff check .` — clean, including the new module.
- A hand-built `depth = full` + `context_path` vendor, `_call_anthropic`
  monkeypatched to a fixed response: `CLAUDE.md` contains both the
  technical section and the action pointer line, `OVERVIEW.md` is written
  with the conversational overview, and `FILETREE.md` shows the `←
  ACTION TARGET` marker on the matching file's line.
- A monkeypatched `_call_anthropic` that raises: the vendor still gets
  `FILETREE.md`/`DEPTREE.md`/`CLAUDE.md` (with the explicit "unavailable"
  note, not a silent gap), `sync_all` continues to the next vendor, and
  the CLI exits non-zero overall.
- `sync --budget <too low>` against a project with several `full` +
  `context_path` vendors: nothing is written and the command exits 1
  with a clear estimate-vs-budget message.
- The new ADR has Status/Context/Decision/Alternatives
  considered/Consequences sections matching the existing template.
- `architecture/overview.md`'s Known footguns section lists every new
  Phase 5 limitation described above.

## Status

planned — this plan file has been written and reviewed; no gap-analysis
code has been implemented yet.
