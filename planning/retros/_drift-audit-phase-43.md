# Drift audit — Phase 43 (43a: `query skills` widen to `cursor_mdc` + `slash_command`)

**Auditor:** docs-reconstructor (MODE 1, per-phase drift audit)
**Base:** working tree vs `git` HEAD `99c415c` (Phase 43 not yet committed)
**Governing doc:** `planning/v1-redefinition/documentation-lifecycle.md` §2.5

## Verdict: NO DRIFT

All current-truth docs that the diff touched, plus every current-truth doc
sentence the widening could have falsified, were checked against the
**verified** code (SQL read directly, three tests re-run green). The
`docs-maintainer` edits to `docs/cli-reference.md` and
`architecture/overview.md`, and the regenerated
`.claude/skills/codecompass/SKILL.md`, all accurately describe the new
behaviour.

## Observable behaviour that changed

1. `graph.skills_index` (`src/codecompass/graph.py:1241-1293`) — SQL is now
   `WHERE kind IN ('skill', 'cursor_mdc', 'slash_command')` via
   `_SKILLS_INDEX_KINDS`; every returned row dict carries `"kind": kind`.
   Verified: `cursor_mdc` and `slash_command` `doc_artifacts` rows are now
   returned. (`test_graph.py::test_skills_index_includes_cursor_mdc_and_slash_command`
   passes.)
2. `cli.py::query_skills` (`src/codecompass/cli.py:646-687`) — Rich table
   gains a **"Kind"** column between "Path" and "Name"
   (`entry["kind"] or ""`); `--json` output is the raw `skills_index` rows
   so it now includes `kind`; `query_skills` docstring and
   `--unused-mentions` help reworded from "Skills/.mdc rules" to
   "agent-context artifact" / "artifacts". Verified via
   `test_cli.py::test_query_skills_shows_cursor_mdc_and_slash_command`.
3. `skill.py::render_tool_skill` (`src/codecompass/skill.py:92-99`) — the
   generated tool-Skill's `query skills` bullet reworded.
   `.claude/skills/codecompass/SKILL.md:23` matches the new generator
   output verbatim (regenerated, not hand-edited — consistent with
   `render_tool_skill`).

## Docs checked against verified behaviour

| Doc | Location | Check | Result |
|---|---|---|---|
| `docs/cli-reference.md` | 129-130 (status line) | "`skills` widened to Cursor `.mdc` rules and the `/discovery` slash command, with a `kind` field, Phase 43a" | Accurate |
| `docs/cli-reference.md` | 151-157 (`query skills` entry) | "every agent-context artifact … Skills, Cursor `.mdc` rules, and the `/discovery` slash command. Each row shows its **Kind** (`skill`, `cursor_mdc`, or `slash_command`), origin, and what it mechanically mentions …; the `kind` is also present in `--json`." | Accurate — matches table columns and JSON |
| `architecture/overview.md` | 604-608 (`/discovery` section) | OLD paragraph ("were not widened in this phase — they remain hard-filtered to `kind = 'skill'` … only through a direct `context-graph.db` read. See `planning/CONTEXT.md` for the current status of this gap.") **fully removed**; replaced with "the read-side query matches `kind IN ('skill', 'cursor_mdc', 'slash_command')`, so a `slash_command` row (and any Cursor `.mdc` rule) appears alongside Skills, each tagged with its `kind`." | Correct — string-for-string matches the new SQL; stale gap claim and the CONTEXT.md pointer are gone |
| `architecture/overview.md` | 1028-1031 (`skills_index` bullet under "Context graph") | "every agent-context `doc_artifacts` row (`kind` one of `skill`, `cursor_mdc`, `slash_command`), its `kind` and `origin`, and what it mechanically mentions" | Accurate |
| `.claude/skills/codecompass/SKILL.md` | 23 | matches `skill.py::render_tool_skill` new output | Consistent (regenerated) |

## Reverse check — did widening falsify any untouched doc sentence?

- **`README.md`** — describes generated Skills / `.cursor/rules` `.mdc`
  and `/discovery` (lines 118-119, 107-109) but never claims `query
  skills` is skill-only. No drift.
- **`ai-docs/README.md`** — mentions `/discovery` (line 33) and generated
  Skills only; no `query skills` scope claim. No drift.
- **`architecture/overview.md`** — remaining `kind='skill'` mentions are
  `build_routes_via_edges` (1301-1306), `scan_skills` (1318-1327),
  `_graph_backed_undo_paths` (1701-1713), and the Phase-20 regeneration-
  ordering note (774-777). All concern other code paths and remain true.
  No other sentence anywhere in `README.md` / `docs/` / `architecture/` /
  `ai-docs/` still says `query skills` / `skills_index` is `skill`-only.
- No current-truth doc counts skills / doc-artifact rows (no "9
  artifacts" / "5 skills" claim to invalidate). The `check` command's
  "orphaned skill mentions" wording (`docs/cli-reference.md:249`,
  `SKILL.md` line ~13) is unaffected — `check` does not call
  `skills_index`.
- No product doc references removed behaviour; nothing was removed, the
  change is purely additive (new column / new JSON field / wider filter).

## Scope note — deliberately not flagged

- **`CHANGELOG.md:622`** — the Phase 17 entry still reads "`query skills`
  doesn't yet surface the new artifact kind." This is a historical
  Keep-a-Changelog record of what Phase 17 did, is time-relative ("yet"),
  and is **out of drift-audit scope** (scope is current-truth docs:
  `README.md`, `docs/`, `architecture/`, `ai-docs/`). Changelog entries
  are not retro-edited; Phase 43a's own `[Unreleased]` entry documents the
  fix. Noted, not a finding.
- `.claude/agents/docs-maintainer.md` (new generated-file rule),
  `planning/learnings/inbox.md` (L-005), `planning/ROADMAP.md`,
  `planning/phase-43*.md`, `tests/**` — not current-truth product docs;
  outside audit scope.
- `.claude/commands/discovery.md:25` only lists the command name with no
  kind constraint — nothing to correct.

## Verification performed

- Read `graph.py::skills_index` and `cli.py::query_skills` source directly
  (did not trust the plan or `docs-maintainer`'s summary).
- Re-ran `test_skills_index_includes_cursor_mdc_and_slash_command`,
  `test_query_skills_shows_cursor_mdc_and_slash_command`,
  `test_render_tool_skill_explains_each_query_subcommand_and_escape_hatch`
  — 3 passed.
- Diffed `render_tool_skill` output against the tracked `SKILL.md`: the
  `query skills` line is identical (other diff noise was a local shell
  encoding artifact + an unloaded `vendor.toml` in the throwaway check).
- `grep` across `README.md`, `docs/`, `architecture/`, `ai-docs/` for
  `query skills` / `skills_index` / `Skill/\`.mdc\`` / `slash_command`.
