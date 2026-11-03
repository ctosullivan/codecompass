"""Phase 86 — maintainer-only, on-demand knowledge-placement validator
for CodeCompass's own `src/codecompass/` source tree and `decisions/`
ADR corpus. Mirrors `scripts/check_self_knowledge_quality.py`'s own
`Finding(rule, message, strict)` convention and report-only-by-default
posture, with `file`/`line` added as structured fields (not present on
that script's own `Finding`) since every finding here is inherently
file/line-based. `--strict` exits 1 on a *blocking* finding only.
Mechanical only — no AI call, no edits, no mutation of source or
canonical knowledge.

See `planning/phase-86-knowledge-placement-code-quality-review.md` §6.A
for the full design this implements.

    python scripts/check_knowledge_placement.py [--strict] [--files PATH ...]

Not part of the `codecompass` package: like its siblings, this checks
CodeCompass's own first-party source, not a consuming project's, and is
not a `codecompass` subcommand.

Citation extraction (§6.A points 1-6): each `src/codecompass/**/*.py`
file is parsed with `ast.parse` for real module/class/function
docstrings and independently tokenized with `tokenize.generate_tokens`
for real `#` comments. A docstring's own text is sliced directly from
the file's **raw source lines** (using the string literal's own
`lineno`/`col_offset`/`end_lineno`/`end_col_offset`), never `ast.
get_docstring`'s decoded value, even with `clean=False` — a decoded
value turns an escaped `\\n` *inside* one physical source line into a
real newline character, which would overcount a later citation's own
physical line; a raw source slice contains only genuine physical line
breaks (Phase 86 corrective pass, finding D). A single bounded regex,
`decisions/([0-9]{4})\\b`, is applied only within each docstring's/
comment's own isolated text — never the rest of the file, never an
ordinary string literal, f-string, or test-fixture string. A per-file
`SyntaxError`/`OSError`/`UnicodeDecodeError`/`tokenize` failure
produces one always-blocking `knowledge-placement-unparseable-source-
file` finding (`line=1`) for that file and processing continues with
the next file — one bad file never aborts the whole run, never
silently looks like a clean one (corrective-pass finding B widened
the caught exception set from `OSError` alone, which does not cover
`UnicodeDecodeError` on invalid-UTF-8 content).

Supersession attribution (§6.A point 7) is scoped to four locations
per `decisions/*.md` ADR file — its own first line (title), `##
Status`, `## Decision`, `## Consequences` — never `## Context` or `##
Alternatives considered`, which this project's own real corpus
(`decisions/0058`) shows is where exploratory, not-yet-decided
discussion legitimately lives. Two patterns, case-insensitive on the
verb only: passive (`decisions/NNNN is/are [fully] superseded [by
decisions/MMMM]`, deliberately excluding "partially") and active
(`supersedes decisions/NNNN`). Verified against the real corpus this
phase's own plan was written against: exactly 8 files match
(`decisions/0031/0032/0033/0034/0043/0061/0070/0078`), with
`decisions/0027`'s "is **not** superseded" and `decisions/0058`'s
`## Context`-only mention confirmed as negative controls, and a
`decisions/0032` conjunction ("X and Y are superseded") only capturing
the number immediately adjacent to the verb — a disclosed, not silent,
limitation. An ADR that cannot be read or decoded is never silently
skipped (corrective-pass finding C) — it produces its own always-
blocking `knowledge-placement-unreadable-decision-file` diagnostic,
since skipping it would let a citation to an ADR actually superseded
*by* the unreadable file report as clean, misrepresenting a partially-
examined corpus as a complete one; every other, readable ADR is still
processed.

Checks:

1. `decision-citation-exists` — every extracted citation must resolve
   to a real file under `decisions/`. **Blocking.**
2. `decision-citation-superseded` — a citation to an ADR some other
   real ADR's title/Status/Decision/Consequences section explicitly
   records as superseded. **Informational, never blocking** — citing
   superseded context for legitimate historical framing (category 8)
   is not itself a defect; this check only makes the citation visible
   for the ad-hoc semantic/editorial reviewer (`docs/workflows/
   knowledge-placement-review.md`) to judge in context.

Diagnostics (not findings about the source/ADR corpus itself, but
about this check's own ability to examine it — both **always
blocking**, since a validator must never produce an apparently
complete, trustworthy result when part of its authoritative input
could not be read or interpreted):

- `knowledge-placement-unparseable-source-file` — a `src/codecompass/
  **/*.py` file could not be read or parsed.
- `knowledge-placement-unreadable-decision-file` — a `decisions/*.md`
  file could not be read or decoded, so this run's own supersession
  attribution is incomplete with respect to it.

Deferred, not shipped (see the plan's own §6.A/§7/§12/§13 for the full
rationale): `decision-citation-status-mismatch` (would conflate a
citation's recorded vs. effective ADR status, demonstrated unsafe by
the real `decisions/0019`/`0061` relationship) and
`docstring-contradicted-by-oracle-result` (would require inferring
that a bare `check_id` citation asserts specific behaviour, and
treating `INVALID`/stale evidence as a demonstrated `FAIL` — neither
licensed by this project's own Oracle semantics). Behavioural review
remains available through the ad-hoc reviewer's own direct reading of
real oracle evidence, never through a dedicated script check here.
"""

from __future__ import annotations

import argparse
import ast
import io
import re
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = ROOT / "src" / "codecompass"
DECISIONS_ROOT = ROOT / "decisions"

CITATION_RE = re.compile(r"decisions/([0-9]{4})\b")

# Passive: "decisions/NNNN is/are [fully] superseded [by decisions/MMMM]".
# "partially" is deliberately excluded from the qualifier alternation --
# a scoped, partial claim (the real decisions/0033 "is partially
# superseded" text) is not an unambiguous "this whole citation is dead"
# signal, and this check does not attempt to judge whether a given
# source citation relies on the superseded part or the surviving part.
_SUPERSEDED_QUALIFIER = r"(?:fully\s+)?"
PASSIVE_SUPERSEDED_RE = re.compile(
    r"decisions/([0-9]{4})`?\s+(?:is|are)\s+" + _SUPERSEDED_QUALIFIER + r"superseded"
    r"(?:\s+by\s+`?decisions/[0-9]{4}`?)?\b",
    re.IGNORECASE,
)
# Active self-declaration: "Supersedes decisions/NNNN" -- case-insensitive
# because this project's own real text capitalises it at sentence-start
# (decisions/0070's Status section, decisions/0043's Consequences).
ACTIVE_SUPERSEDES_RE = re.compile(r"\bsupersedes\s+`?decisions/([0-9]{4})`?", re.IGNORECASE)

_ADR_SECTION_NAMES = ("Status", "Decision", "Consequences")
_ADR_HEADER_RE = re.compile(r"^## (.+)$")
_ADR_FILENAME_NUMBER_RE = re.compile(r"^([0-9]{4})-")


@dataclass
class Finding:
    rule: str
    message: str
    strict: bool = True  # False = informational, never fails --strict
    file: str = ""
    line: int = 0


@dataclass(frozen=True)
class _Citation:
    file: str
    line: int
    number: str


def _parse_adr_sections(text: str) -> dict[str, str]:
    """Title (first line) plus the three sections this check scans --
    `## Context`/`## Alternatives considered`/any other section name
    are discarded here, never retained for matching (§6.A point 7)."""
    lines = text.splitlines()
    sections: dict[str, str] = {"title": lines[0] if lines else ""}
    sections.update({n: "" for n in _ADR_SECTION_NAMES})
    current: str | None = None
    buf: list[str] = []
    for line in lines[1:]:
        m = _ADR_HEADER_RE.match(line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf)
            name = m.group(1).strip()
            current = name if name in _ADR_SECTION_NAMES else None
            buf = []
            continue
        if current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf)
    return sections


def _real_adr_numbers(decisions_root: Path) -> set[str]:
    numbers: set[str] = set()
    for path in decisions_root.glob("*.md"):
        m = _ADR_FILENAME_NUMBER_RE.match(path.name)
        if m:
            numbers.add(m.group(1))
    return numbers


def _build_superseded_map(
    decisions_root: Path, project_root: Path
) -> tuple[dict[str, tuple[str, str, str]], list[Finding]]:
    """Cited ADR number -> (attributing ADR filename, section, pattern)
    for the *first* real attribution found, sorted by filename for
    determinism -- a number attributed from more than one file/section
    (e.g. `decisions/0061` both title and Decision cite `0019`) reports
    only the first, which is sufficient since this check's own job is
    visibility, not an exhaustive attribution list.

    An ADR that cannot be read or decoded is never silently skipped --
    skipping it would make this check's own result look like a complete
    "nothing here is superseded" pass when the authoritative corpus was
    only *partially* examined. Each such file instead produces its own
    always-blocking `knowledge-placement-unreadable-decision-file`
    diagnostic, and every other, readable ADR is still processed."""
    result: dict[str, tuple[str, str, str]] = {}
    diagnostics: list[Finding] = []
    for path in sorted(decisions_root.glob("*.md")):
        try:
            rel = str(path.relative_to(project_root))
        except ValueError:
            rel = str(path)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            diagnostics.append(
                Finding(
                    "knowledge-placement-unreadable-decision-file",
                    f"{rel}: could not be read ({type(exc).__name__}: {exc}) -- the "
                    "decisions/ corpus was only partially examined; supersession "
                    "attribution involving this file is unavailable, not confirmed absent",
                    True,
                    rel,
                    1,
                )
            )
            continue
        sections = _parse_adr_sections(text)
        for section_name, content in sections.items():
            for m in PASSIVE_SUPERSEDED_RE.finditer(content):
                result.setdefault(m.group(1), (path.name, section_name, "passive"))
            for m in ACTIVE_SUPERSEDES_RE.finditer(content):
                result.setdefault(m.group(1), (path.name, section_name, "active"))
    return result, diagnostics


def _docstring_citations(tree: ast.AST, source_lines: list[str]) -> list[tuple[int, str]]:
    """Scans each real docstring's own **raw source text** -- sliced
    directly from `source_lines` using the string literal's own
    `lineno`/`col_offset`/`end_lineno`/`end_col_offset` -- rather than
    `ast.get_docstring`'s decoded string value (even with `clean=
    False`). A decoded value turns an escaped `\\n` *inside* a single
    physical source line into a real newline character, which would
    overcount physical lines for any citation appearing after one; the
    raw source slice contains only genuine physical line breaks, so
    counting `\\n` within it always matches the citation's real line."""
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.body:
            continue
        first = node.body[0]
        if not (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            continue
        value_node = first.value
        start_line = value_node.lineno
        end_line = value_node.end_lineno
        lines = list(source_lines[start_line - 1 : end_line])
        if not lines:
            continue
        if len(lines) == 1:
            lines[0] = lines[0][value_node.col_offset : value_node.end_col_offset]
        else:
            lines[0] = lines[0][value_node.col_offset :]
            lines[-1] = lines[-1][: value_node.end_col_offset]
        raw = "\n".join(lines)
        for m in CITATION_RE.finditer(raw):
            line = start_line + raw[: m.start()].count("\n")
            found.append((line, m.group(1)))
    return found


def _comment_citations(text: str) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type != tokenize.COMMENT:
            continue
        for m in CITATION_RE.finditer(tok.string):
            found.append((tok.start[0], m.group(1)))
    return found


def _extract_file_citations(path: Path, rel: str) -> tuple[list[_Citation], Finding | None]:
    """Returns `(citations, diagnostic)`; `diagnostic` is non-`None`
    (and `citations` empty) exactly when the file could not be read or
    parsed -- never both a diagnostic *and* partial citations, so a
    parse failure can never masquerade as "fewer findings"."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [], Finding(
            "knowledge-placement-unparseable-source-file",
            f"{rel}: could not be read ({type(exc).__name__}: {exc})",
            True,
            rel,
            1,
        )
    try:
        tree = ast.parse(text, filename=str(path))
        comment_hits = _comment_citations(text)
    except (SyntaxError, tokenize.TokenError, IndentationError) as exc:
        return [], Finding(
            "knowledge-placement-unparseable-source-file",
            f"{rel}: could not be parsed ({type(exc).__name__}: {exc})",
            True,
            rel,
            1,
        )
    docstring_hits = _docstring_citations(tree, text.splitlines())
    citations = sorted(
        {_Citation(rel, line, number) for line, number in docstring_hits + comment_hits},
        key=lambda c: (c.line, c.number),
    )
    return citations, None


def check_decision_citation_exists(
    citations: list[_Citation], real_numbers: set[str]
) -> list[Finding]:
    findings: list[Finding] = []
    for c in citations:
        if c.number in real_numbers:
            continue
        findings.append(
            Finding(
                "decision-citation-exists",
                f"{c.file}:{c.line}: cites decisions/{c.number}, which does not "
                "exist under decisions/",
                True,
                c.file,
                c.line,
            )
        )
    return findings


def check_decision_citation_superseded(
    citations: list[_Citation], superseded_map: dict[str, tuple[str, str, str]]
) -> list[Finding]:
    findings: list[Finding] = []
    for c in citations:
        attribution = superseded_map.get(c.number)
        if attribution is None:
            continue
        adr_file, section, pattern = attribution
        findings.append(
            Finding(
                "decision-citation-superseded",
                f"{c.file}:{c.line}: cites decisions/{c.number}, which {adr_file}'s own "
                f"{section} section ({pattern} pattern) records as superseded -- "
                "informational only, citing superseded context for legitimate historical "
                "framing is not itself a defect",
                False,
                c.file,
                c.line,
            )
        )
    return findings


def _iter_source_files(src_root: Path, files: list[Path] | None) -> list[Path]:
    if files is not None:
        return sorted(files)
    if not src_root.is_dir():
        return []
    return sorted(src_root.rglob("*.py"))


def run_all(
    project_root: Path = ROOT,
    src_root: Path | None = None,
    decisions_root: Path | None = None,
    files: list[Path] | None = None,
) -> list[Finding]:
    """`src_root`/`decisions_root` default to `project_root`'s own
    `src/codecompass`/`decisions` -- relativised against `project_root`
    (never the real repository's own global `ROOT`), so a `tmp_path`
    fixture project reports clean, relative `file` values exactly like
    a real run does, rather than leaking an absolute fixture path."""
    if src_root is None:
        src_root = project_root / "src" / "codecompass"
    if decisions_root is None:
        decisions_root = project_root / "decisions"

    findings: list[Finding] = []
    all_citations: list[_Citation] = []

    for path in _iter_source_files(src_root, files):
        try:
            rel = str(path.relative_to(project_root))
        except ValueError:
            rel = str(path)
        citations, diagnostic = _extract_file_citations(path, rel)
        if diagnostic is not None:
            findings.append(diagnostic)
            continue
        all_citations.extend(citations)

    real_numbers = _real_adr_numbers(decisions_root)
    superseded_map, corpus_diagnostics = _build_superseded_map(decisions_root, project_root)
    findings.extend(corpus_diagnostics)

    findings.extend(check_decision_citation_exists(all_citations, real_numbers))
    findings.extend(check_decision_citation_superseded(all_citations, superseded_map))

    return sorted(findings, key=lambda f: (f.file, f.line, f.rule))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 if any blocking finding is reported (default: always exit 0)",
    )
    parser.add_argument(
        "--files",
        type=Path,
        nargs="*",
        default=None,
        help="an explicit, bounded file set to check instead of the whole src/codecompass/ tree",
    )
    args = parser.parse_args()

    findings = run_all(files=args.files)
    blocking = [f for f in findings if f.strict]

    if not findings:
        print("check_knowledge_placement: no findings")
    else:
        print(f"check_knowledge_placement: {len(findings)} finding(s)")
        for f in findings:
            tag = "" if f.strict else " (info)"
            print(f"  [{f.rule}]{tag} {f.message}")

    return 1 if (args.strict and blocking) else 0


if __name__ == "__main__":
    sys.exit(main())
