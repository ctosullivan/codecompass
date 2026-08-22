"""Custom slash command generation: `/discovery`
(planning/phase-17-discovery-slash-command.md) — a distinct artifact type
from `skill.py`'s Agent Skills. Claude Code custom slash commands live
under `.claude/commands/<name>.md` (invoked by typing `/<name>`), not
`.claude/skills/<name>/SKILL.md` (auto-triggered by description
matching), and use a different (though overlapping) frontmatter shape.
Both are templated, non-AI-generated, deterministic text this project
already knows how to produce — this module follows `skill.py`'s
render/write split, not a new pattern.
"""

from __future__ import annotations

from pathlib import Path

_COMMANDS_DIR_NAME = "commands"
_DISCOVERY_COMMAND_FILENAME = "discovery.md"


def render_discovery_command() -> str:
    """Templated (non-AI) markdown for `.claude/commands/discovery.md`.
    Purely deterministic and project-agnostic — unlike `render_tool_skill`,
    no vendor list or enrichment status is threaded in, since this
    command's whole job is to teach Claude *how* to explore whatever a
    project's codecompass output currently is at question time (`query`/
    `check`/persisted digests already answer "what's the current state").

    `allowed-tools` (checked against Claude Code's own docs at this
    phase's implementation date: `.claude/commands/*.md` files support the
    same frontmatter reference Agent Skills do, `allowed-tools` included,
    with the same "pre-approve without prompting for this invocation"
    semantics) makes the read-only posture mechanical, not just
    instructional — `Read`/`Grep`/`Glob` for browsing persisted digests/
    Skills, plus narrowly-scoped `Bash(...)` patterns for exactly the two
    sanctioned escape-hatch commands (`codecompass query`/`check`, and
    read-only `sqlite3` access to `context-graph.db`). `Write` and `Edit`
    are deliberately absent from the list.
    """
    lines = [
        "---",
        "description: >-",
        "  Explore this project's codecompass-tracked dependencies —",
        "  usage, enrichment status, relationships between vendors and",
        "  project source — by querying the context graph and reading",
        "  already-generated digests. Read-only: never writes, edits, or",
        "  plans code changes.",
        "allowed-tools: >-",
        "  Read Grep Glob Bash(codecompass query:*) Bash(codecompass",
        "  check:*) Bash(sqlite3 context-graph.db:*)",
        "---",
        "",
        "# /discovery",
        "",
        "Answer the user's question about this project's dependencies by",
        "**exploring already-generated codecompass output** — never by",
        "writing, editing, or planning code.",
        "",
        "## How to explore",
        "",
        "1. Start with the canned queries — cheapest and most reliable:",
        "   - `codecompass query vendors [--unused] [--json]`",
        "   - `codecompass query vendor <name> [--json]`",
        "   - `codecompass query symbol <name> [--json]`",
        "   - `codecompass query skills [--unused-mentions] [--json]`",
        "   - `codecompass query relations <name> [--json]` — given a",
        "     spec-doc path, what it mechanically mentions; given a vendor",
        "     or Skill name, which spec docs mechanically mention it.",
        "     Shows an AI-enriched summary of *how* the two relate when",
        "     one exists.",
        "   - `codecompass check` — staleness + coverage-gap report.",
        "2. If a question doesn't fit any canned query — an ad hoc join or",
        "   filter across the graph — fall back to direct, read-only SQL",
        "   against `context-graph.db` in the project root, e.g.",
        '   `sqlite3 context-graph.db "SELECT ..."`. See',
        "   `architecture/overview.md`'s \"Context graph\" section for the",
        "   schema (`vendors`, `symbols`, `uses_edges`, `doc_artifacts`,",
        "   `documents_edges`, `skill_mentions_edges`, `routes_via_edges`,",
        "   `depends_on_edges`, `doc_relations_edges`, `vendor_enrichment`,",
        "   `symbol_enrichment`, `doc_relation_enrichment`).",
        "3. Read persisted digests directly when a query result points at",
        "   one: `vendor/<name>/CLAUDE.md`, `vendor/<name>/OVERVIEW.md`",
        "   (if enriched), `vendor/<name>/FILETREE.md`,",
        "   `vendor/<name>/DEPTREE.md`, and `.claude/skills/**/SKILL.md`",
        "   (including this project's own tool-level Skill).",
        "",
        "## Constraints — hold these for the whole exchange, not just once",
        "",
        "- **No `Write`, no `Edit`, no code changes, no plan file.** This",
        "  command answers questions; it does not act on them.",
        "- If answering would require changing something — code, config,",
        "  a digest, anything — **say so explicitly and stop.** Describe",
        "  what change would be needed and let the user decide whether to",
        "  pursue it in a normal (non-`/discovery`) session. Do not make",
        "  the change yourself, even if it looks small or obviously",
        "  correct.",
        "- Prefer the context graph and persisted digests over training",
        "  knowledge — they're version-pinned to what's actually",
        "  installed in this project; training knowledge about a",
        "  dependency may be stale or simply wrong for this version.",
        "- If `context-graph.db` doesn't exist yet, say so and suggest",
        "  `codecompass sync` — don't guess at an answer `query`/`check`",
        "  would otherwise ground.",
        "",
        "**Restated: read-only. No `Write`. No `Edit`. No plan file. No",
        "code changes.** If in doubt, stop and ask rather than act.",
    ]
    return "\n".join(lines) + "\n"


def write_discovery_command(project_root: Path) -> None:
    commands_dir = project_root / ".claude" / _COMMANDS_DIR_NAME
    commands_dir.mkdir(parents=True, exist_ok=True)
    (commands_dir / _DISCOVERY_COMMAND_FILENAME).write_text(
        render_discovery_command(), encoding="utf-8"
    )
