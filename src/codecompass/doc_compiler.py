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
from . import oracle as _oracle

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


def hydrate_records(
    project_root: Path, record_ids: list[str], *, repo_root: Path | None = None
) -> dict[str, dict]:
    """Full hydration via `knowledge_api.get()`'s `details["fields"]` --
    never `search()`/`get_context_packet()`'s own 280-character
    `summary` field. Shared by `resolve_section_packet` (compile-time,
    budget-checked) and the hardening pass's own publish-time
    revalidation (`hash_evidence` over this function's own output) --
    one hydration path, never two independent computations that could
    silently drift apart (§N.A/§N.C hardening)."""
    hydrated: dict[str, dict] = {}
    for record_id in record_ids:
        if record_id in hydrated:
            continue
        response = _api.get(project_root, record_id, repo_root=repo_root)
        if response.status == "result" and response.results:
            hydrated[record_id] = dict(response.results[0].details.get("fields", {}))
    return hydrated


def hash_evidence(hydrated: dict[str, dict]) -> str:
    """Canonical content hash over a section's own hydrated evidence
    map -- the single definition of "evidence identity" shared by
    compile-time packet writing, review-record binding, and publish-
    time revalidation (hardening pass §N.A/§N.C). Never recomputed ad
    hoc at each call site with a different serialization, which would
    make two honestly-identical evidence sets hash differently."""
    return _oracle.sha256_text(json.dumps(hydrated, sort_keys=True))


def resolve_section_packet(
    project_root: Path, schema_section: dict, *, repo_root: Path | None = None
) -> EvidencePacket:
    """Full hydration via `hydrate_records`, budgeted against the *real
    serialized* hydrated content; a required record's content is never
    silently truncated to fit the budget -- exceeding it is a
    `DocCompilerError`, not a silent drop."""
    section_id = schema_section.get("id", "<unknown>")
    max_chars = schema_section.get("max_evidence_chars", 6000)
    ids = resolve_section_ids(schema_section)

    hydrated = hydrate_records(project_root, ids, repo_root=repo_root)

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
# Publication-path and section-identity validation (hardening pass §N.B)
# ---------------------------------------------------------------------------


def compute_schema_slug(schema_path: Path) -> str:
    """A `[a-z0-9-]+` slug for `schema_path`, safe to compose into a
    `region:<schema_slug>-<section_id>` identity (§G.A). A naive
    `.stem.removesuffix(".schema")` breaks on a document whose own name
    already contains a dot (`README.md.schema.yaml` -> stem
    `README.md.schema` -> `README.md` after removesuffix, which still
    has a `.` in it) -- caught directly by `publish_section`'s own
    fail-closed region-id check during Stage 87A's real demonstration
    run. Strips the full `.schema.yaml` suffix in one step, then
    normalises anything left. Moved here from `cli.py`'s own private
    `_schema_slug` (third corrective amendment, finding A) so
    `scripts/check_doc_schema.py`'s new cross-document region-id check
    can share the exact same computation `docs publish` uses, rather
    than risk two independently-maintained copies drifting apart --
    the same discipline `hash_evidence` already established."""
    name = schema_path.name
    if name.endswith(".schema.yaml"):
        name = name[: -len(".schema.yaml")]
    return re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")


def find_schema_section(schema: dict, section_id: str) -> dict | None:
    """The requested `section_id` must belong to the *current, live*
    schema, not merely to whatever schema produced an old pending-review
    manifest -- `None` if no section in `schema["sections"]` declares
    this id."""
    for section in schema.get("sections", []):
        if section.get("id") == section_id:
            return section
    return None


# Hardening pass §N.B: the only documentation targets a compiler-owned
# write may ever land in. README.md at the repo root, or any Markdown
# file under docs/ -- the two targets this project's own real schemas
# (Stage 87A's README.md.schema.yaml, Stage 87B's planned getting-
# started schema) actually need. Any further target requires its own
# explicit justification added here, never silently widened by a schema
# author's own `document` field.
_ALLOWED_DOC_ROOT_DIRS = ("docs",)
_ALLOWED_ROOT_FILES = ("README.md",)


def resolve_publication_target(project_root: Path, document: str) -> Path:
    """Single, reusable publication-path validation policy, used at
    both schema-validation time (`check_doc_schema.py`) and publication
    time (`docs publish`) -- never two independently-maintained checks
    that could drift apart. Raises `DocCompilerError` for: an absolute
    path, a `..` traversal component, any target outside the approved
    `README.md`/`docs/**/*.md` set, or a resolved real path (following
    symlinks) that escapes `project_root` -- resolution-then-comparison
    is used throughout rather than a string-prefix check, since a
    string prefix can be defeated by a symlinked intermediate directory
    or a crafted relative component that still *looks* contained before
    the filesystem actually resolves it."""
    if not document:
        raise DocCompilerError("a schema's document field must not be empty")

    candidate = Path(document)
    if candidate.is_absolute():
        raise DocCompilerError(
            f"document {document!r} is an absolute path -- only a path relative to "
            "the project root is permitted"
        )
    if ".." in candidate.parts:
        raise DocCompilerError(
            f"document {document!r} contains a '..' traversal component -- rejected"
        )

    is_allowed_root_file = document in _ALLOWED_ROOT_FILES
    is_allowed_docs_subtree = (
        candidate.parts[:1] == ("docs",) and candidate.suffix == ".md"
    )
    if not (is_allowed_root_file or is_allowed_docs_subtree):
        raise DocCompilerError(
            f"document {document!r} is not an approved documentation target -- "
            f"only {_ALLOWED_ROOT_FILES!r} or a {'/'.join(_ALLOWED_DOC_ROOT_DIRS)}/"
            "**/*.md Markdown file is permitted"
        )

    root_real = project_root.resolve()
    target_real = (project_root / candidate).resolve()
    if not target_real.is_relative_to(root_real):
        raise DocCompilerError(
            f"document {document!r} resolves to {target_real}, which escapes the "
            f"project root {root_real} -- rejected (symlink-aware confinement check)"
        )

    return target_real


# ---------------------------------------------------------------------------
# Publication-time concurrency guard (Stage 87B §O.D point 3, third
# corrective amendment finding C) -- pure decision logic over an
# already-computed GroundedRegionFinding; the actual
# detect_grounded_region_changes call, the cooperating-writer lock, and
# the write/baseline-advance sequencing all live in the CLI, which owns
# I/O ordering (CLAUDE.md §8). Keeping the branching rule here, as a
# pure function, lets it be tested without a lock or a real document on
# disk.
# ---------------------------------------------------------------------------


def decide_publish_safety(
    finding: _ki.GroundedRegionFinding | None, new_body: str
) -> str | None:
    """Returns `None` if `publish_section` may safely proceed, or an
    explanatory refusal message if not. `finding` is `None` when no
    marker exists yet for this region at all (`detect_grounded_region_
    changes` reported nothing for it) -- genuinely safe, nothing to
    overwrite.

    For every other case, reuses `detect_grounded_region_changes`'s own
    five-state classification directly, never a new, separately-
    invented concurrency check:

    - `"new"` (the marker's own text already exists, unbaselined) --
      **not** automatically safe (the second corrective amendment's own
      gap, fixed here): compares the live region's own hash against the
      hash of `new_body`, the exact body about to be published. Equal
      means this is a legitimate idempotent re-publish of content
      already there; unequal means the live content is not provably
      this compiler's own prior output, so it is never assumed safe to
      discard.
    - `"noop"` (live region matches its recorded baseline exactly) --
      safe; the new, reviewed draft replaces content that hasn't
      independently drifted.
    - `"claims_changed"` (prose matches baseline; only cited knowledge
      moved) -- safe; the caller's own evidence-hash check (`docs
      publish`'s existing schema/evidence identity checks) already
      proves `new_body` reflects the *current* knowledge state, so this
      publish *is* the "current, independently verified replacement" a
      `claims_changed` state requires.
    - `"doc_candidate"` (prose has drifted, no matching knowledge
      change) -- refused; this is exactly "the region contains
      unacknowledged human changes."
    - `"concurrent_conflict"` (both drifted) -- refused; requires
      explicit lead-controlled reconciliation, never an automatic merge
      either direction.
    """
    if finding is None:
        return None
    if finding.case in ("noop", "claims_changed"):
        return None
    if finding.case == "new":
        candidate_hash = _oracle.sha256_text(f"\n{new_body}\n")
        if finding.region_hash == candidate_hash:
            return None
        return (
            f"region {finding.region_id!r} already has unbaselined content that does not "
            "match the draft about to be published -- refusing to overwrite content that "
            "cannot be proven to be this compiler's own prior output (run docs maintain "
            "first to see and resolve it)"
        )
    if finding.case == "doc_candidate":
        return (
            f"region {finding.region_id!r} contains unacknowledged human changes "
            "(doc_candidate) -- refusing to overwrite; run docs maintain and resolve it first"
        )
    if finding.case == "concurrent_conflict":
        return (
            f"region {finding.region_id!r} has both drifted prose and changed cited "
            "knowledge (concurrent_conflict) -- requires explicit lead-controlled "
            "reconciliation, never an automatic merge"
        )
    return f"region {finding.region_id!r} has an unrecognised case {finding.case!r}"


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
