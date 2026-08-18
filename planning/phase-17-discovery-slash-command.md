# Phase 17: `/discovery` slash command

## Scope

**Covered:**
- `src/codecompass/commands.py` (new) — a distinct module from
  `skill.py`, not folded into it: Claude Code custom slash commands are a
  different artifact type from Agent Skills (different directory
  convention — `.claude/commands/`, not `.claude/skills/<name>/` —
  and a different frontmatter shape), even though both are templated,
  non-AI-generated, deterministic text this project already knows how to
  produce.
  - `render_discovery_command() -> str` — templated markdown with
    frontmatter (`description: ...`) and a body instructing Claude to:
    (1) explore using `codecompass query {vendors|vendor|symbol|skills}`
    and, as an escape hatch, direct `sqlite3 context-graph.db` access for
    anything the canned queries don't cover; (2) read persisted
    `vendor/<name>/CLAUDE.md`/`OVERVIEW.md`/`FILETREE.md`/`DEPTREE.md`
    and `.claude/skills/**/SKILL.md` content as needed; (3) **explicit,
    repeated constraints**: no `Write`/`Edit`, no plan file, no code
    changes — if a question's answer requires a change, say so and stop
    rather than proceeding. If Claude Code's slash-command frontmatter
    supports a tool-restriction field (`allowed-tools` or equivalent) as
    of this phase's implementation date, set it to a read-only tool set
    to make the constraint mechanical rather than purely instructional —
    verify the exact current syntax against Claude Code's own docs at
    implementation time (this is prompt-template content, not
    `codecompass` runtime behavior, so it's the one place in this phase
    where "check the current docs" is a real implementation step, not
    boilerplate caution).
  - `write_discovery_command(project_root: Path) -> None` — writes
    `.claude/commands/discovery.md`.
- `src/codecompass/cli.py` — `write_discovery_command` called at the same
  points `write_tool_skill` already is: `_bootstrap`, the `index`
  command, and `sync`'s whole-project branch (Phase 15's Phase A
  completion step) — same generation-trigger pattern reused, not a new
  one invented. Deterministic, no AI cost, so triggering it unconditionally
  alongside the tool Skill is free.
- `src/codecompass/skill_scan.py` (from Phase 12) — extended so
  `scan_skills`-equivalent logic also indexes `.claude/commands/
  discovery.md` itself as a `doc_artifacts` row (`kind` needs a new
  variant — see Design decisions) with `origin='codecompass_tool'`, so
  Phase 18's `undo` can find it the same way it finds every other
  generated artifact, and so it participates in the graph like any other
  codecompass-generated file.
- Tests: `tests/test_commands.py` (new) — deterministic content
  assertions (same style as `tests/test_skill.py`'s existing tool-Skill
  content tests); `tests/test_cli.py` extended to confirm
  `.claude/commands/discovery.md` is written at all three trigger points.

**Explicitly deferred / out of scope:**
- Any behavior change to `chat <vendor>` itself — Phase 19 handles the
  *framing* consequence of `/discovery` existing (chat becomes more
  clearly secondary by comparison); this phase only adds the new
  artifact.
- A `--dry-run`/preview mode for `/discovery`'s own content — not
  requested, not needed (it's deterministic and free to regenerate).

## Design decisions

**`doc_artifacts.kind`'s CHECK constraint needs a new value.** Phase 10's
schema constrained `kind IN ('claude_md','overview','skill','cursor_mdc')`
— `/discovery` doesn't fit any of those. Add `'slash_command'` to the
constraint (a schema migration concern only in the sense that
`init_schema` uses `CREATE TABLE IF NOT EXISTS`, so an already-existing
`context-graph.db` from before this phase won't automatically pick up
the widened constraint — call out explicitly in `graph.py`'s
`schema_version` handling: bump it, and have `open_graph` drop+recreate
the `doc_artifacts` table specifically if the stored version predates
this phase, since the table is fully rebuilt by `rebuild_deterministic`
every whole-project sync anyway — no data loss risk in re-creating a
purely-deterministic table).

## Files

- `src/codecompass/commands.py` (new).
- `src/codecompass/cli.py` — three call sites.
- `src/codecompass/graph.py` — `doc_artifacts.kind` constraint widened;
  `schema_version` bump + migration handling in `open_graph`.
- `src/codecompass/skill_scan.py` — indexes the new artifact.
- `tests/test_commands.py` (new); `tests/test_cli.py`,
  `tests/test_graph.py` extended.
- `docs/cli-reference.md` — documents `/discovery` as a generated
  artifact (not a CLI command — clarify this distinction explicitly, it's
  easy to misread as one more `codecompass` subcommand).
  `architecture/overview.md` — new subsection describing `/discovery`
  alongside the existing Skill-export description.
  `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md`.

## Verification

- `pytest` — full suite passes.
- `ruff check .` — clean.
- Manual: run bare `codecompass` against this repo, confirm
  `.claude/commands/discovery.md` is written with valid frontmatter; open
  a Claude Code session in this repo and invoke `/discovery`, ask a
  relationship question ("what uses `rich`?"), confirm it answers via
  `codecompass query`/digest reads and does not create, edit, or delete
  any file during the exchange.
- Confirm re-running `codecompass index` after manually deleting
  `.claude/commands/discovery.md` regenerates it — same idempotent
  regeneration guarantee every other generated artifact already has.
