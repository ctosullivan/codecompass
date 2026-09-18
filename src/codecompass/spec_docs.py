"""Detects a project's own human-authored spec documentation — README,
ARCHITECTURE.md, `docs/**/*.md`, `decisions/**/*.md`, etc. — as
`doc_artifacts` rows (`kind='spec_doc'`, `origin='project'`), distinct
from codecompass's own generated dependency docs (`claude_md`/`overview`,
`origin='codecompass_vendor'`) and generated/third-party Skills
(`skill`/`cursor_mdc`/`slash_command`). Mechanical only: a fixed default
glob set, no AI call, same posture as `usage.py`/`doc_mapping.py`/
`skill_scan.py`. See
planning/phase-21-spec-doc-detection-and-relationship-graph.md.

Phase 55b adds `name` population (`_extract_title`): every `spec_doc`
row previously had `name=None`, which structurally excluded it from
`doc_mapping.build_doc_relations_edges`'s `mentions_artifact` matching —
that function only ever considers a *named* `doc_artifacts` row as a
match target (see its own docstring). Two independent real-task
findings (`planning/context-gaps/inbox.md` CG-004, and Ledgerkit's own
`validation/codecompass/findings/CC-LK-001`) confirmed this meant two
obviously-related spec docs could never be mechanically related to each
other, in any project, regardless of content. No change to
`build_doc_relations_edges` itself was needed — it already treats any
named artifact as eligible; this module was the one place silently
withholding names from an entire `kind`.

Phase 54c adds `origin='pinned_reference'` detection
(`_has_pinned_reference_frontmatter`): a `dev-docs/**/*.md`-glob-matched
file whose leading content is a YAML frontmatter block carrying both a
`resolved_commit` key and a `source_url` key — the two fields present in
every file the reference-ingestion pipeline
(`planning/reference-projects/ledgerkit/reference-experiment/`)
produces, and structurally absent from ordinary hand-authored prose —
is classified as externally-sourced, revision-pinned reference material
rather than `origin='project'`. Hand-rolled `---`-delimited key scan, no
new parsing dependency, matching this project's own
`reference_pipeline.py::load_references_toml` precedent for a
comparably simple format. See
`planning/knowledge/doc-origin-pinned-reference/` (Phase 54c,
`CG-005`).
"""

from __future__ import annotations

import re
from pathlib import Path

from codecompass.graph import DocArtifactRow
from codecompass.usage import _PROJECT_PRUNE_DIR_NAMES

# Matches a level-1 ATX heading (`# Title`) — deliberately narrower than
# doc_chunking.py's own `_HEADING_RE` (which matches any of `#`-`######`
# for chunk-boundary purposes); a doc's *title* for naming purposes is
# specifically its first H1, not any heading. `re.MULTILINE` so `^`
# matches the start of any line, not just the string's start.
_H1_RE = re.compile(r"^#\s+(\S.*\S|\S)\s*$", re.MULTILINE)

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
    "ai-docs/**/*.md",
    "dev-docs/**/*.md",
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


def _is_specific_enough(candidate: str) -> bool:
    """Rejects a single bare word with no digit/hyphen — e.g. a
    project's own root `README.md` whose H1 is just its repo name
    (`# ledgerkit`), or a section titled only `# Architecture`. Found
    live (not designed speculatively) by independently re-testing this
    phase's fix against the real Ledgerkit repository: a naive "use
    whatever the H1 says" rule produced 55 hypothetical
    `mentions_artifact` edges, 50 of which were every other doc
    "mentioning" `README.md` purely because its title is the bare
    project name — ordinary prose repeatedly saying "ledgerkit" is not
    evidence of a real relationship between two docs, the same
    "guaranteed, universal noise" reasoning `decisions/0043` already
    applied to a vendor's own README mentioning its own vendor name.
    A title/stem with more than one whitespace-separated word, or a
    digit/hyphen (numbered docs like `07-query-regex`, hyphenated slugs
    like `hledger-compatibility`), is specific enough to keep — checked
    against every real title in both this project's own repo and
    Ledgerkit's, none of which was wrongly excluded by this rule.
    """
    return len(candidate.split()) > 1 or any(c.isdigit() or c == "-" for c in candidate)


def _extract_title(path: Path) -> str | None:
    """The doc's own first level-1 heading text, if it has one and it's
    specific enough (`_is_specific_enough`) — e.g. `# Architecture
    overview` yields `"Architecture overview"`. Falls back to the file's
    stem (`hledger-compatibility.md` -> `"hledger-compatibility"`) when
    there's no H1, or the H1 itself isn't specific enough, so every
    `spec_doc` row gets *some* name where a reasonably safe one exists —
    a path-derived stem is still a real string a different doc could
    plausibly mention verbatim, and is checked against the same
    specificity rule (so a doc named plainly `docs/x.md` with a bare
    one-word non-numbered stem still ends up with no name, same as
    before this phase, rather than a new false-positive match target).
    Never raises: an unreadable file (permissions, a broken symlink)
    falls back to the stem the same as a missing-H1 file, matching this
    project's established "never raises, degrade to a safe default"
    posture (`staleness._parse_version`, `skill_scan._extract_scalar`).
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = ""
    match = _H1_RE.search(text) if text else None
    if match and _is_specific_enough(match.group(1)):
        return match.group(1)
    return path.stem if _is_specific_enough(path.stem) else None


def _has_pinned_reference_frontmatter(text: str) -> bool:
    """True if `text` opens with a YAML frontmatter block (a `---` line,
    followed by content, followed by a closing `---` line) containing
    both a `resolved_commit:` key and a `source_url:` key — the two
    fields present in every file
    `reference_pipeline.py::render_extracted_markdown` produces and
    structurally absent from ordinary hand-authored prose (see this
    module's own docstring). Deliberately checks only for key presence,
    not value shape — the classification question is "was this
    materialized by the ingestion pipeline," not "is the pinned commit
    well-formed," which is the pipeline's own concern
    (`ReferencePipelineError`), not this detector's.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    try:
        closing = lines.index("---", 1)
    except ValueError:
        return False
    frontmatter = lines[1:closing]
    has_resolved_commit = any(line.startswith("resolved_commit:") for line in frontmatter)
    has_source_url = any(line.startswith("source_url:") for line in frontmatter)
    return has_resolved_commit and has_source_url


def _detect_origin(path: Path) -> str:
    """`'pinned_reference'` if `path` opens with ingestion-pipeline
    frontmatter (`_has_pinned_reference_frontmatter`), else the
    pre-existing `'project'` default. Never raises: an unreadable file
    falls back to `'project'`, matching `_extract_title`'s own
    "degrade to a safe default" posture for the same failure mode.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "project"
    return "pinned_reference" if _has_pinned_reference_frontmatter(text) else "project"


def scan_spec_docs(project_root: Path) -> list[DocArtifactRow]:
    """Globs the fixed default spec-doc pattern set rooted at
    `project_root`, excluding `CHANGELOG.md`/`CONTRIBUTING.md`/`LICENSE*`/
    root `CLAUDE.md` and anything under `usage._PROJECT_PRUNE_DIR_NAMES`.
    Deterministic, sorted output; a path matching more than one glob
    pattern is only ever recorded once. Each row's `name` is its own
    first H1 heading, or its filename stem if it has none (`_extract_title`,
    Phase 55b) — populating `name` is what makes a `spec_doc` row an
    eligible `mentions_artifact` match target at all; see this module's
    own docstring. Each row's `origin` is `'pinned_reference'` if the
    file opens with ingestion-pipeline frontmatter, else `'project'`
    (`_detect_origin`, Phase 54c).
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
        DocArtifactRow(
            path=rel.as_posix(),
            kind="spec_doc",
            origin=_detect_origin(project_root / rel),
            name=_extract_title(project_root / rel),
        )
        for rel in sorted(matched)
    ]
