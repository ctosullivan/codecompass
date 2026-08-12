# Phase 9c: Context graph — doc & Skill mapping

## Scope

**Covered:**
- `src/depcompass/context_graph.py` — adds `DocArtifactNode(id: str,
  vendor: str | None, kind: str, path: str)`. `kind` distinguishes
  `claude_md` / `overview` / `vendor_skill` / `tool_skill` /
  `cursor_mdc`. `vendor` is `None` for the shared tool-level Skill
  (`.claude/skills/depcompass/SKILL.md`, `decisions/0020`), which isn't
  scoped to one vendor. One `DocArtifactNode` per vendor's `CLAUDE.md`
  (always) and `OVERVIEW.md` (when present, i.e. `depth = full` with a
  successful grounded description), plus the per-vendor `SKILL.md` for
  `depth = full` vendors and the shared tool-level `SKILL.md` for
  `depth = surface` vendors — mirroring `decisions/0020`'s existing
  split exactly, not inventing a new one.
- New `src/depcompass/doc_mapping.py` — builders for the three edge
  types this phase adds, kept in a separate module from `usage.py`
  since these read already-generated artifacts rather than walking
  project or vendor source:
  - `build_documents_edges(...) -> list[DocumentsEdge]` — for each
    `SymbolNode`, a plain-text presence check of that symbol's name
    against the body of its vendor's `CLAUDE.md`, and against
    `OVERVIEW.md`'s body when present (both files, per the plan's
    resolution of open question 1 — excluding `OVERVIEW.md` would
    understate coverage exactly for the vendors that invested most in
    documentation). Explicitly a coverage heuristic, not a quality
    judgment — stated in the module's docstring, matching how
    `DOCUMENTS` is described throughout this plan.
  - `build_routes_via_edges(...) -> list[RoutesViaEdge]` — derived
    mechanically from which Skill file already exists at which path for
    a given vendor (reads `depcompass.skill`'s output paths as data; does
    **not** modify `skill.py` or how Skills are generated — a one-way
    observation, same posture as the `depends_on` builder below).
    `depth = full` vendors route via their own `.claude/skills/
    depcompass-<vendor>/SKILL.md`; `depth = surface` vendors route via
    the shared `.claude/skills/depcompass/SKILL.md`.
  - `build_depends_on_edges(...) -> list[DependsOnEdge]` — folded in from
    each vendor's already-built `vendor/<name>/deptree.json` (parent→
    child, flattened to `Vendor → Vendor`; no new dependency-tree
    construction, pure transformation of existing data already written
    by `sync_vendor`).
- `src/depcompass/cli.py` — extends 9a's "Unused vendors" `check` report
  section with two more lines in the same report-only, non-`--strict`-
  affecting style: "Documented but never used" (a `DocArtifact` mentions
  a symbol with no corresponding `uses` edge anywhere) and "Used but
  undocumented" (a `Symbol` has a `uses` edge but no `documents` edge
  from any of its vendor's doc artifacts).
- Tests: `tests/test_doc_mapping.py` (new), fixture-based, no AI calls
  (this phase, like 9a/9b, only reads already-generated deterministic
  artifacts — `decisions/0016`'s concern doesn't apply).

**Explicitly deferred:**
- `DocChunk`/`EXPLAINS` (chunk-scoped retrieval, requiring an LLM call)
  — Phase 9d, `decisions/0027`.
- Any judgment of documentation *quality* (as opposed to bare presence)
  — Phase 9d's `DOCUMENTS` quality delta, `decisions/0026`.
- Usage-cluster classification / Skill suggestion — Phase 9e,
  `decisions/0028`.

## Design decisions

- `routes_via` operationalizes `decisions/0013` point 6 ("the REPL's
  Tier 1 routing should read from the same underlying digest data
  structure Skill-description generation reads from") as real,
  queryable structured data for the first time — it does not change how
  Skills are generated (that's Phase 7's `skill.py`, already shipped and
  unmodified here); it records, as graph data, which Skill file already
  backs which vendor.
- `depends_on` is pure transformation of `deptree.json`'s existing
  output — this phase adds no new dependency-tree construction logic
  anywhere.
- `documents`'s both-files scope (open question 1) is a deliberate
  choice to avoid understating coverage for the vendors that have
  actually invested in an `OVERVIEW.md`.

## Files

- `src/depcompass/context_graph.py` — extended (`DocArtifactNode`,
  `documents`/`routes_via`/`depends_on` edge types).
- `src/depcompass/doc_mapping.py` (new) — see Scope above.
- `src/depcompass/cli.py` — `check`'s two additional report lines.
- `tests/test_doc_mapping.py` (new).
- Same-commit docs: `architecture/overview.md`'s "Context graph" section
  (extended), `docs/cli-reference.md` (`check`'s two additional lines),
  `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md`.

## Verification

- `pytest` — full suite passes, including the new test file.
- `ruff check .` — clean.
- Manual, against this repository's own real vendors (already tracked
  in its own `vendor.toml`):
  - `depcompass sync` (bare) — confirm `depends_on` edges for `rich`
    exactly match `vendor/rich/deptree.json`'s existing
    `markdown-it-py`/`Pygments`/`mdurl` chain.
  - Confirm `routes_via` edges: `rich → .claude/skills/depcompass-rich/
    SKILL.md` (its own per-vendor Skill, `depth = full`), and a
    `depth = surface` vendor (e.g. `typer`) → the shared
    `.claude/skills/depcompass/SKILL.md`.
  - `depcompass check` (bare) — confirm the two new coverage-gap lines
    appear when applicable and the command still exits 0.
