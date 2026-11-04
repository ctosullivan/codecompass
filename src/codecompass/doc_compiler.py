"""Phase 87 -- knowledge-compilation pipeline core (decisions/0085 §5;
planning/phase-87-documentation-schema-knowledge-compiled-documentation.md
§A.5/§C, amendment findings A/D/E).

Reads `knowledge_api`/`oracle.py`/`knowledge_intermediate.py` only --
never `planning/knowledge/` directly, never a second knowledge store or
a second currency/epistemic computation (§G.2's write-boundary rule).
This module implements the *compiler's own policy* (resolution,
hydration, budgeting, citation verification) on top of Phase 84's
existing read-only API; it never re-derives what that API already
answers.

Steps 6 (clean-room composition) and 8 (editorial-quality assessment),
and step 7's AI-assisted semantic-support check, are deliberately not
functions in this module -- they are ad-hoc dispatches the lead/CLI
orchestrates (`CLAUDE.md` §8: "CodeCompass never spawns or coordinates
agents"). This module implements the deterministic half of the
pipeline: resolution, hydration, gap detection, and the *scope* half of
citation verification (a cited id must be in this section's own
packet) -- never the semantic *depth* half (does the record's content
actually support the sentence's specific wording), which is AI-assisted
by design and lives outside this module.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from . import knowledge_api as _api
from . import knowledge_intermediate as _ki

# decisions/0085 §5's schema field; real record `status` values observed
# in this project's own corpus include `candidate`-tier ("proposed"),
# `supported`-tier ("supported", "current"), and `verified`-tier
# ("verified") -- this ranking is the compiler's own ordinal
# interpretation of that free-text field, not a change to its storage.
_MIN_STATUS_RANK = {
    "candidate": 0,
    "proposed": 0,
    "recorded": 0,
    "supported": 1,
    "current": 1,
    "implemented": 1,
    "approved": 1,
    "verified": 2,
}

_CITATION_TAG_RE = re.compile(r"\{\{cite:([A-Za-z0-9_-]+)\}\}")


class DocCompilerError(Exception):
    """Raised for a fail-closed condition the compiler refuses to work
    around -- an unresolved `discover:` entry reaching compile time, or
    required evidence exceeding its own declared budget. Never caught
    internally to produce a degraded-but-published result."""


@dataclass
class SectionGap:
    kind: str
    # "unresolved_required_knowledge" | "below_min_claim_status" |
    # "stale_or_unconfirmed_evidence" | "contradiction"
    record_id: str | None
    reason: str


@dataclass
class EvidencePacket:
    section_id: str
    record_ids: list[str]
    hydrated: dict[str, dict]  # record_id -> full details["fields"]
    serialized_chars: int


@dataclass
class CitationFinding:
    record_id: str
    classification: str  # "supported" | "unsupported" | "contradicted" | "uncertain"
    reason: str


# ---------------------------------------------------------------------------
# Step 1/3: resolution (amendment finding A)
# ---------------------------------------------------------------------------


def resolve_section_ids(schema_section: dict) -> list[str]:
    """`required_knowledge` entries are, by the time compilation runs,
    always concrete record ids -- a `discover:<query>` entry is resolved
    to exactly one id by `check_doc_schema.py` at schema-validation time
    (amendment finding A, point 2), never by this function or at compile
    time. Raises `DocCompilerError` if an unresolved `discover:` entry
    somehow still reaches here -- a defect in the validation step that
    ran before this one, never silently resolved on the compiler's own
    initiative."""
    ids: list[str] = []
    for entry in schema_section.get("required_knowledge", []):
        if entry.startswith("discover:"):
            raise DocCompilerError(
                f"section {schema_section.get('id')!r} has an unresolved "
                f"discover: entry {entry!r} reaching the compiler -- "
                "check_doc_schema.py must resolve every discover: query "
                "to exactly one concrete record id before compilation runs; "
                "the compiler itself never calls search() to resolve one"
            )
        ids.append(entry)
    return ids


def map_section_to_knowledge(schema_section: dict) -> list[str]:
    """Identity function over `resolve_section_ids` (§C step 3) -- the
    mapping *is* the schema's own `required_knowledge` field; no
    additional inference is performed."""
    return resolve_section_ids(schema_section)


# ---------------------------------------------------------------------------
# Step 2: currency (reuses knowledge_api.get()'s own ConsistencyEnvelope)
# ---------------------------------------------------------------------------


def check_record_currency(
    project_root: Path, record_id: str, *, repo_root: Path | None = None
) -> tuple[str, list[str]]:
    """`(status, reasons)` -- reuses `knowledge_api.get()`'s own
    `ConsistencyEnvelope.status`/`.reasons` (`"current"` | `"stale"` |
    `"unconfirmed"`) directly; this function performs no independent
    currency computation of its own. `"absent"` if the id does not
    resolve at all."""
    response = _api.get(project_root, record_id, repo_root=repo_root)
    if response.status != "result" or not response.results:
        return "absent", [f"{record_id!r} does not resolve via knowledge_api.get()"]
    result = response.results[0]
    return result.consistency.status, list(result.consistency.reasons)


# ---------------------------------------------------------------------------
# Step 4: gap detection before writing (amendment finding A, depth check)
# ---------------------------------------------------------------------------


def find_section_gaps(
    project_root: Path, schema_section: dict, *, repo_root: Path | None = None
) -> list[SectionGap]:
    """A section whose own `min_claim_status` isn't met by *every one* of
    its own resolved ids -- not merely "some id somewhere in the
    project" -- is a generation-blocking gap (L-075's depth distinction,
    applied to documentation). Never silently generated around.

    `min_claim_status`/`allow_unconfirmed_scopes` are flat per-section
    fields (plan §B's minimal schema, corrected during the Stage 87A
    restructuring review) -- not nested under an `evidence_requirements`
    dict, which was the pre-restructuring plan's own shape."""
    gaps: list[SectionGap] = []
    min_status = schema_section.get("min_claim_status", "candidate")
    min_rank = _MIN_STATUS_RANK.get(min_status, 0)
    allow_unconfirmed = schema_section.get("allow_unconfirmed_scopes", False)

    section_ids = resolve_section_ids(schema_section)
    for record_id in section_ids:
        response = _api.get(project_root, record_id, repo_root=repo_root)
        if response.status != "result" or not response.results:
            gaps.append(SectionGap(
                "unresolved_required_knowledge", record_id,
                f"{record_id!r} is required by this section but does not resolve "
                "via knowledge_api.get() -- required knowledge never silently disappears",
            ))
            continue
        result = response.results[0]
        fields = result.details.get("fields", {})

        record_status = fields.get("status", "candidate")
        record_rank = _MIN_STATUS_RANK.get(record_status, 0)
        if record_rank < min_rank:
            gaps.append(SectionGap(
                "below_min_claim_status", record_id,
                f"record status {record_status!r} (rank {record_rank}) is below "
                f"this section's required min_claim_status {min_status!r} (rank {min_rank})",
            ))

        currency_status = result.consistency.status
        if currency_status == "stale":
            gaps.append(SectionGap(
                "stale_or_unconfirmed_evidence", record_id,
                "; ".join(result.consistency.reasons) or "stale evidence",
            ))
        elif currency_status == "unconfirmed" and not allow_unconfirmed:
            gaps.append(SectionGap(
                "stale_or_unconfirmed_evidence", record_id,
                "; ".join(result.consistency.reasons)
                or "unconfirmed evidence, and this section does not allow_unconfirmed_scopes",
            ))

    # Project-wide contradiction/dangling-reference gaps, filtered to
    # exactly this section's own resolved ids -- reusing find_gaps
    # directly, never re-deriving its rules.
    section_id_set = set(section_ids)
    gaps_response = _api.find_gaps(project_root, repo_root=repo_root)
    for gap in gaps_response.gaps:
        if gap.subject_id in section_id_set and gap.kind in (
            "contradiction", "dangling_evidence_reference", "dangling_dependency_reference",
        ):
            gaps.append(SectionGap(gap.kind, gap.subject_id, gap.reason))

    return gaps


# ---------------------------------------------------------------------------
# Step 5: bounded, section-specific evidence packets (amendment finding A)
# ---------------------------------------------------------------------------


def resolve_section_packet(
    project_root: Path, schema_section: dict, *, repo_root: Path | None = None
) -> EvidencePacket:
    """Full hydration via `knowledge_api.get()`'s `details["fields"]` --
    never `search()`/`get_context_packet()`'s own 280-character
    `summary` field. Budgeted against the *real serialized* hydrated
    content; a required record's content is never silently truncated
    to fit the budget -- exceeding it is a `DocCompilerError`, not a
    silent drop."""
    section_id = schema_section.get("id", "<unknown>")
    max_chars = schema_section.get("max_evidence_chars", 6000)
    ids = resolve_section_ids(schema_section)

    hydrated: dict[str, dict] = {}
    for record_id in ids:
        if record_id in hydrated:
            continue
        response = _api.get(project_root, record_id, repo_root=repo_root)
        if response.status == "result" and response.results:
            hydrated[record_id] = dict(response.results[0].details.get("fields", {}))

    total_chars = sum(len(json.dumps(v, sort_keys=True)) for v in hydrated.values())
    if total_chars > max_chars:
        raise DocCompilerError(
            f"section {section_id!r}'s required evidence serializes to "
            f"{total_chars} characters, exceeding its own max_evidence_chars="
            f"{max_chars} -- widen the budget or narrow the section's "
            "required_knowledge; required content is never silently truncated to fit"
        )

    return EvidencePacket(
        section_id=section_id,
        record_ids=list(dict.fromkeys(ids)),
        hydrated=hydrated,
        serialized_chars=total_chars,
    )


# ---------------------------------------------------------------------------
# Step 7 (scope half): citation-tag parsing and in-packet verification
# ---------------------------------------------------------------------------


@dataclass
class CitationTag:
    record_id: str
    span: tuple[int, int]


def parse_citation_tags(text: str) -> list[CitationTag]:
    """Extracts every `{{cite:RECORD-ID}}` token in appearance order --
    the section-specific writing contract's own required citation
    convention (§C step 6e/step 7 point 1), mirroring Oracle's existing
    `scope`-string citation discipline applied to generated prose."""
    return [CitationTag(m.group(1), m.span()) for m in _CITATION_TAG_RE.finditer(text)]


def validate_section_citations(text: str, packet: EvidencePacket) -> list[CitationFinding]:
    """The deterministic, scope half of claim verification (§C step 7
    points 2-4's non-semantic sub-check): every tagged citation must
    name a record id that is a member of *this section's own* resolved
    packet -- not merely a record that exists somewhere in the project
    (L-075's depth-vs-scope distinction, applied here at the scope
    level). The semantic depth check (does the cited record's content
    actually support the sentence's specific wording) is AI-assisted by
    design and is not performed by this function -- see the plan's §C
    step 7 point 3's second sub-check, dispatched independently by the
    caller."""
    findings: list[CitationFinding] = []
    packet_ids = set(packet.record_ids)
    for tag in parse_citation_tags(text):
        if tag.record_id not in packet_ids:
            if tag.record_id in packet.hydrated:
                # unreachable given packet_ids is built from the same
                # dict, but keeps the two checks independently legible
                reason = "cited but not in this section's own resolved id list"
            else:
                reason = (
                    f"{tag.record_id!r} is not a member of this section's own resolved "
                    "evidence packet -- citing a record that exists elsewhere in the "
                    "project does not make it permitted evidence for this section"
                )
            findings.append(CitationFinding(tag.record_id, "unsupported", reason))
        else:
            findings.append(CitationFinding(
                tag.record_id, "supported",
                "citation resolves within this section's own packet (scope check only; "
                "semantic support is verified separately, by independent AI-assisted dispatch)",
            ))
    return findings


_STRAY_SPACE_BEFORE_PUNCTUATION_RE = re.compile(r" +([.,;:!?])")
_STRAY_DOUBLE_SPACE_RE = re.compile(r" {2,}")


def strip_citation_tags(text: str) -> str:
    """Removes every `{{cite:...}}` token, leaving the publishable
    prose -- used when a section's own `citation_display` is not
    `inline` (§C step 9, §G.C). Machine-readable grounding (the
    `codecompass-grounded-by region:<id>` marker) is emitted separately
    by the publisher regardless of this setting -- stripping the inline
    tags here never removes a section's own grounding.

    A real defect found during Stage 87A's own live demonstration run
    (independent editorial review caught it, not a unit test): the
    writing contract places a tag immediately before the sentence's
    own closing punctuation (`fact {{cite:X}}.`), so a bare substitution
    leaves a stray space (`fact .`) or a double space between two
    adjacent tags. Both are cleaned up here, never left for a human
    editor to notice after publication."""
    stripped = _CITATION_TAG_RE.sub("", text)
    stripped = _STRAY_SPACE_BEFORE_PUNCTUATION_RE.sub(r"\1", stripped)
    stripped = _STRAY_DOUBLE_SPACE_RE.sub(" ", stripped)
    return stripped


# ---------------------------------------------------------------------------
# compile_document -- orchestration (steps 1-7's scope half)
# ---------------------------------------------------------------------------

# Restructuring-pass correction (§G.A): a section id composes into a
# `codecompass-grounded-by region:<id>` token, whose own real parser
# (`knowledge_intermediate._REGION_ID_RE`) accepts `[A-Za-z0-9_-]+` but
# NOT `.` -- a dotted id silently truncates. This module's own
# convention is intentionally narrower (lowercase, hyphen-only) to keep
# every id this compiler ever produces unambiguous and consistent with
# `check_doc_schema.py`'s own validation.
_SECTION_ID_RE = re.compile(r"^[a-z0-9-]+$")


@dataclass
class SectionCompileResult:
    section_id: str
    status: str
    # "gap_blocked" | "citation_blocked" | "pending_review" | "composition_failed"
    gaps: list[SectionGap] = field(default_factory=list)
    citation_findings: list[CitationFinding] = field(default_factory=list)
    draft_body: str | None = None
    packet: EvidencePacket | None = None
    error: str | None = None


def compile_document(
    project_root: Path,
    schema: dict,
    *,
    repo_root: Path | None = None,
    compose_and_validate: Callable[[dict, EvidencePacket], tuple[str, list[CitationFinding]]]
    | None = None,
) -> list[SectionCompileResult]:
    """Runs steps 1-5 and the scope half of step 7 for every section in
    `schema`. `compose_and_validate` performs step 6 (clean-room
    composition, `scripts/compile_doc_section.py`) plus the returned-
    text citation-scope check, injected by the caller so this module
    never imports the sandboxing-adjacent `scripts/` layer directly
    (`CLAUDE.md` §8 -- this module never spawns or coordinates an
    agent/broker call itself). A section whose citations are all
    `supported` reaches `pending_review` -- the AI-assisted semantic
    depth check (step 7 point 3) and the editorial-quality assessment
    (step 8) are ad-hoc dispatches the CLI/lead performs next, outside
    this function, never silently skipped by treating `pending_review`
    as equivalent to published."""
    results: list[SectionCompileResult] = []
    for section in schema.get("sections", []):
        section_id = section.get("id", "<missing id>")
        gaps = find_section_gaps(project_root, section, repo_root=repo_root)
        if gaps:
            results.append(SectionCompileResult(section_id, "gap_blocked", gaps=gaps))
            continue

        try:
            packet = resolve_section_packet(project_root, section, repo_root=repo_root)
        except DocCompilerError as exc:
            results.append(SectionCompileResult(section_id, "composition_failed", error=str(exc)))
            continue

        if compose_and_validate is None:
            results.append(SectionCompileResult(section_id, "composition_skipped", packet=packet))
            continue

        try:
            body, findings = compose_and_validate(section, packet)
        except Exception as exc:  # noqa: BLE001 -- any composer failure blocks, never a silent fallback
            results.append(SectionCompileResult(
                section_id, "composition_failed", error=str(exc), packet=packet,
            ))
            continue

        if any(f.classification == "unsupported" for f in findings):
            results.append(SectionCompileResult(
                section_id, "citation_blocked", citation_findings=findings, packet=packet,
            ))
            continue

        results.append(SectionCompileResult(
            section_id, "pending_review", draft_body=body,
            citation_findings=findings, packet=packet,
        ))
    return results


# ---------------------------------------------------------------------------
# publish_section -- grounded-marker publication (§C step 9, §G.C: always
# emits machine-readable grounding regardless of reader-visible display)
# ---------------------------------------------------------------------------


def publish_section(doc_path: Path, *, region_id: str, record_ids: list[str], body: str) -> None:
    """Writes or replaces exactly one `codecompass-grounded-by`-wrapped
    region, identified by its own stable `region:<id>` token -- reusing
    the existing marker convention and identity scheme directly
    (`knowledge_intermediate.parse_grounding_markers`), never a new
    identity mechanism. Machine-readable grounding is unconditional:
    this function has no `citation_display`/`provenance` parameter at
    all -- the caller decides separately (via `strip_citation_tags`,
    before calling this) whether the body text itself still carries a
    reader-visible citation phrase; the marker wrapping it is always
    present either way."""
    if not _SECTION_ID_RE.match(region_id):
        raise DocCompilerError(
            f"region_id {region_id!r} must match {_SECTION_ID_RE.pattern!r} -- "
            "a dot or other separator silently truncates at the real region-id parser"
        )

    header = " ".join([*record_ids, f"region:{region_id}"])
    marker = (
        f"<!-- codecompass-grounded-by: {header} -->\n{body}\n"
        "<!-- /codecompass-grounded-by -->"
    )

    doc_path.parent.mkdir(parents=True, exist_ok=True)
    if not doc_path.is_file():
        doc_path.write_text(marker + "\n", encoding="utf-8")
        return

    text = doc_path.read_text(encoding="utf-8")
    open_re = re.compile(r"<!--\s*codecompass-grounded-by:\s*(.+?)\s*-->")
    close_marker = "<!-- /codecompass-grounded-by -->"
    pos = 0
    while True:
        match = open_re.search(text, pos)
        if match is None:
            break
        close_idx = text.find(close_marker, match.end())
        if close_idx == -1:
            pos = match.end()
            continue
        existing_region_match = re.search(r"\bregion:([A-Za-z0-9_-]+)\b", match.group(1))
        existing_region_id = existing_region_match.group(1) if existing_region_match else None
        span_end = close_idx + len(close_marker)
        if existing_region_id == region_id:
            doc_path.write_text(text[: match.start()] + marker + text[span_end:], encoding="utf-8")
            return
        pos = span_end

    doc_path.write_text(text.rstrip("\n") + "\n\n" + marker + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# maintain_document -- five-state reconciliation (§D.2/§A.3, built on
# knowledge_intermediate.detect_grounded_region_changes directly)
# ---------------------------------------------------------------------------


@dataclass
class MaintainReport:
    established_new: list[str] = field(default_factory=list)
    noop: list[str] = field(default_factory=list)
    doc_candidates: list[str] = field(default_factory=list)
    claims_changed: list[str] = field(default_factory=list)
    concurrent_conflicts: list[str] = field(default_factory=list)


def maintain_document(project_root: Path, doc_names: tuple[str, ...]) -> MaintainReport:
    """Branches on the real five `GroundedRegionFinding.case` values,
    using the three already-implemented resolution functions this
    project has for exactly this problem -- no new diffing model.
    `doc_names` must cover every schema-governed document in one call
    so `DuplicateGroundingRegionIdError` is checked project-wide, not
    merely within the one document being compiled."""
    findings = _ki.detect_grounded_region_changes(project_root, doc_names)
    report = MaintainReport()

    new_findings = [f for f in findings if f.case == "new"]
    if new_findings:
        report.established_new = _ki.establish_new_region_baselines(project_root, new_findings)

    doc_candidate_findings = [f for f in findings if f.case == "doc_candidate"]
    if doc_candidate_findings:
        _ki.write_doc_candidates_to_manifests(project_root, doc_candidate_findings)
        report.doc_candidates = [f.state_key for f in doc_candidate_findings]

    report.noop = [f.state_key for f in findings if f.case == "noop"]
    report.claims_changed = [f.state_key for f in findings if f.case == "claims_changed"]
    report.concurrent_conflicts = [f.state_key for f in findings if f.case == "concurrent_conflict"]

    return report
