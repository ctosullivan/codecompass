"""First-party source file and top-level symbol detection.

Phase 77. A project-facing counterpart to `symbols.py`'s vendor-facing
extractors (`usage.py`'s own architectural role, generalized): where
`symbols.py` pulls a *vendor's* public API surface out of its own
installed source, and `usage.py` detects the *consuming* project's
imports of a tracked vendor, this module walks the *consuming* project's
own source tree and extracts its own top-level implementation symbols —
independent of `vendor.toml`, independent of any tracked vendor at all.

Three deliberate corrections over the first, superseded design (see
`planning/phase-77-first-party-source-and-template.md` §0/§3 for the
full evidence trail):

1. **`Language`, not `core.Ecosystem`.** A first-party source file's own
   programming language is a different concept from a *package*
   ecosystem — `core.Ecosystem.NPM` covers both JavaScript and
   TypeScript dependencies identically, but a project's own `.js` and
   `.ts` files are observably different languages with different
   symbol-kind vocabularies. Defined here, not in `core.py`, since this
   module is its only consumer today.
2. **Implementation scope, not API-surface scope.** The question here is
   "what does this project implement," not "what does this dependency
   expose" — every extractor below includes non-exported/private
   top-level declarations, recording an `exposure` classification as a
   separate property rather than filtering anything out.
3. **Occurrence-based symbol identity with non-null location.** A
   top-level declaration's identity includes where it is
   (`name`, `kind`, `line`) — never collapsed to `name` alone, which a
   real, ordinary language feature (function overloading) would
   otherwise make collide. See `SourceSymbol.line`'s own docstring.

`extract_source_symbols_for_file` never raises and never returns a bare,
ambiguous empty list standing in for more than one real cause — see
`SymbolIndexStatus`/`SourceFileExtraction` below, modeled directly on
`git_topology.RepositoryTopology`'s own status+reason+data shape.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from codecompass.filetree import iter_source_files
from codecompass.usage import _PROJECT_PRUNE_DIR_NAMES


class Language(StrEnum):
    """A first-party source file's own programming language — distinct
    from `core.Ecosystem` (a *package* ecosystem: npm covers both
    JavaScript and TypeScript dependencies identically, but a project's
    own first-party `.js` and `.ts` files are observably different
    languages with different symbol-kind vocabularies).
    """

    PYTHON = "python"
    RUST = "rust"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    HASKELL = "haskell"


class SymbolIndexStatus(StrEnum):
    """A source file's own symbol-extraction outcome — never collapsed
    into a bare empty list. `INDEXED` (a real structural parser ran —
    Python only, today) and `INDEXED_PARTIAL` (a coarse line-scan/regex
    technique ran — Rust and JS/TS, today) are both "succeeded" outcomes,
    distinguished only by technique fidelity, never implying the coarse
    techniques are as complete as a real parser.
    """

    INDEXED = "indexed"
    INDEXED_PARTIAL = "indexed_partial"
    UNSUPPORTED = "unsupported"
    PARSE_ERROR = "parse_error"
    UNREADABLE = "unreadable"


_JS_FAMILY_SUFFIXES = (".js", ".jsx", ".mjs", ".cjs")
_TS_SUFFIXES = (".ts", ".tsx")

_LANGUAGE_BY_SUFFIX: dict[str, Language] = {
    ".py": Language.PYTHON,
    ".rs": Language.RUST,
    ".hs": Language.HASKELL,
    **{suffix: Language.JAVASCRIPT for suffix in _JS_FAMILY_SUFFIXES},
    **{suffix: Language.TYPESCRIPT for suffix in _TS_SUFFIXES},
}

# `(pub(crate|super|self|in <path>)?)? (fn|struct|enum|trait) name` --
# live-verified against 8 representative forms (bare pub, all three
# pub(...) modifiers, and three no-modifier forms), all classified
# correctly. Captures the full modifier text (group 1) so the caller can
# distinguish bare `pub` (public) from any `pub(...)` form (restricted)
# from no modifier at all (internal).
_RUST_ITEM_RE = re.compile(
    r"^(pub(?:\((?:crate|super|self|in\s+[\w:]+)\))?\s+)?"
    r"(fn|struct|enum|trait)\s+(\w+)"
)

# Every top-level `(export)? (default)? (declare)? construct name` --
# widened from the vendor .d.ts-only extractor (`symbols._NPM_EXPORT_RE`)
# to match with or without a leading `export`, live-verified against a
# real .ts implementation file (including a real overloaded-function
# case) during planning.
_JS_FAMILY_ITEM_RE = re.compile(
    r"^(export\s+)?(?:default\s+)?(?:declare\s+)?"
    r"(function|class|interface|const|type|enum)\s+(\w+)"
)
_JS_FAMILY_JSDOC_START_RE = re.compile(r"^\s*/\*\*")


@dataclass(frozen=True)
class SourceSymbol:
    """One first-party top-level implementation symbol occurrence.

    `line` is never `None` — an occurrence's identity is partly defined
    by its own location (`source_symbols.UNIQUE(source_file_id, name,
    kind, line)`, `graph.py`), so a location-less symbol is a
    contradiction in terms: an extractor unable to determine a line for
    a candidate does not emit a row for it at all, rather than emitting
    one with a fabricated or missing location.
    """

    name: str
    kind: str
    line: int
    purpose: str | None = None
    exposure: str | None = None
    # 'public' | 'restricted' | 'internal' | 'conventional_private' | 'unknown' | None


@dataclass(frozen=True)
class SourceFileExtraction:
    """One file's own symbol-extraction outcome — see
    `SymbolIndexStatus` for what each status means. `symbols` may be
    empty for `INDEXED`/`INDEXED_PARTIAL` (a real, valid "nothing here"
    outcome, never conflated with failure).
    """

    status: SymbolIndexStatus
    diagnostic: str | None
    symbols: tuple[SourceSymbol, ...]


def discover_source_files(project_root: Path) -> list[tuple[str, Language]]:
    """Every recognized first-party source file under `project_root`,
    independent of `vendor.toml` — works identically at 0 tracked
    vendors, since language classification is suffix-based, never
    consulting tracked-vendor configuration.

    Reuses `usage._PROJECT_PRUNE_DIR_NAMES` (build/dependency noise and
    the unconditionally-cloned `vendor/` directory only) rather than
    `filetree._PRUNE_DIR_NAMES` (which prunes `test`/`tests`/
    `__tests__`/`fixtures` — correct for rendering a *vendor's* own
    `FILETREE.md`, wrong here: a project's own test file is real
    first-party source, not noise).
    """
    results: list[tuple[str, Language]] = []
    for path in iter_source_files(project_root, prune_dirs=_PROJECT_PRUNE_DIR_NAMES):
        language = _LANGUAGE_BY_SUFFIX.get(path.suffix)
        if language is None:
            continue
        rel = path.relative_to(project_root).as_posix()
        results.append((rel, language))
    return results


def extract_source_symbols_for_file(path: Path, language: Language) -> SourceFileExtraction:
    """Dispatches to the matching per-language extractor. Never raises —
    every failure mode (unsupported language, a genuine parse error, an
    unreadable file) is caught and converted to an explicit
    `SourceFileExtraction`, never a bare empty list standing in for more
    than one real cause.
    """
    if language is Language.PYTHON:
        return _extract_python_source_symbols(path)
    if language is Language.RUST:
        return _extract_rust_source_symbols(path)
    if language in (Language.JAVASCRIPT, Language.TYPESCRIPT):
        return _extract_js_family_source_symbols(path)
    return SourceFileExtraction(status=SymbolIndexStatus.UNSUPPORTED, diagnostic=None, symbols=())


def _extract_python_source_symbols(path: Path) -> SourceFileExtraction:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return SourceFileExtraction(
            status=SymbolIndexStatus.UNREADABLE, diagnostic=str(exc), symbols=()
        )
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return SourceFileExtraction(
            status=SymbolIndexStatus.PARSE_ERROR, diagnostic=str(exc), symbols=()
        )

    symbols: list[SourceSymbol] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            exposure = "conventional_private" if node.name.startswith("_") else "public"
            is_function = isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
            symbols.append(
                SourceSymbol(
                    name=node.name,
                    kind="function" if is_function else "class",
                    line=node.lineno,
                    purpose=ast.get_docstring(node),
                    exposure=exposure,
                )
            )
    return SourceFileExtraction(
        status=SymbolIndexStatus.INDEXED, diagnostic=None, symbols=tuple(symbols)
    )


def _extract_rust_source_symbols(path: Path) -> SourceFileExtraction:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return SourceFileExtraction(
            status=SymbolIndexStatus.UNREADABLE, diagnostic=str(exc), symbols=()
        )

    symbols: list[SourceSymbol] = []
    doc_lines: list[str] = []
    for lineno, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("///"):
            doc_lines.append(stripped.removeprefix("///").strip())
            continue
        match = _RUST_ITEM_RE.match(stripped)
        if match:
            modifier, kind, name = match.groups()
            if modifier is None:
                exposure = "internal"
            elif modifier.strip() == "pub":
                exposure = "public"
            else:
                exposure = "restricted"
            purpose = " ".join(doc_lines) if doc_lines else None
            symbols.append(
                SourceSymbol(
                    name=name, kind=kind, line=lineno, purpose=purpose, exposure=exposure
                )
            )
        doc_lines = []
    return SourceFileExtraction(
        status=SymbolIndexStatus.INDEXED_PARTIAL, diagnostic=None, symbols=tuple(symbols)
    )


def _extract_js_family_source_symbols(path: Path) -> SourceFileExtraction:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        return SourceFileExtraction(
            status=SymbolIndexStatus.UNREADABLE, diagnostic=str(exc), symbols=()
        )

    symbols: list[SourceSymbol] = []
    pending_doc: str | None = None
    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if _JS_FAMILY_JSDOC_START_RE.match(stripped):
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
        match = _JS_FAMILY_ITEM_RE.match(stripped)
        if match:
            exported, kind, name = match.groups()
            exposure = "public" if exported else "internal"
            symbols.append(
                SourceSymbol(
                    name=name, kind=kind, line=lineno, purpose=pending_doc, exposure=exposure
                )
            )
        pending_doc = None
    return SourceFileExtraction(
        status=SymbolIndexStatus.INDEXED_PARTIAL, diagnostic=None, symbols=tuple(symbols)
    )
