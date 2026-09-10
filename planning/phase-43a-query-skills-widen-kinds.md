# Phase 43a: `query skills` surfaces `cursor_mdc` + `slash_command` rows

**Status:** done (2026-09-10) — shipped as the Phase 43 dogfood change;
drift audit NO DRIFT; `release-phase-auditor` PASS (after Phase 43's
planning-doc fixes).

The concrete code change dogfooded in **Phase 43**
(`planning/phase-43-dogfood-agent-led-workflow.md`) — chosen by the user
from that phase's shortlist. Phase 43's own file covers the *meta*
(running the full 14-step loop + GATE DA); this file is the change spec.

## Context / the gap

`doc_artifacts.kind` has, in a real graph today (this repo):
`claude_md`, `overview`, `skill` (5), `cursor_mdc` (3), `slash_command`
(1), `spec_doc`, `vendor_doc`.

`graph.skills_index` — and therefore `codecompass query skills` — is
hard-filtered to `WHERE kind = 'skill'`. So:

- **`/discovery`** (`.claude/commands/discovery.md`, `kind='slash_command'`,
  Phase 17) never appears in `query skills`, only via a raw
  `context-graph.db` read. This is the documented gap
  (`architecture/overview.md` `/discovery` section; `planning/CONTEXT.md`).
- **Cursor `.mdc` rules** (`kind='cursor_mdc'`) *also* never appear —
  even though `query skills`'s own docstring says "Every Skill/`.mdc`
  rule under the project" and `--unused-mentions`'s help says
  "Skills/.mdc rules". A pre-existing, undocumented instance of the same
  bug, found while scoping this change.

`skill_mentions_edges` are already built for `cursor_mdc` and
`slash_command` rows (`skill_scan.build_skill_mentions_edges` iterates
every `scan_skills` row regardless of kind) — only the read-side query
filters them out.

## Scope

**In scope:**

- `graph.skills_index`: `WHERE kind = 'skill'` →
  `WHERE kind IN ('skill', 'cursor_mdc', 'slash_command')`; add
  `"kind": kind` to each returned row dict. Keep the function name
  (`skills_index`) and the SELECT/JOIN shape otherwise unchanged.
- `cli.py::query_skills`: add a **"Kind"** column to the Rich table
  (between Path and Name); `--json` gains `kind` per row (additive).
  `--unused-mentions` filter unchanged (still works — it only reads
  `mentions_vendors`/`mentions_source_files`).
- Docstrings: `graph.skills_index`, `cli.query_skills` — say "Skills,
  Cursor `.mdc` rules, and the `/discovery` slash command" instead of
  "kind='skill'" / "Skill/`.mdc` rule".
- Tests: `tests/test_graph.py` — `skills_index` returns `cursor_mdc` and
  `slash_command` rows with correct `kind`; `tests/test_cli.py` — `query
  skills` table/JSON shows them.
- Docs (`docs-maintainer`): `docs/cli-reference.md` `query skills` entry;
  `architecture/overview.md` `/discovery` section (the "not widened in
  this phase … see CONTEXT.md for the status of this gap" paragraph is
  now stale — the gap is closed); `.claude/skills/codecompass/SKILL.md`
  `query skills` line if it constrains the kinds.
- `CHANGELOG.md` `[Unreleased]` entry.

**Out of scope:**

- Renaming the `skills` command or `skills_index` function (breaking
  change, not worth it — "Kind" column disambiguates).
- `graph.py` schema change (none needed — `kind` values already exist).
- `undo`'s `kind == "skill"` branch (`cli.py` ~L1009) — that's
  path-resolution for a different feature, unaffected.
- Touching `skill_mentions_edges` construction (already correct).
- A new ADR — this is a bug fix (command didn't match its own
  docstring), not a non-obvious tradeoff. The one judgment call
  (include `cursor_mdc`, not just the documented `slash_command`) is
  recorded here: the docstring already promised `.mdc`, so excluding it
  would leave the command still lying.

## Files (actual)

- `src/codecompass/graph.py` — `skills_index` WHERE widened + `kind` in
  each row dict + `_SKILLS_INDEX_KINDS`
- `src/codecompass/cli.py` — `query_skills` "Kind" column + docstring +
  `--unused-mentions` help
- `src/codecompass/skill.py` — the generated tool Skill's `query skills`
  description line (the source of `.claude/skills/codecompass/SKILL.md`)
- `.claude/skills/codecompass/SKILL.md` — **regenerated** from `skill.py`
  (not hand-edited)
- `tests/test_graph.py`, `tests/test_cli.py`, `tests/test_skill.py` — +3
  tests
- `docs/cli-reference.md`, `architecture/overview.md`,
  `.claude/skills/codecompass/SKILL.md` (via `skill.py`) — via
  `docs-maintainer`
- `.claude/agents/docs-maintainer.md` — new "check if a file is
  generated before editing" rule (from **L-005**, surfaced this phase)
- `planning/learnings/inbox.md` — **L-005** filed
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md`,
  `planning/phase-43*.md`, retro + agent reports — via
  `roadmap-context-curator` / lead

## Verification

- `pytest` (new + existing graph/cli tests) / `ruff check .` clean.
- New tests fail against pre-change `graph.skills_index` and pass after.
- Live against this repo: `codecompass sync` (rebuild graph), then
  `codecompass query skills` shows `.claude/commands/discovery.md`
  (Kind `slash_command`) and the 3 `.cursor/rules/*.mdc` rows (Kind
  `cursor_mdc`) alongside the 5 skills; `--json` carries `kind`;
  `--unused-mentions` still filters correctly.
- `python scripts/check_user_docs.py --strict` clean (the new checks +
  the doc updates).

## Done when

Standard DoD (as amended — retro + drift audit + learning triage +
independent auditor PASS) — this is exercised in full as Phase 43's
dogfood.
