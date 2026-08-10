"""Per-ecosystem, no-AI symbol and purpose extraction.

Shared by the ecosystem adapters' API-surface extraction (Phase 2) and
`filetree.py`'s per-file purpose annotations and flat symbol index
(Phase 3). See architecture/overview.md's "Tree generation" section and
planning/phase-3-tree-generation.md's Design decisions.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from depcompass.core import Ecosystem

_RUST_PUB_PREFIXES = ("pub fn ", "pub struct ", "pub enum ", "pub trait ")
_NPM_EXPORT_RE = re.compile(
    r"^export\s+(?:default\s+)?(?:declare\s+)?"
    r"(?:function|class|interface|const|type|enum)\s+(\w+)"
)
_GENERIC_COMMENT_MARKERS = ("#", "//", "/*", '"""', "'''")


@dataclass
class Symbol:
    """One top-level, no-AI-extracted symbol from a single source file."""

    name: str
    purpose: str | None = None


def extract_rust_symbols(path: Path) -> list[Symbol]:
    """Coarse, line-based scan for `pub fn`/`pub struct`/`pub enum`/
    `pub trait` items, pairing each with an immediately preceding `///`
    doc-comment block if present. Generalizes the extraction the Cargo
    adapter used privately in Phase 2. Unlike that string-signature-based
    version, only the item's *name* is captured, so multi-line signatures
    (generic bounds/`where` clauses spanning lines) no longer cause a
    truncated result — the coarse-scan limitation that mattered when the
    full signature line was captured doesn't apply to name extraction.
    """
    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        return []
    symbols: list[Symbol] = []
    doc_lines: list[str] = []
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("///"):
            doc_lines.append(stripped.removeprefix("///").strip())
            continue
        if stripped.startswith(_RUST_PUB_PREFIXES):
            name = _rust_item_name(stripped)
            purpose = " ".join(doc_lines) if doc_lines else None
            symbols.append(Symbol(name=name, purpose=purpose))
        doc_lines = []
    return symbols


def _rust_item_name(signature_line: str) -> str:
    rest = signature_line
    for prefix in _RUST_PUB_PREFIXES:
        if rest.startswith(prefix):
            rest = rest[len(prefix) :]
            break
    match = re.match(r"\w+", rest)
    return match.group(0) if match else rest.strip()


def extract_python_symbols(path: Path) -> list[Symbol]:
    """`ast`-based scan of a single `.py` file's top-level `def`/`class`
    statements, pairing each with its docstring if present. Generalizes
    the per-node loop the Python adapter used privately in Phase 2 (there,
    hardcoded to `__init__.py` only) to any file. Does not extract
    `__all__` — that's module-level data, not a symbol, and stays adapter-
    local (see `adapters/python.py`).
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []
    symbols: list[Symbol] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            symbols.append(Symbol(name=node.name, purpose=ast.get_docstring(node)))
    return symbols


def extract_npm_symbols(path: Path) -> list[Symbol]:
    """Regex scan of a single `.d.ts` file for `export function/class/
    interface/const/type/enum <name>` declarations, pairing each with a
    leading `/** ... */` JSDoc block's first content line if present. No
    equivalent existed in Phase 2 — the npm adapter's `readme_and_api_surface`
    dumps whole `.d.ts` file contents rather than parsing declarations out
    of them; this is purely new, for `filetree.py`'s use.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    symbols: list[Symbol] = []
    pending_doc: str | None = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("/**"):
            inline = stripped.removeprefix("/**").removesuffix("*/").strip()
            pending_doc = inline or None
            continue
        if stripped.startswith("*"):
            if pending_doc is None:
                text = stripped.lstrip("*").strip()
                if text and not text.startswith("@"):
                    pending_doc = text
            continue
        if not stripped:
            continue
        match = _NPM_EXPORT_RE.match(stripped)
        if match:
            symbols.append(Symbol(name=match.group(1), purpose=pending_doc))
        pending_doc = None
    return symbols


def extract_symbols_for_file(path: Path, ecosystem: Ecosystem) -> list[Symbol]:
    """Dispatch to the matching ecosystem extractor, gated on file suffix
    so e.g. a README.md inside an npm package isn't fed to the `.d.ts`
    parser. Returns `[]` for files no ecosystem-specific extractor claims.
    """
    if ecosystem is Ecosystem.PYTHON and path.suffix == ".py":
        return extract_python_symbols(path)
    if ecosystem is Ecosystem.CARGO and path.suffix == ".rs":
        return extract_rust_symbols(path)
    if ecosystem is Ecosystem.NPM and path.name.endswith(".d.ts"):
        return extract_npm_symbols(path)
    return []


def purpose_for_file(path: Path, ecosystem: Ecosystem) -> str | None:
    """One-line purpose annotation for a single file, for FILETREE.md.
    Prefers the first ecosystem-specific symbol with a purpose; falls back
    to a generic leading-comment-marker scan for files no ecosystem parser
    claims, or where the parser found nothing.
    """
    for symbol in extract_symbols_for_file(path, ecosystem):
        if symbol.purpose:
            return symbol.purpose
    return _generic_leading_comment(path)


def _generic_leading_comment(path: Path) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        for marker in _GENERIC_COMMENT_MARKERS:
            if not stripped.startswith(marker):
                continue
            text = stripped.removeprefix(marker)
            text = text.removesuffix("*/") if marker == "/*" else text
            text = text.removesuffix(marker) if marker in ('"""', "'''") else text
            return text.strip() or None
        return None
    return None
