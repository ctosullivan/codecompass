# Phase 21: Spec-doc detection & relationship graph

## Scope

Part 1 of the new three-way relationship feature requested alongside the
path-to-v1.0 roadmap (see `planning/v1.0-initial-release-roadmap.md`).
Mechanical only — no AI call, no cost, same posture as `usage.py`/
`doc_mapping.py`/`skill_scan.py`. Part 2 (AI enrichment of the edges this
phase detects) is Phase 22, deliberately separate: enrichment should only
ever run over relationships mechanical detection has already proven exist,
mirroring `decisions/0031`/`0033`'s "usage-proven, not manually toggled"
gating, generalized from vendor enrichment to relationship enrichment.

**Covered:**

- New `doc_artifacts.kind = 'spec_doc'`, `origin = 'project'` — a project's
  own human-authored documentation, distinct from `codecompass_vendor`
  (generated dependency docs), `codecompass_tool`/`codecompass_vendor`
  (generated Skills), and `third_party` (hand-authored Skills). Both CHECK
  constraints on `doc_artifacts` widen; needs the same recreate-the-table
  migration pattern Phase 17 used for `kind` (`_migrate_doc_artifacts_kind_
  constraint`), extended to also widen `origin`, with `_SCHEMA_VERSION`
  bumped "2" → "3". Safe for the same reason Phase 17's migration was safe:
  `doc_artifacts` and everything that cascades from it is fully rewritten
  by `rebuild_deterministic` on every whole-project sync, so recreating the
  table loses nothing `sync` doesn't already regenerate.
- New module `spec_docs.py`: `scan_spec_docs(project_root: Path) ->
  list[DocArtifactRow]`. Default glob set (no `vendor.toml` configurability
  yet — see Design decisions): `README.md`, `ARCHITECTURE.md`,
  `REQUIREMENTS.md`, `PRD.md`, `docs/**/*.md`, `architecture/**/*.md`,
  `decisions/**/*.md`, `spec/**/*.md`, `specs/**/*.md`, `rfcs/**/*.md`,
  `*.spec.md`. Explicitly excluded: `CHANGELOG.md` (a log, not a spec),
  `CONTRIBUTING.md` (process, not product), `LICENSE*`, root `CLAUDE.md`
  itself (governance, not spec — also already a special-cased file
  elsewhere in this codebase), and anything under the same prune-dir set
  `usage.py`'s `_PROJECT_PRUNE_DIR_NAMES` already excludes (`vendor/`,
  `.claude/`, `.cursor/`, `node_modules/`, `.git/`, `.venv/`, `dist/`,
  `build/`, etc.) — imported from `usage.py`, not duplicated, if that name
  is already a public/importable module attribute; otherwise promote it to
  a small shared constant at implementation time rather than copy-pasting
  the list a third place.
- `graph.py`: new table `doc_relations_edges` — **mechanical only**, wiped
  and reinserted on every `rebuild_deterministic` call exactly like
  `documents_edges`/`skill_mentions_edges`/`depends_on_edges`, no
  cross-rebuild identity to preserve (that concern is Phase 22's, for the
  *enrichment* of these edges, not the edges themselves):
  ```sql
  CREATE TABLE IF NOT EXISTS doc_relations_edges (
    id                     INTEGER PRIMARY KEY,
    source_doc_artifact_id INTEGER NOT NULL REFERENCES doc_artifacts(id) ON DELETE CASCADE,
    target_vendor_id       INTEGER REFERENCES vendors(id) ON DELETE CASCADE,
    target_doc_artifact_id INTEGER REFERENCES doc_artifacts(id) ON DELETE CASCADE,
    relation_kind          TEXT NOT NULL CHECK (relation_kind IN ('mentions_dependency','mentions_artifact')),
    UNIQUE (source_doc_artifact_id, target_vendor_id, target_doc_artifact_id)
  );
  ```
  Exactly one of `target_vendor_id`/`target_doc_artifact_id` is set per
  row, matching `relation_kind` — mirrors `skill_mentions_edges`'s existing
  two-nullable-target shape, not a new pattern. New `DocRelationEdgeRow`
  dataclass (`source_doc_artifact_path`, `target_vendor_name: str | None`,
  `target_doc_artifact_path: str | None`, `relation_kind: str`),
  `rebuild_deterministic` gains a `doc_relations_edges: Sequence[
  DocRelationEdgeRow]` parameter, inserted the same way every other edge
  table is.
- `doc_mapping.py`: new `build_doc_relations_edges(spec_doc_rows:
  list[DocArtifactRow], configs: list[VendorConfig], other_doc_artifact_
  rows: list[DocArtifactRow], project_root: Path) -> list[DocRelationEdgeRow]`.
  For each spec doc, read its text once and word-boundary-scan
  (`re.search(rf"\b{re.escape(name)}\b", text)`, same helper pattern as
  `build_documents_edges`/`build_skill_mentions_edges`) for: (a) every
  tracked vendor's name → `relation_kind='mentions_dependency'`; (b) every
  *other* doc artifact's `name` field (a Skill's frontmatter `name`, a
  dependency doc's `f"{vendor} CLAUDE.md"`-style name) → `relation_kind=
  'mentions_artifact'`. Direction is spec-doc-outward only in this phase
  (see Explicitly deferred) — a Skill's own body mentioning a spec doc by
  name is not scanned for.
- `sync.py`: `rebuild_project_graph` gains a call to `spec_docs.scan_spec_
  docs` and `doc_mapping.build_doc_relations_edges`, feeding the new
  `rebuild_deterministic` parameter — same wiring shape as the existing
  `skill_scan.scan_skills`/`doc_mapping.build_skill_mentions_edges` call
  pair.
- `graph.py`: new query `doc_relations(conn, doc_artifact_path: str) ->
  list[dict]` — every `doc_relations_edges` row for a given source path,
  resolved to the target's name/path, for `query relations` to call.
- `cli.py`: new `codecompass query relations <name>` — accepts a spec-doc
  filename (e.g. `architecture/overview.md`), a vendor name, or a Skill
  name; prints what it mechanically relates to. Same "canned read-only
  query over the graph" pattern as `query vendors`/`query vendor`/`query
  symbol`/`query skills`.
- `check`: new report-only coverage-gap section — spec docs with zero
  detected relations (could mean genuinely unrelated content, could mean a
  naming mismatch worth a human look) — report-only, never `--strict`-
  blocking, same posture as every other graph-derived coverage gap
  (`decisions/`-established, MVP spec point 8).
- `skill.py`'s tool-level Skill and the `/discovery` slash-command template
  gain a short mention of `query relations` alongside the existing `query`
  subcommand documentation (the exact expansion `render_tool_skill` already
  got for `query` earlier this project — same treatment, one more bullet).

**Explicitly deferred / out of scope:**

- `vendor.toml`-configurable spec-doc glob patterns. Ship with the fixed
  default list; add configurability only once a real project shows the
  defaults are wrong for it — same incremental-scope posture already used
  for `enrichment.py`'s batch size (Phase 14) and `usage.py`'s prune-dir
  set.
- Bidirectional mention detection (a Skill or dependency doc's own body
  text mentioning a spec doc by name). Spec-doc-outward scanning only.
  Natural follow-up if real usage shows the missing direction matters;
  not needed for a first version of this feature.
- Any AI call or relationship *summary* — that's Phase 22, gated on this
  phase's mechanical edges as its only input.
- Chunk-level retrieval into a spec doc's specific section (`DocChunk`/
  `EXPLAINS`, already deferred since the original phase-9d sketch) — a
  `doc_relations_edges` row says "this spec doc as a whole mentions this
  vendor," not "this specific section does." Still explicitly deferred,
  not resurrected here.

## Design decisions

**A new `doc_relations_edges` table, not an extension of `documents_edges`
or `skill_mentions_edges`.** Considered folding spec-doc mentions into
`documents_edges` (already `doc_artifact → symbol`) or `skill_mentions_
edges` (already `doc_artifact → vendor/source_file`). Rejected both:
`documents_edges` is specifically "this artifact documents this *symbol*"
(narrower — spec docs mentioning a vendor by name usually aren't naming
individual symbols), and `skill_mentions_edges` is narrowly scoped to
*skills* as the source, not any doc artifact. Widening either table's
semantics to also mean "any doc artifact mentions any other doc artifact"
would blur what each table currently guarantees for existing callers
(`skills_index`, `vendor_profile`'s `documenting_artifacts`). A new,
purpose-built table keeps every existing query function's contract
unchanged and makes the new three-way web (spec docs ↔ dependency docs ↔
skills) queryable on its own terms. Revisit consolidating all "doc artifact
mentions X" edges into one general table only if real duplication pain
shows up across all three — no evidence of that yet.

**Default-glob detection, not a manifest/marker file the user has to
maintain.** A hand-maintained list of "which files are specs" would drift
the same way a hand-maintained `undo` file list would have (rejected for
the same reason in Phase 18, `decisions/0036`) — convention-based
detection, driven by the graph rebuild that already runs on every sync,
stays correct automatically as spec docs are added/removed/renamed.

## Files

- `src/codecompass/graph.py` — new `doc_relations_edges` table + CHECK
  widening migration, `DocRelationEdgeRow`, `rebuild_deterministic`
  parameter + insert helper, `doc_relations` query function.
- `src/codecompass/spec_docs.py` — new module, `scan_spec_docs`.
- `src/codecompass/doc_mapping.py` — new `build_doc_relations_edges`.
- `src/codecompass/sync.py` — wiring into `rebuild_project_graph`.
- `src/codecompass/cli.py` — new `query relations <name>`, `check`'s new
  coverage-gap section.
- `src/codecompass/skill.py` — tool Skill guidance addition.
- `.claude/commands/discovery.md`'s generation template (wherever
  `write_discovery_command` renders it) — same addition.
- `architecture/overview.md` — "Context graph" section gains the new
  table/concept.
- `tests/test_spec_docs.py` (new), `tests/test_doc_mapping.py`,
  `tests/test_graph.py`, `tests/test_cli.py`, `tests/test_skill.py`.
- `decisions/` — new ADR for the spec-doc classification + new-table
  decision (non-obvious tradeoff per `CLAUDE.md` §2), written at
  implementation time once the design here is actually locked in.

## Verification

- `pytest` — full suite passes, including new/extended cases above.
- `ruff check .` — clean.
- Manual, against this repo itself (the established dogfooding pattern):
  run a whole-project `sync`, confirm `README.md`, `architecture/
  overview.md`, every `decisions/*.md`, and every `docs/*.md` appear via
  `query relations` or direct `sqlite3` as `kind='spec_doc'`; confirm
  `CHANGELOG.md` and root `CLAUDE.md` do **not** appear; confirm
  `architecture/overview.md` (which names `rich`/`typer`/`anthropic`
  throughout) shows `mentions_dependency` edges to all three.
