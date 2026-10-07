"""Phase 81 — persistent bidirectional intermediate knowledge layer.

Renders `planning/knowledge/<slug>/` canonical records (Phase 54c's
Observation/Evidence/Claim/Derivation/Decision/Requirement model) into
editable `intermediate/*.md` Markdown projections; detects human/tool
edits to those projections via a dual-hash anchor (one hash for the
canonical record, one for the rendered Markdown — never compared against
each other, see `planning/phase-81-intermediate-knowledge-layer.md`
§1.5); and applies reviewed changes back through the existing,
unmodified Claim/Requirement record format. See that plan file for the
full design — this module implements it, it does not re-derive it.

Unlike `scripts/check_knowledge_base.py` (CodeCompass's own maintainer-
only sanity script, hard-coded to this repository and not part of the
shipped package), this module is shipped as part of `codecompass` and
operates on whatever `planning/knowledge/` directory exists under the
project root it is pointed at — including, but not limited to,
CodeCompass's own repository. It therefore cannot import from
`scripts/`; its own small flat-record parser mirrors (not imports)
`check_knowledge_base.py`'s approach, since both operate on the same
record format by design.

Phase 81 adds **zero new persisted fields** to any canonical record
(§1.2 of the plan) — every epistemic state this module needs is already
expressed by the existing `status`/`evidence_support_state`/`basis`/
`contradicting_evidence` fields. The only new persisted artefacts are
the reconciliation manifest (`planning/knowledge/<slug>/reconciliation/
*.toml`) and the presentation-wording cache
(`planning/knowledge/<slug>/intermediate/.presentation-cache.toml`) —
neither is a canonical record.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Flat-record parsing — mirrors scripts/check_knowledge_base.py's own
# parse_record_text exactly (same record format), duplicated rather than
# imported because scripts/ is deliberately not part of the installed
# package.
# ---------------------------------------------------------------------------

_ID_PATTERN = re.compile(r"\b(OBS|EV|CL|DE|DEC|REQ)-[A-Z0-9]+-\d+\b")

_ID_PREFIX_FOR_KIND = {
    "observation": "OBS",
    "evidence": "EV",
    "claim": "CL",
    "derivation": "DE",
    "decision": "DEC",
    "requirement": "REQ",
}
_KIND_FOR_ID_PREFIX = {v: k for k, v in _ID_PREFIX_FOR_KIND.items()}


def _strip_inline_comment(value: str) -> str:
    if '"' in value or "'" in value:
        return value.strip()
    idx = value.find(" #")
    return (value[:idx] if idx != -1 else value).strip()


def parse_record_text(text: str) -> dict[str, str]:
    """Every top-level (column-0) `key: value` pair. A `>`/`|` block
    scalar's own continuation lines are folded into the key's own value
    (space-joined, trimmed) so `statement`/`rationale`/etc. are usable as
    real prose here, unlike `check_knowledge_base.py`'s own
    presence-only parse (which never needed the prose itself)."""
    fields: dict[str, str] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line or line[0] in " \t#":
            i += 1
            continue
        match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
        if not match:
            i += 1
            continue
        key = match.group(1)
        value = _strip_inline_comment(match.group(2))
        if value in (">", "|", ">-", "|-"):
            block_lines: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                block_lines.append(lines[i].strip())
                i += 1
            fields[key] = " ".join(x for x in block_lines if x).strip()
            continue
        fields[key] = value
        i += 1
    return fields


def parse_record(path: Path) -> dict[str, str]:
    return parse_record_text(path.read_text(encoding="utf-8"))


def _extract_id_strings(value: str) -> list[str]:
    return [m.group(0) for m in _ID_PATTERN.finditer(value)]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Slug layout
# ---------------------------------------------------------------------------


def knowledge_dir(project_root: Path) -> Path:
    return project_root / "planning" / "knowledge"


def slug_dir(project_root: Path, slug: str) -> Path:
    return knowledge_dir(project_root) / slug


def intermediate_dir(project_root: Path, slug: str) -> Path:
    return slug_dir(project_root, slug) / "intermediate"


def reconciliation_dir(project_root: Path, slug: str) -> Path:
    return slug_dir(project_root, slug) / "reconciliation"


def presentation_cache_path(project_root: Path, slug: str) -> Path:
    return intermediate_dir(project_root, slug) / ".presentation-cache.toml"


CANDIDATE_START = "<!-- codecompass-candidates:start -->"
CANDIDATE_END = "<!-- codecompass-candidates:end -->"

_ANCHOR_OPEN_RE = re.compile(
    r"<!--\s*codecompass-knowledge:\s*([A-Z]+-[A-Z0-9]+-\d+)\s+"
    r"semantic-sha256:(\S+)\s+projection-sha256:(\S+)\s*-->"
)
_ANCHOR_CLOSE = "<!-- /codecompass-knowledge -->"

_GROUNDING_OPEN_RE = re.compile(r"<!--\s*codecompass-grounded-by:\s*(.+?)\s*-->")
_GROUNDING_CLOSE = "<!-- /codecompass-grounded-by -->"


def parse_grounding_markers(text: str) -> list[tuple[list[str], str]]:
    """Every explicit `codecompass-grounded-by` region in `text` (§9.2) —
    returns `(cited_record_ids, region_body)` pairs. Used in both
    directions: given a changed record id, find which doc regions cite it
    (`find_grounded_doc_regions`); given a changed doc region, read off
    the exact ids it already cites (the tuple's own first element) —
    both deterministic, no dispatch call needed for the strong,
    explicitly-grounded case (§9.2's own "canonical knowledge changes ->
    affected doc region identified" / "factual doc changes -> relevant
    canonical knowledge identified" pair)."""
    results: list[tuple[list[str], str]] = []
    pos = 0
    while True:
        match = _GROUNDING_OPEN_RE.search(text, pos)
        if not match:
            break
        close_idx = text.find(_GROUNDING_CLOSE, match.end())
        if close_idx == -1:
            pos = match.end()
            continue
        ids = _extract_id_strings(match.group(1))
        results.append((ids, text[match.end() : close_idx]))
        pos = close_idx + len(_GROUNDING_CLOSE)
    return results


def find_grounded_doc_regions(
    project_root: Path,
    record_id: str,
    doc_names: tuple[str, ...] = ("README.md", "CONTRIBUTING.md"),
) -> list[tuple[Path, str]]:
    """§9.2's "canonical knowledge changes -> affected doc region
    identified": every grounded region, in any of `doc_names`, that
    explicitly cites `record_id` — a plain text scan, no graph needed for
    this direct case (a larger project may additionally want the
    `doc_relations_edges` mention-detection fallback for the weaker,
    ungrounded case; that is `knowledge status`'s own concern, §9.6)."""
    hits: list[tuple[Path, str]] = []
    for doc_name in doc_names:
        doc_path = project_root / doc_name
        if not doc_path.is_file():
            continue
        text = doc_path.read_text(encoding="utf-8")
        for ids, region in parse_grounding_markers(text):
            if record_id in ids:
                hits.append((doc_path, region))
    return hits


@dataclass
class KnowledgeRecord:
    record_id: str
    kind: str
    path: Path
    fields: dict[str, str]


def load_slug_records(slug: Path) -> dict[str, KnowledgeRecord]:
    """Every record directly under `slug` (not `intermediate/`,
    `snapshots/`, or `reconciliation/`) keyed by its own `id`."""
    records: dict[str, KnowledgeRecord] = {}
    if not slug.is_dir():
        return records
    for yaml_path in sorted(slug.glob("*.yaml")):
        fields = parse_record(yaml_path)
        record_id = fields.get("id")
        kind = fields.get("kind")
        if record_id and kind:
            records[record_id] = KnowledgeRecord(record_id, kind, yaml_path, fields)
    return records


# ---------------------------------------------------------------------------
# Derived provenance label (§1.2.1) — rendering-time only, never persisted.
# ---------------------------------------------------------------------------


def derive_provenance_label(
    record: KnowledgeRecord, records_by_id: dict[str, KnowledgeRecord]
) -> str:
    """OBSERVED / DECLARED / DECIDED / DERIVED / HISTORICAL / MIXED,
    computed purely from existing kind/basis/status fields — see
    planning/phase-81-intermediate-knowledge-layer.md §1.2.1. Ambiguity
    (`basis: directly_stated` with a mixed evidence chain) always
    resolves to the more cautious label, never the stronger one.
    """
    fields = record.fields
    if fields.get("status") == "superseded":
        return "HISTORICAL"
    if record.kind == "decision":
        return "DECLARED"
    if record.kind == "requirement":
        decision_id = _extract_id_strings(fields.get("decision", ""))
        if decision_id:
            decision = records_by_id.get(decision_id[0])
            if decision and decision.fields.get("status") == "approved":
                return "DECIDED"
        return "DECLARED"
    if record.kind != "claim":
        return "DERIVED"

    basis = fields.get("basis")
    if basis == "observed_behaviour":
        return "OBSERVED"
    if basis == "proposed_policy":
        return "DECLARED"
    if basis == "inferred":
        return "DERIVED"
    if basis == "directly_stated":
        evidence_ids = _extract_id_strings(fields.get("supporting_evidence", ""))
        if not evidence_ids:
            return "DECLARED"  # the cautious default with nothing to check
        saw_observed = False
        saw_non_observed = False
        for ev_id in evidence_ids:
            ev = records_by_id.get(ev_id)
            if ev is None:
                saw_non_observed = True
                continue
            # Evidence has no `basis` field of its own; an Evidence record
            # is "observed" in this sense only if it cites a real
            # Observation at all (even an inferential Evidence usually
            # traces back to one) — checked via evidence_kind as the
            # closest existing signal, defaulting to the cautious label
            # when genuinely unclear rather than guessing.
            if ev.fields.get("evidence_kind") in ("source", "test", "behavioural"):
                saw_observed = True
            else:
                saw_non_observed = True
        if saw_observed and not saw_non_observed:
            return "OBSERVED"
        if saw_observed and saw_non_observed:
            return "MIXED"
        return "DECLARED"
    return "DERIVED"


# ---------------------------------------------------------------------------
# Presentation cache (§4.5)
# ---------------------------------------------------------------------------


@dataclass
class PresentationEntry:
    accepted_for_semantic_hash: str
    wording: str


def _toml_escape(value: str) -> str:
    """A deliberately minimal TOML basic-string encoder — this project's
    own existing posture for hand-rolled TOML (see
    scripts/check_knowledge_base.py's own module docstring, which notes
    `reference_pipeline.py`'s equally minimal precedent): escapes only
    what TOML's basic-string form requires for ordinary prose content,
    never attempts the full spec."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    escaped = escaped.replace("\n", "\\n").replace("\t", "\\t")
    return f'"{escaped}"'


def _toml_unescape(value: str) -> str:
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    return (
        value.replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace('\\"', '"')
        .replace("\\\\", "\\")
    )


def read_presentation_cache(path: Path) -> dict[str, PresentationEntry]:
    if not path.is_file():
        return {}
    import tomllib

    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    cache: dict[str, PresentationEntry] = {}
    for record_id, entry in data.items():
        if isinstance(entry, dict) and "wording" in entry:
            cache[record_id] = PresentationEntry(
                accepted_for_semantic_hash=entry.get("accepted_for_semantic_hash", ""),
                wording=entry.get("wording", ""),
            )
    return cache


def write_presentation_cache(path: Path, cache: dict[str, PresentationEntry]) -> None:
    lines = [
        "# Generated by `codecompass knowledge apply` — do not hand-edit.",
        "# See docs/codecompass-knowledge-workflow.md.",
        "",
    ]
    for record_id in sorted(cache):
        entry = cache[record_id]
        lines.append(f'["{record_id}"]')
        accepted_hash = _toml_escape(entry.accepted_for_semantic_hash)
        lines.append(f"accepted_for_semantic_hash = {accepted_hash}")
        lines.append(f"wording = {_toml_escape(entry.wording)}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Rendering (§4) — deterministic, no AI call.
# ---------------------------------------------------------------------------

_CORE_FILES = (
    "overview.md",
    "invariants-and-constraints.md",
    "interfaces-and-behaviours.md",
    "open-questions-and-conflicts.md",
)

_CANDIDATE_INSTRUCTIONS = (
    "Add new domain knowledge, edge cases, invariants, or open questions "
    "below, strictly between the two marker comments. Content outside this "
    "region — including this paragraph — is never read as knowledge; it is "
    "just narrative framing CodeCompass leaves untouched.\n\n"
    "To propose a Requirement rather than a Claim, cite an existing, "
    'already-approved Decision id explicitly (e.g. "per DEC-ARCH-003") — '
    "CodeCompass never invents a Decision on your behalf; without a cited, "
    "approved Decision, your addition becomes a Claim."
)


def _file_for_record(record: KnowledgeRecord) -> str | None:
    """Deterministic dispatch (§4.1) — never an AI judgment call."""
    if record.kind not in ("claim", "decision", "requirement"):
        return None  # Observation/Evidence/Derivation are cited, not rendered standalone
    if record.fields.get("status") == "contradicted":
        return "open-questions-and-conflicts.md"
    if record.kind == "requirement":
        return "tests-and-acceptance.md"
    if record.kind == "decision":
        return "overview.md"
    assertion_kind = record.fields.get("assertion_kind")
    if assertion_kind in ("invariant", "rule", "boundary", "constraint"):
        return "invariants-and-constraints.md"
    if assertion_kind in ("relationship", "state_transformation", "workflow"):
        return "interfaces-and-behaviours.md"
    if record.fields.get("status") == "proposed" and not record.fields.get(
        "evidence_support_state"
    ):
        return "open-questions-and-conflicts.md"
    return "overview.md"


def render_block(
    record: KnowledgeRecord,
    records_by_id: dict[str, KnowledgeRecord],
    presentation_cache: dict[str, PresentationEntry],
) -> str:
    """One anchored Markdown block (§4.2/§4.3). The block's own
    `projection-sha256` is computed over exactly the body text between the
    two marker comments — never including the marker comments themselves,
    so recomputing it on reimport is unambiguous."""
    semantic_hash = sha256_text(record.path.read_text(encoding="utf-8"))
    cached = presentation_cache.get(record.record_id)
    if cached is not None and cached.accepted_for_semantic_hash == semantic_hash:
        wording = cached.wording
    else:
        wording = (
            record.fields.get("statement")
            or record.fields.get("decides")
            or record.fields.get("what_it_shows")
            or ""
        )
    label = derive_provenance_label(record, records_by_id)
    lines = [f"### {record.record_id}", "", wording.strip(), ""]
    supporting = record.fields.get("supporting_evidence", "")
    if supporting and supporting != "[]":
        lines.append(f"Supporting evidence: {supporting}")
    contradicting = record.fields.get("contradicting_evidence", "")
    if contradicting and contradicting != "[]":
        lines.append(f"Contradicting evidence: {contradicting}")
    if record.kind == "requirement":
        decision = record.fields.get("decision", "")
        if decision:
            lines.append(f"Authorised by: {decision}")
    status_bits = [f"status={record.fields.get('status', '')}"]
    if record.fields.get("evidence_support_state"):
        status_bits.append(f"evidence_support_state={record.fields['evidence_support_state']}")
    lines.append(f"Status: {', '.join(status_bits)}")
    lines.append(f"Provenance: {label}")
    body = "\n".join(lines).rstrip() + "\n"
    # The hashed text must be byte-identical to what `detect_anchor_changes`
    # reads back (everything strictly between the two marker comments,
    # including the newline right after the opening one) -- hashing `body`
    # alone here while reading back `"\n" + body` there was a real bug this
    # module's own test suite caught (a no-op render was misclassified as
    # an edit). `between` is what is hashed and what is literally written.
    between = f"\n{body}"
    projection_hash = sha256_text(between)
    return (
        f"<!-- codecompass-knowledge: {record.record_id} "
        f"semantic-sha256:{semantic_hash} projection-sha256:{projection_hash} -->"
        f"{between}"
        f"{_ANCHOR_CLOSE}\n"
    )


def _extract_existing_candidate_text(path: Path) -> str:
    """Preserves a human's own not-yet-processed candidate-region content
    across a re-render (§2.3's own "no erased prose improvements"
    guarantee, extended to unprocessed candidate submissions)."""
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    start = text.find(CANDIDATE_START)
    end = text.find(CANDIDATE_END)
    if start == -1 or end == -1 or end < start:
        return ""
    return text[start + len(CANDIDATE_START) : end]


def _render_candidate_section(existing_text: str) -> str:
    return (
        "## Candidate additions\n\n"
        f"{_CANDIDATE_INSTRUCTIONS}\n\n"
        f"{CANDIDATE_START}{existing_text}{CANDIDATE_END}\n"
    )


def render_slug(project_root: Path, slug: str) -> list[Path]:
    """Stage 4 of §8's pipeline (and the initial projection). Pure,
    deterministic, no AI call, safe to run any number of times — a
    record whose own content is unchanged since last render reproduces
    byte-identical prose for its own block (§2.3)."""
    records = load_slug_records(slug_dir(project_root, slug))
    cache = read_presentation_cache(presentation_cache_path(project_root, slug))
    by_file: dict[str, list[KnowledgeRecord]] = {}
    for record in records.values():
        target = _file_for_record(record)
        if target:
            by_file.setdefault(target, []).append(record)

    out_dir = intermediate_dir(project_root, slug)
    written: list[Path] = []
    for filename in sorted(set(by_file) | set(_CORE_FILES)):
        file_records = sorted(by_file.get(filename, []), key=lambda r: r.record_id)
        if not file_records and filename not in _CORE_FILES:
            continue  # never an empty placeholder file (§4.1) for an optional file
        blocks = [render_block(r, records, cache) for r in file_records]
        target_path = out_dir / filename
        existing_candidate = _extract_existing_candidate_text(target_path)
        title = filename[:-3].replace("-", " ")
        header = f"# {slug} — {title}\n\n"
        body = "\n".join(blocks) + ("\n\n" if blocks else "")
        content = header + body + _render_candidate_section(existing_candidate)
        out_dir.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")
        written.append(target_path)
    return written


# ---------------------------------------------------------------------------
# Stage 1 — mechanical detection (§8). No AI call, no canonical mutation.
# ---------------------------------------------------------------------------


@dataclass
class AnchorFinding:
    record_id: str
    file: Path
    base_semantic_hash: str
    base_projection_hash: str
    current_semantic_hash: str | None
    current_projection_hash: str
    canonical_changed: bool
    projection_edited: bool
    case: str  # "noop" | "candidate" | "refresh" | "concurrent_conflict"
    body_text: str


@dataclass
class CandidateFinding:
    file: Path
    index: int
    text: str
    cited_decision: str | None


def detect_anchor_changes(project_root: Path, slug: str) -> list[AnchorFinding]:
    """§1.5's dual-hash classification, computed fresh against the live
    canonical records and the live projection text — never comparing a
    semantic hash against a projection hash (the corrected model)."""
    records = load_slug_records(slug_dir(project_root, slug))
    findings: list[AnchorFinding] = []
    for md_path in sorted(intermediate_dir(project_root, slug).glob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        pos = 0
        while True:
            match = _ANCHOR_OPEN_RE.search(text, pos)
            if not match:
                break
            record_id, base_semantic, base_projection = match.groups()
            close_idx = text.find(_ANCHOR_CLOSE, match.end())
            if close_idx == -1:
                pos = match.end()
                continue
            raw_body = text[match.end() : close_idx]
            current_projection_hash = sha256_text(raw_body)
            record = records.get(record_id)
            if record is None:
                current_semantic_hash = None
                canonical_changed = True  # the record itself was deleted/moved
            else:
                current_semantic_hash = sha256_text(record.path.read_text(encoding="utf-8"))
                canonical_changed = current_semantic_hash != base_semantic
            projection_edited = current_projection_hash != base_projection
            if not canonical_changed and not projection_edited:
                case = "noop"
            elif not canonical_changed and projection_edited:
                case = "candidate"
            elif canonical_changed and not projection_edited:
                case = "refresh"
            else:
                case = "concurrent_conflict"
            findings.append(
                AnchorFinding(
                    record_id,
                    md_path,
                    base_semantic,
                    base_projection,
                    current_semantic_hash,
                    current_projection_hash,
                    canonical_changed,
                    projection_edited,
                    case,
                    raw_body,
                )
            )
            pos = close_idx + len(_ANCHOR_CLOSE)
    return findings


def detect_candidate_additions(project_root: Path, slug: str) -> list[CandidateFinding]:
    """§4.4 — only text strictly between the candidate-region markers is
    ever read as a proposal; everything else in the file is narrative
    framing this function never looks at."""
    findings: list[CandidateFinding] = []
    for md_path in sorted(intermediate_dir(project_root, slug).glob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        start = text.find(CANDIDATE_START)
        end = text.find(CANDIDATE_END)
        if start == -1 or end == -1 or end < start:
            continue
        region = text[start + len(CANDIDATE_START) : end].strip("\n")
        if not region.strip():
            continue
        blocks = [b.strip() for b in re.split(r"\n\s*\n", region) if b.strip()]
        for index, block in enumerate(blocks):
            decision_ids = [i for i in _extract_id_strings(block) if i.startswith("DEC-")]
            findings.append(
                CandidateFinding(md_path, index, block, decision_ids[0] if decision_ids else None)
            )
    return findings


def apply_automatic_refreshes(project_root: Path, slug: str) -> list[str]:
    """`canonical_changed=True, projection_edited=False` (§8's table) needs
    no human review at all — it's just `render_slug` re-run; exposed here
    so `select-candidates` can report how many blocks it silently refreshed
    without creating a manifest entry for them."""
    findings = [f for f in detect_anchor_changes(project_root, slug) if f.case == "refresh"]
    if findings:
        render_slug(project_root, slug)
    return [f.record_id for f in findings]


def write_manifest(
    project_root: Path,
    slug: str,
    anchor_findings: list[AnchorFinding],
    candidate_findings: list[CandidateFinding],
) -> Path | None:
    """The reconciliation manifest (§8/§11) — durable, committed, TOML,
    reusing the frozen-snapshot format's own shape. Returns `None` (and
    writes nothing) if there is genuinely nothing to review."""
    reviewable = [f for f in anchor_findings if f.case in ("candidate", "concurrent_conflict")]
    if not reviewable and not candidate_findings:
        return None
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    manifest_path = reconciliation_dir(project_root, slug) / f"{ts}.toml"
    lines = [
        f'manifest_id = "{slug}@{ts}"',
        f'created = "{datetime.now(UTC).isoformat()}"',
        f'slug = "{slug}"',
        "",
    ]
    for f in reviewable:
        state = "concurrent_conflict" if f.case == "concurrent_conflict" else "pending"
        lines += [
            "[[items]]",
            'kind = "anchor_edit"',
            f'record_id = "{f.record_id}"',
            f"file = {_toml_escape(str(f.file.relative_to(project_root)))}",
            f'base_semantic_hash = "{f.base_semantic_hash}"',
            f'base_projection_hash = "{f.base_projection_hash}"',
            f"current_semantic_hash = {_toml_escape(f.current_semantic_hash or '')}",
            f'current_projection_hash = "{f.current_projection_hash}"',
            f'state = "{state}"',
            f"edited_text = {_toml_escape(f.body_text)}",
            '# Stage 2 (human/agent review) sets these two before apply:',
            'decision = "undecided"  # "accept" or "reject"',
            "semantic_change = false  # true if this is more than wording",
            "",
        ]
    for c in candidate_findings:
        lines += [
            "[[items]]",
            'kind = "candidate_addition"',
            f"file = {_toml_escape(str(c.file.relative_to(project_root)))}",
            f"index = {c.index}",
            f"text = {_toml_escape(c.text)}",
            f"cited_decision = {_toml_escape(c.cited_decision or '')}",
            'state = "pending"',
            '# Stage 2 (human/agent review) sets this before apply:',
            'decision = "undecided"  # "accept" or "reject"',
            "",
        ]
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return manifest_path


# ---------------------------------------------------------------------------
# Stage 3 — apply (§8/§11). The only stage allowed to write a canonical
# record. Re-validates mechanically; never trusts Stage 2's own say-so.
# ---------------------------------------------------------------------------


@dataclass
class ApplyOutcome:
    ok: bool
    item: dict
    reason: str
    new_record_id: str | None = None


@dataclass
class ApplyResult:
    applied: list[ApplyOutcome] = field(default_factory=list)
    skipped: list[ApplyOutcome] = field(default_factory=list)


_RECORD_FIELD_ORDER = [
    "id",
    "kind",
    "statement",
    "example",
    "derivation",
    "supporting_evidence",
    "contradicting_evidence",
    "derived_by",
    "repository_revision",
    "timestamp",
    "status",
    "basis",
    "evidence_support_state",
    "assertion_kind",
    "decision",
    "depends_on",
    "supersedes",
]


def _next_id(sdir: Path, prefix: str) -> str:
    slug_token = re.sub(r"[^A-Z0-9]", "", sdir.name.upper())[:12] or "SLUG"
    existing: list[int] = []
    for path in sdir.glob(f"{prefix}-*.yaml"):
        match = re.match(rf"{prefix}-[A-Z0-9]+-(\d+)\.yaml$", path.name)
        if match:
            existing.append(int(match.group(1)))
    next_n = (max(existing) + 1) if existing else 1
    return f"{prefix}-{slug_token}-{next_n:03d}"


def _write_record(path: Path, fields: dict[str, str]) -> None:
    lines: list[str] = []
    seen: set[str] = set()
    for key in _RECORD_FIELD_ORDER:
        if key not in fields:
            continue
        value = str(fields[key])
        if key in ("statement", "example") and "\n" in value:
            lines.append(f"{key}: |")
            lines.extend(f"  {part}" for part in value.splitlines())
        elif key in ("statement", "example") and len(value) > 60:
            lines.append(f"{key}: >")
            lines.append(f"  {value}")
        else:
            lines.append(f"{key}: {value}")
        seen.add(key)
    for key, value in fields.items():
        if key not in seen:
            lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _apply_anchor_edit(project_root: Path, slug: str, item: dict) -> ApplyOutcome:
    record_id = item.get("record_id", "")
    sdir = slug_dir(project_root, slug)
    records = load_slug_records(sdir)
    record = records.get(record_id)
    if record is None:
        return ApplyOutcome(False, item, "record no longer exists")
    live_hash = sha256_text(record.path.read_text(encoding="utf-8"))
    if live_hash != item.get("base_semantic_hash"):
        return ApplyOutcome(
            False,
            item,
            "apply-time race: the canonical record changed since detection "
            "(base_semantic_hash no longer matches) — refusing to write; "
            "re-run `knowledge select-candidates` and review again",
        )
    if not item.get("semantic_change", False):
        cache_path = presentation_cache_path(project_root, slug)
        cache = read_presentation_cache(cache_path)
        cache[record_id] = PresentationEntry(
            accepted_for_semantic_hash=live_hash,
            wording=item.get("edited_text", "").strip(),
        )
        write_presentation_cache(cache_path, cache)
        return ApplyOutcome(True, item, "presentation cache updated; canonical record untouched")
    # A semantic edit never overwrites the original record directly (§7) —
    # it always creates a new, competing candidate Claim instead.
    new_id = _next_id(sdir, "CL")
    fields = {
        "id": new_id,
        "kind": "claim",
        "statement": item.get("edited_text", "").strip(),
        "derivation": "null",
        "supporting_evidence": "[]",
        "contradicting_evidence": "[]",
        "derived_by": '"external:unknown"',
        "repository_revision": '"working tree"',
        "timestamp": f'"{datetime.now(UTC).isoformat()}"',
        "status": "proposed",
        "basis": "proposed_policy",
        "depends_on": f"[{record_id}]",
    }
    _write_record(sdir / f"{new_id}.yaml", fields)
    return ApplyOutcome(True, item, f"created {new_id} as a competing candidate", new_id)


def _apply_candidate_addition(project_root: Path, slug: str, item: dict) -> ApplyOutcome:
    sdir = slug_dir(project_root, slug)
    records = load_slug_records(sdir)
    cited = item.get("cited_decision") or ""
    decision_record = records.get(cited) if cited else None
    if (
        decision_record is not None
        and decision_record.kind == "decision"
        and decision_record.fields.get("status") == "approved"
    ):
        new_id = _next_id(sdir, "REQ")
        fields = {
            "id": new_id,
            "kind": "requirement",
            "statement": item.get("text", ""),
            "example": (
                "Given/When/Then: to be refined during review "
                "(auto-created from an external candidate addition)."
            ),
            "decision": cited,
            "status": "proposed",
        }
    else:
        # No cited id, or it doesn't resolve to an approved Decision --
        # falls back to a Claim-level proposal, never rejected outright
        # and never inventing/approving a Decision on the author's behalf
        # (§4.4/§14.3).
        new_id = _next_id(sdir, "CL")
        fields = {
            "id": new_id,
            "kind": "claim",
            "statement": item.get("text", ""),
            "derivation": "null",
            "supporting_evidence": "[]",
            "contradicting_evidence": "[]",
            "derived_by": '"external:unknown"',
            "repository_revision": '"working tree"',
            "timestamp": f'"{datetime.now(UTC).isoformat()}"',
            "status": "proposed",
            "basis": "proposed_policy",
        }
    _write_record(sdir / f"{new_id}.yaml", fields)
    return ApplyOutcome(True, item, f"created {new_id}", new_id)


def apply_manifest(project_root: Path, manifest_path: Path) -> ApplyResult:
    """The only function in this module (and the only CLI command, §11)
    allowed to write `planning/knowledge/*/*.yaml`. Never trusts Stage 2's
    own annotation at face value — every item is mechanically re-checked."""
    import tomllib

    data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    slug = data.get("slug", "")
    result = ApplyResult()
    for item in data.get("items", []):
        decision = item.get("decision", "undecided")
        if decision == "reject":
            result.skipped.append(ApplyOutcome(False, item, "rejected at review"))
            continue
        if decision != "accept":
            result.skipped.append(
                ApplyOutcome(False, item, "not yet reviewed (decision=undecided)")
            )
            continue
        if item.get("state") == "concurrent_conflict":
            result.skipped.append(
                ApplyOutcome(
                    False,
                    item,
                    "unresolved concurrent-change conflict — refusing to apply "
                    "either side; re-render and re-review this item first",
                )
            )
            continue
        if item.get("kind") == "anchor_edit":
            outcome = _apply_anchor_edit(project_root, slug, item)
        elif item.get("kind") == "candidate_addition":
            outcome = _apply_candidate_addition(project_root, slug, item)
        else:
            outcome = ApplyOutcome(False, item, f"unknown item kind {item.get('kind')!r}")
        (result.applied if outcome.ok else result.skipped).append(outcome)
    return result


# ---------------------------------------------------------------------------
# Advisory status / grounding coverage (§9.6/§11) — never blocking, never
# mutates anything.
# ---------------------------------------------------------------------------


@dataclass
class StatusReport:
    needs_review: list[str] = field(default_factory=list)
    concurrent_conflicts: list[str] = field(default_factory=list)
    grounding: dict[str, dict] = field(default_factory=dict)


def _list_slugs(project_root: Path) -> list[str]:
    kdir = knowledge_dir(project_root)
    if not kdir.is_dir():
        return []
    return sorted(p.name for p in kdir.iterdir() if p.is_dir())


def knowledge_status(project_root: Path, slug: str | None = None) -> StatusReport:
    slugs = [slug] if slug else _list_slugs(project_root)
    report = StatusReport()
    for s in slugs:
        records = load_slug_records(slug_dir(project_root, s))
        for record in records.values():
            if record.kind not in ("claim", "requirement"):
                continue
            if record.fields.get("status") == "contradicted":
                report.needs_review.append(f"{record.record_id} ({s}): status=contradicted")
            elif record.fields.get("status") == "proposed" and not record.fields.get(
                "evidence_support_state"
            ):
                report.needs_review.append(
                    f"{record.record_id} ({s}): proposed, not yet evidence-checked"
                )
        rdir = reconciliation_dir(project_root, s)
        if rdir.is_dir():
            manifests = sorted(rdir.glob("*.toml"))
            if manifests:
                import tomllib

                data = tomllib.loads(manifests[-1].read_text(encoding="utf-8"))
                for item in data.get("items", []):
                    if item.get("state") == "concurrent_conflict" and item.get(
                        "decision", "undecided"
                    ) != "accept":
                        report.concurrent_conflicts.append(
                            f"{item.get('record_id')} ({s}): unresolved, "
                            f"see {manifests[-1].name}"
                        )

    for doc_name in ("README.md", "CONTRIBUTING.md"):
        doc_path = project_root / doc_name
        if not doc_path.is_file():
            continue
        text = doc_path.read_text(encoding="utf-8")
        marked_regions = parse_grounding_markers(text)
        grounded_ids: list[str] = []
        needing_review: list[str] = []
        for ids, _region in marked_regions:
            grounded_ids.extend(ids)
            for record_id in ids:
                for s in slugs:
                    record = load_slug_records(slug_dir(project_root, s)).get(record_id)
                    if record and record.fields.get("status") == "contradicted":
                        needing_review.append(record_id)
        report.grounding[doc_name] = {
            "grounded_regions": len(marked_regions),
            "grounded_ids": sorted(set(grounded_ids)),
            # Advisory only (§9.6) — this build reports regions whose own
            # cited record is currently contradicted/unresolved as the
            # practical "needs a look" signal, rather than a raw text-diff
            # against a stored baseline (no such baseline is kept). Never
            # blocking; see docs/codecompass-knowledge-workflow.md.
            "regions_needing_review": sorted(set(needing_review)),
        }
    return report
