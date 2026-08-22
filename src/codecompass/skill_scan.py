"""Indexes every Skill under `.claude/skills/` and every Cursor `.mdc`
rule under `.cursor/rules/` — not just codecompass's own generated ones
(this rework's spec point 5; the superseded phase-9c design was scoped to
codecompass's own Skills only). See
planning/phase-12-doc-and-wide-skill-mapping.md.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from codecompass.core import VendorConfig
from codecompass.graph import DocArtifactRow, SkillMentionEdgeRow, SourceFileRow
from codecompass.skill import _TOOL_SKILL_DIR_NAME, _vendor_skill_name

_FRONTMATTER_DELIM = "---"
_FOLDED_BLOCK_MARKERS = (">-", ">", "|-", "|")


def _extract_scalar(frontmatter_lines: list[str], key: str) -> str | None:
    """Minimal custom extractor for one key out of a `---`-delimited
    frontmatter block — not a real YAML parser (see
    planning/phase-12-doc-and-wide-skill-mapping.md's Design decisions).
    Handles the two shapes this project's own generated Skills/`.mdc`
    files use: a single-line `key: value`, and a folded `key: >-` block
    with indented continuation lines. Anything it can't confidently parse
    for `key` returns `None` — never raises.
    """
    prefix = f"{key}:"
    for index, raw_line in enumerate(frontmatter_lines):
        stripped = raw_line.strip()
        if not stripped.startswith(prefix):
            continue
        value = stripped[len(prefix) :].strip()
        if value == "" or value in _FOLDED_BLOCK_MARKERS:
            continuation: list[str] = []
            for cont_line in frontmatter_lines[index + 1 :]:
                if not cont_line.strip() or not cont_line[:1].isspace():
                    break
                continuation.append(cont_line.strip())
            return " ".join(continuation) if continuation else None
        return value.strip("'\"")
    return None


def _parse_skill_file(text: str) -> tuple[str | None, str | None, str]:
    """Returns `(name, description, body)`. `body` is everything after the
    closing `---` delimiter; if `text` doesn't start with a recognizable
    frontmatter block, `(None, None, text)` — never raises.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != _FRONTMATTER_DELIM:
        return None, None, text
    try:
        end_index = lines.index(_FRONTMATTER_DELIM, 1)
    except ValueError:
        return None, None, text
    frontmatter_lines = lines[1:end_index]
    body = "\n".join(lines[end_index + 1 :]).strip("\n")
    name = _extract_scalar(frontmatter_lines, "name")
    description = _extract_scalar(frontmatter_lines, "description")
    return name, description, body


def _classify_origin(identifier: str, configs: list[VendorConfig]) -> tuple[str, str | None]:
    """`identifier` is a Skill's directory name (`.claude/skills/<dir>/
    SKILL.md`) or an `.mdc` file's stem — both follow the same naming
    convention codecompass itself writes (`_TOOL_SKILL_DIR_NAME`,
    `_vendor_skill_name`). Returns `(origin, vendor_name)`.
    """
    if identifier == _TOOL_SKILL_DIR_NAME:
        return "codecompass_tool", None
    for config in configs:
        if identifier == _vendor_skill_name(config):
            return "codecompass_vendor", config.name
    return "third_party", None


_DISCOVERY_COMMAND_PATH = Path(".claude") / "commands" / "discovery.md"


def scan_skills(project_root: Path, configs: list[VendorConfig]) -> list[DocArtifactRow]:
    """Globs `.claude/skills/**/SKILL.md` (`kind='skill'`) and
    `.cursor/rules/*.mdc` (`kind='cursor_mdc'`), extracting `name`/
    `description` from each file's frontmatter and classifying `origin` by
    directory name / filename-prefix against codecompass's own naming
    convention — anything not matching `configs` is `third_party`. Also
    indexes `.claude/commands/discovery.md` (`kind='slash_command'`,
    `origin='codecompass_tool'`, Phase 17), if present, so `/discovery`
    participates in the graph like any other codecompass-generated
    artifact — e.g. so Phase 18's `undo` can find it the same way it finds
    every other generated file.
    """
    rows: list[DocArtifactRow] = []

    skills_root = project_root / ".claude" / "skills"
    for skill_path in sorted(skills_root.glob("**/SKILL.md")):
        name, description, _ = _parse_skill_file(skill_path.read_text(encoding="utf-8"))
        origin, vendor_name = _classify_origin(skill_path.parent.name, configs)
        rows.append(
            DocArtifactRow(
                path=skill_path.relative_to(project_root).as_posix(),
                kind="skill",
                origin=origin,
                vendor_name=vendor_name,
                name=name,
                description=description,
            )
        )

    rules_dir = project_root / ".cursor" / "rules"
    for mdc_path in sorted(rules_dir.glob("*.mdc")):
        name, description, _ = _parse_skill_file(mdc_path.read_text(encoding="utf-8"))
        origin, vendor_name = _classify_origin(mdc_path.stem, configs)
        rows.append(
            DocArtifactRow(
                path=mdc_path.relative_to(project_root).as_posix(),
                kind="cursor_mdc",
                origin=origin,
                vendor_name=vendor_name,
                name=name,
                description=description,
            )
        )

    discovery_path = project_root / _DISCOVERY_COMMAND_PATH
    if discovery_path.exists():
        name, description, _ = _parse_skill_file(discovery_path.read_text(encoding="utf-8"))
        rows.append(
            DocArtifactRow(
                path=discovery_path.relative_to(project_root).as_posix(),
                kind="slash_command",
                origin="codecompass_tool",
                vendor_name=None,
                name=name,
                description=description,
            )
        )

    return rows


def build_skill_mentions_edges(
    skill_doc_artifacts: list[DocArtifactRow],
    configs: list[VendorConfig],
    source_file_rows: list[SourceFileRow],
    project_root: Path,
) -> list[SkillMentionEdgeRow]:
    """For each skill's body text (not just frontmatter), word-boundary-
    match against every tracked vendor name and every tracked project
    source file's basename — a presence heuristic ("mechanically
    mentions"), same posture as `doc_mapping.build_documents_edges`,
    explicitly not a claim the skill is *about* that vendor/file.

    Word-boundary (`\\b<name>\\b`), not substring, matching — a naive
    substring match risks false positives on any vendor/file name that
    collides with common English words (`rich`, `six`) or is short enough
    to appear inside an unrelated word. Case-sensitive, matching this
    project's own generated Skill content being lowercase-consistent.
    """
    vendor_names = [config.name for config in configs]
    basenames_to_paths: dict[str, list[str]] = defaultdict(list)
    for source_file in source_file_rows:
        basenames_to_paths[Path(source_file.path).name].append(source_file.path)

    edges: list[SkillMentionEdgeRow] = []
    for row in skill_doc_artifacts:
        text = (project_root / row.path).read_text(encoding="utf-8")
        _, _, body = _parse_skill_file(text)

        for vendor_name in vendor_names:
            if re.search(rf"\b{re.escape(vendor_name)}\b", body):
                edges.append(
                    SkillMentionEdgeRow(doc_artifact_path=row.path, vendor_name=vendor_name)
                )

        for basename, paths in basenames_to_paths.items():
            if re.search(rf"\b{re.escape(basename)}\b", body):
                for path in paths:
                    edges.append(
                        SkillMentionEdgeRow(doc_artifact_path=row.path, source_file_path=path)
                    )

    return edges
