# Phase 14: Batched enrichment (Phase B)

## Scope

**Covered:**
- `src/codecompass/enrichment.py` (new) — replaces
  `grounded_description.py` conceptually (that module is retired in this
  phase, its reusable pieces ported forward — see Files). **Library
  only, like Phase 10's `graph.py` — not called from `cli.py`/`sync.py`
  yet; that wiring is Phase 15.** Tested standalone with monkeypatched
  `_call_anthropic`, per `decisions/0016`.
  - `select_candidates(conn) -> list[EnrichmentCandidate]` — calls
    `graph.enrichment_candidates(conn)` (built in Phase 10: every vendor
    with ≥1 `uses_edges` row, its currently-used symbol names, and any
    existing `vendor_enrichment.symbol_set_hash`), computes each
    candidate's *current* hash
    (`_compute_symbol_set_hash(vendor_name, sorted(used_symbol_names),
    installed_version)`, sha256-based) and filters out any candidate
    whose current hash already matches its stored one — the "don't
    re-pay for an unchanged, already-enriched vendor" behavior
    `decisions/0032` describes. A second, cheaper check happens before
    even reaching the database: `select_candidates` is also handed each
    candidate's persisted `CLAUDE.md` enrichment-hash line (via
    `claude_md.read_enrichment_hash`, new — see below) and skips a
    candidate whose file-level hash already matches too, so a fresh
    clone with no `context-graph.db` at all (gitignored, per
    `decisions/0032`) still doesn't immediately re-enrich everything on
    its first `sync` — belt-and-suspenders with the DB check, and the
    one that actually survives a fresh checkout.
  - `EnrichmentCandidate(vendor: VendorConfig, used_symbol_names:
    list[str], material: str)` — `material` gathered via
    `_gather_material(repo_root, config)`, ported near-verbatim from
    `grounded_description.py` (README + docs folder + one entry-point
    file, same `_RAW_TEXT_CHAR_CAP`/`_DOCS_FILE_CAP`/`_find_entry_point`
    logic) but now reading from `vendor/<name>/src/` unconditionally
    (Phase 13 made this exist for every vendor, not just formerly-`FULL`
    ones) rather than requiring a `depth = full`-gated clone.
  - `plan_batches(candidates: list[EnrichmentCandidate], *,
    batch_char_budget: int = 150_000) -> list[list[EnrichmentCandidate]]`
    — greedily groups candidates into as few batches as fit under
    `batch_char_budget` total material characters per batch (starting
    conservative — empirically tune after this phase's manual
    verification step, not a one-time constant, same treatment this
    project already gives every other cap: `.d.ts`/`.pyi` file caps,
    `_RAW_TEXT_CHAR_CAP`, `_SYMBOL_INDEX_CAP`).
  - `_TOOL_SCHEMA` (batched form) — accepts `{"vendors": [{"name": str,
    "used_symbols": [str], "material": str}, ...]}`, forced tool-use,
    returns `{"results": [{"vendor": str, "technical_description": str,
    "conversational_overview": str, "symbol_purposes": [{"symbol": str,
    "purpose": str}], "action_pointer_file": str | null,
    "action_pointer_note": str | null}, ...]}` — one call describes
    several vendors, each scoped to only the symbols proven used (not
    the vendor's full API surface), satisfying "a small number of
    batched calls, not one per vendor."
  - `run_enrichment_batches(candidates) -> list[EnrichmentResult]` —
    calls `_call_anthropic` once per batch from `plan_batches`, maps each
    batch's response back to its vendors. Same forced-tool-use call
    pattern and per-module monkeypatch test seam as
    `grounded_description._call_anthropic` (ported, not reinvented).
  - `EnrichmentResult(vendor: str, technical_description: str,
    conversational_overview: str, symbol_purposes: dict[str, str],
    action_pointer_file: str | None, action_pointer_note: str | None,
    symbol_set_hash: str)`.
  - `apply_results(conn, project_root, results: list[EnrichmentResult]) ->
    None` — for each result: `graph.record_enrichment(...)` +
    `graph.record_symbol_enrichment(...)` per symbol (Phase 10's writers,
    unchanged); `claude_md.update_description_section(...)` (new, see
    below) to rewrite just that vendor's `CLAUDE.md` Description section
    and enrichment-hash metadata line **in place**, without re-running
    `sync_vendor`'s full pipeline; then `skill.write_vendor_skill`/
    `write_cursor_mdc` using a **minimal `VendorDigest`** populated only
    with the fields those two render functions actually read (`config`,
    `installed_version`, `conversational_overview`,
    `technical_description`, `action_pointer_file`,
    `action_pointer_note`) — confirmed by reading both functions' bodies
    that neither touches `api_surface`/`file_tree`/`dep_tree`/
    `side_effects`, so leaving those fields at their dataclass defaults
    is safe, not a partial/buggy digest.
  - `estimate_cost(batch_count: int) -> float` / `check_budget(candidates,
    budget) -> None` — reworked from `grounded_description.py`'s
    per-vendor formula: cost now scales with `len(plan_batches(...))`,
    not `len(candidates)` 1:1, reflecting the real batched call shape.
    Same abort-before-any-spend contract.
- `src/codecompass/claude_md.py` — two additions:
  - `update_description_section(claude_md_path: Path, *,
    technical_description: str | None, action_pointer_file: str | None,
    action_pointer_note: str | None, symbol_set_hash: str) -> None` —
    reads the existing file, replaces the bounded "## Description"
    section (between the fixed "## Public API surface" and "## Known
    gotchas" headings — section order is fixed by
    `render_vendor_claude_md`'s docstring) via the same regex-bounded
    substitution idiom `index.py`'s marker-block replacement already
    established, and updates (or inserts) a
    `**Enrichment symbol-set hash:** <hash>` line in the Metadata
    section alongside the existing `**Installed version:**` line. Avoids
    reconstructing a full `VendorDigest` just to re-render one section.
  - `read_enrichment_hash(claude_md_path: Path) -> str | None` — regex
    read-back of that new metadata line, mirroring
    `read_installed_version`'s existing pattern exactly.
- `grounded_description.py` **retired**: `git mv` to
  `enrichment.py` is not literal (the call shape changes materially —
  one-vendor-per-call becomes batched), but `_gather_material`,
  `_find_entry_point`, `_read_text`, `_first_existing`, and the
  `_call_anthropic` forced-tool-use pattern are ported into
  `enrichment.py` near-verbatim. `sync.py`'s import of
  `grounded_description` (`GroundedDescriptionError`, `check_budget`,
  `generate_grounded_description`) stays **unchanged in this phase** —
  `sync_vendor` still calls the old module for `depth = full` vendors,
  since `Depth`/`promote` aren't retired until Phase 15/16. Both modules
  coexist through this phase; `grounded_description.py` is only actually
  deleted once Phase 15 rewires `cli.py`/`sync.py` off it entirely.
- Tests: `tests/test_enrichment.py` (new) — candidate selection
  (including the two-tier hash-skip logic), batch planning against a
  character-budget boundary, the batched tool-schema call/response
  mapping (monkeypatched), and `apply_results`'s `CLAUDE.md`
  section-replacement + minimal-digest Skill generation against fixture
  state.

**Explicitly deferred / out of scope:**
- Actually calling any of this from `cli.py`/`sync.py` — Phase 15.
- Deleting `grounded_description.py` — Phase 15 (once nothing calls it).
- Tuning `batch_char_budget` against real-world output quality — flagged
  for empirical adjustment after Phase 15's end-to-end wiring makes a
  real multi-vendor batched call actually reachable to test manually.

## Design decisions

**In-place `CLAUDE.md` section replacement, not full `VendorDigest`
reconstruction.** Re-running `sync_vendor`'s entire pipeline just to fold
in a new description would re-do adapter calls and tree generation for no
reason — genuinely wasteful, and `VendorDigest` was never designed to be
persisted/reloaded (only its *rendered* markdown output is persisted).
Reusing `index.py`'s existing "regenerate just the bounded part, leave
the rest of the file alone" idiom for a *different* bounded section is
more consistent with this project's own precedent than inventing a new
persistence mechanism.

**The enrichment cache-key mechanism (`decisions/0032`) is fully
concrete here**: `vendor_enrichment.symbol_set_hash` (DB) and
`CLAUDE.md`'s new metadata line (committed file) are two independent
checks against the same underlying question — "has this vendor's actual
used-symbol set changed since it was last enriched" — deliberately
redundant so the *file-level* check alone is sufficient to skip
re-enrichment even when `context-graph.db` doesn't exist at all (a fresh
clone, since the DB is gitignored).

## Files

- `src/codecompass/enrichment.py` (new).
- `src/codecompass/claude_md.py` — `update_description_section`,
  `read_enrichment_hash`.
- `tests/test_enrichment.py` (new); `tests/test_claude_md.py` extended.
- `architecture/overview.md` — new "Batched enrichment" subsection under
  "Context graph" (or alongside "Grounded description," noting the two
  modules' coexistence through this phase and `grounded_description.py`'s
  pending retirement in Phase 15); `planning/ROADMAP.md`,
  `planning/CONTEXT.md`, `CHANGELOG.md`.

## Verification

- `pytest` — full suite passes; `decisions/0016` upheld — no test in
  `tests/test_enrichment.py` makes a real Anthropic API call.
- `ruff check .` — clean.
- Manual, standalone (this phase's code isn't reachable via the CLI
  yet): write a small script (or a `pytest -s` manual run) constructing
  a fixture `context-graph.db` with 2-3 usage-proven vendors, call
  `select_candidates`/`plan_batches`/`apply_results` end to end against
  monkeypatched `_call_anthropic`, and confirm the resulting `CLAUDE.md`
  files' Description sections and hash lines update correctly, and that
  re-running `select_candidates` immediately after returns an empty
  candidate list (the cache-hit path).
