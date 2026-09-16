"""Phase 54 reference-ingestion experiment pipeline.

Not a CodeCompass feature (deliberately outside `src/codecompass/` for
this phase — see `../../phase-54-heterogeneous-reference-material-experiment.md`'s
"Design decisions": Stage D's own goal is to gather evidence for Stage
E/GATE DD's generalisation decision, not to pre-empt it). Implements the
prompt's own pipeline shape for exactly one reference source (hledger):

    references.toml -> resolve tag to commit -> references.lock
    -> fetch/cache -> extract selected files/sections -> index with
    provenance

"Index with provenance" here means: write each extraction out as a
small, self-contained Markdown file with a YAML frontmatter provenance
block (source, resolved commit, original path, line range, content
hash, extracted-at timestamp) — a file CodeCompass's own existing,
unmodified `spec_docs.py`/`doc_mapping.py` mechanisms can then detect
and relate, once materialized into a project tree under a path their
existing glob coverage already reaches (`dev-docs/**/*.md`, Phase 49).
This module does not touch `context-graph.db` or any `codecompass`
module directly — its output is plain files on disk; a real
`codecompass sync`/`query` run against a tree containing them is what
tests whether that reuse actually works (see the plan's §3/§4).
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


class ReferencePipelineError(Exception):
    """Raised when a reference source can't be resolved, fetched, or a
    requested selection can't be extracted — a missing tag, an
    unreadable path, a line range past end-of-file.
    """


@dataclass(frozen=True)
class ReferenceSelection:
    """One `[[reference.select]]` entry: a labelled line range within
    one file of the reference source, plus a human-readable note on why
    it was chosen (carried through into the extracted file's own
    frontmatter, so a reader sees the rationale without cross-referencing
    `references.toml` separately).
    """

    label: str
    path: str
    start_line: int
    end_line: int
    note: str


@dataclass(frozen=True)
class ReferenceSource:
    """One `[[reference]]` entry: a Git-backed reference source plus its
    requested selections. `local_path`, if set, is preferred over a fresh
    `git clone` of `url` (see `fetch_cache`'s docstring) — both resolve
    against the same commit either way, so preferring the already-pinned
    local clone is a fetch-cost optimisation, not a different pipeline
    path.
    """

    name: str
    source: str
    url: str
    requested_ref: str
    local_path: str | None
    selections: tuple[ReferenceSelection, ...]


@dataclass(frozen=True)
class ResolvedSelection:
    label: str
    path: str
    start_line: int
    end_line: int
    note: str
    content_hash: str


@dataclass(frozen=True)
class ResolvedReference:
    """One reference source with its tag resolved to an exact commit and
    every requested selection's content hash computed — everything
    `references.lock` records.
    """

    name: str
    source: str
    url: str
    requested_ref: str
    resolved_commit: str
    fetch_method: str
    fetched_at: str
    selections: tuple[ResolvedSelection, ...]


def load_references_toml(path: Path) -> list[ReferenceSource]:
    """Parse `references.toml`. Fail-fast on a missing required field —
    same posture as `codecompass.config.load_vendor_config`, this
    experiment's nearest precedent, rather than collecting every error
    before reporting.
    """
    with path.open("rb") as fp:
        data = tomllib.load(fp)

    sources: list[ReferenceSource] = []
    for entry in data.get("reference", []):
        name = entry["name"]
        selections = tuple(
            ReferenceSelection(
                label=sel["label"],
                path=sel["path"],
                start_line=sel["lines"][0],
                end_line=sel["lines"][1],
                note=sel.get("note", ""),
            )
            for sel in entry.get("select", [])
        )
        sources.append(
            ReferenceSource(
                name=name,
                source=entry["source"],
                url=entry["url"],
                requested_ref=entry["requested_ref"],
                local_path=entry.get("local_path"),
                selections=selections,
            )
        )
    return sources


def _run_git(args: list[str], cwd: Path) -> str:
    resolved_git = shutil.which("git")
    if resolved_git is None:
        raise ReferencePipelineError("git not found on PATH")
    result = subprocess.run(
        [resolved_git, *args], cwd=cwd, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise ReferencePipelineError(
            f"git {' '.join(args)} failed (exit {result.returncode}): {result.stderr.strip()}"
        )
    return result.stdout.strip()


def resolve_ref(reference: ReferenceSource) -> str:
    """Resolve `reference.requested_ref` (a human-friendly tag) to an
    exact, immutable commit SHA. Uses the local clone (`local_path`) if
    given — `git rev-list -n1 <tag>` against a local repository is not a
    network call, so this is safe to run in a test — falling back to
    `git ls-remote --tags <url> <ref>` (a real network call; only
    exercised when no local clone is available, and never from the
    pipeline's own test suite — `decisions/0014`'s "no test makes a real
    external call" posture, applied here even though this module lives
    outside `src/codecompass/`).
    """
    if reference.local_path is not None:
        local = Path(reference.local_path)
        if not local.is_dir():
            raise ReferencePipelineError(f"local_path {local} does not exist")
        try:
            sha = _run_git(["rev-list", "-n", "1", reference.requested_ref], cwd=local)
        except ReferencePipelineError as exc:
            raise ReferencePipelineError(
                f"tag {reference.requested_ref!r} not found in local clone {local}"
            ) from exc
        if not sha:
            raise ReferencePipelineError(
                f"tag {reference.requested_ref!r} not found in local clone {local}"
            )
        return sha

    output = _run_git(
        ["ls-remote", "--tags", reference.url, reference.requested_ref], cwd=Path.cwd()
    )
    if not output:
        raise ReferencePipelineError(
            f"tag {reference.requested_ref!r} not found at {reference.url}"
        )
    return output.splitlines()[0].split()[0]


def _read_source_root(reference: ReferenceSource, resolved_commit: str) -> tuple[Path, str]:
    """The directory to read `reference.selections`' paths from, plus
    which fetch method was used — `local_clone` (the preferred path,
    `local_path` confirmed checked out at exactly `resolved_commit`) or
    `git_clone` (a fresh clone at that commit, the fallback for a
    reference source with no local clone available). Raises if the local
    clone's checked-out HEAD doesn't match `resolved_commit` — a stale or
    moved-on local clone must never be silently treated as pinned.
    """
    if reference.local_path is not None:
        local = Path(reference.local_path)
        checked_out = _run_git(["rev-parse", "HEAD"], cwd=local)
        if checked_out != resolved_commit:
            raise ReferencePipelineError(
                f"local clone {local} is at {checked_out}, not the resolved "
                f"commit {resolved_commit} — re-fetch or re-pin before extracting"
            )
        return local, "local_clone"

    raise ReferencePipelineError(
        "no local_path given and this experiment does not perform a live "
        "git clone outside a local-clone fixture — see resolve_ref's docstring"
    )


def _extract_lines(root: Path, selection: ReferenceSelection) -> tuple[str, str]:
    """Read `selection.path` under `root`, slice `[start_line, end_line]`
    (1-indexed, inclusive — matching `references.toml`'s own convention
    and `doc_chunking.DocChunk`'s established convention elsewhere in
    this project), and return `(sliced_text, content_hash)`. Raises if
    the file doesn't exist or the range is out of bounds — a silently
    truncated or empty extraction would be worse than a hard failure
    here, since this content is provenance evidence, not a best-effort
    digest.
    """
    file_path = root / selection.path
    if not file_path.is_file():
        raise ReferencePipelineError(f"{selection.path} not found under {root}")
    lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if selection.end_line > len(lines) or selection.start_line < 1:
        raise ReferencePipelineError(
            f"{selection.path}:{selection.start_line}-{selection.end_line} out of "
            f"range (file has {len(lines)} lines)"
        )
    sliced = "\n".join(lines[selection.start_line - 1 : selection.end_line])
    content_hash = hashlib.sha256(sliced.encode("utf-8")).hexdigest()
    return sliced, content_hash


def resolve_and_extract(reference: ReferenceSource) -> tuple[ResolvedReference, dict[str, str]]:
    """The full resolve -> fetch -> extract sequence for one reference
    source. Returns the `ResolvedReference` (everything `references.lock`
    records) plus a `{label: extracted_text}` map for
    `write_extracted_markdown` to render.
    """
    resolved_commit = resolve_ref(reference)
    root, fetch_method = _read_source_root(reference, resolved_commit)
    fetched_at = datetime.now(UTC).isoformat()

    resolved_selections: list[ResolvedSelection] = []
    texts: dict[str, str] = {}
    for selection in reference.selections:
        text, content_hash = _extract_lines(root, selection)
        texts[selection.label] = text
        resolved_selections.append(
            ResolvedSelection(
                label=selection.label,
                path=selection.path,
                start_line=selection.start_line,
                end_line=selection.end_line,
                note=selection.note,
                content_hash=content_hash,
            )
        )

    resolved = ResolvedReference(
        name=reference.name,
        source=reference.source,
        url=reference.url,
        requested_ref=reference.requested_ref,
        resolved_commit=resolved_commit,
        fetch_method=fetch_method,
        fetched_at=fetched_at,
        selections=tuple(resolved_selections),
    )
    return resolved, texts


def render_lock_toml(resolved: list[ResolvedReference]) -> str:
    """Hand-rolled TOML rendering — same non-round-trip-preserving
    rationale `codecompass.discovery.write_vendor_toml` already
    documents (`decisions/0011`): `references.lock` is a fresh,
    machine-generated artifact each run, not a hand-edited file whose
    comments/formatting must survive a rewrite.
    """
    lines = [f'generated_at = "{datetime.now(UTC).isoformat()}"', ""]
    for ref in resolved:
        lines += [
            "[[reference]]",
            f'name = "{ref.name}"',
            f'source = "{ref.source}"',
            f'url = "{ref.url}"',
            f'requested_ref = "{ref.requested_ref}"',
            f'resolved_commit = "{ref.resolved_commit}"',
            f'fetch_method = "{ref.fetch_method}"',
            f'fetched_at = "{ref.fetched_at}"',
            "",
        ]
        for sel in ref.selections:
            lines += [
                "[[reference.select]]",
                f'label = "{sel.label}"',
                f'path = "{sel.path}"',
                f"lines = [{sel.start_line}, {sel.end_line}]",
                f'content_hash = "sha256:{sel.content_hash}"',
                "",
            ]
    return "\n".join(lines)


def write_lock(resolved: list[ResolvedReference], path: Path) -> None:
    path.write_text(render_lock_toml(resolved), encoding="utf-8")


def render_extracted_markdown(
    ref: ResolvedReference, selection: ResolvedSelection, text: str
) -> str:
    """One extracted excerpt as a self-contained Markdown file: a YAML
    frontmatter provenance block (everything `references.lock` also
    records for this selection, so the file is independently checkable
    without cross-referencing the lock file) followed by the excerpt
    itself in a fenced code block, plus `selection.note`'s rationale.
    """
    frontmatter = [
        "---",
        f"reference: {ref.name}",
        f"source_url: {ref.url}",
        f"requested_ref: {ref.requested_ref}",
        f"resolved_commit: {ref.resolved_commit}",
        f"fetch_method: {ref.fetch_method}",
        f"path: {selection.path}",
        f"lines: [{selection.start_line}, {selection.end_line}]",
        f"content_hash: sha256:{selection.content_hash}",
        f"extracted_at: {ref.fetched_at}",
        "---",
        "",
    ]
    body = [
        f"# {selection.label}",
        "",
        selection.note,
        "",
        f"Excerpt from `{selection.path}:{selection.start_line}-{selection.end_line}`",
        f"at `{ref.name}` commit `{ref.resolved_commit}`:",
        "",
        "```",
        text,
        "```",
        "",
    ]
    return "\n".join(frontmatter + body)


def write_extracted_markdown(
    resolved: ResolvedReference, texts: dict[str, str], out_dir: Path
) -> list[Path]:
    """Write one `.md` file per selection into `out_dir`, named
    `<reference-name>-<label>.md`. Returns the written paths.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for selection in resolved.selections:
        content = render_extracted_markdown(resolved, selection, texts[selection.label])
        file_path = out_dir / f"{resolved.name}-{selection.label}.md"
        file_path.write_text(content, encoding="utf-8")
        written.append(file_path)
    return written


def run_pipeline(
    references_toml: Path, extracted_dir: Path, lock_path: Path
) -> list[ResolvedReference]:
    """The full pipeline, end to end, for every `[[reference]]` entry in
    `references_toml`. Idempotent: re-running against an unchanged
    reference source produces byte-identical `references.lock` content
    and byte-identical extracted Markdown files (same resolved commit,
    same content hashes, same rendering — only `generated_at`/
    `extracted_at` timestamps differ between runs, which is expected and
    disclosed, not a defect).
    """
    sources = load_references_toml(references_toml)
    resolved_all: list[ResolvedReference] = []
    for source in sources:
        resolved, texts = resolve_and_extract(source)
        write_extracted_markdown(resolved, texts, extracted_dir)
        resolved_all.append(resolved)
    write_lock(resolved_all, lock_path)
    return resolved_all


_EVIDENCE_REF_LINE_RE = re.compile(r"(?P<path>[\w./-]+\.\w+):(?P<lines>[\d, ()a-zA-Z-]+)")
_EVIDENCE_SOURCE_BLOCK_RE = re.compile(r'-\s*kind:\s*source\s*\n\s*ref:\s*"([^"]+)"', re.MULTILINE)


def _parse_evidence_ref_line_numbers(lines_fragment: str) -> list[int]:
    """`lines_fragment` is everything after the first `:` in one
    `evidence.ref` citation, e.g. `"429 (single-date span), 1132-1148
    (doubledatespanp, exclusive end)"` — a human-written, not
    machine-generated, format (real compat-register entries are hand-
    authored by `hledger-researcher`). Extracts every integer that reads
    as a line number or the start/end of a `N-M` range; parenthesised
    notes are ignored. Best-effort, not a full grammar — see
    `match_compat_register_evidence`'s docstring for what this is used
    for and its known limits.
    """
    import re

    numbers: list[int] = []
    for match in re.finditer(r"(\d+)(?:-(\d+))?", lines_fragment):
        numbers.append(int(match.group(1)))
        if match.group(2):
            numbers.append(int(match.group(2)))
    return numbers


def parse_compat_register_source_evidence(yaml_text: str) -> list[tuple[str, list[int]]]:
    """Extract every `kind: source` evidence citation's `(path,
    [line_numbers])` from a Ledgerkit compat-register YAML entry's raw
    text — a small, targeted regex-based reader, not a YAML parser (this
    experiment has no dependency on a YAML library, and a real compat-
    register entry's `evidence:` block has a fixed, simple enough shape
    for this to be reliable — see the module docstring's "relate to
    Ledgerkit code/tests/docs" step).
    """
    citations: list[tuple[str, list[int]]] = []
    for match in _EVIDENCE_SOURCE_BLOCK_RE.finditer(yaml_text):
        ref_text = match.group(1)
        ref_match = _EVIDENCE_REF_LINE_RE.search(ref_text)
        if ref_match is None:
            continue
        path = ref_match.group("path")
        line_numbers = _parse_evidence_ref_line_numbers(ref_match.group("lines"))
        citations.append((path, line_numbers))
    return citations


def match_compat_register_evidence(
    resolved: ResolvedReference, compat_register_yaml_text: str
) -> list[ResolvedSelection]:
    """The §3.3 fallback this experiment's plan named: rather than relying
    on CodeCompass's existing `mentions_artifact` mechanical word-boundary
    detection (empirically confirmed, this phase, to find **zero** edges
    between ingested reference material and Ledgerkit's own docs — see
    the phase retro — because `doc_artifacts.kind='spec_doc'` rows never
    get a `name`, and `mentions_artifact` only matches named artifacts),
    this function directly parses a compat-register entry's own
    structured `evidence.ref` citations and checks each one for a
    same-file, overlapping-line-range match against `resolved`'s own
    extracted selections. This is a **relation candidate**, the same
    epistemic status as any other mechanically-detected relation in
    CodeCompass — a real, checkable overlap, not an AI guess — but is
    **not currently wired into `context-graph.db`** (this experiment
    lives outside `src/codecompass/`; see the plan's Design decisions).
    Returns every selection with at least one overlapping citation.
    """
    citations = parse_compat_register_source_evidence(compat_register_yaml_text)
    matched: list[ResolvedSelection] = []
    for selection in resolved.selections:
        for cited_path, cited_lines in citations:
            if not cited_path.endswith(selection.path) and not selection.path.endswith(cited_path):
                continue
            if any(selection.start_line <= n <= selection.end_line for n in cited_lines):
                matched.append(selection)
                break
    return matched


if __name__ == "__main__":
    _here = Path(__file__).parent
    run_pipeline(_here / "references.toml", _here / "extracted", _here / "references.lock")
