"""Deterministic FILETREE.md (+ filetree.json) rendering, plus a flat
greppable symbol index, from a vendor's source directory.

No AI calls, runs regardless of `depth`. See architecture/overview.md's
"Tree generation" section and planning/phase-3-tree-generation.md.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

from codecompass.core import Ecosystem
from codecompass.symbols import extract_symbols_for_file, purpose_for_file

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


def _is_pruned_dir(part: str, prune_dirs: Iterable[str]) -> bool:
    return part in prune_dirs


def _is_pruned_file(path: Path, prune_globs: Iterable[str]) -> bool:
    return any(path.match(glob) for glob in prune_globs)


def iter_source_files(
    root: Path,
    *,
    prune_dirs: Iterable[str] = _PRUNE_DIR_NAMES,
    prune_globs: Iterable[str] = _PRUNE_FILE_GLOBS,
) -> Iterator[Path]:
    """Deterministic (sorted), pruned walk of `root`. Directories named in
    `prune_dirs` and files matching `prune_globs` are skipped — noise that
    adds tokens without adding navigation value. Defaults to this module's
    own vendor-source-oriented prune sets, so the three existing callers
    below are unaffected; `usage.py` (Phase 11) reuses this same walk shape
    for the *consuming project's* source tree with its own, different
    prune set (a project's own tests are real usage signal, unlike a
    vendor's).
    """
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root).parts[:-1]
        if any(_is_pruned_dir(part, prune_dirs) for part in rel_parts):
            continue
        if _is_pruned_file(path, prune_globs):
            continue
        yield path


def render_filetree_markdown(
    root: Path, ecosystem: Ecosystem, *, action_pointer: tuple[str, str] | None = None
) -> str:
    """No version numbers (that's DEPTREE.md's job); a one-line purpose
    annotation per file where inferable.

    `action_pointer`, when given, is `(relative_file_path, note)` from
    Phase 5's gap analysis — the matching file's line gets an appended
    `← ACTION TARGET: <note>` marker, cross-linking FILETREE.md directly
    to the gap-analysis finding instead of leaving a two-hop lookup
    (deferred in Phase 3, closed here).
    """
    pointer_path, pointer_note = action_pointer if action_pointer else (None, None)
    lines: list[str] = []
    for path in iter_source_files(root):
        rel = path.relative_to(root).as_posix()
        purpose = purpose_for_file(path, ecosystem)
        line = f"- {rel}  — {purpose}" if purpose else f"- {rel}"
        if rel == pointer_path:
            line += f"  ← ACTION TARGET: {pointer_note}"
        lines.append(line)
    return "\n".join(lines)


def render_filetree_json(
    root: Path, ecosystem: Ecosystem, *, action_pointer: tuple[str, str] | None = None
) -> dict:
    """Machine-readable mirror of `render_filetree_markdown`'s walk,
    including the same `action_pointer` cross-link when given.
    """
    pointer_path, pointer_note = action_pointer if action_pointer else (None, None)
    entries = []
    for path in iter_source_files(root):
        rel = path.relative_to(root).as_posix()
        entry = {"path": rel, "purpose": purpose_for_file(path, ecosystem)}
        if rel == pointer_path:
            entry["action_pointer"] = pointer_note
        entries.append(entry)
    return {"entries": entries}


def build_symbol_index(root: Path, ecosystem: Ecosystem) -> str:
    """Flat `name -> path` symbol index across every file in `root`,
    closer to a ctags model than the nested file tree — for "jump
    straight to the thing" on a targeted question. Capped at
    `_SYMBOL_INDEX_CAP` entries with an explicit "+N more" notice if
    exceeded — never a silent truncation.
    """
    entries: list[tuple[str, str]] = []
    for path in iter_source_files(root):
        rel = path.relative_to(root).as_posix()
        for symbol in extract_symbols_for_file(path, ecosystem):
            entries.append((symbol.name, rel))

    lines = [f"{name} -> {path}" for name, path in entries[:_SYMBOL_INDEX_CAP]]
    remaining = len(entries) - _SYMBOL_INDEX_CAP
    if remaining > 0:
        lines.append(f"... +{remaining} more, not shown")
    return "\n".join(lines)
