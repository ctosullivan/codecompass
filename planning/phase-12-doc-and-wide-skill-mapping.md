# Phase 12: Doc & wide skill mapping

## Scope

**Covered:**
- `src/codecompass/doc_mapping.py` (new) — pure transformations of
  already-generated artifacts; no new AI, no new extraction:
  - `collect_vendor_doc_artifacts(configs, project_root) ->
    list[DocArtifactRow]` — for each tracked vendor: a `kind='claude_md'`
    row for `vendor/<name>/CLAUDE.md` (always present once synced) and a
    `kind='overview'` row for `vendor/<name>/OVERVIEW.md` **if it
    exists** (only currently-`promote`d vendors have one — `promote`
    still exists at this point in the sequence, removed in Phase 15).
    Both `origin='codecompass_vendor'`, `vendor_id` set.
  - `build_documents_edges(doc_artifact_rows, symbol_rows) ->
    list[DocumentsEdgeRow]` — for each vendor's `claude_md`/`overview`
    doc artifact, read its file text and word-boundary-match it against
    *that same vendor's* known symbol names (from the `symbols` rows
    Phase 11 already collects) → one edge per match. A coverage
    heuristic ("this symbol's name appears in the vendor's own digest
    text"), explicitly not a quality judgment — same framing the
    superseded phase-9c design already used for this exact edge type.
  - `build_depends_on_edges(configs, project_root) ->
    list[DependsOnEdgeRow]` — for each tracked vendor, read its
    persisted `vendor/<name>/deptree.json` and flatten it to a
    `{name: {versions}}` map (a small local flattener mirroring
    `staleness._flatten`'s existing approach — deptree.json's shape is
    the same either way; duplicating this ~15-line pure function locally
    is consistent with this project's existing style of small,
    module-local private helpers rather than a shared-utils module).
    Emits a `Vendor → Vendor` edge wherever a flattened name matches
    another *tracked* vendor's name (checked against the `vendors` table
    — an untracked transitive dependency isn't a graph node, so no edge
    for it).
  - `build_routes_via_edges(configs, doc_artifact_rows) ->
    list[RoutesViaEdgeRow]` — for each vendor: if a per-vendor Skill doc
    artifact exists (`kind='skill'`, `origin='codecompass_vendor'`, from
    `skill_scan.py` below) route to it; otherwise route to the shared
    tool-level Skill (`kind='skill'`, `origin='codecompass_tool'`) —
    operationalizes `decisions/0013` point 6 as real queryable data,
    exactly as the superseded phase-9c design already specified.
- `src/codecompass/skill_scan.py` (new) — the scope-expanded piece:
  indexes **every** skill under `.claude/skills/`, not just
  codecompass-generated ones (this rework's spec point 5, genuinely new —
  the superseded phase-9c design was scoped to codecompass's own skills
  only).
  - `scan_skills(project_root, configs) -> list[DocArtifactRow]` — globs
    `.claude/skills/**/SKILL.md`, extracts `name`/`description` via a
    **minimal custom frontmatter parser** (split on `---` delimiters,
    handle both a single-line `key: value` and a folded `key: >-` block
    with indented continuation lines — the two forms this project's own
    generated Skills already use; see Design decisions for why this
    isn't a full YAML parser). Classifies `origin`: directory name exactly
    `codecompass` → `codecompass_tool`; directory name `codecompass-
    <vendor>` for a name in `configs` → `codecompass_vendor` (`vendor_id`
    set); anything else → `third_party`. Also scans
    `.cursor/rules/*.mdc` the same way (`kind='cursor_mdc'`, same
    frontmatter shape, same origin classification by filename prefix).
  - `build_skill_mentions_edges(skill_doc_artifacts, configs,
    source_file_rows) -> list[SkillMentionEdgeRow]` — for each skill's
    body text (not just frontmatter), word-boundary-match against every
    tracked vendor name → vendor-mention edge, and against every tracked
    project source-file path's basename → source-file-mention edge. A
    presence heuristic, same posture as `documents_edges` — explicitly
    not a claim the skill is *about* that vendor/file, just that it
    mentions it mechanically.
- `src/codecompass/sync.py` — `rebuild_project_graph` extended to call
  the four new functions above and pass their real output into
  `rebuild_deterministic`'s `doc_artifacts`/`documents_edges`/
  `skill_mentions_edges`/`routes_via_edges`/`depends_on_edges`
  parameters (previously all empty lists from Phase 11).
- Tests: `tests/test_doc_mapping.py`, `tests/test_skill_scan.py` (new) —
  fixture doc/skill files, asserting exact edge output including the
  word-boundary-not-substring matching behavior (e.g. a skill mentioning
  "sixty" must not produce a false mention-edge for a hypothetical
  vendor named "six").

**Explicitly deferred / out of scope:**
- Any CLI-visible query surface (`codecompass query`, `check`'s
  coverage-gap sections reading these new edges) — Phase 15.
- `DocChunk`/`EXPLAINS` chunk-level retrieval — explicitly deferred per
  `decisions/0032`; not part of this phase or this schema at all.
- A real YAML parser dependency — deliberately not added; see Design
  decisions.

## Design decisions

**Frontmatter parsing stays a minimal custom extractor, not a YAML
dependency.** This project has no YAML dependency today (`pyproject.toml`
lists `typer`, `rich`, `anthropic`, `pipdeptree` only) and every Skill
this project itself generates uses one of exactly two simple frontmatter
shapes (single-line `key: value`, or `key: >-` with indented
continuation). Adding a real YAML parser to correctly handle arbitrary
third-party Skill frontmatter (which could use nested structures,
multi-value lists, etc.) would be a real new dependency for a case this
project doesn't need to fully solve — a coarse extractor that handles the
common cases and returns `None`/best-effort on anything it can't parse
(never raising) is consistent with this project's existing precedent
(the Cargo adapter's line-based `pub` scan, `extract_npm_symbols`'s
regex-based export scan — both explicitly coarse, not exhaustive
parsers). Flag if this clips real third-party Skill descriptions once
tested against a repo with a nontrivial `.claude/skills/` tree.

**Word-boundary matching, not substring, for both mention-edge types.**
A naive substring match risks false positives on any vendor/file name
that collides with common English words (`rich`, `six`) or is a short
enough package name to appear inside unrelated words. Regex
`\b<name>\b` (case-sensitive — this project's own generated skill
content is lowercase-consistent, and case-insensitive matching would
increase false-positive risk further) is the minimum bar; flag for
tuning after this phase ships against a project with a large,
non-codecompass-authored `.claude/skills/` tree.

## Files

- `src/codecompass/doc_mapping.py` (new).
- `src/codecompass/skill_scan.py` (new).
- `src/codecompass/sync.py` — `rebuild_project_graph` extended.
- `tests/test_doc_mapping.py` (new), `tests/test_skill_scan.py` (new).
- `architecture/overview.md` — extend "Context graph" section;
  `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md`.

## Verification

- `pytest` — full suite passes; no live API call anywhere.
- `ruff check .` — clean.
- Manual, against this repo itself: run bare `codecompass`, then query
  the graph directly — confirm `.claude/skills/codecompass/SKILL.md`
  appears as a `doc_artifacts` row with `origin='codecompass_tool'`, that
  `routes_via_edges` links every tracked vendor to it (none are
  currently promoted with their own per-vendor Skill, since `rich`'s
  promotion was lost in the earlier session's file-loss incident and not
  yet re-run), and that `depends_on_edges` correctly reflects at least
  one real transitive relationship among the four tracked vendors if one
  exists (check `vendor/*/deptree.json` first to know what to expect).
- Fixture test confirming the word-boundary matcher does *not* produce a
  false mention-edge for a substring collision (e.g. vendor `"six"`
  against skill text containing "sixty-four").
