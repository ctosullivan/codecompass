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
_CANONICAL_STATEMENT_RE = re.compile(r"<!--\s*codecompass-canonical-statement:\s*(.*?)\s*-->")


def extract_canonical_statement(block_text: str) -> str | None:
    """Corrective pass, point 5: when a rendered block is showing accepted
    presentation wording instead of the record's own canonical statement,
    the canonical statement is still embedded as a machine-facing HTML
    comment (invisible to an ordinary rendered-Markdown reader, present in
    the raw text any agent/dev-context consumer actually reads) — this
    reads it back out. Returns `None` for a block with no override in
    effect (the visible wording already *is* the canonical statement in
    that case)."""
    match = _CANONICAL_STATEMENT_RE.search(block_text)
    if not match:
        return None
    return match.group(1).replace("--&gt;", "-->")

_GROUNDING_OPEN_RE = re.compile(r"<!--\s*codecompass-grounded-by:\s*(.+?)\s*-->")
_GROUNDING_CLOSE = "<!-- /codecompass-grounded-by -->"
_REGION_ID_RE = re.compile(r"\bregion:([A-Za-z0-9_-]+)\b")


class DuplicateGroundingRegionIdError(ValueError):
    """A `region:<id>` token (second corrective pass, point 10) must be
    unique project-wide — two markers claiming the same stable identity
    is ambiguous and must fail closed rather than silently pick one."""


def parse_grounding_markers(text: str) -> list[tuple[list[str], str, str | None]]:
    """Every explicit `codecompass-grounded-by` region in `text` (§9.2) —
    returns `(cited_record_ids, region_body, region_id)` triples. The
    optional `region_id` (second corrective pass, point 10) comes from a
    `region:<id>` token anywhere in the marker's own header, e.g.
    `<!-- codecompass-grounded-by: CL-X region:readme-sync-behaviour -->`
    — a stable identity that survives insertion/reordering, unlike a
    positional index. A marker with no `region:` token still works (back-
    compat with every marker this phase shipped before this correction);
    its own identity falls back to `{doc_name}::{index}`, which is
    fragile under insertion but never breaks outright. Used in both
    directions: given a changed record id, find which doc regions cite it
    (`find_grounded_doc_regions`); given a changed doc region, read off
    the exact ids it already cites — both deterministic, no dispatch call
    needed for the strong, explicitly-grounded case."""
    results: list[tuple[list[str], str, str | None]] = []
    pos = 0
    while True:
        match = _GROUNDING_OPEN_RE.search(text, pos)
        if not match:
            break
        close_idx = text.find(_GROUNDING_CLOSE, match.end())
        if close_idx == -1:
            pos = match.end()
            continue
        header = match.group(1)
        ids = _extract_id_strings(header)
        region_id_match = _REGION_ID_RE.search(header)
        region_id = region_id_match.group(1) if region_id_match else None
        results.append((ids, text[match.end() : close_idx], region_id))
        pos = close_idx + len(_GROUNDING_CLOSE)
    return results


def _region_state_key(doc_name: str, index: int, region_id: str | None) -> str:
    """The stable identity a grounding baseline is keyed by — an explicit
    `region:<id>` when present (project-wide namespace, survives insertion/
    reordering within its own doc), else the legacy, insertion-fragile
    positional fallback (`decisions/0074`, point 10)."""
    return f"id:{region_id}" if region_id else f"{doc_name}::{index}"


def _check_no_duplicate_region_ids(
    project_root: Path, doc_names: tuple[str, ...]
) -> None:
    seen: dict[str, tuple[str, int]] = {}
    for doc_name in doc_names:
        doc_path = project_root / doc_name
        if not doc_path.is_file():
            continue
        text = doc_path.read_text(encoding="utf-8")
        for index, (_ids, _region, region_id) in enumerate(parse_grounding_markers(text)):
            if region_id is None:
                continue
            if region_id in seen:
                other_doc, other_index = seen[region_id]
                raise DuplicateGroundingRegionIdError(
                    f"region id {region_id!r} is used by both {other_doc} "
                    f"region #{other_index} and {doc_name} region #{index} — "
                    "region ids must be unique project-wide"
                )
            seen[region_id] = (doc_name, index)


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
        for ids, region, _region_id in parse_grounding_markers(text):
            if record_id in ids:
                hits.append((doc_path, region))
    return hits


# ---------------------------------------------------------------------------
# Grounded project-document reconciliation (`decisions/0073`, point 3) —
# completes §9.2's bidirectional flow: a factual edit to an explicitly
# grounded region now becomes a real reconciliation candidate, not just
# something `find_grounded_doc_regions` can locate after the fact.
# ---------------------------------------------------------------------------

_DEFAULT_GROUNDED_DOCS = ("README.md", "CONTRIBUTING.md")


def grounding_state_path(project_root: Path) -> Path:
    return knowledge_dir(project_root) / ".grounding-state.toml"


def _read_simple_toml_tables(path: Path) -> dict[str, dict]:
    if not path.is_file():
        return {}
    import tomllib

    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_simple_toml_tables(path: Path, tables: dict[str, dict]) -> None:
    lines: list[str] = []
    for table_name in sorted(tables):
        lines.append(f"[{_toml_escape(table_name)}]")
        for key in sorted(tables[table_name]):
            lines.append(f"{_toml_escape(key)} = {_serialize_toml_value(tables[table_name][key])}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _find_record_in_any_slug(project_root: Path, record_id: str) -> KnowledgeRecord | None:
    for slug in _list_slugs(project_root):
        record = load_slug_records(slug_dir(project_root, slug)).get(record_id)
        if record is not None:
            return record
    return None


def _owning_slug_for_record(project_root: Path, record_id: str) -> str | None:
    for slug in _list_slugs(project_root):
        if record_id in load_slug_records(slug_dir(project_root, slug)):
            return slug
    return None


def _current_cited_hashes(project_root: Path, cited_ids: list[str]) -> dict[str, str]:
    current: dict[str, str] = {}
    for rid in cited_ids:
        record = _find_record_in_any_slug(project_root, rid)
        if record is not None:
            current[rid] = sha256_text(record.path.read_text(encoding="utf-8"))
    return current


@dataclass
class GroundedRegionFinding:
    doc_name: str
    index: int
    region_id: str | None
    cited_ids: list[str]
    region_text: str
    region_hash: str
    case: str  # "new" | "noop" | "doc_candidate" | "claims_changed" | "concurrent_conflict"

    @property
    def state_key(self) -> str:
        return _region_state_key(self.doc_name, self.index, self.region_id)


def detect_grounded_region_changes(
    project_root: Path, doc_names: tuple[str, ...] = _DEFAULT_GROUNDED_DOCS
) -> list[GroundedRegionFinding]:
    """Dual-baseline detection for explicitly grounded project-document
    regions, analogous to intermediate-doc anchor reconciliation (§1.5) —
    a safe concurrency model for docs, per `decisions/0073` point 3.
    Compares the region's own current text hash, and each cited record's
    own current content hash, against a persisted baseline
    (`.grounding-state.toml`), keyed by each region's own stable identity
    (`decisions/0074`, point 10 — an explicit `region:<id>` token when
    present, a positional fallback otherwise).

    Entirely read-only (`decisions/0074`, point 1): a region with no
    baseline entry at all is reported as `"new"` but its baseline is
    *not* established here — establishing it is the caller's own explicit
    act (`establish_new_region_baselines`), since even that is a state
    mutation this function itself must never perform as a side effect of
    merely looking. Raises `DuplicateGroundingRegionIdError` if two
    markers claim the same explicit `region:<id>`.

    **The cited-id set itself is part of this region's own concurrency
    identity (`decisions/0075`, point 2)**: a marker's own list of cited
    ids changing — an id added or removed — is a relationship-level
    change even when the region's own prose and every still-cited
    record's own content are both byte-identical to the baseline. Order
    is not significant (reordering `CL-A, CL-B` to `CL-B, CL-A` is not a
    change), so membership is compared as a set, not a sequence; a
    changed set is treated the same as a changed region body (`case`
    becomes `"doc_candidate"`, never silently `"noop"`), since both are
    edits to the region's own definition, as opposed to a cited record's
    *own* content moving independently elsewhere.
    """
    _check_no_duplicate_region_ids(project_root, doc_names)
    state = _read_simple_toml_tables(grounding_state_path(project_root))
    findings: list[GroundedRegionFinding] = []
    for doc_name in doc_names:
        doc_path = project_root / doc_name
        if not doc_path.is_file():
            continue
        text = doc_path.read_text(encoding="utf-8")
        for index, (ids, region, region_id) in enumerate(parse_grounding_markers(text)):
            key = _region_state_key(doc_name, index, region_id)
            baseline = state.get(key)
            region_hash = sha256_text(region)
            if baseline is None:
                findings.append(
                    GroundedRegionFinding(
                        doc_name, index, region_id, ids, region, region_hash, "new"
                    )
                )
                continue
            current_hashes = _current_cited_hashes(project_root, ids)
            base_cited_ids = baseline.get("cited_ids", [])
            base_cited_hashes = baseline.get("cited_hashes", [])
            baseline_by_id = dict(zip(base_cited_ids, base_cited_hashes, strict=False))
            region_changed = region_hash != baseline.get("region_hash", "")
            # decisions/0075, point 2: the cited-id SET is itself part of
            # this region's own identity -- order-insensitive (a mere
            # reorder is not a change), but an id added or removed is,
            # even when the region's own prose is untouched.
            membership_changed = sorted(ids) != sorted(base_cited_ids)
            # Content drift is only meaningful for an id cited in BOTH the
            # baseline and the live marker -- an id's own absence/presence
            # is membership_changed's concern, not this one's, so a newly
            # added or just-removed id is never double-counted as "its own
            # content changed" too.
            common_ids = set(ids) & set(base_cited_ids)
            claims_changed = [
                rid
                for rid in common_ids
                if rid in current_hashes and current_hashes.get(rid) != baseline_by_id.get(rid)
            ]
            structural_changed = region_changed or membership_changed
            if not structural_changed and not claims_changed:
                case = "noop"
            elif structural_changed and not claims_changed:
                case = "doc_candidate"
            elif not structural_changed and claims_changed:
                case = "claims_changed"
            else:
                case = "concurrent_conflict"
            findings.append(
                GroundedRegionFinding(doc_name, index, region_id, ids, region, region_hash, case)
            )
    return findings


def _write_region_baseline(
    project_root: Path,
    key: str,
    region_hash: str,
    cited_ids: list[str],
    cited_hashes: dict[str, str],
) -> None:
    state = _read_simple_toml_tables(grounding_state_path(project_root))
    state[key] = {
        "region_hash": region_hash,
        "cited_ids": cited_ids,
        "cited_hashes": [cited_hashes.get(rid, "") for rid in cited_ids],
    }
    _write_simple_toml_tables(grounding_state_path(project_root), state)


def establish_new_region_baselines(
    project_root: Path, findings: list[GroundedRegionFinding]
) -> list[str]:
    """The only automatic baseline write left (`decisions/0074`, point 1)
    — bootstrapping a region's *first-ever* baseline is not "clearing
    drift" (there is no prior state to lose), unlike advancing an
    existing baseline past a detected `doc_candidate`/`claims_changed`/
    `concurrent_conflict`, which now only ever happens through an
    explicit resolution: `apply` for a `doc_candidate`
    (`_apply_doc_region_edit`), or the dedicated `doc-acknowledge-stale`
    command for `claims_changed`. A `concurrent_conflict` is never
    auto-resolved at all — it keeps being reported until the underlying
    facts actually change again. Returns the state keys established."""
    established: list[str] = []
    for finding in findings:
        if finding.case != "new":
            continue
        current_hashes = _current_cited_hashes(project_root, finding.cited_ids)
        _write_region_baseline(
            project_root, finding.state_key, finding.region_hash, finding.cited_ids, current_hashes
        )
        established.append(finding.state_key)
    return established


def acknowledge_stale_grounded_region(
    project_root: Path, doc_name: str, region_locator: str
) -> GroundedRegionFinding | None:
    """Explicit resolution for a `claims_changed` finding (`decisions/0074`,
    point 1) — a cited record moved, the document's own prose didn't; a
    human has looked at the region and decided the prose still reads
    accurately (or has edited it separately as its own `doc_candidate`
    reconciliation). `region_locator` is either an explicit `region:<id>`
    value or a positional index as a string (`"0"`, `"1"`, ...), matching
    whichever identity the region's own marker actually uses. Returns the
    finding that was acknowledged, or `None` if no matching, genuinely
    `claims_changed` region was found (never silently acknowledges a
    `doc_candidate` or `concurrent_conflict` — those have their own,
    separate resolution paths)."""
    findings = detect_grounded_region_changes(project_root, (doc_name,))
    for finding in findings:
        locator_matches = (
            finding.region_id == region_locator or str(finding.index) == region_locator
        )
        if locator_matches and finding.case == "claims_changed":
            current_hashes = _current_cited_hashes(project_root, finding.cited_ids)
            _write_region_baseline(
                project_root,
                finding.state_key,
                finding.region_hash,
                finding.cited_ids,
                current_hashes,
            )
            return finding
    return None


def write_doc_candidates_to_manifests(
    project_root: Path, findings: list[GroundedRegionFinding]
) -> dict[str, Path]:
    """For every `doc_candidate` finding (a grounded region's own prose
    changed, its cited Claims didn't), writes a manifest item into the
    *owning slug of its first cited id* — reusing the exact same
    manifest/apply/idempotency machinery `write_manifest`/`apply_manifest`
    already provide for intermediate-doc candidates, rather than a second,
    parallel apply path (`decisions/0073`, point 3). A region citing ids
    from more than one slug attaches to the first one's own slug only —
    documented, not silently arbitrary. Returns `{slug: manifest_path}`
    for every slug an item was actually written for; a finding whose
    cited ids resolve to no real slug at all is skipped (nowhere to attach
    it) but remains visible via `detect_grounded_region_changes` itself.

    Each item records both its own `base_region_hash` *and* every cited
    id's own content hash at write time (`decisions/0074`, point 2) — the
    concurrency check at apply time re-verifies both, not just the
    region's own text.
    """
    by_slug: dict[str, list[GroundedRegionFinding]] = {}
    for finding in findings:
        if finding.case != "doc_candidate":
            continue
        owning: str | None = None
        for rid in finding.cited_ids:
            owning = _owning_slug_for_record(project_root, rid)
            if owning:
                break
        if owning is None:
            continue
        by_slug.setdefault(owning, []).append(finding)

    written: dict[str, Path] = {}
    for slug, slug_findings in by_slug.items():
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        manifest_path = reconciliation_dir(project_root, slug) / f"{ts}-doc.toml"
        data: dict = {
            "manifest_id": f"{slug}@{ts}-doc",
            "created": datetime.now(UTC).isoformat(),
            "slug": slug,
            "items": [],
        }
        for finding in slug_findings:
            cited_hashes = _current_cited_hashes(project_root, finding.cited_ids)
            data["items"].append(
                {
                    "kind": "doc_region_edit",
                    "doc_name": finding.doc_name,
                    "region_index": finding.index,
                    "region_id": finding.region_id or "",
                    "cited_ids": finding.cited_ids,
                    "cited_hashes_at_detection": [
                        cited_hashes.get(rid, "") for rid in finding.cited_ids
                    ],
                    "region_text": finding.region_text,
                    "base_region_hash": finding.region_hash,
                    "state": "pending",
                    "decision": "undecided",
                    "semantic_change": False,
                }
            )
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(_serialize_manifest(data), encoding="utf-8")
        written[slug] = manifest_path
    return written


def _locate_live_region(
    doc_path: Path, region_index: int, region_id: str
) -> tuple[int, list[str], str] | None:
    """Resolves a manifest item's own recorded region back to its live
    position in the document — by stable `region_id` first when one was
    recorded, falling back to the positional index otherwise. Returns
    `(index, cited_ids, region_text)` or `None` if it no longer exists."""
    regions = parse_grounding_markers(doc_path.read_text(encoding="utf-8"))
    if region_id:
        for index, (ids, region, rid) in enumerate(regions):
            if rid == region_id:
                return index, ids, region
        return None
    if region_index < len(regions):
        ids, region, _rid = regions[region_index]
        return region_index, ids, region
    return None


def _add_cited_id_to_grounding_marker(
    doc_path: Path, region_index: int, region_id: str, new_id: str
) -> bool:
    """Post-apply grounding update (`decisions/0074`, point 4): after a
    semantic document edit is reconciled into a new Claim, the region's
    own marker is rewritten to additionally cite that new Claim —
    `grounded-by: CL-OLD, CL-NEW` — preserving the relationship to prior
    knowledge rather than silently dropping it, while making the new
    Claim deterministically discoverable from this region from now on.
    Rewrites only the one marker's own opening comment line; the region's
    own prose and every other marker in the document are untouched."""
    text = doc_path.read_text(encoding="utf-8")
    pos = 0
    index = 0
    while True:
        match = _GROUNDING_OPEN_RE.search(text, pos)
        if not match:
            return False
        header = match.group(1)
        region_id_match = _REGION_ID_RE.search(header)
        this_region_id = region_id_match.group(1) if region_id_match else None
        is_target = (
            (region_id and this_region_id == region_id) or (not region_id and index == region_index)
        )
        if is_target:
            ids = _extract_id_strings(header)
            if new_id in ids:
                return False  # already cited -- nothing to do, idempotent
            suffix = f" region:{this_region_id}" if this_region_id else ""
            new_header = f"{', '.join([*ids, new_id])}{suffix}"
            new_text = (
                text[: match.start()]
                + f"<!-- codecompass-grounded-by: {new_header} -->"
                + text[match.end() :]
            )
            doc_path.write_text(new_text, encoding="utf-8")
            return True
        close_idx = text.find(_GROUNDING_CLOSE, match.end())
        pos = (close_idx + len(_GROUNDING_CLOSE)) if close_idx != -1 else match.end()
        index += 1


def _apply_doc_region_edit(project_root: Path, slug: str, item: dict) -> ApplyOutcome:
    doc_name = item.get("doc_name", "")
    doc_path = project_root / doc_name
    if not doc_path.is_file():
        return ApplyOutcome(False, item, f"{doc_name} no longer exists")
    region_id = item.get("region_id") or ""
    region_index = item.get("region_index")
    safe_index = region_index if isinstance(region_index, int) else -1
    located = _locate_live_region(doc_path, safe_index, region_id)
    if located is None:
        return ApplyOutcome(False, item, "grounded region no longer exists")
    live_index, cited_ids, current_region = located
    current_region_hash = sha256_text(current_region)
    if current_region_hash != item.get("base_region_hash"):
        return ApplyOutcome(
            False,
            item,
            "apply-time race: the grounded region's own text changed since "
            "detection — refusing to write; re-run doc detection and review again",
        )
    # decisions/0075, point 3: the cited-id SET itself is part of this
    # region's own concurrency identity, not just its own text -- a
    # membership change (an id added or removed from the marker) between
    # detection and apply must fail closed exactly like a text change,
    # even when every still-cited record's own content hash still matches.
    # Order-insensitive, matching detection's own membership comparison
    # (decisions/0075, point 2) -- a mere reorder is never a conflict.
    manifest_cited_ids = item.get("cited_ids", [])
    if sorted(cited_ids) != sorted(manifest_cited_ids):
        return ApplyOutcome(
            False,
            item,
            "apply-time concurrency conflict: the grounded region's own cited-record "
            "membership changed since detection — refusing to write; re-run doc "
            "detection and review again",
        )
    # decisions/0074, point 2: concurrency protection equivalent to
    # intermediate-doc anchors -- re-verify every cited record's own
    # content hash too, not just the region's own text.
    expected_hashes = dict(
        zip(item.get("cited_ids", []), item.get("cited_hashes_at_detection", []), strict=False)
    )
    current_hashes = _current_cited_hashes(project_root, cited_ids)
    for rid in cited_ids:
        if current_hashes.get(rid, "") != expected_hashes.get(rid, ""):
            return ApplyOutcome(
                False,
                item,
                f"apply-time concurrency conflict: {rid}'s own content changed since "
                "detection — refusing to write; re-run doc detection and review again",
            )

    sdir = slug_dir(project_root, slug)
    records = load_slug_records(sdir)
    statement = current_region.strip()
    state_key = _region_state_key(doc_name, live_index, region_id or None)
    # The region's own hash is computed over the body text between the
    # marker comments only (never the opening comment's own header line),
    # so adding a cited id to the header below never changes this value --
    # computed once, reused for every baseline write in this function.
    region_hash_for_baseline = current_region_hash

    if not item.get("semantic_change", False):
        # decisions/0074, point 3: a presentation-only document edit is a
        # reviewer's own judgment call (never mechanically proven semantic
        # equivalence, same honesty as the intermediate-doc case) -- no
        # Claim is created; only the region's own baseline advances, and
        # only because this is the explicit, successful resolution this
        # phase requires before any baseline may move.
        _write_region_baseline(
            project_root, state_key, region_hash_for_baseline, cited_ids, current_hashes
        )
        return ApplyOutcome(
            True,
            item,
            "presentation-only document edit acknowledged; canonical knowledge unchanged",
        )

    existing = _find_existing_promoted_record(records, statement, kind="claim")
    if existing:
        _add_cited_id_to_grounding_marker(doc_path, live_index, region_id, existing)
        new_cited_ids = cited_ids if existing in cited_ids else [*cited_ids, existing]
        _write_region_baseline(
            project_root,
            state_key,
            region_hash_for_baseline,
            new_cited_ids,
            _current_cited_hashes(project_root, new_cited_ids),
        )
        return ApplyOutcome(
            True, item, f"already applied — {existing} already exists with this content", existing
        )

    new_id = _next_id(sdir, "CL")
    fields = {
        "id": new_id,
        "kind": "claim",
        "statement": statement,
        "derivation": "null",
        "supporting_evidence": "[]",
        "contradicting_evidence": "[]",
        "derived_by": '"external:unknown"',
        "repository_revision": '"working tree"',
        "timestamp": f'"{datetime.now(UTC).isoformat()}"',
        "status": "proposed",
        "depends_on": f"[{', '.join(cited_ids)}]" if cited_ids else "[]",
    }
    _write_record(sdir / f"{new_id}.yaml", fields)
    # decisions/0074, point 4: the region now also cites the new Claim,
    # preserving the relationship to prior knowledge rather than dropping
    # it, and making CL-new deterministically discoverable from this
    # region going forward.
    _add_cited_id_to_grounding_marker(doc_path, live_index, region_id, new_id)
    new_cited_ids = [*cited_ids, new_id]
    _write_region_baseline(
        project_root,
        state_key,
        region_hash_for_baseline,
        new_cited_ids,
        _current_cited_hashes(project_root, new_cited_ids),
    )
    return ApplyOutcome(True, item, f"created {new_id} from a grounded document edit", new_id)


# ---------------------------------------------------------------------------
# Advisory whole-document chunk tracking (§9.6, `decisions/0073` point 4) —
# reuses `doc_chunking.chunk_markdown`'s own already-proven heading-based
# chunking (the same mechanism `context-graph.db`'s `doc_chunks` table is
# built from) rather than inventing a parallel chunker. Purely advisory:
# never creates a canonical record, never blocks anything.
# ---------------------------------------------------------------------------


def doc_chunk_state_path(project_root: Path) -> Path:
    return knowledge_dir(project_root) / ".doc-chunk-state.toml"


def _grounding_marker_line_spans(text: str) -> list[tuple[int, int]]:
    """1-indexed inclusive `(start_line, end_line)` for every grounded
    region's own span — used to classify a changed chunk as grounded or
    not."""
    spans: list[tuple[int, int]] = []
    pos = 0
    while True:
        match = _GROUNDING_OPEN_RE.search(text, pos)
        if not match:
            break
        close_idx = text.find(_GROUNDING_CLOSE, match.end())
        if close_idx == -1:
            pos = match.end()
            continue
        start_line = text.count("\n", 0, match.start()) + 1
        end_line = text.count("\n", 0, close_idx) + 1
        spans.append((start_line, end_line))
        pos = close_idx + len(_GROUNDING_CLOSE)
    return spans


def _chunk_key(heading_path: str, start_line: int, end_line: int) -> str:
    return heading_path or f"<lines {start_line}-{end_line}>"


def detect_doc_chunk_changes(
    project_root: Path, doc_names: tuple[str, ...] = _DEFAULT_GROUNDED_DOCS
) -> dict[str, dict]:
    """Pure, read-only: for each doc, which heading-scoped chunks changed
    since the last `advance_doc_chunk_baseline` call, split into those
    overlapping an explicit grounding marker and those that don't. Never
    mutates the baseline itself — safe to call from `knowledge status`
    (advisory reporting) without side effects."""
    from codecompass.doc_chunking import chunk_markdown

    state = _read_simple_toml_tables(doc_chunk_state_path(project_root))
    report: dict[str, dict] = {}
    for doc_name in doc_names:
        doc_path = project_root / doc_name
        if not doc_path.is_file():
            continue
        text = doc_path.read_text(encoding="utf-8")
        chunks = chunk_markdown(text)
        grounded_spans = _grounding_marker_line_spans(text)
        baseline = state.get(doc_name, {})
        changed_grounded: list[str] = []
        changed_ungrounded: list[str] = []
        for chunk in chunks:
            key = _chunk_key(chunk.heading_path, chunk.start_line, chunk.end_line)
            if baseline.get(key) == chunk.content_hash:
                continue
            overlaps = any(
                chunk.start_line <= end and chunk.end_line >= start
                for start, end in grounded_spans
            )
            (changed_grounded if overlaps else changed_ungrounded).append(key)
        report[doc_name] = {
            "changed_grounded_chunks": changed_grounded,
            "changed_ungrounded_chunks": changed_ungrounded,
        }
    return report


def advance_doc_chunk_baseline(
    project_root: Path, doc_names: tuple[str, ...] = _DEFAULT_GROUNDED_DOCS
) -> None:
    """The explicit acknowledgement step (`decisions/0074`, point 1) —
    recomputes every chunk's current hash and persists it as the new
    baseline. **Never called automatically by detection or `knowledge
    status`** — a human must explicitly run
    `codecompass knowledge doc-acknowledge-chunks` to dismiss an advisory
    ungrounded-change finding; merely observing a change is not
    acknowledgement."""
    from codecompass.doc_chunking import chunk_markdown

    new_state: dict[str, dict] = {}
    for doc_name in doc_names:
        doc_path = project_root / doc_name
        if not doc_path.is_file():
            continue
        chunks = chunk_markdown(doc_path.read_text(encoding="utf-8"))
        new_state[doc_name] = {
            _chunk_key(c.heading_path, c.start_line, c.end_line): c.content_hash for c in chunks
        }
    _write_simple_toml_tables(doc_chunk_state_path(project_root), new_state)


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
    """OBSERVED / DECLARED / DECIDED / DERIVED / HISTORICAL / MIXED /
    UNCLASSIFIED, computed purely from existing kind/basis/status fields
    — see planning/phase-81-intermediate-knowledge-layer.md §1.2.1 and
    `decisions/0073` (corrective pass). Ambiguity (`basis: directly_stated`
    with a mixed evidence chain) always resolves to the more cautious
    label, never the stronger one.

    Corrected by `decisions/0073` (point 8): the original `directly_stated`
    branch used `Evidence.evidence_kind` as a proxy for "this evidence
    traces to a real Observation" — but the real schema
    (`docs/domain/concepts/evidence.md`) already has the actual link: "One
    Evidence record cites one or more Observations via its own
    `observations:` field, or cites source/doc/test directly... when no
    discrete Observation exists to point at." This now walks that real
    field instead of guessing from `evidence_kind`, which an Evidence
    citing a source/doc/test directly (no Observation at all) can equally
    carry.
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
    if not basis:
        # No basis at all -- an unclassified external hypothesis
        # (decisions/0073, point 7): never guess OBSERVED/DECLARED/DERIVED
        # for a candidate nobody has classified yet.
        return "UNCLASSIFIED"
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
            # The real link (docs/domain/concepts/evidence.md): Evidence
            # cites a real Observation via its own `observations:` field.
            # Must actually resolve to a real Observation record -- a
            # dangling/unresolvable id is not evidence of observation.
            observation_ids = _extract_id_strings(ev.fields.get("observations", ""))
            resolved_observations = [
                oid
                for oid in observation_ids
                if records_by_id.get(oid) is not None
                and records_by_id[oid].kind == "observation"
            ]
            if resolved_observations:
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
    "Plain prose becomes an unclassified Claim (a factual hypothesis, not "
    "yet evidence-backed) — this is the default and the common case. "
    "Merely mentioning a Decision id anywhere in your prose does NOT make "
    "your addition a Requirement, and merely using the word \"should\" or "
    "\"must\" does NOT make it declared intent — both need the explicit "
    "structured forms below.\n\n"
    "To propose a REQUIREMENT, start the block with a line reading exactly "
    '"Type: Requirement", followed by:\n'
    "  Decision: <id of an existing, already-approved Decision>\n"
    "  Statement: <the requirement itself, one line>\n"
    "  Example: <a Given/When/Then acceptance example>\n"
    "CodeCompass never invents a Decision on your behalf — a missing or "
    "not-yet-approved Decision id, or an Example that doesn't structurally "
    "read as Given/When/Then, falls back to an ordinary Claim using your "
    "Statement text, never a fabricated placeholder example.\n\n"
    'To declare project INTENT (a proposed policy, not yet a fact about '
    'the system), start the block with a line reading exactly "Type: '
    'Intent", followed by the intended behaviour as plain prose on the '
    "lines after it.\n\n"
    "Anything else — plain prose with no Type: header — stays an "
    "unclassified Claim until a reviewer looks at it."
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
    canonical_statement = (
        record.fields.get("statement")
        or record.fields.get("decides")
        or record.fields.get("what_it_shows")
        or ""
    ).strip()
    cached = presentation_cache.get(record.record_id)
    using_presentation_override = (
        cached is not None and cached.accepted_for_semantic_hash == semantic_hash
    )
    wording = cached.wording if using_presentation_override else canonical_statement
    label = derive_provenance_label(record, records_by_id)
    lines = [f"### {record.record_id}", ""]
    if using_presentation_override:
        # Corrective pass, point 5: `presentation_only` is a reviewer
        # classification, never mechanically proven semantic equivalence
        # (the apply step cannot verify that; see docs/codecompass-
        # knowledge-workflow.md). A human reader sees the accepted
        # wording as the main prose (clean, no visible duplication); an
        # agent/dev-context consumer reading the raw file always has the
        # real canonical statement available too, so cached wording can
        # never become the *only* representation of canonical meaning.
        escaped_canonical = canonical_statement.replace("-->", "--&gt;")
        lines.append(f"<!-- codecompass-canonical-statement: {escaped_canonical} -->")
    lines += [wording.strip(), ""]
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

    brief_path = render_phase_brief(project_root, slug, records, by_file)
    if brief_path:
        written.append(brief_path)
    return written


def render_phase_brief(
    project_root: Path,
    slug: str,
    records: dict[str, KnowledgeRecord] | None = None,
    by_file: dict[str, list[KnowledgeRecord]] | None = None,
) -> Path | None:
    """Phase knowledge package's own single entry point (§5.2) — not a
    separate representation of the same knowledge, a mechanically
    compiled index into the slug's own `intermediate/*.md` files: feature
    intent/domain knowledge (-> overview.md), invariants/constraints,
    interfaces/behaviours, test scenarios (-> tests-and-acceptance.md,
    when present), and open questions. No AI call — purely a count/list
    compiled from records this module already loaded for `render_slug`
    (callers may pass `records`/`by_file` to avoid a second file-system
    scan; both are recomputed when omitted, so this function also works
    standalone). Returns `None` for a slug with no records at all, rather
    than writing an empty placeholder (§4.1's own rule, applied here too).
    """
    sdir = slug_dir(project_root, slug)
    if records is None:
        records = load_slug_records(sdir)
    if not records:
        return None
    if by_file is None:
        by_file = {}
        for record in records.values():
            target = _file_for_record(record)
            if target:
                by_file.setdefault(target, []).append(record)

    def _ids(filename: str) -> list[str]:
        return sorted(r.record_id for r in by_file.get(filename, []))

    overview_ids = _ids("overview.md")
    invariant_ids = _ids("invariants-and-constraints.md")
    behaviour_ids = _ids("interfaces-and-behaviours.md")
    open_ids = _ids("open-questions-and-conflicts.md")
    requirement_ids = _ids("tests-and-acceptance.md")

    lines = [
        f"# {slug} — phase brief",
        "",
        "A single entry point into this slug's own `intermediate/*.md` "
        "files — mechanically compiled from the same records they "
        "render, never a separate representation of the same knowledge "
        "(planning/phase-81-intermediate-knowledge-layer.md §5.2).",
        "",
        f"- **Concepts, architecture, domain knowledge** — "
        f"`overview.md` ({len(overview_ids)}: {', '.join(overview_ids) or 'none yet'})",
        f"- **Invariants and constraints** — `invariants-and-constraints.md` "
        f"({len(invariant_ids)}: {', '.join(invariant_ids) or 'none yet'})",
        f"- **Interfaces and behaviours** — `interfaces-and-behaviours.md` "
        f"({len(behaviour_ids)}: {', '.join(behaviour_ids) or 'none yet'})",
        f"- **Open questions and conflicts** — `open-questions-and-conflicts.md` "
        f"({len(open_ids)}: {', '.join(open_ids) or 'none'})",
    ]
    if requirement_ids:
        lines.append(
            f"- **Test scenarios and acceptance behaviour** — "
            f"`tests-and-acceptance.md` ({len(requirement_ids)}: "
            f"{', '.join(requirement_ids)})"
        )
    lines.append("")
    lines.append(
        "Edge cases and compatibility constraints are recorded as ordinary "
        "Claims above (typically under invariants/constraints or open "
        "questions) rather than in a separate section here — see each "
        "file's own content for the real detail; this brief only indexes "
        "it."
    )
    lines.append("")

    brief_path = intermediate_dir(project_root, slug) / "phase-brief.md"
    existing_candidate = _extract_existing_candidate_text(brief_path)
    content = "\n".join(lines) + "\n" + _render_candidate_section(existing_candidate)
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    brief_path.write_text(content, encoding="utf-8")
    return brief_path


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
    text: str  # the exact raw block, as it appears live -- for presence/consumption checks
    # Explicit structured metadata (decisions/0073, points 6/7) — never
    # inferred from merely mentioning an id anywhere in ordinary prose.
    requirement_decision: str | None = None  # set only if "Type: Requirement"
    requirement_statement: str | None = None
    requirement_example: str | None = None
    declared_intent: bool = False  # set only if "Type: Intent"
    intent_statement: str | None = None  # the body, with the "Type: Intent" header stripped


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


_REQUIREMENT_FIELD_RE = re.compile(r"^(Decision|Statement|Example):\s*(.*)$")


def _parse_candidate_block(block: str) -> dict:
    """Explicit, structured candidate-block metadata (`decisions/0073`,
    points 6/7) — deliberately *not* inferred from merely mentioning an id
    or a word anywhere in ordinary prose. The first line of a block, if it
    is exactly `Type: Requirement` or `Type: Intent`, opts that block into
    one of two recognised structured shapes; anything else (the common
    case — plain prose) stays an ordinary, unclassified factual candidate.

    `Type: Requirement` expects `Decision:`/`Statement:`/`Example:` lines
    immediately following (single-line values) — a Requirement is only
    ever created from this explicit shape, never from prose that happens
    to mention an approved Decision's id.

    `Type: Intent` marks the block as expressing declared project intent
    (eligible for `basis: proposed_policy`) rather than the default,
    unclassified factual hypothesis a plain candidate becomes. Its own
    `"statement"` key (`decisions/0074`, point 7) is the block's body with
    the `Type: Intent` header line itself stripped — control metadata
    must never leak into canonical semantic content.
    """
    lines = block.splitlines()
    if not lines:
        return {}
    first = lines[0].strip()
    if first == "Type: Requirement":
        fields: dict[str, str] = {}
        for line in lines[1:]:
            match = _REQUIREMENT_FIELD_RE.match(line.strip())
            if match:
                fields[match.group(1).lower()] = match.group(2).strip()
        return {"requirement": fields}
    if first == "Type: Intent":
        statement = "\n".join(lines[1:]).strip()
        return {"intent": True, "statement": statement}
    return {}


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
            parsed = _parse_candidate_block(block)
            if "requirement" in parsed:
                req = parsed["requirement"]
                findings.append(
                    CandidateFinding(
                        md_path,
                        index,
                        block,
                        requirement_decision=req.get("decision"),
                        requirement_statement=req.get("statement"),
                        requirement_example=req.get("example"),
                    )
                )
            elif parsed.get("intent"):
                findings.append(
                    CandidateFinding(
                        md_path,
                        index,
                        block,
                        declared_intent=True,
                        intent_statement=parsed.get("statement") or "",
                    )
                )
            else:
                findings.append(CandidateFinding(md_path, index, block))
    return findings


def _replace_anchor_blocks(
    md_path: Path, replacements: dict[str, str]
) -> bool:
    """Targeted, in-place replacement of exactly the named anchors' own
    blocks — every other byte in the file (other anchors, the candidate
    region, any narrative prose) is left completely untouched. `replacements`
    maps `record_id` to the *exact* new full block text (anchor comments
    included) to substitute in place of the existing one. Returns whether
    anything was actually rewritten.

    Corrective pass, point 1: this replaces the original draft's own
    `apply_automatic_refreshes`, which called whole-slug `render_slug` the
    moment *any* anchor needed a safe refresh — regenerating every block in
    every file of the slug from scratch, including blocks a human/external
    tool had just edited but that had not yet been captured in a manifest.
    A refresh of record A must never erase record B's own pending edit in
    the same file; targeted single-block substitution is what guarantees
    that, since a block this function is not told to replace is never
    touched at the byte level.
    """
    text = md_path.read_text(encoding="utf-8")
    pieces: list[str] = []
    last_end = 0
    pos = 0
    changed = False
    while True:
        match = _ANCHOR_OPEN_RE.search(text, pos)
        if not match:
            break
        record_id = match.group(1)
        close_idx = text.find(_ANCHOR_CLOSE, match.end())
        if close_idx == -1:
            pos = match.end()
            continue
        full_end = close_idx + len(_ANCHOR_CLOSE)
        if record_id in replacements:
            pieces.append(text[last_end : match.start()])
            new_block = replacements[record_id]
            # The original slice stops right at the literal close marker,
            # with no trailing newline consumed (whatever newline(s) follow
            # it in the file are preserved verbatim via `text[last_end:]`
            # below) -- strip render_block's own single trailing "\n" so
            # substitution doesn't introduce an extra blank line.
            pieces.append(new_block[:-1] if new_block.endswith("\n") else new_block)
            last_end = full_end
            changed = True
        pos = full_end
    if not changed:
        return False
    pieces.append(text[last_end:])
    md_path.write_text("".join(pieces), encoding="utf-8")
    return True


def refresh_safe_anchors(
    project_root: Path, slug: str, anchor_findings: list[AnchorFinding] | None = None
) -> list[str]:
    """`canonical_changed=True, projection_edited=False` (§8's table)
    needs no human review at all — but, corrected per `decisions/0073`
    (point 1), this is now a *targeted* per-block substitution, never a
    whole-slug `render_slug`. Required flow: scan the complete projection,
    classify every anchor, partition into no-op/safe-refresh/candidate/
    concurrent-conflict, then refresh ONLY the safe-refresh blocks —
    candidate and concurrent-conflict blocks are never rewritten by this
    function, regardless of which file they share with a block being
    refreshed. Pass `anchor_findings` through when the caller already ran
    `detect_anchor_changes` once (the required flow classifies before any
    mutation happens); omitted, this recomputes them itself.
    """
    if anchor_findings is None:
        anchor_findings = detect_anchor_changes(project_root, slug)
    to_refresh = [f for f in anchor_findings if f.case == "refresh"]
    if not to_refresh:
        return []
    records = load_slug_records(slug_dir(project_root, slug))
    cache = read_presentation_cache(presentation_cache_path(project_root, slug))
    by_file: dict[Path, set[str]] = {}
    for finding in to_refresh:
        by_file.setdefault(finding.file, set()).add(finding.record_id)
    refreshed_ids: list[str] = []
    for md_path, record_ids in by_file.items():
        replacements = {
            rid: render_block(records[rid], records, cache)
            for rid in record_ids
            if rid in records
        }
        if replacements and _replace_anchor_blocks(md_path, replacements):
            refreshed_ids.extend(sorted(replacements))
    return refreshed_ids


def apply_automatic_refreshes(project_root: Path, slug: str) -> list[str]:
    """Deprecated name, kept as a thin alias for `refresh_safe_anchors` —
    the original draft's own whole-slug-render implementation is gone
    (`decisions/0073`, point 1); this now delegates to the corrected,
    targeted mechanism."""
    return refresh_safe_anchors(project_root, slug)


_MANIFEST_ITEM_FIELD_ORDER = [
    "kind",
    "record_id",
    "file",
    "base_semantic_hash",
    "base_projection_hash",
    "current_semantic_hash",
    "current_projection_hash",
    "edited_text",
    "index",
    "text",
    "requirement_decision",
    "requirement_statement",
    "requirement_example",
    "declared_intent",
    "intent_statement",
    "doc_name",
    "region_id",
    "region_index",
    "cited_ids",
    "cited_hashes_at_detection",
    "region_text",
    "base_region_hash",
    "state",
    "decision",
    "semantic_change",
    "proposed_basis",
    "applied_record_id",
    "applied_at",
]


def _serialize_toml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_escape(str(v)) for v in value) + "]"
    return _toml_escape(str(value))


def _serialize_manifest_item(item: dict) -> list[str]:
    """Field order is fixed (`_MANIFEST_ITEM_FIELD_ORDER`) for a stable,
    diffable manifest file; any field not in that list (forward
    compatibility) is still written, just after the known ones. Comments
    are not round-tripped — `tomllib` (the only reader, stdlib, read-only)
    discards them on parse, so preserving them through a read-modify-write
    cycle would be inconsistent; the field names themselves are written to
    be self-explanatory instead."""
    lines = ["[[items]]"]
    seen: set[str] = set()
    for key in _MANIFEST_ITEM_FIELD_ORDER:
        if key not in item:
            continue
        lines.append(f"{key} = {_serialize_toml_value(item[key])}")
        seen.add(key)
    for key, value in item.items():
        if key in seen:
            continue
        lines.append(f"{key} = {_serialize_toml_value(value)}")
    lines.append("")
    return lines


def _serialize_manifest(data: dict) -> str:
    """The single source of truth for the manifest's own TOML shape —
    used both to write a brand-new manifest and, by `apply_manifest`
    (`decisions/0073`, point 2), to read-modify-write an existing one so
    an applied item's own state becomes durable and mechanically
    distinguishable from a still-pending one."""
    lines = [
        f"manifest_id = {_toml_escape(data['manifest_id'])}",
        f"created = {_toml_escape(data['created'])}",
        f"slug = {_toml_escape(data['slug'])}",
        "",
    ]
    for item in data.get("items", []):
        lines += _serialize_manifest_item(item)
    return "\n".join(lines).rstrip() + "\n"


def write_manifest(
    project_root: Path,
    slug: str,
    anchor_findings: list[AnchorFinding],
    candidate_findings: list[CandidateFinding],
) -> Path | None:
    """The reconciliation manifest (§8/§11) — durable, committed, TOML,
    reusing the frozen-snapshot format's own shape. Returns `None` (and
    writes nothing) if there is genuinely nothing to review. Every item
    starts at `state = "pending"` (or `"concurrent_conflict"`) — never
    `"applied"`; only `apply_manifest` ever writes that state, and only
    after a real, successful write."""
    reviewable = [f for f in anchor_findings if f.case in ("candidate", "concurrent_conflict")]
    if not reviewable and not candidate_findings:
        return None
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    manifest_path = reconciliation_dir(project_root, slug) / f"{ts}.toml"
    data: dict = {
        "manifest_id": f"{slug}@{ts}",
        "created": datetime.now(UTC).isoformat(),
        "slug": slug,
        "items": [],
    }
    for f in reviewable:
        state = "concurrent_conflict" if f.case == "concurrent_conflict" else "pending"
        data["items"].append(
            {
                "kind": "anchor_edit",
                "record_id": f.record_id,
                "file": str(f.file.relative_to(project_root)),
                "base_semantic_hash": f.base_semantic_hash,
                "base_projection_hash": f.base_projection_hash,
                "current_semantic_hash": f.current_semantic_hash or "",
                "current_projection_hash": f.current_projection_hash,
                "state": state,
                "edited_text": f.body_text,
                # Stage 2 (human/agent review) sets these before apply:
                "decision": "undecided",  # "accept" or "reject"
                "semantic_change": False,  # true if this is more than wording
                "proposed_basis": "",  # e.g. "proposed_policy" -- empty = unclassified
            }
        )
    for c in candidate_findings:
        item: dict = {
            "kind": "candidate_addition",
            "file": str(c.file.relative_to(project_root)),
            "index": c.index,
            "text": c.text,
            "state": "pending",
            "decision": "undecided",  # Stage 2 sets this before apply
        }
        if c.requirement_decision is not None:
            item["requirement_decision"] = c.requirement_decision
            item["requirement_statement"] = c.requirement_statement or ""
            item["requirement_example"] = c.requirement_example or ""
        if c.declared_intent:
            item["declared_intent"] = True
            item["intent_statement"] = c.intent_statement or ""
        data["items"].append(item)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(_serialize_manifest(data), encoding="utf-8")
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


def _find_existing_promoted_record(
    records: dict[str, KnowledgeRecord],
    statement: str,
    kind: str = "claim",
    depends_on: str | None = None,
    decision: str | None = None,
) -> str | None:
    """Content-addressed idempotency check (`decisions/0073` point 2,
    tightened by `decisions/0074` point 9): before creating a new record
    from external text, check whether an equivalent one already exists —
    from a prior apply of the same or an overlapping manifest. Avoids a
    separate ledger file by reusing the canonical records themselves as
    the single source of truth for "has this already happened."

    **Type-aware**: `kind` is always checked (defaults to `"claim"`, the
    overwhelmingly common case) — a pre-existing Claim with identical
    prose must never block an explicit Requirement proposal from actually
    being created, and a Requirement must never accidentally satisfy a
    Claim-kind dedup check just because its own statement text matches.
    `decision`, when given, additionally requires a Requirement's own
    `decision:` field to match (two Requirements with the same statement
    text but different authorising Decisions are not the same
    contribution). Two candidates with byte-identical text (after
    trimming) *of the same kind* are treated as the same contribution by
    design — see `docs/codecompass-knowledge-workflow.md`'s own documented
    rationale.
    """
    target = statement.strip()
    if not target:
        return None
    for record in records.values():
        if record.kind != kind:
            continue
        if record.fields.get("statement", "").strip() != target:
            continue
        if depends_on is not None:
            deps = _extract_id_strings(record.fields.get("depends_on", ""))
            if depends_on not in deps:
                continue
        if decision is not None and record.fields.get("decision") != decision:
            continue
        return record.record_id
    return None


def _consume_candidate_text(md_path: Path, text: str) -> bool:
    """Removes every occurrence of `text` as its own candidate block from
    the live candidate region (`decisions/0073`, point 2) — once a
    candidate's content becomes a real canonical record, that record is
    the one place its provenance now lives; leaving the raw text behind
    would let a fresh `select-candidates` run rediscover it as if it were
    still new. Two blocks with byte-identical text are the same
    contribution (see `_find_existing_promoted_record`), so both are
    consumed together here rather than leaving a duplicate to be
    rediscovered later. Only ever touches the candidate region of this
    one file; everything else, including other still-pending candidate
    blocks, is untouched. Returns whether anything was actually removed
    (`False` if the text is no longer present — already consumed by an
    earlier apply)."""
    full_text = md_path.read_text(encoding="utf-8")
    start = full_text.find(CANDIDATE_START)
    end = full_text.find(CANDIDATE_END)
    if start == -1 or end == -1 or end < start:
        return False
    region_start = start + len(CANDIDATE_START)
    region = full_text[region_start:end]
    blocks = [b.strip() for b in re.split(r"\n\s*\n", region.strip("\n")) if b.strip()]
    target = text.strip()
    if target not in blocks:
        return False
    remaining = [b for b in blocks if b != target]
    new_region = ("\n\n" + "\n\n".join(remaining) + "\n") if remaining else ""
    full_text = full_text[:region_start] + new_region + full_text[end:]
    md_path.write_text(full_text, encoding="utf-8")
    return True


def _refresh_single_anchor_after_apply(
    project_root: Path, slug: str, file_rel: str, record_id: str
) -> None:
    """After a successful anchor-edit apply (either branch), the original
    anchor's own `base_projection_hash` must be brought back in sync with
    whatever is now live — otherwise a later `select-candidates` run would
    see `projection_edited=True` again against the *stale* base and
    rediscover the same already-applied edit as a brand-new candidate
    (`decisions/0073`, point 2). For a presentation-only apply this
    re-renders using the now-cached wording (so the hash matches what the
    reader already sees); for a promoted semantic edit, it resets the
    original block back to the original record's own canonical content,
    since the edit's own content now lives in the new, separately-rendered
    competing Claim. Reuses the exact same targeted single-block
    substitution `refresh_safe_anchors` uses — never a whole-file
    re-render."""
    md_path = project_root / file_rel
    if not md_path.is_file():
        return
    records = load_slug_records(slug_dir(project_root, slug))
    record = records.get(record_id)
    if record is None:
        return
    cache = read_presentation_cache(presentation_cache_path(project_root, slug))
    _replace_anchor_blocks(md_path, {record_id: render_block(record, records, cache)})


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
    edited_text = item.get("edited_text", "").strip()
    if not item.get("semantic_change", False):
        cache_path = presentation_cache_path(project_root, slug)
        cache = read_presentation_cache(cache_path)
        cache[record_id] = PresentationEntry(
            accepted_for_semantic_hash=live_hash,
            wording=edited_text,
        )
        write_presentation_cache(cache_path, cache)
        outcome = ApplyOutcome(
            True, item, "presentation cache updated; canonical record untouched"
        )
        _refresh_single_anchor_after_apply(project_root, slug, item.get("file", ""), record_id)
        return outcome
    # A semantic edit never overwrites the original record directly (§7) —
    # it always creates a new, competing candidate Claim instead.
    existing = _find_existing_promoted_record(
        records, edited_text, kind="claim", depends_on=record_id
    )
    if existing:
        return ApplyOutcome(
            True, item, f"already applied — {existing} already exists with this content", existing
        )
    new_id = _next_id(sdir, "CL")
    fields = {
        "id": new_id,
        "kind": "claim",
        "statement": edited_text,
        "derivation": "null",
        "supporting_evidence": "[]",
        "contradicting_evidence": "[]",
        "derived_by": '"external:unknown"',
        "repository_revision": '"working tree"',
        "timestamp": f'"{datetime.now(UTC).isoformat()}"',
        "status": "proposed",
        "depends_on": f"[{record_id}]",
    }
    # decisions/0073, point 7: basis is only ever proposed_policy when
    # Stage 2 review explicitly classifies this as declared intent --
    # otherwise it stays unclassified (omitted), never guessed.
    proposed_basis = item.get("proposed_basis") or ""
    if proposed_basis:
        fields["basis"] = proposed_basis
    _write_record(sdir / f"{new_id}.yaml", fields)
    _refresh_single_anchor_after_apply(project_root, slug, item.get("file", ""), record_id)
    return ApplyOutcome(True, item, f"created {new_id} as a competing candidate", new_id)


def _requirement_proposal_validity(
    records: dict[str, KnowledgeRecord], item: dict
) -> tuple[bool, str, str]:
    """Pure validity check, no side effects — whether an explicit `Type:
    Requirement` candidate resolves to a real, already-`approved` Decision
    plus a meaningful Given/When/Then example (`decisions/0073`, point 6).
    Returns `(valid, decision_id, statement)`. Factored out of
    `_apply_requirement_proposal` so a candidate's own intended canonical
    identity (`_derive_candidate_identity`) can be derived once, before any
    presence check or record creation, without duplicating this logic."""
    decision_id = item.get("requirement_decision") or ""
    statement = (item.get("requirement_statement") or "").strip()
    example = (item.get("requirement_example") or "").strip()
    decision_record = records.get(decision_id)
    valid_decision = (
        decision_record is not None
        and decision_record.kind == "decision"
        and decision_record.fields.get("status") == "approved"
    )
    # A "meaningful" Given/When/Then example is checked structurally only
    # (does it contain the three words at all) -- deliberately not full
    # semantic validation, which this project does not attempt.
    lowered = example.lower()
    valid_example = all(word in lowered for word in ("given", "when", "then"))
    return bool(valid_decision and statement and valid_example), decision_id, statement


def _apply_requirement_proposal(
    sdir: Path, records: dict[str, KnowledgeRecord], item: dict
) -> ApplyOutcome | None:
    """Explicit `Type: Requirement` candidates only (`decisions/0073`,
    point 6) — a candidate block merely *mentioning* an approved Decision
    id is never enough. Returns `None` (never a Requirement) if the
    explicit proposal is missing a real approved Decision, a statement, or
    a meaningful acceptance example — callers fall back to an ordinary
    Claim proposal in that case, never silently dropping the contribution,
    and never auto-generating a placeholder example to paper over the
    gap."""
    valid, decision_id, statement = _requirement_proposal_validity(records, item)
    if not valid:
        return None
    example = (item.get("requirement_example") or "").strip()
    existing = _find_existing_promoted_record(
        records, statement, kind="requirement", decision=decision_id
    )
    if existing:
        return ApplyOutcome(
            True, item, f"already applied — {existing} already exists with this content", existing
        )
    new_id = _next_id(sdir, "REQ")
    fields = {
        "id": new_id,
        "kind": "requirement",
        "statement": statement,
        "example": example,
        "decision": decision_id,
        "status": "proposed",
    }
    _write_record(sdir / f"{new_id}.yaml", fields)
    return ApplyOutcome(True, item, f"created {new_id}", new_id)


@dataclass
class _CandidateIdentity:
    """A candidate's own intended canonical identity — derived exactly
    once, before any presence check or record creation (`decisions/0075`,
    point 1), and reused for both. Previously a Requirement candidate's
    presence/race check used a different, later-computed statement than
    its own actual creation path, which let a Requirement's live-text
    presence go unchecked entirely — this type makes "what kind of record
    would this become, and under what statement/decision" a single,
    unambiguous value computed up front."""

    kind: str  # "claim" | "requirement"
    statement: str
    decision: str | None = None  # only ever set when kind == "requirement"


def _derive_candidate_identity(
    records: dict[str, KnowledgeRecord], item: dict, text: str
) -> _CandidateIdentity:
    """The single source of truth for "what would this candidate become,
    and under what identity" — computed once, before the live-text
    presence/race check, and reused for the real apply so the two can
    never disagree (`decisions/0075`, point 1). An explicit, *valid*
    `Type: Requirement` resolves to a Requirement identity (statement +
    authorising decision); an incomplete one falls back to a Claim using
    its own Statement text, exactly as `decisions/0073` point 6 already
    established; `Type: Intent` resolves to a Claim identity using the
    already-stripped body (`decisions/0074`, point 7); plain prose is a
    Claim using the raw text."""
    if item.get("requirement_decision"):
        valid, decision_id, statement = _requirement_proposal_validity(records, item)
        if valid:
            return _CandidateIdentity("requirement", statement, decision_id)
        return _CandidateIdentity("claim", statement or text)
    if item.get("declared_intent"):
        return _CandidateIdentity("claim", (item.get("intent_statement") or "").strip() or text)
    return _CandidateIdentity("claim", text)


def _apply_candidate_addition(project_root: Path, slug: str, item: dict) -> ApplyOutcome:
    sdir = slug_dir(project_root, slug)
    records = load_slug_records(sdir)
    file_rel = item.get("file", "")
    md_path = project_root / file_rel
    text = item.get("text", "")  # the exact raw block, as it appears live

    # decisions/0075, point 1: the candidate's own intended identity is
    # derived ONCE, before the presence/race check below -- a Requirement
    # candidate used to branch into its own apply path (and get created)
    # before this check ever ran, letting a stale manifest create a
    # Requirement whose live candidate text had already been deleted or
    # materially changed. Every candidate type now goes through the exact
    # same presence/race gate first.
    identity = _derive_candidate_identity(records, item, text)

    text_present = md_path.is_file() and _candidate_text_present(md_path, text)
    if not text_present:
        # decisions/0074, point 8 (now type-generalised by decisions/0075,
        # point 1): a missing candidate is NOT automatically "already
        # applied" -- that conflates two different situations. Only report
        # success if a matching canonical record can actually be found,
        # using this candidate's own real kind/decision identity (a Claim
        # with identical statement text must never satisfy a Requirement's
        # own already-applied check, and vice versa); otherwise this is a
        # stale manifest and must fail closed, never silently report
        # success.
        existing = _find_existing_promoted_record(
            records, identity.statement, kind=identity.kind, decision=identity.decision
        )
        if existing:
            return ApplyOutcome(
                True,
                item,
                f"already applied — {existing} already exists with this content",
                existing,
            )
        return ApplyOutcome(
            False,
            item,
            "apply-time race: candidate text no longer present in the live "
            "candidate region, and no matching canonical record exists — "
            "refusing to apply; re-run select-candidates and review again",
        )

    # Live text is genuinely present -- proceed with the real,
    # type-specific apply, using the SAME identity derived above.
    if identity.kind == "requirement":
        requirement_outcome = _apply_requirement_proposal(sdir, records, item)
        if requirement_outcome is not None:
            if requirement_outcome.ok:
                _consume_candidate_text(md_path, text)
            return requirement_outcome
        # Unreachable in practice: identity derivation already confirmed
        # validity against this same `records` snapshot moments ago. Falls
        # through to the Claim path below as a safe default rather than an
        # assumption this can never happen.

    claim_statement = identity.statement

    # decisions/0074, point 9: dedup is type-aware -- a pre-existing Claim
    # with identical prose must never block an explicit Requirement from
    # being created (handled above, via _apply_requirement_proposal's own
    # kind="requirement" dedup), and a pre-existing Requirement must never
    # satisfy this Claim-kind dedup check either.
    existing = _find_existing_promoted_record(records, claim_statement, kind="claim")
    if existing:
        _consume_candidate_text(md_path, text)
        return ApplyOutcome(
            True, item, f"already applied — {existing} already exists with this content", existing
        )

    new_id = _next_id(sdir, "CL")
    fields = {
        "id": new_id,
        "kind": "claim",
        "statement": claim_statement,
        "derivation": "null",
        "supporting_evidence": "[]",
        "contradicting_evidence": "[]",
        "derived_by": '"external:unknown"',
        "repository_revision": '"working tree"',
        "timestamp": f'"{datetime.now(UTC).isoformat()}"',
        "status": "proposed",
    }
    # decisions/0073, point 7: an ordinary external candidate is an
    # unclassified factual hypothesis by default (basis omitted) -- only
    # an explicit `Type: Intent` block earns `basis: proposed_policy`.
    if item.get("declared_intent"):
        fields["basis"] = "proposed_policy"
    _write_record(sdir / f"{new_id}.yaml", fields)
    _consume_candidate_text(md_path, text)
    return ApplyOutcome(True, item, f"created {new_id}", new_id)


def _candidate_text_present(md_path: Path, text: str) -> bool:
    full_text = md_path.read_text(encoding="utf-8")
    start = full_text.find(CANDIDATE_START)
    end = full_text.find(CANDIDATE_END)
    if start == -1 or end == -1 or end < start:
        return False
    region = full_text[start + len(CANDIDATE_START) : end]
    blocks = [b.strip() for b in re.split(r"\n\s*\n", region.strip("\n")) if b.strip()]
    return text.strip() in blocks


def apply_manifest(project_root: Path, manifest_path: Path) -> ApplyResult:
    """The only function in this module (and the only CLI command, §11)
    allowed to write `planning/knowledge/*/*.yaml`. Never trusts Stage 2's
    own annotation at face value — every item is mechanically re-checked.

    Idempotent (`decisions/0073`, point 2): an item already at
    `state = "applied"` is skipped immediately, with no re-check and no
    re-write — the manifest file itself is the durable, mechanically
    checkable record of what has already happened, rewritten in place
    (read-modify-write, `_serialize_manifest`) after every successful
    apply so a second run of this same manifest can never create a second
    record."""
    import tomllib

    data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    slug = data.get("slug", "")
    result = ApplyResult()
    changed = False
    for item in data.get("items", []):
        if item.get("state") == "applied":
            result.skipped.append(
                ApplyOutcome(
                    False,
                    item,
                    "already applied (state=applied)",
                    item.get("applied_record_id") or None,
                )
            )
            continue
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
        elif item.get("kind") == "doc_region_edit":
            outcome = _apply_doc_region_edit(project_root, slug, item)
        else:
            outcome = ApplyOutcome(False, item, f"unknown item kind {item.get('kind')!r}")
        if outcome.ok:
            item["state"] = "applied"
            item["applied_record_id"] = outcome.new_record_id or ""
            item["applied_at"] = datetime.now(UTC).isoformat()
            changed = True
            result.applied.append(outcome)
        else:
            result.skipped.append(outcome)
    if changed:
        manifest_path.write_text(_serialize_manifest(data), encoding="utf-8")
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

    grounded_findings = detect_grounded_region_changes(project_root, _DEFAULT_GROUNDED_DOCS)
    chunk_report = detect_doc_chunk_changes(project_root, _DEFAULT_GROUNDED_DOCS)
    for doc_name in _DEFAULT_GROUNDED_DOCS:
        doc_path = project_root / doc_name
        if not doc_path.is_file():
            continue
        text = doc_path.read_text(encoding="utf-8")
        marked_regions = parse_grounding_markers(text)
        grounded_ids: list[str] = []
        needing_review: list[str] = []
        for ids, _region, _region_id in marked_regions:
            grounded_ids.extend(ids)
            for record_id in ids:
                for s in slugs:
                    record = load_slug_records(slug_dir(project_root, s)).get(record_id)
                    if record and record.fields.get("status") == "contradicted":
                        needing_review.append(record_id)

        # decisions/0073, point 4: real changed-region tracking, not just
        # static counts -- a grounded region's own prose change (doc_candidate),
        # its cited Claim(s) moving (claims_changed), or both at once
        # (concurrent_conflict) all count as a "changed grounded region";
        # a changed chunk overlapping no grounding marker at all is
        # reported separately, purely advisory, never auto-converted into
        # a Claim.
        doc_findings = [f for f in grounded_findings if f.doc_name == doc_name]
        _changed_cases = ("doc_candidate", "claims_changed", "concurrent_conflict")
        changed_grounded = [f for f in doc_findings if f.case in _changed_cases]
        chunks = chunk_report.get(doc_name, {})
        report.grounding[doc_name] = {
            "grounded_regions": len(marked_regions),
            "grounded_ids": sorted(set(grounded_ids)),
            # Advisory only (§9.6) — regions whose own cited record is
            # currently contradicted/unresolved, the practical "needs a
            # look" signal. Never blocking.
            "regions_needing_review": sorted(set(needing_review)),
            "changed_grounded_regions": len(changed_grounded),
            "changed_grounded_region_detail": [
                f"region #{f.index} ({', '.join(f.cited_ids)}): {f.case}" for f in changed_grounded
            ],
            "changed_ungrounded_regions_needing_review": len(
                chunks.get("changed_ungrounded_chunks", [])
            ),
            "changed_ungrounded_chunks": chunks.get("changed_ungrounded_chunks", []),
        }
    return report
