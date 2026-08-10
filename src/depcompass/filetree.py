"""Deterministic FILETREE.md (+ filetree.json) rendering, plus a flat
greppable symbol index, from a vendor's source directory.

No AI calls, runs regardless of `depth`. See architecture/overview.md's
"Tree generation" section and planning/phase-3-tree-generation.md.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from depcompass.core import Ecosystem
from depcompass.symbols import extract_symbols_for_file, purpose_for_file

_PRUNE_DIR_NAMES = {
    "dist",
    "build",
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "test",
    "tests",
    "__tests__",
    "fixtures",
}
_PRUNE_FILE_GLOBS = ("*.min.js", "*.map")
_SYMBOL_INDEX_CAP = 200


def _is_pruned_dir(part: str) -> bool:
    return part in _PRUNE_DIR_NAMES


def _is_pruned_file(path: Path) -> bool:
    return any(path.match(glob) for glob in _PRUNE_FILE_GLOBS)


def _iter_files(root: Path) -> Iterator[Path]:
    """Deterministic (sorted), pruned walk of `root`. Directories in
    `_PRUNE_DIR_NAMES` and files matching `_PRUNE_FILE_GLOBS` are skipped
    — noise that adds tokens without adding navigation value.
    """
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root).parts[:-1]
        if any(_is_pruned_dir(part) for part in rel_parts):
            continue
        if _is_pruned_file(path):
            continue
        yield path


def render_filetree_markdown(root: Path, ecosystem: Ecosystem) -> str:
    """No version numbers (that's DEPTREE.md's job); a one-line purpose
    annotation per file where inferable.
    """
    lines: list[str] = []
    for path in _iter_files(root):
        rel = path.relative_to(root).as_posix()
        purpose = purpose_for_file(path, ecosystem)
        lines.append(f"- {rel}  — {purpose}" if purpose else f"- {rel}")
    return "\n".join(lines)


def render_filetree_json(root: Path, ecosystem: Ecosystem) -> dict:
    """Machine-readable mirror of `render_filetree_markdown`'s walk."""
    entries = [
        {"path": path.relative_to(root).as_posix(), "purpose": purpose_for_file(path, ecosystem)}
        for path in _iter_files(root)
    ]
    return {"entries": entries}


def build_symbol_index(root: Path, ecosystem: Ecosystem) -> str:
    """Flat `name -> path` symbol index across every file in `root`,
    closer to a ctags model than the nested file tree — for "jump
    straight to the thing" on a targeted question. Capped at
    `_SYMBOL_INDEX_CAP` entries with an explicit "+N more" notice if
    exceeded — never a silent truncation.
    """
    entries: list[tuple[str, str]] = []
    for path in _iter_files(root):
        rel = path.relative_to(root).as_posix()
        for symbol in extract_symbols_for_file(path, ecosystem):
            entries.append((symbol.name, rel))

    lines = [f"{name} -> {path}" for name, path in entries[:_SYMBOL_INDEX_CAP]]
    remaining = len(entries) - _SYMBOL_INDEX_CAP
    if remaining > 0:
        lines.append(f"... +{remaining} more, not shown")
    return "\n".join(lines)
