"""Project-source-side import detection.

`symbols.py`'s extractors run in the opposite direction — pulling symbols
*out of* a vendor's own source. Nothing before this module inspects the
*consuming* project's source at all. See
planning/phase-11-project-source-usage-detection.md's Design decisions for
why this module's prune set deliberately differs from `filetree.py`'s.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from codecompass.core import Ecosystem, VendorConfig
from codecompass.filetree import iter_source_files

# Build/dependency noise only, no test exclusion — unlike
# `filetree._PRUNE_DIR_NAMES`, a project's own test files importing a
# vendor is real usage signal and must not be pruned away.
#
# `vendor` is pruned for a different reason: since Phase 13/`decisions/
# 0033`, every tracked vendor's own upstream source is cloned to
# `vendor/<name>/src/` unconditionally, at the project root — inside
# this walk's `root` (`project_root`) unless excluded. A vendor's own
# source very often references its own package name somewhere (its own
# absolute self-imports, docs code samples, setup/build scripts), which
# would otherwise register as a false-positive "the project uses this
# vendor" `uses_edges` row for nearly every tracked vendor on every
# run — silently defeating usage-driven enrichment selection
# (`decisions/0031`) by making Phase B (Phase 15) consider almost
# everything "used" regardless of whether the *consuming* project's own
# code actually imports it. Found via Phase 15's first real end-to-end
# CLI exercise of this path — no earlier phase's tests caught it because
# none combined a real clone with a real graph rebuild against a project
# fixture.
_PROJECT_PRUNE_DIR_NAMES = {
    "node_modules",
    "dist",
    "build",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "vendor",
}

_NPM_SOURCE_SUFFIXES = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")

_NPM_NAMED_IMPORT_RE = re.compile(
    r'import\s*\{([^}]*)\}\s*from\s*[\'"]([^\'"]+)[\'"]'
)
_NPM_DEFAULT_IMPORT_RE = re.compile(r'import\s+\w+\s+from\s*[\'"]([^\'"]+)[\'"]')
_NPM_NAMESPACE_IMPORT_RE = re.compile(
    r'import\s*\*\s*as\s+\w+\s+from\s*[\'"]([^\'"]+)[\'"]'
)
_NPM_REQUIRE_RE = re.compile(r'require\(\s*[\'"]([^\'"]+)[\'"]\s*\)')

# A leading `\w+` vendor segment, any number of `::`-separated middle
# segments, then a final `::*` (wildcard, vendor-level), a final `::Symbol`
# (symbol-level), or a bare `use vendor;` (vendor-level). Deliberately
# generalizes the plan's `use crate::Symbol;` shorthand to a real crate
# name in the vendor position — a literal `use crate::foo::Bar;`
# (Rust's own within-crate path syntax) still matches this pattern with
# vendor="crate", which simply never matches a tracked vendor name and is
# filtered out downstream, same as any other untracked-package import.
_RUST_USE_WILDCARD_RE = re.compile(r"use\s+(\w+)(?:::\w+)*::\*\s*;")
_RUST_USE_SYMBOL_RE = re.compile(r"use\s+(\w+)(?:::\w+)*::(\w+)\s*;")
_RUST_USE_BARE_RE = re.compile(r"use\s+(\w+)\s*;")


@dataclass(frozen=True)
class DetectedImport:
    """One detected import in a project source file. `symbol_name=None` is
    the vendor-level fallback — a detected import that doesn't resolve to
    one specific bound name (e.g. `import rich`, `use serde::*;`).
    """

    vendor: str
    symbol_name: str | None
    line: int


def detect_python_imports(path: Path) -> list[DetectedImport]:
    """`ast`-based scan for `import` (vendor-level, plus an attribute-
    resolution upgrade pass — see below) and `from ... import ...` (vendor
    candidate is the first dotted component of `module`, one
    `DetectedImport` per bound name). Relative imports (`from . import x`,
    `from .sibling import x`) are skipped outright — they can never refer
    to an external vendor by definition, only to the project's own package
    structure. Walks the whole tree (not just top-level statements), so
    imports nested inside a function/class body still count as usage.
    Never raises — a file that fails to parse returns `[]`, the same
    convention `symbols.py`'s extractors already follow.

    Phase 26: a plain `import X` (or `import X as alias`) always records
    its vendor-level `DetectedImport(symbol_name=None)` as before — that
    fact doesn't change. Additionally, a second pass over the same tree
    looks for `ast.Attribute` nodes whose value is a bare `ast.Name`
    matching one of this file's bound import names (`alias.asname or
    alias.name`'s top-level component) and emits an *additional*
    `DetectedImport(vendor=<that name's vendor>, symbol_name=<the
    attribute's .attr>, line=<the Attribute node's line>)` per match —
    `import anthropic` + `anthropic.Anthropic(...)` upgrades to a
    symbol-level candidate alongside the untouched vendor-level one. Only
    the *immediate* attribute off the bound name resolves: for `X.sub.Attr`
    the inner `Attribute` (`value` is the bare `Name`) yields `sub`, not
    `Attr` — deeper chains aren't walked, mirroring `ImportFrom`'s own
    first-dotted-component-only precedent rather than guessing at a leaf
    name real type inference would be needed to get right.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []
    detected: list[DetectedImport] = []
    bound_vendors: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                vendor = alias.name.split(".")[0]
                detected.append(DetectedImport(vendor=vendor, symbol_name=None, line=node.lineno))
                bound_vendors[alias.asname or vendor] = vendor
        elif isinstance(node, ast.ImportFrom):
            if node.module is None or node.level > 0:
                continue
            vendor = node.module.split(".")[0]
            for alias in node.names:
                detected.append(
                    DetectedImport(vendor=vendor, symbol_name=alias.name, line=node.lineno)
                )
    if bound_vendors:
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id in bound_vendors
            ):
                detected.append(
                    DetectedImport(
                        vendor=bound_vendors[node.value.id],
                        symbol_name=node.attr,
                        line=node.lineno,
                    )
                )
    return detected


def detect_npm_imports(path: Path) -> list[DetectedImport]:
    """Regex scan over the whole file text for `import { A, B } from
    "pkg"` (named — one entry per name, an ` as alias` suffix stripped so
    the captured name matches the vendor's *declared* export, not the
    project's local bound name), `import Default from "pkg"` / `import *
    as ns from "pkg"` / `require("pkg")` (vendor-level only, no symbol
    candidate) — matching the coarse-regex posture already accepted for
    `extract_npm_symbols`. Never raises.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    detected: list[DetectedImport] = []

    for match in _NPM_NAMED_IMPORT_RE.finditer(text):
        names_blob, vendor = match.groups()
        line = text.count("\n", 0, match.start()) + 1
        for raw_name in names_blob.split(","):
            name = raw_name.strip()
            if not name:
                continue
            name = name.split(" as ")[0].strip()
            if name:
                detected.append(DetectedImport(vendor=vendor, symbol_name=name, line=line))

    for pattern in (_NPM_DEFAULT_IMPORT_RE, _NPM_NAMESPACE_IMPORT_RE, _NPM_REQUIRE_RE):
        for match in pattern.finditer(text):
            vendor = match.group(1)
            line = text.count("\n", 0, match.start()) + 1
            detected.append(DetectedImport(vendor=vendor, symbol_name=None, line=line))

    return detected


def detect_rust_imports(path: Path) -> list[DetectedImport]:
    """Regex scan over the whole file text for `use vendor::Symbol;`
    (symbol candidate = `Symbol`) vs. `use vendor::*;` / `use vendor;`
    (vendor-level only). Never raises.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    detected: list[DetectedImport] = []

    # The three patterns are mutually exclusive by construction: the bare
    # pattern requires a `;` immediately (mod whitespace) after the vendor
    # name, which a `::`-qualified path never satisfies, and the wildcard
    # pattern's trailing `*` never satisfies the symbol pattern's trailing
    # `\w+` — so no `use` statement can match more than one of them.
    for pattern in (_RUST_USE_WILDCARD_RE, _RUST_USE_SYMBOL_RE, _RUST_USE_BARE_RE):
        for match in pattern.finditer(text):
            vendor = match.group(1)
            symbol = match.group(2) if pattern is _RUST_USE_SYMBOL_RE else None
            line = text.count("\n", 0, match.start()) + 1
            detected.append(DetectedImport(vendor=vendor, symbol_name=symbol, line=line))

    return detected


def detect_imports_for_file(path: Path, ecosystem: Ecosystem) -> list[DetectedImport]:
    """Dispatch to the matching ecosystem detector, gated on file suffix —
    mirrors `symbols.extract_symbols_for_file`'s dispatch shape. Returns
    `[]` for files no ecosystem-specific detector claims.
    """
    if ecosystem is Ecosystem.PYTHON and path.suffix == ".py":
        return detect_python_imports(path)
    if ecosystem is Ecosystem.CARGO and path.suffix == ".rs":
        return detect_rust_imports(path)
    if ecosystem is Ecosystem.NPM and path.suffix in _NPM_SOURCE_SUFFIXES:
        return detect_npm_imports(path)
    return []


def resolve_project_usage(
    project_root: Path, configs: list[VendorConfig]
) -> list[tuple[str, DetectedImport]]:
    """Walk `project_root` via `filetree.iter_source_files(project_root,
    prune_dirs=_PROJECT_PRUNE_DIR_NAMES)`, run every ecosystem's detector
    against each file (each detector is itself gated on file suffix, so at
    most one produces results for any given file), and filter to only
    names matching a tracked vendor (`configs`) — an import of an
    untracked package is not this project's concern. Returns
    `(relative_file_path, DetectedImport)` pairs; symbol-name-to-
    `symbol_id` resolution happens in `sync.py` — this module has no
    `graph.py` dependency, keeping it independently unit-testable.
    """
    tracked_names = {c.name for c in configs}
    results: list[tuple[str, DetectedImport]] = []
    for path in iter_source_files(project_root, prune_dirs=_PROJECT_PRUNE_DIR_NAMES):
        rel = path.relative_to(project_root).as_posix()
        for ecosystem in Ecosystem:
            for detected in detect_imports_for_file(path, ecosystem):
                if detected.vendor in tracked_names:
                    results.append((rel, detected))
    return results
