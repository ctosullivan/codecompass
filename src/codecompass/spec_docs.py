"""Detects a project's own human-authored spec documentation — README,
ARCHITECTURE.md, `docs/**/*.md`, `decisions/**/*.md`, etc. — as
`doc_artifacts` rows (`kind='spec_doc'`, `origin='project'`), distinct
from codecompass's own generated dependency docs (`claude_md`/`overview`,
`origin='codecompass_vendor'`) and generated/third-party Skills
(`skill`/`cursor_mdc`/`slash_command`). Mechanical only: a fixed default
glob set, no AI call, same posture as `usage.py`/`doc_mapping.py`/
`skill_scan.py`. See
planning/phase-21-spec-doc-detection-and-relationship-graph.md.
"""

from __future__ import annotations

from pathlib import Path

from codecompass.graph import DocArtifactRow
from codecompass.usage import _PROJECT_PRUNE_DIR_NAMES

# No `vendor.toml` configurability yet (see the phase plan's Design
# decisions) — ship with this fixed default list, add configurability only
# once a real project shows it's wrong for it.
_DEFAULT_GLOBS = (
    "README.md",
    "ARCHITECTURE.md",
    "REQUIREMENTS.md",
    "PRD.md",
    "docs/**/*.md",
    "architecture/**/*.md",
    "decisions/**/*.md",
    "spec/**/*.md",
    "specs/**/*.md",
    "rfcs/**/*.md",
    "*.spec.md",
)

# Root-level-only exclusions: a log (CHANGELOG.md), process docs
# (CONTRIBUTING.md), license text, and this project's own governance file
# (CLAUDE.md, already special-cased elsewhere in this codebase) — none of
# these are a spec even though some sit right next to real specs at the
# project root.
_EXCLUDED_ROOT_NAMES = {"CHANGELOG.md", "CONTRIBUTING.md", "CLAUDE.md"}


def _is_pruned(rel_path: Path) -> bool:
    """Mirrors `usage.py`'s prune posture for the *consuming* project's
    own tree — dropping only build/dependency/tool-config noise
    (`vendor/`, `.claude/`, `.cursor/`, `node_modules/`, `.git/`,
    `.venv/`, `dist/`, `build/`, etc.), reusing `_PROJECT_PRUNE_DIR_NAMES`
    rather than a third copy of that list.
    """
    return any(part in _PROJECT_PRUNE_DIR_NAMES for part in rel_path.parts[:-1])


def _is_excluded(rel_path: Path) -> bool:
    if rel_path.parent != Path("."):
        return False
    if rel_path.name in _EXCLUDED_ROOT_NAMES:
        return True
    return rel_path.name.startswith("LICENSE")


def scan_spec_docs(project_root: Path) -> list[DocArtifactRow]:
    """Globs the fixed default spec-doc pattern set rooted at
    `project_root`, excluding `CHANGELOG.md`/`CONTRIBUTING.md`/`LICENSE*`/
    root `CLAUDE.md` and anything under `usage._PROJECT_PRUNE_DIR_NAMES`.
    Deterministic, sorted output; a path matching more than one glob
    pattern is only ever recorded once.
    """
    matched: set[Path] = set()
    for pattern in _DEFAULT_GLOBS:
        for path in project_root.glob(pattern):
            if not path.is_file():
                continue
            rel = path.relative_to(project_root)
            if _is_pruned(rel) or _is_excluded(rel):
                continue
            matched.add(rel)

    return [
        DocArtifactRow(path=rel.as_posix(), kind="spec_doc", origin="project")
        for rel in sorted(matched)
    ]
